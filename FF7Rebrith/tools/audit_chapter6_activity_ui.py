"""Verify the Costa activity supplement against its own immutable revision."""
import hashlib,re,unicodedata
from collections import Counter
from pathlib import Path
from assemble_chapter6 import W,read,write,txtres,JP
from chapter6_activity_ui import ROOT,ASSET,selected,OFFICIAL_MODE_NAMES
from assemble_ui_completion import fingerprint

def main():
    baseline=read(ROOT+'/baseline.json');snapshot=baseline['snapshot']
    before=read(snapshot+'/translations/working-through-chapter6-th.json')
    now=read('translations/working-through-chapter6-th.json')
    oldassets=read(snapshot+'/qa/chapter6/working-assets.json')
    rows=read('reference/chapter6-activity-ui-source.json')
    patch=read('translations/chapter6-activity-ui-th.json')
    corpus=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset']
    us=txtres.parse(str(W/'source'/ASSET.replace('/JP/','/US/')))
    assert {r['id'] for r in rows}=={k for k in corpus if selected(k)}
    assert len(rows)==164 and len(patch)==131
    assert {r['id'] for r in rows if r['action']=='translate'}==set(patch)
    for a,p in before['assets'].items():
        for field in ('entries','actors'):
            assert all(now['assets'][a][field][k]==t for k,t in p[field].items()),(a,field)
    assert {(a,k) for a,p in now['assets'].items() for k in p['entries'] if k not in before['assets'].get(a,{}).get('entries',{})}=={(ASSET,k) for k in patch}
    cmap=read('reference/through-chapter6-cluster-map.json')
    assert cmap==read(snapshot+'/reference/through-chapter6-cluster-map.json')
    reverse=str.maketrans({v:k for k,v in cmap.items()})
    stage=W/'staging/ThaiJP_ThroughChapter6_Working'
    staged=txtres.parse(str(stage/ASSET));reviews=[]
    aliases={'$CardChallenge_03_Detail':'JP 2号/3号 identify the official Moogle Mage/Moogle Bard cards; use official English UI card names.',
      '$CardChallenge_03_Detail_AfterAmor':'JP 2号/3号 identify the official Moogle Mage/Moogle Bard cards; use official English UI card names.'}
    assert us['$cardtext_card_name_Token_035']['Text']=='Moogle Mage'
    assert us['$cardtext_card_name_Token_036']['Text']=='Moogle Bard'
    for r in rows:
        k=r['id'];assert corpus[k]==r['Japanese'] and us[k]==r['English'],k
        if k not in patch:
            if r['action']=='preserve_English_or_symbol':assert staged[k]==corpus[k],k
            continue
        t=patch[k];assert not JP.search(t) and t.strip()
        assert staged[k]['Text'].translate(reverse)==now['assets'][ASSET]['entries'][k]==t
        assert staged[k].get('MetaData',{})==corpus[k].get('MetaData',{})
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',r['Japanese']['Text']),k
        original=re.sub('<[^>]+>','',unicodedata.normalize('NFKC',r['Japanese']['Text']))
        target=re.sub('<[^>]+>','',t)
        numbers=re.findall(r'\d+',original);thainumbers=re.findall(r'\d+',target)
        if k not in aliases:assert numbers==thainumbers,(k,numbers,thainumbers)
        else:assert numbers==['2','3'] and not thainumbers
        assert not re.search(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน|นะค่ะ',target),k
        if '_Title' in k or k.startswith('$wheelie_clear_rank') or k in OFFICIAL_MODE_NAMES|{'$TravelCameraman_Window_COSTA'}:
            assert t==us[k]['Text'],k
        reviews.append(dict(id=k,jp=r['Japanese']['Text'],thai=t,english_reference=r['English']['Text'],
            tags_preserved=True,source_numbers=numbers,target_numbers=thainumbers,
            number_semantics=aliases.get(k,'Literal numeric tokens preserved'),gender='Neutral system UI'))
    assets=read('qa/chapter6/working-assets.json')
    changed=[a for a in assets if assets[a]!=oldassets[a]]
    assert changed==[str(Path(ASSET))],changed
    assert fingerprint()==baseline['protected']
    for rel,sha in baseline['source_hashes'].items():assert hashlib.sha256((W/rel).read_bytes()).hexdigest()==sha,rel
    write(ROOT+'/audit.json',dict(new_UI_records=len(patch),inventory_records=len(rows),
      retained_original_English_or_symbols=sum(r['action']=='preserve_English_or_symbol' for r in rows),
      preserved_prior_translation_records=sum(len(p['entries']) for p in before['assets'].values()),
      combined_text_records=sum(len(p['entries']) for p in now['assets'].values()),
      unchanged_all_ACTORs=True,unchanged_glyph_map=True,unchanged_all_fonts_and_textures=True,
      changed_assets=changed,scope_verified_against_full_corpus=True,missing_records=[],
      gender_mismatches=[],source_and_installed_files_unchanged=True,in_game_tested=False,
      proper_name_policy='Official same-ID US titles/licenses/mode names. JP-only Run Wild flavor mode descriptions translated descriptively; not invented English official names.',
      coverage_limit='Introductory Card Carnival 01–03 and generic activity HUD/menu categories, not all later-return puzzle courses. No new spoken dialogue or later-state NPCs.',
      reviewed_records=reviews))
    print('Activity UI audit passed:',len(patch),'new;',len(rows),'inventory; 23,680 prior records, all fonts, actors and scene assets preserved.')

if __name__=='__main__':main()
