#!/usr/bin/env python3
"""Download the offline English STT, TTS, and chat models into ./models.

    python3 download_english.py              # all three brains
    python3 download_english.py --brain 4b   # just one

llama.cpp itself: Windows gets it from download_hebrew_voice.py, the Mac
from Homebrew (mac/README.md).
"""

from __future__ import annotations

import argparse
import sys
import urllib.request

from huggingface_hub import hf_hub_download, snapshot_download

from english_voice import (
    BRAINS,
    GGUF_DIR,
    KOKORO_DIR,
    KOKORO_FILES,
    KOKORO_URL,
    STT_DIR,
    STT_MLX,
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

    if sys.platform == "darwin":
        # Whisper for the Mac GPU: turbo (1.6 GB) and small.en (0.5 GB).
        # The one above stays as the CPU fallback.
        for name, folder, repo in STT_MLX.values():
            if not (folder / "config.json").exists():
                print(f"STT (Mac GPU): {repo}")
                snapshot_download(repo_id=repo, local_dir=str(folder))
            else:
                print(f"STT (Mac GPU) {name} already at {folder}")

    if sys.platform == "darwin":
        # Hebrew (--lang he): ivrit.ai Whisper (MLX), Kokoro Hebrew, Phonikud
        # and its tokenizer (else it fetches it at every start).
        from english_voice import (
            KOKORO_HE_DIR,
            KOKORO_HE_REPO,
            PHONIKUD,
            PHONIKUD_REPO,
            PHONIKUD_TOK,
            PHONIKUD_TOK_REPO,
            STT_MLX_HE,
        )

        name, folder, repo = STT_MLX_HE
        if not (folder / "config.json").exists():
            print(f"STT Hebrew (Mac GPU): {repo}  (~1.6 GB)")
            snapshot_download(repo_id=repo, local_dir=str(folder))
        if not (KOKORO_HE_DIR / "kokoro.onnx").exists():
            print(f"TTS Hebrew: {KOKORO_HE_REPO}  (~0.3 GB)")
            snapshot_download(repo_id=KOKORO_HE_REPO, local_dir=str(KOKORO_HE_DIR))
        if not PHONIKUD.exists():
            print(f"Hebrew vowels: {PHONIKUD_REPO}  (~0.3 GB)")
            hf_hub_download(PHONIKUD_REPO, PHONIKUD.name, local_dir=str(PHONIKUD.parent))
        if not PHONIKUD_TOK.exists():
            hf_hub_download(PHONIKUD_TOK_REPO, PHONIKUD_TOK.name, local_dir=str(PHONIKUD_TOK.parent))

    # The face models download on first use. Fetch them now: no internet later.
    from owner import SFACE_PATH, SFACE_URL
    from usb_camera import _ensure_yunet

    _ensure_yunet()
    from usb_camera import LIPS_MODEL, LIPS_TASK_URL

    if not LIPS_MODEL.exists():
        import zipfile

        print("Camera: lip landmark model (~4 MB)")
        task = LIPS_MODEL.with_suffix(".task.part")
        urllib.request.urlretrieve(LIPS_TASK_URL, task)
        with zipfile.ZipFile(task) as z:  # the .task file is a zip
            LIPS_MODEL.write_bytes(z.read(LIPS_MODEL.name))
        task.unlink()
    if not SFACE_PATH.exists():
        print("Camera: owner face model")
        SFACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = SFACE_PATH.with_suffix(".part")
        urllib.request.urlretrieve(SFACE_URL, tmp)
        tmp.rename(SFACE_PATH)

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
        if brain.eyes:  # a brain that cannot see gets a vision brain as its eyes
            eyes = BRAINS[brain.eyes]
            print(f"  its eyes {brain.eyes}: {eyes.repo} / {eyes.file}")
            hf_hub_download(repo_id=eyes.repo, filename=eyes.file, local_dir=str(GGUF_DIR))
            hf_hub_download(repo_id=eyes.repo, filename=eyes.mmproj, local_dir=str(GGUF_DIR))

    print()
    print(f"Done. Talk:  python3 talk_english.py --brain {' | '.join(BRAINS)}")


if __name__ == "__main__":
    main()
