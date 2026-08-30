// ############################################################################
// #  REV 011 — DESIGN OF RECORD (2026-08-10). Forked from Rev 009.          #
// #  Rim stays FACTORY Ø165x35 (no grinder) -> 11T, rib 16.54, wheel Ø198,  #
// #  cord Ø210, idlers Ø108 unchanged.                                      #
// #  THE CHANGE: B 170 -> 150. The 1080 belt spends less on the diagonals,  #
// #  so GROUND CONTACT 203.5 -> 231.2 mm (+13.6%) and the vehicle sits      #
// #  20 mm lower (the conversion had raised it ~120 mm over stock anyway).  #
// #  Cascade: drop 38->22, theta 72->80, a_frac 0.433->0.434, arm rear      #
// #  corners chamfered 10. Revs 009/010 are superseded history.             #
// ############################################################################
// ============================================================================
//  APOLLO TRACK POD — Articulated "Split-Frame" Suspension Mod
//  Parametric OpenSCAD model · Rev 004 (flat-bar edition) · 2026-07-21
//  Companion to the blueprint artifact (Sheets 0–6).
//
//  HOW TO USE
//   1. Measure your pod per blueprint Sheet 0 and set datums A,B,D,G,F,H,T below.
//   2. Open in OpenSCAD, press F5 (preview) / F6 (render).
//   3. render_mode:
//        "assembly"  full pod at ride height (set lead_angle/trail_angle)
//        "exploded"  parts separated for assembly reference
//        "plates"    2D flat layout of all steel plates -> export DXF for laser
//        "tensioner" Sheet-6 close-up: trailing-arm slot, adjuster block,
//                    draw bolt + jam nut, welded tip lug (labeled in 3D)
//   4. Animation: View > Animate, FPS 20, Steps 100, set animate = true.
//
//  CLI EXPORTS (from this folder):
//    openscad -o pod.stl        -D 'render_mode="assembly"' apollo_track_pod.scad
//    openscad -o plates.dxf     -D 'render_mode="plates"'   apollo_track_pod.scad
//
//  REV 001a DELTAS vs the concept sketch (found during 3D fit-check):
//   - Shocks moved OUTBOARD of the carrier plates (mid-plane shocks collide
//     with the sprocket). Lower eye rides on a through-bolt + spacer sleeve
//     through both fork plates; upper eye on a tab welded to the carrier
//     outer face.
//   - The 4-bolt cross-standoff circle removed (it passes through the
//     sprocket). Carriers are boxed by: axle sleeve (top) + pivot axle (mid)
//     + one keel standoff below the pivot (bottom).
//
//  REV 001b DELTAS (real measurements + belt-clearance fix, 2026-07-12):
//   - Real datums baked in: track 1083x118 (18 links x 60 pitch), sprocket
//     OD 180, idler OD 108 x 58 wide on 6302-2RS bearings (15 mm axle).
//   - Idler spacing A now SOLVED from track_len (bisection on belt path).
//   - Belt-clearance fix: at full bump the belt bottom run rises ~32 mm.
//     Keel standoff moved from 45 below the pivot (collided by ~40 mm!) to
//     between the sprocket swept disc and the pivot boss; pivot raised
//     drop 20->30; carrier pivot circle slimmed 56->48. A clearance guard
//     echoes PASS/WARN for every hanging part at bump_max each render.
//
//  REV 001c DELTA (2026-07-12): pivot raised further, drop 30->38 — lug-top
//    margin at full bump ~7.6 -> ~15 mm, steel-contact angle +18.5° -> +22°.
//    Keel moved up with it (still between sprocket and pivot boss; drop<=42
//    is the hard limit for this window). Belt-path variation through travel
//    grows 3.6 -> 5.7 mm — within tensioner range. Keel-to-boss and
//    keel-to-sprocket gaps added to the guard echoes.
//
//  REV 002 DELTAS (owner interview, 2026-07-12):
//   - The pod is a hub-motor scooter conversion: motor inside the sprocket on
//     a static Ø10 flatted axle between fork legs (front gap 120, rear 140).
//   - Carriers redesigned: fork-hung torque-arm plates bolted to the leg
//     OUTER faces (axle slot + one M8 per leg). Carrier bearings (6205),
//     axle sleeve and anti-rotation link DELETED — the fork does both jobs.
//   - Carriers now sit outside the belt width: the tongue can never touch
//     the track. Shocks moved back INBOARD (between belt edge and carrier).
//   - Belt-length solver corrected to the cord line (10T x 60 pitch = Ø191):
//     A = 222.2 (was 243 on the inner-surface assumption).
//   - FIT RISK: 118 belt in 120 front fork gap = 1 mm/side. Verify.
//
//  REV 002b DELTA (2026-07-13): Sheet-6 belt tensioner modeled explicitly.
//   The slot alone can't hold tension — the mechanism is a motorcycle
//   chain adjuster: a lug welded across each trailing fork-plate tip, a
//   small tapped ADJUSTER BLOCK riding on each protruding axle end, and an
//   M8 draw bolt through the lug threading into the block. The bolt head
//   bears on the lug's rear face, so advancing it DRAWS the axle rearward
//   through the 25 mm slot (belt tension pulls the axle forward; the bolt
//   holds it in tension). Jam nut locks against the lug. New parameter
//   tension_pos (0-25) slides the axle through its take-up; new
//   render_mode="tensioner" gives a labeled close-up of the mechanism.
//
//  REV 002c DELTAS (2026-07-13, fork legs MEASURED at 4 mm — was 30 assumed):
//   - Carrier planes move in: |z| = 64 front / 74 rear (was 90 / 100).
//   - Pivot axle shortens: stack ~162 front / ~182 rear -> M20x1.5 x 170/190
//     (was 220 / 240). Keel tube 128/148, keel rod ~152/172 (was 180/205).
//   - Shocks move back OUTBOARD of the carriers (upper tab on the carrier
//     OUTER face): with cz=64 the belt edge (59) leaves only 5 mm inboard —
//     the Rev 002 inboard placement no longer fits. Placement is now
//     automatic: shocks_inboard flag picks the side from cz vs belt width;
//     lower spacer sleeve grows to ~40. Geometry (a, theta, eye position in
//     x-y, MR) is unchanged.
//
//  REV 003 DELTAS (2026-07-20, owner changes):
//   - Pivot axle M20 -> M16 cl.10.9. Bushings 20x25x20 -> SAE 841 flanged
//     16x22x20 (flange ~Ø28x3); boss tube 32x25 -> 32x5 (ream ID 22 H7);
//     spacer tube 25x20 -> 22x16; thrust washers Ø36x20 -> Ø30x16x1.5.
//     Boss OD stays 32 — carrier window and clearance guard unchanged.
//   - Fork gap re-measured: 140 mm FRONT AND REAR (was 120/140). Both pods
//     now identical: cz=74, axle stack ~182 -> M16 x 190, keel tube 148,
//     rod ~172, shocks outboard at |z|=94. The 1 mm/side front belt-fit
//     risk is GONE (11 mm/side both ends).
//
//  REV 003a DELTAS (2026-07-20, full 3D collision audit — owner spotted the
//  first two; the audit found the rest):
//   - PIVOT STACK made continuous: the 25-long bosses now point INBOARD on
//     the trailing forks and OUTBOARD on the leading forks (they can't both
//     protrude toward the scissor interface — only a 1.5 mm washer gap there).
//     Centre spacer shrinks ~60 -> ~14; two NEW outboard sleeves (~7) close
//     the former ~30 mm/side of bare axle to the carriers; thrust washers
//     4 -> 6. Nut can now truly set zero end-float; arms located sideways.
//   - SHOCK BOLT vs WHEEL: the lower through-bolt at a=0.68C passed 12 mm
//     INSIDE the Ø108 idler. a moved to 0.485C (4 mm clear, guarded).
//     MR 0.57 -> 0.41; spring k factor 1.35 -> 2.65 x kg/pod.
//   - CROSS-BRACE vs WHEEL: brace at a±25 also passed through the idler —
//     moved inboard to x = 28..58 (7 mm clear, guarded).
//   - KEEL vs ARM PLATES: the keel at -104 ran through the Ø64 plate boss
//     discs (which span -100..-164). Plate boss disc slimmed to Ø44, keel
//     tube Ø16 -> Ø12x1.5, raised to -100: 4 mm to sprocket disc, 4 mm to
//     the boss disc — both articulation-invariant, guarded.
//   - Shock-bolt lobe (Ø30) added to the plate profile: at the new station
//     the Ø10 hole was <1 mm from the tapered top edge.
//
//  REV 004 DELTAS (2026-07-21, FLAT-BAR EDITION — owner request: build every
//  plate from off-the-shelf rectangular flat bar, straight cuts + drilled
//  holes only, no laser/waterjet profiles):
//   - ARM PLATES: plain 40 x 6.35 flat bar (trailing cut ~185, leading ~166).
//     To fit the 40 bar: lower shock bolt moves onto the bar centreline
//     (shock_y 18 -> 0), station a 0.485C -> 0.46C (keeps 4 mm wheel gap),
//     theta 68 -> 71 deg (coil clears the carrier strip), cross-brace raised
//     to y -18..-6. Upper eye lands at (~±51, -10). MR 0.45 -> ~0.435
//     (springs ~5-8% stiffer; the owner's 100 kg / 8.5 mm units still fit).
//     Bonus: keel-to-arm gap grows 4 -> 6 mm; no tip rounding needed
//     (bar half-width 20 stays inside the r34 lug wrap).
//   - CARRIERS: one 50 x 6 vertical strip, cut ~225 (axle slot, M8 hole,
//     pivot bore, keel hole all on the centreline) + TWO 40 x 6 x 55 tab
//     stubs per carrier, lap-welded on the OUTER face at hub level (17 mm
//     lap, clear of the axle slot, above the coil-top line). Symmetric.
//   - All clearance guards re-run and PASS. Steel order becomes: 40x6.35
//     flat bar ~1 m + 50x6 ~0.5 m + 40x6 ~0.25 m — no plate stock, no
//     cutting shop.
//
//  REV 004c DELTAS (2026-07-22, real hardware confirmed):
//   - PIVOT BOLT: owner sourced M16 x 195, ONE end threaded 45 long (plain
//     hex bolt, not a double-end stud). Smooth shank = 195-45 = 150, which
//     covers the farthest bushing edge (145.85 from head) with 4 mm to
//     spare — that margin falls inside the outboard-sleeve zone, not on a
//     bushing, so it's safe. Nut fully engages (163-179 within the 150-195
//     threaded zone), 16 mm proud. Needs only ONE M16 nylock per bolt (it
//     has a head) — earlier shopping lists said 4 nylocks total; corrected
//     to 2 (1/pod). Washer count (4, one each side) is unchanged.
//   - BOSS TUBE: owner sourced 31 OD x 22 ID (was 32 OD spec) -> wall 4.5
//     (was 5). Plate pivot hole 31.8 -> 30.8. Weld shelf in the 40-wide bar
//     grows slightly, 4.0 -> 4.6 mm/side. No clearance-guard impact (boss
//     OD isn't a guarded dimension). BOM/tools: Ø31 hole saw or Ø30 +
//     hand-ream/file 0.8 mm oversize.
//
//  REV 005 DELTAS (2026-07-24, printed sprocket matched to the real belt):
//   - Belt photos (Yonggu) show the drive lugs are PYRAMID PAIRS astride the
//     centreline with a 22 mm gap between them — not edge guide-lug rows.
//     The kit's Ø16-bore drive wheel (Ø188 over teeth) works by running an
//     18-wide centre rib through that gap (teeth: 15 thick, T-overhangs to
//     51 across). Owner prints the same geometry onto the hub: ABS fill of
//     the rim well flush with the Ø165 hub body (sprocket_od 180 -> 165,
//     MEASURED) + 18-wide centre rib + T-teeth.
//   - The belt rides ON THE RIB TOP, so the cord circle is Ø165 + 2*rib_h
//     + 12, and rib_h is NOT a free choice — an integer number of 60-pitch
//     stations must fit: 11T -> rib 16.54 (needs pyramid lugs <= ~15), or
//     12T -> rib 26.09 (safe for lugs to ~24). rib_h is now DERIVED from
//     sprocket_teeth. Kit wheel is 10T because its body is only ~Ø140.
//   - Idler cord radius decoupled from the sprocket (ri_belt now uses
//     lug_h + T/2: the 58-wide idler hub rides the pyramid TIPS — the F=62
//     clear channel assumed in Rev 001 does NOT exist on this belt).
//   - KNOWN CASUALTY: the bigger swept sprocket (rib top r=99 at 11T,
//     r=108.6 at 12T) eats the keel window (-90..-110). Keel guards now
//     reference the rib-top radius and will WARN/collide until the keel is
//     rehomed — decision pending.
//   - MEASURED 2026-07-24 (owner): pitch 60 CONFIRMED, pyramid lugs 15 tall,
//     base 25 along the belt -> 11T LOCKED (rib 16.54 clears lug tips by
//     1.5). Pocket between stations = 35, tooth thickened 15 -> 20 for the
//     ABS root (15 mm play left). lug_h 20 -> 15 measured.
//   - Keel rehomed BELOW the arm bar (old window closed).
//
//  REV 005b DELTAS (2026-07-24, hub rim measured 35 wide — kit-replica wheel):
//   - Rim is 35 wide, not 60: the pyramid pair (inner edges +-11, span ~105)
//     overlaps the rim by only 6.5 mm/side — the lugs pass BESIDE the hub.
//     So the belt meshes at the kit wheel's own Ø191 cord circle: 10T, rib
//     18 x 7, T-teeth (51 across, 20 thick) whose outboard blades drop to
//     full lug depth (tips sweep Ø149) in the free air past the rim edge.
//     No drum pockets needed. sprocket_w 60 -> 35, sprocket_teeth -> 10.
//   - The 1080 belt still wraps bigger radii than Rev 004 assumed (idlers
//     ride the pyramid tips: ri = D/2 + lug_h + T/2), so A solves ~178 (was
//     260) and the arm shortened. Fixes, keeping the owner's shocks/springs
//     and Ø108 idlers: drop 38 -> 60 (arm V deepened — the old drop<=42 cap
//     was the keel window, gone in 005), a_frac 0.46 -> 0.43 (MR ~0.445 vs
//     the ~0.435 the springs were bought for), cross-brace 28..58 -> 20..50.
//   - VERIFY before printing: pyramid height at 6.5 mm from its inner edge
//     must be <= 7 (only place lug and rim overlap); motor casing Ø inboard
//     of the rim <= ~Ø145 out to |z|=25.5 (blade sweep); drum really Ø165.
//
//  REV 005c DELTAS (2026-07-25, lug inner face measured ~vertical -> 11T):
//   - Owner measured the lug INNER FACE nearly 90 deg: full 15 mm height
//     right where the lug passes over the rim, so 10T's 7 mm headroom FAILS.
//     sprocket_teeth 10 -> 11: rib 16.54, face Ø198.1, cord Ø210.1 — 16.5 mm
//     headroom, lugs clear the rim everywhere by 1.5 mm. Tooth marks every
//     56.57 on the rib top (32.727 deg).
//   - Re-solve: A = 160.2. Suspension re-tuned around the bigger swept rib
//     (r=99.0): drop 60 -> 55 (pivot centre spacer clears the rib by 5.0 —
//     NEW GUARD added), a_frac stays 0.38 (bolt clears wheel 2.2, MR 0.4384
//     ~= the 0.435 the springs were bought for), cross-brace 20..50 ->
//     17..41 (clears wheel 2.5). All 16 guards PASS.
//   - Still to verify: drum really Ø165 after fill (tape 518 circumference);
//     eyeball casing clearance under the blade sweep (owner: air gap, OK).
//
//  REV 006 DELTAS (2026-07-25, rim flanges cut off — kit-replica on the floor):
//   - Owner: the rim ring hangs on spokes across an air gap (no magnets under
//     it) and the flange walls can be ground off, leaving the untouched
//     factory tunnel floor as the drum: Ø149 x 20.5 wide. That drum is
//     NARROWER than the 22 mm lug gap -> lugs and drum never share space,
//     the vertical lug face stops mattering entirely.
//   - Sprocket: 10T (cord Ø191 = kit circle), rib 18 x 15.0, face/wheel OD
//     Ø179, T-teeth 51 x 20 with blades to Ø149; tooth marks every 56.2 on
//     the rib top (36 deg). +10% drive force vs the 11T (cord 191 vs 210).
//     Print = thin clamp shell on the drum + rib + teeth; half-shells bolt
//     to each other THROUGH the spoke gaps.
//   - Suspension: A = 178.1; drop back to 60, a = 0.38C (MR 0.4358 — the
//     springs' design point), cross-brace back out to 20..50. All guards
//     PASS with the fattest margins of any rev (bolt 8.6 / brace 3.7 /
//     spacer 9.5).
//   - BEFORE CUTTING (irreversible): confirm floor width >= 20 at several
//     spots, ring wall >= ~3 under the floor; grind flanges flush WITHOUT
//     touching the floor. AFTER: tape floor circumference = 468 mm (Ø149).
//
//  REV 007 DELTAS (2026-07-25, idler rides IN the lug gap — Rev 004 returns):
//   - Owner: the idler wheel's tread band fits BETWEEN the pair of lugs and
//     rolls on the belt face (the measured 58 is the hub boss, not the
//     tread). ri_belt = D/2 + T/2 = 60 again — the 005/005c "short pod" was
//     an artifact of the wrong lug-tip assumption. A solves 220.8 (~Rev 004's
//     222). idler_wheel() drawn stepped: Ø108 x ~20 tread + narrow boss.
//   - Full Rev 004 suspension restored: drop 38, brace 28..58, keel back in
//     the window at -99.5 (4.0 to the rib sweep / 6.5 to the arm bar),
//     travel +29.9/-27.3, droop 19.0 deg. a_frac 0.433 (a=50.5, bolt clears
//     8.2) -> MR 0.4355 = the springs' design point. Upper eye (+-50, -8.5)
//     ~= Rev 004's (+-53, -9). All guards PASS.
//
//  REV 008 DELTAS (2026-07-25, owner's low-rib insight -> 9T, casing Ø123):
//   - Owner: "with the rim through the lug gap, the rib only needs ~6" —
//     correct in principle; the whole-teeth rule quantizes it to 5.44 = the
//     9T mesh (6.0 itself would give 9.06 stations and skip).
//   - 9T: rib 18 x 5.44, wheel Ø160, cord Ø172 — +11% drive force vs 10T
//     (+22% vs 11T), ~10% slower. Tooth marks every 55.8 on the rib (40
//     deg). Blades still reach lug-tip depth (Ø130) beside the drum.
//   - The gate was the motor casing: lug + blade tips sweep Ø130. Casing
//     MEASURED Ø123 -> 3.4 mm clear, and the casing is rotor-side (spins
//     with the belt at the wrap -> ~zero relative rub). New guard added;
//     casing_d param replaces the old drawn-130 guess.
//   - Belt solve: A = 235.9 — the longest pod of any revision. Suspension
//     stays the restored Rev 004 set (drop 38, brace 28..58, keel in
//     window, a=0.433C): margins only grow with the smaller wheel.
//   - Per-revision archive folders started: archive/rev005c (11T uncut,
//     from git 83ee983), archive/rev007-cut-rim-10T (the 10T fallback),
//     archive/rev006-option-uncut-11T (no-grinding side study).
// ============================================================================

/* [Render] */
render_mode = "assembly"; // [assembly, exploded, plates, tensioner, bracket, part]
// render_mode="part": renders one BOM item alone (thumbnails for the §7
// shopping guide). Pick the item with the part variable below.
part = "bushing"; // [pivot_axle, arm_plates, carrier_plates, boss_tube, bushing, thrust_washer, spacer_tube, shock, shock_mounts, fork_hw, keel, draw_bolt, hardware, zerk, idler_axle, reused]
show_track    = true;
show_sprocket = true;
show_shocks   = true;
show_force    = true;  // live force gauge beside each shock (best with animate)
spring_rate   = 115;   // N/mm — owner's "100 kg / 8.5 mm" springs: 981/8.5
load_kg = 0; // [0:2:300] LOAD SIMULATOR — kg placed on THIS pod (split over its
             // two wheels). 0 = free (angle sliders work); >0 = both arms settle
             // to static equilibrium against the springs and the gauges show the
             // real standing force. Drag it live in Window -> Customizer.
animate       = false;
lead_angle  = 0; // [-15:0.5:15]  front arm, + = bump (up)
trail_angle = 0; // [-15:0.5:15]  rear arm,  + = bump (up)
tension_pos = 8; // [0:0.5:25]  trailing-axle slot position: 0 = most-forward
                 //             (fit the belt), 25 = full take-up (Sheet 6)

/* [Sheet-0 datums — measured 2026-07-12 unless marked PLACEHOLDER, mm] */
A = 260;          // idler axle centre-to-centre — FALLBACK, used only if belt_links == 0
belt_pitch = 60;  // belt link pitch, mm (listing + confirmed by sprocket)
belt_links = 18;  // link count — belt cord-line length = 18 x 60 = 1080; solves A
track_w   = 118;  // belt overall width
B = 150;   // hub centre height above idler axle line — REV 011: was 170.
           // Lowering B shortens the belt's two diagonals and hands that
           // length to the ground run: A 203.5 -> 231.2. Costs 20 mm of ride
           // height (uniform on both pods; does NOT touch belt-to-fender
           // clearance, which is set by the sprocket, not by B).
D = 108;   // idler wheel OD (WJ wheel)
G = 15;    // idler bearing bore (6302-2RS = 15)
brg_od = 42;      // idler bearing OD (6302)
brg_w  = 13;      // idler bearing width (6302)
F = 62;    // belt inner width between guide lugs — derived: H + 4 (matched set)
lug_w = 18;// guide lug row width — conservative estimate, measure
lug_h = 15;// pyramid lug height — MEASURED 2026-07-24 (was pessimistic 20).
           // Base 25 long along the belt -> 35 mm pocket between stations
H = 48.8;  // idler wheel TOTAL width — RE-MEASURED 2026-07-25 (the old
           // 57.85 was wrong). Fork plate faces derive from this (zi = H/2+1)
tread_w = 20.27; // idler TREAD BAND width — MEASURED 2026-07-25: rides the
           // 22 mm gap between the lug pairs with 0.87 mm/side clearance
T = 12;    // belt carcass thickness (confirmed ~12)

/* [Printed sprocket — Rev 006: rim flanges CUT OFF, kit-replica on the floor] */
sprocket_od    = 165;  // REV 009: UNCUT rim body  // drum OD = the tire-well FLOOR (165 - 2x8 flanges).
                       // Rev 006: owner grinds the flange walls off; the floor
                       // itself is untouched factory surface, so it stays round.
                       // VERIFY after the cut: tape circumference = 468 mm.
sprocket_teeth = 11;   // REV 009: uncut rim -> rib must out-reach the 15
                       // lugs over the rim strip -> 16.54 (11T mesh)
sprocket_w     = 35;   // REV 009: UNCUT rim width // drum width = tunnel floor width after the cut
rib_w      = 18;   // centre rib width — rides the 22 mm gap between pyramid pairs
tooth_t    = 20;   // tooth thickness, circumferential. Kit wheel uses 15, but
                   // the measured pocket is 35 (60 pitch - 25 lug base), so we
                   // spend 5 of the slack on a fatter ABS root; 15 mm play left
tooth_span = 51;   // T-tooth width across — overhangs (51-18)/2 = 16.5 per side
tooth_fil  = 5;    // root widening where the overhang meets the rib (fatigue)
rim_wall  = 4;     // cut rim ring wall thickness under the floor — visual
                   // placeholder; VERIFY >= ~3 so the ring stays stiff
shell_t   = 3;     // printed clamp-shell skin over the drum (two halves bolt
                   // to each other THROUGH the spoke gaps — real joint)
casing_d  = 123;   // motor casing OD — MEASURED 2026-07-25 (was drawn 130).
                   // Rev 008 exists because of this number: lug + blade tips
                   // sweep Ø130 at the 9T wheel, 3.4 clear of the casing
// rib height is DERIVED, not chosen: belt face rides the rib top, so an integer
// number of belt_pitch stations must fit the cord circle Ø(drum + 2*rib_h + T).
// (Rev 006: lug height doesn't constrain it at all — the 20.5-wide cut drum
// passes fully through the 22 mm gap between the lug pairs, so lugs and drum
// never share space. 10T on the Ø149 floor -> rib 15.0, face Ø179, cord Ø191.)
rib_h = (sprocket_teeth*belt_pitch/PI - T - sprocket_od)/2;

/* [Fork mount — Rev 002: carriers hang from the scooter fork legs] */
fork_gap = 140;  // inner spacing between fork legs: 140 FRONT AND REAR
                 // (Rev 003 — re-measured; both pods identical, was 120/140)
leg_t    = 4;    // fork leg thickness (z) — MEASURED 2026-07-13 (was 30 placeholder)
axle_d   = 10;   // hub-motor axle Ø (flatted, static — motor spins around it)

/* [Rear-fork bracket — REV 011d (owner, 2026-08-29)] */
// The REAR fork measured for real: two parallel 4 mm plates, INNER gap
// 117.7 = the belt width — they touch. The legs get CUT just before the
// axle groove (65 mm of flat leg remains, 55 tall) and the pod hangs from
// a bracket per side instead. MERGED (owner, 2026-08-29): bracket blade
// and shock tab stub are ONE plate per side — the blade carries the shock
// eye hole, so the rear pod has no separate stubs (the front pod keeps
// Rev 011c stubs until its fork is dealt with). Two DISTINCT plates, mark
// L/R, both 40x6 bar + a 65x55x6 bolt pad welded on the front:
//   TRAILING side (+z): 262 long — key at 190 from the front end, Ø8.4
//     shock eye at 242 (= +52.06, +2.44 of the axle), 20 end margin.
//   LEADING side (-z): 210 long — key at 190, eye at 138 (= -52.06).
// The plate slides onto the hub axle against the carrier outer face
// (two keyed plates, clamped by the hub nut) and bolts to the leg stub
// with 4xM10 through 17 mm of packing (6+6+5). New axle sits 125 behind
// the cut line at the old axle height (20 above the leg bottom edge) ->
// the wheel moves 55 rearward; the Ø222 belt arc clears the stub's cut
// edge by ~14. Shock eye pin cantilevers from the plate through washers
// to the shock plane, as the stub's did. Bolt first, weld at final fit.
use_bracket   = true;   // render + guard the rear-fork bracket
brk_t         = 6;      // bracket plate thickness
brk_blade_w   = 40;     // blade width (the 40x6 bar)
brk_cut_x     = 125;    // axle centre -> fork CUT LINE (forward, -x)
brk_pad_l     = 65;     // leg stub length past the cut line (bolt zone).
                        // NO PAD (owner review, 2026-08-30): the stepped
                        // pad had a 6 mm void under the lower bolt row and
                        // its upper row clashed with the blade's top edge.
                        // Both M10 rows now sit INSIDE the blade band:
                        // 2x2 pattern 35 x 14, rows 13 and 27 up the leg
                        // (y = -7/+7 of the axle line), all four bolts
                        // through leg 4 + packing 11 + blade 6 = 21.
brk_leg_h     = 55;     // fork leg height (MEASURED 2026-08-29)
brk_axle_up   = 20;     // axle centre above the leg BOTTOM edge (old height)
brk_leg_gap   = 117.7;  // rear fork INNER gap (MEASURED — belt touches!)
brk_pack      = 17;     // packing between leg outer face and BLADE (6+6+5).
                        // OWNER CATCH 2026-08-30: this went back to ~17 when
                        // the pad died — the pad used to fill 6 of it. The
                        // blade plane is FIXED at 80 by the carrier (shared
                        // keyed axle); leg outer face is at 62.85; the
                        // packing fills exactly that gap. Nominal 17.15 —
                        // cut to the MEASURED gap at fit-up.
// REMOVABLE JOINT (owner, 2026-08-30): NOTHING is welded to the fork — the
// pod comes off by undoing the 8 M10s. In place of the weld:
//   - BACKING STRIP 65x40x6 (the same 40 bar) on the leg's INNER face —
//     the belt's run stays >12 inboard of the bolt zone, so that face is
//     free. Sandwich: strip 6 / leg 4 / packing 17 / blade 6 = grip 33,
//     bolts M10 x 55 cl.8.8. Doubles the leg bearing, stops dishing/prying.
//   - the joint works as a FRICTION joint (~130 kN clamp/side vs ~160 N*m,
//     demand): keep the preload — witness marks, retorque 1h/5h/20h.
//   - a cross-tube welded BLADE-to-BLADE (pod side, Ø22x3 offcut, at the
//     bolt zone) carries side loads; it leaves the scooter untouched.

/* [Design parameters — blueprint defaults] */
plate_t    = 6.35;  // 1/4" arm fork plates
carrier_t  = 6;     // carrier plates
pivot_d    = 16;    // pivot axle (Rev 003: M16 cl.10.9, was M20)
bushing_od = 22;    // SAE 841 flanged bushing 16×22×20 (Rev 003, was 20×25×20)
boss_len   = 25;    // boss tube length (trailing bosses point IN, leading OUT)
boss_disc  = 40;    // arm FLAT-BAR width (Rev 004: plates are plain 40 mm
                    // rectangles — was the Ø44 boss disc; guards use the same
                    // half-width. 4.6 mm weld shelf beside the Ø31 boss tube
                    // (Rev 004c: tube sourced at 31 OD, was 32 — shelf grows.)
// welded offcut pieces (they carry no holes except the lug's M6 clearance, but
// they ARE part of the cut list, so Rev 011 puts them in the plates layout too)
brace_w    = 30;    // brace web width after trimming the 40 bar
brace_tr   = 50.8;  // brace web length, TRAILING fork (plates at |z|=zi_tr)
brace_ld   = 66.5;  // brace web length, LEADING fork  (nests outside the trailing)
lug_l      = 26;    // tensioner PUSHER BLOCK (Rev 011b): 26 across x 14 tall
lug_h_pl   = 14;    //   x 6 thick, hole 7 up — drill 5.0 + tap M6, or drill
                    //   6.6 and weld an M6 nut over it on the FORWARD face
draw_len   = 45;    // M6 push bolt (cut the purchased x60 full-thread down)
arm_chamf  = 10;    // REV 011: chamfer on the TWO REAR corners of every arm
                    // bar (the (-22, ±20) corners at the pivot end). They are
                    // the closest thing to the spinning sprocket at full
                    // droop; a 10 mm chamfer buys +3.6 mm there for one pass
                    // of a grinder per corner. Guarded below.
keel_od    = 12;    // keel standoff tube OD (Rev 003a: was 16 — Ø12×1.5, ID 9)
use_keel   = false; // Rev 9 (owner, 2026-07-25): keel DELETED — since Rev 002 the
                    // fork legs box the carriers (axle slot + M8 each); the
                    // keel was legacy redundancy and sat lowest in the pod.
                    // Carrier strip shrinks to 224 = same as Rev 010b.
a_frac     = 0.434; // shock bolt station as fraction of C — REV 011: re-tuned
                    // with the new arm/shock angles so the true kinematic MR
                    // lands on 0.4355, the design point of the owner's
                    // purchased 100 kg / 8.5 mm springs. a = 51.1 from the
                    // pivot; the bolt clears the idler wheel by 8.5.
shock_y    = 0;     // lower shock bolt offset from the arm axis (Rev 004: 0 —
                    // a Ø10 hole at y=18 has <2 mm edge in a 40 mm bar)
shock_ee   = 150;   // shock eye-to-eye, free
shock_sag  = 10;    // installed compression at ride height
theta      = 80;    // shock angle to arm at neutral, deg — REV 011: was 72.
                    // The flatter arm (na 20.5 -> 10.6 deg) rotated the shock
                    // line back over the carrier; without this the coil would
                    // foul the carrier strip. 80 restores an upright shock
                    // (coil clears by 4.8) and puts the upper eye at (52, +2).
bump_max   = 15;    // arm travel limit, deg (clearance guard checks this)

$fa = 4; $fs = 0.7;

// ---------------------------------------------------------------- derived --
// Belt-path length for candidate idler spacing Av, measured along the belt's
// inextensible CORD LINE (not the inner surface): 10T x 60 pitch → cord circle
// Ø191 on the Ø180 sprocket → cords ride cord_off above the rubber's inner face.
// Path = sprocket wrap + 2 tangent runs + 2 idler wraps + bottom span.
// Monotonic in Av → bisect to hit track_len.
track_len = belt_links * belt_pitch;             // 1080 — cord-line length
pitch_r   = sprocket_teeth * belt_pitch / (2*PI);// cord radius at sprocket
cord_off  = pitch_r - sprocket_od/2;             // = rib_h + T/2: cord above drum
rs_belt = pitch_r;                    // cord-line wrap radius at sprocket
ri_belt = D/2 + T/2;                  // cord-line wrap radius at idlers — the
                                      // idler's TREAD BAND rides IN the 22 mm
                                      // gap between the lug pairs, directly on
                                      // the belt face (owner confirmed; the 58
                                      // measured is the hub boss, not the tread)
function belt_len(Av) = let(
    wx    = Av/2,
    dd    = sqrt(wx*wx + B*B),
    n_ang = atan2(-B, wx) + acos((rs_belt - ri_belt)/dd),
    Lt    = sqrt(dd*dd - pow(rs_belt - ri_belt, 2)))
  rs_belt*(180 - 2*n_ang)*PI/180 + 2*ri_belt*(90 + n_ang)*PI/180 + 2*Lt + Av;
function solve_A(lo, hi, n) = n <= 0 ? (lo + hi)/2 :
  belt_len((lo + hi)/2) < track_len ? solve_A((lo + hi)/2, hi, n-1)
                                    : solve_A(lo, (lo + hi)/2, n-1);
A_eff  = (belt_links > 0) ? solve_A(120, 800, 48) : A;

half   = A_eff/2;
drop   = 22;                          // pivot sits 22 above the idler axle
                                      // line — REV 011: was 38. With B=150 the
                                      // pivot would otherwise climb into the
                                      // sprocket: the binding limit is the arm
                                      // bar's rear corner sweeping the rib at
                                      // full droop (see the arm-corner guard).
                                      // 22 keeps that at 5.8 mm with the 10 mm
                                      // chamfer, and the pivot spacer at 18.
P      = B - drop;                    // pivot drop below hub centre
C      = sqrt(half*half + drop*drop); // pivot-to-wheel arm length
na     = atan(drop/half);             // arm neutral droop angle, deg
a      = a_frac*C;                    // shock bolt station along arm
pivot  = [0, -P];

zi_tr  = H/2 + 1;                      // trailing fork inner face |z|
zi_ld  = zi_tr + plate_t + 1.5;        // leading fork inner face |z|
cz     = fork_gap/2 + leg_t;           // carrier inner face = fork-leg OUTER face
// Shock plane (Rev 002c): inboard of the carriers ONLY if there is room
// between the belt edge and the carrier inner face (there was at leg_t=30,
// cz=90; at the measured leg_t=4, cz=64 leaves 5 mm — shocks go OUTBOARD).
shocks_inboard = (cz >= track_w/2 + 24);
sz     = shocks_inboard ? track_w/2 + 14        // between belt edge and carrier
                        : cz + carrier_t + 14;  // outboard of the carrier plate
Rc     = sprocket_od/2 - 17;           // carrier disc radius
y_keel = -(P + boss_disc/2 + keel_od/2 + 4); // REV 009: 11T rib sweeps r=99, old window closed -> below the arm bar // Rev 007: back in the Rev 004 window
                                       // between the sprocket swept envelope
                                       // (rib top r=89.5 on the cut Ø149 drum)
                                       // and the arm bar top (-112): keel at
                                       // -99.5 has 4.0 to the rib sweep and
                                       // 6.5 to the bar — both guarded. (005
                                       // parked it below the bar while the
                                       // bigger 11T rib closed this window.)
// pivot-stack cut lengths (Rev 003a): the bosses stack end-to-end through
// thrust washers, so the centre spacer and the two outboard sleeves are what
// close the chain carrier-to-carrier. All three are cut at the §9.3 dry-stack.
sp_half   = zi_tr + plate_t - boss_len - 4.5;  // washer 1.5 + flange 3
sleeve_z0 = zi_ld + boss_len + 4.5;            // leading boss end + flange + washer
sleeve_ln = cz - sleeve_z0;                    // outboard sleeve length
r_wrap = sprocket_od/2 + rib_h;        // belt INNER surface rides the rib top
belt_w = track_w;                      // belt overall width (measured)
ride_len = shock_ee - shock_sag;

function rot2(p, ang) = [ p[0]*cos(ang) - p[1]*sin(ang),
                          p[0]*sin(ang) + p[1]*cos(ang) ];
function arm_pt(local, arm_ang) = pivot + rot2(local, -na + arm_ang);
function mx(p) = [-p[0], p[1]];

low0   = arm_pt([a, shock_y], 0);                  // lower shock eye, neutral
up_dir = -na + 180 - theta;                        // shock leans in toward hub
upP    = low0 + ride_len*[cos(up_dir), sin(up_dir)]; // upper eye (FIXED)

// ---- load simulator: solve the arm angle where the spring balances the
// ---- wheel share of load_kg (virtual work: F_wheel = F_spring x MR(ang))
function MR_at(t) = abs((shock_len(t-0.5) - shock_len(t+0.5))
                  / (arm_pt([C,0], t+0.5)[1] - arm_pt([C,0], t-0.5)[1]));
wheelN = load_kg*9.81/2;                       // per wheel share of the pod load
function fbal(t) = spring_rate*(shock_ee - shock_len(t))*MR_at(t) - wheelN;
function solve_eq(lo, hi, n) = n == 0 ? (lo+hi)/2 :
  fbal((lo+hi)/2) < 0 ? solve_eq((lo+hi)/2, hi, n-1) : solve_eq(lo, (lo+hi)/2, n-1);
ang_eq = min(bump_max, max(-bump_max, solve_eq(-bump_max, bump_max, 40)));
if (load_kg > 0)
  echo(str("LOAD SIM: ", load_kg, " kg on the pod -> arms settle at ",
           round(ang_eq*10)/10, " deg  ·  ", round(spring_rate*(shock_ee - shock_len(ang_eq))),
           " N (", round(spring_rate*(shock_ee - shock_len(ang_eq))/9.81),
           " kg) per shock  ·  bump travel left: ",
           round((arm_pt([C,0],bump_max)[1] - arm_pt([C,0],ang_eq)[1])*10)/10, " mm"));


aL = animate ? 15*sin($t*360)       : (load_kg > 0 ? ang_eq : lead_angle);
aT = animate ? 15*sin($t*360 + 180) : (load_kg > 0 ? ang_eq : trail_angle);

wheel_tr = arm_pt([C + tension_pos, 0], aT);  // axle position in tensioner slot
wheel_ld = mx(arm_pt([C, 0], aL));

echo(str("BELT:     solved A=", A_eff, "  inner length=", belt_len(A_eff),
         " / target ", track_len));
echo(str("SPROCKET: ", sprocket_teeth, " stations x ", belt_pitch, " pitch — rib ",
         rib_w, " wide x ", rib_h, " tall (drum Ø", sprocket_od, " -> rib top Ø",
         sprocket_od + 2*rib_h, ", cord Ø", 2*pitch_r, ") — tooth spacing ON THE",
         " RIB TOP = ", PI*(sprocket_od + 2*rib_h)/sprocket_teeth, " mm (",
         360/sprocket_teeth, " deg apart)"));
echo(str("DERIVED:  P=", P, "  C=", C, "  neutral droop=", na, " deg"));
echo(str("SHOCK:    lower eye station a=", a, "  upper eye at ", upP));
echo(str("TRAVEL:   bump +", C*(sin(bump_max-na)+sin(na)),
         " / droop -", C*(sin(bump_max+na)-sin(na)), " mm at ±", bump_max, "°"));
// true kinematic motion ratio: d(shock length)/d(wheel height), differentiated
// numerically at ride height (the old (a/C)·sinθ approximation read ~5% low)
function shock_len(ang) = norm(arm_pt([a, shock_y], ang) - upP);
MR_true = (shock_len(-0.5) - shock_len(0.5))
        / (arm_pt([C,0], 0.5)[1] - arm_pt([C,0], -0.5)[1]);
echo(str("MOTION RATIO = ", abs(MR_true), " (kinematic)   (spring k = wheel k / MR²)"));
echo(str("SHOCK FORCE (spring_rate=", spring_rate, " N/mm): ride sag ",
         spring_rate*(shock_ee - shock_len(0)), " N -> full bump ",
         spring_rate*(shock_ee - shock_len(bump_max)), " N -> full droop ",
         spring_rate*(shock_ee - shock_len(-bump_max)), " N per shock"));
echo(str("PIVOT STACK: centre spacer ≈ ", 2*sp_half, " · outboard sleeves ≈ ",
         sleeve_ln, " ×2 — all Ø22×3 tube, cut at the §9.3 dry-stack"));
echo(str("TENSIONER: axle at +", tension_pos, " of 25 mm slot take-up — ",
         25 - tension_pos, " mm remaining (render_mode=\"tensioner\" for the ",
         "Sheet-6 close-up; advance both push bolts evenly)"));
// Rev 011d rear-fork bracket guards + cut lengths
if (use_bracket) {
  // belt outer arc at the sprocket (rib top + belt thickness T) vs the fork
  // stub's cut edge — the nearest scooter steel to the spinning belt
  brk_arc_gap = brk_cut_x - (sprocket_od/2 + rib_h + T);
  echo(str(brk_arc_gap < 8 ? "*** WARN " : "PASS ",
           "belt outer arc (Ø", sprocket_od + 2*rib_h + 2*T,
           ") to fork cut edge: ", brk_arc_gap, " mm"));
  echo(str("PASS belt edge (", track_w/2, ") to blade plane (",
           cz + carrier_t, "): ", cz + carrier_t - track_w/2,
           " mm — the render only LOOKS like they touch"));
  // the belt edge vs the REAL rear legs (117.7 inner = touching) is exactly
  // why the legs get cut — only the 65 stub survives, forward of the arc
  echo(str("BRACKET (Rev 011d, merged): TRAILING plate 262x40x", brk_t,
           " (key 190 from front, eye 242) · LEADING plate 210x40x", brk_t,
           " (key 190, eye 138) · NO pad — 2x2 M10 (35x14) in the blade,",
           " rows 13/27 up the leg · two DISTINCT plates, mark L/R · REMOVABLE:",
           " backing strip 65x40 inside the leg, M10x55, NO weld to the fork ·",
           " 2x M8 blade-to-carrier at the axle (reused leg bolts) + weld · through ",
           brk_pack, " packing · wheel moves ", brk_cut_x - 70,
           " rearward vs the old dropout · rear pod has NO separate stubs"));
}
// Rev 011b tensioner guards. The old check (head vs belt FACE at D/2) let
// the pull-type head sit 5 mm INSIDE the drive-lug tip sweep — the teeth
// stand lug_h proud of the face. Guard the teeth, not the face:
tens_lug_gap = (D/2 - lug_h) - 11;   // collar/nylock max radius ~11 about axle
echo(str(tens_lug_gap < 5 ? "*** WARN " : "PASS ",
         "tensioner collar/nylock to belt lug-tip sweep (r", D/2 - lug_h,
         "): ", tens_lug_gap, " mm"));
// pusher's forward stickout vs the lower shock-bolt sleeve at (a, 0): only
// tight near zero take-up; cut the bolt to draw_len so it clears
tens_head_x = (C + tension_pos - 7.5) - draw_len - 4.2;
echo(str(tens_head_x - (a + 7.5) < 2 ? "*** WARN " : "PASS ",
         "push-bolt head to lower shock sleeve: ", tens_head_x - (a + 7.5),
         " mm at tension_pos=", tension_pos));
// cut/buy lengths that follow from fork_gap + leg_t (echoed so the BOM can
// be verified against the measured fork instead of the old 30 mm assumption)
axle_stack = 2*(cz + carrier_t) + 22;   // carriers outer-to-outer + nut/head
echo(str("PIVOT AXLE: stack ≈ ", axle_stack, " → buy M", pivot_d, " cl.10.9 × ",
         10*ceil((axle_stack + 3)/10), " part-threaded (this fork_gap=",
         fork_gap, ", leg_t=", leg_t, ")"));
echo(str("CARRIERS: 40x6 strip cut ≈ ",  // Rev 011c: was 50x6
         (52+16) - min(pivot[1]-24, use_keel ? y_keel-12 : 0),
         use_keel ? str(" (must reach 12 past the keel hole at ", y_keel, ")")
                  : " (no keel — strip ends 24 below the pivot)"));
if (use_keel) echo(str("KEEL: tube Ø", keel_od, "×1.5 cut ", 2*cz,
         " · M8 rod cut ≈ ", 2*(cz+carrier_t)+12));
if (!use_keel) echo("KEEL: deleted (fork legs box the carriers since Rev 002)");
// idler axle — PURCHASED 2026-07-25: 2x GB901 M12x110 (TRAILING) + 2x
// M12x120 (LEADING), grade 8.8 + 500 mm of 15 OD x 12 ID pipe for the sleeve
// stack (SF ~3). Ø15 shaft kept as emergency spare. Stack/side: [Ø15 push
// collar 7, trailing only] + washer 2.5 + M12 nyloc 11.8 + ~2 proud.
echo(str("IDLER AXLE (PURCHASED: M12 studs 2x110 TR + 2x120 LD, 8.8 + 500 pipe): ",
         "cut per axle from 15ODx12ID pipe — inner tube ", 2*zi_tr, " (TR) / ",
         2*zi_ld, " (LD; plate-inner to plate-inner, through both bearings) + 2 rings ",
         plate_t, " in the plate slots/holes. Cut long, file square, fit at dry-stack; ",
         "wheel must spin free with zero side-play before final nyloc torque"));
echo(str("SHOCKS: run ", shocks_inboard ? "INBOARD" : "OUTBOARD",
         " of the carriers at |z|=", sz, " — upper tab on carrier ",
         shocks_inboard ? "INNER" : "OUTER", " face; lower sleeve ≈ ",
         (sz - 5) - (zi_ld + plate_t), " long"));

// ---- belt-clearance guard: nothing hanging from the carrier may touch the
// ---- track when both arms hit full bump (belt bottom run at its highest)
y_w_bump    = -P + C*sin(bump_max - na);   // idler centre at full bump
y_belt_bump = y_w_bump - D/2;              // belt inner surface, bottom run
y_lug_bump  = y_belt_bump + lug_h;         // guide-lug tops
lug_zone    = F/2 + lug_w;                 // |z| outer edge of lug rows
clearances = concat(
  // Rev 002: carrier plates ride OUTSIDE the belt width — tongue check only
  // applies if a future layout puts them back over the belt
  (cz < track_w/2 + 3) ?
    [["carrier tongue Ø48", (pivot[1] - 24) - ((cz < lug_zone) ? y_lug_bump : y_belt_bump)]] : [],
  use_keel ? [[str("keel standoff  Ø", keel_od), (y_keel - keel_od/2) - y_lug_bump]] : [],
  [
   [str("pivot spacer   Ø", bushing_od), (pivot[1] - bushing_od/2) - y_lug_bump],
   [str("arm bar (", boss_disc, " wide)  "), (pivot[1] - boss_disc/2) - y_lug_bump]]);
if (cz >= track_w/2 + 3)
  echo(str("NOTE carrier plates at |z|=", cz, " — outside the belt (half-width ",
           track_w/2, "); they cannot contact the track at any bump"));
echo(str(fork_gap/2 - track_w/2 < 3 ? "*** TIGHT " : "OK ",
         "belt edge to fork leg: ", fork_gap/2 - track_w/2, " mm per side"));
for (c = clearances)
  echo(str(c[1] < 5 ? "*** WARN " : "PASS ", c[0], ": ", c[1],
           " mm above track at +", bump_max, "° bump"));
// keel window fit (all static-to-static or pivot-centred, so the gaps hold at
// every articulation; small values acceptable) + in-plane wheel clearances
keel_gaps = concat(use_keel ? [
  ["keel to sprocket swept rib top", abs(y_keel) - keel_od/2 - (sprocket_od/2 + rib_h)],
  [str("keel to arm bar (", boss_disc, " wide)"),
        abs(y_keel - pivot[1]) - boss_disc/2 - keel_od/2],
  ["keel to pivot washers Ø30",   abs(y_keel - pivot[1]) - 15 - keel_od/2]] : [], [
  // Rev 003a: the lower shock through-bolt and the cross-brace share the
  // space between the fork plates with the Ø108 idler wheel — check both
  ["shock bolt Ø8 to idler wheel", sqrt(pow(C - a, 2) + shock_y*shock_y) - D/2 - 4],
  ["cross-brace to idler wheel",    sqrt(pow(C - 52, 2) + 6*6) - D/2],
  // Rev 005c: the pivot centre spacer (Ø22, spans z ±sp region, crosses the
  // teeth sweep) is what caps `drop` — guard it against the spinning rib top
  ["pivot spacer Ø22 to sprocket swept rib", (abs(pivot[1]) - 11) - (sprocket_od/2 + rib_h)],
  // Rev 008: the 9T wheel pulls the belt close to the motor — lug tips and
  // blade tips both sweep Ø(face - 2*lug_h); guard them against the casing
  ["belt lug/blade tips to motor casing", (sprocket_od/2 + rib_h - lug_h) - casing_d/2],
  // coil spring (Ø~44, r22 about the shock line) vs the carrier tongue edge
  // (|x| ≤ 24): evaluated at the coil's top turn, ~25 mm below the upper eye,
  // the closest point since the line leans away from the tongue going down
  ["shock coil Ø44 to carrier strip (40 wide — Rev 011c)",
     (upP[0] + ((25)/(upP[1]-low0[1]))*(low0[0]-upP[0])) - 20 - 22],
  // Rev 011: THE guard that now caps `drop`. The arm bar's chamfered rear
  // corner sweeps toward the spinning sprocket as the arm droops; this was
  // silently unguarded until Rev 011 (Rev 009 sat at 4.1 mm). Swept over the
  // full travel, worst case is full droop. The trailing arm's inner plate is
  // the one at risk: teeth reach |z|=25.5, that plate sits at |z|=25.4.
  ["arm rear corner to sprocket swept rib (worst over travel)",
     min([for (t = [-bump_max : 1 : bump_max])
           min([for (pt = [[-22, boss_disc/2 - arm_chamf],
                           [-22 + arm_chamf/2, boss_disc/2 - arm_chamf/2],
                           [-22 + arm_chamf, boss_disc/2]])
                 norm(arm_pt(pt, t))])]) - (sprocket_od/2 + rib_h)]]);
for (g = keel_gaps)
  echo(str(g[1] < 2 ? "*** WARN " : "PASS ", g[0], ": ", g[1], " mm gap"));

ex = (render_mode == "exploded") ? 1 : 0;

// ============================================================== 2D profiles
module arm_plate_2d(slot=false){
  // Rev 004: plain flat-bar rectangle, 40 wide — straight cuts + drilled
  // holes. Rev 011 adds ONE grinder pass per rear corner: a 45-degree chamfer
  // (arm_chamf) on the two corners at the pivot end. Those corners swing
  // closest to the spinning sprocket at full droop; the chamfer buys +3.6 mm.
  send = slot ? 18 : 0;
  hb = boss_disc/2;  xf = -22 + arm_chamf;  xe = C + send + 26;
  difference(){
    polygon([[xf, hb], [xe, hb], [xe, -hb], [xf, -hb],
             [-22, -hb + arm_chamf], [-22, hb - arm_chamf]]);
    circle(d=30.8);                             // pivot hole: the Ø31 boss tube
                                                // (Rev 004c: owner sourced 31 OD,
                                                // was 32) passes THROUGH the plate
                                                // and is welded on both faces
                                                // (§9.2); bushing seat Ø22 H7 is
                                                // reamed in the TUBE after welding
    if (slot) hull(){ translate([C,0])    circle(d=G+0.4);
                      translate([C+25,0]) circle(d=G+0.4); }
    else      translate([C,0]) circle(d=G+0.4); // wheel axle bore
    translate([a, shock_y]) circle(d=8.4);      // lower shock bolt M8 (on axis;
                                                // Rev 004b: shock eyes measured Ø8)
  }
}

module axle_key_2d(){
  // hub-motor axle key: Ø10+0.4 with flats 8.9 across — the torque-arm fit.
  // Cut in the carrier AND (Rev 011c) in the shock tab stub; drill Ø10.4,
  // file the flats. Never a slot — a slot lets the axle rotate.
  intersection(){ circle(d=axle_d+0.4);
                  square([axle_d+0.4, 8.9], center=true); }
}

module carrier_2d(){
  // Rev 011c (owner): 40-wide flat-bar strip — was 50. Same stock as the
  // arms/braces/stubs, so the 50x6 steel line is gone entirely. Edge
  // distance at the Ø16 pivot bore drops 17 -> 12 (0.75·d, acceptable);
  // the Ø30 pivot washers keep 5 per side. Every centreline feature
  // (axle key, M8 fork bolt, pivot bore) lands on it. The shock tab is a
  // separate stub (tab_stub_2d) welded on the OUTER face at hub level.
  // Same part both sides (symmetric).
  y_bot = min(pivot[1] - 24, use_keel ? y_keel - 12 : 0);  // reach past the keel
                                            // hole (Rev 9: keel below the arm
                                            // bar -> strip cut ~290, not 225)
  difference(){
    translate([-20, y_bot]) square([40, (52+16) - y_bot]);
    axle_key_2d();   // the plate doubles as a torque arm
    // Rev 011d: 2x M8 blade-to-carrier bolts, 12 above/below the axle on the
    // centreline — anti-rotation redundancy for the keyed axle; the rear
    // pod's freed carrier-to-leg M8x30s move here. Weld blade-to-carrier at
    // final fit on top. (Front pod: skip drilling until it gets a bracket.)
    if (use_bracket) for (yy=[-12,12]) translate([0,yy]) circle(d=8.4);
    translate([0,52])      circle(d=8.5);       // M8 into fork leg (drill leg)
    translate(pivot)       circle(d=pivot_d);   // pivot bore, ream in pair
    if (use_keel) translate([0, y_keel]) circle(d=8.5);  // keel bolt M8
  }
}

module tab_stub_2d(p){
  // Rev 011c (owner): upper shock tab = 40x6 stub, 83 long — spans the FULL
  // 40-wide carrier strip (was a 55-long stub with a 17 lap). It carries the
  // same Ø10.4 flatted key as the carrier, so the hub axle passes through
  // strip AND stub: the axle nut clamps the stub mechanically on top of the
  // weld, and the torque-arm key engagement doubles (6 -> 12 of flats).
  // Weld with the axle inserted through both so the flats index.
  // ONE stub per carrier — each carrier carries only its own arm's shock
  // (trailing on the +z carrier, leading on the -z carrier); the Rev 004
  // drawings showed two per carrier, which was one too many. The two stubs
  // of a pod are a mirror pair: drill two identical blanks, flip one over.
  // Ø8.4 eye pin hole at p (M8 pin — Rev 004b: shock eyes measured Ø8).
  s = p[0] > 0 ? 1 : -1;
  difference(){
    translate([s==1 ? -20 : -63, -20]) square([83, 40]);
    axle_key_2d();
    translate(p) circle(d=8.4);
  }
}

// ============================================================== components
// Sheet-6 belt tensioner, local arm coords (pivot at origin, wheel end +x).
// REV 011b (owner, 2026-08-24): flipped from a pull-type draw bolt to a
// PUSHER, motorcycle-adjuster style, because the pull-type's bolt head sat
// ~44 mm behind the axle — dead centre of the belt wrap, where the drive
// LUG TIPS sweep only D/2 - lug_h = 39 mm from the axle. The old guard
// checked the belt FACE (Ø108, 10 mm clear) and missed the teeth entirely;
// the owner found the head touching them on the bench. The rear of the
// idler is wrapped from ~52 deg over the bottom, so NO rear-mounted head
// can clear the teeth; the FORWARD side (toward the pivot) is never
// wrapped, so the hardware moves there:
//   - pusher BLOCK (26 x 14 x 6, was the 26x18 lug) welded across each
//     plate tip, rear face at C - xb_rear — 7.5 clear of the Ø15 collar at
//     zero take-up, 7.3 clear of the slot's round end for the weld;
//   - M6 push bolt threads THROUGH the block (tap M6, or weld a nut on the
//     forward face); screwing IN pushes the axle rearward. Belt tension now
//     loads the bolt in COMPRESSION - it is a positioner only; the torqued
//     M12 nylocks are what hold the axle, as before.
//   - the bolt tip bears on a Ø15 x 7 PUSH COLLAR cut from the same
//     Ø15x12 axle-sleeve pipe, clamped washer-to-nylock on the stud. It
//     replaces the Rev 004a M6 eye nut (no longer needed - keep as spares)
//     and, unlike pushing a nut flat, cannot rotate at final torque.
//     Stack/side: washer 2.5 + collar 7 + nylock 11.8 = 53.05 -> the
//     purchased M12x110 still ends 1.95 proud. Nothing new to buy.
xb_rear = 15;                     // block REAR face, mm forward of nominal C
module tensioner_hw(zi){
  zo = zi + plate_t;              // fork-plate outer face
  xb = C - xb_rear;               // block REAR face (faces the axle)
  bz = zo + 7;                    // push-bolt axis, centred on the collar
  tip = C + tension_pos - 7.5;    // bolt tip on the Ø15 collar surface
  for (s=[1,-1]) scale([1,1,s]){
    // welded pusher block: upright on the plate outer face, weld all around
    color([0.30,0.36,0.48]) difference(){
      translate([xb-6, -13, zo]) cube([6, 26, (bz - zo) + 7]);
      translate([xb-7, 0, bz]) rotate([0,90,0]) cylinder(h=8, d=5.0); // tap M6
    }
    // Ø15 x 7 push collar on the stud, clamped washer-to-nylock (cut from
    // the same Ø15x12 axle-sleeve pipe) — the solid round target the bolt
    // tip bears on; unlike a nut flat it cannot rotate at final torque
    color([0.55,0.55,0.58]) translate([C + tension_pos, 0, zo + 2.5])
      difference(){ cylinder(h=7, d=15); translate([0,0,-1]) cylinder(h=9, d=12.1); }
    // M6 push bolt through the block: screwing IN pushes the collar (and so
    // the axle) rearward; jam nut locks on the block's FORWARD face
    color([0.55,0.55,0.58]){
      translate([tip - draw_len, 0, bz]) rotate([0,90,0])
        cylinder(h=draw_len, d=5.8);
      translate([xb - 6 - 5.2, 0, bz]) rotate([0,90,0])
        cylinder(h=5.2, d=11.5, $fn=6);   // M6 jam nut on the block front
      translate([tip - draw_len - 4.2, 0, bz]) rotate([0,90,0])
        cylinder(h=4.2, d=11.5, $fn=6);   // M6 bolt head
    }
  }
}

// ---------------------------------------------------------- part catalog --
// Schematic renders of each purchased BOM item (render_mode="part"), used
// as the thumbnail images in blueprint §7. Shapes are illustrative.
cSteel  = [0.62,0.63,0.66];
cBronze = [0.72,0.53,0.30];
module cat_hexnut(af, h, bore){
  difference(){ cylinder(h=h, d=af*1.1547, $fn=6);
                translate([0,0,-1]) cylinder(h=h+2, d=bore); } }
module cat_washer(od, id, t=1.5){
  difference(){ cylinder(h=t, d=od); translate([0,0,-1]) cylinder(h=t+2, d=id); } }
module cat_threads(d, l){           // schematic thread: ribbed cylinder
  cylinder(h=l, d=d-0.6);
  for (i=[0:1.6:l-1.4]) translate([0,0,i]) cylinder(h=0.8, d=d+0.4); }
module cat_bolt(d, shank, thread, head_af, head_h){
  cylinder(h=head_h, d=head_af*1.1547, $fn=6);
  translate([0,0,head_h]) cylinder(h=shank, d=d);
  translate([0,0,head_h+shank]) cat_threads(d, thread); }
module cat_tube(od, id, l){
  difference(){ cylinder(h=l, d=od); translate([0,0,-1]) cylinder(h=l+2, d=id); } }

module part_catalog(name){
  if (name == "pivot_axle"){                     // BOM 1 — M16×195 pivot bolt,
                                                  // one end threaded 45 long
                                                  // (Rev 004c: owner's actual bolt;
                                                  // smooth shank 150 clears all
                                                  // 4 bushings with 4 mm margin —
                                                  // only ONE nylock needed, headed
                                                  // bolt, not a double-end stud)
    color(cSteel) rotate([0,90,0]) cat_bolt(16, 150, 45, 24, 10);
    color(cSteel) translate([60,-45,0]) cat_hexnut(24, 16, 14.8);
    color(cSteel) for (i=[0:1]) translate([110+i*45,-45,0]) cat_washer(30,17,3);
  } else if (name == "arm_plates"){              // BOM 2 — one of each profile
    color(cSteel){ linear_extrude(plate_t) arm_plate_2d(true);
                   translate([0,95,0]) linear_extrude(plate_t) arm_plate_2d(false); }
  } else if (name == "carrier_plates"){          // BOM 3
    color(cSteel) linear_extrude(carrier_t) carrier_2d();
  } else if (name == "boss_tube"){               // BOM 4 — 31×4.5 tube (Rev 004c,
                                                  // was 32×5), ream ID 22 H7
    color(cSteel) for (i=[0:1]) translate([i*55,0,0]) cat_tube(31,22,25);
  } else if (name == "bushing"){                 // BOM 5 — flanged, bronze 16×22×20
    color(cBronze) for (i=[0:1]) translate([i*45,0,0]){
      cat_tube(22,16,20); cat_washer(28,16,3); }
  } else if (name == "thrust_washer"){           // BOM 6
    color(cSteel) for (i=[0:1]) translate([i*46,0,0]) cat_washer(30,16,1.5);
  } else if (name == "spacer_tube"){             // BOM 7 — centre + 2 outboard
    color(cSteel) rotate([0,90,0]) cat_tube(22,16,2*sp_half);
    color(cSteel) for (i=[0:1]) translate([25+i*20,-30,0])
      rotate([0,90,0]) cat_tube(22,16,sleeve_ln);
  } else if (name == "shock"){                   // BOM 8 — coil-over
    shock3d([0,0],[150,0],0);
  } else if (name == "shock_mounts"){            // BOM 9 — tab + sleeve
    color(cSteel) linear_extrude(6) translate([20,20,0]) tab_stub_2d(upP);
    color(cSteel) translate([55,-15,0]) cat_tube(15,9,45);
  } else if (name == "fork_hw"){                 // BOM 10 — M8 bolt + nuts
    color(cSteel) rotate([0,90,0]) cat_bolt(8, 12, 18, 13, 5.5);
    color(cSteel) translate([20,-22,0]) cat_hexnut(13, 8, 6.9);
    color(cSteel) translate([45,-22,0]) cat_hexnut(17, 10, 8.8);  // stock M10
  } else if (name == "keel"){                    // BOM 11 — tube + rod + nuts
    color(cSteel) rotate([0,90,0]) cat_tube(keel_od,9,148);
    color(cSteel) translate([0,30,0]) rotate([0,90,0]) cat_threads(8,172);
    color(cSteel) for (i=[0:3]) translate([20+i*28,55,0]) cat_hexnut(13,7,6.9);
  } else if (name == "draw_bolt"){               // BOM 12 — bolt + jam + collar
    color(cSteel) rotate([0,90,0]) cat_bolt(6, 0, draw_len, 10, 4);
    color(cSteel) translate([25,-24,0]) cat_hexnut(10, 5, 5.2);
    color(cSteel) translate([55,-24,0]) cat_tube(15, 12, 7);
  } else if (name == "hardware"){                // BOM 14 — assortment
    color(cSteel){ cat_hexnut(13,8,6.9);
      translate([24,4,0])  cat_hexnut(17,10,8.8);
      translate([4,26,0])  cat_washer(17,8.5);
      translate([26,30,0]) cat_washer(21,10.5);
      translate([-6,-26,0]) rotate([0,90,20]) cat_bolt(8,10,20,13,5.5); }
  } else if (name == "zerk"){                    // BOM 15 — M6 grease nipple
    color(cSteel) for (i=[0:1]) translate([i*16,0,0]){
      cat_threads(6, 5);
      translate([0,0,5]) cylinder(h=2.5, d=11, $fn=6);
      translate([0,0,7.5]) cylinder(h=3.5, d1=6.5, d2=4.5);
      translate([0,0,11.5]) sphere(d=5); }
  } else if (name == "idler_axle"){              // BOM 16 — 15x148 thru-axle
    color(cSteel) rotate([0,90,0]){              // (MEROCA, 9 mm M15x1.5 tip)
      cylinder(h=5, d=21);                       // low-profile head
      translate([0,0,5]) cylinder(h=139, d=15);
      translate([0,0,144]) cat_threads(15, 9); }
    color(cSteel) translate([30,-25,0]) cat_hexnut(22, 6, 14.8);  // M15x1.5 nut
    color(cSteel) translate([60,-25,0]) cat_tube(22,15.5,35);     // filler sleeve
    color(cSteel) translate([95,-25,0]) cat_tube(22,15.5,8.85);   // centering sleeve
  } else if (name == "reused"){                  // stock sprocket/idler/belt
    sprocket();
    translate([160,0,0]) idler_wheel();
  }
}

// red 3D leader + text for the "tensioner" detail view
module flag(txt, tip, anchor){
  color([0.70,0.18,0.12]){
    hull(){ translate(tip) sphere(0.9); translate(anchor) sphere(0.9); }
    translate(anchor + [2, -2.5, 0]) linear_extrude(1.2) text(txt, size=6);
  }
}

module idler_wheel(){
  // Rev 007: stepped profile — the Ø108 tread band (~20 wide) runs IN the
  // 22 mm gap between the lug pairs on the belt face; the wider hub boss
  // (H=58) sits at a smaller Ø so the 15-tall lugs sweep past it.
  color([0.16,0.16,0.17]) difference(){
    union(){
      cylinder(h=tread_w, d=D, center=true);     // tread band, in the lug gap
      cylinder(h=H,  d=D-2*lug_h-8, center=true);// hub boss, clears the lugs
    }
    cylinder(h=H+2, d=G, center=true);
    for (s=[1,-1]) translate([0,0,s*(H/2 - brg_w/2)])
      cylinder(h=brg_w+0.2, d=brg_od+0.4, center=true); // 6302 bearing recesses
  }
  color([0.75,0.75,0.78]) for (s=[1,-1]) translate([0,0,s*(H/2 - brg_w/2)])
    difference(){ cylinder(h=brg_w,   d=brg_od, center=true);
                  cylinder(h=brg_w+2, d=G,      center=true); }
}

// T-tooth, kit-wheel style: tooth_span across the belt, tooth_t thick,
// widening by tooth_fil per side over the rib zone — that widening IS the
// printed root fillet the ABS overhangs need for fatigue life. Runs radially
// from the drum to flush with the rib top (the belt face rides the rib, so
// the tooth may not stand proud of it).
module sprocket_tooth(){
  ts = tooth_span/2;  rw = rib_w/2;  t2 = tooth_t/2;  f = tooth_fil;
  translate([sprocket_od/2 - 1, 0, 0]) rotate([0,90,0])
    linear_extrude(height=rib_h + 1)
      polygon([[-ts,-t2],[-rw,-t2-f],[rw,-t2-f],[ts,-t2],
               [ts, t2],[ rw, t2+f],[-rw, t2+f],[-ts, t2]]);
  // outboard blades (Rev 005b): beside the 35-wide rim the tooth drops to
  // full lug depth — nothing is there to clash, the rim ends at |z|=17.5.
  // Blade tips sweep Ø149; motor casing must stay under that (Ø130 drawn).
  blade_r = sprocket_od/2 + rib_h - lug_h;
  for (s=[1,-1]) translate([blade_r, 0, 0]) rotate([0,90,0])
    linear_extrude(height=lug_h + 0.1)
      polygon([[s*(sprocket_w/2), -t2],[s*ts, -t2],[s*ts, t2],[s*(sprocket_w/2), t2]]);
}

module sprocket(){
  // Rev 006: hub motor + the CUT-DOWN rim ring (flange walls ground off; the
  // Ø149 tunnel floor is the untouched factory drum) hanging on spokes across
  // the air gap. Printed ABS = thin clamp shell around the drum + 18-wide rib
  // + T-teeth; the two half-shells bolt to each other THROUGH the spoke gaps.
  // The whole 20.5-wide drum passes between the belt's lug pairs (22 gap).
  color([0.13,0.13,0.14]) difference(){        // hub motor casing, axle static
    cylinder(h=sprocket_w+8, d=casing_d, center=true);
    cylinder(h=sprocket_w+40, d=axle_d+0.5, center=true);
  }
  color([0.55,0.55,0.58]){                     // REV 009: UNCUT rim — the whole
    // Ø165 ring reads GRAY from outside (flanges, floor, and the tunnel mouth;
    // the sage ABS fill hides inside it, so it is drawn as part of the ring)
    difference(){ cylinder(h=sprocket_w, d=sprocket_od, center=true);
                  cylinder(h=sprocket_w+2, d=casing_d, center=true); }
  }
  color([0.18,0.18,0.19])                       // the hub's 5 FINS (owner photo):
    for (i=[0:4]) rotate([0,0,i*72])            // black blades, casing -> rim,
      hull(){                                   // brake side; untouched in Rev 009
        translate([casing_d/2 - 2, 0, sprocket_w/2 - 4]) cube([6, 4.1, 12], center=true);
        translate([149/2 - 3, 0, sprocket_w/2 - 3.6]) cube([6, 4.1, 7.25], center=true);
      }
  color([0.55,0.62,0.52]){                     // printed ABS (sage): only what
                                               // stands ABOVE the Ø165 rim
    cylinder(h=rib_w, d=sprocket_od + 2*rib_h, center=true);       // centre rib
    for (i=[0:sprocket_teeth-1]) rotate([0,0,i*360/sprocket_teeth])
      sprocket_tooth();
  }
}

// Rev 008a: live shock-force gauge. Bar fill = compression as a fraction of
// the full-bump compression (green -> red); text = compression (from free
// length, includes the ride sag) and spring force = spring_rate x compression.
// Uses the same shock_len() the motion-ratio calc differentiates.
module force_gauge(ang, zc, mir=false){
  L    = shock_len(ang);                    // current eye-to-eye
  comp = shock_ee - L;                      // compression incl. sag
  cmax = shock_ee - shock_len(bump_max);    // compression at full bump
  fr   = min(1, max(0, comp/cmax));
  F    = spring_rate*comp;
  p0   = mir ? mx(upP) : upP;
  p1   = mir ? mx(arm_pt([a,shock_y],ang)) : arm_pt([a,shock_y],ang);
  m    = (p0+p1)/2;
  translate([m[0] + (mir?-38:30), m[1]-32, zc]){
    color([0.22,0.22,0.25]) cube([9, 64, 2]);               // gauge track
    color([0.9,0.9,0.92])   translate([-1.5,62.5,0]) cube([12, 1.5, 2.5]); // max line
    color([fr, 0.85*(1-fr)+0.1, 0.12])
      translate([1.5,1.5,2]) cube([6, max(0.5, 61*fr), 3.5]); // fill bar
    // text faces OUTWARD on its own side (trailing +z, leading -z)
    color([0.92,0.92,0.94]) translate([mir?-14:14, 24, 0])
      rotate([0, mir?180:0, 0]) linear_extrude(1.4)
        text(str(round(F/9.81), " kg"), size=9);
    color([0.75,0.75,0.78]) translate([mir?-14:14, 10, 0])
      rotate([0, mir?180:0, 0]) linear_extrude(1.4)
        text(str(round(F), " N · ", round(comp*10)/10, " mm"), size=5.5);
  }
}

module shock3d(p, q, zc){
  v = q - p;  L = norm(v);  ang = atan2(v[1], v[0]);
  translate([p[0], p[1], zc]) rotate([0,0,ang]){
    for (x=[0, L]) color([0.55,0.55,0.58])            // eyelets
      translate([x,0,0]) difference(){
        cylinder(h=10, d=18, center=true);
        cylinder(h=12, d=10, center=true); }
    color([0.72,0.72,0.75]) translate([6,0,0])        // damper body
      rotate([0,90,0]) cylinder(h=0.52*L, d=22);
    color([0.72,0.72,0.75]) rotate([0,90,0])          // shaft
      cylinder(h=L-6, d=9);
    color([0.70,0.15,0.12]) translate([10,0,0])       // coil spring
      rotate([0,90,0]) linear_extrude(height=L-22, twist=2160, $fn=24)
        translate([14,0]) circle(d=4.2);
  }
}

// arm as a fork weldment; zi = fork inner face, szs = shock side (+1/-1)
module arm3d(zi, slot, ang, szs){
  translate([pivot[0], pivot[1], 0]) rotate([0,0,-na+ang]){
    // fork plates
    color([0.30,0.36,0.48]) for (s=[1,-1])
      translate([0,0, s==1 ? zi : -zi-plate_t])
        linear_extrude(plate_t) arm_plate_2d(slot);
    // pivot boss tubes — one 25-long tube per plate (Rev 003a: trailing bosses
    // point INBOARD toward the spacer, leading bosses point OUTBOARD toward
    // the sleeves; boss end faces stack through the thrust washers)
    bz0 = slot ? zi + plate_t - boss_len : zi;   // boss inner end |z|
    for (s=[1,-1]) scale([1,1,s]){
      color([0.30,0.36,0.48]) difference(){
        translate([0,0,bz0]) cylinder(h=boss_len, d=31);   // Rev 004c: 31 OD
        translate([0,0,bz0-1]) cylinder(h=boss_len+2, d=bushing_od); }
      // flanged bronze bushing: body 20 in the boss, flange Ø28×3 proud at the
      // thrust face (trailing: inboard end; leading: outboard end)
      fz = slot ? bz0 : bz0 + boss_len;          // flange-side boss face |z|
      color([0.72,0.53,0.30]) difference(){
        union(){
          translate([0,0, slot ? fz : fz-20]) cylinder(h=20, d=bushing_od+0.01);
          translate([0,0, slot ? fz-3 : fz])  cylinder(h=3,  d=28); }
        translate([0,0,fz-24]) cylinder(h=48, d=pivot_d); }
    }
    // lower cross-brace (Rev 003a: inboard of the wheel; Rev 004: raised to
    // y -18..-6 so it stays inside the 40 mm bar width)
    color([0.30,0.36,0.48]) translate([22, -18, -zi]) cube([30, 12, 2*zi]);
    // (Rev 007: brace restored to the Rev 004 position 28..58 — the full
    //  Rev 004 arm is back (C=116.7), clears the idler by 5.0; guard C-58.)
    // shock through-bolt + outboard spacer sleeve
    color([0.55,0.55,0.58]) translate([a, shock_y, -(zi+plate_t)-4])
      cylinder(h=(zi+plate_t)+4 + (sz-5), d=7.8);
    color([0.55,0.55,0.58]) translate([a, shock_y, szs>0 ? zi+plate_t : -(sz-5)])
      difference(){ cylinder(h=(sz-5)-(zi+plate_t), d=15);
                    cylinder(h=sz, d=8.5); }
    // wheel + PURCHASED axle (Rev 008a): GB901 M12 double-end stud (110
    // trailing / 120 leading, grade 8.8) inside the Ø15x12 sleeve stack —
    // inner tube plate-to-plate through both bearings, Ø15 rings in the
    // plate slots/holes, washer + [tensioner eye] + M12 nyloc per end.
    wx = slot ? C + tension_pos : C;
    Ls = slot ? 110 : 120;                                      // stud length
    translate([wx, 0, 0]){
      translate([0,0, ex* (szs>0 ? 0 : 0)]) idler_wheel();
      color([0.60,0.60,0.63]) cylinder(h=Ls, d=11.8, center=true);   // M12 stud
      color([0.55,0.55,0.58]) difference(){                     // inner sleeve tube
        cylinder(h=2*zi, d=15, center=true);
        cylinder(h=2*zi+2, d=12.1, center=true); }
      for (s=[1,-1]) scale([1,1,s]){
        color([0.55,0.55,0.58]) translate([0,0,zi])             // slot/hole ring
          difference(){ cylinder(h=plate_t, d=15); cylinder(h=plate_t+2, d=12.1); }
        color([0.8,0.8,0.82]) translate([0,0,zi+plate_t])       // washer 13x24
          difference(){ cylinder(h=2.5, d=24); cylinder(h=4, d=13, center=true); }
        if (slot) color([0.72,0.68,0.35]) translate([0,0,zi+plate_t+2.5])
          difference(){ cylinder(h=7, d=15);                    // push collar
                        cylinder(h=9, d=12.1, center=true); }
        color([0.45,0.45,0.48]) translate([0,0,zi+plate_t+2.5+(slot?7:0)])
          difference(){ cylinder(h=11.8, d=19, $fn=6);          // M12 nyloc
                        cylinder(h=13, d=12, center=true); }
      }
    }
    // Sheet-6 tensioner hardware on the slotted (trailing) arm
    if (slot) tensioner_hw(zi);
  }
}

module carrier_group(){
  // plates (Rev 002: bolted to the fork-leg outer faces)
  color([0.36,0.43,0.56]) for (s=[1,-1])
    translate([0,0, (s==1 ? cz : -cz-carrier_t) + s*ex*55])
      linear_extrude(carrier_t) carrier_2d();
  // upper shock tabs — welded to the carrier INNER face when the shocks run
  // inboard (Rev 002, thick legs), to the OUTER face when outboard (Rev 002c,
  // measured 4 mm legs leave no inboard room)
  // Rev 011c: ONE full-width tab stub per carrier, on the OUTER face at hub
  // level, keyed on the axle; the eye pin cantilevers from the stub out to
  // the shock plane through washers. +z carrier serves the trailing shock,
  // -z the leading — a shock loads only the carrier it hangs from.
  // 011d merged: with the bracket, the blade IS the shock tab — separate
  // stubs exist only on the front pod (no bracket there yet)
  tab_z0 = cz + carrier_t;
  if (!use_bracket) color([0.36,0.43,0.56]) for (s=[1,-1])
    translate([0,0, (s==1 ? tab_z0 : -(tab_z0 + 6)) + s*ex*55])
      linear_extrude(6) tab_stub_2d(s==1 ? upP : mx(upP));
  // REV 011d rear-fork bracket: blade + pad per side, keyed on the axle at
  // z = carrier outer face .. +brk_t; the shock stub moves outboard by brk_t
  if (use_bracket) for (s=[1,-1]) scale([1,1,s]){
    bz0 = cz + carrier_t;                      // bracket inner face |z|
    // blade = bracket + shock tab in one: trailing (+z) runs to +72 and
    // carries the eye at upP; leading (-z) ends at +20, eye at mx(upP)
    color([0.20,0.55,0.30]) translate([0,0,bz0]) linear_extrude(brk_t)
      difference(){
        translate([-(brk_cut_x + brk_pad_l), -brk_axle_up])
          square([brk_cut_x + brk_pad_l + (s==1 ? 72 : 20), brk_blade_w]);
        axle_key_2d();
        for (yy=[-12,12]) translate([0,yy]) circle(d=8.4);  // M8 to carrier
        translate(s==1 ? upP : mx(upP)) circle(d=8.4);   // shock eye pin
        for (fx=[15,50]) for (fy=[13,27])                // 2x2 M10, 35 x 14 —
          translate([-(brk_cut_x + fx), -brk_axle_up + fy])  // all in the blade
            circle(d=10.5);
      }
    // ghost: the cut rear-fork leg stub + the 17 packing at the pad zone
    color([0.45,0.50,0.60,0.35]) translate([-(brk_cut_x + brk_pad_l),
      -brk_axle_up, brk_leg_gap/2]) cube([brk_pad_l, brk_leg_h, leg_t]);
    color([0.55,0.55,0.58,0.6]) translate([-(brk_cut_x + brk_pad_l),
      -brk_axle_up, brk_leg_gap/2 + leg_t]) cube([brk_pad_l, brk_leg_h, brk_pack]);
    // backing strip on the leg's INNER face — the no-weld sandwich layer
    color([0.20,0.55,0.30]) translate([-(brk_cut_x + brk_pad_l),
      -brk_axle_up, brk_leg_gap/2 - brk_t]) cube([brk_pad_l, brk_blade_w, brk_t]);
  }
  // hub-motor axle: static Ø10, spans fork legs + both plates
  color([0.55,0.55,0.58])
    cylinder(h=2*(cz+carrier_t)+24, d=axle_d, center=true);
  // ghost fork legs (context only — measure leg_t)
  color([0.45,0.50,0.60,0.35]) for (s=[1,-1])
    translate([-20, -12, s==1 ? fork_gap/2 : -fork_gap/2-leg_t])
      cube([40, 150, leg_t]);
  // keel standoff between sprocket disc and arm boss disc
  if (use_keel) color([0.55,0.55,0.58]) translate([0, y_keel, -cz])
    difference(){ cylinder(h=2*cz, d=keel_od); cylinder(h=2*cz+2, d=8.4); }
  if (use_keel) color([0.55,0.55,0.58]) translate([0, y_keel, -cz-carrier_t-6-ex*70])
    cylinder(h=2*(cz+carrier_t)+12, d=8);
}

module pivot_axle_group(){
  translate([0, -ex*110, 0]) translate([pivot[0], pivot[1], 0]){
    color([0.45,0.45,0.48]){
      cylinder(h=2*(cz+carrier_t)+22, d=pivot_d, center=true);      // axle
      translate([0,0,  cz+carrier_t+11]) cylinder(h=10, d=28, $fn=6); // head
      translate([0,0,-(cz+carrier_t+21)]) cylinder(h=15, d=28, $fn=6); // nylock
    }
    color([0.55,0.55,0.58]) difference(){                 // centre spacer ≈14
      cylinder(h=2*sp_half, d=bushing_od, center=true);
      cylinder(h=2*sp_half+2, d=pivot_d+0.4, center=true); }
    color([0.55,0.55,0.58]) for (s=[1,-1])                // outboard sleeves ≈7
      translate([0,0, s*(sleeve_z0 + sleeve_ln/2)]) difference(){
        cylinder(h=sleeve_ln, d=bushing_od, center=true);
        cylinder(h=sleeve_ln+2, d=pivot_d+0.4, center=true); }
    // 6 thrust washers: spacer↔trailing flange, trailing↔leading boss faces
    // (the scissor interface), leading flange↔outboard sleeve
    color([0.8,0.8,0.82]) for (s=[1,-1])
      for (zz=[sp_half+0.75, zi_tr+plate_t+0.75, sleeve_z0-0.75])
      translate([0,0, s*zz]) difference(){
        cylinder(h=1.5, d=30, center=true);
        cylinder(h=2.5, d=pivot_d+0.4, center=true); }
  }
}

module track3d(){
  color([0.08,0.08,0.09,0.38]) translate([0,0,-belt_w/2])
    linear_extrude(belt_w) difference(){
      offset(r=T) hull(){
        circle(r=r_wrap);
        translate(wheel_tr) circle(d=D+2);
        translate(wheel_ld) circle(d=D+2); }
      hull(){
        circle(r=r_wrap);
        translate(wheel_tr) circle(d=D+2);
        translate(wheel_ld) circle(d=D+2); }
    }
}

// ============================================================== top level
if (render_mode == "plates"){
  // Rev 011: compact nesting of the COMPLETE cut list for DXF export / 1:1
  // printing. Earlier revisions omitted the welded offcuts (brace webs and
  // tensioner lugs), so the DXF was not the whole job. Everything is here now:
  // ONE POD's worth, verified against the 3D: 2 carriers + 4 arm bars (2
  // trailing slotted + 2 leading) + 4 tab stubs + 2 brace webs (1 per arm,
  // different lengths) + 2 tensioner lugs (both on the trailing arm, one per
  // fork plate). Cut everything TWICE for the vehicle.
  carrier_2d();                                             // carrier L
  translate([60, 0]) mirror([1,0]) carrier_2d();            // carrier R
  translate([135, 40])  arm_plate_2d(true);                 // trailing ×2
  translate([135, -10]) arm_plate_2d(true);
  translate([135, -60]) arm_plate_2d(false);                // leading ×2
  translate([135, -110]) arm_plate_2d(false);
  translate([0, -190]) for (i=[0:1])          // tab stubs ×2 — FRONT POD ONLY
    translate([i*95, 0] - [-20,-20])           // (rear-pod blades carry the eye);
      tab_stub_2d(upP);                        // mirror pair, flip one over
  translate([0, -245]){                       // brace webs: 1 per arm = 2/pod
    square([brace_tr, brace_w]);                            // trailing 50.8
    translate([60, 0]) square([brace_ld, brace_w]);         // leading  66.5
  }
  translate([150, -245]) for (i=[0:1])        // pusher blocks: 2/pod, both on
    translate([i*32, 0]) difference(){        // the TRAILING arm (one per plate)
      square([lug_l, lug_h_pl]);              // drill 5.0+tap M6, or 6.6+weld nut
      translate([lug_l/2, 7]) circle(d=6.6); }
  if (use_bracket) translate([0, -300]){      // REV 011d MERGED bracket plates:
    for (i=[0:1]) translate([305, -i*50])     // backing strips x2 — leg INNER
      difference(){                           // face, no-weld sandwich layer
        square([brk_pad_l, brk_blade_w]);
        for (fx=[15,50]) for (fy=[13,27])
          translate([brk_pad_l - fx, fy]) circle(d=10.5); }
    for (i=[0:1]) translate([0, -i*50])       // i=0 TRAILING 262, i=1 LEADING 210
      difference(){                           // — two DISTINCT plates, mark L/R
        square([brk_cut_x + brk_pad_l + (i==0 ? 72 : 20), brk_blade_w]);
        translate([brk_pad_l + brk_cut_x, brk_axle_up]){
          axle_key_2d();
          for (yy=[-12,12]) translate([0,yy]) circle(d=8.4);
          translate(i==0 ? upP : [-upP[0], upP[1]]) circle(d=8.4);
          for (fx=[15,50]) for (fy=[-7,7])
            translate([-(brk_cut_x + fx), fy]) circle(d=10.5); } }
  }
} else if (render_mode == "part"){
  part_catalog(part);
} else if (render_mode == "bracket"){
  // ---- REV 011d close-up: the rear-fork bracket, one side (+z, trailing),
  // every layer labeled. Open Window -> Customizer, set render_mode to
  // "bracket", and orbit — this is the whole 'how does the pod hang from
  // the cut fork' story in one picture. Layers from the scooter outward:
  //   fork leg 4 (ghost) -> packing 11 -> BLADE -> hub nut
  // and inboard of the blade: the carrier, on the same keyed axle.
  bz0 = cz + carrier_t;                       // blade inner face |z| = 80
  // carrier (cropped to the hub region so the bracket is not buried)
  color([0.36,0.43,0.56]) translate([0,0,cz]) linear_extrude(carrier_t)
    intersection(){ carrier_2d(); translate([-21,-45]) square([42,110]); }
  // blade: full length, key + eye + lower bolt row
  color([0.20,0.55,0.30]) translate([0,0,bz0]) linear_extrude(brk_t)
    difference(){
      translate([-(brk_cut_x + brk_pad_l), -brk_axle_up])
        square([brk_cut_x + brk_pad_l + 72, brk_blade_w]);
      axle_key_2d();
      for (yy=[-12,12]) translate([0,yy]) circle(d=8.4);  // M8 to carrier
      translate(upP) circle(d=8.4);
      for (fx=[15,50]) for (fy=[13,27])
        translate([-(brk_cut_x + fx), -brk_axle_up + fy]) circle(d=10.5);
    }
  // ghost fork-leg stub + packing
  color([0.45,0.50,0.60,0.35]) translate([-(brk_cut_x + brk_pad_l),
    -brk_axle_up, brk_leg_gap/2]) cube([brk_pad_l, brk_leg_h, leg_t]);
  color([0.55,0.55,0.58,0.6]) translate([-(brk_cut_x + brk_pad_l),
    -brk_axle_up, brk_leg_gap/2 + leg_t]) cube([brk_pad_l, brk_leg_h, brk_pack]);
  // the 4 M10 bolts, drawn through their true stacks
  color([0.20,0.55,0.30]) translate([-(brk_cut_x + brk_pad_l),
    -brk_axle_up, brk_leg_gap/2 - brk_t]) cube([brk_pad_l, brk_blade_w, brk_t]);
  color([0.55,0.55,0.58]) for (fx=[15,50]) for (fy=[13,27])
    translate([-(brk_cut_x + fx), -brk_axle_up + fy, brk_leg_gap/2 - brk_t - 6])
      cylinder(h=56, d=9.8);
  // 2x M8 blade-to-carrier bolts (reused carrier-to-leg M8x30s)
  color([0.55,0.55,0.58]) for (yy=[-12,12])
    translate([0, yy, cz - 6]) cylinder(h=26, d=7.8);
  // hub axle + nut clamping carrier + blade
  color([0.55,0.55,0.58]) cylinder(h=2*(bz0+brk_t)+16, d=axle_d, center=true);
  color([0.45,0.45,0.48]) translate([0,0,bz0+brk_t+2])
    difference(){ cylinder(h=8, d=17, $fn=6); cylinder(h=10, d=10, center=true); }
  // shock eye pin
  color([0.55,0.55,0.58]) translate([upP[0], upP[1], bz0-2])
    cylinder(h=brk_t+12, d=7.8);
  flag("FORK LEG STUB - CUT AT 65 (GHOST)",
       [-(brk_cut_x+30), 20, brk_leg_gap/2+2],   [-(brk_cut_x+90), 70, 95]);
  flag("BACKING STRIP 65x40 - NO WELD TO FORK",
       [-(brk_cut_x+58), -10, brk_leg_gap/2 - brk_t],  [-(brk_cut_x+170), -55, 95]);
  flag("PACKING 17 = 6+6+5",
       [-(brk_cut_x+55), 0, brk_leg_gap/2+leg_t+5], [-(brk_cut_x+150), 30, 95]);
  flag("BLADE - 2x2 M10 (35x14), KEY, EYE",
       [-(brk_cut_x-30), 15, bz0+brk_t],         [-(brk_cut_x-30), -60, 95]);
  flag("CARRIER - SAME KEYED AXLE",
       [0, -35, cz],                              [60, -80, 95]);
  flag("2x M8 BLADE-TO-CARRIER (+WELD AT FINAL)",
       [0, -14, cz + carrier_t + brk_t + 4],     [-60, -75, 95]);
  flag("HUB NUT CLAMPS CARRIER+BLADE",
       [0, 8, bz0+brk_t+8],                       [60, 55, 95]);
  flag("SHOCK EYE PIN",
       [upP[0], upP[1], bz0+brk_t+10],            [upP[0]+40, upP[1]+35, 95]);
} else if (render_mode == "tensioner"){
  // ---- Sheet-6 close-up: trailing-arm belt tensioner, arm drawn level ----
  // (local arm coords: pivot at x=0, wheel end +x = rearward)
  zo = zi_tr + plate_t;
  intersection(){                                    // fork plates, cropped
    for (s=[1,-1]) translate([0,0, s==1 ? zi_tr : -zi_tr-plate_t])
      linear_extrude(plate_t) arm_plate_2d(true);
    translate([C-45, -65, -zo-40]) cube([150, 130, 2*zo+80]);
  }
  tensioner_hw(zi_tr);
  color([0.55,0.55,0.58]) translate([C + tension_pos, 0, 0])   // axle
    cylinder(h=2*(zo+18), d=G, center=true);
  color([0.16,0.16,0.17,0.25]) translate([C + tension_pos, 0, 0])
    cylinder(h=H, d=D, center=true);                           // ghost wheel
  flag("AXLE IN SLOT (25 TAKE-UP)",
       [C + tension_pos, -8, zo+2],  [C-52, -52, zo+26]);
  flag("Ø15 PUSH COLLAR ON THE STUD",
       [C + tension_pos, 7, zo+6],   [C-52, 42, zo+26]);
  flag("WELDED PUSHER BLOCK",
       [C-18, -12, zo+7],            [C+30, -34, zo+26]);
  flag("M6 PUSH BOLT + JAM NUT",
       [C-30, 0, zo+7],              [C+34, 24, zo+26]);
} else {
  // trailing arm (rear, +x) and leading arm (front, -x, mirrored)
  translate([ ex*60, 0, 0]) arm3d(zi_tr, true,  aT, +1);
  translate([-ex*60, 0, 0]) mirror([1,0,0]) arm3d(zi_ld, false, aL, -1);

  carrier_group();
  pivot_axle_group();

  if (show_shocks){
    translate([0,0,  ex*80]) shock3d(upP,     arm_pt([a,shock_y], aT),      sz);
    translate([0,0, -ex*80]) shock3d(mx(upP), mx(arm_pt([a,shock_y], aL)), -sz);
    if (show_force){
      translate([0,0,  ex*80]) force_gauge(aT,  sz+16, false);
      translate([0,0, -ex*80]) force_gauge(aL, -sz-16, true);
    }
  }
  if (show_sprocket) translate([0, ex*150, 0]) sprocket();
  if (show_track && ex == 0) track3d();
}
