"""
levelvolumes.py — read-only inventory of level trigger/volume actors in
FF7 Rebirth cooked .umap files.

Builds on the existing CutsceneTool modules:
  zenasset.Usmap    — .usmap schema (unversioned property layout)
  zenasset.ZenAsset — zen/IoStore package reader
  cityhash          — pure-python CityHash64 for script-import hashes

What it adds on top of those:

  1. Export-bundle offsets. ZenAsset.export_data() locates an export with
     serialOffset - CookedHeaderSize + headerEnd. That is correct only when
     export order happens to equal export-bundle order. In .umap files it
     usually does not: in 2100-COSTA_Gimmick.umap 38 of 39 exports land at a
     different offset under the two schemes. Payload is written in
     export-bundle entry order (command type 1 = Serialize), so we walk the
     bundle table instead. Verified: every actor/component export then decodes
     with exactly a 4-byte tail after its property block.

  2. Class resolution. An export's class is an FPackageObjectIndex, i.e. a
     tagged CityHash64 of the object path, with no name stored in the package.
     We rebuild hash -> "/Script/Module.Class" and invert it.

  3. Volume/trigger detection by usmap ancestry rather than a hardcoded list,
     so subclasses are picked up automatically.

Read-only: nothing here writes to a .umap.

Usage:
    python levelvolumes.py --assets <Field dir> --usmap Mappings.usmap \
        [--uht <UHTHeaderDump dir>] [--out volumes.json] [--quiet]
"""
import argparse
import json
import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zenasset import Usmap, ZenAsset, Reader, NATIVE_STRUCTS
import cityhash

SCRIPT_IMPORT_TAG = 1 << 62

# Ancestry that marks an actor as a volume/trigger. EndStreamingTrigger and
# friends derive straight from Actor, so we also accept any actor owning a
# ShapeComponent-derived component (see LevelScanner._classify).
VOLUME_BASES = ('Volume', 'TriggerBase', 'Brush')
SHAPE_BASE = 'ShapeComponent'

# Unversioned serialisation omits properties equal to the class default, so an
# absent property means "whatever the CDO says" — which the level file does not
# contain. These are the stock UE defaults; anything reported using one is
# flagged with a *_source of "assumed-default" so it is never mistaken for a
# value actually read out of the file.
ASSUMED_DEFAULTS = {
    'RelativeLocation': [0.0, 0.0, 0.0],
    'RelativeRotation': [0.0, 0.0, 0.0],
    'RelativeScale3D': [1.0, 1.0, 1.0],
    'BoxExtent': [32.0, 32.0, 32.0],
    'CapsuleRadius': 22.0,
    'CapsuleHalfHeight': 44.0,
    'SphereRadius': 32.0,
}

# Structs that serialise natively rather than as unversioned properties, and
# that zenasset does not already cover. Without these a decode aborts partway
# through an actor and we lose the properties after the offending one.
EXTRA_NATIVE_STRUCTS = {
    'Box': lambda r, a: {'min': list(r.read('<3f')), 'max': list(r.read('<3f')),
                         'valid': r.read('<B')},
    'Box2D': lambda r, a: {'min': list(r.read('<2f')), 'max': list(r.read('<2f')),
                           'valid': r.read('<B')},
    'IntPoint': lambda r, a: list(r.read('<2i')),
    'IntVector': lambda r, a: list(r.read('<3i')),
    # NOTE: FTransform deliberately absent. It has no custom serialiser here, so
    # it serialises as a nested unversioned property block (Rotation/Translation/
    # Scale3D). Reading it as 10 raw floats desynchronises everything after it —
    # that alone accounted for ~27% of partial decodes before it was removed.
    'BoxSphereBounds': lambda r, a: {'origin': list(r.read('<3f')),
                                     'extent': list(r.read('<3f')),
                                     'radius': r.read('<f')},
    'Vector_NetQuantize': lambda r, a: list(r.read('<3f')),
    'Vector_NetQuantize10': lambda r, a: list(r.read('<3f')),
    'Vector_NetQuantize100': lambda r, a: list(r.read('<3f')),
    'Vector_NetQuantizeNormal': lambda r, a: list(r.read('<3f')),
}


# --------------------------------------------------------------------------
# class-hash resolution
# --------------------------------------------------------------------------

# Fallback when no UHT dump is available: the module list is small enough to
# cross-product against usmap struct names. Exact resolution from a header dump
# is preferred because the cross-product can in principle mint a wrong name.
FALLBACK_MODULES = """ACLPlugin ActorSequence AIModule AnimationBudgetAllocator AnimationCore
AnimationSharing AnimGraphRuntime AssetRegistry AudioExtensions AudioMixer
AudioPlatformConfiguration BinkMediaPlayer BodyDriverPlugin BonamikRt BuildPatchServices
CinematicCamera ClothingSystemRuntimeCommon ClothingSystemRuntimeInterface
ClothingSystemRuntimeNv ControlRig CoreUObject CustomMeshComponent DeveloperSettings EndCore
EndDataBase EndDataObject EndDebug EndGame EndOneSaveData EndTextResource Engine
EngineMessages EngineSettings FacialAnimation Foliage FullBodyIK GameplayTags GameplayTasks
HSFLipSyncRuntime ImageWrapper ImageWriteQueue InputCore InteractiveToolsFramework
JsonUtilities KBDRt KineDriverRt Landscape LevelSequence LightPropagationVolumeRuntime
MaterialShaderQualitySettings MediaAssets MediaUtils MeshDescription MeshModelingTools
ModelingComponents ModelingOperators MoviePlayer MovieScene MovieSceneCapture
MovieSceneTracks NavigationSystem NetCore Niagara NiagaraAnimNotifies NiagaraCore
NiagaraShader OnlineSubsystem OnlineSubsystemEOS OnlineSubsystemSteam OnlineSubsystemUtils
Overlay PacketHandler Paper2D PBIK PhysicsCore PhysXVehicles ProceduralMeshComponent
PropertyAccess PropertyPath Renderer RigVM Serialization SessionMessages SignificanceManager
Slate SlateCore SQEXSEAD StaticMeshDescription TimeManagement UMG VectorVM VFXNiagara""".split()


class ClassResolver:
    """hash -> class name, from a UHT header dump when available."""

    def __init__(self, usmap, uht_dir=None, cache=None):
        self.map = {}
        self.source = None
        if cache and os.path.exists(cache):
            with open(cache) as fh:
                raw = json.load(fh)
            self.map = {int(k): v for k, v in raw['map'].items()}
            self.source = raw['source'] + ' (cached)'
            return
        if uht_dir and os.path.isdir(uht_dir):
            self._from_uht(uht_dir)
        else:
            self._from_cross_product(usmap)
        if cache:
            tmp = cache + '.tmp'
            with open(tmp, 'w') as fh:
                json.dump({'source': self.source,
                           'map': {str(k): v for k, v in self.map.items()}}, fh)
            os.replace(tmp, cache)

    def _add(self, module, name):
        h = cityhash.script_object_hash('/Script/%s.%s' % (module, name))
        self.map[h | SCRIPT_IMPORT_TAG] = name

    def _from_uht(self, uht_dir):
        n = 0
        for module in sorted(os.listdir(uht_dir)):
            mdir = os.path.join(uht_dir, module)
            if not os.path.isdir(mdir):
                continue
            for sub in ('Public', 'Private', ''):
                d = os.path.join(mdir, sub) if sub else mdir
                if not os.path.isdir(d):
                    continue
                for fn in os.listdir(d):
                    if fn.endswith('.h'):
                        self._add(module, fn[:-2])
                        n += 1
        self.source = 'UHT header dump (%d headers)' % n

    def _from_cross_product(self, usmap):
        for s in usmap.structs:
            for m in FALLBACK_MODULES:
                self._add(m, s)
        self.source = 'usmap x module cross-product (no UHT dump given)'

    def get(self, h):
        return self.map.get(h)


# --------------------------------------------------------------------------
# package helpers
# --------------------------------------------------------------------------

def bundle_offsets(asset):
    """Map export index -> real file offset, walking the export bundle table.

    The bundle region is N FExportBundleHeader {FirstEntryIndex, EntryCount}
    followed by all FExportBundleEntry {LocalExportIndex, CommandType}. N is not
    stored anywhere, so derive it: every export contributes exactly two entries
    (Create + Serialize), and whatever is left over in the region is headers.
    Most packages have a single bundle, but not all — the cutscene levels under
    Cut/ have two, and assuming one there walks the entry array off the end.
    """
    base = asset.ExportBundlesOffset
    region = asset.GraphDataOffset - base
    num_entries = 2 * len(asset.exports)
    header_bytes = region - 8 * num_entries
    num_bundles = header_bytes // 8 if header_bytes > 0 and header_bytes % 8 == 0 else 1
    entry_base = base + 8 * num_bundles

    cur = asset.headerEnd
    out = {}
    for b in range(num_bundles):
        first, count = struct.unpack_from('<II', asset.d, base + 8 * b)
        for i in range(first, first + count):
            if i >= num_entries:
                break
            local, command = struct.unpack_from('<II', asset.d, entry_base + 8 * i)
            if command == 1 and local < len(asset.exports):  # Serialize
                out[local] = cur
                cur += asset.exports[local]['serialSize']
    return out


# An EnumProperty is stored using its *underlying* integer type, which the usmap
# records in the property's "inner" entry. zenasset.read_value always reads one
# byte, which is right for the common uint8-backed enum but wrong for the
# int32-backed ones (e.g. EEndNaviMapOpenGroup). Reading 1 byte instead of 4
# shifts every subsequent property.
ENUM_UNDERLYING = {
    'ByteProperty': ('<B', 1), 'Int8Property': ('<b', 1),
    'Int16Property': ('<h', 2), 'UInt16Property': ('<H', 2),
    'IntProperty': ('<i', 4), 'UInt32Property': ('<I', 4),
    'Int64Property': ('<q', 8), 'UInt64Property': ('<Q', 8),
}


class TolerantAsset(ZenAsset):
    """ZenAsset that keeps partial property output when a decode goes wrong.

    An unsupported struct partway through an actor would otherwise discard
    every property already read, including the transform we care about.
    """

    def read_value(self, r, p, isZero, depth):
        if p['type'] == 'EnumProperty' and not isZero:
            fmt, _size = ENUM_UNDERLYING.get(
                (p.get('inner') or {}).get('type', 'ByteProperty'), ('<B', 1))
            v = r.read(fmt)
            names = self.usmap.enums.get(p.get('enum') or '')
            return names[v] if names and 0 <= v < len(names) else v
        return super().read_value(r, p, isZero, depth)

    def read_unversioned(self, r, structName, depth=0):
        schema = self.usmap.schema_chain(structName)
        if not schema:
            raise KeyError('no schema for %s' % structName)
        frags = []
        while True:
            packed = r.read('<H')
            frag = {'skip': packed & 0x7F, 'hasZeros': bool(packed & 0x80),
                    'values': packed >> 9, 'last': bool(packed & 0x100)}
            frags.append(frag)
            if frag['last']:
                break
        num_zero_bits = sum(f['values'] for f in frags if f['hasZeros'])
        zero_mask = []
        if num_zero_bits > 0:
            if num_zero_bits <= 8:
                raw, nb = r.read('<B'), 8
            elif num_zero_bits <= 16:
                raw, nb = r.read('<H'), 16
            else:
                nwords = (num_zero_bits + 31) // 32
                raw = 0
                for w in range(nwords):
                    raw |= r.read('<I') << (32 * w)
            zero_mask = [(raw >> i) & 1 for i in range(num_zero_bits)]

        by_index = {}
        for gi, p in schema:
            by_index.setdefault(gi, p)

        out, idx, zi = {}, 0, 0
        for f in frags:
            idx += f['skip']
            for _ in range(f['values']):
                is_zero = False
                if f['hasZeros']:
                    is_zero = bool(zero_mask[zi])
                    zi += 1
                p = by_index.get(idx)
                if p is None:
                    out['__truncated__'] = 'no schema slot %d on %s' % (idx, structName)
                    return out
                key = p['name'] if p['name'] not in out else '%s[%d]' % (p['name'], idx)
                try:
                    out[key] = self.read_value(r, p, is_zero, depth)
                except Exception as exc:
                    out['__truncated__'] = '%s: %s' % (key, exc)
                    return out
                idx += 1
        return out


# --------------------------------------------------------------------------
# scanning
# --------------------------------------------------------------------------

class LevelScanner:
    def __init__(self, usmap, resolver):
        self.usmap = usmap
        self.resolver = resolver
        self._ancestry = {}
        # Structural self-check: every actor/component export should be
        # "property block + 4-byte tail". Anything else means the offsets or
        # the schema are wrong, so the histogram is the canary.
        self.residuals = {}
        NATIVE_STRUCTS.update(EXTRA_NATIVE_STRUCTS)

    def ancestry(self, name):
        if name not in self._ancestry:
            chain, cur = [], name
            while cur and cur in self.usmap.structs:
                chain.append(cur)
                cur = self.usmap.structs[cur]['super']
            self._ancestry[name] = chain
        return self._ancestry[name]

    def _classify(self, cls, owned_component_classes):
        chain = self.ancestry(cls)
        if 'Volume' in chain:
            return 'volume'
        if 'TriggerBase' in chain:
            return 'trigger'
        if 'Brush' in chain:
            return 'brush'
        for comp in owned_component_classes:
            if SHAPE_BASE in self.ancestry(comp):
                return 'trigger'
        return None

    def scan(self, path, rel):
        asset = TolerantAsset(path, self.usmap)
        offsets = bundle_offsets(asset)
        exports = asset.exports

        classes = [self.resolver.get(e['class']) for e in exports]

        # export index -> children, via the outer FPackageObjectIndex
        children = {}
        for e in exports:
            outer = e['outer']
            if outer >> 62 == 0:  # Export
                children.setdefault(outer & ((1 << 62) - 1), []).append(e['index'])

        decoded = {}

        def decode(i):
            if i in decoded:
                return decoded[i]
            cls = classes[i]
            if not cls or cls not in self.usmap.structs or i not in offsets:
                decoded[i] = None
                return None
            try:
                decoded[i] = self.read_props(asset, offsets, i, cls)
            except Exception as exc:
                decoded[i] = {'__error__': str(exc)}
            return decoded[i]

        out = []
        for e in exports:
            cls = classes[e['index']]
            if not cls or cls not in self.usmap.structs:
                continue
            chain = self.ancestry(cls)
            if 'Actor' not in chain:
                continue
            kids = children.get(e['index'], [])
            kid_classes = [classes[k] for k in kids if classes[k]]
            kind = self._classify(cls, kid_classes)
            if kind is None:
                continue

            props = decode(e['index']) or {}
            record = {
                'level': rel,
                'export': e['index'],
                'actor': e['name'],
                'class': cls,
                'kind': kind,
                'bases': chain[1:],
                'shape': None,
                'components': [],
            }

            for k in kids:
                kcls = classes[k]
                if not kcls:
                    continue
                kchain = self.ancestry(kcls)
                if 'SceneComponent' not in kchain:
                    continue
                kprops = decode(k) or {}
                comp = {'name': exports[k]['name'], 'class': kcls}
                comp.update(self._transform(kprops))
                shape = self._shape(kcls, kchain, kprops)
                if shape:
                    comp['shape'] = shape
                comp['properties'] = self._clean(kprops)
                record['components'].append(comp)

            root = self._pick_root(record['components'], props)
            if root:
                record['location'] = root.get('location')
                record['rotation'] = root.get('rotation')
                record['scale'] = root.get('scale')
                record['transform_source'] = root.get('transform_source')
                record['shape'] = root.get('shape')
                record['root_component'] = root['name']

            record['properties'] = self._clean(props)
            out.append(record)

        return out, len(exports)

    def read_props(self, asset, offsets, index, cls):
        start = offsets[index]
        r = Reader(asset.d, start)
        props = asset.read_unversioned(r, cls)
        if '__truncated__' not in props:
            residual = asset.exports[index]['serialSize'] - (r.o - start)
            key = str(residual) if -1 <= residual <= 32 else 'other'
            self.residuals[key] = self.residuals.get(key, 0) + 1
        return props

    @staticmethod
    def _transform(props):
        info, src = {}, {}
        for key, out_key in (('RelativeLocation', 'location'),
                             ('RelativeRotation', 'rotation'),
                             ('RelativeScale3D', 'scale')):
            if key in props and isinstance(props[key], list):
                info[out_key] = props[key]
                src[out_key] = 'serialized'
            else:
                info[out_key] = list(ASSUMED_DEFAULTS[key])
                src[out_key] = 'assumed-default'
        info['transform_source'] = src
        return info

    @staticmethod
    def _shape(cls, chain, props):
        if 'BoxComponent' in chain:
            serialized = isinstance(props.get('BoxExtent'), list)
            return {'type': 'box',
                    'extent': props['BoxExtent'] if serialized
                              else list(ASSUMED_DEFAULTS['BoxExtent']),
                    'source': 'serialized' if serialized else 'assumed-default'}
        if 'CapsuleComponent' in chain:
            return {'type': 'capsule',
                    'radius': props.get('CapsuleRadius', ASSUMED_DEFAULTS['CapsuleRadius']),
                    'half_height': props.get('CapsuleHalfHeight',
                                             ASSUMED_DEFAULTS['CapsuleHalfHeight']),
                    'source': 'serialized' if 'CapsuleRadius' in props
                              else 'assumed-default'}
        if 'SphereComponent' in chain:
            return {'type': 'sphere',
                    'radius': props.get('SphereRadius', ASSUMED_DEFAULTS['SphereRadius']),
                    'source': 'serialized' if 'SphereRadius' in props
                              else 'assumed-default'}
        if 'BrushComponent' in chain:
            # Geometry lives in a UModel, which has no reflected properties and
            # is not decoded here. Transform is still exact.
            return {'type': 'brush', 'geometry': 'in UModel, not decoded'}
        return None

    @staticmethod
    def _pick_root(components, actor_props):
        if not components:
            return None
        root_ref = actor_props.get('RootComponent')
        if isinstance(root_ref, dict) and 'name' in root_ref:
            for c in components:
                if c['name'] == root_ref['name']:
                    return c
        for c in components:
            if c.get('shape'):
                return c
        return components[0]

    @staticmethod
    def _clean(props):
        return {k: v for k, v in props.items()
                if k not in ('RelativeLocation', 'RelativeRotation', 'RelativeScale3D')}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

# Small, high-signal properties worth keeping in a compact index: the things
# you would actually search on when hunting for a volume to edit.
KEEP_PROPS = (
    'LocationId', 'NaviMapId', 'VolumeLabel', 'EnemyTerritoryID', 'TerritoryType',
    'LocationVolumeType', 'StreamingVolumeType', 'StreamingTarget', 'UnloadMargin',
    'bDisabled', 'bForce', 'bSafeArea', 'bDisplayLocationName', 'bDisableChocoboRide',
    'bDisableBuggyRide', 'bDisableDodge', 'bChangeCamera', 'CameraSettingID',
    'ActivateStoryFlag', 'ShowStoryFlag', 'DeactivateStoryFlag', 'Tags', 'BrushType',
)


def compact(v):
    props = {k: val for k, val in v.get('properties', {}).items()
             if k in KEEP_PROPS or k == '__truncated__'}
    out = {k: v[k] for k in ('level', 'actor', 'class', 'kind', 'export') if k in v}
    for k in ('location', 'rotation', 'scale', 'shape', 'root_component',
              'transform_source'):
        if k in v:
            out[k] = v[k]
    if props:
        out['properties'] = props
    return out


def merge(shards, out_path):
    """Combine shard JSONs written by --start/--count runs into one index."""
    volumes, failures, summary = [], [], {}
    ints = ('levels_scanned', 'levels_failed', 'exports_seen', 'volumes_found',
            'partial_decodes')
    dicts = ('by_kind', 'by_class', 'tail_bytes_after_property_block')
    for path in sorted(shards):
        with open(path) as fh:
            doc = json.load(fh)
        volumes.extend(doc['volumes'])
        failures.extend(doc['failures'])
        s = doc['summary']
        for k in ints:
            summary[k] = summary.get(k, 0) + s.get(k, 0)
        for k in dicts:
            acc = summary.setdefault(k, {})
            for kk, vv in s.get(k, {}).items():
                acc[kk] = acc.get(kk, 0) + vv
        summary['class_table_source'] = s.get('class_table_source')
    summary['by_class'] = dict(sorted(summary['by_class'].items(),
                                      key=lambda kv: -kv[1]))
    summary['shards_merged'] = len(shards)
    with open(out_path, 'w') as fh:
        json.dump({'summary': summary, 'failures': failures,
                   'volumes': volumes}, fh, indent=1)
    print('merged %d shards -> %s' % (len(shards), out_path))
    print(json.dumps(summary, indent=1)[:2000])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--assets', required=True, help='root directory of extracted levels')
    ap.add_argument('--usmap', required=True, help='path to Mappings.usmap')
    ap.add_argument('--uht', help='UHTHeaderDump directory (exact class names)')
    ap.add_argument('--out', default='volumes.json')
    ap.add_argument('--cache', default='.classhash-cache.json')
    ap.add_argument('--limit', type=int, help='stop after N levels (smoke test)')
    ap.add_argument('--start', type=int, default=0,
                    help='index of first level to scan (for resumable chunks)')
    ap.add_argument('--count', type=int,
                    help='scan only this many levels starting at --start')
    ap.add_argument('--merge', nargs='+',
                    help='merge previously written shard JSONs into --out and exit')
    ap.add_argument('--compact', action='store_true',
                    help='emit only identity, transform and shape per volume '
                         '(the full index with every property is ~900MB)')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args(argv)

    if args.merge:
        return merge(args.merge, args.out)

    def log(msg):
        if not args.quiet:
            print(msg, flush=True)

    t0 = time.time()
    usmap = Usmap(args.usmap)
    log('usmap: %d structs, %d enums' % (len(usmap.structs), len(usmap.enums)))
    resolver = ClassResolver(usmap, args.uht, args.cache)
    log('class table: %d entries from %s' % (len(resolver.map), resolver.source))

    scanner = LevelScanner(usmap, resolver)

    umaps = []
    for root, _dirs, files in os.walk(args.assets):
        for fn in files:
            if fn.endswith('.umap'):
                umaps.append(os.path.join(root, fn))
    umaps.sort()
    total_found = len(umaps)
    if args.limit:
        umaps = umaps[:args.limit]
    umaps = umaps[args.start:]
    if args.count:
        umaps = umaps[:args.count]
    log('found %d .umap files; scanning %d starting at index %d'
        % (total_found, len(umaps), args.start))

    volumes, failures, exports_seen = [], [], 0
    for n, path in enumerate(umaps, 1):
        rel = os.path.relpath(path, args.assets).replace('\\', '/')
        try:
            found, nexp = scanner.scan(path, rel[:-5])
            volumes.extend(found)
            exports_seen += nexp
        except Exception as exc:
            failures.append({'level': rel, 'error': '%s: %s' % (type(exc).__name__, exc)})
        if not args.quiet and (n % 200 == 0 or n == len(umaps)):
            log('  %d/%d levels, %d volumes, %d failures'
                % (n, len(umaps), len(volumes), len(failures)))

    if args.compact:
        volumes = [compact(v) for v in volumes]

    by_class, by_kind, truncated = {}, {}, 0
    for v in volumes:
        by_class[v['class']] = by_class.get(v['class'], 0) + 1
        by_kind[v['kind']] = by_kind.get(v['kind'], 0) + 1
        if '__truncated__' in v.get('properties', {}):
            truncated += 1

    doc = {
        'summary': {
            'levels_scanned': len(umaps),
            'levels_failed': len(failures),
            'exports_seen': exports_seen,
            'volumes_found': len(volumes),
            'partial_decodes': truncated,
            'by_kind': by_kind,
            'by_class': dict(sorted(by_class.items(), key=lambda kv: -kv[1])),
            'class_table_source': resolver.source,
            'tail_bytes_after_property_block': dict(
                sorted(scanner.residuals.items(),
                       key=lambda kv: -kv[1])),
            'seconds': round(time.time() - t0, 1),
        },
        'failures': failures,
        'volumes': volumes,
    }
    with open(args.out, 'w') as fh:
        json.dump(doc, fh, indent=1)

    log('\n%d volume/trigger actors across %d levels in %.0fs'
        % (len(volumes), len(umaps) - len(failures), time.time() - t0))
    log('partial decodes: %d   level failures: %d' % (truncated, len(failures)))
    log('tail bytes after property block: %s'
        % doc['summary']['tail_bytes_after_property_block'])
    log('top classes:')
    for cls, n in list(doc['summary']['by_class'].items())[:15]:
        log('  %5d  %s' % (n, cls))
    log('wrote %s' % args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
