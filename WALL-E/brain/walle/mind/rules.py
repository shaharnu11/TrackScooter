"""WALL-E's instructions: the personality (who he is) plus rules/ (how he must behave), in that order."""

from __future__ import annotations

from walle.lang import hebrew
from walle.modes.personality_editor import load_character
from walle.paths import RULES_DIR


def rule(name: str) -> str:
    """One rules/ file as plain sentences (comments and headings dropped)."""
    from walle.modes.personality_editor import _strip

    lines = _strip((RULES_DIR / f"{name}.md").read_text(encoding="utf-8"))
    return " ".join(ln[2:].strip() if ln.startswith("- ") else ln for ln in lines) + " "


def build_system(vision: bool, described: bool = False) -> str:
    """personality (who he is) + rules/ (how he must behave). Re-read each call."""
    eyes = "eyes_described" if described else "eyes_picture" if vision else "eyes_none"
    return load_character() + " " + rule("hebrew" if hebrew() else "english") + rule("always") + rule(eyes)
