#!/usr/bin/env python3
"""Apply QML-only presentation changes to clean Plasma Login Manager v6.8.2."""
from pathlib import Path
import argparse
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent

def fields(source, root):
    field = f'''\n            Layout.preferredHeight: 48
            color: {root}.ink
            placeholderTextColor: {root}.muted
            background: RalleurFieldBackground {{ dark: {root}.dark; showLock: true }}\n'''
    source = source.replace('id: passwordBox\n', 'id: passwordBox\n            objectName: "ralleurPassword"\n            leftPadding: 44\n' + field)
    source = source.replace('id: userNameInput\n', 'id: userNameInput\n' + field)
    return source.replace('id: loginButton\n', f'''id: loginButton
            icon.width: 18
            icon.height: 18
            icon.color: {root}.ink
            background: RalleurFieldBackground {{ dark: {root}.dark; radius: width / 2 }}
''')

def prepare(source):
    version = subprocess.check_output(['git', '-C', str(source), 'describe', '--tags', '--exact-match', 'HEAD'], text=True).strip()
    if version != 'v6.8.2': raise SystemExit('Use the installed version tag v6.8.2.')
    qml = source / 'src/frontend/greeter/qml'
    if 'RalleurSessionScreen' in (qml / 'Login.qml').read_text():
        raise SystemExit('Already patched; start from clean v6.8.2 sources.')
    for item in (ROOT / 'shared').iterdir():
        shutil.copy2(item, qml / item.name)
    login = (qml / 'Login.qml').read_text().replace('SessionManagementScreen {', 'RalleurSessionScreen {')
    login = login.replace('id: root\n', 'id: root\n    objectName: "ralleurLogin"\n')
    (qml / 'Login.qml').write_text(fields(login, 'root'))
    main = (qml / 'Main.qml').read_text().replace('visible: y > 0 && Settings.showClock', 'visible: false')
    main = main.replace('height: root.height + Kirigami.Units.gridUnit * 3', 'height: root.height')
    main = main.replace('opacity: loginScreenRoot.uiVisible ? 1 : 0', 'opacity: 1')
    main = main.replace('id: root\n', 'id: root\n    objectName: "ralleurLoginRoot"\n    property alias wallpaperContainer: loginWallpaper\n')
    main = main.replace('    // If we\'re using software rendering', '    Item { id: loginWallpaper; anchors.fill: parent; z: -100 }\n\n    // If we\'re using software rendering')
    main = main.replace('id: userListComponent\n', 'id: userListComponent\n                backdrop: loginWallpaper.children.length ? loginWallpaper : null\n                bottomInset: footer.height + 24\n')
    main = main.replace('showUsernamePrompt: true\n', 'showUsernamePrompt: true\n                backdrop: loginWallpaper.children.length ? loginWallpaper : null\n                bottomInset: footer.height + 24\n')
    (qml / 'Main.qml').write_text(main)
    cpp = qml.parent / 'main.cpp'
    native = cpp.read_text().replace('#include "plasmaloginsettings.h"', '#include "plasmaloginsettings.h"\n#include "loginwallpaper.h"')
    native = native.replace('        window->show();', '        loadRalleurLoginWallpaper(window);\n        window->show();')
    cpp.write_text(native)
    shutil.copy2(ROOT / 'login/loginwallpaper.h', qml.parent / 'loginwallpaper.h')
    cmake = qml.parent / 'CMakeLists.txt'
    text = cmake.read_text().replace('qml/Login.qml', 'qml/Login.qml\n    qml/RalleurSessionScreen.qml\n    qml/AccountAvatar.qml\n    qml/RalleurFieldBackground.qml')
    text = text.replace('qml/faces/.face.icon', 'qml/faces/.face.icon\n    qml/ralleur-symbol.svg')
    text = text.replace('qml/ralleur-symbol.svg', 'qml/ralleur-symbol.svg\n    qml/FlausenBrand.js\n    qml/flausen-symbol-transparent.svg\n    qml/flausen-lockup-on-dark.svg\n    qml/flausen-lockup-on-light.svg')
    cmake.write_text(text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    prepare(parser.parse_args().source)
