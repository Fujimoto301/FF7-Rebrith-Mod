"""CityHash64 — port of the variant UE/CUE4Parse use (CityHash 1.1)."""
M = (1 << 64) - 1
K0 = 0xc3a5c85c97cb3127
K1 = 0xb492b66fbe98f273
K2 = 0x9ae16a3b2f90404f

def _rot(v, s):
    v &= M
    return v if s == 0 else ((v >> s) | (v << (64 - s))) & M

def _shift_mix(v):
    return (v ^ (v >> 47)) & M

def _u64(b, i=0):
    return int.from_bytes(b[i:i+8], 'little')

def _u32(b, i=0):
    return int.from_bytes(b[i:i+4], 'little')

def _bswap64(v):
    return int.from_bytes((v & M).to_bytes(8, 'little'), 'big')

def _hash16_mul(u, v, mul):
    a = ((u ^ v) & M) * mul & M
    a ^= a >> 47
    b = ((v ^ a) & M) * mul & M
    b ^= b >> 47
    return b * mul & M

def _hash16(u, v):
    return _hash16_mul(u, v, 0x9ddfea08eb382d69)

def _len0to16(s):
    ln = len(s)
    if ln >= 8:
        mul = (K2 + ln * 2) & M
        a = (_u64(s) + K2) & M
        b = _u64(s, ln - 8)
        c = (_rot(b, 37) * mul + a) & M
        d = ((_rot(a, 25) + b) & M) * mul & M
        return _hash16_mul(c, d, mul)
    if ln >= 4:
        mul = (K2 + ln * 2) & M
        a = _u32(s)
        return _hash16_mul((ln + (a << 3)) & M, _u32(s, ln - 4), mul)
    if ln > 0:
        a, b, c = s[0], s[ln >> 1], s[ln - 1]
        y = (a + (b << 8)) & 0xFFFFFFFF
        z = (ln + (c << 2)) & 0xFFFFFFFF
        return _shift_mix((y * K2 ^ z * K0) & M) * K2 & M
    return K2

def _len17to32(s):
    ln = len(s)
    mul = (K2 + ln * 2) & M
    a = _u64(s) * K1 & M
    b = _u64(s, 8)
    c = _u64(s, ln - 8) * mul & M
    d = _u64(s, ln - 16) * K2 & M
    return _hash16_mul((_rot((a + b) & M, 43) + _rot(c, 30) + d) & M,
                       (a + _rot((b + K2) & M, 18) + c) & M, mul)

def _len33to64(s):
    ln = len(s)
    mul = (K2 + ln * 2) & M
    a = _u64(s) * K2 & M
    b = _u64(s, 8)
    c = _u64(s, ln - 24)
    d = _u64(s, ln - 32)
    e = _u64(s, 16) * K2 & M
    f = _u64(s, 24) * 9 & M
    g = _u64(s, ln - 8)
    h = _u64(s, ln - 16) * mul & M
    u = (_rot((a + g) & M, 43) + ((_rot(b, 30) + c) & M) * 9) & M
    v = (((a + g) ^ d) + f + 1) & M
    w = (_bswap64((u + v) * mul & M) + h) & M
    x = (_rot((e + f) & M, 42) + c) & M
    y = ((_bswap64((v + w) * mul & M) + g) & M) * mul & M
    z = (e + f + c) & M
    a = (_bswap64(((x + z) * mul + y) & M) + b) & M
    b = _shift_mix(((z + a) * mul + d + h) & M) * mul & M
    return (b + x) & M

def _weak32(s, i, a, b):
    w, x, y, z = _u64(s, i), _u64(s, i+8), _u64(s, i+16), _u64(s, i+24)
    a = (a + w) & M
    b = _rot((b + a + z) & M, 21)
    c = a
    a = (a + x + y) & M
    b = (b + _rot(a, 44)) & M
    return (a + z) & M, (b + c) & M

def cityhash64(s: bytes) -> int:
    ln = len(s)
    if ln <= 32:
        return _len0to16(s) if ln <= 16 else _len17to32(s)
    if ln <= 64:
        return _len33to64(s)
    x = _u64(s, ln - 40)
    y = (_u64(s, ln - 16) + _u64(s, ln - 56)) & M
    z = _hash16((_u64(s, ln - 48) + ln) & M, _u64(s, ln - 24))
    v = _weak32(s, ln - 64, ln, z)
    w = _weak32(s, ln - 32, (y + K1) & M, x)
    x = (x * K1 + _u64(s)) & M
    ln1 = (ln - 1) & ~63
    i = 0
    while True:
        x = _rot((x + y + v[0] + _u64(s, i+8)) & M, 37) * K1 & M
        y = _rot((y + v[1] + _u64(s, i+48)) & M, 42) * K1 & M
        x ^= w[1]
        y = (y + v[0] + _u64(s, i+40)) & M
        z = _rot((z + w[0]) & M, 33) * K1 & M
        v = _weak32(s, i, v[1] * K1 & M, (x + w[0]) & M)
        w = _weak32(s, i+32, (z + w[1]) & M, (y + _u64(s, i+16)) & M)
        z, x = x, z
        i += 64
        ln1 -= 64
        if ln1 == 0:
            break
    return _hash16((_hash16(v[0], w[0]) + _shift_mix(y) * K1 + z) & M,
                   (_hash16(v[1], w[1]) + x) & M)

def script_object_hash(path: str) -> int:
    """FPackageObjectIndex script-import hash: '.'/':'→'/', lowercase, UTF-16LE, CityHash64, clear top 2 bits."""
    b = path.lower().replace('.', '/').replace(':', '/').encode('utf-16-le')
    return cityhash64(b) & ~(3 << 62)
