# Brain

WALL-E's laptop side: talking (mic, camera, brain, voice) and the robot
control loop. Same code on the Mac and the Windows XPS.

## Start

| What | Mac | Windows (XPS) |
|---|---|---|
| Talk, English | double-click `mac/english/start_walle.command` | double-click `windows\start_walle.bat` |
| Talk, Hebrew | double-click `mac/hebrew/start_walle.command` | `legacy\talk_hebrew.py` (old Hebrew talker) |
| Setup | [`mac/README.md`](mac/README.md) | [`windows/README.md`](windows/README.md) |

Or `.venv/bin/python talk.py --help` for every option (`--lang`, `--brain`,
`--personality`, `--mind cloud`, `--type`, ...).

## Folders

```
brain/
  talk.py            start talking (calls walle/talker.py)
  robot.py           the robot control loop (20 Hz: Spine, eyes, behaviour)
  walle/             all the code
    talker.py        the talk loops: listen, answer, barge-in, owner/visitor
    paths.py         every data folder, in one place
    lang.py          English / Hebrew lines: t(en, he)
    voice/           speech.py (Whisper + Kokoro), listen.py (speech detector),
                     echo.py (echo cancelling), loud_listen.py, util.py
    mind/            chat.py (local / cloud brains, eyes), brains.py (--brain list),
                     llama.py (llama-server), rules.py, sleeper.py
    eyes/            camera.py (faces, lips), talk_cam.py (camera window)
    people/          owner.py (Shahar's face), persons.py (people who said yes)
    modes/           management.py, personality_editor.py, tools.py (owner tools)
    music/           player.py (music folder), spotify.py
    robot/           perception.py, behavior.py, speaker_lock.py, spine_link.py, face_link.py
  rules/             how he must behave (every personality); the owner changes them in management mode
  personalities/     english/<name>/, hebrew/<name>/: who he is
  scripts/           download_models.py, spotify_sync.py, lips_test.py,
                     personality_from_video.py, download_hebrew_windows.py
  tests/             test_safety.py, test_speaker_lock.py
  experiments/       try-outs: debug_live.py, try_hebrew_voice.py, try_speaker_lock.py
  legacy/            the old Windows Hebrew talker (talk_hebrew.py, hebrew_voice.py)
  requirements/      voice.txt (talking), hebrew.txt (old Hebrew), robot.txt (control loop)
  mac/  windows/     start scripts and setup notes per computer
  models/ owner/ persons/ spotify/ music/    data (models and persons/ not in git)
```

Run every script from `brain/` (`.venv/bin/python scripts/lips_test.py`);
the owner's face enroll is `.venv/bin/python -m walle.people.owner enroll`.

## Robot control loop

XPS 15 9510. Python. Camera, personality, sounds, optional local LLM. **No internet.** Allowed to be slow and to crash. Radio is on the Spine.

Closed on the upper tray, spacers. PD 65 W+ and 12 V pack on the lower deck. USB hub on the tray (12 V rail): ELP camera, LiDAR, Teensy, Face. Speaker boxes off → tray out.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements/robot.txt
python3 robot.py --spine /dev/ttyACM0 --face /dev/ttyUSB0 /dev/ttyUSB1
python3 tests/test_safety.py
```

Windows: `COM` ports. Sensor libs commented until hardware exists.

## Load-bearing

1. **Heartbeat is the command**, from the control loop, not a side thread. Loop stall → beat stall. Zero command is still a beat.
2. **AI never emits a motor number.** Actions: `idle` · `look_at` · `greet` · `retreat` · `nudge_forward` · `follow` · `play_sound`. `motion_for()` maps them. Cap 30 % (`tests/test_safety.py`).
3. **Stale ≠ clear.** Every reading has a time. Missing IMU blocks motion. Missing bumper halves speed.

Sensor threads write one slot. No queues.

## Still empty

IMU, LiDAR, sounds in the control loop.
