"""
Reading `CutSceneListLevel` - the table that chains one cutscene to the next.

Why this file exists
--------------------
Everything else in this tool edits a cutscene. Nothing edits the *order* they
play in, and until now we did not know where that order lived: a scan of all
755 extracted timelines found no reference from one scene to another. The
`Jump` and `StoryJump` clips inside a sequence carry a `Goto` like `C0030`,
which is a cut *within the same scene*, and the `SendStateTrigger` IDs are
state flags the scenario listens for, not a handoff.

The handoff is in `/Game/DataObject/Field/<area>/CutSceneListLevel`, whose row
struct `EndDataTableCutSceneListLevel` is in `Mappings.usmap` and carries:

    NextCutSceneNameList_Array        TArray<FName>
    NextCutSceneConditionList_Array   TArray<FName>
    ReadyCutsceneNameList_Array       TArray<FName>
    PreviousCutsceneCount             int32

FModel exports this asset with an empty `DataTable: {}`, which is what made it
look like a dead end. It is not: the rows are there, just not in a shape
FModel's DataTable path recognises. `EndDataObjectBase` derives from
`MemoryMappedAsset`, so the export is a flat blob laid out as parallel arrays
with a name-keyed directory at the end, rather than UE's usual tagged
serialisation.

What is proven and what is not
------------------------------
Proven, and what this module does:

* **The FName encoding.** Row keys are `FName("EV_FOREE", Number)`, which UE
  renders as `EV_FOREE_<Number-1>`. That is why the local name map holds only
  56 names for an area with 155 cutscenes. The exceptions are ids with a
  leading zero - `EV_FOREE_0020` cannot survive the number encoding, because it
  would come back as `EV_FOREE_20` - and those nine are stored literally.
  Checked against the extracted timelines: 144 of 146 encoded names resolve to
  a scene that exists on disk, and the two that do not are coincidental `21`s
  in unrelated data.

* **The directory.** From the first encoded name to the last word of the blob,
  entries are `[nameIndex][nameNumber][count][offset × count]`. Walking it
  consumes the tail exactly, with no slack and no overrun, which is the check
  that says the format is right rather than merely plausible - 193 entries in
  8800-FOREE.

Not proven, and why this module stops short of writing:

* **The 20-byte row is indices, not values.** `EV_FOREE_8510` reads
  `123, -1, 104, 0, 0`: a sequential row number and two indices into arrays
  held elsewhere in the blob. Which index selects which of the eighteen fields
  is still unknown, so we cannot yet say *which* offset on an entry is
  `NextCutSceneNameList_Array` rather than one of the nine other arrays.

  The encouraging part is that the blob is self-describing. All eighteen field
  names appear in the same directory as the scenes, as 12-byte descriptors at
  4104 through 4308 in area order - `ReadyCutsceneNameList_Array`,
  `NextCutSceneConditionList_Array`, `NextCutSceneNameList_Array` and the rest.
  So the field-to-array mapping should be readable out of the file itself
  rather than guessed, which is the difference between a day's work and a
  fishing trip.

* The second offset on the late 85xx entries points into a run of zeros, so
  those scenes appear to carry no next-scene list at all - consistent with boss
  phases being chained by battle logic instead. That is a reasonable reading,
  not a demonstrated one.

The last mile is mapping row indices to field arrays. Until that is done,
nothing here should be used to patch: guessing the wrong offset would rewrite
`PreloadActorNameList` or `StopAIActorName` instead, and both fail quietly.

The good news for patching, when we get there: these are FNames stored as
*indices*, not inline strings. Retargeting is a four-byte index swap with no
resizing at all - unlike the cue-name blanking in `patcher.py`, which can only
ever write a replacement no longer than the original.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import transforms as T


@dataclass(frozen=True)
class Entry:
    """One row of the directory: a scene, and where its data sits."""

    name: str
    #: word index of the entry itself, for reporting
    at: int
    #: byte offset of the fixed 20-byte row, then any array payloads
    offsets: Tuple[int, ...]

    @property
    def row(self) -> int:
        return self.offsets[0]

    @property
    def payloads(self) -> Tuple[int, ...]:
        return self.offsets[1:]


@dataclass
class CutSceneListLevel:
    path: str
    names: List[str] = field(default_factory=list)
    entries: List[Entry] = field(default_factory=list)
    blob: bytes = b""

    def get(self, ev: str) -> Optional[Entry]:
        for e in self.entries:
            if e.name == ev:
                return e
        return None

    def row_words(self, e: Entry) -> Tuple[int, ...]:
        """The five u32s at a scene row. Indices into arrays, not field values.

        Only meaningful for scene rows, which are 20 bytes and evenly spaced
        (308, 328, 348…). The directory also holds the eighteen *field*
        descriptors, and those are 12 bytes at 4104…4308, so reading five words
        there runs into the next descriptor. Told apart by name for now, which
        is enough to explore and not enough to patch.
        """
        return struct.unpack_from("<5I", self.blob, e.row)


def _fname(names: List[str], index: int, number: int) -> str:
    """UE renders `FName(name, n)` as `name_<n-1>`; `n == 0` means bare."""
    if index >= len(names):
        return "<bad:%d>" % index
    return names[index] if number == 0 else "%s_%d" % (names[index], number - 1)


def load(path: str, usmap: str) -> CutSceneListLevel:
    """Read the directory. Raises if it does not consume the blob exactly."""
    r = T.Reader2(path, usmap)
    if not r.exports:
        raise ValueError("%s has no exports" % path)
    off = r.dataOffset[0]
    blob = r.d[off:off + r.exports[0]["serialSize"]]
    words = struct.unpack_from("<%dI" % (len(blob) // 4), blob, 0)
    names = list(r.names)

    start = _directory_start(words, names)
    entries: List[Entry] = []
    i = start
    while i + 2 < len(words):
        idx, num, count = words[i], words[i + 1], words[i + 2]
        if idx >= len(names) or count > 8:
            raise ValueError(
                "directory went off the rails at word %d (index %d, count %d)"
                % (i, idx, count)
            )
        entries.append(
            Entry(
                name=_fname(names, idx, num),
                at=i,
                offsets=tuple(words[i + 3 + j] for j in range(count)),
            )
        )
        i += 3 + count

    if i != len(words):
        # the walk must land exactly on the end. Anything else means the entry
        # shape is wrong, and a directory that parses "nearly" is not parsed.
        raise ValueError(
            "directory ended at word %d, blob is %d words" % (i, len(words))
        )
    return CutSceneListLevel(path=path, names=names, entries=entries, blob=blob)


def _directory_start(words: Tuple[int, ...], names: List[str]) -> int:
    """First word of the name-keyed directory.

    Found rather than assumed: the directory is the tail, and the only place
    where a valid name index is followed by a small count and a run of offsets
    that walks cleanly to the end of the blob. Scanning backwards from the end
    and taking the earliest start that survives the walk is cheap and does not
    bake in a constant that would differ per area.
    """
    best = None
    for start in range(len(words) - 3, max(0, len(words) - 4000), -1):
        i = start
        ok = True
        while i + 2 < len(words):
            idx, count = words[i], words[i + 2]
            if idx >= len(names) or count > 8:
                ok = False
                break
            i += 3 + count
        if ok and i == len(words):
            best = start
    if best is None:
        raise ValueError("no directory found")
    return best


def report(csl: CutSceneListLevel, limit: int = 0) -> str:
    lines = ["%s" % csl.path, "%d entries, %d names" % (len(csl.entries), len(csl.names))]
    rows = csl.entries[:limit] if limit else csl.entries
    for e in rows:
        lines.append(
            "  %-18s row@%-6d payloads=%s  words=%s"
            % (e.name, e.row, list(e.payloads), list(csl.row_words(e)))
        )
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("usage: cutscenelist.py <CutSceneListLevel.uasset> <Mappings.usmap> [ev]")
        raise SystemExit(2)
    csl = load(sys.argv[1], sys.argv[2])
    if len(sys.argv) > 3:
        e = csl.get(sys.argv[3])
        print(e if e is None else report(CutSceneListLevel(
            csl.path, csl.names, [e], csl.blob)))
    else:
        print(report(csl, limit=25))
        print("  ... %d more" % max(0, len(csl.entries) - 25))
