# Apollo Track Pod — Articulated "Split-Frame" Suspension Mod

**Rev 001b · 2026-07-12 · Status: key datums measured and baked in (track, sprocket, idler/bearing); belt-clearance-at-bump fix applied; F + lug profile still to measure**

Converts a rigid bolt-on rubber-track pod (spoked drive sprocket on a hex axle, two
bearing-mounted lower idlers, lugged rubber band — sold as a wheel-replacement track
for mowers / small ATVs / mobility platforms) into an independently articulating
suspension: a central pivot below the drive hub, a leading and a trailing arm, and
two coil-over shocks. Each lower idler gets ~±0.26·C mm of independent vertical travel
(≈ ±39 mm on a typical pod) instead of zero.

---

## Project files

| File | What it is |
|---|---|
| **Blueprint (web)** | https://claude.ai/code/artifact/8435d971-16c0-4a02-9ff1-7adc27d6350e — 7 drawing sheets, BOM, fabrication specs, assembly sequence, test protocol. Readable, always-current version of record. |
| `apollo_track_pod.scad` | Parametric OpenSCAD 3D model (companion to the blueprint). Assembly / exploded / flat-plate modes, articulation animation, DXF + STL export. Verified rendering in all modes. |
| `README.md` | This file. |

### Using the OpenSCAD model

```bash
open -a OpenSCAD apollo_track_pod.scad     # OpenSCAD is installed via Homebrew
```

- `render_mode = "assembly"` — full pod; `lead_angle` / `trail_angle` sliders (−15…+15) articulate the arms; `animate = true` + View→Animate (FPS 20, Steps 100) cycles the suspension.
- `render_mode = "exploded"` — assembly reference.
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

1. **Carrier plates ×2** (6 mm A36, mirrored) — the new backbone. Ride on the vehicle
   axle via their own bearings (6205-2RS on an axle sleeve), so the axle spins the
   sprocket while the carriers stay still. Boxed together by the axle sleeve (top),
   the pivot axle (middle), and one **M8 keel standoff below the pivot** (bottom).
   An **anti-rotation lug** at the top links to the chassis — mandatory, otherwise
   drive torque spins the whole pod. The keel standoff sits **between the sprocket's
   swept disc and the pivot boss** (Rev 001b) — nothing may hang low enough to touch
   the belt's bottom run when the arms are at full bump.
2. **Central pivot axle** — M20×1.5 class-10.9 bolt through the carrier tongues,
   30 mm above the idler axle line (Rev 001b: raised from 20 for belt clearance).
3. **Leading + trailing arms** — fork weldments (2 plates each, ¼″ A36) nested on the
   pivot like scissors; 4 flanged SAE 841 bronze bushings (Ø20×Ø25). Fork shape keeps
   each idler centred on the belt. Trailing arm has a 25 mm slot + jack bolts = belt tensioner.
4. **Coil-over shocks ×2** — run **outboard of the carrier plates**: upper eye on a tab
   welded to the carrier outer face, lower eye on a Ø10 through-bolt + spacer sleeve
   through both fork plates at 0.68·C, leaning ~57° to the arm.

### Design risks (mitigations are mandatory, see blueprint §0)
- **Belt derailment** — articulation changes belt path length. Mitigated by ±15° travel
  limit, spring preload, and correct tensioner setting (10–15 mm mid-span sag).
- **Anti-rotation** — the torque link to the chassis is not optional.

---

## Sheet-0 datums — measured 2026-07-12 (remaining blanks: F, lug profile, J)

Everything is parametric on these.

| Datum | What | Typical* | Measured |
|---|---|---|---|
| track | Belt: inner circumference × width × pitch × links | — | **1083 × 118 mm, 60 mm pitch, 18 links** (2.1 kg) |
| A | Idler axle centre-to-centre | 230–300 | **≈ 243 — solved from track_len** (model bisects the belt path) |
| B | Hub centre height above idler axle line | 150–200 | **170** |
| D | Idler wheel OD | 90–120 | **108** (WJ wheel) |
| G | Idler bearing bore | 15–20 | **15** — bearings are **6302-2RS (15×42×13)**; caliper read 14.86 = 15 nominal |
| sprocket | Drive sprocket OD | — | **180** |
| F | Belt inner width between guide lugs | 60–90 | ___ (75 placeholder) |
| lug_h / lug_w | Guide lug height / row width | — | ___ (20 / 12 placeholders — **feeds the clearance guard, measure!**) |
| H | Idler hub width | 40–60 | **58** (57.85) |
| T | Belt carcass thickness | 8–14 | ___ (12 placeholder) |
| J | Vehicle axle Ø + stock mounting/anti-rotation interface (disassemble one pod, photograph everything) | — | ___ |

\* sanity-check ranges only, never for cutting.

**Derived:** `P = B − 30` (pivot drop below hub centre) · `C = √((A/2)² + 30²)` (arm length)
· wheel travel `≈ +32/−30 mm` at ±15° · shock station `a = 0.68·C` · motion ratio `MR ≈ 0.57`.

**Idler axle:** the 6302 bearings take a **Ø15 mm axle** — a 15×100 MTB thru-axle
(M15×1.5) or a 15 mm hardened shaft + collars, per the sourcing notes.

**Belt-clearance guard (Rev 001b):** every render echoes a PASS/WARN line per hanging
part (carrier tongue, keel, pivot spacer, boss) against the belt/lug line at full bump.
All must read PASS with ≥5 mm before cutting steel — re-check after measuring lug_h/F.

---

## Shock (suspension) purchasing spec

Two per pod, standard "e-scooter / mini-moto rear shock" type:

| Spec | Requirement |
|---|---|
| Type | Coil-over, oil-damped (not friction/spring-only), adjustable preload, replaceable spring |
| Eye-to-eye length | **≈ 0.85–0.9 × B** → B 145–160 → 125/135 mm · **B 160–180 → 150 mm** (design default) · B 180–200 → 165 mm |
| Stroke | ≥ 30 mm (uses ~24 mm at full ±15°; check short shocks' stroke in the listing) |
| Eyelet bore | Ø10 mm (or with reducer bushings) |
| Installed length | free length − ~10 mm sag — use this when positioning the upper tab |
| Spring rate | `k [N/mm] ≈ 1.35 × (kg per pod, loaded)`; N/mm × 5.7 ≈ lb/in |

Spring quick table (weight per pod, vehicle loaded with rider):
30 kg → ~230 lb/in · 40 kg → ~310 lb/in · 50 kg → ~390 lb/in · 60 kg → ~460 lb/in.
Buy one spring a step softer and one stiffer at the same time. The upper tab is welded
*after* the shock is in hand, so exact length has tolerance — verify placement in the
OpenSCAD model by setting `shock_ee`.

---

## Build order (summary — full detail in blueprint §9–10)

1. Strip one donor pod; photograph/measure the internal frame + anti-rotation (datum J).
2. Fill in datums → update `.scad` → export `plates.dxf` → laser-cut 8 plates.
3. Press bushings; dry-stack the pivot (Sheet 2 order); cut spacer tube so idlers sit mid-belt.
4. Box carriers (keel standoff + axle sleeve/bearings); sprocket must spin free, ≥3 mm/face.
5. Locate shock mounts with shocks held at ~30% compression; tack; hand-cycle ±15°; final-weld (bushings out).
6. Paint → final assembly → fit idlers → wrap belt → tension (10–15 mm sag) → mount with anti-rotation link.
7. Test protocol: bench articulation ×50 → bench spin 5 min (belt must not walk) → loaded creep over 50 mm plank → short ridden test → retorque at 1 h / 5 h / every 20 h.
8. Only after the first pod passes: replicate for the other side (mirror carriers only).

Torque: M8 cl.10.9 — 30 N·m · M10 — 60 N·m · M12 — 105 N·m · M20 pivot nylock — zero end-float then back ⅛ turn (running fit). Paint-pen witness marks on everything.

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

## Open items

- [x] Take Sheet-0 measurements — done for track, A (solved), B, D, G, H, sprocket
- [ ] Measure the remaining datums: **F, lug_h, lug_w** (drive the clearance guard), T, J
- [x] Plug datums into `.scad`, confirm fit (all clearance checks PASS at full bump)
- [ ] Export final `plates.dxf` after F/lug/J are confirmed
- [x] Shock length: B=170 → **150 mm eye-to-eye** per the purchasing spec above; weigh corner load → pick spring rate
- [ ] Order idler axles: 15 mm (thru-axle or shaft + collars)
- [ ] Bake real numbers into the blueprint sheets (update artifact)
- [ ] Confirm vehicle-side details: total loaded weight, 2 vs 4 pods, chassis point for anti-rotation link
