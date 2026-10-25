"""Validate the published action fix and update the current handoff base."""
import re
from pathlib import Path
from prepare_chapter9 import W,read,write
from enemy_actions import Q,CFG,digest
from assemble_ui_completion import fingerprint


def main():
    cfg=read(CFG);b=read(Q+'baseline.json');a=read(Q+'translation-audit.json');sign=read(Q+'editorial-signoff.json')
    proof=read(Q+'proof.json');release=read('qa/final-parts/latest.json');mount=read('qa/final-parts/combined-mount-verification.json')
    ctx=read('qa/active-working-set.json');manifest=read(Q+'working-assets.json');h=digest(W/cfg['source'])
    assert h==a['source_sha256']==sign['source_sha256']==proof['source_sha256']==read('qa/shared-dialogs/latest.json')['source_sha256']
    assert ctx['combined_source']==cfg['source'] and ctx['enemy_actions'] and ctx['npc_recheck'] and ctx['choice_completion']
    assert sign['proof_visually_reviewed'] and sign['reviewed_proof_pages']==2
    for p,sha in sign['reviewed_artifacts'].items():assert digest(W/p)==sha,p
    assert len(proof['samples'])==16 and not any(r['clipped'] for r in proof['samples'])
    assert a['total_combined_text_records']==release['combined_text_records']==37830
    assert a['action_inventory_records']==1703 and a['new_action_labels']==1668
    assert a['previous36162_text_and_ACTOR_preserved'] and a['all16_fonts_unchanged']
    assert a['screenshot_English']=='Scorching Breath' and not any(a[k] for k in ['missing','japanese_remaining','tag_mismatches'])
    assert mount['zip_count']==7 and mount['mod_files']==21 and mount['assets']==27 and not mount['overlapping_assets']
    assert mount['all_match_verified_combined_set'] and release['working_stage']==cfg['stage'] and release['working_manifest']==Q+'working-assets.json'
    final=W.parent/'Mod/Final';old={p['zip']:p for p in read(Path(b['snapshot'])/'qa/final-parts/latest.json')['parts']}
    changed=[];unchanged=[];union={}
    assert {p.name for p in final.iterdir()}=={p['zip'] for p in release['parts']}
    for p in release['parts']:
        assert digest(final/p['zip'])==p['sha256'];assert not union.keys()&p['assets'].keys();union.update(p['assets'])
        (unchanged if p['sha256']==old[p['zip']]['sha256'] else changed).append(p['zip'])
    assert union==manifest and changed==['ThaiJP_Common_P.zip'] and len(unchanged)==6
    assert fingerprint()==b['protected']
    for p,sha in b['source_hashes'].items():assert digest(W/p)==sha,p
    assert read('qa/shared-dialogs/NPC-regression.json')['recovered_NPC_inventory_preserved']==8347
    write(Q+'release-verification.json',dict(text_records=37830,action_inventory_records=1703,new_action_labels=1668,
        previous36162_text_and_ACTOR_preserved=True,screenshot_English='Scorching Breath',source_sha256=h,
        all16_fonts_unchanged=True,glyph_clusters=711,ZIP_count=7,mod_files=21,assets=27,
        updated_parts=changed,unchanged_parts=unchanged,all_parts_read_back_and_mounted_together=True,
        no_overlapping_assets=True,source_and_installed_files_unchanged=True,installed=False,in_game_tested=False,backup=release['backups']))
    base='E:/FF7RebrithModTH/FF7Rebrith/'
    note=f'''<!-- enemy-actions-current -->
## ล่าสุด: ชื่อท่าศัตรูอังกฤษทั้งหมวด — 19 ตุลาคม 2026

ส่วนนี้แทนพาธ/ยอดปัจจุบันในประวัติด้านล่าง แก้ชื่อท่าในภาพ **灼熱ブレス → Scorching Breath** รหัส $bt_MidgarZolom_Flamethrower เทียบ US รหัสเดียวกัน ตรวจทั้ง Resident หมวด $bt_ และ $EN9000_10_ **1,703 ชื่อ/ป้ายการใช้ท่า** เพิ่ม **1,668 รหัส** (ญี่ปุ่น 1,667 + ป้ายไม่ทราบชื่อ ？？？？→??? ตาม US 1 รหัส) รักษาชื่ออังกฤษเดิม 35 รหัสและคำอธิบายไทย *_help เดิมทั้ง 12 รหัส ไม่เพิ่มบทพูดบทถัดไป

ฐานรวมปัจจุบัน **37,830 รหัส / 27 assets / 711 clusters** ที่ **{base}translations/working-enemy-actions-th.json**; config reference/enemy-actions-build.json; map reference/enemy-actions-cluster-map.json; stage staging/ThaiJP_EnemyActions_Working; QA qa/enemy-actions รายละเอียด [ENEMY-ACTIONS-STATUS.md]({base}ENEMY-ACTIONS-STATUS.md) ใช้ฐานนี้ต่อ ห้ามฐาน NPC/choice/Ch.9 เดิมทับงานใหม่

รอบนี้แทนป้ายในหมวดการใช้ท่าตาม US รหัสเดียวกันครบ รวมชื่อศัตรู/บอสจากทั้งเกมและข้อความแสดงสถานะใน namespace เดียวกัน คงชื่อทางการและเครื่องหมายตาม US รวม countdown One.../Two... และชื่อระดับ Crimson Breath I/II/III มีความต่างรูปแบบเลข JP/US 53 รายการ ตรวจ numeric-review.json แล้ว เป็นข้อความบน UI ไม่เปลี่ยนค่าพลัง/เวลา/จำนวนในระบบเกม บทพูดเดิม 36,162 รหัส/ACTOR และงานเก็บตก NPC/ตัวเลือกเดิมคงครบ

เปลี่ยนเฉพาะ Resident ใน **ThaiJP_Common_P.zip** ที่ E:/FF7RebrithModTH/Mod/Final ส่วน ZIP บททั้ง 6 คง hash เดิม อ่านกลับรวม 7 ZIP / 21 mod files / 27 assets ผ่านไม่มีซ้ำ สำรองชุด Common ก่อนแก้นอก Final ฟอนต์ทั้ง 16 assets และ map คงไบต์เดิม จึงรักษาระดับจุดไข่ปลา/native ASCII/เลข/ไอคอนและตำแหน่งไทยเดิม ไม่ติดตั้งหรือทดสอบในเกม

ตรวจถาวรก่อนส่งบทต่อไป: คง enemy_actions/npc_recheck/choice_completion ใน active context; audit_shared_dialogs.py เรียก gate หมวดชื่อท่าด้วย บทใหม่จะใช้ audit_enemy_actions_regression.py รักษา 1,703 ป้าย และ audit_npc_regression.py รักษา inventory NPC 8,347 รหัส ต้องขยาย inventory NPC ตามบท/การปลดล็อกจริง ตรวจมี/ไม่มี ACTOR ทุกสถานะ ตัวเลือกทุกปุ่มและชื่อเป้าหมายทั้งหมวด ทำ inverse scan ข้อความที่เหลือพร้อมเหตุผลรายรหัส ห้ามพักทั้ง namespace จากเลขสถานะเพียงอย่างเดียว

ขั้นตอนรอบนี้: enemy_actions.py --prepare (ครั้งเดียว) → enemy_actions.py (text-only) → --verify → audit_shared_dialogs.py → preview_enemy_actions.py และดู 2 หน้า → enemy_actions.py --signoff → publish_final_parts.py → finalize_enemy_actions.py เมื่อเป็นบทใหม่ต้องเพิ่ม gate/signoff ผูก source ใหม่ใน publisher ห้ามใช้ finalize บทเก่าทับ active context ห้าม prepare ซ้ำ

ข้อกำหนดชื่อ/เพศ/ฟอนต์และรายละเอียด NPC เดิมใน NPC-RECHECK-STATUS.md ยังใช้: ชื่อพูดไทยตาม glossary, ACTOR/UI ชื่อทางการอังกฤษ; ชายครับ หญิงค่ะ/คะ/นะคะ unknown ใช้กลาง ไม่เดาเพศจาก mma/mfa; Aerith เอริธ; คำลงท้ายเดิม 976 ครั้งไม่เปลี่ยน 8 fonts จุดไข่ปลาระดับล่างเหมือนเดิม Common ยังถือ COSME เฉพาะ UI เมื่อทำบทที่ใช้ COSME ให้ย้ายทั้ง asset ไปเจ้าของใหม่ไม่ให้ซ้ำ
<!-- /enemy-actions-current -->

'''
    table='\n'.join(f"| {p['zip']} | {len(p['assets'])} | {p['bytes']:,} |" for p in release['parts'])
    status=f'''# แก้ชื่อท่าศัตรูและบอสบน UI

{note}
## ไฟล์ส่งต่อ

พาธต่อจาก **{base}**:

| งาน | ไฟล์ |
| --- | --- |
| ฐานรวมล่าสุด | translations/working-enemy-actions-th.json |
| เฉพาะป้ายชื่อใหม่ 1,668 รหัส | translations/enemy-actions-th.json |
| inventory JP/US 1,703 รหัส | reference/enemy-actions-source.json |
| config/map/stage | reference/enemy-actions-build.json; reference/enemy-actions-cluster-map.json; staging/ThaiJP_EnemyActions_Working/ |
| snapshot ก่อนรอบนี้ ห้ามทับ | qa/enemy-actions/baseline.json; revisions/ |
| source/stage/tag/metadata/font audit | qa/enemy-actions/translation-audit.json; verification.json; working-assets.json |
| รูปแบบเลขชื่อทางการ 53 รายการ | qa/enemy-actions/numeric-review.json |
| ภาพ glyph จริง/ผลทบทวน | qa/enemy-actions/proof.json; proof-1.png; proof-2.png; editorial-signoff.json |
| ผลส่งจริง | qa/enemy-actions/release-verification.json; qa/final-parts/latest.json; combined-mount-verification.json |
| ฐานงาน NPC ก่อนหน้า | NPC-RECHECK-STATUS.md; qa/npc-recheck/ |

ภาพ proof เป็น glyph จริงจาก stage สำหรับ 8 ป้ายใน Large/Normal รวม 16 ตัวอย่าง 2 หน้า มี suffix ตัวเลขจำลองเพื่อดู native ASCII/ตัวเลข ไม่ใช่ภาพเกมหรือข้อความใหม่ในแพ็ก ยังต้องทดสอบชื่อท่าแสดงเหนือศัตรูในเกมจริงเมื่อผู้ใช้สั่งติดตั้ง

## ZIP ล่าสุด

| ZIP ใน E:/FF7RebrithModTH/Mod/Final | assets | bytes |
| --- | ---: | ---: |
{table}

สำรอง Common เดิม: `{release['backups']}` ทั้ง 7 ZIP ต้องใช้ร่วมกัน ไม่มี asset ซ้ำ รอบนี้ไม่แก้ไฟล์เกม/ต้นฉบับ/dist และไม่ติดตั้ง

## สิ่งที่ยังต้องทำ

ชื่อท่าที่อยู่ในสอง namespace นี้เทียบ US ครบ ไม่ใช่การรับรองว่าภาษาญี่ปุ่นทุกประเภททั้งเกมหมดแล้ว รายละเอียดวิเคราะห์/ชีวประวัติศัตรูที่ยังไม่ได้อยู่ในขอบเขตเดิม และบทหลัก/เควสต์บทถัดไปยังแยกไว้ งานตรวจ Ch.1 ก่อนหน้านี้เป็น read-only ไม่แก้คำแปลหรือ ZIP บทนั้น

ก่อนบทถัดไปคงทั้งชื่อท่า/UI/เก็บตก NPC เดิมครบ แล้วทบทวน deferred ตามบทจริงโดยใช้ฐานล่าสุดนี้ ห้ามเริ่มจาก working-npc-recheck หรือ working-choice-completion เพราะไม่มีชื่อท่ารอบนี้

เสียง/บท/เพศอ้างอิงจากงานก่อนหน้า: [คลิปหลัก](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk); reference/plearngaming/glossary.json; reference/plearngaming/remake/decoded-corpus.json รอบนี้เป็นชื่อ UI จากไฟล์ US ไม่ได้ฟังวิดีโอ/ทดสอบเสียงครบใหม่
'''
    (W/'ENEMY-ACTIONS-STATUS.md').write_text(status,'utf-8')
    for p in [W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md']:
        title,body=p.read_text('utf-8').split('\n',1)
        body=re.sub(r'<!-- enemy-actions-current -->.*?<!-- /enemy-actions-current -->\s*','',body,flags=re.S)
        # Keep the NPC instructions as historical evidence, explicitly superseded above.
        p.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    (W/'FINAL-PARTS.md').write_text(f'''# ZIP ล่าสุดแยกแต่ละส่วน

19 ตุลาคม 2026 หลังแก้ชื่อท่าศัตรู: **37,830 ข้อความ / 27 assets / 711 clusters / 7 ZIP / 21 mod files**

| ZIP | assets | bytes |
| --- | ---: | ---: |
{table}

ใช้ทั้ง 7 ZIP ร่วมกันใน **E:/FF7RebrithModTH/Mod/Final** ล่าสุดของแต่ละส่วนเท่านั้น รอบนี้อัปเดต Common ชื่อท่าอังกฤษตาม US รวม Scorching Breath ทั้ง 6 ZIP บทคง hash เดิม อ่านกลับรวมผ่านไม่มี asset ซ้ำ ฟอนต์เดิม ไม่ได้ติดตั้งหรือทดลองในเกม

รายละเอียด [ENEMY-ACTIONS-STATUS.md]({base}ENEMY-ACTIONS-STATUS.md) และ [HANDOFF.md](E:/FF7RebrithModTH/HANDOFF.md)
''','utf-8')
    print('Finalized enemy actions: 37830 records; Common updated; all6 chapter ZIPs unchanged')


if __name__=='__main__':main()
