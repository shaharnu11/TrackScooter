# Apollo Track Pod — Articulated "Split-Frame" Suspension Mod

> ## THIS FOLDER = REV 011 — THE DESIGN OF RECORD (2026-08-10)
> **No grinder: the hub rim stays factory Ø165×35.** Forked from Rev 009; Revs 009 and 010
> are superseded history. The one change that defines this revision: **the hub sits 20 mm
> lower over the idler axle line (B 170 → 150)**, which stops the belt wasting length on its
> two diagonals and hands it to the ground run.
>
> | | Rev 009 | **Rev 011** |
> |---|---|---|
> | **Ground contact (A)** | 203.5 | **231.2 mm (+13.6 %)** |
> | ground pressure @130 kg | ~0.27 | **~0.24 kg/cm²** |
> | ride height | — | **20 mm lower** (the conversion had raised it ~120 mm over stock) |
> | B / drop / θ / a_frac | 170 / 38 / 72 / 0.433 | **150 / 22 / 80 / 0.434** |
> | arm C / neutral droop | 108.6 / 20.5° | **117.7 / 10.8°** |
> | wheel travel | +27.6 / −25.0 | **+30.7 / −29.2** |
> | motion ratio (springs want ≈0.435) | 0.4396 | **0.4351** |
> | shock bolt / brace / coil margins | 3.6 / 3.0 / 2.0 | **8.6 / 11.9 / 4.7** |
> | carrier / trailing arm / leading arm | 224 / 177 / 158 | **220 / 184 / 166** |
>
> **Sprocket is unchanged from Rev 009** — 11 teeth × 32.7°, marks every 56.6 mm on the rib,
> rib 18×16.54, wheel Ø198, cord Ø210. The printed parts and STLs in `stl/` carry over as-is.
>
> **New fabrication step:** chamfer the two REAR corners of every arm bar **10×10 mm**. Those
> corners swing closest to the spinning sprocket at full droop — a clearance that was never
> guarded in any earlier revision (Rev 009 sat at 4.1 mm). Rev 011 adds the guard and the
> chamfer takes it to 5.8 mm.
>
> **Hardware is untouched:** M12 stud axles, sleeves, shocks, springs, bearings, tubes and
> the printed sprocket all carry over. Only cut lengths and hole positions moved.
>
> Model: `apollo_track_pod_rev011.scad` · cut list: `apollo_track_pod_plates.pdf` +
> `plates_rev011.dxf` · wheel: `wheel_hub_print_blueprint_rev011.pdf` + `stl/`.

### Printing the 1:1 drilling templates

`rev011_1to1_drilling_templates.pdf` — one part per page, glue onto the bar,
centre-punch every red cross, peel, drill. Regenerate with:

```bash
python3 make_1to1_templates.py     # rewrites the .html + .pdf, then verifies them 1:1
```

**Print at 100% / "Actual size".** The pages are 195 × 259.5 mm, deliberately
smaller than the printable area of both A4 and US Letter, so "Actual size" and
Acrobat's "Shrink oversized pages" are both exact — but an explicit "Fit to page"
will still stretch them. Measure the SCALE CHECK ruler on every sheet before you
cut: if the 150 mm scale reads short, reprint at `15000 ÷ (the mm you measured)` %.

The generator re-opens its own PDF and asserts every outline, hole diameter and
ruler against the SCAD/DXF numbers, so a silent geometry regression fails the run
rather than reaching steel.

Converts a rigid rubber-track pod (hub-motor drive sprocket on a static Ø10 axle
between scooter-fork legs, two bearing-mounted lower idlers, lugged rubber band)
into an independently articulating suspension: a central pivot below the drive hub,
a leading and a trailing arm, and two coil-over shocks. Each lower idler gets
**+31.8 / −29.2 mm** of independent vertical travel instead of zero (Rev 008 geometry).

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
- `render_mode = "plates"` — all 10 flat-bar rectangles laid out flat (4 arm bars,
  2 carrier strips, 4 tab stubs — Rev 004). Print 1:1 as a drilling template, or
  export DXF if you still want a shop to cut them:

```bash
openscad -o plates.dxf -D 'render_mode="plates"' apollo_track_pod.scad
openscad -o pod.stl    -D 'render_mode="assembly"' apollo_track_pod.scad
```

All Sheet-0 datums are variables at the top of the file — every part and the DXF
resize from them. The console echoes derived values (C, travel, motion ratio) each render.

---

## How the mechanism works

The stock pod's rigid internal frame is removed and replaced by:

1. **Carriers ×2** (Rev 004: a 50 × 6 flat-bar strip ≈225 + two 40 × 6 × 55 tab
   stubs lap-welded at hub level — identical symmetric weldment) — the new
   backbone. Each hangs from a scooter-fork leg: the hub-motor's static Ø10 flatted
   axle passes through a matching slot (the plate doubles as a torque arm) and one
   M8 bolt into the leg 52 mm above locks rotation. No carrier bearings, no
   anti-rotation link — the fork is the chassis anchor. Plates sit on the leg OUTER
   faces (|z| = 74 front AND rear — both gaps 140, legs 4 mm; Rev 003), outside
   the belt's 118 mm width (15 mm/side),
   so **the carrier can never touch the track at any articulation**. Boxed together
   by the hub axle (top), the pivot axle (middle), and the **M8 keel standoff
   back in its Rev 004 window** (bottom) — between the sprocket's swept envelope
   (rib top r = 80 on the Rev 008 wheel) and the arm bar: keel centre 89.9 below
   the hub, 4.0 to the rib sweep / 16.1 to the bar, both guarded. (It spent
   Rev 005–005c parked below the arm bar while bigger ribs closed this window.)
2. **Central pivot axle** — M16×195 bolt, threaded 45 mm on one end only (Rev 004c, owner's actual part; was M20×1.5) through the carrier tongues,
   **38 mm above the idler axle line** — the original Rev 004 value, restored in
   Rev 007 once the corrected idler wrap gave the belt solve its length back
   (Rev 005's deeper-V detour to 55–60 is history; see the revision log).
3. **Leading + trailing arms** — fork weldments (2 plain 40 × ¼″ flat-bar plates each — Rev 004, rectangles only) nested on the
   pivot like scissors; 4 flanged SAE 841 bronze bushings (Ø16×Ø22×20), one in a
   25 mm boss tube per fork plate — trailing bosses point inboard, leading bosses
   outboard, so the whole stack (centre spacer ≈14, 6 thrust washers, 2 outboard
   sleeves ≈7) is continuous carrier-to-carrier (Rev 003a). Fork shape keeps
   each idler centred on the belt. Trailing arm has a 25 mm slot + a motorcycle-style
   chain adjuster (Rev 002b; Rev 004a hardware): M6 lifting eye nut on each axle
   end (Ø20 eye rides the Ø15 axle — replaces the drilled-and-tapped block), M6
   draw bolt through a lug welded to the plate face — advancing the bolt draws
   the axle rearward.
4. **Coil-over shocks ×2** — run **outboard of the carrier plates** (|z| = 94;
   Rev 002c/003 — with the measured 4 mm legs the carriers sit at 74, leaving
   only 15 mm inboard of them, so the Rev 002 inboard placement doesn't fit):
   upper eye on a 40×6×55 tab stub lap-welded to the carrier OUTER face (eye at
   (±51, −8.5) from the hub centre — Rev 008, essentially Rev 004's (±53, −9)),
   lower eye on an M8 through-bolt (eyes measured Ø8 — Rev 004b) + ≈45 mm
   spacer sleeve through both arm-fork plates at **a = 0.433·C = 53.7** on the bar
   centreline — clears the idler wheel by 12.3 mm (guarded) and lands the true
   kinematic **MR = 0.4327**, the design point of the owner's purchased springs.

### Design risks (mitigations are mandatory, see blueprint §0)
- **Belt derailment** — articulation changes belt path length (~6 mm through travel).
  Mitigated by ±15° travel limit, spring preload, and correct tensioner setting
  (10–15 mm mid-span sag).
- ~~Belt-to-fork fit~~ — resolved in Rev 003: both fork gaps re-measured at
  **140 mm**, so the 118 mm belt has 11 mm per side front and rear (the earlier
  120 mm front reading, which left 1 mm/side, was wrong).
- ~~Anti-rotation~~ — resolved in Rev 002: the carriers bolt straight to the fork legs.

---

## Sheet-0 datums — updated 2026-07-24 (Rev 005b: belt + hub measured for real)

Everything is parametric on these.

| Datum | What | Typical* | Measured |
|---|---|---|---|
| track | Belt: cord-line circumference × width × pitch × links | — | **1080 × 118 mm, 60 mm pitch, 18 links** (2.1 kg, Yonggu) — pitch **confirmed by direct measurement 2026-07-24** |
| lugs | Drive lugs (they are NOT edge guide rows) | — | **Pyramid PAIRS astride the centreline**: 22 mm gap between the pair, each 15 tall, base 25 along the belt, pair spans ~105 across |
| A | Idler axle centre-to-centre | 230–300 | **235.9 — solved** (cord Ø172 at the 9T sprocket; idler tread rides the belt face IN the 22 mm lug gap: wrap radius D/2 + 6) |
| B | Hub centre height above idler axle line | 150–200 | **170** |
| D | Idler wheel OD | 90–120 | **108** (WJ wheel) |
| G | Idler bearing bore | 15–20 | **15** — bearings are **6302-2RS (15×42×13)**; caliper read 14.86 = 15 nominal |
| sprocket | Printed drive sprocket (Rev 008) | — | **Drum = cut rim floor Ø149 × 20.5** (flanges ground off; tape check 468 mm) + rib 18×**5.44** + **9 T-teeth** (51 across × 20 thick, blades to Ø130); wheel Ø160, cord Ø172, tooth marks every **55.8 mm on the rib top** (40°). Lug/blade tips sweep Ø130 over the **measured Ø123 casing** — 3.4 mm, guarded |
| fork | Fork-leg inner gap (front / rear) | — | **140 / 140** (re-measured 2026-07-20, Rev 003 — was 120/140) — leg thickness **4** |
| axle | Hub-motor axle | — | **Ø10, flatted, static** — carrier plates slot onto it (torque-arm style) |
| ~~F~~ | ~~Belt inner width between guide lugs~~ | — | **Superseded**: no edge guide rows exist. The working channel is the **22 mm gap between the lug pairs** — the idler tread band (~20 wide; the 58 is its hub boss), the kit wheel's rib, and our printed rib all ride in it (Rev 007 correction) |
| lug_h | Drive-lug (pyramid) height | — | **15 measured** (2026-07-24; was 20 conservative) |
| H | Idler hub width | 40–60 | **58** (57.85) |
| T | Belt carcass thickness | 8–14 | **~12** (confirmed) |

\* sanity-check ranges only, never for cutting.

**Derived (all exact, from the .scad echoes, Rev 008):** `A = 235.9` · `P = B − 38 = 132` ·
`C = 123.9` (arm length) · neutral droop `17.9°` · wheel travel `+31.8 / −29.2 mm` at ±15° ·
shock station `a = 0.433·C = 53.7` (bar axis) · upper shock eye at `(±51, −8.5)` from hub centre ·
keel centre `89.9` below hub centre (Ø12×1.5 tube, in the Rev 004 window) · motion ratio `MR = 0.4327` (true kinematic) ·
carrier planes `|z| = 74` (both pods) · pivot axle stack `≈182` → **M16 × 195, 45 mm thread one end**
(both pods; smooth shank 150 clears all bushings, 4 mm margin) · shock plane `|z| = 94` (outboard) ·
sprocket: 9 stations × 40°, rib top Ø159.9, cord Ø171.9 · lug/blade tips to casing `3.4` (guarded).

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
| Spring rate | `k [N/mm] ≈ 2.1 × (kg per pod, loaded)`; N/mm × 5.7 ≈ lb/in (Rev 008: true kinematic MR = 0.4327 at a = 0.433·C — the owner's purchased "100 kg / 8.5 mm" units were sized for ~0.435 and still fit) |

Spring quick table (weight per pod, vehicle loaded with rider):
30 kg → ~360 lb/in · 40 kg → ~480 lb/in · 50 kg → ~600 lb/in · 60 kg → ~720 lb/in.
Buy one spring a step softer and one stiffer at the same time. The upper tab is welded
*after* the shock is in hand, so exact length has tolerance — verify placement in the
OpenSCAD model by setting `shock_ee`.

---

## Build order (summary — full per-component instructions in blueprint §9.1–§9.8, test protocol §10)

1. Strip one donor pod; photograph/measure the internal frame + anti-rotation (datum J).
2. Fill in datums → update `.scad` → print the `plates` layout 1:1 as a drilling template → cut 10 flat-bar rectangles (4 arm bars, 2 carrier strips, 4 tab stubs) with straight cuts only.
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
  |z| = 74, axle stack ≈182 → **M16 × 195** ×2, keel tube 148 + rod ≈172 ×2,
  shocks outboard at |z| = 94. The 1 mm/side front belt-fit risk is gone
  (11 mm/side). All clearance guards PASS (spacer margin actually improves,
  Ø25 → Ø22).
- **Rev 003a** (2026-07-20) — **full 3D collision audit** (owner spotted the first two, the audit found the rest). Five fixes, all now guarded with PASS/WARN echoes in the .scad:
  1. **Pivot stack made continuous.** The arm pack (~92 wide) never reached the carrier inner faces (148 apart) — ~29 mm of bare axle per side meant the nylock had nothing to snug against and the arms could drift sideways. The 25-long bosses now point *inboard* on the trailing fork and *outboard* on the leading fork (at the scissor interface there is only a 1.5 mm washer gap — bosses can't face each other there); centre spacer shrinks ≈60 → **≈14**, two new **outboard sleeves ≈7** close the chain to the carriers, thrust washers 4 → **6**. All three tube pieces cut at dry-stack.
  2. **Shock through-bolt vs idler wheel:** at a = 0.68·C the lower bolt passed 12 mm *inside* the Ø108 wheel. Moved to **a = 0.485·C** (4.1 mm clear, guarded). MR 0.57 → 0.41.
  3. **Shock angle/coil vs carrier:** at 57° the coil spring (Ø~44) overlapped the carrier tongue edge and tab foot. **θ = 68°**, tab weld foot re-aimed at the hub boss, carrier tab lobe simplified — coil clears by 7.5 mm (guarded), and the steeper line recovers MR to **0.45** (springs ≈2.15×kg/pod, e.g. ~490 lb/in at 40 kg).
  4. **Cross-brace vs idler wheel:** the brace at a±25 also passed through the wheel — moved inboard to x = 28..58 (7 mm clear, guarded).
  5. **Keel vs arm plates:** the keel at −104 ran through the Ø64 plate boss discs (they span −100..−164). Plate boss disc slimmed to **Ø44**, keel tube **Ø16 → Ø12×1.5**, raised to −100 — 4 mm to the sprocket disc and 4 mm to the boss disc, both articulation-invariant (the disc is centred on the pivot), guarded. Shock-bolt Ø30 lobe added to the plate profile (the Ø10 hole was <1 mm from the tapered edge at the new station).
- **Rev 004 (flat-bar edition)** (2026-07-21, owner request) — **every plate becomes off-the-shelf rectangular flat bar**: straight cuts + drilled holes only, no laser/waterjet, ~$15–35 of steel. **Arms:** plain 40 × ¼″ bars (trailing ≈185, leading ≈166). To suit the 40 mm width: lower shock bolt onto the bar centreline (was y = +18), station a → **0.46·C = 54.0** (4.4 mm wheel gap, guarded), **θ = 72°** (coil clears the carrier strip by 5.9 mm, guarded), cross-brace at y −18..−6, upper eyes at **(±53, −9)**; MR ≈ 0.44, springs ≈2.3×kg/pod (~655 lb/in worked example — the ordered 100 kg/8.5 mm shocks still fit). **Carriers:** 50 × 6 strip ≈225 (axle slot, M8, pivot, keel all on centreline) + two 40 × 6 × 55 tab stubs lap-welded on the OUTER face at hub level. Side benefits: keel-to-arm gap 4 → 6 mm; no tip rounding needed (bar half-width 20 < r34 lug wrap). All guards PASS. Backup of Rev 003a kept at `../TrackScooter-backup-rev003a`.
- **Rev 005 (real-belt sprocket)** (2026-07-24) — belt photographed + measured by the owner:
  the drive lugs are **pyramid pairs astride the centreline** (22 mm gap, 15 tall, base 25,
  pair ~105 across), not edge guide rows — the F = 62 "clear channel" never existed. The
  matched kit drive wheel (Ø16 bore, Ø188 over teeth) works by running an 18-wide rib through
  the gap. Sprocket model rebuilt: belt face rides a printed rib, cord circle = integer
  stations × 60 pitch (this is a hard constraint, not a choice); idler wrap radius corrected
  to the lug tips. Keel rehomed below the arm bar (its old window closed).
- **Rev 005b (kit-replica wheel + suspension re-tune)** (2026-07-24) — hub rim measured
  **35 wide** (was assumed 60): the lug pair overlaps the rim by only 6.5 mm/side, so the
  printed sprocket becomes a near-copy of the kit wheel on the Ø165 drum: **10T × 36°,
  rib 18 × 7, T-teeth 51 × 20 (root +5/side), blades to Ø149 in the free air beside the
  rim, no drum pockets**. The 1080 belt around the corrected (bigger) wraps solves
  A = 178 (was 222–260), shortening the arms — fixed keeping the owner's Ø108 idlers,
  belt, shocks and springs: **drop 38 → 60** (old ≤42 cap was the keel window, gone),
  **a = 0.46·C → 0.38·C** (bolt clears the wheel by 8.6 mm; MR lands 0.436 ≈ the 0.435
  the springs were bought for), **cross-brace 28..58 → 20..50**. All 15 guards PASS.
  Explainer diagrams (to scale): https://claude.ai/code/artifact/2c1f69e1-ae04-409e-b36e-10e408f62c0e
- **Rev 005c (11-tooth wheel — lug inner face is vertical)** (2026-07-25) — owner measured
  the lug's inner face at ~90°: the full 15 mm height arrives immediately, so the 10T
  wheel's 7 mm of headroom over the rim fails on contact. Sprocket: **11T × 32.7°, rib
  18 × 16.54** (face Ø198.1, cord Ø210.1, tooth marks every 56.6 on the rib top, blades
  to Ø168) — 16.5 mm headroom clears the lugs everywhere by 1.5. Re-solve A = 160.2;
  re-tune: **drop 60 → 55** (the 11T rib sweeps r = 99; the pivot centre spacer clears
  it by 5.0 — new guard added), a = 0.38·C (bolt clears wheel 2.2), **cross-brace
  20..50 → 17..41** (clears 2.5). MR = 0.438 — purchased springs still fit. All 16
  guards PASS.
- **Rev 006 (cut the rim)** (2026-07-25) — owner: the rim ring hangs on **spokes across
  an air gap** (no magnets under it), so the flange walls can be ground off, leaving the
  untouched factory tunnel floor as the drum: **Ø149 × 20.5** — narrower than the 22 mm
  lug gap, so lugs and wheel body never share space. First cut-rim wheel: 10T, rib 15.
- **Rev 007 (idler rides IN the lug gap — Rev 004 returns)** (2026-07-25, formerly
  numbered 006b) — owner: the idler's **tread band fits between the pair of lugs** and
  rolls on the belt face (the measured 58 is its hub boss). `ri_belt` = D/2 + T/2 = 60
  again — the Rev 005 "short pod" was an artifact of the lug-tip assumption. A solves
  220.8; **full Rev 004 suspension restored** (drop 38, brace 28..58, keel in window,
  travel ~±29, a = 0.433·C → MR 0.4355). Idler drawn stepped (Ø108 tread + slim boss).
  Archived: `archive/rev007-cut-rim-10T`.
- **Rev 008 (9T — owner's low-rib insight + casing measured)** (2026-07-25) — with the
  drum through the lug gap, rib height is quantized only by the whole-teeth rule; the
  owner's "~6 mm rib" is the **9T mesh: rib 5.44**, wheel Ø160, cord Ø172 (+22 % launch
  force vs 11T, ~10 % slower than 10T). Gate: lug/blade tips sweep Ø130 — **casing
  measured Ø123** → 3.4 mm, new guard added (`casing_d`). A = 235.9 — longest pod of
  any revision; margins grow everywhere (bolt 12.3 / brace 12.2 / spacer 41). 17/17
  guards PASS. **Design of record (this file set).**
- **Rev 009 (the no-cut twin)** (2026-07-25) — comparison variant built FROM the Rev 008
  file with one decision flipped: rim stays factory Ø165×35 → 11T, rib 16.54, wheel
  Ø198, cord Ø210, A = 203.5, keel below the arm bar, brace 22..52; all guards pass
  with thin margins (bolt 3.6 / brace 3.0 / coil 2.0). Zero motor modification — the
  escape hatch. `archive/rev009-uncut-11T`.
- *(Numbering note: the revision line was renumbered on 2026-07-25 for clean order —
  what was briefly called 006b/007 is now 007/008.)*

## Revision folders

| Folder | Design | Motor mod |
|---|---|---|
| *(repo root)* | **Rev 008 — 9T on the cut rim (design of record)** | grind flanges |
| `archive/rev009-uncut-11T/` | Rev 009 — 11T, rim untouched (comparison twin) | none |
| `archive/rev008-cut-rim-9T/` | Rev 008 snapshot (complete file set) | grind flanges |
| `archive/rev007-cut-rim-10T/` | Rev 007 — 10T fallback if 9T proves tight | grind flanges |
| `archive/rev005c/` | Rev 005c — 11T era before the idler fix (= git 83ee983) | none |
| `archive/rev003a/` | pre-flat-bar historical snapshot | — |

## Open items

- [x] Take Sheet-0 measurements — track, A (solved), B, D, G, H, sprocket 10T, fork gaps, axle
- [x] Measure: **fork leg thickness** — 4 mm (2026-07-13; axle/keel/shock placement updated, Rev 002c)
- [x] Re-measure fork gaps — **140 front and rear** (2026-07-20, Rev 003; belt-fit risk closed, 11 mm/side)
- [x] Measure: **lug height** — 15 mm, base 25, pitch 60 confirmed, pair spans ~105, gap 22 (2026-07-24, Rev 005/005b)
- [x] Plug datums into `.scad`, confirm fit (all 15 clearance checks PASS at full bump — Rev 005b)
- [x] Lug height at 6.5 mm from its inner edge — measured ~15 (inner face vertical); moot since Rev 006: the cut drum passes through the lug gap
- [x] Motor casing OD — **measured Ø123** (2026-07-25); lug/blade tips sweep Ø130, 3.4 mm clear, guarded in the .scad
- [ ] **Cut the rim flanges** (Rev 008 prerequisite): confirm floor width ≥ 20 at several spots and ring wall ≥ ~3 first; grind flush WITHOUT touching the floor; deburr
- [ ] **After the cut:** tape the bare floor — circumference must read **468 mm** (= Ø149). Send the number before printing.
- [ ] Print the Rev 008 sprocket halves (ABS, axis-vertical orientation, teeth as continuous layer planes; 9 teeth, marks every 55.8 mm on the rib, 40° apart); halves bolt to each other through the spoke gaps
- [ ] Kit reference wheel (Ø16 bore, Ø188) arriving by post — when it lands, sanity-compare its tooth spacing/shape against the print
- [ ] Export final `plates.dxf` (Rev 008: plate layout ≈ Rev 004 again — drop 38, brace 28..58; only the shock bolt hole moved to 0.433·C = 53.7)
- [x] Shock length: B=170 → **150 mm eye-to-eye, 30 mm stroke (not longer)**; springs as purchased fit Rev 005b (MR 0.436)
- [ ] Order idler axles: 15 mm (thru-axle or shaft + collars)
- [ ] Blueprint sheets (web artifact + local HTML/PDF) still draw **Rev 004c geometry** — the local HTML/PDF carry a Rev 008 revision slip; full sheet redraw pending. Much of 004c is valid again (drop 38, brace 28..58, keel window) — main deltas: sprocket, A, shock station
- [ ] Confirm vehicle-side details: total loaded weight, 2 vs 4 pods (motors: 250 W × 3-speed each — startup assessment 2026-07-25: fine on flat/firm, marginal on soft/slopes)
