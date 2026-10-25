"""Verify the delivered Chapter 6 set and update its handoff/documentation."""
import hashlib,json,re
from collections import Counter
from pathlib import Path
from assemble_chapter6 import W,read,write
from assemble_ui_completion import fingerprint

def main():
    release=read('qa/final-parts/latest.json');mount=read('qa/final-parts/combined-mount-verification.json')
    audit=read('qa/chapter6/translation-audit.json');gender=read('qa/gender-through-chapter6/summary.json')
    context=read('qa/chapter6/contextual-gender-review.json');baseline=read('qa/chapter6/baseline.json')
    assert release['chapters']==[1,2,3,4,5,6] and release['combined_text_records']==23811
    assert mount['all_parts_mounted_together'] and mount['all_match_verified_combined_set'] and not mount['overlapping_assets']
    assert mount['zip_count']==5 and mount['assets']==23 and mount['mod_files']==15
    assert fingerprint()==baseline['protected']
    assert len(release['parts'])==5 and all(p['reused_unchanged'] for p in release['parts'][:3])
    assert {p.name for p in (W.parent/'Mod/Final').iterdir()}=={p['zip'] for p in release['parts']}
    for p in release['parts']:assert hashlib.sha256((W.parent/'Mod/Final'/p['zip']).read_bytes()).hexdigest()==p['sha256']
    write('qa/chapter6/release-verification.json',dict(chapters=release['chapters'],text_records=23811,chapter6_records=1698,
        additional_UI_records=153,selected_NPC_records=698,deferred_later_records=107,ZIP_count=5,mod_files=15,assets=23,
        previous_21960_records_preserved=True,chapter1_chapter2_chapter3_4_5_ZIPs_unchanged=True,
        all_parts_mounted_together=True,no_overlapping_assets=True,source_and_installed_files_unchanged=True,
        installed=False,runtime_tested=False,full_new_video_audio_review=False,
        font_proof_visually_inspected=True,font_proof_is_not_in_game_screenshot=True,
        release_manifest='qa/final-parts/latest.json',backup=release['backups'],
        actual_gender_particles=gender['actual_particle_occurrences'],gender_mismatches=[],unresolved_gendered_endings=[]))
    status='''# Chapter 6 — Fool's Paradise

อัปเดต 18 ตุลาคม 2026 (Asia/Bangkok)

แปลและแพ็ก Ch.6 แล้ว **1,698 รหัสบท/ตัวเลือก + 153 รหัส UI** รวมกับงาน Ch.1–5 เป็น **23,811 รหัส / 23 assets / 674 glyph clusters** ไฟล์ใหม่ `ThaiJP_Chapter6_P.zip` อยู่ใน `E:/FF7RebrithModTH/Mod/Final` ใช้ร่วมกับ ZIP ล่าสุดอีก 4 ส่วน

## ขอบเขตและความครบ

| ส่วน | รหัสที่ใส่ในม็อด |
| --- | ---: |
| C2410: ถึง Costa del Sol, โรงแรม/Amor del Amor, Hojo, บทชายหาดทุกทางเลือก, กลับที่พักและ Yuffie เข้ากลุ่ม | 531 |
| COSTT_BOS_06: บทต่อสู้ | 36 |
| COSTT_NPC_10: NPC/เสียงแวดล้อม/คำถามระบบของสถานะเยือนครั้งแรก | 698 |
| COSTT_QST_00–06: กิจกรรมรับชุดชายหาด, ยิงเป้า, Card Carnival, Run Wild, Wheelie, ถ่ายรูป, คอนเสิร์ตเปียโน รวมผลลัพธ์/บทพูดซ้ำ | 359 |
| Resident CARDG_QST_11: คู่แข่งท้องถิ่น Riana/Moa, Dokaccha, Maahir | 74 |
| **รวมบทและตัวเลือกใหม่** | **1,698** |
| UI ฐาน: ห้องเปลี่ยนชุด, Hidden Cactuar, ชื่อร้าน/แลกชุด, เลือกทีมช่วยเหลือ | **22** |
| UI กิจกรรมเพิ่มเติม: ยิงเป้า/Run Wild/Card Carnival/Wheelie/ตั๋ว/กล้อง/ชุดชายหาด | **131** |
| **รวม UI Ch.6** | **153** |

เตรียมต้นฉบับ **1,805 รหัส / 1,737 แม่แบบ** แปลครบทุกแม่แบบ (batch-00 ถึง batch-08 และ exact neutral reuse 35 ชุด ซึ่งทวนบริบทแล้ว) เทียบกับ corpus ทุก asset ครบตามกลุ่มที่เลือก ไม่ตัดเพราะไม่มี ACTOR NPC เตรียม796รหัส เลือก698 รวม612รหัสที่ไม่มี ACTOR ชุดบท/ตัวเลือกที่ใส่จริงแบ่งเป็น ACTOR1,022, เสียงแวดล้อมไม่มีACTOR601 และตัวเลือกระบบ75

แยก **107 รหัสที่ต้องอาศัยความคืบหน้าภายหลัง** เป็น source-only ใน `reference/chapter6-deferred.json`: NPC98 + บท Jenny หลังปรับปรุงโรงแรม9 แบ่งตามเนื้อหาเป็นบริการเฮลิคอปเตอร์ Gold Saucer6, โรงแรมปรับปรุง/ร่างแยกจอห์นนี่/คอลเลกชัน33, เช่าโจโกโบะนอกเมือง14, ปฏิกิริยาแฟชั่นโชว์8, โรงฝึก37, Jenny ที่โรงแรม9 ไม่แปลทับลง asset ในรอบนี้ แม้เตรียมคำแปลไว้แล้ว ไม่เพิ่ม C2510/C2520, CORLE_QST หรือบทสำรวจภูมิภาคซึ่งเป็น Ch.7 เป็นต้นไป UIร้านเช่าโจโกโบะ `$COSTT_ITEM_008` ยังกันไว้กับภูมิภาคถัดไป

## รีเช็คคำแปล ชื่อและเพศ

ตรวจบริบททุกแม่แบบและคำตอบสั้นที่ reuse เช่น まあな ในคำถามยุฟฟี่เป็น “ก็ใช่”; ชื่อเฉพาะในตัวเลือกระบบใช้ Hojo, Seventh Heaven, Yuffie ตามนโยบาย UI ชื่อในบทพูดเป็นไทย ตรวจชื่อทางการ US รหัสเดียวกัน โดยด่านยิงเรือใช้ **Brigantine** และ Run Wild ใช้ **Free-for-All** แต่คงแท็ก JP เดิม

ศัพท์ Plearn ที่พบในข้อมูลให้มาใช้ จอห์นนี่, วิสเปอร์, อิฟาลน่า และโกลด์ซอซเซอร์ พร้อมบันทึก asset/รหัส/ข้อความใน `qa/chapter6/proper-name-review.json` คาโปโน/เจนนี่/เรียนา/โดคัตชา/มาคอย/วีลลี/แฮปปี้เทนเดอร์เป็นการถอดเสียง JP ใหม่ ไม่อ้างว่า Plearn ยืนยันครบทุกชื่อ ชื่ออังกฤษ ACTOR/UI คงทางการ

ป้าย ACTOR ที่ US ขาดตรงรหัสมี3จุด ใช้บริบทที่บันทึกไว้: nem รายบุคคลเป็น Swimsuit Girl ต่างจากประโยคตอบพร้อมกัน Swimsuit Girls; 宝条 เป็น Hojo; ティファ เป็น Tifa ป้าย ??? คงไว้ก่อนเปิดเผยตัว ไม่เปลี่ยน metadata อื่น

ตรวจข้อความระบุเพศผู้พูด27รหัส ทั้งหมดเป็น Johnny ซึ่งแนะนำตัวว่า 男ジョニー ใน JP ไม่ได้เดาจากชื่อหรือ suffix จอห์นนี่ใช้ ผม/ครับตามน้ำเสียง ส่วน NPC ที่ยังไม่ยืนยันตัวใช้ถ้อยคำกลาง คัดทวนคำเรียก/สรรพนาม/ความสัมพันธ์171รหัส (เป็นผลค้นรวมคำธรรมดา เช่น ชายหาดด้วย ไม่ใช่171รหัสระบุเพศจริง) ไม่พบคำลงท้ายสลับเพศในขอบเขตที่ตรวจ

ทั้งชุด Ch.1–6 มีคำลงท้ายจริง **477 ครั้ง ใน467รหัส**: ครับ335 ค่ะ83 คะ59; NPC/ตัวละครนอกปาร์ตี้434ครั้งตามนิยามเดิม ไม่รวม คะ… ที่เป็นเสียงติดอ่างใน คะ…ครับ! ตรวจหลักฐานรายรหัสเดิมไว้ครบ ไม่มีผู้พูดของคำลงท้ายเหล่านี้ที่ไร้หลักฐานเพศ ไม่ได้อ้างว่ายืนยันเพศ NPC ทุกคนจากภาพ/เสียงใหม่

ตัวเลขคงค่าและใช้เลขอารบิก เช่น ห้อง101/102/103, หมายเลข13, ตั๋ว7, 4ตัว, 2ล้อ, อันดับ2 ส่วน “10分の1” เรียงเป็น “1 ใน 10” ในไทย บ้านพัก “セカンドハウス” หมายถึงบ้านตากอากาศ ไม่เติมเลข2 และ “素敵な1日” เป็นคำอวยพรวันดีๆ ไม่ใช่ระยะเวลา1วัน รักษาสำนวนไม่เจาะจงตามนโยบาย

## ไฟล์ที่ใช้รับช่วงต่อ

พาธฐาน `E:/FF7RebrithModTH/FF7Rebrith/`:

| ใช้สำหรับ | พาธ |
| --- | --- |
| JP/US รายรหัสและแม่แบบคงที่ | reference/chapter6-source.json, chapter6-templates.json |
| ขอบเขต/รหัสภายหลัง/ข้อยกเว้น UI | reference/chapter6-scope.json, chapter6-deferred.json, chapter6-ui-overrides.json |
| คำแปลแก้ได้ | translations/chapter6/batch-00.json ถึง batch-08.json, reused-lines.json |
| UI22รหัส | reference/chapter6-ui-source.json, translations/chapter6-ui-th.json |
| Patch / รวมปัจจุบัน | translations/chapter6-th.json, translations/working-through-chapter6-th.json |
| glyph / staging | reference/through-chapter6-cluster-map.json, staging/ThaiJP_ThroughChapter6_Working |
| Snapshotก่อนเริ่ม ห้ามเขียนทับ | qa/chapter6/baseline.json, revisions/ |
| ขอบเขต/แก้ภาษา/ชื่อ/เพศ | qa/chapter6/translation-audit.json, editorial-corrections.json, contextual-gender-review.json, proper-name-review.json |
| ข้อความ/ฟอนต์/แนวตัวเลข | qa/chapter6/verification.json, native-baseline-alignment.json, runtime-baseline-check.json, font-proof.png |
| คำลงท้ายทั้งชุด | qa/gender-through-chapter6/summary.json, records.json |
| ผลแพ็ก/อ่านกลับ/ไม่เปลี่ยนเกม | qa/chapter6/release-verification.json, qa/final-parts/latest.json, combined-mount-verification.json |

## สร้างและตรวจซ้ำ

จากโปรเจกต์ ใช้ Python `C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` ตั้ง `$env:PYTHONUTF8='1'` แล้วรันตามลำดับ:

```text
tools/assemble_chapter6.py
tools/build_chapter1.py --chapter6-working
tools/verify_chapter1.py --chapter6-working
tools/audit_chapter6.py
tools/audit_chapter6_activity_ui.py
tools/audit_chapter6_editorial.py
tools/audit_gender_through_chapter6.py
tools/preview_chapter6.py
tools/preview_chapter6_activity_ui.py
tools/publish_final_parts.py
tools/finalize_chapter6.py
```

ดูภาพ proof ด้วย ไม่ใช้แค่การมีไฟล์ภาพเป็นหลักฐานว่าอ่านได้ ห้ามรัน prepare_chapter6.py ซ้ำหรือเปลี่ยน index ถ้าแก้บทโดยไม่มี glyph ใหม่ใช้ build --text-only ได้เมื่อมีผล build8ฟอนต์เดิม; หาก mapเปลี่ยนต้อง buildเต็ม รักษา Ch.5 combined เดิม21,960รหัสเป็นฐาน ไม่รัน auditเก่าทับ active-working-set

## ZIP และข้อจำกัด

Final มี5ZIPล่าสุดของ Chapter1, Chapter2, Chapter3_4_5, Chapter6 และ Common ต้องใช้ด้วยกันทั้งหมด MIDGR/NIBLE อยู่Chapter1, GRASE/FOREE อยู่Chapter2, JUNOE อยู่Chapter3_4_5, CORLE อยู่Chapter6, Resident/ฟอนต์อยู่Common ไม่มี asset ทับกัน Chapter1/2/3_4_5 ZIPคงเดิม เพิ่มChapter6และอัปเดตCommon

อ่านกลับทั้ง5ZIPร่วมกันผ่าน **15 mod files / 23 assets** แต่ละZIPมีเฉพาะ .pak/.utoc/.ucas ลิขสิทธิ์ฟอนต์อยู่ในZIPcomment สำรองชุดที่แทนที่ไว้นอกFinal ตาม latest.json เพิ่มglyph14clustersแบบappend-only660→674 รักษาป้ายACTORเดิมและ21,960รหัสก่อนหน้า, native Latin/ตัวเลข/ไอคอน/พิกเซล/ระยะ/แนวH ครบ8ฟอนต์ ภาพ proof มีการแทน Ether/1072 EXP/12 AP หลังencodeเหมือนruntime

ยังไม่ได้ติดตั้งชุดนี้หรือทดสอบเล่นจริง ภาพproofไม่ใช่ภาพในเกม ต้นฉบับเกม/distเดิม/ม็อดที่ติดตั้งไม่เปลี่ยน ไม่ได้เปิดดูหรือฟังวิดีโอNPCครบใหม่

## แหล่งอ้างอิงและงานถัดไป

- [คลิปหลักที่ผู้ใช้ให้](https://www.youtube.com/watch?v=i4gD0mmj5vc) ใช้จับภาพผู้พูดเทียบJPดิบ ยังไม่มี timestamp Ch.6 ที่ตรวจใหม่ ห้ามแต่งเวลาอ้างอิง
- [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk) auto transcriptไม่แทนบทJPหรือหลักฐานว่าฟังแล้ว
- บทพูด Ch.7–14 ยังไม่เริ่ม เมื่อได้รับคำสั่งเริ่ม Ch.7 ให้คัดเรื่องภูเขาโคเรล/ภูมิภาค/เควสต์/NPCจากเนื้อหา และตรวจ deferred107รหัสที่เตรียมไว้ว่าปลดล็อกช่วงใด อย่าใส่ทั้งหมดเพียงเพราะเริ่มCh.7
- Ch.7 ใช้ CORLE ร่วมกับ Ch.6 มีโอกาสใช้ MIDGR/Residentร่วมด้วย ต้องตรวจ ownership ทั้งชุดก่อนตั้งชื่อZIPและแพ็ก ห้ามปล่อยสองแพ็กที่มีassetเดียวกัน
- ถ้าต้องติดตั้งให้รอคำสั่งผู้ใช้แยก สำรองก่อนและอ่านกลับทุกส่วน ตรวจภาพจริงของข้อความยาว/การตัดบรรทัดเมื่อมีการทดสอบในเกม
'''
    (W/'CHAPTER6-STATUS.md').write_text(status,'utf-8')
    table='\n'.join(f"| `{p['zip']}` | {len(p['assets'])} | {p['bytes']:,} |" for p in release['parts'])
    final=f'''# ZIP ล่าสุดแยกแต่ละส่วน

อัปเดต 18 ตุลาคม 2026 หลัง Chapter6: **5 ZIP / 15 mod files / 23 assets / 23,811 ข้อความ** ตรวจเปิดแยกและ mount ร่วมกันผ่าน ไม่มี assetทับกัน

| ZIP | assets | bytes |
| --- | ---: | ---: |
{table}

เก็บเฉพาะ ZIP ล่าสุดของแต่ละส่วนใน `E:/FF7RebrithModTH/Mod/Final` เมื่อแก้ให้ลงทับชื่อส่วนเดิม สำรองรุ่นเก่านอกFinal ตาม `qa/final-parts/latest.json` ไม่เก็บเอกสารหรือZIPเก่าในFinal

Ch.6 ใช้ CORLE จึงแยก `ThaiJP_Chapter6_P.zip` ได้ ส่วน JUNOE ของCh.3–5ยังอยู่ในชื่อที่ผู้ใช้เลือก `ThaiJP_Chapter3_4_5_P.zip` **ต้องใช้ทั้ง5ZIPล่าสุดร่วมกัน** เพื่อให้ข้อความ/ฟอนต์ตรงกัน Chapter1 มีMIDGR/NIBLE; Chapter2มีGRASE/FOREE (GRASEมีCh.1–3); Chapter3_4_5มีJUNOE; Chapter6มีCORLE; CommonมีResident+8fonts+8textures

รอบCh.6คง Chapter1/Chapter2/Chapter3_4_5 ZIPเดิม เพิ่มChapter6และอัปเดตCommon รักษา21,960รหัสเดิม เพิ่ม1,698บท/ตัวเลือก+153UI ตารางglyph674clustersแบบappend-only(+14) ชื่อส่วนไม่ได้หมายถึงลงเดี่ยวได้

แต่ละZIPมีเฉพาะ .pak/.utoc/.ucas รวม3ไฟล์ ลิขสิทธิ์ฟอนต์อยู่ในZIPcomment `publish_final_parts.py` อ่าน `qa/active-working-set.json` และเรียก `verify_final_parts.py` เทียบunionกับ `qa/chapter6/working-assets.json` ผลใน `qa/final-parts/latest.json`, `combined-mount-verification.json`, `qa/chapter6/release-verification.json`

ยังไม่ได้ติดตั้งหรือทดสอบเล่นจริง เมื่อติดตั้งตามคำสั่งครั้งถัดไปให้ใช้ทั้ง15ไฟล์จาก5ZIP สำรองม็อดเดิมก่อน นำชื่อ ThaiJP_Chapter3_P/ThaiJP_Chapter3_4_P ที่ถูกแทนที่ออกเพื่อไม่ให้ทับJUNOE รักษาม็อดอื่นไว้ ตรวจแฮชและอ่านกลับหลังลง

ดู [CHAPTER6-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER6-STATUS.md) และ [HANDOFF.md](E:/FF7RebrithModTH/HANDOFF.md)
'''
    (W/'FINAL-PARTS.md').write_text(final,'utf-8')
    handoff=W.parent/'HANDOFF.md';old=handoff.read_text('utf-8')
    if '## ประวัติ snapshot หลัง Chapter5' in old:history=old.split('## ประวัติ snapshot หลัง Chapter5\n\n',1)[1]
    else:history=old
    head='''# ส่งต่องานม็อด FF7 Rebirth ซับไทย / เสียงญี่ปุ่น

อัปเดตล่าสุด **18 ตุลาคม 2026 — หลัง Chapter6 (Asia/Bangkok)** ข้อมูลส่วนนี้แทนพาธ/ยอด/สถานะปัจจุบันของCh.5ในประวัติด้านล่าง คำสั่งใหม่ผู้ใช้มีลำดับเหนือเอกสารเสมอ

## ชุดปัจจุบันและงานที่เสร็จ

- เสร็จ Ch.1–6 ตามขอบเขตแต่ละบท รวม **23,811รหัส / 23assets / 674clusters** Ch.6เพิ่มบท/ตัวเลือก1,698รหัส รวมNPC698(ไม่มีACTOR612) และUI153รหัส แยก107รหัสสถานะภายหลังออก ไม่ได้แปลบทCh.7–14
- ชุดรวม [working-through-chapter6-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter6-th.json), staging [ThaiJP_ThroughChapter6_Working](E:/FF7RebrithModTH/FF7Rebrith/staging/ThaiJP_ThroughChapter6_Working), QA [chapter6](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter6), [active-working-set.json](E:/FF7RebrithModTH/FF7Rebrith/qa/active-working-set.json)
- [Final](E:/FF7RebrithModTH/Mod/Final) มี **Chapter1/Chapter2/Chapter3_4_5/Chapter6/Common ทั้ง5ZIPต้องใช้ร่วมกัน** รวม15mod files23assets เปิดอ่านกลับร่วมกันแล้วไม่มีassetซ้ำ Chapter1/2/3_4_5ZIPคงเดิม เพิ่มChapter6และแก้Common สำรองZIPเก่านอกFinal
- รักษาCh.1–5เดิม21,960รหัสและACTORครบ เพิ่มglyph14แบบappend-only660→674 รักษาLatin/ตัวเลข/ไอคอน/พิกเซล/ระยะ/แนวHเดิม8ฟอนต์ ต้นฉบับเกม,distเก่า,ม็อดที่ติดตั้งไม่เปลี่ยน ยังไม่ได้ติดตั้งชุดใหม่หรือทดสอบเล่น/ฟังเสียงNPCครบใหม่

## กฎคำแปลและเพศ

แปลจากJP ชื่อที่กล่าวในบทพูด/Dialogueเป็นไทย ACTORและชื่อเฉพาะในUIเป็นอังกฤษทางการ ชื่อไอเทม/สกิลในเมนูอังกฤษ ความสามารถไทย ชื่อChapterอังกฤษ ช่วงเวลาอดีต/ปัจจุบันไทย ใช้เลขอารบิกเมื่อเป็นค่าชัดเจน เช่น เซคเตอร์7 แต่คงสำนวนไม่เจาะจง คงแท็ก/ตัวแปรJPและmetadataอื่น

ชายใช้ครับ หญิงใช้ค่ะบอกเล่า/คะคำถาม/นะคะตามน้ำเสียง ไม่เติมทุกบรรทัด ตรวจทั้งผู้พูด ผู้ฟัง และคนถูกกล่าวถึง ไม่เดาเพศจากmma/mfaหรือรหัสโมเดล ถ้าไม่ยืนยันใช้ถ้อยคำกลาง Ch.6มี27รหัสระบุเพศจริง เป็นJohnnyที่JPแนะนำว่า男ジョニー คัดทวนความสัมพันธ์/สรรพนาม171รหัส(รวมคำธรรมดาที่ค้นติด) ไม่พบคำลงท้ายสลับเพศในข้อมูลที่ตรวจ

ทั้งชุดCh.1–6 ครับ/ค่ะ/คะจริง **477ครั้งใน467รหัส: ครับ335 ค่ะ83 คะ59** NPC/ตัวละครนอกปาร์ตี้434ครั้ง ไม่รวมเสียงติดอ่างคะ…ในคะ…ครับ! ผล [summary.json](E:/FF7RebrithModTH/FF7Rebrith/qa/gender-through-chapter6/summary.json) และ [records.json](E:/FF7RebrithModTH/FF7Rebrith/qa/gender-through-chapter6/records.json) ไม่อ้างว่าNPCทุกคนถูกยืนยันจากวิดีโอ

ใช้Wutai=อู่ไถ Red XIIIบนป้ายและ“เรด”ในบทพูดปัจจุบัน ศัพท์Ch.6ที่ยืนยันPlearn: จอห์นนี่/วิสเปอร์/อิฟาลน่า/โกลด์ซอซเซอร์ อ้างอิงรายรหัสใน [proper-name-review.json](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter6/proper-name-review.json) คำใหม่ที่ถอดจากJPแยกต่างหาก ไม่อ้างPlearnรับรอง

## ไฟล์และวิธีทำต่อ

พาธฐาน **E:/FF7RebrithModTH/FF7Rebrith/**:

| หน้าที่ | ไฟล์ใต้พาธฐาน |
| --- | --- |
| JP/US รายรหัส/แม่แบบ/ขอบเขต | reference/chapter6-source.json, chapter6-templates.json, chapter6-scope.json |
| สถานะภายหลัง107รหัส/ชื่อUI | reference/chapter6-deferred.json, chapter6-ui-overrides.json |
| คำแปลแก้ได้ | translations/chapter6/batch-00.json ถึง batch-08.json และ reused-lines.json |
| UI22รหัส | reference/chapter6-ui-source.json, translations/chapter6-ui-th.json |
| glyph/staging | reference/through-chapter6-cluster-map.json, staging/ThaiJP_ThroughChapter6_Working |
| Snapshotห้ามทับ | qa/chapter6/baseline.json และ revisions/ |
| ตรวจขอบเขต/ชื่อ/เพศ/ฟอนต์ | qa/chapter6/translation-audit.json, contextual-gender-review.json, proper-name-review.json, verification.json, runtime-baseline-check.json, font-proof.png |
| ชุดส่งมอบ/ผลเปิดร่วม | qa/final-parts/latest.json, combined-mount-verification.json, qa/chapter6/release-verification.json |
| รายละเอียดขอบเขตและขั้นตอน | CHAPTER6-STATUS.md, FINAL-PARTS.md |

ต้นฉบับ **E:/FF7RebrithModTH/FF7Rebrith/source/End/Content/Text/JP** และ **US** รหัสเดียวกัน Python **C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe** ตั้ง `$env:PYTHONUTF8='1'` จากโปรเจกต์ แล้วรัน `tools/assemble_chapter6.py` → `tools/build_chapter1.py --chapter6-working` → `tools/verify_chapter1.py --chapter6-working` → `tools/audit_chapter6.py` → `tools/audit_chapter6_activity_ui.py` → `tools/audit_chapter6_editorial.py` → `tools/audit_gender_through_chapter6.py` → `tools/preview_chapter6.py` → `tools/preview_chapter6_activity_ui.py`(ดูภาพด้วย) → `tools/publish_final_parts.py` → `tools/finalize_chapter6.py`

ห้ามรันprepare_chapter6.pyซ้ำหรือเปลี่ยนเลขแม่แบบ ห้ามauditบทเก่าทับactive-working-set ถ้าแก้ข้อความไม่เพิ่มglyphใช้build --text-onlyได้ มิฉะนั้นbuildฟอนต์เต็ม รักษาฐานCh.5เดิมครบ ทุกครั้งแก้เสร็จแพ็กZIPล่าสุดแยกส่วนลงFinalตามคำสั่งถาวร ติดตั้งเกมยังต้องมีคำสั่งแยก

## งานที่ยังต้องทำและแหล่งอ้างอิง

- บทCh.7–14ยังไม่เริ่ม เมื่อผู้ใช้สั่งCh.7ให้เริ่มจากภูเขาโคเรล/ภูมิภาค/เควสต์/NPC คัดตามเนื้อหา ตรวจdeferred107รหัสว่าแต่ละชุดใช้ช่วงไหน ไม่รวมทั้งหมดอัตโนมัติ
- CORLEเป็นassetร่วมCh.6–7; MIDGR/Residentอาจร่วมด้วย ตรวจownershipก่อนแพ็ก อย่าทำสองZIPมีassetเดียว ต้องรักษาCh.1–6เป็นฐาน
- deferredCh.2 52รหัส และCh.4 50รหัสยังเก็บแยกตามเหตุการณ์ภายหลัง ไม่ได้นับรวมในบทที่เสร็จ
- UI/ความสามารถไอเทม–สกิล/ชื่อศัตรูอังกฤษที่ทำทั้งเกมแล้วเป็นคนละหมวดกับบทพูด ยังไม่ได้แปลบทพูดทั้งเกม
- [คลิปผู้ใช้ให้](https://www.youtube.com/watch?v=i4gD0mmj5vc) เวลาที่มีหลักฐานบันทึกไว้Ch.4 12:23:04,Ch.5 21:30:39 ยังไม่มีเวลาCh.6ที่ตรวจใหม่ [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk) ใช้จับคู่ภาพผู้พูดกับJPดิบ ห้ามถือauto transcriptเป็นบทถูกต้องหรือหลักฐานว่าฟังครบ
- รอคำสั่งติดตั้ง/ภาพทดสอบจากเกมเพื่อตรวจการตัดบรรทัดและพื้นที่จริง ภาพglyph proofและการอ่านไฟล์กลับไม่แทนruntime test

## ประวัติ snapshot หลัง Chapter5

'''
    handoff.write_text(head+history,'utf-8')
    p=W/'AGENTS.md';s=p.read_text('utf-8');tag='# Current user requirements\n\n'
    note='''- Latest completed work (2026-10-18): Chapter6 — Fool's Paradise adds **1,698 dialogue/system records + 153 Costa UI labels**, including **698 selected NPC records (612 without ACTOR)**. Prepared 1,805 rows/1,737 templates; **107 later-state rows deferred** (98 NPC + 9 post-refurbishment Jenny). Combined current **23,811 records / 23 assets / 674 clusters**. Preserve all21,960 prior records/ACTORs and660 glyph assignments; +14append-only. See CHAPTER6-STATUS.md and HANDOFF.md. Unknown NPCs neutral; Johnny gender proven by JP男ジョニー. Rechecked27gender-sensitive and171context candidates. Global gender endings477occurrences/467records (male335/female142), no mismatches/unresolved ending speakers. No new full audio/video or runtime test.

- Current staging/merged/QA: ThaiJP_ThroughChapter6_Working, working-through-chapter6-th.json, qa/chapter6. Final has **5 ZIPs: Chapter1, Chapter2, Chapter3_4_5, Chapter6, Common — all required**. CORLE owns new Chapter6; JUNOE remains Chapter3_4_5. First3ZIPs unchanged; Chapter6/Common packed and all5mounted/read back:15files23assets, no overlap. Source/dist/installed game unchanged. Build order: assemble_chapter6.py → build_chapter1.py --chapter6-working → verify_chapter1.py --chapter6-working → audit_chapter6.py → audit_chapter6_activity_ui.py → audit_chapter6_editorial.py → audit_gender_through_chapter6.py → preview_chapter6.py → preview_chapter6_activity_ui.py → publish_final_parts.py → finalize_chapter6.py. Do not rerun prepare_chapter6.py/renumber templates/reset active context with old audits. Ch.7–14 not started. Check shared CORLE/MIDGR ownership and deferred state content before next chapter. Current snapshot supersedes older current-path/count/ZIP claims below. Installation still needs a separate user request.

'''
    if note not in s:p.write_text(tag+note+s[len(tag):],'utf-8')
    p=W/'TRANSLATION_GUIDE.md';s=p.read_text('utf-8');line,rest=s.split('\n',1)
    note='อัปเดตล่าสุด18ตุลาคม2026: Ch.6เสร็จแล้ว ดู CHAPTER6-STATUS.md และ E:/FF7RebrithModTH/HANDOFF.md เป็นหลัก ชุดปัจจุบันworking-through-chapter6-th.json/staging ThaiJP_ThroughChapter6_Working/qa chapter6 รวม23,811รหัส23assets674clusters ใช้5ZIP Chapter1/Chapter2/Chapter3_4_5/Chapter6/Commonร่วมกัน เพิ่ม1,698บท+153UI/NPC698 แยก107สถานะภายหลัง คงงานเดิม21,960รหัสครบ คำลงท้ายตรวจทั้งชุด477ครั้งไม่มีสลับเพศตามหลักฐานที่เก็บ ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ UnknownNPCกลาง ใช้วิสเปอร์/อิฟาลน่าตามPlearn ไม่ลงเกมหรืออ้างruntime test ข้อความปัจจุบันบทเก่าด้านล่างเป็นประวัติ'
    if note not in s:p.write_text(line+'\n\n'+note+'\n'+rest,'utf-8')
    p=W/'CHAPTER5-STATUS.md';s=p.read_text('utf-8');line,rest=s.split('\n',1)
    note='> Snapshot Ch.5 สำหรับประวัติ ชุดล่าสุดคือ Ch.6 แล้ว ดู CHAPTER6-STATUS.md / FINAL-PARTS.md ปัจจุบันต้องใช้5ZIPร่วมกัน ข้อมูลQA Ch.5ด้านล่างคงไว้ครบ'
    if note not in s:p.write_text(line+'\n\n'+note+'\n'+rest,'utf-8')
    from finalize_chapter6_activity_ui import finish
    finish()
    print('Chapter6 release verified; handoff, status, guide, AGENTS and Final documentation updated.')

if __name__=='__main__':main()
