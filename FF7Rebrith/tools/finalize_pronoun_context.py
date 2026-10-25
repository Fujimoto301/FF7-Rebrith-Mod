"""Verify current split archives and publish the pronoun-review handoff."""
import re
from pathlib import Path
from prepare_chapter9 import W,read,write
from audit_chapter11 import digest
from assemble_ui_completion import fingerprint
from pronoun_context import Q,OV

def main():
    b=read(Q+'baseline.json');ctx=read('qa/active-working-set.json');sha=digest(W/ctx['combined_source'])
    a=read(Q+'audit.json');s=read('qa/chapter11/editorial-signoff.json');r=read('qa/final-parts/latest.json');m=read('qa/final-parts/combined-mount-verification.json')
    assert sha==a['source_sha256']==s['source_sha256'] and a['reviewed_records']==499 and a['corrected_records']==45
    for p,h in s['reviewed_artifacts'].items():assert digest(W/p)==h,p
    assert fingerprint()==b['protected']
    assert m['zip_count']==8 and m['mod_files']==24 and m['assets']==27 and not m['overlapping_assets'] and m['all_match_verified_combined_set']
    final=W.parent/'Mod/Final';assert {p.name for p in final.glob('*.zip')}=={p['zip'] for p in r['parts']}
    for p in r['parts']:assert digest(final/p['zip'])==p['sha256']
    old=read(Path(b['snapshot'])/'qa/final-parts/latest.json');by={p['zip']:p for p in old['parts']}
    changed=[p['zip'] for p in r['parts'] if p['sha256']!=by[p['zip']]['sha256']]
    assert len(changed)==8
    result=dict(source_sha256=sha,reviewed_candidate_records=499,corrected_records=45,kept_records=454,
        lexical_only_records=a['lexical_only_records'],total_combined_text_records=42450,parts=r['parts'],mount_verification=m,
        changed_ZIPs=changed,backup=r['backups'],all_other_text_ACTOR_tags_numbers_fonts_map_preserved=True,
        protected_files_unchanged=True,installed=False,in_game_tested=False)
    write(Q+'release-verification.json',result);write('qa/chapter11/release-verification.json',result)
    backup=r['backups'].replace('\\','/')
    block=f'''<!-- pronoun-context-current -->
## ฐานล่าสุด: ตรวจบริบท “นาย / เธอ” ครบชุดที่แปลไว้ — 24 ตุลาคม 2026

ส่วนนี้แทนยอดhashและขั้นตอนรุ่นก่อนด้านล่าง ฐานปัจจุบัน **42,450รหัส / 27assets / 721clusters** ที่ `E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter11-th.json` SHA256 **{sha}** ไม่มีเพิ่ม/ลบรหัส ไม่มีเริ่มบทพูดCh.12

ผู้ใช้สั่งตรวจบริบทของนายและเธอทั้งหมด อ่านJP/USรหัสเดียวกัน/ไทย/ผู้พูดครบ **499รหัส** จากทุกassetในชุดที่แปลไว้ (Ch.1–11 + Common รวมUIบทหลังที่มีอยู่แล้ว) ก่อนแก้มีนาย334ครั้ง/เธอ178ครั้ง นับsubstringจึงรวมคำที่ไม่ใช่สรรพนามด้วย แยกคำศัพท์อย่างนายกเทศมนตรี/นายแบบ/นายพราน/เจ้านาย/ทำนาย/อีเธอร์/บราเธอร์ออกจากการตัดสินสรรพนาม ชุดที่เป็นคำศัพท์ล้วน{a['lexical_only_records']}รหัส เก็บไว้ตามเดิม

แก้/ปรับ **45รหัส** อีก454รหัสคงเดิม ไม่ใช่45กรณีเพศผิดทั้งหมด: มีทั้งคำเรียกCloud/Barretผิด, การเลือกคำกลางเมื่อผู้ฟังไม่ชัด, ความสุภาพ และแก้กำกวมแม่ของนายจ้าง อ่านบริบทข้างเคียงจริงในจุดกำกวม ไม่ใช้replaceทั้งเกม ไม่เดาเพศNPCจากsuffix และไม่สมมติว่าคู่รักทุกคู่ต้องชายหญิง

ตัวอย่าง: Regina/Hojo/Fran/Naomi/นักสะสมการ์ดเรียกCloudนายหรือคุณตามบริบท; ทีฟ่าพูดถึงลูกนกชอบBarretใช้**ดูจะถูกใจนายแล้วนะ**; คำรับรองกิจกรรมที่ไม่ได้ระบุผู้รับเป็นชายใช้คุณ; กลุ่มผู้ชักชวนงานใช้พวกคุณ; Gusชี้ทีละคนในกลุ่มผสมใช้คนนี้; บทคู่สนทนาที่ไม่ระบุตัวใช้คุณหรือละสรรพนาม Cloudวัยหนุ่มคุยกับวีรบุรุษSephirothใช้คุณ ส่วนBarretพูดกับTobyใช้**แม่ของนายเป็นคนจ้าง / ให้พวกเรามาเป็นบอดี้การ์ดโคฮาดะ** แยกจากความหมายแม่ของนายจ้าง

คงเธอเมื่อพูดกับ/กล่าวถึงตัวละครหญิง, คนรักหญิงที่มีบริบท, เพลงทั่วไป, การสมมติให้สัตว์/มาสคอตเป็นคู่สนทนา เช่น CloudคุยกับYuffie, BarretฝากเงินกับClaire, MadamMตรวจมือTifa, เนื้อเพลงยุฟฟี่; MadamMที่SaucerคงเธอเพราะประโยคJPถัดไประบุ**彼女** ไม่เปลี่ยนเป็นชายเพราะมีCloudอยู่ในฉาก ถ้าเรียกCloudโดยตรงใช้นาย/คุณ กลุ่มรวมCloudใช้พวกนาย/พวกคุณตามน้ำเสียง

หลักฐาน: `qa/pronoun-context/queue.json`499รหัสJP/US/ไทยเดิม, `decisions.json`คำตัดสินทุกID, `progress.json`อ่านครบ/ค้าง0, `audit.json`, `proof.json`, `visual-review.json`, `unchanged-proof-reuse.json`, `release-verification.json`; คำแก้พร้อมก่อน/หลัง/เหตุผล45รหัสอยู่ **`reference/pronoun-context-overrides.json`**; snapshotเดิมอยู่ `qa/pronoun-context/baseline.json` + `revisions/` ห้ามprepareซ้ำ บทถัดไปต้องcarryคำแก้ชุดนี้หลังcontext-recheck/context-full-read/chapter11-recheckเดิมทุกชุด ใช้ฐาน42,450ล่าสุด ห้ามประกอบบทเก่าทับหรือoverlayค่ารุ่นเก่าท้ายสุด

ตรวจอ่านกลับทุกtext/metadataทั้ง27assets ผ่านUIเดิม6907/ตัวเลือกfamily7218/NPCเดิม8347/ชื่อท่าอังกฤษ1703 คงID/ACTOR/tags/เลข/คำลงท้ายทั้งหมด ฟอนต์16ไฟล์และcluster-map byteตรงรุ่นก่อน ตรวจภาพใหม่6หน้า45panelsจากglyphNormalจริงครบ ส่วนmain12และrecheck14หน้าสร้างใหม่แล้วPNGตรงทุกไบต์กับภาพที่เคยดูจริง จึงreuseหลักฐาน26หน้าอย่างชัดเจน ไม่มีอ้างดูภาพที่เปลี่ยนโดยไม่เปิดดู ภาพตัดบรรทัดเป็นตัวอย่าง ไม่ใช่การเล่น/ฟังทุกแขนงในเกม

Finalมีเฉพาะ **8ZIPล่าสุด** แก้ทั้ง8แพ็กตามassetsที่เกี่ยวข้อง แยกZIPส่วนเดิม อ่านกลับรวม8ZIP/24modfiles/27assetsผ่านไม่มีซ้ำ สำรองรุ่นก่อนนอกFinalที่ `{backup}` ไม่ติดตั้ง/ไม่เปลี่ยนต้นฉบับ เกม หรือdist

สร้างซ้ำ: `tools/assemble_chapter11.py` → `tools/build_chapter11.py --text-only`/`--verify` → `tools/audit_shared_dialogs.py` (รวมpronounauditใหม่และgateเดิม) → previewบท11/recheck/pronoun → ดูภาพใหม่หรือยืนยันreuseเฉพาะภาพเดิมbyteตรง → บันทึกvisual-review → `tools/signoff_chapter11.py` → `tools/publish_final_parts.py` → **`tools/finalize_pronoun_context.py`** แทนfinalizerเก่าที่ผูกยอดก่อนมี45คำแก้นี้ ไม่เปลี่ยนsnapshotประวัติเพื่อให้auditผ่าน

คู่มือคำลงท้าย/ศัพท์และคลิปYouTubeในส่วนก่อนยังใช้ต่อ: ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ ผู้พูดไม่ชัดใช้กลาง ไม่บังคับเติมทุกบรรทัด ยอดคำลงท้าย1548ครั้งคงเดิม คงเอริธ/แซ็ก/เค็ตชี/เรดวัยหนุ่มฉัน และทีฟ่าCh.4เข้ามาสิ/Redเชิญ รอบนี้ไม่ได้ดูฟังวิดีโอครบใหม่
<!-- /pronoun-context-current -->
'''
    paths=[W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'FINAL-PARTS.md',W/'CONTEXT-FULL-READ.md']+sorted(W.glob('CHAPTER*-STATUS.md'))
    for p in paths:
        t=p.read_text('utf8');t=re.sub(r'<!-- pronoun-context-current -->.*?<!-- /pronoun-context-current -->\s*','',t,flags=re.S)
        title,_,rest=t.partition('\n');p.write_text(title+'\n\n'+block+'\n'+rest.lstrip('\n'),encoding='utf8')
    parts='\n'.join(f"- [{p['zip']}](E:/FF7RebrithModTH/Mod/Final/{p['zip']}) — {p['bytes']:,} bytes; SHA256 `{p['sha256']}`" for p in r['parts'])
    (W/'PRONOUN-CONTEXT-REVIEW.md').write_text('# ตรวจบริบทนายและเธอ\n\n'+block+'\n## ZIPปัจจุบัน\n\n'+parts+'\n',encoding='utf8')
    print('Finalized499 reviewed records /45 corrections; all8 latest ZIPs verified; HANDOFF updated.')

if __name__=='__main__':main()
