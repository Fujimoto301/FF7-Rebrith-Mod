# เก็บตก NPC Ch.2–9 และ Common

<!-- npc-recheck-current -->
## ล่าสุด: เก็บตก NPC Ch.2–9 และ Common — 19 ตุลาคม 2026

ส่วนนี้แทนพาธและยอดปัจจุบันในประวัติด้านล่าง เพิ่ม **1,573 รหัส / 1,515 แม่แบบ** เหนือฐาน 34,589 รหัส คงข้อความและ ACTOR เดิมครบ ปัจจุบัน **36,162 รหัส / 27 assets / 711 clusters** แก้ Akira ในภาพครบทั้ง 22 รหัส รวมผู้ชมและบท NPC กลับเยือนเมือง ตรวจ inventory **8,347 รหัส** รวม NPC มี/ไม่มี ACTOR และ shared WORLD/CARDG/MOGLE/PHOTO ไม่อ้างว่าเล่นครบทุกแขนงหรือฟังทุก NPC ใหม่แล้ว

ต้นเหตุที่ยืนยัน: เคยพัก KALMT_NPC_30 ทั้งหมวดตามสถานะตัวเลข ทำให้นักร้องและบทเมืองปกติตกไปด้วย อีกจุดคือบททะเลทราย/งาน Johnny/ตามหานกที่พักตอน Ch.7 ไม่ได้ถูกนำกลับมาตอนเปิดถึง Ch.9 รอบนี้รวมเควสต์ Corel 01–05 และโปรโตเรลิก 2 การทดสอบแรกแล้ว รวมเสียง Nanaki ทางเลือกและบทกลับเยือนของเควสต์เดิมด้วย ยังไม่เริ่มแปลบทหลัก Ch.10 หรือเควสต์ใหม่ที่เริ่ม Ch.12

ฐานต่อไป **E:/FF7RebrithModTH/FF7Rebrith/translations/working-npc-recheck-th.json**; config reference/npc-recheck-build.json; map reference/npc-recheck-cluster-map.json; stage staging/ThaiJP_NPC_Recheck_Working; QA qa/npc-recheck รายละเอียด [NPC-RECHECK-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/NPC-RECHECK-STATUS.md) ห้ามใช้ฐาน choice-completion/Ch.9 เดิมทับชุดนี้

ตรวจย้อนต้นฉบับในไฟล์ภูมิภาคที่เยือนทั้งหมด: *_NPC_* ครบ **4,804 รหัส** รวมไม่มี ACTOR **4,218 รหัส** และตรวจข้อความญี่ปุ่นทุกตัวที่ยังไม่แปลในไฟล์ฉากอีกชั้น เหลือ **2,708 รหัส** พร้อมเหตุผลรายรหัสใน visited-scene-residual-dispositions.json: บทหลัก/เควสต์ปลดล็อกภายหลัง, โปรโตเรลิกช่วงถัดไป, ฉากโบนัสท้าย Remake/INTERmission ไปคาล์ม 36 รหัส และ Test0 battle/debug 14 รหัส ไม่ใช่การยืนยันว่าทุกข้อความทั้งเกมแปลครบ

ฟอนต์ 16 assets/map 711 ตรงฐานก่อนรอบนี้ทุกไบต์ คง ASCII/เลข/ไอคอนและ … ระดับล่างทั้ง 8 fonts คำลงท้ายเดิม 976 ครั้งใน 952 รหัสคงเดิม: ครับ 651 / ค่ะ 198 / คะ 127; NPC/nonparty เดิม 838 ครั้ง ไม่มีคำลงท้ายใหม่ที่ต้องเดาเพศ Unknown NPC ใช้กลาง ไม่อนุมานเพศจาก mma/mfa; ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ ชื่อพูดไทยตาม glossary (Aerith เอริธ, Wutai อู่ไถ, Avalanche อวาแลนช์, Mako มาโก้); ACTOR/UI อังกฤษตาม US รหัสเดียวกัน Akira พูดชื่อ อากิระ / ป้าย Akira ตรวจ tag/metadata/ตัวเลขต่าง 17 รายการแล้ว

Final มี 7 ZIP ล่าสุดแยกส่วน ต้องใช้ร่วมกัน อ่านกลับรวม 21 mod files / 27 assets ไม่มีซ้ำ อัปเดต Ch.2, Ch.3–5, Ch.6–7, Ch.8, Ch.9 และ Common; Ch.1 ไบต์เดิม สำรองนอก Final ไม่ติดตั้งและไม่แก้ต้นฉบับ/dist/ม็อดในเกม Common ยังถือ COSME เฉพาะ UI ตัวเลือก เมื่อทำบทที่ใช้ COSME ต้องย้ายทั้ง asset ไป ZIP เจ้าของใหม่ไม่ซ้ำ

ขั้นตอนรอบนี้: assemble_npc_recheck.py → build_npc_recheck.py --text-only (ไม่มี glyph ใหม่) → --verify → audit_shared_dialogs.py (รวม audit_npc_recheck.py และ audit_npc_remaining.py) → preview_npc_recheck.py และดู proof 4 หน้า → signoff/numeric-review ผูก hash → publish_final_parts.py (อ่านกลับทุก ZIP รวมกัน) → finalize_npc_recheck.py ห้าม prepare ซ้ำ/สลับ index/เขียนทับ snapshot/รัน finalize บทเก่าทับ active context

**ทุกบทต่อไป:** ตรวจ NPC ทุกสถานะในพื้นที่ที่ทำ ทั้งมี/ไม่มี ACTOR พร้อม quest NPC, shared WORLD/CARDG/MOGLE/PHOTO และ namespace ข้างเคียง ตรวจตัวเลือกพร้อมคำถาม/ทุกปุ่ม/คำอธิบาย/ชื่อเป้าหมายทั้งหมวด เพิ่ม family/inventory ใหม่ก่อนแพ็ก ทำ inverse scan ทุกข้อความที่ยังไม่แปลในไฟล์ฉาก จัดเหตุผลรายรหัสตามเนื้อหาและเงื่อนไขปลดล็อกจริง ห้ามพักทั้งหมวดจากเลข NPC_30 หรือคำว่า return เพียงอย่างเดียว ขยายรายการเควสต์เดิมที่เปิดเพิ่มในบทใหม่ด้วย ไม่ตรวจเฉพาะฉากหลัก

audit_shared_dialogs.py จะเรียก audit_npc_regression.py เมื่อ active source เป็นบทใหม่ เพื่อกัน NPC 8,347 รหัสเดิมตกและไม่รีเซ็ต active context กลับมารอบนี้ บทใหม่ต้องสร้าง inventory/QA/signoff ของตัวเองและขยาย publisher gate ให้ตรวจ source ใหม่ด้วย ห้ามข้าม gate โดยปิด npc_recheck/choice_completion; ก่อนส่งต้องตรวจ glyph/ชื่อ/เพศ/ตัวเลขและอ่านกลับชุด ZIP จริงเสมอ
<!-- /npc-recheck-current -->


## ไฟล์ส่งต่อ

พาธต่อจาก **E:/FF7RebrithModTH/FF7Rebrith/**:

| ใช้ทำอะไร | ไฟล์/โฟลเดอร์ |
| --- | --- |
| ฐานรวมปัจจุบัน | translations/working-npc-recheck-th.json |
| เฉพาะข้อความเพิ่ม | translations/npc-recheck-th.json |
| แม่แบบแปลเอง 1,515 ข้อ ห้ามสลับ index | translations/npc-recheck/batch-00.json ถึง batch-11.json; reference/npc-recheck-templates.json |
| JP/US inventory 8,347 รหัส | reference/npc-recheck-source.json |
| ขอบเขตถาวร | tools/npc_recheck.py |
| ต้นฉบับ JP/US | reference/rebirth-jp-corpus.json; source/End/Content/Text/JP/; source/End/Content/Text/US/ |
| Config/map/stage | reference/npc-recheck-build.json; reference/npc-recheck-cluster-map.json; staging/ThaiJP_NPC_Recheck_Working/ |
| Snapshot ก่อนทำรอบนี้ ห้ามทับ | qa/npc-recheck/baseline.json; revisions/ |
| ตรวจรายรหัส/actor/เลข | qa/npc-recheck/review-records.json; actor-review.json; numeric-review.json |
| ตรวจซ้ำต้นฉบับ/ไม่มี ACTOR | qa/npc-recheck/visited-NPC-coverage.json; visited-scene-residual-dispositions.json; other-region-NPC-deferred.json |
| Build/ตรวจ glyph/เพศ/ภาพ | qa/npc-recheck/verification.json; translation-audit.json; proof.json; proof-1.png ถึง proof-4.png; editorial-signoff.json |
| ผลส่งจริง/อ่านกลับ | qa/npc-recheck/release-verification.json; qa/final-parts/latest.json; qa/final-parts/combined-mount-verification.json |
| งานก่อนหน้า เก็บไว้เพื่อประวัติ | CHOICE-COMPLETION-STATUS.md; qa/choice-completion/; qa/chapter9/ |
| เพศ/เสียง NPC เดิม | qa/chapter9/gender/records.json; qa/chapter9/gender/summary.json; reference/plearngaming/glossary.json |

## ชุด ZIP

| ZIP ใน E:/FF7RebrithModTH/Mod/Final | assets | bytes |
| --- | ---: | ---: |
| ThaiJP_Chapter1_P.zip | 2 | 95,094 |
| ThaiJP_Chapter2_P.zip | 2 | 119,229 |
| ThaiJP_Chapter3_4_5_P.zip | 1 | 116,959 |
| ThaiJP_Chapter6_7_P.zip | 1 | 115,220 |
| ThaiJP_Chapter8_P.zip | 1 | 125,828 |
| ThaiJP_Chapter9_P.zip | 1 | 59,395 |
| ThaiJP_Common_P.zip | 19 | 20,400,312 |

สำรองชุดที่ถูกแทนไว้ที่ `E:\FF7RebrithModTH\FF7Rebrith\qa\final-parts\runs\441cf35b5ebf40cbb67f09e33c13390a\previous-final` ZIP มีเฉพาะ .pak/.utoc/.ucas ใบอนุญาตฟอนต์อยู่ใน ZIP comment ชุดปัจจุบันยังไม่ได้ติดตั้งหรือทดสอบในเกม

## ขอบเขตที่ต้องแยกให้ชัด

NPC เมืองเดิมและ NPC ของเควสต์เดิมรวมทุก return state บางรหัสจึงกล่าวถึงสงคราม/Gold Cup ภายหลังด้วย เพื่อไม่พักยกหมวดจนพลาดบทปกติ แต่ยังไม่ได้แปลเควสต์เนื้อเรื่องใหม่หลัง Ch.9 ทั้งชุด เช่น Trouble in Paradise, Woodland Vigil, ภาคจบ Queen's Blood และโปรโตเรลิก Corel การทดสอบ 3–4 รายละเอียดทุกข้อความที่เหลือใน 5 ไฟล์ภูมิภาคอยู่ใน residual-dispositions และไฟล์ของภูมิภาคที่ยังไม่เยือนแยกอีกชุด จึงไม่ใช่หลักฐานว่าไม่มีภาษาญี่ปุ่นทั้งเกม

ทวนเงื่อนไขปลดล็อกเควสต์กับเนื้อหาต้นฉบับ: [Missing: Mr. Birdie เปิด Ch.9](https://www.powerpyx.com/final-fantasy-7-vii-rebirth-chapter-9-the-planet-stirs-walkthrough/), [รายการเควสต์แยกบท](https://www.powerpyx.com/final-fantasy-7-vii-rebirth-all-side-quest-locations/), [Trouble in Paradise เปิด Ch.12](https://www.powerpyx.com/final-fantasy-7-vii-trouble-in-paradise-walkthrough/) ใช้ตรวจขอบเขต ไม่ใช้แทนเสียง/เพศ NPC

## ข้อจำกัดและงานต่อไป

ภาพ proof เป็นการเรนเดอร์ glyph จาก stage จริง 16 ตัวอย่างใน Large/Normal รวม 32 การแสดงผล 4 หน้า ตรวจแล้ว ตัวอย่างรวม Akira, ฝูงชน, Gongaga, shared intel, Johnny และตัวเลขกับดักนก การตัดบรรทัดเป็นแบบจำลอง ไม่ใช่ภาพในเกม ยังต้องทดสอบการโหลดจริง ความยาวซับ ชื่อผู้พูด ตัวเลือกทุกแขนง และฟังเสียง NPC ที่หลักฐานยังไม่ชัดเมื่อมีงานทดสอบในเกม ห้ามกล่าวว่าเดินครบทุก NPC หรือฟังวิดีโอครบแล้ว

เริ่มบทถัดไปจากฐาน working-npc-recheck เท่านั้น รักษา glyph append-only/ระดับจุด/ASCII/ตัวเลขเดิม ทบทวน deferred เดิมตามการปลดล็อกในบทใหม่ พร้อมเพิ่ม inverse scan และเก็บชื่อ/คำลงท้ายตามผู้พูดจริง ไม่อนุมานเพศจาก ID

ลิงก์บท/เสียง/เพศส่งต่อจากงานเดิม: [คลิปหลัก](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk) พร้อม reference/plearngaming/remake/decoded-corpus.json รอบนี้ไม่ได้ฟังใหม่ครบและไม่มี timestamp ยืนยัน NPC ทุกตัว
