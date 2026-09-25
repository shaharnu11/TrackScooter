#!/usr/bin/env python3
"""Try offline Hebrew speech: text to speech, then speech back to text.

    python3 try_hebrew_voice.py
    python3 try_hebrew_voice.py --text "שלום, איך קוראים לך?"
    python3 try_hebrew_voice.py --wav some.wav
"""

from __future__ import annotations

import argparse
from pathlib import Path

from hebrew_voice import OUT_WAV, Voice


HELLO = "שלום. אני וול-אי. נעים להכיר."


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", default=HELLO, help="Hebrew text to speak")
    parser.add_argument("--wav", type=Path, help="Transcribe this wav instead of speaking first")
    parser.add_argument("--tts-only", action="store_true", help="Speak, do not transcribe")
    args = parser.parse_args()

    voice = Voice()
    wav = args.wav
    if wav is None:
        print(f"TTS  in:  {args.text}")
        wav = voice.speak(args.text, OUT_WAV)
        if args.tts_only:
            return
    voice.transcribe(wav)


if __name__ == "__main__":
    main()
