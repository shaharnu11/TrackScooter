// config.h — every number you might want to change, in one place.
//
// Rule for this file: if a value needs tuning in the field, it belongs here.
// If changing it could make the robot less safe, it gets a comment saying so.
//
// See WALL-E/docs/01-architecture.md section 3 for the rules these serve.
//
// ---------------------------------------------------------------------------
//  REWRITTEN 2026-09-22 FOR DECISION D7
// ---------------------------------------------------------------------------
//  There is no VESC and no CAN bus any more. The motors are driven by the two
//  scooter controllers already owned, through a DAC per side that makes the
//  throttle voltage. Everything a VESC used to broadcast is now a sensor this
//  board reads itself:
//
//    was (VESC on CAN)          now (this board)
//    -------------------------  ------------------------------------------
//    duty command               MCP4725 DAC -> throttle wire, + reverse opto
//    input voltage  (rules 5,11) resistor divider per pack, analogue in
//    motor temperature (rule 9) the hub motor's own thermistor, analogue in
//    "is the track turning?" (4) counting the motor's hall edges
//    motor current              ACS758 per pack, telemetry only
//    command timeout            THE HARDWARE WATCHDOG. See PIN_WDT_KICK.
//
//  docs/05-bom.md section 1b is the parts list this file assumes.

#pragma once

// ===========================================================================
//  TIMING
// ===========================================================================
// The control loop rate. 1 kHz is the promise the whole safety argument rests
// on: no single decision is ever more than 1 ms stale.
const uint32_t LOOP_HZ          = 1000;
const uint32_t LOOP_US          = 1000000UL / LOOP_HZ;

// How long we tolerate silence before deciding a source is dead.
const uint32_t RC_TIMEOUT_MS    = 100;   // radio. Do not raise this.
const uint32_t BRAIN_TIMEOUT_MS = 100;   // Jetson heartbeat

// After the Brain comes back, ignore it for this long. Stops a Jetson that is
// crash-looping from producing repeated bursts of movement.
const uint32_t BRAIN_REARM_MS   = 1000;

// ===========================================================================
//  PINS  (Teensy 4.0)
// ===========================================================================
// Pins 0 and 1 are Serial1 (the radio). 18 and 19 are I2C to the DACs and the
// ToF multiplexer. Do not reuse any of those.
const uint8_t PIN_ARM_OUT   = 2;   // MOSFET holding the contactor coils in.
                                   //   LOW = contactors drop = motors dead.
const uint8_t PIN_ESTOP_SNS = 3;   // senses the E-stop chain. Input, active LOW
const uint8_t PIN_TOF_RESET = 4;   // hard reset line for the ToF ring
const uint8_t PIN_LED_OK    = 13;  // on-board LED, heartbeat blink

// --- THE HARDWARE WATCHDOG -------------------------------------------------
// This pin is the most important output on the board. It is squarewaved while,
// and only while, this firmware believes it is in control. A TLC555/TPS3823
// holds a normally-closed relay OPEN as long as the pulses keep coming. Stop
// them — crash, hang, reset, failed DAC write — and the relay falls closed and
// SHORTS BOTH THROTTLE LINES TO GROUND.
//
// A scooter controller has no command timeout of its own, and the DAC holds
// its last value forever, so this relay is the ENTIRE replacement for the
// behaviour the VESC used to give free. docs/01-architecture.md section 4.
const uint8_t PIN_WDT_KICK  = 5;

// --- the two opto-isolated lines per controller ----------------------------
// A scooter controller cannot be told to go backwards with a voltage: the
// throttle is unipolar. Direction is a separate wire, pulled to ground.
const uint8_t PIN_REV_L     = 6;   // reverse line, left controller
const uint8_t PIN_REV_R     = 7;   // reverse line, right controller
const uint8_t PIN_BRAKE_L   = 8;   // e-brake line, left controller
const uint8_t PIN_BRAKE_R   = 9;   // e-brake line, right controller

// --- hall edges, one wire tapped from each motor's hall cable (rule 4) -----
const uint8_t PIN_HALL_L    = 10;
const uint8_t PIN_HALL_R    = 11;

// --- analogue inputs -------------------------------------------------------
// All of these are measured against the SINGLE bonded pack negative. If that
// bond is missing, every one of these numbers is plausible and wrong.
// docs/01-architecture.md section 3b, trap 3.
const uint8_t PIN_VOLT_L    = A0;  // pack A divider
const uint8_t PIN_VOLT_R    = A1;  // pack B divider
const uint8_t PIN_CURR_L    = A2;  // ACS758, left pack lead
const uint8_t PIN_CURR_R    = A3;  // ACS758, right pack lead
const uint8_t PIN_TEMP_L    = A6;  // left hub motor thermistor divider
const uint8_t PIN_TEMP_R    = A7;  // right hub motor thermistor divider

// Serial1 = the RC receiver.  Serial = USB, to the Brain.
#define RC_SERIAL    Serial1
#define BRAIN_SERIAL Serial

// ===========================================================================
//  RADIO
// ===========================================================================
// iBus channel numbers, 0-based. See docs/05-bom.md section 6.
const uint8_t CH_THROTTLE = 0;
const uint8_t CH_STEER    = 1;
const uint8_t CH_ARM      = 2;
const uint8_t CH_MODE     = 3;
const uint8_t CH_SPEED    = 4;

// iBus sends microseconds, 1000 to 2000, centre 1500.
const uint16_t RC_MIN = 1000, RC_MID = 1500, RC_MAX = 2000;
const uint16_t RC_DEADBAND = 30;   // microseconds either side of centre
const uint16_t RC_SWITCH_ON = 1700;// above this, a 2-position switch is ON

// A channel outside this range is treated as garbage, not as a command.
// Protects against a half-received frame that passed the checksum by luck.
const uint16_t RC_SANE_MIN = 900, RC_SANE_MAX = 2100;

// ===========================================================================
//  THROTTLE OUTPUT — the MCP4725 DACs
// ===========================================================================
// Two DACs on one I2C bus, through a level shifter because they run at 5 V to
// reach full throttle and the Teensy is NOT 5 V tolerant.
const uint8_t DAC_ADDR_L = 0x62;
const uint8_t DAC_ADDR_R = 0x63;
const uint32_t I2C_HZ    = 400000;

// ** MEASURE YOUR OWN THROTTLE BEFORE TRUSTING THESE TWO NUMBERS. **
// Read the scooter throttle's signal wire at rest and at full with a
// multimeter. docs/05-bom.md section 1b says the same thing, twice, because
// getting it wrong means the robot creeps at "zero" or never reaches full.
const float THROTTLE_REST_V = 0.80f;   // what the controller reads as OFF
const float THROTTLE_FULL_V = 4.20f;   // what it reads as FULL
const float DAC_SUPPLY_V    = 5.00f;   // the DAC's own rail = its full scale
const uint16_t DAC_COUNTS   = 4095;    // 12-bit

// How often the throttle voltage is rewritten. Slower than the control loop
// because I2C is not free, but fast enough that a ramp still looks smooth.
const uint32_t DAC_TX_HZ = 200;

// ===========================================================================
//  DIRECTION — the reverse line
// ===========================================================================
// Scooter controllers usually REFUSE to change direction while the wheel is
// still turning, and some damage themselves trying. So the Spine never flips
// the reverse line while a side is moving: it commands zero, waits for the
// halls to go quiet, and only then changes direction. This costs a fraction
// of a second when changing direction and it is not negotiable.
const float    REV_ZERO_DUTY  = 0.02f; // below this, treat the command as zero
const uint32_t REV_QUIET_MS   = 250;   // halls silent this long = stopped

// Many scooter controllers cap reverse at about 30 % of forward. This is not a
// safety limit, it is honesty: asking for more than the controller will give
// makes the robot's behaviour depend on an undocumented firmware cap.
const float REVERSE_CEILING = 0.30f;

// ===========================================================================
//  DRIVE
// ===========================================================================
// "duty" here is a 0..1 fraction of the throttle range, not a VESC duty cycle.
const float DUTY_MAX        = 0.85f;  // never command full throttle
const float DUTY_MAX_ASSIST = 0.25f;  // the Brain gets a much lower ceiling
const float TURN_GAIN       = 0.7f;   // how much of a stick sweep is turn

// Slew rate: the fastest the commanded duty may change, per second.
// This is what stops a stick flick from becoming a wheelie, and what makes a
// watchdog stop a ramp rather than a slam.
const float SLEW_UP_PER_S   = 1.2f;   // 0 to full in 0.83 s
const float SLEW_DOWN_PER_S = 2.0f;   // full to 0 in 0.5 s

// ===========================================================================
//  IS EACH TRACK ALIVE?  (arbitration rule 4)
// ===========================================================================
// Replaces the VESC's CAN status. One hall wire per motor, counted by an
// interrupt. If a side is commanded to move and its halls stay silent, that
// side is dead — and on a skid-steer robot a dead side means it PIVOTS
// instead of stopping. Both sides then ramp to zero. Safety log test 8.
const float    HALL_CMD_MOVING = 0.10f; // commanded duty that should turn a wheel
const uint32_t HALL_STALL_MS   = 400;   // commanded that hard, silent this long
                                        //   = dead. Long enough to break away
                                        //   from standstill on sand.

// ===========================================================================
//  PACK VOLTAGE  (arbitration rules 5 and 11)
// ===========================================================================
// Below the floor, stop. Between floor and nominal, scale each side by its own
// voltage so the robot keeps driving straight as the two packs drift apart.
const float PACK_FLOOR_V   = 40.0f;   // 13S Li-ion: 3.08 V per cell. Conservative.
const float PACK_NOMINAL_V = 48.0f;   // the voltage the duty numbers assume
const float PACK_MAX_V     = 60.0f;   // above this, something is wrong. Stop.

// The divider that makes a 60 V pack readable by a 3.3 V input.
// ** CALIBRATE THESE. ** Put a multimeter on the pack, read the telemetry
// line, and correct the scale until they agree. Resistor tolerance alone is
// several percent, and rule 11 divides by this number.
const float VOLT_SCALE_L = 21.0f;     // volts per volt at the pin
const float VOLT_SCALE_R = 21.0f;
const float ADC_REF_V    = 3.30f;
const uint16_t ADC_COUNTS = 1023;     // analogRead() default resolution

// A pack reading this far below the floor is not a flat pack, it is a missing
// or shorted divider. Treated as a fault, not as a low battery, so the
// telemetry says something useful.
const float VOLT_ABSENT_V = 5.0f;

// ===========================================================================
//  MOTOR TEMPERATURE  (arbitration rule 9)
// ===========================================================================
// Hub motors overheat at low speed because there is no airflow through them
// and the duty cycle is high. This is the most likely way to break a pod.
const float MOTOR_T_WARN = 80.0f;   // start scaling back here
const float MOTOR_T_STOP = 100.0f;  // zero here

// The hub motor's own thermistor, in a divider with a fixed resistor to 3.3 V.
// Most hub motors use a 10k NTC. Check yours: a 100k NTC in this divider reads
// cold forever, which disables rule 9 silently — the worst way to be wrong.
const float NTC_R25   = 10000.0f;   // resistance at 25 C
const float NTC_BETA  = 3950.0f;
const float NTC_FIXED = 10000.0f;   // the other half of the divider

// If the thermistor is unplugged the divider reads one of its rails. Either
// extreme means "no sensor", and rule 9 then assumes the motor is hot rather
// than cold, because a silently disabled temperature limit is how you cook a
// hub motor. See therm_c() in spine.ino.
const uint16_t NTC_OPEN_COUNTS  = 1000;  // near the top rail
const uint16_t NTC_SHORT_COUNTS = 20;    // near ground

// ===========================================================================
//  PACK CURRENT — telemetry only
// ===========================================================================
// ACS758 100 A bidirectional: output sits at half its supply with no current,
// and moves 20 mV per amp. It runs at 5 V, so its output needs a divider down
// to 3.3 V like everything else on this board.
const float ACS_MV_PER_A  = 20.0f;
const float ACS_ZERO_V    = 2.50f;   // supply/2, at the SENSOR
const float ACS_DIV_RATIO = 2.0f;    // sensor volts per volt at the pin

// ===========================================================================
//  BUMPER  (arbitration rule 8, the veto)
// ===========================================================================
const uint8_t  TOF_COUNT      = 6;
const uint16_t TOF_STOP_MM    = 400;   // inside this, zero the forward command
const uint16_t TOF_SLOW_MM    = 1200;  // between these, scale down
const uint16_t TOF_MAX_MM     = 4000;  // beyond this, treat as "clear"
// Which sensors face forward and which face back. Index into the ring.
const uint8_t  TOF_FWD[3]     = {0, 1, 2};
const uint8_t  TOF_AFT[3]     = {3, 4, 5};

// ===========================================================================
//  TELEMETRY
// ===========================================================================
const uint32_t TELEM_HZ = 20;   // status lines up to the Brain
