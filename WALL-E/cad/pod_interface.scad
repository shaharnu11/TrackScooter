// ============================================================================
//  POD INTERFACE — the only place these numbers are allowed to live
// ============================================================================
//
//  WHY THIS FILE EXISTS
//
//  The pods are BUILT. Nothing in the WALL-E project may change them. But the
//  WALL-E model needs twenty-three numbers off them, and those numbers used to
//  be typed into cad/walle_frame.scad as plain constants. That is a copy, and
//  a copy of a measurement always ends up disagreeing with the original.
//
//  So they live here, once, and both the WALL-E model and the checker read
//  them from here.
//
//  WHICH POD REVISION? THE NEWEST ONE ON DISK, ALWAYS.
//  pod_latest.sh writes pod_latest.scad, which includes the highest
//  archive/revNNN-*/apollo_track_pod_revNNN.scad. check_pod_interface.scad
//  reads that, so nothing here is ever pinned to an old revision by hand.
//  To repeat the comparison:
//      cd WALL-E && ./pod_latest.sh
//      openscad -o check.echo --export-format echo check_pod_interface.scad
//
//  VERIFIED 2026-09-22 against rev013-double-shear: all 23 agree.
//  (Before that date the z stack below was rev012's, and it was wrong by up to
//  18.5 mm per side. The checker caught it, which is why the checker exists.)
//
//  COORDINATES, pod-local
//    x  fore and aft.   x = 0 is the HUB AXLE. Forward is -x.
//    y  up.             y = 0 is the GROUND.
//    z  left and right. z = 0 is the pod's centre plane.
//
// ============================================================================

// ---- the z stack, outward from the pod centre ------------------------------
// Read this in full. The order CHANGED in rev013 and the names are historical:
//
//     0 .. 59    belt            (track_w 118 wide, so +-59)
//  76.5 .. 82.5  GREEN plate     (gp_t 6. rev013 gp_z0 = cz - gp_t)
//  82.5 .. 88.5  CARRIER plate   (carrier_t 6. rev013 cz, MEASURED 2026-09-18:
//                                 165 clear between the two carriers)
//  88.5 .. 92.5  fork leg        (fork_gap 177, so the legs' inner faces are
//                                 at 88.5. leg_t 4. These are the SCOOTER's
//                                 fork legs, bolted to the carrier's outer
//                                 face. WALL-E does not use them.)
//
//  WHAT CHANGED, and why it matters more than the numbers:
//  In rev012 the green plate was the OUTERMOST part, sitting on top of the
//  carrier at 80..86, and the WALL-E rail bolted flat onto its face. Rev013
//  measured the built pods and the plate is INBOARD of the carrier, at
//  76.5..82.5 — so the carrier now stands 6 mm PROUD of the plate.
//  A rail laid against the plate would foul the carrier. See pod_mount_z.
pod_belt_hw   = 59;      // rev013 track_w/2
pod_gp_zi     = 76.5;    // rev013 gp_z0 = cz - gp_t   green plate INNER face
pod_gp_t      = 6;       // rev013 gp_t
pod_gp_zo     = 82.5;    // = pod_gp_zi + pod_gp_t. The plate's other face
pod_carr_zi   = 82.5;    // rev013 cz               MEASURED 2026-09-18
pod_carr_t    = 6;       // rev013 carrier_t
pod_leg_zi    = 88.5;    // rev013 fork_gap/2 = 177/2
pod_leg_t     = 4;       // rev013 leg_t            MEASURED 2026-07-13

// ---- heights above the ground ----------------------------------------------
pod_hub_h     = 216;     // rev013 hub_h = B + D/2 + T
pod_top       = 327;     // rev013 pod_top = hub_h + pitch_r + T/2 = 327.04
pod_gp_yc     = 227;     // rev013 hub_h + gp_yc (gp_yc = 11, above the AXLE)
pod_gp_w      = 60;      // rev013 gp_w -> the band runs 197 .. 257
pod_fr_top    = 257;     // rev013 fr_top = hub_h + gp_yc + gp_w/2

// ---- the belt loop ---------------------------------------------------------
pod_A         = 231.2;   // rev013 solved A = 231.155. GROUND CONTACT LENGTH
pod_B         = 150;     // rev013 B, hub centre above the idler axle line
pod_idler_d   = 108;     // rev013 D
pod_T         = 12;      // rev013 T, belt carcass thickness
pod_pitch_r   = 105.04;  // rev013 pitch_r = 105.042, sprocket cord radius
pod_belt_w    = 118;     // rev013 track_w
pod_halfl     = 181.6;   // = (A + idler_d + 2*T)/2 = 181.58 -> 363.2 overall

// ---- the M12 holes, ALREADY DRILLED ----------------------------------------
// rev013 rl_bolts = [gp_x0 + gp_end_edge, rl_end_x - rl_end_edge] = [-168, -108]
// Pod-local x, so 108 and 168 FORWARD of the hub axle. They are in the GREEN
// PLATE only — the carrier has no such hole, and drilling one is not allowed.
// WALL-E reuses these two holes per side so that NO NEW HOLE goes into a built
// pod.
pod_bolt_x    = [-168, -108];
pod_bolt_d    = 12;      // M12 10.9

// ---- the carrier strip's footprint, for clash checks ------------------------
// rev013 carrier_2d: 40 wide on the hub axle (x -20..+20), running from 24
// below the pivot up to axle+68 — so it crosses the whole 197..257 rail band.
// The rail cannot dodge it vertically.
pod_carr_x    = [-20, 20];

// ============================================================================
//  THE MOUNTING FACE — the one decision everything downstream hangs on
// ============================================================================
//
//  The rail comes from the robot's centre, outward, and meets (in this order):
//      82.5   the green plate's face          <- the M12 holes are here
//      88.5   the carrier's outer face        <- 6 mm further out, no holes
//      92.5   the scooter fork leg's face     <- not fitted on WALL-E
//
//  So the rail STOPS ON THE CARRIER at 88.5, and there is a 6 mm air gap
//  between the rail and the green plate where the bolts pass. That gap gets a
//  PACKER: a 60x6 offcut, same stock as the plate, one per side, drilled Ø13
//  at the two M12 centres. Bolt order, inboard to outboard:
//      M12 head -> rail inner wall -> rail outer wall -> PACKER 6 ->
//      green plate 6 -> weld nut on the plate's far face.
//  Without the packer the bolts would crush the rail wall into the gap and the
//  joint would have no clamp at all.
//
//  This replaces the old "does the green plate exist?" question. It does exist,
//  it is inboard, and it is no longer the face the rail touches.
pod_has_green_plate = true;    // confirmed by rev013's measured stack

// the face the WALL-E rail actually bolts to
pod_mount_z   = pod_carr_zi + pod_carr_t;      // 88.5 — carrier OUTER face
// the shim that fills rail-to-plate at the bolts
pod_packer_t  = pod_mount_z - pod_gp_zo;       // 6

// ============================================================================
//  ONE CAUTION LEFT
// ============================================================================
//
//  THE GREEN PLATES ARE NOT SYMMETRIC. In rev013 they are:
//    +z (trailing) plate:  x = -188 .. +72   (260 long)
//    -z (leading)  plate:  x = -188 .. +20   (208 long)
//  The +z plate is longer because it carries the rear shock eye. Both plates
//  cover both M12 holes (-168 and -108 are inside -188..+20), so the frame
//  bolts up either way and this does NOT affect the mounting. It matters only
//  for the render and for which way round a pod goes. cad/walle_frame.scad
//  draws them symmetric and places the pods by translation rather than by
//  mirroring, so one pod's long plate faces inboard and the other's faces
//  outboard. Cosmetic today. Fix it before anyone uses the model to decide
//  handedness.
