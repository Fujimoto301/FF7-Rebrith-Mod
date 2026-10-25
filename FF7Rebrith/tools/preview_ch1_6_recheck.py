"""Actual current glyph proof: UI/voices/native substitutions and low ellipsis."""
import re
from PIL import Image,ImageDraw,ImageFont
from assemble_chapter6 import W,read,write,txtres
from prepare_ch1_6_recheck import ROOT,R
from preview_ch12_recheck import renderer

def main():
    cfg=read('reference/ch1-6-recheck-build.json');stage=W/cfg['stage'];cm=read(cfg['cluster_map'])
    resident=txtres.parse(str(stage/R));legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
    ids=['$menu_condor_player_unit_detail_guide','$CF_minigame_birdview_button_guide',
      '$minigame_soldierformation_form_03_help','$minigame_soldierformation_Button_Long',
      '$minigame_DolphinJump_Syslog_JumpFailure','$menu_WorldReport_GRASA_02_Detail_Clear',
      '$it_key_minigamecardPack_003_help','$key_qst07_CollectionMemo_help',
      '$PHOTO_QST_00_0100_0300_00_fcs','$PHOTO_QST_02_0400_0400_00_fcs',
      '$PIANO_QST_01_0200_0400_00_sys','$PHOTO_QST_03_0100_0300_00_fcs',
      '$minigame_chocobocraft_dig_notfound','$sys_item_drop','$sys_get_exp_ap']
    samples=[(k,resident[k]['Text']) for k in ids]
    samples[-2]=(samples[-2][0],samples[-2][1].replace('<object=0>','Ether'))
    samples[-1]=(samples[-1][0],samples[-1][1].replace('<count=0>','1072').replace('<count=1>','12'))
    samples.append(('New appended glyphs', ''.join(cm.get(ch,ch) for ch in __import__('build_prototype').split_clusters('พ็ ฟิ้ อึ้ คลาวด์…'))))
    report=[]
    for page in range(4):
        cols=[]
        for size in ['Large','Normal']:
            gs,mask=renderer(stage,f'U_Com_JP_SystemFont{size}.uasset');cells=[]
            for label,text in samples[page*4:(page+1)*4]:
                text=re.sub('<button=[^>]+>','[X]',text);text=re.sub('<[^>]+>','',text).replace('\r','')
                pen=18;y=40;bottom=110;ops=[]
                for ch in text:
                    if ch=='\n':pen=18;y+=48;continue
                    assert ord(ch) in gs,(size,label,ch)
                    g=gs[ord(ch)]
                    if pen+g[8]>950:pen=18;y+=48
                    if g[4] and g[5]:
                        ops.append((pen+g[6],y+g[7],mask(g)));bottom=max(bottom,y+g[7]+g[5]+20)
                    pen+=g[8]
                cell=Image.new('RGB',(980,bottom),'#16273b');d=ImageDraw.Draw(cell)
                d.text((10,8),size+' | '+label,font=legend,fill='#9bcee9')
                for x,y,m in ops:cell.paste((240,246,253),(x,y),m)
                cells.append(cell);report.append(dict(font=size,sample=label,proof_height=bottom,clipped=False))
            cols.append(cells)
        heights=[max(cols[0][i].height,cols[1][i].height) for i in range(4)]
        img=Image.new('RGB',(2000,65+sum(x+15 for x in heights)),'#091622');d=ImageDraw.Draw(img)
        d.text((18,16),'Ch.1–6 recheck | Actual staged glyphs | Illustrative wrapping / button placeholders | Not in-game',font=legend,fill='#bed9eb')
        y=60
        for i,h in enumerate(heights):
            for c in range(2):img.paste(cols[c][i],(10+c*1000,y))
            y+=h+15
        img.save(W/ROOT/f'proof-{page+1}.png')
    write(ROOT+'/proof.json',dict(actual_staged_glyphs=True,runtime_substitutions_after_encoding=True,
      preview_wrapping_only=True,source_buttons_preserved=True,in_game_screenshot=False,samples=report))
    print('Rendered4pages,16samples in Large/Normal; includes native ASCII injection and new3clusters')

if __name__=='__main__':main()
