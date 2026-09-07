"""Commit only generated editorial data. Repository token is confined to push."""
import base64,os,subprocess
def git(*args,**kwargs):return subprocess.run(['git',*args],check=True,text=True,**kwargs)
git('add','data','content/news')
changed=subprocess.run(['git','diff','--cached','--quiet']).returncode==1
if changed:
 git('config','user.name','github-actions[bot]');git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
 git('commit','-m','chore: record editorial collection and approved edition')
 env=os.environ.copy();token=env.pop('GITHUB_TOKEN');auth=base64.b64encode(('x-access-token:'+token).encode()).decode()
 env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.extraHeader',GIT_CONFIG_VALUE_0='Authorization: Basic '+auth)
 git('push','origin','HEAD:main',env=env)
sha=git('rev-parse','--verify','HEAD',capture_output=True).stdout.strip()
if output:=os.environ.get('GITHUB_OUTPUT'):
 with open(output,'a') as f:f.write(f'changed={str(changed).lower()}\nsha={sha}\n')
print('Editorial data committed.' if changed else 'No changes to commit.')
