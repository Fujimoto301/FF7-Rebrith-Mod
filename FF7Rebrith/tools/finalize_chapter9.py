"""Verify delivered Ch9 artifacts and persist the current handoff, without installing."""
import hashlib
import re
from collections import Counter
from pathlib import Path
from prepare_chapter9 import W, read, write
from assemble_ui_completion import fingerprint


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    cfg = read('reference/chapter9-build.json')
    audit = read('qa/chapter9/translation-audit.json')
    baseline = read('qa/chapter9/baseline.json')
    gender = read('qa/chapter9/gender/summary.json')
    gate = read('qa/shared-dialogs/latest.json')
    sign = read('qa/chapter9/editorial-signoff.json')
    numeric = read('qa/chapter9/numeric-review.json')
    glyphs = read('qa/chapter9/old-glyph-regression.json')
    proof = read('qa/chapter9/proof.json')
    release = read('qa/final-parts/latest.json')
    mount = read('qa/final-parts/combined-mount-verification.json')
    manifest = read('qa/chapter9/working-assets.json')
    deferred = read('reference/chapter9-deferred.json')
    total = audit['total_combined_text_records']
    source_hash = digest(W / cfg['source'])
    recheck = read('qa/chapter9/recheck-review.json')
    assert recheck['source_sha256'] == source_hash and recheck['added_records'] == 8 and recheck['corrected_records'] == 69
    assert recheck['all_prior_IDs_and_ACTOR_preserved'] and recheck['all_font_assets_unchanged']
    assert sign['recheck_proof_visually_reviewed'] and sign['recheck_reviewed_proof_pages'] == 4
    assert len(read('qa/chapter9/recheck-proof.json')['samples']) == 32
    assert release['chapters'] == list(range(1, 10))
    assert release['combined_text_records'] == total == gender['source_records_scanned'] == 32859
    assert audit['new_records'] == 2203 and audit['previous_records_preserved'] == 30656
    assert audit['old_text_and_ACTOR_preserved'] and not audit['missing'] and not audit['japanese_remaining'] and not audit['tag_mismatches']
    assert source_hash == gender['combined_source_sha256'] == sign['combined_source_sha256'] == gate['source_sha256'] == numeric['source_sha256']
    assert sign['translation_sha256'] == digest(W / 'translations/chapter9-th.json')
    assert numeric['reviewed'] and sign['proof_visually_reviewed'] and sign['reviewed_proof_pages'] == 4
    assert not gender['gender_mismatches'] and not gender['unresolved_particle_bearing_speakers']
    assert len(glyphs['fonts']) == 8 and all(f['all698_metrics_preserved'] for f in glyphs['fonts'])
    assert len(proof['samples']) == 32 and not any(s['clipped'] for s in proof['samples'])
    assert mount['zip_count'] == 7 and mount['mod_files'] == 21 and mount['assets'] == 26
    assert mount['all_match_verified_combined_set'] and not mount['overlapping_assets']
    assert fingerprint() == baseline['protected']
    for path, value in baseline['source_hashes'].items():
        assert digest(W / path) == value, path
    previous = read(Path(baseline['backup']) / 'qa/final-parts/latest.json')
    previous = {p['zip']: p for p in previous['parts']}
    final = W.parent / 'Mod/Final'
    assert {p.name for p in final.iterdir()} == {p['zip'] for p in release['parts']}
    updated, unchanged, added = [], [], []
    union = {}
    for part in release['parts']:
        assert digest(final / part['zip']) == part['sha256']
        assert not union.keys() & part['assets'].keys()
        union.update(part['assets'])
        assert all(manifest[k] == v for k, v in part['assets'].items())
        if part['zip'] not in previous:
            added.append(part['zip'])
        else:
            (unchanged if part['sha256'] == previous[part['zip']]['sha256'] else updated).append(part['zip'])
    assert union == manifest
    assert set(added) == {'ThaiJP_Chapter9_P.zip'}
    assert set(updated) == {'ThaiJP_Chapter1_P.zip', 'ThaiJP_Common_P.zip'}
    assert len(unchanged) == 4
    pre_recheck = read(Path(read('qa/chapter9/recheck/current.json')['snapshot']) / 'qa/final-parts/latest.json')
    pre_recheck = {p['zip']: p for p in pre_recheck['parts']}
    recheck_updated = [p['zip'] for p in release['parts'] if p['sha256'] != pre_recheck[p['zip']]['sha256']]
    recheck_unchanged = [p['zip'] for p in release['parts'] if p['sha256'] == pre_recheck[p['zip']]['sha256']]
    assert set(recheck_updated) == {'ThaiJP_Chapter9_P.zip', 'ThaiJP_Common_P.zip'} and len(recheck_unchanged) == 5
    write('qa/chapter9/release-verification.json', dict(
        chapters=list(range(1, 10)), text_records=total, new_records=audit['new_records'],
        previous30656_text_and_ACTOR_preserved=True, assets=26, glyph_clusters=711,
        previous698_assignments_and_metrics_preserved=True,
        previous_Thai_masks_may_have_BC5_recompression=True, native_pixels_preserved=True,
        ZIP_count=7, mod_files=21, added_parts=added, updated_parts=updated, unchanged_parts=unchanged,
        all_parts_read_back_and_mounted_together=True, no_overlapping_assets=True,
        source_and_installed_files_unchanged=True, source_sha256=source_hash,
        recheck_added=8, recheck_corrected=69, recheck_previous32851_IDs_and_ACTOR_preserved=True,
        recheck_all_font_assets_unchanged=True,
        recheck_updated_parts=recheck_updated, recheck_unchanged_parts=recheck_unchanged,
        actual_gender_particle_occurrences=gender['actual_particle_occurrences'], gender_mismatches=[],
        proof_visually_reviewed=True, deferred_records=len(deferred),
        installed=False, in_game_tested=False, new_full_video_audio_review=False,
        manifest='qa/final-parts/latest.json', backup=release['backups']))

    base = 'E:/FF7RebrithModTH/FF7Rebrith/'
    parts = '\n'.join(f"| {p['zip']} | {len(p['assets'])} | {p['bytes']:,} |" for p in release['parts'])
    reasons = '\n'.join(f'| {reason} | {count} |' for reason, count in Counter(r['reason'] for r in deferred).items())
    note = f'''<!-- chapter9-current -->
## ล่าสุด: Chapter 9 — The Planet Stirs ตรวจซ้ำ — 19 ตุลาคม 2026

ส่วนนี้แทนยอด พาธ และสถานะปัจจุบันในประวัติด้านล่าง Ch.9 เสร็จและแพ็กแล้ว เพิ่ม **2,203 รหัส** (บทพูด 1,911 / system 72 / UI 220) รวม **32,859 รหัส / 26 assets / 711 clusters** คงข้อความและ ACTOR ของฐาน Ch.8 ที่แก้เอริธแล้วทั้ง 30,656 รหัส ครอบคลุมบทหลัก Gongaga, NPC, เควสต์ที่พร้อมใน Ch.9, โปรโตเรลิก, CARDG/PHOTO/WORLD และคำถามพร้อมทุกตัวเลือกในหมวดที่ลงทะเบียน พักเหตุการณ์ภายหลัง 252 รหัสพร้อมเหตุผล ไม่เริ่ม Ch.10

รีเช็คครั้งนี้เพิ่ม 8 รหัส แก้ 69 รหัสเหนือ Ch.9 เดิม 32,851 รหัส: ป้าย Chadley's Research อีก 6 ภูมิภาคและคำอธิบายกุญแจบักกี้/ปืนยิงลวด แก้คำตอบ Aerith และคำทักทายที่ใช้คำแปลเดิมไม่เข้าบริบท ปรับชื่อ Ch.9 เป็นทีฟ่า/แชดลี่ย์/โจโกโบะ/มาโก้/เจโนวา/เรดตาม glossary เดิม ไม่เปลี่ยนบท Ch.1–8 ฟอนต์ทั้ง 16 assets ไม่เปลี่ยน อัปเดต ZIP Chapter9 และ Common เท่านั้น อีก 5 ZIP hash เดิมเมื่อเทียบก่อนรีเช็ค หลักฐาน qa/chapter9/recheck-review.json

ฐาน **{base}translations/working-through-chapter9-th.json**; stage staging/ThaiJP_ThroughChapter9_Working; config reference/chapter9-build.json; map reference/through-chapter9-cluster-map.json; QA qa/chapter9 รายละเอียดครบที่ [CHAPTER9-STATUS.md]({base}CHAPTER9-STATUS.md)

Final มี **7 ZIP ล่าสุดแยกส่วน** Chapter1 / Chapter2 / Chapter3_4_5 / Chapter6_7 / Chapter8 / Chapter9 / Common ต้องใช้ร่วมกัน เพิ่ม ThaiJP_Chapter9_P.zip อัปเดต Chapter1 เพราะมี Zack ใน MIDGR และ Common เพราะ Resident/ฟอนต์ อีก 4 ZIP คง hash เดิม อ่านกลับรวม 21 mod files / 26 assets ไม่มีทับกัน สำรองนอก Final ต้นฉบับ/dist/ไฟล์ที่ติดตั้งไม่เปลี่ยน ไม่ได้ติดตั้งหรือทดลองในเกม

ตรวจ standing gate UI ญี่ปุ่นเดิม {gate['verified_JP_origin_records']:,} รหัส พร้อม NPC ส่วนกลาง คำลงท้ายรวม 976 ครั้งใน 952 รหัส: ครับ 651 / ค่ะ 198 / คะ 127 ชาย 651 / หญิง 325 กลุ่ม NPC/nonparty 838 ครั้ง ไม่มีสลับเพศตามหลักฐานรายรหัส Unknown NPC ใช้กลาง ไม่อนุมานเพศจาก mma/mfa หลักฐานโซเท็ตสึมาจากชื่อผู้พูดและ US รหัสเดียวกันที่ระบุ his training

Aerith ในคำพูดใช้ **เอริธ** ป้ายผู้พูดใช้ Aerith; เฉิง / อิเลน่า / คิริเอะ / วิสเปอร์ / โปรโตเรลิก ตรงฐานเดิม ชื่อใหม่ เช่น กอนกาก้า ซิสเน่ โซเท็ตสึ อิโซ เป็นคำสะกดที่ตรวจในงานนี้ ไม่อ้างว่าเทียบเสียง Plearn ครบใหม่ … ยังคงระดับจุดล่าง เลขและอังกฤษ native อยู่แนวเดิม

เพิ่ม 13 clusters แบบ append-only รักษา assignment/metrics ไทยเดิม 698 ตัวครบ 8 fonts และ native ASCII/เลข/ไอคอนพิกเซลเดิม ปรับ build_prototype.py ให้ใช้พื้นที่ว่างปลอดภัยของ atlas เดิมร่วมกับพื้นที่ต่อขยาย และเขียนบล็อก glyph ใหม่คืนหลังคืน mip เดิม แก้ความจุ XLarge4K โดยไม่ลดขนาด raster; BC5 ไทยเดิมอาจต่างเล็กน้อยจาก repack ไม่อ้างว่าไบต์ไทยเดิมตรงทุกตัว ดู proof จริง 4 หน้า/32 ตัวอย่างแล้ว ไม่ใช่ภาพเกมและไม่ได้ฟังวิดีโอครบใหม่

build chain: assemble_chapter9.py → build_chapter9.py (เต็มเมื่อเพิ่ม glyph, --text-only เมื่อไม่เพิ่ม) → build_chapter9.py --verify → audit_chapter9.py → audit_gender_through_chapter9.py → audit_shared_dialogs.py → audit_chapter9_glyph_regression.py → preview_chapter9.py (ดูภาพ) → audit_chapter9_recheck.py และ preview_chapter9.py --recheck (ดูภาพ) → ผูก editorial-signoff/numeric-review กับ hash ปัจจุบัน → publish_final_parts.py → verify_final_parts.py → finalize_chapter9.py ห้าม prepare ซ้ำ/เปลี่ยน index/ใช้ audit หรือ finalize บทเก่าทับ active context

ทุกบทต่อไปต้องค้น NPC มี/ไม่มี ACTOR และ Resident/PHOTO/WORLD/CARDG กับ namespace ข้างเคียง ตรวจคำถามและทุกปุ่ม รับ/ปฏิเสธ/ยกเลิก/ลองใหม่/ผลแพ้ชนะทั้งหมวด เพิ่ม family ใน audit_shared_dialogs.py ก่อนแพ็ก ตรวจสถานะพักที่เพิ่งปลดล็อก รวมชื่อ/เลข/เพศ/ระดับ … เสมอ ไม่อาศัยเลขบทหรือ *_sys อย่างเดียว
<!-- /chapter9-current -->

'''
    status = f'''# Chapter 9 — The Planet Stirs

{note}
## รายละเอียดตรวจซ้ำ

เทียบ snapshot Ch.9 ก่อนรีเช็คใน qa/chapter9/recheck/current.json คง ID และ ACTOR เดิมทั้งหมด เพิ่ม 8 รหัส/แก้ 69 รหัส รวม 32,859 รหัส คงฐาน Ch.1–8 ทั้ง 30,656 ข้อความเหมือนเดิมทุกตัว แก้ そうだね ของ Aerith จากคำตอบรับข้อเสนอเป็นการยอมรับว่าเธอยังชอบ Zack ปรับชื่อกับศัพท์ตามหลักฐาน PlearnGaming ใน glossary เดิม ไม่อ้างฟังใหม่ เปลี่ยนโรงงานเป็นโรงช่างของ Izo และทำคำทักทาย/お疲れ ให้เป็นธรรมชาติ

ค้น corpus ด้วยทั้ง ID และข้อความญี่ปุ่นโดยไม่เรียก selector เดิม พบข้อความที่แปลแล้วสัมพันธ์กับคำค้น 2,390 รหัส พร้อมแยกนอกขอบเขต 262 รหัสรายรหัส (GONGE สถานะภายหลัง 244 / Resident 15 / ฉาก Cosmo-Nibel 3) หมวดนอกขอบเขตที่ได้จากคำค้นนี้ไม่เท่ากับยอด deferred 252 ซึ่งรวม Resident กลุ่มเหยื่อตกปลาภายหลังอีก 8 รหัสด้วย รายการครบใน recheck-review.json ไม่ใช่การยืนยันว่าคำค้นจับข้อความทั้งเกมทุกชนิด

เพิ่ม CHADLEY_SHOP_ และ key_GONGM_ ทั้ง family ใน standing gate แล้ว ตรวจ UI ต้นฉบับญี่ปุ่น 2,844 รหัส คำถาม/ตัวเลือก/NPC และเพศผ่าน ฟอนต์ทั้ง 16 assets เหมือนก่อนรีเช็ค byte-for-byte ดู recheck-proof 4 หน้าเพิ่มจาก proof เดิม 4 หน้า ไม่มี glyph ใหม่ ไม่มีการทดลองในเกม

## ขอบเขตและงานที่ทำแล้ว

คัดต้นฉบับ 2,455 รหัส / 2,262 แม่แบบ แปลใหม่ 2,203 รหัส ตรวจย้อนกับ corpus อิสระและ decode จาก staging จริงทุกข้อความในขอบเขต ไม่พบญี่ปุ่นตกค้างหรือแท็ก/metadata ผิดจากต้นฉบับในกลุ่มที่เลือก UI Gongaga ทั้ง family ที่ลงทะเบียน 290 รหัส รวมรหัสเดิม 70 รหัส

- GONGE: C2710/C2810 บทหลักผ่านเที่ยวบิน Cid และช่วง Hojo/Roche; เควสต์ The Pursuit of Perfection, Teach Me Great Warrior, The Spice of Life, O Chicken; GONGM boss11/12 และ GONGV NPC ทุกรหัสที่อยู่ในสถานะนี้
- CHADL_QST04 ครบ 238 รหัส โปรโตเรลิก/ภาพจำลอง Turks รวมคำถาม คำตอบทั้ง 3 ทาง และผลลัพธ์
- MIDGR: Zack กลุ่ม C2710 จำนวน 15 รหัส อยู่ใน ZIP Chapter1 ตามเจ้าของ asset เดิม
- Resident: CARDG_QST14 จำนวน 49 รหัส, PHOTO_QST05 จำนวน 21 รหัส, WORLD_CDV01 ช่วง Gongaga/การบอกทาง และ WORLD_CDV02_0500 กับ WORLD_MGV01_0500 กลุ่ม Chadley/MAI ที่คัด ไม่รวมคำใบ้เควสต์กลับภูมิภาคภายหลัง 8 รหัส
- UI ทั้งหมวด: เป้าหมาย/คำถามพื้นที่ GONG และ level2400, ร้าน/สนามจำลอง/รายงานโลก/AreaReport, ล่อไก่/เก็บเห็ด, ของเควสต์ 22/24/25, เป้าฝึกโซเท็ตสึและชื่อ NPC/ร้านที่เกี่ยวข้อง รวมคำสั่ง Zack

รหัสที่มี _NPC_ ใหม่ 249 บรรทัด ไม่มี ACTOR 228 บรรทัด เป็นจำนวนบรรทัด ไม่ใช่จำนวนตัวละคร และไม่รวม NPC ที่ใช้รหัสเควสต์/PHOTO/CARDG/WORLD รายการ choice-review 125 candidate เป็นชุดตรวจคำถาม/ระบบ ไม่ใช่จำนวนปุ่มทั้งหมด การตรวจ family ครอบคลุมคำตอบและผลลัพธ์ที่สัมพันธ์กันด้วย

## งานที่พักและต้องทบทวนเมื่อปลดล็อก

พัก 252 รหัส รายรหัสอยู่ reference/chapter9-deferred.json:

| เหตุผล | รหัส |
| --- | ---: |
{reasons}

รายการค้นข้างเคียงรอบแรกอยู่ qa/chapter9/neighbour-dispositions.json; การค้นอิสระรอบรีเช็คที่กว้างขึ้นอยู่ qa/chapter9/recheck-review.json ครอบคลุม WORLD_CDV03 สำหรับ Queen's Blood ภายหลัง ของสะสม Shinra Manor/จดหมาย Snaps หลังเที่ยวภูมิภาคอื่น และคำบรรยาย/เคล็ดลับประเมินศัตรูซึ่งแยกจากป้ายชื่อศัตรูอังกฤษเดิม ไม่อ้างว่าบทพูดหรือคำอธิบายศัตรูทั้งเกมแปลครบแล้ว นำรายการพัก Ch.6–9 มาทบทวนตามเหตุการณ์เมื่อทำบทถัดไป ห้ามใช้เลขบทหรือบุคลิก Red เพียงอย่างเดียวตัดสินขอบเขต

## ชื่อ เพศ ตัวเลข และฟอนต์

JP เป็นหลัก ชื่อเฉพาะใน UI/ACTOR ใช้ US รหัสเดียวกัน ชื่อในคำพูดและจดหมายเป็นไทย คงปุ่ม/แท็ก/ตัวแปรเดิม เลขจริงใช้อารบิก รวม 半刻 ประมาณ 1 ชั่วโมงตาม US within the hour, ครึ่งปี 6 เดือน, 1億 = 100000000 และ 100万 = 1000000 ตรวจ numeric differences 12 รายการแล้วใน numeric-review.json

หญิงใช้ค่ะบอกเล่า คะคำถาม/นะคะ ชายใช้ครับตามน้ำเสียง ไม่เติมทุกประโยค NPC ไม่ทราบเพศใช้กลาง หลักฐานรายรหัสอยู่ gender/records.json รวม 976 ครั้งใน 952 รหัส ครับ 651 / ค่ะ 198 / คะ 127; NPC/nonparty 838 ครั้ง (ครับ 589 / ค่ะ 160 / คะ 89) คงคำลงท้ายเดิม 701 ครั้ง ไม่มี mismatch หรือผู้พูดที่ยังไม่ทราบเพศในบรรทัดที่ใช้คำลงท้าย

เฉิง, อิเลน่า, คิริเอะ, วิสเปอร์, โปรโตเรลิก, เกลนิก้า, ไม และเอริธตรงฐานเดิม ชื่อใหม่ กอนกาก้า/ซิสเน่/โซเท็ตสึ/อิโซ/ทอร์แกน/โกย่า/ซาจิ/ออสการ์/ซิด ไฮวินด์ เป็นคำสะกดบรรณาธิการของงานนี้ ไม่อ้างยืนยัน Plearn ใหม่ โซเท็ตสึมีหลักฐาน US $level_QUEST23_Task_Explanation_110 “his training” เชื่อมกับบทแนะนำตัวที่มีชื่อชัดเจน ไม่ใช้รหัส generic ชี้เพศ Red ในเควสต์ที่มี 2 บุคลิกแปลทั้งแขนงโดยแยกน้ำเสียง

711 clusters: เพิ่ม กุ๊ ง่ำ จิ๋ ชู้ ดุ้ ติ้ ฟึ รึ้ ศ์ หั่ อิ้ ฮื่ ฮ็ รักษา mapping/metrics เดิม 698 ตัว ตรวจ glyph ไม่ว่างและ native ASCII/เลข/ไอคอน/ระยะ/แนวจุดครบ 8 fonts แก้ atlas capacity โดยใช้ช่องว่างที่ปลอดภัยกับพื้นที่ต่อขยาย ไม่ลด raster; BC5 masks ไทยเดิมต่างเล็กน้อยได้ตามรายงาน ไม่เท่ากับการรักษาไบต์ไทยทุกตัวเหมือนเดิม

ตรวจภาพ proof จาก glyph ใน staging จริง 4 หน้า / 32 ตัวอย่าง Large และ Normal รวมชื่ออังกฤษ ตัวเลข ตัวแปรและจุดไข่ปลา เป็นภาพจัดบรรทัดประกอบ ไม่ใช่ภาพเกม ยังไม่ยืนยันทุกบรรทัด/ทุกตัวเลือกในเกมจริง ไม่มีการดูหรือฟังวิดีโอครบใหม่

## ZIP ล่าสุด

| ZIP | assets | bytes |
| --- | ---: | ---: |
{parts}

ที่เก็บ **E:/FF7RebrithModTH/Mod/Final** ใช้ทั้ง 7 ส่วนร่วมกัน เพิ่ม Chapter9 อัปเดต Chapter1 และ Common อีก 4 ส่วน hash เดิม อ่านกลับ/mount รวม 21 mod files ตรง staging 26 assets ไม่มีซ้ำ Final เก็บเฉพาะล่าสุดของแต่ละส่วน สำรองเดิมที่ {release['backups']} ไม่ได้ติดตั้งและไม่ได้แก้ต้นฉบับ/dist/ม็อดในเกม

## ไฟล์ส่งต่อ

ทุกพาธในตารางต่อจาก **{base}**:

| งาน | ไฟล์ |
| --- | --- |
| ฐานปัจจุบัน | translations/working-through-chapter9-th.json |
| คำแปล Ch.9 | translations/chapter9/batch-00.json ถึง batch-11.json, reused-lines.json, reviewed-official-titles.json, zz-recheck.json; translations/chapter9-th.json |
| JP/US/แม่แบบ/ขอบเขต | reference/chapter9-source.json, chapter9-templates.json, chapter9-scope.json, chapter9-deferred.json; rebirth-jp-corpus.json |
| config/map/stage | reference/chapter9-build.json, through-chapter9-cluster-map.json, dialogue-punctuation-policy.json; staging/ThaiJP_ThroughChapter9_Working |
| snapshot ห้ามทับ | qa/chapter9/baseline.json และ revisions/; ใช้ corrected Ch.8 ไม่ใช้ Ch.7 เก่าเป็นฐาน |
| เนื้อหา/ตัวเลือก/เลข/บริบท | qa/chapter9/translation-audit.json, review-records.json, choice-review.json, relationship-context-review.json, number-review.json, numeric-review.json, editorial-notes.json, editorial-signoff.json, neighbour-dispositions.json |
| เพศ | qa/chapter9/gender/summary.json, gender/records.json |
| ฟอนต์/ภาพ | qa/chapter9/verification.json, build-verification.json, old-glyph-regression.json, native-baseline-alignment.json, punctuation-alignment.json, proof.json, proof-1.png ถึง proof-4.png |
| รีเช็ค | qa/chapter9/recheck/current.json, recheck-review.json, recheck/editorial-decisions.json, recheck-proof.json, recheck-proof-1.png ถึง recheck-proof-4.png; tools/recheck_chapter9.py, audit_chapter9_recheck.py |
| ส่งมอบ | qa/chapter9/working-assets.json, release-verification.json; qa/active-working-set.json; qa/final-parts/latest.json, combined-mount-verification.json; FINAL-PARTS.md |
| เครื่องมือ | tools/prepare_chapter9.py (ห้ามรันซ้ำ), extend_chapter9.py, assemble_chapter9.py, build_chapter9.py, audit_chapter9.py, audit_gender_through_chapter9.py, audit_chapter9_glyph_regression.py, preview_chapter9.py, finalize_chapter9.py; audit_shared_dialogs.py, publish_final_parts.py, verify_final_parts.py |

Python **C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe** ตั้ง PYTHONUTF8=1 รันจากโปรเจกต์ตาม chain ในบันทึกด้านบน การเพิ่ม glyph ต้อง build เต็ม ไม่ใช้ --text-only ถ้าแก้ข้อความต้องทบทวน numeric/signoff ที่ผูก hash และดู proof ใหม่ก่อนส่ง ไม่รัน prepare/extend เพื่อล้าง index หรือใช้ finalize บทเก่าทับบริบท

เมื่อผู้ใช้สั่ง Ch.10 ให้เริ่ม working-through-chapter9-th.json กับ map 711 ตัว ตรวจ NPC ทั้งมี/ไม่มี ACTOR และ shared/namespace ข้างเคียง ทบทวนรายการพักตามสถานะจริง เพิ่ม family ลง audit_shared_dialogs.py ก่อนแพ็ก แยก ZIP ตามเจ้าของ asset เท่านั้น หากใช้ฉากร่วมให้รวมแพ็กเดิมตามนโยบาย เก็บ Final ล่าสุดของแต่ละส่วนเสมอ ไม่ติดตั้งจนได้รับคำสั่ง

แหล่งบท/เสียง/เพศที่ส่งต่อจากงานเดิม: [คลิปหลัก](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk), reference/plearngaming/remake/decoded-corpus.json ไม่มี timestamp หรือการฟังครบใหม่ในรอบนี้
'''
    (W / 'CHAPTER9-STATUS.md').write_text(status, 'utf-8')
    for path in [W.parent / 'HANDOFF.md', W / 'AGENTS.md', W / 'TRANSLATION_GUIDE.md']:
        text = path.read_text('utf-8')
        title, body = text.split('\n', 1)
        body = re.sub(r'<!-- chapter[789]-current -->.*?<!-- /chapter[789]-current -->\s*', '', body, flags=re.S)
        path.write_text(title + '\n\n' + note + body.lstrip(), 'utf-8')
    (W / 'FINAL-PARTS.md').write_text(f'''# ZIP ล่าสุดแยกแต่ละส่วน

19 ตุลาคม 2026 หลัง Chapter9: **{total:,} ข้อความ / 26 assets / 711 clusters / 7 ZIP / 21 mod files**

| ZIP | assets | bytes |
| --- | ---: | ---: |
{parts}

ใช้ทั้ง 7 ZIP ร่วมกันใน **E:/FF7RebrithModTH/Mod/Final** รอบรีเช็คอัปเดตเฉพาะ Chapter9 และ Common อีก 5 ส่วน hash เดิม ฟอนต์ไม่เปลี่ยน (การเพิ่ม Ch.9 ครั้งแรกก่อนรีเช็คเคยอัปเดต Chapter1 เพราะ Zack/MIDGR แล้ว) เก็บล่าสุดของแต่ละส่วน สำรองนอก Final อ่านกลับร่วมครบ 26 assets ไม่มีทับกัน ยังไม่ได้ติดตั้งหรือทดลองในเกม

รายละเอียด [CHAPTER9-STATUS.md]({base}CHAPTER9-STATUS.md) และ [HANDOFF.md](E:/FF7RebrithModTH/HANDOFF.md)
''', 'utf-8')
    print('Chapter9 finalized:', total, 'records; 2203 added; 7 ZIPs verified; handoff saved')


if __name__ == '__main__':
    main()
