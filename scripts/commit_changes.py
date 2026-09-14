"""Commit only durable data for an approved edition. Repository token is confined to push."""
import base64,os,subprocess

def git(*args,**kwargs):
 return subprocess.run(['git',*args],check=True,text=True,**kwargs)

def status(*paths):
 result=subprocess.run(['git','status','--porcelain','--',*paths],check=True,text=True,capture_output=True)
 return bool(result.stdout.strip())

# A closing that only updates transient collection/diagnostic state must not create a commit.
# New or corrected public article content is the transaction boundary for a publication.
changed=status('content/news')
if changed:
 git('add','content/news','public/images/news','data/publishing-state.json','data/evidence','data/image-rights.json')
 changed=subprocess.run(['git','diff','--cached','--quiet']).returncode==1

if changed:
 git('config','user.name','github-actions[bot]');git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
 git('commit','-m','chore: publica edição editorial aprovada')
 env=os.environ.copy();token=env.pop('GITHUB_TOKEN');auth=base64.b64encode(('x-access-token:'+token).encode()).decode()
 env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.extraHeader',GIT_CONFIG_VALUE_0='Authorization: Basic '+auth)
 git('push','origin','HEAD:main',env=env)

sha=git('rev-parse','--verify','HEAD',capture_output=True).stdout.strip()
if output:=os.environ.get('GITHUB_OUTPUT'):
 with open(output,'a') as f:f.write(f'changed={str(changed).lower()}\nsha={sha}\n')
print('Approved edition committed.' if changed else 'No published article changes; nothing to commit.')
