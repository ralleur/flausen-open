import QtQuick
import QtQuick.Layouts
import Caelestia.Components
import Caelestia.Config
import Caelestia.Services
import qs.components
import qs.services

StyledRect {
    id: root

    property real cardWidth: Tokens.sizes.dashboard.perfNetworkCardWidth

    color: MenuStyle.cardFill
    radius: Tokens.rounding.extraLarge

    implicitWidth: root.cardWidth
    implicitHeight: Tokens.sizes.dashboard.perfNetworkCardHeight

    ServiceRef {
        service: NetworkUsage
    }

    ColumnLayout {
        id: layout

        anchors.fill: parent
        anchors.margins: Tokens.padding.large
        anchors.bottomMargin: Tokens.padding.medium
        spacing: 0

        RowLayout {
            spacing: Tokens.spacing.small

            MaterialIcon {
                text: "swap_vert"
                color: Colours.palette.m3primary
                fontStyle: Tokens.font.icon.medium
            }

            MenuText {
                text: qsTr("Network")
                font: MenuStyle.withSystemFamily(Tokens.font.title.medium)
            }
        }

        Item {
            Layout.topMargin: Tokens.spacing.medium
            Layout.bottomMargin: Tokens.spacing.small
            Layout.fillWidth: true
            Layout.fillHeight: true

            SparklineItem {
                id: sparkline

                property real targetMax: 1024
                property real smoothMax: targetMax

                anchors.fill: parent
                line1: NetworkUsage.uploadBuffer // qmllint disable missing-type
                line1Color: Colours.palette.m3secondary
                line1FillAlpha: 0.15
                line2: NetworkUsage.downloadBuffer // qmllint disable missing-type
                line2Color: Colours.palette.m3tertiary
                line2FillAlpha: 0.2
                maxValue: smoothMax
                historyLength: NetworkUsage.historyLength

                Connections {
                    function onValuesChanged(): void {
                        sparkline.targetMax = Math.max(NetworkUsage.downloadBuffer.maximum, NetworkUsage.uploadBuffer.maximum, 1024);
                        slideAnim.restart();
                    }

                    target: NetworkUsage.downloadBuffer
                }

                NumberAnimation {
                    id: slideAnim

                    target: sparkline
                    property: "slideProgress"
                    from: 0
                    to: 1
                    easing.type: Easing.Linear
                    duration: GlobalConfig.dashboard.resourceUpdateInterval
                }

                Behavior on smoothMax {
                    Anim {}
                }
            }

            MenuText {
                anchors.centerIn: parent
                text: qsTr("Collecting data...")
                font: MenuStyle.withSystemFamily(Tokens.font.body.small)
                color: Colours.palette.m3outline
                visible: NetworkUsage.downloadBuffer.count < 2
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Tokens.spacing.small

            MaterialIcon {
                text: "download"
                color: Colours.palette.m3tertiary
                fontStyle: Tokens.font.icon.medium
            }

            MenuText {
                text: qsTr("Download")
                font: MenuStyle.withSystemFamily(Tokens.font.body.small)
                color: MenuStyle.muted
            }

            Item {
                Layout.fillWidth: true
            }

            MenuText {
                text: Units.formatBytes(NetworkUsage.downloadSpeed ?? 0, true)
                font: MenuStyle.withSystemFamily(Tokens.font.body.builders.medium.weight(Font.Medium).build())
                color: Colours.palette.m3tertiary
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Tokens.spacing.small

            MaterialIcon {
                text: "upload"
                color: Colours.palette.m3secondary
                fontStyle: Tokens.font.icon.medium
            }

            MenuText {
                text: qsTr("Upload")
                font: MenuStyle.withSystemFamily(Tokens.font.body.small)
                color: MenuStyle.muted
            }

            Item {
                Layout.fillWidth: true
            }

            MenuText {
                text: Units.formatBytes(NetworkUsage.uploadSpeed ?? 0, true)
                font: MenuStyle.withSystemFamily(Tokens.font.body.builders.medium.weight(Font.Medium).build())
                color: Colours.palette.m3secondary
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Tokens.spacing.small

            MaterialIcon {
                text: "history"
                color: MenuStyle.muted
                fontStyle: Tokens.font.icon.medium
            }

            MenuText {
                text: qsTr("Total")
                font: MenuStyle.withSystemFamily(Tokens.font.body.small)
                color: MenuStyle.muted
            }

            Item {
                Layout.fillWidth: true
            }

            MenuText {
                text: `↓${Units.formatBytes(NetworkUsage.downloadTotal ?? 0)} ↑${Units.formatBytes(NetworkUsage.uploadTotal ?? 0)}`
                font: MenuStyle.withSystemFamily(Tokens.font.body.small)
                color: MenuStyle.muted
            }
        }
    }
}
