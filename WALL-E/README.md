# WALL-E

A two-track robot built from the two Rev 012 track pods, for Midburn in the Negev desert.

This folder holds everything for the robot: the documents, the code for three small
computers, and the CAD for the frame. Nothing in here changes the scooter project.
The scooter work stays in `../archive/`.

---

## What we are building

Take the two track pods that were designed for the scooter. Instead of putting them one
behind the other like a motorbike, put them **side by side**, left and right. Then there is
no steering fork at all. To turn, you drive the left track faster than the right track. A
digger and a tank turn this way. WALL-E turns this way too.

On top of the two pods sits a box. Inside the box are the batteries, three small computers,
and two speakers. On top of the box is WALL-E's head, with two screens for eyes.

### How it is driven

A person holds a radio remote control and drives it. This is called **teleoperation**, or
teleop for short. The robot is *not* self-driving.

But the robot is not stupid either. Two things run on their own:

1. **A safety layer.** Sensors watch for obstacles. If something is close, the robot refuses
   to drive into it, even if the driver pushes the stick that way.
2. **A personality layer.** A camera finds people's faces. The eyes look at them. The head
   tilts. Sounds play. This is the part that makes people smile, and it is the reason to
   build the robot at all.

We chose this on purpose. A fully self-driving robot in a crowd of thousands of people, at
night, in dust, is both dangerous and much more work. And nobody in the crowd would even
notice good navigation. They *will* notice eyes that follow them.

---

## The three computers

The most important idea in this whole project: **do not use one computer.** Use three.

The three jobs have completely different speed requirements. Mixing them makes the robot
unsafe.

| Name | Board | Job | How fast must it be |
|---|---|---|---|
| **Brain** | Jetson Orin Nano | Camera, AI, sounds, deciding | Slow is fine: 0.1 to 3 seconds |
| **Spine** | Teensy 4.1 | Reads the remote, talks to the motors | Very fast and exact: 1000 times a second |
| **Face** | ESP32-S3 | The two eye screens and servos | Steady: 30 times a second |

The **Brain** runs Linux, like a normal computer. Linux is good at big jobs like AI, but it
has no promise about timing. It can freeze for two seconds and nobody notices. That is
fine for a camera. It is *not* fine for motors.

The **Spine** runs no operating system at all. Just one small program in a loop. It cannot
freeze. It holds the emergency rules. If the Brain stops talking to it, the Spine stops the
motors by itself.

The radio receiver and the emergency stop wire into the **Spine**, not into the Brain. So if
the Brain crashes, the driver keeps full control of the robot. You lose the eyes and the
sounds, and that is all.

The **Face** is separate so the eyes keep moving smoothly even when the Brain is busy. An
eye that stutters looks broken and ruins the illusion instantly.

---

## Folder guide

```
WALL-E/
  README.md                  <- you are here
  docs/
    00-plan.md               The master plan: status, phases, budget, schedule, risks
    01-architecture.md       How the three computers work together, and the safety rules
    02-shock-bolt.md         The one open problem in the built pods, and how to fix it
    03-safety-log.md         The safety test record. Fill in by hand before going near people
    04-power-and-wiring.md   Every wire, every fuse, and the emergency stop chain
    05-bom.md                What to buy, what it costs, how long it takes to arrive
    99-glossary.md           Every technical word used here, explained simply
  firmware/
    README.md                How to build and flash both boards, and how to test them
    spine/                   The Spine: motor commands and every safety rule
    face/                    The Face: eye animation. One board per eye
  brain/
    README.md                How to run it, and the three load-bearing ideas in it
    main.py                  The 20 Hz control loop
    test_safety.py           Invariant checks. Runs with no dependencies
  cad/
    walle_frame.scad         The whole robot. Parametric, with 33 guards
    walle_robot_*.png        The robot with body and head
    walle_head.png           The eye barrels
    walle_shelf.png          The electronics layout, labelled
    walle_frame_*.png        The bare frame, and the plywood cutting layout
```

---

## The model

`cad/walle_frame.scad` is the whole robot: the frame, the two pods, the batteries, the body,
the head and the electronics layout. Run it and it prints every dimension, the cut list, the
tipping angles, and 33 checks that all have to pass.

```bash
openscad -o walle.stl -D 'render_mode="robot"'    cad/walle_frame.scad   # everything
openscad -o steel.stl -D 'render_mode="frame"'    cad/walle_frame.scad   # steel only, for welding
openscad -o cut.dxf   -D 'render_mode="plates"'   cad/walle_frame.scad   # plywood, flat
openscad -o head.stl  -D 'render_mode="head"'     cad/walle_frame.scad   # the eye barrels
openscad -o sec.stl   -D 'render_mode="section"'  cad/walle_frame.scad   # cut open
```

![the robot, three quarter view](cad/walle_robot_3q.png)

From the front. The body is narrower than the track span on purpose, so the pods stay proud
at the sides — that is what makes the silhouette read as WALL-E rather than as a box on
wheels.

![front view](cad/walle_robot_front.png)

| Headline number | Value |
|---|---|
| Overall width | 700 mm (pods 500 apart, green plates stick out 100 each side) |
| Overall height | 910 mm, to the top of the eye barrels |
| Body | 430 long × 620 wide × 400 tall, floor at 335 mm |
| Rails | 60×30×3 box, 550 long, 240 mm clear between them |
| Lowest point of the robot | 150 mm above the ground |
| Whole robot, estimated | 91 kg — **every mass in the model is still a guess** |
| Centre of mass | 332 mm above the ground, centred over the tracks |
| Ground pressure | 0.167 kg/cm² over 546 cm² |
| Tips forward at | 19.4° of pitch |
| Anti-tip castor catches at | 9.9° — so it catches 9° before the robot goes over |
| Steel needed | 1580 mm of 60×30×3 box tube |

**The pod comes off with two bolts per side.** The frame reuses the four M12 holes that are
already drilled in the green plates, so no new holes go into the built pods.

The tipping numbers are only as good as the mass guesses feeding them. Weigh a pod, weigh a
pack, and put the real numbers in the model before trusting 19.4°.

### Two things the model settled

**There is no room for electronics in the frame.** The interior is almost entirely battery:
8 mm above the packs, 24 mm between them, 13 mm to the cross members. So everything moved
onto a shelf inside the body. It fits four rows and uses 32 % of the shelf area, which
leaves room for the speakers and an air path.

![the electronics shelf](cad/walle_shelf.png)

**The body floor has to clear the belt crown, not the frame.** The pods are 327 mm tall at
the top of the belt but the frame only reaches 257, so the body sits on four risers 78 mm
tall. Miss this and the shell grinds on a moving belt.

### The head

Two 105 mm barrels, 128 mm apart, toed in 6°, each with a 2.1 inch round screen recessed
60 mm behind a clear dome.

![the head](cad/walle_head.png)

The recess is not styling, it is a sun shade: a screen that deep behind a 53 mm aperture is
in shadow for any sun above 49° elevation, and Negev midday sun is 75–80°. The dome seals
the barrel against dust.

**New to this? Read in this order:** `99-glossary.md`, then `00-plan.md`, then
`01-architecture.md`. Do not start buying parts until you have read the plan, because the
parts list only makes sense after it.

---

## What we already have

**Both pods are built, to Rev 012.** The belts are fitted and both hub motors are in hand,
along with the original scooter controllers. Nothing electronic exists yet, and the frame that
holds the two pods side by side has not been designed — that is the first job.

These numbers come from the Rev 012 model, which the pods were built to. Confirm the first one
with a tape measure before the frame is welded, because it is the dimension the frame has to
match.

| Thing | Value |
|---|---|
| **Carrier plate spacing — the frame mounting width** | **168 mm** |
| Ground contact, one pod | 231 mm long × 118 mm wide |
| Pod size | 363 long × 327 tall × ~200 wide |
| Where the pod bolts to the frame | A plate 60 mm tall, 197–257 mm above the ground |
| Suspension travel | +30.7 mm up, −29.2 mm down |
| Ground pressure at 100 kg total | 0.18 kg/cm² |
| Belt movement per motor turn | 660 mm |

See `../archive/rev012-inline-batteries/` for where these come from.

That last ground pressure number is worth understanding. Your own foot presses the ground at
roughly 0.5 kg/cm². This robot, at 100 kg, presses **less than a third as hard as a walking
person**. That is why tracks are the right choice for desert sand, not just a nice look.

---

## Open questions

Full list with deadlines in `docs/00-plan.md` section 4. The three that matter most:

1. **The lower shock bolt.** The pods were built with a known weak point: the bolt holding
   each shock's lower end bends past its limit at full suspension travel. It is fine standing
   still and the fix is cheap, but it must be done before the pods carry the full robot. Read
   `docs/02-shock-bolt.md`.
2. **Does WALL-E carry a person?** If yes, the frame is heavier and it must be registered as
   a mutant vehicle with Midburn. Check the current Midburn rules before the frame is welded.
3. **How do we stop it tipping forward?** The pods put only 231 mm of track on the ground, so
   that is the robot's whole front-to-back footprint. Longer belts are no longer an option
   now the pods are assembled, so the plan is anti-tip wheels plus keeping every heavy thing
   as low as possible.
