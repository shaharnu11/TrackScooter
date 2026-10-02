# WALL-E talking — Windows (Dell XPS 15, RTX 3050 Ti 4 GB)

This is the setup that works today. The code is shared: it lives in `brain/`,
not in this folder. This folder has only the Windows steps and the start script.

## Start

- Double-click **`start_walle.bat`**, or in a terminal:
  ```
  cd WALL-E\brain
  .venv\Scripts\python.exe talk_english.py --brain 4b-vl
  ```
- Stop: **Ctrl+C**, or close the window.
- Options (add after the command, or after `start_walle.bat`):

| Option | What |
|---|---|
| `--brain 4b-vl` | **Default here.** Qwen3-VL-4B, sees the camera |
| `--brain 4b` / `4b-q5` / `8b` | Other brains, no vision (`8b` is slower) |
| `--mind cloud` | Claude over the internet (needs the API key) |
| `--type` | Type instead of talking (mic blocked) |
| `--no-camera` | No camera |
| `--sleep-after 120` | Seconds with nobody before sleep mode |

## Setup (once, on a new Windows PC)

1. **Python 3.12** from python.org. Tick "Add to PATH".
2. **NVIDIA driver** (recent). Check: `nvidia-smi` shows the GPU.
3. Get the code: `git clone https://github.com/shaharnu11/TrackScooter.git`
4. Make the Python environment, in `WALL-E\brain`:
   ```
   python -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements-voice.txt
   ```
5. Download the models (~4 GB for English; more if you take all brains):
   ```
   .venv\Scripts\python.exe download_english.py --brain 4b-vl
   ```
6. Download **llama.cpp (CUDA build)**. It comes from the Hebrew script. That
   script also downloads the Hebrew models (~5 GB extra):
   ```
   .venv\Scripts\python.exe download_hebrew_voice.py --turbo
   ```
   Or copy `models\llama-cpp\` from the XPS. Faster.
7. **Owner** (your face + secret word, once):
   ```
   .venv\Scripts\python.exe owner.py enroll
   ```
   Or copy `brain\owner\` from the XPS.
8. Optional, **Spotify** (desktop app, logged in):
   ```
   .venv\Scripts\python.exe spotify_sync.py --client-id <ID>
   .venv\Scripts\python.exe spotify_sync.py
   ```
9. Optional, **cloud brain**: in a terminal, `setx ANTHROPIC_API_KEY "sk-ant-..."`.
   Type it yourself. Do not paste the key in chat.
10. Music files: put mp3s in `brain\music\`.

## Where things are

| Folder | What | In git? |
|---|---|---|
| `brain\*.py`, `personality.md` | code + character | yes |
| `brain\models\` | brains, Whisper, Kokoro voice, llama.cpp | no (~4–20 GB) |
| `brain\.venv\` | Python + packages | no |
| `brain\owner\`, `brain\spotify\` | your face/secret, Spotify login | no, private |

## Windows-only parts

- **llama.cpp CUDA build** (`models\llama-cpp\llama-server.exe`).
- **Whisper on the GPU** (faster-whisper + CUDA, ~0.5 s per turn).
- **Sleep mode** turns the GPU fully off (D3) to save power.
- **Spotify ducking** lowers Spotify in the Windows mixer while WALL-E talks.
- The cloud key is read from the Windows user settings (`setx`).

## Problems

| Problem | Fix |
|---|---|
| `No module named kokoro_onnx` | Wrong Python. Use `.venv\Scripts\python.exe` (the .bat does) |
| Brain does not start, port busy | An old `llama-server.exe` is running. The .bat stops it. By hand: `taskkill /im llama-server.exe /f` |
| Slow answers | GPU too hot, capped at 20 W. Check `nvidia-smi`. Give the laptop air |
| No sound in / out | Windows Settings → Sound: pick the USB mic (BOYA sound card) and the speakers |
