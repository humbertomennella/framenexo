import json
import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import pipeline as p
import editorial_selection as selection
import evidence_anchor


class RecoveryTransport(unittest.TestCase):
    def test_full_length_writer_keeps_long_timeout_with_bounded_output(self):
        source=Path(p.__file__).read_text()
        self.assertIn("timeout=600 if stage in ('writer','rewrite') else 240",source)
        self.assertEqual(source.count("),1900)"),2)

    def test_self_closing_images_do_not_truncate_article(self):
        raw='<article><p>First paragraph<img src="pixel" /><img src="pixel2" /></p><p>Important second paragraph<br/>continued.</p></article><aside>Unrelated news</aside>'
        body=p.article_text(raw,{'hosts':['example.com']})
        self.assertIn('Important second paragraph',body)
        self.assertIn('continued.',body)
        self.assertNotIn('Unrelated news',body)

    def test_un_news_uses_explicit_body_after_empty_article_shell(self):
        raw='''<article><div class="node__content"></div></article>
        <nav><p>Navigation must stay out.</p></nav>
        <div class="field field--name-field-text-column field__item">
          <p>Primeiro parágrafo confirmado da matéria.</p>
          <p>Segundo parágrafo com os detalhes publicados.</p>
        </div><aside><p>Related story must stay out.</p></aside>'''
        body=p.article_text(raw,{'hosts':['news.un.org']})
        self.assertIn('Primeiro parágrafo',body)
        self.assertIn('Segundo parágrafo',body)
        self.assertNotIn('Navigation',body)
        self.assertNotIn('Related story',body)

    def test_full_cached_route_survives_short_live_excerpt(self):
        cached=' '.join('evidence'+str(i) for i in range(220))
        with patch.object(selection,'cached_evidence',return_value=cached),patch.object(selection,'feed_evidence',return_value=None),patch.object(p,'evidence',return_value='short live header'):
            self.assertEqual(selection.evidence({'id':'one'},{}),cached)

    def test_shared_fact_prompt_has_one_unambiguous_anchor_contract(self):
        captured={}
        def model(system,payload,max_tokens):
            captured['system']=system
            return {'sameFact':False,'conflict':False,'syndicationUncertain':False,'claim':'','routes':[]}
        route=({'id':'one','sourceId':'press','url':'https://example.com/one'},' '.join('word'+str(index) for index in range(30)))
        with patch.object(p,'model_call',side_effect=model):
            selection.shared_fact_review([route],{'press':{'id':'press','organization':'press'}})
        self.assertIn('"anchorId"',captured['system'])
        self.assertNotIn('"quote"',captured['system'])

    def test_copy_rejection_gets_paraphrase_repair_without_bypassing_validation(self):
        first={'facts':[],'title':'First'}
        rewritten={'facts':[],'title':'Rewritten'}
        review={'supported':True,'portuguese':True,'original':True,'duplicate':False}
        with tempfile.TemporaryDirectory() as directory,patch.object(p,'ROOT',Path(directory)),patch.object(p,'model_call',side_effect=[first,rewritten,review]) as model,patch.object(p,'validate_draft',side_effect=[ValueError('copied_passage'),rewritten]) as validate:
            draft,result=p.generate({'id':'candidate123','sourceName':'Newsroom','title':'Source title'},'full evidence',[])
        self.assertEqual(draft,rewritten)
        self.assertEqual(result,review)
        self.assertEqual(validate.call_count,2)
        self.assertIn('REWRITE REQUIRED',model.call_args_list[1].args[0])

    def test_copy_repair_retries_only_while_the_copy_gate_still_fails(self):
        first={'facts':[],'title':'First'}
        still_copied={'facts':[],'title':'Still copied'}
        rewritten={'facts':[],'title':'Rewritten'}
        review={'supported':True,'portuguese':True,'original':True,'duplicate':False}
        with tempfile.TemporaryDirectory() as directory,patch.object(p,'ROOT',Path(directory)),patch.object(p,'copied_passages',return_value=['trecho bloqueado']),patch.object(p,'model_call',side_effect=[first,still_copied,rewritten,review]) as model,patch.object(p,'validate_draft',side_effect=[ValueError('copied_passage'),ValueError('copied_passage'),rewritten]) as validate:
            draft,result=p.generate({'id':'candidate123','sourceName':'Newsroom','title':'Source title'},'full evidence',[])
        self.assertEqual(draft,rewritten)
        self.assertEqual(result,review)
        self.assertEqual(validate.call_count,3)
        self.assertEqual(model.call_args_list[2].args[1]['tentativa'],2)

    def test_copy_repair_redacts_the_exact_blocked_passage(self):
        copied='um dois três quatro cinco seis sete oito nove dez onze doze'
        first={'facts':[],'title':'First','description':'Description','paragraphs':[copied]}
        rewritten={'facts':[],'title':'Rewritten'}
        review={'supported':True,'portuguese':True,'original':True,'duplicate':False}
        with tempfile.TemporaryDirectory() as directory,patch.object(p,'ROOT',Path(directory)),patch.object(p,'model_call',side_effect=[first,rewritten,review]) as model,patch.object(p,'validate_draft',side_effect=[ValueError('copied_passage'),rewritten]):
            p.generate({'id':'candidate123','sourceName':'Newsroom','title':'Source title'},copied,[])
        payload=model.call_args_list[1].args[1]
        self.assertEqual(payload['trechosBloqueados'],1)
        self.assertNotIn(copied,json.dumps(payload,ensure_ascii=False))
        self.assertIn('[trecho a reformular]',payload['evidenciaCompleta'])

    def test_redaction_handles_punctuation_and_nested_draft_fields(self):
        copied='um dois três quatro cinco seis sete oito nove dez onze doze'
        value={'paragraphs':['Um, dois três quatro cinco seis sete oito nove dez onze doze. Fim.']}
        redacted=p.redact_blocked(value,[copied])
        self.assertEqual(redacted['paragraphs'],['[trecho a reformular]. Fim.'])

    def test_copy_matcher_keeps_the_existing_twelve_word_gate(self):
        copied='um dois três quatro cinco seis sete oito nove dez onze doze'
        draft={'title':'Original','description':'Description','paragraphs':[copied]}
        self.assertEqual(p.copied_passages(draft,copied),[p.normalized(copied)])

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
        body=' '.join('palavra'+str(index) for index in range(1000))
        options=selection.anchor_options(body)
        self.assertTrue(options)
        self.assertLessEqual(len(options),selection.MAX_ANCHOR_OPTIONS)
        self.assertTrue(all(evidence_anchor.matches(body,quote) for quote in options.values()))
        self.assertTrue(options['0'].startswith('palavra0 '))
        self.assertIn('palavra990',options[str(len(options)-1)])
        self.assertNotIn('invented',options)
