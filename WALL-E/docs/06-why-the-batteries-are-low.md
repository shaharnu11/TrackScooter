# 06 — Batteries low, box sealed

Packs stay in the frame. The box is closed. Daily charge in place. Every pack still lifts out (L17).

## 1. Box

Six 12 mm ply panels. Cut list from `cad/walle_frame.scad`.

| Panel | Size |
|---|---|
| Floor, lid | 444 × 251. Lid: 12 × M5 at 110 mm pitch |
| Sides | 2 × 444 × 142. No holes |
| Ends | 2 × 251 × 142 |

- 3 mm closed-cell gasket. Bolt pitch 110 mm (gasket only seals where squeezed).
- 8 mm foam pad on the packs. Pad, not glue.
- M12 membrane vent in the **lid**, centreline, over the 24 mm gap between packs. A sealed box is a dust pump without it.

**Daily charge:** XT60 on the body, dust cap. Do not open the box every morning.

**Lift out:**

- 48 V: body off four risers → 12 × M5 lid → unplug XT60 + charge pigtail → lift.
- 12 V and PD pack: speaker boxes off → tray off → unplug → lift. 12 V is 14.6 V LiFePO4 charger. Label the three XT60s.
- XPS comes out with the tray.

Bench: one full charge with the lid on. ~12 W heat at 5 A. If it climbs, charge with the body off, lift the pack (L17), or drop current.

## 2. Why not in the body

Packs need a sealed case **wherever** they go. Body is hot (XPS, controllers, amp), crowded, and a bad place for a cell to vent.

- Traction pack 400 × 110 × 80 mm, ~8 kg. Shelf 356 mm deep. Two packs would eat the shelf.
- 12 V electronics pack is a **different** case (181 × 167 × 77 mm, ~2.5 kg). That one **is** on the shelf.
- Low volume is the best ballast.

| | CoM | Tips forward |
|---|---|---|
| Packs in the frame | 356 mm | **17.4°** |
| Packs on the shelf | 402 mm | 15.5° |

Castor at 12.3°. Speakers, two floors and the U-brace mount leave **5.1°**. Run the model for today’s numbers.

## 3. Ground clearance

Box floor = lowest point, **150 mm**. Since the U-brace mount (2026-09-29) the body floor is 136 mm over the lid, so the old 173 mm lid-bolt limit is gone. The box still hangs off the rails (192–252 mm). A higher box is not checked yet.

Do not put packs in the body for clearance.

Owner: leave 150 mm until the first sand drive (L18).
