#!/usr/bin/env python3
"""Install dashboard typography/material without replacing unrelated shell edits."""
from pathlib import Path
import datetime, difflib, shutil, sys
source=Path(__file__).resolve().parent
shell=Path.home()/'.config/quickshell/caelestia'
for name in ['services/MenuStyle.qml','components/MenuText.qml']:
 if not (shell/name).exists():raise SystemExit('Zuerst taskbar/menu-style/install.py ausführen: '+name)
files={str(p.relative_to(source/'overlay')):p.read_text() for p in (source/'overlay').rglob('*.qml')}
name='modules/drawers/ContentWindow.qml';text=(shell/name).read_text()
needle='            id: dashBg\n'
if text.count(needle)!=1:raise SystemExit('Dashboard-Hintergrund nicht eindeutig')
if needle+'            group: null' not in text:
 text=text.replace(needle,needle+'            group: null // Dashboard draws the shared menu glass itself.\n',1)
marker="        // Dashboard glass shares the existing KWin effect."
if marker not in text:
 anchor="        // Floating taskbar popouts use the start menu's independent rounded blur."
 if text.count(anchor)!=1:raise SystemExit('Gemeinsame Blur-Region nicht gefunden')
 text=text.replace(anchor,marker+"""
        Region {
            x: panels.dashboard.x + panels.leftMargin
            y: panels.dashboard.y + panels.topMargin
            width: panels.dashboard.visible ? panels.dashboard.width : 0
            height: panels.dashboard.visible ? panels.dashboard.height : 0
            radius: Tokens.rounding.extraLarge
            intersection: Intersection.Combine
        }
"""+anchor)
files[name]=text
sys.path.insert(0,str(source.parent/'menu-style'))
from taskbar_glass import configure
configure(files,shell)
changed={n:t for n,t in files.items() if not (shell/n).exists() or (shell/n).read_text()!=t}
if not changed:print('Dashboard-Stil ist bereits installiert.');raise SystemExit(0)
backup=Path.home()/'.local/state/ralleur-taskbar-backups'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-dashboard-style')
patch=[]
for n,t in changed.items():
 target=shell/n;saved=backup/n;saved.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():shutil.copy2(target,saved)
 patch.extend(difflib.unified_diff((target.read_text() if target.exists() else '').splitlines(True),t.splitlines(True),fromfile=n,tofile=n))
for n,t in changed.items():(shell/n).write_text(t)
(source/'backup-latest.txt').write_text(str(backup)+'\n')
(source/'dashboard-style.patch').write_text(''.join(patch))
print(backup)
