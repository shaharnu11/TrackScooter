// spine.ino — the Spine. Teensy 4.0, no operating system.
//
// This board decides what the motors do. Nothing else on the robot is allowed
// to. It runs one loop at 1 kHz and rebuilds the motor commands from scratch
// every pass, in the fixed order described in docs/01-architecture.md section 3.
//
// ---------------------------------------------------------------------------
//  RULES FOR EDITING THIS FILE
// ---------------------------------------------------------------------------
//  1. No dynamic memory. No String. No malloc. Ever.
//  2. Nothing that can block. No delay(), no while-loop waiting on a device.
//  3. Nothing that takes unbounded time. No SD card, no display, no filesystem.
//  4. Every new failure case must ramp the motors to zero, not hold the last
//     value and not slam to zero.
//  5. If you are adding a feature rather than a safety check, it belongs on
//     the Brain, not here. Every line added here is a line that can stop the
//     robot from stopping.
//
// ---------------------------------------------------------------------------
//  REWRITTEN 2026-09-22 FOR DECISION D7 — there is no VESC and no CAN bus
// ---------------------------------------------------------------------------
//  The motors are driven by the two scooter controllers already owned. They
//  take a throttle VOLTAGE and tell you nothing back. So this file now:
//
//    * writes the throttle voltage with an MCP4725 DAC per side, and picks
//      direction with a separate opto-isolated reverse line;
//    * measures what the VESC used to broadcast — pack volts, motor
//      temperature, pack current — with its own sensors;
//    * decides "is this track alive?" by counting the motor's hall edges;
//    * KICKS A HARDWARE WATCHDOG, and deliberately stops kicking it when it
//      can no longer trust its own outputs.
//
//  That last one is the important one. A scooter controller has no command
//  timeout and a DAC holds its last value forever, so if this board dies the
//  robot drives away. The only thing that stops it is the watchdog relay
//  shorting the throttle lines to ground. docs/01-architecture.md section 4.
//
// Build: Arduino IDE or PlatformIO with Teensyduino. Board = Teensy 4.0.
// Libraries: Wire only. (FlexCAN_T4 is no longer used — there is no CAN.)

#include <Wire.h>
#include "config.h"

// ===========================================================================
//  STATE
// ===========================================================================
// Grouped by where it comes from, so it is obvious what is an input and what
// is a decision.

struct RcState {
  uint16_t ch[14]  = {0};
  uint32_t last_ms = 0;
  bool     valid   = false;   // a good frame arrived inside RC_TIMEOUT_MS
} rc;

struct BrainState {
  float    speed   = 0.0f;    // -1 .. +1 requested
  float    turn    = 0.0f;
  uint32_t seq     = 0;
  uint32_t last_ms = 0;
  uint32_t ok_since_ms = 0;   // when it started being continuously alive
  bool     valid   = false;
} brain;

// One of these per side. This is what replaced VescState: nothing arrives on
// its own any more, every field is something this board measured.
struct SideState {
  float volts   = 0.0f;       // pack voltage, from the divider
  float temp_c  = 0.0f;       // hub motor thermistor
  float amps    = 0.0f;       // ACS758, telemetry only
  bool  sense_ok = false;     // the divider reading is plausible at all
  bool  alive   = true;       // rule 4: halls moving when commanded to
  int8_t dir    = 0;          // direction currently latched at the controller
  volatile uint32_t hall_edges   = 0;
  volatile uint32_t hall_last_ms = 0;
};
SideState side_l, side_r;

struct ToFState {
  uint16_t mm[TOF_COUNT] = {0};
  bool     valid[TOF_COUNT] = {false};
} tof;

// What we last actually sent. The slew limiter works on these.
float duty_l = 0.0f, duty_r = 0.0f;

// Did the last throttle write actually reach both DACs? If not, this board is
// no longer in control of the motors, and it must stop kicking the watchdog.
bool output_ok = true;

// Why we are not moving, for telemetry. Index into STOP_REASON[].
enum StopReason : uint8_t {
  RUNNING = 0, R_ESTOP, R_UNARMED, R_NO_RC, R_TRACK_DEAD, R_NO_SENSE,
  R_PACK_LOW, R_PACK_HIGH, R_NO_BRAIN, R_BUMPER, R_MOTOR_HOT, R_DAC_FAIL
};
const char* const STOP_REASON[] = {
  "running", "estop", "unarmed", "no_rc", "track_dead", "no_sense",
  "pack_low", "pack_high", "no_brain", "bumper", "motor_hot", "dac_fail"
};
StopReason stop_reason = R_UNARMED;

enum Mode : uint8_t { MANUAL = 0, ASSIST = 1 };
Mode mode = MANUAL;

// Stick activity overrides the Brain for a moment. docs/01-architecture.md s6.
uint32_t stick_override_until_ms = 0;

// ===========================================================================
//  HALL EDGES — arbitration rule 4's data source
// ===========================================================================
// One wire tapped from each motor's existing hall cable. We do not care about
// speed or direction here, only "is this thing turning at all". Counting one
// phase is enough for that and costs one interrupt.
void hall_l_isr() { side_l.hall_edges++; side_l.hall_last_ms = millis(); }
void hall_r_isr() { side_r.hall_edges++; side_r.hall_last_ms = millis(); }

// ===========================================================================
//  SETUP
// ===========================================================================
void setup() {
  // Arm output LOW first, before anything else, so a reset mid-drive drops
  // the contactors rather than leaving them held in.
  pinMode(PIN_ARM_OUT, OUTPUT);
  digitalWrite(PIN_ARM_OUT, LOW);

  // Then the throttle path, before anything can command movement: brakes on,
  // both directions forward, and (once I2C is up) the DACs at rest.
  pinMode(PIN_REV_L,   OUTPUT); digitalWrite(PIN_REV_L,   LOW);
  pinMode(PIN_REV_R,   OUTPUT); digitalWrite(PIN_REV_R,   LOW);
  pinMode(PIN_BRAKE_L, OUTPUT); digitalWrite(PIN_BRAKE_L, HIGH);
  pinMode(PIN_BRAKE_R, OUTPUT); digitalWrite(PIN_BRAKE_R, HIGH);

  // The watchdog line starts quiet. The relay is therefore CLOSED — throttle
  // shorted to ground — until this firmware has run a full pass and decided
  // it is healthy. Booting into "stopped" is the only safe way to boot.
  pinMode(PIN_WDT_KICK, OUTPUT);
  digitalWrite(PIN_WDT_KICK, LOW);

  pinMode(PIN_ESTOP_SNS, INPUT_PULLUP);
  pinMode(PIN_LED_OK, OUTPUT);
  pinMode(PIN_TOF_RESET, OUTPUT);
  digitalWrite(PIN_TOF_RESET, LOW);

  pinMode(PIN_HALL_L, INPUT_PULLUP);
  pinMode(PIN_HALL_R, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_HALL_L), hall_l_isr, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_HALL_R), hall_r_isr, CHANGE);

  BRAIN_SERIAL.begin(115200);
  RC_SERIAL.begin(115200);          // iBus is 115200 8N1

  Wire.begin();
  Wire.setClock(I2C_HZ);
  dac_write(DAC_ADDR_L, throttle_counts(0.0f));
  dac_write(DAC_ADDR_R, throttle_counts(0.0f));

  tof_begin();
}

// ===========================================================================
//  MAIN LOOP — fixed rate, 1 kHz
// ===========================================================================
void loop() {
  static uint32_t next_us = 0;
  uint32_t now_us = micros();

  // Catch up rather than drift. If we ever fall behind, resync instead of
  // trying to run the missed iterations.
  if ((int32_t)(now_us - next_us) < 0) return;
  if ((int32_t)(now_us - next_us) > (int32_t)(LOOP_US * 5)) next_us = now_us;
  next_us += LOOP_US;

  uint32_t now = millis();

  // ---- inputs ----
  rc_poll();
  brain_poll();
  sense_poll();                     // volts, temperature, current
  tof_poll();                       // non-blocking, one sensor per pass
  freshness_check(now);

  // ---- decide ----
  arbitrate(now);

  // ---- outputs ----
  drive_out(now);                   // reverse lines, then the DACs
  wdt_kick(now);                    // ONLY if we still trust the outputs
  telemetry(now);
  digitalWrite(PIN_LED_OK, (now / 250) & 1);
}

// ===========================================================================
//  THE ARBITRATION — docs/01-architecture.md section 3
// ===========================================================================
// Read this top to bottom. The order IS the safety argument. A rule higher up
// always beats a rule lower down, and every exit path ramps to zero.
void arbitrate(uint32_t now) {
  float want_l = 0.0f, want_r = 0.0f;
  stop_reason = RUNNING;

  // --- Rule 1: the E-stop chain -------------------------------------------
  // Physical. If it is open the contactors are already out and the motors have
  // no power at all. We only sense it so we can say so, and so we refuse to
  // re-arm until the button is reset.
  bool estop_ok = (digitalRead(PIN_ESTOP_SNS) == LOW);
  if (!estop_ok) {
    stop_reason = R_ESTOP;
    hold_off();
    return;
  }

  // --- Rule 2: the arm switch ---------------------------------------------
  // The robot must never move the moment the battery is connected.
  bool armed = rc.valid && rc.ch[CH_ARM] > RC_SWITCH_ON;
  if (!armed) {
    stop_reason = R_UNARMED;
    hold_off();
    return;
  }

  // From here on the contactors may be held in.
  digitalWrite(PIN_ARM_OUT, HIGH);

  // --- Rule 3: is the radio alive? ----------------------------------------
  if (!rc.valid) {
    stop_reason = R_NO_RC;
    ramp_to(0.0f, 0.0f);
    return;
  }

  // --- Rule 3b: do we still control the throttle? -------------------------
  // New with D7. If a DAC write failed, the voltage on the controller is
  // whatever it was, and nothing this function decides can change it. Say so,
  // ramp down, and let wdt_kick() drop the relay.
  if (!output_ok) {
    stop_reason = R_DAC_FAIL;
    ramp_to(0.0f, 0.0f);
    return;
  }

  // --- Rule 4: is each track actually turning as commanded? ---------------
  // Both, not either. One dead track on a skid-steer robot does not stop it,
  // it makes it pivot. docs/01-architecture.md section 3b, trap 2.
  // The VESC used to answer this on CAN. Now it is the hall edges.
  if (!side_l.alive || !side_r.alive) {
    stop_reason = R_TRACK_DEAD;
    ramp_to(0.0f, 0.0f);
    return;
  }

  // --- Rule 5: are both pack voltages sane? -------------------------------
  // A missing or shorted divider reads as a plausible number near zero, which
  // would look like a flat pack. Separate it out so the telemetry tells the
  // truth: "no_sense" is a wiring fault, "pack_low" is a battery.
  if (!side_l.sense_ok || !side_r.sense_ok) {
    stop_reason = R_NO_SENSE;
    ramp_to(0.0f, 0.0f);
    return;
  }
  if (side_l.volts < PACK_FLOOR_V || side_r.volts < PACK_FLOOR_V) {
    stop_reason = R_PACK_LOW;
    ramp_to(0.0f, 0.0f);
    return;
  }
  if (side_l.volts > PACK_MAX_V || side_r.volts > PACK_MAX_V) {
    stop_reason = R_PACK_HIGH;
    ramp_to(0.0f, 0.0f);
    return;
  }

  // --- Rule 6: which mode? ------------------------------------------------
  mode = (rc.ch[CH_MODE] > RC_SWITCH_ON) ? ASSIST : MANUAL;

  // The driver's sticks. Normalised to -1 .. +1.
  float stick_fwd  = norm_stick(rc.ch[CH_THROTTLE]);
  float stick_turn = norm_stick(rc.ch[CH_STEER]);
  // The speed dial is a ceiling the driver sets, 0 .. 1.
  float ceiling = norm_dial(rc.ch[CH_SPEED]) * DUTY_MAX;

  // Any real stick input takes priority over the Brain for a short while.
  if (fabsf(stick_fwd) > 0.02f || fabsf(stick_turn) > 0.02f)
    stick_override_until_ms = now + 2000;

  float cmd_fwd, cmd_turn, cmd_ceiling;

  if (mode == ASSIST && now > stick_override_until_ms) {
    // --- Rule 7: in ASSIST, the Brain must be alive -----------------------
    if (!brain.valid) {
      stop_reason = R_NO_BRAIN;
      ramp_to(0.0f, 0.0f);
      return;
    }
    cmd_fwd     = brain.speed;
    cmd_turn    = brain.turn;
    // The Brain never gets the full speed range. Even when it is working.
    cmd_ceiling = fminf(ceiling, DUTY_MAX_ASSIST);
  } else {
    cmd_fwd     = stick_fwd;
    cmd_turn    = stick_turn;
    cmd_ceiling = ceiling;
  }

  // Skid steer mix, then scale by the ceiling.
  want_l = (cmd_fwd + cmd_turn * TURN_GAIN) * cmd_ceiling;
  want_r = (cmd_fwd - cmd_turn * TURN_GAIN) * cmd_ceiling;

  // --- Rule 8: the bumper veto --------------------------------------------
  // It can only REDUCE the command. It can never add to it, and it can never
  // change its sign. That property is what makes it safe to trust.
  float veto = bumper_scale(cmd_fwd);
  if (veto < 1.0f) stop_reason = R_BUMPER;
  want_l *= veto;
  want_r *= veto;

  // --- Rule 9: motor temperature ------------------------------------------
  // Now read from each hub motor's own thermistor rather than the VESC.
  float heat = fminf(thermal_scale(side_l.temp_c), thermal_scale(side_r.temp_c));
  if (heat < 1.0f) stop_reason = R_MOTOR_HOT;
  want_l *= heat;
  want_r *= heat;

  // --- Rule 11: scale each side by its OWN pack voltage -------------------
  // Applied BEFORE the slew limiter, so what gets ramped is the final target.
  // Aims for the same volts at each motor rather than the same duty fraction,
  // which is what keeps it driving straight as the packs drift apart.
  // docs/01-architecture.md section 3b, trap 1.
  want_l *= PACK_NOMINAL_V / side_l.volts;
  want_r *= PACK_NOMINAL_V / side_r.volts;

  want_l = clampf(want_l, -DUTY_MAX, DUTY_MAX);
  want_r = clampf(want_r, -DUTY_MAX, DUTY_MAX);

  // --- Rule 10: slew limit ------------------------------------------------
  ramp_to(want_l, want_r);
}

// Drop the contactors and forget any ramp. Used only for rules 1 and 2, where
// the motors have no power anyway so there is nothing to ramp down.
void hold_off() {
  digitalWrite(PIN_ARM_OUT, LOW);
  duty_l = 0.0f;
  duty_r = 0.0f;
}

// Move duty_l/duty_r towards the target at no more than the slew rate.
// Every stop in this firmware comes through here, which is why no stop is ever
// a slam. A slam on a 910 mm tall robot could pitch it onto its face.
void ramp_to(float tl, float tr) {
  const float up   = SLEW_UP_PER_S   / LOOP_HZ;
  const float down = SLEW_DOWN_PER_S / LOOP_HZ;
  duty_l = slew1(duty_l, tl, up, down);
  duty_r = slew1(duty_r, tr, up, down);
}

float slew1(float now, float want, float up, float down) {
  // "up" means away from zero, "down" means towards zero. Getting this the
  // wrong way round would make stopping slower than starting.
  bool towards_zero = fabsf(want) < fabsf(now);
  float step = towards_zero ? down : up;
  float d = want - now;
  if (d >  step) d =  step;
  if (d < -step) d = -step;
  return now + d;
}

// ===========================================================================
//  THROTTLE OUTPUT — DAC per side, reverse line per side
// ===========================================================================
// This replaced send_duty()/can_tx(). Three things happen here, in this order,
// and the order matters:
//
//   1. decide the direction, and refuse to change it while the wheel turns;
//   2. write the throttle voltage;
//   3. remember whether the write worked, because wdt_kick() reads that.
//
// The e-brake line is asserted whenever we are stopped for a reason. It is the
// same input the emergency stop is wired into, which is what it is for.
void drive_out(uint32_t now) {
  static uint32_t last = 0;
  if (now - last < 1000 / DAC_TX_HZ) return;
  last = now;

  bool ok = true;
  ok &= side_out(side_l, duty_l, PIN_REV_L, PIN_BRAKE_L, DAC_ADDR_L, now);
  ok &= side_out(side_r, duty_r, PIN_REV_R, PIN_BRAKE_R, DAC_ADDR_R, now);
  output_ok = ok;
}

bool side_out(SideState &s, float duty, uint8_t rev_pin, uint8_t brake_pin,
              uint8_t dac_addr, uint32_t now) {
  float mag = fabsf(duty);
  int8_t want_dir = (duty >  REV_ZERO_DUTY) ?  1
                  : (duty < -REV_ZERO_DUTY) ? -1 : 0;

  // --- the direction interlock --------------------------------------------
  // Scooter controllers commonly refuse to reverse while the wheel is still
  // turning, and some are damaged by being asked. So a direction change is:
  // command zero, wait for the halls to fall silent, then flip the line.
  if (want_dir != 0 && s.dir != 0 && want_dir != s.dir) {
    if (now - s.hall_last_ms < REV_QUIET_MS) {
      mag = 0.0f;                    // still rolling: stop first, flip later
    } else {
      s.dir = want_dir;
      digitalWrite(rev_pin, want_dir < 0 ? HIGH : LOW);
    }
  } else if (want_dir != 0 && s.dir == 0) {
    s.dir = want_dir;
    digitalWrite(rev_pin, want_dir < 0 ? HIGH : LOW);
  }

  // Reverse on these controllers is capped in their own firmware. Asking for
  // more than the cap makes the robot's behaviour depend on an undocumented
  // number, so ask for the cap and no more.
  if (s.dir < 0) mag = fminf(mag, REVERSE_CEILING);

  // The e-brake goes on when we are stopped because something is wrong, not
  // every time the stick is centred — otherwise the robot cannot coast.
  bool braking = (stop_reason != RUNNING) && (mag < REV_ZERO_DUTY);
  digitalWrite(brake_pin, braking ? HIGH : LOW);

  return dac_write(dac_addr, throttle_counts(mag));
}

// Turn a 0..1 magnitude into DAC counts, using the two voltages you measured
// off the real throttle. Below REV_ZERO_DUTY this returns the REST voltage
// exactly, so "stopped" is the same number the controller sees from a thumb
// that let go.
uint16_t throttle_counts(float mag) {
  mag = clampf(mag, 0.0f, 1.0f);
  float v = THROTTLE_REST_V + mag * (THROTTLE_FULL_V - THROTTLE_REST_V);
  float counts = v / DAC_SUPPLY_V * (float)DAC_COUNTS;
  if (counts < 0) counts = 0;
  if (counts > DAC_COUNTS) counts = DAC_COUNTS;
  return (uint16_t)counts;
}

// MCP4725 fast-mode write: two bytes, no EEPROM. Returns false if the device
// did not acknowledge — a pulled wire, a dead DAC, a locked-up I2C bus.
// THE RETURN VALUE IS A SAFETY SIGNAL. Do not ignore it.
bool dac_write(uint8_t addr, uint16_t value) {
  Wire.beginTransmission(addr);
  Wire.write((uint8_t)((value >> 8) & 0x0F));
  Wire.write((uint8_t)(value & 0xFF));
  return Wire.endTransmission() == 0;
}

// ===========================================================================
//  THE HARDWARE WATCHDOG
// ===========================================================================
// Square wave while this firmware is healthy. The moment it stops, a relay
// with normally-closed contacts falls closed and shorts both throttle lines to
// ground. Nothing in software has to work for that to happen.
//
// It is kicked ONLY when the last DAC write succeeded. That is deliberate and
// it is safety log test 16: a Teensy that is alive but has lost the I2C bus
// would otherwise keep kicking happily while the throttle stayed stuck at its
// last value. The blind spot is closed by refusing to kick.
void wdt_kick(uint32_t now) {
  static uint32_t last = 0;
  if (!output_ok) return;                  // <-- the whole point. Do not "fix".
  if (now - last < 5) return;              // 100 Hz square wave
  last = now;
  digitalWrite(PIN_WDT_KICK, !digitalRead(PIN_WDT_KICK));
}

// ===========================================================================
//  THE SENSORS THAT REPLACED THE VESC TELEMETRY
// ===========================================================================
// Everything here is measured against the single bonded pack negative. If that
// bond is missing these numbers are plausible and wrong, which is worse than
// missing. docs/01-architecture.md section 3b, trap 3.
void sense_poll() {
  sense_side(side_l, PIN_VOLT_L, VOLT_SCALE_L, PIN_TEMP_L, PIN_CURR_L);
  sense_side(side_r, PIN_VOLT_R, VOLT_SCALE_R, PIN_TEMP_R, PIN_CURR_R);
}

void sense_side(SideState &s, uint8_t vpin, float vscale,
                uint8_t tpin, uint8_t cpin) {
  // A light low-pass on all three. Motor phase wires run near these cables and
  // a single noisy sample must never trip a rule on its own.
  const float a = 0.05f;
  float v = (float)analogRead(vpin) / (float)ADC_COUNTS * ADC_REF_V * vscale;
  s.volts = s.volts == 0.0f ? v : s.volts + a * (v - s.volts);
  s.sense_ok = (s.volts > VOLT_ABSENT_V);

  float t = therm_c(tpin);
  s.temp_c = s.temp_c == 0.0f ? t : s.temp_c + a * (t - s.temp_c);

  float pin_v = (float)analogRead(cpin) / (float)ADC_COUNTS * ADC_REF_V;
  float sensor_v = pin_v * ACS_DIV_RATIO;
  float amps = (sensor_v - ACS_ZERO_V) * 1000.0f / ACS_MV_PER_A;
  s.amps = s.amps + a * (amps - s.amps);
}

// Hub motor thermistor in a divider. An unplugged sensor reads one of the
// rails, and we return a HOT number for that, not a cold one: a temperature
// limit that switches itself off when the wire falls out is how you cook a
// motor without ever seeing a warning.
float therm_c(uint8_t pin) {
  uint16_t c = analogRead(pin);
  if (c >= NTC_OPEN_COUNTS || c <= NTC_SHORT_COUNTS) return 999.0f;

  float r = NTC_FIXED * (float)c / (float)(ADC_COUNTS - c);
  float inv_t = 1.0f / 298.15f + logf(r / NTC_R25) / NTC_BETA;
  return 1.0f / inv_t - 273.15f;
}

// ===========================================================================
//  THE VETO
// ===========================================================================
// Returns a scale factor 0..1 for the direction we are actually going.
// Sensors facing backwards are ignored when driving forwards, and vice versa,
// because otherwise the robot can never reverse away from an obstacle.
float bumper_scale(float fwd) {
  if (fabsf(fwd) < 0.02f) return 1.0f;         // not moving, nothing to veto

  const uint8_t* look = (fwd > 0) ? TOF_FWD : TOF_AFT;
  uint16_t nearest = TOF_MAX_MM;
  bool any_valid = false;

  for (uint8_t i = 0; i < 3; i++) {
    uint8_t s = look[i];
    if (!tof.valid[s]) continue;
    any_valid = true;
    if (tof.mm[s] < nearest) nearest = tof.mm[s];
  }

  // No working sensor on the side we are driving towards. Do NOT return 1.0 —
  // that would silently disable the veto the moment a sensor died. Half speed
  // and let the telemetry complain.
  if (!any_valid) return 0.5f;

  if (nearest <= TOF_STOP_MM) return 0.0f;
  if (nearest >= TOF_SLOW_MM) return 1.0f;
  return (float)(nearest - TOF_STOP_MM) / (float)(TOF_SLOW_MM - TOF_STOP_MM);
}

float thermal_scale(float t) {
  if (t <= MOTOR_T_WARN) return 1.0f;
  if (t >= MOTOR_T_STOP) return 0.0f;
  return 1.0f - (t - MOTOR_T_WARN) / (MOTOR_T_STOP - MOTOR_T_WARN);
}

// ===========================================================================
//  FRESHNESS — the watchdogs
// ===========================================================================
void freshness_check(uint32_t now) {
  rc.valid = (now - rc.last_ms) < RC_TIMEOUT_MS;

  // Rule 4's test, once per pass, for each side: if it is being told to move
  // and the halls have been silent too long, that side is dead.
  side_alive(side_l, duty_l, now);
  side_alive(side_r, duty_r, now);

  bool fresh = (now - brain.last_ms) < BRAIN_TIMEOUT_MS;
  if (!fresh) {
    brain.ok_since_ms = 0;
    brain.valid = false;
  } else {
    if (brain.ok_since_ms == 0) brain.ok_since_ms = now;
    // Must be continuously alive for BRAIN_REARM_MS before we obey it again.
    // Stops a crash-looping Jetson producing repeated bursts of movement.
    brain.valid = (now - brain.ok_since_ms) >= BRAIN_REARM_MS;
  }
}

void side_alive(SideState &s, float duty, uint32_t now) {
  if (fabsf(duty) < HALL_CMD_MOVING) {
    // Not asking it to move, so a silent wheel proves nothing. Saying "alive"
    // here is not optimism: rule 4 only means "it moves when told to".
    s.alive = true;
    return;
  }
  uint32_t last;
  noInterrupts();
  last = s.hall_last_ms;
  interrupts();
  s.alive = (now - last) < HALL_STALL_MS;
}

// ===========================================================================
//  RADIO — iBus
// ===========================================================================
// 32 bytes: 0x20 0x40, then 14 channels of 2 bytes little-endian, then a
// 2-byte checksum which is 0xFFFF minus the sum of the first 30 bytes.
void rc_poll() {
  static uint8_t buf[32];
  static uint8_t n = 0;

  while (RC_SERIAL.available()) {
    uint8_t b = RC_SERIAL.read();

    if (n == 0) { if (b != 0x20) continue; }
    if (n == 1) { if (b != 0x40) { n = 0; continue; } }

    buf[n++] = b;
    if (n < 32) continue;
    n = 0;

    uint16_t sum = 0xFFFF;
    for (uint8_t i = 0; i < 30; i++) sum -= buf[i];
    uint16_t given = (uint16_t)buf[30] | ((uint16_t)buf[31] << 8);
    if (sum != given) continue;                  // corrupt, drop it silently

    // Reject the whole frame if ANY channel we care about is out of range.
    // A frame can pass the checksum and still be nonsense.
    uint16_t tmp[14];
    for (uint8_t c = 0; c < 14; c++)
      tmp[c] = (uint16_t)buf[2 + c*2] | ((uint16_t)buf[3 + c*2] << 8);

    const uint8_t used[] = {CH_THROTTLE, CH_STEER, CH_ARM, CH_MODE, CH_SPEED};
    for (uint8_t i = 0; i < sizeof(used); i++)
      if (tmp[used[i]] < RC_SANE_MIN || tmp[used[i]] > RC_SANE_MAX) return;

    memcpy(rc.ch, tmp, sizeof(tmp));
    rc.last_ms = millis();
  }
}

float norm_stick(uint16_t us) {
  int16_t d = (int16_t)us - (int16_t)RC_MID;
  if (abs(d) < RC_DEADBAND) return 0.0f;
  d += (d > 0) ? -RC_DEADBAND : RC_DEADBAND;
  float span = (float)(RC_MAX - RC_MID - RC_DEADBAND);
  return clampf((float)d / span, -1.0f, 1.0f);
}

float norm_dial(uint16_t us) {
  return clampf((float)((int16_t)us - (int16_t)RC_MIN) /
                (float)(RC_MAX - RC_MIN), 0.0f, 1.0f);
}

// ===========================================================================
//  BRAIN LINK — plain text, one command per line
// ===========================================================================
// Text on purpose. You can drive this board from a serial terminal while the
// Jetson is in pieces, and you can read a log with your eyes.
//
//   Brain -> Spine :  "C <speed> <turn> <seq>\n"   speed,turn in -1.0 .. 1.0
//   Spine -> Brain :  see telemetry()
//
// Anything unparseable is ignored and does NOT refresh the heartbeat, so a
// Jetson emitting garbage counts as a dead Jetson.
void brain_poll() {
  static char line[64];
  static uint8_t n = 0;

  while (BRAIN_SERIAL.available()) {
    char c = BRAIN_SERIAL.read();
    if (c == '\r') continue;
    if (c != '\n') {
      if (n < sizeof(line) - 1) line[n++] = c;
      else n = 0;                                 // overlong, drop the line
      continue;
    }
    line[n] = 0;
    uint8_t len = n;
    n = 0;
    if (len < 3 || line[0] != 'C') continue;

    float s, t; uint32_t q;
    if (sscanf(line + 1, "%f %f %lu", &s, &t, &q) != 3) continue;
    if (!isfinite(s) || !isfinite(t)) continue;    // NaN would poison the mix

    brain.speed   = clampf(s, -1.0f, 1.0f);
    brain.turn    = clampf(t, -1.0f, 1.0f);
    brain.seq     = q;
    brain.last_ms = millis();
  }
}

// ===========================================================================
//  TELEMETRY
// ===========================================================================
// One line, 20 times a second, human readable. This is the file you will want
// after the first time something goes wrong in the field, so it includes the
// stop reason rather than making you infer it.
//
// "dac" is 1 while this board still controls the throttle. If it ever reads 0
// the hardware watchdog should already have stopped the robot.
void telemetry(uint32_t now) {
  static uint32_t last = 0;
  if (now - last < 1000 / TELEM_HZ) return;
  last = now;

  BRAIN_SERIAL.printf(
    "S %lu %s %s duty %.3f %.3f v %.1f %.1f t %.0f %.0f i %.1f %.1f "
    "hall %lu %lu rc %d brain %d dac %d\n",
    now, mode == ASSIST ? "assist" : "manual", STOP_REASON[stop_reason],
    duty_l, duty_r,
    side_l.volts, side_r.volts,
    side_l.temp_c, side_r.temp_c,
    side_l.amps, side_r.amps,
    (unsigned long)side_l.hall_edges, (unsigned long)side_r.hall_edges,
    rc.valid ? 1 : 0, brain.valid ? 1 : 0, output_ok ? 1 : 0);
}

// ===========================================================================
//  ToF RING — placeholder
// ===========================================================================
// Six VL53L1X on one I2C bus through a TCA9548A multiplexer, because they all
// share the same fixed address. One sensor is read per loop pass, so a hung
// sensor costs one reading and not the control loop.
//
// TODO: implement against the VL53L1X library. Until then every sensor reports
// invalid, which makes bumper_scale() return 0.5 and halve the speed — the
// safe direction to be wrong in. Do not "temporarily" make this return clear.
void tof_begin() {
  digitalWrite(PIN_TOF_RESET, HIGH);
  for (uint8_t i = 0; i < TOF_COUNT; i++) tof.valid[i] = false;
}

void tof_poll() {
  // intentionally empty until the sensors are wired. See the note above.
}

// ===========================================================================
//  SMALL HELPERS
// ===========================================================================
float clampf(float v, float lo, float hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}
