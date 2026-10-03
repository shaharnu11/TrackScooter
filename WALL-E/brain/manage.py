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
    "but keep technical names exactly. Use only the facts below. If the answer is not in them, say you "
    "do not know. When a picture is attached it is the camera view right now; "
    "describe only what is clearly in it.\n\nFacts:\n"
)


def _mac_chip() -> str:
    if sys.platform != "darwin":
        return ""
    try:
        chip = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, timeout=2).stdout.strip()
        mem = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True, timeout=2).stdout)
        return f"{chip}, {mem // 2**30} GB memory"
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
            "Sleep": (
                f"after {self.sleeper.idle_s:.0f} seconds with no face and no talk the brain "
                "and the ears are unloaded; a face wakes them" if self.sleeper.idle_s > 0 else "off"
            ),
            "Commands (his tools)": (
                "play music, play an artist, song or playlist, next song, what's playing, "
                "stop the music; update personality start (owner only: face and secret word); "
                "management mode and exit management mode; goodbye ends the session. "
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
