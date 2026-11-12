import QtQuick

Item {
    id: root
    required property var backend
    required property var shellScreen
    property bool chrome: true
    property bool showWallpaper: true
    readonly property bool wide: width >= Theme.geo.widgetBreakpoint && height >= Theme.geo.widgetMinHeight
    readonly property bool compact: width < Theme.geo.compactBreakpoint
    Image {
        visible: root.showWallpaper
        anchors.fill: parent
        source: Theme.base + "/assets/wallpapers/ralleur-" + Theme.mode + ".svg"
        fillMode: Image.PreserveAspectCrop
        sourceSize: Qt.size(root.width, root.height)
    }
    Topbar {
        id: top
        x: Theme.geo.edge
        y: Theme.geo.edge
        width: parent.width - x * 2
        backend: root.backend
        shellScreen: root.shellScreen
        layoutHeight: root.height
        visible: root.chrome
    }
    Dock {
        id: dock
        x: Theme.geo.edge
        y: Theme.geo.top + Theme.geo.edge * 3
        width: root.compact ? 46 : Theme.geo.dock
        height: parent.height - y - Theme.geo.edge * 3
        backend: root.backend
        shellScreen: root.shellScreen
        compact: root.compact
        visible: root.chrome
    }
    Column {
        id: widgets
        x: root.width - width - Theme.geo.edge * 2.6
        y: dock.y + 4
        width: Math.max(220, Math.min(Theme.geo.widget, root.width * 0.158))
        spacing: Theme.geo.gap
        visible: root.chrome && (root.wide ? ShellUi.widgets : ShellUi.sidebar)
        ClockCard {
            width: parent.width
        }
        MediaCard {
            width: parent.width
            player: root.backend.player
        }
        MetricsCard {
            width: parent.width
        }
        ShellButton {
            anchors.right: parent.right
            text: "×"
            hint: "Widgets schließen"
            visible: !root.wide
            onClicked: ShellUi.sidebar = false
        }
    }
}
