"""
Preview audio and the playback clock.

The hard-won behaviour from the browser build is preserved: seeking a media
player is asynchronous, and for a moment afterwards it still reports the OLD
position. Trusting it in that window sends the playhead back where it came
from - at a cut that means seeking past the gap, being told we are still inside
it, and seeking again forever, which stalls playback on the first cut. So the
player is only trusted as the clock once the seek has landed *and* it agrees
with where we think we are.

The clock itself is a QTimer rather than requestAnimationFrame, and the playhead
advances by measured wall time, not by a fixed increment per tick, so a slow
repaint drops position rather than drifting.
"""

from __future__ import annotations

import os
import time
from typing import Optional

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, QUrl, Signal

from ..core.edits import EditState, empty_edits, skip_over
from ..core.waveform import load as load_waveform

try:
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

    HAVE_MULTIMEDIA = True
except ImportError:  # pragma: no cover - Qt built without multimedia
    HAVE_MULTIMEDIA = False

#: How long to ignore the player clock after a seek, in seconds.
SEEK_SETTLE = 0.15


class PreviewAudio(QObject):
    """The mixed VO/BGM/SE preview track for one scene, if one was rendered."""

    state_text = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._player = None
        self._out = None
        self._path: Optional[str] = None
        self._ticks_per_sec = 24000.0
        self._seek_until = 0.0
        self._ready = False

    @property
    def available(self) -> bool:
        return self._player is not None

    def load(self, path: Optional[str], ticks_per_sec: float) -> None:
        self._ticks_per_sec = ticks_per_sec or 24000.0
        self._ready = False
        if not HAVE_MULTIMEDIA:
            self._teardown()
            self.state_text.emit("no audio backend (PySide6-Multimedia missing)")
            return
        if not path or not os.path.isfile(path):
            self._teardown()
            self.state_text.emit("no preview audio for this scene")
            return

        if self._player is None:
            self._player = QMediaPlayer(self)
            self._out = QAudioOutput(self)
            self._out.setVolume(0.9)
            self._player.setAudioOutput(self._out)
            self._player.mediaStatusChanged.connect(self._on_status)
            self._player.errorOccurred.connect(
                lambda _e, msg: self.state_text.emit("audio failed: %s" % msg)
            )
        self._path = path
        self._player.setSource(QUrl.fromLocalFile(path))
        self.state_text.emit("loading audio…")

    def _teardown(self) -> None:
        if self._player is not None:
            self._player.stop()
            self._player.setSource(QUrl())
        self._path = None

    def _on_status(self, status) -> None:
        if not HAVE_MULTIMEDIA:
            return
        if status == QMediaPlayer.LoadedMedia:
            self._ready = True
            self.state_text.emit("audio ready")
        elif status == QMediaPlayer.InvalidMedia:
            self._ready = False
            self.state_text.emit(
                "audio format not supported by the system codecs (%s)"
                % os.path.basename(self._path or "")
            )

    # -- transport ------------------------------------------------------

    def seek(self, t: float) -> None:
        if not self._player:
            return
        self._player.setPosition(int(t / self._ticks_per_sec * 1000))
        self._seek_until = time.monotonic() + SEEK_SETTLE

    def play(self, from_tick: float) -> None:
        if not self._player:
            return
        self.seek(from_tick)
        self._player.play()

    def pause(self) -> None:
        if self._player:
            self._player.pause()

    def set_volume(self, v: float) -> None:
        if self._out:
            self._out.setVolume(max(0.0, min(1.0, v)))

    def set_muted(self, muted: bool) -> None:
        if self._out:
            self._out.setMuted(muted)

    @property
    def muted(self) -> bool:
        return bool(self._out and self._out.isMuted())

    def current_tick(self) -> float:
        if not self._player:
            return 0.0
        return self._player.position() / 1000.0 * self._ticks_per_sec

    def is_clock(self, playhead: float) -> bool:
        """Should the player drive the playhead right now?"""
        if not self._player or not HAVE_MULTIMEDIA:
            return False
        if self._player.playbackState() != QMediaPlayer.PlayingState:
            return False
        if time.monotonic() < self._seek_until:
            return False
        # a failed seek must not drag the playhead somewhere else
        return abs(self.current_tick() - playhead) < self._ticks_per_sec * 0.5


class MixdownLoader(QObject):
    """Re-renders the preview mix off the UI thread as the edit changes.

    Same shape as `WaveformLoader` and for the same reason: the work is a
    second of ffmpeg and numpy, which is short enough to be tempting to do
    inline and long enough to freeze the window every time a cue is dragged.

    Two guards, both learned from the waveform loader. `token` drops a render
    that lands after the user has moved on, so a slow mix for an edit two
    changes ago never replaces a newer one. And the pool is one thread deep -
    ffmpeg parallelises itself, and a queue of one keeps the newest request
    behind at most one stale render rather than behind all of them.
    """

    ready = Signal(object, int)   # MixReport | None, token

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(1)
        self._token = 0
        self._closing = False

    def request(self, cs, state, content_root, cache_dir, lang="US",
                fmt=None) -> int:
        from ..core import mixdown

        self._token += 1
        token = self._token
        if cs is None or not content_root or self._closing:
            self.ready.emit(None, token)
            return token

        loader = self
        want = fmt or mixdown.DRAFT_FORMAT

        class _Job(QRunnable):
            def run(self) -> None:
                try:
                    rep = mixdown.render(cs, state, content_root, cache_dir,
                                         lang, want)
                except Exception:
                    rep = None
                loader._emit(rep, token)

        job = _Job()
        job.setAutoDelete(True)
        self._pool.start(job)
        return token

    def _emit(self, rep, token: int) -> None:
        if not self._closing:
            self.ready.emit(rep, token)

    def shutdown(self) -> None:
        self._closing = True
        self._pool.waitForDone(2000)


class WaveformLoader(QObject):
    """Decodes a scene mix into an envelope without blocking the window.

    First decode of a 50-second mix is about a third of a second - short enough
    to be tempting to do inline, long enough to be felt on every scene change.
    The result is cached to disk, so this usually finishes before the paint that
    would have shown it.

    `token` guards against a slow decode landing after the user has moved on:
    the result is dropped unless it is still the scene being shown.
    """

    ready = Signal(object, int)   # Waveform | None, token

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._pool = QThreadPool(self)
        # one at a time: decoding is ffmpeg's job to parallelise, and a queue
        # of one keeps the newest request behind at most one stale decode
        self._pool.setMaxThreadCount(1)
        self._token = 0
        self._closing = False

    def request(self, audio_path: Optional[str], cache_dir: Optional[str] = None) -> int:
        self._token += 1
        token = self._token
        if not audio_path or self._closing:
            self.ready.emit(None, token)
            return token

        loader = self

        class _Job(QRunnable):
            def run(self) -> None:
                try:
                    wave = load_waveform(audio_path, cache_dir=cache_dir)
                except Exception:
                    wave = None
                loader._emit(wave, token)

        job = _Job()
        job.setAutoDelete(True)
        self._pool.start(job)
        return token

    def _emit(self, wave, token: int) -> None:
        """Emit unless the window has gone.

        A decode outlives the window that asked for it whenever the app is
        closed mid-scene, and emitting into a deleted receiver raises out of the
        worker thread where nothing can catch it usefully.
        """
        if self._closing:
            return
        try:
            self.ready.emit(wave, token)
        except RuntimeError:
            pass   # receiver already destroyed; there is nothing left to tell

    def shutdown(self, wait_ms: int = 2000) -> None:
        """Stop accepting work and let running decodes finish."""
        self._closing = True
        self._pool.clear()
        self._pool.waitForDone(wait_ms)

    def current_token(self) -> int:
        return self._token


class PlaybackClock(QObject):
    """Advances a playhead in ticks, at wall-clock speed - over the joins.

    The clock knows about the edit because playback is meant to be a preview:
    when the playhead walks into a range marked for deletion it steps straight
    out the far side, so Space shows the cut rather than the footage the cut
    removes. `jumped` fires on the way so the audio can be re-seeked to match;
    without that the picture skips and the sound plays on through the gap.
    """

    tick = Signal(float)     # new playhead
    stopped = Signal()
    jumped = Signal(float)   # playhead stepped over a removed span, to this tick

    def __init__(self, interval_ms: int = 16, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._on_tick)
        self._last = 0.0
        self._playhead = 0.0
        self._end = 0.0
        self._ticks_per_sec = 24000.0
        self.audio: Optional[PreviewAudio] = None
        self.edits: EditState = empty_edits()

    @property
    def running(self) -> bool:
        return self._timer.isActive()

    def configure(self, ticks_per_sec: float, end: float) -> None:
        self._ticks_per_sec = ticks_per_sec or 24000.0
        self._end = end

    def start(self, at: float) -> None:
        self._playhead = at
        self._last = time.monotonic()
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()
        self.stopped.emit()

    def set_playhead(self, t: float) -> None:
        self._playhead = t

    def skip_gap(self, t: float) -> float:
        """`t`, moved to the far side of a removed span if it sits inside one."""
        return skip_over(self.edits, t, self._end or None)

    def _on_tick(self) -> None:
        now = time.monotonic()
        dt = now - self._last
        self._last = now

        if self.audio and self.audio.is_clock(self._playhead):
            self._playhead = self.audio.current_tick()
        else:
            self._playhead += dt * self._ticks_per_sec

        # step over the cut before anything else sees the playhead, so no frame
        # is ever drawn from footage the edit removes
        landed = self.skip_gap(self._playhead)
        if landed != self._playhead:
            self._playhead = landed
            self.jumped.emit(landed)

        if self._end and self._playhead >= self._end:
            self._playhead = self._end
            self.tick.emit(self._playhead)
            self.stop()
            return
        self.tick.emit(self._playhead)
