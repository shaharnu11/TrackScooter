// WALL-E eye cartridge: 2 printed parts per eye, for the
// Waveshare ESP32-S3-Touch-AMOLED-1.75 (standard or -G GPS version)
// in a steel tube 54 mm inside x 90 mm long.
//
//   part 1 = sleeve with the front lip (the glass rests on a foam ring
//            against the lip)
//   part 2 = carrier: tube + cap. The board is screwed to it with 3 x M2
//            into the board's own brass posts. Cap covers the tube end,
//            hole for a PG16 gland, 3 screwdriver holes for the M2 screws.
//
// Assembly: board onto part 2 (3 x M2x6 through the cap holes) -> wires
// onto the header, out through the gland -> foam ring on the lip ->
// part 2 into part 1 -> cartridge into the painted tube -> 3 x M3
// self-tapping from outside through the steel, part 1 and part 2.
//
// Board numbers are from Waveshare's 3D model (ESP32-S3-Touch-AMOLED-1_75.stp),
// measured from the glass front, along the axis:
//   glass Ø48.96, 1.10 thick | board Ø46.0 | USB-C ends at 10.15 (edge, r 23.8)
//   brass posts M2, Ø3.5, tips at 10.43 | header ends at 12.70 | MX1.25 at 11.70
//
// part = "p1" | "p2" (cap down, ready to print) | "all" | "cut"
part = "all";

// STEEL TUBE (mm)
tube_id  = 54;
tube_od  = 60;    // PLACEHOLDER: measure. Only sets the cap's outer size.
tube_len = 90;
recess   = 30;    // lip front, from the tube front (sun shade), painted black

// BOARD (from the Waveshare model)
glass_d  = 48.96;
va_d     = 44.16; // visible picture
post_tip = 10.43; // brass post tips, behind the glass front
post_r   = 2.5;   // printed pad radius (posts are Ø3.5)
posts    = [[13.75, 14.70], [-13.75, 14.70], [0, -20.50]];  // header side is +y
back_max = 12.70; // header back, behind the glass front

foam_t   = 1.5;   // foam ring, as cut
foam_c   = 1.1;   // foam ring, squeezed

// part 1: sleeve + lip
p1_od  = tube_id - 0.4;
p1_id  = glass_d + 0.54;     // 49.5
lip_id = 45;                 // picture is 44.16; the lip only covers the black rim
lip_t  = 2;
p1_len = tube_len - recess;

// part 2: carrier tube + cap
p2_od   = p1_id - 0.4;       // 49.1, slides in part 1
p2_id   = 46;                // clears the header and the MX1.25 sockets
cap_t   = 4;
pg16    = 22.8;              // PG16 gland thread 22.5
access  = 5;                 // screwdriver holes in the cap, over the M2 screws
pad_t   = 3;
m2      = 2.3;               // M2 clearance
m2_head = 4.4;

z_glass = recess + lip_t + foam_c;          // glass front, from the tube front
z_pad   = z_glass + post_tip;               // pad front = post tips
z_ring  = z_glass + back_max + 0.3;         // carrier tube starts behind the header
p2_len  = tube_len - z_pad;                 // pad front to the tube end

screw_from_end = 7;
pilot = 2.6;                 // M3 self-tapping pilot in plastic
$fn = 128;

module tube(od, id, h) { difference() { cylinder(d = od, h = h); translate([0, 0, -1]) cylinder(d = id, h = h + 2); } }

module screw_holes(z, r) {
  for (a = [90, 210, 330]) rotate([0, 0, a]) translate([0, 0, z]) rotate([0, 90, 0])
    cylinder(d = pilot, h = r + 1, $fn = 24);
}

// part 1: lip front at z = 0, tube end at z = p1_len
module part1() {
  difference() {
    union() { tube(p1_od, p1_id, p1_len); tube(p1_od, lip_id, lip_t); }
    screw_holes(p1_len - screw_from_end, p1_od / 2);
  }
}

// part 2: pad fronts at z = 0, tube end at z = p2_len, cap behind it
module part2() {
  rz = z_ring - z_pad;                      // carrier tube front
  difference() {
    union() {
      translate([0, 0, rz]) tube(p2_od, p2_id, p2_len - rz);
      translate([0, 0, p2_len]) cylinder(d = tube_od, h = cap_t);
      for (p = posts) {                     // pad + sloped arm out to the wall
        a = atan2(p[1], p[0]);
        hull() {
          translate([p[0], p[1], 0]) cylinder(r = post_r, h = pad_t, $fn = 48);
          rotate([0, 0, a]) translate([p2_id / 2 - 0.5, -2.5, 0]) cube([1.5, 5, rz + 8]);
        }
      }
    }
    translate([0, 0, p2_len - 1]) cylinder(d = pg16, h = cap_t + 2);
    for (p = posts) translate([p[0], p[1], 0]) {
      translate([0, 0, -1]) cylinder(d = m2, h = pad_t + 2, $fn = 24);
      translate([0, 0, pad_t]) cylinder(d = m2_head, h = p2_len, $fn = 32);
      translate([0, 0, p2_len - 1]) cylinder(d = access, h = cap_t + 2, $fn = 32);
    }
    screw_holes(p2_len - screw_from_end, p2_od / 2);
  }
}

if (part == "p1") part1();
if (part == "p2") translate([0, 0, p2_len + cap_t]) rotate([180, 0, 0]) part2();  // cap down
if (part == "all") {
  color([0.20, 0.45, 0.85]) part1();
  color([0.95, 0.55, 0.15]) translate([tube_od + 15, 0, 0]) part2();
}
// assembled, cut in half along the axis (tube front at the bottom)
module half() { intersection() { children(); translate([-200, -100, -10]) cube([200, 200, 300]); } }
if (part == "cut") {
  color([0.70, 0.72, 0.76]) half() tube(tube_od, tube_id, tube_len);                         // steel
  color([0.20, 0.45, 0.85]) half() translate([0, 0, recess]) part1();
  color([1.00, 0.85, 0.20]) half() translate([0, 0, recess + lip_t]) tube(glass_d, lip_id + 0.5, foam_c);
  color([0.10, 0.15, 0.35]) half() translate([0, 0, z_glass]) cylinder(d = glass_d, h = 1.1);  // glass
  color([0.15, 0.55, 0.25]) half() translate([0, 0, z_glass + 1.1]) cylinder(d = 46, h = 5.8);  // panel + board
  color([0.80, 0.65, 0.20]) half() for (p = posts) translate([p[0], p[1], z_glass + 6.9]) cylinder(d = 3.5, h = 3.53, $fn = 6);
  color([0.95, 0.55, 0.15]) half() translate([0, 0, z_pad]) part2();
}

echo(str("glass front ", z_glass, " mm deep; part 1 ", p1_len, " long; part 2 ", p2_len + cap_t, " long"));
