# Glossary

## Boards

**Teensy 4.0** — Spine. 600 MHz, no OS. **Not 5 V tolerant.**

**ESP32-S3** — Face, one per eye. No WiFi used.

**Dell XPS 15 9510** — Brain. Owned laptop. Closed on the upper tray. No internet. Not on the 12 V rail.

**ELP-USB1080P03-KLC1100** — 1080p USB eye. Metal cube 42 × 42 × 36 mm. LC1100, **86°**. Ordered 2026-09-23.

**Chest LCD** — 7 inch HDMI, 800×480, 107 × 183 mm portrait between the speakers. Brain, not Spine.

**Firmware** — Program on a microcontroller.

**Flashing** — Copying that program over USB.

## Links

**Serial (UART)** — Two wires, agreed baud. Brain↔Spine, Brain↔Face.

**I2C** — Short sensor bus. Spine → two DACs, ToF mux. Each device a different address.

**PWM** — Fast on/off. Not used for throttle here. Throttle is a DAC voltage.

## Drive

**Hub motor** — Direct-drive BLDC in the wheel. Slow + hard = heat. Read the motor thermistor.

**Motor controller** — Scooter ESC. Throttle voltage in. **Nothing back.** No command timeout.

**DAC (MCP4725)** — Number → 0–3.3 V throttle. **Holds last value** if the Teensy dies. That is why the hardware watchdog exists.

**Hardware watchdog** — Timer chip + NC relay. Kicks stop → shorts both throttles to ground.

**Skid steer** — Turn by left ≠ right. Spin = one forward, one reverse. Always scrubs.

**Mixing** — Stick → left/right commands.

**Slew limit** — No instant throttle jumps. Stops tips and belt snap.

## Safety

**E-stop** — Physical. Opens contactor coils. Motors dead. Electronics stay up. Not an isolator.

**Contactor** — DC-rated switch carrying pack current. Coil on pack A.

**Heartbeat** — Brain → Spine every 50 ms. Missing 100 ms → ignore Brain (MANUAL still drives).

**Failsafe** — Break → stop, not keep going.

**Arbitration** — Fixed rule order on the Spine. Higher wins.

**Veto** — Bumper may only reduce a command.

## Sensors

**LiDAR** — Spinning laser map. Night OK. Sun/dust can confuse cheap ones.

**ToF** — Short bumper range. Spine, not Brain.

**Occupancy grid** — Squares: free / blocked / unknown.

**SLAM** — Not used. Desert + crowd has no fixed landmarks.

**GPS** — Metres. Fine for “stay in this area”.

**Compass** — Heading. Keep it far from motors.

## AI (offline)

**Inference** — Run a trained model. We do not train on the robot.

**LLM** — Optional. Picks from `idle` · `look_at` · `greet` · `retreat` · `play_sound` · `nudge_forward`. Never a motor number.

**YuNet** — Face boxes on the XPS CPU.

**Whisper (ivrit Large v3)** — Hebrew speech → text.

**TTS (BlueTTS)** — Text → speech. Recorded WALL-E clips still win for character.

## Electrical

**DC-DC** — One DC voltage to another. Amp is 48→32. Logic is 12→5.

**Brownout** — Voltage dip resets a board. Why electronics have their own 12 V pack (D8).

**Fuse** — Weak point that must open. Not AliExpress for 60/15/10 A.

**AWG** — Smaller number = thicker wire. 10 AWG power, 22 AWG signal.

**Ground** — Shared zero. One bond point. Do not fuse it.

**Ground loop** — Two ground paths. Motor current in the signal zero.
