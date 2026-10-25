"""Render complete revised question/answer groups with staged game glyphs."""
import re,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from prepare_chapter9 import W,read,write,txtres
from context_full_read import Q,decisions,digest
from preview_ch12_recheck import renderer

def main():
    ctx=read('qa/active-working-set.json');stage=W/ctx['stage'];rs=decisions();changed={(r['asset'],r['id']) for r in rs};groups=read('qa/context-recheck/scene-choice-groups.json');contexts=read('qa/context-recheck/all-record-contexts.json');by={(r['asset'],r['id']):r for r in contexts}
    panels=[];covered=set()
    for g in groups:
        keys=[r['id'] for r in g['records']]
        if any((g['asset'],k) in changed for k in keys) or any(r['asset']==g['asset'] and '_'.join(r['id'].split('_')[:3])=='_'.join(keys[0].split('_')[:3]) for r in rs):
            panels.append((f"Choice {g['index']}",g['asset'],keys));covered.update((g['asset'],k) for k in keys)
    # These Common menu confirmations do not use the scene *_sel_* naming
    # convention. Keep each reviewed question and both buttons together.
    resident='End/Content/Text/JP/Resident_TxtRes.uasset'
    menu_groups=[
        ('Fort Condor start',['$menu_condor_start_confirm','$menu_condor_0002_0000','$menu_condor_0002_0001']),
        ('Fort Condor quit',['$menu_condor_cancel_confirm','$menu_condor_0002_0000','$menu_condor_0002_0001']),
        ('Fort Condor retry',['$menu_condor_pause_retry_confirm','$menu_condor_0002_0000','$menu_condor_0002_0001']),
        ('Fort Condor forfeit',['$menu_condor_pause_retire_confirm','$menu_condor_pause_retire_confirm_yes','$menu_condor_pause_retire_confirm_no']),
    ]
    for code in ['0002','0007','0008','0009','0010']:
        menu_groups.append(('Gameover confirmation '+code,[f'$menu_gameover_{code}_{i:04d}' for i in range(3)]))
    for code in ['0009','0016']:
        menu_groups.append(('Main menu confirmation '+code,[f'$menu_mainmenu_{code}_{i:04d}' for i in range(3)]))
    for suffix in ['','_1']:
        menu_groups.append(('Weapon inheritance'+suffix,['$menu_mainmenu_WeaponEquip_WindowMessage'+suffix,'$menu_mainmenu_WeaponEquip_Yes','$menu_mainmenu_WeaponEquip_No']))
    menu_groups += [
        ('Main menu start battle',['$menu_mainmenu_cancel_dialog','$menu_mainmenu_cancel_dialog_yes','$menu_mainmenu_cancel_dialog_no']),
        ('Disable weapon auto-upgrade',['$menu_mainmenu_weaponstatus_auto_release','$menu_mainmenu_weaponstatus_auto_release_yes','$menu_mainmenu_weaponstatus_auto_release_no']),
        ('Map fast travel',['$menu_map_areamap_confirm_fast_travel','$menu_map_areamap_confirm_fast_travel_yes','$menu_map_areamap_confirm_fast_travel_no']),
        ('Options reset all',['$menu_options_0007_0000','$menu_options_0007_0001','$menu_options_0007_0002']),
        ('Input settings reset',['$menu_options_key_config_reset_confirm','$menu_options_key_config_reset_yes','$menu_options_key_config_reset_no']),
    ]
    # Frozen queue indices identify the separately read non-scene menus. Include
    # every reviewed use of shared buttons, rather than just their nearest row.
    queue=read(Q+'queue.json')
    indexed_groups=[
        ('Pause pre-battle checkpoint',[30041,30042,30043]),
        ('Pause return to title',[30044,30045,30046]),
        ('Pause restart minigame',[30051,30052,30053]),
        ('Pause return to course selection',[30054,30055,30056]),
        ('Save selected slot',[30120,30121,30122]),
        ('Load selected slot',[30123,30124,30125]),
        ('Title continue',[30230,30231,30232]),
        ('Title import demo save',[30239,30241,30242]),
        ('Title quit application',[30249,30250,30251]),
        ('Box forfeit',[30491,30492,30493]),
        ('Card forfeit',[30544,30547,30548]),
        ('Card forfeit without rematch',[30545,30547,30548]),
        ('Card start match',[30598,30599,30600]),
        ('Card tutorial',[30602,30603,30604]),
        ('Chocobo capture forfeit',[30638,30639,30640]),
        ('Minigame forfeit',[30785,30786,30787]),
        ('Moogle House enter',[30806,30808,30809]),
        ('Moogle House enter with difficulty note',[30807,30808,30809]),
        ('Moogle Mischief lower difficulty',[30841,30842,30843]),
    ]
    for i in range(30150,30164):
        indexed_groups.append(('Shared shop confirmation '+str(i),[i,30164,30165]))
    for i in [30499,30509,30559,30572,30574,30595]:
        indexed_groups.append(('Shared card confirmation '+str(i),[i,30500,30498]))
    indexed_groups.append(('Card quest match confirmation',[30499,30501,30498]))
    for i in [30736,30737,30740,30749]:
        indexed_groups.append(('Shared race confirmation '+str(i),[i,30741,30734]))
    for label,indices in indexed_groups:
        assert all(queue[i]['index']==i and queue[i]['asset']==resident for i in indices)
        menu_groups.append((label,[queue[i]['id'] for i in indices]))
    for label,keys in menu_groups:
        if any((resident,k) in changed for k in keys):
            assert all((resident,k) in by for k in keys),(label,keys)
            panels.append((label,resident,keys));covered.update((resident,k) for k in keys)
    # Semantic changes outside choice blocks: include the immediately adjacent
    # translated lines; source-order contexts are supplementary, not branch flow.
    for r in rs:
        key=r['asset'],r['id']
        if key in covered:continue
        original=by[key];keys=[x['id'] for x in original['before'][-1:]]+[r['id']]+[x['id'] for x in original['after'][:1]]
        panels.append((r['id'],r['asset'],keys));covered.add(key)
    data={a:txtres.parse(str(stage/a)) for label,a,keys in panels};fonts={size:renderer(stage,f'U_Com_JP_SystemFont{size}.uasset') for size in ['Large','Normal']};legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17);samples=[]
    pages=(len(panels)+7)//8
    for page in range(pages):
        pairs=[]
        for label,a,keys in panels[page*8:(page+1)*8]:
            texts=list(dict.fromkeys(re.sub('<[^>]+>','',data[a][k]['Text']).replace('\r','') for k in keys));text='\n'.join(texts);cells=[]
            for size,(gs,mask) in fonts.items():
                x=15;y=45;ops=[];bottom=100
                for ch in text:
                    if ch=='\n':x=15;y+=52;continue
                    g=gs[ord(ch)]
                    if x+g[8]>945:x=15;y+=52
                    if g[4] and g[5]:
                        m=mask(g);px=x+g[6];py=y+g[7];assert px>=0 and py>=30
                        ops.append((px,py,m));bottom=max(bottom,py+m.height+18)
                    x+=g[8]
                cell=Image.new('RGB',(960,bottom),'#17283d');ImageDraw.Draw(cell).text((10,8),size+' | '+label,font=legend,fill='#9fd8e8')
                for px,py,m in ops:assert px+m.width<=960;cell.paste((242,247,255),(px,py),m)
                cells.append(cell);samples.append(dict(label=label,asset=a,ids=keys,font=size,clipped=False))
            pairs.append(cells)
        heights=[max(c.height for c in pair) for pair in pairs];canvas=Image.new('RGB',(1960,60+sum(h+12 for h in heights)),'#091522');ImageDraw.Draw(canvas).text((15,15),f'Full-read revision {page+1}/{pages} | Staged glyphs | Repeated prompt variants deduplicated | Illustrative, not in-game',font=legend,fill='#bfd7ed');y=55
        for pair,h in zip(pairs,heights):
            for col,cell in enumerate(pair):canvas.paste(cell,(10+980*col,y))
            y+=h+12
        canvas.save(W/Q/f'proof-{page+1}.png')
    write(Q+'proof.json',dict(source_sha256=digest(W/ctx['combined_source']),pages=pages,panels=len(panels),samples=samples,actual_staged_glyphs=True,fonts=['Large','Normal'],all_revised_choice_groups_complete=True,repeated_identical_prompt_text_deduplicated=True,source_order_neighbors_are_not_branch_flow=True,in_game_tested=False))
    print('Rendered',pages,'pages,',len(panels),'complete choice/dialogue/glossary panels')
if __name__=='__main__':main()
