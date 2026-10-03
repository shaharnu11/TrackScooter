"""The older loudness / mouth-motion triggers (--trigger loud, and talking with no camera window)."""

from __future__ import annotations

from walle.eyes.talk_cam import TalkCam

import time


def wait_for_mouth(cam: TalkCam | None) -> bool:
    """Wait until the main face is there and someone is loud or the mouth moves."""
    if cam is None:
        return True
    import numpy as np
    import sounddevice as sd

    print("Look at the camera, then speak…")
    sr = 16000
    block = int(sr * 0.1)
    # The trigger follows the room, not a fixed number: a fixed 0.025 suited
    # the Mac's mic but the XPS's Realtek mic never reached it. The floor
    # tracks the quiet level (falls fast, rises slowly), and speech must be
    # 3.5x above it, the same rule record_utterance uses.
    floor: float | None = None
    last_log = 0.0
    with sd.InputStream(samplerate=sr, channels=1, dtype="float32") as stream:
        while True:
            if not cam.pump():
                return False
            data, _overflow = stream.read(block)
            x = np.asarray(data, dtype=np.float32).reshape(-1)
            rms = float(np.sqrt(np.mean(x * x) + 1e-12))
            if floor is None:
                floor = rms
            elif rms < floor:
                floor = 0.7 * floor + 0.3 * rms
            else:
                floor = 0.98 * floor + 0.02 * rms
            thresh = max(0.004, floor * 3.5)
            cam.set_mic(rms, thresh)
            now = time.monotonic()
            if now - last_log > 2.0:
                print(f"mic {rms:.4f}  trigger {thresh:.4f}  face {cam.locked()}")
                last_log = now
            if cam.locked() and (cam.talking() or rms > thresh):
                return True


def record_utterance(
    sr: int = 16000,
    max_s: float = 8.0,
    silence_s: float = 0.7,
    cam: TalkCam | None = None,
):
    import numpy as np
    import sounddevice as sd

    block = int(sr * 0.1)
    chunks: list = []
    voiced = False
    quiet = 0.0
    floors: list[float] = []
    thresh = 0.02
    print("Speak now…")
    beep()
    with sd.InputStream(samplerate=sr, channels=1, dtype="float32") as stream:
        t0 = time.monotonic()
        while True:
            if cam is not None and not cam.pump():
                return None
            data, _overflow = stream.read(block)
            x = np.asarray(data, dtype=np.float32).reshape(-1)
            chunks.append(x.copy())
            rms = float(np.sqrt(np.mean(x * x) + 1e-12))
            if len(floors) < 5:
                floors.append(rms)
                thresh = max(0.004, float(np.median(floors)) * 3.5)
            loud = rms > thresh
            mouth = cam is not None and cam.talking()
            face = cam is None or cam.locked()
            if face and (loud or mouth):
                voiced = True
                quiet = 0.0
            elif voiced:
                quiet += 0.1
                if quiet >= silence_s:
                    break
            if time.monotonic() - t0 >= max_s:
                break
    if not voiced or not chunks:
        return None
    return np.concatenate(chunks), sr


def beep() -> None:
    import numpy as np
    import sounddevice as sd

    sr = 16000
    t = np.linspace(0, 0.12, int(sr * 0.12), False)
    tone = (0.18 * np.sin(2 * np.pi * 880 * t)).astype(np.float32)
    sd.play(tone, sr)
    sd.wait()


def listen(
    cam: TalkCam,
    sr: int = 16000,
    max_s: float = 8.0,
    silence_s: float = 0.8,
    preroll_s: float = 0.5,
):
    """Wait for the locked face to speak, then record it. One mic stream.

    The old wait_for_mouth -> beep -> record_utterance chain closed the mic
    between waiting and recording, so the first word was lost. Worse, the
    recorder took its noise floor from its first 0.5 s, which was the person
    already talking, set the trigger above their own voice and threw the
    clip away ("Heard nothing"). Here the floor is only learned while waiting,
    and the 0.5 s before the trigger is kept.

    Returns (samples, sr), None for nothing heard, or False if q was pressed.
    """
    import collections

    import numpy as np
    import sounddevice as sd

    print("Look at the camera, then speak…")
    block = int(sr * 0.1)
    preroll: collections.deque = collections.deque(maxlen=int(preroll_s / 0.1))
    floor: float | None = None
    thresh = 0.004
    chunks: list = []
    recording = False
    voiced_blocks = 0
    quiet = 0.0
    t0 = 0.0
    last_log = 0.0
    with sd.InputStream(samplerate=sr, channels=1, dtype="float32") as stream:
        while True:
            if not cam.pump():
                return False
            data, _overflow = stream.read(block)
            x = np.asarray(data, dtype=np.float32).reshape(-1).copy()
            rms = float(np.sqrt(np.mean(x * x) + 1e-12))
            loud = rms > thresh
            if not recording:
                # Floor falls fast and rises slowly, so speech barely moves it.
                if floor is None:
                    floor = rms
                elif rms < floor:
                    floor = 0.7 * floor + 0.3 * rms
                else:
                    floor = 0.98 * floor + 0.02 * rms
                thresh = max(0.004, floor * 3.5)
                cam.set_mic(rms, thresh)
                now = time.monotonic()
                if now - last_log > 2.0:
                    print(f"mic {rms:.4f}  trigger {thresh:.4f}  face {cam.locked()}")
                    last_log = now
                preroll.append(x)
                if cam.locked() and (rms > thresh or cam.talking()):
                    print("Speak now…")
                    recording = True
                    chunks = list(preroll)
                    voiced_blocks = 1
                    quiet = 0.0
                    t0 = time.monotonic()
                continue
            # Recording: the trigger level stays frozen at the waiting floor.
            cam.set_mic(rms, thresh)
            chunks.append(x)
            if loud:
                voiced_blocks += 1
                quiet = 0.0
            else:
                quiet += 0.1
            if quiet >= silence_s or time.monotonic() - t0 >= max_s:
                break
    if voiced_blocks < 3:  # under ~0.3 s of sound: a click, not a sentence
        return None
    return np.concatenate(chunks), sr
