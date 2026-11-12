pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.folderlistmodel
import Quickshell
import Quickshell.Io
import Caelestia
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.modules.screenshot
import qs.utils
import qs.services

ColumnLayout {
    id: root

    property real scaleOffset: 1.15
    property real fontScale: 1.15
    readonly property real bodyPointSize:MenuStyle.bodyPointSize(root.fontScale)
    required property var props
    required property DrawerVisibilities visibilities

    property string selectedPath: ""
    property url selectedUrl
    property size selectedSize: Qt.size(0, 0)
    // Thumbnails stay bounded; read native dimensions only for the selection.
    onSelectedPathChanged: {
        selectedSize = Qt.size(0, 0);
        requestDimensions();
    }
    function requestDimensions(): void {
        if (!selectedPath || dimensions.running) return;
        dimensions.path = selectedPath;
        dimensions.command = ["magick", "identify", "-ping", "-format", "%w %h", selectedPath];
        dimensions.running = true;
    }
    Process {
        id: dimensions
        property string path
        stdout: StdioCollector {
            onStreamFinished: {
                if (dimensions.path !== root.selectedPath) return;
                const parts = text.trim().split(/\s+/).map(Number);
                if (parts.length === 2 && parts.every(n => n > 0)) root.selectedSize = Qt.size(parts[0], parts[1]);
            }
        }
        onExited: (code, status) => {
            if (dimensions.path !== root.selectedPath) root.requestDimensions();
        }
    }
    property bool newestFirst: true
    readonly property bool hasSelection: selectedPath !== ""
    function actOnSelection(action: int): void {
        if (!root.hasSelection || selectedSize.width <= 0 || selectedSize.height <= 0 || actionProcess.running) return;
        // ScreenshotAction cleans up its input; always work on a disposable copy.
        const temporary = Paths.runtimeTemp("gallery-action-" + Date.now() + ".png");
        const script = ScreenshotAction.getScript(0, 0, selectedSize.width, selectedSize.height, temporary, action);
        actionProcess.command = ["bash", "-c", "set -euo pipefail; trap 'rm -f -- \"$2\"' EXIT; cp -- \"$1\" \"$2\"; " + script, "gallery-action", selectedPath, temporary];
        actionProcess.running = true;
    }
    Process {
        id: actionProcess
        onExited: (code, status) => {
            root.feedback = code === 0 ? qsTr("Done") : qsTr("Action failed");
            feedbackTimer.restart();
        }
    }
    property string confirmDelete: ""
    property string pendingCopy: ""
    property string feedback: ""
    readonly property string shotsdir: GlobalConfig.paths.screenshotsDir
    spacing: Tokens.spacing.small

    function openImage(path: string): void {
        root.visibilities.utilities = false;
        if (!Visibilities.sidebarPinned)
            root.visibilities.sidebar = false;
        Quickshell.execDetached(["xdg-open", path]);
    }

    function copyImage(path: string): void {
        root.pendingCopy = path;
        copyNextImage();
    }

    function copyNextImage(): void {
        if (!root.pendingCopy || copyProcess.running) return;
        copyProcess.command = ["bash", "-c", 'wl-copy --type image/png < "$1"', "screenshot-gallery", root.pendingCopy];
        root.pendingCopy = "";
        copyProcess.running = true;
    }

    Process {
        id: copyProcess
        onExited: (exitCode, exitStatus) => {
            root.feedback = exitCode === 0 ? qsTr("Image copied") : qsTr("Could not copy image");
            feedbackTimer.restart();
            root.copyNextImage();
        }
    }

    Timer {
        id: feedbackTimer
        interval: 2200
        onTriggered: root.feedback = ""
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: Tokens.spacing.small

        MaterialIcon {
            text: root.feedback ? "check_circle" : "photo_library"
            color: root.feedback ? MenuStyle.accent : MenuStyle.ink
        }

        MenuText {
            Layout.maximumWidth: 230 * root.scaleOffset
            text: root.feedback || qsTr("Recent captures")
            font.pointSize: root.bodyPointSize*0.94
            color: root.feedback ? MenuStyle.accent : MenuStyle.ink
            elide: Text.ElideRight
        }

        Rectangle {
            implicitWidth: countLabel.implicitWidth + 14
            implicitHeight: countLabel.implicitHeight + 4
            radius: 7
            color: MenuStyle.cardFill
            border.width: 1
            border.color: MenuStyle.rule
            MenuText { id: countLabel; anchors.centerIn: parent; text: gallery.count; color: MenuStyle.muted; font.pointSize: root.bodyPointSize * 0.81 }
        }
        Item { Layout.fillWidth: true }
        IconButton {
            icon: "folder_open"
            type: IconButton.Text
            ToolTip.visible: hovered
            ToolTip.text: qsTr("Open screenshots folder")
            onClicked: Quickshell.execDetached(["xdg-open", root.shotsdir])
        }

        TextButton {
            text: root.newestFirst ? qsTr("Newest first") : qsTr("Oldest first")
            font.family: MenuStyle.fontFamily
            font.pointSize: root.bodyPointSize * 0.81
            defaultRadius: 10 * root.scaleOffset
            checkedRadius: 10 * root.scaleOffset
            border.width: 1
            border.color: MenuStyle.rule
            inactiveColour: MenuStyle.cardFill
            inactiveOnColour: MenuStyle.ink
            onClicked: root.newestFirst = !root.newestFirst
        }
        IconButton {
            icon: root.props.screenshotListExpanded ? "unfold_less" : "unfold_more"
            type: IconButton.Text
            label.animate: true
            onClicked: root.props.screenshotListExpanded = !root.props.screenshotListExpanded
        }
    }

    GridView {
        id: gallery

        readonly property int columns: width >= 540 ? 3 : 2
        readonly property real tileHeight: cellWidth * 0.69 + 34
        model: FolderListModel {
            folder: "file://" + root.shotsdir
            nameFilters: ["*.png"]
            showDirs: false
            sortField: FolderListModel.Time
            sortReversed: !root.newestFirst
        }

        Layout.fillWidth: true
        implicitHeight: Math.max(64, Math.min(Math.ceil(count / columns), root.props.screenshotListExpanded ? 4 : 2) * cellHeight)
        cellWidth: width / columns
        cellHeight: tileHeight + Tokens.spacing.small
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        cacheBuffer: cellHeight

        ScrollBar.vertical: StyledScrollBar { flickable: gallery }

        delegate: Item {
            id: shot
            required property string fileName
            required property string filePath
            required property url fileUrl
            readonly property bool selected: root.selectedPath === filePath
            readonly property bool confirming: root.confirmDelete === filePath
            width: gallery.cellWidth
            height: gallery.cellHeight

            StyledRect {
                anchors.fill: parent
                anchors.rightMargin: Tokens.spacing.small
                anchors.bottomMargin: Tokens.spacing.small
                radius: 11 * root.scaleOffset
                color: pointer.containsMouse ? Qt.alpha(MenuStyle.accent,0.12) : MenuStyle.cardFill
                border.width: shot.selected ? 2 : 1
                border.color: shot.selected ? MenuStyle.accent : MenuStyle.border
                clip: true

                Image {
                    id: preview
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 7 * root.scaleOffset
                    height: parent.height - 32 - Tokens.padding.extraSmall
                    source: shot.fileUrl
                    sourceSize.width: 420
                    sourceSize.height: 260
                    asynchronous: true
                    fillMode: Image.PreserveAspectFit
                }

                MaterialIcon {
                    anchors.centerIn: preview
                    visible: preview.status !== Image.Ready
                    text: preview.status === Image.Error ? "broken_image" : "image"
                    color: MenuStyle.muted
                }

                MouseArea {
                    id: pointer
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    enabled: !shot.confirming
                    onClicked: {
                        root.selectedPath = shot.filePath;
                        root.selectedUrl = shot.fileUrl;
                        root.copyImage(shot.filePath);
                    }
                    onDoubleClicked: root.openImage(shot.filePath)
                    ToolTip.visible: containsMouse
                    ToolTip.delay: 900
                    ToolTip.text: qsTr("Click to copy · Double-click to open") + "\n" + shot.fileName
                }

                Rectangle {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 9
                    width: 24; height: 24; radius: 12
                    visible: shot.selected
                    color: MenuStyle.accent
                    PrimaryControlFill {} // Capture primary material
                    MaterialIcon { anchors.centerIn: parent; text: "check"; color: "white"; fontStyle: Tokens.font.icon.builders.medium.size(13).build() }
                }
                RowLayout {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.leftMargin: Tokens.padding.small
                    height: 32
                    spacing: 0

                    MenuText {
                        Layout.fillWidth: true
                        text: {
                            const match = shot.fileName.match(/^screenshot-(\d{4})-(\d{2})-(\d{2})_(\d{2})\.(\d{2})\.(\d{2})/);
                            return match ? `${match[3]}.${match[2]}. ${match[4]}:${match[5]}` : shot.fileName;
                        }
                        font.pointSize: root.bodyPointSize*0.79
                        color: MenuStyle.muted
                        elide: Text.ElideRight
                    }

                    IconButton {
                        icon: "delete_outline"
                        type: IconButton.Text
                        font: Tokens.font.icon.small
                        onClicked: {
                            root.confirmDelete = shot.filePath;
                        }
                    }
                }

                StyledRect {
                    anchors.fill: parent
                    visible: shot.confirming
                    color: Colours.palette.m3surfaceContainerHigh
                    radius: parent.radius
                    MouseArea { anchors.fill: parent }
                    ColumnLayout {
                        anchors.centerIn: parent
                        width: parent.width - Tokens.padding.small * 2
                        spacing: Tokens.spacing.small
                        MenuText {
                            Layout.fillWidth: true
                            text: qsTr("Delete this screenshot?")
                            font.pointSize: root.bodyPointSize*0.79
                            wrapMode: Text.Wrap
                            horizontalAlignment: Text.AlignHCenter
                        }
                        RowLayout {
                            Layout.alignment: Qt.AlignHCenter
                            IconButton {
                                icon: "close"
                                type: IconButton.Text
                                onClicked: root.confirmDelete = ""
                            }
                            IconButton {
                                icon: "delete_forever"
                                type: IconButton.Text
                                label.color: Colours.palette.m3error
                                onClicked: {
                                    CUtils.deleteFile(shot.fileUrl);
                                    if (root.selectedPath === shot.filePath) root.selectedPath = "";
                                    root.confirmDelete = "";
                                }
                            }
                        }
                    }
                }
            }
        }

        MenuText {
                        font.pointSize:root.bodyPointSize*0.81
            anchors.centerIn: parent
            visible: gallery.count === 0
            text: qsTr("No screenshots found")
            color: MenuStyle.muted
        }

        Behavior on implicitHeight { Anim {} }
    }
    Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: MenuStyle.rule }
    RowLayout {
        Layout.fillWidth: true
        spacing: 8 * root.scaleOffset
        MenuText {
            Layout.fillWidth: true
            text: root.hasSelection ? qsTr("1 selected") : qsTr("Select a capture")
            font.pointSize: root.bodyPointSize * 0.81
            color: MenuStyle.muted
        }
        TextButton {
            text: qsTr("Extract text")
            enabled: root.hasSelection && root.selectedSize.width > 0 && !actionProcess.running
            font.family: MenuStyle.fontFamily
            font.pointSize: root.bodyPointSize * 0.81
            defaultRadius: 10 * root.scaleOffset
            checkedRadius: 10 * root.scaleOffset
            border.width: 1
            border.color: MenuStyle.rule
            inactiveColour: MenuStyle.cardFill
            inactiveOnColour: MenuStyle.ink
            onClicked: root.actOnSelection(ScreenshotAction.SnipAction.CharRecognition)
        }
        TextButton {
            text: qsTr("Image search")
            enabled: root.hasSelection && root.selectedSize.width > 0 && !actionProcess.running
            font.family: MenuStyle.fontFamily
            font.pointSize: root.bodyPointSize * 0.81
            defaultRadius: 10 * root.scaleOffset
            checkedRadius: 10 * root.scaleOffset
            border.width: 1
            border.color: MenuStyle.rule
            inactiveColour: MenuStyle.cardFill
            inactiveOnColour: MenuStyle.ink
            onClicked: root.actOnSelection(ScreenshotAction.SnipAction.Search)
        }
        IconButton {
            icon: "delete_outline"
            type: IconButton.Text
            enabled: root.hasSelection
            label.color: Colours.palette.m3error
            onClicked: root.confirmDelete = root.selectedPath
        }
    }

}
