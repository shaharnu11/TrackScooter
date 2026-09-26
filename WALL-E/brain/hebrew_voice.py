"""Shared offline Hebrew STT/TTS: ivrit Whisper v3 + BlueTTS."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
STT_DIR = MODELS / "whisper-he"
# ivrit-ai large-v3-turbo: same encoder, 4 decoder layers. 1.6 GB, not 3.1.
STT_TURBO_DIR = MODELS / "whisper-he-turbo"
BLUE_DIR = MODELS / "tts-blue"
VOICE_JSON = BLUE_DIR / "voices" / "libri_male_6209.json"
OUT_WAV = ROOT / "hebrew_try.wav"
TALK_WAV = ROOT / "hebrew_talk.wav"


def need(path: Path, what: str) -> None:
    if not path.exists():
        sys.exit(f"Missing {what}: {path}\nRun: python3 download_hebrew_voice.py")


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


def whisper_device() -> tuple[str, str]:
    """CUDA when there is an NVIDIA GPU (the XPS), else CPU int8 (the Mac).

    WALLE_WHISPER_DEVICE=cpu forces the CPU, e.g. if the GPU is full.
    """
    import os

    forced = os.environ.get("WALLE_WHISPER_DEVICE")
    if forced == "cpu":
        return "cpu", "int8"
    _add_cuda_dlls()
    try:
        import ctranslate2

        if ctranslate2.get_cuda_device_count() > 0:
            # int8 weights, fp16 maths: ~1.6 GB of the 3050 Ti's 4 GB.
            return "cuda", "int8_float16"
    except Exception as exc:  # noqa: BLE001 — any CUDA trouble means CPU
        print(f"CUDA check failed ({exc}); Whisper on CPU.")
    return "cpu", "int8"


def _patch_renikud_phonemize() -> None:
    """BlueTTS 2.5 passes speaker=; current renikud-plus G2P only takes text.

    renikud-plus 0.5 also fetches an optional datastore.json that the
    RenikudPlus model repo does not have. The 404 is fatal there; skip it
    instead, which is what the library does when the file is absent.
    """
    import renikud_onnx
    from renikud_onnx import G2P

    if not getattr(renikud_onnx.download_model, "_walle_patched", False):
        orig_download = renikud_onnx.download_model

        def download_model(*args, filename=None, **kwargs):
            if filename != renikud_onnx.DEFAULT_DATASTORE_NAME:
                return orig_download(*args, filename=filename, **kwargs)
            try:
                return orig_download(*args, filename=filename, **kwargs)
            except Exception:  # noqa: BLE001 — optional rescorer, run without it
                return ""

        download_model._walle_patched = True  # type: ignore[attr-defined]
        renikud_onnx.download_model = download_model

    if getattr(G2P.phonemize, "_walle_patched", False):
        return
    orig = G2P.phonemize

    def phonemize(self, text, speaker=None, target_speaker=None, **kwargs):
        return orig(self, text)

    phonemize._walle_patched = True  # type: ignore[attr-defined]
    G2P.phonemize = phonemize  # type: ignore[method-assign]


def _patch_blue_utf8() -> None:
    """BlueTTS opens its JSON with the default encoding: UTF-8 on the Mac,
    cp1252 on Windows, which cannot read the Hebrew in it."""
    import builtins

    import blue_onnx

    if getattr(blue_onnx, "_walle_utf8", False):
        return

    def utf8_open(file, mode="r", *args, **kwargs):
        if "b" not in mode:
            kwargs.setdefault("encoding", "utf-8")
        return builtins.open(file, mode, *args, **kwargs)

    blue_onnx.open = utf8_open  # module global shadows the builtin
    blue_onnx._walle_utf8 = True


class Voice:
    def __init__(self, stt_dir: Path = STT_DIR) -> None:
        from blue_onnx import BlueTTS
        from faster_whisper import WhisperModel

        _patch_renikud_phonemize()
        _patch_blue_utf8()

        tts_json = BLUE_DIR / "tts.json"
        if not tts_json.exists():
            found = list(BLUE_DIR.rglob("tts.json"))
            if found:
                tts_json = found[0]
        need(tts_json, "BlueTTS")
        need(VOICE_JSON, "BlueTTS voice")
        need(stt_dir / "model.bin", "Whisper")

        print("Loading voice…")
        self.tts = BlueTTS(onnx_dir=str(tts_json.parent), style_json=str(VOICE_JSON))
        device, compute = whisper_device()
        print(f"Whisper {stt_dir.name} on {device} ({compute})")
        self.whisper = WhisperModel(str(stt_dir), device=device, compute_type=compute)

    def speak(self, text: str, wav_path: Path | None = None) -> Path:
        import soundfile as sf

        dest = wav_path or TALK_WAV
        print(f"\nWALL-E: {text}")
        samples, sample_rate = self.tts.synthesize(text, lang="he")
        sf.write(str(dest), samples, sample_rate)
        print(f"TTS  wav: {dest}  ({sample_rate} Hz)")
        play(dest)
        return dest

    def transcribe(self, wav_path: Path) -> str:
        print(f"STT  wav: {wav_path}")
        # Whisper invents words on silence and noise (on Hebrew, mostly
        # "תודה" / "תודה רבה"). The VAD cuts non-speech out before Whisper
        # sees it, and segments Whisper itself rates as probably-not-speech
        # are dropped. Silence then comes back as "", i.e. "Heard nothing".
        segments, info = self.whisper.transcribe(
            str(wav_path),
            language="he",
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            condition_on_previous_text=False,
        )
        kept = [s for s in segments if s.no_speech_prob < 0.6]
        text = " ".join(s.text.strip() for s in kept).strip()
        print(f"STT  language: {info.language}  p={info.language_probability:.2f}")
        print(f"STT  out: {text}")
        return text

    def transcribe_samples(self, samples, sample_rate: int) -> str:
        import numpy as np
        import soundfile as sf

        audio = np.asarray(samples, dtype=np.float32).reshape(-1)
        sf.write(str(TALK_WAV), audio, sample_rate)
        return self.transcribe(TALK_WAV)
