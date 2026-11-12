pragma ComponentBehavior: Bound
import QtQuick
import qs.components
import QtQuick.Controls
Switch {
    id: root
    spacing: 12
    implicitHeight: 54
    leftPadding: 16; rightPadding: 16
    indicator: Rectangle {
        x: root.width - width - root.rightPadding
        y: (root.height - height) / 2
        width: 44; height: 25; radius: 13
        color: root.checked ? FlausenStyle.accent : FlausenStyle.light ? "#d2d3d6" : "#464b52"
        PrimaryControlFill {} // Capture primary material
        border.width: root.visualFocus ? 2 : 0
        border.color: FlausenStyle.text
        Rectangle {
            x: root.checked ? parent.width - width - 3 : 3
            y: 3; width: 19; height: 19; radius: 10; color: "#ffffff"
            Behavior on x { NumberAnimation {duration: FlausenStyle.motionDuration} }
        }
    }
    contentItem: Text {
        text: root.text
        font {family:FlausenStyle.family; pixelSize:FlausenStyle.fontScale * 15}
        color: FlausenStyle.text
        verticalAlignment: Text.AlignVCenter
        rightPadding: 64
        elide: Text.ElideRight
    }
}
