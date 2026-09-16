// panel_cfg.h — LovyanGFX panel setup for the round eye display.
//
// This is the one file in the project that has to be copied out of a vendor
// document rather than reasoned about. The 2.1 inch 480x480 round panel is
// QSPI, and the initialisation sequence, pin mapping and timing are specific
// to the module you actually buy.
//
// TODO before the head can light up:
//   1. Find the Waveshare example for the exact module (2.1in round, 480x480).
//   2. Copy its bus and panel config into the class below.
//   3. Check the pin numbers against the ESP32-S3 board you are using, and
//      against config.h — PIN_EYE_SELECT, PIN_SYNC and the two servo pins must
//      not clash with the display bus.
//
// Until then this compiles and runs against a panel that is not there, which
// is enough to develop and test all of the animation logic in face.ino over
// the serial link. That is deliberate: the animation is the hard part and it
// does not need the screen to write.

#pragma once
#include <LovyanGFX.hpp>

class LGFX : public lgfx::LGFX_Device {
  // PLACEHOLDER. Replace both of these with the vendor's config.
  lgfx::Panel_GC9A01  _panel;
  lgfx::Bus_SPI       _bus;

public:
  LGFX() {
    {
      auto cfg = _bus.config();
      cfg.spi_host    = SPI2_HOST;
      cfg.spi_mode    = 0;
      cfg.freq_write  = 40000000;
      cfg.pin_sclk    = 12;    // CHECK against your board
      cfg.pin_mosi    = 11;
      cfg.pin_miso    = -1;
      cfg.pin_dc      = 13;
      _bus.config(cfg);
      _panel.setBus(&_bus);
    }
    {
      auto cfg = _panel.config();
      cfg.pin_cs      = 10;    // CHECK
      cfg.pin_rst     = 14;
      cfg.panel_width  = 480;
      cfg.panel_height = 480;
      cfg.offset_x     = 0;
      cfg.offset_y     = 0;
      cfg.readable     = false;
      cfg.invert       = true;
      _panel.config(cfg);
    }
    setPanel(&_panel);
  }
};
