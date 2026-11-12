#!/usr/bin/env python3
"""Share the launcher's typography/material without changing menu geometry."""
from datetime import datetime, timezone
import difflib
import json
from pathlib import Path
import re
import shutil

SOURCE = Path(__file__).resolve().parent
SHELL = Path.home() / '.config/quickshell/caelestia'
REPO = SOURCE.parents[2]
PANELS = {
    'modules/bar/popouts/Updates.qml': SOURCE.parent / 'update-hub/Updates.qml',
    'modules/bar/popouts/Network.qml': SOURCE.parent / 'network-popover/Network.qml',
    'modules/bar/popouts/WirelessPassword.qml': SOURCE.parent / 'network-popover/WirelessPassword.qml',
    'modules/bar/popouts/Bluetooth.qml': SOURCE.parent / 'bluetooth-popover/Bluetooth.qml',
}


def install():
    files = {'services/MenuStyle.qml': (SOURCE / 'MenuStyle.qml').read_text(),
             'components/MenuText.qml': (SOURCE / 'MenuText.qml').read_text()}
    for name in PANELS:
        text = (SHELL / name).read_text()
        if 'readonly property real bodyPointSize:' not in text:
            raise SystemExit('Zuerst den aktuellen Proportions-Patch installieren: ' + name)
        text = text.replace('StyledText {', 'MenuText {')
        text = text.replace('Tokens.font.body.medium.pointSize * root.fontScale * 0.84', 'MenuStyle.bodyPointSize(root.fontScale)')
        text = re.sub(r'readonly property color muted: Qt.alpha\([^\n]+\)', 'readonly property color muted: MenuStyle.muted', text)
        text = re.sub(r'readonly property color rule: Qt.alpha\([^\n]+\)', 'readonly property color rule: MenuStyle.rule', text)
        text = text.replace('readonly property color accent: "#287dff"', 'readonly property color accent: MenuStyle.accent')
        text = text.replace('Qt.alpha(Colours.palette.m3onSurface, Colours.light ? 0.025 : 0.035)', 'MenuStyle.cardFill')
        if name.endswith('WirelessPassword.qml'):
            text = text.replace('TextButton {\n', 'TextButton {\n                    font.family: MenuStyle.fontFamily\n') if 'font.family: MenuStyle.fontFamily' not in text else text
        files[name] = text
    name = 'modules/bar/popouts/ClipWrapper.qml'
    text = (SHELL / name).read_text()
    text = re.sub(r'        color: \[[^\n]+includes\(content.currentName\)[^\n]+', '        color: MenuStyle.surface', text)
    text = re.sub(r'        border.color: \[[^\n]+includes\(content.currentName\)[^\n]+', '        border.color: MenuStyle.border', text)
    files[name] = text
    name = 'modules/launcher/Content.qml'
    text = (SHELL / name).read_text().replace('color: Colours.light ? "#e6f4f5f7" : "#d911161d"', 'color: MenuStyle.surface').replace('border.color: Colours.light ? "#70969ca5" : "#38ffffff"', 'border.color: MenuStyle.border')
    # The search field shares the system family; its size and field geometry stay intact.
    text = text.replace('id: search\n', 'id: search\n            font.family: MenuStyle.fontFamily\n') if 'font.family: MenuStyle.fontFamily' not in text else text
    files[name] = text
    name = 'modules/launcher/StartHome.qml'
    text = (SHELL / name).read_text()
    for role in ('ink','muted'):
        text = re.sub(r'readonly property color ' + role + r': Colours.light[^\n]+', 'readonly property color '+role+': MenuStyle.'+role, text)
    text = re.sub(r'readonly property color line: Colours.light[^\n]+', 'readonly property color line: MenuStyle.rule', text)
    for size,role in [(16,'bodyPixels'),(15,'listPixels'),(13,'secondaryPixels'),(12,'captionPixels')]:
        text = re.sub(r'font.pixelSize: '+str(size)+r'\b', 'font.pixelSize: MenuStyle.'+role, text)
    text = text.replace('color: Colours.light ? "#0a000000" : "#09ffffff"', 'color: MenuStyle.cardFill')
    files[name] = text
    from taskbar_glass import configure
    configure(files, SHELL)
    changed = {name: value for name,value in files.items() if not (SHELL/name).exists() or (SHELL/name).read_text() != value}
    if not changed:
        print('Gemeinsamer Menüstil ist bereits installiert.'); return
    backup = Path.home()/'.local/state/ralleur-taskbar-backups'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-menu-style')
    backup.mkdir(parents=True)
    patch=[]; created=[]
    for name,value in changed.items():
        target=SHELL/name; old=target.read_text() if target.exists() else ''
        if target.exists():
            saved=backup/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
        else: created.append(name)
        patch.extend(difflib.unified_diff(old.splitlines(True),value.splitlines(True),fromfile=name if old else '/dev/null',tofile=name))
    (backup/'created.json').write_text(json.dumps(created,indent=2)+'\n')
    for name,value in changed.items(): (SHELL/name).write_text(value)
    for name,source in PANELS.items(): source.write_text(files[name])
    launcher=REPO/'kde-customizations/launcher/overlay/modules/launcher'
    for name in ('Content.qml','StartHome.qml'): (launcher/name).write_text(files['modules/launcher/'+name])
    (SOURCE.parent/'menu-style.patch').write_text(''.join(patch))
    (SOURCE.parent/'evidence/menu-style-backup.txt').write_text(str(backup)+'\n')
    print(backup)


if __name__ == '__main__': install()
