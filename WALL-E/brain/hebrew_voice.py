"""Shared offline Hebrew STT/TTS: ivrit Whisper v3 + BlueTTS."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
STT_DIR = MODELS / "whisper-he"
BLUE_DIR = MODELS / "tts-blue"
VOICE_JSON = BLUE_DIR / "voices" / "libri_male_6209.json"
OUT_WAV = ROOT / "hebrew_try.wav"
TALK_WAV = ROOT / "hebrew_talk.wav"


def need(path: Path, what: str) -> None:
    if not path.exists():
        sys.exit(f"Missing {what}: {path}\nRun: python3 download_hebrew_voice.py")


def play(wav_path: Path) -> None:
    player = shutil.which("afplay")
    if player is None:
        print(f"Saved {wav_path}")
        return
    subprocess.run([player, str(wav_path)], check=False)


def _patch_renikud_phonemize() -> None:
    """BlueTTS 2.5 passes speaker=; current renikud-plus G2P only takes text."""
    from renikud_onnx import G2P

    if getattr(G2P.phonemize, "_walle_patched", False):
        return
    orig = G2P.phonemize

    def phonemize(self, text, speaker=None, target_speaker=None, **kwargs):
        return orig(self, text)

    phonemize._walle_patched = True  # type: ignore[attr-defined]
    G2P.phonemize = phonemize  # type: ignore[method-assign]


class Voice:
    def __init__(self) -> None:
        from blue_onnx import BlueTTS
        from faster_whisper import WhisperModel

        _patch_renikud_phonemize()

        tts_json = BLUE_DIR / "tts.json"
        if not tts_json.exists():
            found = list(BLUE_DIR.rglob("tts.json"))
            if found:
                tts_json = found[0]
        need(tts_json, "BlueTTS")
        need(VOICE_JSON, "BlueTTS voice")
        need(STT_DIR / "model.bin", "Whisper")

        print("Loading voice…")
        self.tts = BlueTTS(onnx_dir=str(tts_json.parent), style_json=str(VOICE_JSON))
        self.whisper = WhisperModel(str(STT_DIR), device="cpu", compute_type="int8")

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
        segments, info = self.whisper.transcribe(str(wav_path), language="he")
        text = " ".join(s.text.strip() for s in segments).strip()
        print(f"STT  language: {info.language}  p={info.language_probability:.2f}")
        print(f"STT  out: {text}")
        return text

    def transcribe_samples(self, samples, sample_rate: int) -> str:
        import numpy as np
        import soundfile as sf

        audio = np.asarray(samples, dtype=np.float32).reshape(-1)
        sf.write(str(TALK_WAV), audio, sample_rate)
        return self.transcribe(TALK_WAV)
