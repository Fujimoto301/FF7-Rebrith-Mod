# ชื่อศัตรูอังกฤษทั้งเกม — 2026-10-16

ผู้ใช้สั่งเริ่มแปลชื่อศัตรูทั้งหมดแล้ว จึงใช้ชื่ออังกฤษทางการตามเงื่อนไขที่กำหนดไว้ก่อนหน้า คำสั่งพักชื่อศัตรูในเอกสาร/QA รุ่นก่อนถือว่าถูกแทนที่

ตรวจและใส่ชื่อ 398 รหัส: ชื่อศัตรูหลัก `$en_` ครบ 312 รหัส, ศัตรูมินิเกม Gears and Gambits `$GE_Enemy_*_Name` 14 รหัส และชื่อส่วนเป้าหมายของบอส/กลไกที่เกี่ยวข้องอีก 72 รหัส เช่น แขน ปีก ขา ปืนและเกราะ ชื่อ 3 รหัสของ Sephiroth อยู่ในฐานเดิมแล้ว จึงเพิ่มจริง 395 รหัส รวมทั้งชุดปัจจุบัน **17,178 รหัสข้อความ**

ใช้ข้อความ US รหัสตรงกับ JP ทุกตัว ไม่ถอดเสียงชื่อขึ้นเอง รวมศัตรูหายาก บอส อสูรอัญเชิญ รูปแบบ VR และป้ายคะแนนศัตรูในมินิเกม ตัวอย่าง:

| JP | อังกฤษทางการ |
| --- | --- |
| スピードサウンド | Velociwing |
| マテリアキーパー | Materia Guardian |
| ミドガルズオルム | Midgardsormr |
| ヘルハーレーＶＲ２ | Hell Rider II |
| 警備兵 | Security Officer |
| 重火兵 | Flametrooper |

ชื่อในแถบ HP/รายการศัตรู/ข้อมูลศัตรูและตัวแปรชื่อที่ผลหลังต่อสู้จะใช้รหัสชื่ออังกฤษเหล่านี้ เช่น `กำจัด Velociwing แล้ว` คงข้อความระบบที่แปลแล้วและแท็ก `<object=0>` เดิม ไม่แก้ชื่อศัตรูที่ถูกกล่าวในประโยค Dialogue เดิม ซึ่งยังเป็นไทยตามกฎชื่อเฉพาะ ไม่มีการเพิ่มการแปลบทพูดหรือคำบรรยายชีววิทยา/คำแนะนำต่อสู้ของสารานุกรมศัตรูในรอบนี้

ไฟล์หลัก:

- `E:/FF7RebrithModTH/FF7Rebrith/tools/assemble_enemy_names.py` — สร้างรายการชื่อจาก JP/US พร้อม scope และ snapshot ก่อนแก้
- `E:/FF7RebrithModTH/FF7Rebrith/reference/enemy-name-source.json` — JP/US รายรหัสและหมวด
- `E:/FF7RebrithModTH/FF7Rebrith/reference/enemy-name-scope.json` — ชุดรหัส/แฮช source และนโยบาย
- `E:/FF7RebrithModTH/FF7Rebrith/translations/enemy-names-th.json` — ชุดชื่ออังกฤษที่จะนำเข้าผลรวม
- `E:/FF7RebrithModTH/FF7Rebrith/tools/assemble_ui_completion.py` — รวมชื่อชุดนี้อัตโนมัติเมื่อมีไฟล์ข้างต้น
- `E:/FF7RebrithModTH/FF7Rebrith/qa/enemy-names/audit.json` — ความครบ 398 รหัส เทียบ US อ่านกลับ staging และตรวจข้อความเดิม
- `E:/FF7RebrithModTH/FF7Rebrith/qa/enemy-names/baseline.json` — พาธ snapshot/แฮชก่อนแก้

ลำดับสร้าง: `assemble_enemy_names.py` → `assemble_ui_completion.py` → `build_chapter1.py --ui-completion-working --text-only` (ถ้า cluster map ไม่เปลี่ยน) → `verify_chapter1.py --ui-completion-working` → `audit_ui_completion.py` → `audit_enemy_names.py` → `audit_ui_piano_notifications.py` → `publish_final_parts.py`

ผลตรวจรอบชื่อศัตรู: ชื่อครบตาม scope และตรง US, ไม่มี JP ในชื่อที่เลือก, metadata/แท็กคงเดิม, คำแปลก่อนหน้าทั้งหมดคงเดิม, source/ไฟล์ติดตั้งไม่เปลี่ยน รอบนั้นมีเพียง Resident asset เปลี่ยน ฟอนต์และ 4 ไฟล์ฉากไม่เปลี่ยน จึงเผยแพร่การแก้ใน `E:/FF7RebrithModTH/Mod/Final/ThaiJP_Common_P.zip` ส่วน ZIP Chapter1/2 ใช้เดิมร่วมกัน แพ็ก/อ่านกลับและ mount ทั้ง 3 แพ็กรวมกันก่อนส่ง งานนี้ยังไม่ได้ติดตั้งหรือทดสอบเล่นในเกมจริง

รอบแก้แนวถัดมา: อัปเดต origin ของฟอนต์ 8 assets เพื่อจัดไทยกับชื่ออังกฤษ/ตัวเลขที่เกมเติมภายหลัง ชื่อศัตรูทั้งหมดคงเดิมและผ่าน regression อีกครั้ง ดู `BASELINE-ALIGNMENT-STATUS.md` ภาพฟอนต์/ไฟล์ฉากไม่เปลี่ยน อัปเดต Common ZIP เท่านั้น
