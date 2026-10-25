"""Every corrected ID and every recovered tooltip, rendered from staged glyphs."""
import re,math,hashlib
from PIL import Image,ImageDraw,ImageFont
from prepare_chapter9 import W,read,write,txtres
from preview_ch12_recheck import renderer
from chapter11_recheck import Q,decisions
from audit_chapter11 import digest
def main():
    selected=[dict(asset=r['asset'],id=r['id'],template=r['template'],kind='correction') for r in decisions()]+[dict(asset=r['asset'],id=r['id'],template=r['template'],kind='new UI') for r in read('reference/chapter11-recheck-source.json')]
    render_selected(selected,Q,'Ch11 recheck')

def render_selected(selected,out,title,build_config='reference/chapter11-build.json'):
    cfg=read(build_config);stage=W/cfg['stage']
    gs,mask=renderer(stage,'U_Com_JP_SystemFontNormal.uasset');data={a:txtres.parse(str(stage/a)) for a in {r['asset'] for r in selected}};legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17);samples=[];pages=math.ceil(len(selected)/8)
    for page in range(pages):
        cells=[]
        for r in selected[page*8:(page+1)*8]:
            t=re.sub('<[^>]+>','',data[r['asset']][r['id']]['Text']).replace('\r','');ops=[];pen=14;y=42;bottom=112
            for ch in t:
                if ch=='\n':pen=14;y+=40;continue
                assert ord(ch) in gs,(r['id'],ch)
                g=gs[ord(ch)]
                if pen+g[8]>926:pen=14;y+=40
                if g[4] and g[5]:
                    x=pen+g[6];yy=y+g[7];assert x>=0 and x+g[4]<=940 and yy>=30,(r['id'],'clip');ops.append((x,yy,mask(g)));bottom=max(bottom,yy+g[5]+16)
                pen+=g[8]
            cell=Image.new('RGB',(940,bottom),'#17283d');dr=ImageDraw.Draw(cell);dr.text((10,8),r['kind']+' | '+str(r['template'])+' | Normal',font=legend,fill='#9fd8e8')
            for x,y,m in ops:cell.paste((242,247,255),(x,y),m)
            cells.append(cell);samples.append(dict(r,font='Normal',clipped=False))
        rows=[cells[i:i+2] for i in range(0,len(cells),2)];heights=[max(c.height for c in pair) for pair in rows];canvas=Image.new('RGB',(1920,55+sum(h+12 for h in heights)),'#091522');dr=ImageDraw.Draw(canvas);dr.text((15,12),f'{title} {page+1}/{pages} | Actual staged glyphs | Illustrative wrapping | Not in-game',font=legend,fill='#bfd7ed');y=50
        for pair,h in zip(rows,heights):
            for col,cell in enumerate(pair):canvas.paste(cell,(10+col*960,y))
            y+=h+12
        canvas.save(W/out/f'proof-{page+1}.png')
    write(out+'proof.json',dict(source_sha256=digest(W/cfg['source']),pages=pages,samples=samples,actual_staged_glyphs=True,font='Normal',all_selected_records=True,in_game_tested=False));print('Rendered',pages,'proof pages for',len(samples),'records')
if __name__=='__main__':main()
