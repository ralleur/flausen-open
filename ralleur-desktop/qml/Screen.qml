import QtQuick
import Quickshell
import Quickshell.Wayland

Scope {
    id: root
    required property ShellScreen modelData
    required property var backend
    readonly property bool fullscreen: backend.fullscreen(modelData)
    readonly property bool wide: modelData.width >= Theme.geo.widgetBreakpoint && modelData.height >= Theme.geo.widgetMinHeight
    PanelWindow {
        screen: root.modelData
        anchors {
            top: true
            bottom: true
            left: true
            right: true
        }
        WlrLayershell.namespace: "ralleur-background"
        WlrLayershell.layer: WlrLayer.Background
        exclusionMode: ExclusionMode.Ignore
        color: Theme.colors.background
        mask: Region {}
        Image {
            anchors.fill: parent
            source: Theme.base + "/assets/wallpapers/ralleur-" + Theme.mode + ".svg"
            fillMode: Image.PreserveAspectCrop
            sourceSize: Qt.size(width, height)
        }
    }
    PanelWindow {
        id: top
        screen: root.modelData
        visible: !root.fullscreen
        anchors {
            top: true
            left: true
            right: true
        }
        implicitHeight: Theme.geo.top + 2 * Theme.geo.edge
        exclusionMode: ExclusionMode.Ignore
        WlrLayershell.namespace: "ralleur-top"
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.OnDemand
        color: "transparent"
        Topbar {
            x: Theme.geo.edge
            y: Theme.geo.edge
            width: parent.width - 2 * x
            backend: root.backend
            shellScreen: root.modelData
        }
    }
    PanelWindow {
        screen: root.modelData
        visible: !root.fullscreen
        anchors {
            left: true
            top: true
            bottom: true
        }
        margins.top: top.implicitHeight + Theme.geo.edge
        margins.bottom: Theme.geo.edge * 3
        implicitWidth: (root.modelData.width < Theme.geo.compactBreakpoint ? 46 : Theme.geo.dock) + Theme.geo.edge * 2
        exclusionMode: ExclusionMode.Ignore
        WlrLayershell.namespace: "ralleur-dock"
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.OnDemand
        color: "transparent"
        Dock {
            x: Theme.geo.edge
            width: parent.width - x * 2
            height: parent.height
            backend: root.backend
            shellScreen: root.modelData
            compact: root.modelData.width < Theme.geo.compactBreakpoint
        }
    }
    PanelWindow {
        id: widgets
        screen: root.modelData
        visible: !root.fullscreen && (root.wide ? ShellUi.widgets : ShellUi.sidebar)
        anchors {
            right: true
            top: true
        }
        margins {
            top: Theme.geo.top + Theme.geo.edge * 3 + 4
            right: Theme.geo.edge * 2.6
        }
        implicitWidth: Math.max(220, Math.min(Theme.geo.widget, root.modelData.width * 0.158))
        implicitHeight: content.height
        // A visible column reserves its space. On compact screens the shortcut
        // opens a temporary sidebar and closes it again without moving windows.
        exclusionMode: ExclusionMode.Ignore
        WlrLayershell.namespace: "ralleur-widgets"
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.OnDemand
        color: "transparent"
        Column {
            id: content
            width: parent.width
            spacing: Theme.geo.gap
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
    PanelWindow {
        screen: root.modelData
        visible: !root.fullscreen
        anchors {
            top: true
            left: true
            right: true
        }
        implicitHeight: 1
        exclusiveZone: Theme.geo.top + Theme.geo.edge * 2
        color: "transparent"
        mask: Region {}
        WlrLayershell.namespace: "ralleur-top-reservation"
    }
    PanelWindow {
        screen: root.modelData
        visible: !root.fullscreen
        anchors {
            left: true
            top: true
            bottom: true
        }
        implicitWidth: 1
        exclusiveZone: (root.modelData.width < Theme.geo.compactBreakpoint ? 46 : Theme.geo.dock) + Theme.geo.edge * 2
        color: "transparent"
        mask: Region {}
        WlrLayershell.namespace: "ralleur-dock-reservation"
    }
    PanelWindow {
        screen: root.modelData
        visible: !root.fullscreen && root.wide && ShellUi.widgets
        anchors {
            right: true
            top: true
            bottom: true
        }
        implicitWidth: 1
        exclusiveZone: widgets.implicitWidth + Theme.geo.edge * 4
        color: "transparent"
        mask: Region {}
        WlrLayershell.namespace: "ralleur-widget-reservation"
    }
}
