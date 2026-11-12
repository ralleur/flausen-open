pragma Singleton

import QtQuick
import Quickshell
import Quickshell.Wayland
import Caelestia.Config
import qs.components
import qs.services
import qs.utils
import qs.modules.nexus
import "flausen"

Singleton {
    id: root

    property var openWindow: null

    function create(parent: Item, props: var): var {
        props = props || {};
        if (root.openWindow) {
            const win = root.openWindow;
            if (props.initialPageIdx !== undefined)
                win.nexus.nState.goToSubPage(props.initialPageIdx, props.initialSubPageIdx ?? -1);
            win.minimized = false;
            win.visible = true;
            win.raise();
            Logger.mark("nexus=reused");
            return win;
        }
        const win = nexusComp.createObject(parent ?? dummy, props);
        root.openWindow = win;
        Logger.mark("nexus=created");
        return win;
    }

    function close(): void {
        if (root.openWindow)
            root.openWindow.nexus.nState.requestExit();
    }

    QtObject {
        id: dummy
    }

    Component {
        id: nexusComp

        FloatingWindow {
            id: win
            Tokens.screen: screen?.name ?? ""

            property alias nexus: nexus

            property int initialPageIdx: 0
            property int initialSubPageIdx: -1

            function raise(): void {
                const pageTitles = PageRegistry.pages.map(p => p.label);
                const target = Kwin.windowList.find(w => w.title === win.title || (pageTitles.includes(w.title) && w.class && w.class.includes("quickshell")));
                if (target?.address)
                    Kwin.focusWindow(target.address);
            }

            Component.onDestruction: {
                Logger.mark("nexus=destroyed");
                if (root.openWindow === win)
                    root.openWindow = null;
            }

            color: "transparent"

            surfaceFormat.opaque: false

            BackgroundEffect.blurRegion: Region {
                Region { x: -10; y: -10; width: 1; height: 1 }
                Region { item: (GlobalConfig.appearance.transparency.enabled && GlobalConfig.appearance.blur) ? nexus : null; radius: nexus.frameRadius }
            }

            onVisibleChanged: {
                if (!visible)
                    destroy();
            }

            implicitWidth: nexus.implicitWidth
            implicitHeight: nexus.implicitHeight

            minimumSize.width: Tokens.sizes.nexus.minWidth
            minimumSize.height: Tokens.sizes.nexus.minHeight

            contentItem.Config.screen: screen.name
            contentItem.Tokens.screen: screen.name

            title: qsTranslate("Flausen", "flausen Settings · ") + (nexus.nState.systemModule ? nexus.nState.systemTitle : PageRegistry.pages[nexus.nState.currentPageIdx].label)

            Nexus {
                id: nexus

                anchors.fill: parent
                initialPageIdx: win.initialPageIdx
                initialSubPageIdx: win.initialSubPageIdx
                nState.screen: win.screen
                nState.isWindow: true
                windowMaximized: win.maximized
                onMinimizeRequested: win.minimized = true
                onMaximizeRequested: win.maximized = !win.maximized
                onMoveRequested: win.startSystemMove()
                onClose: win.destroy()
            }

            // Frameless windows retain native compositor resize interactions.
            Repeater {
                model: [Qt.TopEdge, Qt.BottomEdge, Qt.LeftEdge, Qt.RightEdge,
                    Qt.TopEdge | Qt.LeftEdge, Qt.TopEdge | Qt.RightEdge,
                    Qt.BottomEdge | Qt.LeftEdge, Qt.BottomEdge | Qt.RightEdge]
                MouseArea {
                    required property int modelData
                    readonly property bool atLeft: (modelData & Qt.LeftEdge) !== 0
                    readonly property bool atRight: (modelData & Qt.RightEdge) !== 0
                    readonly property bool atTop: (modelData & Qt.TopEdge) !== 0
                    readonly property bool atBottom: (modelData & Qt.BottomEdge) !== 0
                    readonly property bool corner: (atLeft || atRight) && (atTop || atBottom)
                    z: 20
                    enabled: !win.maximized
                    width: corner ? 8 : (atLeft || atRight) ? 5 : parent.width - 16
                    height: corner ? 8 : (atTop || atBottom) ? 5 : parent.height - 16
                    x: atRight ? parent.width - width : atLeft ? 0 : 8
                    y: atBottom ? parent.height - height : atTop ? 0 : 8
                    cursorShape: corner ? ((atLeft && atTop) || (atRight && atBottom) ? Qt.SizeFDiagCursor : Qt.SizeBDiagCursor)
                        : (atLeft || atRight) ? Qt.SizeHorCursor : Qt.SizeVerCursor
                    onPressed: win.startSystemResize(modelData)
                }
            }

            Behavior on color {
                CAnim {}
            }
        }
    }
}
