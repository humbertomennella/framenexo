"""Tiny local server that mounts the static build at BASE_PATH for UI tests."""
import os
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]/'dist'
BASE='/' + os.environ.get('BASE_PATH','/').strip('/')
if BASE!='/' : BASE+='/'

class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  request_path=urlsplit(path).path
  if BASE!='/' and request_path.startswith(BASE):request_path='/'+request_path[len(BASE):]
  clean=Path(request_path.lstrip('/'))
  target=(ROOT/clean).resolve()
  return str(target if ROOT.resolve() in (target,*target.parents) else ROOT)
 def log_message(self,format,*args):pass

ThreadingHTTPServer(('127.0.0.1',4337),Handler).serve_forever()
