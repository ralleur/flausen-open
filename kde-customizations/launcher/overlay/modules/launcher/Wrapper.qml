pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Caelestia.Config
import qs.components
import qs.modules.launcher.services

Item {
    id: root

    required property ShellScreen screen
    required property DrawerVisibilities visibilities
    required property var panels
    Config.screen: root.screen.name
    readonly property real maxWidth: Math.max(0, screen.width - panels.leftMargin - panels.rightMargin - 24)
    readonly property bool shouldBeActive: visibilities.launcher && Config.launcher.enabled && !visibilities.overview
    readonly property real maxHeight: Math.max(120, screen.height - 140)
    property real offsetScale: shouldBeActive ? 0 : 1
    property bool keepAlive: false

    signal closed()

    onOffsetScaleChanged: {
        if (offsetScale >= 1 && !shouldBeActive)
            closed();
    }
    onShouldBeActiveChanged: {
        if (shouldBeActive) {
            implicitHeight = Qt.binding(() => content.implicitHeight);
        } else
            implicitHeight = implicitHeight;
    }
    clip: true
    visible: offsetScale < 1
    height: implicitHeight * (1 - offsetScale)
    implicitHeight: content.implicitHeight
    implicitWidth: content.implicitWidth || 630
    opacity: 1 - offsetScale
    Component.onCompleted: Qt.callLater(() => { Apps; HermesDesktop; })

    Timer {
        running: Config.launcher.enabled && !root.keepAlive
        interval: 1500

        onTriggered: root.keepAlive = true
    }

    Behavior on offsetScale {
        enabled: !visibilities.skipLauncherAnim

        Anim {}
    }
    Loader {
        id: content

        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        active: root.shouldBeActive || root.visible || root.keepAlive
        sourceComponent: Component {
            Content {
                visibilities: root.visibilities
                panels: root.panels
                maxWidth: root.maxWidth
                maxHeight: root.maxHeight
            }
        }
    }
}
