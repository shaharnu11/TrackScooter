# WALL-E eyes — steel tube + printed cartridge

Decided with Shahar, 2026-09-30. One eye = one steel tube + one cartridge.
Build 2.

![side cut](eye_cartridge_cut.png)

![the 2 printed parts](eye_cartridge_parts.png)

## Decisions

- **Eye body:** steel tube (owner's). ESP32 goes **inside** the tube.
- **Screen:** Waveshare **ESP32-S3-Touch-LCD-2.1B**: round 480×480, ESP32-S3 on
  the back, one USB-C. "B" = 2.5D curved glass (looks like an eyeball). Touch
  not used. Board **Ø75**.
- **Buy from:** Ingcool (official Waveshare distributor), ~₪121.55 each +
  ~₪30.54 shipping. 2 needed.
- **Sun shade:** screen sits **40 mm deep**. Inside of the tube painted
  **matte black** (no liner).
- **Mount:** a 2-part printed **cartridge**. The whole eye is built on the
  table, then slides into the tube. **3 screws** from outside hold it.
- **Cable seal:** PG16 gland (the USB-C plug passes through) + **silicone**
  (better than hot glue: hot glue goes soft at 60–80 °C in the sun).

## Parts per eye

| # | Part | Size | Source |
|---|---|---|---|
| 1 | Steel tube | **measure** (placeholder: inside 80, outside 84, length 144) | owned |
| 2 | Matte black paint inside, front ~45 mm | steel primer + flat/BBQ black | local |
| 3 | **Part 1**: sleeve + front lip | outside = tube inside − 0.4; lip hole 66; wall 2 | print |
| 4 | Foam ring | outside 75, hole 66, ~1.5 mm | cut from closed-cell foam sheet |
| 5 | Screen | Ø75, thickness **measure** (placeholder 12) | Waveshare 2.1B |
| 6 | **Part 2**: pusher tube + cap | pusher presses the board rim (71–75); cap hole 22.8 | print |
| 7 | PG16 cable gland, black | thread 22.5 | AliExpress, 10 pcs ~₪6 |
| 8 | 3 × M3 self-tapping screw | through steel + part 1 + part 2 | local |
| 9 | USB-C cable → neck → powered USB hub | length to the hub | — |
| 10 | Silicone sealant around the cable in the gland | — | local |

## Before printing: measure and set

In `eye_cartridge.scad`, top of the file:

- `tube_id`, `tube_od`, `tube_len`: the real tube.
- `screen_t`: the real screen (glass + board + parts on the back).
- Check where the **USB-C socket** is on the board: the pusher tube leaves
  Ø71 free on the back. If the socket is at the edge, the pusher needs a slot.

## Print

- **PETG or ASA, black.** Not PLA (soft at ~55 °C; a steel tube in the sun
  gets hotter).
- 4+ walls, 40 % infill (the screws go into it).
- Export:
  ```
  openscad -D part=\"p1\" -o eye_part1.stl eye_cartridge.scad
  openscad -D part=\"p2\" -o eye_part2.stl eye_cartridge.scad
  ```
  (`p2` is exported cap-down, ready to print.) Print 2 of each.

## Assembly (per eye)

1. Paint the inside of the tube (primer, then matte black), front ~45 mm.
2. Stick the foam ring on the back of the part 1 lip.
3. Screen into part 1 from the back, glass forward, against the foam.
4. USB-C cable through the PG16 gland in the part 2 cap; plug into the screen.
5. Part 2 into part 1: the pusher presses the screen forward.
6. Whole cartridge into the tube from the back, until the cap sits on the tube end.
7. Drill 3 × 3.2 mm through the steel at the 3 holes (7 mm from the end).
   Drive 3 × M3 self-tapping screws.
8. Tighten the gland; fill around the cable with silicone.

**Repair:** remove 3 screws, pull the cartridge out.

## Files

| File | What |
|---|---|
| `eye_cartridge.scad` | the 2 parts. `part = "p1" / "p2" / "all" / "cut"` |
| `eye_cartridge_section.scad` | the labelled side-cut drawing above |
| `eye_cartridge_cut.png` | side cut (labelled) |
| `eye_cartridge_parts.png` | the 2 parts |

## Still open

- Tube measurements (inside, outside, length).
- Screen thickness and USB-C socket position (when the screens arrive).
- Software: the Waveshare board drives its screen itself (RGB, ST7701).
  `firmware/face/panel_cfg.h` is still a placeholder: use Waveshare's example
  code for this board, not a QSPI setup.
- Old plan in `cad/walle_frame.scad` and `docs/02-overview.md`: 60 mm recess +
  clear acrylic dome. This design: 40 mm recess, no dome (the 2.1B glass is
  already curved). Update those files when the tube is measured.
