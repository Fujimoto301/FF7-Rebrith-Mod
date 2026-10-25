import json,collections,re
from pathlib import Path
c=json.loads(Path('FF7Rebrith/reference/rebirth-jp-corpus.json').read_text('utf-8'))
for asset,d in c.items():
 groups=collections.defaultdict(list)
 for k,v in d.items():
  if v['Text'] and re.match(r'^\$(?:[Ii]tem|it_|key_|M_|Materia|BattleSkill|WeaponAbility|menu_WeaponUpgrade|menu_EquipmentSkill|menu_EQSkill|cardtext)',k):groups['_'.join(k.split('_')[:2])].append((k,v['Text']))
 if not groups:continue
 print('\nASSET',asset)
 for g,rs in groups.items():
  print(g,len(rs))
  for k,t in rs[:2]:print(' ',k,t.replace('\r\n',' / ')[:200])
