"""Read supplied, unencrypted Unreal PAK v4 references without changing them.

Outputs are local reference material, not a Rebirth mod. No fonts are exported.
"""
from pathlib import Path
import hashlib
import io
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reference" / "plearngaming"


def read_exact(stream, size):
    data = stream.read(size)
    if len(data) != size:
        raise ValueError("Truncated input")
    return data


def number(stream, fmt):
    return struct.unpack("<" + fmt, read_exact(stream, struct.calcsize("<" + fmt)))[0]


def fstring(stream):
    count = number(stream, "i")
    if count == 0:
        return ""
    if abs(count) > 1_000_000:
        raise ValueError("Invalid FString length")
    width = 2 if count < 0 else 1
    data = read_exact(stream, abs(count) * width)
    if data[-width:] != b"\0" * width:
        raise ValueError("Missing string terminator")
    return data[:-width].decode("utf-16-le" if count < 0 else "utf-8")


def pak_entry(stream):
    offset = number(stream, "q")
    size = number(stream, "q")
    original_size = number(stream, "q")
    compression = number(stream, "I")
    digest = read_exact(stream, 20).hex()
    if compression:
        blocks = number(stream, "I")
        read_exact(stream, blocks * 16)
    encrypted = number(stream, "B")
    block_size = number(stream, "I")
    return dict(offset=offset, size=size, original_size=original_size,
                compression=compression, sha1=digest, encrypted=encrypted,
                block_size=block_size)


def read_index(path):
    with path.open("rb") as stream:
        stream.seek(-45, 2)
        encrypted = number(stream, "B")
        magic = number(stream, "I")
        version = number(stream, "I")
        offset = number(stream, "q")
        size = number(stream, "q")
        digest = read_exact(stream, 20)
        if magic != 0x5A6F12E1 or version != 4 or encrypted:
            raise ValueError("Only unencrypted PAK v4 is supported")
        stream.seek(offset)
        data = read_exact(stream, size)
        if hashlib.sha1(data).digest() != digest:
            raise ValueError("Index checksum mismatch")
    index = io.BytesIO(data)
    mount = fstring(index)
    count = number(index, "I")
    entries = []
    for _ in range(count):
        name = fstring(index)
        entries.append(dict(path=name, **pak_entry(index)))
    if index.tell() != len(data):
        raise ValueError("Unexpected index trailing bytes")
    return mount, entries


def payload(path, entry):
    if entry["compression"] or entry["encrypted"]:
        raise ValueError("Compressed/encrypted payload is unsupported")
    with path.open("rb") as stream:
        stream.seek(entry["offset"])
        header = pak_entry(stream)
        for key in ("size", "original_size", "compression", "sha1", "encrypted"):
            if entry[key] != header[key]:
                raise ValueError("Entry header mismatch")
        data = read_exact(stream, entry["size"])
    if hashlib.sha1(data).hexdigest() != entry["sha1"]:
        raise ValueError("Payload checksum mismatch")
    return data


def read_remake_text(data):
    stream = io.BytesIO(data)
    if read_exact(stream, 2) != b"\0\3":
        raise ValueError("Unexpected text header")
    language = fstring(stream)
    if number(stream, "I") != 0:
        raise ValueError("Unexpected text padding")
    entries = []
    for _ in range(number(stream, "I")):
        label = fstring(stream)
        if not label.startswith("$"):
            raise ValueError("Unexpected text label")
        text = fstring(stream)
        additional = []
        for _ in range(number(stream, "I")):
            kind = number(stream, "I")
            if kind not in (3, 4, 5, 12, 14) or number(stream, "I") != 0:
                raise ValueError("Unexpected additional text field")
            additional.append(dict(kind=kind, text=fstring(stream)))
        entries.append(dict(id=label, text=text, additional=additional))
    if read_exact(stream, 4) != b"\xc1\x83\x2a\x9e" or stream.read(1):
        raise ValueError("Unexpected text footer")
    return dict(language_slot=language, entries=entries)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    report = []
    for folder in ("FF7Remake", "FF7Crisis Core Reunion"):
        path = ROOT / folder / "zThai_PlearnGaming.pak"
        mount, entries = read_index(path)
        game = "remake" if folder == "FF7Remake" else "crisis-core"
        info = dict(source=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                    sha256=hashlib.file_digest(path.open("rb"), "sha256").hexdigest(),
                    mount_point=mount, asset_count=len(entries), assets=entries)
        write_json(OUT / game / "pak-inventory.json", info)
        texts = []
        for entry in entries:
            if entry["path"].endswith("_TxtRes.uexp"):
                parsed = read_remake_text(payload(path, entry))
                parsed["asset"] = entry["path"]
                texts.append(parsed)
        if texts:
            write_json(OUT / game / "text-corpus.json", dict(source=info["source"], assets=texts))
        report.append(dict(game=game, assets=len(entries), text_assets=len(texts),
                           text_entries=sum(len(t["entries"]) for t in texts)))
    write_json(OUT / "summary.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
