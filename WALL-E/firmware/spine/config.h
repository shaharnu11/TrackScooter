// config.h — every number you might want to change, in one place.
//
// Rule for this file: if a value needs tuning in the field, it belongs here.
// If changing it could make the robot less safe, it gets a comment saying so.
//
// See WALL-E/docs/01-architecture.md section 3 for the rules these serve.

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
const uint32_t VESC_TIMEOUT_MS  = 250;   // VESC status on CAN

// After the Brain comes back, ignore it for this long. Stops a Jetson that is
// crash-looping from producing repeated bursts of movement.
const uint32_t BRAIN_REARM_MS   = 1000;

// ===========================================================================
//  PINS  (Teensy 4.1)
// ===========================================================================
const uint8_t PIN_ARM_OUT   = 2;   // MOSFET holding the contactor coils in.
                                   //   LOW = contactors drop = motors dead.
const uint8_t PIN_ESTOP_SNS = 3;   // senses the E-stop chain. Input, active LOW
const uint8_t PIN_LED_OK    = 13;  // on-board LED, heartbeat blink
const uint8_t PIN_TOF_RESET = 4;   // hard reset line for the ToF ring

// Serial1 = iBus from the RC receiver.  Serial = USB, to the Brain.
#define RC_SERIAL   Serial1
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
//  DRIVE
// ===========================================================================
// Duty cycle, not current. See the note in spine.ino above send_duty().
const float DUTY_MAX        = 0.85f;  // never command full duty
const float DUTY_MAX_ASSIST = 0.25f;  // the Brain gets a much lower ceiling
const float TURN_GAIN       = 0.7f;   // how much of a stick sweep is turn

// Slew rate: the fastest the commanded duty may change, per second.
// This is what stops a stick flick from becoming a wheelie, and what makes a
// watchdog stop a ramp rather than a slam.
const float SLEW_UP_PER_S   = 1.2f;   // 0 to full in 0.83 s
const float SLEW_DOWN_PER_S = 2.0f;   // full to 0 in 0.5 s

// ===========================================================================
//  PACK VOLTAGE  (arbitration rules 5 and 11)
// ===========================================================================
// Below the floor, stop. Between floor and nominal, scale each side by its own
// voltage so the robot keeps driving straight as the two packs drift apart.
const float PACK_FLOOR_V   = 40.0f;   // 13S Li-ion: 3.08 V per cell. Conservative.
const float PACK_NOMINAL_V = 48.0f;   // the voltage the duty numbers assume
const float PACK_MAX_V     = 60.0f;   // above this, something is wrong. Stop.

// ===========================================================================
//  MOTOR TEMPERATURE  (arbitration rule 9)
// ===========================================================================
// Hub motors overheat at low speed because there is no airflow through them
// and the duty cycle is high. This is the most likely way to break a pod.
const float MOTOR_T_WARN = 80.0f;   // start scaling back here
const float MOTOR_T_STOP = 100.0f;  // zero here

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
//  CAN / VESC
// ===========================================================================
const uint32_t CAN_BAUD   = 500000;
const uint8_t  VESC_ID_L  = 1;    // set these in the VESC tool, one each
const uint8_t  VESC_ID_R  = 2;
const uint32_t CAN_TX_HZ  = 100;  // command rate to the VESCs

// The VESC's OWN command timeout, set in the VESC tool, not here. It is the
// last line of defence if this board loses power. docs/01-architecture.md
// section 3b. Written down here so it is not forgotten: TARGET 500 ms.

// ===========================================================================
//  TELEMETRY
// ===========================================================================
const uint32_t TELEM_HZ = 20;   // status lines up to the Brain
