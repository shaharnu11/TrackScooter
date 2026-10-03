"""Offline STT/TTS for WALL-E: Whisper + Kokoro, English or Hebrew (--lang).

English needs far less than Hebrew: small.en is 0.5 GB and Kokoro runs on the
CPU, so most of the 3050 Ti's 4 GB goes to the language model (BRAINS).

Hebrew (the Mac): ivrit.ai's Whisper large-v3-turbo on MLX, and Kokoro
Hebrew (he_shaul) fed IPA from Phonikud (vowels + stress). Picked on the M4
Max from: Whisper large-v3 vs turbo (turbo 0.24 s a sentence vs 0.43 s, and
3.0% vs 3.8% letter errors at 0 dB), and Kokoro Hebrew vs Chatterbox
Multilingual (0.8% vs 38% letters misheard by Whisper; 0.35 s vs 1.8 s a
sentence). Kokoro Hebrew's license is non-commercial.
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


HE_DIR = MODELS / "he"
STT_MLX_HE = ("ivrit-ai large-v3-turbo", HE_DIR / "whisper-turbo-mlx", "mlx-community/ivrit-ai-whisper-large-v3-turbo-mlx")
KOKORO_HE_DIR = HE_DIR / "tts-kokoro"
KOKORO_HE_REPO = "thewh1teagle/kokoro-hebrew-nc"
KOKORO_HE_VOICE = "he_shaul"
PHONIKUD = HE_DIR / "phonikud" / "phonikud-1.0.int8.onnx"
PHONIKUD_REPO = "thewh1teagle/phonikud-onnx"
# Phonikud fetches this tokenizer from Hugging Face at every start; kept on
# disk instead, so the Hebrew voice starts with no internet.
PHONIKUD_TOK = PHONIKUD.parent / "tokenizer.json"
PHONIKUD_TOK_REPO = "dicta-il/dictabert-large-char-menaked"


def stt_mlx(lang: str = "en") -> tuple[str, Path, str]:
    """(name, folder, repo) of the Mac Whisper to use."""
    import os

    if lang == "he":
        return STT_MLX_HE
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
    # Hebrew Whisper's own (talk_hebrew.py saw "תודה" / "תודה רבה" on noise).
    "תודה",
    "תודה רבה",
    "תודה שצפיתם",
    "תודה על הצפייה",
    "כתוביות",
}


def phantom(text: str) -> bool:
    import re

    words = " ".join(re.findall(r"[a-z'\u05d0-\u05ea]+", text.lower()))
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


def mlx_ready(lang: str = "en") -> bool:
    """The Mac with mlx-whisper and its model: Whisper runs on the Mac GPU."""
    if sys.platform != "darwin" or not (stt_mlx(lang)[1] / "config.json").exists():
        return False
    import importlib.util

    return importlib.util.find_spec("mlx_whisper") is not None


def whisper_device(want: str, lang: str = "en") -> tuple[str, str]:
    """WALLE_WHISPER_DEVICE=cpu forces the CPU, as in hebrew_voice."""
    import os

    if lang == "he":
        return "mlx", "float16"  # Hebrew runs on the Mac only (checked at start)
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


def _ears(conn, want: str, lang: str = "en") -> None:
    """Whisper in its own process, so sleep can end it.

    Deleting the model inside WALL-E's process left a 73 MiB CUDA context,
    and the NVIDIA chip stayed powered (D0) for as long as WALL-E ran; it
    only switched off (D3) once the process holding CUDA was gone.
    """
    device, compute = whisper_device(want, lang)
    if device == "mlx":
        _ears_mlx(conn, device, compute, lang)
        return
    from faster_whisper import WhisperModel

    model = WhisperModel(str(STT_DIR), device=device, compute_type=compute)
    conn.send((device, f"small.en, {compute}"))
    while (msg := conn.recv()) is not None:
        audio = msg[0]
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


def _ears_mlx(conn, device: str, compute: str, lang: str = "en") -> None:
    """The same loop on the Mac GPU (mlx-whisper). A clip can ask for the
    other language: Hebrew mode hears the (English) secret word in English."""
    import mlx_whisper
    import numpy as np

    name = stt_mlx(lang)[0]

    def hear(audio, in_lang: str) -> str:
        # No vad_filter here: the clip is already cut to speech by Silero
        # (vad_listen) before it gets this far.
        out = mlx_whisper.transcribe(
            audio,
            path_or_hf_repo=str(stt_mlx(in_lang)[1]),
            language=in_lang,
            condition_on_previous_text=False,
            verbose=None,
        )
        return " ".join(
            s["text"].strip() for s in out["segments"] if s["no_speech_prob"] < 0.6
        ).strip()

    hear(np.zeros(16000, dtype=np.float32), lang)  # load + compile now, not on the first question
    conn.send((device, f"{name}, {compute}"))
    while (msg := conn.recv()) is not None:
        audio, in_lang = msg
        conn.send(hear(audio, in_lang or lang))


class EnglishVoice:
    def __init__(self, whisper: str = "cuda", lang: str = "en") -> None:
        from kokoro_onnx import Kokoro

        self.lang = lang
        if lang == "he":
            need(stt_mlx("he")[1] / "config.json", "Hebrew Whisper (ivrit-ai, MLX)")
            need(KOKORO_HE_DIR / "kokoro.onnx", "Kokoro Hebrew")
            need(PHONIKUD, "Phonikud")
        elif not mlx_ready():
            need(STT_DIR / "model.bin", "Whisper small.en")
        for name in KOKORO_FILES:
            need(KOKORO_DIR / name, "Kokoro")
        print("Loading voice…")
        if lang == "he":
            import phonikud_onnx.model as pm
            from phonikud_onnx import Phonikud
            from tokenizers import Tokenizer

            need(PHONIKUD_TOK, "Phonikud tokenizer")

            class _LocalTokenizer:  # Phonikud asks the Hub by name; answer from disk
                @staticmethod
                def from_pretrained(_name):
                    return Tokenizer.from_file(str(PHONIKUD_TOK))

            pm.Tokenizer = _LocalTokenizer
            self.tts = Kokoro(
                str(KOKORO_HE_DIR / "kokoro.onnx"),
                str(KOKORO_HE_DIR / "voices-hebrew.bin"),
                vocab_config=str(KOKORO_HE_DIR / "config.json"),
            )
            self._nikud = Phonikud(str(PHONIKUD))
        else:
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
        self._proc = ctx.Process(target=_ears, args=(child, self._want, self.lang), daemon=True)
        self._proc.start()
        self._ready = False

    def wait_ears(self) -> None:
        if not self._ready:
            device, compute = self._conn.recv()
            self._ready = True
            self.ears = f"Whisper {compute} on {device}"
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
        samples, sample_rate = self.render(text)
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
                    samples, sr = self.render(text)
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

    def render(self, text: str):
        """Text to (samples, sample rate) in WALL-E's voice."""
        if self.lang == "he":
            import phonikud

            # Hebrew script has no vowels: Phonikud adds them, then IPA.
            ipa = phonikud.phonemize(self._nikud.add_diacritics(text))
            return self.tts.create(ipa, voice=KOKORO_HE_VOICE, is_phonemes=True)
        return self.tts.create(text, voice=KOKORO_VOICE, lang="en-us")

    def transcribe_samples(self, samples, sample_rate: int, lang: str | None = None) -> str:
        import numpy as np

        audio = np.asarray(samples, dtype=np.float32).reshape(-1)
        if sample_rate != 16000:
            sys.exit("Whisper wants 16 kHz audio.")
        self.wake_ears()
        self.wait_ears()
        self._conn.send((audio, lang))
        text = self._conn.recv()
        print(f"STT  out: {text}")
        if text and phantom(text):
            print("(a Whisper phantom phrase, not speech: ignored)")
            return ""
        return text
