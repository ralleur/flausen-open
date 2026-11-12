pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services

StyledRect {
    id: root

    property real scaleOffset: 1.0
    property real fontScale: 1.0
    property alias icon: icon.text
    property alias sliderColour: slider.fgColour
    property alias label: label.text
    property alias valueLabel: valueLabel.text
    property string subtext
    property real value
    property var reset
    property bool first
    property bool last
    property bool iconClickable: false
    property bool spacious: false
    property bool roomyHeader: false

    signal moved(value: real)
    signal interaction(value: real)
    signal released(value: real)
    signal iconClicked

    Layout.fillWidth: true
    implicitHeight: rowLayout.implicitHeight + rowLayout.anchors.margins + rowLayout.anchors.topMargin
    color: "transparent"
    topLeftRadius: first ? (spacious ? Tokens.rounding.extraLarge : Tokens.rounding.large) : Tokens.rounding.extraSmall
    topRightRadius: first ? (spacious ? Tokens.rounding.extraLarge : Tokens.rounding.large) : Tokens.rounding.extraSmall
    bottomLeftRadius: last ? (spacious ? Tokens.rounding.extraLarge : Tokens.rounding.large) : Tokens.rounding.extraSmall
    bottomRightRadius: last ? (spacious ? Tokens.rounding.extraLarge : Tokens.rounding.large) : Tokens.rounding.extraSmall

    RowLayout {
        id: rowLayout

        anchors.fill: parent
        anchors.margins: 16 * root.scaleOffset
        anchors.topMargin: 10 * root.scaleOffset
        // Keep the same right inset as ToggleRow/StepperRow (12px) even when
        // spacious, so reset icons line up in one column across every row type.
        anchors.rightMargin: 16 * root.scaleOffset
        spacing: 12 * root.scaleOffset

        MaterialIcon {
            id: icon

            visible: text !== ""
            color: root.enabled ? MenuStyle.muted : Colours.disabledContent
            Layout.preferredWidth: 36 * root.scaleOffset
            Layout.preferredHeight: 30 * root.scaleOffset
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.scaleOffset

            MouseArea {
                anchors.fill: parent
                anchors.margins: -6
                enabled: root.iconClickable
                cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                onClicked: root.iconClicked()
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: spacious ? Tokens.spacing.medium : Tokens.spacing.extraSmall

            RowLayout {
                Layout.fillWidth: true
                Layout.minimumHeight: root.roomyHeader ? 40 : 0
                spacing: Tokens.spacing.small

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0

                    MenuText {
                        id: label

                        Layout.fillWidth: true
                        font.family: MenuStyle.fontFamily
                        font.pointSize: MenuStyle.bodyPointSize(root.fontScale)
                        color: root.enabled ? MenuStyle.ink : Colours.disabledContent
                        elide: Text.ElideRight
                    }

                    MenuText {
                        Layout.fillWidth: true
                        visible: root.subtext !== ""
                        text: root.subtext
                        color: root.enabled ? MenuStyle.muted : Colours.disabledContent
                        font.pointSize: MenuStyle.bodyPointSize(root.fontScale) * 0.79
                        elide: Text.ElideRight
                    }
                }

                MenuText {
                    id: valueLabel

                    color: root.enabled ? MenuStyle.muted : Colours.disabledContent
                    font.family: MenuStyle.fontFamily
                        font.pointSize: MenuStyle.bodyPointSize(root.fontScale)
                }


            }

            CustomMouseArea {
                function onWheel(event: WheelEvent): void {
                    const step = GlobalConfig.services.audioIncrement;
                    if (event.angleDelta.y > 0)
                        root.moved(Math.min(1, root.value + step));
                    else if (event.angleDelta.y < 0)
                        root.moved(Math.max(0, root.value - step));
                }

                Layout.fillWidth: true
                implicitHeight: spacious ? Tokens.padding.medium * 2 : Tokens.padding.large

                StyledSlider {
                    id: slider
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    implicitHeight: parent.implicitHeight

                    radius: Tokens.rounding.small
                    value: root.value
                    enabled: root.enabled
                    onInteraction: v => {
                        root.moved(v);
                        root.interaction(v);
                    }
                    onReleased: v => root.released(v)
                }
            }
        }
    }
}
