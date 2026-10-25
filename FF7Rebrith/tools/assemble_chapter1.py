"""Combine reviewed Thai batches with immutable game IDs and English labels."""
import json
from collections import Counter, defaultdict
from pathlib import Path
import re
import sys

WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORK / "tools/cutscene-tool/1.0"))
import txtres


def in_scope(key):
    return key.startswith(("$C1910_", "$NIBLT_NPC_10_", "$NIBLM_BOS_00_"))


def main():
    rows = json.loads((WORK / "reference/chapter1-source.json").read_text(encoding="utf-8"))
    translated = {}
    for path in sorted((WORK / "translations/chapter1").glob("batch-*.json")):
        batch = json.loads(path.read_text(encoding="utf-8"))
        if translated.keys() & batch.keys():
            raise ValueError("Duplicate translation index")
        translated.update(batch)
    assert set(translated) == {str(i) for i in range(len(rows))}
    assets = {}
    for row in rows:
        thai = translated[str(row["index"])]
        assert thai and re.findall(r"</?[^>]+>", thai) == re.findall(r"</?[^>]+>", row["Text"]), row["id"]
        assert not re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", thai), row["id"]
        assets.setdefault(row["asset"], {"entries": {}, "actors": {}})["entries"][row["id"]] = thai
    label_examples = {}
    global_votes = json.loads((WORK / "reference/actor-english-evidence.json").read_text(encoding="utf-8"))
    for asset, changes in assets.items():
        jp = txtres.parse(str(WORK / "source" / asset))
        en = txtres.parse(str(WORK / "source" / asset.replace("/JP/", "/US/")))
        label_votes = defaultdict(Counter)
        for key, item in jp.items():
            actor = item.get("MetaData", {}).get("ACTOR")
            english = en.get(key, {}).get("MetaData", {}).get("ACTOR")
            if actor and english:
                label_votes[actor][english] += 1
        for key, item in jp.items():
            if not in_scope(key):
                continue
            actor = item.get("MetaData", {}).get("ACTOR")
            if not actor:
                continue
            english = en.get(key, {}).get("MetaData", {}).get("ACTOR")
            if not english and label_votes[actor]:
                english = label_votes[actor].most_common(1)[0][0]
            if not english and actor in global_votes:
                english = max(global_votes[actor], key=global_votes[actor].get)
            if not english and not item["Text"]:
                # Empty, unvoiced entries have no visible subtitle label.
                continue
            if not english or re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", english):
                raise ValueError(f"Missing verified English actor: {key}")
            changes["actors"][key] = english
            label_examples.setdefault(actor, english)
    resident_rel = "End/Content/Text/JP/Resident_TxtRes.uasset"
    resident = txtres.parse(str(WORK / "source" / resident_rel))
    english_ui = txtres.parse(str(WORK / "source" / resident_rel.replace("/JP/", "/US/")))
    named_characters = {"クラウド", "バレット", "ティファ", "エアリス", "レッドXIII", "ザックス", "セフィロス"}
    ui_names = {key: english_ui[key]["Text"] for key, item in resident.items()
                if item["Text"] in named_characters and key in english_ui}
    assets[resident_rel] = {"entries": ui_names, "actors": {}, "kind": "English character-name labels only"}
    output = dict(scope="Chapter 1 dialogue and conversation choices only",
                  name_policy="English actor labels and character-name UI; Thai names in spoken sentences",
                  assets=assets)
    (WORK / "translations/chapter1-th.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    (WORK / "reference/chapter1-actor-labels.json").write_text(json.dumps(label_examples, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Assembled {len(rows)} translations and {len(ui_names)} English UI names across {len(assets)} text assets")
    print(json.dumps(label_examples, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
