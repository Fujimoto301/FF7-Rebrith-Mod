"""Validate immutable visual review provenance, including exact-panel reuse.

All carried panels must lead to an archived, actually viewed proof or contact
sheet. A prior partial visual ledger cannot terminate the evidence chain.
"""
from pathlib import Path
from prepare_chapter9 import W,read
from context_full_read import Q,digest

def validate(folder=Q,expected_sha=None,visited=None):
    visited=set() if visited is None else visited
    proof=read(folder+'proof.json');visual=read(folder+'visual-review.json')
    sha=proof['source_sha256']
    assert expected_sha is None or sha==expected_sha
    assert visual['source_sha256']==sha and visual['pages']==proof['pages']
    assert sha not in visited,'Visual evidence chain must be acyclic'
    visited.add(sha)
    arts=[folder+'proof.json',folder+'visual-review.json']
    for p,h in visual['images'].items():
        # Archived ledgers retain the original paths and hashes. The immutable
        # archive contains the exact image bytes under the same basename.
        name=folder+Path(p).name
        assert digest(W/name)==h,name
        arts.append(name)
    expected={folder+f'proof-{i}.png' for i in range(1,proof['pages']+1)}
    assert expected<=set(arts),'All complete proof pages must remain bound'
    if not visual['all_pages_viewed']:
        reuse=read(folder+'panel-visual-reuse.json')
        assert visual.get('all_panels_reviewed') and reuse['source_sha256']==sha
        assert visual['visual_reuse_report_sha256']==digest(W/folder/'panel-visual-reuse.json')
        indices=[r['current_panel'] for r in reuse['reused_exact_RGB_and_metadata']+reuse['must_view']]
        assert len(indices)==len(set(indices))==proof['panels']
        assert set(indices)==set(range(proof['panels']))
        assert visual['new_contact_sheets_viewed']==list(range(1,reuse['new_contact_sheet_pages']+1))
        for i in visual['new_contact_sheets_viewed']:
            assert folder+f'new-panels-page-{i}.png' in arts
        prior=Q+'releases/'+reuse['prior_source_sha256']+'/viewed-proof/'
        assert digest(W/prior/'visual-review.json')==reuse['prior_visual_review_sha256']
        arts.append(folder+'panel-visual-reuse.json')
        arts+=validate(prior,reuse['prior_source_sha256'],visited)
    return list(dict.fromkeys(arts))

if __name__=='__main__':
    print('Verified visual evidence chain:',len(validate()),'immutable proof/ledger/image artifacts')
