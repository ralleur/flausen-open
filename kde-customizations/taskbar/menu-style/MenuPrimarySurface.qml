import QtQuick
import qs.services

// Shared primary action material. Geometry and interaction belong to the caller.
Rectangle {
    id: root
    property bool disabled: false
    radius: 14
    gradient: Gradient {
        GradientStop { position: 0; color: root.disabled ? MenuStyle.muted : MenuStyle.primaryTop }
        GradientStop { position: 1; color: root.disabled ? MenuStyle.muted : MenuStyle.primaryBottom }
    }
    border.width: 1
    border.color: root.disabled ? MenuStyle.rule : MenuStyle.primaryEdge
    Rectangle {
        anchors.fill: parent
        anchors.margins: 1
        radius: Math.max(0, root.radius - 1)
        topLeftRadius: Math.max(0, root.topLeftRadius - 1)
        topRightRadius: Math.max(0, root.topRightRadius - 1)
        bottomLeftRadius: Math.max(0, root.bottomLeftRadius - 1)
        bottomRightRadius: Math.max(0, root.bottomRightRadius - 1)
        color: "transparent"
        border.width: 1
        border.color: MenuStyle.primaryLight
        opacity: root.disabled ? 0.2 : 0.45
    }
}
