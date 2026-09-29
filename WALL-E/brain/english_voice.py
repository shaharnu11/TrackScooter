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

# Whisper learned from YouTube audio and fills noise with the lines that end
# videos: a live session got "Like and subscribe!" from nobody. Only a whole
# result that IS one of these is dropped; a real sentence that contains the
# words ("thanks for watching my stuff") passes.
PHANTOMS = {
    "like and subscribe",
    "please subscribe",
    "subscribe to my channel",
    "thanks for watching",
    "thank you for watching",
    "thanks for watching please subscribe",
    "see you in the next video",
    "see you next time",
    "thank you",  # a real lone "thank you" is lost too; it needs no answer
    "you",
}


def phantom(text: str) -> bool:
    import re

    words = " ".join(re.findall(r"[a-z']+", text.lower()))
    return words in PHANTOMS


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
        "Qwen3-VL-4B Q4_K_M on GPU, vision on CPU, Whisper on GPU",
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


def chirp() -> None:
    """A short two-note robot chirp, the instant a question is heard.

    Whisper and the brain still take ~1.5 s; the chirp says "got it" at once,
    so the wait feels like thinking, not like not hearing. Does not block.
    """
    import numpy as np
    import sounddevice as sd

    sr = 24000

    def sweep(f0: float, f1: float, dur: float):
        t = np.linspace(0, dur, int(sr * dur), False)
        phase = 2 * np.pi * np.cumsum(np.linspace(f0, f1, t.size)) / sr
        return 0.15 * np.sin(np.pi * t / dur) * np.sin(phase)  # soft in and out

    gap = np.zeros(int(sr * 0.03))
    sd.play(np.concatenate([sweep(900, 1500, 0.07), gap, sweep(1200, 2100, 0.09)]).astype(np.float32), sr)


def wake_sound() -> None:
    """Three rising notes: "booting up". Does not block."""
    import numpy as np
    import sounddevice as sd

    sr = 24000
    notes = []
    for f in (600, 900, 1350):
        t = np.linspace(0, 0.09, int(sr * 0.09), False)
        notes += [0.13 * np.sin(np.pi * t / 0.09) * np.sin(2 * np.pi * f * t), np.zeros(int(sr * 0.03))]
    sd.play(np.concatenate(notes).astype(np.float32), sr)


def _ears(conn, want: str) -> None:
    """Whisper in its own process, so sleep can end it.

    Deleting the model inside WALL-E's process left a 73 MiB CUDA context,
    and the NVIDIA chip stayed powered (D0) for as long as WALL-E ran; it
    only switched off (D3) once the process holding CUDA was gone.
    """
    from faster_whisper import WhisperModel

    device, compute = whisper_device(want)
    model = WhisperModel(str(STT_DIR), device=device, compute_type=compute)
    conn.send((device, compute))
    while (audio := conn.recv()) is not None:
        # VAD drops silence, and segments Whisper rates as not-speech are
        # thrown away ("Thank you." on noise), as on the Hebrew side.
        segments, _info = model.transcribe(
            audio,
            language="en",
            beam_size=1,  # one guess, not five: ~0.1-0.2 s faster on short questions
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            condition_on_previous_text=False,
        )
        conn.send(" ".join(s.text.strip() for s in segments if s.no_speech_prob < 0.6).strip())


class EnglishVoice:
    def __init__(self, whisper: str = "cuda") -> None:
        from kokoro_onnx import Kokoro

        need(STT_DIR / "model.bin", "Whisper small.en")
        for name in KOKORO_FILES:
            need(KOKORO_DIR / name, "Kokoro")
        print("Loading voice…")
        self.tts = Kokoro(str(KOKORO_DIR / KOKORO_FILES[0]), str(KOKORO_DIR / KOKORO_FILES[1]))
        self._want = whisper
        self._proc = None
        self._conn = None
        self.wake_ears()
        self.wait_ears()

    def wake_ears(self) -> None:
        """Start the Whisper process (returns at once; wait_ears() waits)."""
        if self._proc is not None and self._proc.is_alive():
            return
        import multiprocessing as mp

        ctx = mp.get_context("spawn")
        self._conn, child = ctx.Pipe()
        self._proc = ctx.Process(target=_ears, args=(child, self._want), daemon=True)
        self._proc.start()
        self._ready = False

    def wait_ears(self) -> None:
        if not self._ready:
            device, compute = self._conn.recv()
            self._ready = True
            print(f"Whisper small.en on {device} ({compute})")

    def sleep_ears(self) -> None:
        """End the Whisper process: no CUDA left, the chip can power off."""
        if self._proc is None:
            return
        try:
            self._conn.send(None)
        except OSError:
            pass
        self._proc.join(timeout=5)
        if self._proc.is_alive():
            self._proc.terminate()
        self._proc = self._conn = None
        self._ready = False

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

    def speak_stream(self, sentences, t_stop: float | None = None) -> None:
        """Speak sentences as they arrive from the brain.

        speak() rendered the whole reply first: 1.5-2.3 s of silence for a
        two-sentence answer. Here a thread renders sentence n+1 while
        sentence n plays, so the wait is the first sentence only.
        t_stop: when the person stopped talking, for the response-time log.
        """
        import queue
        import threading

        import sounddevice as sd

        ready: queue.Queue = queue.Queue()
        failed: list[BaseException] = []

        def render() -> None:
            try:
                for text in sentences:
                    t0 = time.monotonic()
                    samples, sr = self.tts.create(text, voice=KOKORO_VOICE, lang="en-us")
                    print(f"(voice {time.monotonic() - t0:.1f} s for {len(samples) / sr:.1f} s)")
                    ready.put((text, samples, sr))
            except BaseException as exc:  # noqa: BLE001 — re-raised below
                failed.append(exc)
            finally:
                ready.put(None)

        threading.Thread(target=render, daemon=True).start()
        first = True
        while (item := ready.get()) is not None:
            text, samples, sr = item
            if first and t_stop is not None:
                print(f"(answer started {time.monotonic() - t_stop:.1f} s after you stopped)")
            first = False
            print(f"WALL-E: {text}")
            sd.play(samples, sr)
            sd.wait()
        if failed:
            raise failed[0]

    def transcribe_samples(self, samples, sample_rate: int) -> str:
        import numpy as np

        audio = np.asarray(samples, dtype=np.float32).reshape(-1)
        if sample_rate != 16000:
            sys.exit("Whisper wants 16 kHz audio.")
        self.wake_ears()
        self.wait_ears()
        self._conn.send(audio)
        text = self._conn.recv()
        print(f"STT  out: {text}")
        if text and phantom(text):
            print("(a Whisper phantom phrase, not speech: ignored)")
            return ""
        return text
