# ส่งต่องานม็อด FF7 Rebirth ซับไทย / เสียงญี่ปุ่น

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

<!-- chapter13-current -->
## ล่าสุด: Ch.1–13 + Common — 25 ตุลาคม 2026

ผู้ใช้สั่งทำCh.13แล้ว ส่วนนี้แทนสถานะ/hash/วิธีสร้างปัจจุบันทั้งหมดด้านล่างซึ่งเก็บไว้เป็นประวัติ ฐาน **47,503รหัส / 27assets / 730clusters** `E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter13-th.json` SHA256 **e128a336eda9b01749107fd5c437807868a383e6364b39020804e7a467b59145** ฐานCh.12หลังรีเช็ค46,650รหัสและACTORทุกตัวคงเดิม รวม56คำแก้ล่าสุด/45คำแก้สรรพนาม/ทีฟ่าCh.4**เข้ามาสิ**/Red**เชิญ**/ทีฟ่าCh.1**ถามสิ** ห้ามassembler/finalizerเก่าทับ

Ch.13 **Where Angels Fear to Tread** เพิ่ม **853รหัส / 809แม่แบบ**: C3310/C3320/C3330/C3340ข้ามasset751รหัส (Resident6+FOREE745), บทบอสวิหารTEMPL_BOS19–22ทุกตัวละคร100รหัส, บทช่างภาพจบงานPHOTO00_0900สองรหัส รวมการเดินทาง/วิหารทั้งสองกลุ่ม/การทดสอบRed,Tifa,Yuffie,Barret,Aerith,Cloud/ภาพผนัง/หลบหนี/ช่วงแมทีเรียดำ ไม่มีเพิ่มบทพูดC3410ความฝันหรือC3510/CAPTL_BOSของCh.14

อ่านJP/USรหัสเดียวกัน/ไทยครบ809แม่แบบระหว่างแปลและอ่านทวนJP/ไทยครบอีกครั้ง ปรับร่างใหม่12แม่แบบพร้อมเหตุผลก่อนหลังใน `E:/FF7RebrithModTH/FF7Rebrith/qa/chapter13/editorial-revisions.json` เช่นแมทีเรียดำ**ยกให้ใครไม่ได้** ไม่ใช่ปล่อยให้คนไป; คู่คำเฉิง/เอริธ**ยอมมาซะดีๆ... / ไม่ยอมค่ะ!**; ความโกรธ/ความเศร้าตามJP ไม่เอาบทUSดัดแปลงมาแทน; บทเอริธเรื่องความตายและความแข็งแกร่ง/ภาพผนังเรื่องภัยพิบัติอ่านต่อเนื่องครบ

ตรวจคำถามพร้อมทุกปุ่ม **2ชุด / 6รหัส** ที่แปลไว้แล้ว: ขึ้นฝั่ง/ยังไม่ขึ้น(จุดไม่ย้อนกลับ) และขึ้นเรือ/ยังไม่ขึ้น ทั้งสองคงเดิมตรงบริบท; อ่านUIข้างเคียง **239รหัส** รวมชื่อเป้าหมาย/สรุป/แรงโน้มถ่วง/ไลฟ์สตรีม/คำสั่งช่วย/ร้านวิหาร ไม่มีแก้ฐานเก่า ตรวจนาย/เธอชุดใหม่13รหัสตามผู้ฟังจริง Tifa→Aerith,Nero→Yuffieใช้เธอ; Sephiroth→กลุ่มรวมCloudใช้พวกนาย; ทำนายเป็นคำศัพท์ ไม่ใช่สรรพนาม

Inverse scanทั้งcorpus: C33/TEMPL_BOSที่มีJP **857รหัส** ครบ และNPCมีJP **6297รหัส** ไม่เหลือตกหล่นในทะเบียน; ทุกJPที่ยังไม่แปลจัดเหตุผลรายIDในdeferred-remainingเป็นCh.14หรือdemo/store/event-only UI ไม่พักทั้งnamespaceจากsuffix ไม่อ้างว่าเล่นทุกสถานะแล้ว ตรวจอ่านกลับtext/metadata27assetsผ่านUI6907/ตัวเลือกfamily7218/NPCregression8347/ชื่อท่าศัตรู1703

คำลงท้ายรวม **1814ครั้ง / 1767รหัส**: ครับ1276 / ค่ะ349 / คะ189; NPC/nonparty1439ครั้ง ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ unknownใช้กลาง; ไม่อนุมานเพศจากsuffix. เสียง???ของCaitกลับมาระบุตัวได้จากบรรทัดถัดไปใช้ข้อยกเว้นexactIDเท่านั้น เรดวัยหนุ่มฉัน; เอริธ/แซ็ก/เค็ตชี/บาร์เร็ต/เฉิง/รู้ด/อิเลน่า/เรโน/โซนอน/ซิด/วินเซนต์/เซทรา/มาโก้/แมทีเรีย/โซลเจอร์/อู่ไถตามglossary ชื่อACTORและUIอังกฤษตามUS บทพูดไทย เลขปริมาณอารบิก

ฟอนต์730clustersไม่เพิ่ม ทุกassignment/metricsเดิม8fontsคงเดิม; nativeASCII/เลข/จุดไข่ปลาระดับล่างผ่านตรวจ pixel/textureจริง ดูproof **11หน้า**: คำถามพร้อมทุกปุ่มและ36ตัวอย่างบทพูดคู่Large/Normal รวม76font samples +แผ่นเทียบ8fonts ภาพตัดบรรทัดเป็นตัวอย่าง **ยังไม่ได้ติดตั้ง/ทดสอบในเกม หรือดูฟังวิดีโอครบทุกแขนง**

Finalมี **8ZIPล่าสุดชื่อเดิมแยกส่วน** ที่ `E:/FF7RebrithModTH/Mod/Final` อัปเดต **ThaiJP_Chapter2_P.zip** (FOREEแชร์Ch.2และCh.13) กับ **ThaiJP_Common_P.zip** อีก6ZIPhashเดิม ไม่สร้างZIPCh.13ซ้ำasset อ่านรวม8ZIP/24modfiles/27assetsผ่านไม่มีทับซ้อน ต้องใช้ชุดล่าสุดร่วมกัน สำรองเก่านอกFinal `E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/runs/4dc6ee69daa0458cbbf32ac91feadbee/previous-final` source/dist/เกมไม่เปลี่ยน

ไฟล์ทำงานใต้ `E:/FF7RebrithModTH/FF7Rebrith/`: `reference/chapter13-source.json`, `chapter13-templates.json`, `chapter13-scope.json`, `chapter13-build.json`, `through-chapter13-cluster-map.json` (5ไฟล์นี้ในreference/); `translations/chapter13/batch-01.json`ถึง`batch-08.json`, `translations/chapter13-th.json`, `translations/working-through-chapter13-th.json`. QA `qa/chapter13/`: baseline+revisionsimmutable(ห้ามprepareซ้ำ/รีเซ็ตindex), progress,review-records,editorial-revisions,choice/pronoun/numeric/duplicate-context/adjoining-UI/coverage/deferred/NPC/gender,verification,old-glyph-regression,proof,visual-review,editorial-signoff,release-verification

สร้างซ้ำ: `tools/assemble_chapter13.py` → `tools/build_chapter13.py --text-only` (mapเดิม;เต็มเมื่อglyphใหม่) → `tools/build_chapter13.py --verify` → `tools/audit_shared_dialogs.py` → `tools/audit_chapter13_glyphs.py` → `tools/chapter13_review.py` → `tools/preview_chapter13.py` → เปิดดูภาพจริง+บันทึกvisual-reviewตามhash → `tools/signoff_chapter13.py` → `tools/publish_final_parts.py` → `tools/finalize_chapter13.py` ห้ามprepare13ซ้ำ/รันmigration12เก่า/เอาoverlayเก่าท้ายสุดจนย้อนคำแก้ฐาน

งานต่อเมื่อผู้ใช้สั่งCh.14: ใช้ฐาน47,503นี้ append-only; เพิ่มC3410ในMIDGR,C3510ในFOREE+CAPITและCAPTL_BOS ตรวจACTOR/ไม่มีACTOR/ทุกตัวเลือก/ทุกแขนง/ศัพท์/คำลงท้าย/เลข/tags/ฟอนต์และsharedUIเหมือนเดิม ระวังCAPITเป็นassetที่ยังไม่มีในworkingชุดนี้ ต้องขยายเจ้าของแพ็ก/unionอย่างชัดเจน ไม่ย้ายทับไฟล์เดิม

คลิปผู้ใช้สำหรับบท/เสียง/ผู้พูดและเพศคงอยู่: https://www.youtube.com/watch?v=i4gD0mmj5vc ; https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU ; https://www.youtube.com/watch?v=bxrLsiU-QKk . เพิ่มCh.13 https://www.youtube.com/watch?v=sqDaAon-MlA ตรวจmetadataเท่านั้นในรอบนี้ ไม่อ้างฟังครบ; ขอบเขตเทียบcorpusกับ https://www.powerpyx.com/final-fantasy-7-vii-rebirth-chapter-13-where-angels-fear-to-tread-walkthrough/ และ https://game8.jp/ff7rebirth/596970
<!-- /chapter13-current -->

<!-- chapter12-recheck-current -->
## ล่าสุด: อ่านรีเช็ค Ch.12 ครบชุด — 25 ตุลาคม 2026

ฐานใหม่ **46,650รหัส / 27assets / 730clusters** `E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter12-th.json` SHA256 **dc535bd9767da3f77d26a2b495a486c06fade1a560176ab7fe12d0357b1aa3d0** ส่วนนี้แทนสถานะ/hashของCh.12รุ่นแรกด้านล่าง ฐานCh.1–11เดิมและคำแก้สรรพนาม45รหัสคงอยู่ ห้ามใช้ assembler/finalizerเก่าทับ

อ่านเทียบJP/ไทยซ้ำครบ **3,847แม่แบบ / 4,200รหัส** รวมทุกเดต/LOVELESS/เควส11งาน/โปรโตเรลิก/Queen’s Blood/บทกลับพื้นที่เดิม/NPCไม่มีACTOR/Commonคำอธิบายศัตรู อ่านคำถามพร้อมทุกปุ่มและบริบทคำตอบ **36ชุด** อีกครั้ง ตัวเลือกทั้งหมดคงเดิมในรอบนี้ รวม7คำแก้UIจากรุ่นแรก บริบทซ้ำยึดIDและผู้พูดเดิม ไม่ถือscriptผ่านเป็นการอ่านความหมาย

แก้เพิ่ม **56รหัส** (55รายการจากการอ่านรอบแรกของรีเช็ค+1รายการระบุBillyกับน้องสาวให้ชัด): Redเดินให้ช้าลงตามทุกคน ไม่ใช่เดินให้ทัน; เดตแรกBarretเป็นสวนสนุกคนละแห่ง ไม่ใช่ที่นี่; ElmyraพูดถึงการดูแลAerith ไม่ได้เรียกAerithเป็นผู้ฟัง; 足音คือเสียงฝีเท้า; ผมหน้าม้าสองจุดไม่ใช่ฉันหน้าม้า; ล็อกผลแข่ง/วัยที่เหมาะจะฟังความจริง/หัวหน้าแผนกปกป้องลูกน้อง; อารมณ์มอนสเตอร์; ชื่อRogue StanceตรงUSactionID; สะกดศัตรู/แคคเตอร์ให้ตรงศัพท์เดิม และปรับคำตก/ภาษาแข็ง/ผู้กระเด็นจากโพรงให้ชัด คำอธิบายกับก่อน/หลังรายIDอยู่ `E:/FF7RebrithModTH/FF7Rebrith/reference/chapter12-recheck-overrides.json` อีก46,594textและACTORเดิมทุกตัวคงเดิม ไม่มีเพิ่มบทพูดCh.13 ไม่มีIDเพิ่ม/ลบ

หลักฐาน `E:/FF7RebrithModTH/FF7Rebrith/qa/chapter12/recheck/`: baseline.json+revisionsเป็นsnapshotimmutableก่อนรีเช็ค ห้ามprepareหรือเขียนทับ; progressอ่านครบค้าง0, audit, choice-review, coverage-review, proof7หน้า56panels, visual-review, release-verification. ตรวจinverse source: C32ข้ามasset1,315รหัส, namespaceNPC6,292รหัส, บทเดินJP-only36รหัส และEnemy Intelคำอธิบาย/คำแนะนำ544รหัส ไม่มีJPตกหล่นในทะเบียนเหล่านี้ ไม่ใช่รับรองเล่นทุกแขนงในเกม

ตรวจอ่านกลับtext/metadata27assets ผ่านUIเดิม6907/ตัวเลือกfamily7218/NPCที่เคยเก็บ8347/ชื่อท่า1703 ฟอนต์16ไฟล์กับmap730ตรงรุ่นCh.12ก่อนรีเช็คทุกไบต์ คงellipsis/เลข/อังกฤษ/คำลงท้าย1750ครั้ง (ครับ1261/ค่ะ323/คะ166; NPC1401) เปิดดูproofใหม่7หน้าครบ56คำแก้และmainหน้า13ที่เปลี่ยน ส่วนmainอีก15หน้าสร้างใหม่แล้วhashตรงภาพที่เคยดูจึงreuseหลักฐานอย่างชัดเจน ภาพglyphstageตัดบรรทัดเป็นตัวอย่าง **ยังไม่ได้ทดสอบในเกมหรือดูฟังวิดีโอครบทุกแขนง**

Finalมี **8ZIPล่าสุดแยกส่วน** ชื่อเดิมของCh.12รุ่นแรก อัปเดตครบทั้ง8ZIPตามassetที่แก้ รวม `ThaiJP_Chapter2_P.zip` ซึ่งมีคำแก้FOREE อ่านรวม8ZIP/24modfiles/27assetsผ่านไม่มีซ้ำ สำรองรุ่นก่อนอยู่นอกFinal `E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/runs/d9bc09d0009547809735f8ee7399ed29/previous-final` ไม่ติดตั้ง/ไม่เปลี่ยนsource/dist/เกม ใช้ทั้ง8ZIPrุ่นปัจจุบันร่วมกัน

สร้างซ้ำ: `tools/assemble_chapter12.py` → `tools/build_chapter12.py --text-only`/`--verify` → `tools/audit_shared_dialogs.py` (รวมrecheckgate) → `tools/preview_chapter12.py` + `tools/chapter12_recheck.py --preview` → เปิดดูภาพที่เปลี่ยนหรือreuseเฉพาะhashตรง → บันทึกvisual-review → `tools/signoff_chapter12.py` → `tools/publish_final_parts.py` → **`tools/finalize_chapter12_recheck.py`** ไม่รันmigration `chapter12_editorial.py`/`chapter12_recheck_fixes.py`ซ้ำ ต้องcarry56คำแก้นี้จากฐาน46,650ปัจจุบันเมื่อเริ่มบทใหม่

งานต่อรอคำสั่งCh.13 หลักJPก่อนUS/คำลงท้ายตามเพศ/unknownใช้กลาง/Cloudนายคุณ/เอริธแซ็กเค็ตชี/ตัวเลือกทุกปุ่ม/YouTubeและpathในส่วนCh.12ด้านล่างยังใช้ ไม่มีอ้างว่าอ่านCh.1–11ทุกบรรทัดใหม่ในรอบนี้;ตรวจถดถอยและคงฐานที่รีเช็คไว้แล้ว
<!-- /chapter12-recheck-current -->

<!-- chapter12-current -->
## ฐานปัจจุบัน Ch.1–12 + Common — 25 ตุลาคม 2026

ส่วนนี้แทนสถานะ/hash/วิธีสร้างรุ่นก่อนด้านล่าง ซึ่งเก็บไว้เป็นประวัติ ตอนนี้แปล Ch.12 แล้ว ฐาน **46,650รหัส / 27assets / 730clusters**: `E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter12-th.json` SHA256 **dc535bd9767da3f77d26a2b495a486c06fade1a560176ab7fe12d0357b1aa3d0** ห้ามใช้ assembler/finalizer บทเก่าทับฐานนี้

Ch.12เพิ่ม **4,200รหัส / 3,847แม่แบบ**: C3210/C3220/C3230ข้ามassetครบ1,278รหัส รวมZackและเดตทั้ง6แบบ/LOVELESSทุกRosa/ก่อนออกเรือ;11เควสที่ปลดล็อกในCh.12;โปรโตเรลิกช่วงสุดท้าย/Gilgamesh;Queen’s Bloodตอนจบ;บทกลับพื้นที่เดิม/ภาพถ่าย/เปียโน/สมบัติโจรสลัด เก็บบทเดินGrasslandsที่มีเฉพาะJP36รหัสและNPCNibelในResident122รหัสด้วย เพิ่มคำอธิบาย/คำแนะนำEnemy Intel UIที่เหลือ488รหัสตามขอบเขตUIทั้งเกมที่ผู้ใช้อนุญาต ไม่ได้เริ่มบทพูดCh.13–14

อ่านJPทุกแม่แบบระหว่างแปล ใช้USรหัสเดียวกันเป็นข้อมูลบริบท/ชื่อทางการ ตรวจคำถามพร้อมทุกตัวเลือกและบทตอบ **36ชุด** ปรับคำถามหัวหน้าแผนกShinra6รหัสกับตัวเลือกCissnei1รหัส มีbefore/after/เหตุผลใน `E:/FF7RebrithModTH/FF7Rebrith/reference/chapter12-context-overrides.json` ฐาน42,450เดิมคงtextทุกตัวนอก7รหัสนี้ และACTORเดิมคงทุกตัว รวมคำแก้บริบท/สรรพนาม45รหัสของรุ่นก่อน ห้ามapplyoverlayเก่าท้ายสุดจนย้อนคำแก้ใหม่

รีเช็คชื่อพูดเอริธ/แซ็ก/เค็ตชี/บาร์เร็ต/เฉิง/รู้ด/อวาแลนช์/มาโก้/แมทีเรียตามglossary คงทีฟ่าCh.4**เข้ามาสิ**/Red**เชิญ**/ทีฟ่าCh.1**ถามสิ**; Cloudใช้**นาย/คุณ**ตามน้ำเสียง กลุ่มรวมCloudใช้พวกนาย/พวกคุณ; เธอใช้เมื่อหมายถึงหญิง/เพลง/บริบทที่เหมาะสม แยกนายกเทศมนตรี/ทำนาย/เจ้านายออกจากสรรพนาม ตรวจชุดใหม่146รหัสที่มีนายหรือเธอ แก้主人2จุดเป็นเจ้านาย ไม่replaceสรรพนามทั้งเกม

คำลงท้ายรวม **1750ครั้ง / 1708รหัส**: ครับ1261 / ค่ะ323 / คะ166; NPC/nonparty1401ครั้ง ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ ผู้พูดไม่ชัดใช้กลาง ไม่เดาเพศจากsuffix ไม่บังคับเติมคำลงท้ายทุกประโยค Redวัยหนุ่มใช้ฉัน ชื่อUI/ACTOR/ศัตรู/ท่าอังกฤษตามUSรหัสเดียวกันและenemy/actionIDจริง (JPชื่อท่าซ้ำกันอาจมีอังกฤษต่างกัน เช่นのしかかり/みがまえる ต้องดูศัตรู)

ไฟล์ทำงาน: `E:/FF7RebrithModTH/FF7Rebrith/reference/chapter12-source.json`, `reference/chapter12-templates.json`, `reference/chapter12-scope.json`, `translations/chapter12/batch-01.json`ถึง`batch-33.json`, `translations/chapter12-th.json`, `reference/through-chapter12-cluster-map.json`, `reference/chapter12-build.json` (ทุกrelativepathในประโยคนี้อยู่ใต้ `E:/FF7RebrithModTH/FF7Rebrith/`). snapshotฐานCh.11immutableอยู่ `E:/FF7RebrithModTH/FF7Rebrith/qa/chapter12/baseline.json`และ`revisions/` **ห้ามprepareซ้ำ**

หลักฐาน `E:/FF7RebrithModTH/FF7Rebrith/qa/chapter12/`: progress/translation-audit/review-records, choice-review36ชุด, pronoun-review, numeric-decisions46รหัส(45แม่แบบ), gender, NPC-residual, old-glyph-regression, proof16หน้า, visual-review, editorial-signoff, release-verification. อ่านกลับทุกtext/metadata27assets ตรวจUIเดิม6907/ตัวเลือกfamily7218/NPCที่เคยเก็บ8347/ชื่อท่า1703ผ่าน;ทะเบียนรหัสที่มี `_NPC_` ไม่มีJPตกหล่นใน27assets แต่ไม่ได้รับรองการเล่นทุกเหตุการณ์ในเกม ฟอนต์ใหม่9clusters คง721assignments/metricsเดิมทั้ง8fontsและจุด…ระดับล่าง ตรวจภาพจริงครบ16หน้าจากglyphstage การตัดบรรทัด/เลือกfontในภาพเป็นตัวอย่าง **ยังไม่ได้ทดสอบในเกมหรือดูฟังวิดีโอทุกแขนง**

Finalเก็บเฉพาะ **8ZIPล่าสุด แยกส่วน**: `ThaiJP_Chapter1_11_12_P.zip`แทน1_11เดิม, `ThaiJP_Chapter8_12_P.zip`แทนChapter8เดิม; Chapter2 / Chapter3_4_5 / Chapter6_7 / Chapter9 / Chapter10 / Commonชื่อเดิมแต่เป็นเนื้อหารุ่นล่าสุด ต้องใช้ทั้ง8ส่วนร่วมกัน เพราะCh.12กลับหลายพื้นที่และassetsแชร์กัน อ่านกลับรวม8ZIP/24modfiles/27assetsผ่านไม่มีซ้ำ สำรองZIPก่อนหน้าอยู่นอกFinal `E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/runs/d9bc09d0009547809735f8ee7399ed29/previous-final` ไม่ติดตั้งและไม่เปลี่ยนsource/dist/เกม

สร้างซ้ำตามลำดับ: `tools/assemble_chapter12.py` → `tools/build_chapter12.py` (เต็มเมื่อglyphใหม่, `--text-only`เมื่อmap/fontคงเดิม) → `tools/build_chapter12.py --verify` → `tools/audit_shared_dialogs.py` → `tools/audit_chapter12_glyphs.py` → `tools/preview_chapter12.py` → เปิดดูภาพที่เปลี่ยนและบันทึกvisual-reviewตามhashจริง → `tools/signoff_chapter12.py` → `tools/publish_final_parts.py` → `tools/finalize_chapter12.py` ไม่รัน `chapter12_editorial.py`ซ้ำเพราะเป็นmigrationของร่างก่อนแก้

งานต่อ: รอผู้ใช้สั่งCh.13ก่อนเพิ่มบทพูด C3310/C3320/C3330/C3340/C3410/C3510และTemple/Capitalbosses;ทุกบทใหม่ตรวจNPCไม่มีACTOR/บทใช้ซ้ำ/คำถาม+ทุกปุ่ม+บทตอบ/ชื่อเควส+HUD/คำแจ้งเตือน+ท่าศัตรู/นายเธอ+คำลงท้าย/ตัวเลข+tags+ฟอนต์ด้วย ฐานใหม่ต้องcarry46,650นี้และใช้append-onlyscope/snapshot ไม่รีเซ็ตทะเบียนเก่า

คลิปเดิมสำหรับเทียบบท/เสียง/ผู้พูดและเพศ (ไม่ใช่หลักฐานว่าเปิดดูครบในรอบนี้): https://www.youtube.com/watch?v=i4gD0mmj5vc ; https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU ; https://www.youtube.com/watch?v=bxrLsiU-QKk ; เพิ่มรายการEN Ch.12 https://www.youtube.com/watch?v=0zxhzIW2VbA (ตรวจmetadataเท่านั้น) ขอบเขตเควส/แขนงเทียบcorpusและ walkthroughในreference/chapter12-scope.json
<!-- /chapter12-current -->

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

<!-- chapter11-recheck-current -->
## ฐานล่าสุด: รีเช็คเก็บตก Ch.11 — 24 ตุลาคม 2026

ส่วนนี้แทนยอดและขั้นตอน Chapter11 เดิมด้านล่าง ปัจจุบัน **42,450รหัส / 27assets / 721clusters** SHA256 **5dd656c910f18b7af88513a0999708d02051521b758b61a32bf3ed80b7a04e51** ฐาน `E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter11-th.json` แพ็กแก้แล้วใน `E:/FF7RebrithModTH/Mod/Final` ห้ามรัน finalizer/assembler ของบทเก่าทับฐานนี้

อ่านเทียบJP/ไทยครบ1,658แม่แบบเดิม/1,703รหัส รวมNPCและบรรทัดไม่มีACTOR ตรวจแม่แบบใช้ซ้ำ28กลุ่มพร้อมทุกID และคำถาม12กลุ่ม47รหัสพร้อมทุกปุ่ม/บริบทตอบรับ ตรวจ C31 ข้ามassetครบ659รหัส แก้ **49รหัสเดิม** (รวมตัวเลือกCh.11ที่เคยแปลเป็นUIไว้3รหัส) และเก็บเพิ่ม **Enemy Intel UI56รหัสของ28คู่คำอธิบาย/คำแนะนำ** ใน Common รวมCh.11ใหม่จากฐานCh.10เป็น1,759รหัส/1,714แม่แบบ ไม่มีบทพูดCh.12เพิ่ม ไม่ใช่คำรับรองว่าคำอธิบายศัตรูทั้งเกมครบแล้ว

จุดแก้สำคัญ: Cloudถามถึงความช่วยเหลือในอดีต; BarretถามAerithละนาย; เพลงยุฟฟี่สลับผู้ไล่ตาม; 嗜好品ไม่เจาะจงว่าเป็นเครื่องดื่ม; Chadleyกล่าวถึงงานวิจัยของตัวเอง; คำเรียกหัวหน้าครัว/ราชินีโลหิตดำ; ผู้พูดไม่ชัดใช้กลาง ตัวเลือกคุยTifaเป็นก็เคยอยู่/อย่ามาล้อกันสิ และบทRedเป็นไม่ต้องใส่ใจหรอก โดยคงฝั่งตอบรับเดิม ยึดJPก่อนUS (เช่นเงื่อนไขPyretailและSwan Song) ชื่อUI/ท่าใช้officialEnglishตามenemy/actionIDจริง

หลักฐานแก้: `reference/chapter11-recheck-overrides.json`49รหัสก่อน/หลัง/เหตุผล; เพิ่มUI `reference/chapter11-recheck-source.json`56รหัสกับ `translations/chapter11-recheck-lines.json` ทะเบียนเริ่ม46รหัสถูกเก็บimmutableที่ `qa/chapter11/recheck/inventory-revisions/initial46.json` แล้วappend10 ห้ามprepareซ้ำ ตรวจ `qa/chapter11/recheck/progress.json`, `review.json`, `choice-semantic-review.json`, `duplicate-context-review.json`, `enemy-intel-scope.json`, `release-verification.json` และ [CHAPTER11-RECHECK-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER11-RECHECK-STATUS.md)

ACTORทั้งหมดเดิมตรงเดิม ฐาน42,394ก่อนรีเช็คคงเดิมยกเว้น49รหัสที่มีเหตุผล; ฐานCh.10จำนวน40,691คงเดิมยกเว้นตัวเลือกCh.11จำนวน3รหัสที่อนุมัติบริบทในรอบนี้ ไม่เขียนว่าทั้ง40,691ข้อความคงเดิมอีก คำลงท้ายยัง1548ครั้งใน1509รหัส (ครับ1084/ค่ะ308/คะ156; NPC1257) ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ ผู้พูดไม่ชัดใช้กลาง Cloudนาย/คุณ กลุ่มพวกนาย/พวกคุณ คงเอริธ/แซ็ก/เค็ตชี/เรดวัยหนุ่มฉัน และทีฟ่าCh.4เข้ามาสิ/Redเชิญ

ตรวจอ่านกลับtext/metadataครบ27assets ผ่านUIเดิม6907, ตัวเลือกfamily7218, NPCเดิม8347 และชื่อท่าอังกฤษ1703 เลขต่าง12รายการมีคำตัดสินแล้ว ไม่มีกlyphใหม่ในรอบรีเช็ค: cluster-map721และไฟล์font16ไฟล์ byteตรงรุ่นCh.11ก่อนรีเช็ค ดูภาพจริงครบmain12หน้า96samplesและrecheck14หน้า105panels (ทุก49รหัสแก้+56เพิ่ม) ใช้glyphจากstageจริง การตัดบรรทัดเป็นตัวอย่าง ไม่ใช่ภาพเกม ไม่อ้างฟังเสียงหรือเล่นทุกแขนง

Finalมี8ZIPล่าสุด แทน **ThaiJP_Chapter1_11_P.zip** กับ **ThaiJP_Common_P.zip** อีก6ZIPhashเดิม อ่านกลับ8ZIP/24modfiles/27assetsรวมกันผ่านไม่ซ้ำ สำรองรุ่นก่อนนอกFinal: `E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/runs/35f66d15de544264a187d439f8932d50/previous-final` ไม่ติดตั้งเกม protected source/dist/game hashคงเดิม

สร้างซ้ำ: `tools/assemble_chapter11.py` → `tools/build_chapter11.py --text-only` (เมื่อmapเดิม)/`--verify` → `tools/audit_shared_dialogs.py` → mainและrecheckpreview → ดูภาพจริง/บันทึกvisual-reviewสองชุด → `tools/signoff_chapter11.py` → `tools/publish_final_parts.py` → **`tools/finalize_chapter11_recheck.py`** (แทนfinalize_chapter11เก่า) คงmapและsnapshotเดิม ไม่prepareใหม่ คำแก้49ต้องcarryหลังcontext-recheck/context-full-readเดิมในบทต่อไป โดยใช้ฐาน42,450นี้ ไม่applyoverlayเก่าทับค่าล่าสุด

Ch.12ยังไม่เริ่มบทพูด: NIBLEญี่ปุ่น272รหัส (C3210 128 + NIBLE_QST03/Lament144) คงพักจนผู้ใช้สั่ง ต้องตรวจNPC/ไม่มีACTOR/ตัวเลือกทุกปุ่ม/กิจกรรมพื้นที่เดิมตามปลดล็อกเสมอ แหล่งวิดีโอเดิม: [คลิปผู้ใช้](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์ญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk) รอบนี้ไม่ได้ดูฟังครบใหม่
<!-- /chapter11-recheck-current -->

<!-- chapter11-current -->
## ล่าสุด: Chapter 11 — The Long Shadow of Shinra — 24 ตุลาคม 2026

ผู้ใช้สั่งเริ่ม Ch.11 แล้ว ส่วนนี้แทนคำแนะนำฐานปัจจุบัน/คำสั่งพักCh.11ในประวัติด้านล่าง เพิ่ม **1,703รหัส / 1,658แม่แบบ** รวม **42,394รหัส / 27assets / 721clusters** ฐานก่อนหน้า40,691ข้อความและACTORทุกตัวคงเดิมครบ รวมคำแก้บริบทสองรอบ1,290รหัส ห้ามassembleบทเก่า/รันfinalizerเก่าทับฐานนี้

ฐาน **E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter11-th.json** SHA256 **c8fe2b22ec6900aaff8bcc0cb5df589fce8974baf14aa0ac2483e7471df8c143**; patch translations/chapter11-th.json; แม่แบบ translations/chapter11/batch-01.json ถึง batch-10.json; inventory reference/chapter11-source.json; config reference/chapter11-build.json; map reference/through-chapter11-cluster-map.json; stage staging/ThaiJP_ThroughChapter11_Working; QA qa/chapter11 ดู [CHAPTER11-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER11-STATUS.md)

ทำบทหลักC3110ใหม่632รหัส, โปรโตเรลิกCHADL_QST06ทั้ง4ช่วง204รหัส, เควสต์Esoteric Secrets of the Elders246รหัสและMy White-Haired Angel176รหัส, บทต่อสู้NIBLS_BOS15/16 อีก46รหัส, NIBLT_NPC20ทุกสถานะ201รหัส รวมNIBLEใหม่1,505รหัส และResident198รหัส(Chadley/MAI/Odin/World Intel/PHOTO/Dale/Turner) รวมทั้งบรรทัดไม่มีACTOR ไม่พักNPCทั้งหมวด ตรวจย้อนNIBLEที่ยังญี่ปุ่น272รหัส เหลือC3210บท12จำนวน128กับLament of the Damned144รหัส มีเหตุผลรายID ไม่เริ่มบทพูดCh.12เอง ส่วนUIบทภายหลังที่แปลไว้แล้วคงเดิม

ยึดJPเป็นหลัก USรหัสเดียวกันใช้ป้ายชื่อและเทียบบริบท ไม่ดึงบทดัดแปลงUSมาแทนJP: เรื่องความทรงจำแซ็ก/โฮโจ/โรช/เรด/นิสัยคลาวด์/บิลลี่และแซม ตรวจตัวเลือกCh.11ครบ12กลุ่ม47รหัสพร้อมทุกปุ่มและบทตอบรับในข้อมูล; คงชื่อUIอังกฤษ แต่บทพูดใช้ไทย คงแมว**มารุ**จากCh.1และชื่อใหม่**ชิโระ**ตามJPเพื่อรักษาบทสนทนาเรื่องชื่อที่แปลว่ากลม/ขาว ชื่อNPCในบทพูดใช้ชื่อofficialUSทับศัพท์ เช่นนิค/คริสทีน/บิลลี่/วิล ไม่เดาเพศจากsuffix ผู้ดูแลและผู้พูดไม่ชัดใช้กลาง

คำลงท้ายรวม **1548ครั้งใน1509รหัส: ครับ1084 / ค่ะ308 / คะ156** NPC/nonparty1257ครั้ง รักษา1,278ครั้งเดิมครบ ตรวจผู้พูดที่เพิ่มตามหลักฐาน(บิลลี่ระบุชัดว่าเป็นลูกชายในJP) ไม่พบเพศสลับในทะเบียน ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ; เรียกCloudนาย/คุณ กลุ่มรวมCloudพวกนาย/พวกคุณ ไม่replaceเธอรวมทุกคน คงRedวัยหนุ่มฉัน/เอริธ/แซ็ก/เค็ตชี/โซลเจอร์/แมทีเรียตามศัพท์เดิม

ตรวจอ่านกลับtext/metadataทุกIDทั้งasset ผ่านgateUIเดิม6,907รหัส ตัวเลือกทั้งfamily7,218รหัส NPCเก็บตกเดิม8,347รหัส และชื่อท่าอังกฤษ1,703ป้าย เลขต่าง11รายการอ่านและบันทึกเหตุผลแล้ว เพิ่มclusterคั้/ง้/จื้/ชึ่แบบappend-only รักษา717assignmentและmetricsเดิมทั้ง8fonts/nativeASCIIเลขไอคอนเดิม/จุดไข่ปลาระดับล่าง ภาพproof12หน้า48panels96font samplesดูครบจริง รวม12กลุ่มคำถามครบทุกปุ่ม เป็นตัวอย่างการตัดบรรทัดจากglyphจริง ไม่ใช่ภาพเกมและไม่ใช่การฟัง/เล่นทุกแขนง

Finalมีเฉพาะ8ZIPล่าสุด อัปเดต **ThaiJP_Chapter1_11_P.zip** (NIBLEใช้ร่วมCh.1จึงรวมกับMIDGR แทนThaiJP_Chapter1_P.zipเดิม) และ **ThaiJP_Common_P.zip** (Resident+ฟอนต์) อีก6ZIPhashเดิม อ่านกลับ8ZIP/24modfiles/27assetsรวมกันผ่านไม่มีซ้ำ สำรองรุ่นเดิมนอกFinalที่qa/final-parts/runs/08598cfac07348f599045f745855a7b2/previous-final ไม่ติดตั้ง/ไม่แก้ไฟล์เกมหรือdist

สร้างซ้ำ: tools/assemble_chapter11.py → tools/build_chapter11.py(เต็มเมื่อมีglyphใหม่; --text-onlyเมื่อmapเดิม)/--verify → tools/audit_shared_dialogs.py(รวมgateCh11ใหม่+regressionเก่า) → tools/audit_chapter11_glyphs.py → tools/preview_chapter11.py/ดูภาพจริงก่อนsignoff → tools/signoff_chapter11.py → tools/publish_final_parts.py → tools/finalize_chapter11.py คงreference/context-recheck-overrides.jsonและcontext-full-read-overrides.jsonโดยให้full-readชนะค่ารอบเก่า; frozenbaseมีทั้งสองชุดแล้ว ไม่เรียกoverlayเก่าทับfull-readตรงๆ ห้ามprepare_chapter11ซ้ำ/แก้snapshotในqa/chapter11/revisions

อ้างอิงภาพผู้พูด/เสียงยังใช้[คลิปผู้ใช้](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk)ตามHANDOFFเดิม รอบCh.11นี้ไม่อ้างดู/ฟังวิดีโอครบใหม่ ไม่ถือauto transcriptเป็นบทถูกต้อง งานต่อไปเมื่อผู้ใช้สั่งCh.12: ตั้งinventoryจากฐาน42,394นี้ รวมC3210/NIBLE_QST03, คู่แข่งQBหลังCh.12, Gold Cup/การกลับพื้นที่เก่าและกิจกรรมที่ปลดล็อกใหม่ ต้องตรวจNPCไม่มีACTOR คำถามทุกปุ่ม และสรรพนามตามบริบทอีกครั้ง
<!-- /chapter11-current -->

<!-- context-full-read-current -->
## ตรวจครบชุดข้อความ Ch.1–10 + Common ที่แปลไว้แล้ว — 23 ตุลาคม 2026

**รีเช็คชุดข้อความปัจจุบันครบแล้ว 40,691 รหัส คิวค้าง 0 รหัส** บทหลัก Ch.1–10 จำนวน7,543รหัส รวมบทหลัก/NPC/เควสต์/Commonภาษาไทย32,841รหัสอ่านเทียบ JP/ไทย ส่วนป้ายอังกฤษและสัญลักษณ์7,850รหัสตรวจ JP/USรหัสเดียวกัน เปิดอ่านความต่าง495รายการและcandidateนอกหมวดชื่อ1,049รายการ รวมเงื่อนไขGambitและคำอธิบายที่ตกไป จัดคำตัดสินรายรหัสในenglish-completion-review.json ไม่อ้างว่า7,355ชื่อที่ตรงUSเป็นการอ่านบทพูดไทยใหม่ และไม่ใช่การเล่น/ฟังทุกแขนงในเกม คำถามตรวจพร้อมทุกปุ่มและบทตอบรับเมื่อมีบริบทให้เทียบ ไม่ถือผลscriptผ่านเป็นการอ่านความหมายทุกบรรทัด

รอบอ่านละเอียดแก้เพิ่ม **930 รหัส** จากรอบคัดกรองเดิม368รหัส รวมรอบบริบทสองชุด **1290 รหัส** ตัวอย่าง: ภาวะโดนพิษมาโก้, เซทรา, ห้องโดยสารชั้น2, หัวหน้าหน่วยพาเหรด, การขายโรงแรม, คำปฏิเสธ/คำพูดหยอกของเอริธ, สรรพนามเรด, ชื่อยุฟฟี่/มีน่า/บรอนโก และประโยคตาม JP เมื่อ US ดัดแปลงต่างกัน คงทีฟ่า Ch.4 **เข้ามาสิ** และ Red **เชิญ** ตามที่แก้แล้ว

ฐานล่าสุด `translations/working-through-chapter10-th.json` SHA256 **63c3e1515ac4130a05bf8126af2a50362e6a7c832a2d81613c4559e8a1f43802** ยังคง40,691รหัส/27assets/717clusters คงID/ACTOR/tag/เลขliteral/ฟอนต์และcluster-mapเดิม ผ่านอ่านกลับstageและ **8 ZIP /24 modfiles /27assets** รวมกันไม่มีซ้ำ ใน **E:/FF7RebrithModTH/Mod/Final** แต่ละส่วนมีเฉพาะZIPล่าสุด สำรองนอกFinal ไม่ติดตั้งเกม ไม่อ้างฟัง/เล่นทุกแขนง Proofแก้เพิ่ม122หน้า976panels1952font samples ตรวจครบทุกpanel โดยดูภาพใหม่/ที่เปลี่ยนในcontact sheetsจริง และเทียบRGBกับmetadataตรงทุกจุดสำหรับpanelเดิมที่เคยดูแล้ว ดูvisual-review.jsonกับpanel-visual-reuse.json

หลักฐานใหม่ `reference/context-full-read-overrides.json`, `qa/context-full-read/queue.json`, `progress.json`, `corrections.json`, `audit.json`, `proof.json`, `visual-review.json`, `release-verification.json` และ checkpointผูกsourceใน `qa/context-full-read/releases/` คิวกับbaselineเป็นsnapshotห้ามprepareซ้ำ คิวชุดนี้ตรวจครบแล้ว งานต่อไปต้องตั้งขอบเขตบทใหม่โดยcarryoverrideทั้งสองชุดและgateเดิม ไม่เริ่มบทพูดCh.11หรือเนื้อหาที่พักไว้เอง ห้ามเขียนว่าทดสอบครบทุกแขนงจากยอดการตรวจรอบนี้

ใช้ `tools/context_full_read.py --show START END` อ่านจริง → `--record START END NOTES` เฉพาะช่วงที่อ่าน → เพิ่มก่อน/หลัง/เหตุผลรายIDลงcorrections → `--commit-reviewed` → assemble/build/verify/audit/proof/signoff/publishตามgateปัจจุบัน Overlayใหม่อยู่หลังcontext_recheckเดิม ต้องcarryทั้งสองชุดในบทถัดไป ห้ามรันfinalize_context_recheckเก่าที่hardcodeยอด368ทับรายงานล่าสุด

ข้อสังเกต: คำเชิญเข้าบ้านแซ็กในรอบก่อนเป็นactor zam (แม่แซ็ก) จึงไม่ใช้คำระบุว่าพ่อแซ็กเป็นหลักฐานเพศ ผู้พูดไม่ชัดใช้กลางตามเดิม ดูรายละเอียด [CONTEXT-FULL-READ.md](E:/FF7RebrithModTH/FF7Rebrith/CONTEXT-FULL-READ.md)
<!-- /context-full-read-current -->

## คำสั่งเพิ่มล่าสุด: คำเรียกคลาวด์

ผู้ใช้ส่งภาพโรช Ch.4 แล้วให้ตรวจคลาวด์โดนเรียกว่า “เธอ” ใช้ **นาย/คุณ** ตามน้ำเสียงเมื่อเรียกคลาวด์ และพวกนาย/พวกคุณสำหรับกลุ่มที่รวมเขา บิลใช้พ่อหนุ่มได้ อ่านผู้ฟังจริงจาก JP/US รหัสเดียวกันและประโยคก่อนหลัง; ไม่แทน “เธอ” ทั้งเกม เพราะบางบรรทัดกล่าวถึงผู้หญิงหรือเป็น NPC คุยกันเอง ผู้ฟังไม่ชัดใช้ประโยคกลางโดยไม่เติมเพศ

ตรวจ318รายการที่มีเธอ แก้สรรพนาม149รหัส (รวมผู้ชายอื่น/กลุ่ม/จดหมายถึงผู้เล่น), คง169รหัสตามบริบท โรชเรียก Cloud ทั้ง5จุดที่พบแก้แล้ว โดยภาพเป็น **นายเร็วขึ้นไปอีกแล้วนะ / สหายของฉัน** ดู [ทะเบียนรายรหัส](E:/FF7RebrithModTH/FF7Rebrith/qa/context-full-read/cloud-address-review.json) และ [บันทึกงาน23ตุลาคม](E:/FF7RebrithModTH/FF7Rebrith/qa/context-full-read/session-2026-10-23.md) ห้ามนับการค้นคำนี้เป็นการตรวจในเกมทุกฉากหรืออ่านคิวที่เหลือครบทั้งหมด

อ่านต่อ index **28,983** รายละเอียดรอบ 23 ต.ค. (แก้เพิ่ม53รหัส) และ candidate ป้ายสถานะอังกฤษ40560 ที่ต้องตรวจต่อ: [session-2026-10-23.md](E:/FF7RebrithModTH/FF7Rebrith/qa/context-full-read/session-2026-10-23.md)

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

<!-- chapter4-choice-current -->
## ล่าสุด: ทีฟ่าเข้ามาสิ + ตัวเลือกCh.4 — 20 ตุลาคม 2026

ตามภาพ/คำสั่งใหม่ ทีฟ่า `$C2120_MAIN_2700_0500_00_tif` ใช้ **เข้ามาสิ** แยกจากRedXIIIที่คง **เชิญ** แก้ตัวเลือกที่reuseคำว่า **ดู/ไม่ดู** ผิดบริบทครบ17ป้ายในJUNOE พร้อมป้ายเข้าร่วมพาเหรดที่มีtag1ป้ายและเกลาคำถามขึ้นด้านบน1ข้อความ รวมรอบนี้ **20ข้อความ** (ทีฟ่า1+ตัวเลือก18+คำถาม1) คำตอบขึ้นด้านบนเป็น **ขึ้นไป/ยังไม่ขึ้น**; กลุ่มลองใหม่/ฝึกพาเหรด/เข้าร่วมพาเหรด/FortCondor/ตามSalmon/เล่นJumpfrogใช้คำตอบให้ตรงกิจกรรม ครอบคลุม9กลุ่มคำถาม ตรวจภาพคำถามกับทุกปุ่ม3หน้าใช้glyphจริงแล้ว บทสอนคราฟต์Ch.2ยังใช้ดู/ไม่ดูถูกบริบทจึงคงไว้

ต้นเหตุคือCh4แม่แบบ364/365นำคำแปลはい/いいえจากบทสอนดูมาซ้ำ แก้generic defaultsเป็นใช่/ไม่ใช่ และper-IDoverrideแยกกิจกรรมในreference/chapter4-ui-overrides.json อัปเดตtranslations/chapter4-th.json+reused-lines.json+batch-03.json; tools/chapter4_choice_fix.py overlayท้ายassemble_chapter10.pyโดยอ้างsnapshotใหม่ qa/chapter4-choice-fix/baseline.json+revisions/ **ห้ามprepareซ้ำ/เปลี่ยนsnapshotเก่า** qa/chapter4-door-fixเดิมยังเป็นประวัติและgateประตูสะสมยอมเฉพาะ21IDที่reviewแล้ว(รอบก่อน2+รอบนี้20ซ้ำทีฟ่า1)

ฐานยัง **translations/working-through-chapter10-th.json — 40,691ข้อความ / 27assets / 717clusters** อีก40,671ข้อความและACTORทั้งหมดคงเดิม ทุกฟอนต์/อีก26assetsไบต์เดิม อัปเดตเฉพาะ **ThaiJP_Chapter3_4_5_P.zip** ใน E:/FF7RebrithModTH/Mod/Final อีก7ZIPhashเดิม อ่านกลับ8ZIP/24modfiles/27assetsผ่าน ไม่มีติดตั้ง/ทดลองตัวเลือกจริงในเกม

หลักฐาน [CHAPTER4-CHOICE-FIX.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER4-CHOICE-FIX.md), qa/chapter4-choice-fix/source-review.json(JP/USก่อนหลัง20ID), audit.json, proof-1.pngถึงproof-3.png, release-verification.json SignoffCh10ผูกhashใหม่ทุกไฟล์แล้ว ขั้นตอน: assemble_chapter10 → build_chapter10 --text-only/--verify → chapter10_recheck --quality → audit_shared_dialogs → audit_chapter10_glyphs → preview_chapter10 + chapter4_door_fix --preview + chapter4_choice_fix --preview/ดูภาพ → signoff_chapter10 → publish_final_parts → chapter4_choice_fix --finalize ไม่ใช้finalizeประวัติบทเก่าทับcontextใหม่ เมื่อมีการติดตั้งโดยผู้ใช้ก่อนเริ่มรอบ ให้ใช้protectedmanifestของsnapshotรอบล่าสุด คงdist/ต้นฉบับ/เกมที่ติดตั้งปัจจุบันระหว่างทำงาน
<!-- /chapter4-choice-current -->

<!-- chapter4-door-current -->
## ล่าสุด: แก้คำตอบเคาะประตู Ch.4 — 20 ตุลาคม 2026

ผู้ใช้ยืนยันให้แก้ภาพRedXIIIหน้าห้อง: เปลี่ยน **ถามสิ → เชิญ** ทั้ง2ID `$C2120_MAIN_2900_0100_00_red` และ `$C2120_MAIN_2700_0500_00_tif` ใน8200-JUNOE ต้นฉบับJPどうぞ, USRedYes?/TifaCome in. แม่แบบCh4#209เดิมreuseข้ามบริบท จึงเพิ่มper-IDoverrideในreference/chapter4-ui-overrides.jsonและแก้translations/chapter4/reused-lines.json+chapter4-th.json; assemble_chapter10.pyใช้overlay2IDท้ายการประกอบฐาน ห้ามรันassembleบทเก่าเพื่อทับฐานปัจจุบัน

ฐานยัง **translations/working-through-chapter10-th.json — 40,691ข้อความ / 27assets / 717clusters** คงอีก40,689ข้อความ/ACTORทั้งหมด/ทุกฟอนต์และอีก26assetsทุกไบต์ อัปเดตเฉพาะ **ThaiJP_Chapter3_4_5_P.zip** ใน E:/FF7RebrithModTH/Mod/Final อีก7ZIPhashเดิม อ่านกลับ8ZIP/24modfiles/27assetsผ่านไม่มีซ้ำ สำรองนอกFinal ไม่มีติดตั้งหรือทดสอบเกมจริง

หลักฐาน [CHAPTER4-DOOR-FIX.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER4-DOOR-FIX.md), qa/chapter4-door-fix/baseline.json+revisions/(ห้ามprepareซ้ำ), source-review.json(JP/USแยกID), audit.json, proof.png, release-verification.json; tools/chapter4_door_fix.py เก็บexceptionเฉพาะก่อนถามสิ/หลังเชิญ2ID ไม่ปล่อยให้แก้ฐานอื่นโดยพลการ gateCh10/recheck/continueยังทำงานและsignoffผูกhashoverlay/proofแล้ว ยอดเก็บตกเดิม144ไม่เปลี่ยน การแก้สะสมจาก40,547ตอนนี้61ข้อความที่มีอยู่เดิม(59รอบก่อน+2ประตู); ข้อความทุกIDยังครบ

ขั้นตอนต่อ: assemble_chapter10.py → build_chapter10.py --text-only → --verify → chapter10_recheck.py --quality → audit_shared_dialogs.py(รวมgateประตู) → audit_chapter10_glyphs.py → preview_chapter10.pyและchapter4_door_fix.py --preview/ดูproof → signoff_chapter10.py → publish_final_parts.py → chapter4_door_fix.py --finalize ไม่รันfinalize_chapter10_recheck/continueเดิมเพราะยังผูกbaselineก่อนแก้ประตู ข้อมูลยอด/คำว่าไม่แก้ฐานเก่าในบันทึกก่อนหน้านี้เป็นประวัติ ให้ใช้exception2IDนี้ต่อในบทถัดไป
<!-- /chapter4-door-current -->

<!-- chapter10-continue-current -->
## ล่าสุด: ตรวจความหมาย Ch.10 ต่อ — 20 ตุลาคม 2026

รอบต่อเนื่องนี้แก้ **18ข้อความที่มีอยู่แล้ว ไม่มีเพิ่ม/ลบID**: บทพูดอารมณ์/ประโยคเชื่อมของเอริธ, ตำนานที่แชดลี่ย์เล่า, ความอึดสู้ของบาร์เร็ต, ทิศทางเปรียบเทียบบาฮามุท, ช่องว่างชิปเอไอ, คอสตาเดลโซล, ลางบอกภัยพิบัติ และใช้ **โจโกโบะบิน** ให้ตรงบทสอนเดิมทั้งบทคุยกับข้อความช่วยเดินทาง คง **40,691ข้อความ / 27assets / 717clusters** ทุกID/ACTOR/glyph-mapเดิมครบ คำลงท้าย1,278ครั้ง(ครับ874/ค่ะ255/คะ149)ไม่เปลี่ยน ไม่เริ่มCh.11

อัปเดตเฉพาะ **ThaiJP_Chapter10_P.zip และ ThaiJP_Common_P.zip** ใน E:/FF7RebrithModTH/Mod/Final อีก6ZIPhashเดิม อ่านกลับ8ZIPรวม24modfiles/27assetsผ่านไม่มีซ้ำ ดูproofglyphจริง7หน้า56ตัวอย่างที่ครอบคลุม18ข้อความแก้และคำถาม/ทุกปุ่ม4ชุดแล้ว การตัดบรรทัดในproofเป็นตัวอย่าง ไม่ใช่ภาพเกม **ยังไม่ได้ติดตั้งหรือทดลองทุกแขนงในเกม/ฟังเสียงครบใหม่** จึงไม่รับรองว่าความหมายหรือruntimeไม่มีข้อผิดพลาด100%

หลักฐานใหม่: tools/chapter10_continue_review.py (prepareครั้งเดียว ห้ามซ้ำ), qa/chapter10/continue-review/current.json+revisions/ (ฐาน40,691ก่อนแก้), review.json (before/after18รหัส), release-verification.json และ [CHAPTER10-CONTINUE-REVIEW.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER10-CONTINUE-REVIEW.md) ใช้ฐาน translations/working-through-chapter10-th.json และขั้นตอนbuild/audit/signoff/publishเดิม เพิ่ม gateต่อเนื่องอัตโนมัติในaudit_chapter10_recheck.py; signoffผูกhashรายงานใหม่ไว้แล้ว ปิดเอกสารด้วย finalize_chapter10_recheck.py แล้ว finalize_chapter10_continue.py

ยอดด้านล่าง **เพิ่ม144/แก้59** เทียบกับCh.10ชุดแรก40,547: 59คือข้อความที่มีอยู่ในชุดแรก ส่วนรอบต่อเนื่อง18ประกอบด้วย16ข้อความจากชุดแรกและ2ข้อความจาก144ที่เก็บตก ห้ามนับ18เป็นจำนวนข้อความเพิ่ม ฐานก่อนCh.10ทั้ง37,830ยังคงเดิม
<!-- /chapter10-continue-current -->

<!-- chapter10-recheck-current -->
## ล่าสุด: รีเช็ค Ch.10 และส่วนกลางที่เกี่ยวข้อง — 20 ตุลาคม 2026

ส่วนนี้แทนยอด/ขั้นตอนฐานปัจจุบันในประวัติด้านล่าง รีเช็คครั้งนี้ **เพิ่ม144รหัส แก้59รหัส** เหนือชุดCh.10เดิม40,547รหัส ปัจจุบัน **40,691รหัส / 27assets / 717clusters** งานCh.10และเก็บตกต่อเนื่องรวม2,861รหัส ไม่เริ่มบทหลักCh.11 ฐานยังเป็น **E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter10-th.json**; config reference/chapter10-build.json; stage staging/ThaiJP_ThroughChapter10_Working; map reference/through-chapter10-cluster-map.json

ต้นเหตุที่พบ: การเลือกฉากCosmoเพียงassetเดียวทำให้ฉากปิดโปรโตเรลิกที่ใช้FOREEร่วมกันตกหล่น เช่นเดียวกับResidentบทรายงานหลังฉาก/เรียกบริการCid/แจ้งแรงก์การ์ด รีเช็คเพิ่มfamilyอิสระใน tools/chapter10_recheck_scope.py และ gate tools/audit_chapter10_recheck.py ครอบคลุมFOREE50รหัส(ปิดJunon12/Gongaga22/Cosmo16) และResident94รหัส(รายงานโปรโตเรลิก23, Cid9, สำรวจCosmo4, เปิดBahamutArisen3, ช่วยการเดินทาง4, แรงก์การ์ด22, ทีฟ่าไปเตาปฏิกรณ์Gongaga3, Chadleyกลับเยือนเมืองเดิม26) เก็บordinaryreturnทุกพื้นที่ที่เยือน รวมสถานะหลังจบรายงาน โดยพักเฉพาะNibelที่ยังไม่เยือน ไม่พักทั้งnamespaceจากเลขสถานะ

แก้คำแปลเดิม59รหัส รวม **マルケเป็นวัตถุดิบมาร์เค ไม่ใช่มาร์ล**2จุด, ประโยคถูกขัดจังหวะ/ความรู้สึกอึดอัด/ผืนดินแยกออก/ความมุ่งมั่น และใช้คำเรียกพิธีส่งวิญญาณสู่ดวงดาวกับศาสตร์ชีวิตดวงดาวสม่ำเสมอ คงฐานก่อนCh.10ทั้ง37,830ข้อความและACTORครบ; ชุดCh.10เดิม40,547IDไม่หาย ACTORเดิมคงครบ มีรายการbefore/afterทุกรหัสใน qa/chapter10/recheck/review.json

ตรวจข้ามassetรหัสC2910/C3010ครบ917รหัส เพิ่มจากการตรวจselectorเดิม; ตรวจคำถาม/ตัวเลือกทั้งfamily7,218รหัส, NPCหมวดพื้นที่ที่เยือน5,638รหัส(ไม่มีACTOR4,989), รักษาinventoryเก็บตกNPCเดิม8,347รหัสและชื่อท่าอังกฤษ1,703ป้าย อ่านย้อนทุกID/metadata/tagจากsourceเทียบstageรวม40,691ข้อความ สแกนResidentที่ยังเป็นญี่ปุ่นทุกตัวอีกชั้น **1,234รหัส** มีเหตุผลรายIDใน Resident-residual-dispositions.json: Nibel/บทภายหลัง/เควสต์ใหม่, ชีวประวัติและคำแนะนำวิเคราะห์ศัตรูที่ยังเป็นหมวดไม่ได้เริ่ม, UIdemoที่ไม่ใช้ในretail ไม่อ้างว่าญี่ปุ่นทุกประเภททั้งเกมหมดแล้ว

คำลงท้ายปัจจุบัน **1,278ครั้งใน1,246รหัส: ครับ874/ค่ะ255/คะ149** NPC/nonparty1,094ครั้ง รักษา976ครั้งก่อนCh.10ครบ ตรวจไม่พบสลับเพศหรือผู้พูดที่ยังไม่มีหลักฐาน Unknownใช้กลาง ไม่เดาเพศจากmma/mfa ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ; เอริธ/แซ็ก/เค็ตชี/กอนกาก้า/โซลเจอร์/โพชั่นตามฐานเดิม; ป้ายUSอังกฤษชื่อเดียวกัน ชื่อเรจี้/นาบารา/ไวซ์ในบทพูดเทียบฐานเดิมแล้ว

เพิ่มcluster **ฉี่** อีก1ตัวแบบappend-only รวม717 คง716assignment/metricsเดิมครบ8fonts/nativeASCIIเลขไอคอนพิกเซลเดิม/ระดับ…ล่าง อ่านproofglyphจริง7หน้า56ตัวอย่างรวมคำถามและทุกปุ่ม4ชุดแล้ว ตรวจความต่างตัวเลข27รายการพร้อมเหตุผล บางmaskไทยเดิมอาจต่างเล็กน้อยจากrepackBC5 ไม่อ้างพิกเซลไทยเดิมครบทุกตัว

อัปเดต **Chapter1 / Chapter2 / Chapter10 / Common** ใน E:/FF7RebrithModTH/Mod/Final อีก4ZIPhashเดิม ทั้ง8ZIPต้องใช้ร่วมกัน อ่านกลับรวม24modfiles/27assetsผ่านไม่มีซ้ำ สำรองนอกFinal ไม่ติดตั้ง/ไม่ทดลองในเกมหรือเล่นทุกแขนง/ไม่อ้างฟังวิดีโอครบใหม่ source/dist/ไฟล์ที่ติดตั้งคงเดิม

ไฟล์ส่งต่อเพิ่ม: reference/chapter10-recheck-source.json (144ID, indexappend-only), translations/chapter10-recheck-lines.json, qa/chapter10/recheck/current.json+revisions/(ห้ามprepareซ้ำ), review.json, terminology-decisions.json, Resident-residual-dispositions.json, release-verification.json รายละเอียด [CHAPTER10-RECHECK-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER10-RECHECK-STATUS.md)

ขั้นตอนล่าสุด: assemble_chapter10.py → build_chapter10.py --text-only(เมื่อmapคงเดิม)/เต็มเมื่อเพิ่มglyph → --verify → chapter10_recheck.py --quality → audit_shared_dialogs.py(รวม2gateCh.10+regressionเดิม) → audit_chapter10_glyphs.py → preview_chapter10.pyและดู7หน้า → signoff_chapter10.py → publish_final_parts.py → finalize_chapter10_recheck.py **ห้ามใช้finalize_chapter10.pyเดิมที่ยังผูกยอดก่อนรีเช็ค** บทถัดไปใช้ฐาน40,691นี้ คงflagทั้งหมดและเพิ่มgate/signoffใหม่ก่อนส่ง ต้องคง144รหัสเก็บตกใหม่และทะเบียนNPC/ตัวเลือกด้วย
<!-- /chapter10-recheck-current -->

<!-- chapter10-current -->
## ล่าสุด: Chapter 10 — Watcher of the Vale — 20 ตุลาคม 2026

ส่วนนี้แทนข้อมูลฐานปัจจุบันทั้งหมดในประวัติด้านล่าง เพิ่ม **2,717 รหัส / 2,617 แม่แบบ** รวม **40,547 รหัส / 27 assets / 716 clusters** รักษาฐานเดิม 37,830 ข้อความและ ACTOR ครบ ไม่เริ่ม Ch.11

ฐานล่าสุด **E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter10-th.json**; patch translations/chapter10-th.json; config reference/chapter10-build.json; map reference/through-chapter10-cluster-map.json; stage staging/ThaiJP_ThroughChapter10_Working; QA qa/chapter10 รายละเอียด [CHAPTER10-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER10-STATUS.md) ห้ามใช้ฐาน enemy-actions/NPC/choice/Ch.9 เดิมทับงาน Ch.10 และห้าม prepare_chapter10 ซ้ำ

ทำบทหลัก Cosmo Canyon/หอดูดาว/พิธีส่งคืนสู่ดวงดาว/บททดสอบ Nanaki/เผ่า Gi/ก่อนออกจากหุบเขา และ Zack ใน MIDGR; เควสต์ Bonds of Trust, Absence of a Sign, From Whence Life Flows, Promises to Keep; โปรโตเรลิก Gears and Gambits ครบ4การทดสอบและบทอวาแลนช์; NPC Cosmo649รหัสครบทุกสถานะ รวมไม่มี ACTOR597รหัส และ MIDGR_NPC10อีก185รหัส รวม NPC ใหม่834รหัส/ไม่มี ACTOR771รหัส; Resident238รหัสรวม Chadley/MAI/World Intel/PHOTO/CARDG_QST15 ทั้ง3คู่แข่ง

ตรวจ inventory NPC พื้นที่ที่เยือนรวม5,638รหัส ไม่มี ACTOR4,989รหัส รักษา inventory เก็บตก NPC เดิม8,347รหัส และชื่อท่าศัตรูอังกฤษ1,703ป้ายครบ ตรวจคำถาม/ทุกตัวเลือกทั้งfamily7,218รหัส รวมบทสอน/ค่ายพัก/ชื่อเควสต์/เกมย่อยตาม gate เดิม ไม่ตรวจเฉพาะฉากหลักหรือเฉพาะ *_sys สแกนย้อนทุกข้อความญี่ปุ่นที่ยังเหลือในไฟล์ฉากที่เยือนและแยกเหตุผลรายรหัส2,774รายการ ส่วนของ Cosmoเหลือเฉพาะเควสต์ใหม่ Ch.12 Victim of Circumstance66รหัส ไม่พัก NPC_30 ทั้งหมวด

คำลงท้ายรวม **1,195ครั้งใน1,170รหัส: ครับ791 / ค่ะ255 / คะ149** รวม NPC/nonparty1,011ครั้ง รักษา976ครั้งเดิมครบ เพิ่ม219ครั้งตามหลักฐานผู้พูด ตรวจไม่พบสลับเพศ/ผู้พูดที่ยังไม่มีหลักฐาน ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ Unknown NPC ใช้กลาง ไม่เดาจาก mma/mfa Wedgeป้ายชื่อชัดใช้ชาย ส่วน???ใช้กลาง Aerithพูด **เอริธ**, Zack **แซ็ก**, Cait Sith **เค็ตชี**, Gongaga **กอนกาก้า**, SOLDIER **โซลเจอร์**, Potion **โพชั่น** ป้ายผู้พูด/UI อังกฤษตาม US รหัสเดียวกัน คง Gz เป็นหน่วยวัดในคำถามตามต้นฉบับ

เพิ่ม5clusters งึ/บื/บู๊/ว็/อู แบบappend-only รักษา711assignment/metricsเดิมทั้ง8fonts และnativeASCII/เลข/ไอคอนพิกเซลเดิม คงระดับจุดไข่ปลา…ต่ำเท่าจุดเต็ม ไทยเก่าอาจมีความต่างจากการบีบอัดBC5เล็กน้อยหลังrepack ไม่อ้างว่าพิกเซลไทยเดิมเหมือนทุกตัว ดูproof glyphจริง5หน้า รวมคำถามและทุกปุ่ม4ชุดแล้ว ตรวจความต่างตัวเลข26รายการพร้อมเหตุผล

Final มี **8 ZIPล่าสุดแยกส่วน** ต้องใช้ร่วมกัน เพิ่ม **ThaiJP_Chapter10_P.zip** ถือ COSMEทั้งasset ย้ายออกจากCommonไม่ซ้ำ อัปเดต **ThaiJP_Chapter1_P.zip** เพราะMIDGRใช้ร่วมกับZackCh.10 และ **ThaiJP_Common_P.zip** เพราะResident/ฟอนต์ อีก5ZIPคงhashเดิม อ่านกลับรวม24modfiles/27assetsไม่มีซ้ำ สำรองนอกFinal ไม่ติดตั้ง/ไม่ทดลองในเกม/ไม่อ้างฟังวิดีโอครบใหม่ ต้นฉบับ/dist/ไฟล์เกมคงเดิม

ขั้นตอน: assemble_chapter10.py → build_chapter10.py(เต็มเมื่อมีglyphใหม่; --text-onlyเมื่อmapคงเดิม) → --verify → audit_shared_dialogs.py(รวมaudit_chapter10.py, regressionชื่อท่า/NPCเดิม) → audit_chapter10_glyphs.py → preview_chapter10.pyและดู5หน้า → signoff_chapter10.py → publish_final_parts.py → finalize_chapter10.py บทต่อไปต้องขยายgate/signoffของsourceใหม่ก่อนแพ็ก คงทุกflagในactive context ไม่รันaudit/finalizeบทเก่าทับcontext
<!-- /chapter10-current -->

<!-- enemy-actions-current -->
## ล่าสุด: ชื่อท่าศัตรูอังกฤษทั้งหมวด — 19 ตุลาคม 2026

ส่วนนี้แทนพาธ/ยอดปัจจุบันในประวัติด้านล่าง แก้ชื่อท่าในภาพ **灼熱ブレス → Scorching Breath** รหัส $bt_MidgarZolom_Flamethrower เทียบ US รหัสเดียวกัน ตรวจทั้ง Resident หมวด $bt_ และ $EN9000_10_ **1,703 ชื่อ/ป้ายการใช้ท่า** เพิ่ม **1,668 รหัส** (ญี่ปุ่น 1,667 + ป้ายไม่ทราบชื่อ ？？？？→??? ตาม US 1 รหัส) รักษาชื่ออังกฤษเดิม 35 รหัสและคำอธิบายไทย *_help เดิมทั้ง 12 รหัส ไม่เพิ่มบทพูดบทถัดไป

ฐานรวมปัจจุบัน **37,830 รหัส / 27 assets / 711 clusters** ที่ **E:/FF7RebrithModTH/FF7Rebrith/translations/working-enemy-actions-th.json**; config reference/enemy-actions-build.json; map reference/enemy-actions-cluster-map.json; stage staging/ThaiJP_EnemyActions_Working; QA qa/enemy-actions รายละเอียด [ENEMY-ACTIONS-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/ENEMY-ACTIONS-STATUS.md) ใช้ฐานนี้ต่อ ห้ามฐาน NPC/choice/Ch.9 เดิมทับงานใหม่

รอบนี้แทนป้ายในหมวดการใช้ท่าตาม US รหัสเดียวกันครบ รวมชื่อศัตรู/บอสจากทั้งเกมและข้อความแสดงสถานะใน namespace เดียวกัน คงชื่อทางการและเครื่องหมายตาม US รวม countdown One.../Two... และชื่อระดับ Crimson Breath I/II/III มีความต่างรูปแบบเลข JP/US 53 รายการ ตรวจ numeric-review.json แล้ว เป็นข้อความบน UI ไม่เปลี่ยนค่าพลัง/เวลา/จำนวนในระบบเกม บทพูดเดิม 36,162 รหัส/ACTOR และงานเก็บตก NPC/ตัวเลือกเดิมคงครบ

เปลี่ยนเฉพาะ Resident ใน **ThaiJP_Common_P.zip** ที่ E:/FF7RebrithModTH/Mod/Final ส่วน ZIP บททั้ง 6 คง hash เดิม อ่านกลับรวม 7 ZIP / 21 mod files / 27 assets ผ่านไม่มีซ้ำ สำรองชุด Common ก่อนแก้นอก Final ฟอนต์ทั้ง 16 assets และ map คงไบต์เดิม จึงรักษาระดับจุดไข่ปลา/native ASCII/เลข/ไอคอนและตำแหน่งไทยเดิม ไม่ติดตั้งหรือทดสอบในเกม

ตรวจถาวรก่อนส่งบทต่อไป: คง enemy_actions/npc_recheck/choice_completion ใน active context; audit_shared_dialogs.py เรียก gate หมวดชื่อท่าด้วย บทใหม่จะใช้ audit_enemy_actions_regression.py รักษา 1,703 ป้าย และ audit_npc_regression.py รักษา inventory NPC 8,347 รหัส ต้องขยาย inventory NPC ตามบท/การปลดล็อกจริง ตรวจมี/ไม่มี ACTOR ทุกสถานะ ตัวเลือกทุกปุ่มและชื่อเป้าหมายทั้งหมวด ทำ inverse scan ข้อความที่เหลือพร้อมเหตุผลรายรหัส ห้ามพักทั้ง namespace จากเลขสถานะเพียงอย่างเดียว

ขั้นตอนรอบนี้: enemy_actions.py --prepare (ครั้งเดียว) → enemy_actions.py (text-only) → --verify → audit_shared_dialogs.py → preview_enemy_actions.py และดู 2 หน้า → enemy_actions.py --signoff → publish_final_parts.py → finalize_enemy_actions.py เมื่อเป็นบทใหม่ต้องเพิ่ม gate/signoff ผูก source ใหม่ใน publisher ห้ามใช้ finalize บทเก่าทับ active context ห้าม prepare ซ้ำ

ข้อกำหนดชื่อ/เพศ/ฟอนต์และรายละเอียด NPC เดิมใน NPC-RECHECK-STATUS.md ยังใช้: ชื่อพูดไทยตาม glossary, ACTOR/UI ชื่อทางการอังกฤษ; ชายครับ หญิงค่ะ/คะ/นะคะ unknown ใช้กลาง ไม่เดาเพศจาก mma/mfa; Aerith เอริธ; คำลงท้ายเดิม 976 ครั้งไม่เปลี่ยน 8 fonts จุดไข่ปลาระดับล่างเหมือนเดิม Common ยังถือ COSME เฉพาะ UI เมื่อทำบทที่ใช้ COSME ให้ย้ายทั้ง asset ไปเจ้าของใหม่ไม่ให้ซ้ำ
<!-- /enemy-actions-current -->

<!-- npc-recheck-current -->
## ล่าสุด: เก็บตก NPC Ch.2–9 และ Common — 19 ตุลาคม 2026

ส่วนนี้แทนพาธและยอดปัจจุบันในประวัติด้านล่าง เพิ่ม **1,573 รหัส / 1,515 แม่แบบ** เหนือฐาน 34,589 รหัส คงข้อความและ ACTOR เดิมครบ ปัจจุบัน **36,162 รหัส / 27 assets / 711 clusters** แก้ Akira ในภาพครบทั้ง 22 รหัส รวมผู้ชมและบท NPC กลับเยือนเมือง ตรวจ inventory **8,347 รหัส** รวม NPC มี/ไม่มี ACTOR และ shared WORLD/CARDG/MOGLE/PHOTO ไม่อ้างว่าเล่นครบทุกแขนงหรือฟังทุก NPC ใหม่แล้ว

ต้นเหตุที่ยืนยัน: เคยพัก KALMT_NPC_30 ทั้งหมวดตามสถานะตัวเลข ทำให้นักร้องและบทเมืองปกติตกไปด้วย อีกจุดคือบททะเลทราย/งาน Johnny/ตามหานกที่พักตอน Ch.7 ไม่ได้ถูกนำกลับมาตอนเปิดถึง Ch.9 รอบนี้รวมเควสต์ Corel 01–05 และโปรโตเรลิก 2 การทดสอบแรกแล้ว รวมเสียง Nanaki ทางเลือกและบทกลับเยือนของเควสต์เดิมด้วย ยังไม่เริ่มแปลบทหลัก Ch.10 หรือเควสต์ใหม่ที่เริ่ม Ch.12

ฐานต่อไป **E:/FF7RebrithModTH/FF7Rebrith/translations/working-npc-recheck-th.json**; config reference/npc-recheck-build.json; map reference/npc-recheck-cluster-map.json; stage staging/ThaiJP_NPC_Recheck_Working; QA qa/npc-recheck รายละเอียด [NPC-RECHECK-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/NPC-RECHECK-STATUS.md) ห้ามใช้ฐาน choice-completion/Ch.9 เดิมทับชุดนี้

ตรวจย้อนต้นฉบับในไฟล์ภูมิภาคที่เยือนทั้งหมด: *_NPC_* ครบ **4,804 รหัส** รวมไม่มี ACTOR **4,218 รหัส** และตรวจข้อความญี่ปุ่นทุกตัวที่ยังไม่แปลในไฟล์ฉากอีกชั้น เหลือ **2,708 รหัส** พร้อมเหตุผลรายรหัสใน visited-scene-residual-dispositions.json: บทหลัก/เควสต์ปลดล็อกภายหลัง, โปรโตเรลิกช่วงถัดไป, ฉากโบนัสท้าย Remake/INTERmission ไปคาล์ม 36 รหัส และ Test0 battle/debug 14 รหัส ไม่ใช่การยืนยันว่าทุกข้อความทั้งเกมแปลครบ

ฟอนต์ 16 assets/map 711 ตรงฐานก่อนรอบนี้ทุกไบต์ คง ASCII/เลข/ไอคอนและ … ระดับล่างทั้ง 8 fonts คำลงท้ายเดิม 976 ครั้งใน 952 รหัสคงเดิม: ครับ 651 / ค่ะ 198 / คะ 127; NPC/nonparty เดิม 838 ครั้ง ไม่มีคำลงท้ายใหม่ที่ต้องเดาเพศ Unknown NPC ใช้กลาง ไม่อนุมานเพศจาก mma/mfa; ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ ชื่อพูดไทยตาม glossary (Aerith เอริธ, Wutai อู่ไถ, Avalanche อวาแลนช์, Mako มาโก้); ACTOR/UI อังกฤษตาม US รหัสเดียวกัน Akira พูดชื่อ อากิระ / ป้าย Akira ตรวจ tag/metadata/ตัวเลขต่าง 17 รายการแล้ว

Final มี 7 ZIP ล่าสุดแยกส่วน ต้องใช้ร่วมกัน อ่านกลับรวม 21 mod files / 27 assets ไม่มีซ้ำ อัปเดต Ch.2, Ch.3–5, Ch.6–7, Ch.8, Ch.9 และ Common; Ch.1 ไบต์เดิม สำรองนอก Final ไม่ติดตั้งและไม่แก้ต้นฉบับ/dist/ม็อดในเกม Common ยังถือ COSME เฉพาะ UI ตัวเลือก เมื่อทำบทที่ใช้ COSME ต้องย้ายทั้ง asset ไป ZIP เจ้าของใหม่ไม่ซ้ำ

ขั้นตอนรอบนี้: assemble_npc_recheck.py → build_npc_recheck.py --text-only (ไม่มี glyph ใหม่) → --verify → audit_shared_dialogs.py (รวม audit_npc_recheck.py และ audit_npc_remaining.py) → preview_npc_recheck.py และดู proof 4 หน้า → signoff/numeric-review ผูก hash → publish_final_parts.py (อ่านกลับทุก ZIP รวมกัน) → finalize_npc_recheck.py ห้าม prepare ซ้ำ/สลับ index/เขียนทับ snapshot/รัน finalize บทเก่าทับ active context

**ทุกบทต่อไป:** ตรวจ NPC ทุกสถานะในพื้นที่ที่ทำ ทั้งมี/ไม่มี ACTOR พร้อม quest NPC, shared WORLD/CARDG/MOGLE/PHOTO และ namespace ข้างเคียง ตรวจตัวเลือกพร้อมคำถาม/ทุกปุ่ม/คำอธิบาย/ชื่อเป้าหมายทั้งหมวด เพิ่ม family/inventory ใหม่ก่อนแพ็ก ทำ inverse scan ทุกข้อความที่ยังไม่แปลในไฟล์ฉาก จัดเหตุผลรายรหัสตามเนื้อหาและเงื่อนไขปลดล็อกจริง ห้ามพักทั้งหมวดจากเลข NPC_30 หรือคำว่า return เพียงอย่างเดียว ขยายรายการเควสต์เดิมที่เปิดเพิ่มในบทใหม่ด้วย ไม่ตรวจเฉพาะฉากหลัก

audit_shared_dialogs.py จะเรียก audit_npc_regression.py เมื่อ active source เป็นบทใหม่ เพื่อกัน NPC 8,347 รหัสเดิมตกและไม่รีเซ็ต active context กลับมารอบนี้ บทใหม่ต้องสร้าง inventory/QA/signoff ของตัวเองและขยาย publisher gate ให้ตรวจ source ใหม่ด้วย ห้ามข้าม gate โดยปิด npc_recheck/choice_completion; ก่อนส่งต้องตรวจ glyph/ชื่อ/เพศ/ตัวเลขและอ่านกลับชุด ZIP จริงเสมอ
<!-- /npc-recheck-current -->

<!-- standing-choice-review -->
## ข้อกำหนดถาวร: ตรวจคำถามและตัวเลือกทุกบทก่อนส่งงาน

ผู้ใช้ย้ำ 18 ตุลาคม 2026: ทุกบทต่อไปต้องตรวจคำถามกับตัวเลือกทั้งชุด เช่น บทสอน ใช่/ไม่ใช่ เริ่มกิจกรรม ยกเลิก เล่นต่อ ลองใหม่ และออกจากกิจกรรม รวมทุกทางเลือกในหมวดที่เกี่ยวข้อง ไม่ตรวจเฉพาะภาพตัวอย่างหรือเฉพาะบทพูดหลัก ต้องค้นทั้งไฟล์ฉากและข้อความส่วนกลาง Resident/namespace ข้างเคียง รวม NPC ที่ไม่มี ACTOR ตรวจเทียบต้นฉบับกับข้อความใน staging และแพ็กที่ส่งจริง เพิ่มหมวดที่พบใหม่ใน tools/audit_shared_dialogs.py ก่อนแพ็ก ตรวจชื่อเฉพาะ ตัวเลข คำลงท้ายตามเพศ และระดับจุดไข่ปลาตามกฎเดิมด้วย แยกสถานะภายหลังที่อยู่นอกขอบเขตพร้อมเหตุผลรายรหัส และระบุชัดหากยังไม่ได้ทดลองตัวเลือกจริงในเกม
<!-- /standing-choice-review -->

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

<!-- ch12-current -->
## ชุดล่าสุดหลังตรวจ Ch.1–2 และแก้จุดไข่ปลา — 18 ตุลาคม 2026

ส่วนนี้แทนพาธ/ยอด/ขั้นตอนปัจจุบันทุกส่วนด้านล่าง รวม24,180รหัส24assets674clusters รักษางานCh.1–6เดิม23,811รหัส/ACTORครบ เพิ่ม330UI+39สรุปเปิดเกมTITLB ลด…U+2026ให้เสมอจุดASCII.ใน8fontsโดยเปลี่ยนเฉพาะoriginY พิกเซล/ระยะ/ASCII/ไอคอน/Thai/textureเดิมไม่เปลี่ยน ตรวจCh.1–2เดิม4,033รหัสครบ กัน52สถานะภายหลังไว้ ไม่มีJPเหลือในกลุ่มฉากที่คัดและUI362รหัสที่ตรวจ

ชุดรวมปัจจุบัน **E:/FF7RebrithModTH/FF7Rebrith/translations/working-ch12-recheck-th.json**; stage **staging/ThaiJP_Ch12_Recheck_Working**; glyph **reference/ch12-recheck-cluster-map.json**; config **reference/ch12-recheck-build.json**; QA **qa/ch12-recheck** ดู [CH12-RECHECK-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CH12-RECHECK-STATUS.md) สำหรับไฟล์/ขอบเขต/ข้อจำกัดทั้งหมด

ขั้นตอนปัจจุบัน assemble_ch12_recheck.py → build_chapter1.py --ch12-recheck-working --text-only(หากglyphไม่เพิ่ม) → verify_chapter1.py --ch12-recheck-working → audit_ch12_recheck.py → audit_shared_dialogs.py → preview_ch12_recheck.py(ดูภาพ) → publish_final_parts.py → finalize_ch12_recheck.py ห้ามprepareซ้ำ/เขียนทับsnapshot/ใช้auditหรือfinalizeบทเก่าทับcontext

**คำสั่งถาวรใหม่:** ทุกบทต้องตรวจshared Residentด้วย ทั้งคำถามบทสอน ใช่/ไม่ใช่ ยกเลิก ลองใหม่ การเลือกกิจกรรม เมนูย่อย คำอธิบาย/HUDและทางเลือกต่างสถานะทั้งหมวด เพิ่มfamilyใหม่ลงaudit_shared_dialogs.py ไม่อาศัย*_sysหรือเลขChapterอย่างเดียว ตรวจellipsisเทียบจุดnativeทุกฟอนต์ ใช้ชุดล่าสุดนี้เป็นฐานบทถัดไป คงproper-name/เลขอารบิก/คำลงท้ายตามเพศเดิม UnknownNPCกลาง รวมคำลงท้ายจริงยัง477ครั้งไม่มีเพิ่มจากUI/สรุปใหม่

Finalยัง5ZIP ต้องใช้ร่วมกันทั้งหมด อัปเดตเฉพาะCommon(18assetsเพิ่มTITLB) ZIPบททั้ง4คงเดิม อ่านกลับรวม24assetsไม่มีทับกัน สำรองนอกFinal ไม่ติดตั้ง ไม่ทดสอบเกมจริง ไม่อ้างว่าทวนวิดีโอใหม่ครบ บทCh.7ยังไม่เริ่ม เอกสารด้านล่างเป็นประวัติก่อนรอบนี้
<!-- /ch12-current -->

<!-- costa-activity-ui-current -->
## อัปเดตล่าสุด: เก็บ UI กิจกรรม Ch.6 เพิ่มเติม

18 ตุลาคม 2026: เพิ่ม **131 รหัส UI** จากรายการตรวจ **164 รหัส** ของกิจกรรม Costa del Sol คงข้อความอังกฤษ/ตัวเลข/สัญลักษณ์เดิมอีก33รหัส รวม UI Ch.6 **153รหัส** และชุดทั้งหมด **23,811รหัส / 23assets / 674clusters** บท/ตัวเลือกCh.6ยังเป็น1,698รหัส รวมNPC698รหัส ไม่ได้เพิ่มบทพูดหรือเริ่มCh.7

ครอบคลุม HUD/ปุ่ม/คะแนน/รางวัลของ Pirate's Rampage, Run Wild และ Wheelie, เมนู Card Carnival และปริศนาช่วงเริ่มต้น01–03ทั้งเวอร์ชันงานเทศกาล/หลังงาน รวมกล้อง แผนที่ ตั๋วกิจกรรมและคำบรรยายชุดชายหาด6ชุด ชื่อโหมดใช้ Free-For-All / Time Trial และชื่อโจทย์/ใบอนุญาตเป็นอังกฤษทางการตามUSรหัสเดียวกัน การ์ด Moogle Mage/Moogle Bard ใช้ชื่ออังกฤษแทนชื่อJP2号/3号โดยบันทึกข้อยกเว้นไว้ ไม่อ้างว่าปริศนาระดับหลังกลับเมือง11ขึ้นไปหรือGold Saucerเสร็จแล้ว

ตรวจ corpus ตามหมวดที่เลือกครบ แท็ก/ตัวแปรJPและค่าตัวเลขคงเดิม รักษาคำแปล23,680รหัสและACTORก่อนหน้าทุกจุด ฟอนต์/texture/scene assetsเดิมทั้งหมดไม่เปลี่ยน คำลงท้ายจริง477ครั้งยังผ่านผลตรวจเดิม ไม่เพิ่มคำระบุเพศในUI ภาพproof3หน้าใช้glyphจากstaging ตรวจภาพแล้ว แต่ไม่ได้ทดสอบการตัดบรรทัดในเกมจริง

รอบเก็บตกนี้อัปเดตเฉพาะ **ThaiJP_Common_P.zip** ใน `E:/FF7RebrithModTH/Mod/Final` ZIPบททั้ง4คงเดิมและยังต้องใช้ทั้ง5ส่วนร่วมกัน อ่านกลับทั้ง5ZIPรวม23assetsผ่าน ไม่มีassetทับกัน สำรองCommonรุ่นเก่านอกFinal ไม่ได้ติดตั้งลงเกม

ไฟล์ใต้ฐาน `E:/FF7RebrithModTH/FF7Rebrith/`:

| หน้าที่ | พาธ |
| --- | --- |
| JP/USและรายการครบตามหมวด/สิ่งที่กันไว้ | reference/chapter6-activity-ui-source.json, chapter6-activity-ui-scope.json |
| คำแปล129ข้อความญี่ปุ่น/อักษรเต็มความกว้าง + ชื่อโหมดอังกฤษ2รหัส | translations/chapter6-activity-ui-th.json |
| สคริปต์คำแปล/สร้างชุดรวม | tools/chapter6_activity_ui.py, assemble_chapter6.py |
| ตรวจเก็บตก/ภาพตัวอย่าง | tools/audit_chapter6_activity_ui.py, preview_chapter6_activity_ui.py |
| QA/หลักฐาน/ผลแพ็ก | qa/chapter6/activity-ui/audit.json, proof.json, proof-1.png ถึง proof-3.png, release-verification.json |
| Snapshotก่อนรอบเก็บตก ห้ามทับ | qa/chapter6/activity-ui/baseline.json และ revisions/ |

แก้คำแปลในJSONหรือสคริปต์ที่สร้างJSONให้ตรงกัน รัน `assemble_chapter6.py` → `build_chapter1.py --chapter6-working --text-only`(เมื่อไม่เพิ่มglyph) → `verify_chapter1.py --chapter6-working` → `audit_chapter6.py` → `audit_chapter6_activity_ui.py` → `audit_chapter6_editorial.py` → `audit_gender_through_chapter6.py` → `preview_chapter6_activity_ui.py`(ดูภาพ) → `publish_final_parts.py` → `finalize_chapter6.py` สคริปต์สุดท้ายเรียก `finalize_chapter6_activity_ui.finish()` ด้วย อย่ารัน `chapter6_activity_ui.py --prepare` ซ้ำหรือเขียนทับsnapshot หากมีการแก้รอบใหม่ต้องตั้งbaselineรอบใหม่และเทียบหลักฐานเดิมไว้ด้วย
<!-- /costa-activity-ui-current -->

อัปเดตล่าสุด **18 ตุลาคม 2026 — หลัง Chapter6 (Asia/Bangkok)** ข้อมูลส่วนนี้แทนพาธ/ยอด/สถานะปัจจุบันของCh.5ในประวัติด้านล่าง คำสั่งใหม่ผู้ใช้มีลำดับเหนือเอกสารเสมอ

## ชุดปัจจุบันและงานที่เสร็จ

- เสร็จ Ch.1–6 ตามขอบเขตแต่ละบท รวม **23,811รหัส / 23assets / 674clusters** Ch.6เพิ่มบท/ตัวเลือก1,698รหัส รวมNPC698(ไม่มีACTOR612) และUI153รหัส แยก107รหัสสถานะภายหลังออก ไม่ได้แปลบทCh.7–14
- ชุดรวม [working-through-chapter6-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter6-th.json), staging [ThaiJP_ThroughChapter6_Working](E:/FF7RebrithModTH/FF7Rebrith/staging/ThaiJP_ThroughChapter6_Working), QA [chapter6](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter6), [active-working-set.json](E:/FF7RebrithModTH/FF7Rebrith/qa/active-working-set.json)
- [Final](E:/FF7RebrithModTH/Mod/Final) มี **Chapter1/Chapter2/Chapter3_4_5/Chapter6/Common ทั้ง5ZIPต้องใช้ร่วมกัน** รวม15mod files23assets เปิดอ่านกลับร่วมกันแล้วไม่มีassetซ้ำ Chapter1/2/3_4_5ZIPคงเดิม เพิ่มChapter6และแก้Common สำรองZIPเก่านอกFinal
- รักษาCh.1–5เดิม21,960รหัสและACTORครบ เพิ่มglyph14แบบappend-only660→674 รักษาLatin/ตัวเลข/ไอคอน/พิกเซล/ระยะ/แนวHเดิม8ฟอนต์ ต้นฉบับเกม,distเก่า,ม็อดที่ติดตั้งไม่เปลี่ยน ยังไม่ได้ติดตั้งชุดใหม่หรือทดสอบเล่น/ฟังเสียงNPCครบใหม่

## กฎคำแปลและเพศ

แปลจากJP ชื่อที่กล่าวในบทพูด/Dialogueเป็นไทย ACTORและชื่อเฉพาะในUIเป็นอังกฤษทางการ ชื่อไอเทม/สกิลในเมนูอังกฤษ ความสามารถไทย ชื่อChapterอังกฤษ ช่วงเวลาอดีต/ปัจจุบันไทย ใช้เลขอารบิกเมื่อเป็นค่าชัดเจน เช่น เซคเตอร์7 แต่คงสำนวนไม่เจาะจง คงแท็ก/ตัวแปรJPและmetadataอื่น

ชายใช้ครับ หญิงใช้ค่ะบอกเล่า/คะคำถาม/นะคะตามน้ำเสียง ไม่เติมทุกบรรทัด ตรวจทั้งผู้พูด ผู้ฟัง และคนถูกกล่าวถึง ไม่เดาเพศจากmma/mfaหรือรหัสโมเดล ถ้าไม่ยืนยันใช้ถ้อยคำกลาง Ch.6มี27รหัสระบุเพศจริง เป็นJohnnyที่JPแนะนำว่า男ジョニー คัดทวนความสัมพันธ์/สรรพนาม171รหัส(รวมคำธรรมดาที่ค้นติด) ไม่พบคำลงท้ายสลับเพศในข้อมูลที่ตรวจ

ทั้งชุดCh.1–6 ครับ/ค่ะ/คะจริง **477ครั้งใน467รหัส: ครับ335 ค่ะ83 คะ59** NPC/ตัวละครนอกปาร์ตี้434ครั้ง ไม่รวมเสียงติดอ่างคะ…ในคะ…ครับ! ผล [summary.json](E:/FF7RebrithModTH/FF7Rebrith/qa/gender-through-chapter6/summary.json) และ [records.json](E:/FF7RebrithModTH/FF7Rebrith/qa/gender-through-chapter6/records.json) ไม่อ้างว่าNPCทุกคนถูกยืนยันจากวิดีโอ

ใช้Wutai=อู่ไถ Red XIIIบนป้ายและ“เรด”ในบทพูดปัจจุบัน ศัพท์Ch.6ที่ยืนยันPlearn: จอห์นนี่/วิสเปอร์/อิฟาลน่า/โกลด์ซอซเซอร์ อ้างอิงรายรหัสใน [proper-name-review.json](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter6/proper-name-review.json) คำใหม่ที่ถอดจากJPแยกต่างหาก ไม่อ้างPlearnรับรอง

## ไฟล์และวิธีทำต่อ

พาธฐาน **E:/FF7RebrithModTH/FF7Rebrith/**:

| หน้าที่ | ไฟล์ใต้พาธฐาน |
| --- | --- |
| JP/US รายรหัส/แม่แบบ/ขอบเขต | reference/chapter6-source.json, chapter6-templates.json, chapter6-scope.json |
| สถานะภายหลัง107รหัส/ชื่อUI | reference/chapter6-deferred.json, chapter6-ui-overrides.json |
| คำแปลแก้ได้ | translations/chapter6/batch-00.json ถึง batch-08.json และ reused-lines.json |
| UI22รหัส | reference/chapter6-ui-source.json, translations/chapter6-ui-th.json |
| glyph/staging | reference/through-chapter6-cluster-map.json, staging/ThaiJP_ThroughChapter6_Working |
| Snapshotห้ามทับ | qa/chapter6/baseline.json และ revisions/ |
| ตรวจขอบเขต/ชื่อ/เพศ/ฟอนต์ | qa/chapter6/translation-audit.json, contextual-gender-review.json, proper-name-review.json, verification.json, runtime-baseline-check.json, font-proof.png |
| ชุดส่งมอบ/ผลเปิดร่วม | qa/final-parts/latest.json, combined-mount-verification.json, qa/chapter6/release-verification.json |
| รายละเอียดขอบเขตและขั้นตอน | CHAPTER6-STATUS.md, FINAL-PARTS.md |

ต้นฉบับ **E:/FF7RebrithModTH/FF7Rebrith/source/End/Content/Text/JP** และ **US** รหัสเดียวกัน Python **C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe** ตั้ง `$env:PYTHONUTF8='1'` จากโปรเจกต์ แล้วรัน `tools/assemble_chapter6.py` → `tools/build_chapter1.py --chapter6-working` → `tools/verify_chapter1.py --chapter6-working` → `tools/audit_chapter6.py` → `tools/audit_chapter6_activity_ui.py` → `tools/audit_chapter6_editorial.py` → `tools/audit_gender_through_chapter6.py` → `tools/preview_chapter6.py` → `tools/preview_chapter6_activity_ui.py`(ดูภาพด้วย) → `tools/publish_final_parts.py` → `tools/finalize_chapter6.py`

ห้ามรันprepare_chapter6.pyซ้ำหรือเปลี่ยนเลขแม่แบบ ห้ามauditบทเก่าทับactive-working-set ถ้าแก้ข้อความไม่เพิ่มglyphใช้build --text-onlyได้ มิฉะนั้นbuildฟอนต์เต็ม รักษาฐานCh.5เดิมครบ ทุกครั้งแก้เสร็จแพ็กZIPล่าสุดแยกส่วนลงFinalตามคำสั่งถาวร ติดตั้งเกมยังต้องมีคำสั่งแยก

## งานที่ยังต้องทำและแหล่งอ้างอิง

- บทCh.7–14ยังไม่เริ่ม เมื่อผู้ใช้สั่งCh.7ให้เริ่มจากภูเขาโคเรล/ภูมิภาค/เควสต์/NPC คัดตามเนื้อหา ตรวจdeferred107รหัสว่าแต่ละชุดใช้ช่วงไหน ไม่รวมทั้งหมดอัตโนมัติ
- CORLEเป็นassetร่วมCh.6–7; MIDGR/Residentอาจร่วมด้วย ตรวจownershipก่อนแพ็ก อย่าทำสองZIPมีassetเดียว ต้องรักษาCh.1–6เป็นฐาน
- deferredCh.2 52รหัส และCh.4 50รหัสยังเก็บแยกตามเหตุการณ์ภายหลัง ไม่ได้นับรวมในบทที่เสร็จ
- UI/ความสามารถไอเทม–สกิล/ชื่อศัตรูอังกฤษที่ทำทั้งเกมแล้วเป็นคนละหมวดกับบทพูด ยังไม่ได้แปลบทพูดทั้งเกม
- [คลิปผู้ใช้ให้](https://www.youtube.com/watch?v=i4gD0mmj5vc) เวลาที่มีหลักฐานบันทึกไว้Ch.4 12:23:04,Ch.5 21:30:39 ยังไม่มีเวลาCh.6ที่ตรวจใหม่ [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk) ใช้จับคู่ภาพผู้พูดกับJPดิบ ห้ามถือauto transcriptเป็นบทถูกต้องหรือหลักฐานว่าฟังครบ
- รอคำสั่งติดตั้ง/ภาพทดสอบจากเกมเพื่อตรวจการตัดบรรทัดและพื้นที่จริง ภาพglyph proofและการอ่านไฟล์กลับไม่แทนruntime test

## ประวัติ snapshot หลัง Chapter5

# ส่งต่องานม็อด FF7 Rebirth ซับไทย / เสียงญี่ปุ่น

อัปเดตล่าสุด **17 ตุลาคม 2026 — หลัง Chapter 5 (Asia/Bangkok)** ข้อมูลส่วนนี้แทนสถานะ Ch.4 และพาธ “ปัจจุบัน” ในประวัติด้านล่าง คำสั่งใหม่จากผู้ใช้มีลำดับเหนือเอกสารเสมอ

## สถานะล่าสุดและไฟล์ที่ใช้ต่อ

- เสร็จ Ch.1–5 ตามขอบเขตแต่ละบท รวม **21,960 รหัส / 22 assets / 660 glyph clusters**; Ch.5 เพิ่มบท/ตัวเลือก 1,316 รหัส (รวม NPC 581 มี 572 ไม่มี ACTOR) และ UI ร้านบนเรือ 7 รหัส ตรวจ UI บนเรือรวมครบ 99 รหัส
- แปลต้นฉบับ JP คง ACTOR/ชื่อใน UI อังกฤษทางการ ชื่อที่กล่าวในบทพูด/Dialogue ใช้ไทย Wutai = อู่ไถ; Red XIII ในป้ายชื่ออังกฤษ และในบทพูดปัจจุบันใช้ “เรด” ตาม JP レッド ใช้เลขอารบิก เช่น เซคเตอร์7 คงชื่อไอเทม/สกิลในเมนูอังกฤษและแปลความสามารถไทย
- ครับสำหรับผู้พูดชาย; ค่ะบอกเล่า/คะคำถาม/นะคะสำหรับหญิงตามบริบท ไม่เติมคำสุภาพทุกบรรทัด ไม่เดาเพศ NPC จากรหัสโมเดล หากไม่ยืนยันใช้ถ้อยคำกลาง รักษาเพศผู้ถูกกล่าวถึง/ผู้ฟังตาม JP ตรวจ Ch.5 เพิ่ม 21 รหัสระบุเพศและคำเรียก/ความสัมพันธ์ 83 รหัส ไม่มีคำลงท้ายสลับเพศในการตรวจนี้
- คำลงท้ายจริงทั้ง Ch.1–5 **456 ครั้ง / 446 รหัส**: ครับ314 ค่ะ83 คะ59; NPC/ตัวละครนอกปาร์ตี้413 ครั้ง ไม่รวม “คะ…” ติดอ่างใน “คะ…ครับ!” ดูรายรหัส [gender-through-chapter5](E:/FF7RebrithModTH/FF7Rebrith/qa/gender-through-chapter5/records.json)
- แพ็กเสร็จใน [Final](E:/FF7RebrithModTH/Mod/Final): Chapter1, Chapter2, **ThaiJP_Chapter3_4_5_P.zip**, Common ต้องใช้ทั้ง 4 ZIP ด้วยกัน ไม่มี asset ซ้ำ ชื่อใหม่ตามผู้ใช้แทน Chapter3_4 เก่าที่สำรองนอก Final แล้ว Chapter1/Chapter2 ZIP คงเดิม
- รักษางานเดิม20,637รหัสและ native ASCII/ตัวเลข/ไอคอน/ระยะ/แนว H เดิมครบ8ฟอนต์ เพิ่ม18clustersแบบ append-only ไม่เปลี่ยน source, dist หรือเกมที่ติดตั้ง ยังไม่ได้ลงชุดใหม่/ทดสอบเล่นจริง/ฟังเสียง NPC ครบใหม่

| หน้าที่ | พาธเต็ม |
| --- | --- |
| โปรเจกต์ | E:/FF7RebrithModTH/FF7Rebrith |
| คำแปลแก้ได้ | E:/FF7RebrithModTH/FF7Rebrith/translations/chapter5/batch-00.json ถึง batch-08.json และ reused-lines.json |
| ต้นฉบับคงเลข/ขอบเขต | E:/FF7RebrithModTH/FF7Rebrith/reference/chapter5-source.json, chapter5-templates.json, chapter5-scope.json |
| UI ร้าน7รหัส | E:/FF7RebrithModTH/FF7Rebrith/reference/chapter5-ui-source.json และ E:/FF7RebrithModTH/FF7Rebrith/translations/chapter5-ui-th.json |
| ชุดรวมปัจจุบัน | E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter5-th.json |
| ต้นฉบับ JP / US รหัสเดียวกัน | E:/FF7RebrithModTH/FF7Rebrith/source/End/Content/Text/JP และ E:/FF7RebrithModTH/FF7Rebrith/source/End/Content/Text/US |
| glyph map / staging | E:/FF7RebrithModTH/FF7Rebrith/reference/through-chapter5-cluster-map.json และ E:/FF7RebrithModTH/FF7Rebrith/staging/ThaiJP_ThroughChapter5_Working |
| QA ล่าสุด | E:/FF7RebrithModTH/FF7Rebrith/qa/chapter5 (translation-audit.json, contextual-gender-review.json, proper-name-review.json, font-proof.png, release-verification.json) |
| ชุดทำงาน/ผลแพ็ก | E:/FF7RebrithModTH/FF7Rebrith/qa/active-working-set.json และ E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/latest.json, combined-mount-verification.json |
| วิธีสร้าง/ขอบเขต/คำศัพท์/ผลตรวจละเอียด | E:/FF7RebrithModTH/FF7Rebrith/CHAPTER5-STATUS.md |
| Python | C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe |

## ขั้นตอนสำหรับแก้งานหรือรับช่วงต่อ

จากโฟลเดอร์โปรเจกต์ ตั้ง `$env:PYTHONUTF8='1'` แล้วเรียก Python ข้างต้นตามลำดับ `tools/assemble_chapter5.py` → `tools/build_chapter1.py --chapter5-working` → `tools/verify_chapter1.py --chapter5-working` → `tools/audit_chapter5.py` → `tools/audit_chapter5_editorial.py` → `tools/audit_gender_through_chapter5.py` → `tools/preview_chapter5.py` (ดูภาพด้วย) → `tools/publish_final_parts.py` ซึ่ง mount อ่านกลับทั้ง4แพ็กอัตโนมัติ ตรวจ latest.json และ release-verification.json หลังงาน

ห้ามรัน prepare_chapter5.py ซ้ำหรือเปลี่ยนเลขแม่แบบ อย่า reset active-working-set ด้วย audit บทเก่า ถ้าแก้ตัวบทโดย map ไม่เปลี่ยนใช้ build --text-only ได้ ถ้าเพิ่ม glyph ต้อง build ฟอนต์เต็ม รักษา baseline/snapshot รุ่นเก่าไว้ ไม่ใช้การ build/ภาพ proof แทนการทดสอบในเกม การแพ็กงานเสร็จลง Final อนุญาตแล้ว แต่ติดตั้งเกมต้องมีคำสั่งแยก

## แหล่งบท/ตัวละครและสิ่งที่ยังต้องทำ

- [คลิปหลักที่ผู้ใช้ให้](https://www.youtube.com/watch?v=i4gD0mmj5vc) — เวลาที่บันทึกไว้: Ch.4 12:23:04, **Ch.5 21:30:39** ใช้จับภาพผู้พูดกับ JP ต้นฉบับ ไม่ได้ดู/ฟังครบทุกบรรทัดใหม่ในการทำ Ch.5
- [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรกเสียงญี่ปุ่น](https://www.youtube.com/watch?v=bxrLsiU-QKk) ห้ามถือ auto transcript เป็นบทที่ถูกต้องหรือเป็นหลักฐานว่าฟังเสียงแล้ว
- บทพูด Ch.6–14 ยังไม่เริ่ม งาน Ch.5 หยุดก่อนฉากถึง Costa del Sol; เมื่อผู้ใช้สั่งบทถัดไปให้คัด NPC/ทางเลือก/บอส/กิจกรรมจากบริบท ไม่ตัดเพราะไม่มี ACTOR ไม่เปลี่ยนบทอนาคตโดยอาศัยตัวเลข ID เพียงอย่างเดียว
- คง deferred Ch.2 52 รหัส และ Ch.4 50 รหัสไว้จนถึงสถานะกลับมาเยือนที่ตรงเนื้อหา ไม่เอามานับว่ารวมอยู่ใน Ch.1–5 แล้ว
- ตรวจ asset ร่วมก่อนแยก ZIP บทต่อไป ต้องใช้ glyph map เดียวกันและห้ามสอง ZIP มี asset เดียวกัน ใส่เฉพาะ ZIP ล่าสุดแต่ละส่วนใน Final สำรองเก่านอก Final
- UI/ความสามารถไอเทม–สกิล/ชื่อศัตรูอังกฤษที่ทำทั้งเกมแล้ว ไม่หมายถึงบทพูดทั้งเกมแปลครบ หากมีภาพจากผู้ใช้ให้จับคู่รหัส ตรวจหมวดใกล้เคียง และแก้/แพ็กเฉพาะส่วนที่ได้รับผลกระทบ

## ประวัติและข้อมูลประกอบถึง Ch.4

ส่วนถัดไปคงรายละเอียดและแหล่งอ้างอิงเดิมไว้สำหรับตรวจย้อนหลัง พาธหรือสถานะที่เรียกว่า “ปัจจุบัน” ในส่วนนี้เป็น snapshot เก่า ให้ใช้ส่วน Ch.5 ด้านบนเป็นหลัก

## 1. เริ่มอ่านตรงนี้

ตรวจคำลงท้ายทั้งชุด Ch.1–4 เพิ่มเติมแล้ว: ครับ/ค่ะ/คะ ที่เป็นคำลงท้ายจริง **434 ครั้ง ใน 425 รหัส** ชายใช้ ครับ 292 ครั้ง หญิงใช้ ค่ะ/คะ รวม 142 ครั้ง ไม่พบสลับเพศหรือผู้พูดที่ยังไม่จับคู่หลักฐานในกลุ่มนี้ ป้าย ??? 10 รหัสเป็น Elena ก่อนแนะนำตัว ส่วน คะ…ครับ! ของทหารเป็นเสียงติดอ่าง ไม่ใช่คำลงท้ายหญิง ผลตรวจ [summary.json](E:/FF7RebrithModTH/FF7Rebrith/qa/gender-through-chapter4/summary.json) และ [หลักฐานรายรหัส](E:/FF7RebrithModTH/FF7Rebrith/qa/gender-through-chapter4/records.json) ใช้ `tools/audit_current_gender_particles.py` รันซ้ำ ไม่แก้คำแปล/ZIP/เกมในรอบตรวจนี้ ใช้หลักฐานผู้พูดเดิมและบริบท JP ไม่ได้ฟังวิดีโอใหม่ครบทุกบรรทัด

**ตรวจซ้ำล่าสุดเรื่องเพศ/NPC:** ตรวจ Ch.4 ครบ 3,206 รหัสและ NPC 890 รหัส (781 รหัสไม่มี ACTOR) ทวนคำลงท้าย/สรรพนาม/คำเรียก/ความสัมพันธ์ 436 รายการ ไม่พบ ครับ/ค่ะ/คะ สลับเพศ แต่แก้คำเรียกที่ตีเพศเกิน JP 15 จุด เช่น กลุ่มชายหญิงใช้ “ทุกคน” และคำทั่วไป “รุ่นใหม่” ไม่แปลเจาะจงเป็นผู้ชาย ดู [ผลรวม](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter4/gender-recheck/summary.json), [ก่อน–หลังทั้ง 15 จุด](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter4/gender-recheck/corrections.json) และ [บริบท/ความสัมพันธ์](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter4/gender-recheck/focused-review.json) อัปเดต ZIP Chapter3_4/Common แล้ว ตรวจเปิดร่วมทั้ง 4 ZIP ผ่าน ฟอนต์/ACTOR ไม่เปลี่ยน NPC ที่ยังยืนยันเพศไม่ได้ใช้ถ้อยคำกลาง ไม่ได้ฟัง/ดูคลิปทุก NPC หรือลงเกมใหม่

**สถานะล่าสุดหลัง Chapter 4:** แปลเพิ่ม **3,206 รหัส** รวมงานเดิม **20,637 รหัส / 22 assets / 642 glyph clusters** ครอบคลุมบทหลัก, NPC Junon 890 รหัส, ภารกิจเสริมเริ่มต้น 5 งาน และกิจกรรมในเขต Junon ดูขอบเขตและผลตรวจที่ [CHAPTER4-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER4-STATUS.md) มี 50 รหัสสถานะกลับมาเยือน/Corel ที่เตรียมคำแปลแล้วแต่แยกออกจาก binary รอบนี้ ไม่รวมบทเรือ Ch.5

ชุดรวมล่าสุด: [working-through-chapter4-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter4-th.json), [staging](E:/FF7RebrithModTH/FF7Rebrith/staging/ThaiJP_ThroughChapter4_Working), [active-working-set.json](E:/FF7RebrithModTH/FF7Rebrith/qa/active-working-set.json) ต้นฉบับและแม่แบบคงที่: [chapter4-source.json](E:/FF7RebrithModTH/FF7Rebrith/reference/chapter4-source.json), [chapter4-templates.json](E:/FF7RebrithModTH/FF7Rebrith/reference/chapter4-templates.json), [คำแปล 20 batch + reuse](E:/FF7RebrithModTH/FF7Rebrith/translations/chapter4), [deferred รายรหัส](E:/FF7RebrithModTH/FF7Rebrith/reference/chapter4-deferred.json), [ตารางฟอนต์](E:/FF7RebrithModTH/FF7Rebrith/reference/through-chapter4-cluster-map.json)

รายงานรอบแรกมีคำลงท้าย/สรรพนาม 181 lexical candidates (รวม ผม ที่หมายถึงเส้นผม 2 กรณี) อยู่ใน [gender-review.json](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter4/gender-review.json) ชาย ครับ; หญิง ค่ะ/คะ/นะคะ ตามบริบท; NPC ไม่ทราบตัวใช้ถ้อยคำกลาง ไม่เดาจาก mma/mfa ดู JP/TH และตัวเลขที่ [editorial-review.json](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter4/editorial-review.json), [audit](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter4/translation-audit.json), [ภาพ glyph จริง](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter4/font-proof.png) และ [native baseline](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter4/runtime-baseline-check.json) ยังไม่ได้ดู/ฟังวิดีโอใหม่ครบทุกประโยคหรือติดตั้ง/ทดสอบในเกม

ขั้นตอนปัจจุบัน: `assemble_chapter4.py` → `build_chapter1.py --chapter4-working` → `verify_chapter1.py --chapter4-working` → `audit_chapter4.py` → `preview_chapter4.py` → `publish_final_parts.py` ตรวจผลแต่ละขั้น ห้ามรัน prepare ซ้ำ/จัด index ใหม่/เขียนทับ snapshot เก่า หากแก้ฐานเดิมต้องตั้ง revision ใหม่

Final มี **4 ZIP ล่าสุดของแต่ละส่วน**: Chapter1, Chapter2, [ThaiJP_Chapter3_4_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter3_4_P.zip), Common ต้องใช้ร่วมกัน ผู้ใช้ยืนยันชื่อนี้แทน ZIP Chapter3 เดิม เพราะใช้ JUNOE ร่วมกัน ไฟล์เก่าสำรองนอก Final ตาม [release manifest](E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/latest.json) ตรวจเปิดร่วม 12 mod files / 22 assets แล้ว ไม่มี asset ทับกัน Chapter1/Chapter2 คงเดิม รอบนี้อัปเดต Chapter3_4/Common และคงคำแปลเดิม 17,431 รหัสครบ

บทหลังเหมืองที่พักจาก Ch.3 จำนวน 14 รหัสถูกแปลใน Ch.4 แล้ว ข้อมูล Ch.3 ยังอยู่ใน [CHAPTER3-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER3-STATUS.md) เป็นประวัติ ข้อความ “Ch.4 ยังไม่เริ่ม”/ยอดก่อน Ch.4 ในเอกสารเก่าไม่ใช่สถานะปัจจุบัน งานถัดไป: ทดสอบในเกมเมื่อได้รับคำสั่ง; เริ่ม Ch.5 เมื่อผู้ใช้สั่ง; เก็บ 50 บทที่แยกไว้ตามเหตุการณ์จริงในอนาคต

อัปเดตฟอนต์ล่าสุด: แก้แนวไทยให้ตรงกับอังกฤษและตัวเลขที่เกมเติมภายหลังในแจ้งรับของ/ผลต่อสู้ เช่น Ether, Velociwing และ EXP/AP โดยขยับ Thai clusters ให้ตรง native ASCII H เดิม เปลี่ยนเฉพาะค่าแนวตั้งของ font metadata 8 assets ข้อความและภาพฟอนต์คงเดิม แพ็ก Common ใหม่แล้ว อ่านรายละเอียด/ข้อจำกัดที่ [BASELINE-ALIGNMENT-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/BASELINE-ALIGNMENT-STATUS.md) และดู [ภาพก่อน/หลังจาก glyph จริง](E:/FF7RebrithModTH/FF7Rebrith/qa/baseline-alignment/runtime-substitution-proof.png) ภาพนี้จำลองแทนชื่อ/เลขหลัง encode ไม่ใช่ภาพในเกม ยังไม่ได้ติดตั้งหรือทดสอบเล่นจริง

อัปเดตหลังส่งต่อรอบแรก: เพิ่มชื่อศัตรู/ส่วนเป้าหมายอังกฤษแล้ว ดู [ENEMY-NAMES-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/ENEMY-NAMES-STATUS.md) ตรวจด้วย `assemble_enemy_names.py` และ `audit_enemy_names.py` นอกเหนือจากขั้นตอน UI เดิม การพักชื่อศัตรูในประวัติก่อนหน้าไม่ใช้แล้ว

- แปลบทพูด **Ch.1–4** แล้ว ยังไม่ได้แปลบทพูด Ch.5–14 (รวมเฉพาะขอบเขตคัดเลือกตามสถานะของแต่ละบท)
- แปลความสามารถไอเทม/สกิลทั้งเกมและ UI ตามหมวดที่ผู้ใช้ขอแล้ว ไม่ได้หมายความว่าข้อความทุกหมวดของทั้งเกมแปลครบ
- ชุดปัจจุบันมี **20,637 รหัสข้อความ**, 6 text assets + 8 font assets + 8 font-texture assets = **22 assets**
- ไฟล์ส่งมอบอยู่ใน `E:\FF7RebrithModTH\Mod\Final` แยก **ZIP ล่าสุดของแต่ละส่วน**: Chapter1, Chapter2, Chapter3_4 และ Common ต้องใช้ทั้ง 4 ZIP ร่วมกัน
- งานล่าสุดแก้หน้าเปียโน คำอธิบาย COMMAND แจ้งรับของ/ผลต่อสู้/ระบบ เพิ่ม 421 รหัส และเปลี่ยน HUD ปาร์กัวร์เป็น `Terrain Action` คง `COMMAND` อังกฤษ
- ผู้ใช้สั่งเริ่มชื่อศัตรูทั้งหมดแล้ว: ใช้ชื่ออังกฤษทางการ ครบ 312 รหัสศัตรูหลัก + 14 รหัสศัตรูมินิเกม + 72 รหัสส่วนเป้าหมาย รวม 398 รหัส (เพิ่มใหม่ 395) ดู `E:/FF7RebrithModTH/FF7Rebrith/ENEMY-NAMES-STATUS.md`
- แพ็กและตรวจอ่านกลับผ่านแล้ว แต่ยังไม่ได้ติดตั้งชุดแก้ล่าสุดหรือทดสอบเล่นจริงโดยผู้ทำงาน การตรวจไฟล์/ภาพฟอนต์ไม่เท่ากับการทดสอบในเกม
- คำขอให้เขียนเอกสารส่งต่อนี้ไม่ได้สั่งให้เริ่มแปล Ch.3 หรือให้ติดตั้งม็อดเพิ่ม

## 2. พาธหลัก

| ใช้สำหรับ | พาธจริง |
| --- | --- |
| Workspace | `E:\FF7RebrithModTH` |
| โปรเจกต์ Rebirth ที่ต้องแก้ | `E:\FF7RebrithModTH\FF7Rebrith` — สะกด **Rebrith** ตามโฟลเดอร์จริง |
| เกมที่ติดตั้ง | `E:\steam\steamapps\common\FINAL FANTASY VII REBIRTH` |
| ม็อดที่เกมโหลด | `E:\steam\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks\~mods` |
| ZIP ล่าสุดแยกส่วน | `E:\FF7RebrithModTH\Mod\Final` |
| ไฟล์เกมดิบที่ดึงไว้ | `E:\FF7RebrithModTH\FF7Rebrith\source` |
| ข้อความญี่ปุ่นต้นฉบับ | `E:\FF7RebrithModTH\FF7Rebrith\source\End\Content\Text\JP` |
| อังกฤษรหัสตรงกัน ใช้เทียบชื่อ/กลไก | `E:\FF7RebrithModTH\FF7Rebrith\source\End\Content\Text\US` |
| ชุดทำงานรวมล่าสุด | `E:/FF7RebrithModTH/FF7Rebrith/staging/ThaiJP_ThroughChapter4_Working` |
| Python ที่ใช้งานได้บนเครื่องนี้ | `C:\Users\godca\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` |
| ไลบรารี Python เพิ่มเติมของโปรเจกต์ | `E:\FF7RebrithModTH\tools\python-libs` |
| เครื่องมือและตัวอ่านของ workspace | `E:\FF7RebrithModTH\tools` |
| เครื่องมือของโปรเจกต์ | `E:\FF7RebrithModTH\FF7Rebrith\tools` |

อย่าแก้ไฟล์เกมดิบใน `source` หรือไฟล์เกมที่ติดตั้งเพื่อทำคำแปล เขียนผลใน `staging` แล้วแพ็กเท่านั้น การติดตั้งลงเกมต้องมีคำสั่งแยกจากผู้ใช้

## 3. งานที่ทำไปแล้ว

| ส่วน | สถานะ / ขอบเขต |
| --- | --- |
| Chapter 1 | บทพูด 1,157 รายการ ครอบคลุมฉากเปิด/ย้อนอดีต/NPC/บอสที่อยู่ในขอบเขต มีป้ายชื่ออังกฤษ 27 รหัสใน Resident |
| Chapter 2 | บทพูด 2,876 รายการ: Kalm/Grasslands, โปรโตเรลิก, เควสต์ต้นเกม, NPC, Queen's Blood, Chadley/MAI, สำรวจและต่อสู้ที่คัดไว้ |
| Chapter 3 | บทพูด 253 รายการ: ในเหมือง/เติร์ก/บอส/แยกและรวมกลุ่ม/ฉากออกจากเหมือง ตรวจคำลงท้าย 28 รายการ |
| Chapter 4 | เพิ่ม 3,206 รายการ: บทหลัก/Junon NPC/5 เควสต์ต้นเกม/Fort Condor/QB/วิจัย ตรวจคำลงท้าย 181 รายการ แยก 50 เหตุการณ์ภายหลัง |
| ขอบเขต Ch.2 ที่แยกไว้ | มีข้อมูลต้นทาง 2,928 รายการ โดยพักเหตุการณ์ภายหลัง 52 รายการ ไม่ใส่ลงชุด Ch.2 นี้ |
| เมนูชุดแรก | เลือก 583 รหัส เปลี่ยนจากต้นฉบับ 533 รหัส ครอบคลุม title/main/pause/save/load และหน้าตั้งต้นที่เกี่ยวข้อง |
| ไอเทม/สกิลทั้งเกม | คำอธิบายความสามารถ 2,169 รหัส + ชื่ออังกฤษ 2,773 รหัส จากแม่แบบที่แปล/ตรวจ 1,435 ชุด |
| UI เพิ่มเติม | 7,201 รหัส / แม่แบบที่ต้องใช้และตรวจแล้ว 5,046 ชุด: คำบรรยายอุปกรณ์, ค่าสถานะ/ต้านทาน, คู่มือ/บทสอน, ตั้งค่า, photo mode, HUD, เป้าหมาย/สรุปเนื้อเรื่องใน UI, Chapter, พื้นที่/แผนที่/เซฟ, ร้านค้า/คราฟต์/อัปเกรด |
| แก้จากภาพล่าสุด 7 ภาพ | เพิ่ม 421 รหัสใน COMMAND help, pickup/battle/system notifications และเปียโนทั้งหมวด ปุ่มหยุดเล่นเปียโนใช้ข้อความชัดเจน ตัวโน้ต/ชื่อเพลงใช้ชื่อ US |
| ฟอนต์ | Noto Sans Thai น้ำหนัก 300 รักษาอักษรอังกฤษ/ตัวเลข/ไอคอนเดิม จัด Thai clusters ตรง native ASCII H พร้อม aliases เพื่อรองรับชื่อ/เลขที่เกมเติมหลัง encode ตรวจ 8 ขนาดแล้ว |
| การเผยแพร่ | ZIP แยก 4 ส่วน เปิดอ่านทั้งแยกและร่วมกันได้ครบ 22 assets ไม่มี asset ซ้ำทับกัน |

จำนวนหมวดเป็นจำนวนรหัสที่เลือก/เปลี่ยน ไม่ควรบวกเป็นยอดรวมเอง เพราะมีข้อความร่วม ใช้ยอดรวมใน [final-audit.json](E:/FF7RebrithModTH/FF7Rebrith/qa/ui-completion/final-audit.json) เป็นหลัก

### การตรวจเพศ/คำลงท้ายที่มีหลักฐานแล้ว

- Ch.1 ตรวจรายการคำลงท้ายเดิม 71 รายการ เก็บคำลงท้ายที่มีหลักฐานไว้ 20 รายการ และปรับกรณีระบุตัวผู้พูดไม่ได้เป็นถ้อยคำกลาง
- Ch.2 ตรวจรายการที่เกี่ยวกับเพศ/คำเรียก 237 รายการ ผลตรวจไฟล์ไม่พบความขัดแย้งตามหลักฐานที่บันทึกไว้
- ยังไม่ได้ดู/ฟังคลิปครบทุกประโยค ทุก NPC หรือทุกทางเลือก อย่าเขียนส่งต่อว่าเพศถูกตรวจจากวิดีโอครบทั้งหมด
- บทพูดเดิม Ch.1–2 ไม่ได้เปลี่ยนในรอบแก้เปียโน/ข้อความแจ้งเตือนล่าสุด

## 4. ข้อกำหนดการแปลที่ต้องรักษา

1. แปลจาก **JP ในไฟล์เกม** เพื่อเล่นกับเสียงพากย์ญี่ปุ่น ใช้ US รหัสเดียวกันตรวจชื่อทางการ/ความสามารถ ไม่ใช้คำบรรยายอัตโนมัติของ YouTube แทนบท JP
2. ป้ายชื่อตัวละคร/ผู้พูดเป็นอังกฤษ เช่น `Cloud`, `Tifa`, `Sephiroth`
3. ชื่อเฉพาะในบทพูดและ Dialogue/เนื้อเรื่องที่เปิดอ่าน แปลหรือถอดเป็นไทย รวมชื่อคน เมือง สถานที่ องค์กร ไอเทมและสกิล
4. ใน UI/เมนู/ชื่อพื้นที่/หน้าเซฟ คงชื่อเฉพาะทางการเป็นอังกฤษ ชื่อไอเทม/สกิลไม่แปล แต่แปลคำอธิบายความสามารถเป็นไทย
5. ปุ่มยืนยันระบบ/ตัวเลือกชื่อบุคคลที่เป็น UI ใช้กฎ UI อย่าตัดสินจาก ACTOR ว่างอย่างเดียว เพราะบทพูด NPC บางบรรทัดก็ไม่มี ACTOR
6. ชื่อ Chapter เป็นอังกฤษทางการ ช่วงเวลาเป็นไทย เช่น `5 ปีก่อน`, `ปัจจุบัน`, `4 ปีก่อน`
7. ชื่อศัตรูใน UI/แถบ HP/เป้าหมาย/ข้อมูลศัตรู/แจ้งเตือนหลังสู้ ใช้อังกฤษทางการจาก US รหัสตรงกันแล้ว รักษา `<object=0>` ของข้อความแจ้งเตือนเดิม ชื่อที่กล่าวในประโยค Dialogue เดิมยังเป็นไทย ข้อกำหนดพักชื่อศัตรูถูกแทนที่ด้วยคำสั่งให้เริ่มล่าสุด
8. HUD มุมซ้ายล่างใช้ `Terrain Action` และ `COMMAND` อังกฤษ แต่คำอธิบายการใช้ไอเทม/เวทใต้หน้าต่างคำสั่งเป็นไทย
9. ตัวเลขที่เป็นจำนวน/อายุ/ระยะเวลา/หมายเลขใช้เลขอารบิก เช่น `เซคเตอร์7`, `16`, `5 ปีก่อน` ไม่เขียนเป็นคำจำนวน รักษาสำนวน/คำนามอย่าง `คนหนึ่ง`, `ศูนย์วิจัย`, `สามเหลี่ยม` และชื่อทางการเช่น `Hell Rider II`
10. `ครับ/ค่ะ/คะ` ใส่เฉพาะจำเป็น ตามผู้พูด/บริบทที่มีหลักฐาน ไม่เติมทุกบรรทัด ไม่เดาเพศจากรหัส `mma/mfa` หรือช็อตปฏิกิริยาตัวละคร ถ้าไม่ชัดใช้ถ้อยคำกลางและบันทึกไว้ รวมถึงตรวจสรรพนาม `ผม` ด้วย
   - ผู้พูดชาย: ใช้ **ครับ** เมื่อบริบทต้องสุภาพ เช่น “เข้าใจแล้วครับ”, “พร้อมไหมครับ?”
   - ผู้พูดหญิง: ใช้ **ค่ะ** ในประโยคบอกเล่า/ตอบรับ เช่น “เข้าใจแล้วค่ะ”; ใช้ **คะ** ในคำถามหรือคำเรียก เช่น “พร้อมไหมคะ?”, “คุณคะ” และใช้ **นะคะ** ไม่ใช่ “นะค่ะ”
   - อ้างเพศของ **ผู้พูด** ไม่ใช่เพศผู้ฟัง พร้อมรักษาอายุ บุคลิก ความสนิท และระดับภาษาของตัวละคร ไม่บังคับให้บทที่ห้วน/กันเองต้องมีคำลงท้าย
   - ถ้าระบุตัวผู้พูดหรือเพศไม่ได้ ให้ละคำลงท้าย/ปรับเป็นถ้อยคำกลาง อย่าใส่ “ครับ/ค่ะ” แบบเลือกเอาเองหรือเขียนเครื่องหมายทับลงในบทพูดจริง บันทึกรหัสบรรทัดและหลักฐานที่ยังขาดไว้
11. ศัพท์อ้างอิง PlearnGaming: `Wutai` ใน Dialogue = **อู่ไถ**, UI = `Wutai`; `Materia` ทั่วไป = **แมทีเรีย**; `Stagger` = **สแตกเกอร์** ไม่ใช้เสียสมดุลแทนสถานะนี้โดยอัตโนมัติ
12. ฟอนต์ต้องใกล้ต้นฉบับ รักษาขนาด/สัดส่วนไทย ไม่ย่อเพื่อยัด atlas รักษา glyph/พิกเซลเดิมและไอคอน ตรวจแนวตัวเลข/อังกฤษผสมไทยหลังสร้าง
13. รักษาแท็กปุ่ม/ตัวแปรจาก JP เช่น `<button=...>`, `<object=0>`, `<count=0>`, `<count>` และ color tags อย่าคัดลอกแท็กจาก US มาทับ เพราะ locale มีสัญญาตัวแปรต่างกันได้

## 5. YouTube สำหรับเทียบบท ฉาก และตัวผู้พูด

### วิดีโอที่ผู้ใช้ให้

| แหล่ง | ลิงก์ / ใช้อย่างไร |
| --- | --- |
| วิดีโอยาวอ้างอิงฉาก/ตัวผู้พูด | [วิดีโอ i4gD0mmj5vc](https://www.youtube.com/watch?v=i4gD0mmj5vc) — ใช้เวลาจากตารางด้านล่าง |
| เพลย์ลิสต์เสียงพากย์ญี่ปุ่น | [Final Fantasy VII Rebirth — Japanese Voice / Owl-Quest](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU) — ใช้เทียบบท/น้ำเสียง/ฉากญี่ปุ่น ผู้ใช้ให้ลิงก์นี้โดยตรง |
| ตอนแรกของชุดญี่ปุ่นที่เคยใช้ดูบางฉาก | [Episode 1 — Japanese Voice](https://www.youtube.com/watch?v=bxrLsiU-QKk) |

เวลาของวิดีโอยาว **ใช้แทนเวลาในเพลย์ลิสต์ญี่ปุ่นไม่ได้** เพราะตัดต่อคนละแบบ ตารางนี้คัดจาก timestamps ที่ผู้ใช้ส่ง ยังไม่ได้ตรวจวิดีโอใหม่ทุกจุด ผู้ใช้ระบุว่าเวลาที่เกิน 12 ชั่วโมงให้ดู timestamps ใน description แทน comments

| Chapter | ชื่ออังกฤษทางการ | เวลาเริ่มในวิดีโอ i4gD0mmj5vc |
| --- | --- | --- |
| Prologue | The Hero Returns (ตามรายการเวลาของผู้ใช้) | 00:00:00 |
| 1 | Fall of a Hero | 00:14:13 |
| 2 | A New Journey Begins | 02:06:42 |
| 3 | Deeper into Darkness | 11:07:48 |
| 4 | Dawn of a New Era | 12:23:04 |
| 5 | Blood in the Water | 21:30:39 |
| 6 | Fool's Paradise | 22:49:08 |
| 7 | Those Left Behind | 24:54:25 |
| 8 | All That Glitters | 28:28:23 |
| 9 | The Planet Stirs | 39:29:13 |
| 10 | Watcher of the Vale | 47:19:48 |
| 11 | The Long Shadow of Shinra | 57:12:38 |
| 12 | A Golden Key | 64:38:05 |
| 13 | Where Angels Fear to Tread | 81:18:41 |
| 14 | End of the World | 85:57:35 |

จุดอ้างอิง Ch.1–2 ที่ผู้ใช้ให้: Nibelheim 00:19:15, Nibel Region 00:39:57, Shinra Manor 01:37:06, Sephiroth discovers the truth 01:40:43, Queen's Blood tutorial 02:07:47, Chocobo Bill 03:15:15, Chocobo Ranch 03:30:18, sidequests Grasslands 04:23:25 และ Midgardsormr 10:49:33

### หลักฐานฉาก/เพศที่เก็บไว้

- [reference/japanese-video-reference.json](E:/FF7RebrithModTH/FF7Rebrith/reference/japanese-video-reference.json): บันทึกวิดีโอญี่ปุ่นและข้อจำกัด ระบุ `audio_reviewed: false`
- [reference/gender-particle-review.json](E:/FF7RebrithModTH/FF7Rebrith/reference/gender-particle-review.json): หลักฐานรายประโยค Ch.1 อ้างวิดีโอยาว พร้อมเหตุผลเก็บคำลงท้าย/ปรับเป็นกลาง
- [reference/gender-particle-baseline.json](E:/FF7RebrithModTH/FF7Rebrith/reference/gender-particle-baseline.json): ค่าก่อนตรวจคำลงท้าย
- [qa/chapter1/gender-particle-audit.json](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter1/gender-particle-audit.json): ผลตรวจ Ch.1
- [qa/chapter2/gender-review.json](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter2/gender-review.json): หลักฐาน Ch.2 จากชื่อ ACTOR/ความสัมพันธ์ในบท/ข้อมูลทางการ
- [reference/actor-english-evidence.json](E:/FF7RebrithModTH/FF7Rebrith/reference/actor-english-evidence.json): หลักฐานจับคู่ชื่อผู้พูดอังกฤษ

ฉากในตอนญี่ปุ่นที่มีบันทึก: 637 วินาที คนขับรถ, 842 วินาที Mayor Zander, 1227–1229 วินาที Tifa ทักทายเป็นไกด์ ส่วน reporter/ช่างภาพ/เจ้าของโรงแรมบางฉากยังระบุตัวไม่ได้จากหลักฐานเดิม อย่าใช้ฉากเหล่านั้นยืนยันเพศเพิ่มโดยไม่มีหลักฐานใหม่

## 6. งานที่ยังต้องทำ

### ลำดับแรก: ทดสอบและเก็บจุดตกหล่น

- ทดสอบชุดล่าสุดในเกมเมื่อผู้ใช้สั่งติดตั้ง หรือให้ผู้ใช้ทดสอบเอง ตั้ง `Text & Subtitles = Japanese`, `Voice-over = Japanese` และเริ่มเกมใหม่หลังเปลี่ยนภาษา
- ตรวจภาพที่แก้ล่าสุด: คำอธิบาย ITEM/MAGIC, รับของจากพื้น/หีบ/หลายชิ้น/แมทีเรีย, EXP/AP/กิลหลังต่อสู้, หน้าเล่นเปียโน/เลือกเพลง/โน้ต/ชาร์ปแฟลต/เปลี่ยนคีย์และอ็อกเทฟ/หยุดเล่น/ผลคะแนน
- ตรวจการตัดบรรทัด/ล้นกล่อง สระวรรณยุกต์ แนวตัวเลขและชื่ออังกฤษ โดยเฉพาะค่าที่เกมแทนผ่านแท็กแบบไดนามิก ภาพ proof ไม่ยืนยันพฤติกรรม runtime นี้
- ถ้าพบ JP ตกหล่นเพิ่ม ให้หารหัสจริงและตรวจหมวดที่เกี่ยวข้องทั้งหมด อย่าแก้เพียง string ที่บังเอิญตรงภาพ แล้วเพิ่ม QA/บันทึกขอบเขต
- ทดสอบชื่อศัตรูอังกฤษทั้งศัตรูทั่วไป บอส ศัตรูหายาก อสูร VR มินิเกม และส่วนเป้าหมาย รวมชื่อในแจ้งเตือนหลังสู้ เช่น “กำจัด Velociwing แล้ว” หากยังพบ JP ให้ตรวจรหัส runtime จริงกับ scope ชุดชื่อ

### งานเนื้อหาที่ยังไม่เริ่ม/ไม่ถือว่าเสร็จ

- บทพูด Ch.4–14: รอผู้ใช้ระบุบท/ขอบเขตที่จะทำต่อ ต้องแยกฉากจริง ไม่ใช้ตัวเลขใน ID ตัด chapter อย่างเดียว โดยนำ chapter3-deferred.json มาพิจารณาสำหรับบท 4 ด้วย
- เหตุการณ์ภายหลัง 52 รายการที่พักจาก Ch.2: [chapter2-deferred.json](E:/FF7RebrithModTH/FF7Rebrith/reference/chapter2-deferred.json) ต้องพิจารณาใส่ในบท/เหตุการณ์ที่ถูกต้องภายหลัง
- ชื่อศัตรูอังกฤษทำแล้วตาม scope 398 รหัส งานที่ค้างคือการทดสอบแสดงผลในเกมจริง ไม่ต้องเริ่มแปลชื่อชุดนี้ซ้ำ
- รายละเอียดสารานุกรมศัตรู หมวด World Report/ภารกิจสนามประลองบางหมวด และ flavor ของของสะสม/ไอเทมเควสต์ที่อยู่นอก scope ปัจจุบัน: ไม่ได้ยืนยันว่าครบ ให้ตรวจ scope ก่อนขยาย
- ข้อความ Crisis Core Reunion ยังไม่ได้ถอดสำเร็จครบ จึงยังใช้เป็นฐานคำแปลที่ยืนยันไม่ได้ งาน Remake อ่านและตรวจคำศัพท์ได้แล้ว

### สิ่งที่ต้องปรับเมื่อเพิ่ม chapter ใหม่

- มี workflow Ch.3 แล้วตาม CHAPTER3-STATUS.md บทใหม่ต้องทำ source/scope/คำแปล/เพศเพิ่ม และรวมโดยรักษา Ch.1–3 + inventory + UI/enemy names ล่าสุด
- อย่าแก้เฉพาะ `working-ui-completion-th.json` แล้วรัน assembler เดิม เพราะไฟล์รวมถูกสร้างใหม่ได้และงานที่ไม่ได้ผูกกับต้นทางจะหาย
- `publish_final_parts.py` อ่านกลุ่มเพิ่มจาก qa/active-working-set.json ปัจจุบัน 4 ZIP/22 assets บทถัดไปต้องระบุเจ้าของ asset ให้ไม่ทับกลุ่มเดิมและตรวจ union ทุกแพ็ก อย่าปล่อยให้ asset บทใหม่ไหลเข้า Common โดยไม่ได้ตั้งใจ
- ถ้ามี Thai cluster ใหม่ ตาราง alias อาจเปลี่ยน ต้องสร้างข้อความและฟอนต์จากตารางเดียวกัน แล้วอัปเดตทุก ZIP ที่ได้รับผล ห้ามผสม assets คนละรุ่นของ glyph map

## 7. ไฟล์ต้นทางและคำแปลที่ต้องใช้

ไฟล์ JSON แบบ `*-th.json`/`working-*.json` เป็นผลรวมที่สร้างจากแหล่งย่อย แก้ใน batch/รายการ override ที่ถูกต้อง แล้ว assemble ใหม่ อย่าจัดลำดับ index เดิมใหม่

| ส่วน | ไฟล์/โฟลเดอร์จริง |
| --- | --- |
| Corpus JP รวม | [reference/rebirth-jp-corpus.json](E:/FF7RebrithModTH/FF7Rebrith/reference/rebirth-jp-corpus.json) |
| Chapter 1 คำแปลต้นทาง | [translations/chapter1/](E:/FF7RebrithModTH/FF7Rebrith/translations/chapter1) — `batch-*.json` |
| Ch.1 source / ผลรวม | [chapter1-source.json](E:/FF7RebrithModTH/FF7Rebrith/reference/chapter1-source.json), [chapter1-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/chapter1-th.json) |
| Chapter 2 คำแปลต้นทาง | [translations/chapter2/](E:/FF7RebrithModTH/FF7Rebrith/translations/chapter2) — batch ตาม index |
| Ch.2 source / shared / scope | [chapter2-source.json](E:/FF7RebrithModTH/FF7Rebrith/reference/chapter2-source.json), [chapter2-shared-source.json](E:/FF7RebrithModTH/FF7Rebrith/reference/chapter2-shared-source.json), [chapter2-scope.json](E:/FF7RebrithModTH/FF7Rebrith/reference/chapter2-scope.json) |
| Ch.2 ผลรวม / ฐานรวมถึง Ch.2 | [chapter2-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/chapter2-th.json), [working-through-chapter2-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter2-th.json) |
| เมนูชุดแรก | [translations/menu/](E:/FF7RebrithModTH/FF7Rebrith/translations/menu) — `menu-*.json`, [menu-source.json](E:/FF7RebrithModTH/FF7Rebrith/reference/menu-source.json), [menu-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/menu-th.json) |
| ไอเทม/สกิลต้นทาง | [translations/inventory/](E:/FF7RebrithModTH/FF7Rebrith/translations/inventory) — `batch-*.json` |
| Inventory source / template / scope | [inventory-source.json](E:/FF7RebrithModTH/FF7Rebrith/reference/inventory-source.json), [inventory-templates.json](E:/FF7RebrithModTH/FF7Rebrith/reference/inventory-templates.json), [inventory-scope.json](E:/FF7RebrithModTH/FF7Rebrith/reference/inventory-scope.json) |
| Inventory ผลรวม | [inventory-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/inventory-th.json), [working-inventory-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/working-inventory-th.json) — เป็นฐานของ UI assembler |
| ชื่อศัตรูอังกฤษต้นทาง / scope / ผลรวม | [enemy-name-source.json](E:/FF7RebrithModTH/FF7Rebrith/reference/enemy-name-source.json), [enemy-name-scope.json](E:/FF7RebrithModTH/FF7Rebrith/reference/enemy-name-scope.json), [enemy-names-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/enemy-names-th.json) |
| UI ต้นทางล่าสุด | [translations/ui-completion/](E:/FF7RebrithModTH/FF7Rebrith/translations/ui-completion) — `batch-*.json`; `batch-44.json` เป็นงานเปียโน/แจ้งเตือนล่าสุด |
| UI source / template / scope | [ui-completion-source.json](E:/FF7RebrithModTH/FF7Rebrith/reference/ui-completion-source.json), [ui-completion-templates.json](E:/FF7RebrithModTH/FF7Rebrith/reference/ui-completion-templates.json), [ui-completion-scope.json](E:/FF7RebrithModTH/FF7Rebrith/reference/ui-completion-scope.json) |
| UI overrides ที่ต้องรักษา | อยู่ใน `reference/ui-completion-scope.json`: `english_hud_actions`, `reviewed_text_overrides`, `automatic` และ temporal exception |
| UI ผลรวมเฉพาะส่วน / ผลรวมทั้งหมดล่าสุด | [ui-completion-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/ui-completion-th.json), **[working-ui-completion-th.json](E:/FF7RebrithModTH/FF7Rebrith/translations/working-ui-completion-th.json)** |
| ตาราง glyph ล่าสุด | [reference/ui-completion-cluster-map.json](E:/FF7RebrithModTH/FF7Rebrith/reference/ui-completion-cluster-map.json) |
| บันทึกการแก้กฎชื่อเฉพาะ Ch.1–2 | [qa/current-conditions/](E:/FF7RebrithModTH/FF7Rebrith/qa/current-conditions) |

### ฐาน PlearnGaming ที่ผู้ใช้ให้

- Remake: [โฟลเดอร์ FF7Remake](E:/FF7RebrithModTH/FF7Remake) มี ZIP `from JP except UI-1256-2-3-0-1706280023.zip`
- Crisis Core: [โฟลเดอร์ FF7Crisis Core Reunion](<E:/FF7RebrithModTH/FF7Crisis Core Reunion>) มี ZIP `from JP except UI-39-1-0-1-1724599852.zip`
- ศัพท์ที่ตรวจแล้ว: [reference/plearngaming/glossary.json](E:/FF7RebrithModTH/FF7Rebrith/reference/plearngaming/glossary.json)
- หลักฐาน Stagger: [qa/inventory/reference-terminology.json](E:/FF7RebrithModTH/FF7Rebrith/qa/inventory/reference-terminology.json)
- เก็บ ZIP/PAK อ้างอิงเหล่านี้ไว้เดิม ไม่เอาไปใส่ `Mod/Final` และไม่อ้างว่าใช้ Crisis Core แปลครบแล้ว

## 8. การแบ่ง ZIP และไฟล์เกมที่เกี่ยวข้อง

| ZIP ล่าสุด | Assets ภายในแพ็ก | ขนาด ZIP ณ ส่งต่อ |
| --- | --- | ---: |
| [ThaiJP_Chapter1_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter1_P.zip) | `End/Content/Text/JP/4000-MIDGR_TxtRes.uasset`, `8700-NIBLE_TxtRes.uasset` | 93,926 bytes |
| [ThaiJP_Chapter2_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter2_P.zip) | `End/Content/Text/JP/8100-GRASE_TxtRes.uasset`, `8800-FOREE_TxtRes.uasset` | 119,640 bytes |
| [ThaiJP_Chapter3_4_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter3_4_P.zip) | `End/Content/Text/JP/8200-JUNOE_TxtRes.uasset` | 113,136 bytes |
| [ThaiJP_Common_P.zip](E:/FF7RebrithModTH/Mod/Final/ThaiJP_Common_P.zip) | `End/Content/Text/JP/Resident_TxtRes.uasset` + ฟอนต์/ภาพฟอนต์ 16 assets ใต้ `End/Content/Menu/Billboard/Common` | 19,669,395 bytes |

**ใช้ทั้ง 4 ZIP ร่วมกัน** ชื่อ ZIP เป็นการแบ่งชุดไฟล์ ไม่ใช่ม็อด chapter ที่ลงแยกเดี่ยวได้ครบ: GRASE มีบท Ch.1–3 และ Resident รวมบทพูดร่วม/ป้ายชื่อ/UI/ไอเทมไว้ในไฟล์เดียว

- แต่ละ ZIP แตกออกมาเป็น `.pak`, `.utoc`, `.ucas` ชื่อของส่วนนั้น รวมติดตั้งครบชุด = 12 mod files
- ใน `Final` มีเฉพาะ ZIP ล่าสุดของแต่ละส่วน ไม่ใส่ README/JSON/MD/TXT หรือไฟล์รุ่นเก่า
- ลิขสิทธิ์ฟอนต์ Noto อยู่ใน archive comment ของ ZIP เพื่อรักษาเงื่อนไขไม่เพิ่ม TXT ในไฟล์ที่แตกไปใช้
- เมื่อแก้ไขเสร็จ แพ็กและเขียนทับ ZIP ชื่อเดิมโดยอัตโนมัติตามคำสั่งผู้ใช้ ไม่ต้องรอคำสั่งให้แพ็กใหม่ แต่ **ยังไม่ใช่การอนุญาตติดตั้งในเกม**
- `publish_final_parts.py` เก็บ ZIP ส่วนที่ไม่เปลี่ยนไว้เดิม ตรวจแฮช/CRC ก่อนใช้ซ้ำ ส่วนที่เปลี่ยนสำรองรุ่นเก่านอก Final แล้วแทนที่ หลังจากนั้น mount ทุกแพ็กเพื่อตรวจรวม
- รอบ Chapter 3 เพิ่ม JUNOE และแก้ GRASE พร้อม font/texture ทั้ง 16 assets; Resident/MIDGR/NIBLE/FOREE คงเดิม Chapter1 ZIP จึงไม่เปลี่ยน
- ค่าแฮชและ run ล่าสุดดู [qa/final-parts/latest.json](E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/latest.json) อย่าใช้ `dist` หรือ `qa/ui-completion/final-release.json` รุ่น ZIP รวมเก่าทดแทนชุดนี้

## 9. ขั้นตอนทำงานต่ออย่างถูกสาย

### 9.1 ก่อนแก้แต่ละรอบ

1. อ่านคำสั่งผู้ใช้ล่าสุด/AGENTS แล้วดู `qa/final-parts/latest.json`, `qa/ui-completion/final-audit.json` และ scope ของส่วนที่จะแก้
2. สำรองต้นทาง/ผลรวม/manifest ที่เกี่ยวข้อง และบันทึก hash ของ dist กับม็อดที่ติดตั้งอยู่ในตอนเริ่มรอบ **ใหม่**
3. ใช้ [active-revision.json](E:/FF7RebrithModTH/FF7Rebrith/qa/ui-completion/active-revision.json) ชี้ snapshot ของรอบนั้น การเปลี่ยนม็อดโดยผู้ใช้ระหว่างรอบทำให้ baseline เก่าไม่ตรงได้ ต้องบันทึก baseline ใหม่พร้อมรักษาประวัติ ไม่คัดลอก/ลบ snapshot เก่าเพื่อกลบข้อผิดพลาด
4. snapshot รอบภาพเปียโนอยู่ใต้ `E:\FF7RebrithModTH\FF7Rebrith\qa\ui-completion\revisions\6f16d888d6774b1a982906937d082103` รวมไฟล์ต้นทางก่อนแก้และ protected-files-before
5. หารหัสจาก corpus/JP/US เปรียบเทียบรหัสเดียวกัน ตรวจว่าเป็น Dialogue หรือ UI แล้วจึงแก้ batch/override

### 9.2 โครงสร้างและ index

- `reference/ui-completion-source.json` เก็บ `id`, `asset`, `category`, `jp`, `en`, `mode`, `template`, `numbers` ตามรูปแบบของแต่ละแถว
- `ui-completion-templates.json` เป็น index คงที่ของข้อความที่ normalize แล้ว `{n0}`, `{n1}` เป็นช่องเลขที่ assembler ต้องเติมคืน
- คำแปล batch เป็น mapping `"index": "ข้อความไทย"` ห้ามซ้ำ index ระหว่าง batch
- ถ้าขยายขอบเขต ให้ **append** แถว/แม่แบบใหม่โดยไม่จัดเรียง index เดิม ดูตัวอย่าง `extend_ui_piano_notifications.py`
- `create_ui_completion_scope.py` และ extension เดิมบางตัวเป็นงานสร้างครั้งเดียว ไม่รันซ้ำเพื่อสร้าง index ชุดเดิมทับคำแปล

### 9.3 สร้าง/ตรวจฐาน UI ก่อน Chapter 3 (ประวัติ — ชุดล่าสุดใช้ขั้นตอนในข้อ 1)

ใช้ PowerShell คำสั่งต่อไปนี้สำหรับงานแก้ UI ที่ฐาน Ch.1–2/inventory ไม่เปลี่ยน:

```powershell
Set-Location -LiteralPath 'E:\FF7RebrithModTH\FF7Rebrith'
$taskPython = 'C:\Users\godca\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

& $taskPython 'E:\FF7RebrithModTH\FF7Rebrith\tools\assemble_enemy_names.py'
& $taskPython 'E:\FF7RebrithModTH\FF7Rebrith\tools\assemble_ui_completion.py'
& $taskPython 'E:\FF7RebrithModTH\FF7Rebrith\tools\build_chapter1.py' --ui-completion-working
& $taskPython 'E:\FF7RebrithModTH\FF7Rebrith\tools\verify_chapter1.py' --ui-completion-working
& $taskPython 'E:\FF7RebrithModTH\FF7Rebrith\tools\audit_ui_completion.py'
& $taskPython 'E:\FF7RebrithModTH\FF7Rebrith\tools\audit_enemy_names.py'
& $taskPython 'E:\FF7RebrithModTH\FF7Rebrith\tools\audit_dynamic_baselines.py'
& $taskPython 'E:\FF7RebrithModTH\FF7Rebrith\tools\preview_ui_completion.py'
```

ตรวจ exit code/ผลทุกขั้น หยุดแก้เมื่อมี assertion หรืออ่านกลับไม่ตรง ไม่รัน publish ข้ามข้อผิดพลาด ถ้าไม่มี cluster ใหม่ ใช้ `build_chapter1.py --ui-completion-working --text-only` ได้หลังมีฟอนต์ครบแล้ว โปรแกรมจะยืนยันว่า cluster map ตรงเดิมทุกตัวก่อนใช้ฟอนต์เดิม

สำหรับ regression รอบภาพเปียโน ใช้ `tools/audit_ui_piano_notifications.py` เพิ่ม มันตรวจการแก้ 421 รหัสกับ snapshot ของรอบนั้น ปัจจุบันอนุญาต Resident กับฟอนต์ 8 assets ตามงานชื่อศัตรู/แก้แนวที่ผู้ใช้ขอ ส่วน audit_dynamic_baselines ตรวจอย่างเข้มงวดว่ารอบแนวเปลี่ยนเฉพาะ y origin ไม่เปลี่ยนข้อความหรือภาพ ถ้าเพิ่ม chapter/ขอบเขตใหม่ เงื่อนไขเทียบ snapshot ต้องปรับเป็น regression ที่เหมาะกับรอบใหม่พร้อมเก็บประวัติ ไม่ลบการตรวจข้อความจาก 7 ภาพทิ้งเพียงเพื่อให้ผ่าน

แนวฟอนต์ถาวรอยู่ใน [native-baseline-policy.json](E:/FF7RebrithModTH/FF7Rebrith/reference/native-baseline-policy.json) ตัว build UI เรียก [align_dynamic_baselines.py](E:/FF7RebrithModTH/FF7Rebrith/tools/align_dynamic_baselines.py) อัตโนมัติทั้ง build เต็มและ text-only อย่ารัน main ของตัวปรับแนวซ้ำเพราะมี snapshot ครั้งเดียวสำหรับรอบนี้ ตรวจ origin/การแทน ASCII ภายหลังด้วย [audit_dynamic_baselines.py](E:/FF7RebrithModTH/FF7Rebrith/tools/audit_dynamic_baselines.py), รายงาน [audit.json](E:/FF7RebrithModTH/FF7Rebrith/qa/baseline-alignment/audit.json) และ [alignment.json](E:/FF7RebrithModTH/FF7Rebrith/qa/baseline-alignment/alignment.json) ข้อจำกัดที่ยังต้องทดสอบคือการจัดวาง/ขอบกล่องในเกมจริง

### 9.4 ถ้าแก้ต้นทางบทพูด/เมนู/ไอเทม

อัปเดตผลรวมตามชั้นที่ได้รับผล โดยอ่าน script ก่อนรัน:

```text
translations/chapter1/batch-*.json  -> assemble_chapter1.py -> chapter1-th.json
translations/menu/menu-*.json     -> assemble_menu.py     -> working-th.json
translations/chapter2/*.json      -> assemble_chapter2.py -> working-through-chapter2-th.json
translations/inventory/batch-*.json -> assemble_inventory.py -> working-inventory-th.json
translations/ui-completion/batch-*.json + UI scope/overrides
translations/enemy-names-th.json  -> (รวมชื่ออังกฤษใน UI assembler ด้วย)
                                  -> assemble_ui_completion.py -> working-ui-completion-th.json
                                  -> build / verify / audit / publish
```

ทุก script ในภาพรวมนี้อยู่ที่ `E:\FF7RebrithModTH\FF7Rebrith\tools` หากเปลี่ยนชั้นต้น ต้องรวมชั้นถัดมาจนถึงไฟล์รวมล่าสุดเสมอ และตรวจว่าไม่ถอยการแก้ชื่อเฉพาะ/ตัวเลข/เพศที่เคยทำไว้ใน `qa/current-conditions` อย่ารัน assembler ทุกตัวโดยไม่จำเป็นสำหรับการแก้ UI เพียงรหัสเดียว

เครื่องมือตรวจบทเดิมเพิ่มเติม: [audit_gender_particles.py](E:/FF7RebrithModTH/FF7Rebrith/tools/audit_gender_particles.py), [audit_chapter2.py](E:/FF7RebrithModTH/FF7Rebrith/tools/audit_chapter2.py), [audit_current_conditions.py](E:/FF7RebrithModTH/FF7Rebrith/tools/audit_current_conditions.py), [audit_inventory.py](E:/FF7RebrithModTH/FF7Rebrith/tools/audit_inventory.py) เครื่องมือบางตัวมีขอบเขต/สถานะติดตั้งเฉพาะรุ่นเก่า ต้องอ่านเงื่อนไขก่อนนำมาตัดสินชุดล่าสุด

### 9.5 แพ็ก ZIP หลังแก้เสร็จ

```powershell
& $taskPython 'E:\FF7RebrithModTH\FF7Rebrith\tools\publish_final_parts.py'
```

`publish_final.py` เป็นทางเข้าเดิมที่ส่งต่อไป script เดียวกัน มันตรวจ staging กับ `working-assets.json`, แพ็กด้วย UnrealReZen/Oodle, แก้ Oodle flag ที่จำเป็นสำหรับ Rebirth, อ่าน assets กลับเทียบ byte, ตรวจ ZIP และเรียก [verify_final_parts.py](E:/FF7RebrithModTH/FF7Rebrith/tools/verify_final_parts.py) เพื่อ mount ทุกส่วนร่วมกัน ห้ามข้ามการอ่านกลับหรือเอา assets ซ้ำไปใส่หลายแพ็ก

ถ้าไม่มีไฟล์เปลี่ยน ไม่ต้อง build/pack ซ้ำ การเขียนเอกสารส่งต่อนี้ไม่เปลี่ยนคำแปลหรือ ZIP

## 10. เครื่องมือ/ไลบรารีที่ต้องเก็บไว้

| องค์ประกอบ | พาธ |
| --- | --- |
| ตัวอ่าน/เครื่องมือ Rebirth และ vendored UE4Parse | [tools/cutscene-tool/1.0/](E:/FF7RebrithModTH/FF7Rebrith/tools/cutscene-tool/1.0) — เก็บทั้งโฟลเดอร์รวม vendor/licenses และไฟล์ runtime ที่ใช้อยู่ |
| ตัวอ่าน TxtRes | [tools/cutscene-tool/1.0/txtres.py](E:/FF7RebrithModTH/FF7Rebrith/tools/cutscene-tool/1.0/txtres.py) |
| ตัวแพ็ก IoStore | `E:\FF7RebrithModTH\FF7Rebrith\tools\UnrealReZen\UnrealReZen.exe` |
| แปลงภาพฟอนต์ BC5 | `E:\FF7RebrithModTH\FF7Rebrith\tools\texconv.exe` |
| ฟอนต์ต้นทางปัจจุบัน | [NotoSansThai-Variable.ttf](E:/FF7RebrithModTH/FF7Rebrith/tools/fonts/NotoSansThai-Variable.ttf), [NotoSansThai-Light.ttf](E:/FF7RebrithModTH/FF7Rebrith/tools/fonts/NotoSansThai-Light.ttf) |
| ลิขสิทธิ์ฟอนต์ | [NotoSansThai-OFL.txt](E:/FF7RebrithModTH/FF7Rebrith/tools/fonts/NotoSansThai-OFL.txt) |
| ตัวสร้างฟอนต์/texture | [build_prototype.py](E:/FF7RebrithModTH/FF7Rebrith/tools/build_prototype.py) — ชื่อเก่า แต่ยังเป็นโมดูลที่ build ล่าสุดใช้ |
| ฟังก์ชันอ่าน header/สตริงร่วม | [tools/inspect_reference_mods.py](E:/FF7RebrithModTH/tools/inspect_reference_mods.py) |

การสร้างฟอนต์ใช้ fontTools, FreeType, HarfBuzz, Pillow และ rectpack จาก runtime/ไลบรารีที่ตั้งไว้ ใช้ Python ตามพาธที่ระบุ ไม่สมมติว่า `python` บน PATH คือ environment เดียวกัน ถ้าย้ายเครื่องให้เตรียม dependency และแก้พาธจริงก่อน

`extract_game.py` ปัจจุบันชี้โฟลเดอร์ Paks ของเกมและเขียนผลลง `source` โดยตรง ถ้าต้องดึงไฟล์ใหม่ อย่ารันเพื่อเขียนทับ source ที่ตรวจแล้วทันที ต้องแยกม็อดใน `~mods` ออกจาก input provider และเขียนลงโฟลเดอร์ใหม่เพื่อตรวจสอบก่อน ดูแนวทางอ่านเฉพาะ base PAKs ของ `pack_prototype.py` ซึ่งใช้ temporary hard links โดยไม่ย้ายไฟล์เกม

## 11. QA และข้อมูลสถานะที่ต้องเปิดดู

| เรื่อง | ไฟล์หลัก |
| --- | --- |
| ความครบ UI/ชื่อ/เวลา/ขอบเขต | [qa/ui-completion/final-audit.json](E:/FF7RebrithModTH/FF7Rebrith/qa/ui-completion/final-audit.json) |
| ตรวจข้อความ/metadata/ฟอนต์ทั้งชุด | [qa/ui-completion/verification.json](E:/FF7RebrithModTH/FF7Rebrith/qa/ui-completion/verification.json) |
| แฮช 21 working assets | [qa/ui-completion/working-assets.json](E:/FF7RebrithModTH/FF7Rebrith/qa/ui-completion/working-assets.json) |
| แก้จากภาพล่าสุด / หลักฐานขอบเขต | [piano-notification-review.json](E:/FF7RebrithModTH/FF7Rebrith/qa/ui-completion/piano-notification-review.json), [piano-notification-scope.json](E:/FF7RebrithModTH/FF7Rebrith/qa/ui-completion/piano-notification-scope.json) |
| ภาพ glyph จริงจาก staging | [font-proof.png](E:/FF7RebrithModTH/FF7Rebrith/qa/ui-completion/font-proof.png), [piano-notification-proof.png](E:/FF7RebrithModTH/FF7Rebrith/qa/ui-completion/piano-notification-proof.png) — ไม่ใช่ screenshot ในเกม |
| ZIP ล่าสุดและแฮช/เนื้อหาทุกส่วน | [qa/final-parts/latest.json](E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/latest.json) |
| ตรวจ mount ทั้ง 3 ส่วนพร้อมกัน | [qa/final-parts/combined-mount-verification.json](E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/combined-mount-verification.json) |
| สำรองแพ็กที่ถูกแทน/pack logs/readback | [qa/final-parts/runs/](E:/FF7RebrithModTH/FF7Rebrith/qa/final-parts/runs) |
| ความครบ Ch.2/เพศ/รหัสที่พัก | [qa/chapter2/translation-audit.json](E:/FF7RebrithModTH/FF7Rebrith/qa/chapter2/translation-audit.json) |
| สถานะเอกสารประกอบ | [FINAL-PARTS.md](E:/FF7RebrithModTH/FF7Rebrith/FINAL-PARTS.md), [UI-COMPLETION-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/UI-COMPLETION-STATUS.md), [TRANSLATION_GUIDE.md](E:/FF7RebrithModTH/FF7Rebrith/TRANSLATION_GUIDE.md) |

## 12. สถานะเกมที่ติดตั้งอยู่กับ ZIP ล่าสุดเป็นคนละเรื่อง

ตอนตรวจเพื่อเขียนเอกสารนี้ ใน `~mods` พบแพ็กชื่อ `ThaiJP_Chapter1_P` เพียง 3 ไฟล์: `.pak` 347 bytes, `.utoc` 14,785 bytes, `.ucas` 19,902,000 bytes ซึ่งเป็นชุดรวมก่อนการแก้เปียโนล่าสุด ไม่ใช่ชุดแยก 9 ไฟล์ใน Final โปรแกรมแพ็กไม่ได้เปลี่ยนไฟล์เหล่านั้น และแฮชยังตรง snapshot ตอนเริ่มรอบแก้ UI ล่าสุด

ผู้ใช้อาจติดตั้งเองระหว่างรอบ จึงต้องตรวจสถานะจริงใหม่ก่อนลงม็อด อย่าถือ [qa/installation-latest.json](E:/FF7RebrithModTH/FF7Rebrith/qa/installation-latest.json) เป็นหลักฐานเกมปัจจุบันเสมอ เพราะบันทึกนั้นเป็นการติดตั้งรุ่น inventory ที่ทำไว้ก่อนหน้า

ถ้าผู้ใช้สั่งให้ติดตั้งชุดแยกล่าสุด: ปิดเกม สำรองม็อดปัจจุบัน แล้วติดตั้งไฟล์จากทั้ง 4 ZIP ให้ครบใน `~mods` ตรวจแฮช 12 ไฟล์หลังลง อย่าใช้ `install_current_set.py --inventory` ตรงๆ เพราะจะนำรุ่นเก่ากลับไปลง ไม่มีคำสั่งติดตั้งชุดแยก 4 ZIP แบบใหม่สำเร็จรูปที่ยืนยันแล้วใน workflow นี้

## 13. ภาพที่ผู้ใช้ส่งล่าสุด

ไฟล์อยู่ใน `C:\Users\godca\OneDrive\Pictures\Screenshots`:

- `Screenshot 2026-10-16 141104.png` — HUD ปาร์กัวร์/COMMAND มุมซ้ายล่าง
- `Screenshot 2026-10-16 141126.png` — คำอธิบาย ITEM ใต้หน้าต่างคำสั่ง
- `Screenshot 2026-10-16 141549.png`, `Screenshot 2026-10-16 141705.png` — แจ้งรับ Mega-Potion
- `Screenshot 2026-10-16 142442.png`, `Screenshot 2026-10-16 142520.png` — เปียโน/กล่องหยุดเล่น
- `Screenshot 2026-10-16 143634.png` — แจ้งกำจัดศัตรูและ EXP/AP/กิล

ภาพเหล่านี้เป็นหลักฐานก่อนแก้ ไม่ใช่หลักฐานว่าชุดแก้ล่าสุดผ่านการเล่นจริงแล้ว

## 14. เช็กลิสต์ก่อนส่งงานรอบถัดไป

- [ ] ขอบเขตที่แก้ตรงคำสั่งผู้ใช้ และไม่ได้ขยายไปบทใหม่หรือคำบรรยายศัตรูโดยไม่มีคำสั่ง
- [ ] ต้นทาง batch/scope ถูกอัปเดต ไม่ใช่แก้ผลรวมชั่วคราวอย่างเดียว
- [ ] รักษา index/รหัส/ลำดับ/metadata/แท็ก และบทพูดที่ไม่เกี่ยวข้อง
- [ ] คำลงท้าย/สรรพนามมีหลักฐาน หรือใช้ถ้อยคำกลางโดยไม่เดาเพศ
- [ ] กฎชื่อเฉพาะ UI อังกฤษ / Dialogue ไทย และตัวเลขยังตรง
- [ ] สร้าง/อ่านกลับ text assets และตรวจฟอนต์/ตัวเลข/อังกฤษผ่านตามสิ่งที่เปลี่ยน
- [ ] ตรวจความครบทั้งหมวดที่ขยาย ไม่อ้างว่าแปลทั้งเกมจากการตรวจบางหมวด
- [ ] แพ็ก ZIP ของส่วนที่เปลี่ยนลง Final ชื่อเดิม เก็บเพียงรุ่นล่าสุดของแต่ละส่วน
- [ ] เปิดทุกแพ็กร่วมกันแล้ว union ตรงชุดที่ตรวจ ไม่มี asset ทับกัน
- [ ] รายงานชัดว่าแพ็กแล้วหรือติดตั้งแล้ว และทดสอบในเกมจริงแล้วหรือยัง
- [ ] อัปเดตเอกสารนี้/QA/AGENTS เมื่อสถานะหรือคำสั่งผู้ใช้เปลี่ยน

## ข้อความสำหรับเริ่มแชต/ผู้รับช่วงใหม่

> อ่าน `E:\FF7RebrithModTH\HANDOFF.md` และ `E:\FF7RebrithModTH\FF7Rebrith\AGENTS.md` ก่อนทำงาน ตรวจ manifest ใน `qa/final-parts/latest.json` แล้วทำต่อเฉพาะขอบเขตที่ผู้ใช้สั่ง รักษา Ch.1–3 + inventory + UI ล่าสุด รักษาชื่อศัตรูอังกฤษทางการที่ทำแล้ว แพ็กงานที่เสร็จเป็น ZIP ล่าสุดแยกแต่ละส่วนใน `Mod\Final` โดยยังไม่ติดตั้งเกมเอง อย่าอ้างว่าดูคลิปหรือทดสอบเกมครบจากผลตรวจไฟล์
