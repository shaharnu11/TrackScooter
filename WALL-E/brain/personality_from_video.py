#!/usr/bin/env python3
"""Prepare a video for a new WALL-E personality: transcript + still frames.

    .venv/bin/python personality_from_video.py VIDEO NAME [--lang he|en]

Writes personalities/<hebrew|english>/NAME/source/ (not in git: it is someone else's work):
    transcript.txt   what is said, with times (Whisper, offline, Mac GPU)
    frames/          a still frame every 2 minutes
    info.json        the video file, length, when
Then that folder's personality.md and examples.md are written from it
(by Claude in a session, or by hand), and WALL-E starts with
--personality NAME.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

from english_voice import stt_mlx
from persona_edit import folder

FRAME_EVERY_S = 120


def audio_16k(video: Path) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32)


def frames(video: Path, out: Path, length_s: float) -> int:
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for t in range(FRAME_EVERY_S // 2, int(length_s), FRAME_EVERY_S):
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(video), "-frames:v", "1",
             "-vf", "scale=640:-2", str(out / f"frame_{t // 60:02d}m{t % 60:02d}s.jpg")],
            check=True,
        )
        n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("name")
    ap.add_argument("--lang", choices=("he", "en"), default="he")
    args = ap.parse_args()
    if not args.video.exists():
        sys.exit(f"No such video: {args.video}")
    src = folder(args.lang) / args.name / "source"
    src.mkdir(parents=True, exist_ok=True)

    import mlx_whisper

    t0 = time.monotonic()
    audio = audio_16k(args.video)
    length = len(audio) / 16000
    print(f"Sound: {length / 60:.1f} min")
    out = mlx_whisper.transcribe(
        audio, path_or_hf_repo=str(stt_mlx(args.lang)[1]), language=args.lang, verbose=None
    )
    lines = [
        f"[{int(s['start']) // 60:02d}:{int(s['start']) % 60:02d}] {s['text'].strip()}"
        for s in out["segments"]
        if s["text"].strip() and s.get("no_speech_prob", 0) < 0.6
    ]
    (src / "transcript.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Transcript: {len(lines)} lines in {time.monotonic() - t0:.0f} s -> {src / 'transcript.txt'}")
    n = frames(args.video, src / "frames", length)
    print(f"Frames: {n} -> {src / 'frames'}")
    (src / "info.json").write_text(
        json.dumps(
            {"video": args.video.name, "minutes": round(length / 60, 1), "lang": args.lang,
             "made": datetime.now().isoformat(timespec="minutes")},
            ensure_ascii=False, indent=1,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
