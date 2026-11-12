#!/usr/bin/env python3
"""Install the three-set wallpaper picker on the current adapted shell."""
from pathlib import Path
from datetime import datetime
import subprocess
import shutil

here=Path(__file__).resolve().parent
shell=Path.home()/'.config/quickshell/caelestia'
patch=here.parent/'set-picker.patch'
files=['modules/nexus/pages/wallandstyle/WallpaperSelect.qml','services/Wallpapers.qml']
subprocess.run(['patch','--dry-run','--forward','-p0','-d',str(shell),'-i',str(patch)],check=True)
backup=Path.home()/'.local/state/ralleur-desktop/backups'/(datetime.now().strftime('%Y%m%d-%H%M%S')+'-wallpaper-sets')
for name in files:
 dest=backup/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(shell/name,dest)
shutil.copy2(Path.home()/'.config/caelestia/shell.json',backup/'shell.json')
try:
 subprocess.run(['patch','--forward','-p0','-d',str(shell),'-i',str(patch)],check=True)
except BaseException:
 for name in files:shutil.copy2(backup/name,shell/name)
 raise
(here/'evidence/backup.txt').write_text(str(backup)+'\n')
print('Installed. Backup:',backup)
