"""Apply reviewed Ch9 wording/terminology corrections; preserve frozen template indices."""
from pathlib import Path
from prepare_chapter9 import W, read, write
from assemble_chapter9 import values


def main():
    old = read('qa/chapter9/recheck/current.json')
    snapshot = Path(old['snapshot'])
    previous = read(snapshot / 'translations/chapter9-th.json')
    vals = values()
    active = {r['template'] for r in read('reference/chapter9-source.json') if not r['reason']}
    changes = {}
    # Match the recorded PlearnGaming glossary; change only Ch9, not historical chapters.
    replacements = {'ทีฟา': 'ทีฟ่า', 'มาโค': 'มาโก้', 'เจโนว่า': 'เจโนวา',
                    'โชโคโบะ': 'โจโกโบะ', 'แชดลีย์': 'แชดลี่ย์', 'เร้ด': 'เรด'}
    for i in sorted(active):
        if str(i) not in vals:
            continue
        before = vals[str(i)]
        after = before
        for a, b in replacements.items():
            # Red Shelly is a separately evidenced flower name, not Red XIII.
            if a == 'เร้ด' and 'เร้ดเชลลี่' in after:
                continue
            after = after.replace(a, b)
        if i in (995, 1757, 1761):
            after = after.replace('โรงงาน', 'โรงช่าง')
        if i == 293:
            after = 'นั่นสินะ'
        if i == 1733:
            after = 'แล้วแวะมาใหม่นะ'
        if i == 834:
            after = 'เหนื่อยหน่อยนะคะ~'
        if i == 2149:
            after = 'เหนื่อยหน่อยนะคะ!'
        if after != before:
            changes[str(i)] = after
    path = W / 'translations/chapter9/zz-recheck.json'
    existing = read(path) if path.exists() else {}
    existing.update(changes)
    # Append-only indices created by extend_chapter9.py, located by ID rather than constants.
    extra = {'$key_GONGM_BuggyKey_help':
             'กุญแจสำหรับบักกี้ขนาดใหญ่ที่ใช้ยางพิเศษลุยทะเลทราย\r\nสามารถเรียกบักกี้ได้ในบริเวณที่รองรับการขึ้นรถ',
             '$key_GONGM_WireGun_help':
             'ปืนสำหรับการเคลื่อนที่ที่ยิงลวดออกไปเพื่อดึงตัวขึ้นสู่ที่สูง'}
    for r in read('reference/chapter9-source.json'):
        if r['id'] in extra:
            existing[str(r['template'])] = extra[r['id']]
        elif r['id'].startswith('$CHADLEY_SHOP_'):
            existing[str(r['template'])] = r['English']['Text']
    write(path, existing)
    write('qa/chapter9/recheck/editorial-decisions.json', dict(
        baseline=snapshot.as_posix(), baseline_records=sum(len(p['entries']) for p in previous['assets'].values()),
        corrections=['Aerith still-love answer: そうだね acknowledges preceding question, not accepting an offer',
                     'Ch9 spellings aligned to evidence-backed PlearnGaming glossary; historical chapters unchanged',
                     'Izo 工房 is workshop, not factory', 'Bookshop return greeting made idiomatic'],
        new_UI=['All CHADLEY_SHOP_ official-US shop labels, 6 missing records',
                'Both key_GONGM_ travel-item descriptions, JP-primary movement mechanics'],
        replacements=replacements, template_overrides=existing,
        runtime_tested=False, new_full_video_audio_review=False))
    print('Reviewed overrides:', len(existing))


if __name__ == '__main__':
    main()
