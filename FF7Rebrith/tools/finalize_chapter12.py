"""Verify the published Ch12 release and write the current handoff."""
import re
from prepare_chapter9 import W,read,write
from audit_chapter12 import CFG,Q,digest
from assemble_ui_completion import fingerprint

def main():
    cfg=read(CFG);sha=digest(W/cfg['source']);a=read(Q+'translation-audit.json');s=read(Q+'editorial-signoff.json');r=read('qa/final-parts/latest.json');m=read('qa/final-parts/combined-mount-verification.json');b=read(Q+'baseline.json');g=read(Q+'gender/summary.json')
    assert sha==a['source_sha256']==s['source_sha256'] and a['new_records']==4200
    for rel,h in s['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    assert fingerprint()==b['protected']
    assert m['zip_count']==8 and m['mod_files']==24 and m['assets']==27 and m['all_match_verified_combined_set'] and not m['overlapping_assets']
    assert r['chapters']==list(range(1,13)) and r['working_manifest']==Q+'working-assets.json' and r['combined_text_records']==46650
    final=W.parent/'Mod/Final';assert {p.name for p in final.glob('*.zip')}=={p['zip'] for p in r['parts']}
    for p in r['parts']:assert digest(final/p['zip'])==p['sha256']
    result=dict(source_sha256=sha,total_combined_text_records=46650,new_records=4200,new_templates=3847,previous42450_preserved_except7_exact_choice_UI_changes=True,all_previous_ACTOR_preserved=True,choice_groups_reviewed=36,proof_pages_viewed=16,parts=r['parts'],mount_verification=m,backup=r['backups'],protected_files_unchanged=True,installed=False,in_game_tested=False)
    write(Q+'release-verification.json',result)
    root='E:/FF7RebrithModTH/FF7Rebrith/';backup=r['backups'].replace('\\','/')
    block=f'''<!-- chapter12-current -->
## ฐานปัจจุบัน Ch.1–12 + Common — 25 ตุลาคม 2026

ส่วนนี้แทนสถานะ/hash/วิธีสร้างรุ่นก่อนด้านล่าง ซึ่งเก็บไว้เป็นประวัติ ตอนนี้แปล Ch.12 แล้ว ฐาน **46,650รหัส / 27assets / 730clusters**: `{root}{cfg['source']}` SHA256 **{sha}** ห้ามใช้ assembler/finalizer บทเก่าทับฐานนี้

Ch.12เพิ่ม **4,200รหัส / 3,847แม่แบบ**: C3210/C3220/C3230ข้ามassetครบ1,278รหัส รวมZackและเดตทั้ง6แบบ/LOVELESSทุกRosa/ก่อนออกเรือ;11เควสที่ปลดล็อกในCh.12;โปรโตเรลิกช่วงสุดท้าย/Gilgamesh;Queen’s Bloodตอนจบ;บทกลับพื้นที่เดิม/ภาพถ่าย/เปียโน/สมบัติโจรสลัด เก็บบทเดินGrasslandsที่มีเฉพาะJP36รหัสและNPCNibelในResident122รหัสด้วย เพิ่มคำอธิบาย/คำแนะนำEnemy Intel UIที่เหลือ488รหัสตามขอบเขตUIทั้งเกมที่ผู้ใช้อนุญาต ไม่ได้เริ่มบทพูดCh.13–14

อ่านJPทุกแม่แบบระหว่างแปล ใช้USรหัสเดียวกันเป็นข้อมูลบริบท/ชื่อทางการ ตรวจคำถามพร้อมทุกตัวเลือกและบทตอบ **36ชุด** ปรับคำถามหัวหน้าแผนกShinra6รหัสกับตัวเลือกCissnei1รหัส มีbefore/after/เหตุผลใน `{root}reference/chapter12-context-overrides.json` ฐาน42,450เดิมคงtextทุกตัวนอก7รหัสนี้ และACTORเดิมคงทุกตัว รวมคำแก้บริบท/สรรพนาม45รหัสของรุ่นก่อน ห้ามapplyoverlayเก่าท้ายสุดจนย้อนคำแก้ใหม่

รีเช็คชื่อพูดเอริธ/แซ็ก/เค็ตชี/บาร์เร็ต/เฉิง/รู้ด/อวาแลนช์/มาโก้/แมทีเรียตามglossary คงทีฟ่าCh.4**เข้ามาสิ**/Red**เชิญ**/ทีฟ่าCh.1**ถามสิ**; Cloudใช้**นาย/คุณ**ตามน้ำเสียง กลุ่มรวมCloudใช้พวกนาย/พวกคุณ; เธอใช้เมื่อหมายถึงหญิง/เพลง/บริบทที่เหมาะสม แยกนายกเทศมนตรี/ทำนาย/เจ้านายออกจากสรรพนาม ตรวจชุดใหม่146รหัสที่มีนายหรือเธอ แก้主人2จุดเป็นเจ้านาย ไม่replaceสรรพนามทั้งเกม

คำลงท้ายรวม **{g['actual_particle_occurrences']}ครั้ง / {g['particle_bearing_records']}รหัส**: ครับ{g['counts']['ครับ']} / ค่ะ{g['counts']['ค่ะ']} / คะ{g['counts']['คะ']}; NPC/nonparty{g['npc_or_nonparty_occurrences']}ครั้ง ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ ผู้พูดไม่ชัดใช้กลาง ไม่เดาเพศจากsuffix ไม่บังคับเติมคำลงท้ายทุกประโยค Redวัยหนุ่มใช้ฉัน ชื่อUI/ACTOR/ศัตรู/ท่าอังกฤษตามUSรหัสเดียวกันและenemy/actionIDจริง (JPชื่อท่าซ้ำกันอาจมีอังกฤษต่างกัน เช่นのしかかり/みがまえる ต้องดูศัตรู)

ไฟล์ทำงาน: `{root}reference/chapter12-source.json`, `reference/chapter12-templates.json`, `reference/chapter12-scope.json`, `translations/chapter12/batch-01.json`ถึง`batch-33.json`, `translations/chapter12-th.json`, `reference/through-chapter12-cluster-map.json`, `reference/chapter12-build.json` (ทุกrelativepathในประโยคนี้อยู่ใต้ `{root}`). snapshotฐานCh.11immutableอยู่ `{root}qa/chapter12/baseline.json`และ`revisions/` **ห้ามprepareซ้ำ**

หลักฐาน `{root}qa/chapter12/`: progress/translation-audit/review-records, choice-review36ชุด, pronoun-review, numeric-decisions46รหัส(45แม่แบบ), gender, NPC-residual, old-glyph-regression, proof16หน้า, visual-review, editorial-signoff, release-verification. อ่านกลับทุกtext/metadata27assets ตรวจUIเดิม6907/ตัวเลือกfamily7218/NPCที่เคยเก็บ8347/ชื่อท่า1703ผ่าน;ทะเบียนรหัสที่มี `_NPC_` ไม่มีJPตกหล่นใน27assets แต่ไม่ได้รับรองการเล่นทุกเหตุการณ์ในเกม ฟอนต์ใหม่9clusters คง721assignments/metricsเดิมทั้ง8fontsและจุด…ระดับล่าง ตรวจภาพจริงครบ16หน้าจากglyphstage การตัดบรรทัด/เลือกfontในภาพเป็นตัวอย่าง **ยังไม่ได้ทดสอบในเกมหรือดูฟังวิดีโอทุกแขนง**

Finalเก็บเฉพาะ **8ZIPล่าสุด แยกส่วน**: `ThaiJP_Chapter1_11_12_P.zip`แทน1_11เดิม, `ThaiJP_Chapter8_12_P.zip`แทนChapter8เดิม; Chapter2 / Chapter3_4_5 / Chapter6_7 / Chapter9 / Chapter10 / Commonชื่อเดิมแต่เป็นเนื้อหารุ่นล่าสุด ต้องใช้ทั้ง8ส่วนร่วมกัน เพราะCh.12กลับหลายพื้นที่และassetsแชร์กัน อ่านกลับรวม8ZIP/24modfiles/27assetsผ่านไม่มีซ้ำ สำรองZIPก่อนหน้าอยู่นอกFinal `{backup}` ไม่ติดตั้งและไม่เปลี่ยนsource/dist/เกม

สร้างซ้ำตามลำดับ: `tools/assemble_chapter12.py` → `tools/build_chapter12.py` (เต็มเมื่อglyphใหม่, `--text-only`เมื่อmap/fontคงเดิม) → `tools/build_chapter12.py --verify` → `tools/audit_shared_dialogs.py` → `tools/audit_chapter12_glyphs.py` → `tools/preview_chapter12.py` → เปิดดูภาพที่เปลี่ยนและบันทึกvisual-reviewตามhashจริง → `tools/signoff_chapter12.py` → `tools/publish_final_parts.py` → `tools/finalize_chapter12.py` ไม่รัน `chapter12_editorial.py`ซ้ำเพราะเป็นmigrationของร่างก่อนแก้

งานต่อ: รอผู้ใช้สั่งCh.13ก่อนเพิ่มบทพูด C3310/C3320/C3330/C3340/C3410/C3510และTemple/Capitalbosses;ทุกบทใหม่ตรวจNPCไม่มีACTOR/บทใช้ซ้ำ/คำถาม+ทุกปุ่ม+บทตอบ/ชื่อเควส+HUD/คำแจ้งเตือน+ท่าศัตรู/นายเธอ+คำลงท้าย/ตัวเลข+tags+ฟอนต์ด้วย ฐานใหม่ต้องcarry46,650นี้และใช้append-onlyscope/snapshot ไม่รีเซ็ตทะเบียนเก่า

คลิปเดิมสำหรับเทียบบท/เสียง/ผู้พูดและเพศ (ไม่ใช่หลักฐานว่าเปิดดูครบในรอบนี้): https://www.youtube.com/watch?v=i4gD0mmj5vc ; https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU ; https://www.youtube.com/watch?v=bxrLsiU-QKk ; เพิ่มรายการEN Ch.12 https://www.youtube.com/watch?v=0zxhzIW2VbA (ตรวจmetadataเท่านั้น) ขอบเขตเควส/แขนงเทียบcorpusและ walkthroughในreference/chapter12-scope.json
<!-- /chapter12-current -->
'''
    paths=[W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'FINAL-PARTS.md',W/'CONTEXT-FULL-READ.md']+sorted(W.glob('CHAPTER*-STATUS.md'))
    for p in paths:
        t=p.read_text('utf-8');t=re.sub(r'<!-- chapter12-current -->.*?<!-- /chapter12-current -->\s*','',t,flags=re.S);title,_,rest=t.partition('\n');p.write_text(title+'\n\n'+block+'\n'+rest.lstrip('\n'),encoding='utf-8')
    parts='\n'.join(f"- [{p['zip']}](E:/FF7RebrithModTH/Mod/Final/{p['zip']}) — {p['bytes']:,} bytes; SHA256 `{p['sha256']}`" for p in r['parts'])
    (W/'CHAPTER12-STATUS.md').write_text('# Chapter12 — A Golden Key\n\n'+block+'\n## ZIPปัจจุบัน\n\n'+parts+'\n',encoding='utf-8')
    print('Finalized Ch12 /4200 added IDs /46650 combined;8 ZIPs mounted; HANDOFF updated')
if __name__=='__main__':main()
