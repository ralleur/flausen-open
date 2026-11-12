#!/usr/bin/env python3
"""Install the approved calendar material on bars and bar popovers only."""
from pathlib import Path
from datetime import datetime, timezone
import difflib
import json
import re
import shutil

SOURCE = Path(__file__).resolve().parent
SHELL = Path.home()/'.config/quickshell/caelestia'

BAR_PASSES = '''    // Bar glass uses the same local native passes as the approved calendar.
    TaskbarGlass {
        id: topBarSmoke
        prewarm: true
        suspended: root.hasFullscreen
        screen: root.screen
        active: topBarGlass.visible && !root.hasFullscreen
        geometry: Qt.rect(topBarGlass.x, topBarGlass.y, topBarGlass.width, topBarGlass.height)
        cornerRadius: topBarGlass.radius
        cutout: {
            const button = bar.launcherButton;
            if (!button) return Qt.rect(0, 0, 0, 0);
            for (let item = button; item; item = item.parent) {
                void item.x; void item.y; void item.width; void item.height;
            }
            void topBarGlass.x; void topBarGlass.y;
            const center = button.mapToItem(topBarGlass, button.width / 2, button.height / 2);
            return Qt.rect(center.x - (button.width + 2) / 2, center.y - (button.width + 2) / 2, button.width + 2, button.width + 2);
        }
    }
    TaskbarGlass {
        id: bottomDockSmoke
        prewarm: true
        suspended: root.hasFullscreen
        centered: true
        reserveGeometry: Qt.rect(0, 0, bottomDock.middleZoneSize + bottomDock.thickness * SplitBarSettings.dockMagnificationAmount * 6, bottomDock.height)
        screen: root.screen
        active: bottomDock.visible && !root.hasFullscreen
        geometry: Qt.rect((root.width - bottomDock.footprintWidth) / 2, bottomDock.y, bottomDock.footprintWidth, bottomDock.height)
        cornerRadius: bottomDock.height / 2
    }
    TaskbarGlass {
        id: dropdownSmoke
        screen: root.screen
        prewarm: true
        suspended: root.hasFullscreen
        minimumSize: Qt.size(448, 512)
        readonly property var request: TaskbarGlassState.dropdowns[root.screen.name]
        active: request !== undefined
        geometry: request?.geometry ?? Qt.rect(0, 0, 0, 0)
        reserveGeometry: request?.reserve ?? Qt.rect(0, 0, 0, 0)
        cornerRadius: request?.radius ?? 14
        bottomAnchored: request?.bottomAnchored ?? false
    }
    // Launcher and dashboard share the same prewarmed smoke material/pool policy.
    TaskbarGlass {
        id: launcherSmoke
        screen: root.screen
        prewarm: true
        suspended: root.hasFullscreen
        minimumSize: Qt.size(768, 896)
        active: panels.launcher.visible
        geometry: Qt.rect(panels.launcher.x + panels.leftMargin, panels.launcher.y + panels.topMargin, panels.launcher.width, panels.launcher.height)
        reserveGeometry: Qt.rect(0, 0, panels.launcher.implicitWidth, panels.launcher.implicitHeight)
        cornerRadius: 24
    }
    TaskbarGlass {
        id: dashboardSmoke
        screen: root.screen
        prewarm: true
        suspended: root.hasFullscreen
        minimumSize: Qt.size(1152, 1024)
        centered: true
        active: panels.dashboard.visible
        geometry: Qt.rect(panels.dashboard.x + panels.leftMargin, panels.dashboard.y + panels.topMargin, panels.dashboard.width, panels.dashboard.height)
        reserveGeometry: Qt.rect(0, 0, panels.dashboard.nonAnimWidth, panels.dashboard.nonAnimHeight)
        cornerRadius: panels.dashboard.glassRadius
    }
'''


LAUNCHER_BACKDROP = r'''    // Share Dolphin's fullscreen backdrop; the launcher stays sharp above it.
    function syncLauncherBackdrop(): void {
        if (launcherBackdropSocket.connected) {
            launcherBackdropSocket.write(JSON.stringify({
                owner: "launcher:" + screen.name,
                shown: launcherBackdropActive,
                cutouts: []
            }) + "\n");
            launcherBackdropSocket.flush();
        }
    }
    onLauncherBackdropActiveChanged: syncLauncherBackdrop()
    Socket {
        id: launcherBackdropSocket
        path: Quickshell.env("XDG_RUNTIME_DIR") + "/ralleur-start-backdrop.sock"
        connected: true
        onConnectionStateChanged: {
            if (connected) root.syncLauncherBackdrop();
            else reconnectLauncherBackdrop.restart();
        }
    }
    Timer {
        id: reconnectLauncherBackdrop
        interval: 250
        onTriggered: launcherBackdropSocket.connected = true
    }
'''

def content_window(text):
    # Keep local smoke pools and restore the shared fullscreen background.
    # The helper owns the strength lease and releases disconnected clients.
    begin=text.find('    readonly property string launcherBlurOwner:')
    if begin>=0:
        end=text.index('    property real blurOffsetTop:',begin)
        text=text[:begin]+text[end:]
    if 'id: launcherBackdropSocket' not in text:
        text=text.replace('    property real blurOffsetTop:', LAUNCHER_BACKDROP+'    property real blurOffsetTop:', 1)
    text = text.replace('        id: topBarGlass\n', '        id: topBarGlass\n        smoke: true\n') if '        smoke: true\n' not in text else text
    layer = r'WlrLayershell.layer: (?:\(root.launcherBackdropActive \|\| \(panels.popouts.hasCurrent && panels.popouts.currentName === "clock"\)\)|root.launcherBackdropActive) \?'
    text = re.sub(layer, 'WlrLayershell.layer: (root.launcherBackdropActive || ((topBarGlass.visible || bottomDock.visible) && !root.hasFullscreen) || (panels.popouts.hasCurrent && !panels.popouts.isDetached)) ?', text, count=1)
    anchor='    DrawerVisibilities {\n'
    if text.count(anchor)!=1: raise ValueError('Unerwarteter ContentWindow-Aufbau')
    begin=text.find('    // Bar glass uses the same local native passes')
    if begin>=0:
        text=text[:begin]+text[text.index(anchor,begin):]
    text=text.replace(anchor,BAR_PASSES+anchor)
    text=text.replace('root.launcherBackdropActive || topBarGlass.visible || bottomDock.visible || (panels.popouts.hasCurrent && !panels.popouts.isDetached)', 'root.launcherBackdropActive || ((topBarGlass.visible || bottomDock.visible) && !root.hasFullscreen) || (panels.popouts.hasCurrent && !panels.popouts.isDetached)')
    text=text.replace('root.launcherBackdropActive || ((topBarGlass.visible', 'panels.launcher.visible || panels.dashboard.visible || ((topBarGlass.visible')
    text=text.replace('            target: panels.launcher\n', '            target: null // Dedicated rounded launcher region and pooled smoke.\n')
    text=text.replace('            target: panels.dashboard\n', '            target: null // Dedicated rounded dashboard region and pooled smoke.\n')
    return text


def configure_dock_context(files, shell=SHELL):
    files['modules/bar/popouts/DockContext.qml']=(SOURCE.parent/'overlay/modules/bar/popouts/DockContext.qml').read_text()
    name='modules/bar/popouts/Content.qml'
    text=files.get(name) or (shell/name).read_text()
    # Match Ethernet's typography and menu scale, independently of dock icon size.
    text=text.replace('name: "dockcontext"\n            sourceComponent:', 'name: "dockcontext"\n            previewKey: "network"\n            minScale: 1.15\n            sourceComponent:')
    text=text.replace('name: "dockcontext"\n            previewKey: "dock"\n', 'name: "dockcontext"\n            previewKey: "network"\n            minScale: 1.15\n')
    text=text.replace('name.startsWith("dock") ? BarSettings.SplitBarSettings.dockScale', '(name.startsWith("dock") && name !== "dockcontext") ? BarSettings.SplitBarSettings.dockScale')
    text=text.replace('readonly property real contentMargin: Tokens.padding.large *', 'readonly property real contentMargin: (popouts.currentName === "dockcontext" ? 8 : Tokens.padding.large) *')
    text=text.replace(' + Tokens.padding.extraLargeIncreased * (currentPopout?.item?.scaleOffset ?? 1.0), available', ' + (popouts.currentName === "dockcontext" ? 16 : Tokens.padding.extraLargeIncreased) * (currentPopout?.item?.scaleOffset ?? 1.0), available')
    files[name]=text
    return files


def configure(files, shell=SHELL):
    def read(name):
        return files[name] if name in files else (shell/name).read_text()
    files['services/MenuStyle.qml']=(SOURCE/'MenuStyle.qml').read_text()
    for name in ['TaskbarGlass','TaskbarDropdownGlass','MenuPrimarySurface','PrimaryControlFill']:
        files['components/'+name+'.qml']=(SOURCE/(name+'.qml')).read_text()
    files['services/TaskbarGlassState.qml']=(SOURCE/'TaskbarGlassState.qml').read_text()
    files['modules/bar/GlassSurface.qml']=(SOURCE.parent/'overlay/modules/bar/GlassSurface.qml').read_text()
    configure_dock_context(files, shell)
    files['modules/bar/popouts/CalendarGlass.qml']=(SOURCE.parent/'remaining-overlays/CalendarGlass.qml').read_text()
    name='modules/drawers/ContentWindow.qml';files[name]=content_window(read(name))
    for name in ['modules/launcher/Content.qml','modules/launcher/HermesChat.qml','modules/dashboard/Wrapper.qml']:
        text=read(name).replace('color: MenuStyle.surface','color: MenuStyle.smokeSurface')
        text=text.replace('color: Colours.light ? "#bff8f6f3" : "#a61c2024"','color: MenuStyle.smokeSurface')
        if name.endswith('HermesChat.qml'):
            text=text.replace('color: MenuStyle.smokeSurface','smoke: true')
        if name.endswith('dashboard/Wrapper.qml') and 'readonly property real nonAnimWidth:' not in text:
            text=text.replace('    readonly property real nonAnimHeight:', '    readonly property real nonAnimWidth: (content.item as Content)?.nonAnimWidth ?? 0\n    readonly property real nonAnimHeight:')
        if name.endswith('dashboard/Wrapper.qml') and 'readonly property real glassRadius:' not in text:
            text=text.replace('    readonly property real nonAnimWidth:', '    readonly property real glassRadius: Tokens.rounding.extraLarge\n    readonly property real nonAnimWidth:')
            text=text.replace('radius: Tokens.rounding.extraLarge','radius: root.glassRadius')
        files[name]=text

    name='modules/bar/SplitDock.qml';text=read(name)
    text=text.replace('glass: {type: "nativeBackdrop", darkOpacity: 64 / 255, lightOpacity: 89 / 255}', 'glass: {type: "localNativeBackdrop", opacity: MenuStyle.taskbarSurface.a, additionalLocalPasses: 8}')
    files[name]=text
    name='modules/bar/components/Dock.qml';text=read(name)
    text=text.replace('        GlassSurface {\n            anchors.fill:', '        GlassSurface {\n            smoke: true\n            anchors.fill:')
    files[name]=text
    name='modules/bar/popouts/ClipWrapper.qml';text=read(name)
    text=text.replace('color: content.currentName === "clock" ? MenuStyle.calendarSurface : MenuStyle.surface', 'color: MenuStyle.taskbarSurface')
    text=text.replace('        color: MenuStyle.surface', '        color: MenuStyle.taskbarSurface')
    text=text.replace('// Same glass material and contour as the start menu.', '// Approved calendar smoke; preserve each popover radius.')
    text=text.replace('    Rectangle {\n        anchors.fill: parent', '    Rectangle {\n        id: glassBackground\n        anchors.fill: parent')
    text=re.sub(r'        cornerRadius: \[\"updateIndicator\"[^\n]+', '        cornerRadius: glassBackground.radius', text)
    text=text.replace('    CalendarGlass {\n', '    TaskbarGlass {\n')
    text=text.replace('        target: root\n', '        geometry: Qt.rect(root.x + root.parent.leftMargin, root.y + root.parent.topMargin, root.width, root.height)\n        cornerRadius: glassBackground.radius\n')
    text=text.replace('root.fromFloatingBar && content.currentName === "clock" && content.hasCurrent', 'root.fromFloatingBar && !root.framelessDockPreview && content.hasCurrent')
    if '    TaskbarGlass {' not in text: raise ValueError('Zuerst Kalenderglas installieren')
    text=text.replace('    TaskbarGlass {\n        screen: root.screen', '    TaskbarGlass {\n        id: popoutSmoke\n        screen: root.screen')
    text=re.sub(r'(    TaskbarGlass \{\n        id: popoutSmoke\n).*?(        screen: root.screen\n)', lambda m: m[1]+'''        prewarm: true
        suspended: root.bar.fullscreen
        minimumSize: Qt.size(640, 1024)
        centered: false
        bottomAnchored: root.popoutPosition === "bottom"
        reserveGeometry: Qt.rect(0, 0, content.nonAnimWidth, content.nonAnimHeight)
'''+m[2], text, count=1, flags=re.S)
    files[name]=text
    # Keep card boundaries while removing solid fills that hide the outer glass.
    for component in ['BarComponentContext','DockContext','TrayMenu','Weather','LockStatus','Notifications','Github','Notes']:
        name=f'modules/bar/popouts/{component}.qml';text=read(name)
        if component=='Github':
            text=text.replace('color: Services.Colours.tPalette.m3surfaceContainer', 'color: Services.MenuStyle.cardFill')
        else:
            text=text.replace('color: Colours.tPalette.m3surfaceContainer\n', 'color: MenuStyle.cardFill\n')
        if component=='Notes':
            text=text.replace('color: Colours.tPalette.m3surfaceContainerHigh\n', 'color: MenuStyle.cardFill\n')
        files[name]=text
    name='components/controls/Menu.qml';text=read(name)
    text=text.replace('root.sharedPopoverStyle ? MenuStyle.surface', 'root.sharedPopoverStyle ? MenuStyle.taskbarSurface')
    if '    // Native smoke for taskbar dropdowns only.' not in text:
        anchor='    TransformWatcher {\n'
        if text.count(anchor)!=1: raise ValueError('Unerwarteter Menüaufbau')
        text=text.replace(anchor,'''    // Native smoke for taskbar dropdowns only.
    TaskbarGlass {
        screen: root.QsWindow.window?.screen ?? Quickshell.screens[0]
        active: root.sharedPopoverStyle && root.expanded && root.visible
        geometry: Qt.rect(menu.x, menu.y, menu.width, menu.height)
        cornerRadius: menu.radius
    }

'''+anchor)
    if 'id: taskbarDropdownSource' not in text:
        menu_source=(SOURCE.parent/'capture-clipboard-style/Menu.qml').read_text()
        begin=menu_source.index('        // The dropdown shares a window')
        end=menu_source.index('        StyledRect {\n            // Sideways,',begin)
        text=text.replace('        StyledRect {\n            // Sideways,',menu_source[begin:end]+'        StyledRect {\n            // Sideways,')
    text=text.replace('    TaskbarGlass {\n        screen: root.QsWindow.window', '    TaskbarDropdownGlass {\n        screen: root.QsWindow.window')
    if '        reserveGeometry: Qt.rect(menu.x' not in text:
        text=text.replace('        geometry: Qt.rect(menu.x, menu.y, menu.width, menu.height)\n', '        geometry: Qt.rect(menu.x, menu.y, menu.width, menu.height)\n        reserveGeometry: Qt.rect(menu.x, menu.y, menu.implicitWidth, menu.implicitHeight)\n        bottomAnchored: root.thisSideY === Menu.Bottom\n')
    files[name]=text
    from primary_controls import configure as primary_controls
    primary_controls(files, shell)
    return files


def install(dock_context=False):
    files=configure_dock_context({}) if dock_context else configure({})
    changed={name:value for name,value in files.items() if not (SHELL/name).exists() or (SHELL/name).read_text()!=value}
    if not changed:
        print('Taskbar-Rauchglas ist bereits installiert.');return
    label='dock-context' if dock_context else 'taskbar-smoke'
    backup=Path.home()/'.local/state/ralleur-taskbar-backups'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+label)
    backup.mkdir(parents=True);patch=[];created=[]
    for name,value in changed.items():
        target=SHELL/name;old=target.read_text() if target.exists() else ''
        if target.exists():
            saved=backup/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
        else:created.append(name)
        patch.extend(difflib.unified_diff(old.splitlines(True),value.splitlines(True),fromfile=name if old else '/dev/null',tofile=name))
    (backup/'created.json').write_text(json.dumps(created,indent=2)+'\n')
    for name,value in changed.items():
        target=SHELL/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(value)
    (SOURCE.parent/(label+'.patch')).write_text(''.join(patch))
    (SOURCE.parent/('evidence/'+label+'-backup.txt')).write_text(str(backup)+'\n')
    print(backup)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dock-context', action='store_true', help='Only install the dock app context menu and its margins')
    install(parser.parse_args().dock_context)
