# 01 — Architecture

Three boards. The rules that decide who may move the robot.

## 1. Why three boards

| Job | Must react in | If late |
|---|---|---|
| Stop the motors | 1 ms | Someone gets hurt |
| Animate the eyes | 30 ms | Face looks broken |
| Read a camera frame | 100 ms | Nobody notices |
| Pick a line of speech | 3 s | Fine |

Linux can pause for seconds. A 200 kg machine must not. Motor commands live on a board with **no OS**.

## 2. Layout

```
RADIO ──2.4 GHz──► RC RECEIVER ──iBus──► SPINE (Teensy 4.0)
                                         ▲
LiDAR, ELP cam, GPS, mic ──► BRAIN (XPS) ┤ USB 20 Hz heartbeat
                         local, no net   │ HDMI ──────────► CHEST 7 inch LCD (portrait)
                         USB serial ─────► FACE (ESP32-S3 × 2, screens, no servos)

ToF ring ──► SPINE ──I2C──► 2× MCP4725 DAC ──opto──► 2× scooter controller ──► hub motors
E-stop  ──► SPINE           hardware watchdog shorts both throttles if kicks stop
```

- Radio and bumpers wire into the **Spine**, not the Brain.
- Brain crash costs eyes and sound. Driver keeps the sticks.

## 3. Spine loop (1 kHz)

Higher number loses. Every pass rebuilds motor commands from scratch.

| # | Check | If it fails |
|---|---|---|
| 1 | E-stop closed? | Motors dead. Physical. No override |
| 2 | Arm switch ON? | Send zero |
| 3 | Radio frame in last 100 ms? | Ramp to zero |
| 4 | Each track turning as commanded? (hall edges) | Ramp **both** to zero |
| 5 | Both pack voltages above the floor? (dividers) | Ramp **both** to zero |
| 6 | Mode switch | MANUAL = sticks. ASSIST = Brain may request |
| 7 | ASSIST only: Brain heartbeat in last 100 ms? | Ramp to zero, fall to MANUAL |
| 8 | Bumper close in the direction of travel? | Scale down or to zero. Veto only |
| 9 | Motor too hot? (hub thermistor) | Scale both down |
| 10 | Slew limit | Smooth ramp |
| 11 | Scale each side by its own pack voltage | Straight drive as packs drift |
| 12 | Write DACs. Kick watchdog | Stop kicking if a DAC write fails |

Every failure stops the robot. Nothing speeds it up or ignores the driver.

Controllers report **nothing**. So:

- Rule 4 = hall edges. Commanded to move, halls still: track is dead.
- Rules 5 and 11 = resistor divider per pack.
- Rule 9 = motor’s own thermistor.

A scooter controller has **no command timeout**. A DAC **holds its last voltage**. If the Teensy dies while packs are alive, only the **hardware watchdog** (NC relay shorts throttle to ground) stops the robot. Safety log tests 15 and 16.

## 3b. One pack per pod

Positives never meet. Negatives bonded at **one** point, including the 12 V pack negative. Do not fuse the bond.

**Trap 1 — crooked drive.** Same duty on 50 V vs 44 V is a pull. Rule 11 scales by pack voltage.

**Trap 2 — one dead side pivots the robot.** BMS cut is the usual cause. Rules 4 and 5 stop **both** tracks.

**Trap 3 — floating ground.** Far-pack readings look real and are wrong. One bond, three negatives, two positives that never meet. Bond sized for 40 A. Not fused.

**D8.** Electronics: 12 V 20 Ah, 181 × 167 × 77 mm, on its side, lower deck. Traction packs equal (~17.5 Ah). Drive ~5.6 h. Electronics ~12 h.

| What dies | What stops the robot |
|---|---|
| Pack A | Coils lose 48 V. Both contactors open. Copper |
| 12 V pack | Teensy dies. Arm MOSFET opens the coil chain |
| Pack B | Only rule 4 (halls). Contactor B stays closed with no power behind it |
| Teensy crash, packs alive | Watchdog only |

Coils stay on pack A. Amp stays on 48→32 V off pack A. Do not move either onto 12 V.

## 4. Brain heartbeat

Brain sends speed, turn, and a counter every 50 ms.

- Last message < 100 ms: continue.
- Else: Brain dead. Ramp to zero in 0.5 s (do not slam — 231 mm footprint can tip). Ignore Brain until messages return for 1 s.

In MANUAL a dead Brain does not stop the robot. Sticks go straight into the Spine.

## 5. What each board runs

**Brain — XPS 15 9510, Python, no internet.** Closed on the upper tray (L26). PD pack 65 W+ on the lower deck.

- Occupancy from LiDAR (geometry, not AI).
- ELP-USB1080P03-KLC1100, 86°. YuNet faces on **CPU**. Mouth motion. Speaker-lock. Distance from face size. ToF ring for close range.
- Chest 7 inch HDMI, portrait, between the speakers. Status and captions. Not motors.
- Personality picks `idle` · `look_at` · `greet` · `retreat` · `play_sound` · `nudge_forward`. Optional local LLM (3B, 4-bit) only from that list. **Never a motor number.**
- Log temperatures, voltages, vetoes.

**Spine — Teensy 4.0, C++, no OS.** Section 3 only. Reads thermistors, dividers, ACS758, halls. Forwards telemetry.

**Face — ESP32-S3 × 2.** `GAZE` / `MOOD` → pupils and blinks. No servos.

### Look = drive

Head is rigid. Camera FOV **is** robot FOV: **86°** (±43°). Blind until the body turns. Full own-path width from **363 mm** ahead. Closer: ToF ring.

A look-turn is a normal drive command. Same slew, current, tilt, bumper, watchdog, plus:

| | Rule |
|---|---|
| L1 | Brain requests a **heading offset with a timeout**, never raw motors |
| L2 | Look-turn rate is a fraction of drive turn |
| L3 | Any stick input cancels the look. RC ch 6 = look-turn enable |

Pivot on sand is the peak current. Test ACS758 on a turn in place, not a straight line. Prefer a gentle arc.

## 6. Modes

- **MANUAL** — sticks. Bumper and temp still apply. Brain is cosmetic. Use this in a crowd.
- **ASSIST** — Brain may request a slow turn. Stick above deadband wins for 2 s.

Build MANUAL first.

## 7. Build order

| Stage | Test |
|---|---|
| 1 | One motor, hand throttle, no Teensy. Spins |
| 2 | Teensy → one DAC. Number moves the motor |
| 3 | Radio. Stick moves it. TX off stops it |
| 4 | **Watchdog before the second track.** Kill Teensy power: motor stops |
| 5 | Second controller, mixing, on blocks |
| 6 | E-stop and arm. Cause every §3 failure |
| 7 | First sand drive, no body, tethered E-stop. Watch current on a pivot |
| 8 | Bumpers. Refuses a cardboard box |
| 9 | Face, Brain idle. Eyes follow a hand |
| 10 | Camera + personality. Pupils follow a person. Head still |
| 11 | Look-turns on ch 6. Stick cancels |
| 12 | Body and sound |
