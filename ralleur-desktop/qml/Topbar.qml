import QtQuick
import Quickshell

Item {
    id: root
    required property var backend
    required property var shellScreen
    property int layoutHeight: shellScreen?.height ?? 0
    property bool compact: width < Theme.geo.compactBreakpoint
    readonly property var workspaceIds: backend.activeWorkspace >= 1 && backend.activeWorkspace <= 4 ? [1, 2, 3, 4] : [1, 2, 3, backend.activeWorkspace]
    implicitHeight: Theme.geo.top
    SystemClock {
        id: clock
        precision: SystemClock.Minutes
    }
    ShellButton {
        id: brand
        x: 1
        height: parent.height
        width: Theme.geo.dock - 2
        hint: "Ralleur · Launcher"
        contentItem: Image {
            source: Theme.base + "/assets/brand/ralleur-symbol.svg"
            fillMode: Image.PreserveAspectFit
            sourceSize: Qt.size(26, 30)
            anchors.centerIn: parent
            width: 26
            height: 30
        }
        onClicked: root.backend.drawer(root.shellScreen, "launcher")
    }
    Card {
        id: spaces
        x: Theme.geo.dock + 6
        width: 128
        height: parent.height
        radius: Theme.geo.barRadius ?? 17
        Row {
            anchors.centerIn: parent
            Repeater {
                model: root.workspaceIds
                ShellButton {
                    required property int modelData
                    width: 29
                    height: 26
                    text: modelData > 0 ? String(modelData) : "•"
                    hint: modelData > 0 ? "Arbeitsfläche " + modelData : "Aktuelle benannte Arbeitsfläche"
                    selected: root.backend.activeWorkspace === modelData
                    onClicked: if (modelData > 0)
                        root.backend.workspace(modelData)
                }
            }
        }
    }
    Card {
        x: spaces.x + spaces.width + 8
        width: parent.width - x
        height: parent.height
        radius: Theme.geo.barRadius ?? 17
        ShellText {
            x: 16
            anchors.verticalCenter: parent.verticalCenter
            width: Math.max(0, parent.width * 0.32 - 20)
            text: root.backend.activeTitle
            visible: !root.compact
            font.pixelSize: 11
        }
        ShellText {
            x: root.width / 2 - parent.x - width / 2
            anchors.verticalCenter: parent.verticalCenter
            text: Qt.formatDateTime(clock.date, root.compact ? "HH:mm" : "ddd, d. MMM   HH:mm")
            font.pixelSize: 11
        }
        Status {
            anchors.right: parent.right
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            backend: root.backend
            shellScreen: root.shellScreen
            desktopWidth: root.width + 2 * Theme.geo.edge
            desktopHeight: root.layoutHeight
        }
    }
}
