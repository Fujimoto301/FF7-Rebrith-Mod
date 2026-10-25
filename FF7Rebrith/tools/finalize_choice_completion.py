"""Verify the published UI supplement and update current handoff paths."""
import hashlib,re
from pathlib import Path
from prepare_chapter9 import W,read,write
from assemble_ui_completion import fingerprint


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    cfg=read('reference/choice-completion-build.json');root='qa/choice-completion/'
    audit=read(root+'translation-audit.json');baseline=read(root+'baseline.json')
    sign=read(root+'editorial-signoff.json');proof=read(root+'proof.json')
    release=read('qa/final-parts/latest.json');mount=read('qa/final-parts/combined-mount-verification.json')
    ctx=read('qa/active-working-set.json');manifest=read(root+'working-assets.json')
    source_hash=digest(W/cfg['source']);total=audit['total_combined_text_records']
    assert ctx['choice_completion'] and ctx['combined_source']==cfg['source']
    assert source_hash==audit['source_sha256']==sign['combined_source_sha256']==proof['source_sha256']==read('qa/shared-dialogs/latest.json')['source_sha256']
    assert digest(W/'translations/choice-completion-th.json')==sign['translation_sha256']
    assert digest(W/'reference/choice-completion-source.json')==sign['inventory_sha256']
    assert sign['proof_visually_reviewed'] and sign['reviewed_proof_pages']==4
    for p,h in sign['reviewed_artifacts'].items():assert digest(W/p)==h,p
    assert len(proof['samples'])==32 and not any(s['clipped'] for s in proof['samples'])
    assert total==release['combined_text_records']==34589 and audit['added_UI_records']==1730
    assert audit['inventory_records']==7770 and audit['previous32859_text_and_ACTOR_preserved']
    assert audit['all16_font_assets_unchanged'] and audit['glyph_clusters']==711
    assert audit['prior_gender_particle_records_preserved']==952 and audit['new_gender_endings']==0
    assert audit['gender_particle_occurrences']=={'ครับ':651,'ค่ะ':198,'คะ':127}
    assert not any(audit[k] for k in ['missing','tag_mismatches','japanese_remaining'])
    assert mount['zip_count']==7 and mount['mod_files']==21 and mount['assets']==27
    assert mount['all_match_verified_combined_set'] and not mount['overlapping_assets']
    assert release['working_manifest']==root+'working-assets.json' and release['working_stage']==cfg['stage']
    revision=read(root+'recheck/current.json');review=read(root+'recheck/review.json')
    assert review['source_sha256']==source_hash and review['added_records']==687 and not review['corrected_records']
    assert review['previous33902_text_and_ACTOR_preserved']
    assert sign['recheck_proof_visually_reviewed'] and sign['reviewed_recheck_proof_pages']==4
    assert read(root+'recheck-proof.json')['source_sha256']==source_hash
    assert len(read(root+'recheck-proof.json')['samples'])==32
    final=W.parent/'Mod/Final';previous=read(Path(revision['snapshot'])/'qa/final-parts/latest.json')
    previous={p['zip']:p for p in previous['parts']};changed=[];unchanged=[];union={}
    assert {p.name for p in final.iterdir()}=={p['zip'] for p in release['parts']}
    for part in release['parts']:
        assert digest(final/part['zip'])==part['sha256']
        assert not union.keys()&part['assets'].keys();union.update(part['assets'])
        (unchanged if previous[part['zip']]['sha256']==part['sha256'] else changed).append(part['zip'])
    assert union==manifest and len(union)==27
    assert set(changed)=={'ThaiJP_Common_P.zip'} and len(unchanged)==6
    assert fingerprint()==revision['protected']
    for p,h in baseline['source_hashes'].items():assert digest(W/p)==h,p
    write(root+'release-verification.json',dict(text_records=total,new_UI_records=1730,inventory_records=7770,
        previous32859_text_and_ACTOR_preserved=True,source_sha256=source_hash,assets=27,glyph_clusters=711,
        ZIP_count=7,mod_files=21,updated_parts=changed,unchanged_parts=unchanged,
        all_parts_read_back_and_mounted_together=True,no_overlapping_assets=True,
        all16_font_assets_unchanged=True,previous976_gender_endings_preserved=True,
        source_and_installed_files_unchanged=True,installed=False,in_game_tested=False,
        recheck_added_UI_records=687,previous33902_text_and_ACTOR_preserved=True,
        backup=release['backups'],new_full_video_audio_review=False))
    base='E:/FF7RebrithModTH/FF7Rebrith/'
    table='\n'.join(f"| {p['zip']} | {len(p['assets'])} | {p['bytes']:,} |" for p in release['parts'])
    changed_text=', '.join(changed) or 'ไม่มี';unchanged_text=', '.join(unchanged) or 'ไม่มี'
    note=f'''<!-- choice-completion-current -->
## ล่าสุด: รีเช็คเก็บตกตัวเลือกและข้อความข้างเคียง — 19 ตุลาคม 2026

ส่วนนี้แทนพาธและยอดปัจจุบันในประวัติด้านล่าง **รีเช็คเพิ่ม 687 UI** เหนือชุดก่อน 33,902 รหัส คงข้อความและ ACTOR ชุดนั้นครบ รวมเก็บตกสะสม **1,730 UI** เหนือฐาน Ch.1–9 เดิม 32,859 รหัส ปัจจุบัน **34,589 รหัส / 27 assets / 711 clusters** ไม่เพิ่มบทพูดบทหลัง Ch.9 ตรวจคำถามและตัวเลือก scene *_sys ทุกไฟล์ พร้อม Resident และ namespace ข้างเคียงทั้งหมวด รวม inventory **7,770 รหัส** ไม่อ้างว่าเกมทั้งหมดไม่มีญี่ปุ่นหรือทดสอบทุกแขนงในเกมแล้ว

รอบรีเช็คพบเพิ่มตัวนับส่ง Chocograss/วัสดุ Johnny/จำนวนศัตรูที่กำจัด เงื่อนไขเลือกเป้าหมายและคำอธิบาย Gears and Gambits อีกชุดรหัส GC/GE/GF/GAN เงื่อนไขปลดล็อกสนาม ป้ายพื้นที่ Zack/ร้าน/กิจกรรม ชื่อ NPC บน UI คำอธิบายของเควสต์/ของสะสม/วิธีรับรางวัลและ World Intel ส่วนที่เหลือ เพิ่ม inverse scan จากข้อความ Resident ไม่มี ACTOR ทุกตัวที่ยังไม่แปล เพื่อจับหมวดที่ไม่ได้ลงทะเบียนเดิม ไม่ใช้เพียง regex คำถามชุดเก่า

แก้ภาพผู้ใช้: คำถามใช้ Cushion พร้อม พัก/ไม่พัก/แจ้งเมื่อไม่มี Cushion; HUD เป็น **รอยเท้าโจโกโบะ / จับ Piko ให้ได้**; คำถามบทสอน Queen's Blood พร้อม ใช่/ไม่ใช่ ยังครบ เก็บ native COMMAND และชื่อ UI อังกฤษตามเดิม

ฐานใหม่ **{base}translations/working-choice-completion-th.json**; config reference/choice-completion-build.json; map reference/choice-completion-cluster-map.json; stage staging/ThaiJP_ChoiceCompletion_Working; QA qa/choice-completion รายละเอียด [CHOICE-COMPLETION-STATUS.md]({base}CHOICE-COMPLETION-STATUS.md) ห้ามใช้ฐาน Ch.9 เดิมทับงานใหม่นี้

ฟอนต์ 16 assets และ map 711 ตัวตรงฐานก่อนรอบนี้ทุกไบต์ จึงคง ASCII/เลข/ไอคอนและ … ระดับล่างครบ 8 fonts คำลงท้ายเดิม 976 ครั้งใน 952 รหัสคงเดิม: ครับ 651 / ค่ะ 198 / คะ 127; NPC/nonparty 838 ครั้ง ไม่มีคำลงท้ายใหม่ ชายครับ หญิงค่ะบอกเล่า/คะคำถาม/นะคะ Unknown NPC ใช้กลาง ไม่อนุมานเพศจาก mma/mfa; คะ… ใน คะ…ครับ! ของ Militiaman คือเสียงติดอ่างที่ตรวจไว้ ไม่ใช่คำลงท้ายหญิง

Final มี 7 ZIP ล่าสุดแยกส่วน ต้องใช้ร่วมกัน อ่านกลับรวม 21 mod files / 27 assets ไม่มีซ้ำ อัปเดตรอบนี้: {changed_text} คงเดิม: {unchanged_text} Common ถือ Resident/ฟอนต์/TITLB และ **COSME เฉพาะ UI ตัวเลือก**; เมื่อทำบทที่ใช้ COSME ต้องย้ายทั้ง asset ไปเจ้าของ ZIP ใหม่ไม่ให้ซ้ำ สำรองนอก Final ไม่ติดตั้งและไม่แก้ต้นฉบับ/dist/ม็อดในเกม

ตรวจต้นฉบับ corpus 12 text assets/56,171 รหัส เทียบ inventory และ staging จริง ค้นอิสระคำถาม 1,641 รหัสกับปุ่มสั้น 315 รหัส แยก 194 ข้อความนอกหมวดเป็น NPC/บทภายหลัง/ข้อมูลศัตรู/demo พร้อมเหตุผล และ 10 choice-like keys ที่เหลือเป็น demo เท่านั้น ตรวจตัวเลขต่าง 46 รายการ และ proof จาก glyph จริง 8 หน้า/64 ตัวอย่างแล้ว ไม่ใช่ภาพเกมและไม่ได้ฟังวิดีโอครบใหม่

inverse scan พบ Resident ไม่มี ACTOR ที่ยังเป็นญี่ปุ่น 2,244 รหัส แยกรายรหัสแล้ว: ชื่อท่าโจมตีศัตรู 1,667 / ข้อมูลชีวประวัติและคำใบ้วิเคราะห์ศัตรู 544 / demo 29 / เสียง Moogle ไม่มี ACTOR 4 ไม่ใช่ตัวเลือกหรือชื่อเป้าหมายที่กำลังซ่อม ชื่อศัตรูและเมนูนำทางสมุดศัตรูครอบคลุมแยกไว้แล้ว ไม่มี residual UI ที่ยังไม่จัดประเภทใน Resident

ขั้นตอน: assemble_choice_completion.py → build_choice_completion.py --text-only (เมื่อไม่มี glyph ใหม่) → build_choice_completion.py --verify → audit_shared_dialogs.py (เรียก audit_choice_completion.py ด้วย) → preview_choice_completion.py และ --recheck แล้วดูภาพทั้ง 8 หน้า → ทบทวน signoff/numeric-review ผูก hash → publish_final_parts.py → verify_final_parts.py → finalize_choice_completion.py ห้ามรัน prepare ซ้ำ/เปลี่ยน index/ใช้ audit หรือ finalize บทเก่าทับ active context ใช้ recheck/current.json เป็น snapshot ก่อนรีเช็ค เก็บ baseline เดิมครบ หากติดตั้งชุดก่อนระหว่างรอบให้เทียบ fingerprint ตั้งแต่ต้นรีเช็ค ไม่ทับ snapshot เก่า

งานต่อไป: เมื่อทำบทใหม่ให้เริ่มฐานใหม่ข้างบน ตรวจ NPC ทั้งมี/ไม่มี ACTOR, shared/PHOTO/WORLD/CARDG และ namespace ข้างเคียง ทบทวนรายการพักตามสถานะปลดล็อก ตรวจคำถามพร้อมทุกปุ่ม รับ/ไม่รับ/ลองใหม่/ยกเลิก/ผลแพ้ชนะ/คำอธิบายและชื่อเป้าหมายทั้งหมวด เพิ่ม family ใน choice_completion.py/audit_shared_dialogs.py และรัน gate ก่อนแพ็กทุกครั้ง
<!-- /choice-completion-current -->

'''
    status=f'''# เก็บตกตัวเลือกและชื่อเควสต์ทั้งเกม

{note}
## ขอบเขตและหลักฐาน

รีเช็คเพิ่ม 687 UI รวม patch สะสม 1,730 รหัสจาก 887 แม่แบบที่แปลเอง ร่วมกับชื่อทางการ US และ reuse ที่ตรวจแล้ว คงบทพูด/ACTOR Ch.1–9 และ UI ชุดก่อน 33,902 รหัสทั้งหมด คง asset 8600-COSME สำหรับตัวเลือกเท่านั้น ยังไม่ได้แปลบทพูด Ch.10 เป็นต้นไป รอบนี้เก็บ World Intel รวม Detail_Clear/Detail_NA และคำอธิบาย/จดหมายบนหน้าของสะสมทั้งหมวดด้วย เป็น UI ที่อ่าน ไม่ใช่บทพูดฉากใหม่ ไม่ได้อ้างว่าแปลข้อความเกมทุกประเภทครบ

ตรวจ inventory 7,770: เดิม 5,854 + patch สะสม 1,730 + ต้นฉบับอังกฤษ/สัญลักษณ์ที่คงไว้ 186 รหัส มี hidden sentinel <> เดิม 2 รหัส และโน้ต C・/C・♯ ตรง US ไม่ใช่คำญี่ปุ่นตกหล่น ตรวจด้วยข้อความ รูปแบบ key และ inverse scan อิสระอีกชั้น รายการนอกหมวดมีเหตุผลรายรหัส ไม่ใช้เปอร์เซ็นต์ประมาณแทนหลักฐาน

JP เป็นหลัก ชื่อกิจกรรม/ตัวละคร/ศัตรู/ไอเทม/พื้นที่บน UI เป็นอังกฤษตาม US รหัสเดียวกัน ชื่อในบทพูดยังไทยตาม glossary: Aerith = เอริธ / ACTOR Aerith; ไม่แก้บทพูดเดิม เลขจำนวนจริงใช้อารบิก เช่น 第七→7, ひとつ→1, ふたり→2, ゼロ→0 และ壱弐参四→1–4; First Class เป็นชื่อยศทางการ; 1機ごと→แต่ละตัว คงเงื่อนไขต่อหน่วย แท็กและ metadata ตรวจตรงต้นฉบับทุกตัว

ภาพ proof ใช้ glyph จาก stage จริงทั้ง Large/Normal 8 หน้า/64 ตัวอย่าง แทน object=0 ด้วย Cushion เพื่อดูภาพเท่านั้น ไม่เขียนชื่อตายตัวแทนตัวแปรในเกม การตัดบรรทัด/ปุ่มใน proof เป็นแบบจำลอง ยังต้องทดสอบตำแหน่ง ความยาว การตัดบรรทัด และทุกแขนงในเกมจริงเมื่อมีคำสั่งติดตั้ง

## ไฟล์ส่งต่อ

พาธทุกแถวต่อจาก **{base}**:

| ใช้ทำอะไร | ไฟล์/โฟลเดอร์ |
| --- | --- |
| ฐานรวมปัจจุบัน | translations/working-choice-completion-th.json |
| เฉพาะ patch UI | translations/choice-completion-th.json |
| คำแปลแม่แบบ | translations/choice-completion/batch-00.json ถึง batch-11.json (รอบรีเช็ค 07–11) |
| US/reuse ที่ตรวจแล้ว | translations/choice-completion-automatic.json |
| inventory JP/US | reference/choice-completion-source.json |
| แม่แบบ 887 ข้อ ห้ามสลับ index | reference/choice-completion-templates.json |
| corpus JP; US ต้นฉบับ | reference/rebirth-jp-corpus.json; source/End/Content/Text/US/ |
| config/map/stage | reference/choice-completion-build.json; reference/choice-completion-cluster-map.json; staging/ThaiJP_ChoiceCompletion_Working |
| snapshot ก่อนรอบนี้ ห้ามเขียนทับ | qa/choice-completion/baseline.json; qa/choice-completion/revisions/ |
| snapshot รีเช็ค/รายการเพิ่ม 687 | qa/choice-completion/recheck/current.json; recheck/snapshots/; recheck/review.json |
| audit และรายรหัสเพิ่ม | qa/choice-completion/translation-audit.json; review-records.json |
| ค้นอิสระ/เหตุผลไม่ใช่ตัวเลือก | qa/choice-completion/independent-dispositions.json; independent-choice-key-dispositions.json; quest-namespace-dispositions.json; remaining-Resident-dispositions.json |
| ตัวเลขและ signoff ผูก hash | qa/choice-completion/numeric-review.json; editorial-signoff.json |
| ตรวจไฟล์/ภาพ | qa/choice-completion/verification.json; working-assets.json; proof.json; proof-1.png ถึง proof-4.png; recheck-proof.json; recheck-proof-1.png ถึง recheck-proof-4.png |
| เพศเดิมและหลักฐาน NPC | qa/chapter9/gender/records.json; qa/chapter9/gender/summary.json |
| ส่งมอบ | qa/choice-completion/release-verification.json; qa/final-parts/latest.json; qa/final-parts/combined-mount-verification.json; qa/active-working-set.json |
| เครื่องมือ | tools/choice_completion.py; prepare_choice_completion.py (ห้ามรันซ้ำ); extend_choice_completion.py (append เท่านั้น); assemble_choice_completion.py; build_choice_completion.py; audit_choice_completion.py; preview_choice_completion.py; finalize_choice_completion.py; audit_shared_dialogs.py; publish_final_parts.py; verify_final_parts.py |

Python **C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe** ตั้ง PYTHONUTF8=1 รันจาก {base} ทุกครั้ง หากแก้ข้อความต้อง assemble/build/verify/audit ดู proof ใหม่และทบทวน signoff hash ใหม่ หากเพิ่ม glyph ต้อง build เต็มกับ map append-only ห้ามใช้ text-only

## ZIP ล่าสุด

| ZIP | assets | bytes |
| --- | ---: | ---: |
{table}

ที่เก็บ **E:/FF7RebrithModTH/Mod/Final** ต้องใช้ทั้ง 7 ZIP ร่วมกัน สำรองก่อนทับที่ **{release['backups']}** ไม่ติดตั้ง รอบนี้อัปเดต {changed_text}; คงเดิม {unchanged_text} ตรวจอ่านกลับแล้ว 27 assets ไม่มี overlap

## งานที่ยังต้องทำ

แปลบทพูดบทถัดไปเมื่อผู้ใช้สั่ง เริ่มจากฐาน choice-completion นี้เพื่อไม่ทำ UI หาย ทบทวน deferred Ch.9 252 รหัสและบทก่อนหน้าตามสถานะจริง คงชื่อพูด/เพศ/คำลงท้ายตามหลักฐาน เมื่อใช้ COSME ให้จัดเจ้าของ asset ใหม่ทั้งไฟล์กับ Common โดยไม่ซ้ำ ยังต้องทดสอบ runtime ทุกตัวเลือกที่เกี่ยวข้อง/ทางแยก และตรวจเสียงผู้พูดที่หลักฐานยังไม่ชัด ไม่ยืนยันว่าไม่มีตกหล่นในเกม 100%

อ้างอิงบท/เสียง/เพศจากงานเดิม: [คลิปหลัก](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU), [ตอนแรก](https://www.youtube.com/watch?v=bxrLsiU-QKk) และ reference/plearngaming/glossary.json / reference/plearngaming/remake/decoded-corpus.json ลิงก์ส่งต่อจากบันทึกเดิม รอบนี้ไม่ได้ฟังใหม่ครบหรือมี timestamp ยืนยันทุก NPC
'''
    (W/'CHOICE-COMPLETION-STATUS.md').write_text(status,'utf-8')
    for path in [W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md']:
        text=path.read_text('utf-8');title,body=text.split('\n',1)
        body=re.sub(r'<!-- (?:chapter9|choice-completion)-current -->.*?<!-- /(?:chapter9|choice-completion)-current -->\s*','',body,flags=re.S)
        path.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    (W/'FINAL-PARTS.md').write_text(f'''# ZIP ล่าสุดแยกแต่ละส่วน

19 ตุลาคม 2026 หลังเก็บตกตัวเลือกและชื่อเควสต์: **{total:,} ข้อความ / 27 assets / 711 clusters / 7 ZIP / 21 mod files**

| ZIP | assets | bytes |
| --- | ---: | ---: |
{table}

ใช้ทั้ง 7 ZIP ร่วมกันใน **E:/FF7RebrithModTH/Mod/Final** เก็บล่าสุดของแต่ละส่วนเท่านั้น สำรองนอก Final อ่านกลับรวม 27 assets ไม่มีซ้ำ อัปเดตรอบนี้ {changed_text}; คงเดิม {unchanged_text} ฟอนต์ทั้ง 16 assets ไม่เปลี่ยน ไม่ได้ติดตั้งหรือทดลองในเกม

Common มี COSME เฉพาะตัวเลือก เมื่อแปลบทที่ใช้ COSME ให้ย้ายทั้งไฟล์ไป ZIP เจ้าของใหม่ไม่ซ้ำกับ Common

รายละเอียด [CHOICE-COMPLETION-STATUS.md]({base}CHOICE-COMPLETION-STATUS.md) และ [HANDOFF.md](E:/FF7RebrithModTH/HANDOFF.md)
''','utf-8')
    print('Finalized:',total,'records;',len(changed),'ZIPs updated;',len(unchanged),'unchanged; handoff saved')


if __name__=='__main__':main()
