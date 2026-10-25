"""
transforms.py — decode FMovieSceneFloatChannel curves and extract per-actor
world transforms + camera transforms/FOV from FF7 Rebirth cutscene sequences.

FMovieSceneFloatChannel native layout (UE4.26/27):
  u8  PreInfinityExtrap
  u8  PostInfinityExtrap
  i32 TimesElemSize(4), i32 TimesCount, TimesCount * i32     (frame numbers)
  i32 ValuesElemSize(28), i32 ValuesCount, ValuesCount * 28  (FMovieSceneFloatValue)
  f32 DefaultValue
  u32 bHasDefaultValue
  i32 TickResolution.Numerator, i32 TickResolution.Denominator
FMovieSceneFloatValue = f32 Value + FMovieSceneTangentData(20B) + u8 Interp + u8 TangentMode + 2 pad
"""
import sys, os, struct, json, bisect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vendorpath                 # bundled UE4Parse when none is installed
vendorpath.require()


class FloatChannel:
    __slots__ = ('times', 'values', 'default', 'hasDefault')

    def __init__(self, times=(), values=(), default=0.0, hasDefault=False):
        self.times = times
        self.values = values
        self.default = default
        self.hasDefault = hasDefault

    @classmethod
    def parse_bytes(cls, buf, o=0):
        o += 2  # extrapolation
        es, n = struct.unpack_from('<ii', buf, o); o += 8
        times = struct.unpack_from('<%di' % n, buf, o) if n else (); o += es * n
        ves, vn = struct.unpack_from('<ii', buf, o); o += 8
        values = tuple(struct.unpack_from('<f', buf, o + ves * i)[0] for i in range(vn))
        o += ves * vn
        default, hasDefault = struct.unpack_from('<fI', buf, o); o += 8
        o += 8  # TickResolution
        return cls(times, values, default, bool(hasDefault)), o

    def eval(self, t):
        """Linear sample (good enough for a rough preview; ignores tangents)."""
        ts = self.times
        if not ts:
            return self.default if self.hasDefault else None
        if t <= ts[0]:
            return self.values[0]
        if t >= ts[-1]:
            return self.values[-1]
        i = bisect.bisect_right(ts, t) - 1
        t0, t1 = ts[i], ts[i+1]
        v0, v1 = self.values[i], self.values[i+1]
        if t1 == t0:
            return v0
        return v0 + (v1 - v0) * (t - t0) / (t1 - t0)

    def is_empty(self):
        return not self.times and not self.hasDefault


# ---- pyUE4Parse integration -------------------------------------------------

def install_channel_patch():
    """Teach pyUE4Parse to read MovieSceneFloatChannel natively."""
    from UE4Parse.Assets.Objects.Structs import UScriptStruct as USSmod

    class _Chan:
        def __init__(self, reader):
            start = reader.base_stream.tell()
            # peek enough bytes: header + arrays; read incrementally
            hdr = reader.readBytes(10)
            es, n = struct.unpack_from('<ii', hdr, 2)
            body = reader.readBytes(es * n + 8)
            ves, vn = struct.unpack_from('<ii', body, es * n)
            vbody = reader.readBytes(ves * vn + 16)
            buf = hdr + body + vbody
            self.chan, _ = FloatChannel.parse_bytes(buf, 0)

        @classmethod
        def default(cls):
            inst = object.__new__(cls)
            inst.chan = FloatChannel()
            return inst

        def GetValue(self):
            return self.chan

    _orig = USSmod.UScriptStruct.read

    def patched(self, reader, StructName, readType):
        if StructName == 'MovieSceneFloatChannel':
            self.Struct = _Chan.default() if readType.value == 3 else _Chan(reader)
            return
        return _orig(self, reader, StructName, readType)

    USSmod.UScriptStruct.read = patched


# ---- zenasset-based extraction (handles arrayDim duplicate channels) --------

import zenasset
from zenasset import Usmap, ZenAsset
from cityhash import script_object_hash

MASK62 = ~(3 << 62) & ((1 << 64) - 1)


def _chan_native(r, a):
    ch, newo = FloatChannel.parse_bytes(r.d, r.o)
    r.o = newo
    return ch


zenasset.NATIVE_STRUCTS['MovieSceneFloatChannel'] = _chan_native
zenasset.NATIVE_STRUCTS['MovieSceneKeyHandleMap'] = lambda r, a: None
zenasset.NATIVE_STRUCTS['MovieSceneTransformMask'] = lambda r, a: r.read('<I')
zenasset.NATIVE_STRUCTS['MovieSceneSequenceID'] = lambda r, a: r.read('<I')
zenasset.NATIVE_STRUCTS['MovieSceneTrackIdentifier'] = lambda r, a: r.read('<I')


class Reader2(ZenAsset):
    """ZenAsset + class-name resolution + bundle-order export data offsets."""

    def __init__(self, path, usmap):
        super().__init__(path, usmap)
        # class hash -> name
        mods = [n for n in self.names if n.startswith('/Script/')]
        simple = [n for n in self.names if not n.startswith('/')]
        table = {}
        for m in mods:
            for n in simple:
                table[script_object_hash('%s.%s' % (m, n))] = n
        self.classNames = [table.get(e['class'] & MASK62) for e in self.exports]
        # serialize order / offsets
        import struct as S
        o = self.ExportBundlesOffset
        _first, count = S.unpack_from('<II', self.d, o); o += 8
        off = self.headerEnd
        self.dataOffset = {}
        for _ in range(count):
            li, ct = S.unpack_from('<II', self.d, o); o += 8
            if ct == 1:
                self.dataOffset[li] = off
                off += self.exports[li]['serialSize']

    def read_export(self, i):
        cn = self.classNames[i]
        if cn is None or i not in self.dataOffset:
            return None
        r = zenasset.Reader(self.d, self.dataOffset[i])
        return self.read_unversioned(r, cn)

    def find(self, classname):
        return [i for i, c in enumerate(self.classNames) if c == classname]


def _chan_list(props, base):
    """Collect Name, Name[i], Name[i+1] -> [FloatChannel x3]."""
    out = []
    for k, v in props.items():
        if k == base or k.startswith(base + '['):
            out.append((k, v))
    def order(kv):
        k = kv[0]
        return 0 if k == base else int(k[len(base)+1:-1])
    out.sort(key=order)
    return [v if isinstance(v, FloatChannel) else FloatChannel() for _, v in out]


def extract_scene(path, usmap):
    """Returns {'actors': {name: {...}}, 'cameraCuts': [...], 'fov': channel}"""
    a = Reader2(path, usmap)
    ms_idx = a.find('MovieScene')
    result = {'actors': {}, 'bindings': {}}
    if not ms_idx:
        return result
    ms = a.read_export(ms_idx[0]) or {}
    bindings = ms.get('ObjectBindings') or []
    for b in bindings:
        name = b.get('BindingName')
        if not name:
            continue
        rec = {'tracks': []}
        for tr in (b.get('Tracks') or []):
            ti = tr.get('export') if isinstance(tr, dict) else None
            if ti is None:
                continue
            tclass = a.classNames[ti]
            rec['tracks'].append(tclass)
            if tclass not in ('MovieScene3DTransformTrack', 'EndCinemaVisibilityTrack'):
                continue
            tp = a.read_export(ti) or {}
            for s in (tp.get('Sections') or []):
                si = s.get('export') if isinstance(s, dict) else None
                if si is None:
                    continue
                sp = a.read_export(si) or {}
                sr = sp.get('SectionRange') or {}
                rng = [sr.get('lower'), sr.get('upper')] if sr else None
                if tclass == 'MovieScene3DTransformTrack':
                    rec['translation'] = _chan_list(sp, 'Translation')
                    rec['rotation'] = _chan_list(sp, 'Rotation')
                    rec['range'] = rng
                else:
                    rec.setdefault('visibility', []).append(
                        {'range': rng, 'default': sp.get('DefaultValue')})
        result['actors'][name] = rec
    return result, a


def export_index_of(track_ref):
    """'EV_GRASE_0010_Character.244' -> 244"""
    if isinstance(track_ref, dict):
        p = track_ref.get('ObjectPath') or ''
    else:
        p = str(track_ref)
    if '.' in p:
        tail = p.rsplit('.', 1)[1]
        if tail.isdigit():
            return int(tail)
    return None


def obj_index(v):
    """pyUE4Parse ObjectProperty -> export index (1-based FPackageIndex)."""
    idx = getattr(getattr(v, 'Value', None), 'Index', None)
    if idx is None and isinstance(v, dict):
        idx = v.get('__objref__')
    return (idx - 1) if isinstance(idx, int) and idx > 0 else None


def gather_transforms(pkg, want_types=('MovieScene3DTransformTrack',)):
    """binding name -> {'translation':[cx,cy,cz], 'rotation':[cx,cy,cz], 'range':[a,b]}"""
    exports = list(pkg.ExportMap)

    def props(i):
        if i is None or i < 0 or i >= len(exports):
            return {}
        o = getattr(exports[i], 'exportObject', None)
        return o.Dict if o is not None else {}

    out = {}
    ms = None
    for e in exports:
        if getattr(e, 'type', None) and e.type.string == 'MovieScene':
            ms = e.exportObject
            break
    if ms is None:
        return out
    bindings = ms.Dict.get('ObjectBindings')
    blist = bindings.GetValue() if hasattr(bindings, 'GetValue') else (bindings or [])
    for b in blist:
        name = b.get('BindingName') if isinstance(b, dict) else None
        if not name:
            continue
        for tr in (b.get('Tracks') or []):
            ti = export_index_of(tr)
            tp = props(ti)
            ttype = exports[ti].type.string if ti is not None and getattr(exports[ti], 'type', None) else ''
            if ttype not in want_types:
                continue
            secs = tp.get('Sections')
            secs = secs.GetValue() if hasattr(secs, 'GetValue') else (secs or [])
            for s in secs:
                si = obj_index(s)
                sp = props(si)
                if not sp:
                    continue
                rec = out.setdefault(name, {})
                for key, dest in (('Translation', 'translation'), ('Rotation', 'rotation')):
                    ch = sp.get(key)
                    chans = []
                    for k in (key, key + '[%d]',):
                        pass
                    # unversioned reader stores repeated struct props as Name / Name[idx]
                    for suffix in ('', '[%d]'):
                        pass
                    vals = [sp.get(key)]
                    for gi in range(1, 3):
                        vals.append(sp.get('%s[%d]' % (key, gi)))
                    for v in vals:
                        c = v.GetValue() if hasattr(v, 'GetValue') else v
                        chans.append(c if isinstance(c, FloatChannel) else FloatChannel())
                    rec[dest] = chans
                sr = sp.get('SectionRange')
                srv = sr.GetValue() if hasattr(sr, 'GetValue') else sr
                if isinstance(srv, dict):
                    rec['range'] = [srv['LowerBound']['Value'], srv['UpperBound']['Value']]
    return out


def sample_actors(transforms, ticks):
    """{name: [[x,y,z,yaw]|None per tick]}"""
    out = {}
    for name, rec in transforms.items():
        tr = rec.get('translation') or []
        ro = rec.get('rotation') or []
        if len(tr) < 3:
            continue
        rng = rec.get('range')
        series = []
        for t in ticks:
            if rng and not (rng[0] <= t <= rng[1]):
                series.append(None); continue
            x = tr[0].eval(t); y = tr[1].eval(t); z = tr[2].eval(t)
            if x is None or y is None or z is None:
                series.append(None); continue
            yaw = ro[2].eval(t) if len(ro) > 2 else None
            series.append([round(x, 1), round(y, 1), round(z, 1),
                           round(yaw, 1) if yaw is not None else 0.0])
        if any(s is not None for s in series):
            out[name] = series
    return out
