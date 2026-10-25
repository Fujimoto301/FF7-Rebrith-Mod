"""Snapshot and verify the second, narrowly scoped Chapter10 editorial pass."""
import sys, shutil, uuid
from pathlib import Path
from prepare_chapter9 import W, read, write
from audit_chapter10 import digest
from assemble_ui_completion import fingerprint
from chapter4_door_fix import matches as door_matches,verify_protected

Q = 'qa/chapter10/continue-review/'
FIXES = {
    '1063': ('ทั้งตกตะลึง หวาดกลัว และขวัญเสีย', '萎縮 is shrinking back from fear, not depression.'),
    '1107': ('ดูเหมือนโบราณสถานนี้เคยเป็นที่\r\nขอบคุณและเฉลิมฉลองไลฟ์สตรีมน่ะ', '祝福 here celebrates the lifestream; avoid suggesting people bestow magical powers on it.'),
    '1153': ('ที่ไหนสักแห่งในกลุ่มโบราณสถานนี้\r\nมีสถานที่ที่เซทราผนึก『สิ่งแปลกปลอม』เอาไว้', 'Keep the content of the legend in this subtitle; the following subtitle supplies its attribution.'),
    '1154': ('ผมพบตำนานที่เล่าไว้แบบนั้นครับ', 'という伝承を確認しました attributes the preceding information to a legend without repeating it.'),
    '1161': (None, 'Remove stray space inside the AI-chip noun phrase.'),
    '1166': (None, 'Costa del Sol spoken spelling matches prior chapters: คอสตาเดลโซล.'),
    '1216': (None, 'Remove stray space inside the AI-chip noun phrase.'),
    '1331': (None, 'Sky chocobo wording matches the existing Thai tutorial: โจโกโบะบิน.'),
    '1487': ('จะว่าใช้แทนกันก็คงไม่ได้หรอกนะคะ แต่…', 'そのかわりと言ってはなんですが is a hesitant transition to the monster encountered instead; do not end the thought as a denial.'),
    '1523': ('เมื่อกี้ทำหน้าดุเชียวนะ', 'こわい顔 means a stern/scary expression, not a frightened expression.'),
    '2057': (None, 'Use the same 災いの予兆 term as Caesar and the quest conversation: ลางบอกภัยพิบัติ.'),
    '2061': (None, 'Use the same 災いの予兆 term as Caesar and the quest conversation: ลางบอกภัยพิบัติ.'),
    '2387': ('บ้าเอ๊ย มีแต่ต้องวิ่งให้ไหวจนวินาทีสุดท้าย!', 'ギリギリまで走りきる refers to holding out until the last moment, not reaching the end of a route.'),
    '2489': (None, 'Sky chocobo wording matches the existing Thai tutorial: โจโกโบะบิน.'),
    '2513': (None, 'Sky chocobo wording matches the existing Thai tutorial: โจโกโบะบิน.'),
    '2559': ('ทั้งพลังป้องกันและความคล่องตัว\r\nเหนือกว่าบาฮามุทเดิมจนเทียบกันไม่ติดเลยครับ', 'Make the direction of the comparison explicit: the evolved summon surpasses the earlier form.'),
    'recheck-89': (None, 'Use the same sky-chocobo term in adjacent shared traversal help.'),
    'recheck-90': (None, 'Use the same sky-chocobo term in adjacent shared traversal help.'),
}

def replacement(key, current):
    explicit = FIXES[key][0]
    if explicit is not None:
        return explicit
    return (current.replace('ชิปเอไอ เพิ่มเติม', 'ชิปเอไอเพิ่มเติม')
            .replace('คอสต้าเดลซอล', 'คอสตาเดลโซล')
            .replace('โจโกโบะเวหา', 'โจโกโบะบิน')
            .replace('โจโกโบะฟ้า', 'โจโกโบะบิน')
            .replace('ลางแห่งหายนะ', 'ลางบอกภัยพิบัติ'))

def prepare():
    assert not (W/Q/'current.json').exists(), 'Preserve the immutable second-pass snapshot'
    ctx = read('qa/active-working-set.json')
    snap = W/Q/'revisions'/uuid.uuid4().hex
    paths = [ctx['combined_source'], ctx['cluster_map'], ctx['manifest'],
             'translations/chapter10-th.json', 'translations/chapter10-recheck-lines.json',
             'reference/chapter10-recheck-source.json', 'reference/chapter10-source.json',
             'reference/chapter10-templates.json', 'qa/active-working-set.json',
             'qa/final-parts/latest.json', 'qa/chapter10/recheck/review.json',
             'qa/chapter10/recheck/release-verification.json', 'qa/chapter10/editorial-signoff.json']
    paths += [str(p.relative_to(W)) for p in (W/'translations/chapter10').glob('*.json')]
    for rel in paths:
        dest = snap/rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(W/rel, dest)
    write(Q+'current.json', dict(snapshot=str(snap), active=ctx, protected=fingerprint(),
          original_source_sha256=digest(W/ctx['combined_source']),
          snapshot_hashes={p:digest(snap/p) for p in paths}))
    print('Saved immutable second-pass snapshot:', snap)

def apply():
    assert (W/Q/'current.json').exists()
    seen = set()
    paths = list((W/'translations/chapter10').glob('batch-*.json'))
    paths += [W/'translations/chapter10-recheck-lines.json']
    for path in paths:
        vals = read(path); changed = False
        for key in vals.keys() & FIXES.keys():
            seen.add(key); new = replacement(key, vals[key])
            if new != vals[key]: vals[key] = new; changed = True
        if changed: write(path, vals)
    assert seen == FIXES.keys()
    print('Applied18 reviewed templates; original template indices unchanged')

def audit():
    rev=read(Q+'current.json'); snap=Path(rev['snapshot']); ctx=rev['active']
    for p,h in rev['snapshot_hashes'].items(): assert digest(snap/p)==h,p
    old=read(snap/ctx['combined_source']); now=read(ctx['combined_source'])
    rows=read('reference/chapter10-source.json')+read('reference/chapter10-recheck-source.json')
    index={(r['asset'],r['id']):str(r['template']) for r in rows}
    templates={str(r['index']):r for r in read('reference/chapter10-templates.json')}
    changes=[]
    assert old['assets'].keys()==now['assets'].keys()
    for a,p in old['assets'].items():
        n=now['assets'][a]
        assert p['entries'].keys()==n['entries'].keys() and p['actors']==n['actors']
        for k,t in p['entries'].items():
            if t==n['entries'][k]: continue
            if door_matches(a,k,t,n['entries'][k]): continue
            key=index[a,k]; assert key in FIXES,(a,k)
            assert replacement(key,t)==n['entries'][k],(key,'Unexpected edit')
            changes.append(dict(asset=a,id=k,template=key,before=t,after=n['entries'][k],
                decision=FIXES[key][1],Japanese=templates.get(key,{}).get('jp'),
                English=templates.get(key,{}).get('us')))
    assert {r['template'] for r in changes}==FIXES.keys()
    assert read(ctx['cluster_map'])==read(snap/ctx['cluster_map']), 'No new glyphs or mapping edits expected'
    verify_protected(rev['protected'])
    report=dict(source_sha256=digest(W/ctx['combined_source']),before_source_sha256=rev['original_source_sha256'],
        total_records=sum(len(v['entries']) for v in now['assets'].values()),added_records=0,
        corrected_records=len(changes),changes=changes,all_existing_ids_actors_and_glyphs_preserved=True,
        editorial_reading='JP/Thai line comparison and same-ID US context; continuation through quest/NPC/world-intel text. Automated corpus coverage is separate from manual reading.',
        in_game_tested=False,new_full_video_audio_review=False)
    if (W/'qa/chapter4-door-fix/baseline.json').exists():
        from chapter4_choice_fix import TARGETS,A
        from chapter4_door_fix import KEYS
        report['subsequent_approved_Ch4_corrections']=len(set(KEYS)|set(TARGETS))
        from context_recheck import active as context_active,decisions
        if context_active():report['subsequent_context_corrections']=len(decisions())
    write(Q+'review.json',report)
    print('Second-pass audit:',len(changes),'corrected records; no added/dropped IDs or actor/glyph-map edits')

if __name__=='__main__':
    if '--prepare' in sys.argv: prepare()
    elif '--apply' in sys.argv: apply()
    else: audit()
