"""Mount all ZIP parts together and compare every asset with the verified set."""
import hashlib,json,logging,uuid,zipfile
from pathlib import Path
import pack_prototype as p

W=p.WORK;QA=W/'qa/final-parts';FINAL=W.parent/'Mod/Final'

def main():
    report=json.loads((QA/'latest.json').read_text('utf-8'))
    expected=json.loads((W/report.get('working_manifest','qa/ui-completion/working-assets.json')).read_text('utf-8'))
    check=QA/'mount-checks'/uuid.uuid4().hex;check.mkdir(parents=True)
    names=set()
    for part in report['parts']:
        path=FINAL/part['zip']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==part['sha256']
        with zipfile.ZipFile(path) as z:
            assert z.namelist()==part['mod_files'] and z.testzip() is None
            for name in z.namelist():
                assert Path(name).name==name and name not in names
                names.add(name);(check/name).write_bytes(z.read(name))
    logging.disable(logging.CRITICAL);p.reader.preload_oodle()
    provider=p.DefaultFileProvider(str(check),p.VersionContainer(p.EUEVersion.GAME_UE4_26))
    provider.initialize();assert provider.submit_key()
    p.reader.fix_partition_size(provider)
    actual={}
    for name,entry in p.reader.iter_entries(provider):
        rel=str(Path(name+('' if Path(name).suffix else '.uasset')))
        assert rel not in actual,('Overlapping asset',rel)
        actual[rel]=hashlib.sha256(p.reader._entry_bytes(entry)).hexdigest()
    assert actual==expected,'Combined split archives differ from the verified full translation'
    assert len(names)==3*len(report['parts']) and len(actual)==report['total_assets']
    result=dict(all_parts_mounted_together=True,zip_count=len(report['parts']),all_three_zips_mounted_together=len(report['parts'])==3,mod_files=len(names),assets=len(actual),
        all_match_verified_combined_set=True,overlapping_assets=[],runtime_tested=False)
    (QA/'combined-mount-verification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print('Verified',len(report['parts']),'ZIPs /',len(names),'mod files mounted together:',len(actual),'matching assets, no overlap')

if __name__=='__main__':main()
