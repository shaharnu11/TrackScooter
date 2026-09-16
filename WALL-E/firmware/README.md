# Firmware

Two boards, two jobs, and a hard line between them.

| Folder | Board | Job | May it move the robot? |
|---|---|---|---|
| `spine/` | Teensy 4.1 | Motor commands, every safety rule, the watchdog | **Yes. Only this board.** |
| `face/` | ESP32-S3 × 2 | Eye animation, head servos | No. It has no connection to the motors at all. |

The Brain (the Jetson) lives in `../brain/` and is Python, not firmware.

---

## The Spine

**Board:** Teensy 4.1. **Library:** FlexCAN_T4, which ships with Teensyduino.

Build with the Arduino IDE (install Teensyduino first) or PlatformIO. Select
Teensy 4.1 and upload. There is nothing to configure at build time — every
tunable number is in `spine/config.h`.

### What it does

One loop at 1 kHz. Every pass it rebuilds the motor commands from scratch using
the fixed rule order in `../docs/01-architecture.md` section 3. The rules are in
`arbitrate()` in the same order as the document, with the rule numbers in the
comments, so the two can be checked against each other.

### Before you flash it to a robot that can move

Read the five rules at the top of `spine/spine.ino`. The short version: no
dynamic memory, nothing that blocks, nothing with unbounded runtime, every new
failure path ramps to zero, and features belong on the Brain.

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
prints a status line 20 times a second, including why it is not moving.

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

## The two details in here that are easy to get wrong

**The slew limiter's direction.** In `spine.ino`, `slew1()` treats "up" as away
from zero and "down" as towards zero. Swap them and stopping becomes slower
than starting, which is the wrong way round and would not be obvious from
watching the robot drive.

**Unknown CAN packets must not refresh the timeout.** In `on_can_rx()`, a
packet type we do not recognise returns *before* setting `last_ms`. If it did
not, a VESC that had stopped reporting its status but was still sending
something else would look alive to arbitration rule 4.
