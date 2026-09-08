"""Create the downloadable source snapshot; omit credentials, caches and Sites identity."""
from pathlib import Path
import subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1];target=ROOT/'public/downloads/LinhaZero-source.zip';target.parent.mkdir(parents=True,exist_ok=True)
files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for rel in sorted(set(files)):
  if not rel or rel.startswith(('.openai/','public/downloads/','.cache/')) or '__qa-' in rel or rel.startswith('.env') and rel!='.env.example':continue
  path=ROOT/rel
  if path.is_file():z.write(path,'linha-zero/'+rel)
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 print(f'{len(z.namelist())} files; {target.stat().st_size} bytes; source archive verified')
