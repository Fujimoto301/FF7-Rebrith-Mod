"""Verify the published recheck and record the current source of truth."""
import re
from pathlib import Path
from prepare_chapter9 import W,read,write
from audit_chapter11 import digest
from assemble_ui_completion import fingerprint

def main():
    q='qa/chapter11/';rq=q+'recheck/'
    cfg=read('reference/chapter11-build.json');sha=digest(W/cfg['source'])
    audit=read(q+'translation-audit.json');review=read(rq+'review.json');sign=read(q+'editorial-signoff.json')
    baseline=read(rq+'baseline.json');snap=Path(baseline['snapshot'])
    release=read('qa/final-parts/latest.json');mount=read('qa/final-parts/combined-mount-verification.json')
    assert sha==audit['source_sha256']==review['source_sha256']==sign['source_sha256']
    for rel,h in sign['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    assert audit['previous40691_preserved_except_reviewed_Ch11_UI'] and audit['reviewed_existing_Ch11_UI_changes']==3
    assert review['previous42394_preserved_except49_reviewed_revisions']
    assert review['corrected_records']==49 and review['added_UI_records']==56
    assert fingerprint()==baseline['protected']==read(q+'baseline.json')['protected']
    assert mount['zip_count']==8 and mount['assets']==27 and mount['mod_files']==24
    assert mount['all_match_verified_combined_set'] and not mount['overlapping_assets']
    final=W.parent/'Mod/Final'
    assert {p['zip'] for p in release['parts']}=={p.name for p in final.glob('*.zip')}
    for p in release['parts']:assert digest(final/p['zip'])==p['sha256']
    old=read(snap/'qa/final-parts/latest.json');oldparts={p['zip']:p for p in old['parts']}
    changed=[p['zip'] for p in release['parts'] if p['sha256']!=oldparts[p['zip']]['sha256']]
    assert set(changed)=={'ThaiJP_Chapter1_11_P.zip','ThaiJP_Common_P.zip'}
    current=read(q+'working-assets.json');previous=read(snap/baseline['active']['manifest'])
    fonts={a:h for a,h in current.items() if 'SystemFont' in a}
    assert len(fonts)==16 and all(previous[a]==h for a,h in fonts.items())
    assert digest(W/cfg['cluster_map'])==digest(snap/baseline['active']['cluster_map'])
    result=dict(source_sha256=sha,parts=release['parts'],mount_verification=mount,
        corrected_records=49,added_UI_records=56,total_combined_text_records=42450,
        previous40691_preserved_except3_reviewed_Ch11_UI=True,
        previous42394_preserved_except49_reviewed_revisions=True,all_ACTOR_preserved=True,
        font_files_byte_unchanged_from_original_Ch11=True,cluster_map_unchanged=True,
        protected_files_unchanged=True,changed_ZIPs=changed,unchanged_ZIPs=6,
        original_release_source_sha256=digest(snap/baseline['active']['combined_source']),
        backup=release['backups'],installed=False,in_game_tested=False)
    write(rq+'release-verification.json',result);write(q+'release-verification.json',result)
    backup=release['backups'].replace('\\','/')
    block=f'''<!-- chapter11-recheck-current -->
## ฐานล่าสุด: รีเช็คเก็บตก Ch.11 — 24 ตุลาคม 2026

ส่วนนี้แทนยอดและขั้นตอน Chapter11 เดิมด้านล่าง ปัจจุบัน **42,450รหัส / 27assets / 721clusters** SHA256 **{sha}** ฐาน `E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter11-th.json` แพ็กแก้แล้วใน `E:/FF7RebrithModTH/Mod/Final` ห้ามรัน finalizer/assembler ของบทเก่าทับฐานนี้

อ่านเทียบJP/ไทยครบ1,658แม่แบบเดิม/1,703รหัส รวมNPCและบรรทัดไม่มีACTOR ตรวจแม่แบบใช้ซ้ำ28กลุ่มพร้อมทุกID และคำถาม12กลุ่ม47รหัสพร้อมทุกปุ่ม/บริบทตอบรับ ตรวจ C31 ข้ามassetครบ659รหัส แก้ **49รหัสเดิม** (รวมตัวเลือกCh.11ที่เคยแปลเป็นUIไว้3รหัส) และเก็บเพิ่ม **Enemy Intel UI56รหัสของ28คู่คำอธิบาย/คำแนะนำ** ใน Common รวมCh.11ใหม่จากฐานCh.10เป็น1,759รหัส/1,714แม่แบบ ไม่มีบทพูดCh.12เพิ่ม ไม่ใช่คำรับรองว่าคำอธิบายศัตรูทั้งเกมครบแล้ว

จุดแก้สำคัญ: Cloudถามถึงความช่วยเหลือในอดีต; BarretถามAerithละนาย; เพลงยุฟฟี่สลับผู้ไล่ตาม; 嗜好品ไม่เจาะจงว่าเป็นเครื่องดื่ม; Chadleyกล่าวถึงงานวิจัยของตัวเอง; คำเรียกหัวหน้าครัว/ราชินีโลหิตดำ; ผู้พูดไม่ชัดใช้กลาง ตัวเลือกคุยTifaเป็นก็เคยอยู่/อย่ามาล้อกันสิ และบทRedเป็นไม่ต้องใส่ใจหรอก โดยคงฝั่งตอบรับเดิม ยึดJPก่อนUS (เช่นเงื่อนไขPyretailและSwan Song) ชื่อUI/ท่าใช้officialEnglishตามenemy/actionIDจริง

หลักฐานแก้: `reference/chapter11-recheck-overrides.json`49รหัสก่อน/หลัง/เหตุผล; เพิ่มUI `reference/chapter11-recheck-source.json`56รหัสกับ `translations/chapter11-recheck-lines.json` ทะเบียนเริ่ม46รหัสถูกเก็บimmutableที่ `qa/chapter11/recheck/inventory-revisions/initial46.json` แล้วappend10 ห้ามprepareซ้ำ ตรวจ `qa/chapter11/recheck/progress.json`, `review.json`, `choice-semantic-review.json`, `duplicate-context-review.json`, `enemy-intel-scope.json`, `release-verification.json` และ [CHAPTER11-RECHECK-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER11-RECHECK-STATUS.md)

ACTORทั้งหมดเดิมตรงเดิม ฐาน42,394ก่อนรีเช็คคงเดิมยกเว้น49รหัสที่มีเหตุผล; ฐานCh.10จำนวน40,691คงเดิมยกเว้นตัวเลือกCh.11จำนวน3รหัสที่อนุมัติบริบทในรอบนี้ ไม่เขียนว่าทั้ง40,691ข้อความคงเดิมอีก คำลงท้ายยัง1548ครั้งใน1509รหัส (ครับ1084/ค่ะ308/คะ156; NPC1257) ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ ผู้พูดไม่ชัดใช้กลาง Cloudนาย/คุณ กลุ่มพวกนาย/พวกคุณ คงเอริธ/แซ็ก/เค็ตชี/เรดวัยหนุ่มฉัน และทีฟ่าCh.4เข้ามาสิ/Redเชิญ

ตรวจอ่านกลับtext/metadataครบ27assets ผ่านUIเดิม6907, ตัวเลือกfamily7218, NPCเดิม8347 และชื่อท่าอังกฤษ1703 เลขต่าง12รายการมีคำตัดสินแล้ว ไม่มีกlyphใหม่ในรอบรีเช็ค: cluster-map721และไฟล์font16ไฟล์ byteตรงรุ่นCh.11ก่อนรีเช็ค ดูภาพจริงครบmain12หน้า96samplesและrecheck14หน้า105panels (ทุก49รหัสแก้+56เพิ่ม) ใช้glyphจากstageจริง การตัดบรรทัดเป็นตัวอย่าง ไม่ใช่ภาพเกม ไม่อ้างฟังเสียงหรือเล่นทุกแขนง

Finalมี8ZIPล่าสุด แทน **ThaiJP_Chapter1_11_P.zip** กับ **ThaiJP_Common_P.zip** อีก6ZIPhashเดิม อ่านกลับ8ZIP/24modfiles/27assetsรวมกันผ่านไม่ซ้ำ สำรองรุ่นก่อนนอกFinal: `{backup}` ไม่ติดตั้งเกม protected source/dist/game hashคงเดิม

สร้างซ้ำ: `tools/assemble_chapter11.py` → `tools/build_chapter11.py --text-only` (เมื่อmapเดิม)/`--verify` → `tools/audit_shared_dialogs.py` → mainและrecheckpreview → ดูภาพจริง/บันทึกvisual-reviewสองชุด → `tools/signoff_chapter11.py` → `tools/publish_final_parts.py` → **`tools/finalize_chapter11_recheck.py`** (แทนfinalize_chapter11เก่า) คงmapและsnapshotเดิม ไม่prepareใหม่ คำแก้49ต้องcarryหลังcontext-recheck/context-full-readเดิมในบทต่อไป โดยใช้ฐาน42,450นี้ ไม่applyoverlayเก่าทับค่าล่าสุด

Ch.12ยังไม่เริ่มบทพูด: NIBLEญี่ปุ่น272รหัส (C3210 128 + NIBLE_QST03/Lament144) คงพักจนผู้ใช้สั่ง ต้องตรวจNPC/ไม่มีACTOR/ตัวเลือกทุกปุ่ม/กิจกรรมพื้นที่เดิมตามปลดล็อกเสมอ แหล่งวิดีโอเดิม: [คลิปผู้ใช้](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์ญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk) รอบนี้ไม่ได้ดูฟังครบใหม่
<!-- /chapter11-recheck-current -->
'''
    paths=[W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'FINAL-PARTS.md',W/'CONTEXT-FULL-READ.md']+sorted(W.glob('CHAPTER*-STATUS.md'))
    for path in paths:
        t=path.read_text('utf8');t=re.sub(r'<!-- chapter11-recheck-current -->.*?<!-- /chapter11-recheck-current -->\s*','',t,flags=re.S)
        title,_,rest=t.partition('\n');path.write_text(title+'\n\n'+block+'\n'+rest.lstrip('\n'),encoding='utf8')
    parts='\n'.join(f"- [{p['zip']}](E:/FF7RebrithModTH/Mod/Final/{p['zip']}) — {p['bytes']:,} bytes; SHA256 `{p['sha256']}`" for p in release['parts'])
    (W/'CHAPTER11-RECHECK-STATUS.md').write_text('# Chapter 11 — รีเช็คเก็บตก\n\n'+block+'\n## ZIPล่าสุด\n\n'+parts+'\n',encoding='utf8')
    print('Verified current release; updated HANDOFF and status files.49 corrections +56 recovered UI. No installation.')

if __name__=='__main__':main()
