# แนวทางแปล FF7 Rebirth

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

## คำเรียกคลาวด์ — เพิ่ม 23 ตุลาคม 2026

ผู้ใช้ให้แก้กรณีเรียก Cloud ว่า “เธอ” เป็น **นาย/คุณ** ตามความสัมพันธ์และน้ำเสียง หรือพ่อหนุ่มในน้ำเสียงผู้ใหญ่แบบบิล กลุ่มที่รวมคลาวด์ใช้พวกนาย/พวกคุณตามบริบท ต้องดูว่าใครเป็นผู้ฟังจริง ห้ามแทนทุกคำว่าเธอ: ผู้หญิง, บุคคลที่สาม, บทเพลง และบทสนทนาระหว่าง NPC ต้องรักษาบริบทเดิม ถ้าไม่ชัดให้ใช้ประโยคกลางโดยละสรรพนามที่ไม่จำเป็น พร้อมบันทึกเหตุผลราย ID

ตัวอย่างโรช: **นายเร็วขึ้นไปอีกแล้วนะ / สหายของฉัน** หลักฐานการตรวจ318รายการอยู่ที่ `qa/context-full-read/cloud-address-review.json` ตรวจรวมคำเรียกตัวละครชายอื่นและกลุ่มผู้เล่นด้วย; ยอด149จุดไม่ได้หมายถึงคลาวด์คนเดียวทั้งหมด อ่านตัวเลือกพร้อมทุกปุ่มและบทตอบรับต่อไปตามข้อกำหนดเดิม

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

Latest Costa activity UI supplement (2026-10-18): +131 UI records (164 inventoried;33 English/symbol entries preserved), Ch.6 UI153, combined23,811/23assets/674clusters. Only Common ZIP changed; all4scene ZIPs, all23,680 previous texts/ACTORs, fonts/textures and installed files preserved. See CHAPTER6-STATUS.md activity section and qa/chapter6/activity-ui. Run audit_chapter6_activity_ui.py and preview_chapter6_activity_ui.py in the current build chain; finalize_chapter6.py also finalizes activity docs. No new spoken dialogue/Ch.7/runtime test.

อัปเดตล่าสุด18ตุลาคม2026: Ch.6เสร็จแล้ว ดู CHAPTER6-STATUS.md และ E:/FF7RebrithModTH/HANDOFF.md เป็นหลัก ชุดปัจจุบันworking-through-chapter6-th.json/staging ThaiJP_ThroughChapter6_Working/qa chapter6 รวม23,811รหัส23assets674clusters ใช้5ZIP Chapter1/Chapter2/Chapter3_4_5/Chapter6/Commonร่วมกัน เพิ่ม1,698บท+153UI/NPC698 แยก107สถานะภายหลัง คงงานเดิม21,960รหัสครบ คำลงท้ายตรวจทั้งชุด477ครั้งไม่มีสลับเพศตามหลักฐานที่เก็บ ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ UnknownNPCกลาง ใช้วิสเปอร์/อิฟาลน่าตามPlearn ไม่ลงเกมหรืออ้างruntime test ข้อความปัจจุบันบทเก่าด้านล่างเป็นประวัติ

อัปเดตล่าสุด18ตุลาคม2026: Ch.6เสร็จแล้ว ดู CHAPTER6-STATUS.md และ E:/FF7RebrithModTH/HANDOFF.md เป็นหลัก ชุดปัจจุบันworking-through-chapter6-th.json/staging ThaiJP_ThroughChapter6_Working/qa chapter6 รวม23,680รหัส23assets674clusters ใช้5ZIP Chapter1/Chapter2/Chapter3_4_5/Chapter6/Commonร่วมกัน เพิ่ม1,698บท+22UI/NPC698 แยก107สถานะภายหลัง คงงานเดิม21,960รหัสครบ คำลงท้ายตรวจทั้งชุด477ครั้งไม่มีสลับเพศตามหลักฐานที่เก็บ ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ UnknownNPCกลาง ใช้วิสเปอร์/อิฟาลน่าตามPlearn ไม่ลงเกมหรืออ้างruntime test ข้อความปัจจุบันบทเก่าด้านล่างเป็นประวัติ

อัปเดตล่าสุด 17 ตุลาคม 2026: Ch.5 เสร็จแล้ว ดู CHAPTER5-STATUS.md และ E:/FF7RebrithModTH/HANDOFF.md เป็นหลัก ชุดปัจจุบันคือ translations/working-through-chapter5-th.json / staging/ThaiJP_ThroughChapter5_Working / qa/chapter5 รวม21,960รหัส22assets660clusters ใช้ Chapter1/Chapter2/Chapter3_4_5/Common ทั้ง4ZIPใน Final ทวน Ch.5 ครบ1,316รหัสและร้านบนเรือ7รหัส NPC581รหัสไม่เติมคำระบุเพศถ้าไม่ยืนยัน คำลงท้ายชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ ไม่เติมทุกบรรทัด ตรวจทั้งชุด456ครั้งไม่มีสลับเพศตามหลักฐานที่เก็บไว้ ภาพ proof/การอ่านไฟล์กลับไม่ใช่ runtime test ยังไม่ติดตั้งเกม ข้อมูล “ปัจจุบัน” ของบทเก่าด้านล่างเป็นประวัติ

สถานะล่าสุด 17 ตุลาคม 2026: Chapter 4 เพิ่ม 3,206 รายการ รวม 20,637 รหัส / 22 assets / 642 clusters ใช้ working-through-chapter4-th.json และ build/verify --chapter4-working พร้อม audit_chapter4.py ดู CHAPTER4-STATUS.md Final ล่าสุดมี Chapter1, Chapter2, **Chapter3_4** และ Common รวม 4 ZIP ต้องใช้ร่วมกัน ชื่อ ZIP ร่วมเป็นคำตอบที่ผู้ใช้เลือก แทน Chapter3 เดิม สำรองรุ่นเก่านอก Final ไม่ได้ติดตั้ง/ทดสอบในเกม ข้อความสถานะ Ch.3/Ch.4 ยังไม่เริ่มด้านล่างเป็นประวัติ

สถานะล่าสุด Chapter 3: ผู้ใช้สั่งเริ่มแล้ว แปล/ทวน 253 ข้อความ รวมเป็น `translations/working-through-chapter3-th.json` 17,431 รหัส ใช้ `assemble_chapter3.py`, build/verify `--chapter3-working`, `audit_chapter3.py`, `preview_chapter3.py` และ publish ตาม `qa/active-working-set.json` ดู `CHAPTER3-STATUS.md` ตอนนี้ Final มี ZIP ล่าสุด 4 ส่วน ต้องใช้ร่วมกัน GRASE ใน Chapter2 ZIP มีบทเหมืองของ Ch.3 ด้วย Chapter3 ZIP เพิ่ม JUNOE ฉากออกเหมือง ตาราง glyph ใหม่ append 1 cluster โดยรักษา aliases เดิมและแนว native ASCII ไม่ได้เริ่มบท Chapter 4 หรือติดตั้งในเกม ข้อความ Ch.1–2/UI/ไอเทม/ชื่อศัตรูเดิมคงเดิม

อัปเดตแนวฟอนต์ล่าสุด: ชื่อและจำนวนที่เกมเติมภายหลังยังเป็น ASCII เดิม จึงต้องจัดแนวไทยให้ตรง native ASCII ด้วย ไม่ใช้เพียง aliases ผสมไทย รอบนี้ขยับ Thai clusters ทั้งกลุ่มไปยังขอบหมึก H เดิมในแต่ละฟอนต์ คืน Latin aliases ให้ใช้ origin เดิม และจัด digit aliases ให้ตรงแนวนี้ คง original glyph/พิกเซล/ระยะแนวนอนทั้งหมด รวมถึง optical overshoot ของตัวเลขเดิม รายละเอียด `BASELINE-ALIGNMENT-STATUS.md` และ `reference/native-baseline-policy.json` ขั้น build UI เรียกตัวปรับแนวอัตโนมัติแล้ว ตรวจเพิ่มด้วย `audit_dynamic_baselines.py` (เทียบ snapshot เฉพาะรอบนี้) ภาพจำลองต้องแทนชื่อ/เลขหลัง encode เหมือน runtime อัปเดต Common ZIP เท่านั้น ยังไม่ได้ทดสอบในเกม

คำสั่งล่าสุดให้แปลชื่อศัตรูทั้งหมดแล้ว: ใช้อังกฤษทางการจาก US รหัสตรงกัน รวมชื่อศัตรูหลัก 312 รหัส ศัตรู Gears and Gambits 14 รหัส และชื่อส่วนเป้าหมาย 72 รหัส เป็น 398 รหัส (เพิ่มใหม่จริง 395) รวมชุดล่าสุด 17,178 รหัส ข้อความพักชื่อศัตรูด้านล่างเป็นประวัติก่อนผู้ใช้สั่งเริ่ม คงชื่อที่กล่าวใน Dialogue เดิมเป็นไทย ใช้ assemble_enemy_names.py ก่อน assemble_ui_completion.py และตรวจ audit_enemy_names.py เพิ่ม ดู ENEMY-NAMES-STATUS.md รอบนี้เปลี่ยนเฉพาะ Common ZIP ไม่ได้ติดตั้งเกม

อัปเดตจากภาพทดสอบล่าสุด: เก็บหมวดคำอธิบาย COMMAND, แจ้งรับของ/ผลต่อสู้/ระบบ และหน้าเปียโนเพิ่ม 421 รหัส ใช้ `Terrain Action` และ `COMMAND` อังกฤษใน HUD มุมซ้ายล่าง ส่วนคำอธิบายใต้เมนูเป็นไทย เปียโนใช้ป้ายควบคุม/กล่องยืนยันไทย ชื่อเพลงและตัวโน้ตเป็นชื่อ/สัญลักษณ์อังกฤษตาม US ผู้ใช้ยืนยันยังพักการแก้ชื่อศัตรู รวม UI ปัจจุบัน 7,201 รหัสจาก 5,046 แม่แบบ รวมทั้งชุด 16,783 รหัส การแก้ครั้งนี้อยู่ใน Common ZIP เท่านั้น ไฟล์ฉากและฟอนต์ไม่เปลี่ยน ตรวจด้วย `audit_ui_piano_notifications.py` เพิ่มจากการตรวจปกติ ภาพ proof ไม่ใช่ภาพในเกม

นโยบาย ZIP ล่าสุด: ผู้ใช้ให้แยก ZIP แต่ละส่วน เก็บเฉพาะรุ่นล่าสุดของแต่ละส่วนใน Mod/Final แทนนโยบาย ZIP รวมอันเดียวก่อนหน้า ตอนนี้มี Chapter1, Chapter2 และ Common (UI/ไอเทม/ฟอนต์/ข้อความร่วม) ต้องใช้ทั้ง 3 ร่วมกัน รายละเอียดและวิธีอัปเดตอยู่ใน FINAL-PARTS.md ใช้ publish_final_parts.py และตรวจเปิดทั้ง 3 แพ็กร่วมกัน ไม่ลงเกมอัตโนมัติ

ประวัติคำสั่ง ZIP รวมก่อนผู้ใช้สั่งแยกแต่ละส่วน 2026-10-16: ทุกส่วนที่ทำเสร็จหรือแก้ไขเสร็จให้รวมเป็น ZIP ล่าสุดที่ `E:/FF7RebrithModTH/Mod/Final/ThaiJP_Chapter1_P.zip` เขียนทับชื่อเดิม และใน Final ให้มีเฉพาะ ZIP ล่าสุด ไม่เก็บรุ่นเก่าหรือ ZIP อ้างอิงของทีมอื่นไว้ด้วย คำสั่งนี้แทนที่ข้อห้ามแพ็กงานที่เสร็จในอดีต แต่ไม่ได้อนุญาตให้ติดตั้งในเกมอัตโนมัติ ชุด UI ปัจจุบันใช้ `tools/publish_final.py` แพ็ก/อ่านกลับ 21 assets และตรวจ ZIP ที่มีเฉพาะม็อด 3 ไฟล์ พร้อมลิขสิทธิ์ฟอนต์ใน archive comment รายงาน `qa/ui-completion/final-release.json`

สถานะล่าสุด 2026-10-16: งาน UI จากภาพรวมเป็นไฟล์ทำงานแล้ว เพิ่ม 6,780 รหัสจาก 4,917 แม่แบบ รวมชุดเดิม 16,362 รหัส ตรวจอ่านกลับ 21 assets และตรวจความครบของหมวด/ฟอนต์/แท็ก/ชื่อเฉพาะแล้ว ดู `UI-COMPLETION-STATUS.md` และ `qa/ui-completion/final-audit.json` ชุดนี้ยังไม่แพ็กหรือติดตั้ง และยังไม่ได้ทดสอบเล่นจริง ข้อความประวัติด้านล่างที่บอกว่ายังไม่ได้แปลรายละเอียด UI ถูกแทนที่ด้วยสถานะนี้สำหรับหมวดที่ขยายแล้ว

ขยายขอบเขตจากภาพทดสอบ 18 ภาพ: แปลหมวดที่เหลือทั้งหมวด ได้แก่คำบรรยายอุปกรณ์ ค่าสถานะ/ความต้านทาน คำแนะนำเมนู คู่มือ/ทิป รายละเอียดตั้งค่าและโหมดถ่ายภาพ ข้อความ HUD/คำสั่งภาคสนาม ชื่อบทและช่วงเวลา เป้าหมายเนื้อเรื่องและชื่อพื้นที่/ข้อมูลเซฟ ผู้ใช้ยืนยันว่าข้อความ UI เป้าหมายและพื้นที่ทำทั้งเกม ไม่เพิ่มบทพูด Chapter 3 เป็นต้นไป ชื่อ Chapter ใช้อังกฤษทางการ ช่วงเวลาอดีต/ปัจจุบันใช้ไทย ชื่อสถานที่ใน UI ใช้อังกฤษตามเงื่อนไขชื่อเฉพาะ ชื่อศัตรูตั้งนโยบายอังกฤษแต่ยังไม่เริ่มแก้ป้ายชื่อศัตรูในรอบนี้ เก็บงานขยายนี้เป็นต้นฉบับก่อนจนกว่าจะสั่งติดตั้ง

คำสั่งติดตั้งล่าสุด 2026-10-16: “อันนี้ลงmodได้เลย” อนุญาตให้แพ็กและลงชุดความสามารถไอเทม/สกิลทั้งเกมรวม Ch.1–2 และเมนูเดิม ใช้โหมด `--inventory` ของ pack_prototype.py, package_release.py และ install_current_set.py สำรองด้วย prepare_inventory_install.py ก่อนแพ็ก คงชื่อ ThaiJP_Chapter1_P ทั้ง 3 ไฟล์และตรวจแฮชหลังลง คำสั่งนี้ยกเว้นข้อกำหนดเก็บต้นฉบับสำหรับชุดนี้ครั้งนี้เท่านั้น งานใหม่ภายหลังยังไม่ติดตั้งโดยอัตโนมัติ

ติดตั้งชุดดังกล่าวสำเร็จแล้ว อ่านกลับครบ 21 assets และตรวจแฮช 3 ไฟล์หลังติดตั้งตรงกับแพ็ก รายงาน `qa/installation-latest.json` สำรองที่ `qa/installations/553a3240ce234bc984b0a279b9f4dca6/before/installed` โฟลเดอร์ dist/Chapter1-Test และ ZIP เป็นรุ่นเดียวกัน ยังไม่ได้ทดสอบเล่นจริง

อัปเดต 2026-10-16: ผู้ใช้สั่งเริ่มแปลความสามารถ/ผลของไอเทมและสกิลในเมนูทั้งหมดทั้งเกมแล้ว รวมแมทีเรีย เวทมนตร์ ท่าตัวละคร ท่าเรียกอสูร ท่าร่วม สกิลติดตัวและอาวุธ คงชื่อทางการเป็นอังกฤษในเมนู ข้อกำหนดนี้แทนที่ข้อความรอเริ่มงานฐานข้อมูลด้านล่าง เก็บงานใหม่เป็นต้นฉบับและไฟล์ทำงานก่อน ยังไม่แพ็กหรือติดตั้งจนกว่าจะมีคำสั่ง

งานความสามารถไอเทม/สกิลทั้งเกมมีคำอธิบาย 2,169 รหัสและชื่ออังกฤษ 2,773 รหัส (หลายรหัสใช้ข้อความเดียวกัน) รวมผลอุปกรณ์ แมทีเรีย เวท/ท่าอาวุธ ท่าลิมิต ท่าร่วม สกิลติดตัว อสูร หนังสือแต้มสกิล ชิปคราฟต์ การ์ด Queen's Blood อุปกรณ์/สกิลแข่ง Chocobo และท่า/เงื่อนไขในมินิเกมต่อสู้ ไม่ใช่การแปลข้อความเนื้อเรื่องทุกบทหรือคำบรรยายประวัติอาวุธ/ไอเทมเควสต์ทั้งหมด ต้นฉบับแก้ได้ที่ `translations/inventory/batch-*.json` ใช้ `reference/inventory-templates.json` เป็น index คงที่ ห้ามเรียงใหม่ แปลจาก JP ใช้ US รหัสตรงกันตรวจชื่อและกลไก

รวมด้วย `tools/assemble_inventory.py` สร้างด้วย `tools/build_chapter1.py --inventory-working` ตรวจ `tools/verify_chapter1.py --inventory-working` และ `tools/audit_inventory.py` ไฟล์รวมคือ `translations/working-inventory-th.json` แยก staging/QA เป็น `ThaiJP_Inventory_Working` และ `qa/inventory` ชุดติดตั้งเดิมและ dist ยังไม่เปลี่ยน ตรวจภาพ glyph จริงได้ด้วย `tools/preview_inventory.py` ภาพนี้ไม่ใช่ภาพในเกม และยังต้องทดสอบการจัดวางจริงในเมนู ตรวจความครอบคลุม Normal/Small ทุกอักษรแล้ว ฟอนต์หัวข้อขนาดใหญ่ยังคงขอบเขตสัญลักษณ์เดิมของเกม รายละเอียดที่ `qa/inventory/font-coverage.json`

ศัพท์กลไกของชุดความสามารถนี้: JP バースト / US Stagger ใช้ “สแตกเกอร์” ตาม PlearnGaming เช่น `$Item_M_IND_008_help`, `$Materia_Description_102`, `$bt_PC0000_Burst002_help`, `$bt_PC0002_Burst006_help` และ `$bt_PC0003_Burst001_help` ไม่ใช้ “เสียสมดุล” แทนสถานะนี้ เพราะในม็อดอ้างอิงยังใช้คำนั้นกับบริบท pressure หลักฐานที่ `qa/inventory/reference-terminology.json` รักษาบทพูด Ch.1–2 เดิมในการทำงานชุดนี้

สถานะติดตั้งล่าสุด: ผู้ใช้สั่ง “ลงอันที่แก้แล้วได้เลย” จึงแพ็กและติดตั้งชุด Chapter 1–2 + เมนูที่แก้ตามเงื่อนไขชื่อเฉพาะแล้ว ใช้ `tools/pack_prototype.py --through-chapter2` และ `tools/package_release.py --through-chapter2` อ่านกลับครบ21 assets และใช้ชื่อไฟล์เดิม `ThaiJP_Chapter1_P` แทนชุดก่อนหน้าใน `~mods` ตรวจแฮชหลังติดตั้งครบ3ไฟล์ บันทึกที่ `qa/installation-latest.json` และสำรองที่ `qa/installations/` การอนุญาตนี้ครอบคลุมการลงชุดปัจจุบันครั้งนี้ งานบทถัดไปยังเก็บเป็นต้นฉบับก่อน ไม่ถือว่าตรวจแพ็ก/แฮชเป็นการทดสอบเล่นในเกม

ข้อกำหนดชื่อเฉพาะล่าสุด (ขยายจากชื่อเมือง/สถานที่): แปลหรือถอดเสียงชื่อเฉพาะเป็นไทยในบทพูดและข้อความเนื้อเรื่อง/Dialogue ที่เปิดอ่าน เช่น ชื่อคน เมือง สถานที่ และองค์กรที่กล่าวในประโยค ในเมนูที่แปลคงชื่อเฉพาะเป็นอังกฤษตามชื่อทางการ โดยป้ายชื่อตัวละคร/ผู้พูดยังคงอังกฤษ ไม่ขยายงานไปแก้ชื่อบนแผนที่ ป้ายสถานที่ หรือหน้าจอแสดงชื่อพื้นที่ที่ยังไม่ได้อยู่ในขอบเขต ไม่ถือว่าคำเรียกระบบหรือคำทั่วไปทุกคำเป็นชื่อเฉพาะ

ผู้ใช้ยืนยันเพิ่มเติมขณะตรวจงานแล้วว่า **ชื่อไอเทม/สกิลใช้ไทยใน Dialogue และอังกฤษในเมนู** จึงไม่ใช้ข้อกำหนดคงชื่ออังกฤษของเมนูไปบังคับกับบทพูดด้วย ปุ่มยืนยันของระบบ เช่น ส่งมอบ Windmill Gear, รายชื่อ Burke/Burt/Beck ในตัวเลือก และชื่อมินิเกมบนกล่องยืนยันเป็น UI ส่วนบทพูด NPC รอบเมืองเป็น Dialogue แม้ไม่มี ACTOR metadata งานฐานข้อมูลชื่อ/ความสามารถไอเทมและสกิลยังรอคำสั่งให้เริ่มตามเดิม

อัปเดต 2026-10-15: ผู้ใช้อนุญาตให้ทำ Chapter 2 ต่อและตรวจซ้ำเรื่องตกหล่นกับเพศผู้พูดแล้ว งานใหม่เก็บเป็นต้นฉบับและไฟล์ทำงานเท่านั้น ใช้ `translations/chapter2/batch-*.json` รวมด้วย `tools/assemble_chapter2.py` แล้วสร้าง/ตรวจด้วย `tools/build_chapter1.py --chapter2-working` และ `tools/verify_chapter1.py --chapter2-working` ชุดนี้แยกที่ `staging/ThaiJP_ThroughChapter2_Working` และ `qa/chapter2` ห้ามใช้แทนชุดทดลองที่ติดตั้งอยู่โดยไม่ได้รับคำสั่งติดตั้ง

รายการ Chapter 2 อยู่ใน `reference/chapter2-source.json` และชุดบทพูดร่วมเพิ่มเติม `reference/chapter2-shared-source.json` คง index เดิม ไม่เรียงใหม่ ข้อยกเว้นเหตุการณ์ภายหลังอยู่ใน `reference/chapter2-deferred.json` ป้ายชื่อใช้ข้อมูล US ตรงรหัสเป็นหลัก ไฟล์รวมใหม่คือ `translations/working-through-chapter2-th.json` โดยยังเก็บ `translations/working-th.json` ของชุด Chapter 1 + เมนูไว้ตามเดิม

บทพูดร่วมที่เพิ่มจากการตรวจซ้ำครอบคลุมคู่แข่งควีนส์บลัดในคาล์ม ร้านมูเกิ้ลครั้งแรก และบทแชดลี่ย์/MAI/สมาชิกกลุ่มขณะสำรวจกราสแลนด์ ข้อมูลชื่อและความสามารถในฐานข้อมูลไอเทม/สกิลยังไม่เริ่มแปล ใช้ศัพท์ที่ยืนยันเพิ่มจาก Remake เช่น แชดลี่ย์ คิริเอะ โจโกโบะ มูเกิ้ล และเซเว่นเฮฟเว่น พร้อมหลักฐานใน glossary

ตรวจคำระบุเพศ Chapter 2 แยกใน `qa/chapter2/gender-review.json` ใช้ตัวตนผู้พูดและความสัมพันธ์ที่ต้นฉบับระบุชัด เช่น พี่ชาย/น้องสาว/เด็กหญิง ไม่อ้าง suffix NPC เป็นหลักฐาน เพศแชดลี่ย์มีข้อมูลตัวละครทางการประกอบ ไม่ได้เปิดดู/ฟังคลิปใหม่ครบทุกบรรทัดในการตรวจรอบนี้ สำหรับ NPC ที่ระบุเพศไม่ได้ใช้ถ้อยคำกลางๆ ตามเดิม

ขอบเขตปัจจุบัน: บทพูด Chapter 1 และงานที่ผู้ใช้ขอเพิ่มคือหน้าเริ่มเกม เมนูหลัก เมนูหยุดเกม เซฟ/โหลด พร้อมปุ่ม กล่องยืนยัน และคำแนะนำในหน้าเมนูที่เกี่ยวข้อง ใช้เสียงญี่ปุ่น สร้างงานใน `FF7Rebrith` ใช้บริบท PlearnGaming และให้ฟอนต์ใกล้ต้นฉบับเกมที่สุด

ข้อกำหนดสำหรับการแปลไอเทมและสกิลในอนาคต: คงชื่อไอเทมและชื่อสกิลเดิม ไม่แปลชื่อ แปลเฉพาะความสามารถและผลของการใช้งาน ผู้ใช้กำหนดว่า “ตอนนี้ยังไม่ต้องเริ่ม” จึงรอคำสั่งให้เริ่มส่วนนี้ก่อน ไม่ขยายงาน Chapter 1 ไปแปลไอเทมหรือสกิลในตอนนี้

**ชื่อนอกบทพูดใช้ภาษาอังกฤษ** ตามชื่อทางการของเกม ได้แก่ป้ายผู้พูด รายชื่อสมาชิก และหน้าสถานะ **ชื่อในประโยคบทพูดใช้ไทย** เช่น Cloud บนป้าย แต่ “คลาวด์” ในประโยค ภาษาอังกฤษบนป้ายอ้างอิงข้อมูล US ของเกม ไม่ใช้การถอดเสียงจากญี่ปุ่นเอง

ใช้ `reference/plearngaming/glossary.json` ตรวจคำศัพท์พร้อมหลักฐาน เช่น ทีฟ่า โซลเจอร์ แสตมป์ โฮโจ มิดการ์ ไลฟ์สตรีม คำที่ไม่มีหลักฐานจากม็อดอ้างอิงให้ระบุแยกจากคำที่ยืนยันแล้ว

Wutai / ウータイ ใช้ “อู่ไถ” ตามม็อด Remake ของ PlearnGaming ที่ให้มา ยืนยันจากบทพูดหลายจุด เช่น `Text/US/020-TOWN8_TxtRes.uexp` รหัส `$tk_town8_3016_0010_mn28_0` และ `$tk_town8_3192_0010_wm23_0` ไม่ใช้ “วูไท” ในคำแปลไทย

แปลจาก JP โดยอ่านบทพูดก่อนและหลังประกอบ คงน้ำเสียงผู้พูด อย่าใช้การแทนชื่อทั้งไฟล์ ต้องคงรหัสข้อความ รหัสตัวละคร แท็ก ตัวแปร และ metadata อื่น ๆ การเปลี่ยน metadata อนุญาตเฉพาะค่า ACTOR เป็นอังกฤษตามข้อกำหนดล่าสุด

ใช้เลขอารบิกสำหรับหมายเลข จำนวน อายุ ระยะเวลา และลำดับที่มีค่าชัดเจน เช่น เซคเตอร์7, หน่วยที่2, 5ปีก่อน, อายุ16, 2,000ปี และ 90องศา ตามคำขอผู้ใช้ ไม่แทนคำที่ไม่ได้เป็นตัวเลข เช่น ศูนย์วิจัย พันธสัญญา ห้าม หรือ “คนหนึ่ง” ที่ใช้หมายถึงบุคคลไม่เจาะจง บันทึกการแก้ Chapter 1 ใน `qa/chapter1/number-style-changes.json`

คำลงท้าย “ครับ/ค่ะ/คะ” ต้องเทียบผู้พูดกับฉากในคลิปอ้างอิงที่ผู้ใช้ให้: https://www.youtube.com/watch?v=i4gD0mmj5vc ใช้เฉพาะฉากเปิดและ Chapter 1 ก่อนเวลา 02:06:42 จับคู่ภาพ ชื่อผู้พูด และบทพูดกับรหัสข้อความ อย่านับการเดาจากรหัส NPC เป็นการยืนยันจากคลิป “คะ…ครับ!” เป็นเสียงติดอ่าง ต้องแยกจากคำลงท้ายหญิง

ตรวจคำลงท้ายเดิมครบ 71 รายการแล้ว: คงคำลงท้าย 20 รายการ (18 รายการจับคู่ตัวตนผู้พูดจากภาพ และ 2 รายการมีป้าย Militiaman ในข้อมูล US ของเกม) อีก 51 รายการใช้คำสุภาพที่ไม่ระบุเพศ เพราะยังจับคู่ผู้พูดไม่ได้ชัด หลักฐานรายประโยคอยู่ใน `reference/gender-particle-review.json` ต้นฉบับก่อนแก้อยู่ใน `reference/gender-particle-baseline.json` และ `qa/chapter1/before-gender-review` ตรวจความตรงกันของคำแปล หลักฐาน และคำลงท้ายด้วย `tools/audit_gender_particles.py` ผลอยู่ใน `qa/chapter1/gender-particle-audit.json` อย่าอ้างว่าดูครบทุกประโยคจากคลิปหรือฟังเสียงครบแล้ว

อ้างอิงเพิ่มเติมจากเพลย์ลิสต์เสียงญี่ปุ่นของผู้ใช้: https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU ตอนแรก https://www.youtube.com/watch?v=bxrLsiU-QKk ตรวจภาพฉากคนขับรถ Mayor Zander และ Tifa ประกอบกับคลิปเดิม บันทึกข้อสังเกตใน `reference/japanese-video-reference.json` ข้อความถอดเสียงอัตโนมัติใช้ค้นเวลาฉากเท่านั้น มีคำผิด จึงไม่แทนที่บทญี่ปุ่นจากไฟล์เกม และไม่ถือเป็นหลักฐานว่าได้ฟังเสียงพากย์แล้ว

ข้อความ Chapter 1 ปัจจุบันคัดด้วย `$C1910_` (ไม่รวมสรุปเรื่องราวภาคก่อน), `$NIBLT_NPC_10_`, `$NIBLM_BOS_00_` มี 1,157 ข้อความไม่ว่างจาก 3 assets ข้อความชื่อใน UI 27 รายการอยู่ใน Resident ขอบเขต UI ที่ขอเพิ่มบันทึกแยกใน `reference/menu-source.json` ไม่แปลข้อความของบทถัดไป

คำแปลเมนูอยู่ใน `translations/menu/menu-*.json` อ้างอิง index ใน `reference/menu-source.json` รวมเป็น `translations/menu-th.json` และไฟล์ทำงานรวมกับ Chapter 1 ที่ `translations/working-th.json` โดย `tools/assemble_menu.py` ใช้ `tools/build_chapter1.py --menus-working` และ `tools/verify_chapter1.py --menus-working` สร้างและตรวจเฉพาะ `staging/ThaiJP_Working` และ `qa/menu` ไม่สร้าง ZIP ไม่อัปเดต `dist` หรือไฟล์ในเกม รอรวมแพ็กเมื่อทำครบตามคำสั่งผู้ใช้

ข้อยกเว้นตามคำสั่งล่าสุด: ผู้ใช้ขอให้นำงานเมนูปัจจุบันทำเป็นม็อดและติดตั้งแล้ว ใช้ `tools/pack_prototype.py --menus` และ `tools/package_release.py --menus` แพ็กรวมกับ Chapter 1 ในชื่อ `ThaiJP_Chapter1_P` แล้วอัปเดตทั้ง 3 ไฟล์ใน `~mods` พร้อมสำรองรุ่นก่อนหน้าและตรวจค่าแฮช การอนุญาตนี้ครอบคลุมชุดทดลองปัจจุบัน ไม่ยกเลิกข้อกำหนดให้เก็บงานในอนาคตเป็นต้นฉบับก่อน

งานเมนูนี้รวมชื่อหมวดของ OPTIONS เท่านั้น รายละเอียดค่าตั้งค่า คำอธิบายกราฟิก/เสียง/ปุ่มควบคุม และคู่มือทั่วไปยังอยู่นอกชุดนี้ ชื่อไอเทมและสกิลในข้อความแนะนำคงอังกฤษ เช่น Assess, Magnify, Buster Sword และ Weapon Ability Damage +5% รวมถึงชื่อตัวละครใน UI เช่น Cloud และ Tifa ส่วนข้อมูลชื่อ/ความสามารถไอเทมและสกิลในฐานข้อมูลยังไม่เริ่มแปล

เพิ่มตามคำขอล่าสุด: หน้าเลือกระดับความยากและหน้าเลือกโหมดต่อสู้ แปลเฉพาะหัวข้อและคำอธิบายภาษาญี่ปุ่น คง EASY, NORMAL, ADVANCED, HARD, ACTION และ CLASSIC เป็นอังกฤษตามต้นฉบับ ห้ามแปลงชื่อโหมดเป็นไทยหรือแก้ค่าระดับความยาก/โหมดจริง ดูรายการเฉพาะหน้าจอที่ `reference/menu-screen-settings-scope.json`

คำแปลที่แก้ไขได้อยู่ใน `translations/chapter1/batch-*.json` index อ้างอิง `reference/chapter1-source.json` ห้ามเรียง source ใหม่โดยไม่ย้ายคำแปลให้ตรงกัน หลังแก้ให้ assemble, build, verify และ pack ใหม่

ฟอนต์ไทยเลือก Noto Sans Thai น้ำหนัก 300 หลังเปรียบเทียบกับ glyph จริงของเกม อักษรอังกฤษและไอคอนใช้ glyph เดิม ห้ามย่อไทยบางขนาดเพียงเพื่อให้ยัดลง atlas ได้ ให้รักษาสัดส่วนและเพิ่มพื้นที่อย่างตรวจสอบได้ สระและวรรณยุกต์จัดกลุ่มด้วย HarfBuzz/FreeType ต้องสร้างตาราง private-use ใหม่เมื่อเพิ่มข้อความ

ตัวเลข 0–9 ในข้อความที่แปลใช้ private-use aliases ของ glyph ตัวเลขเดิม ปรับเฉพาะค่าแนวตั้งให้ขอบหมึกด้านล่างเสมอกับอักษรไทยในแต่ละขนาดฟอนต์ รูปทรง พิกเซล และระยะเลื่อนแนวนอนคงเดิม ส่วน glyph ASCII เดิมและชื่อ ACTOR ภาษาอังกฤษคงตำแหน่งเดิม ตรวจทั้ง 10 ตัวเลขในฟอนต์ทั้ง 8 ขนาดด้วย `tools/verify_chapter1.py`

ไฟล์ทำงานเมนูเพิ่ม aliases ของอักษรอังกฤษสำหรับบรรทัดที่ผสมภาษาไทย ให้ใช้แนวฐานเดียวกันโดยคงภาพ glyph และระยะเลื่อนแนวนอนเดิม ตัวอักษรที่มีหางลงล่าง เช่น g และ p คงตำแหน่งเทียบกันตามธรรมชาติ ข้อความอังกฤษล้วนและชื่อ ACTOR ยังใช้ ASCII เดิม การเข้ารหัส aliases ต้องข้ามแท็กปุ่มและตัวแปรทั้งชุด เช่น `<button=L1>` และ `<object=0>` ห้ามแปลงอักษรหรือตัวเลขภายในแท็ก ตรวจแท็กจากไฟล์ที่สร้างโดยตรงก่อนถอด aliases กลับด้วย

ฐาน Remake อ่านและตรวจคำศัพท์ได้แล้ว ส่วน Crisis Core แตก Atel ได้ แต่ยังไม่ยืนยันการถอดรหัสข้อความ อย่าอ้างว่าใช้บริบท Crisis Core ได้ครบหรือว่าทดสอบในเกมแล้วจากการอ่านแพ็กอย่างเดียว
