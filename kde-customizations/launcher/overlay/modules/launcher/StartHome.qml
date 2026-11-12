pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Quickshell.Widgets
import Caelestia.Config
import qs.components
import qs.services
import qs.utils
import qs.modules.launcher.services
import qs.modules.launcher.items

Flickable {
    id: root
    required property DrawerVisibilities visibilities
    signal browse()
    signal account()
    property var user: ({name: Quickshell.env("USER"), detail: "", face: "", recent: []})
    property bool more: false
    property var apps: []
    function refreshApps(): void {
        const next = Apps.recentApps.slice(0, 12);
        if (next.length !== apps.length || next.some((app, index) => app.id !== apps[index].id))
            apps = next;
    }
    Timer { id: appRefresh; interval: 16; onTriggered: root.refreshApps() }
    Connections {
        target: Apps
        function onRecentAppsChanged(): void { appRefresh.restart(); }
    }
    readonly property color ink: MenuStyle.ink
    readonly property color muted: MenuStyle.muted
    readonly property color line: MenuStyle.rule
    contentHeight: body.height
    clip: true
    boundsBehavior: Flickable.StopAtBounds
    ScrollBar.vertical: ScrollBar {}
    function refresh(): void { if (!data.running) data.running = true; }
    function launch(app): void { Apps.launch(app); root.visibilities.launcher = false; }
    Component.onCompleted: { refresh(); appRefresh.restart(); }
    Connections {
        target: root.visibilities
        function onLauncherChanged(): void { if (root.visibilities.launcher) { root.refresh(); appRefresh.restart(); root.more = false; root.contentY = 0; } }
    }
    Process {
        id: data
        command: ["python3", Qt.resolvedUrl("start-data.py").toString().replace("file://", "")]
        stdout: StdioCollector { onStreamFinished: { try { root.user = JSON.parse(text); } catch (e) { console.warn("Start menu data:", e); } } }
    }
    AppContextMenu { id: context; visibilities: root.visibilities; attachTo: root }
    Column {
        id: body
        width: root.width
        spacing: 18
        Button {
            width: parent.width; height: 72
            onClicked: root.account()
            background: Rectangle { radius: 14; color: parent.hovered || parent.visualFocus ? (Colours.light ? "#10000000" : "#10ffffff") : "transparent" }
            contentItem: Item {
                ClippingRectangle {
                    width: 52; height: 52
                    anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                    radius: 26; antialiasing: true
                    color: Colours.light ? "#dce2ea" : "#303b4c"
                    Image {
                        anchors.fill: parent
                        source: root.user.face ? "file://" + root.user.face : ""
                        fillMode: Image.PreserveAspectCrop
                        smooth: true
                        mipmap: true
                    }
                    Text { anchors.centerIn: parent; visible: !root.user.face; text: root.user.name.substring(0, 1).toUpperCase(); color: root.ink; font.pixelSize: 23 }
                }
                Column {
                    x: 66; anchors.verticalCenter: parent.verticalCenter; spacing: 4
                    Text { text: root.user.name; color: root.ink; font.pixelSize: MenuStyle.bodyPixels }
                    Text { text: root.user.detail; color: root.muted; font.pixelSize: MenuStyle.secondaryPixels }
                }
                MaterialIcon { anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; text: "chevron_right"; color: root.muted }
            }
        }

        Rectangle { width: parent.width; height: 1; color: root.line }
        RowLayout {
            width: parent.width
            Text { text: qsTr("Recent apps"); color: root.ink; font.pixelSize: MenuStyle.bodyPixels; Layout.fillWidth: true }
            Button {
                text: qsTr("All apps  ›"); onClicked: root.browse()
                contentItem: Text { text: parent.text; color: root.ink; font.pixelSize: MenuStyle.secondaryPixels; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                background: Rectangle { radius: 12; color: parent.hovered || parent.visualFocus ? "#28ffffff" : "#12ffffff"; border.color: root.line }
            }
        }
        Grid {
            width: parent.width; columns: root.width < 540 ? 4 : 6
            columnSpacing: 12; rowSpacing: 14
            Repeater {
                model: ScriptModel { values: root.apps }
                delegate: Button {
                    id: tile
                    required property var modelData
                    width: Math.floor((root.width - 12 * ((root.width < 540 ? 4 : 6) - 1)) / (root.width < 540 ? 4 : 6)); height: 112
                    hoverEnabled: true
                    Accessible.name: modelData.name
                    onClicked: root.launch(modelData)
                    background: Rectangle { radius: 14; color: tile.hovered || tile.visualFocus ? "#18ffffff" : "transparent"; border.width: tile.visualFocus ? 1 : 0; border.color: root.muted }
                    contentItem: Column {
                        spacing: 9
                        Rectangle {
                            width: 66; height: 66; radius: 16
                            anchors.horizontalCenter: parent.horizontalCenter
                            color: MenuStyle.cardFill
                            border.color: root.line
                            IconImage { anchors.centerIn: parent; implicitSize: 38; source: Quickshell.iconPath(tile.modelData.icon, "application-x-executable") }
                        }
                        Text { width: parent.width; text: tile.modelData.name; color: root.ink; font.pixelSize: MenuStyle.captionPixels; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.Wrap; maximumLineCount: 2; elide: Text.ElideRight }
                    }
                    TapHandler { acceptedButtons: Qt.RightButton; onTapped: context.openFor(tile.modelData, tile) }
                    ToolTip.visible: hovered
                    ToolTip.text: modelData.name
                }
            }
        }
        Text { visible: root.apps.length === 0; text: qsTr("Your recently used apps appear here."); color: root.muted }
        Rectangle { width: parent.width; height: 1; color: root.line }
        RowLayout {
            width: parent.width
            Text { text: qsTr("Recently opened"); color: root.ink; font.pixelSize: MenuStyle.bodyPixels; Layout.fillWidth: true }
            Button {
                visible: root.user.recent.length > 3
                text: root.more ? qsTr("Less  ‹") : qsTr("More  ›")
                onClicked: root.more = !root.more
                contentItem: Text { text: parent.text; color: root.ink; font.pixelSize: MenuStyle.secondaryPixels; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                background: Rectangle { radius: 12; color: parent.hovered || parent.visualFocus ? "#28ffffff" : "#12ffffff"; border.color: root.line }
            }
        }
        Column {
            width: parent.width; spacing: 2
            Repeater {
                model: root.user.recent.slice(0, root.more ? 12 : 3)
                delegate: Button {
                    id: recent
                    required property var modelData
                    width: parent.width; height: 60
                    onClicked: { Qt.openUrlExternally(modelData.uri); root.visibilities.launcher = false; }
                    background: Rectangle { radius: 12; color: parent.hovered || parent.visualFocus ? "#18ffffff" : "transparent" }
                    contentItem: RowLayout {
                        spacing: 16
                        IconImage { implicitSize: 30; source: Quickshell.iconPath(recent.modelData.icon) }
                        ColumnLayout {
                            Layout.fillWidth: true; spacing: 4
                            Text { Layout.fillWidth: true; text: recent.modelData.title; color: root.ink; font.pixelSize: MenuStyle.listPixels; elide: Text.ElideMiddle }
                            Text { Layout.fillWidth: true; text: recent.modelData.detail; color: root.muted; font.pixelSize: MenuStyle.captionPixels; elide: Text.ElideMiddle }
                        }
                        MaterialIcon { text: "chevron_right"; color: root.muted }
                    }
                }
            }
            Text { visible: root.user.recent.length === 0; text: qsTr("No recently opened files yet"); color: root.muted; font.pixelSize: MenuStyle.secondaryPixels; height: 64; verticalAlignment: Text.AlignVCenter }
        }
    }
}
