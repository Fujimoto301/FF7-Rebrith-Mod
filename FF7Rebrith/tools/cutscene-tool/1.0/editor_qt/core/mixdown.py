"""
Preview audio that reflects the edit.

Until now the editor played a mix rendered offline by `audio_build.py`, so
switching a line off or sliding a sound changed the picture and not the sound.
This rebuilds that mix from the same per-cue sources with the current
`EditState` applied, so what you hear is what the build will produce.

What is applied here, and what is not
-------------------------------------
Applied: **disabled cues** are left out, **moved cues** are placed at the tick
they were dragged to, a **trimmed line** is cut to the seconds it keeps, and a
**repointed music trigger** plays the track it was pointed at rather than the
one the scene authored.

*Not* applied: the cuts. That is deliberate and it is not an omission. The mix
stays on the **original** timeline, and `PlaybackClock` already walks the
playhead over each removed span and re-seeks the audio on the way out - the
behaviour `SkipOverCuts` pins down. Rendering the cuts into the file as well
would mean two different clocks disagreeing about where a join is, which is the
class of bug `LESSONS.md` is mostly about. One place skips; this is not it.

What can actually be heard
--------------------------
Only what was exported. Measured over 17 scenes:

=========  =======================================
VO         225 of 225 sources present  (100%)
SE          71 of 367                  (19%)
BGM          4 of 11                   (36%)
=========  =======================================

So a silent SE is usually a missing export, not a broken edit, and the render
reports its coverage so the window can say which it is rather than leaving you
to wonder.

The BGM lookup was simply wrong before
--------------------------------------
`audio_build.bgm_path` searches the BGM tree for `<MusicName>.uasset`. A cue
named `bgm_Foree2_009_03` is not an asset: it is **variation 3 of**
`bgm_Foree2_009`, and the extracted variation is
`bgm_Foree2_009_Project/bgm_Foree2_009_003.wav`. The name never matched a file,
which is why every mix ever rendered reported `bgm: 0` and why the preview has
always been silent where the music is.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .cues import event_cue_key
from .edits import EditState, kept_seconds

#: The tool modules (audio_build) live beside editor_qt, not inside it.
_TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _TOOL_DIR not in sys.path:
    sys.path.insert(0, _TOOL_DIR)

#: Output sample rate - matches audio_build so the two mixes are comparable.
SR = 48000

#: Levels carried over from `audio_build.build`, where they were tuned by ear
#: against dialogue. Dialogue is the reference and sits at 1.0.
SE_GAIN = 2.0
BGM_GAIN = 0.35

#: Event groups scanned for sound, and what each contributes.
SE_GROUPS = ("Sound", "ManualSE", "Effect")

#: Bitrate for the keepable render. The offline mixes are 24 kbit voip mono
#: because there are 678 of them and they are only ever dialogue; this one has
#: music in it.
BITRATE = "96k"

#: The automatic preview writes a **WAV**, and that is a measured choice rather
#: than a lazy one. Timed on three scenes, with the decode cache warm:
#:
#:   =============================  =========  =========  =========
#:   step                            8510       8514       GRASE_0010
#:   =============================  =========  =========  =========
#:   mix (numpy)                     0.71s      0.43s      0.44s
#:   encode opus 96k                 0.21s      0.71s      0.67s
#:   encode opus 48k                 0.25s      0.96s      0.69s
#:   write wav                       0.05s      0.11s      0.09s
#:   =============================  =========  =========  =========
#:
#: Two things fall out of that. The encode, not the mixing, is what you wait
#: for on a long scene - and asking Opus for a *lower* bitrate makes it slower,
#: not faster, because it spends more effort deciding what to throw away. So
#: the quick path is not a low-quality encode, it is no encode at all: a WAV is
#: 5-13x faster to write, and higher fidelity into the bargain. It costs disk
#: (5-18 MB against 0.5-2 MB), which is the one resource a local preview cache
#: has to spare.
DRAFT_FORMAT = "wav"
KEEP_FORMAT = "ogg"


@dataclass
class MixReport:
    """What went into the mix, and what could not be found."""

    path: str = ""
    vo: int = 0
    vo_missing: int = 0
    se: int = 0
    se_missing: int = 0
    bgm: int = 0
    bgm_missing: int = 0
    #: cues left out because the edit switched them off
    disabled: int = 0
    #: cues placed somewhere other than their authored tick
    moved: int = 0
    #: music cues playing a track other than the one the scene authored
    repointed: int = 0
    duration: float = 0.0
    cached: bool = False
    #: music cues that could not be resolved, each with the reason. Named
    #: rather than merely counted: a music cue that silently does not play is
    #: the failure that made the preview untrustworthy in the first place.
    unresolved: List[str] = field(default_factory=list)

    def summary(self) -> str:
        bits = ["%d line%s" % (self.vo, "" if self.vo == 1 else "s")]
        if self.se or self.se_missing:
            bits.append("%d/%d SE" % (self.se, self.se + self.se_missing))
        if self.bgm or self.bgm_missing:
            bits.append("%d/%d music" % (self.bgm, self.bgm + self.bgm_missing))
        if self.disabled:
            bits.append("%d off" % self.disabled)
        if self.moved:
            bits.append("%d moved" % self.moved)
        if self.repointed:
            bits.append("%d repointed" % self.repointed)
        if self.unresolved:
            bits.append("no track for " + self.unresolved[0].split(" — ")[0])
        return " · ".join(bits)


@dataclass
class Placement:
    """One sound, and where it goes on the original timeline."""

    kind: str          # 'vo' | 'se' | 'bgm'
    name: str
    tick: float
    gain: float = 1.0
    #: seconds to keep, for a trimmed line or a BGM cut off by the next one
    max_sec: Optional[float] = None
    #: which HCA stream inside a multi-layer bank
    layer: int = 0


# -- finding the sources -------------------------------------------------


def voice_path(content_root: str, area: str, ev: str, name: str,
               lang: str = "US") -> str:
    return os.path.join(content_root, "Sound", "Voice", lang, "Cut", area, ev,
                        name + ".uasset")


def se_path(content_root: str, area: str, ev: str, name: str) -> str:
    return os.path.join(content_root, "Sound", "SE", "Cut", area, ev,
                        name + ".uasset")


#: Where AudioMog is driven from. The folder holding this file is the one it
#: rebuilds, and therefore the one whose `.wav`s are the track.
REBUILD_SETTINGS = "RebuildSettings.json"


@dataclass(frozen=True)
class BgmSource:
    """Where a music cue's audio actually is, or why it could not be found."""

    kind: str = ""          # 'wav' | 'hca' | '' when unresolved
    path: str = ""
    index: int = 0
    why: str = ""           # set only when unresolved

    @property
    def ok(self) -> bool:
        return bool(self.kind)


def project_dir(content_root: str, base: str) -> Optional[str]:
    """The folder AudioMog rebuilds `base` from.

    Normally `Sound/BGM/<base>_Project/`, and for 815 of the 816 extracted
    banks here that is exactly it. One is nested a level deeper -
    `bgm_Foree2_011_Project/bgm_Foree2_011_Project/` - because it was extracted
    a second time into itself, and looking only at the top level found no
    `.wav` for it and fell through to a fallback that played the wrong music.

    So the folder is identified by what is *in* it rather than by its path:
    the one holding `RebuildSettings.json`, shallowest first. `Modded/` is
    skipped - it is a staging area beside the project, not the project, and
    the build rebuilds from the project.
    """
    top = os.path.join(content_root, "Sound", "BGM", base + "_Project")
    if not os.path.isdir(top):
        return None
    best: Optional[Tuple[int, str]] = None
    for cur, dirs, files in os.walk(top):
        dirs[:] = [d for d in dirs if d.lower() != "modded"]
        if REBUILD_SETTINGS in files:
            depth = cur[len(top):].count(os.sep)
            if best is None or depth < best[0]:
                best = (depth, cur)
    return best[1] if best else top


def slice_count(proj: Optional[str]) -> Optional[int]:
    """How many variations the bank actually has, from `RebuildSettings.json`.

    `Originals` is one entry per slice. Note `MaterialsUsed` is *not* the same
    number: across 816 banks, 62 have materials in the hundreds (shared pools),
    and where the two can be told apart the extracted `.wav` is always named by
    **SliceIndex**. So the number in a cue name is a slice, and that is what
    indexes the files.
    """
    if not proj:
        return None
    try:
        with open(os.path.join(proj, REBUILD_SETTINGS), "r", encoding="utf-8") as f:
            return len(json.load(f).get("Originals") or [])
    except Exception:
        return None


def bgm_source(content_root: str, name: str) -> BgmSource:
    """Where a music cue's audio is.

    `bgm_Foree2_009_03` is not an asset name: it is **slice 3 of**
    `bgm_Foree2_009`, extracted by AudioMog as
    `<project>/bgm_Foree2_009_003.wav` - three digits where the cue uses two.
    Searching the BGM tree for `bgm_Foree2_009_03.uasset`, as `audio_build`
    does, can never match anything, which is why every offline mix reports
    `bgm: 0`.

    **There is deliberately no "near enough" fallback.** The first version of
    this used the slice number as an index into the bank's own HCA streams
    whenever the `.wav` was missing, and that is simply a different track:
    `bgm_Foree2_011` holds 7 streams for 9 slices, and `bgm_Foree2_009` holds 4
    for 5, so the two numberings cannot line up even in principle. It played
    confidently wrong music, which is worse than silence - silence you
    investigate, wrong music you mistake for the scene. The one case still
    taken from the asset is a bank with a single slice, where there is nothing
    to pick wrongly.
    """
    root = os.path.join(content_root, "Sound", "BGM")
    if not os.path.isdir(root):
        return BgmSource(why="no Sound/BGM folder")

    def asset(stem: str) -> Optional[str]:
        direct = os.path.join(root, stem + ".uasset")
        if os.path.isfile(direct):
            return direct
        proj = project_dir(content_root, stem)
        nested = os.path.join(proj, stem + ".uasset") if proj else ""
        return nested if nested and os.path.isfile(nested) else None

    # 1. Does the cue name a whole bank? `bgm_Corle_004` looks like "variation
    #    4 of bgm_Corle" and is nothing of the sort - `bgm_Corle_004.uasset` is
    #    a track in its own right, and 101 of the 195 music cues in this game
    #    are that shape. Existence is what tells the two apart, so it has to be
    #    asked FIRST. Splitting first and checking later is a regression I
    #    wrote and then measured: it sent all 101 of them to "unresolved".
    whole = asset(name)
    if whole:
        proj = project_dir(content_root, name)
        wav = os.path.join(proj, "%s_000.wav" % name) if proj else ""
        if wav and os.path.isfile(wav):
            return BgmSource("wav", wav, 0)
        return BgmSource("hca", whole, 0)

    # 2. Otherwise the trailing number is a slice, and the slice is a file.
    m = re.match(r"^(.*?)_(\d+)$", name)
    if not m:
        return BgmSource(why="no asset called %s" % name)
    base, idx = m.group(1), int(m.group(2))

    proj = project_dir(content_root, base)
    n = slice_count(proj)

    if proj:
        wav = os.path.join(proj, "%s_%03d.wav" % (base, idx))
        if os.path.isfile(wav):
            return BgmSource("wav", wav, idx)

    if n is not None and idx >= n:
        return BgmSource(
            why="%s has %d variation%s, and the cue asks for number %d"
                % (base, n, "" if n == 1 else "s", idx))

    # 3. A single-variation bank cannot be got wrong, so it is worth reading
    #    straight out of the asset when nobody has extracted it.
    if n == 1:
        direct = asset(base)
        if direct:
            return BgmSource("hca", direct, 0)

    if proj:
        return BgmSource(
            why="%s_%03d.wav is not in %s — extract it with AudioMog"
                % (base, idx, os.path.basename(proj)))
    return BgmSource(why="nothing extracted for %s" % base)


# -- what the edit says should sound -------------------------------------


#: What the game plays when it means "stop". There is no audio behind these
#: names, so they place nothing - but they still end whatever was playing.
SILENCE_PREFIX = "bgm_silence"


def placements(cs, state: EditState) -> Tuple[List[Placement], int, int, int]:
    """Every sound the edited scene plays, in order.

    `(list, disabled, moved, repointed)`.

    Cue keys are spelled by `cues.event_cue_key`, which is the same spelling
    `EditState.killed`, `.moves` and `.repoints` are stored under - so a cue
    switched off by clicking its block is the same cue that gets left out here,
    and a trigger pointed at another track is the same cue that plays it.
    """
    out: List[Placement] = []
    disabled = moved = repointed = 0
    ticks = cs.time.ticks_per_second

    def resolved(seq: str, e: Dict[str, Any]) -> Optional[float]:
        """The tick this cue fires at now, or None if it is switched off."""
        nonlocal disabled, moved
        key = event_cue_key(seq, e)
        if key and key in state.killed:
            disabled += 1
            return None
        if key and key in state.moves:
            moved += 1
            return state.moves[key].new_tick
        return e.get("tick")

    for e in cs.events("Voice"):
        name = (e.get("props") or {}).get("VoiceName")
        if not name:
            continue
        at = resolved("Voice", e)
        if at is None:
            continue
        full = e.get("duration") or 0.0
        keep = kept_seconds(state, name, full) if full else None
        out.append(Placement("vo", name, at, 1.0,
                             keep if (full and keep < full) else None))

    for seq in SE_GROUPS:
        for e in cs.events(seq):
            name = (e.get("props") or {}).get("SeName")
            if not name:
                continue
            at = resolved(seq, e)
            if at is not None:
                out.append(Placement("se", name, at, SE_GAIN))

    # Music last, so each track can be cut off where the next one starts. A
    # BGM stream runs for minutes; letting two overlap is what makes a music
    # change inaudible, which is precisely the edit this is here to preview.
    #
    # A repointed trigger plays the track it was pointed at. It is looked up
    # BEFORE the silence test, which matters in both directions: pointing a
    # cue at `bgm_silence` has to make the preview stop, and pointing one that
    # was `bgm_silence` at real music has to make it start. Testing the
    # authored name would get both backwards.
    music: List[Placement] = []
    stops: List[float] = []
    for seq in SE_GROUPS:
        for e in cs.events(seq):
            authored = (e.get("props") or {}).get("MusicName")
            if not authored:
                continue
            key = event_cue_key(seq, e)
            r = state.repoints.get(key) if key else None
            if r:
                repointed += 1
            name = r.to if r else authored
            at = resolved(seq, e)
            if at is None:
                continue
            if name.startswith(SILENCE_PREFIX):
                # Nothing to place, but it is still where the previous track
                # ends. Before this, a scene that stops its music halfway
                # played straight through the stop in the preview - and a
                # trigger repointed TO silence would have sounded like nothing
                # had happened at all.
                stops.append(at)
                continue
            music.append(Placement("bgm", name, at, BGM_GAIN))
    music.sort(key=lambda p: p.tick)
    edges = sorted([p.tick for p in music] + stops)
    for p in music:
        later = [t for t in edges if t > p.tick]
        stop = later[0] if later else cs.total
        p.max_sec = max(0.1, (stop - p.tick) / ticks)
    out.extend(music)

    out.sort(key=lambda p: p.tick)
    return out, disabled, moved, repointed


# -- rendering -----------------------------------------------------------


def _decode_cache() -> Dict[str, Optional[bytes]]:
    if not hasattr(_decode_cache, "store"):
        _decode_cache.store = {}
    return _decode_cache.store


def _decode(kind: str, path: str, layer: int, max_sec: Optional[float]) -> Optional[bytes]:
    """s16le mono PCM at SR, memoised per (file, layer).

    Memoising matters more than it looks: a re-render after every edit would
    otherwise shell out to ffmpeg once per cue, and a scene with twenty sounds
    would take seconds to hear. `max_sec` is applied after decoding rather than
    passed to ffmpeg so the cache holds one entry per file rather than one per
    requested length.
    """
    import audio_build

    key = "%s|%s|%d" % (kind, path, layer)
    store = _decode_cache()
    if key not in store:
        try:
            if kind == "wav":
                r = subprocess.run(
                    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path,
                     "-ac", "1", "-ar", str(SR), "-f", "s16le", "pipe:1"],
                    capture_output=True)
                store[key] = r.stdout if r.returncode == 0 and r.stdout else None
            else:
                raw = open(path, "rb").read()
                store[key] = audio_build.decode_stream(raw, layer=layer)
        except Exception:
            store[key] = None
    pcm = store[key]
    if pcm is not None and max_sec:
        want = int(max_sec * SR) * 2
        if want < len(pcm):
            pcm = pcm[:want]
    return pcm


def edit_fingerprint(cs, state: EditState, lang: str) -> str:
    """A stable name for "this scene, edited this way".

    Only the things the mix depends on go in. Cuts are excluded on purpose:
    they are applied by the clock, not by the file, so adding one must not
    throw away a render that is still perfectly good.
    """
    payload = {
        "ev": cs.name,
        "lang": lang,
        "killed": sorted(state.killed),
        "moves": sorted((k, m.new_tick) for k, m in state.moves.items()),
        "trims": sorted(state.trims.items()),
        # A repoint changes which audio goes into the file, so it has to change
        # the file's name too - otherwise the first render of this scene is
        # served back from the cache and the preview keeps playing the track
        # you just replaced.
        "repoints": sorted((k, r.to) for k, r in state.repoints.items()),
    }
    blob = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha1(blob).hexdigest()[:16]


def render(cs, state: EditState, content_root: Optional[str], cache_dir: str,
           lang: str = "US", fmt: str = DRAFT_FORMAT) -> Optional[MixReport]:
    """Build (or reuse) the preview mix for this scene and edit.

    `fmt` is `'wav'` for the automatic preview and `'ogg'` for the keepable
    render - see `DRAFT_FORMAT` for why the quick one is uncompressed.

    Returns None when there is nothing to render - no Content folder, no numpy,
    or a scene with no placeable sound at all. A missing mix is a missing mix,
    not an error: the window falls back to the offline `.ogg`.
    """
    if not content_root or not cs.area:
        return None
    try:
        import numpy as np
    except ImportError:
        return None

    os.makedirs(cache_dir, exist_ok=True)
    stamp = edit_fingerprint(cs, state, lang)
    out_path = os.path.join(cache_dir, "%s_%s.%s" % (cs.name, stamp, fmt))

    items, disabled, moved, repointed = placements(cs, state)
    report = MixReport(path=out_path, disabled=disabled, moved=moved,
                       repointed=repointed)

    if os.path.isfile(out_path):
        # Counting is cheap and the file is already there; recounting keeps the
        # status line honest instead of blanking it on a cache hit.
        report.cached = True

    ticks = cs.time.ticks_per_second
    total_samples = int(cs.total / ticks * SR) + SR      # +1s tail
    mix = None if report.cached else np.zeros(total_samples, dtype=np.int32)

    for p in items:
        if p.kind == "vo":
            path = voice_path(content_root, cs.area, cs.name, p.name, lang)
            src = (BgmSource("hca", path, 0) if os.path.isfile(path)
                   else BgmSource(why="no voice asset exported"))
        elif p.kind == "se":
            path = se_path(content_root, cs.area, cs.name, p.name)
            src = (BgmSource("hca", path, 0) if os.path.isfile(path)
                   else BgmSource(why="no SE stem exported"))
        else:
            src = bgm_source(content_root, p.name)

        if not src.ok:
            setattr(report, p.kind + "_missing", getattr(report, p.kind + "_missing") + 1)
            # Music is named in the report. A silent SE is usually just an
            # unexported stem and there are hundreds of those; a silent music
            # cue is rare, load-bearing, and worth being told about by name.
            if p.kind == "bgm" and src.why:
                report.unresolved.append("%s — %s" % (p.name, src.why))
            continue

        pcm = None if report.cached else _decode(src.kind, src.path, src.index, p.max_sec)
        if not report.cached and not pcm:
            setattr(report, p.kind + "_missing", getattr(report, p.kind + "_missing") + 1)
            if p.kind == "bgm":
                report.unresolved.append("%s — could not decode %s"
                                         % (p.name, os.path.basename(src.path)))
            continue
        setattr(report, p.kind, getattr(report, p.kind) + 1)
        if report.cached:
            continue

        off = max(0, int(p.tick / ticks * SR))
        n = min(len(pcm) // 2, total_samples - off)
        if n <= 0:
            continue
        chunk = np.frombuffer(pcm, dtype=np.int16, count=n).astype(np.int32)
        mix[off:off + n] += (chunk * p.gain).astype(np.int32) if p.gain != 1.0 else chunk

    report.duration = round(total_samples / SR, 2)
    if report.cached:
        return report
    if not (report.vo or report.se or report.bgm):
        return None

    out = np.clip(mix, -32768, 32767).astype(np.int16)
    encode = (["-c:a", "pcm_s16le"] if fmt == "wav"
              else ["-c:a", "libopus", "-b:a", BITRATE, "-application", "audio"])
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "pipe:0",
         *encode, out_path],
        input=out.tobytes(), capture_output=True)
    if r.returncode != 0:
        return None
    return report
