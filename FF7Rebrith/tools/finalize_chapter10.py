"""Verify the published split release, then record the new handoff baseline."""
import re
from pathlib import Path
from prepare_chapter9 import W,read,write
from audit_chapter10 import CFG,Q,digest
from assemble_ui_completion import fingerprint

def main():
    cfg=read(CFG);a=read(Q+'translation-audit.json');b=read(Q+'baseline.json');sign=read(Q+'editorial-signoff.json');release=read('qa/final-parts/latest.json');mount=read('qa/final-parts/combined-mount-verification.json');ctx=read('qa/active-working-set.json');manifest=read(Q+'working-assets.json');h=digest(W/cfg['source'])
    assert h==a['source_sha256']==sign['source_sha256']==read(Q+'proof.json')['source_sha256']==read('qa/shared-dialogs/latest.json')['source_sha256']
    assert ctx['combined_source']==cfg['source'] and all(ctx[k] for k in ['chapter10','enemy_actions','npc_recheck','choice_completion'])
    for p,sha in sign['reviewed_artifacts'].items():assert digest(W/p)==sha,p
    assert a['new_records']==2717 and a['total_combined_text_records']==release['combined_text_records']==40547
    assert sign['reviewed_proof_pages']==5 and sign['proof_visually_reviewed']
    assert not any(a[k] for k in ['missing','japanese_remaining_in_scope','tag_mismatches'])
    assert mount['zip_count']==8 and mount['mod_files']==24 and mount['assets']==27 and not mount['overlapping_assets'] and mount['all_match_verified_combined_set']
    assert release['working_stage']==cfg['stage'] and release['working_manifest']==Q+'working-assets.json'
    final=W.parent/'Mod/Final';old={p['zip']:p for p in read(Path(b['snapshot'])/'qa/final-parts/latest.json')['parts']};changed=[];unchanged=[];union={}
    assert {p.name for p in final.iterdir()}=={p['zip'] for p in release['parts']}
    for p in release['parts']:
        assert digest(final/p['zip'])==p['sha256'];assert not union.keys()&p['assets'].keys();union.update(p['assets'])
        (unchanged if old.get(p['zip'],{}).get('sha256')==p['sha256'] else changed).append(p['zip'])
    assert union==manifest and changed==['ThaiJP_Chapter1_P.zip','ThaiJP_Chapter10_P.zip','ThaiJP_Common_P.zip'] and len(unchanged)==5
    assert fingerprint()==b['protected']
    for p,sha in b['source_hashes'].items():assert digest(W/p)==sha,p
    write(Q+'release-verification.json',dict(text_records=40547,new_records=2717,previous37830_text_and_ACTOR_preserved=True,glyph_clusters=716,ZIP_count=8,mod_files=24,assets=27,updated_parts=changed,unchanged_parts=unchanged,all_parts_read_back_and_mounted_together=True,no_overlapping_assets=True,source_and_installed_files_unchanged=True,installed=False,in_game_tested=False,source_sha256=h,backup=release['backups']))
    base='E:/FF7RebrithModTH/FF7Rebrith/'
    note=f'''<!-- chapter10-current -->
## ล่าสุด: Chapter 10 — Watcher of the Vale — 20 ตุลาคม 2026

ส่วนนี้แทนข้อมูลฐานปัจจุบันทั้งหมดในประวัติด้านล่าง เพิ่ม **2,717 รหัส / 2,617 แม่แบบ** รวม **40,547 รหัส / 27 assets / 716 clusters** รักษาฐานเดิม 37,830 ข้อความและ ACTOR ครบ ไม่เริ่ม Ch.11

ฐานล่าสุด **{base}translations/working-through-chapter10-th.json**; patch translations/chapter10-th.json; config reference/chapter10-build.json; map reference/through-chapter10-cluster-map.json; stage staging/ThaiJP_ThroughChapter10_Working; QA qa/chapter10 รายละเอียด [CHAPTER10-STATUS.md]({base}CHAPTER10-STATUS.md) ห้ามใช้ฐาน enemy-actions/NPC/choice/Ch.9 เดิมทับงาน Ch.10 และห้าม prepare_chapter10 ซ้ำ

ทำบทหลัก Cosmo Canyon/หอดูดาว/พิธีส่งคืนสู่ดวงดาว/บททดสอบ Nanaki/เผ่า Gi/ก่อนออกจากหุบเขา และ Zack ใน MIDGR; เควสต์ Bonds of Trust, Absence of a Sign, From Whence Life Flows, Promises to Keep; โปรโตเรลิก Gears and Gambits ครบ4การทดสอบและบทอวาแลนช์; NPC Cosmo649รหัสครบทุกสถานะ รวมไม่มี ACTOR597รหัส และ MIDGR_NPC10อีก185รหัส รวม NPC ใหม่834รหัส/ไม่มี ACTOR771รหัส; Resident238รหัสรวม Chadley/MAI/World Intel/PHOTO/CARDG_QST15 ทั้ง3คู่แข่ง

ตรวจ inventory NPC พื้นที่ที่เยือนรวม5,638รหัส ไม่มี ACTOR4,989รหัส รักษา inventory เก็บตก NPC เดิม8,347รหัส และชื่อท่าศัตรูอังกฤษ1,703ป้ายครบ ตรวจคำถาม/ทุกตัวเลือกทั้งfamily7,218รหัส รวมบทสอน/ค่ายพัก/ชื่อเควสต์/เกมย่อยตาม gate เดิม ไม่ตรวจเฉพาะฉากหลักหรือเฉพาะ *_sys สแกนย้อนทุกข้อความญี่ปุ่นที่ยังเหลือในไฟล์ฉากที่เยือนและแยกเหตุผลรายรหัส2,774รายการ ส่วนของ Cosmoเหลือเฉพาะเควสต์ใหม่ Ch.12 Victim of Circumstance66รหัส ไม่พัก NPC_30 ทั้งหมวด

คำลงท้ายรวม **1,195ครั้งใน1,170รหัส: ครับ791 / ค่ะ255 / คะ149** รวม NPC/nonparty1,011ครั้ง รักษา976ครั้งเดิมครบ เพิ่ม219ครั้งตามหลักฐานผู้พูด ตรวจไม่พบสลับเพศ/ผู้พูดที่ยังไม่มีหลักฐาน ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ Unknown NPC ใช้กลาง ไม่เดาจาก mma/mfa Wedgeป้ายชื่อชัดใช้ชาย ส่วน???ใช้กลาง Aerithพูด **เอริธ**, Zack **แซ็ก**, Cait Sith **เค็ตชี**, Gongaga **กอนกาก้า**, SOLDIER **โซลเจอร์**, Potion **โพชั่น** ป้ายผู้พูด/UI อังกฤษตาม US รหัสเดียวกัน คง Gz เป็นหน่วยวัดในคำถามตามต้นฉบับ

เพิ่ม5clusters งึ/บื/บู๊/ว็/อู แบบappend-only รักษา711assignment/metricsเดิมทั้ง8fonts และnativeASCII/เลข/ไอคอนพิกเซลเดิม คงระดับจุดไข่ปลา…ต่ำเท่าจุดเต็ม ไทยเก่าอาจมีความต่างจากการบีบอัดBC5เล็กน้อยหลังrepack ไม่อ้างว่าพิกเซลไทยเดิมเหมือนทุกตัว ดูproof glyphจริง5หน้า รวมคำถามและทุกปุ่ม4ชุดแล้ว ตรวจความต่างตัวเลข26รายการพร้อมเหตุผล

Final มี **8 ZIPล่าสุดแยกส่วน** ต้องใช้ร่วมกัน เพิ่ม **ThaiJP_Chapter10_P.zip** ถือ COSMEทั้งasset ย้ายออกจากCommonไม่ซ้ำ อัปเดต **ThaiJP_Chapter1_P.zip** เพราะMIDGRใช้ร่วมกับZackCh.10 และ **ThaiJP_Common_P.zip** เพราะResident/ฟอนต์ อีก5ZIPคงhashเดิม อ่านกลับรวม24modfiles/27assetsไม่มีซ้ำ สำรองนอกFinal ไม่ติดตั้ง/ไม่ทดลองในเกม/ไม่อ้างฟังวิดีโอครบใหม่ ต้นฉบับ/dist/ไฟล์เกมคงเดิม

ขั้นตอน: assemble_chapter10.py → build_chapter10.py(เต็มเมื่อมีglyphใหม่; --text-onlyเมื่อmapคงเดิม) → --verify → audit_shared_dialogs.py(รวมaudit_chapter10.py, regressionชื่อท่า/NPCเดิม) → audit_chapter10_glyphs.py → preview_chapter10.pyและดู5หน้า → signoff_chapter10.py → publish_final_parts.py → finalize_chapter10.py บทต่อไปต้องขยายgate/signoffของsourceใหม่ก่อนแพ็ก คงทุกflagในactive context ไม่รันaudit/finalizeบทเก่าทับcontext
<!-- /chapter10-current -->

'''
    table='\n'.join(f"| {p['zip']} | {len(p['assets'])} | {p['bytes']:,} |" for p in release['parts'])
    status=f'''# Chapter 10 — Watcher of the Vale

{note}
## ไฟล์สำหรับทำต่อ

พาธทั้งหมดในตารางต่อจาก **{base}**:

| งาน | ไฟล์ |
| --- | --- |
| ฐานรวมล่าสุด / เฉพาะบทใหม่ | translations/working-through-chapter10-th.json / translations/chapter10-th.json |
| คำแปลแม่แบบ | translations/chapter10/batch-00.json ถึง batch-14.json และ reused-lines.json |
| ต้นฉบับ JP/US และดัชนีคงที่ | reference/chapter10-source.json / chapter10-templates.json / chapter10-scope.json |
| นอกขอบเขตใหม่ Ch.12 | reference/chapter10-deferred.json |
| config / map | reference/chapter10-build.json / through-chapter10-cluster-map.json |
| staging ที่ตรวจแล้ว | staging/ThaiJP_ThroughChapter10_Working/ |
| snapshot ก่อนรอบนี้ ห้ามเขียนทับ | qa/chapter10/baseline.json / revisions/ |
| source/stage/metadata/tag/glyph | qa/chapter10/translation-audit.json / verification.json / working-assets.json / old-glyph-regression.json |
| NPC / ตัวเลือก / รายการยังไม่แปล | qa/chapter10/NPC-inventory.json / choice-review.json / visited-scene-residual-dispositions.json |
| บทตรวจละเอียด / ตัวเลข | qa/chapter10/review-records.json / numeric-review.json / numeric-decisions.json |
| เพศและคำลงท้าย | qa/chapter10/gender/records.json / summary.json |
| ภาพฟอนต์จริงและการรับรอง | qa/chapter10/proof-1.png ถึง proof-5.png / proof.json / editorial-signoff.json |
| ผลชุดส่งจริง | qa/chapter10/release-verification.json / qa/final-parts/latest.json / combined-mount-verification.json |

## ขอบเขตที่เพิ่ม

- COSME เพิ่ม2,162รหัส: C2910/C3010, CHADL_QST05, COSME_QST01–04, CSMOC_NPC10ทุกสถานะ, GIZOK_BOS14 บทต่อสู้ รวมอวาแลนช์/เวดจ์และเรื่องราวเผ่ากี
- MIDGR เพิ่ม317รหัส: C3010ของZack132 + MIDGR_NPC10ทั้งหมด185 ไม่เริ่มC3110/C3210หรือบทZackช่วงหลัง
- Resident เพิ่ม238รหัส: WORLD_CDV02_0600/WORLD_MGV01_0600, PHOTO_QST06, PHOTO_QST00ระดับ600, PHOTO_QST03โรงแรมJohnnyที่ปรับปรุงแล้ว, CARDG_QST15 Robin/Bernard/Ka'dina, Chadleyบอกทาง/ชัยชนะBahamut Arisen/การกลับเยือนCosmo
- เควสต์ใหม่Ch.12 COSME_QST05ยังไม่เพิ่ม66บทพูด คำถามUIบางส่วนมีอยู่ก่อนแล้วจากงานUIทั้งเกม ตรวจไม่ทับและไม่เอาUIที่แปลแล้วมานับเป็นบทพูดใหม่

## ตรวจแล้วและข้อจำกัด

อ่านย้อนต้นฉบับทุกIDในassetที่เปลี่ยน เทียบข้อความdecode stagingกับsourceรวม40,547รหัส คงทุกID/ลำดับ/tag/metadataที่ไม่ใช่ACTORและข้อความนอกscope คำลงท้ายตรวจทุกoccurrenceทั้งชุดด้วยหลักฐานชื่อผู้พูด/บริบทเดิม ไม่อนุมานเพศจากmodelcode บทไม่มีป้ายชื่อใช้กลาง จำนวนNPC5,638เป็นหมวด *_NPC_* พื้นที่ที่เยือน+MIDGR10 ไม่ใช่ยอดเดียวกับinventoryเก็บตกเดิม8,347ซึ่งรวมเควสต์และsharedNPCด้วย

ดูproofจริง5หน้าแล้วเป็นเพียงการวางglyph/ตัดบรรทัดจำลอง ไม่ใช่ภาพเกมหรือการยืนยันว่าขนาดซับทุกฉากพอดี ยังต้องทดลองในเกมและเล่นตัวเลือกทุกแขนงเมื่อมีการติดตั้งที่ผู้ใช้สั่ง ตัวเลือกเดิมไม่ได้แปลซ้ำแต่ตรวจทั้งfamilyและอ่านกลับจากแพ็กแล้ว ไม่กล่าวว่าไม่มีตกหล่นทั้งเกม100%

ตัวเลข26ความต่างเกิดจากแปลงตัวสะกด/คันจิเป็นเลขอารบิก เช่นเซคเตอร์7/8/5,ふたり→2,千年→1000,40と5→45,7000飛び83→7083 เก็บเหตุผลทุกIDในnumeric-decisions.json คงGzจากต้นฉบับ เป็นหน่วยที่ตัวละครถามว่าอ่านอย่างไร ต้นฉบับแม่แบบ1045มี『別；ユフィ！』ละเฉพาะannotation別；และแปลเสียงเรียกยุฟฟี่

## ZIPล่าสุดใน E:/FF7RebrithModTH/Mod/Final

| ZIP | assets | bytes |
| --- | ---: | ---: |
{table}

สำรองก่อนแก้: `{release['backups']}` ใช้8ZIPร่วมกัน แต่ละZIPมีเฉพาะpak/utoc/ucas3ไฟล์ พร้อมใบอนุญาตฟอนต์ในZIPcomment Commonถือ18assetsคือResident/TITLBและฟอนต์16assets บทCh.10ถือCOSME1asset บทCh.1ถือMIDGR/NIBLEรวมZackช่วงCh.10 ไม่มีติดตั้ง

## สิ่งที่ต้องทำต่อ

รอคำสั่งเริ่มCh.11 ใช้ฐานล่าสุดนี้ ทบทวนบท/เควสต์/โปรโตเรลิกที่เพิ่งปลดล็อก พร้อมNPCกลับเยือนทุกพื้นที่ อย่าพักทั้งnamespaceเพราะเลขสถานะหรือคำว่าreturn ตรวจPHOTO/WORLD/CARDG/MOGLEและทุกคำถาม/ตัวเลือก/HUD/ชื่อเควสต์/ชื่อสถานที่ ตรวจinverse scanทุกข้อความที่เหลือและลงเหตุผลรายID ขยายgateCh.10สำหรับsourceบทใหม่และpublisherให้ตรวจsignoffใหม่ก่อนแพ็ก ห้ามปิดchapter10/enemy_actions/npc_recheck/choice_completionเพื่อข้ามgate

## แหล่งบท เสียง และเพศ

- [คลิปหลัก PlearnGaming](https://www.youtube.com/watch?v=i4gD0mmj5vc)
- [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU)
- [ตอนแรกของชุดอ้างอิง](https://www.youtube.com/watch?v=bxrLsiU-QKk)
- glossaryเดิม: {base}reference/plearngaming/glossary.json และ reference/plearngaming/remake/decoded-corpus.json

ใช้JPเป็นหลักและUSรหัสเดียวกันประกอบการตีความ/ป้ายชื่อ รอบนี้ไม่อ้างว่าฟังทุกวิดีโอหรือทุกNPCใหม่ แหล่งตรวจเงื่อนไขเควสต์: [Ch.10](https://www.powerpyx.com/final-fantasy-7-vii-rebirth-chapter-10-watcher-of-the-vale-walkthrough/), [Cosmo Intel](https://www.powerpyx.com/final-fantasy-7-vii-rebirth-cosmo-canyon-all-world-intel-locations/), [From Whence Life Flows](https://www.powerpyx.com/final-fantasy-7-vii-rebirth-from-whence-life-flows-walkthrough/), [Promises to Keep](https://www.powerpyx.com/final-fantasy-7-vii-rebirth-promises-to-keep-walkthrough/), [เควสต์และบทปลดล็อก](https://www.powerpyx.com/final-fantasy-7-vii-rebirth-all-side-quest-locations/)
'''
    (W/'CHAPTER10-STATUS.md').write_text(status,'utf-8')
    for p in [W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md']:
        title,body=p.read_text('utf-8').split('\n',1);body=re.sub(r'<!-- chapter10-current -->.*?<!-- /chapter10-current -->\s*','',body,flags=re.S)
        p.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    (W/'FINAL-PARTS.md').write_text(f'''# ZIPล่าสุดแยกแต่ละส่วน

20ตุลาคม2026 หลังCh.10: **40,547ข้อความ / 27assets / 716clusters / 8ZIP / 24modfiles**

| ZIP | assets | bytes |
| --- | ---: | ---: |
{table}

ใช้ทั้ง8ZIPร่วมกันใน **E:/FF7RebrithModTH/Mod/Final** เก็บเฉพาะล่าสุดของแต่ละส่วน เพิ่มChapter10 อัปเดตChapter1(ฉากZackในMIDGRใช้ร่วมกัน)และCommon(Resident/ฟอนต์) อีก5ZIPคงhashเดิม COSMEย้ายจากCommonไปChapter10ทั้งasset อ่านกลับทุกZIPรวม27assetsผ่านไม่มีซ้ำ ไม่ได้ติดตั้งหรือทดลองในเกม

รายละเอียด [CHAPTER10-STATUS.md]({base}CHAPTER10-STATUS.md) และ [HANDOFF.md](E:/FF7RebrithModTH/HANDOFF.md)
''','utf-8')
    print('Finalized Chapter10:40547records,8latestZIPs,24modfiles,27assets; source/game/dist unchanged')

if __name__=='__main__':main()
