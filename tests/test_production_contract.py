"""Regression contracts for production safety and durable editorial state."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def published_metadata():
    rows=[]
    for path in (ROOT/'content/news').glob('*.md'):
        parts=path.read_text().split('---',2)
        if len(parts)<3:
            continue
        meta=json.loads(parts[1])
        if meta.get('status')=='published':
            rows.append(meta)
    return rows


class ProductionContract(unittest.TestCase):
    def test_failed_editorial_pipeline_cannot_validate_or_commit(self):
        workflow=(ROOT/'.github/workflows/collector.yml').read_text()
        self.assertIn("- cron: '7 1,11,16,21 * * *'",workflow)
        self.assertIn("- cron: '27 1,11,16,21 * * *'",workflow)
        self.assertNotIn("- cron: '7 * * * *'",workflow)
        self.assertNotIn("- cron: '27 * * * *'",workflow)
        self.assertNotIn("- cron: '0 * * * *'",workflow)
        self.assertIn("group: framenexo-editorial",workflow)
        self.assertIn("cancel-in-progress: false",workflow)
        self.assertIn("- name: Validar antes de salvar conteúdo\n        if: steps.pipeline.outcome == 'success'",workflow)
        self.assertIn("- name: Salvar edição aprovada\n        if: steps.pipeline.outcome == 'success'",workflow)
        self.assertIn("if: steps.pipeline.outcome == 'failure'",workflow)

    def test_commit_is_bound_to_public_article_changes(self):
        script=(ROOT/'scripts/commit_changes.py').read_text()
        self.assertIn("changed=status('content/news')",script)
        self.assertNotIn("git('add','data'",script)
        for path in (
            'data/publishing-state.json','data/candidates.json','data/scout-state.json',
            'data/editorial-log.json','data/operation-state.json','data/deployment-status.json',
            'data/evidence','data/image-rights.json'):
            self.assertIn(repr(path),script)

    def test_publishing_state_matches_latest_public_article(self):
        rows=published_metadata()
        self.assertTrue(rows)
        state=json.loads((ROOT/'data/publishing-state.json').read_text())
        latest=max(row['publishedAt'] for row in rows)
        self.assertEqual(state.get('lastPublishedAt'),latest)
        slugs={row.get('slug') for row in state.get('history',[])}
        latest_slugs={row['slug'] for row in rows if row['publishedAt']==latest}
        self.assertTrue(latest_slugs <= slugs)

    def test_public_status_uses_four_daily_editorial_windows(self):
        status=(ROOT/'src/pages/status.astro').read_text()
        live=(ROOT/'src/components/LiveOperations.astro').read_text()
        schedule=json.loads((ROOT/'data/edition-schedule.json').read_text())
        self.assertEqual(schedule['slots'],[8,13,18,22])
        self.assertEqual(schedule['maxArticlesPerEdition'],20)
        self.assertEqual(schedule['targetPerCategory'],2)
        self.assertEqual(schedule['maxPerCategory'],2)
        self.assertIn('editionHoursLabel',status)
        self.assertIn('08h, 13h, 18h e 22h',status)
        self.assertIn('20 matérias',status)
        self.assertNotIn('de hora em hora',status)
        self.assertIn("latest('scout.yml')",live)
        self.assertIn("latest('collector.yml')",live)
        self.assertNotIn('setInterval',live)

    def test_no_legacy_site_fallback_or_aplus_abbreviation(self):
        astro=(ROOT/'astro.config.mjs').read_text()
        article=(ROOT/'src/pages/noticias/[slug].astro').read_text()
        self.assertNotIn('framenexo.humberto-mennella.chatgpt.site',astro)
        self.assertNotIn('>A+</span>',article)


if __name__=='__main__':
    unittest.main()
