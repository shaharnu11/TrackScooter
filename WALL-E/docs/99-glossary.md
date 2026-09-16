# Glossary

Every technical word used in this project, explained in plain words. Read this first.
Words are grouped by subject, not alphabetically, because related words are easier to learn
together.

---

## Boards and computers

**Microcontroller**
A very small computer on a single chip. It has no screen, no operating system, and no hard
disk. It runs exactly one program, forever, in a loop. Because there is no operating system,
nothing can interrupt it. That makes it slow at big jobs but perfectly reliable at timing.
An Arduino is a microcontroller.

**SBC (Single Board Computer)**
A full computer on one small board. It runs Linux, has USB ports, and can run heavy
software like AI models. A Raspberry Pi is an SBC. It is powerful but its timing is not
guaranteed, because Linux decides when your program gets to run.

**Teensy 4.1**
The microcontroller we use for the Spine. It is like an Arduino but much faster (600 MHz).
We chose it because it has CAN built in and is very well supported.

**ESP32-S3**
A cheap microcontroller with WiFi and Bluetooth built in, and enough speed to drive small
screens. We use it for the Face. We will not use its WiFi.

**Jetson Orin Nano**
An SBC made by NVIDIA with a graphics chip built in. The graphics chip is what makes AI
models run fast. We use it for the Brain.

**Firmware**
The program that lives inside a microcontroller. Same idea as software, but the word
"firmware" is used because it is burned into the chip and does not change often.

**Flashing / uploading**
Copying your program into a microcontroller over a USB cable. You do this every time you
change the code.

---

## Talking between boards

**Serial (UART)**
The simplest way for two boards to talk. Two wires: one for sending, one for receiving.
Both sides must agree on the speed, called the **baud rate** (for example 115200). Easy to
set up, but only connects two devices.

**CAN bus (Controller Area Network)**
A tougher way for *many* devices to share two wires. It was invented for cars, so it
survives electrical noise, long cables, and vibration. Every message carries an address, so
all devices hear every message and each one picks out the messages meant for it.

We use CAN between the Spine and the two motor controllers. This is the right choice because
motor wires create a lot of electrical noise, and plain serial would get corrupted.

**Transceiver**
A small chip that converts between the microcontroller's weak signal and the tough
CAN signal on the wire. The Teensy has the CAN logic built in but *not* the transceiver, so
you must buy a small transceiver board separately. Forgetting this is a common mistake.

**Termination resistor**
A 120 ohm resistor fitted at each of the two far ends of a CAN cable. Without it, signals
bounce back down the wire like an echo and corrupt the data. You need exactly two, one at
each end, not one per device.

**I2C**
Another two-wire system, for connecting small sensors over short distances. Slower and more
fragile than CAN, but almost every cheap sensor uses it. Each device on the wire needs a
different address.

**PWM (Pulse Width Modulation)**
Switching a voltage on and off very fast. If it is on half the time, the device behaves as
if it got half the voltage. This is how motor speed and servo position are controlled. The
fraction of on-time is called the **duty cycle**.

---

## Motors and driving

**Hub motor**
A motor built inside a wheel. The pods use the scooter's hub motors. It is a
**direct drive** motor, meaning there are no gears between the motor and the load.

**Why direct drive matters here:** with no gears, making the robot go slowly means turning
the motor slowly. A motor turning slowly still has to push hard, so it draws a lot of
electrical current. Current makes heat, and a slowly turning motor has no airflow to cool
itself. So a slow, heavy robot can overheat its motors. This is a real risk in a 40 °C
desert and we design around it.

**BLDC (Brushless DC motor)**
The type of motor in the pods. It cannot be driven by simply connecting a battery. It needs
an electronic controller that switches three wires in the right order, hundreds of times per
second.

**Motor controller / ESC**
The box that does that switching. ESC means Electronic Speed Controller. It takes a command
("go 30%") and the battery power, and drives the motor.

**VESC**
A specific, open-source motor controller design, very popular for electric skateboards and
scooters. You can command it over CAN from your own code, set safety limits inside it, and
read the motor temperature back.

**We are not using VESCs.** Decision D7, 2026-09-17: the two 48 V scooter controllers are
already owned, and they have a reverse line, so they do the job for nothing. They only accept
a throttle voltage and tell you nothing back. Everything the VESC would have reported — speed,
pack voltage, current, motor temperature — is now a separate sensor on the list, and the
command timeout it would have given for free is now the hardware watchdog. See `05-bom.md`
section 1b for what that costs and `01-architecture.md` for why the watchdog is mandatory.

VESC still matters as a word here, because two CAN transceivers stay in the drawer and moving
to VESCs is the planned fallback if the controllers judder at walking pace.

**DAC**
Digital to Analogue Converter. The opposite of the ADC below. The Teensy sends a number over
I2C and the MCP4725 turns it into a voltage between 0 and 3.3 V, which is what the scooter
controller wants to see instead of a twist grip. **A DAC holds its last value when the board
driving it dies** — it does not fall to zero. That single fact is why the robot needs a
hardware watchdog.

**Hardware watchdog**
A separate timer chip that the main board must "kick" regularly. If the kicks stop, the chip
acts on its own — here, it opens a relay in both throttle lines. It is deliberately dumb and
deliberately not running your code, so that it still works when your code is what failed.

**Torque**
Turning force. Not the same as speed. A motor can push very hard while barely turning.

**Current control vs duty control vs RPM control**
Three different ways to command a motor controller.
- **Duty** means "apply 30% of the battery voltage". Behaves most like a throttle pedal. Easy
  to understand and predictable. This is what we start with.
- **Current** means "push with this much force". The motor then goes whatever speed the world
  allows. Good for rough ground.
- **RPM** means "turn at exactly this speed", and the controller fights to hold it. This
  fights against track slip on sand, so we avoid it.

**Skid steer (also called differential drive or tank steer)**
Turning by driving the left and right sides at different speeds. There is no steering joint
at all. To turn left, slow the left track. To spin in place, drive one track forward and the
other backward.

**Scrub**
When a track slides sideways across the ground during a turn instead of rolling. Skid steer
always scrubs. Scrub wears out the track and needs extra motor force. On sand it is mild,
because the sand moves instead of the rubber. On tarmac it is harsh.

**Mixing**
Turning a joystick position into two motor commands. The stick gives you forward/back and
left/right. Mixing converts those into a left motor value and a right motor value. For
example: `left = forward + turn`, `right = forward − turn`.

**Slew rate limiting**
Refusing to change a motor command instantly. If the driver slams the stick from zero to
full, slew limiting ramps it up over half a second instead. This stops violent jerks, saves
the tracks, and stops the robot from tipping.

---

## Safety words

**E-stop (emergency stop)**
A big red mushroom button that cuts power. Real ones are **physical**: pressing them opens
an actual electrical contact. They do not ask software for permission, because software can
be broken. Ours also has a wireless version on a keyfob, held by a person watching the
robot.

**Contactor**
A large electrically operated switch that can carry the full battery current. The E-stop
does not break the motor current itself; it breaks the small coil current that holds the
contactor closed, and the contactor then opens the main power.

**Watchdog**
A timer that resets a system if it stops being told "I am alive". Our Spine has one: the
Brain must send a **heartbeat** message every 50 ms. If two heartbeats in a row go missing,
the Spine assumes the Brain is dead and stops the motors.

**This is the single most important safety feature in the project.** Without it, if the
Brain freezes while the robot is moving, the last command keeps running and a heavy machine
drives into a crowd.

**Failsafe**
Designing so that a failure results in a safe state, not a dangerous one. "Lost radio
signal means stop" is failsafe. "Lost radio signal means keep going" is not.

**Arbitration**
Choosing between several sources that all want to control something. Our Spine listens to
the radio, the Brain, and the bumper sensors, and has a fixed order of priority for deciding
who wins.

**Veto**
When one system is allowed to cancel another system's command but never to give its own.
The bumper sensors have a veto: they can say "no, do not drive forward", but they can never
say "drive left".

---

## Sensors

**LiDAR**
A spinning laser that measures distance in every direction, giving a flat map of what is
around the robot. Works in total darkness, which matters because Midburn happens at night.
Bright sun and thick dust can confuse cheap ones.

**Stereo camera**
Two cameras side by side. By comparing the two pictures, the distance to things can be
calculated, the same way two eyes give you depth. Needs light, so it fails at night unless
you add your own.

**Depth camera / RGB-D**
Any camera that gives distance as well as colour. A stereo camera is one kind.

**ToF sensor (Time of Flight)**
A small cheap sensor that fires an invisible light pulse and times the echo. Measures
distance in one narrow direction only, up to a few metres. We use several as a bumper.

**Occupancy grid**
A simple map made of squares, where each square is marked "free", "blocked", or "unknown".
This is how obstacle sensor data gets turned into something a program can decide with.

**SLAM (Simultaneous Localisation and Mapping)**
Software that builds a map while also working out where you are in it, using a camera or
LiDAR. Impressive, but it needs fixed landmarks and a still scene. **We are not using it.**
Open desert has no landmarks and the crowd keeps moving, which breaks it. Plain GPS works
better in exactly this situation.

**GPS**
Position from satellites. Normally accurate to 2 to 3 metres. That is plenty for "stay
inside this area" and "head back to camp" in an open desert.

**RTK GPS**
A more accurate version using a second fixed receiver, good to a few centimetres. A possible
upgrade later. Not needed at the start.

**Magnetometer / compass**
Measures the direction of the earth's magnetic field, so the robot knows which way it is
pointing. Must be mounted far from the motors and the battery cables, or their magnetic
fields will ruin the reading.

---

## AI words

**Model**
A trained AI program. Different models do completely different jobs. This project uses three
separate ones and they have nothing in common.

**Inference**
Running a trained model to get an answer. As opposed to **training**, which is creating the
model in the first place. We only do inference, and we do it on the robot.

**Offline / local / on-device**
Running on the robot itself, with no internet. Everything in this project is offline,
because there is no network in the desert.

**LLM (Large Language Model)**
The kind of AI that understands and writes language. ChatGPT is one. Small versions can run
offline on the Jetson. It takes 1 to 3 seconds to answer.

**It must never control the motors.** It is far too slow, and it can give surprising
answers. It is allowed to choose from a short fixed list of behaviours, and a simple
reliable program carries the choice out.

**Parameters, and "7B"**
The size of an AI model, counted in billions of adjustable numbers. "7B" means 7 billion.
Bigger is smarter and slower, and needs more memory.

**Quantisation**
Shrinking a model by storing its numbers less precisely. A 7B model might need 14 GB of
memory normally, but about 4 GB quantised, with only a small loss of quality. This is what
makes offline AI on a small board possible at all.

**TOPS (Tera Operations Per Second)**
A rough measure of how fast an AI chip is. Trillions of calculations per second. The Jetson
Orin Nano does about 67.

**NPU (Neural Processing Unit)**
A chip built only for AI. Fast and power-efficient, but only for the kinds of models it was
designed for. Some NPUs are great at vision and poor at language models, which is why the
Jetson's general-purpose graphics chip is a safer choice for us.

**YOLO**
A well-known family of fast models that find objects in a picture and draw boxes around
them. We use one to find people and faces, 15 to 30 times a second.

**Whisper**
An offline model that turns speech into text. Made by OpenAI, free to run yourself.

**TTS (Text To Speech)**
Turning text into spoken audio. **Piper** is a good offline one. For WALL-E, short recorded
sound clips will probably beat TTS, since his voice is famous sound design rather than
speech.

---

## Electrical words

**DC-DC converter**
A circuit that changes one DC voltage into another, for example the 48 V battery down to the
5 V the Jetson needs.

**Isolated**
A converter where the input and the output share no wires, only a magnetic link. This stops
noise and voltage dips on the motor side from reaching the computers.

**Brownout**
When the voltage dips too low for a moment and a computer resets. Motor current spikes cause
this. It is why the computers get their own isolated power supply and a small backup, and
not a shared wire with the motors.

**Supercapacitor**
A component that stores a small amount of energy and can release it very fast. Used to hold
a voltage steady through a brief dip.

**Fuse**
A deliberate weak point that melts and breaks the circuit if too much current flows. Every
branch of the wiring gets one, sized for that branch.

**AWG (American Wire Gauge)**
A wire thickness number. **Confusingly, a smaller number means a thicker wire.** 10 AWG is
thick and carries a lot of current; 22 AWG is thin and is for signals.

**Ground / common**
The shared zero-volt reference. Two boards that talk to each other must share a ground wire,
or the signals mean nothing. A very common cause of "it does not work".

**Ground loop**
When ground is connected by two different paths, so current flows through the ground wire
itself and corrupts signals. Avoided by having one single point where everything's ground
joins.
