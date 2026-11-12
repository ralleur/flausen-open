pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Templates
import Caelestia
import Caelestia.Components
import Caelestia.Config
import qs.components
import qs.services

Slider {
    id: root

    property bool wavy
    property bool animateWave
    property real waveFrequency: 6
    property int waveDuration: 1000
    property int radius: Tokens.rounding.medium
    property bool interactionOnMove: true
    readonly property bool dragging: mouse.pressed

    property color fgColour: Colours.palette.m3primary
    property color bgColour: enabled ? Colours.palette.m3secondaryContainer : Colours.disabledContainer

    property real pos: visualPosition
    property real filledWidth

    signal interaction(v: real)
    signal released(v: real)

    onMoved: {
        if (!mouse.pressed) {
            interaction(position);
            if (!pressed) released(position);
        }
    }

    implicitWidth: 200
    implicitHeight: 28
    background: SegmentedTrack {
        control: root
        position: root.mirrored ? 1 - root.pos : root.pos
        fillColor: root.fgColour
        emptyColor: Colours.light ? "#c2c5c9" : "#575b60"
        outlineColor: Colours.light ? "#333b45" : "#e2e5e8"
    }
    handle: SegmentedHandle { id: handle; control: root }

    Binding {
        id: posBinding

        target: root
        property: "pos"
        value: CUtils.clamp(mouse.pressStartPos + mouse.dragMovement, 0, 1)
        when: mouse.pressed
    }

    MouseArea {
        id: mouse

        property real pressStartX
        property real pressStartPos
        property real dragMovement

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        cursorShape: Qt.PointingHandCursor
        preventStealing: true
        implicitHeight: Math.max(32, root.height)

        onPressed: e => {
            pressStartX = e.x;
            pressStartPos = CUtils.clamp(e.x / width, 0, 1);
            if (root.interactionOnMove)
                root.interaction(root.mirrored ? 1 - pressStartPos : pressStartPos);
        }
        onPositionChanged: e => {
            dragMovement = (e.x - pressStartX) / width;
            if (root.interactionOnMove)
                root.interaction(root.mirrored ? 1 - posBinding.value : posBinding.value);
        }
        onCanceled: dragMovement = 0
        onReleased: e => {
            root.interaction(root.mirrored ? 1 - posBinding.value : posBinding.value);
            root.released(root.mirrored ? 1 - posBinding.value : posBinding.value);
            dragMovement = 0;
        }
    }

}
