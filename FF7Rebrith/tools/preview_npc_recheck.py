"""Render screenshot fixes and whole choice sets from actual staged glyphs."""
import hashlib,re,sys
from PIL import Image,ImageDraw,ImageFont
from prepare_chapter9 import W,read,write,txtres
from preview_ch12_recheck import renderer


def main():
    cfg=read('reference/npc-recheck-build.json');stage=W/cfg['stage']
    rows=read('reference/npc-recheck-source.json');templates=read('reference/npc-recheck-templates.json')
    choices=[]
    for i in [213,214,218,219,172,260,305,390,497,553,633,886,969,1142,1339,1449]:
        r=next(r for r in rows if r.get('template')==i)
        choices.append((r['asset'],r['id']))
    prefix=''
    decoded={};samples=[]
    for a,k in choices:
        if a not in decoded:decoded[a]=txtres.parse(str(stage/a))
        samples.append((a,k,decoded[a][k]['Text']))
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20);report=[]
    for page in range(4):
        cols=[]
        for size in ['Large','Normal']:
            gs,mask=renderer(stage,f'U_Com_JP_SystemFont{size}.uasset');cells=[]
            for a,key,text in samples[page*4:(page+1)*4]:
                # Substitute runtime variables only for illustrative proof rendering.
                text=text.replace('<object=0>','Cushion')
                text=re.sub('<button=[^>]+>','[X]',text)
                text=re.sub('<[^>]+>','',text).replace('\r','')
                pen=18;y=42;bottom=115;ops=[]
                for ch in text:
                    if ch=='\n':pen=18;y+=60;continue
                    assert ord(ch) in gs,(size,key,ch);g=gs[ord(ch)]
                    if pen+g[8]>950:pen=18;y+=60
                    if g[4] and g[5]:
                        x=pen+g[6];gy=y+g[7]
                        assert x>=0 and x+g[4]<980 and gy>=35,(key,'clip')
                        ops.append((x,gy,mask(g)));bottom=max(bottom,gy+g[5]+20)
                    pen+=g[8]
                cell=Image.new('RGB',(980,bottom),'#16273b');d=ImageDraw.Draw(cell)
                d.text((10,8),size+' | '+key,font=legend,fill='#9bcee9')
                for x,gy,m in ops:cell.paste((240,246,253),(x,gy),m)
                cells.append(cell);report.append(dict(font=size,asset=a,id=key,clipped=False))
            cols.append(cells)
        heights=[max(cols[0][i].height,cols[1][i].height) for i in range(4)]
        img=Image.new('RGB',(2000,65+sum(h+15 for h in heights)),'#091622')
        ImageDraw.Draw(img).text((18,16),'NPC recovery / all visited regions | Actual staged glyphs | Illustrative wrapping / variables | Not in-game',font=legend,fill='#bed9eb');y=60
        for i,h in enumerate(heights):
            for col in range(2):img.paste(cols[col][i],(10+col*1000,y))
            y+=h+15
        img.save(W/f'qa/npc-recheck/{prefix}proof-{page+1}.png')
    write(f'qa/npc-recheck/{prefix}proof.json',dict(source_sha256=hashlib.sha256((W/cfg['source']).read_bytes()).hexdigest(),
        actual_staged_glyphs=True,samples=report,in_game_screenshot=False,illustrative_wrapping_and_variables=True))
    print('Rendered 4 pages / 16 samples / 2 fonts from staged assets')


if __name__=='__main__':main()
