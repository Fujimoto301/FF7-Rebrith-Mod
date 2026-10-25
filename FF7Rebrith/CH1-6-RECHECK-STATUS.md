# ตรวจซ้ำทุกบทที่ทำแล้ว Ch.1–6

<!-- chapter7-current -->
## ล่าสุด: Chapter7 — Those Left Behind (18 ตุลาคม 2026)

ชุดนี้แทนพาธ/ยอด/ขั้นตอนปัจจุบันในประวัติด้านล่าง **26,951รหัส24assets687clusters** รักษา24,999ข้อความ/ACTORของชุดตรวจCh.1–6ครบ เพิ่ม1,688บท/ตัวเลือก +68บทส่วนกลาง +196UI รวม1,952รหัสใหม่ NPCในกลุ่มรหัสNPC372(ไม่มีACTOR342) คัดกลุ่มหลักจาก1,966และพัก278สถานะภายหลัง พร้อมเหตุผลรายรหัส ไม่เริ่มCh.8

ใช้ **E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter7-th.json** เป็นฐานบทถัดไป; stage staging/ThaiJP_ThroughChapter7_Working; config/map reference/chapter7-build.json / through-chapter7-cluster-map.json; QA qa/chapter7 รายละเอียด [CHAPTER7-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER7-STATUS.md)

ผู้ใช้เลือกThaiJP_Chapter6_7_P.zipแทนChapter6เดิม เพราะCORLEร่วมกัน Final5ZIPล่าสุดคือChapter1/Chapter2/Chapter3_4_5/Chapter6_7/Common ต้องใช้ร่วมกัน อีก3ZIPแรกคงเดิม อ่านกลับรวม24assetsผ่าน ไม่มีทับกัน สำรองของเก่านอกFinal ไม่ได้ติดตั้ง/เล่นทดสอบจริง/ฟังวิดีโอครบใหม่

build chain: assemble_chapter7.py → build_chapter7.py --text-only(เฉพาะglyphไม่เพิ่ม; หากเพิ่มbuildเต็ม) → build_chapter7.py --verify → audit_chapter7.py → audit_chapter7_glyph_regression.py → audit_gender_through_chapter7.py → audit_shared_dialogs.py → preview_chapter7.py(ดูภาพ) → publish_final_parts.py → finalize_chapter7.py ห้ามprepareซ้ำ/เปลี่ยนindex/ใช้auditบทเก่าทับactive context หลังแก้คำแปลตรวจและอัปเดตqa/chapter7/editorial-signoff.jsonซึ่งผูกhashก่อนfinalize

ตรวจ53system +4คำถามซิตอัปในchoice-review, UIหมวดCorel/ร้าน/ของเควสต์/เหมือง/ซิตอัปทั้งหมวด337รหัสรวมเดิมและบทเสริม Shared gateตอนนี้ตรวจ1,555UIต้นฉบับญี่ปุ่น NPCเช่าChocobo/ชุดว่ายน้ำ/ยิม60และช่างภาพ8ที่พักไว้เดิมเข้ามาแล้ว อย่านับว่ายังค้างทั้งหมดตามตัวเลขเก่าของCh.6

คำลงท้ายจริง609ครั้งใน594รหัส ชาย408/หญิง201 ไม่มีสลับเพศหรือผู้พูดคำลงท้ายไม่ยืนยัน UnknownNPCกลาง หลักฐานAminaเป็นสมาชิกหญิงอยู่ในJP และTerrified WomanมีJP ACTORระบุหญิง ใช้ชื่อไทยในบทพูด ป้ายUSอังกฤษ คงชื่อบาร์เร็ต/โกลด์ซอซเซอร์/โชโคโบะตามเดิม ชื่อใหม่JPคลาปิโย/ชีรอน/นาบาราไม่อ้างว่าPlearnรับรอง

คง677glyph assignment/metricsเดิม เพิ่ม10เป็น687 nativeASCII/เลข/ไอคอนคงเดิม …ยังระดับล่างครบ8fonts atlasไทยrepackBC5มีmaskต่างเล็กน้อย ไม่อ้างว่าไทยเดิมพิกเซลตรงทุกจุด

ทุกบทต้องตรวจทั้งคำถามและทุกตัวเลือกพร้อมข้อความResident/NPCไม่มีACTOR/namespaceข้างเคียง ยกเลิก ลองใหม่ ผลชนะแพ้ ร้าน ของเควสต์ ตามข้อกำหนดถาวรเดิม บทหลังCosmo Canyon/ทะเลทราย/โรงแรมปรับปรุง/ปฏิกิริยาสงครามแยกพร้อมเหตุผล ไม่เติมเรื่องCh.8ขึ้นไปโดยอ้างว่าCh.7ครบ
<!-- /chapter7-current -->

อัปเดต 18 ตุลาคม 2026 (Asia/Bangkok) ตามคำสั่งให้ตรวจทุกบทด้วยเกณฑ์เดียวกับภาพตกหล่น Ch.1–2

ชุดล่าสุด **24,999รหัส / 24assets / 677glyph clusters** รักษาชุดก่อนหน้า24,180รหัสและACTORครบ เพิ่ม **701รหัส UI + 118รหัสบท/ตัวเลือกระบบส่วนกลาง** เก็บเฉพาะเหตุการณ์ของบทที่ทำแล้ว ไม่เริ่มCh.7–14

## ตรวจบทเดิมครบตามขอบเขตทั้ง6บท

| บท | รหัสเดิมที่ตรวจซ้ำ | NPCในกลุ่มรหัสNPC | กันสถานะภายหลัง |
| --- | ---: | ---: | ---: |
| Ch.1 | 1,157 | 336 | 0 |
| Ch.2 | 2,876 | 577 | 52 |
| Ch.3 | 253 | 0 | 0 |
| Ch.4 | 3,206 | 890 | 50 |
| Ch.5 | 1,316 | 581 | 0 |
| Ch.6 | 1,698 | 698 | 107 |

รวม **10,506รหัสบทเดิม** เทียบJPต้นฉบับกับstagingรายรหัส ทั้งข้อความ แท็ก ตัวแปร เมทาดาทา ACTORภาษาอังกฤษ และคำลงท้าย ตรวจNPCที่ไม่มีACTORด้วย จำนวนNPCในตารางนับเฉพาะรหัสกลุ่มNPC ไม่ใช่ตัวละครนอกปาร์ตี้ทุกประเภท สแกนcorpusอิสระตามกลุ่มฉาก/เควสต์/NPCอีก **10,287candidateIDs** เพื่อไม่ตรวจเฉพาะรายการเก่าที่อาจคัดไม่ครบ สองจำนวนนี้ครอบคลุมต่างกัน จึงไม่ควรนำมาบวกเป็นจำนวนบท

Ch.3หลังออกเหมือง14รหัสซึ่งเคยพักไว้ ได้อยู่ในCh.4แล้วครบ ส่วน209รหัสที่ยังกันไว้เดิมคือCh.2จำนวน52, Ch.4จำนวน50, Ch.6จำนวน107 มีเหตุผลเหตุการณ์หลังกลับพื้นที่และยังคงJPดั้งเดิมในasset ไม่แอบนับว่าแปลแล้ว สรุปเปิดเกม39บรรทัดที่เก็บในรอบก่อนยังอยู่ครบ

ตรวจตัวเลขเชิงความหมาย54จุดที่รูปเขียนไม่ตรงกัน เช่น 2,000/2000, วันที่สลับลำดับและเดือนภาษาไทย, เลขคันจิของเซคเตอร์/หน่วยทหาร, คำเรียกคลาสSOLDIER, “ทั้งคู่/สักแก้ว/อีกครั้ง” และสำนวน “วันดีๆ” คงความหมาย ไม่บังคับเปลี่ยนสำนวนทั้งหมดเป็นตัวเลข ดูnumber-review.json

## ส่วนที่พบและแปลเพิ่ม

- **701UI**: เมนู/กล้อง/คำสั่ง/ผลลัพธ์Fort Condor รวม namespace CF, จัดแถวและปุ่มพาเหรดJunon, โลมา/กบ, คำถามยอมแพ้/ลองใหม่/รางวัลร่วม, วิเคราะห์คริสตัลอัญเชิญ, ขุดค้นด้วยChocobo, รายงานสำรวจGrasslands/Junonและเงื่อนไขร่วม, หน้ารายงานช่างภาพ, ร้านค้า/ตู้ขายของในพื้นที่Ch.1–6, คำบรรยายการ์ดและแพ็กการ์ด, คำบรรยายของเควสต์Junonและการ์ดชุดชายหาด
- ตรวจUIตามหมวดรวม **895รหัส** (746รหัสชุดหลัก +149รหัสnamespaceข้างเคียง) รวมข้อความเดิม/อังกฤษ/สัญลักษณ์ที่คงไว้ด้วย มีตัวเลือกต่างสถานะครบตามหมวดที่ลงทะเบียน ไม่ตัดเฉพาะภาพที่ได้รับ ชื่อร้าน/ไอเทม/สกิล/การ์ด/พื้นที่/รูปแบบการแสดงเป็นอังกฤษUSทางการ ส่วนข้อความทั่วไปเป็นไทย รายงานคงชื่อเรื่องเฉพาะUSและแปลหัวชนิดรายงาน
- **118บท/ตัวเลือก** ที่หลุดเพราะอยู่Resident: ช่างภาพSnaps(ชื่อJPโฟกัส) ในGrasslands38, Junon16, Costa17 รวม71รหัส; ผู้ดูแลเปียโนDorian(ชื่อJPปิอาโซลา)/ตัวเลือก/เสียงผู้ชม47รหัส รวม3คำถามและตัวเลือกระบบ ใช้ชื่อไทยเมื่ออยู่ในประโยคและป้ายอังกฤษตามUS ไม่มีการเติมคำลงท้ายที่ระบุเพศให้ผู้พูดที่ยังไม่ยืนยัน เสียงผู้ชม24รหัสใช้กลาง ไม่เดาเพศจากmma/mfa
- แยกshared NPCสถานะภายหลังใหม่ **44รหัส**: แรงก์ช่างภาพหลังสองภูมิภาค24, โรงแรมJohnnyปรับปรุง3, รายงานจุดถ่ายภาพชายฝั่งหลังออกCosta5, รางวัลครบเพลง/เรื่องราวหลังเก็บโน้ตเพลงครบ12 เหตุผลในreference/ch1-6-recheck-deferred.json ไม่ใส่บทเหล่านี้เพื่ออ้างว่าCh.6ครบ
- UIร่วมที่มีรายชื่อระดับ/อัญเชิญ/การ์ดของช่วงหลังแปลทั้งหมวดตามนโยบายUIเดิม แต่ไม่ได้เพิ่มบทพูดของCh.7–14หรือบทของNPCในพื้นที่ใหม่

## เพศ ชื่อ และฟอนต์

ตรวจคำลงท้ายจริงทั้งชุดปัจจุบัน **477ครั้งใน467รหัส: ครับ335 ค่ะ83 คะ59** ชาย335/หญิง142 ไม่มีสลับเพศหรือผู้พูดคำลงท้ายที่ไร้หลักฐานในชุดตรวจ ใช้หลักฐานรายรหัสเดิม/ตัวละครที่ยืนยันและJPบริบท ไม่เดาจากโค้ดNPC คงเสียงติดอ่างคะ…ในคะ…ครับ!เป็นข้อยกเว้น ไม่ได้นับเป็นคำลงท้ายหญิง บทใหม่118รหัสใช้ถ้อยคำกลางทั้งหมด ไม่อ้างว่าฟังNPCทุกคนใหม่

ชื่อเฉพาะในบทพูดไทย ในUI/ACTORอังกฤษ เลขอารบิกเมื่อเป็นค่าชัดเจน Wutai=อู่ไถในบทพูด Red XIIIใช้เรดตามJPปัจจุบันตามกฎเดิม ศัพท์ใหม่โฟกัส/ปิอาโซลาเป็นการถอดจากJP ไม่อ้างว่าPlearnรับรอง ชื่ออังกฤษSnaps/DorianมาจากUSรหัสเดียวกัน

เพิ่มglyph3กลุ่มแบบappend-only **พ็/ฟิ้/อึ้** จาก674เป็น677 รหัสเก่าคงเดิมและmetricsเก่าครบ674กลุ่มทั้ง8ฟอนต์ สร้างฟอนต์เต็มเพื่อเพิ่มglyph: textureไทยถูกจัดวางและบีบอัดBC5ใหม่ จึงมีความต่างเล็กน้อยของmaskไทยเดิม(ไม่อ้างว่าไบต์เดิมทุกพิกเซล) แต่ตัวASCII/เลข/ไอคอนต้นฉบับยังคงพิกเซลและmetricsเดิมตามverifier เส้นฐานภาษาไทย/ASCII/เลขและจุดไข่ปลา…ระดับล่างตรวจผ่านทั้ง8ฟอนต์

ภาพproof4หน้าจากglyphstagingจริง ตรวจภาพแล้ว รวมปุ่มสมมติ[X], ชื่อEther/1072 EXP/12 APที่แทนหลังencode และglyphใหม่ เป็นการจัดบรรทัดสำหรับproof ไม่ใช่ขนาดแผงในเกม ยังไม่ได้เล่นทดสอบการตัดบรรทัดหรือฟังวิดีโอใหม่ครบทุกบรรทัด

## ไฟล์สำหรับทำต่อ

พาธฐาน **E:/FF7RebrithModTH/FF7Rebrith/**:

| งาน | พาธใต้ฐาน |
| --- | --- |
| ชุดรวมล่าสุด | translations/working-ch1-6-recheck-th.json |
| JP/US UI/แม่แบบ/ส่วนข้างเคียง | reference/ch1-6-recheck-ui-source.json, ch1-6-recheck-ui-templates.json, ch1-6-recheck-extra-source.json |
| คำแปลUIและสคริปต์ที่ต้องแก้ให้ตรงกัน | translations/ch1-6-recheck-ui-th.json, ch1-6-recheck-extra-th.json; tools/translate_ch1_6_ui.py, translate_ch1_6_reports.py, extend_ch1_6_recheck.py |
| บทใหม่/สถานะภายหลัง | reference/ch1-6-recheck-speech-source.json, ch1-6-recheck-deferred.json; translations/ch1-6-recheck-speech-th.json; tools/translate_ch1_6_speech.py |
| config/glyph/stage | reference/ch1-6-recheck-build.json, ch1-6-recheck-cluster-map.json, dialogue-punctuation-policy.json; staging/ThaiJP_Ch1_6_Recheck_Working |
| snapshotห้ามทับ | qa/ch1-6-recheck/baseline.json และ revisions/ |
| หลักฐานบททุกบท/corpus/ตัวเลข | qa/ch1-6-recheck/chapter-records.json, corpus-scope-scan.json, number-review.json, existing-deferred-review.json |
| หลักฐานUI/NPCใหม่/เพศ | qa/ch1-6-recheck/ui-review.json, shared-dialogue-review.json, gender/summary.json, gender/records.json |
| ฟอนต์/ภาพ/แพ็ก | qa/ch1-6-recheck/verification.json, old-glyph-regression.json, proof-1.png ถึง proof-4.png, release-verification.json |
| ขอบเขตถาวร/ผลตรวจร่วม | tools/audit_shared_dialogs.py, qa/shared-dialogs/latest.json |
| manifestและactive context | qa/active-working-set.json, qa/final-parts/latest.json, combined-mount-verification.json |

ใช้Python `C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` และ `$env:PYTHONUTF8='1'` จากโปรเจกต์:

```text
tools/assemble_ch1_6_recheck.py
tools/build_ch1_6_recheck.py --text-only
tools/build_ch1_6_recheck.py --verify
tools/audit_ch1_6_recheck.py
tools/audit_ch1_6_glyph_regression.py
tools/audit_gender_through_chapter6.py --active
tools/audit_shared_dialogs.py
tools/preview_ch1_6_recheck.py
tools/publish_final_parts.py
tools/finalize_ch1_6_recheck.py
```

--text-onlyใช้เมื่อไม่เพิ่มglyphและมีผลbuild8fontsอยู่แล้ว ถ้าเพิ่มglyphต้องbuildเต็ม รักษาmapเก่าและการปรับU+2026หลังจัดแนว ห้ามprepareซ้ำ/เปลี่ยนindex/เขียนทับbaseline อย่ารันauditหรือfinalizeบทเก่าทับactive context สำหรับบทถัดไปให้ใช้working-ch1-6-recheck-th.jsonเป็นฐาน

ทุกบทถัดไปต้องตรวจshared Residentและnamespaceข้างเคียงควบคู่ฉาก ทั้งคำถามบทสอน/เริ่มกิจกรรม/ใช่ไม่ใช่/ยกเลิก/ลองใหม่/เมนูย่อย/HUD/คำบรรยายของเควสต์/ร้านค้า ไม่ตรวจแค่*_sys ใส่familyใหม่ลงaudit_shared_dialogs.pyก่อนส่งงาน และตรวจชื่อ/เพศ/ตัวเลข/ellipsisตามเดิม

## ZIPและข้อจำกัด

Finalมี5ZIPล่าสุดของChapter1/Chapter2/Chapter3_4_5/Chapter6/Common ต้องใช้ร่วมกันทั้งหมด รอบนี้เปลี่ยนเฉพาะ **ThaiJP_Common_P.zip**(18assets: Resident/TITLB/8fonts/8textures) ZIPฉากทั้ง4ไม่เปลี่ยน อ่านกลับ5ZIPร่วมกันรวม15mod files24assetsผ่าน ไม่มีassetทับกัน สำรองCommonเก่านอกFinalตามmanifest

ต้นฉบับเกม/distเดิม/ม็อดในเกมไม่เปลี่ยน ไม่ได้ติดตั้ง ไม่ได้เล่นทุกทางเลือกหรือทวนเสียงวิดีโอครบใหม่ การตรวจนี้ยืนยันความครบตามscopeและหมวดที่ลงทะเบียนจากไฟล์ ไม่ใช่คำยืนยันว่าทุกtriggerในเกมถูกทดลองแล้ว

แหล่งที่ผู้ใช้ให้สำหรับจับคู่บท/ภาพผู้พูด: [คลิปหลัก](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk) ห้ามถือauto transcriptเป็นหลักฐานว่าฟังครบ ห้ามแต่งtimestampใหม่
