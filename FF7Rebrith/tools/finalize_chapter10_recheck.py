"""Close the source-bound recheck only after all current archives mount correctly."""
import re
from pathlib import Path
from prepare_chapter9 import W,read,write
from audit_chapter10 import digest
from assemble_ui_completion import fingerprint
Q='qa/chapter10/';R=Q+'recheck/'
def main():
    cfg=read('reference/chapter10-build.json');revision=read(R+'current.json');a=read(Q+'translation-audit.json');r=read(R+'review.json');s=read(Q+'editorial-signoff.json');p=read('qa/final-parts/latest.json');m=read('qa/final-parts/combined-mount-verification.json');h=digest(W/cfg['source']);g=read(Q+'gender/summary.json');ctx=read('qa/active-working-set.json')
    assert h==a['source_sha256']==r['source_sha256']==s['source_sha256']==read('qa/shared-dialogs/latest.json')['source_sha256']
    assert ctx['combined_source']==cfg['source'] and all(ctx[k] for k in ['chapter10','enemy_actions','npc_recheck','choice_completion'])
    for name,sha in s['reviewed_artifacts'].items():assert digest(W/name)==sha,name
    assert a['new_records']==2861 and a['total_combined_text_records']==p['combined_text_records']==40691
    continued=(W/'qa/chapter10/continue-review/current.json').exists()
    corrected=59 if continued else 43
    assert r['added_records']==144 and r['changed_records']==corrected and s['reviewed_proof_pages']==7
    assert m['zip_count']==8 and m['mod_files']==24 and m['assets']==27 and not m['overlapping_assets'] and m['all_match_verified_combined_set']
    old={x['zip']:x for x in read(Path(revision['snapshot'])/'qa/final-parts/latest.json')['parts']};changed=[];unchanged=[];union={};final=W.parent/'Mod/Final'
    assert {x.name for x in final.iterdir()}=={x['zip'] for x in p['parts']}
    for x in p['parts']:
        assert digest(final/x['zip'])==x['sha256'];assert not union.keys()&x['assets'].keys();union.update(x['assets'])
        (unchanged if old[x['zip']]['sha256']==x['sha256'] else changed).append(x['zip'])
    assert union==read(Q+'working-assets.json')
    assert changed==['ThaiJP_Chapter1_P.zip','ThaiJP_Chapter2_P.zip','ThaiJP_Chapter10_P.zip','ThaiJP_Common_P.zip'] and len(unchanged)==4
    assert fingerprint()==revision['protected']
    report=dict(source_sha256=h,total_text_records=40691,new_since_recheck=144,corrected_records=corrected,chapter10_and_recovered_shared_records=2861,working_assets=27,glyph_clusters=717,zip_count=8,mod_files=24,updated_parts=changed,unchanged_parts=unchanged,all_parts_independently_read_back_and_mounted=True,no_overlapping_assets=True,source_and_installed_files_unchanged=True,installed=False,in_game_tested=False,new_full_video_audio_review=False,backups=p['backups'])
    write(R+'release-verification.json',report);write(Q+'release-verification.json',report)
    root='E:/FF7RebrithModTH/FF7Rebrith/'
    note=f'''<!-- chapter10-recheck-current -->
## ล่าสุด: รีเช็ค Ch.10 และส่วนกลางที่เกี่ยวข้อง — 20 ตุลาคม 2026

ส่วนนี้แทนยอด/ขั้นตอนฐานปัจจุบันในประวัติด้านล่าง รีเช็คครั้งนี้ **เพิ่ม144รหัส แก้43รหัส** เหนือชุดCh.10เดิม40,547รหัส ปัจจุบัน **40,691รหัส / 27assets / 717clusters** งานCh.10และเก็บตกต่อเนื่องรวม2,861รหัส ไม่เริ่มบทหลักCh.11 ฐานยังเป็น **{root}translations/working-through-chapter10-th.json**; config reference/chapter10-build.json; stage staging/ThaiJP_ThroughChapter10_Working; map reference/through-chapter10-cluster-map.json

ต้นเหตุที่พบ: การเลือกฉากCosmoเพียงassetเดียวทำให้ฉากปิดโปรโตเรลิกที่ใช้FOREEร่วมกันตกหล่น เช่นเดียวกับResidentบทรายงานหลังฉาก/เรียกบริการCid/แจ้งแรงก์การ์ด รีเช็คเพิ่มfamilyอิสระใน tools/chapter10_recheck_scope.py และ gate tools/audit_chapter10_recheck.py ครอบคลุมFOREE50รหัส(ปิดJunon12/Gongaga22/Cosmo16) และResident94รหัส(รายงานโปรโตเรลิก23, Cid9, สำรวจCosmo4, เปิดBahamutArisen3, ช่วยการเดินทาง4, แรงก์การ์ด22, ทีฟ่าไปเตาปฏิกรณ์Gongaga3, Chadleyกลับเยือนเมืองเดิม26) เก็บordinaryreturnทุกพื้นที่ที่เยือน รวมสถานะหลังจบรายงาน โดยพักเฉพาะNibelที่ยังไม่เยือน ไม่พักทั้งnamespaceจากเลขสถานะ

แก้คำแปลเดิม43รหัส รวม **マルケเป็นวัตถุดิบมาร์เค ไม่ใช่มาร์ล**2จุด, ประโยคถูกขัดจังหวะ/ความรู้สึกอึดอัด/ผืนดินแยกออก/ความมุ่งมั่น และใช้คำเรียกพิธีส่งวิญญาณสู่ดวงดาวกับศาสตร์ชีวิตดวงดาวสม่ำเสมอ คง38,830? **ฐานก่อนCh.10จริง37,830ข้อความและACTORครบ**; ชุดCh.10เดิม40,547IDไม่หาย ACTORเดิมคงครบ มีรายการbefore/afterทุกรหัสใน qa/chapter10/recheck/review.json

ตรวจข้ามassetรหัสC2910/C3010ครบ917รหัส เพิ่มจากการตรวจselectorเดิม; ตรวจคำถาม/ตัวเลือกทั้งfamily7,218รหัส, NPCหมวดพื้นที่ที่เยือน5,638รหัส(ไม่มีACTOR4,989), รักษาinventoryเก็บตกNPCเดิม8,347รหัสและชื่อท่าอังกฤษ1,703ป้าย อ่านย้อนทุกID/metadata/tagจากsourceเทียบstageรวม40,691ข้อความ สแกนResidentที่ยังเป็นญี่ปุ่นทุกตัวอีกชั้น **1,234รหัส** มีเหตุผลรายIDใน Resident-residual-dispositions.json: Nibel/บทภายหลัง/เควสต์ใหม่, ชีวประวัติและคำแนะนำวิเคราะห์ศัตรูที่ยังเป็นหมวดไม่ได้เริ่ม, UIdemoที่ไม่ใช้ในretail ไม่อ้างว่าญี่ปุ่นทุกประเภททั้งเกมหมดแล้ว

คำลงท้ายปัจจุบัน **1,278ครั้งใน1,246รหัส: ครับ874/ค่ะ255/คะ149** NPC/nonparty1,094ครั้ง รักษา976ครั้งก่อนCh.10ครบ ตรวจไม่พบสลับเพศหรือผู้พูดที่ยังไม่มีหลักฐาน Unknownใช้กลาง ไม่เดาเพศจากmma/mfa ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ; เอริธ/แซ็ก/เค็ตชี/กอนกาก้า/โซลเจอร์/โพชั่นตามฐานเดิม; ป้ายUSอังกฤษชื่อเดียวกัน ชื่อเรจี้/นาบารา/ไวซ์ในบทพูดเทียบฐานเดิมแล้ว

เพิ่มcluster **ฉี่** อีก1ตัวแบบappend-only รวม717 คง716assignment/metricsเดิมครบ8fonts/nativeASCIIเลขไอคอนพิกเซลเดิม/ระดับ…ล่าง อ่านproofglyphจริง7หน้า56ตัวอย่างรวมคำถามและทุกปุ่ม4ชุดแล้ว ตรวจความต่างตัวเลข27รายการพร้อมเหตุผล บางmaskไทยเดิมอาจต่างเล็กน้อยจากrepackBC5 ไม่อ้างพิกเซลไทยเดิมครบทุกตัว

อัปเดต **Chapter1 / Chapter2 / Chapter10 / Common** ใน E:/FF7RebrithModTH/Mod/Final อีก4ZIPhashเดิม ทั้ง8ZIPต้องใช้ร่วมกัน อ่านกลับรวม24modfiles/27assetsผ่านไม่มีซ้ำ สำรองนอกFinal ไม่ติดตั้ง/ไม่ทดลองในเกมหรือเล่นทุกแขนง/ไม่อ้างฟังวิดีโอครบใหม่ source/dist/ไฟล์ที่ติดตั้งคงเดิม

ไฟล์ส่งต่อเพิ่ม: reference/chapter10-recheck-source.json (144ID, indexappend-only), translations/chapter10-recheck-lines.json, qa/chapter10/recheck/current.json+revisions/(ห้ามprepareซ้ำ), review.json, terminology-decisions.json, Resident-residual-dispositions.json, release-verification.json รายละเอียด [CHAPTER10-RECHECK-STATUS.md]({root}CHAPTER10-RECHECK-STATUS.md)

ขั้นตอนล่าสุด: assemble_chapter10.py → build_chapter10.py --text-only(เมื่อmapคงเดิม)/เต็มเมื่อเพิ่มglyph → --verify → chapter10_recheck.py --quality → audit_shared_dialogs.py(รวม2gateCh.10+regressionเดิม) → audit_chapter10_glyphs.py → preview_chapter10.pyและดู7หน้า → signoff_chapter10.py → publish_final_parts.py → finalize_chapter10_recheck.py **ห้ามใช้finalize_chapter10.pyเดิมที่ยังผูกยอดก่อนรีเช็ค** บทถัดไปใช้ฐาน40,691นี้ คงflagทั้งหมดและเพิ่มgate/signoffใหม่ก่อนส่ง ต้องคง144รหัสเก็บตกใหม่และทะเบียนNPC/ตัวเลือกด้วย
<!-- /chapter10-recheck-current -->

'''.replace('คง38,830? **ฐานก่อนCh.10จริง37,830ข้อความและACTORครบ**','คงฐานก่อนCh.10ทั้ง37,830ข้อความและACTORครบ')
    note=note.replace('แก้43รหัส',f'แก้{corrected}รหัส').replace('แก้คำแปลเดิม43รหัส',f'แก้คำแปลเดิม{corrected}รหัส')
    table='\n'.join(f"| {x['zip']} | {len(x['assets'])} | {x['bytes']:,} |" for x in p['parts'])
    detail=f'''# ผลรีเช็ค Chapter10

{note}
## หลักฐาน/สิ่งที่เหลือ

พาธต่อจาก {root}:

| งาน | ไฟล์ |
| --- | --- |
| รายการก่อน/หลังแก้43รหัสและfamilyที่เพิ่ม | qa/chapter10/recheck/review.json |
| คำแปลเก็บตก144รหัส JP/USคู่กัน | reference/chapter10-recheck-source.json; translations/chapter10-recheck-lines.json |
| สแกนต้นฉบับอิสระ | qa/chapter10/recheck/independent-residual-scan.json (snapshotก่อนเก็บตก) |
| ญี่ปุ่นที่ยังเหลือในResidentพร้อมเหตุผลทุกID | qa/chapter10/recheck/Resident-residual-dispositions.json |
| ชื่อ/ศัพท์ทั้ง2,861รหัสและ4การย่อคำว่าเตาปฏิกรณ์ตามบริบท | qa/chapter10/recheck/terminology-candidates.json; terminology-decisions.json |
| เพศ/tag/metadata/ทุกID/ตัวเลือก | qa/chapter10/translation-audit.json; verification.json; gender/summary.json; choice-review.json |
| glyphและภาพที่ดูแล้ว | qa/chapter10/old-glyph-regression.json; proof-1.pngถึงproof-7.png; editorial-signoff.json |
| ผลส่งจริง/ZIPร่วมกัน | qa/chapter10/recheck/release-verification.json; qa/final-parts/latest.json; combined-mount-verification.json |

ต้นฉบับและindexเดิมไม่ถูกเปลี่ยน เก็บตกเพิ่มเป็นทะเบียนแยกเพื่อไม่ทำให้แม่แบบเดิมเลื่อน ภาพproofเป็นการวางglyphและตัดบรรทัดจำลอง ไม่ใช่ภาพเกม การตรวจไฟล์ทุกIDไม่ใช่การรับรองว่ามนุษย์ดูทุกฉาก/ฟังทุกNPCหรือทดลองทุกตัวเลือกในเกมแล้ว ต้องทดสอบruntimeเพิ่มเติมเมื่อผู้ใช้สั่งติดตั้ง

แยกเควสต์ใหม่Ch.12 Victim of Circumstance66บทพูดตามเดิม; รายการฉากที่เยือนยังเป็นญี่ปุ่น2,774รหัสแยกใน qa/chapter10/visited-scene-residual-dispositions.json ไม่เริ่มNibelบทหลัก/เควสต์/เนื้อเรื่องGoldSaucerกลับเยือนใหม่ ชื่อLidrehl/Vincent/Shadowbloodและบทจบ6เพลงเปียโนแยกตามเงื่อนไขความคืบหน้า ไม่เอาชื่อquest/พื้นที่อย่างเดียวมาตัดสินว่าอยู่ในCh.10

เสียง/บท/เพศอ้างอิงเดิม: [คลิปหลัก](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์ญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk); reference/plearngaming/glossary.json ไม่อ้างว่าฟังใหม่ครบ แหล่งประกอบเงื่อนไข: [กิจกรรมCosmo](https://www.powerpyx.com/final-fantasy-7-vii-rebirth-cosmo-canyon-all-world-intel-locations/), [Ch.10/ReginaหลังถึงCosmo](https://www.powerpyx.com/final-fantasy-7-vii-rebirth-chapter-10-watcher-of-the-vale-walkthrough/)

## ZIPส่งจริง

| ZIPใน E:/FF7RebrithModTH/Mod/Final | assets | bytes |
| --- | ---: | ---: |
{table}

สำรองก่อนรีเช็คอยู่นอกFinal: `{p['backups']}` ใช้8ZIPล่าสุดร่วมกัน CommonยังถือResident/TITLB/ฟอนต์ ส่วนCOSMEอยู่Chapter10, FOREEอยู่Chapter2, MIDGRอยู่Chapter1 ไม่มีassetซ้ำ
'''
    detail=detail.replace('ก่อน/หลังแก้43รหัส',f'ก่อน/หลังแก้{corrected}รหัส')
    (W/'CHAPTER10-RECHECK-STATUS.md').write_text(detail,'utf-8')
    for path in [W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'CHAPTER10-STATUS.md']:
        title,body=path.read_text('utf-8').split('\n',1);body=re.sub(r'<!-- chapter10-recheck-current -->.*?<!-- /chapter10-recheck-current -->\s*','',body,flags=re.S);path.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    (W/'FINAL-PARTS.md').write_text(f'''# ZIPล่าสุดแยกแต่ละส่วน

20ตุลาคม2026 หลังรีเช็คCh.10: **40,691ข้อความ / 27assets / 717clusters / 8ZIP / 24modfiles**

| ZIP | assets | bytes |
| --- | ---: | ---: |
{table}

ใช้ทั้ง8ZIPล่าสุดร่วมกันใน **E:/FF7RebrithModTH/Mod/Final** รอบนี้แก้Chapter1/Chapter2/Chapter10/Common อีก4ZIPhashเดิม อ่านกลับ27assetsรวมกันผ่านไม่มีซ้ำ สำรองนอกFinal ไม่ติดตั้งหรือทดลองในเกม รายละเอียด [CHAPTER10-RECHECK-STATUS.md]({root}CHAPTER10-RECHECK-STATUS.md)
''','utf-8')
    print(f'Finalized recheck:144added,{corrected}corrected,40691records,8latestZIPs; no game installation')
if __name__=='__main__':main()
