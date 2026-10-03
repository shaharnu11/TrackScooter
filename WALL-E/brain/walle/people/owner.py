#!/usr/bin/env python3
"""Is this Shahar? Face + secret word, for "update personality start".

WALL-E only checks when he hears that phrase: nothing is recognised or
stored for anyone else, ever.

    python -m walle.people.owner enroll    # once: learn the face, set the secret word

Face: OpenCV's SFace recognizer on the face YuNet already finds (the same
detector as walle/eyes/camera.py), CPU only. A face counts as Shahar's when its
cosine similarity to the enrolled ones reaches SFACE_MATCH, OpenCV's own
threshold for this model, in at least 2 of the frames checked.

Secret word: typed once at enrollment and stored only as a salted SHA-256.
At check time it is spoken, so Whisper's text is compared: pick plain
English words (e.g. "purple giraffe"), not numbers or names Whisper might
spell differently.

owner/ holds both files and is not in git.
"""

from __future__ import annotations

from walle.paths import BRAIN

import hashlib
import json
import re
import secrets
import sys
import time
from pathlib import Path

import numpy as np

ROOT = BRAIN
OWNER_DIR = ROOT / "owner"
FACE_FILE = OWNER_DIR / "face.npy"
SECRET_FILE = OWNER_DIR / "secret.json"
SFACE_PATH = ROOT / "models" / "camera" / "face_recognition_sface_2021dec.onnx"
SFACE_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/"
    "models/face_recognition_sface/face_recognition_sface_2021dec.onnx"
)
SFACE_MATCH = 0.363  # OpenCV's cosine threshold for SFace
FRAMES_NEEDED = 2


def _norm_words(text: str) -> str:
    # Letters and digits only, no spaces: typed "holycow" and Whisper's
    # "Holy cow!" are the same secret (the space broke the first live try).
    return "".join(re.findall(r"[a-z0-9]+", text.lower()))


def _hash(salt: str, words: str) -> str:
    return hashlib.sha256((salt + words).encode("utf-8")).hexdigest()


class Owner:
    def __init__(self) -> None:
        self.faces = np.load(FACE_FILE) if FACE_FILE.exists() else None
        self.secret = json.loads(SECRET_FILE.read_text(encoding="utf-8")) if SECRET_FILE.exists() else None
        self._det = None
        self._rec = None

    @property
    def enrolled(self) -> bool:
        return self.faces is not None and len(self.faces) > 0 and self.secret is not None

    # ----- face ------------------------------------------------------------
    def _models(self):
        import cv2

        from walle.eyes.camera import _ensure_yunet

        if self._det is None:
            if not SFACE_PATH.exists():
                import urllib.request

                urllib.request.urlretrieve(SFACE_URL, SFACE_PATH)
            self._det = cv2.FaceDetectorYN.create(str(_ensure_yunet()), "", (320, 320), 0.7, 0.3)
            self._rec = cv2.FaceRecognizerSF.create(str(SFACE_PATH), "")
        return self._det, self._rec

    def feature(self, frame) -> np.ndarray | None:
        """SFace feature of the biggest face in the frame, or None."""
        det, rec = self._models()
        h, w = frame.shape[:2]
        det.setInputSize((w, h))
        _ok, faces = det.detect(frame)
        if faces is None or len(faces) == 0:
            return None
        face = max(faces, key=lambda f: f[2] * f[3])  # the one in front
        aligned = rec.alignCrop(frame, face)
        return rec.feature(aligned).reshape(-1).copy()

    def similarity(self, feat: np.ndarray) -> float:
        import cv2

        _det, rec = self._models()
        return max(
            float(rec.match(feat.reshape(1, -1), f.reshape(1, -1), cv2.FaceRecognizerSF_FR_COSINE))
            for f in self.faces
        )

    def is_owner(self, frames) -> tuple[bool, float]:
        """True if the face in front matches in at least FRAMES_NEEDED frames."""
        if not self.enrolled:
            return False, 0.0
        best, hits = 0.0, 0
        for frame in frames:
            if frame is None:
                continue
            feat = self.feature(frame)
            if feat is None:
                continue
            s = self.similarity(feat)
            best = max(best, s)
            hits += s >= SFACE_MATCH
        return hits >= FRAMES_NEEDED, best

    # ----- secret word -----------------------------------------------------
    def secret_ok(self, spoken: str) -> bool:
        if not self.secret:
            return False
        return secrets.compare_digest(_hash(self.secret["salt"], _norm_words(spoken)), self.secret["sha256"])


def enroll() -> None:
    """Learn Shahar's face from the ELP camera and set the secret word."""
    import getpass

    from walle.eyes.camera import UsbCamera

    OWNER_DIR.mkdir(parents=True, exist_ok=True)
    owner = Owner()
    cam = UsbCamera()
    if not cam.open():
        sys.exit(cam.last_error or "No camera.")
    print("Look at the camera. Turn your head a little left, right, up and down.")
    feats: list[np.ndarray] = []
    t0 = time.monotonic()
    while len(feats) < 20 and time.monotonic() - t0 < 30:
        _obs, frame = cam.read()
        if frame is None:
            continue
        feat = owner.feature(frame)
        if feat is not None:
            feats.append(feat)
            print(f"  face {len(feats)}/20")
            time.sleep(0.3)
    cam.close()
    if len(feats) < 8:
        sys.exit("Not enough clear frames of your face. Better light, closer, and try again.")
    np.save(FACE_FILE, np.stack(feats))
    print(f"Face saved: {len(feats)} views.")

    print("\nSecret word or words. Plain English words work best (Whisper will hear them).")
    while True:
        a = getpass.getpass("Secret word(s): ")
        b = getpass.getpass("Again: ")
        if _norm_words(a) and _norm_words(a) == _norm_words(b):
            break
        print("Empty or not the same, try again.")
    salt = secrets.token_hex(16)
    SECRET_FILE.write_text(json.dumps({"salt": salt, "sha256": _hash(salt, _norm_words(a))}), encoding="utf-8")
    print(f"Secret saved (hashed). Both in {OWNER_DIR} (not in git).")


if __name__ == "__main__":
    if sys.argv[1:] == ["enroll"]:
        enroll()
    else:
        sys.exit(__doc__)
