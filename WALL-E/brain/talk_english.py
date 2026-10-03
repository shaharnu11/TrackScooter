#!/usr/bin/env python3
"""Talk to WALL-E in English. Offline. Microphone in, speaker out.

    python3 talk_english.py --brain 4b      # Qwen3-4B Q4, fast
    python3 talk_english.py --brain 4b-q5   # Qwen3-4B Q5, a bit sharper
    python3 talk_english.py --brain 8b      # Qwen3-8B, smarter, slower
    python3 talk_english.py --brain 4b-vl   # Qwen3-VL-4B: sees the camera
    python3 talk_english.py --brain 8b-vl   # Qwen3-VL-8B: sees, smarter (the Mac)
    python3 talk_english.py --brain 30b-vl  # Qwen3-VL-30B-A3B: the Mac's brain (Mac only)
    python3 talk_english.py --brain 4b-vl --mind cloud   # Claude online,
        # Qwen3-VL-4B only if the connection fails. Needs ANTHROPIC_API_KEY.

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

from english_voice import BRAINS, GGUF_DIR, KOKORO_VOICE, Brain, EnglishVoice, chirp, wake_sound
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
from owner import Owner
from manage import CHANGE_LINE as MANAGE_CHANGE_LINE
from manage import EXIT as MANAGE_EXIT
from manage import START as MANAGE_START
from manage import Manager
from persons import FORGET, People
from persona_edit import START as PERSONA_START
from persona_edit import PersonaEditor, load_character
from vad_listen import BLOCK, END_S, Gate, Heard, StreamVAD, listen_vad

FALLBACK = "Sorry, I missed that. Say it again?"
MIN_CLIP_SPEECH = 0.5

# Who he is lives in personality.md (Shahar edits it by voice, persona_edit.py).
# How he must behave is RULES below: fixed here, so an update cannot drop it.
RULES = (
    "Speak plain spoken English: one or two short, warm, simple sentences, "
    "under 25 words. No lists, no asterisks, no emojis, no code. "
    # Midburn: most people are Israelis, English is not their first language.
    "Most people you meet are not native English speakers. Use simple, common "
    "words a learner knows (say tiring, not exhausting), short sentences, and "
    "no idioms, slang or fancy words. Often end with one short, simple question "
    "to the person, to keep the talk going. "
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
    "If anything in your personality conflicts with these rules, the rules win. "
)

EYES_TEXT_ONLY = (
    "Your camera only tells you that a person is in front of you. You cannot "
    "see objects, colours, weather or scenery, so never describe them, not "
    "even the place around you."
)

# The vision brain: a picture comes with questions about seeing. At home it
# added a dog and glasses that were not there, and sand dunes to a living
# room; asked yes/no, it said no to both. So: only what is clear, admit doubt.
EYES_VISION = (
    "When a picture is attached, it is what your camera eye sees right now, "
    "and the person talking to you is in it. Describe only what is clearly in "
    "the picture. If you are not sure about something, say so; never guess "
    "small things like glasses, animals or writing. You may mention or ask "
    "about one thing you clearly see, even when nobody asked. With no picture, never "
    "say you see anything, and do not describe the person or the place "
    "around you."
)


def build_system(vision: bool) -> str:
    """personality.md (who he is) + RULES + camera rules. Re-read each call."""
    return load_character() + " " + RULES + (EYES_VISION if vision else EYES_TEXT_ONLY)

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

PEEK_EVERY = 3  # turns between unasked looks through the camera

# A sentence is done at . ! ? once the next word starts. Not at "…", so
# "One… two… three." stays one sentence.
SENTENCE_END = re.compile(r"[.!?](?=\s)")

EMOJI = re.compile(r"[\U0001f000-\U0001faff\U00002600-\U000027bf\U0000fe0f]")
# Qwen slips into Chinese now and then ("Five十六"). Kokoro cannot say it.
CJK = re.compile(r"[\U00003000-\U00009fff\U0000ac00-\U0000d7af\U0000ff00-\U0000ffef]")


def gpu_mem() -> str:
    if sys.platform == "darwin":
        return "Apple GPU (Metal), memory shared with the system"
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

    # Management mode (manage.py) swaps these; None = the festival persona.
    override: str | None = None
    max_sentences = 2
    max_tokens = 100

    def set_mode(self, system: str | None, sentences: int = 2, tokens: int = 100) -> None:
        self.override, self.max_sentences, self.max_tokens = system, sentences, tokens

    # Who is in front (persons.py): name and notes, added to the persona.
    visitor = ""

    def set_visitor(self, note: str) -> None:
        self.visitor = note

    def system_prompt(self) -> str:
        if self.override:
            return self.override
        return self.system + ("\n\n" + self.visitor if self.visitor else "")

    def __init__(self, brain: Brain) -> None:
        self.history: list[dict[str, str]] = []
        model = GGUF_DIR / brain.file
        if not model.exists():
            sys.exit(f"Missing {model}\nRun: python download_english.py")
        # The notes and the GPU/CPU split in BRAINS are sized for the XPS's
        # 4 GB card. The Mac's GPU uses the shared RAM: everything fits on it.
        mac = sys.platform == "darwin"
        print(f"Loading chat: {brain.file}, all on the Mac GPU" if mac else f"Loading chat: {brain.note}")
        extra = [
            "-ngl", "99" if mac else brain.gpu_layers,
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
        self.system = build_system(self.vision)
        if self.vision:
            # The eye model stays in RAM and runs on the CPU: 780 MiB less on
            # the card (3.85 -> ~3.06 GB with Whisper), and looks are rare.
            # 256 image tokens, not 384: alone on the bench a look took 2.4 s,
            # but in a live session (camera, speech detector and voice all on
            # the CPU too) it took 5.9-6.5 s. 384 saw "an earbud in the right
            # ear" where 256 saw "earbuds"; speed matters more to a talker.
            extra += [
                "--mmproj", str(GGUF_DIR / brain.mmproj),
                "--image-max-tokens", "256",
            ]
            if not mac:
                extra.append("--no-mmproj-offload")
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

    def reload_system(self) -> None:
        """Pick up a changed personality.md without a restart."""
        self.system = build_system(self.vision)

    def complete(self, system: str, text: str, max_tokens: int = 400) -> str:
        """One stand-alone request with its own instructions (no history)."""
        messages = [{"role": "system", "content": system}, {"role": "user", "content": text}]
        return self._raw_reply(messages, 0.3, max_tokens)

    def _raw_reply(self, messages: list[dict], temperature: float, max_tokens: int = 100) -> str:
        body = json.dumps(
            {
                "messages": messages,
                "max_tokens": max_tokens,
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
                "max_tokens": self.max_tokens,
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
        messages: list[dict] = [{"role": "system", "content": self.system_prompt()}, *self.history[-8:]]
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
        try:
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
                    # A short opener ("Hello!", "Tel Aviv, huh?") does not use
                    # up the limit: counting it cut off the question that came
                    # after it, the one that keeps the talk going.
                    full = sum(1 for x in said if len(x.split()) > 3)
                    if full >= self.max_sentences or len(said) >= self.max_sentences + 2:
                        break
            if not said:
                said.append(FALLBACK)
                yield FALLBACK
        finally:
            # Also when he was talked over and the stream was closed early.
            if said:
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
        # "Go to sleep": brain off, camera paused, only the mic and Whisper
        # listen, and only "wake up" wakes him (a face does not).
        self.manual = False
        # One sleep or wake at a time. "Wake up" and a face seen a moment
        # later both woke him: two brains started, sleep stopped one, and
        # the other kept its memory.
        self._lock = threading.Lock()

    def touch(self) -> None:
        self.last = time.monotonic()

    def sleep_now(self) -> None:
        self.manual = True  # first: no face can start a wake from here on
        if self._busy is not None:
            self._busy.join()
        with self._lock:
            print("(told to sleep: brain off, camera paused; say wake up)")
            self.chat.sleep()
            self.awake = False

    def wake_now(self) -> None:
        if self._busy is not None:
            self._busy.join()
        self._wake()
        self.manual = False  # last: no face-wake can run beside this one

    def tick(self, face: bool) -> None:
        if self.idle_s <= 0 or self.manual:
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
        if self.manual:
            return
        if not self.awake and (self._busy is None or not self._busy.is_alive()):
            self._run(self._wake)

    def ready(self) -> None:
        """Block until the models are loaded (before Whisper or the brain)."""
        if self.manual:
            self.voice.wake_ears()  # told to sleep: only Whisper, for "wake up"
            self.voice.wait_ears()
            return
        if self._busy is not None:
            self._busy.join()
        if not self.awake:
            self._wake()

    def _run(self, job) -> None:
        self._busy = threading.Thread(target=job, daemon=True)
        self._busy.start()

    def _sleep(self) -> None:
        with self._lock:
            if not self.awake:
                return
            print(f"(nobody for {self.idle_s:.0f} s: sleeping, models off the GPU)")
            self.chat.sleep()
            self.voice.sleep_ears()
            self.awake = False

    def _wake(self) -> None:
        with self._lock:
            if self.awake:
                return
            t0 = time.monotonic()
            print("(waking up…)")
            wake_sound()
            self.voice.wake_ears()  # Whisper's process loads while the brain does
            self.chat.wake()
            self.voice.wait_ears()
            self.awake = True
            self.touch()
            print(f"(awake in {time.monotonic() - t0:.1f} s)")


CLOUD_MODEL = "claude-opus-5"
# USD per million input / output tokens, for the running cost in the log.
CLOUD_PRICES = {
    "claude-opus-5": (5.0, 25.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-haiku-4-5": (1.0, 5.0),
}
CLOUD_RETRY_S = 60  # after a failed cloud call, stay local this long


def _api_key_from_windows() -> None:
    """`setx ANTHROPIC_API_KEY ...` only reaches new windows. Read it anyway."""
    import os

    if os.environ.get("ANTHROPIC_API_KEY") or sys.platform != "win32":
        return
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            os.environ["ANTHROPIC_API_KEY"] = winreg.QueryValueEx(k, "ANTHROPIC_API_KEY")[0]
    except OSError:
        pass


class CloudChat(EnglishChat):
    """Claude over the internet, with the local brain's interface.

    Same persona and the same two-sentence streaming, so WALL-E sounds the
    same, only sharper. Sees every picture it is sent. Uses no GPU.
    Effort "low": a festival chat needs a quick answer, not deep thought.
    Refusals fall back server-side to another Claude model ("default").
    """

    def __init__(self, model: str = CLOUD_MODEL) -> None:
        import anthropic

        _api_key_from_windows()
        self.history: list[dict] = []
        self.vision = True
        self.system = build_system(True)
        self.model = model
        self._server = None
        # Fail fast when the signal is bad: the local brain is the fallback.
        self.client = anthropic.Anthropic(
            timeout=anthropic.Timeout(20.0, connect=3.0, read=10.0), max_retries=0
        )
        self.spent = 0.0
        import os

        # With no key the SDK raises a bare TypeError at the first call.
        self.ready = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
        print(f"Chat in the cloud: {model}" if self.ready else
              "No ANTHROPIC_API_KEY: the cloud brain is off, using the local one.")

    def sleep(self) -> None:
        self.history.clear()  # a new visitor; nothing on the GPU to free

    def wake(self) -> None:
        pass

    def close(self) -> None:
        pass

    def _messages(self, user_text: str, jpeg: bytes | None) -> list[dict]:
        self.history.append({"role": "user", "content": user_text})
        messages = [dict(m) for m in self.history[-8:]]
        while messages and messages[0]["role"] != "user":
            messages.pop(0)  # the API wants a user turn first
        if jpeg is not None:
            messages[-1] = {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64.standard_b64encode(jpeg).decode("ascii"),
                        },
                    },
                    {"type": "text", "text": user_text},
                ],
            }
        return messages

    def _request(self, messages: list[dict], max_tokens: int) -> dict:
        return {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": self.system_prompt(),
            "messages": messages,
            "output_config": {"effort": "low"},
            "betas": ["server-side-fallback-2026-07-01"],
            "fallbacks": "default",
        }

    def _account(self, usage) -> None:
        if usage is None:
            return
        p_in, p_out = CLOUD_PRICES.get(self.model, (5.0, 25.0))
        tokens_in = (usage.input_tokens or 0) + (getattr(usage, "cache_read_input_tokens", 0) or 0)
        cost = tokens_in * p_in / 1e6 + (usage.output_tokens or 0) * p_out / 1e6
        self.spent += cost
        print(f"(cloud {tokens_in} in / {usage.output_tokens} out, ${cost:.4f}; this run ${self.spent:.2f})")

    def _raw_reply(self, messages: list[dict], temperature: float, max_tokens: int = 1024) -> str:
        msg = self.client.beta.messages.create(**self._request(messages, 1024))
        self._account(msg.usage)
        return "".join(b.text for b in msg.content if b.type == "text")

    def reload_system(self) -> None:
        self.system = build_system(True)

    def complete(self, system: str, text: str, max_tokens: int = 1024) -> str:
        req = self._request([{"role": "user", "content": text}], max_tokens)
        req["system"] = system
        msg = self.client.beta.messages.create(**req)
        self._account(msg.usage)
        return "".join(b.text for b in msg.content if b.type == "text")

    def _stream(self, messages: list[dict], temperature: float) -> Iterator[str]:
        t0 = time.monotonic()
        first = True
        buf = ""
        with self.client.beta.messages.stream(**self._request(messages, 1024)) as stream:
            try:
                for text in stream.text_stream:
                    buf += text
                    while (m := SENTENCE_END.search(buf)) is not None:
                        sentence, buf = buf[: m.end()].strip(), buf[m.end():]
                        if first:
                            print(f"(cloud first sentence {time.monotonic() - t0:.1f} s)")
                            first = False
                        yield sentence
            finally:
                # Also when WALL-E stops after two sentences mid-stream.
                snap = getattr(stream, "current_message_snapshot", None)
                self._account(getattr(snap, "usage", None))
        if buf.strip():
            yield buf.strip()


class MindChat:
    """--mind cloud: Claude while the internet works, the local brain when not.

    The local brain is only started the first time the cloud fails, so a
    good connection leaves the GPU to Whisper alone. After a failure it stays
    local for CLOUD_RETRY_S, then tries the cloud again.
    """

    def __init__(self, cloud: CloudChat, make_local) -> None:
        self.cloud = cloud
        self._make_local = make_local
        self.local: EnglishChat | None = None
        self.history = cloud.history  # one conversation, whichever brain answers
        self.vision = True
        self._offline_until = 0.0

    def set_mode(self, system: str | None, sentences: int = 2, tokens: int = 100) -> None:
        self._mode = (system, sentences, tokens)
        self.cloud.set_mode(*self._mode)
        if self.local is not None:
            self.local.set_mode(*self._mode)

    def set_visitor(self, note: str) -> None:
        self._visitor = note
        self.cloud.set_visitor(note)
        if self.local is not None:
            self.local.set_visitor(note)

    def _local_brain(self) -> EnglishChat:
        if self.local is None:
            print("(no cloud: starting the local brain)")
            self.local = self._make_local()
            self.local.history = self.history
            self.local.set_mode(*getattr(self, "_mode", (None, 2, 100)))
            self.local.set_visitor(getattr(self, "_visitor", ""))
        else:
            self.local.wake()
        return self.local

    def reply_stream(self, user_text: str, jpeg: bytes | None = None) -> Iterator[str]:
        import anthropic

        if self.cloud.ready and time.monotonic() >= self._offline_until:
            spoke = False
            try:
                for part in self.cloud.reply_stream(user_text, jpeg):
                    spoke = True
                    yield part
                return
            except anthropic.AnthropicError as exc:  # network, timeout, 4xx/5xx
                why = "no API key" if isinstance(exc, anthropic.AuthenticationError) else type(exc).__name__
                print(f"(cloud failed: {why}; local brain for {CLOUD_RETRY_S} s)")
                self._offline_until = time.monotonic() + CLOUD_RETRY_S
                if spoke:
                    return  # half an answer was already spoken; leave it
                if self.history and self.history[-1] == {"role": "user", "content": user_text}:
                    self.history.pop()  # the local brain adds the turn again
        local = self._local_brain()
        yield from local.reply_stream(user_text, jpeg if local.vision else None)

    def reload_system(self) -> None:
        self.cloud.reload_system()
        if self.local is not None:
            self.local.reload_system()

    def complete(self, system: str, text: str) -> str:
        import anthropic

        if self.cloud.ready and time.monotonic() >= self._offline_until:
            try:
                return self.cloud.complete(system, text)
            except anthropic.AnthropicError as exc:
                print(f"(cloud failed: {type(exc).__name__}; local brain for {CLOUD_RETRY_S} s)")
                self._offline_until = time.monotonic() + CLOUD_RETRY_S
        return self._local_brain().complete(system, text)

    def sleep(self) -> None:
        self.cloud.sleep()
        if self.local is not None:
            self.local.sleep()

    def wake(self) -> None:
        pass  # the local brain wakes only when the cloud is out

    def close(self) -> None:
        if self.local is not None:
            self.local.close()


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


def vet(rec, vad: StreamVAD, gate: Gate, use_gate: bool, trigger: str):
    """A recording worth sending to Whisper: (samples, sr, heard, t_stop),
    or None. Prints why not."""
    if rec is None:
        print("(too little speech, ignored)")
        return None
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
        print("(no speech in clip, ignored)")
        return None
    if heard is not None:
        # A voice while your face is locked is not always yours: a
        # video nearby got answered. Mouth and loudness say whose.
        print(f"(who: {gate.describe(heard)})")
        why = gate.reasons(heard) if use_gate else []
        if why:
            print(f"(someone else talking? {'; '.join(why)}. Ignored)")
            return None
    # The recording ended one end-of-speech pause after the voice did.
    t_stop = time.monotonic() - (END_S if trigger == "speech" else 0.8)
    return samples, sr, heard, t_stop


# "Go to sleep" / "wake up". "I'm going to sleep now" is about the person.
SLEEP = re.compile(r"\b(go to (sleep|bed)|sleep now|sleep mode|take a nap)\b", re.I)
NOT_SLEEP = re.compile(r"\b(i|i'm|i am|i'll|we|we're|they)\b[^.?!]{0,15}\bgo(ing)? to (sleep|bed)\b", re.I)
WAKE = re.compile(r"\b(wake|get up|good morning)\b", re.I)


def _answers_only(parts):
    """Management mode: no question back after the answer. Told not to,
    the brain still ended with "What kind of music do you like?"."""
    for i, part in enumerate(parts):
        if i > 0 and part.rstrip().endswith("?"):
            continue
        yield part


def asleep_heard(user: str, voice, sleeper, cam) -> bool:
    """Told to sleep: True if the sentence was handled here (woken or ignored)."""
    if not sleeper.manual:
        return False
    if WAKE.search(user):
        if cam is not None:
            cam.resume()
        sleeper.wake_now()
        voice.speak("I'm awake! Hi again.")
    else:
        print("(asleep: only wake up counts, ignored)")
    return True


def respond(user: str, t_stop: float, voice, chat, cam, music, sleeper, editor, hear, manager=None, people=None) -> bool:
    """Answer one sentence. False when it was goodbye."""
    if manager is not None and not manager.active and MANAGE_START.search(user) and not MANAGE_EXIT.search(user):
        if manager.enter(chat, cam):
            voice.speak("Management mode. Ask me anything about how I work. Say exit management mode when you're done.")
        else:
            voice.speak("Sorry, management mode is only for Shahar.")
        return True
    if manager is not None and manager.active and MANAGE_EXIT.search(user):
        manager.leave(chat)
        voice.speak("Okay, back to normal.")
        return True
    if (
        manager is not None and manager.active and not PERSONA_START.search(user)
        and manager.wants_change(chat, user)
    ):
        voice.speak(MANAGE_CHANGE_LINE)
        return True
    if SLEEP.search(user) and not NOT_SLEEP.search(user):
        voice.speak("Okay, going to sleep. Say wake up to wake me.")
        sleeper.sleep_now()
        if cam is not None:
            cam.pause()
        return True
    if PERSONA_START.search(user):
        # Shahar only: face + secret word, then the changes, read back,
        # confirmed. Checked only when this phrase is heard.
        music.duck(True)
        editor.session(voice, chat, cam, hear)
        music.duck(False)
        sleeper.touch()
        return True
    if re.search(r"\b(bye|goodbye|see you|shut ?down|turn yourself off)\b", user.lower()):
        voice.speak("Bye! That was nice.")
        return False
    managing = manager is not None and manager.active
    if people is not None and not managing:
        if FORGET.search(user):
            people.forget(voice, chat)
            return True
        people.before(chat)  # same person, someone new, or someone remembered
    music.duck(True)
    print()
    # Management mode: "what can you play?" is a question, not a command.
    cmd = None if manager is not None and manager.active else music.command(user)
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
        # A picture also comes unasked on the first sentence and every third
        # one, so he can notice things and ask about them (~0.5 s slower then).
        # Not in management mode: there it only answers.
        peek = (manager is None or not manager.active) and len(chat.history) // 2 % PEEK_EVERY == 0
        jpeg = look(cam) if chat.vision and (LOOK.search(user) or peek) else None
        parts = chat.reply_stream(user, jpeg)
        if manager is not None and manager.active:
            parts = _answers_only(parts)
        voice.speak_stream(parts, t_stop)
    if people is not None and not managing and not (voice.interrupt is not None and voice.interrupt.is_set()):
        people.after(voice, chat, hear)  # after a few exchanges: "can I remember you?"
    return True


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
    manager: Manager | None = None,
    people: People | None = None,
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
    editor = PersonaEditor(Owner())
    print(f"Listening trigger: {trigger}" + ("" if use_gate else " (no mouth/loudness check)"))

    def hear():
        """One sentence from the person in front: (text, t_stop), None when
        there is nothing worth answering, False when q was pressed."""
        if cam is None and not auto and not typed:
            try:
                input()
            except EOFError:
                return False
        if typed:
            text = input("You:    ").strip()
            sleeper.ready()
            return (text, time.monotonic()) if text else None
        if trigger == "speech":
            # Speech-triggered, not loudness-triggered: music and fans pass.
            # The music ducks the moment a voice starts, not after; a
            # sleeping WALL-E starts loading the same moment.
            rec = listen_vad(
                cam,
                vad,
                on_start=lambda: (music.duck(True), sleeper.kick()),
                on_tick=sleeper.tick,
                face_free=lambda: sleeper.manual,
            )
        elif cam is not None:
            rec = listen(cam)  # the old loudness / mouth-motion trigger
        else:
            rec = record_utterance(cam=None)
        if rec is False:
            return False
        got = vet(rec, vad, gate, use_gate and not sleeper.manual, trigger)
        if got is None:
            music.duck(False)
            return None
        samples, sr, heard, t_stop = got
        chirp()
        sleeper.ready()  # asleep: this is where the ~6 s reload is waited out
        t0 = time.monotonic()
        text = voice.transcribe_samples(samples, sr)
        print(f"(stt {time.monotonic() - t0:.1f} s)")
        if not text:
            music.duck(False)
            print("Heard nothing. Try again.")
            return None
        if heard is not None:
            gate.accept(heard)  # learn how loud the person in front sounds
        return text, t_stop

    while True:
        got = hear()
        if got is False:
            return
        if got is None:
            continue
        user, t_stop = got
        if asleep_heard(user, voice, sleeper, cam):
            continue
        if PERSONA_START.search(user):
            respond(user, t_stop, voice, chat, cam, music, sleeper, editor, hear, manager, people)
            continue
        if not respond(user, t_stop, voice, chat, cam, music, sleeper, editor, hear, manager, people):
            return
        music.duck(False)
        sleeper.touch()
        if cam is None and not auto:
            print("Enter to talk again.")
        else:
            time.sleep(0.4)


def loop_barge(
    voice: EnglishVoice,
    chat: EnglishChat,
    cam: TalkCam | None,
    music: MusicPlayer,
    sleeper: Sleeper,
    use_gate: bool = True,
    use_lips: bool = True,
    manager: Manager | None = None,
    people: People | None = None,
) -> None:
    """Talk over WALL-E: he stops and listens.

    loop() does one thing at a time: while Whisper, the brain and the voice
    worked, the mic was closed and the camera window froze. Here this thread
    listens all the time (mic, speech detector, camera window) and a worker
    thread transcribes, thinks and talks. Speech from the person in front
    while he thinks or talks stops him (Speaker fades out), and the new
    sentence is answered. echo.py keeps his own voice out of the mic.
    """
    import queue

    from echo import open_audio

    speaker, mic = open_audio()
    voice.speaker = speaker
    voice.interrupt = threading.Event()
    clips: queue.Queue = queue.Queue()
    quit_ = threading.Event()
    busy = threading.Event()  # the worker is on a sentence
    recording = threading.Event()  # a voice is being recorded right now
    vad = StreamVAD()
    gate = Gate()
    editor = PersonaEditor(Owner())

    def unduck() -> None:
        if not busy.is_set() and not recording.is_set() and clips.empty():
            music.duck(False)

    def hear():
        """The worker's next sentence: (text, t_stop), None, or False to quit."""
        item = clips.get()
        if item is None:
            return False
        samples, sr, heard, t_stop = item
        voice.interrupt.clear()  # a new sentence: he may talk again
        sleeper.ready()  # asleep: this is where the reload is waited out
        t0 = time.monotonic()
        text = voice.transcribe_samples(samples, sr)
        print(f"(stt {time.monotonic() - t0:.1f} s)")
        if not text:
            print("Heard nothing. Try again.")
            return None
        if heard is not None:
            gate.accept(heard)  # learn how loud the person in front sounds
        return text, t_stop

    def work() -> None:
        try:
            while True:
                got = hear()
                if got is False:
                    return
                if got is None:
                    unduck()
                    continue
                if asleep_heard(got[0], voice, sleeper, cam):
                    continue
                busy.set()
                try:
                    if not respond(*got, voice, chat, cam, music, sleeper, editor, hear, manager, people):
                        quit_.set()
                        return
                finally:
                    busy.clear()
                    sleeper.touch()
                    unduck()
        except BaseException:
            quit_.set()  # a crash in the worker ends the listening too
            raise

    def on_start() -> None:
        recording.set()
        if sleeper.manual:
            return  # asleep: only listening for "wake up"
        music.duck(True)  # under the voice from its first moment
        sleeper.kick()  # a sleeping WALL-E starts loading now
        if busy.is_set():
            print("(you spoke over WALL-E: he stops)")
            voice.interrupt.set()

    voice.speak("Hi. I'm WALL-E. Talk to me.")
    print(f"Music folder: {music.folder}  ({len(music.songs())} songs)")
    print()
    print("Talk any time, also while he talks. Ctrl+C or q to quit.")
    lips = use_gate and use_lips and cam is not None and cam.cam.lips
    print("Listening trigger: speech, barge-in" + (", moving lips" if lips else "")
          + ("" if use_gate else " (no mouth/loudness check)"))
    worker = threading.Thread(target=work, daemon=True)
    worker.start()
    try:
        while not quit_.is_set():
            rec = listen_vad(
                cam, vad, stream=mic, on_start=on_start, on_tick=sleeper.tick,
                busy=busy.is_set, quit=quit_, need_lips=use_gate and use_lips,
                face_free=lambda: sleeper.manual,
            )
            recording.clear()
            if rec is False:
                break
            got = vet(rec, vad, gate, use_gate and not sleeper.manual, "speech")
            if got is None:
                unduck()
                continue
            chirp()
            clips.put(got)
    finally:
        voice.interrupt.set()  # stop talking
        clips.put(None)
        worker.join(timeout=10)
        speaker.close()
        mic.close()


INSTANCE_PORT = 8088  # held while WALL-E runs: a second start refuses


def one_instance():
    """Two WALL-Es ran at once (an old one never quit): two voices, two
    brains. Holding a local port is the lock; the OS frees it on any exit,
    also a crash, on the Mac and on Windows."""
    import socket

    lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        lock.bind(("127.0.0.1", INSTANCE_PORT))
    except OSError:
        sys.exit("WALL-E is already running. Stop it first (Ctrl+C or q in its window).")
    return lock


def main() -> None:
    _lock = one_instance()  # noqa: F841 — kept open until WALL-E exits
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
        "--mind",
        choices=("local", "cloud"),
        default="local",
        help="local: the brain on this laptop. cloud: Claude over the internet, "
        "falling back to the local brain when the connection fails",
    )
    parser.add_argument(
        "--cloud-model",
        choices=tuple(CLOUD_PRICES),
        default=CLOUD_MODEL,
        help="Claude model for --mind cloud",
    )
    parser.add_argument(
        "--no-barge-in",
        action="store_true",
        help="One thing at a time: no talking over WALL-E (the Mac's default is barge-in)",
    )
    parser.add_argument(
        "--no-people",
        action="store_true",
        help="Do not offer to remember people (persons/)",
    )
    parser.add_argument(
        "--no-lips",
        action="store_true",
        help="Do not wait for moving lips (the Mac's default: a voice counts only while the lips move)",
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
    if args.mind == "cloud":
        # The local brain is only loaded if the cloud fails; --brain picks it.
        chat = MindChat(CloudChat(args.cloud_model), lambda: EnglishChat(brain))
    else:
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
    # Barge-in needs the echo canceller (echo.py). Mac only for now: it was
    # tested there; the XPS keeps the one-thing-at-a-time loop.
    barge = (
        sys.platform == "darwin" and not args.no_barge_in and not args.type
        and args.trigger == "speech" and auto
    )
    if barge:
        from echo import available

        if not available():
            print("No echo canceller (pip install livekit): barge-in off.")
            barge = False
    lips = barge and not args.no_lips and not args.no_gate and cam is not None and cam.cam.lips
    facts = {
        "Brain": (
            f"Claude {args.cloud_model} over the internet; when offline, {brain.file} on this computer"
            if args.mind == "cloud" else f"{brain.file} (--brain {args.brain}) on this computer, offline"
        ) + (", it can see through the camera" if chat.vision else ""),
        "Hearing": f"{getattr(voice, 'ears', 'Whisper')}, Silero speech detector",
        "Voice": f"Kokoro text to speech, voice {KOKORO_VOICE}",
        "Talking over him (barge-in)": (
            "on: Shahar or a guest can talk while WALL-E talks; WALL-E then stops and listens"
            if barge else "off: WALL-E does not listen while he thinks or talks"
        ),
        "Moving-lips check": "on: a voice counts only while the lips in front move" if lips else "off",
    }
    manager = Manager(PersonaEditor(Owner())._is_shahar, facts, music, cam, sleeper)
    # Remembering people needs the camera; never without it.
    people = People(cam) if cam is not None and not args.no_people else None
    manager.people = people
    try:
        if barge:
            loop_barge(
                voice, chat, cam, music, sleeper, use_gate=not args.no_gate,
                use_lips=not args.no_lips, manager=manager, people=people,
            )
        else:
            loop(
                voice, chat, typed=args.type, auto=auto, cam=cam,
                music=music, sleeper=sleeper, trigger=args.trigger, use_gate=not args.no_gate,
                manager=manager, people=people,
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
