# 00 — Master plan

The whole project: where it stands, what must happen in what order, what it costs, and what
can go wrong. Read this before buying anything or cutting any steel.

Read `99-glossary.md` alongside it if a word is unfamiliar, and `01-architecture.md` for the
detail of how the electronics fit together.

---

## 1. What "done" looks like

A tracked robot, about 672 mm wide and roughly a metre tall, that clearly reads as WALL-E to
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
| L6 | **Body from 12 mm plywood.** REVISED 2026-09-17: was foam with a thin ply skin and fibreglass over it | Mass up high makes the tipping worse, and plywood turned out to be the LIGHTER answer: the foam build was a 25 kg guess, the plywood box computes to 13.6 kg from its own geometry. 11.5 kg off the robot, 15 mm off the centre of mass, 0.7 deg more forward tipping margin, and 445 dollars cheaper |
| L7 | Keep the fitted 18-link belts | Was decision D1. See below |
| L8 | Frame mounting width 168 mm | Set by the built pods. Not a choice any more |
| L9 | One 48 V pack per pod, positives separate, negatives bonded at one point | Was D4. Avoids paralleling two packs entirely. `01-architecture.md` §3b |
| L10 | Electronics fed from the **larger** pack, one isolated converter | The extra load pushes both packs towards emptying together. Needs safety log test 15 |
| L11 | Frame stays 550 mm long. **All electronics on a shelf inside the body** | The frame interior is entirely battery — 8 mm above the packs, 24 between them. Nothing fits. Owner decision, 2026-09-16 |
| L12 | Body length follows the **pod** length, not the anti-tip castors | A body sized to cover the castors is 745 mm on 363 mm pods, and looks like a crate on toy wheels. The castor arms show as outriggers instead |
| L13 | Two Face boards, one per eye | Two 480×480 QSPI panels on one ESP32-S3 is tight and would tear. 12 dollars removes the risk. `05-bom.md` §4 |
| L14 | The amplifier gets its own 48→32 V converter | A TPA3255 maxes out at 53.5 V and a "48 V" pack is 54.6 V full. It also keeps the audio spikes off the Jetson's rail. `04-power-and-wiring.md` §4 |
| L15 | **Batteries stay in the frame, not in the body** | Not for the tipping, which is affordable. They need a sealed case wherever they go, and once that is true the body is the hottest, most crowded and most dangerous place for them. `06-why-the-batteries-are-low.md` |
| L16 | The battery box is a **closed, gasketed box** with a membrane vent in the lid | Owner, 2026-09-16: sand. It was a three-sided U hanging where the belts throw sand. Now six panels, plugged spanner holes, foam pad, lid vent |
| L17 | Packs charge **in place** and never come out in the field | Every opening of a sealed box at a dusty event undoes the sealing. Charge lead out through a gland to a connector on the body, behind a dust cap |
| L18 | Box floor stays at 150 mm for now | Raising it to 173 — the limit, set by lid-bolt access under the body floor — would buy 23 mm of ground clearance for 0.1° of tipping. Owner: revisit after the first drive on sand |
| L19 | **Two 6.5 inch drivers in the chest panel**, 280 mm apart, 584 mm up | Owner, 2026-09-16. Position is derived, not chosen: the enclosures have to clear the tallest shelf box and the body lid, and the driver centres on what is left |
| L20 | Each driver gets its **own sealed 10.1 litre enclosure**. They do not fire into the body | The body is not airtight — filtered intake, removable lid, cable entries — so an open back would chuff and lose its bass. And 100 W of pressure in the electronics bay shakes every connector |
| L21 | The enclosures **bolt** to the chest panel and lift out | They shade 54 % of the shelf. Glued in, half the electronics is unreachable |
| L22 | Metal grilles over both drivers | A crowd will push a finger through an open cone |
| L23 | **The head is rigid. No pan, no nod, no tilt, no servos** | Owner, 2026-09-17. To look left or right the whole robot turns. Removes four gear trains, a bearing, a slip ring and a cable twist limit from a machine that lives in blowing sand, and takes the head from a 5 kg guess to 2.1 kg computed, which drops the centre of mass 18 mm. The cost is in firmware, not hardware: a gaze is now a drive command, so it needs rules L1 to L3 in `01-architecture.md` |

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
| **D7** | Reuse the scooter controllers, or buy two VESCs? | Cost, and whether motor temperature can be read | **DECIDED 2026-09-17: reuse them.** They have a reverse line, and the motor's own thermistor gives the temperature. 260 dollars held as contingency |

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

**REVISED 2026-09-17. This decision used to recommend buying two VESCs. It no longer does.**

The controllers **have a reverse line**, confirmed by the owner. That was the one fact that
could have ruled them out: skid steer needs each side to run forwards and backwards on its
own, and without reverse the robot could only make wide arcs, never turn on the spot.

**Use them now, for free, to prove the motors work.** Bench-test both hub motors with their
original controllers and a physical throttle before you buy anything. No code. If a motor is
dead, you want to know today.

**Then drive them from the Teensy.** They accept a throttle voltage and nothing else, so a
digital-to-analogue converter fakes it. The reverse and e-brake lines are switched to ground
through opto-isolators. `05-bom.md` section 1b is the parts list, about 76 dollars.

**Two of the three old objections have been answered:**

1. *They report no motor temperature.* The hub motor has **its own thermistor** in its cable.
   Read it straight into the Teensy for the price of two resistors. Risk R5 keeps its
   defence.
2. *They report no current.* An ACS758 hall sensor on each pack lead, 20 dollars the pair.
3. *Their current limits, ramp and cut-off are fixed in firmware and cannot be tuned for a
   slow heavy robot.* **Still true, and not fixable.** So is the six-step commutation, which
   judders at walking pace — exactly where a skid-steer robot spends its life.

**Two new conditions come with this decision:**

- A **hardware watchdog** is now mandatory. A throttle springs back to zero; a DAC holds its
  last value forever, so a Teensy crash mid-drive leaves the robot driving. A relay with
  normally-closed contacts, held open by a heartbeat pulse, shorts the throttle to ground
  when the pulses stop. Nothing in software has to work for that to happen.
- Check for **automatic cruise control**. Some scooter controllers engage it after a few
  seconds of steady throttle. In a crowd that is dangerous. If it cannot be disabled, buy the
  VESCs.

**Recommendation: use the controllers you own, and hold 260 dollars as a contingency.** This
is a bet that six-step control is smooth enough at walking pace. You will not know until you
drive it. If it judders, two VESCs drop straight in: the Teensy and the
power wiring all stay, and you add two 3.3 V CAN transceivers, which are not on the list until
then. What you throw away is the throttle interface — the two DACs, the level
shifter and the opto-isolators, about 30 dollars — and you gain back the telemetry and the
command timeout. The hardware watchdog stays either way; it is cheap insurance.

---

## 5. Workstreams and the critical path

Four streams. Two of them start today and do not wait for each other.

```
  W1 FRAME ─── the critical path ────────────────────────────────►
     measure pods → design in SCAD → shock bolt retrofit → build → mount pods

  W2 DRIVE ELECTRONICS ── starts on a bench, no frame needed ────►
     test motors → throttle by hand → Teensy + DAC → watchdog → radio → E-stop → 2 motors → install

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
| Order a Teensy 4.0, two MCP4725 DACs, a level shifter, the watchdog parts, the radio set, a multimeter | W2 |

**Exit test:** both motors spin under their own power, and the measured pod dimensions are
written down and match the model within a millimetre or two.

### Phase 1 — Frame design, and prove the drive on a bench (weeks 2 – 7)

| W1 frame | W2 bench electronics |
|---|---|
| Model the side-by-side frame in OpenSCAD | Spin a hub motor from its own scooter controller and a hand throttle |
| Batteries low, below the mounting beam | Get the Teensy to drive the throttle through the DAC, with the watchdog wired |
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
| Batteries in low, both scooter controllers, the Teensy, the contactor and the fusing |
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
| Eye screens working from the ESP32 |
| Head built: rigid post, two ply barrels, camera under the brow |
| Look-turn enable on RC channel 6, capped and cancelled by the stick |
| Amplifier and sound clips into the two 3.22 litre speaker wells |

**Exit test:** the robot refuses to drive into a cardboard box even when you push the stick at
it, and its pupils follow a person walking across a room. The head itself does not move — if
the person walks out of the camera's 69 degree view, the robot turns its body to keep them,
slowly, and stops the moment you touch the stick.

### Phase 5 — Body, paint, lighting (weeks 14 – 24)

Shell from 12 mm plywood, arms fitted, sealed or varnished against the day-to-night humidity swing, night lighting. The eye barrels are stacks of 12 plywood rings, glued up and sanded round.

**Exit test:** somebody who has seen the film says "WALL-E" without being prompted.

### Phase 6 — Field readiness (weeks 24 – 28)

The phase everybody skips and then regrets.

| Task |
|---|
| Dust covers on every bearing, bushing, and the LiDAR window |
| Heat test: run it in full midday sun until something complains |
| Endurance test: a full evening on sand, on one charge |
| Night test: can the driver see it, can it see, are the eyes visible |
| Spares kit: printed sprocket, belt links, fuses, a spare 48 V controller, spare DACs, a spare eye panel |
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
| Drive electronics | throttle interface, contactor, fuses, heavy cable, lugs (controllers already owned) | 270 – 380 |
| Radio control | Transmitter, receiver, wireless E-stop keyfob | 150 – 250 |
| Compute | Jetson Orin Nano 8GB, storage, cooling | 300 – 350 |
| Spine and Face boards | Teensy 4.0, ESP32-S3, 2 round LCDs | 80 – 120 |
| Sensors | LiDAR, OAK-D camera, 6 × ToF, GPS, compass | 300 – 400 |
| Power conditioning | Isolated DC-DC converters, buffer, distribution | 100 – 150 |
| Audio | Class-D amplifier, wiring | 60 – 100 |
| Body and head | 12 mm plywood, glue, hinges, gas strut, sealer. Steel already owned | 280 - 360 |
| Lighting | LED strips, drivers, the eye illumination | 100 – 150 |
| Tools and consumables | Soldering, crimping, multimeter, drill bits | 200 – 400 |
| Spares kit | Section 6, Phase 6 | 250 – 350 |
| **Total still to spend** | | **≈ 2,400 – 3,000** |

If the donor battery packs cannot be reused, add 600 to 1,200.

### Buy in this order, not all at once

1. **Now:** a Teensy, the throttle interface parts, the radio set, a multimeter. About 250
   dollars, and it is the cheapest way to find out whether the drive electronics are going to
   be a problem.
2. **Now:** the shock bolt retrofit steel. Small money, and it unblocks loading the pods.
3. **Phase 1:** the frame steel, the contactor, the fusing, heavy cable.
4. **Phase 2:** the Jetson and the sensors. Do not buy these early. They sit in a drawer
   losing value while you do metalwork, and a newer version may appear.
5. **Phase 4:** the screens and the amplifier. No servos — the head is rigid.
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
| 5 | Arduino: turn the potentiometer into a voltage on the MCP4725 DAC, and read it back with the multimeter | 0 to 3.3 V follows the knob. This replaces the old "drive a servo" exercise, which taught PWM the robot no longer uses anywhere — and it is the real throttle task in miniature |
| 6 | Spin a motor from its scooter controller and a hand throttle, no code | The hub motor turns, and you know it is healthy |
| 7 | Teensy: one value written to the DAC | The motor moves because of a number in your code |
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
| R5 | Hub motors overheat crawling | Dead robot mid-event | Read the motor's OWN thermistor into the Teensy and log it from the first bench test. The scooter controllers cannot limit current for us, so the Teensy has to back the throttle off itself. Keep it light |
| R6 | Motor current spikes reboot the Brain | Eyes and sounds die in front of an audience | Isolated DC-DC rail, own fuse, buffer capacitor |
| R6b | The electronics pack's BMS cuts out, so the Spine dies too | No board left to enforce any stop rule | The scooter controllers have NO command timeout of their own, so this defence is now entirely the hardware watchdog: heartbeat stops, relay falls closed, throttle shorted to ground. Prove it by safety log test 15 |
| R6c | The motor controllers cook inside the body | One track dies, and the robot pivots | Direct consequence of L11: on a plywood shelf they have no steel to dump heat into. Each gets an aluminium plate bolted through to a body panel, and one filtered air path pushes air IN so the body runs at positive pressure |
| R7 | Frame arrives late, no time to integrate | A clever box that cannot move | Frame design starts week 2. Electronics run in parallel on a bench |
| R8 | Sand destroys bushings and bearings | Progressive seizure over the event | Covers. Daily cleaning. Spares in the kit |
| R8b | Sand gets into the battery box | Grit between the cells and the box, chafed wiring, a short | L16: closed box, gasketed lid on 110 mm bolt pitch, silicone plugs in all four spanner holes. **Check the plugs are in every morning** — they are the weak point, and they point at the belts |
| R8c | The sealed box breathes and pumps dust in through its worst leak | Slow, invisible version of R8b, and it defeats the gasket | Membrane vent in the lid, on the centreline over the gap between the packs, so the air has a clean path it does not have to find |
| R8d | Charging in a sealed box has nowhere to put the heat | Packs age fast, or worse | About 12 W of loss at 5 A. Log the pack temperature through one full charge with the lid on, on the bench, before the event. If it climbs, charge with the body lid open or drop the current |
| R10 | Forward tipping margin keeps getting eaten | The castor catches, the robot stops looking like it meant to | The speakers alone took 1.5°, leaving 5.4° over the castor. **Every new part forward of centre or high up spends this number.** Weigh the real pods, packs, body and speakers and put the measured figures in the model before adding anything else |
| R11 | Speaker enclosures rattle or buzz at volume | Sounds broken, and it is the thing the crowd hears | Sealed boxes, braced, and the drivers bolted through with gasket tape. Test at full volume on the bench before the body goes on |
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
6. Order a Teensy, the throttle interface parts, and the radio set
7. Start learning plan steps 1 to 5 while the parcels are in the post
8. Design the frame in OpenSCAD
