"""Durable Actions artifact even when no article can be published. No main commit."""
import json,os
from pathlib import Path

def report(root=Path('.')):
    run=os.environ.get('GITHUB_RUN_ID')
    def read(path):
        try:return json.loads((root/path).read_text())
        except (OSError,ValueError):return {}
    state=read('data/operation-state.json')
    # Never present an older checked-in execution as this run's outcome.
    if not run or str(state.get('runId'))!=run:
        state={'status':'not_recorded','reason':'pipeline did not produce a result for this run'}
    result={'runId':run,'attempt':os.environ.get('GITHUB_RUN_ATTEMPT'),
        'pipelineOutcome':os.environ.get('PIPELINE_OUTCOME'), 'operation':state,
        'snapshotRestore':read('.cache/scout/restore.json')}
    path=root/'.cache/editorial-report.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if summary:=os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(summary,'a') as f:f.write('\nResultado editorial\n```json\n'+json.dumps(result,ensure_ascii=False,indent=2)+'\n```\n')
    return result
if __name__=='__main__':report()
