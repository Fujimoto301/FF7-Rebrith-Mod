"""
audio_build.py — extract CRI HCA voice audio embedded in FF7 Rebirth
SQEXSEADSound .uasset files and mix one timeline-aligned Opus track per cutscene.

The .uasset embeds a SEAD "sabf" archive whose material payload is a plain
(unencrypted, ciph=0) HCA stream. ffmpeg decodes HCA natively.

Usage: python3 audio_build.py <EV_folder> <timeline.json> <out.ogg> [--lang US]
"""
import sys, os, struct, subprocess, json

SR = 48000  # output sample rate


def find_hca(data):
    """Return the exact HCA byte range embedded in a SEAD sound uasset."""
    for magic in (b'HCA\x00', b'\xc8\xc3\xc1\x80'):
        i = data.find(magic)
        if i < 0:
            continue
        hdr = data[i:i+0x200]
        header_size = struct.unpack_from('>H', hdr, 6)[0]
        if not (8 <= header_size <= 0x200):
            continue
        j = hdr.find(b'fmt\x00')
        k = hdr.find(b'comp')
        if j < 0 or k < 0:
            return data[i:]
        blocks = struct.unpack_from('>I', hdr, j + 8)[0]
        block_size = struct.unpack_from('>H', hdr, k + 4)[0]
        total = header_size + blocks * block_size
        return data[i:i+total] if total <= len(data) - i else data[i:]
    return None


def decode_pcm(hca_bytes, stereo=False, max_sec=None):
    """HCA -> s16le PCM bytes at SR, via ffmpeg stdin/stdout."""
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'hca', '-i', 'pipe:0']
    if max_sec:
        cmd += ['-t', '%.2f' % max_sec]
    cmd += ['-ac', '2' if stereo else '1', '-ar', str(SR), '-f', 's16le', 'pipe:1']
    r = subprocess.run(cmd, input=hca_bytes, capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    return r.stdout


def find_all_hca(data):
    """All HCA streams in a SEAD archive (BGM .mab banks hold many layers)."""
    out = []
    i = 0
    while True:
        i = data.find(b'HCA\x00', i)
        if i < 0:
            break
        try:
            hdr = data[i:i+0x200]
            hs = struct.unpack_from('>H', hdr, 6)[0]
            j = hdr.find(b'fmt\x00'); k = hdr.find(b'comp')
            if j < 0 or k < 0 or not (8 <= hs <= 0x200):
                i += 4; continue
            ch = hdr[j+4]
            sr = int.from_bytes(hdr[j+5:j+8], 'big')
            blocks = struct.unpack_from('>I', hdr, j+8)[0]
            bs = struct.unpack_from('>H', hdr, k+4)[0]
            total = hs + blocks*bs
            if total <= len(data) - i:
                out.append({'off': i, 'size': total, 'ch': ch, 'sr': sr,
                            'dur': blocks*1024/sr if sr else 0})
                i += total
                continue
        except Exception:
            pass
        i += 4
    return out


def voice_path(content_root, area, ev, name, lang='US'):
    return os.path.join(content_root, 'Sound', 'Voice', lang, 'Cut', area, ev, name + '.uasset')


def se_path(content_root, area, ev, name):
    return os.path.join(content_root, 'Sound', 'SE', 'Cut', area, ev, name + '.uasset')


def bgm_path(content_root, name):
    """Search the BGM tree for <name>.uasset."""
    base = os.path.join(content_root, 'Sound', 'BGM')
    for root, _dirs, files in os.walk(base):
        if name + '.uasset' in files:
            return os.path.join(root, name + '.uasset')
    return None


def decode_stream(raw, layer=0, stereo=False, max_sec=None):
    """Decode the Nth HCA stream of a SEAD archive to PCM bytes at SR."""
    streams = find_all_hca(raw)
    if not streams:
        return None
    s = streams[min(layer, len(streams)-1)]
    return decode_pcm(raw[s['off']:s['off']+s['size']], stereo=stereo, max_sec=max_sec)


def build(ev_dir, timeline, out_path, lang='US', bitrate='24k',
          with_se=False, with_bgm=False, se_gain=2.0, bgm_gain=0.35, bgm_layer=0):
    ev_dir = ev_dir.rstrip('/')
    ev = os.path.basename(ev_dir)
    area = os.path.basename(os.path.dirname(ev_dir))
    content_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(ev_dir))))

    root_meta = (timeline.get('sequences', {}).get('Root', {}) or {}).get('meta', {}) or {}
    tick = (root_meta.get('tickResolution') or {}).get('Numerator', 24000)
    pb = root_meta.get('playbackRange') or [0, 0]
    total_samples = int((pb[1] - pb[0]) / tick * SR) + SR  # +1s tail

    events = [e for e in (timeline.get('events', {}).get('Voice') or [])
              if isinstance(e, dict) and e.get('tick') is not None]
    if not events:
        return None

    import numpy as np
    mix = np.zeros(total_samples, dtype=np.int32)
    placed = missing = 0
    lines = []
    for e in events:
        name = (e.get('props') or {}).get('VoiceName')
        if not name:
            continue
        p = voice_path(content_root, area, ev, name, lang)
        if not os.path.exists(p):
            missing += 1
            continue
        hca = find_hca(open(p, 'rb').read())
        if hca is None:
            missing += 1
            continue
        pcm = decode_pcm(hca)
        if pcm is None:
            missing += 1
            continue
        off = max(0, int((e['tick'] - pb[0]) / tick * SR))
        n = min(len(pcm) // 2, total_samples - off)
        if n <= 0:
            continue
        mix[off:off+n] += np.frombuffer(pcm, dtype=np.int16, count=n).astype(np.int32)
        placed += 1
        lines.append({'name': name, 'tick': e['tick'], 'dur': round(len(pcm)/2/SR, 2),
                      'actor': e.get('actor'), 'text': e.get('text')})

    # ---- optional SE + BGM beds (only if those .uassets were exported) ----
    extra = {'se': 0, 'se_missing': 0, 'bgm': 0, 'bgm_missing': 0}
    if with_se or with_bgm:
        for key in ('Sound', 'ManualSE', 'Effect'):
            for e in (timeline.get('events', {}).get(key) or []):
                if not isinstance(e, dict) or e.get('tick') is None:
                    continue
                p_ = e.get('props') or {}
                off = max(0, int((e['tick'] - pb[0]) / tick * SR))
                if with_se and p_.get('SeName'):
                    fp = se_path(content_root, area, ev, p_['SeName'])
                    if not os.path.exists(fp):
                        extra['se_missing'] += 1
                        continue
                    pcm = decode_stream(open(fp, 'rb').read())
                    if not pcm:
                        extra['se_missing'] += 1
                        continue
                    n = min(len(pcm)//2, total_samples - off)
                    if n > 0:
                        mix[off:off+n] += (np.frombuffer(pcm, dtype=np.int16, count=n)
                                           .astype(np.int32) * se_gain).astype(np.int32)
                        extra['se'] += 1
                if with_bgm and p_.get('MusicName'):
                    nm = p_['MusicName']
                    if nm.startswith('bgm_silence'):
                        continue
                    fp = bgm_path(content_root, nm)
                    if not fp:
                        extra['bgm_missing'] += 1
                        continue
                    need = (total_samples - off) / SR + 1
                    pcm = decode_stream(open(fp, 'rb').read(), layer=bgm_layer,
                                        max_sec=need)
                    if not pcm:
                        extra['bgm_missing'] += 1
                        continue
                    n = min(len(pcm)//2, total_samples - off)
                    if n > 0:
                        mix[off:off+n] += (np.frombuffer(pcm, dtype=np.int16, count=n)
                                           .astype(np.int32) * bgm_gain).astype(np.int32)
                        extra['bgm'] += 1

    if not placed:
        return None

    out = np.clip(mix, -32768, 32767).astype(np.int16)

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    r = subprocess.run(
        ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
         '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', 'pipe:0',
         '-c:a', 'libopus', '-b:a', bitrate, '-application', 'voip', out_path],
        input=out.tobytes(), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[:300])
    info = {'file': os.path.basename(out_path), 'lang': lang,
            'placed': placed, 'missing': missing,
            'duration': round(total_samples / SR, 2),
            'bytes': os.path.getsize(out_path), 'lines': lines}
    if with_se or with_bgm:
        info.update(extra)
    info['mix'] = 'vo' + ('+bgm' if with_bgm else '') + ('+se' if with_se else '')
    return info


if __name__ == '__main__':
    ev_dir, tl, out = sys.argv[1], sys.argv[2], sys.argv[3]
    lang = sys.argv[sys.argv.index('--lang')+1] if '--lang' in sys.argv else 'US'
    info = build(ev_dir, json.load(open(tl)), out, lang,
                 with_se='--se' in sys.argv, with_bgm='--bgm' in sys.argv)
    print(json.dumps({k: v for k, v in info.items() if k != 'lines'}, indent=1) if info else 'no audio')
