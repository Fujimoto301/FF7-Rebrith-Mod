"""Verify the delivered Ch8 recheck and persist count-driven current handoff notes."""
import hashlib,re
from pathlib import Path
from collections import Counter
from prepare_chapter8 import W,read,write
from assemble_ui_completion import fingerprint

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    cfg=read('reference/chapter8-build.json');a=read('qa/chapter8/translation-audit.json');g=read('qa/chapter8/gender/summary.json')
    check=read('qa/chapter8/recheck-review.json');baseline=read('qa/chapter8/recheck-current.json');snapshot=Path(baseline['snapshot'])
    release=read('qa/final-parts/latest.json');mount=read('qa/final-parts/combined-mount-verification.json');sign=read('qa/chapter8/editorial-signoff.json');gate=read('qa/shared-dialogs/latest.json')
    total=a['total_combined_text_records'];clusters=a['glyph_clusters'];n=a['chapter8_records'];shared=a['new_shared_speech'];ui=a['new_UI'];defer=read('reference/chapter8-deferred.json')
    fixes=a.get('prior_record_name_spelling_corrections',[])
    preservation='คงรหัส/ACTORครบ โดยแก้สะกดเอริธ4รหัส' if fixes else 'คงข้อความ/ACTORครบ'
    assert release['chapters']==list(range(1,9)) and release['combined_text_records']==total==check['combined_records']==g['source_records_scanned']
    assert mount['zip_count']==6 and mount['assets']==25 and mount['mod_files']==18 and mount['all_match_verified_combined_set'] and not mount['overlapping_assets']
    assert fingerprint()==baseline['protected']
    assert check['source_sha256']==g['combined_source_sha256']==sign['combined_source_sha256']==gate['source_sha256']==digest(W/cfg['source'])
    assert sign['translation_sha256']==digest(W/'translations/chapter8-th.json') and sign['proof_visually_reviewed'] and sign['recheck_proof_visually_reviewed']
    assert not g['gender_mismatches'] and not g['unresolved_particle_bearing_speakers']
    assert (a['old_text_and_ACTOR_preserved'] or len(fixes)==4 and a['prior_record_IDs_and_ACTOR_preserved']) and a['previous_records_preserved']+len(fixes)==26951
    assert len(check['fonts'])==8 and all(f['previous698_metrics_preserved'] and not f['changed_masks'] for f in check['fonts'])
    assert len(read('qa/chapter8/proof.json')['samples'])==len(read('qa/chapter8/recheck-proof.json')['samples'])==32
    prior={p['zip']:p for p in read(snapshot/'qa/final-parts/latest.json')['parts']};final=W.parent/'Mod/Final'
    assert {p.name for p in final.iterdir()}=={p['zip'] for p in release['parts']}
    manifest=read('qa/chapter8/working-assets.json');updated=[];unchanged=[]
    for p in release['parts']:
        assert digest(final/p['zip'])==p['sha256'] and all(manifest[k]==v for k,v in p['assets'].items())
        (unchanged if p['sha256']==prior[p['zip']]['sha256'] else updated).append(p['zip'])
    assert set(updated)=={'ThaiJP_Chapter8_P.zip','ThaiJP_Common_P.zip'}|({'ThaiJP_Chapter6_7_P.zip'} if fixes else set())
    write('qa/chapter8/release-verification.json',dict(chapters=list(range(1,9)),text_records=total,chapter8_primary_records=n,new_shared_speech=shared,new_UI=ui,
      prior_26951_text_and_ACTOR_preserved=not fixes,prior_26951_IDs_and_ACTOR_preserved=True,prior_name_spelling_corrections=fixes,assets=25,glyph_clusters=clusters,recheck_added=check['added_records'],recheck_corrected=check['corrected_records'],
      prior_30401_IDs_and_ACTOR_preserved=True,previous698_mapping_metrics_and_masks_preserved=True,ZIP_count=6,mod_files=18,updated_parts=updated,unchanged_parts=unchanged,
      all_parts_read_back_and_mounted_together=True,no_overlapping_assets=True,source_and_installed_files_unchanged=True,actual_gender_particle_occurrences=g['actual_particle_occurrences'],
      gender_mismatches=[],proof_visually_reviewed=True,installed=False,in_game_tested=False,new_full_video_audio_review=False,manifest='qa/final-parts/latest.json',backup=release['backups']))
    parts='\n'.join(f"| {p['zip']} | {len(p['assets'])} | {p['bytes']:,} |" for p in release['parts'])
    reasons='\n'.join(f'| {key} | {value} |' for key,value in Counter(r['reason'] for r in defer).items())
    base='E:/FF7RebrithModTH/FF7Rebrith/'
    note=f'''<!-- chapter8-current -->
## ล่าสุด: Chapter8 ตรวจซ้ำ — 19 ตุลาคม 2026

ส่วนนี้แทนยอด/พาธ/สถานะเก่า: **{total:,}รหัส25assets{clusters}clusters** กลุ่มหลัก{n:,}+บทส่วนกลาง{shared}+UI{ui} เหนือฐานCh.7เดิม26,951{preservation} รอบตรวจซ้ำเพิ่ม{check['added_records']}รหัสแก้{check['corrected_records']}รหัสจากCh.8เดิม30,401 เก็บตกNPCทั่วไป13และPHOTOช่างภาพ/ChadleyWORLD รวมG-Bike/Card Challenge/ร้าน/ของสะสม/คำอธิบายโชโคโบะ พักสถานะบทภายหลัง{len(defer)}รหัสพร้อมเหตุผล ไม่เริ่มCh.9

ฐาน **{base}translations/working-through-chapter8-th.json**; stage staging/ThaiJP_ThroughChapter8_Working; config/map reference/chapter8-build.json / through-chapter8-cluster-map.json; QA qa/chapter8 รายละเอียดและไฟล์ทั้งหมด [CHAPTER8-STATUS.md]({base}CHAPTER8-STATUS.md)

Finalมี6ZIPล่าสุดแยกส่วน Chapter1/Chapter2/Chapter3_4_5/Chapter6_7/Chapter8/Common ต้องใช้ร่วมกัน ชุดตรวจซ้ำอัปเดต {', '.join(updated)} คงเดิม{len(unchanged)}ส่วนเมื่อเทียบก่อนตรวจซ้ำ สำรองนอกFinal อ่านกลับ18mod files25assetsผ่านไม่มีทับกัน ไม่ได้ติดตั้งหรือทดสอบในเกม

ชื่อAerithปัจจุบันใช้ “เอริธ” ในบทพูด ป้ายผู้พูด/UIใช้Aerith เมื่อพบCh.6–7ตกอีก4รหัส ได้แก้เฉพาะ4รหัสและอัปเดตChapter6_7เพิ่มเติม รายการก่อน/หลังอยู่ในtranslations/aerith-name-corrections.json และqa/aerith-name-fix/latest.json เก็บฐานCh.7ประวัติเดิมไว้ไม่แก้ย้อนหลัง assemble_chapter8.pyลงcorrection overlayก่อนbuild; audit_chapter8.pyอนุญาตเฉพาะ4รายการที่ประกาศไว้ ฐานที่ใช้ส่งต่องานต้องเป็นworking-through-chapter8-th.json

ตรวจUIญี่ปุ่น{gate['verified_JP_origin_records']:,}รหัสในstandinggateพร้อมspeechfamilyทุกหมวดที่ลงทะเบียน คำลงท้าย{g['actual_particle_occurrences']}ครั้งใน{g['particle_bearing_records']}รหัส:ครับ{g['counts']['ครับ']}/ค่ะ{g['counts']['ค่ะ']}/คะ{g['counts']['คะ']} ชาย{g['male_speaker_occurrences']}/หญิง{g['female_speaker_occurrences']} ไม่มีสลับเพศตามหลักฐาน UnknownNPCกลาง ไม่ใช้mma/mfaตัดสินเพศ ตรวจชื่อ/เลข/ผู้ฟังและบริบทด้วย …ระดับล่าง/nativeASCIIเลขไอคอนเดิมครบ8fonts รักษา698assignment/metrics/maskเทียบCh.8ก่อนตรวจซ้ำครบ ไม่เพิ่มglyph ไม่อ้างเล่นหรือฟังวิดีโอครบใหม่

build chain: assemble_chapter8.py → build_chapter8.py --text-only(เมื่อglyphไม่เพิ่ม มิฉะนั้นbuildเต็ม) → --verify → audit_chapter8.py → audit_chapter8_glyph_regression.py → audit_gender_through_chapter8.py → audit_shared_dialogs.py → audit_chapter8_recheck.py → preview_chapter8.py และ --recheck(ดูภาพ) → publish_final_parts.py → verify_final_parts.py → finalize_chapter8.py อัปเดตeditorial-signoffผูกhashก่อนfinalize ห้ามprepareซ้ำ/เปลี่ยนindex/ใช้auditบทเก่าทับactivecontext

ทุกบทถัดไปต้องค้นNPCมี/ไม่มีACTORกับResident/PHOTO/WORLD/CARDGและnamespaceข้างเคียง ตรวจคำถามและทุกปุ่ม รับ/ปฏิเสธ/ยกเลิก/ลองใหม่/ผลแพ้ชนะทั้งหมวด เพิ่มfamilyในaudit_shared_dialogs.pyก่อนแพ็ก ตรวจสถานะค้างที่ปลดล็อกใหม่ ไม่อาศัยเลขChapterหรือ*_sysอย่างเดียว คงข้อกำหนดถาวรด้านล่าง
<!-- /chapter8-current -->

'''
    status=f'''# Chapter 8 — All That Glitters: ตรวจซ้ำล่าสุด

{note}
## สิ่งที่พบและแก้ในการตรวจซ้ำ

เทียบกับCh.8ที่ส่งก่อนหน้า30,401รหัส เพิ่ม **{check['added_records']}รหัส** แก้ **{check['corrected_records']}รหัส** รักษาID/ACTORเดิมครบ รายละเอียดก่อน/หลังทุกจุด: qa/chapter8/recheck-review.json

- เก็บตกNPCทั่วไป13รหัสที่เคยกันรวมกับCh.12: Park Central6และผู้ชมBeast Battleground7 ยังพักปฏิกิริยาสงคราม/ปาร์ตี้Gus/Gold Cupที่เป็นเนื้อเรื่องภายหลัง
- เพิ่มPHOTO_QST_04ของSnaps และWORLD_CDV_01ช่วงNorth Corel/Gold Saucer/Corel PrisonของChadley รวมเก็บตกส่วนกลางCh.7 ไม่อ้างว่ารอบก่อนครอบคลุมNPCเหล่านี้แล้ว
- เพิ่มเมนูควบคุม/HUD G-Bike ชื่อร้านทั้ง7Square Card Challengeระดับต้น/สูง/Survivalครบกติกา/เงื่อนไข/ชื่อด่าน ตั๋วเข้า/ตั๋วคู่ ของสะสม/คำใบ้ ชุดCait Sith ชื่อZoom de Chocobo และเป้าหมายส่วนกลางMidgar9รหัส
- แก้คำอธิบายโชโคโบะ7รายการที่ถูกเข้าใจว่าเป็นชื่อและยังเป็นอังกฤษให้เป็นไทย ยึดJPเรื่องความสามารถ โดยไม่เพิ่มคุณสมบัติของตัวจักรกลจากUSที่ไม่มีในJP
- ใช้มูเกิ้ล/เจสซี่/วันเดอร์/โซลเจอร์ตรงชุดเดิม แก้ชื่อหน้าพิซซ่าที่เจสซี่พูดจากPlearnเดิม ปรับถ้อยคำบางจุดและตรวจสระ/วรรณยุกต์ซ้ำทั้งชุด

## ขอบเขตและรายการพัก

กลุ่มหลัก{n:,}จากต้นฉบับ2,701รหัส/2,557แม่แบบ ส่วนกลางเหนือฐานCh.7เป็น{shared}บท+{ui}UI รวมงานเหนือฐาน **{n+shared+ui:,}รหัส** คลังส่วนกลาง{a['supplement_inventory']:,}รหัสรวมรหัสเดิมด้วย ครอบคลุมGold Saucerครั้งแรก ทุกแขนงเพื่อนร่วมเที่ยว เหตุยิง Corel Prison ทุกกิจกรรมหาอาหารPiko ปริศนาจริง/เท็จ การเตรียมแข่ง/ฝึก/แพ้/ลองใหม่/ชนะ Dyne, Palmerและบักกี้หลบหนี

รวมZackMIDGR59รหัส(เก็บตกCh.7จำนวน32/Ch.8จำนวน27), CARDG_QST_03/12/13ของWize/Rolf/Rocco/Biff/Prison ในกลุ่มรหัสNPCหลักมี{a['NPC_records']}บรรทัด ไม่มีACTOR{a['NPC_without_ACTOR']}บรรทัด เป็นจำนวนบรรทัด ไม่ใช่จำนวนตัวละคร และไม่รวมNPCที่ใช้รหัสเควสต์/CARDG/PHOTO/WORLD

พักกลุ่มหลัก **{len(defer)}รหัส** พร้อมเหตุผลรายรหัสในreference/chapter8-deferred.json:

| เหตุผล | รหัส |
| --- | ---: |
{reasons}

ไม่แตะC3210/C3230, GOLDE_QST, GOLDS_BOS17/18หรือMIDGRหลังC2610 สนามจำลอง/ภูมิภาคอื่น279รหัสอยู่ในchapter8-supplement-outside-scope.json ผลค้นเนื้อหาข้างเคียง/การแยกค้างอยู่ในqa/chapter8/recheck-neighbour-dispositions.json UIกิจกรรม/ของสะสมที่ปลดล็อกภายหลังแปลตามนโยบายUIทั้งเกม แต่ไม่เพิ่มบทพูดCh.12หรืออ้างว่าข้อความญี่ปุ่นทั้งเกมหมดแล้ว

## หลักตรวจและข้อจำกัด

ตรวจคำถามพร้อมทุกปุ่มของหมวดที่ลงทะเบียน: ใช่/ไม่ใช่/เริ่ม/รับบริการ/ยกเลิก/เล่นต่อ/ลองใหม่/ผลแพ้ชนะ ทั้งฉากและResident ไม่อาศัย*_sysอย่างเดียว กลุ่มหลักมี39systemรหัส; choice-reviewคัดด้วยsys/หรือไม่ จึงไม่ใช่จำนวนปุ่มทั้งหมด Standing gateตรวจUIต้นฉบับญี่ปุ่น{gate['verified_JP_origin_records']:,}รหัสพร้อมคลังNPCส่วนกลาง เพิ่มfamilyถาวรในchapter8_supplement.pyที่audit_shared_dialogs.pyนำเข้า และตรวจspeechfamilyกับcorpusอิสระ

JPเป็นหลัก ป้ายผู้พูด/ชื่อเฉพาะในUIใช้USรหัสเดียวกัน ชื่อในคำพูดและจดหมายเป็นไทย เลขจริงเป็นอารบิก คงแท็กปุ่ม/สี/ตัวแปรJP รวมSurvival5รอบ ห้ามจั่วตั้งแต่รอบ4 สนับสนุนรอบ1 และจั่ว5ใบถึงรอบ3ที่USละบางรายละเอียด เลข32ในIfrit's 32-Bit Flamesเป็นชื่อUS ไม่ใช่เลขเนื้อหาที่เพิ่มเอง ดูrecheck-numeric-review.json

คำลงท้ายตามnoteด้านบน: ค่ะบอกเล่า คะคำถาม/นะคะ ห้ามนะค่ะ NPCไม่ทราบเพศใช้ถ้อยคำกลาง ไม่ใช้mma/mfaตัดสินเพศ ตรวจผู้ฟังและบุคคลที่กล่าวถึงด้วย แยกคะ…ครับที่เป็นการติดอ่างชายออกจากคำลงท้ายหญิง หลักฐานรายรหัสอยู่ในgender/records.json ไม่อ้างว่าฟังเสียงทุกคนใหม่

เทียบCh.8ก่อนตรวจซ้ำแล้ว698assignment/metrics/maskตรงเดิมครบ8fonts NativeASCII/เลข/ไอคอนผ่านการตรวจพิกเซลเดิม …ระดับล่างเสมอจุดnative ไม่เพิ่มglyphรอบนี้ เมื่อเทียบฐานCh.7เดิม687ตัว การสร้างatlasของCh.8ครั้งแรกมีBC5recompressionไทยเล็กน้อยตามold-glyph-regression ต้องระบุฐานเทียบให้ถูก

ดูproof8หน้าจากglyphในstagingจริงแล้ว: proof-1ถึง4และrecheck-proof-1ถึง4 รวมเลข/อังกฤษแทนตัวแปรหลังencodeและ… เป็นภาพจัดบรรทัดประกอบตรวจฟอนต์ ไม่ใช่ภาพเกม จึงยังไม่ยืนยันการตัดบรรทัดและทุกทางเลือกในเกมจริง ไม่อ้างว่าดูหรือฟังวิดีโอครบใหม่

## ZIP ล่าสุดแยกแต่ละส่วน

| ZIP | assets | bytes |
| --- | ---: | ---: |
{parts}

ใช้ทั้ง6ZIPร่วมกันใน E:/FF7RebrithModTH/Mod/Final ชุดตรวจซ้ำอัปเดต {', '.join(updated)} คงเดิม{len(unchanged)}ส่วนเมื่อเทียบก่อนตรวจซ้ำ สำรองตัวเก่านอกFinal อ่านกลับ18mod filesและmountร่วมกันตรงstaging25assets ไม่มีทับกัน ต้นฉบับ/dist/ม็อดที่ติดตั้งไม่เปลี่ยน

## ไฟล์และงานส่งต่อ

ฐาน **{base}**:

| งาน | ไฟล์ใต้ฐาน |
| --- | --- |
| รวมปัจจุบัน | translations/working-through-chapter8-th.json |
| JP/US/แม่แบบ/ขอบเขต | reference/chapter8-source.json, chapter8-templates.json, chapter8-scope.json, chapter8-deferred.json |
| คำแปลหลัก | translations/chapter8/batch-00.jsonถึงbatch-13.json, batch-14-recheck.json, reused-lines.json; translations/chapter8-th.json |
| ส่วนกลาง | reference/chapter8-supplement-source.json, chapter8-supplement-templates.json, chapter8-supplement-outside-scope.json; translations/chapter8-supplement-manual.json, chapter8-supplement-automatic.json |
| config/map/stage | reference/chapter8-build.json, through-chapter8-cluster-map.json, dialogue-punctuation-policy.json; staging/ThaiJP_ThroughChapter8_Working |
| snapshotห้ามทับ | qa/chapter8/baseline.json, revisions/, recheck-current.json, recheck/ |
| ตรวจบท/ตัวเลือก/ชื่อ/เลข/เพศ | qa/chapter8/translation-audit.json, review-records.json, choice-review.json, relationship-context-review.json, number-review.json, proper-name-review.json, recheck-review.json, recheck-additions.json, recheck-numeric-review.json, recheck-neighbour-dispositions.json, editorial-signoff.json, gender/summary.json, gender/records.json |
| ฟอนต์/แพ็ก | qa/chapter8/verification.json, old-glyph-regression.json, proof*.png, recheck-proof*.png, release-verification.json; qa/active-working-set.json; qa/final-parts/latest.json, combined-mount-verification.json |

Python `C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`; ตั้งPYTHONUTF8=1 รันจากโปรเจกต์ตามbuild chainในnoteด้านบน ใช้--text-onlyเมื่อไม่มีglyphเพิ่ม มิฉะนั้นbuildเต็ม ต้องดูภาพและผูกeditorial-signoffกับhashปัจจุบันก่อนfinalize ห้ามprepareซ้ำ/เปลี่ยนindex/ใช้auditบทเก่าทับactivecontext ไม่ลงม็อดจนผู้ใช้สั่ง เครื่องมือต่อเติมเก็บไว้เพื่อหลักฐาน ห้ามรันซ้ำเพื่อล้างแม่แบบ

เมื่อผู้ใช้สั่งCh.9 ให้เริ่มจากworking-through-chapter8-th.json ตรวจNPCมี/ไม่มีACTORกับทุกคำถาม/ตัวเลือกทั้งfamily รวมPHOTO/WORLD/CARDG/Residentและnamespaceข้างเคียง ตรวจสถานะค้างCh.6–8ที่ปลดล็อกใหม่ ชื่อ/เลข/เพศ/ระดับ… คงชื่อUIอังกฤษและเลขอารบิก รอบนี้ไม่ได้เริ่มCh.9

แหล่งเทียบบท/เพศเดิม: [คลิปหลัก](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk), reference/plearngaming/remake/decoded-corpus.json ไม่มีtimestampหรือการฟังครบใหม่
'''
    (W/'CHAPTER8-STATUS.md').write_text(status,'utf-8')
    for path in [W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md']:
        text=path.read_text('utf-8');title,body=text.split('\n',1);body=re.sub(r'<!-- chapter[78]-current -->.*?<!-- /chapter[78]-current -->\s*','',body,flags=re.S)
        path.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    (W/'FINAL-PARTS.md').write_text(f'# ZIP ล่าสุดแยกแต่ละส่วน\n\n19 ตุลาคม 2026 หลังตรวจซ้ำCh.8และแก้ชื่อเอริธ: **{total:,}ข้อความ /25assets /{clusters}glyph clusters /6ZIP /18mod files**\n\n| ZIP | assets | bytes |\n| --- | ---: | ---: |\n{parts}\n\nใช้ทั้ง6ZIPร่วมกันใน E:/FF7RebrithModTH/Mod/Final ชุดตรวจซ้ำอัปเดต {", ".join(updated)} คงเดิม{len(unchanged)}ส่วนเมื่อเทียบก่อนตรวจซ้ำ เก็บล่าสุดของแต่ละส่วน สำรองนอกFinal อ่านกลับร่วม25assetsผ่านไม่มีทับกัน ไม่ได้ติดตั้งหรือทดลองในเกม\n\nรายละเอียด [CHAPTER8-STATUS.md]({base}CHAPTER8-STATUS.md) และ [HANDOFF.md](E:/FF7RebrithModTH/HANDOFF.md)\n','utf-8')
    print('Chapter8 recheck complete:',total,'records;',check['added_records'],'added;',check['corrected_records'],'corrected;6ZIPs verified; handoff saved')

if __name__=='__main__':main()
