"""Commit one approved editorial transaction. Scout-only changes never reach main."""
import base64,os,subprocess

def git(*args,**kwargs):
 return subprocess.run(['git',*args],check=True,text=True,**kwargs)

def status(*paths):
 result=subprocess.run(['git','status','--porcelain','--',*paths],check=True,text=True,capture_output=True)
 return bool(result.stdout.strip())

# Public article creation/correction is the transaction boundary. The companion
# files below may travel with a real edition, but can never create a commit by
# themselves. This preserves closing decisions without reviving Scout commits.
changed=status('content/news')
if changed:
 git('add',
     'content/news',
     'public/images/news',
     'data/publishing-state.json',
     'data/candidates.json',
     'data/scout-state.json',
     'data/editorial-log.json',
     'data/operation-state.json',
     'data/deployment-status.json',
     'data/evidence',
     'data/image-rights.json')
 changed=subprocess.run(['git','diff','--cached','--quiet']).returncode==1

if changed:
 git('config','user.name','github-actions[bot]')
 git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
 git('commit','-m','chore: publica edição editorial aprovada')
 env=os.environ.copy();token=env.pop('GITHUB_TOKEN');auth=base64.b64encode(('x-access-token:'+token).encode()).decode()
 env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.extraHeader',GIT_CONFIG_VALUE_0='Authorization: Basic '+auth)
 # The editorial job can run for several minutes while maintenance commits land
 # on main. Rebase the approved edition onto the latest main before pushing so a
 # harmless concurrent workflow/config change cannot kill a valid publication.
 git('fetch','origin','main',env=env)
 git('rebase','origin/main')
 git('push','origin','HEAD:main',env=env)

sha=git('rev-parse','--verify','HEAD',capture_output=True).stdout.strip()
if output:=os.environ.get('GITHUB_OUTPUT'):
 with open(output,'a') as f:f.write(f'changed={str(changed).lower()}\nsha={sha}\n')
print('Approved edition committed.' if changed else 'No public article changes; nothing to commit.')
