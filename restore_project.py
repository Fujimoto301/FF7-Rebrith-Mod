"""Restore a deduplicated FF7 project backup into a NEW or EMPTY directory."""
import argparse,hashlib,json,os,shutil,zipfile
from pathlib import Path

def digest(stream):
 h=hashlib.sha256()
 for chunk in iter(lambda:stream.read(4*1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--archive',required=True,type=Path)
 p.add_argument('--destination',type=Path)
 p.add_argument('--verify-only',action='store_true')
 a=p.parse_args()
 with zipfile.ZipFile(a.archive) as z:
  m=json.loads(z.read('manifest.json'))
  if m.get('format')!='sha256-deduplicated-zip-v1':raise SystemExit('Unsupported backup format')
  if a.verify_only:
   for sha in sorted({x['sha256'] for x in m['files']}):
    with z.open('objects/'+sha) as f:
     if digest(f)!=sha:raise SystemExit('Checksum mismatch: '+sha)
   print('Verified',len(m['files']),'file records');return
  if not a.destination:raise SystemExit('--destination is required unless --verify-only is used')
  target=a.destination.resolve()
  if target.exists() and any(target.iterdir()):raise SystemExit('Destination must be NEW or EMPTY. Existing files will not be overwritten.')
  target.mkdir(parents=True,exist_ok=True)
  def safe(rel):
   q=(target/rel).resolve()
   try:q.relative_to(target)
   except ValueError:raise SystemExit('Unsafe relative path: '+rel)
   return q
  for d in m['directories']:safe(d).mkdir(parents=True,exist_ok=True)
  restored={}
  for i,item in enumerate(m['files'],1):
   dst=safe(item['path']);dst.parent.mkdir(parents=True,exist_ok=True)
   if dst.exists():raise SystemExit('Refusing overwrite: '+str(dst))
   sha=item['sha256']
   if sha in restored:shutil.copyfile(restored[sha],dst)
   else:
    h=hashlib.sha256()
    with z.open('objects/'+sha) as src,dst.open('xb') as out:
     for b in iter(lambda:src.read(4*1024*1024),b''):h.update(b);out.write(b)
    if h.hexdigest()!=sha:raise SystemExit('Checksum mismatch: '+str(dst))
    restored[sha]=dst
   if dst.stat().st_size!=item['size']:raise SystemExit('Size mismatch: '+str(dst))
   os.utime(dst,ns=(item['mtime_ns'],item['mtime_ns']))
   if i%500==0:print(i,'/',len(m['files']),flush=True)
  print('Restored',len(m['files']),'files to',target)
if __name__=='__main__':main()
