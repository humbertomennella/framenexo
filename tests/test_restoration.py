import datetime as dt,gzip,io,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import pipeline as p
import editorial_report

class Restoration(unittest.TestCase):
 def test_agency_body_excludes_navigation_and_scripts(self):
  raw='<nav>menu</nav><div class="conteudo-noticia"><p>Texto público <strong>da matéria</strong>.</p><script>ruído</script><p>Segundo parágrafo.</p></div><div>relacionadas</div>'
  text=p.article_text(raw,{'hosts':['agenciabrasil.ebc.com.br']})
  self.assertIn('Texto público',text);self.assertIn('Segundo parágrafo',text)
  for noise in ['menu','ruído','relacionadas']:self.assertNotIn(noise,text)
 def test_paid_or_unbounded_body_is_rejected(self):
  for raw in ['<div>conteúdo sem limite conhecido</div>','<script>{"isAccessibleForFree":false}</script><article>texto</article>']:
   with self.assertRaises(ValueError):p.article_text(raw,{})
 def test_full_article_is_attempted_without_feed_shortcut(self):
  body=' '.join(['Conteúdo']*100)
  with patch.object(p,'fetch',side_effect=[b'User-agent: *\nAllow: /',f'<article>{body}</article>'.encode()]) as fetch:
   self.assertEqual(p.evidence({'url':'https://example.com/article'},{'hosts':['example.com'],'feed':'https://example.com/feed'}),body)
   self.assertEqual(fetch.call_count,2)
 def test_gzip_expansion_is_bounded(self):
  raw=gzip.compress(b'x'*5000)
  response=io.BytesIO(raw)
  with patch.object(p,'MAX_BYTES',100),patch.object(p,'validate_url'),patch.object(p.urllib.request,'build_opener') as opener:
   opener.return_value.open.return_value=response
   with self.assertRaisesRegex(ValueError,'source_too_large'):p.fetch('https://example.com/feed',['example.com'])
 def test_lead_balance_uses_dates_not_file_order(self):
  history=[{'publishedAt':'2026-09-15T00:00:00Z','leadSourceOrganization':'one'}]*20+[{'publishedAt':'2026-09-01T00:00:00Z','leadSourceOrganization':'two'}]*20
  group=[dict(sourceId=x,sourceType='press',relevance=55) for x in ['one','two']]
  self.assertEqual(p.choose_lead(group,{},history)['sourceId'],'two')
 def test_report_does_not_reuse_a_previous_run(self):
  with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'GITHUB_RUN_ID':'new','PIPELINE_OUTCOME':'failure'}):
   root=Path(directory);(root/'data').mkdir();(root/'data/operation-state.json').write_text(json.dumps({'runId':'old','status':'completed'}))
   with patch.dict(os.environ,{'GITHUB_STEP_SUMMARY':str(root/'summary')}):result=editorial_report.report(root)
   self.assertEqual(result['operation']['status'],'not_recorded')
 def test_report_preserves_retention_without_publication(self):
  with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'GITHUB_RUN_ID':'new'}):
   root=Path(directory);(root/'data').mkdir();(root/'data/operation-state.json').write_text(json.dumps({'runId':'new','result':{'publication':'held_no_valid_scout_snapshot'}}))
   with patch.dict(os.environ,{'GITHUB_STEP_SUMMARY':str(root/'summary')}):result=editorial_report.report(root)
   self.assertEqual(result['operation']['result']['publication'],'held_no_valid_scout_snapshot')
if __name__=='__main__':unittest.main()
