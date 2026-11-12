import QtQuick
import "Engine.js" as Motion

Item {
    id: root
    property bool animate: visible
    property var engine: null
    property real unit: 1
    property real pendingTime: 0
    readonly property int barCount: pieces.count
    clip: true

    function resizeEngine() {
        if (!engine) return
        engine.resize(width, height)
        unit = engine.unit
        paintPose()
    }
    function paintPose() {
        if (!engine) return
        for (let i = 0; i < pieces.count; i++) {
            const piece = pieces.itemAt(i) as Bar
            const body = engine.bodies[i]
            piece.x = body.p.x
            piece.y = body.p.y
            piece.rotation = body.a * 180 / Math.PI
            piece.stretchX = body.s.x
            piece.stretchY = body.s.y
        }
    }
    onWidthChanged: resizeEngine()
    onHeightChanged: resizeEngine()
    onAnimateChanged: pendingTime = 0

    component Bar: Item {
        id: piece
        required property var modelData
        property real stretchX: 1
        property real stretchY: 1
        transform: Scale { xScale: piece.stretchX; yScale: piece.stretchY }
        Rectangle {
            x: -width / 2
            y: -height / 2
            width: piece.modelData[2]
            height: piece.modelData[3]
            radius: 1
            color: piece.modelData[4]
            antialiasing: true
        }
    }

    Rectangle { anchors.fill: parent; color: "black" }
    Item {
        scale: root.unit
        transformOrigin: Item.TopLeft
        Repeater {
            id: pieces
            model: Motion.bars
            delegate: Bar {}
        }
    }
    FrameAnimation {
        running: root.animate && root.visible && root.engine !== null
        onTriggered: {
            root.pendingTime += frameTime
            // Limit simulation/UI updates to 60/s even on high refresh monitors.
            if (root.pendingTime < 1 / 60 - 0.0001) return
            root.engine.step(root.pendingTime)
            root.pendingTime = 0
            root.paintPose()
        }
    }
    Component.onCompleted: {
        engine = new Motion.Engine(width, height)
        unit = engine.unit
        paintPose()
    }
}
