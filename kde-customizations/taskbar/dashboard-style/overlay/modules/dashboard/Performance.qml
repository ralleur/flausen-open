import "performance"
import QtQuick
import QtQuick.Layouts
import Quickshell.Services.UPower
import Caelestia.Config
import Caelestia.Services
import qs.components
import qs.services

Item {
    id: root

    // Compact mode for embedding (e.g. bar popout): tighter fixed cards.
    // Defaults to false, so the dashboard is untouched.
    property bool compact: false

    implicitWidth: placeholder.active ? Tokens.sizes.dashboard.perfPlaceholderWidth : content.implicitWidth
    implicitHeight: placeholder.active ? placeholder.implicitHeight + Tokens.padding.extraLarge * 2 : content.implicitHeight

    Loader {
        id: placeholder

        anchors.centerIn: parent
        active: !Config.dashboard.performance.showCpu && !(Config.dashboard.performance.showGpu && Gpu.type !== Gpu.None) && !Config.dashboard.performance.showMemory && !Config.dashboard.performance.showStorage && !(UPower.displayDevice.isLaptopBattery && Config.dashboard.performance.showBattery)
        asynchronous: true

        sourceComponent: ColumnLayout {
            spacing: Tokens.spacing.medium

            MaterialIcon {
                Layout.alignment: Qt.AlignHCenter
                text: "tune"
                fontStyle: Tokens.font.icon.builders.extraLarge.scale(2).build()
                color: MenuStyle.muted
            }

            MenuText {
                Layout.topMargin: -Tokens.spacing.small
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("No widgets enabled")
                font: MenuStyle.withSystemFamily(Tokens.font.title.large)
                color: MenuStyle.ink
            }

            MenuText {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("Enable widgets in the dashboard settings")
                font: MenuStyle.withSystemFamily(Tokens.font.body.small)
                color: MenuStyle.muted
            }
        }
    }

    RowLayout {
        id: content

        anchors.left: parent.left
        anchors.right: parent.right
        spacing: Tokens.spacing.medium
        visible: !placeholder.active

        ColumnLayout {
            id: mainColumn

            Layout.fillWidth: true
            spacing: Tokens.spacing.medium

            RowLayout {
                spacing: Tokens.spacing.medium
                visible: cpuCard.active || gpuCard.active

                WrappedLoader {
                    id: cpuCard

                    active: Config.dashboard.performance.showCpu

                    sourceComponent: HeroCard {
                        cardWidth: root.compact ? 340 : Tokens.sizes.dashboard.perfHeroCardWidth
                        icon: "memory"
                        label: qsTr("CPU")
                        subLabel: Cpu.name
                        usage: Cpu.percentage
                        temperature: Cpu.temperature
                        accent: Colours.palette.m3primary

                        ServiceRef {
                            service: Cpu
                        }
                    }
                }

                WrappedLoader {
                    id: gpuCard

                    active: Config.dashboard.performance.showGpu && Gpu.type !== Gpu.None

                    sourceComponent: HeroCard {
                        cardWidth: root.compact ? 340 : Tokens.sizes.dashboard.perfHeroCardWidth
                        icon: "desktop_windows"
                        label: qsTr("GPU")
                        subLabel: Gpu.name
                        usage: Gpu.percentage
                        temperature: Gpu.temperature
                        accent: Colours.palette.m3secondary

                        ServiceRef {
                            service: Gpu
                        }
                    }
                }
            }

            RowLayout {
                spacing: Tokens.spacing.medium
                visible: storageCard.active || memoryCard.active

                WrappedLoader {
                    id: storageCard

                    active: Config.dashboard.performance.showStorage
                    sourceComponent: StorageCard {}
                }

                WrappedLoader {
                    id: memoryCard

                    active: Config.dashboard.performance.showMemory
                    sourceComponent: MemoryCard {}
                }
            }
        }

        WrappedLoader {
            Layout.fillWidth: false
            active: UPower.displayDevice.isLaptopBattery && Config.dashboard.performance.showBattery
            sourceComponent: BatteryTank {}
        }
    }

    component WrappedLoader: Loader {
        Layout.fillWidth: true
        Layout.fillHeight: true
        visible: active
    }
}
