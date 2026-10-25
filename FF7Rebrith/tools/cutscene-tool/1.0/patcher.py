"""
patcher.py — apply a ripple edit plan to FF7 Rebirth cutscene .uasset files.

Every timing value in these packages is a 32-bit tick count inside a fixed-size
field, so the edit can be applied as an **in-place byte patch**: no offsets,
export sizes or bundle tables change, which keeps the Zen package structurally
identical and safe to repack.

What gets remapped:
  * MovieScene PlaybackRange / SelectionRange           (MovieSceneFrameRange)
  * every section's SectionRange                        (MovieSceneFrameRange)
  * FrameNumber properties (pre/post roll, offsets)
  * MovieSceneFloatChannel Times arrays                 (camera + character anim)
  * MovieSceneParticleChannel Times arrays              (VFX activation)
  * event Times arrays inside the compiled templates    (voice/text/SE/...)

Usage:
  python3 patcher.py <EV_folder> <editplan.json> <out_dir> <Mappings.usmap>
"""
import os, sys, json, struct, shutil, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zenasset
import evalfield
from zenasset import Usmap
import transforms as T
from payload_events import MAGIC

BOUND = ['Exclusive', 'Inclusive', 'Open']

# FrameNumber properties that are lengths/offsets, not points on the timeline
# Everything V1 did not do. V1 is the build that cut cleanly in-game, so these
# are the only candidates for the regression and each can be turned off on its
# own. All default to V1 behaviour being OFF (i.e. the newer behaviour on);
# build_mod flips them.
OPTS = {
    'evalfield': True,        # rewrite the baked evaluation field
    'shots': True,            # square camera cuts into a partition
    'durations': False,       # True = shift duration fields as V1 did
    'holdvalues': True,       # correct the values of keys collapsed onto a join
    # Where collapsed sections go. 'camera' moves only camera cut sections,
    # which is the case parking was actually proven on — it cured the dead frame
    # over the surviving shot. 'all' extends it to every section class, which
    # also relocates dozens of skeletal animation, spawn and visibility sections
    # per scene; that is a much bigger claim about engine behaviour and it is
    # not proven. 'none' leaves everything collapsed on the join.
    'parkempty': 'camera',    # 'camera' | 'all' | 'none'
    'templates': True,        # remap section times baked into the compiled templates
    'dropactorevents': False, # neutralise show/hide commands from removed footage
    'collapsestate': True,    # make collapsed state triggers agree on the final state
    'relocatecues': True,     # carry the plan's relocateCues back across the join
    'cutsubtitles': True,     # drop captions belonging to footage the cut removed
}


def _eval_at(times, vals, t, step=False):
    """What a key array reads at time t.

    `step` is for stepped channels — visibility, spawn, enum switches. They hold
    the last key's value until the next one rather than interpolating, so
    averaging between two keys would invent a state that never existed.
    """
    if not times:
        return None
    if t <= times[0]:
        return vals[0]
    if t >= times[-1]:
        return vals[-1]
    i, lo, hi = 0, 0, len(times) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if times[mid] <= t:
            i = mid; lo = mid + 1
        else:
            hi = mid - 1
    if step or times[i] == t or i + 1 >= len(times):
        return vals[i]
    t0, t1 = times[i], times[i + 1]
    v0, v1 = vals[i], vals[i + 1]
    if t1 == t0:
        return v0
    return v0 + (v1 - v0) * float(t - t0) / float(t1 - t0)


def _hold_value(times, vals, a, b, total, step=False):
    """The value a curve should hold across a removed range [a, b).

    Every key inside the range collapses onto the join, and the engine takes the
    last key at that time — which is the value from the far side of the cut. For
    a middle cut that is the value playback resumes on, so it wants the value at
    `b`. For a cut that runs to the end nothing resumes: the scene stops at `a`,
    so the last frame must hold the value it had at `a`, not the pose the actor
    was in 24 seconds later.
    """
    return _eval_at(times, vals, a if b >= total else b, step)

# Stepped keyed channels: Times plus a parallel Values array, no interpolation.
# Float curves are handled separately because they serialise natively.
KEYED_CHANNELS = {
    'MovieSceneBoolChannel': 'bool',
    'MovieSceneByteChannel': 'byte',
    'MovieSceneIntegerChannel': 'int',
}

DURATION_FIELDS = {
    'PreRollFrames', 'PostRollFrames',
    'StartFrameOffset', 'EndFrameOffset', 'FirstLoopStartFrameOffset',
    'StartOffset', 'EndOffset', 'ForcedTime',
}


# ---------------- time mapping ----------------

class Remap:
    """Maps original ticks onto the edited timeline defined by removed ranges."""

    def __init__(self, removes, total):
        self.rem = sorted([tuple(r) for r in removes])
        self.total = total
        self.removed_total = sum(b - a for a, b in self.rem)

    def shift(self, t):
        """Cumulative removed time strictly before t."""
        d = 0
        for a, b in self.rem:
            if b <= t:
                d += b - a
            elif a < t:
                return None          # t falls inside a removed range
            else:
                break
        return d

    def point(self, t, inside='clamp'):
        """Remap a single tick. Ticks inside a cut collapse to the join."""
        d = self.shift(t)
        if d is not None:
            return t - d
        for a, b in self.rem:
            if a <= t < b:
                return a - (self.shift(a) or 0)
        return t

    def bounds(self, lo, hi):
        """Remap a [lo,hi) range; a range wholly inside a cut collapses."""
        return self.point(lo), self.point(hi)


# ---------------- locating tick fields ----------------

class Tracker(T.Reader2):
    """Reader2 that records the byte offset of every timing field it parses."""

    def __init__(self, path, usmap):
        self.hits = []          # (offset, kind, value)
        self.channels = []      # one record per keyed channel (float or stepped)
        self._cap = None        # channel currently being captured
        super().__init__(path, usmap)

    def scan(self):
        """Parse every export, recording tick field offsets.

        If an export fails to parse we discard everything it contributed: once a
        parse derails, later offsets come from misaligned data and writing to them
        would corrupt the package. Better to leave that export untouched.
        """
        self.skipped = []
        for i, cn in enumerate(self.classNames):
            if cn is None or i not in self.dataOffset:
                continue
            mark = len(self.hits)
            cmark = len(self.channels)
            try:
                self._scan_export(i, cn)
            except Exception as e:
                del self.hits[mark:]          # roll back this export's hits
                del self.channels[cmark:]     # ...and its channels
                self.skipped.append((i, cn, repr(e)[:60]))
        return self.hits

    def _scan_export(self, i, cn):
        r = zenasset.Reader(self.d, self.dataOffset[i])
        self._walk(r, cn)

    def _walk(self, r, structName, depth=0):
        """Mirror of read_unversioned, but recording offsets of timing fields."""
        schema = self.usmap.schema_chain(structName)
        if not schema:
            raise KeyError(structName)
        frags = []
        while True:
            packed = r.read('<H')
            f = {'skip': packed & 0x7F, 'hasZeros': bool(packed & 0x80),
                 'values': packed >> 9, 'last': bool(packed & 0x100)}
            frags.append(f)
            if f['last']:
                break
        nz = sum(f['values'] for f in frags if f['hasZeros'])
        zeros = []
        if nz > 0:
            if nz <= 8:   raw = r.read('<B')
            elif nz <= 16: raw = r.read('<H')
            else:
                raw = 0
                for w in range((nz + 31)//32):
                    raw |= r.read('<I') << (32*w)
            zeros = [(raw >> k) & 1 for k in range(nz)]
        by = {}
        for gi, p in schema:
            by.setdefault(gi, p)
        idx = 0; zi = 0
        for f in frags:
            idx += f['skip']
            for _ in range(f['values']):
                isZero = False
                if f['hasZeros']:
                    isZero = bool(zeros[zi]); zi += 1
                p = by.get(idx)
                if p is None:
                    raise KeyError(idx)
                self._value(r, p, isZero, depth)
                idx += 1

    def _value(self, r, p, isZero, depth):
        t = p['type']
        if t == 'BoolProperty':
            if not isZero: r.read('<B')
            return
        if isZero:
            return
        if t == 'StructProperty':
            sn = p.get('struct')
            if sn == 'MovieSceneFrameRange':
                off = r.o
                lt = r.read('<B'); lo = r.read('<i'); ut = r.read('<B'); hi = r.read('<i')
                self.hits.append((off, 'range', (lt, lo, ut, hi)))
                return
            if sn == 'FrameNumber':
                off = r.o; v = r.read('<i')
                # PreRoll/PostRoll are durations and the *Offset fields index into an
                # animation — none of them are positions on the timeline, so shifting
                # them by the removed time would be meaningless.
                if OPTS['durations'] or p['name'] not in DURATION_FIELDS:
                    self.hits.append((off, 'frame', v))
                return
            if sn == 'MovieSceneFloatChannel':
                self._float_channel(r)
                return
            if sn in zenasset.NATIVE_STRUCTS:
                zenasset.NATIVE_STRUCTS[sn](r, self)
                return
            if sn in KEYED_CHANNELS:
                # A stepped channel — visibility, spawn, an enum switch. Its keys
                # collapse onto a join exactly like a float curve's, and its
                # values need the same correction, or a spotlight ends up on
                # when it should be off. Capture the two parallel arrays while
                # the normal walk goes past them.
                prev = self._cap
                self._cap = {'kind': KEYED_CHANNELS[sn], 'times': [], 'vals': [],
                             'vals_off': None, 'stride': None}
                try:
                    self._walk(r, sn, depth+1)
                    c = self._cap
                    if c['times'] and c['vals_off'] is not None \
                            and len(c['vals']) == len(c['times']):
                        self.channels.append(c)
                finally:
                    self._cap = prev
                return
            self._walk(r, sn, depth+1)
            return
        if t == 'ArrayProperty':
            n = r.read('<i')
            inner = p['inner']
            # a bare array of FrameNumber/int is a times array (particle channels etc.)
            if inner.get('struct') == 'FrameNumber':
                for _ in range(n):
                    off = r.o; v = r.read('<i')
                    self.hits.append((off, 'frame', v))
                    if self._cap is not None and p['name'] == 'Times':
                        self._cap['times'].append(v)
                return
            if self._cap is not None and p['name'] == 'Values' and \
                    inner['type'] in ('BoolProperty', 'ByteProperty',
                                      'EnumProperty', 'IntProperty'):
                stride = 4 if inner['type'] == 'IntProperty' else 1
                self._cap['vals_off'] = r.o
                self._cap['stride'] = stride
                for k in range(n):
                    if stride == 4:
                        self._cap['vals'].append(
                            struct.unpack_from('<i', r.d, r.o + 4*k)[0])
                    else:
                        self._cap['vals'].append(r.d[r.o + k])
                r.o += stride * n
                return
            for _ in range(n):
                self._value(r, inner, False, depth+1)
            return
        if t == 'MapProperty':
            r.read('<i'); n = r.read('<i')
            for _ in range(n):
                self._value(r, p['key'], False, depth+1)
                self._value(r, p['value'], False, depth+1)
            return
        if t == 'SetProperty':
            r.read('<i'); n = r.read('<i')
            for _ in range(n):
                self._value(r, p['inner'], False, depth+1)
            return
        # everything else: reuse the normal reader to advance correctly
        self.read_value(r, p, False, depth)

    def _float_channel(self, r):
        r.o += 2                                     # extrapolation
        es, n = struct.unpack_from('<ii', r.d, r.o); r.o += 8
        times_off = r.o
        times = []
        for k in range(n):
            off = r.o + 4*k
            v, = struct.unpack_from('<i', r.d, off)
            times.append(v)
            self.hits.append((off, 'frame', v))
        r.o += es * n
        ves, vn = struct.unpack_from('<ii', r.d, r.o); r.o += 8
        vals_off = r.o
        # FMovieSceneFloatValue is 28 bytes and opens with the float32 value
        vals = [struct.unpack_from('<f', r.d, vals_off + ves*k)[0] for k in range(vn)]
        if n and vn == n:
            self.channels.append({'kind': 'float', 'times_off': times_off,
                                  'times': times, 'vals_off': vals_off,
                                  'stride': ves, 'vals': vals})
        r.o += ves * vn
        r.o += 16                                    # default, hasDefault, tickres


def _read_fstring_at(d, o):
    ln, = struct.unpack_from('<i', d, o)
    if ln <= 0:
        return None, o + 4, 0, 0
    return d[o+4:o+4+ln].split(b'\0')[0].decode('latin1'), o + 4 + ln, o + 4, ln


def payload_all_fields(data, pos, size):
    """[(key, type, value, offset)] for one event payload.

    Same walk as payload_name_fields, but it keeps booleans and reports where
    each value sits so it can be rewritten in place. A BoolProperty stores its
    value in the property header — one byte, fixed size.
    """
    out = []
    o = pos + 8
    end = pos + 8 + size
    while o < end - 4:
        try:
            name, o2, _, _ = _read_fstring_at(data, o)
        except struct.error:
            break
        if not name or name == 'None':
            break
        o = o2
        try:
            typ, o, _, _ = _read_fstring_at(data, o)
            if typ is None:
                break
            sz, _ai = struct.unpack_from('<ii', data, o); o += 8
        except struct.error:
            break
        base = re.sub(r'_\d+_[0-9A-F]{32}$', '', name)
        if typ in ('EnumProperty', 'ByteProperty'):
            _e, o, _, _ = _read_fstring_at(data, o); o += 1 + sz
        elif typ == 'BoolProperty':
            out.append((base, typ, bool(data[o]), o)); o += 2
        elif typ == 'StructProperty':
            _s, o, _, _ = _read_fstring_at(data, o); o += 16 + 1 + sz
        elif typ == 'ArrayProperty':
            _i, o, _, _ = _read_fstring_at(data, o); o += 1 + sz
        else:
            o += 1
            if typ in ('NameProperty', 'StrProperty'):
                val, _o2, soff, _slen = _read_fstring_at(data, o)
                if val:
                    out.append((base, typ, val, soff))
            o += sz
    return out


# Payload flags that describe an actor's state rather than a one-off action.
# These are the ones worth forcing to agree across a join.
STATE_FLAGS = ('Hidden',)


def payload_name_fields(data, pos, size, keys):
    """[(offset, length, key, value)] for the named string fields in one payload."""
    out = []
    o = pos + 8
    end = pos + 8 + size
    while o < end - 4:
        try:
            name, o2, _, _ = _read_fstring_at(data, o)
        except struct.error:
            break
        if not name or name == 'None':
            break
        o = o2
        try:
            typ, o, _, _ = _read_fstring_at(data, o)
            if typ is None:
                break
            sz, _ai = struct.unpack_from('<ii', data, o); o += 8
        except struct.error:
            break
        base = re.sub(r'_\d+_[0-9A-F]{32}$', '', name)
        if typ in ('EnumProperty', 'ByteProperty'):
            _e, o, _, _ = _read_fstring_at(data, o); o += 1 + sz
        elif typ == 'BoolProperty':
            o += 2
        elif typ == 'StructProperty':
            _s, o, _, _ = _read_fstring_at(data, o); o += 16 + 1 + sz
        elif typ == 'ArrayProperty':
            _i, o, _, _ = _read_fstring_at(data, o); o += 1 + sz
        else:
            o += 1
            if typ in ('NameProperty', 'StrProperty') and base in keys:
                val, _o2, soff, slen = _read_fstring_at(data, o)
                if val:
                    out.append((soff, slen, base, val))
            o += sz
    return out


# cue payloads whose name we blank when the cue falls inside a removed range.
# Voice/SE are one-shots that would otherwise all fire together at the join.
# BGM and SendStateTrigger are left alone on purpose: music should keep playing
# and story triggers still need to fire for the game to progress.
SILENCE_KEYS = ('VoiceName', 'SeName')

# Show/hide commands for actors. A cutscene swaps between several copies of a
# character and manages which one is on screen with these. When a cut removes
# the stretch they live in, they all collapse onto the join and fire at once,
# and whichever lands last wins — which can leave a double visible for the rest
# of the scene with nothing later to switch it off. Neutralising the ones that
# came from removed footage instead carries the pre-cut state across the join.
# Opt-in, because the opposite choice is defensible: those commands are also
# what the scene expects to have run by the time it resumes.
ACTOR_KEYS = ('ActorName',)

# ---------------- switching a caption off ----------------
#
# `SILENCE_KEYS` works because a sound whose name no longer resolves plays
# nothing: a missed lookup is silence, and silence is what was wanted. A
# caption behaves the opposite way. Break the name and the game still draws
# something — the broken label itself — so a subtitle disabled the way a sound
# is disabled comes out as gibberish on screen rather than as nothing. That is
# not a subtler kind of failure; it is the rename working exactly as designed
# against a system where a miss is visible.
#
# There is a flag meant for this. Every subtitle payload is a `Clip_SubTitle`
# carrying `TextLabel`, `Language` and a `BoolProperty` called `Enable`, and a
# line is a pair of them sharing a label: `Enable` set where the caption is
# raised, clear where it is dropped. Clearing the byte on the "on" payload
# means the caption is never raised, so there is nothing to look up and nothing
# to draw. One byte, no resize — the same edit `collapsestate` and the
# visibility pins already make to `Hidden`.
#
# Measured over all 870 `_Text` assets in the game: 40,532 subtitle payloads,
# every one of them carrying `Enable`. There is no second shape to fall back
# for.
#
# WHICH payloads to clear is the part that needs care, because a line is never
# one payload:
#
#   * it appears twice over, once in its section export and once in the
#     compiled template, and a shipping build evaluates the second one;
#   * 44 lines carry per-language variants (JP/US/DE/FR) sitting at *different*
#     ticks. `$C3510_MAIN_3100_1800_00_sep` in EV_FOREE_8514 opens at 2962400
#     in Japanese, 3001600 in English and 3003200 in German. Matching the one
#     tick the editor recorded clears the Japanese caption and leaves the
#     English one on screen — a bug that would only ever show up for somebody
#     playing in the language the editor did not happen to pair.
#
# So a line is matched over a *window* rather than at a tick. Matching by label
# alone would be wrong the other way round: 176 labels are used more than once
# within their own scene, and switching one off would take the other with it.
#
# What separates the two cases is measured, not assumed. The language variants
# of a single line always overlap in time — 54 of 54, the smallest overlap
# being 36% of the Japanese range — and two uses of one label never do: 0 of 86
# consecutive pairs, the tightest sitting exactly end-to-start. So the window
# is the stretch over which *some* copy of the label is up, which is read off
# the asset by counting: a line opens where the count of raised captions goes
# from none to one and closes where it returns to none. That needs no threshold
# and, usefully, no `Language` — the count says which payloads belong together
# without anything having to pair them by name. The plan carries the same tick
# it always did and the window is derived here, so a plan saved before any of
# this switches a caption off correctly in every language.


def subtitle_switches(data, blocks, label=None):
    """`[(times offset, tick, raises, enable offset)]` for subtitle payloads.

    `raises` says whether the payload puts a caption up or takes it down, and
    `enable offset` is where that byte sits, ready to be rewritten in place.
    Restricted to one `TextLabel` when `label` is given.
    """
    out = []
    for toff, tick, pos, size in blocks:
        lab = flag = None
        for key, typ, val, off in payload_all_fields(data, pos, size):
            if key == 'TextLabel' and typ != 'BoolProperty':
                lab = val
            elif key == 'Enable' and typ == 'BoolProperty':
                flag = (bool(val), off)
        if lab is None or flag is None:
            continue
        if label is not None and lab != label:
            continue
        out.append((toff, tick, flag[0], flag[1]))
    return out


def subtitle_lines(data, blocks, label):
    """`[(start, end, [enable offsets], [raise ticks])]` — one per appearance.

    A line is the stretch over which at least one copy of the label is up. The
    sweep opens a line when the count of raised captions leaves zero and closes
    it when the count comes back to zero, so the two or three language variants
    of one line — which always overlap — arrive as a single entry, while two
    separate uses of the label — which never do — stay apart. At equal ticks a
    drop is counted before a raise, which is what keeps two uses meeting
    exactly end-to-start from being read as one.

    The offsets are of the "on" payloads only, including both the section
    export's copy and the compiled template's. Those are the bytes that decide
    whether a caption is ever raised.

    An asset with an unpaired event (31 exist across the game, out of 40,532
    payloads) cannot send the count negative: it is clamped, and a line left
    open at the end of the sweep is closed at its last event.
    """
    events = sorted(
        ((tick, raises, off) for _toff, tick, raises, off
         in subtitle_switches(data, blocks, label)),
        key=lambda e: (e[0], e[1]),        # a drop sorts before a raise
    )
    lines, depth, cur = [], 0, None
    for tick, raises, off in events:
        if raises:
            if cur is None:
                cur = [tick, tick, [], []]
            cur[1] = max(cur[1], tick)
            cur[2].append(off)
            cur[3].append(tick)
            depth += 1
        else:
            depth = max(0, depth - 1)
            if cur is not None:
                cur[1] = max(cur[1], tick)
                if depth == 0:
                    lines.append(tuple(cur))
                    cur = None
    if cur is not None:
        lines.append(tuple(cur))
    return lines


def clear_subtitle(data, blocks, label, tick):
    """Stop one line ever being raised. Returns the number of bytes changed.

    `tick` is where the plan says the line starts, which is where one of its
    language variants opens — so the line meant is the one that *raises* a
    caption at that tick, and every "on" payload of that line is then cleared:
    both copies, and every language.

    Asking instead which line is merely up at that moment is not good enough,
    and the assets say so. Two uses of one label can meet exactly end to start
    — the tightest of the 86 gaps measured is zero — and a tick on that seam
    belongs to both, so switching the second one off took the first with it.
    Matching the raise is unambiguous where a range containing it is not.

    The label itself is deliberately left intact. It is what the line's own
    "off" payload is matched by, and a caption that is never raised needs no
    name broken. Breaking it is what put gibberish on screen to begin with.
    """
    snap = bytes(data)
    lines = subtitle_lines(snap, blocks, label)
    hits = [ln for ln in lines if tick in ln[3]]
    if not hits:
        # A plan pointing between the raises — an older extraction paired the
        # line differently — still means the line that is up at that moment.
        hits = [ln for ln in lines if ln[0] <= tick < ln[1]]
    if not hits:
        # And failing that, the payload sitting exactly there: what a plan
        # naming a line this walk could not pair still asks for.
        hits = [(tick, tick,
                 [off for _toff, t, raises, off
                  in subtitle_switches(snap, blocks, label)
                  if raises and t == tick], [tick])]
    changed = 0
    for _start, _end, offsets, _ticks in hits:
        for off in offsets:
            if data[off]:
                data[off] = 0
                changed += 1
    return changed


# ---------------- carrying cues back across a cut ----------------
#
# A cut that swallows a fade leaves the scene ending on a hard frame, and one
# that swallows a SwitchStreamingVolume leaves the next scene's sky, lighting
# and sub-levels unloaded — and can swallow the trigger that puts the world in
# the state the next scene expects. The editor's collapse.py decides where each
# one goes; this end only carries it out.
#
# Only cues the editor lists in `relocateCues` are touched, and only by
# rewriting the int32 tick in their event Times arrays — same size, in place,
# exactly like every other tick this file rewrites.
#
# Moving the tick is sufficient: measured over 16 scenes, not one event tick
# introduces an evaluation-field boundary of its own (49 coincide with another
# section's boundary, 0 stand alone, 31 are not boundaries at all), so the
# field is never refined by an event section and nothing but the tick decides
# when one fires. SILENCE_KEYS above is the same fact from the other side —
# swallowed voice and SE cues have to be renamed precisely because, collapsed
# onto the join, they still fire.
#
# Every payload appears twice: once in its own section export and once as a
# compiled template. Matching by payload rather than by offset moves both,
# which is required — the compiled copy is the one a shipping build evaluates.

#: Payload keys that say *which* cue this is. A block is a candidate only if
#: every one of these it carries is also in the plan's `match` and agrees, so a
#: fade is never confused with an actor command that happens to share its tick.
DISCRIMINATORS = (
    'From', 'To', 'Frame', 'White',
    'VolumeLabel', 'SwitchLabel', 'SwitchType',
    'Labels', 'Hidden', 'WithoutCollision',
    'TargetName', 'MovieName',
    'ActorName', 'ActorNames', 'SeName', 'VoiceName', 'MusicName',
    'TextLabel', 'TriggerID', 'CharaSpec', 'Reference',
)


def _block_matches(fields, want):
    """Does this payload identify the cue the plan is describing?

    `fields` is what payload_all_fields could read — names, strings and bools.
    Floats, ints and arrays are invisible to that walk, so a fade is identified
    by its tick plus `White`, and a streaming command by its volume and switch
    labels. Requiring at least one visible key to agree, and none to disagree,
    is what stops the tick being enough on its own.
    """
    seen = 0
    for key, _typ, val, _off in fields:
        if key not in DISCRIMINATORS:
            continue
        if key not in want:
            return False                   # carries something the cue does not
        if want[key] != val:
            return False
        seen += 1
    return seen > 0


def relocation_offsets(data, blocks, moves, report, label):
    """{time_offset: new_tick} for every cue the plan asks to carry across.

    Refusals are reported rather than swallowed: a cue that was meant to be
    preserved and silently was not is the failure this whole feature exists to
    remove.
    """
    out = {}
    if not moves:
        return out
    raw = bytes(data)
    for m in moves:
        try:
            tick = int(m['tick'])
            new = int(m['newTick'])
        except (KeyError, TypeError, ValueError):
            continue
        want = m.get('match') or {}
        hit = []
        for toff, btick, pos, size in blocks:
            if btick != tick:
                continue
            if _block_matches(payload_all_fields(raw, pos, size), want):
                hit.append(toff)
        if not hit:
            report.setdefault('relocateMissed', []).append(
                '%s: %s at %d not found' % (label, m.get('label') or m.get('clip'), tick))
            continue
        for toff in hit:
            out[toff] = new
        report.setdefault('relocated', []).append(
            '%s: %s %d -> %d (%d cop%s)'
            % (label, m.get('label') or m.get('clip'), tick, new,
               len(hit), 'y' if len(hit) == 1 else 'ies'))
    return out


def check_relocation_order(blocks, overrides, report, label, remap=None):
    """Drop any move that would leave an event Times array out of order.

    The arrays are read as sorted — `compiled_event_blocks` finds them by that
    property and the engine's own lookup depends on it. Every cue we move sits
    alone in its array, so this never fires on the assets we have; it is here
    so that if one day it would, the cue is left where it was and said so
    rather than quietly corrupting a lookup.
    """
    if not overrides:
        return overrides
    # Entries of one Times array are consecutive int32s, so they sit 4 bytes
    # apart; a bigger gap means a different array.
    order = sorted(blocks, key=lambda b: b[0])
    groups, cur = [], []
    for b in order:
        if cur and b[0] - cur[-1][0] != 4:
            groups.append(cur); cur = []
        cur.append(b)
    if cur:
        groups.append(cur)

    bad = set()
    for g in groups:
        # Compare in ONE space. An entry we did not move still gets remapped
        # later, so checking its original tick against a moved entry's edited
        # one compares two different clocks and can pass or fail by luck.
        vals = [overrides[toff] if toff in overrides
                else (remap.point(tick) if remap else tick)
                for toff, tick, _p, _s in g]
        if all(y >= x for x, y in zip(vals, vals[1:])):
            continue
        for toff, tick, _p, _s in g:
            if toff in overrides:
                bad.add(toff)
                report.setdefault('relocateRefused', []).append(
                    '%s: tick %d left in place — moving it would unsort its array'
                    % (label, tick))
                # The same fact as a number, because `build_mod.verify` has to
                # act on it and must not do so by parsing English. A refusal
                # here is a decision, not a failure: the cue is remapped onto
                # the join like any other tick inside a cut, so it still fires.
                # Without this the build was failed for a plan the patcher had
                # already corrected — which is what EV_GRASE_2280 did.
                report.setdefault('relocateRefusedTicks', []).append(int(tick))
    for toff in bad:
        overrides.pop(toff, None)
    return overrides


def _event_runs(data):
    """Payload blocks grouped into the runs that share one Times array."""
    magics = [m.start() for m in re.finditer(re.escape(MAGIC), data)]
    runs = []; prev = None
    for pos in magics:
        try:
            sz, = struct.unpack_from('<i', data, pos+4)
        except struct.error:
            continue
        if sz < 0 or pos + 8 + sz > len(data):
            continue
        if runs and prev is not None and 0 <= pos - prev <= 64:
            runs[-1].append(pos)
        else:
            runs.append([pos])
        prev = pos + 8 + sz
    return runs


def times_for_run(data, first, n, max_tick):
    """`(offset, ticks)` of the Times array in front of a run, or None.

    Two passes, and the second only runs when the first found nothing.

    The strict pass is the original rule: the candidate must be ascending and
    every tick must sit inside the scene's playback range. That range test is
    what makes a backwards byte search reliable, so it stays first.

    But it was also all-or-nothing, and real arrays do carry ticks past the
    playback end. EV_FOREE_8512's five streaming cues share

        [0, 912800, 1282400, 5672000, 5828000]     playback ends at 1282400

    and the two stragglers threw away the whole array - so the patcher never
    found those cues and never remapped them. The scene rippled 9.1s earlier
    around them: the `OtherSky_Black` preload stayed 9.1s late, and the switch
    that consumes it stayed at 1282400, past the new end of 1064000, where it
    can never fire at all.

    The relaxed pass asks only for ascending, non-negative ticks that *start*
    inside the scene - enough structure to not match noise, without demanding
    that a real array be tidy. Additive by construction: every array the strict
    pass matches is matched exactly as it was, and only runs that previously
    matched nothing gain a result.

    Same fault as `evalfield`'s frame-alignment rule in LIGHTING.md - a
    property that data usually has, mistaken for one it cannot help having.
    """
    relaxed = None
    for back in range(8, 48):
        cnt_pos = first - back
        if cnt_pos < 0:
            break
        try:
            n_kv, = struct.unpack_from('<I', data, cnt_pos)
        except struct.error:
            break
        if n_kv != n:
            continue
        t_pos = cnt_pos - 4*n - 4
        if t_pos < 0:
            continue
        try:
            n_t, = struct.unpack_from('<I', data, t_pos)
            if n_t != n:
                continue
            vals = struct.unpack_from('<%di' % n, data, t_pos + 4)
        except struct.error:
            continue
        if vals[0] < 0 or not all(y >= x for x, y in zip(vals, vals[1:])):
            continue
        if all(0 <= v <= max_tick for v in vals):
            return t_pos, list(vals)
        if relaxed is None and vals[0] <= max_tick:
            relaxed = (t_pos, list(vals))
    return relaxed


def compiled_event_blocks(data, max_tick):
    """[(time_offset, tick, payload_pos, payload_size)] for every compiled event."""
    out = []
    for run in _event_runs(data):
        n = len(run); first = run[0]
        found = times_for_run(data, first, n, max_tick)
        if not found:
            continue
        t_pos, vals = found
        for k, (pos, v) in enumerate(zip(run, vals)):
            sz, = struct.unpack_from('<i', data, pos+4)
            out.append((t_pos + 4 + 4*k, v, pos, sz))
    return out


def compiled_event_times(data, max_tick):
    """Offsets of the event Times arrays that sit in the compiled templates."""
    out = []
    for run in _event_runs(data):
        found = times_for_run(data, run[0], len(run), max_tick)
        if not found:
            continue
        t_pos, vals = found
        for k, v in enumerate(vals):
            out.append((t_pos + 4 + 4*k, 'frame', v))
    return out


# ---------------- patching ----------------

def patch_file(src, dst, remap, usmap, max_tick, report, silence=True,
               evalfield_ok=True, frame=None, moves=None, pins=None):
    data = bytearray(open(src, 'rb').read())
    hits = []
    tr = None
    try:
        tr = Tracker(src, usmap)
        hits.extend(tr.scan())
    except Exception as e:
        report.setdefault('warnings', []).append('%s: structural scan failed (%r)'
                                                 % (os.path.basename(src), e))

    # --- silence one-shot cues that sit wholly inside a removed range ---------
    # They can't be deleted (that would resize the array and break the in-place
    # patch) and remapping puts them all on the join, where they would fire at
    # once. Renaming the cue makes the sound lookup miss, so nothing plays.
    silenced = []
    blocks = compiled_event_blocks(bytes(data), max_tick)

    # --- cues the plan asks to carry back across the join --------------------
    # Worked out before anything else touches the ticks, so the match is made
    # against the ORIGINAL times the plan was written from.
    relocated = {}
    if OPTS.get('relocatecues') and moves:
        try:
            relocated = relocation_offsets(data, blocks, moves, report,
                                           os.path.basename(src))
            # Ordering is checked HERE as well as at the end, because the
            # silencing pass below has to know which moves will really happen.
            # A move that survives means the cue keeps its name; one that is
            # refused means the cue is still lost to the cut and must be
            # silenced like any other. Deciding that against a set that might
            # yet shrink is how a refused move would leave a sound firing on
            # the join at full volume. Running the check twice is safe: it only
            # ever removes entries, and the ones it removed are already gone.
            relocated = check_relocation_order(blocks, relocated, report,
                                               os.path.basename(src), remap)
        except Exception as e:
            relocated = {}
            report.setdefault('warnings', []).append(
                '%s: cues not relocated (%r)' % (os.path.basename(src), e))

    keys = SILENCE_KEYS + (ACTOR_KEYS if OPTS.get('dropactorevents') else ())
    rescued = []
    if silence:
        for _toff, tick, pos, size in blocks:
            # A cue the plan is carrying to a new time is not lost to the cut,
            # so it must keep the name the game looks up. Silencing is for cues
            # that stay where the edit swallowed them.
            #
            # This is what makes dragging a sound or a line of dialogue OUT of
            # a cut work at all. Without it the rename still fired — the cue
            # arrived at its new tick with a broken name, and the rescue was
            # silently undone by the pass that runs three lines further down.
            if _toff in relocated:
                if any(a <= tick < b for a, b in remap.rem):
                    rescued.append(tick)
                continue
            # Everything the cut removes, the cue sitting exactly on the cut
            # start included. `shift` calls that one a survivor because it maps
            # to itself, but it belongs to the shot being deleted: left alone it
            # lands on the join beside the cue that resumes the scene, and two
            # stems get started on the same tick. Whichever the engine honours
            # last is what you hear, and half the time it is the audio from
            # footage that is no longer there.
            if not any(a <= tick < b for a, b in remap.rem):
                continue                       # survives the cut
            for soff, slen, key, val in payload_name_fields(bytes(data), pos, size,
                                                            keys):
                if val.startswith('CUT_'):
                    continue
                # FStrings here are null-terminated and the length field counts
                # that byte — only rewrite the characters, never the terminator.
                nul = 1 if slen > 0 and data[soff+slen-1] == 0 else 0
                room = slen - nul
                if room < 1:
                    continue
                new = ('CUT_' + val[4:]) if room >= 4 else 'X' * room
                data[soff:soff+room] = new[:room].ljust(room, 'X').encode('latin1')
                silenced.append('%s=%s' % (key, val))
    if silenced:
        report.setdefault('silenced', []).extend(silenced)
    if rescued:
        report.setdefault('rescued', []).append(
            '%s: %d cue(s) carried out of a cut and left audible'
            % (os.path.basename(src), len(rescued)))

    # --- captions the cut swallowed ------------------------------------------
    # The pass above covers voice and SE because those are the cues that arrive
    # audibly on the join. A caption collapses the same way, and it fails for
    # longer: only the "on" event is inside the cut, so it lands on the join
    # while the matching "off" survives untouched further down the timeline.
    # The line for footage that is no longer there then sits over whatever
    # follows until the moment it was originally due to end. `impact.py`
    # already warns about the mirror image — a line whose "off" is cut and
    # whose "on" is not — which is the same failure seen from the other side.
    #
    # Cleared by the flag rather than by breaking the label, for the reason
    # set out above `clear_subtitle`: a broken caption label gets drawn, not
    # dropped. A caption being carried out of the cut by `relocateCues` is left
    # alone, exactly as a rescued sound keeps its name.
    if (silence and OPTS.get('cutsubtitles')
            and os.path.basename(src).endswith('_Text.uasset')):
        try:
            cleared = 0
            for toff, tick, raises, off in subtitle_switches(bytes(data), blocks):
                if not raises or toff in relocated:
                    continue
                if not any(a <= tick < b for a, b in remap.rem):
                    continue
                if data[off]:
                    data[off] = 0
                    cleared += 1
            if cleared:
                report.setdefault('cutSubtitles', []).append(
                    '%s: %d caption payload(s) dropped with the footage they '
                    'belonged to' % (os.path.basename(src), cleared))
        except Exception as e:
            report.setdefault('warnings', []).append(
                '%s: captions not dropped (%r)' % (os.path.basename(src), e))

    # --- make collapsed state triggers agree ---------------------------------
    # A cutscene swaps between several copies of a character and manages which
    # one is on screen with show/hide commands. When a cut removes the stretch
    # they live in, every one of them lands on the join. Whether they all fire,
    # and in what order, is the engine's business — and if the wrong one lands
    # last, a double stays on screen with nothing later in the scene to switch
    # it off.
    #
    # So don't rely on the ordering at all. Work out the state each actor is
    # left in at the END of the removed stretch — which is the state the scene
    # resumes in — and write it into EVERY trigger for that actor collapsing
    # onto that join. They then all say the same thing, and any subset of them
    # firing in any order produces the same result. One byte each, no resize.
    if OPTS.get('collapsestate'):
        try:
            fixed = 0
            for a_, b_ in remap.rem:
                per = {}
                for order, (_toff, tick, pos, size) in enumerate(blocks):
                    if not (a_ <= tick < b_):
                        continue
                    f = payload_all_fields(bytes(data), pos, size)
                    actor = next((v for k, t_, v, _o in f
                                  if k == 'ActorName' and t_ != 'BoolProperty'), None)
                    if actor is None:
                        continue
                    for k, t_, v, off in f:
                        if t_ != 'BoolProperty' or k not in STATE_FLAGS:
                            continue
                        per.setdefault((actor, k), []).append((tick, order, v, off))
                for (actor, k), items in per.items():
                    items.sort(key=lambda x: (x[0], x[1]))
                    final = items[-1][2]
                    for _tk, _o, v, off in items:
                        if v != final:
                            data[off] = 1 if final else 0
                            fixed += 1
                    if len(items) > 1:
                        report.setdefault('collapsedState', []).append(
                            '%s: %s.%s -> %s at join %d (%d trigger(s))'
                            % (os.path.basename(src), actor, k, final,
                               remap.point(a_), len(items)))
            if fixed:
                report.setdefault('collapsedStateBytes', []).append(
                    '%s: %d' % (os.path.basename(src), fixed))
        except Exception as e:
            report.setdefault('warnings', []).append(
                '%s: collapsed state triggers not reconciled (%r)'
                % (os.path.basename(src), e))

    # --- actor visibility the plan pins -------------------------------------
    # Here, for two reasons. It is after `collapsestate`, so a pin is the last
    # word on a Hidden byte rather than something that pass can undo. And it is
    # before a single tick is rewritten, which is the only point at which the
    # file's ticks are still the ORIGINAL ones the plan's windows are written
    # in — comparing a plan window against remapped ticks matched nothing.
    #
    # Whole-scene pins go on first and bounded ones on top, so a bounded pin is
    # an exception carved out of the scene-wide state. Hide for the scene plus
    # Show over one range is "hidden everywhere except there", which is the
    # combination EV_FOREE_8514 needs and neither pin can express alone.
    if pins:
        pinned = 0
        # One command, both copies: the section export and the compiled
        # template. Keyed by tick so the pair moves and flips together.
        grouped = {}
        for toff, tick, pos, size in blocks:
            f = payload_all_fields(bytes(data), pos, size)
            who = next((v for k, t_, v, _o in f
                        if k == 'ActorName' and t_ != 'BoolProperty'), None)
            flags = [off for k, t_, v, off in f
                     if t_ == 'BoolProperty' and k == 'Hidden']
            if not who or not flags:
                continue
            e = grouped.setdefault((who, tick), [tick, [], []])
            e[1].append(toff)
            e[2].extend(flags)
        by_actor = {}
        for (who, _t), e in grouped.items():
            by_actor.setdefault(who, []).append(tuple(e))
        for v in by_actor.values():
            v.sort(key=lambda c: c[0])

        def _set(cmd, val):
            n = 0
            for off in cmd[2]:
                if data[off] != val:
                    data[off] = val
                    n += 1
            return n

        for p_ in pins:
            actor = p_.get('actor')
            cmds = by_actor.get(actor)
            if not actor or not cmds:
                continue
            target = 1 if p_.get('hidden') else 0
            win = p_.get('range')

            if win is None:                       # whole scene
                for c in cmds:
                    pinned += _set(c, target)
                continue
            if len(win) < 2 or win[1] <= win[0]:
                continue

            # A window has to start where it was drawn, and the actor usually
            # has no command there — 8514's last one is 64 seconds earlier, so
            # flipping it turned her on a minute too soon. Ticks are int32s like
            # any other, so MOVE spare commands to the window's edges instead:
            # one to open it, one to close it. Nothing is added, no payload
            # changes, only when they fire.
            #
            # The ones moved are the LAST by tick. Their array has to stay
            # sorted, and the window is later than everything else the actor
            # does, so the tail is the only part that can travel there.
            close = win[1] < max_tick
            need = 2 if close else 1
            outside = 1 - target
            if OPTS.get('relocatecues', True) and len(cmds) > need:
                for c in cmds[:-need]:            # everything before the window
                    pinned += _set(c, outside)
                edges = [(cmds[-need], win[0], target)]
                if close:
                    edges.append((cmds[-1], win[1], outside))
                for cmd, at, val in edges:
                    # A window drawn with the mouse arrives as floats; every
                    # tick in the file is an int32, so round once here rather
                    # than letting a float reach struct.pack_into.
                    where = int(round(remap.point(at)))
                    for toff in cmd[1]:
                        relocated[toff] = where
                    pinned += _set(cmd, val)
                    report.setdefault('pinWindow', []).append(
                        '%s: %s %d -> %d (%s)'
                        % (os.path.basename(src), actor, cmd[0], where,
                           'hidden' if val else 'visible'))
                continue

            # Not enough commands to bound a window. Fall back to rewriting the
            # ones inside it plus the one that governs it - the state then
            # changes from that earlier command, which is said out loud rather
            # than silently.
            inside = [c for c in cmds if win[0] <= c[0] < win[1]]
            before = [c[0] for c in cmds if c[0] < win[0]]
            gov = max(before) if before else None
            want = inside + [c for c in cmds if gov is not None and c[0] == gov]
            for c in want:
                pinned += _set(c, target)
            report.setdefault('pinWindowShort', []).append(
                '%s: %s has %d command(s), too few to bound [%d, %d) - state '
                'changes from %s instead'
                % (os.path.basename(src), actor, len(cmds), win[0], win[1],
                   gov if gov is not None else 'the first one inside'))
        if pinned:
            report.setdefault('pinnedFlags', []).append(
                '%s: %d' % (os.path.basename(src), pinned))

    if relocated:
        relocated = check_relocation_order(blocks, relocated, report,
                                           os.path.basename(src), remap)

    hits.extend((t, 'frame', v) for t, v, _p, _s in blocks)

    # --- the baked evaluation field ------------------------------------------
    # Sections say *what*; this cooked field says *when*, and at runtime it wins.
    # Leaving it alone is why removed shots kept playing and cameras held on.
    if evalfield_ok and OPTS['evalfield']:
        try:
            for i, cn in enumerate(tr.classNames):
                if cn != 'MovieSceneCompiledData' or i not in tr.dataOffset:
                    continue
                n = evalfield.patch(data, tr.dataOffset[i],
                                    tr.exports[i]['serialSize'], remap, max_tick,
                                    frame=frame)
                if n:
                    report.setdefault('evalField', []).append(
                        '%s: %d range(s)' % (os.path.basename(src), n))
        except Exception as e:
            report.setdefault('warnings', []).append(
                '%s: evaluation field not patched (%r)' % (os.path.basename(src), e))

    # --- values of keys that collapse onto a join --------------------------
    # Times are remapped below; a key inside a cut lands on the join along with
    # every other key from that cut. The engine reads the last of them, so the
    # curve ends on a value from the far side of the edit — the deleted pose
    # showing up in the final frames. Same size, so it is rewritten in place.
    if tr is not None and OPTS['holdvalues']:
        try:
            held = 0
            drift = []
            for ch in tr.channels:
                times, vals = ch['times'], ch['vals']
                kind = ch.get('kind', 'float')
                step = kind != 'float'
                fmt = '<f' if kind == 'float' else ('<i' if ch['stride'] == 4 else '<B')
                for a, b in remap.rem:
                    hold = _hold_value(times, vals, a, b, max_tick, step)
                    if hold is None:
                        continue
                    # Keys collapsing onto this join, in array order. They end
                    # up sharing a time, and the two things that read them want
                    # different answers:
                    #
                    #   * the segment arriving at the join interpolates toward
                    #     the FIRST key at that time, and must still land on the
                    #     value the curve had at the cut start — otherwise the
                    #     footage before the cut drifts toward post-cut values
                    #     that have not happened yet
                    #   * evaluation AT the join reads the LAST key, which must
                    #     be the value playback resumes on
                    #
                    # Giving the first key the approach value makes the whole
                    # pre-cut stretch evaluate exactly as it did before the
                    # edit: same endpoints over the same span, so a linear
                    # segment reproduces the original curve point for point.
                    approach = _eval_at(times, vals, a, step)
                    # Everything landing on this join, INCLUDING a key sitting
                    # exactly on the cut start. `shift` calls that one a
                    # survivor because it maps to itself, but after the edit it
                    # is the join: the frame it governs shows what plays after
                    # the cut, not what used to be there. Leaving it alone was
                    # why lights held their pre-cut level across the join with
                    # no key inside the cut to correct them.
                    idx = [k for k, t in enumerate(times) if a <= t < b]
                    # With only ONE key on the join there is nothing to split
                    # the two jobs between, so pick the one that matters here.
                    # A cut reaching the start of the scene has no run-up to
                    # protect, so the join wins outright. Otherwise the join
                    # still wins unless this is the channel's very first key,
                    # in which case it governs the entire stretch before the
                    # cut and the drift would be long rather than one segment.
                    if not idx and b < max_tick and frame:
                        # Nothing collapses onto this join, so no key carries the
                        # value playback resumes on: the curve simply
                        # interpolates straight across the cut. Where the actor
                        # moved during the removed footage they arrive at the
                        # join in the old place and slide to the new one over
                        # the following seconds — which, next to a double
                        # standing correctly, looks like the character twice.
                        #
                        # These sequences keep a key one tick before each
                        # section end. Cuts land on frame boundaries, so a key
                        # at a-1 is never sampled by any frame: giving it the
                        # resume value costs nothing visible and puts the value
                        # where the join can read it.
                        prev = [k for k, t in enumerate(times) if t < a]
                        donated = False
                        if prev:
                            k = prev[-1]
                            if 0 < a - times[k] < frame and hold is not None \
                                    and vals[k] != hold:
                                struct.pack_into(
                                    '<f' if not step else fmt, data,
                                    ch['vals_off'] + ch['stride']*k,
                                    hold if not step else int(round(hold)))
                                held += 1
                                donated = True
                        if not donated and not step and hold is not None:
                            # No key anywhere on the join and none close enough
                            # to lend: the curve has to interpolate straight
                            # across. Harmless when nothing moved during the
                            # removed footage, visible when something did, and
                            # not fixable in place — a key cannot be added
                            # without growing the export. Worth saying out loud
                            # so the cut can be nudged onto a boundary where
                            # keys exist.
                            moved = abs(hold - (approach if approach is not None else hold))
                            if moved > 1.0:
                                drift.append((a, moved))
                        continue
                    lone = None
                    if len(idx) == 1:
                        lone = approach if (idx[0] == 0 and remap.point(a) > 0) else hold
                    for pos, k in enumerate(idx):
                        want = lone if lone is not None else (approach if pos == 0 else hold)
                        if want is None or vals[k] == want:
                            continue
                        if step:
                            want = int(round(want))
                        struct.pack_into(fmt, data,
                                         ch['vals_off'] + ch['stride']*k, want)
                        held += 1
            if held:
                report.setdefault('heldValues', []).append(
                    '%s: %d' % (os.path.basename(src), held))
            if drift:
                by_cut = {}
                for a_, m in drift:
                    by_cut[a_] = max(by_cut.get(a_, 0.0), m)
                for a_ in sorted(by_cut):
                    report.setdefault('joinDrift', []).append(
                        '%s: cut at %d — %d channel(s) interpolate across it, '
                        'worst %.0f units' % (os.path.basename(src), a_,
                                              sum(1 for x, _ in drift if x == a_),
                                              by_cut[a_]))
        except Exception as e:
            report.setdefault('warnings', []).append(
                '%s: collapsed key values not corrected (%r)'
                % (os.path.basename(src), e))

    # every SectionRange/FrameRange offset with its ORIGINAL value, kept so the
    # compiled templates can be matched against what the sections used to say
    range_offsets = {o: v for o, k, v in hits if k == 'range'}

    seen = set(); changed = 0
    for off, kind, val in hits:
        if off in seen:
            continue
        seen.add(off)
        if kind == 'range':
            lt, lo, ut, hi = val
            if lt == 2 and ut == 2:            # Open/Open — spans everything, leave it
                continue
            nlo, nhi = remap.bounds(lo, hi)
            if nhi < nlo: nhi = nlo
            if (nlo, nhi) != (lo, hi):
                struct.pack_into('<BiBi', data, off, lt, nlo, ut, nhi)
                changed += 1
        else:
            if val < 0 or val > max_tick:      # sentinels like -2147483648
                continue
            # A relocated cue is PLACED, not remapped: the editor already
            # decided where it goes on the edited timeline, and remapping that
            # answer would move it a second time.
            nv = relocated[off] if off in relocated else remap.point(val)
            if nv != val:
                struct.pack_into('<i', data, off, int(round(nv)))
                changed += 1
    # --- every collapsed section moves off the join --------------------------
    # A removed shot's section collapses to an empty range that starts on the
    # join — the same tick the surviving shot starts on. Whatever the engine
    # resolves that tie to holds until the next section boundary, so when it
    # picks the removed one the result is a whole shot of wrong content: a
    # camera with no data, a character never spawned, an animation that never
    # advances. It is not confined to camera cuts; skeletal animation, spawn,
    # visibility, transform, colour and attach tracks all collapse the same way.
    # Parking them at the new end puts them past the last live section, where
    # playback has already stopped and nothing can select them. Sections are
    # matched by time rather than array order, so moving them is safe.
    if tr is not None and OPTS['parkempty'] in (True, 'all'):
        try:
            end = remap.point(max_tick)
            secs = {o: v for o, k, v in hits if k == 'range'}
            parked = 0
            for i, cn in enumerate(tr.classNames):
                if not cn or 'Section' not in cn or i not in tr.dataOffset:
                    continue
                if cn == 'MovieSceneCameraCutSection':
                    continue                       # the shots pass owns these
                a0 = tr.dataOffset[i]; b0 = a0 + tr.exports[i]['serialSize']
                here = sorted(o for o in secs if a0 <= o < b0)
                if not here:
                    continue
                off = here[0]                      # SectionRange comes first
                lt, lo, ut, hi = secs[off]
                if lt == 2 and ut == 2:            # Open/Open spans everything
                    continue
                nlo, nhi = remap.bounds(lo, hi)
                if nhi < nlo:
                    nhi = nlo
                if nlo == nhi and nlo != end:
                    struct.pack_into('<BiBi', data, off, lt, end, ut, end)
                    parked += 1
            if parked:
                report.setdefault('parkedSections', []).append(
                    '%s: %d' % (os.path.basename(src), parked))
        except Exception as e:
            report.setdefault('warnings', []).append(
                '%s: collapsed sections not parked (%r)' % (os.path.basename(src), e))

    # --- camera cuts must partition the timeline exactly like the field -------
    # Otherwise a removed shot leaves an empty section while the field still
    # schedules it, the camera-cut track has no camera for that moment, and the
    # view drops to a blank background that holds until the next shot.
    if tr is not None and OPTS['shots']:
        try:
            ranges = {o: v for o, k, v in hits if k == 'range'}
            cams = []
            for i, cn in enumerate(tr.classNames):
                if cn != 'MovieSceneCameraCutSection' or i not in tr.dataOffset:
                    continue
                a = tr.dataOffset[i]; b = a + tr.exports[i]['serialSize']
                here = sorted(o for o in ranges if a <= o < b)
                if here:
                    cams.append((ranges[here[0]][1], here[0], ranges[here[0]]))
            cams.sort()                      # original order = shot order
            new = [list(remap.bounds(v[1], v[3])) for _lo, _o, v in cams]
            end = remap.point(max_tick)
            evalfield.enforce_partition(new, end)
            if OPTS['parkempty'] not in (False, 'none'):
                evalfield.park_empty(new, end)
            for (_lo, off, v), nb in zip(cams, new):
                struct.pack_into('<BiBi', data, off, v[0], nb[0], v[2], nb[1])
            if cams:
                report.setdefault('shots', []).append(
                    '%s: %d' % (os.path.basename(src), len(cams)))
        except Exception as e:
            report.setdefault('warnings', []).append(
                '%s: camera cuts not squared up (%r)' % (os.path.basename(src), e))

    # --- section times baked into the compiled evaluation templates ----------
    # The compiled data holds more than the evaluation field. Every section also
    # gets a baked template, and for skeletal animation that template carries
    # its own copy of the section's start and end as a plain pair of int32s.
    # Those copies are what the animation is actually evaluated against.
    #
    # The camera survived without this because its timing lives in the field we
    # already rewrite — one buried pair in the whole file. A character sequence
    # has hundreds, so the sections moved while every animation went on being
    # evaluated against the original times: characters frozen in place, snapping
    # between poses, appearing at the wrong moment or not at all.
    #
    # We know each section's real before-and-after range from the structural
    # parse, so this is a lookup rather than a guess: find that exact pair of
    # int32s inside a compiled-data export and write the pair we already wrote
    # into the section itself, so template and section cannot disagree. Every
    # match is located against the original bytes before anything is written,
    # so no rewrite can cascade into another.
    if tr is not None and OPTS['templates']:
        try:
            mapping = {}
            for i, cn in enumerate(tr.classNames):
                if not cn or 'Section' not in cn or i not in tr.dataOffset:
                    continue
                a0 = tr.dataOffset[i]; b0 = a0 + tr.exports[i]['serialSize']
                here = sorted(o for o in range_offsets if a0 <= o < b0)
                if not here:
                    continue
                off = here[0]
                lt, lo, ut, hi = range_offsets[off]
                if lt == 2 and ut == 2:
                    continue
                nlo, nhi = struct.unpack_from('<i', data, off + 1)[0], \
                           struct.unpack_from('<i', data, off + 6)[0]
                if (lo, hi) != (nlo, nhi):
                    mapping[(lo, hi)] = (nlo, nhi)
            done = 0
            if mapping:
                for i, cn in enumerate(tr.classNames):
                    if cn != 'MovieSceneCompiledData' or i not in tr.dataOffset:
                        continue
                    a0 = tr.dataOffset[i]; size = tr.exports[i]['serialSize']
                    blob = bytes(data[a0:a0 + size])
                    writes = []
                    for (lo, hi), (nlo, nhi) in mapping.items():
                        pat = struct.pack('<ii', lo, hi)
                        j = blob.find(pat)
                        while j >= 0:
                            writes.append((a0 + j, nlo, nhi))
                            j = blob.find(pat, j + 1)
                    for pos, nlo, nhi in writes:
                        struct.pack_into('<ii', data, pos, nlo, nhi)
                    done += len(writes)
            if done:
                report.setdefault('templateTimes', []).append(
                    '%s: %d' % (os.path.basename(src), done))
        except Exception as e:
            report.setdefault('warnings', []).append(
                '%s: compiled template times not remapped (%r)'
                % (os.path.basename(src), e))

    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    open(dst, 'wb').write(bytes(data))
    assert os.path.getsize(dst) == os.path.getsize(src), 'size changed — not an in-place patch!'
    return changed, len(hits)


SUBSEQ = ['', '_Camera', '_Character', '_Constraint', '_CutEvent', '_Effect',
          '_Light', '_Light_Low', '_Low', '_ManualSE', '_PlannerEvent',
          '_Sound', '_Text', '_Voice']


def retime_subtitles(path, trims, remap, max_tick, tick_rate):
    """Pull each trimmed line's subtitle 'off' event back to the new line end.

    Times arrays must stay ascending, so an event is never moved earlier than
    the one before it — a subtitle may linger slightly rather than corrupt the
    array.

    Only payloads that actually drop the caption are moved. "everything after
    the first tick is an off event" holds for the 9,762 lines that exist in one
    language, and breaks for the 44 that carry per-language variants: those
    open two or three times over, and a later *on* event would be dragged back
    to the trim point and take its caption with it. `Enable` says which is
    which, so it does not have to be inferred from position.
    """
    data = bytearray(open(path, 'rb').read())
    blocks = compiled_event_blocks(bytes(data), max_tick)
    if not blocks:
        return 0, []
    raises = {(toff, tick) for toff, tick, on, _off
              in subtitle_switches(bytes(data), blocks) if on}
    # group by the Times array each event belongs to (contiguous offsets)
    by_label = {}
    for toff, tick, pos, size in blocks:
        for _o, _l, key, val in payload_name_fields(bytes(data), pos, size, ('TextLabel',)):
            by_label.setdefault(val.lstrip('$'), []).append((toff, tick))
    changed, notes = 0, []
    order = sorted(blocks, key=lambda b: b[0])           # by byte offset in the array
    prev_by_off = {}
    for idx, (toff, tick, _p, _s) in enumerate(order):
        prev_by_off[toff] = order[idx-1][1] if idx > 0 else None
    for t in trims:
        name = t['voice']
        entries = sorted(by_label.get(name, []), key=lambda x: x[1])
        if len(entries) < 2:
            continue
        start_tick = entries[0][1]
        want = int(start_tick + t['keepSeconds'] * tick_rate)
        for toff, tick in entries[1:]:                    # every 'off' copy
            if tick <= want or (toff, tick) in raises:
                continue
            floor = prev_by_off.get(toff)
            new = want if floor is None else max(want, floor)
            if new != tick and 0 <= new <= max_tick:
                struct.pack_into('<i', data, toff, new)
                changed += 1
        notes.append('%s subtitle -> %.2fs' % (name, t['keepSeconds']))
    if changed:
        open(path, 'wb').write(bytes(data))
    return changed, notes


# fields naming a cue we can switch off. Most are neutralised by breaking the
# name the game looks up. Two are not: `TextLabel` is cleared with the caption's
# own `Enable` flag, because a caption whose lookup misses is drawn rather than
# dropped, and a `Constraint` is turned round with its own `Detach` flag —
# see `detach_constraint`.
DISABLE_FIELDS = ('VoiceName', 'SeName', 'MusicName', 'TextLabel', 'ActorName')
SEQ_SUFFIX = {'Voice': '_Voice', 'Text': '_Text', 'Sound': '_Sound',
              'ManualSE': '_ManualSE', 'CutEvent': '_CutEvent', 'Light': '_Light',
              'PlannerEvent': '_PlannerEvent', 'Constraint': '_Constraint',
              'Character': '_Character'}


def detach_constraint(data, blocks, actor, want_tick):
    """Turn an attach round: flip a Constraint payload's `Detach` flag on.

    Breaking the name does nothing here. A `Constraint` carries `ActorName`,
    `ParentName`, `SocketName` and a `Detach` bool, and the name is not
    something the game looks up — it says which actor to attach. EV_CORLE_0100
    proved it the expensive way: six flower-lei constraints were renamed to
    `CUT_ORLE_0100_FA0418_00a`.., the patched asset carried every one of them,
    and the leis were still round the characters' necks in game.

    The payload's own flag is the switch the format actually offers. `Detach`
    true means "take this actor off that socket", so the cue that put the lei
    on becomes the cue that takes it off, at the same tick, for the same actor.

    The names are deliberately left alone. A detach has to resolve the same
    actor and the same parent the attach did, so breaking either would sabotage
    exactly the operation being asked for — this is the one disable that needs
    its cue's name intact.

    One byte per payload, and every cue has two copies (its own section and the
    compiled template a shipping build evaluates), so both are rewritten.
    """
    changed = 0
    for _toff, tick, pos, size in blocks:
        if want_tick is not None and tick != want_tick:
            continue
        fields = payload_all_fields(bytes(data), pos, size)
        name = next((v for k, t, v, _o in fields
                     if k == 'ActorName' and t != 'BoolProperty'), None)
        if name != actor:
            continue
        for k, t, v, off in fields:
            if k == 'Detach' and t == 'BoolProperty' and not v:
                data[off] = 1
                changed += 1
    return changed


def disable_cues(staged_seq_dir, ev, cues, remap, max_tick):
    """Neutralise individual cues. Returns (count, notes).

    By name for everything the game looks up and plays, and by the `Enable`
    flag for captions, which are the one kind of cue a broken name makes
    *louder* rather than quieter — see `clear_subtitle`.
    """
    by_seq = {}
    for c in cues:
        if c.get('kind') == 'vfx':
            continue
        by_seq.setdefault(c.get('seq') or 'Voice', []).append(c)
    total, notes = 0, []
    for seq, items in by_seq.items():
        suf = SEQ_SUFFIX.get(seq)
        if not suf:
            continue
        path = os.path.join(staged_seq_dir, ev + suf + '.uasset')
        if not os.path.exists(path):
            continue
        data = bytearray(open(path, 'rb').read())
        blocks = compiled_event_blocks(bytes(data), max_tick)
        changed = 0
        for c in items:
            field, value = c.get('field'), c.get('value')
            if field not in DISABLE_FIELDS or not value:
                continue
            want_tick = remap.point(c['tick']) if c.get('tick') is not None else None
            if field == 'TextLabel':
                if want_tick is None:
                    continue
                got = clear_subtitle(data, blocks, value, want_tick)
                changed += got
                notes.append('%s: subtitle %s never raised (%d payload(s))'
                             % (seq, value, got))
                continue
            if seq == 'Constraint' or c.get('clip') == 'Constraint':
                got = detach_constraint(data, blocks, value, want_tick)
                changed += got
                notes.append('%s: %s detached instead of attached (%d payload(s))'
                             % (seq, value, got) if got else
                             '%s: %s — no attach found to turn round' % (seq, value))
                continue
            for _toff, tick, pos, size in blocks:
                if want_tick is not None and tick != want_tick:
                    continue
                for soff, slen, key, val in payload_name_fields(bytes(data), pos, size,
                                                               (field,)):
                    if val != value or val.startswith('CUT_'):
                        continue
                    nul = 1 if slen > 0 and data[soff+slen-1] == 0 else 0
                    room = slen - nul
                    if room < 1:
                        continue
                    new = ('CUT_' + val[4:]) if room >= 4 else 'X' * room
                    data[soff:soff+room] = new[:room].ljust(room, 'X').encode('latin1')
                    changed += 1
            notes.append('%s: %s=%s' % (seq, field, value))
        if changed:
            open(path, 'wb').write(bytes(data))
            total += changed
    return total, notes


#: The property tag of a music name, as it appears in a compiled payload:
#: the UserDefinedStruct field name, its GUID suffix, and the NUL that ends
#: the FString holding it.
_MUSIC_NAME_TAG = re.compile(rb'MusicName(?:_\d+_[0-9A-Fa-f]{32})?\x00', re.S)


def music_name_spans(data):
    """[(offset, length, value)] for every `MusicName` property in a file.

    A second way to find the same thing `payload_name_fields` finds, and it
    exists because the first way does not always work. `compiled_event_blocks`
    can only see a payload whose **Times array** it managed to locate — it
    searches backwards from each run of payloads for a count that matches — and
    on 53 of this game's 645 music cues that search comes up empty. The cue is
    right there in the bytes; the machinery for addressing it by *time* is what
    is missing.

    That machinery is indispensable for anything that moves a cue or asks which
    side of a cut it falls on. Renaming one needs none of it: the name is a
    string in a property tag with its own length, and the tag can be recognised
    on sight. So this walks the file for the tag itself, checks the shape
    around it — the field name is an FString of exactly that length, the type
    that follows is `NameProperty`, and the tag's size is the value's own
    length plus its four-byte prefix — and reports what it finds.

    Deliberately no tick. This is the fallback used when nothing else can find
    the cue at all, and `repoint_music` only takes it when the name is
    unambiguous, precisely because it cannot tell two cues apart by time.
    """
    out = []
    for m in _MUSIC_NAME_TAG.finditer(data):
        start, end = m.start(), m.end()
        if start < 4:
            continue
        nlen, = struct.unpack_from('<i', data, start - 4)
        if nlen != end - start:
            continue                      # not an FString of exactly this name
        try:
            typ, o, _, _ = _read_fstring_at(data, end)
            if typ != 'NameProperty':
                continue
            sz, _ai = struct.unpack_from('<ii', data, o)
            val, _o2, soff, slen = _read_fstring_at(data, o + 8 + 1)
        except struct.error:
            continue
        if not val or slen != sz - 4:
            continue
        out.append((soff, slen, val))
    return out


def repoint_music(staged_seq_dir, ev, items, remap, max_tick):
    """Point music triggers at a different track. Returns (count, notes, problems).

    A BGM cue is a `Clip_BGM` payload carrying one interesting field —
    `MusicName` — and the bank it names is **not an import**: nothing in the
    cutscene package refers to `/Game/Sound/BGM/...` at all, the game resolves
    the name at runtime. So repointing a trigger is a string edit and nothing
    else. No import table, no dependency graph, no second file to keep in step.

    It is also the reason this is preferable to shipping a replaced bank: the
    edit lives inside this cutscene, so pointing a scene at `bgm_Corle_000`
    cannot disturb any other scene that plays it. `stage_music` — the older
    `replaceMusic` path — rebuilds the bank itself, which changes that music
    everywhere in the game.

    **The new name may be shorter than the old one but never longer.** The
    string sits inside a compiled payload with its length in a prefix and its
    size in the property tag, and `patch_file` asserts the file comes out the
    same size it went in: growing it would move every offset after it and the
    Zen package would no longer describe itself. So the replacement is written
    into the span the old name occupies and padded out with NULs. That is safe
    because these payloads serialise names *as strings* — the archive reads the
    prefix's worth of bytes and takes the string up to the first NUL, which is
    what `payload_events.read_fstring` and `_read_fstring_at` both already do.
    The property tag's size is untouched, so the reader lands in exactly the
    same place afterwards.

    A cue is found by tick **and** by the name it currently carries. Matching on
    the tick alone would let a plan overwrite whatever cue happened to move into
    that slot; a payload whose `MusicName` no longer reads `from` is reported as
    a miss and left exactly as it is.
    """
    by_seq = {}
    for r in items:
        if not r.get('from') or not r.get('to'):
            continue
        by_seq.setdefault(r.get('seq') or 'ManualSE', []).append(r)
    total, notes, problems = 0, [], []
    for seq, wanted in sorted(by_seq.items()):
        suf = SEQ_SUFFIX.get(seq)
        if not suf:
            problems.append('%s: not a sub-sequence this tool patches' % seq)
            continue
        path = os.path.join(staged_seq_dir, ev + suf + '.uasset')
        if not os.path.exists(path):
            problems.append('%s: %s%s.uasset was not staged' % (seq, ev, suf))
            continue
        data = bytearray(open(path, 'rb').read())
        size_before = len(data)
        blocks = compiled_event_blocks(bytes(data), max_tick)
        changed = 0
        for r in wanted:
            old, new = r['from'], r['to']
            try:
                raw = new.encode('latin1')
            except UnicodeEncodeError:
                problems.append('%s -> %s: not a name this format can hold' % (old, new))
                continue
            want_tick = remap.point(r['tick']) if r.get('tick') is not None else None

            def spans(at_tick):
                """(offset, length) of every `MusicName` reading `old`, by tick."""
                found = {}
                for _toff, tick, pos, size in blocks:
                    if at_tick is not None and tick != at_tick:
                        continue
                    for soff, slen, _key, val in payload_name_fields(
                            bytes(data), pos, size, ('MusicName',)):
                        if val == old:
                            found.setdefault(tick, []).append((soff, slen))
                return found

            at = spans(want_tick)
            if not at and want_tick is not None:
                # The cue has been dragged: `patch_file` has already written it
                # at a tick the plan's own `relocateCues` chose, so the authored
                # tick no longer finds it. Falling back to the name is safe only
                # while the name is unambiguous, so it is taken only when the
                # whole file has this music name at exactly one time.
                anywhere = spans(None)
                if len(anywhere) == 1:
                    at = anywhere
                    notes.append('%s: %s found at tick %d, not %d — the cue has '
                                 'moved' % (seq, old, next(iter(at)), want_tick))
                elif len(anywhere) > 1:
                    problems.append(
                        '%s: %s appears at %d different times and none of them is '
                        'the one the plan named (%d) — refusing to guess'
                        % (seq, old, len(anywhere), want_tick))
            if not at:
                # Nothing found by time at all. On 53 of this game's 645 music
                # cues the Times array behind the payload cannot be located, so
                # `compiled_event_blocks` never reports the cue — it is in the
                # file, it just has no address the block walk can express. The
                # name itself is still findable, and renaming needs no timing.
                #
                # Only when the plan is unambiguous about it: without a tick
                # this cannot tell two cues apart, so a scene asking to send
                # two cues that both play `bgm_silence` to two different tracks
                # gets a refusal rather than both of them going the same way.
                same = [x for x in wanted if x is not r and x.get('from') == old]
                spans = [(soff, slen) for soff, slen, val
                         in music_name_spans(bytes(data)) if val == old]
                if spans and not same:
                    at = {None: spans}
                    notes.append(
                        '%s: %s found by its property tag — this scene\'s '
                        'compiled event runs could not be located, so every '
                        'copy of the name was rewritten (%d)' % (seq, old, len(spans)))
                elif spans:
                    problems.append(
                        '%s: %s cannot be addressed by time in this scene and the '
                        'plan repoints it more than once — refusing to guess which '
                        'copy is which' % (seq, old))
            hits = 0
            for _tick, found in sorted(at.items()):
                for soff, slen in found:
                    nul = 1 if slen > 0 and data[soff+slen-1] == 0 else 0
                    room = slen - nul
                    if len(raw) > room:
                        problems.append(
                            '%s -> %s: the new name is %d characters and the cue '
                            'has room for %d' % (old, new, len(raw), room))
                        continue
                    # write the name, then NULs to the end of the old span, so
                    # the length prefix and the tag size stay true
                    data[soff:soff+slen] = raw.ljust(slen, b'\0')
                    hits += 1
            if hits:
                changed += hits
                notes.append('%s: %s -> %s (%d payload%s)'
                             % (seq, old, new, hits, '' if hits == 1 else 's'))
            else:
                problems.append('%s: no music cue reading %s%s'
                                % (seq, old,
                                   '' if want_tick is None else ' at tick %d' % want_tick))
        if changed:
            open(path, 'wb').write(bytes(data))
            assert os.path.getsize(path) == size_before, \
                'size changed — not an in-place patch!'
            total += changed
    return total, notes, problems


def disable_vfx(effect_path, cues, remap, usmap):
    """Collapse a VFX activation window so the effect never plays."""
    vfx = [c for c in cues if c.get('kind') == 'vfx']
    if not vfx or not os.path.exists(effect_path):
        return 0, []
    data = bytearray(open(effect_path, 'rb').read())
    a = T.Reader2(effect_path, usmap)
    wanted = {(remap.point(c['start']), remap.point(c['end']))
              for c in vfx if c.get('start') is not None and c.get('end') is not None}
    changed, notes = 0, []
    for i in a.find('MovieSceneParticleSection'):
        try:
            off = a.dataOffset[i]
        except KeyError:
            continue
        sp = a.read_export(i) or {}
        pk = sp.get('ParticleKeys') or {}
        times = pk.get('Times') or []
        if len(times) < 2:
            continue
        if (times[0], times[-1]) not in wanted:
            continue
        # find the two ints in this export's bytes and collapse them to the start
        blob = bytes(data[off:off + a.exports[i]['serialSize']])
        pat = struct.pack('<%di' % len(times), *times)
        j = blob.find(pat)
        if j < 0:
            continue
        struct.pack_into('<%di' % len(times), data, off + j, *([times[0]] * len(times)))
        changed += 1
        notes.append('vfx window %d collapsed' % times[0])
    if changed:
        open(effect_path, 'wb').write(bytes(data))
    return changed, notes


def invalidate_compiled(path, usmap):
    """Mark the cached compiled sequence data stale so the engine rebuilds it.

    MovieSceneCompiledData holds its own evaluation field with range tables that
    we cannot rewrite (the struct fails to parse — it nests several types absent
    from the .usmap). Its CompiledSignature is a copy of the sequence's Signature;
    when the two differ, UE recompiles from the source tracks, which we *have*
    patched correctly.
    """
    import binascii
    a = T.Reader2(path, usmap)
    sig = None
    for cls in ('EndCinemaSequence', 'LevelSequence', 'MovieSceneSequence'):
        for i in a.find(cls):
            d = a.read_export(i) or {}
            if d.get('Signature'):
                sig = d['Signature']; break
        if sig:
            break
    if not sig:
        return 0
    raw = binascii.unhexlify(sig)
    data = bytearray(open(path, 'rb').read())
    changed = 0
    for i in a.find('MovieSceneCompiledData'):
        if i not in a.dataOffset:
            continue
        off, size = a.dataOffset[i], a.exports[i]['serialSize']
        j = data.find(raw, off, off + size)
        while j >= 0:
            data[j] ^= 0xFF          # break the match -> forces a recompile
            changed += 1
            j = data.find(raw, j + 1, off + size)
    if changed:
        open(path, 'wb').write(bytes(data))
    return changed


def apply_trims(ev_dir, plan, out_root, report, ffmpeg='ffmpeg'):
    """Shorten spoken lines listed in plan['trimLines']."""
    import audio_trim
    trims = plan.get('trimLines') or []
    if not trims:
        return []
    ev = os.path.basename(ev_dir.rstrip('/'))
    area = os.path.basename(os.path.dirname(ev_dir.rstrip('/')))
    content_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(ev_dir.rstrip('/')))))
    lang = plan.get('lang', 'US')
    done = []
    for t in trims:
        name = t.get('voice')
        keep = t.get('keepSeconds')
        if not name or not keep:
            continue
        src = audio_trim.voice_asset_path(content_root, area, ev, name, lang)
        if not os.path.exists(src):
            report.setdefault('warnings', []).append('voice asset missing: %s' % name)
            continue
        dst = os.path.join(out_root, audio_trim.voice_rel_path(area, ev, name, lang))
        try:
            done.append(audio_trim.trim_voice_file(src, dst, keep, ffmpeg))
        except Exception as e:
            report.setdefault('warnings', []).append('trim failed for %s: %r' % (name, e))
    return done


def apply_plan(ev_dir, plan, out_root, usmap, recompile=False, only=None, skip=None):
    """Patch every subsequence of a cutscene into out_root (archive-relative layout)."""
    ev_dir = ev_dir.rstrip('/')
    ev = os.path.basename(ev_dir)
    area = os.path.basename(os.path.dirname(ev_dir))
    total = plan['playbackRange'][1] - plan['playbackRange'][0]
    remap = Remap(plan.get('removeRanges') or [], total)
    # ticks per frame — real evaluation-field bounds land on frames, which is
    # how they are told apart from data that merely looks like a range
    frame = plan.get('ticksPerFrame')
    if not frame:
        tr_ = plan.get('tickResolution') or 24000
        dr_ = plan.get('displayRate') or 30
        frame = int(tr_ // dr_) if dr_ else None
    report = {'cutscene': ev, 'files': [], 'removedTicks': remap.removed_total,
              'newTotal': total - remap.removed_total, 'ticksPerFrame': frame}

    # Fades and streaming commands the editor is carrying across the join,
    # grouped by the sub-sequence they live in. Applied to that sequence's
    # `_Low` twin as well: the low-spec duplicate has to fire the same commands
    # or a machine running it loses the same fade.
    moves_by_seq = {}
    for m in (plan.get('relocateCues') or []):
        moves_by_seq.setdefault('_' + str(m.get('seq') or ''), []).append(m)
    if moves_by_seq:
        report['relocateRequested'] = sum(len(v) for v in moves_by_seq.values())

    # Actor visibility, scene-wide pins first and bounded ones after, so a
    # bounded pin overrides the base state inside its window. Applied in
    # patch_file; see the note there for why it cannot wait until afterwards.
    pins = []
    for key, hide in (('forceVisible', False), ('forceHidden', True)):
        for name in (plan.get(key) or []):
            pins.append({'actor': name, 'hidden': hide, 'range': None})
    for p in (plan.get('pinSpans') or []):
        if p.get('actor') and p.get('range'):
            pins.append({'actor': p['actor'], 'hidden': bool(p.get('hidden')),
                         'range': list(p['range'])[:2]})
    if pins:
        report['pins'] = [
            '%s %s%s' % (x['actor'], 'hidden' if x['hidden'] else 'shown',
                         '' if x['range'] is None
                         else ' over [%d, %d)' % (x['range'][0], x['range'][1]))
            for x in pins
        ]

    rel = os.path.join('End', 'Content', 'Cut', 'Game', area, ev)
    for suf in SUBSEQ:
        src = os.path.join(ev_dir, ev + suf + '.uasset')
        if not os.path.exists(src):
            continue
        label = suf.lstrip('_') or 'Root'
        dst = os.path.join(out_root, rel, ev + suf + '.uasset')
        if (only and label not in only) or (skip and label in skip):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)          # ship the original, untouched
            report['files'].append({'file': ev + suf + '.uasset',
                                    'tickFields': 0, 'patched': 0, 'unpatched': True})
            continue
        base = suf[:-4] if suf.endswith('_Low') else suf
        changed, found = patch_file(src, dst, remap, usmap, total, report,
                                    frame=frame, moves=moves_by_seq.get(base),
                                    pins=pins)
        report['files'].append({'file': ev + suf + '.uasset',
                                'tickFields': found, 'patched': changed})

    # force the engine to rebuild its cached evaluation data from our patched tracks
    if recompile:
        n = 0
        for suf in SUBSEQ:
            f = os.path.join(out_root, rel, ev + suf + '.uasset')
            if os.path.exists(f):
                try:
                    n += invalidate_compiled(f, usmap)
                except Exception as e:
                    report.setdefault('warnings', []).append(
                        'compiled-data invalidation failed for %s (%r)' % (suf or 'root', e))
        report['compiledInvalidated'] = n


    # individually deleted cues
    cues = plan.get('disableCues') or []
    if cues:
        n, notes = disable_cues(os.path.join(out_root, rel), ev, cues, remap, total)
        vn, vnotes = disable_vfx(os.path.join(out_root, rel, ev + '_Effect.uasset'),
                                 cues, remap, usmap)
        report['disabledCues'] = {'payloads': n, 'vfx': vn, 'items': notes + vnotes}

    # music triggers pointed at a different track
    #
    # After `disable_cues`, and skipping any cue that pass switched off. A
    # disabled cue has had the name broken to `CUT_...` precisely so the lookup
    # misses, and repointing it would either undo that or — if it ran first —
    # hide the cue from `disable_cues` and leave it playing. Switching a cue off
    # wins: the editor does not offer both, and a hand-written plan asking for
    # both gets the same answer whichever order it lists them in.
    repoints = plan.get('repointMusic') or []
    if repoints:
        off = {(c.get('seq'), c.get('tick'), c.get('value')) for c in cues}
        live = [r for r in repoints
                if (r.get('seq'), r.get('tick'), r.get('from')) not in off]
        n, notes, problems = repoint_music(os.path.join(out_root, rel), ev,
                                           live, remap, total)
        rep = {'payloads': n, 'requested': len(repoints), 'items': notes}
        if len(live) != len(repoints):
            rep['skippedBecauseDisabled'] = len(repoints) - len(live)
        if problems:
            rep['problems'] = problems
            report.setdefault('warnings', []).extend(problems)
        report['repointedMusic'] = rep

    # shortened dialogue: silence the tail of each trimmed line, then pull its
    # subtitle in to match
    trims = plan.get('trimLines') or []
    if trims:
        report['trims'] = apply_trims(ev_dir, plan, out_root, report)
        tick_rate = plan.get('tickResolution', 24000)
        tf = os.path.join(out_root, rel, ev + '_Text.uasset')
        if os.path.exists(tf):
            n, notes = retime_subtitles(tf, trims, remap, total, tick_rate)
            report['subtitleEdits'] = {'events': n, 'lines': notes}
    return report


def main():
    ev_dir, plan_path, out_root, usmap_path = sys.argv[1:5]
    plan = json.load(open(plan_path))
    usmap = Usmap(usmap_path)
    rep = apply_plan(ev_dir, plan, out_root, usmap)
    print(json.dumps(rep, indent=1))


if __name__ == '__main__':
    main()
