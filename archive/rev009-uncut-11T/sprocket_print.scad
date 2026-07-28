// ============================================================================
//  APOLLO TRACK POD — PRINT-READY DRIVE SPROCKET (wheel-hub clamp shells)
//  Companion to apollo_track_pod.scad — generates the actual 3D-printable
//  part for BOTH final revisions:
//
//    rev = 10  (design of record, archive/rev010-cut-rim-10T-final):
//              10T on the CUT rim — flange walls ground off, the print is a
//              3 mm clamp shell around the bare Ø149 x 20.5 tunnel floor,
//              rib 18 x 15 (top Ø179), 10 T-teeth, cord Ø191.
//    rev = 9   (no-cut twin, archive/rev009-uncut-11T):
//              11T on the FACTORY rim — the print FILLS the tire well
//              (Ø149 floor x 20.5, flush to the Ø165 rim body), rib 18 x
//              16.5 (top Ø198.1), 11 T-teeth, cord Ø210.1.
//
//  WHAT THIS FILE ADDS over the assembly model (which draws rib+teeth only):
//   - the clamp shell / well fill that actually grips the drum
//   - the split into two HALF-SHELLS (the uncut Rev 9 rim flanges make a
//     one-piece ring impossible to install; Rev 10 needs the clamp force)
//   - an under-floor bolt ring on the NON-FIN side (the hub's 5 fins arch
//     on the brake-disc side only): the halves bolt to each other through
//     the open space between the fins, per the blueprint's clamp concept.
//     Ring stays inside the lug-tip sweep (Ø149 rev10 / Ø168.1 rev9) and
//     3 mm clear of the Ø123 motor casing — see guard echoes each render.
//   - bore fit clearance (bore_clr) — calibrate with the TEST ARC first
//
//  PIECES (set `piece`, or use the CLI lines below):
//    half_A / half_B  the two bolt-together halves (print axis-vertical)
//    test_arc         2-tooth arc (README pre-print check: bore fit on the
//                     drum + tooth spacing 56.2 mm rev10 / 56.6 mm rev9)
//    both             both halves, exploded 6 mm — visual check only
//
//  CLI EXPORTS (from this folder):
//    for r in 9 10; do for p in half_A half_B test_arc; do
//      openscad -o stl/rev0${r}_${p}.stl -D "rev=${r}" -D "piece=\"${p}\"" sprocket_print.scad
//    done; done
//
//  HARDWARE: rev10 — 2x M4x30 cl.8.8 + nyloc + washers (one per joint line)
//            rev9  — 2x M5x35 cl.8.8 + nyloc + washers
//
//  BEFORE PRINTING (from the rev010 README, still mandatory):
//   - Rev 10: verify floor >= 20 wide and ring wall >= 3 -> grind -> tape
//     circumference must read 468 mm (= Ø149). Send the number first.
//   - Both: print the TEST ARC first; adjust bore_clr until it seats snug.
//   - fin positions are 72.0 deg NOMINAL — verify the bolt bosses (at the
//     split lines) land between fins before committing plastic.
// ============================================================================

rev   = 10;        // [9, 10]
piece = "half_A";  // [half_A, half_B, test_arc, both]

bore_clr = 0.2;    // radial fit clearance on the Ø149 drum seat, per side —
                   // TUNE WITH THE TEST ARC (ABS shrinks ~0.3-0.8%)
joint_gap = 0.25;  // deg trimmed off each half at the split faces (~0.32 mm
                   // at the bore) so the bolts can actually clamp the drum

/* [Shared belt / hub datums — LOCKED, from the rev models] */
belt_pitch = 60;   // belt link pitch
T          = 12;   // belt carcass thickness
lug_h      = 15;   // belt pyramid lug height (tips sweep rib_top - 2*lug_h)
rib_w      = 18;   // centre rib width — rides the 22 mm gap between lug pairs
tooth_t    = 20;   // tooth thickness, circumferential
tooth_span = 51;   // T-tooth width across the belt
tooth_fil  = 5;    // root widening over the rib zone (printed fatigue fillet)
shell_t    = 3;    // clamp-shell skin thickness (rev 10)
casing_d   = 123;  // motor casing OD — MEASURED 2026-07-25
floor_d    = 149;  // factory tunnel-floor Ø (tape check 468 mm)
floor_w    = 20.5; // tunnel-floor width

/* [Per-rev derived] */
teeth    = (rev == 10) ? 10   : 11;
drum_od  = (rev == 10) ? 149  : 165;   // rev10: cut floor; rev9: uncut rim body
drum_w   = (rev == 10) ? 20.5 : 35;    // blade inner faces sit beside this
rim_face = drum_w/2;                   // rim side face |z|
rib_h    = (teeth*belt_pitch/PI - T - drum_od)/2;
rib_top  = drum_od + 2*rib_h;          // belt face Ø (179.0 / 198.1)
blade_r  = drum_od/2 + rib_h - lug_h;  // tooth blade root radius beside the rim
lug_tip_d = rib_top - 2*lug_h;         // belt lug tips sweep this Ø beside teeth

// under-floor bolt ring (non-fin side, -z): between motor casing and lug sweep
ring_in_r  = casing_d/2 + 3;                       // 64.5 -> Ø129 core clearance
ring_out_r = (rev == 10) ? 72.4 : 82;              // Ø144.8 / Ø164 — >=2 mm
                                                   // under the lug-tip sweep
ring_th    = 8;
ring_z0    = -(rim_face + 0.2);                    // registers on the rim face
boss_th    = 12;
bolt_d     = (rev == 10) ? 4.4 : 5.4;              // M4 / M5 clearance
joints     = (rev == 10) ? [18, 198]               // 10T: gaps opposite -> straight split
                         : [180/11, 180];          // 11T (odd): bent split, both
                                                   // lines still through tooth gaps
// rev9 well-fill only: flange pocket cut (steel well walls Ø149->Ø165, 7.25
// wide each side) with 0.4 radial / 0.1 axial clearance
flange_pocket_d = 165.8;

$fa = 2; $fs = 0.4;

// ------------------------------------------------------------------ guards --
echo(str("REV ", rev, ": ", teeth, "T, rib_h ", rib_h, ", belt face Ø", rib_top,
         ", cord Ø", teeth*belt_pitch/PI, ", tooth marks every ",
         PI*rib_top/teeth, " mm (", 360/teeth, " deg)"));
echo(str("GUARD ring-to-lug-sweep: ring OD ", 2*ring_out_r, " vs lug tips Ø",
         lug_tip_d, " -> ", (lug_tip_d - 2*ring_out_r)/2, " mm/side ",
         lug_tip_d - 2*ring_out_r >= 2 ? "PASS" : "FAIL"));
echo(str("GUARD ring-to-casing: ring ID ", 2*ring_in_r, " vs casing Ø", casing_d,
         " -> ", ring_in_r - casing_d/2, " mm ",
         ring_in_r - casing_d/2 >= 2.5 ? "PASS" : "FAIL"));

// -------------------------------------------------------------- primitives --
module wedge(a0, a1){                   // solid pie a0..a1 deg, oversized
  n = max(4, ceil((a1 - a0)/4));
  linear_extrude(height=140, center=true)
    polygon(concat([[0,0]],
      [for (i=[0:n]) 200*[cos(a0 + (a1-a0)*i/n), sin(a0 + (a1-a0)*i/n)]]));
}

module tooth(){                         // identical to the rev models' geometry
  ts = tooth_span/2;  rw = rib_w/2;  t2 = tooth_t/2;  f = tooth_fil;
  translate([drum_od/2 - 1, 0, 0]) rotate([0,90,0])
    linear_extrude(height=rib_h + 1)
      polygon([[-ts,-t2],[-rw,-t2-f],[rw,-t2-f],[ts,-t2],
               [ts, t2],[ rw, t2+f],[-rw, t2+f],[-ts, t2]]);
  for (sd=[1,-1]) translate([blade_r, 0, 0]) rotate([0,90,0])
    linear_extrude(height=lug_h + 0.1)
      polygon([[sd*rim_face, -t2],[sd*ts, -t2],[sd*ts, t2],[sd*rim_face, t2]]);
}

// under-floor ring + per-joint bolt bosses (trimmed to ring_out_r so nothing
// pokes into the belt-lug sweep between tooth stations)
module under_ring(with_bosses=true){
  conn_bot = max(ring_z0 - ring_th, -(tooth_span/2 - 0.1));
  intersection(){
    union(){
      translate([0,0, ring_z0 - ring_th])
        cylinder(h=ring_th, r=ring_out_r);
      if (with_bosses) for (a=joints) rotate([0,0,a])
        translate([(ring_in_r + ring_out_r)/2, 0, ring_z0 - boss_th/2])
          cube([ring_out_r - ring_in_r, 30, boss_th], center=true);
    }
    cylinder(h=400, r=ring_out_r, center=true);
  }
  // connectors: tie the ring into each tooth's outboard blade (-z side)
  for (i=[0:teeth-1]) rotate([0,0,i*360/teeth])
    translate([(ring_in_r + blade_r + 1.5)/2, 0, (ring_z0 + conn_bot)/2])
      cube([blade_r + 1.5 - ring_in_r, tooth_t, ring_z0 - conn_bot], center=true);
}

module sprocket_solid(with_bosses=true){
  difference(){
    union(){
      // shell (rev10) / well fill flush to the rim body (rev9)
      cylinder(h=floor_w, d=(rev == 10) ? drum_od + 2*shell_t : drum_od,
               center=true);
      cylinder(h=rib_w, d=rib_top, center=true);            // centre rib
      for (i=[0:teeth-1]) rotate([0,0,i*360/teeth]) tooth();
      under_ring(with_bosses);
    }
    // drum seat: the Ø149 floor + fit clearance
    cylinder(h=floor_w + ((rev == 9) ? 0.2 : 0),
             d=floor_d + 2*bore_clr, center=true);
    // rev9: pockets for the steel well walls (flanges), Ø149->Ø165 x 7.25/side
    if (rev == 9) rev9_flange_pockets();
    // core: everything inside Ø129 removed (casing + fins pass through)
    cylinder(h=400, r=ring_in_r, center=true);
    // bolt holes, tangential through each boss pair
    if (with_bosses) for (a=joints) rotate([0,0,a])
      translate([(ring_in_r + ring_out_r)/2, 0, ring_z0 - boss_th/2])
        rotate([90,0,0]) cylinder(h=70, d=bolt_d, center=true);
  }
}

// rev9 well-wall (flange) pockets: steel walls span z 10.25..17.5, Ø149->165;
// cut z 10.15..17.75 at Ø165.8 -> 0.4 radial / 0.1 axial clearance
module rev9_flange_pockets(){
  for (s=[0,1]) mirror([0,0,s])
    translate([0,0,10.15]) cylinder(h=7.6, d=flange_pocket_d);
}

module half(a0, a1){
  intersection(){
    sprocket_solid(true);
    wedge(a0 + joint_gap, a1 - joint_gap);
  }
}

// ------------------------------------------------------------------ render --
if (piece == "half_A"){
  half(joints[0], joints[1]);
} else if (piece == "half_B"){
  half(joints[1], joints[0] + 360);
} else if (piece == "test_arc"){
  // 2 teeth centred, no bolt bosses: checks bore fit + tooth spacing
  intersection(){
    sprocket_solid(false);
    wedge(-180/teeth, 3*180/teeth);
  }
} else {                                 // "both": exploded visual check
  ja = (joints[0] + joints[1])/2;
  translate(6*[cos(ja), sin(ja), 0]) half(joints[0], joints[1]);
  translate(-6*[cos(ja), sin(ja), 0]) half(joints[1], joints[0] + 360);
}
