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
# Whisper for the Mac GPU (MLX); faster-whisper is CPU only there.
# Mac default: large-v3-turbo. With speech mixed into kick drum, bass and
# crowd talk it made 0% word errors at 5 dB (small.en 4%) and 10% at 0 dB
# (small.en 12.5%), for 0.22 s a question instead of 0.09 s.
# WALLE_WHISPER=small picks small.en again.
STT_MLX = {
    "turbo": ("large-v3-turbo", MODELS / "whisper-turbo-mlx", "mlx-community/whisper-large-v3-turbo"),
    "small": ("small.en", MODELS / "whisper-en-mlx", "mlx-community/whisper-small.en-mlx"),
}


def stt_mlx() -> tuple[str, Path, str]:
    """(name, folder, repo) of the Mac Whisper to use."""
    import os

    return STT_MLX.get(os.environ.get("WALLE_WHISPER", "turbo"), STT_MLX["turbo"])
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
    whisper: str  # "cuda" or "cpu": who gets the GPU memory (the Mac: always its GPU)
    gpu_layers: str  # llama-server -ngl: how many layers live on the GPU
    note: str
    mmproj: str = ""  # vision projector file: set = the brain can see
    mac_only: bool = False  # too big for the XPS: offered on the Mac only


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
}
# The brains this computer can run: the Mac-only ones are left out elsewhere.
BRAINS = {k: b for k, b in BRAINS.items() if not b.mac_only or sys.platform == "darwin"}


def mlx_ready() -> bool:
    """The Mac with mlx-whisper and its model: Whisper runs on the Mac GPU."""
    if sys.platform != "darwin" or not (stt_mlx()[1] / "config.json").exists():
        return False
    import importlib.util

    return importlib.util.find_spec("mlx_whisper") is not None


def whisper_device(want: str) -> tuple[str, str]:
    """WALLE_WHISPER_DEVICE=cpu forces the CPU, as in hebrew_voice."""
    import os

    if os.environ.get("WALLE_WHISPER_DEVICE") == "cpu":
        return "cpu", "int8"
    if mlx_ready():
        # Memory is shared on the Mac: Whisper never has to give way to the brain.
        return "mlx", "float16"
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
    device, compute = whisper_device(want)
    if device == "mlx":
        _ears_mlx(conn, device, compute)
        return
    from faster_whisper import WhisperModel

    model = WhisperModel(str(STT_DIR), device=device, compute_type=compute)
    conn.send((device, f"small.en, {compute}"))
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


def _ears_mlx(conn, device: str, compute: str) -> None:
    """The same loop on the Mac GPU (mlx-whisper)."""
    import mlx_whisper
    import numpy as np

    name, folder, _repo = stt_mlx()

    def hear(audio) -> str:
        # No vad_filter here: the clip is already cut to speech by Silero
        # (vad_listen) before it gets this far.
        out = mlx_whisper.transcribe(
            audio,
            path_or_hf_repo=str(folder),
            language="en",
            condition_on_previous_text=False,
            verbose=None,
        )
        return " ".join(
            s["text"].strip() for s in out["segments"] if s["no_speech_prob"] < 0.6
        ).strip()

    hear(np.zeros(16000, dtype=np.float32))  # load + compile now, not on the first question
    conn.send((device, f"{name}, {compute}"))
    while (audio := conn.recv()) is not None:
        conn.send(hear(audio))


class EnglishVoice:
    def __init__(self, whisper: str = "cuda") -> None:
        from kokoro_onnx import Kokoro

        if not mlx_ready():
            need(STT_DIR / "model.bin", "Whisper small.en")
        for name in KOKORO_FILES:
            need(KOKORO_DIR / name, "Kokoro")
        print("Loading voice…")
        self.tts = Kokoro(str(KOKORO_DIR / KOKORO_FILES[0]), str(KOKORO_DIR / KOKORO_FILES[1]))
        self._want = whisper
        # Barge-in (talk_english.py): speech goes through echo.Speaker, and
        # setting interrupt stops it mid-sentence.
        self.speaker = None
        self.interrupt = None
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
            print(f"Whisper on {device} ({compute})")

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
        if self.speaker is not None:
            self.speaker.play(samples, sample_rate)
            self.speaker.wait(self.interrupt)
            return
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
        halt = threading.Event()  # interrupted: stop asking the brain

        def render() -> None:
            try:
                for text in sentences:
                    if halt.is_set():
                        break
                    t0 = time.monotonic()
                    samples, sr = self.tts.create(text, voice=KOKORO_VOICE, lang="en-us")
                    print(f"(voice {time.monotonic() - t0:.1f} s for {len(samples) / sr:.1f} s)")
                    ready.put((text, samples, sr))
            except BaseException as exc:  # noqa: BLE001 — re-raised below
                failed.append(exc)
            finally:
                close = getattr(sentences, "close", None)
                if close is not None:
                    close()  # the brain's stream ends here, history kept
                ready.put(None)

        threading.Thread(target=render, daemon=True).start()
        first = True
        while (item := ready.get()) is not None:
            text, samples, sr = item
            if first and t_stop is not None:
                print(f"(answer started {time.monotonic() - t_stop:.1f} s after you stopped)")
            first = False
            if self.interrupt is not None and self.interrupt.is_set():
                halt.set()
                continue  # drain: the render thread ends at the next sentence
            print(f"WALL-E: {text}")
            if self.speaker is not None:
                self.speaker.play(samples, sr)
                if not self.speaker.wait(self.interrupt):
                    print("(interrupted)")
                    halt.set()
                continue
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
