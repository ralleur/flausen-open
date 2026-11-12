pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Caelestia
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services
import qs.utils

Item {
    id: root

    required property PopoutState popouts
    property var model: popouts.dockModel

    readonly property bool isBattlenet: {
        const ids = [model?.id, model?.entry?.id];
        return ids.some(id => id && String(id).replace(/\.desktop$/, "") === "lab-battlenet");
    }
    property bool framegenEnabled: false
    property bool framegenRunning: false
    property bool framegenReady: false
    property string framegenError: ""
    readonly property string framegenHelper: Quickshell.env("HOME") + "/Projekte/linux-gaming-lab/bin/battlenet-framegen"

    function refreshFramegen(): void {
        if (isBattlenet && !framegenRead.running && !framegenWrite.running)
            framegenRead.running = true;
    }

    function acceptFramegen(text: string): void {
        try {
            const state = JSON.parse(text);
            if (typeof state.enabled !== "boolean" || typeof state.running !== "boolean")
                throw new Error(state.error || qsTranslate("Flausen", "Frame generation unavailable"));
            framegenEnabled = state.enabled;
            framegenRunning = state.running;
            framegenError = "";
            framegenReady = true;
        } catch (error) {
            framegenReady = false;
            framegenError = String(error.message);
        }
    }

    Timer {
        interval: 750
        repeat: true
        triggeredOnStart: true
        running: root.isBattlenet && root.popouts.hasCurrent && root.popouts.currentName === "dockcontext"
        onTriggered: root.refreshFramegen()
    }

    Process {
        id: framegenRead
        command: [root.framegenHelper, "status"]
        stdout: StdioCollector {
            onStreamFinished: root.acceptFramegen(text)
        }
        onExited: code => {
            if (code !== 0) {
                root.framegenReady = false;
                root.framegenError = qsTr("Frame generation unavailable");
            }
        }
    }

    Process {
        id: framegenWrite
        property string action: "off"
        command: [root.framegenHelper, action]
        stdout: StdioCollector {
            onStreamFinished: root.acceptFramegen(text)
        }
        onExited: root.refreshFramegen()
    }

    property bool isPinned: {
        if (!model)
            return false;
        const current = GlobalConfig.bar.dock.pinnedApps || [];
        for (let i = 0; i < current.length; i++) {
            if (model.id === current[i] || (model.entry && model.entry.id === current[i])) {
                return true;
            }
        }
        return false;
    }

    property real scaleOffset: 1.0
    property real fontScale: 1.0
    property bool _isSidebarOpen: false

    // Geometry follows the mock independently of the shared font/material roles.
    readonly property real rowHeight: 40 * scaleOffset
    readonly property bool canQuit: {
        if (!model?.toplevels?.length) return false;
        return !model.toplevels.some(t => t.title && String(t.title).startsWith("Nexus"));
    }
    width: implicitWidth
    implicitWidth: Math.max(250 * scaleOffset, pinItem.implicitWidth, newWinItem.implicitWidth, quitItem.implicitWidth)
    implicitHeight: actions.implicitHeight
    height: implicitHeight

    component ActionRow: Rectangle {
        id: action
        required property string text
        required property string icon
        property color iconColour: MenuStyle.ink
        signal triggered()
        Layout.fillWidth: true
        implicitWidth: label.implicitWidth + 68 * root.scaleOffset
        implicitHeight: Math.max(root.rowHeight, label.implicitHeight + 16 * root.scaleOffset)
        radius: 10 * root.scaleOffset
        color: mouse.pressed ? Qt.alpha(MenuStyle.accent, 0.25)
             : mouse.containsMouse || activeFocus ? Qt.alpha(MenuStyle.accent, 0.16) : "transparent"
        activeFocusOnTab: visible && enabled
        Accessible.role: Accessible.MenuItem
        Accessible.name: text
        Accessible.onPressAction: triggered()
        Keys.onReturnPressed: triggered()
        Keys.onEnterPressed: triggered()
        Keys.onSpacePressed: triggered()

        MaterialIcon {
            anchors.left: parent.left
            anchors.leftMargin: 16 * root.scaleOffset
            anchors.verticalCenter: parent.verticalCenter
            text: action.icon
            color: action.iconColour
            fontStyle.pointSize: 20 * 0.75 * root.scaleOffset
        }
        MenuText {
            id: label
            anchors.left: parent.left
            anchors.leftMargin: 60 * root.scaleOffset
            anchors.verticalCenter: parent.verticalCenter
            text: action.text
            font.pointSize: MenuStyle.bodyPointSize(root.fontScale)
        }
        MouseArea {
            id: mouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: action.triggered()
        }
    }

    ColumnLayout {
        id: actions
        width: parent.width
        spacing: 4 * root.scaleOffset

        ActionRow {
            id: pinItem
            visible: root.model?.entry != null
            text: root.isPinned ? qsTr("Unpin from dock") : qsTr("Pin to dock")
            icon: root.isPinned ? "keep_off" : "keep"
            onTriggered: {
                if (isPinned) {
                    const current = GlobalConfig.bar.dock.pinnedApps ? [...GlobalConfig.bar.dock.pinnedApps] : [];
                    let index = current.indexOf(model.id);
                    if (index === -1 && model.entry)
                        index = current.indexOf(model.entry.id);
                    if (index !== -1) {
                        current.splice(index, 1);
                        GlobalConfig.bar.dock.pinnedApps = current;
                    }
                } else {
                    const current = GlobalConfig.bar.dock.pinnedApps ? [...GlobalConfig.bar.dock.pinnedApps] : [];
                    const idToPin = model.entry ? model.entry.id : model.id;
                    if (!current.includes(idToPin)) {
                        current.push(idToPin);
                        GlobalConfig.bar.dock.pinnedApps = current;
                    }
                }
                root.popouts.hasCurrent = false;
            }
        }
        ActionRow {
            id: newWinItem
            visible: root.model?.entry != null
            text: qsTr("Open new window")
            icon: "add_to_queue"
            onTriggered: {
                if (root.model.entry) Launch.launchEntry(root.model.entry);
                root.popouts.hasCurrent = false;
            }
        }
        ColumnLayout {
            Layout.fillWidth: true
            visible: root.isBattlenet
            spacing: Tokens.spacing.small * root.scaleOffset

            RowLayout {
                Layout.fillWidth: true
                enabled: root.framegenReady && !root.framegenRunning && !framegenWrite.running

                MenuText {
                    Layout.fillWidth: true
                    text: qsTr("Framegen")
                    color: parent.enabled ? Colours.palette.m3onSurface : Colours.disabledContent
                    font.pointSize: MenuStyle.bodyPointSize(root.fontScale)
                }

                StyledSwitch {
                    id: framegenSwitch
                    Binding {
                        target: framegenSwitch
                        property: "checked"
                        value: root.framegenEnabled
                    }
                    onToggled: {
                        framegenWrite.action = checked ? "on" : "off";
                        framegenWrite.running = true;
                    }
                }
            }

            MenuText {
                Layout.fillWidth: true
                visible: root.framegenRunning || root.framegenError !== ""
                text: root.framegenError || qsTr("Close Battle.net or WoW first")
                color: Colours.disabledContent
                wrapMode: Text.WordWrap
                font.pointSize: MenuStyle.bodyPointSize(root.fontScale) * MenuStyle.secondaryPixels / MenuStyle.bodyPixels
            }
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.leftMargin: 8 * root.scaleOffset
            Layout.rightMargin: 8 * root.scaleOffset
            Layout.topMargin: 8 * root.scaleOffset
            Layout.bottomMargin: 8 * root.scaleOffset
            implicitHeight: 1
            color: MenuStyle.rule
            visible: root.canQuit && (pinItem.visible || root.isBattlenet)
        }
        ActionRow {
            id: quitItem
            visible: root.canQuit
            text: qsTr("Quit app")
            icon: "power_settings_new"
            iconColour: Colours.palette.m3error
            onTriggered: {
                for (const toplevel of model.toplevels) {
                    if (toplevel.pid) {
                        Quickshell.execDetached({ command: ["kill", "-15", String(toplevel.pid)] });
                    } else if (Kwin.windowList.length > 0) {
                        Kwin.closeWindow(toplevel.address);
                    } else {
                        Kwin.dispatch(Kwin.usingLua ? `hl.dsp.window.close({ window = "address:0x${toplevel.address}" })` : `closewindow address:0x${toplevel.address}`);
                    }
                }
                root.popouts.hasCurrent = false;
            }
        }
    }
}
