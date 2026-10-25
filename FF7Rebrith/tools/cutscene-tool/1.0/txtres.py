"""
txtres.py - read `EndTextResource` (`Content/Text/<lang>/<area>_TxtRes.uasset`),
the table that holds every subtitle line in the game.

Why this file exists
--------------------
`extract_timeline.py` gets caption text from FModel's *JSON* export of this
asset. That is fine when the user dumped the game with FModel, and useless when
the tool extracted the assets itself out of the containers - so without this,
one-folder setup produces an editor with no subtitle text, only labels.

pyUE4Parse cannot help: `EndTextResource` derives from `MemoryMappedAsset`, so
a normal parse yields `{Type, Name, Outer, Properties: {Language}}` and no
strings at all. Same shape of problem `cutscenelist.py` documents for
`CutSceneListLevel`, and the same answer - read the blob directly.

The format
----------
Plain UE serialisation, no surprises once you look at it:

    int32   count
    count x record:
        FString  key          "$C3310_MAIN_0300_0100_00_eln"
        FString  text         the caption
        int32    metaCount
        metaCount x:
            int32   name index      into the package name map
            int32   name number     always 0 in practice
            FString value

`FString` is UE's own: int32 length *including* the NUL terminator, positive for
UTF-8 and negative for UTF-16LE, with the terminator stripped. The metadata key
is an FName, not a string - the only part that is not obvious, and the part that
quietly produces `{"": "Elena"}` instead of `{"ACTOR": "Elena"}` if you assume
otherwise. Index 4 is `ACTOR` in every file checked; it is resolved through the
name map rather than hardcoded.

What says it is right
---------------------
Two checks, both in `verify()`:

* The walk consumes the file to the last byte, with no slack and no overrun.
  Guessing a record layout wrong does not land on EOF exactly.
* Every key, text and metadata entry matches FModel's own export of the same
  asset, across all 142 areas - an independent implementation agreeing line for
  line on 9,806 captions.
"""

from __future__ import annotations

import json
import os
import struct
from typing import Dict, List, Optional, Tuple

# Finding the blob start
# ----------------------
# Every caption label begins with "$", and the two int32s before the first one
# are its FString length and the record count, so a "$" locates the table at
# index - 8. Two things stop that being a one-liner:
#
# * The name map can itself contain a "$" - 25 of the 142 areas have a label
#   interned as an FName - so the first "$" in the file is not necessarily the
#   first record. The search therefore starts after the name map ends, a
#   boundary the header gives us exactly.
# * Even then, a "$" could appear inside an earlier string. So every candidate
#   is tried and only one whose walk lands on the final byte is accepted.
#   Guessing wrong does not consume a file to EOF exactly.
#
# Telling an empty table from a changed format
# --------------------------------------------
# 23 of the 142 areas carry no captions at all - a header and nothing else -
# and in most of them a stray "$" still turns up in the bytes past the name
# map. So "found a $" cannot mean "has a table", and failing to parse cannot
# mean the format broke.
#
# The discriminator is the pair of int32s before the label: the record count
# and the first key's FString length. A real table has a small positive count
# and a key length of a few dozen bytes. The garbage candidates in those files
# read as counts of 683532669, -1594872879 and 0 - and one, sitting inside a
# hash blob, had a credible count of 49508 next to a key length of 149094400,
# which is why both fields have to be sane rather than just the count. So:
#
#   * some candidate had a plausible count but did not walk to EOF
#       -> the layout really has changed; raise, do not guess
#   * no candidate even had a plausible count
#       -> there is no table here; return {} like FModel does
#
# That keeps a genuine format change loud while treating the empty case as the
# ordinary thing it is.
_KEY_SENTINEL = b"$"
_MAX_RECORDS = 200000
# Labels run about 28 characters; a kilobyte is already absurd for one.
_MAX_KEY_LEN = 1024


def read_names(data: bytes) -> List[str]:
    """The package name map. Same decode `loosezen.read_names` uses, inlined so
    this module has no import cycle with it."""
    nm_off, nm_size = struct.unpack_from("<ii", data, 24)
    names: List[str] = []
    o = nm_off
    end = nm_off + nm_size
    while o < end:
        b0, b1 = data[o], data[o + 1]
        o += 2
        utf16 = b0 >> 7
        ln = ((b0 & 0x7F) << 8) | b1
        if utf16:
            names.append(data[o:o + 2 * ln].decode("utf-16-le", "replace"))
            o += 2 * ln
        else:
            names.append(data[o:o + ln].decode("latin1"))
            o += ln
    return names


def _fstring(data: bytes, o: int) -> Tuple[str, int]:
    (n,) = struct.unpack_from("<i", data, o)
    o += 4
    if n == 0:
        return "", o
    if n < 0:
        raw = data[o:o - 2 * n]
        o += -2 * n
        return raw.decode("utf-16-le", "replace").rstrip("\x00"), o
    raw = data[o:o + n]
    o += n
    return raw.decode("utf-8", "replace").rstrip("\x00"), o


def _walk(data: bytes, start: int, names: List[str], limit: int = _MAX_RECORDS
          ) -> Tuple[Optional[List[Tuple[str, str, Dict[str, str]]]], int]:
    """Read the table at `start`. Returns (records, end_offset), or (None, -1)
    if the bytes do not fit the layout."""
    o = start
    try:
        (count,) = struct.unpack_from("<i", data, o)
        o += 4
        if not (0 < count <= limit):
            return None, -1
        out: List[Tuple[str, str, Dict[str, str]]] = []
        for _ in range(count):
            key, o = _fstring(data, o)
            text, o = _fstring(data, o)
            (nmeta,) = struct.unpack_from("<i", data, o)
            o += 4
            if not (0 <= nmeta <= 32):
                return None, -1
            meta: Dict[str, str] = {}
            for _m in range(nmeta):
                (idx,) = struct.unpack_from("<i", data, o)
                o += 4
                (num,) = struct.unpack_from("<i", data, o)
                o += 4
                value, o = _fstring(data, o)
                name = names[idx] if 0 <= idx < len(names) else str(idx)
                # FName numbering: 0 means bare, n means "<name>_<n-1>". No
                # file checked uses it, but decoding it is free and silently
                # collapsing Foo_1 onto Foo would not be.
                if num:
                    name = "%s_%d" % (name, num - 1)
                meta[name] = value
            out.append((key, text, meta))
        return out, o
    except (struct.error, IndexError, UnicodeDecodeError):
        return None, -1


def parse(path: str) -> Dict[str, Dict[str, object]]:
    """{label: {"Text": str, "MetaData": {...}}}, in FModel's shape.

    Raises ValueError when no candidate offset produces a walk that ends on the
    last byte - better a clear failure than a half-read table that silently
    drops captions.
    """
    with open(path, "rb") as f:
        data = f.read()

    nm_off, nm_size = struct.unpack_from("<ii", data, 24)
    floor = max(nm_off + nm_size, 8)

    if data.find(_KEY_SENTINEL, floor) < 0:
        # No labels past the header: an empty table. FModel writes {} for these.
        return {}

    names = read_names(data)
    recs = None
    tried = 0
    plausible = 0
    at = data.find(_KEY_SENTINEL, floor)
    while at >= 8:
        tried += 1
        (count,) = struct.unpack_from("<i", data, at - 8)
        (key_len,) = struct.unpack_from("<i", data, at - 4)
        if 0 < count <= _MAX_RECORDS and 0 < key_len <= _MAX_KEY_LEN:
            plausible += 1
        got, stop = _walk(data, at - 8, names)
        if got is not None and stop == len(data):
            recs = got
            break
        at = data.find(_KEY_SENTINEL, at + 1)

    if recs is None:
        if plausible:
            raise ValueError(
                "%s: %d of %d candidate offsets had a plausible record count "
                "but none walked to the last byte - the format has changed"
                % (os.path.basename(path), plausible, tried))
        # Nothing here looked like a table at all: an empty one.
        return {}

    out: Dict[str, Dict[str, object]] = {}
    for key, text, meta in recs:
        entry: Dict[str, object] = {"Text": text}
        # FModel omits MetaData entirely when there is none, and `verify`
        # compares against FModel, so match it exactly rather than nearly.
        if meta:
            entry["MetaData"] = meta
        out[key] = entry
    return out


def to_fmodel_json(path: str, lang: str = "US") -> list:
    """The same envelope FModel writes, so `load_subtitles` cannot tell the
    difference between this and a real export."""
    name = os.path.basename(path)
    if name.endswith(".uasset"):
        name = name[:-len(".uasset")]
    return [{
        "Type": "EndTextResource",
        "Name": name,
        "Properties": {"Language": lang},
        "Strings": parse(path),
    }]


def verify(text_dir: str) -> Dict[str, object]:
    """Compare this reader against every FModel JSON sitting beside a uasset."""
    checked = exact = 0
    bad: List[str] = []
    lines = 0
    for fn in sorted(os.listdir(text_dir)):
        if not fn.endswith("_TxtRes.uasset"):
            continue
        ua = os.path.join(text_dir, fn)
        ref = ua[:-len(".uasset")] + ".json"
        if not os.path.isfile(ref):
            continue
        checked += 1
        try:
            mine = parse(ua)
        except ValueError as e:
            bad.append("%s: %s" % (fn, e))
            continue
        with open(ref, encoding="utf-8-sig") as f:
            doc = json.load(f)
        want = (doc[0] if isinstance(doc, list) else doc).get("Strings", {})
        lines += len(want)
        if mine == want:
            exact += 1
        else:
            only_mine = set(mine) - set(want)
            only_want = set(want) - set(mine)
            diffs = [k for k in want if k in mine and mine[k] != want[k]]
            bad.append("%s: +%d -%d ~%d (e.g. %s)" % (
                fn, len(only_mine), len(only_want), len(diffs),
                (diffs or list(only_want) or list(only_mine))[:1]))
    return {"checked": checked, "exact": exact, "lines": lines,
            "mismatches": bad[:15], "mismatch_total": len(bad)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "verify":
        r = verify(sys.argv[2])
        print("areas compared to FModel : %d" % r["checked"])
        print("byte-for-byte identical  : %d" % r["exact"])
        print("caption lines covered    : %d" % r["lines"])
        print("mismatches               : %d" % r["mismatch_total"])
        for m in r["mismatches"]:
            print("   ! %s" % m)
        raise SystemExit(0 if r["exact"] == r["checked"] and r["checked"] else 1)
    if len(sys.argv) >= 2:
        print(json.dumps(to_fmodel_json(sys.argv[1]), ensure_ascii=False,
                         indent=1)[:4000])
        raise SystemExit(0)
    print(__doc__)
