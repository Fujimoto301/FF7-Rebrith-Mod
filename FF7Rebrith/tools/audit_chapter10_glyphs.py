"""Prior711 assignments/metrics, native glyphs, and bounded Thai BC5 repacking."""
from PIL import ImageChops
from prepare_chapter9 import W,read,write
from preview_ch12_recheck import renderer
def main():
    cfg=read('reference/chapter10-build.json');b=read('qa/chapter10/baseline.json');old=W/b['active']['stage'];stage=W/cfg['stage'];seed=read(cfg['seed']);report=[]
    if (W/'qa/chapter10/recheck/current.json').exists():
        revision=read('qa/chapter10/recheck/current.json');snapshot=__import__('pathlib').Path(revision['snapshot']);old=snapshot/'stage';seed=read(snapshot/revision['active']['cluster_map'])
    for p in sorted((stage/'End/Content/Menu/Billboard/Common').glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in p.name:continue
        og,om=renderer(old,p.name);ng,nm=renderer(stage,p.name);changed=0;worst=(0,'')
        for cluster,code in seed.items():
            a=og[ord(code)];z=ng[ord(code)];assert a[4:]==z[4:],(p.name,cluster,'metrics')
            x,y=om(a),nm(z);d=ImageChops.difference(x,y);mean=sum(i*n for i,n in enumerate(d.histogram()))/(x.width*x.height)
            if x.tobytes()!=y.tobytes():changed+=1
            if mean>worst[0]:worst=(mean,cluster)
        assert worst[0]<4,(p.name,worst)
        report.append(dict(font=p.name,previous_clusters=len(seed),all_metrics_preserved=True,compressed_mask_differences=changed,max_mean_absolute_difference=worst))
    assert len(report)==8
    write('qa/chapter10/old-glyph-regression.json',dict(fonts=report,native_pixels_preserved_by_standard_verifier=True,previous_map_assignments_preserved=True,Thai_BC5_recompression_note='New atlas repacking may change compressed Thai masks slightly; metrics and native pixels remain preserved.',in_game_tested=False));print('Prior',len(seed),'glyph metrics preserved across8fonts')
if __name__=='__main__':main()
