// WALL-E eye cartridge: 2 printed parts per eye. Build the eye on the table,
// then slide it into the steel tube and fix it with 3 screws.
//
//   part 1 = sleeve with the front lip (the screen rests against the lip)
//   part 2 = cap with a pusher tube (slides inside part 1, holds the screen
//            from behind; the cap covers the tube end, hole for a PG16 gland)
//
// Assembly: foam + screen into part 1 from the back, against the lip ->
// USB-C cable through the gland, plug into the screen -> part 2 into part 1 ->
// whole cartridge into the painted steel tube -> 3 x M3 self-tapping screws
// from outside, through the steel, part 1 and part 2 (holes at the back end).
//
// part = "p1" | "p2" | "all" (both, side by side) | "cut" (assembled, cut)
part = "all";

// MEASURE THE TUBE AND SET THESE (mm). Placeholder values:
tube_id  = 80;    // steel tube inside diameter
tube_od  = 84;    // steel tube outside diameter
tube_len = 144;   // one eye tube length
recess   = 40;    // screen depth from the front (sun shade), painted black

// screen: Waveshare ESP32-S3-Touch-LCD-2.1B
screen_d = 75;
screen_t = 12;    // glass + board + parts on the back, approx: CHECK on the real one
foam_t   = 1.5;   // foam ring between lip and glass

// part 1: sleeve + lip
p1_od  = tube_id - 0.4;       // slides into the tube
p1_id  = screen_d + 0.6;      // screen slides in
lip_id = 66;                  // covers the screen rim only; picture is ~53
lip_t  = 3;
p1_len = tube_len - recess;   // from the lip to the tube end

// part 2: pusher tube + cap
p2_od  = p1_id - 0.4;         // slides into part 1
p2_id  = 71;                  // presses the board edge; inside stays free
cap_t  = 4;
p2_len = p1_len - lip_t - foam_t - screen_t;   // pusher reaches the screen back
pg16   = 22.8;                // PG16 gland thread 22.5

screw_from_end = 7;           // screw holes, measured from the tube end
pilot = 2.6;                  // M3 self-tapping pilot in plastic
$fn = 128;

module tube(od, id, h) { difference() { cylinder(d = od, h = h); translate([0, 0, -1]) cylinder(d = id, h = h + 2); } }

module screw_holes(z, r) {
  for (a = [0, 120, 240]) rotate([0, 0, a + 90]) translate([0, 0, z]) rotate([0, 90, 0])
    cylinder(d = pilot, h = r + 1, $fn = 24);
}

// part 1: lip at z = 0 (front), tube end at z = p1_len (back)
module part1() {
  difference() {
    union() { tube(p1_od, p1_id, p1_len); tube(p1_od, lip_id, lip_t); }
    screw_holes(p1_len - screw_from_end, p1_od / 2);
  }
}

// part 2: pusher front at z = 0, cap at the back
module part2() {
  difference() {
    union() {
      tube(p2_od, p2_id, p2_len);
      translate([0, 0, p2_len]) cylinder(d = tube_od, h = cap_t);
    }
    translate([0, 0, p2_len - 1]) cylinder(d = pg16, h = cap_t + 2);
    screw_holes(p2_len - screw_from_end, p2_od / 2);
  }
}

if (part == "p1") part1();
if (part == "p2") translate([0, 0, p2_len + cap_t]) rotate([180, 0, 0]) part2();  // cap down, prints well
if (part == "all") {
  color([0.20, 0.45, 0.85]) part1();
  color([0.95, 0.55, 0.15]) translate([tube_od + 15, 0, 0]) part2();
}
// assembled, cut in half along the axis (front = lip at the bottom)
module half() { intersection() { children(); translate([-200, -100, -10]) cube([200, 200, 300]); } }
if (part == "cut") {
  color([0.70, 0.72, 0.76]) half() translate([0, 0, -recess]) tube(tube_od, tube_id, tube_len); // steel
  color([0.20, 0.45, 0.85]) half() part1();
  color([1.00, 0.85, 0.20]) half() translate([0, 0, lip_t]) tube(screen_d, lip_id, foam_t);      // foam ring
  color([0.10, 0.15, 0.35]) half() translate([0, 0, lip_t + foam_t]) cylinder(d = screen_d, h = 3); // glass
  color([0.15, 0.55, 0.25]) half() translate([0, 0, lip_t + foam_t + 3]) cylinder(d = screen_d - 1, h = screen_t - 3); // board
  color([0.95, 0.55, 0.15]) half() translate([0, 0, lip_t + foam_t + screen_t]) part2();
}
