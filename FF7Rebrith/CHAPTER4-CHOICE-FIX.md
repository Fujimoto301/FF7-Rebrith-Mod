# แก้บริบทตัวเลือก Ch.4

<!-- chapter4-choice-current -->
## ล่าสุด: ทีฟ่าเข้ามาสิ + ตัวเลือกCh.4 — 20 ตุลาคม 2026

ตามภาพ/คำสั่งใหม่ ทีฟ่า `$C2120_MAIN_2700_0500_00_tif` ใช้ **เข้ามาสิ** แยกจากRedXIIIที่คง **เชิญ** แก้ตัวเลือกที่reuseคำว่า **ดู/ไม่ดู** ผิดบริบทครบ17ป้ายในJUNOE พร้อมป้ายเข้าร่วมพาเหรดที่มีtag1ป้ายและเกลาคำถามขึ้นด้านบน1ข้อความ รวมรอบนี้ **20ข้อความ** (ทีฟ่า1+ตัวเลือก18+คำถาม1) คำตอบขึ้นด้านบนเป็น **ขึ้นไป/ยังไม่ขึ้น**; กลุ่มลองใหม่/ฝึกพาเหรด/เข้าร่วมพาเหรด/FortCondor/ตามSalmon/เล่นJumpfrogใช้คำตอบให้ตรงกิจกรรม ครอบคลุม9กลุ่มคำถาม ตรวจภาพคำถามกับทุกปุ่ม3หน้าใช้glyphจริงแล้ว บทสอนคราฟต์Ch.2ยังใช้ดู/ไม่ดูถูกบริบทจึงคงไว้

ต้นเหตุคือCh4แม่แบบ364/365นำคำแปลはい/いいえจากบทสอนดูมาซ้ำ แก้generic defaultsเป็นใช่/ไม่ใช่ และper-IDoverrideแยกกิจกรรมในreference/chapter4-ui-overrides.json อัปเดตtranslations/chapter4-th.json+reused-lines.json+batch-03.json; tools/chapter4_choice_fix.py overlayท้ายassemble_chapter10.pyโดยอ้างsnapshotใหม่ qa/chapter4-choice-fix/baseline.json+revisions/ **ห้ามprepareซ้ำ/เปลี่ยนsnapshotเก่า** qa/chapter4-door-fixเดิมยังเป็นประวัติและgateประตูสะสมยอมเฉพาะ21IDที่reviewแล้ว(รอบก่อน2+รอบนี้20ซ้ำทีฟ่า1)

ฐานยัง **translations/working-through-chapter10-th.json — 40,691ข้อความ / 27assets / 717clusters** อีก40,671ข้อความและACTORทั้งหมดคงเดิม ทุกฟอนต์/อีก26assetsไบต์เดิม อัปเดตเฉพาะ **ThaiJP_Chapter3_4_5_P.zip** ใน E:/FF7RebrithModTH/Mod/Final อีก7ZIPhashเดิม อ่านกลับ8ZIP/24modfiles/27assetsผ่าน ไม่มีติดตั้ง/ทดลองตัวเลือกจริงในเกม

หลักฐาน [CHAPTER4-CHOICE-FIX.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER4-CHOICE-FIX.md), qa/chapter4-choice-fix/source-review.json(JP/USก่อนหลัง20ID), audit.json, proof-1.pngถึงproof-3.png, release-verification.json SignoffCh10ผูกhashใหม่ทุกไฟล์แล้ว ขั้นตอน: assemble_chapter10 → build_chapter10 --text-only/--verify → chapter10_recheck --quality → audit_shared_dialogs → audit_chapter10_glyphs → preview_chapter10 + chapter4_door_fix --preview + chapter4_choice_fix --preview/ดูภาพ → signoff_chapter10 → publish_final_parts → chapter4_choice_fix --finalize ไม่ใช้finalizeประวัติบทเก่าทับcontextใหม่ เมื่อมีการติดตั้งโดยผู้ใช้ก่อนเริ่มรอบ ให้ใช้protectedmanifestของsnapshotรอบล่าสุด คงdist/ต้นฉบับ/เกมที่ติดตั้งปัจจุบันระหว่างทำงาน
<!-- /chapter4-choice-current -->

