import sys
import build_chapter1 as b
import verify_chapter1 as v
if __name__=='__main__':
    if '--verify' in sys.argv:v.main(chapter6_working=True,review_working='reference/chapter14-build.json')
    else:b.main(chapter6_working=True,review_working='reference/chapter14-build.json',text_only='--text-only' in sys.argv)
