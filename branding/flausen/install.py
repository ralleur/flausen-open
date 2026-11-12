#!/usr/bin/env python3
"""Install user-local brand assets and the supported Caelestia logo setting."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
HOME=Path.home()
DATA=Path(os.environ.get('XDG_DATA_HOME',HOME/'.local/share'))
STATE=Path(os.environ.get('XDG_STATE_HOME',HOME/'.local/state'))/'flausen-os'
CONFIG=Path(os.environ.get('XDG_CONFIG_HOME',HOME/'.config'))/'caelestia/shell.json'
CURRENT=STATE/'branding.json'

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def save(path,content):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.flausen-new');temp.write_bytes(content);temp.replace(path)

def config(): return json.loads(CONFIG.read_text())

def verify(record):
    for item in record['files']:
        p=Path(item['path'])
        if p.is_symlink() or digest(p)!=item['sha256']: raise SystemExit(f'Geänderte Datei bleibt erhalten: {p}')
    if config().get('general',{}).get('logo')!=record['logo']: raise SystemExit('Logo wurde später geändert; Rückbau abgebrochen.')

def install():
    if CURRENT.exists():
        verify(json.loads(CURRENT.read_text()));print('Bereits installiert. Für neue Assets zuerst zurückbauen.');return
    if CONFIG.is_symlink(): raise SystemExit('Symbolische Konfiguration bleibt erhalten.')
    cfg=config()
    if not isinstance(cfg.get('general',{}),dict): raise SystemExit('Unbekanntes Konfigurationsformat.')
    sysinfo=Path(os.environ.get('XDG_CONFIG_HOME',HOME/'.config'))/'quickshell/caelestia/utils/SysInfo.qml'
    if not sysinfo.exists() or 'GlobalConfig.general.logo' not in sysinfo.read_text(): raise SystemExit('Installiertes Caelestia unterstützt den erwarteten Logo-Schlüssel nicht.')
    backup=STATE/('branding-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    shutil.copy2(CONFIG,backup/'shell.json')
    payload=DATA/'flausen-os/branding'
    sources=[ROOT/'About.qml',ROOT/'flausen-about']
    sources+=list((ROOT/'generated').rglob('*'))+list((ROOT/'handoff/assets').rglob('*'))
    sources+=[ROOT/'handoff/ATTRIBUTION_AND_RELEASE.md']
    files={payload/p.relative_to(ROOT):p.read_bytes() for p in sources if p.is_file()}
    files[DATA/'icons/hicolor/scalable/apps/flausen-os.svg']=(ROOT/'handoff/assets/logos/flausen-symbol-transparent.svg').read_bytes()
    for p in (ROOT/'handoff/assets/icons').glob('*.png'):
        size=p.stem.split('-')[-1];files[DATA/f'icons/hicolor/{size}x{size}/apps/flausen-os.png']=p.read_bytes()
    desktop=f'''[Desktop Entry]
Type=Application
Name=About flausen.
Name[de]=Über flausen.
Comment=Everyday OS by ralleur
Exec=/bin/sh "{payload}/flausen-about"
Icon=flausen-os
Categories=Settings;System;
Keywords=flausen;OS;System;About;
Terminal=false
StartupNotify=false
'''
    files[DATA/'applications/flausen-os-about.desktop']=desktop.encode()
    for p in files:
        if p.is_symlink(): raise SystemExit(f'Symbolische Datei bleibt erhalten: {p}')
    record={'files':[],'config':str(CONFIG),'logoBefore':cfg.get('general',{}).get('logo'),'hadLogo':'logo' in cfg.get('general',{}),'hadGeneral':'general' in cfg,'logo':str(payload/'handoff/assets/logos/flausen-symbol-transparent.svg'),'backup':str(backup)}
    try:
        for i,(p,content) in enumerate(files.items()):
            before=str(backup/str(i)) if p.exists() else None
            if before: shutil.copy2(p,before)
            record['files'].append({'path':str(p),'before':before})
            save(p,content);record['files'][-1]['sha256']=digest(p)
        cfg.setdefault('general',{})['logo']=record['logo']
        save(CONFIG,(json.dumps(cfg,ensure_ascii=False,indent=4)+'\n').encode())
        save(CURRENT,(json.dumps(record,indent=2)+'\n').encode())
    except BaseException:
        for item in reversed(record['files']):
            p=Path(item['path'])
            if item['before']: shutil.copy2(item['before'],p)
            else: p.unlink(missing_ok=True)
        shutil.copy2(backup/'shell.json',CONFIG)
        raise
    print(f'flausen. installiert. Sicherung: {backup}')

def restore():
    record=json.loads(CURRENT.read_text());verify(record)
    cfg=config()
    for item in reversed(record['files']):
        p=Path(item['path'])
        if item['before']: shutil.copy2(item['before'],p)
        else:p.unlink()
    if record['hadLogo']: cfg['general']['logo']=record['logoBefore']
    else: cfg['general'].pop('logo',None)
    if not record['hadGeneral'] and not cfg['general']: cfg.pop('general')
    save(CONFIG,(json.dumps(cfg,ensure_ascii=False,indent=4)+'\n').encode())
    CURRENT.unlink();print('Vorherige Marke wiederhergestellt; weitere Einstellungen erhalten.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--restore',action='store_true');args=parser.parse_args()
    restore() if args.restore else install()
