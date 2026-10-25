"""Require current-source semantic, gender, coverage and visual evidence."""
from prepare_chapter9 import W,read,write
from audit_chapter14 import CFG,Q,digest

def main():
    cfg=read(CFG);sha=digest(W/cfg['source']);a=read(Q+'translation-audit.json');p=read(Q+'proof.json');g=read(Q+'gender/summary.json');progress=read(Q+'progress.json')
    assert a['source_sha256']==p['source_sha256']==g['source_sha256']==sha
    assert a['new_records']==936 and a['new_templates']==897 and a['total_combined_text_records']==48439 and a['previous47503_text_and_ACTOR_preserved']
    assert a['working_assets']==28 and p['pages']==11 and p['complete_choice_groups']==3 and len(p['samples'])==80 and not any(r['clipped'] for r in p['samples'])
    assert progress['semantic_review_complete'] and progress['second_read_complete'] and progress['remaining_templates']==0 and progress['read_ranges']==[[0,896]]
    visual=read(Q+'visual-review.json');assert visual['source_sha256']==sha and visual['all_pages_viewed']
    images={Q+f'proof-{n}.png':digest(W/Q/f'proof-{n}.png') for n in range(1,12)};assert visual['images']==images
    assert not g['gender_mismatches'] and not g['unresolved_particle_bearing_speakers']
    reviews=['choice-review','numeric-decisions','pronoun-review','duplicate-context-review','coverage-review','deferred-remaining','NPC-residual','adjoining-UI-review']
    for n in reviews:assert read(Q+n+'.json')['source_sha256']==sha,n
    assert len(read(Q+'choice-review.json')['groups'])==3 and read(Q+'NPC-residual.json')['untranslated_NPC_rows']==0
    assert len(read(Q+'numeric-decisions.json')['records'])==5 and read(Q+'numeric-decisions.json')['all_differences_reviewed']
    assert read(Q+'deferred-remaining.json')['all_remaining_Japanese_classified']
    ui=read(Q+'adjoining-UI-review.json');assert ui['all_registered_rows_read'] and ui['registered_rows']==43
    now=read(cfg['source'])
    for r in ui['records']:assert now['assets'][r['asset']]['entries'][r['id']]==r['thai']
    artifacts=['reference/chapter14-build.json','reference/chapter14-source.json','reference/chapter14-templates.json','reference/chapter14-scope.json','reference/chapter14-actor-labels.json',cfg['cluster_map']]
    artifacts+=['tools/'+n+'.py' for n in ['chapter14_scope','assemble_chapter14','build_chapter14','audit_chapter14','audit_chapter14_glyphs','chapter14_review','preview_chapter14','signoff_chapter14','audit_shared_dialogs','audit_npc_regression','publish_final_parts']]
    artifacts += [Q+n+'.json' for n in ['baseline','translation-audit','verification','working-assets','review-records','numeric-review','progress','editorial-revisions','old-glyph-regression','proof','visual-review','same-scene-variant-reuse','actor-label-candidates']+reviews]
    artifacts += [Q+'gender/summary.json',Q+'gender/records.json','qa/shared-dialogs/latest.json','qa/shared-dialogs/NPC-regression.json','qa/shared-dialogs/enemy-actions-regression.json']+list(images)
    artifacts += [str(p.relative_to(W)).replace('\\','/') for p in sorted((W/'translations/chapter14').glob('batch-*.json'))]
    write(Q+'editorial-signoff.json',dict(source_sha256=sha,translation_sha256=digest(W/'translations/chapter14-th.json'),inventory_sha256=digest(W/'reference/chapter14-source.json'),proof_visually_reviewed=True,reviewed_proof_pages=11,numeric_differences_reviewed=True,gender_review_passed=True,choice_context_reviewed=True,unknown_speakers_neutral=True,reviewed_artifacts={n:digest(W/n) for n in artifacts},Japanese_dialogue_primary=True,same_id_US_used_for_labels_and_context=True,CAPIT_missing_US_text_not_used_as_translation=True,new_full_video_audio_review=False,in_game_tested=False))
    print('Signed897 templates /936 IDs;3 complete choice groups;5 numeric decisions;11 viewed proof pages')

if __name__=='__main__':main()
