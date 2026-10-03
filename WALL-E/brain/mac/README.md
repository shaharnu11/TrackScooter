# WALL-E talking — Mac (Apple Silicon)

**Status: works.** Tested 2026-10-03 on a MacBook Pro M4 Max, 48 GB, macOS 15.1:
mic, camera, owner face, Whisper, brain, voice, Spotify. The code is shared
with Windows (it lives in `brain/`). The table at the end lists what differs.

- Needs an **M1 or newer** Mac. Intel Macs: do not use.
- **16 GB RAM or more** for the bigger brains (`8b`, `8b-vl`).
- **32 GB RAM or more** for the Mac's default brain, `30b-vl`.

## Start

Two folders, one per language. Double-click the start script in Finder:

| Language | Start | Listens | Thinks | Speaks |
|---|---|---|---|---|
| English | **`mac/english/start_walle.command`** | Whisper large-v3-turbo | Qwen3-VL-30B (`30b-vl`, sees) | Kokoro (am_michael) |
| Hebrew | **`mac/hebrew/start_walle.command`** | ivrit.ai Whisper large-v3-turbo | DictaLM 3.0 12B (`dicta-12b`) + Qwen3-VL-4B as its eyes | Kokoro Hebrew (he_shaul) + Phonikud |

- Or in Terminal, from `WALL-E/brain`:
  `.venv/bin/python talk_english.py --brain 30b-vl` (English) or
  `.venv/bin/python talk_english.py --lang he --brain dicta-12b` (Hebrew).
- Stop: **Ctrl+C**, **q** in the camera window, or say bye / ביי.
- Options: the same as on Windows (`--brain`, `--mind cloud`, `--type`,
  `--no-camera`, `--sleep-after`). See `../windows/README.md`.
- Voice commands work in both languages in both modes (sleep / לך לישון,
  wake up / תתעורר, management mode / מצב ניהול, update personality /
  עדכון אישיות, forget me / תשכח אותי, music / תנגן…, bye / ביי).
- Hebrew mode hears the secret word in English (it is an English word).

### Personalities

`personalities/english/<name>/` and `personalities/hebrew/<name>/`, each with
`personality.md` (who he is) and optional `examples.md` (sample lines in his
style). Pick one: `./mac/hebrew/start_walle.command --personality shemTovEvi`.
Without `--personality` he is `default`. "Update personality" by voice changes
the one running (backups in its `history/`).

New one from a video: `.venv/bin/python personality_from_video.py VIDEO NAME --lang he`
writes the transcript and still frames to `personalities/hebrew/NAME/source/`
(not in git); then personality.md and examples.md are written from it.
- `hebrew/shemTovEvi`: the washed-up rapper from Kan's satire "עלייתו ונפילתו
  של שם טוב האבי". Edgy on purpose (curses, drug and prison jokes); the joke
  is always on him, never on the visitor's origin, colour or who they love.

### Why these Hebrew models (measured on the M4 Max)

- **Listening:** ivrit.ai large-v3-turbo vs large-v3: 0.24 s vs 0.43 s a
  sentence; letter errors 0.8% vs 0% clean, 3.0% vs 3.8% at 0 dB noise.
- **Brain:** DictaLM 3.0 12B vs Qwen3-VL-30B on the same Hebrew chat: Dicta
  natural and asks back (0.6–1.0 s an answer); Qwen made up words. Dicta
  cannot see, so Qwen3-VL-4B describes the camera in words (0.4–0.7 s).
- **Voice:** Kokoro Hebrew vs Chatterbox Multilingual: Whisper misheard
  0.8% vs 38% of the letters; 0.35 s vs 1.8 s a sentence. Kokoro Hebrew is
  **non-commercial** only. Qwen3-TTS Hebrew (needs its own C++ build and a
  voice sample) was not tried.

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
4. Models (~21 GB for `30b-vl`; Hebrew adds ~12 GB with `--brain dicta-12b`). Download them on the Mac; nothing comes
   from the XPS:
   ```
   .venv/bin/python download_english.py --brain 30b-vl
   .venv/bin/python download_english.py --brain dicta-12b   # Hebrew
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
   chmod +x mac/english/start_walle.command mac/hebrew/start_walle.command
   ```
7. **Permissions:** the first start asks for **Microphone** and **Camera**
   for Terminal. Allow both (System Settings → Privacy & Security).
   The first Spotify command asks to let Terminal **control Spotify**: allow.
8. **Owner** (face + secret word) and **Spotify** (song list) are in git
   (`brain/owner/`, `brain/spotify/`). Nothing to do. The XPS face matched on
   the Mac camera. Only if it stops matching: `.venv/bin/python owner.py enroll`.
9. **Spotify songs offline:** WALL-E can only play downloaded songs without
   internet. All his songs are in one private playlist, **"WALL-E offline"**.
   In the Spotify app on the Mac: open it and switch **Download** on, once.
   After a new `spotify_sync.py`, update it: `spotify_sync.py --offline-playlist`.
10. Optional, **cloud brain**: add to `~/.zshrc`:
    `export ANTHROPIC_API_KEY="sk-ant-..."`. Type it yourself. Do not paste it
    in chat.
11. Music files: put mp3s in `brain/music/`.

## Remembering people (with their yes)

After 3 exchanges with someone new, WALL-E asks: "Can I remember you?"
Only on a yes: their name, then 4 face photos (0.5 s apart, cropped to the
face) and face features, plus notes the brain writes (where from, with
whom, what they like) go to `brain/persons/<name>/`. Next time the face
matches, he greets them by name and knows the notes; the notes grow with
each talk. **"Forget me"** deletes the folder. Never in git, never without
a yes, not for Shahar (already known). Off: `--no-people`. Code: `persons.py`.

## Sleep by voice

- **"Go to sleep"**: the brain is unloaded and the camera stops face and lip
  tracking (the CPU cost). Only the mic and Whisper stay on, to hear
  "wake up". A face does not wake him. The camera window shows SLEEPING.
- **"Wake up"**: back in ~1 s.
- **"Shut down"** (or "bye"): WALL-E quits.
- "I'm going to sleep" is about you, not a command.
- Measured (M4 Max): WALL-E's main process awake ~60% of one core (camera,
  faces, lips, mic), asleep ~3% (mic + speech detector only). The brain
  (`llama-server`, ~19 GB with `30b-vl`) is gone while asleep; Whisper
  (~1.7 GB) stays to hear "wake up".
- Without a command he still sleeps by himself after `--sleep-after`
  seconds with nobody around, and a face wakes him.

## Management mode

Say **"management mode"** (owner face check). WALL-E drops the jokes and
answers plainly about himself: brain, Whisper, voice, camera, lips,
barge-in, music and Spotify, sleep, his commands, the computer and his
personality. Up to five sentences; music words do not start music.
**"Exit management mode"** or **"back to normal"** ends it, and the fun
conversation comes back. Code: `manage.py`.

## Talking over WALL-E (barge-in)

On the Mac you can talk while he talks: he stops at once and answers the
new sentence. The mic and the camera window never stop.

- His own voice is taken out of the mic (WebRTC echo cancellation,
  `echo.py`): alone, his voice was heard as speech in 68% of the mic's
  blocks before, 0% after.
- Measured: a second voice over him stopped him **0.7 s** after it began.
- While he talks, 0.4 s of speech is needed (0.25 s otherwise), so a cough
  does not cut him off.
- Off: `--no-barge-in` (one thing at a time, as on Windows).
- **Moving lips:** a voice counts only while the lips of the face in front
  move. A TV talking next to a quiet face no longer starts a recording or
  cuts him off. Lips: Google's face landmark model (478 points) on the plain
  TFLite runtime (`ai-edge-litert`), ~2 ms a face. Not MediaPipe: it sends
  usage logs to Google and has no off switch. Threshold `LIPS_TALK` 0.75;
  **check it with `.venv/bin/python lips_test.py`** (quiet 6 s, talk 6 s)
  and set it with `WALLE_LIPS_TALK=<n> ./mac/english/start_walle.command`. Off: `--no-lips`.
  Off: `--no-lips`. The log line `speech … lips 3.2` shows the value.
- Not cancelled: music and Spotify (they play on their own). They stay ducked.

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
