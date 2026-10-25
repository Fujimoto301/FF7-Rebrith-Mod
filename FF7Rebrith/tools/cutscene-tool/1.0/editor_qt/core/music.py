"""
The music library: which BGM banks exist, what is inside one, and what a cue
would have to be called to play it.

This is the read-only half of repointing a music trigger. The write half is
`edits.with_music_repointed` and, in the end, `patcher.repoint_music`.

Three facts about this game's music decide the shape of everything here.

**A bank is a folder, not a file.** `Sound/BGM/bgm_Corle_005.uasset` is one
`SQEXSEADMusic` asset holding several streams, and AudioMog extracts them beside
it as `bgm_Corle_005_Project/bgm_Corle_005_00N.wav`. Those streams are the
*slices*, and a slice is the smallest thing a cue can name.

**A cue names a slice, not a section.** `mixdown.bgm_source` established this
and it is not obvious: `bgm_Corle_005_01` is slice **1** of `bgm_Corle_005`,
which is `bgm_Corle_005_001.wav`, and slice 0 is named by the bare bank name
with no suffix at all. The section names in the asset - `Section0`, `Skip`,
`L5_1_baret` - are *labels on* slices, not addresses of them: one slice can
serve four sections, and `TrackUsers.txt` is the only thing that says which.
So the picker lists slices and captions them with their sections, rather than
listing sections and hoping each has a slice to itself.

**Nothing here is written to the asset.** Repointing a trigger changes one
string inside the cutscene, so the bank is only ever read - which is what makes
it safe to point ten scenes at one bank without any of them owning it.

Everything is lazy and cached. Listing 815 banks is one `listdir`; opening one
reads two small files. A dialog that scanned every bank up front would read
1,600 files to draw its first frame.
"""

from __future__ import annotations

import os
import re
import wave as wave_file
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .mixdown import REBUILD_SETTINGS, project_dir, slice_count

#: Where the banks live under a content root.
BGM_DIR = ("Sound", "BGM")

#: What AudioMog writes beside a bank's `.wav`s, mapping stream -> the sections
#: that use it. One line per stream:
#:
#:     bgm_Corle_005_000.hca,      users: Section0 (layer 0)
#:     bgm_Foree_051_007.hca,      users: Skip (layer 0), Skip1 (layer 0)
#:
#: A stream with no users at all is normal - several banks carry unreferenced
#: takes - and is listed as such rather than hidden, because "the composer left
#: an alternate in here" is exactly the thing worth finding.
TRACK_USERS = "TrackUsers.txt"

_USER_RE = re.compile(r"^\s*(.+?)\s*\(layer\s*(\d+)\)\s*$")
_SLICE_SUFFIX = re.compile(r"^(.*)_(\d+)$")


@dataclass(frozen=True)
class MusicSlice:
    """One stream inside a bank - the smallest thing a cue can point at."""

    index: int
    #: sections that play this stream, in the order TrackUsers lists them
    sections: Tuple[str, ...] = ()
    #: layer per section, same order. Layer > 0 is a stem mixed under another.
    layers: Tuple[int, ...] = ()
    #: the extracted `.wav`, when AudioMog has been run on the bank
    wav: str = ""
    #: length of that `.wav`, read from its header. None when there is no wav.
    seconds: Optional[float] = None

    @property
    def label(self) -> str:
        """What to call this slice in a list.

        The section names when it has any, because `Section0` and
        `L5_1_baret` are what the composer called it and what the rest of the
        game's cues say. Falling back to the number keeps a nameless stream
        selectable rather than blank.
        """
        if not self.sections:
            return "slice %d" % self.index
        return ", ".join(self.sections)

    @property
    def unused(self) -> bool:
        return not self.sections


@dataclass(frozen=True)
class MusicBank:
    """One `SQEXSEADMusic` asset and the streams inside it."""

    name: str
    uasset: str = ""
    project: str = ""
    slices: Tuple[MusicSlice, ...] = ()
    #: set when the bank could be listed but not opened
    why: str = ""

    @property
    def extracted(self) -> bool:
        """Has AudioMog been run on it? Without that there is nothing to hear."""
        return any(s.wav for s in self.slices)

    def slice_at(self, index: int) -> Optional[MusicSlice]:
        for s in self.slices:
            if s.index == index:
                return s
        return None


def cue_name(bank: str, index: int = 0) -> str:
    """What a cue has to be called to play slice `index` of `bank`.

    Slice 0 is the bare bank name. This asymmetry is the game's, not ours:
    `bgm_Corle_005` and `bgm_Corle_005_01` are slices 0 and 1 of the same bank,
    and `bgm_Corle_005_00` is not a name the game uses anywhere.
    """
    return bank if index <= 0 else "%s_%02d" % (bank, index)


def split_cue_name(name: str, exists) -> Tuple[str, int]:
    """`bgm_Corle_005_01` -> `('bgm_Corle_005', 1)`; unknown -> `('', 0)`.

    `exists(bank)` decides. It has to, and the order matters: **whole-bank
    first**. `bgm_Corle_004` looks exactly like "slice 4 of bgm_Corle" and is
    nothing of the sort - it is a bank in its own right, and most cues in this
    game are that shape. `mixdown.bgm_source` learned this the expensive way;
    splitting first and checking afterwards sends every one of them to the
    wrong bank.
    """
    if not name:
        return "", 0
    if exists(name):
        return name, 0
    m = _SLICE_SUFFIX.match(name)
    if m and exists(m.group(1)):
        return m.group(1), int(m.group(2))
    return "", 0


def capacity_of(authored: str) -> int:
    """How many characters a trigger the scene authored as `authored` has room for.

    **Pass the authored name, never the name a repoint has already put there.**
    The plan is applied to pristine assets on every build - `build_mod` wipes
    the staging folder first - so the span being written into is always the one
    the scene shipped with, whatever the editor is currently showing. Measuring
    a repoint against its own last choice would ratchet the budget down with
    every shorter track picked, and a trigger sent somewhere brief could never
    be sent home again.

    A shorter name is padded out with NULs rather than moving anything, so the
    span survives the round trip: the budget is a property of the scene, not of
    the edit.

    A cue's name lives in a length-prefixed string inside a compiled payload,
    and `patcher.py` patches these files **in place** - every offset and every
    size stays where it is, which is what keeps the Zen package repackable. So
    the replacement is written into the bytes the old name already occupies:
    it may be shorter, padded out with NULs, but it can never be longer.

    The exact figure belongs to the file, not to us - `patcher.repoint_music`
    measures the real span and refuses anything that will not fit. This is the
    editor's honest estimate of it, and it is right whenever the name is ASCII
    and NUL-terminated, which is every music cue in the game.
    """
    return len(authored or "")


def fits(new_name: str, authored: str) -> bool:
    """Can `new_name` be written over the name the scene authored?"""
    return bool(new_name) and len(new_name) <= capacity_of(authored)


def why_not(new_name: str, current: str) -> str:
    """Why this bank cannot be reached from this trigger, in plain words."""
    if fits(new_name, current):
        return ""
    return (
        "“%s” is %d characters and this trigger has room for %d - "
        "the name is written into the bytes the scene's own name occupies, so "
        "it can be shorter but never longer"
        % (new_name, len(new_name), capacity_of(current))
    )


def _wav_seconds(path: str) -> Optional[float]:
    """Length from the RIFF header. Never decodes - this runs 800 times."""
    try:
        with wave_file.open(path, "rb") as w:
            rate = w.getframerate()
            return (w.getnframes() / rate) if rate else None
    except Exception:
        return None


def _read_track_users(path: str) -> Dict[int, Tuple[Tuple[str, ...], Tuple[int, ...]]]:
    """slice index -> (section names, layers), from `TrackUsers.txt`."""
    out: Dict[int, Tuple[Tuple[str, ...], Tuple[int, ...]]] = {}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return out
    for line in lines:
        stem, _, rest = line.partition(",")
        m = _SLICE_SUFFIX.match(os.path.splitext(stem.strip())[0])
        if not m:
            continue
        idx = int(m.group(2))
        _, _, users = rest.partition("users:")
        names: List[str] = []
        layers: List[int] = []
        for part in users.split("),"):
            part = part.strip()
            if not part:
                continue
            if not part.endswith(")"):
                part += ")"
            hit = _USER_RE.match(part)
            if hit:
                names.append(hit.group(1))
                layers.append(int(hit.group(2)))
        out[idx] = (tuple(names), tuple(layers))
    return out


class MusicLibrary:
    """The folder of BGM banks, read on demand.

    Deliberately shaped like `library.SceneLibrary`: a cheap listing up front,
    and the contents of one entry only when something asks for it.
    """

    def __init__(self, content_root: Optional[str]) -> None:
        self.content_root = content_root or ""
        self._names: Optional[Tuple[str, ...]] = None
        self._known: frozenset = frozenset()
        self._banks: Dict[str, MusicBank] = {}

    @property
    def root(self) -> str:
        return os.path.join(self.content_root, *BGM_DIR) if self.content_root else ""

    @property
    def available(self) -> bool:
        return bool(self.root) and os.path.isdir(self.root)

    def names(self) -> Tuple[str, ...]:
        """Every bank, sorted, case-insensitively. One `listdir`."""
        if self._names is None:
            found: List[str] = []
            try:
                for f in os.listdir(self.root):
                    if f.lower().endswith(".uasset"):
                        found.append(f[: -len(".uasset")])
            except OSError:
                found = []
            self._names = tuple(sorted(found, key=str.lower))
            self._known = frozenset(self._names)
        return self._names

    def exists(self, name: str) -> bool:
        self.names()
        return name in self._known

    def search(self, query: str) -> Tuple[str, ...]:
        """Banks whose name contains every word typed, in any order.

        Words rather than a substring, so `corle 10` finds `bgm_Corle_106`
        without knowing what sits between the two.
        """
        words = [w for w in (query or "").lower().split() if w]
        if not words:
            return self.names()
        return tuple(n for n in self.names()
                     if all(w in n.lower() for w in words))

    def bank(self, name: str) -> MusicBank:
        """One bank, with its slices. Cached; two small file reads."""
        if name in self._banks:
            return self._banks[name]
        bank = self._load_bank(name)
        self._banks[name] = bank
        return bank

    def _load_bank(self, name: str) -> MusicBank:
        uasset = os.path.join(self.root, name + ".uasset")
        if not os.path.isfile(uasset):
            return MusicBank(name=name, why="no bank called %s" % name)
        proj = project_dir(self.content_root, name) or ""
        if not proj or not os.path.isfile(os.path.join(proj, REBUILD_SETTINGS)):
            # A bank nobody has extracted still has exactly one address the
            # game understands - its own name - so it stays selectable, just
            # with nothing to audition.
            return MusicBank(name=name, uasset=uasset, project=proj,
                             slices=(MusicSlice(index=0),),
                             why="not extracted - run AudioMog on it to hear it")
        n = slice_count(proj) or 0
        users = _read_track_users(os.path.join(proj, TRACK_USERS))
        # TrackUsers can list streams RebuildSettings does not count, and the
        # other way about. Taking the union keeps a real, playable stream from
        # disappearing because the two files disagree about how many there are.
        indices = sorted(set(range(n)) | set(users))
        slices: List[MusicSlice] = []
        for i in indices:
            wav = os.path.join(proj, "%s_%03d.wav" % (name, i))
            has = os.path.isfile(wav)
            sections, layers = users.get(i, ((), ()))
            slices.append(MusicSlice(
                index=i,
                sections=sections,
                layers=layers,
                wav=wav if has else "",
                seconds=_wav_seconds(wav) if has else None,
            ))
        return MusicBank(name=name, uasset=uasset, project=proj,
                         slices=tuple(slices))

    # -- what a cue currently points at -----------------------------------

    def resolve(self, music_name: str) -> Tuple[str, int]:
        """The bank and slice a cue name addresses, or `('', 0)`."""
        return split_cue_name(music_name, self.exists)

    def describe(self, music_name: str) -> str:
        """One line for a cue name: the bank, the slice, and what it is called.

        Used where a name alone would not say much - `bgm_Corle_005_01` reads
        as a track number until you know it is the second stream of a bank
        whose sections are named.
        """
        bank_name, idx = self.resolve(music_name)
        if not bank_name:
            return "%s - no bank of that name" % music_name
        s = self.bank(bank_name).slice_at(idx)
        if s is None:
            return "%s - %s has no slice %d" % (music_name, bank_name, idx)
        bits = [bank_name, "slice %d" % idx]
        if s.sections:
            bits.append(s.label)
        if s.seconds:
            bits.append(_mmss(s.seconds))
        return " · ".join(bits)


def _mmss(seconds: float) -> str:
    m, s = divmod(int(round(seconds)), 60)
    return "%d:%02d" % (m, s)
