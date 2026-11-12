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

    property alias icon: icon.text
    property alias label: label.text
    property alias status: status.text

    signal clicked

    Layout.fillWidth: true
    implicitHeight: navLayout.implicitHeight + navLayout.anchors.margins * 2

    StateLayer {
        onClicked: root.clicked()
    }

    RowLayout {
        id: navLayout

        anchors.fill: parent
        anchors.margins: Tokens.padding.medium
        anchors.leftMargin: Tokens.padding.largeIncreased
        anchors.rightMargin: Tokens.padding.largeIncreased
        spacing: Tokens.spacing.medium

        MaterialIcon {
            id: icon

            color: FlausenStyle.secondary
            fontStyle: Tokens.font.icon.medium
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
                id: status

                Layout.fillWidth: true
                visible: text
                color: FlausenStyle.secondary
                font: NexusStyle.secondaryFont
                elide: Text.ElideRight
                animate: true
            }
        }

        MaterialIcon {
            text: "chevron_right"
            color: FlausenStyle.secondary
            fontStyle: Tokens.font.icon.medium
        }
    }
}
