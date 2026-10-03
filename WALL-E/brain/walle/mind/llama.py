"""llama.cpp's llama-server: start it on a port and wait until it answers; reply clean-up helpers."""

from __future__ import annotations

from pathlib import Path

import re
import subprocess
import sys
import time
import urllib.request

from walle.paths import MODELS


LLAMA_SERVER = MODELS / "llama-cpp" / (
    "llama-server.exe" if sys.platform == "win32" else "llama-server"
)


LLAMA_PORT = 8089


def clean_reply(text: str) -> str:
    t = text.strip()
    for stop in ("<|im_end|>", "<|endoftext|>", "</s>"):
        t = t.split(stop, 1)[0]
    t = t.replace("*", "").replace("#", "").strip()
    t = re.sub(r"(.)\1{5,}", r"\1\1", t)
    parts = re.split(r"(?<=[.!?؟])\s+", t)
    out = " ".join(p.strip() for p in parts[:2] if p.strip())
    return out or t[:160]


def _stale(text: str, recent: list[str]) -> bool:
    """True if text repeats a recent answer, ignoring the first word
    (he echoes the greeting: "הלו! אני כאן..." / "בשמחה! אני כאן...")."""
    def tail(s: str) -> str:
        parts = s.split(None, 1)
        return parts[1] if len(parts) > 1 else s

    return any(tail(text) == tail(r) for r in recent)


def start_llama(model: Path, extra: list[str], port: int = LLAMA_PORT) -> subprocess.Popen:
    """Start llama-server on port and wait until /health answers."""
    if not LLAMA_SERVER.exists():
        sys.exit(f"Missing {LLAMA_SERVER}\nRun: python scripts/download_hebrew_windows.py")
    log_path = MODELS / ("llama-server.log" if port == LLAMA_PORT else f"llama-server-{port}.log")
    log = open(log_path, "w", encoding="utf-8")
    server = subprocess.Popen(
        [
            str(LLAMA_SERVER),
            "-m", str(model),
            "--host", "127.0.0.1",
            "--port", str(port),
            "-c", "2048",
            "--jinja",  # the chat template inside the GGUF
            *extra,
        ],
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if server.poll() is not None:
            sys.exit(f"llama-server exited. See {log_path}")
        try:
            url = f"http://127.0.0.1:{port}/health"
            with urllib.request.urlopen(url, timeout=1) as r:
                if r.status == 200:
                    return server
        except OSError:
            pass
        time.sleep(0.3)
    server.kill()
    sys.exit("llama-server did not come up in 90 s.")
