"""
cuetypes.py — identify which Clip_* type a decoded cutscene payload belongs to,
and extract Niagara VFX windows from the _Effect subsequence.

Clip_* structs are UserDefinedStructs exported by FModel as JSON alongside the
uassets in Content/Cut/Clips. Each has a distinctive set of field names, so the
cleaned property-name set of a payload identifies its clip type.
"""
import os, re, json, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_SIG = None
_CLEAN = re.compile(r'^(.+?)_\d+_[0-9A-F]{32}$')


def clean(name):
    m = _CLEAN.match(name)
    return m.group(1) if m else name


def load_signatures(clips_dir):
    """{frozenset(field names): Clip name}"""
    global _SIG
    if _SIG is not None:
        return _SIG
    sig = {}
    for f in glob.glob(os.path.join(clips_dir, 'Clip_*.json')):
        try:
            data = json.load(open(f, encoding='utf-8-sig'))
        except Exception:
            continue
        obj = data[0] if isinstance(data, list) and data else data
        name = obj.get('Name') or os.path.basename(f)[:-5]
        fields = frozenset(clean(p.get('Name', '')) for p in (obj.get('ChildProperties') or []))
        if fields:
            sig.setdefault(fields, name)
    _SIG = sig
    return sig


def identify(props, clips_dir):
    """Best-matching Clip name for a payload's property dict."""
    sig = load_signatures(clips_dir)
    keys = frozenset(k for k in props if not k.startswith('__'))
    if keys in sig:
        return sig[keys]
    # payload may omit default-valued fields: pick the closest superset
    best, score = None, 0
    for fields, name in sig.items():
        if keys and keys <= fields:
            s = len(keys) / len(fields)
            if s > score:
                best, score = name, s
    return best


def label_events(events, clips_dir):
    """Annotate each event with its clip type (in place)."""
    cache = {}
    for e in events:
        p = e.get('props') or {}
        key = tuple(sorted(k for k in p if not k.startswith('__')))
        if key not in cache:
            cache[key] = identify(p, clips_dir)
        t = cache[key]
        if t:
            e['clip'] = t.replace('Clip_', '')
    return events


# ---------------- Niagara VFX ----------------

def extract_vfx(effect_path, usmap):
    """[{name, start, end}] activation windows for cutscene particle effects."""
    import transforms as T
    a = T.Reader2(effect_path, usmap)
    ms_idx = a.find('MovieScene')
    if not ms_idx:
        return []
    ms = a.read_export(ms_idx[0]) or {}
    poss = ms.get('Possessables') or []
    parent = {p['Guid']: p.get('ParentGuid') for p in poss if p.get('Guid')}
    spawn = {s['Guid']: s.get('Name') for s in (ms.get('Spawnables') or []) if s.get('Guid')}
    byguid = {b['ObjectGuid']: b for b in (ms.get('ObjectBindings') or [])}

    out = []
    for b in (ms.get('ObjectBindings') or []):
        for t in (b.get('Tracks') or []):
            ti = t.get('export') if isinstance(t, dict) else None
            if ti is None or a.classNames[ti] != 'MovieSceneParticleTrack':
                continue
            tp = a.read_export(ti) or {}
            secs = tp.get('ParticleSections') or tp.get('Sections') or []
            for sec in secs:
                si = sec.get('export') if isinstance(sec, dict) else None
                if si is None:
                    continue
                sp = a.read_export(si) or {}
                pk = sp.get('ParticleKeys') or {}
                times = pk.get('Times') or []
                vals = pk.get('Values') or []
                if not times:
                    continue
                pg = parent.get(b.get('ObjectGuid'))
                nm = (spawn.get(pg) or (byguid.get(pg) or {}).get('BindingName')
                      or b.get('BindingName') or 'FX')
                # values: 0 = activate, 1 = deactivate
                start = None
                for tk, v in zip(times, list(vals) + [None]*len(times)):
                    if v == 0 or v is None:
                        if start is None:
                            start = tk
                    elif v == 1 and start is not None:
                        out.append({'name': nm, 'start': start, 'end': tk})
                        start = None
                if start is not None:
                    out.append({'name': nm, 'start': start, 'end': None})
    # identical windows are emitted once per particle section — collapse them
    seen = set()
    uniq = []
    for x in sorted(out, key=lambda y: (y['start'], y['name'])):
        k = (x['name'], x['start'], x['end'])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(x)
    return uniq


def prettify_fx(name):
    """'FX_EV_GOLDE_4850_C0200_Chocobo_Fade_01_26' -> 'C0200 Chocobo Fade 01'"""
    n = re.sub(r'^FX_', '', name)
    n = re.sub(r'^EV_[A-Za-z]+_\d+_?', '', n)
    n = re.sub(r'_\d+$', '', n)
    return n.replace('_', ' ').strip() or name
