#!/usr/bin/env python3
"""Talk to WALL-E in English. Offline. Microphone in, speaker out.

    python3 talk.py --brain 4b      # Qwen3-4B Q4, fast
    python3 talk.py --brain 4b-q5   # Qwen3-4B Q5, a bit sharper
    python3 talk.py --brain 8b      # Qwen3-8B, smarter, slower
    python3 talk.py --brain 4b-vl   # Qwen3-VL-4B: sees the camera
    python3 talk.py --brain 8b-vl   # Qwen3-VL-8B: sees, smarter (the Mac)
    python3 talk.py --brain 30b-vl  # Qwen3-VL-30B-A3B: the Mac's brain (Mac only)
    python3 talk.py --brain 4b-vl --mind cloud   # Claude online,
        # Qwen3-VL-4B only if the connection fails. Needs ANTHROPIC_API_KEY.

Same camera and mic handling as legacy/talk_hebrew.py. q quits the window.

    python3 talk.py --brain 4b --no-camera --auto
    python3 talk.py --brain 4b --type
"""

from __future__ import annotations

from walle.mind.chat import CLOUD_MODEL, CLOUD_PRICES, CloudChat, LocalChat, MindChat
from walle.mind.sleeper import Sleeper

import argparse
import base64
import json
import re
import subprocess
import sys
import threading
import time
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from contextlib import closing

from walle.mind.brains import BRAINS, GGUF_DIR, Brain
from walle.voice.speech import KOKORO_HE_VOICE, KOKORO_VOICE, Speech, chirp, wake_sound
from walle.lang import hebrew, set_lang, t
from walle.mind.llama import LLAMA_PORT, _stale, clean_reply, start_llama
from walle.eyes.talk_cam import TalkCam
from walle.voice.loud_listen import listen, record_utterance
from walle.music.player import MusicPlayer
from walle.people.owner import Owner
from walle.modes.management import CHANGE_LINE as MANAGE_CHANGE_LINE
from walle.modes.management import EXIT as MANAGE_EXIT
from walle.modes.management import START as MANAGE_START
from walle.modes.management import Manager
from walle.people.persons import FORGET, People
from walle.modes import tools
from walle.modes.personality_editor import START as PERSONA_START
from walle.modes.personality_editor import PersonaEditor, load_character
from walle.voice.listen import BLOCK, END_S, Gate, Heard, StreamVAD, listen_vad

MIN_CLIP_SPEECH = 0.5

# Who he is lives in personalities/<lang>/<name>/personality.md (Shahar edits
# it by voice, walle/modes/personality_editor.py). How he must behave is rules/: fixed files,
# added after the personality, so an update cannot drop them.


# Questions that need the eye. Everything else stays text-only and fast.
LOOK = re.compile(
    r"\b(see|seeing|look|looks|looking|watch|camera|picture|image|photo|"
    r"wear|wearing|holding|behind|colou?r|room|glasses|shirt|hair|"
    r"what is this|what's this|how many|"
    # Surroundings: without the picture he invented "grass and trees".
    r"where (are you|are we|you are|we are)|around (you|us|me|here)|"
    r"this place|surround\w*)\b"
    # Hebrew: see, look, camera, picture, wear, hold, colour, shirt, hair,
    # glasses, how many, where are we, around.
    r"|(רואה|רואים|תסתכל|תסתכלי|תראה|מצלמה|תמונה|לובש|לובשת|מחזיק|מחזיקה|"
    r"צבע|חולצה|שיער|משקפיים|כמה אצבעות|איפה אנחנו|מסביב|מה זה)",
    re.IGNORECASE,
)

PEEK_EVERY = 3  # turns between unasked looks through the camera


def gpu_mem() -> str:
    if sys.platform == "darwin":
        return "Apple GPU (Metal), memory shared with the system"
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        return out or "?"
    except OSError:
        return "no nvidia-smi"


def look(cam: TalkCam | None) -> bytes | None:
    """The current camera frame as a 640-wide JPEG, for the vision brain."""
    if cam is None:
        return None
    frame = cam.snapshot()
    if frame is None:
        return None
    import cv2

    h, w = frame.shape[:2]
    if w > 640:
        frame = cv2.resize(frame, (640, int(h * 640 / w)))
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        return None
    print("(looking through the camera)")
    return buf.tobytes()


def vet(rec, vad: StreamVAD, gate: Gate, use_gate: bool, trigger: str):
    """A recording worth sending to Whisper: (samples, sr, heard, t_stop),
    or None. Prints why not."""
    if rec is None:
        print("(too little speech, ignored)")
        return None
    heard = rec if isinstance(rec, Heard) else None
    samples, sr = (heard.samples, heard.sr) if heard else rec
    # Silero's verdict on the whole clip. At home real speech scored
    # 0.96-0.99 and the one empty clip 0.24: below 0.5, skip Whisper
    # (it invents "Thanks for watching!" on noise).
    vad.reset()
    clip = samples[: len(samples) // BLOCK * BLOCK].reshape(-1, BLOCK)
    peak = max((vad(b) for b in clip), default=0.0)
    print(f"(clip {len(samples) / sr:.1f} s, speech score peak {peak:.2f})")
    if peak < MIN_CLIP_SPEECH:
        print("(no speech in clip, ignored)")
        return None
    if heard is not None:
        # A voice while your face is locked is not always yours: a
        # video nearby got answered. Mouth and loudness say whose.
        print(f"(who: {gate.describe(heard)})")
        why = gate.reasons(heard) if use_gate else []
        if why:
            print(f"(someone else talking? {'; '.join(why)}. Ignored)")
            return None
    # The recording ended one end-of-speech pause after the voice did.
    t_stop = time.monotonic() - (END_S if trigger == "speech" else 0.8)
    return samples, sr, heard, t_stop


# "Go to sleep" / "wake up". "I'm going to sleep now" is about the person.
# Hebrew too: "\bלך לישון" does not match "הולך לישון" (I'm going to sleep).
SLEEP = re.compile(r"\b(go to (sleep|bed)|sleep now|sleep mode|take a nap|לך לישון|לכי לישון|תלך לישון|מצב שינה|לך לנוח)\b", re.I)
NOT_SLEEP = re.compile(r"\b(i|i'm|i am|i'll|we|we're|they)\b[^.?!]{0,15}\bgo(ing)? to (sleep|bed)\b", re.I)
WAKE = re.compile(r"\b(wake|get up|good morning|תתעורר|תתעוררי|התעורר|קום|קומי|בוקר טוב)\b", re.I)
BYE = re.compile(r"\b(bye|goodbye|see you|shut ?down|turn yourself off|ביי|להתראות|תכבה את עצמך|כבה את עצמך)\b", re.I)


def _answers_only(parts):
    """Management mode: no question back after the answer. Told not to,
    the brain still ended with "What kind of music do you like?"."""
    for i, part in enumerate(parts):
        if i > 0 and part.rstrip().endswith("?"):
            continue
        yield part


def asleep_heard(user: str, voice, sleeper, cam) -> bool:
    """Told to sleep: True if the sentence was handled here (woken or ignored)."""
    if not sleeper.manual:
        return False
    if WAKE.search(user):
        if cam is not None:
            cam.resume()
        sleeper.wake_now()
        voice.speak(t("I'm awake! Hi again.", "התעוררתי! היי שוב."))
    else:
        print("(asleep: only wake up counts, ignored)")
    return True


# "owner" or "visitor" when there is no camera to tell: typed mode is the
# owner at the keyboard; a voice with no camera is a visitor.
NO_CAMERA_ROLE = "visitor"
PENDING_RESTART: dict[str, str] | None = None  # set by an owner tool; main execs it


def respond(user: str, t_stop: float, voice, chat, cam, music, sleeper, editor, hear, manager=None, people=None) -> bool:
    """Answer one sentence. False when WALL-E should stop (owner's bye, or a restart)."""
    global PENDING_RESTART
    managing = manager is not None and manager.active
    if people is not None and not managing:
        people.before(chat)  # owner, someone new, or someone remembered
    owner = (people.role if people is not None else NO_CAMERA_ROLE) == "owner"
    print(f"(who: {'owner' if owner else 'visitor'})")
    if manager is not None and not manager.active and MANAGE_START.search(user) and not MANAGE_EXIT.search(user):
        if manager.enter(chat, cam):
            voice.speak(t(
                "Management mode. Ask me anything about how I work. Say exit management mode when you're done.",
                "מצב ניהול. תשאל אותי כל דבר על איך אני עובד. כשתסיים, תגיד: צא ממצב ניהול.",
            ))
        else:
            voice.speak(t("Sorry, management mode is only for Shahar.", "סליחה, מצב ניהול רק לשחר."))
        return True
    if manager is not None and manager.active and MANAGE_EXIT.search(user):
        manager.leave(chat)
        voice.speak(t("Okay, back to normal.", "בסדר, חוזר לרגיל."))
        return True
    if (
        manager is not None and manager.active and not PERSONA_START.search(user)
        and manager.wants_change(chat, user)
    ):
        voice.speak(MANAGE_CHANGE_LINE())
        return True
    if SLEEP.search(user) and not NOT_SLEEP.search(user):
        if not owner:  # a visitor cannot switch him off
            voice.speak(t("Sleep? No way, I'm having too much fun!", "לישון? בחיים לא, כיף לי מדי!"))
            return True
        voice.speak(t("Okay, going to sleep. Say wake up to wake me.", "בסדר, הולך לישון. תגיד תתעורר כדי להעיר אותי."))
        sleeper.sleep_now()
        if cam is not None:
            cam.pause()
        return True
    if PERSONA_START.search(user):
        # Shahar only: face + secret word, then the changes, read back,
        # confirmed. Checked only when this phrase is heard.
        music.duck(True)
        editor.session(voice, chat, cam, hear)
        music.duck(False)
        sleeper.touch()
        return True
    if BYE.search(user):
        voice.speak(t("Bye! That was nice.", "ביי! היה כיף."))
        if owner:
            return False  # the owner's bye (or shut down) quits WALL-E
        if people is not None:
            people.end_visit(chat)  # a visitor's bye only ends their talk
        return True
    if people is not None and not managing and FORGET.search(user):
        people.forget(voice, chat)
        return True
    music.duck(True)
    print()
    # Management mode: "what can you play?" is a question, not a command.
    cmd = None if manager is not None and manager.active else music.command(user)
    if cmd is None and owner and not managing:
        # Owner only: the brain may pick a tool; the code runs it (tools.py).
        tool, args = tools.plan(chat, user, "he" if hebrew() else "en")
        if tool != "none":
            try:
                if tools.run(tool, args, voice, chat, hear, people):
                    chat.history += [{"role": "user", "content": user}, {"role": "assistant", "content": f"(did: {tool})"}]
                    return True
            except tools.Restart as r:
                PENDING_RESTART = r.options
                return False
    if cmd is not None:
        # Handled in code, not by the brain; the brain still gets the
        # exchange in its history so "did you like that song?" makes sense.
        print("(music command)")
        if cmd.first is not None:
            cmd.line = cmd.first()  # Spotify: start it, check it plays, then name it
            music.duck(True)  # the new song starts at full volume
        voice.speak_stream(iter([cmd.line]), t_stop)
        if cmd.after is not None:
            cmd.after()
        chat.history += [
            {"role": "user", "content": user},
            {"role": "assistant", "content": cmd.line},
        ]
    else:
        # A picture also comes unasked on the first sentence and every third
        # one, so he can notice things and ask about them (~0.5 s slower then).
        # Not in management mode: there it only answers.
        peek = (manager is None or not manager.active) and len(chat.history) // 2 % PEEK_EVERY == 0
        jpeg = look(cam) if chat.vision and (LOOK.search(user) or peek) else None
        parts = chat.reply_stream(user, jpeg)
        if manager is not None and manager.active:
            parts = _answers_only(parts)
        voice.speak_stream(parts, t_stop)
    if people is not None and not managing and not (voice.interrupt is not None and voice.interrupt.is_set()):
        people.after(voice, chat, hear)  # after a few exchanges: "can I remember you?"
    return True


def loop(
    voice: Speech,
    chat: LocalChat,
    typed: bool,
    auto: bool,
    cam: TalkCam | None,
    music: MusicPlayer,
    sleeper: Sleeper,
    trigger: str = "speech",
    use_gate: bool = True,
    manager: Manager | None = None,
    people: People | None = None,
) -> None:
    voice.speak(t("Hi. I'm WALL-E. Talk to me.", "היי. אני וול-אי. דבר איתי."))
    print(f"Music folder: {music.folder}  ({len(music.songs())} songs)")
    print()
    if cam is not None:
        print("Green SPEAKER = he will listen. Ctrl+C or q to quit.")
    elif auto:
        print("Listening. Speak, then go quiet. Ctrl+C to quit.")
    else:
        print("Enter to talk. Ctrl+C to quit.")
    vad = None if typed else StreamVAD()
    gate = Gate()
    editor = PersonaEditor(Owner())
    print(f"Listening trigger: {trigger}" + ("" if use_gate else " (no mouth/loudness check)"))

    def hear(lang: str | None = None):
        """One sentence from the person in front: (text, t_stop), None when
        there is nothing worth answering, False when q was pressed."""
        if cam is None and not auto and not typed:
            try:
                input()
            except EOFError:
                return False
        if typed:
            try:
                text = input("You:    ").strip()
            except EOFError:
                return False  # input ended (Ctrl+D, or a piped script ran out)
            sleeper.ready()
            return (text, time.monotonic()) if text else None
        if trigger == "speech":
            # Speech-triggered, not loudness-triggered: music and fans pass.
            # The music ducks the moment a voice starts, not after; a
            # sleeping WALL-E starts loading the same moment.
            rec = listen_vad(
                cam,
                vad,
                on_start=lambda: (music.duck(True), sleeper.kick()),
                on_tick=sleeper.tick,
                face_free=lambda: sleeper.manual,
            )
        elif cam is not None:
            rec = listen(cam)  # the old loudness / mouth-motion trigger
        else:
            rec = record_utterance(cam=None)
        if rec is False:
            return False
        got = vet(rec, vad, gate, use_gate and not sleeper.manual, trigger)
        if got is None:
            music.duck(False)
            return None
        samples, sr, heard, t_stop = got
        chirp()
        sleeper.ready()  # asleep: this is where the ~6 s reload is waited out
        t0 = time.monotonic()
        text = voice.transcribe_samples(samples, sr, lang)
        print(f"(stt {time.monotonic() - t0:.1f} s)")
        if not text:
            music.duck(False)
            print("Heard nothing. Try again.")
            return None
        if heard is not None:
            gate.accept(heard)  # learn how loud the person in front sounds
        return text, t_stop

    while True:
        got = hear()
        if got is False:
            return
        if got is None:
            continue
        user, t_stop = got
        if asleep_heard(user, voice, sleeper, cam):
            continue
        if PERSONA_START.search(user):
            respond(user, t_stop, voice, chat, cam, music, sleeper, editor, hear, manager, people)
            continue
        if not respond(user, t_stop, voice, chat, cam, music, sleeper, editor, hear, manager, people):
            return
        music.duck(False)
        sleeper.touch()
        if cam is None and not auto:
            print("Enter to talk again.")
        else:
            time.sleep(0.4)


def loop_barge(
    voice: Speech,
    chat: LocalChat,
    cam: TalkCam | None,
    music: MusicPlayer,
    sleeper: Sleeper,
    use_gate: bool = True,
    use_lips: bool = True,
    manager: Manager | None = None,
    people: People | None = None,
) -> None:
    """Talk over WALL-E: he stops and listens.

    loop() does one thing at a time: while Whisper, the brain and the voice
    worked, the mic was closed and the camera window froze. Here this thread
    listens all the time (mic, speech detector, camera window) and a worker
    thread transcribes, thinks and talks. Speech from the person in front
    while he thinks or talks stops him (Speaker fades out), and the new
    sentence is answered. walle/voice/echo.py keeps his own voice out of the mic.
    """
    import queue

    from walle.voice.echo import open_audio

    speaker, mic = open_audio()
    voice.speaker = speaker
    voice.interrupt = threading.Event()
    clips: queue.Queue = queue.Queue()
    quit_ = threading.Event()
    busy = threading.Event()  # the worker is on a sentence
    recording = threading.Event()  # a voice is being recorded right now
    vad = StreamVAD()
    gate = Gate()
    editor = PersonaEditor(Owner())

    def unduck() -> None:
        if not busy.is_set() and not recording.is_set() and clips.empty():
            music.duck(False)

    def hear(lang: str | None = None):
        """The worker's next sentence: (text, t_stop), None, or False to quit."""
        item = clips.get()
        if item is None:
            return False
        samples, sr, heard, t_stop = item
        voice.interrupt.clear()  # a new sentence: he may talk again
        sleeper.ready()  # asleep: this is where the reload is waited out
        t0 = time.monotonic()
        text = voice.transcribe_samples(samples, sr, lang)
        print(f"(stt {time.monotonic() - t0:.1f} s)")
        if not text:
            print("Heard nothing. Try again.")
            return None
        if heard is not None:
            gate.accept(heard)  # learn how loud the person in front sounds
        return text, t_stop

    def work() -> None:
        try:
            while True:
                got = hear()
                if got is False:
                    return
                if got is None:
                    unduck()
                    continue
                if asleep_heard(got[0], voice, sleeper, cam):
                    continue
                busy.set()
                try:
                    if not respond(*got, voice, chat, cam, music, sleeper, editor, hear, manager, people):
                        quit_.set()
                        return
                finally:
                    busy.clear()
                    sleeper.touch()
                    unduck()
        except BaseException:
            quit_.set()  # a crash in the worker ends the listening too
            raise

    def on_start() -> None:
        recording.set()
        if sleeper.manual:
            return  # asleep: only listening for "wake up"
        music.duck(True)  # under the voice from its first moment
        sleeper.kick()  # a sleeping WALL-E starts loading now
        if busy.is_set():
            print("(you spoke over WALL-E: he stops)")
            voice.interrupt.set()

    voice.speak(t("Hi. I'm WALL-E. Talk to me.", "היי. אני וול-אי. דבר איתי."))
    print(f"Music folder: {music.folder}  ({len(music.songs())} songs)")
    print()
    print("Talk any time, also while he talks. Ctrl+C or q to quit.")
    lips = use_gate and use_lips and cam is not None and cam.cam.lips
    print("Listening trigger: speech, barge-in" + (", moving lips" if lips else "")
          + ("" if use_gate else " (no mouth/loudness check)"))
    worker = threading.Thread(target=work, daemon=True)
    worker.start()
    try:
        while not quit_.is_set():
            rec = listen_vad(
                cam, vad, stream=mic, on_start=on_start, on_tick=sleeper.tick,
                busy=busy.is_set, quit=quit_, need_lips=use_gate and use_lips,
                face_free=lambda: sleeper.manual,
            )
            recording.clear()
            if rec is False:
                break
            got = vet(rec, vad, gate, use_gate and not sleeper.manual, "speech")
            if got is None:
                unduck()
                continue
            chirp()
            clips.put(got)
    finally:
        voice.interrupt.set()  # stop talking
        clips.put(None)
        worker.join(timeout=10)
        speaker.close()
        mic.close()


INSTANCE_PORT = 18088  # held while WALL-E runs: a second start refuses (8088 is a common dev port)


def one_instance():
    """Two WALL-Es ran at once (an old one never quit): two voices, two
    brains. Holding a local port is the lock; the OS frees it on any exit,
    also a crash, on the Mac and on Windows."""
    import socket

    lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        lock.bind(("127.0.0.1", INSTANCE_PORT))
        lock.listen(1)  # listening: the start scripts find this WALL-E by its port
    except OSError:
        sys.exit("WALL-E is already running. Stop it first (Ctrl+C or q in its window).")
    return lock


def main() -> None:
    _lock = one_instance()  # noqa: F841 — kept open until WALL-E exits
    import signal

    # A plain kill (SIGTERM) quits like Ctrl+C: brain and Whisper closed too.
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brain", choices=BRAINS, default="4b", help="Language model")
    parser.add_argument(
        "--personality",
        default="default",
        help="Which personalities/<english|hebrew>/<name>/ to be (by --lang). Default: default",
    )
    parser.add_argument(
        "--lang",
        choices=("en", "he"),
        default="en",
        help="Language he hears and speaks. he (Mac only): ivrit.ai Whisper, Kokoro Hebrew; use --brain dicta-12b",
    )
    parser.add_argument(
        "--type", action="store_true", help="Type English instead of using the mic"
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
        "--trigger",
        choices=("speech", "loud"),
        default="speech",
        help="Start recording on detected speech (default) or on loudness",
    )
    parser.add_argument(
        "--sleep-after",
        type=float,
        default=180,
        help="Seconds with no talk and no face before the models leave the GPU (0 = never)",
    )
    parser.add_argument(
        "--mind",
        choices=("local", "cloud"),
        default="local",
        help="local: the brain on this laptop. cloud: Claude over the internet, "
        "falling back to the local brain when the connection fails",
    )
    parser.add_argument(
        "--cloud-model",
        choices=tuple(CLOUD_PRICES),
        default=CLOUD_MODEL,
        help="Claude model for --mind cloud",
    )
    parser.add_argument(
        "--no-barge-in",
        action="store_true",
        help="One thing at a time: no talking over WALL-E (the Mac's default is barge-in)",
    )
    parser.add_argument(
        "--no-people",
        action="store_true",
        help="Do not offer to remember people (persons/)",
    )
    parser.add_argument(
        "--no-lips",
        action="store_true",
        help="Do not wait for moving lips (the Mac's default: a voice counts only while the lips move)",
    )
    parser.add_argument(
        "--no-gate",
        action="store_true",
        help="Answer every voice, even with a still mouth or from far away",
    )
    args = parser.parse_args()
    set_lang(args.lang)
    from walle.modes.personality_editor import available, set_personality

    if args.personality not in available(args.lang):
        parser.error(f"no {args.lang} personality {args.personality!r}; there are: {', '.join(available(args.lang))}")
    set_personality(args.personality, args.lang)
    print(f"Personality: {args.personality} ({args.lang})")
    if args.lang == "he" and sys.platform != "darwin":
        parser.error("--lang he runs on the Mac only (legacy/talk_hebrew.py is the Windows Hebrew talker)")
    if args.type and args.auto:
        parser.error("use --type or --auto, not both")
    brain = BRAINS[args.brain]
    # Whisper first: --fit on the 8b sizes the model to what is left.
    voice = Speech(whisper=brain.whisper, lang=args.lang)
    if args.mind == "cloud":
        # The local brain is only loaded if the cloud fails; --brain picks it.
        chat = MindChat(CloudChat(args.cloud_model), lambda: LocalChat(brain))
    else:
        chat = LocalChat(brain)
    print(f"GPU memory: {gpu_mem()}")
    cam: TalkCam | None = None
    if not args.type and not args.no_camera:
        cam = TalkCam()
        if not cam.start():
            cam = None
            print("Camera off. Falling back to mic only.")
            if not args.auto:
                print("Press Enter to talk, or rerun with --auto.")
    auto = args.auto or cam is not None
    music = MusicPlayer()
    sleeper = Sleeper(voice, chat, args.sleep_after)
    # Barge-in needs the echo canceller (walle/voice/echo.py). Mac only for now: it was
    # tested there; the XPS keeps the one-thing-at-a-time loop.
    barge = (
        sys.platform == "darwin" and not args.no_barge_in and not args.type
        and args.trigger == "speech" and auto
    )
    if barge:
        from walle.voice.echo import available

        if not available():
            print("No echo canceller (pip install livekit): barge-in off.")
            barge = False
    lips = barge and not args.no_lips and not args.no_gate and cam is not None and cam.cam.lips
    facts = {
        "Brain": (
            f"Claude {args.cloud_model} over the internet; when offline, {brain.file} on this computer"
            if args.mind == "cloud" else f"{brain.file} (--brain {args.brain}) on this computer, offline"
        ) + (", it can see through the camera" if chat.vision else ""),
        "Hearing": f"{getattr(voice, 'ears', 'Whisper')}, Silero speech detector",
        "Voice": (
            f"Kokoro Hebrew text to speech, voice {KOKORO_HE_VOICE}, vowels by Phonikud"
            if hebrew() else f"Kokoro text to speech, voice {KOKORO_VOICE}"
        ),
        "Language": "Hebrew" if hebrew() else "English",
        "Personality": f"{args.personality} (personalities/{'hebrew' if hebrew() else 'english'}/{args.personality}/)",
        "Talking over him (barge-in)": (
            "on: Shahar or a guest can talk while WALL-E talks; WALL-E then stops and listens"
            if barge else "off: WALL-E does not listen while he thinks or talks"
        ),
        "Moving-lips check": "on: a voice counts only while the lips in front move" if lips else "off",
    }
    manager = Manager(PersonaEditor(Owner())._is_shahar, facts, music, cam, sleeper)
    # Who is talking (owner or visitor) needs the camera; remembering people
    # too. Without a camera: typed mode is the owner, a voice is a visitor.
    global NO_CAMERA_ROLE
    NO_CAMERA_ROLE = "owner" if args.type else "visitor"
    people = People(cam, remember=not args.no_people) if cam is not None else None
    manager.people = people if not args.no_people else None
    try:
        if barge:
            loop_barge(
                voice, chat, cam, music, sleeper, use_gate=not args.no_gate,
                use_lips=not args.no_lips, manager=manager, people=people,
            )
        else:
            loop(
                voice, chat, typed=args.type, auto=auto, cam=cam,
                music=music, sleeper=sleeper, trigger=args.trigger, use_gate=not args.no_gate,
                manager=manager, people=people,
            )
    except KeyboardInterrupt:
        print("\nBye.")
    finally:
        music.close()
        chat.close()
        voice.sleep_ears()
        if cam is not None:
            cam.stop()
    if PENDING_RESTART is not None:  # an owner tool asked for another WALL-E
        del _lock  # free the instance lock before the new one takes it
        tools.exec_restart(PENDING_RESTART)


if __name__ == "__main__":
    main()
