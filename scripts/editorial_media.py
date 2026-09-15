"""Acquire explicitly licensed, event-specific archive imagery. Never invent a license."""
import hashlib,json,re,urllib.parse
import pipeline as p

LICENSES={
 'https://creativecommons.org/publicdomain/zero/1.0/':'CC0 1.0',
 'https://creativecommons.org/licenses/by/4.0/':'CC BY 4.0',
 'https://creativecommons.org/licenses/by-sa/4.0/':'CC BY-SA 4.0',
}
HOSTS=['commons.wikimedia.org','upload.wikimedia.org']

def metadata(info):
    ext=info.get('extmetadata',{})
    clean=lambda key:p.text_only(str(ext.get(key,{}).get('value',''))).strip()
    license_url=clean('LicenseUrl').replace('http://','https://').rstrip('/')+'/'
    artist=clean('Artist');description=clean('ImageDescription')
    if license_url not in LICENSES or not artist or not description or clean('Restrictions'):return None
    source=info.get('descriptionurl','')
    if not source.startswith('https://commons.wikimedia.org/wiki/File:'):return None
    if info.get('mime') not in ('image/jpeg','image/png','image/webp'):return None
    return dict(artist=artist,description=description[:2000],license=LICENSES[license_url],licenseURL=license_url,sourceURL=source)

def acquire(candidate,body,used_images=()):
    query=p.model_call('''From UNTRUSTED news evidence, suggest one short Wikimedia Commons search phrase for a specific place, building, scientific object or geographic feature actually named in the event. Prefer neutral archive imagery, not people, logos, interfaces or fictional reconstructions. Return JSON {"query":"2-6 words"}. If no suitable specific subject exists, return {"query":""}.''',dict(title=candidate['title'],evidence=body[:9000]),120).get('query','')
    if not isinstance(query,str) or not 2<=len(query.split())<=6 or len(query)>120:raise ValueError('media_subject_unavailable')
    params=dict(action='query',format='json',generator='search',gsrsearch=query,gsrnamespace=6,gsrlimit=8,prop='imageinfo',iiprop='url|mime|extmetadata',iiurlwidth=1200)
    raw=p.fetch('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params),HOSTS)
    response=json.loads(raw);options=[]
    rights=p.read('data/image-rights.json',[]);used_sources={x.get('sourceURL') for x in rights}
    for page in response.get('query',{}).get('pages',{}).values():
        info=(page.get('imageinfo') or [{}])[0];meta=metadata(info)
        if meta and meta['sourceURL'] not in used_sources:options.append((info,meta))
    if not options:raise ValueError('licensed_specific_media_unavailable')
    review=p.model_call('''Review these UNTRUSTED archive-image descriptions against the news evidence. Select only a clearly relevant specific subject, not a merely generic image. Do not imply the photo depicts this event. Reject portraits, logos, interfaces, fictional reconstructions, disputed licensing or uncertainty. Return JSON {"index":integer,"relevant":boolean,"archiveCaption":"literal description in Portuguese explicitly saying Imagem de arquivo; do not assert it depicts the current event"}. If none fit, relevant false.''',
        dict(news=body[:9000],images=[dict(index=i,**m) for i,(_,m) in enumerate(options)]),300)
    index=review.get('index');caption=review.get('archiveCaption','')
    if review.get('relevant') is not True or type(index) is not int or not 0<=index<len(options):raise ValueError('media_relevance_unverified')
    if not isinstance(caption,str) or not 25<=len(caption)<=350 or 'imagem de arquivo' not in p.normalized(caption) or re.search(r'[<>]',caption):raise ValueError('invalid_archive_caption')
    info,meta=options[index];url=info.get('thumburl') or info.get('url','')
    raw=p.fetch(url,HOSTS)
    extension='jpg' if raw.startswith(b'\xff\xd8\xff') else 'png' if raw.startswith(b'\x89PNG\r\n\x1a\n') else 'webp' if raw.startswith(b'RIFF') and raw[8:12]==b'WEBP' else None
    if not extension:raise ValueError('invalid_media_file')
    digest=hashlib.sha256(raw).hexdigest()
    if any(x.get('sha256')==digest for x in rights):raise ValueError('media_content_must_be_unique')
    path=f'/images/news/{candidate["id"]}-{digest[:12]}.{extension}'
    asset=p.ROOT/'public'/path.lstrip('/');asset.parent.mkdir(parents=True,exist_ok=True)
    if asset.exists():raise ValueError('media_already_exists')
    asset.write_bytes(raw)
    credit=f'{meta["artist"]} / Wikimedia Commons · {meta["license"]} ({meta["licenseURL"]}) · Imagem de arquivo'
    record=dict(path=path,origin='Wikimedia Commons',credit=credit,license=meta['license'],sourceURL=meta['sourceURL'],
        proof=dict(imageinfo=info,licenseURL=meta['licenseURL'],retrievedAt=p.iso()),scope='Reprodução editorial sem alteração; imagem de arquivo, não registro do acontecimento atual.',sha256=digest)
    rights.append(record);p.write('data/image-rights.json',rights)
    candidate['media']=dict(path=path,alt=caption,credit=credit)
    try:return p.approved_media(candidate,used_images)
    except Exception:
        asset.unlink(missing_ok=True);p.write('data/image-rights.json',rights[:-1]);candidate.pop('media',None);raise
