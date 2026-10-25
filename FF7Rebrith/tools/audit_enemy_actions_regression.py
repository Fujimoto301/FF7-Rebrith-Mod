"""Preserve the official action inventory in future active chapter builds."""
from prepare_chapter9 import W,read,write,txtres


def main():
    ctx=read('qa/active-working-set.json');now=read(ctx['combined_source']);cmap=read(ctx['cluster_map'])
    reverse=str.maketrans({v:k for k,v in cmap.items()});r='End/Content/Text/JP/Resident_TxtRes.uasset'
    decoded=txtres.parse(str(W/ctx['stage']/r));rows=read('reference/enemy-actions-source.json')
    for row in rows:
        k=row['id'];t=row['English']['Text']
        assert now['assets'][r]['entries'][k]==t==decoded[k]['Text'].translate(reverse),(k,'Official action label lost')
    write('qa/shared-dialogs/enemy-actions-regression.json',dict(combined_source=ctx['combined_source'],official_action_inventory_preserved=len(rows),passed=True))
    print('Preserved',len(rows),'official English enemy action labels')


if __name__=='__main__':main()
