# ตรวจต่อ Ch.10

<!-- chapter10-continue-current -->
## ล่าสุด: ตรวจความหมาย Ch.10 ต่อ — 20 ตุลาคม 2026

รอบต่อเนื่องนี้แก้ **18ข้อความที่มีอยู่แล้ว ไม่มีเพิ่ม/ลบID**: บทพูดอารมณ์/ประโยคเชื่อมของเอริธ, ตำนานที่แชดลี่ย์เล่า, ความอึดสู้ของบาร์เร็ต, ทิศทางเปรียบเทียบบาฮามุท, ช่องว่างชิปเอไอ, คอสตาเดลโซล, ลางบอกภัยพิบัติ และใช้ **โจโกโบะบิน** ให้ตรงบทสอนเดิมทั้งบทคุยกับข้อความช่วยเดินทาง คง **40,691ข้อความ / 27assets / 717clusters** ทุกID/ACTOR/glyph-mapเดิมครบ คำลงท้าย1,278ครั้ง(ครับ874/ค่ะ255/คะ149)ไม่เปลี่ยน ไม่เริ่มCh.11

อัปเดตเฉพาะ **ThaiJP_Chapter10_P.zip และ ThaiJP_Common_P.zip** ใน E:/FF7RebrithModTH/Mod/Final อีก6ZIPhashเดิม อ่านกลับ8ZIPรวม24modfiles/27assetsผ่านไม่มีซ้ำ ดูproofglyphจริง7หน้า56ตัวอย่างที่ครอบคลุม18ข้อความแก้และคำถาม/ทุกปุ่ม4ชุดแล้ว การตัดบรรทัดในproofเป็นตัวอย่าง ไม่ใช่ภาพเกม **ยังไม่ได้ติดตั้งหรือทดลองทุกแขนงในเกม/ฟังเสียงครบใหม่** จึงไม่รับรองว่าความหมายหรือruntimeไม่มีข้อผิดพลาด100%

หลักฐานใหม่: tools/chapter10_continue_review.py (prepareครั้งเดียว ห้ามซ้ำ), qa/chapter10/continue-review/current.json+revisions/ (ฐาน40,691ก่อนแก้), review.json (before/after18รหัส), release-verification.json และ [CHAPTER10-CONTINUE-REVIEW.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER10-CONTINUE-REVIEW.md) ใช้ฐาน translations/working-through-chapter10-th.json และขั้นตอนbuild/audit/signoff/publishเดิม เพิ่ม gateต่อเนื่องอัตโนมัติในaudit_chapter10_recheck.py; signoffผูกhashรายงานใหม่ไว้แล้ว ปิดเอกสารด้วย finalize_chapter10_recheck.py แล้ว finalize_chapter10_continue.py

ยอดด้านล่าง **เพิ่ม144/แก้59** เทียบกับCh.10ชุดแรก40,547: 59คือข้อความที่มีอยู่ในชุดแรก ส่วนรอบต่อเนื่อง18ประกอบด้วย16ข้อความจากชุดแรกและ2ข้อความจาก144ที่เก็บตก ห้ามนับ18เป็นจำนวนข้อความเพิ่ม ฐานก่อนCh.10ทั้ง37,830ยังคงเดิม
<!-- /chapter10-continue-current -->

## รายการแก้

before/afterฉบับเต็มพร้อมJP/USอยู่ที่ [review.json](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter10/continue-review/review.json)

| แม่แบบ | ID | เหตุผล |
| --- | --- | --- |
| 2489 | $WORLD_CDV_01_0100_14800_00_chd | Sky chocobo wording matches the existing Thai tutorial: โจโกโบะบิน. |
| 2513 | $WORLD_CDV_01_0500_2500_00_chd | Sky chocobo wording matches the existing Thai tutorial: โจโกโบะบิน. |
| 2559 | $WORLD_CDV_02_0600_4300_00_chd | Make the direction of the comparison explicit: the evolved summon surpasses the earlier form. |
| recheck-89 | $WORLD_CDV_02_0100_5600_00_chd | Use the same sky-chocobo term in adjacent shared traversal help. |
| recheck-90 | $WORLD_CDV_02_0100_5700_00_chd | Use the same sky-chocobo term in adjacent shared traversal help. |
| 1063 | $CHADL_QST_05_0300_0200_00_bly | 萎縮 is shrinking back from fear, not depression. |
| 1107 | $CHADL_QST_05_0700_0800_00_nay | 祝福 here celebrates the lifestream; avoid suggesting people bestow magical powers on it. |
| 1153 | $CHADL_QST_05_1900_0200_00_chd | Keep the content of the legend in this subtitle; the following subtitle supplies its attribution. |
| 1154 | $CHADL_QST_05_1900_0210_00_chd | という伝承を確認しました attributes the preceding information to a legend without repeating it. |
| 1161 | $CHADL_QST_05_1900_0800_00_chd | Remove stray space inside the AI-chip noun phrase. |
| 1166 | $CHADL_QST_05_2100_0110_00_jec | Costa del Sol spoken spelling matches prior chapters: คอสตาเดลโซล. |
| 1216 | $CHADL_QST_05_2600_0600_00_chd | Remove stray space inside the AI-chip noun phrase. |
| 1331 | $COSME_QST_01_0300_2400_00_kmm | Sky chocobo wording matches the existing Thai tutorial: โจโกโบะบิน. |
| 1487 | $COSME_QST_02_0700_0200_00_art | そのかわりと言ってはなんですが is a hesitant transition to the monster encountered instead; do not end the thought as a denial. |
| 1523 | $COSME_QST_02_1100_1800_00_art | こわい顔 means a stern/scary expression, not a frightened expression. |
| 2057 | $CSMOC_NPC_10_0400_10200_00_mma | Use the same 災いの予兆 term as Caesar and the quest conversation: ลางบอกภัยพิบัติ. |
| 2061 | $CSMOC_NPC_10_0400_10600_00_mma | Use the same 災いの予兆 term as Caesar and the quest conversation: ลางบอกภัยพิบัติ. |
| 2387 | $GIZOK_BOS_14_1100_1800_00_blt | ギリギリまで走りきる refers to holding out until the last moment, not reaching the end of a route. |

คงผลตรวจครบหมวดเดิม: ตัวเลือก7,218รหัส, NPCพื้นที่ที่เยือน5,638รหัส(ไม่มีACTOR4,989), inventoryNPCเดิม8,347รหัส, ชื่อท่าอังกฤษ1,703ป้าย, source/stage40,691รหัสพร้อมtag/metadata, ทุก8ฟอนต์/nativeASCII/เลข/ไอคอนและellipsisระดับล่าง Residentญี่ปุ่นนอกหมวดปัจจุบัน1,234รหัสยังแยกเหตุผลรายIDใน qa/chapter10/recheck/Resident-residual-dispositions.json ตามเดิม ไม่มีการอ้างว่าญี่ปุ่นทุกประเภททั้งเกมหมดแล้ว

งานนี้อ่านเทียบJP/Thaiและอ้างUSรหัสเดียวกันเพื่อความหมายรายประโยคต่อจากรอบก่อน การสแกนไฟล์ครบทุกIDแยกจากการอ่านความหมายโดยมนุษย์ ไม่เท่ากับเล่นเกม/ฟังNPCครบทุกเงื่อนไข เอกสารขอบเขตบทภายหลังและลิงก์YouTubeเดิมยังอยู่ในHANDOFF/CHAPTER10-RECHECK-STATUS.md
