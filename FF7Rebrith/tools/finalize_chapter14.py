"""Verify the complete split release and bind the current handoff to its source."""
import re
from pathlib import Path
from prepare_chapter9 import W,read,write
from audit_chapter14 import CFG,Q,digest
from assemble_ui_completion import fingerprint

def main():
    cfg=read(CFG);sha=digest(W/cfg['source']);a=read(Q+'translation-audit.json');s=read(Q+'editorial-signoff.json');r=read('qa/final-parts/latest.json');m=read('qa/final-parts/combined-mount-verification.json');b=read(Q+'baseline.json');g=read(Q+'gender/summary.json')
    assert sha==a['source_sha256']==s['source_sha256'] and a['new_records']==936 and a['previous47503_text_and_ACTOR_preserved']
    for rel,h in s['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    assert fingerprint()==b['protected']
    assert m['zip_count']==9 and m['mod_files']==27 and m['assets']==28 and m['all_match_verified_combined_set'] and not m['overlapping_assets']
    assert r['chapters']==list(range(1,15)) and r['working_manifest']==Q+'working-assets.json' and r['combined_text_records']==48439
    final=W.parent/'Mod/Final';assert {p.name for p in final.iterdir()}=={p['zip'] for p in r['parts']}
    for p in r['parts']:assert digest(final/p['zip'])==p['sha256']
    old={p['zip']:p for p in read(Path(b['snapshot'])/'qa/final-parts/latest.json')['parts']}
    added=[p['zip'] for p in r['parts'] if p['zip'] not in old]
    changed=[p['zip'] for p in r['parts'] if p['zip'] in old and p['sha256']!=old[p['zip']]['sha256']]
    assert added==['ThaiJP_Chapter14_P.zip'] and set(changed)=={'ThaiJP_Chapter1_11_12_P.zip','ThaiJP_Chapter2_P.zip'}
    write(Q+'release-verification.json',dict(source_sha256=sha,total_combined_text_records=48439,new_records=936,new_templates=897,previous47503_text_and_ACTOR_preserved=True,choice_groups_reviewed=3,proof_pages_viewed=11,changed_ZIPs=changed,new_ZIPs=added,parts=r['parts'],mount_verification=m,backup=r['backups'],protected_files_unchanged=True,installed=False,in_game_tested=False))
    root='E:/FF7RebrithModTH/FF7Rebrith/';backup=r['backups'].replace('\\','/');cov=read(Q+'coverage-review.json');deferred=read(Q+'deferred-remaining.json')
    block=f'''<!-- chapter14-current -->
## ล่าสุด: Ch.1–14 + Common — 25 ตุลาคม 2026

ผู้ใช้สั่ง Ch.14 แล้ว ส่วนนี้แทนสถานะ/hash/วิธีสร้างและคำว่างานต่อรอCh.14ด้านล่างทั้งหมด ซึ่งคงไว้เป็นประวัติ ฐานปัจจุบัน **48,439รหัส / 28assets / 730clusters** `{root}{cfg['source']}` SHA256 **{sha}**. ฐานCh.13หลังรีเช็ค **47,503รหัสและACTORทุกตัวคงเดิม** รวมคำแก้บริบท/สรรพนามก่อนหน้าและทีฟ่าCh.4**เข้ามาสิ**/Red**เชิญ**/ทีฟ่าCh.1**ถามสิ** ห้ามassembler/finalizerบทเก่าทับฐานล่าสุด

Ch.14 **End of the World** เพิ่ม **936รหัส / 897แม่แบบ**: MIDGR201 (ความฝัน/เดต/ทางเลือกทุกเส้นของZack), FOREE435 (ฉากจบ338+บทบอสทุกตัวละคร97), CAPIT300 (สคริปต์JPอีกฉบับของฉากท้าย). อ่านJP/USรหัสเดียวกันเมื่อมี/ไทยครบ897แม่แบบระหว่างแปลและทวนJP/ไทยครบอีกครั้ง รวมบทที่ไม่มีACTORอังกฤษและคำอุทานซ้ำหลายผู้พูด ตรวจความหมายชัดเจนก่อนใช้คำแปลร่วม. CAPITไม่มีคำแปลอังกฤษจริง USเป็นรหัสplaceholder จึงแปลจากJPและใช้ชื่อผู้พูดตามตัวตนJPกับทะเบียนsame-ID JP/USในcorpus **ไม่ใช้placeholderเป็นต้นฉบับ**. CAPITบางบรรทัดเป็นคำกำกับการแสดงในวงเล็บและสคริปต์ต่างจากFOREE แปลคงเนื้อหาและIDไว้ ไม่อ้างว่าทุกบรรทัดถูกเรียกในเกม

ปรับร่างใหม่5แม่แบบใน `{root}qa/chapter14/editorial-revisions.json`: ตัวเลข1เรื่อง, รสขนมที่**ระคายลิ้น**, รูฟัสมองรูปพ่อใช้**พ่อนี่มัน**แทนนาย, เอริธ**ถ้าบอกว่าไม่ไหวล่ะ?**, และประโยคแก้แค้นของBarret. เรื่องโลกหลายชั้น/ดวงดาว/คำอธิษฐานยึดJP ไม่แทนด้วยENที่ดัดแปลง. เซฟิรอธ**ฉันประเมินเธอต่ำไป**หมายถึงAerithที่ปรากฏร่วมสู้ ไม่ใช่Cloud; มีบริบทข้างเคียงและรายงานคำตอบNojimaประกอบในpronoun-review

อ่านตัวเลือกครบ **3ชุด / 11รหัส**: ของขวัญพร้อม3ชิ้น, ขนมพร้อม3ชนิด, ท่าถ่ายรูปทั้ง3แบบ พร้อมบทเชิญ/ปฏิเสธ/คำตอบในฉาก ไม่ใช้คำตอบดู/ไม่ดูกับกิจกรรมอื่น ชื่อitemในUIอังกฤษตามUSเดิม. อ่านUIข้างเคียง **43รหัส** รวมเป้าหมายCh.14/สรุป/การพักครั้งสุดท้าย/ออกเมนูหลังจบ/เลือกบทHARD/คุณสมบัติหลังจบ/เปลี่ยนชุด คงคำแปลฐานเดิม. นาย/เธอชุดใหม่43รหัสอ่านตามผู้ฟังจริง รวมCloud/Biggs/Sephiroth/RufusชายและAerithหญิง ไม่replaceรวม; ทำนายเป็นคำศัพท์

Inverse scanทั้งcorpusพบJPในC3410/C3510/CAPTL_BOS **{cov['Ch14_JP_origin_rows']}รหัส** มีคำแปลครบในทะเบียน (รวมUIเดิม). namespaceNPCมีJP **6,297รหัส** ไม่มีตกหล่นเชิงทะเบียน; regressionNPC8,347รหัส/ACTORผ่าน, UI6,907/choicefamily7,218/ชื่อท่าศัตรู1,703ผ่าน. JPที่ยังไม่ได้แปลทั้งหมด **{len(deferred['records'])}รหัส** แยกรายIDเป็นdemo/store/event-only UI ในdeferred-remaining ไม่เหลือบทพูดretailที่ยังไม่ได้จัดหมวดในcorpusนี้ **ไม่รับรองเล่นทุกสถานะหรือไม่มีข้อผิดพลาด100%**

คำลงท้ายรวม **{g['actual_particle_occurrences']}ครั้ง / {g['particle_bearing_records']}รหัส**: ครับ{g['counts']['ครับ']} / ค่ะ{g['counts']['ค่ะ']} / คะ{g['counts']['คะ']}; NPC/nonparty{g['npc_or_nonparty_occurrences']}ครั้ง ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ unknownใช้กลาง ไม่เดาเพศจากsuffix. AerithตอนปลุกCloudยังแสดง???ใช้ข้อยกเว้นexactIDจากการเปิดเผยตัวในฉาก; label???คงตามเกม. เรดวัยหนุ่มฉัน. ศัพท์และชื่อบทพูดไทยตามglossaryเดิม (Aerithเอริธ/Zackแซ็ก/Caitเค็ตชี/Barretบาร์เร็ต/Sephirothเซฟิรอธ/อู่ไถ/มาโก้/แมทีเรีย/เซทรา/เมเทโอ/รียูเนียน); ACTOR/UIอังกฤษตามUSหรือmappingJPที่มีหลักฐาน เลขปริมาณอารบิก

730clustersเดิมไม่เพิ่ม ฟอนต์16assetsเหมือนรุ่นก่อนทุกไบต์ metrics8fonts/ASCII/digit pixels/จุดไข่ปลาระดับล่างคงเดิม. เปิดดูproofใหม่ครบ **11หน้า**: 3ชุดตัวเลือกและ37ตัวอย่างบทพูดในLarge/Normal รวม80font samples +แผ่น8fonts. ภาพแสดงglyphจากไฟล์จริง แต่ตัดบรรทัดเป็นตัวอย่าง **ยังไม่ได้ติดตั้ง/ทดสอบในเกม หรือดูฟังวิดีโอทุกแขนง**

Final `{final.as_posix()}` มี **9ZIPล่าสุดแยกส่วน** เพิ่ม **ThaiJP_Chapter14_P.zip** สำหรับCAPITใหม่, อัปเดต **ThaiJP_Chapter1_11_12_P.zip** สำหรับMIDGRร่วม และ **ThaiJP_Chapter2_P.zip** สำหรับFOREEร่วม อีก6ZIPhashเดิมรวมCommon ไม่สร้างMIDGR/FOREEซ้ำในZIP14 ต้องใช้ชุดล่าสุดร่วมกัน อ่านกลับรวม9ZIP/27modfiles/28assetsผ่าน ไม่มีทับซ้อน ไม่มีรุ่นเก่าหรือsupportfilesในFinal สำรองเก่านอกFinal `{backup}`. Source/dist/เกมไม่เปลี่ยน

ไฟล์หลักใต้ `{root}`: `reference/chapter14-source.json`, `chapter14-templates.json`, `chapter14-scope.json`, `chapter14-build.json`, `chapter14-actor-labels.json`, `through-chapter14-cluster-map.json`; `translations/chapter14/batch-01.json`ถึง`batch-09.json`, `translations/chapter14-th.json`, `{cfg['source']}`. QA `qa/chapter14/`: baseline+revisionsimmutableห้ามprepareซ้ำ/รีเซ็ตindex; progress/review-records/editorial-revisions/same-scene-variant-reuse/actor-label-candidates; choice/pronoun/numeric/duplicate-context/adjoining-UI/coverage/deferred/NPC/gender; verification/old-glyph-regression/proof/visual-review/editorial-signoff/release-verification

สร้างซ้ำ: `tools/assemble_chapter14.py` → `tools/build_chapter14.py --text-only` (mapเดิม;เต็มเมื่อglyphใหม่) → `tools/build_chapter14.py --verify` → `tools/audit_chapter14.py` → `tools/audit_shared_dialogs.py` → `tools/audit_chapter14_glyphs.py` → `tools/chapter14_review.py` → `tools/preview_chapter14.py` → เปิดดูภาพจริงแล้วบันทึกvisual-reviewตามhash → `tools/signoff_chapter14.py` → `tools/publish_final_parts.py` → `tools/finalize_chapter14.py`. ห้ามprepareซ้ำ/เอาoverlayหรือassemblerเก่าท้ายสุดจนย้อนคำแก้. SourceCAPITใหม่ต้องมีownerแพ็กเฉพาะและunion28assets

งานต่อ: รอผู้ใช้เลือกรีเช็ค/ทดสอบในเกม/แก้ภาพที่พบ; **ยังไม่ติดตั้งโดยอัตโนมัติ**. ขอบเขตเนื้อเรื่องCh.1–14ในทะเบียนปัจจุบันแปลแล้ว แต่ยังต้องตรวจผลจริงทุกแขนง/พื้นที่กลับมา/กิจกรรมหากผู้ใช้รายงานหรือสั่งรีเช็คเพิ่ม ใช้ฐาน48,439ล่าสุดนี้เสมอ. Demo29รหัสพักตามขอบเขต ไม่เพิ่มโดยอัตโนมัติ

คลิปผู้ใช้สำหรับบท/เสียง/ผู้พูดและเพศ: https://www.youtube.com/watch?v=i4gD0mmj5vc ; https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU ; https://www.youtube.com/watch?v=bxrLsiU-QKk . Ch.14เพิ่มเติม https://www.youtube.com/watch?v=BIHjKH4c1BI ตรวจmetadata/ขอบเขต ไม่อ้างฟังครบ. ขอบเขตเทียบassetกับ https://www.powerpyx.com/final-fantasy-7-vii-rebirth-chapter-14-end-of-the-world-walkthrough/ และ https://gamers-high.com/ff7-rebirth/story/chapter14.html . ประโยคเซฟิรอธถึงเอริธมีคำอธิบายผู้เขียนบทที่รายงานใน https://www.frontlinejp.net/2024/04/17/final-fantasy-vii-rebirth-post-release-interview-part-2-devs-discuss-side-characters-dialogue-and-sequel/
<!-- /chapter14-current -->
'''
    paths=[W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'FINAL-PARTS.md',W/'CONTEXT-FULL-READ.md']+sorted(W.glob('CHAPTER*-STATUS.md'))
    for p in paths:
        t=p.read_text('utf8');t=re.sub(r'<!-- chapter14-current -->.*?<!-- /chapter14-current -->\s*','',t,flags=re.S);title,_,rest=t.partition('\n');p.write_text(title+'\n\n'+block+'\n'+rest.lstrip('\n'),encoding='utf8')
    parts='\n'.join(f"- [{p['zip']}](E:/FF7RebrithModTH/Mod/Final/{p['zip']}) — {p['bytes']:,} bytes; SHA256 `{p['sha256']}`" for p in r['parts'])
    (W/'CHAPTER14-STATUS.md').write_text('# Chapter14 — End of the World\n\n'+block+'\n## ZIPปัจจุบัน\n\n'+parts+'\n',encoding='utf8')
    print('Finalized Ch14:936 added,48439 total;2 updated ZIPs+1 new,9 mounted; HANDOFF current')

if __name__=='__main__':main()
