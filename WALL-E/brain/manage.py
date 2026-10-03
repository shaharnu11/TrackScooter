"""Management mode: WALL-E answers Shahar plainly about himself.

    "management mode"            -> owner face check, then serious answers
    "what brain do you run?"     -> facts from status(), no jokes
    "exit management mode" / "back to normal" -> the festival WALL-E again

In the mode the persona and its sarcasm are off, answers may run to five
sentences, music words do not start music ("what can you play?" is a
question), and the fun conversation is put aside and comes back after.
The brain is told to use only the facts below and say when it does not know.
"""

from __future__ import annotations

import re
import subprocess
import sys

from persona_edit import load_character

START = re.compile(r"\b(management|manager|manage|admin)\s+mode\b", re.I)
EXIT = re.compile(
    r"\b(exit|leave|end|stop|close|quit|finish|out of)\b.*\b(management|manager|manage|admin)\b"
    r"|\b(back to normal|normal mode|festival mode)\b",
    re.I,
)

SYSTEM = (
    "Management mode is on. You are WALL-E's management console, talking to "
    "Shahar, who built WALL-E and owns him. No jokes, no sarcasm, no persona, "
    "no cursing. Answer his questions about WALL-E plainly and correctly, in "
    "spoken English: up to five short sentences, no lists, no markdown, no "
    "symbols. English is not his first language: use simple, common words, "
    "but keep technical names exactly. Use only the facts below. If the answer "
    "is not in them, say you do not know. When a picture is attached it is the "
    "camera view right now; describe only what is clearly in it. "
    # A live session: he refused a personality wish as "not safe or allowed",
    # then asked Shahar what music he likes. Neither belongs here.
    "Do not ask Shahar questions, do not make small talk: only answer. Ask "
    "back only when you did not understand his question. This mode cannot "
    "change anything. If Shahar wants to change your personality or how you "
    "behave, do not judge or refuse the wish: tell him to say update "
    "personality start. Shahar decides who WALL-E is.\n\nFacts:\n"
)


KIND = (
    "In management mode, Shahar talks to WALL-E, a robot. Speech recognition "
    "may garble words. Is his sentence a QUESTION (about WALL-E, his setup, "
    "or anything to answer) or a CHANGE (a wish to change how WALL-E talks or "
    "behaves, his personality, jokes, topics)? Answer with one word: QUESTION "
    "or CHANGE."
)

CHANGE_LINE = (
    "I can't change that in management mode. To change my personality, "
    "say: update personality start."
)


def _mac_chip() -> str:
    if sys.platform != "darwin":
        return ""
    try:
        chip = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, timeout=2).stdout.strip()
        mem = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True, timeout=2).stdout)
        return f"{chip}, {mem // 2**30} GB memory in total, shared by all programs"
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return ""


class Manager:
    def __init__(self, owner_check, facts: dict[str, str], music, cam, sleeper) -> None:
        """owner_check(cam) -> (ok, score); facts: fixed lines set at start."""
        self._owner_check = owner_check
        self.facts = facts
        self.music, self.cam, self.sleeper = music, cam, sleeper
        self.active = False
        self._saved: list[dict] = []
        self.people = None  # persons.People, set by talk_english

    def status(self, chat) -> str:
        m, sp = self.music, self.music.spotify
        now = sp.now() if sp.active else m.now
        lines = {
            "Computer": f"{sys.platform}, {_mac_chip()}".strip(", "),
            **self.facts,
            "Camera": "on, it locks onto the nearest face" if self.cam is not None else "off",
            "Music folder": f"{len(m.songs())} songs in {m.folder}",
            "Spotify": (
                f"ready, {len(sp.tracks)} songs in {len(sp.lists)} lists, synced {sp.synced[:10]}"
                if sp.ready else "not set up on this computer"
            ),
            "Playing now": now or "nothing",
            "People remembered": (
                f"{self.people.count()} people said yes and are saved in persons/ "
                "(face features, a face photo, name, notes); only with their yes; "
                "'forget me' deletes a person" if self.people is not None else "off (no camera)"
            ),
            "Sleep": (
                f"after {self.sleeper.idle_s:.0f} seconds with no face and no talk the brain "
                "and the ears are unloaded; a face wakes them" if self.sleeper.idle_s > 0 else "off"
            ),
            "Commands (his tools)": (
                "play music, play an artist, song or playlist, next song, what's playing, "
                "stop the music; update personality start (owner only: face and secret word); "
                "management mode and exit management mode; forget me (deletes that person); go to sleep (brain off, camera "
                "paused, only wake up wakes him) and wake up; goodbye or shut down quits. "
                "He cannot search the internet, set timers or control other things."
            ),
            "Conversation before this mode": f"{len(self._saved) // 2} exchanges",
            "Personality (personality.md, changed by voice)": load_character(),
            "Fixed rules (talk_english.py, cannot be changed by voice)": (
                "one or two short sentences under 25 words, plain English, never pretend to play "
                "music or search, describe only what the camera clearly shows"
            ),
        }
        return "\n".join(f"- {k}: {v}" for k, v in lines.items())

    def wants_change(self, chat, text: str) -> bool:
        """A wish to change him, not a question? A live session took "say
        something funny about drugs" as an order and performed it here."""
        try:
            word = chat.complete(KIND, text).strip().upper()
        except Exception as exc:  # noqa: BLE001 — treat as a question
            print(f"(management: kind check failed: {exc})")
            return False
        print(f"(management: {word[:20]})")
        return word.startswith("CHANGE")

    def enter(self, chat, cam) -> bool:
        if cam is not None:
            ok, score = self._owner_check(cam)
            print(f"(management: owner face check {'match' if ok else 'no match'}, best {score:.2f})")
            if not ok:
                return False
        self._saved = list(chat.history)
        chat.history.clear()
        chat.set_mode(SYSTEM + self.status(chat), sentences=5, tokens=300)
        self.active = True
        return True

    def leave(self, chat) -> None:
        chat.set_mode(None)
        chat.history[:] = self._saved  # in place: MindChat shares this list
        self._saved = []
        self.active = False
