"""Create one deduplicated issue when an editorial collection is degraded."""
import json,os,urllib.request
from pathlib import Path

state=json.loads(Path('data/operation-state.json').read_text())
errors=state.get('result',{}).get('collection',{}).get('errors',[])
if not errors:raise SystemExit(0)
repo=os.environ['GITHUB_REPOSITORY'];title='Coleta editorial com fontes indisponíveis'
def api(path,data=None):
 req=urllib.request.Request('https://api.github.com/repos/'+repo+path,data=json.dumps(data).encode() if data else None,headers={'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],'Accept':'application/vnd.github+json'})
 with urllib.request.urlopen(req,timeout=20) as response:return json.load(response)
if any(issue['title']==title for issue in api('/issues?state=open&per_page=100')):raise SystemExit(0)
affected=', '.join(sorted({error.get('source','fonte não identificada') for error in errors}))
body=f'A coleta terminou com falhas parciais. Fontes afetadas: {affected}.\n\nA última versão válida foi preservada. Consulte os registros da execução para diagnosticar a causa. Coleta bem-sucedida em outras fontes não significa publicação de matéria.'
api('/issues',{'title':title,'body':body})
