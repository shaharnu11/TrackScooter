"""WALL-E's music: songs from ./music, asked for by voice.

    "play some music"  "play Billy Joel"  "next song"
    "what's playing?"  "stop the music"

Commands are matched here, in plain code, before the language model sees the
sentence. Asked "can you play music?", the 4B brain said "Here's a jazzy
number!" and played nothing; now either a song really starts or he says the
folder is empty.

Songs decode with PyAV (already installed for faster-whisper): mp3, m4a,
wav, flac, ogg. They play in their own output stream, so WALL-E's voice
(sd.play) talks over them, and the music ducks to DUCK while he listens or
speaks. When a song ends, a random next one starts, like a radio.
"""

from __future__ import annotations

import queue
import random
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

from lang import hebrew, t

MUSIC_DIR = Path(__file__).resolve().parent / "music"
AUDIO_EXT = {".mp3", ".m4a", ".aac", ".wav", ".flac", ".ogg", ".opus"}
SR = 44100
DUCK = 0.2  # music level, as a share of normal, while WALL-E listens or talks

_STOP = re.compile(
    r"\b(stop|pause|turn off|switch off|kill|enough)\b.*\b(music|song|it|playing|this)\b"
    r"|\bstop (the )?music\b|\bmusic off\b"
    r"|(עצור|תעצור|תעצרי|תפסיק|תפסיקי|תכבה|תכבי|די עם|בלי)\s+(את\s+)?(ה)?(מוזיקה|שיר)",
    re.IGNORECASE,
)
_NEXT = re.compile(
    r"\b(next|skip|another|different|change)\b.*\b(song|track|one|music|it|this)\b|^\W*skip\b"
    r"|(ה)?שיר (ה)?הבא|שיר אחר|תעביר (שיר|את השיר)|תחליף (שיר|את השיר)|^\W*דלג",
    re.IGNORECASE,
)
_WHAT = re.compile(
    r"\bwhat('s| is)?\s+(this|that|the)?\s*(song|track|playing)\b"
    r"|\bwhat are (we|you) (listening|playing)\b|\bwho (is )?(sings|singing)\b"
    r"|מה מתנגן|איזה שיר (זה|מתנגן)|מה השיר (הזה|שמתנגן)|מי שר",
    re.IGNORECASE,
)
# The asked-for words land in group "q". Hebrew "שים" alone is too wide
# ("תשים לב" = pay attention): it needs a music word after it.
_PLAY = re.compile(
    r"\b(play|put on|throw on|blast)\b(?P<q>.*)"
    r"|(תנגן|נגן|תנגני|נגני)(?P<q2>.*)"
    r"|(תשים|שים|תשימי|תפעיל|תפעילי)\s+(לי\s+|לנו\s+)?(?P<q3>(שיר|מוזיקה|את)\b.*)",
    re.IGNORECASE,
)
# "play" also means "play a game". Anything else after "play" is taken as
# music, so "play Coldplay" gets "I don't have Coldplay" rather than the
# brain pretending to play it.
_NOT_MUSIC = re.compile(
    r"\b(game|games|tag|hide|seek|catch|ball|cards?|chess|football|soccer|"
    r"outside|together|with|pretend|around|dead|fair|nice|role|trick|joke|"
    r"video|guitar|piano|drums|instrument)\b",
    re.IGNORECASE,
)
_FILLER = {
    "a", "an", "the", "some", "any", "me", "us", "for", "please", "can", "you",
    "could", "would", "will", "wally", "walle", "wall", "e", "hey", "now",
    "again", "on", "play", "put", "throw", "blast", "music", "song", "songs",
    "track", "tracks", "tune", "tunes", "something", "anything", "by", "of",
    "from", "random", "little", "bit", "your", "my", "good", "nice", "cool",
    "one", "to", "listen", "i", "want", "like", "let", "lets", "let's", "us",
    # Hebrew
    "לי", "לנו", "את", "שיר", "שירים", "מוזיקה", "של", "קצת", "משהו", "בבקשה",
    "תנגן", "נגן", "תשים", "שים", "וולי", "וול", "אי", "איזה", "כלשהו", "אחד",
}


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9'\u05d0-\u05ea]+", text.lower())


def _speakable(text: str) -> bool:
    """Latin letters only: the English voice cannot read Hebrew and the like."""
    return not re.search(r"[^\x00-ɏ -⁯]", text)


def song_name(path: Path) -> str:
    """ "Billy Joel - Piano Man.mp3" -> "Piano Man by Billy Joel"."""
    stem = re.sub(r"[\[(].*?[\])]", "", path.stem)  # (Official Video), [320k]
    stem = re.sub(r"^\d+[\s._-]+", "", stem)  # track numbers
    stem = re.sub(r"[_]+", " ", stem).strip()
    if " - " in stem:
        artist, title = (s.strip() for s in stem.split(" - ", 1))
        return f"{title} by {artist}"
    return stem


@dataclass
class Command:
    line: str  # what WALL-E says
    after: Callable[[], None] | None = None  # run once he has said it
    # Run *before* speaking; returns the line. Spotify: start the song, see
    # it really plays, then name the song that did.
    first: Callable[[], str] | None = None


class MusicPlayer:
    def __init__(self, folder: Path = MUSIC_DIR) -> None:
        self.folder = folder
        self.folder.mkdir(parents=True, exist_ok=True)
        self.now: str | None = None
        self._path: Path | None = None
        self._q: queue.Queue = queue.Queue(maxsize=48)  # ~1.5 s of decoded audio
        self._gen = 0  # bumped on stop/next: stale decoder threads quit
        self._cur: np.ndarray | None = None
        self._pos = 0
        self._gain = 0.0
        self._level = 1.0  # 1.0 normal, DUCK when ducked
        self._playing = False
        self._stream = None
        from spotify_player import Spotify

        self.spotify = Spotify()  # empty until spotify_sync.py has run

    @property
    def playing(self) -> bool:
        return self._playing or self.spotify.active

    # ----- songs ---------------------------------------------------------
    def songs(self) -> list[Path]:
        return sorted(
            p for p in self.folder.rglob("*") if p.suffix.lower() in AUDIO_EXT and p.is_file()
        )

    def find(self, query: str) -> Path | None:
        """Best file-name match for the words in query, or None."""
        want = [w for w in _words(query) if w not in _FILLER]
        if not want:
            return None
        best: list[Path] = []
        for p in self.songs():
            have = _words(p.stem)
            score = sum(
                1 for w in want if w in have or (len(w) >= 4 and any(h.startswith(w) for h in have))
            )
            if score < len(want):
                continue  # every asked word must match, as for Spotify
            best.append(p)
        return random.choice(best) if best else None

    # ----- voice commands ------------------------------------------------
    def command(self, text: str) -> Command | None:
        """A music command in what was said, or None to let the brain answer."""
        sp = self.spotify
        if _STOP.search(text):
            if not self.playing:
                return Command(t("Nothing is playing.", "שום דבר לא מתנגן."))
            self.stop()
            sp.pause()
            return Command(t("Okay, music off.", "בסדר, כיביתי את המוזיקה."))
        if _WHAT.search(text):
            now = sp.now() if sp.active else self.now if self._playing else None
            return Command(t(f"This is {now}.", f"זה {now}.") if now else t("Nothing is playing right now.", "שום דבר לא מתנגן עכשיו."))
        if _NEXT.search(text) and self.playing:
            if sp.active:
                return Command(t("Next one!", "הבא!"), sp.next)
            nxt = self._pick(exclude=self._path)
            if nxt is None:
                return Command(t("That is the only song I have.", "זה השיר היחיד שיש לי."))
            return Command(t(f"Next one: {song_name(nxt)}.", f"הבא: {song_name(nxt)}."), lambda: self.play(nxt))
        m = _PLAY.search(text)
        if m is None:
            return None
        query = m.group("q") or m.group("q2") or m.group("q3") or ""
        wanted = [w for w in _words(query) if w not in _FILLER]
        # "play a game", "play with me": not music. With 3,751 Spotify songs
        # some title always matches ("Tender Games"), so these words win
        # unless music is named outright.
        # Two or more words that all match a title still win: "play Piano Man".
        if _NOT_MUSIC.search(query) and not re.search(r"\b(song|music|track|playlist)\b|שיר|מוזיקה|פלייליסט", query, re.IGNORECASE):
            if len(wanted) < 2 or (self.find(query) is None and sp.find(query, _FILLER) is None):
                return None
        if re.search(r"\bspotify\b", query, re.IGNORECASE) and not [w for w in wanted if w != "spotify"]:
            if not sp.running():
                return Command(t("Spotify is not open on my laptop.", "ספוטיפיי לא פתוח במחשב שלי."))
            self.stop()
            return Command(t("Okay, Spotify!", "בסדר, ספוטיפיי!"), sp.resume)
        # Asked for something: the music folder first, then the Spotify list.
        if wanted:
            song = self.find(query)
            if song is not None:
                return Command(t(f"Here's {song_name(song)}.", f"הנה {song_name(song)}."), lambda: self._local(song))
            hit = sp.find(query, _FILLER) if sp.ready else None
            if hit is not None:
                return self._spotify(*hit)
        # Anything, or nothing matched: a random song from wherever there is one.
        song = self._pick(exclude=self._path)
        if song is not None:
            say = t(f"Here's {song_name(song)}", f"הנה {song_name(song)}")
            if wanted:
                say = t(f"I don't have {' '.join(wanted)}. {say} instead", f"אין לי {' '.join(wanted)}. {say} במקום")
            return Command(say + "!", lambda: self._local(song))
        if sp.ready:
            return self._spotify("any", None, t(f"I don't have {' '.join(wanted)}. ", f"אין לי {' '.join(wanted)}. ") if wanted else "")
        return Command(t("My music folder is empty. Put some songs in it and ask me again.", "תיקיית המוזיקה שלי ריקה. תשים בה שירים ותבקש שוב."))

    def _local(self, song: Path) -> None:
        self.spotify.pause()
        self.play(song)

    def _spotify(self, kind: str, item, prefix: str = "") -> Command:
        if not self.spotify.running():
            return Command(t("Spotify is not open on my laptop.", "ספוטיפיי לא פתוח במחשב שלי."))

        def go() -> str:
            self.stop()
            tr = self.spotify.play(kind, item)
            if tr is None:
                return prefix + t("I couldn't start that one. It may not be downloaded.", "לא הצלחתי להפעיל את זה. אולי הוא לא הורד.")
            if kind == "playlist":
                album = item.get("album")
                name = item["name"].replace("ClaudeDJ / ", "")
                if hebrew():
                    return prefix + f"הנה {'האלבום' if album else 'הפלייליסט'} {name}."
                what = "album" if album else "playlist"
                return prefix + (f"Here's your {name} {what}." if _speakable(name) else f"Here's your {what}.")
            if hebrew():  # the Hebrew voice reads Hebrew names; English ones it only tries
                artists = tr.get("artists", [])[:2]
                return prefix + f"הנה {tr['name']}" + (f" של {', '.join(artists)}." if artists else ".")
            artists = [a for a in tr.get("artists", [])[:2] if _speakable(a)]
            if _speakable(tr["name"]):
                return prefix + f"Here's {tr['name']}" + (f" by {', '.join(artists)}." if artists else ".")
            # Kokoro speaks English only: "Here's סטלות" comes out as noise.
            return prefix + (f"Here's a song by {', '.join(artists)}." if artists else "Here's a song for you.")

        return Command("", first=go)

    # ----- playback ------------------------------------------------------
    def _pick(self, exclude: Path | None = None) -> Path | None:
        songs = self.songs()
        others = [p for p in songs if p != exclude]
        return random.choice(others or songs) if songs else None

    def play(self, path: Path) -> None:
        self.stop()
        self._open()
        gen = self._gen
        self._playing = True
        threading.Thread(target=self._feed, args=(gen, path), daemon=True).start()

    def stop(self) -> None:
        self._gen += 1
        self._playing = False
        self.now = None
        self._path = None
        while True:
            try:
                self._q.get_nowait()
            except queue.Empty:
                break
        self._cur = None

    def duck(self, on: bool) -> None:
        self._level = DUCK if on else 1.0
        try:
            self.spotify.duck(on, DUCK)
        except Exception as exc:  # noqa: BLE001 — a mixer hiccup must not stop the talk
            print(f"(spotify duck failed: {exc})")

    def close(self) -> None:
        self.duck(False)  # never leave Spotify at 20% when WALL-E quits
        self.stop()
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def _open(self) -> None:
        if self._stream is not None:
            return
        import sounddevice as sd

        self._stream = sd.OutputStream(
            samplerate=SR, channels=2, dtype="float32", blocksize=1024, callback=self._callback
        )
        self._stream.start()

    def _put(self, gen: int, item) -> bool:
        while gen == self._gen:
            try:
                self._q.put(item, timeout=0.2)
                return True
            except queue.Full:
                continue
        return False

    def _feed(self, gen: int, path: Path) -> None:
        """Decode songs into the queue, one after another, until stopped."""
        import av

        while gen == self._gen and path is not None:
            if not self._put(gen, ("song", path)):
                return
            try:
                with av.open(str(path)) as container:
                    resampler = av.AudioResampler(format="flt", layout="stereo", rate=SR)
                    for frame in container.decode(audio=0):
                        for out in resampler.resample(frame):
                            chunk = out.to_ndarray().reshape(-1, 2).astype(np.float32)
                            if not self._put(gen, ("pcm", chunk)):
                                return
            except Exception as exc:  # noqa: BLE001 — a bad file skips to the next
                print(f"(music: cannot play {path.name}: {exc})")
            path = self._pick(exclude=path)

    def _callback(self, outdata, frames, _time, _status) -> None:
        out = np.zeros((frames, 2), dtype=np.float32)
        filled = 0
        while filled < frames:
            if self._cur is None or self._pos >= len(self._cur):
                try:
                    kind, item = self._q.get_nowait()
                except queue.Empty:
                    break
                if kind == "song":
                    self._path, self.now = item, song_name(item)
                    continue
                self._cur, self._pos = item, 0
            n = min(frames - filled, len(self._cur) - self._pos)
            out[filled : filled + n] = self._cur[self._pos : self._pos + n]
            self._pos += n
            filled += n
        # Glide the volume (no clicks when ducking): ~0.3 s from full to DUCK.
        target = self._level if self._playing else 0.0
        g1 = self._gain + float(np.clip(target - self._gain, -0.06, 0.06))
        out *= np.linspace(self._gain, g1, frames, dtype=np.float32)[:, None]
        self._gain = g1
        outdata[:] = out
