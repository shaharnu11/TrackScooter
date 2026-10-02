# Notes for Claude

## How to write to Shahar

- English is not his native language.
- Answer in short bullet points. Plain, simple words. Short sentences.
- No extra adjectives, no filler, no long introductions.
- Be clear and direct: what it is, what to do.

## WALL-E (folder `WALL-E/`)

- A WALL-E robot on 2 tracked scooter pods, for the **Midburn desert festival**:
  loud background music, dust, sun, **mostly offline**.
- Brain = a laptop running `WALL-E/brain/talk_english.py --brain 4b-vl`:
  Qwen3-VL-4B (llama.cpp) + Whisper small.en + Kokoro voice + Silero VAD,
  music folder + Spotify, sleep mode, owner face + secret word, optional
  `--mind cloud` (Claude API). This is the chosen setup.
- Robot control: Teensy "Spine" (`WALL-E/firmware/spine`), 2 eye boards,
  sensors. Parts list and purchases: `WALL-E/docs/05-bom.md`.
  Eyes (3D-printed cartridge): `WALL-E/cad/eye/README.md`.
- Never put API keys, the owner face/secret (`brain/owner/`), or the Spotify
  login (`brain/spotify/`) in git or in chat.

## Current task (2026-10): move the talking brain to a Mac

The brain ran on a Dell XPS 15 (Windows, RTX 3050 Ti 4 GB). Shahar is now
moving it to an Apple Silicon Mac. Start with `WALL-E/brain/mac/README.md`
(setup, and what differs from Windows). Windows steps: `WALL-E/brain/windows/`.

Order of work:
1. Check the Mac: chip and RAM (`sysctl -n machdep.cpu.brand_string`,
   `sysctl -n hw.memsize`). Tell Shahar what that allows.
2. Do the setup in `brain/mac/README.md`. Fix whatever breaks on macOS
   (it was written on Windows and never run on a Mac).
   **Nothing is copied from the XPS. Download everything on the Mac:**
   - `brew install python@3.12 llama.cpp git`, then link `llama-server` into
     `brain/models/llama-cpp/` (README step 5).
   - In `brain/`: make `.venv`, `pip install -r requirements-voice.txt`.
   - Models: `.venv/bin/python download_english.py --brain 4b-vl`
     (Qwen3-VL-4B + mmproj, Whisper small.en, Kokoro; ~4 GB). Later other
     brains with `--brain 8b` etc. Do not run `download_hebrew_voice.py`
     (Hebrew only, ~5 GB, not needed).
   - Owner (face + secret word): run `.venv/bin/python owner.py enroll` with
     Shahar at the camera. He types the secret word himself.
   - Spotify (optional): `spotify_sync.py --client-id <ID>` needs Shahar's
     Spotify developer app ID and his login in the browser. Ask him first.
   - Cloud key (optional): Shahar adds `export ANTHROPIC_API_KEY=...` to
     `~/.zshrc` himself. Never ask him to paste it in chat.
   - Music files (`brain/music/`) are not in git: ask Shahar for them.
3. Get `talk_english.py --brain 4b-vl` talking end to end (mic, camera,
   voice). Grant Microphone + Camera to the terminal.
4. Whisper on the Mac GPU: replace faster-whisper (CPU only on Mac) with
   mlx-whisper or whisper.cpp, behind a platform check. Keep the Windows
   CUDA path working. Target ~0.5 s per turn.
5. With 16 GB+ RAM: try a bigger brain (`--brain 8b`, a bigger vision model).
6. Spotify ducking on Mac (AppleScript volume), if Shahar wants it.

Rules for the port:
- One shared code base. Use `sys.platform` checks; no copy of the code per OS.
- Keep the Windows XPS path working.
- Judge changes against: loud music, no internet, battery power.
