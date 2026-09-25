#!/usr/bin/env python3
"""Live camera + mic check. No language model. q to quit."""

from __future__ import annotations

import time

import numpy as np
import sounddevice as sd

from usb_camera import UsbCamera


def main() -> int:
    cam = UsbCamera()
    cam.max_faces = 1
    cam.min_rel_h = 0.08
    cam.min_score = 0.55
    if not cam.open():
        print(cam.last_error or "No camera")
        return 1
    print(f"Camera device {cam.device}. Talk. q quits.", flush=True)
    import cv2

    sr = 16000
    block = int(sr * 0.1)
    last_print = 0.0
    with sd.InputStream(samplerate=sr, channels=1, dtype="float32") as stream:
        while True:
            obs, frame = cam.read()
            data, _ = stream.read(block)
            x = np.asarray(data, dtype=np.float32).reshape(-1)
            rms = float(np.sqrt(np.mean(x * x) + 1e-12))
            if frame is None:
                time.sleep(0.03)
                continue
            for o in obs:
                x0, y0, w, h = o.box
                cv2.rectangle(frame, (x0, y0), (x0 + w, y0 + h), (0, 255, 0), 3)
                cv2.putText(
                    frame,
                    f"YOU m={o.mouth_ema:.1f} talk={int(o.speaking)}",
                    (x0, max(28, y0 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
            msg = f"faces {len(obs)}  rms {rms:.3f}"
            if not obs:
                msg = "NO FACE  " + msg
            cv2.putText(
                frame, msg, (12, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
            )
            now = time.monotonic()
            if now - last_print > 0.4:
                if obs:
                    o = obs[0]
                    print(
                        f"faces={len(obs)} box={o.box} ema={o.mouth_ema:.1f} "
                        f"talk={o.speaking} rms={rms:.3f}",
                        flush=True,
                    )
                else:
                    print(f"faces=0 rms={rms:.3f}", flush=True)
                last_print = now
            cv2.imshow("WALL-E debug", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    cam.close()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
