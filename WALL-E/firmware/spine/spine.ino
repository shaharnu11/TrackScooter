// spine.ino — the Spine. Teensy 4.1, no operating system.
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
// Build: Arduino IDE or PlatformIO with Teensyduino. Board = Teensy 4.1.
// Library needed: FlexCAN_T4 (built into Teensyduino).

#include <FlexCAN_T4.h>
#include <Wire.h>
#include "config.h"

FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> can;

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

struct VescState {
  float    volts    = 0.0f;
  float    temp_mot = 0.0f;
  float    temp_fet = 0.0f;
  float    current  = 0.0f;
  int32_t  erpm     = 0;
  uint32_t last_ms  = 0;
  bool     valid    = false;
};
VescState vesc_l, vesc_r;

struct ToFState {
  uint16_t mm[TOF_COUNT] = {0};
  bool     valid[TOF_COUNT] = {false};
} tof;

// What we last actually sent. The slew limiter works on these.
float duty_l = 0.0f, duty_r = 0.0f;

// Why we are not moving, for telemetry. Index into STOP_REASON[].
enum StopReason : uint8_t {
  RUNNING = 0, R_ESTOP, R_UNARMED, R_NO_RC, R_NO_VESC, R_PACK_LOW,
  R_PACK_HIGH, R_NO_BRAIN, R_BUMPER, R_MOTOR_HOT
};
const char* const STOP_REASON[] = {
  "running", "estop", "unarmed", "no_rc", "no_vesc", "pack_low",
  "pack_high", "no_brain", "bumper", "motor_hot"
};
StopReason stop_reason = R_UNARMED;

enum Mode : uint8_t { MANUAL = 0, ASSIST = 1 };
Mode mode = MANUAL;

// Stick activity overrides the Brain for a moment. docs/01-architecture.md s6.
uint32_t stick_override_until_ms = 0;

// ===========================================================================
//  SETUP
// ===========================================================================
void setup() {
  // Arm output LOW first, before anything else, so a reset mid-drive drops
  // the contactors rather than leaving them held in.
  pinMode(PIN_ARM_OUT, OUTPUT);
  digitalWrite(PIN_ARM_OUT, LOW);

  pinMode(PIN_ESTOP_SNS, INPUT_PULLUP);
  pinMode(PIN_LED_OK, OUTPUT);
  pinMode(PIN_TOF_RESET, OUTPUT);
  digitalWrite(PIN_TOF_RESET, LOW);

  BRAIN_SERIAL.begin(115200);
  RC_SERIAL.begin(115200);          // iBus is 115200 8N1

  Wire.begin();
  Wire.setClock(400000);
  tof_begin();

  can.begin();
  can.setBaudRate(CAN_BAUD);
  can.setMaxMB(16);
  can.enableFIFO();
  can.enableFIFOInterrupt();
  can.onReceive(on_can_rx);
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
  tof_poll();                       // non-blocking, one sensor per pass
  freshness_check(now);

  // ---- decide ----
  arbitrate(now);

  // ---- outputs ----
  can_tx(now);
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

  // --- Rule 4: are BOTH VESCs reporting? ----------------------------------
  // Both, not either. One dead track on a skid-steer robot does not stop it,
  // it makes it pivot. docs/01-architecture.md section 3b, trap 2.
  if (!vesc_l.valid || !vesc_r.valid) {
    stop_reason = R_NO_VESC;
    ramp_to(0.0f, 0.0f);
    return;
  }

  // --- Rule 5: are both pack voltages sane? -------------------------------
  if (vesc_l.volts < PACK_FLOOR_V || vesc_r.volts < PACK_FLOOR_V) {
    stop_reason = R_PACK_LOW;
    ramp_to(0.0f, 0.0f);
    return;
  }
  if (vesc_l.volts > PACK_MAX_V || vesc_r.volts > PACK_MAX_V) {
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
  float heat = fminf(thermal_scale(vesc_l.temp_mot), thermal_scale(vesc_r.temp_mot));
  if (heat < 1.0f) stop_reason = R_MOTOR_HOT;
  want_l *= heat;
  want_r *= heat;

  // --- Rule 11: scale each side by its OWN pack voltage -------------------
  // Applied BEFORE the slew limiter, so what gets ramped is the final target.
  // Aims for the same volts at each motor rather than the same duty fraction,
  // which is what keeps it driving straight as the packs drift apart.
  // docs/01-architecture.md section 3b, trap 1.
  want_l *= PACK_NOMINAL_V / vesc_l.volts;
  want_r *= PACK_NOMINAL_V / vesc_r.volts;

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
  rc.valid      = (now - rc.last_ms)      < RC_TIMEOUT_MS;
  vesc_l.valid  = (now - vesc_l.last_ms)  < VESC_TIMEOUT_MS;
  vesc_r.valid  = (now - vesc_r.last_ms)  < VESC_TIMEOUT_MS;

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
//  CAN — VESC
// ===========================================================================
// Extended ID is (packet_type << 8) | vesc_id.
enum : uint8_t {
  CAN_SET_DUTY   = 0,
  CAN_STATUS_1   = 9,    // erpm, current, duty
  CAN_STATUS_4   = 16,   // temp fet, temp motor, current in
  CAN_STATUS_5   = 27,   // tacho, voltage in
};

// Duty rather than current. Duty means "this fraction of the pack voltage at
// the motor", which is what makes the pack-voltage scaling in rule 11 a single
// multiplication. Current mode gives nicer crawling but the voltage-drift
// correction then has to be a control loop instead of a multiply, and a loop
// in here is a loop that can misbehave. Revisit only if crawl control is bad.
void send_duty(uint8_t id, float duty) {
  CAN_message_t m;
  m.flags.extended = 1;
  m.id  = ((uint32_t)CAN_SET_DUTY << 8) | id;
  m.len = 4;
  int32_t v = (int32_t)(duty * 100000.0f);
  m.buf[0] = (v >> 24) & 0xFF;   // VESC is big-endian on the wire
  m.buf[1] = (v >> 16) & 0xFF;
  m.buf[2] = (v >>  8) & 0xFF;
  m.buf[3] = (v      ) & 0xFF;
  can.write(m);
}

void can_tx(uint32_t now) {
  static uint32_t last = 0;
  if (now - last < 1000 / CAN_TX_HZ) return;
  last = now;
  send_duty(VESC_ID_L, duty_l);
  send_duty(VESC_ID_R, duty_r);
}

static int16_t be16(const uint8_t* b) { return (int16_t)((b[0] << 8) | b[1]); }
static int32_t be32(const uint8_t* b) {
  return (int32_t)(((uint32_t)b[0] << 24) | ((uint32_t)b[1] << 16) |
                   ((uint32_t)b[2] <<  8) |  (uint32_t)b[3]);
}

void on_can_rx(const CAN_message_t &m) {
  if (!m.flags.extended) return;
  uint8_t id   = m.id & 0xFF;
  uint8_t type = (m.id >> 8) & 0xFF;

  VescState* v = (id == VESC_ID_L) ? &vesc_l
               : (id == VESC_ID_R) ? &vesc_r : nullptr;
  if (!v) return;

  switch (type) {
    case CAN_STATUS_1:
      if (m.len < 6) return;
      v->erpm    = be32(&m.buf[0]);
      v->current = be16(&m.buf[4]) / 10.0f;
      break;
    case CAN_STATUS_4:
      if (m.len < 4) return;
      v->temp_fet = be16(&m.buf[0]) / 10.0f;
      v->temp_mot = be16(&m.buf[2]) / 10.0f;
      break;
    case CAN_STATUS_5:
      if (m.len < 6) return;
      v->volts = be16(&m.buf[4]) / 10.0f;
      break;
    default:
      return;   // do NOT refresh last_ms on a packet we did not understand
  }
  v->last_ms = millis();
}

// ===========================================================================
//  TELEMETRY
// ===========================================================================
// One line, 20 times a second, human readable. This is the file you will want
// after the first time something goes wrong in the field, so it includes the
// stop reason rather than making you infer it.
void telemetry(uint32_t now) {
  static uint32_t last = 0;
  if (now - last < 1000 / TELEM_HZ) return;
  last = now;

  BRAIN_SERIAL.printf(
    "S %lu %s %s duty %.3f %.3f v %.1f %.1f t %.0f %.0f i %.1f %.1f rc %d brain %d\n",
    now, mode == ASSIST ? "assist" : "manual", STOP_REASON[stop_reason],
    duty_l, duty_r,
    vesc_l.volts, vesc_r.volts,
    vesc_l.temp_mot, vesc_r.temp_mot,
    vesc_l.current, vesc_r.current,
    rc.valid ? 1 : 0, brain.valid ? 1 : 0);
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
