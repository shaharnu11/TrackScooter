#!/usr/bin/env python3
"""Talk to WALL-E in Hebrew. Offline. Microphone in, speaker out.

    python3 talk_hebrew.py --auto

Camera window: green box is the talker. He records only while that mouth
moves. Music with no talking face is ignored. q quits the window.

    python3 talk_hebrew.py --auto --no-camera
    python3 talk_hebrew.py --type
"""

from __future__ import annotations

import argparse
import re
import threading
import time
from pathlib import Path

from hebrew_voice import Voice
from perception import Person
from speaker_lock import SpeakerLock
from usb_camera import UsbCamera

CHAT_DIR = Path(__file__).resolve().parent / "models" / "chat"
CHAT_REPO = "ssdataanalysis/DictaLM-3.0-1.7B-Instruct-mlx-8Bit"

SYSTEM = (
    "אתה וול-אי, רובוט קטן וסקרן מפסטיבל במדבר. "
    "מדבר רק עברית מדוברת. משפט אחד או שניים, קצר, חם, פשוט. "
    "בלי רשימות, בלי כוכביות, בלי מנועים, בלי קוד. "
    "אם לא הבנת, תשאל בעדינות."
)


def ensure_chat() -> Path:
    marker = CHAT_DIR / "config.json"
    if marker.exists():
        return CHAT_DIR
    print(f"Chat model: {CHAT_REPO}  (~1.8 GB, first time only)")
    from huggingface_hub import snapshot_download

    CHAT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=CHAT_REPO, local_dir=str(CHAT_DIR))
    return CHAT_DIR


def strip_nikud(text: str) -> str:
    return re.sub(r"[\u0591-\u05c7]", "", text)


def clean_reply(text: str) -> str:
    t = text.strip()
    for stop in ("<|im_end|>", "<|endoftext|>", "</s>"):
        t = t.split(stop, 1)[0]
    t = t.replace("*", "").replace("#", "").strip()
    t = re.sub(r"(.)\1{5,}", r"\1\1", t)
    parts = re.split(r"(?<=[.!?؟])\s+", t)
    out = " ".join(p.strip() for p in parts[:2] if p.strip())
    return out or t[:160]


class Chat:
    def __init__(self) -> None:
        from mlx_lm import generate, load

        print("Loading chat…")
        self.model, self.tokenizer = load(str(ensure_chat()))
        self._generate = generate
        self.history: list[dict[str, str]] = []

    def reply(self, user_text: str) -> str:
        self.history.append({"role": "user", "content": user_text})
        messages = [{"role": "system", "content": SYSTEM}, *self.history[-8:]]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        raw = self._generate(self.model, self.tokenizer, prompt=prompt, max_tokens=80)
        text = clean_reply(raw)
        if re.search(r"[\u4e00-\u9fff]", text) or not re.search(r"[\u0590-\u05ff]", text):
            text = "ווה? לא הבנתי. תגיד שוב?"
        if not text:
            text = "ווה? לא הבנתי. תגיד שוב?"
        self.history.append({"role": "assistant", "content": text})
        return text


class TalkCam:
    """USB camera + speaker lock. Main thread pumps the window."""

    def __init__(self) -> None:
        self.cam = UsbCamera()
        self.lock = SpeakerLock()
        self._stop = threading.Event()
        self._mu = threading.Lock()
        self.frame = None
        self.obs: list = []
        self.speaker_id: int | None = None
        self.mouth = False
        self.ok = False
        self._thread: threading.Thread | None = None

    def start(self) -> bool:
        if not self.cam.open():
            print(self.cam.last_error or "No camera.")
            return False
        self.cam.max_faces = 1
        self.cam.min_rel_h = 0.08
        self.cam.min_score = 0.55
        self.ok = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"Camera {self.cam.device}. Green box = talker. q quits.")
        return True

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.5)
        self.cam.close()
        try:
            import cv2
            cv2.destroyAllWindows()
        except Exception:
            pass

    def locked(self) -> bool:
        with self._mu:
            return self.speaker_id is not None

    def talking(self) -> bool:
        with self._mu:
            return self.mouth and self.speaker_id is not None

    def pump(self) -> bool:
        """Draw the window. Return False if the user pressed q."""
        if not self.ok:
            return True
        try:
            import cv2
        except ImportError:
            return True
        with self._mu:
            frame = None if self.frame is None else self.frame.copy()
            obs = list(self.obs)
            sid = self.speaker_id
        if frame is None:
            return True
        for o in obs:
            x, y, w, h = o.box
            is_focus = sid is not None and o.track_id == sid
            color = (0, 255, 0) if is_focus else (0, 220, 255)
            thick = 4 if is_focus else 3
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, thick)
            label = "YOU" if is_focus else "FACE"
            if o.speaking:
                label += " talk"
            cv2.putText(
                frame, f"{label}  m={o.mouth_ema:.1f}", (x, max(28, y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2,
            )
        if not obs:
            cv2.putText(
                frame, "NO FACE — come closer, more light, look at camera",
                (12, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
            )
        else:
            status = f"faces {len(obs)}"
            if sid is not None:
                status += f"  lock {sid}"
            cv2.putText(
                frame, status, (12, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2,
            )
        try:
            cv2.imshow("WALL-E speaker lock", frame)
        except cv2.error:
            print("No GUI window. Run in Terminal.app, not SSH.")
            return False
        return (cv2.waitKey(1) & 0xFF) != ord("q")

    def _loop(self) -> None:
        while not self._stop.is_set():
            obs, frame = self.cam.read()
            if frame is None:
                if self._stop.wait(0.03):
                    break
                continue
            people = [
                Person(
                    az_deg=o.az_deg,
                    el_deg=o.el_deg,
                    distance_m=o.distance_m,
                    confidence=o.confidence,
                    track_id=o.track_id,
                    speaking=o.speaking,
                )
                for o in obs
            ]
            now = time.monotonic()
            # One real head: always lock it. Mouth motion is too weak alone
            # (open but still mouth never trips SPEAKER, so he never answers).
            sid = None
            mouth = False
            if obs:
                sid = obs[0].track_id
                mouth = bool(obs[0].speaking)
            with self._mu:
                self.frame = frame
                self.obs = obs
                self.speaker_id = sid
                self.mouth = mouth


def wait_for_mouth(cam: TalkCam | None) -> bool:
    """Wait until the main face is there and someone is loud or the mouth moves."""
    if cam is None:
        return True
    import numpy as np
    import sounddevice as sd

    print("Look at the camera, then speak…")
    sr = 16000
    block = int(sr * 0.1)
    with sd.InputStream(samplerate=sr, channels=1, dtype="float32") as stream:
        while True:
            if not cam.pump():
                return False
            data, _overflow = stream.read(block)
            x = np.asarray(data, dtype=np.float32).reshape(-1)
            rms = float(np.sqrt(np.mean(x * x) + 1e-12))
            if cam.locked() and (cam.talking() or rms > 0.025):
                return True


def record_utterance(
    sr: int = 16000,
    max_s: float = 8.0,
    silence_s: float = 0.7,
    cam: TalkCam | None = None,
):
    import numpy as np
    import sounddevice as sd

    block = int(sr * 0.1)
    chunks: list = []
    voiced = False
    quiet = 0.0
    floors: list[float] = []
    thresh = 0.02
    print("Speak now…")
    beep()
    with sd.InputStream(samplerate=sr, channels=1, dtype="float32") as stream:
        t0 = time.monotonic()
        while True:
            if cam is not None and not cam.pump():
                return None
            data, _overflow = stream.read(block)
            x = np.asarray(data, dtype=np.float32).reshape(-1)
            chunks.append(x.copy())
            rms = float(np.sqrt(np.mean(x * x) + 1e-12))
            if len(floors) < 5:
                floors.append(rms)
                thresh = max(0.015, float(np.median(floors)) * 3.5)
            loud = rms > thresh
            mouth = cam is not None and cam.talking()
            face = cam is None or cam.locked()
            if face and (loud or mouth):
                voiced = True
                quiet = 0.0
            elif voiced:
                quiet += 0.1
                if quiet >= silence_s:
                    break
            if time.monotonic() - t0 >= max_s:
                break
    if not voiced or not chunks:
        return None
    return np.concatenate(chunks), sr


def beep() -> None:
    import numpy as np
    import sounddevice as sd

    sr = 16000
    t = np.linspace(0, 0.12, int(sr * 0.12), False)
    tone = (0.18 * np.sin(2 * np.pi * 880 * t)).astype(np.float32)
    sd.play(tone, sr)
    sd.wait()


def loop(
    voice: Voice,
    chat: Chat,
    typed: bool,
    auto: bool,
    cam: TalkCam | None,
) -> None:
    voice.speak("שלום. אני וול-אי. דבר אלי.")
    print()
    if cam is not None:
        print("Green SPEAKER = he will listen. Ctrl+C or q to quit.")
    elif auto:
        print("Listening. Speak, then go quiet. Ctrl+C to quit.")
    else:
        print("Enter to talk. Ctrl+C to quit.")
    if typed:
        print("Type a line and press Enter.")
    while True:
        if cam is not None:
            if not wait_for_mouth(cam):
                return
        elif not auto and not typed:
            try:
                input()
            except EOFError:
                return
        elif typed:
            try:
                input()
            except EOFError:
                return
        if typed:
            user = input("You:    ").strip()
        else:
            rec = record_utterance(cam=cam)
            if rec is None:
                print("Heard nothing. Try again.")
                continue
            samples, sr = rec
            user = voice.transcribe_samples(samples, sr)
        if not user:
            print("Heard nothing. Try again.")
            continue
        folded = strip_nikud(user)
        if any(w in folded for w in ("ביי", "להתראות", "יאללה ביי")):
            voice.speak("ביי. נעים היה.")
            return
        answer = chat.reply(user)
        voice.speak(answer)
        if cam is None and not auto:
            print("Enter to talk again.")
        else:
            time.sleep(0.4)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--type", action="store_true", help="Type Hebrew instead of using the mic"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Keep listening after each answer. Implied when the camera is on.",
    )
    parser.add_argument(
        "--no-camera",
        action="store_true",
        help="Mic only. Do not open the USB camera.",
    )
    args = parser.parse_args()
    if args.type and args.auto:
        parser.error("use --type or --auto, not both")
    voice = Voice()
    chat = Chat()
    cam: TalkCam | None = None
    if not args.type and not args.no_camera:
        cam = TalkCam()
        if not cam.start():
            cam = None
            print("Camera off. Falling back to mic only.")
            if not args.auto:
                print("Press Enter to talk, or rerun with --auto.")
    auto = args.auto or cam is not None
    try:
        loop(voice, chat, typed=args.type, auto=auto, cam=cam)
    except KeyboardInterrupt:
        print("\nBye.")
    finally:
        if cam is not None:
            cam.stop()


if __name__ == "__main__":
    main()
