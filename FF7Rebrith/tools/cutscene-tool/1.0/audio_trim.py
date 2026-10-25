"""
audio_trim.py — shorten a spoken line inside its SQEXSEADSound .uasset.

CRI HCA stores audio as a header plus N fixed-size frames, each self-contained
with its own CRC. Every frame is independently decodable, so a line can be
shortened by **overwriting the trailing frames with copies of a silent frame
taken from the same clip**. That keeps the file byte-for-byte the same size,
every frame CRC stays valid, and the package remains in-place patchable.

We deliberately do not lower `blockCount`: decoders read to the end of the
declared data, so a shorter count alone would not silence anything.
"""
import os, struct, subprocess


def crc16(data):
    """CRC-16/IBM, as used by the HCA header."""
    c = 0
    for b in data:
        c ^= b << 8
        for _ in range(8):
            c = ((c << 1) ^ 0x8005) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
    return c


def hca_info(data):
    """-> dict describing the embedded HCA stream, or None."""
    i = data.find(b'HCA\x00')
    if i < 0:
        return None
    try:
        hs = struct.unpack_from('>H', data, i + 6)[0]
        j = data.find(b'fmt\x00', i, i + hs)
        k = data.find(b'comp', i, i + hs)
        if j < 0 or k < 0:
            return None
        ch = data[j + 4]
        sr = int.from_bytes(data[j + 5:j + 8], 'big')
        blocks = struct.unpack_from('>I', data, j + 8)[0]
        bs = struct.unpack_from('>H', data, k + 4)[0]
    except Exception:
        return None
    if not (sr and bs and blocks):
        return None
    return {'off': i, 'headerSize': hs, 'fmtOff': j, 'channels': ch,
            'sampleRate': sr, 'blocks': blocks, 'blockSize': bs,
            'dataOff': i + hs, 'duration': blocks * 1024 / sr}


def _decode(chunk, sr, ffmpeg='ffmpeg'):
    r = subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-f', 'hca',
                        '-i', 'pipe:0', '-f', 's16le', '-ac', '1', '-ar', str(sr), 'pipe:1'],
                       input=chunk, capture_output=True)
    return r.stdout if r.returncode == 0 else b''


def quietest_frame(data, info, ffmpeg='ffmpeg'):
    """Index of the quietest frame — our donor for silence.

    Falls back to the last frame (nearly always trailing room tone) when ffmpeg
    isn't available, so trimming still works on a bare Python install.
    """
    try:
        pcm = _decode(bytes(data[info['off']:info['dataOff'] + info['blocks']*info['blockSize']]),
                      info['sampleRate'], ffmpeg)
        if not pcm:
            raise RuntimeError
        import array
        s = array.array('h', pcm[:len(pcm) - len(pcm) % 2])
        best, best_e = info['blocks'] - 1, None
        for n in range(info['blocks']):
            seg = s[n*1024:(n+1)*1024]
            if not len(seg):
                continue
            e = sum(abs(v) for v in seg) / len(seg)
            if best_e is None or e < best_e:
                best, best_e = n, e
        return best
    except Exception:
        return info['blocks'] - 1


def trim_voice_file(src, dst, keep_seconds, ffmpeg='ffmpeg'):
    """Silence everything after keep_seconds. Returns a summary dict."""
    data = bytearray(open(src, 'rb').read())
    info = hca_info(data)
    if not info:
        raise ValueError('no HCA stream in %s' % os.path.basename(src))
    sr, bs, blocks = info['sampleRate'], info['blockSize'], info['blocks']
    keep = max(1, min(blocks, int(round(keep_seconds * sr / 1024))))
    if keep >= blocks:
        os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
        open(dst, 'wb').write(bytes(data))
        return {'file': os.path.basename(src), 'trimmed': False,
                'originalSeconds': round(info['duration'], 3),
                'keptSeconds': round(info['duration'], 3)}

    donor_idx = quietest_frame(data, info, ffmpeg)
    d0 = info['dataOff'] + donor_idx * bs
    donor = bytes(data[d0:d0 + bs])
    for n in range(keep, blocks):
        o = info['dataOff'] + n * bs
        data[o:o + bs] = donor

    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    open(dst, 'wb').write(bytes(data))
    assert os.path.getsize(dst) == os.path.getsize(src), 'voice asset changed size!'
    return {'file': os.path.basename(src), 'trimmed': True,
            'originalSeconds': round(info['duration'], 3),
            'keptSeconds': round(keep * 1024 / sr, 3),
            'silencedFrames': blocks - keep, 'donorFrame': donor_idx}


def voice_asset_path(content_root, area, ev, name, lang='US'):
    return os.path.join(content_root, 'Sound', 'Voice', lang, 'Cut', area, ev, name + '.uasset')


def voice_rel_path(area, ev, name, lang='US'):
    return os.path.join('End', 'Content', 'Sound', 'Voice', lang, 'Cut', area, ev,
                        name + '.uasset')
