"""The Brain's control loop.

One loop at 20 Hz. It reads the latest perception, asks the personality what to
do, applies its own safety checks, and sends one command to the Spine. That
command is also the heartbeat, so if this loop stops, the Spine notices within
100 ms and ramps the motors to zero.

Everything slow — camera, LiDAR, speech — runs in its own thread and writes
into a latest-value slot. This loop never waits for any of it.

What this loop is NOT
---------------------
It is not the thing that keeps the robot safe. The Spine is. Every check in
here is a second opinion, running on top of the Spine's own arbitration
(docs/01-architecture.md section 3). If a check in this file is the only thing
stopping the robot from doing something dangerous, the check is in the wrong
file.

Run it:  python3 main.py --spine /dev/ttyACM0
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time

from face_link import FaceLink
from perception import Perception
from personality import Action, Motion, Personality, motion_for
from spine_link import SpineLink

log = logging.getLogger("brain")

LOOP_HZ = 20
LOOP_S = 1.0 / LOOP_HZ

# The robot tips forward at 19.4 degrees and the anti-tip castor catches it at
# 9.9 (cad/walle_frame.scad). Stop asking for forward motion well before the
# castor has to do anything.
PITCH_LIMIT_DEG = 7.0

# If the motors are this hot, stop asking for movement. The Spine also limits
# on temperature, at 80 degrees. We back off earlier so that in normal running
# the Spine's limiter never has to act — if it does, something is wrong.
MOTOR_T_BACKOFF = 70.0


class Brain:
    def __init__(self, spine_port: str, face_ports: list[str]):
        self.spine = SpineLink(spine_port)
        self.face = FaceLink(face_ports)
        self.perception = Perception()
        self.personality = Personality()
        self._running = False
        self._late_loops = 0

    # -- lifecycle ----------------------------------------------------------
    def start(self) -> None:
        self.spine.open()
        self.face.open()
        self.perception.start()
        self._running = True

    def stop(self) -> None:
        self._running = False
        # Order matters: stop asking for movement before tearing anything down.
        try:
            self.spine.send(0.0, 0.0)
        except Exception:
            pass
        self.perception.stop()
        self.face.close()
        self.spine.close()

    # -- the loop -----------------------------------------------------------
    def run(self) -> None:
        next_t = time.monotonic()
        while self._running:
            next_t += LOOP_S
            self.step()

            slack = next_t - time.monotonic()
            if slack > 0:
                time.sleep(slack)
            else:
                # We are behind. Do not try to catch up by running extra
                # iterations — resync, and count it. Persistent lateness means
                # something in this loop is too slow and needs moving to a
                # thread.
                self._late_loops += 1
                if self._late_loops % 20 == 1:
                    log.warning("control loop late by %.0f ms", -slack * 1000)
                next_t = time.monotonic()

    def step(self) -> None:
        snap = self.perception.snapshot
        status = self.spine.status

        may_move, reason = self._may_move(snap, status)

        intent = self.personality.update(snap, may_move=may_move)
        motion = motion_for(intent) if may_move else Motion()

        # --- the face. Cosmetic, and allowed to fail. ---
        self.face.gaze(intent.gaze_az, intent.gaze_el)
        self.face.mood(intent.mood)

        # --- the command. This is also the heartbeat. ---
        # Sent unconditionally, every pass, even when it is zero. A zero
        # command means "I am alive and I want nothing"; no command at all
        # means "I am dead". Those must stay distinguishable.
        self.spine.send(motion.speed, motion.turn)

        if not may_move and reason:
            self._log_block(reason)

    # -- the Brain's own safety checks --------------------------------------
    def _may_move(self, snap, status) -> tuple[bool, str]:
        """Second opinion on whether it is reasonable to ask for movement.

        Returns (allowed, reason_if_not). Each of these is also covered by the
        Spine; the point of repeating them here is to stop the Brain from
        making requests that would only be refused, which keeps the log clean
        and makes a real fault stand out.
        """
        if not status.fresh:
            return False, "no telemetry from the spine"
        if status.mode != "assist":
            return False, "driver has it in manual"
        if status.stop_reason != "running":
            return False, f"spine is stopped: {status.stop_reason}"

        # Pitch. Only blocks if the reading is fresh — a dead IMU must not
        # silently remove the check, so treat missing pitch data as a block.
        if not snap.fresh(snap.imu_at):
            return False, "no imu data"
        if abs(snap.pitch_deg) > PITCH_LIMIT_DEG:
            return False, f"pitched {snap.pitch_deg:.0f} deg"

        hot = max(status.temp_motor)
        if hot > MOTOR_T_BACKOFF:
            return False, f"motor at {hot:.0f} C"

        return True, ""

    def _log_block(self, reason: str) -> None:
        # Rate limited, or this fills the log at 20 lines a second.
        now = time.monotonic()
        last, last_reason = getattr(self, "_blk", (0.0, ""))
        if reason != last_reason or (now - last) > 5.0:
            log.info("not moving: %s", reason)
            self._blk = (now, reason)


def main() -> int:
    ap = argparse.ArgumentParser(description="WALL-E brain")
    ap.add_argument("--spine", default="/dev/ttyACM0",
                    help="serial port for the Teensy spine")
    ap.add_argument("--face", nargs="*",
                    default=["/dev/ttyUSB0", "/dev/ttyUSB1"],
                    help="serial ports for the two eye boards")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )

    brain = Brain(args.spine, args.face)

    def on_signal(_sig, _frm):
        log.info("stopping")
        brain.stop()

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    try:
        brain.start()
    except Exception:
        log.exception("failed to start — check the serial ports")
        return 1

    try:
        brain.run()
    finally:
        brain.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
