# Chapter13 — complete source recheck

<!-- chapter14-current -->
## ล่าสุด: Ch.1–14 + Common — 25 ตุลาคม 2026

ผู้ใช้สั่ง Ch.14 แล้ว ส่วนนี้แทนสถานะ/hash/วิธีสร้างและคำว่างานต่อรอCh.14ด้านล่างทั้งหมด ซึ่งคงไว้เป็นประวัติ ฐานปัจจุบัน **48,439รหัส / 28assets / 730clusters** `E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter14-th.json` SHA256 **5958321967a1bf3d18897aef9f77156457f71e5f41174441b573682ef55b9b32**. ฐานCh.13หลังรีเช็ค **47,503รหัสและACTORทุกตัวคงเดิม** รวมคำแก้บริบท/สรรพนามก่อนหน้าและทีฟ่าCh.4**เข้ามาสิ**/Red**เชิญ**/ทีฟ่าCh.1**ถามสิ** ห้ามassembler/finalizerบทเก่าทับฐานล่าสุด

Ch.14 **End of the World** เพิ่ม **936รหัส / 897แม่แบบ**: MIDGR201 (ความฝัน/เดต/ทางเลือกทุกเส้นของZack), FOREE435 (ฉากจบ338+บทบอสทุกตัวละคร97), CAPIT300 (สคริปต์JPอีกฉบับของฉากท้าย). อ่านJP/USรหัสเดียวกันเมื่อมี/ไทยครบ897แม่แบบระหว่างแปลและทวนJP/ไทยครบอีกครั้ง รวมบทที่ไม่มีACTORอังกฤษและคำอุทานซ้ำหลายผู้พูด ตรวจความหมายชัดเจนก่อนใช้คำแปลร่วม. CAPITไม่มีคำแปลอังกฤษจริง USเป็นรหัสplaceholder จึงแปลจากJPและใช้ชื่อผู้พูดตามตัวตนJPกับทะเบียนsame-ID JP/USในcorpus **ไม่ใช้placeholderเป็นต้นฉบับ**. CAPITบางบรรทัดเป็นคำกำกับการแสดงในวงเล็บและสคริปต์ต่างจากFOREE แปลคงเนื้อหาและIDไว้ ไม่อ้างว่าทุกบรรทัดถูกเรียกในเกม

ปรับร่างใหม่5แม่แบบใน `E:/FF7RebrithModTH/FF7Rebrith/qa/chapter14/editorial-revisions.json`: ตัวเลข1เรื่อง, รสขนมที่**ระคายลิ้น**, รูฟัสมองรูปพ่อใช้**พ่อนี่มัน**แทนนาย, เอริธ**ถ้าบอกว่าไม่ไหวล่ะ?**, และประโยคแก้แค้นของBarret. เรื่องโลกหลายชั้น/ดวงดาว/คำอธิษฐานยึดJP ไม่แทนด้วยENที่ดัดแปลง. เซฟิรอธ**ฉันประเมินเธอต่ำไป**หมายถึงAerithที่ปรากฏร่วมสู้ ไม่ใช่Cloud; มีบริบทข้างเคียงและรายงานคำตอบNojimaประกอบในpronoun-review

อ่านตัวเลือกครบ **3ชุด / 11รหัส**: ของขวัญพร้อม3ชิ้น, ขนมพร้อม3ชนิด, ท่าถ่ายรูปทั้ง3แบบ พร้อมบทเชิญ/ปฏิเสธ/คำตอบในฉาก ไม่ใช้คำตอบดู/ไม่ดูกับกิจกรรมอื่น ชื่อitemในUIอังกฤษตามUSเดิม. อ่านUIข้างเคียง **43รหัส** รวมเป้าหมายCh.14/สรุป/การพักครั้งสุดท้าย/ออกเมนูหลังจบ/เลือกบทHARD/คุณสมบัติหลังจบ/เปลี่ยนชุด คงคำแปลฐานเดิม. นาย/เธอชุดใหม่43รหัสอ่านตามผู้ฟังจริง รวมCloud/Biggs/Sephiroth/RufusชายและAerithหญิง ไม่replaceรวม; ทำนายเป็นคำศัพท์

Inverse scanทั้งcorpusพบJPในC3410/C3510/CAPTL_BOS **946รหัส** มีคำแปลครบในทะเบียน (รวมUIเดิม). namespaceNPCมีJP **6,297รหัส** ไม่มีตกหล่นเชิงทะเบียน; regressionNPC8,347รหัส/ACTORผ่าน, UI6,907/choicefamily7,218/ชื่อท่าศัตรู1,703ผ่าน. JPที่ยังไม่ได้แปลทั้งหมด **29รหัส** แยกรายIDเป็นdemo/store/event-only UI ในdeferred-remaining ไม่เหลือบทพูดretailที่ยังไม่ได้จัดหมวดในcorpusนี้ **ไม่รับรองเล่นทุกสถานะหรือไม่มีข้อผิดพลาด100%**

คำลงท้ายรวม **1848ครั้ง / 1801รหัส**: ครับ1294 / ค่ะ361 / คะ193; NPC/nonparty1439ครั้ง ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ unknownใช้กลาง ไม่เดาเพศจากsuffix. AerithตอนปลุกCloudยังแสดง???ใช้ข้อยกเว้นexactIDจากการเปิดเผยตัวในฉาก; label???คงตามเกม. เรดวัยหนุ่มฉัน. ศัพท์และชื่อบทพูดไทยตามglossaryเดิม (Aerithเอริธ/Zackแซ็ก/Caitเค็ตชี/Barretบาร์เร็ต/Sephirothเซฟิรอธ/อู่ไถ/มาโก้/แมทีเรีย/เซทรา/เมเทโอ/รียูเนียน); ACTOR/UIอังกฤษตามUSหรือmappingJPที่มีหลักฐาน เลขปริมาณอารบิก

730clustersเดิมไม่เพิ่ม ฟอนต์16assetsเหมือนรุ่นก่อนทุกไบต์ metrics8fonts/ASCII/digit pixels/จุดไข่ปลาระดับล่างคงเดิม. เปิดดูproofใหม่ครบ **11หน้า**: 3ชุดตัวเลือกและ37ตัวอย่างบทพูดในLarge/Normal รวม80font samples +แผ่น8fonts. ภาพแสดงglyphจากไฟล์จริง แต่ตัดบรรทัดเป็นตัวอย่าง **ยังไม่ได้ติดตั้ง/ทดสอบในเกม หรือดูฟังวิดีโอทุกแขนง**

Final `E:/FF7RebrithModTH/Mod/Final` มี **9ZIPล่าสุดแยกส่วน** เพิ่ม **ThaiJP_Chapter14_P.zip** สำหรับCAPITใหม่, อัปเดต **ThaiJP_Chapter1_11_12_P.zip** สำหรับMIDGRร่วม และ **ThaiJP_Chapter2_P.zip** สำหรับFOREEร่วม อีก6ZIPhashเดิมรวมCommon ไม่สร้างMIDGR/FOREEซ้ำในZIP14 ต้องใช้ชุดล่าสุดร่วมกัน อ่านกลับรวม9ZIP/27modfiles/28assetsผ่าน ไม่มีทับซ้อน ไม่มีรุ่นเก่าหรือsupportfilesในFinal สำรองเก่านอกFinal `E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/runs/98ea546b10594b41ba1ebe2c8f411c89/previous-final`. Source/dist/เกมไม่เปลี่ยน

ไฟล์หลักใต้ `E:/FF7RebrithModTH/FF7Rebrith/`: `reference/chapter14-source.json`, `chapter14-templates.json`, `chapter14-scope.json`, `chapter14-build.json`, `chapter14-actor-labels.json`, `through-chapter14-cluster-map.json`; `translations/chapter14/batch-01.json`ถึง`batch-09.json`, `translations/chapter14-th.json`, `translations/working-through-chapter14-th.json`. QA `qa/chapter14/`: baseline+revisionsimmutableห้ามprepareซ้ำ/รีเซ็ตindex; progress/review-records/editorial-revisions/same-scene-variant-reuse/actor-label-candidates; choice/pronoun/numeric/duplicate-context/adjoining-UI/coverage/deferred/NPC/gender; verification/old-glyph-regression/proof/visual-review/editorial-signoff/release-verification

สร้างซ้ำ: `tools/assemble_chapter14.py` → `tools/build_chapter14.py --text-only` (mapเดิม;เต็มเมื่อglyphใหม่) → `tools/build_chapter14.py --verify` → `tools/audit_chapter14.py` → `tools/audit_shared_dialogs.py` → `tools/audit_chapter14_glyphs.py` → `tools/chapter14_review.py` → `tools/preview_chapter14.py` → เปิดดูภาพจริงแล้วบันทึกvisual-reviewตามhash → `tools/signoff_chapter14.py` → `tools/publish_final_parts.py` → `tools/finalize_chapter14.py`. ห้ามprepareซ้ำ/เอาoverlayหรือassemblerเก่าท้ายสุดจนย้อนคำแก้. SourceCAPITใหม่ต้องมีownerแพ็กเฉพาะและunion28assets

งานต่อ: รอผู้ใช้เลือกรีเช็ค/ทดสอบในเกม/แก้ภาพที่พบ; **ยังไม่ติดตั้งโดยอัตโนมัติ**. ขอบเขตเนื้อเรื่องCh.1–14ในทะเบียนปัจจุบันแปลแล้ว แต่ยังต้องตรวจผลจริงทุกแขนง/พื้นที่กลับมา/กิจกรรมหากผู้ใช้รายงานหรือสั่งรีเช็คเพิ่ม ใช้ฐาน48,439ล่าสุดนี้เสมอ. Demo29รหัสพักตามขอบเขต ไม่เพิ่มโดยอัตโนมัติ

คลิปผู้ใช้สำหรับบท/เสียง/ผู้พูดและเพศ: https://www.youtube.com/watch?v=i4gD0mmj5vc ; https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU ; https://www.youtube.com/watch?v=bxrLsiU-QKk . Ch.14เพิ่มเติม https://www.youtube.com/watch?v=BIHjKH4c1BI ตรวจmetadata/ขอบเขต ไม่อ้างฟังครบ. ขอบเขตเทียบassetกับ https://www.powerpyx.com/final-fantasy-7-vii-rebirth-chapter-14-end-of-the-world-walkthrough/ และ https://gamers-high.com/ff7-rebirth/story/chapter14.html . ประโยคเซฟิรอธถึงเอริธมีคำอธิบายผู้เขียนบทที่รายงานใน https://www.frontlinejp.net/2024/04/17/final-fantasy-vii-rebirth-post-release-interview-part-2-devs-discuss-side-characters-dialogue-and-sequel/
<!-- /chapter14-current -->

<!-- chapter13-recheck-current -->
## ล่าสุด: รีเช็ค Ch.13 ครบชุด — 25 ตุลาคม 2026

ฐานปัจจุบัน **47,503รหัส / 27assets / 730clusters** `E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter13-th.json` SHA256 **e128a336eda9b01749107fd5c437807868a383e6364b39020804e7a467b59145** ส่วนนี้แทนสถานะ/hashของCh.13รุ่นแรกด้านล่าง ฐานCh.1–12เดิม46,650และACTORทุกตัวคงเดิม ห้ามassembler/finalizerบทเก่าทับ

อ่านเทียบJP/ไทยครบ **809แม่แบบ / 853รหัส** ใหม่อีกรอบ รวมการเดินทาง/วิหารทั้งสองกลุ่ม/ฉากทดสอบ/NPCไม่มีACTOR/ภาพผนัง/บทบอสและบทช่างภาพ ทวนคำถามพร้อมทุกปุ่ม **2ชุด / 6รหัส** และบริบทบรรทัดข้างเคียง ตัวเลือกคงเดิม แก้ **11แม่แบบ / 11รหัส**: ถามเอริธว่า**เรียกเธออยู่เหรอ?** ไม่ทำให้สับสนผู้เรียก; 1หมัดสามจุด/เติร์กส์1คน/โลก1ใบใช้เลขอารบิก; **ยังเชื่อมถึงกันอยู่** ไม่สมมติเพิ่มว่าต้องเป็นทางกายภาพ; **ยกดวงดาวให้**ตรง譲る; เรด**เสียดายที่ไม่ได้ขอโทษ**เป็นอดีตพลาดโอกาส; ปรับคำเอาคืนระหว่างต่อสู้ และระบุ**พวกเราไม่มีที่ให้หนี**ขณะกำแพงDemon Gateบีบเข้ามา

คำแก้before/after/JP/เหตุผลแต่ละIDอยู่ `E:/FF7RebrithModTH/FF7Rebrith/reference/chapter13-recheck-overrides.json` อัปเดตbatchต้นทาง+patch+combinedแล้ว อีก **47,492text** และACTORทุกตัวคงเดิม ไม่มีเพิ่ม/ลบID ไม่เริ่มCh.14 คำลงท้ายยัง **1,814ครั้ง** (ครับ1276/ค่ะ349/คะ189; NPC1439) ไม่มีสลับเพศในทะเบียน; ชุดนาย/เธอใหม่13รหัสรวมทีฟ่าเรียกเอริธใช้เธอ ถูกผู้ฟังจริง ไม่replaceทั้งเกม

QA `E:/FF7RebrithModTH/FF7Rebrith/qa/chapter13/recheck/`: baseline+revisionsimmutableก่อนรีเช็ค(ห้ามprepareซ้ำ/เขียนทับ), progressอ่าน809ค้าง0, audit, proof2หน้า11คำแก้, visual-review และrelease-verification. ตรวจภาพ2หน้าใหม่ครบแล้ว mainproof11หน้าสร้างใหม่hashตรงภาพที่เคยดูทั้งหมดจึงreuseหลักฐานโดยบันทึกชัดเจนในvisual-reviewหลัก ไม่ได้อ้างเปิดดู11หน้าใหม่ซ้ำ ฟอนต์16assets/map730ตรงรุ่นก่อนทุกไบต์ ตรวจเลข9รายการ/JP C33+TEMPL857รหัส/NPC6297รหัส/ตัวเลือก7218/UI6907/NPCregression8347/ชื่อท่า1703ผ่าน UIข้างเคียง239รหัสคงเดิมและตรวจโครงสร้างต่อจากการอ่านครั้งก่อน

Finalที่ `E:/FF7RebrithModTH/Mod/Final` มี **8ZIPล่าสุดแยกส่วน** อัปเดตเฉพาะ **ThaiJP_Chapter2_P.zip** เพราะFOREEใช้ร่วมCh.2/Ch.13 อีก7ZIPรวมCommonhashเดิม อ่านรวม8ZIP/24modfiles/27assetsผ่าน ไม่มีassetทับซ้อน สำรองZIPก่อนนอกFinal `E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/runs/4dc6ee69daa0458cbbf32ac91feadbee/previous-final` source/dist/เกมไม่เปลี่ยน **ยังไม่ได้ติดตั้งหรือทดสอบในเกม/ฟังวิดีโอทุกแขนง**

สร้างซ้ำตามpipelineCh.13ด้านล่าง โดยเพิ่ม `tools/chapter13_recheck.py` gateอัตโนมัติในshared audit และ `--preview`สำหรับคำแก้11รหัส; mainpreviewใช้ภาพเดิมได้เฉพาะhashตรงหลักฐานที่เคยดู ต้องดูrecheckproofที่เปลี่ยนก่อนsignoff/publish ปิดด้วย **`tools/finalize_chapter13_recheck.py`** แทนfinalize13เดี่ยวๆ บทถัดไปcarryฐาน47,503ปัจจุบันพร้อม11คำแก้นี้ ห้ามประกอบจากbatchรุ่นก่อน งานต่อรอผู้ใช้สั่งCh.14; กฎJPก่อนUS/ศัพท์/เพศ/ตัวเลือกทุกปุ่ม/YouTubeและpathในส่วนCh.13ด้านล่างยังใช้
<!-- /chapter13-recheck-current -->
