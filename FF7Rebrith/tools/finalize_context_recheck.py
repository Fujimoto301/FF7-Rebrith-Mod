"""Verify the published context revision and update the handoff without rewriting history."""
import re
from pathlib import Path
from prepare_chapter9 import W,read,write
from context_recheck import Q,digest,decisions,audit

def main():
    audit();ctx=read('qa/active-working-set.json');rev=read(Q+'baseline.json');snap=Path(rev['snapshot']);parts=read('qa/final-parts/latest.json');before={p['zip']:p for p in read(snap/'qa/final-parts/latest.json')['parts']};sign=read('qa/chapter10/editorial-signoff.json');h=digest(W/ctx['combined_source'])
    assert sign['source_sha256']==h
    for p,d in sign['reviewed_artifacts'].items():assert digest(W/p)==d,p
    updated=[]
    for p in parts['parts']:
        assert digest(W.parent/'Mod/Final'/p['zip'])==p['sha256']
        if before[p['zip']]['sha256']!=p['sha256']:updated.append(p['zip'])
    assert len(updated)==8
    assert {p.name for p in (W.parent/'Mod/Final').iterdir()}==set(updated),'Keep only latest ZIP per part in Final'
    mount=read('qa/final-parts/combined-mount-verification.json')
    assert mount['zip_count']==8 and mount['mod_files']==24 and mount['assets']==27 and not mount['overlapping_assets'] and mount['all_match_verified_combined_set']
    result=dict(source_sha256=h,corrected_records=len(decisions()),total_records=40691,unchanged_records=40691-len(decisions()),changed_text_assets=10,all_fonts_actors_cluster_map_preserved=True,updated_parts=updated,all8_archives_read_back=True,combined27asset_mount_verified=True,installed=False,in_game_tested=False,full_manual_every_line_review=False)
    write(Q+'release-verification.json',result)
    root='E:/FF7RebrithModTH/FF7Rebrith/'
    note=f'''<!-- context-recheck-current -->
## ล่าสุด: ตรวจบริบทและตัวเลือก Ch.1–10 + Common — 21 ตุลาคม 2026

รอบนี้แก้ **368ข้อความเดิม ไม่มีเพิ่ม/ลบรหัส**: **143ข้อความด้านความหมาย/ตัวเลือกหรือคำเรียกร่วม** กับ **225ข้อความปรับศัพท์อย่างเดียว** ตรวจคำถามและทุกปุ่มหน้าฉากครบ **201กลุ่ม/777รหัส** เปลี่ยน **126รหัสใน62กลุ่ม** ให้ตอบกิจกรรมจริง เช่น ขึ้นเรือ/ยังไม่ขึ้น รายงาน/ยังไม่รายงาน ลองใหม่/ไม่ลอง รู้แล้ว/ยังไม่รู้; ใช้ตกลง/ยกเลิกเฉพาะคู่Wheelieที่แชร์ทั้งสมัครและรายงานระยะทาง แต่ละรหัสคงฝั่งตอบรับ/ปฏิเสธเดิม ไม่replaceはい/いいえแบบรวมทุกบริบท

แยกคำเชิญเข้าบ้านของพ่อแซ็ก Ch.9เป็น **เชิญเข้ามาสิ**; เก็บทีฟ่า Ch.4 **เข้ามาสิ**/RedXIII **เชิญ** และทีฟ่า Ch.1 **ถามสิ** เพราะคลาวด์ขอถามจริง แก้なんでも屋ที่หมายถึงคนจากร้านเป็นนักรับจ้าง คำถามหามงกุฎเป็นอนาคต คำตอบまあなตามความมั่นใจแต่ละฉาก คำตอบどうしたตามการเรียก/รอขึ้นเวที คำบอกล่วงหน้าของเซฟิรอธ และเรื่องเสียงผู้หญิงในคฤหาสน์เป็นเรื่องผี ปรับFortCondorโหมดHARDให้ตรงป้ายเดิม เหยื่อล่อไม่สื่อว่าต้องตกปลาด้วยเบ็ด ใช้โจโกโบะบินตรงบทสอนเดิม ศัพท์แมทีเรีย/มาโก้/ทีฟ่า/โจโกโบะ/อวาแลนช์/โซลเจอร์/โพชั่น/เซเว่นเฮฟเว่น/แซ็กเทียบต้นฉบับแยกรหัส ไม่แตะคำที่เพียงมีsubstringคล้ายกัน

ฐานยัง **translations/working-through-chapter10-th.json — 40,691รหัส / 27assets / 717clusters** sourceSHA256 **{h}** อีก **40,323ข้อความ** และACTORทั้งหมดเดิมครบ แก้10textassets ฟอนต์16assets/cluster-map/nativeASCII/ตัวเลขเดิมทุกไบต์ คำลงท้ายยัง1,278ครั้ง(ครับ874/ค่ะ255/คะ149) ไม่พบเพศสลับตามหลักฐานผู้พูดในauditเดิมที่carryต่อ NPC8347รหัส/UI6907รหัส/ชื่อท่าศัตรู1703รหัสยังผ่านregression

อัปเดต **ทั้ง8ZIP** ล่าสุดแยกส่วนใน E:/FF7RebrithModTH/Mod/Final แล้ว อ่านกลับ24modfiles/27assetsร่วมกันไม่มีซ้ำ สำรองรุ่นก่อนนอกFinal **ไม่ติดตั้งเกม** ไม่มีเริ่มบทพูดCh.11; ตัวเลือกบทภายหลังเป็นUIที่แปลไว้แล้วจึงตรวจร่วมด้วย

ขอบเขตหลักฐาน: คัดกรองโครงสร้าง/รหัส/ศัพท์/ตัวอักษรทั้ง40,691รหัส; อ่านเทียบตัวเลือกหน้าฉาก201กลุ่ม, sharedprompt candidates289รายการ(รวมplaceholderชื่อ????), คำสั้นซ้ำ348กลุ่มเปรียบเทียบJP/Thai/USvariants และเปิดบริบทข้างเคียงเฉพาะจุดเสี่ยง **ไม่ได้อ่านบทพูดทั้ง40,691รหัสซ้ำทุกบรรทัดหรือฟัง/เล่นทุกแขนง** จึงไม่รับรองความหมาย100% และไม่นับscriptผ่านเป็นตรวจบริบททุกบรรทัด หลักฐานนี้แยกไว้ชัดเจนในqa/context-recheck/corpus-screen.json, choice-semantic-review.json, short-dialogue-review.json, shared-prompt-review.json ดูproofglyphจริง **21หน้า/84panels/168font samples** แล้ว การตัดบรรทัดเป็นตัวอย่าง ไม่ใช่ภาพเกม

ไฟล์แก้ authoritative **reference/context-recheck-overrides.json** เก็บJP/US/ก่อน/หลัง/เหตุผลต่อasset+ID ส่วน **qa/context-recheck/baseline.json+revisions/** เป็นsnapshotก่อนรอบนี้ ห้ามprepareซ้ำ/แก้snapshot อัปเดตpatchchapter*-thที่มีรหัสนั้นแล้ว แต่แม่แบบเก่ายังคงเป็นประวัติ **assemble_chapter10.pyใช้context_recheck.overlayท้ายสุด** ห้ามเอาแม่แบบ/reuseคำสั้นเก่าทับoverride บทถัดไปต้องใช้ฐานล่าสุดและcarryoverrideนี้ พร้อมตรวจคำถามทุกปุ่ม/ประโยคก่อนหลัง ห้ามแชร์คำสั้นเพียงเพราะJPเหมือนกัน

ขั้นตอนสร้างซ้ำ: assemble_chapter10 → build_chapter10 --text-only/--verify → chapter10_recheck --quality → audit_shared_dialogs → context_recheck --review-ledger → audit_chapter10_glyphs → preview_chapter10 + chapter4_door_fix --preview + chapter4_choice_fix --preview + context_recheck_preview/ดูภาพที่เปลี่ยน → บันทึกvisual-reviewผูกhashจริง → signoff_chapter10 → publish_final_parts → finalize_context_recheck ไม่ใช้finalizerประวัติบทเก่าทับบริบทใหม่ รายงานละเอียด [CONTEXT-RECHECK.md]({root}CONTEXT-RECHECK.md)
<!-- /context-recheck-current -->

'''
    (W/'CONTEXT-RECHECK.md').write_text('# ตรวจบริบทบทพูดและตัวเลือก\n\n'+note,'utf-8')
    paths=[W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'FINAL-PARTS.md']+list(W.glob('CHAPTER*-STATUS.md'))
    for path in paths:
        title,body=path.read_text('utf-8').split('\n',1);body=re.sub(r'<!-- context-recheck-current -->.*?<!-- /context-recheck-current -->\s*','',body,flags=re.S);path.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    print('Finalized368 corrections, all8 latest ZIPs verified, handoff updated; no installation')
if __name__=='__main__':main()
