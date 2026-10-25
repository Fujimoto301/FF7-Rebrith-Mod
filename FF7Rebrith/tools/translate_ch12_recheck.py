"""Reviewed JP-source translations for whole early-game activity UI families."""
import re
from assemble_chapter6 import read,write,JP

def main():
    rows=read('reference/ch12-recheck-ui-source.json');out={}
    lookup={r['id']:r for r in rows}
    def put(prefix,d):out.update({prefix+k:t for k,t in d.items()})
    for r in rows:
        if r['mode']=='english_name':out[r['id']]=r['English']['Text']
    common={'はい':'ใช่','いいえ':'ไม่ใช่','戻る':'ย้อนกลับ','再挑戦しますか？':'ต้องการลองใหม่หรือไม่?',
      'チュートリアルを確認しますか？':'ต้องการดูบทสอนเล่นหรือไม่?',
      'チュートリアルに再挑戦しますか？':'ต้องการเล่นบทสอนอีกครั้งหรือไม่?',
      'リトライ':'ลองใหม่','やりなおす':'ลองใหม่','本当にリタイアしますか？':'ต้องการยอมแพ้หรือไม่?',
      'リタイアする':'ยอมแพ้','ゲームを再開する':'เล่นต่อ','カード一覧':'รายการการ์ด',
      'ソート／フィルター':'เรียงลำดับ/ตัวกรอง'}
    for r in rows:
        if r['mode']=='translate' and r['Japanese']['Text'] in common:out[r['id']]=common[r['Japanese']['Text']]
    put('$minigame_cardgame_',{
      'Mulligan_guide':'<button=decide> เลือกการ์ดที่จะเปลี่ยน',
      'Mulligan_help':'เลือกการ์ดที่ต้องการเปลี่ยน',
      'Mulligan_start_guide':'<button=triangle> เริ่มเกม',
      'Try':"ต้องการเล่น Queen's Blood หรือไม่?",'YES_Quest':'<button=quest>ใช่',
      'bouterrank_rankup_condition':'เงื่อนไขเลื่อนแรงก์',
      'bouterrank_rankup_condition_max':'ถึงแรงก์สูงสุดแล้ว',
      'bouterrankup_header':'แรงก์ผู้เล่นเพิ่มขึ้น!',
      'cardbout_cannot_start':'เด็คนี้ยังใช้เล่นไม่ได้\nต้องจัดเด็คให้มีการ์ด 15 ใบก่อน',
      'cardlist_sorting_guide':'<button=triangle> เรียงลำดับ/ตัวกรอง',
      'changeview_guide':'<button=triangle> เรียงลำดับ/ตัวกรอง',
      'deckcopy_comfirm_replace':'ต้องการเขียนทับ <object=0> ด้วย <object=1> หรือไม่?',
      'deckcopy_guide_select_deck':'<button=L1><button=R1> สลับเด็คต้นทาง',
      'deckcopy_header':'เลือกเด็คที่ต้องการคัดลอก',
      'deckedit_add':'เพิ่ม','deckedit_delete':'ลบ',
      'deckedit_aquired_cardlist_complete':"ได้รับการ์ดครบทุกใบแล้ว\nขอให้สนุกกับ Queen's Blood ต่อไป!",
      'deckedit_aquired_cardlist_header':'การ์ดที่มี',
      'deckedit_cardlist_sorting_guide':'<button=triangle> เรียงลำดับ/ตัวกรอง',
      'deckedit_deckselect_transition_guide':'<button=triangle> แก้ไขเด็ค',
      'deckedit_editcancel':'ออกโดยไม่บันทึกการเปลี่ยนแปลง',
      'deckedit_exit_alert':'เด็คนี้ยังใช้เล่นไม่ได้\nต้องจัดเด็คให้มีการ์ด 15 ใบก่อน\nต้องการออกจากการแก้ไขเด็คหรือไม่?',
      'deckedit_exit_alert_no':'แก้ไขเด็คต่อ',
      'deckedit_exit_alert_yes':'บันทึกการเปลี่ยนแปลงแล้วออก',
      'deckedit_nocards':'ยังไม่ได้ใส่การ์ดในเด็ค',
      'deckedit_over_alert':'※เด็คใส่การ์ดได้สูงสุด 15 ใบ',
      'deckedit_preset_title':'เลือกเด็คแนะนำ',
      'detail_card_number':'หมายเลขการ์ด',
      'guide_deckcopy':'<button=R3> คัดลอกจากเด็คอื่น',
      'no_hand':'ไม่มีการ์ดในมือ','no_possession':'ยังไม่มี',
      'no_possession_button_guide':'<button=square> แสดง/ซ่อนการ์ดที่ยังไม่มี',
      'pass_gameend':'ผ่านแล้วจะจบเกม','pass_nocard1':'ไม่มีการ์ดที่วางได้','pass_nocard2':'ไม่มีการ์ดที่วางได้',
      'pass_normal':'<button=triangle> ผ่าน','pass_roundend':'ผ่านแล้วจะจบรอบ',
      'pause_retire_comfirm_lose':'ต้องการยอมแพ้หรือไม่?\n(จะถือว่าแพ้และแข่งใหม่ไม่ได้)',
      'pause_retire_lose':'ยอมแพ้ (ถือว่าแพ้และแข่งใหม่ไม่ได้)',
      'presetdeck_confirm':'ต้องการเขียนทับ <object=0> ด้วย “<object=1>” หรือไม่?',
      'presetdeck_decide':'<button=decide> เขียนทับด้วยเด็คนี้',
      'presetdeck_guide':'<button=options> สร้างจากเด็คสำเร็จรูป',
      'presetdeck_shortage':'ยังขาดการ์ดต่อไปนี้','presetdeck_title':'เด็คสำเร็จรูป',
      'prize_received':'※รับแล้ว','readymenu_boss_bouter':'ชนะผู้เล่นระดับบอส',
      'readymenu_defeated_bouter':'จำนวนคู่แข่งที่ชนะ',
      'readymenu_prize_Earned':'※รับแล้ว','readymenu_prize_all_nothing':'ไม่มีรางวัล',
      'readymenu_prize_card_nothing':'ไม่มีรางวัลการ์ด',
      'readymenu_rankup_notice':'ชนะตานี้เพื่อเลื่อนแรงก์!',
      'result_ViewMode':'<button=square> โหมดชม',
      'result_retry_2':'<button=triangle> ลองใหม่',
      'result_retry_tutorial_2':'<button=triangle> เล่นบทสอนอีกครั้ง',
      'sorting_filter_ability_header':'สกิล','sorting_filter_cardrank_Ex':'พิเศษ',
      'sorting_filter_cardrank_header':'แรงก์การ์ด','sorting_filter_header':'ตัวกรอง',
      'sorting_filter_nocards':'ไม่มีการ์ดที่ตรงกับตัวกรองปัจจุบัน',
      'sorting_filter_rarity_header':'ความหายาก','sorting_filter_rarity_legend':'ตำนาน',
      'sorting_filter_rarity_nomal':'ปกติ','sorting_sort_acquisition':'ลำดับที่ได้รับ',
      'sorting_sort_ascending':'น้อยไปมาก','sorting_sort_cardnumber':'หมายเลขการ์ด',
      'sorting_sort_cardrank':'แรงก์การ์ด','sorting_sort_descending':'มากไปน้อย',
      'sorting_sort_header':'เรียงลำดับ','sorting_sort_new':'ใหม่ไปเก่า',
      'sorting_sort_old':'เก่าไปใหม่','sorting_sort_power':'พลัง','sorting_sort_rarity':'ความหายาก',
      'start_tutorial_guide':'<button=touch> ดูบทสอนเล่น',
      'startgame_alert':'เริ่มเกมไม่ได้\nจำนวนการ์ดในเด็คที่เลือกไม่ตรงตามกำหนด',
      'startgame_confirmation':'ต้องการเริ่มเกมหรือไม่?',
      'startgame_guide':'<button=options> เริ่มแข่ง',
      'tutorial_Check':"ต้องการดูบทสอนเล่น Queen's Blood หรือไม่?",
      'viewboard_guide_end':'<button=cancel> กลับไปเลือกการ์ดในมือ',
      'viewboard_guide_start':'<button=up> ตรวจดูการ์ดบนกระดาน',
      'viewboard_hidedetail':'<button=square> ซ่อนข้อมูลการ์ด',
      'viewboard_showdetail':'<button=square> แสดงข้อมูลการ์ด',
      'presetdeck0_help':'เด็คที่จัดจากการ์ดใช้ง่าย เหมาะกับผู้เริ่มเล่น Queen\'s Blood ใช้การ์ดแรงก์ต่ำยึดพื้นที่ แล้ววาง Magic Pot เพื่อเพิ่มพลังให้การ์ดรอบข้างและพลิกเกมกลับมาชนะ',
      'presetdeck10_help':'เด็คที่เน้นการ์ดพลังต่ำ แต่เพิ่มแรงก์พื้นที่ได้ 2 ระดับ ยึดและขยายพื้นที่ก่อนคู่แข่งจะแย่งไป เมื่อขยายพื้นที่ว่างได้มากพอ ให้วาง Shiva ในจังหวะเหมาะสมเพื่อเปลี่ยนพื้นที่ทั้งหมดเป็นพลัง',
      'presetdeck11_help':'เด็คที่เน้นการ์ดซึ่งใช้สกิลทรงพลังเมื่อตนถูกลดพลัง ต้องเลือกจังหวะเสียสละแล้วโต้กลับให้ดี ใช้ Jabberwock ลดพลังการ์ดฝ่ายเดียวกันเพื่อกระตุ้นสกิลอันทรงพลัง',
      'presetdeck2_help':'เด็คที่เน้นการ์ดเสริมพลังให้ฝ่ายเดียวกัน เลือกตำแหน่งวาง Magic Pot ให้เสริมพลังการ์ดได้หลายใบ ยิ่งมีการ์ดฝ่ายเราที่ได้รับการเสริมพลังจากสกิลมากเท่าไร Chocobo & Moogle ก็ยิ่งมีพลังสูงขึ้น',
      'presetdeck4_help':'เด็คที่เน้นการ์ดพลังต่ำ แต่ค่อยๆ ลดพลังการ์ดคู่แข่งจนถูกทำลาย การ์ดที่พลังเหลือ 0 จะถูกทำลาย ส่วนการ์ดทีเด็ด Midgardsormr จะมีพลังสูงขึ้นอย่างมากเมื่อมีการ์ดถูกทำลาย',
      'presetdeck5_help':'เด็คที่เน้นลดพลังและทำลายการ์ดหลายใบทั้งสองฝ่าย เมื่อการ์ดถูกทำลาย ให้ใช้ Mandragora เพิ่มการ์ดในมือพร้อมยึดพื้นที่ แล้วค่อยๆ เพิ่มพลังให้ Sea Devil ซึ่งเป็นการ์ดทีเด็ด',
      'presetdeck6_help':'เด็คที่เน้นการ์ดซึ่งใช้สกิลทรงพลังเมื่อถูกทำลาย ใช้สกิลลดพลังของ Capparwire หรือการ์ดอื่นกับฝ่ายตนเองจนพลังเหลือ 0 เพื่อกระตุ้นสกิลเมื่อถูกทำลาย ส่วน Tonberry King จะมีพลังสูงขึ้นเมื่อการ์ดฝ่ายเดียวกันถูกทำลาย',
      'presetdeck7_help':'เด็คที่เน้นสกิลวางทับการ์ดฝ่ายเดียวกันบนกระดาน การ์ดที่ถูกทับจะถูกทำลายและกระตุ้นสกิลเมื่อถูกทำลาย ใช้กลยุทธ์พลิกแพลงกับ Grandhorn, Gigantoad และการ์ดอื่นๆ เพื่อคว้าชัยชนะ',
      'presetdeck8_help':'เด็คที่เน้นการ์ดซึ่งใช้สกิลทรงพลังเมื่อตนได้รับการเสริมพลัง สกิลชนิดนี้ทำงานเพียงครั้งเดียว จึงต้องจัดลำดับวางการ์ดที่ช่วยกระตุ้นสกิลให้ดี เลือกจังหวะใช้ Stone Golem และการ์ดทีเด็ดอื่นให้เหมาะสม',
      'presetdeck9_help':'เด็คที่เน้นสกิลวางทับและนำพลังของการ์ดที่ถูกทำลายไปใช้กับสกิลเพิ่มหรือลดพลัง การถ่ายโอนพลังจากการทำลายคือกุญแจสำคัญ ใช้ Griffon, Gi Specter และการ์ดอื่นในช่วงท้าย เพื่อชิงความได้เปรียบแต่ละเลน',
    })
    for i in range(1,7):out[f'$minigame_cardgame_deckedit_decknumber_{i}']=f'เด็คหมายเลข {i}'
    put('$cardtext_HowtoGet_',{'Bout':'ได้รับจากการชนะคู่แข่งในการ์ดแบตเทิล',
      'Extra_Event':'ได้รับจากเนื้อเรื่องหรือเควสต์','Extra_Game':'ได้รับจากการผ่านความท้าทายการ์ด',
      'Shop':'ซื้อได้จากร้านค้า'})
    put('$card_MenuLog_',{
      'Absence':'คู่แข่งไม่อยู่',
      'JNONV_CardGamer02':'ชนะ Devin ผู้น้องแล้ว\nต่อไปลองเอาชนะ Darren ผู้พี่',
    })
    places={'CORLV':'North Corel','CSMOA':'Cosmo Canyon','GONGV':'Gongaga','JNONV':'Under Junon',
      'JUNOA':"the Crow's Nest",'KALMT':'Kalm','NIBLT':'Nibelheim','UNDRS':'the Dustbowl'}
    for code,name in places.items():out['$card_MenuLog_Appeared_'+code]=f"มีผู้เล่น Queen's Blood รายใหม่\nปรากฏตัวใน {name}"
    for code,rank in [('CORLV','Blood Knight'),('GOLDS','Blood Marquis'),('GONGV','Blood Tactician'),('JUNOA','Blood Squire'),('UNDRS','Blood Captain')]:
        k='$card_MenuLog_NotFill_'+code+'Boss';tag=re.search('<[^>]+>',lookup[k]['Japanese']['Text'])[0]
        out[k]=f'ต้องถึงแรงก์ {tag} {rank} ก่อนจึงจะท้าประลองได้'
    out['$GRASA_CARD_000']="ร้านการ์ด Queen's Blood"
    put('$minigame_chocobocapture_',{
      'Awakening_Log':'เคว้!? Chocobo ตื่นแล้ว!',
      'Csmoa_attention1':'ใช้รถรางให้เป็นประโยชน์\nเพื่อบังสายตา Chocobo',
      'Csmoa_attention2':'ลองใช้สวิตช์เปลี่ยนราง',
      'FeathersGetLog':'ได้รับ Golden Plume ×2',
      'GetSupport_Log':'ล่อ Selena สำเร็จแล้ว\nเข้าไปใกล้แล้วจับได้เลย',
      'Interest_Stone':'Chocobo กำลังสนใจก้อนหินก้อนอื่น',
      'Interest_Vegetable':'Chocobo กำลังสนใจเหยื่อล่ออันอื่น',
      'VegetableLog':'Chocobo ตัวอื่นนอกจาก Selena\nดูจะไม่สนใจ Chocobo Bait',
      'attention1':'เดินเข้าไปโดยอย่าให้ Chocobo มองเห็น',
      'attention2':'โยนก้อนหินไปด้านหลัง Chocobo\nเพื่อเบี่ยงเบนความสนใจ',
      'attention3':'โยนก้อนหินให้โดนสวิตช์เพื่อสับสวิตช์',
      'attention4':'Chocobo เฝ้าอยู่จนไปต่อไม่ได้\nลองขึ้นทางที่ทอดไปบนหน้าผา',
      'attention5':'โยน Chocobo Bait จากที่สูง\nเพื่อล่อ Selena ไปทาง入口',
      'attention6':'ผ่านไปตอน Chocobo หันหลังให้',
      'attention7':'เข้าไปจับ Piko\nโดยอย่าให้ Chocobo ตัวอื่นมองเห็น',
      'commandmenu_count_next':'ใช้รถเคลื่อนที่บังตัวขณะเดินเข้าไป',
      'commandmenu_count_next_next':'กด <button=field-action> เพื่อลองใหม่',
      'commandmenu_count_next_next_next':'ดูเหมือนจะไม่สนใจก้อนหิน',
      'commandmenu_count_next_next_next_next':'ขยับรถรางแล้วใช้บังตัวขณะเดินเข้าไป',
      'commandmenu_throw_mode':'ขว้าง','dodge':'กลิ้งหลบ',
      'find':'ถูก Chocobo พบตัวแล้ว','find_beg':"ถูก Beck's Badasses พบตัวแล้ว",
      'gameover':'Chocobo หนีไปแล้ว','gameover_beg':"Beck's Badasses หนีไปแล้ว",
      'item_stone':'Rocks','item_vege1':'Chocobo Bait',
      'lost':'Chocobo หายระแวงแล้ว','lost_beg':"Beck's Badasses หายระแวงแล้ว",
      'pause_retry_comfirm':'ต้องการลองใหม่หรือไม่?',
      'pause_retry_comfirm_next_reset':'เริ่มใหม่ตั้งแต่ต้น',
      'pause_retry_comfirm_next_retry':'เริ่มใหม่จากจุดตรวจสอบ',
      'pause_retry_comfirm_reset':'ต้องการเริ่มใหม่ตั้งแต่ต้นหรือไม่?',
      'pause_retry_comfirm_retry':'ต้องการเริ่มใหม่จากจุดตรวจสอบหรือไม่?',
      'pick_stone':'เก็บก้อนหินแล้ว','pick_vege_01':'ได้รับ Chocobo Bait',
      'retrypoint_update':'อัปเดตจุดตรวจสอบแล้ว','select_checkpoint_question':'เลือกจุดที่จะเริ่มใหม่',
      'select_checkpoint_start0':'เริ่มใหม่ตั้งแต่ต้น','select_checkpoint_start1':'เริ่มต่อจากจุดตรวจสอบ',
      'shirena_log':'โยน Chocobo Bait\nเพื่อล่อ Selena ไปทาง入口',
    })
    # Entrance is generic UI text, not a place name.
    for k in list(out):out[k]=out[k].replace('入口','ทางเข้า')
    put('$minigame_mooglecapture_',{
      'Clear_Log':'พา Moogle กลับมาครบทุกตัวแล้ว!',
      'DoorOpen':'ต้องการเข้า Moogle House หรือไม่?',
      'DoorOpen_EasyMode':'ต้องการเข้า Moogle House หรือไม่?\n(ผ่านรายงานได้ด้วยความยากระดับใดก็ได้)',
      'Retry_Easy':'EASY (ถูกโจมตี 5 ครั้งจะจบเกม)',
      'Retry_Normal':'NORMAL (ถูกโจมตี 3 ครั้งจะจบเกม)',
      'Retry_Text':'<color=yellow>【Moogle Mischief】</color>\nอยากเล่นระดับไหน คุโปะ?\n<color=orange>※ผ่านด่านเพื่อรับ Moogle Medal 1 เหรียญ!</color>',
      'ShopLevel_07':'Moogle Emporium\nมีระดับการค้า MAX แล้ว',
      'dooropen_levelselect':'ต้องการเล่น Moogle Mischief ด้วยความยากระดับใด?',
      'dooropen_levelselect_easy':'EASY (ถูกโจมตี 5 ครั้งจะจบเกม)',
      'dooropen_levelselect_normal':'NORMAL (ถูกโจมตี 3 ครั้งจะจบเกม)',
      'grab':'อุ้ม','hint_cyclone':'ใช้พายุหมุนช่วยจับ Moogle!',
      'hint_cyclone_switch':'เปิดสวิตช์เพื่อสร้างพายุหมุน!',
      'leveleasy_select':'ต้องการลดความยากของ Moogle Mischief หรือไม่?\n(ถูกโจมตี 5 ครั้งจะจบเกม)',
      'moogle_medal_reward':'ได้รับรางวัล Moogle Medal ×1',
      'retry_window':'อยากเล่นอีกครั้งไหม คุโปะ?',
      'reward_collection':'ผ่าน Moogle Mischief ครบแล้ว!\nได้รับของขวัญจากผู้จัดการ Moogle',
      'start_title_msg':'พา Moogle ทั้ง 5 ตัวกลับ Moogle House!',
      'start_title_msg_02':'พา Moogle กลับบ้านให้ทันเวลาที่กำหนด!',
    })
    for i in range(1,8):
        out[f'$minigame_mooglecapture_Retry_Level{i}']=f'ระดับความซน {i}'
        out[f'$minigame_mooglecapture_Retry_Text_Level{i}']=f'<color=yellow>【Moogle Mischief】</color>\n<color=orange>ระดับความซน {i}</color>\nอยากเล่นความยากระดับไหน คุโปะ?'
        if i<7:out[f'$minigame_mooglecapture_ShopLevel_{i:02}']=f'Moogle Emporium\nมีระดับการค้า {i} แล้ว'
    for i,name in enumerate(['Molala','Molulu','Mokey','Moog','Mosh'],1):
        out[f'$minigame_mooglecapture_Capture_Children_{i:02}']=f'จับ {name} ได้แล้ว!'
    names={'11':'Cloud','12':'Barret','13':'Tifa','14':'Aerith','15':'Red XIII','16':'Yuffie','17':'Cait Sith','1S':'Sephiroth','1Z':'Zack'}
    for code,name in names.items():
        out[f'$menu_Colosseum_CourseFlavor_COL{code}_TutorialBtl_01']=f'หลักสูตรฝึกต่อสู้สำหรับ {name}\nเรียนรู้วิธีต่อสู้ของ {name} ด้วยการฝึกจริง\n\n<color=orange>※ห้ามใช้ไอเทม</color>'
    out['$menu_Colosseum_CourseFlavor_COL20_TutorialBtl_01']='หลักสูตรฝึกต่อสู้สำหรับ Cloud กับ Barret รวม 2 คน เรียนรู้พื้นฐานการต่อสู้ด้วยการฝึกจริง\n\n<color=orange>※ห้ามใช้ไอเทม</color>'
    out['$menu_Colosseum_CourseFlavor_COL30_TutorialBtl_01']='หลักสูตรฝึกต่อสู้สำหรับ Cloud, Barret และ Tifa รวม 3 คน เรียนรู้การร่วมมือใช้สกิลประสานและความสามารถประสาน\n\n<color=orange>※ฝึกได้แม้ยังไม่ได้เรียนรู้ท่าประสาน</color>\n<color=orange>※ห้ามใช้ไอเทม</color>'
    for r in rows:
        if r['mode']=='translate' and r['id'].startswith('$menu_Colosseum_CourseTitle_'):out[r['id']]=r['English']['Text']
    expected={r['id'] for r in rows if r['mode'] in ('translate','english_name')}
    missing=expected-set(out);extra=set(out)-expected
    if missing:print('MISSING',[(k,lookup[k]['Japanese']['Text']) for k in sorted(missing)])
    if extra:print('EXTRA',sorted(extra))
    assert not missing and not extra
    for r in rows:
        if r['id'] not in out:continue
        t=out[r['id']];assert t.strip() and not JP.search(t),(r['id'],t)
        assert re.findall('</?[^>]+>',t)==re.findall('</?[^>]+>',r['Japanese']['Text']),r['id']
    write('translations/ch12-recheck-ui-th.json',out)
    print('Saved',len(out),'reviewed UI entries')

if __name__=='__main__':main()
