"""Glyph proof from staged menu assets; not a simulated in-game screenshot."""
import json,re
from PIL import Image,ImageDraw,ImageFont
import verify_chapter1 as v
import txtres
W=v.WORK;STAGE=W/'staging/ThaiJP_Inventory_Working';QA=W/'qa/inventory'
COMMON='End/Content/Menu/Billboard/Common';FONT='U_Com_JP_SystemFontNormal'
def main():
    glyphs={g[0]:g for g in v.glyphs((STAGE/COMMON/(FONT+'.uasset')).read_bytes())[0]}
    pages={}
    def page(n):
        if n not in pages:
            p=STAGE/COMMON/f'{FONT}-{n:02d}.uasset'
            if not p.exists():p=W/'source'/COMMON/p.name
            pages[n]=v.atlas(p)[0].getchannel('R')
        return pages[n]
    d=txtres.parse(str(STAGE/'End/Content/Text/JP/Resident_TxtRes.uasset'))
    samples=[('$item_potion','Potion'),('$item_gravity','Orb of Gravity'),
             ('$Item_M_SUP_001','Magnify'),('$M_MAG_004_atk003','Firaga'),
             ('$PC0005_AtkBurst10',"Storm's Fury"),('$BattleSkill_128_LastLeave','Reprieve'),
             ('$menu_EQSkill_E_ACC_0008','Revival Earrings'),('$ChocoboRaceAbility_01','Speed Burst')]
    out=Image.new('RGB',(1800,1700),'#0b1525');draw=ImageDraw.Draw(out)
    legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23)
    draw.text((35,20),'Item / Skill effects | Actual staged glyph proof | Not an in-game screenshot',font=legend,fill='#bdd2ed')
    reports=[]
    for i,(key,label) in enumerate(samples):
        candidates=[key+'_help',key+'_Detail',key]
        key=next(k for k in candidates if k in d and (k.endswith(('_help','_Detail')) or k.startswith('$menu_EQSkill')))
        text=d[key]['Text'];text=re.sub(r'<count=\d+>','5',text)
        text=re.sub(r'<object=\d+>','Fire',text);text=re.sub(r'<[^>]+>','',text)
        col=i%2;row=i//2;x=25+col*890;top=75+row*395
        draw.rounded_rectangle((x,top,x+860,top+375),radius=12,fill='#111f34',outline='#2c4666')
        draw.text((x+25,top+20),label,font=legend,fill='#9bd7f5')
        pen=x+25;y=top+75;maxx=pen
        for c in text:
            if c in '\r\n':
                if c=='\n':pen=x+25;y+=38
                continue
            assert ord(c) in glyphs,(key,hex(ord(c)))
            g=glyphs[ord(c)]
            if pen+g[8]>x+830:pen=x+25;y+=38
            if g[4] and g[5]:
                mask=page(g[1]).crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
                out.paste((237,244,254),(pen+g[6],y+g[7]),mask)
            pen+=g[8];maxx=max(maxx,pen)
        assert y<top+340,(key,'Sample overflow')
        reports.append({'id':key,'name':label,'width':maxx-x-25,'lines':1+(y-top-75)//38})
    out.save(QA/'font-proof.png')
    (QA/'font-proof.json').write_text(json.dumps({'in_game_screenshot':False,'uses_staged_glyphs':True,'preview_only_wrap':True,'samples':reports},indent=2),'utf-8')
    print(QA/'font-proof.png')
if __name__=='__main__':main()
