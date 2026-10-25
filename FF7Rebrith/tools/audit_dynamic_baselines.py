"""Verify real runtime-style ASCII substitutions, preserving all original glyphs."""
import hashlib,re,string,struct
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from create_ui_completion_scope import W,R,read,write
from assemble_ui_completion import fingerprint,protected_snapshot
import verify_chapter1 as v

COMMON=Path('End/Content/Menu/Billboard/Common');STAGE=W/'staging/ThaiJP_UICompletion_Working'
QA=W/'qa/baseline-alignment'

def main():
    baseline=read('qa/baseline-alignment/baseline.json');backup=Path(baseline['backup'])
    cmap=read('reference/ui-completion-cluster-map.json')
    before=read(baseline['previous_assets']);after=read('qa/ui-completion/working-assets.json')
    fonts={a for a in before if 'Menu\\Billboard\\Common\\U_Com_JP_SystemFont' in a and '-' not in Path(a).name}
    assert len(fonts)==8
    assert {a for a in before if before[a]!=after[a]}==fonts,'Only eight font metadata files may change'
    previous=read(baseline['previous_combined_source']);current=read('translations/working-ui-completion-th.json')
    assert previous==current,'Translation text or actor metadata changed'
    assert read(str(backup/'reference/ui-completion-cluster-map.json'))==cmap
    actual=v.txtres.parse(str(STAGE/R))
    english=read('translations/enemy-names-th.json')['assets'][R]['entries']
    # Substitute after alias encoding, as the game does. These injected names,
    # letters and numbers remain native ASCII: the failure case in the photos.
    samples=[('$sys_item_drop',{'<object=0>':'Ether'}),
        ('$sys_enemy_down',{'<object=0>':english['$en_Formula_SonicSpeedEnd2']+' B'}),
        ('$sys_enemy_down',{'<object=0>':english['$en_Formula_SonicSpeedEnd2']+' A'}),
        ('$sys_get_exp_ap',{'<count=0>':'1072','<count=1>':'12'}),
        ('$sys_get_gil',{'<count=0>':'506'}),
        ('$sys_item_drop_multiple',{'<object=0>':'Mega-Potion','<count>':'3'})]
    encoded=[]
    for key,values in samples:
        text=actual[key]['Text']
        for token,value in values.items():assert token in text;text=text.replace(token,value)
        assert not re.search('<[^>]+>',text)
        encoded.append((key,text,values))
    proof=Image.new('RGB',(2050,1640),'#0a1523');draw=ImageDraw.Draw(proof)
    label=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24)
    draw.text((25,14),'Actual staged glyph proof | Native ASCII substituted after encoding | Not in-game footage',font=label,fill='#b8d2ea')
    reports=[];preview_row=0
    for path in sorted((STAGE/COMMON).glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in path.name:continue
        olddata=(backup/'fonts'/path.name).read_bytes();newdata=path.read_bytes()
        old,ot=v.glyphs(olddata);new,nt=v.glyphs(newdata)
        assert ot==nt and len(old)==len(new)
        o={g[0]:g for g in old};n={g[0]:g for g in new};pages={}
        def mask(g):
            if g[1] not in pages:
                p=path.with_name(path.stem+f'-{g[1]:02d}.uasset')
                if not p.exists():p=W/'source'/COMMON/p.name
                pages[g[1]]=v.atlas(p)[0].getchannel('R')
            return pages[g[1]].crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
        def bottom(g):
            return g[7]+mask(g).point(lambda p:255 if p>=64 else 0).getbbox()[3]
        h=bottom(n[ord('H')]);thai=bottom(n[ord(cmap['ก'])]);assert h==thai
        delta=thai-bottom(o[ord(cmap['ก'])]);allowed={ord(x) for x in cmap.values()}
        for code,g in o.items():
            assert n[code][:7]+n[code][8:]==g[:7]+g[8:],(path.name,code,'Image/spacing changed')
            if code not in allowed:assert n[code]==g,(path.name,code,'Original glyph changed')
        thai_clusters=[k for k in cmap if '\u0e01'<=k[0]<='\u0e5b']
        for cluster in thai_clusters:
            a=ord(cmap[cluster]);assert n[a][7]-o[a][7]==delta,(path.name,cluster)
        assert all(n[ord(cmap[c])][1:]==n[ord(c)][1:] for c in string.ascii_letters)
        digit_overshoot={c:bottom(n[ord(c)])-thai for c in string.digits}
        assert max(map(abs,digit_overshoot.values()))<=2,(path.name,digit_overshoot)
        assert all(bottom(n[ord(cmap[c])])==thai for c in string.digits)
        # Reconstruct the old bytes by restoring only permitted y-offset fields.
        restored=bytearray(newdata);e=v.b.header_end(newdata);start=10 if newdata[e:e+2]==b'\1\11' else 12
        for i,g in enumerate(new):struct.pack_into('<h',restored,e+start+i*18+14,o[g[0]][7])
        assert bytes(restored)==olddata,'Changed something other than glyph vertical origins'
        reports.append(dict(font=path.name,thai_shift_from_previous=delta,native_baseline=h,
            thai_baseline=thai,native_digit_optical_overshoot=digit_overshoot,
            original_glyphs_preserved=True,pixels_and_spacing_unchanged=True,
            all_thai_clusters_shift_together=True,runtime_ascii_and_static_aliases_share_baseline=True))
        if path.stem not in ('U_Com_JP_SystemFontNormal','U_Com_JP_SystemFontSmall','U_Com_JP_SystemFontNormal4K','U_Com_JP_SystemFontSmall4K'):continue
        row=preview_row;preview_row+=1
        for col,(heading,glyphmap) in enumerate((('Before',o),('After',n))):
            x0=25+col*1015;top=65+row*385
            draw.rounded_rectangle((x0,top,x0+985,top+365),radius=12,fill='#142338',outline='#29485f')
            draw.text((x0+18,top+8),heading+' | '+path.stem.replace('U_Com_JP_SystemFont',''),font=label,fill='#93d3ed')
            scale=.62 if '4K' in path.stem else 1.0
            line_height=75 if '4K' in path.stem else 45
            layer=Image.new('RGB',(int(950/scale),line_height*len(encoded)+25),'#142338')
            for i,(key,text,values) in enumerate(encoded):
                pen=0;y=8+i*line_height
                for ch in text:
                    g=glyphmap[ord(ch)]
                    if g[4] and g[5]:layer.paste((238,245,253),(pen+g[6],y+g[7]),mask(g))
                    pen+=g[8]
                assert pen<layer.width,(path.name,key,'Proof overflow')
            if scale!=1:layer=layer.resize((round(layer.width*scale),round(layer.height*scale)),Image.Resampling.LANCZOS)
            proof.paste(layer,(x0+18,top+45))
    assert len(reports)==8 and preview_row==4
    proof.save(QA/'runtime-substitution-proof.png')
    assert fingerprint()==protected_snapshot()
    write('qa/baseline-alignment/audit.json',dict(fonts=reports,only_vertical_origins_changed=True,
        source_and_text_and_textures_unchanged=True,all_previous_translations_preserved=True,
        changed_assets=sorted(fonts),runtime_substitution_samples=[dict(id=k,values=p) for k,t,p in encoded],
        proof_uses_real_glyphs=True,proof_is_game_screenshot=False,runtime_tested=False,installed=False))
    print('Verified native baseline alignment in all 8 fonts; only vertical glyph origins changed')
    print(QA/'runtime-substitution-proof.png')

if __name__=='__main__':main()
