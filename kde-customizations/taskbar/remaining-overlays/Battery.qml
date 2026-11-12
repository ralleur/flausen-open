pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Quickshell.Services.UPower
import Caelestia.Config
import qs.components
import qs.services

ColumnLayout {
    id: root

    required property PopoutState popouts
    property real scaleOffset: 1.0
    property real fontScale: 1.0
    readonly property real bodyPointSize: MenuStyle.bodyPointSize(root.fontScale)
    readonly property real titlePointSize: root.bodyPointSize * 1.68
    readonly property real contentInset: 7 * root.scaleOffset
    property bool _isSidebarOpen: false

    // PowerProfiles.degradationReason is an enum; printing it directly showed the
    // enum member name ("HighTemperature") rather than something a user reads.
    function perfDegradationToString(p: int): string {
        switch (p) {
        case PerformanceDegradationReason.HighTemperature:
            return qsTr("The device is too hot");
        case PerformanceDegradationReason.LapDetected:
            return qsTr("The device is on a lap");
        default:
            return qsTr("Unknown reason");
        }
    }

    width: Math.max(420 * scaleOffset, _isSidebarOpen ? (Visibilities.sidebarWidthFor(Tokens.sizes.sidebar.width) * scaleOffset) - Tokens.padding.extraLargeIncreased : 0)
    implicitWidth: width
    spacing: 10 * scaleOffset

    MenuText {
        Layout.topMargin: 3 * root.scaleOffset
        Layout.leftMargin: 12 * root.scaleOffset
        text: qsTr("Battery")
        font.weight: 600
        font.pointSize: root.titlePointSize
    }

    StyledRect {
        Layout.fillWidth: true
        Layout.leftMargin: root.contentInset
        Layout.rightMargin: root.contentInset
        border.width: 1
        border.color: MenuStyle.rule
        implicitWidth: cardLayout.implicitWidth + Tokens.padding.medium * 2 * root.scaleOffset
        implicitHeight: cardLayout.implicitHeight + Tokens.padding.medium * 2 * root.scaleOffset
        radius: 14 * root.scaleOffset
        color: MenuStyle.cardFill
        clip: true

        ColumnLayout {
            id: cardLayout

            width: parent.width - Tokens.padding.medium * 2 * root.scaleOffset
            x: Tokens.padding.medium * root.scaleOffset
            y: Tokens.padding.medium * root.scaleOffset
            spacing: Tokens.spacing.large * root.scaleOffset

            RowLayout {
                Layout.fillWidth: true
                spacing: Tokens.spacing.large * root.scaleOffset

                Item {
                    id: batteryIllustration
                    Layout.preferredWidth: 60 * root.scaleOffset
                    Layout.preferredHeight: 110 * root.scaleOffset
                    Layout.alignment: Qt.AlignVCenter

                    Rectangle {
                        id: nub
                        visible: UPower.displayDevice.isLaptopBattery

                        width: 24 * root.scaleOffset
                        height: 10 * root.scaleOffset
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                        color: Colours.palette.m3primary
                        radius: Tokens.rounding.small

                        Rectangle {
                            width: parent.width
                            height: parent.radius
                            anchors.bottom: parent.bottom
                            color: parent.color
                        }
                    }

                    Item {
                        id: batteryBody
                        visible: UPower.displayDevice.isLaptopBattery

                        anchors.top: parent.top
                        anchors.topMargin: 8 * root.scaleOffset
                        anchors.bottom: parent.bottom
                        anchors.left: parent.left
                        anchors.right: parent.right

                        Item {
                            id: liquidContainer

                            anchors.bottom: parent.bottom
                            anchors.left: parent.left
                            anchors.right: parent.right

                            height: parent.height * (UPower.displayDevice.isLaptopBattery ? UPower.displayDevice.percentage : 0)

                            Behavior on height {
                                Anim { type: Anim.FastSpatial }
                            }

                            Rectangle {
                                anchors.top: parent.top
                                anchors.topMargin: waveLayer.opacity * Math.min(24, parent.height)
                                anchors.bottom: parent.bottom
                                anchors.left: parent.left
                                anchors.right: parent.right

                                color: Colours.palette.m3primary

                                bottomLeftRadius: Tokens.rounding.medium - 3
                                bottomRightRadius: Tokens.rounding.medium - 3
                                topLeftRadius: height >= batteryBody.height - 3 ? Tokens.rounding.medium - 3 : 0
                                topRightRadius: height >= batteryBody.height - 3 ? Tokens.rounding.medium - 3 : 0
                            }

                            Item {
                                id: waveLayer

                                anchors.top: parent.top
                                anchors.left: parent.left
                                anchors.right: parent.right
                                height: Math.min(25, parent.height)
                                clip: true

                                opacity: {
                                    if (UPower.onBattery) return 0;
                                    if (parent.height <= 30) return 0;
                                    if (parent.height < 40) return (parent.height - 30) / 10.0;
                                    return 1.0;
                                }

                                Behavior on opacity { Anim { type: Anim.SlowEffects } }

                                Rectangle {
                                    width: 140 * root.scaleOffset; height: 140 * root.scaleOffset
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    y: 8 * root.scaleOffset

                                    color: Colours.palette.m3primary
                                    radius: 50 * root.scaleOffset

                                    RotationAnimation on rotation {
                                        loops: Animation.Infinite
                                        from: 0; to: 360
                                        duration: 4000
                                        running: waveLayer.opacity > 0 && Tokens.anim.enabled
                                    }
                                }
                            }
                        }

                        Rectangle {
                            anchors.fill: parent
                            color: "transparent"
                            border.color: Colours.palette.m3primary
                            border.width: 3 * root.scaleOffset
                            radius: 14 * root.scaleOffset
                        }

                        MaterialIcon {
                            anchors.centerIn: parent
                            text: "bolt"
                            visible: !UPower.onBattery
                            color: Colours.palette.m3onPrimary
                            fontStyle.pointSize: Tokens.font.icon.large.pointSize * root.scaleOffset
                            z: 1
                        }
                    }
                    MaterialIcon {
                        anchors.centerIn: parent
                        visible: !UPower.displayDevice.isLaptopBattery
                        text: "power"
                        color: MenuStyle.muted
                        fontStyle.pointSize: Tokens.font.icon.extraLarge.pointSize * root.scaleOffset
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignVCenter
                    spacing: Tokens.spacing.small * root.scaleOffset

                    MenuText {
                        text: UPower.displayDevice.isLaptopBattery ? qsTr("%1%").arg(Math.round(UPower.displayDevice.percentage * 100)) : qsTr("AC power")
                        font.pointSize: root.bodyPointSize * 2.25
                        font.weight: 600
                    }

                    MenuText {
                        text: {
                            if (!UPower.displayDevice.isLaptopBattery)
                                return qsTr("No battery detected");

                            if (UPower.onBattery)
                                return qsTr("~ %1").arg(Units.formatDurationShort(UPower.displayDevice.timeToEmpty, "Calculating..."));

                            if (UPower.displayDevice.state === UPowerDeviceState.FullyCharged || UPower.displayDevice.percentage >= 1.0)
                                return qsTr("Fully charged!");

                            return qsTr("~ %1").arg(Units.formatDurationShort(UPower.displayDevice.timeToFull, "Calculating..."));
                        }
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        color: MenuStyle.muted
                        font.pointSize: root.bodyPointSize
                    }
                }
            }

            Loader {
                asynchronous: true
                Layout.fillWidth: true

                active: PowerProfiles.degradationReason !== PerformanceDegradationReason.None

                sourceComponent: StyledRect {
                    implicitWidth: child.implicitWidth + Tokens.padding.medium * 2 * root.scaleOffset
                    implicitHeight: child.implicitHeight + Tokens.padding.small * 2 * root.scaleOffset

                    color: Colours.palette.m3error
                    radius: Tokens.rounding.large * root.scaleOffset

                    Column {
                        id: child

                        anchors.centerIn: parent

                        Row {
                            anchors.horizontalCenter: parent.horizontalCenter
                            spacing: Tokens.spacing.small * root.scaleOffset

                            MaterialIcon {
                                anchors.verticalCenter: parent.verticalCenter
                                text: "warning"
                                color: Colours.palette.m3onError
                            }

                            MenuText {
                                anchors.verticalCenter: parent.verticalCenter
                                text: qsTr("Performance degraded: %1").arg(root.perfDegradationToString(PowerProfiles.degradationReason))
                                color: Colours.palette.m3onError
                                font.pointSize: root.bodyPointSize * 0.79
                            }
                        }
                    }
                }
            }

            StyledRect {
                id: profiles

                Layout.alignment: Qt.AlignHCenter
                Layout.fillWidth: true

                property string current: {
                    const p = PowerProfiles.profile;
                    if (p === PowerProfile.PowerSaver)
                        return saver.icon;
                    if (p === PowerProfile.Performance)
                        return perf.icon;
                    return balance.icon;
                }

                implicitHeight: Math.max(saver.implicitHeight, balance.implicitHeight, perf.implicitHeight) + Tokens.padding.small * root.scaleOffset

                color: MenuStyle.cardFill
                radius: Tokens.rounding.full * root.scaleOffset

                StyledRect {
                    id: indicator
                    PrimaryControlFill {} // Capture primary material

                    color: Colours.palette.m3primary
                    radius: Tokens.rounding.full * root.scaleOffset
                    state: profiles.current

                    states: [
                        State {
                            name: saver.icon

                            Fill {
                                item: saver
                            }
                        },
                        State {
                            name: balance.icon

                            Fill {
                                item: balance
                            }
                        },
                        State {
                            name: perf.icon

                            Fill {
                                item: perf
                            }
                        }
                    ]

                    transitions: Transition {
                        AnchorAnim {}
                    }
                }

                Profile {
                    id: saver

                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: Tokens.padding.extraSmall * root.scaleOffset

                    profile: PowerProfile.PowerSaver
                    icon: "energy_savings_leaf"
                }

                Profile {
                    id: balance

                    anchors.centerIn: parent

                    profile: PowerProfile.Balanced
                    icon: "balance"
                }

                Profile {
                    id: perf

                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: parent.right
                    anchors.rightMargin: Tokens.padding.extraSmall * root.scaleOffset

                    profile: PowerProfile.Performance
                    icon: "rocket_launch"
                }
            }
        }
    }

    component Fill: AnchorChanges {
        required property Item item

        target: indicator
        anchors.left: item.left
        anchors.right: item.right
        anchors.top: item.top
        anchors.bottom: item.bottom
    }

    component Profile: Item {
        required property string icon
        required property int profile

        implicitWidth: icon.implicitHeight + Tokens.padding.small * root.scaleOffset
        implicitHeight: icon.implicitHeight + Tokens.padding.small * root.scaleOffset

        StateLayer {
            radius: Tokens.rounding.full * root.scaleOffset
            color: profiles.current === parent.icon ? Colours.palette.m3onPrimary : Colours.palette.m3onSurface
            onClicked: PowerProfiles.profile = parent.profile
        }

        MaterialIcon {
            id: icon

            anchors.centerIn: parent

            text: parent.icon
            fontStyle.pointSize: Tokens.font.icon.large.pointSize * root.scaleOffset
            color: profiles.current === text ? Colours.palette.m3onPrimary : Colours.palette.m3onSurfaceVariant
            fill: profiles.current === text ? 1 : 0

            Behavior on fill {
                Anim {
                    type: Anim.DefaultEffects
                }
            }
        }
    }
}
