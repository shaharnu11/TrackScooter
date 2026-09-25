# Building WALL-E

Order of work. Numbers from `cad/walle.scad`. Front = **+x**.

| File | |
|---|---|
| `cad/walle.scad` | Entry |
| `cad/pod_interface.scad` | 23 facts about the **built** pods |
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
| Overall | 910 H, 677 W, 430 body L |
| Mass | ~91 kg, **guess** — step 0 |
| Lowest | box floor 150 mm |
| Tips | 19.0°. Castor 12.3°. **6.8°** in hand |
| Speakers | 2 × 6.5 inch, 7.5 L each |

---

# Step 0. Before cutting

### 0a. Joint (rev013, measured)

- Green plate inboard. Carrier 6 mm proud.
- Rail lands on the **carrier**. Packer 6 mm fills the step. Skip it and the bolt has no clamp.
- Scooter fork legs come **off**.
- Full stack: [FRAME_AND_PODS.md](FRAME_AND_PODS.md).

### 0a2. Tape measure (do not trust this file)

| Measure | Should be |
|---|---|
| Clear between carriers | 165 mm |
| Over carriers | **177 mm** |
| Over green plates | 165 mm |
| Plate thickness | 6 mm each |
| Band above ground | 197–257 mm |
| M12 centres, forward of hub | 108 and 168 mm |

If any differ: edit `cad/pod_interface.scad`, then `cad/pod_latest.sh`, checker, `cad/render_all.sh`. Never patch `walle_frame.scad` around a pod number.

### 0b. Weigh

Guesses in `cad/walle_frame.scad` (`STILL GUESSES`). Weigh a pod and a pack. If forward tip < ~15°, move mass back before the body.

**Check:** `every guard passes` and `ALL 23 NUMBERS AGREE`.

---

# Step 1. Cut steel

Sheet 2. 60×30×3 except castor legs.

| Part | Count | Length |
|---|---|---|
| Rail | 2 | 550 mm |
| Cross member | 2 | 263 mm |
| Castor leg, 30×30 | 2 | 87 mm |
| Castor tie | 2 | — |

1626 mm of 60×30. Rails same length ±1 mm.

---

# Step 2. Drill rails

Each rail: **2 × Ø25** through both walls.

- **107 mm and 167 mm from the REAR (−x) end**
- **30 mm up from the bottom**

Weld Ø25/Ø13 × 30 sleeve in each. Hold rail on the **carrier** with the packer; sleeves must line up with the plate holes.

---

# Step 3. Weld

![Sheet 2 — frame weldment. This is the drawing the welder works from.](fig/s2.svg)

![The bare frame, three quarter view.](fig/walle_frame_3q.png)

- Rail outer faces 323 mm apart. **263 mm clear.**
- Rear cross 25 mm. Front 525 mm. From rail rear. Crosses between the rails: 263 mm.
- Rails 197–257 mm above ground.
- Anti-tip: 87 mm uprights, Ø75, 280 mm out, **35 mm** off the ground.

**Check:** diagonals match. Clear 263 mm at both ends.

---

# Step 4. Bolt to pods

![The robot cut in half, so you can see how the rail meets the pod and where the battery box hangs.](fig/walle_frame_section.png)

4 × M12 10.9. Two per side. Pods vertical, frame level. Two bolts per side still reach.

---

# Step 5. Battery box

![Sheet 3 — the battery box: six plywood panels, drawn flat for cutting.](fig/s3.svg)

| Panel | Count | Size |
|---|---|---|
| Floor, lid | 1 each | 444 × 240 |
| Side | 2 | 444 × 142 |
| End | 2 | 240 × 142 |

Sides handed: Ø30 at 54 and 114 mm from rear, 77 mm up (spanner, not vents). Lid: 12 × M5 at 110 mm, Ø12 vent centre.

1. Floor + walls. 2. 3 mm gasket. 3. Packs in. 4. 8 mm pad. 5. Lid. 6. Ø30 plugs **after** pod bolts.

Daily charge: XT60 on the body. Lift-out: L17. Floor is **150 mm** and the lowest point.

---

# Step 6. Body and chest

![Sheet 4 — chest panel and speaker baffle, with the two holes.](fig/s4.svg)

Floor 335 mm (8 mm over belt crown). Body 430 × 640 × 400 on 78 mm risers.

Chest: 530 × 290, set back 20 mm. Two Ø165, 330 mm apart, 194 mm up from panel bottom. Dry-fit drivers. 140 mm between rims. Each rim has 5 mm of plywood outboard. 7 inch LCD portrait 107 × 183 between them. Window 90 × 160. Bezel on the face.

---

# Step 7. Speaker boxes

260 × 200 × 205, 12 mm ply. **7.5 L.** Bolt on. Do not glue. Seal joints. Metal grilles. Cone should feel springy.

---

# Step 8. Shelf

![Sheet 5 — the electronics shelf: what goes where, and where the cable runs.](fig/s5.svg)

Two floors. Lower 356 × 546 at 347 mm: controllers, contactor, fuses, Teensy, 12 V pack **flat**, PD 65 W+, amp. Upper 315 × 360 tray at 451 mm: XPS + USB hub. Hub from 12 V rail. Amp has its own 48→32 V.

Straps, not glue. Cables long enough for the tray. After boxes on: can you still reach connectors? Can 12 V and PD come out?

Wiring: `04-power-and-wiring.md`.

---

# Step 9. Head

Rigid post. No pan/nod/tilt. Look = body turn.

Neck 70 mm off body top at 735 mm. Head centre 858 mm, 233 mm wide. Barrels Ø105, 128 mm apart. Height **910 mm**. Screen 53 mm, recess 60 mm. Shade above 49°. Mouths: 7 mm clear. Toe in.

Camera under the brow: ELP 42 × 42 × 36 mm.

---

# Step 10. Before driving

1. Level ground. Castors **35 mm** clear.
2. Push the front. Castor touches **before** it goes over (12.3° vs 19.0°).
3. Slow on sand. Watch the **150 mm** box floor, not the tracks.

---

# After a change

```sh
cd WALL-E && cad/render_all.sh
```

Need `every guard passes` and `ALL 23 NUMBERS AGREE`.
