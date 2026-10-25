"""
Retarget one cutscene link in an `EndDataObject*` asset.

    python retarget.py 8590 7500
    python retarget.py EV_FOREE_8590 EV_FOREE_7500 --area 8800-FOREE
    python retarget.py 8590 7500 --field ReadyCutsceneNameList_Array --element 0

Why this is a directory edit and not a pointer edit
---------------------------------------------------
Every FName in these files is stored as **eight zero bytes**. Nothing in the row
records, the FName pool or the key array carries a name. The directory at the tail
is the fixup table: each entry says "at these addresses, write FName(base, number)",
and the loader fills them in. Verified — the whole pool region and every key-record
name field is zero on disk.

So retargeting a link means moving one address from the source scene's directory
entry to the target scene's. Nothing else moves: not the pool, not the row records,
not the pointers, not the hash buckets.

Size is preserved when both scenes share a name-table base, which every
`EV_<AREA>_nnnn` in an area does — one entry shrinks by four bytes, the other grows
by four. The script refuses to write if the delta is not zero, because a resize
would shift the directory and invalidate every offset in it.

The target does **not** need its own name-table string. Names are `FName(base,
number)`, so any `EV_FOREE_nnnn` is reachable as long as `EV_FOREE` is in the table.
"""

from __future__ import annotations

import argparse
import os
import shutil
import struct
import sys

from dataobject import CATENA_FIELDS, LEVEL_FIELDS, DataObject

DEFAULT_ASSET = "Content/DataObject/Field/8800-FOREE/CutSceneListLevel.uasset"


def split_label(label, names):
    """'EV_FOREE_7500' -> (nameTableIndex, fnameNumber). Literal names win."""
    if label in names:
        return names.index(label), 0
    base, _, tail = label.rpartition("_")
    if base in names and tail.isdigit():
        return names.index(base), int(tail) + 1
    raise SystemExit(
        "cannot encode %r: neither a literal name nor <base>_<number> with a known "
        "base. Bases present: %s" % (label, ", ".join(n for n in names if "_" not in n))
    )


def resolve(o, want, hint):
    """Accept '8590', 'EV_FOREE_8590' or a literal row name."""
    if want in o.rowname.values():
        return want
    cands = [n for n in o.rowname.values() if n.endswith("_" + want) or n == want]
    if len(cands) == 1:
        return cands[0]
    if not cands:
        raise SystemExit("%s %r is not a row in this asset" % (hint, want))
    raise SystemExit("%s %r is ambiguous: %s" % (hint, want, ", ".join(sorted(cands))))


def serialize(ents_raw):
    """ents_raw: list of (nameIndex, number, sorted offsets)."""
    out = bytearray()
    for ni, num, offs in sorted(ents_raw):
        out += struct.pack("<III", ni, num, len(offs))
        for x in sorted(offs):
            out += struct.pack("<I", x)
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="scene whose link is being changed, e.g. 8590")
    ap.add_argument("target", help="scene it should go to instead, e.g. 7500")
    ap.add_argument("--asset", default=None, help="path to the .uasset")
    ap.add_argument("--area", default="8800-FOREE")
    ap.add_argument("--root", default="..", help="extraction root holding Content/")
    ap.add_argument("--field", default="NextCutSceneNameList_Array")
    ap.add_argument("--element", type=int, default=0, help="which entry in the array")
    ap.add_argument("-o", "--out", default="retarget_out")
    ap.add_argument(
        "--stage-into",
        help="also drop the patched asset into an existing build's staged/ folder. "
        "build_mod.py wipes staged/ on every run, so do this AFTER building.",
    )
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    asset = a.asset or os.path.join(
        a.root, "Content/DataObject/Field/%s/CutSceneListLevel.uasset" % a.area
    )
    if not os.path.exists(asset):
        raise SystemExit("no such asset: %s" % asset)
    fields = CATENA_FIELDS if "Catena" in asset else LEVEL_FIELDS
    o = DataObject(asset, fields)
    if a.field not in o.foff:
        raise SystemExit(
            "%s is not laid out in this asset. Present: %s"
            % (a.field, ", ".join(sorted(o.foff)))
        )

    src = resolve(o, a.source, "source")
    row = next(r for r, n in o.rowname.items() if n == src)

    # locate the FName slot this link occupies
    P = o.row0 + o.stride * row + o.foff[a.field]
    ptr, count = o.u64(P), o.u32(P + 8)
    if not count or not ptr & 1:
        raise SystemExit("%s has no %s to retarget" % (src, a.field))
    if not 0 <= a.element < count:
        raise SystemExit("%s has %d element(s); --element %d is out of range"
                         % (a.field, count, a.element))
    slot = P + (ptr >> 1) + 8 * a.element
    was = o.pool.get(slot)
    if was is None:
        raise SystemExit("slot 0x%x is not named by the directory" % slot)

    # target need only share a base with something already in the name table
    tgt = a.target if a.target.startswith(("EV_", "MV_")) else None
    if tgt is None:
        base = src.rpartition("_")[0]
        tgt = "%s_%s" % (base, a.target)
    ni_t, num_t = split_label(tgt, o.names)

    print("%s\n  %-24s %s[%d] @ 0x%x" % (asset, src, a.field, a.element, slot))
    print("  %-24s %s" % ("currently", was))
    print("  %-24s %s   (name index %d, number %d)" % ("retarget to", tgt, ni_t, num_t))

    # An FName is encodable whether or not the scene exists, so a typo writes
    # cleanly and fails only in game. Check the two places it should show up.
    if tgt not in o.rowname.values():
        print("  %-24s NOT a row in this table — it has no load/battle setup"
              % "[warn]")
    area = os.path.basename(os.path.dirname(os.path.abspath(asset)))
    cut = os.path.join(a.root, "Content/Cut/Game", area, tgt)
    if os.path.isdir(cut):
        print("  %-24s %s" % ("scene assets", cut))
    else:
        print("  %-24s no cutscene folder at %s" % ("[warn]", cut))
    if o.d[slot : slot + 8] != b"\0" * 8:
        raise SystemExit("slot is not zero on disk — assumption broken, refusing")

    # rebuild the directory with the address moved between entries
    raw = []
    for e, (nm, num, offs) in enumerate(o.ents):
        raw.append([o.names.index(nm), num, list(offs)])
    biased = slot - o.D
    moved_from = None
    for ent in raw:
        if biased in ent[2]:
            ent[2].remove(biased)
            moved_from = (ent[0], ent[1])
            break
    if moved_from is None:
        raise SystemExit("address 0x%x not found in the directory" % slot)
    for ent in raw:
        if (ent[0], ent[1]) == (ni_t, num_t):
            ent[2].append(biased)
            break
    else:
        raw.append([ni_t, num_t, [biased]])
        print("  note: %s had no directory entry; created one" % tgt)
    raw = [e for e in raw if e[2]]

    body = serialize([(x[0], x[1], x[2]) for x in raw])
    delta = len(body) - _dirlen(o)
    if delta:
        raise SystemExit(
            "directory would change size by %+d bytes; every offset in it is "
            "relative, so a resize is not a safe in-place edit." % delta
        )

    patched = bytearray(o.d)
    patched[o.dir_start : o.dir_start + len(body)] = body
    assert len(patched) == len(o.d)

    if a.dry_run:
        print("  dry run — nothing written")
        return

    rel = os.path.relpath(os.path.abspath(asset), os.path.abspath(a.root))
    dest = os.path.join(a.out, "End", rel.replace("\\", "/"))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(patched)
    print("  wrote %s (%d bytes, unchanged)" % (dest, len(patched)))
    if a.stage_into:
        if not os.path.isdir(a.stage_into):
            raise SystemExit("--stage-into %r does not exist" % a.stage_into)
        into = os.path.join(a.stage_into, "End", rel.replace("\\", "/"))
        os.makedirs(os.path.dirname(into), exist_ok=True)
        shutil.copy2(dest, into)
        print("  staged %s" % into)
    verify(asset, dest, fields, src, a.field, a.element, tgt)


def _dirlen(o):
    """Bytes the directory actually occupies, excluding trailing zero padding."""
    n = 0
    for nm, num, offs in o.ents:
        n += 12 + 4 * len(offs)
    return n


def verify(original, patched, fields, src, field, element, expect):
    """Re-parse both and prove exactly one link changed."""
    a, b = DataObject(original, fields), DataObject(patched, fields)
    print("\nverification")
    print("  size            %d -> %d" % (len(a.d), len(b.d)))
    print("  rows            %d -> %d" % (a.nrow, b.nrow))
    print("  geometry        row0/stride/pool %s -> %s"
          % ((hex(a.row0), a.stride, hex(a.pool0)), (hex(b.row0), b.stride, hex(b.pool0))))

    def snapshot(o):
        s = {}
        for r in range(o.nrow):
            for f, w in o.fields.items():
                if w != 16 or f not in o.foff:
                    continue
                v = o.array(r, f)
                if v:
                    s[(o.rowname.get(r, r), f)] = v
        return s

    sa, sb = snapshot(a), snapshot(b)
    diff = [k for k in set(sa) | set(sb) if sa.get(k) != sb.get(k)]
    for k in sorted(diff, key=str):
        print("  changed         %s %s: %s -> %s" % (k[0], k[1], sa.get(k), sb.get(k)))
    got = sb.get((src, field), [None] * (element + 1))[element]
    ok = len(diff) == 1 and got == expect
    unresolved = sum(1 for v in sb.values() for x in v if x.startswith("<unresolved"))
    print("  other links      %d changed" % (len(diff) - 1 if diff else 0))
    print("  unresolved ptrs  %d" % unresolved)
    print("\n  %s" % ("PASS" if ok and not unresolved else "FAIL"))
    if not (ok and not unresolved):
        sys.exit(1)


if __name__ == "__main__":
    main()
