"""Verify scope, English labels, font preservation, and UE texture consumers."""
import io
import json
import re
import struct
import string
import sys

import build_prototype as b
from PIL import Image
import txtres
sys.path.insert(0,str(b.WORK/"tools/cutscene-tool/1.0/vendor"))
from UE4Parse.BinaryReader import BinaryStream
from UE4Parse.Versions import EUEVersion
from UE4Parse.Assets.Exports.Textures.Objects.FTexturePlatformData import FTexturePlatformData

WORK=b.WORK
STAGE=WORK/"staging/ThaiJP_Chapter1_P"
QA=WORK/"qa/chapter1"


def glyphs(data):
    e=b.header_end(data)
    start=10 if data[e:e+2]==b"\1\11" else 12
    count=struct.unpack_from("<I",data,e+start-4)[0]
    records=[struct.unpack_from("<6H2hH",data,e+start+i*18) for i in range(count)]
    return records,data[e+start+count*18:]


def atlas(path):
    data=path.read_bytes()
    e=b.header_end(data)
    # Consume the platform data with an external UE4 texture parser.
    stream=BinaryStream(data)
    stream.game=EUEVersion.GAME_UE4_26
    stream.version=stream.game.get_ar_ver()
    stream.seek(e+63,0)
    platform=FTexturePlatformData(stream,ubulk=None,ubulkOffset=0)
    assert not platform.bIsVirtual
    assert len(data)-stream.tell()==8, "Expected final None FName only"
    assert platform.PixelFormat.name=="PF_BC5"
    packed=b"".join(m.BulkData.Data for m in platform.Mips)
    img=Image.open(io.BytesIO(b.dds_header(platform.SizeX,platform.SizeY,len(platform.Mips))+packed)).convert("RGB")
    return img,platform


def main(menu_working=False, chapter2_working=False, inventory_working=False, ui_completion_working=False, chapter3_working=False, chapter4_working=False, chapter5_working=False, chapter6_working=False, review_working=False):
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
        menu_working=True
        chapter2_working=True
        STAGE=WORK/"staging/ThaiJP_ThroughChapter3_Working"
        QA=WORK/"qa/chapter3"
    elif ui_completion_working:
        menu_working=True
        chapter2_working=True
        STAGE=WORK/"staging/ThaiJP_UICompletion_Working"
        QA=WORK/"qa/ui-completion"
    elif inventory_working:
        menu_working=True
        chapter2_working=True
        STAGE=WORK/"staging/ThaiJP_Inventory_Working"
        QA=WORK/"qa/inventory"
    elif chapter2_working:
        menu_working=True
        STAGE=WORK/"staging/ThaiJP_ThroughChapter2_Working"
        QA=WORK/"qa/chapter2"
    elif menu_working:
        STAGE=WORK/"staging/ThaiJP_Working"
        QA=WORK/"qa/menu"
    edits=json.loads((WORK/("translations/working-through-chapter6-th.json" if chapter6_working else "translations/working-through-chapter5-th.json" if chapter5_working else "translations/working-through-chapter4-th.json" if chapter4_working else "translations/working-through-chapter3-th.json" if chapter3_working else "translations/working-ui-completion-th.json" if ui_completion_working else "translations/working-inventory-th.json" if inventory_working else "translations/working-through-chapter2-th.json" if chapter2_working else "translations/working-th.json" if menu_working else "translations/chapter1-th.json")).read_text(encoding="utf-8"))
    cmap=json.loads((WORK/("reference/through-chapter6-cluster-map.json" if chapter6_working else "reference/through-chapter5-cluster-map.json" if chapter5_working else "reference/through-chapter4-cluster-map.json" if chapter4_working else "reference/through-chapter3-cluster-map.json" if chapter3_working else "reference/ui-completion-cluster-map.json" if ui_completion_working else "reference/inventory-cluster-map.json" if inventory_working else "reference/through-chapter2-cluster-map.json" if chapter2_working else "reference/working-cluster-map.json" if menu_working else "reference/chapter1-cluster-map.json")).read_text(encoding="utf-8"))
    review=json.loads((WORK/(review_working if isinstance(review_working,str) else 'reference/ch12-recheck-build.json')).read_text('utf-8')) if review_working else None
    if review:
        STAGE=WORK/review['stage'];QA=WORK/review['qa']
        edits=json.loads((WORK/review['source']).read_text('utf-8'))
        cmap=json.loads((WORK/review['cluster_map']).read_text('utf-8'))
    reverse=str.maketrans({v:k for k,v in cmap.items()})
    text_reports=[]
    for asset,patch in edits["assets"].items():
        original=txtres.parse(str(WORK/"source"/asset))
        actual=txtres.parse(str(STAGE/asset))
        assert list(original)==list(actual),"ID or record order changed"
        untouched=0
        for key,item in original.items():
            text=patch["entries"].get(key,item["Text"])
            assert actual[key]["Text"].translate(reverse)==text,key
            assert re.findall(r"</?[^>]+>",actual[key]["Text"]) == re.findall(r"</?[^>]+>",text), key
            expected_meta=dict(item.get("MetaData",{}))
            if key in patch["actors"]:
                expected_meta["ACTOR"]=patch["actors"][key]
                assert not re.search(r"[\u3040-\u30ff\u4e00-\u9fff]",expected_meta["ACTOR"])
            assert actual[key].get("MetaData",{})==expected_meta,key
            if key not in patch["entries"] and key not in patch["actors"]:
                assert item==actual[key],key
                untouched+=1
        text_reports.append(dict(asset=asset,text_changes=len(patch["entries"]),
                                 english_actor_labels=len(patch["actors"]),untouched_records=untouched))
    screen_checks = {}
    screen_scope_path = WORK/"reference/menu-screen-settings-scope.json"
    if menu_working and screen_scope_path.exists():
        screen_scope=json.loads(screen_scope_path.read_text(encoding="utf-8"))
        resident=txtres.parse(str(STAGE/"End/Content/Text/JP/Resident_TxtRes.uasset"))
        for key,expected in screen_scope["protected_english"].items():
            assert resident[key]["Text"] == expected, (key,"English mode label changed")
            screen_checks[key]=expected
    font_reports=[]
    common="End/Content/Menu/Billboard/Common"
    for path in sorted((STAGE/common).glob("U_Com_JP_SystemFont*.uasset")):
        if "-" in path.name:
            continue
        original_path=WORK/"source"/common/path.name
        old,old_tail=glyphs(original_path.read_bytes())
        new,new_tail=glyphs(path.read_bytes())
        new_map={g[0]:g for g in new}
        assert len(new_map)==len(new)
        # The screenshot correction explicitly permits only U+2026's y-origin.
        punctuation_codes={8230} if review else set()
        assert all(new_map[g[0]]==g for g in old if g[0] not in punctuation_codes)
        for g in old:
            if g[0] in punctuation_codes:
                assert new_map[g[0]][:7]+new_map[g[0]][8:]==g[:7]+g[8:]
        assert old_tail==new_tail,"Font page references or icon map changed"
        assert all(ord(code) in new_map for code in cmap.values())
        page=max(g[1] for g in old)
        texture=path.with_name(path.stem+f"-{page:02d}.uasset")
        old_texture=original_path.with_name(texture.name)
        old_img,old_platform=atlas(old_texture)
        new_img,new_platform=atlas(texture)
        page_images = {page: new_img}
        def glyph_mask(g):
            if g[1] not in page_images:
                other = path.with_name(path.stem+f"-{g[1]:02d}.uasset")
                if not other.exists():
                    other = original_path.with_name(other.name)
                page_images[g[1]] = atlas(other)[0]
            img = page_images[g[1]]
            assert g[2]+g[4]<=img.width and g[3]+g[5]<=img.height, (path.name,g)
            return img.getchannel("R").crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
        if review:
            from align_dialogue_punctuation import expected_glyph
            original_map={g[0]:g for g in old}
            assert new_map[8230]==expected_glyph(original_map[8230],original_map[ord('.')],glyph_mask),path.name
        checked=0
        for g in old:
            if g[1]!=page or not g[4] or not g[5]:
                continue
            box=(g[2],g[3],g[2]+g[4],g[3]+g[5])
            assert old_img.crop(box).tobytes()==new_img.crop(box).tobytes(),f"Original glyph pixels changed: {path.name} U+{g[0]:04X}"
            checked+=1
        for cluster,code in cmap.items():
            g=new_map[ord(code)]
            mask=glyph_mask(g)
            assert mask.getbbox(),f"Empty Thai glyph: {cluster}"
        anchor = new_map[ord(cmap["ก"])]
        anchor_box = glyph_mask(anchor).point(lambda p: 255 if p >= 64 else 0).getbbox()
        thai_bottom = anchor[7] + anchor_box[3]
        if (ui_completion_working or chapter3_working or chapter4_working or chapter5_working or chapter6_working) and (WORK/'reference/native-baseline-policy.json').exists():
            native_h=new_map[ord('H')]
            native_box=glyph_mask(native_h).point(lambda p:255 if p>=64 else 0).getbbox()
            assert thai_bottom==native_h[7]+native_box[3],(path.name,'Thai vs native ASCII baseline')
        digit_checks = []
        original_map = {g[0]:g for g in old}
        for digit in "0123456789":
            alias = new_map[ord(cmap[digit])]
            original_digit = original_map[ord(digit)]
            assert alias[1:7] == original_digit[1:7] and alias[8] == original_digit[8], (path.name,digit)
            assert glyph_mask(alias).tobytes() == glyph_mask(original_digit).tobytes(), (path.name,digit)
            box = glyph_mask(alias).point(lambda p: 255 if p >= 64 else 0).getbbox()
            ink_bottom = alias[7] + box[3]
            assert abs(ink_bottom-thai_bottom) <= 1, (path.name,digit,ink_bottom,thai_bottom)
            digit_checks.append(dict(digit=digit,thai_ink_bottom=thai_bottom,digit_ink_bottom=ink_bottom,vertical_shift=alias[7]-original_digit[7]))
        latin_checks = []
        if menu_working:
            h = new_map[ord(cmap["H"])]
            h_box = glyph_mask(h).point(lambda p: 255 if p >= 64 else 0).getbbox()
            assert abs(h[7]+h_box[3]-thai_bottom) <= 1, path.name
            common_shift = h[7]-original_map[ord("H")][7]
            for letter in string.ascii_letters:
                alias = new_map[ord(cmap[letter])]
                original_letter = original_map[ord(letter)]
                assert alias[1:7] == original_letter[1:7] and alias[8] == original_letter[8], (path.name,letter)
                assert alias[7]-original_letter[7] == common_shift, (path.name,letter)
                assert glyph_mask(alias).tobytes() == glyph_mask(original_letter).tobytes(), (path.name,letter)
                latin_checks.append(dict(letter=letter,vertical_shift=common_shift))
        font_reports.append(dict(font=path.name,original_records_preserved=len(old),
                                 original_atlas_glyphs_pixel_checked=checked,
                                 thai_clusters_verified=len(cmap),texture_size=[new_img.width,new_img.height],
                                 texture_consumer="UE4Parse.FTexturePlatformData", aligned_digits=digit_checks, aligned_latin=latin_checks))
    assert len(font_reports)==8
    report=dict(chapter=review.get('chapters',[1,2,3,4,5,6]) if review else [1,2,3,4,5,6] if chapter6_working else [1,2,3,4,5] if chapter5_working else [1,2,3,4] if chapter4_working else [1,2,3] if chapter3_working else [1,2] if chapter2_working else 1,text=text_reports,fonts=font_reports,
                outside_scope_text_unchanged=True,original_font_glyphs_preserved=True,runtime_tested=False,
                menu_records=len(edits.get("menu_ids",[])),inventory_records=edits.get("inventory_description_records",0),ui_completion_records=edits.get("ui_completion_records",0),working_assets_only=menu_working)
    report["protected_english_mode_labels"]=screen_checks
    if review:
        report['original_font_glyphs_preserved_except_authorized_ellipsis_y']=True
        report['original_font_glyphs_preserved']=False
        report['authorized_font_change']='U+2026 vertical origin only; original pixels and spacing preserved'
    (QA/"verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("Verified chapter scope, English actor labels, original glyph pixels, and 8 UE4 texture assets")


if __name__=="__main__":
    main(menu_working="--menus-working" in sys.argv, chapter2_working="--chapter2-working" in sys.argv,inventory_working="--inventory-working" in sys.argv,ui_completion_working="--ui-completion-working" in sys.argv,chapter3_working="--chapter3-working" in sys.argv,chapter4_working="--chapter4-working" in sys.argv,chapter5_working="--chapter5-working" in sys.argv,chapter6_working="--chapter6-working" in sys.argv or "--ch12-recheck-working" in sys.argv,review_working="--ch12-recheck-working" in sys.argv)
