// ============================================================================
//  WALL-E — THE GLOBAL FILE
// ============================================================================
//
//  One entry point for the whole robot. Everything downstream of here is
//  derived; there are no numbers in this file that are not about drawing.
//
//  WHAT THIS FILE IS FOR
//
//    1. A single command that renders any view of the robot, so you never
//       have to remember which sub-file holds what.
//    2. DIMENSIONED BLUEPRINT SHEETS. Not pretty pictures — drawings with
//       witness lines, arrows and numbers on them, which is what you actually
//       take to a workshop. OpenSCAD has no dimensioning, so section 2 below
//       builds one.
//
//  WHERE THE NUMBERS COME FROM
//
//    pod_interface.scad     the 23 facts about the BUILT pods. Verified
//                           against the pod model; run check_pod_interface.scad
//    cad/walle_frame.scad   everything WALL-E actually decides, plus the guards
//
//  HOW TO USE IT
//
//    ./render_all.sh                      every sheet and every view, in one go
//    openscad walle.scad                  open it and pick a mode in the GUI
//    openscad -o out.png -D 'view="s1"' walle.scad
//
//  THE MODES
//
//    Blueprint sheets, 2D, dimensioned — these are the drawings:
//      s1   General arrangement: front and side, overall sizes
//      s2   Frame weldment: what the welder needs. Steel only, with holes
//      s3   Battery box: all six plywood panels flat, with hole positions
//      s4   Chest panel and speakers: cutout positions
//      s5   Electronics shelf: what sits where
//
//    Solid views, 3D — these are for looking at and for STL export:
//      robot, frame, head, chest, shelf, section, assembly, plates
//
// ============================================================================

// The list in the comment below is what gives you a DROPDOWN in OpenSCAD's
// Customizer panel instead of a plain text box. It has to sit on the same line
// as the assignment, and the values have to match the dispatch at the bottom
// of this file by hand — OpenSCAD cannot read them out of the code.
view = "s1"; // [s1:Sheet 1 general arrangement, s2:Sheet 2 frame weldment, s3:Sheet 3 battery box, s4:Sheet 4 chest panel, s5:Sheet 5 electronics shelf, robot:Whole robot, frame:Steel frame only, section:Cut in half, head:Head only, chest:Chest and speakers, shelf:Electronics shelf]

// Pull in the whole model for its numbers and its modules, but stop it from
// drawing itself on top of our sheets.
no_render = true;
include <walle_frame.scad>

// ============================================================================
//  2. A DIMENSIONING LIBRARY
// ============================================================================
//  OpenSCAD cannot dimension a drawing, so this is the minimum that makes a
//  sheet readable: an extension line off the feature, an arrow at each end,
//  and the number sitting on the line.
//
//  Everything takes a scale `s`. A sheet 3 metres across and a sheet 300 mm
//  across need very different arrow and text sizes, and hard-coding them is
//  what makes drawings unreadable when you change the zoom.
// ============================================================================

lw      = 2.5;    // line weight, in model units, scaled by s
arrow_l = 9;      // arrow length
arrow_w = 3.5;    // arrow half width
txt     = 15;     // text height
gap     = 6;      // witness line does not touch the feature

module bp_line(p0, p1, s = 1){
  d = [p1[0] - p0[0], p1[1] - p0[1]];
  l = sqrt(d[0]*d[0] + d[1]*d[1]);
  if (l > 0.001)
    translate(p0) rotate([0, 0, atan2(d[1], d[0])])
      translate([0, -lw*s/2]) square([l, lw*s]);
}

module bp_arrow(tip, ang, s = 1){
  translate(tip) rotate([0, 0, ang])
    polygon([[0,0], [arrow_l*s, arrow_w*s], [arrow_l*s, -arrow_w*s]]);
}

// horizontal dimension: from x0 to x1, drawn at height y
module dim_h(x0, x1, y, label, s = 1, flip = false){
  bp_line([x0, y], [x1, y], s);
  bp_arrow([x0, y], 0, s);
  bp_arrow([x1, y], 180, s);
  translate([(x0 + x1)/2, y + (flip ? -txt*s*1.6 : txt*s*0.5)])
    text(label, size = txt*s, halign = "center", valign = "baseline");
}

// vertical dimension: from y0 to y1, drawn at x
module dim_v(y0, y1, x, label, s = 1, left = false){
  bp_line([x, y0], [x, y1], s);
  bp_arrow([x, y0], 90, s);
  bp_arrow([x, y1], -90, s);
  translate([x + (left ? -txt*s*0.6 : txt*s*0.6), (y0 + y1)/2])
    rotate([0, 0, 90])
      text(label, size = txt*s, halign = "center",
           valign = left ? "top" : "baseline");
}

// Hollow out an already-2D shape. Note this is ONE module level with two
// children() calls, which works; the three-level version further down does
// not, and the comment there explains why.
module o2(t = 3){
  difference(){ children(); offset(delta = -t) children(); }
}

// a witness line, to carry a dimension away from the part
module wit(p0, p1, s = 1){ bp_line(p0, p1, s); }

// a leader with a note on the end
module note(from, to, label, s = 1, halign = "left"){
  bp_line(from, to, s);
  bp_arrow(from, atan2(from[1] - to[1], from[0] - to[0]), s);
  translate([to[0] + (halign == "left" ? txt*s*0.4 : -txt*s*0.4), to[1]])
    text(label, size = txt*s, halign = halign, valign = "center");
}

// ring a feature that needs pointing out
module ring(c, d, s = 1){
  translate(c) difference(){
    circle(d = d + 4*lw*s, $fn = 48);
    circle(d = d, $fn = 48);
  }
}

// A drawing border. It is not decoration: --viewall frames whatever the
// widest geometry is, so without a border every sheet gets framed to its own
// stray dimension text and ends up a different size with random margins. With
// one, the border IS the widest thing and the drawing fills the page.
module sheet_frame(x0, y0, x1, y1, s = 1){
  b = lw*s*1.6;
  difference(){
    translate([x0, y0]) square([x1 - x0, y1 - y0]);
    translate([x0 + b, y0 + b]) square([x1 - x0 - 2*b, y1 - y0 - 2*b]);
  }
}

// a title block, bottom left of every sheet
module title_block(x, y, sheet, name, s = 1){
  t = txt*s;
  translate([x, y]){
    difference(){
      square([t*34, t*6.4]);
      translate([lw*s, lw*s]) square([t*34 - lw*s*2, t*6.4 - lw*s*2]);
    }
    translate([t*0.9, t*4.4]) text(str("WALL-E  ", sheet), size = t*1.2);
    translate([t*0.9, t*2.7]) text(name, size = t*0.85);
    translate([t*0.9, t*1.1])
      text("all dimensions mm · generated by walle.scad · do not hand-edit",
           size = t*0.55);
  }
}

// ============================================================================
//  3. OUTLINES
// ============================================================================
//  A blueprint wants line work, not a filled silhouette. These project the
//  REAL 3D model and then hollow the result, so the outline can never drift
//  away from what the model says.
//
//  The model is Y-up and its front is +x, so:
//    front view   rotate([0,90,0])   -> sheet x = model z, sheet y = model y
//    side  view   no rotation        -> sheet x = model x, sheet y = model y
//    top   view   rotate([90,0,0])   -> sheet x = model x, sheet y = -model z
// ============================================================================

//  Each view does its own hollowing. It would read better as
//  `outline(t) projection() ... children()`, and that is how it was written
//  first, but it silently produced SOLID SILHOUETTES: chaining children()
//  through two module levels leaves the second instantiation empty, so the
//  subtraction removed nothing. Two direct children() calls inside one module
//  are fine, so each view repeats the projection instead.
module view_front(t = 4){
  difference(){
    projection() rotate([0, 90, 0]) children();
    offset(delta = -t) projection() rotate([0, 90, 0]) children();
  }
}
module view_side(t = 4){
  difference(){
    projection() children();
    offset(delta = -t) projection() children();
  }
}
module view_top(t = 4){
  difference(){
    projection() rotate([90, 0, 0]) children();
    offset(delta = -t) projection() rotate([90, 0, 0]) children();
  }
}

// the robot without the ground plane, which would swamp every projection
module robot_nog(){
  if (show_pods) for (s = [1,-1]) translate([0, 0, s*pod_z]) pod();
  frame_steel(); pod_bolts(); battery_box();
  if (show_batteries) batteries();
  anti_tip(); risers(); body_shell(); shelf_layout();
  if (show_speakers) { speaker_boxes(); speakers(); }
  head();
}
module steel_only(){ frame_steel(); anti_tip(); risers(); }

// ============================================================================
//  SHEET 1 — GENERAL ARRANGEMENT
// ============================================================================
module sheet1(){
  s = 2.2;
  // ---- front elevation, on the left
  translate([-700, 0]){
    view_front(5) robot_nog();
    // overall width, below the tracks
    dim_h(-width_over/2, width_over/2, -120, str("WIDTH ", width_over), s);
    wit([-width_over/2, -20], [-width_over/2, -110], s);
    wit([ width_over/2, -20], [ width_over/2, -110], s);
    // pod centres
    dim_h(-pod_cl/2, pod_cl/2, -230, str("POD CENTRES ", pod_cl), s);
    // overall height, on the left
    dim_v(0, robot_h, -width_over/2 - 150, str("HEIGHT ", round(robot_h)), s, true);
    // The key heights, called out to the right. They are only 20-30 mm apart
    // down at the frame, so the LABELS are spread on a ladder and a kinked
    // leader joins each one back to its real height. Stacking them at their
    // true heights made four of them overlap into mush.
    hx = width_over/2 + 60;
    hl = width_over/2 + 300;
    heights = [[tray_y0,  str("box floor ", tray_y0, "  = LOWEST POINT")],
               [fr_bot,   str("rail bottom ", fr_bot)],
               [batt_y1,  str("pack top ", batt_y1)],
               [pod_top,  str("belt crown ", pod_top)],
               [body_y0,  str("body floor ", body_y0)],
               [spk_yc,   str("speaker centres ", round(spk_yc))],
               [body_y1,  str("body top ", body_y1)]];
    for (i = [0 : len(heights) - 1]){
      ly = 60 + i*105;                       // the label's slot on the ladder
      wit([0, heights[i][0]], [hx, heights[i][0]], s);
      wit([hx, heights[i][0]], [hl, ly], s);
      translate([hl + 10*s, ly])
        text(heights[i][1], size = txt*s*0.75, valign = "center");
    }
    dim_v(0, tray_y0, -width_over/2 - 60, str(tray_y0), s, true);
    translate([0, -460]) text("FRONT", size = txt*s*1.3, halign = "center");
  }
  // ---- side elevation, on the right
  translate([980, 0]){
    view_side(5) robot_nog();
    dim_h(-body_l/2, body_l/2, -120, str("BODY ", body_l), s);
    dim_h(-at_x - at_d/2, at_x + at_d/2, -230,
          str("OVER THE CASTORS ", 2*at_x + at_d), s);
    dim_h(-pod_A/2, pod_A/2, -340, str("GROUND CONTACT ", round(pod_A)), s);
    dim_v(0, robot_h, at_x + at_d/2 + 150, str(round(robot_h)), s);
    note([body_l/2 + 30, spk_yc], [body_l/2 + 300, spk_yc + 120],
         str("2 x 6.5\" speakers, ", round(spk_vol*10)/10, " L each"), s);
    note([at_x, at_clear + at_d/2], [at_x + 180, -150],
         str("anti-tip castor, ", at_clear, " clear"), s);
    translate([0, -460]) text("SIDE  (front is to the right)",
                              size = txt*s*1.3, halign = "center");
  }
  sheet_frame(-1460, -880, 1820, 1030, s);
  title_block(-1330, -800, "SHEET 1", "GENERAL ARRANGEMENT", s);
}

// ============================================================================
//  SHEET 2 — FRAME WELDMENT.  This is the one the welder gets.
// ============================================================================
module sheet2(){
  s = 1.5;
  // Dimensions go in BANDS at fixed heights, so nothing can land on top of
  // anything else. The plan sits high, the rail elevation low, and each has
  // its own bands above and below.

  // ---- PLAN, looking down
  translate([0, 820]){
    view_top(4) steel_only();
    // above: widths
    dim_h(-rail_zi, rail_zi, 210, str("CLEAR BAY ", bay_w), s);
    dim_h(-rail_zo, rail_zo, 320, str("OVER THE RAILS ", 2*rail_zo), s);
    // below: lengths, measured from the REAR end (x0), which is -x
    dim_h(rail_x0, rail_x1, -230, str("RAIL LENGTH ", rail_len), s, true);
    dim_h(rail_x0, cm_rear_x, -340,
          str("rear cross member ", round(cm_rear_x - rail_x0)), s, true);
    dim_h(rail_x0, cm_front_x, -450,
          str("front cross member ", round(cm_front_x - rail_x0)), s, true);
    note([0, rail_zi], [560, 300],
         str("cross members ", fr_w, "x", fr_h, ", ", cm_len,
             " long, ", bay_w, " clear"), s);
    translate([0, 355]) text("PLAN   front to the RIGHT",
                             size = txt*s*1.35, halign = "center");
  }

  // ---- RAIL ELEVATION, and the M12 holes. This is the point of the sheet.
  translate([0, -330]){
    view_side(4) steel_only();
    // the two holes, ringed, with witness lines up into the dimension bands
    for (bx = pod_bolt_x){
      ring([bx, pod_gp_yc], 25, s);
      wit([bx, pod_gp_yc], [bx, fr_top + 70], s);
    }
    dim_h(pod_bolt_x[0], pod_bolt_x[1], fr_top + 90,
          str("M12 PITCH ", pod_bolt_x[1] - pod_bolt_x[0]), s);
    dim_h(rail_x0, pod_bolt_x[0], fr_top + 200,
          str("REAR hole, ", round(pod_bolt_x[0] - rail_x0),
              " from the rail's REAR end"), s);
    // heights, on the left where nothing else goes
    dim_v(fr_bot, fr_top, rail_x0 - 110, str("rail ", fr_h), s, true);
    dim_v(0, fr_bot, rail_x0 - 260, str("rail bottom ", fr_bot), s, true);
    // and the sleeve note, out to the right
    note([pod_bolt_x[1] + 20, pod_gp_yc], [rail_x1 + 120, fr_top + 150],
         str("2 x Ø25 THROUGH BOTH WALLS, ", pod_gp_yc - fr_bot,
             " up from the rail bottom"), s);
    note([pod_bolt_x[1] + 20, pod_gp_yc - 30], [rail_x1 + 120, fr_top + 60],
         str("weld a Ø25 / Ø13 x ", fr_w, " sleeve into each"), s);
    translate([0, -150]) text("RAIL ELEVATION   front to the RIGHT",
                              size = txt*s*1.35, halign = "center");
  }

  translate([-770, 1270])
    text("Reuses the 4 M12 holes ALREADY DRILLED in the pods. No new hole goes into a built pod.",
         size = txt*s*0.85);
  sheet_frame(-830, -760, 1510, 1350, s);
  title_block(-750, -700, "SHEET 2", "FRAME WELDMENT — STEEL ONLY", s);
}

// ============================================================================
//  SHEET 3 — BATTERY BOX, six panels flat
// ============================================================================
module sheet3(){
  s = 1.1;
  bw2 = tray_clear + 2*tray_t;    // the box's outside width, 240

  // Every panel gets its own y slot with room for its dimensions underneath.
  // Laid out tight, the side wall's hole dimensions landed on the lid above.
  y_floor = 0;
  y_lid   = 420;
  y_sideA = 940;
  y_sideB = 1290;
  y_ends  = 1640;

  // ---- floor
  translate([0, y_floor]){
    o2() square([tray_len, bw2]);
    translate([tray_len/2, bw2/2])
      text("FLOOR", size = txt*s, halign = "center", valign = "center");
    dim_h(0, tray_len, -90, str(tray_len), s, true);
    dim_v(0, bw2, tray_len + 90, str(bw2), s);
  }

  // ---- lid
  translate([0, y_lid]){
    o2() box_lid_2d();
    translate([tray_len/2, bw2*0.74])
      text("LID", size = txt*s, halign = "center");
    dim_h(6, 6 + (tray_len - 12)/n_lid_x, -90,
          str("M5 pitch ", round((tray_len - 12)/n_lid_x)), s, true);
    note([tray_len/2 + vent_d/2, bw2/2], [tray_len + 130, bw2*0.62],
         str("Ø", vent_d, " MEMBRANE VENT, on the centreline"), s);
  }

  // ---- side walls. The M12 spanner holes are the only tricky part here.
  translate([0, y_sideA]){
    o2() box_side_2d();
    translate([tray_len*0.70, box_wall_h*0.22])
      text("SIDE WALL   2 off, HANDED", size = txt*s, halign = "center");
    for (bx = pod_bolt_x)
      wit([bx + tray_len/2, pod_gp_yc - tray_y0], [bx + tray_len/2, -60], s);
    dim_h(pod_bolt_x[0] + tray_len/2, pod_bolt_x[1] + tray_len/2, -90,
          str("pitch ", pod_bolt_x[1] - pod_bolt_x[0]), s, true);
    dim_h(0, pod_bolt_x[0] + tray_len/2, -200,
          str("from the REAR edge ", round(pod_bolt_x[0] + tray_len/2)), s, true);
    dim_v(0, pod_gp_yc - tray_y0, -90, str(pod_gp_yc - tray_y0, " up"), s, true);
    dim_v(0, box_wall_h, tray_len + 90, str(box_wall_h), s);
    note([pod_bolt_x[1] + tray_len/2 + bolt_access_d/2, pod_gp_yc - tray_y0],
         [tray_len + 130, box_wall_h*0.75],
         str("2 x Ø", bolt_access_d, " M12 SPANNER ACCESS"), s);
    note([pod_bolt_x[1] + tray_len/2 + bolt_access_d/2, pod_gp_yc - tray_y0 - 18],
         [tray_len + 130, box_wall_h*0.30],
         "FIT SILICONE BLANKING PLUGS AFTER BOLTING UP", s);
  }
  translate([0, y_sideB]){
    o2() box_side_2d();
    translate([tray_len*0.66, box_wall_h*0.58])
      text("SIDE WALL", size = txt*s, halign = "center");
  }

  // ---- end walls
  for (i = [0, 1]) translate([i*(bw2 + 100), y_ends]){
    o2() box_end_2d();
    translate([bw2/2, box_wall_h/2])
      text("END", size = txt*s, halign = "center", valign = "center");
    if (i == 0){
      dim_h(0, bw2, -90, str(bw2), s, true);
      dim_v(0, box_wall_h, -90, str(box_wall_h), s, true);
    }
  }

  translate([-340, 1880])
    text(str("Cut all six from one ", tray_t,
             " mm sheet. Gasket tape on every mating face. See BUILD.md step 4."),
         size = txt*s*0.95);
  sheet_frame(-400, -560, 1380, 1960, s);
  title_block(-330, -500, "SHEET 3",
              str(tray_t, " mm PLYWOOD — CLOSED BATTERY BOX, 6 PANELS"), s);
}

// ============================================================================
//  SHEET 4 — CHEST PANEL, the speaker baffle
// ============================================================================
module sheet4(){
  s = 1.1;
  cw = 2*chest_z;
  ch = chest_y1 - chest_y0;
  o2() difference(){
    square([cw, ch]);
    for (sz = [1,-1])
      translate([cw/2 + sz*spk_zc, spk_yc - chest_y0]) circle(d = spk_cut_d, $fn = 96);
  }
  dim_h(0, cw, -80, str("PANEL ", cw), s);
  dim_v(0, ch, cw + 80, str(ch), s);
  dim_h(cw/2 - spk_zc, cw/2 + spk_zc, ch + 90, str("CENTRES ", 2*spk_zc), s);
  dim_v(0, spk_yc - chest_y0, -80,
        str("up from the bottom edge ", round(spk_yc - chest_y0)), s, true);
  for (sz = [1,-1]) wit([cw/2 + sz*spk_zc, spk_yc - chest_y0],
                        [cw/2 + sz*spk_zc, ch + 70], s);
  note([cw/2 + spk_zc + spk_cut_d/2, spk_yc - chest_y0],
       [cw + 120, ch*0.78], str("2 x Ø", spk_cut_d, " CUTOUT"), s);
  note([cw/2 - spk_zc - spk_cut_d/2, spk_yc - chest_y0],
       [-200, ch*0.80], str("Ø", spk_rim_d, " rim lands on this face"), s, "right");
  translate([cw/2, -215])
    text(str(chest_t, " mm ply · set back ", chest_d, " from the body's front face"),
         size = txt*s*0.9, halign = "center");
  translate([cw/2, -275])
    text(str("a sealed enclosure bolts behind each: ", spk_box_d, " x ",
             round(spk_box_h), " x ", round(spk_box_w), " -> ",
             round(spk_vol*10)/10, " litres"),
         size = txt*s*0.9, halign = "center");
  sheet_frame(-430, -560, 1060, 520, s);
  title_block(-370, -500, "SHEET 4", "CHEST PANEL / SPEAKER BAFFLE", s);
}

// ============================================================================
//  SHEET 5 — ELECTRONICS SHELF
// ============================================================================
module sheet5(){
  s = 1.2;
  o2() square([shelf_l, shelf_w]);
  // lower deck, four rows centred on the shelf
  for (row = lower_rows)
    for (i = [0 : len(low_parts(row)) - 1])
      let(p  = low_parts(row)[i],
          d  = p[1],
          px = shelf_l/2 - row_len(row)/2 + xrun(row, i),
          pz = shelf_w/2 + rows_dep/2 - row_z(row) - d[1]){
        translate([px, pz]) o2(1.8) square([d[0], d[1]]);
        translate([px + d[0]/2, pz + d[1]/2])
          text(p[0], size = txt*s*0.55, halign = "center", valign = "center");
      }
  // upper tray, centred. Laptop and hub sit on this, not on the lower deck.
  translate([shelf_l/2 - upper_l/2, shelf_w/2 - upper_w/2])
    o2(2.4) square([upper_l, upper_w]);
  for (p = upper_items)
    let(d  = p[1],
        px = shelf_l/2 - upper_l/2 + 10 + p[2][0],
        pz = shelf_w/2 - upper_w/2 + 10 + p[2][1]){
      translate([px, pz]) o2(1.8) square([d[0], d[1]]);
      translate([px + d[0]/2, pz + d[1]/2])
        text(p[0], size = txt*s*0.62, halign = "center", valign = "center");
    }
  // where the speaker enclosures sit OVER the shelf
  for (sz = [1,-1]){
    x0 = shelf_l/2 + max(spk_box_x0, -shelf_l/2);
    y0 = shelf_w/2 + sz*spk_zc - spk_box_w/2;
    translate([x0, y0]) o2(1.2) square([spk_shadow_x, spk_box_w]);
    translate([x0 + spk_shadow_x/2, y0 + (sz > 0 ? spk_box_w - 22 : 12)])
      text("SPEAKER BOX OVERHEAD", size = txt*s*0.62, halign = "center");
  }
  dim_h(0, shelf_l, -70, str("LOWER SHELF ", round(shelf_l)), s);
  dim_v(0, shelf_w, shelf_l + 70, str(round(shelf_w)), s);
  dim_h(shelf_l/2 - upper_l/2, shelf_l/2 + upper_l/2, shelf_w + 40,
        str("LAPTOP TRAY ", round(upper_l), " x ", round(upper_w)), s);
  translate([shelf_l/2, shelf_w + 250])
    text("PLAN, looking down.  Front of the robot is to the RIGHT.  TWO FLOORS.",
         size = txt*s*0.90, halign = "center");
  translate([shelf_l/2, shelf_w + 195])
    text(str("Lower: four rows, ", round(shelf_fill),
             "% of the shelf. Upper: XPS + USB hub on a lift-out tray. PD pack stays DOWN."),
         size = txt*s*0.68, halign = "center");
  translate([shelf_l/2, shelf_w + 150])
    text(str("The two enclosures cover ", round(100 - shelf_reach),
             "% of the shelf. Unbolt them, then lift the tray. Stack ",
             round(part_h_max), " mm."),
         size = txt*s*0.68, halign = "center");
  sheet_frame(-300, -400, 800, 960, s);
  title_block(-240, -340, "SHEET 5", "ELECTRONICS — TWO FLOORS", s);
}

// ============================================================================
//  4. PICK A VIEW
// ============================================================================
// A note on colour, because it looks like a bug and is not one: OpenSCAD's
// CGAL renderer draws a 2D FILL in one colour and a 2D EDGE in another, and
// color() does not override it. So anything solid comes out as a block of
// colour and anything thin comes out as a line. That is why every sheet below
// is drawn as OUTLINES — it is the only way to get line work out of OpenSCAD,
// and it is what a blueprint wants anyway.
if      (view == "s1") sheet1();
else if (view == "s2") sheet2();
else if (view == "s3") sheet3();
else if (view == "s4") sheet4();
else if (view == "s5") sheet5();
// the solid views just hand straight back to the model's own scene()
else if (view == "robot")    robot_full();
else if (view == "frame")  { frame_steel(); pod_bolts(); anti_tip(); risers(); }
else if (view == "head")     head();
else if (view == "chest")  { chest_panel(); speaker_boxes(); speakers(); }
else if (view == "shelf")  { color(c_ply) translate([-shelf_l/2, shelf_y, -shelf_w/2])
                               cube([shelf_l, shelf_t, shelf_w]);
                             color(c_ply) translate([-upper_l/2, upper_y, -upper_w/2])
                               cube([upper_l, upper_t, upper_w]);
                             shelf_layout(); }
else if (view == "section")  difference(){ robot_full();
                               translate([-800,-50,0]) cube([1600,1400,800]); }
else echo(str("*** unknown view \"", view,
              "\" — pick one of s1 s2 s3 s4 s5 robot frame head chest shelf section"));
