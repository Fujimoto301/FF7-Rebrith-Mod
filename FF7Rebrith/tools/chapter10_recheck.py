"""Independent Chapter10 content/adjacency review and immutable revision snapshot."""
import re,sys,shutil,uuid
from pathlib import Path
from collections import Counter
from prepare_chapter9 import W,read,write,txtres
from assemble_ui_completion import fingerprint
Q='qa/chapter10/recheck/'
def prepare():
    assert not (W/Q/'current.json').exists(),'Keep original recheck snapshot'
    ctx=read('qa/active-working-set.json');snap=W/Q/'revisions'/uuid.uuid4().hex
    paths=[ctx['combined_source'],ctx['cluster_map'],ctx['manifest'],'translations/chapter10-th.json','qa/active-working-set.json','qa/final-parts/latest.json','reference/chapter10-source.json','reference/chapter10-templates.json','reference/chapter10-scope.json']
    paths += [str(p.relative_to(W)) for p in (W/'translations/chapter10').glob('*.json')]
    for rel in paths:
        dest=snap/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,dest)
    write(Q+'current.json',dict(snapshot=str(snap),active=ctx,protected=fingerprint()))

def scan():
    ctx=read('qa/active-working-set.json');now=read(ctx['combined_source']);corpus=read('reference/rebirth-jp-corpus.json');rows=[]
    for a,d in corpus.items():
        e=now['assets'].get('End/Content/Text/JP/'+a,{}).get('entries',{})
        for k,v in d.items():
            if v['Text'] and re.search('[\u3040-\u30ff\u3400-\u9fff]',v['Text']) and k not in e:
                rows.append(dict(asset=a,id=k,jp=v['Text'],actor=v.get('MetaData',{}).get('ACTOR','')))
    write(Q+'independent-residual-scan.json',rows)
    resident=[r for r in rows if r['asset']=='Resident_TxtRes.uasset']
    print('Resident remaining Japanese',len(resident))
    for r in resident:
        if r['id'].startswith(('$CHADL_QST_05_','$C3010_','$WORLD_PCV_','$PIANO_QST_01_','$WORLD_CDV_01_')):
            print(r['id'],r['actor'],r['jp'].replace('\r\n',' / '))
    print('Other assets with Cosmo main/shared content keys:')
    for r in rows:
        if r['asset'] not in ['Resident_TxtRes.uasset','8600-COSME_TxtRes.uasset'] and r['id'].startswith(('$C2910_','$C3010_','$CHADL_QST_05_','$COSME_QST_','$CSMOC_NPC_')):
            print(r['asset'],r['id'],r['jp'])

def lines(start,end):
    ts=read('reference/chapter10-templates.json');from assemble_chapter10 import values
    vals=values()
    for t in ts[start:end]:print(t['index'],t['actor'],t['jp'].replace('\r\n',' / '),'=>',vals[str(t['index'])].replace('\r\n',' / '))

def related():
    for r in read(Q+'independent-residual-scan.json'):
        if r['asset']=='Resident_TxtRes.uasset' and r['id'].startswith(('$WORLD_CDV_02_','$WORLD_CDV_03_','$WORLD_MGV_','$WORLD_QST_','$CHADL_QST_03_','$CHADL_QST_04_','$PHOTO_QST_00_')):
            print(r['id'],r['actor'],r['jp'].replace('\r\n',' / '))

def foreign():
    rows=read(Q+'independent-residual-scan.json')
    for r in rows:
        if r['asset']=='8800-FOREE_TxtRes.uasset' and r['id'].startswith('$CHADL_'):
            print(r['asset'],r['id'],r['actor'],r['jp'].replace('\r\n',' / '))

def inventory():
    from chapter10_recheck_scope import extra
    before=read(Q+'current.json');old=read(Path(before['snapshot'])/before['active']['combined_source']);c=read('reference/rebirth-jp-corpus.json');out=[];us={}
    for a,d in c.items():
        for k,v in d.items():
            why=extra(a,k)
            if not why or not v['Text'] or k in old['assets'].get('End/Content/Text/JP/'+a,{}).get('entries',{}):continue
            if a not in us:us[a]=txtres.parse(str(W/'source/End/Content/Text/US'/a))
            r=dict(asset='End/Content/Text/JP/'+a,id=k,Japanese=v,English=us[a][k],reason=None,family=why,template='recheck-'+str(len(out)));out.append(r)
    p=W/'reference/chapter10-recheck-source.json'
    if p.exists():
        previous=read(p);indexed={(r['asset'],r['id']):r for r in previous};current={(r['asset'],r['id']):r for r in out}
        assert indexed.keys()<=current.keys()
        for key,r in indexed.items():assert {k:v for k,v in r.items() if k!='template'}=={k:v for k,v in current[key].items() if k!='template'}
        additions=[r for r in out if (r['asset'],r['id']) not in indexed]
        for r in additions:r['template']='recheck-'+str(len(previous));previous.append(r)
        out=previous
    write(p,out)
    print('Newly found:',len(out),Counter(r['family'] for r in out))
    for i,r in enumerate(out):
        if '--appended' in sys.argv and i<118:continue
        print(i,r['id'],r['English'].get('MetaData',{}).get('ACTOR',''),r['Japanese']['Text'].replace('\r\n',' / '),'|US',r['English']['Text'].replace('\r\n',' / '))

def terms():
    before=read(Q+'current.json');old=read(Path(before['snapshot'])/before['active']['combined_source']);c=read('reference/rebirth-jp-corpus.json')
    for term in ['ワイズ','レジー','ナバラ','ゴールドソーサー','マルケ']:
        found=[]
        for a,p in old['assets'].items():
            for k,t in p['entries'].items():
                if term in c[Path(a).name][k]['Text'] and (not a.endswith('Resident_TxtRes.uasset') or k.startswith(('$CARDG_','$WORLD_'))):found.append((k,t))
        print(term,found[:5])

def revise():
    fixes={
      '174':'ใช่เลย ช่วงนี้\r\nสตูมาร์เคจืดชืดไปหน่อยนะ',
      '304':'สตูมาร์เคมาแล้ว\r\nความหวานกับเครื่องเทศที่เข้ากันลงตัว',
      '634':'การที่หัวใจรู้สึกซาบซึ้งเป็นเรื่องดี\r\nพลังเช่นนั้นของพิธีส่งวิญญาณสู่ดวงดาวช่างวิเศษนัก',
      '818':'อืม เข้าใจแล้ว',
      '900':'รู้สึกอึดอัดในอกแปลกๆ แฮะ',
      '916':'ท้องฟ้าแตกออก ผืนดินแยกออก\r\nทะเลหายไป กาลเวลาปั่นป่วน',
      '1241':'สรุปก็คือ เรื่องที่ว่าเวดจ์ไม่มีประโยชน์──',
      '1268':'คนที่ยังไม่มีความมุ่งมั่น\r\nก็มีประโยชน์น้อยกว่าก้อนหินเสียอีก',
    };ts=read('reference/chapter10-templates.json');assert 'マルケ' in ts[304]['jp']
    for p in (W/'translations/chapter10').glob('batch-*.json'):
        vals=read(p)
        for k,t in list(vals.items()):
            vals[k]=fixes.get(k,t).replace('ศาสตร์แห่งชีวิตดวงดาว','ศาสตร์ชีวิตดวงดาว').replace('พิธีส่งคืนสู่ดวงดาว','พิธีส่งวิญญาณสู่ดวงดาว').replace('วันส่งคืนสู่ดวงดาว','วันส่งวิญญาณสู่ดวงดาว').replace('คืนส่งคืนสู่ดวงดาว','คืนส่งวิญญาณสู่ดวงดาว')
        write(p,vals)
    p='translations/chapter10-recheck-lines.json';v=read(p)
    v['recheck-96']=v['recheck-96'].replace('นาวาลัน','นาบารา');v['recheck-108']=v['recheck-108'].replace('เรจินา','เรจี้')
    write(p,v)
def snapshotstage():
    before=read(Q+'current.json');snap=Path(before['snapshot']);dest=snap/'stage';ctx=before['active'];assert not dest.exists()
    from audit_chapter10 import digest
    manifest=read(snap/ctx['manifest'])
    for rel,h in manifest.items():assert digest(W/ctx['stage']/rel)==h,rel
    shutil.copytree(W/ctx['stage'],dest);print('Saved verified27asset pre-recheck stage')

def quality():
    now=read('translations/working-through-chapter10-th.json');src=read('reference/rebirth-jp-corpus.json');p=read('translations/chapter10-th.json');anchors={'クラウド':['คลาวด์'],'エアリス':['เอริธ'],'ティファ':['ทีฟ่า'],'バレット':['บาร์เร็ต'],'ザックス':['แซ็ก'],'ケット・シー':['เค็ตชี'],'アバランチ':['อวาแลนช์'],'ウータイ':['อู่ไถ'],'ゴンガガ':['กอนกาก้า'],'マルケ':['มาร์เค'],'魔晄':['มาโก้'],'マテリア':['แมทีเรีย'],'ソルジャー':['โซลเจอร์'],'セフィロス':['เซฟิรอธ'],'ジェノバ':['เจโนวา']};flags=[];lines=0
    for a,v in p['assets'].items():
        for k,t in v['entries'].items():
            lines+=1;j=src[Path(a).name][k]['Text']
            for jp,th in anchors.items():
                if jp in j and not any(word in t for word in th):flags.append(dict(asset=a,id=k,jp=j,thai=t,term=jp))
    write(Q+'terminology-candidates.json',flags);print('All',lines,'new/reviewed speech records screened; terminology candidates',len(flags))
    for r in flags:print(r['id'],r['term'],r['jp'].replace('\r\n',' / '),'=>',r['thai'].replace('\r\n',' / '))

if __name__=='__main__':
    if '--prepare' in sys.argv:prepare()
    elif '--lines' in sys.argv:lines(int(sys.argv[-2]),int(sys.argv[-1]))
    elif '--related' in sys.argv:related()
    elif '--foreign' in sys.argv:foreign()
    elif '--inventory' in sys.argv:inventory()
    elif '--terms' in sys.argv:terms()
    elif '--revise' in sys.argv:revise()
    elif '--snapshot-stage' in sys.argv:snapshotstage()
    elif '--quality' in sys.argv:quality()
    else:scan()
