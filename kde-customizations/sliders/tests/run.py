#!/usr/bin/env python3
"""Run native slider tests with the real shared primary material and a theme fixture."""
from pathlib import Path
import os,subprocess,tempfile
HERE=Path(__file__).resolve().parent
STYLE=HERE.parents[1]/'taskbar/menu-style'
with tempfile.TemporaryDirectory(prefix='flausen-control-tests-') as folder:
    imports=Path(folder)
    components=imports/'qs/components';components.mkdir(parents=True)
    names=['MenuPrimarySurface','PrimaryControlFill']
    for name in names:(components/(name+'.qml')).symlink_to(STYLE/(name+'.qml'))
    (components/'qmldir').write_text('module qs.components\n'+''.join(f'{n} 1.0 {n}.qml\n' for n in names))
    services=imports/'qs/services';services.mkdir(parents=True)
    (services/'MenuStyle.qml').symlink_to(STYLE/'MenuStyle.qml')
    (services/'Colours.qml').write_text('pragma Singleton\nimport QtQuick\nQtObject { property bool light: false }\n')
    (services/'qmldir').write_text('module qs.services\nsingleton MenuStyle 1.0 MenuStyle.qml\nsingleton Colours 1.0 Colours.qml\n')
    result=subprocess.run(['/usr/lib/qt6/bin/qmltestrunner','-import',str(imports),'-input',str(HERE)],env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software'))
    raise SystemExit(result.returncode)
