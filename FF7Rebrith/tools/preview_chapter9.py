"""Render actual current glyphs with representative dialogue and whole choices."""
import re,sys
from PIL import Image,ImageDraw,ImageFont
from prepare_chapter9 import W,read,write,txtres
from preview_ch12_recheck import renderer

def main():
    cfg=read('reference/chapter9-build.json');stage=W/cfg['stage'];rows=read('reference/chapter9-source.json');decoded={};samples=[]
    indices=[293,943,444,512,2259,2260,2261,1733,834,2149,181,382,810,811,812,813] if '--recheck' in sys.argv else [382,76,181,223,309,365,510,573,678,765,810,811,812,813,1293,2248]
    prefix='recheck-' if '--recheck' in sys.argv else ''
    for i in indices:
        r=next(r for r in rows if r['template']==i and not r['reason']);a=r['asset']
        if a not in decoded:decoded[a]=txtres.parse(str(stage/a))
        samples.append((r['id'],decoded[a][r['id']]['Text']))
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20);report=[]
    for page in range(4):
        cols=[]
        for size in ['Large','Normal']:
            gs,mask=renderer(stage,f'U_Com_JP_SystemFont{size}.uasset');cells=[]
            for label,text in samples[page*4:(page+1)*4]:
                text=re.sub('<button=[^>]+>','[X]',text);text=re.sub('<[^>]+>','',text).replace('\r','');pen=18;y=40;bottom=110;ops=[]
                for ch in text:
                    if ch=='\n':pen=18;y+=48;continue
                    assert ord(ch) in gs,(size,label,ch);g=gs[ord(ch)]
                    if pen+g[8]>950:pen=18;y+=48
                    if g[4] and g[5]:ops.append((pen+g[6],y+g[7],mask(g)));bottom=max(bottom,y+g[7]+g[5]+20)
                    pen+=g[8]
                cell=Image.new('RGB',(980,bottom),'#16273b');d=ImageDraw.Draw(cell);d.text((10,8),size+' | '+label,font=legend,fill='#9bcee9')
                for x,y,m in ops:cell.paste((240,246,253),(x,y),m)
                cells.append(cell);report.append(dict(font=size,id=label,clipped=False))
            cols.append(cells)
        heights=[max(cols[0][i].height,cols[1][i].height) for i in range(4)];img=Image.new('RGB',(2000,65+sum(x+15 for x in heights)),'#091622');d=ImageDraw.Draw(img);d.text((18,16),'Chapter9 | Actual staged glyphs | Illustrative wrapping / buttons | Not in-game',font=legend,fill='#bed9eb');y=60
        for i,h in enumerate(heights):
            for col in range(2):img.paste(cols[col][i],(10+col*1000,y))
            y+=h+15
        img.save(W/f'qa/chapter9/{prefix}proof-{page+1}.png')
    write(f'qa/chapter9/{prefix}proof.json',dict(actual_staged_glyphs=True,samples=report,in_game_screenshot=False,illustrative_wrapping=True))
    print('Rendered4pages,16samples in2font sizes')

if __name__=='__main__':main()
