import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import evidence_anchor


class EvidenceAnchor(unittest.TestCase):
 def test_formatting_only_difference_is_accepted(self):
  body='Tribunal determina\nentrega de “dados completos” ainda hoje.'
  quote='Tribunal determina entrega de dados completos ainda hoje'
  self.assertTrue(evidence_anchor.matches(body,quote))

 def test_changed_word_is_rejected(self):
  body='Tribunal determina entrega de dados completos ainda hoje.'
  quote='Tribunal cancela entrega de dados completos ainda hoje'
  self.assertFalse(evidence_anchor.matches(body,quote))

 def test_too_short_anchor_is_rejected(self):
  self.assertFalse(evidence_anchor.matches('Tribunal determina entrega hoje.','Tribunal determina entrega hoje'))

if __name__=='__main__':unittest.main()
