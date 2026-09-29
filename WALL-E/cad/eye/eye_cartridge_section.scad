// WALL-E eye cartridge: flat labelled cross-section for the README.
// Side view, cut through the middle. x = depth (front at 0), y = up/down, mm.
// Same numbers as eye_cartridge.scad (placeholder tube 80 / 84 / 144).
$fn = 64;
Ri = 40; Ro = 42; L = 144; rec = 40;             // steel tube
p1o = 39.8; p1i = 37.8; lipi = 33; lip_t = 3;     // part 1
foam_t = 1.5; sc = 37.5; scr_t = 12;              // foam, screen
p2o = 37.6; p2i = 35.5; cap_t = 4;                // part 2
xl = rec; xf = xl + lip_t; xs = xf + foam_t; xb = xs + scr_t;

module p(c) { color(c) linear_extrude(1) children(); }
module both(y0, y1, x0, x1) { translate([x0, y0]) square([x1 - x0, y1 - y0]); translate([x0, -y1]) square([x1 - x0, y1 - y0]); }
module lbl(n, x, y, tx, ty, s) {
  color("black") linear_extrude(1.2) {
    hull() { translate([x, y]) circle(0.35); translate([tx, ty]) circle(0.35); }
    translate([x, y]) circle(1.1);
    translate([tx + (tx > x ? 1.5 : -1.5), ty - 1.6]) text(str(n, "  ", s), size = 3.8, halign = tx > x ? "left" : "right", font = "Liberation Sans:style=Bold");
  }
}
module dim(x0, y0, x1, y1, s) {
  color([0.1, 0.3, 0.8]) linear_extrude(1.2) {
    hull() { translate([x0, y0]) circle(0.3); translate([x1, y1]) circle(0.3); }
    translate([x0, y0]) circle(0.9); translate([x1, y1]) circle(0.9);
    translate([(x0 + x1) / 2 + (x0 == x1 ? 1.5 : 0), (y0 + y1) / 2 + (x0 == x1 ? -1.5 : 1.8)]) text(s, size = 3.4, halign = x0 == x1 ? "left" : "center");
  }
}

p([0.62, 0.64, 0.70]) both(Ri, Ro, 0, L);                 // 1 steel
p([0.05, 0.05, 0.05]) both(Ri - 0.6, Ri, 0, rec);         // 2 black paint
p([0.20, 0.45, 0.85]) both(p1i, p1o, xl, L);              // 3 part 1 sleeve
p([0.20, 0.45, 0.85]) both(lipi, p1o, xl, xl + lip_t);    //   part 1 lip
p([1.00, 0.80, 0.15]) both(lipi, sc, xf, xs);             // 4 foam ring
p([0.15, 0.30, 0.75]) translate([xs, -sc]) square([3, 2 * sc]);            // 5 glass
p([0.20, 0.60, 0.30]) translate([xs + 3, -sc + 0.5]) square([scr_t - 3, 2 * sc - 1]); // 6 board
p([0.35, 0.35, 0.35]) translate([xb, -16]) square([6, 9]);                // USB-C socket
p([0.95, 0.55, 0.15]) both(p2i, p2o, xb, L);              // 7 part 2 pusher
p([0.95, 0.55, 0.15]) both(11.4, Ro + 1, L, L + cap_t);   //   part 2 cap
p([0.18, 0.18, 0.20]) translate([L + cap_t, -9]) square([9, 18]);          // 8 PG16 gland
p([0.85, 0.70, 0.10]) translate([L - 8.5, p2i]) square([3, 9.5]);          // 9 screw
p([0.85, 0.70, 0.10]) translate([L - 10, Ro]) square([6, 1.8]);
color([0.02, 0.02, 0.02]) linear_extrude(1.1) {                            // 10 cable
  hull() { translate([xb + 6, -11.5]) circle(1.6); translate([xb + 30, -11.5]) circle(1.6); }
  hull() { translate([xb + 30, -11.5]) circle(1.6); translate([L - 6, 0]) circle(1.6); }
  hull() { translate([L - 6, 0]) circle(1.6); translate([L + 45, 0]) circle(1.6); }
}
color([0.95, 0.75, 0.05]) linear_extrude(1.1) hull() { translate([-25, 78]) circle(0.5); translate([xs, -sc + 3]) circle(0.5); }
color([0.9, 0.6, 0.0]) linear_extrude(1.2) translate([-24, 81]) text("sun", size = 4);

lbl(2, 18, Ri - 0.3, -12, 50, "black paint inside (sun shade)");
lbl(3, xl + 1.5, 35, -12, 62, "PART 1: lip, hole 66");
lbl(4, xf + 0.7, 35.5, -12, 72, "foam ring 75 / 66");
lbl(5, xs + 1.5, 8, -12, 22, "screen glass = the eye");
lbl(9, L - 7, 44, 164, 72, "3 x M3 screw: steel + part 1 + part 2");
lbl(1, 100, Ro - 1, 164, 60, "steel tube");
lbl(7, 110, 36.5, 164, 48, "PART 2: pusher tube");
lbl(3, 120, 38.8, 164, 38, "PART 1: sleeve");
lbl(7, L + 2, 30, 164, 26, "PART 2: cap");
lbl(6, xs + 7, 14, 164, 14, "board, ESP32-S3 on the back");
lbl(8, L + 8, -6, 164, -20, "PG16 gland + glue/silicone");
lbl(10, 118, -3.8, 164, -32, "USB-C cable -> neck -> hub");
dim(0, -47, rec, -47, "40 deep");
dim(-5, -Ri, -5, Ri, "tube inside");
color("black") linear_extrude(1.2) translate([-62, -62]) text("FRONT (people see this side)", size = 4, font = "Liberation Sans:style=Bold");
color("black") linear_extrude(1.2) translate([150, -62]) text("BACK", size = 4, font = "Liberation Sans:style=Bold");
color([0.1, 0.1, 0.1]) linear_extrude(1.2) translate([-62, 88]) text("WALL-E eye cartridge - side cut (placeholder tube 80/84/144)", size = 4.6, font = "Liberation Sans:style=Bold");
