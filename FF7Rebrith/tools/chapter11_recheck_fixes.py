"""Reviewed contextual revisions; no blanket pronoun or repeated-word replacement."""
from pathlib import Path
from prepare_chapter9 import W,read,write,txtres
from chapter11_recheck import Q,decisions
FIXES={
55:('ปัจจุบันเป็นสถานพักฟื้นสำหรับผู้มีภาวะเป็นพิษจากมาโก้','Use established mako-poisoning terminology.'),
80:('เรื่องแบบนั้น……ฉันไม่มีทางทำหรอก','するはずない denies doing it; it does not express inability.'),
117:('ตอนนั้นฉันพอจะช่วยได้บ้างไหม?','Asks whether Cloud helped Tifa after their reunion; past help, not a new offer.'),
130:('ฉันเป็นเด็กเรื่องมาก ตัวเองก็คิดอย่างนั้น','面倒くさいガキ describes a troublesome child, not a difficult task.'),
147:('ภาวะเป็นพิษจากมาโก้สินะ','Preserve the established condition name.'),
154:('นั่นไม่ใช่รอยจากการรักษาภาวะเป็นพิษจากมาโก้เหรอ?','Keep the chef’s question and established condition name.'),
300:('กว่าจะก่อตัวได้ถึงขั้นนี้ตามธรรมชาติ\r\nต้องใช้เวลานานแค่ไหนกันนะ','ここまで refers to materia formation, not only physical size.'),
345:('สำหรับคนที่ตายไปแล้ว จะยังไงก็ไม่ต่างกันหรอก','Connect to the preceding ceasefire question: dead people are unaffected by its status.'),
348:('พวกเขาเริ่มลงมือแล้ว……สงครามเริ่มแล้วสินะ','Preserve active 始めた then intransitive 始まった in Yuffie’s reaction.'),
404:('เคยได้ยินว่าดอกเตอร์โฮโจ\r\nใช้ที่นี่ทดลองครับ','Consistent spelling with other Hojo dialogue.'),
405:('คงไม่ใช่เรื่องดีแน่ๆ','ロクでもねえ reacts to Hojo’s experiments being sinister, not merely useless.'),
488:('จะช่วยด้วยใช่ไหม?','Barret asks Aerith, whose affirmative reply follows; remove the male addressee นาย.'),
558:('ใครเป็นฝ่ายถูกกันแน่','道理 challenges who is in the right before 私かおまえか, not general intelligence.'),
648:('นั่นสิ เจอเรื่องโหดร้ายขนาดนี้ด้วยนี่นา','Keep present suffering in the discussion of the robes’ lack of conscious thought.'),
709:('คนชุดคลุมดำ～ไล่ตามฉัน～','Deliberate inversion of previous lyric: I follow robes / robes follow me. The preceding followers context also supports the inverse subject.'),
732:('พวกชุดคลุมดำกับเซฟิรอธเกี่ยวข้องกัน','Render 無関係じゃない clearly as a connection; next line intensifies it.'),
843:('จะว่าคนแก่ธรรมดาก็ไม่ใช่\r\nตาคนนี้แก่สุดๆ เลยต่างหาก','Respond to the just-an-old-man choice without the ambiguous phrase ตาธรรมดา.'),
953:('เปล่า แค่ของที่ข้าเสพเพื่อความเพลิดเพลินน่ะ','嗜好品 is not necessarily a beverage; later 吸う explicitly refers to smoking.'),
984:('เอาเถอะ แข่งอีกสักไม่กี่ครั้ง\r\nก็คงจะคุ้นเคยเอง','何度か means a few times, not the interrogative สักกี่ครั้ง.'),
991:('นั่นแสดงว่าเรื่องของโจโกโบะ\r\nยังมีอะไรให้เรียนรู้อีกมาก','奥が深い concerns depth of knowledge, not a literally profound creature.'),
1006:('ข้าเลยจำใจ\r\nโยนงานจิปาถะให้ทำไปตามเรื่อง นั่นแหละจุดเริ่มต้น','しかたがないので = having no choice; avoid sounding unable to help.'),
1021:('ข้าจึงคิดจะให้เวลาเจ้าปล่อยวางความแค้น\r\nแล้วกลับมาทบทวนตัวเองอีกครั้งเสียก่อน','邪念 here is Billy’s revenge fixation, as the following hatred/avenging dialogue confirms.'),
1091:('ฮึๆ ฉันชื่อคริสทีน\r\nเป็นหัวหน้าครัวของที่นี่','料理長 is a gender-neutral occupation; avoid introducing พ่อครัว as gender evidence.'),
1121:('ทั้งที่ฉันเป็นคนได้แมวมา\r\nแต่พ่ออาจจะเป็นฝ่ายที่รักเจ้าเหมียวมากกว่าก็ได้','Compare father’s and Tifa’s affection for the cat; avoid implying father loved the cat more than his daughter.'),
1187:('ค่อยๆ กลับเข้าจังหวะได้นะ','持ち直せる is encouragement to recover during the piano performance.'),
1190:('ขอโทษนะ ฉันมั่นใจเกินไปหน่อย','Bad-performance branch: 調子に乗った is getting overconfident, not merely playing for too long.'),
1352:('ตั้งแต่มาอยู่ที่นี่\r\nทุกคนก็มีสุขภาพดีกันนะ','Natural Thai rendering of living healthily.'),
1365:('ได้ยินเสียงแมวครางเบาๆ ใช่ไหม?\r\nแปลว่ามีความสุข กำลังบอกว่าขอบคุณอยู่นะ','ゴロゴロ is contented purring, not labored breathing.'),
1419:('ถ้าหาหัวหน้าครัวคริสทีน\r\nอยู่ที่ชั้น 2 นะ','Use the same gender-neutral job title.'),
1435:('เพราะหัวหน้าครัว\r\nเลยทำงานอย่างสนุกทุกวันเลย!','Use the same gender-neutral job title.'),
1436:('ฉันก็อยากเป็นคนสบายๆ ไม่คิดมาก\r\nได้ทุกที่ทุกเวลาเหมือนหัวหน้าครัวบ้างจัง','おおらか describes an easygoing demeanor; keep the occupation neutral.'),
1481:('โลหิต……ดำ……\r\nราชินี……แม่มด……','Match existing spoken ราชินีโลหิตดำ terminology; เงา was inconsistent.'),
1510:('หรือว่านาย……ว่างงานอยู่?','無職 means unemployed, without asserting a recent job loss.'),
1520:('ฉันเห็นภาพผลงานของคุณ\r\nเดินทางไปทั่วโลกเลย','Neutral first-person pronoun where no new speaker-sex evidence was established.'),
1528:('ฉันยื่นเรื่องจนขออนุญาตถ่ายภาพได้ในที่สุด','Same neutral first-person policy.'),
1531:('ถ้าเจอจุดถ่ายภาพดีๆ\r\nก็บอกด้วยนะ','He asks the player to recommend a spot, not to find an already recommended one.'),
1532:('เป้าหมายของฉันก็คือเขานิเบิลลูกนั้น','Same neutral first-person policy.'),
1536:('หาจุดถ่ายภาพดีๆ\r\nให้แล้วสินะ ขอบคุณมาก','Acknowledge the player’s recommendation naturally.'),
1541:('แถวนี้มีอาคารที่เรียกว่าคฤหาสน์ชินระอยู่\r\nแต่มีแค่ที่นั่นที่ฉันไม่ได้รับอนุญาตให้ถ่ายภาพ','Same neutral first-person policy.'),
1581:('เพื่อก้าวข้ามดอกเตอร์โฮโจ\r\nผมอาจลองทำวิจัยที่นี่ดูก็ได้นะครับ','Chadley proposes his own research, not that Cloud should become a researcher.'),
1594:('จะช่วยเสริมความสามารถ\r\nในการให้คำแนะนำของฉันให้ดียิ่งขึ้นค่ะ!','MAI means combat guidance, not geographic navigation.'),
1625:('จากนี้จะเริ่มให้คำแนะนำค่ะ','Natural Thai word order; apply to all five same-context guidance-start lines.')
}
UI={
'$C3110_MAIN_0800_1700_00_sys':('ก็เคยอยู่','Affirm Aerith’s question about watching Tifa from the tower; original นั่นสิ is vague.'),
'$C3110_MAIN_0800_1900_00_sys':('อย่ามาล้อกันสิ','Aerith is teasing, and Cloud’s voiced answer uses the same sense; no claim that she looks down on him.'),
'$C3110_MAIN_1800_0500_00_sys':('ไม่ต้องใส่ใจหรอก','Reassure Red about apologizing for badmouthing the hometown, matching the voiced answer.')
}
def main():
    assert not decisions(),'Preserve this reviewed correction ledger'
    b=read(Q+'baseline.json');old=read(Path(b['snapshot'])/b['active']['combined_source']);rows=[]
    for r in read('reference/chapter11-source.json'):
        if r['template'] not in FIXES:continue
        t,reason=FIXES[r['template']];a,k=r['asset'],r['id'];before=old['assets'][a]['entries'][k];assert before!=t
        rows.append(dict(asset=a,id=k,template=r['template'],Japanese=r['Japanese'],English=r['English'],before=before,after=t,reason=reason))
    a='End/Content/Text/JP/8700-NIBLE_TxtRes.uasset';jp=txtres.parse(str(W/'source'/a));us=txtres.parse(str(W/'source'/a.replace('/JP/','/US/')))
    for k,(t,reason) in UI.items():rows.append(dict(asset=a,id=k,template='existing-UI',Japanese=jp[k],English=us[k],before=old['assets'][a]['entries'][k],after=t,reason=reason))
    write('reference/chapter11-recheck-overrides.json',dict(records=rows,scope='Explicit Ch11 source IDs only; previous Ch1–10 unchanged except these three previously translated Ch11 choice labels.'))
    print('Recorded',len(rows),'exact contextual corrections')
if __name__=='__main__':main()
