"""Before/after ellipsis and shared-dialogue proof from real staged font glyphs."""
import re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import verify_chapter1 as v
from assemble_chapter6 import W,read,write
from prepare_ch12_recheck import ROOT,R

COMMON=Path('End/Content/Menu/Billboard/Common')
def renderer(stage,fontname):
    gs={g[0]:g for g in v.glyphs((stage/COMMON/fontname).read_bytes())[0]};pages={}
    def mask(g):
        if g[1] not in pages:
            p=stage/COMMON/(Path(fontname).stem+f'-{g[1]:02d}.uasset')
            if not p.exists():p=W/'source'/COMMON/p.name
            pages[g[1]]=v.atlas(p)[0].getchannel('R')
        return pages[g[1]].crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
    return gs,mask

def main():
    cfg=read('reference/ch12-recheck-build.json');base=read(ROOT+'/baseline.json')
    stage=W/cfg['stage'];before=W/base['snapshot']/'stage';cmap=read(cfg['cluster_map'])
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
    fonts=sorted(p.name for p in (stage/COMMON).glob('U_Com_JP_SystemFont*.uasset') if '-' not in p.name)
    out=Image.new('RGB',(2050,70+len(fonts)*200),'#091522');d=ImageDraw.Draw(out);reports=[]
    d.text((20,15),'Ellipsis before / after | Actual asset glyphs, green line = native full-stop bottom | Not in-game',font=legend,fill='#bfd7ed')
    text=''.join(cmap.get(ch,ch) for ch in v.b.split_clusters('คลาวด์…'))
    for row,fontname in enumerate(fonts):
        top=65+row*200
        for col,folder in enumerate((before,stage)):
            gs,mask=renderer(folder,fontname);left=20+col*1020
            d.rounded_rectangle((left,top,left+995,top+190),radius=8,fill='#17283d')
            d.text((left+10,top+6),('Before | ' if col==0 else 'After | ')+fontname,font=legend,fill='#9fd8e8')
            y=top+44;pen=left+20
            period=gs[ord('.')];bottom=y+period[7]+mask(period).point(lambda p:255 if p>=64 else 0).getbbox()[3]
            d.line((left+15,bottom,left+970,bottom),fill='#3d845e')
            for ch in text:
                g=gs[ord(ch)]
                if g[4] and g[5]:out.paste((242,247,255),(pen+g[6],y+g[7]),mask(g))
                pen+=g[8]
            eg=gs[8230];eb=y+eg[7]+mask(eg).point(lambda p:255 if p>=64 else 0).getbbox()[3]
            if col:assert eb==bottom
            reports.append(dict(font=fontname,state='before' if col==0 else 'after',ellipsis_bottom=eb-y,full_stop_bottom=bottom-y))
    out.save(W/ROOT/'ellipsis-before-after.png')
    resident=v.txtres.parse(str(stage/R));title=v.txtres.parse(str(stage/'End/Content/Text/JP/0005-TITLB_TxtRes.uasset'))
    samples=[('$minigame_cardgame_tutorial_Check',resident),('$minigame_cardgame_tutorial_YES',resident),
      ('$minigame_cardgame_tutorial_NO',resident),('$minigame_cardgame_pause_retire_comfirm_lose',resident),
      ('$minigame_cardgame_deckedit_exit_alert',resident),('$minigame_cardgame_presetdeck6_help',resident),
      ('$minigame_mooglecapture_DoorOpen_EasyMode',resident),('$minigame_mooglecapture_Retry_Text',resident),
      ('$minigame_chocobocapture_attention7',resident),('$minigame_chocobocapture_pause_retry_comfirm_reset',resident),
      ('$C1910_MAIN_0050_0900_00_red',title),('$C1910_MAIN_0050_1500_00_red',title)]
    gs,mask=renderer(stage,'U_Com_JP_SystemFontNormal.uasset');cells=[]
    for key,data in samples:
        t=re.sub('<button=[^>]+>','[X]',data[key]['Text']);t=re.sub('<[^>]+>','',t).replace('\r','')
        y=40;pen=20;ops=[];bottom=100
        for ch in t:
            if ch=='\n':pen=20;y+=45;continue
            g=gs[ord(ch)]
            if pen+g[8]>1150:pen=20;y+=45
            if g[4] and g[5]:ops.append((pen+g[6],y+g[7],mask(g)));bottom=max(bottom,y+g[7]+g[5]+20)
            pen+=g[8]
        cell=Image.new('RGB',(1180,bottom),'#17283d');cd=ImageDraw.Draw(cell);cd.text((12,8),key,font=legend,fill='#9fd8e8')
        for x,y,m in ops:cell.paste((242,247,255),(x,y),m)
        cells.append(cell)
    for page in range(3):
        cs=cells[page*4:(page+1)*4];out=Image.new('RGB',(1200,65+sum(c.height+15 for c in cs)),'#091522');d=ImageDraw.Draw(out)
        d.text((15,15),'Staged UI / recap proof | Illustrative wrapping, [X] icon placeholder | Not in-game',font=legend,fill='#bfd7ed')
        y=60
        for cell in cs:out.paste(cell,(10,y));y+=cell.height+15
        out.save(W/ROOT/f'ui-proof-{page+1}.png')
    write(ROOT+'/proof.json',dict(actual_staged_glyphs=True,ellipsis_comparison=reports,UI_and_recap_samples=[k for k,d in samples],
      preview_only_wrap=True,in_game_tested=False))
    print('Rendered ellipsis before/after for all8 fonts and3 UI/recap proof pages')

if __name__=='__main__':main()
