"""
audio_ripple.py — make a scene's sound follow the cut.

The SE and BGM stems are not per-shot stingers: each is a single stream as long
as the whole cutscene, started at t=0. Cutting the timeline leaves them playing
straight through, which is why sound carried on past a truncated ending.

CRI HCA stores audio as fixed-size, independently decodable frames, so the edit
can be applied by *rearranging frames*: output frame i is filled with whichever
original frame covers the time that plays at i on the edited timeline. Frames
past the new ending get the quietest frame in the stream, which is silence.
Every frame keeps its own CRC because it is copied whole, the frame count never
changes, and the file stays exactly the same size — so the asset can be patched
in place like everything else.

Frames are 1024 samples, so alignment is within ~32 ms at 32 kHz — under a frame
of video.
"""
import os, struct, subprocess
from fractions import Fraction

SAMPLES_PER_FRAME = 1024


def streams(data):
    """Every HCA stream in a SEAD asset, with the fields needed to edit it."""
    out = []
    i = 0
    while True:
        i = data.find(b'HCA\x00', i)
        if i < 0:
            return out
        hdr = data[i:i + 0x200]
        try:
            hs = struct.unpack_from('>H', hdr, 6)[0]
            j = hdr.find(b'fmt\x00'); k = hdr.find(b'comp')
            if j < 0 or k < 0 or not (8 <= hs <= 0x200):
                i += 4; continue
            ch = hdr[j + 4]
            sr = int.from_bytes(hdr[j + 5:j + 8], 'big')
            blocks = struct.unpack_from('>I', hdr, j + 8)[0]
            bs = struct.unpack_from('>H', hdr, k + 4)[0]
            total = hs + blocks * bs
            if not sr or not bs or total > len(data) - i:
                i += 4; continue
            out.append({'off': i, 'size': total, 'ch': ch, 'sr': sr,
                        'headerSize': hs, 'blocks': blocks, 'blockSize': bs,
                        'dur': blocks * SAMPLES_PER_FRAME / sr})
            i += total
        except Exception:
            i += 4


def _quietest_frame(data, s):
    """Index of the lowest-energy frame, used as the silence to pad with."""
    raw = data[s['off']:s['off'] + s['size']]
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'hca',
           '-i', 'pipe:0', '-ac', '1', '-ar', str(s['sr']), '-f', 's16le', 'pipe:1']
    r = subprocess.run(cmd, input=raw, capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return 0
    pcm = r.stdout
    best, best_e = 0, None
    step = SAMPLES_PER_FRAME * 2
    for f in range(s['blocks']):
        chunk = pcm[f * step:(f + 1) * step]
        if len(chunk) < step:
            break
        e = sum(abs(int.from_bytes(chunk[o:o + 2], 'little', signed=True))
                for o in range(0, step, 32))
        if best_e is None or e < best_e:
            best, best_e = f, e
    return best


def build_inverse(remove_ranges, total):
    """edited tick -> original tick, from the ranges that survive the cut."""
    keep = []
    cur = 0
    for a, b in sorted(tuple(r) for r in remove_ranges):
        a = max(0, min(a, total)); b = max(0, min(b, total))
        if a > cur:
            keep.append((cur, a))
        cur = max(cur, b)
    if cur < total:
        keep.append((cur, total))
    spans = []
    acc = 0
    for a, b in keep:
        spans.append((acc, acc + (b - a), a))
        acc += b - a

    def inverse(t):
        for lo, hi, src in spans:
            if lo <= t < hi:
                return src + (t - lo)
        return None                     # past the end of the edited timeline

    return inverse, acc


def ripple_asset(path, out_path, remove_ranges, total_ticks, tick_res=24000):
    """Apply the cut to every HCA stream in one sound asset. Size never changes."""
    data = bytearray(open(path, 'rb').read())
    ss = streams(bytes(data))
    if not ss:
        return None
    inverse, new_total = build_inverse(remove_ranges, total_ticks)
    report = []
    for s in ss:
        base = s['off'] + s['headerSize']
        bs, n = s['blockSize'], s['blocks']
        frames = [bytes(data[base + i * bs: base + (i + 1) * bs]) for i in range(n)]
        quiet = frames[_quietest_frame(bytes(data), s)]
        # Exact ticks per frame. Floating point here costs whole frames: a
        # value that should land on frame i lands a hair below and truncates to
        # i-1, shuffling untouched audio by 32 ms. At 32 kHz / 24000 ticks this
        # is exactly 768, and Fraction keeps it exact for any other rate.
        tpf = Fraction(SAMPLES_PER_FRAME * tick_res, s['sr'])
        moved = silenced = 0
        for i in range(n):
            t_edit = int(i * tpf)
            src_t = inverse(t_edit)
            if src_t is None:
                data[base + i * bs: base + (i + 1) * bs] = quiet
                silenced += 1
                continue
            j = int(Fraction(src_t) / tpf)
            if j == i or not (0 <= j < n):
                continue
            data[base + i * bs: base + (i + 1) * bs] = frames[j]
            moved += 1
        report.append({'off': s['off'], 'ch': s['ch'], 'sr': s['sr'],
                       'frames': n, 'moved': moved, 'silenced': silenced,
                       'dur': s['dur'], 'newDur': new_total / tick_res})
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, 'wb').write(bytes(data))
    return report
