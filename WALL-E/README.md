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
| **Spine** | Teensy 4.1 | Talks to the motors | Very fast and exact: 1000 times a second |
| **Face** | ESP32-S3 | The two eye screens and servos | Steady: 30 times a second |

The **Brain** runs Linux, like a normal computer. Linux is good at big jobs like AI, but it
has no promise about timing. It can freeze for two seconds and nobody notices. That is
fine for a camera. It is *not* fine for motors.

The **Spine** runs no operating system at all. Just one small program in a loop. It cannot
freeze. It holds the emergency rules. If the Brain stops talking to it, the Spine stops the
motors by itself.

The **Face** is separate so the eyes keep moving smoothly even when the Brain is busy. An
eye that stutters looks broken and ruins the illusion instantly.

---

## Folder guide

```
WALL-E/
  README.md                  <- you are here
  docs/
    01-architecture.md       How the three computers work together, and the safety rules
    02-power-and-wiring.md   Every wire, every fuse, and the emergency stop chain
    03-bom.md                What to buy, what it costs, how long it takes to arrive
    99-glossary.md           Every technical word used here, explained simply
  firmware/
    spine-teensy/            Code for the Spine (the motor board)
    face-esp32/              Code for the Face (the eye board)
  brain/                     Code for the Brain (Python, on the Jetson)
  cad/                       OpenSCAD model of the side-by-side frame
```

**New to this? Read in this order:** `99-glossary.md`, then `01-architecture.md`, then
`02-power-and-wiring.md`. Do not start buying parts until you have read the architecture
document, because the parts list only makes sense after it.

---

## What we already have

These numbers come from the finished pod design. They are measured or solved, not guessed.
See `../archive/rev012-inline-batteries/` for where they come from.

| Thing | Value |
|---|---|
| Ground contact, one pod | 231 mm long × 118 mm wide |
| Pod size | 363 long × 327 tall × ~200 wide |
| Where the pod bolts to the frame | A plate 60 mm tall, 197–257 mm above the ground |
| Suspension travel | +30.7 mm up, −29.2 mm down |
| Ground pressure at 100 kg total | 0.18 kg/cm² |
| Belt movement per motor turn | 660 mm |

That last ground pressure number is worth understanding. Your own foot presses the ground at
roughly 0.5 kg/cm². This robot, at 100 kg, presses **less than a third as hard as a walking
person**. That is why tracks are the right choice for desert sand, not just a nice look.

---

## Open questions

These are decided later, and each one changes the frame. They are listed here so they do not
get forgotten.

1. **Does WALL-E carry a person?** If yes, the frame is heavier and it must be registered as
   a mutant vehicle with Midburn. Check the current Midburn rules before the frame is welded.
2. **How long is the belt?** The pods use an 18-link belt, giving 231 mm of ground contact.
   That is short, and a tall robot on a short footprint tips forward easily. A 24-link belt
   gives roughly 400 mm and is much steadier. This must be decided before the arms are cut.
3. **How is the body made?** Foam and thin plywood keeps the weight low and high up, which is
   what we want. Steel up high would make the tipping worse.
