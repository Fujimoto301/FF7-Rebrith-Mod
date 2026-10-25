"""Verify the delivered screenshot fixes and retain a clear continuation record."""
import hashlib
from assemble_chapter6 import W,read,write
from prepare_ch12_recheck import ROOT
from assemble_ui_completion import fingerprint

def main():
    cfg=read('reference/ch12-recheck-build.json');audit=read(ROOT+'/translation-audit.json')
    baseline=read(ROOT+'/baseline.json');release=read('qa/final-parts/latest.json')
    mounted=read('qa/final-parts/combined-mount-verification.json')
    prior=read(baseline['snapshot']+'/qa/final-parts/latest.json');old={p['zip']:p for p in prior['parts']}
    assert release['combined_text_records']==audit['total_combined_text_records']==24180
    assert mounted['assets']==24 and mounted['zip_count']==5 and mounted['mod_files']==15
    assert mounted['all_match_verified_combined_set'] and not mounted['overlapping_assets']
    changed=[]
    for p in release['parts']:
        assert hashlib.sha256((W.parent/'Mod/Final'/p['zip']).read_bytes()).hexdigest()==p['sha256']
        if p['sha256']!=old[p['zip']]['sha256']:changed.append(p['zip'])
    assert changed==['ThaiJP_Common_P.zip']
    assert {p.name for p in (W.parent/'Mod/Final').iterdir()}=={p['zip'] for p in release['parts']}
    assert fingerprint()==baseline['protected']
    proof=read(ROOT+'/proof.json');assert len(proof['ellipsis_comparison'])==16
    shared=read('qa/shared-dialogs/latest.json');assert not shared['missing'] and shared['combined_source']==cfg['source']
    gender=read('qa/gender-through-chapter6/summary.json');gender.update(source_records_scanned=24180,
      combined_source_sha256=hashlib.sha256((W/cfg['source']).read_bytes()).hexdigest(),
      recheck_basis='All 23,811 prior translations/ACTORs unchanged; all 330 new UI and39 opening narration lines checked neutral with no gendered endings.',
      reference_previous_records='qa/gender-through-chapter6/records.json',new_gendered_endings=0)
    write(ROOT+'/gender-summary.json',gender)
    write(ROOT+'/release-verification.json',dict(total_records=24180,new_UI_records=330,new_opening_recap_records=39,
      chapter1_2_previous_records_reviewed=4033,deferred_later_state_records=52,
      previous_23811_translations_and_all_ACTORs_preserved=True,cluster_map_674_unchanged=True,
      only_font_change='U+2026 y origin in8fonts, native full-stop baseline; all glyph pixels/spacing/other records preserved',
      only_changed_ZIP=changed[0],all_four_scene_ZIPs_unchanged=True,ZIP_count=5,mod_files=15,assets=24,
      all_archives_mounted_and_read_back=True,no_overlap=True,source_and_installed_files_unchanged=True,
      proof_visually_inspected=True,in_game_tested=False,installed=False,video_audio_reviewed_anew=False,
      backup=release['backups'],manifest='qa/final-parts/latest.json'))
    status='''# ตรวจ Ch.1–2 และแก้จุดไข่ปลา

อัปเดต 18 ตุลาคม 2026 (Asia/Bangkok) ตามภาพ113848/114018/161004/122833ของผู้ใช้

ชุดล่าสุดรวม **24,180รหัส / 24assets / 674glyph clusters / 5ZIP** รักษาคำแปลเดิม23,811รหัสและACTORทุกจุด เพิ่มUI330รหัสกับสรุปเปิดเกม39บรรทัด ไม่เริ่มCh.7 ไม่ติดตั้งเกม

## ผลตรวจและสิ่งที่แก้

- ลด **… U+2026** ทั้ง8ฟอนต์ให้ขอบล่างหมึกเสมอกับจุดASCII `.` จึงตรงแนวตัวอักษรไทยตามภาพตัวอย่าง เปลี่ยนเฉพาะค่าoriginYของglyphนี้ คงภาพจุด ระยะกว้าง ตัวASCII/เลข/ไอคอน/Thai glyph/textureทุกส่วนเดิม แก้ทั้งข้อความที่มีอยู่แล้ว80ตำแหน่งโดยไม่ต้องเปลี่ยนประโยค ไม่ได้เปลี่ยนU+2025ที่ยังไม่ใช้
- ต้นเหตุคำถามสอนการ์ดที่ตกหล่นคือ Resident `$minigame_cardgame_tutorial_Check` ไม่อยู่ในรหัสฉาก `*_sys` เก็บทั้งคำถาม “ต้องการดูบทสอนเล่น Queen's Blood หรือไม่?” ตัวเลือกใช่/ไม่ใช่ เมนูเด็ค ปุ่ม/ยอมแพ้/ลองใหม่/จัดการการ์ด/คำบรรยายเด็คและการแจ้งเตือนพร้อมกัน
- ตรวจUIทั้งหมวด362รหัส: เพิ่ม330 คงเดิม31รหัสภาษาอังกฤษ/ตัวเลข/สัญลักษณ์ และคงคำแปลเดิม1รหัส ครอบคลุมQueen's Blood, จับChocobo, Moogle Mischief, ชื่อคู่แข่ง/ร้าน/แจ้งเตือน และหลักสูตรฝึกต่อสู้ รวมตัวเลือกต่างสถานะ ไม่ตัดเฉพาะสิ่งที่เห็นในภาพ ชื่อเฉพาะ/ไอเทม/การ์ด/UIคงชื่อUSอังกฤษ รักษาแท็กJPและค่าตัวเลขโดยนับゼロเป็น0
- ตรวจรายการCh.1–2เดิมทั้งหมด4,085รหัส: ที่ใส่แล้ว4,033ครบ และ52รหัสสถานะภายหลังยังกันไว้พร้อมเหตุผลรายรหัส ตรวจcorpusอิสระอีก3,657candidateIDsตามกลุ่มฉาก/NPC/เควสต์ของCh.1–2 พบสรุปเปิดเกม39บรรทัดที่หลุดอยู่ในไฟล์TITLB จึงแปลเพิ่มครบ เนื้อหาพากย์โดยRed XIII ใช้ชื่อไทยในประโยคและถ้อยคำกลาง ฉัน/พวกเรา ไม่เติมคำลงท้ายระบุเพศ
- ช่วงท้ายCh.1/เปลี่ยนผ่านC1920และเนื้อเรื่องC2010 รวมNPC/บทแวดล้อม/ตัวเลือกระบบและshared rowsที่มีในscopeเดิมได้รับการตรวจซ้ำ ไม่พบJPเหลือในขอบเขตนี้ จำนวนcandidateอิสระไม่ใช่จำนวนบททั้งเกม และการไม่มีรหัสขาดไม่ได้พิสูจน์เงื่อนไขเรียกบททุกแบบจากการเล่นจริง
- ไม่เอาสถานะกลับGrasslandsหลังGoldSaucer/Nibel/GoldCup, Kalmระยะหลัง, เควสต์ทดแทนเมื่อBrodenไม่อยู่ หรือTifaแยกปาร์ตี้ช่วงหลัง มาปะปนกับCh.2 ดู52deferredเดิมและขอบเขตคัดsource ส่วนบท/UIนอกหมวดที่ระบุไม่ได้อ้างว่าเสร็จครบทั้งเกม
- คำลงท้ายเดิมยัง477ครั้งใน467รหัส (ครับ335/ค่ะ83/คะ59) UI/สรุปใหม่ไม่มีคำลงท้ายระบุเพศ ตรวจรักษาถ้อยคำเดิมครบ ไม่เดาเพศจากsuffix NPC และไม่ได้ดู/ฟังวิดีโอใหม่ครบ

## ไฟล์ปัจจุบัน

ฐาน **E:/FF7RebrithModTH/FF7Rebrith/**:

| หน้าที่ | พาธใต้ฐาน |
| --- | --- |
| ชุดรวมปัจจุบัน | translations/working-ch12-recheck-th.json |
| UIต้นฉบับJP/US/คำแปล | reference/ch12-recheck-ui-source.json, translations/ch12-recheck-ui-th.json |
| สรุปเปิดเกมJP/ไทย | reference/ch1-opening-recap-source.json, translations/ch1-opening-recap-th.json |
| สร้างคำแปล/รวม | tools/translate_ch12_recheck.py, translate_ch1_recap.py, assemble_ch12_recheck.py |
| config/glyph/punctuation | reference/ch12-recheck-build.json, ch12-recheck-cluster-map.json, dialogue-punctuation-policy.json |
| stage/active context | staging/ThaiJP_Ch12_Recheck_Working, qa/active-working-set.json |
| baselineห้ามทับ | qa/ch12-recheck/baseline.json และ revisions/ |
| ตรวจทวน4,033/52/3657 | qa/ch12-recheck/chapter1-2-records.json, deferred-later-states.json, corpus-scope-inventory.json |
| QAคำแปล/ฟอนต์/เพศ | qa/ch12-recheck/translation-audit.json, verification.json, punctuation-alignment.json, ui-review.json, opening-recap-review.json, gender-summary.json |
| proofจากglyphจริง(ไม่ใช่ในเกม) | qa/ch12-recheck/ellipsis-before-after.png, ui-proof-1.png ถึง ui-proof-3.png, proof.json |
| ตรวจshared UIถาวร | tools/audit_shared_dialogs.py, qa/shared-dialogs/latest.json |
| ชุดส่งมอบ | qa/ch12-recheck/release-verification.json, qa/final-parts/latest.json, combined-mount-verification.json |

## สร้างซ้ำและทำบทต่อไป

ใช้Python `C:/Users/godca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` ตั้ง `$env:PYTHONUTF8='1'` จากโปรเจกต์:

```text
tools/assemble_ch12_recheck.py
tools/build_chapter1.py --ch12-recheck-working --text-only
tools/verify_chapter1.py --ch12-recheck-working
tools/audit_ch12_recheck.py
tools/audit_shared_dialogs.py
tools/preview_ch12_recheck.py
tools/publish_final_parts.py
tools/finalize_ch12_recheck.py
```

เมื่อแก้ข้อความให้ดูภาพproofด้วย ถ้าเพิ่มglyphต้องbuildเต็มโดยเอา--text-onlyออก รักษาmapแบบappend-only อย่ารันprepare_ch12_recheck.pyซ้ำ อย่าใช้finalize/auditบทเก่าทับactive context สำหรับบทถัดไปใช้working-ch12-recheck-th.jsonเป็นฐานและคงการปรับU+2026หลังจัดแนวฟอนต์ รักษาข้อมูลเดิมทุกส่วน

**หลังจากนี้ต้องตรวจทุกบท:** สแกนshared Residentควบคู่ฉาก ไม่พึ่งเลขChapterหรือ*_sysอย่างเดียว ตรวจคำถามเริ่มบทสอน/ใช่ไม่ใช่/ยกเลิก/ย้อนกลับ/ลองใหม่/หน้าถัดไป/คำอธิบายและHUDของกิจกรรมที่เปิดในบทนั้นทั้งหมวด ใส่familyใหม่ในaudit_shared_dialogs.pyก่อนส่งงาน ตรวจellipsisเทียบจุดnativeทุกฟอนต์ ใช้ภาพproofและเมื่อมีภาพเล่นจริงให้เทียบอีกครั้ง ตรวจชื่อเฉพาะและเพศผู้พูด/ผู้ฟังตามกฎเดิม

## ZIP/ข้อจำกัด

Finalยังมี5ZIPล่าสุดเท่านั้น อัปเดตเฉพาะThaiJP_Common_P.zipซึ่งตอนนี้รวมResident+TITLBสรุปเปิดเกม+8fonts+8textures(18assets) อีก4ZIPบทคงเดิม ทั้ง5ต้องใช้ร่วมกัน อ่านกลับรวม15mod files24assetsผ่าน ไม่มีassetทับกัน Commonรุ่นก่อนสำรองไว้นอกFinalตามmanifest ไม่มีการติดตั้งหรือทดสอบในเกมจริง ไม่อ้างว่าดูวิดีโอหรือทวนทุกgameplay triggerแล้ว

อ้างอิงเสียง/ผู้พูดที่ผู้ใช้ให้ยังอยู่ในHANDOFF: [คลิปหลัก](https://www.youtube.com/watch?v=i4gD0mmj5vc), [เพลย์ลิสต์เสียงญี่ปุ่น](https://www.youtube.com/playlist?list=PL0w8Te9HdCC5PCW055occRACeikVNdnoU) ใช้JPดิบเป็นต้นฉบับ คำบรรยายอัตโนมัติไม่ใช่หลักฐานว่าได้ฟังแล้ว
'''
    (W/'CH12-RECHECK-STATUS.md').write_text(status,'utf-8')
    table='\n'.join(f"| `{p['zip']}` | {len(p['assets'])} | {p['bytes']:,} |" for p in release['parts'])
    (W/'FINAL-PARTS.md').write_text(f'''# ZIP ล่าสุดแยกแต่ละส่วน

18 ตุลาคม 2026 หลังตรวจCh.1–2/แก้จุดไข่ปลา: **24,180ข้อความ / 24assets / 5ZIP / 15mod files**

| ZIP | assets | bytes |
| --- | ---: | ---: |
{table}

ใช้ทั้ง5ZIPร่วมกันจาก `E:/FF7RebrithModTH/Mod/Final` ล่าสุดของแต่ละส่วนเท่านั้น รอบนี้อัปเดตเฉพาะCommon ซึ่งมีResident+TITLBสรุปเปิดเกม+8fonts+8textures อีก4ZIPบทไม่เปลี่ยน ต้นฉบับ/dist/ม็อดในเกมไม่เปลี่ยน ไม่ได้ติดตั้งหรือทดสอบเล่นจริง อ่านกลับรวม24assetsผ่านไม่มีทับกัน สำรองCommonเก่านอกFinalตามqa/final-parts/latest.json

รายละเอียดและขั้นตอนล่าสุด: [CH12-RECHECK-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CH12-RECHECK-STATUS.md) และ [HANDOFF.md](E:/FF7RebrithModTH/HANDOFF.md)
''','utf-8')
    note='''<!-- ch12-current -->
## ชุดล่าสุดหลังตรวจ Ch.1–2 และแก้จุดไข่ปลา — 18 ตุลาคม 2026

ส่วนนี้แทนพาธ/ยอด/ขั้นตอนปัจจุบันทุกส่วนด้านล่าง รวม24,180รหัส24assets674clusters รักษางานCh.1–6เดิม23,811รหัส/ACTORครบ เพิ่ม330UI+39สรุปเปิดเกมTITLB ลด…U+2026ให้เสมอจุดASCII.ใน8fontsโดยเปลี่ยนเฉพาะoriginY พิกเซล/ระยะ/ASCII/ไอคอน/Thai/textureเดิมไม่เปลี่ยน ตรวจCh.1–2เดิม4,033รหัสครบ กัน52สถานะภายหลังไว้ ไม่มีJPเหลือในกลุ่มฉากที่คัดและUI362รหัสที่ตรวจ

ชุดรวมปัจจุบัน **E:/FF7RebrithModTH/FF7Rebrith/translations/working-ch12-recheck-th.json**; stage **staging/ThaiJP_Ch12_Recheck_Working**; glyph **reference/ch12-recheck-cluster-map.json**; config **reference/ch12-recheck-build.json**; QA **qa/ch12-recheck** ดู [CH12-RECHECK-STATUS.md](E:/FF7RebrithModTH/FF7Rebrith/CH12-RECHECK-STATUS.md) สำหรับไฟล์/ขอบเขต/ข้อจำกัดทั้งหมด

ขั้นตอนปัจจุบัน assemble_ch12_recheck.py → build_chapter1.py --ch12-recheck-working --text-only(หากglyphไม่เพิ่ม) → verify_chapter1.py --ch12-recheck-working → audit_ch12_recheck.py → audit_shared_dialogs.py → preview_ch12_recheck.py(ดูภาพ) → publish_final_parts.py → finalize_ch12_recheck.py ห้ามprepareซ้ำ/เขียนทับsnapshot/ใช้auditหรือfinalizeบทเก่าทับcontext

**คำสั่งถาวรใหม่:** ทุกบทต้องตรวจshared Residentด้วย ทั้งคำถามบทสอน ใช่/ไม่ใช่ ยกเลิก ลองใหม่ การเลือกกิจกรรม เมนูย่อย คำอธิบาย/HUDและทางเลือกต่างสถานะทั้งหมวด เพิ่มfamilyใหม่ลงaudit_shared_dialogs.py ไม่อาศัย*_sysหรือเลขChapterอย่างเดียว ตรวจellipsisเทียบจุดnativeทุกฟอนต์ ใช้ชุดล่าสุดนี้เป็นฐานบทถัดไป คงproper-name/เลขอารบิก/คำลงท้ายตามเพศเดิม UnknownNPCกลาง รวมคำลงท้ายจริงยัง477ครั้งไม่มีเพิ่มจากUI/สรุปใหม่

Finalยัง5ZIP ต้องใช้ร่วมกันทั้งหมด อัปเดตเฉพาะCommon(18assetsเพิ่มTITLB) ZIPบททั้ง4คงเดิม อ่านกลับรวม24assetsไม่มีทับกัน สำรองนอกFinal ไม่ติดตั้ง ไม่ทดสอบเกมจริง ไม่อ้างว่าทวนวิดีโอใหม่ครบ บทCh.7ยังไม่เริ่ม เอกสารด้านล่างเป็นประวัติก่อนรอบนี้
<!-- /ch12-current -->

'''
    for p in [W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'CHAPTER6-STATUS.md']:
        text=p.read_text('utf-8');title,body=text.split('\n',1)
        if '<!-- ch12-current -->' in body:
            start=body.index('<!-- ch12-current -->');end=body.index('<!-- /ch12-current -->')+len('<!-- /ch12-current -->')
            body=body[:start]+body[end:]
        p.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    print('Verified latest5ZIPs/24assets; Common only updated; handoff/current instructions and ongoing shared-dialog gate saved.')

if __name__=='__main__':main()
