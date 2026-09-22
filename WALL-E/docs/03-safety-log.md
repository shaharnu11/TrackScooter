# 03 — Safety log

The record of the Phase 3 safety gate. Fill this in by hand as each test is done.

**The rule:** until every row below is signed off, the robot does not operate within ten
metres of another person. There is no schedule pressure that justifies skipping this.

Each test is done **while the robot is driving**, not while it is parked. A stop that works
from standstill proves nothing.

---

## What counts as a pass

For every test, all four of these must be true:

1. The robot comes to a stop.
2. It does not lurch, jump, or accelerate first.
3. It does not turn to one side.
4. It stays stopped, and does not restart on its own when the fault clears.

A stop that arrives smoothly over half a second is a pass. A stop that slams the tracks is a
fail, because a hard stop on a 231 mm footprint can pitch the robot forward.

---

## The tests

| # | Test | How to cause it | Expected result | Pass | Date | Notes |
|---|---|---|---|---|---|---|
| 1 | Physical E-stop | Press the red mushroom button while driving | Contactor opens, motors dead immediately | | | |
| 2 | Wireless E-stop | Press the keyfob from 20 m away | Same as test 1 | | | |
| 3 | Transmitter off | Switch the radio transmitter off mid-drive | Ramp to zero within 0.1 s of the last frame | | | |
| 4 | Out of radio range | Walk the robot away until the link drops | Same as test 3, and it must not restart when the link returns without re-arming | | | |
| 5 | Brain USB unplugged | Pull the Jetson's serial cable in ASSIST mode | Watchdog fires, ramp to zero, fall back to MANUAL | | | |
| 6 | Brain power lost | Cut power to the Jetson in ASSIST mode | Same as test 5 | | | |
| 7 | Bumper triggered | Hold a board in front of a ToF sensor while driving forward | Forward motion vetoed. Reverse must still work | | | |
| 8 | Throttle signal wire disconnected | Unplug the throttle line between one DAC and one controller while driving | **Both** motors stop, not just one. The Teensy sees that track's speed sensor stop changing while commanded, and ramps both down (rule 4) | | | |
| 9 | Arm switch off | Flick the arm switch to off while driving | Ramp to zero | | | |
| 10 | Power on while armed | Connect the battery with the arm switch already ON | Robot must NOT move. It must require the switch to be cycled off then on | | | |
| 11 | One pack disconnected | Open the left pack's main switch while driving forward | **Both** tracks stop. The robot must NOT pivot on the surviving track | | | |
| 12 | The other pack disconnected | Repeat test 11 on the right pack | Same as test 11 | | | |
| 13 | Uneven pack voltage | Drive with the packs at clearly different charge levels | It still drives straight. Any pull to one side means rule 11 compensation is not working | | | |
| 14 | Ground bond removed | With the robot parked and unarmed, disconnect the negative bond between the packs | The Teensy's readings for the far pack go wrong or open-circuit, and it refuses to arm. **See the note below — this test changed completely with the scooter controllers.** | | | |
| 15 | **Spine unpowered mid-drive** | Cut power to the Teensy while driving forward | **The hardware watchdog loses its heartbeat and opens the relay within its timeout**, cutting the throttle lines. The robot must NOT pivot on one track, and must NOT keep driving. | | | |
| 16 | **Teensy alive, I2C to a DAC dead** | Pull one I2C wire to a DAC while driving forward | The Teensy sees the write fail, **deliberately stops kicking the watchdog**, and the relay opens. See the note below: this is the failure the watchdog does not catch on its own. | | | |
| 17 | Reverse line glitches while driving forward | With the track on blocks, toggle one controller's reverse line while it is driving forward | It must not slam into reverse. If the controller has no ramp of its own, the Teensy must command zero, wait for the track to stop, and only then change the line | | | |
| 18 | **Current limit on a turn in place** | On sand, not on blocks, turn in place at full stick while watching the ACS758 readings | Current stays within the limit the wiring was sized for, and the Teensy backs the throttle off if it does not. A turn in place is the highest-current thing this robot does | | | |
| 19 | **Electronics battery open mid-drive** | Pull the electronics battery's fuse while driving forward, with both packs healthy | The Teensy dies, so its arm MOSFET opens the coil chain and **both** contactors drop. The watchdog relay opens too. The robot coasts straight and does **not** pivot. New with decision D8 — see the note below | | | |
| 20 | **Electronics battery bond intact** | With the robot parked and unarmed, measure from 12 V negative to pack negative | **Exactly one** path, through the ground bond. Zero means the Teensy's pack readings are floating (trap 3). More than one means a ground loop for the motor current to find | | | |

**Tests 11 and 12 are not the same test, although they read like it.** Both contactor coils
run from pack A (`04-power-and-wiring.md` section 3), so:

- **Test 11, pack A open.** The coils lose power, both contactors open, both motors are
  disconnected. This test proves the **wiring**. It should pass even with the Teensy
  unplugged, and it is worth trying that way once — which matters more since decision D8,
  because the Teensy now has its own battery and stays alive through this test. Unplug it
  deliberately, or you are testing the arm MOSFET at the same time and will not know which of
  the two actually stopped the robot.
- **Test 12, pack B open.** Contactor B stays closed with no power behind it, so the left
  track keeps driving and the robot will pivot unless the firmware notices. This test proves
  **arbitration rule 4** — the Teensy counting hall edges and seeing a dead track.

If test 12 passes for the wrong reason, you will not find out until the day pack B's BMS
trips in a crowd. Run it with the robot on blocks first and watch which track keeps turning.

Tests 11 and 12 are the most important new ones, and they are specific to having one battery
per pod. On a skid-steer machine, one dead track does not slow the robot down — the surviving
track spins it on the spot. Both of these must produce a stop of **both** sides.

### Tests 8, 14, 15 and 16 were rewritten on 2026-09-17

Decision D7 settled the drive electronics as the two scooter controllers already owned. These
four tests had been written expecting a controller that protects itself, and **three of them
were checking for protection that does not exist.** That is worse than having no test, because a test you expect to pass tells
you the robot is safe when it is not.

| Test | Was checking | Now checks |
|---|---|---|
| 8 | Unplugging a CAN wire | There is no CAN. It unplugs a **throttle line** instead, and the robot must notice the dead track through its speed sensor. |
| 14 | That losing the ground bond dropped CAN and blocked arming | There is no CAN. The bond now matters **more**: the ACS758 current sensors and the pack voltage dividers all measure against pack negative, so a missing bond corrupts the Teensy's readings rather than announcing itself. |
| 15 | The controllers releasing the motors **on their own** | **There is no command timeout.** A scooter controller driven by a DAC holds its last throttle voltage and keeps going. Only the hardware watchdog stops it. |
| 16 | — | New. See below. |

**Test 15 is the one the whole electronics supply decision rests on.** Whenever the Spine loses
power it cannot enforce any of the rules above. **The scooter controllers will not stop on
their own.** The DAC keeps
holding whatever voltage it was last told to hold, and the robot drives away with nothing in
control of it.

> **What decision D8 changed here, 2026-09-19.** This paragraph used to say the Spine switches
> off when the larger pack's BMS cuts out, because the electronics ran from that pack. They
> now run from their own 12 V battery, so a pack dying no longer unpowers the Spine. Test 15
> keeps its meaning — cut the Teensy's power and the watchdog must stop the robot — but the
> event that would cause it in the field has moved. **Test 19 is that event**, and it is not
> the same test: test 15 cuts the Spine alone, while test 19 takes the Brain and the Face down
> with it. Run both.

The hardware watchdog in `05-bom.md` section 1b is the entire replacement for that behaviour.
This is why it is listed as non-negotiable. Test 15 proves it works, and until test 15 is
signed off there is nothing standing between a dead Teensy and a runaway robot.

**Test 16 exists because the watchdog has one blind spot.** The watchdog only fires when the
Teensy stops kicking it. So consider a Teensy that is perfectly alive but has lost the I2C bus
to the DACs: it wants to command zero, it cannot, and it is still happily kicking the watchdog.
The throttle stays wherever it was.

The firmware has to close that gap itself. Every DAC write is checked, and **on a failed write
the Teensy must stop kicking the watchdog on purpose** — choosing to kill itself because it has
lost the ability to steer. Test 16 proves that path, and it is easy to leave out, because
nothing fails visibly until the day it matters.

Test 10 catches a mistake that is easy to make in code and dangerous in the field: a robot
that starts driving the instant you plug the battery in, because the stick was not centred or
the switch was left on.

---

## Re-test triggers

The whole table above is re-run from the start after any of these:

- Any change to the Spine firmware, however small
- Any change to the wiring of the E-stop chain, the contactor, the watchdog, or the fusing
- Any change to the throttle path: the DACs, their I2C wiring, or the opto-isolators
- Any change to the radio equipment or its binding
- Any change to how the Brain and the Spine talk to each other
- The robot being transported, dropped, or repaired in the field

The last one matters at the event. After a repair in the dust at night, run at least tests 1,
2, 3 and 9 before the robot goes near people again.

---

## Sign-off

| | Name | Date |
|---|---|---|
| All twenty tests passed | | |
| Re-tested after last firmware change | | |
| Re-tested on site at Midburn | | |
