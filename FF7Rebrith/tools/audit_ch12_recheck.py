"""Whole-family/shared-entry coverage, Ch.1–2 source audit and ellipsis regression."""
import hashlib,re,struct,unicodedata
from collections import Counter
from pathlib import Path
from assemble_chapter6 import W,read,write,JP,txtres
from assemble_ui_completion import fingerprint
from prepare_ch12_recheck import ROOT,R,family
import verify_chapter1 as v

def story_candidate(k):
    if k.startswith(('$C1910_','$NIBLT_NPC_10_','$NIBLM_BOS_00_','$C1920_','$C2010_',
      '$KALMT_NPC_10_','$KALMT_NPC_20_','$GRASA_NPC_10_','$SWAMP_BOS_01_','$CHADL_QST_01_')):return True
    if k.startswith(tuple('$GRASE_QST_%02d_'%n for n in range(1,6))):
        return not (k.startswith('$GRASE_QST_05_') and int(k.split('_')[3])>=1200)
    return False

def main():
    cfg=read('reference/ch12-recheck-build.json');stage=W/cfg['stage'];base=read(ROOT+'/baseline.json')
    old=read(base['snapshot']+'/translations/working-through-chapter6-th.json')
    now=read(cfg['source']);cmap=read(cfg['cluster_map']);oldmap=read(base['snapshot']+'/reference/through-chapter6-cluster-map.json')
    assert cmap==oldmap and len(cmap)==674
    reverse=str.maketrans({y:x for x,y in cmap.items()});corpus=read('reference/rebirth-jp-corpus.json')
    rows=read('reference/ch12-recheck-ui-source.json');patch=read('translations/ch12-recheck-ui-th.json')
    recap=read('translations/ch1-opening-recap-th.json');T='End/Content/Text/JP/0005-TITLB_TxtRes.uasset'
    assert len(patch)==330 and len(recap)==39 and len(rows)==362
    assert {r['id'] for r in rows}=={k for k,x in corpus['Resident_TxtRes.uasset'].items() if family(k) and x['Text']}
    assert {r['id'] for r in rows if r['mode'] in ('translate','english_name')}==set(patch)
    staged={a:txtres.parse(str(stage/a)) for a in now['assets']}
    for a,p in old['assets'].items():
        for field in ('entries','actors'):assert all(now['assets'][a][field][k]==t for k,t in p[field].items()),(a,field)
    added={(a,k) for a,p in now['assets'].items() for k in p['entries'] if k not in old['assets'].get(a,{}).get('entries',{})}
    assert added=={(R,k) for k in patch}|{(T,k) for k in recap}
    review=[]
    for r in rows:
        k=r['id'];j=corpus['Resident_TxtRes.uasset'][k];assert j==r['Japanese']
        if r['mode']=='unchanged':assert staged[R][k]==j;continue
        if r['mode']=='existing':continue
        t=patch[k];assert staged[R][k]['Text'].translate(reverse)==t and not JP.search(t),k
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',j['Text']),k
        assert staged[R][k].get('MetaData',{})==j.get('MetaData',{}),k
        assert not re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน|กระผม|นะค่ะ',re.sub('<[^>]+>','',t)),k
        a=unicodedata.normalize('NFKC',re.sub('<[^>]+>','',j['Text'])).replace('ゼロ','0')
        b=re.sub('<[^>]+>','',t)
        if r['mode']=='english_name':assert t==r['English']['Text']
        else:assert re.findall(r'\d+',a)==re.findall(r'\d+',b),(k,a,b)
        review.append(dict(id=k,family=r['family'],jp=j['Text'],thai=t,official_English=r['English']['Text'],
          tags_verified=True,numbers_verified=True,neutral_gender=True))
    # Same source values, metadata and English names in the optional opening recap.
    recap_review=[]
    for r in read('reference/ch1-opening-recap-source.json'):
        k=r['id'];j=corpus['0005-TITLB_TxtRes.uasset'][k];t=recap[k]
        assert j==r['Japanese'] and staged[T][k]['Text'].translate(reverse)==t
        assert staged[T][k].get('MetaData',{})==j.get('MetaData',{})
        assert not JP.search(t) and not re.search(r'[A-Za-z]{2,}|ครับ|ค่ะ|คะ(?=[!?…\s]|$)',t),k
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',j['Text'])
        original=j['Text'].replace('壱番','1番').replace('伍番','5番').replace('八番','8番').replace('七番','7番')
        assert re.findall(r'\d+',original)==re.findall(r'\d+',t),(k,original,t)
        recap_review.append(dict(id=k,jp=j['Text'],thai=t,narrator='Red XIII; named in opening recap context',
          gender_policy='ฉัน / พวกเรา; no gendered sentence endings',proper_names='Thai inside narration'))
    # Recheck every previously inventoried Ch.1–2 record, then independently scan the corpus.
    previous_rows=[]
    for name in ('chapter1-source.json','chapter2-source.json','chapter2-shared-source.json'):
        previous_rows+=read('reference/'+name)
    deferred={r['id']:r['reason'] for r in read('reference/chapter2-deferred.json')}
    checked=[];later=[]
    for r in previous_rows:
        a=r['asset'];k=r['id'];source=corpus[Path(a).name][k]
        assert source['Text']==r['Text']
        if k in deferred:
            assert staged[a][k]==source,(a,k)
            later.append(dict(asset=a,id=k,jp=source['Text'],reason=deferred[k]));continue
        assert k in now['assets'][a]['entries'],(a,k)
        assert not JP.search(now['assets'][a]['entries'][k]),(a,k)
        checked.append(dict(asset=a,id=k,source=r['Text'],thai=now['assets'][a]['entries'][k],
          group='system_choice' if k.endswith('_sys') else 'dialogue_or_ambient'))
    scope_rows=[]
    for a,d in corpus.items():
        for k,x in d.items():
            if not x['Text'] or not story_candidate(k):continue
            asset='End/Content/Text/JP/'+a
            if k in deferred:decision='deferred_later_state'
            else:
                assert k in now['assets'].get(asset,{}).get('entries',{}),(a,k,'Unexpected chapter gap')
                decision='translated'
            scope_rows.append(dict(asset=asset,id=k,decision=decision,reason=deferred.get(k,'')))
    # Old glyph bytes can be reconstructed by restoring only ellipsis y, in all 8 fonts.
    fonts=[];common=Path('End/Content/Menu/Billboard/Common')
    for p in sorted((stage/common).glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in p.name:continue
        olddata=(W/base['snapshot']/'stage'/common/p.name).read_bytes();newdata=p.read_bytes()
        oldgs,ot=v.glyphs(olddata);newgs,nt=v.glyphs(newdata)
        assert len(oldgs)==len(newgs) and ot==nt
        for og,ng in zip(oldgs,newgs):
            if og[0]!=8230:assert og==ng,(p.name,og[0])
            else:assert og[:7]+og[8:]==ng[:7]+ng[8:] and ng[7]>og[7],p.name
        restored=bytearray(newdata);e=v.b.header_end(newdata);start=10 if newdata[e:e+2]==b'\1\11' else 12
        i=next(i for i,g in enumerate(oldgs) if g[0]==8230)
        struct.pack_into('<h',restored,e+start+i*18+14,oldgs[i][7]);assert bytes(restored)==olddata
        fonts.append(dict(font=p.name,only_ellipsis_y_changed=True,shift=newgs[i][7]-oldgs[i][7]))
    assert len(fonts)==8
    manifest={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*.uasset'))}
    prior=read(base['snapshot']+'/'+base['active']['manifest'])
    changed=[a for a in manifest if manifest[a]!=prior.get(a)]
    expected={str(Path(R)),str(Path(T))}|{str(common/f['font']) for f in fonts}
    assert set(changed)==expected and len(manifest)==24,(changed,len(manifest))
    assert fingerprint()==base['protected']
    for rel,sha in base['source_hashes'].items():assert hashlib.sha256((W/rel).read_bytes()).hexdigest()==sha,rel
    assert len(read(ROOT+'/verification.json')['fonts'])==8
    total=sum(len(p['entries']) for p in now['assets'].values());assert total==24180
    write(ROOT+'/working-assets.json',manifest)
    write(ROOT+'/ui-review.json',review);write(ROOT+'/opening-recap-review.json',recap_review)
    write(ROOT+'/chapter1-2-records.json',checked);write(ROOT+'/deferred-later-states.json',later)
    write(ROOT+'/corpus-scope-inventory.json',scope_rows)
    gender=read('qa/gender-through-chapter6/summary.json');assert gender['actual_particle_occurrences']==477 and not gender['gender_mismatches']
    write(ROOT+'/translation-audit.json',dict(total_combined_text_records=total,working_assets=24,
      new_UI_records=330,new_opening_recap_records=39,UI_inventory_records=len(rows),
      original_chapter1_2_source_records=len(previous_rows),reviewed_original_chapter1_2_records=len(checked),
      deferred_later_records=len(later),independent_corpus_candidate_records=len(scope_rows),
      selected_chapter_corpus_missing=[],shared_UI_family_missing=[],japanese_remaining_in_scope=[],
      original_23811_texts_and_all_ACTORs_preserved=True,glyph_map_unchanged=True,ellipsis_fonts=fonts,
      changed_assets=changed,actual_gender_particles=477,gender_mismatches=[],
      source_and_installed_files_unchanged=True,installed=False,runtime_tested=False,video_audio_verified=False,
      audit_limit='Source and staged-file coverage; does not establish all gameplay triggers or actual on-screen wrapping.',
      ongoing_policy='For every chapter, audit shared tutorial prompts, yes/no and retry dialogs, activity menus/HUD and written instructions together with scene dialogue; check punctuation against original period baseline.'))
    active=dict(base['active']);active.update(stage=cfg['stage'],manifest=ROOT+'/working-assets.json',audit=ROOT+'/translation-audit.json',
      asset_count=24,combined_source=cfg['source'],cluster_map=cfg['cluster_map'],
      shared_file_note='All five ZIPs required. Chapter scene assets unchanged; Common contains Resident, opening title recap, 8 fonts and 8 textures. Ch.1–2 recheck retains Chapters1–6.')
    write('qa/active-working-set.json',active)
    print('Passed:',len(checked),'Ch.1–2 original records;',len(later),'later-state deferrals;',len(scope_rows),'independent corpus candidates; +330 UI/+39 recap; 8 ellipsis fonts; total',total)

if __name__=='__main__':main()
