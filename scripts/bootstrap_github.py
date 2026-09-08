"""Create ONLY a new public dedicated repo. Run locally with authenticated gh."""
import argparse,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--owner',default='humbertomennella');parser.add_argument('--repo',default='framenexo');a=parser.parse_args()
if not shutil.which('gh'):raise SystemExit('Instale o GitHub CLI e execute gh auth login no seu computador. Não cole tokens em arquivos.')
def run(args,cwd=None,capture=False):return subprocess.run(args,cwd=cwd,check=True,text=True,capture_output=capture)
login=run(['gh','api','user','--jq','.login'],capture=True).stdout.strip()
if login!=a.owner:raise SystemExit('A conta autenticada não corresponde ao proprietário solicitado.')
full=f'{a.owner}/{a.repo}'
exists=subprocess.run(['gh','repo','view',full,'--json','name'],capture_output=True,text=True)
if exists.returncode==0:raise SystemExit('Repositório já existe. O script não altera nem sobrescreve repositórios existentes.')
if 'not found' not in exists.stderr.lower() and 'could not resolve' not in exists.stderr.lower():raise SystemExit('Não foi possível confirmar a ausência do repositório. Verifique o acesso e tente novamente.')
with tempfile.TemporaryDirectory(prefix='framenexo-github-') as temp:
 target=Path(temp)/a.repo
 shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('.git','.openai','node_modules','dist','.astro','.cache','__pycache__','.venv','.env','.env.local','downloads','*.pyc','*.tar.gz'))
 # The initial scheduled job will record real operational status after it executes.
 status=json.loads((target/'data/deployment-status.json').read_text());status.update(repository=full,notes='Repositório criado. Consulte as execuções para confirmar a ativação da rotina.');(target/'data/deployment-status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
 run(['git','init','-b','main'],target);run(['git','config','user.name',login],target);run(['git','config','user.email',f'{login}@users.noreply.github.com'],target);run(['git','add','.'],target);run(['git','commit','-m','feat: launch Vértice Factual editorial portal'],target)
 run(['gh','repo','create',full,'--public','--source',str(target),'--remote','origin','--description','Brasil, mundo e contexto.'])
 # Enable Pages before the first push triggers the deployment workflow.
 try:run(['gh','api','--method','POST',f'repos/{full}/pages','-f','build_type=workflow'])
 except subprocess.CalledProcessError:print('Pages não ativado automaticamente. Configure Settings > Pages > GitHub Actions. O repositório foi criado e o código será enviado.')
 run(['git','push','-u','origin','main'],target)
 print(f'Repositório: https://github.com/{full}\nAcompanhe Actions; a conclusão depende dos workflows e das permissões da conta.')
