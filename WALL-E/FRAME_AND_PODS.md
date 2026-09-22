# Frame and pods — the mechanical facts, in one place

This is the page to read before you cut, drill, or weld anything. It answers
one question: **where does the frame meet the pods, and what is allowed to
change?** The step-by-step build order is in [BUILD.md](BUILD.md), further down
this same guide page.

---

## 1. The rule that comes before everything

The two track pods are **built**. Nothing in the WALL-E project changes them.
**No new hole goes into a built pod.** The frame is designed around what the
pods already are, never the other way round.

Because of that rule, the pod numbers are not typed into the frame model. They
live in one file, `pod_interface.scad`, and a checker compares that file against
the real pod model:

```
cd WALL-E
./pod_latest.sh                                        # point at the newest revision
openscad -o chk.echo --export-format echo check_pod_interface.scad
```

`pod_latest.sh` picks the **highest** `archive/revNNN-*/apollo_track_pod_revNNN.scad`
on disk and writes `pod_latest.scad`. So WALL-E always follows the latest pod
revision. Nothing is pinned to an old one by hand. `render_all.sh` runs this
first and **stops** if the check says MISMATCH, because every dimension
downstream of a wrong pod number is also wrong.

Today the newest revision is **rev013-double-shear**, and all 23 numbers agree.

---

## 2. The z stack — what the rail actually touches

Measured on the built pods (2026-09-18), outward from one pod's centre plane:

| From | To | What |
|---|---|---|
| 0 | 59 | belt, 118 wide |
| 76.5 | 82.5 | **green plate**, 60×6 — the two M12 holes are in here |
| 82.5 | 88.5 | **carrier plate**, 40×6 |
| 88.5 | 92.5 | scooter fork leg — **not fitted on WALL-E** |

**This order changed.** In rev012 the green plate was the outermost part and the
rail bolted flat onto it. Rev013 measured the real pods: the plate is **inboard**
of the carrier, so the carrier now stands **6 mm proud** of the plate.

Consequence, and it is the whole reason this page exists:

- The rail comes in from the middle of the robot and **lands on the carrier**,
  at 88.5 from the pod centre. That is `pod_mount_z`.
- The M12 holes are 6 mm further out, in the green plate.
- So the bolts cross a **6 mm air gap**, and that gap needs a **packer**.

The carrier cannot be dodged: it is only 40 mm wide (±20 either side of the hub
axle) but it runs the full height of the 197–257 mm rail band.

---

## 3. The joint, part by part

Per side, inboard to outboard:

```
M12 head  →  rail inner wall  →  Ø25/Ø13 sleeve in the rail  →  rail outer wall
          →  PACKER 6 mm  →  green plate 6 mm  →  M12 nut welded on the far face
```

- **Rail:** 60×30×3 box, outer face at 161.5 from the robot centre line.
- **Sleeve:** Ø25 outside, Ø13 bore, 30 long, welded through both rail walls.
  Without it an M12 at full torque crushes a 3 mm wall.
- **Packer:** 60×6 offcut — the same stock as the green plates. One per side,
  drilled Ø13 at both M12 centres. **Without the packer there is no clamp at
  all**: the bolt would simply pull the rail wall into the gap.
- **Bolts:** 2 × M12 10.9 per side. Four bolts and **a pod is off the robot**.

Resulting overall width: **677 mm** (pods 500 apart, centre to centre).

---

## 4. Numbers you can check with a tape measure

| Measure this on the real pod | Should be |
|---|---|
| Clear gap between the two carrier plates | 165 mm |
| Over the two carrier plates, outer face to outer face | 177 mm |
| Over the two green plates | 165 mm |
| Green plate band, bottom edge above ground | 197 mm |
| Green plate band, top edge above ground | 257 mm |
| M12 hole centres, forward of the hub axle | 108 and 168 mm |
| Belt width | 118 mm |

If any of these disagree with the pod, **the pod wins** — fix
`pod_interface.scad`, re-run the check, then re-run the guards. Do not adjust
the frame numbers directly; they are all derived.

---

## 5. Where the numbers come from, and what happens if you change one

```
archive/rev013-*/apollo_track_pod_rev013.scad     the pods (never edited here)
        │
        ├── pod_latest.sh  →  pod_latest.scad     "newest revision on disk"
        │        │
        │        └── check_pod_interface.scad     23 numbers, OK or MISMATCH
        │
pod_interface.scad                                the only copy of pod facts
        │
cad/walle_frame.scad                              everything else is derived
        │
        └── 46 guards: clearances, stresses, bolt edge distances
```

Change `pod_cl` (how far apart the pods sit) and the width, the bay, the battery
box and the anti-tip arms all move with it. Change a pod number by hand without
the checker agreeing, and the model lies to you quietly. That is exactly what
happened once before: the stack was written as 84/88/94/100, the frame came out
14 mm too wide per side, and only the checker caught it.

---

## 6. Steel list for the pod joint

| Qty | Part | Stock |
|---|---|---|
| 2 | Rail, 550 long | 60×30×3 box |
| 4 | Sleeve, Ø25 × Ø13 × 30 | turned or bought |
| 2 | Packer, 60 long, 2 × Ø13 holes | 60×6 flat |
| 4 | Bolt M12 × 10.9, plus nyloc | — |
| 4 | M12 nut, welded to the green plate's far face | — |

The full list, with prices and lead times, is in part 2 of the guide
(`docs/05-bom.md`).
