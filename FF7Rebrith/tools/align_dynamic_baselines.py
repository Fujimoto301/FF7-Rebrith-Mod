"""Align Thai glyph origins with native ASCII, including runtime substitutions."""
import hashlib,json,shutil,string,struct,uuid
from pathlib import Path
from create_ui_completion_scope import W,read,write
from assemble_ui_completion import fingerprint

COMMON=Path('End/Content/Menu/Billboard/Common')
STAGE=W/'staging/ThaiJP_UICompletion_Working'
POLICY=W/'reference/native-baseline-policy.json'

def begin_revision():
    qa=W/'qa/baseline-alignment';qa.mkdir(parents=True,exist_ok=True)
    assert not (qa/'baseline.json').exists(),'Use the existing snapshot for this correction'
    run=qa/'revisions'/uuid.uuid4().hex;run.mkdir(parents=True)
    for rel in ('translations/working-ui-completion-th.json','reference/ui-completion-cluster-map.json',
                'qa/ui-completion/working-assets.json','qa/ui-completion/build-verification.json',
                'qa/ui-completion/active-revision.json','qa/final-parts/latest.json'):
        dest=run/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/rel,dest)
    for p in (STAGE/COMMON).glob('*.uasset'):
        if '-' in p.name:continue
        dest=run/'fonts'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    protected=run/'protected-files-before.json';write(str(protected),fingerprint())
    baseline=dict(backup=str(run),previous_combined_source=str(run/'translations/working-ui-completion-th.json'),
        previous_assets=str(run/'qa/ui-completion/working-assets.json'),protected_manifest=str(protected))
    write('qa/baseline-alignment/baseline.json',baseline)
    write('qa/ui-completion/active-revision.json',dict(**baseline,
        reason='Align Thai glyph positions with native ASCII so runtime names and numbers share the same baseline.'))
    write('reference/native-baseline-policy.json',dict(anchor='Original ASCII H ink bottom',
        thai_alignment='Shift all Thai clusters by the same vertical delta per font',
        ascii_glyphs='Original records, pixels and spacing unchanged',
        latin_aliases='Use the original ASCII vertical origin',
        digit_aliases='Align ink bottom to the Thai/native H baseline',
        original_digit_overshoot='Retain native optical rounding, up to 2 pixels in 4K fonts',
        source_tags_and_text='Unchanged',working_set='ThaiJP_UICompletion_Working'))

def align_fonts(stage=STAGE,cmap=None,report_path='qa/baseline-alignment/alignment.json'):
    import verify_chapter1 as v
    cmap=cmap or read('reference/ui-completion-cluster-map.json')
    reports=[]
    for path in sorted((stage/COMMON).glob('U_Com_JP_SystemFont*.uasset')):
        if '-' in path.name:continue
        data=path.read_bytes();records,tail=v.glyphs(data);mapping={g[0]:g for g in records};pages={}
        def mask(g):
            if g[1] not in pages:
                p=path.with_name(path.stem+f'-{g[1]:02d}.uasset')
                if not p.exists():p=W/'source'/COMMON/p.name
                pages[g[1]]=v.atlas(p)[0].getchannel('R')
            return pages[g[1]].crop((g[2],g[3],g[2]+g[4],g[3]+g[5]))
        def bottom(g):
            box=mask(g).point(lambda p:255 if p>=64 else 0).getbbox();assert box
            return g[7]+box[3]
        native=bottom(mapping[ord('H')]);old_thai=bottom(mapping[ord(cmap['ก'])]);delta=native-old_thai
        thai_keys={k for k in cmap if '\u0e01'<=k[0]<='\u0e5b'}
        for cluster in thai_keys:
            g=list(mapping[ord(cmap[cluster])]);g[7]+=delta
            assert -32768<=g[7]<=32767
            mapping[g[0]]=tuple(g)
        digit_shifts={}
        for ch in string.ascii_letters+string.digits:
            g=list(mapping[ord(ch)]);g[0]=ord(cmap[ch])
            shift=native-bottom(mapping[ord(ch)]) if ch.isdigit() else 0
            g[7]+=shift;mapping[g[0]]=tuple(g)
            if ch.isdigit():digit_shifts[ch]=shift
        e=v.b.header_end(data);start=10 if data[e:e+2]==b'\1\11' else 12
        patched=bytearray(data)
        for i,g in enumerate(records):struct.pack_into('<6H2hH',patched,e+start+i*18,*mapping[g[0]])
        assert all(mapping[g[0]]==g for g in records if g[0] not in {ord(x) for x in cmap.values()})
        assert bottom(mapping[ord(cmap['ก'])])==native
        assert all(bottom(mapping[ord(cmap[c])])==native for c in string.digits)
        assert all(mapping[ord(cmap[c])][1:]==mapping[ord(c)][1:] for c in string.ascii_letters)
        if patched!=data:path.write_bytes(patched)
        reports.append(dict(font=path.name,thai_shift_applied=delta,thai_baseline_before=old_thai,
            native_ascii_baseline=native,thai_baseline_after=native,thai_cluster_count=len(thai_keys),
            latin_alias_shift=0,digit_alias_shifts=digit_shifts,original_ascii_records_unchanged=True,
            atlas_unchanged=True,sha256=hashlib.sha256(patched).hexdigest()))
    assert len(reports)==8
    write(report_path,dict(fonts=reports,policy=read(str(POLICY)),runtime_tested=False))
    return reports

if __name__=='__main__':
    begin_revision()
    for r in align_fonts():print(r['font'],'Thai shift',r['thai_shift_applied'],'native baseline',r['native_ascii_baseline'])
