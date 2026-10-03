#!/usr/bin/env python3
"""Talk to WALL-E in Hebrew. Offline. Microphone in, speaker out.

    python3 talk_hebrew.py --auto

Camera window: green box is the talker. A locked face plus loud mic
starts a recording (mouth motion on this camera is too weak to wait on).
A face with no sound is ignored. q quits the window.

    python3 talk_hebrew.py --auto --no-camera
    python3 talk_hebrew.py --type
    python3 talk_hebrew.py --auto --thinking --turbo   # reasoning chat + fast STT
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import threading
import urllib.request
import time
from pathlib import Path

from hebrew_voice import STT_DIR, STT_TURBO_DIR, Voice
from perception import Person
from speaker_lock import SpeakerLock
from usb_camera import UsbCamera

MODELS = Path(__file__).resolve().parent / "models"
CHAT_DIR = MODELS / "chat"
CHAT_REPO = "ssdataanalysis/DictaLM-3.0-1.7B-Instruct-mlx-8Bit"
# Same DictaLM 1.7B as GGUF, for llama.cpp on the XPS's NVIDIA GPU. Q4_K_M is
# ~1.1 GB, so it fits next to Whisper in the 3050 Ti's 4 GB. Q8 does not.
GGUF_DIR = MODELS / "chat-gguf"
GGUF_REPO = "EMD123/DictaLM-3.0-1.7B-Instruct-Q4_K_M-GGUF"
GGUF_FILE = "dictalm-3.0-1.7b-instruct-q4_k_m.gguf"
# The reasoning variant, same size. Its template always opens <think>, so
# every answer costs a thinking pass first; THINK_BUDGET caps it.
THINK_GGUF_REPO = "dicta-il/DictaLM-3.0-1.7B-Thinking-GGUF"
THINK_GGUF_FILE = "DictaLM-3.0-1.7B-Thinking-Q4_K_M.gguf"
THINK_BUDGET = 256  # tokens, ~4 s on the 3050 Ti at ~68 tok/s
LLAMA_SERVER = MODELS / "llama-cpp" / (
    "llama-server.exe" if sys.platform == "win32" else "llama-server"
)
LLAMA_PORT = 8089
FALLBACK = "ווה? לא הבנתי. תגיד שוב?"

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


def _stale(text: str, recent: list[str]) -> bool:
    """True if text repeats a recent answer, ignoring the first word
    (he echoes the greeting: "הלו! אני כאן..." / "בשמחה! אני כאן...")."""
    def tail(s: str) -> str:
        parts = s.split(None, 1)
        return parts[1] if len(parts) > 1 else s

    return any(tail(text) == tail(r) for r in recent)


def ensure_gguf(thinking: bool = False) -> Path:
    repo, name = (THINK_GGUF_REPO, THINK_GGUF_FILE) if thinking else (GGUF_REPO, GGUF_FILE)
    path = GGUF_DIR / name
    if path.exists():
        return path
    print(f"Chat model: {repo}  (~1.1 GB, first time only)")
    from huggingface_hub import hf_hub_download

    GGUF_DIR.mkdir(parents=True, exist_ok=True)
    hf_hub_download(repo_id=repo, filename=name, local_dir=str(GGUF_DIR))
    return path


def start_llama(model: Path, extra: list[str]) -> subprocess.Popen:
    """Start llama-server on LLAMA_PORT and wait until /health answers."""
    if not LLAMA_SERVER.exists():
        sys.exit(f"Missing {LLAMA_SERVER}\nRun: python download_hebrew_voice.py")
    log_path = MODELS / "llama-server.log"
    log = open(log_path, "w", encoding="utf-8")
    server = subprocess.Popen(
        [
            str(LLAMA_SERVER),
            "-m", str(model),
            "--host", "127.0.0.1",
            "--port", str(LLAMA_PORT),
            "-c", "2048",
            "--jinja",  # the chat template inside the GGUF
            *extra,
        ],
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if server.poll() is not None:
            sys.exit(f"llama-server exited. See {log_path}")
        try:
            url = f"http://127.0.0.1:{LLAMA_PORT}/health"
            with urllib.request.urlopen(url, timeout=1) as r:
                if r.status == 200:
                    return server
        except OSError:
            pass
        time.sleep(0.3)
    server.kill()
    sys.exit("llama-server did not come up in 90 s.")


def use_mlx() -> bool:
    """Apple Silicon runs MLX. Everything else (the XPS) runs llama.cpp."""
    if sys.platform != "darwin":
        return False
    try:
        import mlx_lm  # noqa: F401
    except ImportError:
        return False
    return True


class Chat:
    """DictaLM 1.7B. MLX on the Mac, llama.cpp on the GPU everywhere else."""

    def __init__(self, thinking: bool = False) -> None:
        self.history: list[dict[str, str]] = []
        self._server: subprocess.Popen | None = None
        self.thinking = thinking
        print("Loading chat…")
        if use_mlx() and thinking:
            sys.exit("--thinking needs llama.cpp (GGUF); there is no MLX build.")
        if use_mlx():
            from mlx_lm import generate, load

            self.model, self.tokenizer = load(str(ensure_chat()))
            self._generate = generate
            self._backend = "mlx"
        else:
            self._start_llama()
            self._backend = "llama.cpp"
        print(f"Chat on {self._backend}")

    def _start_llama(self) -> None:
        extra = ["-ngl", "99"]  # every layer on the GPU
        if self.thinking:
            # Thoughts go to reasoning_content, not the spoken answer.
            extra += ["--reasoning-format", "deepseek", "--reasoning-budget", str(THINK_BUDGET)]
        self._server = start_llama(ensure_gguf(self.thinking), extra)

    def close(self) -> None:
        if self._server is not None and self._server.poll() is None:
            self._server.terminate()
            try:
                self._server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server.kill()
        self._server = None

    def _raw_reply(
        self, messages: list[dict[str, str]], temperature: float = 0.8
    ) -> str:
        if self._backend == "mlx":
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            return self._generate(
                self.model, self.tokenizer, prompt=prompt, max_tokens=80
            )
        # A 1.7B model copies its own last answers out of the history
        # ("אני כאן, מוכן לפעולה" six times running). The penalties push it off
        # words it has already used.
        params = {
            "messages": messages,
            "max_tokens": 80,
            "temperature": temperature,
            "repeat_penalty": 1.3,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5,
        }
        if self.thinking:
            # max_tokens counts the thoughts too. The penalties would punish
            # the answer for words it already used while thinking. Dicta's
            # card suggests 0.6.
            params = {
                "messages": messages,
                "max_tokens": THINK_BUDGET + 120,
                "temperature": 0.6 if temperature <= 0.8 else 0.9,  # retry: hotter
            }
        body = json.dumps(params).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{LLAMA_PORT}/v1/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        t0 = time.monotonic()
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        msg = data["choices"][0]["message"]
        if self.thinking:
            used = data.get("usage", {}).get("completion_tokens", "?")
            thought = msg.get("reasoning_content") or ""
            print(f"(thought {len(thought)} chars, {used} tokens, {time.monotonic() - t0:.1f} s)")
        return msg.get("content") or ""

    def reply(self, user_text: str) -> str:
        self.history.append({"role": "user", "content": user_text})
        messages = [{"role": "system", "content": SYSTEM}, *self.history[-8:]]
        text = clean_reply(self._raw_reply(messages))
        recent = [
            m["content"] for m in self.history[-7:] if m["role"] == "assistant"
        ]
        if self._backend != "mlx" and _stale(text, recent):
            # Same answer as a recent one: one more try, hotter.
            text = clean_reply(self._raw_reply(messages, temperature=1.1))
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
        self._mouth_t = -1e9  # last time the locked face's lips moved
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

    def lips_moving(self, within_s: float) -> bool | None:
        """Did the locked face's lips move in the last within_s? None when
        there are no lip landmarks (then nothing can be said)."""
        if not self.cam.lips:
            return None
        with self._mu:
            return time.monotonic() - self._mouth_t <= within_s

    def mouth_level(self) -> float | None:
        """Mouth-area motion of the locked face (usb_camera mouth_ema), or None."""
        with self._mu:
            return getattr(self, "mouth_ema", 0.0) if self.speaker_id is not None else None

    def snapshot(self):
        """The latest raw camera frame (no boxes drawn), or None."""
        with self._mu:
            return None if self.frame is None else self.frame.copy()

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
        self._draw_mic(cv2, frame)
        try:
            cv2.imshow("WALL-E speaker lock", frame)
        except cv2.error:
            print("No GUI window. Run in Terminal.app, not SSH.")
            return False
        return (cv2.waitKey(1) & 0xFF) != ord("q")

    def set_mic(self, level: float, thresh: float) -> None:
        self.mic_level = level
        self.mic_thresh = thresh

    def _draw_mic(self, cv2, frame) -> None:
        """Mic bar, bottom left. The white tick is the trigger level."""
        level = getattr(self, "mic_level", 0.0)
        thresh = getattr(self, "mic_thresh", 0.0)
        if thresh <= 0:
            return
        h = frame.shape[0]
        full = 300
        scale = full / (thresh * 3)  # the tick sits a third of the way along
        x0, y0 = 12, h - 40
        loud = level > thresh
        cv2.rectangle(frame, (x0, y0), (x0 + full, y0 + 20), (60, 60, 60), -1)
        cv2.rectangle(
            frame, (x0, y0), (x0 + int(min(level * scale, full)), y0 + 20),
            (0, 255, 0) if loud else (0, 200, 255), -1,
        )
        tx = x0 + int(thresh * scale)
        cv2.line(frame, (tx, y0 - 4), (tx, y0 + 24), (255, 255, 255), 2)
        cv2.putText(
            frame, "MIC: HEARING YOU" if loud else "MIC", (x0 + full + 10, y0 + 17),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if loud else (200, 200, 200), 2,
        )

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
            mouth_ema = 0.0
            if obs:
                sid = obs[0].track_id
                mouth = bool(obs[0].speaking)
                mouth_ema = float(obs[0].mouth_ema)
            with self._mu:
                self.frame = frame
                self.obs = obs
                self.speaker_id = sid
                self.mouth = mouth
                self.mouth_ema = mouth_ema
                if mouth:
                    self._mouth_t = now


def wait_for_mouth(cam: TalkCam | None) -> bool:
    """Wait until the main face is there and someone is loud or the mouth moves."""
    if cam is None:
        return True
    import numpy as np
    import sounddevice as sd

    print("Look at the camera, then speak…")
    sr = 16000
    block = int(sr * 0.1)
    # The trigger follows the room, not a fixed number: a fixed 0.025 suited
    # the Mac's mic but the XPS's Realtek mic never reached it. The floor
    # tracks the quiet level (falls fast, rises slowly), and speech must be
    # 3.5x above it, the same rule record_utterance uses.
    floor: float | None = None
    last_log = 0.0
    with sd.InputStream(samplerate=sr, channels=1, dtype="float32") as stream:
        while True:
            if not cam.pump():
                return False
            data, _overflow = stream.read(block)
            x = np.asarray(data, dtype=np.float32).reshape(-1)
            rms = float(np.sqrt(np.mean(x * x) + 1e-12))
            if floor is None:
                floor = rms
            elif rms < floor:
                floor = 0.7 * floor + 0.3 * rms
            else:
                floor = 0.98 * floor + 0.02 * rms
            thresh = max(0.004, floor * 3.5)
            cam.set_mic(rms, thresh)
            now = time.monotonic()
            if now - last_log > 2.0:
                print(f"mic {rms:.4f}  trigger {thresh:.4f}  face {cam.locked()}")
                last_log = now
            if cam.locked() and (cam.talking() or rms > thresh):
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
                thresh = max(0.004, float(np.median(floors)) * 3.5)
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


def listen(
    cam: TalkCam,
    sr: int = 16000,
    max_s: float = 8.0,
    silence_s: float = 0.8,
    preroll_s: float = 0.5,
):
    """Wait for the locked face to speak, then record it. One mic stream.

    The old wait_for_mouth -> beep -> record_utterance chain closed the mic
    between waiting and recording, so the first word was lost. Worse, the
    recorder took its noise floor from its first 0.5 s, which was the person
    already talking, set the trigger above their own voice and threw the
    clip away ("Heard nothing"). Here the floor is only learned while waiting,
    and the 0.5 s before the trigger is kept.

    Returns (samples, sr), None for nothing heard, or False if q was pressed.
    """
    import collections

    import numpy as np
    import sounddevice as sd

    print("Look at the camera, then speak…")
    block = int(sr * 0.1)
    preroll: collections.deque = collections.deque(maxlen=int(preroll_s / 0.1))
    floor: float | None = None
    thresh = 0.004
    chunks: list = []
    recording = False
    voiced_blocks = 0
    quiet = 0.0
    t0 = 0.0
    last_log = 0.0
    with sd.InputStream(samplerate=sr, channels=1, dtype="float32") as stream:
        while True:
            if not cam.pump():
                return False
            data, _overflow = stream.read(block)
            x = np.asarray(data, dtype=np.float32).reshape(-1).copy()
            rms = float(np.sqrt(np.mean(x * x) + 1e-12))
            loud = rms > thresh
            if not recording:
                # Floor falls fast and rises slowly, so speech barely moves it.
                if floor is None:
                    floor = rms
                elif rms < floor:
                    floor = 0.7 * floor + 0.3 * rms
                else:
                    floor = 0.98 * floor + 0.02 * rms
                thresh = max(0.004, floor * 3.5)
                cam.set_mic(rms, thresh)
                now = time.monotonic()
                if now - last_log > 2.0:
                    print(f"mic {rms:.4f}  trigger {thresh:.4f}  face {cam.locked()}")
                    last_log = now
                preroll.append(x)
                if cam.locked() and (rms > thresh or cam.talking()):
                    print("Speak now…")
                    recording = True
                    chunks = list(preroll)
                    voiced_blocks = 1
                    quiet = 0.0
                    t0 = time.monotonic()
                continue
            # Recording: the trigger level stays frozen at the waiting floor.
            cam.set_mic(rms, thresh)
            chunks.append(x)
            if loud:
                voiced_blocks += 1
                quiet = 0.0
            else:
                quiet += 0.1
            if quiet >= silence_s or time.monotonic() - t0 >= max_s:
                break
    if voiced_blocks < 3:  # under ~0.3 s of sound: a click, not a sentence
        return None
    return np.concatenate(chunks), sr


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
        if cam is None and not auto and not typed:
            try:
                input()
            except EOFError:
                return
        if typed:
            user = input("You:    ").strip()
        else:
            if cam is not None:
                rec = listen(cam)
                if rec is False:
                    return
            else:
                rec = record_utterance(cam=None)
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
    parser.add_argument(
        "--thinking",
        action="store_true",
        help="DictaLM 1.7B Thinking instead of Instruct (llama.cpp only)",
    )
    parser.add_argument(
        "--turbo",
        action="store_true",
        help="Whisper large-v3-turbo instead of large-v3",
    )
    args = parser.parse_args()
    if args.type and args.auto:
        parser.error("use --type or --auto, not both")
    voice = Voice(STT_TURBO_DIR if args.turbo else STT_DIR)
    chat = Chat(thinking=args.thinking)
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
        chat.close()
        if cam is not None:
            cam.stop()


if __name__ == "__main__":
    main()
