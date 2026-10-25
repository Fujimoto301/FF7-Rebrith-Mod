"""Render official action labels and native numbers from actual staged fonts."""
import hashlib,re
from PIL import Image,ImageDraw,ImageFont
from prepare_chapter9 import W,read,write,txtres
from preview_ch12_recheck import renderer


def main():
    cfg=read('reference/enemy-actions-build.json');stage=W/cfg['stage']
    r='End/Content/Text/JP/Resident_TxtRes.uasset';d=txtres.parse(str(stage/r))
    rows=read('reference/enemy-actions-source.json');keys=['$bt_MidgarZolom_Flamethrower','$EN9000_10_AtkMagicCircle01','$bt_Judge_Judgement']
    keys+=[r['id'] for r in rows if r['mode']=='official_US' and any(ch.isdigit() for ch in r['English']['Text'])][:2]
    keys+=[r['id'] for r in sorted(rows,key=lambda r:len(r['English']['Text']),reverse=True) if r['id'] not in keys][:3]
    assert len(keys)==8;legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19);report=[]
    for page in range(2):
        canvas=Image.new('RGB',(2000,840),'#091622');dr=ImageDraw.Draw(canvas)
        dr.text((18,16),'Official enemy actions | Actual staged glyphs | Illustrative wrapping | Not in-game',font=legend,fill='#bed9eb')
        for col,size in enumerate(['Large','Normal']):
            gs,mask=renderer(stage,f'U_Com_JP_SystemFont{size}.uasset')
            for i,k in enumerate(keys[page*4:(page+1)*4]):
                x0=10+col*1000;y0=60+i*195;cell=Image.new('RGB',(980,180),'#16273b');dd=ImageDraw.Draw(cell)
                dd.text((10,6),size+' | '+k,font=legend,fill='#9bcee9');pen=18;y=42
                text=d[k]['Text']+' / 1072 EXP'
                for ch in text:
                    assert ord(ch) in gs,(size,k,ch);g=gs[ord(ch)]
                    if pen+g[8]>960:pen=18;y+=55
                    if g[4] and g[5]:
                        x=pen+g[6];gy=y+g[7];assert x>=0 and x+g[4]<980 and gy>=30 and gy+g[5]<180,(k,'clip')
                        cell.paste((240,246,253),(x,gy),mask(g))
                    pen+=g[8]
                canvas.paste(cell,(x0,y0));report.append(dict(font=size,id=k,clipped=False,synthetic_numeric_suffix=True))
        canvas.save(W/f'qa/enemy-actions/proof-{page+1}.png')
    write('qa/enemy-actions/proof.json',dict(source_sha256=hashlib.sha256((W/cfg['source']).read_bytes()).hexdigest(),
        actual_staged_glyphs=True,samples=report,in_game_screenshot=False))
    print('Rendered 2 pages / 8 action labels in Large and Normal')


if __name__=='__main__':main()
