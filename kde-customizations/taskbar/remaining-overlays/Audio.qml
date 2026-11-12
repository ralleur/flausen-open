pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Services.Pipewire
import Caelestia.Config
import Caelestia.Services
import qs.components
import qs.components.controls
import qs.services
import qs.utils

ColumnLayout {
    id: root

    required property PopoutState popouts

    property real scaleOffset: 1.0
    property real fontScale: 1.0
    property bool _isSidebarOpen: false
    readonly property real bodyPointSize: MenuStyle.bodyPointSize(root.fontScale)
    readonly property real titlePointSize: root.bodyPointSize * 1.68
    readonly property real contentInset: 7 * root.scaleOffset
    property bool _outputsOpen: false
    property bool _inputsOpen: false
    readonly property var player: Players.active

    function deviceName(node, fallback): string {
        return node ? (node.properties?.["node.nick"] || node.description || node.name) : fallback;
    }

    function outputIcon(node: PwNode): string {
        const name = (node?.description || node?.name || "").toLowerCase();
        return /headset|headphone|earbud|earphone/.test(name) ? "headphones" : "speaker";
    }

    function sourceIcon(node: PwNode): string {
        return (node?.name || "").includes("headset") ? "headset_mic" : "mic";
    }

    width: _isSidebarOpen ? Math.max(420 * scaleOffset, (Visibilities.sidebarWidthFor(Tokens.sizes.sidebar.width) * scaleOffset) - Tokens.padding.extraLargeIncreased) : 420 * scaleOffset
    implicitWidth: width
    spacing: 9 * scaleOffset

    RowLayout {
        Layout.topMargin: 3 * root.scaleOffset
        Layout.leftMargin: 20 * root.scaleOffset
        Layout.rightMargin: 14 * root.scaleOffset
        Layout.bottomMargin: 2 * root.scaleOffset
        Layout.fillWidth: true

        MenuText {
            Layout.fillWidth: true
            text: qsTr("Audio")
            font.weight: Font.DemiBold
            font.pointSize: root.titlePointSize
        }
        IconButton {
            Layout.alignment: Qt.AlignVCenter
            implicitWidth: 38 * root.scaleOffset
            implicitHeight: implicitWidth
            icon: "settings"
            font: Tokens.font.icon.medium
            type: IconButton.Tonal
            isRound: true
            inactiveColour: "transparent"
            inactiveOnColour: MenuStyle.muted
            Accessible.name: qsTr("Audio settings")
            onClicked: root.popouts.detachRequested("audio")
        }
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.leftMargin: root.contentInset
        Layout.rightMargin: root.contentInset
        spacing: 9 * root.scaleOffset

        ChannelCard {
            title: qsTr("Output")
            input: false
        }
        ChannelCard {
            title: qsTr("Input")
            input: true
        }
    }

    MenuAudioSection {
        Layout.topMargin: 1 * root.scaleOffset
        scaleOffset: root.scaleOffset
        fontScale: root.fontScale
        title: qsTr("App volumes")
        icon: "graphic_eq"

        MenuText {
            Layout.fillWidth: true
            Layout.margins: 12 * root.scaleOffset
            visible: Audio.appStreams.length === 0
            text: qsTr("No apps playing audio")
            color: MenuStyle.muted
            font.pointSize: root.bodyPointSize * 0.81
        }
        Repeater {
            model: ScriptModel { values: [...Audio.appStreams] }
            MenuAppStreamRow {
                required property PwNode modelData
                required property int index
                scaleOffset: root.scaleOffset
                fontScale: root.fontScale
                node: modelData
                muteOnIconClick: true
                first: index === 0
                last: index === Audio.appStreams.length - 1
            }
        }
    }

    MenuAudioSection {
        scaleOffset: root.scaleOffset
        fontScale: root.fontScale
        title: qsTr("Now playing")
        icon: "music_note"

        ColumnLayout {
            Layout.fillWidth: true
            Layout.margins: 12 * root.scaleOffset
            spacing: 6 * root.scaleOffset
            MenuText {
                Layout.fillWidth: true
                text: root.player?.trackTitle || qsTr("No media playing")
                wrapMode: Text.Wrap
                font.pointSize: root.bodyPointSize
            }
            MenuText {
                Layout.fillWidth: true
                visible: text !== ""
                text: root.player?.trackArtist || ""
                wrapMode: Text.Wrap
                color: MenuStyle.muted
                font.pointSize: root.bodyPointSize * 0.81
            }
            RowLayout {
                Layout.alignment: Qt.AlignHCenter
                visible: !!root.player
                IconButton {
                    icon: "skip_previous"
                    enabled: root.player?.canGoPrevious ?? false
                    onClicked: root.player?.previous()
                }
                IconButton {
                    icon: root.player?.isPlaying ? "pause" : "play_arrow"
                    enabled: root.player?.canTogglePlaying ?? false
                    onClicked: root.player?.togglePlaying()
                }
                IconButton {
                    icon: "skip_next"
                    enabled: root.player?.canGoNext ?? false
                    onClicked: root.player?.next()
                }
            }
        }
    }

    component ChannelCard: Rectangle {
        id: channel
        required property string title
        required property bool input
        readonly property var node: input ? Audio.source : Audio.sink
        readonly property real volume: input ? Audio.sourceVolume : Audio.volume
        readonly property bool muted: input ? Audio.sourceMuted : Audio.muted
        readonly property color accent: input ? (Colours.light ? "#c64836" : "#ff745f") : (Colours.light ? "#248a4b" : "#55d084")
        readonly property bool devicesOpen: input ? root._inputsOpen : root._outputsOpen
        readonly property var devices: input ? Audio.sources : Audio.sinks
        function setVolume(value: real): void {
            if (input) Audio.setSourceVolume(value);
            else Audio.setVolume(value);
        }
        function toggleDevices(): void {
            if (input) root._inputsOpen = !root._inputsOpen;
            else root._outputsOpen = !root._outputsOpen;
        }

        Layout.fillWidth: true
        Layout.preferredWidth: 0
        Layout.alignment: Qt.AlignTop
        implicitHeight: channelColumn.implicitHeight + 24 * root.scaleOffset
        radius: 14 * root.scaleOffset
        color: MenuStyle.cardFill
        border.width: 1
        border.color: MenuStyle.rule

        ColumnLayout {
            id: channelColumn
            x: 12 * root.scaleOffset
            y: 12 * root.scaleOffset
            width: parent.width - 24 * root.scaleOffset
            spacing: 10 * root.scaleOffset

            MenuText {
                Layout.fillWidth: true
                Layout.leftMargin: 4 * root.scaleOffset
                text: channel.title
                font.pointSize: root.bodyPointSize
                font.weight: Font.DemiBold
            }
            Rectangle {
                objectName: channel.input ? "audioInputDevice" : "audioOutputDevice"
                activeFocusOnTab: channel.devices.length > 1
                Accessible.role: Accessible.Button
                Accessible.name: root.deviceName(channel.node, channel.input ? qsTr("No input device") : qsTr("No output device"))
                Keys.onSpacePressed: channel.toggleDevices()
                Keys.onReturnPressed: channel.toggleDevices()
                Layout.fillWidth: true
                implicitHeight: Math.max(48 * root.scaleOffset, root.bodyPointSize * 4 / 3 * 0.9 * 2.5 + 10 * root.scaleOffset)
                radius: 10 * root.scaleOffset
                color: MenuStyle.cardFill
                border.width: 1
                border.color: MenuStyle.rule
                RowLayout {
                    id: deviceRow
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.margins: 6 * root.scaleOffset
                    spacing: 6 * root.scaleOffset
                    Rectangle {
                        implicitWidth: 30 * root.scaleOffset
                        implicitHeight: implicitWidth
                        radius: 9 * root.scaleOffset
                        color: Qt.alpha(MenuStyle.accent, 0.22)
                        MaterialIcon {
                            anchors.centerIn: parent
                            text: channel.input ? root.sourceIcon(channel.node) : root.outputIcon(channel.node)
                            color: MenuStyle.ink
                            fontStyle.pointSize: 18 * root.scaleOffset
                        }
                    }
                    MenuText {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 0
                        text: root.deviceName(channel.node, channel.input ? qsTr("No input device") : qsTr("No output device"))
                        font.pointSize: root.bodyPointSize * 0.81
                        wrapMode: Text.Wrap
                        maximumLineCount: 2
                        elide: Text.ElideRight
                    }
                    MaterialIcon {
                        text: "expand_more"
                        rotation: channel.devicesOpen ? 180 : 0
                        color: channel.devices.length > 1 ? MenuStyle.muted : Qt.alpha(MenuStyle.muted, 0.4)
                        Layout.preferredWidth: 14 * root.scaleOffset
                        fontStyle.pointSize: 12 * root.scaleOffset
                    }
                }
                StateLayer {
                    anchors.fill: parent
                    radius: parent.radius
                    disabled: channel.devices.length < 2
                    onClicked: channel.toggleDevices()
                }
            }
            ColumnLayout {
                Layout.fillWidth: true
                visible: channel.devicesOpen
                spacing: 2 * root.scaleOffset
                Repeater {
                    model: channel.devicesOpen ? channel.devices : []
                    AudioDevice {
                        isInput: channel.input
                        active: channel.node?.id === modelData.id
                        onSelected: {
                            if (channel.input) Audio.setAudioSource(modelData);
                            else Audio.setAudioSink(modelData);
                            channel.toggleDevices();
                        }
                    }
                }
            }
            IconButton {
                objectName: channel.input ? "audioInputMute" : "audioOutputMute"
                Layout.alignment: Qt.AlignHCenter
                Layout.topMargin: 1 * root.scaleOffset
                implicitWidth: 43 * root.scaleOffset
                implicitHeight: implicitWidth
                icon: channel.input ? Icons.getMicVolumeIcon(channel.volume, channel.muted) : Icons.getVolumeIcon(channel.volume, channel.muted)
                font: Qt.font({family: Tokens.font.icon.medium.family, pointSize: 22 * root.scaleOffset})
                isRound: true
                enabled: !!channel.node?.ready
                Accessible.name: channel.input ? qsTr("Mute microphone") : qsTr("Mute output")
                inactiveColour: Qt.alpha(channel.accent, channel.muted ? 0.08 : 0.18)
                inactiveOnColour: channel.muted ? MenuStyle.muted : MenuStyle.ink
                onClicked: {
                    if (channel.node?.ready && channel.node?.audio)
                        channel.node.audio.muted = !channel.node.audio.muted;
                }
            }
            Item {
                id: level
                objectName: channel.input ? "audioInputVolume" : "audioOutputVolume"
                Layout.alignment: Qt.AlignHCenter
                implicitWidth: 64 * root.scaleOffset
                implicitHeight: 214 * root.scaleOffset
                enabled: !!channel.node?.ready
                activeFocusOnTab: enabled
                readonly property int segments: 24
                readonly property int filled: Math.round(Math.max(0, Math.min(1, channel.volume)) * segments)
                function updateAt(y: real): void {
                    channel.setVolume(Math.max(0, Math.min(1, 1 - y / height)));
                }
                Keys.onPressed: event => {
                    const step = GlobalConfig.services.audioIncrement;
                    if ([Qt.Key_Up, Qt.Key_Right, Qt.Key_Down, Qt.Key_Left, Qt.Key_Home, Qt.Key_End].includes(event.key)) {
                        channel.setVolume(event.key === Qt.Key_Home ? 0 : event.key === Qt.Key_End ? 1 : Math.max(0, Math.min(1, channel.volume + ([Qt.Key_Up, Qt.Key_Right].includes(event.key) ? step : -step))));
                        event.accepted = true;
                    }
                }
                Accessible.role: Accessible.Slider
                Accessible.name: channel.input ? qsTr("Input volume") : qsTr("Output volume")
                Accessible.description: Math.round(channel.volume * 100) + "%"
                Column {
                    anchors.centerIn: parent
                    spacing: 3 * root.scaleOffset
                    Repeater {
                        model: level.segments
                        Rectangle {
                            required property int index
                            width: 35 * root.scaleOffset
                            height: (level.height - 23 * 3 * root.scaleOffset) / 24
                            radius: 2 * root.scaleOffset
                            color: index >= level.segments - level.filled && !channel.muted && level.enabled ? channel.accent : Qt.alpha(MenuStyle.muted, 0.3)
                            Rectangle {
                                anchors.fill: parent
                                anchors.margins: -2 * root.scaleOffset
                                visible: !!channel.node && index === level.segments - Math.max(1, level.filled)
                                radius: 3 * root.scaleOffset
                                color: "transparent"
                                border.width: level.activeFocus ? 2 : 1
                                border.color: level.activeFocus ? MenuStyle.accent : MenuStyle.ink
                            }
                        }
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    preventStealing: true
                    onPressed: mouse => { level.forceActiveFocus(); level.updateAt(mouse.y); }
                    onPositionChanged: mouse => { if (pressed) level.updateAt(mouse.y); }
                    onReleased: { if (!channel.input) Audio.playEffectTick(); }
                    onWheel: event => {
                        const delta = event.angleDelta.y || event.angleDelta.x;
                        if (delta) channel.setVolume(Math.max(0, Math.min(1, channel.volume + (delta > 0 ? 1 : -1) * GlobalConfig.services.audioIncrement)));
                        event.accepted = true;
                    }
                }
            }
            MenuText {
                Layout.alignment: Qt.AlignHCenter
                text: channel.node ? Math.round(channel.volume * 100) + "%" : "—"
                color: channel.node && !channel.muted ? MenuStyle.ink : MenuStyle.muted
                font.pointSize: root.bodyPointSize * 1.3
                Accessible.description: channel.muted ? qsTr("Muted") : ""
            }
        }
    }

    component AudioDevice: StyledRect {
        id: device
        objectName: "audioDeviceChoice-" + modelData.id

        required property PwNode modelData
        property bool isInput: false
        property bool active: false

        activeFocusOnTab: true
        Accessible.role: Accessible.RadioButton
        Accessible.name: root.deviceName(modelData, qsTr("Unknown"))
        Accessible.checked: active
        Keys.onSpacePressed: selected()
        Keys.onReturnPressed: selected()
        signal selected

        Layout.fillWidth: true
        Layout.preferredWidth: 0
        implicitHeight: Math.max(44 * root.scaleOffset, row.implicitHeight + 16 * root.scaleOffset)
        radius: Tokens.rounding.small * root.scaleOffset
        color: device.active || device.activeFocus ? Qt.alpha(MenuStyle.accent, 0.08) : "transparent"

        RowLayout {
            id: row

            anchors.left: parent.left
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 6 * root.scaleOffset
            anchors.rightMargin: 6 * root.scaleOffset
            spacing: 6 * root.scaleOffset

            MenuText {
                Layout.fillWidth: true
                Layout.preferredWidth: 0
                wrapMode: Text.Wrap
                maximumLineCount: 3
                elide: Text.ElideRight
                text: device.modelData?.properties?.["node.nick"] || device.modelData?.description || device.modelData?.name || qsTr("Unknown")
                color: device.active ? MenuStyle.ink : MenuStyle.muted
                font.pointSize: root.bodyPointSize * 0.79
            }

            MaterialIcon {
                text: device.active ? "check_circle" : "radio_button_unchecked"
                color: device.active ? Colours.palette.m3primary : MenuStyle.muted
                fontStyle.pointSize: 14 * root.scaleOffset
            }
        }

        StateLayer {
            anchors.fill: parent
            radius: device.radius
            onClicked: device.selected()
        }
    }
}

