"""Reviewed follow-up: Tifa invitation and each affected Junon choice context."""
import hashlib,re,shutil,sys,uuid
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
Q='qa/chapter4-choice-fix/'
A='End/Content/Text/JP/8200-JUNOE_TxtRes.uasset'
TIFA='$C2120_MAIN_2700_0500_00_tif'
TARGETS={
 TIFA:'เข้ามาสิ',
 '$C2120_MAIN_3800_0110_00_sys':'จะขึ้นไปด้านบนหรือไม่?\r\n(จะยังกลับมา Under Junon ไม่ได้สักพัก)',
 '$C2120_MAIN_3800_0120_00_sys':'ขึ้นไป', '$C2120_MAIN_3800_0130_00_sys':'ยังไม่ขึ้น',
 '$C2120_MAIN_4400_0020_00_sys':'ลองใหม่', '$C2120_MAIN_4400_0030_00_sys':'ไม่ลอง',
 '$C2210_MAIN_2420_0200_00_sys':'ฝึกอีกครั้ง', '$C2210_MAIN_2420_0300_00_sys':'ไม่ฝึก',
 '$C2210_MAIN_5000_0320_00_sys':'<button=main-story>เข้าร่วม', '$C2210_MAIN_5000_0330_00_sys':'ยังไม่เข้าร่วม',
 '$CHADL_QST_02_0400_0300_00_sys':'ท้าทาย', '$CHADL_QST_02_0400_0400_00_sys':'ยกเลิก',
 '$CHADL_QST_02_0410_0200_00_sys':'ลองใหม่', '$CHADL_QST_02_0410_0300_00_sys':'ยกเลิก',
 '$CHADL_QST_02_1000_0200_00_sys':'เข้าไป', '$CHADL_QST_02_1000_0300_00_sys':'ยังไม่เข้า',
 '$JUNOE_QST_02_0300_0120_00_sys':'ตามไป', '$JUNOE_QST_02_0300_0130_00_sys':'ยังไม่ไป',
 '$JUNOE_QST_05_0400_0800_00_sys':'เล่น', '$JUNOE_QST_05_0400_0900_00_sys':'ยังไม่เล่น',
}
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def active():return (W/Q/'baseline.json').exists()
def records():return read(Q+'source-review.json')['records']
def matches(a,k,before,after):
    if not active() or a!=A or k not in TARGETS or after!=TARGETS[k]:return False
    r=next(r for r in records() if r['id']==k)
    return before==r['before'] or k==TIFA and before=='ถามสิ'
def overlay(now):
    if not active():return
    for r in records():
        old=now['assets'][A]['entries'][r['id']]
        assert old==r['after'] or matches(A,r['id'],old,r['after'])
        now['assets'][A]['entries'][r['id']]=r['after']
def prepare():
    assert not active(),'Never replace the follow-up snapshot'
    ctx=read('qa/active-working-set.json');now=read(ctx['combined_source']);snap=W/Q/'revisions'/uuid.uuid4().hex
    paths=[ctx['combined_source'],ctx['manifest'],ctx['cluster_map'],'qa/active-working-set.json','qa/final-parts/latest.json','qa/chapter10/editorial-signoff.json','reference/chapter4-ui-overrides.json','translations/chapter4-th.json','translations/chapter4/reused-lines.json','translations/chapter4/batch-03.json','qa/chapter4-door-fix/source-review.json']
    for rel in paths:
        dest=snap/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,dest)
    write(Q+'baseline.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint(),hashes={p:digest(snap/p) for p in paths}))
    jp=txtres.parse(str(W/'source'/A));us=txtres.parse(str(W/'source'/A.replace('/JP/','/US/')))
    rows=[]
    for k,t in TARGETS.items():
        before=now['assets'][A]['entries'][k];assert before!=t
        assert re.findall('<[^>]+>',t)==re.findall('<[^>]+>',jp[k]['Text'])
        rows.append(dict(asset=A,id=k,before=before,after=t,Japanese=jp[k],English=us[k],decision='Tifa uses the explicitly requested invitation.' if k==TIFA else 'Answer the actual action in the adjacent prompt; do not reuse tutorial viewing labels.'))
    assert len(rows)==20
    write(Q+'source-review.json',dict(records=rows,root_cause='Shared はい/いいえ templates364/365 inherited ดู/ไม่ดู from the Ch2 transmutation tutorial.',correct_tutorial_pair_retained=True))
    print('Saved follow-up snapshot and20 JP/US context corrections')
def apply():
    assert active()
    v=read('translations/chapter4/reused-lines.json');assert v['364']=='ดู' and v['365']=='ไม่ดู';v['364']='ใช่';v['365']='ไม่ใช่';write('translations/chapter4/reused-lines.json',v)
    v=read('translations/chapter4/batch-03.json');v['363']=TARGETS['$C2120_MAIN_3800_0110_00_sys'];write('translations/chapter4/batch-03.json',v)
    overrides=read('reference/chapter4-ui-overrides.json');overrides.update(TARGETS);write('reference/chapter4-ui-overrides.json',overrides)
    p=read('translations/chapter4-th.json');overlay(p);write('translations/chapter4-th.json',p)
    print('Applied per-ID choice overrides and safe generic yes/no rebuild defaults')
def audit():
    from context_recheck import matches as context_matches,active as context_active,decisions
    from context_full_read import matches as full_matches,decisions as full_decisions,active as full_active,Q as FULL_Q
    rev=read(Q+'baseline.json');snap=Path(rev['snapshot']);ctx=read('qa/active-working-set.json');old=read(snap/ctx['combined_source']);now=read(ctx['combined_source']);changes=[]
    for p,h in rev['hashes'].items():assert digest(snap/p)==h,p
    assert old['assets'].keys()==now['assets'].keys()
    for a,p in old['assets'].items():
        n=now['assets'][a];assert p['entries'].keys()==n['entries'].keys() and p['actors']==n['actors']
        for k,t in p['entries'].items():
            if t!=n['entries'][k]:assert matches(a,k,t,n['entries'][k]) or context_matches(a,k,t,n['entries'][k]) or full_matches(a,k,t,n['entries'][k]),(a,k);changes.append((a,k))
    extra={(r['asset'],r['id']) for r in decisions()} if context_active() else set()
    extra|={(r['asset'],r['id']) for r in full_decisions()}
    assert set(changes)=={(A,k) for k in TARGETS}|extra
    assert read(ctx['cluster_map'])==read(snap/ctx['cluster_map'])
    prior=read(snap/ctx['manifest']);current={str(p.relative_to(W/ctx['stage'])):digest(p) for p in sorted((W/ctx['stage']).rglob('*.uasset'))}
    assert current.keys()==prior.keys() and {p.replace('\\','/') for p,h in current.items() if h!=prior[p]}=={A}|{a for a,k in extra}
    corpus=read('reference/rebirth-jp-corpus.json');left=[]
    for a,p in now['assets'].items():
        for k,t in p['entries'].items():
            if t in ['ดู','ไม่ดู'] and corpus[Path(a).name][k]['Text'] in ['はい','いいえ']:left.append((a,k,t))
    assert len(left)==2 and all('C1920_MAIN_3400_' in k for a,k,t in left),'Unexpected tutorial labels in unrelated yes/no context'
    for r in records():
        assert now['assets'][A]['entries'][r['id']]==read('reference/chapter4-ui-overrides.json')[r['id']]==read('translations/chapter4-th.json')['assets'][A]['entries'][r['id']]==r['after']
        assert re.findall('<[^>]+>',r['after'])==re.findall('<[^>]+>',r['Japanese']['Text'])
    expected_protected=read('qa/context-recheck/baseline.json')['protected'] if context_active() else rev['protected']
    if full_active():expected_protected=read(FULL_Q+'baseline.json')['protected']
    from verify_installed_session import verify
    verify(expected_protected)
    write(Q+'audit.json',dict(source_sha256=digest(W/ctx['combined_source']),corrected_records=20,subsequent_context_corrections=len(extra),total_records=40691,all_other40671_texts_and_actors_preserved=not extra,all_fonts_and_other26_assets_identical=not extra,all_fonts_identical=True,all_original20_corrections_preserved=True,legitimate_tutorial_labels=left,in_game_tested=False))
    print('Ch4 follow-up20 corrections retained; subsequent context changes:',len(extra),'; Ch2 tutorial viewing pair retained; all fonts unchanged')
def groups():
    jp=read('reference/rebirth-jp-corpus.json')['8200-JUNOE_TxtRes.uasset']
    result=[('Door responses',[TIFA,'$C2120_MAIN_2900_0100_00_red'])]
    for prefix in ['$C2120_MAIN_3800_','$C2120_MAIN_4400_','$C2210_MAIN_2420_','$C2210_MAIN_5000_','$CHADL_QST_02_0400_','$CHADL_QST_02_0410_','$CHADL_QST_02_1000_','$JUNOE_QST_02_0300_','$JUNOE_QST_05_0400_']:
        result.append((prefix,[k for k,v in jp.items() if k.startswith(prefix) and k.endswith('_sys') and v['Text'] and (prefix!='$JUNOE_QST_05_0400_' or int(k.split('_')[-3])<1000)]))
    return result
def preview():
    from PIL import Image,ImageDraw,ImageFont
    from preview_ch12_recheck import renderer
    ctx=read('qa/active-working-set.json');stage=W/ctx['stage'];data=txtres.parse(str(stage/A));legend=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
    fonts={size:renderer(stage,f'U_Com_JP_SystemFont{size}.uasset') for size in ['Large','Normal']};gsamples=[];allgroups=groups()
    for page in range((len(allgroups)+3)//4):
        pairs=[]
        for label,keys in allgroups[page*4:(page+1)*4]:
            cells=[]
            for size,(gs,mask) in fonts.items():
                text=re.sub('<[^>]+>','','\n'.join(data[k]['Text'] for k in keys)).replace('\r','');x=14;y=45;ops=[];bottom=125
                for ch in text:
                    if ch=='\n':x=14;y+=52;continue
                    g=gs[ord(ch)]
                    if x+g[8]>945:x=14;y+=52
                    if g[4] and g[5]:ops.append((x+g[6],y+g[7],mask(g)));bottom=max(bottom,y+g[7]+g[5]+18)
                    x+=g[8]
                cell=Image.new('RGB',(960,bottom),'#17283d');ImageDraw.Draw(cell).text((10,8),size+' | '+label,font=legend,fill='#9fd8e8')
                for x,y,m in ops:cell.paste((242,247,255),(x,y),m)
                cells.append(cell);gsamples.append(dict(ids=keys,font=size,clipped=False))
            pairs.append(cells)
        heights=[max(c.height for c in pair) for pair in pairs];canvas=Image.new('RGB',(1960,60+sum(h+12 for h in heights)),'#091522');d=ImageDraw.Draw(canvas);d.text((15,15),'Ch4 choice contexts | Actual staged glyphs | Illustrative layout, not in-game',font=legend,fill='#bfd7ed');y=55
        for pair,h in zip(pairs,heights):
            for col,cell in enumerate(pair):canvas.paste(cell,(10+980*col,y))
            y+=h+12
        canvas.save(W/Q/f'proof-{page+1}.png')
    write(Q+'proof.json',dict(source_sha256=digest(W/ctx['combined_source']),pages=3,samples=gsamples,actual_staged_glyphs=True,in_game_tested=False))
    print('Rendered3 pages: door pair and all questions/options in9 affected choice groups')
def finalize():
    audit();rev=read(Q+'baseline.json');snap=Path(rev['snapshot']);ctx=read('qa/active-working-set.json');parts=read('qa/final-parts/latest.json');old={p['zip']:p for p in read(snap/'qa/final-parts/latest.json')['parts']};updated=[]
    for p in parts['parts']:
        assert digest(W.parent/'Mod/Final'/p['zip'])==p['sha256']
        if p['sha256']!=old[p['zip']]['sha256']:updated.append(p['zip'])
    assert updated==['ThaiJP_Chapter3_4_5_P.zip']
    m=read('qa/final-parts/combined-mount-verification.json');assert m['zip_count']==8 and m['mod_files']==24 and m['assets']==27 and not m['overlapping_assets'] and m['all_match_verified_combined_set']
    s=read('qa/chapter10/editorial-signoff.json');assert s['source_sha256']==digest(W/ctx['combined_source'])
    for p,h in s['reviewed_artifacts'].items():assert digest(W/p)==h,p
    write(Q+'release-verification.json',dict(source_sha256=s['source_sha256'],corrected_records=20,total_records=40691,updated_parts=updated,other7_zips_unchanged=True,all8_archives_read_back=True,installed=False,in_game_tested=False))
    root='E:/FF7RebrithModTH/FF7Rebrith/'
    note=f'''<!-- chapter4-choice-current -->
## ล่าสุด: ทีฟ่าเข้ามาสิ + ตัวเลือกCh.4 — 20 ตุลาคม 2026

ตามภาพ/คำสั่งใหม่ ทีฟ่า `$C2120_MAIN_2700_0500_00_tif` ใช้ **เข้ามาสิ** แยกจากRedXIIIที่คง **เชิญ** แก้ตัวเลือกที่reuseคำว่า **ดู/ไม่ดู** ผิดบริบทครบ17ป้ายในJUNOE พร้อมป้ายเข้าร่วมพาเหรดที่มีtag1ป้ายและเกลาคำถามขึ้นด้านบน1ข้อความ รวมรอบนี้ **20ข้อความ** (ทีฟ่า1+ตัวเลือก18+คำถาม1) คำตอบขึ้นด้านบนเป็น **ขึ้นไป/ยังไม่ขึ้น**; กลุ่มลองใหม่/ฝึกพาเหรด/เข้าร่วมพาเหรด/FortCondor/ตามSalmon/เล่นJumpfrogใช้คำตอบให้ตรงกิจกรรม ครอบคลุม9กลุ่มคำถาม ตรวจภาพคำถามกับทุกปุ่ม3หน้าใช้glyphจริงแล้ว บทสอนคราฟต์Ch.2ยังใช้ดู/ไม่ดูถูกบริบทจึงคงไว้

ต้นเหตุคือCh4แม่แบบ364/365นำคำแปลはい/いいえจากบทสอนดูมาซ้ำ แก้generic defaultsเป็นใช่/ไม่ใช่ และper-IDoverrideแยกกิจกรรมในreference/chapter4-ui-overrides.json อัปเดตtranslations/chapter4-th.json+reused-lines.json+batch-03.json; tools/chapter4_choice_fix.py overlayท้ายassemble_chapter10.pyโดยอ้างsnapshotใหม่ qa/chapter4-choice-fix/baseline.json+revisions/ **ห้ามprepareซ้ำ/เปลี่ยนsnapshotเก่า** qa/chapter4-door-fixเดิมยังเป็นประวัติและgateประตูสะสมยอมเฉพาะ21IDที่reviewแล้ว(รอบก่อน2+รอบนี้20ซ้ำทีฟ่า1)

ฐานยัง **translations/working-through-chapter10-th.json — 40,691ข้อความ / 27assets / 717clusters** อีก40,671ข้อความและACTORทั้งหมดคงเดิม ทุกฟอนต์/อีก26assetsไบต์เดิม อัปเดตเฉพาะ **ThaiJP_Chapter3_4_5_P.zip** ใน E:/FF7RebrithModTH/Mod/Final อีก7ZIPhashเดิม อ่านกลับ8ZIP/24modfiles/27assetsผ่าน ไม่มีติดตั้ง/ทดลองตัวเลือกจริงในเกม

หลักฐาน [CHAPTER4-CHOICE-FIX.md]({root}CHAPTER4-CHOICE-FIX.md), qa/chapter4-choice-fix/source-review.json(JP/USก่อนหลัง20ID), audit.json, proof-1.pngถึงproof-3.png, release-verification.json SignoffCh10ผูกhashใหม่ทุกไฟล์แล้ว ขั้นตอน: assemble_chapter10 → build_chapter10 --text-only/--verify → chapter10_recheck --quality → audit_shared_dialogs → audit_chapter10_glyphs → preview_chapter10 + chapter4_door_fix --preview + chapter4_choice_fix --preview/ดูภาพ → signoff_chapter10 → publish_final_parts → chapter4_choice_fix --finalize ไม่ใช้finalizeประวัติบทเก่าทับcontextใหม่ เมื่อมีการติดตั้งโดยผู้ใช้ก่อนเริ่มรอบ ให้ใช้protectedmanifestของsnapshotรอบล่าสุด คงdist/ต้นฉบับ/เกมที่ติดตั้งปัจจุบันระหว่างทำงาน
<!-- /chapter4-choice-current -->

'''
    (W/'CHAPTER4-CHOICE-FIX.md').write_text('# แก้บริบทตัวเลือก Ch.4\n\n'+note,'utf-8')
    for path in [W.parent/'HANDOFF.md',W/'AGENTS.md',W/'TRANSLATION_GUIDE.md',W/'CHAPTER4-STATUS.md',W/'CHAPTER10-STATUS.md',W/'FINAL-PARTS.md']:
        title,body=path.read_text('utf-8').split('\n',1);body=re.sub(r'<!-- chapter4-choice-current -->.*?<!-- /chapter4-choice-current -->\s*','',body,flags=re.S);path.write_text(title+'\n\n'+note+body.lstrip(),'utf-8')
    print('Finalized20 Ch4 corrections; only Chapter3_4_5 ZIP updated;8 archives verified')
if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    elif '--apply' in sys.argv:apply()
    elif '--preview' in sys.argv:preview()
    elif '--finalize' in sys.argv:finalize()
    else:audit()
