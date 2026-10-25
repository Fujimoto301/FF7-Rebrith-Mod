# สำรองงานม็อดซับไทย FF7 Rebirth

สำรองวันที่ 25 ตุลาคม 2026 (Asia/Bangkok) จาก `E:/FF7RebrithModTH` โดยไม่แก้ไขต้นฉบับ

## สิ่งที่เก็บบน GitHub

- `HANDOFF.md`: สถานะงานและขั้นตอนทำต่อ (ล่าสุด Ch.1–14 + Common)
- `FF7Rebrith/tools`, `translations`, `reference` และเอกสารระดับบน: โค้ด คำแปล ข้อมูลอ้างอิงและการตั้งค่าบิลด์
- `Mod/Final`: ม็อดชุดล่าสุด 9 ZIP ใช้ร่วมกันตาม HANDOFF
- `chats/FF7-Rebirth-chat.md` และ `.json`: บทสนทนาผู้ใช้/ผู้ช่วย 690 ข้อความ ไม่รวม reasoning ภายในหรือ tool output
- `GITHUB-FILES-SHA256.json`: รายการ hash สำหรับไฟล์สำรอง (ไม่รวมตัวรายการนี้และเอกสารนี้)

## สำรองฉบับเต็มบน external SSD

ตำแหน่ง: `E:/ChatFF7Rebrit/backup-20261025-195854`

- `FF7RebrithModTH-full.zip`: สำรองทุกไฟล์ของโฟลเดอร์งาน รวม source, staging และประวัติ QA ใช้ manifest และ objects แบบตัดเนื้อหาไฟล์ซ้ำ ต้องกู้ผ่าน `restore_project.py` ไม่ใช่แตก ZIP อย่างเดียว
- `project-manifest.json`: ตำแหน่งเดิม ขนาด เวลา และ SHA256 ของทุกไฟล์
- `chat-readable`: แชต FF7 และแชตตรวจซ่อม Windows แบบอ่านได้
- `codex-recovery-local-only`: สำเนา rollout ต้นฉบับของแชตสองรายการ พร้อม snapshot ฐานข้อมูล/ข้อมูล sidebar สำหรับกู้คืนโดยผู้เชี่ยวชาญ ไม่มี auth.json และไม่อัปโหลดส่วนนี้ไป GitHub

การนำข้อมูลกู้คืน Codex กลับเข้าแอปไม่ใช่การ import ที่รับประกันโดยแอป ต้องเก็บสำเนาไว้และตรวจเวอร์ชัน/พาธก่อนแทนข้อมูล แอปต้องปิดก่อนกู้คืน ห้ามแทนฐานข้อมูลขณะเปิดแอป

GitHub ชุดนี้ตั้งใจไม่เก็บ source game assets, staging, ประวัติ QA ทุกชุด, สำเนาม็อดเก่า และ runtime ที่ดาวน์โหลดไว้ สิ่งเหล่านี้อยู่ในสำรองฉบับเต็มบน SSD ตามที่ผู้ใช้เลือก ไม่ใช่สำรองคนละดิสก์

การซ่อม Windows: ใช้เฉพาะตัวเลือก Keep personal files and apps; อย่าล้าง external SSD สำรองนี้
