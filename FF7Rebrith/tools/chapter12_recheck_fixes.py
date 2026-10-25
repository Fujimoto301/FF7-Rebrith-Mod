"""One-shot exact corrections from the second complete Japanese/Thai read."""
from prepare_chapter9 import W,read,write
from assemble_chapter12 import values
Q='qa/chapter12/recheck/'
def main():
    assert not (W/'reference/chapter12-recheck-overrides.json').exists(),'Already recorded; do not recreate historical review'
    vals=values();ts=read('reference/chapter12-templates.json');fix={
      0:('เอริธน่ะ เดี๋ยวฉันดูแลเองนะ','Elmyra tells Zack she will tend to Aerith; Aerith is the topic, not the person being addressed.'),
      49:('กลับมาให้ทันมื้ออาหารล่ะ','JP食事 does not specify dinner.'),
      311:('ได้เวลาเริ่มการแสดงแล้ว~!','Natural show-start announcement.'),325:('จบการแสดงแล้ว~ เหนื่อยหน่อยนะ','Natural show-end announcement.'),
      475:('จะคัมภีร์หรือนักดาบอะไรนั่นก็ช่าง','Preserve dismissive mispronunciation without a nonsensical Thai word.'),
      600:('พอแค่นั้นแล้ว ยกโทษให้หลานฉันเถอะ พ่อนักรับจ้าง','Mireille asks Cloud to stop pressing Kyrie and forgive her; not forgive to that extent.'),
      723:('เอริธตอบรับอย่างเต็มใจเสมอเลยนะ','返事がいい refers to her enthusiastic acceptance.'),
      812:('ต้องคอยเดินให้ช้าลงตามทุกคน\r\nช่วงนี้ร่างกายเลยไม่ค่อยได้ออกแรง','Red adjusts his pace down to the party; previous keep-up wording reversed the implication.'),
      917:('จะอ่านหรือเปล่านะ...','Keep Aerith tentative about reading; avoid an unsupported explicit addressee.'),
      1054:('ขอบคุณสำหรับอาหาร~\r\nข้าอิ่มแปล้แล้ว!','Garm retains the theatricalข้า register used in his other lines.'),
      1066:('หรือความคำนึงถึงสหายที่เคยแยกทางกัน\r\nจะเป็นสิ่งที่ยังพอค้ำจุนเขาไว้ได้','かろうじて means barely managing, not faint/indistinct.'),
      1121:('<i>ถูกเสียงฝีเท้าเร่งรีบเร่งเร้า</i>','足音 means sound of footsteps, not footprints.'),
      1189:('คลาวด์ ขึ้นมาสิ','Tifa invites him aboard; natural request rather than a question mark attached to imperative.'),
      1268:('แต่ทั้งหมดก็เป็นแค่การหลอกเด็กจริงๆ นั่นแหละ','Keep the literal child-tricking joke in natural Thai.'),
      1298:('เดตแรกของเราไปสวนสนุกกันน่ะ','He recalls a different travelling amusement park; นี่แหละ wrongly implied this location.'),
      1334:('ถึงอยากสนใจ ก็ไม่รู้จะสนใจยังไง','気にしようがない: cannot attend to unknowable fate, rather than inability to act on it.'),
      1542:('ปล่อยไปเถอะ ที่สำคัญกว่านั้น...','Shift attention from Rufus to Cait Sith, not the literal ยิ่งกว่านั้น.'),
      1739:('ล็อกผลแข่งเหรอ? ไร้สาระ','八百長 means race-fixing; ล้มแข่ง is unclear.'),
      1759:('แต่เรื่องนี้เด็กยังไม่ควรรู้\r\nรอให้โตก่อนแล้วค่อยฟังความจริงเถอะ','まだ早い concerns maturity, not a child listening quickly.'),
      1900:('เท่านี้คุณก็ก้าวแรก\r\nสู่การเป็นนักเที่ยวได้แล้ว','Complete the sentence with the attained-step predicate.'),
      1945:('เพราะมีแต่ผมที่ยืนปกป้องลูกน้อง\r\nแล้วต่อกรกับเบื้องบนได้','He stands up for his subordinates against management, rather than merely standing in front of them.'),
      2438:('เลือกขุดตำนานผิดเรื่องเข้าแล้วสินะ','Vincent comments on the ill-fated legend chosen, not simply that the legend is evil.'),
      2517:('หมายถึงฉันทำทีเหมือนมีใจ\r\nเพื่อเรียกร้องความสนใจจากนายเหรอ?','Cissnei playfully interprets suggestive behavior as flirtation before Cloud clarifies that she seems to know him.'),
      2535:('เฮ้อ ทำอะไรไม่ได้เลย','無力 here is feeling powerless to affect world events.'),
      2560:('ขออภัยที่เสียมารยาท\r\nฉันชื่อเมฟ เป็นนักเขียนหนังสือภาพ','Natural apology/introduction.'),
      2651:('ตอนที่ได้ยินข่าวลือว่าชินระวางแผนทำลายเขต7\r\nพูดตรงๆ ว่าฉันยังไม่ค่อยเชื่อ','Restore the heard-rumor verb.'),
      2865:('ที่นี่เป็นบ้านเกิดคุณใช่ไหม\r\nอยากให้สงบลงเร็วๆ นะ','A hometown remains a hometown; remove unsupported formerly.'),
      2954:('มอนสเตอร์ก็เติบโต และมีความคิดความรู้สึกด้วย','精神活動 in this explanation is mental/emotional life, not awkward กิจกรรมทางจิตใจ.'),
      2955:('หากต้องอยู่กับสภาพอันเกินทน ก็อาจร้องเพลงคร่ำครวญ\r\nอาจเป็นแบบนั้นก็ได้','Natural statement preserving the hypothetical emotional explanation.'),
      3064:('นี่มันเอ็กซ์คาลิ『พัวร์』!','The same-ID official name is Excalipoor; preserve the emphasized differing syllable.'),
      3140:('ฝีมือนายตอนนี้ยังไม่พอ\r\nไปเพิ่มฝีมือให้มากกว่านี้ก่อน','いまの君ではダメ is insufficient skill, not the incomplete ยังไม่ได้.'),
      3141:('มาแล้วสินะ คลาวด์','よくきた is welcome, not came well.'),
      3208:('บอกว่า『จงปล่อยตัวไปตามอำนาจ แล้วครอบงำทุกสิ่ง』','Entrust oneself to power, not hand oneself in.'),
      3338:('จากนี้ก็ขอให้นิ้วมือของท่าน\r\nบรรเลงเสียงอันงดงามต่อไปด้วยนะ','その指 does not mean a pair of fingers.'),
      3473:('ก้อนน้ำที่ Terror of the Deep พ่นออกมา ใช้เยื่อน้ำหุ้มเหยื่อแล้วกักขังไว้','水の玉 is a water sphere; ลูกน้ำ suggests mosquito larvae.'),
      3586:('สิ่งมีชีวิตเทียมที่ฝ่ายวิทยาศาสตร์ชินระสร้าง ผลผลิตวิปลาสจากการหลอมรวมร่างทดลองรูปร่างมนุษย์กับรูปร่างสัตว์ ถูกกักในศูนย์วิจัยเตาปฏิกรณ์ใต้ทะเล แต่หลบหนีออกมาได้','人型/獣型 specify body forms, not necessarily actual human/animal origins.'),
      3630:('สัตว์กินพืชขนาดใหญ่ที่อาศัยในป่า มีร่างกายกำยำหุ้มหนังหนาและเขายักษ์2ข้าง ราวกับรถถังมหึมาที่พุ่งอาละวาด','Natural heavy runaway-tank metaphor; keep2 horns.'),
      3694:('โจมตีด้วยท่ารุนแรงเพื่อทำให้ติดHEAT แต่ขณะอยู่ใน Rogue Stance ต้องใช้ท่ารุนแรงโจมตีโดน2ครั้ง การขัดท่าประสานของเติร์กสก็ทำให้ติดHEATได้เช่นกัน','疾風スタイル official same action ID $bt_Elena_B_Support02 is Rogue Stance.'),
      3754:('ใช้การโจมตีรุนแรงให้ชะงัก เพื่อกระแทกมันออกจากโพรงและทำให้ติดHEAT','Make the enemy, rather than the player, the explicit object of knockback.'),
      3755:('โจมตีธาตุจุดอ่อน หรือใช้การโจมตีรุนแรงให้ชะงัก เพื่อกระแทกมันออกจากโพรงและทำให้ติดHEAT','Preserve alternate elemental condition; enemy is object of knockback.'),
      3777:('เมื่อHPต่ำกว่าระดับที่กำหนด จะเข้าใกล้แล้วพยายามใช้『Self-Destruct』ระเบิดตัวเอง ซึ่งสร้างความเสียหายแก่ศัตรูในระยะด้วย ใช้ท่ารุนแรงโจมตีให้มันกระเด็นไปข้างหน้าไกลๆ แล้วระเบิดได้','Explicitly knock the enemy forward; previous subject of กระเด็น was unclear.'),
      3840:('เปลี่ยนเป็นธาตุไฟ น้ำแข็ง หรือสายฟ้า โจมตีธาตุจุดอ่อนจนสร้างความเสียหายถึงระดับหนึ่งเพื่อทำให้ติดHEATและปลดธาตุ หากปลดไม่สำเร็จจะเรียกสิ่งมีชีวิตธาตุออกมา เมื่อครบ3ธาตุจะใช้『Tri-Disaster』','エレメント出現 describes manifested elemental beings; merely a type appearing was vague.'),
    }
    reasons={n:r for n,(_,r) in fix.items()};after={str(n):t for n,(t,_) in fix.items()}
    for k,t in vals.items():
        n=int(k);z=after.get(k,t)
        if 'ศัตรู้' in z:z=z.replace('ศัตรู้','ศัตรู');reasons.setdefault(n,'Correct ศัตรู้ spelling to ศัตรู.')
        if n in (3544,3660):z=z.replace('ฉันหน้าม้า','ผมหน้าม้า');reasons[n]='前髪 is hair/bangs; ฉัน was an incorrect pronoun substitution.'
        if 'แคคทัวร์' in z:z=z.replace('แคคทัวร์','แคคเตอร์');reasons.setdefault(n,'Canonical spoken Cactuar spelling in the prior chapters is แคคเตอร์.')
        if n in (1864,1939,2634):z=z.lstrip();reasons.setdefault(n,'Remove unintended leading space.')
        if z!=t:after[k]=z
    assert all(vals[k]!=z for k,z in after.items())
    rows=read('reference/chapter12-source.json');records=[]
    for r in rows:
        k=str(r['template'])
        if k in after:records.append(dict(asset=r['asset'],id=r['id'],template=r['template'],jp=r['Japanese']['Text'],before=vals[k],after=after[k],reason=reasons[int(k)]))
    for p in sorted((W/'translations/chapter12').glob('batch-*.json')):
        d=read(p);write(p,{k:after.get(k,t) for k,t in d.items()})
    write('reference/chapter12-recheck-overrides.json',dict(records=records,templates=len(after),source='Second complete JP/Thai template read; original release snapshot retained.'))
    write(Q+'progress.json',dict(read_ranges=[[0,3846]],total_templates=3847,reviewed_templates=3847,remaining_templates=0,complete=True,choices_reviewed=36,duplicate_contexts_checked=True,correction_templates=len(after),corrected_ids=len(records),new_full_video_audio_review=False,in_game_tested=False))
    print('Applied',len(after),'template corrections /',len(records),'IDs')
if __name__=='__main__':main()
