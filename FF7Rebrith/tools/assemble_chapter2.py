"""Assemble the reviewed Chapter 2 working set without touching releases or the game."""
import copy
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

W = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(W / 'tools/cutscene-tool/1.0'))
import txtres

def read(path):
    return json.loads((W / path).read_text(encoding='utf-8'))

def write(path, obj):
    (W / path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    rows = read('reference/chapter2-source.json')
    manifest = read('reference/chapter2-scope.json')
    assert hashlib.sha256((W / 'reference/chapter2-source.json').read_bytes()).hexdigest() == manifest['source_sha256']
    assert hashlib.sha256((W / 'reference/chapter2-shared-source.json').read_bytes()).hexdigest() == manifest['shared_source_sha256']
    rows += read('reference/chapter2-shared-source.json')
    deferred = {r['index'] for r in read('reference/chapter2-deferred.json')}
    translations = {}
    for path in sorted((W / 'translations/chapter2').glob('*.json')):
        values = json.loads(path.read_text(encoding='utf-8'))
        assert not translations.keys() & values.keys(), path
        translations.update(values)
    expected = {str(r['index']) for r in rows if r['index'] not in deferred}
    assert set(translations) == expected, (expected - translations.keys(), translations.keys() - expected)
    assets = {}
    for row in rows:
        if row['index'] in deferred:
            continue
        text = translations[str(row['index'])]
        assert text and not re.search(r'[\u3040-\u30ff\u4e00-\u9fff\ud800-\udfff]', text), row['id']
        assert re.findall(r'</?[^>]+>', text) == re.findall(r'</?[^>]+>', row['Text']), row['id']
        assets.setdefault(row['asset'], dict(entries={}, actors={}))['entries'][row['id']] = text
    global_votes = read('reference/actor-english-evidence.json')
    for asset, patch in assets.items():
        jp = txtres.parse(str(W / 'source' / asset))
        en = txtres.parse(str(W / 'source' / asset.replace('/JP/', '/US/')))
        votes = defaultdict(Counter)
        for key, value in jp.items():
            actor = value.get('MetaData', {}).get('ACTOR')
            english = en.get(key, {}).get('MetaData', {}).get('ACTOR')
            if actor and english:
                votes[actor][english] += 1
        for key in patch['entries']:
            actor = jp[key].get('MetaData', {}).get('ACTOR')
            if not actor:
                continue
            english = en.get(key, {}).get('MetaData', {}).get('ACTOR')
            if not english and votes[actor]:
                english = votes[actor].most_common(1)[0][0]
            if not english and actor in global_votes:
                english = max(global_votes[actor], key=global_votes[actor].get)
            assert english and not re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', english), (asset, key, actor)
            patch['actors'][key] = english
    output = dict(scope=manifest['scope'], translated_records=len(translations), deferred_later_records=len(deferred),
                  source_only=True, assets=assets)
    write('translations/chapter2-th.json', output)
    combined = copy.deepcopy(read('translations/working-th.json'))
    for asset, patch in assets.items():
        dest = combined['assets'].setdefault(asset, dict(entries={}, actors={}))
        for field in ('entries', 'actors'):
            for key, text in patch[field].items():
                assert key not in dest[field] or dest[field][key] == text, (asset, field, key)
                dest[field][key] = text
    combined.update(scope='Chapters 1 and 2 plus existing authorized menus; working assets only', chapter2_records=len(translations), source_only=True)
    write('translations/working-through-chapter2-th.json', combined)
    print(f'Assembled {len(translations)} Chapter 2 records across {len(assets)} assets; {len(deferred)} later-event records deferred')

if __name__ == '__main__':
    main()
