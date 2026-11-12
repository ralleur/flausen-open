import QtQuick
import QtQuick.Controls

Card {
    id: root
    required property var player
    implicitHeight: Theme.geo.mediaHeight ?? 150
    function duration(seconds: real): string {
        if (!isFinite(seconds) || seconds < 0)
            return "–:––";
        return Math.floor(seconds / 60) + ":" + String(Math.floor(seconds % 60)).padStart(2, "0");
    }
    Rectangle {
        x: 20
        y: 18
        width: 60
        height: 60
        radius: 7
        color: Theme.colors.elevated
        clip: true
        Image {
            anchors.fill: parent
            source: root.player?.trackArtUrl ?? ""
            fillMode: Image.PreserveAspectCrop
            asynchronous: true
        }
        ShellText {
            anchors.centerIn: parent
            visible: !root.player?.trackArtUrl
            text: "♫"
            font.pixelSize: 25
            color: Theme.colors.muted
        }
    }
    ShellText {
        x: 96
        y: 20
        width: parent.width - 112
        text: root.player?.trackTitle || "Keine Wiedergabe"
        font.weight: Font.Medium
    }
    ShellText {
        x: 96
        y: 40
        width: parent.width - 112
        text: root.player?.trackArtist || (root.player?.identity ?? "MPRIS-Player öffnen")
        color: Theme.colors.muted
        font.pixelSize: 11
    }
    ShellText {
        anchors.right: parent.right
        anchors.rightMargin: 20
        y: 65
        text: root.player ? root.duration(root.player.position) + " / " + root.duration(root.player.length) : ""
        font.pixelSize: 10
        color: Theme.colors.muted
    }
    Slider {
        id: seek
        x: 18
        y: 85
        width: parent.width - 36
        height: 16
        from: 0
        to: Math.max(1, root.player?.length ?? 1)
        value: root.player?.position ?? 0
        enabled: !!root.player?.canSeek && !!root.player?.lengthSupported
        Accessible.name: "Wiedergabeposition"
        onMoved: if (root.player?.canSeek)
            root.player.position = value
        background: Rectangle {
            x: seek.leftPadding
            y: seek.height / 2 - 1.5
            width: seek.availableWidth
            height: 3
            radius: 2
            color: Theme.colors.stroke
            Rectangle {
                width: seek.visualPosition * parent.width
                height: parent.height
                radius: 2
                color: Theme.colors.text
            }
        }
        handle: Rectangle {
            x: seek.leftPadding + seek.visualPosition * (seek.availableWidth - width)
            y: seek.height / 2 - height / 2
            width: 8
            height: 8
            radius: 4
            color: Theme.colors.focus
            visible: seek.hovered || seek.activeFocus
        }
    }
    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 104
        spacing: 26
        ShellButton {
            text: "⏮"
            hint: "Vorheriger Titel"
            enabled: !!root.player?.canGoPrevious
            onClicked: root.player.previous()
        }
        ShellButton {
            text: root.player?.isPlaying ? "Ⅱ" : "▶"
            hint: "Wiedergabe / Pause"
            enabled: !!root.player?.canTogglePlaying
            onClicked: root.player.togglePlaying()
        }
        ShellButton {
            text: "⏭"
            hint: "Nächster Titel"
            enabled: !!root.player?.canGoNext
            onClicked: root.player.next()
        }
    }
    Timer {
        interval: 1000
        running: root.visible && !!root.player?.isPlaying
        repeat: true
        onTriggered: root.player.positionChanged()
    }
}
