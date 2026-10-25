"""Freeze Ch9 first-visit Gongaga, side quests, protorelic and shared NPCs."""
import re,hashlib,uuid,shutil
from collections import defaultdict,Counter
from prepare_chapter8 import W,read,write,txtres
from assemble_ui_completion import fingerprint

def primary(a,k):
    return a=='8500-GONGE_TxtRes.uasset' or a=='4000-MIDGR_TxtRes.uasset' and k.startswith('$C2710_')

def shared(k):
    if k.startswith(('$WORLD_CDV_02_0500_','$WORLD_MGV_01_0500_')):return True
    if k in ('$WORLD_CDV_01_0100_20700_00_chd','$WORLD_CDV_01_0100_26300_00_chd'):return True
    if k.startswith(('$CARDG_QST_14_','$PHOTO_QST_05_')):return True
    if k.startswith('$WORLD_CDV_01_0100_'):return 13700<=int(k.split('_')[4])<=14600
    if k.startswith('$WORLD_CDV_01_0500_'):return int(k.split('_')[4])==2400
    return False

def defer(k):
    if k in ('$C2710_MAIN_3500_0600_00_zaf','$C2710_MAIN_3600_0100_00_zam','$C2710_MAIN_3600_0600_00_zam','$C2710_MAIN_3600_0700_00_zam'):return 'Later war reaction from Zack parents'
    if k.startswith('$WORLD_CDV_02_0500_') and int(k.split('_')[4]) in (400,500,600,1100,1200,1300,1400,1500):return 'Later Trouble in Paradise odd job legendary-bait reactions; preserve for regional return'
    if k.startswith('$GONGE_QST_05_'):return 'Later Woodland Vigil odd job / return-state Cissnei patrol'
    if k.startswith('$GONGE_QST_06_'):return 'Later Escape from Endless Writers Block photo writer return-state quest'
    if k.startswith('$CARDG_QST_07_'):return 'Late Queen Blood finale with Vincent and Regina, outside Ch9'
    if k.startswith('$GONGV_NPC_10_0100_') and 8000<=int(k.split('_')[4])<=8200:return 'Later impending-war village reaction; review before later chapter inclusion'
    return None

def ui(k):
    if k.startswith('$CHADLEY_SHOP_'):return 'Chadley_research_shop_names'
    if k.startswith('$key_GONGM_'):return 'Gongaga_shared_travel_items'
    if k.startswith('$key_qst22_') or k.startswith(('$menu_BattleMission_Quest1000_','$menu_BattleMission_Quest1100_')):return 'Gongaga_quest_objective_UI'
    if k in ('$name_izo','$name_sot','$name_csn') or k.startswith('$npc_Gongaga_'):return 'Gongaga_shop_UI'
    if k.startswith(('$AreaReport_GONGA_','$minigame_ChickenLure_','$minigame_MushroomPicking_','$key_qst24_','$key_qst25_')):return 'Gongaga_adjoining_activity_UI'
    if re.match(r'\$GONG[AMPV]_(?:ITEM|MAGIC|MOOGLESHOP|CLOSET|WEAPON|CARD)_',k):return 'Gongaga_shop_UI'
    if k in ('$4000_zack_Raise','$Release_COL30_SUMMON_Kjata','$menu_EnemyBookAreaText_map2400_MainHabitat'):return 'Gongaga_adjoining_UI'
    if k.startswith(('$level_GONG','$level2400_')):return 'Gongaga_field_and_choices'
    if k.startswith(('$GONGV_','$GONGE_')) and any(w in k for w in ['SHOP','ITEM','MAGIC','WEAPON','CARD']):return 'Gongaga_shop_UI'
    if k.startswith('$menu_WorldReport_GONGA_') or k=='$menu_chadleyshop_help_materia_development_GONGA':return 'Gongaga_report_UI'
    if re.match(r'\$(?:menu_Colosseum_Course(?:Title|Flavor)_|Release_COL).*GONGA',k):return 'Gongaga_simulator_UI'
    if k.endswith('_GONGA') or '_GONGA_' in k:
        if k.startswith(('$level_sys_','$menu_Colosseum_cond_')):return 'Gongaga_adjoining_UI'
    return None

def main():
    assert not (W/'reference/chapter9-source.json').exists(),'Frozen indices already exist'
    c=read('reference/rebirth-jp-corpus.json');base=read('translations/working-through-chapter8-th.json');rows=[];ts=[];ix={};reuse={};byjp=defaultdict(set)
    for a,p in base['assets'].items():
        for k,t in p['entries'].items():
            if not re.search(r'ครับ|ค่ะ|คะ|ผม|ดิฉัน|[A-Za-z]{2,}',re.sub('<[^>]+>','',t)):byjp[c[__import__('pathlib').Path(a).name][k]['Text']].add(t)
    for a,d in c.items():
        selected=[(k,v) for k,v in d.items() if v['Text'] and (primary(a,k) or a=='Resident_TxtRes.uasset' and (shared(k) or ui(k)))]
        if not selected:continue
        rel='End/Content/Text/JP/'+a;us=txtres.parse(str(W/'source'/rel.replace('/JP/','/US/')))
        for k,v in selected:
            if k in base['assets'].get(rel,{}).get('entries',{}):continue
            group='UI' if a=='Resident_TxtRes.uasset' and ui(k) else 'system' if k.endswith('_sys') else 'speech'
            key=(group,v['Text'])
            if key not in ix:
                i=len(ts);ix[key]=i;ts.append(dict(index=i,jp=v['Text'],us=us.get(k,{}).get('Text',''),group=group,examples=[],actors=[]))
                if len(byjp[v['Text']])==1:reuse[str(i)]=next(iter(byjp[v['Text']]))
                if group=='UI' and (k.startswith('$menu_Colosseum_CourseTitle_') or ui(k)=='Gongaga_shop_UI'):reuse[str(i)]=us[k]['Text']
            i=ix[key];ts[i]['examples'].append(k);ac=us.get(k,{}).get('MetaData',{}).get('ACTOR','')
            if ac not in ts[i]['actors']:ts[i]['actors'].append(ac)
            rows.append(dict(asset=rel,id=k,Japanese=v,English=us.get(k,{}),template=i,group=group,reason=defer(k)))
    write('reference/chapter9-source.json',rows);write('reference/chapter9-templates.json',ts)
    write('reference/chapter9-deferred.json',[r for r in rows if r['reason']]);write('translations/chapter9/reused-lines.json',reuse)
    backup=W/'qa/chapter9/revisions'/uuid.uuid4().hex
    for rel in ['translations/working-through-chapter8-th.json','reference/through-chapter8-cluster-map.json','qa/chapter8/working-assets.json','qa/final-parts/latest.json','qa/active-working-set.json']:
        dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/rel,dest)
    write('qa/chapter9/baseline.json',dict(backup=str(backup),base_source=str(backup/'translations/working-through-chapter8-th.json'),previous_assets=str(backup/'qa/chapter8/working-assets.json'),protected=fingerprint(),source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source/End/Content/Text').rglob('*.uasset')}))
    write('reference/chapter9-scope.json',dict(source_sha256=hashlib.sha256((W/'reference/chapter9-source.json').read_bytes()).hexdigest(),records=len(rows),templates=len(ts),selected=sum(not r['reason'] for r in rows),deferred=sum(bool(r['reason']) for r in rows),groups=dict(Counter(r['group'] for r in rows if not r['reason'])),base='translations/working-through-chapter8-th.json'))
    print(read('reference/chapter9-scope.json'));print('Reuses',len(reuse),'remaining',len({r['template'] for r in rows if not r['reason']}-set(map(int,reuse))))

if __name__=='__main__':main()
