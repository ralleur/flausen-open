pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Caelestia
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services
import qs.utils

Item {
    id: root

    required property Brightness.Monitor monitor
    required property DrawerVisibilities visibilities

    required property real volume
    required property bool muted
    required property real sourceVolume
    required property bool sourceMuted
    required property real brightness

    readonly property real controlWidth: 52
    readonly property real controlHeight: Math.min(226, Math.max(130, ((root.Window.window?.height ?? 1080) - 180) / 3 - 24))

    implicitWidth: controlWidth + 32
    implicitHeight: layout.implicitHeight + 32

    Rectangle {
        anchors.fill: parent
        radius: 26
        color: "#b321282d"
        border.width: 1
        border.color: "#60ffffff"
    }

    ColumnLayout {
        id: layout

        anchors.centerIn: parent
        spacing: 22

        WrappedLoader {
            Layout.alignment: Qt.AlignHCenter
            shouldBeActive: Config.osd.enableVolume !== false
            targetWidth: root.controlWidth
            targetHeight: root.controlHeight

            sourceComponent: CustomMouseArea {
                function onWheel(event: WheelEvent) {
                    if (event.angleDelta.y > 0)
                        Audio.incrementVolume();
                    else if (event.angleDelta.y < 0)
                        Audio.decrementVolume();
                }

                implicitWidth: root.controlWidth
                implicitHeight: root.controlHeight

                SegmentedSlider {
                    anchors.fill: parent

                    fillColor: "#53c67b"
                    muteEnabled: true
                    onMuteToggled: {
                        if (Audio.sink?.audio)
                            Audio.sink.audio.muted = !Audio.muted;
                    }
                    muted: root.muted
                    accessibleLabel: qsTr("Volume")
                    icon: Icons.getVolumeIcon(value, root.muted)
                    value: root.volume
                    to: GlobalConfig.services.maxVolume
                    onMoved: Audio.setVolume(value)
                }
            }
        }

        WrappedLoader {
            Layout.alignment: Qt.AlignHCenter
            shouldBeActive: Config.osd.enableMicrophone
            targetWidth: root.controlWidth
            targetHeight: root.controlHeight

            sourceComponent: CustomMouseArea {
                function onWheel(event: WheelEvent) {
                    if (event.angleDelta.y > 0)
                        Audio.incrementSourceVolume();
                    else if (event.angleDelta.y < 0)
                        Audio.decrementSourceVolume();
                }

                implicitWidth: root.controlWidth
                implicitHeight: root.controlHeight

                SegmentedSlider {
                    anchors.fill: parent

                    fillColor: "#f16f5c"
                    muteEnabled: true
                    onMuteToggled: {
                        if (Audio.source?.audio)
                            Audio.source.audio.muted = !Audio.sourceMuted;
                    }
                    muted: root.sourceMuted
                    accessibleLabel: qsTr("Microphone")
                    icon: Icons.getMicVolumeIcon(value, root.sourceMuted)
                    value: root.sourceVolume
                    to: GlobalConfig.services.maxVolume
                    onMoved: Audio.setSourceVolume(value)
                }
            }
        }

        WrappedLoader {
            Layout.alignment: Qt.AlignHCenter
            shouldBeActive: Config.osd.enableBrightness
            targetWidth: root.controlWidth
            targetHeight: root.controlHeight

            sourceComponent: CustomMouseArea {
                function onWheel(event: WheelEvent) {
                    const monitor = root.monitor;
                    if (!monitor)
                        return;
                    if (event.angleDelta.y > 0)
                        monitor.stepBrightness(GlobalConfig.services.brightnessIncrement);
                    else if (event.angleDelta.y < 0)
                        monitor.stepBrightness(-GlobalConfig.services.brightnessIncrement);
                }

                implicitWidth: root.controlWidth
                implicitHeight: root.controlHeight

                SegmentedSlider {
                    anchors.fill: parent

                    fillColor: "#efb34f"
                    accessibleLabel: qsTr("Brightness")
                    icon: "light_mode"
                    value: root.brightness
                    onMoved: root.monitor?.setBrightness(value)
                }
            }
        }
    }

    component WrappedLoader: Loader {
        required property bool shouldBeActive
        property real targetWidth: 0
        property real targetHeight: 0

        asynchronous: true
        Layout.preferredWidth: shouldBeActive ? targetWidth : 0
        Layout.preferredHeight: shouldBeActive ? targetHeight : 0
        opacity: shouldBeActive ? 1 : 0
        active: opacity > 0
        visible: active

        Behavior on Layout.preferredWidth {
            Anim {
                type: Anim.Emphasized
            }
        }

        Behavior on Layout.preferredHeight {
            Anim {
                type: Anim.Emphasized
            }
        }

        Behavior on opacity {
            Anim {
                type: Anim.DefaultEffects
            }
        }
    }
}
