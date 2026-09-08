"""Pinned local inference. No API credentials or metered service."""
from pathlib import Path
import hashlib,json,os,platform,subprocess,tarfile,urllib.request
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache/model'
def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def download(url,path,expected):
 if path.exists() and digest(path)==expected:return
 tmp=path.with_suffix('.part')
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'LinhaZeroSetup/1.0'}),timeout=90) as src,open(tmp,'wb') as dst:
  for block in iter(lambda:src.read(1024*1024),b''):dst.write(block)
 if digest(tmp)!=expected:
  tmp.unlink(missing_ok=True);raise ValueError('download_checksum_mismatch')
 tmp.replace(path)
def install():
 if platform.system()!='Linux' or platform.machine() not in ('x86_64','AMD64'):raise RuntimeError('Use Linux x86_64 / WSL2 for local inference')
 lock=json.loads((ROOT/'data/model-lock.json').read_text());CACHE.mkdir(parents=True,exist_ok=True)
 archive=CACHE/'llama.tar.gz';weights=CACHE/'model.gguf';runtime=CACHE/'runtime';marker=runtime/'.verified-archive'
 download(lock['engineUrl'],archive,lock['engineSha256'])
 if not marker.exists() or marker.read_text()!=lock['engineSha256']:
  runtime.mkdir(exist_ok=True)
  with tarfile.open(archive) as tar:tar.extractall(runtime,filter='data')
  marker.write_text(lock['engineSha256'])
 server=next(runtime.rglob('llama-server'));server.chmod(0o755)
 download(lock['modelUrl'],weights,lock['modelSha256'])
 return server,weights
def command():
 server,weights=install();env=os.environ.copy();env['LD_LIBRARY_PATH']=str(server.parent)
 args=[str(server),'-m',str(weights),'--host','127.0.0.1','--port','8080','-c','8192','-t',str(min(os.cpu_count() or 2,4)),'-np','1','--jinja','--reasoning-budget','0']
 return args,env
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('action',choices=['install','serve']);a=p.parse_args()
 if a.action=='install':install();print('Pinned engine and model verified.')
 else:
  args,env=command();raise SystemExit(subprocess.call(args,env=env))
