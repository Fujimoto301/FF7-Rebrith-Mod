"""Append screenshot-related UI families and the reviewed English HUD exception."""
import json,re,shutil,uuid
from pathlib import Path
from create_ui_completion_scope import W,R,read,write,normalized
from assemble_ui_completion import fingerprint
import txtres

def main():
    marker=W/'qa/ui-completion/piano-notification-scope.json'
    if marker.exists():raise RuntimeError('Scope already appended; retain stable indices')
    run=W/'qa/ui-completion/revisions'/uuid.uuid4().hex;run.mkdir(parents=True)
    for p in ('translations/working-ui-completion-th.json','reference/ui-completion-source.json',
              'reference/ui-completion-templates.json','reference/ui-completion-scope.json',
              'qa/ui-completion/working-assets.json','qa/final-parts/latest.json'):
        target=run/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/p,target)
    protected=run/'protected-files-before.json';write(str(protected),fingerprint())
    write('qa/ui-completion/active-revision.json',dict(protected_manifest=str(protected),
        previous_combined_source=str(run/'translations/working-ui-completion-th.json'),
        reason='User gameplay screenshots: command help, pickup/battle notifications, piano; HUD action labels English; enemy names still deferred.'))
    rows=read('reference/ui-completion-source.json');ts=read('reference/ui-completion-templates.json');scope=read('reference/ui-completion-scope.json')
    j=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset'];u=txtres.parse(str(W/'source/End/Content/Text/US/Resident_TxtRes.uasset'))
    base=read('translations/working-inventory-th.json')['assets'][R]['entries']
    seen={r['id'] for r in rows};bytext={t['jp']:t['index'] for t in ts};added=[]
    prefixes=('$Piano_','$minigame_piano_','$menu_commandmenu_','$sys_')
    # Musical note/chord symbols and piece titles use their official US notation.
    musical=re.compile(r'^\$minigame_piano_(?:[A-G](?:2)?(?:_(?:flat|sharp))?|score[1-8])$')
    for k,v in j.items():
        t=v['Text']
        if not k.startswith(prefixes) or k in seen or k in base or not t:continue
        assert not v.get('MetaData',{}).get('ACTOR'),k
        c='piano_ui' if k.startswith(('$Piano_','$minigame_piano_')) else 'command_menu_help' if k.startswith('$menu_commandmenu_') else 'system_notifications'
        en=u.get(k,{}).get('Text','');mode='manual'
        if musical.fullmatch(k):mode='english'
        elif not re.search(r'[\u3040-\u30ff\u3400-\u9fff]',t):mode='unchanged'
        row=dict(index=len(rows),id=k,asset=R,category=c,jp=t,en=en,mode=mode)
        if mode in ('english','unchanged'):
            scope['automatic'][k]=en if mode=='english' else t
            assert scope['automatic'][k].strip(),k
        else:
            nt,ns=normalized(t)
            if nt not in bytext:
                bytext[nt]=len(ts);ts.append(dict(index=len(ts),jp=nt,en=en,category=c,ids=[]))
            n=bytext[nt];ts[n]['ids'].append(k);row.update(template=n,numbers=ns)
        rows.append(row);seen.add(k);scope['selected_ids'].append(k);added.append(k)
    k='$level_sys_show_parkour_input';r=next(r for r in rows if r['id']==k)
    r['mode']='english';scope['automatic'][k]=u[k]['Text'];assert u[k]['Text']=='Terrain Action'
    scope['english_hud_actions']={k:u[k]['Text']}
    write('reference/ui-completion-source.json',rows);write('reference/ui-completion-templates.json',ts)
    write('reference/ui-completion-scope.json',scope)
    write('qa/ui-completion/piano-notification-scope.json',dict(prefixes=prefixes,added_ids=added,
        english_hud_actions=scope['english_hud_actions'],musical_notation='Official US note letters and piece names; existing ASCII chord symbols preserved',
        enemy_names_deferred=True,templates_total=len(ts),revision_backup=str(run)))
    print('Appended',len(added),'UI records; templates total',len(ts))

if __name__=='__main__':main()
