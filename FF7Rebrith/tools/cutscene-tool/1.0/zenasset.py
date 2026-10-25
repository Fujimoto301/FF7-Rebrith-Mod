"""
zenasset.py — minimal reader for FF7 Rebirth (UE4.26/27 Zen/IoStore) loose cooked
.uasset exports (FModel raw export layout) using a .usmap for unversioned properties.

Prototype scope: enough property coverage to extract MovieScene/Sequencer timeline
data (frame ranges, object refs, names, strings, enums, basic structs/arrays).
"""
import struct, json, sys, os

# ---------------- usmap ----------------

EPT = ["ByteProperty","BoolProperty","IntProperty","FloatProperty","ObjectProperty",
       "NameProperty","DelegateProperty","DoubleProperty","ArrayProperty","StructProperty",
       "StrProperty","TextProperty","InterfaceProperty","MulticastDelegateProperty",
       "WeakObjectProperty","LazyObjectProperty","AssetObjectProperty","SoftObjectProperty",
       "UInt64Property","UInt32Property","UInt16Property","Int64Property","Int16Property",
       "Int8Property","MapProperty","SetProperty","EnumProperty","FieldPathProperty"]

class Usmap:
    def __init__(self, path):
        self.path = path if isinstance(path, str) else None
        d = open(path,'rb').read()
        magic, ver = struct.unpack('<HB', d[:3])
        assert magic == 0x30C4, "bad usmap magic"
        o = 3
        if ver >= 1:
            hasVer = d[o]; o += 1
            if hasVer:
                o += 8
                n, = struct.unpack('<i', d[o:o+4]); o += 4 + n*20 + 4
        method = d[o]; o += 1
        compSize, decompSize = struct.unpack('<II', d[o:o+8]); o += 8
        assert method == 0, "compressed usmap not supported in prototype"
        d = d[o:o+decompSize]; o = 0
        def u32():
            nonlocal o
            v, = struct.unpack_from('<I', d, o); o += 4; return v
        def u16():
            nonlocal o
            v, = struct.unpack_from('<H', d, o); o += 2; return v
        def u8():
            nonlocal o
            v = d[o]; o += 1; return v
        # names
        n = u32()
        self.names = []
        for _ in range(n):
            ln = u8()
            self.names.append(d[o:o+ln].decode('utf-8','replace')); o += ln
        # enums
        n = u32()
        self.enums = {}
        for _ in range(n):
            nm = self.names[u32()]
            cnt = u8()
            self.enums[nm] = [self.names[u32()] for _ in range(cnt)]
        # structs
        n = u32()
        self.structs = {}
        def read_ptype():
            t = u8()
            typ = EPT[t] if t < len(EPT) else 'Unknown'
            info = {'type': typ}
            if typ == 'EnumProperty':
                info['inner'] = read_ptype()
                info['enum'] = self.names[u32()]
            elif typ == 'StructProperty':
                info['struct'] = self.names[u32()]
            elif typ in ('ArrayProperty','SetProperty','OptionalProperty'):
                info['inner'] = read_ptype()
            elif typ == 'MapProperty':
                info['key'] = read_ptype()
                info['value'] = read_ptype()
            return info
        for _ in range(n):
            nm = self.names[u32()]
            sup = u32()
            superName = self.names[sup] if sup != 0xFFFFFFFF else None
            propCount = u16(); serializableCount = u16()
            props = []
            for _p in range(serializableCount):
                idx = u16(); arrayDim = u8(); pnm = self.names[u32()]
                pt = read_ptype()
                props.append({'index': idx, 'arrayDim': arrayDim, 'name': pnm, **pt})
            self.structs[nm] = {'super': superName, 'propCount': propCount, 'props': props}

    def schema_chain(self, name):
        """Flattened serializable property list as (globalIndex, prop).

        UE indexes unversioned properties DERIVED-first: indices [0, propCount)
        belong to the most-derived struct, then the super's block follows.
        """
        out = []
        base = 0
        cur = name
        while cur is not None and cur in self.structs:
            st = self.structs[cur]
            for p in st['props']:
                for dim in range(p['arrayDim']):
                    out.append((base + p['index'] + dim, p))
            base += st['propCount']
            cur = st['super']
        return out

# ---------------- zen package ----------------

class Reader:
    def __init__(self, data, off=0):
        self.d = data; self.o = off
    def read(self, fmt):
        v = struct.unpack_from(fmt, self.d, self.o)
        self.o += struct.calcsize(fmt)
        return v if len(v) > 1 else v[0]
    def bytes(self, n):
        b = self.d[self.o:self.o+n]; self.o += n; return b

NATIVE_STRUCTS = {
    'Guid':            lambda r, a: r.bytes(16).hex(),
    'FrameNumber':     lambda r, a: r.read('<i'),
    'MovieSceneFrameRange': lambda r, a: {
        'lowerType': ['Exclusive','Inclusive','Open'][r.read('<B')],
        'lower': r.read('<i'),
        'upperType': ['Exclusive','Inclusive','Open'][r.read('<B')],
        'upper': r.read('<i')},
    'FrameTime':       lambda r, a: {'frame': r.read('<i'), 'sub': r.read('<f')},
    'Vector':          lambda r, a: list(r.read('<3f')),
    'Vector2D':        lambda r, a: list(r.read('<2f')),
    'Vector4':         lambda r, a: list(r.read('<4f')),
    'Rotator':         lambda r, a: list(r.read('<3f')),
    'Quat':            lambda r, a: list(r.read('<4f')),
    'LinearColor':     lambda r, a: list(r.read('<4f')),
    'Color':           lambda r, a: list(r.read('<4B')),
    'Timespan':        lambda r, a: r.read('<q'),
    'DateTime':        lambda r, a: r.read('<q'),
    'SoftObjectPath':  lambda r, a: {'asset': a.read_fname(r), 'sub': a.read_fstring(r)},
    'SoftClassPath':   lambda r, a: {'asset': a.read_fname(r), 'sub': a.read_fstring(r)},
}

class ZenAsset:
    def __init__(self, path, usmap):
        self.path = path
        self.usmap = usmap
        d = self.d = open(path,'rb').read()
        (self.NameIdx, self.SourceName, self.PackageFlags, self.CookedHeaderSize,
         nmO, nmS, nhO, nhS, self.ImportMapOffset, self.ExportMapOffset,
         self.ExportBundlesOffset, self.GraphDataOffset, self.GraphDataSize,
         _pad) = struct.unpack('<QQIIiiiiiiiiii', d[:64])
        self.headerEnd = self.GraphDataOffset + self.GraphDataSize
        # name map
        self.names = []
        o = nmO
        while o < nmO + nmS:
            b0, b1 = d[o], d[o+1]; o += 2
            utf16 = b0 >> 7; ln = ((b0 & 0x7f) << 8) | b1
            if utf16:
                self.names.append(d[o:o+2*ln].decode('utf-16-le')); o += 2*ln
            else:
                self.names.append(d[o:o+ln].decode('latin1')); o += ln
        # imports
        n = (self.ExportMapOffset - self.ImportMapOffset)//8
        self.imports = list(struct.unpack_from('<%dQ' % n, d, self.ImportMapOffset))
        # exports
        n = (self.ExportBundlesOffset - self.ExportMapOffset)//72
        self.exports = []
        for i in range(n):
            (cso, css, nameIdx, nameNum, outer, cls, sup, tmpl, glob, flags, ff) = \
                struct.unpack_from('<QQIIQQQQQIB3x', d, self.ExportMapOffset + 72*i)
            self.exports.append({
                'index': i,
                'name': self.names[nameIdx & 0x7FFFFFFF],
                'nameNumber': nameNum,
                'serialOffset': cso, 'serialSize': css,
                'outer': outer, 'class': cls, 'super': sup,
                'template': tmpl, 'globalImport': glob, 'flags': flags})
        # export bundle headers give class resolution only via global store; instead map
        # class hash -> usmap struct by matching per-export via known name (heuristic below)

    def export_data(self, e):
        off = e['serialOffset'] - self.CookedHeaderSize + self.headerEnd
        return Reader(self.d, off), off, e['serialSize']

    # ---- primitive readers ----
    def read_fname(self, r):
        idx, num = r.read('<II')
        nm = self.names[idx & 0x7FFFFFFF] if (idx & 0x7FFFFFFF) < len(self.names) else '<bad:%d>' % idx
        return nm if num == 0 else '%s_%d' % (nm, num-1)

    def read_fstring(self, r):
        ln = r.read('<i')
        if ln == 0: return ''
        if ln < 0:
            return r.bytes(-2*ln).decode('utf-16-le').rstrip('\0')
        return r.bytes(ln).decode('utf-8','replace').rstrip('\0')

    def read_packageindex(self, r):
        v = r.read('<i')
        if v == 0: return None
        if v > 0:
            ex = self.exports[v-1]
            return {'export': v-1, 'name': ex['name']}
        return {'import': -v-1, 'hash': '%016x' % self.imports[-v-1] if -v-1 < len(self.imports) else None}

    # ---- unversioned properties ----
    def read_unversioned(self, r, structName, depth=0):
        schema = self.usmap.schema_chain(structName)
        if not schema:
            raise KeyError('no schema for %s' % structName)
        # fragments
        frags = []
        while True:
            packed = r.read('<H')
            frag = {'skip': packed & 0x7F, 'hasZeros': bool(packed & 0x80),
                    'values': packed >> 9, 'last': bool(packed & 0x100)}
            frags.append(frag)
            if frag['last']: break
        numZeroBits = sum(f['values'] for f in frags if f['hasZeros'])
        zeroMask = []
        if numZeroBits > 0:
            if numZeroBits <= 8: raw = r.read('<B'); nb = 8
            elif numZeroBits <= 16: raw = r.read('<H'); nb = 16
            else:
                nwords = (numZeroBits + 31)//32
                raw = 0
                for w in range(nwords):
                    raw |= r.read('<I') << (32*w)
                nb = nwords*32
            zeroMask = [(raw >> i) & 1 for i in range(numZeroBits)]
        # walk schema
        bySchemaIdx = {}
        for gi, p in schema:
            bySchemaIdx.setdefault(gi, p)
        out = {}
        idx = 0
        zi = 0
        for f in frags:
            idx += f['skip']
            for _ in range(f['values']):
                isZero = False
                if f['hasZeros']:
                    isZero = bool(zeroMask[zi]); zi += 1
                p = bySchemaIdx.get(idx)
                if p is None:
                    raise KeyError('schema index %d missing on %s' % (idx, structName))
                key = p['name']
                if key in out:
                    key = '%s[%d]' % (p['name'], idx)
                out[key] = self.read_value(r, p, isZero, depth)
                idx += 1
        return out

    def zero_value(self, p):
        t = p['type']
        if t == 'BoolProperty': return False
        if t in ('IntProperty','Int8Property','Int16Property','Int64Property','UInt16Property',
                 'UInt32Property','UInt64Property','ByteProperty'): return 0
        if t in ('FloatProperty','DoubleProperty'): return 0.0
        if t == 'NameProperty': return 'None'
        if t == 'ObjectProperty': return None
        if t == 'StrProperty': return ''
        if t == 'ArrayProperty': return []
        if t == 'EnumProperty':
            en = self.usmap.enums.get(p.get('enum') or '', None)
            return en[0] if en else 0
        if t == 'StructProperty':
            return {'__zero__': p.get('struct')}
        return None

    def read_value(self, r, p, isZero, depth):
        t = p['type']
        if t == 'BoolProperty':
            # unversioned: a non-zero bool still serializes one byte
            return False if isZero else bool(r.read('<B'))
        if isZero:
            return self.zero_value(p)
        if t in ('ByteProperty','Int8Property'): return r.read('<b' if t=='Int8Property' else '<B')
        if t == 'Int16Property': return r.read('<h')
        if t == 'UInt16Property': return r.read('<H')
        if t == 'IntProperty': return r.read('<i')
        if t == 'UInt32Property': return r.read('<I')
        if t == 'Int64Property': return r.read('<q')
        if t == 'UInt64Property': return r.read('<Q')
        if t == 'FloatProperty': return r.read('<f')
        if t == 'DoubleProperty': return r.read('<d')
        if t == 'NameProperty': return self.read_fname(r)
        if t == 'StrProperty': return self.read_fstring(r)
        if t == 'ObjectProperty' or t == 'WeakObjectProperty' or t == 'InterfaceProperty':
            return self.read_packageindex(r)
        if t == 'SoftObjectProperty':
            return {'asset': self.read_fname(r), 'sub': self.read_fstring(r)}
        if t == 'EnumProperty':
            v = r.read('<B')
            en = self.usmap.enums.get(p.get('enum') or '', None)
            return en[v] if en and v < len(en) else v
        if t == 'ArrayProperty':
            n = r.read('<i')
            inner = p['inner']
            return [self.read_value(r, inner, False, depth+1) for _ in range(n)]
        if t == 'SetProperty':
            r.read('<i')  # elements to remove (0 in cooked)
            n = r.read('<i')
            return [self.read_value(r, p['inner'], False, depth+1) for _ in range(n)]
        if t == 'MapProperty':
            r.read('<i')
            n = r.read('<i')
            out = []
            for _ in range(n):
                k = self.read_value(r, p['key'], False, depth+1)
                v = self.read_value(r, p['value'], False, depth+1)
                out.append([k, v])
            return out
        if t == 'StructProperty':
            sn = p.get('struct')
            if sn in NATIVE_STRUCTS:
                return NATIVE_STRUCTS[sn](r, self)
            return self.read_unversioned(r, sn, depth+1)
        if t == 'TextProperty':
            # cooked FText: flags u32, historyType i8; support None(-1)+hasString and Base(0)
            flags = r.read('<I'); ht = r.read('<b')
            if ht == -1:
                has = r.read('<i')
                return {'text': self.read_fstring(r) if has else None}
            if ht == 0:
                ns = self.read_fstring(r); key = self.read_fstring(r); src = self.read_fstring(r)
                return {'ns': ns, 'key': key, 'text': src}
            raise ValueError('unsupported FText history %d' % ht)
        raise ValueError('unsupported property type %s' % t)
