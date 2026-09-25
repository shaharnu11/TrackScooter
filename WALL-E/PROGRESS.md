# WALL-E — where we stopped

Read this first. Date: **2026-09-26**. Branch: `walle-xps-two-floor-packs`.

This is the Midburn tracked robot that uses the two Apollo pods. The original scooter is a separate machine. Do not mix their wiring rules.

Talk to the owner in short numbered points and everyday English. Do not commit unless asked. Do not push unless asked. Do not skip contactors. Do not treat garden autonomy as Midburn self-drive.

---

## What works right now (Mac, tonight)

Hebrew talk with the USB camera is **live and answering**.

```bash
cd WALL-E/brain
PYTHONUNBUFFERED=1 ./.venv/bin/python -u talk_hebrew.py --auto
```

- Window title: **WALL-E speaker lock**. Green **YOU** box = talker. `q` quits.
- No Enter. Face lock + loud mic (`rms > 0.025`) starts a recording.
- Pipeline: ivrit Whisper Large v3 (CPU int8) → DictaLM 1.7B MLX 8-bit → BlueTTS.
- Models live in `brain/models/` and are **not in git**. Download: `python3 download_hebrew_voice.py`.
- Venv: `WALL-E/brain/.venv` (Python 3.14). Homebrew `python3` has no `cv2`.
- It is **slow**. Whisper on CPU is the wait. Chat on this Mac already uses Apple GPU via MLX. XPS later: Whisper on CUDA; MLX will not run (need GGUF/CUDA). XPS 15 9510 GPU is about 4 GB — Whisper + chat may not both fit.

Debug camera+mic only (no LLM):

```bash
PYTHONUNBUFFERED=1 ./.venv/bin/python -u debug_live.py
```

Known bugs still in the live loop:

1. Mouth motion (`mouth_ema`) stays ~0. Listen uses **sound**, not mouth.
2. YuNet false faces (plants). Mitigated: `max_faces=1`, score 0.55, `min_rel_h=0.08`. Sit close.
3. He can hear his own speaker after TTS. No mute-while-speaking yet.
4. `TalkCam.locked()` was missing; added. Do not rename it to `.lock` — that is the `SpeakerLock` object.

---

## Brain map

| File | Role |
|---|---|
| `brain/personality.py` | Named actions only. **Never a motor number.** |
| `brain/talk_hebrew.py` | Live Hebrew + camera lock |
| `brain/usb_camera.py` | ELP, YuNet, mouth EMA |
| `brain/hebrew_voice.py` | Whisper + BlueTTS |
| `brain/speaker_lock.py` | Who is talking |
| `brain/perception.py` | Snapshot. `tof_poll()` still empty |
| `brain/main.py` | 20 Hz loop to Spine (not wired to talk yet) |
| `brain/test_safety.py` | Personality invariants |

Garden ASSIST (radio **on**, sticks centred, Spine still owns stop):

- Close person `< 1.2 m` → `retreat`
- No person + `may_move` → 25% chance `nudge_forward` (1 s, 0.25)
- Person 1.5–4 m + `may_move` → `follow` (speed 0.20, turn from `gaze_az`, clamp ±0.20)

**Owner said: build follow later.** Code is already in `personality.py`. Do not push more follow until asked. Midburn stays MANUAL / radio. No unsupervised crowd self-drive.

---

## Locked hardware / safety (do not reopen)

- Teensy owns motors. Radio and E-stop on the Spine.
- Brain = owned XPS 15 9510. Offline. No Jetson. No cloud at the event.
- Pack A+ and Pack B+ never meet. Contactor coils on Pack A.
- 12 V electronics pack (D8). XPS not on that rail. Every battery removable.
- Head rigid. Gaze = pupils. Camera = ELP-USB1080P03-KLC1100.
- **DC contactors stay.** Owner asked to skip them more than once. Refuse.
- Low-level e-brake = pull to GND via PC817. Radio stays on in ASSIST.
- Rear pod rails bolt to **inboard green plates** (M12 at 108/168 mm forward of hub), not carrier-only. Sleeves Ø25×Ø13×40 flush or 0.5 mm short, weld, then grind. Front fork is still carriers; front fork→frame is **undesigned**.
- CAD frame is still **60×30** unless the owner asks to change it to 100×40.

---

## Contactor / fuse buy (decided in chat, **docs not fully updated**)

BOM still says Albright 80 A+ and 60 A fuses / XT90-S. Chat decision:

| Item | Decision |
|---|---|
| Contactor | **ZJ50A** (or ZJ100A), **48 V coil**, 1NO, **DC** rated. Not CJX2-K (that listing is coil-only / AC). |
| Fuse | **40 A**, **smaller than the contactor**. Not 50 A fuse on a 50 A contactor. J-case must be **58 V DC**, not 32 V. |
| Main plug | Owner already has **XT60**. Allowed for ~250 W **only if you plug with contactors open**. |
| Mushroom | **NC on the coil chain only** (~0.3 A/coil). Battery motor current does **not** go through the mushroom. |
| Arm | Radio channel 3. Coil powered while armed. |

Do not “limit amps in software” instead of contactors. Nameplate 250 W / 48 V is not stall current.

Lighting buy (WS2815 12 V 60/m IP67, fused 12 V, not 48 V) was designed in chat. **Not in the BOM yet.**

---

## Still open / next work

1. Mute the mic while TTS plays (he talks to himself).
2. Port talk to XPS: CUDA Whisper, non-MLX chat, keep answers short.
3. Wire `talk_hebrew` into `main.py` / personality (one place for camera + rules + talk).
4. Follow behaviour: already coded; owner wants it later.
5. Update BOM/docs to ZJ50A + 40 A fuse + XT60 if owner confirms buy.
6. CAD 100×40 only if asked. Front fork→frame.
7. `tof_poll()` empty. IMU/LiDAR empty.
8. Do not commit `brain/models/` weights.

Hebrew character = SYSTEM prompt in `talk_hebrew.py`, not a fine-tune.
