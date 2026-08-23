# Rev 011 — threaded hardware: every nut, bolt, stud and washer

Extracted from `apollo_track_pod_blueprint.html` §7.2–§7.8 and reconciled against the
Rev 011 revision slip + `apollo_track_pod_rev011.scad`. **Two §7 sections are stale and
would make you buy the wrong parts** — see [Do NOT buy](#do-not-buy).

Nothing below class **8.8** anywhere on the pod. Grade 8 (US) = class 10.9 here.

Quantities are given **per pod** and **for both pods** (the build is two pods, one per
side). Where a source said only "2×" without saying which, the reading is noted.

---

## A · Pivot axle — Sheet 2 / §7.2, §7.3

| Item | /pod | both | Notes |
|---|---:|---:|---|
| M16 × 195 hex bolt, **part-threaded 45 mm one end only**, cl.10.9 | 1 | **2** | Owner-sourced part. Smooth shank 150 must span all 4 bushings + spacer — bushings must never ride on thread |
| M16 nylock nut | 1 | **2** | **One per bolt only** — it is a headed bolt, not a stud |
| Ø16 hardened flat washer | 2 | **4** | |
| Ø16 × Ø30 × 1.5 hardened thrust washer | 6 | **12** | Every steel face that rotates against another |

Head must be stamped **10.9**. Torque: tighten the nylock to **zero end-float, then back
off ⅛ turn** (running fit) — not to a torque figure.

An earlier shopping list said 4 M16 nylocks total; that was wrong and is corrected in
`apollo_track_pod_rev011.scad:146`.

**Substitute** (owner's fallback): M16 double-end stud × 190 + **2** nylocks per pod. The
smooth middle must still be ≥150. Prefer 8.8/B7 over A2-70 stainless; anti-seize on
stainless.

Not fasteners but part of this stack: 4 flanged bronze bushings per pod (SAE 841,
Ø16 ID × Ø22 OD × 20, flange ≈Ø28×3) → **8** for both pods.

## B · Idler axles — Rev 011, **supersedes §7.5**

Already purchased 2026-07-25 (`ARCHIVE-NOTE.txt`). Grade **8.8** GB901 double-end studs
in a Ø15 OD × Ø12 ID sleeve stack — *not* the Ø15 thru-axles §7.5 still describes.

| Item | /pod | both | Notes |
|---|---:|---:|---|
| GB901 **M12 × 110** double-end stud, 8.8 — TRAILING | 1 | **2** | Runs in the 25 mm tensioner slot |
| GB901 **M12 × 120** double-end stud, 8.8 — LEADING | 1 | **2** | Plain Ø15.4 bore |
| M12 nylock nut | 4 | **8** | Two per stud — a double-end stud has no head |
| M12 washer, ≈2.5 thick | 4 | **8** | |

Stack per side: `[Ø15 push collar 7 — trailing only, Rev 011b] + washer 2.5 + M12 nylock 11.8 + ~2 proud`. The collar is a 7 mm ring cut from the same Ø15 × Ø12 pipe as the sleeves.
Sleeves (inner tube 50.8 trailing / 66.5 leading + 2 × 6.35 rings per axle) are cut from
the 500 mm length of Ø15 OD × Ø12 ID pipe in the §7.1 steel order — cut long, file square,
fit at dry-stack.

The wheel must **spin free with zero side-play** before final nylock torque. If torquing
drags the wheel, the inner spacer tube between the 6302 inner races is missing or short.

## C · Fork mount — §7.7

| Item | /pod | both | Notes |
|---|---:|---:|---|
| M8 × 30 cl.10.9 bolt | 2 | **4** | One per fork leg: carrier 6 + leg 4 + nut |
| M8 nylock nut | 2 | **4** | |
| M10 hub-motor axle nuts | — | — | **Reused from the donor pod** — do not buy |

The carrier's Ø10.4 axle hole with flats 8.9 apart is the torque arm; the M8 into the leg
locks rotation. Rev 011 carriers have **no keel hole**.

## D · Shocks — §7.7 / §9.5

Four shocks total (2 per pod, one per arm), eyes measured **Ø8**.

| Item | /pod | both | Notes |
|---|---:|---:|---|
| M8 part-threaded bolt, ≈**135** — lower eye | 2 | **4** | Through both arm plates; eye rides the spacer sleeve; smooth shank where eye + sleeve ride |
| M8 nylock nut | 2 | **4** | |
| Ø15 OD × Ø9 ID × ≈45 spacer sleeve | 2 | **4** | In the §7.1 steel order, not a fastener |
| M8 pin/bolt ≈**35–40** + nylock — upper eye | 2 | **4** | ⚠ **Missing from §7.7** — see below |

⚠ **Gap in the published BOM:** the upper shock tab carries a Ø8.4 "eye pin hole" for an
M8 pin (`apollo_track_pod_rev011.scad:652`, and the Ø8.4 in `plates_rev011.dxf` poly 26/28),
but §7.7 lists only the fork bolts and the *lower* shock bolts. Length is not specified
anywhere; the tab is a single 6 mm plate, so head + shock eye + 6 + washer + nylock lands
around 35–40. **Measure it at the §9.5 fitting** with the real shock eye in hand.

Confirm the lower bolt length at §9.5 too — §7.7 only says "≈135".

## E · Belt tensioner — **Rev 011b PUSHER** (supersedes the §7.6 / Rev 004a pull-type)

**Why it changed (2026-08-24):** the pull-type draw-bolt head sat ~44 mm behind the axle,
dead centre of the belt wrap — where the drive-lug tips sweep only 39 mm from the axle.
The old guard checked the belt *face*, not the teeth; the head touched the lugs on the
bench. The forward side of the idler is never wrapped, so the hardware moved there:
a block welded **forward** of the slot, and the M6 bolt now **pushes** the axle rearward.

| Item | /pod | both | Notes |
|---|---:|---:|---|
| M6 × **45** full-thread push bolt, cl.8.8 or better | 2 | **4** | Cut the purchased ×60 down to 45 — full length fouls the lower shock sleeve near zero take-up. Threads through the block; loaded in **compression** |
| M6 jam nut | 2 | **4** | Locks against the block's **forward** face once tension is set |
| M6 plain nut, welded to the block's forward face | 2 | **4** | The thread the bolt runs in (or skip it: drill the block 5.0 and tap M6) |
| ~~M6 lifting eye nut DIN 582~~ | — | — | **No longer needed** — replaced by the Ø15 push collar. Keep as spares |

The bolt tip bears on the **Ø15 × 7 push collar** clamped on the stud between washer and
nylock (cut from the §7.1 pipe — not a fastener). The bolt is a *positioner*, not a
retainer: the torqued M12 nylocks hold the axle, exactly as before. Adjust with nylocks
snug, both sides evenly, jam, then torque to 105 N·m.

## F · Consumables that are threaded — §7.8

- **2 × M6 grease zerks** + EP2 lithium grease (+ gun). Check the zerk thread really is M6.
- Nylock + hardened washer **assortment**, M8/M10, class 10 / Gr8 — for the fitting-up you
  will inevitably redo.
- **Medium (blue) threadlocker**; paint pen for torque witness marks.

---

## Do NOT buy

| Superseded item | Why |
|---|---|
| M8 threaded rod ≈172 + 4 nuts + washers — "keel standoff" (§7.6) | **Keel is deleted** in Rev 011 (`use_keel = false`, `apollo_track_pod_rev011.scad:363`). The fork legs box the carriers |
| M8 keel bolt through the carriers | Carrier strips are 220 with **no keel hole** |
| 4 × M15×1.5 fine nuts + ~8 Ø15 washers (§7.5) | Idler axles are now **M12 studs**. The Ø15 shaft is kept only as an emergency spare |
| A second M16 nylock per pivot bolt | The bolt has a head — one nut per bolt |
| Anything below class 8.8 | Unmarked hardware-store rod/bolts are out |

## Torque

| | |
|---|---|
| M8 cl.10.9 | 30 N·m |
| M10 (hub axle, reused nuts) | 60 N·m |
| M12 (idler axle nylocks) | 105 N·m — but only after the wheel spins free with zero side-play |
| M16 pivot nylock | zero end-float, then back ⅛ turn |

Paint-pen witness marks on everything. Retorque at 1 h / 5 h / then every 20 h (§10).

---

## Shopping total, both pods

```
M16 × 195 part-threaded cl.10.9 bolt ........  2
M16 nylock nut ..............................  2
Ø16 hardened flat washer ....................  4
Ø16 × Ø30 × 1.5 thrust washer ............... 12
GB901 M12 × 110 stud, 8.8 ...................  2   (purchased)
GB901 M12 × 120 stud, 8.8 ...................  2   (purchased)
M12 nylock nut ..............................  8
M12 washer ..................................  8
M8 × 30 cl.10.9 bolt ........................  4
M8 part-threaded bolt ≈135 ..................  4
M8 pin/bolt ≈35–40 (upper shock eye) ........  4   ← not in §7.7, measure at §9.5
M8 nylock nut ............................... 12
M6 × 60 full-thread bolt 8.8 (cut to 45) ....  4   push bolts — Rev 011b
M6 jam nut ..................................  4
M6 plain nut (weld to pusher blocks) ........  4
M6 lifting eye nut DIN 582 (eye Ø20) ........  0   ← Rev 011b: NOT needed, keep as spares
M6 grease zerk ..............................  2
M10 hub axle nut ............................  reused from donor pod
```

Source of truth is the model, `apollo_track_pod_rev011.scad`, plus the revision slip at
the top of the blueprint — **not** the §7 prose, which still describes Rev 004c for the
idler axles and the keel.
