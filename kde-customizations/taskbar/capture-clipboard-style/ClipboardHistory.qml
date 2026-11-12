pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.components.images
import qs.services
import qs.modules.launcher.services as Launcher

StyledRect {
    id: root
    required property var popouts
    property real scaleOffset: 1.0
    property real fontScale: 1.0
    property bool _isSidebarOpen: false
    property string feedback: ""
    readonly property real bodyPointSize:MenuStyle.bodyPointSize(root.fontScale)
    readonly property var entries: Launcher.Clipboard.getSortedItems()

    width: 420*root.scaleOffset
    implicitWidth:width
    implicitHeight: layout.implicitHeight + 7*root.scaleOffset*2
    radius: Tokens.rounding.large
    color: "transparent"

    Component.onCompleted: Launcher.Clipboard.reload()

    function copyEntry(entry: var): void {
        if (copyProcess.running)
            return;
        if (entry.isPinned) {
            Launcher.Clipboard.copyPinned(entry.pinId);
            root.feedback = qsTr("Copied");
            feedbackTimer.restart();
        } else {
            copyProcess.command = ["bash", "-o", "pipefail", "-c", 'cliphist decode "$1" | wl-copy', "clipboard-popout", String(entry.id)];
            copyProcess.running = true;
        }
    }

    Process {
        id: copyProcess
        onExited: (exitCode, exitStatus) => {
            root.feedback = exitCode === 0 ? qsTr("Copied") : qsTr("Copy failed");
            feedbackTimer.restart();
        }
    }
    Timer {
        id: feedbackTimer
        interval: 2200
        onTriggered: root.feedback = ""
    }

    ColumnLayout {
        id: layout
        anchors.fill: parent
        anchors.margins: 7*root.scaleOffset
        spacing: 14*root.scaleOffset

        RowLayout {
            Layout.fillWidth: true
            spacing: 14*root.scaleOffset
            Layout.leftMargin:5*root.scaleOffset
            Layout.rightMargin:5*root.scaleOffset
            StyledRect {
                implicitWidth: implicitHeight
                implicitHeight: 38*root.scaleOffset
                radius: 12*root.scaleOffset
                color: Qt.alpha(MenuStyle.accent,0.18)
                MaterialIcon {
                    id: headerIcon
                    anchors.centerIn: parent
                    text: "attach_file"
                    color: MenuStyle.accent
                    fontStyle: Tokens.font.icon.builders.medium.size(Tokens.font.icon.medium.pointSize*root.scaleOffset).build()
                }
            }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 0
                MenuText {
                    Layout.fillWidth: true
                    text: qsTr("Clipboard")
                    font.pointSize: root.bodyPointSize*1.68
                }
                MenuText {
                    Layout.fillWidth: true
                    text: root.feedback || qsTr("%1 entries · Click to copy").arg(root.entries.length)
                    color: root.feedback ? MenuStyle.accent : MenuStyle.muted
                    font.pointSize: root.bodyPointSize*0.81
                    elide: Text.ElideRight
                }
            }
        }

        ListView {
            id: history
            Layout.fillWidth: true
            implicitHeight: Math.min(contentHeight, 380)
            clip: true
            spacing: 12*root.scaleOffset
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: ScrollBar {}
            model: ScriptModel { values: root.entries }

            delegate: StyledRect {
                id: entryRow
                required property var modelData
                width: history.width
                implicitHeight: modelData.isImage ? 88*root.scaleOffset : Math.max(55*root.scaleOffset,entryText.implicitHeight+20*root.scaleOffset)
                radius: 14*root.scaleOffset
                color: MenuStyle.cardFill
                border.width:1
                border.color:MenuStyle.rule
                property string imagePath: modelData.isPinned ? (modelData.imagePath ?? "")
                    : (modelData.isImage && Launcher.Clipboard.isImageCached(modelData.id)
                        ? Launcher.Clipboard.getImagePath(modelData.id) : "")
                Connections {
                    target: Launcher.Clipboard
                    function onImageReady(id: int, path: string): void {
                        if (entryRow.modelData.isImage && id === entryRow.modelData.id)
                            entryRow.imagePath = path;
                    }
                }
                StateLayer {
                    radius: entryRow.radius
                    onClicked: root.copyEntry(entryRow.modelData)
                }
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12*root.scaleOffset
                    spacing: 14*root.scaleOffset
                    MaterialIcon {
                        Layout.preferredWidth:30*root.scaleOffset
                        text: entryRow.modelData.isImage ? "image" : "content_paste"
                        color: MenuStyle.muted
                    }
                    CachingImage {
                        visible: entryRow.modelData.isImage && !!entryRow.imagePath
                        Layout.preferredWidth: 100
                        Layout.fillHeight: true
                        path: entryRow.imagePath
                        fillMode: Image.PreserveAspectFit
                    }
                    MenuText {
                        id:entryText
                        Layout.fillWidth: true
                        text: entryRow.modelData.isImage ? qsTr("Image") : entryRow.modelData.preview
                        font.pointSize: root.bodyPointSize
                        maximumLineCount: 2
                        wrapMode: Text.Wrap
                        elide: Text.ElideRight
                    }
                    IconButton {
                        icon: entryRow.modelData.isPinned ? "keep" : "keep_off"
                        type: IconButton.Text
                        ToolTip.visible: hovered
                        ToolTip.text: entryRow.modelData.isPinned ? qsTr("Unpin") : qsTr("Pin")
                        onClicked: {
                            if (entryRow.modelData.isPinned)
                                Launcher.Clipboard.unpin(entryRow.modelData.pinId);
                            else
                                Launcher.Clipboard.pin(entryRow.modelData.id);
                        }
                    }
                }
            }
        }
        MenuText {
            Layout.fillWidth: true
            visible: root.entries.length === 0
            text: Launcher.Clipboard.available ? qsTr("No entries yet") : qsTr("Clipboard history unavailable")
            font.pointSize: root.bodyPointSize*0.81
            color: MenuStyle.muted
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
