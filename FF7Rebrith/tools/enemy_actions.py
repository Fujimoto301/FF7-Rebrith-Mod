"""Recover whole-game enemy action UI from official same-ID US labels."""
import copy,hashlib,re,shutil,sys,uuid
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from choice_completion import JP

Q='qa/enemy-actions/'
CFG='reference/enemy-actions-build.json'
R='End/Content/Text/JP/Resident_TxtRes.uasset'


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def selected(a,k):
    return a=='Resident_TxtRes.uasset' and k.startswith(('$bt_','$EN9000_10_')) and not k.endswith('_help')


def prepare():
    assert not (W/Q/'baseline.json').exists(),'Keep immutable baseline'
    ctx=read('qa/active-working-set.json');base=read(ctx['combined_source'])
    snap=W/Q/'revisions'/uuid.uuid4().hex
    for rel in [ctx['combined_source'],ctx['cluster_map'],ctx['manifest'],'qa/active-working-set.json','qa/final-parts/latest.json']:
        p=snap/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,p)
    write(Q+'baseline.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint(),
        source_hashes={str(p.relative_to(W)):digest(p) for p in (W/'source').rglob('*.uasset')}))
    j=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset'];u=txtres.parse(str(W/'source'/R.replace('/JP/','/US/')))
    rows=[];now=copy.deepcopy(base);patch={}
    for k,v in j.items():
        if not v['Text'] or not selected('Resident_TxtRes.uasset',k):continue
        assert k in u and u[k]['Text'] and not JP.search(u[k]['Text']),k
        t=u[k]['Text'];assert all(ord(ch)<128 for ch in t),k
        mode='existing' if k in base['assets'][R]['entries'] else 'official_US'
        if mode=='existing':assert base['assets'][R]['entries'][k]==t,k
        else:patch[k]=t;now['assets'][R]['entries'][k]=t
        rows.append(dict(id=k,asset=R,Japanese=v,English=u[k],mode=mode))
    assert len(rows)==1703 and len(patch)==1668
    assert patch['$bt_MidgarZolom_Flamethrower']=='Scorching Breath'
    now.update(scope='Ch1–9 plus recovered visited-region NPCs and whole-game official English enemy action UI',enemy_actions=True)
    write('reference/enemy-actions-source.json',rows);write('translations/enemy-actions-th.json',dict(assets={R:dict(entries=patch,actors={})}))
    write('translations/working-enemy-actions-th.json',now)
    cfg=dict(source='translations/working-enemy-actions-th.json',stage='staging/ThaiJP_EnemyActions_Working',qa=Q.rstrip('/'),
        cluster_map='reference/enemy-actions-cluster-map.json',seed=ctx['cluster_map'],chapters=list(range(1,10)),punctuation_policy='reference/dialogue-punctuation-policy.json')
    write(CFG,cfg);shutil.copytree(W/ctx['stage'],W/cfg['stage'])
    shutil.copy2(W/ctx['cluster_map'],W/cfg['cluster_map']);shutil.copy2(W/'qa/npc-recheck/build-verification.json',W/Q/'build-verification.json')
    print('Prepared',len(rows),'action labels;',len(patch),'new (1667 Japanese + 1 fullwidth question-mark label)')


def audit():
    cfg=read(CFG);b=read(Q+'baseline.json');ctx=read('qa/active-working-set.json')
    base=read(Path(b['snapshot'])/b['active']['combined_source']);now=read(cfg['source']);c=read('reference/rebirth-jp-corpus.json')
    assert read(cfg['cluster_map'])==read(Path(b['snapshot'])/b['active']['cluster_map'])
    reverse=str.maketrans({v:k for k,v in read(cfg['cluster_map']).items()});stage=W/cfg['stage']
    expected={(a,k) for a,d in c.items() for k,v in d.items() if v['Text'] and selected(a,k)}
    rows=read('reference/enemy-actions-source.json');assert expected=={(Path(r['asset']).name,r['id']) for r in rows} and len(rows)==1703
    u=txtres.parse(str(W/'source'/R.replace('/JP/','/US/')));new=[];numbers=[]
    for r in rows:
        k=r['id'];t=now['assets'][R]['entries'][k];assert r['English']==u[k] and t==u[k]['Text'] and not JP.search(t),k
        assert re.findall('<[^>]+>',t)==re.findall('<[^>]+>',r['Japanese']['Text']),k
        if r['mode']!='existing':
            new.append(k)
            jn=re.findall(r'\d+',r['Japanese']['Text']);tn=re.findall(r'\d+',t)
            if jn!=tn:numbers.append(dict(id=k,jp=r['Japanese']['Text'],official_US=t,source_numbers=jn,target_numbers=tn,decision='Official localized action label copied byte-for-byte from identical US ID; not a gameplay-value substitution'))
    assert len(new)==1668
    for a,p in base['assets'].items():
        for field in ['entries','actors']:assert all(now['assets'][a][field][k]==t for k,t in p[field].items()),a
    for a,p in now['assets'].items():
        original=txtres.parse(str(W/'source'/a));assert original==c[Path(a).name],a
        decoded=txtres.parse(str(stage/a));assert decoded.keys()==original.keys(),a
        for k,v in original.items():
            assert decoded[k]['Text'].translate(reverse)==p['entries'].get(k,v['Text']),(a,k)
            meta=dict(v.get('MetaData',{}))
            if k in p['actors']:meta['ACTOR']=p['actors'][k]
            assert decoded[k].get('MetaData',{})==meta,(a,k)
    manifest={str(p.relative_to(stage)):digest(p) for p in sorted(stage.rglob('*.uasset'))}
    old=read(Path(b['snapshot'])/b['active']['manifest']);changed=[a for a,h in manifest.items() if old.get(a)!=h]
    assert len(manifest)==27 and changed==[str(Path(R))]
    assert all(manifest[a]==h for a,h in old.items() if 'Billboard' in a)
    assert fingerprint()==b['protected']
    for p,h in b['source_hashes'].items():assert digest(W/p)==h,p
    report=dict(total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),new_action_labels=1668,
        previously_Japanese_labels=1667,fullwidth_unknown_label_normalized=1,action_inventory_records=1703,
        previous36162_text_and_ACTOR_preserved=True,all12_existing_action_help_descriptions_preserved=True,
        screenshot_id='$bt_MidgarZolom_Flamethrower',screenshot_English='Scorching Breath',
        same_ID_official_US=True,numeric_label_differences=len(numbers),source_sha256=digest(W/cfg['source']),
        working_assets=27,glyph_clusters=711,all16_fonts_unchanged=True,changed_assets=changed,
        missing=[],japanese_remaining=[],tag_mismatches=[],source_and_installed_files_unchanged=True,in_game_tested=False)
    assert report['total_combined_text_records']==37830
    write(Q+'translation-audit.json',report);write(Q+'working-assets.json',manifest);write(Q+'numeric-review.json',numbers)
    out=dict(b['active']);out.update(stage=cfg['stage'],manifest=Q+'working-assets.json',audit=Q+'translation-audit.json',
        combined_source=cfg['source'],cluster_map=cfg['cluster_map'],enemy_actions=True,
        shared_file_note='All7 ZIPs required. Common holds Resident including whole-game official English enemy action names, fonts and COSME choice-only UI. Earlier NPC repair fully preserved.')
    write('qa/active-working-set.json',out);print(report)


def signoff():
    cfg=read(CFG);proof=read(Q+'proof.json');assert proof['source_sha256']==digest(W/cfg['source'])
    arts=[Q+n for n in ['translation-audit.json','numeric-review.json','working-assets.json','verification.json','proof.json','proof-1.png','proof-2.png']]
    arts+=['tools/enemy_actions.py','tools/audit_enemy_actions_regression.py','qa/shared-dialogs/latest.json','qa/shared-dialogs/NPC-regression.json']
    write(Q+'editorial-signoff.json',dict(source_sha256=digest(W/cfg['source']),translation_sha256=digest(W/'translations/enemy-actions-th.json'),
        inventory_sha256=digest(W/'reference/enemy-actions-source.json'),proof_visually_reviewed=True,reviewed_proof_pages=2,
        reviewed_artifacts={p:digest(W/p) for p in arts},same_ID_US_labels_reviewed=True,in_game_tested=False))


if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    elif '--audit' in sys.argv:audit()
    elif '--signoff' in sys.argv:signoff()
    elif '--verify' in sys.argv:
        import verify_chapter1 as v
        v.main(chapter6_working=True,review_working=CFG)
    else:
        import build_chapter1 as b
        b.main(chapter6_working=True,review_working=CFG,text_only=True)
