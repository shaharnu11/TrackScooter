// ============================================================================
//  CHECK: does pod_interface.scad still agree with the real pod model?
// ============================================================================
//
//  Run this, and only this, whenever the pod model changes:
//
//    openscad -o /dev/null WALL-E/check_pod_interface.scad
//
//  It loads BOTH files and compares them number by number. Every line prints
//  either OK or *** MISMATCH. It renders nothing.
//
//  If you see a MISMATCH, pod_interface.scad is wrong and every dimension in
//  the WALL-E model downstream of it is wrong too. Fix the interface file,
//  then re-run cad/walle_frame.scad and re-check its guards.
//
// ============================================================================

include <../archive/rev012-inline-batteries/apollo_track_pod_rev012.scad>

// pod_interface.scad prefixes everything with pod_, and rev012 does not, so
// the two sets of names do not collide. Load ours second so ours win.
include <pod_interface.scad>

// rev012 does not expose these four under a single name, so rebuild them from
// its own primitives rather than hard-coding anything.
//
// These MUST be defined before the `checks` list below. OpenSCAD does not
// resolve a forward reference inside a top-level list: put them after and the
// four checks that use them silently compare against undef.
A_r12         = A_eff;
idler_d_r12   = 2*(hub_h - B - T);              // from hub_h = B + D/2 + T
pod_top_r12   = hub_h + pitch_r + T/2;
pod_halfl_r12 = (A_eff + idler_d_r12 + 2*T)/2;

// ---- the comparison --------------------------------------------------------
// [what it is, our number, rev012's number, how close is close enough]
checks = [
  ["belt half width",        pod_belt_hw,  track_w/2,                  0.01],
  ["fork leg inner face",    pod_leg_zi,   fork_gap/2,                 0.01],
  ["fork leg thickness",     pod_leg_t,    leg_t,                      0.01],
  ["carrier inner face",     pod_carr_zi,  cz,                         0.01],
  ["carrier thickness",      pod_carr_t,   carrier_t,                  0.01],
  ["green plate inner face", pod_gp_zi,    cz + carrier_t,             0.01],
  ["green plate thickness",  pod_gp_t,     gp_t,                       0.01],
  ["green plate outer face", pod_gp_zo,    cz + carrier_t + gp_t,      0.01],
  ["hub axle height",        pod_hub_h,    hub_h,                      0.01],
  ["belt crown height",      pod_top,      pod_top_r12,                0.10],
  ["green band centre",      pod_gp_yc,    hub_h + gp_yc,              0.01],
  ["green band height",      pod_gp_w,     gp_w,                       0.01],
  ["green band top",         pod_fr_top,   hub_h + gp_yc + gp_w/2,     0.01],
  ["ground contact length",  pod_A,        A_r12,                      0.10],
  ["hub above idler line",   pod_B,        B,                          0.01],
  ["idler diameter",         pod_idler_d,  idler_d_r12,                0.01],
  ["belt thickness",         pod_T,        T,                          0.01],
  ["sprocket cord radius",   pod_pitch_r,  pitch_r,                    0.01],
  ["belt width",             pod_belt_w,   track_w,                    0.01],
  ["pod half length",        pod_halfl,    pod_halfl_r12,              0.10],
  ["front M12 hole",         pod_bolt_x[0],rl_bolts[0],                0.01],
  ["rear M12 hole",          pod_bolt_x[1],rl_bolts[1],                0.01],
  ["M12 diameter",           pod_bolt_d,   bolt_d,                     0.01],
];

echo("");
echo("=== POD INTERFACE CHECK ==================================================");
echo(str("    ours: WALL-E/pod_interface.scad"));
echo(str("  theirs: archive/rev012-inline-batteries/apollo_track_pod_rev012.scad"));
echo("");
for (c = checks)
  echo(str(abs(c[1] - c[2]) <= c[3] ? "  OK       " : "  *** MISMATCH  ",
           c[0], ": ours ", c[1], " vs rev012 ", c[2],
           abs(c[1] - c[2]) <= c[3] ? "" : str("   <<< DIFFERS BY ",
                                               round(abs(c[1]-c[2])*1000)/1000)));
bad = len([for (c = checks) if (abs(c[1] - c[2]) > c[3]) 1]);
echo("");
echo(str(bad == 0
         ? str("=== ALL ", len(checks), " NUMBERS AGREE ===============================================")
         : str("=== ", bad, " MISMATCH(ES) — THE WALL-E MODEL IS BUILT ON WRONG NUMBERS ===")));
echo("");

// Nothing to draw.
