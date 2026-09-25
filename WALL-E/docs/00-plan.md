# 00 — Plan

Read `99-glossary.md` for words. Read `01-architecture.md` for the boards.

## 1. Done looks like

- Tracked robot, 677 mm wide, about 1 m tall. Reads as WALL-E.
- A person drives it with a radio. Not self-driving (L2). No passengers unless D3 says yes.
- Eyes find faces and follow them. Speaker-lock stays on the talker.
- WALL-E sounds. Hebrew talk is optional, offline, on the XPS.
- Full evening on Negev sand, in a crowd, without hurting anyone.

## 2. Status

| Item | Status |
|---|---|
| Pods | Built, Rev 013. Belts on. Do not drill new holes |
| Hub motors + scooter controllers | In hand. Controllers have reverse |
| Frame | Not welded |
| Electronics / body | Nothing built |

**Measure before welding:** 177 mm over the carrier outer faces (green plates 6 mm inboard; packer fills it). `cad/pod_latest.sh` + `cad/check_pod_interface.scad`.

| Fact | Value |
|---|---|
| Mounting width | 177 mm over carriers |
| Ground contact, one pod | 231 × 118 mm |
| Pod | 363 L × 327 H × 177 W |
| Mount band | 60 mm tall, 197–257 mm above ground |
| Travel | +30.7 / −29.2 mm |

## 3. Constraints

- No internet at the event. Every model on the XPS.
- 40 °C sun, fine sand, mostly night. Cooling, covers, lighting.
- Crowds. Safety layer is not optional.
- One person, evenings. Cut scope (section 9) before compressing phases.

## 4. Locked

| # | Decision |
|---|---|
| L1 | Pods side by side, skid steer |
| L2 | Radio drive. Not self-driving |
| L3 | Brain (XPS) / Spine (Teensy 4.0) / Face (ESP32-S3 × 2) |
| L4 | Radio and E-stop wire into the Spine |
| L5 | No SLAM. GPS/compass only if needed |
| L6 | Body: 12 mm plywood |
| L7 | Keep the fitted 18-link belts (231 mm contact). Anti-tip + mass low instead of longer belts |
| L8 | Frame mounts 177 mm over the carriers |
| L9 | One 48 V pack per pod. Positives never meet. Negatives bonded at one point |
| L10 | Electronics on their own 12 V pack (181 × 167 × 77 mm, on its side). XPS not on that rail. **Contactor coils stay on pack A** |
| L11 | Frame 550 mm. All electronics on two floors in the body |
| L12 | Body length follows the pod, not the castors |
| L13 | Two Face boards, one per eye |
| L14 | Amp on its own 48→32 V converter |
| L15 | Traction packs stay in the frame box, not the body |
| L16 | Battery box closed, gasketed, vent in the lid |
| L17 | Every battery unplugs and lifts out. Daily charge still in place (XT60 on the body) |
| L18 | Box floor 150 mm for now. Raise toward 173 mm only after the first sand drive |
| L19 | Two 6.5 inch drivers in the chest, 330 mm apart, 613 mm up. On the chest edges. 140 mm between rims |
| L20 | Each driver: sealed 7.5 L box. Does not fire into the body |
| L21 | Speaker boxes bolt on and lift off |
| L22 | Metal grilles |
| L23 | Head rigid. No pan/nod/tilt. Gaze = pupils. Look left = body turn |
| L24 | Lower shock bolt: closed on the real pods |
| L25 | Brain = owned XPS 15 9510. No Jetson. No cloud |
| L26 | Two floors: XPS + USB hub on a lift-out tray. Rest below. PD pack 65 W+ stays down |
| L27 | Camera = ELP-USB1080P03-KLC1100 (86°, 42 × 42 × 36 mm). No OAK-D. Speaker-lock on CPU |
| L28 | Chest LCD: 7 inch 800×480, 107 × 183 mm, portrait, between the speakers. HDMI from XPS |
| D7 | Use the two scooter controllers already owned |
| D8 | Own 12 V battery for electronics |

## 5. Still open

| # | Question | Decide by |
|---|---|---|
| D3 | Carry a person? | Before Phase 2 |
| D4 | Both pack Ah, both BMS healthy? Traction packs should be **equal** | Before Phase 1 buy |
| D5 | Midburn date and mutant-vehicle rules | This week |
| D6 | Anti-tip: how many, where, 30–40 mm off the ground | Phase 1 |

D6: castors 30–40 mm up so they never load in normal driving. They only catch a pitch. Packs stay low (~190 mm).

## 6. Streams

```
W1 FRAME     measure → SCAD → weld → mount pods
W2 DRIVE     bench motors → DAC → watchdog → radio → E-stop → two motors
W3 SENSE     XPS → camera → personality → eyes. LiDAR later
W4 BODY      last
```

Start W1 and W2 on day one. Do not start with AI.

## 7. Phases

A phase ends when its **exit test** passes.

**Phase 0 — week 1.** Measure pods. Spin both motors on their own controllers. Confirm D4, D5. Order Teensy, DACs, watchdog, radio, clamp meter.

Exit: both motors spin. Pod numbers match the model.

**Phase 1 — weeks 2–7.** Frame in SCAD. Anti-tip mounts. Bench: Teensy + DAC + watchdog + radio + E-stop. Log motor temperature from the first run.

Exit W1: model, zero warnings. Exit W2: stick drives one motor; stop on TX off, E-stop, and unplugged Teensy.

**Phase 2 — weeks 6–12.** Weld. Mount pods at 177 mm. Mixing, slew, anti-tip. Ballast to body weight.

Exit: drive, reverse, turn, spin on sand. Tethered E-stop. Anti-tip catches a pitch.

**Phase 3 — weeks 12–13.** Cause every failure in `01-architecture.md` §3 while driving. Log in `03-safety-log.md`.

Exit: all stops are controlled. No lurch, no turn, no runaway.

Until Phase 3 passes, stay 10 m from people.

**Phase 4 — weeks 10–18.** XPS + PD pack. ELP camera + speaker-lock. Eyes. Rigid head, camera under the brow. Look-turn on RC ch 6. Amp + clips. Chest 7 inch LCD portrait.

Exit: refuses a cardboard box. Pupils follow a person. Head does not move. Out of the 86° view, the body turns slowly and the stick cancels it.

**Phase 5 — weeks 14–24.** Plywood shell, paint, lighting. Eye barrels = 12 × 12 mm rings.

Exit: someone says “WALL-E” without being asked.

**Phase 6 — weeks 24–28.** Covers, heat test, night test, endurance, spares.

Exit: one full evening on sand with only the spares kit.

## 8. Budget (USD, still to buy)

Pods already paid. Total about **$2,060 – $2,590**. Donor packs unusable: add $600–$1,200. Line items: `05-bom.md`.

Buy order:

1. Now: Teensy, 1b parts, radio, meter (~$250).
2. Phase 1: steel, contactor, fuses, cable.
3. Phase 2: LiDAR and sensors. Camera already ordered.
4. Phase 4: screens, amp, chest LCD. No servos.
5. Phase 5: body materials against a finished robot.

Israel VAT ~$75 per import. Several small AliExpress orders can beat one big one.

## 9. If time is short, cut in this order

Must have: drives on sand, Phase 3 stops, looks like WALL-E, eyes follow, sounds.

Cut first:

1. Language model and Hebrew speech
2. ASSIST (keep MANUAL)
3. GPS and compass
4. LiDAR (keep ToF ring)
5. Moving arms
6. Neck motion (already rigid)

## 10. Learn while parts ship

1. Meter: voltage, continuity, current.
2. Crimp and solder. Pull-test the joint.
3. Blink an LED.
4. Print a pot over serial.
5. Pot → MCP4725 → meter (0–3.3 V).
6. Motor + scooter controller + hand throttle. No code.
7. Teensy writes the DAC.
8. Read the radio.
9. Stick drives the motor.
10. Watchdog + arm switch. Pull a cable, motor stops.

Camera: window → one photo → live video → robot.

## 11. Risks

| # | Risk | Defence |
|---|---|---|
| R1 | Someone hurt | Phase 3. E-stop. Keyfob minder. MANUAL in crowds |
| R2 | Tips forward | Anti-tip (D6). Mass low. Ballast test |
| R4 | One BMS cuts out, robot pivots | Rules 4 and 5 stop **both** tracks |
| R5 | Hubs overheat crawling | Read motor thermistors. Teensy backs off throttle |
| R6 | Motor spikes reboot 12 V | Own 12 V pack (D8). XPS on a third supply |
| R6b | Electronics pack dies | Hardware watchdog shorts throttle |
| R6c | Controllers cook in the body | Al plate + filtered air in |
| R6d | XPS cooks or eats sand | Spacers, filter, pull the tray |
| R7 | Frame late | Frame week 2. Electronics on the bench |
| R8 | Sand in bearings / box | Covers. Closed box, plugs, vent (L16) |
| R8d | Charge heat in a sealed box | Log one full charge with the lid on |
| R9 | PLA sprocket in the sun | Check filament. Spare in ASA/nylon |
| R10 | Forward margin eaten | Speakers + two floors leave **6.8°**. Weigh real parts before adding mass |
| R11 | Speakers rattle | Sealed, braced, grille. Bench at full volume |
| R12 | Stuck on electronics | Section 10. Bench early |

## 12. Next

1. D5: date and rules.
2. Measure the pods.
3. Spin both motors on their own controllers.
4. D4: pack Ah and BMS.
5. Order Teensy, 1b, radio.
6. Learn steps 1–5 while parcels ship.
7. Frame in OpenSCAD.
