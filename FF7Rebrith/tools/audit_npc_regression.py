"""Carry every recovered Ch2–9 NPC into a later active chapter without resetting it."""
from prepare_chapter9 import W,read,write,txtres
from choice_completion import JP
from chapter4_door_fix import matches as reviewed_choice_match


def main():
    ctx=read('qa/active-working-set.json');now=read(ctx['combined_source'])
    previous=read('translations/working-npc-recheck-th.json')
    cmap=read(ctx['cluster_map']);reverse=str.maketrans({v:k for k,v in cmap.items()})
    decoded={};count=0;reviewed_changes=[]
    for r in read('reference/npc-recheck-source.json'):
        a,k=r['asset'],r['id'];p=now['assets'][a];expected=previous['assets'][a]
        ch12=False
        if ctx.get('chapter12'):
            for change in read('reference/chapter12-context-overrides.json')['records']:
                if (a,k)==(change['asset'],change['id']) and p['entries'][k]==change['after']:
                    ch12=expected['entries'][k]==change['before'] or reviewed_choice_match(a,k,expected['entries'][k],change['before'])
        assert k in p['entries'] and (p['entries'][k]==expected['entries'][k] or reviewed_choice_match(a,k,expected['entries'][k],p['entries'][k]) or ch12),(k,'Recovered NPC changed or lost; explicitly review a new revision')
        if p['entries'][k]!=expected['entries'][k]:
            from context_recheck import matches as context_matches
            proof='reference/context-recheck-overrides.json' if context_matches(a,k,expected['entries'][k],p['entries'][k]) else 'qa/chapter4-choice-fix/source-review.json'
            from pronoun_context import matches as pronoun_matches
            if pronoun_matches(a,k,expected['entries'][k],p['entries'][k]):proof='reference/pronoun-context-overrides.json'
            if ch12:proof='reference/chapter12-context-overrides.json'
            reviewed_changes.append(dict(asset=a,id=k,before=expected['entries'][k],after=p['entries'][k],review=proof))
        if a not in decoded:decoded[a]=txtres.parse(str(W/ctx['stage']/a))
        assert decoded[a][k]['Text'].translate(reverse)==p['entries'][k] and not JP.search(p['entries'][k]),k
        if k in expected['actors']:
            assert p['actors'][k]==expected['actors'][k]==decoded[a][k]['MetaData']['ACTOR'],k
        count+=1
    write('qa/shared-dialogs/NPC-regression.json',dict(combined_source=ctx['combined_source'],recovered_NPC_inventory_preserved=count,reviewed_context_corrections=reviewed_changes,passed=True))
    print('NPC regression preserved',count,'IDs/actors with',len(reviewed_changes),'explicitly reviewed context corrections; active context retained')


if __name__=='__main__':main()
