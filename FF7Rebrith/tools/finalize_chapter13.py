"""Bind the verified Ch13 split release and update the next-work handoff."""
import re
from pathlib import Path
from prepare_chapter9 import W,read,write
from audit_chapter13 import CFG,Q,digest
from assemble_ui_completion import fingerprint

def main():
    cfg=read(CFG);sha=digest(W/cfg['source']);a=read(Q+'translation-audit.json');s=read(Q+'editorial-signoff.json');r=read('qa/final-parts/latest.json');m=read('qa/final-parts/combined-mount-verification.json');b=read(Q+'baseline.json');g=read(Q+'gender/summary.json')
    assert sha==a['source_sha256']==s['source_sha256'] and a['new_records']==853 and a['previous46650_text_and_ACTOR_preserved']
    for rel,h in s['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    assert fingerprint()==b['protected']
    assert m['zip_count']==8 and m['mod_files']==24 and m['assets']==27 and m['all_match_verified_combined_set'] and not m['overlapping_assets']
    assert r['chapters']==list(range(1,14)) and r['working_manifest']==Q+'working-assets.json' and r['combined_text_records']==47503
    final=W.parent/'Mod/Final';assert {p.name for p in final.iterdir()}=={p['zip'] for p in r['parts']}
    for p in r['parts']:assert digest(final/p['zip'])==p['sha256']
    old={p['zip']:p for p in read(Path(b['snapshot'])/'qa/final-parts/latest.json')['parts']};changed=[p['zip'] for p in r['parts'] if p['sha256']!=old[p['zip']]['sha256']]
    assert set(changed)=={'ThaiJP_Chapter2_P.zip','ThaiJP_Common_P.zip'}
    result=dict(source_sha256=sha,total_combined_text_records=47503,new_records=853,new_templates=809,previous46650_text_and_ACTOR_preserved=True,choice_groups_reviewed=2,proof_pages_viewed=11,changed_ZIPs=changed,parts=r['parts'],mount_verification=m,backup=r['backups'],protected_files_unchanged=True,installed=False,in_game_tested=False)
    write(Q+'release-verification.json',result)
    root='E:/FF7RebrithModTH/FF7Rebrith/';backup=r['backups'].replace('\\','/');ui=read(Q+'adjoining-UI-review.json')['registered_rows'];cov=read(Q+'coverage-review.json');npc=read(Q+'NPC-residual.json')
    block=f'''<!-- chapter13-current -->
## ล่าสุด: Ch.1–13 + Common — 25 ตุลาคม 2026

ผู้ใช้สั่งทำCh.13แล้ว ส่วนนี้แทนสถานะ/hash/วิธีสร้างปัจจุบันทั้งหมดด้านล่างซึ่งเก็บไว้เป็นประวัติ ฐาน **47,503รหัส / 27assets / 730clusters** `{root}{cfg['source']}` SHA256 **{sha}** ฐานCh.12หลังรีเช็ค46,650รหัสและACTORทุกตัวคงเดิม รวม56คำแก้ล่าสุด/45คำแก้สรรพนาม/ทีฟ่าCh.4**เข้ามาสิ**/Red**เชิญ**/ทีฟ่าCh.1**ถามสิ** ห้ามassembler/finalizerเก่าทับ

Ch.13 **Where Angels Fear to Tread** เพิ่ม **853รหัส / 809แม่แบบ**: C3310/C3320/C3330/C3340ข้ามasset751รหัส (Resident6+FOREE745), บทบอสวิหารTEMPL_BOS19–22ทุกตัวละคร100รหัส, บทช่างภาพจบงานPHOTO00_0900สองรหัส รวมการเดินทาง/วิหารทั้งสองกลุ่ม/การทดสอบRed,Tifa,Yuffie,Barret,Aerith,Cloud/ภาพผนัง/หลบหนี/ช่วงแมทีเรียดำ ไม่มีเพิ่มบทพูดC3410ความฝันหรือC3510/CAPTL_BOSของCh.14

อ่านJP/USรหัสเดียวกัน/ไทยครบ809แม่แบบระหว่างแปลและอ่านทวนJP/ไทยครบอีกครั้ง ปรับร่างใหม่12แม่แบบพร้อมเหตุผลก่อนหลังใน `{root}qa/chapter13/editorial-revisions.json` เช่นแมทีเรียดำ**ยกให้ใครไม่ได้** ไม่ใช่ปล่อยให้คนไป; คู่คำเฉิง/เอริธ**ยอมมาซะดีๆ... / ไม่ยอมค่ะ!**; ความโกรธ/ความเศร้าตามJP ไม่เอาบทUSดัดแปลงมาแทน; บทเอริธเรื่องความตายและความแข็งแกร่ง/ภาพผนังเรื่องภัยพิบัติอ่านต่อเนื่องครบ

ตรวจคำถามพร้อมทุกปุ่ม **2ชุด / 6รหัส** ที่แปลไว้แล้ว: ขึ้นฝั่ง/ยังไม่ขึ้น(จุดไม่ย้อนกลับ) และขึ้นเรือ/ยังไม่ขึ้น ทั้งสองคงเดิมตรงบริบท; อ่านUIข้างเคียง **{ui}รหัส** รวมชื่อเป้าหมาย/สรุป/แรงโน้มถ่วง/ไลฟ์สตรีม/คำสั่งช่วย/ร้านวิหาร ไม่มีแก้ฐานเก่า ตรวจนาย/เธอชุดใหม่{len(read(Q+'pronoun-review.json')['records'])}รหัสตามผู้ฟังจริง Tifa→Aerith,Nero→Yuffieใช้เธอ; Sephiroth→กลุ่มรวมCloudใช้พวกนาย; ทำนายเป็นคำศัพท์ ไม่ใช่สรรพนาม

Inverse scanทั้งcorpus: C33/TEMPL_BOSที่มีJP **{cov['Ch13_JP_origin_rows']}รหัส** ครบ และNPCมีJP **{npc['registered_NPC_JP_rows']}รหัส** ไม่เหลือตกหล่นในทะเบียน; ทุกJPที่ยังไม่แปลจัดเหตุผลรายIDในdeferred-remainingเป็นCh.14หรือdemo/store/event-only UI ไม่พักทั้งnamespaceจากsuffix ไม่อ้างว่าเล่นทุกสถานะแล้ว ตรวจอ่านกลับtext/metadata27assetsผ่านUI6907/ตัวเลือกfamily7218/NPCregression8347/ชื่อท่าศัตรู1703

คำลงท้ายรวม **{g['actual_particle_occurrences']}ครั้ง / {g['particle_bearing_records']}รหัส**: ครับ{g['counts']['ครับ']} / ค่ะ{g['counts']['ค่ะ']} / คะ{g['counts']['คะ']}; NPC/nonparty{g['npc_or_nonparty_occurrences']}ครั้ง ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ unknownใช้กลาง; ไม่อนุมานเพศจากsuffix. เสียง???ของCaitกลับมาระบุตัวได้จากบรรทัดถัดไปใช้ข้อยกเว้นexactIDเท่านั้น เรดวัยหนุ่มฉัน; เอริธ/แซ็ก/เค็ตชี/บาร์เร็ต/เฉิง/รู้ด/อิเลน่า/เรโน/โซนอน/ซิด/วินเซนต์/เซทรา/มาโก้/แมทีเรีย/โซลเจอร์/อู่ไถตามglossary ชื่อACTORและUIอังกฤษตามUS บทพูดไทย เลขปริมาณอารบิก

ฟอนต์730clustersไม่เพิ่ม ทุกassignment/metricsเดิม8fontsคงเดิม; nativeASCII/เลข/จุดไข่ปลาระดับล่างผ่านตรวจ pixel/textureจริง ดูproof **11หน้า**: คำถามพร้อมทุกปุ่มและ36ตัวอย่างบทพูดคู่Large/Normal รวม76font samples +แผ่นเทียบ8fonts ภาพตัดบรรทัดเป็นตัวอย่าง **ยังไม่ได้ติดตั้ง/ทดสอบในเกม หรือดูฟังวิดีโอครบทุกแขนง**

Finalมี **8ZIPล่าสุดชื่อเดิมแยกส่วน** ที่ `E:/FF7RebrithModTH/Mod/Final` อัปเดต **ThaiJP_Chapter2_P.zip** (FOREEแชร์Ch.2และCh.13) กับ **ThaiJP_Common_P.zip** อีก6ZIPhashเดิม ไม่สร้างZIPCh.13ซ้ำasset อ่านรวม8ZIP/24modfiles/27assetsผ่านไม่มีทับซ้อน ต้องใช้ชุดล่าสุดร่วมกัน สำรองเก่านอกFinal `{backup}` source/dist/เกมไม่เปลี่ยน

ไฟล์ทำงานใต้ `{root}`: `reference/chapter13-source.json`, `chapter13-templates.json`, `chapter13-scope.json`, `chapter13-build.json`, `through-chapter13-cluster-map.json` (5ไฟล์นี้ในreference/); `translations/chapter13/batch-01.json`ถึง`batch-08.json`, `translations/chapter13-th.json`, `{cfg['source']}`. QA `qa/chapter13/`: baseline+revisionsimmutable(ห้ามprepareซ้ำ/รีเซ็ตindex), progress,review-records,editorial-revisions,choice/pronoun/numeric/duplicate-context/adjoining-UI/coverage/deferred/NPC/gender,verification,old-glyph-regression,proof,visual-review,editorial-signoff,release-verification

สร้างซ้ำ: `tools/assemble_chapter13.py` → `tools/build_chapter13.py --text-only` (mapเดิม;เต็มเมื่อglyphใหม่) → `tools/build_chapter13.py --verify` → `tools/audit_shared_dialogs.py` → `tools/audit_chapter13_glyphs.py` → `tools/chapter13_review.py` → `tools/preview_chapter13.py` → เปิดดูภาพจริง+บันทึกvisual-reviewตามhash → `tools/signoff_chapter13.py` → `tools/publish_final_parts.py` → `tools/finalize_chapter13.py` ห้ามprepare13ซ้ำ/รันmigration12เก่า/เอาoverlayเก่าท้ายสุดจนย้อนคำแก้ฐาน

งานต่อเมื่อผู้ใช้สั่งCh.14: ใช้ฐาน47,503นี้ append-only; เพิ่มC3410ในMIDGR,C3510ในFOREE+CAPITและCAPTL_BOS ตรวจACTOR/ไม่มีACTOR/ทุกตัวเลือก/ทุกแขนง/ศัพท์/คำลงท้าย/เลข/tags/ฟอนต์และsharedUIเหมือนเดิม ระวังCAPITเป็นassetที่ยังไม่มีในworkingชุดนี้ ต้องขยายเจ้าของแพ็ก/unionอย่างชัดเจน ไม่ย้ายทับไฟล์เดิม

คลิปผู้ใช้สำหรับบท/เสียง/ผู้พูดและเพศคงอยู่: https://www.youtube.com/watch?v=i4gD0mmj5vc ; https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU ; https://www.youtube.com/watch?v=bxrLsiU-QKk . เพิ่มCh.13 https://www.youtube.com/watch?v=sqDaAon-MlA ตรวจmetadataเท่านั้นในรอบนี้ ไม่อ้างฟังครบ; ขอบเขตเทียบcorpusกับ https://www.powerpyx.com/final-fantasy-7-vii-rebirth-chapter-13-where-angels-fear-to-tread-walkthrough/ และ https://game8.jp/ff7rebirth/596970
<!-- /chapter13-current -->
'''
    paths=[W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'FINAL-PARTS.md',W/'CONTEXT-FULL-READ.md']+sorted(W.glob('CHAPTER*-STATUS.md'))
    for p in paths:
        t=p.read_text('utf8');t=re.sub(r'<!-- chapter13-current -->.*?<!-- /chapter13-current -->\s*','',t,flags=re.S);title,_,rest=t.partition('\n');p.write_text(title+'\n\n'+block+'\n'+rest.lstrip('\n'),encoding='utf8')
    parts='\n'.join(f"- [{p['zip']}](E:/FF7RebrithModTH/Mod/Final/{p['zip']}) — {p['bytes']:,} bytes; SHA256 `{p['sha256']}`" for p in r['parts'])
    (W/'CHAPTER13-STATUS.md').write_text('# Chapter13 — Where Angels Fear to Tread\n\n'+block+'\n## ZIPปัจจุบัน\n\n'+parts+'\n',encoding='utf8')
    print('Finalized Ch13:853 added,47503 total;2 updated ZIPs,8 mounted; HANDOFF current')
if __name__=='__main__':main()
