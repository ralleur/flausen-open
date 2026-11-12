#!/usr/bin/env python3
"""Apply the shared menu skin to media, audio, battery and calendar."""
from datetime import datetime,timezone
import difflib
import json
from pathlib import Path
import re
import shutil
import sys

SOURCE=Path(__file__).resolve().parent
SHELL=Path.home()/'.config/quickshell/caelestia'


def install():
    if not (SHELL/'services/MenuStyle.qml').exists():
        raise SystemExit('Zuerst den gemeinsamen Menüstil installieren.')
    names=['Media','Audio','Battery','CalendarPopout','CalendarGlass','MenuAudioSection','MenuAudioSlider','MenuAppStreamRow']
    files={'modules/bar/popouts/'+name+'.qml':(SOURCE/(name+'.qml')).read_text() for name in names}
    files['modules/bar/components/Clock.qml']=(SOURCE/'Clock.qml').read_text()
    path='modules/bar/components/WeatherWidget.qml'
    text=(SHELL/path).read_text()
    old='            font: Tokens.font.body.medium'
    new='''            font: {
                // Use the same size, weight and family as the horizontal clock.
                const rawScale = !isNaN(Config.bar.scale) ? Config.bar.scale : 1.0;
                const thickness = rawScale < 1.0 ? Tokens.sizes.bar.innerWidth
                    : Math.round(Tokens.sizes.bar.innerWidth * rawScale);
                const value = Tokens.font.body.builders.small.size(Math.round(thickness * 0.32)).build();
                value.family = MenuStyle.fontFamily;
                return value;
            }'''
    previous='''            font: {
                const value = Tokens.font.body.medium;
                value.family = MenuStyle.fontFamily;
                return value;
            }'''
    if previous in text:text=text.replace(previous,new)
    if new not in text:
        if text.count(old)!=1:raise SystemExit('Unerwartete Wetterschrift: '+path)
        text=text.replace(old,new)
    text=text.replace('            color: Colours.palette.m3onSurface', '            color: Colours.barForeground')
    files[path]=text
    path='modules/bar/popouts/Content.qml';text=(SHELL/path).read_text()
    for name in ['media','audio','battery']:
        pattern=r'(name: "'+name+r'"\n)(\s*minScale: [0-9.]+\n)?'
        text,count=re.subn(pattern,r'\1            minScale: 1.15\n',text,count=1)
        if count!=1:raise SystemExit('Unerwarteter Popout-Aufbau: '+name)
    files[path]=text
    path='modules/bar/popouts/ClipWrapper.qml'
    def extend(match):
        keys=json.loads(match.group(1))
        for name in ['audio','battery','clock']:
            if name not in keys:keys.append(name)
        return json.dumps(keys)+'.includes(content.currentName)'
    text,count=re.subn(r'(\[[^\]\n]*"updateIndicator"[^\]\n]*\])\.includes\(content.currentName\)',extend,(SHELL/path).read_text())
    if count<1:raise SystemExit('Unerwartetes gemeinsames Glasprofil')
    files[path]=text
    sys.path.insert(0, str(SOURCE.parent/'menu-style'))
    from taskbar_glass import configure
    configure(files, SHELL)
    changed={name:text for name,text in files.items() if not (SHELL/name).exists() or (SHELL/name).read_text()!=text}
    if not changed:
        print('Now Playing, Audio, Akku und Kalender sind bereits angepasst.');return
    backup=Path.home()/'.local/state/ralleur-taskbar-backups'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-remaining-overlays')
    backup.mkdir(parents=True);patch=[];created=[]
    for name,text in changed.items():
        target=SHELL/name;old=target.read_text() if target.exists() else ''
        if target.exists():
            saved=backup/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
        else:created.append(name)
        patch.extend(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile=name if old else '/dev/null',tofile=name))
    (backup/'created.json').write_text(json.dumps(created,indent=2)+'\n')
    for name,text in changed.items():(SHELL/name).write_text(text)
    (SOURCE.parent/'remaining-overlays.patch').write_text(''.join(patch))
    (SOURCE.parent/'evidence/remaining-overlays-backup.txt').write_text(str(backup)+'\n')
    print(backup)


if __name__=='__main__':install()
