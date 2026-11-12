import QtQuick
import Quickshell

Card {
    implicitHeight: Theme.geo.clockHeight ?? 166
    SystemClock {
        id: clock
        precision: SystemClock.Minutes
    }
    ShellText {
        x: 20
        y: 20
        text: Qt.formatDateTime(clock.date, "ddd, d. MMM")
        font.pixelSize: 13
    }
    ShellText {
        x: 18
        y: 38
        text: Qt.formatDateTime(clock.date, "HH:mm")
        font.pixelSize: Theme.type.clock
        font.weight: Font.Light
        font.letterSpacing: -2
    }
    ShellText {
        x: 20
        y: 115
        text: "Raum für gute Ideen."
        color: Theme.colors.muted
        font.pixelSize: 11
    }
    Row {
        anchors {
            right: parent.right
            bottom: parent.bottom
            margins: 20
        }
        Repeater {
            model: [Theme.brand.amber, Theme.brand.blue, Theme.brand.green, Theme.brand.red]
            Rectangle {
                required property string modelData
                width: 9
                height: 3
                color: modelData
            }
        }
    }
}
