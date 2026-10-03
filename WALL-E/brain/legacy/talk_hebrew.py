#!/usr/bin/env python3
"""Talk to WALL-E in Hebrew. Offline. Microphone in, speaker out.

    python3 legacy/talk_hebrew.py --auto

Camera window: green box is the talker. A locked face plus loud mic
starts a recording (mouth motion on this camera is too weak to wait on).
A face with no sound is ignored. q quits the window.

    python3 legacy/talk_hebrew.py --auto --no-camera
    python3 legacy/talk_hebrew.py --type
    python3 legacy/talk_hebrew.py --auto --thinking --turbo   # reasoning chat + fast STT
"""

from __future__ import annotations


import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # brain/, for the walle package
from walle.paths import BRAIN
from walle.eyes.talk_cam import TalkCam
from walle.mind.llama import LLAMA_PORT, _stale, clean_reply, start_llama
from walle.voice.loud_listen import listen, record_utterance

import argparse
import json
import re
import subprocess
import sys
import threading
import urllib.request
import time
from pathlib import Path

from legacy.hebrew_voice import STT_DIR, STT_TURBO_DIR, Voice
from walle.robot.perception import Person
from walle.robot.speaker_lock import SpeakerLock
from walle.eyes.camera import UsbCamera

MODELS = BRAIN / "models"
CHAT_DIR = MODELS / "chat"
CHAT_REPO = "ssdataanalysis/DictaLM-3.0-1.7B-Instruct-mlx-8Bit"
# Same DictaLM 1.7B as GGUF, for llama.cpp on the XPS's NVIDIA GPU. Q4_K_M is
# ~1.1 GB, so it fits next to Whisper in the 3050 Ti's 4 GB. Q8 does not.
GGUF_DIR = MODELS / "chat-gguf"
GGUF_REPO = "EMD123/DictaLM-3.0-1.7B-Instruct-Q4_K_M-GGUF"
GGUF_FILE = "dictalm-3.0-1.7b-instruct-q4_k_m.gguf"
# The reasoning variant, same size. Its template always opens <think>, so
# every answer costs a thinking pass first; THINK_BUDGET caps it.
THINK_GGUF_REPO = "dicta-il/DictaLM-3.0-1.7B-Thinking-GGUF"
THINK_GGUF_FILE = "DictaLM-3.0-1.7B-Thinking-Q4_K_M.gguf"
THINK_BUDGET = 256  # tokens, ~4 s on the 3050 Ti at ~68 tok/s
FALLBACK = "ווה? לא הבנתי. תגיד שוב?"

SYSTEM = (
    "אתה וול-אי, רובוט קטן וסקרן מפסטיבל במדבר. "
    "מדבר רק עברית מדוברת. משפט אחד או שניים, קצר, חם, פשוט. "
    "בלי רשימות, בלי כוכביות, בלי מנועים, בלי קוד. "
    "אם לא הבנת, תשאל בעדינות."
)


def ensure_chat() -> Path:
    marker = CHAT_DIR / "config.json"
    if marker.exists():
        return CHAT_DIR
    print(f"Chat model: {CHAT_REPO}  (~1.8 GB, first time only)")
    from huggingface_hub import snapshot_download

    CHAT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=CHAT_REPO, local_dir=str(CHAT_DIR))
    return CHAT_DIR


def strip_nikud(text: str) -> str:
    return re.sub(r"[\u0591-\u05c7]", "", text)


def ensure_gguf(thinking: bool = False) -> Path:
    repo, name = (THINK_GGUF_REPO, THINK_GGUF_FILE) if thinking else (GGUF_REPO, GGUF_FILE)
    path = GGUF_DIR / name
    if path.exists():
        return path
    print(f"Chat model: {repo}  (~1.1 GB, first time only)")
    from huggingface_hub import hf_hub_download

    GGUF_DIR.mkdir(parents=True, exist_ok=True)
    hf_hub_download(repo_id=repo, filename=name, local_dir=str(GGUF_DIR))
    return path


def use_mlx() -> bool:
    """Apple Silicon runs MLX. Everything else (the XPS) runs llama.cpp."""
    if sys.platform != "darwin":
        return False
    try:
        import mlx_lm  # noqa: F401
    except ImportError:
        return False
    return True


class Chat:
    """DictaLM 1.7B. MLX on the Mac, llama.cpp on the GPU everywhere else."""

    def __init__(self, thinking: bool = False) -> None:
        self.history: list[dict[str, str]] = []
        self._server: subprocess.Popen | None = None
        self.thinking = thinking
        print("Loading chat…")
        if use_mlx() and thinking:
            sys.exit("--thinking needs llama.cpp (GGUF); there is no MLX build.")
        if use_mlx():
            from mlx_lm import generate, load

            self.model, self.tokenizer = load(str(ensure_chat()))
            self._generate = generate
            self._backend = "mlx"
        else:
            self._start_llama()
            self._backend = "llama.cpp"
        print(f"Chat on {self._backend}")

    def _start_llama(self) -> None:
        extra = ["-ngl", "99"]  # every layer on the GPU
        if self.thinking:
            # Thoughts go to reasoning_content, not the spoken answer.
            extra += ["--reasoning-format", "deepseek", "--reasoning-budget", str(THINK_BUDGET)]
        self._server = start_llama(ensure_gguf(self.thinking), extra)

    def close(self) -> None:
        if self._server is not None and self._server.poll() is None:
            self._server.terminate()
            try:
                self._server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server.kill()
        self._server = None

    def _raw_reply(
        self, messages: list[dict[str, str]], temperature: float = 0.8
    ) -> str:
        if self._backend == "mlx":
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            return self._generate(
                self.model, self.tokenizer, prompt=prompt, max_tokens=80
            )
        # A 1.7B model copies its own last answers out of the history
        # ("אני כאן, מוכן לפעולה" six times running). The penalties push it off
        # words it has already used.
        params = {
            "messages": messages,
            "max_tokens": 80,
            "temperature": temperature,
            "repeat_penalty": 1.3,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5,
        }
        if self.thinking:
            # max_tokens counts the thoughts too. The penalties would punish
            # the answer for words it already used while thinking. Dicta's
            # card suggests 0.6.
            params = {
                "messages": messages,
                "max_tokens": THINK_BUDGET + 120,
                "temperature": 0.6 if temperature <= 0.8 else 0.9,  # retry: hotter
            }
        body = json.dumps(params).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{LLAMA_PORT}/v1/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        t0 = time.monotonic()
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        msg = data["choices"][0]["message"]
        if self.thinking:
            used = data.get("usage", {}).get("completion_tokens", "?")
            thought = msg.get("reasoning_content") or ""
            print(f"(thought {len(thought)} chars, {used} tokens, {time.monotonic() - t0:.1f} s)")
        return msg.get("content") or ""

    def reply(self, user_text: str) -> str:
        self.history.append({"role": "user", "content": user_text})
        messages = [{"role": "system", "content": SYSTEM}, *self.history[-8:]]
        text = clean_reply(self._raw_reply(messages))
        recent = [
            m["content"] for m in self.history[-7:] if m["role"] == "assistant"
        ]
        if self._backend != "mlx" and _stale(text, recent):
            # Same answer as a recent one: one more try, hotter.
            text = clean_reply(self._raw_reply(messages, temperature=1.1))
        if re.search(r"[\u4e00-\u9fff]", text) or not re.search(r"[\u0590-\u05ff]", text):
            text = "ווה? לא הבנתי. תגיד שוב?"
        if not text:
            text = "ווה? לא הבנתי. תגיד שוב?"
        self.history.append({"role": "assistant", "content": text})
        return text


def loop(
    voice: Voice,
    chat: Chat,
    typed: bool,
    auto: bool,
    cam: TalkCam | None,
) -> None:
    voice.speak("שלום. אני וול-אי. דבר אלי.")
    print()
    if cam is not None:
        print("Green SPEAKER = he will listen. Ctrl+C or q to quit.")
    elif auto:
        print("Listening. Speak, then go quiet. Ctrl+C to quit.")
    else:
        print("Enter to talk. Ctrl+C to quit.")
    if typed:
        print("Type a line and press Enter.")
    while True:
        if cam is None and not auto and not typed:
            try:
                input()
            except EOFError:
                return
        if typed:
            user = input("You:    ").strip()
        else:
            if cam is not None:
                rec = listen(cam)
                if rec is False:
                    return
            else:
                rec = record_utterance(cam=None)
            if rec is None:
                print("Heard nothing. Try again.")
                continue
            samples, sr = rec
            user = voice.transcribe_samples(samples, sr)
        if not user:
            print("Heard nothing. Try again.")
            continue
        folded = strip_nikud(user)
        if any(w in folded for w in ("ביי", "להתראות", "יאללה ביי")):
            voice.speak("ביי. נעים היה.")
            return
        answer = chat.reply(user)
        voice.speak(answer)
        if cam is None and not auto:
            print("Enter to talk again.")
        else:
            time.sleep(0.4)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--type", action="store_true", help="Type Hebrew instead of using the mic"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Keep listening after each answer. Implied when the camera is on.",
    )
    parser.add_argument(
        "--no-camera",
        action="store_true",
        help="Mic only. Do not open the USB camera.",
    )
    parser.add_argument(
        "--thinking",
        action="store_true",
        help="DictaLM 1.7B Thinking instead of Instruct (llama.cpp only)",
    )
    parser.add_argument(
        "--turbo",
        action="store_true",
        help="Whisper large-v3-turbo instead of large-v3",
    )
    args = parser.parse_args()
    if args.type and args.auto:
        parser.error("use --type or --auto, not both")
    voice = Voice(STT_TURBO_DIR if args.turbo else STT_DIR)
    chat = Chat(thinking=args.thinking)
    cam: TalkCam | None = None
    if not args.type and not args.no_camera:
        cam = TalkCam()
        if not cam.start():
            cam = None
            print("Camera off. Falling back to mic only.")
            if not args.auto:
                print("Press Enter to talk, or rerun with --auto.")
    auto = args.auto or cam is not None
    try:
        loop(voice, chat, typed=args.type, auto=auto, cam=cam)
    except KeyboardInterrupt:
        print("\nBye.")
    finally:
        chat.close()
        if cam is not None:
            cam.stop()


if __name__ == "__main__":
    main()
