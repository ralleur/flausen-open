#!/usr/bin/env python3
"""Install a separate native wallpaper and select it for the KDE lock screen."""
from pathlib import Path
from datetime import datetime
import subprocess,json,argparse
ROOT=Path(__file__).resolve().parent
ID='com.flausen.kinetic.screensaver'
STATE=Path.home()/'.local/state/flausen-os/screensaver'
RECORD=STATE/'installed.json'
def read_plugin():
    return subprocess.check_output(['kreadconfig6','--file','kscreenlockerrc','--group','Greeter','--key','WallpaperPlugin'],text=True).strip()
def select(plugin):
    subprocess.run(['kwriteconfig6','--file','kscreenlockerrc','--group','Greeter','--key','WallpaperPlugin',plugin],check=True)
def install():
    STATE.mkdir(parents=True,exist_ok=True)
    if not RECORD.exists():
        RECORD.write_text(json.dumps({'before':read_plugin(),'selected':ID,'time':datetime.now().astimezone().isoformat()},indent=2)+'\n')
    target=Path.home()/'.local/share/plasma/wallpapers'/ID
    subprocess.run(['kpackagetool6','--type','Plasma/Wallpaper','--upgrade' if target.exists() else '--install',str(ROOT/'wallpaper')],check=True)
    select(ID)
    print('Selected flausen. Kinetic Playground for the next screen lock.')
def restore():
    record=json.loads(RECORD.read_text())
    if read_plugin()!=ID:raise SystemExit('The wallpaper selection has since changed; keeping it.')
    select(record['before']);RECORD.unlink();print('Previous lockscreen wallpaper restored.')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--restore',action='store_true')
    restore() if parser.parse_args().restore else install()
