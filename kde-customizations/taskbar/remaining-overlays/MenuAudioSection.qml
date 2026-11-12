pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Caelestia.Config
import qs.components
import qs.services

ColumnLayout {
    id: root

    required property string title
    property string icon: ""
    property bool expanded: false
    property real scaleOffset: 1.0
    property real fontScale: 1.0
    property real minHeaderHeight: 42
    property real headerRightMargin: Tokens.padding.extraSmall * scaleOffset
    default property alias content: contentColumn.data

    Layout.fillWidth: true
    Layout.leftMargin: 7 * root.scaleOffset
    Layout.rightMargin: 7 * root.scaleOffset
    spacing: Tokens.spacing.extraSmall * root.scaleOffset

    Item {
        id: sectionHeader

        activeFocusOnTab: true
        Accessible.role: Accessible.Button
        Accessible.name: root.title
        Accessible.expanded: root.expanded
        Keys.onSpacePressed: root.expanded = !root.expanded
        Keys.onReturnPressed: root.expanded = !root.expanded
        Layout.fillWidth: true
        Layout.preferredHeight: Math.max(titleRow.implicitHeight + 12 * root.scaleOffset, root.minHeaderHeight * root.scaleOffset)

        Rectangle {
            anchors.fill: parent
            radius: 13 * root.scaleOffset
            color: MenuStyle.cardFill
            border.width: 1
            border.color: sectionHeader.activeFocus ? MenuStyle.accent : MenuStyle.rule
        }

        RowLayout {
            id: titleRow

            anchors.fill: parent
            anchors.leftMargin: 16 * root.scaleOffset
            anchors.rightMargin: 16 * root.scaleOffset
            spacing: Tokens.spacing.small * root.scaleOffset

            MaterialIcon {
                visible: root.icon !== ""
                text: root.icon
                color: MenuStyle.ink
                Layout.preferredWidth: 30 * root.scaleOffset
                fontStyle.pointSize: 16 * root.scaleOffset
            }

            MenuText {
                Layout.fillWidth: true
                text: root.title
                font.weight: Font.Normal
                font.pointSize: MenuStyle.bodyPointSize(root.fontScale)
            }

            MaterialIcon {
                text: "expand_more"
                rotation: root.expanded ? 180 : 0
                color: MenuStyle.muted
                fontStyle.pointSize: 14 * root.scaleOffset

                Behavior on rotation {
                    Anim {
                        type: Anim.StandardSmall
                    }
                }
            }
        }

        StateLayer {
            anchors.fill: parent
            radius: Tokens.rounding.medium * root.scaleOffset
            showHoverBackground: false
            onClicked: root.expanded = !root.expanded
        }
    }

    Item {
        id: contentWrapper
        enabled: root.expanded
        visible: Layout.preferredHeight > 0

        Layout.fillWidth: true
        Layout.preferredHeight: root.expanded ? (contentColumn.implicitHeight + Tokens.spacing.extraSmall * root.scaleOffset) : 0
        implicitHeight: Layout.preferredHeight
        clip: true
        Rectangle {
            anchors.fill: parent
            radius: 14 * root.scaleOffset
            color: MenuStyle.cardFill
            border.width: 1
            border.color: MenuStyle.rule
        }

        Behavior on Layout.preferredHeight {
            Anim {}
        }

        ColumnLayout {
            id: contentColumn

            width: parent.width
            y: Tokens.spacing.extraSmall * root.scaleOffset
            spacing: Tokens.spacing.extraSmall * root.scaleOffset
            opacity: root.expanded ? 1.0 : 0.0

            Behavior on opacity {
                Anim {
                    type: Anim.DefaultEffects
                }
            }
        }
    }
}
