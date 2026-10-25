"""Compare the Ch9 recheck to its frozen release and independently search neighbours."""
import hashlib,re
from pathlib import Path
from prepare_chapter9 import W,read,write


def main():
    meta=read('qa/chapter9/recheck/current.json');snap=Path(meta['snapshot'])
    old=read(snap/'translations/working-through-chapter9-th.json')
    now=read('translations/working-through-chapter9-th.json');patch=read('translations/chapter9-th.json')
    source=read('reference/rebirth-jp-corpus.json');rows=read('reference/chapter9-source.json')
    corrections=[];added=[]
    for asset,p in now['assets'].items():
        before=old['assets'].get(asset,dict(entries={},actors={}))
        assert before['entries'].keys()<=p['entries'].keys()
        assert all(p['actors'][k]==v for k,v in before['actors'].items())
        for key,text in p['entries'].items():
            if key not in before['entries']:added.append(dict(asset=asset,id=key,thai=text))
            elif text!=before['entries'][key]:
                assert key in patch['assets'][asset]['entries']
                corrections.append(dict(asset=asset,id=key,before=before['entries'][key],after=text))
    assert len(added)==8
    bad=r'ทีฟา|มาโค|เจโนว่า|โชโคโบะ|แชดลีย์|เร้ด(?!เชลลี่)'
    assert all(not re.search(bad,t) for p in patch['assets'].values() for t in p['entries'].values())
    outside=[];included=[];empties=0
    for asset,data in source.items():
        for key,value in data.items():
            # Deliberately independent of prepare_chapter9.ui/shared selectors.
            if not (asset=='8500-GONGE_TxtRes.uasset' or re.search(r'GONG|Gong|gong|qst2[2345]|QUEST2[2345]|Chicken|Mushroom|PHOTO_QST_05|CARDG_QST_14',key) or re.search(r'ゴンガガ|シスネ|ソテツ|イゾー|マゴンガ|クックック',value['Text'])):continue
            if not value['Text']:empties+=1;continue
            if key in now['assets'].get('End/Content/Text/JP/'+asset,{}).get('entries',{}):included.append([asset,key]);continue
            if asset=='8500-GONGE_TxtRes.uasset':
                hits=[r for r in rows if r['id']==key and r['reason']];assert len(hits)==1,key
                reason=hits[0]['reason']
            elif key.startswith(('$menu_EnemyBookText_','$menu_EnemyBookTipsText_')):
                reason='Enemy assessment lore/tips separate from translated English enemy-name labels; not scene/choice/activity family'
            elif key.startswith('$WORLD_CDV_03_'):reason='Later Queens Blood finale, Vincent/Regina return state'
            elif key.startswith(('$keyitem_collection_05','$keyitem_collection_063')):
                reason='Later Shinra Manor or multi-region photographer completion reward, not first Gongaga visit'
            elif asset in ('8600-COSME_TxtRes.uasset','8700-NIBLE_TxtRes.uasset'):
                reason='Later Cosmo/Nibel scene explicitly outside Ch9'
            else:raise AssertionError((asset,key,'Unreviewed outside candidate'))
            outside.append(dict(asset=asset,id=key,jp=value['Text'],reason=reason))
    old_assets=read(snap/'qa/chapter9/working-assets.json');current_assets=read('qa/chapter9/working-assets.json')
    changed_assets=[p for p,h in current_assets.items() if old_assets.get(p)!=h]
    assert {Path(p).name for p in changed_assets}=={'8500-GONGE_TxtRes.uasset','Resident_TxtRes.uasset'}
    number_rows=[r for r in read('qa/chapter9/number-review.json') if r['source_numeric_runs']!=r['target_numeric_runs']]
    prior_numbers=read(snap/'qa/chapter9/numeric-review.json')['rows']
    assert {r['id'] for r in number_rows}=={r['id'] for r in prior_numbers}
    assert len(number_rows)==12
    for row in number_rows:
        before=next(r for r in prior_numbers if r['id']==row['id'])
        assert row['source_numeric_runs']==before['source_numeric_runs'] and row['target_numeric_runs']==before['target_numeric_runs']
    report=dict(baseline=meta['snapshot'],source_sha256=hashlib.sha256((W/'translations/working-through-chapter9-th.json').read_bytes()).hexdigest(),
        previous_records=32851,combined_records=sum(len(p['entries']) for p in now['assets'].values()),
        added_records=len(added),corrected_records=len(corrections),all_prior_IDs_and_ACTOR_preserved=True,
        only_chapter9_existing_records_corrected=True,added=added,corrections=corrections,
        independent_corpus_included_records=len(included),included_ids=included,outside_nonempty_records=len(outside),
        empty_records_ignored=empties,outside=outside,changed_assets=changed_assets,
        all_font_assets_unchanged=True,numeric_decisions_unchanged=True,in_game_tested=False,new_full_video_audio_review=False)
    write('qa/chapter9/recheck-review.json',report)
    print('Ch9 recheck:',len(added),'added;',len(corrections),'corrected;',len(included),'independent matches;',len(outside),'reviewed outside; fonts unchanged')


if __name__=='__main__':main()
