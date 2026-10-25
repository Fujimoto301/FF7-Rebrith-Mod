"""Audit coverage against extracted assets and review gender-sensitive lines."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
import assemble_chapter2 as a

W = a.W
def main():
    rows = a.read('reference/chapter2-source.json') + a.read('reference/chapter2-shared-source.json')
    deferred = {r['index'] for r in a.read('reference/chapter2-deferred.json')}
    compiled = a.read('translations/chapter2-th.json')
    values = {}
    for p in sorted((W / 'translations/chapter2').glob('*.json')):
        batch = json.loads(p.read_text(encoding='utf-8'))
        assert not batch.keys() & values.keys(), p
        values.update(batch)
    assert set(values) == {str(r['index']) for r in rows if r['index'] not in deferred}
    original = {p:a.txtres.parse(str(W / 'source' / p)) for p in {r['asset'] for r in rows}}
    gender = []
    female = {'ティファ', 'クリン', 'ネネ'}
    male = {'チャドリー', 'グリングリン'}
    gender_rx = re.compile(r'ครับ|ค่ะ|คะ(?=[!?…\s]|$)|ผม|ดิฉัน|กระผม')
    evidence = {
        'チャドリー': {'gender':'male','basis':'Named ACTOR Chadley; official Square Enix profile uses he/his', 'url':'https://www.square-enix.com/ffvii/en-us/games/rebirth/characters/chadley/'},
        'グリングリン': {'gender':'male','basis':'Billy explicitly called お兄ちゃん by Chloe in this source; exact US ACTOR Billy'},
        'クリン': {'gender':'female','basis':'Chloe explicitly called 妹 by Billy; source indices422,1042-1044'},
        'ティファ': {'gender':'female','basis':'Tifa named actor; existing Chapter1 visual identity evidence and お嬢さんたち addressing Tifa/Aerith indices310-311'},
        'ネネ': {'gender':'female','basis':'Nene explicitly introduced as お嬢ちゃん in adjacent source indices2483,2491-2492'},
    }
    named_english = re.compile(r'\b(?:Cloud|Barret|Tifa|Aerith|Chadley|Broden|Billy|Chloe|Sephiroth)\b')
    for row in rows:
        item = original[row['asset']][row['id']]
        assert item['Text'] == row['Text'] and item.get('MetaData', {}) == row['MetaData'], row['id']
        if row['index'] in deferred:
            assert row['id'] not in compiled['assets'].get(row['asset'], {}).get('entries', {})
            continue
        text = values[str(row['index'])]
        assert compiled['assets'][row['asset']]['entries'][row['id']] == text
        assert not re.search(r'[\u3040-\u30ff\u4e00-\u9fff\ud800-\udfff\uff10-\uff19]', text), row['id']
        assert re.findall(r'</?[^>]+>', text) == re.findall(r'</?[^>]+>', row['Text']), row['id']
        assert not named_english.search(text), row['id']
        assert not re.search(r'(?:เซคเตอร์|หมายเลข|อันดับ|อายุ)(?:หนึ่ง|สอง|สาม|สี่|ห้า|หก|เจ็ด|แปด|เก้า)', text)
        actor = row['MetaData'].get('ACTOR')
        if actor in male:
            assert not re.search(r'ค่ะ|คะ(?=[!?…\s]|$)|ดิฉัน', text), row['id']
        if actor in female:
            assert not re.search(r'ครับ|กระผม|ผม', text), row['id']
        if gender_rx.search(text):
            if row['index'] in (1800, 2123):
                basis = {'gender':'not_gendered','basis':'ผม means hair in this sentence'}
            elif row['index'] in (506, 2421):
                basis = {'gender':'male','basis':'System question repeats adjacent voiced Chadley line, indices505/2419'}
            elif row['index'] in (1801, 1807):
                basis = {'gender':'male','basis':'Same two-speaker conversation explicitly calls itself the two-member モテない男同盟, indices1800-1808; not inferred from mma suffix'}
            else:
                assert actor in evidence, (row['index'], actor, text)
                basis = evidence[actor]
            gender.append(dict(index=row['index'], id=row['id'], actor=actor, text=text, evidence=basis))
    install = a.read('qa/menu/installation.json')
    protected = []
    for f in install['files']:
        for path in [Path(f['path']), W / 'dist/ThaiJP_Chapter1_P' / f['file']]:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            assert digest.upper() == f['sha256'].upper(), path
            protected.append(dict(path=str(path),sha256=digest,unchanged_from_installed_trial=True))
    a.write('qa/chapter2/gender-review.json', dict(policy='Only needed particles. Neutral phrasing for unidentified NPCs; no inference from mma/mfa alone. Video/audio was not reviewed anew in this pass.', speaker_evidence=evidence, records=gender))
    counts = Counter('_'.join(r['id'].split('_')[:3]) for r in rows if r['index'] not in deferred)
    report = dict(translated_records=len(values),source_inventory_records=len(rows),deferred_later_event_records=len(deferred),
                  missing_records=0,duplicate_indices=0,japanese_text_remaining=0,tag_mismatches=0,
                  source_records_verified_against_extracted_assets=True,english_character_names_inside_dialogue=0,
                  reviewed_gender_sensitive_records=sum(r['evidence']['gender']!='not_gendered' for r in gender),
                  gender_mismatches=0,per_prefix=dict(counts),protected_trial_files=protected,
                  runtime_tested=False,video_audio_verified=False)
    a.write('qa/chapter2/translation-audit.json', report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('protected_trial_files','per_prefix')},ensure_ascii=False))

if __name__ == '__main__':
    main()
