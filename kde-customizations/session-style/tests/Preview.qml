import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import org.kde.plasma.components as PC
import "../shared"
Window {
    id: window
    width: 1280; height: 800; visible: true
    title: "Ralleur · Sperrbildschirm-Vorschau"
    property bool light: Qt.application.arguments.indexOf("--light") >= 0
    Image { id: previewWallpaper; anchors.fill: parent; source: window.light ? "file:///home/USER/ralleurOS/ralleur-desktop/assets/wallpapers/ralleur-light.png" : "file:///home/USER/ralleurOS/ralleur-desktop/assets/wallpapers/ralleur-dark.png"; fillMode: Image.PreserveAspectCrop }
    RalleurSessionScreen {
        backdrop: previewWallpaper
        anchors.fill: parent
        mode: window.light ? "light" : "dark"
        userListModel: ListModel { ListElement { name: "ralleur"; realName: "ralleur"; icon: "" } }
        RowLayout {
            Layout.fillWidth: true
            PC.TextField {
                echoMode: TextInput.Password
                Layout.fillWidth: true; Layout.preferredHeight: 48
                placeholderText: "Passwort eingeben"
                background: RalleurFieldBackground { dark: !window.light }
            }
            PC.Button { text: "→"; Layout.preferredWidth: 48; Layout.preferredHeight: 48; background: RalleurFieldBackground { dark: !window.light } }
        }
    }
    Timer {
        interval: 600; running: true
        onTriggered: window.contentItem.grabToImage(function(result) { result.saveToFile(window.light ? "/home/USER/ralleurOS/.cache/lock-light.png" : "/home/USER/ralleurOS/.cache/lock-dark.png"); Qt.quit() })
    }
}
