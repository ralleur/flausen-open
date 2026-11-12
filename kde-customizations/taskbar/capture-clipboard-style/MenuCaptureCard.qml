pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Quickshell
import Caelestia.Components
import Caelestia.Services
import qs.modules.nexus.common
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services
import qs.utils

StyledRect {
    id: root

    required property var props
    required property DrawerVisibilities visibilities
    property real scaleOffset: 1.15
    property real fontScale: 1.15
    readonly property real bodyPointSize:MenuStyle.bodyPointSize(root.fontScale)
    readonly property bool shotMode: root.props.captureMode === "shot"
    readonly property real nonAnimHeight: btnLayout.implicitHeight + modeRow.implicitHeight + listOrControls.implicitHeight + layout.spacing * 2 + layout.anchors.margins * 2

    readonly property bool hoverLocked: captureButton.expanded || recordingButton.expanded || shortcutDialog.visible
    property int shortcutRevision: 0

    function shortcutText(name: string): string {
        root.shortcutRevision;
        return KeybindsModel.getKey(name);
    }

    function editShortcut(name: string, target: Item): void {
        shortcutDialog.shortcutName = name;
        shortcutDialog.currentKey = KeybindsModel.getKey(name);
        shortcutDialog.targetItem = target;
        shortcutDialog.open();
        captureButton.expanded = false;
    }

    Connections {
        target: KeybindsModel
        function onKeybindsChanged(): void { root.shortcutRevision++; }
    }

    KeyCaptureDialog {
        id: shortcutDialog
        appendKey: false
        allowClear: true
        onConfirm: (name, newKey) => KeybindsModel.setKey(name, newKey)
        onClear: name => KeybindsModel.setKey(name, "")
    }

    Layout.fillWidth: true
    implicitHeight: layout.implicitHeight + layout.anchors.margins * 2

    radius: Tokens.rounding.large
    color: "transparent"

    ColumnLayout {
        id: layout

        anchors.fill: parent
        anchors.margins: 12 * root.scaleOffset
        spacing: 14 * root.scaleOffset

        RowLayout {
            id: btnLayout
            Layout.fillWidth:true
            Layout.leftMargin:5*root.scaleOffset
            Layout.rightMargin:5*root.scaleOffset

            spacing: 14 * root.scaleOffset

            StyledRect {
                Layout.alignment:Qt.AlignTop
                Layout.topMargin:4*root.scaleOffset
                implicitWidth: implicitHeight
                implicitHeight: 46 * root.scaleOffset

                radius: 12 * root.scaleOffset
                color: !root.shotMode && Recorder.running ? Colours.palette.m3error : Qt.alpha(MenuStyle.accent,0.18)

                MaterialIcon {
                    id: icon

                    anchors.centerIn: parent
                    anchors.verticalCenterOffset: Centering.pixelAlign(parent.height, height)
                    text: root.shotMode ? "screenshot_region" : "screen_record"
                    color: !root.shotMode && Recorder.running ? Colours.palette.m3onError : MenuStyle.accent
                    fontStyle: Tokens.font.icon.builders.medium.size(Tokens.font.icon.medium.pointSize*root.scaleOffset).build()
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 0

                MenuText {
                    Layout.fillWidth: true
                    text: qsTr("Screen Capture")
                    font.pointSize: root.bodyPointSize*1.65
                    font.weight: Font.DemiBold
                    wrapMode:Text.WordWrap
                }

                MenuText {
                    Layout.fillWidth: true
                    text: root.shotMode ? qsTr("Capture, OCR and image search") : Recorder.paused ? qsTr("Paused") : Recorder.running ? qsTr("Running...") : qsTr("Ready")
                    color: MenuStyle.muted
                    font.pointSize: root.bodyPointSize*0.81
                    wrapMode:Text.WordWrap
                    animate: true
                }
            }

            MenuCaptureSplitButton {
                id: recordingButton
                fontScale:root.fontScale
                scaleOffset:root.scaleOffset
                Layout.alignment:Qt.AlignTop
                Layout.topMargin:4*root.scaleOffset
                visible: !root.shotMode
                disabled: Recorder.running

                active: menuItems.find(m => root.props.recordingMode === m.icon + m.text) ?? menuItems[0]
                menu.onItemSelected: item => root.props.recordingMode = item.icon + item.text

                menuItems: [
                    MenuItem {
                        icon: "fullscreen"
                        text: qsTr("Record")
                        activeText: qsTr("Start")
                        onClicked: {
                            root.visibilities.utilities = false;
                            Recorder.start();
                        }
                    },
                    MenuItem {
                        icon: "volume_up"
                        text: qsTr("Record with Sound")
                        activeText: qsTr("Start")
                        onClicked: {
                            root.visibilities.utilities = false;
                            Recorder.start(["-s"]);
                        }
                    },
                    MenuItem {
                        icon: "mic"
                        text: qsTr("Record with Microphone")
                        activeText: qsTr("Start")
                        onClicked: {
                            root.visibilities.utilities = false;
                            Recorder.start(["-i"]);
                        }
                    },
                    MenuItem {
                        icon: "select_to_speak"
                        text: qsTr("Both Sound & Microphone")
                        activeText: qsTr("Start")
                        onClicked: {
                            root.visibilities.utilities = false;
                            Recorder.start(["-s", "-i"]);
                        }
                    },
                    MenuItem {
                        visible: Config.utilities.showGifRecorder
                        icon: "animated_images"
                        text: qsTr("Record GIF")
                        activeText: qsTr("Start")
                        onClicked: {
                            root.visibilities.utilities = false;
                            Recorder.startGif();
                        }
                    },
                    MenuItem {
                        icon: "screenshot_region"
                        text: qsTr("Use Spectacle")
                        activeText: qsTr("Spectacle")
                        onClicked: {
                            root.visibilities.utilities = false;
                            Recorder.launchSpectacle();
                        }
                    }
                ]
            }

            MenuCaptureSplitButton {
                fontScale:root.fontScale
                scaleOffset:root.scaleOffset
                Layout.alignment:Qt.AlignTop
                Layout.topMargin:4*root.scaleOffset
                id: captureButton
                menu.constrainToWindow: true
                menu.maxHeight: 480
                visible: root.shotMode

                active: captureShotItem

                menuItems: [
                    MenuItem {
                        id: captureShotItem

                        icon: "screenshot_region"
                        text: qsTr("Capture region")
                        shortcutName: "screenshot"
                        shortcutText: root.shortcutText(shortcutName)
                        onEditShortcut: target => root.editShortcut(shortcutName, target)
                        activeText: qsTr("Capture")
                        onClicked: {
                            root.visibilities.utilities = false;
                            if (!Visibilities.sidebarPinned)
                                root.visibilities.sidebar = false;
                            Quickshell.execDetached(["qs", "-c", "caelestia", "ipc", "call", "region", "screenshot"]);
                        }
                    },
                    MenuItem {
                        icon: "fullscreen"
                        text: qsTr("Capture fullscreen")
                        shortcutName: "captureFullscreen"
                        shortcutText: root.shortcutText(shortcutName)
                        onEditShortcut: target => root.editShortcut(shortcutName, target)
                        activeText: qsTr("Fullscreen")
                        onClicked: {
                            root.visibilities.utilities = false;
                            if (!Visibilities.sidebarPinned)
                                root.visibilities.sidebar = false;
                            const pad = n => String(n).padStart(2, "0");
                            const now = new Date();
                            const file = `${GlobalConfig.paths.screenshotsDir}/screenshot-${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}_${pad(now.getHours())}.${pad(now.getMinutes())}.${pad(now.getSeconds())}.png`;
                            Quickshell.execDetached(["spectacle", "-b", "-f", "-o", file]);
                        }
                    },
                    MenuItem {
                        icon: "select_window"
                        text: qsTr("Capture active window")
                        shortcutName: "captureActiveWindow"
                        shortcutText: root.shortcutText(shortcutName)
                        onEditShortcut: target => root.editShortcut(shortcutName, target)
                        activeText: qsTr("Window")
                        onClicked: {
                            root.visibilities.utilities = false;
                            if (!Visibilities.sidebarPinned)
                                root.visibilities.sidebar = false;
                            const pad2 = n => String(n).padStart(2, "0");
                            const now2 = new Date();
                            const file2 = `${GlobalConfig.paths.screenshotsDir}/screenshot-${now2.getFullYear()}-${pad2(now2.getMonth() + 1)}-${pad2(now2.getDate())}_${pad2(now2.getHours())}.${pad2(now2.getMinutes())}.${pad2(now2.getSeconds())}.png`;
                            Quickshell.execDetached(["spectacle", "-b", "-a", "-o", file2]);
                        }
                    },
                    MenuItem {
                        icon: "text_fields"
                        text: qsTr("Recognize text")
                        shortcutName: "ocr"
                        shortcutText: root.shortcutText(shortcutName)
                        onEditShortcut: target => root.editShortcut(shortcutName, target)
                        activeText: qsTr("Recognize")
                        onClicked: {
                            root.visibilities.utilities = false;
                            if (!Visibilities.sidebarPinned)
                                root.visibilities.sidebar = false;
                            Quickshell.execDetached(["qs", "-c", "caelestia", "ipc", "call", "region", "ocr"]);
                        }
                    },
                    MenuItem {
                        icon: "image_search"
                        text: qsTr("Search image")
                        shortcutName: "googleLens"
                        shortcutText: root.shortcutText(shortcutName)
                        onEditShortcut: target => root.editShortcut(shortcutName, target)
                        activeText: qsTr("Search")
                        onClicked: {
                            root.visibilities.utilities = false;
                            if (!Visibilities.sidebarPinned)
                                root.visibilities.sidebar = false;
                            Quickshell.execDetached(["qs", "-c", "caelestia", "ipc", "call", "region", "search"]);
                        }
                    },
                    MenuItem {
                        icon: "screenshot_monitor"
                        text: qsTr("Use Spectacle")
                        shortcutName: "captureSpectacle"
                        shortcutText: root.shortcutText(shortcutName)
                        onEditShortcut: target => root.editShortcut(shortcutName, target)
                        activeText: qsTr("Spectacle")
                        onClicked: {
                            root.visibilities.utilities = false;
                            if (!Visibilities.sidebarPinned)
                                root.visibilities.sidebar = false;
                            Quickshell.execDetached(["spectacle"]);
                        }
                    }
                ]
            }
        }

        Rectangle {
            id: modeRow
            Layout.preferredWidth: Math.min(layout.width, 316 * root.scaleOffset)
            implicitHeight: Math.max(40 * root.scaleOffset, modeOptions.implicitHeight + 4)
            radius: 13 * root.scaleOffset
            color: MenuStyle.cardFill
            border.width: 1
            border.color: MenuStyle.border
            RowLayout {
                id: modeOptions
                anchors.fill: parent
                anchors.margins: 3
                spacing: 3
                Repeater {
                    model: [ { label: qsTr("Screenshot"), icon: "photo_camera", mode: "shot" },
                             { label: qsTr("Recording"), icon: "videocam", mode: "record" } ]
                    delegate: Rectangle {
                        required property var modelData
                        readonly property bool selected: root.props.captureMode === modelData.mode
                        Layout.fillWidth: true
                        implicitHeight: Math.max(34 * root.scaleOffset, optionLabel.implicitHeight + 14)
                        radius: 10 * root.scaleOffset
                        color: selected ? Qt.alpha(MenuStyle.accent, 0.24) : "transparent"
                        border.width: selected ? 1 : 0
                        border.color: Qt.alpha(MenuStyle.primaryEdge, 0.42)
                        RowLayout {
                            anchors.centerIn: parent
                            spacing: 9 * root.scaleOffset
                            MaterialIcon { text: modelData.icon; color: MenuStyle.ink }
                            MenuText { id: optionLabel; text: modelData.label; font.pointSize: root.bodyPointSize }
                        }
                        StateLayer { onClicked: root.props.captureMode = modelData.mode }
                    }
                }
            }
            WheelHandler {
                acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                onWheel: event => {
                    const d = event.angleDelta.y || event.angleDelta.x;
                    if (d) root.props.captureMode = d < 0 ? "shot" : "record";
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 1
            color: MenuStyle.rule
        }

        Loader {
            id: listOrControls

            property bool running: !root.shotMode && Recorder.running

            asynchronous: true
            Layout.fillWidth: true
            Layout.preferredHeight: implicitHeight
            sourceComponent: running ? recordingControls : root.shotMode ? screenshotList : recordingList
            clip: Layout.preferredHeight < implicitHeight

            Behavior on Layout.preferredHeight {
                id: locHeightAnim

                enabled: false

                Anim {}
            }

            Behavior on running {
                SequentialAnimation {
                    Anim {
                        target: listOrControls
                        property: "opacity"
                        to: 0
                        type: Anim.DefaultEffects
                    }
                    PropertyAction {
                        target: locHeightAnim
                        property: "enabled"
                        value: true
                    }
                    PropertyAction {}
                    ParallelAnimation {
                        SequentialAnimation {
                            PauseAnimation {
                                duration: 100
                            }
                            PropertyAction {
                                target: locHeightAnim
                                property: "enabled"
                                value: false
                            }
                        }
                        Anim {
                            target: listOrControls
                            property: "opacity"
                            to: 1
                            type: Anim.SlowEffects
                        }
                    }
                }
            }
        }
    }

    Component {
        id: recordingList

        MenuRecordingList {
            scaleOffset:root.scaleOffset
            fontScale:root.fontScale
            props: root.props
            visibilities: root.visibilities
        }
    }

    Component {
        id: screenshotList

        MenuScreenshotList {
            scaleOffset:root.scaleOffset
            fontScale:root.fontScale
            props: root.props
            visibilities: root.visibilities
        }
    }

    Component {
        id: recordingControls

        RowLayout {
            spacing: 14 * root.scaleOffset

            StyledRect {
                radius: Tokens.rounding.full
                color: Recorder.paused ? Colours.palette.m3tertiary : Colours.palette.m3error

                implicitWidth: recText.implicitWidth + Tokens.padding.medium * 2
                implicitHeight: recText.implicitHeight + Tokens.padding.large

                MenuText {
                    id: recText

                    anchors.centerIn: parent
                    animate: true
                    text: Recorder.paused ? "PAUSED" : "REC"
                    color: Recorder.paused ? Colours.palette.m3onTertiary : Colours.palette.m3onError
                    font.pointSize: root.bodyPointSize*0.81
                }

                Behavior on implicitWidth {
                    Anim {}
                }

                SequentialAnimation on opacity {
                    running: !Recorder.paused && Tokens.anim.enabled
                    alwaysRunToEnd: true
                    loops: Animation.Infinite

                    Anim {
                        from: 1
                        to: 0
                        duration: Tokens.anim.durations.large
                        easing: Tokens.anim.emphasizedAccel
                    }
                    Anim {
                        from: 0
                        to: 1
                        duration: Tokens.anim.durations.extraLarge
                        easing: Tokens.anim.emphasizedDecel
                    }
                }
            }

            MenuText {
                Layout.fillWidth: true
                text: qsTr("Recording %1").arg(Units.formatDuration(Recorder.elapsed))
                font.pointSize: root.bodyPointSize
                elide: Text.ElideMiddle
            }

            ButtonRow {
                spacing: Tokens.spacing.extraSmall

                IconButton {
                    shapeMorph: true
                    isRound: true
                    label.animate: true
                    icon: Recorder.paused ? "play_arrow" : "pause"
                    isToggle: true
                    checked: Recorder.paused
                    type: IconButton.Tonal
                    font: Tokens.font.icon.medium
                    onClicked: {
                        Recorder.togglePause();
                        internalChecked = Recorder.paused;
                    }

                    implicitWidth: {
                        const h = label.implicitHeight + Tokens.padding.large * 2;
                        if (h % 2 !== 0)
                            return h + 1;
                        return h;
                    }
                }

                IconButton {
                    shapeMorph: true
                    isRound: true
                    icon: "stop"
                    inactiveColour: Colours.palette.m3error
                    inactiveOnColour: Colours.palette.m3onError
                    font: Tokens.font.icon.medium
                    onClicked: Recorder.stop()

                    implicitWidth: {
                        const h = label.implicitHeight + Tokens.padding.large * 2;
                        if (h % 2 !== 0)
                            return h + 1;
                        return h;
                    }
                }
            }
        }
    }
}
