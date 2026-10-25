"""Reviewed adjoining namespaces found by the independent second coverage pass."""
import re
from assemble_chapter6 import W,read,write,txtres
from prepare_ch1_6_recheck import R

def selected(k):
    return k.startswith('$CF_') or bool(re.match(r'\$(?:NIBLT|NIBLM|MYTHM)_(?:ITEM|MAGIC)_',k)) or k.startswith(('$key_qst07_','$key_qst08_','$key_qst10_','$keyitem_CostameetUpCard_')) or k=='$key_CostaClothes_yuffie'

def main():
    base=read('translations/working-ch12-recheck-th.json')['assets'][R]['entries']
    j=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset'];u=txtres.parse(str(W/'source'/R.replace('/JP/','/US/')))
    manual={
      '$CF_minigame_birdview_button_guide':'<button=decide> โหมดวางแผน <button=L3> สลับกล้องเคลื่อนไหว',
      '$CF_minigame_dynamicview_button_guide':'<button=decide> โหมดวางแผน <button=L3> สลับกล้องมุมสูง',
      '$CF_minigame_result_button_guide_cancel':'<button=decide> ย้อนกลับ',
      '$CF_minigame_result_button_guide_retry':'<button=triangle> ลองใหม่',
      '$CF_minigame_waitmode_button_guide':'<button=decide> เรียกยูนิต <button=cancel> ย้อนกลับ',
      '$key_qst07_CartParts_Bad_help':'ชิ้นส่วนโยกคลอนที่ช่างทำขึ้นขณะงัวเงีย',
      '$key_qst07_CartParts_Good_help':'ชิ้นส่วนแข็งแรงที่ช่างตั้งใจทำอย่างเต็มที่',
      '$key_qst07_CartParts_Normal_help':'ชิ้นส่วนคุณภาพพอใช้ที่ช่างทำขึ้นอย่างรวดเร็ว',
      '$key_qst07_CollectionItem_help':'วัสดุทำชิ้นส่วนรถลากที่ Gabe ช่างทำรถลากขอให้หา',
      '$key_qst07_CollectionMemo_help':'บันทึกสิ่งของที่ต้องใช้ปลุกช่างทำรถลาก Gabe\nระดับการประเมินแบ่งตามจำนวนที่หาได้\n<color=orange>\nจำนวนมาก: Dried Driftwood ×3\nพอประมาณ: Dried Driftwood ×2\nจำนวนน้อย: Dried Driftwood ×1\n</color>',
      '$key_qst08_PrizeMoney_help':'เงินส่งเสียให้ลูกชายที่ออกจาก Under Junon ไป',
      '$key_qst10_CondorFeed_Bad_help':'ผักที่ไม่เคยเห็นมาก่อน ซึ่งขุดพบแถวนี้',
      '$key_qst10_CondorFeed_Good_help':'เนื้อวัวที่เติบโตในธรรมชาติ ดูสดและนุ่ม',
      '$key_qst10_CondorFeed_Normal_help':'เนื้อที่มีสีและกลิ่นชวนให้รู้สึกถึงอันตรายอย่างชัดเจน',
      '$key_qst10_CondorPhoto_Bad_help':'ภาพเบลอมากที่พอจะเห็น Condor อยู่บ้าง',
      '$key_qst10_CondorPhoto_Good_help':'ภาพล้ำค่าที่เก็บ Condor ได้อย่างสมบูรณ์แบบ',
      '$key_qst10_CondorPhoto_Normal_help':'ภาพที่ดีและเก็บ Condor ได้ชัดเจน',
    }
    rows=[];patch={}
    for k,v in j.items():
        if not selected(k) or not v['Text']:continue
        mode='existing' if k in base else 'unchanged' if not re.search('[\u3040-\u30ff\u3400-\u9fff]',v['Text']) else 'translate' if k in manual else 'English_name'
        rows.append(dict(id=k,asset=R,Japanese=v,English=u[k],mode=mode))
        if mode=='translate':patch[k]=manual[k]
        if mode=='English_name':patch[k]=u[k]['Text']
    assert set(manual)<=set(patch)
    write('reference/ch1-6-recheck-extra-source.json',rows);write('translations/ch1-6-recheck-extra-th.json',patch)
    print('Additional namespace inventory',len(rows),'new entries',len(patch))

if __name__=='__main__':main()
