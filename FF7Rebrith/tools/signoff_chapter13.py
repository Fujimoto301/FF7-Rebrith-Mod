"""Require source-bound Ch13 review, prior-release preservation and viewed proofs."""
from prepare_chapter9 import W,read,write
from audit_chapter13 import CFG,Q,digest

def main():
    cfg=read(CFG);sha=digest(W/cfg['source']);a=read(Q+'translation-audit.json');p=read(Q+'proof.json');g=read(Q+'gender/summary.json');progress=read(Q+'progress.json')
    assert a['source_sha256']==p['source_sha256']==g['source_sha256']==sha
    assert a['new_records']==853 and a['new_templates']==809 and a['total_combined_text_records']==47503 and a['previous46650_text_and_ACTOR_preserved']
    assert p['pages']==11 and p['complete_choice_groups']==2 and len(p['samples'])==76 and not any(r['clipped'] for r in p['samples'])
    assert progress['semantic_review_complete'] and progress['second_read_complete'] and progress['remaining_templates']==0 and progress['read_ranges']==[[0,808]]
    visual=read(Q+'visual-review.json');assert visual['source_sha256']==sha and visual['all_pages_viewed']
    images={Q+f'proof-{n}.png':digest(W/Q/f'proof-{n}.png') for n in range(1,12)};assert visual['images']==images
    assert not g['gender_mismatches'] and not g['unresolved_particle_bearing_speakers']
    for n in ['choice-review','numeric-decisions','pronoun-review','duplicate-context-review','coverage-review','deferred-remaining','NPC-residual','adjoining-UI-review']:
        assert read(Q+n+'.json')['source_sha256']==sha,n
    assert len(read(Q+'choice-review.json')['groups'])==2 and read(Q+'NPC-residual.json')['untranslated_NPC_rows']==0
    numeric_count=9 if (W/'reference/chapter13-recheck-overrides.json').exists() else 4
    assert len(read(Q+'numeric-decisions.json')['records'])==numeric_count and read(Q+'numeric-decisions.json')['all_differences_reviewed']
    ui=read(Q+'adjoining-UI-review.json');now=read(cfg['source']);assert ui['all_registered_rows_read']
    for r in ui['records']:assert now['assets'][r['asset']]['entries'][r['id']]==r['thai']
    assert read(Q+'deferred-remaining.json')['all_remaining_Japanese_classified']
    artifacts=['reference/chapter13-build.json','reference/chapter13-source.json','reference/chapter13-templates.json','reference/chapter13-scope.json','reference/chapter12-recheck-overrides.json',cfg['cluster_map']]
    artifacts += ['tools/'+n+'.py' for n in ['chapter13_scope','assemble_chapter13','build_chapter13','audit_chapter13','audit_chapter13_glyphs','chapter13_review','preview_chapter13','signoff_chapter13','audit_shared_dialogs','audit_npc_regression','publish_final_parts']]
    artifacts += [Q+n+'.json' for n in ['baseline','translation-audit','verification','working-assets','review-records','numeric-review','numeric-decisions','NPC-residual','choice-review','progress','editorial-revisions','old-glyph-regression','proof','visual-review','pronoun-review','duplicate-context-review','coverage-review','deferred-remaining','adjoining-UI-review']]
    artifacts += [Q+'gender/summary.json',Q+'gender/records.json','qa/shared-dialogs/latest.json','qa/shared-dialogs/NPC-regression.json','qa/shared-dialogs/enemy-actions-regression.json']+list(images)
    artifacts += [str(p.relative_to(W)).replace('\\','/') for p in sorted((W/'translations/chapter13').glob('batch-*.json'))]
    if (W/'reference/chapter13-recheck-overrides.json').exists():
        from chapter13_recheck import audit as recheck_audit,Q as RQ
        recheck_audit();rp=read(RQ+'proof.json');rv=read(RQ+'visual-review.json')
        assert rp['source_sha256']==rv['source_sha256']==sha and rv['all_pages_viewed'] and rp['pages']==2 and len(rp['samples'])==11
        assert {(r['asset'],r['id']) for r in rp['samples']}=={(r['asset'],r['id']) for r in read('reference/chapter13-recheck-overrides.json')['records']}
        for n,h in rv['images'].items():assert digest(W/n)==h,n
        artifacts+=['reference/chapter13-recheck-overrides.json','tools/chapter13_recheck.py']+[RQ+n+'.json' for n in ['baseline','progress','audit','proof','visual-review']]+list(rv['images'])
    write(Q+'editorial-signoff.json',dict(source_sha256=sha,translation_sha256=digest(W/'translations/chapter13-th.json'),inventory_sha256=digest(W/'reference/chapter13-source.json'),proof_visually_reviewed=True,reviewed_proof_pages=11,numeric_differences_reviewed=True,gender_review_passed=True,choice_context_reviewed=True,unknown_speakers_neutral=True,reviewed_artifacts={n:digest(W/n) for n in artifacts},Japanese_dialogue_primary=True,same_id_US_used_for_labels_and_context=True,new_full_video_audio_review=False,in_game_tested=False))
    print('Signed809 templates /853 IDs;2 complete choice groups;',numeric_count,'numeric decisions;11 main proof pages plus any recheck proof')
if __name__=='__main__':main()
