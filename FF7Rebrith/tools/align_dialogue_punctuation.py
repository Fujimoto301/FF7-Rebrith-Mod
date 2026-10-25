"""Lower U+2026 to the native full-stop ink baseline; preserve original pixels."""
import struct,hashlib
from pathlib import Path
import verify_chapter1 as v
from assemble_chapter6 import W,read,write

COMMON=Path('End/Content/Menu/Billboard/Common')
def expected_glyph(g,period,mask):
    def bottom(x):
        box=mask(x).point(lambda p:255 if p>=64 else 0).getbbox();assert box
        return x[7]+box[3]
    result=list(g);result[7]+=bottom(period)-bottom(g)
    return tuple(result)

def apply(stage,policy_path,report_path):
    policy=read(policy_path);reports=[]
    assert policy['codepoints']==[8230],'Only the specifically requested ellipsis is authorized'
    for path in sorted((stage/COMMON).glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in path.name:continue
        data=path.read_bytes();records,tail=v.glyphs(data);gs={g[0]:g for g in records};pages={}
        def mask(g):
            if g[1] not in pages:
                p=path.with_name(path.stem+f'-{g[1]:02d}.uasset')
                if not p.exists():p=W/'source'/COMMON/p.name
                pages[g[1]]=v.atlas(p)[0].getchannel('R')
            return pages[g[1]].crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
        old=gs[8230];new=expected_glyph(old,gs[ord('.')],mask)
        assert old[:7]+old[8:]==new[:7]+new[8:]
        patched=bytearray(data);e=v.b.header_end(data);start=10 if data[e:e+2]==b'\1\11' else 12
        index=next(i for i,g in enumerate(records) if g[0]==8230)
        struct.pack_into('<h',patched,e+start+index*18+14,new[7])
        restored=bytearray(patched);struct.pack_into('<h',restored,e+start+index*18+14,old[7])
        assert restored==data,'Only one y-origin field may change'
        if patched!=data:path.write_bytes(patched)
        reports.append(dict(font=path.name,codepoint='U+2026',old_y=old[7],new_y=new[7],shift=new[7]-old[7],
          original_pixels_spacing_and_other_glyphs_preserved=True,sha256=hashlib.sha256(patched).hexdigest()))
    assert len(reports)==8
    write(report_path,dict(policy=policy,fonts=reports,in_game_tested=False))
    return reports
