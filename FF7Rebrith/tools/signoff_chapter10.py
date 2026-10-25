"""Bind reviewed current source, numeric decisions and viewed five-page proof."""
from prepare_chapter9 import W,read,write
from audit_chapter10 import CFG,Q,digest
def main():
    cfg=read(CFG);a=read(Q+'translation-audit.json');proof=read(Q+'proof.json');g=read(Q+'gender/summary.json')
    assert proof['source_sha256']==a['source_sha256']==g['source_sha256']==digest(W/cfg['source'])
    revised=(W/'reference/chapter10-recheck-source.json').exists();pages=7 if revised else 5
    assert len(proof['samples'])==pages*8 and not any(r['clipped'] for r in proof['samples'])
    reasons={
      40:'七番街 -> sector7; literal district number in Arabic digits.',176:'おひとつ is one item, rendered1.',178:'おひとつ is one item, rendered1.',179:'おひとり様おひとつ: one per person, rendered1.',
      207:'七番プレート -> sector7 plate.',229:'明後日 is two days from now, rendered2.',287:'八番街 -> sector8.',306:'伍番街 -> sector5.',308:'いちばん explicit superlative ranking -> number1.',
      408:'よんじゅう reads forty, rendered40.',501:'年にいちど means once per year, rendered1.',548:'年にいちど means once per year, rendered1.',608:'ひとり means one remaining person, rendered1.',
      657:'ふたりとも both parents, rendered2.',664:'ふたりのみ two participants, rendered2.',688:'40と5年前 is forty-and-five years, rendered45, not two separate dates.',795:'ふたり both parents, rendered2.',1062:'七番街 -> sector7.',
      1389:'ふたり two traveling companions, rendered2.',1594:'あとひとつ one site remains, rendered1.',1602:'7000飛び83 denotes7083, not a subtraction or range.',2020:'ふたり two travelers, rendered2.',2026:'ふたり two household members, rendered2.',
      2069:'十数億 means a little over one billion, approximatedราว1พันกว่าล้าน preserving uncertainty.',2578:'千年 means1000 years. Footstep remains natural indefinite expression.'}
    if revised:reasons['recheck-15']='二度目 means second time, renderedครั้งที่2 in Arabic digits; value unchanged.'
    numbers=read(Q+'numeric-review.json');assert {r['template'] for r in numbers}==set(reasons)
    write(Q+'numeric-decisions.json',dict(source_sha256=a['source_sha256'],records=[dict(id=r['id'],template=r['template'],decision=reasons[r['template']]) for r in numbers],all_differences_reviewed=True,reviewed_records=len(numbers)))
    arts=[Q+n for n in ['translation-audit.json','verification.json','working-assets.json','numeric-review.json','numeric-decisions.json','NPC-inventory.json','choice-review.json','visited-scene-residual-dispositions.json','gender/summary.json','gender/records.json','old-glyph-regression.json','proof.json']]
    arts+=[Q+f'proof-{i}.png' for i in range(1,pages+1)]
    if revised:arts+=['reference/chapter10-recheck-source.json','translations/chapter10-recheck-lines.json','tools/chapter10_recheck_scope.py','tools/audit_chapter10_recheck.py','qa/chapter10/recheck/review.json','qa/chapter10/recheck/Resident-residual-dispositions.json','qa/chapter10/recheck/terminology-decisions.json']
    if (W/'qa/chapter10/continue-review/current.json').exists():
        from chapter10_continue_review import FIXES
        assert set(FIXES)<={str(r['template']) for r in proof['samples']}
        arts+=['tools/chapter10_continue_review.py','qa/chapter10/continue-review/current.json','qa/chapter10/continue-review/review.json']
    if (W/'qa/chapter4-door-fix/baseline.json').exists():
        from chapter4_door_fix import Q as DOOR_Q,KEYS
        door_proof=read(DOOR_Q+'proof.json')
        assert door_proof['source_sha256']==a['source_sha256'] and {r['id'] for r in door_proof['samples']}==set(KEYS) and len(door_proof['samples'])==4
        arts+=['tools/chapter4_door_fix.py',DOOR_Q+'baseline.json',DOOR_Q+'source-review.json',DOOR_Q+'audit.json',DOOR_Q+'proof.json',DOOR_Q+'proof.png','reference/chapter4-ui-overrides.json','translations/chapter4/reused-lines.json','translations/chapter4-th.json']
    if (W/'qa/chapter4-choice-fix/baseline.json').exists():
        from chapter4_choice_fix import Q as CHOICE_Q,TARGETS
        choice_proof=read(CHOICE_Q+'proof.json')
        assert choice_proof['source_sha256']==a['source_sha256'] and choice_proof['pages']==3
        assert set(TARGETS)<={k for r in choice_proof['samples'] for k in r['ids']}
        arts+=['tools/chapter4_choice_fix.py','tools/audit_npc_regression.py',CHOICE_Q+'baseline.json',CHOICE_Q+'source-review.json',CHOICE_Q+'audit.json',CHOICE_Q+'proof.json','translations/chapter4/batch-03.json']+[CHOICE_Q+f'proof-{i}.png' for i in range(1,4)]
    arts+=['tools/audit_chapter10.py','tools/chapter10_scope.py','tools/assemble_chapter10.py','tools/preview_chapter10.py','tools/audit_shared_dialogs.py','tools/publish_final_parts.py','qa/shared-dialogs/latest.json','qa/shared-dialogs/NPC-regression.json']
    from context_recheck import active as context_active,Q as CONTEXT_Q
    if context_active():
        cp=read(CONTEXT_Q+'proof.json');visual=read(CONTEXT_Q+'visual-review.json')
        assert cp['source_sha256']==visual['source_sha256']==a['source_sha256']
        assert visual['all_context_proof_pages_viewed'] and visual['pages']==cp['pages']
        for p,h in visual['images'].items():assert digest(W/p)==h,p
        for p in ['audit.json','choice-semantic-review.json','short-dialogue-review.json','shared-prompt-review.json','corpus-screen.json']:
            assert read(CONTEXT_Q+p)['source_sha256']==a['source_sha256']
        arts+=['reference/context-recheck-overrides.json','tools/context_recheck.py','tools/context_recheck_preview.py']+[CONTEXT_Q+p for p in ['baseline.json','inventory.json','all-record-contexts.json','scene-choice-groups.json','reused-short-dialogue.json','shared-prompt-contexts.json','audit.json','choice-semantic-review.json','short-dialogue-review.json','shared-prompt-review.json','corpus-screen.json','additional-risk-review.json','proof.json','visual-review.json']]+[CONTEXT_Q+f'proof-{i}.png' for i in range(1,cp['pages']+1)]
    from context_full_read import active as full_active,Q as FULL_Q,OVERRIDES
    if full_active():
        fp=read(FULL_Q+'proof.json');fv=read(FULL_Q+'visual-review.json');fa=read(FULL_Q+'audit.json')
        assert fp['source_sha256']==fv['source_sha256']==fa['source_sha256']==a['source_sha256']
        from validate_context_visual import validate as validate_full_visual
        arts += validate_full_visual(FULL_Q,a['source_sha256'])
        arts += ['tools/validate_context_visual.py',FULL_Q+'compare-viewed-panels.py']
        from verify_installed_session import CHECKPOINT,verify as verify_installed
        verify_installed(read(FULL_Q+'baseline.json')['protected'])
        if (W/CHECKPOINT).exists():arts += ['tools/verify_installed_session.py',CHECKPOINT]
        arts += [FULL_Q+'cloud-address-review.json',FULL_Q+'queue-cloud-address.py']
        if read(FULL_Q+'progress.json')['semantic_review_complete']:
            from audit_english_completion import main as audit_english_completion
            audit_english_completion()
            arts += ['tools/audit_english_completion.py',FULL_Q+'english-completion-review.json',FULL_Q+'english-completion-audit.json']
        for p,h in fv['images'].items():assert digest(W/p)==h,p
        assert {(r['asset'],r['id']) for r in read(OVERRIDES)['records']}<={(r['asset'],k) for r in fp['samples'] for k in r['ids']}
        # The read queue continues after publication. Bind an immutable release
        # checkpoint, rather than invalidating the released ZIPs whenever the
        # live editorial progress ledger advances without changing game text.
        checkpoint=FULL_Q+'releases/'+a['source_sha256']+'/'
        import shutil
        for name in ['progress.json','corrections.json']:
            dest=W/checkpoint/name
            if not dest.exists():
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(W/FULL_Q/name,dest)
        arts += [OVERRIDES,'tools/context_full_read.py','tools/context_full_read_preview.py']+[FULL_Q+p for p in ['baseline.json','queue.json','audit.json','proof.json','visual-review.json']]+[checkpoint+p for p in ['progress.json','corrections.json']]+list(fv['images'])
    write(Q+'editorial-signoff.json',dict(source_sha256=a['source_sha256'],translation_sha256=digest(W/'translations/chapter10-th.json'),inventory_sha256=digest(W/'reference/chapter10-source.json'),proof_visually_reviewed=True,reviewed_proof_pages=pages,numeric_differences_reviewed=True,gender_review_passed=not g['gender_mismatches'] and not g['unresolved_particle_bearing_speakers'],unknown_speakers_neutral=True,named_Wedge_male=True,canonical_names_reviewed=['Aerith เอริธ','Zack แซ็ก','Cait Sith เค็ตชี','Gongaga กอนกาก้า','SOLDIER โซลเจอร์','Potion โพชั่น','Marche มาร์เค','Regina เรจี้','Navalan นาบารา'],source_anomalies=[dict(template=1045,jp='別；ユフィ！',decision='Alternate-take annotation 別； omitted; dialogue is Yuffie!')],reviewed_artifacts={p:digest(W/p) for p in arts},new_full_video_audio_review=False,in_game_tested=False))
    print('Signed current Chapter10 source and',pages,'visually reviewed proof pages')
if __name__=='__main__':main()
