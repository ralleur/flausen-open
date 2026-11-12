pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Caelestia
import Caelestia.Config
import Caelestia.Services
import qs.components
import qs.components.controls
import qs.services
import qs.modules.launcher.services

Item {
    id: root

    required property DrawerVisibilities visibilities
    required property var panels
    required property real maxWidth
    required property real maxHeight

    readonly property int padding: 26
    property bool browsing: false
    readonly property bool showHome: !search.text && !browsing
    readonly property int rounding: Tokens.rounding.extraLarge
    readonly property bool isClipboardMode: search.text.startsWith(`${GlobalConfig.launcher.actionPrefix}clipboard `)
    readonly property int footerSpacing: Tokens.spacing.small

    property bool windowsAvailable: false
    readonly property string windowsHelper: Qt.resolvedUrl("windows-boot.py").toString().replace("file://", "")
    function refreshWindows(): void {
        if (!windowsProbe.running) windowsProbe.running = true;
    }
    Component.onCompleted: refreshWindows()
    Connections {
        target: root.visibilities
        function onLauncherChanged(): void {
            if (root.visibilities.launcher) root.refreshWindows();
        }
    }
    Process {
        id: windowsProbe
        command: ["/usr/bin/python3", "-I", root.windowsHelper]
        stdout: StdioCollector {
            onStreamFinished: {
                try { root.windowsAvailable = JSON.parse(text).available === true; }
                catch (e) { root.windowsAvailable = false; }
            }
        }
    }
    Process {
        id: windowsReboot
        command: ["/usr/bin/pkexec", "/usr/bin/python3", "-I", root.windowsHelper, "--reboot"]
        stderr: StdioCollector { id: windowsError }
        onExited: (exitCode, exitStatus) => {
            if (exitCode !== 0 && exitCode !== 126) {
                Toaster.toast(qsTr("Restart into Windows failed"),
                    windowsError.text.trim() || qsTr("System authorization was not granted."), "error");
            }
        }
    }

    function askHermes(): void {
        if (!search.text.trim() || hermes.busy) return;
        hermes.send(search.text);
        search.text = "";
    }

    HermesChat {
        id: hermes
        visibilities: root.visibilities
        onBack: {
            expanded = false;
            root.browsing = false;
            search.text = "";
            search.forceActiveFocus();
        }
    }

    function clearClipboardHistory(): void {
        Clipboard.clearHistory();
    }

    function triggerSessionCommand(command: var): void {
        // Nested JavaScript arrays from the footer model must not be coerced
        // through a QML list<string> function parameter (Qt drops their values).
        const args = [];
        for (let i = 0; command && i < command.length; ++i)
            args.push(String(command[i]));
        if (!args.length) {
            console.warn("Start menu: empty action command");
            return;
        }
        root.visibilities.launcher = false;
        if (!SessionManager.exec(args))
            Quickshell.execDetached(args);
    }

    implicitWidth: Math.min(720, maxWidth - 40)
    implicitHeight: Math.min(880, maxHeight)

    Rectangle {
        anchors.fill: parent
        opacity: 1 - hermes.reveal
        radius: 24
        color: MenuStyle.smokeSurface
        border.width: 1
        border.color: MenuStyle.border
    }
    Shortcut { sequence: "Ctrl+K"; enabled: root.visibilities.launcher && !hermes.expanded; onActivated: search.forceActiveFocus() }
    StartHome {
        id: home
        anchors.top: searchWrapper.bottom
        anchors.topMargin: 14
        anchors.bottom: sessionFooter.top
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: root.padding
        anchors.rightMargin: root.padding
        visible: root.showHome
        opacity: 1 - hermes.reveal
        enabled: !hermes.expanded
        visibilities: root.visibilities
        onBrowse: { root.browsing = true; search.forceActiveFocus(); }
        onAccount: root.triggerSessionCommand(["kcmshell6", "kcm_users"])
    }

    Connections {
        function onClearHistoryFinished(success: bool): void {
            if (success) {
                if (GlobalConfig.utilities.toasts.clipboardChanged)
                    Toaster.toast(qsTr("Clipboard history cleared"), "", "delete");
            } else {
                Toaster.toast(qsTr("Failed to clear clipboard history"), "", "error");
            }
        }

        target: Clipboard
    }

    Item {
        id: listWrapper
        visible: !root.showHome
        opacity: 1 - hermes.reveal
        enabled: !hermes.expanded
        anchors.top: searchWrapper.bottom
        anchors.topMargin: askCard.visible ? 88 : 16
        anchors.bottom: sessionFooter.top
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: root.padding
        anchors.rightMargin: root.padding
        clip: true
        ContentList {
            id: list
            content: root
            visibilities: root.visibilities
            panels: root.panels
            maxWidth: listWrapper.width
            maxHeight: listWrapper.height
            search: search
            padding: root.padding
            rounding: root.rounding
        }
    }

    Item {
        id: sessionFooter
        opacity: 1 - hermes.reveal
        enabled: !hermes.expanded
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: root.padding
        height: 52
        implicitHeight: height
        Rectangle { width: parent.width; height: 1; color: Colours.light ? "#24969ca5" : "#26ffffff" }
        RowLayout {
            anchors.fill: parent
            anchors.topMargin: 12
            spacing: 4
            Repeater {
                model: [
                    {label: qsTr("Settings"), icon: "settings", command: ["flausen-settings"], power: false},
                    {label: qsTr("Restart into Windows"), icon: "windows", command: [], power: true, windows: true},
                    {label: qsTr("Lock"), icon: "lock", command: ["loginctl", "lock-session"], power: false},
                    {label: qsTr("Restart"), icon: "restart_alt", command: Config.session.commands.reboot, power: true},
                    {label: qsTr("Shut down"), icon: "power_settings_new", command: Config.session.commands.shutdown, power: true}
                ]
                delegate: Button {
                    id: action
                    required property var modelData
                    Layout.fillWidth: true
                    Layout.preferredWidth: implicitWidth
                    Layout.fillHeight: true
                    visible: (!modelData.power || Config.launcher.showPowerMenu) && (!modelData.windows || root.windowsAvailable)
                    enabled: !modelData.windows || !windowsReboot.running
                    onClicked: {
                        if (modelData.windows) {
                            if (!windowsReboot.running) {
                                root.visibilities.launcher = false;
                                windowsReboot.running = true;
                            }
                        } else root.triggerSessionCommand(modelData.command);
                    }
                    ToolTip.visible: hovered
                    ToolTip.text: modelData.label
                    background: Rectangle { radius: 10; color: action.hovered || action.visualFocus ? "#20ffffff" : "transparent" }
                    contentItem: RowLayout {
                        spacing: 6
                        Image {
                            visible: action.modelData.windows === true
                            source: Qt.resolvedUrl("windows.svg")
                            Layout.preferredWidth: 18
                            Layout.preferredHeight: 18
                            sourceSize.width: 36; sourceSize.height: 36
                        }
                        MaterialIcon { visible: !action.modelData.windows; text: action.modelData.icon; color: action.modelData.icon === "power_settings_new" ? "#ff625c" : Colours.palette.m3onSurface; fontStyle: Tokens.font.icon.small }
                        Text { Layout.fillWidth: true; text: action.modelData.label; color: Colours.palette.m3onSurface; font.pixelSize: 12; elide: Text.ElideRight }
                    }
                }
            }
        }
    }

    StyledRect {
        id: searchWrapper
        opacity: 1 - hermes.reveal
        enabled: !hermes.expanded

        color: Colours.light ? "#10000000" : "#10ffffff"
        radius: 17
        border.width: 1
        border.color: Colours.light ? "#26969ca5" : "#26ffffff"

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: root.padding

        height: 56
        implicitHeight: height

        MaterialIcon {
            id: searchIcon

            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: root.padding

            text: "search"
            color: Colours.palette.m3onSurfaceVariant
        }

        StyledTextField {
            id: search
            font.family: MenuStyle.fontFamily

            anchors.left: searchIcon.right
            anchors.right: clearClipboardIcon.left
            anchors.leftMargin: Tokens.spacing.small
            anchors.rightMargin: Tokens.spacing.small

            topPadding: Tokens.padding.medium
            bottomPadding: Tokens.padding.medium

            placeholderText: ""

            background: Item {}
            anchors.verticalCenter: parent.verticalCenter

            onAccepted: {
                if (text.trim() && !text.startsWith(GlobalConfig.launcher.actionPrefix)) {
                    root.askHermes();
                    return;
                }
                if (root.showHome) { root.browsing = true; return; }
                if (list.showAppsBrowser) {
                    list.currentList?.activateCurrent();
                    return;
                }

                const currentItem = list.currentList?.currentItem;
                if (currentItem) {
                    if (list.showWallpapers) {
                        Wallpapers.setWallpaper(currentItem.modelData.path);
                        root.visibilities.launcher = false;
                    } else if (text.startsWith(GlobalConfig.launcher.actionPrefix)) {
                        if (text.startsWith(`${GlobalConfig.launcher.actionPrefix}calc `))
                            currentItem.onClicked();
                        else if (text.startsWith(`${GlobalConfig.launcher.actionPrefix}emoji `) || text.startsWith(`${GlobalConfig.launcher.actionPrefix}clipboard `) || text.startsWith(`${GlobalConfig.launcher.actionPrefix}windows `) || text.startsWith(`${GlobalConfig.launcher.actionPrefix}keybinds `) || text.startsWith(`${GlobalConfig.launcher.actionPrefix}animations `))
                            currentItem.clicked();
                        else
                            currentItem.modelData.onClicked(list.currentList);
                    } else {
                        Apps.launch(currentItem.modelData);
                        root.visibilities.launcher = false;
                    }
                }
            }

            Keys.onUpPressed: {
                if (!list.showWallpapers)
                    list.currentList?.decrementCurrentIndex();
            }
            Keys.onDownPressed: {
                if (root.showHome) root.browsing = true;
                else if (!list.showWallpapers)
                    list.currentList?.incrementCurrentIndex();
            }
            Keys.onLeftPressed: event => {
                if (list.showWallpapers || list.showWindowSwitcher) {
                    list.currentList?.decrementCurrentIndex();
                    event.accepted = true;
                } else if (list.showAppsBrowser) {
                    list.currentList?.moveLeft();
                    event.accepted = true;
                } else {
                    event.accepted = false;
                }
            }
            Keys.onRightPressed: event => {
                if (list.showWallpapers || list.showWindowSwitcher) {
                    list.currentList?.incrementCurrentIndex();
                    event.accepted = true;
                } else if (list.showAppsBrowser) {
                    list.currentList?.moveRight();
                    event.accepted = true;
                } else {
                    event.accepted = false;
                }
            }

            Keys.onEscapePressed: {
                if (root.browsing && !search.text) { root.browsing = false; return; }
                Windows.isSwitching = false;
                Kwin.clearHighlight();
                root.visibilities.launcher = false;
            }

            Keys.onReleased: event => {
                if (Windows.isSwitching && text.startsWith(`${GlobalConfig.launcher.actionPrefix}windows `)) {
                    const switcherKey = (typeof KeybindsModel !== "undefined" && KeybindsModel.getKey("windowSwitcher")) || "Alt+Tab";
                    if (!CUtils.isShortcutModifierPressed(switcherKey)) {
                        Windows.focusSelectedWindow();
                        root.visibilities.launcher = false;
                        event.accepted = true;
                    }
                }
            }

            Keys.onPressed: event => {
                if (Windows.isSwitching && text.startsWith(`${GlobalConfig.launcher.actionPrefix}windows `)) {
                    if (event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab) {
                        if (event.modifiers & Qt.ShiftModifier || event.key === Qt.Key_Backtab) {
                            Windows.triggerCyclePrev();
                        } else {
                            Windows.triggerCycleNext();
                        }
                        event.accepted = true;
                        return;
                    }
                    if (event.key === Qt.Key_Left || event.key === Qt.Key_Up) {
                        Windows.triggerCyclePrev();
                        event.accepted = true;
                        return;
                    }
                    if (event.key === Qt.Key_Right || event.key === Qt.Key_Down) {
                        Windows.triggerCycleNext();
                        event.accepted = true;
                        return;
                    }
                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                        Windows.focusSelectedWindow();
                        root.visibilities.launcher = false;
                        event.accepted = true;
                        return;
                    }
                    if (event.key === Qt.Key_Escape) {
                        Windows.isSwitching = false;
                        Kwin.clearHighlight();
                        root.visibilities.launcher = false;
                        event.accepted = true;
                        return;
                    }
                }

                if (list.showAppsBrowser && event.key === Qt.Key_Tab) {
                    list.currentList?.toggleFocus();
                    event.accepted = true;
                    return;
                }

                if (!GlobalConfig.launcher.vimKeybinds)
                    return;

                if (event.modifiers & Qt.ControlModifier) {
                    if (event.key === Qt.Key_J || event.key === Qt.Key_N) {
                        list.currentList?.incrementCurrentIndex();
                        event.accepted = true;
                    } else if (event.key === Qt.Key_K || event.key === Qt.Key_P) {
                        list.currentList?.decrementCurrentIndex();
                        event.accepted = true;
                    }
                } else if (event.key === Qt.Key_Backtab || (event.key === Qt.Key_Tab && (event.modifiers & Qt.ShiftModifier))) {
                    list.currentList?.decrementCurrentIndex();
                    event.accepted = true;
                } else if (event.key === Qt.Key_Tab) {
                    list.currentList?.incrementCurrentIndex();
                    event.accepted = true;
                }
            }

            onTextChanged: {
                if (!text.startsWith(`${GlobalConfig.launcher.actionPrefix}windows `)) {
                    Windows.isSwitching = false;
                    Kwin.clearHighlight();
                }
            }

            Component.onCompleted: {
                if (Visibilities.launcherInitialSearch) {
                    text = Visibilities.launcherInitialSearch;
                    Visibilities.launcherInitialSearch = "";
                }
                forceActiveFocus();
            }

            Connections {
                function onLauncherChanged(): void {
                    if (root.visibilities.launcher) {
                        // Every open decides the field: the requested prefix, or the app grid.
                        root.browsing = false;
                        search.text = Visibilities.launcherInitialSearch;
                        Visibilities.launcherInitialSearch = "";
                        if (hermes.expanded) hermes.focusComposer();
                        else search.forceActiveFocus();
                    } else {
                        Windows.isSwitching = false;
                        Kwin.clearHighlight();
                        Wallpapers.stopPreview();
                    }
                }

                function onSessionChanged(): void {
                    if (!root.visibilities.session) {
                        if (hermes.expanded) hermes.focusComposer();
                        else search.forceActiveFocus();
                    }
                }

                target: root.visibilities
            }

            Connections {
                function onClosed(): void {
                    search.text = "";
                    root.browsing = false;
                }

                target: root.panels.launcher
            }

            Connections {
                function onModifierReleased(): void {
                    if (Windows.isSwitching && root.visibilities.launcher && search.text.startsWith(`${GlobalConfig.launcher.actionPrefix}windows `)) {
                        const switcherKey = (typeof KeybindsModel !== "undefined" && KeybindsModel.getKey("windowSwitcher")) || "Alt+Tab";
                        if (!CUtils.isShortcutModifierPressed(switcherKey)) {
                            Windows.focusSelectedWindow();
                            root.visibilities.launcher = false;
                        }
                    }
                }

                target: CUtils
            }
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter
            x: search.x + search.leftPadding
            width: Math.max(0, search.width - search.leftPadding - search.rightPadding)
            visible: !search.text
            text: qsTr("Search apps or ask Hermes …")
            color: Colours.palette.m3onSurfaceVariant
            font: search.font
            elide: Text.ElideRight
        }

        MaterialIcon {
            id: clearClipboardIcon

            anchors.verticalCenter: parent.verticalCenter
            anchors.right: clearIcon.left
            anchors.rightMargin: (root.isClipboardMode && Clipboard.items.length > 0) ? Tokens.spacing.small : 0

            width: (root.isClipboardMode && Clipboard.items.length > 0) ? implicitWidth : 0
            opacity: (root.isClipboardMode && Clipboard.items.length > 0) ? 1 : 0

            text: "delete"
            color: clipboardMouse.containsMouse ? Colours.palette.m3error : Colours.palette.m3onSurfaceVariant

            MouseArea {
                id: clipboardMouse

                anchors.fill: parent
                hoverEnabled: true
                cursorShape: (root.isClipboardMode && Clipboard.items.length > 0) ? Qt.PointingHandCursor : undefined

                onClicked: {
                    if (!root.isClipboardMode || Clipboard.items.length === 0)
                        return;

                    if (GlobalConfig.launcher.confirmClearClipboard)
                        clearClipboardConfirmPopup.open();
                    else
                        root.clearClipboardHistory();
                }
            }

            Behavior on color {
                CAnim {}
            }

            Behavior on width {
                Anim {
                    type: Anim.StandardSmall
                }
            }

            Behavior on opacity {
                Anim {
                    type: Anim.StandardSmall
                }
            }
        }

        MaterialIcon {
            id: clearIcon

            anchors.verticalCenter: parent.verticalCenter
            anchors.right: commandsBtn.left
            anchors.rightMargin: search.text ? Tokens.spacing.small : 0

            width: search.text ? implicitWidth : 0
            opacity: search.text ? 1 : 0

            text: "close"
            color: mouse.containsMouse ? Colours.palette.m3primary : Colours.palette.m3onSurfaceVariant

            MouseArea {
                id: mouse

                anchors.fill: parent
                hoverEnabled: true
                cursorShape: search.text ? Qt.PointingHandCursor : undefined

                onClicked: search.text = ""
            }

            Behavior on color {
                CAnim {}
            }

            Behavior on width {
                Anim {
                    type: Anim.StandardSmall
                }
            }

            Behavior on opacity {
                Anim {
                    type: Anim.StandardSmall
                }
            }
        }

        IconButton {
            id: commandsBtn

            isToggle: true
            type: IconButton.Text
            implicitWidth: 32
            implicitHeight: 32
            radius: Tokens.rounding.full
            radiusMorph: false
            icon: root.browsing ? "arrow_back" : "terminal"

            anchors.verticalCenter: parent.verticalCenter
            anchors.right: hermesButton.left
            anchors.rightMargin: 4
            checked: search.text.startsWith(GlobalConfig.launcher.actionPrefix)

            onClicked: {
                if (root.browsing && !search.text) {
                    root.browsing = false;
                } else if (search.text.startsWith(GlobalConfig.launcher.actionPrefix)) {
                    search.text = "";
                } else {
                    search.text = GlobalConfig.launcher.actionPrefix;
                }
                search.forceActiveFocus();
                search.cursorPosition = search.text.length;
            }
        }

        Button {
            id: hermesButton
            anchors.right: parent.right
            anchors.rightMargin: 10
            anchors.verticalCenter: parent.verticalCenter
            implicitWidth: 36; implicitHeight: 36
            ToolTip.visible: hovered
            ToolTip.text: hermes.busy ? qsTr("Hermes is working · Open conversation") : qsTr("Open Hermes")
            background: Rectangle { radius: 11; color: hermesButton.hovered || hermes.busy ? Qt.alpha(Colours.palette.m3primary, 0.18) : "transparent" }
            contentItem: MaterialIcon { text: "auto_awesome"; color: Colours.palette.m3primary; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            onClicked: {
                if (search.text.trim() && !hermes.busy) root.askHermes();
                else { hermes.expanded = true; hermes.focusComposer(); }
            }
        }
    }

    Button {
        id: askCard
        anchors.top: searchWrapper.bottom
        anchors.topMargin: 12
        anchors.left: parent.left; anchors.right: parent.right
        anchors.leftMargin: root.padding; anchors.rightMargin: root.padding
        height: 62
        visible: search.text.trim().length > 0 && !search.text.startsWith(GlobalConfig.launcher.actionPrefix) && !hermes.expanded
        enabled: !hermes.busy
        background: Rectangle {
            radius: 14
            color: Qt.alpha(Colours.palette.m3primary, askCard.hovered ? 0.16 : 0.08)
            border.width: 1; border.color: Qt.alpha(Colours.palette.m3primary, 0.18)
        }
        contentItem: RowLayout {
            spacing: 12
            MaterialIcon { text: "auto_awesome"; color: Colours.palette.m3primary }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 3
                Text { text: hermes.busy ? qsTr("Hermes is still working …") : qsTr("Ask Hermes"); color: Colours.palette.m3onSurface; font.pixelSize: 13; font.weight: Font.DemiBold }
                Text { Layout.fillWidth: true; text: qsTr("Ask Hermes · Click an app below to open it"); color: Colours.palette.m3onSurfaceVariant; font.pixelSize: 11; elide: Text.ElideRight }
            }
            Text { text: "↵"; color: Colours.palette.m3primary; font.pixelSize: 20 }
        }
        onClicked: root.askHermes()
    }

    Popup {
        id: clearClipboardConfirmPopup

        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        x: Math.round((root.width - width) / 2)
        y: Math.round((root.height - height) / 2)

        padding: Tokens.padding.large

        contentItem: Column {
            spacing: Tokens.spacing.medium

            StyledText {
                text: qsTr("Clear clipboard history?")
                font: Tokens.font.body.builders.large.weight(Font.Medium).build()
            }

            StyledText {
                text: qsTr("This removes all clipboard entries.")
                color: Colours.palette.m3onSurfaceVariant
                font: Tokens.font.body.small
            }

            Row {
                spacing: Tokens.spacing.small

                TextButton {
                    text: qsTr("Cancel")
                    onClicked: clearClipboardConfirmPopup.close()
                }

                TextButton {
                    text: qsTr("Clear")
                    type: TextButton.Filled
                    onClicked: {
                        clearClipboardConfirmPopup.close();
                        root.clearClipboardHistory();
                    }
                }
            }
        }

        background: StyledRect {
            radius: Tokens.rounding.large
            color: Colours.palette.m3surfaceContainer
        }
    }
}
