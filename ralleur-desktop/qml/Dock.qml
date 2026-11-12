import QtQuick
import Quickshell

Card {
    id: root
    required property var backend
    required property var shellScreen
    property bool compact: false
    property var apps: AppCatalog.apps
    radius: Theme.geo.dockRadius ?? 20
    Column {
        x: (parent.width - width) / 2
        y: 16
        spacing: root.compact ? 5 : 12
        ShellButton {
            text: "⠿"
            hint: "Apps suchen · Super+Leertaste"
            onClicked: root.backend.drawer(root.shellScreen, "launcher")
        }
        ShellButton {
            text: "⌂"
            hint: "Home"
            onClicked: root.backend.launch({
                id: "home",
                classes: ["dolphin", "thunar", "nemo"]
            })
        }
        Repeater {
            model: root.height < 480 ? root.apps.filter(a => ["browser", "terminal", "files"].includes(a.id)) : root.apps
            Item {
                required property var modelData
                width: 36
                height: 36
                ShellButton {
                    anchors.fill: parent
                    iconName: parent.modelData.icon
                    hint: parent.modelData.name
                    onClicked: root.backend.launch(parent.modelData)
                }
                Rectangle {
                    x: -5
                    anchors.verticalCenter: parent.verticalCenter
                    width: 3
                    height: 13
                    radius: 2
                    color: Theme.colors.focus
                    visible: root.backend.running(parent.modelData)
                }
            }
        }
    }
    Column {
        anchors {
            bottom: parent.bottom
            horizontalCenter: parent.horizontalCenter
            bottomMargin: 12
        }
        spacing: 5
        ShellButton {
            text: "◐"
            hint: "Light / Dark wechseln · Super+Shift+T"
            onClicked: Theme.toggle()
        }
        ShellButton {
            text: "⚙"
            hint: "Caelestia-Einstellungen"
            onClicked: root.backend.drawer(root.shellScreen, "settings")
        }
        ShellButton {
            text: "⏻"
            hint: "Sitzung / Sperren"
            onClicked: root.backend.drawer(root.shellScreen, "session")
        }
    }
}
