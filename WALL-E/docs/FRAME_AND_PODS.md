# Frame and pods — mechanical interface

Scope: where the frame meets the pods, and what may change. Read before cutting, drilling or welding. Build order: [BUILD.md](BUILD.md).

---

## 1. Constraint

- The two track pods are built.
- This project does not modify them. **No new hole goes into a built pod.**
- The frame is derived from the pods. Not the reverse.

Pod numbers are not typed into the frame model. They exist in `cad/pod_interface.scad` and are checked against the pod model:

```
cd WALL-E
cad/pod_latest.sh                                      # select newest revision
openscad -o chk.echo --export-format echo cad/check_pod_interface.scad
```

- `cad/pod_latest.sh` selects the highest `archive/revNNN-*/apollo_track_pod_revNNN.scad` and writes `pod_latest.scad`.
- No revision is pinned by hand.
- `cad/render_all.sh` runs the check first and exits on MISMATCH. A wrong pod number invalidates every dimension below it.

State: newest revision `rev013-double-shear`, 23/23 numbers agree.

---

## 2. Z stack

Measured on the built pods, 2026-09-18. Distance outward from one pod centre plane, mm:

| From | To | Part |
|---|---|---|
| 0 | 59 | belt, 118 wide |
| 76.5 | 82.5 | **green plate**, 60×6. Contains the two M12 holes |
| 82.5 | 88.5 | **carrier plate**, 40×6 |
| 88.5 | 92.5 | scooter fork leg. **Not fitted on WALL-E** |

Change from rev012:

- rev012: green plate outermost, rail bolted flat to it.
- rev013 (measured): green plate is **inboard** of the carrier. Carrier stands **6 mm proud** of the plate.

Consequences:

- The rail approaches from the robot centre and lands on the **carrier**, at 88.5. This is `pod_mount_z`.
- The M12 holes are 6 mm further out, in the green plate.
- The bolts therefore cross a **6 mm gap**. The gap requires a **packer**.
- The carrier cannot be avoided: 40 mm wide (±20 about the hub axle), full height of the 197–257 mm rail band.

---

## 3. Joint stack

Per side, inboard to outboard:

```
M12 head  →  rail inner wall  →  Ø25/Ø13 sleeve in the rail  →  rail outer wall
          →  PACKER 6 mm  →  green plate 6 mm  →  M12 nut welded on the far face
```

| Part | Specification | Function |
|---|---|---|
| Rail | 60×30×3 box, outer face at 161.5 from robot centre | Structure |
| Sleeve | Ø25 OD, Ø13 bore, 30 long, welded through both rail walls | Prevents M12 preload crushing the 3 mm wall |
| Packer | 60×6, one per side, 2 × Ø13 at the M12 centres | Fills the carrier-to-plate step. Without it the bolt pulls the rail wall into the gap and clamp force is zero |
| Bolts | 2 × M12 10.9 per side | 4 bolts total: pod removal |

Overall width: **677 mm** at pod centres 500 mm apart.

---

## 4. Verification by tape measure

| Measurement | Expected |
|---|---|
| Clear gap between carrier plates | 165 mm |
| Over carrier plates, outer to outer | 177 mm |
| Over the two green plates | 165 mm |
| Green plate band, bottom edge above ground | 197 mm |
| Green plate band, top edge above ground | 257 mm |
| M12 hole centres, forward of hub axle | 108 and 168 mm |
| Belt width | 118 mm |

On disagreement the pod is authoritative. Correct `cad/pod_interface.scad`, re-run the check, re-run the guards. Do not edit frame numbers directly — they are derived.

---

## 5. Dependency chain

```
archive/rev013-*/apollo_track_pod_rev013.scad     the pods (not edited here)
        │
        ├── cad/pod_latest.sh → cad/pod_latest.scad   newest revision on disk
        │        │
        │        └── cad/check_pod_interface.scad     23 numbers, OK or MISMATCH
        │
cad/pod_interface.scad                            only copy of pod facts
        │
cad/walle_frame.scad                              all else derived
        │
        └── guards: clearances, stresses, bolt edge distances (55 today)
```

- Changing `pod_cl` moves width, bay, battery box and anti-tip arms together.
- Changing a pod number without the checker agreeing produces silent error.
- Precedent: the stack was once written 84/88/94/100. Result: frame 14 mm per side too wide. Detected only by the checker.

---

## 6. Steel for the joint

| Qty | Part | Stock |
|---|---|---|
| 2 | Rail, 550 long | 60×30×3 box |
| 4 | Sleeve, Ø25 × Ø13 × 30 | turned or bought |
| 2 | Packer, 60 long, 2 × Ø13 | 60×6 flat |
| 4 | Bolt M12 × 10.9 + nyloc | — |
| 4 | M12 nut, welded to green plate far face | — |

Prices and lead times: `docs/05-bom.md`.
