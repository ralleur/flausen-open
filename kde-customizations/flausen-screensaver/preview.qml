import QtQuick
import QtQuick.Window
import "wallpaper/contents/ui" as Flausen

Window {
    width: 960; height: 540; visible: true
    property int frame: 0
    property int segment: 0
    property int inSegment: 0
    readonly property var program: [["arrival",120],["hold",24],["wave",108],["burst",156],["snake",312]]
    Flausen.KineticAnimation { id: animation; anchors.fill: parent; animate: false }
    function captureNext() {
        if (frame >= 720) { Qt.quit(); return }
        if (inSegment === 0) animation.engine.start(program[segment][0])
        animation.engine.step(1 / 24)
        animation.paintPose()
        animation.grabToImage(function(result) {
            const name = String(frame).padStart(4,"0")
            if(!result.saveToFile("/home/USER/flausen/.cache/flausen-saver-preview/frame"+name+".png")){Qt.exit(2);return}
            frame++
            inSegment++
            if (inSegment >= program[segment][1]) { segment++; inSegment=0 }
            Qt.callLater(captureNext)
        })
    }
    Timer { interval: 150; running: true; onTriggered: captureNext() }
    Timer { interval: 90000; running: true; onTriggered: Qt.exit(3) }
}
