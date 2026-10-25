# ตรวจ Ch.1–2 และแก้จุดไข่ปลา

<!-- all-completed-chapters-current -->
## ล่าสุด: ตรวจซ้ำครบ Ch.1–6 — 18 ตุลาคม 2026

ส่วนนี้แทนพาธ/ยอด/ขั้นตอนปัจจุบันในประวัติด้านล่าง ตรวจบทเดิม10,506รหัสครบทั้ง6บทและสแกนcorpusอิสระ10,287candidateIDs เก็บตกใหม่701UI+118บท/ตัวเลือกส่วนกลาง รวม **24,999รหัส24assets677clusters** คง24,180รหัส/ACTORเดิมครบ กัน209สถานะภายหลังเดิมและ44shared NPCสถานะภายหลังใหม่ มีเหตุผลรายรหัส ไม่เริ่มCh.7

ชุดรวมล่าสุด **E:/FF7RebrithModTH/FF7Rebrith/translations/working-ch1-6-recheck-th.json**; staging **staging/ThaiJP_Ch1_6_Recheck_Working**; glyph/config **reference/ch1-6-recheck-cluster-map.json / ch1-6-recheck-build.json**; QA **qa/ch1-6-recheck** ใช้เป็นฐานบทต่อไป รายละเอียดครบที่ [CH1-6-RECHECK-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CH1-6-RECHECK-STATUS.md)

build chainล่าสุด: assemble_ch1_6_recheck.py → build_ch1_6_recheck.py --text-only(เมื่อglyphไม่เพิ่ม) → build_ch1_6_recheck.py --verify → audit_ch1_6_recheck.py → audit_ch1_6_glyph_regression.py → audit_gender_through_chapter6.py --active → audit_shared_dialogs.py → preview_ch1_6_recheck.py(ดูภาพ) → publish_final_parts.py → finalize_ch1_6_recheck.py ห้ามprepareซ้ำ/เปลี่ยนindex/เขียนทับsnapshot/ใช้auditหรือfinalizeบทเก่าทับactive context

UIใหม่ครอบคลุมFortCondor/CF, พาเหรด, โลมา/กบ, วิเคราะห์อัญเชิญ/ขุดค้น, รายงานGrasslands/Junon, การ์ด/แพ็ก, ร้าน/ตู้ขายของ และของเควสต์ บทใหม่ช่างภาพSnaps(โฟกัส)กับDorian(ปิอาโซลา)/เสียงผู้ชมคงป้ายUSอังกฤษ พูดชื่อไทย UnknownNPCกลาง ผลคำลงท้ายจริง477ครั้งใน467รหัส(ครับ335/ค่ะ83/คะ59) ไม่มีสลับเพศตามหลักฐานที่เก็บ ไม่อ้างว่าฟังวิดีโอทุกคนใหม่

เพิ่มglyph3clusterพ็/ฟิ้/อึ้แบบappend-only รักษา674assignment/metricsเดิมและnativeASCII/เลข/ไอคอนพิกเซลเดิม การrepackBC5ทำให้maskไทยเดิมต่างเล็กน้อย ไม่อ้างว่าไบต์ไทยเดิมครบ ฟอนต์8ชุดยังคงจุดไข่ปลา…ระดับล่างตามภาพผู้ใช้และnative period baseline

**ทุกบทต่อไปต้องตรวจshared UIและNPCที่ไม่ได้อยู่ในรหัสฉาก**: บทสอน/คำถาม/ใช่ไม่ใช่/ยกเลิก/ลองใหม่/กิจกรรมทั้งหมวด/HUD/ร้าน/ของเควสต์และnamespaceข้างเคียง ใส่familyลงaudit_shared_dialogs.py ตรวจชื่อ/ตัวเลข/เพศ/ellipsisพร้อมกัน อย่าพึ่ง*_sysหรือเลขChapterอย่างเดียว

Finalมี5ZIPต้องใช้ร่วมกันทั้งหมด อัปเดตเฉพาะCommon ZIPบททั้ง4คงเดิม อ่านกลับรวม24assetsผ่านไม่มีทับกัน สำรองนอกFinal ยังไม่ได้ติดตั้ง/เล่นทดสอบจริง/ดูเสียงครบใหม่ ข้อมูลบทเก่าในส่วนถัดไปเป็นประวัติ
<!-- /all-completed-chapters-current -->

อัปเดต 18 ตุลาคม 2026 (Asia/Bangkok) ตามภาพ113848/114018/161004/122833ของผู้ใช้

ชุดล่าสุดรวม **24,180รหัส / 24assets / 674glyph clusters / 5ZIP** รักษาคำแปลเดิม23,811รหัสและACTORทุกจุด เพิ่มUI330รหัสกับสรุปเปิดเกม39บรรทัด ไม่เริ่มCh.7 ไม่ติดตั้งเกม

## ผลตรวจและสิ่งที่แก้

- ลด **… U+2026** ทั้ง8ฟอนต์ให้ขอบล่างหมึกเสมอกับจุดASCII `.` จึงตรงแนวตัวอักษรไทยตามภาพตัวอย่าง เปลี่ยนเฉพาะค่าoriginYของglyphนี้ คงภาพจุด ระยะกว้าง ตัวASCII/เลข/ไอคอน/Thai glyph/textureทุกส่วนเดิม แก้ทั้งข้อความที่มีอยู่แล้ว80ตำแหน่งโดยไม่ต้องเปลี่ยนประโยค ไม่ได้เปลี่ยนU+2025ที่ยังไม่ใช้
- ต้นเหตุคำถามสอนการ์ดที่ตกหล่นคือ Resident `$minigame_cardgame_tutorial_Check` ไม่อยู่ในรหัสฉาก `*_sys` เก็บทั้งคำถาม “ต้องการดูบทสอนเล่น Queen's Blood หรือไม่?” ตัวเลือกใช่/ไม่ใช่ เมนูเด็ค ปุ่ม/ยอมแพ้/ลองใหม่/จัดการการ์ด/คำบรรยายเด็คและการแจ้งเตือนพร้อมกัน
- ตรวจUIทั้งหมวด362รหัส: เพิ่ม330 คงเดิม31รหัสภาษาอังกฤษ/ตัวเลข/สัญลักษณ์ และคงคำแปลเดิม1รหัส ครอบคลุมQueen's Blood, จับChocobo, Moogle Mischief, ชื่อคู่แข่ง/ร้าน/แจ้งเตือน และหลักสูตรฝึกต่อสู้ รวมตัวเลือกต่างสถานะ ไม่ตัดเฉพาะสิ่งที่เห็นในภาพ ชื่อเฉพาะ/ไอเทม/การ์ด/UIคงชื่อUSอังกฤษ รักษาแท็กJPและค่าตัวเลขโดยนับゼロเป็น0
- ตรวจรายการCh.1–2เดิมทั้งหมด4,085รหัส: ที่ใส่แล้ว4,033ครบ และ52รหัสสถานะภายหลังยังกันไว้พร้อมเหตุผลรายรหัส ตรวจcorpusอิสระอีก3,657candidateIDsตามกลุ่มฉาก/NPC/เควสต์ของCh.1–2 พบสรุปเปิดเกม39บรรทัดที่หลุดอยู่ในไฟล์TITLB จึงแปลเพิ่มครบ เนื้อหาพากย์โดยRed XIII ใช้ชื่อไทยในประโยคและถ้อยคำกลาง ฉัน/พวกเรา ไม่เติมคำลงท้ายระบุเพศ
- ช่วงท้ายCh.1/เปลี่ยนผ่านC1920และเนื้อเรื่องC2010 รวมNPC/บทแวดล้อม/ตัวเลือกระบบและshared rowsที่มีในscopeเดิมได้รับการตรวจซ้ำ ไม่พบJPเหลือในขอบเขตนี้ จำนวนcandidateอิสระไม่ใช่จำนวนบททั้งเกม และการไม่มีรหัสขาดไม่ได้พิสูจน์เงื่อนไขเรียกบททุกแบบจากการเล่นจริง
- ไม่เอาสถานะกลับGrasslandsหลังGoldSaucer/Nibel/GoldCup, Kalmระยะหลัง, เควสต์ทดแทนเมื่อBrodenไม่อยู่ หรือTifaแยกปาร์ตี้ช่วงหลัง มาปะปนกับCh.2 ดู52deferredเดิมและขอบเขตคัดsource ส่วนบท/UIนอกหมวดที่ระบุไม่ได้อ้างว่าเสร็จครบทั้งเกม
- คำลงท้ายเดิมยัง477ครั้งใน467รหัส (ครับ335/ค่ะ83/คะ59) UI/สรุปใหม่ไม่มีคำลงท้ายระบุเพศ ตรวจรักษาถ้อยคำเดิมครบ ไม่เดาเพศจากsuffix NPC และไม่ได้ดู/ฟังวิดีโอใหม่ครบ

## ไฟล์ปัจจุบัน

ฐาน **E:/FF7RebrithModTH/FF7Rebrith/**:

| หน้าที่ | พาธใต้ฐาน |
| --- | --- |
| ชุดรวมปัจจุบัน | translations/working-ch12-recheck-th.json |
| UIต้นฉบับJP/US/คำแปล | reference/ch12-recheck-ui-source.json, translations/ch12-recheck-ui-th.json |
| สรุปเปิดเกมJP/ไทย | reference/ch1-opening-recap-source.json, translations/ch1-opening-recap-th.json |
| สร้างคำแปล/รวม | tools/translate_ch12_recheck.py, translate_ch1_recap.py, assemble_ch12_recheck.py |
| config/glyph/punctuation | reference/ch12-recheck-build.json, ch12-recheck-cluster-map.json, dialogue-punctuation-policy.json |
| stage/active context | staging/ThaiJP_Ch12_Recheck_Working, qa/active-working-set.json |
| baselineห้ามทับ | qa/ch12-recheck/baseline.json และ revisions/ |
| ตรวจทวน4,033/52/3657 | qa/ch12-recheck/chapter1-2-records.json, deferred-later-states.json, corpus-scope-inventory.json |
| QAคำแปล/ฟอนต์/เพศ | qa/ch12-recheck/translation-audit.json, verification.json, punctuation-alignment.json, ui-review.json, opening-recap-review.json, gender-summary.json |
| proofจากglyphจริง(ไม่ใช่ในเกม) | qa/ch12-recheck/ellipsis-before-after.png, ui-proof-1.png ถึง ui-proof-3.png, proof.json |
| ตรวจshared UIถาวร | tools/audit_shared_dialogs.py, qa/shared-dialogs/latest.json |
| ชุดส่งมอบ | qa/ch12-recheck/release-verification.json, qa/final-parts/latest.json, combined-mount-verification.json |

## สร้างซ้ำและทำบทต่อไป

ใช้Python `C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` ตั้ง `$env:PYTHONUTF8='1'` จากโปรเจกต์:

```text
tools/assemble_ch12_recheck.py
tools/build_chapter1.py --ch12-recheck-working --text-only
tools/verify_chapter1.py --ch12-recheck-working
tools/audit_ch12_recheck.py
tools/audit_shared_dialogs.py
tools/preview_ch12_recheck.py
tools/publish_final_parts.py
tools/finalize_ch12_recheck.py
```

เมื่อแก้ข้อความให้ดูภาพproofด้วย ถ้าเพิ่มglyphต้องbuildเต็มโดยเอา--text-onlyออก รักษาmapแบบappend-only อย่ารันprepare_ch12_recheck.pyซ้ำ อย่าใช้finalize/auditบทเก่าทับactive context สำหรับบทถัดไปใช้working-ch12-recheck-th.jsonเป็นฐานและคงการปรับU+2026หลังจัดแนวฟอนต์ รักษาข้อมูลเดิมทุกส่วน

**หลังจากนี้ต้องตรวจทุกบท:** สแกนshared Residentควบคู่ฉาก ไม่พึ่งเลขChapterหรือ*_sysอย่างเดียว ตรวจคำถามเริ่มบทสอน/ใช่ไม่ใช่/ยกเลิก/ย้อนกลับ/ลองใหม่/หน้าถัดไป/คำอธิบายและHUDของกิจกรรมที่เปิดในบทนั้นทั้งหมวด ใส่familyใหม่ในaudit_shared_dialogs.pyก่อนส่งงาน ตรวจellipsisเทียบจุดnativeทุกฟอนต์ ใช้ภาพproofและเมื่อมีภาพเล่นจริงให้เทียบอีกครั้ง ตรวจชื่อเฉพาะและเพศผู้พูด/ผู้ฟังตามกฎเดิม

## ZIP/ข้อจำกัด

Finalยังมี5ZIPล่าสุดเท่านั้น อัปเดตเฉพาะThaiJP_Common_P.zipซึ่งตอนนี้รวมResident+TITLBสรุปเปิดเกม+8fonts+8textures(18assets) อีก4ZIPบทคงเดิม ทั้ง5ต้องใช้ร่วมกัน อ่านกลับรวม15mod files24assetsผ่าน ไม่มีassetทับกัน Commonรุ่นก่อนสำรองไว้นอกFinalตามmanifest ไม่มีการติดตั้งหรือทดสอบในเกมจริง ไม่อ้างว่าดูวิดีโอหรือทวนทุกgameplay triggerแล้ว

อ้างอิงเสียง/ผู้พูดที่ผู้ใช้ให้ยังอยู่ในHANDOFF: [คลิปหลัก](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU) ใช้JPดิบเป็นต้นฉบับ คำบรรยายอัตโนมัติไม่ใช่หลักฐานว่าได้ฟังแล้ว
