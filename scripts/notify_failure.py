"""One issue per failed trusted main-branch run; no speculative remediation."""
import json,os,urllib.request
event=json.load(open(os.environ['GITHUB_EVENT_PATH']));run=event['workflow_run'];repo=os.environ['GITHUB_REPOSITORY']
if run['conclusion']!='failure' or run['head_branch']!='main' or run['head_repository']['full_name']!=repo:raise SystemExit(0)
title=f"Automação requer atenção: {run['name']} #{run['run_number']}"
def api(path,data=None):
 req=urllib.request.Request('https://api.github.com/repos/'+repo+path,headers={'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'},data=json.dumps(data).encode() if data else None)
 with urllib.request.urlopen(req,timeout=25) as r:return json.load(r)
if any(i['title']==title for i in api('/issues?state=all&per_page=100')):raise SystemExit(0)
body=f"""**Ação necessária**\nRevisar a execução que falhou antes de autorizar qualquer alteração de acesso, custo ou infraestrutura.\n\n**Motivo**\nO workflow terminou com falha. A causa ainda precisa ser confirmada no log.\n\n**Impacto**\nA edição ou a atualização do site pode estar atrasada. Conteúdo válido deve ser preservado.\n\n**Risco**\nNão executar rollback destrutivo, ampliar permissões globais ou contratar serviços como resposta automática.\n\n**Alternativa**\nManter a última versão válida e pausar temporariamente a rotina.\n\n**Diagnóstico**\n[Consultar a execução]({run['html_url']}).\n"""
api('/issues',{'title':title,'body':body})
