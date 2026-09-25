# Hebrew speech models (offline)

Not in git. Large.

```bash
cd WALL-E/brain
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-voice.txt
python3 download_hebrew_voice.py
python3 talk_hebrew.py
```

| Path | |
|---|---|
| `whisper-he/` | STT: ivrit-ai/whisper-large-v3-ct2 (2025-05-13) |
| `tts-blue/` | TTS: BlueTTS 2.5 + ReNikud. Voice `libri_male_6209` |
| `chat/` | DictaLM-3.0-1.7B-Instruct, MLX 8-bit (this Mac). XPS uses NVIDIA later |
| `camera/face_detection_yunet_2023mar.onnx` | YuNet. Auto-download on first camera open |
