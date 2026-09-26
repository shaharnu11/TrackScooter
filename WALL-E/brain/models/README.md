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
| `whisper-he-turbo/` | STT, `--turbo`: ivrit-ai/whisper-large-v3-turbo-ct2. ~1.1 GB VRAM vs ~2.0 |
| `chat-gguf/` | XPS chat, llama.cpp CUDA: DictaLM 1.7B Instruct Q4_K_M, or Thinking Q4_K_M with `--thinking` |
| `tts-blue/` | TTS: BlueTTS 2.5 + ReNikud. Voice `libri_male_6209` |
| `chat/` | DictaLM-3.0-1.7B-Instruct, MLX 8-bit (this Mac). XPS uses NVIDIA later |
| `whisper-en/` | English STT (`talk_english.py`): Systran/faster-whisper-small.en |
| `tts-kokoro/` | English TTS: Kokoro v1.0 ONNX, voice `am_michael`. CPU |
| `chat-gguf/Qwen3-*` | English brains: `--brain 4b` / `4b-q5` / `8b`. `python3 download_english.py` |
| `camera/face_detection_yunet_2023mar.onnx` | YuNet. Auto-download on first camera open |
