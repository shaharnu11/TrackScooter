#!/usr/bin/env python3
"""Download the offline Hebrew STT, TTS, and chat models into ./models.

    python3 download_hebrew_voice.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parent / "models"
STT_DIR = ROOT / "whisper-he"
BLUE_DIR = ROOT / "tts-blue"
CHAT_DIR = ROOT / "chat"
VOICE_JSON = BLUE_DIR / "voices" / "libri_male_6209.json"

STT_REPO = "ivrit-ai/whisper-large-v3-ct2"
BLUE_REPO = "notmax123/BlueTTS2.5-onnx"
CHAT_REPO = "ssdataanalysis/DictaLM-3.0-1.7B-Instruct-mlx-8Bit"


def fetch(repo: str, dest: Path, label: str) -> None:
    print(f"{label}: {repo}")
    dest.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=repo, local_dir=str(dest))


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)

    if not (STT_DIR / "model.bin").exists():
        print(f"STT: {STT_REPO}  (~3.1 GB, 2025-05-13 weights)")
        tmp = ROOT / "whisper-he-new"
        if tmp.exists():
            shutil.rmtree(tmp)
        snapshot_download(repo_id=STT_REPO, local_dir=str(tmp))
        if STT_DIR.exists():
            shutil.rmtree(STT_DIR)
        tmp.rename(STT_DIR)
    else:
        print(f"STT already at {STT_DIR}")

    fetch(BLUE_REPO, BLUE_DIR, "TTS")
    if not VOICE_JSON.exists():
        raise SystemExit(f"Missing BlueTTS voice: {VOICE_JSON}")

    fetch(CHAT_REPO, CHAT_DIR, "Chat")

    print()
    print("Done.")
    print(f"  STT  {STT_DIR}")
    print(f"  TTS  {BLUE_DIR}")
    print(f"  voice {VOICE_JSON}")
    print(f"  chat {CHAT_DIR}")
    print("Try it:  python3 try_hebrew_voice.py")
    print("Talk:    python3 talk_hebrew.py")


if __name__ == "__main__":
    main()
