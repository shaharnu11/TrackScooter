"""Sleep: unload the brain and Whisper when nobody is around, or when the owner says go to sleep."""

from __future__ import annotations

from walle.mind.chat import LocalChat
from walle.voice.speech import Speech

import threading
import time

from walle.voice.speech import wake_sound


class Sleeper:
    """Take the GPU models off the card when nobody is around.

    On battery the laptop drew 38.8 W with WALL-E idle, 10.4 W of it the GPU
    just holding the brain and Whisper. With nothing loaded Windows can
    switch the NVIDIA chip off. Camera, face lock and music keep running on
    the CPU; a locked face starts the reload (~6-7 s), usually while the
    person is still walking up.
    """

    def __init__(self, voice: Speech, chat: LocalChat, idle_s: float) -> None:
        self.voice, self.chat, self.idle_s = voice, chat, idle_s
        self.awake = True
        self.last = time.monotonic()  # last talk or face
        self._busy: threading.Thread | None = None
        # "Go to sleep": brain off, camera paused, only the mic and Whisper
        # listen, and only "wake up" wakes him (a face does not).
        self.manual = False
        # One sleep or wake at a time. "Wake up" and a face seen a moment
        # later both woke him: two brains started, sleep stopped one, and
        # the other kept its memory.
        self._lock = threading.Lock()

    def touch(self) -> None:
        self.last = time.monotonic()

    def sleep_now(self) -> None:
        self.manual = True  # first: no face can start a wake from here on
        if self._busy is not None:
            self._busy.join()
        with self._lock:
            print("(told to sleep: brain off, camera paused; say wake up)")
            self.chat.sleep()
            self.awake = False

    def wake_now(self) -> None:
        if self._busy is not None:
            self._busy.join()
        self._wake()
        self.manual = False  # last: no face-wake can run beside this one

    def tick(self, face: bool) -> None:
        if self.idle_s <= 0 or self.manual:
            return
        if face:
            self.last = time.monotonic()
        if self._busy is not None and self._busy.is_alive():
            return
        if self.awake and time.monotonic() - self.last > self.idle_s:
            self._run(self._sleep)
        elif not self.awake and face:
            self._run(self._wake)

    def kick(self) -> None:
        """Someone started talking: start waking now, if asleep."""
        if self.manual:
            return
        if not self.awake and (self._busy is None or not self._busy.is_alive()):
            self._run(self._wake)

    def ready(self) -> None:
        """Block until the models are loaded (before Whisper or the brain)."""
        if self.manual:
            self.voice.wake_ears()  # told to sleep: only Whisper, for "wake up"
            self.voice.wait_ears()
            return
        if self._busy is not None:
            self._busy.join()
        if not self.awake:
            self._wake()

    def _run(self, job) -> None:
        self._busy = threading.Thread(target=job, daemon=True)
        self._busy.start()

    def _sleep(self) -> None:
        with self._lock:
            if not self.awake:
                return
            print(f"(nobody for {self.idle_s:.0f} s: sleeping, models off the GPU)")
            self.chat.sleep()
            self.voice.sleep_ears()
            self.awake = False

    def _wake(self) -> None:
        with self._lock:
            if self.awake:
                return
            t0 = time.monotonic()
            print("(waking up…)")
            wake_sound()
            self.voice.wake_ears()  # Whisper's process loads while the brain does
            self.chat.wake()
            self.voice.wait_ears()
            self.awake = True
            self.touch()
            print(f"(awake in {time.monotonic() - t0:.1f} s)")
