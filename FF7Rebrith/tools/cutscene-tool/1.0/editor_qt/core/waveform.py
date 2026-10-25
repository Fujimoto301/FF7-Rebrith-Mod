"""
Waveforms for the scene mix.

The extraction already renders one mixed `.ogg` per cutscene - voice, music and
SE together - and the editor already plays it. This turns it into something you
can *see*, which is how you find the exact frame a sound starts rather than
scrubbing for it.

The shape of the data is chosen for the thing it has to survive: zooming. A
waveform drawn from raw samples has to re-read the file every time the zoom
changes. Instead the file is reduced once to a fixed-rate envelope - one peak
per 1/`RATE` of a second - and drawing at any zoom is a walk over that array.
At 100 peaks a second a 90-second scene is 9,000 bytes, so the whole thing sits
in memory and the paint path never touches the disk.

ffmpeg does the decoding, which is not a new dependency: the audio pipeline
already requires it for dialogue trimming.
"""

from __future__ import annotations

import array
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional

#: Peaks per second. 100 is a peak every 0.3 of a frame at 30fps - finer than
#: anything a cut can land on, and still tiny.
RATE = 100

#: Decode rate. High enough that a short transient still lands in the envelope,
#: low enough that a 90-second scene decodes in well under a second.
DECODE_HZ = 22050

#: Bump when the cache layout changes so old caches are ignored, not misread.
CACHE_VERSION = 1


@dataclass(frozen=True)
class Waveform:
    """An amplitude envelope: `peaks[i]` covers second `i / rate`."""

    #: 0-255, absolute peak in each bucket
    peaks: List[int]
    rate: int
    #: length of the audio in seconds, from the peak count
    duration: float
    source: str = ""

    @property
    def empty(self) -> bool:
        return not self.peaks

    def slice_for(self, start_s: float, end_s: float, columns: int) -> List[int]:
        """`columns` peaks covering [start_s, end_s) - one per pixel column.

        Reducing by maximum rather than by sampling: a transient one bucket wide
        must not disappear because the zoom level stepped over it. A cut landing
        on a sound you cannot see is the failure this is guarding against.
        """
        if not self.peaks or columns <= 0:
            return []
        n = len(self.peaks)
        a = start_s * self.rate
        b = end_s * self.rate
        step = (b - a) / columns
        out: List[int] = []
        for i in range(columns):
            lo = int(a + i * step)
            hi = int(a + (i + 1) * step)
            if hi <= lo:
                hi = lo + 1
            if hi <= 0 or lo >= n:
                out.append(0)
                continue
            lo = max(0, lo)
            hi = min(n, hi)
            out.append(max(self.peaks[lo:hi]) if hi > lo else 0)
        return out


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _cache_path(audio_path: str, cache_dir: Optional[str]) -> str:
    base = os.path.splitext(os.path.basename(audio_path))[0] + ".peaks.json"
    folder = cache_dir or os.path.join(os.path.dirname(audio_path), ".peaks")
    return os.path.join(folder, base)


def _read_cache(path: str, audio_path: str) -> Optional[Waveform]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            blob = json.load(f)
    except Exception:
        return None
    if blob.get("version") != CACHE_VERSION:
        return None
    # mtime, not a hash: re-rendering a mix is exactly when this must be redone
    if int(blob.get("mtime", -1)) != int(os.path.getmtime(audio_path)):
        return None
    peaks = blob.get("peaks") or []
    rate = blob.get("rate") or RATE
    return Waveform(peaks=peaks, rate=rate, duration=len(peaks) / rate,
                    source=audio_path)


def _write_cache(path: str, audio_path: str, wave: Waveform) -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "version": CACHE_VERSION,
                    "mtime": int(os.path.getmtime(audio_path)),
                    "rate": wave.rate,
                    "peaks": wave.peaks,
                },
                f,
                separators=(",", ":"),
            )
    except Exception:
        pass   # a cache that cannot be written is not an error worth stopping for


def decode_peaks(audio_path: str, rate: int = RATE) -> Waveform:
    """Run ffmpeg and reduce the samples to an envelope. No caching."""
    if not ffmpeg_available():
        raise RuntimeError("ffmpeg is not on PATH")

    proc = subprocess.run(
        [
            "ffmpeg", "-v", "error", "-nostdin",
            "-i", audio_path,
            "-f", "s16le", "-acodec", "pcm_s16le",
            "-ac", "1", "-ar", str(DECODE_HZ),
            "-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "ffmpeg could not decode %s: %s"
            % (os.path.basename(audio_path), proc.stderr.decode("utf-8", "replace")[:200])
        )

    raw = proc.stdout
    samples = array.array("h")
    samples.frombytes(raw[: len(raw) - (len(raw) % samples.itemsize)])

    per_bucket = max(1, DECODE_HZ // rate)
    peaks: List[int] = []
    for i in range(0, len(samples), per_bucket):
        chunk = samples[i:i + per_bucket]
        if not chunk:
            break
        # max(abs) without building a second array: min() catches the negative
        # half, and -32768 has no positive counterpart in int16
        loudest = max(max(chunk), -min(chunk), 0)
        peaks.append(min(255, loudest * 255 // 32767))

    return Waveform(peaks=peaks, rate=rate, duration=len(peaks) / rate,
                    source=audio_path)


def load(audio_path: str, cache_dir: Optional[str] = None,
         rate: int = RATE) -> Optional[Waveform]:
    """Envelope for a file, from cache when it is still valid.

    Returns None when there is nothing to draw - no file, no ffmpeg, or a file
    ffmpeg will not decode. A missing waveform is a missing row, not an error:
    every other part of the editor works without it.
    """
    if not audio_path or not os.path.isfile(audio_path):
        return None

    cache = _cache_path(audio_path, cache_dir)
    cached = _read_cache(cache, audio_path)
    if cached is not None:
        return cached

    try:
        wave = decode_peaks(audio_path, rate=rate)
    except Exception:
        return None
    if wave.empty:
        return None
    _write_cache(cache, audio_path, wave)
    return wave
