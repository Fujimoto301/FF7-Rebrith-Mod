"""Compile the reviewed whole-category UI expansion, without distributing it."""
import collections, copy, hashlib, json, re
from pathlib import Path
from create_ui_completion_scope import W, R, read, write

PROTECTED = [W/'dist', Path(r'E:\steam\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks\~mods')]

def fingerprint():
    return {str(p):hashlib.sha256(p.read_bytes()).hexdigest()
            for root in PROTECTED if root.exists() for p in sorted(root.rglob('*')) if p.is_file()}

def tags(t):return sorted(re.findall(r'<[^>]+>',t))

def protected_snapshot():
    active=W/'qa/ui-completion/active-revision.json'
    if active.exists():return read(json.loads(active.read_text('utf-8'))['protected_manifest'])
    return read('qa/ui-completion/protected-files-before.json')

def main():
    manifest=W/'qa/ui-completion/protected-files-before.json'
    if not manifest.exists():write('qa/ui-completion/protected-files-before.json',fingerprint())
    assert fingerprint()==protected_snapshot(),'Distribution or installed files changed during this revision'
    rows=read('reference/ui-completion-source.json');templates=read('reference/ui-completion-templates.json')
    scope=read('reference/ui-completion-scope.json');base=read('translations/working-inventory-th.json')
    original=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset']
    translated={}
    for p in sorted((W/'translations/ui-completion').glob('batch-*.json')):
        for n,t in json.loads(p.read_text('utf-8')).items():
            assert n not in translated,('Duplicate template',n)
            translated[n]=t
    needed={str(r['template']) for r in rows if r['mode']=='manual'}
    assert needed<=translated.keys(),('Missing templates',needed-translated.keys())
    for n in needed:
        src=templates[int(n)]['jp'];t=translated[n]
        assert tags(t)==tags(src),('Template tags',n)
        assert sorted(re.findall(r'\{n\d+\}',t))==sorted(re.findall(r'\{n\d+\}',src)),('Number placeholders',n)
        assert not re.search(r'[\u3040-\u30ff\u3400-\u9fff]',t),n
    entries={};exceptions=[]
    for row in rows:
        k=row['id'];jp=original[k]['Text'];assert jp==row['jp'],k
        assert not original[k].get('MetaData',{}).get('ACTOR'),('Speech selected',k)
        assert k not in base['assets'][R]['entries'],('Existing text overwritten',k)
        if row['mode']=='manual':
            t=translated[str(row['template'])]
            for i,num in enumerate(row['numbers']):t=t.replace('{n'+str(i)+'}',num)
            if row['template'] in (897,898,911):
                assert row['numbers']==['2'] and 'Hell Rider II' in row['en'],k
                t=t.replace('Hell Rider VR2','Hell Rider II')
                exceptions.append(dict(id=k,reason='Official US enemy reference in UI prose: JP VR2 is named Hell Rider II; enemy labels remain deferred.'))
        elif row['mode']=='temporal_override':
            assert k=='$area2360_4yearsago' and jp=='４年前',k
            t='4 ปีก่อน'
        else:
            t=scope['automatic'][k]
            if tags(t)!=tags(jp):
                assert k in ('$area1360_DaihachiShinramaru','$lvl_Location_ev_junoe_4011','$map1360') and not tags(jp),k
                assert all(x in ('<i>','</i>') for x in tags(t)),k
                t=t.replace('<i>','').replace('</i>','')
                exceptions.append(dict(id=k,reason='US italics decoration removed to preserve the JP tag contract.'))
        if k in scope.get('reviewed_text_overrides',{}):
            t=scope['reviewed_text_overrides'][k]
        # The official piano note C・ uses a nonlinguistic octave dot.
        assert t.strip() and not re.search(r'\{n\d+\}|[\u3040-\u30ff\u3400-\u9fff]',t.replace('・','')),k
        assert tags(t)==tags(jp),('Source control tags',k)
        assert k not in entries,k
        entries[k]=t
    combined=copy.deepcopy(base)
    combined['scope']='Chapters 1–2 dialogue, existing inventory effects, and screenshot-related whole-game UI categories; working assets only'
    combined['assets'][R]['entries'].update(entries)
    enemy_records=0
    enemy_path=W/'translations/enemy-names-th.json'
    if enemy_path.exists():
        enemy=read(str(enemy_path))['assets'][R]['entries']
        for k,t in enemy.items():
            assert k not in combined['assets'][R]['entries'] or combined['assets'][R]['entries'][k]==t,(k,'Enemy name conflicts with existing translation')
            assert tags(t)==tags(original[k]['Text']),k
        combined['assets'][R]['entries'].update(enemy)
        enemy_records=len(enemy)
        combined['enemy_name_records']=enemy_records
    combined['ui_completion_records']=len(entries)
    combined['source_only']=True
    assert len(entries)==len(scope['selected_ids'])==len(set(scope['selected_ids']))
    assert set(entries)==set(scope['selected_ids'])
    for a,patch in base['assets'].items():
        assert combined['assets'][a]['actors']==patch['actors'],a
        for k,t in patch['entries'].items():assert combined['assets'][a]['entries'][k]==t,(a,k)
    assert not any(k.startswith(('$en_','$enemy_','$menu_EnemyBookText_')) for k in entries),'Enemy labels/encyclopedia added'
    write('translations/ui-completion-th.json',{'scope':combined['scope'],'assets':{R:{'entries':entries,'actors':{}}}})
    write('translations/working-ui-completion-th.json',combined)
    write('qa/ui-completion/assembly.json',dict(new_ui_records=len(entries),reviewed_manual_templates=len(needed),
        total_text_records=sum(len(a['entries']) for a in combined['assets'].values()),
        categories=dict(collections.Counter(r['category'] for r in rows)),modes=dict(collections.Counter(r['mode'] for r in rows)),
        original_base_records_preserved=True,enemy_labels_deferred=not bool(enemy_records),enemy_name_records=enemy_records,no_new_spoken_dialogue=True,
        exceptions=exceptions,distribution_unchanged=True,installed=False,runtime_tested=False))
    print('Compiled',len(entries),'new UI records;',len(needed),'reviewed templates; base records preserved')

if __name__=='__main__':main()
