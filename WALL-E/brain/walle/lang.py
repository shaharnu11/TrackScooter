"""WALL-E's language: English or Hebrew, set once at start (--lang).

t(en, he) picks the fixed line to say. Voice commands are matched in both
languages either way, so "management mode" still works in Hebrew mode.
"""

from __future__ import annotations

LANG = "en"


def set_lang(code: str) -> None:
    global LANG
    LANG = code


def hebrew() -> bool:
    return LANG == "he"


def t(en: str, he: str) -> str:
    return he if LANG == "he" else en
