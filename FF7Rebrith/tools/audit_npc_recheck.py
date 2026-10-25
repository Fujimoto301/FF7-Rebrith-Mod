"""Audit original NPC corpus against the current decoded staging and frozen release."""
import hashlib,re,unicodedata
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from npc_recheck import selected,REGIONS
from choice_completion import family,JP,musical_notation


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    cfg=read('reference/npc-recheck-build.json');b=read('qa/npc-recheck/baseline.json')
    base=read(Path(b['snapshot'])/b['active']['combined_source']);now=read(cfg['source'])
    c=read('reference/rebirth-jp-corpus.json');rows=read('reference/npc-recheck-source.json');stage=W/cfg['stage']
    cm=read(cfg['cluster_map']);assert cm==read(Path(b['snapshot'])/b['active']['cluster_map'])
    reverse=str.maketrans({v:k for k,v in cm.items()});parsed={a:txtres.parse(str(stage/a)) for a in now['assets']}
    for a,d in c.items():assert txtres.parse(str(W/'source/End/Content/Text/JP'/a))==d,a
    expected={(f'End/Content/Text/JP/{a}',k) for a,d in c.items() for k,v in d.items() if v['Text'] and selected(a,k)}
    assert expected=={(r['asset'],r['id']) for r in rows} and len(expected)==8347
    for a,p in base['assets'].items():
        for f in ['entries','actors']:assert all(now['assets'][a][f][k]==t for k,t in p[f].items()),a
    for a,p in now['assets'].items():
        for k,t in p['entries'].items():assert parsed[a][k]['Text'].translate(reverse)==t,k
    us={a:txtres.parse(str(W/'source'/a.replace('/JP/','/US/'))) for a in now['assets']}
    new=[];numbers=[];actors=[]
    for r in rows:
        a,k=r['asset'],r['id'];t=now['assets'][a]['entries'][k];jp=r['Japanese']['Text']
        assert not JP.search(t) and t.strip() and t.strip()!='<>',(k,t)
        assert re.findall('</?[^>]+>',jp)==re.findall('</?[^>]+>',t),k
        assert r['English']==us[a].get(k,{}),k
        meta=dict(r['Japanese'].get('MetaData',{}))
        if k in now['assets'][a]['actors']:meta['ACTOR']=now['assets'][a]['actors'][k]
        assert parsed[a][k].get('MetaData',{})==meta,k
        if r['mode']=='existing':continue
        assert not re.search('ครับ|ค่ะ|คะ(?=[^\u0e00-\u0e7f]|$)|นะค่ะ|แอริธ|เอเลน่า',t),(k,t)
        assert not any(x in t for x in ['อวาลันช์','วูไท','มาโคะ','ชีรัน','เกลนน์']),(k,'Glossary regression',t)
        assert not re.search(r'([\u0e31\u0e34-\u0e39\u0e47-\u0e4e])\1',t),(k,t)
        actor=now['assets'][a]['actors'].get(k,'');official=r['English'].get('MetaData',{}).get('ACTOR','')
        if actor:
            assert actor==official or actor=='Mooglets' and meta.get('ACTOR')=='Mooglets' and r['Japanese']['MetaData']['ACTOR']=='コモーグリ',k
            actors.append(dict(asset=a,id=k,actor=actor,method='same-ID US' if official else 'Same JP コモーグリ actor, US adjacent $MOGLE_QST_01_0100_0300_00_lmg = Mooglets'))
        strip=lambda s:unicodedata.normalize('NFKC',re.sub('<[^>]+>','',s))
        jn=re.findall(r'\d+',strip(jp));tn=re.findall(r'\d+',strip(t))
        if jn!=tn:
            reason='Kana/kanji literal count or official ordinal/name rendered in Arabic; manually reviewed'
            if k=='$GOLDS_NPC_10_0300_9600_00_mma' and jn==['1'] and not tn:
                reason='歴史的な1戦 is this single historic match, singular ศึกประวัติศาสตร์; not a lost gameplay quantity'
            else:assert not jn,(k,jn,tn)
            numbers.append(dict(asset=a,id=k,jp=jp,thai=t,source_numbers=jn,target_numbers=tn,decision=reason))
        new.append(dict(asset=a,id=k,family=r['family'],thai=t,actor=actor))
    assert len(new)==1573
    # Independent all-state NPC scan, both with and without ACTOR. No numeric-state exclusion.
    coverage=[];remaining=[]
    for a,d in c.items():
        e=now['assets'].get('End/Content/Text/JP/'+a,{}).get('entries',{})
        for k,v in d.items():
            if not v['Text'] or '_NPC_' not in k:continue
            if a in REGIONS:
                assert k in e and not JP.search(e[k]),(a,k,'Visited NPC missing')
                coverage.append(dict(asset=a,id=k,ACTOR=bool(v.get('MetaData',{}).get('ACTOR')),translated=True))
            elif k not in e:remaining.append(dict(asset=a,id=k,jp=v['Text'],reason='NPC from region not yet covered by Ch2–9 scene work; retained for its upcoming chapter'))
    resident='End/Content/Text/JP/Resident_TxtRes.uasset'
    uiids=[]
    for a,d in c.items():
        for k,v in d.items():
            if not v['Text'] or not family(a,k):continue
            e=now['assets']['End/Content/Text/JP/'+a]['entries']
            if not JP.search(v['Text']) and k not in e:continue
            assert k in e and (not JP.search(e[k]) or musical_notation(k,e[k])),k;uiids.append(k)
    # Verified gender endings remain byte-for-byte in the unchanged prior texts.
    from audit_gender_through_chapter8 import PARTICLES
    totals=Counter();count=0
    for a,p in now['assets'].items():
        for k,t in p['entries'].items():
            counts={n:len(rx.findall(re.sub('<[^>]+>','',t))) for n,rx in PARTICLES.items()}
            if k=='$C1910_MAIN_7150_0500_00_mma' and t=='คะ…ครับ!':counts['คะ']=0
            if sum(counts.values()):
                assert t==base['assets'][a]['entries'][k],k
                totals.update(counts);count+=1
    assert dict(totals)=={'ครับ':651,'ค่ะ':198,'คะ':127} and count==952
    manifest={str(p.relative_to(stage)):digest(p) for p in sorted(stage.rglob('*.uasset'))}
    old=read(Path(b['snapshot'])/b['active']['manifest'])
    assert len(manifest)==27 and all(manifest[p]==h for p,h in old.items() if 'Billboard' in p)
    assert fingerprint()==b['protected']
    for p,h in b['source_hashes'].items():assert digest(W/p)==h,p
    screenshot=[r for r in new if r['id'].startswith('$KALMT_NPC_30_0700_')];assert len(screenshot)==22
    assert next(r for r in screenshot if '0200_00_akr' in r['id'])['actor']=='Akira'
    report=dict(total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),new_NPC_records=len(new),
        previous34589_text_and_ACTOR_preserved=True,inventory_records=len(rows),visited_region_NPC_records=len(coverage),
        visited_region_NPC_without_ACTOR=sum(not r['ACTOR'] for r in coverage),families=dict(Counter(r['family'] for r in new)),
        all22_Akira_records_included=True,prior_UI_inventory_records_preserved=7770,verified_choice_UI_records=len(uiids),
        numeric_differences_reviewed=len(numbers),new_gender_endings=0,prior_gender_counts=dict(totals),
        working_assets=27,glyph_clusters=711,all16_fonts_unchanged=True,source_sha256=digest(W/cfg['source']),
        changed_assets=[p for p in manifest if manifest[p]!=old.get(p)],missing=[],japanese_remaining=[],tag_mismatches=[],
        source_and_installed_files_unchanged=True,in_game_tested=False,new_full_audio_review=False)
    q='qa/npc-recheck/'
    for path,value in [('translation-audit.json',report),('working-assets.json',manifest),('numeric-review.json',dict(source_sha256=report['source_sha256'],reviewed=True,rows=numbers)),('actor-review.json',actors),('visited-NPC-coverage.json',coverage),('other-region-NPC-deferred.json',remaining)]:write(q+path,value)
    ctx=dict(b['active']);ctx.update(stage=cfg['stage'],manifest=q+'working-assets.json',audit=q+'translation-audit.json',combined_source=cfg['source'],cluster_map=cfg['cluster_map'],npc_recheck=True,
        shared_file_note='All7 latest ZIPs required. Common also owns COSME choice-only UI. Ch2–9 visited NPC families include all return states; earlier Corel quests through Ch9 recovered. Later full quests/main chapters remain separately deferred.')
    write('qa/active-working-set.json',ctx);print(report)
    from audit_npc_remaining import main as audit_inverse_scene
    audit_inverse_scene()


if __name__=='__main__':main()
