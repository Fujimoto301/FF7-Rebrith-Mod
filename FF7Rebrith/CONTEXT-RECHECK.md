# ตรวจบริบทบทพูดและตัวเลือก

<!-- context-full-read-current -->
## ตรวจครบชุดข้อความ Ch.1–10 + Common ที่แปลไว้แล้ว — 23 ตุลาคม 2026

**รีเช็คชุดข้อความปัจจุบันครบแล้ว 40,691 รหัส คิวค้าง 0 รหัส** บทหลัก Ch.1–10 จำนวน7,543รหัส รวมบทหลัก/NPC/เควสต์/Commonภาษาไทย32,841รหัสอ่านเทียบ JP/ไทย ส่วนป้ายอังกฤษและสัญลักษณ์7,850รหัสตรวจ JP/USรหัสเดียวกัน เปิดอ่านความต่าง495รายการและcandidateนอกหมวดชื่อ1,049รายการ รวมเงื่อนไขGambitและคำอธิบายที่ตกไป จัดคำตัดสินรายรหัสในenglish-completion-review.json ไม่อ้างว่า7,355ชื่อที่ตรงUSเป็นการอ่านบทพูดไทยใหม่ และไม่ใช่การเล่น/ฟังทุกแขนงในเกม คำถามตรวจพร้อมทุกปุ่มและบทตอบรับเมื่อมีบริบทให้เทียบ ไม่ถือผลscriptผ่านเป็นการอ่านความหมายทุกบรรทัด

รอบอ่านละเอียดแก้เพิ่ม **930 รหัส** จากรอบคัดกรองเดิม368รหัส รวมรอบบริบทสองชุด **1290 รหัส** ตัวอย่าง: ภาวะโดนพิษมาโก้, เซทรา, ห้องโดยสารชั้น2, หัวหน้าหน่วยพาเหรด, การขายโรงแรม, คำปฏิเสธ/คำพูดหยอกของเอริธ, สรรพนามเรด, ชื่อยุฟฟี่/มีน่า/บรอนโก และประโยคตาม JP เมื่อ US ดัดแปลงต่างกัน คงทีฟ่า Ch.4 **เข้ามาสิ** และ Red **เชิญ** ตามที่แก้แล้ว

ฐานล่าสุด `translations/working-through-chapter10-th.json` SHA256 **63c3e1515ac4130a05bf8126af2a50362e6a7c832a2d81613c4559e8a1f43802** ยังคง40,691รหัส/27assets/717clusters คงID/ACTOR/tag/เลขliteral/ฟอนต์และcluster-mapเดิม ผ่านอ่านกลับstageและ **8 ZIP /24 modfiles /27assets** รวมกันไม่มีซ้ำ ใน **E:/FF7RebrithModTH/Mod/Final** แต่ละส่วนมีเฉพาะZIPล่าสุด สำรองนอกFinal ไม่ติดตั้งเกม ไม่อ้างฟัง/เล่นทุกแขนง Proofแก้เพิ่ม122หน้า976panels1952font samples ตรวจครบทุกpanel โดยดูภาพใหม่/ที่เปลี่ยนในcontact sheetsจริง และเทียบRGBกับmetadataตรงทุกจุดสำหรับpanelเดิมที่เคยดูแล้ว ดูvisual-review.jsonกับpanel-visual-reuse.json

หลักฐานใหม่ `reference/context-full-read-overrides.json`, `qa/context-full-read/queue.json`, `progress.json`, `corrections.json`, `audit.json`, `proof.json`, `visual-review.json`, `release-verification.json` และ checkpointผูกsourceใน `qa/context-full-read/releases/` คิวกับbaselineเป็นsnapshotห้ามprepareซ้ำ คิวชุดนี้ตรวจครบแล้ว งานต่อไปต้องตั้งขอบเขตบทใหม่โดยcarryoverrideทั้งสองชุดและgateเดิม ไม่เริ่มบทพูดCh.11หรือเนื้อหาที่พักไว้เอง ห้ามเขียนว่าทดสอบครบทุกแขนงจากยอดการตรวจรอบนี้

ใช้ `tools/context_full_read.py --show START END` อ่านจริง → `--record START END NOTES` เฉพาะช่วงที่อ่าน → เพิ่มก่อน/หลัง/เหตุผลรายIDลงcorrections → `--commit-reviewed` → assemble/build/verify/audit/proof/signoff/publishตามgateปัจจุบัน Overlayใหม่อยู่หลังcontext_recheckเดิม ต้องcarryทั้งสองชุดในบทถัดไป ห้ามรันfinalize_context_recheckเก่าที่hardcodeยอด368ทับรายงานล่าสุด

ข้อสังเกต: คำเชิญเข้าบ้านแซ็กในรอบก่อนเป็นactor zam (แม่แซ็ก) จึงไม่ใช้คำระบุว่าพ่อแซ็กเป็นหลักฐานเพศ ผู้พูดไม่ชัดใช้กลางตามเดิม ดูรายละเอียด [CONTEXT-FULL-READ.md](E:/FF7RebrithModTH/FF7Rebrith/CONTEXT-FULL-READ.md)
<!-- /context-full-read-current -->

<!-- context-recheck-current -->
## ล่าสุด: ตรวจบริบทและตัวเลือก Ch.1–10 + Common — 21 ตุลาคม 2026

รอบนี้แก้ **368ข้อความเดิม ไม่มีเพิ่ม/ลบรหัส**: **143ข้อความด้านความหมาย/ตัวเลือกหรือคำเรียกร่วม** กับ **225ข้อความปรับศัพท์อย่างเดียว** ตรวจคำถามและทุกปุ่มหน้าฉากครบ **201กลุ่ม/777รหัส** เปลี่ยน **126รหัสใน62กลุ่ม** ให้ตอบกิจกรรมจริง เช่น ขึ้นเรือ/ยังไม่ขึ้น รายงาน/ยังไม่รายงาน ลองใหม่/ไม่ลอง รู้แล้ว/ยังไม่รู้; ใช้ตกลง/ยกเลิกเฉพาะคู่Wheelieที่แชร์ทั้งสมัครและรายงานระยะทาง แต่ละรหัสคงฝั่งตอบรับ/ปฏิเสธเดิม ไม่replaceはい/いいえแบบรวมทุกบริบท

แยกคำเชิญเข้าบ้านของพ่อแซ็ก Ch.9เป็น **เชิญเข้ามาสิ**; เก็บทีฟ่า Ch.4 **เข้ามาสิ**/RedXIII **เชิญ** และทีฟ่า Ch.1 **ถามสิ** เพราะคลาวด์ขอถามจริง แก้なんでも屋ที่หมายถึงคนจากร้านเป็นนักรับจ้าง คำถามหามงกุฎเป็นอนาคต คำตอบまあなตามความมั่นใจแต่ละฉาก คำตอบどうしたตามการเรียก/รอขึ้นเวที คำบอกล่วงหน้าของเซฟิรอธ และเรื่องเสียงผู้หญิงในคฤหาสน์เป็นเรื่องผี ปรับFortCondorโหมดHARDให้ตรงป้ายเดิม เหยื่อล่อไม่สื่อว่าต้องตกปลาด้วยเบ็ด ใช้โจโกโบะบินตรงบทสอนเดิม ศัพท์แมทีเรีย/มาโก้/ทีฟ่า/โจโกโบะ/อวาแลนช์/โซลเจอร์/โพชั่น/เซเว่นเฮฟเว่น/แซ็กเทียบต้นฉบับแยกรหัส ไม่แตะคำที่เพียงมีsubstringคล้ายกัน

ฐานยัง **translations/working-through-chapter10-th.json — 40,691รหัส / 27assets / 717clusters** sourceSHA256 **945ea2b6b86fb6d87c3d6e32710aac28e891157352028ec3322f730fe3414e1e** อีก **40,323ข้อความ** และACTORทั้งหมดเดิมครบ แก้10textassets ฟอนต์16assets/cluster-map/nativeASCII/ตัวเลขเดิมทุกไบต์ คำลงท้ายยัง1,278ครั้ง(ครับ874/ค่ะ255/คะ149) ไม่พบเพศสลับตามหลักฐานผู้พูดในauditเดิมที่carryต่อ NPC8347รหัส/UI6907รหัส/ชื่อท่าศัตรู1703รหัสยังผ่านregression

อัปเดต **ทั้ง8ZIP** ล่าสุดแยกส่วนใน E:/FF7RebrithModTH/Mod/Final แล้ว อ่านกลับ24modfiles/27assetsร่วมกันไม่มีซ้ำ สำรองรุ่นก่อนนอกFinal **ไม่ติดตั้งเกม** ไม่มีเริ่มบทพูดCh.11; ตัวเลือกบทภายหลังเป็นUIที่แปลไว้แล้วจึงตรวจร่วมด้วย

ขอบเขตหลักฐาน: คัดกรองโครงสร้าง/รหัส/ศัพท์/ตัวอักษรทั้ง40,691รหัส; อ่านเทียบตัวเลือกหน้าฉาก201กลุ่ม, sharedprompt candidates289รายการ(รวมplaceholderชื่อ????), คำสั้นซ้ำ348กลุ่มเปรียบเทียบJP/Thai/USvariants และเปิดบริบทข้างเคียงเฉพาะจุดเสี่ยง **ไม่ได้อ่านบทพูดทั้ง40,691รหัสซ้ำทุกบรรทัดหรือฟัง/เล่นทุกแขนง** จึงไม่รับรองความหมาย100% และไม่นับscriptผ่านเป็นตรวจบริบททุกบรรทัด หลักฐานนี้แยกไว้ชัดเจนในqa/context-recheck/corpus-screen.json, choice-semantic-review.json, short-dialogue-review.json, shared-prompt-review.json ดูproofglyphจริง **21หน้า/84panels/168font samples** แล้ว การตัดบรรทัดเป็นตัวอย่าง ไม่ใช่ภาพเกม

ไฟล์แก้ authoritative **reference/context-recheck-overrides.json** เก็บJP/US/ก่อน/หลัง/เหตุผลต่อasset+ID ส่วน **qa/context-recheck/baseline.json+revisions/** เป็นsnapshotก่อนรอบนี้ ห้ามprepareซ้ำ/แก้snapshot อัปเดตpatchchapter*-thที่มีรหัสนั้นแล้ว แต่แม่แบบเก่ายังคงเป็นประวัติ **assemble_chapter10.pyใช้context_recheck.overlayท้ายสุด** ห้ามเอาแม่แบบ/reuseคำสั้นเก่าทับoverride บทถัดไปต้องใช้ฐานล่าสุดและcarryoverrideนี้ พร้อมตรวจคำถามทุกปุ่ม/ประโยคก่อนหลัง ห้ามแชร์คำสั้นเพียงเพราะJPเหมือนกัน

ขั้นตอนสร้างซ้ำ: assemble_chapter10 → build_chapter10 --text-only/--verify → chapter10_recheck --quality → audit_shared_dialogs → context_recheck --review-ledger → audit_chapter10_glyphs → preview_chapter10 + chapter4_door_fix --preview + chapter4_choice_fix --preview + context_recheck_preview/ดูภาพที่เปลี่ยน → บันทึกvisual-reviewผูกhashจริง → signoff_chapter10 → publish_final_parts → finalize_context_recheck ไม่ใช้finalizerประวัติบทเก่าทับบริบทใหม่ รายงานละเอียด [CONTEXT-RECHECK.md](E:/FF7RebrithModTH/FF7Rebrith/CONTEXT-RECHECK.md)
<!-- /context-recheck-current -->

