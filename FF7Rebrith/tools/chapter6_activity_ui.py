"""Reviewed first-visit Costa activity UI supplement; no later story dialogue."""
import copy,hashlib,json,re,shutil,uuid
from pathlib import Path
from assemble_chapter6 import W,read,write,txtres,JP
from assemble_ui_completion import fingerprint

ASSET='End/Content/Text/JP/Resident_TxtRes.uasset'
ROOT='qa/chapter6/activity-ui'
EXCLUDED={'$card_challenge_header_GS','$card_challenge_category_special_rule_1','$card_challenge_category_special_rule_2'}
EXTRA={'$RunWild_reward_header','$Bronze_reward_runwild_score','$Bronze_reward_runwild_score_amor1',
 '$Gold_reward_runwild_score','$Silver_reward_runwild_score','$key_HappytenderCamera_help',
 '$key_HappytenderMemo_help','$keyitem_CostaAmorNoCard77_help','$keyitem_CostaAmorNoCard7_help',
 '$card_MenuLog_Appeared_COSTT','$TravelCameraman_Window_COSTA'}
OFFICIAL_MODE_NAMES={'$minigame_runwild_modename_battle','$minigame_runwild_modename_target'}

def selected(k):
    return k not in EXCLUDED and (k.startswith(('$minigame_ShootingGame_','$minigame_runwild_',
      '$wheelie_','$card_challenge_','$CardChallenge_01_','$CardChallenge_02_','$CardChallenge_03_',
      '$keyitem_CostaClothes_')) or k in EXTRA)

def prepare():
    assert not (W/(ROOT+'/baseline.json')).exists(),'Revision already prepared; preserve its baseline'
    dest=ROOT+'/revisions/'+uuid.uuid4().hex
    for rel in ['translations/working-through-chapter6-th.json','translations/chapter6-th.json',
      'reference/through-chapter6-cluster-map.json','qa/chapter6/working-assets.json','qa/final-parts/latest.json']:
        p=W/dest/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,p)
    write(ROOT+'/baseline.json',dict(snapshot=dest,protected=fingerprint(),
      source_hashes={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest()
        for lang in ('JP','US') for p in (W/f'source/End/Content/Text/{lang}').glob('*.uasset')}))
    j=read('reference/rebirth-jp-corpus.json')['Resident_TxtRes.uasset']
    u=txtres.parse(str(W/'source'/ASSET.replace('/JP/','/US/')))
    old=read('translations/working-through-chapter6-th.json')['assets'][ASSET]['entries']
    rows=[dict(asset=ASSET,id=k,Japanese=v,English=u.get(k,{}),
      action='existing_translation' if k in old else 'translate' if k in OFFICIAL_MODE_NAMES or re.search('[\u3040-\u30ff\u3400-\u9fff\uff21-\uff3a\uff10-\uff19]',v['Text']) else 'preserve_English_or_symbol')
      for k,v in j.items() if selected(k)]
    write('reference/chapter6-activity-ui-source.json',rows)
    write('reference/chapter6-activity-ui-scope.json',dict(
      description='First-visit Costa activity HUD, generic menus, introductory Card Carnival puzzles 01–03, tickets, camera and six beach outfits. Shared HUD labels may also appear in later difficulty variants.',
      excluded_specific_keys=sorted(EXCLUDED),
      excluded_categories=['Gold Saucer ShootingCoaster and CardChallenge_GS','CardChallenge 11+ later-return puzzles','Later-state NPC dialogue and regional quests'],
      inventory_records=len(rows),patch_records=sum(r['action']=='translate' for r in rows),
      unchanged_policy='Preserve existing translations and original English/number/symbol-only records. Challenge/course/license proper names use same-ID US.'))
    print('Prepared',len(rows),'inventory records;',sum(r['action']=='translate' for r in rows),'new UI records')

def translations():
    out={}
    def put(prefix,items):
        for k,t in items.items():out[prefix+k]=t
    put('$',{
      'Bronze_reward_runwild_score':'อันดับ 2',
      'Bronze_reward_runwild_score_amor1':'อันดับ 1 เพียงทีมเดียว',
      'Gold_reward_runwild_score':'อันดับ 1 เพียงทีมเดียว',
      'Silver_reward_runwild_score':'อันดับ 1 ร่วม',
      'RunWild_reward_header':'อันดับ',
      'TravelCameraman_Window_COSTA':'Corel Coastline',
      'card_MenuLog_Appeared_COSTT':"มีผู้เล่น Queen's Blood รายใหม่\nปรากฏตัวใน Costa del Sol",
      'key_HappytenderCamera_help':'กล้องเช่าสำหรับกิจกรรม Cactuar Caper',
      'key_HappytenderMemo_help':'แผนที่ระบุตำแหน่ง Hidden Cactuar\nพร้อมค่าซูมกล้องที่ต้องใช้ถ่ายภาพแต่ละจุด',
      'keyitem_CostaAmorNoCard77_help':'ตั๋วเข้าร่วมกิจกรรมต่อไปนี้ใน Costa del Amor\n<color=orange>\nRun Wild\nCactuar Caper\nWheelie Rendezvous\nRoyal Coast Concert\n</color>',
      'keyitem_CostaAmorNoCard7_help':"ตั๋วเข้าร่วมกิจกรรมต่อไปนี้ใน Costa del Amor\n<color=orange>\nPirate's Rampage\nCard Carnival\n</color>",
    })
    put('$keyitem_CostaClothes_',{
      'bike_help':'ชุดพักร้อนที่เติมความสนุกให้วันหยุดอย่างเต็มที่\n※เมื่อสวมชุดนี้ จะไม่แสดงรูปลักษณ์อาวุธที่ติดตั้งอยู่',
      'card_help':'ชุดพักร้อนที่สดชื่นราวกับ Chocobo วิ่งฝ่าท้องทะเล',
      'detective_help':'ชุดพักร้อนที่ช่วยเพิ่มความกล้าและให้อารมณ์แบบเขตร้อน',
      'dribble_help':'ชุดพักร้อนที่มีกลิ่นหอมของดอกไม้บานรับแสงตะวัน',
      'photo_help':'ชุดพักร้อนที่ชวนให้ออกผจญภัยไปกับเกลียวคลื่นระยิบระยับ\n※เมื่อสวมชุดนี้ จะไม่แสดงรูปลักษณ์อาวุธที่ติดตั้งอยู่',
      'shooting_help':'ชุดพักร้อนที่ปลดปล่อยสัญชาตญาณ พร้อมโต้คลื่นทุกรูปแบบ',
    })
    put('$card_challenge_',{
      'bronze_condition':'รางวัลทองแดง <count=0> คะแนน',
      'category_CharacterCard':'ความท้าทายการ์ดสะสม',
      'category_QBproblem':'ปริศนาการ์ดขั้นสูง',
      'category_SkillTutorial':'ฝึกใช้สกิล',
      'category_highscore_challange':'เอาตัวรอด',
      'category_structured_deck':'ปริศนาการ์ดขั้นต้น',
      'course':'ความท้าทาย',
      'gold_condition':'รางวัลทอง <count=0> คะแนน',
      'open4':'ปลดล็อกความท้าทายสำหรับผู้เล่นคนเดียว\nใน Card Carnival แล้ว',
      'open_advanced':'เพิ่มความท้าทายใหม่\nใน Card Carnival แล้ว',
      'opponent_deck_header':'เด็คเฉพาะสำหรับ Card Carnival',
      'opponent_deck_return_guide':'<button=cancel> ย้อนกลับ',
      'prize_1':'รางวัลครั้งแรก',
      'prize_2':'รางวัลปกติ',
      'prize_hiscore_1':'รางวัล',
      'prize_hiscore_2':'ครั้งแรก',
      'release_condition':'เงื่อนไขปลดล็อก',
      'silver_condition':'รางวัลเงิน <count=0> คะแนน',
      'view_opponent_deck_guide':'<button=square> ดูเด็คเฉพาะสำหรับ Card Carnival',
    })
    put('$minigame_ShootingGame_',{
      'BaseScore':'คะแนนยิงเป้า','HitRate':'ความแม่นยำ',
      'HitRateNotificationUI_Excellent':'ความแม่นยำ <count=0>％ สมบูรณ์แบบ!',
      'HitRateNotificationUI_Great':'ความแม่นยำ <count=0>％ ยอดเยี่ยม!',
      'HitRateNotificationUI_Nice':'ความแม่นยำ <count=0>％ ดีมาก!',
      'HitRateNotificationUI_None':'ความแม่นยำ <count=0>％',
      'HitRateNotificationUI_Over':'ความแม่นยำมากกว่า <count=0>％',
      'HitRateNotificationUI_Under':'ความแม่นยำน้อยกว่า <count=0>％',
      'Log_MotionSensor':'เปลี่ยนเป็นเล็งด้วยเซ็นเซอร์ตรวจจับการเคลื่อนไหวแล้ว',
      'Log_Stick':'เปลี่ยนเป็นเล็งด้วยสติ๊กแล้ว',
      'OperationGuide':'<button=shooting-shoot-R> ยิง',
      'OperationGuide02':'<button=shooting-shoot-L> ยิง',
      'OperationGuide03':'<button=decide> แรงต้านไกปืน',
      'OperationGuide04':'<button=square> สลับปุ่มยิงและสติ๊กเล็ง',
      'OperationGuide05':'<button=square> แสดง/ซ่อนคะแนนเป้าที่ทำลาย',
      'OperationGuide06':'<button=shooting-target-R> เล็ง',
      'OperationGuide07':'<button=shooting-target-L> เล็ง',
      'OperationGuide08':'ความเร็วในการเล็ง',
      'OperationGuide09':'ON','OperationGuide10':'OFF',
      'OperationGuide11':'<button=triangle> ลองใหม่','OperationGuide12':'ลองใหม่',
      'RoundBestScoreEverUI':'สถิติสูงสุด: รอบ <count=0>',
      'RoundBestScoreEverUI_Record':'ทำลายสถิติสูงสุด!',
    })
    put('$minigame_runwild_',{
      'announce_ball_add':'เพิ่มลูกบอลใหม่แล้ว!',
      'announce_teamB_retire':'ทีมสีน้ำเงิน... หมดกำลังใจแล้ว!',
      'announce_teamB_wildend':'ทีมสีน้ำเงิน... สงบลงแล้ว!',
      'announce_teamB_wildstart':'ทีมสีน้ำเงินปลดปล่อยสัญชาตญาณ!\nเปิดใช้โหมดสุนัขป่า!',
      'announce_teamC_retire':'ทีมสีดำ... หมดกำลังใจแล้ว!',
      'announce_teamC_wildend':'ทีมสีดำ... สงบลงแล้ว!',
      'announce_teamC_wildstart':'ทีมสีดำปลดปล่อยสัญชาตญาณ!\nเปิดใช้โหมดสุนัขจอมลีลา!',
      'announce_teamD_retire':'ทีมสีเหลือง... หมดกำลังใจแล้ว!',
      'announce_teamD_wildend':'ทีมสีเหลือง... สงบลงแล้ว!',
      'announce_teamD_wildstart':'ทีมสีเหลืองปลดปล่อยสัญชาตญาณ!\nเปิดใช้โหมด Chocobo จอมทำประตู!',
      'keyguide1':'วิ่งเร็ว','keyguide2':'วิ่งเต็มฝีเท้า','keyguide3':'ยิงประตู',
      'keyguide4':'ยิงโด่ง','keyguide5':'กระโดด','keyguide6':'กระโดดยิง',
      'keyguide7':'ตีลังกายิง','score_retry':'ต้องการลองใหม่หรือไม่?',
      'target':'【หมายเลขเป้าหมาย】',
      'target_explain':'ยิงลูกบอลเข้าประตูที่มีหมายเลขตรงกัน!',
      'teamA':'ทีมสีแดง','teamB':'ทีมสีน้ำเงิน','teamC':'ทีมสีดำ','teamD':'ทีมสีเหลือง',
      'modename_battle':'Free-For-All','modename_target':'Time Trial',
    })
    put('$wheelie_',{
      'hud_Mileage':'ระยะทางรวม','hud_Mileage_Cmn':'ระยะทางรวม',
      'hud_Minigame_BlueInfo':'Wheelie สีน้ำเงิน','hud_Minigame_BlueInfo_Cmn':'Wheelie สีน้ำเงิน',
      'hud_Minigame_CountUp':'เก็บคืน Wheelie สีแดงแล้ว',
      'hud_Minigame_CountUp_Blue':'เก็บคืน Wheelie สีน้ำเงินแล้ว',
      'hud_Minigame_CountUp_Yellow':'เก็บคืน Wheelie สีเหลืองแล้ว',
      'hud_Minigame_Head':'จำนวนรถที่นำคืน','hud_Minigame_Head_Cmn':'จำนวนรถที่นำคืน',
      'hud_Minigame_RedInfo':'Wheelie สีแดง','hud_Minigame_RedInfo_Cmn':'Wheelie สีแดง',
      'hud_Minigame_Story':'เก็บคืน Wheelie ที่จอดทิ้งไว้',
      'hud_Minigame_YellowInfo':'Wheelie สีเหลือง','hud_Minigame_YellowInfo_Cmn':'Wheelie สีเหลือง',
      'log_Minigame_1st':'รับรางวัลขับ Wheelie ครบ 200 m แล้ว!',
      'log_Minigame_2nd':'รับรางวัลขับ Wheelie ครบ 1000 m แล้ว!',
      'log_Minigame_3rd':'รับรางวัลขับ Wheelie ครบ 2000 m แล้ว!',
      'log_Minigame_4th':'รับรางวัลขับ Wheelie ครบ 4000 m แล้ว!',
      'rewardui_advanced':'ขั้นสูง','rewardui_beginer':'เบื้องต้น',
      'rewardui_elementary':'ขั้นต้น','rewardui_intermediate':'ขั้นกลาง',
    })
    details={
      '01':'ใช้การ์ดเพียง 3 ใบในการท้าทายนี้\nการ์ดของคู่แข่งวางหงายอยู่บนกระดานแล้ว\n\nตำแหน่งและลำดับการวางการ์ดคือกุญแจสำคัญ\nสังเกตเลนของคู่แข่งและการ์ดของตนให้ดี เพื่อคว้าชัยชนะ',
      '02':'ใช้การ์ดในมือ 3 ใบกับการ์ดบนกระดาน 1 ใบในการท้าทายนี้\nการ์ดของคู่แข่งวางหงายอยู่บนกระดานแล้ว\n\nแม้ชนะเพียงเลนเดียวก็ชนะเกมได้ หากมีคะแนนสูงกว่า\nรวมการ์ด Chocobo ไว้ในเลนเดียวกัน\nหาวิธีเพิ่มคะแนนให้ได้มากที่สุดเพื่อคว้าชัยชนะ',
      '03':'ใช้เด็คเฉพาะในการท้าทายนี้\nการ์ดของคู่แข่งวางหงายอยู่บนกระดานแล้ว\n\nการ์ดทีเด็ด Moogle Trio มีสกิลเพิ่ม\nMoogle Mage และ Moogle Bard เข้ามาในมือ\nวางการ์ดให้ใช้ความสามารถของแต่ละใบได้เต็มที่เพื่อคว้าชัยชนะ',
    }
    rows=read('reference/chapter6-activity-ui-source.json')
    lookup={r['id']:r for r in rows}
    for i,body in details.items():
        prefix='$CardChallenge_'+i+'_'
        out[prefix+'Detail']='ความท้าทายเฉพาะช่วงจัดงาน Costa del Amor!\n'+body+'\n\n<color=yellow-black>※Regina คู่หูของคุณผ่านการท้าทายนี้แล้ว\nหาก Cloud ผ่านด้วย ก็จะผ่านเข้ารอบได้</color>'
        out[prefix+'Detail_AfterAmor']=body
        if i=='01':out[prefix+'Detail_AfterAmor']+='\n\n<color=red>※ขณะเลือกการ์ด เลื่อนเคอร์เซอร์ไปบนกระดาน\nเพื่อตรวจดูสกิลของการ์ดที่วางอยู่</color>'
        out[prefix+'Jenre']='ปริศนาการ์ดขั้นต้น'
        for suffix in ('Title','Title_AfterAmor'):
            k=prefix+suffix;out[k]=lookup[k]['English']['Text']
        if i!='01':
            out[prefix+'Condition']=f'ชนะ Cards del Amor Challenge รอบ {int(i)-1}'
            out[prefix+'Condition_AfterAmor']='ผ่าน '+lookup['$CardChallenge_'+f'{int(i)-1:02}'+'_Title_AfterAmor']['English']['Text']
    for i in range(1,5):
        k='$wheelie_clear_rank'+str(i);out[k]=lookup[k]['English']['Text']
    expected={r['id'] for r in rows if r['action']=='translate'}
    assert set(out)==expected,('missing',expected-set(out),'extra',set(out)-expected)
    out={k:t.replace('％','%') for k,t in out.items()}
    for r in rows:
        if r['action']!='translate':continue
        t=out[r['id']];assert not JP.search(t),r['id']
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',r['Japanese']['Text']),r['id']
    write('translations/chapter6-activity-ui-th.json',out)
    print('Saved',len(out),'reviewed UI translations')

if __name__=='__main__':
    import sys
    if '--prepare' in sys.argv:prepare()
    translations()
