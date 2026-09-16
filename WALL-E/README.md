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
    04-power-and-wiring.md   Every wire, every fuse, and the emergency stop chain (to come)
    05-bom.md                What to buy, what it costs, how long it takes to arrive (to come)
    99-glossary.md           Every technical word used here, explained simply
  firmware/
    spine-teensy/            Code for the Spine (the motor board)
    face-esp32/              Code for the Face (the eye board)
  brain/                     Code for the Brain (Python, on the Jetson)
  cad/                       OpenSCAD model of the side-by-side frame
```

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
