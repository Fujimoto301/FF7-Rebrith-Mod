"""Record the 18-line continuation against its own immutable release baseline."""
import re
from pathlib import Path
from prepare_chapter9 import W, read, write
from audit_chapter10 import digest
from chapter10_continue_review import Q, audit

def main():
    audit()
    rev=read(Q+'current.json'); snap=Path(rev['snapshot']); review=read(Q+'review.json')
    source_hash=review['source_sha256']; signoff=read('qa/chapter10/editorial-signoff.json')
    assert source_hash==signoff['source_sha256']==read('qa/chapter10/release-verification.json')['source_sha256']
    assert review['corrected_records']==18 and review['added_records']==0
    for p,h in signoff['reviewed_artifacts'].items(): assert digest(W/p)==h,p
    old={p['zip']:p for p in read(snap/'qa/final-parts/latest.json')['parts']}
    final=read('qa/final-parts/latest.json'); changed=[]; unchanged=[]
    for p in final['parts']:
        assert digest(W.parent/'Mod/Final'/p['zip'])==p['sha256']
        (unchanged if old[p['zip']]['sha256']==p['sha256'] else changed).append(p['zip'])
    assert changed==['ThaiJP_Chapter10_P.zip','ThaiJP_Common_P.zip'] and len(unchanged)==6
    mount=read('qa/final-parts/combined-mount-verification.json')
    assert mount['assets']==27 and mount['zip_count']==8 and mount['mod_files']==24 and not mount['overlapping_assets'] and mount['all_match_verified_combined_set']
    report=dict(source_sha256=source_hash,corrected_records=18,added_records=0,total_records=40691,
        updated_parts=changed,unchanged_parts=unchanged,zip_count=8,assets=27,
        source_actors_ids_and_glyph_map_preserved=True,all_archives_read_back=True,
        installed=False,in_game_tested=False,new_full_audio_review=False)
    write(Q+'release-verification.json',report)
    root='E:/FF7RebrithModTH/FF7Rebrith/'
    note=f'''<!-- chapter10-continue-current -->
## ล่าสุด: ตรวจความหมาย Ch.10 ต่อ — 20 ตุลาคม 2026

รอบต่อเนื่องนี้แก้ **18ข้อความที่มีอยู่แล้ว ไม่มีเพิ่ม/ลบID**: บทพูดอารมณ์/ประโยคเชื่อมของเอริธ, ตำนานที่แชดลี่ย์เล่า, ความอึดสู้ของบาร์เร็ต, ทิศทางเปรียบเทียบบาฮามุท, ช่องว่างชิปเอไอ, คอสตาเดลโซล, ลางบอกภัยพิบัติ และใช้ **โจโกโบะบิน** ให้ตรงบทสอนเดิมทั้งบทคุยกับข้อความช่วยเดินทาง คง **40,691ข้อความ / 27assets / 717clusters** ทุกID/ACTOR/glyph-mapเดิมครบ คำลงท้าย1,278ครั้ง(ครับ874/ค่ะ255/คะ149)ไม่เปลี่ยน ไม่เริ่มCh.11

อัปเดตเฉพาะ **ThaiJP_Chapter10_P.zip และ ThaiJP_Common_P.zip** ใน E:/FF7RebrithModTH/Mod/Final อีก6ZIPhashเดิม อ่านกลับ8ZIPรวม24modfiles/27assetsผ่านไม่มีซ้ำ ดูproofglyphจริง7หน้า56ตัวอย่างที่ครอบคลุม18ข้อความแก้และคำถาม/ทุกปุ่ม4ชุดแล้ว การตัดบรรทัดในproofเป็นตัวอย่าง ไม่ใช่ภาพเกม **ยังไม่ได้ติดตั้งหรือทดลองทุกแขนงในเกม/ฟังเสียงครบใหม่** จึงไม่รับรองว่าความหมายหรือruntimeไม่มีข้อผิดพลาด100%

หลักฐานใหม่: tools/chapter10_continue_review.py (prepareครั้งเดียว ห้ามซ้ำ), qa/chapter10/continue-review/current.json+revisions/ (ฐาน40,691ก่อนแก้), review.json (before/after18รหัส), release-verification.json และ [CHAPTER10-CONTINUE-REVIEW.md]({root}CHAPTER10-CONTINUE-REVIEW.md) ใช้ฐาน translations/working-through-chapter10-th.json และขั้นตอนbuild/audit/signoff/publishเดิม เพิ่ม gateต่อเนื่องอัตโนมัติในaudit_chapter10_recheck.py; signoffผูกhashรายงานใหม่ไว้แล้ว ปิดเอกสารด้วย finalize_chapter10_recheck.py แล้ว finalize_chapter10_continue.py

ยอดด้านล่าง **เพิ่ม144/แก้59** เทียบกับCh.10ชุดแรก40,547: 59คือข้อความที่มีอยู่ในชุดแรก ส่วนรอบต่อเนื่อง18ประกอบด้วย16ข้อความจากชุดแรกและ2ข้อความจาก144ที่เก็บตก ห้ามนับ18เป็นจำนวนข้อความเพิ่ม ฐานก่อนCh.10ทั้ง37,830ยังคงเดิม
<!-- /chapter10-continue-current -->

'''
    changes='\n'.join(f"| {r['template']} | {r['id']} | {r['decision']} |" for r in review['changes'])
    (W/'CHAPTER10-CONTINUE-REVIEW.md').write_text('# ตรวจต่อ Ch.10\n\n'+note+f'''## รายการแก้

before/afterฉบับเต็มพร้อมJP/USอยู่ที่ [review.json]({root}{Q}review.json)

| แม่แบบ | ID | เหตุผล |
| --- | --- | --- |
{changes}

คงผลตรวจครบหมวดเดิม: ตัวเลือก7,218รหัส, NPCพื้นที่ที่เยือน5,638รหัส(ไม่มีACTOR4,989), inventoryNPCเดิม8,347รหัส, ชื่อท่าอังกฤษ1,703ป้าย, source/stage40,691รหัสพร้อมtag/metadata, ทุก8ฟอนต์/nativeASCII/เลข/ไอคอนและellipsisระดับล่าง Residentญี่ปุ่นนอกหมวดปัจจุบัน1,234รหัสยังแยกเหตุผลรายIDใน qa/chapter10/recheck/Resident-residual-dispositions.json ตามเดิม ไม่มีการอ้างว่าญี่ปุ่นทุกประเภททั้งเกมหมดแล้ว

งานนี้อ่านเทียบJP/Thaiและอ้างUSรหัสเดียวกันเพื่อความหมายรายประโยคต่อจากรอบก่อน การสแกนไฟล์ครบทุกIDแยกจากการอ่านความหมายโดยมนุษย์ ไม่เท่ากับเล่นเกม/ฟังNPCครบทุกเงื่อนไข เอกสารขอบเขตบทภายหลังและลิงก์YouTubeเดิมยังอยู่ในHANDOFF/CHAPTER10-RECHECK-STATUS.md
''','utf-8')
    for path in [W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'CHAPTER10-STATUS.md',W/'CHAPTER10-RECHECK-STATUS.md',W/'FINAL-PARTS.md']:
        title,body=path.read_text('utf-8').split('\n',1)
        body=re.sub(r'<!-- chapter10-continue-current -->.*?<!-- /chapter10-continue-current -->\s*','',body,flags=re.S)
        path.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    print('Finalized18 corrections; only Chapter10/Common updated;8 current ZIPs verified')

if __name__=='__main__': main()
