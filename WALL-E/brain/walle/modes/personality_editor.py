"""The owner changes WALL-E's soft side by voice, in management mode.

    "management mode"                       -> owner face check (management.py)
    "be more sarcastic" / "stop the drug jokes" / "answers can be longer"
        -> the brain picks the file: the running personality.md, or a rules/
           file (always, english / hebrew, the camera ones), and rewrites it
           with only that change
    he reads back what is added and removed, "yes"
        -> saved (the old file in that folder's history/), active at once
    "no" / "cancel"                         -> nothing changes

Soft rules are the rules/ files: the owner may change anything there. Hard
rules live only in code (sentence limit, filters, owner checks, consent,
tools) and cannot be changed by voice. Outside management mode nobody can
change anything by voice.
"""

from __future__ import annotations

from walle.paths import BRAIN

import re
import shutil
from datetime import datetime
from pathlib import Path

from walle.lang import hebrew, t

ROOT = BRAIN
# One folder per personality and language, personalities/<english|hebrew>/<name>/
# (--personality NAME, the language from --lang): personality.md (who he
# is), examples.md (optional: short example talks in his style), history/
# (backups before each voice update), source/ (e.g. a video transcript it
# was made from; not in git).
PERSONALITIES = ROOT / "personalities"
LANG_DIRS = {"en": "english", "he": "hebrew"}
PERSONALITY = "default"
PERSONALITY_FILE = PERSONALITIES / "english" / PERSONALITY / "personality.md"
HISTORY_DIR = PERSONALITY_FILE.parent / "history"


def folder(lang: str) -> Path:
    return PERSONALITIES / LANG_DIRS[lang]


def available(lang: str = "en") -> list[str]:
    return sorted(d.name for d in folder(lang).iterdir() if (d / "personality.md").exists())


def set_personality(name: str, lang: str = "en") -> None:
    global PERSONALITY, PERSONALITY_FILE, HISTORY_DIR
    PERSONALITY = name
    PERSONALITY_FILE = folder(lang) / name / "personality.md"
    HISTORY_DIR = PERSONALITY_FILE.parent / "history"

CANCEL = re.compile(r"\b(cancel|never\s*mind|forget it|abort|בטל|תבטל|לבטל|עזוב|לא משנה|תשכח מזה)\b", re.I)
YES = re.compile(r"\b(yes|yeah|yep|yup|confirm|confirmed|save it|correct|do it|sure|go ahead|כן|בטח|יאללה|תשמור|שמור|נכון|סבבה|אישור)\b", re.I)
NO = re.compile(r"\b(no|nope|don't|do not|wrong|לא|אל תשמור|טעות)\b", re.I)


MAX_LINES = 8

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


def confirmed(chat, answer: str) -> str:
    """YES / NO / UNCLEAR for the save question."""
    yes, no = bool(YES.search(answer)), bool(NO.search(answer) or CANCEL.search(answer))
    if yes != no:
        return "YES" if yes else "NO"
    if not answer:
        return "UNCLEAR"
    word = _ask(chat, CONFIRM, f"The owner answered: {answer}").strip(" .*").upper()
    return word if word in ("YES", "NO") else "UNCLEAR"


def _strip(text: str) -> list[str]:
    """Lines without HTML comments, headings or blank lines."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]


def load_character() -> str:
    """personality.md for the prompt: comments and headings stripped.
    examples.md, if there, follows line by line as examples of his style."""
    text = PERSONALITY_FILE.read_text(encoding="utf-8") if PERSONALITY_FILE.exists() else ""
    lines = [ln[2:].strip() if ln.startswith("- ") else ln for ln in _strip(text)]
    who = " ".join(lines) or "You are WALL-E, a small, curious robot at a desert festival."
    examples = PERSONALITY_FILE.with_name("examples.md")
    if examples.exists():
        ex = _strip(examples.read_text(encoding="utf-8"))
        if ex:
            who += (
                "\n\nSample lines in your style. Make up new lines like these; never say these exact "
                "lines, and only ever write your own answer, never the other person's line:\n"
                + "\n".join(ex) + "\n\n"
            )
    return who


RULES_FILES = {
    "always": "rules for every language and personality: how he answers, questions back, music, what he cannot do",
    "english": "how he speaks English: length, simple words",
    "hebrew": "how he speaks Hebrew: length, gender, no English",
    "eyes_picture": "what he may say about camera pictures (the brain sees them)",
    "eyes_described": "what he may say about the camera when it comes as words (Hebrew)",
    "eyes_none": "what he may say when he has no camera picture",
}

PICK = (
    "WALL-E is a robot. His owner wants to change how WALL-E behaves. Pick the "
    "one file the change belongs in. PERSONALITY is who WALL-E is: character, "
    "humour, likes, topics, style. The rules are how he must behave in every "
    "personality:\n{rules}\n"
    "How long his answers are, and how simply he speaks, belong in english "
    "(or hebrew), not in PERSONALITY.\n"
    "Answer with one word: PERSONALITY or one of the rule names."
)

REWRITE = (
    "Here is a file that tells WALL-E, a robot, {what}. His owner asked for a "
    "change; speech recognition may have garbled a few words, so read for "
    "meaning. Rewrite the whole file with only that change: add, remove or "
    "reword lines as asked. If a line already talks about the same thing, "
    "change that line instead of adding a new one (for example, a line saying "
    "'one or two sentences' and the change 'up to three sentences': that line "
    "now says 'up to three sentences'). The owner may name a line in other "
    "words ('drugs' for a line about 'herbal remedies'). If no line fits, add "
    "a new line that does what he asked; never return the file unchanged. "
    "Keep everything else word for word, including "
    "<!-- comments --> and # headings. Lines that tell WALL-E something start "
    "with '- ' and talk to him as 'you'. Output only the new file."
)


def _pick_file(chat, request: str) -> tuple[Path, str]:
    from walle.paths import RULES_DIR

    rules = "\n".join(f"{k}: {v}" for k, v in RULES_FILES.items())
    word = _ask(chat, PICK.replace("{rules}", rules), request).strip(" .*").lower()
    if word in RULES_FILES:
        return RULES_DIR / f"{word}.md", f"how to behave ({RULES_FILES[word]})"
    return PERSONALITY_FILE, "who he is (his personality)"


def _bullets(text: str) -> list[str]:
    return [ln[2:].strip() for ln in _strip(text) if ln.startswith("- ")]


def _rewrite(chat, path: Path, what: str, request: str) -> tuple[str, str, list[str], list[str]]:
    """(old text, new text, lines added, lines removed) for this change."""
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    system = REWRITE.replace("{what}", what) + (" New lines in Hebrew." if hebrew() and path == PERSONALITY_FILE else "")
    try:
        new = chat.complete(system, f"The file:\n{old}\n\nThe owner asked: {request}", 1500).strip()
    except Exception as exc:  # noqa: BLE001
        print(f"(editor failed: {exc})")
        new = old
    new = re.sub(r"^```\w*\n|\n```$", "", new).strip() + "\n"
    before, after = _bullets(old), _bullets(new)
    added = [ln for ln in after if ln not in before]
    removed = [ln for ln in before if ln not in after]
    print(f"(editor: {path.relative_to(BRAIN)}: +{len(added)} -{len(removed)})")
    return old, new, added, removed


def update(voice, chat, hear, request: str) -> None:
    """Apply the owner's spoken change to the personality or a rules file:
    read back, save on "yes". Called from management mode only."""
    voice.speak(t("Let me think about that.", "רגע, אני חושב על זה."))
    path, what = _pick_file(chat, request)
    old, new, added, removed = _rewrite(chat, path, what, request)
    if not added and not removed and path != PERSONALITY_FILE:
        # The change was not in that rules file (e.g. "stop the drug jokes"
        # went to rules/always.md, the line is in the personality): try it.
        path, what = PERSONALITY_FILE, "who he is (his personality)"
        old, new, added, removed = _rewrite(chat, path, what, request)
    before, after = _bullets(old), _bullets(new)
    if not added and not removed or len(after) < len(before) // 2:
        # Nothing changed, or most of the file gone: do not trust it.
        voice.speak(t("I couldn't turn that into a change. Nothing changed.", "לא הצלחתי להפוך את זה לשינוי. לא שיניתי כלום."))
        return
    where = t("my personality", "האישיות שלי") if path == PERSONALITY_FILE else t(f"my {path.stem} rules", f"החוקים שלי ({path.stem})")
    voice.speak(t(f"In {where}:", f"ב{where}:"))
    for ln in added:
        voice.speak(t("Add: ", "להוסיף: ") + ln)
    for ln in removed:
        voice.speak(t("Remove: ", "להוריד: ") + ln)
    for _ in range(3):
        voice.speak(t("Should I save this? Say yes or no.", "לשמור את זה? תגיד כן או לא."))
        got = hear()
        if got is False:
            return
        answer = got[0] if got else ""
        verdict = confirmed(chat, answer)
        print(f"(save answer: {answer!r} -> {verdict})")
        if verdict == "YES":
            history = path.parent / "history"
            history.mkdir(parents=True, exist_ok=True)
            backup = history / f"{path.stem}_{datetime.now():%Y-%m-%d_%H%M%S}.md"
            if path.exists():
                shutil.copy2(path, backup)
            path.write_text(new, encoding="utf-8")
            chat.reload_system()
            print(f"(saved {path.relative_to(BRAIN)}; previous version in {backup.name})")
            voice.speak(t("Saved. I feel different already.", "שמרתי. אני כבר מרגיש אחרת."))
            return
        if verdict == "NO":
            voice.speak(t("Okay, nothing changed.", "בסדר, לא שיניתי כלום."))
            return
    voice.speak(t("I didn't get a yes, so nothing changed.", "לא שמעתי כן, אז לא שיניתי כלום."))
