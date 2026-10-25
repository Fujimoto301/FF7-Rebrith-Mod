"""Freeze adjacent Chapter7 UI and previous Costa deferrals unlocked now."""
import re
from collections import defaultdict
from prepare_chapter7 import W,read,write,txtres
R='End/Content/Text/JP/Resident_TxtRes.uasset'
def family(k):
    if k.startswith(('$menu_WorldReport_CORLA_','$AreaReport_CORLA_')):return 'Corel_report_UI'
    if k.startswith(('$minigame_SitUp_','$level_minigame_situp_')):return 'situp_activity_choices'
    if k.startswith(('$level_CORLM_','$level_CORLV_','$level_CORLA_qst15_')):return 'Corel_field_prompts'
    if re.match(r'\$CORL[AMV]_(?:ITEM|MAGIC|WEAPON|MOOGLESHOP)_',k):return 'Corel_shop_names'
    if re.match(r'\$key_qst1[457]_',k):return 'Corel_quest_items'
    return None
def main():
    assert not (W/'reference/chapter7-supplement-source.json').exists()
    c=read('reference/rebirth-jp-corpus.json');base=read('translations/working-ch1-6-recheck-th.json')
    source=[];templates=[];indices={};reuse={};byjp=defaultdict(set)
    for a,p in base['assets'].items():
        for k,t in p['entries'].items():
            v=c[a.split('/')[-1]][k]
            if a==R and not v.get('MetaData',{}).get('ACTOR'):byjp[v['Text']].add(t)
    old=read('reference/chapter6-deferred.json')
    unlocked={r['id'] for i,r in enumerate(old) if 2<=i<=16 or 47<=i<=91}
    for a,d in c.items():
        wanted=[]
        for k,v in d.items():
            f=family(k) if a=='Resident_TxtRes.uasset' else None
            speech=k in unlocked or a=='Resident_TxtRes.uasset' and k.startswith(('$PHOTO_QST_03_0400_','$PHOTO_QST_00_0400_'))
            if v['Text'] and (f or speech):wanted.append((k,v,'speech' if speech else f))
        if not wanted:continue
        rel='End/Content/Text/JP/'+a;us=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
        for k,v,f in wanted:
            mode='existing' if k in base['assets'].get(rel,{}).get('entries',{}) else 'translate'
            r=dict(asset=rel,id=k,Japanese=v,English=us.get(k,{}),family=f,mode=mode)
            if mode=='translate':
                t=None
                if f!='speech':
                    if f=='Corel_shop_names' or f=='Corel_quest_items' and not k.endswith('_help') or f=='Corel_report_UI' and re.search('_Title(?:_NA)?$',k):
                        t=us[k]['Text'];r['mode']='official_English_name'
                    elif not re.search('[\u3040-\u30ff\u3400-\u9fff]',v['Text']):t=v['Text'];r['mode']='original_symbol_or_English'
                    elif len(byjp[v['Text']])==1:t=next(iter(byjp[v['Text']]));r['mode']='exact_UI_reuse'
                if t is not None:reuse[k]=t
                else:
                    key=(f=='speech',v['Text'])
                    if key not in indices:
                        indices[key]=len(templates);templates.append(dict(index=len(templates),jp=v['Text'],family=f,examples=[],us=us.get(k,{}).get('Text','')))
                    r['template']=indices[key];templates[r['template']]['examples'].append(k)
            source.append(r)
    write('reference/chapter7-supplement-source.json',source);write('reference/chapter7-supplement-templates.json',templates)
    write('translations/chapter7-supplement-automatic.json',reuse)
    print(len(source),'supplement records;',len(templates),'manual templates;',len(reuse),'automatic entries')
if __name__=='__main__':main()
