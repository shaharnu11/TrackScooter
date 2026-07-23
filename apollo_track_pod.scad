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
// ============================================================================

/* [Render] */
render_mode = "assembly"; // [assembly, exploded, plates, tensioner, part]
// render_mode="part": renders one BOM item alone (thumbnails for the §7
// shopping guide). Pick the item with the part variable below.
part = "bushing"; // [pivot_axle, arm_plates, carrier_plates, boss_tube, bushing, thrust_washer, spacer_tube, shock, shock_mounts, fork_hw, keel, draw_bolt, hardware, zerk, idler_axle, reused]
show_track    = true;
show_sprocket = true;
show_shocks   = true;
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
B = 170;   // hub centre height above idler axle line
D = 108;   // idler wheel OD (WJ wheel)
G = 15;    // idler bearing bore (6302-2RS = 15)
brg_od = 42;      // idler bearing OD (6302)
brg_w  = 13;      // idler bearing width (6302)
F = 62;    // belt inner width between guide lugs — derived: H + 4 (matched set)
lug_w = 18;// guide lug row width — conservative estimate, measure
lug_h = 20;// guide lug height — owner estimates 10-20; keeping pessimistic 20
H = 58;    // idler hub width (measured 57.85)
T = 12;    // belt carcass thickness (confirmed ~12)

/* [Stock sprocket — hub motor] */
sprocket_od    = 180;
sprocket_teeth = 10;   // counted. 10T x 60 pitch → pitch/cord circle Ø191,
                       // i.e. the belt cord line rides 5.5 above the Ø180 surface
sprocket_w     = 60;   // measure across the sprocket rim

/* [Fork mount — Rev 002: carriers hang from the scooter fork legs] */
fork_gap = 140;  // inner spacing between fork legs: 140 FRONT AND REAR
                 // (Rev 003 — re-measured; both pods identical, was 120/140)
leg_t    = 4;    // fork leg thickness (z) — MEASURED 2026-07-13 (was 30 placeholder)
axle_d   = 10;   // hub-motor axle Ø (flatted, static — motor spins around it)

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
keel_od    = 12;    // keel standoff tube OD (Rev 003a: was 16 — Ø12×1.5, ID 9)
a_frac     = 0.46;  // shock bolt station as fraction of C (Rev 004: was 0.485 —
                    // the bolt moved onto the bar centreline (shock_y 18 -> 0),
                    // which is closer to the wheel, so a comes in to keep the
                    // 4 mm wheel clearance. Rev 003a: 0.68 was INSIDE the wheel.)
shock_y    = 0;     // lower shock bolt offset from the arm axis (Rev 004: 0 —
                    // a Ø10 hole at y=18 has <2 mm edge in a 40 mm bar)
shock_ee   = 150;   // shock eye-to-eye, free
shock_sag  = 10;    // installed compression at ride height
theta      = 72;    // shock angle to arm at neutral, deg (Rev 004: was 68 —
                    // with the lower eye at shock_y=0 the shock line must stay
                    // near-vertical so the coil (Ø~44) clears the 50 mm carrier
                    // strip; upper eye lands at (±51, −10). MR ≈ 0.435)
bump_max   = 15;    // arm travel limit, deg (clearance guard checks this)

$fa = 4; $fs = 0.7;

// ---------------------------------------------------------------- derived --
// Belt-path length for candidate idler spacing Av, measured along the belt's
// inextensible CORD LINE (not the inner surface): 10T x 60 pitch → cord circle
// Ø191 on the Ø180 sprocket → cords ride cord_off above the rubber's inner face.
// Path = sprocket wrap + 2 tangent runs + 2 idler wraps + bottom span.
// Monotonic in Av → bisect to hit track_len.
track_len = belt_links * belt_pitch;             // 1080 — cord-line length
pitch_r   = sprocket_teeth * belt_pitch / (2*PI);// 95.49 — cord radius at sprocket
cord_off  = pitch_r - sprocket_od/2;             // 5.49 — cord height above rubber
rs_belt = pitch_r;                    // cord-line wrap radius at sprocket
ri_belt = D/2 + cord_off;             // cord-line wrap radius at idlers
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
drop   = 38;                          // pivot sits 38 above idler axle line
                                      // (raised 20->30->38 for belt clearance;
                                      //  keel window closes at drop=42)
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
y_keel = -(sprocket_od/2 + 10);        // keel standoff BETWEEN sprocket swept
                                       // disc (steel, r=90) and the ARM boss
                                       // disc (Rev 003a: window is bounded by
                                       // the Ø44 plate disc top, not the Ø32
                                       // tube — Ø12 tube fits with 4/4 mm)
// pivot-stack cut lengths (Rev 003a): the bosses stack end-to-end through
// thrust washers, so the centre spacer and the two outboard sleeves are what
// close the chain carrier-to-carrier. All three are cut at the §9.3 dry-stack.
sp_half   = zi_tr + plate_t - boss_len - 4.5;  // washer 1.5 + flange 3
sleeve_z0 = zi_ld + boss_len + 4.5;            // leading boss end + flange + washer
sleeve_ln = cz - sleeve_z0;                    // outboard sleeve length
r_wrap = sprocket_od/2 + 2;            // belt INNER surface at sprocket (visual)
belt_w = track_w;                      // belt overall width (measured)
ride_len = shock_ee - shock_sag;

function rot2(p, ang) = [ p[0]*cos(ang) - p[1]*sin(ang),
                          p[0]*sin(ang) + p[1]*cos(ang) ];
function arm_pt(local, arm_ang) = pivot + rot2(local, -na + arm_ang);
function mx(p) = [-p[0], p[1]];

low0   = arm_pt([a, shock_y], 0);                  // lower shock eye, neutral
up_dir = -na + 180 - theta;                        // shock leans in toward hub
upP    = low0 + ride_len*[cos(up_dir), sin(up_dir)]; // upper eye (FIXED)

aL = animate ? 15*sin($t*360)       : lead_angle;
aT = animate ? 15*sin($t*360 + 180) : trail_angle;

wheel_tr = arm_pt([C + tension_pos, 0], aT);  // axle position in tensioner slot
wheel_ld = mx(arm_pt([C, 0], aL));

echo(str("BELT:     solved A=", A_eff, "  inner length=", belt_len(A_eff),
         " / target ", track_len));
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
echo(str("PIVOT STACK: centre spacer ≈ ", 2*sp_half, " · outboard sleeves ≈ ",
         sleeve_ln, " ×2 — all Ø22×3 tube, cut at the §9.3 dry-stack"));
echo(str("TENSIONER: axle at +", tension_pos, " of 25 mm slot take-up — ",
         25 - tension_pos, " mm remaining (render_mode=\"tensioner\" for the ",
         "Sheet-6 close-up; advance both draw bolts evenly)"));
// draw-bolt head must stay radially inside the belt wrap at the wheel (D/2)
tens_head_gap = D/2 - ((34 + 18) - tension_pos);
echo(str(tens_head_gap < 2 ? "*** WARN " : "PASS ",
         "draw-bolt head to belt wrap: ", tens_head_gap,
         " mm at tension_pos=", tension_pos));
// cut/buy lengths that follow from fork_gap + leg_t (echoed so the BOM can
// be verified against the measured fork instead of the old 30 mm assumption)
axle_stack = 2*(cz + carrier_t) + 22;   // carriers outer-to-outer + nut/head
echo(str("PIVOT AXLE: stack ≈ ", axle_stack, " → buy M", pivot_d, " cl.10.9 × ",
         10*ceil((axle_stack + 3)/10), " part-threaded (this fork_gap=",
         fork_gap, ", leg_t=", leg_t, ")"));
echo(str("KEEL: tube Ø", keel_od, "×1.5 cut ", 2*cz, " · M8 rod cut ≈ ",
         2*(cz+carrier_t)+12));
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
  [[str("keel standoff  Ø", keel_od), (y_keel - keel_od/2) - y_lug_bump],
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
keel_gaps = [
  ["keel to sprocket swept disc", abs(y_keel) - keel_od/2 - sprocket_od/2],
  [str("keel to arm bar (", boss_disc, " wide)"),
        abs(y_keel - pivot[1]) - boss_disc/2 - keel_od/2],
  ["keel to pivot washers Ø30",   abs(y_keel - pivot[1]) - 15 - keel_od/2],
  // Rev 003a: the lower shock through-bolt and the cross-brace share the
  // space between the fork plates with the Ø108 idler wheel — check both
  ["shock bolt Ø8 to idler wheel", sqrt(pow(C - a, 2) + shock_y*shock_y) - D/2 - 4],
  ["cross-brace to idler wheel",    sqrt(pow(C - 58, 2) + 6*6) - D/2],
  // coil spring (Ø~44, r22 about the shock line) vs the carrier tongue edge
  // (|x| ≤ 24): evaluated at the coil's top turn, ~25 mm below the upper eye,
  // the closest point since the line leans away from the tongue going down
  ["shock coil Ø44 to carrier strip (50 wide)",
     (upP[0] + ((25)/(upP[1]-low0[1]))*(low0[0]-upP[0])) - 25 - 22]];
for (g = keel_gaps)
  echo(str(g[1] < 2 ? "*** WARN " : "PASS ", g[0], ": ", g[1], " mm gap"));

ex = (render_mode == "exploded") ? 1 : 0;

// ============================================================== 2D profiles
module arm_plate_2d(slot=false){
  // Rev 004: plain flat-bar rectangle, 40 wide — no profile cutting.
  // Trailing bar cut ≈185, leading ≈166; only straight cuts + drilled holes.
  send = slot ? 18 : 0;
  difference(){
    translate([-22, -boss_disc/2]) square([22 + C + send + 26, boss_disc]);
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

module carrier_2d(){
  // Rev 004: plain 50-wide flat-bar strip, cut ≈225 — every centreline feature
  // (axle slot, M8 fork bolt, pivot bore, keel hole) lands on it. The shock
  // tabs are separate stubs (tab_stub_2d) lap-welded on the OUTER face at hub
  // level. Same part both sides (symmetric).
  difference(){
    translate([-25, pivot[1]-24]) square([50, (52+16) - (pivot[1]-24)]);
    // hub-motor axle slot: Ø10 with flats — the plate doubles as a torque arm
    intersection(){ circle(d=axle_d+0.4);
                    square([axle_d+0.4, 8.9], center=true); }
    translate([0,52])      circle(d=8.5);       // M8 into fork leg (drill leg)
    translate(pivot)       circle(d=pivot_d);   // pivot bore, ream in pair
    translate([0, y_keel]) circle(d=8.5);       // keel standoff bolt M8
  }
}

module tab_stub_2d(p){
  // Rev 004: upper shock tab = 40×6 flat-bar stub, ≈55 long, lap-welded onto
  // the carrier strip's OUTER face at hub level (17 mm lap onto the strip,
  // clear of the axle slot). Ø8.4 eye pin hole at p (M8 pin — Rev 004b:
  // shock eyes measured Ø8). Sits ABOVE the coil-top
  // line, so the spring corridor stays clear.
  s = p[0] > 0 ? 1 : -1;
  difference(){
    translate([s==1 ? 8 : -63, -20]) square([55, 40]);
    translate(p) circle(d=8.4);
  }
}

// ============================================================== components
// Sheet-6 belt tensioner, local arm coords (pivot at origin, wheel end +x).
// Motorcycle chain-adjuster style: welded lug across each fork-plate tip,
// M6 EYE NUT riding on the protruding axle end (Rev 004a), M6 draw bolt
// through the lug threading into the block. Head + jam nut bear on the lug's
// REAR face -> advancing the bolt DRAWS the axle rearward through the slot;
// belt tension (which pulls the axle forward) loads the bolt in tension.
// Lug position: front face at C+34 — behind the slot's rear end (C+32.7),
// forward of the plate tip (C+44). This keeps the bolt head within 52 mm of
// the axle at every slot position (belt wrap radius at the wheel = D/2 = 54;
// a tip-mounted lug would have pushed the head THROUGH the belt at slack).
// Block-rear meets lug-front exactly at full 25 mm take-up = natural stop.
xl_lug = 34;                      // lug front face, mm behind nominal axle (C)
module tensioner_hw(zi){
  zo = zi + plate_t;              // fork-plate outer face
  xl = C + xl_lug;                // lug front face
  bz = zo + 11;                   // draw-bolt axis, outboard of the plate
  for (s=[1,-1]) scale([1,1,s]){
    // welded lug: upright standing on the plate outer face, weld all around
    color([0.30,0.36,0.48]) difference(){
      translate([xl, -13, zo]) cube([6, 26, (bz - zo) + 7]);
      translate([xl-1, 0, bz]) rotate([0,90,0]) cylinder(h=8, d=6.6);
    }
    // 7 mm standoff ring between plate outer face and eye nut (sets the eye
    // at the lug-hole height; cut from the Ø22×3 tube)
    color([0.55,0.55,0.58]) translate([C + tension_pos, 0, zo])
      difference(){ cylinder(h=7, d=22); cylinder(h=9, d=15.4); }
    // M6 lifting EYE NUT on the protruding axle end (Rev 004a — replaces the
    // drilled+tapped block: eye Ø20 over the Ø15 axle, threaded boss toward
    // the lug; zero fabrication). DIN 582-style, eye d2=20, section s=8.
    color([0.45,0.45,0.48]) translate([C + tension_pos, 0, bz]){
      difference(){ cylinder(h=8, d=36, center=true);          // eye ring
                    cylinder(h=10, d=20, center=true); }
      translate([13,0,0]) rotate([0,90,0]) difference(){       // threaded boss
        cylinder(h=10, d=13, center=true);
        cylinder(h=12, d=5, center=true); }
    }
    // M6 draw bolt: from the eye-nut boss, through the lug; jam nut + head
    color([0.55,0.55,0.58]){
      translate([C + tension_pos - 8, 0, bz]) rotate([0,90,0])
        cylinder(h=(xl + 16) - (C + tension_pos - 8), d=5.8);
      translate([xl + 6.5,  0, bz]) rotate([0,90,0])
        cylinder(h=5.2, d=11.5, $fn=6);   // M6 jam nut against the lug
      translate([xl + 13.5, 0, bz]) rotate([0,90,0])
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
    color(cSteel) linear_extrude(6) translate([-8,20,0]) tab_stub_2d(upP);
    color(cSteel) translate([55,-15,0]) cat_tube(15,9,45);
  } else if (name == "fork_hw"){                 // BOM 10 — M8 bolt + nuts
    color(cSteel) rotate([0,90,0]) cat_bolt(8, 12, 18, 13, 5.5);
    color(cSteel) translate([20,-22,0]) cat_hexnut(13, 8, 6.9);
    color(cSteel) translate([45,-22,0]) cat_hexnut(17, 10, 8.8);  // stock M10
  } else if (name == "keel"){                    // BOM 11 — tube + rod + nuts
    color(cSteel) rotate([0,90,0]) cat_tube(keel_od,9,148);
    color(cSteel) translate([0,30,0]) rotate([0,90,0]) cat_threads(8,172);
    color(cSteel) for (i=[0:3]) translate([20+i*28,55,0]) cat_hexnut(13,7,6.9);
  } else if (name == "draw_bolt"){               // BOM 12 — bolt + jam + eye nut
    color(cSteel) rotate([0,90,0]) cat_bolt(6, 4, 52, 10, 4);
    color(cSteel) translate([25,-24,0]) cat_hexnut(10, 5, 5.2);
    color([0.45,0.45,0.48]) translate([62,-24,0]){
      difference(){ cylinder(h=8, d=36, center=true);
                    cylinder(h=10, d=20, center=true); }
      translate([0,-16,0]) rotate([90,0,0]) difference(){
        cylinder(h=10, d=13, center=true);
        cylinder(h=12, d=5, center=true); } }
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
  color([0.16,0.16,0.17]) difference(){
    cylinder(h=H, d=D, center=true);
    cylinder(h=H+2, d=G, center=true);
    for (s=[1,-1]) translate([0,0,s*(H/2 - brg_w/2)])
      cylinder(h=brg_w+0.2, d=brg_od+0.4, center=true); // 6302 bearing recesses
  }
  color([0.75,0.75,0.78]) for (s=[1,-1]) translate([0,0,s*(H/2 - brg_w/2)])
    difference(){ cylinder(h=brg_w,   d=brg_od, center=true);
                  cylinder(h=brg_w+2, d=G,      center=true); }
}

module sprocket(){
  // Rev 002: the sprocket IS the hub motor — casing drawn, axle Ø10 static
  color([0.13,0.13,0.14]) difference(){
    union(){
      cylinder(h=sprocket_w, d=sprocket_od-14, center=true);
      for (i=[0:sprocket_teeth-1]) rotate([0,0,i*360/sprocket_teeth])
        translate([sprocket_od/2-8, 0, 0])
          cube([14, 12, sprocket_w-4], center=true);
      cylinder(h=sprocket_w+8, d=130, center=true);  // motor casing
    }
    cylinder(h=sprocket_w+40, d=axle_d+0.5, center=true);
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
    color([0.30,0.36,0.48]) translate([28, -18, -zi]) cube([30, 12, 2*zi]);
    // shock through-bolt + outboard spacer sleeve
    color([0.55,0.55,0.58]) translate([a, shock_y, -(zi+plate_t)-4])
      cylinder(h=(zi+plate_t)+4 + (sz-5), d=7.8);
    color([0.55,0.55,0.58]) translate([a, shock_y, szs>0 ? zi+plate_t : -(sz-5)])
      difference(){ cylinder(h=(sz-5)-(zi+plate_t), d=15);
                    cylinder(h=sz, d=8.5); }
    // wheel + MEROCA 15x148 thru-axle with its full spacer stack (Rev 004a).
    // Only the tip 9 mm is threaded, so cut-to-fit filler sleeves place the
    // M15x1.5 nut exactly on the thread. Head at -z, nut at +z.
    wx = slot ? C + tension_pos : C;
    z_head = slot ? -(zi + plate_t + 7 + 8) : -(zi + plate_t);  // shank start
    translate([wx, 0, 0]){
      translate([0,0, ex* (szs>0 ? 0 : 0)]) idler_wheel();
      color([0.55,0.55,0.58]){
        translate([0,0,z_head]) cylinder(h=148, d=G);           // Ø15 shank
        translate([0,0,z_head-3]) cylinder(h=3, d=21);          // head flange
      }
      // washers plate->bearing inner race (trailing) / centering sleeves (leading)
      color([0.8,0.8,0.82]) for (s=[1,-1]) scale([1,1,s])
        if (slot) translate([0,0,29])
          difference(){ cylinder(h=1, d=26); cylinder(h=3, d=15.4, center=true); }
        else translate([0,0,29])
          difference(){ cylinder(h=8.85, d=22); cylinder(h=20, d=15.4, center=true); }
      // filler sleeve + washer + M15x1.5 nut on the +z end
      fz0 = slot ? zi + plate_t + 7 + 8 : zi + plate_t;         // stack end |z|
      fln = (z_head + 148 - 8.5) - fz0;                         // filler length
      color([0.55,0.55,0.58]) translate([0,0,fz0])
        difference(){ cylinder(h=fln, d=22); cylinder(h=fln+2, d=15.4, center=true); }
      color([0.8,0.8,0.82]) translate([0,0,fz0+fln])
        difference(){ cylinder(h=1.5, d=28); cylinder(h=4, d=15.4, center=true); }
      color([0.45,0.45,0.48]) translate([0,0,fz0+fln+1.5])
        difference(){ cylinder(h=6, d=24, $fn=6); cylinder(h=8, d=15, center=true); }
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
  // Rev 004: tab stubs (40×6 bar) lap-welded on the carrier OUTER faces; the
  // eye pin cantilevers from the stub out to the shock plane through washers
  tab_z0 = cz + carrier_t;
  color([0.36,0.43,0.56]) for (s=[1,-1])
    translate([0,0, (s==1 ? tab_z0 : -(tab_z0 + 6)) + s*ex*55])
      linear_extrude(6){ tab_stub_2d(s==1 ? upP : mx(upP));
                         tab_stub_2d(s==1 ? mx(upP) : upP); }
  // hub-motor axle: static Ø10, spans fork legs + both plates
  color([0.55,0.55,0.58])
    cylinder(h=2*(cz+carrier_t)+24, d=axle_d, center=true);
  // ghost fork legs (context only — measure leg_t)
  color([0.45,0.50,0.60,0.35]) for (s=[1,-1])
    translate([-20, -12, s==1 ? fork_gap/2 : -fork_gap/2-leg_t])
      cube([40, 150, leg_t]);
  // keel standoff between sprocket disc and arm boss disc
  color([0.55,0.55,0.58]) translate([0, y_keel, -cz])
    difference(){ cylinder(h=2*cz, d=keel_od); cylinder(h=2*cz+2, d=8.4); }
  color([0.55,0.55,0.58]) translate([0, y_keel, -cz-carrier_t-6-ex*70])
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
  // 2D layout for DXF export — all laser-cut steel, flat
  carrier_2d();                                             // carrier L
  translate([2.4*Rc, 0]) mirror([1,0]) carrier_2d();        // carrier R
  translate([-Rc-40, -P-C+40]) rotate([0,0,90]){
    arm_plate_2d(false);                                    // leading ×2
    translate([0, 90])  arm_plate_2d(false);
    translate([0, 180]) arm_plate_2d(true);                 // trailing ×2
    translate([0, 270]) arm_plate_2d(true);
  }
  translate([0, -2.6*P]) for (i=[0:3])                      // tab stubs ×4
    translate([i*70, 0] - [8,-20]) intersection(){
      tab_stub_2d(upP); translate([8,-20]) square([55,40]); }
} else if (render_mode == "part"){
  part_catalog(part);
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
  flag("M6 EYE NUT ON AXLE END (Ø20 EYE)",
       [C + tension_pos, 9, zo+13],  [C-52, 42, zo+26]);
  flag("WELDED LUG",
       [C+37, -12, zo+9],            [C+50, -34, zo+26]);
  flag("DRAW BOLT + JAM NUT",
       [C+52, 0, zo+11],             [C+42, 24, zo+26]);
} else {
  // trailing arm (rear, +x) and leading arm (front, -x, mirrored)
  translate([ ex*60, 0, 0]) arm3d(zi_tr, true,  aT, +1);
  translate([-ex*60, 0, 0]) mirror([1,0,0]) arm3d(zi_ld, false, aL, -1);

  carrier_group();
  pivot_axle_group();

  if (show_shocks){
    translate([0,0,  ex*80]) shock3d(upP,     arm_pt([a,shock_y], aT),      sz);
    translate([0,0, -ex*80]) shock3d(mx(upP), mx(arm_pt([a,shock_y], aL)), -sz);
  }
  if (show_sprocket) translate([0, ex*150, 0]) sprocket();
  if (show_track && ex == 0) track3d();
}
