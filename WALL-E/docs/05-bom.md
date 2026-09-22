# 05 — Bill of materials

What to buy, in the order to buy it, with the traps attached to each part.

**About the prices.** Most are still estimates in US dollars and not quotes. The eight in
section 9's table were checked against real AliExpress listings on 2026-09-17 and were all
**over**-estimated; nothing came back cheaper than listed, so assume the unchecked rows are
a little high too. Check every one before ordering. Prices for the Jetson and the cameras in particular move a
lot. Treat the totals as a planning figure, not a budget you can commit to.

**About the currency.** The Est. column is **US dollars**, but you are buying in **shekels**.
At ₪1 = $0.33 (checked 2026-09-18), ₪100 is about $33. Two things follow, and they matter more
than they look:

1. **Compare delivered prices, not part prices.** The dollar figures in this document are bare
   part prices. An AliExpress price to Israel usually includes shipping; a US or EU
   distributor's does not, and shipping one small board from the US can cost as much as the
   board. A part that looks 50 % dearer on AliExpress can still be the cheaper way to get it.
2. **Watch the order-total threshold.** Israel exempts small personal imports from VAT and
   duty below roughly 75 dollars, and charges VAT above it. Verify the current figure before
   you commit, but the shape of it means **several small orders can cost less than one big
   one** — which also suits this document, because it is already split into phases you buy
   at different times.

**About the lead times.** "Stock" means a normal shop will post it this week. "Long" means
plan four to eight weeks, usually because it ships from China or is a low-volume industrial
part. The long-lead items are the ones to order first, even if you will not use them for
months.

---

## 1. Buy now — the de-risking order

Sections 1 and 1b together are about **422 dollars**, and this is the cheapest way to find out early whether the drive
electronics are going to be a problem. Everything here is useful on a bench with no frame and
no body.

**No VESCs in this list.** Decision D7 in `00-plan.md` used to recommend buying two, at 260
dollars. You already own two 48 V scooter controllers, **and they have a reverse line**,
which was the one thing that could have ruled them out — without reverse on each side
independently the robot cannot turn on the spot, only in wide arcs. So the plan is now to
drive the controllers you have from the Teensy, and to buy back the telemetry they do not
give you with a handful of cheap sensors. That costs 76 dollars instead of 260. Section 1b is
the parts list and the conditions that come with it.

| Qty | Part | Est. | Lead | Notes | Buy from — **read §9 first** |
|---|---|---|---|---|---|
| 1 | Teensy **4.0** | 38 | Stock | The Spine. 600 MHz i.MX RT1062 — **the same chip as the 4.1**. Downgraded from the 4.1 on 2026-09-18 because both reasons for picking it had expired: decision D7 killed the CAN bus, and `01-architecture.md` bans SD-card logging. The Spine needs about 21 pins with 6 analogue (2 pack voltages, 2 motor thermistors, 2 ACS758); the 4.0's 24 edge pins include 14 analogue, so it fits without using the awkward bottom pads. **Not 5 V tolerant** — it needs the level shifter in §1b. | [AliExpress ₪114.08](https://he.aliexpress.com/item/1005009258422669.html) |
| 1 | RC transmitter and receiver set, 8+ channels | 120 | Stock | See section 6 for what the channels are for. | [search](https://www.aliexpress.com/w/wholesale-8-channel-RC-transmitter-receiver.html) |
| 1 | Multimeter with a clamp for **DC** current | 25 | Stock | The clamp matters. You cannot break into a 40 A circuit to measure it. **Check the listing says DC amps, not only AC.** Most cheap clamp meters are AC-only and will read 0 A on a battery wire. Needs 100 A DC or more. You use it to find the controllers' real current limit, to calibrate the two ACS758 sensors, and to measure contactor coil inrush — see the 167 W warning in §9. | [AliExpress ₪77.35](https://he.aliexpress.com/item/1005002037433118.html) |
| 1 | Bench power supply, 60 V 5 A, adjustable current limit | 69 | **3 weeks** | The current limit turns a wiring mistake into a beep instead of a fire. Borrow one if you can. Priced from a Jesverty 60V05A listing at ₪207.92, about 69 USD, or 61 with the on-page coupon. Two checks before paying: keep the **220 V EU plug** variant selected, and confirm the description says **CC / constant current** — you need the supply to drop its voltage automatically at the limit, not just display the current. 60 V is the minimum useful figure because a full 48 V pack sits at about 54.6 V. | [search: Jesverty 60V05A](https://www.aliexpress.com/w/wholesale-Jesverty-DC-lab-power-supply-60V-5A.html) — Jesverty Official Store, variant `60V05A-Model V`, 220 V EU plug |

### The one thing to check on day one

Before anything else, get **one pod motor spinning from its own scooter controller and a
physical throttle**, with the pod on blocks. No Teensy, no Arduino, no code. If a hub motor's
hall sensors are damaged you want to find out today and not in month four, and this test
costs nothing because you already own every part of it.

---

## 1b. Driving the scooter controllers from the Teensy — about 60 dollars

A throttle is three wires: **+5 V, ground, and a signal wire** carrying roughly 0.8 V at rest
and 4.2 V at full. The controller cannot tell whether a thumb or a computer made that
voltage. So you replace the throttle with a chip that makes the voltage on command.

**Measure your real throttle first.** Read the signal wire at rest and at full with the
multimeter and match those numbers. Do not assume 0.8 and 4.2.

| Qty | Part | Est. | Lead | Notes | Buy from — **read §9 first** |
|---|---|---|---|---|---|
| 2 | MCP4725 12-bit I2C DAC breakout | 4 | Stock | One per controller. Makes the throttle voltage. Two share one I2C bus at addresses 0x62 and 0x63. | [search](https://www.aliexpress.com/w/wholesale-MCP4725-DAC-module.html) |
| 1 | I2C level shifter, 4 channel (BSS138 or TXS0102) | 2 | Stock | The DAC has to run at 5 V to reach full throttle, and **the Teensy is not 5 V tolerant.** Without this you damage its pins. | [search](https://www.aliexpress.com/w/wholesale-BSS138-I2C-level-shifter.html) |
| 4 | Opto-isolator, PC817, plus resistors | 3 | Stock | Two per controller: one pulls the **reverse** line, one pulls the **e-brake** line. Isolated, so a controller fault cannot travel back into the Teensy. | [search](https://www.aliexpress.com/w/wholesale-PC817-optocoupler.html) |
| 2 | Watchdog: TLC555 or TPS3823, plus a signal relay with normally-closed contacts | 8 | Stock | **Not optional.** See the warning below. | [search](https://www.aliexpress.com/w/wholesale-TLC555-timer-IC.html) |
| 2 | ACS758 100 A bidirectional hall current sensor | 18 | Stock | Puts back the current reading the VESC would have given you. One per pack lead. | [search](https://www.aliexpress.com/w/wholesale-ACS758-100A.html) |
| — | Resistors for the motor thermistor divider | 2 | Stock | Reads the hub motor's **own** temperature sensor straight into the Teensy. This is the defence against risk R5, and it replaces arbitration rule 9's data source. | [search](https://www.aliexpress.com/w/wholesale-metal-film-resistor-kit.html) |
| — | Resistors for two pack voltage dividers | 2 | Stock | Arbitration rules 5 and 11 used to read pack voltage off the VESC's CAN messages. There is no CAN now, so the Teensy has to measure it. Mind the ground reference. | [search](https://www.aliexpress.com/w/wholesale-metal-film-resistor-kit.html) |
| — | Wiring to bring both motors' hall sensors to the Teensy | 6 | Stock | Arbitration rule 4 asked "is each track alive?" and got the answer from CAN. Now the Teensy counts hall edges instead: commanded to move, halls not changing, track is dead. | [search](https://www.aliexpress.com/w/wholesale-shielded-cable-4-core.html) |
| — | Shielded 4-core signal cable and connectors | 15 | Stock | Throttle lines run beside motor phase wires. Shield them or the robot twitches. | [search](https://www.aliexpress.com/w/wholesale-shielded-cable-4-core.html) |

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
at low speed is unacceptable. The Teensy, the wiring and the frame are all unchanged — you
swap the controllers and drop the DACs. You would also need two 3.3 V CAN transceivers, which
are **deliberately not on this list** (owner decision 2026-09-18): they are a $2 commodity part
with no other use in the current design, so buy them alongside the VESCs if that day comes.

---

## 2. Frame and drive — phase 1

| Qty | Part | Est. | Lead | Notes | Buy from — **read §9 first** |
|---|---|---|---|---|---|
| 2 | DC contactor, **48 V coil** (confirmed 2026-09-17), 80 A+ **DC rated** | 80 | Long | Albright SW-series or Gigavac. **An AC-rated relay will weld shut.** `04-power-and-wiring.md` section 5. | **§9 — not here** |
| 2 | Fuse, 60 A, and holders | 25 | Stock | Class T or ANL. One per pack. | **§9 — not here** |
| 3 | Fuse, 10 A, and holders | 15 | Stock | 12 V converter, amplifier supply, spare. | **§9 — not here** |
| 3 | Fuse, 5 A **slow-blow**, and holders | 6 | Stock | The contactor coil circuit. Slow-blow because it is sized for the coil inrush, not the 0.3 A holding current. See §9. | **§9 — not here** |
| 10 m | 10 AWG silicone wire, red and black | 40 | Stock | Silicone, not PVC. It has to stay flexible when hot. | [search](https://www.aliexpress.com/w/wholesale-10AWG-silicone-wire.html) |
| 10 m | 12 AWG silicone wire | 30 | Stock | Motor phases. | [search](https://www.aliexpress.com/w/wholesale-12AWG-silicone-wire.html) |
| 1 set | Ring lugs, heatshrink, and a proper crimp tool | 70 | Stock | The tool is not optional. See `04-power-and-wiring.md` section 8. | [search](https://www.aliexpress.com/w/wholesale-hydraulic-crimping-tool-cable-lug.html) |
| 4 | **XT90-S anti-spark** connector pairs | 20 | Stock | The main disconnect on each pack, plus two spares. **Was Anderson SB50.** The "-S" is not optional: it is the built-in resistor that pre-charges the controller capacitors, so the contacts stop sparking every time you plug in. **Put the SOCKET half on the battery** — the disconnect sits ahead of the fuses, so exposed pins on the pack side would be an unfused short waiting for a dropped spanner. See `04-power-and-wiring.md` §5. | [search](https://www.aliexpress.com/w/wholesale-XT90-S-anti-spark-connector.html) |
| 8 | Silicone caps for the XT90 halves | 6 | Stock | Dust cover and idiot guard in one. Anderson housings were genderless and recessed; XT is not, so this replaces a safety property we gave up. | [search](https://www.aliexpress.com/w/wholesale-XT90-connector-silicone-cap.html) |
| 1 | Latching mushroom emergency stop, red, IP65 | 25 | Stock | Normally-closed contact. | **§9 — not here** |
| 1 | **12 V 20 Ah LiFePO4 battery** — the electronics supply | 75 | Stock | **Replaces the isolated 48→12 V converter**, owner decision D8. 240 Wh against a 38 W rail is 6.3 hours. The Jetson takes 9–19 V in, so it runs off this directly. **Fit it LYING ON ITS SIDE**: upright it is 167 mm tall and it takes the air out of the speaker enclosures — `cad/walle_frame.scad` guards this. | [search](https://www.aliexpress.com/w/wholesale-12V-20Ah-LiFePO4-battery.html) |
| 1 | LiFePO4 charger, 14.6 V 5 A | 25 | Stock | For the battery above. **A lead-acid charger is not a LiFePO4 charger** — the float voltage is wrong and it will sit there cooking the pack. | [search](https://www.aliexpress.com/w/wholesale-14.6V-5A-LiFePO4-charger.html) |
| 1 | Fuse, 15 A, and holder, at the battery terminal | 5 | Stock | A 20 Ah LiFePO4 will push hundreds of amps into a short and its BMS is not a fuse. Mount it **at the terminal**, not at the far end of the run. | **§9 — not here** |
| — | ~~Isolated DC-DC, 48→12 V, 100 W (Mean Well SD-100C-12)~~ | — | — | **Deleted 2026-09-19 by decision D8.** Saves 70 dollars and, more usefully, deletes the one power part that could not be bought on AliExpress — see §9. There is no 48 V on the electronics rail any more. | deleted |
| 1 | Buck converter, 48→32 V, 150 W, non-isolated | 25 | Stock | The amplifier's supply only. `04-power-and-wiring.md` section 4. | [search](https://www.aliexpress.com/w/wholesale-DC-DC-buck-converter-48V-32V-150W.html) |
| 1 | Buck converter, 12→5 V, 5 A | 12 | Stock | Teensy and ESP32 only. No servos any more, so this is a much easier load. | [search](https://www.aliexpress.com/w/wholesale-DC-DC-buck-converter-12V-5V-5A.html) |
| — | Capacitors, 4700 µF 25 V, and TVS diodes | 20 | Stock | Rail buffer and controller input protection. | [search](https://www.aliexpress.com/w/wholesale-capacitor-4700uF-25V.html) |
| — | Steel box tube 60×30×3 and 30×30, plate | — | — | **You already have the steel.** Cut list is echoed by `cad/walle_frame.scad`: 2 × 550 rails, 2 × 263 cross members, 1626 mm of 60×30 in total. | owned |
| 2 | **Packer, 60×6 flat bar, 60 mm long, 2 holes Ø13** | 5 | Stock | One per side. Fills the 6 mm step between the carrier face the rail sits on and the green plate the M12s thread into. **Without it the bolts crush the rail wall into the gap and the joint has no clamp.** Offcut of the same 60×6 as the plates. | Offcut / steel stockist |
| — | M12 10.9 bolts, and the Ø25/Ø13×30 sleeves to weld into the rails | 25 | Stock | The sleeve is what stops an M12 crushing a 3 mm box wall. Not optional. | [search](https://www.aliexpress.com/w/wholesale-M12-10.9-bolt.html) |
| 12 mm | Birch plywood sheet | 60 | Stock | Battery box (six panels) and electronics shelf. | timber yard |
| 2 | Castor wheels, Ø75 | 35 | Stock | Anti-tip. `cad/walle_frame.scad`. Mounting steel you already have. | [search](https://www.aliexpress.com/w/wholesale-caster-wheel-75mm.html) |

### Sealing the battery box — small money, and it decides whether the packs survive

The box hangs inboard of the belts, which throw sand at it. `06-why-the-batteries-are-low.md`
has the reasoning. Cheap parts, so buy spares of all of them.

| Qty | Part | Cost, USD | Lead | Notes | Buy from |
|---|---|---|---|---|---|
| 5 m | Closed-cell foam tape, 3 mm, self-adhesive | 10 | Stock | The lid gasket. EPDM, not open-cell — open-cell soaks up water and holds grit. | [search](https://www.aliexpress.com/w/wholesale-EPDM-foam-tape-3mm.html) |
| 1 sheet | Closed-cell foam, 8 mm | 10 | Stock | The pad on top of the packs. Clamps them down and takes the vibration. | [search](https://www.aliexpress.com/w/wholesale-closed-cell-foam-sheet-8mm.html) |
| 8 | Silicone blanking plug, Ø30 | 10 | Stock | 4 needed, 4 spare. **These plug the M12 spanner holes.** Without them the rest of the sealing is pointless. Check them every morning. | [search](https://www.aliexpress.com/w/wholesale-silicone-blanking-plug-30mm.html) |
| 2 | Screw-in membrane vent, M12, IP67 (Gore type or equivalent) | 16 | Stock | 1 needed, 1 spare. Goes in the **lid**. A sealed box breathes with the day/night temperature swing; this is the clean path so it does not pull dust through a leak. | [search](https://www.aliexpress.com/w/wholesale-M12-waterproof-breather-vent.html) |
| 4 | Cable gland, M16, IP68 | 10 | Stock | Charge leads and pack sense wiring out of the box. Not a drilled hole. | [search](https://www.aliexpress.com/w/wholesale-cable-gland-M16-IP68.html) |
| 16 | M5 bolts, nuts and washers, 25 mm | 8 | Stock | 12 for the lid at 110 mm pitch, plus spares. A gasket only seals where it is squeezed. | [search](https://www.aliexpress.com/w/wholesale-M5-bolt-nut-washer-set.html) |
| 3 | **XT60** charge connector with a dust cap, body-mounted | 18 | Stock | One per traction pack, plus one for the electronics battery. Everything charges **in place** and nothing comes out in the field. XT60 is right here and wrong for the main disconnect: charging is a few amps, it is plugged in rarely, and there is no capacitor bank to spark into. **Label all three.** Two are 48 V and one is 12 V, and the connectors are identical. | [search](https://www.aliexpress.com/w/wholesale-XT60-panel-mount-connector.html) |

### The contactor is the long pole

Two DC-rated contactors is the single biggest line in this section and the one most likely to
arrive late. Order them in phase 0 even though they are not needed until phase 2.

---

## 3. Compute and sensors — phase 2, and not before

Do not buy these early. They sit in a drawer losing value while you do metalwork, and a newer
version may appear.

| Qty | Part | Est. | Lead | Notes | Buy from — **read §9 first** |
|---|---|---|---|---|---|
| 1 | Jetson Orin Nano 8 GB developer kit | 250 | Stock | Takes 9–19 V DC in, so it runs off the 12 V rail directly. | **§9 — not here** |
| 1 | NVMe SSD, 500 GB | 40 | Stock | Do not run it from an SD card. They wear out and then corrupt, in the field. | [search](https://www.aliexpress.com/w/wholesale-NVMe-SSD-500GB.html) |
| 1 | Active cooler and a filtered intake fan | 30 | Stock | It throttles without one, and Midburn is hot. | [search](https://www.aliexpress.com/w/wholesale-Jetson-Orin-Nano-cooling-fan.html) |
| 1 | OAK-D Lite depth camera | 150 | Stock | Runs the person-detection model on its own chip, so the Jetson gets a ready-made list. | **§9 — not here** |
| 1 | RPLIDAR A1M8, 12 m 2D scanner | 100 | Stock | Enough for obstacle detection. The A2 is 2.5× the price for range you do not need. | [search](https://www.aliexpress.com/w/wholesale-RPLIDAR-A1M8.html) |
| 6 | VL53L1X time-of-flight distance sensor | 24 | Stock | The bumper ring. These wire to the **Spine**, not the Brain. | [search](https://www.aliexpress.com/w/wholesale-VL53L1X-module.html) |
| 1 | I2C multiplexer (TCA9548A) | 3 | Stock | Six VL53L1X boards share one I2C address. You need this or you need to sequence their XSHUT pins. | [search](https://www.aliexpress.com/w/wholesale-TCA9548A-I2C-multiplexer.html) |
| 1 | BNO085 IMU with fused heading | 30 | Stock | Gives a compass heading and detects pitch, which matters on a tippy robot. | [search](https://www.aliexpress.com/w/wholesale-BNO085-IMU.html) |
| 1 | u-blox NEO-M9N GPS module | 50 | Stock | Midburn is a flat featureless plain. GPS, not SLAM. | [search](https://www.aliexpress.com/w/wholesale-NEO-M9N-GPS-module.html) |
| 1 | USB microphone | 20 | Stock | For speech. Get one with some directionality. | [search](https://www.aliexpress.com/w/wholesale-USB-microphone-directional.html) |

---

## 4. Face and sound — phase 4

| Qty | Part | Est. | Lead | Notes | Buy from — **read §9 first** |
|---|---|---|---|---|---|
| 2 | ESP32-S3 development board | 24 | Stock | Two, one per eye. See the warning below. | [search](https://www.aliexpress.com/w/wholesale-ESP32-S3-development-board.html) |
| 2 | 2.1 inch round LCD, 480×480, QSPI (Waveshare) | 60 | Stock | 53 mm active area. The barrel in the CAD model is built around this size. | [search](https://www.aliexpress.com/w/wholesale-2.1-inch-round-LCD-480x480-QSPI.html) **§9** |
| 2 | Clear acrylic dome or lens, Ø99 | 20 | Stock | Dust seal and the glassy look. `cad/walle_frame.scad`. | [search](https://www.aliexpress.com/w/wholesale-acrylic-dome-100mm.html) |
| — | ~~Metal-gear servos~~ | — | — | **Deleted 2026-09-17. The head is rigid — no pan, no nod, no tilt.** Saves 60 dollars, 4 gear trains that sand would have eaten, and the whole servo power branch. | deleted |
| 1 | Camera mount hardware and a plywood hood for the lens | 15 | Stock | The OAK-D goes **under** the eye barrels, not between them. See the head note below. | local |
| 1 | TPA3255 class-D amplifier board | 20 | Stock | Runs on the 32 V supply, not the pack. `04-power-and-wiring.md` section 4. | [search](https://www.aliexpress.com/w/wholesale-TPA3255-amplifier-board.html) |
| 2 | Full-range or coaxial speaker, 6.5 inch, **4 Ω** | 60 | Stock | One per amplifier channel. Ø165 cutout, Ø190 rim, 50 mm deep — the chest panel is drilled for exactly that. **Check the mounting depth on the one you buy**; over 200 mm and the enclosure has to grow. | [search](https://www.aliexpress.com/w/wholesale-6.5-inch-speaker-4-ohm.html) |
| 2 | Speaker grille, Ø190, steel | 20 | Stock | Not optional. A crowd will push a finger through an open cone. | [search](https://www.aliexpress.com/w/wholesale-speaker-grille-190mm.html) |
| — | 12 mm ply for the two enclosures, plus bracing | 25 | Stock | About 0.6 m². Sizes echoed by `cad/walle_frame.scad`. | timber yard |
| — | Gasket tape, acoustic wadding, M5 bolts for the drivers and the boxes | 20 | Stock | The boxes **bolt** to the chest panel — they shade 54 % of the shelf and have to lift out. | [search](https://www.aliexpress.com/w/wholesale-acoustic-wadding-speaker.html) |
| — | LED strip, drivers, eye illumination | 120 | Stock | | [search](https://www.aliexpress.com/w/wholesale-WS2812B-LED-strip.html) |

### The speakers are not just an audio decision

They are 7.3 kg, they sit 584 mm up, and both of them are forward of centre. That combination
took **1.5° off the forward tipping margin** on its own, leaving 7.0° between going over and
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

> This table is a **snapshot from the day that decision was made**, kept because the
> difference between the two columns is the argument. Several decisions have moved the robot
> since, in both directions — the rigid head and the shorter speaker boxes took mass off, the
> electronics battery put some back. For today's numbers run `cad/walle_frame.scad`, do not
> read the right-hand column.

| Qty | Part | Est. | Lead | Notes | Buy from — **read §9 first** |
|---|---|---|---|---|---|
| — | 12 mm birch plywood, about 1.7 m² | 130 | Stock | Floor, four walls, and the lid. Sizes come straight out of `cad/walle_frame.scad`. | timber yard |
| — | 12 mm plywood for the eye rings, about 0.3 m² | 25 | Stock | 24 discs of Ø105. See the head note below. | timber yard |
| — | Glue, screws, corner blocks | 30 | Stock | A plywood box is only as good as its corners. | local |
| — | Hinges, catches, gas strut for the lid | 90 | Stock | The body top is the access lid for the shelf. Aluminium angle no longer needed. | [search](https://www.aliexpress.com/w/wholesale-gas-strut-lid-support.html) |
| — | Exterior sealer or varnish | 40 | Stock | Not for looks. Plywood in the Negev sees big day-to-night humidity swings and delaminates if left bare. | local |
| — | Steel for the neck and the head frame | — | — | **You already have the steel.** | owned |

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
| 1 — de-risking | now | 252 |
| 1b — throttle interface for the scooter controllers | now | 60 |
| 2 — frame and drive, including sealing the box and the electronics battery | 1 | 681 |
| 3 — compute and sensors | 2 | 697 |
| 4 — face and sound | 4 | 384 |
| 5 — body and head, plywood | 5 | 315 |
| Tools and consumables not listed above | throughout | 250 |
| Spares kit (`00-plan.md` phase 6) | 6 | 300 |
| **Total** | | **≈ 2,939** |

Every figure above is now **summed from its own table** rather than typed in.
Doing that turned up three that had drifted: section 1 said 350 when it summed
to 552, section 3 said 740 against 738, and section 4 said 400 when it actually
sums to 459. The total was understated in one place and overstated in another.

### How it got from 4,200 to 2,898

| Change | Saving |
|---|---|
| The body is plywood, not foam and fibreglass | **445** |
| You already own the frame and head steel | **335** |
| Use the scooter controllers instead of two VESCs | **180**, after 76 spent on the interface |
| The head is rigid, so four servos are gone | **60**, less 15 for the camera mount |
| Correcting section 4, which was understated | **−59** |
| Checking real AliExpress prices, section 9 | **161** |
| Dropping the two CAN transceivers nothing uses yet | **10**, less 6 for the real Teensy price |
| The electronics battery, decision D8 | **−41**: 105 for the battery, its charger and its fuse, plus 6 for a third charge connector, less the 70 the isolated converter cost |
| A real clamp-meter price instead of a guess | **35** |
| A real bench-supply price instead of a guess | **21** |
| The shock bolt retrofit, fixed by the owner | **50** |
| Correcting the I2C multiplexer, which I had mis-set to 24 | **21** |

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
2. **The GPS and IMU.** 80 dollars. Only needed for `ASSIST` mode, which `00-plan.md`
   already lists as the first thing to drop.
3. **The LED eye illumination**, 120 dollars in section 4. The screens are the eyes; the
   strip is decoration on top of decoration.

The body is no longer on this list, because it is already down to 315.

The four places **not** to cut: the DC contactors, the crimp tool, the current-limited bench
supply, and the **hardware throttle watchdog** in section 1b.

---

## 9. Buying it on AliExpress

**Read this before using the `search` links.** Added 2026-09-17.

### Why these are search links and not product links

Product links die. The listings that came up while checking prices for this
section had customer reviews dated **2019 and 2020**, so those pages are
probably already gone. You will be buying from this document over six months.
A search link still works in six months; a product link does not.

There is also no single "real price" on AliExpress. The same MCP4725 DAC came
back at **$0.99, $1.38, $1.75, $2.33, $4.57 and $6.37** from different sellers
on the same day. So what is below is a band, not a quote.

### Prices that were checked, and were wrong in this document

| Part | Was | Checked | Now |
|---|---|---|---|
| DC contactor, 2 off | 200 | $39 each from an EV distributor, $11 on AliExpress | **80** |
| VL53L1X, 6 off | 60 | $2.73 – $5.11 each | **24** |
| TPA3255 amplifier board | 40 | $18.79 – $19.82 for the DC19-50V 300+300 W board | **20** |
| MCP4725, 2 off | 8 | $0.99 – $2.33 each | **4** |
| RC transmitter and receiver | 180 | ER8 receiver $35, R88 $20, FlySky sets from $21 | **120** |
| 6.5 inch speakers, 2 off | 70 | $30.69 each, 4 Ω | **60** |
| ACS758 100 A, 2 off | 20 | $7.46 – $9.92 each | **18** |
| I2C level shifter, opto-isolators, watchdog, TCA9548A | 29 | all under $3 | **16** |

That is **161 dollars** off the total, and the contactor is most of it. Nothing
was checked and found to be *under*-estimated, which is worth knowing: the rest
of the list is probably a little high too.

### Two traps that cost more than the savings

**1. The cheap 2.1 inch round screens are the wrong interface.** Searching that
size returns panels at $7.64 and $9.98, against about $30 for the one this robot
needs. They are not the same part. The cheap ones are **40-pin RGB or MIPI**,
which needs a Raspberry Pi class host with a parallel display controller. The
ESP32-S3 in `01-architecture.md` drives **QSPI**. This document already warns
about that trap for the bigger 3.4 and 4 inch panels; it applies just as much
here. **Check the interface in the listing, not the diagonal.** If it says RGB,
MIPI, or 40-pin, it will not work with the Face board.

**2. There is no isolated 48→12 V converter on AliExpress — and this trap is what
killed the part.** Every result for that search is a **non-isolated** buck module,
from $1.09 to $36.84. Section 3 of `04-power-and-wiring.md` required isolation,
because a non-isolated converter shares its negative with the pack, which puts
motor return current through the Jetson's ground reference. The symptoms are USB
devices dropping out, the camera disconnecting, and random reboots under
acceleration — all horrible to diagnose. The only real answer was a Mean Well
SD-100C-12 from a distributor, at 70 dollars.

**Resolved 2026-09-19 by decision D8: the converter is deleted.** The electronics
run from their own 12 V battery, so there is no 48 V left to step down and no
isolation to get wrong. This entry stays here as the reason, not as a warning you
still have to act on. If you ever reverse D8, reverse this too — **do not** put a
$1.09 non-isolated module on the Jetson's rail.

### The five parts to buy from a real distributor

For these, a counterfeit does not waste a few dollars, it costs the robot or
starts a fire. They are marked **§9 — not here** in the tables above.

| Part | Why not AliExpress |
|---|---|
| 60 A, 15 A and 10 A fuses | Fake current ratings are common. A fuse that does not open is not a fuse, and it is the only thing between a shorted battery and the wiring. The 15 A one guards the electronics battery, which will push hundreds of amps into a short just like the traction packs will. |
| DC contactor | It is part of the emergency stop chain. One listing checked at $10.99 has a buyer review reporting **coil inrush of 167 W against a 4.4 W specification** — see the warning below, because that number matters beyond the price. |
| Latching mushroom E-stop | Same chain, same reasoning. |
| ~~Isolated 48→12 V converter~~ | **Deleted by D8.** The 15 A fuse at the electronics battery takes its place on this list, for the same reason as the other fuses. |
| Jetson Orin Nano | Relabelled and grey-market modules, often a different memory size than advertised. |
| OAK-D Lite | Depth cameras there are usually grey imports with no warranty and no firmware support. Buy from Luxonis. |

### A contactor warning that is not about money

The buyer review on the cheap contactor reports **167 W of coil inrush where the
datasheet claims 4.4 W**. Check this on whatever contactor you buy, because two
numbers in this project depend on it:

1. `04-power-and-wiring.md` section 3 budgets **6 W for both coils** on the 12 V
   rail, continuous and peak. If the real inrush is anywhere near what that
   review describes, the 100 W converter is sized for the wrong load and will
   brown out the Jetson every time a contactor pulls in.
2. That same table listed the coils on the **12 V rail**, while section 2 here specified a
   **48 V coil**. **RESOLVED 2026-09-17: the coil is 48 V and runs off pack A**, through its
   own 5 A slow-blow fuse and the E-stop chain. The coils are gone from the 12 V rail budget,
   which dropped from 44 W to 38 W continuous. Two good consequences: the inrush now comes
   out of a 20 Ah battery instead of browning out the Jetson, and pack A dying drops **both**
   contactors, so the robot cannot pivot on its surviving track. See
   `04-power-and-wiring.md` section 3.

Measure the inrush with the bench supply's current limit before it is wired into
anything.

### Things not to buy there at all

Plywood, glue, varnish, hinges, timber and the steel are marked **timber yard**,
**local** or **owned**. Shipping a plywood sheet from China makes no sense, and
you already have the steel.

---

## 8. Spares to have at the festival

Failures in the desert are dust, heat and vibration, in that order. Carry the parts that
those break.

| Qty | Part | Why |
|---|---|---|
| 1 | 48 V controller with a reverse line, 50 | You own exactly two and need exactly two. One dying kills one whole track, and the robot cannot turn on one track. |
| 2 | MCP4725 DAC breakout | 4 dollars, and it is the single point of failure for a whole side's throttle. |
| 1 | 12→5 V converter | Loses the Spine and the Face together. |
| 1 | ESP32-S3 board | An eye. |
| — | Every fuse value, several of each | Obvious, and always forgotten. |
| — | Crimp lugs, heatshrink, wire, the crimp tool | You will be making cables at night. |
| 1 | Ø53 round LCD panel | The eyes are the whole face now, and there is no servo to blame. |
| — | Compressed air, brushes, filter material | The actual most useful items in the box. |
