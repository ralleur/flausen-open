pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import Quickshell
import Caelestia.Config
import qs.components
import qs.services
import qs.modules.bar
import qs.modules.nexus

Item {
    id: root
    required property PopoutState popouts
    property bool workspaceMenu: false
    readonly property int desktopCount: Kwin.workspaces.length
    readonly property int selectedWorkspace: Kwin.workspaces.find(desktop => desktop.id === popouts.selectedWorkspaceId)?.index ?? 0
    Config.screen: QsWindow.window?.screen.name ?? ""
    property real scaleOffset: 1.0
    property real fontScale: 1.0
    property bool _isSidebarOpen: false
    readonly property real rowHeight: 40 * scaleOffset
    width: implicitWidth
    height: implicitHeight
    implicitWidth: workspaceMenu
        ? Math.max(250 * scaleOffset, addDesktop.implicitWidth, removeDesktop.implicitWidth, workspaceSettings.implicitWidth, modules.implicitWidth)
        : Math.max(250 * scaleOffset, manager.implicitWidth, settings.implicitWidth, lock.implicitWidth, autoHide.implicitWidth)
    implicitHeight: actions.implicitHeight

    component ActionRow: Rectangle {
        id: action
        required property string text
        required property string icon
        property color iconColour: MenuStyle.ink
        property bool checkable: false
        property bool checked: false
        signal triggered()
        Layout.fillWidth: true
        implicitWidth: label.implicitWidth + (checkable ? 104 : 68) * root.scaleOffset
        implicitHeight: Math.max(root.rowHeight, label.implicitHeight + 16 * root.scaleOffset)
        radius: 10 * root.scaleOffset
        color: mouse.pressed ? Qt.alpha(MenuStyle.accent, 0.25)
             : mouse.containsMouse || activeFocus ? Qt.alpha(MenuStyle.accent, 0.16) : "transparent"
        opacity: enabled ? 1 : 0.45
        activeFocusOnTab: visible && enabled
        Accessible.role: checkable ? Accessible.CheckBox : Accessible.MenuItem
        Accessible.checkable: checkable
        Accessible.checked: checked
        Accessible.name: text
        Accessible.onPressAction: { if (action.enabled) action.triggered(); }
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
        MaterialIcon {
            anchors.right: parent.right
            anchors.rightMargin: 12 * root.scaleOffset
            anchors.verticalCenter: parent.verticalCenter
            visible: action.checkable && action.checked
            text: "check"
            color: MenuStyle.ink
            fontStyle.pointSize: 15 * root.scaleOffset
        }
        MouseArea {
            id: mouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: action.triggered()
        }
    }

    function openSettings(index: int): void {
        popouts.hasCurrent = false;
        WindowFactory.create(null, {
            initialPageIdx: PageRegistry.indexForKey("panels"),
            initialSubPageIdx: index
        });
    }

    ColumnLayout {
        id: actions
        width: parent.width
        spacing: 4 * root.scaleOffset
        ActionRow {
            id: addDesktop
            visible: root.workspaceMenu
            enabled: root.desktopCount > 0 && root.desktopCount < 8
            text: qsTr("Create desktop")
            icon: "add"
            onTriggered: {
                Kwin.createWorkspace("");
                root.popouts.hasCurrent = false;
            }
        }
        ActionRow {
            id: removeDesktop
            visible: root.workspaceMenu
            enabled: root.desktopCount > 1 && root.selectedWorkspace > 0
            text: root.selectedWorkspace > 0 ? qsTr("Remove desktop %1").arg(root.selectedWorkspace) : qsTr("Remove desktop")
            icon: "remove"
            onTriggered: {
                Kwin.removeWorkspace(root.popouts.selectedWorkspaceId);
                root.popouts.hasCurrent = false;
            }
        }
        ActionRow {
            id: manager
            visible: !root.workspaceMenu
            text: qsTr("Task manager")
            icon: "monitoring"
            onTriggered: {
                root.popouts.hasCurrent = false;
                Quickshell.execDetached(["flausen-task-manager"]);
            }
        }
        ActionRow {
            id: settings
            visible: !root.workspaceMenu
            text: qsTr("Taskbar settings")
            icon: "settings"
            onTriggered: root.openSettings(2)
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.leftMargin: 8 * root.scaleOffset
            Layout.rightMargin: 8 * root.scaleOffset
            Layout.topMargin: 8 * root.scaleOffset
            Layout.bottomMargin: 8 * root.scaleOffset
            implicitHeight: 1
            color: MenuStyle.rule
        }
        ActionRow {
            id: workspaceSettings
            visible: root.workspaceMenu
            text: qsTranslate("Content", "Workspaces settings")
            icon: "settings"
            onTriggered: root.openSettings(7)
        }
        ActionRow {
            id: modules
            visible: root.workspaceMenu
            text: qsTranslate("Content", "Elements & Modules")
            icon: "widgets"
            onTriggered: root.openSettings(15)
        }
        ActionRow {
            id: lock
            visible: !root.workspaceMenu
            text: SplitBarSettings.taskbarUnlocked ? qsTr("Lock Taskbar") : qsTr("Unlock to move")
            icon: SplitBarSettings.taskbarUnlocked ? "lock" : "open_with"
            onTriggered: {
                SplitBarSettings.setTaskbarUnlocked(!SplitBarSettings.taskbarUnlocked);
                root.popouts.hasCurrent = false;
            }
        }
        ActionRow {
            id: autoHide
            visible: !root.workspaceMenu
            text: qsTr("Auto Hide")
            icon: "visibility_off"
            checkable: true
            checked: !Config.bar.persistent && Config.bar.showOnHover
            onTriggered: {
                const enabled = !checked;
                const config = GlobalConfig.bar;
                config.showOnHover = true;
                config.persistent = !enabled;
                const bar = Visibilities.bars.get(QsWindow.window.screen.name);
                if (bar) bar.visibilities.bar = false;
                root.popouts.hasCurrent = false;
            }
        }
    }
}
