#!/usr/bin/env python3
"""Talk to WALL-E in English. Offline. Microphone in, speaker out.

    python3 talk_english.py --brain 4b      # Qwen3-4B Q4, fast
    python3 talk_english.py --brain 4b-q5   # Qwen3-4B Q5, a bit sharper
    python3 talk_english.py --brain 8b      # Qwen3-8B, smarter, slower
    python3 talk_english.py --brain 4b-vl   # Qwen3-VL-4B: sees the camera

Same camera and mic handling as talk_hebrew.py. q quits the window.

    python3 talk_english.py --brain 4b --no-camera --auto
    python3 talk_english.py --brain 4b --type
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import time
import urllib.request

from english_voice import BRAINS, GGUF_DIR, Brain, EnglishVoice
from talk_hebrew import (
    LLAMA_PORT,
    TalkCam,
    _stale,
    clean_reply,
    listen,
    record_utterance,
    start_llama,
)
from vad_listen import BLOCK, StreamVAD, listen_vad

FALLBACK = "Sorry, I missed that. Say it again?"
MIN_CLIP_SPEECH = 0.5

_PERSONA = (
    "You are WALL-E, a small, curious robot at a desert festival. "
    "Speak plain spoken English: one or two short, warm, simple sentences, "
    "under 25 words. No lists, no asterisks, no emojis, no code. "
    # Whisper hears through festival music: half-heard lines will come in.
    # Worded softly: "it is loud around you" made him answer a clear
    # "what's up?" with "you're making noise, can you repeat that?".
    "Answer what people say. Only if a sentence is clearly cut off or makes "
    "no sense, ask them to say it again. "
)

SYSTEM = _PERSONA + (
    "Your camera only tells you that a person is in front of you. You cannot "
    "see objects, colours, weather or scenery, so never describe them, not "
    "even the place around you."
)

# The vision brain: a picture comes with questions about seeing. At home it
# added a dog and glasses that were not there, and sand dunes to a living
# room; asked yes/no, it said no to both. So: only what is clear, admit doubt.
SYSTEM_VL = _PERSONA + (
    "When a picture is attached, it is what your camera eye sees right now, "
    "and the person talking to you is in it. Describe only what is clearly in "
    "the picture. If you are not sure about something, say so; never guess "
    "small things like glasses, animals or writing. With no picture, never "
    "say you see anything, and do not describe the person or the place "
    "around you."
)

# Questions that need the eye. Everything else stays text-only and fast.
LOOK = re.compile(
    r"\b(see|seeing|look|looks|looking|watch|camera|picture|image|photo|"
    r"wear|wearing|holding|behind|colou?r|room|glasses|shirt|hair|"
    r"what is this|what's this|how many|"
    # Surroundings: without the picture he invented "grass and trees".
    r"where (are you|are we|you are|we are)|around (you|us|me|here)|"
    r"this place|surround\w*)\b",
    re.IGNORECASE,
)

EMOJI = re.compile(r"[\U0001f000-\U0001faff\U00002600-\U000027bf\U0000fe0f]")
# Qwen slips into Chinese now and then ("Five十六"). Kokoro cannot say it.
CJK = re.compile(r"[\U00003000-\U00009fff\U0000ac00-\U0000d7af\U0000ff00-\U0000ffef]")


def gpu_mem() -> str:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        return out or "?"
    except OSError:
        return "no nvidia-smi"


class EnglishChat:
    """A Qwen3 GGUF in llama-server. Thinking off: WALL-E answers at once."""

    def __init__(self, brain: Brain) -> None:
        self.history: list[dict[str, str]] = []
        model = GGUF_DIR / brain.file
        if not model.exists():
            sys.exit(f"Missing {model}\nRun: python download_english.py")
        print(f"Loading chat: {brain.note}")
        extra = [
            "-ngl", brain.gpu_layers,
            "--reasoning", "off",
            "--reasoning-format", "deepseek",
            # One talker, so one slot; 8-bit KV cache and a smaller batch.
            # Together ~150 MiB less on the 4 GB card, same answers.
            "-np", "1",
            "-fa", "on",
            "-ctk", "q8_0",
            "-ctv", "q8_0",
            "-ub", "256",
        ]
        self.vision = bool(brain.mmproj)
        self.system = SYSTEM_VL if self.vision else SYSTEM
        if self.vision:
            # 384 image tokens: saw "a white earbud in their right ear" where
            # 256 saw "earbuds"; no more memory once the KV cache is 8-bit.
            extra += ["--mmproj", str(GGUF_DIR / brain.mmproj), "--image-max-tokens", "384"]
        self._server: subprocess.Popen | None = start_llama(model, extra)

    def close(self) -> None:
        if self._server is not None and self._server.poll() is None:
            self._server.terminate()
            try:
                self._server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server.kill()
        self._server = None

    def _raw_reply(self, messages: list[dict], temperature: float) -> str:
        body = json.dumps(
            {
                "messages": messages,
                "max_tokens": 100,
                "temperature": temperature,
                "repeat_penalty": 1.1,
                "chat_template_kwargs": {"enable_thinking": False},
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{LLAMA_PORT}/v1/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        t0 = time.monotonic()
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.load(r)
        tps = data.get("timings", {}).get("predicted_per_second", 0.0)
        used = data.get("usage", {}).get("completion_tokens", "?")
        print(f"(chat {time.monotonic() - t0:.1f} s, {used} tokens, {tps:.0f} tok/s)")
        return data["choices"][0]["message"].get("content") or ""

    def reply(self, user_text: str, jpeg: bytes | None = None) -> str:
        self.history.append({"role": "user", "content": user_text})
        messages: list[dict] = [{"role": "system", "content": self.system}, *self.history[-8:]]
        if jpeg is not None:
            # The picture rides on this turn only; history keeps the words.
            url = "data:image/jpeg;base64," + base64.b64encode(jpeg).decode("ascii")
            messages[-1] = {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": url}},
                    {"type": "text", "text": user_text},
                ],
            }
        text = EMOJI.sub("", clean_reply(self._raw_reply(messages, 0.7))).strip()
        recent = [m["content"] for m in self.history[-7:] if m["role"] == "assistant"]
        if _stale(text, recent):
            text = EMOJI.sub("", clean_reply(self._raw_reply(messages, 1.0))).strip()
        if CJK.search(text):
            # One cooler retry; if it is still not English, ask again.
            text = EMOJI.sub("", clean_reply(self._raw_reply(messages, 0.3))).strip()
            if CJK.search(text):
                text = FALLBACK
        text = text or FALLBACK
        self.history.append({"role": "assistant", "content": text})
        return text


def look(cam: TalkCam | None) -> bytes | None:
    """The current camera frame as a 640-wide JPEG, for the vision brain."""
    if cam is None:
        return None
    frame = cam.snapshot()
    if frame is None:
        return None
    import cv2

    h, w = frame.shape[:2]
    if w > 640:
        frame = cv2.resize(frame, (640, int(h * 640 / w)))
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        return None
    print("(looking through the camera)")
    return buf.tobytes()


def loop(
    voice: EnglishVoice,
    chat: EnglishChat,
    typed: bool,
    auto: bool,
    cam: TalkCam | None,
    trigger: str = "speech",
) -> None:
    voice.speak("Hi. I'm WALL-E. Talk to me.")
    print()
    if cam is not None:
        print("Green SPEAKER = he will listen. Ctrl+C or q to quit.")
    elif auto:
        print("Listening. Speak, then go quiet. Ctrl+C to quit.")
    else:
        print("Enter to talk. Ctrl+C to quit.")
    vad = None if typed else StreamVAD()
    print(f"Listening trigger: {trigger}")
    while True:
        if cam is None and not auto and not typed:
            try:
                input()
            except EOFError:
                return
        if typed:
            user = input("You:    ").strip()
        else:
            if trigger == "speech":
                # Speech-triggered, not loudness-triggered: music and fans pass.
                rec = listen_vad(cam, vad)
            elif cam is not None:
                rec = listen(cam)  # the old loudness / mouth-motion trigger
            else:
                rec = record_utterance(cam=None)
            if rec is False:
                return
            if rec is None:
                print("(too little speech, ignored)")
                continue
            samples, sr = rec
            # Silero's verdict on the whole clip. At home real speech scored
            # 0.96-0.99 and the one empty clip 0.24: below 0.5, skip Whisper
            # (it invents "Thanks for watching!" on noise).
            vad.reset()
            clip = samples[: len(samples) // BLOCK * BLOCK].reshape(-1, BLOCK)
            peak = max((vad(b) for b in clip), default=0.0)
            print(f"(clip {len(samples) / sr:.1f} s, speech score peak {peak:.2f})")
            if peak < MIN_CLIP_SPEECH:
                print("(no speech in clip, ignored)")
                continue
            t0 = time.monotonic()
            user = voice.transcribe_samples(samples, sr)
            print(f"(stt {time.monotonic() - t0:.1f} s)")
        if not user:
            print("Heard nothing. Try again.")
            continue
        if re.search(r"\b(bye|goodbye|see you)\b", user.lower()):
            voice.speak("Bye! That was nice.")
            return
        jpeg = look(cam) if chat.vision and LOOK.search(user) else None
        answer = chat.reply(user, jpeg)
        voice.speak(answer)
        if cam is None and not auto:
            print("Enter to talk again.")
        else:
            time.sleep(0.4)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brain", choices=BRAINS, default="4b", help="Language model")
    parser.add_argument(
        "--type", action="store_true", help="Type English instead of using the mic"
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
        "--trigger",
        choices=("speech", "loud"),
        default="speech",
        help="Start recording on detected speech (default) or on loudness",
    )
    args = parser.parse_args()
    if args.type and args.auto:
        parser.error("use --type or --auto, not both")
    brain = BRAINS[args.brain]
    # Whisper first: --fit on the 8b sizes the model to what is left.
    voice = EnglishVoice(whisper=brain.whisper)
    chat = EnglishChat(brain)
    print(f"GPU memory: {gpu_mem()}")
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
        loop(voice, chat, typed=args.type, auto=auto, cam=cam, trigger=args.trigger)
    except KeyboardInterrupt:
        print("\nBye.")
    finally:
        chat.close()
        if cam is not None:
            cam.stop()


if __name__ == "__main__":
    main()
