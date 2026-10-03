"""The camera while talking: face and lip tracking in a thread, the camera window, the mic bar."""

from __future__ import annotations

import threading
import time

from walle.eyes.camera import UsbCamera
from walle.robot.perception import Person
from walle.robot.speaker_lock import SpeakerLock


class TalkCam:
    """USB camera + speaker lock. Main thread pumps the window."""

    def __init__(self) -> None:
        self.cam = UsbCamera()
        self.lock = SpeakerLock()
        self._stop = threading.Event()
        self._mu = threading.Lock()
        self.frame = None
        self.obs: list = []
        self.speaker_id: int | None = None
        self.mouth = False
        self._mouth_t = -1e9  # last time the locked face's lips moved
        self.ok = False
        self._thread: threading.Thread | None = None
        self._paused = threading.Event()  # "go to sleep": no faces, no lips
        self._slept_drawn = False

    def start(self) -> bool:
        if not self.cam.open():
            print(self.cam.last_error or "No camera.")
            return False
        self.cam.max_faces = 1
        self.cam.min_rel_h = 0.08
        self.cam.min_score = 0.55
        self.ok = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"Camera {self.cam.device}. Green box = talker. q quits.")
        return True

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.5)
        self.cam.close()
        try:
            import cv2
            cv2.destroyAllWindows()
        except Exception:
            pass

    def pause(self) -> None:
        """Stop face and lip tracking and close the camera (asleep: ~0% CPU
        here instead of ~23% for a paused but open camera)."""
        self._paused.set()
        with self._mu:
            self.obs, self.speaker_id, self.mouth = [], None, False

    def resume(self) -> None:
        self._paused.clear()

    def locked(self) -> bool:
        with self._mu:
            return self.speaker_id is not None

    def talking(self) -> bool:
        with self._mu:
            return self.mouth and self.speaker_id is not None

    def lips_moving(self, within_s: float) -> bool | None:
        """Did the locked face's lips move in the last within_s? None when
        there are no lip landmarks (then nothing can be said)."""
        if not self.cam.lips:
            return None
        with self._mu:
            return time.monotonic() - self._mouth_t <= within_s

    def mouth_level(self) -> float | None:
        """Mouth-area motion of the locked face (usb_camera mouth_ema), or None."""
        with self._mu:
            return getattr(self, "mouth_ema", 0.0) if self.speaker_id is not None else None

    def snapshot(self):
        """The latest raw camera frame (no boxes drawn), or None."""
        with self._mu:
            return None if self.frame is None else self.frame.copy()

    def pump(self) -> bool:
        """Draw the window. Return False if the user pressed q."""
        if not self.ok:
            return True
        try:
            import cv2
        except ImportError:
            return True
        with self._mu:
            frame = None if self.frame is None else self.frame.copy()
            obs = list(self.obs)
            sid = self.speaker_id
        if frame is None:
            return True
        if self._paused.is_set():
            # Asleep: draw the dimmed picture once, then only check for q.
            # Redrawing it 10 times a second cost ~19% CPU.
            if not self._slept_drawn:
                dim = (frame * 0.25).astype(frame.dtype)
                cv2.putText(dim, "SLEEPING - say wake up", (12, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)
                cv2.imshow("WALL-E speaker lock", dim)
                self._slept_drawn = True
            return (cv2.waitKey(1) & 0xFF) != ord("q")
        self._slept_drawn = False
        for o in obs:
            x, y, w, h = o.box
            is_focus = sid is not None and o.track_id == sid
            color = (0, 255, 0) if is_focus else (0, 220, 255)
            thick = 4 if is_focus else 3
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, thick)
            label = "YOU" if is_focus else "FACE"
            if o.speaking:
                label += " talk"
            cv2.putText(
                frame, f"{label}  m={o.mouth_ema:.1f}", (x, max(28, y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2,
            )
        if not obs and not self._paused.is_set():
            cv2.putText(
                frame, "NO FACE — come closer, more light, look at camera",
                (12, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
            )
        else:
            status = f"faces {len(obs)}"
            if sid is not None:
                status += f"  lock {sid}"
            cv2.putText(
                frame, status, (12, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2,
            )
        self._draw_mic(cv2, frame)
        try:
            cv2.imshow("WALL-E speaker lock", frame)
        except cv2.error:
            print("No GUI window. Run in Terminal.app, not SSH.")
            return False
        return (cv2.waitKey(1) & 0xFF) != ord("q")

    def set_mic(self, level: float, thresh: float) -> None:
        self.mic_level = level
        self.mic_thresh = thresh

    def _draw_mic(self, cv2, frame) -> None:
        """Mic bar, bottom left. The white tick is the trigger level."""
        level = getattr(self, "mic_level", 0.0)
        thresh = getattr(self, "mic_thresh", 0.0)
        if thresh <= 0:
            return
        h = frame.shape[0]
        full = 300
        scale = full / (thresh * 3)  # the tick sits a third of the way along
        x0, y0 = 12, h - 40
        loud = level > thresh
        cv2.rectangle(frame, (x0, y0), (x0 + full, y0 + 20), (60, 60, 60), -1)
        cv2.rectangle(
            frame, (x0, y0), (x0 + int(min(level * scale, full)), y0 + 20),
            (0, 255, 0) if loud else (0, 200, 255), -1,
        )
        tx = x0 + int(thresh * scale)
        cv2.line(frame, (tx, y0 - 4), (tx, y0 + 24), (255, 255, 255), 2)
        cv2.putText(
            frame, "MIC: HEARING YOU" if loud else "MIC", (x0 + full + 10, y0 + 17),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if loud else (200, 200, 200), 2,
        )

    def _loop(self) -> None:
        while not self._stop.is_set():
            if self._paused.is_set():
                with self._mu:  # also undo a frame that landed after pause()
                    self.obs, self.speaker_id, self.mouth = [], None, False
                if self.cam.is_open:
                    self.cam.close()  # here, in the thread that reads it
                self._stop.wait(0.2)
                continue
            if not self.cam.is_open and not self.cam.reopen():
                self._stop.wait(1.0)  # woken, camera not back yet: try again
                continue
            obs, frame = self.cam.read()
            # Faces and lips on every second frame: 15 a second is plenty,
            # and it halves the CPU (detection + lips ~1.6 cores at 30 fps
            # on the full frame before).
            self.cam.skip()
            if frame is None:
                if self._stop.wait(0.03):
                    break
                continue
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
            now = time.monotonic()
            # One real head: always lock it. Mouth motion is too weak alone
            # (open but still mouth never trips SPEAKER, so he never answers).
            sid = None
            mouth = False
            mouth_ema = 0.0
            if obs:
                sid = obs[0].track_id
                mouth = bool(obs[0].speaking)
                mouth_ema = float(obs[0].mouth_ema)
            with self._mu:
                self.frame = frame
                self.obs = obs
                self.speaker_id = sid
                self.mouth = mouth
                self.mouth_ema = mouth_ema
                if mouth:
                    self._mouth_t = now
