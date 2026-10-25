"""
extract_timeline.py — extract the Sequencer timeline of an FF7 Rebirth cutscene
(EV_* folder of loose Zen .uasset exports) into a JSON file.

Usage: python3 extract_timeline.py <EV_folder> <Mappings.usmap> <out.json>
"""
import sys, os, json, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vendorpath                 # bundled UE4Parse when none is installed
vendorpath.require()
from cityhash import script_object_hash
import loosezen
from loosezen import load_package, read_names

# ---- monkeypatch 1: native readers for MovieScene structs pyUE4Parse lacks ----
from UE4Parse.Assets.Objects.Structs import UScriptStruct as USSmod

class FMovieSceneFrameRange:
    BOUND = ['Exclusive', 'Inclusive', 'Open']
    def __init__(self, reader):
        lt = reader.readByteToInt()
        lv = reader.readInt32()
        ut = reader.readByteToInt()
        uv = reader.readInt32()
        self.Value = {'LowerBound': {'Type': self.BOUND[lt], 'Value': lv},
                      'UpperBound': {'Type': self.BOUND[ut], 'Value': uv}}
    @classmethod
    def default(cls):
        inst = object.__new__(cls)
        inst.Value = {'LowerBound': {'Type': 'Open', 'Value': 0},
                      'UpperBound': {'Type': 'Open', 'Value': 0}}
        return inst
    def GetValue(self):
        return self.Value

_orig_read = USSmod.UScriptStruct.read
def _patched_read(self, reader, StructName, readType):
    if StructName == 'MovieSceneFrameRange':
        if readType.value == 3:
            self.Struct = FMovieSceneFrameRange.default()
        else:
            self.Struct = FMovieSceneFrameRange(reader)
        return
    return _orig_read(self, reader, StructName, readType)
USSmod.UScriptStruct.read = _patched_read

# ---- monkeypatch 2: tolerate unresolvable (external) object indices ----
from UE4Parse.IoObjects import IoUtils
_orig_resolve = IoUtils.resolveObjectIndex
def _safe_resolve(pkg, globaldata, index):
    try:
        return _orig_resolve(pkg, globaldata, index)
    except Exception:
        return None
IoUtils.resolveObjectIndex = _safe_resolve
import UE4Parse.Assets.PackageReader as PRmod
import UE4Parse.Assets.Objects.FPackageIndex as FPImod
PRmod.resolveObjectIndex = _safe_resolve
FPImod.resolveObjectIndex = _safe_resolve

PKG_TYPE = 2 << 62
MASK62 = (1 << 62) - 1


def build_import_names(uasset_path, pkg):
    """Resolve PackageImport hashes in the import map to object paths via the name map."""
    names = read_names(uasset_path)
    cands = {}
    for n in names:
        if not n.startswith('/'):
            continue
        cands[script_object_hash(n)] = n
    resolved = {}
    for i, poi in enumerate(pkg.ImportMap):
        v = poi.typeAndId
        if (v >> 62) == 2:  # PackageImport
            path = cands.get(v & MASK62)
            if path:
                resolved[i] = path
    return resolved


from UE4Parse.Assets.PropertyTagData.ObjectProperty import ObjectProperty as PTObjectProperty

def plain(v, depth=0):
    """Convert pyUE4Parse property objects to plain JSON-safe values."""
    if depth > 24:
        return '<deep>'
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    if isinstance(v, PTObjectProperty):
        idx = getattr(v.Value, 'Index', None)
        return {'__objref__': idx}
    if isinstance(v, dict):
        return {k: plain(x, depth+1) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [plain(x, depth+1) for x in v]
    if hasattr(v, 'GetValue'):
        try:
            return plain(v.GetValue(), depth+1)
        except Exception as e:
            return '<err:%s>' % e
    return str(v)


def uobj_props(exp):
    o = getattr(exp, 'exportObject', None)
    if o is None:
        return {}
    return {k: plain(p) for k, p in o.Dict.items()}


def obj_ref(prop_plain, pkg, import_names):
    """Interpret a plain ObjectProperty value or return as-is."""
    return prop_plain


def frange(v):
    if not isinstance(v, dict) or 'LowerBound' not in v:
        return None
    return [v['LowerBound']['Value'], v['UpperBound']['Value'],
            v['LowerBound']['Type'], v['UpperBound']['Type']]


def load_and_index(uasset_path, usmap):
    pkg = load_package(uasset_path, usmap)
    import_names = build_import_names(uasset_path, pkg)
    exports = []
    for i, e in enumerate(pkg.ExportMap):
        exports.append({
            'index': i,
            'name': e.name.string if hasattr(e.name, 'string') else str(e.name),
            'type': e.type.string if getattr(e, 'type', None) else None,
            'props': uobj_props(e),
        })
    return pkg, exports, import_names


def resolve_export_ref(ref, exports):
    """ObjectProperty GetValue may yield dict/str; try to find target export index."""
    if isinstance(ref, dict):
        nm = ref.get('ObjectName') or (ref.get('Name') or {})
        if isinstance(nm, dict):
            nm = nm.get('string')
        return nm
    return ref


STOPWORDS = set('''ArrayProperty BoolProperty ByteProperty EnumProperty FloatProperty IntProperty
Int16Property UInt16Property MapProperty NameProperty ObjectProperty StructProperty StrProperty
MovieScene CompiledData Signature Sections Tracks MasterTracks PlaybackRange TickResolution
DisplayRate FrameNumber FrameRate FrameNumberRange FrameNumberRangeBound LowerBound UpperBound
Value Times KeyValues Entries Flags Package Class Section Range Ranges Priority Numerator
EndCinemaSequence EndEventPayload EventData EventReceivers Parameters SpawnObjects
CompletionMode CompilerVersion CompiledSignature AccumulatedMask ActiveEntities ActiveSequences
AllocatedMask'''.split())


def resolve_ref(v, exports, import_names):
    """Resolve {'__objref__': FPackageIndex-int} to export/import name."""
    if not (isinstance(v, dict) and '__objref__' in v):
        return v
    idx = v['__objref__']
    if idx is None or idx == 0:
        return None
    if idx > 0:
        ex = exports[idx-1]
        return {'export': idx-1, 'name': ex['name'], 'type': ex['type']}
    imp = -idx-1
    return {'import': imp, 'path': import_names.get(imp)}


def compiled_data_hints(uasset_path):
    """Readable identifiers from the file (voice cues, trigger IDs...) — coarse."""
    import re
    data = open(uasset_path, 'rb').read()
    out = []
    seen = set()
    for m in re.finditer(rb'[A-Za-z0-9_\-]{5,64}', data):
        s = m.group().decode()
        if s in seen or s in STOPWORDS:
            continue
        if s.startswith(('Default__', 'MovieScene', 'EMovieScene', 'ERangeBound', 'ESection',
                         'EEvaluation', 'EEnd', 'EUpdate', 'LevelSequence', 'bEvaluat',
                         'bFireEvents', 'Track', 'Evaluation', 'Template', 'Ledger')):
            continue
        seen.add(s)
        out.append(s)
    return out[:80]


def extract_sequence(uasset_path, usmap, label):
    pkg, exports, import_names = load_and_index(uasset_path, usmap)
    by_type = {}
    for ex in exports:
        by_type.setdefault(ex['type'], []).append(ex)
    out = {'label': label, 'file': os.path.basename(uasset_path), 'sections': [], 'meta': {}}

    ms = (by_type.get('MovieScene') or [{}])[0]
    p = ms.get('props', {})
    out['meta']['playbackRange'] = frange(p.get('PlaybackRange'))
    out['meta']['tickResolution'] = p.get('TickResolution')
    out['meta']['displayRate'] = p.get('DisplayRate')

    for ex in exports:
        if not ex['type'] or not ex['type'].endswith('Section'):
            continue
        pr = ex['props']
        sec = {
            'exportIndex': ex['index'],
            'type': ex['type'],
            'range': frange(pr.get('SectionRange')) if 'SectionRange' in pr else None,
            'rowIndex': pr.get('RowIndex', 0),
        }
        if 'ShotDisplayName' in pr:
            sec['name'] = pr['ShotDisplayName']
        if 'SubSequence' in pr:
            sec['subSequence'] = resolve_ref(pr['SubSequence'], exports, import_names)
        if 'Parameters' in pr:
            sec['parameters'] = pr['Parameters']
        if 'CameraBindingID' in pr:
            g = pr['CameraBindingID']
            sec['cameraGuid'] = (g.get('Guid') if isinstance(g, dict) else str(g))
        out['sections'].append(sec)

    out['exportSummary'] = [{'index': e['index'], 'name': e['name'], 'type': e['type']}
                            for e in exports]
    out['importNames'] = import_names
    out['hints'] = compiled_data_hints(uasset_path)
    return out


from payload_events import extract_events


def load_subtitles(content_root, area, lang='US'):
    """TxtRes: '$C1910_...' -> {'text':..., 'actor':...}"""
    p = os.path.join(content_root, 'Text', lang, area + '_TxtRes.json')
    if not os.path.exists(p):
        return {}
    data = json.load(open(p, encoding='utf-8-sig'))
    strings = data[0].get('Strings', {}) if isinstance(data, list) else data.get('Strings', {})
    out = {}
    for k, v in strings.items():
        out[k] = {'text': (v.get('Text') or '').replace('\r\n', ' '),
                  'actor': (v.get('MetaData') or {}).get('ACTOR', '')}
    return out


def load_vo_durations(content_root, area, ev, lang='US'):
    """VoiceName -> duration seconds, from SQEXSEADSound FModel JSONs."""
    d = os.path.join(content_root, 'Sound', 'Voice', lang, 'Cut', area, ev)
    out = {}
    if not os.path.isdir(d):
        return out
    for f in os.listdir(d):
        if not f.endswith('.json'):
            continue
        try:
            data = json.load(open(os.path.join(d, f), encoding='utf-8-sig'))
            props = data[0].get('Properties', {}) if isinstance(data, list) else {}
            dur = props.get('Duration')
            if dur:
                out[f[:-5]] = dur
        except Exception:
            pass
    return out


def collect_events(ev_dir, ev, max_tick, subtitles, vo_dur, content_root_hint=None):
    """Timed events for every subsequence that has payloads, with VO/subtitle joins."""
    out = {}
    for part in ['Voice', 'Text', 'CutEvent', 'PlannerEvent', 'ManualSE',
                 'Sound', 'Effect', 'Constraint', 'Light', 'Character']:
        f = os.path.join(ev_dir, '%s_%s.uasset' % (ev, part))
        if not os.path.exists(f):
            continue
        try:
            evs = extract_events(f, max_tick=max_tick)
        except Exception as e:
            out[part] = {'error': str(e)}
            continue
        # the compiled template stores duplicate copies of each event run — dedupe
        seen = set()
        deduped = []
        for e in evs:
            key = (e['tick'], json.dumps(e['props'], sort_keys=True, default=str))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(e)
        evs = deduped
        try:
            import cuetypes
            cuetypes.label_events(evs, os.path.join(content_root_hint or '', 'Cut', 'Clips'))
        except Exception:
            pass
        for e in evs:
            p = e['props']
            lang = p.get('Language', '')
            e['lang'] = 'US' if lang.endswith('::US') else ('JP' if lang.endswith('::JP') else None)
            if 'VoiceName' in p:
                vn = p['VoiceName']
                e['duration'] = vo_dur.get(vn)
                sub = subtitles.get('$' + vn)
                if sub:
                    e['text'] = sub['text']; e['actor'] = sub['actor']
            if 'TextLabel' in p:
                sub = subtitles.get(p['TextLabel'])
                if sub:
                    e['text'] = sub['text']; e['actor'] = sub['actor']
        out[part] = evs
    # pair Text enable/disable into ranges
    #
    # `editor_qt.core.timeline` owns the pairing — it has to re-do it anyway
    # for the timelines extracted before per-language pairing existed, and two
    # implementations of it would drift without anyone noticing.
    if 'Text' in out and isinstance(out['Text'], list):
        from editor_qt.core.timeline import pair_subtitles
        out['SubtitleRanges'] = pair_subtitles(out['Text'])
    return out


_SUBTITLE_CACHE = {}

def extract_cutscene(ev_dir, usmap, compact=False, verbose=True):
    ev_dir = ev_dir.rstrip('/')
    # pyUE4Parse needs the .usmap PATH; zenasset uses a parsed Usmap object.
    # Accept either and normalise, so callers can't silently pass the wrong one.
    usmap_path = usmap if isinstance(usmap, str) else getattr(usmap, 'path', None)
    if not usmap_path:
        raise ValueError('extract_cutscene needs the .usmap file path '
                         '(got %s with no .path)' % type(usmap).__name__)
    usmap = usmap_path
    ev = os.path.basename(ev_dir)
    area = os.path.basename(os.path.dirname(ev_dir))
    content_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(ev_dir))))
    result = {'cutscene': ev, 'area': area, 'sequences': {}}
    parts = ['', '_Camera', '_CutEvent', '_PlannerEvent', '_Voice', '_Text',
             '_Sound', '_ManualSE', '_Effect', '_Constraint']
    for suffix in parts:
        f = os.path.join(ev_dir, ev + suffix + '.uasset')
        if not os.path.exists(f):
            continue
        label = suffix.lstrip('_') or 'Root'
        try:
            seq = extract_sequence(f, usmap, label)
            if compact:
                seq.pop('exportSummary', None)
                seq.pop('hints', None)
                seq.pop('importNames', None)
            result['sequences'][label] = seq
            if verbose: print('[ok]', label)
        except Exception as e:
            if verbose:
                import traceback
                print('[fail]', label, e)
                traceback.print_exc()
    pb = result['sequences'].get('Root', {}).get('meta', {}).get('playbackRange')
    if not pb:
        raise RuntimeError('%s: Root sequence failed to extract — refusing to write a '
                           'timeline the viewer cannot render' % ev)
    max_tick = pb[1] if pb else None
    if area not in _SUBTITLE_CACHE:
        _SUBTITLE_CACHE[area] = load_subtitles(content_root, area)
    subtitles = _SUBTITLE_CACHE[area]
    vo_dur = load_vo_durations(content_root, area, ev)
    if verbose:
        print('subtitles: %d labels, VO durations: %d lines' % (len(subtitles), len(vo_dur)))
    result['events'] = collect_events(ev_dir, ev, max_tick, subtitles, vo_dur, content_root)
    try:
        import scene3d
        from zenasset import Usmap
        global _USMAP
        try:
            _USMAP
        except NameError:
            _USMAP = None
        if _USMAP is None:
            _USMAP = Usmap(usmap) if isinstance(usmap, str) else usmap
        import cuetypes
        fx_path = os.path.join(ev_dir, ev + '_Effect.uasset')
        if os.path.exists(fx_path):
            try:
                fx = cuetypes.extract_vfx(fx_path, _USMAP)
                if fx:
                    result['vfx'] = [{'name': cuetypes.prettify_fx(x['name']),
                                      'raw': x['name'], 'start': x['start'], 'end': x['end']}
                                     for x in fx]
            except Exception:
                pass
        try:
            import lipsync
            ls = lipsync.build(ev_dir, result)
            if ls:
                result['lipsync'] = ls
        except Exception:
            pass
        sc = scene3d.build(ev_dir, _USMAP)
        if sc and sc.get('actors'):
            result['scene'] = sc
            if verbose:
                print('scene: %d actors, %d samples' % (len(sc['actors']), len(sc['ticks'])))
    except Exception as e:
        if verbose:
            print('[scene skipped]', repr(e)[:100])
    return result


def main():
    ev_dir, usmap, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    result = extract_cutscene(ev_dir, usmap)
    with open(out_path, 'w') as fh:
        json.dump(result, fh, indent=1, default=str)
    print('wrote', out_path)


if __name__ == '__main__':
    main()
