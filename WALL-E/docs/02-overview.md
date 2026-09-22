# 02 — What this robot is

A two-track robot built from the two track pods in `../archive/`, for Midburn in the Negev
desert. The pods are **built already**. Nothing in this project changes them.

Take the two track pods that were designed for the scooter. Instead of putting them one
behind the other like a motorbike, put them **side by side**, left and right. Then there is
no steering fork at all. To turn, you drive the left track faster than the right track. A
digger and a tank turn this way. WALL-E turns this way too.

On top of the two pods sits a box. Inside the box are the batteries, three small computers,
and two speakers. On top of the box is WALL-E's head, with two screens for eyes.

![The robot, three quarter view](fig/walle_robot_3q.png)

## How it is driven

A person holds a radio remote control and drives it. This is called **teleoperation**, or
teleop for short. The robot is *not* self-driving.

But the robot is not stupid either. Two things run on their own:

1. **A safety layer.** Sensors watch for obstacles. If something is close, the robot refuses
   to drive into it, even if the driver pushes the stick that way.
2. **A personality layer.** A camera finds people's faces. The eyes look at them, and the
   whole robot turns slowly to face them, because the head is rigid and does not move on its
   own. Sounds play. This is the part that makes people smile, and it is the reason to build
   the robot at all.

We chose this on purpose. A fully self-driving robot in a crowd of thousands of people, at
night, in dust, is both dangerous and much more work. And nobody in the crowd would even
notice good navigation. They *will* notice eyes that follow them.

## The three computers

The most important idea in this whole project: **do not use one computer.** Use three.

The three jobs have completely different speed requirements. Mixing them makes the robot
unsafe.

| Name | Board | Job | How fast must it be |
|---|---|---|---|
| **Brain** | Jetson Orin Nano | Camera, AI, sounds, deciding | Slow is fine: 0.1 to 3 seconds |
| **Spine** | Teensy 4.0 | Reads the remote, talks to the motors | Very fast and exact: 1000 times a second |
| **Face** | ESP32-S3 | The two eye screens. No servos — the head is rigid | Steady: 30 times a second |

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

## The headline numbers

The body is narrower than the track span on purpose, so the pods stay proud at the sides —
that is what makes the silhouette read as WALL-E rather than as a box on wheels.

![From the front](fig/walle_robot_front.png)

| Headline number | Value |
|---|---|
| Overall width | 677 mm (pods 500 apart, the pods stick out either side) |
| Overall height | 910 mm, to the top of the eye barrels |
| Body | 430 long × 620 wide × 400 tall, floor at 335 mm |
| Rails | 60×30×3 box, 550 long, 263 mm clear between them |
| Lowest point of the robot | 150 mm above the ground |
| Whole robot | 88.9 kg — **the pods, packs and electronics are still guesses** |
| Centre of mass | 318.2 mm up, and 4.4 mm forward of centre — the chest speakers |
| Ground pressure | 0.163 kg/cm² over 546 cm² |
| Tips forward at | 19.3° of pitch (backward 20.7°) |
| Anti-tip castor catches at | 12.3° — so it catches 7.0° before the robot goes over |
| Steel needed | 1580 mm of 60×30×3 box tube |

**The pod comes off with two bolts per side.** The frame reuses the four M12 holes that are
already drilled in the green plates, so no new holes go into the built pods. The rail itself
lands on the carrier, which stands 6 mm proud of the plate, so each side needs a 6 mm packer
under the bolts. Part 5 has that stack, part by part.

The tipping numbers are only as good as the mass guesses feeding them. Weigh a pod, weigh a
pack, and put the real numbers in the model before trusting 19.3°.

## Four things the model settled

**There is no room for electronics in the frame.** The interior is almost entirely battery:
8 mm above the packs, 24 mm between them, 13 mm to the cross members. So everything moved
onto a shelf inside the body. It fits four rows and uses 40 % of the shelf area, which
leaves room for the speakers and an air path.

![The electronics shelf, labelled](fig/walle_shelf.png)

**The body floor has to clear the belt crown, not the frame.** The pods are 327 mm tall at
the top of the belt but the frame only reaches 257, so the body sits on four risers 78 mm
tall. Miss this and the shell grinds on a moving belt.

**The battery box has to be a closed box, and it was not one.** It was a three-sided U,
open across the top and at both ends, hanging right where the belts throw sand. It is now
six panels with a gasketed lid, plugs in the spanner holes, and a membrane vent — a sealed
box breathes with the day/night temperature swing and pulls dust in through its worst leak,
so it needs a clean air path. The packs charge in place through a connector on the outside
of the body and never come out in the field.

![The plywood cutting layout](fig/walle_frame_plates.png)

**The chest panel was a hole, not a panel.** `chest_d` recesses the chest 20 mm into a
12 mm wall, so the recess cut the front wall clean away and you could see the electronics
through WALL-E's chest. It is now a real 12 mm plate set back 20 mm — which is lucky,
because that plate is exactly what the speakers needed to mount to.

## The speakers

Two 6.5 inch drivers in the chest panel, 280 mm apart, 584 mm above the ground. That is how
WALL-E talks and plays music.

**Each driver gets its own sealed plywood enclosure, 9.8 litres.** They do not fire into
the body, and that is deliberate. The body is not airtight — it has a filtered air intake,
a removable lid and cable entries — so an open back would chuff and lose all its bass. And
100 W of pressure swinging around the electronics bay shakes every connector on the shelf.

![The chest panel and the two sealed enclosures, from behind](fig/walle_chest.png)

Two things the model flagged that are easy to miss:

**The enclosures shade 54 % of the electronics shelf.** They clear it by 20 mm, so nothing
clashes, but they sit above it. So they **bolt** to the chest panel — glue them in and
half the electronics becomes unreachable.

**They cost about 1.5° of forward tipping margin.** 7.3 kg at 584 mm, and both of them forward
of centre, which pulls the centre of mass 4.4 mm towards the direction the robot already tips.
With them fitted the robot tips forward at 19.3°, and the castor still catches 7.0° before
that. It passes, but the speakers are one of several things pushing that number down, so weigh
the real parts before adding another.

## The head

Two 105 mm barrels, 128 mm apart, toed in 6°, each with a 2.1 inch round screen recessed
60 mm behind a clear dome.

![The head, with the two eye barrels](fig/walle_head.png)

The recess is not styling, it is a sun shade: a screen that deep behind a 53 mm aperture is
in shadow for any sun above 49° elevation, and Negev midday sun is 75–80°. The dome seals
the barrel against dust.

## What we already have

**Both pods are built.** The belts are fitted and both hub motors are in hand, along with the
original scooter controllers. Nothing electronic exists yet, and the frame that holds the two
pods side by side has not been welded — that is the first job.

These numbers were measured on the built pods and are carried by the newest pod revision,
rev013. Confirm the first one with a tape measure before the frame is welded, because it is
the dimension the frame has to match.

| Thing | Value |
|---|---|
| **Carrier outer faces — the frame mounting width** | **177 mm** (green plates 165 mm, 6 mm further in — that step is the packer) |
| Ground contact, one pod | 231 mm long × 118 mm wide |
| Pod size | 363 long × 327 tall × 177 wide over the carriers |
| Where the pod bolts to the frame | A plate 60 mm tall, 197–257 mm above the ground |
| Suspension travel | +30.7 mm up, −29.2 mm down |
| Ground pressure at 100 kg total | 0.18 kg/cm² |
| Belt movement per motor turn | 660 mm |

See `../archive/rev013-double-shear/` for where these come from.

That last ground pressure number is worth understanding. Your own foot presses the ground at
roughly 0.5 kg/cm². This robot, at 100 kg, presses **less than a third as hard as a walking
person**. That is why tracks are the right choice for desert sand, not just a nice look.

## Open questions

Full list with deadlines in part 2, section 4. The three that matter most:

1. **Both pack capacities, in Ah, and are both BMS units healthy?** This sets the runtime and
   the fuse sizing. Since decision D8 gave the electronics their own battery, the two traction
   packs want to be the **same** capacity — see decision D4.
2. **Does WALL-E carry a person?** If yes, the frame is heavier and it must be registered as
   a mutant vehicle with Midburn. Check the current Midburn rules before the frame is welded.
3. **How do we stop it tipping forward?** The pods put only 231 mm of track on the ground, so
   that is the robot's whole front-to-back footprint. Longer belts are no longer an option
   now the pods are assembled, so the plan is anti-tip wheels plus keeping every heavy thing
   as low as possible.
