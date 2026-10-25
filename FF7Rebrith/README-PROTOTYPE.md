# FF7 Rebirth — ต้นแบบซับไทย + เสียงญี่ปุ่น

> เก็บไว้เพื่ออ้างอิงเท่านั้น ไม่แนะนำให้ติดตั้งต้นแบบรุ่นนี้ การแก้การจัดวาง glyph และการตรวจฟอนต์ล่าสุดอยู่ในรุ่น Chapter 1 ให้ใช้ `README-CHAPTER1.md` และ `dist/ThaiJP_Chapter1_P.zip`

**สถานะ: ต้นแบบแปลสรุปเรื่องราวภาคก่อน (Story So Far) 39 ข้อความ ยังไม่ใช่ม็อดแปลทั้งเกม และยังไม่ได้ทดสอบขณะเล่นเกม**

ไฟล์พร้อมทดลองอยู่ใน `dist/ThaiJP_Prototype_P.zip` และโฟลเดอร์ `dist/ThaiJP_Prototype_P` ตรวจอ่านแพ็กกลับแล้วครบ 17 assets ตรงกับไฟล์ที่เตรียมไว้

## ขอบเขตต้นแบบ

- แปลจากข้อความญี่ปุ่น โดยใช้คำเรียกจากม็อด Remake ของ PlearnGaming ที่ผู้ใช้ให้มาเป็นบริบท
- คงชื่อในป้ายผู้พูดและ UI ตามต้นฉบับ ถอดชื่อเป็นไทยเฉพาะที่อยู่ในประโยคบทพูด
- เพิ่มตัวอักษรไทยจาก Sarabun ในฟอนต์ญี่ปุ่น 8 ขนาด พร้อม texture 8 ไฟล์ คง glyph เดิมและไอคอนเดิม
- ต้นแบบแทนข้อความในช่องภาษา **ญี่ปุ่น** เมนูและฉากอื่นที่ยังไม่ได้แปลจึงยังเป็นภาษาญี่ปุ่น
- ไฟล์เสียงไม่ได้ถูกแก้ไข ให้เลือกเสียงญี่ปุ่นในเกม

## ทดลองใช้งาน

1. ปิดเกมก่อน และแตก ZIP ไปยังโฟลเดอร์ชั่วคราว
2. นำไฟล์ทั้งสามนี้ไปไว้ใน `E:\steam\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks\~mods` สร้างโฟลเดอร์ `~mods` ถ้ายังไม่มี
   - `ThaiJP_Prototype_P.pak`
   - `ThaiJP_Prototype_P.utoc`
   - `ThaiJP_Prototype_P.ucas`
3. ในเกมเลือกภาษาข้อความเป็น **Japanese** และเสียงพากย์เป็น **Japanese**
4. เปิดสรุปเรื่องราวภาคก่อน / Story So Far จากเมนูเกม เพื่อตรวจข้อความไทย 39 รายการ
5. ตรวจว่าสระและวรรณยุกต์ครบ ซับไม่ถูกตัด และชื่อในป้ายยังคงเดิม หากมีม็อดอื่นแก้ข้อความญี่ปุ่นหรือ SystemFont เดียวกัน ให้ทดสอบต้นแบบนี้โดยไม่มีม็อดเหล่านั้นเพื่อแยกผล

ยังไม่ได้ติดตั้งต้นแบบลงในโฟลเดอร์เกมโดยอัตโนมัติ การถอนต้นแบบทำได้โดยลบเฉพาะไฟล์ชื่อ `ThaiJP_Prototype_P` ทั้งสามไฟล์ออกจาก `~mods`

## ไฟล์สำหรับทำงานต่อ

- `translations/prototype-th.json` — คำแปลไทยที่แก้ไขได้
- `reference/prototype-jp.json` — ต้นฉบับญี่ปุ่นของฉากต้นแบบ
- `reference/plearngaming/glossary.json` — คำศัพท์และหลักฐานจากม็อดอ้างอิง
- `TRANSLATION_GUIDE.md` — ข้อกำหนดชื่อและแนวทางแปล
- `qa/subtitle-preview.png` — ภาพจำลองจาก atlas ที่สร้างจริง เป็นภาพตรวจฟอนต์ ไม่ใช่ภาพจากเกม
- `qa/build-verification.json`, `qa/font-verification.json`, `qa/package-verification.json`, `qa/text-preservation.json` — ผลตรวจไฟล์

ข้อมูล Remake ถอดข้อความอ้างอิงได้แล้ว ส่วน Crisis Core แตกแพ็ก Atel ได้ แต่ยังถอดข้อความไม่สำเร็จ จึงยังไม่อ้างว่าใช้บริบทจากทั้งสองภาคได้ครบ

## สร้างต้นแบบซ้ำ

ใช้ PowerShell จากโฟลเดอร์นี้ หลังแก้คำแปลให้สร้างฟอนต์และแพ็กใหม่ตามลำดับ:

```powershell
& 'C:\Users\godca\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/build_prototype.py
& 'C:\Users\godca\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/verify_text_preservation.py
& 'C:\Users\godca\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/pack_prototype.py
& 'C:\Users\godca\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/package_release.py
```

เครื่องมือและ Python libraries อยู่ในโปรเจกต์นี้และ `..\tools` ขั้นตอนแตกไฟล์เกมคือ `tools/extract_game.py` การแพ็กใช้ Oodle และการปรับ flag เฉพาะ Rebirth ตาม [คำแนะนำของผู้ดูแล UnrealReZen](https://github.com/rm-NoobInCoding/UnrealReZen/issues/58)

## เครดิต

PlearnGaming เป็นแหล่งอ้างอิงคำศัพท์จากม็อดที่ผู้ใช้ให้มา งานนี้ไม่ใช่ผลงานทางการหรือการรับรองของทีม ฟอนต์ไทยใช้ Sarabun จาก Google Fonts ตาม SIL Open Font License ซึ่งรวมไว้ในแพ็ก เครื่องมือภายนอกและใบอนุญาตเก็บไว้ใน `tools`
