# 01 — Architecture

How the three boards fit together, and the rules that decide who is allowed to move the
robot. Read `99-glossary.md` first if any word here is unfamiliar.

This is the most important document in the project. Everything else follows from it.

---

## 1. The core decision: three boards, not one

The natural instinct is to buy one powerful computer and let it do everything: read the
camera, run the AI, and drive the motors. **Do not do this.** It is the main way projects
like this become dangerous.

The reason is timing. The three jobs have completely different needs:

| Job | Must react within | What happens if it is late |
|---|---|---|
| Stop the motors | 1 millisecond | Somebody gets hurt |
| Animate the eyes | 30 milliseconds | The face stutters and looks broken |
| Understand a camera frame | 100 milliseconds | Nothing, nobody notices |
| Decide what to say | 3 seconds | Nothing, it feels natural |

A Linux computer cannot promise one millisecond. Linux is allowed to pause your program
whenever it wants, to do something else. Normally the pause is tiny. Occasionally it is two
full seconds. You cannot prevent this and you cannot predict it.

Two seconds of a 200 kg machine continuing at its last speed, in a crowd, is unacceptable.
So the motor commands live on a board that has no operating system and therefore cannot
pause.

---

## 2. The layout

```
        ┌────────────────┐
        │  RADIO REMOTE  │   The driver. A normal RC transmitter.
        │  in a human's  │
        │     hands      │
        └───────┬────────┘
                │  radio, 2.4 GHz
                ▼
   ┌─────────────────────────┐
   │   RC RECEIVER           │
   └───────────┬─────────────┘
               │ iBus serial
               │
  SENSE        ▼                                   FACE
┌─────────┐  ┌──────────────────────┐   USB    ┌──────────────┐
│ LiDAR   │  │                      │  serial  │  ESP32-S3    │
│ OAK-D   ├─►│   BRAIN              ├─────────►│  2 LCD eyes  │
│ GPS     │  │   Jetson Orin Nano   │          │  2 servos    │
│ mic     │  │   Linux              │          └──────────────┘
└─────────┘  │                      │
             │  camera, AI, sound   │      Can freeze. That is allowed.
             └──────────┬───────────┘
                        │ USB serial, 20 Hz
                        │ commands + heartbeat
                        ▼
  SAFETY     ┌──────────────────────┐
┌──────────┐ │                      │
│ ToF ring │ │   SPINE              │
│ bumper   ├►│   Teensy 4.1         │◄── RC receiver also wires in HERE
│ switch   │ │   no operating system│
└──────────┘ │                      │
             │  mixing, ramping,    │      Cannot freeze. Holds every rule.
             │  watchdog, limits    │
             └──────────┬───────────┘
                        │ CAN bus, 500 kbit
             ┌──────────┴──────────┐
             ▼                     ▼
      ┌─────────────┐       ┌─────────────┐
      │ VESC left   │       │ VESC right  │
      └──────┬──────┘       └──────┬──────┘
             ▼                     ▼
      ┌─────────────┐       ┌─────────────┐
      │ hub motor   │       │ hub motor   │
      │ left pod    │       │ right pod   │
      └─────────────┘       └─────────────┘
```

### Two things in that diagram matter more than the rest

**The radio receiver wires into the Spine, not into the Brain.** This means the driver keeps
full control of the robot even if the Jetson is switched off, crashed, or still booting. If
the radio went through the Brain, a Linux crash would take away the driver's steering at the
worst possible moment. Instead, a Brain crash costs you the eyes and the sounds, and the
robot still drives normally.

**The bumper sensors wire into the Spine too.** Same reason. The last line of defence must
not depend on the most complicated part of the machine.

---

## 3. Who is allowed to move the robot

The Spine runs one loop, 1000 times a second. Every pass through the loop, it decides the
motor commands from scratch using this fixed order. A rule higher in the list always beats a
rule lower down.

| # | Check | If it fails | Why |
|---|---|---|---|
| 1 | Is the E-stop circuit closed? | Motors dead. Nothing can override. | This is physical, not software. The contactor is open, so there is no power to the motors at all. |
| 2 | Is the arm switch on the remote ON? | Send zero. | The robot must never move the instant you connect the battery. The driver has to deliberately arm it. |
| 3 | Has a radio frame arrived in the last 100 ms? | Ramp to zero. | Radio out of range or transmitter battery flat. Stop is the only safe answer. |
| 4 | Which mode does the remote's mode switch say? | — | `MANUAL` uses the sticks. `ASSIST` uses the Brain. |
| 5 | In `ASSIST` only: has a Brain heartbeat arrived in the last 100 ms? | Ramp to zero and fall back to `MANUAL`. | The Brain is frozen or rebooting. |
| 6 | Do the bumper sensors see anything close in the direction of travel? | Scale the command down, or to zero. | The veto. It can only reduce, never add. |
| 7 | Is either motor too hot? | Scale both commands down. | Protects the hub motors from overheating at low speed. |
| 8 | Apply the slew rate limit. | — | Turns any sudden change into a smooth ramp. |
| 9 | Send on CAN. | — | |

### The important property of this list

Every single failure leads to the robot stopping. There is no combination of broken parts
that makes it speed up, turn unexpectedly, or ignore the driver. When you are unsure whether
a design is safe, check it against this: **ask what each part does when it breaks, not when
it works.**

---

## 4. The watchdog, in detail

This deserves its own section because it is easy to skip and it is the feature that matters
most.

The Brain sends a small message to the Spine 20 times a second, so one every 50 ms. The
message contains the requested speed and turn, plus a counter that goes up by one each time.

The Spine remembers when the last message arrived. Every loop it checks: *was it less than
100 ms ago?*

- **Yes** — carry on normally.
- **No** — the Brain is considered dead. Ramp both motors to zero over 0.5 seconds and stop
  obeying the Brain until fresh messages come back for a full second.

Note what this does **not** do: it does not slam the brakes. A sudden stop on a tall robot
could tip it forward. Ramping down over half a second stops it safely without pitching it
over.

Note also that in `MANUAL` mode a dead Brain does not stop the robot at all, because the
driver's sticks come straight into the Spine. The Brain's heartbeat only gates the Brain's
own authority.

---

## 5. What each board actually runs

### Brain — Jetson Orin Nano, Linux, Python

Four things, all independent, all allowed to be slow:

1. **Obstacle map.** Read the LiDAR, build an occupancy grid, work out which directions are
   blocked. This is not AI. It is geometry, and it is fully predictable.
2. **People detection.** The OAK-D camera runs a YOLO model on its own chip, so the Jetson
   gets a ready-made list of where people are without spending any effort. Output is simple:
   "person at 20 degrees left, 3 metres away."
3. **Personality.** A state machine picks a behaviour: idle, curious, greeting, shy,
   retreating. It sends gaze targets to the Face and plays sound clips. Optionally an LLM
   chooses the behaviour instead of fixed rules, but see the warning below.
4. **Logging.** Record motor temperature, battery voltage, and any veto events to a file.
   You will need this after the first time something goes wrong in the field.

> **The AI never drives.**
> The personality layer chooses from a short fixed list: `idle`, `look_at`, `greet`,
> `retreat`, `play_sound`, `nudge_forward`. A plain reliable program turns the choice into
> motion, and the safety layer can cancel it at any moment. The AI never produces a motor
> number. This is what makes it safe to put a language model on a heavy machine.

### Spine — Teensy 4.1, C++, no operating system

One loop at 1 kHz that does exactly what section 3 describes. Nothing else. No logging to SD
card, no screens, no clever features. Every line of code added here is a line that can stop
the robot from stopping.

It also reads the VESC status messages that arrive on CAN anyway, and forwards motor
temperature and battery voltage up to the Brain.

### Face — ESP32-S3, C++

Receives short intent messages from the Brain, such as `GAZE 20 -5` or `MOOD curious`, and
then runs the animation itself: pupil movement, blinking, and the barrel tilt servos.

The Brain says *what to feel*. The Face decides *how to show it*. This split is why the face
stays smooth while the Brain is busy, and it means you can develop and test the head with
the Brain unplugged.

---

## 6. Modes the driver can select

Two positions on a switch on the remote:

**MANUAL** — the sticks drive the tracks directly. The bumper veto and the temperature limit
still apply, because those are in the Spine. The Brain is purely cosmetic in this mode: the
eyes still follow people and the sounds still play, but it cannot move the robot at all.

This is the mode to use in a crowd.

**ASSIST** — the Brain may also request movement, for behaviours like slowly turning towards
a person who is talking. The driver's stick still overrides instantly: any stick input above
a small deadband takes priority over the Brain for the next two seconds.

Start with `MANUAL` working perfectly. Only build `ASSIST` once you trust everything else.
`MANUAL` alone plus a good face is already the whole show.

---

## 7. Build and test order

Do not build this in the order of the diagram. Build it in the order that lets you test
something real at every stage.

| Stage | What you build | How you know it works |
|---|---|---|
| 1 | One VESC on a bench, one pod motor, no Teensy | The motor spins from the VESC's own configuration tool |
| 2 | Teensy sends CAN to one VESC | The motor responds to a number you type in |
| 3 | Add the RC receiver, one motor | The stick spins the motor, and it stops when you switch the transmitter off |
| 4 | Add the second VESC and mixing | Both tracks on blocks, the robot steers correctly in the air |
| 5 | Add the E-stop and the arm switch | Every one of the section 3 failures gives a stop. **Test each one on purpose.** |
| 6 | First drive, outdoors, no body, tethered E-stop | It drives and turns on sand |
| 7 | Add the bumper sensors | It refuses to drive into a cardboard box |
| 8 | Add the Face, with the Brain doing nothing else | Eyes animate and follow a hand |
| 9 | Add the camera and the personality | Eyes follow a real person across the room |
| 10 | Add the body and the sound | — |

Stage 5 is not optional and cannot be rushed. Go through the failure list in section 3 and
deliberately cause each one: pull the radio antenna, unplug the Brain's USB cable, press the
E-stop mid-drive, short the bumper sensor. If any of them does not produce a stop, the robot
is not ready to be near people.
