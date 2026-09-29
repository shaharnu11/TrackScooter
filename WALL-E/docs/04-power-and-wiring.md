# 04 — Power and wiring

Physical version of `01-architecture.md`.

- One 48 V pack per pod. Positives never meet. Negatives + 12 V negative bonded at **one** point. Bond not fused.
- Electronics on their own 12 V pack (D8). **Contactor coils stay on pack A.**

## 1. Tree

```
PACK A 48 V ── XT60 ───┬── 30 A ── CONTACTOR A ── controller L ── left hub
                        ├── 10 A ── 48→24 V ── amp
                        └──  5 A ── E-stop chain ── both contactor coils (48 V)

PACK B 48 V ── XT60 ────── 30 A ── CONTACTOR B ── controller R ── right hub

12 V 20 Ah ── 15 A ── 12 V rail ── 12→5 V ── Teensy, ESP32
              (USB hub, fans). XPS is NOT on this rail.

PACK A (−) ══ 12 AWG bond, not fused ══ PACK B (−) ══ 12 V (−)
```

- E-stop kills **motors only**. Electronics stay up. E-stop is not an isolator. Isolator = XT60 (section 5).
- Both coils on one chain. Cutting one track only is a spin command. Never do that.

## 2. Current (91.6 kg)

| Case | Per side | Use |
|---|---|---|
| Straight, walking | ~2 A | Normal |
| Pivot on sand | ~8 A | Budget here |
| Start / rut | ~25 A | Seconds |
| Absolute | **40 A** | Wire and fuse must survive |

40 A is **measured**, not chosen. Controllers cannot change their peak. Clamp-meter at stall on blocks. Main fuse is **30 A** (10×38 gPV, owner 2026-09-29): 40 A bursts of seconds pass, a minute of stall does not. If the real peak is well above 40 A, rethink wire and fuse together. Teensy current control = back off throttle from ACS758. Slow.

## 3. 12 V rail

| Load | Cont. | Peak |
|---|---|---|
| USB hub | 10 W | 15 W |
| Fans | 5 W | 5 W |
| 12→5 V (Teensy, ESP32) | 5 W | 8 W |
| Chest 7 inch LCD | 8 W | 10 W |
| **Total** | **28 W** | **38 W** |

- XPS: own cells + USB-C PD **65 W+**. No 48→12, no boost from this pack.
- Pack: 12 V 20 Ah LiFePO4, 181 × 167 × 77 mm, **on its side**. 240 Wh / 28 W ≈ 8.5 h.
- 15 A fuse **at the terminal**. BMS is not a fuse.
- Own 14.6 V LiFePO4 charger. Label the three XT60s (two 48 V, one 12 V).

**Coils are 48 V on pack A**, 5 A slow-blow. Measure inrush (one listing claimed 167 W). Holding ~0.3 A.

| What dies | Contactors |
|---|---|
| Pack A | Coils die. Both open |
| 12 V pack | Teensy dies. Arm MOSFET opens chain |
| Pack B | Rule 4 only |
| Teensy crash, pack A alive | Watchdog only |

4700 µF on 12 V for fan/LiDAR inrush.

## 4. Amp

TPA3116D2 (owner, 2026-09-29; was TPA3255). Max **26 V**. A “48 V” pack is **54.6 V** full (13S) or **58.4 V** (16S LiFePO4). Dedicated **48→24 V 5 A (120 W)**, input **30–75 V**, off pack A through the 10 A fuse. Not on 12 V: bass peaks on the 12 V rail can reset the Teensy.

Check every part against **full** pack voltage.

## 5. Switches

| # | What | When |
|---|---|---|
| 1 | XT60 per pack | Before wiring, transport, overnight. **Only with the contactors open** |
| 2 | Mushroom E-stop | Emergency. Motors dead, electronics alive |
| 3 | Wireless E-stop | Must **open on signal loss**, not only on a stop message |
| 4 | Arm switch on TX | Session start/stop. Software |

Every 48 V fuse is 10×38 mm gPV, 1000 V DC (30 / 10 / 5 A). Blade and J-case fuses are 32 V: 12 V side only.

XT60 for the disconnect (owner, 2026-09-29; was XT90-S). It has **no anti-spark resistor**, so **plug and unplug only disarmed, contactors open**: the controller capacitors then sit behind the open contactor and the contacts do not arc. Plugging in armed burns the pins a little every time. 30 A continuous is fine for ~8 A cruising and 40 A bursts.

**Socket half on the battery.** Live pins on the pack = unfused short. Cap both halves.

```
PACK A + ── 5 A slow-blow ── mushroom NC ── wireless NC ── Teensy arm MOSFET
                                                      ├── coil A
                                                      └── coil B ── PACK A −
```

Contactor must be **DC-rated** ≥ 48 V 80 A. AC-rated welds shut.

Non-emergency: Spine ramps to zero, then drops the contactor. Mushroom does not wait. TVS on each controller input.

## 6. Wire

| Run | Gauge |
|---|---|
Three sizes only (owner, 2026-09-29). All silicone.

| Run | Gauge |
|---|---|
| Pack → 30 A fuse → contactor → controller | 12 AWG |
| Phases | owned motor cable |
| Ground bond | 12 AWG, short, **not fused** |
| 12 V pack → rail | 12 AWG (15 A fuse) |
| Amp 48→24 and 24 V | 16 AWG |
| 12 V distribution | 16 AWG |
| Coils, E-stop chain | 16 AWG |
| Throttle, reverse, e-brake | 22 AWG **shielded** |
| Halls / thermistors | 22 AWG shielded, away from phases |

Ring terminals: 12 AWG → yellow RV5.5, 16 AWG → red RV1.25, one HS-30J crimper.

## 7. Throttle path

```
Teensy 3.3 V I2C → level shift 5 V → 2× MCP4725 → opto → controller throttle
                 → pin 5 kick → watchdog → NC relay shorts both throttles
```

1. Relay is not optional. DAC holds last voltage.
2. Failed DAC write → stop kicking. Test 16.
3. Shielded, away from phases. Noise is throttle.
4. Opto isolate. Controller throttle ground is that pack’s negative.

## 8. Survive Midburn

- Crimp moving wires. Do not solder.
- Strain-relieve every connector.
- Signal crosses phases at 90°.
- Fan **in**, filter on inlet. Positive pressure.
- Nothing important on the body floor.
- Label both ends of every wire.

## 9. Commissioning

Bench supply 48 V, **2 A limit**. Packs last.

1. Bond negatives only. One ground path.
2. Coil chain, no contactors. Each of four breaks opens it.
3. Contactors on the bench. Both click.
4. 12 V pack + 15 A. 12 V on the rail. One path 12 V− to pack−.
5. Spine on. Arm holds contactors.
6. Controllers, no motors. Throttle 0–3.3 V follows Teensy.
7. One motor on blocks. Stops on every §3 fault.
8. Second motor. Steers in the air.
9. Watchdog: kill Teensy power while a motor runs. Relay opens.
10. Real packs. Then `03-safety-log.md`.
