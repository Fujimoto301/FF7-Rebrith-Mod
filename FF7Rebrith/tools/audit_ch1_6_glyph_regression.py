"""Distinguish original native glyph preservation from Thai atlas recompression."""
from PIL import ImageChops
from assemble_chapter6 import read,write,W
from preview_ch12_recheck import renderer

def main():
    root='qa/ch1-6-recheck';base=read(root+'/baseline.json');cfg=read('reference/ch1-6-recheck-build.json')
    m=read(base['snapshot']+'/'+base['active']['cluster_map']);stage=W/cfg['stage'];before=W/base['snapshot']/'stage';reports=[]
    for p in sorted((stage/'End/Content/Menu/Billboard/Common').glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in p.name:continue
        og,om=renderer(before,p.name);ng,nm=renderer(stage,p.name);changed=0;worst=(0,'');shape=0
        for cluster,code in m.items():
            a=og[ord(code)];b=ng[ord(code)];assert a[4:]==b[4:],(p.name,cluster,'Metrics regressed')
            x=om(a);y=nm(b);d=ImageChops.difference(x,y)
            mean=sum(i*v for i,v in enumerate(d.histogram()))/(x.width*x.height)
            if x.tobytes()!=y.tobytes():changed+=1
            if mean>worst[0]:worst=(mean,cluster)
            if x.point(lambda z:255 if z>=64 else 0).tobytes()!=y.point(lambda z:255 if z>=64 else 0).tobytes():shape+=1
        # Compression depends on 4x4 block location after repacking. This limit
        # catches a new raster/scale rather than pretending the blocks are identical.
        assert worst[0]<4,(p.name,worst)
        reports.append(dict(font=p.name,all674glyph_metrics_preserved=True,compression_mask_differences=changed,
          threshold64_differences=shape,max_mean_absolute_compression_difference=worst))
    assert len(reports)==8
    write(root+'/old-glyph-regression.json',dict(fonts=reports,
      original_native_glyph_pixels_preserved_by_standard_verifier=True,new_clusters=['พ็','ฟิ้','อึ้'],
      note='Full atlas repacking recompresses Thai glyphs; prior Thai compressed masks differ slightly, while their metrics and original native ASCII/icon glyph pixels remain preserved. No in-game verification.'))
    print('All674 previous glyph metrics preserved in8fonts; Thai BC5 recompression bounded; native glyph preservation checked separately.')

if __name__=='__main__':main()
