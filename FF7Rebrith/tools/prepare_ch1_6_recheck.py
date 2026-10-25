"""Freeze the current release and audit all completed chapters plus shared UI."""
import hashlib,re,shutil,uuid
from collections import Counter,defaultdict
from pathlib import Path
from assemble_chapter6 import W,read,write,txtres
from assemble_ui_completion import fingerprint

ROOT='qa/ch1-6-recheck';R='End/Content/Text/JP/Resident_TxtRes.uasset'
def ui_family(k):
    if k.startswith('$menu_condor_'):return 'Fort_Condor'
    if k.startswith('$minigame_soldierformation_'):return 'Junon_parade'
    if k.lower().startswith(('$minigame_dolphinjump','$minigame_frogflap')):return 'Dolphin_and_frog'
    if k.startswith('$minigame_common_') or re.match(r'\$minigame_(reward\d|scorerank\d)',k):return 'common_activity_dialogs'
    if k.startswith('$minigame_CrystalAnalysis_'):return 'summon_crystal_analysis'
    if k.startswith(('$minigame_chocobocraft_','$minigame_subquest_chocobocraft_','$minigame_subquest_chocoboccraft_')):return 'chocobo_excavation'
    if k.startswith(('$menu_WorldReport_GRASA_','$menu_WorldReport_JUNOA_','$menu_WorldReport_Condition_','$menu_WorldReport_Moogle_','$AreaReport_GRASA_','$AreaReport_JUNOA_')):return 'Grasslands_Junon_intel_UI'
    if k.startswith('$TravelCameraman_'):return 'photographer_UI'
    if re.match(r'\$(?:KALMT|GRASA|JNONT|JNONV|JUNOA|FERRY|COSTT)_(?:ITEM|MAGIC|WEAPON|CLOSET|MOOGLESHOP|MiniGame)_',k) or k in {'$CHADLEY_SHOP_JUNON','$CHADLEY_SHOP_GRASS'}:return 'visited_town_shop_and_activity_labels'
    if k.startswith('$it_key_minigamecard') and k.endswith('_help'):return 'QB_card_and_pack_descriptions'
    return None

def dialogue_decision(k):
    if k.startswith('$PHOTO_QST_00_'):
        # 1st/2nd regional report ranks available in Grasslands and Junon.
        return ('include',2) if int(k.split('_')[3])<=300 else ('later_world_photo_rank',7)
    if k.startswith('$PHOTO_QST_01_'):return ('include',2)
    if k.startswith('$PHOTO_QST_02_'):return ('include',4)
    if k.startswith('$PHOTO_QST_03_'):
        stage=int(k.split('_')[3]);line=int(k.split('_')[4])
        if stage==100 and line>=500:return ('renovated_Johnny_inn',7)
        if stage==400:return ('Corel_coast_photo_report_after_leaving_Costa',7)
        return ('include',6)
    if k.startswith('$PIANO_QST_01_'):
        stage=int(k.split('_')[3]);line=int(k.split('_')[4])
        if stage==300 or stage==200 and line>=1000:return ('complete_all_music_scores_later',11)
        return ('include',4)
    return None

def main():
    assert not (W/(ROOT+'/baseline.json')).exists(),'Preserve existing revision baseline'
    ctx=read('qa/active-working-set.json');base=read(ctx['combined_source']);root=ROOT+'/revisions/'+uuid.uuid4().hex
    for rel in [ctx['combined_source'],ctx['cluster_map'],ctx['manifest'],'qa/active-working-set.json','qa/final-parts/latest.json']:
        p=W/root/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,p)
    shutil.copytree(W/ctx['stage'],W/root/'stage')
    write(ROOT+'/baseline.json',dict(snapshot=root,active=ctx,protected=fingerprint(),
      source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source').rglob('*.uasset')}))
    j=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset'];u=txtres.parse(str(W/'source'/R.replace('/JP/','/US/')))
    by_jp=defaultdict(set)
    for k,t in base['assets'][R]['entries'].items():
        if not j[k].get('MetaData',{}).get('ACTOR'):by_jp[j[k]['Text']].add(t)
    rows=[];templates=[];indices={};automatic={};speech=[];deferred=[]
    for k,v in j.items():
        cat=ui_family(k)
        if cat and v['Text']:
            mode='existing' if k in base['assets'][R]['entries'] else 'unchanged' if not re.search('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]',v['Text']) else 'translate'
            r=dict(id=k,asset=R,family=cat,Japanese=v,English=u.get(k,{}),mode=mode)
            if mode=='translate':
                if cat=='visited_town_shop_and_activity_labels' or cat=='photographer_UI' and re.fullmatch(r'\$TravelCameraman_Window_(?:CORLA|COSMA|COSTA|GONGA|GRASA|JUNOA|NIBLA|HideAreaName)',k) or cat=='Junon_parade' and re.match(r'.*_(?:form|formname|unit)_\d+$',k):
                    r['mode']='English_name';automatic[k]=u[k]['Text']
                elif cat=='Grasslands_Junon_intel_UI' and re.search('_Title(?:_NA)?$',k):
                    r['mode']='report_title';automatic[k]=u[k]['Text']
                elif cat=='QB_card_and_pack_descriptions':r['mode']='card_description'
                elif len(by_jp[v['Text']])==1:r['mode']='exact_UI_reuse';automatic[k]=next(iter(by_jp[v['Text']]))
                else:
                    if v['Text'] not in indices:
                        indices[v['Text']]=len(templates);templates.append(dict(index=len(templates),jp=v['Text'],examples=[],family=cat))
                    r['template']=indices[v['Text']];templates[r['template']]['examples'].append(k)
            rows.append(r)
        d=dialogue_decision(k)
        if d and v['Text']:
            r=dict(id=k,asset=R,Text=v['Text'],MetaData=v.get('MetaData',{}),English=u.get(k,{}),chapter=d[1])
            if d[0]=='include':speech.append(r)
            else:r['reason']=d[0];deferred.append(r)
    write('reference/ch1-6-recheck-ui-source.json',rows);write('reference/ch1-6-recheck-ui-templates.json',templates)
    write('reference/ch1-6-recheck-speech-source.json',speech);write('reference/ch1-6-recheck-deferred.json',deferred)
    write('translations/ch1-6-recheck-ui-automatic.json',automatic)
    stage='staging/ThaiJP_Ch1_6_Recheck_Working';shutil.copytree(W/ctx['stage'],W/stage)
    shutil.copy2(W/ctx['cluster_map'],W/'reference/ch1-6-recheck-cluster-map.json')
    shutil.copy2(W/'qa/ch12-recheck/build-verification.json',W/ROOT/'build-verification.json')
    write('reference/ch1-6-recheck-build.json',dict(stage=stage,qa=ROOT,source='translations/working-ch1-6-recheck-th.json',
      cluster_map='reference/ch1-6-recheck-cluster-map.json',cluster_seed=ctx['cluster_map'],punctuation_policy='reference/dialogue-punctuation-policy.json'))
    print('UI',len(rows),Counter(r['mode'] for r in rows),'manual templates',len(templates),'new speech',len(speech),'deferred',len(deferred))
    for t in templates:print(t['index'],t['family'],t['examples'][0],t['jp'].replace('\r','').replace('\n',' | '))

if __name__=='__main__':main()
