#!/usr/bin/env python3
"""Apply the Capture primary material to shared blue controls, preserving input."""
from pathlib import Path
from datetime import datetime, timezone
import json, shutil, difflib
SOURCE=Path(__file__).resolve().parent
SHELL=Path.home()/'.config/quickshell/caelestia'
# Exact, reviewed upstream anchors; do not vendor a second copy of shell controls.
RULES={
 'modules/bar/popouts/Network.qml': [('                        color: wifiSwitch.checked ? root.accent : Qt.alpha(Colours.palette.m3onSurface, 0.22)\n',1)],
 'modules/bar/popouts/Bluetooth.qml': [('                        color: powerSwitch.checked ? root.accent : Qt.alpha(Colours.palette.m3onSurface, 0.22)\n',1)],
 'modules/bar/popouts/Battery.qml': [('                    id: indicator\n',1)],
 'modules/bar/popouts/Updates.qml': [('            id: updateButton\n',1)],
 'modules/bar/popouts/CalendarPopout.qml': [('                        color: MenuStyle.accent\n',1)],
 'modules/bar/popouts/MenuScreenshotList.qml': [('                    color: MenuStyle.accent\n',1)],
 'components/controls/ButtonBase.qml': [('    id: root\n',1)],
 'components/controls/ToggleButton.qml': [('    id: root\n',1)],
 'components/controls/StyledSwitch.qml': [('    indicator: StyledRect {\n',1)],
 'components/controls/StyledRadioButton.qml': [('            color: !root.enabled ? Colours.disabledContent : root.checked ? Colours.palette.m3primary : "transparent"\n',1)],
 'components/controls/SplitButton.qml': [('        color: root.disabled ? Colours.disabledContainer : root.colour\n',2)],
}
def decorate(text, rules):
    if '// Capture primary material' in text:
        if text.count('// Capture primary material')!=sum(count for _,count in rules):
            raise ValueError('Incomplete primary material patch; preserve local edits')
        return text
    for anchor,count in rules:
        if text.count(anchor)!=count:raise ValueError('Unsupported control layout: '+anchor.strip())
        indent=anchor[:len(anchor)-len(anchor.lstrip())]
        # After the opening/root id, before existing label/interaction children.
        addition=indent+('    ' if anchor.rstrip().endswith('{') else '')+'PrimaryControlFill {} // Capture primary material\n'
        text=text.replace(anchor,anchor+addition)
    return text

def configure(files, shell=SHELL):
    for name,rules in RULES.items():
        text=files.get(name,(shell/name).read_text())
        if 'import qs.components\n' not in text:text=text.replace('import QtQuick\n','import QtQuick\nimport qs.components\n',1)
        files[name]=decorate(text,rules)
    name='modules/launcher/HermesChat.qml'
    text=files.get(name,(shell/name).read_text())
    for anchor in [
        'background: Rectangle { radius: 9; color: root.accent; opacity: allowButton.enabled ? 1 : 0.5',
        'background: Rectangle { radius: 11; color: sendButton.enabled ? root.accent : Qt.alpha(root.foreground, 0.07); opacity: sendButton.hovered ? 0.85 : 1',
    ]:
        if text.count(anchor)!=1:raise ValueError('Unsupported Hermes action')
        if anchor+' }' in text:text=text.replace(anchor+' }',anchor+'; PrimaryControlFill {} }')
    files[name]=text
    for name in ['MenuPrimarySurface','PrimaryControlFill']:
        files['components/'+name+'.qml']=(SOURCE/(name+'.qml')).read_text()
    files['services/MenuStyle.qml']=(SOURCE/'MenuStyle.qml').read_text()
    return files

def install():
    files=configure({})
    changed={n:t for n,t in files.items() if not (SHELL/n).exists() or (SHELL/n).read_text()!=t}
    if not changed:print('Blue controls already use the Capture material.');return
    backup=Path.home()/'.local/state/ralleur-taskbar-backups'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-primary-controls')
    backup.mkdir(parents=True);created=[];patch=[]
    for name,text in changed.items():
        target=SHELL/name;old=target.read_text() if target.exists() else ''
        if target.exists():
            saved=backup/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
        else:created.append(name)
        patch.extend(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile=name if old else '/dev/null',tofile=name))
    (backup/'created.json').write_text(json.dumps(created,indent=2)+'\n')
    for name,text in changed.items():(SHELL/name).write_text(text)
    (SOURCE.parent/'primary-controls.patch').write_text(''.join(patch))
    (SOURCE.parent/'evidence/primary-controls-backup.txt').write_text(str(backup)+'\n')
    print(backup)
if __name__=='__main__':install()
