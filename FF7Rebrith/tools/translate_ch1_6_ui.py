"""Reviewed activity UI plus regional report/card description assembly."""
import re
from assemble_chapter6 import read,write,JP
from translate_ch1_6_reports import VALUES

def intel_title(en):
    labels={'Activation Intel':'ข้อมูลเปิดใช้งาน','Fiend Intel':'ข้อมูลปราบศัตรู',
      'Expedition Intel':'ข้อมูลสำรวจ','Divine Intel':'ข้อมูลอัญเชิญ','Phenomenon Intel':'ข้อมูลปรากฏการณ์',
      'Excavation Intel':'ข้อมูลขุดค้น','Chocobo Intel':'ข้อมูล Chocobo','Moogle Intel':'ข้อมูล Moogle',
      'Classified Intel':'ข้อมูลลับ','Fiend Sighting':'จุดพบศัตรู'}
    for x,y in labels.items():
        if en.startswith(x):return y+en[len(x):]
    return en

def main():
    values=dict(VALUES)
    values.update({
113:'<button=decide> จบเกม',114:'ยูนิต',115:'<button=square> ข้อมูล Materia โดยละเอียด',116:'<button=square> ข้อมูลยูนิต',117:'<button=L2> รายละเอียดยูนิต',118:'รายละเอียดยูนิต <button=R2>',119:'<button=decide> วาง',120:'<button=decide> ใช้',121:'<button=L3> ความยาก EASY <button=toggle-on>',122:'<button=L3> ความยาก EASY <button=toggle-off>',123:'<button=L1> รายละเอียดยูนิตฮีโร่',124:'<button=L1> <color=yellow>ส่งยูนิตฮีโร่ลงสนาม</color>',125:'<button=L2> รายละเอียดยูนิตกองกำลัง',126:'<button=L1> สลับเป็นยูนิตฮีโร่',127:'<button=L1> สลับเป็นยูนิตกองกำลัง',128:'ต้องการออกจาก Fort Condor หรือไม่?',129:'ได้เปรียบในการต่อสู้',130:'<button=decide-hold> แสดงรายละเอียด <button=options> เริ่มเกม',131:'เวลาที่เหลือ',132:'ลองใหม่',133:'<button=decide-hold> แสดงรายละเอียด <button=L1><button=R1> สลับฮีโร่ลงสนาม <button=L2><button=R2> สลับรูปขบวนกองกำลัง <button=options> เริ่มเกม',134:'<color=yellow>รูปขบวน: สมดุลรุกและรับ</color>',135:'<color=yellow>รูปขบวน: เน้นโจมตี</color>',136:'<color=yellow>รูปขบวน: เน้นป้องกัน</color>',137:'<color=yellow>รูปขบวน: ตั้งรับในป้อม</color>',138:'วินาที',139:'ต้องการเริ่ม Fort Condor หรือไม่?',140:'ยูนิตบอส',141:'กองทัพ Shinra',142:'ยูนิตกองกำลัง',143:'กองทัพ Condor',144:'ยูนิตฮีโร่',
145:'ต้องการวิเคราะห์ความรู้ของ Alexander หรือไม่?',146:'ต้องการวิเคราะห์ความรู้ของ Kujata หรือไม่?',147:'ยกเลิก',148:'ต้องการวิเคราะห์ความรู้ของ Bahamut Arisen หรือไม่?',149:'ต้องการวิเคราะห์ความรู้ของ Odin หรือไม่?',150:'ต้องการวิเคราะห์ความรู้ของ Phoenix หรือไม่?',151:'ต้องการวิเคราะห์ความรู้ของ Titan หรือไม่?',152:'วิเคราะห์',153:'<button=options> จบการวิเคราะห์',154:'<button=decide> เริ่มวิเคราะห์',155:'<button=decide> ลองใหม่',156:'วิเคราะห์ความรู้ของ Alexander แล้ว',157:'วิเคราะห์ความรู้ของ Kujata แล้ว',158:'วิเคราะห์ความรู้ของ Bahamut Arisen แล้ว',159:'วิเคราะห์ความรู้ของ Odin แล้ว',160:'วิเคราะห์ความรู้ของ Phoenix แล้ว',161:'วิเคราะห์ความรู้ของ Titan แล้ว',162:'<button=L2> ลองใหม่',163:'ข้ามการกระโดดโลมา',164:'จังหวะกระโดดไม่ตรง',165:'โลมาเหนื่อยแล้ว',166:'สำรวจขุดค้นไม่ได้หากไม่มี Chocobo',167:'ไม่พบอะไรเลย……',168:'ดูเหมือนไม่มีอะไรอยู่ใกล้ๆ',169:'Chocobo สัมผัสได้ถึงอะไรบางอย่าง',170:'<button=decide> ปิด',171:'<button=LS> กำลังใช้งาน',172:'<object=0> × <count> ชิ้น',173:'Materia <object=0> × <count> ชิ้น',
174:'เครื่องหมายแนะนำสีน้ำเงินรูป 6 เหลี่ยม\nให้กดปุ่มค้างไว้',175:'เครื่องหมายแนะนำสีเหลืองรูป 5 เหลี่ยม\nให้กดปุ่มรัวๆ',176:'เครื่องหมายแนะนำสีแดงรูป 4 เหลี่ยม\nให้กดปุ่มครั้งเดียว',177:'ระดับความยาก',178:'การแสดงที่ 1',179:'การแสดงที่ 2',180:'การแสดงที่ 3',181:'ต้องจัดกำลังให้ครบ 5 หน่วย\nจึงจะเข้าร่วมพาเหรดได้',
182:'การแสดงที่ปลุกใจให้ฮึกเหิมราวเปลวเพลิง\nจำนวนครั้งที่กด: น้อย ปุ่ม: <button=minigame-A><button=minigame-B>',
183:'การแสดงยากที่เคลื่อนไหวดุจมังกรทะยานฟ้า\nจำนวนครั้งที่กด: ปานกลาง ปุ่ม: <button=minigame-Y><button=minigame-X><button=minigame-A><button=minigame-B>\nมีการกดรัวและกดค้าง',
184:'การแสดงที่มีจังหวะหนักเบาน่าตื่นเต้นราวสายฟ้า\nจำนวนครั้งที่กด: น้อย ปุ่ม: <button=minigame-X><button=minigame-A><button=minigame-B>\nมีการกดรัว',
185:'การแสดงสง่างามดุจดอกไม้น้ำแข็ง\nจำนวนครั้งที่กด: น้อย ปุ่ม: <button=minigame-Y><button=minigame-A><button=minigame-B>\nมีการกดค้าง',
186:'การแสดงที่ปลุกใจให้ฮึกเหิมราวเปลวเพลิง\nจำนวนครั้งที่กด: ปานกลาง ปุ่ม: <button=minigame-Y><button=minigame-X><button=minigame-A><button=minigame-B>',
187:'การแสดงที่ปลุกใจให้ฮึกเหิมราวเปลวเพลิง\nจำนวนครั้งที่กด: มาก ปุ่ม: <button=minigame-Y><button=minigame-X><button=minigame-A><button=minigame-B>',
188:'การแสดงยากที่เคลื่อนไหวดุจมังกรทะยานฟ้า\nจำนวนครั้งที่กด: มาก ปุ่ม: <button=minigame-Y><button=minigame-X><button=minigame-A><button=minigame-B>\nมีการกดรัวและกดค้าง',
189:'การแสดงที่มีจังหวะหนักเบาน่าตื่นเต้นราวสายฟ้า\nจำนวนครั้งที่กด: ปานกลาง ปุ่ม: <button=minigame-Y><button=minigame-X><button=minigame-A><button=minigame-B>\nมีการกดรัว',
190:'การแสดงที่มีจังหวะหนักเบาน่าตื่นเต้นราวสายฟ้า\nจำนวนครั้งที่กด: มาก ปุ่ม: <button=minigame-Y><button=minigame-X><button=minigame-A><button=minigame-B>\nมีการกดรัว',
191:'การแสดงสง่างามดุจดอกไม้น้ำแข็ง\nจำนวนครั้งที่กด: ปานกลาง ปุ่ม: <button=minigame-Y><button=minigame-X><button=minigame-A><button=minigame-B>\nมีการกดค้าง',
192:'การแสดงสง่างามดุจดอกไม้น้ำแข็ง\nจำนวนครั้งที่กด: มาก ปุ่ม: <button=minigame-Y><button=minigame-X><button=minigame-A><button=minigame-B>\nมีการกดค้าง',
193:'<button=decide> สลับหน่วย (รูปแบบการแสดงเปลี่ยนตามหน่วยที่เข้าร่วม) <button=dir> เลือกหน่วย',194:'<button=decide> สลับ <button=dir> เลือกหน่วย',195:'มีหน่วยใหม่มาสมทบแล้ว',196:'จัดขบวน',197:'หน่วยที่เข้าร่วม',198:'หน่วยสำรอง',199:'ค้นหาหน่วยทหาร',200:'ขี่ Chocobo แล้วลองสำรวจ',201:'Chocobo จดจำกลิ่นแล้ว',202:'ตามร่องรอยกลิ่นไป',203:'สำรวจพื้นดิน',204:'ตอนนี้รีบไป Gongaga Reactor ก่อน',205:'พบร่องรอยกลิ่นใหม่แล้ว',206:'ขุดพบไอเทมครบทั้งหมดแล้ว',207:'พบร่องรอยกลิ่นมอนสเตอร์แล้ว',208:'ดูเหมือนไม่มีร่องรอยกลิ่นอยู่ใกล้ๆ',209:'ดมกลิ่น',
    })
    rows=read('reference/ch1-6-recheck-ui-source.json');templates=read('reference/ch1-6-recheck-ui-templates.json');lookup={r['id']:r for r in rows}
    for t in templates:
        k=t['examples'][0]
        if '_Title' in k:values[t['index']]=intel_title(lookup[k]['English']['Text'])
    assert set(values)=={t['index'] for t in templates},set(t['index'] for t in templates)-set(values)
    out=read('translations/ch1-6-recheck-ui-automatic.json')
    for r in rows:
        if r['mode']=='report_title':out[r['id']]=intel_title(out[r['id']])
        elif r['mode']=='translate':out[r['id']]=values[r['template']]
        elif r['mode']=='card_description':
            jp=r['Japanese']['Text'];en=r['English']['Text']
            if k:=re.search('<color=orange>(.*?)</color>',en,re.S):
                body=k[1].replace('\r','').strip()
                body=re.sub(r'No\. (\d+):',r'การ์ด \1:',body)
                out[r['id']]="แพ็กการ์ด Queen's Blood\nมีการ์ดต่อไปนี้\n<color=orange>\n"+body+'\n</color>'
            else:out[r['id']]="การ์ดระดับตำนานของ Queen's Blood" if 'レジェンド' in jp else "การ์ดสำหรับ Queen's Blood"
    expected={r['id'] for r in rows if r['mode'] not in ('existing','unchanged')}
    assert set(out)==expected
    for r in rows:
        if r['id'] not in out:continue
        t=out[r['id']];assert t.strip() and not JP.search(t),(r['id'],t)
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',r['Japanese']['Text']),r['id']
    write('translations/ch1-6-recheck-ui-manual.json',{str(k):v for k,v in values.items()})
    write('translations/ch1-6-recheck-ui-th.json',out)
    print('Assembled',len(out),'new reviewed UI records from',len(templates),'manual templates plus official names/reuse/card descriptions')

if __name__=='__main__':main()
