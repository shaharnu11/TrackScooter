#!/usr/bin/env python3
"""Download the offline Hebrew STT, TTS, and chat models into ./models.

    python3 download_hebrew_voice.py
    python3 download_hebrew_voice.py --turbo --thinking   # the lighter combo
"""

from __future__ import annotations

import argparse
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

from huggingface_hub import hf_hub_download, snapshot_download

ROOT = Path(__file__).resolve().parent / "models"
STT_DIR = ROOT / "whisper-he"
STT_TURBO_DIR = ROOT / "whisper-he-turbo"
BLUE_DIR = ROOT / "tts-blue"
CHAT_DIR = ROOT / "chat"
GGUF_DIR = ROOT / "chat-gguf"
LLAMA_DIR = ROOT / "llama-cpp"
VOICE_JSON = BLUE_DIR / "voices" / "libri_male_6209.json"

STT_REPO = "ivrit-ai/whisper-large-v3-ct2"
STT_TURBO_REPO = "ivrit-ai/whisper-large-v3-turbo-ct2"
BLUE_REPO = "notmax123/BlueTTS2.5-onnx"
# Mac: MLX. XPS (NVIDIA): the same model as GGUF, run by llama.cpp on CUDA.
CHAT_REPO = "ssdataanalysis/DictaLM-3.0-1.7B-Instruct-mlx-8Bit"
GGUF_REPO = "EMD123/DictaLM-3.0-1.7B-Instruct-Q4_K_M-GGUF"
GGUF_FILE = "dictalm-3.0-1.7b-instruct-q4_k_m.gguf"
# Dicta's own GGUF of the reasoning model. XPS only: no MLX build of it.
THINK_GGUF_REPO = "dicta-il/DictaLM-3.0-1.7B-Thinking-GGUF"
THINK_GGUF_FILE = "DictaLM-3.0-1.7B-Thinking-Q4_K_M.gguf"
LLAMA_BUILD = "b11191"
LLAMA_ZIPS = (
    f"llama-{LLAMA_BUILD}-bin-win-cuda-12.4-x64.zip",
    "cudart-llama-bin-win-cuda-12.4-x64.zip",
)


def fetch(repo: str, dest: Path, label: str) -> None:
    print(f"{label}: {repo}")
    dest.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=repo, local_dir=str(dest))


def fetch_llama_windows() -> None:
    """llama.cpp's own CUDA 12.4 build, plus the CUDA runtime DLLs it needs."""
    if (LLAMA_DIR / "llama-server.exe").exists():
        print(f"llama.cpp already at {LLAMA_DIR}")
        return
    LLAMA_DIR.mkdir(parents=True, exist_ok=True)
    base = f"https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_BUILD}"
    for name in LLAMA_ZIPS:
        print(f"llama.cpp: {name}")
        zip_path = LLAMA_DIR / name
        urllib.request.urlretrieve(f"{base}/{name}", zip_path)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(LLAMA_DIR)
        zip_path.unlink()


def fetch_stt(repo: str, dest: Path, size: str) -> None:
    if (dest / "model.bin").exists():
        print(f"STT already at {dest}")
        return
    print(f"STT: {repo}  ({size})")
    tmp = dest.with_name(dest.name + "-new")
    if tmp.exists():
        shutil.rmtree(tmp)
    snapshot_download(repo_id=repo, local_dir=str(tmp))
    if dest.exists():
        shutil.rmtree(dest)
    tmp.rename(dest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--turbo", action="store_true", help="Whisper large-v3-turbo (~1.6 GB)"
    )
    parser.add_argument(
        "--thinking", action="store_true", help="DictaLM 1.7B Thinking GGUF"
    )
    args = parser.parse_args()
    if args.thinking and sys.platform == "darwin":
        parser.error("--thinking is GGUF / llama.cpp only, not MLX")
    ROOT.mkdir(parents=True, exist_ok=True)

    if args.turbo:
        stt = STT_TURBO_DIR
        fetch_stt(STT_TURBO_REPO, stt, "~1.6 GB")
    else:
        stt = STT_DIR
        fetch_stt(STT_REPO, stt, "~3.1 GB, 2025-05-13 weights")

    fetch(BLUE_REPO, BLUE_DIR, "TTS")
    if not VOICE_JSON.exists():
        raise SystemExit(f"Missing BlueTTS voice: {VOICE_JSON}")

    if sys.platform == "darwin":
        fetch(CHAT_REPO, CHAT_DIR, "Chat")
        chat = CHAT_DIR
    else:
        repo, name = (
            (THINK_GGUF_REPO, THINK_GGUF_FILE) if args.thinking else (GGUF_REPO, GGUF_FILE)
        )
        print(f"Chat: {repo}")
        GGUF_DIR.mkdir(parents=True, exist_ok=True)
        hf_hub_download(repo_id=repo, filename=name, local_dir=str(GGUF_DIR))
        chat = GGUF_DIR / name
        if sys.platform == "win32":
            fetch_llama_windows()

    print()
    print("Done.")
    print(f"  STT  {stt}")
    print(f"  TTS  {BLUE_DIR}")
    print(f"  voice {VOICE_JSON}")
    print(f"  chat {chat}")
    print("Try it:  python3 try_hebrew_voice.py")
    flags = " --turbo" * args.turbo + " --thinking" * args.thinking
    print(f"Talk:    python3 talk_hebrew.py{flags}")


if __name__ == "__main__":
    main()
