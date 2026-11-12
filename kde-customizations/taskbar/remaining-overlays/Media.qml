pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Services.Mpris
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.components.effects
import qs.services

// Taskbar player. The surrounding ClipWrapper owns the shared smoke glass.
ColumnLayout {
    id: root
    required property var popouts
    property real scaleOffset: 1.0
    property real fontScale: 1.0
    property bool _isSidebarOpen: false
    readonly property MprisPlayer player: Players.sourcePlayer(Config.bar.media.excludedSources)
    readonly property string sourceName: Players.getIdentity(root.player)
    readonly property real bodyPointSize: MenuStyle.bodyPointSize(root.fontScale)
    readonly property real duration: Math.max(0, root.player?.length ?? 0)
    readonly property real progress: root.duration > 0 ? Math.max(0, Math.min(1, (root.player?.position ?? 0) / root.duration)) : 0
    readonly property var playerStream: Audio.appStreams ? Players.playerStream(root.player, Audio) : null
    readonly property real currentVolume: (root.playerStream && root.playerStream.audio) ? root.playerStream.audio.volume : (root.playerStream ? Audio.getAppVolume(root.playerStream) : Audio.volume)
    readonly property var desktopEntry: root.player ? DesktopEntries.byId(root.player.desktopEntry) : null

    // Chromium and Plasma can expose the same tab twice. Chromium may supply
    // only "title • artist" and its application logo, while Plasma has the art.
    // Borrow artwork only from a richer entry for the same app and exact track;
    // keep transport, position and source selection on the chosen player.
    readonly property string artworkUrl: {
        const selected = root.player;
        if (!selected) return "";
        const normalise = value => String(value || "").toLowerCase().replace(/[\s•·|–—:,&-]/g, "");
        const title = normalise(selected.trackTitle);
        if (title && !selected.trackArtist && !selected.trackAlbum) {
            for (const candidate of Players.list) {
                if (candidate === selected || !candidate.trackArtist || !candidate.trackTitle)
                    continue;
                const sameApp = selected.desktopEntry && candidate.desktopEntry
                    ? selected.desktopEntry === candidate.desktopEntry
                    : Players.getIdentity(selected) === Players.getIdentity(candidate);
                if (!sameApp) continue;
                const candidateTitle = normalise(candidate.trackTitle);
                const candidateArtist = normalise(candidate.trackArtist);
                if (title === candidateTitle || title === candidateTitle + candidateArtist) {
                    const art = Players.getArtUrl(candidate);
                    if (art) return art;
                }
            }
        }
        return Players.getArtUrl(selected);
    }

    function timestamp(seconds: real): string {
        if (!isFinite(seconds) || seconds < 0) return "–:––";
        const total = Math.floor(seconds);
        return Math.floor(total / 60) + ":" + String(total % 60).padStart(2, "0");
    }
    function setVolumeLevel(value: real): void {
        Players.setPlayerVolume(root.player, root.playerStream, Audio, value);
    }

    width: 376 * root.scaleOffset
    spacing: 0

    RowLayout {
        Layout.fillWidth: true
        spacing: 12 * root.scaleOffset
        MenuText {
            Layout.fillWidth: true
            Layout.minimumWidth: 110 * root.scaleOffset
            text: qsTr("Now playing")
            font.pointSize: root.bodyPointSize * 1.35
            wrapMode: Text.WordWrap
        }
        Button {
            id: sourceSelector
            objectName: "mediaSource"
            Layout.preferredWidth: 160 * root.scaleOffset
            implicitHeight: Math.max(40 * root.scaleOffset, sourceLabel.implicitHeight + 16 * root.scaleOffset)
            enabled: Players.list.length > 1
            Accessible.name: qsTr("Media source: %1").arg(root.sourceName || qsTr("No media"))
            onClicked: sourceMenu.expanded = !sourceMenu.expanded
            background: Rectangle {
                radius: 14 * root.scaleOffset
                color: sourceSelector.hovered || sourceSelector.visualFocus ? MenuStyle.rule : MenuStyle.cardFill
                border.width: 1
                border.color: sourceSelector.visualFocus ? MenuStyle.accent : MenuStyle.border
            }
            contentItem: RowLayout {
                spacing: 8 * root.scaleOffset
                Image {
                    Layout.preferredWidth: 26 * root.scaleOffset
                    Layout.preferredHeight: width
                    source: Quickshell.iconPath(root.desktopEntry?.icon || root.sourceName.toLowerCase().replace(/ /g, "-") || "audio-x-generic", "audio-x-generic")
                }
                MenuText {
                    id: sourceLabel
                    Layout.fillWidth: true
                    text: root.sourceName || qsTr("No media")
                    font.pointSize: root.bodyPointSize
                    elide: Text.ElideRight
                }
                MaterialIcon {
                    text: "expand_more"
                    fontStyle: Tokens.font.icon.size(root.bodyPointSize * 1.2).build()
                    color: MenuStyle.muted
                    opacity: Players.list.length > 1 ? 1 : 0.4
                }
            }
            Menu {
                id: sourceMenu
                objectName: "mediaSourceMenu"
                attachTo: sourceSelector
                attachSideY: Menu.Bottom
                thisSideY: Menu.Top
                attachSideX: Menu.Right
                thisSideX: Menu.Right
                sharedPopoverStyle: true
                menuFontScale: root.fontScale
                menuGeometryScale: root.scaleOffset
                items: playerList.instances
                onItemSelected: item => Players.manualActive = (item as PlayerItem).modelData
            }
        }
    }

    Item {
        Layout.alignment: Qt.AlignHCenter
        Layout.topMargin: 24 * root.scaleOffset
        Layout.preferredWidth: 256 * root.scaleOffset
        Layout.preferredHeight: width
        Rectangle {
            id: coverMask
            anchors.fill: parent
            radius: 20 * root.scaleOffset
            color: MenuStyle.cardFill
            border.width: 1
            border.color: MenuStyle.border
        }
        Rectangle {
            id: imageMask
            anchors.fill: parent
            radius: coverMask.radius
            color: "white"
            visible: false
            layer.enabled: true
        }
        Image {
            id: artwork
            anchors.fill: parent
            anchors.margins: 1
            source: root.artworkUrl
            asynchronous: true
            fillMode: Image.PreserveAspectFit
            layer.enabled: true
            layer.effect: Mask { maskSource: imageMask }
        }
        MaterialIcon {
            anchors.centerIn: parent
            visible: artwork.status !== Image.Ready
            text: artwork.status === Image.Loading ? "downloading" : "music_note"
            fontStyle: Tokens.font.icon.size(56 * root.scaleOffset).build()
            color: MenuStyle.muted
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        Layout.topMargin: 17 * root.scaleOffset
        spacing: 5 * root.scaleOffset
        MenuText {
            Layout.fillWidth: true
            text: root.player ? (root.player.trackTitle || qsTr("Unknown title")) : qsTr("No media playing")
            font.pointSize: root.bodyPointSize * 1.65
            font.weight: Font.DemiBold
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.Wrap
            maximumLineCount: 2
            elide: Text.ElideRight
        }
        MenuText {
            Layout.fillWidth: true
            visible: text !== ""
            text: root.player?.trackArtist || ""
            font.pointSize: root.bodyPointSize
            color: MenuStyle.muted
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.Wrap
            maximumLineCount: 2
            elide: Text.ElideRight
        }
        MenuText {
            Layout.fillWidth: true
            visible: text !== ""
            text: root.player?.trackAlbum || ""
            font.pointSize: root.bodyPointSize * MenuStyle.secondaryPixels / MenuStyle.bodyPixels
            color: MenuStyle.muted
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }
    }

    Slider {
        id: seek
        objectName: "mediaSeek"
        Layout.fillWidth: true
        Layout.topMargin: 20 * root.scaleOffset
        implicitHeight: 30 * root.scaleOffset
        leftPadding: 0
        rightPadding: 0
        value: root.progress
        stepSize: root.duration > 0 ? Math.min(1, 5 / root.duration) : 0.01
        enabled: !!root.player?.canSeek && !!root.player?.positionSupported && root.duration > 0
        Accessible.name: qsTr("Playback position")
        onMoved: if (enabled) root.player.position = value * root.duration
        Keys.onPressed: event => {
            if (enabled && (event.key === Qt.Key_Home || event.key === Qt.Key_End)) {
                root.player.position = event.key === Qt.Key_Home ? 0 : root.duration;
                event.accepted = true;
            }
        }
        background: Row {
            y: (seek.height - height) / 2
            width: seek.availableWidth
            height: 20 * root.scaleOffset
            spacing: 3 * root.scaleOffset
            Repeater {
                model: 32
                Rectangle {
                    required property int index
                    width: (seek.availableWidth - 31 * 3 * root.scaleOffset) / 32
                    height: 20 * root.scaleOffset
                    radius: 2 * root.scaleOffset
                    color: MenuStyle.rule
                    MenuPrimarySurface {
                        anchors.fill: parent
                        radius: parent.radius
                        visible: (index + 0.5) / 32 <= seek.visualPosition
                    }
                }
            }
        }
        handle: Rectangle {
            x: Math.max(0, Math.min(seek.availableWidth - width, seek.visualPosition * seek.availableWidth - width / 2))
            y: (seek.height - height) / 2
            width: 10 * root.scaleOffset
            height: 25 * root.scaleOffset
            radius: 3 * root.scaleOffset
            color: "transparent"
            visible: seek.enabled
            border.width: seek.visualFocus ? 2 : 1
            border.color: seek.visualFocus ? MenuStyle.accent : MenuStyle.ink
        }
    }
    RowLayout {
        Layout.fillWidth: true
        MenuText {
            text: root.timestamp(seek.pressed ? seek.value * root.duration : (root.player?.positionSupported ? root.player.position : -1))
            font.pointSize: root.bodyPointSize * MenuStyle.secondaryPixels / MenuStyle.bodyPixels
            color: MenuStyle.muted
        }
        Item { Layout.fillWidth: true }
        MenuText {
            text: root.timestamp(root.duration > 0 ? root.duration : -1)
            font.pointSize: root.bodyPointSize * MenuStyle.secondaryPixels / MenuStyle.bodyPixels
            color: MenuStyle.muted
        }
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.topMargin: 25 * root.scaleOffset
        Layout.bottomMargin: 12 * root.scaleOffset
        spacing: (root.width - 292 * root.scaleOffset) / 4
        TransportButton {
            symbol: "shuffle"
            text: qsTr("Shuffle")
            enabled: root.player?.shuffleSupported ?? false
            checked: root.player?.shuffle ?? false
            onClicked: root.player.shuffle = !root.player.shuffle
        }
        TransportButton {
            symbol: "skip_previous"
            text: qsTr("Previous track")
            enabled: root.player?.canGoPrevious ?? false
            onClicked: root.player.previous()
        }
        TransportButton {
            primary: true
            symbol: root.player?.isPlaying ? "pause" : "play_arrow"
            text: root.player?.isPlaying ? qsTr("Pause") : qsTr("Play")
            enabled: root.player?.canTogglePlaying ?? false
            onClicked: root.player.togglePlaying()
        }
        TransportButton {
            symbol: "skip_next"
            text: qsTr("Next track")
            enabled: root.player?.canGoNext ?? false
            onClicked: root.player.next()
        }
        TransportButton {
            symbol: root.player?.loopState === MprisLoopState.Track ? "repeat_one" : "repeat"
            text: qsTr("Repeat")
            enabled: root.player?.loopSupported ?? false
            checked: !!root.player && root.player.loopState !== MprisLoopState.None
            Accessible.description: root.player?.loopState === MprisLoopState.Track ? qsTr("Repeat track") : checked ? qsTr("Repeat playlist") : qsTr("Repeat off")
            onClicked: {
                const state = root.player.loopState;
                root.player.loopState = state === MprisLoopState.None ? MprisLoopState.Track : state === MprisLoopState.Track ? MprisLoopState.Playlist : MprisLoopState.None;
            }
        }
    }

    component TransportButton: Button {
        id: control
        property string symbol
        property bool primary: false
        Layout.fillWidth: false
        Layout.preferredWidth: (primary ? 68 : 56) * root.scaleOffset
        implicitHeight: (primary ? 68 : 56) * root.scaleOffset
        objectName: "media-" + symbol
        Accessible.name: text
        ToolTip.visible: hovered
        ToolTip.text: text
        ToolTip.delay: 700
        background: Rectangle {
            radius: height / 2
            color: control.down || control.hovered ? MenuStyle.rule : MenuStyle.cardFill
            border.width: control.visualFocus || control.checked ? 1 : 0
            border.color: control.visualFocus || control.checked ? MenuStyle.accent : MenuStyle.border
            MenuPrimarySurface {
                anchors.fill: parent
                radius: parent.radius
                visible: control.primary
                disabled: !control.enabled
            }
            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                color: "transparent"
                border.width: control.visualFocus ? 2 : 0
                border.color: MenuStyle.ink
            }
        }
        contentItem: MaterialIcon {
            text: control.symbol
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            fontStyle: Tokens.font.icon.size((control.primary ? 28 : 23) * root.scaleOffset).build()
            color: control.primary ? "white" : control.checked ? MenuStyle.accent : MenuStyle.ink
            opacity: control.enabled ? 1 : 0.3
        }
    }
    component PlayerItem: MenuItem {
        required property MprisPlayer modelData
        icon: modelData === root.player ? "check" : ""
        text: Players.getIdentity(modelData)
        activeIcon: "animated_images"
    }
    Variants {
        id: playerList
        model: Players.list
        PlayerItem {}
    }
    Timer {
        running: root.visible && (root.player?.isPlaying ?? false) && (root.player?.positionSupported ?? false)
        interval: 1000
        triggeredOnStart: true
        repeat: true
        onTriggered: root.player?.positionChanged()
    }
    WheelHandler {
        acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
        onWheel: event => {
            const step = GlobalConfig.services.audioIncrement || 0.05;
            if (event.angleDelta.y !== 0)
                root.setVolumeLevel(root.currentVolume + (event.angleDelta.y > 0 ? step : -step));
        }
    }
}
