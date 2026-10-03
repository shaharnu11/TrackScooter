# WALL-E talking — Mac (Apple Silicon)

**Status: works.** Tested 2026-10-03 on a MacBook Pro M4 Max, 48 GB, macOS 15.1:
mic, camera, owner face, Whisper, brain, voice, Spotify. The code is shared
with Windows (it lives in `brain/`). The table at the end lists what differs.

- Needs an **M1 or newer** Mac. Intel Macs: do not use.
- **16 GB RAM or more** for the bigger brains (`8b`, `8b-vl`).
- **32 GB RAM or more** for the Mac's default brain, `30b-vl`.

## Start

- Double-click **`start_walle.command`** in Finder, or in Terminal:
  ```
  cd WALL-E/brain
  .venv/bin/python talk_english.py --brain 30b-vl
  ```
- Stop: **Ctrl+C**, or close the window.
- Options: the same as on Windows (`--brain`, `--mind cloud`, `--type`,
  `--no-camera`, `--sleep-after`). See `../windows/README.md`.
- Brain on the Mac: **`30b-vl`** (Qwen3-VL-30B-A3B, sees). **Mac only**:
  Windows does not offer it. Smaller ones: `--brain 4b-vl`, `--brain 8b-vl`.

## Setup (once)

1. **Homebrew** (https://brew.sh), then in Terminal:
   ```
   brew install python@3.12 llama.cpp git
   ```
2. Get the code:
   ```
   git clone https://github.com/shaharnu11/TrackScooter.git
   cd TrackScooter/WALL-E/brain
   ```
3. Python environment:
   ```
   python3.12 -m venv .venv
   .venv/bin/python -m pip install -r requirements-voice.txt
   ```
4. Models (~21 GB for `30b-vl`). Download them on the Mac; nothing comes
   from the XPS:
   ```
   .venv/bin/python download_english.py --brain 30b-vl
   ```
   On the Mac this also gets Whisper for the Mac GPU (`models/whisper-turbo-mlx/`,
   `models/whisper-en-mlx/`)
   and the two camera face models. **Run it while online**: after that,
   WALL-E needs no internet.
5. **llama.cpp**: the code looks for it in `models/llama-cpp/`. Link the
   Homebrew one there:
   ```
   mkdir -p models/llama-cpp
   ln -sf "$(which llama-server)" models/llama-cpp/llama-server
   ```
   (Do not copy the Windows `llama-server.exe`. It does not run on a Mac.)
6. Allow the start script to run (once):
   ```
   chmod +x mac/start_walle.command
   ```
7. **Permissions:** the first start asks for **Microphone** and **Camera**
   for Terminal. Allow both (System Settings → Privacy & Security).
   The first Spotify command asks to let Terminal **control Spotify**: allow.
8. **Owner** (face + secret word) and **Spotify** (song list) are in git
   (`brain/owner/`, `brain/spotify/`). Nothing to do. The XPS face matched on
   the Mac camera. Only if it stops matching: `.venv/bin/python owner.py enroll`.
9. **Spotify songs offline:** open the Spotify app on the Mac, log in, and
   **download** the playlists (the green arrow). WALL-E can only play
   downloaded songs without internet.
10. Optional, **cloud brain**: add to `~/.zshrc`:
    `export ANTHROPIC_API_KEY="sk-ant-..."`. Type it yourself. Do not paste it
    in chat.
11. Music files: put mp3s in `brain/music/`.

## Measured on the M4 Max

| Step | Mac (M4 Max) | XPS (3050 Ti) |
|---|---|---|
| Whisper `large-v3-turbo` (Mac default), per question | **0.22 s** (Mac GPU) | does not fit |
| Whisper `small.en`, per question | 0.07 s (Mac GPU) | ~0.5 s (GPU) |
| Whisper on CPU (fallback) | 0.9 s | 2.5 s |
| Brain `4b-vl`, first sentence | 0.2–0.4 s | — |
| Brain `4b-vl`, a look through the camera | **0.6 s** | 5.9–6.5 s |
| Brain `8b-vl`, first sentence | 0.15–0.45 s | does not fit |
| Brain `8b-vl`, a look through the camera | 0.8 s | does not fit |
| Brain `30b-vl` (Mac default), first sentence | 0.2–0.6 s | does not fit |
| Brain `30b-vl`, a look through the camera | 0.8 s | does not fit |
| Wake from sleep (Whisper + `30b-vl`) | ~1 s | ~6–7 s (all) |
| First start after boot (`4b-vl` / `8b-vl` / `30b-vl`) | 1.2 / 2.4 / 7.6 s | — |

`30b-vl` gave the best answers of the three; `8b-vl` is shorter and drier.

**Whisper in noise** (speech mixed with kick drum, bass, synth and crowd talk;
word errors): at 5 dB turbo 0%, small.en 4%; at 0 dB turbo 10%, small.en
12.5%; at −3 dB both ~30%. Back to small.en: `WALLE_WHISPER=small`.

## Differences from Windows

| Part | Windows (XPS) | Mac |
|---|---|---|
| Brain (llama.cpp) | CUDA build, 4 GB GPU | Homebrew build, **Metal** GPU, shared RAM. All layers and the eye model on the GPU |
| Whisper (speech-to-text) | faster-whisper `small.en`, CUDA | **mlx-whisper `large-v3-turbo`** on the Mac GPU. Falls back to faster-whisper on the CPU if the MLX model is missing. `WALLE_WHISPER_DEVICE=cpu` forces the CPU |
| Kokoro voice | CPU | CPU |
| Camera | DirectShow | AVFoundation (Camera permission) |
| Sleep mode | GPU fully off (D3) | Stops the brain and Whisper to free memory |
| Spotify control | Windows media keys + window title | **AppleScript** (`osascript`) |
| Spotify ducking | Windows mixer (pycaw) | Spotify's own volume, by AppleScript |
| Cloud key | `setx` (Windows settings) | `export` in `~/.zshrc` |
| Teensy / eyes / CP2102 | `COM3`, `COM4`… | `/dev/tty.usbmodem…`, `/dev/tty.usbserial…` |

## Known harmless messages

- `objc: Class AVFFrameReceiver is implemented in both …av… and …cv2…`:
  two libraries bring the same video code. Ignore it.
- `IMKClient subclass`: macOS text input, from the camera window. Ignore it.

## Hebrew

Not set up on the Mac. If needed: `pip install -r requirements-hebrew.txt`
and `download_hebrew_voice.py` (~5 GB).
