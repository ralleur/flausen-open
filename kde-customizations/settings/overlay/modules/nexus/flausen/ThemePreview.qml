pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
Button {
    id: root
    property string label
    text: label
    property bool dark
    property bool automatic
    property bool selected
    Layout.fillWidth: true
    Layout.preferredWidth: 1
    implicitHeight: width * 0.56 + 30
    Accessible.name: label
    Accessible.role: Accessible.RadioButton
    Accessible.checkable: true
    Accessible.checked: selected
    background: Item {}
    contentItem: Item {
        Rectangle {
            id: preview
            width: parent.width
            height: parent.height - 30
            radius: 12
            color: root.dark ? "#343f50" : "#e6e2df"
            border { width: root.selected || root.visualFocus ? 2 : 1; color: root.selected || root.visualFocus ? FlausenStyle.accent : FlausenStyle.line }
            clip: true
            Rectangle { width: parent.height * 0.56; height: width; radius: width/2; x: 16; y: 12; color: "#f17a67" }
            Rectangle { width: parent.width * 0.55; height: width; radius: width/2; x: parent.width * 0.62; y: parent.height * 0.55; color: "#efb55c" }
            Rectangle { width: parent.width * 0.45; height: width; radius: width/2; x: parent.width * 0.79; y: parent.height * 0.7; color: "#4c87dc" }
            Rectangle {
                anchors.centerIn: parent
                width: parent.width * 0.64
                height: parent.height * 0.64
                radius: 8
                color: root.dark ? "#202429" : "#f8f6f4"
                border { width: 1; color: root.dark ? "#474b50" : "#d9d5d2" }
                Row {
                    x: 9; y: 8; spacing: 4
                    Repeater { model: ["#f56c59", "#f4bb53", "#64c577"]; Rectangle { required property string modelData; width: 5; height: 5; radius: 3; color: modelData } }
                }
                Column { x: 10; y: 22; spacing: 4
                    Repeater { model: 4; Rectangle { width: preview.width * 0.14; height: 4; radius: 2; color: root.dark ? "#41464b" : "#d7d4d1" } }
                }
                Rectangle { x: parent.width * 0.42; y: 22; width: parent.width * 0.5; height: parent.height - 30; radius: 4; color: root.dark ? "#30353c" : "#e9e6e3" }
            }
            Rectangle { visible: root.automatic; x: parent.width/2; width: parent.width/2; height: parent.height; color: "#35445d"; opacity: 0.55 }
        }
        Row {
            anchors { horizontalCenter: parent.horizontalCenter; bottom: parent.bottom }
            spacing: 8
            Rectangle { width: 16; height: 16; radius: 8; color: "transparent"; border { width: 1.5; color: root.selected ? FlausenStyle.accent : FlausenStyle.secondary }
                Rectangle { anchors.centerIn: parent; width: 9; height: 9; radius: 5; color: FlausenStyle.accent; visible: root.selected }
            }
            Text { text: root.label; font {family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 14} color: FlausenStyle.text }
        }
    }
}
