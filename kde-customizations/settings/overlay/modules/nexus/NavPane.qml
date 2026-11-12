import "navpane"
import QtQuick
import QtQuick.Window
import QtQuick.Controls as QQC
import Flausen.Settings
import QtQuick.Effects
import Quickshell
import "flausen"
import QtQuick.Layouts
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services
import qs.modules.nexus

ColumnLayout {
    id: root

    required property NexusState nState

    // Both result panes search the index and build a delegate per hit, so the
    // query is published once typing pauses instead of on every keystroke.
    function publishQuery(): void {
        searchDebounce.stop();
        root.nState.searchQuery = searchField.text;
    }

    function clearQuery(): void {
        searchDebounce.stop();
        root.nState.searchQuery = "";
    }

    spacing: 20
    AccountProfile { id: profile }
    PicturePicker {
        visible: false
        id: avatarPicker
        objectName: "accountPicturePicker"
        onAccepted: profile.setPicture(selectedFile)
        onFailed: profile.error = error
    }
    QQC.Dialog {
        id: avatarError
        parent: root.Window.window?.contentItem ?? root
        title: qsTranslate("Flausen", "Change profile picture")
        modal: true
        anchors.centerIn: parent
        width: Math.min(480, parent.width - 40)
        standardButtons: QQC.Dialog.Ok
        contentItem: Text { text: profile.error; wrapMode: Text.WordWrap; color: FlausenStyle.text; font: FlausenStyle.typeface(14) }
        background: Rectangle { color: FlausenStyle.card; radius: 14; border.color: FlausenStyle.line }
    }
    Connections { target: profile; function onErrorChanged() { if (profile.error) avatarError.open(); } }

    RowLayout {
        Layout.fillWidth: true
        Layout.topMargin: 4
        Layout.bottomMargin: 6
        spacing: 14
        QQC.Button {
            id: avatarButton
            objectName: "accountAvatarButton"
            implicitWidth: 48; implicitHeight: 48
            padding: 0
            enabled: profile.accountPath !== "" && !profile.busy
            Accessible.name: qsTranslate("Flausen", "Change profile picture")
            QQC.ToolTip.visible: hovered
            QQC.ToolTip.text: qsTranslate("Flausen", "Change profile picture")
            QQC.ToolTip.delay: 500
            onClicked: avatarPicker.open()
            background: Rectangle {
                radius: 24
                color: FlausenStyle.selected
                border.width: avatarButton.visualFocus || avatarButton.hovered ? 2 : 0
                border.color: FlausenStyle.accent
            }
            contentItem: Item {
                Image {
                    id: avatarImage
                    objectName: "accountAvatarImage"
                    anchors.fill: parent
                    source: profile.source
                    cache: false
                    smooth: true
                    mipmap: true
                    sourceSize: Qt.size(256, 256)
                    fillMode: Image.PreserveAspectCrop
                    layer.enabled: true
                    layer.smooth: true
                    layer.mipmap: true
                    layer.textureSize: Qt.size(Math.ceil(width * Screen.devicePixelRatio * 4), Math.ceil(height * Screen.devicePixelRatio * 4))
                    layer.effect: MultiEffect {
                        maskEnabled: true
                        maskSource: avatarMask
                        Rectangle { id: avatarMask; anchors.fill: parent; radius: width/2; color: "white"; visible: false; layer.enabled: true }
                    }
                }
                Text {
                    anchors.centerIn: parent
                    visible: avatarImage.status !== Image.Ready
                    text: profile.displayName.charAt(0).toUpperCase() || "?"
                    color: FlausenStyle.text
                    font { family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 26; weight: Font.Medium }
                }
            }
        }
        QQC.Button {
            id: userButton
            objectName: "accountSettingsButton"
            Layout.fillWidth: true
            padding: 0
            Accessible.name: qsTranslate("Flausen", "Open account settings")
            onClicked: root.nState.navigateToSystemModule(17, "kcm_users", qsTranslate("Flausen", "User account"))
            background: Rectangle {
                radius: 6
                color: userButton.hovered ? Qt.alpha(FlausenStyle.text, 0.06) : "transparent"
                border.width: userButton.visualFocus ? 1 : 0
                border.color: FlausenStyle.accent
            }
            contentItem: ColumnLayout {
                spacing: 3
                Text { text: profile.displayName; Layout.fillWidth: true; elide: Text.ElideRight; color: FlausenStyle.text; font {family:FlausenStyle.family; pixelSize:FlausenStyle.fontScale * 17; weight:Font.DemiBold} }
                Text { text: qsTranslate("Flausen", "Local account"); color: FlausenStyle.secondary; font {family:FlausenStyle.family; pixelSize:FlausenStyle.fontScale * 12} }
            }
        }
    }
    Shortcut { sequence: "Ctrl+F"; onActivated: searchField.forceActiveFocus() }
    SearchBar {
        id: searchField

        z: 1
        Layout.fillWidth: true

        placeholderText: qsTranslate("Flausen", "Search settings")
        color: FlausenStyle.text
        placeholderTextColor: FlausenStyle.secondary
        topPadding: 12
        bottomPadding: 12
        font.family: FlausenStyle.family
        font.pixelSize: FlausenStyle.fontScale * 13

        bg.color: FlausenStyle.card
        bg.border.color: FlausenStyle.line
        searchIcon.fontStyle: Tokens.font.icon.medium
        searchIcon.anchors.leftMargin: Tokens.padding.largeIncreased
        clearIcon.font: Tokens.font.icon.medium
        clearIcon.padding: Tokens.padding.extraSmall

        onTextChanged: {
            if (text === "")
                root.clearQuery();
            else
                searchDebounce.restart();
        }

        Keys.onReturnPressed: {
            if (root.nState.searchOpen) {
                root.publishQuery();
                searchResults.executeSelected();
            }
        }

        Keys.onUpPressed: {
            if (root.nState.searchOpen) {
                searchResults.moveUp();
            }
        }

        Keys.onDownPressed: {
            if (root.nState.searchOpen) {
                searchResults.moveDown();
            }
        }

        Behavior on bg.border.color {
            CAnim {}
        }

        Binding {
            target: root.nState
            property: "searchOpen"
            value: searchField.text.length > 0
        }

        Connections {
            function onSearchQueryChanged() {
                if (root.nState.searchQuery !== searchField.text) {
                    searchField.text = root.nState.searchQuery;
                }
            }

            target: root.nState
        }

        Timer {
            id: searchDebounce

            interval: 400
            onTriggered: root.publishQuery()
        }
    }

    NavLocations {
        visible: !root.nState.searchOpen

        Layout.fillWidth: true
        Layout.fillHeight: true
        nState: root.nState
    }

    SearchResults {
        id: searchResults

        visible: root.nState.searchOpen

        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.topMargin: -topMargin
        Layout.bottomMargin: -bottomMargin
        nState: root.nState
    }
}
