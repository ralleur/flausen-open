pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Quickshell
import Caelestia.Config
import qs.components

import qs.services

// Taskbar capture gallery; utilities keep their independent card.
ColumnLayout {
    id: root

    required property var popouts
    required property DrawerVisibilities visibilities

    property real scaleOffset: 1.15
    property real fontScale: 1.15
    property bool _isSidebarOpen: false
    readonly property bool hoverLocked: captureView.hoverLocked

    width: 560 * root.scaleOffset
    implicitWidth: width
    spacing: Tokens.spacing.small

    MenuCaptureCard {
        id: captureView

        Layout.fillWidth: true
        visibilities: root.visibilities
        props: cardProps
        scaleOffset:root.scaleOffset
        fontScale:root.fontScale
    }

    PersistentProperties {
        id: cardProps

        property bool screenshotListExpanded: false
        property string captureMode: "shot"
        property bool recordingListExpanded: false
        property string recordingConfirmDelete: ""
        property string recordingMode
    }
}
