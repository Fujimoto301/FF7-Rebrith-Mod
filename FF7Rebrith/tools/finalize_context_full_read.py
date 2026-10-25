"""Document verified editorial scope separately from unperformed runtime tests."""
from pathlib import Path
import hashlib,json,re
from prepare_chapter9 import W,read,write

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ctx=read('qa/active-working-set.json');sha=digest(W/ctx['combined_source'])
    audit=read('qa/context-full-read/audit.json');latest=read('qa/final-parts/latest.json')
    sign=read('qa/chapter10/editorial-signoff.json')
    assert sha==audit['source_sha256']==sign['source_sha256']
    for p,h in sign['reviewed_artifacts'].items():assert digest(W/p)==h,p
    assert len(latest['parts'])==8
    final=W.parent/'Mod'/'Final'
    assert {p.name for p in final.glob('*.zip')}=={p['zip'] for p in latest['parts']}
    for p in latest['parts']:assert digest(final/p['zip'])==p['sha256']
    write('qa/context-full-read/release-verification.json',dict(source_sha256=sha,corrected_records=audit['corrected_records'],reviewed_records_at_release=audit['reviewed_records'],remaining_records_at_release=audit['remaining_records'],full_editorial_read_complete=audit['full_editorial_read_complete'],parts=latest['parts'],all_eight_zip_hashes_verified=True,independent_readback_all_assets=True,in_game_tested=False,backups=latest['backups']))
    proof=read('qa/context-full-read/proof.json')
    visual=read('qa/context-full-read/visual-review.json')
    visual_note='ดูครบทุกหน้าแล้ว' if visual['all_pages_viewed'] else 'ตรวจครบทุกpanel โดยดูภาพใหม่/ที่เปลี่ยนในcontact sheetsจริง และเทียบRGBกับmetadataตรงทุกจุดสำหรับpanelเดิมที่เคยดูแล้ว ดูvisual-review.jsonกับpanel-visual-reuse.json'
    # The new read may refine an ID already changed in the earlier 368-ID pass.
    # Count distinct source IDs rather than adding two overlapping ledgers.
    prior_keys={(r['asset'],r['id']) for r in read('reference/context-recheck-overrides.json')['records']}
    full_keys={(r['asset'],r['id']) for r in read('reference/context-full-read-overrides.json')['records']}
    context_total=len(prior_keys|full_keys)
    progress=read('qa/context-full-read/progress.json')
    reviewed={i for r in progress['read_ranges'] for i in range(r['start'],r['end_exclusive'])}
    queue=read('qa/context-full-read/queue.json')
    pending=[r for r in queue if r['index'] not in reviewed]
    remaining_scope='ป้ายภาษาอังกฤษและสัญลักษณ์' if pending and all(r['queue']=='13-English-UI-notation' for r in pending) else 'NPC/เควสต์/Common/ป้ายภาษาอังกฤษตามช่วงที่ยังไม่อ่าน'
    common_note='อ่านข้อความไทยในคิวบทหลัก Ch.1–10, NPC/เควสต์ในชุดแปล และ Common ครบแล้ว แต่ยังไม่ใช่การทดสอบทุกแขนงในเกม' if pending and all(r['queue']=='13-English-UI-notation' for r in pending) else 'ต้องอ่านต่อในช่วงที่ยังไม่อยู่ในread_ranges'
    complete=audit['full_editorial_read_complete'] and not pending
    heading='ตรวจครบชุดข้อความ Ch.1–10 + Common ที่แปลไว้แล้ว' if complete else 'กำลังอ่านเทียบบริบททุกข้อความ Ch.1–10 + Common'
    completion_note=('**รีเช็คชุดข้อความปัจจุบันครบแล้ว 40,691 รหัส คิวค้าง 0 รหัส** บทหลัก Ch.1–10 จำนวน7,543รหัส รวมบทหลัก/NPC/เควสต์/Commonภาษาไทย32,841รหัสอ่านเทียบ JP/ไทย ส่วนป้ายอังกฤษและสัญลักษณ์7,850รหัสตรวจ JP/USรหัสเดียวกัน เปิดอ่านความต่าง495รายการและcandidateนอกหมวดชื่อ1,049รายการ รวมเงื่อนไขGambitและคำอธิบายที่ตกไป จัดคำตัดสินรายรหัสในenglish-completion-review.json ไม่อ้างว่า7,355ชื่อที่ตรงUSเป็นการอ่านบทพูดไทยใหม่ และไม่ใช่การเล่น/ฟังทุกแขนงในเกม' if complete else '**งานนี้ยังไม่จบทั้งหมด** รวมอ่านแล้ว {:,} รหัสจาก40,691 เหลือ {:,} รหัสในคิว{}ที่ต้องอ่านต่อ {}'.format(audit['reviewed_records'],audit['remaining_records'],remaining_scope,common_note))
    next_note='คิวชุดนี้ตรวจครบแล้ว งานต่อไปต้องตั้งขอบเขตบทใหม่โดยcarryoverrideทั้งสองชุดและgateเดิม ไม่เริ่มบทพูดCh.11หรือเนื้อหาที่พักไว้เอง' if complete else 'อ่านต่อจากรหัสแรกที่ยังไม่อยู่ในread_rangesของprogress ต้องrecordเฉพาะช่วงที่อ่านจริงและดูpendingรายการแยก'
    block='''<!-- context-full-read-current -->
## {heading} — 23 ตุลาคม 2026

{completion_note} คำถามตรวจพร้อมทุกปุ่มและบทตอบรับเมื่อมีบริบทให้เทียบ ไม่ถือผลscriptผ่านเป็นการอ่านความหมายทุกบรรทัด

รอบอ่านละเอียดแก้เพิ่ม **{fixed} รหัส** จากรอบคัดกรองเดิม368รหัส รวมรอบบริบทสองชุด **{total} รหัส** ตัวอย่าง: ภาวะโดนพิษมาโก้, เซทรา, ห้องโดยสารชั้น2, หัวหน้าหน่วยพาเหรด, การขายโรงแรม, คำปฏิเสธ/คำพูดหยอกของเอริธ, สรรพนามเรด, ชื่อยุฟฟี่/มีน่า/บรอนโก และประโยคตาม JP เมื่อ US ดัดแปลงต่างกัน คงทีฟ่า Ch.4 **เข้ามาสิ** และ Red **เชิญ** ตามที่แก้แล้ว

ฐานล่าสุด `{source}` SHA256 **{sha}** ยังคง40,691รหัส/27assets/717clusters คงID/ACTOR/tag/เลขliteral/ฟอนต์และcluster-mapเดิม ผ่านอ่านกลับstageและ **8 ZIP /24 modfiles /27assets** รวมกันไม่มีซ้ำ ใน **E:/FF7RebrithModTH/Mod/Final** แต่ละส่วนมีเฉพาะZIPล่าสุด สำรองนอกFinal ไม่ติดตั้งเกม ไม่อ้างฟัง/เล่นทุกแขนง Proofแก้เพิ่ม{pages}หน้า{panels}panels{samples}font samples {visual_note}

หลักฐานใหม่ `reference/context-full-read-overrides.json`, `qa/context-full-read/queue.json`, `progress.json`, `corrections.json`, `audit.json`, `proof.json`, `visual-review.json`, `release-verification.json` และ checkpointผูกsourceใน `qa/context-full-read/releases/` คิวกับbaselineเป็นsnapshotห้ามprepareซ้ำ {next_note} ห้ามเขียนว่าทดสอบครบทุกแขนงจากยอดการตรวจรอบนี้

ใช้ `tools/context_full_read.py --show START END` อ่านจริง → `--record START END NOTES` เฉพาะช่วงที่อ่าน → เพิ่มก่อน/หลัง/เหตุผลรายIDลงcorrections → `--commit-reviewed` → assemble/build/verify/audit/proof/signoff/publishตามgateปัจจุบัน Overlayใหม่อยู่หลังcontext_recheckเดิม ต้องcarryทั้งสองชุดในบทถัดไป ห้ามรันfinalize_context_recheckเก่าที่hardcodeยอด368ทับรายงานล่าสุด

ข้อสังเกต: คำเชิญเข้าบ้านแซ็กในรอบก่อนเป็นactor zam (แม่แซ็ก) จึงไม่ใช้คำระบุว่าพ่อแซ็กเป็นหลักฐานเพศ ผู้พูดไม่ชัดใช้กลางตามเดิม ดูรายละเอียด [CONTEXT-FULL-READ.md](E:/FF7RebrithModTH/FF7Rebrith/CONTEXT-FULL-READ.md)
<!-- /context-full-read-current -->'''.format(read=audit['reviewed_records'],left=audit['remaining_records'],fixed=audit['corrected_records'],total=context_total,source=ctx['combined_source'],sha=sha,pages=proof['pages'],panels=proof['panels'],samples=len(proof['samples']),visual_note=visual_note,remaining_scope=remaining_scope,common_note=common_note,heading=heading,completion_note=completion_note,next_note=next_note)
    targets=[W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'FINAL-PARTS.md',W/'CONTEXT-RECHECK.md']+list(W.glob('CHAPTER*-STATUS.md'))
    for p in targets:
        if not p.exists():continue
        s=p.read_text('utf-8')
        s=re.sub(r'\n?<!-- context-full-read-current -->.*?<!-- /context-full-read-current -->\n?', '',s,flags=re.S)
        pos=s.find('\n')+1;s=s[:pos]+'\n'+block+'\n'+s[pos:]
        p.write_text(s,encoding='utf-8')
    (W/'CONTEXT-FULL-READ.md').write_text('# อ่านเทียบบริบท Ch.1–10 + Common ทุกข้อความ\n\n'+block+'\n',encoding='utf-8')
    print('Documented editorial release:',audit['corrected_records'],'corrections;',audit['remaining_records'],'records remain unchecked; runtime untested')

if __name__=='__main__':main()
