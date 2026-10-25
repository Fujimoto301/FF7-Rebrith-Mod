"""Bind the second-read release and retain exact historical evidence."""
import re
from pathlib import Path
from prepare_chapter9 import W,read,write
from audit_chapter12 import digest
from chapter12_recheck import Q,audit

def main():
    from finalize_chapter12 import main as finalize_base
    finalize_base();audit()
    sha=digest(W/'translations/working-through-chapter12-th.json');r=read('qa/final-parts/latest.json');m=read('qa/final-parts/combined-mount-verification.json');b=read(Q+'baseline.json');s=read('qa/chapter12/editorial-signoff.json');cov=read(Q+'coverage-review.json');choice=read(Q+'choice-review.json');a=read(Q+'audit.json')
    assert sha==s['source_sha256']==cov['source_sha256']==choice['source_sha256']==a['source_sha256']
    for p,h in s['reviewed_artifacts'].items():assert digest(W/p)==h,p
    before=read(Path(b['snapshot'])/'qa/final-parts/latest.json');by={p['zip']:p for p in before['parts']};changed=[p['zip'] for p in r['parts'] if p['sha256']!=by[p['zip']]['sha256']]
    changed_assets={str(Path(x['asset'])).replace('\\','/') for x in read('reference/chapter12-recheck-overrides.json')['records']}
    expected_changed={p['zip'] for p in r['parts'] if any(rel.replace('\\','/') in changed_assets for rel in p['assets'])}
    assert set(changed)==expected_changed and len(changed)==8
    result=dict(source_sha256=sha,reviewed_templates=3847,corrected_records=56,other46594_text_records_and_all_ACTOR_preserved=True,total_combined_text_records=46650,complete_choice_groups_reviewed=36,choice_changes_this_pass=0,all16_font_assets_byte_identical=True,parts=r['parts'],changed_ZIPs=changed,mount_verification=m,backup=r['backups'],protected_files_unchanged=True,installed=False,in_game_tested=False)
    write(Q+'release-verification.json',result)
    backup=r['backups'].replace('\\','/');root='E:/FF7RebrithModTH/FF7Rebrith/'
    block=f'''<!-- chapter12-recheck-current -->
## ล่าสุด: อ่านรีเช็ค Ch.12 ครบชุด — 25 ตุลาคม 2026

ฐานใหม่ **46,650รหัส / 27assets / 730clusters** `{root}translations/working-through-chapter12-th.json` SHA256 **{sha}** ส่วนนี้แทนสถานะ/hashของCh.12รุ่นแรกด้านล่าง ฐานCh.1–11เดิมและคำแก้สรรพนาม45รหัสคงอยู่ ห้ามใช้ assembler/finalizerเก่าทับ

อ่านเทียบJP/ไทยซ้ำครบ **3,847แม่แบบ / 4,200รหัส** รวมทุกเดต/LOVELESS/เควส11งาน/โปรโตเรลิก/Queen’s Blood/บทกลับพื้นที่เดิม/NPCไม่มีACTOR/Commonคำอธิบายศัตรู อ่านคำถามพร้อมทุกปุ่มและบริบทคำตอบ **36ชุด** อีกครั้ง ตัวเลือกทั้งหมดคงเดิมในรอบนี้ รวม7คำแก้UIจากรุ่นแรก บริบทซ้ำยึดIDและผู้พูดเดิม ไม่ถือscriptผ่านเป็นการอ่านความหมาย

แก้เพิ่ม **56รหัส** (55รายการจากการอ่านรอบแรกของรีเช็ค+1รายการระบุBillyกับน้องสาวให้ชัด): Redเดินให้ช้าลงตามทุกคน ไม่ใช่เดินให้ทัน; เดตแรกBarretเป็นสวนสนุกคนละแห่ง ไม่ใช่ที่นี่; ElmyraพูดถึงการดูแลAerith ไม่ได้เรียกAerithเป็นผู้ฟัง; 足音คือเสียงฝีเท้า; ผมหน้าม้าสองจุดไม่ใช่ฉันหน้าม้า; ล็อกผลแข่ง/วัยที่เหมาะจะฟังความจริง/หัวหน้าแผนกปกป้องลูกน้อง; อารมณ์มอนสเตอร์; ชื่อRogue StanceตรงUSactionID; สะกดศัตรู/แคคเตอร์ให้ตรงศัพท์เดิม และปรับคำตก/ภาษาแข็ง/ผู้กระเด็นจากโพรงให้ชัด คำอธิบายกับก่อน/หลังรายIDอยู่ `{root}reference/chapter12-recheck-overrides.json` อีก46,594textและACTORเดิมทุกตัวคงเดิม ไม่มีเพิ่มบทพูดCh.13 ไม่มีIDเพิ่ม/ลบ

หลักฐาน `{root}qa/chapter12/recheck/`: baseline.json+revisionsเป็นsnapshotimmutableก่อนรีเช็ค ห้ามprepareหรือเขียนทับ; progressอ่านครบค้าง0, audit, choice-review, coverage-review, proof7หน้า56panels, visual-review, release-verification. ตรวจinverse source: C32ข้ามasset1,315รหัส, namespaceNPC6,292รหัส, บทเดินJP-only36รหัส และEnemy Intelคำอธิบาย/คำแนะนำ544รหัส ไม่มีJPตกหล่นในทะเบียนเหล่านี้ ไม่ใช่รับรองเล่นทุกแขนงในเกม

ตรวจอ่านกลับtext/metadata27assets ผ่านUIเดิม6907/ตัวเลือกfamily7218/NPCที่เคยเก็บ8347/ชื่อท่า1703 ฟอนต์16ไฟล์กับmap730ตรงรุ่นCh.12ก่อนรีเช็คทุกไบต์ คงellipsis/เลข/อังกฤษ/คำลงท้าย1750ครั้ง (ครับ1261/ค่ะ323/คะ166; NPC1401) เปิดดูproofใหม่7หน้าครบ56คำแก้และmainหน้า13ที่เปลี่ยน ส่วนmainอีก15หน้าสร้างใหม่แล้วhashตรงภาพที่เคยดูจึงreuseหลักฐานอย่างชัดเจน ภาพglyphstageตัดบรรทัดเป็นตัวอย่าง **ยังไม่ได้ทดสอบในเกมหรือดูฟังวิดีโอครบทุกแขนง**

Finalมี **8ZIPล่าสุดแยกส่วน** ชื่อเดิมของCh.12รุ่นแรก อัปเดตครบทั้ง8ZIPตามassetที่แก้ รวม `ThaiJP_Chapter2_P.zip` ซึ่งมีคำแก้FOREE อ่านรวม8ZIP/24modfiles/27assetsผ่านไม่มีซ้ำ สำรองรุ่นก่อนอยู่นอกFinal `{backup}` ไม่ติดตั้ง/ไม่เปลี่ยนsource/dist/เกม ใช้ทั้ง8ZIPrุ่นปัจจุบันร่วมกัน

สร้างซ้ำ: `tools/assemble_chapter12.py` → `tools/build_chapter12.py --text-only`/`--verify` → `tools/audit_shared_dialogs.py` (รวมrecheckgate) → `tools/preview_chapter12.py` + `tools/chapter12_recheck.py --preview` → เปิดดูภาพที่เปลี่ยนหรือreuseเฉพาะhashตรง → บันทึกvisual-review → `tools/signoff_chapter12.py` → `tools/publish_final_parts.py` → **`tools/finalize_chapter12_recheck.py`** ไม่รันmigration `chapter12_editorial.py`/`chapter12_recheck_fixes.py`ซ้ำ ต้องcarry56คำแก้นี้จากฐาน46,650ปัจจุบันเมื่อเริ่มบทใหม่

งานต่อรอคำสั่งCh.13 หลักJPก่อนUS/คำลงท้ายตามเพศ/unknownใช้กลาง/Cloudนายคุณ/เอริธแซ็กเค็ตชี/ตัวเลือกทุกปุ่ม/YouTubeและpathในส่วนCh.12ด้านล่างยังใช้ ไม่มีอ้างว่าอ่านCh.1–11ทุกบรรทัดใหม่ในรอบนี้;ตรวจถดถอยและคงฐานที่รีเช็คไว้แล้ว
<!-- /chapter12-recheck-current -->
'''
    paths=[W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'FINAL-PARTS.md',W/'CONTEXT-FULL-READ.md']+sorted(W.glob('CHAPTER*-STATUS.md'))
    for p in paths:
        t=p.read_text('utf8');t=re.sub(r'<!-- chapter12-recheck-current -->.*?<!-- /chapter12-recheck-current -->\s*','',t,flags=re.S);title,_,rest=t.partition('\n');p.write_text(title+'\n\n'+block+'\n'+rest.lstrip('\n'),encoding='utf8')
    (W/'CHAPTER12-RECHECK-STATUS.md').write_text('# Chapter12 — second complete source review\n\n'+block,encoding='utf8')
    print('Finalized Ch12 recheck:56 corrections;36 choice groups;8 updated ZIPs,8 mounted; HANDOFF current')
if __name__=='__main__':main()
