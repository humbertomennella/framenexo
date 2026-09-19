"""Artifact transport and isolation tests; no network or model downloads."""
import datetime as dt
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import urllib.error
import zipfile
from unittest.mock import patch, MagicMock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pipeline as p
import scout_snapshot as s
import run_scout
import run_editorial

REPO = 'humbertomennella/framenexo'
ROOT = Path(__file__).resolve().parents[1]

class Snapshots(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(p, 'ROOT', self.root)
        self.patch.start(); self.addCleanup(self.patch.stop)
        self.env = patch.dict(os.environ, GITHUB_REPOSITORY=REPO, GITHUB_RUN_ID='100', GITHUB_RUN_ATTEMPT='1')
        self.env.start(); self.addCleanup(self.env.stop)
        (self.root / 'content/news').mkdir(parents=True)

    def candidate(self, **kw):
        return dict(dict(id='abc123', url='https://example.com/news', title='Official game expansion announced',
                         sourceId='official', sourceName='Official', sourceType='primary',
                         category='Tecnologia', publishedAt=p.iso(), relevance=90, status='candidate'), **kw)

    def document(self, items=None):
        return s.create(items if items is not None else [self.candidate()],
                        dict(status='healthy', publishingAllowed=False, sourcesReached=2))

    def run_info(self, ident=100, **kw):
        return dict(dict(id=ident, run_attempt=1, status='completed', conclusion='success', head_branch='main',
                         event='schedule', updated_at=p.iso(), head_repository={'full_name': REPO}), **kw)

    def zipped(self, doc):
        buf=io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as archive: archive.writestr('snapshot.json', json.dumps(doc))
        return buf.getvalue()

    def test_checksum_origin_run_and_age(self):
        good=self.document()
        self.assertEqual(s.validate(good, self.run_info())['version'], 2)
        bad=json.loads(json.dumps(good));bad['payload']['candidates'][0]['title']='altered'
        with self.assertRaisesRegex(ValueError,'checksum'):s.validate(bad)
        for key,value in [('repository','other/repo'),('completedAt',p.iso(p.now()-dt.timedelta(hours=25))),
                          ('completedAt',p.iso(p.now()+dt.timedelta(minutes=10))),('completedAt',5),('version',3)]:
            bad=json.loads(json.dumps(good));bad['payload'][key]=value;bad['sha256']=s.digest(bad['payload'])
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):s.validate(bad)
        with self.assertRaisesRegex(ValueError,'run_mismatch'):s.validate(good,self.run_info(99))

    def test_snapshot_carries_recent_url_bound_evidence(self):
        candidate=self.candidate()
        evidence=' '.join(['verified']*80)
        p.write(f'.cache/evidence/{candidate["id"]}.json',dict(url=candidate['url'],text=evidence,fetchedAt=p.iso()))
        doc=self.document([candidate]);payload=s.validate(doc)
        self.assertEqual(payload['evidence'][candidate['id']]['text'],evidence)
        (self.root/'.cache/evidence'/f'{candidate["id"]}.json').unlink()
        s.restore_evidence(payload)
        restored=p.read(f'.cache/evidence/{candidate["id"]}.json',{})
        self.assertEqual(restored['url'],candidate['url']);self.assertEqual(restored['text'],evidence)

    def test_failed_state_is_not_valid_even_with_checksum(self):
        doc=self.document();doc['payload']['state']['status']='failed';doc['sha256']=s.digest(doc['payload'])
        with self.assertRaises(ValueError):s.validate(doc)

    def test_prunes_expiry_future_published_and_canonical_duplicates(self):
        items=[self.candidate(),self.candidate(url='https://example.com/news/?utm_source=test'),
               self.candidate(url='https://example.com/old',publishedAt=p.iso(p.now()-dt.timedelta(days=8))),
               self.candidate(url='https://example.com/future',publishedAt=p.iso(p.now()+dt.timedelta(hours=1))),
               self.candidate(url='https://example.com/published',status='published')]
        self.assertEqual(len(s.prune(items)),1)

    def test_zip_layout_and_size_are_rejected_without_extraction(self):
        for name in ('../snapshot.json','arbitrary.json'):
            buf=io.BytesIO()
            with zipfile.ZipFile(buf,'w') as archive:archive.writestr(name,'{}')
            with self.assertRaises(ValueError):s.unpack(buf.getvalue(),self.run_info())
        with patch.object(s,'MAX_BYTES',10),self.assertRaises(ValueError):s.unpack(self.zipped(self.document()),self.run_info())

    def test_redirect_does_not_leak_auth(self):
        req=s.urllib.request.Request('https://api.github.com/a',headers={'Authorization':'Bearer test'})
        redirected=s.NoAuthRedirect().redirect_request(req,None,302,'',{},'https://storage.example/file')
        self.assertIsNone(redirected.get_header('Authorization'))
        with self.assertRaises(ValueError):s.NoAuthRedirect().redirect_request(req,None,302,'',{},'http://storage.example/file')

    def test_restore_skips_failed_running_and_wrong_branch(self):
        runs=[self.run_info(200,status='in_progress'),self.run_info(201,conclusion='failure'),self.run_info(202,head_branch='feature')]
        with patch.object(s,'api',return_value={'workflow_runs':runs}) as api:
            self.assertEqual(s.restore()['status'],'unavailable')
            self.assertEqual(api.call_count,1)

    def test_corrupt_newest_falls_back_to_valid_completed_snapshot(self):
        runs=[self.run_info(102,updated_at=p.iso(p.now()-dt.timedelta(minutes=1))),self.run_info(101,updated_at=p.iso(p.now()-dt.timedelta(minutes=2)))]
        doc=self.document();doc['payload']['runId']='101';doc['sha256']=s.digest(doc['payload'])
        def api(path,binary=False):
            if '/workflows/' in path:return {'workflow_runs':runs}
            if '/runs/' in path:
                ident=path.split('/')[3]
                return {'artifacts':[{'id':ident,'name':f'{s.NAME}-{ident}-1','expired':False}]}
            return b'corrupt' if '/102/' in path else self.zipped(doc)
        with patch.object(s,'api',side_effect=api):result=s.restore(required=True)
        self.assertEqual(result['runId'],'101');self.assertEqual(len(result['errors']),1)

    def test_missing_snapshot_bootstraps_and_api_outage_keeps_pool_collecting(self):
        p.write('data/candidates.json',[self.candidate()])
        with patch.object(s,'api',return_value={'workflow_runs':[]}):s.restore()
        with patch.object(p,'collect',return_value={'sourcesOK':1,'collected':0,'errors':[]}):run_scout.main()
        self.assertEqual(len(p.read('.cache/scout/snapshot.json',{})['payload']['candidates']),1)
        with patch.object(s,'api',side_effect=urllib.error.URLError('offline')):s.restore()
        with patch.object(p,'collect',return_value={'sourcesOK':1,'collected':0,'errors':[]}) as collect:
            run_scout.main()
        collect.assert_called_once()
        self.assertEqual(len(p.read('.cache/scout/snapshot.json',{})['payload']['candidates']),1)

    def test_github_closing_consumes_snapshot_without_collecting(self):
        doc=self.document()
        p.write('.cache/scout/input.json',doc)
        with patch.dict(os.environ,{'GITHUB_ACTIONS':'true'}), \
             patch.object(p,'collect') as collect, \
             patch.object(run_editorial.schedule,'is_due',return_value=False):
            result=run_editorial.run()
        collect.assert_not_called()
        self.assertEqual(result['publication'],'not_due')
        self.assertEqual(p.read('.cache/scout/input.json',{})['sha256'],doc['sha256'])

    def test_scout_preserves_all_durable_files_on_partial_and_total_failure(self):
        p.write('data/candidates.json',[self.candidate()])
        p.write('data/publishing-state.json',{'editionCount':7})
        (self.root/'content/news/permanent.md').write_text('permanent public content')
        p.write('.cache/scout/restore.json',{'status':'unavailable','errors':[]})
        before={str(f):f.read_bytes() for f in self.root.rglob('*') if f.is_file() and '.cache' not in f.parts}
        def collect():
            p.write('data/candidates.json',[self.candidate()]);p.write('data/publishing-state.json',{'transient':True});p.log('collection')
            return {'sourcesOK':1,'collected':1,'errors':[{'source':'test','code':'TimeoutError'}]}
        with patch.object(p,'collect',side_effect=collect):run_scout.main()
        doc=p.read('.cache/scout/snapshot.json',{});self.assertEqual(s.validate(doc)['state']['status'],'degraded')
        with patch.object(p,'collect',return_value={'sourcesOK':0}),self.assertRaisesRegex(RuntimeError,'all_sources_failed'):run_scout.main()
        self.assertFalse((self.root/'.cache/scout/snapshot.json').exists())
        after={str(f):f.read_bytes() for f in self.root.rglob('*') if f.is_file() and '.cache' not in f.parts}
        self.assertEqual(before,after);self.assertEqual(p.STATE_PATHS,{})

    def test_concurrent_local_scout_is_rejected(self):
        (self.root/'.cache').mkdir()
        with (self.root/'.cache/scout.lock').open('w') as lock:
            run_scout.fcntl.flock(lock,run_scout.fcntl.LOCK_EX|run_scout.fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError):run_scout.main()

    def test_editorial_without_snapshot_holds_before_collection_or_model(self):
        with patch.dict(os.environ,{'GITHUB_ACTIONS':'false'}), \
             patch.object(p,'collect') as collect, \
             patch.object(run_editorial.local_model,'command') as model:
            self.assertEqual(run_editorial.run(force=True)['publication'],'held_no_valid_scout_snapshot')
        collect.assert_not_called();model.assert_not_called()

    def test_github_closing_fails_loudly_when_completed_snapshot_is_unavailable(self):
        with patch.dict(os.environ,{'GITHUB_ACTIONS':'true'}), \
             patch.object(p,'collect') as collect:
            with self.assertRaisesRegex(RuntimeError,'completed_scout_snapshot_unavailable'):
                run_editorial.run(force=True)
            collect.assert_not_called()

    def test_consumer_keeps_approved_media_and_editorial_holds(self):
        p.write('data/candidates.json',[self.candidate(status='needs_review',media={'path':'/approved.webp'})])
        p.write('.cache/scout/input.json',self.document())
        s.consume();row=p.read('data/candidates.json',[])[0]
        self.assertEqual(row['status'],'needs_review');self.assertEqual(row['media']['path'],'/approved.webp')

    def test_closing_generates_immutable_edition_from_snapshot(self):
        first=self.candidate();second=self.candidate(id='def456',sourceId='press',sourceName='Newsroom',sourceType='press',url='https://news.test/report')
        p.write('.cache/scout/input.json',self.document([first,second]))
        p.write('data/sources.json',[{'id':'official','organization':'official','hosts':['example.com']},{'id':'press','organization':'press','hosts':['news.test']}])
        asset=self.root/'public/images/news/test.webp';asset.parent.mkdir(parents=True);asset.write_bytes(b'test image')
        media={'path':'/images/news/test.webp','alt':'Ilustração editorial de teste.','credit':'Apurante Editorial'}
        p.write('data/image-rights.json',[dict(path=media['path'],origin='generated',credit=media['credit'],license='original',sourceURL=None,proof='test fixture')])
        p.write('data/candidates.json',[dict(first,media=media)])
        draft={'title':'Expansão anunciada oficialmente','description':'Informações verificadas do anúncio.', 'paragraphs':['Fato aprovado.','Detalhe aprovado.'], 'eventKey':'fixture-expansion','tags':['Tecnologia'],'facts':[{'claim':'Anúncio','quote':'announcement'}]}
        response=MagicMock();response.__enter__.return_value.status=200
        server=MagicMock();server.poll.return_value=None
        with patch.dict(os.environ,{'GITHUB_ACTIONS':'false'}),patch.object(p,'collect') as collect,patch.object(p,'evidence',return_value='Official announcement.'),patch.object(p,'generate',return_value=(draft,{'supported':True})),patch.object(run_editorial.editorial_selection,'verify',side_effect=lambda group,sources,cache:(group,'Official announcement.')),patch.object(run_editorial.local_model,'command',return_value=(['fixture'],{})),patch.object(run_editorial.subprocess,'Popen',return_value=server),patch.object(run_editorial.urllib.request,'build_opener') as opener:
            opener.return_value.open.return_value=response
            self.assertEqual(run_editorial.run(force=True)['published'],1)
            files=list((self.root/'content/news').glob('*.md'));original=files[0].read_bytes()
            run_editorial.run(force=True)
            self.assertEqual(files[0].read_bytes(),original);self.assertEqual(len(list((self.root/'content/news').glob('*.md'))),1)
            collect.assert_not_called()
        meta=json.loads(original.decode().split('---')[1]);self.assertIn('articleId',meta);self.assertIn('editionId',meta)

class WorkflowIsolation(unittest.TestCase):
    def test_scout_cannot_commit_or_deploy_and_keeps_clock(self):
        text=(ROOT/'.github/workflows/scout.yml').read_text()
        for forbidden in ('contents: write','commit_scout.py','commit_changes.py','publish_edition','deploy.yml','run_editorial.py'):
            self.assertNotIn(forbidden,text)
        self.assertIn('git diff --exit-code',text);self.assertIn("'*/15 * * * *'",text)
        self.assertIn('group: apurante-scout-snapshot',text);self.assertIn('cancel-in-progress: false',text)
        self.assertIn('actions/upload-artifact@',text)
        collector=(ROOT/'.github/workflows/collector.yml').read_text()
        self.assertIn("'7 1,11,16,21 * * *'",collector)
        self.assertIn("'27 1,11,16,21 * * *'",collector)
        self.assertNotIn("'7 * * * *'",collector)
        self.assertNotIn("'27 * * * *'",collector)
        self.assertNotIn("'0 * * * *'",collector)

if __name__=='__main__':unittest.main()
