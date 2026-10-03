"""Serial link to the two Face boards, one per eye.

The Brain sends intent, not animation. "Look 20 degrees left" and "you are
curious", a few times a second. The Face boards do the smoothing, the blinking
and the servo movement themselves, at 30 fps.

Two consequences of that split, both useful:

* The face stays smooth while the Brain is busy with a camera frame.
* If this link dies, the eyes fall back to an idle behaviour rather than
  freezing. A frozen face reads as "broken" to everyone watching; a bored face
  reads as "fine". See firmware/face/face.ino idle_behaviour().

Nothing in this file can move the robot. The Face boards have no connection to
the Spine, the CAN bus or the contactors.
"""

from __future__ import annotations

import logging
import time
from typing import Iterable

import serial

log = logging.getLogger(__name__)

BAUD = 115200

MOODS = ("idle", "curious", "happy", "sad", "alarm", "sleepy")


class FaceLink:
    """Talks to both eye boards at once.

    Writes are best-effort on purpose. A dead eye must not be able to take down
    the control loop, so every failure here is logged and swallowed. This is
    the opposite of SpineLink, where a write failure is raised — and the
    difference is exactly the difference between cosmetic and safety-critical.
    """

    def __init__(self, ports: Iterable[str] = ("/dev/ttyUSB0", "/dev/ttyUSB1")):
        self._port_names = list(ports)
        self._ports: list[serial.Serial] = []
        self._last_mood: str | None = None
        self._last_gaze: tuple[float, float] | None = None
        self._last_sent = 0.0

    def open(self) -> None:
        for name in self._port_names:
            try:
                self._ports.append(serial.Serial(name, BAUD, timeout=0,
                                                 write_timeout=0.05))
                log.info("face board open on %s", name)
            except Exception:
                log.warning("face board %s not available, carrying on", name)
        if not self._ports:
            log.warning("no face boards found — the robot will be expressionless")

    def close(self) -> None:
        for p in self._ports:
            try:
                p.close()
            except Exception:
                pass
        self._ports.clear()

    # -- the three commands the firmware understands ------------------------
    def gaze(self, az_deg: float, el_deg: float) -> None:
        """Where to look, in degrees. Negative azimuth is to the robot's left.

        Deduplicated: only sent when it has moved enough to matter. There is no
        point spending serial bandwidth on a tenth of a degree, and the Face
        smooths towards the target anyway.
        """
        az = _clamp(az_deg, -45.0, 45.0)
        el = _clamp(el_deg, -45.0, 45.0)
        if self._last_gaze is not None:
            if abs(az - self._last_gaze[0]) < 1.0 and \
               abs(el - self._last_gaze[1]) < 1.0:
                return
        self._last_gaze = (az, el)
        self._write(f"GAZE {az:.1f} {el:.1f}\n")

    def mood(self, name: str) -> None:
        if name not in MOODS:
            raise ValueError(f"unknown mood {name!r}, expected one of {MOODS}")
        if name == self._last_mood:
            return              # moods are sticky; resending is just noise
        self._last_mood = name
        self._write(f"MOOD {name}\n")

    def blink(self) -> None:
        self._write("BLINK\n")

    # -- internals ----------------------------------------------------------
    def _write(self, s: str) -> None:
        data = s.encode("ascii")
        dead = []
        for p in self._ports:
            try:
                p.write(data)
            except Exception:
                log.warning("face board %s stopped responding", p.port)
                dead.append(p)
        for p in dead:
            self._ports.remove(p)
            try:
                p.close()
            except Exception:
                pass


def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v
