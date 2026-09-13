import datetime as dt,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import edition_schedule as schedule
import publish_edition

UTC=dt.timezone.utc
ROOT=Path(__file__).resolve().parents[1]

class EditionClock(unittest.TestCase):
 def test_schedule_is_brazil_time(self):
  self.assertEqual(schedule.config()['timezone'],'America/Sao_Paulo')
  self.assertEqual(schedule.config()['slots'],[8,13,18,22])

 def test_slot_and_next_slot_use_sao_paulo_clock(self):
  at=dt.datetime(2026,9,13,14,0,tzinfo=UTC) # 11h em Brasília
  self.assertEqual(schedule.slot_for(at),dt.datetime(2026,9,13,11,0,tzinfo=UTC)) # edição 08h
  self.assertEqual(schedule.next_slot(at),dt.datetime(2026,9,13,16,0,tzinfo=UTC)) # edição 13h

 def test_regular_slot_is_due_once(self):
  at=dt.datetime(2026,9,13,11,5,tzinfo=UTC)
  self.assertTrue(schedule.is_due({},at))
  self.assertFalse(schedule.is_due({'lastEditionSlot':'2026-09-13T11:00:00Z'},at))

 def test_regular_slot_expires_outside_publication_window(self):
  self.assertFalse(schedule.is_due({},dt.datetime(2026,9,13,14,0,tzinfo=UTC)))

 def test_late_night_points_to_next_morning(self):
  at=dt.datetime(2026,9,14,2,0,tzinfo=UTC) # 23h do dia 13 em Brasília
  self.assertEqual(schedule.next_slot(at),dt.datetime(2026,9,14,11,0,tzinfo=UTC))

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
  selected=publish_edition.balanced_groups(groups,max_total=30,max_per_category=4)
  self.assertEqual(len(selected),4)

class WorkflowContract(unittest.TestCase):
 def test_regular_publisher_runs_four_times_per_day(self):
  text=(ROOT/'.github/workflows/collector.yml').read_text()
  self.assertIn("cron: '0 1,11,16,21 * * *'",text)

 def test_scout_keeps_collecting_without_publishing(self):
  text=(ROOT/'.github/workflows/scout.yml').read_text()
  self.assertIn("cron: '*/15 * * * *'",text)
  self.assertIn('Observar fontes sem publicar',text)

if __name__=='__main__':unittest.main()
