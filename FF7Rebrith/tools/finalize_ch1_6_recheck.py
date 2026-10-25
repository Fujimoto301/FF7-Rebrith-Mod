"""Verify split release and write the latest all-completed-chapter handoff."""
import hashlib
from collections import Counter
from assemble_chapter6 import W,read,write
from assemble_ui_completion import fingerprint
from prepare_ch1_6_recheck import ROOT

def main():
    cfg=read('reference/ch1-6-recheck-build.json');base=read(ROOT+'/baseline.json')
    audit=read(ROOT+'/translation-audit.json');gender=read(ROOT+'/gender/summary.json')
    release=read('qa/final-parts/latest.json');mount=read('qa/final-parts/combined-mount-verification.json')
    prior=read(base['snapshot']+'/qa/final-parts/latest.json');old={p['zip']:p for p in prior['parts']}
    assert release['combined_text_records']==audit['total_combined_text_records']==24999
    assert mount['zip_count']==5 and mount['assets']==24 and mount['mod_files']==15
    assert mount['all_match_verified_combined_set'] and not mount['overlapping_assets']
    changed=[]
    for p in release['parts']:
        assert hashlib.sha256((W.parent/'Mod/Final'/p['zip']).read_bytes()).hexdigest()==p['sha256']
        if p['sha256']!=old[p['zip']]['sha256']:changed.append(p['zip'])
    assert changed==['ThaiJP_Common_P.zip']
    assert {p.name for p in (W.parent/'Mod/Final').iterdir()}==set(old)
    assert fingerprint()==base['protected']
    assert gender['actual_particle_occurrences']==477 and not gender['gender_mismatches'] and not gender['unresolved_particle_bearing_speakers']
    assert gender['source_records_scanned']==24999
    assert read('qa/shared-dialogs/latest.json')['combined_source']==cfg['source']
    assert len(read(ROOT+'/proof.json')['samples'])==32
    assert len(read(ROOT+'/old-glyph-regression.json')['fonts'])==8
    # Ensure packaged records match the last revision, not an earlier candidate.
    assert read('qa/active-working-set.json')['manifest']==ROOT+'/working-assets.json'
    for p in release['parts']:
        for rel,sha in p['assets'].items():assert read(ROOT+'/working-assets.json')[rel]==sha
    write(ROOT+'/release-verification.json',dict(total_records=24999,chapters_rechecked=[1,2,3,4,5,6],
      prior_chapter_records_rechecked=10506,previous_combined_records_preserved=24180,
      added_UI_records=701,added_shared_dialogue_and_system_records=118,
      source_corpus_candidates=10287,registered_UI_inventory_records=895,
      prior_deferred_later_state_records=209,new_shared_later_state_records=44,
      actual_gender_particle_occurrences=477,gender_mismatches=[],unresolved_gendered_speakers=[],
      old_glyph_assignments_preserved=674,total_glyph_clusters=677,appended_glyph_clusters=['พ็','ฟิ้','อึ้'],
      native_ASCII_digit_icon_glyphs_preserved=True,previous_Thai_glyph_metrics_preserved=True,
      Thai_compression='Atlas repacking produces small BC5 mask differences; no claim of byte-identical prior Thai masks.',
      ellipsis_low_baseline_preserved_all8fonts=True,proof_pages_visually_inspected=True,
      only_changed_ZIP='ThaiJP_Common_P.zip',all_four_scene_ZIPs_unchanged=True,
      ZIP_count=5,assets=24,mod_files=15,all_archives_mounted_and_read_back=True,no_overlap=True,
      source_and_installed_files_unchanged=True,installed=False,in_game_tested=False,new_full_audio_video_review=False,
      manifest='qa/final-parts/latest.json',backup=release['backups']))
    table='\n'.join(f"| Ch.{c} | {audit['per_chapter'][str(c)]['translated']:,} | {audit['per_chapter'][str(c)].get('NPC',0):,} | {audit['per_chapter'][str(c)].get('deferred',0)} |" for c in range(1,7))
    status=f'''# ตรวจซ้ำทุกบทที่ทำแล้ว Ch.1–6

อัปเดต 18 ตุลาคม 2026 (Asia/Bangkok) ตามคำสั่งให้ตรวจทุกบทด้วยเกณฑ์เดียวกับภาพตกหล่น Ch.1–2

ชุดล่าสุด **24,999รหัส / 24assets / 677glyph clusters** รักษาชุดก่อนหน้า24,180รหัสและACTORครบ เพิ่ม **701รหัส UI + 118รหัสบท/ตัวเลือกระบบส่วนกลาง** เก็บเฉพาะเหตุการณ์ของบทที่ทำแล้ว ไม่เริ่มCh.7–14

## ตรวจบทเดิมครบตามขอบเขตทั้ง6บท

| บท | รหัสเดิมที่ตรวจซ้ำ | NPCในกลุ่มรหัสNPC | กันสถานะภายหลัง |
| --- | ---: | ---: | ---: |
{table}

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
'''
    (W/'CH1-6-RECHECK-STATUS.md').write_text(status,'utf-8')
    note='''<!-- all-completed-chapters-current -->
## ล่าสุด: ตรวจซ้ำครบ Ch.1–6 — 18 ตุลาคม 2026

ส่วนนี้แทนพาธ/ยอด/ขั้นตอนปัจจุบันในประวัติด้านล่าง ตรวจบทเดิม10,506รหัสครบทั้ง6บทและสแกนcorpusอิสระ10,287candidateIDs เก็บตกใหม่701UI+118บท/ตัวเลือกส่วนกลาง รวม **24,999รหัส24assets677clusters** คง24,180รหัส/ACTORเดิมครบ กัน209สถานะภายหลังเดิมและ44shared NPCสถานะภายหลังใหม่ มีเหตุผลรายรหัส ไม่เริ่มCh.7

ชุดรวมล่าสุด **E:/FF7RebrithModTH/FF7Rebrith/translations/working-ch1-6-recheck-th.json**; staging **staging/ThaiJP_Ch1_6_Recheck_Working**; glyph/config **reference/ch1-6-recheck-cluster-map.json / ch1-6-recheck-build.json**; QA **qa/ch1-6-recheck** ใช้เป็นฐานบทต่อไป รายละเอียดครบที่ [CH1-6-RECHECK-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CH1-6-RECHECK-STATUS.md)

build chainล่าสุด: assemble_ch1_6_recheck.py → build_ch1_6_recheck.py --text-only(เมื่อglyphไม่เพิ่ม) → build_ch1_6_recheck.py --verify → audit_ch1_6_recheck.py → audit_ch1_6_glyph_regression.py → audit_gender_through_chapter6.py --active → audit_shared_dialogs.py → preview_ch1_6_recheck.py(ดูภาพ) → publish_final_parts.py → finalize_ch1_6_recheck.py ห้ามprepareซ้ำ/เปลี่ยนindex/เขียนทับsnapshot/ใช้auditหรือfinalizeบทเก่าทับactive context

UIใหม่ครอบคลุมFortCondor/CF, พาเหรด, โลมา/กบ, วิเคราะห์อัญเชิญ/ขุดค้น, รายงานGrasslands/Junon, การ์ด/แพ็ก, ร้าน/ตู้ขายของ และของเควสต์ บทใหม่ช่างภาพSnaps(โฟกัส)กับDorian(ปิอาโซลา)/เสียงผู้ชมคงป้ายUSอังกฤษ พูดชื่อไทย UnknownNPCกลาง ผลคำลงท้ายจริง477ครั้งใน467รหัส(ครับ335/ค่ะ83/คะ59) ไม่มีสลับเพศตามหลักฐานที่เก็บ ไม่อ้างว่าฟังวิดีโอทุกคนใหม่

เพิ่มglyph3clusterพ็/ฟิ้/อึ้แบบappend-only รักษา674assignment/metricsเดิมและnativeASCII/เลข/ไอคอนพิกเซลเดิม การrepackBC5ทำให้maskไทยเดิมต่างเล็กน้อย ไม่อ้างว่าไบต์ไทยเดิมครบ ฟอนต์8ชุดยังคงจุดไข่ปลา…ระดับล่างตามภาพผู้ใช้และnative period baseline

**ทุกบทต่อไปต้องตรวจshared UIและNPCที่ไม่ได้อยู่ในรหัสฉาก**: บทสอน/คำถาม/ใช่ไม่ใช่/ยกเลิก/ลองใหม่/กิจกรรมทั้งหมวด/HUD/ร้าน/ของเควสต์และnamespaceข้างเคียง ใส่familyลงaudit_shared_dialogs.py ตรวจชื่อ/ตัวเลข/เพศ/ellipsisพร้อมกัน อย่าพึ่ง*_sysหรือเลขChapterอย่างเดียว

Finalมี5ZIPต้องใช้ร่วมกันทั้งหมด อัปเดตเฉพาะCommon ZIPบททั้ง4คงเดิม อ่านกลับรวม24assetsผ่านไม่มีทับกัน สำรองนอกFinal ยังไม่ได้ติดตั้ง/เล่นทดสอบจริง/ดูเสียงครบใหม่ ข้อมูลบทเก่าในส่วนถัดไปเป็นประวัติ
<!-- /all-completed-chapters-current -->

'''
    for p in [W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'CHAPTER6-STATUS.md',W/'CH12-RECHECK-STATUS.md']:
        text=p.read_text('utf-8');title,body=text.split('\n',1)
        if '<!-- all-completed-chapters-current -->' in body:
            start=body.index('<!-- all-completed-chapters-current -->');end=body.index('<!-- /all-completed-chapters-current -->')+len('<!-- /all-completed-chapters-current -->')
            body=body[:start]+body[end:]
        p.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    table='\n'.join(f"| `{p['zip']}` | {len(p['assets'])} | {p['bytes']:,} |" for p in release['parts'])
    (W/'FINAL-PARTS.md').write_text(f'''# ZIP ล่าสุดแยกแต่ละส่วน

18 ตุลาคม 2026 หลังตรวจครบCh.1–6: **24,999ข้อความ / 24assets / 677glyph clusters / 5ZIP / 15mod files**

| ZIP | assets | bytes |
| --- | ---: | ---: |
{table}

ต้องใช้ทั้ง5ZIPร่วมกันจาก `E:/FF7RebrithModTH/Mod/Final` เก็บล่าสุดของแต่ละส่วนเท่านั้น รอบนี้อัปเดตเฉพาะCommon (Resident/TITLB/8fonts/8textures) อีก4ZIPบทไม่เปลี่ยน สำรองCommonเก่านอกFinalตามqa/final-parts/latest.json อ่านกลับร่วม24assetsผ่านไม่มีทับกัน ต้นฉบับ/dist/ม็อดในเกมไม่เปลี่ยน ไม่ได้ติดตั้งหรือทดสอบเล่นจริง

รายละเอียดและวิธีสร้างล่าสุด: [CH1-6-RECHECK-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CH1-6-RECHECK-STATUS.md) และ [HANDOFF.md](E:/FF7RebrithModTH/HANDOFF.md)
''','utf-8')
    print('All1–6 recheck release verified; Common only updated; all handoff/current workflow docs updated.')

if __name__=='__main__':main()
