pragma ComponentBehavior: Bound
import QtQuick
import qs.components

// Visual only: native slider range, step, keyboard and pointer handling survive.
Item {
    id: root
    required property var control
    property real position: control.position
    property color fillColor: control.palette.highlight
    property color emptyColor: "#575b60"
    property color outlineColor: "#e2e5e8"
    property bool muted: false
    readonly property bool vertical: control.orientation === Qt.Vertical
    readonly property int count: Math.max(2, Math.min(60, Math.floor((vertical ? height : width) / 10)))
    readonly property real pitch: (vertical ? height : width) / count
    readonly property real gap: Math.min(3, pitch * 0.28)
    readonly property int current: Math.round(Math.max(0, Math.min(1, position)) * (count - 1))
    implicitWidth: vertical ? 28 : 200
    implicitHeight: vertical ? 200 : 28
    x: control.leftPadding
    y: control.topPadding
    width: control.availableWidth
    height: control.availableHeight
    opacity: control.enabled ? 1 : 0.4

    Repeater {
        model: root.count
        Rectangle {
            required property int index
            readonly property int visualIndex: root.vertical || root.control.mirrored ? root.count - 1 - index : index
            readonly property bool lit: !root.muted && root.position > 0 && index <= root.current
            x: root.vertical ? (root.width - width) / 2 : visualIndex * root.pitch + root.gap / 2
            y: root.vertical ? visualIndex * root.pitch + root.gap / 2 : (root.height - height) / 2
            width: root.vertical ? Math.min(28, root.width - 6) : root.pitch - root.gap
            height: root.vertical ? root.pitch - root.gap : Math.max(18, Math.min(24, root.height - 6))
            radius: 1.8
            color: lit ? root.fillColor : root.emptyColor
            PrimaryControlFill {} // Capture primary material
            Rectangle {
                anchors.fill: parent
                anchors.margins: -2
                visible: parent.index === root.current
                color: "transparent"
                radius: 3
                border.width: root.control.visualFocus ? 2 : 1.3
                border.color: root.outlineColor
            }
        }
    }
}
