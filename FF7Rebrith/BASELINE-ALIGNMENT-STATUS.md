# แนวภาษาไทย อังกฤษ และตัวเลขที่เกมเติมภายหลัง

แก้ตามภาพ `ได้รับ Ether` และผลต่อสู้ `Velociwing / EXP / AP / กิล` วันที่ 16 ตุลาคม 2026

ชื่อและจำนวนที่เกมแทนใน `<object>` / `<count>` หลังอ่านข้อความยังเป็น ASCII เดิม จึงไม่ผ่าน aliases ที่เคยจัดแนวกับไทย การแก้รอบนี้ย้ายแนวตั้งของ Thai clusters ให้ตรงขอบหมึก ASCII H เดิมในแต่ละฟอนต์ พร้อมคืน Latin aliases ให้ใช้ origin เดียวกับ ASCII และจัด digit aliases ให้ตรงแนวเดียวกัน อักษรหางลงล่างยังคงตำแหน่งตามธรรมชาติ ตัวเลข native คง optical overshoot เดิมไม่เกิน 2 พิกเซลในฟอนต์ 4K

| ฟอนต์ | ย้ายไทยลงจากรุ่นก่อน (พิกเซล) |
| --- | ---: |
| Large / Large4K | 5 / 9 |
| Normal / Normal4K | 3 / 6 |
| Small / Small4K | 2 / 2 |
| XLarge / XLarge4K | 7 / 10 |

เปลี่ยนเฉพาะค่าแนวตั้งใน font metadata 8 assets ข้อความทั้งหมด 17,178 รหัส, glyph map, ภาพฟอนต์, รูปทรง, ขนาด, ระยะแนวนอน, glyph ASCII เดิม และไอคอนคงเดิม ตำแหน่งสระ/วรรณยุกต์กับพยัญชนะขยับพร้อมกัน

ไฟล์และขั้นตอนสำหรับทำต่อ (ทั้งหมดใต้ `E:/FF7RebrithModTH/FF7Rebrith`):

- `reference/native-baseline-policy.json` — นโยบายที่ build ล่าสุดใช้อัตโนมัติ
- `tools/align_dynamic_baselines.py` — ฟังก์ชัน `align_fonts` ถูกเรียกจาก `build_chapter1.py --ui-completion-working` ทั้งแบบเต็มและ `--text-only`; main เป็นงาน snapshot ครั้งเดียว ห้ามรัน main ซ้ำทับ baseline
- `qa/baseline-alignment/baseline.json` — พาธ snapshot ก่อนแก้สำหรับเปรียบเทียบ
- `tools/audit_dynamic_baselines.py` — ตรวจรอบนี้อย่างเข้มงวดว่าเปลี่ยนเฉพาะ y origin และจำลองแทน ASCII หลัง encode; การตรวจเทียบ snapshot นี้ใช้เมื่อข้อความและ glyph map ยังตรงกับรอบนี้ หากขยายข้อความในอนาคตให้รักษา snapshot ประวัติและสร้าง regression ที่เหมาะสม
- `qa/baseline-alignment/audit.json` และ `alignment.json` — ผลตรวจ 8 ฟอนต์
- `qa/baseline-alignment/runtime-substitution-proof.png` — ภาพก่อน/หลังจาก glyph จริง รวม Ether, Velociwing A/B, 1072 EXP, 12 AP, 506 กิล และ Mega-Potion ×3 เป็นภาพจำลอง ไม่ใช่ภาพในเกม

ผ่าน `verify_chapter1.py --ui-completion-working`, `audit_ui_completion.py`, `audit_dynamic_baselines.py`, `audit_enemy_names.py` และ `audit_ui_piano_notifications.py` แล้ว แพ็ก Common และอ่านกลับ 17 assets จากนั้นเปิด 3 แพ็กร่วมกันยืนยัน 21 assets ไม่ซ้ำและตรง staging

อัปเดตเฉพาะ `E:/FF7RebrithModTH/Mod/Final/ThaiJP_Common_P.zip` ส่วน Chapter1/2 ZIP เดิมไม่เปลี่ยน ยังต้องใช้ทั้ง 3 ZIP ร่วมกัน ไม่ได้ติดตั้งหรือทดสอบเล่นในเกมจริง ควรตรวจตำแหน่งข้อความและขอบกล่องจริงจากจุดในภาพผู้ใช้หลังติดตั้ง
