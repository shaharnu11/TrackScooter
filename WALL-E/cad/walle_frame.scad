// ############################################################################
// #  WALL-E FRAME — the two Rev 012 track pods, SIDE BY SIDE, skid steer     #
// #                                                                          #
// #  The pods are BUILT. Every pod number in here is therefore a fixed       #
// #  input, not a choice: carrier plates 168 apart, green plates at |z|      #
// #  94..100, the M12 holes already drilled at pod-local x -168 and -108.    #
// #  This file designs only the thing that does not exist yet — the frame    #
// #  that holds the two pods left and right, carries a battery each side,    #
// #  and stops the robot pitching onto its face.                            #
// #                                                                          #
// #  AXES (same as the pod model, so a pod drops straight in):               #
// #    x = fore/aft, +x FORWARD        y = up, GROUND AT y=0                 #
// #    z = left/right                                                        #
// #                                                                          #
// #  openscad -o walle.stl -D 'render_mode="assembly"' walle_frame.scad      #
// ############################################################################

render_mode = "assembly";   // [assembly, frame, section, plates, robot, head, shelf]
// assembly — pods, frame, batteries, anti-tip wheels, body envelope ghost
// frame    — the steel only, for welding
// section  — cut on the centre plane, to see how the batteries sit
// plates   — the plywood battery box laid flat, for cutting / DXF
// robot    — the WHOLE thing: frame, body shell, neck, head. Proportion check
// head     — the head alone: eye barrels, screens, sun shade
// shelf    — the electronics shelf, laid out, to check everything fits

show_body_ghost = true;     // the body envelope, as a transparent block
show_batteries  = true;
show_pods       = true;
show_ground     = true;     // set false for PNG renders, or it fills the frame
shelf_labels    = false;    // part names on the shelf. On for the shelf render
png_up          = false;    // true only for PNG renders — see the note at the bottom

// ============================================================================
//  1. POD FACTS — MEASURED / BUILT. Do not "improve" these.
// ============================================================================
// Straight from apollo_track_pod_rev012.scad. Re-measure the first three on the
// real pods before cutting steel; everything in this file hangs off them.
pod_gp_zi   = 94;    // green plate INNER face, pod-local |z| (= carrier outer face)
pod_gp_t    = 6;     // green plate thickness -> OUTER face at 100, the pod's widest point
pod_gp_yc   = 227;   // green plate band centre, above the GROUND (hub 216 + gp_yc 11)
pod_gp_w    = 60;    // green plate band height -> 197 .. 257 above ground
pod_hub_h   = 216;   // hub axle height above ground
pod_halfl   = 181.6; // pod half length  -> 363 overall
pod_top     = 327;   // belt crown height
pod_belt_w  = 118;   // belt width
pod_A       = 231.2; // idler axle centres = GROUND CONTACT LENGTH
pod_idler_d = 108;   // idler wheel OD
pod_B       = 150;   // hub centre above the idler axle line
pod_T       = 12;    // belt carcass thickness
pod_pitch_r = 105.04;// sprocket cord radius

// The M12 holes in the green plates. ALREADY DRILLED, pod-local x, both plates.
// They sit 108..168 FORWARD of the hub, because Rev 012 ran its rails forward
// from the pod. We are stuck with them — see the note at guard "joint offset".
pod_bolt_x  = [-168, -108];
pod_bolt_d  = 12;    // M12 10.9

// ============================================================================
//  2. THE CHOICES — this is what this file actually decides
// ============================================================================
pod_cl      = 500;   // POD CENTRE TO CENTRE, left to right. Owner, 2026-09-16.
                     // Overall width = pod_cl + 200 (the green plates stick out
                     // 100 each side). 500 -> 700 wide, good WALL-E proportion.

// -- rails: box tube, running fore/aft, bolted to the INBOARD green plates ----
fr_h        = 60;    // rail height, y. 60 matches the green plate band exactly
fr_w        = 30;    // rail thickness, z
fr_t        = 3;     // wall
rail_x0     = -275;  // rail front end
rail_len    = 550;   // -> rear end at +275, symmetric about the ground contact

// -- the battery box: plywood, slung between the rails ------------------------
tray_t      = 12;    // plywood
tray_y0     = 150;   // box UNDERSIDE above ground = the robot's lowest point
batt_l      = 400;   // pack, measured
batt_w      = 110;
batt_h      = 80;
batt_upright = true; // true  = pack on its side: 80 wide, 110 tall  <- DEFAULT
                     // false = pack flat:        110 wide, 80 tall
                     // Upright wins because the plywood box walls eat 24 mm of
                     // the clear width. Flat leaves almost nothing. The cost is
                     // about 15 mm of extra centre-of-mass height, which is
                     // nothing next to the body. Guards below check both.
batt_gap_z  = 24;    // gap between the two packs, for straps and wiring
bolt_access_d = 30;  // hole in the box side wall to get a spanner on each M12

// -- anti-tip wheels ---------------------------------------------------------
// The whole reason these exist: the pods put only 231 mm of track on the
// ground, so that is the robot's ENTIRE fore/aft footprint. See 00-plan.md D6.
// Set them CLEAR of the ground. They must never touch in normal driving, or
// they fight the pods' +30/-29 mm of suspension travel.
at_x        = 280;   // castor centre, fore and aft of the ground contact centre
at_clear    = 35;    // how far the castor sits ABOVE the ground at rest
at_d        = 75;    // castor wheel diameter

// -- electronics -------------------------------------------------------------
// Owner decision 2026-09-16: the frame stays 550 long, so there is NO room for
// electronics inside it — the interior is all battery. Everything therefore
// lives on a shelf inside the body. The cost of that choice is thermal: the
// VESCs lose the steel rail as a heatsink, so they get an aluminium plate that
// bolts through to a body side panel. See the VESC HEAT guard below.
shelf_t     = 12;    // plywood electronics shelf
shelf_marg  = 25;    // keep-out round the shelf edge, for cable runs

// real part sizes [length x, width z, height y], mm
vesc_d      = [85, 65, 30];    // Flipsky 75100 class, one per pod
jet_d       = [103, 90, 50];   // Jetson Orin Nano dev kit + cooler
teensy_d    = [60, 40, 25];    // Teensy 4.1 in a small sealed box
cont_d      = [60, 50, 70];    // main contactor
// A real 100 W isolated 48->12 V brick is much bigger than it feels like it
// should be: a Mean Well SD-100C-12 is 159 x 97 x 38. Placeholder guesses were
// half that, which would have made the shelf layout a lie.
dcdc_d      = [159, 97, 38];   // isolated 48 V -> 12 V, 100 W, electronics rail
amp_ps_d    = [120, 70, 35];   // 48 V -> 32 V buck, amplifier only. See
                               //   docs/04-power-and-wiring.md section 4: the
                               //   amp CANNOT run off a full 54.6 V pack.
fuse_d      = [80, 50, 40];    // fuse / distribution block
amp_d       = [120, 80, 40];   // audio amplifier
vesc_hs_t   = 6;     // aluminium heatsink plate under each VESC

// -- body --------------------------------------------------------------------
// Two proportion rules, both taken from the film:
//  - narrower than the 700 mm track span, so the pods stay proud at the sides
//  - WIDER THAN IT IS DEEP. WALL-E is a wide, shallow box, not a cube. A body
//    sized to cover the anti-tip castors (665 long) looks like a packing crate
//    on toy wheels, so body_l is driven by the POD length instead and the
//    castor arms are left showing as little outriggers.
body_w      = 620;
body_l      = 430;   // pod is 363 long — this overhangs it by 33 each end
body_h      = 400;
body_wall   = 12;    // thin ply skin over a foam core
body_gap    = 8;     // body floor clearance over the pod belt crown
chest_d     = 20;    // how deep the front chest panel is recessed
chest_marg  = 55;    // border round the chest panel

// -- head --------------------------------------------------------------------
neck_h      = 70;    // fixed for now. A real neck telescopes — out of scope
neck_d      = 90;
eye_d       = 105;   // eye barrel outside diameter
eye_len     = 150;
eye_cl      = 128;   // barrel centre to centre. Driven by the toe-in: the
                     //   barrels swing TOWARDS each other at the mouth, so
                     //   this has to be bigger than eye_d or they collide.
eye_toe     = 6;     // degrees each barrel toes INWARD. WALL-E's eyes are not
                     //   parallel, and this one number does most of the "it
                     //   looks like him" work.
// Screen choice is tied to the Face board. An ESP32-S3 drives a 2.1 inch
// 480x480 round LCD over QSPI, and that part is cheap and definitely buyable.
// Bigger round screens (3.4 / 4 inch) are DSI, which needs a Raspberry Pi —
// a FOURTH computer, which is not worth it. So the screen stays small and the
// clear dome does the work of making the eye look big.
scr_d       = 53;    // 2.1 inch round LCD, active area diameter
scr_recess  = 60;    // how deep the screen sits inside the barrel. This is the
                     //   SUN SHADE — see the SUN guard. Midburn is the Negev.
dome_t      = 3;     // clear acrylic dome over the barrel mouth. Two jobs:
                     //   it seals the barrel against dust, and the highlight
                     //   on it reads as a big glassy eye.

// ============================================================================
//  3. MASS ESTIMATES — every one of these is a guess. Replace with scale
//     readings as parts get built. The tipping guard is only as good as these.
// ============================================================================
pod_kg      = 15;    // GUESS per pod: hub motor + belt + steel + idlers
pod_com_y   = 190;   // GUESS: pod centre of mass height. Low, it is mostly
                     //   belt and hub motor
batt_kg     = 8;     // GUESS per 48 V pack
elec_kg     = 6;     // GUESS: 2 VESCs, Teensy, Jetson, wiring, contactor
body_kg     = 25;    // GUESS: foam + thin ply shell
head_kg     = 5;     // GUESS: head, screens, servos, neck
// body and head heights are now DERIVED from the geometry below, not guessed.
// body_com_frac: the mass sits low in the body, because the shelf, the amp and
// the speakers are all near the floor and the upper walls are foam.
body_com_frac = 0.40;
steel_rho   = 7850;  // kg/m3
ply_rho     = 650;   // kg/m3  birch

// ============================================================================
//  4. DERIVED
// ============================================================================
$fa = 4; $fs = 0.7;

pod_z       = pod_cl/2;                 // each pod's centre plane
pod_gp_zo   = pod_gp_zi + pod_gp_t;     // 100 — pod's widest point, pod-local
width_over  = pod_cl + 2*pod_gp_zo;     // 700 — overall robot width

// the rail's OUTER face lies flat on the inboard green plate's outer face
rail_zo     = pod_z - pod_gp_zo;        // 150
rail_zi     = rail_zo - fr_w;           // 120 — rail inner face
bay_w       = 2*rail_zi;                // 240 — clear width between the rails

fr_bot      = pod_gp_yc - pod_gp_w/2;   // 197 — rail bottom, flush with the plate
fr_top      = fr_bot + fr_h;            // 257 — rail top, flush with the plate
rail_x1     = rail_x0 + rail_len;       // 275
cm_rear_x   = rail_x0 + fr_w/2 + 10;    // cross member centres
cm_front_x  = rail_x1 - fr_w/2 - 10;

// battery box: plywood U hung off the rail inner faces
tray_zi     = rail_zi - tray_t;         // 108 — box inner wall face
tray_clear  = 2*tray_zi;                // 216 — usable width inside the box
tray_floor  = tray_y0 + tray_t;         // 162 — packs stand on this
tray_len    = batt_l + 2*tray_t + 20;   // box outside length

bw          = batt_upright ? batt_h : batt_w;   // pack width in z
bh          = batt_upright ? batt_w : batt_h;   // pack height in y
batt_need   = 2*bw + batt_gap_z;                // width both packs need
batt_z      = (bw + batt_gap_z)/2;              // each pack's centre plane
batt_y1     = tray_floor + bh;                  // pack top
batt_com_y  = tray_floor + bh/2;

deck_y      = max(fr_top, batt_y1) + 8;         // top of the frame-level stack

// -- body and head geometry --------------------------------------------------
// The body floor cannot sit at deck_y, because the pods' belt crown is HIGHER
// than the frame. It has to clear the crown, and the gap between the two is
// bridged by four risers off the rail tops.
pod_crown   = pod_top;                          // 327 — belt crown, the high point
body_y0     = max(pod_crown, deck_y) + body_gap;// body floor
body_y1     = body_y0 + body_h;                 // body top
riser_h     = body_y0 - fr_top;                 // riser length, rail top to floor
shelf_y     = body_y0 + body_wall;              // electronics stand on this
body_com_y  = body_y0 + body_h*body_com_frac;
// the castor arms stick out past the body by this much, each end
at_proud    = (at_x + at_d/2) - body_l/2;

neck_y0     = body_y1;
head_yc     = body_y1 + neck_h + eye_d/2;       // head centre height
head_com_y  = head_yc;
head_w      = eye_cl + eye_d;                   // overall head width
// toe-in swings each mouth inward by half the barrel length times sin(toe), so
// the mouths end up CLOSER than eye_cl. This is the number that has to clear.
eye_mouth_cl = eye_cl - eye_len*sin(eye_toe);
robot_h     = head_yc + eye_d/2;                // top of the robot

// Sun shade: a screen sunk scr_recess deep behind an aperture scr_d wide is in
// shadow whenever the sun sits HIGHER than this elevation angle.
sun_block   = atan(scr_recess/scr_d);

// -- electronics shelf layout ------------------------------------------------
// THREE rows, not two: the body is only 430 deep, so a row can only be about
// 356 long, and the eight boxes do not fit in two rows of that length. The
// shelf is wide (546) and shallow, so rows are cheap and length is not.
// Row 0 is nearest the front, row 2 nearest the back.
shelf_l     = body_l - 2*body_wall - 2*shelf_marg;
shelf_w     = body_w - 2*body_wall - 2*shelf_marg;
// [name, size, row]
shelf_parts = [
  ["VESC L",   vesc_d,   0],   // the two motor controllers share a row so the
  ["VESC R",   vesc_d,   0],   //   pack and phase cables stay short
  ["Jetson",   jet_d,    0],
  ["Contactor",cont_d,   1],
  ["Fuse blk", fuse_d,   1],
  ["Teensy",   teensy_d, 1],
  ["DC-DC 12V",dcdc_d,   2],
  ["Amp PSU",  amp_ps_d, 3],
  ["Amp",      amp_d,    3],
];
shelf_rows  = [0, 1, 2, 3];
shelf_area  = shelf_l * shelf_w;
function add_area(i) = i < 0 ? 0
                     : shelf_parts[i][1][0]*shelf_parts[i][1][1] + add_area(i-1);
parts_area  = add_area(len(shelf_parts) - 1);
shelf_fill  = 100*parts_area/shelf_area;
// tallest part decides the headroom the shelf needs
part_h_max  = max([for (p = shelf_parts) p[1][2]]) + vesc_hs_t;

// pack each row end to end along x, with a 10 mm gap between boxes
function row_parts(r) = [for (p = shelf_parts) if (p[2] == r) p];
function xrun(r, i)   = i == 0 ? 0 : xrun(r, i-1) + row_parts(r)[i-1][1][0] + 10;
function row_len(r)   = xrun(r, len(row_parts(r)) - 1)
                      + row_parts(r)[len(row_parts(r)) - 1][1][0];
function row_dep(r)   = max([for (p = row_parts(r)) p[1][1]]);
// where each row starts in z, measured from the shelf's front edge
function row_z(r)     = r == 0 ? 0 : row_z(r-1) + row_dep(r-1) + 15;
row_max_len = max([for (r = shelf_rows) row_len(r)]);
rows_dep    = row_z(len(shelf_rows)-1) + row_dep(len(shelf_rows)-1);

// -- masses ------------------------------------------------------------------
// box tube cross-section area, m2
fr_area     = (fr_h*fr_w - (fr_h - 2*fr_t)*(fr_w - 2*fr_t)) * 1e-6;
cm_len      = bay_w;                            // cross member length
steel_len   = (2*rail_len + 2*cm_len) * 1e-3;   // m
m_steel     = fr_area * steel_len * steel_rho;
m_tray      = ((tray_len*tray_clear                       // floor
              + 2*tray_len*(fr_top - tray_floor)) * tray_t) * 1e-9 * ply_rho;
m_frame     = m_steel + m_tray + 1.5;           // +1.5 bolts, sleeves, brackets

// -- centre of mass ----------------------------------------------------------
// [mass, x, y] for everything on the robot
mass_items = [
  [2*pod_kg,  0,               pod_com_y  ],
  [m_frame,   (rail_x0 + rail_x1)/2, (fr_bot + fr_top)/2 ],
  [2*batt_kg, 0,               batt_com_y ],
  [elec_kg,   0,               shelf_y + shelf_t + part_h_max/2],
  [body_kg,   0,               body_com_y ],
  [head_kg,   0,               head_com_y ],
];
m_total = [for (i = mass_items) i[0]] == [] ? 0 :
          mass_items[0][0]+mass_items[1][0]+mass_items[2][0]
         +mass_items[3][0]+mass_items[4][0]+mass_items[5][0];
function wsum(k) = mass_items[0][0]*mass_items[0][k] + mass_items[1][0]*mass_items[1][k]
                 + mass_items[2][0]*mass_items[2][k] + mass_items[3][0]*mass_items[3][k]
                 + mass_items[4][0]*mass_items[4][k] + mass_items[5][0]*mass_items[5][k];
com_x = wsum(1)/m_total;
com_y = wsum(2)/m_total;

// -- tipping -----------------------------------------------------------------
// The robot pivots about the edge of the ground contact patch. The patch is
// 231 mm long, centred on x=0, so the edges are at +-115.6.
tip_edge   = pod_A/2;
tip_fwd    = atan((tip_edge - com_x)/com_y);    // deg of pitch before it goes over
tip_aft    = atan((tip_edge + com_x)/com_y);
tip_side   = atan((pod_z + pod_belt_w/2)/com_y);// belt outer edge, both pods as one base
// the anti-tip castor catches the pitch when it reaches the ground
at_lever   = at_x - tip_edge;
at_catch   = asin(at_clear/at_lever);

// -- the pod joint -----------------------------------------------------------
// The bolt pair is 138 mm forward of the ground contact centre, so the vertical
// load arrives at the joint with a lever and the two bolts take it as a couple.
jt_xc      = (pod_bolt_x[0] + pod_bolt_x[1])/2; // -138
jt_span    = abs(pod_bolt_x[1] - pod_bolt_x[0]);// 60
jt_F       = m_total*9.81/2;                    // vertical load per pod
jt_M       = jt_F * abs(jt_xc - com_x);         // N.mm
jt_Fbolt   = jt_M/jt_span;                      // per bolt, tension/compression
jt_Zgp     = pod_gp_t*pod_gp_w*pod_gp_w/6;      // green plate, 60x6 on edge
jt_Irl     = (fr_w*pow(fr_h,3) - (fr_w - 2*fr_t)*pow(fr_h - 2*fr_t,3))/12;
jt_Zrl     = jt_Irl/(fr_h/2);
jt_s_gp    = jt_M/jt_Zgp;
jt_s_rl    = jt_M/jt_Zrl;
bolt_preload = 50000;                           // N, M12 10.9 at ~100 N.m

// ============================================================================
//  5. GEOMETRY
// ============================================================================
c_steel = [0.42,0.45,0.50];
c_ply   = [0.78,0.65,0.45];
c_green = [0.30,0.62,0.38];
c_belt  = [0.13,0.13,0.15];
c_batt  = [0.20,0.32,0.46];
c_at    = [0.55,0.25,0.25];

module beam_x(len, h, w, t){           // box tube along x
  difference(){
    cube([len, h, w]);
    translate([-1, t, t]) cube([len + 2, h - 2*t, w - 2*t]);
  }
}
module beam_z(len, h, w, t){           // box tube along z
  difference(){
    cube([w, h, len]);
    translate([t, t, -1]) cube([w - 2*t, h - 2*t, len + 2]);
  }
}

// ---- one pod, simplified: belt envelope + carrier + green plates ------------
module pod(){
  idler_y = pod_hub_h - pod_B;                    // 66
  // belt envelope — hull of the sprocket circle and the two idler circles
  color(c_belt, 0.55) translate([0,0,-pod_belt_w/2])
    linear_extrude(pod_belt_w) hull(){
      translate([0, pod_hub_h])          circle(r = pod_pitch_r + pod_T);
      translate([ pod_A/2, idler_y])     circle(r = pod_idler_d/2 + pod_T);
      translate([-pod_A/2, idler_y])     circle(r = pod_idler_d/2 + pod_T);
    };
  // carrier plates, |z| 88..94
  color([0.36,0.43,0.56]) for (s = [1,-1]) scale([1,1,s])
    translate([0, 0, pod_gp_zi - 6]) linear_extrude(6)
      hull(){ translate([0, pod_hub_h]) circle(d = 48);
              translate([ pod_A/2, idler_y]) circle(d = 40);
              translate([-pod_A/2, idler_y]) circle(d = 40); };
  // green plates, |z| 94..100, the band the frame bolts to
  color(c_green) for (s = [1,-1]) scale([1,1,s])
    translate([0, 0, pod_gp_zi]) linear_extrude(pod_gp_t)
      difference(){
        translate([-188, pod_gp_yc - pod_gp_w/2]) square([260, pod_gp_w]);
        for (bx = pod_bolt_x) translate([bx, pod_gp_yc]) circle(d = pod_bolt_d + 1);
      };
  // hub
  color([0.25,0.25,0.28]) translate([0, pod_hub_h, -40]) cylinder(h = 80, d = 90);
}

// ---- the frame: 2 rails + 2 cross members ----------------------------------
module frame_steel(){
  color(c_steel){
    // rails, bolt holes bored through both walls
    for (s = [1,-1]) scale([1,1,s]) translate([rail_x0, fr_bot, rail_zi])
      difference(){
        beam_x(rail_len, fr_h, fr_w, fr_t);
        for (bx = pod_bolt_x)
          translate([bx - rail_x0, pod_gp_yc - fr_bot, -1])
            rotate([0,0,0]) translate([0,0,0])
              cylinder(h = fr_w + 2, d = 25);
      }
    // front + rear cross members, between the rail inner faces
    for (cx = [cm_rear_x, cm_front_x])
      translate([cx - fr_w/2, fr_bot, -rail_zi]) beam_z(bay_w, fr_h, fr_w, fr_t);
  }
  // the Ø25 sleeves welded into each rail at the bolt holes, so the bolt does
  // not crush the thin box walls
  color([0.62,0.64,0.68]) for (s = [1,-1]) scale([1,1,s])
    for (bx = pod_bolt_x) translate([bx, pod_gp_yc, rail_zi]) difference(){
      cylinder(h = fr_w, d = 25);
      translate([0,0,-1]) cylinder(h = fr_w + 2, d = 13);
    }
}

// ---- M12s: in from the INBOARD side, through the rail and the green plate,
//      into a nut welded on the green plate's outer face. Axis along z.
//      The head therefore faces the battery bay, which is why the plywood box
//      wall needs an access hole at each bolt — see battery_box().
module pod_bolts(){
  for (s = [1,-1]) scale([1,1,s]) for (bx = pod_bolt_x)
    translate([bx, pod_gp_yc, rail_zi - 12]) {
      color([0.75,0.72,0.55]) cylinder(h = 12 + fr_w + pod_gp_t + 10, d = pod_bolt_d - 0.2);
      color([0.75,0.72,0.55]) cylinder(h = 10, d = 21.9, $fn = 6);      // head
    }
}

// ---- plywood battery box ---------------------------------------------------
// A U hung off the two rail inner faces. It is the battery box AND the floor,
// and it keeps the sand off the packs.
module box_side_2d(){
  difference(){
    square([tray_len, fr_top - tray_y0]);
    // access for the 4 M12 heads — without these you cannot get a spanner on
    // the bolts that hold the pods, so the pods cannot come off
    for (bx = pod_bolt_x)
      translate([bx + tray_len/2, pod_gp_yc - tray_y0]) circle(d = bolt_access_d);
  }
}
module battery_box(){
  color(c_ply, 0.9){
    translate([-tray_len/2, tray_y0, -tray_clear/2 - tray_t])
      cube([tray_len, tray_t, tray_clear + 2*tray_t]);              // floor
    for (s = [1,-1]) scale([1,1,s])
      translate([-tray_len/2, tray_y0, tray_zi])
        linear_extrude(tray_t) box_side_2d();                       // side walls
  }
}

module batteries(){
  color(c_batt) for (s = [1,-1]) scale([1,1,s])
    translate([-batt_l/2, tray_floor, batt_z - bw/2]) cube([batt_l, bh, bw]);
}

// ---- anti-tip castors ------------------------------------------------------
// An L per end, on the centreline: a horizontal arm out from the cross member,
// then a drop to the castor. The castor axle runs LEFT/RIGHT (along z) so the
// wheel rolls fore and aft, which is the direction it has to give way in.
// Nothing here is near the pods — they sit at z +-250, this is all at z +-15.
module anti_tip(){
  for (sx = [1,-1]){
    x_cm  = sx > 0 ? cm_front_x : cm_rear_x;
    x_leg = sx*at_x;
    color(c_steel) translate([min(x_cm, x_leg), fr_bot, -15])
      cube([abs(x_leg - x_cm) + 15, 30, 30]);                        // arm
    color(c_steel) translate([x_leg - 15, at_clear + at_d/2, -15])
      cube([30, fr_bot - at_clear - at_d/2, 30]);                    // drop
    color(c_at) translate([x_leg, at_clear + at_d/2, 0])
      cylinder(h = 26, d = at_d, center = true);                     // castor
  }
}

// body_l is driven BY the castors, not chosen: the body has to reach past them
// or they stick out in front of WALL-E's face. See the derived section.
module body_ghost(){
  color([0.85,0.72,0.35], 0.12)
    translate([-body_l/2, body_y0, -body_w/2])
      cube([body_l, body_h, body_w]);
}

// ---- risers: rail top up to the body floor, over the pod belt crown --------
module risers(){
  for (sx = [-1,1]) for (sz = [-1,1])
    color(c_steel)
      translate([sx*(rail_x1 - 40) - 15, fr_top, sz*(rail_zo - fr_w/2) - 15])
        cube([30, riser_h, 30]);
}

// ---- the body shell --------------------------------------------------------
module body_shell(){
  color([0.78,0.66,0.34], 0.55)
  difference(){
    translate([-body_l/2, body_y0, -body_w/2]) cube([body_l, body_h, body_w]);
    // hollow it out, leaving the skin. Open at the top: that is the lid, and
    // it is how you reach the shelf.
    translate([-body_l/2 + body_wall, body_y0 + body_wall, -body_w/2 + body_wall])
      cube([body_l - 2*body_wall, body_h, body_w - 2*body_wall]);
    // the chest panel, recessed into the front face
    translate([body_l/2 - chest_d, body_y0 + chest_marg, -body_w/2 + chest_marg])
      cube([chest_d + 1, body_h - 2*chest_marg, body_w - 2*chest_marg]);
  }
  // the electronics shelf
  color(c_ply)
    translate([-shelf_l/2, shelf_y, -shelf_w/2]) cube([shelf_l, shelf_t, shelf_w]);
}

// ---- electronics on the shelf ---------------------------------------------
// Laid out in two rows so every box can be reached from the front or the back.
module shelf_layout(){
  for (row = shelf_rows)
    for (i = [0 : len(row_parts(row)) - 1])
      // each row is centred on the shelf in x, and the block of rows is
      // centred in z, so the load sits over the middle of the frame
      let(p  = row_parts(row)[i],
          d  = p[1],
          vesc = p[0][0] == "V",
          zc = rows_dep/2 - row_z(row) - d[1])
      translate([-row_len(row)/2 + xrun(row, i), shelf_y + shelf_t, zc]){
        // a VESC gets an aluminium heatsink plate under it, because on this
        // shelf it has no steel to dump heat into
        if (vesc) color([0.75,0.78,0.80])
          translate([-8, 0, -8]) cube([d[0] + 16, vesc_hs_t, d[1] + 16]);
        // NOTE the reorder: the part arrays are [length x, width z, height y]
        // to match how datasheets quote them, but cube() wants [x, y, z].
        color(vesc ? [0.25,0.30,0.38] : [0.20,0.22,0.25])
          translate([0, vesc ? vesc_hs_t : 0, 0]) cube([d[0], d[2], d[1]]);
        // labels lie flat on top of each box, the right way up for the
        // top-down shelf render
        if (shelf_labels)
          color([0.05,0.05,0.05])
            translate([d[0]/2, d[2] + vesc_hs_t + 1, d[1]/2])
              rotate([-90,0,0])
                linear_extrude(1) text(p[0], size = 9, halign = "center",
                                       valign = "center");
      }
}

// ---- neck and head --------------------------------------------------------
module eye_barrel(){
  color([0.72,0.62,0.32])
  difference(){
    // barrel: a plain tube, axis along x, mouth facing forward
    rotate([0,90,0]) cylinder(h = eye_len, d = eye_d, center = true);
    // the screen well, bored in from the mouth. Its depth IS the sun shade.
    translate([eye_len/2 - scr_recess, 0, 0])
      rotate([0,90,0]) cylinder(h = scr_recess + 1, d = scr_d + 6, center = false);
    // a cable and servo pocket in the back half
    translate([-eye_len/2 - 1, 0, 0])
      rotate([0,90,0]) cylinder(h = eye_len/2, d = eye_d - 24, center = false);
  }
  // the screen itself, sunk at the bottom of the well
  color([0.10,0.45,0.95])
    translate([eye_len/2 - scr_recess, 0, 0])
      rotate([0,90,0]) cylinder(h = 3, d = scr_d, center = false);
  // the clear dome across the mouth — dust seal, and the highlight on it is
  // what makes a 53 mm screen read as a big glassy eye
  color([0.75,0.90,1.00], 0.45)
    translate([eye_len/2 - dome_t, 0, 0])
      rotate([0,90,0]) cylinder(h = dome_t, d = eye_d - 6, center = false);
}

module head(){
  // neck
  color(c_steel)
    translate([0, neck_y0, 0]) rotate([-90,0,0]) cylinder(h = neck_h, d = neck_d);
  // yoke joining the two barrels
  color([0.60,0.52,0.28])
    translate([-25, head_yc - 20, -eye_cl/2]) cube([50, 40, eye_cl]);
  // each barrel toes inward, so the eyes converge slightly in front of him
  for (sz = [-1,1])
    translate([0, head_yc, sz*eye_cl/2])
      rotate([0, sz*eye_toe, 0]) eye_barrel();
}

// ============================================================================
//  6. RENDER
// ============================================================================
module ground(){
  if (show_ground)
    color([0.80,0.73,0.60]) translate([-480, -6, -430]) cube([960, 6, 860]);
}

module robot(){
  ground();
  if (show_pods) for (s = [1,-1]) translate([0, 0, s*pod_z]) pod();
  frame_steel();
  pod_bolts();
  battery_box();
  if (show_batteries) batteries();
  anti_tip();
  risers();
  if (show_body_ghost) body_ghost();
}

// the whole robot, with the shell and head on rather than the ghost
module robot_full(){
  ground();
  if (show_pods) for (s = [1,-1]) translate([0, 0, s*pod_z]) pod();
  frame_steel();
  pod_bolts();
  battery_box();
  if (show_batteries) batteries();
  anti_tip();
  risers();
  body_shell();
  shelf_layout();
  head();
}

module scene(){
if (render_mode == "assembly")      robot();
else if (render_mode == "frame")  { ground(); frame_steel(); pod_bolts(); anti_tip(); risers(); }
else if (render_mode == "robot")    robot_full();
else if (render_mode == "head")     head();
else if (render_mode == "shelf")  { color(c_ply) translate([-shelf_l/2, shelf_y, -shelf_w/2])
                                      cube([shelf_l, shelf_t, shelf_w]);
                                    shelf_layout(); }
else if (render_mode == "section")  difference(){ robot_full(); translate([-800,-50,0]) cube([1600,1400,800]); }
else if (render_mode == "plates"){
  // the plywood box, laid flat for cutting
  color(c_ply) translate([0,0,0])           square([tray_len, tray_clear + 2*tray_t]);
  color(c_ply) translate([0, tray_clear + 2*tray_t + 20, 0])            box_side_2d();
  color(c_ply) translate([0, tray_clear + 2*tray_t + 40 + (fr_top - tray_y0), 0])
                                                                        box_side_2d();
}
}

// This model is Y-up, like the pod model it has to mate with. OpenSCAD's
// command-line camera assumes Z-up, so PNG renders come out lying on their
// side. png_up=true rotates the scene for rendering only — it does not touch
// the geometry, the STL, or any number above.
if (png_up) rotate([90,0,0]) scene(); else scene();

// ============================================================================
//  7. NUMBERS — always printed
// ============================================================================
echo("");
echo("=========== WALL-E FRAME — TWO REV 012 PODS, SIDE BY SIDE, SKID STEER ===========");
echo(str("LAYOUT:   pods ", pod_cl, " apart centre to centre -> ", width_over,
         " mm OVERALL WIDTH · ground contact ", pod_A, " x ", pod_belt_w,
         " per pod, TOTAL FOOTPRINT ", pod_A, " long x ", pod_cl + pod_belt_w, " wide"));
echo(str("FRAME:    rails ", fr_h, "x", fr_w, "x", fr_t, " box, ", rail_len,
         " long, outer faces ", 2*rail_zo, " apart, ", bay_w, " clear inside · ",
         "rails ", fr_bot, "..", fr_top, " above ground, flush with the green plates"));
echo(str("BATTERY:  pack ", batt_l, "x", batt_w, "x", batt_h, " — ",
         batt_upright ? "UPRIGHT (80 wide, 110 tall)" : "FLAT (110 wide, 80 tall)",
         " · box floor ", tray_floor, ", pack top ", batt_y1,
         " · LOWEST POINT OF THE ROBOT ", tray_y0, " above ground"));
echo(str("DECK:     frame-level stack tops out at ", deck_y,
         " · but the pod BELT CROWN is higher, at ", pod_crown,
         ", so the body floor has to clear THAT"));
echo(str("BODY:     floor ", body_y0, " (", body_gap, " over the crown), top ",
         body_y1, " · ", body_l, " long x ", body_w, " wide x ", body_h,
         " tall · risers ", round(riser_h), " tall, rail top to floor",
         " · anti-tip arms show ", round(at_proud), " past each end, BY DESIGN"));
echo(str("HEAD:     neck ", neck_h, " tall from ", neck_y0,
         " · head centre ", round(head_yc), ", ", head_w, " wide (", eye_d,
         " barrels, ", eye_cl, " apart) · ROBOT HEIGHT ", round(robot_h), " mm"));
echo(str("EYES:     ", scr_d, " mm screen in a ", eye_d,
         " mm barrel = ", round(100*scr_d/eye_d), "% of the barrel filled",
         " · sunk ", scr_recess, " deep, so SUN ABOVE ", round(sun_block),
         " deg ELEVATION IS SHADED (Negev midday is 75-80 deg, so it is shaded)"));
echo(str("SHELF:    ", round(shelf_l), " x ", round(shelf_w), " at ", shelf_y,
         ", tallest box ", part_h_max, " tall · ", len(shelf_rows),
         " rows, longest ", round(row_max_len), ", ", round(rows_dep),
         " deep in total · ", round(shelf_fill),
         "% of the shelf area used"));

echo("");
echo(str("MASS:     steel ", round(m_steel*10)/10, " kg · plywood box ",
         round(m_tray*10)/10, " kg -> FRAME ", round(m_frame*10)/10,
         " kg  ·  WHOLE ROBOT ", round(m_total*10)/10,
         " kg (pods ", 2*pod_kg, " · batteries ", 2*batt_kg, " · electronics ",
         elec_kg, " · body ", body_kg, " · head ", head_kg, ") — ALL GUESSES"));
echo(str("CoM:      x ", round(com_x*10)/10, " (0 = over the middle of the tracks)",
         "  ·  y ", round(com_y*10)/10, " above ground"));
// contact area in cm2 = both patches in mm2 / 100
gnd_area = 2*pod_A*pod_belt_w/100;
echo(str("GROUND PRESSURE: ", round(m_total/gnd_area*1000)/1000,
         " kg/cm2 over ", round(gnd_area), " cm2 — a walking person is about 0.5,",
         " so it presses the sand a third as hard as you do"));

echo("");
echo("--- TIPPING: the whole reason the anti-tip wheels exist -------------------");
echo(str("  pitch FORWARD before it goes over: ", round(tip_fwd*10)/10, " deg"));
echo(str("  pitch BACKWARD before it goes over: ", round(tip_aft*10)/10, " deg"));
echo(str("  ROLL sideways before it goes over:  ", round(tip_side*10)/10,
         " deg — sideways is never the problem, the pods are 700 apart"));
echo(str("  anti-tip castor catches the pitch at: ", round(at_catch*10)/10,
         " deg (", at_x, " out, ", at_clear, " clear, lever ", round(at_lever), ")"));

echo("");
echo("--- THE POD JOINT --------------------------------------------------------");
echo(str("  the 2 M12 holes are ALREADY DRILLED at pod-local x ", pod_bolt_x,
         ", centroid ", jt_xc, ", span ", jt_span));
echo(str("  load per pod ", round(jt_F), " N, arriving ", round(abs(jt_xc - com_x)),
         " mm forward of the ground contact centre -> moment ", round(jt_M/1000), " N.m"));

guards = [
  // [name, actual, minimum, unit]
  ["battery width: both packs inside the plywood box", tray_clear - batt_need, 15],
  ["battery height: pack top below the body floor",    deck_y - batt_y1, 5],
  ["battery length inside the box",                    tray_len - 2*tray_t - batt_l, 10],
  ["box floor above the ground (obstacle clearance)",  tray_y0, 120],
  ["rail inner face to the belt edge, per side",       rail_zi - pod_belt_w/2, 20],
  ["rail outer face sits ON the green plate (must be 0)", -abs(rail_zo - (pod_z - pod_gp_zo)), -0.01],
  ["front bolt to the green plate's front end",        (pod_bolt_x[0] - (-188)) - 1.5*(pod_bolt_d + 1), 0],
  ["both bolts land within the rail",                  min(pod_bolt_x[0] - rail_x0, rail_x1 - pod_bolt_x[1]), 40],
  ["anti-tip catches BEFORE the robot tips forward",   tip_fwd - at_catch, 4],
  // at_clear MUST exceed the pods' bump travel, or the castor takes load on
  // every bump and fights the suspension. That fights wanting it small, so it
  // catches the pitch early. This pair of guards is the whole trade-off.
  ["anti-tip clear of the ground at full bump (+30.7)", at_clear - 30.7, 3],
  // the body floor must clear the pod BELT CROWN, not the frame. Get this
  // wrong and the shell grinds on a moving belt.
  ["body floor clears the pod belt crown",             body_y0 - pod_crown, 6],
  ["body floor clears the battery pack tops",          body_y0 - batt_y1, 5],
  ["body narrower than the track span, pods stay proud", width_over - body_w, 40],
  ["body WIDER than it is deep (WALL-E proportion)",   body_w - body_l, 100],
  ["body covers the pod length",                       body_l - 2*pod_halfl, 30],
  // the castor arms now stick out past the body on purpose. Check they are
  // outriggers, not a trip hazard reaching half a metre into the crowd.
  ["castor arms not sticking out too far",             120 - at_proud, 0],
  ["head narrower than the body (WALL-E proportion)",  body_w - head_w, 200],
  ["longest electronics row fits the shelf",           shelf_l - row_max_len, 40],
  ["all electronics rows fit the shelf depth",         shelf_w - rows_dep, 60],
  ["headroom over the tallest box, under the body top", body_y1 - (shelf_y + shelf_t + part_h_max), 100],
  ["eye screen fills enough of the barrel (%)",        100*scr_d/eye_d, 45],
  ["eye barrel MOUTHS do not collide when toed in",    eye_mouth_cl - eye_d, 4],
  ["screen shaded from the midday sun (deg elevation)", 75 - sun_block, 0],
  ["bolt access hole above the box floor",             (pod_gp_yc - bolt_access_d/2) - tray_floor, 10],
  ["bolt access hole below the box top edge",          fr_top - (pod_gp_yc + bolt_access_d/2), 5],
  ["bolt access holes inside the box length",          tray_len/2 - abs(pod_bolt_x[0]) - bolt_access_d/2, 10],
  ["CoM within the footprint, fore/aft",               tip_edge - abs(com_x) - 40, 0],
  ["green plate bending at the joint (MPa under 235)", 235 - jt_s_gp, 100],
  ["rail bending at the joint (MPa under 235)",        235 - jt_s_rl, 100],
  ["M12 bolt load vs preload (N of margin)",           bolt_preload - jt_Fbolt, 10000],
];
echo("");
echo("--- GUARDS ---------------------------------------------------------------");
for (g = guards)
  echo(str(g[1] < g[2] ? "*** WARN " : "PASS ", g[0], ": ", round(g[1]*10)/10));

echo("");
echo(str("STRESS:   green plate at the joint ", round(jt_s_gp*10)/10,
         " MPa · rail at the joint ", round(jt_s_rl*10)/10,
         " MPa · per M12 ", round(jt_Fbolt), " N of ", bolt_preload, " preload"));

echo("");
echo("--- CUT LIST -------------------------------------------------------------");
echo(str("  ", fr_h, "x", fr_w, "x", fr_t, " box  rails               2 x ", rail_len));
echo(str("  ", fr_h, "x", fr_w, "x", fr_t, " box  cross members       2 x ", cm_len,
         "   -> ", 2*rail_len + 2*cm_len, " mm of box tube total"));
echo(str("    each rail: 2 holes Ø25 through BOTH walls at ",
         pod_bolt_x[0] - rail_x0, " and ", pod_bolt_x[1] - rail_x0,
         " mm from the rail's FRONT end, ", pod_gp_yc - fr_bot,
         " mm up from the rail's bottom; weld a Ø25xØ13x", fr_w, " sleeve in each"));
echo(str("  ", tray_t, " mm plywood  box floor        1 x ", tray_len, " x ", tray_clear + 2*tray_t));
echo(str("  ", tray_t, " mm plywood  box side walls   2 x ", tray_len, " x ", fr_top - tray_y0,
         ", each with 2 holes Ø", bolt_access_d, " at ",
         pod_bolt_x[0] + tray_len/2, " and ", pod_bolt_x[1] + tray_len/2,
         " mm from the FRONT edge, ", pod_gp_yc - tray_y0, " mm up (M12 spanner access)"));
echo(str("  anti-tip legs  30x30 box  2 x ", round(fr_bot - at_clear - at_d),
         " + 2 fore/aft ties · castors 2 x Ø", at_d));
echo(str("  M12 10.9 bolts 4 off, through the rail into the nut welded on the ",
         "green plate — THE POD COMES OFF WITH 2 BOLTS PER SIDE"));

echo("");
echo("--- STILL GUESSES: replace with real numbers ------------------------------");
echo(str("  pod_kg ", pod_kg, " · pod_com_y ", pod_com_y, " · batt_kg ", batt_kg,
         " · elec_kg ", elec_kg, " · body_kg ", body_kg, " · body_com_y ", body_com_y,
         " · head_kg ", head_kg, " · head_com_y ", head_com_y));
echo("  The tipping numbers above are only as good as these. Weigh things.");
