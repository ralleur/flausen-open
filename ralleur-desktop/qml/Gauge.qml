import QtQuick

Item {
    id: root
    required property string label
    required property real value
    required property color accent
    width: 66
    height: 78
    Canvas {
        id: ring
        width: 58
        height: 58
        anchors.horizontalCenter: parent.horizontalCenter
        property color track: Theme.colors.stroke
        onTrackChanged: requestPaint()
        onPaint: {
            const ctx = getContext("2d");
            ctx.reset();
            ctx.lineWidth = 3;
            ctx.lineCap = "round";
            ctx.strokeStyle = track;
            ctx.beginPath();
            ctx.arc(29, 29, 26, Math.PI * 0.75, Math.PI * 2.25);
            ctx.stroke();
            if (root.value >= 0) {
                ctx.strokeStyle = root.accent;
                ctx.beginPath();
                ctx.arc(29, 29, 26, Math.PI * 0.75, Math.PI * (0.75 + 1.5 * Math.min(100, root.value) / 100));
                ctx.stroke();
            }
        }
        ShellText {
            anchors.centerIn: parent
            text: root.value < 0 ? "–" : Math.round(root.value) + "%"
            font.weight: Font.Medium
        }
    }
    onValueChanged: ring.requestPaint()
    onAccentChanged: ring.requestPaint()
    ShellText {
        y: 63
        anchors.horizontalCenter: parent.horizontalCenter
        text: root.label
        font.pixelSize: 11
    }
}
