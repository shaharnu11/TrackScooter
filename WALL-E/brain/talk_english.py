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
import threading
import time
import urllib.request
from collections.abc import Iterator
from contextlib import closing

from english_voice import BRAINS, GGUF_DIR, Brain, EnglishVoice, chirp, wake_sound
from talk_hebrew import (
    LLAMA_PORT,
    TalkCam,
    _stale,
    clean_reply,
    listen,
    record_utterance,
    start_llama,
)
from music import MusicPlayer
from vad_listen import BLOCK, END_S, Gate, Heard, StreamVAD, listen_vad

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
    # He claimed "I can play music. Here's a jazzy number!" and played
    # nothing. Music commands are handled in code (music.py) before he sees
    # them; he only needs to know not to pretend.
    "You can play songs from your music folder, but that happens by itself "
    "when someone asks: never say you are playing, stopping or choosing a "
    "song. You cannot search the internet, set timers or control anything "
    "else; if asked, say so kindly. "
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

# A sentence is done at . ! ? once the next word starts. Not at "…", so
# "One… two… three." stays one sentence.
SENTENCE_END = re.compile(r"[.!?](?=\s)")

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
            # The eye model stays in RAM and runs on the CPU: 780 MiB less on
            # the card (3.85 -> ~3.06 GB with Whisper), and looks are rare.
            # Measured: first look 6.3 s vs 4.4 s on the GPU, then 2.4 s both.
            extra += [
                "--mmproj", str(GGUF_DIR / brain.mmproj),
                "--image-max-tokens", "384",
                "--no-mmproj-offload",
            ]
        self._model, self._extra = model, extra
        self._server: subprocess.Popen | None = start_llama(model, extra)

    def sleep(self) -> None:
        """Take the brain off the GPU. The conversation starts fresh after."""
        self.close()
        self.history.clear()

    def wake(self) -> None:
        if self._server is None or self._server.poll() is not None:
            self._server = start_llama(self._model, self._extra)

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

    def _stream(self, messages: list[dict], temperature: float) -> Iterator[str]:
        """The reply sentence by sentence, as llama-server writes it."""
        body = json.dumps(
            {
                "messages": messages,
                "max_tokens": 100,
                "temperature": temperature,
                "repeat_penalty": 1.1,
                "chat_template_kwargs": {"enable_thinking": False},
                "stream": True,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{LLAMA_PORT}/v1/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        t0 = time.monotonic()
        first = True
        buf = ""
        with urllib.request.urlopen(req, timeout=120) as r:
            for raw in r:
                line = raw.decode("utf-8").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                choices = json.loads(data).get("choices") or []
                if choices:
                    buf += choices[0].get("delta", {}).get("content") or ""
                while (m := SENTENCE_END.search(buf)) is not None:
                    sentence, buf = buf[: m.end()].strip(), buf[m.end():]
                    if first:
                        print(f"(chat first sentence {time.monotonic() - t0:.1f} s)")
                        first = False
                    yield sentence
        if buf.strip():
            if first:
                print(f"(chat {time.monotonic() - t0:.1f} s)")
            yield buf.strip()

    def _messages(self, user_text: str, jpeg: bytes | None) -> list[dict]:
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
        return messages

    def reply_stream(self, user_text: str, jpeg: bytes | None = None) -> Iterator[str]:
        """The answer one clean sentence at a time, two at most.

        WALL-E starts speaking the first while the brain writes the second.
        No stale-answer retry here (that needs the whole answer first); the
        repeat penalty covers Qwen, which repeated far less than DictaLM.
        """
        messages = self._messages(user_text, jpeg)
        said: list[str] = []
        with closing(self._stream(messages, 0.7)) as parts:
            for part in parts:
                part = EMOJI.sub("", part.replace("*", "").replace("#", "")).strip()
                if not part:
                    continue
                if CJK.search(part):
                    if not said:
                        # Nothing spoken yet: one cooler, whole-answer retry.
                        retry = EMOJI.sub("", clean_reply(self._raw_reply(messages, 0.3))).strip()
                        if retry and not CJK.search(retry):
                            said.append(retry)
                            yield retry
                    break
                said.append(part)
                yield part
                if len(said) == 2:
                    break
        if not said:
            said.append(FALLBACK)
            yield FALLBACK
        self.history.append({"role": "assistant", "content": " ".join(said)})

    def reply(self, user_text: str, jpeg: bytes | None = None) -> str:
        messages = self._messages(user_text, jpeg)
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


class Sleeper:
    """Take the GPU models off the card when nobody is around.

    On battery the laptop drew 38.8 W with WALL-E idle, 10.4 W of it the GPU
    just holding the brain and Whisper. With nothing loaded Windows can
    switch the NVIDIA chip off. Camera, face lock and music keep running on
    the CPU; a locked face starts the reload (~6-7 s), usually while the
    person is still walking up.
    """

    def __init__(self, voice: EnglishVoice, chat: EnglishChat, idle_s: float) -> None:
        self.voice, self.chat, self.idle_s = voice, chat, idle_s
        self.awake = True
        self.last = time.monotonic()  # last talk or face
        self._busy: threading.Thread | None = None

    def touch(self) -> None:
        self.last = time.monotonic()

    def tick(self, face: bool) -> None:
        if self.idle_s <= 0:
            return
        if face:
            self.last = time.monotonic()
        if self._busy is not None and self._busy.is_alive():
            return
        if self.awake and time.monotonic() - self.last > self.idle_s:
            self._run(self._sleep)
        elif not self.awake and face:
            self._run(self._wake)

    def kick(self) -> None:
        """Someone started talking: start waking now, if asleep."""
        if not self.awake and (self._busy is None or not self._busy.is_alive()):
            self._run(self._wake)

    def ready(self) -> None:
        """Block until the models are loaded (before Whisper or the brain)."""
        if self._busy is not None:
            self._busy.join()
        if not self.awake:
            self._wake()

    def _run(self, job) -> None:
        self._busy = threading.Thread(target=job, daemon=True)
        self._busy.start()

    def _sleep(self) -> None:
        print(f"(nobody for {self.idle_s:.0f} s: sleeping, models off the GPU)")
        self.chat.sleep()
        self.voice.sleep_ears()
        self.awake = False

    def _wake(self) -> None:
        t0 = time.monotonic()
        print("(face! waking up…)")
        wake_sound()
        self.voice.wake_ears()  # Whisper's process loads while the brain does
        self.chat.wake()
        self.voice.wait_ears()
        self.awake = True
        self.touch()
        print(f"(awake in {time.monotonic() - t0:.1f} s)")


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
    music: MusicPlayer,
    sleeper: Sleeper,
    trigger: str = "speech",
    use_gate: bool = True,
) -> None:
    voice.speak("Hi. I'm WALL-E. Talk to me.")
    print(f"Music folder: {music.folder}  ({len(music.songs())} songs)")
    print()
    if cam is not None:
        print("Green SPEAKER = he will listen. Ctrl+C or q to quit.")
    elif auto:
        print("Listening. Speak, then go quiet. Ctrl+C to quit.")
    else:
        print("Enter to talk. Ctrl+C to quit.")
    vad = None if typed else StreamVAD()
    gate = Gate()
    print(f"Listening trigger: {trigger}" + ("" if use_gate else " (no mouth/loudness check)"))
    while True:
        if cam is None and not auto and not typed:
            try:
                input()
            except EOFError:
                return
        if typed:
            user = input("You:    ").strip()
            t_stop = time.monotonic()
            sleeper.ready()
        else:
            if trigger == "speech":
                # Speech-triggered, not loudness-triggered: music and fans pass.
                # The music ducks the moment a voice starts, not after; a
                # sleeping WALL-E starts loading the same moment.
                rec = listen_vad(
                    cam,
                    vad,
                    on_start=lambda: (music.duck(True), sleeper.kick()),
                    on_tick=sleeper.tick,
                )
            elif cam is not None:
                rec = listen(cam)  # the old loudness / mouth-motion trigger
            else:
                rec = record_utterance(cam=None)
            if rec is False:
                return
            if rec is None:
                music.duck(False)
                print("(too little speech, ignored)")
                continue
            heard = rec if isinstance(rec, Heard) else None
            samples, sr = (heard.samples, heard.sr) if heard else rec
            # Silero's verdict on the whole clip. At home real speech scored
            # 0.96-0.99 and the one empty clip 0.24: below 0.5, skip Whisper
            # (it invents "Thanks for watching!" on noise).
            vad.reset()
            clip = samples[: len(samples) // BLOCK * BLOCK].reshape(-1, BLOCK)
            peak = max((vad(b) for b in clip), default=0.0)
            print(f"(clip {len(samples) / sr:.1f} s, speech score peak {peak:.2f})")
            if peak < MIN_CLIP_SPEECH:
                music.duck(False)
                print("(no speech in clip, ignored)")
                continue
            if heard is not None:
                # A voice while your face is locked is not always yours: a
                # video nearby got answered. Mouth and loudness say whose.
                print(f"(who: {gate.describe(heard)})")
                why = gate.reasons(heard) if use_gate else []
                if why:
                    music.duck(False)
                    print(f"(someone else talking? {'; '.join(why)}. Ignored)")
                    continue
            # The recording ended one end-of-speech pause after the voice did.
            t_stop = time.monotonic() - (END_S if trigger == "speech" else 0.8)
            chirp()
            sleeper.ready()  # asleep: this is where the ~6 s reload is waited out
            t0 = time.monotonic()
            user = voice.transcribe_samples(samples, sr)
            print(f"(stt {time.monotonic() - t0:.1f} s)")
        if not user:
            music.duck(False)
            print("Heard nothing. Try again.")
            continue
        if not typed and heard is not None:
            gate.accept(heard)  # learn how loud the person in front sounds
        if re.search(r"\b(bye|goodbye|see you)\b", user.lower()):
            voice.speak("Bye! That was nice.")
            return
        music.duck(True)
        print()
        cmd = music.command(user)
        if cmd is not None:
            # Handled in code, not by the brain; the brain still gets the
            # exchange in its history so "did you like that song?" makes sense.
            print("(music command)")
            if cmd.first is not None:
                cmd.line = cmd.first()  # Spotify: start it, check it plays, then name it
                music.duck(True)  # the new song starts at full volume
            voice.speak_stream(iter([cmd.line]), t_stop)
            if cmd.after is not None:
                cmd.after()
            chat.history += [
                {"role": "user", "content": user},
                {"role": "assistant", "content": cmd.line},
            ]
        else:
            jpeg = look(cam) if chat.vision and LOOK.search(user) else None
            voice.speak_stream(chat.reply_stream(user, jpeg), t_stop)
        music.duck(False)
        sleeper.touch()
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
    parser.add_argument(
        "--sleep-after",
        type=float,
        default=180,
        help="Seconds with no talk and no face before the models leave the GPU (0 = never)",
    )
    parser.add_argument(
        "--no-gate",
        action="store_true",
        help="Answer every voice, even with a still mouth or from far away",
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
    music = MusicPlayer()
    sleeper = Sleeper(voice, chat, args.sleep_after)
    try:
        loop(
            voice, chat, typed=args.type, auto=auto, cam=cam,
            music=music, sleeper=sleeper, trigger=args.trigger, use_gate=not args.no_gate,
        )
    except KeyboardInterrupt:
        print("\nBye.")
    finally:
        music.close()
        chat.close()
        voice.sleep_ears()
        if cam is not None:
            cam.stop()


if __name__ == "__main__":
    main()
