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

Sections 1 and 1b together are about **498 dollars**, and this is the cheapest way to find out early whether the drive
electronics are going to be a problem. Everything here is useful on a bench with no frame and
no body.

**No VESCs in this list.** Decision D7 in `00-plan.md` used to recommend buying two, at 260
dollars. You already own two 48 V scooter controllers, **and they have a reverse line**,
which was the one thing that could have ruled them out — without reverse on each side
independently the robot cannot turn on the spot, only in wide arcs. So the plan is now to
drive the controllers you have from the Teensy, and to buy back the telemetry they do not
give you with a handful of cheap sensors. That costs 76 dollars instead of 260. Section 1b is
the parts list and the conditions that come with it.

| Qty | Part | Est. | Lead | Notes |
|---|---|---|---|---|
| 1 | Teensy 4.1 | 32 | Stock | Has three CAN controllers on the chip. It still needs an external transceiver. |
| 2 | CAN transceiver breakout, 3.3 V (SN65HVD230 / MCP2562FD) | 10 | Stock | Not needed to drive the scooter controllers, which have no CAN. Buy them anyway — they are 5 dollars each and they are what you need the day you move to VESCs. |
| 1 | RC transmitter and receiver set, 8+ channels | 180 | Stock | See section 6 for what the channels are for. |
| 1 | Multimeter with a clamp for DC current | 60 | Stock | The clamp matters. You cannot break into a 40 A circuit to measure it. |
| 1 | Bench power supply, 60 V 5 A, adjustable current limit | 90 | Stock | The current limit turns a wiring mistake into a beep instead of a fire. Borrow one if you can. |
| — | Shock bolt retrofit steel and fasteners (decision D2) | 50 | Stock | See `02-shock-bolt.md`. Small money, and it unblocks putting load on the pods. |

### The one thing to check on day one

Before anything else, get **one pod motor spinning from its own scooter controller and a
physical throttle**, with the pod on blocks. No Teensy, no Arduino, no code. If a hub motor's
hall sensors are damaged you want to find out today and not in month four, and this test
costs nothing because you already own every part of it.

---

## 1b. Driving the scooter controllers from the Teensy — about 76 dollars

A throttle is three wires: **+5 V, ground, and a signal wire** carrying roughly 0.8 V at rest
and 4.2 V at full. The controller cannot tell whether a thumb or a computer made that
voltage. So you replace the throttle with a chip that makes the voltage on command.

**Measure your real throttle first.** Read the signal wire at rest and at full with the
multimeter and match those numbers. Do not assume 0.8 and 4.2.

| Qty | Part | Est. | Lead | Notes |
|---|---|---|---|---|
| 2 | MCP4725 12-bit I2C DAC breakout | 8 | Stock | One per controller. Makes the throttle voltage. Two share one I2C bus at addresses 0x62 and 0x63. |
| 1 | I2C level shifter, 4 channel (BSS138 or TXS0102) | 4 | Stock | The DAC has to run at 5 V to reach full throttle, and **the Teensy is not 5 V tolerant.** Without this you damage its pins. |
| 4 | Opto-isolator, PC817, plus resistors | 5 | Stock | Two per controller: one pulls the **reverse** line, one pulls the **e-brake** line. Isolated, so a controller fault cannot travel back into the Teensy. |
| 2 | Watchdog: TLC555 or TPS3823, plus a signal relay with normally-closed contacts | 14 | Stock | **Not optional.** See the warning below. |
| 2 | ACS758 100 A bidirectional hall current sensor | 20 | Stock | Puts back the current reading the VESC would have given you. One per pack lead. |
| — | Resistors for the motor thermistor divider | 2 | Stock | Reads the hub motor's **own** temperature sensor straight into the Teensy. This is the defence against risk R5, and it replaces arbitration rule 9's data source. |
| — | Resistors for two pack voltage dividers | 2 | Stock | Arbitration rules 5 and 11 used to read pack voltage off the VESC's CAN messages. There is no CAN now, so the Teensy has to measure it. Mind the ground reference. |
| — | Wiring to bring both motors' hall sensors to the Teensy | 6 | Stock | Arbitration rule 4 asked "is each track alive?" and got the answer from CAN. Now the Teensy counts hall edges instead: commanded to move, halls not changing, track is dead. |
| — | Shielded 4-core signal cable and connectors | 15 | Stock | Throttle lines run beside motor phase wires. Shield them or the robot twitches. |

### Do not use an Arduino PWM pin for the throttle

An Arduino has no true analogue output. `analogWrite` gives a square wave, and filtering it
with a resistor and capacitor gives a slow, noisy voltage. Noise on a throttle line is a
robot that twitches. The DAC is 4 dollars.

### Warning: a DAC does not spring back

A real throttle returns to zero when you let go. **A DAC holds its last value forever.** If
the Teensy crashes mid-drive, the throttle voltage stays exactly where it was and the robot
keeps going.

So the watchdog is a hardware part, not a software one: the Teensy sends a heartbeat pulse,
and a relay with **normally-closed** contacts is held open by it. Stop the pulses — crash,
reset, unplugged wire — and the relay falls closed and **shorts the throttle signal to
ground**. Nothing in software has to work for this to happen.

Wire the emergency stop into the controller's **e-brake** input as well. That is what it is
there for.

### What you still give up, and what it costs to get back

| The VESC would give you | With scooter controllers |
|---|---|
| Motor temperature | **Bought back for 2 dollars.** The hub motor has its own thermistor in its cable. Read it directly. |
| Motor current | **Bought back for 20 dollars** with the ACS758 sensors. |
| Field-oriented control — smooth torque from standstill | **Cannot be bought back.** Scooter controllers use six-step commutation, which judders at walking pace. Skid steer lives at walking pace. |
| Tunable current limit, ramp rate, cutoff | **Cannot be bought back.** Fixed in their firmware, tuned for a 15 kg scooter carrying a person, not a 100 kg tracked robot. |
| Full-speed reverse | Scooter reverse is usually capped near 30% and often refuses to change direction while the wheel is still turning. |

Also check for **cruise control**. Some scooter controllers engage it automatically after a
few seconds of steady throttle. On a robot in a crowd that is dangerous. If yours does it and
cannot be turned off, that alone is worth the 260 dollars.

**The upgrade path stays open.** Two VESCs are 260 dollars whenever you decide the juddering
at low speed is unacceptable. The Teensy, the CAN transceivers, the wiring and the frame are
all unchanged — you swap the controllers and drop the DACs.

---

## 2. Frame and drive — phase 1

| Qty | Part | Est. | Lead | Notes |
|---|---|---|---|---|
| 2 | DC contactor, 48 V coil, 80 A+ **DC rated** | 200 | Long | Albright SW-series or Gigavac. **An AC-rated relay will weld shut.** `04-power-and-wiring.md` section 5. |
| 2 | Fuse, 60 A, and holders | 25 | Stock | Class T or ANL. One per pack. |
| 3 | Fuse, 10 A, and holders | 15 | Stock | 12 V converter, amplifier supply, spare. |
| 10 m | 10 AWG silicone wire, red and black | 40 | Stock | Silicone, not PVC. It has to stay flexible when hot. |
| 10 m | 12 AWG silicone wire | 30 | Stock | Motor phases. |
| 1 set | Ring lugs, heatshrink, and a proper crimp tool | 70 | Stock | The tool is not optional. See `04-power-and-wiring.md` section 8. |
| 4 | **XT90-S anti-spark** connector pairs | 20 | Stock | The main disconnect on each pack, plus two spares. **Was Anderson SB50.** The "-S" is not optional: it is the built-in resistor that pre-charges the controller capacitors, so the contacts stop sparking every time you plug in. **Put the SOCKET half on the battery** — the disconnect sits ahead of the fuses, so exposed pins on the pack side would be an unfused short waiting for a dropped spanner. See `04-power-and-wiring.md` §5. |
| 8 | Silicone caps for the XT90 halves | 6 | Stock | Dust cover and idiot guard in one. Anderson housings were genderless and recessed; XT is not, so this replaces a safety property we gave up. |
| 1 | Latching mushroom emergency stop, red, IP65 | 25 | Stock | Normally-closed contact. |
| 1 | Isolated DC-DC, 48→12 V, 100 W (Mean Well SD-100C-12) | 70 | Stock | **Isolated.** Check it: no continuity from output negative to input negative. It is 159 × 97 × 38, which is bigger than it sounds — the shelf model accounts for that. |
| 1 | Buck converter, 48→32 V, 150 W, non-isolated | 25 | Stock | The amplifier's supply only. `04-power-and-wiring.md` section 4. |
| 1 | Buck converter, 12→5 V, 5 A | 12 | Stock | Teensy and ESP32 only. No servos any more, so this is a much easier load. |
| — | Capacitors, 4700 µF 25 V, and TVS diodes | 20 | Stock | Rail buffer and controller input protection. |
| — | Steel box tube 60×30×3 and 30×30, plate | — | — | **You already have the steel.** Cut list is echoed by `cad/walle_frame.scad`: 2 × 550 rails, 2 × 240 cross members, 1580 mm of 60×30 in total. |
| — | M12 10.9 bolts, and the Ø25/Ø13×30 sleeves to weld into the rails | 25 | Stock | The sleeve is what stops an M12 crushing a 3 mm box wall. Not optional. |
| 12 mm | Birch plywood sheet | 60 | Stock | Battery box (six panels) and electronics shelf. |
| 2 | Castor wheels, Ø75 | 35 | Stock | Anti-tip. `cad/walle_frame.scad`. Mounting steel you already have. |

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
| 2 | **XT60** charge connector with a dust cap, body-mounted | 12 | Stock | One per pack. The packs charge **in place** and do not come out in the field. XT60 is right here and wrong for the main disconnect: charging is a few amps, it is plugged in rarely, and there is no capacitor bank to spark into. |

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
| — | ~~Metal-gear servos~~ | — | — | **Deleted 2026-09-17. The head is rigid — no pan, no nod, no tilt.** Saves 60 dollars, 4 gear trains that sand would have eaten, and the whole servo power branch. |
| 1 | Camera mount hardware and a plywood hood for the lens | 15 | Stock | The OAK-D goes **under** the eye barrels, not between them. See the head note below. |
| 1 | TPA3255 class-D amplifier board | 40 | Stock | Runs on the 32 V supply, not the pack. `04-power-and-wiring.md` section 4. |
| 2 | Full-range or coaxial speaker, 6.5 inch, **4 Ω** | 70 | Stock | One per amplifier channel. Ø165 cutout, Ø190 rim, 50 mm deep — the chest panel is drilled for exactly that. **Check the mounting depth on the one you buy**; over 200 mm and the enclosure has to grow. |
| 2 | Speaker grille, Ø190, steel | 20 | Stock | Not optional. A crowd will push a finger through an open cone. |
| — | 12 mm ply for the two enclosures, plus bracing | 25 | Stock | About 0.6 m². Sizes echoed by `cad/walle_frame.scad`. |
| — | Gasket tape, acoustic wadding, M5 bolts for the drivers and the boxes | 20 | Stock | The boxes **bolt** to the chest panel — they shade 54 % of the shelf and have to lift out. |
| — | LED strip, drivers, eye illumination | 120 | Stock | |

### The speakers are not just an audio decision

They are 7.4 kg, they sit 584 mm up, and both of them are forward of centre. That combination
took **1.5° off the forward tipping margin** on its own, leaving 5.4° between going over and
the anti-tip castor catching. See risk R10. Anything else you add high or forward spends the
same number, so weigh the real parts before adding a third thing.

The other thing worth knowing before you buy: **sensitivity matters more than power out here.**
Outdoors there are no walls to reflect sound, so bass is largely hopeless whatever you do. A
driver rated 3 dB higher in sensitivity is worth more than doubling the amplifier power. Pick
on the sensitivity figure, not the "max watts" number on the box.

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

## 5. Body and head — phase 5

**The body is PLYWOOD now.** Owner decision 2026-09-17: no foam core, no
fibreglass, no filler, no paint job. A 12 mm plywood box, which is what
`cad/walle_frame.scad` already models the walls as.

This is the single best change in the whole document. It is **330 dollars
cheaper** and the robot came out **11.5 kg lighter**, because the model was
carrying a 25 kg guess for foam and glass and the real plywood box works out at
13.6 kg computed from its own geometry. Every stability number improved:

| | Was, foam body | Now, plywood body |
|---|---|---|
| Whole robot | 100.4 kg | **88.9 kg** |
| Centre of mass | 349 mm | **334 mm** |
| Tips forward at | 17.7° | **18.4°** |
| Margin over the castor | 5.4° | **6.1°** |
| Ground pressure | 0.184 kg/cm² | **0.163 kg/cm²** |

| Qty | Part | Est. | Lead | Notes |
|---|---|---|---|---|
| — | 12 mm birch plywood, about 1.7 m² | 130 | Stock | Floor, four walls, and the lid. Sizes come straight out of `cad/walle_frame.scad`. |
| — | 12 mm plywood for the eye rings, about 0.3 m² | 25 | Stock | 24 discs of Ø105. See the head note below. |
| — | Glue, screws, corner blocks | 30 | Stock | A plywood box is only as good as its corners. |
| — | Hinges, catches, gas strut for the lid | 90 | Stock | The body top is the access lid for the shelf. Aluminium angle no longer needed. |
| — | Exterior sealer or varnish | 40 | Stock | Not for looks. Plywood in the Negev sees big day-to-night humidity swings and delaminates if left bare. |
| — | Steel for the neck and the head frame | — | — | **You already have the steel.** |

### The eyes are wood, and that changes how they are made

The barrels are **Ø105 round, built as a stack of 12 plywood rings**, glued up
and then sanded round on the outside. Nobody is turning a 105 mm tube, and a
stack of hole-sawn discs gets there with tools you have.

That fixes the barrel length to a multiple of the sheet thickness: **12 rings
of 12 mm = 144 mm**, not the 150 it used to be. Two guards now enforce it.

Per barrel, from the cut list the model prints:

| Rings | Bore | What it is |
|---|---|---|
| 5 | Ø59 | The screen well. **This depth is the sun shade.** |
| 1 | Ø53 | The shoulder the screen sits on |
| 6 | Ø81 | Cable room behind. **No servos** — the head is rigid |

**The camera does not fit between the barrels.** They are 128 mm apart centre to centre
with 105 mm bodies, so the gap is 23 mm and the OAK-D Lite is 91 mm wide. Spreading the eyes
far enough apart would take the head to 311 mm across and stop it looking like WALL-E. So it
mounts **under** the barrel pair, on the front of the yoke, with a 30 mm plywood hood over
the lens. The barrels above it read as a brow, and the hood shades the lens from sun above
25 degrees — a lens pointed at the Negev sky needs shade as much as the screens do.

**Do not change the 60 mm recess to suit the ring count.** 60 is exactly five
rings, so the screen lands on a glue line shoulder rather than mid-ring, and
60 mm is what shades the screen from sun above 49° elevation. Negev midday is
75 to 80°. There is a guard on each of those two facts.

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
| 6 | **Look-turn enable** | Switch | Off |
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
| 1 — de-risking | now | 422 |
| 1b — throttle interface for the scooter controllers | now | 76 |
| 2 — frame and drive, including sealing the box | 1 | 754 |
| 3 — compute and sensors | 2 | 738 |
| 4 — face and sound | 4 | 414 |
| 5 — body and head, plywood | 5 | 315 |
| Tools and consumables not listed above | throughout | 250 |
| Spares kit (`00-plan.md` phase 6) | 6 | 300 |
| **Total** | | **≈ 3,270** |

Every figure above is now **summed from its own table** rather than typed in.
Doing that turned up three that had drifted: section 1 said 350 when it summed
to 552, section 3 said 740 against 738, and section 4 said 400 when it actually
sums to 459. The total was understated in one place and overstated in another.

### How it got from 4,200 to 3,270

| Change | Saving |
|---|---|
| The body is plywood, not foam and fibreglass | **445** |
| You already own the frame and head steel | **335** |
| Use the scooter controllers instead of two VESCs | **180**, after 76 spent on the interface |
| The head is rigid, so four servos are gone | **60**, less 15 for the camera mount |
| Correcting section 4, which was understated | **−59** |

The two big ones cost nothing in capability. **The plywood body actively made
the robot better**: 11.5 kg lighter, centre of mass 15 mm lower, and 0.7° more
forward tipping margin, because the 25 kg foam-and-glass figure was a guess and
the plywood box is computed from its own geometry.

The rigid head is the cheapest change of all, and it removes four gear trains from a
machine that will spend a week in blowing sand. It is not free, though: the cost moved into
the firmware, because looking left is now a drive command. Read
[`01-architecture.md`](01-architecture.md), "Looking around now means driving", before you
write any of the personality code.

**The controller decision is still the one you may have to undo.** Hold its 260
dollars as contingency. If six-step commutation judders at walking pace, two
VESCs drop straight in.

The three places to cut, in order:

1. **The LiDAR.** 100 dollars, and the ToF bumper ring plus the depth camera already cover
   the safety case. The LiDAR is for the mapping you probably will not build.
3. **The GPS and IMU.** Only needed for `ASSIST` mode, which `00-plan.md` already lists as
   the first thing to drop.

The four places **not** to cut: the DC contactors, the crimp tool, the current-limited bench
supply, and the **hardware throttle watchdog** in section 1b.

---

## 8. Spares to have at the festival

Failures in the desert are dust, heat and vibration, in that order. Carry the parts that
those break.

| Qty | Part | Why |
|---|---|---|
| 1 | 48 V controller with a reverse line, 50 | You own exactly two and need exactly two. One dying kills one whole track, and the robot cannot turn on one track. |
| 2 | MCP4725 DAC breakout | 4 dollars, and it is the single point of failure for a whole side's throttle. |
| 2 | CAN transceiver | Cheap, and they fail. |
| 1 | 12→5 V converter | Loses the Spine and the Face together. |
| 1 | ESP32-S3 board | An eye. |
| — | Every fuse value, several of each | Obvious, and always forgotten. |
| — | Crimp lugs, heatshrink, wire, the crimp tool | You will be making cables at night. |
| 1 | Ø53 round LCD panel | The eyes are the whole face now, and there is no servo to blame. |
| — | Compressed air, brushes, filter material | The actual most useful items in the box. |
