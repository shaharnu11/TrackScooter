#!/usr/bin/env python3
"""Download the offline English STT, TTS, and chat models into ./models.

    python3 download_english.py              # all three brains
    python3 download_english.py --brain 4b   # just one

llama.cpp itself comes from download_hebrew_voice.py.
"""

from __future__ import annotations

import argparse
import urllib.request

from huggingface_hub import hf_hub_download, snapshot_download

from english_voice import (
    BRAINS,
    GGUF_DIR,
    KOKORO_DIR,
    KOKORO_FILES,
    KOKORO_URL,
    STT_DIR,
    STT_REPO,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brain", choices=BRAINS, help="Only this brain (default: all)")
    args = parser.parse_args()

    if not (STT_DIR / "model.bin").exists():
        print(f"STT: {STT_REPO}  (~0.5 GB)")
        snapshot_download(repo_id=STT_REPO, local_dir=str(STT_DIR))
    else:
        print(f"STT already at {STT_DIR}")

    KOKORO_DIR.mkdir(parents=True, exist_ok=True)
    for name in KOKORO_FILES:
        dest = KOKORO_DIR / name
        if not dest.exists():
            print(f"TTS: {name}")
            tmp = dest.with_suffix(dest.suffix + ".part")
            urllib.request.urlretrieve(f"{KOKORO_URL}/{name}", tmp)
            tmp.rename(dest)

    GGUF_DIR.mkdir(parents=True, exist_ok=True)
    for key, brain in BRAINS.items():
        if args.brain and key != args.brain:
            continue
        print(f"Brain {key}: {brain.repo} / {brain.file}")
        hf_hub_download(repo_id=brain.repo, filename=brain.file, local_dir=str(GGUF_DIR))
        if brain.mmproj:
            hf_hub_download(repo_id=brain.repo, filename=brain.mmproj, local_dir=str(GGUF_DIR))

    print()
    print(f"Done. Talk:  python3 talk_english.py --brain {' | '.join(BRAINS)}")


if __name__ == "__main__":
    main()
