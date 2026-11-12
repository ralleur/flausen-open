/*
    SPDX-FileCopyrightText: 2016 David Edmundson <davidedmundson@kde.org>

    SPDX-License-Identifier: LGPL-2.0-or-later
*/

import QtQuick
import "FlausenBrand.js" as FlausenBrand

import QtQuick.Layouts

import org.kde.plasma.components as PlasmaComponents3
import org.kde.kirigami as Kirigami
import org.kde.breeze.components as Breeze
import QtQuick.Controls as QQC2
import Qt5Compat.GraphicalEffects

FocusScope {
    id: root

    /*
     * Any message to be displayed to the user, visible above the text fields
     */
    property alias notificationMessage: notificationsLabel.text

    /*
     * A list of Items (typically ActionButtons) to be shown in a Row beneath the prompts
     */
    property alias actionItems: actionItemsLayout.children

    /*
     * Whether to show or hide the list of action items as a whole.
     */
    property alias actionItemsVisible: actionItemsLayout.visible

    /*
     * A model with a list of users to show in the view.
     * There are different implementations in sddm greeter (UserModel) and
     * KScreenLocker (SessionsModel), so some roles will be missing.
     *
     * type: {
     *  name: string,
     *  realName: string,
     *  homeDir: string,
     *  icon: string,
     *  iconName?: string,
     *  needsPassword?: bool,
     *  displayNumber?: string,
     *  vtNumber?: int,
     *  session?: string
     *  isTty?: bool,
     * }
     */
    property alias userListModel: userListView.model

    /*
     * Self explanatory
     */
    property alias userListCurrentIndex: userListView.currentIndex
    property alias userListCurrentItem: userListView.currentItem
    property bool showUserList: true
    property bool minimalIdentity: false

    property alias userList: userListView

    property real fontSize: Kirigami.Theme.defaultFont.pointSize + 2

    /*
     * The item used to indicate the type of authentication required, e.g. a password or fingerprint icon.
     */
    property Item authenticationTypeItem: null
    property string mode: "auto"
    property Item backdrop: null
    property real bottomInset: 24
    SystemPalette { id: systemPalette }
    readonly property bool dark: mode === "dark" || (mode === "auto" && systemPalette.window.hslLightness < 0.5)
    Kirigami.Theme.inherit: false
    Kirigami.Theme.colorSet: Kirigami.Theme.Window
    readonly property var brandTheme: dark ? FlausenBrand.tokens.color.dark : FlausenBrand.tokens.color.light
    Kirigami.Theme.backgroundColor: brandTheme.background
    Kirigami.Theme.textColor: ink
    readonly property color ink: brandTheme.text
    readonly property color muted: brandTheme.textMuted
    property date now: new Date()

    default property alias _children: innerLayout.children

    signal userSelected()

    function playHighlightAnimation() {
        card.opacity = 0.7; restoreOpacity.restart();
    }

    Timer { interval: 1000; running: true; repeat: true; onTriggered: root.now = new Date() }
    Timer { id: restoreOpacity; interval: 180; onTriggered: card.opacity = 1 }
    Image {
        visible: !root.minimalIdentity
        anchors { left: parent.left; top: parent.top; margins: 28 }
        source: root.dark ? "flausen-lockup-on-dark.svg" : "flausen-lockup-on-light.svg"
        width: 120; height: 80
        fillMode: Image.PreserveAspectFit
        Accessible.name: "flausen."
    }
    Flickable {
        id: actionViewport
        objectName: "ralleurLockActionsViewport"
        anchors { bottom: parent.bottom; horizontalCenter: parent.horizontalCenter; bottomMargin: root.bottomInset }
        width: Math.max(0, Math.min(actionItemsLayout.naturalWidth, parent.width - 48))
        height: Math.min(actionItemsLayout.implicitHeight, Math.max(64, root.height * 0.28))
        contentWidth: width
        contentHeight: actionItemsLayout.implicitHeight
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        interactive: contentHeight > height
        QQC2.ScrollBar.vertical: QQC2.ScrollBar { policy: QQC2.ScrollBar.AsNeeded }
        Flow {
            id: actionItemsLayout
            objectName: "ralleurLockActions"
            width: actionViewport.width
            spacing: 8
            readonly property real naturalWidth: {
                let total = 0
                let count = 0
                for (const button of children) {
                    if (button.visible && button.implicitWidth !== undefined) {
                        total += button.implicitWidth
                        count++
                    }
                }
                return total + Math.max(0, count - 1) * spacing
            }
            function constrainButtons() {
                for (const button of children) {
                    if (button.implicitWidth !== undefined)
                        button.width = Qt.binding(() => Math.min(button.implicitWidth, actionViewport.width))
                }
            }
            onChildrenChanged: constrainButtons()
            Component.onCompleted: constrainButtons()
        }
    }
    Rectangle {
        id: card
        anchors.centerIn: parent
        width: Math.min(420, parent.width - 40)
        height: root.minimalIdentity ? content.implicitHeight + 60 : Math.max(510, content.implicitHeight + 56)
        readonly property real bottomReserved: root.bottomInset + actionViewport.height + 16
        scale: Math.min(1, Math.max(0.1, (root.height - bottomReserved - 60) / height))
        anchors.verticalCenterOffset: Math.min(0, root.height / 2 - bottomReserved - 16 - height * scale / 2)
        radius: 22
        border.width: 1
        border.color: root.brandTheme.border
        color: "transparent"
        Item {
            anchors.fill: parent
            anchors.margins: 1
            Loader {
                anchors.fill: parent
                active: root.backdrop !== null && GraphicsInfo.api !== GraphicsInfo.Software
                sourceComponent: Component {
                    Item {
                        ShaderEffectSource {
                            id: wallpaperSample
                            anchors.fill: parent
                            sourceItem: root.backdrop
                            // Map both corners to account for the responsive
                            // card scale and the wallpaper's actual geometry.
                            sourceRect: {
                                const factor = card.scale
                                const left = card.x + card.width * (1 - factor) / 2
                                const top = card.y + card.height * (1 - factor) / 2
                                const point = root.mapToItem(root.backdrop, left + factor, top + factor)
                                return Qt.rect(point.x, point.y, (card.width - 2) * factor, (card.height - 2) * factor)
                            }
                            live: true
                            visible: false
                        }
                        FastBlur {
                            id: frostedWallpaper
                            anchors.fill: parent
                            source: wallpaperSample
                            radius: 48
                            transparentBorder: false
                            visible: false
                        }
                        Rectangle {
                            id: roundedMask
                            anchors.fill: parent
                            radius: card.radius - 1
                            color: "white"
                            visible: false
                        }
                        OpacityMask {
                            anchors.fill: parent
                            source: frostedWallpaper
                            maskSource: roundedMask
                        }
                    }
                }
            }
            Rectangle {
                anchors.fill: parent
                radius: card.radius - 1
                color: Qt.alpha(root.brandTheme.surface, root.dark ? 0.72 : 0.78)
            }
        }
        Behavior on opacity { NumberAnimation { duration: 160 } }
        ColumnLayout {
            id: content
            anchors { left: parent.left; right: parent.right; verticalCenter: parent.verticalCenter; margins: 30 }
            spacing: 16
            Text {
                objectName: "ralleurLockDate"
                text: Qt.formatDate(root.now, Qt.locale(), Qt.locale().dateFormat(Locale.LongFormat))
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                color: root.muted; font.family: "Inter"; font.pixelSize: 17
                Layout.alignment: Qt.AlignHCenter
            }
            Text {
                text: Qt.formatTime(root.now, Qt.locale().timeFormat(Locale.ShortFormat))
                color: root.ink; font.family: "Inter"; font.pixelSize: 64; font.weight: Font.Light
                Layout.alignment: Qt.AlignHCenter
                Layout.bottomMargin: root.minimalIdentity ? 0 : 16
            }
            Breeze.UserList {
                id: userListView
                visible: root.showUserList
                Layout.fillWidth: true
                Layout.preferredHeight: root.minimalIdentity ? 84 : 125
                fontSize: 14
                onUserSelected: root.userSelected()
                delegate: Breeze.UserDelegate {
                    required property int index
                    required property string icon
                    required property string realName
                    required property var model
                    width: userListView.userItemWidth
                    height: root.minimalIdentity ? 84 : 125
                    faceSize: 76
                    avatarPath: accountAvatar.source || icon || ""
                    iconSource: model.iconName || "user-identity"
                    name: root.minimalIdentity ? "" : (realName || model.name || "")
                    userName: model.name || ""
                    AccountAvatar {
                        id: accountAvatar
                        userName: model.name || ""
                    }
                    Accessible.name: realName || model.name || qsTr("User")
                    needsPassword: model.needsPassword !== undefined ? model.needsPassword : true
                    fontSize: 14
                    isCurrent: ListView.isCurrentItem
                    constrainText: userListView.count > 1
                    onClicked: { userListView.currentIndex = index; root.userSelected() }
                    Rectangle {
                        visible: !root.minimalIdentity
                        anchors { top: parent.top; horizontalCenter: parent.horizontalCenter }
                        width: 76; height: 76; radius: 38
                        color: root.brandTheme.surfaceRaised
                        border.width: 1; border.color: root.brandTheme.border
                        Text {
                            anchors.centerIn: parent
                            text: (model.name || realName || "?").slice(0,1).toLowerCase()
                            color: root.ink; font.family: "Inter"; font.pixelSize: 32
                        }
                        Image { source: "flausen-symbol-transparent.svg"; width: 16; height: 16; anchors { right: parent.right; bottom: parent.bottom } }
                    }
                }
            }
            RowLayout {
                Layout.fillWidth: true
                visible: root.authenticationTypeItem !== null && root.authenticationTypeItem.visible
                children: root.authenticationTypeItem ? [root.authenticationTypeItem] : []
            }
            PlasmaComponents3.Label {
                id: notificationsLabel
                visible: text.length > 0
                Layout.fillWidth: true
                textFormat: Text.PlainText
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                color: root.ink
            }
            ColumnLayout {
                id: innerLayout
                Layout.fillWidth: true
                spacing: 12
            }
            Text {
                visible: !root.minimalIdentity
                text: i18nd("flausen", "Press Enter to continue")
                color: root.muted; font.family: "Inter"; font.pixelSize: 12
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }
}
