"""Render samples from the actual working font/text assets, not the game."""
import json
import re
from PIL import Image, ImageDraw, ImageFont
import verify_chapter1 as v
import txtres

W=v.WORK
STAGE=W/'staging/ThaiJP_ThroughChapter2_Working'
QA=W/'qa/chapter2'
COMMON='End/Content/Menu/Billboard/Common'
FONT='U_Com_JP_SystemFontLarge'

def main():
    rows=json.loads((W/'reference/chapter2-source.json').read_text(encoding='utf-8'))+json.loads((W/'reference/chapter2-shared-source.json').read_text(encoding='utf-8'))
    glyphs={g[0]:g for g in v.glyphs((STAGE/COMMON/(FONT+'.uasset')).read_bytes())[0]}
    pages={}
    def page(n):
        if n not in pages:
            p=STAGE/COMMON/f'{FONT}-{n:02d}.uasset'
            if not p.exists():p=W/'source'/COMMON/p.name
            pages[n]=v.atlas(p)[0].getchannel('R')
        return pages[n]
    samples=[8,310,504,458,1878,2376,2502,1700]
    out=Image.new('RGB',(1800,1860),'#0b1525')
    draw=ImageDraw.Draw(out)
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24)
    draw.text((35,20),'Chapter 2 | Actual staged font proof, not an in-game screenshot',font=legend,fill='#bdd2ed')
    measures=[]
    def render(text,x,y):
        for li,line in enumerate(text.splitlines()):
            line=re.sub(r'<[^>]+>','',line)
            pen=x
            for c in line:
                g=glyphs[ord(c)]
                if g[4] and g[5]:
                    mask=page(g[1]).crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
                    out.paste((237,244,254),(pen+g[6],y+li*49+g[7]),mask)
                pen+=g[8]
            assert pen<1760,(text,pen)
            measures.append(pen-x)
    for number,index in enumerate(samples):
        r=rows[index];item=txtres.parse(str(STAGE/r['asset']))[r['id']]
        top=80+number*220
        draw.rounded_rectangle((25,top,1775,top+205),radius=12,fill='#111f34',outline='#2c4666')
        draw.text((45,top+12),f"Record {index} | {item.get('MetaData',{}).get('ACTOR','Choice')}",font=legend,fill='#78acd9')
        render(item['Text'],60,top+65)
    out.save(QA/'font-proof.png')
    (QA/'font-proof.json').write_text(json.dumps(dict(in_game_screenshot=False,rendered_from_working_assets=True,sample_indices=samples,max_width=max(measures),panel_width=1680),indent=2),encoding='utf-8')
    print(QA/'font-proof.png')

if __name__=='__main__':main()
