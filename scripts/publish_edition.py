"""Edition-aware publisher built on the conservative editorial pipeline."""
from __future__ import annotations
import collections,datetime as dt,hashlib,re,time,urllib.error
import pipeline as p
import edition_schedule as schedule

CATEGORIES=['Brasil','Mundo','Política','Economia','Tecnologia','Ciência','Cultura','Esportes','Saúde','Meio Ambiente']

def balanced_groups(groups,max_total=None,max_per_category=None):
 """Round-robin categories so one busy desk cannot consume the whole edition."""
 cfg=schedule.config();max_total=int(max_total or cfg.get('maxArticlesPerEdition',30));max_per_category=int(max_per_category or cfg.get('maxPerCategory',4))
 buckets=collections.defaultdict(list)
 for group in groups:
  lead=max(group,key=lambda item:item.get('relevance',0));buckets[lead.get('category','Outros')].append(group)
 order=CATEGORIES+[key for key in buckets if key not in CATEGORIES];selected=[]
 for _ in range(max_per_category):
  for category in order:
   if buckets[category] and len(selected)<max_total:selected.append(buckets[category].pop(0))
 return selected

def publish(force=False,dry_run=False,limit=30):
 start=time.monotonic();state=p.read('data/publishing-state.json',{});history=p.published()
 if history:state['lastPublishedAt']=max([h['publishedAt'] for h in history]+([state['lastPublishedAt']] if state.get('lastPublishedAt') else []))
 if state.get('paused') or (not force and not schedule.is_due(state)):return dict(published=0,reason='paused_or_not_due')
 mode='extraordinary' if force else 'scheduled';edition_slot=p.iso() if force else schedule.slot_iso();edition_label='Edição extraordinária' if force else schedule.slot_label()
 edition_id=f'{mode}:{edition_slot}'
 all_items=p.read('data/candidates.json',[]);sources={s['id']:s for s in p.read('data/sources.json',[])};urls={u for h in history for u in h['sourceUrls']};used_images={h.get('image') for h in history if h.get('image')};reserved_images=set();eligible=[]
 for c in all_items:
  if c['url'] in urls:
   if c['status']=='candidate':c['status']='published'
   continue
  threshold=65 if c.get('sourceType')=='primary' else 55
  stamp=p.date(c.get('publishedAt'))
  if c['status']=='candidate' and c.get('sourceId') in sources and c.get('relevance',0)>=threshold and not p.needs_editor(c['title']) and stamp and p.now()-dt.timedelta(days=7)<=stamp<=p.now():eligible.append(c)
 groups=balanced_groups(p.clusters(eligible),max_total=max(0,min(int(limit),int(schedule.config().get('maxArticlesPerEdition',30)))))
 count=0;held=0;published_stamps=[];edition_slugs=[];category_counts=collections.Counter()
 for group in groups:
  if time.monotonic()-start>1800:break
  c=p.choose_lead(group,sources,history)
  try:
   if not p.corroborated(group,sources):raise ValueError('independent_confirmation_required')
   media=None
   for item in group:
    try:media=p.approved_media(item,used_images|reserved_images);break
    except ValueError:continue
   if media is None:raise ValueError('approved_media_required')
   reserved_images.add(media['path'])
   body=p.combined_evidence(group,sources);draft,review=p.generate(c,body,[{'title':h['title'],'eventKey':h['eventKey']} for h in history])
   if any(h.get('eventKey')==draft['eventKey'] for h in history):raise ValueError('duplicate_published_event')
   slug=re.sub(r'[^a-z0-9]+','-',p.normalized(draft['title'])).strip('-')[:80].rstrip('-')+'-'+c['id'][:6];stamp=p.iso()
   article_id=f"apr-{stamp[:10]}-{c['id'][:7]}";takeaways=[f.get('claim') for f in draft.get('facts',[]) if isinstance(f,dict) and f.get('claim')][:3] or [draft['description']]
   lead_org=p.source_organization(c,sources.get(c.get('sourceId'),{}))
   meta=dict(articleId=article_id,title=draft['title'],slug=slug,description=draft['description'],quickTakeaways=takeaways,publishedAt=stamp,updatedAt=stamp,category=c['category'],tags=list(dict.fromkeys([c['category']]+draft['tags'])),image=media['path'],imageAlt=media['alt'],imageCredit=media['credit'],status='published',confidence=p.publication_confidence(group,sources),verificationPolicyVersion=2,relevance=c['relevance'],eventKey=draft['eventKey'],editionId=edition_id,editionType=mode,editionSlot=edition_slot,editionLabel=edition_label,leadSourceOrganization=lead_org,sources=p.unique_sources(group,sources),corrections=[],author='Apurante Editorial',production='Apurante Editorial: texto original, evidência rastreável, confirmação independente e revisão factual automatizada')
   if dry_run:
    p.write(f'.cache/drafts/{c["id"]}.json',dict(metadata=meta,paragraphs=draft['paragraphs'],review=review));count+=1;continue
   target=p.ROOT/'content/news'/f'{slug}.md'
   with target.open('x') as f:f.write('---\n'+p.json.dumps(meta,ensure_ascii=False,indent=2)+'\n---\n\n'+p.render_article(draft))
   for x in group:x['status']='published'
   record=dict(slug=slug,title=meta['title'],eventKey=meta['eventKey'],publishedAt=stamp,image=meta['image'],sourceUrls=[x['url'] for x in group],sourceOrganizations=list(p.independent_organizations(group,sources)),leadSourceOrganization=lead_org,editionId=edition_id,editionType=mode,editionSlot=edition_slot)
   history.append(record);published_stamps.append(stamp);edition_slugs.append(slug);category_counts[c['category']]+=1
   p.write(f'data/evidence/{c["id"]}.json',dict(sourceUrls=record['sourceUrls'],sourceOrganizations=record['sourceOrganizations'],sourceSha256=hashlib.sha256(body.encode()).hexdigest(),verifiedAt=stamp,claims=[f['claim'] for f in draft['facts']],review=review,model='Qwen3-4B-Q4_K_M',checks=['numeric anchors','copy detection','format validation','independent organizations','same-model factual review','event deduplication']))
   count+=1
  except (urllib.error.URLError,TimeoutError) as e:
   p.log('error',stage='generation',candidate=c['id'],code=type(e).__name__);break
  except Exception as e:
   held+=1
   if not dry_run:
    for x in group:x['status']='needs_review'
   p.log('error',stage='verification',candidate=c['id'],code=str(e) if isinstance(e,ValueError) else type(e).__name__)
 if not dry_run:
  p.write('data/candidates.json',all_items)
  if count:
   state['history']=history;state['lastPublishedAt']=max(published_stamps);state['editionCount']=state.get('editionCount',0)+1
   if mode=='scheduled':state['lastEditionSlot']=edition_slot
   editions=state.get('editionHistory',[]);editions.append(dict(id=edition_id,type=mode,slot=edition_slot,label=edition_label,publishedAt=max(published_stamps),articleCount=count,categories=dict(category_counts),slugs=edition_slugs));state['editionHistory']=editions[-120:]
   p.write('data/publishing-state.json',state)
 p.log('publication',editionId=edition_id,editionType=mode,eligible=len(eligible),selected=len(groups),held=held,published=0 if dry_run else count,dryRunApproved=count if dry_run else 0,categories=dict(category_counts),seconds=round(time.monotonic()-start,2))
 return dict(published=0 if dry_run else count,approvedDrafts=count if dry_run else 0,held=held,editionId=edition_id,editionType=mode,categories=dict(category_counts))
