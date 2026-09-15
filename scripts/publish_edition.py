"""Edition-aware publisher built on the conservative editorial pipeline."""
from __future__ import annotations
import collections,datetime as dt,hashlib,json,re,time,urllib.error
import pipeline as p
import edition_schedule as schedule
import editorial_selection
import editorial_media

CATEGORIES=['Brasil','Mundo','Política','Economia','Tecnologia','Ciência','Cultura','Esportes','Saúde','Meio Ambiente']
GENERIC_EDITORIAL_COVER='/og.png'

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

def verification_priority(group):
 """Prefer groups whose independent routes already carry recent URL-bound evidence."""
 cached=sum(1 for item in group if editorial_selection.cached_evidence(item))
 newest=max((item.get('publishedAt','') for item in group),default='')
 return cached,newest

def verification_queue(groups,publish_limit,category_limit):
 """Build a deeper verification queue; publication ceilings are enforced on successes, not attempts."""
 if publish_limit<=0:return []
 attempt_total=max(publish_limit,min(len(groups),max(16,publish_limit*3)))
 attempt_per_category=max(category_limit,min(10,category_limit*5))
 ranked=sorted(groups,key=verification_priority,reverse=True)
 return balanced_groups(ranked,max_total=attempt_total,max_per_category=attempt_per_category)

def editorial_cover_media(candidate):
 """Safe first-party fallback. The frontend renders /og.png as an article-specific EditorialCover."""
 title=str(candidate.get('title') or 'matéria').strip()
 return dict(path=GENERIC_EDITORIAL_COVER,alt=f'Capa editorial tipográfica do APURANTE para: {title}.',credit='Apurante Editorial · Capa editorial original.')

def resolve_media(group,candidate,body,used_images=()):
 """Prefer approved/explicitly licensed media; never hold verified journalism solely for an image outage."""
 for item in group:
  try:return p.approved_media(item,used_images)
  except ValueError:continue
 try:return editorial_media.acquire(candidate,body,used_images)
 except (ValueError,urllib.error.URLError,TimeoutError,RuntimeError,KeyError,TypeError,json.JSONDecodeError) as error:
  code=str(error) if isinstance(error,ValueError) else type(error).__name__
  p.log('media_fallback',candidate=candidate.get('id'),code=code)
  return editorial_cover_media(candidate)

def publish(force=False,dry_run=False,limit=30):
 start=time.monotonic();state=p.read('data/publishing-state.json',{});history=p.published()
 if history:state['lastPublishedAt']=max([h['publishedAt'] for h in history]+([state['lastPublishedAt']] if state.get('lastPublishedAt') else []))
 if state.get('paused') or (not force and not schedule.is_due(state)):return dict(published=0,reason='paused_or_not_due')
 mode='extraordinary' if force else 'scheduled';edition_slot=p.iso() if force else schedule.slot_iso();edition_label='Edição extraordinária' if force else schedule.slot_label()
 edition_id=f'{mode}:{edition_slot}'
 all_items=p.read('data/candidates.json',[]);sources={s['id']:s for s in p.read('data/sources.json',[])};urls={u for h in history for u in h['sourceUrls']};used_images={h.get('image') for h in history if h.get('image')};reserved_images=set();eligible=[]
 for c in all_items:
  if c['url'] in urls:c['status']='published'
 eligible=editorial_selection.eligible(all_items,sources)
 cfg=schedule.config();publish_limit=max(0,min(int(limit),int(cfg.get('maxArticlesPerEdition',30))));category_limit=max(1,int(cfg.get('maxPerCategory',4)))
 corroborated_groups=[g for g in editorial_selection.groups(eligible) if p.corroborated(g,sources)]
 groups=verification_queue(corroborated_groups,publish_limit,category_limit)
 count=0;held=0;reasons=collections.Counter();processed=set();evidence_cache={};published_stamps=[];edition_slugs=[];category_counts=collections.Counter()
 for group in groups:
  if count>=publish_limit or time.monotonic()-start>1800:break
  if any(x['id'] in processed for x in group):continue
  c=p.choose_lead(group,sources,history)
  if category_counts[c.get('category','Outros')]>=category_limit:continue
  try:
   if not p.corroborated(group,sources):raise ValueError('independent_confirmation_required')
   group,body=editorial_selection.verify(group,sources,evidence_cache)
   c=p.choose_lead(group,sources,history)
   if category_counts[c.get('category','Outros')]>=category_limit:continue
   draft,review=p.generate(c,body,[{'title':h['title'],'eventKey':h['eventKey']} for h in history])
   if any(h.get('eventKey')==draft['eventKey'] for h in history):raise ValueError('duplicate_published_event')
   if dry_run:
    media=None
    for item in group:
     try:media=p.approved_media(item,used_images|reserved_images);break
     except ValueError:continue
    if media is None:media=editorial_cover_media(c)
   else:media=resolve_media(group,c,body,used_images|reserved_images)
   if media['path']!=GENERIC_EDITORIAL_COVER:reserved_images.add(media['path'])
   slug=re.sub(r'[^a-z0-9]+','-',p.normalized(draft['title'])).strip('-')[:80].rstrip('-')+'-'+c['id'][:6];stamp=p.iso()
   article_id=f"apr-{stamp[:10]}-{c['id'][:7]}";takeaways=[f.get('claim') for f in draft.get('facts',[]) if isinstance(f,dict) and f.get('claim')][:3] or [draft['description']]
   lead_org=p.source_organization(c,sources.get(c.get('sourceId'),{}))
   meta=dict(articleId=article_id,title=draft['title'],slug=slug,description=draft['description'],quickTakeaways=takeaways,publishedAt=stamp,updatedAt=stamp,category=c['category'],tags=list(dict.fromkeys([c['category']]+draft['tags'])),image=media['path'],imageAlt=media['alt'],imageCredit=media['credit'],status='published',confidence=p.publication_confidence(group,sources),verificationPolicyVersion=2,relevance=p.rank(c['title'],c.get('sourceType')),eventKey=draft['eventKey'],editionId=edition_id,editionType=mode,editionSlot=edition_slot,editionLabel=edition_label,leadSourceOrganization=lead_org,sources=p.unique_sources(group,sources),corrections=[],author='Apurante Editorial',production='Apurante Editorial: texto original, evidência rastreável, confirmação independente e revisão factual automatizada')
   if dry_run:
    p.write(f'.cache/drafts/{c["id"]}.json',dict(metadata=meta,paragraphs=draft['paragraphs'],review=review));count+=1;continue
   target=p.ROOT/'content/news'/f'{slug}.md'
   with target.open('x') as f:f.write('---\n'+json.dumps(meta,ensure_ascii=False,indent=2)+'\n---\n\n'+p.render_article(draft))
   ids={x['id'] for x in group};processed.update(ids)
   for x in all_items:
    if x['id'] in ids:x['status']='published'
   record=dict(slug=slug,title=meta['title'],eventKey=meta['eventKey'],publishedAt=stamp,image=meta['image'],sourceUrls=[x['url'] for x in group],sourceOrganizations=list(p.independent_organizations(group,sources)),leadSourceOrganization=lead_org,editionId=edition_id,editionType=mode,editionSlot=edition_slot)
   history.append(record);published_stamps.append(stamp);edition_slugs.append(slug);category_counts[c['category']]+=1
   p.write(f'data/evidence/{c["id"]}.json',dict(sourceUrls=record['sourceUrls'],sourceOrganizations=record['sourceOrganizations'],sourceSha256=hashlib.sha256(body.encode()).hexdigest(),verifiedAt=stamp,claims=[f['claim'] for f in draft['facts']],review=review,model='Qwen3-4B-Q4_K_M',checks=['numeric anchors','copy detection','format validation','independent organizations','same-model factual review','event deduplication']))
   count+=1
  except (urllib.error.URLError,TimeoutError) as e:
   held+=1;reasons[type(e).__name__]+=1
   p.log('error',stage='generation',candidate=c['id'],code=type(e).__name__);break
  except Exception as e:
   held+=1;reason=str(e) if isinstance(e,ValueError) else type(e).__name__;reasons[reason]+=1
   p.log('error',stage='verification',candidate=c['id'],code=str(e) if isinstance(e,ValueError) else type(e).__name__)
 if not dry_run:
  p.write('data/candidates.json',all_items)
  if count:
   state['history']=history;state['lastPublishedAt']=max(published_stamps);state['editionCount']=state.get('editionCount',0)+1
   if mode=='scheduled':state['lastEditionSlot']=edition_slot
   editions=state.get('editionHistory',[]);editions.append(dict(id=edition_id,type=mode,slot=edition_slot,label=edition_label,publishedAt=max(published_stamps),articleCount=count,categories=dict(category_counts),slugs=edition_slugs));state['editionHistory']=editions[-120:]
   p.write('data/publishing-state.json',state)
 p.log('publication',editionId=edition_id,editionType=mode,eligible=len(eligible),selected=len(groups),held=held,holdReasons=dict(reasons),published=0 if dry_run else count,dryRunApproved=count if dry_run else 0,categories=dict(category_counts),seconds=round(time.monotonic()-start,2))
 return dict(published=0 if dry_run else count,approvedDrafts=count if dry_run else 0,held=held,holdReasons=dict(reasons),editionId=edition_id,editionType=mode,categories=dict(category_counts))
