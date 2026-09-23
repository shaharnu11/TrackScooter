# Brain

The owner's Dell XPS 15 9510. Python. Runs the camera list, a small local
language model, the personality and the sounds. **No internet.**

**This is the part that is allowed to be slow, and allowed to crash.** If it
dies, the driver keeps full control of the robot, because the radio receiver
wires into the Spine and not into here. A Brain crash costs you the eyes and
the sounds. `../docs/01-architecture.md` section 2.

The laptop sits closed on a lift-out tray (the upper floor), on spacers. The
USB-C PD power bank of 65 W or more stays on the **lower** deck with the 12 V
battery and the motor controllers. A powered USB 3 hub (fed from the robot
12 V rail) sits on the tray next to the laptop and carries the OAK-D, the
LiDAR, the Teensy and the Face boards. Unbolt the speaker boxes, then lift the
tray out.

---

## Files

| File | What it is |
|---|---|
| `main.py` | The 20 Hz control loop. Start here. |
| `spine_link.py` | Serial to the Teensy. Commands out, telemetry in. |
| `face_link.py` | Serial to the two eye boards. |
| `perception.py` | Camera, LiDAR and IMU threads. Currently stubs. |
| `personality.py` | The state machine that picks a behaviour. |
| `test_safety.py` | Checks the invariants that keep the personality harmless. |

## Running it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python3 main.py --spine /dev/ttyACM0 --face /dev/ttyUSB0 /dev/ttyUSB1
```

On Windows the port names are `COM` numbers, not `/dev/tty*`.

Only `pyserial` is needed to run the loop. The sensor libraries are commented
out in `requirements.txt` until the hardware exists.

Run the invariant checks with no dependencies at all:

```bash
python3 test_safety.py
```

---

## The three things in here that are load-bearing

### 1. The heartbeat is the command, and it comes from the control loop

Not from a separate thread. This is the most important line in the whole Brain,
and it is easy to get wrong in a way that looks like an improvement.

A heartbeat on its own thread never misses a beat — which means it keeps
telling the Spine "I am healthy" while the thinking part of the program is
frozen. That defeats the watchdog, and the watchdog is the main safety feature
of the architecture. **If the control loop stalls, the beat must stall with
it.**

Note also that a zero command is still a heartbeat. "I am alive and I want
nothing" and "I am dead" must stay distinguishable, so `main.py` sends a
command every single pass, even when it is zero.

### 2. The AI never produces a motor number

The personality chooses an **action** from a fixed list of six names:

```
idle · look_at · greet · retreat · nudge_forward · play_sound
```

A dull table lookup in `motion_for()` turns the name into a speed and a turn.
The chooser can be a state machine today and a 3B local language model
tomorrow, and it makes no difference to the safety argument — because there is
no way to say "0.8 duty for four seconds" in that vocabulary.

The language model, if used, runs **on the laptop, offline**. Cloud APIs are
not used. Recorded WALL-E sounds beat spoken sentences for this character.

`test_safety.py` enforces this. It checks that every action, including any
added later, stays inside 30 % and that no action is missing from the table.

### 3. Stale data must look stale, not clear

Every reading in `perception.py` carries the time it was taken, and callers
check `fresh` before trusting it. A sensor that has stopped updating must look
like a sensor that stopped — never like a sensor reporting "all clear".

`main.py` applies this to the IMU: no fresh pitch reading blocks movement,
rather than being treated as level. The same rule is in the Spine firmware,
where a bumper ring with no working sensor halves the speed instead of
reporting a clear path.

---

## Sensor threads and why there are no queues

The slow work runs in threads and writes into a single slot, overwriting
whatever was there. A queue would let a backlog build up, and the robot would
end up reacting to where a person was five seconds ago. For control, a
stale-but-current reading is right and a complete history is wrong.

## Still to do

All three sensor loops in `perception.py` are empty. In rough order of value:

1. **The IMU.** Smallest job, and it is a real safety input — the robot tips
   forward at 19.4° and the anti-tip castor catches it at 9.9°.
2. **The camera.** The OAK-D Lite runs the detection model on its own chip, so
   this thread only converts finished boxes into angles and distances.
3. **The LiDAR.** Occupancy for later slow self-drive. The ToF ring on the
   Spine already covers the close-range safety case.

Sounds are not implemented at all. `Intent.sound` is carried through the
personality and then ignored.
