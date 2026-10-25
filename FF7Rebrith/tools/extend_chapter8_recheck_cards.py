"""Append the independently discovered Card Challenge family; never reindex existing work."""
import re
from chapter8_supplement import W,R,read,write,txtres,family,name

def main():
    rows=read('reference/chapter8-supplement-source.json');ts=read('reference/chapter8-supplement-templates.json')
    auto=read('translations/chapter8-supplement-automatic.json');manual=read('translations/chapter8-supplement-manual.json')
    existing={r['id'] for r in rows};base=read('translations/working-through-chapter7-th.json')['assets'][R]['entries']
    c=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset'];us=txtres.parse(str(W/'source'/R.replace('/JP/','/US/')))
    support='การท้าประลองไพ่ที่เพิ่มการ์ดสนับสนุนให้เมื่อเริ่มเล่น\r\n\r\n'
    board='การท้าประลองไพ่บนกระดานที่มีกติกาพิเศษ\r\n\r\n'
    details={
      '01':support+'เพิ่มการ์ด Gigantuar ที่มีสกิลเพิ่มระดับช่องในแดนของคุณ\r\nเข้ามาในมือ ใช้การ์ดระดับสูงได้ตั้งแต่ต้นเกม\r\nแล้วคว้าชัยในการประลองอันดุเดือดนี้',
      '02':support+'เพิ่มการ์ด Cactrot ที่มีสกิลเพิ่มพลังเข้ามาในมือ\r\nเสริมความแข็งแกร่งให้การ์ดไม้ตายของคุณ\r\nแล้วกวาดล้างคู่ต่อสู้',
      '03':board+'เริ่มเกมโดยสลับแดนของคุณกับคู่ต่อสู้\r\nระวังอย่าสับสน ใช้การ์ดโจมตีด้านหลังที่ปกติใช้ได้ยาก\r\nแล้วสนุกกับการสวมบทเป็นฝ่ายตัวร้าย',
      '04':support+'เพิ่มการ์ด Chadley ที่มีสกิลวางทับการ์ดฝ่ายเดียวกัน\r\nเข้ามาในมือ ใช้การวิเคราะห์อันแม่นยำ\r\nคิดว่าจะวางลงตรงไหนและเมื่อไร',
      '05':board+'เริ่มประลองโดยมี Polygonal Ifrit วางอยู่กลางกระดาน\r\nIfrit จะเพิ่มพลังอย่างมากให้การ์ดบนช่องเอฟเฟกต์พิเศษรอบตัว\r\nไม่ว่าจะเป็นฝ่ายเดียวกันหรือคู่ต่อสู้ อย่ากลัวเปลวเพลิง\r\nจงลุยเข้าไปแล้วจุดไฟแห่งชัยชนะ',
      '11':board+'เริ่มประลองโดยช่องในแดนมีระดับสูงตั้งแต่แรก\r\nส่งการ์ดระดับสูงลงสนามตั้งแต่ต้นเกม บุกเข้าแดนคู่ต่อสู้\r\nแล้วคว้าชัยในการต่อสู้อันดุเดือด',
      '12':support+'เพิ่มการ์ด MAI ที่มีสกิลวางทับการ์ดฝ่ายเดียวกันเข้ามาในมือ\r\nเธอจะแสดงความสามารถเหนือกว่า Chadley ได้หรือไม่\r\nมาพิสูจน์ฝีมือของเธอกัน',
      '13':board+'เริ่มประลองโดยแดนของคุณอยู่ตรงกลางและถูกคู่ต่อสู้ขนาบทั้ง 2 ด้าน\r\nเสริมการป้องกันทั้ง 2 ฝั่งเพื่อต้านการบุกอันรุนแรง\r\nพร้อมหาทางหลุดพ้นจากสถานการณ์คับขัน',
      '14':board+'เริ่มประลองโดยแดนทั้ง 2 ฝ่ายหันเข้าหากันจากด้านบนและด้านล่าง\r\nAlexander ที่วางอยู่ในแดนของแต่ละฝ่ายจะมีพลังเพิ่มขึ้น\r\nตามจำนวนการ์ดฝ่ายเดียวกันที่ถูกลดพลัง\r\nวางแผนใช้ความได้เปรียบของกระดานที่แผ่ออกด้านข้าง\r\nแล้วเลือกวางการ์ดให้เหมาะสม',
      '15':board+'เริ่มประลองโดยมีช่องในแดนตั้งต้นน้อยกว่าปกติ\r\nใช้กลยุทธ์อย่างการบุกไปยังช่องเพิ่มพลังอันทรงพลัง\r\nรอบ Polygonal Ifrit ที่อยู่กลางกระดาน\r\nแม้ตกอยู่ในสถานการณ์ลำบาก ก็จงตัดสินใจอย่างสุขุม\r\nและคว้าชัยด้วยจิตใจนักสู้อันเร่าร้อน',
      '21':'การท้าทายเอาตัวรอดระดับต้น แข่ง 3 รอบเพื่อสะสมคะแนนรวม\r\nหากชนะ จะได้รับรางวัลตามระดับคะแนนรวม\r\n\r\n<color=yellow-black>《กติกาการท้าทายเอาตัวรอด》\r\n- เพิ่มการ์ดสนับสนุนให้เมื่อเริ่มรอบที่ 1\r\n- จั่วการ์ดจากเด็คเพียง 5 ใบเมื่อเริ่มแต่ละรอบ\r\n- จั่วการ์ดจากเด็คระหว่างรอบไม่ได้</color>',
      '22':'การท้าทายเอาตัวรอดระดับกลาง แข่ง 3 รอบเพื่อสะสมคะแนนรวม\r\nหากชนะ จะได้รับรางวัลตามระดับคะแนนรวม\r\n\r\n<color=yellow-black>《กติกาการท้าทายเอาตัวรอด》\r\n- เพิ่มการ์ดสนับสนุนให้เมื่อเริ่มรอบที่ 1\r\n- จั่วการ์ดจากเด็คเพียง 5 ใบเมื่อเริ่มแต่ละรอบ\r\n- จั่วการ์ดจากเด็คระหว่างรอบไม่ได้</color>',
      '23':'การท้าทายเอาตัวรอดระดับยากที่สุด แข่ง 5 รอบ\r\nหากชนะ จะได้รับรางวัลตามระดับคะแนนรวม\r\n\r\n<color=red>《กติกาการท้าทายเอาตัวรอดระดับยากที่สุด》\r\n- ตั้งแต่รอบที่ 4 เป็นต้นไป จะจั่วการ์ดจากเด็คไม่ได้\r\n- เพิ่มการ์ดสนับสนุนให้เมื่อเริ่มรอบที่ 1\r\n- จนถึงรอบที่ 3 จั่วการ์ดจากเด็คเพียง 5 ใบเมื่อเริ่มแต่ละรอบ\r\n- จั่วการ์ดจากเด็คระหว่างรอบไม่ได้</color>',
    }
    ix={(r['family']=='speech',r['jp']):r['index'] for r in ts};added=[]
    for k,v in c.items():
        f=family(k)
        if k in existing or not f or not v['Text']:continue
        row=dict(asset=R,id=k,Japanese=v,English=us.get(k,{}),family=f,mode='existing' if k in base else 'translate')
        if k not in base:
            if name(k,f):auto[k]=us[k]['Text'];row['mode']='official_English_name'
            else:
                if k.endswith('_Detail'):t=details[k.split('_')[2]]
                elif k.endswith('_Jenre'):t={'ゴールドソーサー初級':'Gold Saucer ระดับต้น','ゴールドソーサー上級':'Gold Saucer ระดับสูง','サバイバルチャレンジ':'การท้าทายเอาตัวรอด'}[v['Text']]
                elif '_Condition_Rank_' in k:
                    tag=re.search('<button=[^>]+>',v['Text']).group();rank=us[k]['Text'].split(': ',1)[1]
                    t=f'นักประลองระดับ {tag} {rank} ขึ้นไป'
                elif '_Condition' in k:t='ผ่าน '+us[k]['Text'].removeprefix('Complete ')
                elif k=='$keyitem_CoupleTicket_help':t='ตั๋วคู่สำหรับค่ำคืนพิเศษในสวรรค์สีทอง\r\nใช้ชมละคร LOVELESS และนั่งกระเช้าลอยฟ้าได้'
                elif k=='$keyitem_GoldTicket_help':t='บัตรผ่านพิเศษที่ใช้เข้า Gold Saucer ได้ไม่จำกัดจำนวนครั้ง'
                else:raise AssertionError(k)
                key=(False,v['Text'])
                if key not in ix:
                    ix[key]=len(ts);ts.append(dict(index=len(ts),jp=v['Text'],family=f,examples=[],us=us[k]['Text'],actors=[]))
                i=ix[key];row['template']=i;ts[i]['examples'].append(k)
                assert str(i) not in manual or manual[str(i)]==t,(k,'shared template context')
                manual[str(i)]=t
            added.append(k)
        rows.append(row)
    write('reference/chapter8-supplement-source.json',rows);write('reference/chapter8-supplement-templates.json',ts)
    write('translations/chapter8-supplement-automatic.json',auto);write('translations/chapter8-supplement-manual.json',manual)
    report=read('qa/chapter8/recheck-additions.json');report['card_challenge_and_ticket_UI_added']=added
    write('qa/chapter8/recheck-additions.json',report)
    print('Added',len(added),'new UI rows;',len(rows),'inventory;',len(ts),'stable templates')

if __name__=='__main__':main()
