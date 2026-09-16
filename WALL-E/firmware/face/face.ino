// face.ino — the Face. ESP32-S3, one board per eye.
//
// This board owns the animation. The Brain sends intent a few times a second
// ("look 20 degrees left", "you are curious now") and this board turns that
// into smooth 30 fps movement, blinks, saccades and servo motion.
//
// The split matters for a practical reason as much as an architectural one:
// you can develop and test the whole head with the Jetson unplugged, by typing
// commands into a serial terminal.
//
// This board CANNOT move the robot. It has no connection to the Spine, the CAN
// bus or the contactors. That is deliberate.
//
// Board: ESP32-S3. Libraries: LovyanGFX (display), ESP32Servo (servos).

#include <LovyanGFX.hpp>
#include "config.h"

// ---------------------------------------------------------------------------
//  DISPLAY
// ---------------------------------------------------------------------------
// The 480x480 round panel is QSPI, which LovyanGFX supports but needs a panel
// config block filled in from the module's datasheet. That block is vendor
// specific, so it lives in its own header rather than cluttering this file.
//
// TODO: fill in panel_cfg.h from the Waveshare 2.1in round LCD documentation.
// Until then, everything below runs against the sprite and simply draws to
// nothing, which is still enough to test the animation logic over serial.
#include "panel_cfg.h"
static LGFX lcd;
static LGFX_Sprite eye(&lcd);       // draw off-screen, push once. No tearing.

// ---------------------------------------------------------------------------
//  STATE
// ---------------------------------------------------------------------------
enum Mood : uint8_t { IDLE = 0, CURIOUS, HAPPY, SAD, ALARM, SLEEPY, MOOD_N };
const char* const MOOD_NAME[MOOD_N] =
  {"idle", "curious", "happy", "sad", "alarm", "sleepy"};

struct {
  // where the Brain wants us to look, -1..+1 in each axis
  float want_x = 0, want_y = 0;
  // where we actually are, smoothed
  float x = 0, y = 0;
  // saccade offset, added on top
  float sx = 0, sy = 0;
  Mood  mood = IDLE;
  float lid = 0;            // 0 = open, 1 = shut
  float lid_want = 0;
  float tilt_deg = 0, tilt_want = 0;
  float pan_deg = 0,  pan_want = 0;
  uint32_t brain_last_ms = 0;
} st;

bool is_left = true;        // set in setup() from the select pin

// ===========================================================================
//  SETUP
// ===========================================================================
void setup() {
  pinMode(PIN_EYE_SELECT, INPUT_PULLUP);
  is_left = (digitalRead(PIN_EYE_SELECT) == LOW);

  // The left board drives the sync line, the right board listens to it.
  pinMode(PIN_SYNC, is_left ? OUTPUT : INPUT);

  Serial.begin(BRAIN_BAUD);

  lcd.init();
  lcd.setRotation(0);
  lcd.fillScreen(COL_BG);
  eye.setColorDepth(16);
  eye.createSprite(SCR_W, SCR_H);

  servo_begin();
  randomSeed(esp_random());
}

// ===========================================================================
//  MAIN LOOP
// ===========================================================================
void loop() {
  static uint32_t next_ms = 0;
  const uint32_t frame_ms = 1000 / TARGET_FPS;

  brain_poll();

  uint32_t now = millis();
  if ((int32_t)(now - next_ms) < 0) return;
  next_ms = now + frame_ms;

  frame_sync();
  idle_behaviour(now);
  blink_update(now);
  saccade_update(now);
  gaze_update();
  mood_apply();
  servo_update();
  draw();
}

// Keep the two eyes on the same frame. The left board pulses, the right board
// waits for the edge. If the wire is broken or the other board is dead, the
// wait times out immediately and each eye just runs on its own clock.
void frame_sync() {
  if (is_left) {
    digitalWrite(PIN_SYNC, HIGH);
    delayMicroseconds(50);
    digitalWrite(PIN_SYNC, LOW);
  } else {
    uint32_t t0 = micros();
    while (digitalRead(PIN_SYNC) == LOW) {
      if (micros() - t0 > 2000) break;     // no partner, carry on alone
    }
  }
}

// ===========================================================================
//  BEHAVIOUR WHEN THE BRAIN IS QUIET
// ===========================================================================
// A crashed Jetson must leave a robot that looks bored, not one that looks
// broken. Frozen eyes read as "switched off" to everyone watching.
void idle_behaviour(uint32_t now) {
  if (now - st.brain_last_ms < BRAIN_IDLE_MS) return;

  st.mood = IDLE;
  // Drift slowly around, looking at nothing in particular.
  static uint32_t next_look = 0;
  if (now > next_look) {
    next_look = now + 1800 + random(2600);
    st.want_x = (random(200) - 100) / 140.0f;
    st.want_y = (random(200) - 100) / 220.0f;
  }
}

// ===========================================================================
//  BLINK
// ===========================================================================
void blink_update(uint32_t now) {
  static uint32_t next_blink = 0;
  static uint32_t phase_end  = 0;
  static uint8_t  phase      = 0;   // 0 idle, 1 closing, 2 opening

  if (phase == 0) {
    if (now >= next_blink) {
      phase = 1;
      phase_end = now + BLINK_DOWN_MS;
      st.lid_want = 1.0f;
    }
    return;
  }
  if (now < phase_end) return;

  if (phase == 1) {
    phase = 2;
    phase_end = now + BLINK_UP_MS;
    st.lid_want = 0.0f;
  } else {
    phase = 0;
    next_blink = now + BLINK_MIN_GAP_MS +
                 random(BLINK_MAX_GAP_MS - BLINK_MIN_GAP_MS);
  }
}

void blink_now() {
  // Force a blink on the next frame by pretending the gap has elapsed.
  st.lid_want = 1.0f;
}

// ===========================================================================
//  SACCADES
// ===========================================================================
// Tiny flicks, a few times a second. This is the cheapest single thing you can
// do to stop the eyes looking dead, and nobody can tell you why it works.
void saccade_update(uint32_t now) {
  static uint32_t next = 0;
  if (now < next) return;
  next = now + SACCADE_GAP_MS / 2 + random(SACCADE_GAP_MS);
  st.sx = ((random(200) - 100) / 100.0f) * SACCADE_AMPL;
  st.sy = ((random(200) - 100) / 100.0f) * SACCADE_AMPL;
}

// ===========================================================================
//  SMOOTHING
// ===========================================================================
void gaze_update() {
  st.x   += (st.want_x - st.x) * GAZE_SMOOTH;
  st.y   += (st.want_y - st.y) * GAZE_SMOOTH;
  st.lid += (st.lid_want - st.lid) * LID_SMOOTH;
}

// ===========================================================================
//  MOOD
// ===========================================================================
// Mood does two things: it tilts the barrel, and it sets how far the lid rests
// closed. Those two together carry almost all of the expression — WALL-E's
// eyes are tubes, so the tilt IS the eyebrow.
void mood_apply() {
  switch (st.mood) {
    case IDLE:    st.tilt_want =   0; break;
    case CURIOUS: st.tilt_want =  10; break;   // barrels up and forward
    case HAPPY:   st.tilt_want =   6; break;
    case SAD:     st.tilt_want = -16; break;   // barrels drooped
    case ALARM:   st.tilt_want =  16; break;
    case SLEEPY:  st.tilt_want = -10; break;
    default: break;
  }
  // A resting lid position on top of whatever the blink is doing.
  float rest = (st.mood == SLEEPY) ? 0.45f
             : (st.mood == SAD)    ? 0.22f
             : (st.mood == ALARM)  ? 0.00f : 0.06f;
  if (st.lid_want < rest) st.lid_want = rest;
}

// ===========================================================================
//  DRAW
// ===========================================================================
void draw() {
  eye.fillScreen(COL_BG);

  int16_t gx = SCR_CX + (int16_t)((st.x + st.sx) * GAZE_RANGE);
  int16_t gy = SCR_CY + (int16_t)((st.y + st.sy) * GAZE_RANGE);

  // iris, with a darker rim so it has some depth on a flat panel
  eye.fillCircle(gx, gy, IRIS_R,     COL_IRIS_2);
  eye.fillCircle(gx, gy, IRIS_R - 9, COL_IRIS);
  eye.fillCircle(gx, gy, PUPIL_R,    COL_PUPIL);

  // The highlight does not move with the gaze. A real reflection comes from
  // the light in the room, so it stays put while the eye moves under it.
  eye.fillCircle(SCR_CX - 46, SCR_CY - 52, HILITE_R, COL_HILITE);

  // eyelids, closing from top and bottom
  if (st.lid > 0.01f) {
    int16_t h = (int16_t)(st.lid * (SCR_H / 2));
    eye.fillRect(0, 0,            SCR_W, h, COL_BG);
    eye.fillRect(0, SCR_H - h,    SCR_W, h, COL_BG);
  }

  eye.pushSprite(0, 0);
}

// ===========================================================================
//  SERVOS
// ===========================================================================
// Slew limited, because a servo snapping to position looks mechanical and a
// servo easing looks alive. It also stops the head shaking the whole body.
void servo_update() {
  const float step = SERVO_SLEW_DPS / TARGET_FPS;

  st.tilt_want = clampf(st.tilt_want, TILT_MIN_DEG, TILT_MAX_DEG);
  st.tilt_deg += clampf(st.tilt_want - st.tilt_deg, -step, step);
  servo_write(PIN_SERVO_TILT, st.tilt_deg, TILT_MIN_DEG, TILT_MAX_DEG);

  if (is_left) {
    // Head pan follows the gaze, but only the part the eyes cannot reach.
    // The eye moves first and the head follows, which is how people do it.
    st.pan_want = clampf(st.x * 45.0f, PAN_MIN_DEG, PAN_MAX_DEG);
    st.pan_deg += clampf(st.pan_want - st.pan_deg, -step, step);
    servo_write(PIN_SERVO_PAN, st.pan_deg, PAN_MIN_DEG, PAN_MAX_DEG);
  }
}

void servo_begin() {
  ledcAttach(PIN_SERVO_TILT, 50, 16);
  if (is_left) ledcAttach(PIN_SERVO_PAN, 50, 16);
}

void servo_write(uint8_t pin, float deg, float lo, float hi) {
  float f  = (deg - lo) / (hi - lo);                       // 0..1
  uint16_t us = SERVO_US_MIN + (uint16_t)(f * (SERVO_US_MAX - SERVO_US_MIN));
  // 50 Hz, 16-bit: full period is 20000 us mapped onto 65535 counts.
  ledcWrite(pin, (uint32_t)us * 65535UL / 20000UL);
}

// ===========================================================================
//  BRAIN LINK
// ===========================================================================
// Plain text, one command per line, so you can type it by hand:
//
//   GAZE <az> <el>    degrees. Negative az is left. Both get clamped.
//   MOOD <name>       idle | curious | happy | sad | alarm | sleepy
//   BLINK             blink once, now
//
// Unknown lines are ignored. Anything malformed does not count as contact, so
// a Jetson emitting garbage falls through to the idle behaviour.
void brain_poll() {
  static char line[48];
  static uint8_t n = 0;

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\r') continue;
    if (c != '\n') {
      if (n < sizeof(line) - 1) line[n++] = c;
      else n = 0;
      continue;
    }
    line[n] = 0;
    uint8_t len = n;
    n = 0;
    if (len == 0) continue;
    if (handle(line)) st.brain_last_ms = millis();
  }
}

bool handle(const char* s) {
  float az, el;
  char name[16];

  if (sscanf(s, "GAZE %f %f", &az, &el) == 2) {
    // 45 degrees of gaze maps to the full travel of the iris.
    st.want_x = clampf(az / 45.0f, -1.0f, 1.0f);
    st.want_y = clampf(el / 45.0f, -1.0f, 1.0f);
    return true;
  }
  if (sscanf(s, "MOOD %15s", name) == 1) {
    for (uint8_t i = 0; i < MOOD_N; i++)
      if (!strcmp(name, MOOD_NAME[i])) { st.mood = (Mood)i; return true; }
    return false;
  }
  if (!strcmp(s, "BLINK")) { blink_now(); return true; }
  return false;
}

// ===========================================================================
float clampf(float v, float lo, float hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}
