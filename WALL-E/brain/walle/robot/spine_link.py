"""Serial link to the Spine.

The Spine is the Teensy that actually drives the motors. This module is the
only place in the Brain that is allowed to talk to it.

The single most important thing in this file
--------------------------------------------
The heartbeat is not a separate timer. It IS the command message, and it is
sent from the control loop that decides the command.

It is tempting to put the heartbeat on its own thread so it never misses a
beat. Do not. A heartbeat that keeps ticking while the thinking part of the
program is frozen tells the Spine "I am healthy" when the Brain is in fact
dead. That defeats the entire watchdog, which is the main safety feature of
the architecture. If the control loop stalls, the beat must stall with it.

See WALL-E/docs/01-architecture.md section 4.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field

import serial

log = logging.getLogger(__name__)

# Must match firmware/spine/config.h
BAUD = 115200
BRAIN_TIMEOUT_MS = 100          # the Spine gives up on us after this
SEND_HZ = 20                    # so a beat every 50 ms, half the timeout


@dataclass
class SpineStatus:
    """The last telemetry line the Spine sent. All fields may be stale."""

    t_ms: int = 0
    mode: str = "unknown"
    stop_reason: str = "unknown"
    duty: tuple[float, float] = (0.0, 0.0)
    volts: tuple[float, float] = (0.0, 0.0)
    temp_motor: tuple[float, float] = (0.0, 0.0)
    current: tuple[float, float] = (0.0, 0.0)
    rc_ok: bool = False
    brain_ok: bool = False
    received_at: float = field(default_factory=lambda: 0.0)

    @property
    def fresh(self) -> bool:
        return (time.monotonic() - self.received_at) < 0.5

    @property
    def moving(self) -> bool:
        return abs(self.duty[0]) > 0.01 or abs(self.duty[1]) > 0.01


class SpineLink:
    def __init__(self, port: str = "/dev/ttyACM0"):
        self._port_name = port
        self._ser: serial.Serial | None = None
        self._seq = 0
        self._status = SpineStatus()
        self._lock = threading.Lock()
        self._reader: threading.Thread | None = None
        self._stop = threading.Event()

    # -- connection ---------------------------------------------------------
    def open(self) -> None:
        # timeout is non-zero but small: reads must never block the reader
        # thread for long, and writes must never block the control loop.
        self._ser = serial.Serial(self._port_name, BAUD, timeout=0.05,
                                  write_timeout=0.05)
        self._stop.clear()
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()
        log.info("spine link open on %s", self._port_name)

    def close(self) -> None:
        self._stop.set()
        if self._reader:
            self._reader.join(timeout=1.0)
        if self._ser:
            # Send one last zero so the robot does not coast on our last
            # command while the Spine waits out its timeout.
            try:
                self.send(0.0, 0.0)
            except Exception:
                pass
            self._ser.close()

    # -- the command, which is also the heartbeat ---------------------------
    def send(self, speed: float, turn: float) -> None:
        """Send one command. Call this from the control loop, at SEND_HZ.

        Raises on write failure rather than swallowing it, because a Brain that
        cannot reach the Spine should crash loudly and let the Spine's watchdog
        stop the robot. Quietly retrying would hide the fault.
        """
        if self._ser is None:
            raise RuntimeError("spine link not open")
        speed = _clamp(speed, -1.0, 1.0)
        turn = _clamp(turn, -1.0, 1.0)
        self._seq = (self._seq + 1) & 0xFFFFFFFF
        line = f"C {speed:.4f} {turn:.4f} {self._seq}\n"
        self._ser.write(line.encode("ascii"))

    # -- telemetry ----------------------------------------------------------
    @property
    def status(self) -> SpineStatus:
        with self._lock:
            return self._status

    def _read_loop(self) -> None:
        assert self._ser is not None
        while not self._stop.is_set():
            try:
                raw = self._ser.readline()
            except Exception:
                log.exception("spine read failed")
                time.sleep(0.2)
                continue
            if not raw:
                continue
            try:
                s = _parse_status(raw.decode("ascii", "replace").strip())
            except Exception:
                continue        # a malformed line is not worth logging at 20 Hz
            if s is not None:
                with self._lock:
                    self._status = s


def _parse_status(line: str) -> SpineStatus | None:
    """Parse the Spine's telemetry line.

    Format, from firmware/spine/spine.ino telemetry():
      S <t_ms> <mode> <stop_reason> duty <l> <r> v <l> <r> t <l> <r>
        i <l> <r> rc <0|1> brain <0|1>
    """
    p = line.split()
    if len(p) < 20 or p[0] != "S":
        return None
    return SpineStatus(
        t_ms=int(p[1]),
        mode=p[2],
        stop_reason=p[3],
        duty=(float(p[5]), float(p[6])),
        volts=(float(p[8]), float(p[9])),
        temp_motor=(float(p[11]), float(p[12])),
        current=(float(p[14]), float(p[15])),
        rc_ok=p[17] == "1",
        brain_ok=p[19] == "1",
        received_at=time.monotonic(),
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v
