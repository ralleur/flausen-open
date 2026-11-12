import QtQuick
import Quickshell
import Quickshell.Services.Pipewire
import Quickshell.Services.UPower
import Quickshell.Networking
import Quickshell.Services.SystemTray

Row {
    id: root
    required property var backend
    required property var shellScreen
    required property int desktopWidth
    required property int desktopHeight
    spacing: 6
    PwObjectTracker {
        objects: [Pipewire.defaultAudioSink]
    }
    ShellButton {
        width: 28
        height: 28
        text: Pipewire.defaultAudioSink?.audio?.muted ? "⊘" : "♪"
        hint: "Audio · Klick für Stumm / Ton"
        enabled: !!Pipewire.defaultAudioSink?.audio
        onClicked: Pipewire.defaultAudioSink.audio.muted = !Pipewire.defaultAudioSink.audio.muted
    }
    ShellButton {
        width: 28
        height: 28
        text: Networking.wifiEnabled ? "⌁" : "⇄"
        hint: "Netzwerk / Schnelleinstellungen"
        onClicked: root.backend.drawer(root.shellScreen, "sidebar")
    }
    Repeater {
        model: SystemTray.items
        ShellButton {
            id: trayButton
            required property var modelData
            width: 26
            height: 28
            iconName: ""
            hint: modelData.tooltipTitle || modelData.id
            function showMenu(): void {
                if (!modelData.hasMenu)
                    return;
                const point = mapToItem(null, 0, height);
                modelData.display(QsWindow.window, point.x, point.y);
            }
            contentItem: Item {
                Image {
                    id: trayPicture
                    anchors.fill: parent
                    source: {
                        const url = trayButton.modelData.icon.toString();
                        return url.startsWith("image://icon/") ? Theme.icon(decodeURIComponent(url.slice(13).split("?")[0])) : url;
                    }
                    sourceSize: Qt.size(24, 24)
                    fillMode: Image.PreserveAspectFit
                    visible: source.toString().length > 0 && status === Image.Ready
                }
                ShellText {
                    anchors.centerIn: parent
                    text: "•"
                    visible: !trayPicture.visible
                }
            }
            onClicked: modelData.onlyMenu ? showMenu() : modelData.activate()
            TapHandler {
                acceptedButtons: Qt.RightButton
                onTapped: trayButton.showMenu()
            }
        }
    }
    ShellText {
        anchors.verticalCenter: parent.verticalCenter
        visible: UPower.displayDevice.isLaptopBattery
        text: (UPower.onBattery ? "▱ " : "⚡ ") + Math.round(UPower.displayDevice.percentage * 100) + "%"
        font.pixelSize: 11
    }
    ShellButton {
        width: 28
        height: 28
        text: "◫"
        hint: "Widgets ein-/ausblenden · Super+W"
        onClicked: ShellUi.toggle(root.desktopWidth, root.desktopHeight)
    }
}
