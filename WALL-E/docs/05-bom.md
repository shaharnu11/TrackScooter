# 05 — Bill of materials

Buy in phase order. Est. is **USD**. You pay **shekels**. Compare delivered prices. Israel VAT ~$75 per import — several small orders can beat one big one.

- Stock = ships this week. Long = 4–8 weeks. Order long items first.
- **§9 not here:** fuses, DC contactors, mushroom E-stop. Fake ratings fire.
- Search links last longer than product links. Read §9 before clicking.

---

## 1. Buy now — bench, no frame

~ $422 with 1b. Controllers already owned (reverse line confirmed). 1b buys back what they do not report.

| Qty | Part | Est. | Lead | Notes | Buy from — **read §9 first** |
|---|---|---|---|---|---|
| 1 | Teensy **4.0** | 38 | Stock | Spine. **Not 5 V tolerant** — needs the §1b level shifter. | [AliExpress ₪114.08](https://he.aliexpress.com/item/1005009258422669.html) |
| 1 | RC transmitter and receiver set, 8+ channels | 120 | Stock | See section 6 for what the channels are for. | [search](https://www.aliexpress.com/w/wholesale-8-channel-RC-transmitter-receiver.html) |
| 1 | Multimeter with a clamp for **DC** current | 25 | Stock | The clamp matters. You cannot break into a 40 A circuit to measure it. **Check the listing says DC amps, not only AC.** Most cheap clamp meters are AC-only and will read 0 A on a battery wire. Needs 100 A DC or more. You use it to find the controllers' real current limit, to calibrate the two ACS758 sensors, and to measure contactor coil inrush — see the 167 W warning in §9. | [AliExpress ₪77.35](https://he.aliexpress.com/item/1005002037433118.html) |
| 1 | Bench power supply, 60 V 5 A, adjustable current limit | 69 | **3 weeks** | The current limit turns a wiring mistake into a beep instead of a fire. Borrow one if you can. Priced from a Jesverty 60V05A listing at ₪207.92, about 69 USD, or 61 with the on-page coupon. Two checks before paying: keep the **220 V EU plug** variant selected, and confirm the description says **CC / constant current** — you need the supply to drop its voltage automatically at the limit, not just display the current. 60 V is the minimum useful figure because a full 48 V pack sits at about 54.6 V. | [search: Jesverty 60V05A](https://www.aliexpress.com/w/wholesale-Jesverty-DC-lab-power-supply-60V-5A.html) — Jesverty Official Store, variant `60V05A-Model V`, 220 V EU plug |

Day one: one motor, own controller, hand throttle, on blocks. No code.

---

## 1b. Teensy → scooter controllers — ~$60

Throttle is +5 V, GND, signal (~0.8 V rest, ~4.2 V full). **Measure yours.** DAC fakes it.

| Qty | Part | Est. | Lead | Notes | Buy from — **read §9 first** |
|---|---|---|---|---|---|
| 2 | MCP4725 12-bit I2C DAC breakout | 4 | Stock | One per controller. Makes the throttle voltage. Two share one I2C bus at addresses 0x62 and 0x63. | [search](https://www.aliexpress.com/w/wholesale-MCP4725-DAC-module.html) |
| 1 | I2C level shifter, 4 channel (BSS138 or TXS0102) | 2 | Stock | The DAC has to run at 5 V to reach full throttle, and **the Teensy is not 5 V tolerant.** Without this you damage its pins. | [search](https://www.aliexpress.com/w/wholesale-BSS138-I2C-level-shifter.html) |
| 4 | Opto-isolator, PC817, plus resistors | 3 | Stock | Two per controller: one pulls the **reverse** line, one pulls the **e-brake** line. Isolated, so a controller fault cannot travel back into the Teensy. | [search](https://www.aliexpress.com/w/wholesale-PC817-optocoupler.html) |
| 2 | Watchdog: TLC555 or TPS3823, plus a signal relay with normally-closed contacts | 8 | Stock | **Not optional.** See the warning below. | [search](https://www.aliexpress.com/w/wholesale-TLC555-timer-IC.html) |
| 2 | ACS758 100 A bidirectional hall current sensor | 18 | Stock | Gives the Teensy a current reading the controllers do not report. One per pack lead. | [search](https://www.aliexpress.com/w/wholesale-ACS758-100A.html) |
| — | Resistors for the motor thermistor divider | 2 | Stock | Reads the hub motor's **own** temperature sensor straight into the Teensy. This is the defence against risk R5, and it replaces arbitration rule 9's data source. | [search](https://www.aliexpress.com/w/wholesale-metal-film-resistor-kit.html) |
| — | Resistors for two pack voltage dividers | 2 | Stock | Arbitration rules 5 and 11 need pack voltage, and the controllers do not report it, so the Teensy measures it. Mind the ground reference. | [search](https://www.aliexpress.com/w/wholesale-metal-film-resistor-kit.html) |
| — | Wiring to bring both motors' hall sensors to the Teensy | 6 | Stock | Arbitration rule 4 asks "is each track alive?" and the controllers do not answer, so the Teensy counts hall edges: commanded to move, halls not changing, track is dead. | [search](https://www.aliexpress.com/w/wholesale-shielded-cable-4-core.html) |
| — | Shielded 4-core signal cable and connectors | 15 | Stock | Throttle lines run beside motor phase wires. Shield them or the robot twitches. | [search](https://www.aliexpress.com/w/wholesale-shielded-cable-4-core.html) |

- No PWM “analogue”. DAC only.
- DAC holds last voltage. Hardware watchdog (NC relay) shorts throttle when kicks stop.
- E-stop also into controller **e-brake**.
- Bought back: thermistor, ACS758. Not bought: FOC, tunable limits, full-speed reverse.
- If the controller has cruise that cannot turn off, it does not go on this robot.

---

## 2. Frame and drive — phase 1

| Qty | Part | Est. | Lead | Notes | Buy from — **read §9 first** |
|---|---|---|---|---|---|
| 2 | DC contactor, **48 V coil** (confirmed 2026-09-17), 80 A+ **DC rated** | 80 | Long | Albright SW-series or Gigavac. **An AC-rated relay will weld shut.** `04-power-and-wiring.md` section 5. | **§9 — not here** |
| 2 | Fuse, 60 A, and holders | 25 | Stock | Class T or ANL. One per pack. | **§9 — not here** |
| 3 | Fuse, 10 A, and holders | 15 | Stock | Amplifier 48→32 V supply, plus two spares. | **§9 — not here** |
| 3 | Fuse, 5 A **slow-blow**, and holders | 6 | Stock | The contactor coil circuit. Slow-blow because it is sized for the coil inrush, not the 0.3 A holding current. See §9. | **§9 — not here** |
| 10 m | 10 AWG silicone wire, red and black | 40 | Stock | Silicone, not PVC. It has to stay flexible when hot. | [search](https://www.aliexpress.com/w/wholesale-10AWG-silicone-wire.html) |
| 10 m | 12 AWG silicone wire | 30 | Stock | Motor phases. | [search](https://www.aliexpress.com/w/wholesale-12AWG-silicone-wire.html) |
| 1 set | Ring lugs, heatshrink, and a proper crimp tool | 70 | Stock | The tool is not optional. See `04-power-and-wiring.md` section 8. | [search](https://www.aliexpress.com/w/wholesale-hydraulic-crimping-tool-cable-lug.html) |
| 4 | **XT90-S anti-spark** connector pairs | 20 | Stock | The main disconnect on each pack, plus two spares. **Was Anderson SB50.** The "-S" is not optional: it is the built-in resistor that pre-charges the controller capacitors, so the contacts stop sparking every time you plug in. **Put the SOCKET half on the battery** — the disconnect sits ahead of the fuses, so exposed pins on the pack side would be an unfused short waiting for a dropped spanner. See `04-power-and-wiring.md` §5. | [search](https://www.aliexpress.com/w/wholesale-XT90-S-anti-spark-connector.html) |
| 8 | Silicone caps for the XT90 halves | 6 | Stock | Dust cover and idiot guard in one. Anderson housings were genderless and recessed; XT is not, so this replaces a safety property we gave up. | [search](https://www.aliexpress.com/w/wholesale-XT90-connector-silicone-cap.html) |
| 1 | Latching mushroom emergency stop, red, IP65 | 25 | Stock | Normally-closed contact. | **§9 — not here** |
| 1 | **12 V 20 Ah LiFePO4 battery** — the electronics supply | 75 | Stock | Owner decision D8. **Different case from the 48 V packs:** this one is **181 × 167 × 77 mm**, those are **400 × 110 × 80 mm** and live in the frame box. 240 Wh against a 20 W rail is 12 hours. This rail is the Teensy, the Face, the fans, and the powered USB hub. **The XPS is not on it.** **Fit LYING ON ITS SIDE on the lower deck**, on a strap, not glue. Upright it is 167 mm tall and it lifts the laptop tray — `cad/walle_frame.scad` guards this. Unplug the XT60 and lift it out after the laptop tray comes off (L17). | [search](https://www.aliexpress.com/w/wholesale-12V-20Ah-LiFePO4-battery.html) |
| 1 | LiFePO4 charger, 14.6 V 5 A | 25 | Stock | For the battery above. **A lead-acid charger is not a LiFePO4 charger** — the float voltage is wrong and it will sit there cooking the pack. | [search](https://www.aliexpress.com/w/wholesale-14.6V-5A-LiFePO4-charger.html) |
| 1 | Fuse, 15 A, and holder, at the battery terminal | 5 | Stock | A 20 Ah LiFePO4 will push hundreds of amps into a short and its BMS is not a fuse. Mount it **at the terminal**, not at the far end of the run. | **§9 — not here** |
| 1 | Buck converter, 48→32 V, 150 W, non-isolated | 25 | Stock | The amplifier's supply only. `04-power-and-wiring.md` section 4. | [search](https://www.aliexpress.com/w/wholesale-DC-DC-buck-converter-48V-32V-150W.html) |
| 1 | Buck converter, 12→5 V, 5 A | 12 | Stock | Teensy and ESP32 only. | [search](https://www.aliexpress.com/w/wholesale-DC-DC-buck-converter-12V-5V-5A.html) |
| — | Capacitors, 4700 µF 25 V, and TVS diodes | 20 | Stock | Rail buffer and controller input protection. | [search](https://www.aliexpress.com/w/wholesale-capacitor-4700uF-25V.html) |
| — | Steel box tube 60×30×3 and 30×30, plate | — | — | **You already have the steel.** Cut list is echoed by `cad/walle_frame.scad`: 2 × 550 rails, 2 × 263 cross members, 1626 mm of 60×30 in total. | owned |
| 2 | **Packer, 60×6 flat bar, 60 mm long, 2 holes Ø13** | 5 | Stock | One per side. Fills the 6 mm step between the carrier face the rail sits on and the green plate the M12s thread into. **Without it the bolts crush the rail wall into the gap and the joint has no clamp.** Offcut of the same 60×6 as the plates. | Offcut / steel stockist |
| — | M12 10.9 bolts, and the Ø25/Ø13×30 sleeves to weld into the rails | 25 | Stock | The sleeve is what stops an M12 crushing a 3 mm box wall. Not optional. | [search](https://www.aliexpress.com/w/wholesale-M12-10.9-bolt.html) |
| 12 mm | Birch plywood sheet | 60 | Stock | Battery box (six panels), electronics shelf, and the lift-out laptop tray (315 × 360). | timber yard |
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
| 4 | Cable gland, M16, IP68 | 10 | Stock | Charge leads and pack sense wiring out of the box. Not a drilled hole. **The gland holds a jumper, not the pack.** Each traction pack unplugs inside the box (XT90-S plus a charge pigtail) so the pack lifts out. | [search](https://www.aliexpress.com/w/wholesale-cable-gland-M16-IP68.html) |
| 16 | M5 bolts, nuts and washers, 25 mm | 8 | Stock | 12 for the lid at 110 mm pitch, plus spares. A gasket only seals where it is squeezed. | [search](https://www.aliexpress.com/w/wholesale-M5-bolt-nut-washer-set.html) |
| 3 | **XT60** charge connector with a dust cap, body-mounted | 18 | Stock | One per traction pack, plus one for the electronics battery. **Daily charge is in place.** Each pack also has the mating half on the pack itself, so you can unplug and charge it on a bench. XT60 is right here and wrong for the main disconnect. **Label all three.** Two are 48 V and one is 12 V, and the connectors are identical. | [search](https://www.aliexpress.com/w/wholesale-XT60-panel-mount-connector.html) |
| 4 | M8 bolts, body floor into the risers | 8 | Stock | The body lifts off so the 48 V box lid can open. Do not weld the body to the risers. | [search](https://www.aliexpress.com/w/wholesale-M8-bolt.html) |
| 3 | Webbing strap or Velcro, 25 mm | 8 | Stock | One each for the 12 V pack, the PD pack, and a spare. Clamps them to the lower deck. Not glue. | [search](https://www.aliexpress.com/w/wholesale-25mm-webbing-strap.html) |

### The contactor is the long pole

Two DC-rated contactors is the single biggest line in this section and the one most likely to
arrive late. Order them in phase 0 even though they are not needed until phase 2.

---

## 3. Compute and sensors — phase 2, not before

Brain = owned XPS 15 9510 (L25). No internet. Two floors (L26). Camera ordered (L27).

| Qty | Part | Est. | Lead | Notes | Buy from — **read §9 first** |
|---|---|---|---|---|---|
| 1 | Filtered intake fan for the body | 15 | Stock | Air **in**. Positive pressure. | [search](https://www.aliexpress.com/w/wholesale-120mm-12V-fan-filter.html) |
| 1 | Powered USB-C hub, USB 3 | 25 | Stock | The XPS has USB-C only. Webcam, LiDAR, Teensy, both Face boards and the mic share this hub. **Power the hub from the 12 V rail**, not from the laptop. | [search](https://www.aliexpress.com/w/wholesale-powered-USB-C-hub-USB3.html) |
| 1 | USB-C PD power bank, 20 000 mAh, **65 W or more** | 40 | Stock | Feeds the XPS. Check the label says 65 W PD, not 22.5 W. Strap it on the **lower** deck, not on the laptop tray. Keep it off the laptop vents. Pull it if it gets hot. | local / [search](https://www.aliexpress.com/w/wholesale-20000mAh-65W-PD-power-bank.html) |
| 1 | ELP-USB1080P03-KLC1100, metal cube, LC1100 lens | 52 | Ordered 2026-09-23 | **L27.** 1080p 30 fps, SC2210, USB 2.0 UVC, 5 V 180 mA, 3 m cable. **42 × 42 × 36 mm**. LC1100 **86°**. ₪195.65. | owned |
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
| 1 | Camera mount hardware and a plywood hood for the lens | 15 | Stock | The ELP cube goes **under** the eye barrels, not between them. See the head note below. | local |
| 1 | TPA3255 class-D amplifier board | 20 | Stock | Runs on the 32 V supply, not the pack. `04-power-and-wiring.md` section 4. | [search](https://www.aliexpress.com/w/wholesale-TPA3255-amplifier-board.html) |
| 2 | Full-range or coaxial speaker, 6.5 inch, **4 Ω** | 60 | Stock | One per amplifier channel. Ø165 cutout, Ø190 rim, 50 mm deep — the chest panel is drilled for exactly that. **Check the mounting depth on the one you buy**; over 200 mm and the enclosure has to grow. | [search](https://www.aliexpress.com/w/wholesale-6.5-inch-speaker-4-ohm.html) |
| 2 | Speaker grille, Ø190, steel | 20 | Stock | Not optional. A crowd will push a finger through an open cone. | [search](https://www.aliexpress.com/w/wholesale-speaker-grille-190mm.html) |
| 1 | 7 inch HDMI LCD, 800×480, **183 × 107 mm** | 25 | Stock | **L28.** Portrait between the speakers: 107 wide, 183 tall. 16.5 mm to each rim. HDMI from the XPS. Power from the 12 V rail. Acrylic cover. Not the Spine. | [search](https://www.aliexpress.com/w/wholesale-7-inch-HDMI-LCD-800x480.html) |
| — | 12 mm ply for the two enclosures, plus bracing | 25 | Stock | About 0.6 m². Sizes echoed by `cad/walle_frame.scad`. | timber yard |
| — | Gasket tape, acoustic wadding, M5 bolts for the drivers and the boxes | 20 | Stock | The boxes **bolt** to the chest panel — they shade 54 % of the shelf and have to lift out. | [search](https://www.aliexpress.com/w/wholesale-acoustic-wadding-speaker.html) |
| — | LED strip, drivers, eye illumination | 120 | Stock | | [search](https://www.aliexpress.com/w/wholesale-WS2812B-LED-strip.html) |

- Speakers: 6.8 kg at 613 mm, both forward. **6.8°** castor margin. Weigh before adding high/forward mass. Buy on **sensitivity**, not “max watts”.
- Screens: **QSPI 480×480** for the eyes, not RGB/MIPI/40-pin. Chest is a separate **HDMI** 7 inch. Two ESP32-S3, one per eye, one sync wire. Do not use 1.28 inch GC9A01.

---

## 5. Body and head — phase 5

12 mm plywood (L6). Numbers: run `cad/walle_frame.scad`.

| Qty | Part | Est. | Lead | Notes | Buy from — **read §9 first** |
|---|---|---|---|---|---|
| — | 12 mm birch plywood, about 1.7 m² | 130 | Stock | Floor, four walls, and the lid. Sizes come straight out of `cad/walle_frame.scad`. | timber yard |
| — | 12 mm plywood for the eye rings, about 0.3 m² | 25 | Stock | 24 discs of Ø105. See the head note below. | timber yard |
| — | Glue, screws, corner blocks | 30 | Stock | A plywood box is only as good as its corners. | local |
| — | Hinges, catches, gas strut for the lid | 90 | Stock | The body top is the access lid for the shelf. Aluminium angle no longer needed. | [search](https://www.aliexpress.com/w/wholesale-gas-strut-lid-support.html) |
| — | Exterior sealer or varnish | 40 | Stock | Not for looks. Plywood in the Negev sees big day-to-night humidity swings and delaminates if left bare. | local |
| — | Steel for the neck and the head frame | — | — | **You already have the steel.** | owned |

### Head

- Barrels: 12 × 12 mm ply rings = 144 mm. 5× Ø59 well (sun shade), 1× Ø53 shoulder, 6× Ø81 cable. Recess stays **60 mm**.
- Camera under the brow. Gap between barrels is 23 mm. Cube is 42 mm. Hood 30 mm. USB gland behind.

---

## 6. Radio channels

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

Set failsafe on every channel to the last column. Test: TX off, on blocks. Wireless E-stop is a **separate** receiver.

---

## 7. Totals

| Section | Phase | Est. |
|---|---|---|
| 1 — de-risking | now | 252 |
| 1b — throttle interface for the scooter controllers | now | 60 |
| 2 — frame and drive, including sealing the box and the electronics battery | 1 | 681 |
| 3 — compute and sensors | 2 | 359 |
| 4 — face and sound | 4 | 409 |
| 5 — body and head, plywood | 5 | 315 |
| Tools and consumables not listed above | throughout | 250 |
| Spares kit (`00-plan.md` phase 6) | 6 | 300 |
| **Total** | | **≈ 2,626** |

Cut first: LiDAR, GPS+IMU, LED strip. Do not cut: DC contactors, crimp tool, current-limited bench supply, hardware watchdog.

---

## 9. AliExpress

Search links last. Same part, six prices. Band, not a quote.

**Not AliExpress:** 60/15/10 A fuses, DC contactor, mushroom E-stop. Fake ratings. Contactor coil inrush can be 167 W — measure on the bench supply. Coils on pack A.

**Not from China:** plywood, glue, varnish, timber, steel (owned).

**Screens:** listing must say **QSPI**. RGB / MIPI / 40-pin will not work with the Face.

**Do not** add a 48→12 off pack A. That undoes D8.

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
| 2 m | Closed-cell foam tape, 3 mm | Reseal the 48 V box lid after a pack comes out. |
| — | Crimp lugs, heatshrink, wire, the crimp tool | You will be making cables at night. |
| 1 | Ø53 round LCD panel | The eyes are the whole face now, and there is no servo to blame. |
| — | Compressed air, brushes, filter material | The actual most useful items in the box. |
