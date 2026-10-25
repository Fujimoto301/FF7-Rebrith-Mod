"""
scene3d.py — build a compact "who is roughly on screen" dataset for a cutscene:
sampled character world positions + per-cut camera transform/FOV.

Usage: python3 scene3d.py <EV_folder> <Mappings.usmap> <out.json>
"""
import sys, os, re, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transforms as T
from zenasset import Usmap

# actor id prefix -> readable name, learned from the cutscene's IDTable name map
NAME_RE = re.compile(r'^((?:PC|NP|EN|BG|WE)\d{4})_\d{2}_([A-Za-z0-9]+)')


def learn_names(ev_dir, ev, usmap):
    out = {}
    p = os.path.join(ev_dir, 'IDTable', ev + '_IDTable.uasset')
    if not os.path.exists(p):
        return out
    try:
        a = T.Reader2(p, usmap)
    except Exception:
        return out
    for n in a.names:
        m = NAME_RE.match(n)
        if m:
            out.setdefault(m.group(1), m.group(2))
    return out


def actor_label(binding, ev, names):
    """'EV_GRASE_0010_PC0000_00' -> ('Cloud', 'PC0000_00', kind)"""
    short = binding[len(ev)+1:] if binding.startswith(ev + '_') else binding
    m = re.match(r'^((?:PC|NP|EN|BG|WE)\d{4})', short)
    key = m.group(1) if m else None
    nice = names.get(key) if key else None
    kind = key[:2].lower() if key else 'other'
    return (nice or short), short, kind


def rot_matrix(roll, pitch, yaw):
    """UE FRotationMatrix rows = X(forward), Y(right), Z(up) axes."""
    r, p, y = map(math.radians, (roll, pitch, yaw))
    SR, CR = math.sin(r), math.cos(r)
    SP, CP = math.sin(p), math.cos(p)
    SY, CY = math.sin(y), math.cos(y)
    return [[CP*CY, CP*SY, SP],
            [SR*SP*CY - CR*SY, SR*SP*SY + CR*CY, -SR*CP],
            [-(CR*SP*CY + SR*SY), CY*SR - CR*SP*SY, CR*CP]]


def mat_mul(a, b):
    """Row-vector convention: result = a * b."""
    return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def vec_mul(v, m):
    return [sum(v[k]*m[k][j] for k in range(3)) for j in range(3)]


def mat_to_rotator(m):
    """UE FMatrix::Rotator() -> (roll, pitch, yaw) degrees."""
    X, Y, Z = m[0], m[1], m[2]
    pitch = math.degrees(math.atan2(X[2], math.hypot(X[0], X[1])))
    yaw = math.degrees(math.atan2(X[1], X[0]))
    sy = rot_matrix(0.0, pitch, yaw)[1]
    roll = math.degrees(math.atan2(sum(Z[i]*sy[i] for i in range(3)),
                                   sum(Y[i]*sy[i] for i in range(3))))
    return roll, pitch, yaw


def compose(parent, child):
    """(pos, (roll,pitch,yaw)) pairs -> world (pos, (roll,pitch,yaw))."""
    pp, pr = parent
    cp, cr = child
    Mp = rot_matrix(*pr)
    Mc = rot_matrix(*cr)
    world_pos = [pp[i] + vec_mul(cp, Mp)[i] for i in range(3)]
    return world_pos, mat_to_rotator(mat_mul(Mc, Mp))


def extract_cameras(cam_path, usmap):
    """[{range, pos:[chans], rot:[chans], fov:chan}] one per camera cut."""
    a = T.Reader2(cam_path, usmap)
    ms_idx = a.find('MovieScene')
    if not ms_idx:
        return [], None
    ms = a.read_export(ms_idx[0]) or {}
    bindings = ms.get('ObjectBindings') or []
    poss = ms.get('Possessables') or []
    parent_of = {}
    for p in poss:
        g = p.get('Guid'); pg = p.get('ParentGuid')
        if isinstance(g, str) and isinstance(pg, str) and int(pg.replace('-', ''), 16) != 0:
            parent_of[g] = pg

    binfo = {}
    for b in bindings:
        guid = b.get('ObjectGuid')
        rec = {'name': b.get('BindingName'), 'pos': None, 'rot': None, 'fov': None}
        for tr in (b.get('Tracks') or []):
            ti = tr.get('export') if isinstance(tr, dict) else None
            if ti is None:
                continue
            cls = a.classNames[ti]
            tp = a.read_export(ti) or {}
            if cls == 'MovieScene3DTransformTrack':
                for s in (tp.get('Sections') or []):
                    sp = a.read_export(s['export']) or {}
                    rec['pos'] = T._chan_list(sp, 'Translation')
                    rec['rot'] = T._chan_list(sp, 'Rotation')
            elif cls == 'MovieSceneFloatTrack':
                pname = (tp.get('PropertyBinding') or {}).get('PropertyName')
                if pname == 'FieldOfView':
                    for s in (tp.get('Sections') or []):
                        sp = a.read_export(s['export']) or {}
                        ch = sp.get('FloatCurve')
                        if isinstance(ch, T.FloatChannel):
                            rec['fov'] = ch
        binfo[guid] = rec

    # the CineCamera's animated motion + FOV live on the child "Camera Component";
    # attach the child record to its parent camera actor binding
    for guid, rec in binfo.items():
        pg = parent_of.get(guid)
        if pg and pg in binfo:
            par = binfo[pg]
            if rec['fov'] is not None and par['fov'] is None:
                par['fov'] = rec['fov']
            if rec['pos'] is not None and par.get('child') is None:
                par['child'] = rec

    cuts = []
    for i in a.find('MovieSceneCameraCutSection'):
        cs = a.read_export(i) or {}
        sr = cs.get('SectionRange') or {}
        bid = cs.get('CameraBindingID') or {}
        guid = bid.get('Guid')
        rec = binfo.get(guid)
        if rec is None or rec['pos'] is None:
            continue
        cuts.append({'range': [sr.get('lower'), sr.get('upper')], 'rec': rec})
    cuts.sort(key=lambda c: c['range'][0])
    return cuts, a


def build(ev_dir, usmap_path, step_frames=6):
    ev_dir = ev_dir.rstrip('/')
    ev = os.path.basename(ev_dir)
    usmap = Usmap(usmap_path) if isinstance(usmap_path, str) else usmap_path
    names = learn_names(ev_dir, ev, usmap)

    char_path = os.path.join(ev_dir, ev + '_Character.uasset')
    cam_path = os.path.join(ev_dir, ev + '_Camera.uasset')
    if not (os.path.exists(char_path) and os.path.exists(cam_path)):
        return None

    scene, ca = T.extract_scene(char_path, usmap)
    cuts, _ = extract_cameras(cam_path, usmap)

    # timing from the character sequence's MovieScene
    ms = ca.read_export(ca.find('MovieScene')[0]) or {}
    pr = ms.get('PlaybackRange') or {}
    lo, hi = pr.get('lower', 0), pr.get('upper', 0)
    tick = (ms.get('TickResolution') or {}).get('Numerator', 24000)
    fps = (ms.get('DisplayRate') or {}).get('Numerator', 30)
    tpf = tick / fps
    stepT = tpf * step_frames
    ticks = []
    t = lo
    while t < hi:
        ticks.append(int(t)); t += stepT
    ticks.append(hi)

    actors = []
    for binding, rec in scene['actors'].items():
        tr = rec.get('translation') or []
        ro = rec.get('rotation') or []
        if len(tr) < 3 or not any(c.times or c.hasDefault for c in tr):
            continue
        label, short, kind = actor_label(binding, ev, names)
        series = []
        moved = False
        first = None
        for tk in ticks:
            x, y, z = (tr[0].eval(tk), tr[1].eval(tk), tr[2].eval(tk))
            if x is None or y is None or z is None:
                series.append(None); continue
            yaw = ro[2].eval(tk) if len(ro) > 2 else 0.0
            p = [round(x), round(y), round(z), round(yaw or 0.0)]
            if first is None:
                first = p
            elif abs(p[0]-first[0]) + abs(p[1]-first[1]) + abs(p[2]-first[2]) > 1.0:
                moved = True
            series.append(p)
        if all(s is None for s in series):
            continue
        # weapons/props sit at the origin until attached — skip pure-zero tracks
        if first and abs(first[0]) < 1 and abs(first[1]) < 1 and abs(first[2]) < 1 and not moved:
            continue
        # static scenery/weapon props aren't "characters" — skip to cut noise and size
        if kind in ('bg', 'we') and not moved:
            continue
        actors.append({'label': label, 'id': short, 'kind': kind, 'p': series})

    cam = []
    for tk in ticks:
        c = None
        for cu in cuts:
            if cu['range'][0] <= tk < cu['range'][1]:
                c = cu; break
        if c is None and cuts:
            c = cuts[-1] if tk >= cuts[-1]['range'][0] else cuts[0]
        if c is None:
            cam.append(None); continue
        r = c['rec']

        def sample(rec):
            p = [rec['pos'][i].eval(tk) if len(rec['pos']) > i else 0.0 for i in range(3)]
            q = [rec['rot'][i].eval(tk) if rec['rot'] and len(rec['rot']) > i else 0.0
                 for i in range(3)]
            p = [v if v is not None else 0.0 for v in p]
            q = [v if v is not None else 0.0 for v in q]
            return p, (q[0], q[1], q[2])

        if r['pos'] is None:
            cam.append(None); continue
        pos, rot = sample(r)
        child = r.get('child')
        if child and child.get('pos'):
            pos, rot = compose((pos, rot), sample(child))
        fov = r['fov'].eval(tk) if r['fov'] is not None else None
        cam.append([round(pos[0]), round(pos[1]), round(pos[2]),
                    round(rot[0], 1), round(rot[1], 1), round(rot[2], 1),
                    round(fov or 45.0, 1)])

    return {'ev': ev, 'ticks': ticks, 'tick': tick, 'fps': fps,
            'step': step_frames, 'actors': actors, 'cam': cam,
            'cuts': [[c['range'][0], c['range'][1]] for c in cuts]}


if __name__ == '__main__':
    usmap = Usmap(sys.argv[2])
    data = build(sys.argv[1], usmap)
    json.dump(data, open(sys.argv[3], 'w'), default=str)
    print('actors:', [a['label'] for a in data['actors']])
    print('samples:', len(data['ticks']), 'cuts:', len(data['cuts']))
    print('size KB:', os.path.getsize(sys.argv[3])//1024)
