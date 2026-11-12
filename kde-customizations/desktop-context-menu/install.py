#!/usr/bin/env python3
"""Apply only the desktop context-menu opt-in and shared context roles."""
from pathlib import Path
import subprocess,datetime,shutil,json
source=Path(__file__).resolve().parent
shell=Path.home()/'.config/quickshell/caelestia'
patch=(source/'desktop-context-menu.patch').read_text()
args=['patch','--batch','-p0']
def check(mode):
 return subprocess.run(args+['--dry-run',mode],cwd=shell,input=patch,text=True,capture_output=True)
if check('--reverse').returncode==0:
 print('Desktop-Kontextmenü ist bereits angepasst.');raise SystemExit(0)
result=check('--forward')
if result.returncode:raise SystemExit('Die Shell wurde inzwischen an denselben Stellen geändert. Patch prüfen:\n'+result.stdout+result.stderr)
backup=Path.home()/'.local/state/ralleur-desktop/backups'/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-desktop-context-menu')
for name in json.loads((source/'files.json').read_text())+['context_menu.json']:
 path=shell/name
 if path.exists():
  target=backup/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
subprocess.run(args+['--forward'],cwd=shell,input=patch,text=True,check=True)
config=shell/'context_menu.json'
if config.exists():
 data=json.loads(config.read_text())
 for entry in data:
  if entry.get('action')=='OpenRightClickMenu':entry['label']='Menü anpassen'
 config.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
(source/'backup-latest.txt').write_text(str(backup)+'\n')
print(backup)
