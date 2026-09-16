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

render_mode = "assembly";   // [assembly, frame, section, plates, robot, head, shelf, chest]
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
show_speakers   = true;
show_ground     = true;     // set false for PNG renders, or it fills the frame
shelf_labels    = false;    // part names on the shelf. On for the shelf render
png_up          = false;    // true only for PNG renders — see the note at the bottom

// ============================================================================
//  1. POD FACTS — MEASURED / BUILT. Do not "improve" these.
// ============================================================================
// These used to be typed out here as twenty-odd constants copied by hand from
// apollo_track_pod_rev012.scad. That is a copy of a measurement, and a copy
// always ends up disagreeing with the original, so they moved to ONE file:
//
//     ../pod_interface.scad
//
// which also records where each number came from and what is still unconfirmed
// about the real pods. To prove it still agrees with the pod model, run:
//
//     openscad -o /dev/null WALL-E/check_pod_interface.scad
//
// It compares all 23 numbers and prints OK or MISMATCH for each. As of
// 2026-09-16 all 23 agree.
include <../pod_interface.scad>

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
rail_x0     = -275;  // rail REAR end. Front is +x on this robot — the chest
                     //   panel, the eye barrels and cm_front_x are all at +x.
                     //   This said "front end" and the cut list echoed hole
                     //   positions "from the FRONT end" while measuring them
                     //   from HERE, which would have put both M12 holes 336 mm
                     //   out of place.
rail_len    = 550;   // -> FRONT end at +275, symmetric about the ground contact

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
                     //   Each one gets a SILICONE BLANKING PLUG. They are
                     //   holes in a sealed box, and they point at the belts.

// -- sealing the box ---------------------------------------------------------
tray_lid_t  = 12;    // plywood lid over the top
batt_pad    = 8;     // closed-cell foam between the packs and the lid. Does two
                     //   jobs: clamps the packs down, and takes the vibration.
gasket_t    = 3;     // closed-cell foam tape under the lid, compressed by the
                     //   lid bolts. This is the actual seal.
lid_bolt_p  = 110;   // lid bolt pitch. Closer than feels necessary, because a
                     //   gasket only seals where it is squeezed.
vent_d      = 12;    // screw-in membrane vent, in the LID, on the centreline.
                     //   A fully sealed box BREATHES as the desert heats and
                     //   cools, and every breath pulls dust through whichever
                     //   leak is worst. A membrane vent gives it a clean path.
                     //   It went in the lid because there is barely any wall
                     //   above the packs — see the guards.

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
body_wall   = 12;    // SOLID plywood, not a skin over foam. Owner 2026-09-17.
body_gap    = 8;     // body floor clearance over the pod belt crown
chest_d     = 20;    // how deep the front chest panel is recessed
chest_marg  = 55;    // border round the chest panel
chest_t     = 12;    // the chest panel itself. It has to BE a panel: chest_d is
                     //   deeper than body_wall, so the recess cuts clean
                     //   through the front wall and leaves a hole. This is the
                     //   plate that sits at the bottom of the recess, and it is
                     //   also the speaker baffle.

// -- speakers ----------------------------------------------------------------
// Two 6.5 inch drivers in the chest, so WALL-E can talk and play music.
// Numbers carried over from the scooter build, where they were measured.
spk_cut_d   = 165;   // the HOLE in the baffle, not the rim
spk_rim_d   = 190;   // the rim that lands on the baffle face
spk_depth   = 50;    // driver depth behind the baffle (MEASURED)
spk_disp    = 0.4;   // litres the driver body itself takes out of the box
spk_edge    = 8;     // cutout edge -> inside face of the enclosure
spk_box_t   = 12;    // enclosure plywood
spk_box_d   = 260;   // how far each enclosure reaches back into the body
spk_zc      = 140;   // driver centres, left and right of the centreline. 155
                     //   left only 5 mm of chest border outboard of the rim
spk_clr     = 20;    // clearance from the enclosure floor to the tallest box
spk_grille  = true;  // draw the grilles. Not optional in a crowd
// Each driver gets its OWN SEALED enclosure. It does not fire into the body.
// Two reasons, and both of them bite. The body is not airtight — it has a
// filtered air intake, a removable lid and cable entries — so an open back
// would chuff and lose all its bass. And 100 W of pressure swinging around the
// electronics bay shakes every connector on the shelf.

// -- head --------------------------------------------------------------------
neck_h      = 70;    // fixed for now. A real neck telescopes — out of scope
neck_d      = 90;
eye_d       = 105;   // eye barrel outside diameter
// The barrels are made of WOOD — owner decision 2026-09-17. Nobody is turning a
// 105 mm tube on a lathe, so each one is a STACK OF PLYWOOD RINGS, cut with a
// hole saw or a router circle jig, glued up, then sanded round on the outside.
// That makes the length a multiple of the sheet thickness rather than a free
// choice: 12 rings of 12 mm is 144, which is why eye_len is not 150 any more.
eye_ring_t  = 12;    // one ply sheet = one ring
eye_rings   = 12;    // how many in the stack
eye_len     = eye_ring_t * eye_rings;           // 144
// The bore changes down the stack, so the rings are not all the same part:
//   front 5 rings  bored Ø59 — the screen well, and the SUN SHADE
//   ring 6         bored Ø53 — the screen lands on this shoulder
//   rear 6 rings   bored Ø81 — cable and servo room
// scr_recess below has to stay on a ring boundary or the screen sits on a
// glue line instead of a shoulder. 60 = 5 rings exactly. Do not nudge it.
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
head_kg     = 5;     // GUESS: head, screens, servos, neck
body_extra  = 3;     // internal framing, hinges, catches, gas strut, paint.
                     //   Sits low, so it gets its own centre of mass below.
spk_drv_kg  = 1.6;   // GUESS: one 6.5 inch driver, magnet and all
steel_rho   = 7850;  // kg/m3
ply_rho     = 650;   // kg/m3  birch

// -- the body is SOLID PLYWOOD now, so stop guessing its weight --------------
// Owner decision 2026-09-17: the body is plywood, not a foam core with a thin
// skin and fibreglass over it. That means its mass is geometry, not a guess,
// so compute it: floor, four walls, and the lid that is also the access hatch.
m_body_floor = body_l * body_w * body_wall;
m_body_lid   = body_l * body_w * body_wall;
m_body_wallz = 2 * body_l * body_h * body_wall;                 // left + right
m_body_wallx = 2 * (body_w - 2*body_wall) * body_h * body_wall; // front + back
m_body_shell = (m_body_floor + m_body_lid + m_body_wallz + m_body_wallx)
               * 1e-9 * ply_rho;
body_kg      = m_body_shell + body_extra;

// body_com_frac: where the body's mass sits, as a fraction of body_h.
// This used to be a flat 0.40, justified by "the upper walls are foam". They
// are not foam any more. For a plywood box the floor and the lid are equal and
// opposite, so the SHELL's centroid is exactly mid-height. Only the extras
// (framing, hinges, the gas strut) sit low. So compute the blend rather than
// assert a number. The speakers are NOT in this figure — they are high and
// forward, and they get their own mass item.
body_shell_frac = 0.50;
body_extra_frac = 0.30;
body_com_frac = (m_body_shell*body_shell_frac + body_extra*body_extra_frac)
                / (m_body_shell + body_extra);

// ============================================================================
//  4. DERIVED
// ============================================================================
$fa = 4; $fs = 0.7;

pod_z       = pod_cl/2;                 // each pod's centre plane
// pod_mount_z comes from ../pod_interface.scad. It is the pod's widest point
// AND the face the rail bolts to — 100 with the green plates fitted, 94
// without them. That question is still open; see the cautions in that file.
width_over  = pod_cl + 2*pod_mount_z;   // 700 — overall robot width

// the rail's OUTER face lies flat on the inboard green plate's outer face
rail_zo     = pod_z - pod_mount_z;      // 150
rail_zi     = rail_zo - fr_w;           // 120 — rail inner face
bay_w       = 2*rail_zi;                // 240 — clear width between the rails

fr_bot      = pod_gp_yc - pod_gp_w/2;   // 197 — rail bottom, flush with the plate
fr_top      = fr_bot + fr_h;            // 257 — rail top, flush with the plate
rail_x1     = rail_x0 + rail_len;       // 275
cm_rear_x   = rail_x0 + fr_w/2 + 10;    // cross member centres
cm_front_x  = rail_x1 - fr_w/2 - 10;

// battery box: a CLOSED plywood box hung off the rail inner faces.
//
// It was a three-sided U — floor and two side walls stopping at the rail top —
// and that was wrong. The box hangs directly inboard of the belts, which throw
// sand inward and upward, and a U is open at the top and at both ends. Owner,
// 2026-09-16: the packs must be in a closed box. So: floor, two sides, two
// ends, and a gasketed lid over the top.
tray_zi     = rail_zi - tray_t;         // 108 — box inner wall face
tray_clear  = 2*tray_zi;                // 216 — usable width inside the box
tray_floor  = tray_y0 + tray_t;         // 162 — packs stand on this
tray_len    = batt_l + 2*tray_t + 20;   // box outside length
tray_in_len = tray_len - 2*tray_t;      // clear length inside, between the ends

bw          = batt_upright ? batt_h : batt_w;   // pack width in z
bh          = batt_upright ? batt_w : batt_h;   // pack height in y
batt_need   = 2*bw + batt_gap_z;                // width both packs need
batt_z      = (bw + batt_gap_z)/2;              // each pack's centre plane
batt_y1     = tray_floor + bh;                  // pack top
batt_com_y  = tray_floor + bh/2;

// the lid, and the foam pad that holds the packs down against it
box_top     = batt_y1 + batt_pad + tray_lid_t;  // top face of the lid
box_wall_h  = box_top - tray_y0;                // how tall the side walls are

deck_y      = max(fr_top, box_top) + 8;         // top of the frame-level stack

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
// Several short rows, not two long ones: the body is only 430 deep, so a row
// runs fore-aft and can only be about 356 long, and the nine boxes do not fit
// in two rows of that length. The rows then stack across the width, where
// there is 546 to play with, so rows are cheap and row LENGTH is not.
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

// -- speakers in the chest ---------------------------------------------------
// The chest panel: a real plate, set back chest_d from the outer face. This is
// the speaker baffle, so its position sets everything else.
chest_x1    = body_l/2 - chest_d;               // 195 — baffle FRONT face
chest_x0    = chest_x1 - chest_t;               // 183 — baffle back face
chest_y0    = body_y0 + chest_marg;             // recess bottom edge
chest_y1    = body_y1 - chest_marg;             // recess top edge
chest_z     = body_w/2 - chest_marg;            // recess half width

// The drivers are NOT placed by eye. Each enclosure has to sit clear above the
// electronics and under the body lid, and the driver centres on what is left.
parts_top   = shelf_y + shelf_t + part_h_max;   // top of the tallest box
spk_box_y0  = parts_top + spk_clr;              // enclosure floor
spk_box_y1  = body_y1 - body_wall - 10;         // enclosure ceiling
spk_box_h   = spk_box_y1 - spk_box_y0;
spk_yc      = (spk_box_y0 + spk_box_y1)/2;      // driver centre height
spk_box_w   = spk_cut_d + 2*spk_edge + 2*spk_box_t;
spk_box_x1  = chest_x0;                         // enclosure front = baffle back
spk_box_x0  = spk_box_x1 - spk_box_d;

// sealed volume behind one driver, in litres
spk_vol     = (spk_box_d - spk_box_t)*(spk_box_h - 2*spk_box_t)
              *(spk_box_w - 2*spk_box_t)/1e6 - spk_disp;
spk_com_x   = (spk_box_x0 + spk_box_x1)/2;      // the pair sits FORWARD of centre

// How much of the shelf the two enclosures sit OVER. They do not touch the
// electronics — there is spk_clr of headroom — but they are above it, so the
// boxes have to come out to reach what is underneath. That is why they bolt to
// the chest panel and are not glued in.
spk_shadow_x = min(spk_box_x1, shelf_l/2) - max(spk_box_x0, -shelf_l/2);
spk_shadow  = 2*spk_shadow_x*spk_box_w;
shelf_reach = 100*(shelf_area - spk_shadow)/shelf_area;

// -- masses ------------------------------------------------------------------
// box tube cross-section area, m2
fr_area     = (fr_h*fr_w - (fr_h - 2*fr_t)*(fr_w - 2*fr_t)) * 1e-6;
cm_len      = bay_w;                            // cross member length
steel_len   = (2*rail_len + 2*cm_len) * 1e-3;   // m
m_steel     = fr_area * steel_len * steel_rho;
// the battery box is now a CLOSED box, so this counts all six panels. It used
// to count a floor and two short walls, and so it under-read.
box_out_w   = tray_clear + 2*tray_t;
m_tray      = (tray_len*box_out_w*tray_t                  // floor
             + tray_len*box_out_w*tray_lid_t              // lid
             + 2*tray_len*box_wall_h*tray_t               // side walls
             + 2*box_out_w*box_wall_h*tray_t              // end walls
              ) * 1e-9 * ply_rho;
m_frame     = m_steel + m_tray + 1.5;           // +1.5 bolts, sleeves, brackets

// one speaker: the driver, plus its enclosure worked out from the geometry
// rather than guessed. The enclosure is open at the front, where the chest
// panel closes it, so one wall's worth of plywood is missing on purpose.
m_spk_box   = (spk_box_d*spk_box_h*spk_box_w
             - (spk_box_d - spk_box_t)*(spk_box_h - 2*spk_box_t)
               *(spk_box_w - 2*spk_box_t)) * 1e-9 * ply_rho;
spk_kg      = spk_drv_kg + m_spk_box;

// -- centre of mass ----------------------------------------------------------
// [mass, x, y] for everything on the robot
mass_items = [
  [2*pod_kg,  0,               pod_com_y  ],
  [m_frame,   (rail_x0 + rail_x1)/2, (fr_bot + fr_top)/2 ],
  [2*batt_kg, 0,               batt_com_y ],
  [elec_kg,   0,               shelf_y + shelf_t + part_h_max/2],
  [body_kg,   0,               body_com_y ],
  [head_kg,   0,               head_com_y ],
  // The speakers are the only mass on the robot that is NOT on the
  // centreline fore/aft. Both of them are in the chest, so they pull com_x
  // forward, which is the direction the robot already tips.
  [2*spk_kg,  spk_com_x,       spk_yc     ],
];
// Summed by recursion, not by hand. The hand-written version had to be edited
// every time an item was added, and that is how a mass gets silently dropped.
function msum(i)      = i < 0 ? 0 : mass_items[i][0] + msum(i-1);
function wsum_i(k, i) = i < 0 ? 0 : mass_items[i][0]*mass_items[i][k] + wsum_i(k, i-1);
m_total = msum(len(mass_items) - 1);
function wsum(k) = wsum_i(k, len(mass_items) - 1);
com_x = wsum(1)/m_total;
com_y = wsum(2)/m_total;

// -- WHAT IF the batteries went in the body instead? -------------------------
// A fair question, and this is the arithmetic that answers it. See the
// BATTERY PLACEMENT echo block and docs/06-why-the-batteries-are-low.md.
//
// Packs would lie flat on the electronics shelf, 80 tall, so their centre of
// mass rises from batt_com_y to here:
bib_com_y   = shelf_y + shelf_t + batt_h/2;
bib_com_all = (wsum(2) - 2*batt_kg*batt_com_y + 2*batt_kg*bib_com_y)/m_total;
bib_tip_fwd = atan((pod_A/2 - com_x)/bib_com_all);
// A pack is 400 long and the shelf is only ~356 deep, so they cannot lie
// fore-aft. They would have to lie ACROSS the robot. Then:
bib_need_x  = 2*batt_w + batt_gap_z;            // 244 of the shelf's length
bib_need_z  = batt_l;                           // 400 of the shelf's width
bib_area    = 100*bib_need_x*bib_need_z/shelf_area;
// and the lowest point of the robot becomes the rail bottom, not the box floor
bib_clear   = fr_bot;

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
    square([tray_len, box_wall_h]);
    // access for the 4 M12 heads — without these you cannot get a spanner on
    // the bolts that hold the pods, so the pods cannot come off. Each one is
    // closed with a silicone blanking plug in service.
    for (bx = pod_bolt_x)
      translate([bx + tray_len/2, pod_gp_yc - tray_y0]) circle(d = bolt_access_d);
  }
}

module box_end_2d(){
  square([tray_clear + 2*tray_t, box_wall_h]);
}

// Lid bolts run all round the edge at lid_bolt_p pitch, because a gasket only
// seals where it is squeezed. n_lid_x per long side, 2 per end.
n_lid_x = max(2, round(tray_len / lid_bolt_p));
module box_lid_2d(){
  w = tray_clear + 2*tray_t;
  difference(){
    square([tray_len, w]);
    for (i = [0:n_lid_x]) for (sz = [0,1])
      translate([6 + i*(tray_len - 12)/n_lid_x, sz ? w - 6 : 6]) circle(d = 5);
    for (sx = [0,1])
      translate([sx ? tray_len - 6 : 6, w/2]) circle(d = 5);
    // The membrane vent goes in the LID, not in a wall. The lid is the most
    // sheltered surface on the box: the body floor sits 43 mm above it, so
    // nothing has a straight path to it. It sits on the centreline, over the
    // gap between the two packs, so the foam pad does not block the airway.
    translate([tray_len/2, w/2]) circle(d = vent_d);
  }
}

module battery_box(){
  color(c_ply, 0.9){
    translate([-tray_len/2, tray_y0, -tray_clear/2 - tray_t])
      cube([tray_len, tray_t, tray_clear + 2*tray_t]);              // floor
    for (s = [1,-1]) scale([1,1,s])
      translate([-tray_len/2, tray_y0, tray_zi])
        linear_extrude(tray_t) box_side_2d();                       // side walls
    // END WALLS. The box was open at both ends, pointing straight at the
    // belts. These are the panels that make it a box.
    for (sx = [1,-1])
      translate([sx*(tray_len/2 - tray_t) - (sx > 0 ? 0 : tray_t),
                 tray_y0, -tray_clear/2 - tray_t])
        cube([tray_t, box_wall_h, tray_clear + 2*tray_t]);
  }
  // the gasket, then the lid
  color([0.15,0.15,0.18])
    translate([-tray_len/2, box_top - tray_lid_t - gasket_t, -tray_clear/2 - tray_t])
      cube([tray_len, gasket_t, tray_clear + 2*tray_t]);
  color(c_ply)
    translate([-tray_len/2, box_top - tray_lid_t, -tray_clear/2 - tray_t])
      cube([tray_len, tray_lid_t, tray_clear + 2*tray_t]);
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
    // the recess in the front face. chest_d is DEEPER than body_wall, so this
    // cuts the front wall away completely over the chest area — which is why
    // the chest panel below has to be a real plate and not just a rebate.
    translate([chest_x1, chest_y0, -chest_z])
      cube([chest_d + 1, chest_y1 - chest_y0, 2*chest_z]);
  }
  chest_panel();
  // the electronics shelf
  color(c_ply)
    translate([-shelf_l/2, shelf_y, -shelf_w/2]) cube([shelf_l, shelf_t, shelf_w]);
}

// ---- the chest panel, which is also the speaker baffle ---------------------
module chest_panel(){
  color([0.70,0.60,0.30])
  difference(){
    translate([chest_x0, chest_y0, -chest_z])
      cube([chest_t, chest_y1 - chest_y0, 2*chest_z]);
    for (sz = [1,-1])
      translate([chest_x0 - 1, spk_yc, sz*spk_zc])
        rotate([0,90,0]) cylinder(h = chest_t + 2, d = spk_cut_d);
  }
}

// ---- speakers --------------------------------------------------------------
// A sealed plywood enclosure per driver, hung off the back of the chest panel.
// See the parameter block for why they are not simply firing into the body.
module speaker_boxes(){
  for (sz = [1,-1]) translate([0, 0, sz*spk_zc])
    color(c_ply, 0.85)
    difference(){
      translate([spk_box_x0, spk_box_y0, -spk_box_w/2])
        cube([spk_box_d, spk_box_h, spk_box_w]);
      // the air space. Open at the front, where the chest panel closes it.
      translate([spk_box_x0 + spk_box_t, spk_box_y0 + spk_box_t,
                 -spk_box_w/2 + spk_box_t])
        cube([spk_box_d, spk_box_h - 2*spk_box_t, spk_box_w - 2*spk_box_t]);
    }
}

module speakers(){
  for (sz = [1,-1]) translate([chest_x1, spk_yc, sz*spk_zc]) rotate([0,90,0]){
    color([0.15,0.15,0.17]) cylinder(h = 4, d = spk_rim_d);          // rim
    color([0.30,0.30,0.33]) translate([0, 0, -spk_depth])
      cylinder(h = spk_depth, d1 = spk_cut_d/3, d2 = spk_cut_d - 4); // basket
    color([0.22,0.22,0.25]) translate([0, 0, -spk_depth])
      cylinder(h = 12, d = spk_cut_d/2.4);                           // magnet
    // Grille. A festival crowd WILL push a finger through an open cone.
    if (spk_grille) color([0.42,0.42,0.45]){
      // an outer ring, then radial bars across it
      difference(){
        translate([0, 0, 4]) cylinder(h = 5, d = spk_rim_d);
        translate([0, 0, 3]) cylinder(h = 7, d = spk_rim_d - 16);
      }
      for (a = [0:30:150]) rotate([0,0,a])
        translate([-spk_rim_d/2, -2, 4]) cube([spk_rim_d, 4, 4]);
    }
  }
}

// ---- electronics on the shelf ---------------------------------------------
// Each row runs FORE AND AFT, and the rows stack ACROSS the robot's width, so
// every box can be reached from above with a hand either side of it.
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
  // Drawn ring by ring rather than as one tube, because that is how it gets
  // built and because the glue lines are the thing you have to cut to. Each
  // ring is one sheet of plywood.
  for (i = [0 : eye_rings - 1]){
    x0   = -eye_len/2 + i*eye_ring_t;           // this ring's back face
    // depth of this ring's FRONT face, measured back from the mouth
    dep  = eye_len - (i + 1)*eye_ring_t;
    bore = dep < scr_recess       ? scr_d + 6   // front rings: the screen well
         : dep < scr_recess + eye_ring_t ? scr_d // the shoulder the screen sits on
         : eye_d - 24;                           // rear rings: cable and servos
    color(c_ply) translate([x0, 0, 0]) difference(){
      rotate([0,90,0]) cylinder(h = eye_ring_t, d = eye_d);
      translate([-1, 0, 0])
        rotate([0,90,0]) cylinder(h = eye_ring_t + 2, d = bore);
    }
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
  if (show_speakers) { speaker_boxes(); speakers(); }
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
else if (render_mode == "chest")  { chest_panel(); speaker_boxes(); speakers(); }
else if (render_mode == "section")  difference(){ robot_full(); translate([-800,-50,0]) cube([1600,1400,800]); }
else if (render_mode == "plates"){
  // every plywood panel of the closed battery box, laid flat for cutting
  bw2 = tray_clear + 2*tray_t;
  color(c_ply)                                   square([tray_len, bw2]);   // floor
  color(c_ply) translate([0, bw2 + 20])          box_lid_2d();              // lid
  color(c_ply) translate([0, 2*bw2 + 40])        box_side_2d();             // side
  color(c_ply) translate([0, 2*bw2 + 60 + box_wall_h])   box_side_2d();     // side
  color(c_ply) translate([0, 2*bw2 + 80 + 2*box_wall_h]) box_end_2d();      // end
  color(c_ply) translate([bw2 + 20, 2*bw2 + 80 + 2*box_wall_h]) box_end_2d();
}
}

// This model is Y-up, like the pod model it has to mate with. OpenSCAD's
// command-line camera assumes Z-up, so PNG renders come out lying on their
// side. png_up=true rotates the scene for rendering only — it does not touch
// the geometry, the STL, or any number above.
// no_render lets ../walle.scad include this file for its numbers and its
// modules without drawing the robot on top of a blueprint sheet. Standalone,
// no_render is undefined and the scene draws as normal.
suppress = is_undef(no_render) ? false : no_render;
if (!suppress) { if (png_up) rotate([90,0,0]) scene(); else scene(); }

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
         " · barrel is ", eye_rings, " x ", eye_ring_t,
         " mm PLY RINGS glued up and sanded round",
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
         elec_kg, " · body ", round(body_kg*10)/10, " · speakers ", round(2*spk_kg*10)/10,
         " · head ", head_kg, ") — ALL GUESSES"));
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
echo("--- SPEAKERS: two 6.5 inch in the chest -----------------------------------");
echo(str("  drivers:   Ø", spk_cut_d, " cutout, Ø", spk_rim_d, " rim, ", spk_depth,
         " deep · centres ", round(spk_yc), " above ground, ", spk_zc,
         " each side of the centreline"));
echo(str("  baffle:    the CHEST PANEL, ", chest_t, " mm ply, set back ", chest_d,
         " from the front face · cut 2 holes Ø", spk_cut_d, " at ",
         spk_zc, " either side of centre, ", round(spk_yc - chest_y0),
         " mm up from the panel's bottom edge"));
echo(str("  enclosure: ", spk_box_d, " deep x ", round(spk_box_h), " tall x ",
         round(spk_box_w), " wide, ", spk_box_t, " mm ply, SEALED, one per driver",
         " -> ", round(spk_vol*10)/10, " litres of air behind each"));
echo(str("  mass:      ", round(spk_kg*10)/10, " kg each (", spk_drv_kg,
         " driver + ", round(m_spk_box*10)/10, " box) = ", round(2*spk_kg*10)/10,
         " kg, and it sits FORWARD: com_x moved to ", round(com_x*10)/10, " mm"));
echo(str("  amplifier: one channel each, 4 Ω. The amp is on the shelf below —",
         " see docs/04-power-and-wiring.md section 4 for why it gets its own",
         " 48->32 V supply"));
echo(str("  SERVICE:   each enclosure sits OVER the shelf with ", spk_clr,
         " mm of headroom, shading ", round(100 - shelf_reach),
         "% of it. BOLT them to the chest panel, do not glue them in — only ",
         round(shelf_reach), "% of the shelf is reachable with them in place"));

echo("");
echo("--- BATTERY PLACEMENT: why they are LOW and not in the body ---------------");
echo(str("  AS BUILT, packs in the frame:  battery CoM ", round(batt_com_y),
         " · robot CoM ", round(com_y*10)/10,
         " · tips forward at ", round(tip_fwd*10)/10, " deg"));
echo(str("  IF MOVED to the body shelf:    battery CoM ", round(bib_com_y),
         " · robot CoM ", round(bib_com_all*10)/10,
         " · tips forward at ", round(bib_tip_fwd*10)/10, " deg"));
echo(str("  COST:    ", round((bib_com_all - com_y)*10)/10,
         " mm higher CoM, ", round((tip_fwd - bib_tip_fwd)*10)/10,
         " deg less tipping margin, and the packs take ", round(bib_area),
         "% of the shelf on top of the ", round(shelf_fill),
         "% the electronics already use = ", round(bib_area + shelf_fill), "%"));
echo(str("  ALSO:    a pack is ", batt_l, " long and the shelf is only ",
         round(shelf_l), " deep, so they could not lie fore-aft at all —",
         " they would have to lie ACROSS the robot"));
echo(str("  GAIN:    ground clearance would go from ", tray_y0, " to ",
         bib_clear, " mm, because the plywood box is the lowest part"));

echo("");
echo("--- THE POD JOINT --------------------------------------------------------");
echo(str("  the 2 M12 holes are ALREADY DRILLED at pod-local x ", pod_bolt_x,
         ", centroid ", jt_xc, ", span ", jt_span));
echo(str("  load per pod ", round(jt_F), " N, arriving ", round(abs(jt_xc - com_x)),
         " mm forward of the ground contact centre -> moment ", round(jt_M/1000), " N.m"));

guards = [
  // [name, actual, minimum, unit]
  ["battery width: both packs inside the plywood box", tray_clear - batt_need, 15],
  ["foam pad between the packs and the lid",           batt_pad, 5],
  ["box lid clears the body floor above it",           body_y0 - box_top, 20],
  ["battery length inside the closed box (end to end)", tray_in_len - batt_l, 10],
  ["box side walls reach ABOVE the packs (sealed top)", box_top - tray_lid_t - batt_y1, 5],
  ["gap between the packs clears the lid vent",         batt_gap_z - vent_d, 8],
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
  // speakers. The chest panel must EXIST, which it did not: chest_d is deeper
  // than body_wall, so the recess cut the front wall clean away.
  ["chest panel is a real plate, not a hole",         chest_t, 6],
  ["speaker rim fits the chest recess, top and bottom", (chest_y1 - chest_y0)/2 - spk_rim_d/2, 20],
  ["speaker rim fits the chest recess, left and right", chest_z - (spk_zc + spk_rim_d/2), 20],
  ["gap between the two speaker rims",                2*spk_zc - spk_rim_d, 30],
  ["speaker cutout fits the enclosure face",          spk_box_h/2 - spk_cut_d/2, 10],
  ["speaker enclosures clear each other",             2*spk_zc - spk_box_w, 20],
  ["enclosures stay inside the body sides",           body_w/2 - body_wall - (spk_zc + spk_box_w/2), 10],
  ["enclosures clear the tallest electronics box",    spk_box_y0 - parts_top, 15],
  ["enclosures clear the body lid",                   body_y1 - body_wall - spk_box_y1, 5],
  ["enclosures do not foul the body back wall",       spk_box_x0 - (-body_l/2 + body_wall), 20],
  ["driver depth fits behind the baffle",             spk_box_d - spk_box_t - spk_depth, 50],
  ["sealed volume per driver, litres (6.5 inch wants 7-14)", spk_vol, 7],
  ["shelf reachable from above without pulling a speaker box (%)", shelf_reach, 35],
  ["screen recess lands on a ring glue line (mm off)",
                                  -abs(scr_recess - round(scr_recess/eye_ring_t)*eye_ring_t), 0],
  ["eye barrel is a whole number of ply sheets (mm off)",
                                  -abs(eye_len - eye_rings*eye_ring_t), 0],
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
         " mm from the rail's REAR end, ", pod_gp_yc - fr_bot,
         " mm up from the rail's bottom; weld a Ø25xØ13x", fr_w, " sleeve in each"));
echo(str("  ", tray_t, " mm plywood  box floor        1 x ", tray_len, " x ", tray_clear + 2*tray_t));
echo(str("  ", tray_t, " mm plywood  box side walls   2 x ", tray_len, " x ", box_wall_h,
         ", each with 2 holes Ø", bolt_access_d, " at ",
         pod_bolt_x[0] + tray_len/2, " and ", pod_bolt_x[1] + tray_len/2,
         " mm from the REAR edge, ", pod_gp_yc - tray_y0,
         " mm up (M12 spanner access — FIT SILICONE PLUGS)"));
echo(str("  ", tray_t, " mm plywood  box END walls    2 x ", tray_clear + 2*tray_t,
         " x ", box_wall_h, "   <- these are what close the box"));
echo(str("  ", tray_lid_t, " mm plywood  box LID       1 x ", tray_len, " x ",
         tray_clear + 2*tray_t, ", ", 2*(n_lid_x + 1) + 2,
         " x M5 round the edge at ", lid_bolt_p, " pitch"));
echo(str("  sealing:  ", gasket_t, " mm closed-cell foam tape under the lid · ",
         batt_pad, " mm foam pad on top of the packs · 4 x Ø", bolt_access_d,
         " silicone blanking plugs · 1 x M", vent_d,
         " screw-in membrane vent in the LID centre, over the gap between the packs"));
echo(str("  anti-tip legs  30x30 box  2 x ", round(fr_bot - at_clear - at_d),
         " + 2 fore/aft ties · castors 2 x Ø", at_d));
echo(str("  ", eye_ring_t, " mm plywood  EYE RINGS   ", 2*eye_rings, " x \u00d8", eye_d,
     " discs: ", 2*5, " bored \u00d8", scr_d + 6, " (screen well), ", 2*1, " bored \u00d8", scr_d,
     " (screen shoulder), ", 2*(eye_rings - 6), " bored \u00d8", eye_d - 24,
     " (cables). Glue each stack of ", eye_rings, ", then sand the OUTSIDE round"));
echo(str("  M12 10.9 bolts 4 off, through the rail into the nut welded on the ",
         "green plate — THE POD COMES OFF WITH 2 BOLTS PER SIDE"));

echo("");
echo("--- STILL GUESSES: replace with real numbers ------------------------------");
echo(str("  pod_kg ", pod_kg, " · pod_com_y ", pod_com_y, " · batt_kg ", batt_kg,
         " · elec_kg ", elec_kg, " · body_kg ", body_kg, " · body_com_y ", body_com_y,
         " · head_kg ", head_kg, " · head_com_y ", head_com_y));
echo("  The tipping numbers above are only as good as these. Weigh things.");
