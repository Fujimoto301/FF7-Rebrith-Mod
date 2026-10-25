"""Adaptive proof layout from staged fonts; wrapping is illustrative, not game UI."""
import re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import verify_chapter1 as v
from assemble_chapter6 import W,read,write
from chapter6_activity_ui import ROOT,ASSET

def main():
    stage=W/'staging/ThaiJP_ThroughChapter6_Working'
    resident=v.txtres.parse(str(stage/ASSET));common=Path('End/Content/Menu/Billboard/Common')
    samples=['$CardChallenge_02_Detail','$CardChallenge_03_Detail_AfterAmor',
      '$keyitem_CostaAmorNoCard77_help','$keyitem_CostaClothes_photo_help',
      '$minigame_ShootingGame_HitRateNotificationUI_Excellent',
      '$minigame_ShootingGame_OperationGuide04',
      '$minigame_runwild_announce_teamD_wildstart',
      '$minigame_runwild_target_explain','$wheelie_log_Minigame_3rd',
      '$wheelie_hud_Minigame_CountUp_Blue','$card_challenge_gold_condition',
      '$CardChallenge_03_Condition_AfterAmor']
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
    report=[]
    for page in range(3):
        ids=samples[page*4:(page+1)*4];columns=[]
        for size in ('Large','Normal'):
            stem='U_Com_JP_SystemFont'+size
            gs={g[0]:g for g in v.glyphs((stage/common/(stem+'.uasset')).read_bytes())[0]};pages={}
            def mask(g):
                if g[1] not in pages:
                    p=stage/common/f'{stem}-{g[1]:02d}.uasset'
                    if not p.exists():p=W/'source'/common/p.name
                    pages[g[1]]=v.atlas(p)[0].getchannel('R')
                return pages[g[1]].crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
            cells=[]
            for k in ids:
                encoded=resident[k]['Text'].replace('<count=0>','100')
                encoded=re.sub(r'<button=[^>]+>','[X]',encoded)
                encoded=re.sub('<[^>]+>','',encoded).replace('\r','')
                pen=20;y=45;bottom=y;ops=[]
                for ch in encoded:
                    if ch=='\n':pen=20;y+=50;continue
                    assert ord(ch) in gs,(size,k,ch)
                    g=gs[ord(ch)]
                    if pen+g[8]>950:pen=20;y+=50
                    if g[4] and g[5]:
                        ops.append((pen+g[6],y+g[7],mask(g)))
                        bottom=max(bottom,y+g[7]+g[5])
                    pen+=g[8]
                h=max(150,bottom+20);cell=Image.new('RGB',(980,h),'#15283d');d=ImageDraw.Draw(cell)
                d.text((12,8),size+' | '+k,font=legend,fill='#97d9ef')
                for x,y,m in ops:cell.paste((240,247,255),(x,y),m)
                cells.append(cell);report.append(dict(id=k,font=size,clipped=False,height=h))
            columns.append(cells)
        heights=[max(columns[c][i].height for c in range(2)) for i in range(len(ids))]
        out=Image.new('RGB',(2000,70+sum(h+15 for h in heights)),'#091624');d=ImageDraw.Draw(out)
        d.text((20,15),'Costa activity UI | Actual staged glyphs | Illustrative wrapping and button placeholders | Not in-game',font=legend,fill='#b6d8ec')
        y=60
        for i,h in enumerate(heights):
            for col in range(2):out.paste(columns[col][i],(10+col*1000,y))
            y+=h+15
        out.save(W/ROOT/f'proof-{page+1}.png')
    write(ROOT+'/proof.json',dict(actual_staged_glyphs=True,in_game_screenshot=False,
      wrapping='Proof layout only; not a measurement of game panel widths',control_icons='[X] placeholder for inspection only; source button tags preserved in assets',
      samples=report))
    print('Rendered 3 proof pages, 12 samples in Large and Normal')

if __name__=='__main__':main()
