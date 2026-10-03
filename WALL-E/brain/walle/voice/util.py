"""Small audio helpers shared by the voices: a missing-model message, playing a wav, CUDA DLLs on Windows."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def need(path: Path, what: str) -> None:
    if not path.exists():
        sys.exit(
            f"Missing {what}: {path}\n"
            "Run: python3 scripts/download_models.py (English) or scripts/download_hebrew_windows.py (Hebrew)"
        )


def play(wav_path: Path) -> None:
    player = shutil.which("afplay")
    if player is not None:
        subprocess.run([player, str(wav_path)], check=False)
        return
    # Windows / Linux: no afplay. Play through sounddevice, blocking.
    import sounddevice as sd
    import soundfile as sf

    data, sr = sf.read(str(wav_path), dtype="float32")
    sd.play(data, sr)
    sd.wait()


def _add_cuda_dlls() -> None:
    """Windows: let CTranslate2 find cuBLAS / cuDNN from the nvidia-* pip wheels."""
    if sys.platform != "win32":
        return
    import os

    for pkg in ("nvidia.cublas", "nvidia.cudnn"):
        try:
            mod = __import__(pkg, fromlist=["__path__"])
        except ImportError:
            continue
        for base in mod.__path__:
            bin_dir = Path(base) / "bin"
            if bin_dir.is_dir():
                os.add_dll_directory(str(bin_dir))
                os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ["PATH"]
