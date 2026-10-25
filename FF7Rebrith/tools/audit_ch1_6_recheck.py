"""Corpus-wide coverage gate for every completed chapter and added shared family."""
import hashlib,re,unicodedata
from pathlib import Path
from collections import Counter
from assemble_chapter6 import W,read,write,txtres,JP
from assemble_ui_completion import fingerprint
from prepare_ch1_6_recheck import ROOT,R,ui_family,dialogue_decision
from extend_ch1_6_recheck import selected as extra_selected
from audit_ch12_recheck import story_candidate
from prepare_chapter3 import selected as ch3_selected
from prepare_chapter4 import in_scope as ch4_selected
from prepare_chapter5 import in_scope as ch5_selected
from prepare_chapter6 import in_scope as ch6_selected
from audit_chapter6 import number_tokens
import verify_chapter1 as v

def number_review(j,t):
    raw=number_tokens(j);target=re.findall(r'\d+',re.sub('<[^>]+>','',t))
    if raw==target:return None
    normalized=re.sub(r'(?<=\d),(?=\d)','',t)
    if raw==re.findall(r'\d+',re.sub('<[^>]+>','',normalized)):return 'Thousands grouping preserves value'
    if '月' in j and any(x in t for x in ['กันยายน','กรกฎาคม']):return 'JP numeric month expressed as Thai month name; dates reordered day/month/year'
    if '１ｓｔ' in j or '２ｎｄ' in j:return 'SOLDIER class name transliterated เฟิร์สคลาส / เซคันด์คลาส'
    if any(x in j for x in ['零番','弐番','参番','伍番','六番','七世','八番','第二班']):return 'JP kanji location/unit/regnal numbers rendered Arabic'
    if '両手' in j:return 'Both hands rendered as 2 hands'
    if '１９時' in j:return '19 hours expressed as 19:00'
    if 'いちばん' in j and 'อันดับ1' in t:return 'Best-in-world expression rendered rank1'
    if 'ふたり' in j and any(x in t for x in ['ทั้งคู่','ฝาแฝด','ด้วยกัน','พวกเธอ']):return 'Dual-person reference preserved by Thai pair/plural wording'
    if '第七' in j and 'セカンド' in j:return 'Thai reverses order of regiment7 and performance2'
    if any(x in j for x in ['１杯','１枚','１匹','もう１回','１日','ゼロ']):return 'Indefinite request / idiom, no literal measured quantity omitted'
    raise AssertionError(('Unreviewed semantic number mismatch',j,t,raw,target))

def main():
    cfg=read('reference/ch1-6-recheck-build.json');stage=W/cfg['stage'];base=read(ROOT+'/baseline.json');ctx=base['active']
    old=read(base['snapshot']+'/'+ctx['combined_source']);now=read(cfg['source'])
    cmap=read(cfg['cluster_map']);oldmap=read(base['snapshot']+'/'+ctx['cluster_map'])
    assert all(cmap[k]==x for k,x in oldmap.items()) and len(cmap)==677 and len(oldmap)==674
    assert set(cmap)-set(oldmap)=={'พ็','ฟิ้','อึ้'}
    reverse=str.maketrans({y:x for x,y in cmap.items()});corpus=read('reference/rebirth-jp-corpus.json')
    staged={a:txtres.parse(str(stage/a)) for a in now['assets']}
    for a,p in old['assets'].items():
        for field in ('entries','actors'):assert all(now['assets'][a][field][k]==t for k,t in p[field].items()),(a,field)
    ui=read('translations/ch1-6-recheck-ui-th.json');extra=read('translations/ch1-6-recheck-extra-th.json');speech=read('translations/ch1-6-recheck-speech-th.json')
    assert len(ui)==659 and len(extra)==42 and len(speech['entries'])==118
    expected=set(ui)|set(extra)|set(speech['entries'])
    added={(a,k) for a,p in now['assets'].items() for k in p['entries'] if k not in old['assets'][a]['entries']}
    assert added=={(R,k) for k in expected} and len(added)==819
    ui_rows=read('reference/ch1-6-recheck-ui-source.json');extra_rows=read('reference/ch1-6-recheck-extra-source.json')
    assert {r['id'] for r in ui_rows}=={k for k,x in corpus['Resident_TxtRes.uasset'].items() if x['Text'] and ui_family(k)}
    assert {r['id'] for r in extra_rows}=={k for k,x in corpus['Resident_TxtRes.uasset'].items() if x['Text'] and extra_selected(k)}
    reviews=[]
    for rows,patch in [(ui_rows,ui),(extra_rows,extra)]:
        for r in rows:
            k=r['id'];source=corpus['Resident_TxtRes.uasset'][k];assert source==r['Japanese']
            if k not in patch:
                if r['mode']=='unchanged':assert staged[R][k]==source,k
                continue
            t=patch[k];assert t and not JP.search(t),k
            assert staged[R][k]['Text'].translate(reverse)==now['assets'][R]['entries'][k]==t
            assert staged[R][k].get('MetaData',{})==source.get('MetaData',{})
            assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',source['Text']),k
            assert not re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน|กระผม|นะค่ะ',re.sub('<[^>]+>','',t)),k
            if r['mode']=='English_name':assert t==r['English']['Text'],k
            a=re.findall(r'\d+',unicodedata.normalize('NFKC',re.sub('<[^>]+>','',source['Text'])))
            b=re.findall(r'\d+',re.sub('<[^>]+>','',t));reason='Literal numeric values preserved'
            if a!=b:
                if k=='$it_key_minigamecardPack_003_help':
                    assert a==['022','025','028','029','2'] and b==['022','025','028','029']
                    assert 'Hell Rider II' in t;reason='JP VR2 card name is official English Hell Rider II; card IDs022/025/028/029 unchanged'
                elif k.startswith('$minigame_soldierformation_Button_'):
                    kanji={'Long':('六角',['6']),'Rush':('五角',['5']),'Single':('四角',['4'])}
                    x,y=kanji[k.rsplit('_',1)[-1]];assert x in source['Text'] and not a and b==y
                    reason='JP polygon count written in kanji; Thai uses Arabic digits'
                else:assert False,(k,a,b)
            reviews.append(dict(id=k,family=r.get('family','adjoining_activity_or_quest_UI'),jp=source['Text'],thai=t,
              official_English=r['English']['Text'],number_review=reason,source_numbers=a,target_numbers=b,tags_preserved=True))
    speech_rows=read('reference/ch1-6-recheck-speech-source.json');later=read('reference/ch1-6-recheck-deferred.json')
    assert {(r['id'],'include') for r in speech_rows}|{(r['id'],r['reason']) for r in later}=={(k,dialogue_decision(k)[0]) for k,x in corpus['Resident_TxtRes.uasset'].items() if x['Text'] and dialogue_decision(k)}
    speech_review=[]
    for r in speech_rows:
        k=r['id'];source=corpus['Resident_TxtRes.uasset'][k];t=speech['entries'][k]
        assert source['Text']==r['Text'] and source.get('MetaData',{})==r['MetaData']
        assert staged[R][k]['Text'].translate(reverse)==t and not JP.search(t)
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',source['Text'])
        if not k.endswith('_sys'):assert not re.search('[A-Za-z]{2,}',t),k
        assert not re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ผม|ดิฉัน|กระผม',t),k
        a=re.findall(r'\d+',unicodedata.normalize('NFKC',source['Text']));b=re.findall(r'\d+',t)
        assert a==b,(k,a,b)
        if r['MetaData'].get('ACTOR'):assert speech['actors'][k]==r['English']['MetaData']['ACTOR']
        speech_review.append(dict(id=k,chapter=r['chapter'],jp=source['Text'],thai=t,actor=speech['actors'].get(k,''),
          gender='Neutral phrasing; no gender-specific endings or ผม added; unknown audience NPCs not inferred from code',
          proper_names='JP narration uses โฟกัส/ปิอาโซลา, English label Snaps/Dorian per same-ID US',tags_and_numbers_preserved=True))
    for r in later:assert staged[R][r['id']]==corpus['Resident_TxtRes.uasset'][r['id']],r['id']
    # Every previous chapter source, including actorless NPCs, is paired again with actual staged text.
    chapter_reviews=[];counts={};deferred_reviews=[];number_reviews=[]
    deferred={}
    for ch in [2,4,6]:
        for r in read(f'reference/chapter{ch}-deferred.json'):deferred[r['id']]=r
    source_sets={}
    for ch in range(1,7):
        rows=read(f'reference/chapter{ch}-source.json')
        if ch==2:rows+=read('reference/chapter2-shared-source.json')
        source_sets[ch]={(Path(r['asset']).name,r['id']) for r in rows}
        counter=Counter()
        for r in rows:
            a=r['asset'];k=r['id'];source=corpus[Path(a).name][k]
            assert source['Text']==r['Text'] and source.get('MetaData',{})==r.get('MetaData',{})
            if k in deferred:
                assert k not in now['assets'][a]['entries'] and staged[a][k]==source
                counter['deferred']+=1;deferred_reviews.append(dict(chapter=ch,id=k,reason=deferred[k]['reason']));continue
            assert k in now['assets'][a]['entries'],(ch,a,k)
            t=now['assets'][a]['entries'][k];assert t.strip() and not JP.search(t)
            assert staged[a][k]['Text'].translate(reverse)==t
            assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',source['Text'])
            sm=source.get('MetaData',{});dm=staged[a][k].get('MetaData',{})
            if sm.get('ACTOR'):
                assert now['assets'][a]['actors'][k]==dm['ACTOR'] and not JP.search(dm['ACTOR']),k
            assert {x:y for x,y in sm.items() if x!='ACTOR'}=={x:y for x,y in dm.items() if x!='ACTOR'}
            reason=number_review(source['Text'],t)
            if reason:number_reviews.append(dict(chapter=ch,id=k,jp=source['Text'],thai=t,reason=reason))
            assert not re.search('นะค่ะ|ไหมค่ะ|เหรอค่ะ|หรือเปล่าค่ะ|เซคเตอร์เจ็ด',t),k
            counter['translated']+=1
            if '_NPC_' in k:
                counter['NPC']+=1
                if not sm.get('ACTOR'):counter['NPC_without_ACTOR']+=1
            if k.endswith('_sys'):counter['system_choices']+=1
            chapter_reviews.append(dict(chapter=ch,asset=a,id=k,jp=source['Text'],thai=t,actor=dm.get('ACTOR',''),
              actorless=not sm.get('ACTOR'),source_staged_tags_metadata_verified=True,
              prior_editorial_and_gender_evidence_retained=True))
        counts[str(ch)]=dict(counter)
    assert [counts[str(c)]['translated'] for c in range(1,7)]==[1157,2876,253,3206,1316,1698]
    # Independent entire-corpus scan does not rely only on the old frozen source lists.
    corpus_scan=[]
    for a,d in corpus.items():
        for k,x in d.items():
            if not x['Text']:continue
            chapters=[]
            if story_candidate(k):chapters.append('1–2')
            if ch3_selected(k):chapters.append('3')
            if ch4_selected(a,k):chapters.append('4')
            if ch5_selected(a,k):chapters.append('5')
            if ch6_selected(a,k):chapters.append('6')
            if not chapters:continue
            asset='End/Content/Text/JP/'+a
            present=k in now['assets'].get(asset,{}).get('entries',{})
            assert present or k in deferred,(a,k,'Unexplained chapter gap')
            corpus_scan.append(dict(asset=asset,id=k,chapters=chapters,decision='translated' if present else 'deferred',reason=deferred.get(k,{}).get('reason','')))
    for r in read('reference/chapter3-deferred.json'):assert r['id'] in now['assets'][r['asset']]['entries'],'Post-mine Ch.4 follow-up missing'
    # Prior NPC/gender corrections are required, not recomputed from model-name codes.
    prior_gender=read('qa/gender-through-chapter6/records.json')['records']
    for r in prior_gender:assert now['assets'][r['asset']]['entries'][r['id']]==r['thai']
    # Native ASCII/Thai and digit alignment, including the intentional low ellipsis.
    fonts=[];common=Path('End/Content/Menu/Billboard/Common')
    for p in sorted((stage/common).glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in p.name:continue
        gs={g[0]:g for g in v.glyphs(p.read_bytes())[0]};pages={}
        def bottom(code):
            g=gs[code]
            if g[1] not in pages:
                path=p.with_name(p.stem+f'-{g[1]:02d}.uasset')
                if not path.exists():path=W/'source'/common/path.name
                pages[g[1]]=v.atlas(path)[0].getchannel('R')
            box=pages[g[1]].crop((g[2],g[3],g[2]+g[4],g[3]+g[5])).point(lambda z:255 if z>=64 else 0).getbbox()
            return g[7]+box[3]
        h=bottom(ord('H'));assert h==bottom(ord(cmap['ก']))
        assert all(bottom(ord(cmap[c]))==h for c in '0123456789')
        assert bottom(8230)==bottom(ord('.'))
        fonts.append(dict(font=p.name,ellipsis_period_baseline=bottom(8230),thai_native_H_baseline=h,original_ASCII_preserved=True))
    assert len(fonts)==8
    assert fingerprint()==base['protected']
    for rel,sha in base['source_hashes'].items():assert hashlib.sha256((W/rel).read_bytes()).hexdigest()==sha,rel
    manifest={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(stage.rglob('*.uasset'))}
    previous=read(base['snapshot']+'/'+ctx['manifest']);assert set(manifest)==set(previous) and len(manifest)==24
    changed=[p for p in manifest if manifest[p]!=previous[p]]
    assert set(changed)<={str(Path(R))}|{a for a in previous if 'Billboard' in a}
    total=sum(len(p['entries']) for p in now['assets'].values());assert total==24999
    write(ROOT+'/working-assets.json',manifest);write(ROOT+'/ui-review.json',reviews)
    write(ROOT+'/shared-dialogue-review.json',speech_review);write(ROOT+'/chapter-records.json',chapter_reviews)
    write(ROOT+'/corpus-scope-scan.json',corpus_scan);write(ROOT+'/number-review.json',number_reviews)
    write(ROOT+'/existing-deferred-review.json',deferred_reviews)
    write(ROOT+'/translation-audit.json',dict(total_combined_text_records=total,working_assets=24,
      previous_records_preserved=24180,new_UI_records=701,new_shared_dialogue_records=118,
      chapter_source_records_rechecked=len(chapter_reviews),per_chapter=counts,
      shared_UI_inventory_records=len(ui_rows)+len(extra_rows),independent_corpus_candidates=len(corpus_scan),
      old_deferred_records=len(deferred_reviews),new_shared_dialogue_later_states=len(later),
      semantic_number_reviews=len(number_reviews),missing=[],japanese_remaining_in_selected_scope=[],tag_mismatches=[],
      old_actor_metadata_preserved=True,old_glyph_assignments_preserved=True,new_clusters=['พ็','ฟิ้','อึ้'],glyph_clusters=677,
      fonts=fonts,changed_assets=changed,source_and_installed_files_unchanged=True,
      in_game_tested=False,video_audio_reviewed_anew=False,
      scope_limit='All completed chapter frozen scopes plus independent chapter-ID corpus coverage and registered adjoining shared UI/NPC families. Later story states remain separately reasoned, and actual game trigger/wrapping verification remains outstanding.'))
    active=dict(ctx);active.update(stage=cfg['stage'],manifest=ROOT+'/working-assets.json',audit=ROOT+'/translation-audit.json',
      combined_source=cfg['source'],cluster_map=cfg['cluster_map'],asset_count=24,
      shared_file_note='All5 ZIPs required; all1–6 chapters rechecked. Resident/title/fonts shared in Common; scene ZIPs unchanged in this revision.')
    write('qa/active-working-set.json',active)
    print('All chapter audit passed:',len(chapter_reviews),'prior chapter records;',len(corpus_scan),'corpus candidates; +701UI/+118shared dialogue; total',total)

if __name__=='__main__':main()
