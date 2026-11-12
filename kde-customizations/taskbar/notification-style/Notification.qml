pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Services.Notifications
import Caelestia.Components
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.components.effects
import qs.services
import qs.utils

StyledRect {
    id: root

    required property NotifData modelData
    readonly property bool hasImage: modelData.image.length > 0
    readonly property bool hasAppIcon: modelData.appIcon.length > 0
    readonly property real nonAnimHeight: Math.max(84, content.implicitHeight + 36)
    readonly property real textScale: Math.max(0.75, Tokens.font.body.small.pointSize / 12)
    readonly property bool hasProgress: modelData.hints?.value !== undefined
    readonly property real progress: Math.max(0, Math.min(100, Number(modelData.hints?.value ?? 0)))
    property bool expanded: true

    color: MenuStyle.smokeSurface
    border.width: 1
    border.color: root.modelData.urgency === NotificationUrgency.Critical ? Colours.palette.m3error : MenuStyle.border
    radius: 20

    implicitHeight: nonAnimHeight

    x: implicitWidth
    Component.onCompleted: {
        x = 0;
        modelData.lock(this);
    }
    Component.onDestruction: modelData.unlock(this)

    Behavior on x {
        Anim {
            easing: Tokens.anim.emphasizedDecel
        }
    }

    MouseArea {
        property int startY

        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.expanded && body.hoveredLink ? Qt.PointingHandCursor : pressed ? Qt.ClosedHandCursor : undefined
        acceptedButtons: Qt.LeftButton | Qt.MiddleButton
        preventStealing: true

        onEntered: root.modelData.timer.stop()
        onExited: {
            if (!pressed)
                root.modelData.timer.start();
        }

        drag.target: parent
        drag.axis: Drag.XAxis

        onPressed: event => {
            root.modelData.timer.stop();
            startY = event.y;
            if (event.button === Qt.MiddleButton)
                root.modelData.close();
        }
        onReleased: event => {
            if (!containsMouse)
                root.modelData.timer.start();

            if (Math.abs(root.x) < root.implicitWidth * Config.notifs.clearThreshold)
                root.x = 0;
            else
                root.modelData.popup = false;
        }
        onPositionChanged: event => {
            if (pressed) {
                const diffY = event.y - startY;
                if (Math.abs(diffY) > Config.notifs.expandThreshold)
                    root.expanded = diffY > 0;
            }
        }
        onClicked: event => {
            if (!GlobalConfig.notifs.actionOnClick || event.button !== Qt.LeftButton)
                return;

            const actions = root.modelData.actions;
            if (actions.length === 1)
                actions[0].invoke();
        }

        Item {
            id: inner
            anchors.fill: parent
            anchors.margins: 18

            Rectangle {
                id: iconTile
                width: 48; height: 48
                radius: root.hasImage ? 12 : 14
                color: root.hasAppIcon ? "transparent" : Qt.alpha(MenuStyle.accent, 0.20)
                Image {
                    anchors.fill: parent
                    visible: root.hasImage
                    source: root.hasImage ? Qt.resolvedUrl(root.modelData.image) : ""
                    fillMode: Image.PreserveAspectFit
                    asynchronous: true
                }
                ColouredIcon {
                    anchors.centerIn: parent
                    width: root.hasImage ? 22 : 46
                    height: width
                    visible: root.hasAppIcon
                    anchors.horizontalCenterOffset: root.hasImage ? 17 : 0
                    anchors.verticalCenterOffset: root.hasImage ? 17 : 0
                    source: root.hasAppIcon ? Quickshell.iconPath(root.modelData.appIcon) : ""
                    colour: MenuStyle.ink
                    layer.enabled: root.modelData.appIcon.endsWith("symbolic")
                }
                MaterialIcon {
                    anchors.centerIn: parent
                    visible: !root.hasAppIcon && !root.hasImage
                    text: root.modelData.materialIcon || Icons.getNotifIcon(root.modelData.summary, root.modelData.urgency)
                    color: MenuStyle.accent
                    fontStyle: Tokens.font.icon.large
                }
            }

            ColumnLayout {
                id: content
                anchors.left: iconTile.right
                anchors.leftMargin: 16
                anchors.right: parent.right
                spacing: 4

                Item {
                    Layout.fillWidth: true
                    implicitHeight: Math.max(metadata.implicitHeight, 20)
                    MenuText {
                        id: metadata
                        anchors.left: parent.left
                        anchors.right: closeButton.left
                        anchors.rightMargin: 8
                        text: (root.modelData.appName || qsTr("System")) + "  •  " + root.modelData.timeStr
                        font.pixelSize: MenuStyle.secondaryPixels * root.textScale
                        color: MenuStyle.muted
                        elide: Text.ElideRight
                        textFormat: Text.PlainText
                    }
                    Item {
                        id: closeButton
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.topMargin: -6
                        width: 30; height: 30
                        StateLayer {
                            radius: 8
                            color: MenuStyle.ink
                            onClicked: root.modelData.close()
                        }
                        MaterialIcon {
                            anchors.centerIn: parent
                            text: "close"
                            color: MenuStyle.muted
                            fontStyle: Tokens.font.icon.medium
                        }
                    }
                }
                MenuText {
                    Layout.fillWidth: true
                    Layout.rightMargin: 8
                    text: root.modelData.summaryPlain
                    textFormat: Text.PlainText
                    font.pixelSize: MenuStyle.bodyPixels * 1.125 * root.textScale
                    font.weight: Font.DemiBold
                    wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                    maximumLineCount: root.expanded ? 6 : 1
                    elide: Text.ElideRight
                }
                MenuText {
                    id: body
                    Layout.fillWidth: true
                    visible: text.length > 0 && !root.hasProgress
                    textFormat: root.expanded ? Text.StyledText : Text.PlainText
                    text: root.expanded ? root.modelData.bodyStyled : root.modelData.bodyPlain
                    color: MenuStyle.muted
                    font.pixelSize: MenuStyle.bodyPixels * root.textScale
                    wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                    maximumLineCount: root.expanded ? 12 : 1
                    elide: Text.ElideRight
                    onLinkActivated: link => {
                        Qt.openUrlExternally(link);
                        root.modelData.popup = false;
                    }
                }
                Row {
                    Layout.fillWidth: true
                    Layout.topMargin: 8
                    visible: root.hasProgress
                    spacing: 3
                    Repeater {
                        model: 32
                        Rectangle {
                            required property int index
                            width: Math.max(1, (content.width - 31 * 3) / 32)
                            height: 10
                            radius: 2
                            color: index < Math.round(root.progress * 32 / 100) ? MenuStyle.accent : MenuStyle.rule
                            MenuPrimarySurface { anchors.fill: parent; radius: 2; visible: parent.index < Math.round(root.progress * 32 / 100) }
                        }
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    visible: root.hasProgress
                    MenuText {
                        Layout.fillWidth: true
                        text: root.modelData.bodyPlain
                        textFormat: Text.PlainText
                        wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                        font.pixelSize: MenuStyle.secondaryPixels * root.textScale
                        color: MenuStyle.muted
                    }
                    MenuText {
                        Layout.alignment: Qt.AlignBottom
                        text: Math.round(root.progress) + "%"
                        font.pixelSize: MenuStyle.secondaryPixels * root.textScale
                        color: MenuStyle.muted
                    }
                }
                Flow {
                    Layout.fillWidth: true
                    Layout.topMargin: visible ? 12 : 0
                    visible: root.expanded && root.modelData.actions.length > 0
                    layoutDirection: Qt.RightToLeft
                    spacing: 8
                    Repeater {
                        model: root.modelData.actions
                        TextButton {
                            required property var modelData
                            required property int index
                            // Keep every application-supplied action, including default.
                            text: modelData.text
                            type: index === 0 ? ButtonBase.Filled : ButtonBase.Text
                            inactiveColour: index === 0 ? MenuStyle.accent : MenuStyle.muted
                            inactiveOnColour: index === 0 ? "white" : MenuStyle.muted
                            font.family: MenuStyle.fontFamily
                            font.pixelSize: MenuStyle.bodyPixels * root.textScale
                            implicitWidth: Math.min(content.width, label.implicitWidth + 28)
                            implicitHeight: Math.max(36, label.implicitHeight + 12)
                            radiusMorph: false
                            defaultRadius: 11
                            label.width: width - 28
                            label.elide: Text.ElideRight
                            label.horizontalAlignment: Text.AlignHCenter
                            onClicked: modelData.invoke()
                        }
                    }
                }
            }
            // Secondary utilities appear on hover, without competing with actions.
            Row {
                anchors.left: parent.left
                anchors.top: iconTile.bottom
                anchors.topMargin: 6
                visible: parent.parent.containsMouse
                IconButton {
                    icon: root.expanded ? "expand_less" : "expand_more"
                    type: ButtonBase.Text
                    padding: 0
                    font: Tokens.font.icon.small
                    implicitWidth: 24
                    implicitHeight: 28
                    inactiveOnColour: MenuStyle.muted
                    onClicked: root.expanded = !root.expanded
                }
                IconButton {
                    icon: "content_copy"
                    type: ButtonBase.Text
                    padding: 0
                    font: Tokens.font.icon.small
                    implicitWidth: 24
                    implicitHeight: 28
                    inactiveOnColour: MenuStyle.muted
                    onClicked: Quickshell.clipboardText = root.modelData.body
                }
            }
        }
    }
}
