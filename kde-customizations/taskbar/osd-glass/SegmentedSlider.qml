pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Templates as T
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services

Item {
    id: root

    required property string icon
    required property string accessibleLabel
    property color fillColor: Colours.palette.m3primary
    property bool muted: false
    property bool muteEnabled: false
    property alias value: slider.value
    property alias to: slider.to
    signal moved()
    signal muteToggled()

    T.Button {
        id: badge
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        width: 36
        height: width
        enabled: root.muteEnabled
        padding: 0
        hoverEnabled: true
        focusPolicy: root.muteEnabled ? Qt.StrongFocus : Qt.NoFocus
        checkable: root.muteEnabled
        checked: root.muted
        Accessible.name: (root.muted ? qsTr("Enable %1") : qsTr("Mute %1")).arg(root.accessibleLabel)
        onClicked: root.muteToggled()

        background: Rectangle {
            radius: width / 2
            color: Qt.rgba(root.fillColor.r, root.fillColor.g, root.fillColor.b, badge.hovered || badge.down ? 0.35 : 0.2)
            border.width: badge.visualFocus ? 1 : 0
            border.color: root.fillColor
        }
        HoverHandler { cursorShape: root.muteEnabled ? Qt.PointingHandCursor : Qt.ArrowCursor }

        contentItem: MaterialIcon {
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: root.icon
            color: "#f4f5f6"
            fontStyle: Tokens.font.icon.medium
        }
    }

    T.Slider {
        id: slider
        anchors.top: badge.bottom
        anchors.topMargin: 10
        anchors.bottom: percentage.top
        anchors.bottomMargin: 8
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width
        orientation: Qt.Vertical
        from: 0
        to: 1
        stepSize: 0.01
        padding: 0
        live: true
        focusPolicy: Qt.StrongFocus
        Accessible.name: root.accessibleLabel
        Accessible.description: Math.round(value * 100) + "%"
        onMoved: root.moved()

        background: SegmentedTrack {
            control: slider
            fillColor: root.fillColor
            muted: root.muted
            emptyColor: "#575b60"
        }
        handle: SegmentedHandle { control: slider }
        HoverHandler { cursorShape: Qt.PointingHandCursor }
    }

    StyledText {
        id: percentage
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        text: Math.round(slider.value * 100) + "%"
        color: "#f4f5f6"
        font.pixelSize: 18
        font.weight: Font.Medium
    }
}
