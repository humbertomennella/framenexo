"""Immutable, bounded Scout snapshots. No git writes and no publication authority."""
from __future__ import annotations
import argparse, hashlib, io, json, os, re, urllib.request, urllib.error, zipfile
import datetime as dt
import pipeline as p

NAME='apurante-scout-v1'
MAX_BYTES=12_000_000
MAX_AGE=dt.timedelta(hours=24)
TRANSIENT={f'data/{name}.json':f'.cache/scout/{name}.json' for name in
           ('candidates','scout-state','editorial-log','publishing-state')}

def digest(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def prune(items, at=None):
    at=at or p.now(); kept={}
    for item in items:
        stamp=p.date(item.get('publishedAt'))
        if not stamp or not at-dt.timedelta(days=7)<=stamp<=at+dt.timedelta(minutes=5):continue
        if item.get('status') in ('expired','published'):continue
        row=dict(item);row['url']=p.canonical_url(row['url'])
        kept.setdefault(row['url'],row)
    return list(kept.values())[-2000:]

def create(items,state):
    payload={'version':1,'repository':os.environ.get('GITHUB_REPOSITORY','humbertomennella/framenexo'),
             'runId':str(os.environ.get('GITHUB_RUN_ID','local')),
             'runAttempt':int(os.environ.get('GITHUB_RUN_ATTEMPT','1')),
             'completedAt':p.iso(),'candidates':prune(items),'state':state}
    return {'payload':payload,'sha256':digest(payload)}

def validate(document,run=None,at=None):
    if not isinstance(document,dict):raise ValueError('invalid_snapshot')
    if len(json.dumps(document,ensure_ascii=False).encode())>MAX_BYTES:raise ValueError('snapshot_too_large')
    payload=document.get('payload')
    if not isinstance(payload,dict) or document.get('sha256')!=digest(payload):raise ValueError('snapshot_checksum')
    if payload.get('version')!=1 or payload.get('repository')!=os.environ.get('GITHUB_REPOSITORY','humbertomennella/framenexo'):raise ValueError('snapshot_origin')
    at=at or p.now();stamp=p.date(payload.get('completedAt')) if isinstance(payload.get('completedAt'),str) else None
    if not stamp or not dt.timedelta(minutes=-5)<=at-stamp<=MAX_AGE:raise ValueError('snapshot_stale_or_future')
    if run and (payload.get('runId')!=str(run['id']) or payload.get('runAttempt')!=run.get('run_attempt',1)):raise ValueError('snapshot_run_mismatch')
    state=payload.get('state',{})
    if not isinstance(state,dict):raise ValueError('snapshot_state')
    if type(state.get('sourcesReached')) is not int:raise ValueError('snapshot_source_count')
    if state.get('publishingAllowed') is not False or state.get('status') not in ('healthy','degraded') or not state.get('sourcesReached',0)>0:raise ValueError('snapshot_failed_collection')
    items=payload.get('candidates')
    if not isinstance(items,list) or len(items)>2000:raise ValueError('snapshot_candidates')
    for item in items:
        if not isinstance(item,dict) or any(not isinstance(item.get(k),str) or not item[k] for k in ('id','url','title','sourceId','sourceName','sourceType','category','publishedAt','status')):raise ValueError('snapshot_candidate_schema')
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,100}',item['id']) or not p.date(item['publishedAt']):raise ValueError('snapshot_candidate_id_date')
        if type(item.get('relevance')) not in (int,float) or not 0<=item['relevance']<=100:raise ValueError('snapshot_relevance')
        if item['status'] not in ('candidate','needs_review','blocked'):raise ValueError('snapshot_candidate_status')
        if not item['url'].startswith('https://'):raise ValueError('snapshot_candidate_url')
    return payload

class NoAuthRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        # GitHub redirects artifact downloads to signed storage URLs. Never forward the token.
        if not newurl.startswith('https://'):raise ValueError('insecure_artifact_redirect')
        redirected=super().redirect_request(req,fp,code,msg,headers,newurl)
        if redirected:redirected.remove_header('Authorization')
        return redirected

def api(path,binary=False):
    repo=os.environ['GITHUB_REPOSITORY']
    if not re.fullmatch(r'[\w.-]+/[\w.-]+',repo):raise ValueError('invalid_repository')
    request=urllib.request.Request('https://api.github.com/repos/'+repo+path,headers={
        'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],'Accept':'application/vnd.github+json'})
    with urllib.request.build_opener(NoAuthRedirect()).open(request,timeout=30) as response:
        raw=response.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError('artifact_too_large')
    return raw if binary else json.loads(raw)

def unpack(raw,run):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries=archive.infolist()
        if len(entries)!=1 or entries[0].filename!='snapshot.json' or entries[0].file_size>MAX_BYTES:raise ValueError('artifact_layout')
        document=json.loads(archive.read(entries[0]))
    validate(document,run)
    return document

def restore(required=False):
    """Only successful main Scout runs; fallback to an older valid artifact, never a failed run."""
    errors=[]
    try:
        runs=[]
        for page in range(1,5):
            batch=api(f'/actions/workflows/scout.yml/runs?branch=main&status=success&per_page=100&page={page}').get('workflow_runs',[])
            runs.extend(batch)
            if len(batch)<100:break
        # Completion time, not queue/create order, handles delayed and rerun executions.
        runs.sort(key=lambda r:r.get('updated_at',''),reverse=True)
        for run in runs:
            if run.get('status')!='completed' or run.get('conclusion')!='success' or run.get('head_branch')!='main' or run.get('event') not in ('schedule','push','workflow_dispatch'):continue
            if run.get('head_repository',{}).get('full_name')!=os.environ['GITHUB_REPOSITORY']:continue
            if str(run['id'])==os.environ.get('GITHUB_RUN_ID'):continue
            finished=p.date(run.get('updated_at'))
            if not finished or p.now()-finished>MAX_AGE:continue
            try:
                artifacts=api(f"/actions/runs/{run['id']}/artifacts?per_page=100").get('artifacts',[])
                expected=f"{NAME}-{run['id']}-{run.get('run_attempt',1)}"
                for artifact in artifacts:
                    if artifact.get('name')!=expected or artifact.get('expired'):continue
                    document=unpack(api(f"/actions/artifacts/{artifact['id']}/zip",True),run)
                    p.write('.cache/scout/input.json',document)
                    result={'status':'restored','runId':str(run['id']),'completedAt':document['payload']['completedAt'],'errors':errors}
                    p.write('.cache/scout/restore.json',result);return result
            except (ValueError,KeyError,TypeError,zipfile.BadZipFile,urllib.error.URLError,TimeoutError) as error:
                errors.append({'runId':str(run['id']),'code':type(error).__name__})
    except (ValueError,KeyError,urllib.error.URLError,TimeoutError) as error:
        errors.append({'code':type(error).__name__})
    # Clear any previous local input so a repeated invocation cannot consume stale leftovers.
    (p.ROOT/'.cache/scout/input.json').unlink(missing_ok=True)
    result={'status':'unavailable','errors':errors};p.write('.cache/scout/restore.json',result)
    if required:raise RuntimeError('no_valid_completed_scout_snapshot')
    return result

def consume():
    payload=validate(p.read('.cache/scout/input.json',{}))
    items=prune(payload['candidates'])
    # Published files are the durable authority. Preserve editorial holds from the last closing.
    history=p.published();published_urls={p.canonical_url(url) for a in history for url in a['sourceUrls']}
    decisions={p.canonical_url(c['url']):c for c in p.read('data/candidates.json',[])}
    for item in items:
        previous=decisions.get(item['url'],{})
        if item['url'] in published_urls:item['status']='published'
        elif previous.get('status') in ('needs_review','blocked'):item['status']=previous['status']
        if 'media' in previous:item['media']=previous['media']
    p.write('data/candidates.json',items)
    # Static status page receives only the actual observation timestamp, at closing.
    p.write('data/scout-state.json',payload['state'])
    return payload

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--required',action='store_true');args=parser.parse_args()
    print(json.dumps(restore(args.required)))
