# 05 — Bill of materials

What to buy, in the order to buy it, with the traps attached to each part.

**About the prices.** They are estimates in US dollars, from memory, and they are not quotes.
Check every one before ordering. Prices for the Jetson and the cameras in particular move a
lot. Treat the totals as a planning figure, not a budget you can commit to.

**About the lead times.** "Stock" means a normal shop will post it this week. "Long" means
plan four to eight weeks, usually because it ships from China or is a low-volume industrial
part. The long-lead items are the ones to order first, even if you will not use them for
months.

---

## 1. Buy now — the de-risking order

This is about 350 dollars, and it is the cheapest way to find out early whether the drive
electronics are going to be a problem. Everything here is useful on a bench with no frame and
no body.

| Qty | Part | Est. | Lead | Notes |
|---|---|---|---|---|
| 1 | VESC, 75 V / 100 A class (Flipsky FSESC 75100, Spintend Ubox) | 130 | Long | **Buy one, not two.** Prove it works with your motor before doubling up. Must have CAN and a motor temperature input. |
| 1 | Teensy 4.1 | 32 | Stock | Has three CAN controllers on the chip. It still needs an external transceiver. |
| 2 | CAN transceiver breakout, 3.3 V (SN65HVD230 / MCP2562FD) | 10 | Stock | Buy a spare. They are the first thing you blow up. |
| 1 | RC transmitter and receiver set, 8+ channels | 180 | Stock | See section 6 for what the channels are for. |
| 1 | Multimeter with a clamp for DC current | 60 | Stock | The clamp matters. You cannot break into a 40 A circuit to measure it. |
| 1 | Bench power supply, 60 V 5 A, adjustable current limit | 90 | Stock | The current limit turns a wiring mistake into a beep instead of a fire. Borrow one if you can. |
| — | Shock bolt retrofit steel and fasteners (decision D2) | 50 | Stock | See `02-shock-bolt.md`. Small money, and it unblocks putting load on the pods. |

### The one thing to check on day one

Before anything else, get **one VESC driving one pod motor from the VESC's own configuration
tool**, with the pod on blocks. Not from the Teensy. If the hub motor's hall sensors are
damaged, or its winding resistance is wrong for the controller, you want to find out now and
not in month four.

---

## 2. Frame and drive — phase 1

| Qty | Part | Est. | Lead | Notes |
|---|---|---|---|---|
| 1 | VESC, second one, identical to the first | 130 | Long | Identical. Do not mix models across the two sides; the tuning will not transfer. |
| 2 | DC contactor, 48 V coil, 80 A+ **DC rated** | 200 | Long | Albright SW-series or Gigavac. **An AC-rated relay will weld shut.** `04-power-and-wiring.md` section 5. |
| 2 | Fuse, 60 A, and holders | 25 | Stock | Class T or ANL. One per pack. |
| 3 | Fuse, 10 A, and holders | 15 | Stock | 12 V converter, amplifier supply, spare. |
| 10 m | 10 AWG silicone wire, red and black | 40 | Stock | Silicone, not PVC. It has to stay flexible when hot. |
| 10 m | 12 AWG silicone wire | 30 | Stock | Motor phases. |
| 1 set | Ring lugs, heatshrink, and a proper crimp tool | 70 | Stock | The tool is not optional. See `04-power-and-wiring.md` section 8. |
| 4 | Anderson connectors, 50 A+ | 30 | Stock | The main disconnect on each pack, plus spares. |
| 1 | Latching mushroom emergency stop, red, IP65 | 25 | Stock | Normally-closed contact. |
| 1 | Isolated DC-DC, 48→12 V, 100 W (Mean Well SD-100C-12) | 70 | Stock | **Isolated.** Check it: no continuity from output negative to input negative. It is 159 × 97 × 38, which is bigger than it sounds — the shelf model accounts for that. |
| 1 | Buck converter, 48→32 V, 150 W, non-isolated | 25 | Stock | The amplifier's supply only. `04-power-and-wiring.md` section 4. |
| 1 | Buck converter, 12→5 V, 5 A | 12 | Stock | Teensy, ESP32, head servos. |
| — | Capacitors, 4700 µF 25 V, and TVS diodes | 20 | Stock | Rail buffer and VESC input protection. |
| — | Steel box tube 60×30×3 and 30×30, plate, M12 10.9 bolts | 300 | Stock | Cut list is echoed by `cad/walle_frame.scad`. |
| 12 mm | Birch plywood sheet | 60 | Stock | Battery box (six panels) and electronics shelf. |
| 2 | Castor wheels, Ø75, and mounting steel | 60 | Stock | Anti-tip. `cad/walle_frame.scad`. |

### Sealing the battery box — small money, and it decides whether the packs survive

The box hangs inboard of the belts, which throw sand at it. `06-why-the-batteries-are-low.md`
has the reasoning. Cheap parts, so buy spares of all of them.

| Qty | Part | Cost, USD | Lead | Notes |
|---|---|---|---|---|
| 5 m | Closed-cell foam tape, 3 mm, self-adhesive | 10 | Stock | The lid gasket. EPDM, not open-cell — open-cell soaks up water and holds grit. |
| 1 sheet | Closed-cell foam, 8 mm | 10 | Stock | The pad on top of the packs. Clamps them down and takes the vibration. |
| 8 | Silicone blanking plug, Ø30 | 10 | Stock | 4 needed, 4 spare. **These plug the M12 spanner holes.** Without them the rest of the sealing is pointless. Check them every morning. |
| 2 | Screw-in membrane vent, M12, IP67 (Gore type or equivalent) | 16 | Stock | 1 needed, 1 spare. Goes in the **lid**. A sealed box breathes with the day/night temperature swing; this is the clean path so it does not pull dust through a leak. |
| 4 | Cable gland, M16, IP68 | 10 | Stock | Charge leads and pack sense wiring out of the box. Not a drilled hole. |
| 16 | M5 bolts, nuts and washers, 25 mm | 8 | Stock | 12 for the lid at 110 mm pitch, plus spares. A gasket only seals where it is squeezed. |
| 1 | Anderson or XT60 charge connector with a dust cap, body-mounted | 15 | Stock | The packs charge **in place** and do not come out in the field. |

### The contactor is the long pole

Two DC-rated contactors is the single biggest line in this section and the one most likely to
arrive late. Order them in phase 0 even though they are not needed until phase 2.

---

## 3. Compute and sensors — phase 2, and not before

Do not buy these early. They sit in a drawer losing value while you do metalwork, and a newer
version may appear.

| Qty | Part | Est. | Lead | Notes |
|---|---|---|---|---|
| 1 | Jetson Orin Nano 8 GB developer kit | 250 | Stock | Takes 9–19 V DC in, so it runs off the 12 V rail directly. |
| 1 | NVMe SSD, 500 GB | 40 | Stock | Do not run it from an SD card. They wear out and then corrupt, in the field. |
| 1 | Active cooler and a filtered intake fan | 30 | Stock | It throttles without one, and Midburn is hot. |
| 1 | OAK-D Lite depth camera | 150 | Stock | Runs the person-detection model on its own chip, so the Jetson gets a ready-made list. |
| 1 | RPLIDAR A1M8, 12 m 2D scanner | 100 | Stock | Enough for obstacle detection. The A2 is 2.5× the price for range you do not need. |
| 6 | VL53L1X time-of-flight distance sensor | 60 | Stock | The bumper ring. These wire to the **Spine**, not the Brain. |
| 1 | I2C multiplexer (TCA9548A) | 8 | Stock | Six VL53L1X boards share one I2C address. You need this or you need to sequence their XSHUT pins. |
| 1 | BNO085 IMU with fused heading | 30 | Stock | Gives a compass heading and detects pitch, which matters on a tippy robot. |
| 1 | u-blox NEO-M9N GPS module | 50 | Stock | Midburn is a flat featureless plain. GPS, not SLAM. |
| 1 | USB microphone | 20 | Stock | For speech. Get one with some directionality. |

---

## 4. Face and sound — phase 4

| Qty | Part | Est. | Lead | Notes |
|---|---|---|---|---|
| 2 | ESP32-S3 development board | 24 | Stock | Two, one per eye. See the warning below. |
| 2 | 2.1 inch round LCD, 480×480, QSPI (Waveshare) | 60 | Stock | 53 mm active area. The barrel in the CAD model is built around this size. |
| 2 | Clear acrylic dome or lens, Ø99 | 20 | Stock | Dust seal and the glassy look. `cad/walle_frame.scad`. |
| 4 | Metal-gear servo, 20 kg·cm | 60 | Stock | Head pan, head tilt, and one barrel tilt each. |
| 1 | TPA3255 class-D amplifier board | 40 | Stock | Runs on the 32 V supply, not the pack. |
| 2 | Full-range speaker, 6.5 inch | 70 | Stock | The Rev 012 deck already has the cutouts designed for these. |
| — | LED strip, drivers, eye illumination | 120 | Stock | |

### Warning: two round screens is harder than it looks

The 2.1 inch 480×480 panels are **QSPI**, not plain SPI, and they need a lot of bandwidth. One
ESP32-S3 has two SPI hosts that can do quad mode, so driving two panels from one board is
*plausible* but tight, and it is the kind of thing that works at 20 frames per second and then
tears when you add anything else.

**Budget for two ESP32-S3 boards, one per eye**, with a single wire between them for frame
sync. They are 12 dollars each. This removes the risk entirely and it means one eye keeps
working if the other board dies.

The alternative, if you want one board, is the 1.28 inch GC9A01 panel — trivially easy to
drive in pairs on shared SPI. But its active area is only 32 mm, which fills 30 % of a 105 mm
barrel instead of 50 %, and the eyes are the whole point. Not worth the saving.

---

## 5. Body — phase 5

Buy this against a finished robot you can measure, not against the CAD model.

| Qty | Part | Est. | Lead | Notes |
|---|---|---|---|---|
| — | Rigid foam board, 50 mm | 150 | Stock | The bulk of the shell. Keep the top light: `00-plan.md` locked decision L6. |
| — | 4 mm plywood skin | 80 | Stock | |
| — | Fibreglass cloth, resin, filler, primer, paint | 350 | Stock | |
| — | Aluminium angle, hinges, catches, gas strut for the lid | 120 | Stock | The body top is the access lid for the shelf. |
| — | Steel for the neck and the head frame | 60 | Stock | |

---

## 6. What the radio channels are for

Eight channels sounds like a lot until you allocate them. This is the minimum set:

| Ch | Function | Type | Fails to |
|---|---|---|---|
| 1 | Throttle, forward and back | Stick | Centre |
| 2 | Steering | Stick | Centre |
| 3 | **Arm** | 2-position switch | **Off** |
| 4 | Mode: MANUAL / ASSIST | 2-position switch | **MANUAL** |
| 5 | Speed limit | Dial | **Slowest** |
| 6 | Head pan override | Dial | Centre |
| 7 | Trigger a sound or a behaviour | Momentary | Off |
| 8 | Spare | — | — |

**Set the receiver's failsafe explicitly for every channel**, to the values in the last
column. Do not rely on the default, and do not rely on "no pulse" behaviour — configure it,
then test it by switching the transmitter off while the robot is on blocks.

The wireless emergency stop is **not** one of these channels. It is a separate receiver on a
separate link, so that a failure of the main radio system and a failure of the stop system
cannot be the same failure.

---

## 7. Totals

| Section | Phase | Est. |
|---|---|---|
| 1 — de-risking | now | 550 |
| 2 — frame and drive | 1 | 1,110 |
| 2b — sealing the battery box | 1 | 80 |
| 3 — compute and sensors | 2 | 740 |
| 4 — face and sound | 4 | 400 |
| 5 — body | 5 | 760 |
| Tools and consumables not listed above | throughout | 250 |
| Spares kit (`00-plan.md` phase 6) | 6 | 300 |
| **Total** | | **≈ 4,200** |

This sits at the top of the 2,700 to 4,200 range in `00-plan.md` section 7, which is what
happens when estimates turn into named parts. The three places to cut, in order:

1. **The body.** Foam and paint is 760 dollars of the total and none of it makes the robot
   work. A rough body for the first outing is fine.
2. **The LiDAR.** 100 dollars, and the ToF bumper ring plus the depth camera already cover
   the safety case. The LiDAR is for the mapping you probably will not build.
3. **The GPS and IMU.** Only needed for `ASSIST` mode, which `00-plan.md` already lists as
   the first thing to drop.

The three places **not** to cut: the DC contactors, the crimp tool, and the current-limited
bench supply.

---

## 8. Spares to have at the festival

Failures in the desert are dust, heat and vibration, in that order. Carry the parts that
those break.

| Qty | Part | Why |
|---|---|---|
| 1 | VESC | The most expensive thing that can die, and it kills one whole track. |
| 2 | CAN transceiver | Cheap, and they fail. |
| 1 | 12→5 V converter | Loses the Spine and the Face together. |
| 1 | ESP32-S3 board | An eye. |
| — | Every fuse value, several of each | Obvious, and always forgotten. |
| — | Crimp lugs, heatshrink, wire, the crimp tool | You will be making cables at night. |
| 1 | Set of servos | Sand gets into gear trains. |
| — | Compressed air, brushes, filter material | The actual most useful items in the box. |
