pragma ComponentBehavior: Bound

import QtQuick
import qs.modules.nexus.flausen
import QtQuick.Layouts
import Caelestia.Config
import qs.components
import qs.components.containers
import qs.components.controls
import qs.services
import qs.modules.nexus
import "../flausen"

ColumnLayout {
    id: root

    required property string title
    required property NexusState nState
    property string subtitle: ""
    property bool isSubPage
    property bool scrollable: true
    readonly property int cappedWidth: Math.min(Tokens.sizes.nexus.maxContentWidth, width)
    readonly property alias flickable: flickable
    property list<Item> headerActions

    default property Item contentChild

    spacing: 12

    MouseArea {
        z: 1
        implicitWidth: header.implicitWidth
        implicitHeight: header.implicitHeight - Layout.bottomMargin
        Layout.bottomMargin: -flickable.topMargin
        Layout.fillWidth: true

        RowLayout {
            id: header

            width: parent.width

            spacing: Tokens.spacing.largeIncreased

            Loader {
                visible: active
                active: root.isSubPage
                asynchronous: true
                sourceComponent: IconButton {
                    icon: "arrow_back"
                    font: Tokens.font.icon.medium
                    type: IconButton.Tonal
                    isRound: true
                    inactiveColour: FlausenStyle.card
                    inactiveOnColour: FlausenStyle.secondary
                    onClicked: root.nState.closeSubPage()
                }
            }

            StyledText {
                Layout.fillWidth: true
                text: root.title
                font.family: FlausenStyle.family
                font.pixelSize: FlausenStyle.fontScale * 30
                font.weight: Font.DemiBold
                color: FlausenStyle.text
                elide: Text.ElideRight
            }

            RowLayout {
                spacing: Tokens.spacing.small
                children: root.headerActions
            }
        }
    }

    Text {
        visible: root.subtitle.length > 0
        text: root.subtitle
        color: FlausenStyle.secondary
        font: FlausenStyle.typeface(15)
        wrapMode: Text.WordWrap
        Layout.fillWidth: true
        Layout.bottomMargin: 10
    }
    VerticalFadeFlickable {
        id: flickable

        interactive: root.scrollable
        Layout.fillWidth: true
        Layout.fillHeight: true

        Layout.topMargin: -topMargin
        topMargin: Tokens.padding.large
        bottomMargin: Tokens.padding.extraLarge

        contentHeight: root.scrollable ? (root.contentChild?.implicitHeight ?? 0) : height
        contentItem.children: [root.contentChild]
    }
}
