"""What WALL-E may DO, and for whom.

Everyone (in talk_english.respond, by fixed phrases): talk, music (play,
next, stop, what's playing), a camera look, remember me / forget me, wake
up, and bye (for a visitor it only ends their own talk).

Owner only (Shahar's face in front, lips moving; typed mode counts as the
owner): sleep, quit, management mode, personality update (also needs the
secret word), and the tools below. For an owner sentence the brain picks a
tool (plan); the code checks and runs it. A visitor's sentence never
reaches plan(): the brain cannot act for a visitor at all.

    shell        a zsh command on the Mac; read back, runs only after "yes";
                 blocked: sudo, wiping disks or the home folder; 30 s limit;
                 logged to owner_commands.log
    volume       the Mac's speaker volume
    personality  / language / brain: restart as another WALL-E (~10 s)
    spotify_sync refresh the Spotify song list (needs internet)
    people       list the people remembered, or delete one (after "yes")
"""

from __future__ import annotations

from walle.paths import BRAIN

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from walle.mind.brains import BRAINS
from walle.lang import hebrew, t
from walle.modes.personality_editor import available, confirmed

ROOT = BRAIN
LOG = ROOT / "owner_commands.log"
SHELL_TIMEOUT_S = 30

# Never, even for the owner: no password prompts, nothing that wipes a disk,
# the home folder or the system, nothing that powers the Mac off.
BLOCKED = re.compile(
    r"\bsudo\b|\bsu\s|\bdiskutil\s+(erase|partition|zero|secure)|\bmkfs|\bdd\s+if=|\bcsrutil\b"
    r"|\brm\s+(-\w*\s+)*(/|~|\$HOME|/Users)(\s|/?$)|\b(shutdown|reboot|halt)\b|:\(\)\s*\{",
    re.I,
)

PLAN = (
    "You decide if Shahar, the owner, is asking WALL-E (a robot running on his "
    "Mac) to DO something with one of these tools, or just talking.\n"
    "Tools:\n"
    '- volume {"level": 0-100}: set the Mac speaker volume.\n'
    '- personality {"name": "..."}: become another personality. Names: {names}.\n'
    '- language {"lang": "en" or "he"}: switch the language he speaks.\n'
    '- brain {"key": "..."}: switch the brain. Keys: {brains}.\n'
    '- spotify_sync {}: refresh the Spotify song list.\n'
    '- people {"action": "list"} or {"action": "delete", "name": "..."}: the '
    "people WALL-E remembers.\n"
    "- none {}: he is chatting, asking a question, or asking for music.\n"
    'Answer with JSON only, like {"tool": "volume", "args": {"level": 40}}.'
)


class Restart(Exception):
    """Become another WALL-E: talk_english.main restarts with these options."""

    def __init__(self, options: dict[str, str]) -> None:
        super().__init__(str(options))
        self.options = options


def plan(chat, text: str, lang: str) -> tuple[str, dict]:
    """The owner's sentence as (tool, args); ("none", {}) when it is talk."""
    system = (
        PLAN.replace("{names}", ", ".join(available(lang)))
        .replace("{brains}", ", ".join(BRAINS))
    )
    try:
        raw = chat.complete(system, text)
        m = re.search(r"\{.*\}", raw, re.S)
        data = json.loads(m.group(0)) if m else {}
    except Exception as exc:  # noqa: BLE001 — no plan: just talk
        print(f"(tools: plan failed: {exc})")
        return "none", {}
    tool = str(data.get("tool", "none")).strip().lower()
    args = data.get("args") or {}
    print(f"(tools: {tool} {json.dumps(args, ensure_ascii=False)})")
    return tool, args if isinstance(args, dict) else {}


def run(tool: str, args: dict, voice, chat, hear, people) -> bool:
    """Do it. False when the plan was not a tool after all (then just talk)."""
    if tool == "shell":
        return False  # removed: no Mac commands (it once ran rm -rf on the home folder)
    elif tool == "volume":
        level = max(0, min(100, int(float(args.get("level", 50)))))
        subprocess.run(["osascript", "-e", f"set volume output volume {level}"], check=False)
        voice.speak(t(f"Volume {level}.", f"ווליום {level}."))
    elif tool == "personality":
        name = str(args.get("name", ""))
        if name not in available("he" if hebrew() else "en"):
            voice.speak(t(f"I don't have a personality called {name}.", f"אין לי אישיות בשם {name}."))
            return True
        voice.speak(t(f"Okay, becoming {name}. Back in a few seconds.", f"בסדר, הופך ל{name}. חוזר עוד כמה שניות."))
        raise Restart({"--personality": name})
    elif tool == "language":
        lang = str(args.get("lang", "")).lower()
        if lang not in ("en", "he"):
            return False
        voice.speak(t("Okay, switching language. Back in a few seconds.", "בסדר, מחליף שפה. חוזר עוד כמה שניות."))
        # Each language has its own brain and personalities.
        raise Restart({"--lang": lang, "--brain": "dicta-12b" if lang == "he" else "30b-vl", "--personality": "default"})
    elif tool == "brain":
        key = str(args.get("key", ""))
        if key not in BRAINS:
            voice.speak(t(f"I don't have a brain called {key}.", f"אין לי מוח בשם {key}."))
            return True
        voice.speak(t(f"Okay, switching to {key}. Back in a few seconds.", f"בסדר, עובר ל-{key}. חוזר עוד כמה שניות."))
        raise Restart({"--brain": key})
    elif tool == "spotify_sync":
        voice.speak(t("Syncing Spotify. It takes a minute.", "מסנכרן את ספוטיפיי. זה לוקח דקה."))
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "scripts/spotify_sync.py")], capture_output=True, text=True, timeout=600)
        voice.speak(t("Spotify is synced.", "ספוטיפיי מסונכרן.") if r.returncode == 0 else t("The sync failed.", "הסנכרון נכשל."))
    elif tool == "people" and people is not None:
        _people(args, voice, chat, hear, people)
    else:
        return False
    return True


def _people(args: dict, voice, chat, hear, people) -> None:
    names = [p.name for p in people.known]
    if args.get("action") == "delete":
        name = str(args.get("name", ""))
        hit = next((p for p in people.known if p.name.lower() == name.lower()), None)
        if hit is None:
            voice.speak(t(f"I don't remember anyone called {name}.", f"אני לא זוכר מישהו בשם {name}."))
            return
        voice.speak(t(f"Delete {hit.name}? Say yes or no.", f"למחוק את {hit.name}? תגיד כן או לא."))
        got = hear()
        if got and confirmed(chat, got[0]) == "YES":
            shutil.rmtree(hit.folder)
            people.known.remove(hit)
            voice.speak(t(f"{hit.name} is deleted.", f"{hit.name} נמחק."))
        else:
            voice.speak(t("Okay, I kept them.", "בסדר, השארתי."))
        return
    if not names:
        voice.speak(t("I don't remember anyone yet.", "אני עוד לא זוכר אף אחד."))
    else:
        voice.speak(t(f"I remember {len(names)}: {', '.join(names)}.", f"אני זוכר {len(names)}: {', '.join(names)}."))


def _log(command: str, status: str, out: str) -> None:
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')}  [{status}]  {command}\n")
        if out:
            f.write("    " + out[:500].replace("\n", "\n    ") + "\n")


def restart_argv(argv: list[str], options: dict[str, str]) -> list[str]:
    """argv with these options set (replaced or added)."""
    out = list(argv)
    for opt, val in options.items():
        if opt in out:
            i = out.index(opt)
            out[i + 1 : i + 2] = [val]
        else:
            out += [opt, val]
    return out


def exec_restart(options: dict[str, str]) -> None:
    """Replace this process with WALL-E started with the new options."""
    argv = restart_argv(sys.argv, options)
    print(f"(restarting: {' '.join(argv)})")
    os.execv(sys.executable, [sys.executable, *argv])
