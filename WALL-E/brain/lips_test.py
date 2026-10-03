#!/usr/bin/env python3
"""Measure lip activity, quiet vs talking, and suggest LIPS_TALK.

    .venv/bin/python lips_test.py

Look at the camera. WALL-E's voice asks you to stay quiet for 6 s, then to
talk for 6 s. Run it again in new light or with a new camera (the festival).
Use the suggested number with:  WALLE_LIPS_TALK=<number> ./mac/start_walle.command
"""

from __future__ import annotations

import shutil
import subprocess
import time

import numpy as np

from talk_hebrew import TalkCam
from usb_camera import LIPS_TALK


def say(text: str) -> None:
    if shutil.which("say"):
        subprocess.run(["say", text], check=False)
    else:
        print(text)
        time.sleep(1.5)


def grab(cam: TalkCam, secs: float) -> np.ndarray:
    vals = []
    end = time.monotonic() + secs
    while time.monotonic() < end:
        cam.pump()
        m = cam.mouth_level()
        if m is not None:
            vals.append(m)
        time.sleep(0.05)
    return np.array(vals)


def main() -> None:
    cam = TalkCam()
    if not cam.start():
        raise SystemExit("No camera.")
    if not cam.cam.lips:
        raise SystemExit("No lip model: run download_english.py, pip install -r requirements-voice.txt")
    time.sleep(1.0)
    say("Lip test. Look at the camera, and stay quiet for six seconds.")
    quiet = grab(cam, 6)
    say("Now talk to me for six seconds. Say anything.")
    talk = grab(cam, 6)
    say("Thank you. Done.")
    cam.stop()
    if len(quiet) < 20 or len(talk) < 20:
        raise SystemExit(f"Too little face seen (quiet {len(quiet)}, talk {len(talk)} samples). Sit closer, more light.")
    q90, t50 = float(np.percentile(quiet, 90)), float(np.median(talk))
    print(f"quiet: median {np.median(quiet):.2f}  90% below {q90:.2f}  max {quiet.max():.2f}")
    print(f"talk:  10% below {np.percentile(talk, 10):.2f}  median {t50:.2f}  max {talk.max():.2f}")
    if t50 <= q90:
        print("Quiet and talking overlap: the lips check will not work well here. Try more light, or --no-lips.")
        return
    suggest = round(q90 + 0.35 * (t50 - q90), 2)
    print(f"now LIPS_TALK = {LIPS_TALK}; suggested: {suggest}")
    print(f"use it:  WALLE_LIPS_TALK={suggest} ./mac/start_walle.command")


if __name__ == "__main__":
    main()
