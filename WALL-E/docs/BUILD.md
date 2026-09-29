# Building WALL-E

Order of work. Numbers from `cad/walle.scad`. Front = **+x**.

| File | |
|---|---|
| `cad/walle.scad` | Entry |
| `cad/pod_interface.scad` | 31 facts about the **built** pods |
| `cad/check_pod_interface.scad` | Must match the pod model |
| `cad/walle_frame.scad` | Everything else + guards |
| `cad/render_all.sh` | Check, redraw, rebuild guide |

```sh
cd WALL-E && cad/render_all.sh
```

Stops on pod mismatch. On purpose.

| Sheet | Use |
|---|---|
| 1 General | Heights |
| 2 Frame weldment | Give to the welder — step 3 |
| 3 Battery box | Plywood cut — step 5 |
| 4 Chest / speakers | Step 6 |
| 5 Shelf | Step 8 |

![Sheet 1 — general arrangement. Overall sizes and every important height.](fig/s1.svg)

| | |
|---|---|
| Overall | 1003 H, 677 W, 430 body L |
| Mass | ~95 kg, **guess** — step 0 |
| Lowest | box floor 150 mm |
| Tips | 17.4°. Castor 12.3°. **5.1°** in hand |
| Speakers | 2 × 6.5 inch, 7.5 L each |

---

# Step 0. Before cutting

### 0a. Joint (rev013, measured)

- The frame **hangs from the pods' U braces**. Only the rear pod has green plates, so they are not used.
- Per pod: a hanger on the inboard carrier face, on the U brace's own inboard M12 (made M12×40). A tab on top, clamped to the U bridge with 4 × M10 beside the bridge.
- The front pod's bridge is at 387 mm, the rear pod's at 407 mm. The hangers are 195 and 215 mm.
- Scooter fork legs come **off**.
- Full stack: [FRAME_AND_PODS.md](FRAME_AND_PODS.md).

### 0a2. Tape measure (do not trust this file)

| Measure | Should be |
|---|---|
| Clear between carriers | 165 mm |
| Over carriers | **177 mm** |
| U bridge top, front pod | 387 mm |
| U bridge top, rear pod | 407 mm |
| U brace M12 above ground | 268 mm |
| U bar | 40 × 6 mm |

If any differ: edit `cad/pod_interface.scad`, then `cad/pod_latest.sh`, checker, `cad/render_all.sh`. Never patch `walle_frame.scad` around a pod number.

### 0b. Weigh

Guesses in `cad/walle_frame.scad` (`STILL GUESSES`). Weigh a pod and a pack. If forward tip < ~15°, move mass back before the body.

**Check:** `every guard passes` and `ALL 31 NUMBERS AGREE`.

---

# Step 1. Cut steel

Sheet 2. 60×30×3 except castor legs.

| Part | Count | Length |
|---|---|---|
| Rail | 2 | 550 mm |
| Cross member | 2 | 251 mm |
| Castor leg, 30×30 | 2 | 82 mm |
| Castor tie | 2 | — |
| Hanger, 60×6 flat | 1 + 1 | 215 mm (rear pod), 195 mm (front pod) |
| Tab, 6 mm plate | 2 | 80 × 177 mm |
| Clamp plate, 6 mm plate | 4 | 80 × 30 mm |

1602 mm of 60×30. Rails same length ±1 mm.

---

# Step 2. Drill the hanger parts

The rails get **no holes**.

- Each hanger: **1 × Ø13**, centred, **76 mm up from the bottom end**. This is the U brace M12.
- Each tab: **4 × Ø11** at x ±27 mm, 39.5 and 149.5 mm from the inboard end.
- Each clamp plate: **2 × Ø11** at ±27 mm.
- Drill tab and clamps together, clamped as a stack, so the holes line up.

---

# Step 3. Weld

![Sheet 2 — frame weldment. This is the drawing the welder works from.](fig/s2.svg)

![The bare frame, three quarter view.](fig/walle_frame_3q.png)

- Rail outer faces 311 mm apart. **251 mm clear.**
- Rear cross 25 mm. Front 525 mm. From rail rear. Crosses between the rails: 251 mm.
- Rails 192–252 mm above ground.
- Hanger centred 275 mm from each rail's rear end, bottom flush with the rail bottom. Rail outer face welded to the hanger.
- Tab: tack it on top of the hanger **with the frame sitting on the pods**, M12s and M10s in. The two bridges are 20 mm apart in height, so do not trust a drawing here. Take it off, finish the welds.
- Anti-tip: 82 mm uprights, Ø75, 280 mm out, **35 mm** off the ground.

**Check:** diagonals match. Clear 251 mm at both ends.

---

# Step 4. Bolt to pods

![The robot cut in half, so you can see how the rail meets the pod and where the battery box hangs.](fig/walle_frame_section.png)

Per pod: take out the U brace's **inboard** M12×35. Put in an M12×40 through the U leg, carrier and hanger, nut on the hanger. Then 4 × M10×35 down through the tab, beside the bridge, into the clamp plates under it.

Pods vertical, frame level. Use a ring spanner on the M12 nut from above, with the body off.

---

# Step 5. Battery box

![Sheet 3 — the battery box: six plywood panels, drawn flat for cutting.](fig/s3.svg)

| Panel | Count | Size |
|---|---|---|
| Floor, lid | 1 each | 444 × 251 |
| Side | 2 | 444 × 142 |
| End | 2 | 251 × 142 |

Sides have **no holes** now. Lid: 12 × M5 at 110 mm, Ø12 vent centre.

1. Floor + walls. 2. 3 mm gasket. 3. Packs in. 4. 8 mm pad. 5. Lid.

Daily charge: XT60 on the body. Lift-out: L17. Floor is **150 mm** and the lowest point.

---

# Step 6. Body and chest

![Sheet 4 — chest panel and speaker baffle, with the two holes.](fig/s4.svg)

Floor 428 mm (8 mm over the M10 heads on the rear pod's U tab). Body 430 × 640 × 400 on 176 mm risers.

Chest: 530 × 290, set back 20 mm. Two Ø165, 330 mm apart, 194 mm up from panel bottom. Dry-fit drivers. 140 mm between rims. Each rim has 5 mm of plywood outboard. 7 inch LCD portrait 107 × 183 between them. Window 90 × 160. Bezel on the face.

---

# Step 7. Speaker boxes

260 × 200 × 205, 12 mm ply. **7.5 L.** Bolt on. Do not glue. Seal joints. Metal grilles. Cone should feel springy.

---

# Step 8. Shelf

![Sheet 5 — the electronics shelf: what goes where, and where the cable runs.](fig/s5.svg)

Two floors. Lower 356 × 546 at 440 mm: controllers, contactor, fuses, Teensy, 12 V pack **flat**, PD 65 W+, amp. Upper 315 × 360 tray at 544 mm: XPS + USB hub. Hub from 12 V rail. Amp has its own 48→24 V.

Straps, not glue. Cables long enough for the tray. After boxes on: can you still reach connectors? Can 12 V and PD come out?

Wiring: `04-power-and-wiring.md`.

---

# Step 9. Head

Rigid post. No pan/nod/tilt. Look = body turn.

Neck 70 mm off body top at 828 mm. Head centre 951 mm, 233 mm wide. Barrels Ø105, 128 mm apart. Height **1003 mm**. Screen 53 mm, recess 60 mm. Shade above 49°. Mouths: 7 mm clear. Toe in.

Camera under the brow: ELP 42 × 42 × 36 mm.

---

# Step 10. Before driving

1. Level ground. Castors **35 mm** clear.
2. Push the front. Castor touches **before** it goes over (12.3° vs 17.4°).
3. Slow on sand. Watch the **150 mm** box floor, not the tracks.

---

# After a change

```sh
cd WALL-E && cad/render_all.sh
```

Need `every guard passes` and `ALL 31 NUMBERS AGREE`.
