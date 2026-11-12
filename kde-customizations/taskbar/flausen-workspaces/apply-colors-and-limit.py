#!/usr/bin/env python3
"""Install colored workspace icons, the desktop menu and the eight-desktop limit."""
from pathlib import Path
from datetime import datetime
import json, shutil, subprocess, sys, time
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
HOME=Path.home()
SHELL=HOME/'.config/quickshell/caelestia'
REL=Path('modules/bar/components/workspaces')
menu = Path('modules/bar/popouts/TaskbarContext.qml')
management_patch = HERE/'desktop-management.patch'
patch_command = ['patch', '--batch', '--fuzz=0', '-p1', '-d', str(SHELL), '-i', str(management_patch)]
needs_patch = subprocess.run([*patch_command, '--dry-run', '--forward'], capture_output=True).returncode == 0
if not needs_patch:
    subprocess.run([*patch_command, '--dry-run', '--reverse'], check=True, capture_output=True)

backup=HOME/'.local/state/ralleur-desktop/backups'/(datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'-desktop-management')
backup.mkdir(parents=True)
sys.path.insert(0,str(REPO/'kde-customizations/fullscreen-desktops/tests'))
from kwin import report
state=report('const result={desktops:workspace.desktops.map(d=>({id:d.id,name:d.name})),current:workspace.currentDesktop.id,windows:workspace.windowList().map(w=>({id:w.internalId.toString(),desktops:w.desktops.map(d=>d.id)}))};')
(backup/'desktops.json').write_text(json.dumps(state,indent=2)+'\n')
shutil.copy2(HOME/'.config/kwinrc',backup/'kwinrc')
files=[REL/'FlausenWorkspaceIcon.qml', REL/'ActiveIndicator.qml']+[REL/'flausen-shapes'/p.name for p in (HERE/'shapes').glob('*.svg')]
files += [menu, Path('modules/bar/popouts/PopoutState.qml'),
          Path('modules/bar/popouts/Content.qml'), Path('modules/bar/popouts/Wrapper.qml'),
          Path('modules/bar/BarWrapper.qml'), REL/'Workspaces.qml']
for file in files:
 dest=backup/file;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SHELL/file,dest)
shutil.copy2(HERE/'FlausenWorkspaceIcon.qml', SHELL/REL/'FlausenWorkspaceIcon.qml')
for shape in (HERE/'shapes').glob('*.svg'):
    shutil.copy2(shape, SHELL/REL/'flausen-shapes'/shape.name)
p=SHELL/REL/'ActiveIndicator.qml';old=p.read_text()
new=old.replace('    Colouriser {\n        source: root.mask\n        sourceColor: Colours.barForeground\n        colorizationColor: Colours.barForeground','    ShaderEffectSource {\n        sourceItem: root.mask\n        live: true\n        hideSource: false')
if new==old and 'sourceItem: root.mask' not in old:raise SystemExit('Unexpected active indicator component; backup: '+str(backup))
p.write_text(new)
if needs_patch:
    subprocess.run([*patch_command, '--forward'], check=True)
shutil.copy2(HERE.parent/'overlay'/menu, SHELL/menu)
package=HOME/'.local/share/kwin/scripts/flausen-four-desktops'
if package.exists():shutil.copytree(package,backup/'four-desktops-package')
(package/'contents/code').mkdir(parents=True,exist_ok=True)
shutil.copy2(HERE/'four-desktops/main.js',package/'contents/code/main.js');shutil.copy2(HERE/'four-desktops/metadata.json',package/'metadata.json')
def run(*args):return subprocess.check_output(args,text=True).strip()
fullscreen=HOME/'.local/share/kwin/scripts/ralleur-fullscreen-desktops/contents/code/main.js'
# Only the legacy variant creates desktops. Preserve the newer fixed-pool router.
if fullscreen.exists() and 'workspace.createDesktop(' in fullscreen.read_text():
    run('kwriteconfig6','--file','kwinrc','--group','Plugins','--key','ralleur-fullscreen-desktopsEnabled','false')
    run('qdbus6','org.kde.KWin','/Scripting','unloadScript','ralleur-fullscreen-desktops')
run('kwriteconfig6','--file','kwinrc','--group','Plugins','--key','flausen-four-desktopsEnabled','true')
scripting = ('qdbus6', 'org.kde.KWin', '/Scripting')
plugin = 'flausen-four-desktops'
run(*scripting, 'unloadScript', plugin)
deadline = time.monotonic() + 2
while run(*scripting, 'isScriptLoaded', plugin) == 'true':
    if time.monotonic() >= deadline:
        raise SystemExit(f'KWin did not unload {plugin}; backup: {backup}')
    time.sleep(0.05)
# Start via KWin's package loader. Numeric Script IDs can collide after unloading.
run(*scripting, 'start')
if run(*scripting, 'isScriptLoaded', plugin) != 'true':
    raise SystemExit(f'KWin did not load {plugin}; backup: {backup}')
(HERE/'color-limit-backup.txt').write_text(str(backup)+'\n')
print('Installed. Backup:',backup)
