"""Bind the exact source, manually reviewed numeric differences and viewed proof."""
from prepare_chapter9 import W,read,write
from audit_chapter11 import CFG,Q,digest,main as audit
def main():
    audit();cfg=read(CFG);a=read(Q+'translation-audit.json');p=read(Q+'proof.json');g=read(Q+'gender/summary.json');sha=digest(W/cfg['source'])
    assert a['source_sha256']==p['source_sha256']==g['source_sha256']==sha
    assert len(p['samples'])==96 and not any(r['clipped'] for r in p['samples'])
    assert len(read(Q+'choice-groups.json')['groups'])==12
    reasons={251:'いちばん = rank1; same superlative in Arabic digits.',327:'三羽ガラス = the Three Ravens; numeral3 in the named trio.',328:'Same Three Ravens name rendered3.',450:'おふたり = both2 companions.',475:'Four groups of two digits; Thai reverses constituent order but retains4 and2 with their respective nouns.',751:'Spoken Japanese counting いち through ろく rendered1–6 in the same order.',891:'ふたり = two previously named disciples, rendered2.',1319:'１日中 is the idiom all day; Thaiทั้งวัน preserves duration without an extra numeric token.',1433:'１日３食 = three meals per day; วันละ3มื้อ retains the rate and quantity.',1517:'１日にしてならず = not achieved in one day; Thaiวันเดียว preserves one day.',1614:'まっぷたつ = cut into two halves; rendered2.'}
    revised=(W/'qa/chapter11/recheck/baseline.json').exists()
    if revised:reasons['recheck-21']='ふたり andふたつ specify two personas and two heads; rendered2,2 with one shared body retained in Thai.'
    nums=read(Q+'numeric-review.json');assert {r['template'] for r in nums}==set(reasons)
    write(Q+'numeric-decisions.json',dict(source_sha256=sha,records=[dict(template=r['template'],id=r['id'],decision=reasons[r['template']]) for r in nums],all_differences_reviewed=True))
    images={Q+f'proof-{n}.png':digest(W/Q/f'proof-{n}.png') for n in range(1,13)}
    # This ledger is recorded only after actually viewing the images. A build
    # cannot manufacture a new visual approval merely by running this script.
    visual=read(Q+'visual-review.json')
    assert visual['source_sha256']==sha and visual['all12_pages_viewed']
    assert visual['images']==images,'View the regenerated proof and record its actual image hashes first'
    arts=['reference/chapter11-source.json','reference/chapter11-templates.json','reference/chapter11-scope.json','reference/chapter11-deferred.json','reference/chapter11-build.json','reference/context-recheck-overrides.json','reference/context-full-read-overrides.json','tools/chapter11_scope.py','tools/assemble_chapter11.py','tools/build_chapter11.py','tools/audit_chapter11.py','tools/audit_chapter11_glyphs.py','tools/preview_chapter11.py','tools/signoff_chapter11.py','tools/audit_shared_dialogs.py','tools/publish_final_parts.py']
    arts += [Q+n for n in ['baseline.json','translation-audit.json','verification.json','working-assets.json','review-records.json','numeric-review.json','numeric-decisions.json','NPC-inventory.json','choice-review.json','choice-groups.json','Nibel-residual-dispositions.json','gender/summary.json','gender/records.json','old-glyph-regression.json','proof.json','visual-review.json']]
    arts+=['qa/shared-dialogs/latest.json','qa/shared-dialogs/NPC-regression.json','qa/shared-dialogs/enemy-actions-regression.json']+list(images)
    arts += [str(p.relative_to(W)).replace('\\','/') for p in sorted((W/'translations/chapter11').glob('batch-*.json'))]
    if revised:
        from chapter11_recheck import Q as RQ,audit as recheck_audit
        recheck_audit();rp=read(RQ+'proof.json');rv=read(RQ+'visual-review.json');progress=read(RQ+'progress.json')
        assert progress['complete'] and progress['choices_reviewed'] and progress['duplicate_contexts_reviewed'] and progress['remaining_templates']==0
        assert rp['source_sha256']==rv['source_sha256']==sha and rv['all_pages_viewed'] and len(rp['samples'])==105
        assert {(r['asset'],r['id']) for r in rp['samples']}=={(r['asset'],r['id']) for r in read('reference/chapter11-recheck-overrides.json')['records']+read('reference/chapter11-recheck-source.json')}
        for n,h in rv['images'].items():assert digest(W/n)==h,n
        arts += ['tools/chapter11_recheck.py','tools/chapter11_recheck_fixes.py','tools/preview_chapter11_recheck.py','reference/chapter11-recheck-source.json','reference/chapter11-recheck-overrides.json','translations/chapter11-recheck-lines.json']+[RQ+n for n in ['baseline.json','progress.json','review.json','enemy-intel-scope.json','inventory-revisions/initial46.json','choice-semantic-review.json','duplicate-context-review.json','proof.json','visual-review.json']]+list(rv['images'])
    if (W/'qa/pronoun-context/baseline.json').exists():
        from pronoun_context import Q as PQ,audit as pronoun_audit,decisions as pronoun_decisions
        pronoun_audit();pp=read(PQ+'proof.json');pv=read(PQ+'visual-review.json')
        assert pp['source_sha256']==pv['source_sha256']==sha and pv['all_pages_viewed']
        assert len(pp['samples'])==len(pronoun_decisions())==45 and pp['pages']==6
        assert {(r['asset'],r['id']) for r in pp['samples']}=={(r['asset'],r['id']) for r in pronoun_decisions()}
        assert set(pv['images'])=={PQ+f'proof-{n}.png' for n in range(1,7)}
        for n,h in pv['images'].items():assert digest(W/n)==h,n
        arts+=['reference/pronoun-context-overrides.json','tools/pronoun_context.py','tools/pronoun_context_decisions.py','tools/preview_pronoun_context.py','tools/chapter4_door_fix.py','tools/audit_npc_regression.py']+[PQ+n for n in ['baseline.json','queue.json','progress.json','historical-inputs.json','corrections-draft.json','decisions.json','audit.json','proof.json','visual-review.json','unchanged-proof-reuse.json']]+list(pv['images'])
    write(Q+'editorial-signoff.json',dict(source_sha256=sha,translation_sha256=digest(W/'translations/chapter11-th.json'),inventory_sha256=digest(W/'reference/chapter11-source.json'),proof_visually_reviewed=True,reviewed_proof_pages=12,numeric_differences_reviewed=True,gender_review_passed=not g['gender_mismatches'] and not g['unresolved_particle_bearing_speakers'],unknown_speakers_neutral=True,reviewed_artifacts={n:digest(W/n) for n in arts},same_id_US_used_for_labels_and_context=True,Japanese_dialogue_primary=True,new_full_video_audio_review=False,in_game_tested=False))
    print('Signed Ch11 source,',len(reasons),'numeric decisions and12 viewed main proof pages; recheck proof bound:',revised)
if __name__=='__main__':main()
