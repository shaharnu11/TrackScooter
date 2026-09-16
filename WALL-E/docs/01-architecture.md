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
| 4 | **Are BOTH VESCs reporting on CAN?** | **Ramp BOTH to zero.** | See section 3b. One dead track does not stop a skid-steer robot, it makes it pivot. |
| 5 | **Are both pack voltages above the floor?** | **Ramp BOTH to zero.** | A BMS cutting out is the most likely way one side dies. |
| 6 | Which mode does the remote's mode switch say? | — | `MANUAL` uses the sticks. `ASSIST` uses the Brain. |
| 7 | In `ASSIST` only: has a Brain heartbeat arrived in the last 100 ms? | Ramp to zero and fall back to `MANUAL`. | The Brain is frozen or rebooting. |
| 8 | Do the bumper sensors see anything close in the direction of travel? | Scale the command down, or to zero. | The veto. It can only reduce, never add. |
| 9 | Is either motor too hot? | Scale both commands down. | Protects the hub motors from overheating at low speed. |
| 10 | Apply the slew rate limit. | — | Turns any sudden change into a smooth ramp. |
| 11 | **Scale each side by its own pack voltage.** | — | See section 3b. Keeps it driving straight as the two packs drift apart. |
| 12 | Send on CAN. | — | |

### The important property of this list

Every single failure leads to the robot stopping. There is no combination of broken parts
that makes it speed up, turn unexpectedly, or ignore the driver. When you are unsure whether
a design is safe, check it against this: **ask what each part does when it breaks, not when
it works.**

---

## 3b. One battery per pod, and the three traps that come with it

We have two 48 V packs, and each one feeds its own pod: left pack to the left VESC, right pack
to the right VESC. The positives stay completely separate.

This is a good decision. It removes the worst problem with two packs, which is connecting them
in parallel. Two packs at different states of charge, joined together, dump a very large
current into each other the moment you connect them. Keeping the positives separate means that
can never happen, and each pack keeps its own BMS working independently.

But splitting the power this way creates three problems that have to be designed for.

### Trap 1 — It will drive crooked as the packs drift apart

Skid steer only works if the left and right sides respond the same way to the same command.
A duty cycle command means "apply this fraction of the pack voltage to the motor". So if one
pack is at 50 V and the other at 44 V, the same stick position makes one track about 12 %
faster than the other, and the robot pulls to one side the whole time.

The packs **will** drift apart, for three reasons: every turn loads the outer track harder
than the inner one, the two packs will not be equally healthy, and one of them is also feeding
the electronics.

**The fix (arbitration rule 11):** the VESCs already report their input voltage over CAN, and
the Spine is already listening. So the Spine scales each side's command by that side's own pack
voltage, aiming for the same volts at each motor rather than the same fraction. In code this is
one multiplication per side, and it makes the problem disappear.

### Trap 2 — One dead side makes the robot pivot, not stop

This is the dangerous one, and it is easy to miss.

On a car, losing drive to one wheel means you slow down. On a skid-steer machine, losing one
track means **the other track keeps pushing and the robot spins on the spot.** In a crowd, a
heavy machine that suddenly starts turning instead of stopping is exactly what you do not want.

The most likely cause is not a broken wire. It is one pack's **BMS cutting out** — from low
voltage, over-current, or over-temperature — which it is designed to do, without warning, on
its own.

**The fix (arbitration rules 4 and 5):** the Spine requires both VESCs to be reporting on CAN
and both pack voltages to be above a floor. If either check fails, it ramps **both** sides to
zero. Never one.

### Trap 3 — The two packs need a shared ground, or CAN will not work

Two separate packs have two separate negative terminals. The CAN bus connecting the Spine to
both VESCs needs one common zero-volt reference, and without it the two ends of the bus float
against each other and the data is meaningless.

**The fix: bond the two pack negatives together at one single point, and keep the two positives
separate.** Each pack then returns its own current through the shared negative, but there is no
path between the positives, so the cross-charging problem in the opening paragraph still cannot
happen.

Two details on that bond:

- Size it for the larger of the two motor currents, and keep it short and thick. It is
  carrying real current, not just a reference.
- **Do not fuse it.** A fuse that opens in the ground bond leaves the CAN bus floating while
  the robot is still driving, which is worse than the fault it was protecting against.

### The electronics supply: the larger pack, and why that is the right choice

The two packs are **not the same capacity**. The electronics run from the larger one, through
one isolated DC-DC converter.

This is better than it first looks. Mismatched capacities are a problem on their own: with the
same motor current on both sides, the smaller pack empties sooner, so the two voltages diverge
faster and trap 1 gets worse. And because rules 4 and 5 stop the robot when either side drops
out, **the runtime of the whole robot is set by the smaller pack, not the average.**

Putting the electronics load on the larger pack drains it faster on purpose, which pushes the
two packs towards emptying at the same moment. The load you want is:

```
electronics current  =  motor current per side  ×  ( larger capacity / smaller capacity − 1 )
```

A worked example. Say the packs are 20 Ah and 15 Ah, and each side pulls about 3.1 A on
average while crawling:

| | Capacity | Current drawn | Runtime |
|---|---|---|---|
| Larger pack: left motor + all electronics | 20 Ah | 3.1 + 1.15 = 4.25 A | 4.7 hours |
| Smaller pack: right motor only | 15 Ah | 3.1 A | 4.8 hours |

The two land within a few minutes of each other, which is as good as it gets. Fill in the real
capacities and check where yours land — if the mismatch is much bigger than 4:3, the
electronics load will not be enough to even it out, and the smaller pack becomes the limit.

### The consequence that must be tested

Running the electronics from one pack means **the Spine dies when that pack dies.** So the
chain of events if the larger pack's BMS cuts out is:

1. The Spine loses power and stops sending CAN commands.
2. The other VESC still has power, from the smaller pack.
3. Arbitration rules 4 and 5 cannot help, because the board that enforces them is off.

The robot is then relying entirely on **the VESC's own command timeout**: if no command
arrives for about a second, a VESC releases the motor and lets it coast. That behaviour is what
stops the robot pivoting on its surviving track.

So this becomes a critical configuration item rather than a detail:

- Set the command timeout explicitly in both VESCs. Do not assume the default is what you
  want, and do not assume it is enabled.
- Test it, as safety log test 15: cut power to the Spine while the robot is driving, and
  confirm the surviving track releases within a second and the robot does not turn.
- Keep a buffer capacitor on the electronics rail anyway. That is for risk R6, the motor
  current spikes, and it is needed whichever pack the supply comes from.

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
