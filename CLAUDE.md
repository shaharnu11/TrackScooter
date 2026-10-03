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

Status 2026-10-03 (branch `mac-brain-port`, MacBook Pro M4 Max, 48 GB):
- Steps 1-4 and 6 done. `talk.py --brain 4b-vl` runs end to end
  (mic, camera, owner face, voice). Whisper on the Mac GPU (mlx-whisper).
  Spotify play/next/pause/ducking via AppleScript.
- Step 5: brains `8b-vl` and `30b-vl` (Qwen3-VL-30B-A3B) added. Shahar chose
  **`30b-vl` for the Mac** (Mac only, not offered on Windows; the Mac start
  script uses it). The XPS stays on `4b-vl`. Times: `mac/README.md`.
- Step 4: the Mac uses Whisper `large-v3-turbo` (mlx, 0.22 s, better in
  noise); `WALLE_WHISPER=small` for small.en. The XPS keeps small.en on CUDA.
- Hebrew on the Mac (`--lang he`, `mac/hebrew/start_walle.command`):
  ivrit.ai Whisper turbo, DictaLM 3.0 12B + Qwen3-VL-4B eyes, Kokoro Hebrew
  + Phonikud. Fixed lines via `lang.t()`; commands match both languages.
  English start: `mac/english/start_walle.command`.
- Barge-in on the Mac (`walle/voice/echo.py`, `loop_barge` in talk.py): talk
  over WALL-E, he stops. Windows keeps the old `loop`.
- Open: a real spoken test with Shahar (loud music); Spotify playlists must
  be downloaded in the Mac app for offline; music files from Shahar.

Order of work:
1. Check the Mac: chip and RAM (`sysctl -n machdep.cpu.brand_string`,
   `sysctl -n hw.memsize`). Tell Shahar what that allows.
2. Do the setup in `brain/mac/README.md`. Fix whatever breaks on macOS
   (it was written on Windows and never run on a Mac).
   **Nothing is copied from the XPS. Download everything on the Mac:**
   - `brew install python@3.12 llama.cpp git`, then link `llama-server` into
     `brain/models/llama-cpp/` (README step 5).
   - In `brain/`: make `.venv`, `pip install -r requirements/voice.txt`.
   - Models: `.venv/bin/python scripts/download_models.py --brain 4b-vl`
     (Qwen3-VL-4B + mmproj, Whisper small.en, Kokoro; ~4 GB). Later other
     brains with `--brain 8b` etc. Do not run `scripts/download_hebrew_windows.py`
     (Hebrew only, ~5 GB, not needed).
   - Owner (face + secret word) and Spotify (app ID, login, synced song list)
     **are in git** (`brain/owner/`, `brain/spotify/`, added by Shahar on
     purpose). Use them; no new enroll or login needed. Only if the face
     check fails on the Mac camera: `.venv/bin/python -m walle.people.owner enroll` with
     Shahar there. Only if Spotify refuses the saved login:
     `scripts/spotify_sync.py --client-id <ID>` with Shahar logging in.
   - Cloud key (optional): Shahar adds `export ANTHROPIC_API_KEY=...` to
     `~/.zshrc` himself. Never ask him to paste it in chat.
   - Music files (`brain/music/`) are not in git: ask Shahar for them.
3. Get `talk.py --brain 4b-vl` talking end to end (mic, camera,
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
