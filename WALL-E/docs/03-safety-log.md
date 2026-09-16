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
| 8 | CAN wire disconnected | Unplug one CAN wire at a VESC | Both motors stop, not just one | | | |
| 9 | Arm switch off | Flick the arm switch to off while driving | Ramp to zero | | | |
| 10 | Power on while armed | Connect the battery with the arm switch already ON | Robot must NOT move. It must require the switch to be cycled off then on | | | |
| 11 | One pack disconnected | Open the left pack's main switch while driving forward | **Both** tracks stop. The robot must NOT pivot on the surviving track | | | |
| 12 | The other pack disconnected | Repeat test 11 on the right pack | Same as test 11 | | | |
| 13 | Uneven pack voltage | Drive with the packs at clearly different charge levels | It still drives straight. Any pull to one side means rule 11 compensation is not working | | | |
| 14 | Ground bond removed | With the robot parked and unarmed, disconnect the negative bond between the packs | CAN drops, so the Spine sees both VESCs stop reporting and refuses to arm at all | | | |
| 15 | **Spine unpowered mid-drive** | Cut power to the Teensy while driving forward | Both VESCs hit their own command timeout and release within 1 s. The robot must NOT pivot on one track | | | |

Tests 11 and 12 are the most important new ones, and they are specific to having one battery
per pod. On a skid-steer machine, one dead track does not slow the robot down — the surviving
track spins it on the spot. Both of these must produce a stop of **both** sides.

Run test 14 parked and unarmed. It is checking that a missing ground bond fails safe rather
than producing unpredictable CAN behaviour while driving.

**Test 15 is the one the whole electronics supply decision rests on.** The electronics run from
the larger pack only, so if that pack's BMS cuts out, the Spine switches off and cannot enforce
any of the rules above. The only thing left protecting you is each VESC's own command timeout.
Set that timeout explicitly in both controllers — do not assume the default is enabled — and
prove it here before the robot goes near anybody.

Test 10 catches a mistake that is easy to make in code and dangerous in the field: a robot
that starts driving the instant you plug the battery in, because the stick was not centred or
the switch was left on.

---

## Re-test triggers

The whole table above is re-run from the start after any of these:

- Any change to the Spine firmware, however small
- Any change to the wiring of the E-stop chain, the contactor, or the fusing
- Any change to the radio equipment or its binding
- Any change to how the Brain and the Spine talk to each other
- The robot being transported, dropped, or repaired in the field

The last one matters at the event. After a repair in the dust at night, run at least tests 1,
2, 3 and 9 before the robot goes near people again.

---

## Sign-off

| | Name | Date |
|---|---|---|
| All ten tests passed | | |
| Re-tested after last firmware change | | |
| Re-tested on site at Midburn | | |
