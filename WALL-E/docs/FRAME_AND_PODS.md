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

State: newest revision `rev013-double-shear`, 31/31 numbers agree.

---

## 2. Z stack

Measured on the built pods, 2026-09-18. Distance outward from one pod centre plane, mm:

| From | To | Part |
|---|---|---|
| 0 | 59 | belt, 118 wide |
| 76.5 | 82.5 | **U brace leg**, 40×6, at the hub. **Green plate**, 60×6, rear pod only |
| 82.5 | 88.5 | **carrier plate**, 40×6 |
| 88.5 | 94.5 | **WALL-E hanger**, 60×6, inboard side only |

The scooter fork legs (88.5–92.5) are **not fitted on WALL-E**. The hanger takes their place on the inboard side.

---

## 3. Joint: the frame hangs from the U braces

Decided 2026-09-29. Both U braces are **already built** (rev013 `use_ubar`).

Why not the green plates any more: **only the rear pod has green plates**. The front pod has shock stubs instead. So the old rail-to-green-plate joint could not bolt the front pod.

Per pod, on the **inboard** side only:

1. A **hanger** (60×6 flat bar) stands flat on the carrier's outer face, centred on the hub.
2. The U brace's **inboard M12** goes through the U leg, the carrier and the hanger. The head stays inside the U, as built. The nut is on the hanger. The bolt is 6 mm longer: M12×40 instead of M12×35.
3. At the top, the hanger is welded under a **tab** (6 mm plate, 80 × 177). The tab lies on the U bridge.
4. Two **clamp plates** (80 × 30 × 6) go under the bridge, one near each U leg.
5. **4 × M10** per pod go down through the tab, **beside** the 40 mm bridge, and through the clamp plates. Nothing is drilled into the pod.
6. The rail is welded to the hanger's inboard face.

Pitch (nose-down) load goes into the pod at two points 119 mm apart vertically: the M12 and the bridge. The M10 pairs on either side of the bridge also resist it.

Bridge heights: rev013 draws the front U 20 mm lower (387 mm) than the rear U (407 mm). **The owner says the built U braces are the same height** (2026-09-29). The built pods win, so the model uses **407 mm for both**, and both hangers are **215 mm**. This is **not measured yet**. Measure both bridge tops and correct `cad/pod_interface.scad`.

Tack the tabs with the frame sitting on the pods, then take it off and finish the welds.

| Part | Specification | Function |
|---|---|---|
| Rail | 60×30×3 box, 192–252 above ground, outer face 155.5 from robot centre | Structure. No holes |
| Hanger | 60×6 flat, Ø13 at 76 mm up from the bottom end | Joins the rail to the pod |
| Tab | 6 mm plate 80 × 177, 4 × Ø11 | Sits on the U bridge |
| Clamp | 6 mm plate 80 × 30, 2 × Ø11, 4 total | Under the bridge |
| Bolts | per pod: 1 × M12×40 8.8 + 4 × M10×35 8.8, washers, nylocks | Pod removal: 5 bolts per side |

The rail sits **under** the M12 nut (5.6 mm clear). That is what sets the rail height.

Overall width: **677 mm** at pod centres 500 mm apart.

**Cost of this joint:** the body floor has to clear the M10 heads on the tabs (413 + 7 mm). Owner accepted this height (2026-09-29). The floor goes from 335 to **428 mm**. The robot is **1003 mm** tall (was 910). Forward tip goes from 18.9° to **17.4°**. The castor still catches first (12.3°).

---

## 4. Verification by tape measure

| Measurement | Expected |
|---|---|
| Clear gap between carrier plates | 165 mm |
| Over carrier plates, outer to outer | 177 mm |
| U bridge top above ground, **front** pod | 407 mm (owner: same as rear; rev013 draws 387) |
| U bridge top above ground, **rear** pod | 407 mm |
| U brace M12 centre above ground | 268 mm |
| U bridge width (fore-aft), centred on the hub | 40 mm |
| Space under each bridge to the belt | ~74 mm |
| Belt width | 118 mm |

On disagreement the pod is authoritative. Correct `cad/pod_interface.scad`, re-run the check, re-run the guards. Do not edit frame numbers directly — they are derived.

---

## 5. Dependency chain

```
archive/rev013-*/apollo_track_pod_rev013.scad     the pods (not edited here)
        │
        ├── cad/pod_latest.sh → cad/pod_latest.scad   newest revision on disk
        │        │
        │        └── cad/check_pod_interface.scad     31 numbers, OK or MISMATCH
        │
cad/pod_interface.scad                            only copy of pod facts
        │
cad/walle_frame.scad                              all else derived
        │
        └── guards: clearances, stresses, bolt edge distances (64 today)
```

- Changing `pod_cl` moves width, bay, box, and anti-tip together.
- Edit `pod_interface.scad` only. Never invent frame numbers.

---

## 6. Steel for the joint

| Qty | Part | Stock |
|---|---|---|
| 2 | Rail, 550 long | 60×30×3 box |
| 2 | Hanger, 215 long, 1 × Ø13 | 60×6 flat |
| 2 | Tab, 80 × 177, 4 × Ø11 | 6 mm plate |
| 4 | Clamp plate, 80 × 30, 2 × Ø11 | 6 mm plate |
| 2 | Bolt M12×40 8.8 + washer + nylock (replaces the U brace's inboard M12×35) | — |
| 8 | Bolt M10×35 8.8 + washer + nylock | — |

Prices and lead times: `docs/05-bom.md`.
