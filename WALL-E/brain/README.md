# Brain

XPS 15 9510. Python. Camera, personality, sounds, optional local LLM. **No internet.** Allowed to be slow and to crash. Radio is on the Spine.

Closed on the upper tray, spacers. PD 65 W+ and 12 V pack on the lower deck. USB hub on the tray (12 V rail): ELP camera, LiDAR, Teensy, Face. Speaker boxes off → tray out.

## Files

| File | |
|---|---|
| `main.py` | 20 Hz loop |
| `spine_link.py` | Teensy serial |
| `face_link.py` | Two eye boards |
| `perception.py` | Camera + speaker-lock. LiDAR/IMU empty |
| `personality.py` | Behaviours |
| `usb_camera.py` | ELP, YuNet, 86° |
| `talk_hebrew.py` | Live Hebrew mic loop |
| `test_safety.py` | Personality invariants |

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python3 main.py --spine /dev/ttyACM0 --face /dev/ttyUSB0 /dev/ttyUSB1
python3 test_safety.py
```

Windows: `COM` ports. Sensor libs commented until hardware exists.

## Load-bearing

1. **Heartbeat is the command**, from the control loop, not a side thread. Loop stall → beat stall. Zero command is still a beat.
2. **AI never emits a motor number.** Actions: `idle` · `look_at` · `greet` · `retreat` · `nudge_forward` · `play_sound`. `motion_for()` maps them. Cap 30 % (`test_safety.py`).
3. **Stale ≠ clear.** Every reading has a time. Missing IMU blocks motion. Missing bumper halves speed.

Sensor threads write one slot. No queues.

## Still empty

IMU, LiDAR, sounds in the control loop.

Hebrew try-out:

```bash
pip install -r requirements-voice.txt
python3 download_hebrew_voice.py
python3 talk_hebrew.py          # Enter, speak, go quiet
python3 try_speaker_lock.py     # camera window
```

STT ivrit Whisper Large v3. TTS BlueTTS. Chat DictaLM. Files in `models/` (not in git). `--type` if the mic is blocked.
