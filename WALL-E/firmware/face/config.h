// config.h — the Face. One of these boards per eye.
//
// See WALL-E/docs/01-architecture.md section 5 for the split of responsibility:
// the Brain says WHAT TO FEEL, this board decides HOW TO SHOW IT. That is why
// the animation runs here and not on the Jetson — the face stays smooth even
// while the Brain is busy or rebooting.

#pragma once

// ===========================================================================
//  WHICH EYE IS THIS BOARD?
// ===========================================================================
// Tie PIN_EYE_SELECT to ground on the left board and leave it floating on the
// right one. Same firmware on both, so there is only ever one binary to keep
// track of, and swapping a dead board in the field needs no laptop.
const uint8_t PIN_EYE_SELECT = 4;   // LOW = left eye

// ===========================================================================
//  FRAME SYNC
// ===========================================================================
// One wire between the two boards. The left board pulses it; the right board
// starts its frame on the pulse. Without this the two eyes blink a few tens of
// milliseconds apart, which is subtly unsettling in a way people notice
// without being able to say why.
const uint8_t PIN_SYNC = 5;

// ===========================================================================
//  DISPLAY
// ===========================================================================
// Waveshare 2.1 inch round, 480x480, QSPI. 53 mm active area, sitting in a
// 105 mm barrel. See docs/05-bom.md section 4 and cad/walle_frame.scad.
const uint16_t SCR_W = 480, SCR_H = 480;
const int16_t  SCR_CX = SCR_W / 2, SCR_CY = SCR_H / 2;
const uint8_t  TARGET_FPS = 30;     // docs/01-architecture.md section 1

// ===========================================================================
//  EYE GEOMETRY, in screen pixels
// ===========================================================================
const int16_t IRIS_R      = 150;    // the coloured part
const int16_t PUPIL_R     = 62;     // the dark centre
const int16_t GAZE_RANGE  = 78;     // how far the iris may travel off centre
const int16_t HILITE_R    = 26;     // the specular dot that sells it as glass

// Colours, RGB565.
const uint16_t COL_BG     = 0x0000; // black. The barrel interior is black too.
const uint16_t COL_IRIS   = 0x5D7F; // pale blue
const uint16_t COL_IRIS_2 = 0x2ADF; // deeper blue, for the rim
const uint16_t COL_PUPIL  = 0x0000;
const uint16_t COL_HILITE = 0xFFFF;

// ===========================================================================
//  ANIMATION
// ===========================================================================
// Gaze is smoothed towards the target rather than jumped, so the Brain can
// send coarse 5 Hz updates and the eye still moves like an eye.
const float GAZE_SMOOTH   = 0.14f;  // per frame, 0..1. Lower is lazier.
const float LID_SMOOTH    = 0.35f;

// Blinking. A real blink is fast down and slower up.
const uint16_t BLINK_DOWN_MS = 70;
const uint16_t BLINK_UP_MS   = 130;
const uint16_t BLINK_MIN_GAP_MS = 2200;   // never blink more often than this
const uint16_t BLINK_MAX_GAP_MS = 7000;   // idle blink, so he looks alive

// Saccades: tiny involuntary flicks. Without these the gaze looks dead even
// when it is moving, because real eyes are never still.
const float    SACCADE_AMPL   = 0.035f;
const uint16_t SACCADE_GAP_MS = 900;

// ===========================================================================
//  SERVO — barrel tilt
// ===========================================================================
// One servo per barrel, tilting it up and down. Head pan is a separate servo
// on the neck, driven by the left board only.
const uint8_t  PIN_SERVO_TILT = 6;
const uint8_t  PIN_SERVO_PAN  = 7;    // left board only
const uint16_t SERVO_US_MIN   = 1000;
const uint16_t SERVO_US_MAX   = 2000;
// Mechanical limits, degrees. Going past these makes the barrel hit the yoke.
const float    TILT_MIN_DEG   = -22.0f, TILT_MAX_DEG = 18.0f;
const float    PAN_MIN_DEG    = -55.0f, PAN_MAX_DEG  = 55.0f;
const float    SERVO_SLEW_DPS = 140.0f; // degrees per second. Keeps it calm.

// ===========================================================================
//  BRAIN LINK
// ===========================================================================
const uint32_t BRAIN_BAUD    = 115200;
// If the Brain goes quiet, do NOT freeze. Fall back to the idle behaviour, so
// a crashed Jetson leaves a robot that looks bored rather than broken.
const uint32_t BRAIN_IDLE_MS = 1500;
