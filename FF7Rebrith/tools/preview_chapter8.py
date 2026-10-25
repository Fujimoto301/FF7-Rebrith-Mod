"""Actual current glyph proof: UI/voices/native substitutions and low ellipsis."""
import re
from PIL import Image,ImageDraw,ImageFont
from assemble_chapter6 import W,read,write,txtres
ROOT='qa/chapter8'
R='End/Content/Text/JP/Resident_TxtRes.uasset'
from preview_ch12_recheck import renderer

def main(recheck=False):
    cfg=read('reference/chapter8-build.json');stage=W/cfg['stage'];cm=read(cfg['cluster_map'])
    resident=txtres.parse(str(stage/R));legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
    scene='End/Content/Text/JP/8400-GOLDE_TxtRes.uasset'
    rows=read('reference/chapter8-source.json');patch=read('translations/chapter8-th.json')
    selected=[r for r in rows if r['id'] in patch['assets'].get(r['asset'],{}).get('entries',{})]
    sample_templates=[40,71,1082,609,733,877,974,1093,1137,1176,1233,2467]
    samples=[]
    for template in sample_templates:
        r=next(r for r in selected if r['template']==template)
        samples.append((r['id'],txtres.parse(str(stage/r['asset']))[r['id']]['Text']))
    samples += [(k,resident[k]['Text']) for k in ['$minigame_chocoborace_pause_quit_confirm','$minigame_3Dbattler_challenger_name03_hint','$sys_item_drop','$sys_get_exp_ap']]
    samples[-2]=(samples[-2][0],samples[-2][1].replace('<object=0>','Ether'))
    samples[-1]=(samples[-1][0],samples[-1][1].replace('<count=0>','1072').replace('<count=1>','12'))
    if recheck:
        keys=['$CardChallenge_GS_23_Detail','$CardChallenge_GS_21_Detail',
          '$CardChallenge_GS_Condition_Rank_Commander','$minigame_chocoborace_chocobo07_explain',
          '$menu_bike_keyguide_0000_0000','$menu_bike_keyguide_0000_0001',
          '$GS_SHOP_SQUARE1','$keyitem_CoupleTicket_help',
          '$WORLD_CDV_01_0100_9300_00_chd','$WORLD_CDV_01_0100_10000_00_chd',
          '$PHOTO_QST_04_0200_0100_00_fcs','$WORLD_CDV_01_0100_12400_00_chd',
          '$keyitem_collection_075_help','$keyitem_collection_037_help',
          '$CardChallenge_GS_14_Detail','$minigame_chocoborace_pause_quit_confirm']
        samples=[(k,resident[k]['Text']) for k in keys]
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
        d.text((18,16),'Chapter8 | Actual staged glyphs | Illustrative wrapping / button placeholders | Not in-game',font=legend,fill='#bed9eb')
        y=60
        for i,h in enumerate(heights):
            for c in range(2):img.paste(cols[c][i],(10+c*1000,y))
            y+=h+15
        img.save(W/ROOT/f'{"recheck-" if recheck else ""}proof-{page+1}.png')
    write(ROOT+('/recheck-proof.json' if recheck else '/proof.json'),dict(actual_staged_glyphs=True,runtime_substitutions_after_encoding=not recheck,
      preview_wrapping_only=True,source_buttons_preserved=True,in_game_screenshot=False,samples=report))
    print('Rendered4pages,16samples in Large/Normal; includes native ASCII injection and Chapter8 choices')

if __name__=='__main__':
    import sys
    main(recheck='--recheck' in sys.argv)
