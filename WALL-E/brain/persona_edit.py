"""Shahar updates WALL-E's personality by talking to him.

    "update personality start"   -> face check + secret word
    ...say the changes, as many sentences as you like; he says back each one...
    "that's all" (or any way of saying you are done) -> he reads the changes back
    "yes"                        -> saved to personality.md, reloaded at once
    "cancel" at any point        -> nothing changes

The brain reads each sentence for its meaning (SESSION): a change, done,
cancel, or unclear. A live session got stuck: only the exact words "update
personality finish" ended it, so "let the update finish" and "stop the
update" were saved as personality notes.

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

from lang import hebrew, t

ROOT = Path(__file__).resolve().parent
PERSONALITY_FILE = ROOT / "personality.md"
HISTORY_DIR = ROOT / "personality_history"

START = re.compile(
    r"\b(update|change)\s+(your\s+|my\s+)?personality\W*\s*(start|starts|started|starting|begin)\b"
    r"|(עדכון|עדכן|תעדכן|לעדכן|שינוי|תשנה)\s+(את\s+)?(ה)?אישיות",
    re.I,
)
FINISH = re.compile(r"\b(update|change)\s+(your\s+|my\s+)?personality\W*\s*(finish|finished|finishing|done|end|ended)\b", re.I)
CANCEL = re.compile(r"\b(cancel|never\s*mind|forget it|abort|בטל|תבטל|לבטל|עזוב|לא משנה|תשכח מזה)\b", re.I)
YES = re.compile(r"\b(yes|yeah|yep|yup|confirm|confirmed|save it|correct|do it|sure|go ahead|כן|בטח|יאללה|תשמור|שמור|נכון|סבבה|אישור)\b", re.I)
NO = re.compile(r"\b(no|nope|don't|do not|wrong|לא|אל תשמור|טעות)\b", re.I)

# Exact phrases still work without the brain (and if it fails).
DONE = re.compile(r"\b(that'?s (all|it)|i'?m (done|finished)|we'?re done|(stop|end|finish) the update|זהו|זה הכל|סיימתי|עד כאן|סיום עדכון|סוף עדכון)\b", re.I)
# Talk about the update itself, not about WALL-E: "let the update finish",
# "Wally stop got it and personality" (Whisper's "stop update personality").
# "personality" only counts close to the word: "your personality is cheerful
# and you end every sentence with a beep" is a change.
ABOUT_UPDATE = re.compile(
    r"\bupdate\b.*\b(finish\w*|done|stop\w*|end|ended|over)\b"
    r"|\b(finish\w*|done|stop|end)\b.*\bupdate\b"
    r"|\bpersonality\W+(\w+\W+){0,2}(finish\w*|done|stop\w*|end|ended|over)\b"
    r"|\b(finish\w*|done|stop|end)\W+(\w+\W+){0,3}personality\b",
    re.I,
)

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


SESSION = (
    "You help WALL-E, a small robot, during a personality update. His owner, "
    "Shahar, is dictating changes to WALL-E's personality out loud, one "
    "sentence at a time. Speech recognition may garble words, so read for "
    "meaning. Decide what Shahar's latest sentence means:\n"
    "CHANGE: something about who WALL-E is or how he acts (a trait, a like or "
    "dislike, a way of talking, a fact about himself), even a whole new "
    "personality, or a correction to an earlier change.\n"
    "DONE: Shahar has finished dictating and wants to end, review or save the "
    "update, in any words: 'that's all', 'let the update finish', 'stop the "
    "update', 'finish personality'. A sentence about the update itself, not "
    "about WALL-E, is DONE. A change that only mentions stopping or "
    "finishing ('you never finish your sentences') is a CHANGE.\n"
    "CANCEL: Shahar wants to throw this update away, saving nothing.\n"
    "UNCLEAR: none of these, or too garbled to tell.\n"
    "Answer with one line: the label, ' | ', then for CHANGE what you "
    "understood, said to Shahar by WALL-E in a few words starting with 'I' "
    "('CHANGE | I'll love dancing.'). For the other labels nothing after the bar."
)

CONFIRM = (
    "WALL-E, a small robot, read a list of personality changes to his owner "
    "and asked: should I save this? Speech recognition may garble words. "
    "Answer with one word: YES if the owner agrees to save, NO if he refuses "
    "or wants to throw it away, UNCLEAR otherwise."
)


def _ask(chat, system: str, text: str) -> str:
    """The brain's one-line answer, or "" if it failed (no brain, no cloud)."""
    try:
        return chat.complete(system, text).strip().splitlines()[0].strip()
    except Exception as exc:  # noqa: BLE001 — fall back to the fixed phrases
        print(f"(personality brain failed: {exc})")
        return ""


def understand(chat, text: str, notes: list[str]) -> tuple[str, str]:
    """(CHANGE / DONE / CANCEL / UNCLEAR, what WALL-E understood)."""
    if FINISH.search(text) or DONE.search(text) or ABOUT_UPDATE.search(text):
        return "DONE", ""
    so_far = "\n".join(f"- {n}" for n in notes) or "(none yet)"
    system = SESSION + (" Write the part after the bar in Hebrew, starting with 'אני'." if hebrew() else "")
    raw = _ask(chat, system, f"Changes so far:\n{so_far}\n\nLatest sentence: {text}")
    label, _, said = raw.partition("|")
    # (In Hebrew mode the prompt asks for the part after the bar in Hebrew.)
    label = label.strip().strip("*").upper()
    if label not in ("CHANGE", "DONE", "CANCEL", "UNCLEAR"):
        # No usable answer: the old rules. Cancel words, else a change.
        label = "CANCEL" if CANCEL.search(text) else "CHANGE"
        said = ""
    print(f"(personality brain: {label}{' | ' + said.strip() if said.strip() else ''})")
    return label, said.strip()


def confirmed(chat, answer: str) -> str:
    """YES / NO / UNCLEAR for the save question."""
    yes, no = bool(YES.search(answer)), bool(NO.search(answer) or CANCEL.search(answer))
    if yes != no:
        return "YES" if yes else "NO"
    if not answer:
        return "UNCLEAR"
    word = _ask(chat, CONFIRM, f"The owner answered: {answer}").strip(" .*").upper()
    return word if word in ("YES", "NO") else "UNCLEAR"


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
        voice.speak(t("Sorry, only Shahar can change my personality.", "סליחה, רק שחר יכול לשנות את האישיות שלי."))

    def session(self, voice, chat, cam, hear) -> None:
        """hear() -> (text, t_stop), None for nothing, or False for quit."""
        if not self.owner.enrolled:
            voice.speak(t("I don't know my owner yet. Shahar has to run the enroll step first.", "אני עוד לא מכיר את הבעלים שלי. שחר צריך לעשות רישום קודם."))
            return
        if time.monotonic() < self.locked_until:
            print("(personality update locked after failed checks)")
            voice.speak(t("Sorry, only Shahar can change my personality.", "סליחה, רק שחר יכול לשנות את האישיות שלי."))
            return

        ok, score = self._is_shahar(cam)
        print(f"(owner face check: {'match' if ok else 'no match'}, best {score:.2f})")
        if not ok:
            self._fail(voice, "face")
            return
        voice.speak(t("Hi Shahar. What's the secret word?", "היי שחר. מה מילת הסוד?"))
        # Whisper mishears a short phrase now and then (a live "holy cow"
        # came out as "Pico"), so three tries count as one attempt.
        for attempt in range(3):
            # The secret word is English: Hebrew mode hears it in English.
            got = hear("en")
            if got is False:
                return
            if got and self.owner.secret_ok(got[0]):
                break
            print(f"(secret word not matched: {got[0] if got else 'nothing heard'!r})")
            if attempt < 2:
                voice.speak(t("I didn't catch that. Say the secret word again.", "לא שמעתי. תגיד שוב את מילת הסוד."))
        else:
            self._fail(voice, "secret word")
            return
        self.fails = 0

        voice.speak(t(
            "Okay, I'm listening. Tell me how I should change. Say that's all when you're done.",
            "בסדר, אני מקשיב. תגיד לי איך להשתנות. כשתסיים, תגיד: זהו.",
        ))
        notes: list[str] = []
        while True:
            got = hear()
            if got is False:
                return
            if not got:
                continue
            text = got[0]
            label, said = understand(chat, text, notes)
            if label == "CANCEL":
                voice.speak(t("Okay, nothing changed.", "בסדר, לא שיניתי כלום."))
                return
            if label == "DONE":
                break
            if label == "UNCLEAR":
                voice.speak(t("Sorry, I didn't get that. Say it again, or say that's all.", "סליחה, לא הבנתי. תגיד שוב, או תגיד: זהו."))
                continue
            notes.append(text)
            print(f"(personality note {len(notes)}: {text})")
            got_it = t("Got it.", "הבנתי.")
            voice.speak(f"{got_it} {said}" if said else got_it)
        if not notes:
            voice.speak(t("You didn't tell me anything to change. Nothing changed.", "לא אמרת לי מה לשנות. לא שיניתי כלום."))
            return

        voice.speak(t("Let me think about that.", "רגע, אני חושב על זה."))
        current = load_character()
        prompt = "Current personality:\n" + current + "\n\nShahar said:\n" + "\n".join(f"- {n}" for n in notes)
        # Hebrew mode: lines in Hebrew, so WALL-E can read them back.
        raw = chat.complete(EDITOR + (" Write the lines in Hebrew." if hebrew() else ""), prompt)
        lines = [ln.strip()[2:].strip() for ln in raw.splitlines() if ln.strip().startswith("- ")][:MAX_LINES]
        if not lines:
            print(f"(personality editor gave nothing usable: {raw!r})")
            voice.speak(t("I couldn't turn that into changes. Nothing changed.", "לא הצלחתי להפוך את זה לשינויים. לא שיניתי כלום."))
            return

        voice.speak(t(
            f"Here {'is the change' if len(lines) == 1 else f'are the {len(lines)} changes'}.",
            "הנה השינוי." if len(lines) == 1 else f"הנה {len(lines)} השינויים.",
        ))
        for i, ln in enumerate(lines, 1):
            voice.speak(f"{i}. {ln}")
        for _ in range(3):
            voice.speak(t("Should I save this? Say yes or no.", "לשמור את זה? תגיד כן או לא."))
            got = hear()
            if got is False:
                return
            answer = got[0] if got else ""
            verdict = confirmed(chat, answer)
            print(f"(save answer: {answer!r} -> {verdict})")
            if verdict == "YES":
                ok, score = self._is_shahar(cam)  # still you at the confirm?
                if not ok:
                    self._fail(voice, f"face at confirm, best {score:.2f}")
                    return
                backup = _save(lines)
                chat.reload_system()
                print(f"(personality saved; previous version in {backup.name})")
                voice.speak(t("Saved. I feel different already.", "שמרתי. אני כבר מרגיש אחרת."))
                return
            if verdict == "NO":
                voice.speak(t("Okay, nothing changed.", "בסדר, לא שיניתי כלום."))
                return
        voice.speak(t("I didn't get a yes, so nothing changed.", "לא שמעתי כן, אז לא שיניתי כלום."))
