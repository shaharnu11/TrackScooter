// ============================================================================
//  POD INTERFACE — the only place these numbers are allowed to live
// ============================================================================
//
//  WHY THIS FILE EXISTS
//
//  The pods are BUILT. Nothing in the WALL-E project may change them. But the
//  WALL-E model needs thirteen numbers off them, and those numbers used to be
//  typed into cad/walle_frame.scad as plain constants. That is a copy, and a
//  copy of a measurement always ends up disagreeing with the original.
//
//  So they live here, once, and both the WALL-E model and the checker read
//  them from here.
//
//  EVERY NUMBER BELOW WAS VERIFIED AGAINST THE POD MODEL ON 2026-09-16:
//    archive/rev012-inline-batteries/apollo_track_pod_rev012.scad
//  All thirteen agreed. The rev012 variable each one came from is named in its
//  comment, so the check can be repeated. To repeat it, run:
//    openscad -o /dev/null WALL-E/check_pod_interface.scad
//
//  COORDINATES, pod-local
//    x  fore and aft.   x = 0 is the HUB AXLE. Forward is -x.
//    y  up.             y = 0 is the GROUND.
//    z  left and right. z = 0 is the pod's centre plane.
//
// ============================================================================

// ---- the z stack, outward from the pod centre ------------------------------
// This is the stack the frame has to land on, and it is worth reading in full
// because the names are historical and misleading:
//
//    0 .. 59    belt            (track_w 118 wide, so +-59)
//   84 .. 88    fork leg        (leg_t 4, MEASURED. The donor fork's leg)
//   88 .. 94    CARRIER plate   (carrier_t 6. rev012 cz = fork_gap/2 + leg_t)
//   94 .. 100   GREEN plate     (gp_t 6. The pod's widest point)
//
// rev012's `fork_gap = 168` is commented there as "spacing of the two carrier
// plates". It is not — it is the FORK LEG inner gap. The carriers sit on the
// legs' outer faces, at 88. That comment is wrong in rev012; do not trust it.
pod_belt_hw   = 59;      // rev012 track_w/2
pod_leg_zi    = 84;      // rev012 fork_gap/2
pod_leg_t     = 4;       // rev012 leg_t        MEASURED 2026-07-13
pod_carr_zi   = 88;      // rev012 cz
pod_carr_t    = 6;       // rev012 carrier_t
pod_gp_zi     = 94;      // rev012 cz + carrier_t   green plate INNER face
pod_gp_t      = 6;       // rev012 gp_t
pod_gp_zo     = 100;     // = pod_gp_zi + pod_gp_t. THE POD'S WIDEST POINT

// ---- heights above the ground ----------------------------------------------
pod_hub_h     = 216;     // rev012 hub_h = B + D/2 + T
pod_top       = 327;     // rev012 pod_top = hub_h + pitch_r + T/2 = 327.04
pod_gp_yc     = 227;     // rev012 hub_h + gp_yc (gp_yc = 11, above the AXLE)
pod_gp_w      = 60;      // rev012 gp_w -> the band runs 197 .. 257
pod_fr_top    = 257;     // rev012 fr_top = hub_h + gp_yc + gp_w/2

// ---- the belt loop ---------------------------------------------------------
pod_A         = 231.2;   // rev012 solved A = 231.155. GROUND CONTACT LENGTH
pod_B         = 150;     // rev012 B, hub centre above the idler axle line
pod_idler_d   = 108;     // rev012 D
pod_T         = 12;      // rev012 T, belt carcass thickness
pod_pitch_r   = 105.04;  // rev012 pitch_r = 105.042, sprocket cord radius
pod_belt_w    = 118;     // rev012 track_w
pod_halfl     = 181.6;   // = (A + idler_d + 2*T)/2 = 181.58 -> 363.2 overall

// ---- the M12 holes, ALREADY DRILLED ----------------------------------------
// rev012 rl_bolts = [gp_x0 + gp_end_edge, rl_end_x - rl_end_edge] = [-168, -108]
// Pod-local x, so 108 and 168 FORWARD of the hub axle. Rev 012 ran its rails
// forward of the pod; WALL-E runs them across it. The holes are where they
// are, and WALL-E reuses them so that NO NEW HOLE goes into a built pod.
pod_bolt_x    = [-168, -108];
pod_bolt_d    = 12;      // M12 10.9

// ============================================================================
//  TWO CAUTIONS, both real, neither yet resolved
// ============================================================================
//
//  1. THE GREEN PLATES ARE NOT SYMMETRIC. In rev012 they are:
//       +z (trailing) plate:  x = -188 .. +72   (260 long)
//       -z (leading)  plate:  x = -188 .. +20   (208 long)
//     The +z plate is longer because it carries the rear shock eye. Both
//     plates cover both M12 holes (-168 and -108 are inside -188..+20), so
//     the WALL-E frame bolts up either way and this does NOT affect the
//     mounting. It matters only for the render and for which way round a pod
//     goes. cad/walle_frame.scad draws them symmetric, and places the two
//     pods by translation rather than by mirroring, so one pod's long plate
//     faces inboard and the other's faces outboard. Cosmetic today. Fix it
//     before anyone uses the model to decide handedness.
//
//  2. DO THE GREEN PLATES EVEN EXIST ON THE BUILT PODS? rev012 asks the same
//     question at line 390: "why do we need the green plate at all? — we
//     don't, once the deck goes", and in its own chassis mode it drops the
//     bracket and picks up on the CARRIERS directly. WALL-E currently assumes
//     the green plates are fitted, which is what puts its widest point at
//     100 and its overall width at 700.
//     IF THE PLATES ARE NOT ON THE PODS, set pod_has_green_plate = false.
//     Then the frame lands on the carrier outer faces at 94 instead, the
//     robot is 12 mm narrower, and the rails move out 6 mm each side.
//     ** CONFIRM THIS AGAINST THE PHYSICAL PODS BEFORE CUTTING STEEL. **
pod_has_green_plate = true;

// the face the WALL-E rail actually bolts to, derived from that answer
pod_mount_z   = pod_has_green_plate ? pod_gp_zo : pod_gp_zi;   // 100 or 94
