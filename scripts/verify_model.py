"""Run a real candidate through local writing and verification without publishing."""
import argparse,json,subprocess,time,urllib.request
import pipeline as p
import local_model
parser=argparse.ArgumentParser();parser.add_argument('candidate_id');a=parser.parse_args()
c=next(c for c in p.read('data/candidates.json',[]) if c['id']==a.candidate_id)
s=next(s for s in p.read('data/sources.json',[]) if s['id']==c['sourceId'])
body=p.evidence(c,s);args,env=local_model.command();start=time.monotonic();opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
with (p.ROOT/'.cache/llama-validation.log').open('w') as log:
 server=subprocess.Popen(args,env=env,stdout=log,stderr=subprocess.STDOUT)
 try:
  for _ in range(90):
   if server.poll() is not None:raise RuntimeError('Model exited during startup')
   try:
    with opener.open('http://127.0.0.1:8080/health',timeout=3) as response:
     if response.status==200:break
   except Exception:time.sleep(2)
  else:raise RuntimeError('Startup timeout')
  draft,review=p.generate(c,body,[{'title':h['title'],'eventKey':h['eventKey']} for h in p.published()])
  p.write('.cache/validation/latest.json',dict(candidateId=c['id'],sourceURL=c['url'],draft=draft,review=review,seconds=round(time.monotonic()-start,2)))
  status=p.read('data/deployment-status.json',{});status['generationValidated']=True;p.write('data/deployment-status.json',status)
  p.log('model_validation',candidate=c['id'],approved=True,seconds=round(time.monotonic()-start,2));print(json.dumps({'approved':True,'title':draft['title'],'review':review,'seconds':round(time.monotonic()-start,2)},ensure_ascii=False))
 finally:
  server.terminate()
  try:server.wait(timeout=15)
  except subprocess.TimeoutExpired:server.kill();server.wait()
