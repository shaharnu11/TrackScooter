# 03 — Safety log

Fill in by hand. Until every row is signed off, stay **10 m** from people.

- Run every test **while driving**. A stop from standstill proves nothing.
- Pass: stops, no lurch, no turn, stays stopped. ~0.5 s ramp is pass. A slam is fail (231 mm footprint can tip).

## Tests

| # | Test | How | Expected | Pass | Date | Notes |
|---|---|---|---|---|---|---|
| 1 | Physical E-stop | Mushroom while driving | Contactor opens, motors dead | | | |
| 2 | Wireless E-stop | Keyfob from 20 m | Same as 1 | | | |
| 3 | Transmitter off | Switch TX off | Ramp to zero. FS-iA6B may repeat last sticks — Spine must report `rc_frozen` and stop within `RC_FROZEN_MS` (500 ms) | | | |
| 4 | Out of range | Walk away | Same as 3. No restart without re-arm | | | |
| 5 | Brain USB out | Pull XPS serial in ASSIST | Watchdog, ramp, fall to MANUAL | | | |
| 6 | Brain power lost | Cut XPS in ASSIST | Same as 5 | | | |
| 7 | Bumper | Board in front of ToF, driving forward | Forward vetoed. Reverse still works | | | |
| 8 | Throttle wire off | Unplug one DAC→controller | **Both** motors stop (rule 4 halls) | | | |
| 9 | Arm off | Flick arm while driving | Ramp to zero | | | |
| 10 | Power on armed | Connect battery with arm already ON | No move. Cycle arm off then on | | | |
| 11 | Pack A open | Open left pack switch | **Both** tracks stop. Wiring: coils on pack A. Run once with Teensy unplugged | | | |
| 12 | Pack B open | Repeat on right pack | **Both** stop. Firmware: rule 4. Not the same as 11 | | | |
| 13 | Uneven packs | Different charge | Drives straight (rule 11) | | | |
| 14 | Ground bond off | Parked, unarmed, disconnect pack negatives | Far-pack readings wrong. Refuses to arm | | | |
| 15 | Spine unpowered | Cut Teensy power while driving | Watchdog relay opens. No pivot | | | |
| 16 | Teensy alive, I2C dead | Pull one DAC I2C wire | Write fails, kicks stop, relay opens | | | |
| 17 | Reverse glitch | On blocks, toggle reverse while going forward | Zero, wait for halls, then change line | | | |
| 18 | Pivot current | On sand, full stick turn, watch ACS758 | Stays in limit or Teensy backs off | | | |
| 19 | 12 V fuse out | Pull electronics fuse, packs healthy | Arm MOSFET drops both contactors. Coast, no pivot | | | |
| 20 | 12 V bond | Parked: 12 V negative to pack negative | **Exactly one** path through the bond | | | |

11 ≠ 12. Pack A: copper. Pack B: halls. Do 12 on blocks first.

Scooter controllers have **no timeout**. DAC holds last voltage. Test 15 is the watchdog. Test 16 is its blind spot (alive Teensy, stuck throttle).

## Re-test

Whole table after: Spine firmware, E-stop/contactor/watchdog/fuse wiring, throttle path, radio, Brain–Spine protocol, transport, drop, field repair.

At the event, after a night repair: at least 1, 2, 3, 9 before people.

## Sign-off

| | Name | Date |
|---|---|---|
| All twenty passed | | |
| Re-tested after last firmware change | | |
| Re-tested at Midburn | | |
