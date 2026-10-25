"""Check IDs and metadata against the original game export."""
import io
import json
from pathlib import Path
import struct
import sys

WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORK.parent / "tools"))
from inspect_reference_mods import fstring, number


def read_records(path):
    data = path.read_bytes()
    header = struct.unpack_from("<15i", data)
    start = header[13] + header[14]
    stream = io.BytesIO(data)
    stream.seek(start + 2)
    language = fstring(stream)
    if number(stream, "I") != 0:
        raise ValueError("Unexpected text property")
    count = number(stream, "I")
    prefix = data[start:stream.tell()]
    records = []
    for _ in range(count):
        key = fstring(stream)
        text = fstring(stream)
        meta_start = stream.tell()
        nmeta = number(stream, "I")
        for _ in range(nmeta):
            number(stream, "I")
            number(stream, "I")
            fstring(stream)
        records.append((key, text, data[meta_start:stream.tell()]))
    if stream.tell() != len(data):
        raise ValueError("Unexpected trailing content")
    return language, prefix, records


def main():
    translations = json.loads((WORK / "translations/prototype-th.json").read_text(encoding="utf-8"))
    rel = translations["asset"]
    old_lang, old_prefix, old = read_records(WORK / "source" / rel)
    new_lang, new_prefix, new = read_records(WORK / "staging/ThaiJP_Prototype_P" / rel)
    assert old_lang == new_lang == "JP" and old_prefix == new_prefix
    assert len(old) == len(new)
    changed = []
    for a, b in zip(old, new):
        assert a[0] == b[0], "Entry ID changed"
        assert a[2] == b[2], f"Metadata changed: {a[0]}"
        if a[1] != b[1]:
            changed.append(a[0])
        elif a[0] in translations["entries"]:
            raise ValueError(f"Expected translation missing: {a[0]}")
    assert set(changed) == set(translations["entries"])
    report = dict(asset=rel, changed_dialogue_entries=len(changed),
                  language_preserved=True, entry_ids_preserved=True,
                  all_record_metadata_preserved=True,
                  actor_label_and_ui_assets_modified=False, runtime_tested=False)
    (WORK / "qa/text-preservation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Verified IDs and metadata unchanged; {len(changed)} dialogue strings changed")


if __name__ == "__main__":
    main()
