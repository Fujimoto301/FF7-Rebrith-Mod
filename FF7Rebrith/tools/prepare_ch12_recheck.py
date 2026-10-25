"""Immutable snapshot and whole-family inventory for the Ch.1–2 screenshot audit."""
import hashlib,re,shutil,uuid
from assemble_chapter6 import W,read,write,txtres
from assemble_ui_completion import fingerprint

ROOT='qa/ch12-recheck';R='End/Content/Text/JP/Resident_TxtRes.uasset'
def family(k):
    if k.startswith('$minigame_cardgame_'):return 'queens_blood_UI'
    if k.startswith('$minigame_chocobocapture_'):return 'chocobo_capture_UI'
    if k.startswith('$minigame_mooglecapture_'):return 'moogle_mischief_UI'
    if k.startswith(('$card_opponent_','$card_questopponent_','$card_MenuLog_','$cardtext_HowtoGet_')):return 'queens_blood_navigation_and_notifications'
    if k.startswith(('$menu_Colosseum_CourseTitle_','$menu_Colosseum_CourseFlavor_')) and '_TutorialBtl_' in k:return 'combat_tutorial_courses'
    if k in {'$GRASA_CARD_000','$Moogle_Shop'}:return 'local_shop_labels'

def english_name(k):
    return k.startswith(('$card_opponent_','$card_questopponent_','$minigame_cardgame_bouterrank_')) and not re.search('condition|rankup',k) or bool(re.fullmatch(r'\$minigame_cardgame_presetdeck\d+_name',k)) or bool(re.fullmatch(r'\$minigame_(?:chocobocapture|mooglecapture)_name_\d+',k)) or k in {'$Moogle_Shop'}

def main():
    assert not (W/(ROOT+'/baseline.json')).exists(),'Keep immutable revision snapshots'
    root=ROOT+'/revisions/'+uuid.uuid4().hex
    old=read('qa/active-working-set.json')
    for rel in ['translations/working-through-chapter6-th.json','reference/through-chapter6-cluster-map.json',
      old['manifest'],'qa/active-working-set.json','qa/final-parts/latest.json']:
        p=W/root/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,p)
    shutil.copytree(W/old['stage'],W/root/'stage')
    write(ROOT+'/baseline.json',dict(snapshot=root,protected=fingerprint(),active=old,
      source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'source').rglob('*.uasset')}))
    oldtext=read('translations/working-through-chapter6-th.json')['assets'][R]['entries']
    j=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset'];u=txtres.parse(str(W/'source'/R.replace('/JP/','/US/')))
    rows=[dict(id=k,asset=R,family=family(k),Japanese=v,English=u.get(k,{}),
      mode='existing' if k in oldtext else 'unchanged' if not re.search('[\u3040-\u30ff\u3400-\u9fff\uff10-\uff19]',v['Text']) else 'english_name' if english_name(k) else 'translate')
      for k,v in j.items() if family(k) and v['Text']]
    write('reference/ch12-recheck-ui-source.json',rows)
    stage='staging/ThaiJP_Ch12_Recheck_Working';qa=ROOT
    shutil.copytree(W/old['stage'],W/stage)
    shutil.copy2(W/'reference/through-chapter6-cluster-map.json',W/'reference/ch12-recheck-cluster-map.json')
    shutil.copy2(W/'qa/chapter6/build-verification.json',W/qa/'build-verification.json')
    write('reference/ch12-recheck-build.json',dict(stage=stage,qa=qa,source='translations/working-ch12-recheck-th.json',
      cluster_map='reference/ch12-recheck-cluster-map.json',cluster_seed='reference/through-chapter6-cluster-map.json',
      punctuation_policy='reference/dialogue-punctuation-policy.json'))
    write('reference/dialogue-punctuation-policy.json',dict(codepoints=[8230],anchor='Original ASCII full stop ink bottom',
      change='Only vertical origin of U+2026; preserve pixels, bearings, advance, original ASCII, icons and Thai alignment',
      reason='User screenshots 2026-10-18 show midline ellipsis; requested baseline dots as in supplied low-dot reference.',
      references=['Screenshot 2026-10-18 113848.png','Screenshot 2026-10-18 114018.png','Screenshot 2026-10-18 161004.png']))
    print('Prepared',len(rows),'UI inventory records; modes:',{m:sum(r['mode']==m for r in rows) for m in ['existing','unchanged','english_name','translate']})
    for r in rows:
        if r['mode']=='translate':print(r['id']+'\n'+r['Japanese']['Text'].replace('\r','')+'\n')

if __name__=='__main__':main()
