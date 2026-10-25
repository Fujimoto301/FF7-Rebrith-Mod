"""
lipsync.py — read HSFLipSyncDataPack (LSD_*) viseme data and key it to the
cutscene timeline.

Each voice line has one LSD pack named 'LSD_<VoiceName>' holding phoneme
keyframes with times *relative to the clip*. Multiplying by the sequence tick
rate and offsetting by the line's own tick puts them on the cutscene timeline.

Shapes: fv, bmp, aa, ee, oo, ln, sh
"""
import os, json

SHAPES = ['fv', 'bmp', 'aa', 'ee', 'oo', 'ln', 'sh']


def lsd_path(content_root, area, ev, voice_name, lang='US'):
    return os.path.join(content_root, 'LipSync', 'Lsd', lang, 'Cut', area, ev,
                        'LSD_' + voice_name + '.json')


def read_pack(path):
    """-> {'audioLength': float, 'frames': [[start, end, phoneme, {shape: w}], ...]}"""
    try:
        data = json.load(open(path, encoding='utf-8-sig'))
    except Exception:
        return None
    obj = data[0] if isinstance(data, list) and data else data
    entries = (obj.get('Properties') or {}).get('Data') or []
    if not entries:
        return None
    val = entries[0].get('Value') or {}
    info = val.get('Info') or {}
    frames = []
    for k in (val.get('KeyFrames') or []):
        shapes = {s['Key']: round(float(s.get('Value') or 0), 3)
                  for s in (k.get('Shapes') or []) if s.get('Key')}
        frames.append([round(float(k.get('StartTime') or 0), 3),
                       round(float(k.get('EndTime') or 0), 3),
                       k.get('Phoneme') or '', shapes])
    if not frames:
        return None
    return {'audioLength': info.get('AudioLength'),
            'avgPower': info.get('AvgAudioPower'),
            'maxPower': info.get('MaxAudioPower'),
            'frames': frames}


def build(ev_dir, timeline, lang='US'):
    """[{voice, actor, tick, audioLength, frames:[[startTick,endTick,phoneme,shapes]]}]"""
    ev_dir = ev_dir.rstrip('/')
    ev = os.path.basename(ev_dir)
    area = os.path.basename(os.path.dirname(ev_dir))
    content_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(ev_dir))))

    meta = (timeline.get('sequences', {}).get('Root', {}) or {}).get('meta', {}) or {}
    tick = (meta.get('tickResolution') or {}).get('Numerator', 24000)

    out = []
    for e in (timeline.get('events', {}).get('Voice') or []):
        if not isinstance(e, dict) or e.get('tick') is None:
            continue
        name = (e.get('props') or {}).get('VoiceName')
        if not name:
            continue
        p = lsd_path(content_root, area, ev, name, lang)
        if not os.path.exists(p):
            continue
        pack = read_pack(p)
        if not pack:
            continue
        base = e['tick']
        frames = [[int(base + f[0]*tick), int(base + f[1]*tick), f[2], f[3]]
                  for f in pack['frames']]
        out.append({'voice': name, 'actor': e.get('actor'), 'tick': base,
                    'audioLength': pack['audioLength'],
                    'text': e.get('text'), 'frames': frames})
    out.sort(key=lambda x: x['tick'])
    return out


if __name__ == '__main__':
    import sys
    tl = json.load(open(sys.argv[2]))
    data = build(sys.argv[1], tl)
    print('lines with lipsync: %d, keyframes: %d'
          % (len(data), sum(len(d['frames']) for d in data)))
    for d in data[:3]:
        print('  %-32s %s  %d frames  e.g. %s'
              % (d['voice'], d['actor'], len(d['frames']), d['frames'][:2]))
