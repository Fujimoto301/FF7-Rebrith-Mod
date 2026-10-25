# ตรวจบริบทนายและเธอ

<!-- pronoun-context-current -->
## ฐานล่าสุด: ตรวจบริบท “นาย / เธอ” ครบชุดที่แปลไว้ — 24 ตุลาคม 2026

ส่วนนี้แทนยอดhashและขั้นตอนรุ่นก่อนด้านล่าง ฐานปัจจุบัน **42,450รหัส / 27assets / 721clusters** ที่ `E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter11-th.json` SHA256 **40693dad0d32bd096011020cdb51486209cd8f3fea5255716ca07eab50b3e69c** ไม่มีเพิ่ม/ลบรหัส ไม่มีเริ่มบทพูดCh.12

ผู้ใช้สั่งตรวจบริบทของนายและเธอทั้งหมด อ่านJP/USรหัสเดียวกัน/ไทย/ผู้พูดครบ **499รหัส** จากทุกassetในชุดที่แปลไว้ (Ch.1–11 + Common รวมUIบทหลังที่มีอยู่แล้ว) ก่อนแก้มีนาย334ครั้ง/เธอ178ครั้ง นับsubstringจึงรวมคำที่ไม่ใช่สรรพนามด้วย แยกคำศัพท์อย่างนายกเทศมนตรี/นายแบบ/นายพราน/เจ้านาย/ทำนาย/อีเธอร์/บราเธอร์ออกจากการตัดสินสรรพนาม ชุดที่เป็นคำศัพท์ล้วน53รหัส เก็บไว้ตามเดิม

แก้/ปรับ **45รหัส** อีก454รหัสคงเดิม ไม่ใช่45กรณีเพศผิดทั้งหมด: มีทั้งคำเรียกCloud/Barretผิด, การเลือกคำกลางเมื่อผู้ฟังไม่ชัด, ความสุภาพ และแก้กำกวมแม่ของนายจ้าง อ่านบริบทข้างเคียงจริงในจุดกำกวม ไม่ใช้replaceทั้งเกม ไม่เดาเพศNPCจากsuffix และไม่สมมติว่าคู่รักทุกคู่ต้องชายหญิง

ตัวอย่าง: Regina/Hojo/Fran/Naomi/นักสะสมการ์ดเรียกCloudนายหรือคุณตามบริบท; ทีฟ่าพูดถึงลูกนกชอบBarretใช้**ดูจะถูกใจนายแล้วนะ**; คำรับรองกิจกรรมที่ไม่ได้ระบุผู้รับเป็นชายใช้คุณ; กลุ่มผู้ชักชวนงานใช้พวกคุณ; Gusชี้ทีละคนในกลุ่มผสมใช้คนนี้; บทคู่สนทนาที่ไม่ระบุตัวใช้คุณหรือละสรรพนาม Cloudวัยหนุ่มคุยกับวีรบุรุษSephirothใช้คุณ ส่วนBarretพูดกับTobyใช้**แม่ของนายเป็นคนจ้าง / ให้พวกเรามาเป็นบอดี้การ์ดโคฮาดะ** แยกจากความหมายแม่ของนายจ้าง

คงเธอเมื่อพูดกับ/กล่าวถึงตัวละครหญิง, คนรักหญิงที่มีบริบท, เพลงทั่วไป, การสมมติให้สัตว์/มาสคอตเป็นคู่สนทนา เช่น CloudคุยกับYuffie, BarretฝากเงินกับClaire, MadamMตรวจมือTifa, เนื้อเพลงยุฟฟี่; MadamMที่SaucerคงเธอเพราะประโยคJPถัดไประบุ**彼女** ไม่เปลี่ยนเป็นชายเพราะมีCloudอยู่ในฉาก ถ้าเรียกCloudโดยตรงใช้นาย/คุณ กลุ่มรวมCloudใช้พวกนาย/พวกคุณตามน้ำเสียง

หลักฐาน: `qa/pronoun-context/queue.json`499รหัสJP/US/ไทยเดิม, `decisions.json`คำตัดสินทุกID, `progress.json`อ่านครบ/ค้าง0, `audit.json`, `proof.json`, `visual-review.json`, `unchanged-proof-reuse.json`, `release-verification.json`; คำแก้พร้อมก่อน/หลัง/เหตุผล45รหัสอยู่ **`reference/pronoun-context-overrides.json`**; snapshotเดิมอยู่ `qa/pronoun-context/baseline.json` + `revisions/` ห้ามprepareซ้ำ บทถัดไปต้องcarryคำแก้ชุดนี้หลังcontext-recheck/context-full-read/chapter11-recheckเดิมทุกชุด ใช้ฐาน42,450ล่าสุด ห้ามประกอบบทเก่าทับหรือoverlayค่ารุ่นเก่าท้ายสุด

ตรวจอ่านกลับทุกtext/metadataทั้ง27assets ผ่านUIเดิม6907/ตัวเลือกfamily7218/NPCเดิม8347/ชื่อท่าอังกฤษ1703 คงID/ACTOR/tags/เลข/คำลงท้ายทั้งหมด ฟอนต์16ไฟล์และcluster-map byteตรงรุ่นก่อน ตรวจภาพใหม่6หน้า45panelsจากglyphNormalจริงครบ ส่วนmain12และrecheck14หน้าสร้างใหม่แล้วPNGตรงทุกไบต์กับภาพที่เคยดูจริง จึงreuseหลักฐาน26หน้าอย่างชัดเจน ไม่มีอ้างดูภาพที่เปลี่ยนโดยไม่เปิดดู ภาพตัดบรรทัดเป็นตัวอย่าง ไม่ใช่การเล่น/ฟังทุกแขนงในเกม

Finalมีเฉพาะ **8ZIPล่าสุด** แก้ทั้ง8แพ็กตามassetsที่เกี่ยวข้อง แยกZIPส่วนเดิม อ่านกลับรวม8ZIP/24modfiles/27assetsผ่านไม่มีซ้ำ สำรองรุ่นก่อนนอกFinalที่ `E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/runs/90bf161ef2da4c5c894e57d07854df7b/previous-final` ไม่ติดตั้ง/ไม่เปลี่ยนต้นฉบับ เกม หรือdist

สร้างซ้ำ: `tools/assemble_chapter11.py` → `tools/build_chapter11.py --text-only`/`--verify` → `tools/audit_shared_dialogs.py` (รวมpronounauditใหม่และgateเดิม) → previewบท11/recheck/pronoun → ดูภาพใหม่หรือยืนยันreuseเฉพาะภาพเดิมbyteตรง → บันทึกvisual-review → `tools/signoff_chapter11.py` → `tools/publish_final_parts.py` → **`tools/finalize_pronoun_context.py`** แทนfinalizerเก่าที่ผูกยอดก่อนมี45คำแก้นี้ ไม่เปลี่ยนsnapshotประวัติเพื่อให้auditผ่าน

คู่มือคำลงท้าย/ศัพท์และคลิปYouTubeในส่วนก่อนยังใช้ต่อ: ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ ผู้พูดไม่ชัดใช้กลาง ไม่บังคับเติมทุกบรรทัด ยอดคำลงท้าย1548ครั้งคงเดิม คงเอริธ/แซ็ก/เค็ตชี/เรดวัยหนุ่มฉัน และทีฟ่าCh.4เข้ามาสิ/Redเชิญ รอบนี้ไม่ได้ดูฟังวิดีโอครบใหม่
<!-- /pronoun-context-current -->

## ZIPปัจจุบัน

- [ThaiJP_Chapter1_11_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter1_11_P.zip) — 98,185 bytes; SHA256 `f84ca0a8759e3c4456fdc2406d88a732c3494abec2422cb8e9761ccce0a0d4e3`
- [ThaiJP_Chapter2_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter2_P.zip) — 119,853 bytes; SHA256 `df2f2cd4190e27fea4bd7ccda84f7a7ae6257768a912160c4fee611068ec9c24`
- [ThaiJP_Chapter3_4_5_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter3_4_5_P.zip) — 117,024 bytes; SHA256 `ccaf7728509690c9c7609b4e409065bfba6700741f7b73530cf801484f18526f`
- [ThaiJP_Chapter6_7_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter6_7_P.zip) — 115,238 bytes; SHA256 `7d6d07523d0636b7e312a744053f3907cea5241c08e6acf90d2ba5af1f1dcb63`
- [ThaiJP_Chapter8_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter8_P.zip) — 125,812 bytes; SHA256 `22516514754cdb53dd83c015c05a870f05c65dcd6c0de3692bf113d083a2f2ba`
- [ThaiJP_Chapter9_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter9_P.zip) — 59,428 bytes; SHA256 `1736bf5c3aca8c7d7278466feecd82397ea3db8f895af2af2c6c73e2e2b40803`
- [ThaiJP_Chapter10_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter10_P.zip) — 71,479 bytes; SHA256 `d2e56ec22fa103ae272b6f694d45f1bfcb5f76f630662f65d8da8410c0e16e8c`
- [ThaiJP_Common_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Common_P.zip) — 20,419,432 bytes; SHA256 `c0cbd8092196b885d7e575bcbb7121df7b95100aa3f5b9cae580ee11cee78aa2`
