import QtQuick
import QtQuick.Layouts
import qs.services

Rectangle {
    implicitHeight: content.implicitHeight + 24
    color: "#19ef4444"
    border.width: 1
    border.color: "#88ef4444"
    radius: 12
    RowLayout {
        id: content
        anchors {left: parent.left;right: parent.right;top: parent.top;margins: 12}
        spacing: 10
        MaterialIcon {
            text: "warning"
            color: "#ef6a74"
            Layout.alignment: Qt.AlignTop
        }
        Text {
            Layout.fillWidth: true
            text: qsTr("Warning: Run local agents only in sandboxes and on isolated test systems. They can change files and system settings. Hermes does not currently enable a sandbox.")
            color: MenuStyle.ink
            font.family: MenuStyle.fontFamily
            font.pixelSize: 13
            wrapMode: Text.WordWrap
        }
    }
}
