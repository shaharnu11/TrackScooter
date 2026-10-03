"""Speech-triggered listening, for loud places: music, crowds, wind, fans.

listen() in talk_hebrew.py starts on loudness (3.5x the room level) or on
mouth motion. At home that threw away 29 of 36 clips: a laptop fan kept the
level high and mouth motion on the ELP camera fires on a still face. In the
desert, with music, loudness says nothing at all.

Here Silero VAD (the one inside faster-whisper, CPU, ~2 MB) scores every
32 ms of sound for *speech*. A recording starts only after a quarter second
of speech while a face is locked, and ends after END_S without speech.
Music and noise still move the level; they do not move the speech score
much. Singing does, which is why the face lock stays.
"""

from __future__ import annotations

import collections
import contextlib
import time
from dataclasses import dataclass

import numpy as np

SR = 16000
BLOCK = 512  # 32 ms, the size Silero is trained on
BLOCK_S = BLOCK / SR
# The camera window is redrawn once per read. Redrawing every 32 ms fell
# behind the mic: the stream overflowed, dropped audio, and Silero scored
# the chopped speech ~0. So read 3 blocks (96 ms) per redraw.
READ = 3 * BLOCK
CONTEXT = 64
# Silence that ends a sentence. Loudness needed 0.8 s to be sure; the speech
# score drops as soon as the voice does, so 0.5 s is enough. A mid-sentence
# pause longer than this gets answered half way: raise it if that happens.
END_S = 0.5


class StreamVAD:
    """Silero VAD run block by block, keeping its state between calls."""

    def __init__(self) -> None:
        from faster_whisper.vad import get_vad_model

        self._session = get_vad_model().session
        self.reset()

    def reset(self) -> None:
        self._h = np.zeros((1, 1, 128), dtype=np.float32)
        self._c = np.zeros((1, 1, 128), dtype=np.float32)
        self._ctx = np.zeros(CONTEXT, dtype=np.float32)

    def __call__(self, block: np.ndarray) -> float:
        x = np.concatenate([self._ctx, block]).astype(np.float32)[None, :]
        out, self._h, self._c = self._session.run(
            None, {"input": x, "h": self._h, "c": self._c}
        )
        self._ctx = block[-CONTEXT:]
        return float(np.asarray(out).reshape(-1)[0])


def listen_vad(
    cam,
    vad: StreamVAD,
    max_s: float = 8.0,
    start_s: float = 0.25,
    end_s: float = END_S,
    min_speech_s: float = 0.4,
    preroll_s: float = 0.5,
    on: float = 0.6,
    off: float = 0.35,
    face_grace_s: float = 1.0,
    on_start=None,
    on_tick=None,
    stream=None,
    busy=None,
    barge_s: float = 0.4,
    quit=None,
):
    """Wait for speech (from the locked face, if there is a camera), record it.

    Returns a Heard (samples + who-is-talking clues), None for nothing
    worth sending to Whisper, or
    False if q was pressed in the camera window. on_start() runs the moment
    a recording starts; on_tick(face_seen) every 32 ms while waiting.

    Barge-in (talk_english.py): stream is the always-on, echo-cancelled mic
    (echo.Mic) instead of a fresh one; while busy() (WALL-E thinking or
    talking) speech must last barge_s to count, so a cough does not cut him
    off; quit (an Event) ends the wait like q does.
    """
    import sounddevice as sd

    print("Look at the camera, then speak…" if cam is not None else "Listening…")
    vad.reset()
    preroll: collections.deque = collections.deque(maxlen=int(preroll_s / BLOCK_S))
    chunks: list[np.ndarray] = []
    recording = False
    run = 0  # consecutive speech blocks while waiting
    speech_blocks = 0
    quiet = 0.0
    t0 = 0.0
    last_log = 0.0
    # The face lock flickers: at home it dropped for a frame or two mid
    # sentence, which reset the speech count and he never heard a thing.
    # A face seen in the last second counts as there.
    last_face = -1e9
    overflows = 0
    peak_p = 0.0
    done = False
    # Who is talking: mouth motion just before vs during the voice, and how
    # loud the voice is (see Gate).
    mouth_hist: collections.deque = collections.deque(maxlen=int(1.5 / BLOCK_S))
    mouth_talk: list[float] = []
    levels: list[float] = []
    mouth_still = None
    opened = (
        contextlib.nullcontext(stream)
        if stream is not None
        else sd.InputStream(samplerate=SR, channels=1, dtype="float32", blocksize=BLOCK)
    )
    with opened as stream:
        while not done:
            if cam is not None and not cam.pump():
                return False
            if quit is not None and quit.is_set():
                return False
            data, overflow = stream.read(READ)
            overflows += bool(overflow)
            audio = np.asarray(data, dtype=np.float32).reshape(-1).copy()
            for x in audio.reshape(-1, BLOCK):
                p = vad(x)
                peak_p = max(peak_p, p)
                if cam is not None:
                    cam.set_mic(p, on)
                if not recording:
                    now = time.monotonic()
                    if cam is None or cam.locked():
                        last_face = now
                    face = now - last_face <= face_grace_s
                    if on_tick is not None:
                        on_tick(cam is not None and face)  # e.g. sleep / wake the GPU models
                    run = run + 1 if (p > on and face) else 0
                    preroll.append(x)
                    m = cam.mouth_level() if cam is not None else None
                    mouth_hist.append(m)
                    if now - last_log > 2.0:
                        rms = float(np.sqrt(np.mean(audio * audio) + 1e-12))
                        print(
                            f"speech {peak_p:.2f}  level {rms:.3f}  face {face}"
                            + (f"  OVERFLOW x{overflows}" if overflows else "")
                        )
                        last_log = now
                        peak_p = 0.0
                    if run * BLOCK_S >= (barge_s if busy is not None and busy() else start_s):
                        print("Speak now…")
                        if on_start is not None:
                            on_start()  # e.g. duck the music under the voice
                        recording = True
                        chunks = list(preroll)
                        speech_blocks = run
                        quiet = 0.0
                        t0 = time.monotonic()
                        hist = list(mouth_hist)
                        before = [v for v in hist[: max(0, len(hist) - run)] if v is not None]
                        mouth_still = float(np.median(before)) if before else None
                        mouth_talk = [v for v in hist[-run:] if v is not None]
                        levels = [_rms(b) for b in chunks[-run:]]
                    continue
                chunks.append(x)
                if p > on:
                    speech_blocks += 1
                    levels.append(_rms(x))
                    m = cam.mouth_level() if cam is not None else None
                    if m is not None:
                        mouth_talk.append(m)
                quiet = quiet + BLOCK_S if p < off else 0.0
                if quiet >= end_s or time.monotonic() - t0 >= max_s:
                    done = True
                    break
    if speech_blocks * BLOCK_S < min_speech_s:
        return None
    return Heard(
        np.concatenate(chunks),
        SR,
        level=float(np.median(levels)) if levels else 0.0,
        mouth_talk=float(np.median(mouth_talk)) if mouth_talk else None,
        mouth_still=mouth_still,
    )


def _rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x * x) + 1e-12))


@dataclass
class Heard:
    samples: np.ndarray
    sr: int
    level: float  # median loudness of the speech blocks
    mouth_talk: float | None  # median mouth motion while the voice was on
    mouth_still: float | None  # ... in the 1.5 s before it started


# Mouth motion (usb_camera mouth_ema) counts as talking above this, as there.
MOUTH_SPEAK = 2.5


class Gate:
    """Is this voice the person in front of WALL-E, or someone else?

    At home a video playing nearby was taken as the person talking: the face
    was locked, and Silero rightly heard speech. Two checks, both relative,
    so they fit any mic and any face:

    - mouth: the locked face's mouth must move more while the voice is on
      than just before it (or clearly, above MOUTH_SPEAK). A still mouth
      under a voice is someone else.
    - near: the voice must not be far quieter than the person talking to
      him has been (median of the last accepted clips); a voice at a third
      of that is someone further away.

    reasons() says why a clip fails; accept() learns from ones that pass.
    """

    MOUTH_RATIO = 1.3
    # Off: usb_camera's mouth motion cannot tell talking from silent on the
    # ELP camera (see _mouth_speaking). The loudness check does the work;
    # it rejected a video at 0.038 against a talker at 0.176.
    MOUTH_CHECK = False
    # Share of the talker's usual level below which a voice is "far away".
    # Was 0.35: with a group, the loudest person set the bar (0.242) and a
    # friend a metre back (0.067-0.084) was ignored four times. 0.25 hears
    # them and still drops the video from the first test (0.038 vs 0.176).
    NEAR_SHARE = 0.25
    LEARN_AFTER = 3  # accepted clips before the loudness check starts
    # Rejected clips never teach the level, so once the talker got quieter
    # (leaned back from the Mac: 0.09 -> 0.007) he was ignored for good.
    # The second "too quiet" in a row starts the level over and is answered.
    RELEARN_AFTER = 2

    def __init__(self) -> None:
        self.levels: collections.deque = collections.deque(maxlen=10)
        self.rejects = 0  # "too quiet" clips in a row

    def reasons(self, h: Heard) -> list[str]:
        why = []
        if self.MOUTH_CHECK and h.mouth_talk is not None and h.mouth_still is not None:
            if h.mouth_talk < MOUTH_SPEAK and h.mouth_talk < self.MOUTH_RATIO * h.mouth_still:
                why.append("mouth did not move")
        if len(self.levels) >= self.LEARN_AFTER:
            usual = float(np.median(self.levels))
            if h.level < self.NEAR_SHARE * usual:
                self.rejects += 1
                if self.rejects >= self.RELEARN_AFTER:
                    print(f"(too quiet {self.rejects} times in a row: learning the voice level again)")
                    self.levels.clear()
                    self.rejects = 0
                else:
                    why.append(f"too quiet for the one in front ({h.level:.3f} vs usual {usual:.3f})")
        return why

    def accept(self, h: Heard) -> None:
        self.rejects = 0
        self.levels.append(h.level)

    def describe(self, h: Heard) -> str:
        mouth = (
            f"mouth {h.mouth_talk:.1f} vs {h.mouth_still:.1f} before"
            if h.mouth_talk is not None and h.mouth_still is not None
            else "mouth ?"
        )
        usual = f", usual {float(np.median(self.levels)):.3f}" if self.levels else ""
        return f"level {h.level:.3f}{usual}; {mouth}"
