// ============================================================================
//  APOLLO TRACK POD — Articulated "Split-Frame" Suspension Mod
//  Parametric OpenSCAD model · Rev 002 · 2026-07-12
//  Companion to the blueprint artifact (Sheets 0–6).
//
//  HOW TO USE
//   1. Measure your pod per blueprint Sheet 0 and set datums A,B,D,G,F,H,T below.
//   2. Open in OpenSCAD, press F5 (preview) / F6 (render).
//   3. render_mode:
//        "assembly"  full pod at ride height (set lead_angle/trail_angle)
//        "exploded"  parts separated for assembly reference
//        "plates"    2D flat layout of all steel plates -> export DXF for laser
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
// ============================================================================

/* [Render] */
render_mode = "assembly"; // [assembly, exploded, plates]
show_track    = true;
show_sprocket = true;
show_shocks   = true;
animate       = false;
lead_angle  = 0; // [-15:0.5:15]  front arm, + = bump (up)
trail_angle = 0; // [-15:0.5:15]  rear arm,  + = bump (up)

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
fork_gap = 120;  // inner spacing between fork legs: FRONT 120, REAR 140
leg_t    = 30;   // fork leg thickness (z) — PLACEHOLDER, measure
axle_d   = 10;   // hub-motor axle Ø (flatted, static — motor spins around it)

/* [Design parameters — blueprint defaults] */
plate_t    = 6.35;  // 1/4" arm fork plates
carrier_t  = 6;     // carrier plates
pivot_d    = 20;    // pivot axle
bushing_od = 25;    // SAE 841 flanged bushing
shock_ee   = 150;   // shock eye-to-eye, free
shock_sag  = 10;    // installed compression at ride height
theta      = 57;    // shock angle to arm at neutral, deg
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
a      = 0.68*C;                      // shock bolt station along arm
pivot  = [0, -P];

zi_tr  = H/2 + 1;                      // trailing fork inner face |z|
zi_ld  = zi_tr + plate_t + 1.5;        // leading fork inner face |z|
cz     = fork_gap/2 + leg_t;           // carrier inner face = fork-leg OUTER face
sz     = track_w/2 + 14;               // shock plane: between belt edge and carrier
Rc     = sprocket_od/2 - 17;           // carrier disc radius
y_keel = -(sprocket_od/2 + 14);        // keel standoff BETWEEN sprocket swept
                                       // disc (steel, r=90) and pivot boss
                                       // (Rev 001b: was P+45 below pivot — hit
                                       // belt at bump; 001c: raised with boss)
r_wrap = sprocket_od/2 + 2;            // belt INNER surface at sprocket (visual)
belt_w = track_w;                      // belt overall width (measured)
ride_len = shock_ee - shock_sag;

function rot2(p, ang) = [ p[0]*cos(ang) - p[1]*sin(ang),
                          p[0]*sin(ang) + p[1]*cos(ang) ];
function arm_pt(local, arm_ang) = pivot + rot2(local, -na + arm_ang);
function mx(p) = [-p[0], p[1]];

low0   = arm_pt([a, 18], 0);                       // lower shock eye, neutral
up_dir = -na + 180 - theta;                        // shock leans in toward hub
upP    = low0 + ride_len*[cos(up_dir), sin(up_dir)]; // upper eye (FIXED)

aL = animate ? 15*sin($t*360)       : lead_angle;
aT = animate ? 15*sin($t*360 + 180) : trail_angle;

wheel_tr = arm_pt([C + 8, 0], aT);        // +8 = tensioner mid-slot
wheel_ld = mx(arm_pt([C, 0], aL));

echo(str("BELT:     solved A=", A_eff, "  inner length=", belt_len(A_eff),
         " / target ", track_len));
echo(str("DERIVED:  P=", P, "  C=", C, "  neutral droop=", na, " deg"));
echo(str("SHOCK:    lower eye station a=", a, "  upper eye at ", upP));
echo(str("TRAVEL:   bump +", C*(sin(bump_max-na)+sin(na)),
         " / droop -", C*(sin(bump_max+na)-sin(na)), " mm at ±", bump_max, "°"));
echo(str("MOTION RATIO ≈ ", 0.68*sin(theta), "   (spring k = wheel k / MR²)"));

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
  [["keel standoff  Ø16", (y_keel   -  8)   - y_lug_bump],
   ["pivot spacer   Ø25", (pivot[1] - 12.5) - y_lug_bump],
   ["pivot boss     Ø32", (pivot[1] - 16)   - y_lug_bump]]);
if (cz >= track_w/2 + 3)
  echo(str("NOTE carrier plates at |z|=", cz, " — outside the belt (half-width ",
           track_w/2, "); they cannot contact the track at any bump"));
echo(str(fork_gap/2 - track_w/2 < 3 ? "*** TIGHT " : "OK ",
         "belt edge to fork leg: ", fork_gap/2 - track_w/2, " mm per side"));
for (c = clearances)
  echo(str(c[1] < 5 ? "*** WARN " : "PASS ", c[0], ": ", c[1],
           " mm above track at +", bump_max, "° bump"));
// keel window fit (both are static-to-static, small gaps acceptable)
keel_gaps = [
  ["keel to sprocket swept disc", abs(y_keel) - 8 - sprocket_od/2],
  ["keel to pivot washers Ø36",   abs(y_keel - pivot[1]) - 18 - 8]];
for (g = keel_gaps)
  echo(str(g[1] < 2 ? "*** WARN " : "PASS ", g[0], ": ", g[1], " mm gap"));

ex = (render_mode == "exploded") ? 1 : 0;

// ============================================================== 2D profiles
module arm_plate_2d(slot=false){
  send = slot ? 18 : 0;
  difference(){
    hull(){ circle(d=64); translate([C+send, 0]) circle(d=52); }
    circle(d=bushing_od);                       // bushing seat Ø25 H7
    if (slot) hull(){ translate([C,0])    circle(d=G+0.4);
                      translate([C+25,0]) circle(d=G+0.4); }
    else      translate([C,0]) circle(d=G+0.4); // wheel axle bore
    translate([a, 18]) circle(d=10);            // lower shock bolt Ø10
  }
}

module carrier_2d(){
  // Rev 002: fork-hung torque-arm plate. Same part both sides (symmetric).
  difference(){
    union(){
      hull(){ circle(d=44);                       // hub-motor axle boss
              translate([0,52]) circle(d=32); }   // fork-leg bolt strap
      hull(){ circle(d=44);
              translate(pivot)      circle(d=48);
              translate([0,y_keel]) circle(d=30); }
      for (p = [upP, mx(upP)])                    // shock-tab weld lobes, both
        hull(){ circle(d=44);                     // sides so L/R part is common
                translate(p) circle(d=30);
                translate(p + [8,-34]) circle(d=30); }
    }
    // hub-motor axle slot: Ø10 with flats — the plate doubles as a torque arm
    intersection(){ circle(d=axle_d+0.4);
                    square([axle_d+0.4, 8.9], center=true); }
    translate([0,52])      circle(d=8.5);       // M8 into fork leg (drill leg)
    translate(pivot)       circle(d=pivot_d);   // pivot bore, ream in pair
    translate([0, y_keel]) circle(d=8.5);       // keel standoff bolt M8
  }
}

module upper_tab_2d(p){
  difference(){
    hull(){ translate(p) circle(d=22);
            translate(p + [8,-34]) circle(d=30); } // weld foot, clear of bore
    translate(p) circle(d=10);
  }
}

// ============================================================== components
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
    // pivot boss tube, welded through both plates
    color([0.30,0.36,0.48]) difference(){
      cylinder(h=2*(zi+plate_t)+6, d=32, center=true);
      cylinder(h=2*(zi+plate_t)+10, d=bushing_od, center=true); }
    // bronze bushings (flanged, 4 per pod)
    color([0.72,0.53,0.30]) for (s=[1,-1]) translate([0,0, s*(zi+plate_t/2)])
      difference(){ cylinder(h=plate_t+3, d=bushing_od+0.01, center=true);
                    cylinder(h=plate_t+6, d=pivot_d, center=true); }
    // lower cross-brace
    color([0.30,0.36,0.48]) translate([a-25, -26, -zi]) cube([50, 12, 2*zi]);
    // shock through-bolt + outboard spacer sleeve
    color([0.55,0.55,0.58]) translate([a, 18, -(zi+plate_t)-4])
      cylinder(h=(zi+plate_t)+4 + (sz-5), d=9.8);
    color([0.55,0.55,0.58]) translate([a, 18, szs>0 ? zi+plate_t : -(sz-5)])
      difference(){ cylinder(h=(sz-5)-(zi+plate_t), d=15);
                    cylinder(h=sz, d=10); }
    // wheel + axle
    wx = slot ? C+8 : C;
    translate([wx, 0, 0]){
      translate([0,0, ex* (szs>0 ? 0 : 0)]) idler_wheel();
      color([0.55,0.55,0.58])
        cylinder(h=2*(zi+plate_t)+18, d=G, center=true);
    }
  }
}

module carrier_group(){
  // plates (Rev 002: bolted to the fork-leg outer faces)
  color([0.36,0.43,0.56]) for (s=[1,-1])
    translate([0,0, (s==1 ? cz : -cz-carrier_t) + s*ex*55])
      linear_extrude(carrier_t) carrier_2d();
  // upper shock tabs, welded to carrier INNER faces (shocks run between
  // belt edge and carrier — Rev 002; they were outboard in 001a)
  color([0.36,0.43,0.56]) for (s=[1,-1])
    translate([0,0, (s==1 ? sz+5 : -cz) + s*ex*55])
      linear_extrude(cz-(sz+5)) upper_tab_2d(s==1 ? upP : mx(upP));
  // hub-motor axle: static Ø10, spans fork legs + both plates
  color([0.55,0.55,0.58])
    cylinder(h=2*(cz+carrier_t)+24, d=axle_d, center=true);
  // ghost fork legs (context only — measure leg_t)
  color([0.45,0.50,0.60,0.35]) for (s=[1,-1])
    translate([-20, -12, s==1 ? fork_gap/2 : -fork_gap/2-leg_t])
      cube([40, 150, leg_t]);
  // keel standoff below pivot
  color([0.55,0.55,0.58]) translate([0, y_keel, -cz])
    difference(){ cylinder(h=2*cz, d=16); cylinder(h=2*cz+2, d=8.4); }
  color([0.55,0.55,0.58]) translate([0, y_keel, -cz-carrier_t-6-ex*70])
    cylinder(h=2*(cz+carrier_t)+12, d=8);
}

module pivot_axle_group(){
  translate([0, -ex*110, 0]) translate([pivot[0], pivot[1], 0]){
    color([0.45,0.45,0.48]){
      cylinder(h=2*(cz+carrier_t)+22, d=pivot_d, center=true);      // axle
      translate([0,0,  cz+carrier_t+11]) cylinder(h=13, d=34, $fn=6); // head
      translate([0,0,-(cz+carrier_t+24)]) cylinder(h=13, d=32, $fn=6); // nylock
    }
    color([0.55,0.55,0.58]) difference(){                            // spacer
      cylinder(h=2*zi_tr, d=25, center=true);
      cylinder(h=2*zi_tr+2, d=pivot_d+0.4, center=true); }
    color([0.8,0.8,0.82]) for (s=[1,-1]) for (zz=[zi_tr-0.75, zi_ld+plate_t+1])
      translate([0,0, s*zz]) difference(){                           // washers
        cylinder(h=1.5, d=36, center=true);
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
  translate([0, -2.6*P]) for (i=[0:1])                      // upper tabs ×2
    translate([i*70, 0] - upP) upper_tab_2d(upP);
} else {
  // trailing arm (rear, +x) and leading arm (front, -x, mirrored)
  translate([ ex*60, 0, 0]) arm3d(zi_tr, true,  aT, +1);
  translate([-ex*60, 0, 0]) mirror([1,0,0]) arm3d(zi_ld, false, aL, -1);

  carrier_group();
  pivot_axle_group();

  if (show_shocks){
    translate([0,0,  ex*80]) shock3d(upP,     arm_pt([a,18], aT),      sz);
    translate([0,0, -ex*80]) shock3d(mx(upP), mx(arm_pt([a,18], aL)), -sz);
  }
  if (show_sprocket) translate([0, ex*150, 0]) sprocket();
  if (show_track && ex == 0) track3d();
}
