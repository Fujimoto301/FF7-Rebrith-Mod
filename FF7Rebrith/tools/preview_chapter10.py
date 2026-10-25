"""Illustrative proof from encoded text and actual staged game glyph masks."""
import re,hashlib
from PIL import Image,ImageDraw,ImageFont
from prepare_chapter9 import W,read,write,txtres
from preview_ch12_recheck import renderer

def main():
    cfg=read('reference/chapter10-build.json');stage=W/cfg['stage'];rows=read('qa/chapter10/review-records.json');by={r['template']:r for r in rows}
    continued=(W/'qa/chapter10/continue-review/current.json').exists()
    if continued:
        from chapter10_continue_review import FIXES
        selected=[by[n] for n in [124,408,688,1704,2615,'recheck-54']]
        selected += [by[int(k)] for k in FIXES if k.isdigit()]
    else:
        selected=[by[n] for n in [124,408,608,688,1103,1161,1306,1389,1575,1602,1704,1794,2333,2343,2523,2615]]
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18);report=[];data={a:txtres.parse(str(stage/a)) for a in {r['asset'] for r in selected}}
    cosmo='End/Content/Text/JP/8600-COSME_TxtRes.uasset'
    for prefix,lines in [('$C2910_MAIN_4800_',['0200','0300','0400']),('$CHADL_QST_05_0700_',['2400','2500','2600']),('$COSME_QST_01_0800_',['1100','1200','1300']),('$COSME_QST_03_1700_',['1000','1100','1200','1300','1400'])]:
        keys=[prefix+n+'_00_sys' for n in lines]
        selected.append(dict(asset=cosmo,id=keys[0],ids=keys,template='choice-set',actor='UI | '+prefix))
    if (W/'reference/chapter10-recheck-source.json').exists():
        selected += [by[n] for n in (['recheck-89','recheck-90'] if continued else ['recheck-54','recheck-38','recheck-15','recheck-111','recheck-82',174,634,'recheck-139'])]
        for a in {r['asset'] for r in selected}-data.keys():data[a]=txtres.parse(str(stage/a))
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
        dr.text((15,15),'Chapter10 | Actual staged glyphs | Illustrative wrapping and font selection | Not in-game',font=legend,fill='#bfd7ed');y=55
        for cs,h in zip(pairs,heights):
            for col,cell in enumerate(cs):canvas.paste(cell,(10+col*980,y))
            y+=h+12
        canvas.save(W/f'qa/chapter10/proof-{page+1}.png')
    write('qa/chapter10/proof.json',dict(source_sha256=hashlib.sha256((W/cfg['source']).read_bytes()).hexdigest(),actual_staged_glyphs=True,samples=report,illustrative_wrapping=True,in_game_tested=False))
    print('Rendered',len(selected)//4,'proof pages including4 complete question/option sets')
if __name__=='__main__':main()
