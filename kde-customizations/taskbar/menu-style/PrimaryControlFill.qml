import QtQuick
import qs.services

// Decoration only: preserve the owning control's layout, input and state layer.
MenuPrimarySurface {
    property bool active: true
    property color sourceColor: parent.color
    anchors.fill: parent
    anchors.margins: parent.border.width > 1 ? parent.border.width : 0
    radius: Math.max(0, parent.radius - anchors.margins)
    topLeftRadius: Math.max(0, parent.topLeftRadius - anchors.margins)
    topRightRadius: Math.max(0, parent.topRightRadius - anchors.margins)
    bottomLeftRadius: Math.max(0, parent.bottomLeftRadius - anchors.margins)
    bottomRightRadius: Math.max(0, parent.bottomRightRadius - anchors.margins)
    visible: active && enabled && (parent.disabled === undefined || !parent.disabled)
        && MenuStyle.isBlueControl(sourceColor)
}
