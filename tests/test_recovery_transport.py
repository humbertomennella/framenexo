import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import pipeline as p
import editorial_selection as selection
import evidence_anchor


class RecoveryTransport(unittest.TestCase):
    def test_self_closing_images_do_not_truncate_article(self):
        raw='<article><p>First paragraph<img src="pixel" /><img src="pixel2" /></p><p>Important second paragraph<br/>continued.</p></article><aside>Unrelated news</aside>'
        body=p.article_text(raw,{'hosts':['example.com']})
        self.assertIn('Important second paragraph',body)
        self.assertIn('continued.',body)
        self.assertNotIn('Unrelated news',body)

    def test_full_cached_route_survives_short_live_excerpt(self):
        cached=' '.join('evidence'+str(i) for i in range(220))
        with patch.object(selection,'cached_evidence',return_value=cached),patch.object(selection,'feed_evidence',return_value=None),patch.object(p,'evidence',return_value='short live header'):
            self.assertEqual(selection.evidence({'id':'one'},{}),cached)

    def test_rdf_feed_keeps_dublin_core_date(self):
        raw=b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/"><item><title>Official notice</title><link>https://example.com/news</link><dc:date>2026-09-19T10:00:00Z</dc:date></item></rdf:RDF>'
        self.assertEqual(p.parse_feed(raw)[0]['date'],'2026-09-19T10:00:00Z')

    def test_ibge_adapter_preserves_official_date_and_https(self):
        raw=json.dumps({'items':[{'titulo':'Dados oficiais','introducao':'Texto oficial','link':'http://agenciadenoticias.ibge.gov.br/news','data_publicacao':'19/09/2026 10:00:00'}]}).encode()
        with patch.object(p,'fetch',return_value=raw),patch.object(p,'validate_url'):
            rows=p.source_entries({'feed':'https://servicodados.ibge.gov.br/api/v3/noticias/','hosts':['agenciadenoticias.ibge.gov.br'],'feedFormat':'ibge-json'})
        self.assertEqual(rows[0]['date'],'2026-09-19')
        self.assertEqual(rows[0]['url'],'https://agenciadenoticias.ibge.gov.br/news')

    def test_anchor_options_are_always_literal_and_bounded(self):
        body='O tribunal determinou nesta sexta-feira a apresentação dos documentos originais. A decisão mantém todos os prazos previstos.'
        options=selection.anchor_options(body)
        self.assertTrue(options)
        self.assertTrue(all(evidence_anchor.matches(body,quote) for quote in options.values()))
        self.assertNotIn('invented',options)
