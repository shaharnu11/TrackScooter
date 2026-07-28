# Apollo Track Pod — Articulated Split-Frame Suspension

Hub-motor scooter → tracked vehicle conversion. **This root is an index only —
all working files live in the per-revision folders. Every future change lands in
`archive/rev009-uncut-11T/` and/or `archive/rev010-cut-rim-10T-final/`.**

## The two live revisions

| Folder | Design | Status |
|---|---|---|
| **[`archive/rev010-cut-rim-10T-final/`](archive/rev010-cut-rim-10T-final/)** | **Rev 010 — design of record.** Rim flanges cut (clean cut: the hub's five 4.1 mm fins arch to the tunnel floor's underside), printed 10-tooth sprocket on the Ø149×20.5 floor (rib 18×15, wheel Ø179, cord Ø191, marks 56.2 @36°). A=220.8, no keel, carriers 224. +10 % launch, biggest margins. | complete file set: scad, print model + STLs, 2D wheel blueprint, plates PDF/DXF, README, pod blueprint |
| **[`archive/rev009-uncut-11T/`](archive/rev009-uncut-11T/)** | **Rev 009 — no-cut twin.** 11 teeth on the factory Ø165×35 rim (rib 18×16.5, marks 56.6 @32.7°). A=203.5, no keel, carriers 224 (identical steel). Zero motor modification, buildable today, upgradeable to Rev 010 later. | complete file set (same layout) |

Shared facts: Yonggu belt 1080×118 @60 pitch (pyramid-pair lugs, 22 mm centre gap) ·
idlers Ø108 (tread 20.27 rides IN the gap) · M12 GB901 8.8 stud axles + Ø15×12 sleeves
(purchased) · shocks 150 mm / 100 kg-8.5 mm springs at their design point in both.

## External documents

- **Shopping list (live, robot-maintained):** [Parts to Buy — Rev 010 FINAL, images + checkboxes](https://docs.google.com/document/d/1putRc1Q8nmpfGutUm1MNZg5LL_oXczPzJIrjNoAym6Y/edit)
- **Drive-wheel explainer (to-scale):** https://claude.ai/code/artifact/2c1f69e1-ae04-409e-b36e-10e408f62c0e
- Older shopping docs / checklist sheet: archived in the same Drive.

## History

`archive/rev003a` → `rev005c` → `rev007-cut-rim-10T` → `rev008-cut-rim-9T` →
`rev009` / `rev010`. Each folder's `ARCHIVE-NOTE.txt` explains what it was and why it
was superseded. Full revision log: the README inside either live folder.
