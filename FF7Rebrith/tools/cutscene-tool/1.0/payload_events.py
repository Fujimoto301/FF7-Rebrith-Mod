"""
payload_events.py — extract timed event payloads from FF7 Rebirth cutscene
subsequence assets (Voice, Text, CutEvent, ...).

The cooked MovieSceneCompiledData template stores, per EndEventSection:
  [N i32][N ascending u32 tick times]          <- Times
  [N i32]                                      <- KeyValues count
  N x payload blocks:
    [14-byte header][outerSize i32][A1B2C3D4][innerSize i32]
    tagged properties with *string* names, terminated by "None"
"""
import re, struct

MAGIC = b'\xd4\xc3\xb2\xa1'


def read_fstring(d, o):
    ln, = struct.unpack_from('<i', d, o); o += 4
    if ln == 0:
        return '', o
    if ln < 0:
        s = d[o:o-2*ln].decode('utf-16-le', 'replace').rstrip('\0'); o += -2*ln
    else:
        s = d[o:o+ln].decode('utf-8', 'replace').rstrip('\0'); o += ln
    return s, o


def clean_key(name):
    """'VoiceName_35_AE6F6481...' -> 'VoiceName'"""
    m = re.match(r'(.+?)_\d+_[0-9A-F]{32}$', name)
    return m.group(1) if m else name


def parse_tagged(d, o, end):
    """Parse tagged props (string names) until 'None' or end. Returns (props, o)."""
    props = {}
    while o < end - 4:
        name, o = read_fstring(d, o)
        if name == 'None' or name == '':
            break
        typ, o = read_fstring(d, o)
        size, arrayIndex = struct.unpack_from('<ii', d, o); o += 8
        if typ == 'EnumProperty' or typ == 'ByteProperty':
            _enum, o = read_fstring(d, o)
            o += 1  # hasGuid
            if typ == 'ByteProperty' and _enum == 'None':
                val = d[o]; o0 = o; o += size
            else:
                val, _ = read_fstring(d, o); o += size
        elif typ == 'BoolProperty':
            val = bool(d[o]); o += 1
            o += 1  # hasGuid
        elif typ == 'StructProperty':
            _sn, o = read_fstring(d, o)
            o += 16  # struct guid
            o += 1   # hasGuid
            inner, _ = parse_tagged(d, o, o + size)
            val = {'__struct__': _sn, **inner}
            o += size
        elif typ == 'ArrayProperty':
            inner_type, o = read_fstring(d, o)   # element type precedes the guid flag
            o += 1                               # hasGuid
            end_of_array = o + size
            n, = struct.unpack_from('<i', d, o); o2 = o + 4
            vals = []
            try:
                for _ in range(max(0, n)):
                    if inner_type in ('NameProperty', 'StrProperty'):
                        v, o2 = read_fstring(d, o2)
                    elif inner_type == 'IntProperty':
                        v, = struct.unpack_from('<i', d, o2); o2 += 4
                    elif inner_type == 'FloatProperty':
                        v, = struct.unpack_from('<f', d, o2); o2 += 4
                    elif inner_type in ('ByteProperty', 'BoolProperty'):
                        v = d[o2]; o2 += 1
                    else:
                        raise ValueError(inner_type)
                    vals.append(v)
                val = vals
            except Exception:
                val = '<%s[%d]>' % (inner_type, n)
            o = end_of_array
        else:
            o += 1  # hasGuid
            if typ in ('NameProperty', 'StrProperty'):
                val, _ = read_fstring(d, o)
            elif typ == 'IntProperty':
                val, = struct.unpack_from('<i', d, o)
            elif typ == 'FloatProperty':
                val, = struct.unpack_from('<f', d, o)
            elif typ == 'Int64Property':
                val, = struct.unpack_from('<q', d, o)
            else:
                val = '<%s:%d bytes>' % (typ, size)
            o += size
        props[clean_key(name)] = val
    return props, o


def extract_events(path, max_tick=None):
    """Return list of {'tick': int, 'props': {...}} for every payload in the file."""
    d = open(path, 'rb').read()
    magics = [m.start() for m in re.finditer(re.escape(MAGIC), d)]
    events = []
    # group magic blocks into runs: same run when the next magic starts within
    # ~64 bytes of the previous block's payload end (14B header + sizes)
    runs = []
    prev_end = None
    for pos in magics:
        try:
            inner_size, = struct.unpack_from('<i', d, pos + 4)
        except struct.error:
            continue
        if inner_size < 0 or pos + 8 + inner_size > len(d):
            continue
        if runs and prev_end is not None and 0 <= pos - prev_end <= 64:
            runs[-1].append(pos)
        else:
            runs.append([pos])
        prev_end = pos + 8 + inner_size
    for run in runs:
        n = len(run)
        first = run[0]
        # find [N (KeyValues count)] within ~40 bytes before the first block,
        # preceded by [N][N ascending tick values] (the Times array)
        # Two passes; the relaxed one only runs if the strict one found nothing.
        # The range test makes a backwards byte search reliable, but it was
        # all-or-nothing and real arrays carry ticks past the playback end -
        # EV_FOREE_8512's five streaming cues share
        # [0, 912800, 1282400, 5672000, 5828000] against an end of 1282400, and
        # all five came back with tick None because of the last two. A cue with
        # no tick cannot be tested against a cut, so it was invisible to the
        # edit planner and to the patcher alike. See patcher.times_for_run,
        # which carries the same fix so the two cannot disagree.
        times, relaxed = [], None
        for back in range(8, 48):
            cnt_pos = first - back
            if cnt_pos < 0:
                break
            n_kv, = struct.unpack_from('<I', d, cnt_pos)
            if n_kv != n:
                continue
            t_cnt_pos = cnt_pos - 4*n - 4
            if t_cnt_pos < 0:
                continue
            n_t, = struct.unpack_from('<I', d, t_cnt_pos)
            if n_t != n:
                continue
            vals = struct.unpack_from('<%di' % n, d, t_cnt_pos + 4)
            if vals[0] < 0 or not all(b >= a for a, b in zip(vals, vals[1:])):
                continue
            if max_tick is None or all(0 <= v <= max_tick for v in vals):
                times = list(vals)
                break
            if relaxed is None and vals[0] <= max_tick:
                relaxed = list(vals)
        if not times and relaxed is not None:
            times = relaxed
        for i, pos in enumerate(run):
            try:
                inner_size, = struct.unpack_from('<i', d, pos + 4)
                props, _ = parse_tagged(d, pos + 8, pos + 8 + inner_size)
            except (struct.error, UnicodeDecodeError):
                props = {'__parse_error__': True}
            events.append({
                'tick': times[i] if i < len(times) else None,
                'props': props,
            })
    return events


if __name__ == '__main__':
    import sys, json
    evs = extract_events(sys.argv[1])
    print(json.dumps(evs, indent=1, default=str))
