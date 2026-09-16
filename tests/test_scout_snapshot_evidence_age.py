"""Regression coverage for Scout snapshot/evidence freshness semantics."""
import datetime as dt
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pipeline as p
import scout_snapshot as s

REPO='humbertomennella/framenexo'


class SnapshotEvidenceAgeRegression(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.root_patch=patch.object(p,'ROOT',self.root)
        self.root_patch.start();self.addCleanup(self.root_patch.stop)
        self.env=patch.dict(os.environ,GITHUB_REPOSITORY=REPO,GITHUB_RUN_ID='100',GITHUB_RUN_ATTEMPT='1')
        self.env.start();self.addCleanup(self.env.stop)

    def test_snapshot_remains_valid_after_embedded_evidence_expires(self):
        created=dt.datetime(2026,9,16,1,46,tzinfo=dt.timezone.utc)
        candidate=dict(id='abc123',url='https://example.com/news',title='Verified report',sourceId='official',
                       sourceName='Official',sourceType='primary',category='Tecnologia',publishedAt=p.iso(created),
                       relevance=90,status='candidate')
        p.write('.cache/evidence/abc123.json',dict(url=candidate['url'],text='verified evidence',
                                                   fetchedAt=p.iso(created-dt.timedelta(hours=23,minutes=30))))
        with patch.object(p,'now',return_value=created):
            document=s.create([candidate],dict(status='healthy',publishingAllowed=False,sourcesReached=1))

        later=created+dt.timedelta(hours=11)
        payload=s.validate(document,at=later)
        with patch.object(p,'now',return_value=later):
            s.restore_evidence(payload)

        self.assertFalse((self.root/'.cache/evidence/abc123.json').exists())


if __name__=='__main__':unittest.main()
