"""Current Ch13 gate; historical releases remain immutable evidence."""
import re,hashlib,unicodedata
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from chapter13_scope import scope
from choice_completion import JP,family,musical_notation
from audit_gender_through_chapter8 import PARTICLES,NAMED,PARTY
CFG='reference/chapter13-build.json';Q='qa/chapter13/'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    cfg=read(CFG);b=read(Q+'baseline.json');old=read(Path(b['snapshot'])/b['active']['combined_source']);now=read(cfg['source']);rows=read('reference/chapter13-source.json');patch=read('translations/chapter13-th.json');c=read('reference/rebirth-jp-corpus.json');cm=read(cfg['cluster_map']);seed=read(cfg['seed']);stage=W/cfg['stage'];reverse=str.maketrans({v:k for k,v in cm.items()})
    for p,h in b['hashes'].items():assert digest(Path(b['snapshot'])/p)==h,p
    assert digest(W/'reference/chapter13-source.json')==read('reference/chapter13-scope.json')['source_sha256']
    assert all(cm[k]==v for k,v in seed.items())
    expected={('End/Content/Text/JP/'+a,k) for a,d in c.items() for k,v in d.items() if v['Text'] and scope(a,k,v['Text']) and k not in old['assets'].get('End/Content/Text/JP/'+a,{}).get('entries',{})}
    assert expected=={(r['asset'],r['id']) for r in rows}=={(a,k) for a,p in patch['assets'].items() for k in p['entries']}
    overrides=[];assert old['assets'].keys()==now['assets'].keys()
    for a,p in old['assets'].items():
        for f in ('entries','actors'):
            for k,t in p[f].items():assert now['assets'][a][f][k]==t,(a,k,'Frozen rechecked Ch12 base changed')
            assert set(now['assets'][a][f])-set(p[f])==set(patch['assets'].get(a,{}).get(f,{})),(a,f)
    review=[];numbers=[];choices=[];npc=[]
    for a,p in now['assets'].items():
        src=txtres.parse(str(W/'source'/a));dst=txtres.parse(str(stage/a));assert src==c[Path(a).name] and list(src)==list(dst)
        for k,v in src.items():
            assert dst[k]['Text'].translate(reverse)==p['entries'].get(k,v['Text']),(a,k,'roundtrip')
            md=dict(v.get('MetaData',{}))
            if k in p['actors']:md['ACTOR']=p['actors'][k]
            assert md==dst[k].get('MetaData',{}),(a,k,'metadata')
            if v['Text'] and family(Path(a).name,k) and JP.search(v['Text']):
                assert k in p['entries'] and (not JP.search(p['entries'][k]) or musical_notation(k,p['entries'][k])),(k,'UI missing');choices.append(k)
            if v['Text'] and '_NPC_' in k and (k in old['assets'][a]['entries'] or (a,k) in expected):
                assert k in p['entries'];npc.append(k)
    for r in rows:
        a,k=r['asset'],r['id'];j=r['Japanese']['Text'];t=now['assets'][a]['entries'][k]
        assert r['Japanese']==c[Path(a).name][k] and t==patch['assets'][a]['entries'][k]
        assert t.strip() and not JP.search(t) and not re.search('แอริธ|แซ็ค|นะค่ะ|ไหมค่ะ|เหรอค่ะ|ค่ะ\\s*\\?|ฉันหน้าม้า|ศัตรู้',t),(k,t)
        assert re.findall('<[^>]+>',j)==re.findall('<[^>]+>',t),(k,'tags')
        item=dict(asset=a,id=k,template=r['template'],actor=patch['assets'][a]['actors'].get(k,''),jp=j,thai=t);review.append(item)
        jn=re.findall(r'\d+',unicodedata.normalize('NFKC',re.sub('<[^>]+>','',j)));tn=re.findall(r'\d+',re.sub('<[^>]+>','',t))
        if jn!=tn:numbers.append(dict(item,source_numeric_runs=jn,target_numeric_runs=tn))
    assert fingerprint()==b['protected'],'Source/dist/installed files changed'
    for p,h in b['source_hashes'].items():assert digest(W/p)==h,p
    manifest={str(p.relative_to(stage)):digest(p) for p in sorted(stage.rglob('*.uasset'))};previous=read(Path(b['snapshot'])/b['active']['manifest']);assert manifest.keys()==previous.keys() and len(manifest)==27
    verification=read(Q+'verification.json');assert len(verification['fonts'])==8 and verification['chapter']==list(range(1,14))
    report=dict(chapter=13,new_records=len(rows),new_templates=len(read('reference/chapter13-templates.json')),total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),previous46650_preserved_except_exact_reviewed_UI=bool(overrides),previous46650_text_and_ACTOR_preserved=not overrides,reviewed_existing_UI_changes=len(overrides),working_assets=27,glyph_clusters=len(cm),new_clusters=[k for k in cm if k not in seed],registered_choice_records=len(choices),visited_NPC_records=len(npc),numeric_differences=len(numbers),missing=[],japanese_remaining_in_scope=[],tag_mismatches=[],source_and_installed_files_unchanged=True,in_game_tested=False,new_full_video_audio_review=False,source_sha256=digest(W/cfg['source']))
    for n,d in [('translation-audit',report),('working-assets',manifest),('review-records',review),('numeric-review',numbers)]:write(Q+n+'.json',d)
    gender(now,patch)
    ctx=dict(b['active']);ctx.update(stage=cfg['stage'],manifest=Q+'working-assets.json',audit=Q+'translation-audit.json',combined_source=cfg['source'],cluster_map=cfg['cluster_map'],chapters=cfg['chapters'],chapter13=True,shared_file_note='Eight non-overlapping parts; Ch13 FOREE shares Chapter2; preserve all current package names, latest eight required together.')
    write('qa/active-working-set.json',ctx);print(report)
def gender(now,patch):
    prior=read('qa/chapter12/gender/records.json')['records'];registry={(r['asset'],r['id']):r for r in prior};out=[];counts=Counter();npc=Counter();named=dict(NAMED,Reno=('male','Established named Turk Reno; same identity as preceding Ch4 scenes.'),Sonon=('male','Established named Sonon Kusakabe, Yuffie senior/junior flashback in INTERmission; explicit matching Sonon actor, no inference from suffix.'),Snaps=('male','Same named photographer previously verified in Ch8 gender records.'),**{'Tifa & Aerith':('female','Both established women, same-ID joint actor in C3310 sailing response.')})

    for a,p in now['assets'].items():
        for k,t in p['entries'].items():
            ns={s:len(rx.findall(re.sub('<[^>]+>','',t))) for s,rx in PARTICLES.items()}
            if k=='$C1910_MAIN_7150_0500_00_mma':ns['คะ']=0
            if not sum(ns.values()):continue
            if (a,k) in registry:
                r=dict(registry[a,k]);assert r['thai']==t and r['counts']==ns
            else:
                assert k in patch['assets'].get(a,{}).get('entries',{})
                actor=re.sub('<[^>]+>','',p['actors'].get(k,''))
                if actor=='???' and k=='$C3340_MAIN_1900_0100_00_cat':actor='Cait Sith' # immediate reveal in next line; exact ID, not generic suffix inference
                assert actor in named,(k,actor,t,'Unknown speaker must be neutral')
                g,ev=named[actor];assert (not ns['ครับ'] if g=='female' else not ns['ค่ะ'] and not ns['คะ']),(k,t)
                r=dict(asset=a,id=k,actor_label=actor,speaker_gender=g,counts=ns,npc_or_nonparty=actor not in PARTY,thai=t,evidence=ev,matches_speaker_gender=True)
            counts.update(ns)
            if r['npc_or_nonparty']:npc.update(ns)
            out.append(r)
    write(Q+'gender/records.json',dict(records=out));write(Q+'gender/summary.json',dict(source_sha256=digest(W/read(CFG)['source']),particle_bearing_records=len(out),actual_particle_occurrences=sum(counts.values()),counts=dict(counts),npc_or_nonparty_occurrences=sum(npc.values()),npc_or_nonparty_counts=dict(npc),gender_mismatches=[],unresolved_particle_bearing_speakers=[],unknown_speakers_neutral=True))
if __name__=='__main__':main()
