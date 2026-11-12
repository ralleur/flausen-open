#!/usr/bin/env python3
"""Verify installed dock geometry at both size limits and restore the initial scale.

Restarts the desktop shell for each size. Run only in an idle HDMI-A-2 session.
"""
from pathlib import Path
import subprocess,json,time
shell='/home/USER/.config/quickshell/caelestia'
def state():return json.loads(subprocess.check_output(['quickshell','ipc','-p',shell,'call','ralleurTaskbar-HDMI-A-2','inspect'],text=True,stderr=subprocess.DEVNULL))
initial=state()['dock']['scale'];out={}
def load(scale):
 subprocess.run(['systemctl','--user','stop','caelestia-shell.service'],check=True)
 subprocess.run(['kwriteconfig6','--file',str(Path.home()/'.config/Caelestia/caelestia-shell.conf'),'--group','RalleurTaskbar','--key','dockScale',str(scale)],check=True)
 subprocess.run(['systemctl','--user','start','caelestia-shell.service'],check=True)
 for _ in range(80):
  try:
   s=state()
   if s['dock']['sections']['apps'] and abs(s['dock']['scale']-scale)<.001:return s
  except (subprocess.CalledProcessError,KeyError,TypeError):pass
  time.sleep(.1)
 raise AssertionError('shell did not load requested scale')
try:
 out['minimum']=load(.4);out['maximum']=load(3.2)
 assert out['minimum']['dock']['height']==16
 assert out['maximum']['dock']['height']==128
 assert out['minimum']['dock']['sections']['itemSize']==16
 assert out['maximum']['dock']['sections']['itemSize']==128
 assert out['minimum']['top']['height']==out['maximum']['top']['height']
 out['passed']=True
finally:
 out['restored']=load(initial)
 Path('/home/USER/ralleurOS/kde-customizations/taskbar/evidence/dock-size-range-check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:{'scale':v['dock']['scale'],'height':v['dock']['height'],'width':v['dock']['width']} for k,v in out.items() if isinstance(v,dict)}))
