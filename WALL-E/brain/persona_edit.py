"""Shahar updates WALL-E's personality by talking to him.

    "update personality start"   -> face check + secret word
    ...say the changes, as many sentences as you like...
    "update personality finish"  -> WALL-E reads the changes back
    "yes"                        -> saved to personality.md, reloaded at once
    "cancel" at any point        -> nothing changes

Only ever started by that phrase; nobody else's face is checked or kept.
The brain turns the spoken notes into short personality lines; nothing is
filtered, Shahar decides, and hears every line before saying yes. The
answer-style and honesty rules are in talk_english.py (RULES), not here.
"""

from __future__ import annotations

import re
import shutil
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PERSONALITY_FILE = ROOT / "personality.md"
HISTORY_DIR = ROOT / "personality_history"

START = re.compile(r"\b(update|change)\s+(your\s+|my\s+)?personality\W*\s*(start|starts|started|starting|begin)\b", re.I)
FINISH = re.compile(r"\b(update|change)\s+(your\s+|my\s+)?personality\W*\s*(finish|finished|finishing|done|end|ended)\b", re.I)
CANCEL = re.compile(r"\b(cancel|never\s*mind|forget it|abort)\b", re.I)
YES = re.compile(r"\b(yes|yeah|yep|yup|confirm|confirmed|save it|correct|do it|sure|go ahead)\b", re.I)
NO = re.compile(r"\b(no|nope|don't|do not|wrong)\b", re.I)

MAX_LINES = 8
FACE_FRAMES = 6
MAX_FAILS = 3
LOCK_S = 600  # after MAX_FAILS failed checks, refuse for this long

EDITOR = (
    "You edit the personality notes of WALL-E, a small robot at a desert "
    "festival. His owner, Shahar, dictated changes out loud; speech "
    "recognition may have garbled a few words, so read for meaning. Turn the "
    "changes into short personality lines, each on its own line starting "
    "with '- ' and written to WALL-E in the second person ('You love ...'). "
    "Keep everything Shahar asked for, in his meaning; he decides who WALL-E "
    "is and confirms every line before it is saved. Merge repeats, and skip "
    f"anything the current personality already says. At most {MAX_LINES} "
    "lines. Output only the lines, or the single word NONE if nothing is left."
)


def load_character() -> str:
    """personality.md for the prompt: comments and headings stripped."""
    text = PERSONALITY_FILE.read_text(encoding="utf-8") if PERSONALITY_FILE.exists() else ""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    lines = [ln[2:].strip() if ln.startswith("- ") else ln for ln in lines]
    return " ".join(lines) or "You are WALL-E, a small, curious robot at a desert festival."


def _save(lines: list[str]) -> Path:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup = HISTORY_DIR / f"personality_{stamp}.md"
    shutil.copy2(PERSONALITY_FILE, backup)
    with PERSONALITY_FILE.open("a", encoding="utf-8") as f:
        f.write(f"\n## Update {datetime.now():%Y-%m-%d %H:%M}\n\n")
        f.write("\n".join(f"- {ln}" for ln in lines) + "\n")
    return backup


class PersonaEditor:
    def __init__(self, owner) -> None:
        self.owner = owner
        self.fails = 0
        self.locked_until = 0.0

    def _is_shahar(self, cam) -> tuple[bool, float]:
        if cam is None:
            return False, 0.0
        frames = []
        for _ in range(FACE_FRAMES):
            frames.append(cam.snapshot())
            time.sleep(0.25)
        return self.owner.is_owner(frames)

    def _fail(self, voice, why: str) -> None:
        self.fails += 1
        print(f"(personality update refused: {why}; fail {self.fails}/{MAX_FAILS})")
        if self.fails >= MAX_FAILS:
            self.locked_until = time.monotonic() + LOCK_S
            self.fails = 0
        voice.speak("Sorry, only Shahar can change my personality.")

    def session(self, voice, chat, cam, hear) -> None:
        """hear() -> (text, t_stop), None for nothing, or False for quit."""
        if not self.owner.enrolled:
            voice.speak("I don't know my owner yet. Shahar has to run the enroll step first.")
            return
        if time.monotonic() < self.locked_until:
            print("(personality update locked after failed checks)")
            voice.speak("Sorry, only Shahar can change my personality.")
            return

        ok, score = self._is_shahar(cam)
        print(f"(owner face check: {'match' if ok else 'no match'}, best {score:.2f})")
        if not ok:
            self._fail(voice, "face")
            return
        voice.speak("Hi Shahar. What's the secret word?")
        # Whisper mishears a short phrase now and then (a live "holy cow"
        # came out as "Pico"), so three tries count as one attempt.
        for attempt in range(3):
            got = hear()
            if got is False:
                return
            if got and self.owner.secret_ok(got[0]):
                break
            print(f"(secret word not matched: {got[0] if got else 'nothing heard'!r})")
            if attempt < 2:
                voice.speak("I didn't catch that. Say the secret word again.")
        else:
            self._fail(voice, "secret word")
            return
        self.fails = 0

        voice.speak("Okay, I'm listening. Tell me how I should change. "
                    "Say update personality finish when you're done.")
        notes: list[str] = []
        while True:
            got = hear()
            if got is False:
                return
            if not got:
                continue
            text = got[0]
            if CANCEL.search(text):
                voice.speak("Okay, nothing changed.")
                return
            if FINISH.search(text):
                break
            notes.append(text)
            print(f"(personality note {len(notes)}: {text})")
            voice.speak("Got it.")
        if not notes:
            voice.speak("You didn't tell me anything to change. Nothing changed.")
            return

        voice.speak("Let me think about that.")
        current = load_character()
        prompt = "Current personality:\n" + current + "\n\nShahar said:\n" + "\n".join(f"- {n}" for n in notes)
        raw = chat.complete(EDITOR, prompt)
        lines = [ln.strip()[2:].strip() for ln in raw.splitlines() if ln.strip().startswith("- ")][:MAX_LINES]
        if not lines:
            print(f"(personality editor gave nothing usable: {raw!r})")
            voice.speak("I couldn't turn that into changes. Nothing changed.")
            return

        voice.speak(f"Here {'is the change' if len(lines) == 1 else f'are the {len(lines)} changes'}.")
        for i, ln in enumerate(lines, 1):
            voice.speak(f"{i}. {ln}")
        for _ in range(3):
            voice.speak("Should I save this? Say yes or no.")
            got = hear()
            if got is False:
                return
            answer = got[0] if got else ""
            if YES.search(answer) and not NO.search(answer):
                ok, score = self._is_shahar(cam)  # still you at the confirm?
                if not ok:
                    self._fail(voice, f"face at confirm, best {score:.2f}")
                    return
                backup = _save(lines)
                chat.reload_system()
                print(f"(personality saved; previous version in {backup.name})")
                voice.speak("Saved. I feel different already.")
                return
            if NO.search(answer) or CANCEL.search(answer):
                voice.speak("Okay, nothing changed.")
                return
        voice.speak("I didn't get a yes, so nothing changed.")
