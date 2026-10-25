"""Two source-ID-specific, user-approved corrections over the current Ch1-10 release."""
import copy, hashlib, re, shutil, sys, uuid
from pathlib import Path
from prepare_chapter9 import W, read, write, txtres
from assemble_ui_completion import fingerprint

Q='qa/chapter4-door-fix/'
ASSET='End/Content/Text/JP/8200-JUNOE_TxtRes.uasset'
KEYS=('$C2120_MAIN_2700_0500_00_tif','$C2120_MAIN_2900_0100_00_red')
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def active(): return (W/Q/'baseline.json').exists()
def matches(a,k,before,after):
    from pronoun_context import matches as pronoun_matches
    if pronoun_matches(a,k,before,after):return True
    from context_full_read import matches as full_matches
    if full_matches(a,k,before,after):return True
    from context_recheck import matches as context_matches
    if context_matches(a,k,before,after):return True
    from chapter4_choice_fix import active as followup_active,TARGETS,matches as followup_matches
    if followup_active() and a==ASSET and k in TARGETS:return followup_matches(a,k,before,after)
    return active() and a==ASSET and k in KEYS and before=='ถามสิ' and after=='เชิญ'

def verify_protected(historical):
    current=fingerprint()
    if not active():
        assert current==historical
        return
    # The user installed the last release between turns. Preserve that current
    # installation exactly; never replace historical manifests with new hashes.
    from chapter4_choice_fix import active as followup_active,Q as FOLLOWUP_Q
    expected=read((FOLLOWUP_Q if followup_active() else Q)+'baseline.json')['protected']
    from context_recheck import active as context_active,Q as CONTEXT_Q
    if context_active():expected=read(CONTEXT_Q+'baseline.json')['protected']
    from context_full_read import active as full_active,Q as FULL_Q
    if full_active():expected=read(FULL_Q+'baseline.json')['protected']
    from verify_installed_session import verify
    verify(expected)
    dist_root=str(W/'dist')
    assert {p:h for p,h in historical.items() if p.startswith(dist_root)}=={p:h for p,h in current.items() if p.startswith(dist_root)},'Distribution changed'

def prepare():
    assert not active(),'Keep the immutable door-fix baseline'
    ctx=read('qa/active-working-set.json'); old=read(ctx['combined_source'])
    for k in KEYS: assert old['assets'][ASSET]['entries'][k]=='ถามสิ'
    snap=W/Q/'revisions'/uuid.uuid4().hex
    paths=[ctx['combined_source'],ctx['manifest'],ctx['cluster_map'],'qa/active-working-set.json',
        'qa/final-parts/latest.json','translations/chapter4/reused-lines.json','translations/chapter4-th.json',
        'reference/chapter4-ui-overrides.json','qa/chapter10/editorial-signoff.json',
        'qa/chapter10/continue-review/release-verification.json']
    for rel in paths:
        dest=snap/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,dest)
    write(Q+'baseline.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint(),
          hashes={p:digest(snap/p) for p in paths}))
    rows=[r for r in read('reference/chapter4-source.json') if r['id'] in KEYS]
    assert len(rows)==2 and all(r['asset']==ASSET and r['Text']=='どうぞ' for r in rows)
    write(Q+'source-review.json',dict(records=[dict(r,before='ถามสิ',after='เชิญ',
        decision='Response at the door: どうぞ invites entry/acknowledges the caller; it does not tell Cloud to ask a question. Reviewed separately by source ID; English Tifa Come in., Red XIII Yes?.') for r in rows],
        user_approved=True,screenshot='C:/Users/godca/AppData/Local/Temp/codex-clipboard-8b6a92fb-e535-4164-a7ef-9e0d69f8e31f.png'))
    print('Saved immutable Ch4 door-fix baseline and two JP/US context records')

def apply_overlay(now):
    if not active(): return
    for k in KEYS:
        assert now['assets'][ASSET]['entries'][k] in ['ถามสิ','เชิญ']
        now['assets'][ASSET]['entries'][k]='เชิญ'

def apply():
    assert active()
    vals=read('translations/chapter4/reused-lines.json');assert vals['209']=='ถามสิ';vals['209']='เชิญ';write('translations/chapter4/reused-lines.json',vals)
    # Explicit per-ID overrides prevent a future short-string reuse from undoing the fix.
    overrides=read('reference/chapter4-ui-overrides.json')
    for k in KEYS: overrides[k]='เชิญ'
    write('reference/chapter4-ui-overrides.json',overrides)
    patch=read('translations/chapter4-th.json');apply_overlay(patch);write('translations/chapter4-th.json',patch)
    print('Corrected both Ch4 source IDs and rebuild inputs; historical working sets/snapshots retained')

def audit():
    rev=read(Q+'baseline.json');snap=Path(rev['snapshot']);ctx=read('qa/active-working-set.json')
    assert ctx['combined_source']==rev['active']['combined_source']
    for p,h in rev['hashes'].items(): assert digest(snap/p)==h,p
    old=read(snap/ctx['combined_source']);now=read(ctx['combined_source']);changed=[]
    assert old['assets'].keys()==now['assets'].keys()
    for a,p in old['assets'].items():
        n=now['assets'][a];assert p['entries'].keys()==n['entries'].keys() and p['actors']==n['actors']
        for k,t in p['entries'].items():
            if t!=n['entries'][k]:
                assert matches(a,k,t,n['entries'][k]),(a,k,'Unexpected translation edit')
                changed.append((a,k))
    from chapter4_choice_fix import active as followup_active,TARGETS,audit as followup_audit
    all_keys=set(KEYS)|set(TARGETS) if followup_active() else set(KEYS)
    from context_recheck import active as context_active,decisions,audit as context_audit
    extra={(r['asset'],r['id']) for r in decisions()} if context_active() else set()
    from context_full_read import decisions as full_decisions
    extra|={(r['asset'],r['id']) for r in full_decisions()}
    assert set(changed)=={(ASSET,k) for k in all_keys}|extra
    assert read(ctx['cluster_map'])==read(snap/ctx['cluster_map'])
    stage=W/ctx['stage'];manifest={str(p.relative_to(stage)):digest(p) for p in sorted(stage.rglob('*.uasset'))}
    prior=read(snap/ctx['manifest']);assert manifest.keys()==prior.keys() and len(manifest)==27
    modified=[p for p,h in manifest.items() if prior[p]!=h]
    assert {p.replace('\\','/') for p in modified}=={ASSET}|{a for a,k in extra},modified
    cmap=read(ctx['cluster_map']);reverse=str.maketrans({v:k for k,v in cmap.items()})
    src=txtres.parse(str(W/'source'/ASSET));dst=txtres.parse(str(stage/ASSET));us=txtres.parse(str(W/'source'/ASSET.replace('/JP/','/US/')))
    for k,v in src.items():
        assert dst[k]['Text'].translate(reverse)==now['assets'][ASSET]['entries'].get(k,v['Text'])
        md=dict(v.get('MetaData',{}))
        if k in now['assets'][ASSET]['actors']: md['ACTOR']=now['assets'][ASSET]['actors'][k]
        assert dst[k].get('MetaData',{})==md
    for k in KEYS:
        assert src[k]['Text']=='どうぞ' and us[k]['Text'] in ['Come in.','Yes?']
        target=TARGETS.get(k,'เชิญ') if followup_active() else 'เชิญ'
        assert now['assets'][ASSET]['entries'][k]==read('reference/chapter4-ui-overrides.json')[k]==read('translations/chapter4-th.json')['assets'][ASSET]['entries'][k]==target
    verify_protected(rev['protected'])
    report=dict(source_sha256=digest(W/ctx['combined_source']),corrected_records=2,total_combined_text_records=40691,
        changes=read(Q+'source-review.json')['records'],all_other40689_texts_and_all_actors_preserved=True,
        all_glyphs_fonts_and_other26_assets_byte_identical=True,changed_assets=modified,
        original_sources_and_installed_game_unchanged=True,in_game_tested=False)
    if followup_active():
        followup_audit()
        report['corrected_records']=len(changed)
        report['all_other40689_texts_and_all_actors_preserved']=False
        report['all_other40670_texts_and_all_actors_preserved']=True
        report['subsequent_followup']='qa/chapter4-choice-fix/audit.json'
        report['changes']=[dict(asset=a,id=k,before=old['assets'][a]['entries'][k],after=now['assets'][a]['entries'][k]) for a,k in changed]
    write(Q+'audit.json',report);print('Reviewed cumulative context corrections:',len(changed),'; all other texts/actors/fonts unchanged')
    if context_active():
        context_audit()
        report.update(all_glyphs_fonts_and_other26_assets_byte_identical=False,all_fonts_identical=True,all_other40670_texts_and_all_actors_preserved=False,all_other_texts_and_all_actors_preserved=True,subsequent_context_review='qa/context-recheck/audit.json')
        write(Q+'audit.json',report)

def preview():
    from PIL import Image,ImageDraw,ImageFont
    from preview_ch12_recheck import renderer
    ctx=read('qa/active-working-set.json');stage=W/ctx['stage'];dst=txtres.parse(str(stage/ASSET))
    canvas=Image.new('RGB',(1960,345),'#091522');d=ImageDraw.Draw(canvas)
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
    d.text((15,10),'Chapter4 door response | Actual staged glyphs | Not an in-game screenshot',font=legend,fill='#bfd7ed')
    samples=[]
    for col,size in enumerate(['Large','Normal']):
        gs,mask=renderer(stage,f'U_Com_JP_SystemFont{size}.uasset')
        for row,k in enumerate(KEYS):
            left=15+col*980;top=50+row*140
            d.rectangle((left,top,left+950,top+125),fill='#17283d')
            d.text((left+10,top+8),size+' | '+('Tifa' if row==0 else 'Red XIII')+' | 209 / per-ID override',font=legend,fill='#9fd8e8')
            x=left+16;y=top+55
            for ch in dst[k]['Text']:
                g=gs[ord(ch)]
                if g[4] and g[5]: canvas.paste((242,247,255),(x+g[6],y+g[7]),mask(g))
                x+=g[8]
            samples.append(dict(id=k,font=size))
    canvas.save(W/Q/'proof.png')
    write(Q+'proof.json',dict(source_sha256=digest(W/ctx['combined_source']),actual_staged_glyphs=True,samples=samples,in_game_tested=False))
    print('Rendered both corrected door responses in Large/Normal')

def finalize():
    audit();ctx=read('qa/active-working-set.json');rev=read(Q+'baseline.json');snap=Path(rev['snapshot'])
    final=read('qa/final-parts/latest.json');old={p['zip']:p for p in read(snap/'qa/final-parts/latest.json')['parts']};changed=[]
    for p in final['parts']:
        assert digest(W.parent/'Mod/Final'/p['zip'])==p['sha256']
        if p['sha256']!=old[p['zip']]['sha256']:changed.append(p['zip'])
    assert changed==['ThaiJP_Chapter3_4_5_P.zip']
    mount=read('qa/final-parts/combined-mount-verification.json')
    assert mount['zip_count']==8 and mount['mod_files']==24 and mount['assets']==27 and not mount['overlapping_assets'] and mount['all_match_verified_combined_set']
    sign=read('qa/chapter10/editorial-signoff.json')
    assert sign['source_sha256']==digest(W/ctx['combined_source'])
    for p,h in sign['reviewed_artifacts'].items():assert digest(W/p)==h,p
    write(Q+'release-verification.json',dict(source_sha256=sign['source_sha256'],corrected_records=2,total_records=40691,
        updated_parts=changed,unchanged_zip_count=7,zip_count=8,mod_files=24,assets=27,all_archives_read_back=True,installed=False,in_game_tested=False))
    root='E:/FF7RebrithModTH/FF7Rebrith/'
    note=f'''<!-- chapter4-door-current -->
## ล่าสุด: แก้คำตอบเคาะประตู Ch.4 — 20 ตุลาคม 2026

ผู้ใช้ยืนยันให้แก้ภาพRedXIIIหน้าห้อง: เปลี่ยน **ถามสิ → เชิญ** ทั้ง2ID `$C2120_MAIN_2900_0100_00_red` และ `$C2120_MAIN_2700_0500_00_tif` ใน8200-JUNOE ต้นฉบับJPどうぞ, USRedYes?/TifaCome in. แม่แบบCh4#209เดิมreuseข้ามบริบท จึงเพิ่มper-IDoverrideในreference/chapter4-ui-overrides.jsonและแก้translations/chapter4/reused-lines.json+chapter4-th.json; assemble_chapter10.pyใช้overlay2IDท้ายการประกอบฐาน ห้ามรันassembleบทเก่าเพื่อทับฐานปัจจุบัน

ฐานยัง **translations/working-through-chapter10-th.json — 40,691ข้อความ / 27assets / 717clusters** คงอีก40,689ข้อความ/ACTORทั้งหมด/ทุกฟอนต์และอีก26assetsทุกไบต์ อัปเดตเฉพาะ **ThaiJP_Chapter3_4_5_P.zip** ใน E:/FF7RebrithModTH/Mod/Final อีก7ZIPhashเดิม อ่านกลับ8ZIP/24modfiles/27assetsผ่านไม่มีซ้ำ สำรองนอกFinal ไม่มีติดตั้งหรือทดสอบเกมจริง

หลักฐาน [CHAPTER4-DOOR-FIX.md]({root}CHAPTER4-DOOR-FIX.md), qa/chapter4-door-fix/baseline.json+revisions/(ห้ามprepareซ้ำ), source-review.json(JP/USแยกID), audit.json, proof.png, release-verification.json; tools/chapter4_door_fix.py เก็บexceptionเฉพาะก่อนถามสิ/หลังเชิญ2ID ไม่ปล่อยให้แก้ฐานอื่นโดยพลการ gateCh10/recheck/continueยังทำงานและsignoffผูกhashoverlay/proofแล้ว ยอดเก็บตกเดิม144ไม่เปลี่ยน การแก้สะสมจาก40,547ตอนนี้61ข้อความที่มีอยู่เดิม(59รอบก่อน+2ประตู); ข้อความทุกIDยังครบ

ขั้นตอนต่อ: assemble_chapter10.py → build_chapter10.py --text-only → --verify → chapter10_recheck.py --quality → audit_shared_dialogs.py(รวมgateประตู) → audit_chapter10_glyphs.py → preview_chapter10.pyและchapter4_door_fix.py --preview/ดูproof → signoff_chapter10.py → publish_final_parts.py → chapter4_door_fix.py --finalize ไม่รันfinalize_chapter10_recheck/continueเดิมเพราะยังผูกbaselineก่อนแก้ประตู ข้อมูลยอด/คำว่าไม่แก้ฐานเก่าในบันทึกก่อนหน้านี้เป็นประวัติ ให้ใช้exception2IDนี้ต่อในบทถัดไป
<!-- /chapter4-door-current -->

'''
    (W/'CHAPTER4-DOOR-FIX.md').write_text('# แก้คำตอบหน้าประตู Ch.4\n\n'+note,'utf-8')
    for path in [W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'CHAPTER4-STATUS.md',W/'CHAPTER10-STATUS.md',W/'FINAL-PARTS.md']:
        title,body=path.read_text('utf-8').split('\n',1);body=re.sub(r'<!-- chapter4-door-current -->.*?<!-- /chapter4-door-current -->\s*','',body,flags=re.S)
        path.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    print('Finalized two Ch4 door fixes; only Chapter3_4_5 ZIP updated; all8 verified')

if __name__=='__main__':
    if '--prepare' in sys.argv: prepare()
    elif '--apply' in sys.argv: apply()
    elif '--preview' in sys.argv: preview()
    elif '--finalize' in sys.argv: finalize()
    else: audit()
