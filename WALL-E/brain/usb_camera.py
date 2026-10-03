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

# Lip landmarks: Google's face landmark model (478 points, the one inside
# MediaPipe's face_landmarker.task) run by the plain TFLite runtime
# (ai-edge-litert) on the YuNet face box, ~2 ms a face. Lip activity = how
# much the inner-lip gap (points 13/14, over the eye distance) varies in the
# last LIPS_WINDOW_S, x100.
# Not MediaPipe itself: 0.10.35 sends usage logs to Google (clearcut) and has
# no off switch; 1.0.1 crashes on the Mac. Not OpenCV's Facemark LBF: it
# jitters, a quiet face read like a talking one.
LIPS_MODEL = YUNET_PATH.parent / "face_landmarks_detector.tflite"
LIPS_TASK_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/latest/face_landmarker.task"
)  # a zip; LIPS_MODEL is the file inside it
LIPS_INPUT = 256
# Set from the MediaPipe test; the TFLite model reads the same points but
# without MediaPipe's smoothing: check with lips_test.py. WALLE_LIPS_TALK
# overrides it without a code change.
LIPS_TALK = float(os.environ.get("WALLE_LIPS_TALK", "0.75"))
DETECT_W = 640  # face detection runs on a copy this wide
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
        self._lips_model = None  # TFLite face landmarks, when installed
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

    @property
    def is_open(self) -> bool:
        return self._cap is not None

    def reopen(self) -> bool:
        """Open the camera again after close(); the face models stay loaded."""
        import cv2

        if self._cap is None:
            self._cap = self._open_capture(cv2)
        return self._cap is not None

    def skip(self) -> None:
        """Drop the next frame without decoding it (half the work per second)."""
        if self._cap is not None:
            self._cap.grab()

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
        gap = self._lip_gap(cv2, frame, obs[0].box) if self._lips_model is not None and obs else None
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
            # YuNet on the full 1280x720 frame took ~1.7 CPU cores at 30 fps
            # on the M4 Max. A 640-wide copy is ~4x less work, and a face
            # 1-2 m away is still plenty of pixels. Boxes are scaled back.
            k = min(1.0, DETECT_W / w)
            small = frame if k == 1.0 else cv2.resize(frame, (int(w * k), int(h * k)), interpolation=cv2.INTER_AREA)
            size = (small.shape[1], small.shape[0])
            if self._size != size:
                self._det.setInputSize(size)
                self._size = size
            _ok, faces = self._det.detect(small)
            if faces is None:
                return []
            out = []
            for row in faces:
                x, y, bw, bh = [int(v / k) for v in row[:4]]
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
            from ai_edge_litert.interpreter import Interpreter
        except ImportError:
            log.warning("no lip landmarks (pip install ai-edge-litert): mouth motion is a guess")
            return
        if not LIPS_MODEL.exists():
            log.warning("no lip landmarks: %s missing (download_english.py)", LIPS_MODEL)
            return
        it = Interpreter(model_path=str(LIPS_MODEL), num_threads=2)
        it.allocate_tensors()
        self._lips_in = it.get_input_details()[0]["index"]
        self._lips_out = max(it.get_output_details(), key=lambda d: int(np.prod(d["shape"])))["index"]
        self._lips_model = it

    def _lip_gap(self, cv2, frame, box) -> float | None:
        """Inner-lip gap over eye distance for the face in box, or None."""
        x, y, w, h = box
        if w < 16 or h < 16:
            return None
        # A square 1.5x the face box, scaled to the model's 256x256 input.
        s = 1.5 * max(w, h)
        k = LIPS_INPUT / s
        m = np.float32([[k, 0, LIPS_INPUT / 2 - (x + w / 2) * k], [0, k, LIPS_INPUT / 2 - (y + h / 2) * k]])
        crop = cv2.warpAffine(frame, m, (LIPS_INPUT, LIPS_INPUT))
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB).astype(np.float32)[None] / 255.0
        self._lips_model.set_tensor(self._lips_in, rgb)
        self._lips_model.invoke()
        p = self._lips_model.get_tensor(self._lips_out).reshape(-1, 3)
        eye = float(np.hypot(*(p[33, :2] - p[263, :2])))
        return float(np.hypot(*(p[13, :2] - p[14, :2]))) / eye if eye > 0 else None

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
