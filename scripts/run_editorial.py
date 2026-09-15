"""Consume a completed Scout snapshot, start CPU-only model when an edition is due, publish, clean up."""
import argparse,fcntl,json,os,subprocess,time,urllib.request
import pipeline as p
import edition_schedule as schedule
import scout_snapshot
import editorial_selection
import publish_edition
import local_model

# The local model was repeatedly producing otherwise useful drafts with headline
# fields just outside the public schema, plus an occasional malformed JSON object.
# Repair only presentation shape here; factual, evidence, length and verifier gates
# remain untouched inside pipeline.validate_draft / pipeline.generate.
_BASE_VALIDATE_DRAFT=p.validate_draft
_BASE_MODEL_CALL=p.model_call

def _trim_at_word(value,max_chars):
 value=' '.join(str(value).split())
 if len(value)<=max_chars:return value
 clipped=value[:max_chars+1].rsplit(' ',1)[0].rstrip(' ,;:-')
 return clipped if clipped else value[:max_chars].rstrip(' ,;:-')

def _validate_draft_with_safe_shape(draft,body):
 if isinstance(draft,dict):
  draft=dict(draft)
  if isinstance(draft.get('title'),str):draft['title']=_trim_at_word(draft['title'],130)
  if isinstance(draft.get('description'),str):draft['description']=_trim_at_word(draft['description'],240)
 return _BASE_VALIDATE_DRAFT(draft,body)

def _model_call_with_json_retry(system,payload,max_tokens=800):
 try:return _BASE_MODEL_CALL(system,payload,max_tokens)
 except json.JSONDecodeError:
  retry_system=system+'\nCRITICAL OUTPUT CONTRACT: return exactly one syntactically valid JSON object. Escape every internal quote and newline correctly; emit no prose before or after the JSON.'
  return _BASE_MODEL_CALL(retry_system,payload,max_tokens)

p.validate_draft=_validate_draft_with_safe_shape
p.model_call=_model_call_with_json_retry
p.WRITER+='''\nSTRICT PUBLICATION SHAPE: title must contain 15-130 characters and description 35-240 characters. Keep both concise enough to fit those limits before returning JSON. Do not compensate for these limits by removing verified context from the article body.'''

def run(force=False,dry_run=False,limit=30):
 state=p.read('data/publishing-state.json',{})
 if state.get('paused'):return {'paused':True}
 try:snapshot=scout_snapshot.consume()
 except (ValueError,TypeError,KeyError) as error:
  p.log('edition_held',reason='no_valid_scout_snapshot',code=str(error),restore=p.read('.cache/scout/restore.json',{}))
  return {'publication':'held_no_valid_scout_snapshot'}
 observed=snapshot['state']
 result=dict(sourcesOK=observed['sourcesReached'],collected=observed.get('newCandidates',0),errors=observed.get('sourceErrors',[]),snapshotRunId=snapshot['runId'],snapshotCompletedAt=snapshot['completedAt'])
 state['lastCollectedAt']=snapshot['completedAt'];p.write('data/publishing-state.json',state)
 if os.environ.get('GITHUB_ACTIONS')=='true':
  status=p.read('data/deployment-status.json',{});status.update(repository=os.environ['GITHUB_REPOSITORY'],scheduleActive=True,notes='Escuta contínua; fechamentos editoriais regulares às 08h, 13h, 18h e 22h em America/Sao_Paulo, com meta de até 20 matérias verificadas por edição. Uma pauta fica de fora quando não passa por confirmação por duas organizações independentes e pela validação editorial.');p.write('data/deployment-status.json',status)
 state=p.read('data/publishing-state.json',{})
 if not force and not schedule.is_due(state):return dict(collection=result,publication='not_due',nextEdition=schedule.next_label())
 sources={s['id']:s for s in p.read('data/sources.json',[])}
 candidates=editorial_selection.eligible(p.read('data/candidates.json',[]),sources)
 related=editorial_selection.groups(candidates)
 independent=[g for g in related if p.corroborated(g,sources)]
 primary=[g for g in related if editorial_selection.authoritative_primary(g,sources) and not p.corroborated(g,sources)]
 publishable=[g for g in related if editorial_selection.publishable(g,sources)]
 result['selection']=dict(eligible=len(candidates),relatedGroups=len(related),independentCandidates=len(independent),primaryCandidates=len(primary),publishableCandidates=len(publishable))
 if not publishable:return dict(collection=result,publication='held_no_publishable_candidate_group')
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
   publication=publish_edition.publish(force,dry_run,limit)
   result=dict(collection=result,**publication)
   if result.get('published',0)>0 or result.get('approvedDrafts',0)>0:
    status=p.read('data/deployment-status.json',{});status['generationValidated']=True;p.write('data/deployment-status.json',status)
   return result
  finally:
   server.terminate()
   try:server.wait(timeout=15)
   except subprocess.TimeoutExpired:server.kill();server.wait()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--force',action='store_true',help='Publica edição extraordinária fora do cronograma');parser.add_argument('--dry-run',action='store_true');parser.add_argument('--limit',type=int,default=30);a=parser.parse_args();(p.ROOT/'.cache').mkdir(exist_ok=True)
 with (p.ROOT/'.cache/editorial.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  started=p.iso()
  try:
   result=run(a.force,a.dry_run,a.limit)
   p.write('data/operation-state.json',dict(startedAt=started,finishedAt=p.iso(),status='degraded' if result.get('collection',{}).get('errors') or result.get('held') or str(result.get('publication','')).startswith('held_') else 'completed',runId=os.environ.get('GITHUB_RUN_ID'),result=result))
   p.log('runner_completed',result=result)
   print(json.dumps(result))
  except Exception as e:
   p.write('data/operation-state.json',dict(startedAt=started,finishedAt=p.iso(),status='failed',runId=os.environ.get('GITHUB_RUN_ID'),error=type(e).__name__))
   p.log('error',stage='runner',code=type(e).__name__);raise
