"""Compare all698 existing glyphs with corrected Ch8; never alter old metrics."""
from PIL import ImageChops
from prepare_chapter9 import W,read,write
from preview_ch12_recheck import renderer

def main():
    cfg=read('reference/chapter9-build.json');cm=read(cfg['cluster_map']);seed=read(cfg['seed']);stage=W/cfg['stage'];old=W/'staging/ThaiJP_ThroughChapter8_Working';reports=[]
    for p in sorted((stage/'End/Content/Menu/Billboard/Common').glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in p.name:continue
        og,om=renderer(old,p.name);ng,nm=renderer(stage,p.name);changed=0;worst=(0,'')
        for k,code in seed.items():
            assert cm[k]==code;g=og[ord(code)];n=ng[ord(code)];assert g[4:]==n[4:],(p.name,k,'old metrics')
            x=om(g);y=nm(n);diff=ImageChops.difference(x,y);mean=sum(i*v for i,v in enumerate(diff.histogram()))/(x.width*x.height)
            changed+=x.tobytes()!=y.tobytes()
            if mean>worst[0]:worst=(mean,k)
        assert worst[0]<4,(p.name,worst)
        reports.append(dict(font=p.name,all698_metrics_preserved=True,compression_mask_differences=changed,max_mean_absolute_compression_difference=worst))
    assert len(reports)==8
    write('qa/chapter9/old-glyph-regression.json',dict(fonts=reports,new_clusters=[k for k in cm if k not in seed],native_pixels_verified_separately=True,note='No raster/size change. Repacking into safe spare space may change Thai BC5 masks slightly; old native ASCII/digits/icons checked pixelwise by standard verifier. Not in-game.'))
    print('All698 glyph assignments/metrics preserved in8fonts; BC5 differences bounded')

if __name__=='__main__':main()
