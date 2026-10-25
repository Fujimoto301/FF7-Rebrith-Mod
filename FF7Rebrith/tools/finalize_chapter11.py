"""Record the verified Chapter11 release and prepend current handoff instructions."""
import re,json
from pathlib import Path
from prepare_chapter9 import W,read,write
from audit_chapter11 import digest
from assemble_ui_completion import fingerprint
def main():
    cfg=read('reference/chapter11-build.json');a=read('qa/chapter11/translation-audit.json');g=read('qa/chapter11/gender/summary.json');b=read('qa/chapter11/baseline.json');r=read('qa/final-parts/latest.json');m=read('qa/final-parts/combined-mount-verification.json');sign=read('qa/chapter11/editorial-signoff.json')
    sha=digest(W/cfg['source']);assert a['source_sha256']==sign['source_sha256']==sha and a['previous40691_text_and_ACTOR_preserved']
    assert fingerprint()==b['protected'] and m['zip_count']==8 and m['assets']==27 and not m['overlapping_assets']
    for p in r['parts']:assert digest(W.parent/'Mod/Final'/p['zip'])==p['sha256']
    assert {p['zip'] for p in r['parts']}=={p.name for p in (W.parent/'Mod/Final').glob('*.zip')}
    write('qa/chapter11/release-verification.json',dict(source_sha256=sha,parts=r['parts'],mount_verification=m,previous40691_preserved=True,protected_files_unchanged=True,installed=False,in_game_tested=False,original_rename_backup='qa/final-parts/runs/08598cfac07348f599045f745855a7b2/previous-final'))
    block=f'''<!-- chapter11-current -->
## ล่าสุด: Chapter 11 — The Long Shadow of Shinra — 24 ตุลาคม 2026

ผู้ใช้สั่งเริ่ม Ch.11 แล้ว ส่วนนี้แทนคำแนะนำฐานปัจจุบัน/คำสั่งพักCh.11ในประวัติด้านล่าง เพิ่ม **1,703รหัส / 1,658แม่แบบ** รวม **42,394รหัส / 27assets / 721clusters** ฐานก่อนหน้า40,691ข้อความและACTORทุกตัวคงเดิมครบ รวมคำแก้บริบทสองรอบ1,290รหัส ห้ามassembleบทเก่า/รันfinalizerเก่าทับฐานนี้

ฐาน **E:/FF7RebrithModTH/FF7Rebrith/translations/working-through-chapter11-th.json** SHA256 **{sha}**; patch translations/chapter11-th.json; แม่แบบ translations/chapter11/batch-01.json ถึง batch-10.json; inventory reference/chapter11-source.json; config reference/chapter11-build.json; map reference/through-chapter11-cluster-map.json; stage staging/ThaiJP_ThroughChapter11_Working; QA qa/chapter11 ดู [CHAPTER11-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CHAPTER11-STATUS.md)

ทำบทหลักC3110ใหม่632รหัส, โปรโตเรลิกCHADL_QST06ทั้ง4ช่วง204รหัส, เควสต์Esoteric Secrets of the Elders246รหัสและMy White-Haired Angel176รหัส, บทต่อสู้NIBLS_BOS15/16 อีก46รหัส, NIBLT_NPC20ทุกสถานะ201รหัส รวมNIBLEใหม่1,505รหัส และResident198รหัส(Chadley/MAI/Odin/World Intel/PHOTO/Dale/Turner) รวมทั้งบรรทัดไม่มีACTOR ไม่พักNPCทั้งหมวด ตรวจย้อนNIBLEที่ยังญี่ปุ่น272รหัส เหลือC3210บท12จำนวน128กับLament of the Damned144รหัส มีเหตุผลรายID ไม่เริ่มบทพูดCh.12เอง ส่วนUIบทภายหลังที่แปลไว้แล้วคงเดิม

ยึดJPเป็นหลัก USรหัสเดียวกันใช้ป้ายชื่อและเทียบบริบท ไม่ดึงบทดัดแปลงUSมาแทนJP: เรื่องความทรงจำแซ็ก/โฮโจ/โรช/เรด/นิสัยคลาวด์/บิลลี่และแซม ตรวจตัวเลือกCh.11ครบ12กลุ่ม47รหัสพร้อมทุกปุ่มและบทตอบรับในข้อมูล; คงชื่อUIอังกฤษ แต่บทพูดใช้ไทย คงแมว**มารุ**จากCh.1และชื่อใหม่**ชิโระ**ตามJPเพื่อรักษาบทสนทนาเรื่องชื่อที่แปลว่ากลม/ขาว ชื่อNPCในบทพูดใช้ชื่อofficialUSทับศัพท์ เช่นนิค/คริสทีน/บิลลี่/วิล ไม่เดาเพศจากsuffix ผู้ดูแลและผู้พูดไม่ชัดใช้กลาง

คำลงท้ายรวม **{g['actual_particle_occurrences']}ครั้งใน{g['particle_bearing_records']}รหัส: ครับ{g['counts']['ครับ']} / ค่ะ{g['counts']['ค่ะ']} / คะ{g['counts']['คะ']}** NPC/nonparty{g['npc_or_nonparty_occurrences']}ครั้ง รักษา1,278ครั้งเดิมครบ ตรวจผู้พูดที่เพิ่มตามหลักฐาน(บิลลี่ระบุชัดว่าเป็นลูกชายในJP) ไม่พบเพศสลับในทะเบียน ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ; เรียกCloudนาย/คุณ กลุ่มรวมCloudพวกนาย/พวกคุณ ไม่replaceเธอรวมทุกคน คงRedวัยหนุ่มฉัน/เอริธ/แซ็ก/เค็ตชี/โซลเจอร์/แมทีเรียตามศัพท์เดิม

ตรวจอ่านกลับtext/metadataทุกIDทั้งasset ผ่านgateUIเดิม6,907รหัส ตัวเลือกทั้งfamily7,218รหัส NPCเก็บตกเดิม8,347รหัส และชื่อท่าอังกฤษ1,703ป้าย เลขต่าง11รายการอ่านและบันทึกเหตุผลแล้ว เพิ่มclusterคั้/ง้/จื้/ชึ่แบบappend-only รักษา717assignmentและmetricsเดิมทั้ง8fonts/nativeASCIIเลขไอคอนเดิม/จุดไข่ปลาระดับล่าง ภาพproof12หน้า48panels96font samplesดูครบจริง รวม12กลุ่มคำถามครบทุกปุ่ม เป็นตัวอย่างการตัดบรรทัดจากglyphจริง ไม่ใช่ภาพเกมและไม่ใช่การฟัง/เล่นทุกแขนง

Finalมีเฉพาะ8ZIPล่าสุด อัปเดต **ThaiJP_Chapter1_11_P.zip** (NIBLEใช้ร่วมCh.1จึงรวมกับMIDGR แทนThaiJP_Chapter1_P.zipเดิม) และ **ThaiJP_Common_P.zip** (Resident+ฟอนต์) อีก6ZIPhashเดิม อ่านกลับ8ZIP/24modfiles/27assetsรวมกันผ่านไม่มีซ้ำ สำรองรุ่นเดิมนอกFinalที่qa/final-parts/runs/08598cfac07348f599045f745855a7b2/previous-final ไม่ติดตั้ง/ไม่แก้ไฟล์เกมหรือdist

สร้างซ้ำ: tools/assemble_chapter11.py → tools/build_chapter11.py(เต็มเมื่อมีglyphใหม่; --text-onlyเมื่อmapเดิม)/--verify → tools/audit_shared_dialogs.py(รวมgateCh11ใหม่+regressionเก่า) → tools/audit_chapter11_glyphs.py → tools/preview_chapter11.py/ดูภาพจริงก่อนsignoff → tools/signoff_chapter11.py → tools/publish_final_parts.py → tools/finalize_chapter11.py คงreference/context-recheck-overrides.jsonและcontext-full-read-overrides.jsonโดยให้full-readชนะค่ารอบเก่า; frozenbaseมีทั้งสองชุดแล้ว ไม่เรียกoverlayเก่าทับfull-readตรงๆ ห้ามprepare_chapter11ซ้ำ/แก้snapshotในqa/chapter11/revisions

อ้างอิงภาพผู้พูด/เสียงยังใช้[คลิปผู้ใช้](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk)ตามHANDOFFเดิม รอบCh.11นี้ไม่อ้างดู/ฟังวิดีโอครบใหม่ ไม่ถือauto transcriptเป็นบทถูกต้อง งานต่อไปเมื่อผู้ใช้สั่งCh.12: ตั้งinventoryจากฐาน42,394นี้ รวมC3210/NIBLE_QST03, คู่แข่งQBหลังCh.12, Gold Cup/การกลับพื้นที่เก่าและกิจกรรมที่ปลดล็อกใหม่ ต้องตรวจNPCไม่มีACTOR คำถามทุกปุ่ม และสรรพนามตามบริบทอีกครั้ง
<!-- /chapter11-current -->
'''
    # Count is generated rather than inferred from the number of groups.
    count=sum(len(v) for v in read('qa/chapter11/choice-groups.json')['groups'].values());block=block.replace('12กลุ่ม47รหัส',f'12กลุ่ม{count}รหัส')
    paths=[W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'FINAL-PARTS.md',W/'CONTEXT-FULL-READ.md']+sorted(W.glob('CHAPTER*-STATUS.md'))
    for path in paths:
        t=path.read_text('utf8');t=re.sub(r'<!-- chapter11-current -->.*?<!-- /chapter11-current -->\s*','',t,flags=re.S)
        title,sep,rest=t.partition('\n');path.write_text(title+'\n\n'+block+'\n'+rest.lstrip('\n'),encoding='utf8')
    parts='\n'.join(f"- [{p['zip']}](E:/FF7RebrithModTH/Mod/Final/{p['zip']}) — {p['bytes']:,} bytes; SHA256 `{p['sha256']}`" for p in r['parts'])
    (W/'CHAPTER11-STATUS.md').write_text('# Chapter 11 — The Long Shadow of Shinra\n\n'+block+'\n## ZIPล่าสุดในFinal\n\n'+parts+'\n',encoding='utf8')
    print('Updated handoff, current release status and Chapter11 verification')
if __name__=='__main__':main()
