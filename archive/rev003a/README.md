# Apollo Track Pod — Articulated "Split-Frame" Suspension Mod

**Rev 003a · 2026-07-20 · Status: pivot downsized M20 → M16 (bushings 16×22×20); fork gaps re-measured 140/140 — pods identical, belt-fit risk gone (11 mm/side); full 3D collision audit fixed 5 interferences (pivot stack made continuous with outboard sleeves; boss orientation; shock bolt, cross-brace and keel all moved out of collisions) — every clearance now guarded in the .scad; remaining to measure: guide-lug height only**

Converts a rigid rubber-track pod (hub-motor drive sprocket on a static Ø10 axle
between scooter-fork legs, two bearing-mounted lower idlers, lugged rubber band)
into an independently articulating suspension: a central pivot below the drive hub,
a leading and a trailing arm, and two coil-over shocks. Each lower idler gets
**+30 / −27.5 mm** of independent vertical travel instead of zero.

---

## Project files

| File | What it is |
|---|---|
| **Blueprint (web)** | https://claude.ai/code/artifact/8435d971-16c0-4a02-9ff1-7adc27d6350e — 7 drawing sheets, BOM + shopping guide (§7.1–§7.9: per-part sourcing, substitutes, costs, receiving inspection), fabrication specs, per-component build chapters (§9.1–§9.8: tools, steps, checks, common mistakes), test protocol. Readable, always-current version of record. |
| `apollo_track_pod_blueprint.html` / `.pdf` | Local copy of the blueprint; the PDF is printed from the HTML (one topic per page). |
| `apollo_track_pod.scad` | Parametric OpenSCAD 3D model (companion to the blueprint). Assembly / exploded / flat-plate modes, articulation animation, DXF + STL export. Verified rendering in all modes. |
| `README.md` | This file. |

### Using the OpenSCAD model

```bash
open -a OpenSCAD apollo_track_pod.scad     # OpenSCAD is installed via Homebrew
```

- `render_mode = "assembly"` — full pod; `lead_angle` / `trail_angle` sliders (−15…+15) articulate the arms; `animate = true` + View→Animate (FPS 20, Steps 100) cycles the suspension.
- `render_mode = "exploded"` — assembly reference.
- `render_mode = "tensioner"` — labeled 3D close-up of the Sheet-6 belt tensioner
  (slot, adjuster blocks, draw bolts, welded lugs); `tension_pos` (0–25) slides the
  axle through its take-up.
- `render_mode = "plates"` — all 8 laser-cut steel parts flat. Export for the laser cutter:

```bash
openscad -o plates.dxf -D 'render_mode="plates"' apollo_track_pod.scad
openscad -o pod.stl    -D 'render_mode="assembly"' apollo_track_pod.scad
```

All Sheet-0 datums are variables at the top of the file — every part and the DXF
resize from them. The console echoes derived values (C, travel, motion ratio) each render.

---

## How the mechanism works

The stock pod's rigid internal frame is removed and replaced by:

1. **Carrier plates ×2** (6 mm A36, identical symmetric part — Rev 002) — the new
   backbone. Each hangs from a scooter-fork leg: the hub-motor's static Ø10 flatted
   axle passes through a matching slot (the plate doubles as a torque arm) and one
   M8 bolt into the leg 52 mm above locks rotation. No carrier bearings, no
   anti-rotation link — the fork is the chassis anchor. Plates sit on the leg OUTER
   faces (|z| = 74 front AND rear — both gaps 140, legs 4 mm; Rev 003), outside
   the belt's 118 mm width (15 mm/side),
   so **the carrier can never touch the track at any articulation**. Boxed together
   by the hub axle (top), the pivot axle (middle), and the **M8 keel standoff
   between the sprocket's swept disc and the pivot boss** (bottom).
2. **Central pivot axle** — M16 class-10.9 bolt (Rev 003, was M20×1.5) through the carrier tongues,
   38 mm above the idler axle line (raised from 20 in two steps for belt clearance;
   38 is near the max — the keel window closes at 42).
3. **Leading + trailing arms** — fork weldments (2 plates each, ¼″ A36) nested on the
   pivot like scissors; 4 flanged SAE 841 bronze bushings (Ø16×Ø22×20), one in a
   25 mm boss tube per fork plate — trailing bosses point inboard, leading bosses
   outboard, so the whole stack (centre spacer ≈14, 6 thrust washers, 2 outboard
   sleeves ≈7) is continuous carrier-to-carrier (Rev 003a). Fork shape keeps
   each idler centred on the belt. Trailing arm has a 25 mm slot + a motorcycle-style
   chain adjuster (Rev 002b): tapped block on each axle end, M8 draw bolt through a
   lug welded to the plate face — advancing the bolt draws the axle rearward.
4. **Coil-over shocks ×2** — run **outboard of the carrier plates** (|z| = 94;
   Rev 002c/003 — with the measured 4 mm legs the carriers sit at 74, leaving
   only 15 mm inboard of them, so the Rev 002 inboard placement doesn't fit):
   upper eye on a tab welded to the carrier OUTER face at (±52, +6) from the
   hub centre, lower eye on a Ø10 through-bolt + ≈45 mm spacer sleeve through
   both arm-fork plates at a = 0.485·C = 56.9, leaning ~68° to the arm
   (Rev 003a: the old 0.68·C bolt passed through the Ø108 idler wheel; the old
   57° line ran the coil spring into the carrier tongue). MR ≈ 0.45.

### Design risks (mitigations are mandatory, see blueprint §0)
- **Belt derailment** — articulation changes belt path length (~6 mm through travel).
  Mitigated by ±15° travel limit, spring preload, and correct tensioner setting
  (10–15 mm mid-span sag).
- ~~Belt-to-fork fit~~ — resolved in Rev 003: both fork gaps re-measured at
  **140 mm**, so the 118 mm belt has 11 mm per side front and rear (the earlier
  120 mm front reading, which left 1 mm/side, was wrong).
- ~~Anti-rotation~~ — resolved in Rev 002: the carriers bolt straight to the fork legs.

---

## Sheet-0 datums — measured 2026-07-12 (remaining blanks: F, lug profile, J)

Everything is parametric on these.

| Datum | What | Typical* | Measured |
|---|---|---|---|
| track | Belt: cord-line circumference × width × pitch × links | — | **1080 × 118 mm, 60 mm pitch, 18 links** (2.1 kg) |
| A | Idler axle centre-to-centre | 230–300 | **222.2 — solved from the belt cord line** (10T × 60 pitch = cord Ø191, 5.5 above the Ø180 face) |
| B | Hub centre height above idler axle line | 150–200 | **170** |
| D | Idler wheel OD | 90–120 | **108** (WJ wheel) |
| G | Idler bearing bore | 15–20 | **15** — bearings are **6302-2RS (15×42×13)**; caliper read 14.86 = 15 nominal |
| sprocket | Drive sprocket OD × teeth | — | **180 × 10T** (hub motor inside) |
| fork | Fork-leg inner gap (front / rear) | — | **140 / 140** (re-measured 2026-07-20, Rev 003 — was 120/140) — leg thickness **4** |
| axle | Hub-motor axle | — | **Ø10, flatted, static** — carrier plates slot onto it (torque-arm style) |
| F | Belt inner width between guide lugs | 60–90 | **62 derived** (H + 4, matched wheel/belt set) |
| lug_h / lug_w | Guide lug height / row width | — | ___ (20 / 18 conservative — owner estimates 10–20; **measure**) |
| H | Idler hub width | 40–60 | **58** (57.85) |
| T | Belt carcass thickness | 8–14 | **~12** (confirmed) |

\* sanity-check ranges only, never for cutting.

**Derived (all exact, from the .scad echoes):** `A = 222.2` · `P = B − 38 = 132` ·
`C = 117.4` (arm length) · neutral droop `18.9°` · wheel travel `+30 / −27.5 mm` at ±15° ·
shock station `a = 0.485·C = 56.9` · upper shock eye at `(±52, +6)` from hub centre ·
keel centre `100` below hub centre (Ø12×1.5 tube) · motion ratio `MR ≈ 0.45` ·
fork widths: trailing arm `60` inner / leading arm `75.7` inner · carrier planes `|z| = 74` (both pods) ·
pivot axle stack `≈182` → **M16 cl.10.9 × 190, part-threaded** (both pods) · shock plane `|z| = 94` (outboard).

**Idler axle:** the 6302 bearings take a **Ø15 mm axle** — a 15×100 MTB thru-axle
(M15×1.5) or a 15 mm hardened shaft + collars, per the sourcing notes.

**Belt-clearance guard (Rev 001b):** every render echoes a PASS/WARN line per hanging
part (carrier tongue, keel, pivot spacer, boss) against the belt/lug line at full bump.
All must read PASS with ≥5 mm before cutting steel — re-check after measuring lug_h/F.

---

## Shock (suspension) purchasing spec

Two per pod, standard "e-scooter / mini-moto rear shock" type
(the expanded buying guide — sources, search terms, receipt checks — is blueprint **§7.4**):

| Spec | Requirement |
|---|---|
| Type | Coil-over, oil-damped (not friction/spring-only), adjustable preload, replaceable spring |
| Eye-to-eye length | **≈ 0.85–0.9 × B** → B 145–160 → 125/135 mm · **B 160–180 → 150 mm** (design default) · B 180–200 → 165 mm |
| Stroke | ≥ 30 mm (uses ~24 mm at full ±15°; check short shocks' stroke in the listing) |
| Eyelet bore | Ø10 mm (or with reducer bushings) |
| Installed length | free length − ~10 mm sag — use this when positioning the upper tab |
| Spring rate | `k [N/mm] ≈ 2.15 × (kg per pod, loaded)`; N/mm × 5.7 ≈ lb/in (Rev 003a: was 1.35× — the shock station moved to 0.485·C for wheel clearance, MR 0.57 → 0.45) |

Spring quick table (weight per pod, vehicle loaded with rider):
30 kg → ~370 lb/in · 40 kg → ~490 lb/in · 50 kg → ~615 lb/in · 60 kg → ~740 lb/in.
Buy one spring a step softer and one stiffer at the same time. The upper tab is welded
*after* the shock is in hand, so exact length has tolerance — verify placement in the
OpenSCAD model by setting `shock_ee`.

---

## Build order (summary — full per-component instructions in blueprint §9.1–§9.8, test protocol §10)

1. Strip one donor pod; photograph/measure the internal frame + anti-rotation (datum J).
2. Fill in datums → update `.scad` → export `plates.dxf` → laser-cut 8 plates.
3. Press bushings (trailing flanges inboard, leading flanges outboard); dry-stack the pivot (Sheet 2 order); cut the centre spacer + 2 outboard sleeves so idlers sit mid-belt and the stack is snug carrier-to-carrier.
4. Bolt carriers to the fork legs (axle slot + M8 per leg) and fit the keel standoff; motor must spin free, ≥3 mm/face.
5. Locate shock mounts with shocks held at ~30% compression; tack; hand-cycle ±15°; final-weld (bushings out).
6. Paint → final assembly → fit idlers → wrap belt → tension (10–15 mm sag) → torque axle nuts + fork M8s.
7. Test protocol: bench articulation ×50 → bench spin 5 min (belt must not walk) → loaded creep over 50 mm plank → short ridden test → retorque at 1 h / 5 h / every 20 h.
8. Only after the first pod passes: replicate for the other side (mirror carriers only).

Torque: M8 cl.10.9 — 30 N·m · M10 — 60 N·m · M12 — 105 N·m · M16 pivot nylock — zero end-float then back ⅛ turn (running fit). Paint-pen witness marks on everything.

---

## Revision history

- **Rev 001** — initial engineering pass over the AI-concept sketch. Arms changed to fork
  weldments (idler centring); shock tab moved 0.45·C → 0.68·C (sane spring rates);
  eccentric-cam tensioner → slot + jack bolt; carrier bearings + anti-rotation link added
  (concept had no torque path to chassis); parametric datum system added.
- **Rev 001a** — corrections found by 3D fit-check in the OpenSCAD model: shocks moved
  outboard of the carrier plates, and the four bolt-circle cross-standoffs (which passed
  through the sprocket's swept disc) replaced by a single keel standoff below the pivot.
- **Rev 001b** — real datums baked in (track 1083×118 @60 mm pitch, sprocket 180,
  idler 108×58 on 6302-2RS → 15 mm axle); idler spacing A now solved from track length.
  **Belt-clearance fix:** at full bump the belt bottom run rises ~32 mm and the 001a keel
  standoff would have hit it by ~40 mm — keel relocated between sprocket and pivot boss,
  pivot raised (drop 20→30), carrier pivot circle slimmed Ø56→Ø48. Automatic PASS/WARN
  clearance guard added to every render.
- **Rev 001c** — pivot raised further (drop 30→38, near the 42 hard limit where the keel
  window closes): lug-top margin at full bump 7.6→15.3 mm, steel-touches-belt angle
  +18.5°→+22° (buffer against shock-travel overshoot). Keel moved up 6 mm with it;
  keel-to-sprocket and keel-to-boss gaps added to the clearance guard. Cost: belt-path
  variation through travel 3.6→5.7 mm — within tensioner range.
- **Rev 002** — owner interview: the pod is a **hub-motor scooter conversion** (motor
  inside the sprocket, static Ø10 flatted axle, fork gaps 120 front / 140 rear).
  Carriers redesigned as fork-hung torque-arm plates (identical symmetric part, axle
  slot + one M8 per leg); 6205 bearings, axle sleeve and anti-rotation link deleted;
  shocks moved inboard of the carriers; sprocket counted 10T → belt solver corrected
  to the cord line (A 243 → 222.2). Carriers now ride outside the belt width — the
  original tongue-hits-track failure mode is geometrically impossible. New fit risk
  flagged: 118 belt in 120 front fork gap (1 mm/side).
- **Rev 002a** (2026-07-13) — documentation only, no dimension changes: blueprint §7
  expanded from a bare BOM into a shopping guide (§7.1–§7.9 — per-part spec, where to
  buy, search terms, substitutes, rough cost, receiving-inspection table); §9 expanded
  into per-component build chapters (§9.1–§9.8 — tools, numbered steps, pass/fail
  checks, common mistakes); print CSS added so the PDF paginates one topic per page.
- **Rev 002b** (2026-07-13) — Sheet-6 belt tensioner detailed and modeled explicitly in
  the .scad: motorcycle chain-adjuster style (tapped adjuster block on each axle end,
  M8×60 draw bolt through a lug welded to the fork-plate outer face, jam nut). The 3D
  fit-check moved the lug from the plate tip to a station 34 mm behind the nominal axle
  centre — a tip lug puts the bolt head outside the belt's 54 mm wrap radius at slack.
  New: `tension_pos` parameter, `render_mode="tensioner"` labeled close-up, and a
  "draw-bolt head to belt wrap" PASS/WARN guard echo. BOM #12 updated.
- **Rev 002c** (2026-07-13) — fork legs **measured: 4 mm** (placeholder was 30).
  Carrier planes move in to |z| = 64/74; pivot axle stack 162/182 → **M20×1.5 ×
  170/190** (was 220/240); fork bolts M8×30; keel tube 128/148 + rod ≈152/172.
  **Shocks return outboard of the carriers** (|z| = 84/94, tabs on the OUTER faces,
  sleeves ≈35) — only 5 mm remain between belt edge and carrier, so the Rev 002
  inboard placement no longer fits. Side-view shock geometry unchanged. The .scad
  picks the shock side automatically and echoes buy/cut lengths per fork_gap.
  Only open measurement: guide-lug height.
- **Rev 003** (2026-07-20) — two owner changes. **(1) Pivot downsized M20 → M16**
  class-10.9 (still ~9× margin over the ~1.2 kN full-bump load); everything on
  the pivot cascades: bushings → SAE 841 flanged **16×22×20** (flange ≈Ø28×3),
  boss tube → 32×5 (OD unchanged, ream ID 22 H7 — carrier window and clearance
  guards untouched), spacer tube → 22×16, thrust washers → Ø30×Ø16×1.5, axle
  seats ream Ø22 H7. **(2) Fork gap re-measured: 140 mm front AND rear** (the
  120 front reading was wrong). Both pods are now identical — carriers at
  |z| = 74, axle stack ≈182 → **M16 × 190** ×2, keel tube 148 + rod ≈172 ×2,
  shocks outboard at |z| = 94. The 1 mm/side front belt-fit risk is gone
  (11 mm/side). All clearance guards PASS (spacer margin actually improves,
  Ø25 → Ø22).
- **Rev 003a** (2026-07-20) — **full 3D collision audit** (owner spotted the first two, the audit found the rest). Five fixes, all now guarded with PASS/WARN echoes in the .scad:
  1. **Pivot stack made continuous.** The arm pack (~92 wide) never reached the carrier inner faces (148 apart) — ~29 mm of bare axle per side meant the nylock had nothing to snug against and the arms could drift sideways. The 25-long bosses now point *inboard* on the trailing fork and *outboard* on the leading fork (at the scissor interface there is only a 1.5 mm washer gap — bosses can't face each other there); centre spacer shrinks ≈60 → **≈14**, two new **outboard sleeves ≈7** close the chain to the carriers, thrust washers 4 → **6**. All three tube pieces cut at dry-stack.
  2. **Shock through-bolt vs idler wheel:** at a = 0.68·C the lower bolt passed 12 mm *inside* the Ø108 wheel. Moved to **a = 0.485·C** (4.1 mm clear, guarded). MR 0.57 → 0.41.
  3. **Shock angle/coil vs carrier:** at 57° the coil spring (Ø~44) overlapped the carrier tongue edge and tab foot. **θ = 68°**, tab weld foot re-aimed at the hub boss, carrier tab lobe simplified — coil clears by 7.5 mm (guarded), and the steeper line recovers MR to **0.45** (springs ≈2.15×kg/pod, e.g. ~490 lb/in at 40 kg).
  4. **Cross-brace vs idler wheel:** the brace at a±25 also passed through the wheel — moved inboard to x = 28..58 (7 mm clear, guarded).
  5. **Keel vs arm plates:** the keel at −104 ran through the Ø64 plate boss discs (they span −100..−164). Plate boss disc slimmed to **Ø44**, keel tube **Ø16 → Ø12×1.5**, raised to −100 — 4 mm to the sprocket disc and 4 mm to the boss disc, both articulation-invariant (the disc is centred on the pivot), guarded. Shock-bolt Ø30 lobe added to the plate profile (the Ø10 hole was <1 mm from the tapered edge at the new station).

## Open items

- [x] Take Sheet-0 measurements — track, A (solved), B, D, G, H, sprocket 10T, fork gaps, axle
- [x] Measure: **fork leg thickness** — 4 mm (2026-07-13; axle/keel/shock placement updated, Rev 002c)
- [x] Re-measure fork gaps — **140 front and rear** (2026-07-20, Rev 003; belt-fit risk closed, 11 mm/side)
- [ ] Measure: **lug height** (`lug_h`, assumed 20) — also needed to close the one **unguarded** clearance: guide-lug tips on the *diagonal* belt runs vs the arm-plate top edges and shock hardware near full bump (the guards cover the bottom run only; at lug_h = 20 this is tight on paper, at lug_h ≤ 12 it clears comfortably)
- [x] Plug datums into `.scad`, confirm fit (all clearance checks PASS at full bump)
- [ ] Export final `plates.dxf` (leg_t confirmed; re-check after lug_h is measured)
- [x] Shock length: B=170 → **150 mm eye-to-eye, 30 mm stroke (not longer)**; weigh corner load → pick spring rate (~330 lb/in at 40 kg/pod)
- [ ] Order idler axles: 15 mm (thru-axle or shaft + collars)
- [x] Bake real numbers into the blueprint sheets (artifact updated to Rev 002)
- [ ] Confirm vehicle-side details: total loaded weight, 2 vs 4 pods
