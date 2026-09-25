#!/usr/bin/env python3
"""See speaker-lock on a USB webcam.

Green box = the person the robot would look at.
Grey box = other faces.

    cd WALL-E/brain
    .venv/bin/python try_speaker_lock.py
    WALLE_CAMERA=1 .venv/bin/python try_speaker_lock.py
"""

from __future__ import annotations

import sys
import time

from perception import Person
from speaker_lock import SpeakerLock
from usb_camera import UsbCamera


def main() -> int:
    cam = UsbCamera()
    if not cam.open():
        print(cam.last_error or "No camera.")
        return 1
    lock = SpeakerLock()
    print(f"Camera {cam.device}. Talk. q quits.")
    try:
        import cv2
    except ImportError:
        print("opencv-python is not installed. Use WALL-E/brain/.venv")
        cam.close()
        return 1

    misses = 0
    try:
        while True:
            obs, frame = cam.read()
            if frame is None:
                misses += 1
                if misses > 60:
                    print("Camera opened, then stopped sending frames.")
                    return 1
                time.sleep(0.03)
                continue
            misses = 0
            people = [
                Person(
                    az_deg=o.az_deg,
                    el_deg=o.el_deg,
                    distance_m=o.distance_m,
                    confidence=o.confidence,
                    track_id=o.track_id,
                    speaking=o.speaking,
                )
                for o in obs
            ]
            sid = lock.update(people, time.monotonic())
            for o in obs:
                x, y, w, h = o.box
                is_focus = sid is not None and o.track_id == sid
                color = (0, 220, 0) if is_focus else (160, 160, 160)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                label = "SPEAKER" if is_focus else ("talk" if o.speaking else "")
                if label:
                    cv2.putText(
                        frame, label, (x, max(20, y - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
                    )
            status = f"faces {len(obs)}"
            if sid is not None:
                status += f"  lock {sid}"
            cv2.putText(
                frame, status, (12, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 0), 2,
            )
            try:
                cv2.imshow("WALL-E speaker lock", frame)
            except cv2.error:
                print("No GUI window. Run this in Terminal.app, not over SSH.")
                return 1
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cam.close()
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
