"""
evalfield.py — remap the baked evaluation field inside MovieSceneCompiledData.

Why this exists
---------------
Every sequence carries a cooked `MovieSceneCompiledData` export holding a
pre-baked evaluation field: a sorted, contiguous list of time ranges that tells
the engine which entities are live during each slice of the timeline. At runtime
in a shipping build this field is authoritative — the section data we patch is
only consulted for values, not for *when* things happen.

So patching the sections alone moves the content while the schedule stays put:
removed shots keep playing, cameras hold past their cut, cues fire at the old
times. A cut at the very end appears to work only because playback stops before
the disagreement matters.

The field can't be deserialized (it nests several structs with custom
serialisers that the .usmap can't describe), but it doesn't need to be. Each
entry begins with a TRange<FFrameNumber> — two bounds of one type byte plus one
int32 tick — and the entries sit at a fixed stride. Because the ranges are
contiguous and ascending, a run of them is unmistakable, and every tick is a
fixed-size int32, so rewriting them in place changes no offsets.
"""
import struct

BOUND_TYPES = (0, 1, 2)          # Exclusive, Inclusive, Open

# A run this long is a real evaluation field on length alone — see find_runs.
LONG_RUN = 8


def _range_at(blob, p):
    """Decode a TRange<FFrameNumber> at p, or None if it isn't one."""
    if p + 10 > len(blob):
        return None
    lt = blob[p]
    ut = blob[p + 5]
    if lt not in BOUND_TYPES or ut not in BOUND_TYPES:
        return None
    lo, = struct.unpack_from('<i', blob, p + 1)
    hi, = struct.unpack_from('<i', blob, p + 6)
    return lt, lo, ut, hi


def find_runs(blob, total, min_len=3, frame=None):
    """Find runs of evenly spaced, contiguous, ascending ranges.

    Returns [(stride, [positions])].

    "Contiguous and ascending" is NOT enough on its own. Animation, lighting and
    particle payloads are full of int32s that read as neat ascending pairs —
    float bit patterns and 64 KB-aligned sizes especially — and three of them in
    a row at a fixed stride happens easily. Rewriting those corrupts data that
    has nothing to do with time, and the package then fails to load: the game
    crashes as the scene comes in, before anything is evaluated.

    The property that actually identifies an evaluation field is that it
    *partitions the whole timeline*: the first entry opens at 0 and the last
    closes exactly on the sequence length. Real fields do this by construction;
    a coincidental run essentially never does. On EV_FOREE_8510 that separates
    8 genuine fields from 28 impostors.

    Ticks are also bounded by `total` itself. The old bound of total*4 admitted
    values four times longer than the cutscene.
    """
    lim = total
    cand = []
    for p in range(len(blob) - 10):
        r = _range_at(blob, p)
        if not r:
            continue
        _lt, lo, _ut, hi = r
        if 0 <= lo <= hi <= lim:
            cand.append((p, lo, hi))
    by_lo = {}
    for p, lo, hi in cand:
        by_lo.setdefault(lo, []).append((p, hi))

    runs = []
    used = set()
    for p, lo, hi in cand:
        if p in used or hi == lo:
            continue
        chain = [p]
        stride = None
        cur_p, cur_hi = p, hi
        while True:
            nxt = None
            for q, qhi in by_lo.get(cur_hi, ()):
                d = q - cur_p
                if d <= 0 or q in used:
                    continue
                if stride is not None and d != stride:
                    continue
                if 10 <= d <= 512:
                    nxt = (q, qhi, d)
                    break
            if not nxt:
                break
            q, qhi, d = nxt
            stride = d
            chain.append(q)
            cur_p, cur_hi = q, qhi
        if len(chain) >= min_len:
            runs.append((stride, chain))
            used.update(chain)

    # Separate real fields from coincidences. Requiring a run to partition the
    # whole timeline is too strong: genuine fields cover part of it — an effect
    # that only exists between two moments has a field spanning just that. Over
    # 60 cutscenes that test threw away 101 real fields, which is why VFX and
    # cut events stopped following the edit.
    #
    # Frame alignment is the property that actually separates them. Real bounds
    # come from authored frames, so every one is a multiple of the ticks-per-
    # frame (or one below it, from an inclusive/exclusive conversion). The
    # impostors are float bit patterns and 64 KB-aligned sizes, and essentially
    # never land on a frame. Across those same 60 cutscenes this keeps 419 runs
    # and rejects 845, with no overlap between the two groups.
    kept = []
    for stride, chain in runs:
        bounds = []
        for p in chain:
            r = _range_at(blob, p)
            if not r:
                bounds = None
                break
            bounds += [r[1], r[3]]
        if not bounds:
            continue
        if any(b < 0 or b > total for b in bounds):
            continue
        # Long runs are genuine by construction. Across 50 cutscenes every
        # in-range run of 8 or more entries was a real field (172 of 172) and
        # every impostor was three entries long — a coincidence big enough to
        # chain that far simply does not occur.
        #
        # This matters because real fields are NOT perfectly frame-aligned. A
        # lighting field in EV_FOREE_8514 has 26 of its 148 bounds sitting a
        # few ticks off a frame, which are genuine sub-frame boundaries. The
        # all-or-nothing alignment test threw away the whole 74-entry field for
        # them, so lighting was never remapped and the lights went on switching
        # on the original schedule.
        if len(chain) < LONG_RUN and frame and \
                any(b % frame and (b + 1) % frame for b in bounds):
            continue
        kept.append((stride, chain))
    return kept


def enforce_partition(bounds, limit=None):
    """Make a list of [lo, hi] pairs sorted, contiguous and never inverted —
    and leave removed entries EMPTY.

    A removed shot collapses to lower == upper. That is not a defect to be
    repaired; it is the signal. An empty range is how the engine is told the
    shot no longer occupies any time, and it skips it. Widening one back to a
    single tick puts the shot back on the schedule: the field reports it live,
    the camera-cut track executes a cut to it, and its section has been
    collapsed to nothing — so the engine cuts to a camera with no data. That is
    the crash, and it is why the split cut worked before the flash-frame fix
    and stopped afterwards.

    The blank frame that motivated the widening was never caused by emptiness.
    It was caused by the field and the sections DISAGREEING — the field had been
    widened to one tick while the section was still empty, so for that tick a
    shot was live with nothing to show. Both are built here, from this one
    function, so they agree; empty in both places means never scheduled and
    never cut to, and there is no frame to be blank.

    `limit`, the new end of the cutscene, only clamps: nothing may run past it.
    """
    live = [v for v in bounds if v is not None]
    cursor = None
    for val in live:
        if cursor is not None and val[0] < cursor:
            val[0] = cursor
        if val[1] < val[0]:                 # never inverted...
            val[1] = val[0]                 # ...but zero-width is allowed, and
        if limit is not None:               #    is the whole point
            if val[0] > limit: val[0] = limit
            if val[1] > limit: val[1] = limit
        cursor = val[1]
    return bounds


def park_empty(bounds, end):
    """Move every empty entry to `end`, out of the way of live content.

    For camera cut sections only. An empty section left on a join shares its
    start time with the shot that survives there, and a camera cut holds until
    the next one — so if the engine resolves that tie to the removed shot it
    binds a camera whose data has collapsed, and the dead frame covers the whole
    surviving shot. At `end` they sit past the last live section, where playback
    has already stopped, which is where cuts running to the end put them anyway.

    Sections are matched by time, not by array order, so this is safe — the
    original array is not in timeline order either.

    The evaluation field must NOT be parked: it has to stay contiguous. An empty
    field entry is never live, so the two still agree.

    Used by the patcher and by the build's verification, from one place, so the
    two cannot drift apart.
    """
    for v in bounds:
        if v is not None and v[0] == v[1]:
            v[0] = v[1] = end
    return bounds


def patch(data, off, size, remap, total, frame=None):
    """Rewrite every evaluation-field range in one compiled-data export.

    The field is meant to *partition* the timeline: entries are contiguous and
    each one advances. A removed shot would naturally collapse to an empty range
    (lower == upper), which breaks that invariant — and engine code that walks
    the field by stepping to each range's upper bound then never advances, which
    is what a freeze rather than a crash looks like.

    So a collapsed entry is given the minimum width that still advances, one
    tick, and that tick is reclaimed from the start of the next entry. Ranges
    stay sorted, contiguous and non-empty, no entry drifts, and one tick is
    1/24000 s — far below a frame.

    `data` is a bytearray of the whole file; returns how many ranges moved.
    """
    blob = bytes(data[off:off + size])
    moved = 0
    runs = find_runs(blob, total, frame=frame)
    covered = set()
    for _stride, chain in runs:
        for q in chain:
            covered.update(range(q, q + 10))

    # The whole-sequence span, on its own rather than in a run. The master and
    # its _Low twin carry one per sub-sequence instance — the tree saying "this
    # child is live for the length of the scene". They are not part of any
    # strided field, so the run scan never sees them, and they were left
    # declaring the original duration after everything else had moved.
    # Only an exact [0, total) with real bound types is touched, and only its
    # upper bound, which makes this about as narrow as a rewrite can be.
    new_total = remap.point(total)
    if new_total != total:
        for p in range(len(blob) - 10):
            if p in covered:
                continue
            r = _range_at(blob, p)
            if r and r[1] == 0 and r[3] == total and r[0] in (0, 1) and r[2] in (0, 1):
                struct.pack_into('<i', data, off + p + 6, new_total)
                moved += 1

    if not runs:
        return moved
    for _stride, chain in runs:
        entries = []
        for p in chain:
            r = _range_at(blob, p)
            entries.append((p, r))
        # first pass: remap
        new = []
        for p, r in entries:
            if not r:
                new.append(None); continue
            lt, lo, ut, hi = r
            if lt == 2 and ut == 2:
                new.append(None); continue    # spans everything; leave alone
            nlo, nhi = remap.bounds(lo, hi)
            new.append(None if nlo is None or nhi is None else [nlo, nhi])
        # second pass: keep the partition intact, ending on the new run time
        enforce_partition(new, remap.point(total))
        # write back
        for (p, r), val in zip(entries, new):
            if val is None or not r:
                continue
            lt, lo, ut, hi = r
            if (val[0], val[1]) != (lo, hi):
                struct.pack_into('<i', data, off + p + 1, val[0])
                struct.pack_into('<i', data, off + p + 6, val[1])
                moved += 1
    return moved
