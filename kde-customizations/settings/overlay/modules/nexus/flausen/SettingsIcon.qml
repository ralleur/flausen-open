pragma ComponentBehavior: Bound
import QtQuick
import qs.components
// Fixed optical field: glyph size and alignment are independent of label metrics.
Item {
    id: root
    required property string name
    property int fieldSize: 48
    property int glyphPixels: 48
    property color color: FlausenStyle.text
    implicitWidth: fieldSize
    implicitHeight: fieldSize
    MaterialIcon {
        anchors.fill: parent
        text: root.name
        color: root.color
        fontStyle.pointSize: root.glyphPixels * 0.75
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        renderType: Text.QtRendering
        antialiasing: true
    }
}
