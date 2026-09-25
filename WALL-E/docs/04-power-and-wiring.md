# 04 — Power and wiring

Physical version of `01-architecture.md`.

- One 48 V pack per pod. Positives never meet. Negatives + 12 V negative bonded at **one** point. Bond not fused.
- Electronics on their own 12 V pack (D8). **Contactor coils stay on pack A.**

## 1. Tree

```
PACK A 48 V ── XT90-S ─┬── 60 A ── CONTACTOR A ── controller L ── left hub
                        ├── 10 A ── 48→32 V ── amp
                        └──  5 A ── E-stop chain ── both contactor coils (48 V)

PACK B 48 V ── XT90-S ──── 60 A ── CONTACTOR B ── controller R ── right hub

12 V 20 Ah ── 15 A ── 12 V rail ── 12→5 V ── Teensy, ESP32
              (USB hub, fans). XPS is NOT on this rail.

PACK A (−) ══ 10 AWG bond, not fused ══ PACK B (−) ══ 12 V (−)
```

- E-stop kills **motors only**. Electronics stay up. E-stop is not an isolator. Isolator = XT90-S (section 5).
- Both coils on one chain. Cutting one track only is a spin command. Never do that.

## 2. Current (91.6 kg)

| Case | Per side | Use |
|---|---|---|
| Straight, walking | ~2 A | Normal |
| Pivot on sand | ~8 A | Budget here |
| Start / rut | ~25 A | Seconds |
| Absolute | **40 A** | Wire and fuse must survive |

40 A is **measured**, not chosen. Controllers cannot change their peak. Clamp-meter at stall on blocks. If real peak ≠ 40 A, resize 12 AWG and 60 A. Teensy current control = back off throttle from ACS758. Slow.

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

TPA3255 max **53.5 V**. A “48 V” pack is **54.6 V** full (13S) or **58.4 V** (16S LiFePO4). Dedicated **48→32 V 150 W**, non-isolated, off pack A. Not on 12 V.

Check every part against **full** pack voltage.

## 5. Switches

| # | What | When |
|---|---|---|
| 1 | XT90-S per pack | Before wiring, transport, overnight |
| 2 | Mushroom E-stop | Emergency. Motors dead, electronics alive |
| 3 | Wireless E-stop | Must **open on signal loss**, not only on a stop message |
| 4 | Arm switch on TX | Session start/stop. Software |

XT90-S, not XT60, for the disconnect: ~43 A on pack A, anti-spark resistor, daily cycles.

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
| Pack → contactor → controller, 40 A | 10 AWG silicone |
| Phases | 12 AWG (or motor lead, whichever thicker) |
| Ground bond | 10 AWG, short, **not fused** |
| 12 V pack → rail | 14 AWG (sized for 15 A fuse) |
| Amp 48→32 and 32 V | 16 AWG |
| 12 V distribution | 16 AWG |
| Coils | 20 AWG |
| Throttle | 22 AWG **shielded** |
| Halls / thermistors | 24 AWG shielded, away from phases |

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
