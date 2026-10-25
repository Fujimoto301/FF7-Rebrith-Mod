"""Build Chapter 1 Thai dialogue with English names and original Latin glyphs."""
import io
import json
import re
from pathlib import Path
import struct
import string
import sys

import build_prototype as b
from inspect_reference_mods import fstring, number
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import txtres

WORK = b.WORK
STAGE = WORK / "staging/ThaiJP_Chapter1_P"
QA = WORK / "qa/chapter1"


def patch_asset(path, changes, cmap):
    data = path.read_bytes()
    end = b.header_end(data)
    stream = io.BytesIO(data)
    stream.seek(end + 2)
    assert fstring(stream) == "JP" and number(stream,"I") == 0
    count = number(stream,"I")
    body = bytearray(data[end:stream.tell()])
    names = txtres.read_names(data)
    changed_text, changed_actors = set(), set()
    for _ in range(count):
        key_start = stream.tell()
        key = fstring(stream)
        text_start = stream.tell()
        text = fstring(stream)
        meta_start = stream.tell()
        nmeta = number(stream,"I")
        metadata = bytearray(data[meta_start:stream.tell()])
        for _ in range(nmeta):
            start = stream.tell()
            idx, num = number(stream,"I"), number(stream,"I")
            value_start = stream.tell()
            value = fstring(stream)
            if names[idx] == "ACTOR" and key in changes["actors"]:
                metadata.extend(data[start:value_start]+b.write_string(changes["actors"][key]))
                changed_actors.add(key)
            else:
                metadata.extend(data[start:stream.tell()])
        if key in changes["entries"]:
            translated = changes["entries"][key]
            mixed_thai = any("\u0e01" <= c <= "\u0e5b" for c in translated)
            # Keep control tags byte-for-byte, including letters and digits in
            # button names and variable indexes. Only visible text gets aliases.
            def encode_visible(segment):
                return "".join(part if not mixed_thai and part.isascii() and part.isalnum() else cmap.get(part,part)
                               for part in b.split_clusters(segment))
            encoded = "".join(segment if re.fullmatch(r"</?[^>]+>", segment) else encode_visible(segment)
                              for segment in re.split(r"(</?[^>]+>)", translated))
            body.extend(data[key_start:text_start]+b.write_string(encoded)+metadata)
            changed_text.add(key)
        elif key in changes["actors"]:
            body.extend(data[key_start:meta_start]+metadata)
        else:
            body.extend(data[key_start:stream.tell()])
    assert stream.tell()==len(data)
    assert changed_text == set(changes["entries"])
    assert changed_actors == set(changes["actors"])
    return b.with_body(data,body)


def main(menu_working=False, chapter2_working=False, inventory_working=False, ui_completion_working=False, text_only=False, chapter3_working=False, chapter4_working=False, chapter5_working=False, chapter6_working=False, review_working=False):
    global STAGE, QA
    if chapter6_working:
        menu_working=True
        chapter2_working=True
        STAGE=WORK/"staging/ThaiJP_ThroughChapter6_Working"
        QA=WORK/"qa/chapter6"
    elif chapter5_working:
        menu_working=True
        chapter2_working=True
        STAGE=WORK/"staging/ThaiJP_ThroughChapter5_Working"
        QA=WORK/"qa/chapter5"
    elif chapter4_working:
        menu_working=True
        chapter2_working=True
        STAGE=WORK/"staging/ThaiJP_ThroughChapter4_Working"
        QA=WORK/"qa/chapter4"
    elif chapter3_working:
        menu_working = True
        chapter2_working = True
        STAGE = WORK / "staging/ThaiJP_ThroughChapter3_Working"
        QA = WORK / "qa/chapter3"
    elif ui_completion_working:
        menu_working = True
        chapter2_working = True
        STAGE = WORK / "staging/ThaiJP_UICompletion_Working"
        QA = WORK / "qa/ui-completion"
    elif inventory_working:
        menu_working = True
        chapter2_working = True
        STAGE = WORK / "staging/ThaiJP_Inventory_Working"
        QA = WORK / "qa/inventory"
    elif chapter2_working:
        menu_working = True
        STAGE = WORK / "staging/ThaiJP_ThroughChapter2_Working"
        QA = WORK / "qa/chapter2"
    elif menu_working:
        STAGE = WORK / "staging/ThaiJP_Working"
        QA = WORK / "qa/menu"
    review=json.loads((WORK/(review_working if isinstance(review_working,str) else 'reference/ch12-recheck-build.json')).read_text('utf-8')) if review_working else None
    if review:STAGE=WORK/review['stage'];QA=WORK/review['qa']
    QA.mkdir(parents=True,exist_ok=True)
    changes_path = WORK / ("translations/working-through-chapter6-th.json" if chapter6_working else "translations/working-through-chapter5-th.json" if chapter5_working else "translations/working-through-chapter4-th.json" if chapter4_working else "translations/working-through-chapter3-th.json" if chapter3_working else "translations/working-ui-completion-th.json" if ui_completion_working else "translations/working-inventory-th.json" if inventory_working else "translations/working-through-chapter2-th.json" if chapter2_working else "translations/working-th.json" if menu_working else "translations/chapter1-th.json")
    if review:changes_path=WORK/review['source']
    changes = json.loads(changes_path.read_text(encoding="utf-8"))
    clusters = sorted({c for a in changes["assets"].values() for text in a["entries"].values()
                       for c in b.split_clusters(text) if "\u0e01"<=c[0]<= "\u0e5b"})
    # Numeral aliases are used only by translated text, never ACTOR metadata.
    clusters = sorted(set(clusters) | set("0123456789"))
    if menu_working:
        clusters = sorted(set(clusters) | set(string.ascii_letters))
    cmap = {cluster:chr(0xe800+i) for i,cluster in enumerate(clusters)}
    cluster_path = WORK / ("reference/through-chapter6-cluster-map.json" if chapter6_working else "reference/through-chapter5-cluster-map.json" if chapter5_working else "reference/through-chapter4-cluster-map.json" if chapter4_working else "reference/through-chapter3-cluster-map.json" if chapter3_working else "reference/ui-completion-cluster-map.json" if ui_completion_working else "reference/inventory-cluster-map.json" if inventory_working else "reference/through-chapter2-cluster-map.json" if chapter2_working else "reference/working-cluster-map.json" if menu_working else "reference/chapter1-cluster-map.json")
    if review:cluster_path=WORK/review['cluster_map']
    if chapter3_working or chapter4_working or chapter5_working or chapter6_working:
        # Append new clusters so previously released text retains its encoding.
        seed=cluster_path if cluster_path.exists() else WORK/('reference/through-chapter5-cluster-map.json' if chapter6_working else 'reference/through-chapter4-cluster-map.json' if chapter5_working else 'reference/through-chapter3-cluster-map.json' if chapter4_working else 'reference/ui-completion-cluster-map.json')
        if review and not cluster_path.exists():seed=WORK/review['seed']
        cmap=json.loads(seed.read_text(encoding='utf-8'))
        next_code=max(map(ord,cmap.values()))+1
        for cluster in clusters:
            if cluster not in cmap:
                assert next_code<=0xf8ff,'Private-use font range exhausted'
                cmap[cluster]=chr(next_code);next_code+=1
    previous = None
    if text_only:
        assert ui_completion_working or chapter3_working or chapter4_working or chapter5_working or chapter6_working, "Text-only refresh requires a verified combined working set"
        assert json.loads(cluster_path.read_text(encoding="utf-8")) == cmap, "Font cluster map changed; rebuild all fonts"
        previous = json.loads((QA/"build-verification.json").read_text(encoding="utf-8"))
        assert len(previous['fonts']) == 8
    cluster_path.write_text(json.dumps(cmap,ensure_ascii=False,indent=2),encoding="utf-8")
    font = instantiateVariableFont(TTFont(WORK/"tools/fonts/NotoSansThai-Variable.ttf"),
                                   {"wght":300,"wdth":100},inplace=False)
    font_path = WORK/"tools/fonts/NotoSansThai-Light.ttf"
    font.save(font_path)
    b.FONT=font_path
    b.QA=QA
    reverse = str.maketrans({v:k for k,v in cmap.items()})
    for asset,patch in changes["assets"].items():
        target = STAGE/asset
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(patch_asset(WORK/"source"/asset,patch,cmap))
        parsed = txtres.parse(str(target))
        for key,value in patch["entries"].items():
            assert parsed[key]["Text"].translate(reverse)==value,key
            assert re.findall(r"</?[^>]+>", parsed[key]["Text"]) == re.findall(r"</?[^>]+>", value), key
        for key,value in patch["actors"].items():
            assert parsed[key]["MetaData"]["ACTOR"]==value,key
    fonts=previous['fonts'] if previous else []
    common=Path("End/Content/Menu/Billboard/Common")
    sources=[] if text_only else sorted((WORK/"source"/common).glob("U_Com_JP_SystemFont*.uasset"))
    for source in sources:
        if "-" in source.name:
            continue
        fd,td,stats=b.patch_font(source,cmap,allow_expand=True,scale_override=1.15,align_digits=True,align_latin=menu_working)
        dest=STAGE/common/source.name
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(fd)
        dest.with_name(source.stem+f'-{stats["page"]:02d}.uasset').write_bytes(td)
        fonts.append(stats)
        print(f'Built {source.stem}, Thai {stats["thai_pixel_size"]}px, atlas {stats["atlas_size"]}',flush=True)
    native_alignment=None
    if (ui_completion_working or chapter3_working or chapter4_working or chapter5_working or chapter6_working) and (WORK/'reference/native-baseline-policy.json').exists():
        from align_dynamic_baselines import align_fonts
        native_alignment=align_fonts(STAGE,cmap,report_path=review['qa']+'/native-baseline-alignment.json' if review else 'qa/chapter6/native-baseline-alignment.json' if chapter6_working else 'qa/chapter5/native-baseline-alignment.json' if chapter5_working else 'qa/chapter4/native-baseline-alignment.json' if chapter4_working else 'qa/chapter3/native-baseline-alignment.json' if chapter3_working else 'qa/baseline-alignment/alignment.json')
    punctuation=None
    if review:
        from align_dialogue_punctuation import apply
        punctuation=apply(STAGE,review['punctuation_policy'],review['qa']+'/punctuation-alignment.json')
    report=dict(chapter=review.get('chapters',[1,2,3,4,5,6]) if review else [1,2,3,4,5,6] if chapter6_working else [1,2,3,4,5] if chapter5_working else [1,2,3,4] if chapter4_working else [1,2,3] if chapter3_working else [1,2] if chapter2_working else 1,dialogue_translations=1157+changes.get("chapter2_records",0)+changes.get('chapter3_records',0)+changes.get('chapter4_records',0)+changes.get('chapter5_records',0)+changes.get('chapter6_records',0),english_ui_names=27,
                thai_clusters=len(cmap),font="Noto Sans Thai",weight=300,
                original_latin_glyphs_preserved=True,fonts=fonts,runtime_tested=False,
                menu_records=len(changes.get("menu_ids",[])),inventory_records=changes.get("inventory_description_records",0),ui_completion_records=changes.get("ui_completion_records",0),working_assets_only=menu_working)
    (QA/"build-verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    if native_alignment:
        report['native_baseline_alignment']=native_alignment
        (QA/"build-verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    if punctuation:
        report['dialogue_punctuation_alignment']=punctuation
        (QA/"build-verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("Working set staged and round-trip checked" if menu_working else "Chapter 1 staged and subtitle round-trip checked",flush=True)


if __name__=="__main__":
    main(menu_working="--menus-working" in sys.argv, chapter2_working="--chapter2-working" in sys.argv,inventory_working="--inventory-working" in sys.argv,ui_completion_working="--ui-completion-working" in sys.argv,text_only="--text-only" in sys.argv,chapter3_working="--chapter3-working" in sys.argv,chapter4_working="--chapter4-working" in sys.argv,chapter5_working="--chapter5-working" in sys.argv,chapter6_working="--chapter6-working" in sys.argv or "--ch12-recheck-working" in sys.argv,review_working="--ch12-recheck-working" in sys.argv)
