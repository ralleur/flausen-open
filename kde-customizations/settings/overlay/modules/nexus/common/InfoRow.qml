pragma ComponentBehavior: Bound

import QtQuick
import qs.modules.nexus.flausen
import QtQuick.Layouts
import Caelestia.Config
import qs.components
import qs.services
import qs.modules.nexus.common

ConnectedRect {
    id: root

    property alias label: label.text
    property string subtext
    property alias value: value.text
    property string icon
    property color iconColour: FlausenStyle.secondary
    property Component leadingComponent: icon ? iconComp : null

    Layout.fillWidth: true
    implicitHeight: rowLayout.implicitHeight + rowLayout.anchors.margins * 2

    Component {
        id: iconComp

        MaterialIcon {
            text: root.icon
            color: root.iconColour
            fontStyle: Tokens.font.icon.small
        }
    }

    RowLayout {
        id: rowLayout

        anchors.fill: parent
        anchors.margins: Tokens.padding.medium
        anchors.leftMargin: Tokens.padding.largeIncreased
        anchors.rightMargin: Tokens.padding.largeIncreased
        spacing: Tokens.spacing.medium

        Loader {
            visible: root.leadingComponent
            active: root.leadingComponent
            sourceComponent: root.leadingComponent
        }

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
                Layout.fillWidth: true
                visible: root.subtext
                text: root.subtext
                color: FlausenStyle.secondary
                font: NexusStyle.secondaryFont
                elide: Text.ElideRight
            }
        }

        StyledText {
            id: value

            Layout.maximumWidth: root.width / 2
            horizontalAlignment: Text.AlignRight
            color: FlausenStyle.secondary
            font: FlausenStyle.typeface(14)
            elide: Text.ElideRight
        }
    }
}
