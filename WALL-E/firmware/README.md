# Firmware

Two boards, two jobs, and a hard line between them.

| Folder | Board | Job | May it move the robot? |
|---|---|---|---|
| `spine/` | Teensy 4.0 | Motor commands, every safety rule, the watchdog | **Yes. Only this board.** |
| `face/` | ESP32-S3 × 2 | Eye animation, head servos | No. It has no connection to the motors at all. |

The Brain (the Jetson) lives in `../brain/` and is Python, not firmware.

---

## The Spine

**Board:** Teensy 4.0. **Library:** `Wire` only — it ships with Teensyduino.

Build with the Arduino IDE (install Teensyduino first) or PlatformIO. Select
Teensy 4.0 and upload. There is nothing to configure at build time — every
tunable number is in `spine/config.h`.

> **There is no CAN bus.** Decision D7 replaced the VESCs with the scooter
> controllers already owned, and this firmware was rewritten for that on
> 2026-09-22. `FlexCAN_T4` is gone. If you ever go back to VESCs, that rewrite
> reverses: the DAC output and the sensors below go away, and the CAN layer
> comes back, along with two 3.3 V CAN transceivers that are deliberately not
> in the BOM.

### What it does

One loop at 1 kHz. Every pass it rebuilds the motor commands from scratch using
the fixed rule order in `../docs/01-architecture.md` section 3. The rules are in
`arbitrate()` in the same order as the document, with the rule numbers in the
comments, so the two can be checked against each other.

### How it drives a scooter controller

A scooter controller takes a **throttle voltage** and tells you nothing back.
So the Spine does all of this itself:

| What | How |
|---|---|
| Speed | MCP4725 DAC per side, through a level shifter (the Teensy is **not** 5 V tolerant) |
| Direction | a separate opto-isolated **reverse** line per side |
| Stopping hard | an opto-isolated **e-brake** line per side, the same input the E-stop uses |
| Pack voltage (rules 5, 11) | a resistor divider per pack into an analogue pin |
| Motor temperature (rule 9) | each hub motor's **own thermistor** |
| Is the track alive? (rule 4) | counting that motor's **hall edges** |
| Motor current | ACS758 per pack — telemetry only, no rule depends on it |

### Pins

| Pin | Use |
|---|---|
| 0, 1 | Serial1 — iBus from the RC receiver |
| 2 | Arm output → contactor coil MOSFET. LOW = contactors drop |
| 3 | E-stop sense, active LOW |
| 4 | ToF ring reset |
| **5** | **Watchdog kick — see below** |
| 6, 7 | Reverse line, left / right |
| 8, 9 | E-brake line, left / right |
| 10, 11 | Hall input, left / right |
| 13 | On-board LED heartbeat |
| 18, 19 | I2C — the two DACs and the ToF multiplexer |
| A0, A1 | Pack voltage divider, left / right |
| A2, A3 | ACS758 current, left / right |
| A6, A7 | Motor thermistor, left / right |

### The watchdog is the most important wire on the robot

A VESC releases the motor if it stops being commanded. **A scooter controller
never does**, and the DAC holds its last voltage forever. So if this board
crashes mid-drive, the robot keeps going at whatever throttle it had.

The only thing that stops it is the hardware watchdog: pin 5 square-waves while
the firmware is healthy, holding a **normally-closed** relay open. Stop the
pulses and the relay falls closed and shorts both throttle lines to ground.
Nothing in software has to work for that to happen.

`wdt_kick()` refuses to kick when the last DAC write failed. That is not a bug
and it is not optional — see the gotchas at the bottom.

### Before you flash it to a robot that can move

Read the five rules at the top of `spine/spine.ino`. The short version: no
dynamic memory, nothing that blocks, nothing with unbounded runtime, every new
failure path ramps to zero, and features belong on the Brain.

Then **measure your own throttle** and put the numbers in `config.h`:
`THROTTLE_REST_V` and `THROTTLE_FULL_V`. Read the scooter throttle's signal
wire at rest and at full with a multimeter. The defaults (0.80 V and 4.20 V)
are typical, not yours. Get them wrong and the robot either creeps when it
should be stopped, or never reaches full speed.

Calibrate `VOLT_SCALE_L` and `VOLT_SCALE_R` the same way: multimeter on the
pack, compare with the telemetry line, correct until they agree. Rule 11
divides by that number.

### Still to do

`tof_poll()` is empty. The bumper ring is not implemented yet.

This is deliberately failing in the safe direction: with no valid sensor
readings, `bumper_scale()` returns 0.5 and halves the speed. **Do not make it
return 1.0 to get full speed for a test.** That silently switches off the veto,
and it is exactly the kind of temporary change that stays in.

### Testing it without a robot

The Brain link is plain text, so you can drive the board from a serial
terminal at 115200:

```
C 0.2 0.0 1
```

means "20 % forward, no turn, sequence 1". Send one every 50 ms or the
watchdog will stop obeying you, which is itself a good first test. The board
prints a status line 20 times a second, including why it is not moving:

```
S 12345 manual running duty 0.200 0.200 v 49.8 49.6 t 31 30 i 2.1 2.0 hall 8123 8110 rc 1 brain 1 dac 1
```

`dac 1` means this board still controls the throttle. If it ever reads `0`, the
hardware watchdog should already have stopped the robot.

The tests that matter for this firmware are in `../docs/03-safety-log.md`:
**8** (throttle wire pulled — both tracks must stop), **15** (Spine unpowered),
**16** (Teensy alive but I2C dead), and **17** (reverse line glitch).

---

## The Face

**Board:** ESP32-S3, two of them, one per eye. **Libraries:** LovyanGFX.

### Same binary on both boards

Tie `PIN_EYE_SELECT` to ground on the left board and leave it floating on the
right. The firmware works out which eye it is at boot. There is only ever one
binary to keep track of, and swapping in a spare board in the field needs no
laptop.

### Why two boards and not one

The 480×480 round panels are QSPI and need real bandwidth. One ESP32-S3 can
*probably* drive two, and would then tear the moment you add anything else.
Two boards at 12 dollars each removes the risk and means one eye keeps working
if the other board dies. `../docs/05-bom.md` section 4.

The two are kept in step by a single wire: the left board pulses it, the right
board starts its frame on the pulse. If that wire breaks, each eye runs on its
own clock and the only symptom is that the blinks drift apart slightly.

### Still to do

`face/panel_cfg.h` is a placeholder. The QSPI panel's init sequence and pin
mapping have to be copied from the vendor's example for the exact module you
buy — it is the one part of this project that cannot be worked out from first
principles.

Everything else runs without it. You can develop and test the whole animation
over the serial link with no screen attached, which is worth doing because the
animation is the hard part.

### Testing it

Three commands, typed by hand at 115200:

```
GAZE -20 5
MOOD curious
BLINK
```

Moods: `idle`, `curious`, `happy`, `sad`, `alarm`, `sleepy`.

If the link goes quiet for 1.5 seconds the eyes fall back to an idle
behaviour — drifting around, blinking now and then. That is on purpose: a
crashed Jetson should leave a robot that looks bored, not one that looks
broken. Frozen eyes read as "switched off" to everyone watching.

---

## The three details in here that are easy to get wrong

**The slew limiter's direction.** In `spine.ino`, `slew1()` treats "up" as away
from zero and "down" as towards zero. Swap them and stopping becomes slower
than starting, which is the wrong way round and would not be obvious from
watching the robot drive.

**`wdt_kick()` must stay gated on `output_ok`.** It looks like a bug — the
board is alive, so why not kick the watchdog? Because the watchdog's job is to
stop the robot when the **throttle** is out of control, not when the CPU is.
A Teensy that is running fine but has lost the I2C bus to a DAC would otherwise
keep kicking happily while the throttle stayed stuck at its last value. That
blind spot is closed by refusing to kick. Safety log test 16.

**The reverse line is never flipped while the wheel is turning.** `side_out()`
commands zero and waits for the halls to fall silent first. Scooter controllers
commonly refuse to change direction under motion, and some are damaged by being
asked. Removing that interlock would make direction changes feel snappier on
the bench and would eventually break a controller. Safety log test 17.
