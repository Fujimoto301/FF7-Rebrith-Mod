"""Compare the recheck with the previous delivered Ch8, including all698 glyphs."""
import hashlib,re
from pathlib import Path
from PIL import ImageChops
from prepare_chapter8 import W,read,write,txtres
from assemble_ui_completion import fingerprint
from preview_ch12_recheck import renderer

def main():
    root='qa/chapter8/';b=read(root+'recheck-current.json');before=Path(b['snapshot']);cfg=read('reference/chapter8-build.json')
    prior=read(before/'translations/working-through-chapter8-th.json');now=read(cfg['source']);cm=read(cfg['cluster_map']);rev=str.maketrans({v:k for k,v in cm.items()})
    changes=[];added=[];preserved=0
    for a,p in prior['assets'].items():
        decoded=txtres.parse(str(before/'stage'/a))
        for k,t in p['entries'].items():
            assert k in now['assets'][a]['entries'],(a,k,'old ID lost')
            assert decoded[k]['Text'].translate(rev)==t,(k,'old mapping changed')
            nt=now['assets'][a]['entries'][k]
            if nt!=t:changes.append(dict(asset=a,id=k,before=t,after=nt))
            else:preserved+=1
        assert all(now['assets'][a]['actors'][k]==v for k,v in p['actors'].items()),a
    for a,p in now['assets'].items():
        for k,t in p['entries'].items():
            if k not in prior['assets'].get(a,{}).get('entries',{}):added.append(dict(asset=a,id=k,thai=t))
            assert not re.search(r'([\u0e31\u0e34-\u0e39\u0e47-\u0e4e])\1',t),(k,'duplicate combining mark')
    fonts=[];stage=W/cfg['stage'];old698={k:v for k,v in list(cm.items())[:698]}
    for path in sorted((stage/'End/Content/Menu/Billboard/Common').glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in path.name:continue
        og,om=renderer(before/'stage',path.name);ng,nm=renderer(stage,path.name);changed=0;worst=(0,'')
        for cluster,code in old698.items():
            a=og[ord(code)];b1=ng[ord(code)];assert a[4:]==b1[4:],(path.name,cluster,'metrics')
            x=om(a);y=nm(b1);d=ImageChops.difference(x,y);mean=sum(i*v for i,v in enumerate(d.histogram()))/(x.width*x.height)
            changed+=x.tobytes()!=y.tobytes()
            if mean>worst[0]:worst=(mean,cluster)
        assert worst[0]<4,(path.name,worst)
        fonts.append(dict(font=path.name,previous698_metrics_preserved=True,changed_masks=changed,max_mean_absolute_difference=worst))
    assert len(fonts)==8 and fingerprint()==b['protected']
    write(root+'recheck-review.json',dict(previous_delivered_records=preserved+len(changes),unchanged_records=preserved,corrected_records=len(changes),added_records=len(added),
      combined_records=sum(len(p['entries']) for p in now['assets'].values()),changes=changes,added=added,all_prior_ACTOR_values_preserved=True,
      prior698_mapping_verified_against_entire_previous_staged_text=True,fonts=fonts,source_and_installed_files_unchanged=True,
      source_sha256=hashlib.sha256((W/cfg['source']).read_bytes()).hexdigest(),snapshot=str(before),in_game_tested=False,new_full_video_audio_review=False))
    print('Recheck:',len(added),'added;',len(changes),'corrected;',preserved,'unchanged; all prior698 glyphs checked in8 fonts')

if __name__=='__main__':main()
