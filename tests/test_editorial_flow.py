import sys,tempfile,unittest,json
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import pipeline as p
import editorial_selection as selection
import editorial_media as media

class EditorialFlow(unittest.TestCase):
 def row(self,id='a',source='one',**kw):
  return dict(dict(id=id,sourceId=source,sourceOrganization=source,sourceName=source,sourceType='press',title='Tribunal determina entrega de dados do celular',url=f'https://{source}.test/{id}',publishedAt=p.iso(),status='candidate',relevance=30,category='Brasil'),**kw)
 def test_ordinary_press_report_not_rejected_for_old_keyword_score(self):
  row=self.row();self.assertEqual(selection.eligible([row],{'one':{'id':'one','enabled':True}}),[row])
 def test_opinion_rumor_disabled_sources_and_future_stay_out(self):
  for row in [self.row(title='Rumor de novas medidas'),self.row(title='Opinion sobre governo'),self.row(publishedAt='2099-01-01T00:00:00Z')]:
   self.assertFalse(selection.eligible([row],{'one':{'id':'one'}}))
  self.assertFalse(selection.eligible([self.row()],{'one':{'id':'one','enabled':False}}))
 def test_related_headlines_preserve_independent_route(self):
  rows=[self.row(str(i)) for i in range(5)]+[self.row('other','two')]
  first=selection.groups(rows)[0]
  self.assertEqual({x['sourceId'] for x in first},{'one','two'})
 def test_same_topic_with_conflicting_facts_is_held(self):
  rows=[self.row(),self.row('b','two')];sources={x:{'id':x,'organization':x} for x in ('one','two')}
  with patch.object(p,'evidence',return_value='Court orders delivery of complete records today.'),patch.object(p,'model_call',return_value={'sameFact':True,'conflict':True,'syndicationUncertain':False}),self.assertRaisesRegex(ValueError,'shared_fact'):selection.verify(rows,sources)
 def test_invented_quotes_and_wire_republications_fail(self):
  rows=[self.row(),self.row('b','two')];sources={x:{'id':x,'organization':x} for x in ('one','two')}
  review=dict(sameFact=True,conflict=False,syndicationUncertain=False,routes=[dict(id=x['id'],quote='these words do not exist here',originalOrganization=x['sourceId']) for x in rows])
  with patch.object(p,'evidence',return_value='Court orders delivery of complete records today.'),patch.object(p,'model_call',return_value=review),self.assertRaisesRegex(ValueError,'anchor'):selection.verify(rows,sources)
  with patch.object(p,'evidence',return_value='Por Reuters Court orders delivery of complete records today.'),self.assertRaisesRegex(ValueError,'independent'):selection.verify(rows,sources)
 def test_supported_routes_are_recorded(self):
  rows=[self.row(),self.row('b','two')];sources={x:{'id':x,'organization':x} for x in ('one','two')}
  review=dict(sameFact=True,conflict=False,syndicationUncertain=False,claim='Decisão judicial',routes=[dict(id=x['id'],quote='Court orders delivery of complete records today.',originalOrganization=x['sourceId']) for x in rows])
  with tempfile.TemporaryDirectory() as temp,patch.object(p,'ROOT',Path(temp)),patch.object(p,'evidence',return_value='Court orders delivery of complete records today.'),patch.object(p,'model_call',return_value=review):
   group,body=selection.verify(rows,sources);self.assertEqual(len(group),2);self.assertIn('https://two.test/b',body);self.assertTrue((Path(temp)/'.cache/drafts/a-shared-fact.json').exists())
 def info(self):
  return dict(descriptionurl='https://commons.wikimedia.org/wiki/File:Example.jpg',mime='image/jpeg',thumburl='https://upload.wikimedia.org/example.jpg',extmetadata={k:{'value':v} for k,v in dict(LicenseUrl='https://creativecommons.org/licenses/by/4.0/',Artist='Example Photographer',ImageDescription='Specific court building').items()})
 def test_public_access_is_not_a_license(self):
  info=self.info();self.assertIsNotNone(media.metadata(info))
  for value in ('','All rights reserved','https://creativecommons.org/licenses/by-nc/4.0/'):
   info['extmetadata']['LicenseUrl']['value']=value;self.assertIsNone(media.metadata(info))
 def test_acquisition_records_rights_hash_and_archive_caption(self):
  with tempfile.TemporaryDirectory() as temp,patch.object(p,'ROOT',Path(temp)):
   info=self.info();api=json.dumps({'query':{'pages':{'1':{'imageinfo':[info]}}}}).encode()
   responses=[{'query':'Specific court building'},{'index':0,'relevant':True,'archiveCaption':'Imagem de arquivo do edifício do tribunal.'}]
   with patch.object(p,'model_call',side_effect=responses),patch.object(p,'fetch',side_effect=[api,b'\xff\xd8\xfffixture']):
    result=media.acquire(self.row(),'Text of verified event.')
   rights=p.read('data/image-rights.json',[]);self.assertEqual(len(rights),1);self.assertEqual(len(rights[0]['sha256']),64);self.assertIn('CC BY 4.0',result['credit']);self.assertIn('Imagem de arquivo',result['alt']);self.assertTrue((Path(temp)/'public'/result['path'].lstrip('/')).is_file())
 def test_missing_licensed_media_retains_story(self):
  with patch.object(p,'model_call',return_value={'query':'Specific court building'}),patch.object(p,'fetch',return_value=b'{"query":{"pages":{}}}'),self.assertRaisesRegex(ValueError,'licensed_specific'):media.acquire(self.row(),'Evidence')
if __name__=='__main__':unittest.main()
