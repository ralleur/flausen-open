import QtQuick
import QtQuick.Controls
import QtTest
import "../overlay/components/controls"

Item {
    width: 700; height: 360
    Rectangle { anchors.fill: parent; color: "#14181c" }
    Slider {
        id: horizontal
        x: 70; y: 55; width: 550; height: 40
        from: -20; to: 80; stepSize: 1; value: -20
        background: SegmentedTrack { id: track; control: horizontal }
        handle: SegmentedHandle { control: horizontal }
    }
    Slider {
        id: vertical
        x: 30; y: 110; width: 40; height: 200
        orientation: Qt.Vertical; value: 0.5
        background: SegmentedTrack { control: vertical; fillColor: "#53c67b" }
        handle: SegmentedHandle { control: vertical }
    }
    Rectangle {
        x: 100; y: 150; width: 540; height: 150; color: "#f7f6f5"; radius: 14
        Slider {
            id: light
            anchors.centerIn: parent; width: 480; height: 40; value: 1
            background: SegmentedTrack { control: light; emptyColor: "#c2c5c9"; outlineColor: "#333b45" }
            handle: SegmentedHandle { control: light }
        }
    }
    TestCase {
        name: "SegmentedSliders"
        when: windowShown
        function test_accentChanges() {
            const original = horizontal.palette.highlight
            horizontal.value = 30
            for (const accent of ["#e83279", "#32b578"]) {
                horizontal.palette.highlight = accent
                compare(track.fillColor, accent)
                const segment = track.children[2]
                verify(segment.lit)
                compare(segment.color, accent)
            }
            horizontal.palette.highlight = original
        }
        function test_pointerAndKeyboard() {
            horizontal.value = horizontal.from
            compare(track.current, 0)
            horizontal.forceActiveFocus()
            keyClick(Qt.Key_Right)
            compare(horizontal.value, -19)
            mouseClick(horizontal, horizontal.width - 2, horizontal.height / 2)
            compare(horizontal.value, horizontal.to)
            compare(track.current, track.count - 1)
            mouseClick(horizontal, 2, horizontal.height / 2)
            compare(horizontal.value, horizontal.from)
            mouseClick(vertical, vertical.width / 2, 2)
            compare(vertical.value, 1)
            mouseClick(vertical, vertical.width / 2, vertical.height - 2)
            compare(vertical.value, 0)
            horizontal.enabled = false
            mouseClick(horizontal, horizontal.width - 2, horizontal.height / 2)
            compare(horizontal.value, horizontal.from)
            horizontal.enabled = true
            horizontal.value = 30; vertical.value = .5
            horizontal.focus = false
            let saved = false
            horizontal.parent.grabToImage(function(result) {
                saved = result.saveToFile(Qt.resolvedUrl("../evidence/segmented-sliders.png").toString().replace("file://", ""));
            })
            tryVerify(() => saved)
        }
    }
}
