"""Independent current-source gate: frozen base, entire assets and Ch11 families."""
import re,hashlib,unicodedata
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from chapter11_scope import primary,shared,defer
from audit_gender_through_chapter8 import PARTICLES,NAMED,PARTY
from choice_completion import family,JP,musical_notation
CFG='reference/chapter11-build.json';Q='qa/chapter11/'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    cfg=read(CFG);b=read(Q+'baseline.json');old=read(Path(b['snapshot'])/b['active']['combined_source']);now=read(cfg['source']);rows=read('reference/chapter11-source.json');patch=read('translations/chapter11-th.json');c=read('reference/rebirth-jp-corpus.json');cm=read(cfg['cluster_map']);seed=read(cfg['seed']);stage=W/cfg['stage'];reverse=str.maketrans({v:k for k,v in cm.items()})
    from chapter11_recheck import matches as recheck_matches,decisions as recheck_decisions
    from pronoun_context import matches as pronoun_matches,decisions as pronoun_decisions
    extra=read('reference/chapter11-recheck-source.json') if (W/'reference/chapter11-recheck-source.json').exists() else []
    rows+=extra
    for p,h in b['hashes'].items():assert digest(Path(b['snapshot'])/p)==h,p
    assert digest(W/'reference/chapter11-source.json')==read('reference/chapter11-scope.json')['source_sha256']
    assert all(cm[k]==v for k,v in seed.items())
    expected={(f'End/Content/Text/JP/{a}',k) for a,d in c.items() for k,v in d.items() if v['Text'] and (primary(a,k) or a=='Resident_TxtRes.uasset' and shared(k)) and not defer(k) and k not in old['assets'].get(f'End/Content/Text/JP/{a}',{}).get('entries',{})}
    expected.update((r['asset'],r['id']) for r in extra)
    assert expected=={(r['asset'],r['id']) for r in rows}=={(a,k) for a,p in patch['assets'].items() for k in p['entries']}
    assert old['assets'].keys()==now['assets'].keys()
    for a,p in old['assets'].items():
        for f in ('entries','actors'):
            assert all(now['assets'][a][f][k]==t or f=='entries' and (recheck_matches(a,k,t,now['assets'][a][f][k]) or pronoun_matches(a,k,t,now['assets'][a][f][k])) for k,t in p[f].items()),(a,f,'Frozen Ch1–10 changed without exact reviewed exception')
            assert set(now['assets'][a][f])-set(p[f])==set(patch['assets'].get(a,{}).get(f,{})),(a,f)
    for a,p in now['assets'].items():
        src=txtres.parse(str(W/'source'/a));dst=txtres.parse(str(stage/a));assert src==c[Path(a).name] and list(src)==list(dst)
        for k,v in src.items():
            assert dst[k]['Text'].translate(reverse)==p['entries'].get(k,v['Text']),(a,k,'roundtrip')
            md=dict(v.get('MetaData',{}))
            if k in p['actors']:md['ACTOR']=p['actors'][k]
            assert md==dst[k].get('MetaData',{}),(k,'metadata')
    review=[];numbers=[];npc=[];choices=[];residual=[]
    for r in rows:
        a,k=r['asset'],r['id'];t=patch['assets'][a]['entries'][k];j=r['Japanese']['Text'];assert r['Japanese']==c[Path(a).name][k]
        assert t.strip() and not JP.search(t) and not re.search('[\uff10-\uff19]',t),(k,t)
        assert re.findall('<[^>]+>',j)==re.findall('<[^>]+>',t),(k,'tags')
        assert not re.search('แอริธ|แซ็ค|นะค่ะ|ไหมค่ะ|เหรอค่ะ|ค่ะ\\s*\\?',t),(k,t)
        item=dict(asset=a,id=k,template=r['template'],actor=patch['assets'][a]['actors'].get(k,''),jp=j,thai=t);review.append(item)
        jn=re.findall(r'\d+',unicodedata.normalize('NFKC',re.sub('<[^>]+>','',j)));tn=re.findall(r'\d+',re.sub('<[^>]+>','',t))
        if jn!=tn:numbers.append(dict(item,source_numeric_runs=jn,target_numeric_runs=tn))
    for a,d in c.items():
        rel='End/Content/Text/JP/'+a
        if rel not in now['assets']:continue
        p=now['assets'][rel]
        for k,v in d.items():
            if not v['Text']:continue
            if '_NPC_' in k and (rel in old['assets'] and k in old['assets'][rel]['entries'] or primary(a,k) and not defer(k)):
                assert k in p['entries'],(k,'NPC missing');npc.append(dict(asset=rel,id=k,actor=p['actors'].get(k,''),thai=p['entries'][k]))
            if JP.search(v['Text']) and family(a,k):
                assert k in p['entries'],(k,'Choice/UI missing')
                assert not JP.search(p['entries'][k]) or musical_notation(k,p['entries'][k]);choices.append(dict(asset=rel,id=k,jp=v['Text'],thai=p['entries'][k]))
            if a=='8700-NIBLE_TxtRes.uasset' and JP.search(v['Text']) and k not in p['entries']:
                why=defer(k) or ('Chapter12 C3210 main-story return' if k.startswith('$C3210_') else None)
                assert why,(k,v['Text'],'Unclassified Nibel residual');residual.append(dict(asset=rel,id=k,jp=v['Text'],reason=why))
    assert fingerprint()==b['protected'],'Source/dist/installed files changed'
    for p,h in b['source_hashes'].items():assert digest(W/p)==h,p
    manifest={str(p.relative_to(stage)):digest(p) for p in sorted(stage.rglob('*.uasset'))};previous=read(Path(b['snapshot'])/b['active']['manifest']);assert manifest.keys()==previous.keys() and len(manifest)==27
    changed=[a for a,h in manifest.items() if previous[a]!=h]
    pronoun_assets={r['asset'].replace('/','\\') for r in pronoun_decisions()}
    assert all('Billboard' in a or Path(a).name in ['8700-NIBLE_TxtRes.uasset','Resident_TxtRes.uasset'] or a in pronoun_assets for a in changed),changed
    verification=read(Q+'verification.json');assert len(verification['fonts'])==8 and verification['chapter']==list(range(1,12))
    report=dict(chapter=11,new_records=len(rows),new_templates=len(read('reference/chapter11-templates.json')),total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),previous40691_text_and_ACTOR_preserved=True,working_assets=len(manifest),glyph_clusters=len(cm),new_clusters=[k for k in cm if k not in seed],visited_NPC_records=len(npc),new_NPC_records=sum('_NPC_' in r['id'] for r in rows),registered_choice_records=len(choices),numeric_differences=len(numbers),changed_assets=changed,missing=[],japanese_remaining_in_scope=[],tag_mismatches=[],source_and_installed_files_unchanged=True,in_game_tested=False,new_full_video_audio_review=False,source_sha256=digest(W/cfg['source']))
    base_changes=[r for r in recheck_decisions() if r['id'] in old['assets'][r['asset']]['entries']]
    if base_changes:report.update(previous40691_text_and_ACTOR_preserved=False,previous40691_preserved_except_reviewed_Ch11_UI=True,reviewed_existing_Ch11_UI_changes=len(base_changes))
    if pronoun_decisions():report.update(previous40691_preserved_except_reviewed_Ch11_UI=False,previous40691_preserved_except_reviewed_Ch11_UI_and_pronoun_context=True,reviewed_pronoun_changes=len(pronoun_decisions()))
    report.update(recheck_added_records=len(extra),new_templates=1658+len(extra))
    for n,d in [('translation-audit',report),('working-assets',manifest),('review-records',review),('numeric-review',numbers),('NPC-inventory',npc),('choice-review',choices),('Nibel-residual-dispositions',residual)]:write(Q+n+'.json',d)
    gender(now,patch)
    ctx=dict(b['active']);ctx.update(stage=cfg['stage'],manifest=Q+'working-assets.json',audit=Q+'translation-audit.json',combined_source=cfg['source'],cluster_map=cfg['cluster_map'],chapters=cfg['chapters'],chapter11=True,chapter1_part_name='ThaiJP_Chapter1_11_P',superseded_parts=['ThaiJP_Chapter1_P'],shared_file_note='All8 latest ZIPs required. Chapter1_11 owns whole NIBLE and MIDGR; Common owns Resident and fonts. No duplicate assets.')
    write('qa/active-working-set.json',ctx);print(report)
def gender(now,patch):
    old=read('qa/chapter10/gender/records.json')['records'];prior={(r['asset'],r['id']):r for r in old};review=[];total=Counter();npc=Counter()
    assert any(r['template']==896 and '息子' in r['Japanese']['Text'] for r in read('reference/chapter11-source.json'))
    named=dict(NAMED,Billy=('male','Ch11 template896, NIBLE_QST01: JP explicitly self-identifies as Will’s son (息子). Same named JP ACTOR グリングリン / US Billy across the quest.'))
    for a,p in now['assets'].items():
        for k,t in p['entries'].items():
            counts={s:len(rx.findall(re.sub('<[^>]+>','',t))) for s,rx in PARTICLES.items()}
            if k=='$C1910_MAIN_7150_0500_00_mma':counts['คะ']=0
            if not sum(counts.values()):continue
            if (a,k) in prior:
                row=dict(prior[a,k]);assert row['thai']==t and row['counts']==counts,(k,'Prior gender evidence changed')
            else:
                assert k in patch['assets'].get(a,{}).get('entries',{})
                actor=re.sub('<[^>]+>','',p['actors'].get(k,''));assert actor in named,(k,actor,t,'No gender evidence')
                g,ev=named[actor];assert (not counts['ครับ'] if g=='female' else not counts['ค่ะ'] and not counts['คะ']),(k,t)
                row=dict(asset=a,id=k,actor_label=actor,speaker_gender=g,counts=counts,npc_or_nonparty=actor not in PARTY,thai=t,evidence=ev,matches_speaker_gender=True)
            total.update(counts)
            if row['npc_or_nonparty']:npc.update(counts)
            review.append(row)
    assert set(prior)<={(r['asset'],r['id']) for r in review}
    write(Q+'gender/records.json',dict(records=review))
    write(Q+'gender/summary.json',dict(source_sha256=digest(W/read(CFG)['source']),particle_bearing_records=len(review),actual_particle_occurrences=sum(total.values()),counts=dict(total),npc_or_nonparty_occurrences=sum(npc.values()),npc_or_nonparty_counts=dict(npc),prior1278_particles_preserved=True,gender_mismatches=[],unresolved_particle_bearing_speakers=[],unknown_speakers_neutral=True,in_game_tested=False))
if __name__=='__main__':main()
