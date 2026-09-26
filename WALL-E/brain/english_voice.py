"""Offline English STT/TTS for WALL-E: Whisper small.en + Kokoro.

English needs far less than Hebrew: small.en is 0.5 GB and Kokoro runs on the
CPU, so most of the 3050 Ti's 4 GB goes to the language model (BRAINS).
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

from hebrew_voice import _add_cuda_dlls, need, play

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
STT_DIR = MODELS / "whisper-en"
STT_REPO = "Systran/faster-whisper-small.en"
KOKORO_DIR = MODELS / "tts-kokoro"
KOKORO_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
KOKORO_FILES = ("kokoro-v1.0.onnx", "voices-v1.0.bin")
KOKORO_VOICE = "am_michael"
GGUF_DIR = MODELS / "chat-gguf"
TALK_WAV = ROOT / "english_talk.wav"


@dataclass(frozen=True)
class Brain:
    repo: str
    file: str
    whisper: str  # "cuda" or "cpu": who gets the GPU memory
    gpu_layers: str  # llama-server -ngl: how many layers live on the GPU
    note: str
    mmproj: str = ""  # vision projector file: set = the brain can see


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
        "Qwen3-VL-4B Q4_K_M + vision, all on GPU, Whisper on GPU",
        mmproj="mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf",
    ),
}


def whisper_device(want: str) -> tuple[str, str]:
    if want == "cuda":
        _add_cuda_dlls()
        try:
            import ctranslate2

            if ctranslate2.get_cuda_device_count() > 0:
                return "cuda", "int8_float16"
        except Exception as exc:  # noqa: BLE001 — any CUDA trouble means CPU
            print(f"CUDA check failed ({exc}); Whisper on CPU.")
    return "cpu", "int8"


class EnglishVoice:
    def __init__(self, whisper: str = "cuda") -> None:
        from faster_whisper import WhisperModel
        from kokoro_onnx import Kokoro

        need(STT_DIR / "model.bin", "Whisper small.en")
        for name in KOKORO_FILES:
            need(KOKORO_DIR / name, "Kokoro")
        print("Loading voice…")
        self.tts = Kokoro(str(KOKORO_DIR / KOKORO_FILES[0]), str(KOKORO_DIR / KOKORO_FILES[1]))
        device, compute = whisper_device(whisper)
        print(f"Whisper small.en on {device} ({compute})")
        self.whisper = WhisperModel(str(STT_DIR), device=device, compute_type=compute)

    def speak(self, text: str) -> None:
        import soundfile as sf

        print(f"\nWALL-E: {text}")
        t0 = time.monotonic()
        samples, sample_rate = self.tts.create(text, voice=KOKORO_VOICE, lang="en-us")
        # Kokoro renders the whole reply before a sound comes out: this is
        # the wait between the brain answering and WALL-E speaking.
        print(f"(voice {time.monotonic() - t0:.1f} s for {len(samples) / sample_rate:.1f} s of speech)")
        sf.write(str(TALK_WAV), samples, sample_rate)
        play(TALK_WAV)

    def transcribe_samples(self, samples, sample_rate: int) -> str:
        import numpy as np

        audio = np.asarray(samples, dtype=np.float32).reshape(-1)
        if sample_rate != 16000:
            sys.exit("Whisper wants 16 kHz audio.")
        # Same guards as the Hebrew side: VAD drops silence, and segments
        # Whisper rates as not-speech are thrown away ("Thank you." on noise).
        segments, _info = self.whisper.transcribe(
            audio,
            language="en",
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            condition_on_previous_text=False,
        )
        text = " ".join(s.text.strip() for s in segments if s.no_speech_prob < 0.6).strip()
        print(f"STT  out: {text}")
        return text
