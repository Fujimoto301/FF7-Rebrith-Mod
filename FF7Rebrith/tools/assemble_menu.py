"""Assemble only explicitly selected menu IDs, preserving all game tokens."""
from collections import Counter
import copy
import json
from pathlib import Path
import re
import sys

WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORK / "tools/cutscene-tool/1.0"))
import txtres

TOKEN = re.compile(r"</?[^>]+>")
JAPANESE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
TECHNICAL = {"Lv.", "EXP", "HP", "MP", "ATK", "DEF", "AP", "LOVELESS", "G-BIKE", "1.5x", "2.0x"}
PROTECTED_NAMES = {
    "クラウド": "Cloud", "バレット": "Barret", "ティファ": "Tifa", "エアリス": "Aerith",
    "レッドXIII": "Red XIII", "ユフィ": "Yuffie", "チャドリー": "Chadley",
    "ジョニー": "Johnny", "ルーファウス": "Rufus", "バスターソード": "Buster Sword",
    "リヴァイアサン": "Leviathan", "ラムウ": "Ramuh", "みやぶる": "Assess",
    "スピンスラッシュ": "Spinning Slash", "逆襲の構え": "Retaliation Stance",
    "神羅屋敷": "Shinra Manor", "コスタ・デル・ソル": "Costa del Sol",
    "ゴールドソーサー": "Gold Saucer", "ニブルヘイム": "Nibelheim",
    "モーグリ": "Moogle", "第八神羅丸": "Shinra-8",
    "クイーンズ・ブラッド": "Queen's Blood",
}


def main():
    source = json.loads((WORK / "reference/menu-source.json").read_text(encoding="utf-8"))
    manual = {}
    for path in sorted((WORK / "translations/menu").glob("menu-*.json")):
        batch = json.loads(path.read_text(encoding="utf-8"))
        assert not (manual.keys() & batch.keys()), path
        manual.update(batch)
    translations = {}
    passthrough = []
    known_indexes = {str(u["index"]) for u in source["unique"]}
    assert set(manual) <= known_indexes
    for row in source["unique"]:
        index = str(row["index"])
        original = row["text"]
        if index in manual:
            thai = manual[index]
        elif original in TECHNICAL or not re.search(r"[A-Za-z\u3040-\u30ff\u3400-\u9fff]", TOKEN.sub("", original)):
            thai = original
            passthrough.append(int(index))
        else:
            raise AssertionError((index, "Missing translation", original))
        assert thai and not JAPANESE.search(thai), (index, thai)
        assert TOKEN.findall(thai) == TOKEN.findall(original), (index, "Changed control or variable token sequence")
        for jp, english in PROTECTED_NAMES.items():
            if jp in original:
                assert english.casefold() in thai.casefold(), (index, "Name must remain English", english)
        for mode in ("EASY", "NORMAL", "ADVANCED", "HARD", "ACTION", "CLASSIC", "WAIT"):
            if mode in original:
                assert mode in thai, (index, "Named mode must remain English", mode)
        for key in row["ids"]:
            assert key not in translations
            translations[key] = thai
    raw = txtres.parse(str(WORK / "source" / source["asset"]))
    assert set(translations) == {r["id"] for r in source["rows"]}
    for row in source["rows"]:
        assert raw[row["id"]]["Text"] == row["Text"], row["id"]
    screen_scope_path = WORK / "reference/menu-screen-settings-scope.json"
    if screen_scope_path.exists():
        screen_scope = json.loads(screen_scope_path.read_text(encoding="utf-8"))
        assert all(k in translations for k in screen_scope["japanese_ids"])
        for key, original in screen_scope["protected_english"].items():
            assert raw[key]["Text"] == original
            assert key not in translations or translations[key] == original, key
    forbidden = ("$Item", "$item", "$it_", "$BattleSkill", "$Materia", "$WeaponAbility", "$tutorial_")
    assert not any(k.startswith(forbidden) for k in translations)
    patch = dict(scope=source["scope"], assets={source["asset"]: dict(entries=translations, actors={})})
    (WORK / "translations/menu-th.json").write_text(json.dumps(patch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    combined = copy.deepcopy(json.loads((WORK / "translations/chapter1-th.json").read_text(encoding="utf-8")))
    existing = combined["assets"][source["asset"]]["entries"]
    assert not (set(existing) & set(translations))
    existing.update(translations)
    combined["scope"] = "Chapter 1 dialogue + title/main/pause menu working assets; not an installable release"
    combined["menu_ids"] = sorted(translations)
    (WORK / "translations/working-th.json").write_text(json.dumps(combined, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa = WORK / "qa/menu"
    qa.mkdir(parents=True, exist_ok=True)
    report = dict(selected_records=len(translations),
                  changed_records=sum(raw[k]["Text"] != v for k,v in translations.items()),
                  unique_strings=len(source["unique"]), manually_reviewed_strings=len(manual),
                  preserved_technical_or_token_strings=passthrough,
                  groups=dict(Counter("_".join(k.split("_")[:2]) for k in translations)),
                  tokens_and_variables_preserved=True, item_and_skill_data_unchanged=True,
                  actor_metadata_unchanged=True, installable_package_created=False,
                  installed_in_game=False, runtime_tested=False,
                  excluded="Other detailed options values/help/key remapping, general manuals and tutorials, item/skill names and effects, other story chapters")
    (qa / "translation-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
