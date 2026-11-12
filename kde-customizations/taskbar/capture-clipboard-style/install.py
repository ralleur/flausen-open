#!/usr/bin/env python3
from pathlib import Path
import json,datetime,difflib,shutil,re
source=Path(__file__).resolve().parent
shell=Path.home()/'.config/quickshell/caelestia'
files={'modules/bar/popouts/'+name+'.qml':(source/(name+'.qml')).read_text() for name in ['ScreenCapture','ClipboardHistory','MenuCaptureCard','MenuScreenshotList','MenuRecordingList','MenuCaptureSplitButton']}
files['services/MenuStyle.qml']=(source.parent/'menu-style/MenuStyle.qml').read_text()
for helper in ['MenuPrimarySurface','PrimaryControlFill']:
 files['components/'+helper+'.qml']=(source.parent/('menu-style/'+helper+'.qml')).read_text()
files['components/controls/Menu.qml']=(source/'Menu.qml').read_text()
name='modules/bar/popouts/Content.qml';text=(shell/name).read_text()
for key in ['screencapture','clipboard']:
 text,count=re.subn(r'(name: "'+key+r'"\n)(\s*minScale: [0-9.]+\n)?',r'\1            minScale: 1.15\n',text,count=1)
 if count!=1:raise SystemExit('Unerwarteter Popout: '+key)
files[name]=text
name='modules/bar/popouts/ClipWrapper.qml'
def expand(match):
 keys=json.loads(match[1])
 for key in ['screencapture','clipboard']:
  if key not in keys:keys.append(key)
 return json.dumps(keys)+'.includes(content.currentName)'
text,count=re.subn(r'(\[[^\]\n]*"updateIndicator"[^\]\n]*\])\.includes\(content.currentName\)',expand,(shell/name).read_text())
if count!=1:raise SystemExit('Unerwartetes Glasprofil')
files[name]=text
changed={name:text for name,text in files.items() if not (shell/name).exists() or (shell/name).read_text()!=text}
if not changed:print('Screenshot und Zwischenablage sind bereits angepasst.');raise SystemExit(0)
backup=Path.home()/'.local/state/ralleur-taskbar-backups'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-capture-clipboard-style');backup.mkdir(parents=True)
patch=[];created=[]
for name,text in changed.items():
 target=shell/name;old=target.read_text() if target.exists() else ''
 if target.exists():
  saved=backup/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
 else:created.append(name)
 patch.extend(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile=name if old else '/dev/null',tofile=name))
(backup/'created.json').write_text(json.dumps(created,indent=2)+'\n')
for name,text in changed.items():(shell/name).write_text(text)
(source/'backup-latest.txt').write_text(str(backup)+'\n')
(source/'capture-clipboard-style.patch').write_text(''.join(patch))
print(backup)
