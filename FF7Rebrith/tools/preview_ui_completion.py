"""Render actual working glyphs for review, without simulating the game UI."""
import json,re
from PIL import Image,ImageDraw,ImageFont
import verify_chapter1 as v
W=v.WORK;STAGE=W/'staging/ThaiJP_UICompletion_Working';QA=W/'qa/ui-completion'
COMMON='End/Content/Menu/Billboard/Common'

def main(samples_override=None,proof_name='font-proof'):
    d=v.txtres.parse(str(STAGE/'End/Content/Text/JP/Resident_TxtRes.uasset'))
    rows=json.loads((W/'reference/ui-completion-source.json').read_text('utf-8'))
    def template(n):return next(r['id'] for r in rows if r.get('template')==n)
    samples=[('Chapter title',['$chapter_title_0001']),
             ('Temporal captions',['$lvl_time_5yearsago','$lvl_time_now','$area2360_4yearsago']),
             ('Status / resistances',['$status_0002_0002','$status_0002_0005','$menu_Libra_0004_0002']),
             ('Menu navigation',[template(4654),template(4652)]),
             ('Equipment description',['$Item_E_ACC_0001_help']),
             ('Settings',[template(2416),template(2417)]),
             ('Story objectives',[template(3687),template(3832)]),
             ('Map / crafting',[template(4835),template(4836),template(4753)])]
    if samples_override is not None:samples=samples_override
    out=Image.new('RGB',(1880,2020),'#091523');draw=ImageDraw.Draw(out)
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
    draw.text((25,18),'UI completion | Actual staged glyphs | Preview wrapping only | Not an in-game screenshot',font=legend,fill='#bdd4eb')
    report=[]
    for col,size in enumerate(('Normal','Small')):
        stem='U_Com_JP_SystemFont'+size
        glyphs={g[0]:g for g in v.glyphs((STAGE/COMMON/(stem+'.uasset')).read_bytes())[0]};pages={}
        def page(n):
            if n not in pages:
                p=STAGE/COMMON/f'{stem}-{n:02d}.uasset'
                if not p.exists():p=W/'source'/COMMON/p.name
                pages[n]=v.atlas(p)[0].getchannel('R')
            return pages[n]
        for row,(label,keys) in enumerate(samples):
            left=20+col*935;top=65+row*240
            draw.rounded_rectangle((left,top,left+910,top+225),radius=10,fill='#122238',outline='#31516b')
            draw.text((left+18,top+10),size+' | '+label,font=legend,fill='#92d7f6')
            text='\n'.join(d[k]['Text'] for k in keys)
            # Tokens are omitted in the proof; the actual assets retain all of them.
            text=re.sub(r'<[^>]+>','',text)
            x=left+18;y=top+46;max_bottom=y
            for c in text:
                if c=='\r':continue
                if c=='\n':x=left+18;y+=32;continue
                assert ord(c) in glyphs,(keys,hex(ord(c)))
                g=glyphs[ord(c)]
                if x+g[8]>left+885:x=left+18;y+=32
                if g[4] and g[5]:
                    mask=page(g[1]).crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
                    out.paste((238,245,255),(x+g[6],y+g[7]),mask)
                    max_bottom=max(max_bottom,y+g[7]+g[5])
                x+=g[8]
            assert max_bottom<top+218,(size,label,'Proof panel overflow')
            report.append(dict(font=size,ids=keys,tag_tokens_omitted_for_proof=True,clipped=False))
    out.save(QA/(proof_name+'.png'))
    (QA/(proof_name+'.json')).write_text(json.dumps(dict(actual_staged_glyphs=True,in_game_screenshot=False,
        preview_only_wrap=True,samples=report),indent=2)+'\n','utf-8')
    print(QA/(proof_name+'.png'))

if __name__=='__main__':main()
