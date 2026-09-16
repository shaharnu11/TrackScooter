# 04 — Power and wiring

Every wire on the robot, what size it has to be, and why. Read `01-architecture.md` first —
this document is the physical version of the rules in there.

Two decisions from the architecture drive everything here:

- **Each pack feeds its own pod.** The positives never meet. The negatives are bonded at one
  point. (`01-architecture.md` section 3b.)
- **The electronics run from the larger pack**, through one isolated converter.

---

## 1. The power tree

```
PACK A — larger, 48 V, 20 Ah                 (capacity is a placeholder)
 +─┬── FUSE 60 A ──── CONTACTOR A ────────── VESC LEFT ──── hub motor, left pod
   │
   ├── FUSE 10 A ──── DC-DC 48→12 V ───────── 12 V RAIL     (see section 3)
   │                  isolated, 100 W
   │
   └── FUSE 10 A ──── DC-DC 48→32 V ───────── AUDIO AMPLIFIER
                      non-isolated, 150 W    (why 32 V and not 48: section 4)

PACK B — smaller, 48 V, 15 Ah
 +─┬── FUSE 60 A ──── CONTACTOR B ────────── VESC RIGHT ─── hub motor, right pod


PACK A (−) ══════════ GROUND BOND ══════════ PACK B (−)
                   10 AWG, short, NOT FUSED
```

### Three things about that tree

**The two taps on pack A come off BEFORE contactor A.** This is deliberate. It means pressing
the emergency stop kills both motors but leaves the Spine, the Brain and the face powered. The
robot can then tell you it is stopped, log why, refuse to re-arm until the button is reset, and
put a message on the eyes. If the electronics died with the motors, you would get a machine
that goes dark and silent and tells you nothing.

**The emergency stop is therefore not an isolator.** It stops movement. It does not make the
robot electrically safe to work on. For that you need the separate main disconnect in section
5. Do not confuse the two, and do not let a helper confuse them either.

**Two contactors, one coil circuit.** Because the packs are separate, one contactor cannot cut
both. Both coils are wired in parallel onto the same emergency stop chain, so any single break
drops both sides together. Never wire a stop that can cut one track and leave the other
driving — on a skid-steer machine that is a command to spin, not a command to stop.

---

## 2. How much current, really

These are the numbers the wire sizes and fuses come from. The robot is 91 kg
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
| Absolute limit set in the VESC | **40 A** | the number the wire and the fuse must survive |

Set the VESC's motor current limit to 40 A and its **battery** current limit to 40 A as well.
The battery limit is the one that protects the pack and the fuse, and it is easy to forget
because it is a separate setting.

---

## 3. The 12 V rail

| Load | Continuous | Peak |
|---|---|---|
| Jetson Orin Nano, with the camera and LiDAR on its USB | 25 W | 40 W |
| Cooling fans | 5 W | 5 W |
| 12→5 V converter, feeding the Teensy, the ESP32 and the head servos | 8 W | 20 W |
| Contactor coils, both | 6 W | 6 W |
| **Total** | **44 W** | **71 W** |

So a **100 W isolated 48→12 V converter** is the right part: comfortable at the continuous
load, and it rides out the peak. Drawn from a 48 V pack that is 1.15 A, which is exactly the
electronics current the runtime calculation in `01-architecture.md` section 3b assumes.

**It must be an isolated converter.** A non-isolated buck converter shares its negative with
the pack, which puts the motor return current through the same copper as the Jetson's ground
reference. Every time the motor current changes, the Jetson's idea of zero volts moves. The
symptoms are horrible and hard to diagnose: USB devices dropping out, the camera
disconnecting, random reboots under acceleration.

**Put a buffer capacitor on the 12 V rail.** Something in the region of 4700 µF. Motor current
spikes pull the pack voltage down for a few milliseconds, and the converter's output sags with
it. The capacitor covers the gap. Without it, a hard start can reboot the Jetson, which means
losing the eyes exactly when the robot is doing something interesting.

---

## 4. The amplifier gets its own supply, and NOT the pack directly

Audio is the peakiest load on the robot. A bass note is a 100 W spike. Those spikes must stay
off the rail the Jetson sits on, or the camera drops out every time the robot speaks. So the
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
  ground; it is the Jetson that needs isolating, not the speakers.
- Keep it physically and electrically separate from the 12 V converter. The whole point is
  that the two loads do not share a rail.

The cost is one extra converter and one extra fuse on the pack.

> **Check the voltage rating of every part against the FULLY CHARGED pack voltage, not the
> nominal figure.** Then check it again for the LiFePO4 case if the pack chemistry is not yet
> decided. This applies to the VESCs, the DC-DC converters, the contactors and the fuses.

---

## 5. Switches, in the order you use them

| # | Device | What it does | When you use it |
|---|---|---|---|
| 1 | **Main disconnect** — an Anderson connector on each pack, reachable without tools | Physically separates each pack. Nothing downstream is live. | Before touching any wiring. Before transport. Overnight. |
| 2 | **Emergency stop** — latching mushroom button, red, on the outside of the body | Opens both contactor coils. Motors dead, electronics alive. | Something is going wrong, right now. |
| 3 | **Wireless emergency stop** — a relay on a dedicated receiver | Same effect as the button, from a distance. | The robot is further away than you can run. |
| 4 | **Arm switch** — a toggle on the RC transmitter | Software only. The Spine sends zero. | Normal start and stop of a session. |

### The wireless stop has to fail the right way

The wireless stop relay must be wired so that **losing the radio signal opens the circuit.**
A relay that only opens when it receives a "stop" message is useless, because the situation
where you most need it is the situation where the radio has stopped working.

Test this by switching off the stop transmitter, not by pressing its button.

### The coil circuit

```
12 V RAIL
   │
   ├─[ MUSHROOM E-STOP ]──  normally closed, latching
   │
   ├─[ WIRELESS STOP RELAY ]── normally closed, opens on signal loss
   │
   ├─[ SPINE ARM OUTPUT ]── a MOSFET the Teensy holds on
   │
   ├──┬── CONTACTOR A coil ──┐
   │  └── CONTACTOR B coil ──┤
   │                         │
  GND ───────────────────────┘
```

Four things in series, any one of them breaks the chain, both contactors drop. The Spine's
MOSFET being in the chain means a crashed or unpowered Spine also drops the contactors,
which is the behaviour you want.

### The contactor must be DC rated

This is the one place in this document where getting it wrong is genuinely dangerous.

Breaking 48 V DC at 40 A draws an arc that does not self-extinguish, because unlike AC the
current never passes through zero. A contactor or relay rated only for AC will weld its own
contacts shut the first time it has to break under load — and then the emergency stop looks
fine and does nothing.

Use a contactor with an explicit DC rating at or above 48 V and 80 A. Albright SW-series and
Gigavac parts are the usual choices.

### Opening a contactor under load is hard on the VESCs

When the contactor opens while the motors are pulling current, the motor inductance has
nowhere to dump its energy and the VESC input voltage spikes. This is a known way to destroy
controllers.

Two mitigations, both cheap:

- Put a TVS diode across each VESC input, chosen to clamp above the maximum pack voltage but
  below the VESC's limit.
- For every stop that is **not** an emergency, have the Spine ramp the current to zero first
  and only then drop the contactor. The mushroom button bypasses this on purpose, because an
  emergency stop that waits for software is not an emergency stop.

---

## 6. Wire sizes

Short runs, bundled, in a hot enclosed body. The sizes below already allow for that — do not
take them from a free-air table and go thinner.

| Run | Current | Gauge | Notes |
|---|---|---|---|
| Pack to contactor to VESC | 40 A peak | **10 AWG** | Silicone insulated. It has to stay flexible when hot. |
| VESC to hub motor, 3 phases | 40 A peak | **12 AWG** | Or match whatever the motor's own leads are, whichever is thicker. |
| Pack negative to pack negative bond | see below | **10 AWG** | Short and direct. |
| Pack to the 48→12 V converter | 1.2 A | **16 AWG** | Sized for the 10 A fuse, not the load. |
| Pack to the amplifier's 32 V converter | 3 A | **16 AWG** | Same reason. |
| 32 V converter to the amplifier | 5 A | **16 AWG** | |
| 12 V rail distribution | 6 A | **16 AWG** | |
| Contactor coils | 0.5 A | **20 AWG** | |
| CAN bus | signal | **22 AWG twisted pair** | Section 7. |
| Hall sensors and thermistors from the motors | signal | **24 AWG shielded** | Route away from the phase wires. |

### About the ground bond

Size it for the larger of the two motor currents — 40 A — because in normal running each
pack's return current flows through it. It is not a thin reference wire.

**Do not put a fuse in it.** If that fuse ever opened, the CAN bus would lose its common
reference while the robot was still driving, and the Spine would stop being able to talk to
the VESCs. That is a worse failure than anything the fuse was protecting against.

---

## 7. The CAN bus

500 kbit/s, three devices: Spine, left VESC, right VESC.

```
   SPINE                VESC LEFT              VESC RIGHT
 ┌────────┐            ┌────────┐             ┌────────┐
 │ CANH ──┼────────────┼── CANH ┼─────────────┼── CANH │
 │ CANL ──┼────────────┼── CANL ┼─────────────┼── CANL │
 └───┬────┘            └────────┘             └───┬────┘
   120 Ω                                        120 Ω
```

Four rules, and breaking any of them gives you an intermittent bus, which is the worst kind
of fault to chase:

1. **One line, two ends.** Devices tap onto the pair; they do not each get their own branch
   back to the Spine. A star layout does not work on CAN.
2. **120 Ω at each end of the line, and nowhere else.** The Spine is one end, the far VESC is
   the other. The middle VESC gets no resistor. Most VESCs have a solder jumper for this —
   check which way it is set rather than assuming.
3. **Twisted pair.** This is what makes CAN survive next to motor phase wires. Untwisted CAN
   in a robot like this will work on the bench and fail under load.
4. **The pack negatives must already be bonded** (section 1), or the two ends of the bus have
   no shared idea of zero volts.

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
| 4 | Add the 48→12 V converter and the 12 V rail. Measure it. | 12 V, and the isolation: no continuity from 12 V negative to pack negative. |
| 5 | Power the Spine only. | It boots, and its arm output holds the contactors in. |
| 6 | Add the CAN bus and both VESCs, motors NOT connected. | Both VESCs appear on CAN and report their input voltage. |
| 7 | Add one motor, pod on blocks. | It spins the right way, and stops on every fault in `01-architecture.md` section 3. |
| 8 | Add the second motor. | It steers correctly in the air. |
| 9 | Swap the bench supply for the real packs. | Nothing changes. |

Step 4's isolation check is worth doing carefully. If the converter turns out not to be
isolated, you want to know before the Jetson is connected to it.
