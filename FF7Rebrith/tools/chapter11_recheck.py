"""Immutable recheck baseline and exact per-ID editorial corrections for Chapter11."""
import copy,re,shutil,sys,uuid
from collections import defaultdict
from pathlib import Path
from prepare_chapter9 import W,read,write
from audit_chapter11 import digest
from assemble_ui_completion import fingerprint
Q='qa/chapter11/recheck/'
ENEMIES=['Nibel Wolf','Pyretail','Zu','King Zu','Kyuvildun','Carnifex','Poison Cap','Valron','Marquis Valron','Disgorgon','Suevite Disgorgon','Black Bat','Twin Brain','Screamer','Adjudicator','Diabolic Variant','Yin & Yang','Forgotten Specimen','Galian Beast','Roche','Amalgam','Daemonic Entity','Necrotic Entity','Dragon','Odin','Sleipnir']
def prepare_extra():
    assert not (W/'reference/chapter11-recheck-source.json').exists(),'Keep stable recheck indices'
    from prepare_chapter9 import txtres
    c=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset'];us=txtres.parse(str(W/'source/End/Content/Text/US/Resident_TxtRes.uasset'))
    now=read('translations/working-through-chapter11-th.json');a='End/Content/Text/JP/Resident_TxtRes.uasset'
    suffixes={r['id'][4:] for r in read('reference/enemy-name-source.json') if r['id'].startswith('$en_') and r['en'] in ENEMIES}
    rows=[]
    for k,v in c.items():
        if not k.startswith(('$menu_EnemyBookText_','$menu_EnemyBookTipsText_')):continue
        if not any(k.endswith('_'+s) for s in suffixes):continue
        if not v['Text'] or k in now['assets'][a]['entries']:continue
        rows.append(dict(asset=a,id=k,Japanese=v,English=us.get(k,{}),template='recheck-'+str(len(rows)),reason='Enemy Intel biography or Assess instructions for Ch11 route, regional encounters/protorelic, or Odin. Whole per-enemy Text+Tips families; not new dialogue.'))
    write('reference/chapter11-recheck-source.json',rows)
    write(Q+'enemy-intel-scope.json',dict(enemies=ENEMIES,suffixes=sorted(suffixes),records=len(rows),source_sha256=digest(W/'reference/chapter11-recheck-source.json'),scope_sources=['https://samurai-gamers.com/final-fantasy-7-rebirth/ff7reb-chapter-11-walkthrough/','https://gamefaqs.gamespot.com/ps5/371123-final-fantasy-vii-rebirth/faqs/81141/nibel-region-intel'],exclusions='NIBLE_QST03/Lament boss and pirate treasure guardian are Ch12; no later dialogue added.',in_game_tested=False))
    print('Prepared',len(rows),'Enemy Intel UI records')
def prepare():
    assert not (W/Q/'baseline.json').exists(),'Do not replace the immutable recheck baseline'
    ctx=read('qa/active-working-set.json');assert ctx['chapter11']
    snap=W/Q/'revisions'/uuid.uuid4().hex
    paths=[ctx['combined_source'],ctx['cluster_map'],ctx['manifest'],'translations/chapter11-th.json','qa/active-working-set.json','qa/chapter11/editorial-signoff.json','qa/chapter11/proof.json','qa/chapter11/visual-review.json','qa/final-parts/latest.json']
    paths += [str(p.relative_to(W)).replace('\\','/') for p in (W/'translations/chapter11').glob('batch-*.json')]
    for rel in paths:
        dst=snap/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,dst)
    write(Q+'baseline.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint(),hashes={p:digest(snap/p) for p in paths}))
    write(Q+'progress.json',dict(read_template_ranges=[],templates=1658,records=1703,complete=False,duplicate_contexts_reviewed=False,choices_reviewed=False,source_sha256=digest(W/ctx['combined_source'])))
    write('reference/chapter11-recheck-overrides.json',dict(records=[]))
    print('Frozen current Ch11 release for recheck')
def decisions():
    p=W/'reference/chapter11-recheck-overrides.json';return read(p)['records'] if p.exists() else []
def overlay(now):
    for r in decisions():
        a,k=r['asset'],r['id'];e=now['assets'].get(a,{}).get('entries',{})
        if k not in e:continue
        assert e[k] in (r['before'],r['after']),(k,'Unexpected recheck overlay input')
        e[k]=r['after']
def matches(a,k,before,after):return any(r['asset']==a and r['id']==k and before==r['before'] and after==r['after'] for r in decisions())
def record(start,end,note):
    p=read(Q+'progress.json');p['read_template_ranges'].append(dict(start=start,end_exclusive=end,note=note));seen={i for r in p['read_template_ranges'] for i in range(r['start'],r['end_exclusive'])};p['read_templates']=len(seen);p['remaining_templates']=1658-len(seen);write(Q+'progress.json',p)
def audit():
    from prepare_chapter9 import txtres
    b=read(Q+'baseline.json');snap=Path(b['snapshot']);ctx=read('qa/active-working-set.json');now=read(ctx['combined_source']);old=read(snap/b['active']['combined_source']);ds=decisions();ix={(r['asset'],r['id']):r for r in ds};extra=read('reference/chapter11-recheck-source.json');sc=read(Q+'enemy-intel-scope.json')
    for p,h in b['hashes'].items():assert digest(snap/p)==h,p
    assert fingerprint()==b['protected']
    assert digest(W/'reference/chapter11-recheck-source.json')==sc['source_sha256']
    assert extra[:46]==read(Q+'inventory-revisions/initial46.json')
    assert len(ix)==len(ds)==49 and len(extra)==56
    primary={(r['asset'],r['id']) for r in read('reference/chapter11-source.json')}
    from chapter11_recheck_fixes import UI
    from pronoun_context import matches as pronoun_matches,decisions as pronoun_decisions
    assert set(ix)<=primary|{('End/Content/Text/JP/8700-NIBLE_TxtRes.uasset',k) for k in UI}
    for a,p in old['assets'].items():
        assert p['actors']==now['assets'][a]['actors'],(a,'ACTOR changed')
        for k,t in p['entries'].items():
            r=ix.get((a,k));expected=r['after'] if r else t;actual=now['assets'][a]['entries'][k]
            assert actual==expected or pronoun_matches(a,k,expected,actual),(k,'Unreviewed change')
            if r:assert r['before']==t
    additions={(a,k) for a,p in now['assets'].items() for k in p['entries'] if k not in old['assets'][a]['entries']}
    assert additions=={(r['asset'],r['id']) for r in extra}
    jp=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset'];asset='End/Content/Text/JP/Resident_TxtRes.uasset';suffixes=sc['suffixes']+sc['explicit_suffixes'];checked=[]
    for k,v in jp.items():
        if not v['Text'] or not k.startswith(('$menu_EnemyBookText_','$menu_EnemyBookTipsText_')) or not any(k.endswith('_'+s) for s in suffixes):continue
        assert k in now['assets'][asset]['entries'];t=now['assets'][asset]['entries'][k];assert not re.search('[\u3040-\u30ff\u3400-\u9fff]',t),(k,t);checked.append(k)
    assert len(checked)==56
    nibel='End/Content/Text/JP/8700-NIBLE_TxtRes.uasset';c=read('reference/rebirth-jp-corpus.json')['8700-NIBLE_TxtRes.uasset'];us=txtres.parse(str(W/'source'/nibel.replace('/JP/','/US/')));cross=[]
    for name,data in read('reference/rebirth-jp-corpus.json').items():
        a='End/Content/Text/JP/'+name
        for k,v in data.items():
            if v['Text'] and k.startswith('$C31'):
                assert k in now['assets'][a]['entries'];cross.append(dict(asset=a,id=k))
    groups=read('qa/chapter11/choice-groups.json')['groups'];choices=[]
    for root,keys in groups.items():
        context=[dict(id=k,jp=v['Text'],us=us.get(k,{}).get('Text',''),thai=now['assets'][nibel]['entries'].get(k,'')) for k,v in c.items() if k.startswith(root+'_') and v['Text']]
        assert all(r['thai'] for r in context)
        choices.append(dict(prefix=root,buttons_and_question=keys,context=context,decision='Question, every button and neighboring voiced responses read against JP; US contextual reference only. Runtime branch triggers not independently played.'))
    dup=defaultdict(list)
    for r in read('reference/chapter11-source.json'):dup[r['template']].append(dict(id=r['id'],jp=r['Japanese']['Text'],us=r['English'].get('Text',''),thai=now['assets'][r['asset']]['entries'][r['id']]))
    write(Q+'duplicate-context-review.json',dict(source_sha256=digest(W/ctx['combined_source']),groups={str(k):v for k,v in dup.items() if len(v)>1},reviewed_same_JP_and_actor_separately_by_ID=True))
    write(Q+'choice-semantic-review.json',dict(source_sha256=digest(W/ctx['combined_source']),groups=choices,group_count=len(choices),records=sum(len(v) for v in groups.values()),in_game_tested=False))
    report=dict(source_sha256=digest(W/ctx['combined_source']),previous42394_preserved_except49_reviewed_revisions=True,corrected_records=len(ds),added_UI_records=len(extra),total_combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),whole_enemy_description_and_tips_records=checked,cross_asset_C31_records=len(cross),reviewed_corrections=ds,missing=[],new_dialogue_after_Ch11=False,installed=False,in_game_tested=False)
    if pronoun_decisions():report.update(previous42394_preserved_except49_reviewed_revisions=False,previous42394_preserved_except49_revisions_and_reviewed_pronoun_changes=True,pronoun_changes=len(pronoun_decisions()))
    write(Q+'review.json',report);print('Ch11 recheck:49 revisions,56 new Enemy Intel UI records; all659 C31 IDs covered')
def main():
    if sys.argv[1]=='--prepare':prepare()
    elif sys.argv[1]=='--prepare-extra':prepare_extra()
    elif sys.argv[1]=='--record':record(int(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
    elif sys.argv[1]=='--audit':audit()
if __name__=='__main__':main()
