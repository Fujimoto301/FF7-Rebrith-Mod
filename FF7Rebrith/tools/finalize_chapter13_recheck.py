"""Finalize the exact second-release audit and current handoff."""
import re
from pathlib import Path
from prepare_chapter9 import W,read,write
from audit_chapter13 import CFG,digest
from chapter13_recheck import Q,audit

def main():
    from finalize_chapter13 import main as finalize_base
    finalize_base();audit()
    cfg=read(CFG);sha=digest(W/cfg['source']);r=read('qa/final-parts/latest.json');m=read('qa/final-parts/combined-mount-verification.json');b=read(Q+'baseline.json');s=read('qa/chapter13/editorial-signoff.json')
    assert s['source_sha256']==sha
    for p,h in s['reviewed_artifacts'].items():assert digest(W/p)==h,p
    before={p['zip']:p for p in read(Path(b['snapshot'])/'qa/final-parts/latest.json')['parts']}
    changed=[p['zip'] for p in r['parts'] if before[p['zip']]['sha256']!=p['sha256']];assert changed==['ThaiJP_Chapter2_P.zip']
    write(Q+'release-verification.json',dict(source_sha256=sha,total_combined_text_records=47503,reviewed_templates=809,corrected_records=11,other47492_text_records_and_all_ACTOR_preserved=True,all16_font_assets_byte_identical=True,choice_groups_reread=2,parts=r['parts'],changed_ZIPs=changed,mount_verification=m,backup=r['backups'],installed=False,in_game_tested=False))
    root='E:/FF7RebrithModTH/FF7Rebrith/';backup=r['backups'].replace('\\','/')
    block=f'''<!-- chapter13-recheck-current -->
## ล่าสุด: รีเช็ค Ch.13 ครบชุด — 25 ตุลาคม 2026

ฐานปัจจุบัน **47,503รหัส / 27assets / 730clusters** `{root}{cfg['source']}` SHA256 **{sha}** ส่วนนี้แทนสถานะ/hashของCh.13รุ่นแรกด้านล่าง ฐานCh.1–12เดิม46,650และACTORทุกตัวคงเดิม ห้ามassembler/finalizerบทเก่าทับ

อ่านเทียบJP/ไทยครบ **809แม่แบบ / 853รหัส** ใหม่อีกรอบ รวมการเดินทาง/วิหารทั้งสองกลุ่ม/ฉากทดสอบ/NPCไม่มีACTOR/ภาพผนัง/บทบอสและบทช่างภาพ ทวนคำถามพร้อมทุกปุ่ม **2ชุด / 6รหัส** และบริบทบรรทัดข้างเคียง ตัวเลือกคงเดิม แก้ **11แม่แบบ / 11รหัส**: ถามเอริธว่า**เรียกเธออยู่เหรอ?** ไม่ทำให้สับสนผู้เรียก; 1หมัดสามจุด/เติร์กส์1คน/โลก1ใบใช้เลขอารบิก; **ยังเชื่อมถึงกันอยู่** ไม่สมมติเพิ่มว่าต้องเป็นทางกายภาพ; **ยกดวงดาวให้**ตรง譲る; เรด**เสียดายที่ไม่ได้ขอโทษ**เป็นอดีตพลาดโอกาส; ปรับคำเอาคืนระหว่างต่อสู้ และระบุ**พวกเราไม่มีที่ให้หนี**ขณะกำแพงDemon Gateบีบเข้ามา

คำแก้before/after/JP/เหตุผลแต่ละIDอยู่ `{root}reference/chapter13-recheck-overrides.json` อัปเดตbatchต้นทาง+patch+combinedแล้ว อีก **47,492text** และACTORทุกตัวคงเดิม ไม่มีเพิ่ม/ลบID ไม่เริ่มCh.14 คำลงท้ายยัง **1,814ครั้ง** (ครับ1276/ค่ะ349/คะ189; NPC1439) ไม่มีสลับเพศในทะเบียน; ชุดนาย/เธอใหม่13รหัสรวมทีฟ่าเรียกเอริธใช้เธอ ถูกผู้ฟังจริง ไม่replaceทั้งเกม

QA `{root}qa/chapter13/recheck/`: baseline+revisionsimmutableก่อนรีเช็ค(ห้ามprepareซ้ำ/เขียนทับ), progressอ่าน809ค้าง0, audit, proof2หน้า11คำแก้, visual-review และrelease-verification. ตรวจภาพ2หน้าใหม่ครบแล้ว mainproof11หน้าสร้างใหม่hashตรงภาพที่เคยดูทั้งหมดจึงreuseหลักฐานโดยบันทึกชัดเจนในvisual-reviewหลัก ไม่ได้อ้างเปิดดู11หน้าใหม่ซ้ำ ฟอนต์16assets/map730ตรงรุ่นก่อนทุกไบต์ ตรวจเลข9รายการ/JP C33+TEMPL857รหัส/NPC6297รหัส/ตัวเลือก7218/UI6907/NPCregression8347/ชื่อท่า1703ผ่าน UIข้างเคียง239รหัสคงเดิมและตรวจโครงสร้างต่อจากการอ่านครั้งก่อน

Finalที่ `E:/FF7RebrithModTH/Mod/Final` มี **8ZIPล่าสุดแยกส่วน** อัปเดตเฉพาะ **ThaiJP_Chapter2_P.zip** เพราะFOREEใช้ร่วมCh.2/Ch.13 อีก7ZIPรวมCommonhashเดิม อ่านรวม8ZIP/24modfiles/27assetsผ่าน ไม่มีassetทับซ้อน สำรองZIPก่อนนอกFinal `{backup}` source/dist/เกมไม่เปลี่ยน **ยังไม่ได้ติดตั้งหรือทดสอบในเกม/ฟังวิดีโอทุกแขนง**

สร้างซ้ำตามpipelineCh.13ด้านล่าง โดยเพิ่ม `tools/chapter13_recheck.py` gateอัตโนมัติในshared audit และ `--preview`สำหรับคำแก้11รหัส; mainpreviewใช้ภาพเดิมได้เฉพาะhashตรงหลักฐานที่เคยดู ต้องดูrecheckproofที่เปลี่ยนก่อนsignoff/publish ปิดด้วย **`tools/finalize_chapter13_recheck.py`** แทนfinalize13เดี่ยวๆ บทถัดไปcarryฐาน47,503ปัจจุบันพร้อม11คำแก้นี้ ห้ามประกอบจากbatchรุ่นก่อน งานต่อรอผู้ใช้สั่งCh.14; กฎJPก่อนUS/ศัพท์/เพศ/ตัวเลือกทุกปุ่ม/YouTubeและpathในส่วนCh.13ด้านล่างยังใช้
<!-- /chapter13-recheck-current -->
'''
    paths=[W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'FINAL-PARTS.md',W/'CONTEXT-FULL-READ.md']+sorted(W.glob('CHAPTER*-STATUS.md'))
    for p in paths:
        t=p.read_text('utf8');t=re.sub(r'<!-- chapter13-recheck-current -->.*?<!-- /chapter13-recheck-current -->\s*','',t,flags=re.S);title,_,rest=t.partition('\n');p.write_text(title+'\n\n'+block+'\n'+rest.lstrip('\n'),encoding='utf8')
    (W/'CHAPTER13-RECHECK-STATUS.md').write_text('# Chapter13 — complete source recheck\n\n'+block,encoding='utf8')
    print('Finalized Ch13 recheck:11 corrections;2 choice groups;1 updated ZIP,8 mounted; HANDOFF current')
if __name__=='__main__':main()
