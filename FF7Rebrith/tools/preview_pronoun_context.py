"""Render every changed pronoun record using current staged glyphs."""
from pronoun_context import Q,decisions
from preview_chapter11_recheck import render_selected
if __name__=='__main__':
    render_selected([dict(asset=r['asset'],id=r['id'],template=r['index'],kind=r['actor'] or 'NPC') for r in decisions()],Q,'Pronoun context')
