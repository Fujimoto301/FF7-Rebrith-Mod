# แก้คำตอบหน้าประตู Ch.4

<!-- chapter4-door-current -->
## ล่าสุด: แก้คำตอบเคาะประตู Ch.4 — 20 ตุลาคม 2026

ผู้ใช้ยืนยันให้แก้ภาพRedXIIIหน้าห้อง: เปลี่ยน **ถามสิ → เชิญ** ทั้ง2ID `$C2120_MAIN_2900_0100_00_red` และ `$C2120_MAIN_2700_0500_00_tif` ใน8200-JUNOE ต้นฉบับJPどうぞ, USRedYes?/TifaCome in. แม่แบบCh4#209เดิมreuseข้ามบริบท จึงเพิ่มper-IDoverrideในreference/chapter4-ui-overrides.jsonและแก้translations/chapter4/reused-lines.json+chapter4-th.json; assemble_chapter10.pyใช้overlay2IDท้ายการประกอบฐาน ห้ามรันassembleบทเก่าเพื่อทับฐานปัจจุบัน

ฐานยัง **translations/working-through-chapter10-th.json — 40,691ข้อความ / 27assets / 717clusters** คงอีก40,689ข้อความ/ACTORทั้งหมด/ทุกฟอนต์และอีก26assetsทุกไบต์ อัปเดตเฉพาะ **ThaiJP_Chapter3_4_5_P.zip** ใน E:/FF7RebrithModTH/Mod/Final อีก7ZIPhashเดิม อ่านกลับ8ZIP/24modfiles/27assetsผ่านไม่มีซ้ำ สำรองนอกFinal ไม่มีติดตั้งหรือทดสอบเกมจริง

หลักฐาน [CHAPTER4-DOOR-FIX.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER4-DOOR-FIX.md), qa/chapter4-door-fix/baseline.json+revisions/(ห้ามprepareซ้ำ), source-review.json(JP/USแยกID), audit.json, proof.png, release-verification.json; tools/chapter4_door_fix.py เก็บexceptionเฉพาะก่อนถามสิ/หลังเชิญ2ID ไม่ปล่อยให้แก้ฐานอื่นโดยพลการ gateCh10/recheck/continueยังทำงานและsignoffผูกhashoverlay/proofแล้ว ยอดเก็บตกเดิม144ไม่เปลี่ยน การแก้สะสมจาก40,547ตอนนี้61ข้อความที่มีอยู่เดิม(59รอบก่อน+2ประตู); ข้อความทุกIDยังครบ

ขั้นตอนต่อ: assemble_chapter10.py → build_chapter10.py --text-only → --verify → chapter10_recheck.py --quality → audit_shared_dialogs.py(รวมgateประตู) → audit_chapter10_glyphs.py → preview_chapter10.pyและchapter4_door_fix.py --preview/ดูproof → signoff_chapter10.py → publish_final_parts.py → chapter4_door_fix.py --finalize ไม่รันfinalize_chapter10_recheck/continueเดิมเพราะยังผูกbaselineก่อนแก้ประตู ข้อมูลยอด/คำว่าไม่แก้ฐานเก่าในบันทึกก่อนหน้านี้เป็นประวัติ ให้ใช้exception2IDนี้ต่อในบทถัดไป
<!-- /chapter4-door-current -->

