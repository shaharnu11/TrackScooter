"""ELP-USB1080P03-KLC1100: faces, mouth motion, angles.

No OAK-D. Person list and speaker cues run on the Brain CPU so the GPU stays
free for the language model. Distance is estimated from face size. Close-range
safety still belongs to the ToF ring on the Spine.

OpenCV 5 dropped Haar CascadeClassifier. Faces use YuNet (FaceDetectorYN).
The ELP LC1100 lens is 86° horizontal. MJPEG is required for 30 fps.
"""

from __future__ import annotations

import collections
import logging
import os
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np

log = logging.getLogger(__name__)

# ELP-USB1080P03-KLC1100. Listing says HOV 86 degree, 16:9.
HFOV_DEG = 86.0
VFOV_DEG = 55.4
MOUTH_SPEAK = 2.5
MATCH_MAX_DEG = 12.0

YUNET_NAME = "face_detection_yunet_2023mar.onnx"
YUNET_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/"
    "models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
YUNET_PATH = Path(__file__).resolve().parent / "models" / "camera" / YUNET_NAME

# Lip landmarks: MediaPipe Face Landmarker (CPU, ~7 ms a frame). Lip
# activity = how much the inner-lip gap (points 13/14, over the eye distance)
# varies in the last LIPS_WINDOW_S, x100. Measured on the Mac camera, Shahar
# ~0.6 m away: quiet median 0.19 (max 0.67), talking median 3.1 (low 0.8).
# OpenCV's Facemark LBF was tried: it jitters, quiet read 2.2-2.6 live, the
# same as talking. MediaPipe 1.0.1 crashes on the Mac (Metal); 0.10.35 runs.
LIPS_MODEL = YUNET_PATH.parent / "face_landmarker.task"
LIPS_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/latest/face_landmarker.task"
)
LIPS_TALK = 0.75
LIPS_WINDOW_S = 0.5


@dataclass
class FaceObs:
    track_id: int
    az_deg: float
    el_deg: float
    distance_m: float
    confidence: float
    speaking: bool
    box: tuple[int, int, int, int] = (0, 0, 0, 0)
    mouth_ema: float = 0.0  # lip activity with LBF, else the old pixel motion


def _ensure_yunet() -> Path:
    if YUNET_PATH.exists() and YUNET_PATH.stat().st_size > 50_000:
        return YUNET_PATH
    YUNET_PATH.parent.mkdir(parents=True, exist_ok=True)
    log.info("downloading YuNet face model")
    urllib.request.urlretrieve(YUNET_URL, YUNET_PATH)
    return YUNET_PATH


class UsbCamera:
    def __init__(self, device: int | None = None) -> None:
        self.device = 0 if device is None else device
        env = os.environ.get("WALLE_CAMERA")
        if env is not None:
            self.device = int(env)
        self._cap = None
        self._det = None
        self._faces = None
        self._size: tuple[int, int] | None = None
        self._prev_mouth: dict[int, np.ndarray] = {}
        self._motion: dict[int, float] = {}
        self._lips_model = None  # MediaPipe Face Landmarker, when installed
        self._lips: dict[int, collections.deque] = {}
        self._t0 = time.monotonic()
        self._next_id = 1
        self._last: list[FaceObs] = []
        self.last_error = ""
        # Talk mode: keep only the biggest real head. Plants become "faces".
        self.max_faces = 0
        self.min_rel_h = 0.0
        self.min_score = 0.5

    def open(self) -> bool:
        try:
            import cv2
        except ImportError:
            self.last_error = "opencv-python is not installed. Use WALL-E/brain/.venv"
            log.warning(self.last_error)
            return False
        if not self._load_detector(cv2):
            return False
        self._load_lips(cv2)
        cap = self._open_capture(cv2)
        if cap is None:
            return False
        self._cap = cap
        log.info("usb camera opened on device %s", self.device)
        return True

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def read(self) -> tuple[list[FaceObs], object | None]:
        """Return people and the BGR frame (frame is None if grab failed)."""
        import cv2

        if self._cap is None:
            return [], None
        try:
            ok, frame = self._cap.read()
        except cv2.error as exc:
            # One bad frame must not kill the camera thread.
            log.warning("camera read failed: %s", exc)
            return [], None
        if not ok or frame is None:
            return [], None
        boxes = self._detect(cv2, frame)
        h, w = frame.shape[:2]
        boxes = self._keep_real_heads(boxes, w, h)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        obs = [self._observe(box, w, h) for box in boxes]
        self._assign_ids(obs)
        gap = self._lip_gap(cv2, frame) if self._lips_model is not None and obs else None
        for i, o in enumerate(obs):
            if self._lips_model is not None:
                # One face measured: the biggest, which is obs[0].
                o.speaking = self._lips_speaking(o, gap if i == 0 else None)
            else:
                o.speaking = self._mouth_speaking(gray, o)
        self._last = obs
        return obs, frame

    def _load_detector(self, cv2) -> bool:
        try:
            path = _ensure_yunet()
            self._det = cv2.FaceDetectorYN.create(str(path), "", (320, 320), 0.55, 0.3)
            self._faces = None
            return True
        except Exception as exc:
            log.warning("YuNet failed (%s); trying Haar", exc)
        if not hasattr(cv2, "CascadeClassifier"):
            self.last_error = (
                "No face detector. OpenCV 5 needs the YuNet file at "
                f"{YUNET_PATH}"
            )
            log.warning(self.last_error)
            return False
        haar = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        clf = cv2.CascadeClassifier(haar)
        if clf.empty():
            self.last_error = f"Haar file missing: {haar}"
            log.warning(self.last_error)
            return False
        self._faces = clf
        self._det = None
        return True

    def _open_capture(self, cv2):
        if os.environ.get("WALLE_CAMERA") is not None:
            indices = [self.device]
        else:
            indices = list(dict.fromkeys([self.device, 0, 1, 2]))
        backends = []
        if sys.platform == "darwin":
            backends.append(cv2.CAP_AVFOUNDATION)
        elif sys.platform == "win32":
            # The default Media Foundation backend breaks after the MJPG
            # switch below (_step >= minstep). DirectShow takes it.
            backends.append(cv2.CAP_DSHOW)
        backends.append(cv2.CAP_ANY)
        for index in indices:
            for backend in backends:
                cap = cv2.VideoCapture(index, backend)
                if not cap.isOpened():
                    cap.release()
                    continue
                ok, frame = cap.read()
                if ok and frame is not None:
                    self.device = index
                    # YUY2 on this ELP is 5 fps at 1080p. MJPEG is 30 fps.
                    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    return cap
                cap.release()
        hint = ""
        if sys.platform == "darwin":
            hint = (
                " macOS blocked the camera. System Settings > Privacy & Security"
                " > Camera: turn on Terminal (or Cursor), then run this again"
                " from that app. Do not run it from a sandbox."
            )
        self.last_error = (
            f"No camera on device {self.device}."
            " Plug in a USB webcam, or set WALLE_CAMERA=0"
            + hint
        )
        log.warning(self.last_error)
        return None

    def _detect(self, cv2, frame) -> list[tuple[int, int, int, int, float]]:
        h, w = frame.shape[:2]
        if self._det is not None:
            size = (w, h)
            if self._size != size:
                self._det.setInputSize(size)
                self._size = size
            _ok, faces = self._det.detect(frame)
            if faces is None:
                return []
            out = []
            for row in faces:
                x, y, bw, bh = [int(v) for v in row[:4]]
                score = float(row[-1])
                if bw < 16 or bh < 16:
                    continue
                out.append((x, y, bw, bh, score))
            return out
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        raw = self._faces.detectMultiScale(gray, 1.1, 5, minSize=(48, 48))
        return [(int(x), int(y), int(bw), int(bh), 0.8) for (x, y, bw, bh) in raw]

    def _keep_real_heads(self, boxes, w: int, h: int):
        min_h = max(16, int(self.min_rel_h * h))
        kept = [b for b in boxes if b[3] >= min_h and b[4] >= self.min_score]
        kept.sort(key=lambda b: b[2] * b[3], reverse=True)
        if self.max_faces > 0:
            kept = kept[: self.max_faces]
        return kept

    def _observe(self, box, w: int, h: int) -> FaceObs:
        x, y, bw, bh, score = box
        cx = x + bw / 2.0
        cy = y + bh / 2.0
        az = (cx / w - 0.5) * HFOV_DEG
        el = (0.5 - cy / h) * VFOV_DEG
        frac = bh / max(h, 1)
        dist = max(0.4, min(6.0, 0.55 / max(frac, 0.05)))
        return FaceObs(
            track_id=0,
            az_deg=az,
            el_deg=el,
            distance_m=dist,
            confidence=score,
            speaking=False,
            box=(x, y, bw, bh),
        )

    def _assign_ids(self, obs: list[FaceObs]) -> None:
        used: set[int] = set()
        for o in obs:
            best_id = None
            best_d = MATCH_MAX_DEG
            for prev in self._last:
                if prev.track_id in used:
                    continue
                d = abs(o.az_deg - prev.az_deg) + abs(o.el_deg - prev.el_deg)
                if d < best_d:
                    best_d = d
                    best_id = prev.track_id
            if best_id is None:
                best_id = self._next_id
                self._next_id += 1
            o.track_id = best_id
            used.add(best_id)

    @property
    def lips(self) -> bool:
        """True when speaking comes from real lip landmarks."""
        return self._lips_model is not None

    def _load_lips(self, cv2) -> None:
        try:
            from mediapipe.tasks.python import BaseOptions, vision
        except ImportError:
            log.warning("no lip landmarks (pip install mediapipe): mouth motion is a guess")
            return
        if not LIPS_MODEL.exists():
            log.warning("no lip landmarks: %s missing (download_english.py)", LIPS_MODEL)
            return
        self._lips_model = vision.FaceLandmarker.create_from_options(
            vision.FaceLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=str(LIPS_MODEL), delegate=BaseOptions.Delegate.CPU),
                running_mode=vision.RunningMode.VIDEO,
                num_faces=1,
            )
        )

    def _lip_gap(self, cv2, frame) -> float | None:
        """Inner-lip gap over eye distance for the biggest face, or None."""
        import mediapipe as mp

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ms = int((time.monotonic() - self._t0) * 1000)
        r = self._lips_model.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), ms)
        if not r.face_landmarks:
            return None
        p = r.face_landmarks[0]
        eye = float(np.hypot(p[33].x - p[263].x, p[33].y - p[263].y))
        return float(np.hypot(p[13].x - p[14].x, p[13].y - p[14].y)) / eye if eye > 0 else None

    def _lips_speaking(self, obs: FaceObs, gap: float | None) -> bool:
        hist = self._lips.setdefault(obs.track_id, collections.deque())
        now = time.monotonic()
        if gap is not None:
            hist.append((now, gap))
        while hist and now - hist[0][0] > LIPS_WINDOW_S:
            hist.popleft()
        obs.mouth_ema = 100 * float(np.std([g for _, g in hist])) if len(hist) >= 5 else 0.0
        return obs.mouth_ema >= LIPS_TALK

    def _mouth_speaking(self, gray, obs: FaceObs) -> bool:
        x, y, bw, bh = obs.box
        my = y + int(bh * 0.58)
        mh = max(8, int(bh * 0.38))
        mx = x + int(bw * 0.15)
        mw = max(8, int(bw * 0.70))
        h, w = gray.shape
        y1, y2 = max(0, my), min(h, my + mh)
        x1, x2 = max(0, mx), min(w, mx + mw)
        roi = gray[y1:y2, x1:x2]
        if roi.size < 20:
            return False
        # Known and left as is (2026-09-26): the face box moves a pixel or two
        # every frame, so the crop rarely matches the last one's shape and
        # this mostly returns False with mouth_ema 0.0. Resizing the crop to
        # a fixed size made it measure, but silent vs talking came out the
        # same (median 3.84 vs 3.83, two runs): camera noise and head motion
        # swamp the lips, and every face then read as "speaking". Lip
        # landmarks would be needed to do this properly.
        prev = self._prev_mouth.get(obs.track_id)
        self._prev_mouth[obs.track_id] = roi.copy()
        if prev is None or prev.shape != roi.shape:
            return False
        delta = float(np.mean(np.abs(roi.astype(np.float32) - prev.astype(np.float32))))
        ema = 0.55 * self._motion.get(obs.track_id, 0.0) + 0.45 * delta
        self._motion[obs.track_id] = ema
        obs.mouth_ema = ema
        return ema >= MOUTH_SPEAK
