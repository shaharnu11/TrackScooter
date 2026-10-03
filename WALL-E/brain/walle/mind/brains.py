"""The brains WALL-E can run (--brain): GGUF files for llama.cpp, sized for the XPS's 4 GB card and the Mac."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from walle.paths import MODELS


GGUF_DIR = MODELS / "chat-gguf"


@dataclass(frozen=True)
class Brain:
    repo: str
    file: str
    whisper: str  # "cuda" or "cpu": who gets the GPU memory (the Mac: always its GPU)
    gpu_layers: str  # llama-server -ngl: how many layers live on the GPU
    note: str
    mmproj: str = ""  # vision projector file: set = the brain can see
    mac_only: bool = False  # too big for the XPS: offered on the Mac only
    eyes: str = ""  # a BRAINS key: a vision brain that describes the camera in words


BRAINS = {
    # 2.5 GB file, ~3 GB on the card. Whisper fits beside it.
    "4b": Brain(
        "unsloth/Qwen3-4B-Instruct-2507-GGUF",
        "Qwen3-4B-Instruct-2507-Q4_K_M.gguf",
        "cuda", "99",
        "Qwen3-4B Q4_K_M, all on GPU, Whisper on GPU",
    ),
    # Same brain, less rounding. 2.9 GB file: Whisper moves to the CPU.
    "4b-q5": Brain(
        "unsloth/Qwen3-4B-Instruct-2507-GGUF",
        "Qwen3-4B-Instruct-2507-Q5_K_M.gguf",
        "cpu", "99",
        "Qwen3-4B Q5_K_M, all on GPU, Whisper on CPU",
    ),
    # 5 GB file does not fit in 4 GB: 26 of 36 layers on the GPU, the rest on
    # the CPU. Measured on the 3050 Ti: 26 -> 3.6 GB, 16 tok/s. Past ~29,
    # Windows spills into shared memory and it gets slower, not faster.
    # (--fit left 1 GB unused and ran at 11-13 tok/s.)
    "8b": Brain(
        "Qwen/Qwen3-8B-GGUF",
        "Qwen3-8B-Q4_K_M.gguf",
        "cpu", "26",
        "Qwen3-8B Q4_K_M, split GPU/CPU, Whisper on CPU",
    ),
    # Qwen3-VL: the 4B brain plus eyes. It gets the camera frame when asked
    # what it sees. 2.5 GB model + 0.45 GB vision projector. With Whisper on
    # the GPU too it measures 3.9 GB of 4.1: tight, but Whisper on the CPU
    # took 2.5 s per turn (vs 0.5 s) next to the camera and Kokoro.
    "4b-vl": Brain(
        "Qwen/Qwen3-VL-4B-Instruct-GGUF",
        "Qwen3VL-4B-Instruct-Q4_K_M.gguf",
        "cuda", "99",
        "Qwen3-VL-4B Q4_K_M on GPU, vision on CPU, Whisper on GPU",
        mmproj="mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf",
    ),
    # The 8B with eyes, for the Mac: 5 GB model + 0.75 GB vision projector.
    # Too big for the XPS's 4 GB card; the split below is the 8b's, untested.
    "8b-vl": Brain(
        "Qwen/Qwen3-VL-8B-Instruct-GGUF",
        "Qwen3VL-8B-Instruct-Q4_K_M.gguf",
        "cpu", "26",
        "Qwen3-VL-8B Q4_K_M, split GPU/CPU, vision on CPU, Whisper on CPU",
        mmproj="mmproj-Qwen3VL-8B-Instruct-Q8_0.gguf",
    ),
    # The Mac's brain: 30B mixture of experts, ~3B of it works per word, so
    # it answers about as fast as the 4B and knows more. 18.6 GB model +
    # 0.7 GB vision projector: needs the Mac's shared memory (32 GB+).
    "30b-vl": Brain(
        "Qwen/Qwen3-VL-30B-A3B-Instruct-GGUF",
        "Qwen3VL-30B-A3B-Instruct-Q4_K_M.gguf",
        "cuda", "99",
        "Qwen3-VL-30B-A3B Q4_K_M, all on the Mac GPU",
        mmproj="mmproj-Qwen3VL-30B-A3B-Instruct-Q8_0.gguf",
        mac_only=True,
    ),
    # Hebrew (--lang he): Dicta's DictaLM 3.0, Hebrew-first. Against
    # Qwen3-VL-30B on the same Hebrew chat it was natural where Qwen made up
    # words ("אם תסבכי על השמיים"); ~0.8 s an answer at 43 tok/s. It cannot
    # see: Qwen3-VL-4B describes the camera picture in words for it.
    "dicta-12b": Brain(
        "dicta-il/DictaLM-3.0-Nemotron-12B-Instruct-GGUF",
        "DictaLM-3.0-Nemotron-12B-Instruct-Q4_K_M.gguf",
        "cpu", "99",
        "DictaLM 3.0 12B (Hebrew), Qwen3-VL-4B as its eyes, all on the Mac GPU",
        mac_only=True,
        eyes="4b-vl",
    ),
}


# The brains this computer can run: the Mac-only ones are left out elsewhere.
BRAINS = {k: b for k, b in BRAINS.items() if not b.mac_only or sys.platform == "darwin"}
