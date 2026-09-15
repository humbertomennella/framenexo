import datetime as dt,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import edition_schedule as schedule
import publish_edition

UTC=dt.timezone.utc
ROOT=Path(__file__).resolve().parents[1]

class EditionClock(unittest.TestCase):
 def test_schedule_is_brazil_time(self):
  cfg=schedule.config()
  self.assertEqual(cfg['timezone'],'America/Sao_Paulo')
  self.assertEqual(cfg['slots'],[8,13,18,22])
  self.assertEqual(cfg['targetPerCategory'],2)
  self.assertEqual(cfg['maxPerCategory'],2)
  self.assertEqual(cfg['maxArticlesPerEdition'],20)

 def test_slot_and_next_slot_use_sao_paulo_clock(self):
  at=dt.datetime(2026,9,13,14,15,tzinfo=UTC) # 11h15 em Brasília
  self.assertEqual(schedule.slot_for(at),dt.datetime(2026,9,13,11,0,tzinfo=UTC)) # edição 08h
  self.assertEqual(schedule.next_slot(at),dt.datetime(2026,9,13,16,0,tzinfo=UTC)) # edição 13h

 def test_regular_slot_is_due_once(self):
  at=dt.datetime(2026,9,13,11,5,tzinfo=UTC) # 08h05 em Brasília
  self.assertTrue(schedule.is_due({},at))
  self.assertFalse(schedule.is_due({'lastEditionSlot':'2026-09-13T11:00:00Z'},at))

 def test_recovery_run_does_not_duplicate_published_slot(self):
  recovery=dt.datetime(2026,9,13,11,27,tzinfo=UTC)
  self.assertTrue(schedule.is_due({},recovery))
  self.assertFalse(schedule.is_due({'lastEditionSlot':'2026-09-13T11:00:00Z'},recovery))

 def test_regular_slot_expires_outside_publication_window(self):
  self.assertFalse(schedule.is_due({},dt.datetime(2026,9,13,11,51,tzinfo=UTC)))

 def test_late_night_points_to_next_morning(self):
  at=dt.datetime(2026,9,14,2,15,tzinfo=UTC) # 23h15 do dia 13 em Brasília
  self.assertEqual(schedule.next_slot(at),dt.datetime(2026,9,14,11,0,tzinfo=UTC)) # 08h do dia 14

class EditionBalance(unittest.TestCase):
 def group(self,category,index,relevance=80):
  return [{'category':category,'relevance':relevance,'id':f'{category}-{index}'}]

 def test_round_robin_prevents_one_category_from_dominating(self):
  groups=[self.group('Brasil',i,100-i) for i in range(6)]+[self.group('Mundo',i,90-i) for i in range(3)]+[self.group('Ciência',i,80-i) for i in range(2)]
  selected=publish_edition.balanced_groups(groups,max_total=8,max_per_category=4)
  categories=[group[0]['category'] for group in selected]
  self.assertEqual(categories[:3],['Brasil','Mundo','Ciência'])
  self.assertLessEqual(categories.count('Brasil'),4)
  self.assertEqual(len(selected),8)

 def test_per_category_ceiling_is_respected(self):
  groups=[self.group('Brasil',i) for i in range(10)]
  selected=publish_edition.balanced_groups(groups,max_total=20,max_per_category=2)
  self.assertEqual(len(selected),2)

 def test_twenty_article_target_can_fill_two_per_ten_categories(self):
  categories=['Brasil','Mundo','Política','Economia','Tecnologia','Ciência','Cultura','Esportes','Saúde','Meio Ambiente']
  groups=[self.group(category,index) for index in range(2) for category in categories]
  selected=publish_edition.balanced_groups(groups,max_total=20,max_per_category=2)
  self.assertEqual(len(selected),20)
  counts={category:sum(1 for group in selected if group[0]['category']==category) for category in categories}
  self.assertTrue(all(value==2 for value in counts.values()))

 def test_verification_queue_keeps_reserve_groups_beyond_publish_ceiling(self):
  groups=[self.group('Brasil',i) for i in range(6)]
  with patch.object(publish_edition.editorial_selection,'cached_evidence',return_value='evidência suficiente'):
   selected=publish_edition.verification_queue(groups,publish_limit=8,category_limit=2)
  self.assertEqual(len(selected),6)

 def test_verification_queue_prefers_groups_with_cached_evidence(self):
  stale=[{'category':'Brasil','relevance':80,'id':'stale-1','publishedAt':'2026-09-15T02:00:00Z'}]
  ready=[{'category':'Brasil','relevance':80,'id':'ready-1','publishedAt':'2026-09-15T01:00:00Z'}]
  with patch.object(publish_edition.editorial_selection,'cached_evidence',side_effect=lambda item:'evidência' if item['id'].startswith('ready') else None):
   selected=publish_edition.verification_queue([stale,ready],publish_limit=2,category_limit=2)
  self.assertEqual(selected[0][0]['id'],'ready-1')

class MediaFallback(unittest.TestCase):
 def test_verified_story_falls_back_to_first_party_cover(self):
  candidate={'id':'abc123','title':'Acontecimento verificado sem imagem externa'}
  group=[candidate]
  with patch.object(publish_edition.p,'approved_media',side_effect=ValueError('approved_media_required')),patch.object(publish_edition.editorial_media,'acquire',side_effect=ValueError('licensed_specific_media_unavailable')),patch.object(publish_edition.p,'log') as log:
   media=publish_edition.resolve_media(group,candidate,'evidência verificada',set())
  self.assertEqual(media['path'],'/og.png')
  self.assertIn(candidate['title'],media['alt'])
  self.assertIn('Apurante Editorial',media['credit'])
  log.assert_called_once()

 def test_approved_media_still_wins_over_fallback(self):
  candidate={'id':'abc123','title':'Acontecimento com imagem aprovada'}
  approved={'path':'/images/news/approved.webp','alt':'Imagem aprovada','credit':'Crédito aprovado'}
  with patch.object(publish_edition.p,'approved_media',return_value=approved),patch.object(publish_edition.editorial_media,'acquire') as acquire:
   self.assertEqual(publish_edition.resolve_media([candidate],candidate,'evidência',set()),approved)
  acquire.assert_not_called()

class WorkflowContract(unittest.TestCase):
 def test_regular_publisher_has_primary_and_recovery_runs(self):
  text=(ROOT/'.github/workflows/collector.yml').read_text()
  self.assertIn("cron: '7 1,11,16,21 * * *'",text)
  self.assertIn("cron: '27 1,11,16,21 * * *'",text)
  self.assertNotIn("cron: '7 * * * *'",text)
  self.assertNotIn("cron: '27 * * * *'",text)

 def test_scout_keeps_collecting_without_publishing(self):
  text=(ROOT/'.github/workflows/scout.yml').read_text()
  self.assertIn("cron: '*/15 * * * *'",text)
  self.assertIn('Observar fontes sem publicar',text)

if __name__=='__main__':unittest.main()
