# 00 — Master plan

The whole project: where it stands, what must happen in what order, what it costs, and what
can go wrong. Read this before buying anything or cutting any steel.

Read `99-glossary.md` alongside it if a word is unfamiliar, and `01-architecture.md` for the
detail of how the electronics fit together.

---

## 1. What "done" looks like

A tracked robot, about 700 mm wide and roughly a metre tall, that clearly reads as WALL-E to
anybody who has seen the film. It is driven by a person with a radio remote. Its eyes find
faces and follow them. It makes WALL-E's noises. It runs for a full evening on the sand of
the Negev, in a crowd, without hurting anybody and without breaking down.

Three things are deliberately **not** goals:

- It does not drive itself. See section 4, L2.
- It does not carry passengers, unless decision D3 changes that.
- It does not talk in full sentences. Short recorded sounds beat synthesised speech for this
  character, and cost almost nothing.

---

## 2. Where the project stands today

**Both pods are built, to Rev 012.** This is a much stronger starting position than a design
on paper, and it moves the hard part of the project from metalwork to electronics.

| Item | Status |
|---|---|
| Pod design (Rev 012) | Complete, all clearance checks pass |
| Both pods | **Built**, carrier plates 168 mm apart, shocks inboard at \|z\|=73 |
| Belts | **Fitted** — 1080 mm, 18 links, 231 mm on the ground per pod |
| Hub motors | **Both in hand** |
| Original scooter controllers | **Both in hand** — see decision D7 |
| Frame for the side-by-side layout | Not designed. This project designs it |
| Electronics | Nothing bought, nothing built |
| Body | Nothing |

### What "built to Rev 012" gives us

These are now real, measurable numbers rather than design intent:

| Thing | Value |
|---|---|
| Carrier plate spacing | 168 mm, so the frame mounting width is fixed at this |
| Ground contact, one pod | 231 mm long × 118 mm wide |
| Pod size | 363 long × 327 tall × ~200 wide over the plates |
| Pod mounting band | A plate 60 mm tall, 197–257 mm above the ground, at the hub |
| Suspension travel | +30.7 mm up, −29.2 mm down |
| Ground pressure at 100 kg | 0.18 kg/cm², about a third of a walking person's foot |
| Belt movement per motor turn | 660 mm |

Confirm the 168 mm spacing with a tape measure across the two carrier plates before the
frame is welded. It is the one dimension that, if wrong, makes the frame useless.

### One design problem is still open, and the pods were built with it

The model raises two warnings about the **lower shock bolt**. They are explained in full in
`02-shock-bolt.md`. The short version:

- The shock's lower eye sits on a bolt that is held on one side only. The other end hangs
  free, so the shock force bends it like a diving board.
- At full suspension bump the force is 2681 N over a 41 mm lever, which gives 351 MPa of
  bending stress. Mild steel bends permanently at 235 MPa.
- Sitting still it is fine, at about 150 MPa. The problem is the first hard hit.

Because the pods are already assembled, this is now a **retrofit** rather than a design
change. The good news is that the standard fix — supporting the bolt's outer end so it is
held at both ends — can be added from outside without taking a pod apart. Decision D2.

### What this means for the plan

With the pods built, the critical path is now the **frame and the electronics**. Two things
follow from that:

1. The frame can be designed this week, because every dimension it has to match already
   exists on a finished pod and can be measured.
2. You own two hub motors, so the entire drive electronics chain can be built and tested on
   a workbench immediately, in parallel with the frame. That removes the scariest unknown
   early.

---

## 3. Hard constraints

| Constraint | Consequence |
|---|---|
| No network at the event | Every model runs on the robot. No cloud, no phone tethering |
| Negev heat, 40 °C and direct sun | Active cooling. No PLA anywhere structural. Heat test before you go |
| Fine abrasive sand | Covers on every bearing and bushing. Daily cleaning. Spares |
| The event is mostly at night | Vision alone is not enough. Lighting is required, not decorative |
| Crowds of people, some not sober | The safety layer is the reason this plan is shaped this way |
| Builder is new to electronics | Section 10 is a learning plan, on the schedule as real time |
| Pods are already built | The 168 mm spacing and the 231 mm footprint are now fixed inputs |
| One person, evenings and weekends | Section 8 assumes this. Extra hands change everything |

---

## 4. Decisions

### Locked — do not revisit without a reason

| # | Decision | Why |
|---|---|---|
| L1 | Pods side by side, skid steer | Deletes the undesigned steering link, and it is how WALL-E works |
| L2 | Teleoperated, not self-driving | Safer in a crowd, far less work, and the crowd cannot tell |
| L3 | Three boards: Brain, Spine, Face | Timing requirements differ by 1000×. `01-architecture.md` §1 |
| L4 | Radio receiver and E-stop wire into the Spine | The driver keeps control when the Brain crashes |
| L5 | No SLAM. GPS and compass if position is needed at all | Open desert has no landmarks and the crowd keeps moving |
| L6 | Body from foam and thin plywood | Mass up high makes the tipping worse. Keep the top light |
| L7 | Keep the fitted 18-link belts | Was decision D1. See below |
| L8 | Frame mounting width 168 mm | Set by the built pods. Not a choice any more |
| L9 | One 48 V pack per pod, positives separate, negatives bonded at one point | Was D4. Avoids paralleling two packs entirely. `01-architecture.md` §3b |
| L10 | Electronics fed from the **larger** pack, one isolated converter | The extra load pushes both packs towards emptying together. Needs safety log test 15 |
| L11 | Frame stays 550 mm long. **All electronics on a shelf inside the body** | The frame interior is entirely battery — 8 mm above the packs, 24 between them. Nothing fits. Owner decision, 2026-09-16 |
| L12 | Body length follows the **pod** length, not the anti-tip castors | A body sized to cover the castors is 745 mm on 363 mm pods, and looks like a crate on toy wheels. The castor arms show as outriggers instead |
| L13 | Two Face boards, one per eye | Two 480×480 QSPI panels on one ESP32-S3 is tight and would tear. 12 dollars removes the risk. `05-bom.md` §4 |
| L14 | The amplifier gets its own 48→32 V converter | A TPA3255 maxes out at 53.5 V and a "48 V" pack is 54.6 V full. It also keeps the audio spikes off the Jetson's rail. `04-power-and-wiring.md` §4 |
| L15 | **Batteries stay in the frame, not in the body** | Not for the tipping, which is affordable. The shelf has no room, the body is the hottest and most sealed place on the robot, and it is the worst place for a cell to fail. If clearance is the problem, raise the box floor towards 190 mm instead. `06-why-the-batteries-are-low.md` |

#### L7 — why we keep the short belts now

Longer belts would give about 400 mm of ground contact instead of 231 mm, and would make the
robot much harder to tip forward. While the arms were uncut, that was cheap and was the
recommendation.

It is no longer cheap. Changing the belt length changes the arm lengths, so it means
stripping both finished pods, re-cutting the arms, re-solving the shock geometry, and
rebuilding. That is weeks of work undoing work that is already done.

**So we keep the 231 mm footprint and solve the tipping a different way:** anti-tip wheels,
plus keeping all the heavy things as low as possible. See decision D6.

### Open — each one has a deadline, because something waits on it

| # | Question | Blocks | Decide by |
|---|---|---|---|
| **D2** | How is the lower shock bolt retrofit done? | Whether the pods are safe to load | **Before Phase 2.** Read `02-shock-bolt.md` |
| **D3** | Does WALL-E carry a person? | Frame strength, tipping, Midburn registration | Before Phase 2 |
| **D4** | Both pack capacities in Ah, and are both BMS units healthy? | Runtime, which side gets the electronics, fuse and cable sizing | Before Phase 1 buying |
| **D5** | Confirmed Midburn date and mutant vehicle rules | The entire schedule | This week |
| **D6** | Anti-tip wheels: how many, where, how high off the ground? | Frame design | Phase 1 |
| **D7** | Reuse the scooter controllers, or buy two VESCs? | Cost, and whether motor temperature can be read | Before Phase 1 buying |

#### D6 — the tipping fix, since the belts are staying

The robot's whole front-to-back footprint is 231 mm, so ±115 mm from the centre. With all the
mass low, it starts to go over at about 16 degrees of pitch. Braking hard, or driving off a
small step, can reach that.

The fix used on wheelchairs and forklifts is an **anti-tip wheel**: a small castor mounted
front and back, set deliberately **30 to 40 mm above the ground**. In normal driving it never
touches anything, so it does not carry load and does not interfere with the suspension. It
only touches when the robot has already started to pitch, and then it stops the pitch before
it becomes a fall.

This is much better than a tail skid that always touches, because a permanent third contact
point fights against the pods' ±30 mm of suspension travel in a way that is hard to predict.

Alongside it: put both battery packs **below** the pod mounting beam, down near the 145 mm
floor line. Roughly 24 kg of ballast at 190 mm above the ground does most of the stability
work for free, and it costs nothing because the batteries have to go somewhere anyway.

#### D7 — the scooter controllers you already have

They are worth keeping, but probably not for the final robot.

**Use them now, for free, to prove the motors work.** Bench-test both hub motors with their
original controllers and a throttle before you buy anything. If a motor is dead, you want to
know today.

**They are poor for the real build**, for three reasons:

1. They accept a throttle voltage and nothing else. You can fake that from a microcontroller
   with a digital-to-analogue converter, so skid steer is technically possible.
2. But they report nothing back. No motor temperature, no current. Motor overheating at low
   speed is risk R5 in section 11, and temperature feedback is our main defence against it.
   Giving that up to save money is a bad trade.
3. Their current limits, cruise control, and cut-off behaviour are fixed in firmware and
   cannot be tuned for a slow heavy robot.

**Recommendation: two VESCs, about 260 dollars.** Keep the scooter controllers as bench test
gear and as an emergency spare that could get the robot driving badly if a VESC dies at the
event.

---

## 5. Workstreams and the critical path

Four streams. Two of them start today and do not wait for each other.

```
  W1 FRAME ─── the critical path ────────────────────────────────►
     measure pods → design in SCAD → shock bolt retrofit → build → mount pods

  W2 DRIVE ELECTRONICS ── starts on a bench, no frame needed ────►
     test motors → VESC → Teensy → CAN → radio → E-stop → 2 motors → install

                    W3 SENSE, BRAIN AND FACE ──────────────────────►
                       Jetson → LiDAR → camera → personality → eyes → head

                              W4 BODY ─────────────────────────────►
                                 shell → paint → lighting
```

W1 and W2 start on day one. W3 needs no frame either, but attention is the real scarce
resource, so it starts once W2 works on the bench. W4 starts last, because the body must fit
around finished hardware and because it is the stream most likely to eat all remaining time.

**The biggest scheduling mistake available to you** is to start with W3, the AI, because it is
the most interesting. Then the frame arrives late, there is no time to integrate, and you
bring a very clever box that cannot move.

---

## 6. Phases, with exit tests

A phase is not finished because the work is done. It is finished when its exit test passes.

### Phase 0 — Measure, decide, order (week 1)

| Task | Stream |
|---|---|
| Measure the real pods: carrier spacing, mounting band height, overall width | W1 |
| Bench-test both hub motors with the original scooter controllers | W2 |
| Read `02-shock-bolt.md`, inspect both pods, decide D2 | W1 |
| Confirm the donor battery voltage and capacity (D4) | W2 |
| Confirm the Midburn date and vehicle rules (D5) | — |
| Order one VESC, a Teensy 4.1, a CAN transceiver, the radio set, a multimeter | W2 |

**Exit test:** both motors spin under their own power, and the measured pod dimensions are
written down and match the model within a millimetre or two.

### Phase 1 — Frame design, and prove the drive on a bench (weeks 2 – 7)

| W1 frame | W2 bench electronics |
|---|---|
| Model the side-by-side frame in OpenSCAD | Set up the VESC with its own tool, spin a hub motor |
| Batteries low, below the mounting beam | Get the Teensy to send one CAN message to the VESC |
| Anti-tip wheel mounts, 30–40 mm clear (D6) | Add the radio receiver, drive the motor from the stick |
| Design and fit the shock bolt retrofit (D2) | Add the E-stop and the arm switch, with the watchdog |
| Order the steel | Log motor temperature from the very first run |

**Exit test, W1:** the frame model runs with zero warnings, and the retrofit is fitted to both
pods.
**Exit test, W2:** the stick drives one motor, and the motor stops when you switch the
transmitter off, when you press the E-stop, and when you unplug the Teensy's serial cable.

### Phase 2 — Build the frame and drive it (weeks 6 – 12)

| Task |
|---|
| Weld and assemble the frame |
| Mount both pods on the 168 mm carrier spacing |
| Batteries in low, both VESCs, the Teensy, the contactor and the fusing |
| Add mixing for two motors, and slew rate limiting |
| Fit the anti-tip wheels |

**Exit test:** it drives forward, backward, turns both ways, and spins in place, on sand, with
a tethered E-stop in a walking person's hand. Add ballast to match the planned body weight and
confirm it does not pitch alarmingly under braking, and that the anti-tip wheels catch it.

### Phase 3 — The safety gate (weeks 12 – 13)

Not a build phase. A test phase, and the most important one in the project.

Work down the arbitration list in `01-architecture.md` §3 and **deliberately cause every
failure** while the robot is driving:

1. Press the physical E-stop
2. Trigger the wireless keyfob E-stop
3. Switch the transmitter off
4. Walk the robot out of radio range
5. Unplug the Brain's USB cable
6. Pull the power to the Brain
7. Short a bumper sensor
8. Disconnect one CAN wire

**Exit test:** all eight produce a controlled stop, and none produces a lurch, a turn, or a
runaway. Record the date and result for each one in `03-safety-log.md`.

> Until Phase 3 passes, the robot does not operate within ten metres of another person.
> There is no schedule pressure that justifies skipping this.

### Phase 4 — Senses, face, and personality (weeks 10 – 18)

| Task |
|---|
| LiDAR fitted, obstacle map built, bumper veto wired into the Spine |
| Jetson installed on its isolated power rail, temperature logging running |
| Camera fitted, face detection running, gaze targets sent to the Face |
| Eye screens and barrel tilt servos working from the ESP32 |
| Head mechanism built |
| Amplifier and sound clips into the two 3.22 litre speaker wells |

**Exit test:** the robot refuses to drive into a cardboard box even when you push the stick at
it, and its eyes follow a person walking across a room while the head tilts.

### Phase 5 — Body, paint, lighting (weeks 14 – 24)

Shell from foam and thin plywood, arms fitted, weathered paint, night lighting.

**Exit test:** somebody who has seen the film says "WALL-E" without being prompted.

### Phase 6 — Field readiness (weeks 24 – 28)

The phase everybody skips and then regrets.

| Task |
|---|
| Dust covers on every bearing, bushing, and the LiDAR window |
| Heat test: run it in full midday sun until something complains |
| Endurance test: a full evening on sand, on one charge |
| Night test: can the driver see it, can it see, are the eyes visible |
| Spares kit: printed sprocket, belt links, fuses, a spare VESC, servos |
| Field repair kit and a printed copy of the wiring diagram |

**Exit test:** a full evening of driving on sand with no intervention that is not in the
spares kit.

---

## 7. Budget

Approximate, in US dollars, for what is **still to buy**. The pods are built, so all pod
material, shocks, bearings, axles, belts and sprockets are already paid for and not counted.

| Group | Items | Cost |
|---|---|---|
| Shock bolt retrofit | Steel strap, longer bolts, sleeves (D2) | 30 – 80 |
| Frame | Steel tube, plate, plywood, welding consumables | 250 – 400 |
| Anti-tip wheels | 2 castors and their mounts | 40 – 80 |
| Drive electronics | 2 × VESC, contactor, fuses, heavy cable, lugs | 400 – 550 |
| Radio control | Transmitter, receiver, wireless E-stop keyfob | 150 – 250 |
| Compute | Jetson Orin Nano 8GB, storage, cooling | 300 – 350 |
| Spine and Face boards | Teensy 4.1, CAN transceiver, ESP32-S3, 2 round LCDs | 80 – 120 |
| Sensors | LiDAR, OAK-D camera, 6 × ToF, GPS, compass | 300 – 400 |
| Power conditioning | Isolated DC-DC converters, buffer, distribution | 100 – 150 |
| Audio | Class-D amplifier, wiring | 60 – 100 |
| Body | Foam, plywood, fibreglass, filler, paint | 400 – 800 |
| Lighting | LED strips, drivers, the eye illumination | 100 – 150 |
| Tools and consumables | Soldering, crimping, multimeter, drill bits | 200 – 400 |
| Spares kit | Section 6, Phase 6 | 250 – 350 |
| **Total still to spend** | | **≈ 2,700 – 4,200** |

If the donor battery packs cannot be reused, add 600 to 1,200.

### Buy in this order, not all at once

1. **Now:** one VESC, a Teensy, a CAN transceiver, the radio set, a multimeter. About 300
   dollars, and it is the cheapest way to find out whether the drive electronics are going to
   be a problem.
2. **Now:** the shock bolt retrofit steel. Small money, and it unblocks loading the pods.
3. **Phase 1:** the frame steel, the second VESC, the contactor, the fusing, heavy cable.
4. **Phase 2:** the Jetson and the sensors. Do not buy these early. They sit in a drawer
   losing value while you do metalwork, and a newer version may appear.
5. **Phase 4:** the screens, servos, amplifier.
6. **Phase 5:** the body materials, bought against a finished robot you can measure.

---

## 8. Schedule

Weeks from the start, because the target date needs confirming first (D5). Assumes one person
working evenings and weekends, learning as they go.

| Weeks | Phase | Streams |
|---|---|---|
| 1 | 0 — measure, decide, order | W1 + W2 |
| 2 – 7 | 1 — frame design / bench electronics | W1 + W2 in parallel |
| 6 – 12 | 2 — build the frame and drive it | W1 → W2 |
| 12 – 13 | 3 — safety gate | — |
| 10 – 18 | 4 — senses, face, personality | W3 |
| 14 – 24 | 5 — body and paint | W4 |
| 24 – 28 | 6 — field readiness | all |

**About six months of part-time work.** Having the pods built saves roughly six weeks off the
critical path compared with building them from the cut list.

The ranges overlap on purpose, because metalwork has waiting time — paint drying, parts in the
post — and that waiting time is where the electronics get built.

Count backwards from the event date and add **six weeks of slack**. If that does not fit, do
not compress the phases. Use section 9 and cut scope instead.

---

## 9. If time runs short, cut in this order

Decide this now, while calm, rather than in a panic three weeks before the event.

**Must have. Without these there is no robot:**

1. It drives and steers on sand
2. Every failure in the Phase 3 list produces a stop
3. It looks like WALL-E
4. The eyes move and follow people
5. It makes WALL-E's sounds

**Cut first, in this order, and lose almost nothing:**

1. The language model and any speech recognition
2. `ASSIST` mode — manual driving only
3. GPS and compass
4. The LiDAR, keeping only the ToF bumper ring
5. Moving arms — static arms look fine
6. The neck mechanism — a fixed neck with a moving head still reads correctly

Note what is at the top of the cut list: the AI. That is deliberate. A crowd reacts to the
eyes, the sounds, and the movement. Nobody will ask what model is running.

---

## 10. Learning plan

You have not worked with microcontrollers, motor controllers, or AI models before. That is on
the schedule as real time rather than pretended away. Each step is an evening or two, and each
one produces something that works.

| Step | What you learn | You know it worked when |
|---|---|---|
| 1 | Multimeter: voltage, continuity, current | You can measure a battery and find a broken wire |
| 2 | Soldering and crimping | A joint you made survives being pulled hard |
| 3 | Arduino: blink an LED | The LED blinks at a rate you chose |
| 4 | Arduino: read a potentiometer, print it over serial | Numbers change on screen as you turn the knob |
| 5 | Arduino: drive one servo from the potentiometer | The servo follows the knob |
| 6 | VESC Tool: configure and spin a motor, no code | The hub motor turns, and its limits are set |
| 7 | Teensy: one CAN message to the VESC | The motor moves because of a number in your code |
| 8 | Read the radio receiver on the Teensy | Stick numbers print on your screen |
| 9 | Put steps 7 and 8 together | The stick drives the motor |
| 10 | Add the watchdog and the arm switch | Pulling a cable stops the motor |

Steps 1 to 5 use about 30 dollars of parts and no project hardware. Do them while waiting for
deliveries. **Step 10 is the whole Spine**, in concept — everything after that is detail.

For the Brain, the same principle: get a camera window to appear on a screen before you try to
run a model. Then run a model on one saved photograph. Then on live video. Then connect it to
the robot. Four separate evenings, each one testable.

---

## 11. Risk register

Ordered by how much damage each one does, not how likely it is.

| # | Risk | Effect | What we do about it |
|---|---|---|---|
| R1 | Somebody gets hurt | Ends the project, and much worse | Phase 3 gate. Physical E-stop. Human minder with a keyfob. Manual mode in crowds |
| R2 | It tips forward | Broken robot, possibly a broken person | Anti-tip wheels (D6). All mass low. Ballast test in Phase 2 |
| R3 | Lower shock bolt yields on the first hard hit | Suspension failure under load | The D2 retrofit, before the frame is loaded. See `02-shock-bolt.md` |
| R4 | One pack's BMS cuts out while driving | The surviving track spins the robot on the spot instead of stopping | Arbitration rules 4 and 5: either side missing stops both. Safety log tests 11 and 12 |
| R5 | Hub motors overheat crawling | Dead robot mid-event | Log motor temperature from the first bench test. VESC current limits. Keep it light |
| R6 | Motor current spikes reboot the Brain | Eyes and sounds die in front of an audience | Isolated DC-DC rail, own fuse, buffer capacitor |
| R6b | The electronics pack's BMS cuts out, so the Spine dies too | No board left to enforce any stop rule | Each VESC's own command timeout, set explicitly and proven by safety log test 15 |
| R6c | The VESCs cook inside the body | One track dies, and the robot pivots | Direct consequence of L11: on a plywood shelf they have no steel to dump heat into. Each gets an aluminium plate bolted through to a body panel, and one filtered air path pushes air IN so the body runs at positive pressure |
| R7 | Frame arrives late, no time to integrate | A clever box that cannot move | Frame design starts week 2. Electronics run in parallel on a bench |
| R8 | Sand destroys bushings and bearings | Progressive seizure over the event | Covers. Daily cleaning. Spares in the kit |
| R9 | Printed sprocket softens in the sun | Drive failure | Check what the fitted ones are printed in. If PLA, reprint in ASA or nylon. Carry a spare |
| R10 | Scope grows, especially the body | Nothing is finished | Section 9 cut list, agreed in advance |
| R11 | Midburn vehicle rules not met | Cannot operate at the event | D5 this week, before the frame is welded |
| R12 | Builder gets stuck on the electronics | Project stalls silently | Section 10 learning plan. Bench work early, so problems appear when there is time |

R9 is worth checking early: the sprockets are already printed and fitted, so find out what
filament was used. PLA softens at around 60 °C, and a black plastic part in direct Negev sun
will reach that.

---

## 12. What happens next

In order. Nothing later on this list should start before the things above it.

1. Confirm the Midburn date and vehicle rules (D5)
2. Measure the built pods and write the numbers down
3. Bench-test both hub motors with the original scooter controllers — free, and it de-risks
   the whole project
4. Read `02-shock-bolt.md`, inspect the lower shock mounts on both pods, decide D2
5. Confirm both pack capacities in Ah and that both BMS units are healthy (D4)
6. Order one VESC, a Teensy, a CAN transceiver, and the radio set
7. Start learning plan steps 1 to 5 while the parcels are in the post
8. Design the frame in OpenSCAD
