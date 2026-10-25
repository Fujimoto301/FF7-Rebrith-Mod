"""Verify delivered split archives and persist the Chapter7 handoff."""
import hashlib
from collections import Counter
from pathlib import Path
from assemble_chapter7 import W,read,write
from assemble_ui_completion import fingerprint

def main():
    cfg=read('reference/chapter7-build.json');audit=read('qa/chapter7/translation-audit.json');gender=read('qa/chapter7/gender/summary.json')
    baseline=read('qa/chapter7/baseline.json');release=read('qa/final-parts/latest.json');mount=read('qa/final-parts/combined-mount-verification.json')
    old=read(Path(baseline['backup'])/'qa/final-parts/latest.json');prior={p['zip']:p for p in old['parts']}
    assert release['chapters']==list(range(1,8)) and release['combined_text_records']==26951
    assert mount['zip_count']==5 and mount['assets']==24 and mount['mod_files']==15
    assert mount['all_match_verified_combined_set'] and not mount['overlapping_assets']
    assert fingerprint()==baseline['protected']
    final=W.parent/'Mod/Final';assert {p.name for p in final.iterdir()}=={p['zip'] for p in release['parts']}
    for p in release['parts']:
        assert hashlib.sha256((final/p['zip']).read_bytes()).hexdigest()==p['sha256']
        for rel,sha in p['assets'].items():assert read('qa/chapter7/working-assets.json')[rel]==sha
        if p['zip'] in ['ThaiJP_Chapter1_P.zip','ThaiJP_Chapter2_P.zip','ThaiJP_Chapter3_4_5_P.zip']:assert p['sha256']==prior[p['zip']]['sha256']
    assert not (final/'ThaiJP_Chapter6_P.zip').exists()
    assert gender['actual_particle_occurrences']==609 and not gender['gender_mismatches'] and not gender['unresolved_particle_bearing_speakers']
    assert gender['source_records_scanned']==26951
    sign=read('qa/chapter7/editorial-signoff.json')
    assert sign['translation_sha256']==hashlib.sha256((W/'translations/chapter7-th.json').read_bytes()).hexdigest()
    assert read('qa/shared-dialogs/latest.json')['combined_source']==cfg['source']
    assert len(read('qa/chapter7/proof.json')['samples'])==32
    assert len(read('qa/chapter7/old-glyph-regression.json')['fonts'])==8
    write('qa/chapter7/release-verification.json',dict(chapters=list(range(1,8)),text_records=26951,chapter7_records=1688,new_shared_speech=68,new_UI=196,selected_NPC_records=372,NPC_without_ACTOR=342,
      prior_24999_text_and_ACTOR_preserved=True,assets=24,glyph_clusters=687,append_only_old677=True,
      ZIP_count=5,mod_files=15,first_three_ZIPs_unchanged=True,renamed_part='ThaiJP_Chapter6_7_P.zip',superseded='ThaiJP_Chapter6_P.zip',
      all_parts_read_back_and_mounted_together=True,no_overlapping_assets=True,source_and_installed_files_unchanged=True,
      actual_gender_particle_occurrences=609,gender_mismatches=[],proof_visually_reviewed=True,installed=False,in_game_tested=False,new_full_video_audio_review=False,
      manifest='qa/final-parts/latest.json',backup=release['backups']))
    rows=read('reference/chapter7-source.json');deferred=read('reference/chapter7-deferred.json');keys={r['id'] for r in deferred}
    groups=Counter('_'.join(r['id'].split('_')[:2 if r['id'].startswith('$C2') else 3]) for r in rows if r['id'] not in keys)
    table='\n'.join(f'| {name} | {count:,} |' for name,count in groups.items())
    deferred_table='\n'.join(f'| {name} | {count} |' for name,count in Counter(r['reason'] for r in deferred).items())
    status=f'''# Chapter 7 — Those Left Behind

อัปเดต 18 ตุลาคม 2026 (Asia/Bangkok)

แปลและแพ็ก Ch.7 จากชุดตรวจซ้ำ Ch.1–6 ล่าสุดแล้ว เพิ่ม **1,688รหัสบท/ตัวเลือก +68บทส่วนกลาง/NPCที่ปลดล็อก +196UI =1,952รหัสใหม่** รวม **26,951รหัส /24assets /687glyph clusters** รักษาข้อความและACTORเดิม24,999รหัสครบ

## ขอบเขตบทและNPC

| กลุ่มหลัก | รหัสที่ใส่ในม็อด |
| --- | ---: |
{table}
| **รวมกลุ่มหลัก** | **1,688** |

ครอบคลุมขึ้น Mt. Corel, Aerith เหนื่อย/พัก, Turksและบอส, การประชุมRufus, Yuffieผ่านเหมือง, ลูกนกクラピヨ, ทุกแขนงรถรางปลอดภัย/หวาดเสียว, North Corel, หมอSheiran, อดีตหมู่บ้านและขึ้นกระเช้าไปGold Saucer เป็นจบบท ก่อนเริ่มCh.8 ไม่เพิ่มบทGold Saucerหรือทะเลทรายของบทถัดไป

เควสต์Johnnyเพิ่มช่วงวัสดุ/ซิปไลน์/หม้อต้มและขอให้ไปตามร่างแยกในทะเลทราย แต่ช่วงส่งมงกุฎและปรับปรุงโรงแรมยังรอการเข้าถึงพื้นที่ภายหลัง เควสต์นัดเดต/เก็บเปลือกหอย/งานชุดว่ายน้ำ, กำจัดมอนสเตอร์ให้ยิม/แข่งซิตอัปทุกผลลัพธ์ และช่วยเสื้อคลุมดำของหมอSheiranรวมคำถาม/ทางเลือกทั้งหมดในสถานะปัจจุบัน

NPCรวมกลุ่มรหัสNPC **372รหัส: North Corel312 +Costa60** รวมไม่มีACTOR342รหัส จำนวนนี้ไม่รวมคู่แข่งการ์ด เจ้าของเควสต์ หรือผู้พูดหลักที่เป็นNPCแต่ใช้รหัสกลุ่มอื่น Costa60นำมาจากรายการที่พักไว้ในCh.6 คือเช่าChocobo14, เห็นJohnnyหลายคน1, ผู้ชมงานชุดว่ายน้ำ8, ค่ายฝึก37 เพิ่มช่างภาพรายงานชายฝั่ง5และแรงก์หลังภูมิภาคCorel3 รวมบทเสริม68รหัส

## สถานะที่กันไว้

เตรียมกลุ่มหลัก1,966รหัส/1,891แม่แบบ เลือก1,688และกัน **278รหัส** พร้อมเหตุผลรายรหัสในreference/chapter7-deferred.json:

| เหตุผล | รหัส |
| --- | ---: |
{deferred_table}

บทเสียงวัยเด็กของRed/Nanakiเป็นคู่ทางเลือกหลังCosmo Canyon ไม่ปนกับเสียงเคร่งขรึมในCh.7 รายการพักไว้ของCh.6ยังเป็นประวัติ หัก60ที่ปลดล็อกแล้วตามรายการเสริมCh.7เมื่อทำต่อ อย่ากลับไปใช้จำนวนค้างเดิม107โดยไม่ตรวจรหัส เช่นเดียวกับ8บทช่างภาพที่ย้ายจากรายการค้างshared1–6มาแล้ว

## UI คำถาม ตัวเลือก และเพศ

สำรวจส่วนเสริม337รหัส:73เดิมคงไว้ เพิ่ม264(68บท/196UI) ตรวจCorel World Reportทั้ง159รหัสรวมรายงานทะเลทรายในฐานะUIตามนโยบายทั้งเกม, ร้าน/ตู้ขายของ, ของเควสต์, HUDเหมือง/หมู่บ้าน, ซิตอัปทุกระดับพร้อมชื่อUS มีรายการคำถาม/ตัวเลือกใหม่57รหัส(รวมsystem53รหัส และคำถามซิตอัป4แบบ) ตรวจค่าใช่/ไม่ใช่รายรหัส ไม่ใช้คำตอบค่ะของTifaกับปุ่มระบบที่JPซ้ำกัน

เพิ่มfamilyเข้าtools/audit_shared_dialogs.pyแล้ว ผลรวม1,555รหัสUIต้นฉบับญี่ปุ่น รวมshared NPC/ระบบที่กำหนด ตรวจว่ามีคำแปลจริงในstaging ไม่มีJPค้าง แท็ก/ตัวแปรและเมทาดาทาที่ไม่ใช่ACTORตรงต้นฉบับ การตรวจนี้ยืนยันกลุ่มรหัสที่คัดและหมวดที่ลงทะเบียน ไม่ใช่การทดลองtriggerทุกทางในเกม

ตรวจสัมพันธ์/สรรพนาม/คำเรียก219จุด ตัวเลขและคำคันจิ/สำนวน96จุด คงเลขอารบิกที่เป็นค่าชัดเจน เช่น5ปี,49/51,45/55,7,000เท่า,10,000กิล ส่วนหอยสองฝาเป็นชื่อสามัญ ไม่ใช่จำนวนหอย บันทึกqa/chapter7/editorial-signoff.jsonผูกhashคำแปล; หากแก้ให้ตรวจจุดเปลี่ยนและต่ออายุsignoffก่อนfinalize

คำลงท้ายทั้งชุดปัจจุบัน **609ครั้งใน594รหัส**: {gender['counts']} ชาย408/หญิง201 ไม่พบสลับเพศหรือคำลงท้ายที่ยังไม่ระบุตัวผู้พูด UnknownNPCกลาง ไม่เดาจากmma/mfa AminaมีหลักฐานJPระบุสมาชิกหญิง, Terrified WomanมีACTORおびえた女性ชัดเจน, Johnny/ร่างแยกใช้หลักฐาน男ジョニーจากCh.6, Yuffieแกล้งใช้คำสุภาพคะกับBarret; มีตัวอย่างในproof

ชื่อพูดไทยตามJP เช่นSheiran=ชีรอน, Navalan=นาบารา, クラピヨ=คลาปิโย แต่ป้ายUSยังDoctor Sheiran/Navalan/Cloud Jr. Fran/Naomi/Yordaในบทพูดใช้JPเฟรน/โนเอมี/ยอร์ดา บาร์เร็ต/โกลด์ซอซเซอร์/โชโคโบะ/เกล็นน์ตามงานเดิม Wutai=อู่ไถ ศัพท์ใหม่ไม่ได้อ้างว่าPlearnรับรอง ดูqa/chapter7/proper-name-review.json

## ฟอนต์และแพ็ก

เพิ่ม10clustersแบบappend-only จาก677เป็น687: {audit['new_clusters']} คง677assignment/metricsเดิมครบทั้ง8ฟอนต์ nativeASCII/ตัวเลข/ไอคอนต้นฉบับพิกเซลและmetricsเดิม ตรวจเส้นฐานThai/ASCII/เลขและ…ระดับล่างผ่านทั้ง8ฟอนต์ การจัดatlasไทยใหม่ทำให้maskBC5เดิมต่างเล็กน้อย จึงไม่อ้างว่าพิกเซลไทยเดิมทุกจุดเหมือนเดิม

ภาพproof4หน้าจากglyphในstagingจริง ตรวจแล้ว รวมคำถาม ชื่ออังกฤษ เลขและค่าที่แทนหลังencode เป็นการจัดบรรทัดประกอบการตรวจ ไม่ใช่ขนาดแผง/ภาพในเกม ยังไม่ได้ฟังวิดีโอครบใหม่หรือเล่นทดสอบ

ผู้ใช้เลือก **ThaiJP_Chapter6_7_P.zip** แทนThaiJP_Chapter6_P.zip เพราะCORLEใช้ร่วมกัน อัปเดตCommonด้วย อีก3ZIPแรกคงเดิม Finalเก็บล่าสุดของแต่ละส่วน5ZIP ต้องใช้ร่วมกัน อ่านกลับรวม15mod files24assetsผ่าน ไม่มีassetทับกัน สำรองZIPเก่านอกFinalตามqa/final-parts/latest.json ไม่ได้ติดตั้งหรือเปลี่ยนต้นฉบับเกม/dist/ม็อดในเกม

## ไฟล์และขั้นตอนทำต่อ

ฐาน **E:/FF7RebrithModTH/FF7Rebrith/**:

| งาน | ไฟล์ใต้ฐาน |
| --- | --- |
| รวมปัจจุบัน | translations/working-through-chapter7-th.json |
| กลุ่มหลักJP/US/แม่แบบ/ขอบเขต | reference/chapter7-source.json, chapter7-templates.json, chapter7-scope.json, chapter7-deferred.json; tools/prepare_chapter7.py, chapter7_scope.py |
| คำแปลหลัก | translations/chapter7/batch-00.json ถึง batch-09.json, reused-lines.json; translations/chapter7-th.json |
| ส่วนเสริมJP/US/แม่แบบ | reference/chapter7-supplement-source.json, chapter7-supplement-templates.json; tools/chapter7_supplement.py |
| คำแปลส่วนเสริม | translations/chapter7-supplement-manual.json, chapter7-supplement-automatic.json |
| config/glyph/stage | reference/chapter7-build.json, through-chapter7-cluster-map.json, dialogue-punctuation-policy.json; staging/ThaiJP_ThroughChapter7_Working |
| snapshotห้ามทับ | qa/chapter7/baseline.json และ revisions/ |
| ตรวจบท/ตัวเลือก/ความหมาย | qa/chapter7/review-records.json, choice-review.json, relationship-context-review.json, number-review.json, editorial-notes.json, editorial-signoff.json, proper-name-review.json |
| เพศ/ฟอนต์/แพ็ก | qa/chapter7/gender/summary.json, gender/records.json, verification.json, old-glyph-regression.json, proof-1.png ถึง proof-4.png, release-verification.json |
| สถานะปัจจุบัน/ZIP | qa/active-working-set.json, qa/final-parts/latest.json, combined-mount-verification.json |

Python `C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`; ตั้ง `$env:PYTHONUTF8='1'` แล้วรันจากโปรเจกต์:

```text
tools/assemble_chapter7.py
tools/build_chapter7.py --text-only
tools/build_chapter7.py --verify
tools/audit_chapter7.py
tools/audit_chapter7_glyph_regression.py
tools/audit_gender_through_chapter7.py
tools/audit_shared_dialogs.py
tools/preview_chapter7.py
tools/publish_final_parts.py
tools/finalize_chapter7.py
```

--text-onlyเมื่อglyphไม่เพิ่มและมีผลbuild8fontsแล้ว ถ้าเพิ่มglyphต้องbuildเต็มด้วยbuild_chapter7.py รักษาmapเก่า configseedปัจจุบันชี้ชุดตรวจ1–6 ห้ามprepareซ้ำ/สลับindex/ใช้auditหรือfinalizeบทเก่าทับactive context เริ่มCh.8จากworking-through-chapter7-th.jsonเท่านั้น

ทุกบทถัดไปต้องตรวจคำถามและตัวเลือกครบทั้งหมวด รวมResident/NPCไม่มีACTOR/namespaceข้างเคียง กิจกรรม/ผลชนะแพ้/ยกเลิก/ลองใหม่/ร้าน/ของเควสต์ ไม่อาศัย*_sysหรือเลขChapterอย่างเดียว ตรวจชื่อ/เพศ/ตัวเลข/ellipsisพร้อมกัน ขอบเขตบทต่อไปต้องรับคำสั่งจากผู้ใช้ ยังไม่เริ่มCh.8

แหล่งเดิมสำหรับเทียบบท/เพศ: [คลิปหลัก](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk) รอบนี้ไม่มีtimestampใหม่ ไม่อ้างว่าauto transcriptเป็นการฟังครบ
'''
    (W/'CHAPTER7-STATUS.md').write_text(status,'utf-8')
    note='''<!-- chapter7-current -->
## ล่าสุด: Chapter7 — Those Left Behind (18 ตุลาคม 2026)

ชุดนี้แทนพาธ/ยอด/ขั้นตอนปัจจุบันในประวัติด้านล่าง **26,951รหัส24assets687clusters** รักษา24,999ข้อความ/ACTORของชุดตรวจCh.1–6ครบ เพิ่ม1,688บท/ตัวเลือก +68บทส่วนกลาง +196UI รวม1,952รหัสใหม่ NPCในกลุ่มรหัสNPC372(ไม่มีACTOR342) คัดกลุ่มหลักจาก1,966และพัก278สถานะภายหลัง พร้อมเหตุผลรายรหัส ไม่เริ่มCh.8

ใช้ **E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter7-th.json** เป็นฐานบทถัดไป; stage staging/ThaiJP_ThroughChapter7_Working; config/map reference/chapter7-build.json / through-chapter7-cluster-map.json; QA qa/chapter7 รายละเอียด [CHAPTER7-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER7-STATUS.md)

ผู้ใช้เลือกThaiJP_Chapter6_7_P.zipแทนChapter6เดิม เพราะCORLEร่วมกัน Final5ZIPล่าสุดคือChapter1/Chapter2/Chapter3_4_5/Chapter6_7/Common ต้องใช้ร่วมกัน อีก3ZIPแรกคงเดิม อ่านกลับรวม24assetsผ่าน ไม่มีทับกัน สำรองของเก่านอกFinal ไม่ได้ติดตั้ง/เล่นทดสอบจริง/ฟังวิดีโอครบใหม่

build chain: assemble_chapter7.py → build_chapter7.py --text-only(เฉพาะglyphไม่เพิ่ม; หากเพิ่มbuildเต็ม) → build_chapter7.py --verify → audit_chapter7.py → audit_chapter7_glyph_regression.py → audit_gender_through_chapter7.py → audit_shared_dialogs.py → preview_chapter7.py(ดูภาพ) → publish_final_parts.py → finalize_chapter7.py ห้ามprepareซ้ำ/เปลี่ยนindex/ใช้auditบทเก่าทับactive context หลังแก้คำแปลตรวจและอัปเดตqa/chapter7/editorial-signoff.jsonซึ่งผูกhashก่อนfinalize

ตรวจ53system +4คำถามซิตอัปในchoice-review, UIหมวดCorel/ร้าน/ของเควสต์/เหมือง/ซิตอัปทั้งหมวด337รหัสรวมเดิมและบทเสริม Shared gateตอนนี้ตรวจ1,555UIต้นฉบับญี่ปุ่น NPCเช่าChocobo/ชุดว่ายน้ำ/ยิม60และช่างภาพ8ที่พักไว้เดิมเข้ามาแล้ว อย่านับว่ายังค้างทั้งหมดตามตัวเลขเก่าของCh.6

คำลงท้ายจริง609ครั้งใน594รหัส ชาย408/หญิง201 ไม่มีสลับเพศหรือผู้พูดคำลงท้ายไม่ยืนยัน UnknownNPCกลาง หลักฐานAminaเป็นสมาชิกหญิงอยู่ในJP และTerrified WomanมีJP ACTORระบุหญิง ใช้ชื่อไทยในบทพูด ป้ายUSอังกฤษ คงชื่อบาร์เร็ต/โกลด์ซอซเซอร์/โชโคโบะตามเดิม ชื่อใหม่JPคลาปิโย/ชีรอน/นาบาราไม่อ้างว่าPlearnรับรอง

คง677glyph assignment/metricsเดิม เพิ่ม10เป็น687 nativeASCII/เลข/ไอคอนคงเดิม …ยังระดับล่างครบ8fonts atlasไทยrepackBC5มีmaskต่างเล็กน้อย ไม่อ้างว่าไทยเดิมพิกเซลตรงทุกจุด

ทุกบทต้องตรวจทั้งคำถามและทุกตัวเลือกพร้อมข้อความResident/NPCไม่มีACTOR/namespaceข้างเคียง ยกเลิก ลองใหม่ ผลชนะแพ้ ร้าน ของเควสต์ ตามข้อกำหนดถาวรเดิม บทหลังCosmo Canyon/ทะเลทราย/โรงแรมปรับปรุง/ปฏิกิริยาสงครามแยกพร้อมเหตุผล ไม่เติมเรื่องCh.8ขึ้นไปโดยอ้างว่าCh.7ครบ
<!-- /chapter7-current -->

'''
    for p in [W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'CHAPTER6-STATUS.md',W/'CH1-6-RECHECK-STATUS.md']:
        t=p.read_text('utf-8');title,body=t.split('\n',1)
        if '<!-- chapter7-current -->' in body:
            i=body.index('<!-- chapter7-current -->');j=body.index('<!-- /chapter7-current -->')+len('<!-- /chapter7-current -->');body=body[:i]+body[j:]
        p.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    table='\n'.join(f"| {p['zip']} | {len(p['assets'])} | {p['bytes']:,} |" for p in release['parts'])
    (W/'FINAL-PARTS.md').write_text(f'''# ZIP ล่าสุดแยกแต่ละส่วน

18 ตุลาคม 2026 หลัง Ch.7: **26,951ข้อความ /24assets /687glyph clusters /5ZIP /15mod files**

| ZIP | assets | bytes |
| --- | ---: | ---: |
{table}

ใช้ทั้ง5ZIPร่วมกันจาก E:/FF7RebrithModTH/Mod/Final เก็บล่าสุดของแต่ละส่วนเท่านั้น ผู้ใช้เลือกChapter6_7แทนChapter6เพราะCORLEใช้ร่วมกัน อัปเดตCommonด้วย อีก3ZIPแรกคงเดิม สำรองนอกFinal อ่านกลับร่วม24assetsผ่านไม่มีทับกัน ไม่ได้ติดตั้ง/ทดสอบเล่นจริง ต้นฉบับ/dist/ม็อดในเกมไม่เปลี่ยน

รายละเอียด [CHAPTER7-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER7-STATUS.md) และ [HANDOFF.md](E:/FF7RebrithModTH/HANDOFF.md)
''','utf-8')
    print('Chapter7 release verified; five latest ZIPs; handoff/current docs updated.')
if __name__=='__main__':main()
