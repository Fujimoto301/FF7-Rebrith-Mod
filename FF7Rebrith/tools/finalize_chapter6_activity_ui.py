"""Supplement the current Ch.6 handoff with the verified activity-UI revision."""
import hashlib
from assemble_chapter6 import W,read,write
from chapter6_activity_ui import ROOT
from assemble_ui_completion import fingerprint

def finish():
    baseline=read(ROOT+'/baseline.json');audit=read(ROOT+'/audit.json')
    release=read('qa/final-parts/latest.json');mounted=read('qa/final-parts/combined-mount-verification.json')
    old=read(baseline['snapshot']+'/qa/final-parts/latest.json')
    before={p['zip']:p for p in old['parts']};current={p['zip']:p for p in release['parts']}
    assert release['combined_text_records']==audit['combined_text_records']==23811
    assert set(before)==set(current) and len(current)==5
    changed=[k for k in current if current[k]['sha256']!=before[k]['sha256']]
    assert changed==['ThaiJP_Common_P.zip'],changed
    for k,p in current.items():
        assert hashlib.sha256((W.parent/'Mod/Final'/k).read_bytes()).hexdigest()==p['sha256']
    assert mounted['assets']==23 and mounted['zip_count']==5 and mounted['mod_files']==15
    assert mounted['all_match_verified_combined_set'] and not mounted['overlapping_assets']
    assert fingerprint()==baseline['protected']
    gender=read('qa/gender-through-chapter6/summary.json')
    assert gender['actual_particle_occurrences']==477 and not gender['gender_mismatches']
    proof=read(ROOT+'/proof.json');assert len(proof['samples'])==24
    result=dict(new_UI_records=131,all_Costa_UI_records=153,total_text_records=23811,
      prior_23680_translation_records_and_ACTORs_preserved=True,unchanged_all_fonts_and_textures=True,
      unchanged_all_scene_ZIPs=True,only_updated_ZIP=changed[0],ZIP_count=5,assets=23,
      all_parts_mounted_and_read_back=True,no_overlapping_assets=True,source_and_installed_files_unchanged=True,
      proof_pages_visually_inspected=['proof-1.png','proof-2.png','proof-3.png'],
      proof_uses_staged_glyphs=True,proof_is_not_in_game=True,in_game_tested=False,
      full_new_video_audio_review=False,installed=False,release_manifest='qa/final-parts/latest.json',
      previous_ZIP_backup=release['backups'])
    write(ROOT+'/release-verification.json',result)
    overall=read('qa/chapter6/release-verification.json');overall.update(activity_UI_revision=result)
    write('qa/chapter6/release-verification.json',overall)
    note='''<!-- costa-activity-ui-current -->
## อัปเดตล่าสุด: เก็บ UI กิจกรรม Ch.6 เพิ่มเติม

18 ตุลาคม 2026: เพิ่ม **131 รหัส UI** จากรายการตรวจ **164 รหัส** ของกิจกรรม Costa del Sol คงข้อความอังกฤษ/ตัวเลข/สัญลักษณ์เดิมอีก33รหัส รวม UI Ch.6 **153รหัส** และชุดทั้งหมด **23,811รหัส / 23assets / 674clusters** บท/ตัวเลือกCh.6ยังเป็น1,698รหัส รวมNPC698รหัส ไม่ได้เพิ่มบทพูดหรือเริ่มCh.7

ครอบคลุม HUD/ปุ่ม/คะแนน/รางวัลของ Pirate's Rampage, Run Wild และ Wheelie, เมนู Card Carnival และปริศนาช่วงเริ่มต้น01–03ทั้งเวอร์ชันงานเทศกาล/หลังงาน รวมกล้อง แผนที่ ตั๋วกิจกรรมและคำบรรยายชุดชายหาด6ชุด ชื่อโหมดใช้ Free-For-All / Time Trial และชื่อโจทย์/ใบอนุญาตเป็นอังกฤษทางการตามUSรหัสเดียวกัน การ์ด Moogle Mage/Moogle Bard ใช้ชื่ออังกฤษแทนชื่อJP2号/3号โดยบันทึกข้อยกเว้นไว้ ไม่อ้างว่าปริศนาระดับหลังกลับเมือง11ขึ้นไปหรือGold Saucerเสร็จแล้ว

ตรวจ corpus ตามหมวดที่เลือกครบ แท็ก/ตัวแปรJPและค่าตัวเลขคงเดิม รักษาคำแปล23,680รหัสและACTORก่อนหน้าทุกจุด ฟอนต์/texture/scene assetsเดิมทั้งหมดไม่เปลี่ยน คำลงท้ายจริง477ครั้งยังผ่านผลตรวจเดิม ไม่เพิ่มคำระบุเพศในUI ภาพproof3หน้าใช้glyphจากstaging ตรวจภาพแล้ว แต่ไม่ได้ทดสอบการตัดบรรทัดในเกมจริง

รอบเก็บตกนี้อัปเดตเฉพาะ **ThaiJP_Common_P.zip** ใน `E:/FF7RebrithModTH/Mod/Final` ZIPบททั้ง4คงเดิมและยังต้องใช้ทั้ง5ส่วนร่วมกัน อ่านกลับทั้ง5ZIPรวม23assetsผ่าน ไม่มีassetทับกัน สำรองCommonรุ่นเก่านอกFinal ไม่ได้ติดตั้งลงเกม

ไฟล์ใต้ฐาน `E:/FF7RebrithModTH/FF7Rebrith/`:

| หน้าที่ | พาธ |
| --- | --- |
| JP/USและรายการครบตามหมวด/สิ่งที่กันไว้ | reference/chapter6-activity-ui-source.json, chapter6-activity-ui-scope.json |
| คำแปล129ข้อความญี่ปุ่น/อักษรเต็มความกว้าง + ชื่อโหมดอังกฤษ2รหัส | translations/chapter6-activity-ui-th.json |
| สคริปต์คำแปล/สร้างชุดรวม | tools/chapter6_activity_ui.py, assemble_chapter6.py |
| ตรวจเก็บตก/ภาพตัวอย่าง | tools/audit_chapter6_activity_ui.py, preview_chapter6_activity_ui.py |
| QA/หลักฐาน/ผลแพ็ก | qa/chapter6/activity-ui/audit.json, proof.json, proof-1.png ถึง proof-3.png, release-verification.json |
| Snapshotก่อนรอบเก็บตก ห้ามทับ | qa/chapter6/activity-ui/baseline.json และ revisions/ |

แก้คำแปลในJSONหรือสคริปต์ที่สร้างJSONให้ตรงกัน รัน `assemble_chapter6.py` → `build_chapter1.py --chapter6-working --text-only`(เมื่อไม่เพิ่มglyph) → `verify_chapter1.py --chapter6-working` → `audit_chapter6.py` → `audit_chapter6_activity_ui.py` → `audit_chapter6_editorial.py` → `audit_gender_through_chapter6.py` → `preview_chapter6_activity_ui.py`(ดูภาพ) → `publish_final_parts.py` → `finalize_chapter6.py` สคริปต์สุดท้ายเรียก `finalize_chapter6_activity_ui.finish()` ด้วย อย่ารัน `chapter6_activity_ui.py --prepare` ซ้ำหรือเขียนทับsnapshot หากมีการแก้รอบใหม่ต้องตั้งbaselineรอบใหม่และเทียบหลักฐานเดิมไว้ด้วย
<!-- /costa-activity-ui-current -->

'''
    for p in [W/'CHAPTER6-STATUS.md',W/'FINAL-PARTS.md',W.parent/'HANDOFF.md']:
        text=p.read_text('utf-8');title,body=text.split('\n',1)
        # The base finalizer rewrites these docs; guard independent reruns too.
        if '<!-- costa-activity-ui-current -->' in body:
            start=body.index('<!-- costa-activity-ui-current -->');end=body.index('<!-- /costa-activity-ui-current -->')+len('<!-- /costa-activity-ui-current -->')
            body=body[:start]+body[end:]
        p.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    for p in [W/'AGENTS.md',W/'TRANSLATION_GUIDE.md']:
        text=p.read_text('utf-8');title,body=text.split('\n',1)
        short='Latest Costa activity UI supplement (2026-10-18): +131 UI records (164 inventoried;33 English/symbol entries preserved), Ch.6 UI153, combined23,811/23assets/674clusters. Only Common ZIP changed; all4scene ZIPs, all23,680 previous texts/ACTORs, fonts/textures and installed files preserved. See CHAPTER6-STATUS.md activity section and qa/chapter6/activity-ui. Run audit_chapter6_activity_ui.py and preview_chapter6_activity_ui.py in the current build chain; finalize_chapter6.py also finalizes activity docs. No new spoken dialogue/Ch.7/runtime test.'
        if short not in text:p.write_text(title+'\n\n'+short+'\n\n'+body.lstrip(),'utf-8')
    print('Activity revision delivery verified: Common only; four chapter ZIPs unchanged; handoff updated.')

if __name__=='__main__':finish()
