#!/usr/bin/env python3
"""Live check of KWin's desktop cap, fullscreen behavior and colored indicators."""
from pathlib import Path
import json, os, subprocess, sys, tempfile, time
from PIL import Image
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'kde-customizations/fullscreen-desktops/tests'))
from kwin import report

def state():
    return report('const result={current:workspace.currentDesktop.id,desktops:workspace.desktops.map(d=>d.id)};')
original=state()
assert 1 <= len(original['desktops']) <= 8
checks=[]
import xml.etree.ElementTree as ET
for name,color in [('play','#2563C9'),('everyday','#E56D2F'),('idea','#278F8B'),('weight','#8F5B40')]:
    live=Path.home()/'.config/quickshell/caelestia/modules/bar/components/workspaces/flausen-shapes'/(name+'.svg')
    assert ET.parse(live).getroot().find('{http://www.w3.org/2000/svg}path').get('fill')==color
checks.append('Installed SVGs retain the four exact brand fills; screenshot tolerance allows thin-edge antialiasing')
original_ids = json.dumps(original['desktops'])
try:
    expanded = report('for (let i = workspace.desktops.length; i < 8; ++i) workspace.createDesktop(i, "Flausen cap verification"); const result=workspace.desktops.map(d=>d.id);')
    assert len(expanded) == 8
    created = report('workspace.createDesktop(8,"Flausen overflow verification"); const result=workspace.desktops.map(d=>d.id);')
    assert created == expanded
    checks.append('Attempt to create desktop 9 rejected; all eight IDs unchanged')
finally:
    report('const original=' + original_ids + '; for (const d of workspace.desktops.slice().reverse()) if (!original.includes(d.id)) workspace.removeDesktop(d); const result=true;')
process=None
try:
    with tempfile.TemporaryDirectory() as d:
        qml=Path(d)/'fullscreen.qml'
        qml.write_text('import QtQuick\nimport QtQuick.Window\nWindow {visible:true;width:480;height:320;title:"Flausen desktop cap verification";color:"#17191D"}')
        process=subprocess.Popen(['/usr/lib/qt6/bin/qml',str(qml)],env={**os.environ,'QT_QPA_PLATFORM':'wayland'},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(50):
            found=report('const w=workspace.windowList().find(w=>w.caption==="Flausen desktop cap verification");if(w)w.fullScreen=true;const result=!!w;')
            if found:break
            time.sleep(.1)
        assert found
        time.sleep(.4)
        assert state()['desktops']==original['desktops']
        checks.append('Real Wayland window enters fullscreen without creating a desktop')
        process.terminate();process.wait(timeout=5);process=None
    if len(original['desktops']) == 4:
        for index,id in enumerate(original['desktops'],1):
            subprocess.run(['qdbus6','org.kde.KWin','/KWin','org.kde.KWin.setCurrentDesktop',str(index)],check=True,capture_output=True)
            time.sleep(.35)
            subprocess.run(['spectacle','-b','-n','-f','-o','/tmp/flausen-colored-check.png'],check=True,capture_output=True)
            image=Image.open('/tmp/flausen-colored-check.png').convert('RGB').crop((0,0,520,90))
            pixels=list(image.get_flattened_data())
            for color in [(37,99,201),(229,109,47),(39,143,139),(143,91,64)]:
                assert any(max(abs(a-b) for a,b in zip(pixel,color))<=28 for pixel in pixels),(index,color)
            image.save(HERE/f'colored-desktop-{index}.jpg',quality=94)
        checks.append('Four concept colors present on each of the four active-desktop states')
finally:
    if process:process.terminate();process.wait(timeout=5)
    report('workspace.currentDesktop=workspace.desktops.find(d=>d.id==='+json.dumps(original['current'])+');const result=true;')
assert state()['desktops']==original['desktops']
(HERE/'color-limit-check.json').write_text(json.dumps({'checks':checks,'desktopCount':len(original['desktops']),'restoredOriginalDesktop':True},indent=2)+'\n')
print(json.dumps(checks,indent=2))
