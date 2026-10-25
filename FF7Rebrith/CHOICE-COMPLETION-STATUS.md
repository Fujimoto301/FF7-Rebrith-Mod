# เก็บตกตัวเลือกและชื่อเควสต์ทั้งเกม

<!-- choice-completion-current -->
## ล่าสุด: รีเช็คเก็บตกตัวเลือกและข้อความข้างเคียง — 19 ตุลาคม 2026

ส่วนนี้แทนพาธและยอดปัจจุบันในประวัติด้านล่าง **รีเช็คเพิ่ม 687 UI** เหนือชุดก่อน 33,902 รหัส คงข้อความและ ACTOR ชุดนั้นครบ รวมเก็บตกสะสม **1,730 UI** เหนือฐาน Ch.1–9 เดิม 32,859 รหัส ปัจจุบัน **34,589 รหัส / 27 assets / 711 clusters** ไม่เพิ่มบทพูดบทหลัง Ch.9 ตรวจคำถามและตัวเลือก scene *_sys ทุกไฟล์ พร้อม Resident และ namespace ข้างเคียงทั้งหมวด รวม inventory **7,770 รหัส** ไม่อ้างว่าเกมทั้งหมดไม่มีญี่ปุ่นหรือทดสอบทุกแขนงในเกมแล้ว

รอบรีเช็คพบเพิ่มตัวนับส่ง Chocograss/วัสดุ Johnny/จำนวนศัตรูที่กำจัด เงื่อนไขเลือกเป้าหมายและคำอธิบาย Gears and Gambits อีกชุดรหัส GC/GE/GF/GAN เงื่อนไขปลดล็อกสนาม ป้ายพื้นที่ Zack/ร้าน/กิจกรรม ชื่อ NPC บน UI คำอธิบายของเควสต์/ของสะสม/วิธีรับรางวัลและ World Intel ส่วนที่เหลือ เพิ่ม inverse scan จากข้อความ Resident ไม่มี ACTOR ทุกตัวที่ยังไม่แปล เพื่อจับหมวดที่ไม่ได้ลงทะเบียนเดิม ไม่ใช้เพียง regex คำถามชุดเก่า

แก้ภาพผู้ใช้: คำถามใช้ Cushion พร้อม พัก/ไม่พัก/แจ้งเมื่อไม่มี Cushion; HUD เป็น **รอยเท้าโจโกโบะ / จับ Piko ให้ได้**; คำถามบทสอน Queen's Blood พร้อม ใช่/ไม่ใช่ ยังครบ เก็บ native COMMAND และชื่อ UI อังกฤษตามเดิม

ฐานใหม่ **E:/FF7RebrithModTH/FF7Rebrith/translations/working-choice-completion-th.json**; config reference/choice-completion-build.json; map reference/choice-completion-cluster-map.json; stage staging/ThaiJP_ChoiceCompletion_Working; QA qa/choice-completion รายละเอียด [CHOICE-COMPLETION-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHOICE-COMPLETION-STATUS.md) ห้ามใช้ฐาน Ch.9 เดิมทับงานใหม่นี้

ฟอนต์ 16 assets และ map 711 ตัวตรงฐานก่อนรอบนี้ทุกไบต์ จึงคง ASCII/เลข/ไอคอนและ … ระดับล่างครบ 8 fonts คำลงท้ายเดิม 976 ครั้งใน 952 รหัสคงเดิม: ครับ 651 / ค่ะ 198 / คะ 127; NPC/nonparty 838 ครั้ง ไม่มีคำลงท้ายใหม่ ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ Unknown NPC ใช้กลาง ไม่อนุมานเพศจาก mma/mfa; คะ… ใน คะ…ครับ! ของ Militiaman คือเสียงติดอ่างที่ตรวจไว้ ไม่ใช่คำลงท้ายหญิง

Final มี 7 ZIP ล่าสุดแยกส่วน ต้องใช้ร่วมกัน อ่านกลับรวม 21 mod files / 27 assets ไม่มีซ้ำ อัปเดตรอบนี้: ThaiJP_Common_P.zip คงเดิม: ThaiJP_Chapter1_P.zip, ThaiJP_Chapter2_P.zip, ThaiJP_Chapter3_4_5_P.zip, ThaiJP_Chapter6_7_P.zip, ThaiJP_Chapter8_P.zip, ThaiJP_Chapter9_P.zip Common ถือ Resident/ฟอนต์/TITLB และ **COSME เฉพาะ UI ตัวเลือก**; เมื่อทำบทที่ใช้ COSME ต้องย้ายทั้ง asset ไปเจ้าของ ZIP ใหม่ไม่ให้ซ้ำ สำรองนอก Final ไม่ติดตั้งและไม่แก้ต้นฉบับ/dist/ม็อดในเกม

ตรวจต้นฉบับ corpus 12 text assets/56,171 รหัส เทียบ inventory และ staging จริง ค้นอิสระคำถาม 1,641 รหัสกับปุ่มสั้น 315 รหัส แยก 194 ข้อความนอกหมวดเป็น NPC/บทภายหลัง/ข้อมูลศัตรู/demo พร้อมเหตุผล และ 10 choice-like keys ที่เหลือเป็น demo เท่านั้น ตรวจตัวเลขต่าง 46 รายการ และ proof จาก glyph จริง 8 หน้า/64 ตัวอย่างแล้ว ไม่ใช่ภาพเกมและไม่ได้ฟังวิดีโอครบใหม่

inverse scan พบ Resident ไม่มี ACTOR ที่ยังเป็นญี่ปุ่น 2,244 รหัส แยกรายรหัสแล้ว: ชื่อท่าโจมตีศัตรู 1,667 / ข้อมูลชีวประวัติและคำใบ้วิเคราะห์ศัตรู 544 / demo 29 / เสียง Moogle ไม่มี ACTOR 4 ไม่ใช่ตัวเลือกหรือชื่อเป้าหมายที่กำลังซ่อม ชื่อศัตรูและเมนูนำทางสมุดศัตรูครอบคลุมแยกไว้แล้ว ไม่มี residual UI ที่ยังไม่จัดประเภทใน Resident

ขั้นตอน: assemble_choice_completion.py → build_choice_completion.py --text-only (เมื่อไม่มี glyph ใหม่) → build_choice_completion.py --verify → audit_shared_dialogs.py (เรียก audit_choice_completion.py ด้วย) → preview_choice_completion.py และ --recheck แล้วดูภาพทั้ง 8 หน้า → ทบทวน signoff/numeric-review ผูก hash → publish_final_parts.py → verify_final_parts.py → finalize_choice_completion.py ห้ามรัน prepare ซ้ำ/เปลี่ยน index/ใช้ audit หรือ finalize บทเก่าทับ active context ใช้ recheck/current.json เป็น snapshot ก่อนรีเช็ค เก็บ baseline เดิมครบ หากติดตั้งชุดก่อนระหว่างรอบให้เทียบ fingerprint ตั้งแต่ต้นรีเช็ค ไม่ทับ snapshot เก่า

งานต่อไป: เมื่อทำบทใหม่ให้เริ่มฐานใหม่ข้างบน ตรวจ NPC ทั้งมี/ไม่มี ACTOR, shared/PHOTO/WORLD/CARDG และ namespace ข้างเคียง ทบทวนรายการพักตามสถานะปลดล็อก ตรวจคำถามพร้อมทุกปุ่ม รับ/ไม่รับ/ลองใหม่/ยกเลิก/ผลแพ้ชนะ/คำอธิบายและชื่อเป้าหมายทั้งหมวด เพิ่ม family ใน choice_completion.py/audit_shared_dialogs.py และรัน gate ก่อนแพ็กทุกครั้ง
<!-- /choice-completion-current -->


## ขอบเขตและหลักฐาน

รีเช็คเพิ่ม 687 UI รวม patch สะสม 1,730 รหัสจาก 887 แม่แบบที่แปลเอง ร่วมกับชื่อทางการ US และ reuse ที่ตรวจแล้ว คงบทพูด/ACTOR Ch.1–9 และ UI ชุดก่อน 33,902 รหัสทั้งหมด คง asset 8600-COSME สำหรับตัวเลือกเท่านั้น ยังไม่ได้แปลบทพูด Ch.10 เป็นต้นไป รอบนี้เก็บ World Intel รวม Detail_Clear/Detail_NA และคำอธิบาย/จดหมายบนหน้าของสะสมทั้งหมวดด้วย เป็น UI ที่อ่าน ไม่ใช่บทพูดฉากใหม่ ไม่ได้อ้างว่าแปลข้อความเกมทุกประเภทครบ

ตรวจ inventory 7,770: เดิม 5,854 + patch สะสม 1,730 + ต้นฉบับอังกฤษ/สัญลักษณ์ที่คงไว้ 186 รหัส มี hidden sentinel <> เดิม 2 รหัส และโน้ต C・/C・♯ ตรง US ไม่ใช่คำญี่ปุ่นตกหล่น ตรวจด้วยข้อความ รูปแบบ key และ inverse scan อิสระอีกชั้น รายการนอกหมวดมีเหตุผลรายรหัส ไม่ใช้เปอร์เซ็นต์ประมาณแทนหลักฐาน

JP เป็นหลัก ชื่อกิจกรรม/ตัวละคร/ศัตรู/ไอเทม/พื้นที่บน UI เป็นอังกฤษตาม US รหัสเดียวกัน ชื่อในบทพูดยังไทยตาม glossary: Aerith = เอริธ / ACTOR Aerith; ไม่แก้บทพูดเดิม เลขจำนวนจริงใช้อารบิก เช่น 第七→7, ひとつ→1, ふたり→2, ゼロ→0 และ壱弐参四→1–4; First Class เป็นชื่อยศทางการ; 1機ごと→แต่ละตัว คงเงื่อนไขต่อหน่วย แท็กและ metadata ตรวจตรงต้นฉบับทุกตัว

ภาพ proof ใช้ glyph จาก stage จริงทั้ง Large/Normal 8 หน้า/64 ตัวอย่าง แทน object=0 ด้วย Cushion เพื่อดูภาพเท่านั้น ไม่เขียนชื่อตายตัวแทนตัวแปรในเกม การตัดบรรทัด/ปุ่มใน proof เป็นแบบจำลอง ยังต้องทดสอบตำแหน่ง ความยาว การตัดบรรทัด และทุกแขนงในเกมจริงเมื่อมีคำสั่งติดตั้ง

## ไฟล์ส่งต่อ

พาธทุกแถวต่อจาก **E:/FF7RebrithModTH/FF7Rebrith/**:

| ใช้ทำอะไร | ไฟล์/โฟลเดอร์ |
| --- | --- |
| ฐานรวมปัจจุบัน | translations/working-choice-completion-th.json |
| เฉพาะ patch UI | translations/choice-completion-th.json |
| คำแปลแม่แบบ | translations/choice-completion/batch-00.json ถึง batch-11.json (รอบรีเช็ค 07–11) |
| US/reuse ที่ตรวจแล้ว | translations/choice-completion-automatic.json |
| inventory JP/US | reference/choice-completion-source.json |
| แม่แบบ 887 ข้อ ห้ามสลับ index | reference/choice-completion-templates.json |
| corpus JP; US ต้นฉบับ | reference/rebirth-jp-corpus.json; source/End/Content/Text/US/ |
| config/map/stage | reference/choice-completion-build.json; reference/choice-completion-cluster-map.json; staging/ThaiJP_ChoiceCompletion_Working |
| snapshot ก่อนรอบนี้ ห้ามเขียนทับ | qa/choice-completion/baseline.json; qa/choice-completion/revisions/ |
| snapshot รีเช็ค/รายการเพิ่ม 687 | qa/choice-completion/recheck/current.json; recheck/snapshots/; recheck/review.json |
| audit และรายรหัสเพิ่ม | qa/choice-completion/translation-audit.json; review-records.json |
| ค้นอิสระ/เหตุผลไม่ใช่ตัวเลือก | qa/choice-completion/independent-dispositions.json; independent-choice-key-dispositions.json; quest-namespace-dispositions.json; remaining-Resident-dispositions.json |
| ตัวเลขและ signoff ผูก hash | qa/choice-completion/numeric-review.json; editorial-signoff.json |
| ตรวจไฟล์/ภาพ | qa/choice-completion/verification.json; working-assets.json; proof.json; proof-1.png ถึง proof-4.png; recheck-proof.json; recheck-proof-1.png ถึง recheck-proof-4.png |
| เพศเดิมและหลักฐาน NPC | qa/chapter9/gender/records.json; qa/chapter9/gender/summary.json |
| ส่งมอบ | qa/choice-completion/release-verification.json; qa/final-parts/latest.json; qa/final-parts/combined-mount-verification.json; qa/active-working-set.json |
| เครื่องมือ | tools/choice_completion.py; prepare_choice_completion.py (ห้ามรันซ้ำ); extend_choice_completion.py (append เท่านั้น); assemble_choice_completion.py; build_choice_completion.py; audit_choice_completion.py; preview_choice_completion.py; finalize_choice_completion.py; audit_shared_dialogs.py; publish_final_parts.py; verify_final_parts.py |

Python **C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe** ตั้ง PYTHONUTF8=1 รันจาก E:/FF7RebrithModTH/FF7Rebrith/ ทุกครั้ง หากแก้ข้อความต้อง assemble/build/verify/audit ดู proof ใหม่และทบทวน signoff hash ใหม่ หากเพิ่ม glyph ต้อง build เต็มกับ map append-only ห้ามใช้ text-only

## ZIP ล่าสุด

| ZIP | assets | bytes |
| --- | ---: | ---: |
| ThaiJP_Chapter1_P.zip | 2 | 95,094 |
| ThaiJP_Chapter2_P.zip | 2 | 119,834 |
| ThaiJP_Chapter3_4_5_P.zip | 1 | 117,631 |
| ThaiJP_Chapter6_7_P.zip | 1 | 116,014 |
| ThaiJP_Chapter8_P.zip | 1 | 126,548 |
| ThaiJP_Chapter9_P.zip | 1 | 59,493 |
| ThaiJP_Common_P.zip | 19 | 20,401,877 |

ที่เก็บ **E:/FF7RebrithModTH/Mod/Final** ต้องใช้ทั้ง 7 ZIP ร่วมกัน สำรองก่อนทับที่ **E:\FF7RebrithModTH\FF7Rebrith\qa\final-parts\runs\238f6296189141799a2a25cb75725cb3\previous-final** ไม่ติดตั้ง รอบนี้อัปเดต ThaiJP_Common_P.zip; คงเดิม ThaiJP_Chapter1_P.zip, ThaiJP_Chapter2_P.zip, ThaiJP_Chapter3_4_5_P.zip, ThaiJP_Chapter6_7_P.zip, ThaiJP_Chapter8_P.zip, ThaiJP_Chapter9_P.zip ตรวจอ่านกลับแล้ว 27 assets ไม่มี overlap

## งานที่ยังต้องทำ

แปลบทพูดบทถัดไปเมื่อผู้ใช้สั่ง เริ่มจากฐาน choice-completion นี้เพื่อไม่ทำ UI หาย ทบทวน deferred Ch.9 252 รหัสและบทก่อนหน้าตามสถานะจริง คงชื่อพูด/เพศ/คำลงท้ายตามหลักฐาน เมื่อใช้ COSME ให้จัดเจ้าของ asset ใหม่ทั้งไฟล์กับ Common โดยไม่ซ้ำ ยังต้องทดสอบ runtime ทุกตัวเลือกที่เกี่ยวข้อง/ทางแยก และตรวจเสียงผู้พูดที่หลักฐานยังไม่ชัด ไม่ยืนยันว่าไม่มีตกหล่นในเกม 100%

อ้างอิงบท/เสียง/เพศจากงานเดิม: [คลิปหลัก](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk) และ reference/plearngaming/glossary.json / reference/plearngaming/remake/decoded-corpus.json ลิงก์ส่งต่อจากบันทึกเดิม รอบนี้ไม่ได้ฟังใหม่ครบหรือมี timestamp ยืนยันทุก NPC
