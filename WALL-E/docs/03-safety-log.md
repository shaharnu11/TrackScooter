# 03 — Safety log

Record of the Phase 3 safety gate. Fill in by hand as each test is completed.

- **Gate:** until every row is signed off, the robot does not operate within 10 m of a person.
- No schedule pressure overrides this.
- Every test is run **while driving**. A stop that works from standstill proves nothing.

---

## Pass criteria

All four must hold:

1. The robot stops.
2. No lurch, jump or acceleration before stopping.
3. No turn to either side.
4. It stays stopped. No restart when the fault clears.

- Smooth stop over ~0.5 s: pass.
- Slammed stop: **fail**. A hard stop on a 231 mm footprint can pitch the robot forward.

---

## The tests

| # | Test | How to cause it | Expected result | Pass | Date | Notes |
|---|---|---|---|---|---|---|
| 1 | Physical E-stop | Press the red mushroom button while driving | Contactor opens, motors dead immediately | | | |
| 2 | Wireless E-stop | Press the keyfob from 20 m away | Same as test 1 | | | |
| 3 | Transmitter off | Switch the radio transmitter off mid-drive | Ramp to zero within 0.1 s of the last frame. **On the FS-iA6B the frames may not stop** — the receiver can repeat the last stick values. The Spine must then report `rc_frozen` and ramp to zero within `RC_FROZEN_MS` (500 ms). Both paths must stop the robot | | | |
| 4 | Out of radio range | Walk the robot away until the link drops | Same as test 3, and no restart when the link returns without re-arming | | | |
| 5 | Brain USB unplugged | Pull the XPS serial cable in ASSIST mode | Watchdog fires, ramp to zero, fall back to MANUAL | | | |
| 6 | Brain power lost | Cut power to the XPS in ASSIST mode | Same as test 5 | | | |
| 7 | Bumper triggered | Hold a board in front of a ToF sensor while driving forward | Forward motion vetoed. Reverse still works | | | |
| 8 | Throttle signal wire disconnected | Unplug the throttle line between one DAC and one controller while driving | **Both** motors stop, not one. The Teensy sees that track's speed sensor stop changing while commanded, and ramps both down (rule 4) | | | |
| 9 | Arm switch off | Flick the arm switch off while driving | Ramp to zero | | | |
| 10 | Power on while armed | Connect the battery with the arm switch already ON | No movement. Requires the switch cycled off then on | | | |
| 11 | One pack disconnected | Open the left pack's main switch while driving forward | **Both** tracks stop. No pivot on the surviving track | | | |
| 12 | The other pack disconnected | Repeat test 11 on the right pack | Same as test 11 | | | |
| 13 | Uneven pack voltage | Drive with the packs at clearly different charge levels | Drives straight. Any pull to one side means rule 11 compensation is not working | | | |
| 14 | Ground bond removed | Parked and unarmed, disconnect the negative bond between the packs | Far-pack readings go wrong or open-circuit, and it refuses to arm. See note below | | | |
| 15 | **Spine unpowered mid-drive** | Cut power to the Teensy while driving forward | **The hardware watchdog loses its heartbeat and opens the relay within its timeout**, cutting the throttle lines. No pivot, no continued driving | | | |
| 16 | **Teensy alive, I2C to a DAC dead** | Pull one I2C wire to a DAC while driving forward | The Teensy sees the write fail, **deliberately stops kicking the watchdog**, and the relay opens. See note below | | | |
| 17 | Reverse line glitches while driving forward | On blocks, toggle one controller's reverse line while driving forward | No slam into reverse. The Teensy commands zero, waits for the track to stop, then changes the line | | | |
| 18 | **Current limit on a turn in place** | On sand, not blocks, turn in place at full stick, watching the ACS758 readings | Current stays within the limit the wiring was sized for, and the Teensy backs off the throttle if not. A turn in place is the highest-current case | | | |
| 19 | **Electronics battery open mid-drive** | Pull the electronics battery fuse while driving forward, both packs healthy | The Teensy dies, its arm MOSFET opens the coil chain, **both** contactors drop, the watchdog relay opens. The robot coasts straight, no pivot. New with D8 | | | |
| 20 | **Electronics battery bond intact** | Parked and unarmed, measure from 12 V negative to pack negative | **Exactly one** path, through the ground bond. Zero = floating pack readings (trap 3). More than one = ground loop for motor current | | | |

---

## Tests 11 and 12 are different tests

Both contactor coils run from pack A (`04-power-and-wiring.md` section 3).

- **Test 11 — pack A open.** Coils lose power, both contactors open, both motors disconnect. Proves the **wiring**. It passes with the Teensy unplugged; run it that way once. Since D8 the Teensy has its own battery and stays alive through this test, so unplug it deliberately or the arm MOSFET is under test at the same time and the cause is ambiguous.
- **Test 12 — pack B open.** Contactor B stays closed with no power behind it. The left track keeps driving and the robot pivots unless the firmware detects it. Proves **arbitration rule 4**: hall-edge counting detecting a dead track.

If test 12 passes for the wrong reason, the failure surfaces when pack B's BMS trips in a crowd. Run it on blocks first and observe which track keeps turning.

Both tests are specific to one battery per pod. On a skid-steer machine a dead track does not slow the robot: the surviving track spins it on the spot. Both tests must stop **both** sides.

---

## Tests 8, 14, 15 and 16 were rewritten on 2026-09-17

Decision D7 settled the drive electronics as the two scooter controllers already owned. These four tests assumed a controller that protects itself. **Three were checking for protection that does not exist**, which is worse than no test: a test expected to pass reports safety that is absent.

| Test | Was checking | Now checks |
|---|---|---|
| 8 | Unplugging a data wire | Unplugs a **throttle line**. The robot must detect the dead track through its speed sensor |
| 14 | That losing the ground bond blocked arming | The bond matters **more**: ACS758 sensors and pack dividers all measure against pack negative, so a missing bond corrupts readings instead of announcing itself |
| 15 | The controllers releasing the motors **on their own** | **There is no command timeout.** A scooter controller driven by a DAC holds its last throttle voltage. Only the hardware watchdog stops it |
| 16 | — | New. See below |

**Test 15 carries the electronics supply decision.** With the Spine unpowered no rule is enforced, and the scooter controllers do not stop on their own: the DAC holds its last voltage and the robot drives away uncontrolled.

> **Effect of D8, 2026-09-19.** The electronics previously ran from the larger pack, so a BMS cut also killed the Spine. They now run from a separate 12 V battery, so a pack failure no longer unpowers the Spine. Test 15 keeps its meaning — cut Teensy power, the watchdog must stop the robot — but the field event that causes it has moved to **test 19**, which also takes down the Brain and the Face. Run both.

The hardware watchdog (`05-bom.md` section 1b) is the entire replacement for the missing command timeout. Until test 15 is signed off, nothing stands between a dead Teensy and a runaway robot.

**Test 16 covers the watchdog's blind spot.** The watchdog fires only when kicks stop. A Teensy that is alive but has lost the I2C bus to the DACs wants to command zero, cannot, and keeps kicking. The throttle stays where it was.

The firmware closes this itself: every DAC write is checked, and **on a failed write the Teensy stops kicking on purpose**. Test 16 proves that path. It is easy to omit, because nothing fails visibly until it matters.

**Test 10** catches a robot that drives the instant the battery is connected, because a stick was off-centre or the arm switch was left on.

---

## Re-test triggers

Re-run the whole table from the start after any of:

- Any change to the Spine firmware, however small
- Any change to the E-stop chain, contactor, watchdog or fusing wiring
- Any change to the throttle path: DACs, their I2C wiring, or the opto-isolators
- Any change to the radio equipment or its binding
- Any change to the Brain–Spine protocol
- Transport, a drop, or a field repair

At the event: after a repair in dust or at night, run at least tests 1, 2, 3 and 9 before the robot goes near people.

---

## Sign-off

| | Name | Date |
|---|---|---|
| All twenty tests passed | | |
| Re-tested after last firmware change | | |
| Re-tested on site at Midburn | | |
