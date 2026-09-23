# 04 — Power and wiring

Every wire on the robot, what size it has to be, and why. Read `01-architecture.md` first —
this document is the physical version of the rules in there.

Two decisions from the architecture drive everything here:

- **Each pack feeds its own pod.** The positives never meet. The negatives are bonded at one
  point. (`01-architecture.md` section 3b.)
- **The electronics run from their own 12 V battery**, not from either pack. Owner decision
  D8, 2026-09-19. **But the contactor coils still run from pack A**, and section 3 explains
  why that split is deliberate rather than untidy.

---

## 1. The power tree

```
PACK A — 48 V, 17.5 Ah                       (capacity is a placeholder)
 +── XT90-S ─┬── FUSE 60 A ── CONTACTOR A ─── CONTROLLER L ── hub motor, left pod
  DISCONNECT │
   sees ~43A ├── FUSE 10 A ── DC-DC 48→32 V ── AUDIO AMPLIFIER
             │                non-isolated,    (why 32 V and not 48: section 4)
             │                150 W
             │
             └── FUSE 5 A ─── E-STOP CHAIN ─── CONTACTOR A COIL, 48 V
                              in series:   └── CONTACTOR B COIL, 48 V
                              mushroom button,
                              wireless stop relay
                              (both coils, BOTH packs, run from PACK A)

PACK B — 48 V, 17.5 Ah                       (the same as pack A — section 3)
 +── XT90-S ──── FUSE 60 A ── CONTACTOR B ─── CONTROLLER R ── hub motor, right pod
  DISCONNECT
   sees ~40A

ELECTRONICS BATTERY — 12 V, 20 Ah LiFePO4    (240 Wh, on the shelf)
 +── FUSE 15 A ── 12 V RAIL                  (see section 3)
                    └── 12→5 V buck ── Teensy, ESP32


PACK A (−) ═══ GROUND BOND ═══ PACK B (−) ═══ 12 V BATTERY (−)
            10 AWG, short, NOT FUSED      one point, section 3
```

### Three things about that tree

**The emergency stop leaves the electronics alive.** This is deliberate, and it now happens
twice over. The Spine, the Brain and the face are on their own battery, which the contactors
cannot touch at all. The amplifier and the coil chain tap pack A **before** contactor A, so
they survive the stop too. Pressing the mushroom button therefore kills both motors and
nothing else: the robot can tell you it is stopped, log why, refuse to re-arm until the button
is reset, and put a message on the eyes. A machine that goes dark and silent tells you nothing.

**The emergency stop is therefore not an isolator.** It stops movement. It does not make the
robot electrically safe to work on. For that you need the separate main disconnect in section
5. Do not confuse the two, and do not let a helper confuse them either.

**Two contactors, one coil circuit.** Because the packs are separate, one contactor cannot cut
both. Both coils are wired in parallel onto the same emergency stop chain, so any single break
drops both sides together. Never wire a stop that can cut one track and leave the other
driving — on a skid-steer machine that is a command to spin, not a command to stop.

---

## 2. How much current, really

These are the numbers the wire sizes and fuses come from. The robot is 91.6 kg
(`cad/walle_frame.scad`).

### Driving in a straight line on sand

| Step | Working | Result |
|---|---|---|
| Rolling resistance, tracks on soft sand | coefficient about 0.15 | — |
| Force to keep it moving | 0.15 × 91 kg × 9.81 | 134 N |
| Mechanical power at walking pace | 134 N × 1.0 m/s | 134 W |
| Electrical power at 75 % efficiency | 134 / 0.75 | 179 W |
| Current from 48 V, both sides | 179 / 48 | **3.7 A total, 1.9 A per side** |

That is a small number, and it is why the runtime is measured in hours rather than minutes.

### Turning, which is the case that actually sizes the wiring

Skid steer turns by dragging both tracks sideways across the ground. There is no steering
geometry helping; the friction has to be overcome by the motors. A pivot turn on sand costs
roughly **four times** the straight-line power, and the two sides fight each other while it
happens.

| Case | Per side | Notes |
|---|---|---|
| Straight, walking pace | 2 A | the normal condition |
| Continuous pivot turning | 8 A | budget for this, not for the straight line |
| Starting from rest, or climbing out of a rut | 25 A | seconds at a time |
| Absolute limit | **40 A** | the number the wire and the fuse must survive |

> ### The 40 A in that table is measured, not chosen
>
> **The scooter controllers' current limit is fixed in their firmware and you cannot change
> it.** So 40 A is not a number you pick and then size the wire to. It is a number you have to
> go and measure.
>
> **Do this before finalising the wire gauge and the fuse rating:**
>
> 1. Find the controller's rated peak current. It is usually printed on the case or in the
>    listing. Scooter controllers in this class are commonly 30 A to 60 A peak.
> 2. Confirm it with the clamp meter, on blocks, at stall — hold the track against a block
>    and read the actual draw. Do not trust the label alone.
> 3. If the real peak is **above 40 A**, the 12 AWG phase wire and the 60 A fuse in section 7
>    have to be re-checked against the real figure, not against 40.
> 4. If it is **well below 40 A**, that is not free either: it caps how hard the robot can
>    pivot and climb out of a rut, which is the case that matters on sand.
>
> The battery current limit, which is the one that actually protects the pack and the fuse,
> is likewise fixed. The Teensy cannot command a current limit, so **the only current control
> you have is backing off the throttle yourself** when the ACS758 sensor reads high. That is a
> software limit on top of a hardware one, and it is slow and weak.
>
> If this measurement comes back ugly, the wire gauge and the fuses in section 7 have to be
> resized around the real number. Do not design to the 40.

---

## 3. The 12 V rail

| Load | Continuous | Peak |
|---|---|---|
| Powered USB hub (OAK-D, LiDAR, serial adapters) | 10 W | 15 W |
| Cooling fans | 5 W | 5 W |
| 12→5 V converter, feeding the Teensy and the ESP32 | 5 W | 8 W |
| **Total** | **20 W** | **28 W** |

The XPS is **not** on this rail. It runs from its own battery and a USB-C PD pack of 65 W or
more.

### This rail has its own 12 V battery

**Owner decision D8, 2026-09-19.** A **12 V 20 Ah LiFePO4** on the lower electronics deck
feeds this rail. Case size **181 × 167 × 77 mm**, lying on its side. That is **not** the 48 V
traction pack case (**400 × 110 × 80 mm**, two of them in the frame box). The Teensy, the
Face, the fans and the USB hub sit on it.

**Owner decision L25, 2026-09-22.** The Brain is the Dell XPS 15. It does not take 12 V in. Do
not try to feed it from this pack with a cheap boost module. Use USB-C PD.

Three reasons, in the order they matter:

1. **The 12 V rail does not share copper with 40 A of motor current.** That is risk R6. There
   is nothing for the motors to pull down.
2. **Both traction packs can be the same capacity.** See `01-architecture.md` section 3b: the
   20 Ah / 15 Ah split only existed to make an electronics load even out two mismatched
   packs. Two equal packs run 5.6 hours instead of 4.7.
3. **Do not add a 48→12 module off pack A to "save" this battery.** A cheap buck shares the
   motor ground and will reboot the Teensy under load.

**Sizing.** 240 Wh against a 20 W continuous rail is 12 hours, so the electronics outlast the
drive. That is the right way round: when the motors stop, the face and the logs are still up
to tell you why.

**It still needs a fuse.** 15 A at the battery terminal, close to the terminal. A 20 Ah
LiFePO4 will happily push hundreds of amps into a short, and its BMS is not a fuse.

**Do not charge it from the packs.** No DC-DC from 48 V to trickle it, because that rebuilds
the exact shared-ground path this decision removed. It gets its own charger and its own
connector on the body, alongside the two pack charge leads. Daily charge is in place; the
pack still unplugs and lifts out (`06-why-the-batteries-are-low.md`, L17).

### The contactor coils are NOT on this rail

They used to be listed here at 6 W. **They are 48 V coils and they run straight off pack A**,
through their own 5 A fuse and the E-stop chain. Owner decision 2026-09-17, resolving a
contradiction: this table had them on the 12 V rail while `05-bom.md` section 2 specified a
48 V coil, and those cannot both be true.

Keeping them off the 12 V rail matters for a reason that is not tidiness. A buyer review on
one cheap contactor reports **coil inrush of 167 W against a 4.4 W specification**
(`05-bom.md` section 9). If that is anywhere near right and the coils were on the 12 V rail,
every contactor pull-in would brown out the 12 V supply. On the pack they are pulling
inrush from a 48 V traction battery instead, which does not care.

**This got more important with decision D8, not less.** The 12 V rail is now a battery, and a
20 Ah LiFePO4 would also shrug off 167 W. But a coil on the electronics battery is a coil that
does not drop when pack A dies, and that is the failure the next section is about. The coils
are on pack A for what they *stop*, not for what they can survive.

**The 5 A fuse is sized for that inrush, not for the holding current.** Two coils hold at
roughly 0.3 A total. Use a slow-blow fuse and measure the real inrush with the bench supply's
current limit before it goes near the robot.

### Running both coils from pack A makes one failure safe for free

This is worth understanding, because it changes what the hardware watchdog is actually for.

Both coils run from **pack A**. So if pack A's BMS cuts out, the coils lose power, **both
contactors open, and both motors are physically disconnected** — including the right-hand one,
which still has a healthy pack B behind it. The robot coasts to a stop instead of pivoting on
its surviving track.

**Decision D8 added a second, independent version of the same protection.** The Teensy's arm
MOSFET sits in the coil chain (see the diagram in section 5), and the Teensy now runs from the
electronics battery. So the chain breaks from either end:

| What dies | What opens the contactors |
|---|---|
| Pack A | Its coils lose their supply directly |
| The electronics battery | The Teensy dies, so its arm MOSFET in the chain opens |

Both give a coast. That is why the coils were left on pack A rather than moved onto the new
battery with everything else: on pack A they are covered from both directions, and on the
electronics battery pack A could die with the contactors still happily closed.

That is the exact failure `01-architecture.md` calls "the consequence that must be tested",
and it is now handled in copper rather than in software. It costs nothing: it is a
consequence of which pack the coil circuit taps, so choose it deliberately.

**It does not make the watchdog optional.** The watchdog covers a different failure: the
Teensy crashing, hanging, or losing its I2C bus **while pack A is still perfectly alive**. In
that case the contactors stay happily closed, the DACs keep holding their last throttle, and
nothing but the watchdog relay will stop the robot. Both mechanisms are needed, and they
catch different things.

**One asymmetry to know about.** Losing pack A stops the robot in hardware, as above. Losing
**pack B** does not: contactor B stays closed but has no power behind it, so the left track
keeps driving and the robot pivots. Only arbitration rule 4 — the Teensy counting hall edges
and seeing a dead track — stops that one. So safety log tests 11 and 12 are not the same
test, even though they read like it. Test 11 proves the wiring; test 12 proves the firmware.

### The ground bond is the only thing tying the electronics to the packs

A separate battery keeps motor return current off the 12 V rail — there is no shared copper
at all — but it creates a new question: what is the electronics ground referenced to?

It cannot float. The Teensy measures the pack voltage dividers, the two ACS758 current sensors
and the throttle line references **against pack negative**. Floating them is trap 3 in
`01-architecture.md` section 3b, and that trap is nasty because it does not announce itself:
a floating analogue reference returns plausible wrong numbers and the Spine acts on them.

**So bond the electronics battery negative to the same single point as the two packs.** One
point, one bond, as in the tree in section 1.

The throttle lines stay opto-isolated regardless (section 7). That isolation was never about
the supply; it is about the controller's throttle ground being its own pack negative.

**Keep the buffer capacitor anyway.** Something in the region of 4700 µF across the 12 V rail.
A battery holds its voltage well; the capacitor covers the inrush when the fans and the
LiDAR all start together.

---

## 4. The amplifier gets its own supply, and NOT the pack directly

Audio is the peakiest load on the robot. A bass note is a 100 W spike. Those spikes must stay
off the 12 V rail, or the USB devices drop out every time the robot speaks. So the
amplifier does not share the 12 V rail.

The obvious move is to run it straight off the pack, because a class-D amplifier of the
TPA3255 family takes a high supply voltage. **That does not work, and the reason is worth
understanding, because it catches people out.**

A pack sold as "48 V" is 48 V *nominal*, not maximum:

| Pack type | Cells | Nominal | **Fully charged** |
|---|---|---|---|
| Li-ion | 13S | 48.1 V | **54.6 V** |
| LiFePO4 | 16S | 51.2 V | **58.4 V** |

The TPA3255's absolute maximum supply is 53.5 V. Either pack exceeds that straight off the
charger. The amplifier would work for weeks — right up until the first drive on a freshly
charged pack, and then it is gone.

**So the amplifier gets a dedicated 48→32 V step-down converter**, sized at about 150 W.

- 32 V is comfortably inside the chip's range with room for supply ripple, and still gives
  roughly 2 × 80 W into 4 Ω, which is far more than loud enough.
- This one does **not** need to be isolated. The amplifier's ground can sit on the pack
  ground; it is the Brain and the Spine that need a clean rail, not the speakers.
- Keep it physically and electrically separate from the 12 V battery rail. The whole point is
  that the two loads do not share a rail.

The cost is one extra converter and one extra fuse on the pack.

> **Check the voltage rating of every part against the FULLY CHARGED pack voltage, not the
> nominal figure.** Then check it again for the LiFePO4 case if the pack chemistry is not yet
> decided. This applies to the controllers, the DC-DC converters, the contactors and the fuses.

---

## 5. Switches, in the order you use them

| # | Device | What it does | When you use it |
|---|---|---|---|
| 1 | **Main disconnect** — an **XT90-S anti-spark** connector on each pack, reachable without tools | Physically separates each pack. Nothing downstream is live. | Before touching any wiring. Before transport. Overnight. |
| 2 | **Emergency stop** — latching mushroom button, red, on the outside of the body | Opens both contactor coils. Motors dead, electronics alive. | Something is going wrong, right now. |
| 3 | **Wireless emergency stop** — a relay on a dedicated receiver | Same effect as the button, from a distance. | The robot is further away than you can run. |
| 4 | **Arm switch** — a toggle on the RC transmitter | Software only. The Spine sends zero. | Normal start and stop of a session. |

### Why the main disconnect is XT90-S, and not XT60

**Short answer: XT60 is the right part for the charge lead and the wrong part for the main
disconnect.** Both were Anderson before. The charge lead is now XT60 and the disconnect is
XT90-S, which is the same family, same tooling, same price bracket.

Three reasons the main disconnect needs the bigger part.

**1. Current.** Look at the tree in section 1: **pack A's disconnect carries everything.**
The motor's 40 A plus the 12 V rail and the amplifier, so about 43 A. An XT60 is rated 60 A,
so that is 72 % of its rating on a connector that is known to run warm past about 40 A. An
XT90 is rated 90 A, which is 48 % — real margin, on the one connector that gets handled
every single day.

**2. It sparks, and XT60 has no answer to that.** Plugging a 48 V pack into the controllers'
input capacitors dumps a large current into them for a few milliseconds, and you get a visible
spark. Every spark pits the contact faces. Pitted contacts have more resistance, more
resistance makes more heat, and heat makes the pitting worse. **The "-S" in XT90-S is an
anti-spark resistor built into the connector**: it pre-charges those capacitors through the
resistor during insertion, so the main contacts meet with the load already charged. There is
no anti-spark XT60.

**3. Mating cycles.** Read the right-hand column of the table above: before touching wiring,
before transport, overnight. That is several cycles a day for months. Anderson SB50 is rated
for hundreds of cycles, and XT90 is in that class. XT60's bullets are not — they loosen, and
a loose high-current contact is the thing that starts fires.

### The one rule you must not get wrong: the socket half goes on the battery

Anderson SB connectors are **genderless** — both halves are identical, with the contacts
recessed inside a housing. That is a safety property we are giving up, and it has to be
replaced by a rule instead.

An XT connector has a pin half and a socket half. **Put the SOCKET half on the battery.**

The main disconnect sits at the pack terminals, ahead of the fuses. So when it is unplugged
overnight, the battery side is live at 54.6 V with **nothing between it and hundreds of amps
of pack**. If that side has exposed pins 7 mm apart, a dropped spanner or a bit of steel
swarf across them is a dead short that no fuse in this robot will interrupt. With the socket
half on the battery, the live contacts are recessed and nothing can bridge them.

Get this backwards and you have built a short circuit that is waiting for a dropped tool.

- Battery side: **socket half**, contacts recessed.
- Load side: pin half.
- Cap both halves when parted. A cheap silicone cap is a fine dust cover and a fine idiot
  guard at the same time.

### The wireless stop has to fail the right way

The wireless stop relay must be wired so that **losing the radio signal opens the circuit.**
A relay that only opens when it receives a "stop" message is useless, because the situation
where you most need it is the situation where the radio has stopped working.

Test this by switching off the stop transmitter, not by pressing its button.

### The coil circuit

```
PACK A +, through the 5 A slow-blow fuse        <- NOT the 12 V rail
   │
   ├─[ MUSHROOM E-STOP ]──  normally closed, latching
   │
   ├─[ WIRELESS STOP RELAY ]── normally closed, opens on signal loss
   │
   ├─[ SPINE ARM OUTPUT ]── a MOSFET the Teensy holds on
   │                        (the Teensy is on the ELECTRONICS BATTERY)
   ├──┬── CONTACTOR A coil ──┐   48 V coils, both of them
   │  └── CONTACTOR B coil ──┤
   │                         │
  PACK A − ──────────────────┘
```

Four things in series, any one of them breaks the chain, both contactors drop. The Spine's
MOSFET being in the chain means a crashed or unpowered Spine also drops the contactors,
which is the behaviour you want.

**Note which supply is where, because the chain spans two of them.** The coils are 48 V and
run from pack A. The Teensy that holds the arm MOSFET on runs from the electronics battery.
That is deliberate, not an oversight: it means the chain opens when *either* supply dies.
Section 3 has the table.

### The contactor must be DC rated

This is the one place in this document where getting it wrong is genuinely dangerous.

Breaking 48 V DC at 40 A draws an arc that does not self-extinguish, because unlike AC the
current never passes through zero. A contactor or relay rated only for AC will weld its own
contacts shut the first time it has to break under load — and then the emergency stop looks
fine and does nothing.

Use a contactor with an explicit DC rating at or above 48 V and 80 A. Albright SW-series and
Gigavac parts are the usual choices.

### Opening a contactor under load is hard on the controllers

When the contactor opens while the motors are pulling current, the motor inductance has
nowhere to dump its energy and the controller input voltage spikes. This is a known way to destroy
controllers.

Two mitigations, both cheap:

- Put a TVS diode across each controller input, chosen to clamp above the maximum pack
  voltage but below the controller's limit.
- For every stop that is **not** an emergency, have the Spine ramp the current to zero first
  and only then drop the contactor. The mushroom button bypasses this on purpose, because an
  emergency stop that waits for software is not an emergency stop.

---

## 6. Wire sizes

Short runs, bundled, in a hot enclosed body. The sizes below already allow for that — do not
take them from a free-air table and go thinner.

| Run | Current | Gauge | Notes |
|---|---|---|---|
| Pack to contactor to controller | 40 A peak | **10 AWG** | Silicone insulated. It has to stay flexible when hot. |
| Controller to hub motor, 3 phases | 40 A peak | **12 AWG** | Or match whatever the motor's own leads are, whichever is thicker. |
| Pack negative to pack negative bond | see below | **10 AWG** | Short and direct. |
| Electronics battery to the 12 V rail | 3.2 A | **14 AWG** | Sized for the 15 A fuse, not the 20 W load. |
| Pack to the amplifier's 32 V converter | 3 A | **16 AWG** | Sized for the 10 A fuse, not the load. |
| 32 V converter to the amplifier | 5 A | **16 AWG** | |
| 12 V rail distribution | 6 A | **16 AWG** | |
| Contactor coils | 0.5 A | **20 AWG** | |
| Throttle lines, DAC to controller | signal | **22 AWG shielded** | Section 7. Shielded, not twisted pair — there is no CAN. |
| Hall sensors and thermistors from the motors | signal | **24 AWG shielded** | Route away from the phase wires. |

### About the ground bond

Size it for the larger of the two motor currents — 40 A — because in normal running each
pack's return current flows through it. It is not a thin reference wire.

**Do not put a fuse in it.** If that fuse ever opened, every measurement the Teensy makes on
the far pack — its voltage divider, its ACS758 current sensor, its throttle line reference —
would lose its common zero while the robot was still driving. And unlike a digital link, which
simply goes quiet, a floating analogue reference keeps returning plausible wrong numbers that
the Spine will act on. That is a worse failure than anything the fuse was protecting against.

---

## 7. The throttle signal path

**There is no data bus to the motors.** The scooter controllers are analogue devices: they see
a throttle voltage and they drive. What this section specifies is the path that voltage travels,
which is fragile and needs care, because it carries no error detection of any kind.

```
  TEENSY 4.0            LEVEL        MCP4725 DAC      OPTO           CONTROLLER
              3.3 V      SHIFT         x2                            throttle in
  ┌────────┐  I2C      ┌───────┐    ┌──────────┐   ┌──────┐        ┌────────────┐
  │ SDA ───┼───────────┼─ 5 V ─┼────┼─ DAC A ──┼───┼─ iso ┼────────┼─ 0-3.3 V L │
  │ SCL ───┼───────────┼─ I2C ─┼────┼─ DAC B ──┼───┼─ iso ┼────────┼─ 0-3.3 V R │
  │        │           └───────┘    └──────────┘   └──────┘        └────────────┘
  │ KICK ──┼──────────────────────► WATCHDOG ─────► RELAY in both throttle lines
  └────────┘                        TLC555
```

Four rules. The first one is the one that can hurt somebody.

1. **The relay in the throttle lines is not optional.** A DAC holds its last output when the
   Teensy dies; it does not fall to zero. Without the watchdog relay, a dead Teensy means a
   robot driving away at whatever throttle it last had. See `01-architecture.md`, "The
   consequence that must be tested", and safety log tests 15 and 16.
2. **Check every DAC write, and stop kicking the watchdog when one fails.** The watchdog only
   fires when the kicks stop. A Teensy that is alive but has lost I2C will keep kicking while
   the throttle sits stuck. The firmware has to choose to kill itself. Safety log test 16.
3. **Shielded cable for the throttle lines, routed away from the phase wires.** These are
   slow analogue signals with no error checking at all, running beside 40 A of switching
   motor current. Noise on one does not produce an error — it produces throttle.
4. **Opto-isolate each throttle line.** The controller's throttle ground is the pack negative
   for that side. Tying the Teensy directly to it puts motor return current through the
   Teensy's ground reference.

---

## 8. Building it so it survives Midburn

Dust and vibration break more festival robots than electrical faults do.

- **Crimp, do not solder, anything that moves or vibrates.** Solder wicks up inside the
  strands and makes a hard spot, and the wire then snaps just past it. Crimp properly, with
  the right tool, and add heatshrink over the joint.
- **Strain relieve every connector.** The load must be on a cable tie or a P-clip, never on
  the connector body.
- **Keep the signal wires away from the phase wires.** Where they have to cross, cross at a
  right angle rather than running alongside.
- **One filtered air path for the electronics.** In and out, with a filter on the inlet and a
  fan pushing air *in* so the body stays at slightly positive pressure. Dust then leaves
  through the gaps instead of being sucked in through them.
- **Nothing important on the floor of the body.** Sand collects there.
- **Label both ends of every wire** before you install it. You will be working on this at
  night, in dust, by torchlight, with someone waiting.

---

## 9. Commissioning order

Do not connect the packs until the end. Work through this with a bench supply set to 48 V and
a current limit of 2 A — a current limit turns a wiring mistake into a beep instead of a fire.

| # | Step | You are checking |
|---|---|---|
| 1 | Bond the pack negatives. Nothing else connected. | Continuity, and that it is the only ground path. |
| 2 | Wire the coil circuit. No contactors yet, just a multimeter where the coils go. | The chain opens when each of the four switches opens. |
| 3 | Add the contactors, still on the bench supply. | They pull in and drop out, and you can hear both. |
| 4 | Add the electronics battery, its 15 A fuse and the 12 V rail. Measure it. | 12 V at the rail, and the bond: **one** path from 12 V negative to pack negative, through the ground bond and nothing else. |
| 5 | Power the Spine only. | It boots, and its arm output holds the contactors in. |
| 6 | Add both controllers and their throttle lines, motors NOT connected. | A multimeter on each throttle line follows the number the Teensy sends, 0 to 3.3 V. |
| 7 | Add one motor, pod on blocks. | It spins the right way, and stops on every fault in `01-architecture.md` section 3. |
| 8 | Add the second motor. | It steers correctly in the air. |
| 9 | Swap the bench supply for the real packs. | Nothing changes. |

Step 4's bonding check is worth doing carefully. You want **exactly one** path from 12 V
negative to pack negative, through the ground bond. Zero paths means every analogue reading
on the packs is floating, which is trap 3. Two or more means you have built a ground loop,
and the motor current will find it.
