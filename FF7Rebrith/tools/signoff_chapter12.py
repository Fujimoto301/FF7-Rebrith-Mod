"""Require exact reviewed source, numeric decisions and viewed staged proof."""
from prepare_chapter9 import W,read,write
from audit_chapter12 import CFG,Q,digest

def main():
    cfg=read(CFG);sha=digest(W/cfg['source']);a=read(Q+'translation-audit.json');p=read(Q+'proof.json');g=read(Q+'gender/summary.json');progress=read(Q+'progress.json')
    assert a['source_sha256']==p['source_sha256']==g['source_sha256']==sha
    assert a['new_records']==4200 and a['new_templates']==3847 and a['total_combined_text_records']==46650
    assert p['pages']==16 and p['complete_choice_groups']==36 and len(p['samples'])==120 and not any(r['clipped'] for r in p['samples'])
    assert progress['semantic_review_complete'] and progress['remaining_templates']==0 and progress['read_ranges']==[[0,3846]]
    reasons={
      57:'六番 = reactor6.',327:'第七 = seventh regiment.',357:'第七 = seventh regiment.',440:'四号 = reactor4.',698:'三界 = three domains: land,sea,sky.',
      811:'どっちも = both2.',977:'おふたり = these2.',999:'ひとり...ひとり =1...1; the remaining person kept singular in Thai.',1006:'ひとり =1 of the travellers.',1048:'ふたり =2 lovers.',
      1071:'ひと幕 =1 remaining act.',1073:'表裏一体 = two sides of the same coin; idiomatic Thaiเหรียญ2ด้าน.',1140:'世界一 = rank1 in the world.',1178:'ふたりきり =2 people alone.',
      1395:'ワンツー = spoken1,2.',1411:'ワン = round1.',1420:'ツー = round2.',1437:'スリー = round3.',1498:'双方 = both2 sides.',1546:'両者 = both2 contestants.',
      1624:'七番街 = Sector7.',1629:'七番街 = Sector7.',1632:'七番街 = Sector7.',1648:'５人１チーム =5 per team; Thaiทีมละ5 retains rate, not an omitted team.',
      1980:'両陣営 = both2 factions.',1983:'両者 = both2 contestants.',2353:'１戦 = this match, not a quantity of opponents; Thaiศึก.',2367:'この１戦 = this specific match; Thaiศึกนี้.',
      2554:'１枚２０００ =2000 per photo; Thaiรูปละ2000 keeps rate.',2605:'最後の１枚 = the final photo; Thaiรูปสุดท้าย.',2651:'七番街 = Sector7.',2653:'七番街 = Sector7.',
      3059:'ひとり =1 swordsman.',3198:'ふたりきり =2 people alone.',3227:'もう１戦 = another round; Thaiอีกตา.',3234:'参号 = reactor3.',3455:'七番プレート = Sector7 plate.',
      3615:'二足 =2 legs.',3617:'二足 =2 legs.',3630:'二本 =2 horns.',3643:'四本 =4 legs.',3708:'両腕 = both2 arms.',
      3830:'針千本 official action label1,000 Needles; regex splits thousands separator but magnitude is unchanged.',3841:'両腕 =2 arms; explicit1 karma level retained.',3844:'ゼロ = HP0.'}
    nums=read(Q+'numeric-review.json');assert {r['template'] for r in nums}==set(reasons)
    write(Q+'numeric-decisions.json',dict(source_sha256=sha,records=[dict(asset=r['asset'],id=r['id'],template=r['template'],decision=reasons[r['template']]) for r in nums],all_differences_reviewed=True))
    visual=read(Q+'visual-review.json');assert visual['source_sha256']==sha and visual['all16_pages_viewed']
    images={Q+f'proof-{n}.png':digest(W/Q/f'proof-{n}.png') for n in range(1,17)};assert visual['images']==images
    assert not g['gender_mismatches'] and not g['unresolved_particle_bearing_speakers']
    assert read(Q+'NPC-residual.json')['untranslated_NPC_rows']==0
    artifacts=['reference/chapter12-build.json','reference/chapter12-source.json','reference/chapter12-templates.json','reference/chapter12-scope.json','reference/chapter12-context-overrides.json','reference/pronoun-context-overrides.json',cfg['cluster_map']]
    artifacts += ['tools/'+n+'.py' for n in ['chapter12_scope','assemble_chapter12','build_chapter12','audit_chapter12','audit_chapter12_glyphs','preview_chapter12','signoff_chapter12','audit_shared_dialogs','audit_npc_regression','publish_final_parts']]
    artifacts += [Q+n+'.json' for n in ['baseline','translation-audit','verification','working-assets','review-records','numeric-review','numeric-decisions','NPC-residual','choice-review','choice-groups-expanded','progress','editorial-revisions','editorial-action-revisions','old-glyph-regression','proof','visual-review','pronoun-review']]
    artifacts += [Q+'gender/summary.json',Q+'gender/records.json','qa/shared-dialogs/latest.json','qa/shared-dialogs/NPC-regression.json','qa/shared-dialogs/enemy-actions-regression.json']+list(images)
    artifacts += [str(p.relative_to(W)).replace('\\','/') for p in sorted((W/'translations/chapter12').glob('batch-*.json'))]
    if (W/'reference/chapter12-recheck-overrides.json').exists():
        from chapter12_recheck import audit as recheck_audit,Q as RQ
        recheck_audit();rp=read(RQ+'proof.json');rv=read(RQ+'visual-review.json')
        assert rp['source_sha256']==rv['source_sha256']==sha and rv['all_pages_viewed'] and rp['pages']==7 and len(rp['samples'])==56
        assert {(r['asset'],r['id']) for r in rp['samples']}=={(r['asset'],r['id']) for r in read('reference/chapter12-recheck-overrides.json')['records']}
        for n,h in rv['images'].items():assert digest(W/n)==h,n
        artifacts += ['reference/chapter12-recheck-overrides.json','tools/chapter12_recheck.py','tools/chapter12_recheck_fixes.py','tools/preview_chapter11_recheck.py']+[RQ+n+'.json' for n in ['baseline','progress','audit','proof','visual-review','choice-review','coverage-review']]+list(rv['images'])
    write(Q+'editorial-signoff.json',dict(source_sha256=sha,translation_sha256=digest(W/'translations/chapter12-th.json'),inventory_sha256=digest(W/'reference/chapter12-source.json'),proof_visually_reviewed=True,reviewed_proof_pages=16,numeric_differences_reviewed=True,gender_review_passed=True,choice_context_reviewed=True,unknown_speakers_neutral=True,reviewed_artifacts={n:digest(W/n) for n in artifacts},Japanese_dialogue_primary=True,same_id_US_used_for_labels_and_context=True,new_full_video_audio_review=False,in_game_tested=False))
    print('Signed3847 translated templates /4200 IDs;36 choice sets;46 numeric rows;16 viewed proof pages')
if __name__=='__main__':main()
