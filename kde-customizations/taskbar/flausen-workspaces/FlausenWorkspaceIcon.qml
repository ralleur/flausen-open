import QtQuick
import qs.components
import Quickshell.Widgets
import qs.services

Item {
    id: root

    required property int workspaceId
    required property int activeWorkspaceId
    required property bool occupied
    required property string screenName

    readonly property bool active: workspaceId === activeWorkspaceId
    // Stable identity per desktop, independent of focus, occupancy and delegate reuse.
    readonly property var shapes: ["play", "everyday", "idea", "weight"]
    readonly property string shapeName: shapes[((workspaceId - 1) % shapes.length + shapes.length) % shapes.length]
    readonly property real rawSwipeOffset: Kwin.swipeOffsetByOutput?.[screenName] ?? Kwin.swipeOffset
    property int swipeStartWorkspaceId: -1
    property bool swiping: false
    readonly property real swipeWeight: {
        if (!swiping || rawSwipeOffset === 0)
            return active ? 1 : 0;
        const start = swipeStartWorkspaceId > 0 ? swipeStartWorkspaceId : activeWorkspaceId;
        const target = start + (rawSwipeOffset > 0 ? 1 : -1);
        const progress = Math.min(1, Math.abs(rawSwipeOffset));
        if (workspaceId === start)
            return 1 - progress;
        if (workspaceId === target)
            return progress;
        return 0;
    }
    property real smoothSwipeWeight: swipeWeight

    onRawSwipeOffsetChanged: {
        if (rawSwipeOffset !== 0) {
            if (!swiping)
                swipeStartWorkspaceId = activeWorkspaceId;
            swiping = true;
            settle.stop();
        } else {
            settle.restart();
        }
    }

    Timer {
        id: settle
        interval: 120
        onTriggered: root.swiping = false
    }

    Behavior on smoothSwipeWeight {
        enabled: root.swiping
        SmoothedAnimation { velocity: -1; duration: 60; easing.type: Easing.Linear }
    }

    IconImage {
        anchors.centerIn: parent
        source: Qt.resolvedUrl("flausen-shapes/" + root.shapeName + ".svg")
        implicitSize: Math.min(root.width, root.height)
        mipmap: true
        scale: 0.62 + 0.22 * (root.swiping ? root.smoothSwipeWeight : (root.active ? 1 : 0))
        opacity: 1

        Behavior on scale {
            enabled: !root.swiping
            Anim { type: Anim.FastSpatial }
        }
        Behavior on opacity { Anim { type: Anim.DefaultEffects } }
    }
}
