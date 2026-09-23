"""What the robot can see.

Everything in here runs in its own thread and is allowed to be slow. The
control loop never waits for a camera frame; it reads whatever the last result
was and gets on with it.

The "latest value" pattern
--------------------------
Each sensor thread writes into a single slot, overwriting whatever was there.
There are no queues. A queue would let a slow consumer build up a backlog, and
then the robot would be reacting to where a person was five seconds ago. For
control, a stale-but-current reading is right and a complete history is wrong.

Every reading carries the time it was taken, and the control loop is expected
to check `fresh` before trusting it. A sensor that stops updating must look
like a sensor that stopped, not like a sensor reporting "all clear".
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field

log = logging.getLogger(__name__)

STALE_AFTER_S = 1.0


@dataclass
class Person:
    """Someone the camera found."""

    az_deg: float               # negative is to the robot's left
    el_deg: float
    distance_m: float
    confidence: float

    @property
    def interesting(self) -> bool:
        # Close enough to be worth reacting to, confident enough to believe.
        return self.distance_m < 6.0 and self.confidence > 0.55


@dataclass
class Snapshot:
    """The latest of everything, with the time each part was taken."""

    people: list[Person] = field(default_factory=list)
    people_at: float = 0.0
    # Clear distance in each of 8 sectors around the robot, metres.
    # Index 0 is straight ahead, increasing clockwise.
    sectors_m: list[float] = field(default_factory=lambda: [0.0] * 8)
    sectors_at: float = 0.0
    heading_deg: float = 0.0
    pitch_deg: float = 0.0
    imu_at: float = 0.0

    def fresh(self, when: float) -> bool:
        return when > 0.0 and (time.monotonic() - when) < STALE_AFTER_S

    @property
    def nearest_person(self) -> Person | None:
        good = [p for p in self.people if p.interesting]
        if not good or not self.fresh(self.people_at):
            return None
        return min(good, key=lambda p: p.distance_m)


class Perception:
    def __init__(self) -> None:
        self._snap = Snapshot()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []

    @property
    def snapshot(self) -> Snapshot:
        with self._lock:
            return self._snap

    def start(self) -> None:
        for fn in (self._camera_loop, self._lidar_loop, self._imu_loop):
            t = threading.Thread(target=fn, daemon=True)
            t.start()
            self._threads.append(t)

    def stop(self) -> None:
        self._stop.set()
        for t in self._threads:
            t.join(timeout=1.0)

    # -- sensor threads -----------------------------------------------------
    def _camera_loop(self) -> None:
        """OAK-D Lite.

        TODO: connect with depthai. The detection model runs on the camera's
        own chip, so this thread only has to read a finished list of boxes and
        convert them to angles and distances. That is the whole reason for
        choosing this camera: the XPS GPU stays free for a small local language model.
        """
        while not self._stop.wait(0.1):
            pass

    def _lidar_loop(self) -> None:
        """RPLIDAR A1.

        TODO: read the scan, bin it into the 8 sectors, take the nearest
        return in each. Note what this is NOT: it is not SLAM and not a map.
        Midburn is a flat featureless plain, so mapping buys nothing and GPS
        plus a compass does the job. See docs/00-plan.md.

        Beware the blind spot: the LiDAR sits on top of the body and cannot see
        anything closer than the body is wide. Close-in work belongs to the ToF
        ring, which is wired to the Spine, not here.
        """
        while not self._stop.wait(0.1):
            pass

    def _imu_loop(self) -> None:
        """BNO085: fused heading, and pitch.

        Pitch matters more than it looks. The robot tips forward at 19.4
        degrees and the anti-tip castor catches it at 9.9 (cad/walle_frame.scad).
        So a pitch reading above about 7 degrees means the castor is about to
        take load, and the right response is to stop asking for forward motion.
        """
        while not self._stop.wait(0.05):
            pass

    # -- for testing without hardware --------------------------------------
    def inject(self, **kw) -> None:
        """Set fields directly. Used by the simulator and by tests."""
        with self._lock:
            now = time.monotonic()
            if "people" in kw:
                self._snap.people = kw["people"]
                self._snap.people_at = now
            if "sectors_m" in kw:
                self._snap.sectors_m = kw["sectors_m"]
                self._snap.sectors_at = now
            if "heading_deg" in kw:
                self._snap.heading_deg = kw["heading_deg"]
                self._snap.imu_at = now
            if "pitch_deg" in kw:
                self._snap.pitch_deg = kw["pitch_deg"]
                self._snap.imu_at = now
