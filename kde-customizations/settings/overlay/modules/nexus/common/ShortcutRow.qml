pragma ComponentBehavior: Bound

import QtQuick
import qs.modules.nexus.flausen
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Effects
import Caelestia
import Caelestia.Config
import Caelestia.Services
import qs.components
import qs.services
import qs.modules.nexus.common

ConnectedRect {
    id: root

    property alias label: label.text
    property alias status: status.text
    property string actionName: ""
    property string keybind: ""
    property bool isOverridden: false
    property bool isShell: false

    signal clicked
    signal addClicked(var target)
    signal resetClicked
    signal keybindEdited(string newKeybind)

    Layout.fillWidth: true
    implicitHeight: navLayout.implicitHeight + navLayout.anchors.margins * 2

    RowLayout {
        id: navLayout

        anchors.fill: parent
        anchors.margins: Tokens.padding.medium
        anchors.leftMargin: Tokens.padding.largeIncreased
        anchors.rightMargin: Tokens.padding.largeIncreased
        spacing: Tokens.spacing.medium

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 0

            StyledText {
                id: label
                Layout.fillWidth: true

                font: FlausenStyle.typeface(14)
                elide: Text.ElideRight
            }

            StyledText {
                id: status
                Layout.fillWidth: true

                visible: text
                color: FlausenStyle.secondary
                font: NexusStyle.secondaryFont
                elide: Text.ElideRight
                animate: true
            }
        }

        RowLayout {
            spacing: Tokens.spacing.small

            Repeater {
                model: {
                    let parts = root.keybind.split(";").map(s => s.trim()).filter(s => s.length > 0)
                    return parts
                }
                delegate: Rectangle {
                    required property string modelData
                    required property int index

                    Layout.preferredHeight: 32
                    Layout.preferredWidth: pillRow.implicitWidth + Tokens.padding.medium * 2
                    radius: Tokens.rounding.small
                    color: FlausenStyle.card
                    border.width: 1
                    border.color: FlausenStyle.line

                    RowLayout {
                        id: pillRow

                        anchors.centerIn: parent
                        spacing: Tokens.spacing.extraSmall

                        StyledText {
                            text: modelData
                            font: FlausenStyle.typeface(13)
                            color: FlausenStyle.secondary
                        }

                        Rectangle {
                            property string partCollisionName: KeybindsModel.getKeyCollisionForPart(root.actionName, modelData)

                            visible: partCollisionName !== ""
                            Layout.preferredWidth: 8
                            Layout.preferredHeight: 8
                            Layout.alignment: Qt.AlignVCenter
                            radius: Tokens.rounding.full
                            color: Colours.palette.m3error

                            layer.enabled: true

                            layer.effect: MultiEffect {
                                shadowEnabled: true
                                shadowColor: Colours.palette.m3error
                                shadowBlur: 0.8
                            }

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                ToolTip.visible: containsMouse
                                ToolTip.text: qsTr("Collides with: ") + parent.partCollisionName
                            }
                        }

                        MaterialIcon {
                            text: "close"
                            fontStyle: Tokens.font.icon.small
                            color: maClose.containsMouse ? Colours.palette.m3error : FlausenStyle.secondary

                            MouseArea {
                                id: maClose

                                anchors.fill: parent
                                anchors.margins: -Tokens.padding.small
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    let parts = root.keybind.split(";").map(s => s.trim()).filter(s => s.length > 0)
                                    parts.splice(index, 1)
                                    root.keybindEdited(parts.join("; "))
                                }
                            }

                            Behavior on color {
                                CAnim {}
                            }
                        }
                    }
                }
            }

            MaterialIcon {
                id: addIcon

                text: "add"
                color: maAdd.containsMouse ? Colours.palette.m3primary : FlausenStyle.secondary
                fontStyle: Tokens.font.icon.medium

                MouseArea {
                    id: maAdd

                    anchors.fill: parent
                    anchors.margins: -Tokens.padding.small
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.addClicked(addIcon)
                }

                Behavior on color {
                    CAnim {}
                }
            }

            MaterialIcon {
                visible: root.isOverridden
                text: "settings_backup_restore"
                color: maReset.containsMouse ? Colours.palette.m3error : FlausenStyle.secondary
                fontStyle: Tokens.font.icon.medium

                MouseArea {
                    id: maReset

                    anchors.fill: parent
                    anchors.margins: -Tokens.padding.small
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.resetClicked()
                }

                Behavior on color {
                    CAnim {}
                }
            }
        }
    }
}
