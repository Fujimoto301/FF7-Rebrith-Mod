"""Review/save manually translated normalized descriptions; preserve runtime tokens."""
import json, re, sys
from pathlib import Path
W = Path(__file__).resolve().parents[1]
rows = json.loads((W/'reference/inventory-templates.json').read_text('utf-8'))
if sys.argv[1] == 'show':
    for row in rows[int(sys.argv[2]):int(sys.argv[3])]:
        print(row['index'], row['jp'].replace('\r\n',' / '))
        if '--en' in sys.argv: print(' EN:',row['en'].replace('\r\n',' / '))
else:
    out = {}
    for line in sys.stdin.read().splitlines():
        if not line.strip(): continue
        n,t = line.split('|',1); n=int(n);t=t.replace('\\n','\r\n')
        assert n not in out and t.strip(),n
        src=rows[n]['jp']
        if sys.argv[1]=='savebody' and '\r\n\r\n' in src:
            tail=src[src.index('\r\n\r\n'):]
            translations={
                '連携相手とコマンド名:':'คู่ร่วมท่าและชื่อคำสั่ง:',
                '連携相手:':'คู่ร่วมท่า:',
                'バースト中のヒット効果:':'ผลเมื่อโจมตีโดนศัตรูที่สแตกเกอร์:',
                'ヒット効果:':'ผลเมื่อโจมตีโดน:', '使用効果:':'ผลเมื่อใช้:',
                'リミット技Lvアップ':'เพิ่มระดับท่าลิมิต',
                '一定時間ATBゲージが{n0}段階に増加':'เพิ่มเกจ ATB เป็น {n0} ส่วนชั่วคราว',
                '一定時間MP消費なし':'ไม่ใช้ MP ชั่วคราว',
                '威力アップ&バースト時間延長':'เพิ่มความรุนแรงและยืดระยะเวลาสแตกเกอร์',
                'ビートヒット(物理攻撃)':'Bullet Batter (โจมตีกายภาพ)',
                'ハウルスマッシュ(魔法攻撃)':'Howling Smash (โจมตีเวท)',
                'インテンスブレイク(物理攻撃)':'Power Cleave (โจมตีกายภาพ)',
                'マギアブレイク(魔法攻撃)':'Spell Blade (โจมตีเวท)',
                '摩天翔(遠距離攻撃)':'Soaring Flurry (โจมตีระยะไกล)',
                '天昇撃(打ち上げ攻撃)':'Heavenly Ascent (โจมตีเสยขึ้น)',
                '※『忍術変化』で属性が変わります。':'※ธาตุเปลี่ยนตาม Elemental Ninjutsu',
            }
            for a,b in translations.items(): tail=tail.replace(a,b)
            t+=tail
        token=lambda s: sorted(re.findall(r'<[^>]+>|\{n\d+\}',s))
        assert token(t)==token(src),(n,token(src),token(t))
        assert not re.search(r'[\u3040-\u30ff\u3400-\u9fff]',t),n
        out[str(n)]=t
    p=W/'translations/inventory'/sys.argv[2];p.parent.mkdir(parents=True,exist_ok=True)
    assert not p.exists(),str(p)
    p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
    print('Saved',p.name,len(out))
