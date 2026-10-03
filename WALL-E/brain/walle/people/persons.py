"""WALL-E remembers people who say he may.

After a few exchanges with someone new he asks: "Can I remember you?" Only
on a yes he asks the name and saves persons/<name>/:

    face.npy    SFace face features (numbers, not a picture), up to 10
    photo_1-4.jpg  4 photos, 0.5 s apart, cropped to the face (nobody in
                the background); each also gives a feature: more angles,
                surer matches next time
    info.json   name, first met, last seen, visits, notes about them

Next time the face matches (the owner check's SFace threshold), the brain
gets the name and the notes, and greets them as an old friend. "Forget me"
deletes the folder. Nobody is saved without a yes; persons/ is not in git
and stays on this computer. Shahar (owner/) is known already, never asked.

Faces are checked once per sentence heard (~3 frames, ~0.1 s), not per
camera frame.
"""

from __future__ import annotations

from walle.paths import BRAIN

import json
import re
import shutil
import time
from datetime import datetime
from pathlib import Path

import numpy as np

from walle.lang import t
from walle.people.owner import SFACE_MATCH, Owner
from walle.modes.personality_editor import confirmed

ROOT = BRAIN
PERSONS_DIR = ROOT / "persons"
ASK_AFTER = 3  # exchanges with someone new before "can I remember you?"
NEW_FACE = 0.25  # below this the face in front is someone else: a new visit
NOTES_EVERY = 4  # exchanges between note updates for a known person
MAX_FEATS = 10
PHOTOS = 4  # photos (and features) taken when someone is first remembered
PHOTO_GAP_S = 0.5

FORGET = re.compile(r"\bforget (me|about me|my face|who i am)\b|(תשכח|תשכחי|שכח|תמחק|תמחקי) אותי", re.I)

NAME = (
    "A robot asked a person for their first name. Speech recognition may "
    "garble words. Answer with the first name only, spelled the usual way "
    "in the language they said it, or NONE if they did not say a name or "
    "refused."
)

NOTES = (
    "Write short notes about the PERSON (not the robot) from this "
    "conversation, for the robot to remember them next time: where they come "
    "from, who they came with, what they like, what they did or plan at the "
    "festival, anything personal they told. Only facts the person said. At "
    "most 5 short lines, each starting with '- '. Merge with the old notes; "
    "newer facts win. Output only the lines."
)


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9\u05d0-\u05ea]+", "-", name.lower()).strip("-") or "person"
    out, n = s, 2
    while (PERSONS_DIR / out).exists():
        out, n = f"{s}-{n}", n + 1
    return out


class Person:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.info = json.loads((folder / "info.json").read_text(encoding="utf-8"))
        self.feats = np.load(folder / "face.npy")

    @property
    def name(self) -> str:
        return self.info["name"]

    def match(self, feat: np.ndarray) -> float:
        return max(_cos(feat, f) for f in self.feats)

    def save(self) -> None:
        np.save(self.folder / "face.npy", self.feats[-MAX_FEATS:])
        (self.folder / "info.json").write_text(json.dumps(self.info, indent=1, ensure_ascii=False), encoding="utf-8")

    def note(self) -> str:
        """For the brain's instructions."""
        when = self.info.get("last_seen", self.info["first_met"])[:10]
        notes = self.info.get("notes", "").strip()
        return (
            f"You are talking to {self.name}, someone you met before (last time "
            f"{when}). Greet them by name like an old friend. "
            + (f"What you remember about them:\n{notes}\n" if notes else "")
        )


class Visit:
    """The person in front now, from the first sentence they said."""

    def __init__(self, feat: np.ndarray) -> None:
        self.feat = feat
        self.person: Person | None = None
        self.owner = False
        self.turns = 0
        self.asked = False


class People:
    """Who is in front, each sentence: the owner or a visitor (tools.py
    decides what each may do); and, with remember on, people who said yes."""

    def __init__(self, cam, remember: bool = True) -> None:
        self.cam = cam
        self.remember = remember
        self._face = Owner()  # its SFace models, and the owner's own face
        PERSONS_DIR.mkdir(exist_ok=True)
        self.known = [Person(d) for d in sorted(PERSONS_DIR.iterdir()) if (d / "info.json").exists()]
        self.visit: Visit | None = None
        print(f"(people: {len(self.known)} remembered)")

    @property
    def role(self) -> str:
        return "owner" if self.visit is not None and self.visit.owner else "visitor"

    def end_visit(self, chat) -> None:
        """A visitor said bye: their talk ends here (WALL-E keeps running)."""
        self._end(chat)
        chat.set_visitor("")

    # ----- who is in front --------------------------------------------------
    def _look(self) -> tuple[np.ndarray | None, list]:
        """Mean face feature over ~3 frames, and the frames."""
        frames, feats = [], []
        for _ in range(3):
            f = self.cam.snapshot()
            if f is not None:
                frames.append(f)
                feat = self._face.feature(f)
                if feat is not None:
                    feats.append(feat)
            time.sleep(0.08)
        return (np.mean(feats, axis=0) if feats else None), frames

    def before(self, chat) -> None:
        """Each sentence heard: same person, or a new visit (and who)."""
        feat, frames = self._look()
        if feat is None:
            return  # no clear face this time: keep the visit as it is
        v = self.visit
        if v is not None and _cos(feat, v.feat) >= NEW_FACE:
            v.feat = 0.8 * v.feat + 0.2 * feat
            return
        self._end(chat)
        v = self.visit = Visit(feat)
        if self._face.faces is not None and max(_cos(feat, f) for f in self._face.faces) >= SFACE_MATCH:
            v.owner = True
            chat.set_visitor("You are talking to Shahar, who built you and owns you.")
            print("(people: Shahar)")
            return
        if not self.remember:
            chat.set_visitor("")
            print("(people: a visitor)")
            return
        best = max(self.known, key=lambda p: p.match(feat), default=None)
        score = best.match(feat) if best is not None else 0.0
        if best is not None and score >= SFACE_MATCH:
            v.person = best
            best.info["visits"] = best.info.get("visits", 1) + 1
            best.info["last_seen"] = datetime.now().isoformat(timespec="minutes")
            best.feats = np.vstack([best.feats, feat])
            best.save()
            chat.set_visitor(best.note())
            print(f"(people: {best.name} again, match {score:.2f})")
        else:
            chat.set_visitor("")
            print(f"(people: someone new, best match {score:.2f})")

    def after(self, voice, chat, hear) -> None:
        """After WALL-E answered: count, maybe ask, maybe update notes."""
        v = self.visit
        if v is None or v.owner or not self.remember:
            return
        v.turns += 1
        if v.person is not None:
            if v.turns % NOTES_EVERY == 0:
                self._update_notes(chat, v.person)
            return
        if v.turns >= ASK_AFTER and not v.asked:
            v.asked = True
            self._ask(voice, chat, hear)

    def forget(self, voice, chat) -> None:
        v = self.visit
        if v is None or v.person is None:
            voice.speak(t("I don't have you saved, so there is nothing to forget.", "אתה לא שמור אצלי, אז אין מה לשכוח."))
            return
        name = v.person.name
        shutil.rmtree(v.person.folder)
        self.known.remove(v.person)
        v.person, v.asked = None, True  # and do not ask again now
        chat.set_visitor("")
        print(f"(people: forgot {name})")
        voice.speak(t(f"Done, {name}. I forgot you.", f"זהו, {name}. שכחתי אותך."))

    def count(self) -> int:
        return len(self.known)

    # ----- remembering ------------------------------------------------------
    def _ask(self, voice, chat, hear) -> None:
        voice.speak(t(
            "Can I remember you, so I know you next time? I would keep your face and name, only on this computer.",
            "אפשר לזכור אותך, כדי שאכיר אותך בפעם הבאה? אשמור את הפנים והשם שלך, רק במחשב הזה.",
        ))
        got = hear()
        if not got or confirmed(chat, got[0]) != "YES":
            print("(people: not remembered)")
            voice.speak(t("No problem.", "אין בעיה."))
            return
        name = ""
        for _ in range(2):
            voice.speak(t("What's your name?", "איך קוראים לך?"))
            got = hear()
            if not got:
                continue
            name = chat.complete(NAME, got[0]).strip().strip(".").split("\n")[0]
            if name and name.upper() != "NONE" and len(name) <= 30:
                break
            name = ""
        if not name:
            voice.speak(t("I didn't get your name. Maybe next time.", "לא הבנתי את השם. אולי בפעם הבאה."))
            return
        voice.speak(t(f"Thanks, {name}. Look at me for two seconds.", f"תודה, {name}. תסתכל עליי שתי שניות."))
        shots = self._photos()
        feats = [self.visit.feat] + [f for _jpg, f in shots]
        folder = PERSONS_DIR / _slug(name)
        folder.mkdir(parents=True)
        np.save(folder / "face.npy", np.array(feats))
        for i, (jpg, _f) in enumerate(shots, 1):
            (folder / f"photo_{i}.jpg").write_bytes(jpg)
        print(f"(people: {len(shots)} photos, {len(feats)} face features)")
        now = datetime.now().isoformat(timespec="minutes")
        (folder / "info.json").write_text(
            json.dumps({"name": name, "first_met": now, "last_seen": now, "visits": 1, "notes": ""}, indent=1),
            encoding="utf-8",
        )
        p = Person(folder)
        self.known.append(p)
        self.visit.person = p
        self._update_notes(chat, p)
        chat.set_visitor(p.note())
        print(f"(people: remembered {name} in {folder.name}/)")
        voice.speak(t(f"Nice to meet you, {name}. I will remember you.", f"נעים להכיר, {name}. אני אזכור אותך."))

    def _photos(self) -> list[tuple[bytes, np.ndarray]]:
        """PHOTOS face crops PHOTO_GAP_S apart, each with its face feature.
        Only frames with a clear face count; up to 3 s in all."""
        import cv2

        det, rec = self._face._models()
        out: list[tuple[bytes, np.ndarray]] = []
        end = time.monotonic() + PHOTOS * PHOTO_GAP_S + 1.0
        while len(out) < PHOTOS and time.monotonic() < end:
            frame = self.cam.snapshot()
            if frame is None:
                time.sleep(0.1)
                continue
            h, w = frame.shape[:2]
            det.setInputSize((w, h))
            _ok, faces = det.detect(frame)
            if faces is None or len(faces) == 0:
                time.sleep(0.1)
                continue
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, bw, bh = [int(v) for v in face[:4]]
            m = int(0.35 * max(bw, bh))
            crop = frame[max(0, y - m) : min(h, y + bh + m), max(0, x - m) : min(w, x + bw + m)]
            ok, buf = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ok:
                out.append((buf.tobytes(), rec.feature(rec.alignCrop(frame, face)).reshape(-1).copy()))
            time.sleep(PHOTO_GAP_S)
        return out

    def _update_notes(self, chat, p: Person) -> None:
        talk = "\n".join(
            f"{'Person' if m['role'] == 'user' else 'Robot'}: {m['content']}"
            for m in chat.history[-12:]
            if isinstance(m.get("content"), str)
        )
        old = p.info.get("notes", "")
        try:
            raw = chat.complete(NOTES, f"Old notes:\n{old or '(none)'}\n\nConversation:\n{talk}")
        except Exception as exc:  # noqa: BLE001 — keep the old notes
            print(f"(people: notes failed: {exc})")
            return
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip().startswith("- ")][:5]
        if lines:
            p.info["notes"] = "\n".join(lines)
            p.save()
            chat.set_visitor(p.note())
            print(f"(people: notes for {p.name}: {' '.join(lines)[:120]})")

    def _end(self, chat) -> None:
        """A visit is over (someone new is in front): last notes, fresh talk."""
        v = self.visit
        if v is not None and v.person is not None and v.turns % NOTES_EVERY:
            self._update_notes(chat, v.person)
        if v is not None:
            chat.history.clear()  # the next person does not inherit this talk
        self.visit = None
