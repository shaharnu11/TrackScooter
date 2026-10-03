"""The chat brains: LocalChat (llama.cpp), Eyes (a vision brain that describes the camera), CloudChat (Claude), MindChat (cloud, local when offline)."""

from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
import time
import urllib.request
from collections.abc import Iterator
from contextlib import closing

from walle.lang import t
from walle.mind.brains import BRAINS, GGUF_DIR, Brain
from walle.mind.llama import LLAMA_PORT, _stale, clean_reply, start_llama
from walle.mind.rules import build_system


def fallback() -> str:
    return t("Sorry, I missed that. Say it again?", "סליחה, לא שמעתי. תגיד שוב?")


# Hard rule (rules/always.md says it too): the brain never claims to play,
# stop or pick music. Only music.py does that, and its lines do not pass
# through the brain. A sentence that claims it is dropped.
MUSIC_CLAIM = re.compile(
    r"\b(i'?m (now )?playing|i'?ll play|i will play|let me play|playing (you|a|some|this)|"
    r"here'?s (a|some|your) (song|track|tune|music)|i'?m (stopping|turning off) the music|"
    r"i (just )?(put|turned) on)\b"
    r"|אני (מנגן|אנגן|שם|אשים|מפעיל|אפעיל)\s+(לך\s+|לכם\s+)?(שיר|מוזיקה|את)|הנה שיר בשבילך|שמתי לך שיר",
    re.I,
)


OTHER_SPEAKER = re.compile(r"^\W*(אדם|משתמש|בן אדם|user|person|human)\s*:", re.I)


OWN_LABEL = re.compile(r"^\W*(וול-?אי|wall-?e|robot|רובוט)\s*:\s*", re.I)


# A sentence is done at . ! ? once the next word starts. Not at "…", so
# "One… two… three." stays one sentence.
SENTENCE_END = re.compile(r"[.!?](?=\s)")


EMOJI = re.compile(r"[\U0001f000-\U0001faff\U00002600-\U000027bf\U0000fe0f]")


# Qwen slips into Chinese now and then ("Five十六"). Kokoro cannot say it.
CJK = re.compile(r"[\U00003000-\U00009fff\U0000ac00-\U0000d7af\U0000ff00-\U0000ffef]")


EYES_PORT = 18090  # 8090 was taken by Cursor on this Mac


DESCRIBE = (
    "You are the camera eye of a small robot. Describe the picture in one or "
    "two short English sentences: the person in front (clothes, hair, what "
    "they hold, how they look) and the place. Only what is clearly there; "
    "never guess small things like writing or animals."
)


class Eyes:
    """A vision brain that only describes the camera picture in words, for a
    brain that cannot see (DictaLM in Hebrew). Its own llama-server port."""

    def __init__(self, brain: Brain) -> None:
        model = GGUF_DIR / brain.file
        if not model.exists() or not (GGUF_DIR / brain.mmproj).exists():
            sys.exit(f"Missing {model} or its mmproj\nRun: python scripts/download_models.py --brain {brain.file}")
        print(f"Loading eyes: {brain.file}")
        self._model = model
        self._extra = [
            "-ngl", "99", "-np", "1", "-fa", "on",
            "--reasoning", "off",
            "--mmproj", str(GGUF_DIR / brain.mmproj),
            "--image-max-tokens", "256",
        ]
        self._server: subprocess.Popen | None = start_llama(model, self._extra, EYES_PORT)

    def describe(self, jpeg: bytes) -> str:
        url = "data:image/jpeg;base64," + base64.b64encode(jpeg).decode("ascii")
        body = json.dumps({
            "messages": [
                {"role": "system", "content": DESCRIBE},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": url}},
                    {"type": "text", "text": "What do you see?"},
                ]},
            ],
            "max_tokens": 70, "temperature": 0.2,
            "chat_template_kwargs": {"enable_thinking": False},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{EYES_PORT}/v1/chat/completions", data=body, headers={"Content-Type": "application/json"}
        )
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                text = (json.load(r)["choices"][0]["message"].get("content") or "").strip()
        except OSError as exc:
            print(f"(eyes failed: {exc})")
            return ""
        print(f"(eyes {time.monotonic() - t0:.1f} s: {text})")
        return text

    def wake(self) -> None:
        if self._server is None or self._server.poll() is not None:
            self._server = start_llama(self._model, self._extra, EYES_PORT)

    def close(self) -> None:
        if self._server is not None and self._server.poll() is None:
            self._server.terminate()
            try:
                self._server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server.kill()
        self._server = None


class LocalChat:
    """A Qwen3 GGUF in llama-server. Thinking off: WALL-E answers at once."""

    port = LLAMA_PORT
    eyes: Eyes | None = None

    # Management mode (walle/modes/management.py) swaps these; None = the festival persona.
    override: str | None = None
    max_sentences = 2
    max_tokens = 100

    def set_mode(self, system: str | None, sentences: int = 2, tokens: int = 100) -> None:
        self.override, self.max_sentences, self.max_tokens = system, sentences, tokens

    # Who is in front (walle/people/persons.py): name and notes, added to the persona.
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
            sys.exit(f"Missing {model}\nRun: python scripts/download_models.py")
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
        self.vision = bool(brain.mmproj) or bool(brain.eyes)
        self.eyes = Eyes(BRAINS[brain.eyes]) if brain.eyes else None
        self.system = build_system(self.vision, described=self.eyes is not None)
        if brain.mmproj:
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
        if self.eyes is not None:
            self.eyes.wake()

    def close(self) -> None:
        if self._server is not None and self._server.poll() is None:
            self._server.terminate()
            try:
                self._server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server.kill()
        self._server = None
        if self.eyes is not None:
            self.eyes.close()

    def reload_system(self) -> None:
        """Pick up a changed personality.md without a restart."""
        self.system = build_system(self.vision, described=self.eyes is not None)

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
            f"http://127.0.0.1:{self.port}/v1/chat/completions",
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
            f"http://127.0.0.1:{self.port}/v1/chat/completions",
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
        if jpeg is not None and self.eyes is not None:
            # Hebrew: the eyes put the picture into words for DictaLM.
            seen = self.eyes.describe(jpeg)
            if seen:
                messages[-1] = {"role": "user", "content": f"{user_text}\n\n(Your camera sees right now: {seen})"}
        elif jpeg is not None:
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
                    # A personality with example lines made the brain write
                    # the visitor's next line too ("אדם: ..."): stop there.
                    if OTHER_SPEAKER.match(part):
                        break
                    part = OWN_LABEL.sub("", part).strip()
                    if MUSIC_CLAIM.search(part):
                        print(f"(rule: dropped a music claim: {part})")
                        continue
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
                said.append(fallback())
                yield said[-1]
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
                text = fallback()
        text = text or fallback()
        self.history.append({"role": "assistant", "content": text})
        return text


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


class CloudChat(LocalChat):
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
        self.local: LocalChat | None = None
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

    def _local_brain(self) -> LocalChat:
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
