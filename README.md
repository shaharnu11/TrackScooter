# Apollo Track Pod — Articulated Split-Frame Suspension

Hub-motor scooter → tracked vehicle conversion. **This root is an index only — all working
files live in the per-revision folders. Every future change lands in the live revision below.**

## Live revision

**[`archive/rev011-uncut-11T-lowB/`](archive/rev011-uncut-11T-lowB/) — Rev 011, the design of record.**

No grinder: the hub rim stays factory Ø165×35, driven by a printed 11-tooth sprocket
(rib 18×16.5, wheel Ø198, cord Ø210, tooth marks every 56.6 mm on the rib). The defining
change is that the hub sits **20 mm lower** over the idler axle line (B = 150), which stops
the 1080 mm belt wasting length on its two diagonals:

| | value |
|---|---|
| Ground contact | **231.2 mm** (was 203.5 — +13.6 %) |
| Ground pressure @ ~130 kg | ~0.24 kg/cm² |
| Wheel travel | +30.7 / −29.2 mm at ±15° |
| Motion ratio | 0.4351 — the purchased springs' design point |
| Cut lengths | carrier 220 · trailing arm 184 · leading arm 166 (rear corners chamfered 10×10) |
| Guards | all PASS, zero warnings |

Folder contents: model (`apollo_track_pod_rev011.scad`), printable sprocket
(`sprocket_print.scad` + `stl/`), 2D wheel blueprint, plate cutting sheet + DXF, pod
blueprint, README, archive note.

## Shared facts

Yonggu belt 1080 × 118 @ 60 pitch (pyramid-pair lugs, 22 mm centre gap) · idlers Ø108
(tread 20.27 rides *in* the lug gap) · M12 GB901 8.8 double-end stud axles + Ø15×12 sleeve
stacks (purchased) · shocks 150 mm / 100 kg-8.5 mm springs · no keel (the fork legs box the
carriers) · motor casing Ø123, hub fins 4.1 mm arching to the tunnel-floor underside.

## External documents

- **Shopping list (live, robot-maintained):** [Parts to Buy](https://docs.google.com/document/d/1putRc1Q8nmpfGutUm1MNZg5LL_oXczPzJIrjNoAym6Y/edit)
- **Drive-wheel explainer (to-scale):** https://claude.ai/code/artifact/2c1f69e1-ae04-409e-b36e-10e408f62c0e
- Older shopping docs / checklist sheet: archived in the same Drive.

## History (frozen — do not edit)

| Folder | What it was | Why superseded |
|---|---|---|
| `archive/rev010-cut-rim-10T-final/` | the grinder path: cut rim Ø149, 10T, contact 220.8 | retired 2026-08-10 — Rev 011 beats it on the factory rim |
| `archive/rev009-uncut-11T/` | Rev 011's parent: same wheel, B = 170, contact 203.5 | hub lowered in Rev 011 |
| `archive/rev008-cut-rim-9T/` | 9T max-torque wheel | excluded by the hub-fin measurement |
| `archive/rev007-cut-rim-10T/` · `rev005c/` · `rev003a/` | earlier eras | see each folder's `ARCHIVE-NOTE.txt` |

Each folder's `ARCHIVE-NOTE.txt` explains what it was and why it was superseded.
