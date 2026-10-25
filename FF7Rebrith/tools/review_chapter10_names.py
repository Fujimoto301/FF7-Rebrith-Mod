"""Apply established spellings only to new reviewed lines; old base is frozen."""
from prepare_chapter9 import W,read,write
def main():
    for p in sorted((W/'translations/chapter10').glob('batch-*.json')):
        v=read(p)
        for k,t in list(v.items()):
            v[k]=t.replace('เคทซี','เค็ตชี').replace('แซ็ค','แซ็ก').replace('กองกาก้า','กอนกาก้า').replace('โซลเยอร์','โซลเจอร์').replace('โพชัน','โพชั่น').replace(' AI','เอไอ').replace('\r\r\n','\r\n')
        if '124' in v:v['124']='แซ็ก ขึ้นไปดูที่ชั้น2หน่อยสิ'
        if '408' in v:v['408']='40…?'
        if '1103' in v:v['1103']='<i>ไม่เป็นไรหรอก</i>'
        write(p,v)
if __name__=='__main__':main()
