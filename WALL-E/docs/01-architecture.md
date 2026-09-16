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
│ GPS     │  │   Jetson Orin Nano   │          │  NO SERVOS   │
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
                        │ I2C to 2 DACs, then an
                        │ opto-isolated 0-3.3 V
                        │ throttle line each
             ┌──────────┴──────────┐
             ▼                     ▼
      ┌─────────────┐       ┌─────────────┐
      │ CONTROLLER  │       │ CONTROLLER  │
      │ left, 48 V  │       │ right, 48 V │
      │ NO FEEDBACK │       │ NO FEEDBACK │
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
| 4 | **Is each track actually turning as commanded?** | **Ramp BOTH to zero.** | See section 3b. One dead track does not stop a skid-steer robot, it makes it pivot. **This rule was written for VESCs reporting on CAN. Scooter controllers report nothing — see the note below.** |
| 5 | **Are both pack voltages above the floor?** | **Ramp BOTH to zero.** | A BMS cutting out is the most likely way one side dies. **Also came off the VESC's CAN messages — see the note below.** |
| 6 | Which mode does the remote's mode switch say? | — | `MANUAL` uses the sticks. `ASSIST` uses the Brain. |
| 7 | In `ASSIST` only: has a Brain heartbeat arrived in the last 100 ms? | Ramp to zero and fall back to `MANUAL`. | The Brain is frozen or rebooting. |
| 8 | Do the bumper sensors see anything close in the direction of travel? | Scale the command down, or to zero. | The veto. It can only reduce, never add. |
| 9 | Is either motor too hot? | Scale both commands down. | Protects the hub motors from overheating at low speed. |
| 10 | Apply the slew rate limit. | — | Turns any sudden change into a smooth ramp. |

> ### Rules 4, 5 and 11 lost their data source on 2026-09-17
>
> Decision D7 changed the motor controllers from VESCs to the scooter controllers already
> owned. VESCs broadcast their status on CAN — motor current, input voltage, temperature,
> fault codes — and three arbitration rules were built on that broadcast. **Scooter
> controllers send nothing back at all.** There is no CAN bus to the motors any more.
>
> Each rule needs a new source. None is expensive, but none is automatic either:
>
> | Rule | Was | Now needs |
> |---|---|---|
> | 4 — is each track alive? | VESC reporting on CAN | **A speed sensor per track.** The hub motor's hall wires already give one, and the Teensy can count their edges. If a track is commanded to move and its halls are not changing, that track is dead. |
> | 5 and 11 — pack voltage | VESC input voltage over CAN | **A resistor divider per pack** into a Teensy analogue input. Two resistors and care with the ground reference. Cheap, but it must be on the list. |
> | 9 — is either motor too hot? | VESC motor temperature | **The hub motor's own thermistor**, read directly. This one actually got simpler — see `05-bom.md` section 1b. |
>
> **The bigger loss is the VESC command timeout.** A VESC releases the motor if no command
> arrives for about a second, and section 4 below leans on that as the last line of defence
> when the Spine dies. A scooter controller has no such behaviour: it holds whatever throttle
> voltage is on its input, forever.
>
> That defence is now **entirely** the hardware watchdog in `05-bom.md` section 1b — a relay
> with normally-closed contacts, held open by a heartbeat from the Teensy, which shorts the
> throttle to ground the moment the pulses stop. It is a single cheap part carrying a load
> that used to be shared. **Test it deliberately and often**, and treat safety log test 15 as
> mandatory rather than routine.
| 11 | **Scale each side by its own pack voltage.** | — | See section 3b. Keeps it driving straight as the two packs drift apart. |
| 12 | Send on CAN. | — | |

### The important property of this list

Every single failure leads to the robot stopping. There is no combination of broken parts
that makes it speed up, turn unexpectedly, or ignore the driver. When you are unsure whether
a design is safe, check it against this: **ask what each part does when it breaks, not when
it works.**

---

## 3b. One battery per pod, and the three traps that come with it

We have two 48 V packs, and each one feeds its own pod: left pack to the left controller, right
pack to the right controller. The positives stay completely separate.

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

**The fix (arbitration rule 11):** the Spine scales each side's command by that side's own pack
voltage, aiming for the same volts at each motor rather than the same fraction. In code this is
one multiplication per side, and it makes the problem disappear.

**Where that voltage comes from changed.** It used to be read off the VESC's CAN messages for
free. The scooter controllers report nothing, so each pack needs **a resistor divider into a
Teensy analogue input** — two resistors per pack, and care with the ground reference. Cheap,
but it is now a part you have to fit rather than a message you already have.

### Trap 2 — One dead side makes the robot pivot, not stop

This is the dangerous one, and it is easy to miss.

On a car, losing drive to one wheel means you slow down. On a skid-steer machine, losing one
track means **the other track keeps pushing and the robot spins on the spot.** In a crowd, a
heavy machine that suddenly starts turning instead of stopping is exactly what you do not want.

The most likely cause is not a broken wire. It is one pack's **BMS cutting out** — from low
voltage, over-current, or over-temperature — which it is designed to do, without warning, on
its own.

**The fix (arbitration rules 4 and 5):** the Spine requires **both tracks to be turning as
commanded** and both pack voltages to be above a floor. If either check fails, it ramps
**both** sides to zero. Never one.

"Turning as commanded" used to mean "reporting on CAN". With the scooter controllers it means
**counting the hub motor's own hall sensor edges**: if a track is commanded to move and its
halls are not changing, that track is dead. Safety log test 8 is the test for it.

### Trap 3 — The two packs need a shared ground, or nothing the Teensy measures is real

Two separate packs have two separate negative terminals. Everything the Teensy measures about
the far pack — its voltage divider, its ACS758 current sensor, its throttle line reference —
is measured against pack negative. Without one common zero-volt reference, those two negatives
float against each other and every reading from the far side is meaningless.

**This trap got worse when the VESCs went, not better.** A floating CAN bus announces itself:
the messages simply stop and rule 4 catches it. A floating analogue reference does not announce
anything. It gives you a plausible-looking wrong number, and the Spine acts on it.

**The fix: bond the two pack negatives together at one single point, and keep the two positives
separate.** Each pack then returns its own current through the shared negative, but there is no
path between the positives, so the cross-charging problem in the opening paragraph still cannot
happen.

Two details on that bond:

- Size it for the larger of the two motor currents, and keep it short and thick. It is
  carrying real current, not just a reference.
- **Do not fuse it.** A fuse that opens in the ground bond leaves every analogue reading on
  the far pack floating while the robot is still driving, which is worse than the fault it was
  protecting against.

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

1. The Spine loses power and stops driving the DACs.
2. The other controller still has power, from the smaller pack.
3. Arbitration rules 4 and 5 cannot help, because the board that enforces them is off.

**This is the step that decision D7 made dangerous, and it is the single most important
paragraph in this document.**

With VESCs, the robot was relying on the **VESC's own command timeout**: no command for about
a second and it released the motor. That behaviour is what stopped the robot pivoting on its
surviving track, and it was free.

**A scooter controller has no such timeout.** It is an analogue device. It sees a throttle
voltage and it drives. Worse, the DAC that produces that voltage **keeps holding its last
value** when the Teensy dies — it does not fall to zero. So the exact failure that used to
produce a graceful coast now produces a robot driving away at whatever throttle it had, with
nothing at all in control of it.

The **hardware watchdog** is the entire replacement for that lost behaviour. It is a separate
timer chip that must be kicked by the Teensy every cycle; if the kicks stop, it opens a relay
in the throttle lines. This is why `05-bom.md` lists it as non-negotiable rather than as a
nice extra.

So this becomes the critical item in the whole build, not a configuration detail:

- **Fit the hardware watchdog.** Nothing else does this job. There is no setting to enable.
- Test it, as safety log test 15: cut power to the Spine while the robot is driving, and
  confirm both tracks stop and the robot does not turn.
- Test its blind spot too, as safety log test 16. The watchdog only fires when the kicks stop,
  so a Teensy that is alive but has lost the I2C bus to the DACs will keep kicking while the
  throttle stays stuck. The firmware must check every DAC write and **stop kicking on purpose**
  when one fails.
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

It also reads the sensors that replaced the VESC telemetry — the hub motors' thermistors, the
pack voltage dividers, the ACS758 current sensors and the hall-edge speed counts — and forwards
motor temperature and battery voltage up to the Brain.

### Looking around now means driving

With a fixed head, **`GAZE` can only move pupils.** To actually look left or right, the
robot has to turn its whole body. That has three consequences, and the third is the one
that can hurt somebody.

**1. The camera's field of view is the robot's field of view.** The OAK-D Lite sees 69
degrees, so `+-34.5` degrees ahead and nothing else. It is blind across the remaining 111
degrees until the body turns. The model now prints this, and it only sees the full width of
its own path from 489 mm ahead — closer than that, its own track edges are out of frame.
That is the job the ToF bumper ring was already doing, and it is now load-bearing rather
than a nice extra.

**2. A turn in place is the hardest thing the drive ever does.** Skid steering a tracked
vehicle means running the two belts in opposite directions and scrubbing them sideways
across the ground. It is the highest-current manoeuvre there is, and in soft Negev sand the
belts dig in rather than slide, which raises it further. Every "look left" spends the
current budget of a hard acceleration. Two things follow:

- The current limit that section 1b's ACS758 sensors enforce will be hit by *turning*, not
  by driving. Test it by turning in place on sand, not by driving in a straight line.
- Turning in place is also what wears belts and pulls them off. Prefer a gentle arc over a
  pirouette wherever the behaviour allows it.

**3. The personality layer can now command motion, and it must not have that authority.**
This is the part to get right. Before, "be curious about that person" moved a servo, and the
worst case was a twitchy head. Now the same intent moves 86 kg of robot. A frozen or
confused Brain used to produce a stuck head; now it can produce a robot that keeps turning.

So a look-driven turn is **not** a special case. It is an ordinary drive command and it goes
through every rule in section 2 exactly like a stick input: the slew limit, the current
limit, the tilt cut-out, the bumper stop, and the watchdog. Three rules on top of that:

| | Rule |
|---|---|
| L1 | The Brain may only request a turn as a **heading offset with a timeout**, never as a raw motor command. If the Brain stops talking, the turn stops with it — the existing heartbeat already does this. |
| L2 | **Cap look-turns well below the driving limit.** A gaze turn gets a fraction of full turn rate, so a runaway look is a slow spin you can walk away from, not a spin that knocks somebody over. |
| L3 | **The operator's stick always wins.** Any stick movement cancels an in-progress look-turn immediately. The operator must never have to fight the personality for control. |

Rule L3 is why the RC channel that used to be "head pan override" is not deleted but
**repurposed as a look-turn enable**. Put it on a switch. If the crowd is tight, the robot
stops turning on its own and only the operator drives.

### Face — ESP32-S3, C++

Receives short intent messages from the Brain, such as `GAZE 20 -5` or `MOOD curious`, and
then runs the animation itself: pupil movement and blinking, on the two screens.

**There are no servos.** Owner decision 2026-09-17: the head is a rigid welded post. It
does not pan, nod, or tilt. Everything the face does, it does with 480x480 pixels per eye.

That is a real gain in a sand-blown desert — no gear train, no bearing, no slip ring, and no
cable twist limit — but it moves a problem into the firmware. See "Looking around now means
driving" below.

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
| 1 | One controller on a bench, one pod motor, a hand throttle, no Teensy | The motor spins from the throttle. You now know the controller and motor are healthy, with no code involved |
| 2 | Teensy drives one DAC into that controller's throttle line | The motor responds to a number you type in |
| 3 | Add the RC receiver, one motor | The stick spins the motor, and it stops when you switch the transmitter off |
| 4 | **Add the hardware watchdog, before the second track** | Pull the Teensy's power while the motor runs: the relay opens and the motor stops. Do this stage **before** there are two tracks that can pivot the robot |
| 5 | Add the second controller and mixing | Both tracks on blocks, the robot steers correctly in the air |
| 6 | Add the E-stop and the arm switch | Every one of the section 3 failures gives a stop. **Test each one on purpose.** |
| 7 | First drive, outdoors, no body, tethered E-stop | It drives and turns on sand. **Watch the current on a turn in place** — that is the peak, not straight-line driving |
| 8 | Add the bumper sensors | It refuses to drive into a cardboard box |
| 9 | Add the Face, with the Brain doing nothing else | Eyes animate and follow a hand |
| 10 | Add the camera and the personality | Pupils follow a real person across the room. The head does not move |
| 11 | Enable look-turns, on the channel 6 switch | The body turns slowly to keep a person in view, and **any stick input cancels it instantly** |
| 10 | Add the body and the sound | — |

Stage 5 is not optional and cannot be rushed. Go through the failure list in section 3 and
deliberately cause each one: pull the radio antenna, unplug the Brain's USB cable, press the
E-stop mid-drive, short the bumper sensor. If any of them does not produce a stop, the robot
is not ready to be near people.
