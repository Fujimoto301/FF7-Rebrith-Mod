"""Publish the newest non-overlapping installation parts, one ZIP per part."""
import hashlib,json,os,shutil,uuid,zipfile
from pathlib import Path
import pack_prototype

W=Path(__file__).resolve().parents[1]
FINAL=W.parent/'Mod/Final'
QA=W/'qa/final-parts'
STAGE=W/'staging/ThaiJP_UICompletion_Working'
GAME=Path(r'E:\steam\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks\~mods')

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files(root):return {str(p.relative_to(root)):digest(p) for p in sorted(root.rglob('*')) if p.is_file()}
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')

def main():
    global STAGE
    context_path=W/'qa/active-working-set.json'
    context=json.loads(context_path.read_text('utf-8')) if context_path.exists() else dict(
        stage='staging/ThaiJP_UICompletion_Working',manifest='qa/ui-completion/working-assets.json',
        audit='qa/ui-completion/final-audit.json',asset_count=21,additional_parts=[])
    STAGE=W/context['stage']
    if context.get('chapter14'):
        from audit_shared_dialogs import main as audit_current_chapter14
        audit_current_chapter14()
        cfg=json.loads((W/'reference/chapter14-build.json').read_text('utf-8'))
        assert context['combined_source']==cfg['source']
        sign=json.loads((W/'qa/chapter14/editorial-signoff.json').read_text('utf-8'))
        assert sign['source_sha256']==digest(W/cfg['source'])
        assert sign['translation_sha256']==digest(W/'translations/chapter14-th.json')
        assert sign['inventory_sha256']==digest(W/'reference/chapter14-source.json')
        assert sign['proof_visually_reviewed'] and sign['numeric_differences_reviewed'] and sign['gender_review_passed'] and sign['choice_context_reviewed']
        for rel,h in sign['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    elif context.get('chapter13'):
        from audit_shared_dialogs import main as audit_current_chapter13
        audit_current_chapter13()
        cfg=json.loads((W/'reference/chapter13-build.json').read_text('utf-8'))
        assert context['combined_source']==cfg['source']
        sign=json.loads((W/'qa/chapter13/editorial-signoff.json').read_text('utf-8'))
        assert sign['source_sha256']==digest(W/cfg['source'])
        assert sign['translation_sha256']==digest(W/'translations/chapter13-th.json')
        assert sign['inventory_sha256']==digest(W/'reference/chapter13-source.json')
        assert sign['proof_visually_reviewed'] and sign['numeric_differences_reviewed'] and sign['gender_review_passed'] and sign['choice_context_reviewed']
        for rel,h in sign['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    elif context.get('chapter12'):
        from audit_shared_dialogs import main as audit_current_chapter12
        audit_current_chapter12()
        cfg=json.loads((W/'reference/chapter12-build.json').read_text('utf-8'))
        assert context['combined_source']==cfg['source']
        sign=json.loads((W/'qa/chapter12/editorial-signoff.json').read_text('utf-8'))
        assert sign['source_sha256']==digest(W/cfg['source'])
        assert sign['translation_sha256']==digest(W/'translations/chapter12-th.json')
        assert sign['inventory_sha256']==digest(W/'reference/chapter12-source.json')
        assert sign['proof_visually_reviewed'] and sign['numeric_differences_reviewed'] and sign['gender_review_passed']
        for rel,h in sign['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    elif context.get('chapter11'):
        from audit_shared_dialogs import main as audit_current_chapter11
        audit_current_chapter11()
        cfg=json.loads((W/'reference/chapter11-build.json').read_text('utf-8'))
        assert context['combined_source']==cfg['source']
        sign=json.loads((W/'qa/chapter11/editorial-signoff.json').read_text('utf-8'))
        assert sign['source_sha256']==digest(W/cfg['source'])
        assert sign['translation_sha256']==digest(W/'translations/chapter11-th.json')
        assert sign['inventory_sha256']==digest(W/'reference/chapter11-source.json')
        assert sign['proof_visually_reviewed'] and sign['numeric_differences_reviewed'] and sign['gender_review_passed']
        for rel,h in sign['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    elif context.get('chapter10'):
        from audit_shared_dialogs import main as audit_current_chapter10
        audit_current_chapter10()
        cfg=json.loads((W/'reference/chapter10-build.json').read_text('utf-8'))
        assert context['combined_source']==cfg['source'],'Create a current-source gate for the next chapter'
        sign=json.loads((W/'qa/chapter10/editorial-signoff.json').read_text('utf-8'))
        assert sign['source_sha256']==digest(W/cfg['source'])
        assert sign['translation_sha256']==digest(W/'translations/chapter10-th.json')
        assert sign['inventory_sha256']==digest(W/'reference/chapter10-source.json')
        required_pages=7 if (W/'reference/chapter10-recheck-source.json').exists() else 5
        assert sign['proof_visually_reviewed'] and sign['reviewed_proof_pages']==required_pages
        assert sign['numeric_differences_reviewed'] and sign['gender_review_passed']
        for rel,h in sign['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    elif context.get('enemy_actions'):
        from audit_shared_dialogs import main as audit_current_actions
        audit_current_actions()
        cfg=json.loads((W/'reference/enemy-actions-build.json').read_text('utf-8'))
        assert context['combined_source']==cfg['source'],'Create a current-source release gate for the new chapter before publishing'
        sign=json.loads((W/'qa/enemy-actions/editorial-signoff.json').read_text('utf-8'))
        assert sign['source_sha256']==digest(W/cfg['source'])
        assert sign['translation_sha256']==digest(W/'translations/enemy-actions-th.json')
        assert sign['inventory_sha256']==digest(W/'reference/enemy-actions-source.json')
        assert sign['proof_visually_reviewed'] and sign['reviewed_proof_pages']==2
        for rel,h in sign['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    elif context.get('npc_recheck'):
        from audit_shared_dialogs import main as audit_current_NPC
        audit_current_NPC()
        cfg=json.loads((W/'reference/npc-recheck-build.json').read_text('utf-8'))
        sign=json.loads((W/'qa/npc-recheck/editorial-signoff.json').read_text('utf-8'))
        assert sign['source_sha256']==digest(W/cfg['source'])
        assert sign['translation_sha256']==digest(W/'translations/npc-recheck-th.json')
        assert sign['inventory_sha256']==digest(W/'reference/npc-recheck-source.json')
        assert sign['proof_visually_reviewed'] and sign['reviewed_proof_pages']==4
        for rel,h in sign['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    if context.get('choice_completion') and not context.get('npc_recheck'):
        # This revision expands the whole-game choice inventory. Fail closed if
        # edits have made the source, family review, proofs, or signoff stale.
        from audit_shared_dialogs import main as audit_current_choices
        audit_current_choices()
        cfg=json.loads((W/'reference/choice-completion-build.json').read_text('utf-8'))
        root=W/'qa/choice-completion'
        sign=json.loads((root/'editorial-signoff.json').read_text('utf-8'))
        assert sign['combined_source_sha256']==digest(W/cfg['source'])
        assert sign['translation_sha256']==digest(W/'translations/choice-completion-th.json')
        assert sign['inventory_sha256']==digest(W/'reference/choice-completion-source.json')
        assert sign['proof_visually_reviewed'] and sign['reviewed_proof_pages']==4
        if (root/'recheck/current.json').exists():
            revision=json.loads((root/'recheck/review.json').read_text('utf-8'))
            assert revision['source_sha256']==sign['combined_source_sha256']
            assert revision['previous33902_text_and_ACTOR_preserved']
            assert sign['recheck_proof_visually_reviewed'] and sign['reviewed_recheck_proof_pages']==4
        for rel,h in sign['reviewed_artifacts'].items():assert digest(W/rel)==h,rel
    expected=json.loads((W/context['manifest']).read_text('utf-8'))
    actual={str(p.relative_to(STAGE)):digest(p) for p in sorted(STAGE.rglob('*.uasset'))}
    assert actual==expected and len(actual)==context['asset_count'],'Reverify combined working assets first'
    before_game=files(GAME)
    QA.mkdir(parents=True,exist_ok=True)
    run=QA/'runs'/uuid.uuid4().hex;run.mkdir(parents=True)
    last=json.loads((QA/'latest.json').read_text('utf-8')) if (QA/'latest.json').exists() else {}
    cached={p['name']:p for p in last.get('parts',[])}
    specifications=[
        (context.get('chapter1_part_name','ThaiJP_Chapter1_P'),('4000-MIDGR_TxtRes.uasset','8700-NIBLE_TxtRes.uasset')),
        ('ThaiJP_Chapter2_P',('8100-GRASE_TxtRes.uasset','8800-FOREE_TxtRes.uasset')),
    ]
    specifications.extend((name,tuple(basenames)) for name,basenames in context['additional_parts'])
    specifications.append(('ThaiJP_Common_P',None))
    part_count=len(specifications)
    used=set();parts=[]
    license_comment=b'Embedded Thai font license and copyright notice (UTF-8):\n\n'+(W/'tools/fonts/NotoSansThai-OFL.txt').read_bytes()
    assert len(license_comment)<=65535
    for name,basenames in specifications:
        selected={rel for rel in actual if Path(rel).name in basenames} if basenames else set(actual)-used
        assert selected and not selected & used
        if basenames:assert {Path(rel).name for rel in selected}==set(basenames)
        used.update(selected)
        old_part=cached.get(name)
        if old_part and old_part['assets']=={rel:actual[rel] for rel in selected}:
            old_zip=FINAL/old_part['zip']
            if old_zip.is_file() and digest(old_zip)==old_part['sha256']:
                with zipfile.ZipFile(old_zip) as z:
                    assert z.namelist()==old_part['mod_files'] and z.testzip() is None
                    assert z.comment==license_comment
                part=dict(old_part);part['reused_unchanged']=True
                part['all_parts_required']=True;part['all_three_zips_required']=part_count==3;parts.append(part)
                print('Keeping unchanged ZIP:',old_part['zip'],flush=True)
                continue
        stage=run/name/'staging';pack_qa=run/name/'qa';target=run/name/'packed'
        for rel in sorted(selected):
            dest=stage/rel;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(STAGE/rel,dest);assert digest(dest)==actual[rel]
        print('Packing',name,':',len(selected),'assets',flush=True)
        pack_prototype.main(name,len(selected),stage_override=str(stage),qa_override=str(pack_qa),
                            target_override=str(target),font_license='NotoSansThai-OFL.txt')
        readback=json.loads((pack_qa/'package-verification.json').read_text('utf-8'))
        mounted={str(Path(x['asset'])):x['sha256'] for x in readback['assets']}
        assert mounted=={rel:actual[rel] for rel in selected},name
        names=[name+ext for ext in ('.pak','.utoc','.ucas')]
        candidate=run/(name+'.zip')
        with zipfile.ZipFile(candidate,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.comment=license_comment
            for n in names:z.write(target/n,n)
        with zipfile.ZipFile(candidate) as z:
            assert z.namelist()==names and z.comment==license_comment and z.testzip() is None
            for n in names:assert z.read(n)==(target/n).read_bytes()
        parts.append(dict(name=name,zip=name+'.zip',bytes=candidate.stat().st_size,sha256=digest(candidate),
            assets={rel:actual[rel] for rel in sorted(selected)},mod_files=names,
            all_parts_required=True,all_three_zips_required=part_count==3,independent_readback=True,reused_unchanged=False,runtime_tested=False))
    assert used==set(actual)
    mod_names=[n for p in parts for n in p['mod_files']]
    assert len(mod_names)==len(set(mod_names))==3*part_count
    assert files(GAME)==before_game
    # Publish only after all candidates pass. Preserve replaced archives outside Final.
    FINAL.mkdir(parents=True,exist_ok=True)
    recognized={p['zip'] for p in parts}
    superseded={name+'.zip' for name in context.get('superseded_parts',[])}
    assert not superseded & recognized
    assert {p.name for p in FINAL.glob('*.zip')} <= recognized|superseded,'Unrecognized ZIP in Final'
    # Explicitly authorized part rename: retain the previous ZIP outside Final.
    for name in superseded:
        old=FINAL/name
        assert old.resolve().parent==FINAL.resolve() and old.suffix=='.zip'
        if old.exists():
            backup=run/'previous-final'/name;backup.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(old,backup);assert digest(old)==digest(backup)
    for name in (p['zip'] for p in parts if not p['reused_unchanged']):
        old=FINAL/name
        if old.exists():
            backup=run/'previous-final'/name;backup.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(old,backup);assert digest(old)==digest(backup)
    for p in parts:
        if not p['reused_unchanged']:os.replace(run/p['zip'],FINAL/p['zip'])
        assert digest(FINAL/p['zip'])==p['sha256']
    for name in superseded:
        old=FINAL/name
        if old.exists():
            assert old.resolve().parent==FINAL.resolve()
            assert digest(old)==digest(run/'previous-final'/name)
            old.unlink()
    assert {p.name for p in FINAL.glob('*.zip')}==recognized
    assert files(GAME)==before_game
    report=dict(parts=parts,zip_count=part_count,total_assets=len(actual),asset_sets_disjoint=True,
        combined_text_records=json.loads((W/context['audit']).read_text('utf-8'))['total_combined_text_records'],
        union_matches_verified_combined_set=True,installed_files_unchanged=True,installed_files_snapshot=before_game,installed=False,
        runtime_tested=False,all_parts_required=True,all_three_zips_required=part_count==3,
        working_manifest=context['manifest'],working_stage=context['stage'],chapters=context.get('chapters',[1,2]),
        shared_file_note=context.get('shared_file_note','GRASE in Chapter2 ZIP contains Ch.1–3 records; additional chapter ZIPs contain shared JUNOE dialogue. Resident and fonts are shared. Keep assets whole and install all current ZIPs together.'),
        backups=str(run/'previous-final'),run=str(run))
    save(run/'release.json',report);save(QA/'latest.json',report)
    old_report=W/'qa/ui-completion/final-release.json'
    if old_report.exists():
        old=json.loads(old_report.read_text('utf-8'));old['superseded_by_split_release']=str(QA/'latest.json')
        old['active_release']=False;save(old_report,old)
    from verify_final_parts import main as verify_together
    verify_together()
    print('Published',part_count,'latest ZIPs to',FINAL,flush=True)
    print(len(actual),'assets partitioned without overlap. Install all parts together. Game files unchanged.',flush=True)

if __name__=='__main__':main()
