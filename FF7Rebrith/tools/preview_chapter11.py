"""Illustrative proof from encoded text and actual staged game glyph masks."""
import re,hashlib
from PIL import Image,ImageDraw,ImageFont
from prepare_chapter9 import W,read,write,txtres
from preview_ch12_recheck import renderer

def main():
    cfg=read('reference/chapter11-build.json');stage=W/cfg['stage'];rows=read('qa/chapter11/review-records.json');by={r['template']:r for r in rows}
    selected=[by[n] for n in [43,107,143,191,237,327,359,450,475,485,507,533,548,595,607,614,668,703,709,750,798,818,891,903,951,955,1032,1106,1164,1200,1214,1400,1517,1586,1614,1639]]
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18);report=[]
    asset='End/Content/Text/JP/8700-NIBLE_TxtRes.uasset'
    corpus=read('reference/rebirth-jp-corpus.json')['8700-NIBLE_TxtRes.uasset']
    groups={}
    for k,v in corpus.items():
        if k.endswith('_sys') and v['Text'] and k.startswith(('$C3110_','$NIBLE_QST_01_','$NIBLE_QST_02_')):
            group='_'.join(k.split('_')[:-3]);groups.setdefault(group,[]).append(k)
    for prefix,keys in groups.items():selected.append(dict(asset=asset,id=keys[0],ids=keys,template='choices:'+prefix,actor='UI'))
    data={a:txtres.parse(str(stage/a)) for a in {r['asset'] for r in selected}}
    write('qa/chapter11/choice-groups.json',dict(groups=groups,question_and_all_buttons=True,context_review='Reviewed Japanese question, all options and nearby response translations. Source order is context, not runtime branch proof.',in_game_tested=False))
    fonts={size:renderer(stage,f'U_Com_JP_SystemFont{size}.uasset') for size in ['Large','Normal']}
    for page in range(len(selected)//4):
        pairs=[]
        for r in selected[page*4:(page+1)*4]:
            cells=[]
            for size in fonts:
                gs,mask=fonts[size];t=re.sub('<[^>]+>','','\r\n'.join(data[r['asset']][k]['Text'] for k in r.get('ids',[r['id']]))).replace('\r','');ops=[];pen=14;y=42;bottom=130
                for ch in t:
                    if ch=='\n':pen=14;y+=55;continue
                    assert ord(ch) in gs,(r['id'],ch)
                    g=gs[ord(ch)]
                    if pen+g[8]>946:pen=14;y+=55
                    if g[4] and g[5]:
                        x=pen+g[6];yy=y+g[7];assert x>=0 and x+g[4]<=960 and yy>=30,(r['id'],'clip');ops.append((x,yy,mask(g)));bottom=max(bottom,yy+g[5]+18)
                    pen+=g[8]
                cell=Image.new('RGB',(960,bottom),'#17283d');dr=ImageDraw.Draw(cell);dr.text((10,8),size+' | '+str(r['template'])+' | '+r['actor'],font=legend,fill='#9fd8e8')
                for x,y,m in ops:cell.paste((242,247,255),(x,y),m)
                cells.append(cell);report.append(dict(id=r['id'],template=r['template'],font=size,clipped=False))
            pairs.append(cells)
        heights=[max(x.height for x in cs) for cs in pairs];canvas=Image.new('RGB',(1960,60+sum(h+12 for h in heights)),'#091522');dr=ImageDraw.Draw(canvas)
        dr.text((15,15),'Chapter11 | Actual staged glyphs | Illustrative wrapping and font selection | Not in-game',font=legend,fill='#bfd7ed');y=55
        for cs,h in zip(pairs,heights):
            for col,cell in enumerate(cs):canvas.paste(cell,(10+col*980,y))
            y+=h+12
        canvas.save(W/f'qa/chapter11/proof-{page+1}.png')
    write('qa/chapter11/proof.json',dict(source_sha256=hashlib.sha256((W/cfg['source']).read_bytes()).hexdigest(),actual_staged_glyphs=True,samples=report,illustrative_wrapping=True,in_game_tested=False))
    print('Rendered',len(selected)//4,'proof pages including',len(groups),'complete question/option sets')
if __name__=='__main__':main()
