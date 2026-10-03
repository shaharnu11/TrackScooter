"""Drive the Spotify desktop app from WALL-E, offline.

The song list comes from scripts/spotify_sync.py (spotify/library.json), made at home
while online. Here, with no internet:

  - a song or playlist is handed to the app by its spotify: link, and the app
    plays its downloaded copy;
  - next / pause / play are the Windows media keys, which Spotify obeys even
    minimised;
  - "what's playing" is the Spotify window title, "Artist - Song";
  - ducking sets Spotify's own volume in the Windows mixer (pycaw).

On the Mac the same four go through AppleScript (osascript): play track,
next track / playpause, the current track, and Spotify's own sound volume.
The first use asks once to let the terminal control Spotify: allow it.

Windows and Mac. Needs the desktop app (the web player cannot play offline),
logged in, with the playlists downloaded.
"""

from __future__ import annotations

from walle.paths import BRAIN

import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path

LIBRARY = BRAIN / "spotify" / "library.json"
BAD = LIBRARY.parent / "not_downloaded.json"  # songs that would not start
TRIES = 3  # songs to try before giving up on a request
START_WAIT = 6.0  # seconds a song gets to start playing

VK_NEXT, VK_PREV, VK_STOP, VK_PLAY_PAUSE = 0xB0, 0xB1, 0xB2, 0xB3
_IDLE_TITLES = {"spotify", "spotify premium", "spotify free", ""}


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9'\u05d0-\u05ea]+", text.lower())


def _same(title: str, t: dict) -> bool:
    """Is the Spotify title "Artist - Song" this track? Loose on purpose:
    the title shows one artist and can shorten "feat." parts."""
    title = title.lower()
    name = re.split(r"\s[-(]", t["name"].lower())[0].strip()
    return bool(name) and name in title


def _osa(script: str) -> str | None:
    """Run one AppleScript; its output, or None if it failed."""
    try:
        r = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, timeout=5
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def _mac_running() -> bool:
    # Asking this does not start the app; "tell application" would.
    return _osa('application "Spotify" is running') == "true"


def _mac_tell(command: str) -> str | None:
    if not _mac_running():
        return None
    return _osa(f'tell application "Spotify" to {command}')


_MAC_KEYS = {VK_NEXT: "next track", VK_PREV: "previous track", VK_STOP: "pause", VK_PLAY_PAUSE: "playpause"}


def _key(vk: int) -> None:
    if sys.platform == "darwin":
        _mac_tell(_MAC_KEYS[vk])
        return
    if sys.platform != "win32":
        return
    import ctypes

    user32 = ctypes.windll.user32
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, 2, 0)  # KEYEVENTF_KEYUP


def _open(uri: str, context: str | None) -> None:
    """Hand one song to the app, inside its list when there is one."""
    if sys.platform == "darwin":
        _mac_tell(f'play track "{uri}"' + (f' in context "{context}"' if context else ""))
    else:
        os.startfile(uri + (f"?context={context}" if context else ""))


def _spotify_title() -> str | None:
    """The Spotify main window title, or None if the app is not running.

    The Mac has no such title: build the same "Artist - Song" from the
    current track while it plays, and the idle "Spotify" when it does not.
    """
    if sys.platform == "darwin":
        if not _mac_running():
            return None
        title = _osa(
            'tell application "Spotify"\n'
            'if player state is playing then return (artist of current track) & " - " & (name of current track)\n'
            'return "Spotify"\n'
            "end tell"
        )
        return title or "Spotify"
    if sys.platform != "win32":
        return None
    import ctypes
    from ctypes import wintypes

    user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
    titles: list[str] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def each(hwnd, _lp):
        if not user32.IsWindowVisible(hwnd):
            return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h = kernel32.OpenProcess(0x1000, False, pid.value)  # QUERY_LIMITED_INFORMATION
        if not h:
            return True
        buf = ctypes.create_unicode_buffer(260)
        size = wintypes.DWORD(260)
        ok = kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size))
        kernel32.CloseHandle(h)
        if ok and buf.value.lower().endswith("spotify.exe"):
            n = user32.GetWindowTextLengthW(hwnd)
            if n:
                t = ctypes.create_unicode_buffer(n + 1)
                user32.GetWindowTextW(hwnd, t, n + 1)
                titles.append(t.value)
        return True

    user32.EnumWindows(each, 0)
    return titles[0] if titles else None


class Spotify:
    def __init__(self, library: Path = LIBRARY) -> None:
        self.tracks: list[dict] = []
        self.lists: list[dict] = []
        self.synced = ""
        if library.exists():
            data = json.loads(library.read_text(encoding="utf-8"))
            self.tracks = data.get("tracks", [])
            self.lists = data.get("playlists", [])
            self.synced = data.get("synced", "")
        self.active = False  # WALL-E started Spotify music this session
        self._volume = None  # Spotify's mixer level before ducking
        self._jobs = None  # the Mac: ducking runs on its own thread
        self.bad: set[str] = set(json.loads(BAD.read_text(encoding="utf-8"))) if BAD.exists() else set()

    @property
    def ready(self) -> bool:
        return sys.platform in ("win32", "darwin") and bool(self.tracks)

    def running(self) -> bool:
        return _spotify_title() is not None

    # ----- finding ---------------------------------------------------------
    def find(self, query: str, filler: set[str]) -> tuple[str, dict] | None:
        """("playlist", p) or ("track", t) best matching the words, or None."""
        want = [w for w in _words(query) if w not in filler and w != "playlist"]
        if not want:
            return None

        def score(text: str) -> int:
            have = _words(text)
            return sum(
                1 for w in want if w in have or (len(w) >= 4 and any(h.startswith(w) for h in have))
            )

        # A playlist wins when every asked word is in its name: "my desert mix".
        lists = [(score(p["name"]), p) for p in self.lists]
        best_list = max(lists, key=lambda x: x[0], default=(0, None))
        if best_list[1] is not None and best_list[0] == len(want):
            return "playlist", best_list[1]
        # Every asked word must match: half a match played a "Billy Esteban
        # Remix" for "play Billy Joel".
        scored = [(score(f"{t['name']} {' '.join(t['artists'])} {t['album']}"), t) for t in self.tracks]
        full = [t for s, t in scored if s == len(want)]
        return ("tracks", full) if full else None

    # ----- playing -----------------------------------------------------------
    def play(self, kind: str, item) -> dict | None:
        """Start music and check it really plays. Returns the playing track.

        kind: "playlist" (item = a list), "tracks" (item = matching songs) or
        "any" (item unused). There is no way to ask Spotify which songs are
        downloaded (offline_lists.bnk is a cache of recently opened lists,
        not downloads), so try up to TRIES songs and watch the window title.
        A song that does not start is remembered in not_downloaded.json and
        never picked again.

        Songs start inside a list (?context=<playlist>) so the music carries
        on afterwards: a bare playlist link only opens its page.
        """
        accept: list[dict] = []
        if kind == "playlist":
            pool = [t for t in self.tracks if item["name"] in t.get("playlists", [])]
            accept, context = pool, item["uri"]
        elif kind == "tracks":
            pool, context = list(item), None
        else:
            pool, context = list(self.tracks), None
        pool = [t for t in pool if t["uri"] not in self.bad]
        random.shuffle(pool)
        for t in pool[:TRIES]:
            playing = self._start(t, context or self._context_of(t))
            if playing is not None and _same(playing, t):
                return t
            self._forget(t)
            # Offline, Spotify skips an undownloaded song to the next one in
            # the list: fine for a playlist request, wrong for "play Omer Adam".
            if playing is not None and accept:
                hit = next((a for a in accept if _same(playing, a)), None)
                if hit is not None:
                    return hit
        self.pause()
        return None

    def _context_of(self, t: dict) -> str | None:
        names = t.get("playlists", [])
        return next((p["uri"] for p in self.lists if names and p["name"] == names[0]), None)

    def _forget(self, t: dict) -> None:
        print(f"(spotify: {t['name']} did not play: not downloaded? skipping it from now on)")
        self.bad.add(t["uri"])
        BAD.parent.mkdir(parents=True, exist_ok=True)
        BAD.write_text(json.dumps(sorted(self.bad), indent=0), encoding="utf-8")

    def _start(self, t: dict, context: str | None) -> str | None:
        """Open one song; return the Spotify title once a song plays, or None.

        Tested on the laptop: opening Piano Man played it at 2 s, then it
        stopped by itself at 4 s; one play key press started it for good.
        While a song plays, the app ignores a new link (Haul kept playing over
        "play Felix Dickinson"), so pause first.
        """
        if self.now() is not None:
            _key(VK_PLAY_PAUSE)
            time.sleep(0.5)
        before = _spotify_title()
        _open(t["uri"], context)
        self.active = True
        pressed = False
        t0 = time.monotonic()
        while time.monotonic() - t0 < START_WAIT:
            time.sleep(0.3)
            title = _spotify_title() or ""
            if " - " in title and title != before:
                time.sleep(1.5)  # it can stop again after ~2 s: check once more
                title = _spotify_title() or ""
                if " - " in title:
                    return title
            if not pressed and time.monotonic() - t0 > 2.5:
                _key(VK_PLAY_PAUSE)
                pressed = True
        return None

    def now(self) -> str | None:
        """ "Piano Man by Billy Joel" while playing, else None."""
        title = _spotify_title()
        if title is None or title.strip().lower() in _IDLE_TITLES or " - " not in title:
            return None
        artist, song = title.split(" - ", 1)
        return f"{song} by {artist}"

    def next(self) -> None:
        _key(VK_NEXT)

    def pause(self) -> None:
        if self.now() is not None:  # the key toggles: only press it when playing
            _key(VK_PLAY_PAUSE)
        self.active = False

    def resume(self) -> None:
        if self.now() is None:
            _key(VK_PLAY_PAUSE)
        self.active = True

    # ----- ducking -----------------------------------------------------------
    def duck(self, on: bool, level: float) -> None:
        """Lower Spotify in the Windows mixer while WALL-E listens or talks."""
        if sys.platform == "darwin":
            if self.active or not on:
                self._duck_mac(on, level)
            return
        if not self.active and self._volume is None:
            return  # nothing of ours playing, nothing to restore
        # (Restoring must work after a pause: "stop the music" is heard while
        # ducked, and Spotify would stay at 20% for good.)
        try:
            from pycaw.pycaw import AudioUtilities
        except ImportError:
            return
        for s in AudioUtilities.GetAllSessions():
            if s.Process is None or s.Process.name().lower() != "spotify.exe":
                continue
            vol = s.SimpleAudioVolume
            if on:
                if self._volume is None:
                    # Below 0.3 is a duck left over from a run that ended
                    # mid-sentence, not the real level: ducking that again
                    # left Spotify at 4%.
                    level_now = vol.GetMasterVolume()
                    self._volume = level_now if level_now >= 0.3 else 1.0
                vol.SetMasterVolume(self._volume * level, None)
            elif self._volume is not None:
                vol.SetMasterVolume(self._volume, None)
        if not on:
            self._volume = None

    def _duck_mac(self, on: bool, level: float) -> None:
        """The same on the Mac: Spotify's own volume, 0-100, by AppleScript.

        On its own thread, in order: a call takes ~0.1-0.2 s, and that long a
        stop inside the mic loop (ducking starts there) made it drop audio.
        """
        if self._jobs is None:
            import queue
            import threading

            self._jobs = queue.Queue()
            threading.Thread(target=self._duck_mac_worker, daemon=True).start()
        self._jobs.put((on, level))
        if not on:
            self._jobs.join()  # restored for sure, also when WALL-E quits

    def _duck_mac_worker(self) -> None:
        while True:
            on, level = self._jobs.get()
            try:
                self._duck_mac_now(on, level)
            except Exception as exc:  # noqa: BLE001 — a hiccup must not end the thread
                print(f"(spotify duck failed: {exc})")
            finally:
                self._jobs.task_done()

    def _duck_mac_now(self, on: bool, level: float) -> None:
        if on and self._volume is None:
            if not _mac_running():
                return
            # Read and lower in one call. Below 30 is a duck left over from a
            # run that ended mid-sentence, as on Windows.
            now = _osa(
                'tell application "Spotify"\n'
                "set v to sound volume\n"
                "if v < 30 then set v to 100\n"
                f"set sound volume to round (v * {level})\n"
                "return v\n"
                "end tell"
            )
            if now is not None and now.isdigit():
                self._volume = int(now)
        elif on:
            _mac_tell(f"set sound volume to {round(self._volume * level)}")
        elif self._volume is not None:
            # Spotify lands one below what it is told (48 reads back as 47),
            # except at 100: ask for one more, or every duck costs a step.
            _mac_tell(f"set sound volume to {min(100, self._volume + 1)}")
            self._volume = None
