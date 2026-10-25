"""Per-ID decisions from the complete 499-record pronoun review."""
from prepare_chapter9 import W,read,write
from pronoun_context import Q,OV

def main():
    rows=read(Q+'queue.json')['records'];out=[]
    changes={
      16:('แล้วจะทำยังไงต่อ?','Ambient conversation does not identify the addressee; omit the unnecessary gendered second person.'),
      19:('คุณ','Young Cloud admires his hero Sephiroth; respectful คุณ fits that relationship.'),
      105:('คุณ','Refugee couple speaking to each other, not Cloud; neutral คุณ avoids assuming partner gender.'),
      110:('คุณ','Boast addressed to another resident; no identified addressee gender. Use neutral คุณ.'),
      112:('คุณ','Dating partner responds to preceding remark; use neutral คุณ rather than feminizing the partner.'),
      114:('คุณ','Response to the resident suggesting arbitrary reports. No explicit listener identity; neutral คุณ.'),
      115:('คุณ','Rejects the preceding confession hopeful, not a woman established in the text. Use neutral คุณ.'),
      116:('คุณ','Dating conversation with the same returning NPC couple; neutral คุณ.'),
      117:('คุณ','Reply to the partner proposing marriage; consistent neutral คุณ.'),
      153:('คุณ','Glide de Chocobo certificate does not name a male recipient; the quest includes Yuffie and Cloud. Use neutral คุณ.'),
      155:('คุณ','Pirate shooting certificate is not addressed to a named man; neutral recipient wording also covers Aerith.'),
      156:('คุณ','Same Pirate shooting certificate family; neutral recipient wording.'),
      161:('คุณ','Beast Battleground certificate does not name a male recipient. Neutral คุณ also matches Kansai あんさん.'),
      162:('คุณ','Same Test0 certificate family, neutral recipient wording.'),
      253:('นาย','Regina addresses her tournament opponent Cloud, consistent with her earlier lines.'),
      254:('คุณ','Regina addresses an additional prospective opponent; คุณ preserves the unspecific addressee without gender inference.'),
      260:('สุดยอดมากเลย คุณคลาวด์!','Keep the explicit คุณคลาวด์ address; remove the inconsistent second-person นาย from the same sentence.'),
      272:('คุณ','Business partners discussing a project; professional neutral คุณ fits the relationship.'),
      287:('แม่ของนายเป็นคนจ้าง\r\nให้พวกเรามาเป็นบอดี้การ์ดโคฮาดะ','Barret addresses Toby, the client’s son. Disambiguate แม่ของนายจ้าง (your mother hired us), which can read as employer’s mother.'),
      298:('นาย','Hojo addresses Cloud as another subject responding to the Reunion, not the swimsuit staff in the preceding scene.'),
      299:('นาย','Same Hojo-to-Cloud exchange: the brothers are fellow robed subjects.'),
      313:('นาย','Tifa comments on the chick favoring Barret; preceding Barret protest and following Yuffie line explicitly name him.'),
      335:('นาย','Fran addresses Cloud about his fight with Hojo.'),
      336:('นาย','Fran offers the job to Cloud; Aerith is his proposed date.'),
      337:('นาย','Naomi asks Cloud to date his girlfriend; second person is Cloud, not Aerith.'),
      338:('นาย','Fran says Cloud is easily pressured; the next line separately addresses assertive Aerith.'),
      364:('คุณ','The recipient is the recruiting group in the preceding lines, not an established group of women. Use neutral พวกคุณ.'),
      366:('คุณ','The preceding conversation explicitly mentions two men vacationing together (男ふたり). Keep the romantic tone with neutral คุณ.'),
      362:('ใจเย็น หัวหน้าไม่อยู่แล้ว\r\nไม่มีใครจะมาซ้อมหรอก','Ambient reassurance leaves listener identity unspecified. Thai can omit the object without changing who is being reassured.'),
      365:('คุณ','Angry telephone customer cannot know the agent’s gender from this text; neutral คุณ, consistent with preceding line.'),
      368:('คุณ','Amor customer asks a passing participant to partner up; no named recipient, so neutral คุณ.'),
      369:('คุณ','Customer flirts with the flower-shop employee; polite neutral คุณ fits an employee not explicitly named in the line.'),
      370:('คุณ','Household couple: neutral คุณ suits the familiar adult relationship and avoids assuming partner gender.'),
      371:('คุณ','Ring conversation with a partner; neutral คุณ preserves the teasing tone.'),
      372:('คุณ','Flirtatious offer addressed to a passing participant, potentially Cloud. Neutral คุณ fits any participant.'),
      383:('คุณ','Middle Manager asks the studio employee to become his partner. Neutral คุณ suits the customer-staff exchange.'),
      405:('คนนี้เหรอ? คนนี้? หรือคนนี้?','Gus pretends to identify Cloud among a mixed party. Deictic wording avoids assigning นาย to every person he points at.'),
      432:('นาย','Card Collector recommends cards to Cloud, the player of the completed Queen’s Blood job.'),
      433:('นาย','Same Card Collector thanks Cloud for winning.'),
      434:('นาย','Repeated Card Collector recommendation to Cloud, consistent with the earlier variant.'),
      463:('อ๋อ ก็สัตว์ไม่ชอบ\r\nมาตั้งแต่ไหนแต่ไรแล้วนี่','Ambient exchange gives no explicit listener identity; omit gendered second person while retaining the familiar reply.'),
      492:('คุณ','Conversation about the departed Royal Concert pianist does not identify the recipient by name; use neutral คุณ.'),
      493:('คุณ','Reply praises the next conversation partner’s presentation. Neutral คุณ avoids misgendering the respondent.'),
      494:('คุณ','Same personal-history conversation; keep neutral คุณ across both lines.'),
      496:('คุณ','Standalone photographer-like remark does not identify its recipient; neutral คุณ retains the compliment without inferring gender.'),
    }
    for i,(value,reason) in changes.items():
        r=rows[i];t=r['thai']
        if value in ('นาย','คุณ'):
            # Only the target pronoun changes. All names, metadata, particles,
            # line breaks and surrounding grammar remain untouched.
            token='เธอ' if 'เธอ' in t else 'นาย'
            after=t.replace(token,value)
        else:after=value
        assert after!=t,(i,t)
        out.append(dict(index=i,asset=r['asset'],id=r['id'],before=t,after=after,reason=reason,jp=r['jp'],us=r['us'],actor=r['actor']))
    assert len(out)==45
    write(Q+'corrections-draft.json',dict(records=out))
    # The full queue was opened sequentially, with ambiguous recipients reopened
    # alongside neighboring JP and Thai dialogue. This records that actual read.
    write(Q+'progress.json',dict(total=499,reviewed_ranges=[dict(start=0,end_exclusive=499,note='Read all JP/US/Thai records and speakers. Reopened ambiguous contexts including16,48,49,63,64,73,105–120,253–255,266–268,272,277,297–298,313,335,338,344,364–374,383–384,400,405,428,432,464,492–498 and Glide quest context. Kept MadamM400 because the following JP explicitly says彼女; kept both-female and same-sex relationships without assuming heterosexual pairs.')],reviewed_records=499,remaining_records=0,complete=True,corrected_records=45,global_replace_used=False))
    print('Recorded45 exact corrections; all499 candidates read')

if __name__=='__main__':main()
