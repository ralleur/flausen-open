import QtQuick
import QtQuick.Shapes
import "Engine.js" as Motion
import "Geometry.js" as Geometry

Item {
    id: root
    property bool animate: visible
    property var engine: null
    property real unit: 1
    property real pendingTime: 0
    readonly property int pieceCount: pieces.count
    clip: true

    function paintPose() {
        if (!engine) return
        for (let i = 0; i < pieces.count; i++) {
            const piece = pieces.itemAt(i) as KineticPiece
            const body = engine.bodies[i]
            piece.x = body.p.x
            piece.y = body.p.y
            piece.rotation = body.a * 180 / Math.PI
            piece.stretchX = body.s.x
            piece.stretchY = body.s.y
        }
    }
    function resizeEngine() {
        if (!engine) return
        engine.resize(width, height)
        unit = engine.unit
        paintPose()
    }
    onWidthChanged: resizeEngine()
    onHeightChanged: resizeEngine()
    onAnimateChanged: pendingTime = 0

    component KineticPiece: Item {
        id: piece
        required property var modelData
        property real stretchX: 1
        property real stretchY: 1
        transform: Scale { xScale: piece.stretchX; yScale: piece.stretchY }
        Shape {
            x: -piece.modelData.cx * piece.modelData.scale
            y: -piece.modelData.cy * piece.modelData.scale
            scale: piece.modelData.scale
            transformOrigin: Item.TopLeft
            preferredRendererType: Shape.CurveRenderer
            ShapePath {
                strokeWidth: -1
                fillColor: piece.modelData.color
                fillRule: ShapePath.OddEvenFill
                PathSvg { path: piece.modelData.path }
            }
        }
    }
    Rectangle { anchors.fill: parent; color: "black" }
    Item {
        scale: root.unit
        transformOrigin: Item.TopLeft
        Repeater { id: pieces; model: Geometry.pieces; delegate: KineticPiece {} }
    }
    FrameAnimation {
        running: root.animate && root.visible && root.engine !== null
        onTriggered: {
            root.pendingTime += frameTime
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
