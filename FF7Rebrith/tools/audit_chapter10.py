"""Chapter10 independent completeness, metadata, prior-source and NPC regression."""
import re,hashlib,unicodedata
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from chapter10_scope import primary,shared,defer
from choice_completion import family,JP,musical_notation
from npc_recheck import REGIONS
from audit_npc_remaining import reason
from audit_gender_through_chapter8 import PARTICLES,NAMED,PARTY
from chapter10_recheck_scope import extra
from chapter4_door_fix import active as door_active,matches as door_matches,audit as audit_door,verify_protected

CFG='reference/chapter10-build.json';Q='qa/chapter10/'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    cfg=read(CFG);b=read(Q+'baseline.json');old=read(Path(b['snapshot'])/b['active']['combined_source']);now=read(cfg['source']);patch=read('translations/chapter10-th.json');rows=read('reference/chapter10-source.json');late=read('reference/chapter10-deferred.json');c=read('reference/rebirth-jp-corpus.json');cm=read(cfg['cluster_map']);seed=read(cfg['seed']);stage=W/cfg['stage'];reverse=str.maketrans({v:k for k,v in cm.items()})
    assert all(cm[k]==v for k,v in seed.items())
    assert digest(W/'reference/chapter10-source.json')==read('reference/chapter10-scope.json')['source_sha256']
    extension=read('reference/chapter10-recheck-source.json') if (W/'reference/chapter10-recheck-source.json').exists() else []
    rows+=extension
    candidates={(f'End/Content/Text/JP/{a}',k) for a,d in c.items() for k,v in d.items() if v['Text'] and (primary(a,k) or a=='Resident_TxtRes.uasset' and shared(k) or extra(a,k) and extension) and k not in old['assets'].get(f'End/Content/Text/JP/{a}',{}).get('entries',{})}
    assert candidates=={(r['asset'],r['id']) for r in rows+late}
    assert {(r['asset'],r['id']) for r in rows}=={(a,k) for a,p in patch['assets'].items() for k in p['entries']}
    for a,p in old['assets'].items():
        for f in ['entries','actors']:assert all(now['assets'][a][f][k]==t or f=='entries' and door_matches(a,k,t,now['assets'][a][f][k]) for k,t in p[f].items()),(a,f,'Frozen previous base changed')
    for a,p in now['assets'].items():
        for f in ['entries','actors']:assert set(p[f])-set(old['assets'].get(a,{}).get(f,{}))==set(patch['assets'].get(a,{}).get(f,{}))
    for a,p in now['assets'].items():
        src=txtres.parse(str(W/'source'/a));assert src==c[Path(a).name]
        dst=txtres.parse(str(stage/a));assert list(src)==list(dst)
        for k,v in src.items():
            assert dst[k]['Text'].translate(reverse)==p['entries'].get(k,v['Text']),(a,k,'roundtrip')
            md=dict(v.get('MetaData',{}))
            if k in p['actors']:md['ACTOR']=p['actors'][k]
            assert dst[k].get('MetaData',{})==md,(k,'metadata')
    review=[];numbers=[];choices=[]
    for r in rows:
        a,k=r['asset'],r['id'];t=patch['assets'][a]['entries'][k];j=r['Japanese']['Text'];assert r['Japanese']==c[Path(a).name][k]
        assert not JP.search(t) and not re.search('[\uff10-\uff19]',t),(k,t)
        assert re.findall('<[^>]+>',j)==re.findall('<[^>]+>',t),(k,'tags')
        assert not re.search('แอริธ|เอเลน่า|เคทซี|กองกาก้า|แซ็ค|นะค่ะ|ไหมค่ะ|เหรอค่ะ|ค่ะ\\s*\\?',t),(k,t)
        assert not re.search(r'([\u0e31\u0e34-\u0e39\u0e47-\u0e4e])\1',t),(k,t)
        item=dict(asset=a,id=k,template=r['template'],actor=patch['assets'][a]['actors'].get(k,''),jp=j,thai=t);review.append(item)
        jn=re.findall(r'\d+',unicodedata.normalize('NFKC',re.sub('<[^>]+>','',j)));tn=re.findall(r'\d+',re.sub('<[^>]+>','',t))
        if jn!=tn:numbers.append(dict(item,source_numeric_runs=jn,target_numeric_runs=tn))
    # Full-family inventory, both named and anonymous, not only new translations.
    npc=[];residual=[]
    for a,d in c.items():
        if a not in REGIONS|{'8600-COSME_TxtRes.uasset'}:continue
        rel='End/Content/Text/JP/'+a;e=now['assets'][rel]['entries']
        for k,v in d.items():
            if not v['Text']:continue
            if '_NPC_' in k:
                assert k in e,(k,'NPC omission');npc.append(dict(asset=rel,id=k,actor=now['assets'][rel]['actors'].get(k,''),thai=e[k]))
            if JP.search(v['Text']) and k not in e:
                why=defer(k) or reason(k);assert why,(a,k,v['Text'],'Unclassified residual')
                residual.append(dict(asset=a,id=k,jp=v['Text'],reason=why))
    for r in late:assert r['reason']==defer(r['id']) and r['id'] not in now['assets'][r['asset']]['entries']
    mid='End/Content/Text/JP/4000-MIDGR_TxtRes.uasset'
    for k,v in c[Path(mid).name].items():
        if v['Text'] and k.startswith('$MIDGR_NPC_10_'):
            assert k in now['assets'][mid]['entries'],(k,'Midgar Chapter10 NPC missing')
            npc.append(dict(asset=mid,id=k,actor=now['assets'][mid]['actors'].get(k,''),thai=now['assets'][mid]['entries'][k]))
    for a,d in c.items():
        if 'End/Content/Text/JP/'+a not in now['assets']:continue
        p=now['assets']['End/Content/Text/JP/'+a]
        for k,v in d.items():
            if v['Text'] and JP.search(v['Text']) and family(a,k):
                assert k in p['entries'],(k,'registered choice missing')
                assert not JP.search(p['entries'][k]) or musical_notation(k,p['entries'][k])
                choices.append(dict(asset=a,id=k,thai=p['entries'][k]))
    verify_protected(b['protected'])
    for p,h in b['source_hashes'].items():assert digest(W/p)==h,p
    manifest={str(p.relative_to(stage)):digest(p) for p in sorted(stage.rglob('*.uasset'))};assert len(manifest)==27
    previous=read(Path(b['snapshot'])/b['active']['manifest']);assert manifest.keys()==previous.keys()
    changed=[a for a,h in manifest.items() if previous[a]!=h]
    from context_recheck import active as context_active,decisions
    context_assets={r['asset'] for r in decisions()} if context_active() else set()
    from context_full_read import decisions as full_decisions
    context_assets|={r['asset'] for r in full_decisions()}
    assert all(a.replace('\\','/') in context_assets or 'Billboard' in a or Path(a).name in ['4000-MIDGR_TxtRes.uasset','8600-COSME_TxtRes.uasset','8800-FOREE_TxtRes.uasset','Resident_TxtRes.uasset'] or door_active() and Path(a).name=='8200-JUNOE_TxtRes.uasset' for a in changed)
    v=read(Q+'verification.json');assert len(v['fonts'])==8 and v['chapter']==list(range(1,11))
    report=dict(chapter=10,new_records=len(rows),new_templates=2617+len(extension),recheck_added_records=len(extension),total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),previous37830_text_and_ACTOR_preserved=True,working_assets=len(manifest),glyph_clusters=len(cm),new_clusters=[k for k in cm if k not in seed],deferred_new_Ch12_quest_records=len(late),new_NPC_records=sum('_NPC_' in r['id'] for r in rows),new_NPC_without_ACTOR=sum('_NPC_' in r['id'] and not r['actor'] for r in review),visited_region_NPC_records=len(npc),visited_region_NPC_without_ACTOR=sum(not r['actor'] for r in npc),registered_choice_records=len(choices),numeric_differences=len(numbers),changed_assets=changed,missing=[],japanese_remaining_in_scope=[],tag_mismatches=[],source_and_installed_files_unchanged=True,in_game_tested=False,new_full_video_audio_review=False,source_sha256=digest(W/cfg['source']))
    if door_active():
        audit_door()
        report['previous37830_text_and_ACTOR_preserved']=False
        approved=read('qa/chapter4-door-fix/audit.json')['corrected_records']
        report['previous37830_preserved_except_reviewed_Ch4_corrections']=True
        report['approved_older_text_corrections']=approved
        if context_active():
            report['approved_older_text_corrections']=sum(t!=now['assets'][a]['entries'][k] for a,p in old['assets'].items() for k,t in p['entries'].items())
            report['approved_context_corrections_since_door_baseline']=approved
            report['previous37830_preserved_except_reviewed_Ch4_corrections']=False
            report['previous37830_preserved_except_explicit_context_corrections']=True
            report['context_review']='qa/context-recheck/audit.json'
    for name,data in [('translation-audit',report),('working-assets',manifest),('review-records',review),('numeric-review',numbers),('NPC-inventory',npc),('choice-review',choices),('visited-scene-residual-dispositions',residual)]:write(Q+name+'.json',data)
    out=dict(b['active']);out.update(stage=cfg['stage'],manifest=Q+'working-assets.json',audit=Q+'translation-audit.json',combined_source=cfg['source'],cluster_map=cfg['cluster_map'],chapters=list(range(1,11)),chapter10=True,additional_parts=b['active']['additional_parts']+[['ThaiJP_Chapter10_P',['8600-COSME_TxtRes.uasset']]],shared_file_note='All8 latest ZIPs required. Chapter10 owns entire COSME asset moved from Common; Chapter1 MIDGR also includes Chapter10 Zack; Common holds Resident and fonts. No duplicate assets.')
    write('qa/active-working-set.json',out);print(report)
    gender(now,patch)

def gender(now,patch):
    previous=read('qa/chapter9/gender/records.json')['records'];prior={(r['asset'],r['id']):r for r in previous};review=[];total=Counter();npc=Counter();actors={}
    named=dict(NAMED,Wedge=('male','Established named Avalanche member Wedge; explicit named ACTOR ウェッジ, prior Remake identity. Unknown ??? lines have neutral endings.'))
    for a,p in now['assets'].items():
        for k,t in p['entries'].items():
            counts={s:len(rx.findall(re.sub('<[^>]+>','',t))) for s,rx in PARTICLES.items()}
            if k=='$C1910_MAIN_7150_0500_00_mma':counts['คะ']=0
            if not sum(counts.values()):continue
            if (a,k) in prior:
                row=dict(prior[a,k]);assert (row['thai']==t or door_matches(a,k,row['thai'],t)) and row['counts']==counts
                row['thai']=t
            else:
                assert k in patch['assets'].get(a,{}).get('entries',{}),(k,'New unaudited previous particle')
                actor=re.sub('<[^>]+>','',p['actors'].get(k,''));assert actor in named,(k,actor,t,'No gender evidence')
                g,ev=named[actor];assert not counts['ครับ'] if g=='female' else not counts['ค่ะ'] and not counts['คะ'],(k,t)
                assert not re.search(r'นะค่ะ|ไหมค่ะ|เหรอค่ะ|หรือเปล่าค่ะ|ค่ะ\s*\?',t),(k,t)
                row=dict(asset=a,id=k,actor_label=actor,speaker_gender=g,counts=counts,npc_or_nonparty=actor not in PARTY,thai=t,evidence=ev,matches_speaker_gender=True)
            total.update(counts)
            if row['npc_or_nonparty']:npc.update(counts)
            actors.setdefault(row['actor_label'],Counter()).update(counts);review.append(row)
    assert set(prior)=={(r['asset'],r['id']) for r in review if (r['asset'],r['id']) in prior}
    summary=dict(particle_bearing_records=len(review),actual_particle_occurrences=sum(total.values()),counts=dict(total),npc_or_nonparty_occurrences=sum(npc.values()),npc_or_nonparty_counts=dict(npc),prior976_particles_preserved=True,gender_mismatches=[],unresolved_particle_bearing_speakers=[],new_full_video_audio_review=False,in_game_tested=False,source_sha256=digest(W/read(CFG)['source']))
    write(Q+'gender/records.json',dict(records=review,by_actor={k:dict(v) for k,v in actors.items()}));write(Q+'gender/summary.json',summary);print(summary)

if __name__=='__main__':main()
