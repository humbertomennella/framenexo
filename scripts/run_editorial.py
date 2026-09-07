"""Collect, start CPU-only model when an edition is due, publish, clean up."""
import argparse,fcntl,json,os,subprocess,time,urllib.request
import pipeline as p
import local_model
def run(force=False,dry_run=False,limit=15):
 state=p.read('data/publishing-state.json',{})
 if state.get('paused'):return {'paused':True}
 result=p.collect()
 if not result['sourcesOK']:raise RuntimeError('all_sources_failed')
 if os.environ.get('GITHUB_ACTIONS')=='true':
  status=p.read('data/deployment-status.json',{});status.update(repository=os.environ['GITHUB_REPOSITORY'],scheduleActive=True,notes='Rotina executada no GitHub. O site mostra os dados do último build.');p.write('data/deployment-status.json',status)
 state=p.read('data/publishing-state.json',{})
 if not force and not p.due(state):return dict(collection=result,publication='not_due')
 if not any(c['status']=='candidate' and c['sourceType']=='primary' and c['relevance']>=65 for c in p.read('data/candidates.json',[])):return dict(collection=result,publication='no_eligible_candidates')
 args,env=local_model.command();opener=urllib.request.build_opener(urllib.request.ProxyHandler({}));(p.ROOT/'.cache').mkdir(exist_ok=True)
 with (p.ROOT/'.cache/llama-server.log').open('w') as logfile:
  server=subprocess.Popen(args,env=env,stdout=logfile,stderr=subprocess.STDOUT)
  try:
   for attempt in range(90):
    if server.poll() is not None:raise RuntimeError('model_server_exited')
    try:
     with opener.open('http://127.0.0.1:8080/health',timeout=3) as r:
      if r.status==200:break
    except Exception:time.sleep(2)
   else:raise RuntimeError('model_start_timeout')
   result=p.publish(force,dry_run,limit)
   if result.get('published',0)>0 or result.get('approvedDrafts',0)>0:
    status=p.read('data/deployment-status.json',{});status['generationValidated']=True;p.write('data/deployment-status.json',status)
   return result
  finally:
   server.terminate()
   try:server.wait(timeout=15)
   except subprocess.TimeoutExpired:server.kill();server.wait()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--force',action='store_true');parser.add_argument('--dry-run',action='store_true');parser.add_argument('--limit',type=int,default=15);a=parser.parse_args();(p.ROOT/'.cache').mkdir(exist_ok=True)
 with (p.ROOT/'.cache/editorial.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:print(json.dumps(run(a.force,a.dry_run,a.limit)))
  except Exception as e:p.log('error',stage='runner',code=type(e).__name__);raise
