// ############################################################################
// #  REV 012 (2026-09-10) — THIS FOLDER. The POD is Rev 011, unchanged.     #
// #  New: the scratch-built NARROW FRAME with the batteries in line and the  #
// #  rear pod's green plates bolted to the rails' inner faces. Find it in    #
// #  render_mode="chassis" and the REV 012 block after the Rev 011d params.  #
// ############################################################################
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
render_mode = "assembly"; // [assembly, exploded, plates, tensioner, bracket, chassis, chassis_link, chassis_plates, part]
// render_mode="chassis": REV 012 — the whole vehicle: narrow 100x40x2 frame,
// 2 batteries in line, rear pod on 60x6 green plates bolted to the rails'
// inner faces (4 bolts), front pod in the donor fork.
// render_mode="chassis_link": labelled close-up of how the rear pod hangs on the
// rails; link_explode pulls the pod back out.
// render_mode="chassis_plates": the green plates laid flat for DXF / 1:1 print.
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
fork_gap = 177;  // inner spacing between fork legs.
                 // REV 013, 2026-09-18 — THE STACK IS INVERTED. Owner is
                 // building his OWN fork, and it BOLTS TO THE CARRIER PLATE'S
                 // OUTER FACE. Up to Rev 012 it was the other way round: the
                 // carrier was bolted to the fork leg's outer face, so cz was
                 // derived FROM fork_gap. Now the carriers are the reference
                 // and the fork follows them:
                 //     fork_gap = 2 x (cz + carrier_t) = 2 x (82.5 + 6) = 177
                 // The donor fork (117.7) and the Rev 011d blade conversion are
                 // both irrelevant now — owner 2026-09-18, "forget about the
                 // donor one". Belt clears the legs by 29.5 mm per side, up
                 // from 11, because the legs moved outboard of the carriers.
                 // Guarded against cz + carrier_t below; change one, not both.
                 // (Rev 003 — re-measured; both pods identical, was 120/140)
leg_t    = 4;    // fork leg thickness (z) — MEASURED 2026-07-13 (was 30 placeholder)
carrier_shim = 0;   // NO LONGER SETS THE CARRIER POSITION. cz is measured now
                 // (see cz_meas), and with the fork bolting to the carrier's
                 // outer face there is no fork-to-carrier shim in the stack at
                 // all. The 19 mm the owner measured is the OUTBOARD PIVOT
                 // SLEEVE on the M16 axle, which the model derives for itself
                 // as sleeve_ln and echoes in the PIVOT STACK line — check that
                 // echo against your 19 mm rather than setting it here. Rev 012 briefly tried to buy the
                 // same room by inventing fork_gap=168; that was reverted. The
                 // gap stays the donor's measured 140 and the extra width is
                 // recorded here as the hardware it actually is.
                 // Consequences, all good: cz clears the belt (94 > 59+24), so
                 //   the shocks flip INBOARD to |z|=73 on their own and the
                 //   lower shock lever drops 62 -> 41 mm; the bay opens to 212
                 //   so the Ø165 speaker hole keeps 23.5 mm to the rail.
                 // Costs: pivot axle M16x190 -> M16x230.
                 // CAUTION: a shim of 1..8 mm leaves the shocks OUTBOARD and
                 //   only pushes them further out, making that bolt WORSE (up
                 //   to 598 MPa). 9 mm is the flip. Do not fit a part shim.
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
use_bracket   = false;  // OFF 2026-09-18: the whole Rev 011d bracket existed
                        // only to work around the DONOR rear fork. Owner is
                        // building his own fork, so there is nothing to work
                        // around. Assembly now renders the Rev 011c tab stubs.
// REV 012 (owner, 2026-09-10): "why do we need the green plate at all?" —
// we don't, once the deck goes. The whole Rev 011d bracket exists to work
// around ONE fact: the donor's rear fork has a 117.7 inner gap and the belt
// is 118 wide. We were bending over backwards not to modify a fork we are
// now cutting off and throwing away. In chassis mode the bracket is FORCED
// OFF and the carriers pick up on the new frame directly.
use_bracket_eff = (render_mode == "chassis") ? false : use_bracket;
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

// ############################################################################
// #  REV 012 — NARROW FRAME, BATTERIES IN LINE (owner, 2026-09-10)          #
// #                                                                          #
// #  Forked from the Rev 011 folder; the POD is unchanged. The donor deck is #
// #  scrapped; the FRONT pod stays in the donor front fork (it steers).      #
// #  Behind it:                                                              #
// #    - two RAILS of 100x40x2 (BOUGHT), 100 side vertical, whose INNER      #
// #      faces lie FLAT on the two GREEN PLATES (60x6, BOUGHT). No tabs, no  #
// #      slots: 2x M12 per side go through the rail (steel sleeve welded     #
// #      inside) into a nut welded on the green plate. The whole rear pod    #
// #      comes off with 4 bolts.                                             #
// #    - so the rails are only 172 apart inside, and the two battery packs   #
// #      (400 x 110 x 80, MEASURED) sit ONE BEHIND THE OTHER between them,   #
// #      on a plywood tray, under a plywood lid.                             #
// #    - a front and a rear cross member (100x40x2) keep the rails square.   #
// #    - the WHEELBASE follows from the batteries — derived, not chosen.     #
// #                                                                          #
// #  WHY FLAT: the hub plate is a 40x6 strip; anything grabbing it from the  #
// #  side bends it like a page. A rail wall lying flat on the green plate    #
// #  loads everything in its own plane — the way the scooter fork did.       #
// #  WHY THE RAILS END SHORT: the front shock stands at x -46..-52 on the    #
// #  left, so both rails stop in front of it (guarded).                      #
// #                                                                          #
// #  Steel sizes are real (bought). Numbers marked TBD are guesses.          #
// #  The front fork -> frame link is NOT designed yet (owner: later).        #
// ############################################################################

/* [Chassis — REV 012: narrow frame, batteries in line] */
show_chassis_labels = true;
show_batteries      = true;
show_speakers       = true;
show_lid            = true;
show_tray           = true;
link_explode = 0;   // [0:10:150] chassis_link view: pull the rear pod back out of the rails

// -- vehicle ------------------------------------------------------------------
front_cm_x  = 210;  // TBD front cross member FRONT face, behind the front axle.
                    //     Must stay behind the front pod when it steers (guarded).
rear_ct_x   = 190;  // rear cross member REAR face, AHEAD of the rear hub axle.
                    //     Must clear the rear track (guarded).
rider_kg    = 130;  // TBD rider + luggage; strength checks use 2x this

// -- batteries (MEASURED by the owner, 2026-09-10) ----------------------------
batt_l      = 400;
batt_w      = 110;
batt_h      = 80;
batt_n      = 2;    // one behind the other
batt_gap    = 20;   // between the two packs
batt_end_clr = 10;  // pack to cross member, each end
bay_len_set = 1000; // clear bay the owner asked for. The bay never goes below
                    //   what the packs AND the speaker wells need (guarded);
                    //   any spare sits behind the rear pack.

// -- speakers: one 6.5" firing UP through the deck at each end ----------------
// The well is a sealed box made of parts that are already there: the two rail
// inner faces are its sides, the tray is its floor, the lid is its top, the
// cross member is its outer end. Only the inner end is new (a plywood bulkhead).
spk_cut_d   = 165;  // TBD MEASURE — the HOLE in the lid, not the rim. The owner
                    //   gave Ø165 x 50 for the driver. Many 6.5" units need a
                    //   hole of only ~147: set the real number here and the
                    //   wells, the bay and the wheelbase all shrink with it.
spk_depth   = 50;   // driver depth below the lid (MEASURED)
spk_rim_d   = 190;  // TBD the rim that lands on the lid (drawn only)
spk_edge    = 8;    // cutout edge -> bulkhead face / cross member face
spk_bhd_t   = 12;   // plywood bulkhead that seals the well off from the batteries
spk_disp    = 0.4;  // TBD litres the driver itself takes out of the box

// -- frame: 100x40x2 rectangular tube, 100 side VERTICAL (BOUGHT) ------------
fr_h        = 100;
fr_w        = 40;
fr_t        = 2;
lid_t       = 12;   // TBD plywood lid (you stand on it)
tray_t      = 12;   // TBD plywood battery tray
lid_over    = 25;   // TBD lid overhang past each rail, for foot room
wood_rho    = 6.0e-7; // kg/mm³, birch plywood ~600 kg/m³
wood_limit  = 15;   // MPa, plywood bending with margin

// -- green plate 60x6 (BOUGHT) + the rail joint --------------------------------
gp_w        = 60;
gp_t        = 6;
gp_gap      = 2;    // green plate front end -> rear cross member
gp_spring_clr = 3;  // green plate bottom edge -> top of the spring
rl_shock_clr = 8;   // rail rear end ahead of the front shock (coil guard)
rl_end_edge = 25;   // rear M12 centre from the rail's rear end (sleeve hole Ø25)
gp_end_edge = 20;   // front M12 centre from the green plate's front end
bolt_d      = 12;   // M12 10.9
bolt_preload = 50000; // N — M12 10.9 at ~100 N·m
bolt_mu     = 0.2;  // clean dry steel
sleeve_od   = 25;   // steel sleeve welded inside the rail at each bolt, so the
sleeve_id   = 13;   //   2 mm walls are not crushed by the bolt (guarded)

// -- top of the shock (MEASURED) ---------------------------------------------
coil_d      = 45;   // MEASURED 2026-09-18 by the owner: the spring coil is 45
                    // across. Was hard-coded as 44 (r22) in three separate
                    // guards and two label strings, none of which were linked
                    // to each other. Now they all read this one number.
shock_perch_d = coil_d; // widest part at the top of the spring (tilt check)
shock_neck  = 25;   // MEASURED 2026-09-10: TOP eye centre -> top of the SPRING

// -- front end: donor head tube + fork (ghost; link TBD) ----------------------
head_ang    = 72;   // TBD head tube angle from the GROUND
fork_off    = 30;   // TBD front axle ahead of the steering axis
fork_len    = 340;  // TBD front axle -> head tube BOTTOM, along the fork
head_len    = 220;  // TBD head tube length
head_od     = 45;   // TBD head tube OD
stock_axle_h = 116; // TBD donor front axle height on its ORIGINAL wheel
steer_lock  = 35;   // TBD steering lock each way, degrees (guarded)

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

/* [Lower shock mount — REV 013: DOUBLE SHEAR] */
// THE FIX REV 012 KEPT WARNING ABOUT. Up to Rev 012 the lower shock eye hung
// off a CANTILEVER: an M8 bolt in a Ø15×Ø9 sleeve, supported only by the arm
// plates, with the eye on the free outboard end. 530 MPa at full bump with
// the shocks outboard, 351 with them inboard — both past the 235 MPa yield of
// mild steel, before any impact. Worse, the bare bolt in the span BETWEEN the
// two arm plates carried nearly the same moment on 1/12 of the section.
// Rev 013 (owner, 2026-09-16) closes both: the Ø15×Ø9 sleeve runs CONTINUOUS
// from the far arm plate, through the near plate, through the shock eye and
// into a new outer STRAP plate. The eye load is now caught between two
// supports, and the bolt is only a clamp — it never sees bending anywhere.
ds_strap  = true;  // OWNER 2026-09-18: switched off for a look at the bare
                   // cantilever, back ON 2026-09-19. With it false the lower
                   // pin is at 304 MPa against a 235 limit, and no width
                   // change fixes that — widening the pod moves the eye
                   // FURTHER from the arm plate and makes it worse.
ds_t      = 6;     // strap thickness — 40x6 bar, the stock already in the BOM
ds_clr    = 1;     // running clearance, shock eye outer face to strap inner face
ds_eye_w  = 24;    // shock LOWER EYE WIDTH across the boss — MEASURED 2026-09-18
                   // by the owner: the eye tube is 24 long. Was a 10 guess.
ds_eye_bore = 8;   // shock LOWER EYE BORE — MEASURED 2026-09-18 by the owner:
                   // Ø8, and an M8 bolt runs through a Ø9xØ15 sleeve. So the
                   // sleeve CANNOT pass through the eye: Ø15 will not go into
                   // Ø8. The sleeve stops either side and the bare M8 crosses
                   // the eye alone, on about 1/11 of the sleeve's section.
                   // That bare span is now the weakest part of the pod.
                   // Was 15, which assumed the eye rode on the sleeve. THIS
                   // WHOLE BRACKET, and the build notes disagree with themselves:
                   // FASTENERS.md §D says "eyes measured Ø8" on one line and
                   // "eye rides the spacer sleeve" (Ø15 OD) on the next. The
                   // owner's own account is that the eye rides the pipe, so Ø15
                   // is the default. If yours is Ø8, change it here and the
                   // model rebuilds the mount around it.
                   //   >= lsb_od — the sleeve passes THROUGH the eye. One sleeve,
                   //     one outer strap, no bare bolt anywhere. ~70 MPa.
                   //   <  lsb_od — the sleeve must stop at the eye and the bolt
                   //     crosses it bare on 1/11 of the section. The model then
                   //     adds an INNER JAW so the eye is gripped from both sides
                   //     ds_clr away, which is the only thing that keeps the bare
                   //     span short, and checks the bolt against ds_bolt_y.
ds_bolt_y = 1100;  // through-bolt proof strength, MPa: 640 = cl.8.8,
                   // 940 = cl.10.9, 1100 = cl.12.9. Only used when the bolt
                   // runs bare through an eye — which, with a Ø8 bore, is both
                   // ends of both shocks. Checked at half of it, safety factor 2.
                   // OWNER 2026-09-19: the pins stay M8, so cl.12.9 is not a
                   // preference, it is the only grade that carries them. A
                   // cl.10.9 M8 allows 470 and the lower pin sits at 504.
                   // Buy these as cl.12.9 and mark them — a shop-drawer 8.8
                   // put in the same hole is at three times its limit.
ds_pin_d  = 8;     // bare pin across the eyes: 8 = M8, as the eyes are bored
                   // today. 10 = M10, which needs the Ø8 bores opened out, and
                   // roughly halves every bending figure below because the
                   // section goes as d³. Check first whether the eye holds a
                   // pressed bushing — if it does, its own bore may already be
                   // big enough and nothing needs drilling.
function pin_root(d) = d == 6 ? 4.77 : d == 8 ? 6.47 : d == 10 ? 8.16
                     : d == 12 ? 9.85 : 0.81*d;   // ISO coarse thread minor Ø
ds_eye_od = 20;    // shock LOWER EYE OUTER diameter, across the boss — MEASURE
                   // YOURS. It MUST be bigger than lsb_od (15), because with a
                   // Ø8 bore the sleeve cannot pass through and has to butt
                   // against this face instead. Guarded below.
ds_spring = 12;    // lower eye centre -> bottom of the spring — MEASURE YOURS.
                   // This is what caps how far the strap may reach ABOVE the
                   // eye, so it sets the strap's edge distance. Guarded below.
ds_gus_t  = 6;     // gusset thickness
ds_gus_x  = 30;    // the two gussets stand this far fore and aft of the eye,
                   // along the arm. It is a real trade, not a clearance
                   // minimum: the further out they stand, the less the coil
                   // crowds them at full droop, so the deeper they may be cut
                   // and the less they bend. Model says, with ds_end following:
                   //   26 -> 21.5 deep, 114 MPa   30 -> 28.5 deep, 65 MPa
                   //   34 -> 38 deep,    36 MPa   38 -> 40 deep,   33 MPa
                   // 34 and up would push the strap's inboard end into the Ø22
                   // pivot sleeve, so 30 is as far as the geometry allows.
ds_gus_notch = 4.5; // half-width of the SLOT up the outboard gusset's inboard
                   // edge. The trailing arm's M6 tensioner push bolt (Ø5.8)
                   // runs along the arm 7 mm off that edge and would otherwise
                   // pierce the gusset. Drill Ø9 on the bolt axis, then file
                   // out to the edge. Both arms get it, so the four gussets of
                   // a pod cut to one pattern.
ds_end    = 8;     // strap steel past each gusset line. Do not just make this
                   // bigger: the inboard end swings past the Ø22 pivot sleeve,
                   // which is guarded below. With ds_gus_x = 30 it leaves 2 mm.

/* [Upper shock mount — REV 013: DOUBLE SHEAR] */
// The upper eye carried the SAME fault as the lower one, and unlike the lower
// one nothing was watching it. Rev 011c hung the eye pin off a single stub —
// the comment at tab_stub_2d says so outright, "the eye pin cantilevers from
// the stub out to the shock plane through washers". A shock pushes equally
// hard at both ends, so that pin saw the same 2681 N on a 12 mm lever with
// nothing on its far side: 1210 MPa with an M8, past even a cl.12.9 pin.
// The cure is the shape the lower mount already uses: a SECOND stub on the
// eye's inner face, keyed on the same hub axle, so the axle nut clamps both
// and the pin is held at both ends. It is the mirror of the outer stub, which
// tab_stub_2d already produces — the pod now cuts four of that blank, not two.
// Room for it, all guarded below:
//   - it sits at |z| 39.5..45.5, which IS inside the lug rows (31..49), but
//     its far corner is only 66 from the axle and the lug tips sweep 84, so
//     it passes under them;
//   - the Ø123 motor casing ends at |z| 21.5, well inboard of it;
//   - the drum is 35 wide, so |z| 17.5. Nothing else lives in that slice.
us_clevis = true;  // false renders the Rev 011c cantilever, for comparison
us_t      = 6;     // inner stub thickness — same 40x6 bar as the outer one
us_clr    = 1;     // running clearance, shock eye face to inner stub
us_bear_t = 6;     // how much of the OUTER stub the pin actually bears on.
                   // stub_t is 12 = two 40x6 bars, and if the pin were a snug
                   // fit through both, its outer support would sit 6 mm out at
                   // the pair's mid-plane — a longer lever, 552 MPa, over the
                   // 550 a cl.12.9 M8 allows. Drill the INNER bar Ø8.4 and the
                   // OUTER one Ø12 clearance and the pin bears on the inner bar
                   // alone, 3 mm from the eye instead of 6. 478 MPa. It costs a
                   // different drill bit on one of two plates that are being
                   // cut anyway. Set this to stub_t to model a snug pin in both.

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
// REV 013, 2026-09-18: cz IS A MEASUREMENT NOW, not a calculation.
// The pods are BUILT. Their width is a fact to be read off with a tape, and
// every attempt to derive it from fork_gap + leg_t + shim has been wrong,
// because the chain depends on which fork the pod has and how the shim stacks.
// The owner measured 165 mm CLEAR between the two carrier plates' inner faces,
// so each one is at 82.5.
cz_meas = 82.5;                        // = 165/2, MEASURED 2026-09-18
cz      = cz_meas;
// The old chain is kept, but only to be CHECKED against the tape below.
// The fork follows the carriers now, so this is the relationship to check.
cz_calc = fork_gap/2 - carrier_t;

// Shock plane. Also a measurement now, for the same reason: the owner reports
// the shocks run INBOARD, mounted on the inner face of the stubs. The old rule
// (cz >= track_w/2 + 24) computes FALSE at cz=82.5 — it misses by 0.5 mm — and
// would silently flip the whole shock design to the wrong side of the plate.
// A built pod does not get its layout guessed at. State it, then guard it.
shocks_inboard = true;                 // OWNER 2026-09-18, measured
// The upper shock stubs. OWNER 2026-09-18: "the stubs are from inside", and
// "the carrier plates are the last and first plates regarding z". So the stub
// lies against the carrier's INNER face, and the shock hangs off the stub's
// inner face in turn. This read cz + carrier_t in three places, which put the
// stub OUTBOARD — exactly where the new fork now bolts.
stub_t  = 12;                          // 2026-09-19: 6 (one 40x6 bar, Rev 011c)
                                       // left the lower strap 1 mm INSIDE the
                                       // carrier plate. The stub is what spaces
                                       // the shock off the carrier, so thicken
                                       // it and the whole mount moves inboard
                                       // into clear air. 11 is the minimum;
                                       // 12 = two 40x6 bars, stock already here.
                                       // This does NOT widen the pod: carriers
                                       // stay 165 apart, fork gap stays 177.
tab_z0  = cz - stub_t;                 // 70.5 — stub INNER face |z|
// Shock centre plane. Inboard, the shock hangs on the stub's INNER face, so
// the plane is set by the stub and the eye's own width — not by a guess at
// "14 mm off the belt edge", which is what this used to say.
sz     = shocks_inboard ? tab_z0 - ds_eye_w/2
                        : cz + carrier_t + 14;  // outboard of the carrier plate
// ---- Rev 013 double-shear lower shock mount, derived ----------------------
lsb_od  = 15;         // spacer sleeve OD  (FASTENERS.md §D)
lsb_id  = ds_pin_d+1; // spacer sleeve ID — follows the pin. Going to M10 bores
                      // this out to 11, which makes the SLEEVE weaker, not
                      // stronger. That only matters where the sleeve is the
                      // beam, i.e. with ds_strap off.
ds_z0   = sz + ds_eye_w/2 + ds_clr;    // 79 — strap INNER face |z|
ds_z1   = ds_z0 + ds_t;                // 85 — strap OUTER face |z|
ds_zs   = ds_z0 + ds_t/2;              // 82 — strap mid-plane, the 2nd support
// Does the Ø15 sleeve fit through the shock eye, or must it stop at it?
ds_thru = ds_eye_bore >= lsb_od;
// INNER JAW — built only when the sleeve cannot pass through the eye. It is the
// mirror of the strap on the other face of the eye, and it exists for exactly
// one reason: without it the nearest support is the arm plate, 44 mm away, and
// the bare bolt in the eye sees 629 MPa. With it the bare span is ds_eye_w plus
// two clearances and the bolt is fine.
ds_j1   = sz - ds_eye_w/2 - ds_clr;    // inner jaw OUTER face |z|
ds_j0   = ds_j1 - ds_t;                // inner jaw INNER face |z|
ds_jn   = ds_j1 - ds_t/2;              // inner jaw mid-plane, the 1st support
// where the sleeve stops on the shock side
ds_sl_out = ds_thru ? ds_z1 : ds_j1;
// ---- Rev 013 double-shear UPPER shock mount, derived ----------------------
// The eye sits against the outer stub's inner face, so the outer support is
// that stub and the inner one is the new stub, ds_clr off the eye's other face.
us_j1   = sz - ds_eye_w/2 - us_clr;    // 45.5 — inner stub OUTER face |z|
us_j0   = us_j1 - us_t;                // 39.5 — inner stub INNER face |z|
us_jn   = us_j1 - us_t/2;              // 42.5 — inner stub mid-plane, support 1
us_sn   = tab_z0 + us_bear_t/2;        // 73.5 — outer support: the mid-plane of
                                       // the bearing length, measured from the
                                       // stub's INNER face, which is the face
                                       // the eye lies against
us_span = us_sn - us_jn;
// Far corner of tab_stub_2d from the hub axle: the blank runs x -20..63 and
// y -20..20, so the worst corner is the outboard bottom one. This is what has
// to duck under the lug tips, because the inner stub stands in the lug rows.
us_corner = norm([63, 20]);
// Strap top edge: the spring stops the strap climbing past the eye, so the
// edge distance above the Ø15 bore is whatever ds_spring leaves. The load at
// full bump pushes the eye DOWN, so the steel that matters is below the bore
// (a full 20 mm, the bar's half width); the thin lip above only has to hold
// the 318 N of full droop. Guarded below.
ds_top  = boss_disc/2;                 // 20 — strap blank is the full bar width;
                                       // ds_coil_cut_2d carves the top edge back
                                       // to whatever the spring actually allows
ds_bot  = boss_disc/2;                 // 20 — strap bottom edge, flush with the bar
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

// ---- lower shock mount (checked since 2026-09-10, FIXED in Rev 013) --------
// Rev 012 and earlier: the eye rides an M8 through-bolt + Ø15×Ø9 spacer sleeve
// (FASTENERS.md §D) supported ONLY by the arm plates, with its outboard end
// free. The shock force bends it as a CANTILEVER from the arm plate's outer
// face out to the eye centre. That is the 530/351 MPa warning.
// Rev 013: the sleeve is continuous into an outer strap, so the eye load sits
// BETWEEN two supports — the near arm plate and the strap — and the peak
// moment is F·a·b/L instead of F·L. Section: the SLEEVE ALONE. Rev 012 added
// the bolt's minor diameter to it; with the sleeve now continuous the bolt is
// a clamp, not a beam, so leaving it out is both truer and conservative.
// STATIC spring force at full bump — a real impact is higher.
lsb_Z   = PI*(pow(lsb_od,4) - pow(lsb_id,4))/(32*lsb_od);
lsb_F   = spring_rate*(shock_ee - shock_len(bump_max));
// per arm: [name, near arm plate OUTER face |z|, that plate's MID-plane |z|]
ds_arms = [["trailing", zi_tr + plate_t, zi_tr + plate_t/2],
           ["leading",  zi_ld + plate_t, zi_ld + plate_t/2]];
// Bolt minor-diameter section — what is left where the sleeve cannot follow.
ds_Zb = PI*pow(pin_root(ds_pin_d),3)/32;
for (arm = ds_arms) let(
    // Rev 012 cantilever: arm plate outer face -> eye.
    // Rev 013 two supports, load at sz between them. Which pair of supports
    // depends on whether the sleeve gets through the eye: if it does, the arm
    // plate is the near one; if it does not, the inner jaw is.
    lsb_near = !ds_strap ? arm[2] : ds_thru ? arm[2] : ds_jn,
    lsb_span = ds_zs - lsb_near,
    // Spread the eye's grip over its own width — a point load overstates it.
    lsb_M    = ds_strap ? lsb_F * (sz - lsb_near) * (ds_zs - sz) / lsb_span
                          - lsb_F * ds_eye_w / 8
                        : lsb_F * (sz - arm[1]),
    // and which section carries that moment
    lsb_bare = ds_strap && !ds_thru,
    lsb_s    = lsb_M / (lsb_bare ? ds_Zb : lsb_Z),
    lsb_lim  = lsb_bare ? ds_bolt_y/2 : 235)
  echo(str(lsb_s > lsb_lim ? "*** WARN " : "PASS ",
           "lower shock ", lsb_bare ? "BOLT" : "sleeve", " bending, ", arm[0],
           " arm: ",
           !ds_strap ? str("CANTILEVER lever ", round(sz - arm[1]), " mm")
           : str("double shear over ", round(lsb_span), " mm span, ",
                 lsb_bare ? str("bare M", ds_pin_d, " across the eye")
                          : "sleeve right through"),
           ", ", round(lsb_F), " N at full bump -> ", round(lsb_s), " MPa (limit ",
           round(lsb_lim), ")",
           lsb_s > lsb_lim ? " — Support the eye's OUTER end (double shear: clevis / outer strap), or a much stiffer pin." : ""));

// ---- UPPER shock eye pin: the check that never existed ---------------------
// Every revision up to here guarded the lower eye six ways and the upper eye
// not at all, which is how a 1210 MPa cantilever sat in the drawings unnoticed
// from Rev 011c to Rev 013. A shock carries the same force at both ends, so
// lsb_F is the load here too. Bare pin either way: the Ø8 eye bore takes no
// sleeve, exactly as at the lower end.
let(us_M = us_clevis
             // load between two supports, its grip spread over the eye width
             ? lsb_F*(sz - us_jn)*(us_sn - sz)/us_span - lsb_F*ds_eye_w/8
             // Rev 011c: pin held by the outer stub only, eye hanging inboard
             : lsb_F*(tab_z0 - sz),
         us_s = us_M / ds_Zb,
         us_lim = ds_bolt_y/2)
  echo(str(us_s > us_lim ? "*** WARN " : "PASS ",
           "upper shock PIN bending: ",
           us_clevis ? str("double shear over ", round(us_span), " mm span")
                     : str("CANTILEVER lever ", round(tab_z0 - sz), " mm"),
           ", bare M", ds_pin_d, " across the eye, ", round(lsb_F),
           " N at full bump -> ", round(us_s), " MPa (limit ", round(us_lim), ")",
           us_s > us_lim
             ? " — set us_clevis, raise ds_bolt_y, or open the eye for ds_pin_d=10."
             : ""));

// ---- Rev 013: does the bracket clear the coil, at every arm angle? ---------
// The crude "how far along the arm is the gusset" test is not enough: the shock
// leans ~10 deg off the arm's normal and the bracket steel stands 6..12 mm out
// of the shock's own plane, so the real gap is a 3D one and it changes as the
// arm swings. Measure it properly — perpendicular distance from the shock axis,
// counting only the part of the axis the spring actually occupies.
// p is an ARM-LOCAL point [x, y, |z|]; t is the arm angle.
function ds_axis(t) = let(e = arm_pt([a, shock_y], t), v = upP - e) v/norm(v);
function ds_coil_gap(p, t) =
  let(e  = arm_pt([a, shock_y], t),
      q  = arm_pt([p[0], p[1]], t),
      d  = ds_axis(t),
      w  = q - e,
      s  = w*d,                                  // distance along the shock axis
      rp = norm(w - s*d))                        // perpendicular, in the pod plane
  s < ds_spring ? 99                             // below the spring: nothing there
                : sqrt(rp*rp + pow(p[2] - sz, 2)) - coil_d/2;
// The strap and the inner jaw carve themselves clear (ds_coil_cut_2d). The
// gussets cannot: they stand edge-on to the coil, so their cut line would be a
// different curve at every height. Give them a straight top edge instead and
// let the sweep say how high it may go — a full-width 40 gusset fouls the coil
// by 6 mm at full droop, which is exactly the trap a flat guess falls into.
function ds_gus_clear(yy) =
  min([for (t = [-bump_max : 2.5 : bump_max], s = [1,-1],
            zz = [zi_tr + plate_t : 3 : ds_z0])
         ds_coil_gap([a + s*ds_gus_x, shock_y + yy, zz], t)]);
ds_gus_top = max([for (yy = [0 : 0.5 : boss_disc/2]) if (ds_gus_clear(yy) >= 2) yy]);
ds_coil_pts =
  [for (s = [1,-1], zz = [zi_tr + plate_t : 3 : ds_z0])
     [a + s*ds_gus_x, shock_y + ds_gus_top, zz]];
ds_coil_min = min([for (t = [-bump_max : 2.5 : bump_max])
                     min([for (p = ds_coil_pts) ds_coil_gap(p, t)])]);

// ---- Rev 013: everything the strap itself has to survive -------------------
// Reaction split between the two supports, worst (trailing) arm. Nearly all of
// it lands on the strap, because the eye sits close to it.
ds_near0 = ds_thru ? ds_arms[0][2] : ds_jn;
ds_R  = lsb_F * (sz - ds_near0) / (ds_zs - ds_near0);             // strap share
if (ds_strap) {
  ds_checks = [
    // Strap as a beam in its own plane between the two gussets, central load,
    // net section through the Ø15.4 bore.
    ["strap bending between the gussets",
       (ds_R * 2*ds_gus_x / 4)
       / (ds_t * (pow(boss_disc,3) - pow(lsb_od+0.4,3)) / (6*boss_disc)), 235],
    // Sleeve bearing on the strap bore, and on the arm plate bore.
    // Each gusset is a cantilever sticking ds_z0 - (arm plate) out into the
    // bay, carrying half the strap's reaction at its free end. Its depth is
    // what the coil left it, so this is the check that ds_gus_x really buys.
    ["gusset bending at its weld to the arm plate",
       (ds_R/2) * (ds_z0 - (zi_tr + plate_t))
       / (ds_gus_t * pow(boss_disc/2 + ds_gus_top, 2) / 6), 235],
    ["sleeve bearing in the strap bore",  ds_R / (ds_t * lsb_od), 235],
    ["sleeve bearing in the arm plate",   (lsb_F - ds_R) / (plate_t * lsb_od), 235],
    // The sleeve is now cut twice, so check plain shear at each support too.
    ["sleeve double shear",
       ds_R / (2 * PI*(pow(lsb_od,2) - pow(lsb_id,2))/4), 140],
    // Arm plate net section at the enlarged Ø15.4 bore. The arm moment there
    // is the wheel force times the distance out to the axle, shared by 2 plates.
    ["arm plate net section at the Ø15.4 bore",
       (lsb_F*abs(MR_true) * (C - a))
       / (2 * plate_t * (pow(boss_disc,3) - pow(lsb_od+0.4,3)) / (6*boss_disc)), 235]];
  for (c = ds_checks)
    echo(str(c[1] > c[2] ? "*** WARN " : "PASS ", "Rev 013 ", c[0], ": ",
             round(c[1]), " MPa (limit ", c[2], ")"));
  ds_gaps = [
    ["strap outer face to the carrier inner face", cz - ds_z1, 4],
    [str("Ø", coil_d, " coil to the nearest bracket steel, swept over travel"), ds_coil_min, 2],
    ["gusset inboard face clear of the idler wheel", zi_tr + plate_t - H/2, 2],
    // Along the shock axis, which is the direction the load actually acts in.
    // The spring's flat end is what stops the steel on the tension side.
    ["strap bore edge distance ABOVE it (the spring caps this)",
       ds_spring - (lsb_od + 0.4)/2, 2],
    ["strap bore edge distance BELOW it (the loaded side)",
       ds_bot - (lsb_od + 0.4)/2, 11],
    // The strap swings with the arm and its inboard end passes the Ø22 pivot
    // sleeve, which is static and concentric with the pivot — so this gap is
    // the same at every arm angle. It is what caps ds_end.
    ["strap inboard end to the Ø22 pivot sleeve",
       (a - ds_gus_x - ds_end) - bushing_od/2, 2],
    // The outboard gusset is slotted for the M6 push bolt; what is left
    // between the slot and the gusset's own edge is the weld land.
    ["outboard gusset steel beside the push-bolt slot",
       boss_disc/2 - ds_gus_notch, 8]];
  for (g = ds_gaps)
    echo(str(g[1] < g[2] ? "*** WARN " : "PASS ", "Rev 013 ", g[0], ": ",
             g[1], " mm"));
  echo(str("REV 013 LOWER SHOCK MOUNT — eye bore Ø", ds_eye_bore, ", so the sleeve ",
           ds_thru ? "GOES THROUGH the eye: one sleeve per arm."
                   : str("STOPS AT the eye: two sleeves per arm, and the mount needs the INNER JAW as well as the strap (",
                         2, " identical plates per arm, not 1).")));
  echo(str("  sleeve Ø", lsb_od, "×Ø", lsb_id, ", main: ",
           zi_tr + plate_t + ds_sl_out, " (trailing) / ",
           zi_ld + plate_t + ds_sl_out, " (leading)",
           ds_thru ? "" : str(" · outer sleeve 2 x ", ds_z1 - (sz + ds_eye_w/2))));
  echo(str("  strap", ds_thru ? "" : " and inner jaw (same part)", ": ", boss_disc,
           "x", ds_t, " bar, ", 2*(ds_gus_x + ds_end), " long, bore Ø", lsb_od + 0.4,
           " at mid-length on the bar centreline, ", ds_thru ? 1 : 2,
           " per arm. TOP EDGE IS NOT STRAIGHT — cut it to the 1:1 template; the",
           " coil sweeps over that corner at full droop."));
  echo(str("  gussets: ", boss_disc/2 + ds_gus_top, " wide (bottom edge flush with",
           " the arm bar, top edge trimmed to clear the coil) x ", ds_gus_t,
           " thick x ", ds_z0 - (zi_tr + plate_t), " (trailing) / ",
           ds_z0 - (zi_ld + plate_t), " (leading) long, 2 per arm, ONE of each",
           " pair slotted Ø", 2*ds_gus_notch, " for the M6 push bolt"));
  echo(str("  M8 through-bolt cl.", ds_bolt_y >= 940 ? "10.9" : "8.8", ", ",
           10*ceil((zi_ld + plate_t + ds_z1 + 14)/10), " long, + nylock"));
}
echo(str("SHOCK FORCE (spring_rate=", spring_rate, " N/mm): ride sag ",
         spring_rate*(shock_ee - shock_len(0)), " N -> full bump ",
         spring_rate*(shock_ee - shock_len(bump_max)), " N -> full droop ",
         spring_rate*(shock_ee - shock_len(-bump_max)), " N per shock"));
echo(str("PIVOT STACK: centre spacer ≈ ", 2*sp_half, " · outboard sleeves ≈ ",
         sleeve_ln, " ×2 — all Ø22×3 tube, cut at the §9.3 dry-stack",
         carrier_shim > 0 ? str(" (that is the Rev 012 ", sleeve_ln - carrier_shim,
           " plus the ", carrier_shim, " mm Rev 013 measured shim; cut ONE tube per side, do not stack two)")
         : ""));
echo(str("TENSIONER: axle at +", tension_pos, " of 25 mm slot take-up — ",
         25 - tension_pos, " mm remaining (render_mode=\"tensioner\" for the ",
         "Sheet-6 close-up; advance both push bolts evenly)"));
// Rev 011d rear-fork bracket guards + cut lengths
if (use_bracket_eff) {
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
         shocks_inboard ? "INNER" : "OUTER", " face; Rev 012 lower sleeve was ",
         (sz - 5) - (zi_ld + plate_t), " long"));

// ---- belt-clearance guard: nothing hanging from the carrier may touch the
// ---- track when both arms hit full bump (belt bottom run at its highest)
y_w_bump    = -P + C*sin(bump_max - na);   // idler centre at full bump
y_belt_bump = y_w_bump - D/2;              // belt inner surface, bottom run
y_lug_bump  = y_belt_bump + lug_h;         // guide-lug tops
lug_zone    = F/2 + lug_w;                 // |z| outer edge of lug rows
// The lower shock mount reaches inboard PAST the belt edge — the inner jaw
// stands at |z| 39.5, inside even the lug rows — and it swings with the arm.
// Nothing checked it against the belt until 2026-09-19. Take the eye at full
// bump, where the arm is highest and the belt's bottom run is highest too, and
// measure from the lowest steel of the mount (ds_bot below the eye centre).
sh_in_z  = ds_strap ? ds_j0 : sz - ds_eye_w/2;        // innermost |z| of it
sh_floor = sh_in_z < lug_zone ? y_lug_bump : y_belt_bump;
clearances = concat(
  // Rev 002: carrier plates ride OUTSIDE the belt width — tongue check only
  // applies if a future layout puts them back over the belt
  (cz < track_w/2 + 3) ?
    [["carrier tongue Ø48", (pivot[1] - 24) - ((cz < lug_zone) ? y_lug_bump : y_belt_bump)]] : [],
  (sh_in_z < track_w/2) ?
    [[str("lower shock mount (reaches |z| ", sh_in_z, ") over the ",
          sh_in_z < lug_zone ? "lug rows" : "belt"),
      (arm_pt([a, shock_y], bump_max)[1] - ds_bot) - sh_floor]] : [],
  use_keel ? [[str("keel standoff  Ø", keel_od), (y_keel - keel_od/2) - y_lug_bump]] : [],
  [
   [str("pivot spacer   Ø", bushing_od), (pivot[1] - bushing_od/2) - y_lug_bump],
   [str("arm bar (", boss_disc, " wide)  "), (pivot[1] - boss_disc/2) - y_lug_bump]]);
if (cz >= track_w/2 + 3)
  echo(str("NOTE carrier plates at |z|=", cz, " — outside the belt (half-width ",
           track_w/2, "); they cannot contact the track at any bump"));
// Rev 013: measure to the carrier mounting plane (cz), which now includes the
// fitted shims — fork_gap alone stopped describing where that plane sits.
echo(str(cz - track_w/2 < 3 ? "*** TIGHT " : "OK ",
         "belt edge to the carrier mounting plane: ", cz - track_w/2,
         " mm per side (MEASURED cz ", cz, ")"));

// ---- Rev 013: the two checks that replaced the two rules --------------------
// cz used to be CALCULATED and shocks_inboard used to be DECIDED. Both are now
// stated from the built pod, so both need a check standing behind them,
// otherwise a wrong tape reading just propagates in silence.
echo(str(abs(cz_meas - cz_calc) <= 0.5 ? "OK " : "*** WARN ",
         "measured carrier face ", cz_meas, " vs fork_gap/2 - carrier_t ",
         cz_calc, ". The owner's fork bolts to the carrier's OUTER face, so",
         " fork_gap must stay 2 x (cz + carrier_t) = ", 2*(cz + carrier_t),
         ". If you move one, move the other."));
echo(str(cz + carrier_t - track_w/2 >= 10 ? "PASS " : "*** WARN ",
         "belt edge to the FORK LEG inner face: ", cz + carrier_t - track_w/2,
         " mm per side (want 10+). The legs sit outboard of the carriers now,",
         " so this is no longer the same number as the carrier clearance."));
// With shocks_inboard asserted rather than derived, nothing was left checking
// that the shock actually FITS between the belt and the carrier. This is that
// check: the old rule wanted the shock centre 10 mm clear of the carrier face.
echo(str(ds_eye_od > lsb_od ? "PASS " : "*** WARN ",
         "shock eye outer Ø", ds_eye_od, " vs sleeve outer Ø", lsb_od,
         ". With a Ø", ds_eye_bore, " bore the sleeve cannot pass through the",
         " eye, so it butts against the eye's end face. If the eye is narrower",
         " than the sleeve there is nothing for the sleeve to press on."));
echo(str(!shocks_inboard ? "n/a  shocks run outboard"
         : str(cz - sz >= 10 ? "PASS " : "*** WARN ",
               "inboard shock centre to carrier inner face: ", cz - sz,
               " mm (want 10). The old automatic rule refused inboard below 10",
               " and would have flipped the shocks outboard here.")));
for (c = clearances)
  echo(str(c[1] < 5 ? "*** WARN " : "PASS ", c[0], ": ", c[1],
           " mm above track at +", bump_max, "° bump"));
// The upper clevis's inner stub stands in the lug rows in z (39.5..45.5 against
// rows at 31..49), so it cannot pass BESIDE the lugs — it has to pass UNDER
// them. That makes this a radial check about the hub axle, not a vertical one,
// which is why it does not belong in the bump list above.
if (us_clevis && us_j0 < lug_zone)
  echo(str((r_wrap - lug_h) - us_corner >= 5 ? "PASS " : "*** WARN ",
           "upper inner stub at |z| ", us_j0, "..", us_j1,
           " stands in the lug rows — its far corner is ", us_corner,
           " from the axle, lug tips sweep ", r_wrap - lug_h, ": ",
           (r_wrap - lug_h) - us_corner, " mm clear underneath"));
// keel window fit (all static-to-static or pivot-centred, so the gaps hold at
// every articulation; small values acceptable) + in-plane wheel clearances
keel_gaps = concat(use_keel ? [
  ["keel to sprocket swept rib top", abs(y_keel) - keel_od/2 - (sprocket_od/2 + rib_h)],
  [str("keel to arm bar (", boss_disc, " wide)"),
        abs(y_keel - pivot[1]) - boss_disc/2 - keel_od/2],
  ["keel to pivot washers Ø30",   abs(y_keel - pivot[1]) - 15 - keel_od/2]] : [], [
  // Rev 003a: the lower shock through-bolt and the cross-brace share the
  // space between the fork plates with the Ø108 idler wheel — check both
  // Rev 013: the sleeve now runs the whole way across, so this span is Ø15,
  // not the Ø8 bolt it used to be here. Guard the bigger one.
  [str("shock sleeve Ø", ds_strap ? lsb_od : 8, " to idler wheel"),
     sqrt(pow(C - a, 2) + shock_y*shock_y) - D/2 - (ds_strap ? lsb_od : 8)/2],
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
  [str("shock coil Ø", coil_d, " to carrier strip (40 wide — Rev 011c)"),
     (upP[0] + ((25)/(upP[1]-low0[1]))*(low0[0]-upP[0])) - 20 - coil_d/2],
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
    // Rev 013: the Ø15×Ø9 sleeve now runs THROUGH both arm plates instead of
    // butting on the outer face, so this opens from Ø8.4 to Ø15.4. Net section
    // guarded above ("arm plate net section at the Ø15.4 bore").
    translate([a, shock_y]) circle(d = ds_strap ? lsb_od + 0.4 : 8.4);
  }
}

module ds_coil_cut_2d(dz){
  // ARM-LOCAL footprint swept by the Ø44 coil across the full travel, as seen
  // by a plate sitting dz out of the shock plane. No steel may live in here.
  // The spring is a flat-ended cylinder starting ds_spring up from the eye, so
  // the footprint is a RECTANGLE, not a capsule — a capsule's round end would
  // eat the bore itself and is simply the wrong shape.
  r = (coil_d*coil_d/4 - dz*dz > 0) ? sqrt(coil_d*coil_d/4 - dz*dz) : 0;
  if (r > 0)
    for (t = [-bump_max : 2.5 : bump_max]) {
      uL  = rot2(upP - pivot, na - t);        // upper eye, in arm-local terms
      d   = uL - [a, shock_y];
      L   = norm(d);
      translate([a, shock_y]) rotate(atan2(d[1], d[0]))
        translate([ds_spring, -r]) square([L - shock_neck - ds_spring, 2*r]);
    }
}

module ds_strap_2d(dz){
  // REV 013 outer strap (and, when the eye bore is too small for the sleeve,
  // the identical inner jaw) — cut from 40x6 bar. Sits alongside the shock eye
  // and turns the lower mount into double shear.
  // The top edge is not a straight line: the coil comes down to within
  // ds_spring of the eye and, at FULL DROOP, swings inboard over the bar. So
  // the blank is the full 40 and ds_coil_cut_2d carves whatever the spring
  // needs. That leaves the most steel the shock allows, instead of a flat
  // guess. What survives above the bore only ever carries the 318 N of droop;
  // the bump load pushes the eye the other way, into the full 20 mm below.
  half = ds_gus_x + ds_end;
  difference(){
    translate([a - half, shock_y - ds_bot]) square([2*half, ds_bot + ds_top]);
    translate([a, shock_y]) circle(d = lsb_od + 0.4);
    ds_coil_cut_2d(dz);
  }
}

module ds_gusset_2d(z0, notch){
  // REV 013 gusset FLAT PATTERN: boss_disc wide, and long enough to span from
  // the arm plate's outer face (z0) out to the strap's inner face. Two per
  // arm, standing ds_gus_x fore and aft of the eye. The trailing and leading
  // arms have different z0, so their gussets differ in length — mark them.
  // `notch` clears the M6 tensioner push bolt, which runs along the arm at
  // z ≈ z0 + 7. Both arms get it so the four gussets of a pod cut the same.
  // Top edge trimmed to ds_gus_top: at full droop the coil swings inboard over
  // the arm and a full-width gusset would be inside it.
  difference(){
    translate([-boss_disc/2, 0])
      square([boss_disc/2 + ds_gus_top, ds_z0 - z0]);
    if (notch) hull(){ circle(r = ds_gus_notch);
                       translate([0, 7]) circle(r = ds_gus_notch); }
  }
}

module axle_key_2d(){
  // hub-motor axle key: Ø10+0.4 with flats 8.9 across — the torque-arm fit.
  // Cut in the carrier AND (Rev 011c) in the shock tab stub; drill Ø10.4,
  // file the flats. Never a slot — a slot lets the axle rotate.
  intersection(){ circle(d=axle_d+0.4);
                  square([axle_d+0.4, 8.9], center=true); }
}

module carrier_2d(m8 = use_bracket_eff ? [-12, 12] : []){
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
    for (yy = m8) translate([0,yy]) circle(d=8.4);
    translate([0,52])      circle(d=8.5);       // M8 into fork leg (drill leg)
    translate(pivot)       circle(d=pivot_d);   // pivot bore, ream in pair
    if (use_keel) translate([0, y_keel]) circle(d=8.5);  // keel bolt M8
  }
}

module tab_stub_2d(p, yb = -20){
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
    translate([s==1 ? -20 : -63, yb]) square([83, 40]);
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
module flag(txt, tip, anchor, size = 6){
  color([0.70,0.18,0.12]){
    hull(){ translate(tip) sphere(0.9); translate(anchor) sphere(0.9); }
    translate(anchor + [2, -2.5, 0]) linear_extrude(1.2) text(txt, size=size);
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
    // REV 013 2026-09-18: these were hard-coded h=10 / bore d=10 and had no
    // link to the measured eye at all, which is why a 24 mm eye still drew
    // 10 mm long. Both read the measurements now.
    for (x=[0, L]) color([0.55,0.55,0.58])            // eyelets
      translate([x,0,0]) difference(){
        cylinder(h=ds_eye_w, d=ds_eye_od, center=true);
        cylinder(h=ds_eye_w + 2, d=ds_eye_bore, center=true); }
    // REV 012c: owner measured 25 mm from the TOP eye centre to the spring
    // (shock_neck) — body and spring start there, only the thin rod above it
    color([0.72,0.72,0.75]) translate([shock_neck,0,0])        // damper body
      rotate([0,90,0]) cylinder(h=6 + 0.52*L - shock_neck, d=22);
    color([0.72,0.72,0.75]) rotate([0,90,0])          // shaft
      cylinder(h=L-6, d=9);
    color([0.70,0.15,0.12]) translate([shock_neck,0,0])        // coil spring
      rotate([0,90,0]) linear_extrude(height=L-12-shock_neck,
                                      twist=2160*(L-12-shock_neck)/(L-22), $fn=24)
        translate([(coil_d - 4.2)/2, 0]) circle(d=4.2);  // was a flat 14, which
                                      // drew a Ø32 coil regardless of coil_d
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
    // ---- lower shock mount -------------------------------------------------
    // Rev 012 and before: bolt through both plates, sleeve only on the shock
    // side, eye on its free end (single shear).
    // Rev 013: sleeve CONTINUOUS from the far plate through to the outer strap
    // (double shear), plus that strap and its two gussets.
    scale([1, 1, szs]) {
      ds_far = -(zi + plate_t);                       // far arm plate outer face
      ds_in  = ds_strap ? ds_far : zi + plate_t;      // inboard end of the sleeve
      ds_out = ds_strap ? ds_sl_out : sz - 5;         // outboard end of the sleeve
      color([0.55,0.55,0.58]) translate([a, shock_y, ds_far - 4])
        cylinder(h = (ds_z1 + 8) - (ds_far - 4), d=7.8);           // M8 bolt
      color([0.55,0.55,0.58]) translate([a, shock_y, ds_in])       // main sleeve
        difference(){
          cylinder(h = ds_out - ds_in, d=lsb_od);
          translate([0,0,-1]) cylinder(h = 2*sz + 40, d=8.5); }
      if (ds_strap) {
        // second short sleeve, only when the eye bore is too small to pass the
        // first one: it carries the eye's outer face across to the strap
        if (!ds_thru) color([0.55,0.55,0.58])
          translate([a, shock_y, sz + ds_eye_w/2]) difference(){
            cylinder(h = ds_z1 - (sz + ds_eye_w/2), d=lsb_od);
            translate([0,0,-1]) cylinder(h = 40, d=8.5); }
        // Both plates sit the same ds_clr + eye/2 out of the shock plane, so
        // the coil carves them identically: strap and jaw are ONE part.
        color([0.36,0.43,0.56]) translate([0, 0, ds_z0])
          linear_extrude(ds_t) ds_strap_2d(ds_z0 - sz);   // outer strap
        if (!ds_thru) color([0.36,0.43,0.56]) translate([0, 0, ds_j0])
          linear_extrude(ds_t) ds_strap_2d(sz - ds_j1);   // inner jaw — same part
        for (s = [1, -1])
          color([0.36,0.43,0.56])
            translate([a + s*ds_gus_x - ds_gus_t/2, shock_y, zi + plate_t])
              rotate([90,0,90]) linear_extrude(ds_gus_t)
                ds_gusset_2d(zi + plate_t, s > 0);
      }
    }
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

module carrier_group(mount = use_bracket_eff ? "bracket" : "stub"){
  // mount: "bracket" (Rev 011d), "stub" (Rev 011c), "stub_clear" (REV 012
  // front pod), "green" (REV 012 rear pod: 60x6 green plates)
  // plates (Rev 002: bolted to the fork-leg outer faces)
  color([0.36,0.43,0.56]) for (s=[1,-1])
    translate([0,0, (s==1 ? cz : -cz-carrier_t) + s*ex*55])
      linear_extrude(carrier_t) carrier_2d(mount == "bracket" ? [-12, 12] : mount == "green" ? gp_m8 : []);
  // upper shock tabs — welded to the carrier INNER face when the shocks run
  // inboard (Rev 002, thick legs), to the OUTER face when outboard (Rev 002c,
  // measured 4 mm legs leave no inboard room)
  // Rev 011c: ONE full-width tab stub per carrier, on the OUTER face at hub
  // level, keyed on the axle; the eye pin cantilevers from the stub out to
  // the shock plane through washers. +z carrier serves the trailing shock,
  // -z the leading — a shock loads only the carrier it hangs from.
  // 011d merged: with the bracket, the blade IS the shock tab — separate
  // stubs exist only on the front pod (no bracket there yet)
  if (mount == "stub" || mount == "stub_clear") color([0.36,0.43,0.56]) for (s=[1,-1]){
    // outer stub — thickness was drawn as a flat 6 while stub_t said otherwise
    translate([0,0, (s==1 ? tab_z0 : -(tab_z0 + stub_t)) + s*ex*55])
      linear_extrude(stub_t) tab_stub_2d(s==1 ? upP : mx(upP), mount == "stub_clear" ? stub_yb : -20);
    // inner stub — same blank flipped, closing the clevis round the upper eye
    if (us_clevis) translate([0,0, (s==1 ? us_j0 : -us_j1) + s*ex*55])
      linear_extrude(us_t) tab_stub_2d(s==1 ? upP : mx(upP), mount == "stub_clear" ? stub_yb : -20);
  }
  // REV 012 rear pod: green plate = bracket + shock tab in one, flat on the
  // hub plate; the rails and bolts belong to the frame (rear_link)
  if (mount == "green") color(c_green) for (s=[1,-1]) scale([1,1,s])
    translate([0,0,gp_z0]) linear_extrude(gp_t) green_plate_2d(s);
  // REV 011d rear-fork bracket: blade + pad per side, keyed on the axle at
  // z = carrier outer face .. +brk_t; the shock stub moves outboard by brk_t
  if (mount == "bracket") for (s=[1,-1]) scale([1,1,s]){
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
  // ghost fork legs (context only — measure leg_t); REV 012 draws its own
  if (mount == "stub" || mount == "bracket") color([0.45,0.50,0.60,0.35]) for (s=[1,-1])
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

// ====================================================== pod as one object ==
// Rev 012: the assembly branch's body, lifted verbatim into a module so the
// chassis view can place TWO of them (front and rear) in vehicle coordinates.
// Pod coords: origin = hub axle centre, +x rearward, +y up, z across.
module pod_assembly(mount = use_bracket_eff ? "bracket" : "stub"){
  // trailing arm (rear, +x) and leading arm (front, -x, mirrored)
  translate([ ex*60, 0, 0]) arm3d(zi_tr, true,  aT, +1);
  translate([-ex*60, 0, 0]) mirror([1,0,0]) arm3d(zi_ld, false, aL, -1);

  carrier_group(mount);
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

// ======================================================= REV 012 chassis ===
// Vehicle coords: X = 0 at the FRONT hub axle, +X rearward.
//                 Y = 0 at the GROUND, +Y up.   Z = across, 0 on centreline.
// A pod drops straight in with translate([x, hub_h, 0]) — same axes as the
// pod's own coordinates.

hub_h     = B + D/2 + T;             // 216 — hub axle height above ground
pod_halfl = A_eff/2 + D/2 + T;       // 181.6
pod_halfw = sz + 22;                 // 116
pod_top   = hub_h + pitch_r + T/2;   // belt crown

// ---- loads the rear pod puts into ONE side (static springs) -----------------
function ch_Fs(t) = max(0, spring_rate*(shock_ee - shock_len(t)));
function ch_lo(t) = arm_pt([a, shock_y], t);
function ch_us(t) = (upP - ch_lo(t)) / norm(upP - ch_lo(t));
function ch_Fw(t) = ch_Fs(t) * MR_at(t);
function ch_sum(v, i = 0)  = i >= len(v) ? 0     : v[i] + ch_sum(v, i + 1);
function ch_vsum(v, i = 0) = i >= len(v) ? [0,0] : v[i] + ch_vsum(v, i + 1);
function ch_side(s, tT, tL) = let(
    pT = [0, ch_Fw(tT)] - ch_Fs(tT)*ch_us(tT),
    pL = [0, ch_Fw(tL)] - ch_Fs(tL)*mx(ch_us(tL)),
    half = (pT + pL)/2)
  s > 0 ? [[upP,     ch_Fs(tT)*ch_us(tT)],     [[0, -P], half]]
        : [[mx(upP), ch_Fs(tL)*mx(ch_us(tL))], [[0, -P], half]];
// in-plane bending moment at a plate section (xs, yc) from the loads AFT of it
// (the plate is held at its FRONT, by the rail)
function ch_M(ld, xs, yc = 0) = abs(ch_sum([for (l = ld) if (l[0][0] > xs)
    (l[0][0] - xs)*l[1][1] - (l[0][1] - yc)*l[1][0]]));
ch_cases = [[0, 0], [bump_max, bump_max], [bump_max, -bump_max], [-bump_max, bump_max]];
function ch_Mmax(s, xs, yc = 0) = max([for (c = ch_cases) ch_M(ch_side(s, c[0], c[1]), xs, yc)]);
function ch_V(s) = max([for (c = ch_cases) norm(ch_vsum([for (l = ch_side(s, c[0], c[1])) l[1]]))]);

// ---- green plate: position (Rev 012c — no cut, ends above the spring) -------
gp_yc   = ceil(upP[1] - shock_neck + gp_spring_clr + gp_w/2);   // 11 — band centre above the hub axle
stub_yb = max(-20, ceil(upP[1] - shock_neck + gp_spring_clr));   // -19 — front pod shock tab bottom
gp_m8   = [24];                      // ONE M8 to the hub plate above the axle key, + weld all round
// REV 013, 2026-09-18 (owner): the GREEN PLATES ARE INBOARD of the carriers.
// "the carrier plates are the last and first plates regarding z position" — so
// the carrier is the outermost steel on each side, and the green plate lies
// against its INNER face, not its outer one. Until now this read
// cz + carrier_t, which put the plate outboard and made the pod 12 mm wider
// per side than it is.
gp_z0   = cz - gp_t;                 // 76.5 — plate INNER face
gp_x0   = -rear_ct_x + gp_gap;       // -188 — plate front end
gp_x1_tr = round(upP[0]) + 20;       // +72 — right (+z) plate, past the rear shock eye
gp_x1_ld = 20;                       // +20 — left (-z) plate, past the axle key
gp_gap_z = sz - (gp_z0 + gp_t);      // shock centreline minus the plate OUTER
                                     // face. Negative now the plate is inboard:
                                     // the shock sits inboard of it

// ---- where the rails end, and the 2 bolts per side (rear pod coords) --------
ch_lead_xmin = -max(concat([upP[0]], [for (t = [-bump_max : 2.5 : bump_max]) ch_lo(t)[0]]));
rl_end_x = floor(ch_lead_xmin - shock_perch_d/2 - rl_shock_clr);  // -83 — rail rear end
rl_bolts = [gp_x0 + gp_end_edge, rl_end_x - rl_end_edge];         // [-168, -108]

// ---- frame ------------------------------------------------------------------
rail_in  = gp_z0 - fr_w;             // rail lies on the green plate's INNER
                                     // face now the plate is inboard, so the
                                     // rail runs inboard from it, not outboard
rail_out = rail_in + fr_w;           // 126
bay_w    = 2*rail_in;                // 172 — clear width between the rails
fr_top   = hub_h + gp_yc + gp_w/2;   // 257 — flush with the green plate top
fr_bot   = fr_top - fr_h;            // 157
deck_y   = fr_top + lid_t;           // 269 — STANDING HEIGHT
tray_y0  = fr_bot - tray_t;          // 145 — lowest point
lid_w    = 2*rail_out + 2*lid_over;  // 302
spk_well = spk_cut_d + 2*spk_edge;           // 181 — clear length of one well
spk_bay  = 2*(spk_well + spk_bhd_t);         // 386 — bay length the two wells take
bay_pack_len = batt_n*batt_l + (batt_n - 1)*batt_gap + 2*batt_end_clr;  // 840 — what the packs need
bay_need = bay_pack_len + spk_bay;           // 1226 — packs + both wells
bay_len  = max(bay_len_set, bay_need);       // 1226 — the clear bay that is built
fr_x0    = front_cm_x;               // front cross member front face
bay_x0   = fr_x0 + fr_w;
bay_x1   = bay_x0 + bay_len;
wheelbase = bay_x1 + fr_w + rear_ct_x;   // 1706 — front offset + bay + cross members + rear offset

// ---- where the two speakers and their bulkheads sit --------------------------
// Wells hard against each cross member; any bay spare falls behind the rear pack.
spk_cx    = [bay_x0 + spk_well/2, bay_x1 - spk_well/2];            // driver centres
spk_bhd_x = [bay_x0 + spk_well, bay_x1 - spk_well - spk_bhd_t];    // bulkhead front faces
batt_x0   = bay_x0 + spk_well + spk_bhd_t + batt_end_clr;          // first pack front face
spk_vol   = bay_w*fr_h*spk_well/1e6 - spk_disp;  // litres of air behind one driver
ct_x1    = wheelbase - rear_ct_x;    // rear cross member rear face = lid rear edge
rail_x1  = wheelbase + rl_end_x;     // rail rear end
rail_len = rail_x1 - fr_x0;

// ---- steering axis + front pod sweep ----------------------------------------
u_ax = [cos(head_ang), sin(head_ang)];
nb   = [sin(head_ang), -cos(head_ang)];
Q_ax = [fork_off*nb[0], hub_h + fork_off*nb[1]];
t_bot = sqrt(max(1, fork_len*fork_len - fork_off*fork_off));
head_p0 = Q_ax + t_bot*u_ax;
head_p1 = head_p0 + head_len*u_ax;
head_bot_y = head_p0[1];
trail = -(Q_ax[0] - Q_ax[1]*u_ax[0]/u_ax[1]);
steer_xs  = fork_off / sin(head_ang);
steer_pts = [[ pod_halfl, track_w/2], [-pod_halfl, track_w/2],
             [ 52, pod_halfw],        [-52, pod_halfw]];
steer_xmax = max([for (p = steer_pts) for (sgz = [1,-1])
                    for (th = concat([for (k = [-steer_lock : 5 : steer_lock]) k], [steer_lock]))
                    let(dx = p[0] - steer_xs, zz = sgz*p[1])
                    steer_xs + dx*cos(th) - zz*sin(th)]);

// ---- rear track outer surface, for the rear cross member ---------------------
function ch_belt_dist(X, t) = let(
    c1 = [0,0], R1 = r_wrap + T, c2 = mx(arm_pt([C, 0], t)), R2 = D/2 + T,
    d = c2 - c1, Ld = norm(d), an = atan2(d[1], d[0]),
    n1 = [cos(an + acos((R1 - R2)/Ld)), sin(an + acos((R1 - R2)/Ld))],
    n2 = [cos(an - acos((R1 - R2)/Ld)), sin(an - acos((R1 - R2)/Ld))],
    n  = n1[0] < 0 ? n1 : n2, T1 = c1 + R1*n, T2 = c2 + R2*n,
    sp = (X - T1)*(T2 - T1)/pow(norm(T2 - T1), 2))
  (sp >= 0 && sp <= 1) ? (X - T1)*n : min(norm(X - c1) - R1, norm(X - c2) - R2);
ch_ct_clear = min([for (t = [-bump_max : 5 : bump_max])
                     for (x = [-rear_ct_x - fr_w : 2 : -rear_ct_x])
                     for (y = [fr_bot - hub_h : 2 : deck_y - hub_h]) ch_belt_dist([x, y], t)]);

// ---- top of the spring vs the plate / tab above it --------------------------
function ch_spring_top(s, t) = let(
    eye = s > 0 ? upP : mx(upP),
    lo  = s > 0 ? ch_lo(t) : mx(ch_lo(t)),
    u   = (lo - eye)/norm(lo - eye),
    q   = eye + shock_neck*u)
  q[1] + (shock_perch_d/2)*abs(u[0]);
ch_spring_hi = max([for (s = [1,-1]) for (t = [-bump_max : 2.5 : bump_max]) ch_spring_top(s, t)]);

// ---------------------------------------------------------------- colours ---
c_frame = [0.42,0.45,0.50];
c_lid   = [0.72,0.55,0.35,0.45];   // plywood
c_tray  = [0.66,0.50,0.32,0.50];   // plywood
c_green = [0.20,0.55,0.30];
c_bolt  = [0.78,0.78,0.80];
c_ghost = [0.50,0.55,0.62,0.30];
c_batt  = [0.20,0.45,0.80,0.45];

module beam_x(len, h, w, t){
  difference(){
    translate([0, 0, -w/2]) cube([len, h, w]);
    translate([-1, t, -(w/2 - t)]) cube([len+2, h - 2*t, w - 2*t]);
  }
}
module beam_z(len, h, w, t){
  difference(){
    translate([-w/2, 0, 0]) cube([w, h, len]);
    translate([-(w/2 - t), t, -1]) cube([w - 2*t, h - 2*t, len+2]);
  }
}

// ---- green plate, cut from 60x6 (rear pod coords) ---------------------------
// s = +1: RIGHT plate (+z), rear shock eye.   s = -1: LEFT plate (-z), front shock eye.
module green_plate_2d(s){
  eye = s > 0 ? upP : mx(upP);
  x1  = s > 0 ? gp_x1_tr : gp_x1_ld;
  difference(){
    translate([gp_x0, gp_yc - gp_w/2]) square([x1 - gp_x0, gp_w]);
    axle_key_2d();                                              // keyed on the hub axle
    for (yy = gp_m8) translate([0, yy]) circle(d = 8.4);        // M8 to the hub plate
    translate(eye) circle(d = 8.4);                             // shock top eye pin
    for (bx = rl_bolts) translate([bx, gp_yc]) circle(d = bolt_d + 1);   // 2x M12 to the rail
  }
}

// ---- 3D (vehicle coords) ----------------------------------------------------
module rail(s){
  // one rail, with a Ø25 hole through both walls at each bolt and a steel
  // sleeve welded in it (the bolt clamps the sleeve, not the 2 mm walls)
  translate([0, 0, s*(rail_in + fr_w/2)]){
    color(c_frame) difference(){
      translate([fr_x0, fr_bot, 0]) beam_x(rail_len, fr_h, fr_w, fr_t);
      for (bx = rl_bolts) translate([wheelbase + bx, hub_h + gp_yc, 0])
        cylinder(h = fr_w + 2, d = sleeve_od, center = true);
    }
    color([0.62,0.64,0.68]) for (bx = rl_bolts) translate([wheelbase + bx, hub_h + gp_yc, 0])
      difference(){ cylinder(h = fr_w, d = sleeve_od, center = true);
                    cylinder(h = fr_w + 2, d = sleeve_id, center = true); }
  }
}
module chassis_frame(lid = true, tray = true){
  for (s = [1, -1]) rail(s);
  color(c_frame){
    translate([fr_x0 + fr_w/2, fr_bot, -rail_in]) beam_z(bay_w, fr_h, fr_w, fr_t);   // front cross member
    translate([ct_x1 - fr_w/2, fr_bot, -rail_in]) beam_z(bay_w, fr_h, fr_w, fr_t);   // rear cross member
  }
  if (lid)  color(c_lid)  difference(){
    translate([fr_x0, fr_top, -lid_w/2]) cube([ct_x1 - fr_x0, lid_t, lid_w]);
    for (cx = spk_cx) translate([cx, fr_top - 1, 0])
      rotate([-90,0,0]) cylinder(h = lid_t + 2, d = spk_cut_d);      // speaker hole
  }
  if (tray) color(c_tray) translate([fr_x0, tray_y0, -rail_out])  cube([ct_x1 - fr_x0, tray_t, 2*rail_out]);
  // the bulkhead that closes each speaker well off from the batteries (plywood,
  // so it comes and goes with the tray — the link close-up does not want it)
  if (tray) color(c_lid) for (bx = spk_bhd_x)
    translate([bx, fr_bot, -bay_w/2]) cube([spk_bhd_t, fr_h, bay_w]);
}
module speakers(){
  // 6.5" driver dropped into the lid from above, firing up
  for (cx = spk_cx) translate([cx, fr_top, 0]) rotate([-90,0,0]){
    color([0.15,0.15,0.17])   cylinder(h = lid_t + 3, d = spk_rim_d);          // rim on the lid
    color([0.30,0.30,0.33])   translate([0, 0, -spk_depth])
      cylinder(h = spk_depth, d1 = spk_cut_d/3, d2 = spk_cut_d - 4);           // basket + cone
    color([0.22,0.22,0.25])   translate([0, 0, -spk_depth])
      cylinder(h = spk_depth/3, d = spk_cut_d/2.2);                            // magnet
  }
}
module rear_link(bolt_out = 0, pod_dx = 0){
  // per side: 2x M12 put in from OUTSIDE the rail, through the sleeve and the
  // green plate, into an M12 nut welded on the green plate's inner face
  translate([wheelbase, hub_h, 0]) for (s = [1, -1]) scale([1, 1, s])
    for (bx = rl_bolts) translate([bx, gp_yc, 0]){
      color(c_bolt) translate([0, 0, bolt_out]){
        translate([0, 0, gp_z0 - 12]) cylinder(h = 12 + gp_t + fr_w + 3, d = bolt_d - 0.2);   // shank
        translate([0, 0, rail_out])      cylinder(h = 3, d = 24);                              // washer
        translate([0, 0, rail_out + 3])  cylinder(h = 7.5, d = 21.9, $fn = 6);                 // head
      }
      color([0.55,0.55,0.58]) translate([pod_dx, 0, gp_z0 - 10])
        cylinder(h = 10, d = 21.9, $fn = 6);                                                   // weld nut
    }
}
module front_end_ghost(){
  color(c_ghost){
    translate([head_p0[0], head_p0[1], 0]) rotate([0, 90 - head_ang, 0])
      cylinder(h = head_len, d = head_od);
    for (s = [1, -1]) translate([0, 0, s*(fork_gap/2 + leg_t/2)])
      hull(){
        translate([head_p0[0], head_p0[1], 0]) rotate([90,0,0]) cylinder(h = leg_t, d = 26, center = true);
        translate([0, hub_h, 0]) rotate([90,0,0]) cylinder(h = leg_t, d = 26, center = true);
      }
  }
}
module battery_boxes(){
  // one behind the other, on the tray, centred between the rails
  color(c_batt) for (i = [0 : batt_n - 1])
    translate([batt_x0 + i*(batt_l + batt_gap), fr_bot, -batt_w/2])
      cube([batt_l, batt_h, batt_w]);
}
module chassis_ground(){
  color([0.80,0.80,0.82,0.35]) translate([-400, -2, -450]) cube([wheelbase + 800, 2, 900]);
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
  if (use_bracket_eff) translate([0, -300]){      // REV 011d MERGED bracket plates:
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
} else if (render_mode == "chassis"){
  // ---- REV 012: narrow frame, batteries in line, rear pod on the rails.
  chassis_ground();
  translate([0,         hub_h, 0]) pod_assembly("stub_clear");    // FRONT pod — donor fork
  translate([wheelbase, hub_h, 0]) pod_assembly("green");         // REAR pod — green plates
  chassis_frame(show_lid, show_tray);
  rear_link();
  front_end_ghost();
  if (show_batteries) battery_boxes();
  if (show_speakers)  speakers();

  if (show_chassis_labels){
    lz = lid_w/2 + 90;
    flag("FRONT POD - DONOR FORK (LINK TO FRAME: LATER)",
         [0, hub_h + 40, pod_halfw],                        [-430, deck_y + 330, lz]);
    flag(str("2 RAILS 100x40x2 - ", bay_w, " APART INSIDE"),
         [fr_x0 + 80, fr_bot + fr_h/2, rail_out],           [-430, deck_y + 250, lz]);
    flag(str("STANDING HEIGHT ", deck_y, " mm - LID ", lid_w, " WIDE"),
         [(fr_x0 + ct_x1)/2, deck_y, lid_w/2],              [(fr_x0 + ct_x1)/2 - 250, deck_y + 330, lz]);
    flag(str("2 BATTERIES IN LINE - ", batt_l, "x", batt_w, "x", batt_h),
         [(bay_x0 + bay_x1)/2, fr_bot + 30, rail_out],      [(fr_x0 + ct_x1)/2 - 250, -160, lz]);
    flag(str("6.5\" SPEAKER UP THROUGH THE DECK - HOLE ", spk_cut_d, ", WELL ", spk_well),
         [spk_cx[0], deck_y, 0],                            [-430, deck_y + 170, lz]);
    flag(str("WHEELBASE ", wheelbase, " mm (BAY ", bay_len, " CLEAR)"),
         [wheelbase/2, 2, 0],                               [(fr_x0 + ct_x1)/2 - 250, -240, lz]);
    flag("GREEN PLATE 60x6 FLAT ON THE RAIL INNER FACE",
         [wheelbase + (rl_bolts[0] + rl_end_x)/2, hub_h + gp_yc + gp_w/2, rail_in],
                                                            [wheelbase + 150, deck_y + 330, lz]);
    flag("2x M12 PER SIDE - POD OFF WITH 4 BOLTS",
         [wheelbase + rl_bolts[1], hub_h + gp_yc, rail_out + 10], [wheelbase + 150, deck_y + 250, lz]);
    flag("RAILS END BEFORE THE FRONT SHOCK",
         [rail_x1, fr_top, rail_out],                       [wheelbase + 150, deck_y + 170, lz]);
  }

  // ---------------------------------------------------- chassis guards ----
  ch_Pr   = 2*rider_kg*9.81;
  ch_Pf   = ch_Pr/2;
  ch_Irl  = (fr_w*pow(fr_h,3) - (fr_w - 2*fr_t)*pow(fr_h - 2*fr_t, 3))/12;
  ch_Zrl  = ch_Irl/(fr_h/2);
  ch_Zgp  = gp_t*gp_w*gp_w/6;
  ch_Zgpn = gp_t*(pow(gp_w,3) - pow(bolt_d + 1, 3))/12/(gp_w/2);              // at a bolt hole
  ch_Zeye = (gp_t*pow(gp_w,3)/12 - (gp_t*8.4*8.4*8.4/12 + gp_t*8.4*pow(gp_yc - upP[1], 2))) / (gp_w/2);
  ch_xc   = (rl_bolts[0] + rl_bolts[1])/2;
  ch_Mj   = max(ch_Mmax(1, ch_xc, gp_yc), ch_Mmax(-1, ch_xc, gp_yc));
  ch_Fb   = ch_Mj/abs(rl_bolts[1] - rl_bolts[0]) + max(ch_V(1), ch_V(-1))/2;
  ch_grip = bolt_mu*bolt_preload;                                             // ONE interface: rail wall / plate
  ch_Asl  = PI/4*(sleeve_od*sleeve_od - sleeve_id*sleeve_id);

  echo("");
  echo("=================== REV 012 CHASSIS — NARROW FRAME, BATTERIES IN LINE ===================");
  echo("STEEL:    rails + cross members 100x40x2 (BOUGHT) · green plates 60x6 (BOUGHT) · lid + tray plywood");
  echo(str("VEHICLE:  WHEELBASE ", wheelbase, " mm — front cross member at ", front_cm_x, " + bay ", bay_len,
           " (", batt_n, " x ", batt_l, " packs need ", bay_pack_len, " + 2 speaker wells need ", spk_bay,
           ") + cross members + ", rear_ct_x, " to the rear axle"));
  echo(str("SPEAKERS: 6.5\" firing UP at each end of the deck — hole Ø", spk_cut_d, " in the lid, driver ",
           spk_depth, " deep, centres at x ", spk_cx[0], " and ", spk_cx[1],
           " · each well is a sealed box of the two rails + tray + lid + cross member + one ",
           spk_bhd_t, " mm bulkhead ≈ ", round(spk_vol*100)/100, " litres"));
  echo(str("FRAME:    rails ", rail_len, " long, ", bay_w, " apart inside, ", 2*rail_out, " outside · lid ", lid_w,
           " wide · STANDING HEIGHT ", deck_y, " · lowest point (tray) ", tray_y0, " above ground"));
  echo(str("REAR POD: green plate flat on each rail's inner face -> 2x M12 per side -> OFF WITH 4 BOLTS"));
  echo(str("FRONT:    head ", head_ang, " deg, offset ", fork_off, " -> trail ", round(trail*10)/10,
           " (TBD) · front pod lifts the front end ", round(hub_h - stock_axle_h), " mm · fork -> frame link NOT DESIGNED YET"));

  ch_clear = [
    ["front cross member behind the front pod at full steering lock",   front_cm_x - steer_xmax, 10],
    ["rear cross member + lid edge to the rear track, over full travel", ch_ct_clear,            10],
    ["rail rear end ahead of the front shock (left side)",               (ch_lead_xmin - shock_perch_d/2) - rl_end_x, 5],
    ["rail inner face to the track edge",                                rail_in - track_w/2,    10],
    ["M12 weld nut (inside the green plate) to the track edge",          (gp_z0 - 10) - track_w/2, 5],
    ["green plate bottom edge above the spring, over full travel",       (gp_yc - gp_w/2) - ch_spring_hi, 1.5],
    ["front pod shock tab above the spring, over full travel",           stub_yb - ch_spring_hi, 1.5],
    ["front M12 hole to the green plate's front end (need 1.5 x hole)",  (rl_bolts[0] - gp_x0) - 1.5*(bolt_d + 1), 0],
    ["rear sleeve hole to the rail's rear end (steel left)",             (rl_end_x - rl_bolts[1]) - sleeve_od/2, 8],
    ["batteries between the rails, width spare",                         bay_w - batt_w,         20],
    ["batteries under the lid, height spare",                            fr_h - batt_h,          5],
    ["bay length spare behind the rear pack",                            bay_len - bay_need,     0],
    ["speaker hole edge to the rail inner face",                         (bay_w - spk_cut_d)/2,  5],
    ["speaker rim to the lid edge",                                      (lid_w - spk_rim_d)/2,  10],
    ["air under the driver cone, well floor to driver",                  fr_h - spk_depth,       20],
  ];
  for (g = ch_clear)
    echo(str(g[1] < g[2] ? "*** WARN " : "PASS ", g[0], ": ", round(g[1]*10)/10, " mm"));
  echo(str("NOTE shock: top eye centre -> spring = ", shock_neck, " mm (MEASURED). The green plate is not cut; it sits ",
           gp_yc, " mm above the axle so it ends above the spring."));

  ch_stress = [
    ["green plate where the rail ends, right side",           ch_Mmax( 1, rl_end_x, gp_yc)/ch_Zgp],
    ["green plate where the rail ends, left side",            ch_Mmax(-1, rl_end_x, gp_yc)/ch_Zgp],
    ["green plate at the rear M12 hole (net section)",        max(ch_Mmax(1, rl_bolts[1], gp_yc), ch_Mmax(-1, rl_bolts[1], gp_yc))/ch_Zgpn],
    ["green plate at the front shock eye hole, left side",    ch_Mmax(-1, -upP[0] - 4.2, gp_yc)/ch_Zeye],
    ["rail at the joint (the plate's twist becomes rail bending)", ch_Mj/ch_Zrl],
    ["sleeve walls in the rail, bearing",                     ch_Fb/(2*sleeve_od*fr_t)],
    ["sleeve squeezed by the bolt preload",                   bolt_preload/ch_Asl],
    ["M12 bolt, single shear",                                ch_Fb/(PI*bolt_d*bolt_d/4)],
    ["rails, rider x2 in the middle",                         ch_Pr*(ct_x1 - fr_x0 - fr_w)/4 / (2*ch_Zrl)],
  ];
  for (g = ch_stress)
    echo(str(g[1] > 141 ? "*** WARN " : "PASS ", g[0], ": ", round(g[1]), " MPa"));
  ch_s_lid = ch_Pf/2*(bay_w/2 - 25) / (250*lid_t*lid_t/6);
  echo(str(ch_s_lid > wood_limit ? "*** WARN " : "PASS ", "plywood lid ", lid_t,
           " mm, one foot between the rails: ", round(ch_s_lid*10)/10, " MPa (plywood limit ", wood_limit, ")"));
  ch_lid_side = (lid_w - spk_cut_d)/2;   // plywood left each side of a speaker hole
  echo(str(ch_lid_side >= fr_w ? "PASS " : "*** WARN ", "lid beside a speaker hole: ", ch_lid_side,
           " mm each side vs the ", fr_w, " mm rail under it — the lid still lands on both rails. ",
           "The hole carries nothing: each speaker needs a grille you can stand on."));
  echo(str(ch_Fb <= 0.9*ch_grip ? "PASS " : "*** WARN ", "bolt joint: ", round(ch_Fb), " N per bolt vs grip ",
           round(ch_grip), " N (M12 10.9 at ~100 N·m) -> ", ch_Fb <= 0.9*ch_grip ? "does not slip" : "SLIPS"));
  echo("  (static spring forces at the travel limits, no impact factor. The 141 MPa limit = 0.6 x 235 steel.)");

  echo("CUT LIST — REV 012:");
  echo(str("  100x40x2  rails                    2 x ", rail_len));
  echo(str("  100x40x2  front + rear cross members 2 x ", bay_w, "   -> ", 2*rail_len + 2*bay_w, " mm of 100x40x2"));
  echo(str("            each rail: 2 holes Ø", sleeve_od, " through BOTH walls, centres ", rl_end_x - rl_bolts[1], " and ",
           rl_end_x - rl_bolts[0], " mm from the rail's REAR end, ", hub_h + gp_yc - fr_bot,
           " mm up from the rail's bottom; weld a Ø", sleeve_od, "xØ", sleeve_id, " x ", fr_w, " steel sleeve in each"));
  echo(str("  60x6      green plate RIGHT (rear shock)  1 x ", gp_x1_tr - gp_x0));
  echo(str("  60x6      green plate LEFT (front shock)  1 x ", gp_x1_ld - gp_x0, "   -> ",
           (gp_x1_tr - gp_x0) + (gp_x1_ld - gp_x0), " mm of 60x6"));
  echo(str("  plywood ", lid_t, " mm  lid ", ct_x1 - fr_x0, " x ", lid_w, "  ·  plywood ", tray_t, " mm  tray ",
           ct_x1 - fr_x0, " x ", 2*rail_out));
  echo(str("  plywood ", spk_bhd_t, " mm  speaker bulkheads 2 x ", bay_w, " x ", fr_h,
           " (front faces at x ", spk_bhd_x[0], " and ", spk_bhd_x[1], ")"));
  echo(str("            lid: 2 holes Ø", spk_cut_d, " on the centreline, centres ", spk_cx[0] - fr_x0, " and ",
           spk_cx[1] - fr_x0, " mm from the lid's FRONT edge. Each hole needs a grille you can stand on."));
  echo(str("  hardware: 4x M12x65 10.9 + washer · 4x M12 weld nut (on the green plates) · 4x steel sleeve Ø",
           sleeve_od, "xØ", sleeve_id, "x", fr_w, " · 2x M8 green plate -> hub plate (+ weld all round)"));

  ch_rho    = 7.85e-6;
  ch_m_tube = (fr_h*fr_w - (fr_h - 2*fr_t)*(fr_w - 2*fr_t)) * (2*rail_len + 2*bay_w) * ch_rho;
  ch_m_gp   = gp_w*gp_t*((gp_x1_tr - gp_x0) + (gp_x1_ld - gp_x0)) * ch_rho;
  ch_m_sl   = 4*ch_Asl*fr_w*ch_rho;
  ch_m_lid  = (ct_x1 - fr_x0)*lid_w*lid_t*wood_rho;
  ch_m_tray = (ct_x1 - fr_x0)*2*rail_out*tray_t*wood_rho;
  ch_m_bhd  = 2*bay_w*fr_h*spk_bhd_t*wood_rho;
  ch_m_hw   = 0.5;
  echo(str("WEIGHT:   STEEL ~", round((ch_m_tube + ch_m_gp + ch_m_sl + ch_m_hw)*10)/10, " kg (tubes ", round(ch_m_tube*10)/10,
           " · green plates ", round(ch_m_gp*10)/10, " · sleeves ", round(ch_m_sl*10)/10, " · bolts+welds ~", ch_m_hw,
           ")  +  PLYWOOD ~", round((ch_m_lid + ch_m_tray + ch_m_bhd)*10)/10, " kg (lid + tray + ",
           round(ch_m_bhd*100)/100, " of speaker bulkheads)  ->  CHASSIS ~",
           round((ch_m_tube + ch_m_gp + ch_m_sl + ch_m_hw + ch_m_lid + ch_m_tray + ch_m_bhd)*10)/10,
           " kg (no pods, no batteries, no speakers, no front fork)"));
  echo("FILL IN — still guesses: front_cm_x · rider_kg · lid_t/tray_t/lid_over · shock_perch_d ·");
  echo("          head_ang · fork_off · fork_len · head_len · head_od · stock_axle_h · steer_lock ·");
  echo("          spk_cut_d (MEASURE the hole your driver needs) · spk_rim_d · spk_disp");
  echo("==========================================================================================");

} else if (render_mode == "chassis_link"){
  // ---- REV 012 close-up: how the rear pod hangs on the rails.
  // ---- Customizer: link_explode 0..150 pulls the pod back out.
  lk_bo = link_explode > 0 ? 55 : 0;
  chassis_frame(false, false);
  rear_link(lk_bo, link_explode);
  translate([wheelbase + link_explode, hub_h, 0]) pod_assembly("green");
  lk_z = rail_out + 40;
  lk_x = ct_x1 - 360;
  lk_r = wheelbase + 90 + link_explode;
  flag("1. RAIL 100x40x2 - ITS INNER FACE LIES ON THE GREEN PLATE",
       [rail_x1 - 50, fr_top, rail_in + fr_w/2],                                    [lk_x, fr_top + 230, lk_z], 9);
  flag("2. STEEL SLEEVE WELDED INSIDE THE RAIL AT EACH BOLT",
       [wheelbase + rl_bolts[0], hub_h + gp_yc + sleeve_od/2, rail_out],            [lk_x, fr_top + 170, lk_z], 9);
  flag("3. 2x M12 BOLTS, PUT IN FROM OUTSIDE",
       [wheelbase + rl_bolts[1], hub_h + gp_yc + 11, rail_out + 10.5 + lk_bo],      [lk_x, fr_top + 110, lk_z], 9);
  flag("4. REAR CROSS MEMBER KEEPS THE RAILS 172 APART",
       [ct_x1 - fr_w/2, fr_top, 0],                                                 [lk_x, hub_h - 100, lk_z], 9);
  flag("5. GREEN PLATE 60x6 - NO CUT",
       [wheelbase + link_explode - 40, hub_h + gp_yc + gp_w/2, gp_z0 + gp_t],       [lk_r, fr_top + 230, lk_z], 9);
  flag("6. OTHER END: FLAT ON THE HUB PLATE (AXLE + M8 + WELD)",
       [wheelbase + link_explode, hub_h + gp_m8[0], gp_z0 + gp_t],                  [lk_r, fr_top + 170, lk_z], 9);
  flag("7. M12 NUT WELDED ON THE GREEN PLATE (INSIDE)",
       [wheelbase + link_explode + rl_bolts[0], hub_h + gp_yc - 11, gp_z0 - 5],     [lk_r, fr_top + 110, lk_z], 9);
  echo(str("CHASSIS LINK: rail inner face on the green plate -> 2x M12 through rail + sleeve + plate into a weld nut",
           " · pod pulled back ", link_explode, " mm"));

} else if (render_mode == "chassis_plates"){
  // ---- REV 012 flat parts from the 60x6 bar, laid out for DXF / 1:1 print.
  //   openscad -o rev012_plates.dxf -D 'render_mode="chassis_plates"' apollo_track_pod_rev012.scad
  sh = -gp_x0 + 5;
  translate([sh, -gp_yc])      green_plate_2d(1);
  translate([sh, -80 - gp_yc]) green_plate_2d(-1);
  translate([5,  36])  text("GREEN PLATE RIGHT (+z) - REAR SHOCK EYE - NO CUT", size = 6);
  translate([5, -44])  text("GREEN PLATE LEFT (-z) - FRONT SHOCK EYE - NO CUT", size = 6);
  echo(str("CHASSIS PLATES (60x6): right plate ", gp_x1_tr - gp_x0, " · left plate ", gp_x1_ld - gp_x0,
           " · holes: axle key + Ø8.4 M8 ", gp_m8[0], " above it, Ø8.4 shock eye, 2x Ø", bolt_d + 1,
           " at x ", rl_bolts[0], " / ", rl_bolts[1], " from the axle, ", gp_yc, " above it"));
  // machine-readable numbers for make_rev012_templates.py (the 1:1 paper templates)
  echo(str("TEMPLATE_JSON {\"x0\":", gp_x0, ",\"x1_right\":", gp_x1_tr, ",\"x1_left\":", gp_x1_ld,
           ",\"w\":", gp_w, ",\"yc\":", gp_yc, ",\"bolts\":[", rl_bolts[0], ",", rl_bolts[1],
           "],\"bolt_hole\":", bolt_d + 1, ",\"m8_y\":", gp_m8[0], ",\"m8_hole\":8.4",
           ",\"eye_x\":", upP[0], ",\"eye_y\":", upP[1], ",\"eye_hole\":8.4",
           ",\"key_d\":10.4,\"key_flats\":8.9",
           ",\"rail_end_x\":", rl_end_x, ",\"rail_h\":", fr_h, ",\"rail_hole_up\":", hub_h + gp_yc - fr_bot,
           ",\"sleeve_od\":", sleeve_od, "}"));

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
  pod_assembly();
}
