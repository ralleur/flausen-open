pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Window
import QtQuick.Controls
Button {
    id: root
    required property string controlAction
    required property string description
    implicitWidth: 30
    implicitHeight: 30
    Accessible.name: description
    ToolTip.visible: hovered
    ToolTip.text: description
    ToolTip.delay: 600
    background: Rectangle {
        width: 28; height: 28
        anchors.centerIn: parent
        radius: 4
        color: Qt.alpha(root.palette.windowText, root.down ? 0.20 : root.hovered ? 0.12 : 0)
        border.width: root.visualFocus ? 1 : 0
        border.color: FlausenStyle.accent
    }
    contentItem: Item {
        Canvas {
            anchors.centerIn: parent
            width: 16; height: 16
            property color ink: root.palette.windowText
            opacity: root.Window.window?.active ? 1 : 0.55
            onInkChanged: requestPaint()
            onPaint: {
                const ctx = getContext("2d");
                ctx.reset();
                ctx.strokeStyle = ink;
                ctx.lineWidth = 1.2;
                ctx.lineCap = "square";
                ctx.lineJoin = "miter";
                ctx.beginPath();
                if (root.controlAction === "minimize") {
                    ctx.moveTo(4, 11.5); ctx.lineTo(12, 11.5);
                } else if (root.controlAction === "maximize") {
                    ctx.rect(4.5, 4.5, 7, 7);
                } else {
                    ctx.moveTo(4.5, 4.5); ctx.lineTo(11.5, 11.5);
                    ctx.moveTo(11.5, 4.5); ctx.lineTo(4.5, 11.5);
                }
                ctx.stroke();
            }
        }
    }
}
