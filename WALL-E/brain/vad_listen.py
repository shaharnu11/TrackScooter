"""Speech-triggered listening, for loud places: music, crowds, wind, fans.

listen() in talk_hebrew.py starts on loudness (3.5x the room level) or on
mouth motion. At home that threw away 29 of 36 clips: a laptop fan kept the
level high and mouth motion on the ELP camera fires on a still face. In the
desert, with music, loudness says nothing at all.

Here Silero VAD (the one inside faster-whisper, CPU, ~2 MB) scores every
32 ms of sound for *speech*. A recording starts only after a quarter second
of speech while a face is locked, and ends after 0.8 s without speech.
Music and noise still move the level; they do not move the speech score
much. Singing does, which is why the face lock stays.
"""

from __future__ import annotations

import collections
import time

import numpy as np

SR = 16000
BLOCK = 512  # 32 ms, the size Silero is trained on
BLOCK_S = BLOCK / SR
# The camera window is redrawn once per read. Redrawing every 32 ms fell
# behind the mic: the stream overflowed, dropped audio, and Silero scored
# the chopped speech ~0. So read 3 blocks (96 ms) per redraw.
READ = 3 * BLOCK
CONTEXT = 64


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
    end_s: float = 0.8,
    min_speech_s: float = 0.4,
    preroll_s: float = 0.5,
    on: float = 0.6,
    off: float = 0.35,
    face_grace_s: float = 1.0,
):
    """Wait for speech (from the locked face, if there is a camera), record it.

    Returns (samples, SR), None for nothing worth sending to Whisper, or
    False if q was pressed in the camera window.
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
    with sd.InputStream(samplerate=SR, channels=1, dtype="float32", blocksize=BLOCK) as stream:
        while not done:
            if cam is not None and not cam.pump():
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
                    run = run + 1 if (p > on and face) else 0
                    preroll.append(x)
                    if now - last_log > 2.0:
                        rms = float(np.sqrt(np.mean(audio * audio) + 1e-12))
                        print(
                            f"speech {peak_p:.2f}  level {rms:.3f}  face {face}"
                            + (f"  OVERFLOW x{overflows}" if overflows else "")
                        )
                        last_log = now
                        peak_p = 0.0
                    if run * BLOCK_S >= start_s:
                        print("Speak now…")
                        recording = True
                        chunks = list(preroll)
                        speech_blocks = run
                        quiet = 0.0
                        t0 = time.monotonic()
                    continue
                chunks.append(x)
                if p > on:
                    speech_blocks += 1
                quiet = quiet + BLOCK_S if p < off else 0.0
                if quiet >= end_s or time.monotonic() - t0 >= max_s:
                    done = True
                    break
    if speech_blocks * BLOCK_S < min_speech_s:
        return None
    return np.concatenate(chunks), SR
