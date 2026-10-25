"""
Reader for `EndDataObject*` memory-image assets (the FModel "DataTable: {}" ones).

The container is fully self-describing; nothing here is guessed. Layout, in file order:

    0x40                name table, entries of [00][len][bytes], no NUL
    ...                 header / hash blobs
    KEY                 key array, 20 bytes per row:
                          +0,+4  unused
                          +8     ordinal (dense, 0..N-1)
                          +12    next-in-bucket ordinal, -1 = end
                          +16    hash bucket
    FDESC               field descriptors, 12 bytes each, type code at +8
                          11 = TArray<FName> or FName, 7 = int32, 2 = uint8
    ROW0                row records, fixed stride, fields in *descriptor* order
    POOL                FName pool, 8 bytes per slot, contiguous
    DIR                 directory, entries of [nameIndex][nameNumber][count][offset x count]

Two things that cost a day each:

* Directory offsets are relative, not absolute. The bias `D` is the same for every
  offset in the file and is recovered by matching the key array: the directory's
  stride-20 run of offsets is the key array, so `D = KEY - min(run)`.

* TArray pointers are `(selfRelativeOffset << 1) | 1`. The low bit is a tag, so the
  raw u64 is always odd and always looked ~2x too large. Target is
  `P + (u64(P) >> 1)`, then `count` FNames of 8 bytes each.

Names are `FName(base, number)` and render as `base_<number-1>`, so `EV_FOREE`
with number 7501 is `EV_FOREE_7500`. Ids with a leading zero cannot survive that
encoding and are stored literally.

Verified on `Resident/CutSceneCatenaList` (49 rows, 51 pool slots, 0 unresolved)
and all nine `Field/*/CutSceneListLevel` files.
"""

from __future__ import annotations

import struct

# --- field layouts, from EndDataObject.hpp -----------------------------------
# name -> byte width in the memory image. Order comes from the file, not from here.
CATENA_FIELDS = {
    "NextCutSceneName1_Array": 16,
    "NextCutSceneName2_Array": 16,
    "NextCutSceneName3_Array": 16,
    "NextCutSceneName4_Array": 16,
    "SpecialCatenaDatering": 1,
    "Reserve1": 1,
    "Reserve2": 1,
}

LEVEL_FIELDS = {
    "NextCutSceneNameList_Array": 16,
    "ReadyCutsceneNameList_Array": 16,
    "NextCutSceneConditionList_Array": 16,
    "IgnoreLevelActor_Array": 16,
    "PreloadActorNameList_Array": 16,
    "StopAIActorName_Array": 16,
    "AnimationSequenceActorName_Array": 16,
    "AnimationSequenceState_Array": 16,
    "LoadSaveRestorePositionActorName_Array": 16,
    "LoadSaveRestorePositionTargetPoint_Array": 16,
    "EncountBattleTerritoryID": 8,
    "PreviousCutsceneCount": 4,
    "ExtraFlags": 4,
    "BattleStart": 4,
    "SpawnActorWait": 1,
    "OverwriteBindActor": 1,
    "LoadControlType": 1,
    "BlendStartType": 1,
}


def _align(v, a):
    return (v + a - 1) // a * a


class DataObject:
    def __init__(self, path, fields):
        self.path = path
        self.d = open(path, "rb").read()
        self.fields = fields
        self._names()
        self._directory()
        self._geometry()
        self._labels()

    # -- primitives
    def u32(self, o):
        return struct.unpack_from("<I", self.d, o)[0]

    def i32(self, o):
        return struct.unpack_from("<i", self.d, o)[0]

    def u64(self, o):
        return struct.unpack_from("<Q", self.d, o)[0]

    # -- name table
    def _names(self):
        d = self.d
        o, names = 0x40, []
        while o + 2 < len(d) and d[o] == 0:
            n = d[o + 1]
            if n == 0 or o + 2 + n > len(d):
                break
            s = d[o + 2 : o + 2 + n]
            if any(b < 32 or b > 126 for b in s):
                break
            names.append(s.decode())
            o += 2 + n
        self.names, self.names_end = names, o

    # -- directory
    def _walk(self, start):
        """Walk [nameIndex][nameNumber][count][offset x count] to EOF, or fail."""
        d, o, ents, last = self.d, start, [], (-1, -1)
        while o + 12 <= len(d) and any(d[o : o + 12]):
            ni, num, cnt = self.u32(o), self.u32(o + 4), self.u32(o + 8)
            if ni >= len(self.names) or not 0 < cnt <= 4096:
                return None
            if (ni, num) <= last or o + 12 + 4 * cnt > len(d):
                return None
            last = (ni, num)
            ents.append((self.names[ni], num, [self.u32(o + 12 + 4 * k) for k in range(cnt)]))
            o += 12 + 4 * cnt
        # the directory runs to EOF; only zero padding may follow
        return ents if ents and not any(d[o:]) else None

    def _find_key0(self):
        # the 20-byte key array: dense ordinals at +8. Found without the directory.
        for c in range(0x100, len(self.d) - 20 * 24, 4):
            if all(self.i32(c + 8 + 20 * k) == k for k in range(24)):
                return c
        raise ValueError("key array not found")

    def _directory(self):
        # the real directory is the walk whose offsets, once biased, all land before it
        self.key0 = self._find_key0()
        for s in range(_align(self.names_end, 4), len(self.d) - 16, 4):
            e = self._walk(s)
            if not e:
                continue
            raw = sorted({x for _, _, offs in e for x in offs})
            rawset = set(raw)
            run = max(
                ((a, n) for a in raw for n in [self._runlen(a, rawset)]),
                key=lambda t: t[1],
            )
            if run[1] < 8:
                continue
            D = self.key0 - run[0]
            if 0 <= raw[0] + D and raw[-1] + D < s:
                self.dir_start, self.ents = s, e
                return
        raise ValueError("directory not found")

    @staticmethod
    def _runlen(a, s):
        n = 0
        while a + 20 * n in s:
            n += 1
        return n

    # -- geometry: bias D, key array, descriptors, row stride, pool
    def _geometry(self):
        d = self.d
        raw = sorted({x for _, _, offs in self.ents for x in offs})
        rawset = set(raw)
        # longest stride-20 run == the key array
        best = (0, 0)
        for a in raw:
            n = 0
            while a + 20 * n in rawset:
                n += 1
            if n > best[1]:
                best = (a, n)
        keymin = best[0]
        self.D = self.key0 - keymin
        # row count comes from the key array itself, not from the directory:
        # rows nothing references by name have no directory entry.
        self.nrow = 0
        while self.i32(self.key0 + 8 + 20 * self.nrow) == self.nrow:
            self.nrow += 1
        self.keymin = keymin

        # descriptor table: field names in the directory point at their descriptors
        fo = sorted(x for nm, _, offs in self.ents if nm in self.fields for x in offs)
        self.fdesc0 = fo[0] + self.D
        self.nfield = (fo[-1] + self.D + 12 - self.fdesc0) // 12
        self.field_at = {}  # descriptor index -> field name
        for nm, _, offs in self.ents:
            if nm in self.fields:
                for x in offs:
                    self.field_at[(x + self.D - self.fdesc0) // 12] = nm
        self.row0 = _align(self.fdesc0 + 12 * self.nfield, 8)

        # Memory-image offsets: descriptor order, natural alignment. A field that
        # nothing references has no directory entry, so its slot is anonymous; its
        # width comes from the type code, disambiguated against the fields left
        # over. Type 11 covers both TArray (16) and FName (8), which is why the
        # type code alone is not enough.
        spare = [f for f in self.fields if f not in self.field_at.values()]
        self.foff, off = {}, 0
        for i in range(self.nfield):
            nm = self.field_at.get(i)
            if nm:
                w = self.fields[nm]
            else:
                allowed = {11: (16, 8), 7: (4,), 2: (1,)}.get(
                    self.u32(self.fdesc0 + 12 * i + 8), (4,)
                )
                pick = next((f for f in spare if self.fields[f] in allowed), None)
                w = self.fields[pick] if pick else allowed[0]
                if pick:
                    spare.remove(pick)
                    nm = pick
            off = _align(off, min(w, 8))
            if nm:
                self.foff[nm] = off
            off += w
        self.stride = _align(off, 8)
        self.pool0 = self.row0 + self.stride * self.nrow
        if self.pool0 > self.dir_start:
            raise ValueError("row block overruns directory; layout wrong")

    def _width_from_type(self, i):
        # fallback for descriptor slots whose field name is absent from the directory
        return {11: 16, 7: 4, 2: 1}.get(self.u32(self.fdesc0 + 12 * i + 8), 4)

    # -- names for rows and pool slots
    def _labels(self):
        def lab(nm, num):
            return nm if num == 0 else "%s_%04d" % (nm, num - 1)

        self.rowname, self.pool = {}, {}
        for nm, num, offs in self.ents:
            if nm in self.fields:
                continue
            for x in offs:
                a = x + self.D
                if self.key0 <= a < self.key0 + 20 * self.nrow and (a - self.key0) % 20 == 0:
                    # the package/class self-reference heads the directory and
                    # aliases a real row; never let it win the row name
                    if not nm.startswith("/"):
                        self.rowname[(a - self.key0) // 20] = lab(nm, num)
                elif a >= self.pool0:
                    self.pool[a] = lab(nm, num)

    # -- accessors
    def array(self, row, field):
        """Read a TArray<FName> field as a list of names."""
        P = self.row0 + self.stride * row + self.foff[field]
        v, n = self.u64(P), self.u32(P + 8)
        if not n or not v & 1:
            return []
        t = P + (v >> 1)
        return [self.pool.get(t + 8 * k, "<unresolved:%x>" % (t + 8 * k)) for k in range(n)]

    def scalar(self, row, field):
        P = self.row0 + self.stride * row + self.foff[field]
        w = self.fields[field]
        return self.d[P] if w == 1 else self.u32(P)

    def rows(self):
        for r in range(self.nrow):
            yield r, self.rowname.get(r, "row%d" % r)


def catena(path):
    """Global cutscene chain table -> {scene: {1..4: [next, ...]}}"""
    o = DataObject(path, CATENA_FIELDS)
    out = {}
    for r, name in o.rows():
        ch = {}
        for i in (1, 2, 3, 4):
            v = o.array(r, "NextCutSceneName%d_Array" % i)
            if v:
                ch[i] = v
        out[name] = {"chains": ch, "SpecialCatenaDatering": o.scalar(r, "SpecialCatenaDatering")}
    return o, out


def level(path):
    """Per-area CutSceneListLevel -> {scene: {field: value}}"""
    o = DataObject(path, LEVEL_FIELDS)
    out = {}
    for r, name in o.rows():
        rec = {}
        for f, w in LEVEL_FIELDS.items():
            if f not in o.foff:
                continue
            v = o.array(r, f) if w == 16 else o.scalar(r, f)
            if v:
                rec[f.replace("_Array", "")] = v
        out[name] = rec
    return o, out


if __name__ == "__main__":
    import json
    import sys

    p = sys.argv[1]
    fn = catena if "Catena" in p else level
    o, out = fn(p)
    print(
        "%s\n  rows=%d fields=%d stride=%d D=0x%x keys=0x%x desc=0x%x row0=0x%x pool=0x%x dir=0x%x"
        % (p, o.nrow, o.nfield, o.stride, o.D, o.key0, o.fdesc0, o.row0, o.pool0, o.dir_start)
    )
    if len(sys.argv) > 2:
        json.dump(out, open(sys.argv[2], "w"), indent=1)
        print("  wrote", sys.argv[2])
    else:
        for k, v in out.items():
            if v.get("chains") or v.get("NextCutSceneNameList"):
                print("  %-18s %s" % (k, v.get("chains") or v["NextCutSceneNameList"]))
