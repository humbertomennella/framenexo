"""Check the built public artifact, including base-path routing and SEO records."""
from pathlib import Path
from html.parser import HTMLParser
import datetime as dt,hashlib,json,sys,urllib.parse,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist';errors=[]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.h1=0;self.ids=set();self.links=[];self.images=[];self.title='';self.in_title=False;self.meta={};self.canonical=None;self.schemas=[];self.in_schema=False;self.buffer=''
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='h1':self.h1+=1
  if a.get('id'):self.ids.add(a['id'])
  if tag=='title':self.in_title=True
  if tag=='a' and a.get('href'):self.links.append(a['href'])
  if tag=='img':self.images.append(a)
  if tag=='meta':self.meta[a.get('name') or a.get('property')]=a.get('content')
  if tag=='link' and a.get('rel')=='canonical':self.canonical=a.get('href')
  if tag=='script' and a.get('type')=='application/ld+json':self.in_schema=True;self.buffer=''
 def handle_data(self,text):
  if self.in_title:self.title+=text
  if self.in_schema:self.buffer+=text
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
  if tag=='script' and self.in_schema:
   self.in_schema=False
   try:self.schemas.append(json.loads(self.buffer))
   except json.JSONDecodeError:errors.append('Invalid JSON-LD')
def check(ok,msg):
 if not ok:errors.append(msg)
pages={}
for file in DIST.rglob('*.html'):
 page=Page();page.feed(file.read_text());pages[file]=page
 check(page.h1==1,f'{file.relative_to(DIST)}: expected one h1, got {page.h1}');check(bool(page.title),f'{file.name}: missing title');check(bool(page.meta.get('description')),f'{file.name}: missing description');check(bool(page.canonical and page.canonical.startswith('https://')),f'{file.name}: invalid canonical')
 for img in page.images:check('alt' in img,f'{file.name}: missing alt');check(img.get('width') and img.get('height'),f'{file.name}: image lacks dimensions')
check(DIST/'index.html' in pages,'Missing homepage');check(bool(list(DIST.glob('404*'))),'Missing 404')
base=urllib.parse.urlsplit(pages[DIST/'index.html'].canonical).path.rstrip('/')+'/'
origin=urllib.parse.urlsplit(pages[DIST/'index.html'].canonical).netloc
def resolve(url,current):
 p=urllib.parse.urlsplit(url)
 if p.scheme or p.netloc:return None,p.fragment
 if p.path.startswith('/'):
  check(p.path.startswith(base),f'Link escapes base path: {url}')
  rel=p.path[len(base):] if p.path.startswith(base) else p.path.lstrip('/')
  file=DIST/urllib.parse.unquote(rel)
 else:file=current.parent/urllib.parse.unquote(p.path) if p.path else current
 if file.is_dir():file=file/'index.html'
 if not file.exists() and file.suffix=='':file=file/'index.html'
 return file,p.fragment
for file,page in pages.items():
 for url in page.links+[i.get('src','') for i in page.images]:
  target,fragment=resolve(url,file)
  if target is None:continue
  check(target.exists(),f'{file.relative_to(DIST)}: broken link {url}')
  if fragment and target in pages:check(urllib.parse.unquote(fragment) in pages[target].ids,f'{file.name}: missing anchor {url}')
records=[]
used_image_paths=set();used_image_hashes=set();now=dt.datetime.now(dt.timezone.utc)
for file in (ROOT/'content/news').glob('*.md'):
 parts=file.read_text().split('---',2);check(len(parts)==3,f'{file.name}: frontmatter missing')
 try:a=json.loads(parts[1])
 except Exception:errors.append(f'{file.name}: invalid frontmatter');continue
 for key in ['title','slug','description','publishedAt','updatedAt','category','tags','image','imageCredit','status','sources','confidence']:check(key in a,f'{file.name}: missing {key}')
 if a.get('status')!='published':continue
 records.append(a);check(bool(a.get('sources')),f'{file.name}: sources missing');image_file=DIST/a['image'].lstrip('/');check(image_file.is_file(),f'{file.name}: image missing');check('<script' not in parts[2].lower(),f'{file.name}: unsafe body')
 try:published=dt.datetime.fromisoformat(a['publishedAt'].replace('Z','+00:00'));check(published<=now+dt.timedelta(minutes=5),f'{file.name}: publication date is in the future')
 except Exception:errors.append(f'{file.name}: invalid publication date')
 check(a['image'] not in used_image_paths,f'{file.name}: duplicate image path');used_image_paths.add(a['image'])
 if image_file.is_file():
  image_hash=hashlib.sha256(image_file.read_bytes()).hexdigest();check(image_hash not in used_image_hashes,f'{file.name}: duplicate image content');used_image_hashes.add(image_hash)
 rendered=pages.get(DIST/'noticias'/a['slug']/'index.html');check(rendered is not None,f'{file.name}: article not rendered')
 if rendered:
  check(rendered.meta.get('og:title')==a['title'],f'{file.name}: OG mismatch');check(rendered.meta.get('twitter:description')==a['description'],f'{file.name}: social description mismatch');check(any(s.get('@type')=='NewsArticle' and s.get('headline')==a['title'] for s in rendered.schemas),f'{file.name}: NewsArticle missing')
try:
 rss=ET.parse(DIST/'rss.xml').getroot();check(len(rss.findall('./channel/item'))==len(records),'RSS article count mismatch');sitemap=ET.parse(DIST/'sitemap.xml').getroot()
 for loc in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
  url=urllib.parse.urlsplit(loc.text);check(url.netloc==origin and url.path.startswith(base),'Sitemap origin/base mismatch')
 check('Sitemap: https://' in (DIST/'robots.txt').read_text(),'robots sitemap missing');index=json.loads((DIST/'search-index.json').read_text());check(len(index)==len(records),'Search index count mismatch')
except Exception as e:errors.append('Feed/index validation: '+str(e))
for forbidden in ['.git','.cache','data','scripts','__qa-mobile.html']:check(not (DIST/forbidden).exists(),'Private or QA artifact exposed: '+forbidden)
if errors:print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(pages)} HTML pages, {len(records)} articles, internal links, images, metadata, JSON-LD, RSS, sitemap, robots and search. Base: {base}')
