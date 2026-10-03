"""Barge-in audio: talk to WALL-E while he talks.

One mic stream and one speaker stream stay open the whole time, with
WebRTC echo cancellation between them (livekit's AudioProcessingModule):
everything Speaker plays is given to it as the reference, and Mic hands on
the mic with that removed. Without it WALL-E hears himself and stops his
own sentence.

Measured on the M4 Max (MacBook speakers and mic, voice at normal level):
WALL-E alone scored as speech in 68% of the mic's blocks, 0% after the
canceller. With a second voice talking over him, that voice stayed (39% of
its blocks, runs up to 0.54 s) and Whisper still read it.

Only what goes through Speaker is cancelled. Music (music.py) and Spotify
play on their own and are not: they stay ducked while he listens or talks.
"""

from __future__ import annotations

import math
import queue
import threading

import numpy as np

OUT_SR = 48000  # speaker
IN_SR = 16000  # mic, what Silero and Whisper want
OUT_FRAME = OUT_SR // 100  # the canceller works in 10 ms frames
IN_FRAME = IN_SR // 100
FADE_S = 0.03  # a stopped sentence fades out this fast: no click


def available() -> bool:
    try:
        from livekit import rtc  # noqa: F401
    except ImportError:
        return False
    return True


class EchoCanceller:
    def __init__(self) -> None:
        from livekit import rtc

        self._rtc = rtc
        # Noise suppression off: Whisper hears the voice as before, only
        # WALL-E's own voice taken out.
        self._apm = rtc.AudioProcessingModule(
            echo_cancellation=True,
            noise_suppression=False,
            high_pass_filter=True,
            auto_gain_control=False,
        )
        self._out = np.zeros(0, np.float32)
        self._in = np.zeros(0, np.float32)

    def close(self) -> None:
        """Free the native canceller now. Left to Python's exit, livekit's
        drop fails ("AssertionError" printed at every quit)."""
        try:
            self._apm._ffi_handle.dispose()
        except Exception:  # noqa: BLE001 — quitting anyway
            pass

    def set_delay(self, seconds: float) -> None:
        self._apm.set_stream_delay_ms(int(seconds * 1000))

    def _frame(self, x: np.ndarray, rate: int):
        pcm = (np.clip(x, -1.0, 1.0) * 32767).astype(np.int16)
        return self._rtc.AudioFrame(pcm.tobytes(), rate, 1, len(pcm))

    def render(self, x: np.ndarray) -> None:
        """What the speaker is playing now (48 kHz): the reference."""
        buf = np.concatenate([self._out, x])
        n = len(buf) // OUT_FRAME * OUT_FRAME
        for i in range(0, n, OUT_FRAME):
            self._apm.process_reverse_stream(self._frame(buf[i : i + OUT_FRAME], OUT_SR))
        self._out = buf[n:]

    def capture(self, x: np.ndarray) -> np.ndarray:
        """Mic audio (16 kHz) in, the same with the echo removed out."""
        buf = np.concatenate([self._in, x])
        n = len(buf) // IN_FRAME * IN_FRAME
        out = []
        for i in range(0, n, IN_FRAME):
            f = self._frame(buf[i : i + IN_FRAME], IN_SR)
            self._apm.process_stream(f)
            out.append(np.frombuffer(f.data, dtype=np.int16).astype(np.float32) / 32767)
        self._in = buf[n:]
        return np.concatenate(out) if out else np.zeros(0, np.float32)


class Speaker:
    """WALL-E's voice. play() queues, wait() blocks until done or stopped."""

    def __init__(self, echo: EchoCanceller) -> None:
        import sounddevice as sd

        self._echo = echo
        self._q: queue.Queue = queue.Queue()
        self._cur: np.ndarray | None = None
        self._pos = 0
        self._lock = threading.Lock()
        self._idle = threading.Event()
        self._idle.set()
        self._stream = sd.OutputStream(
            samplerate=OUT_SR, channels=1, dtype="float32", blocksize=OUT_FRAME, callback=self._callback
        )
        self._stream.start()

    @property
    def latency(self) -> float:
        return float(self._stream.latency)

    @property
    def busy(self) -> bool:
        return not self._idle.is_set()

    def play(self, samples, sr: int) -> None:
        from scipy.signal import resample_poly

        x = np.asarray(samples, dtype=np.float32).reshape(-1)
        if sr != OUT_SR:
            g = math.gcd(OUT_SR, sr)
            x = resample_poly(x, OUT_SR // g, sr // g).astype(np.float32)
        with self._lock:
            self._idle.clear()
            self._q.put(x)

    def wait(self, stop: threading.Event | None = None) -> bool:
        """True when all of it played, False if stop was set (then it fades out)."""
        while not self._idle.wait(0.02):
            if stop is not None and stop.is_set():
                self.stop()
                return False
        return not (stop is not None and stop.is_set())

    def stop(self) -> None:
        with self._lock:
            while True:
                try:
                    self._q.get_nowait()
                except queue.Empty:
                    break
            if self._cur is not None and self._pos < len(self._cur):
                tail = self._cur[self._pos : self._pos + int(FADE_S * OUT_SR)]
                self._cur = tail * np.linspace(1.0, 0.0, len(tail), dtype=np.float32)
                self._pos = 0

    def close(self) -> None:
        self.stop()
        self._stream.stop()
        self._stream.close()

    def _callback(self, outdata, frames, _time, _status) -> None:
        out = np.zeros(frames, dtype=np.float32)
        filled = 0
        with self._lock:
            while filled < frames:
                if self._cur is None or self._pos >= len(self._cur):
                    try:
                        self._cur, self._pos = self._q.get_nowait(), 0
                    except queue.Empty:
                        self._cur = None
                        break
                n = min(frames - filled, len(self._cur) - self._pos)
                out[filled : filled + n] = self._cur[self._pos : self._pos + n]
                self._pos += n
                filled += n
            if (self._cur is None or self._pos >= len(self._cur)) and self._q.empty():
                self._idle.set()
        outdata[:, 0] = out
        self._echo.render(out)


class Mic:
    """The always-on mic, echo removed. read() works like sd.InputStream.read."""

    def __init__(self, echo: EchoCanceller) -> None:
        import sounddevice as sd

        self._echo = echo
        self._q: queue.Queue = queue.Queue(maxsize=500)  # ~15 s of 30 ms blocks
        self._buf = np.zeros(0, np.float32)
        self._overflow = False
        self._stream = sd.InputStream(
            samplerate=IN_SR, channels=1, dtype="float32", blocksize=3 * IN_FRAME, callback=self._callback
        )
        self._stream.start()

    @property
    def latency(self) -> float:
        return float(self._stream.latency)

    def read(self, n: int) -> tuple[np.ndarray, bool]:
        while len(self._buf) < n:
            self._buf = np.concatenate([self._buf, self._q.get()])
        data, self._buf = self._buf[:n], self._buf[n:]
        overflow, self._overflow = self._overflow, False
        return data.reshape(-1, 1), overflow

    def close(self) -> None:
        """Close after Speaker: this also frees the canceller they share."""
        self._stream.stop()
        self._stream.close()
        self._echo.close()

    def _callback(self, indata, _frames, _time, status) -> None:
        clean = self._echo.capture(indata[:, 0].copy())
        try:
            self._q.put_nowait(clean)
        except queue.Full:
            self._overflow = True
        if status.input_overflow:
            self._overflow = True


def open_audio() -> tuple[Speaker, Mic]:
    echo = EchoCanceller()
    speaker = Speaker(echo)
    mic = Mic(echo)
    echo.set_delay(speaker.latency + mic.latency)
    return speaker, mic
