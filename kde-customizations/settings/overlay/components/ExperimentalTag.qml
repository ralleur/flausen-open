import QtQuick
import qs.services

Rectangle {
    property bool compact: false
    implicitWidth: label.implicitWidth + 12
    implicitHeight: label.implicitHeight + 6
    radius: 5
    color: "#a62f3b"
    border.width: 1
    border.color: "#ed7580"
    Text {
        id: label
        anchors.centerIn: parent
        text: qsTr("Experimental")
        color: "#ffffff"
        font.family: MenuStyle.fontFamily
        font.pixelSize: parent.compact ? 10 : 12
        font.weight: Font.DemiBold
    }
}
