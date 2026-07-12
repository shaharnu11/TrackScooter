// ============================================================================
//  APOLLO TRACK POD — Articulated "Split-Frame" Suspension Mod
//  Parametric OpenSCAD model · Rev 001a · 2026-07-10
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
// ============================================================================

/* [Render] */
render_mode = "assembly"; // [assembly, exploded, plates]
show_track    = true;
show_sprocket = true;
show_shocks   = true;
animate       = false;
lead_angle  = 0; // [-15:0.5:15]  front arm, + = bump (up)
trail_angle = 0; // [-15:0.5:15]  rear arm,  + = bump (up)

/* [Sheet-0 datums — MEASURE YOUR POD, mm] */
A = 260;   // idler axle centre-to-centre
B = 170;   // hub centre height above idler axle line
D = 100;   // idler wheel OD
G = 17;    // idler bearing bore (6203 = 17)
F = 75;    // belt inner width between guide lugs
H = 50;    // idler hub width
T = 12;    // belt carcass thickness

/* [Stock sprocket] */
sprocket_od    = 190;
sprocket_teeth = 23;
sprocket_w     = 60;   // measure across the sprocket rim
hex_af         = 24;   // vehicle axle hex across-flats

/* [Design parameters — blueprint defaults] */
plate_t    = 6.35;  // 1/4" arm fork plates
carrier_t  = 6;     // carrier plates
pivot_d    = 20;    // pivot axle
bushing_od = 25;    // SAE 841 flanged bushing
shock_ee   = 150;   // shock eye-to-eye, free
shock_sag  = 10;    // installed compression at ride height
theta      = 57;    // shock angle to arm at neutral, deg

$fa = 4; $fs = 0.7;

// ---------------------------------------------------------------- derived --
half   = A/2;
drop   = 20;                          // pivot sits 20 above idler axle line
P      = B - drop;                    // pivot drop below hub centre
C      = sqrt(half*half + drop*drop); // pivot-to-wheel arm length
na     = atan(drop/half);             // arm neutral droop angle, deg
a      = 0.68*C;                      // shock bolt station along arm
pivot  = [0, -P];

zi_tr  = H/2 + 1;                      // trailing fork inner face |z|
zi_ld  = zi_tr + plate_t + 1.5;        // leading fork inner face |z|
cz     = zi_ld + plate_t + 3;          // carrier plate inner face |z|
sz     = cz + carrier_t + 13;          // shock centre plane |z|
Rc     = sprocket_od/2 - 17;           // carrier disc radius
y_keel = -(P + 45);                    // keel standoff position
r_wrap = sprocket_od/2 + 2;            // belt wrap radius at sprocket
belt_w = F + 70;                       // belt overall width (approx.)
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

echo(str("DERIVED:  P=", P, "  C=", C, "  neutral droop=", na, " deg"));
echo(str("SHOCK:    lower eye station a=", a, "  upper eye at ", upP));
echo(str("TRAVEL:   wheel bump/droop = ±", C*sin(15), " mm at ±15°"));
echo(str("MOTION RATIO ≈ ", 0.68*sin(theta), "   (spring k = wheel k / MR²)"));

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
  difference(){
    union(){
      hull(){ circle(r=Rc);
              translate(pivot)      circle(d=56);
              translate([0,y_keel]) circle(d=30); }
      // anti-rotation lug (link exits laterally to chassis)
      hull(){ translate([0, Rc+2]) circle(d=24);
              translate([0, Rc-12]) square([44, 8], center=true); }
    }
    circle(d=52);                               // carrier bearing 6205-2RS
    translate(pivot)       circle(d=pivot_d);   // pivot bore, ream in pair
    translate([0, y_keel]) circle(d=8.5);       // keel standoff bolt M8
    translate([0, Rc+2])   circle(d=8.5);       // anti-rotation link bolt
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
    for (s=[1,-1]) translate([0,0,s*(H/2-6)])
      cylinder(h=12.2, d=40, center=true);      // bearing recesses
  }
  color([0.75,0.75,0.78]) for (s=[1,-1]) translate([0,0,s*(H/2-6)])
    difference(){ cylinder(h=10, d=40, center=true);
                  cylinder(h=12, d=G,  center=true); }
}

module sprocket(){
  color([0.13,0.13,0.14]) difference(){
    union(){
      cylinder(h=sprocket_w, d=sprocket_od-14, center=true);
      for (i=[0:sprocket_teeth-1]) rotate([0,0,i*360/sprocket_teeth])
        translate([sprocket_od/2-8, 0, 0])
          cube([14, 12, sprocket_w-4], center=true);
      cylinder(h=sprocket_w+14, d=72, center=true);
    }
    cylinder(h=sprocket_w+40, d=hex_af/cos(30), center=true, $fn=6);
    for (i=[0:7]) rotate([0,0,i*45]) translate([56,0,0])
      cylinder(h=sprocket_w+2, d=32, center=true);   // spoke windows
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
  // plates
  color([0.36,0.43,0.56]) for (s=[1,-1])
    translate([0,0, (s==1 ? cz : -cz-carrier_t) + s*ex*55])
      linear_extrude(carrier_t) carrier_2d();
  // upper shock tabs, welded to carrier OUTER faces
  color([0.36,0.43,0.56]) for (s=[1,-1])
    translate([0,0, (s==1 ? cz+carrier_t : -(sz-5)) + s*ex*55])
      linear_extrude((sz-5)-(cz+carrier_t)) upper_tab_2d(s==1 ? upP : mx(upP));
  // centre axle sleeve + carrier bearings
  color([0.55,0.55,0.58]) difference(){
    cylinder(h=2*(cz+carrier_t), d=25, center=true);
    cylinder(h=2*cz+40, d=hex_af/cos(30)+1, center=true, $fn=6); }
  color([0.8,0.8,0.82]) for (s=[1,-1])
    translate([0,0, s*(cz+carrier_t/2) + s*ex*55])
      difference(){ cylinder(h=15, d=52, center=true);
                    cylinder(h=17, d=25, center=true); }
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
