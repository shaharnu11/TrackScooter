# WALL-E talking — Mac (Apple Silicon)

**Status: not tested on a Mac yet.** The code is shared with Windows (it lives
in `brain/`). Most of it should run on a Mac as it is. The table at the end
lists what is different or missing.

- Needs an **M1 or newer** Mac. Intel Macs: do not use.
- **16 GB RAM or more** to gain over the XPS (bigger brains fit). 8 GB is
  about the same as the XPS.

## Start

- Double-click **`start_walle.command`** in Finder, or in Terminal:
  ```
  cd WALL-E/brain
  .venv/bin/python talk_english.py --brain 4b-vl
  ```
- Stop: **Ctrl+C**, or close the window.
- Options: the same as on Windows (`--brain`, `--mind cloud`, `--type`,
  `--no-camera`, `--sleep-after`). See `../windows/README.md`.

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
4. Models (~4 GB for `4b-vl`; the same files as on Windows):
   ```
   .venv/bin/python download_english.py --brain 4b-vl
   ```
   Or copy `models/chat-gguf/`, `models/whisper-en/` and `models/tts-kokoro/`
   from the XPS.
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
8. **Owner** (face + secret word): `.venv/bin/python owner.py enroll`, or copy
   `brain/owner/` from the XPS.
9. Optional, **cloud brain**: add to `~/.zshrc`:
   `export ANTHROPIC_API_KEY="sk-ant-..."`. Type it yourself. Do not paste it
   in chat.
10. Music files: put mp3s in `brain/music/`.

## Differences from Windows

| Part | Windows (XPS) | Mac |
|---|---|---|
| Brain (llama.cpp) | CUDA build, 4 GB GPU | Homebrew build, **Metal** GPU, uses the shared RAM. Should work as is |
| Whisper (speech-to-text) | GPU, ~0.5 s per turn | **CPU only** (faster-whisper has no Mac GPU). Slower, maybe ~1–2 s. Falls back by itself |
| Kokoro voice | CPU | CPU. Works |
| Camera | works | works (Camera permission) |
| Sleep mode | GPU fully off (D3) | Stops the brain to free memory. No GPU switch needed |
| Spotify ducking | Windows mixer | **Not on Mac.** Spotify keeps its volume while WALL-E talks |
| Cloud key | `setx` (Windows settings) | `export` in `~/.zshrc` |
| Teensy / eyes / CP2102 | `COM3`, `COM4`… | `/dev/tty.usbmodem…`, `/dev/tty.usbserial…` |

## To do, to make the Mac better

- Whisper on the Mac GPU: switch to **mlx-whisper** or **whisper.cpp**
  (back to ~0.5 s per turn).
- With 16 GB+: try `--brain 8b`, or a bigger vision brain.
- Spotify ducking: lower the volume with AppleScript.
