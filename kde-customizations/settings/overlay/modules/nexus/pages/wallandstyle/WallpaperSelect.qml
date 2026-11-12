pragma ComponentBehavior: Bound

import QtQuick
import qs.modules.nexus.flausen
import QtQuick.Layouts
import Quickshell
import Caelestia
import Caelestia.Components
import Caelestia.Config
import Caelestia.Images
import Caelestia.Models
import qs.components
import qs.components.controls
import qs.components.filedialog
import qs.services
import qs.utils
import qs.modules.nexus.common

PageBase {
    id: root

    readonly property var wallpaperSets: [
        { name: "ralleur set", icon: "grid_view", path: Paths.home + "/Bilder/Wallpapers/ralleur-4k/png", preview: "01-nocturne.png" },
        { name: "flausen dark", icon: "dark_mode", path: Paths.home + "/Bilder/Wallpapers/flausen-4k/dark/png", preview: "01-still-air-dark.png" },
        { name: "flausen light", icon: "light_mode", path: Paths.home + "/Bilder/Wallpapers/flausen-4k/light/png", preview: "01-still-air-light.png" }
    ]
    readonly property var activeWallpaperSet: wallpaperSets.find(set => set.path === Paths.wallsdir.replace(/\/+$/, "")) ?? null
    readonly property string setPreview: activeWallpaperSet ? activeWallpaperSet.path + "/" + activeWallpaperSet.preview : Wallpapers.fallback

    function selectImage(path: string): void {
        GlobalConfig.background.slideshowEnabled = false;
        GlobalConfig.save();
        Wallpapers.setWallpaper(path);
    }

    function toggleRandom(): void {
        const enabled = !Config.background.slideshowEnabled;
        GlobalConfig.background.slideshowRandom = true;
        GlobalConfig.background.slideshowEnabled = enabled;
        GlobalConfig.save();
        if (enabled)
            Wallpapers.setRandom();
    }

    function selectWallpaperSet(index: int): void {
        const set = wallpaperSets[index];
        if (!set)
            return;
        root.sortColor = "transparent";
        root.wallpaperColors = ({});
        root.colorDistances = ({});
        GlobalConfig.paths.wallpaperDir = set.path;
        GlobalConfig.save();
        gridList.positionViewAtBeginning();
    }

    property Timer sortDebouncer: Timer {
        interval: 250
        onTriggered: root.analyzeColors()
    }

    property color sortColor: "transparent"

    property var colorDistances: ({})

    property int sortVersion: 0

    property var wallpaperColors: ({})

    readonly property var sortColors: ["#e53935"
        , "#1e88e5"
        , "#43a047"
        , "#fdd835"
        , "#8e24aa"
        , "#fb8c00"
    ]

    property var wallsList: {
        const walls = Wallpapers.list;
        const baseDir = Paths.wallsdir;
        const categories = {};
        const list = [];
        const filter = root.nState ? root.nState.wallpaperFilterType : "all";

        for (const w of walls) {
            const isVid = Images.isVideo(w.name);
            const isGif = w.name.toLowerCase().endsWith(".gif");
            const isImg = Images.isValidImageByName(w.name) && !isGif;

            let matches = false;
            if (filter === "all") matches = true;
            else if (filter === "video" && isVid) matches = true;
            else if (filter === "gif" && isGif) matches = true;
            else if (filter === "image" && isImg) matches = true;

            if (!matches) continue;

            if (w.parentDir !== baseDir) {
                const category = Wallpapers.getCategoryFor(w);
                if (category && (!(category in categories) || categories[category].name.localeCompare(w.name) > 0))
                    categories[category] = w;
            } else {
                list.push(w);
            }
        }

        for (const cat in categories) {
            list.push(categories[cat]);
        }

        if (root.sortColor.a > 0) {
            list.sort((a, b) => {
                const distA = root.colorDistances[a.path] ?? 999999;
                const distB = root.colorDistances[b.path] ?? 999999;
                return distA - distB;
            });
        } else {
            list.sort((a, b) => a.name.localeCompare(b.name));
        }

        while (list.length % Config.nexus.wallpapersPerRow !== 0)
            list.push(null);
        return list;
    }

    function colorDistance(c1: color, c2: color): real {
        const rMean = (c1.r + c2.r) / 2;
        const dr = c1.r - c2.r;
        const dg = c1.g - c2.g;
        const db = c1.b - c2.b;
        return Math.sqrt((2 + rMean) * dr * dr + 4 * dg * dg + (3 - rMean) * db * db);
    }

    function toggleSortColor(color: color) {
        if (root.sortColor === color) {
            root.sortColor = "transparent";
        } else {
            root.sortColor = color;
            root.analyzeColors();
        }
    }

    function analyzeColors() {
        const walls = Wallpapers.list;
        const baseDir = Paths.wallsdir;
        const newDistances = {};

        for (const w of walls) {
            if (w.parentDir !== baseDir)
                continue;

            const dominant = root.wallpaperColors[w.path];
            if (dominant === undefined)
                continue;

            newDistances[w.path] = colorDistance(dominant, root.sortColor);
        }

        root.colorDistances = newDistances;
        root.sortVersion++;
    }

    title: qsTr("Select wallpaper")
    isSubPage: true
    scrollable: false

    onSortColorChanged: {
        if (sortColor.a === 0) {
            wallpaperColors = ({});
            colorDistances = ({});
        }
    }

    ListView {
        id: gridList
        objectName: "wallpaper-grid"

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: root.cappedWidth
        clip: true
        spacing: Tokens.spacing.medium

        model: root.wallsList.length > 0 ? Math.ceil(root.wallsList.length / Config.nexus.wallpapersPerRow) : 0

        header: ColumnLayout {
            width: gridList.width
            spacing: Tokens.spacing.small


            ButtonRow {
                Layout.bottomMargin: Tokens.spacing.medium
                Layout.alignment: Qt.AlignHCenter
                spacing: Tokens.spacing.small

                IconTextButton {
                    icon: "photo_library"
                    text: qsTr("Browse")
                    font: FlausenStyle.typeface(16)
                    isRound: true
                    shapeMorph: true
                    horizontalPadding: Tokens.padding.extraLarge
                    verticalPadding: Tokens.padding.medium
                    onClicked: browseDialog.open()

                    FileDialog {
                        id: browseDialog

                        title: qsTr("Select an image")
                        filterLabel: qsTr("Image files")
                        filters: Images.validImageExtensions
                        onAccepted: path => {
                            root.selectImage(path);
                        }
                    }
                }

                IconTextButton {
                    disabled: Wallpapers.list.length === 0
                    icon: "shuffle"
                    objectName: "wallpaper-random"
                    text: Config.background.slideshowEnabled ? qsTranslate("Flausen", "Random: on") : qsTranslate("Flausen", "Random: off")
                    Accessible.role: Accessible.CheckBox
                    Accessible.name: qsTranslate("Flausen", "Automatically change wallpaper")
                    Accessible.checked: Config.background.slideshowEnabled
                    activeFocusOnTab: true
                    border.width: activeFocus ? 2 : 0
                    border.color: FlausenStyle.text
                    Keys.onReturnPressed: clicked()
                    Keys.onEnterPressed: clicked()
                    Keys.onSpacePressed: clicked()
                    font: FlausenStyle.typeface(16)
                    isRound: true
                    shapeMorph: true
                    horizontalPadding: Tokens.padding.extraLarge
                    verticalPadding: Tokens.padding.medium
                    type: Config.background.slideshowEnabled ? IconTextButton.Filled : IconTextButton.Tonal
                    onClicked: root.toggleRandom()
                }

                IconTextButton {
                    icon: "folder_open"
                    text: qsTr("Open folder")
                    font: FlausenStyle.typeface(16)
                    isRound: true
                    shapeMorph: true
                    horizontalPadding: Tokens.padding.extraLarge
                    verticalPadding: Tokens.padding.medium
                    type: IconTextButton.Tonal
                    onClicked: Quickshell.execDetached(["xdg-open", Paths.wallsdir])
                }
            }

            WallItem {
                Layout.topMargin: Tokens.spacing.medium
                imgHeight: Math.round(width * 0.3)
                radius: Tokens.rounding.extraLarge
                source: root.setPreview
                text: root.activeWallpaperSet ? root.activeWallpaperSet.name : qsTr("Featured wallpaper")
                fillLabel: false
                onClicked: {
                    root.selectImage(root.setPreview);
                    root.nState.closeSubPage();
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.bottomMargin: Tokens.spacing.medium
                spacing: Tokens.spacing.small

                StyledText {
                    text: qsTranslate("Flausen", "Wallpaper sets")
                    font: FlausenStyle.typeface(18)
                }

                Flow {
                    Layout.fillWidth: true
                    spacing: Tokens.spacing.small

                    Repeater {
                        id: setButtons
                        model: root.wallpaperSets

                        IconTextButton {
                            required property var modelData
                            required property int index

                            objectName: "wallpaper-set-" + index
                            icon: modelData.icon
                            text: modelData.name
                            type: root.activeWallpaperSet?.path === modelData.path ? IconTextButton.Filled : IconTextButton.Tonal
                            isRound: true
                            horizontalPadding: Tokens.padding.large
                            verticalPadding: Tokens.padding.medium
                            activeFocusOnTab: true
                            border.width: activeFocus ? 2 : 0
                            border.color: FlausenStyle.text
                            Accessible.role: Accessible.RadioButton
                            Accessible.name: modelData.name
                            Accessible.checked: !!root.activeWallpaperSet && root.activeWallpaperSet.path === modelData.path
                            Keys.onReturnPressed: clicked()
                            Keys.onEnterPressed: clicked()
                            Keys.onSpacePressed: clicked()
                            onClicked: root.selectWallpaperSet(index)
                        }
                    }
                }

                StyledText {
                    Layout.fillWidth: true
                    text: qsTranslate("Flausen", "Automatic changes use the selected set. Selecting an image stops automatic changes.")
                    font: FlausenStyle.typeface(14)
                    color: FlausenStyle.secondary
                    wrapMode: Text.WordWrap
                }
            }

            StepperRow {
                objectName: "wallpaper-interval"
                Layout.fillWidth: true
                label: qsTranslate("Flausen", "Change interval (minutes)")
                subtext: qsTranslate("Flausen", "Random switches wallpapers automatically at this interval.")
                from: 1
                to: 1440
                stepSize: 1
                value: Math.max(1, Math.round(Config.background.slideshowInterval * 60))
                enabled: Config.background.slideshowEnabled && Config.background.wallpaperEnabled
                onMoved: value => {
                    GlobalConfig.background.slideshowInterval = value / 60;
                    GlobalConfig.save();
                }
            }

            RowLayout {
                Layout.topMargin: Tokens.spacing.medium
                Layout.fillWidth: true
                z: typeFilterBtn.expanded ? 1 : 0

                Item {
                    Layout.fillWidth: true
                }

                Row {
                    spacing: Tokens.spacing.medium

                    Rectangle {
                        width: 36
                        height: 36
                        radius: Tokens.rounding.full
                        color: "#e53935"

                        Rectangle {
                            anchors.centerIn: parent
                            width: 36
                            height: 36
                            radius: parent.radius
                            color: "transparent"
                            border.width: root.sortColor === "#e53935" ? 3 : 0
                            border.color: FlausenStyle.text
                        }

                        StateLayer {
                            anchors.fill: parent
                            radius: parent.radius
                            onClicked: root.toggleSortColor("#e53935")
                        }
                    }

                    Rectangle {
                        width: 36
                        height: 36
                        radius: Tokens.rounding.full
                        color: "#1e88e5"

                        Rectangle {
                            anchors.centerIn: parent
                            width: 36
                            height: 36
                            radius: parent.radius
                            color: "transparent"
                            border.width: root.sortColor === "#1e88e5" ? 3 : 0
                            border.color: FlausenStyle.text
                        }

                        StateLayer {
                            anchors.fill: parent
                            radius: parent.radius
                            onClicked: root.toggleSortColor("#1e88e5")
                        }
                    }

                    Rectangle {
                        width: 36
                        height: 36
                        radius: Tokens.rounding.full
                        color: "#43a047"

                        Rectangle {
                            anchors.centerIn: parent
                            width: 36
                            height: 36
                            radius: parent.radius
                            color: "transparent"
                            border.width: root.sortColor === "#43a047" ? 3 : 0
                            border.color: FlausenStyle.text
                        }

                        StateLayer {
                            anchors.fill: parent
                            radius: parent.radius
                            onClicked: root.toggleSortColor("#43a047")
                        }
                    }

                    Rectangle {
                        width: 36
                        height: 36
                        radius: Tokens.rounding.full
                        color: "#fdd835"

                        Rectangle {
                            anchors.centerIn: parent
                            width: 36
                            height: 36
                            radius: parent.radius
                            color: "transparent"
                            border.width: root.sortColor === "#fdd835" ? 3 : 0
                            border.color: FlausenStyle.text
                        }

                        StateLayer {
                            anchors.fill: parent
                            radius: parent.radius
                            onClicked: root.toggleSortColor("#fdd835")
                        }
                    }

                    Rectangle {
                        width: 36
                        height: 36
                        radius: Tokens.rounding.full
                        color: "#8e24aa"

                        Rectangle {
                            anchors.centerIn: parent
                            width: 36
                            height: 36
                            radius: parent.radius
                            color: "transparent"
                            border.width: root.sortColor === "#8e24aa" ? 3 : 0
                            border.color: FlausenStyle.text
                        }

                        StateLayer {
                            anchors.fill: parent
                            radius: parent.radius
                            onClicked: root.toggleSortColor("#8e24aa")
                        }
                    }

                    Rectangle {
                        width: 36
                        height: 36
                        radius: Tokens.rounding.full
                        color: "#fb8c00"

                        Rectangle {
                            anchors.centerIn: parent
                            width: 36
                            height: 36
                            radius: parent.radius
                            color: "transparent"
                            border.width: root.sortColor === "#fb8c00" ? 3 : 0
                            border.color: FlausenStyle.text
                        }

                        StateLayer {
                            anchors.fill: parent
                            radius: parent.radius
                            onClicked: root.toggleSortColor("#fb8c00")
                        }
                    }
                }

                Item {
                    Layout.fillWidth: true
                }

                SplitButton {
                    id: typeFilterBtn

                    type: SplitButton.Tonal
                    fallbackIcon: "collections"
                    fallbackText: qsTr("All")
                    minLeftWidth: 100

                    menuItems: [
                        MenuItem {
                            property string filterValue: "all"

                            text: qsTr("All")
                            icon: "collections"
                            onClicked: {
                                if (root.nState) root.nState.wallpaperFilterType = "all"
                            }
                        },
                        MenuItem {
                            property string filterValue: "image"

                            text: qsTr("Images")
                            icon: "image"
                            onClicked: {
                                if (root.nState) root.nState.wallpaperFilterType = "image"
                            }
                        },
                        MenuItem {
                            property string filterValue: "gif"

                            text: qsTr("GIFs")
                            icon: "gif"
                            onClicked: {
                                if (root.nState) root.nState.wallpaperFilterType = "gif"
                            }
                        },
                        MenuItem {
                            property string filterValue: "video"

                            text: qsTr("Videos")
                            icon: "movie"
                            onClicked: {
                                if (root.nState) root.nState.wallpaperFilterType = "video"
                            }
                        }
                    ]

                    active: {
                        const f = root.nState ? root.nState.wallpaperFilterType : "all";
                        return menuItems.find(m => m.filterValue === f) ?? menuItems[0];
                    }
                }
            }

            StyledText {
                Layout.topMargin: Tokens.spacing.large
                text: root.activeWallpaperSet ? root.activeWallpaperSet.name + " · " + Wallpapers.list.length + qsTranslate("Flausen", " wallpapers") : qsTr("Local wallpapers")
                font: FlausenStyle.typeface(18)
            }
        }

        delegate: RowLayout {
            id: rowDel

            required property int index

            width: gridList.width
            spacing: Tokens.spacing.large

            Repeater {
                model: Config.nexus.wallpapersPerRow

                WallItem {
                    id: wallItem

                    required property int index
                    readonly property int globalIndex: rowDel.index * Config.nexus.wallpapersPerRow + index
                    readonly property var modelData: root.wallsList[globalIndex]

                    opacity: modelData ? 1 : 0
                    enabled: !!modelData
                    Layout.fillWidth: true

                    isFolder: !!modelData && modelData.parentDir !== Paths.wallsdir
                    folderCount: {
                        if (!modelData || modelData.parentDir === Paths.wallsdir)
                            return 0;
                        const group = Wallpapers.grouped[Wallpapers.getCategoryFor(modelData)];
                        return group ? group.length : 0;
                    }

                    source: String(modelData?.path ?? "")
                    text: {
                        if (!modelData)
                            return "";

                        if (modelData.parentDir !== Paths.wallsdir) {
                            const category = Wallpapers.getCategoryFor(modelData);
                            return category.slice(0, 1).toUpperCase() + category.slice(1);
                        }
                        return modelData.name;
                    }
                    onClicked: {
                        if (modelData.parentDir !== Paths.wallsdir) {
                            root.nState.selectedWallpaperCategory = Wallpapers.getCategoryFor(modelData);
                            root.nState.openSubPage(2);
                        } else {
                            root.selectImage(modelData.path);
                        }
                    }

                    ImageAnalyser {
                        id: colorAnalyzer

                        source: (root.sortColor.a > 0 && wallItem.modelData && wallItem.modelData.parentDir === Paths.wallsdir) ? wallItem.modelData.path : ""
                        rescaleSize: 64
                        onDominantColourChanged: {
                            if (wallItem.modelData && dominantColour.a > 0) {
                                root.wallpaperColors[wallItem.modelData.path] = dominantColour;
                                if (root.sortColor.a > 0) {
                                    root.sortDebouncer.restart();
                                }
                            }
                        }
                    }
                }
            }
        }

        Loader {
            Layout.fillWidth: true

            asynchronous: true
            active: root.wallsList.length === 0
            visible: active

            sourceComponent: StyledRect {
                color: FlausenStyle.card
                radius: Tokens.rounding.extraLarge
                implicitHeight: noWallsLayout.implicitHeight + Tokens.padding.extraExtraLarge * 2

                ColumnLayout {
                    id: noWallsLayout

                    anchors.centerIn: parent
                    spacing: Tokens.spacing.extraSmall

                    MaterialIcon {
                        Layout.alignment: Qt.AlignHCenter
                        text: "hide_image"
                        color: FlausenStyle.secondary
                        fontStyle: Tokens.font.icon.extraLarge
                    }

                    StyledText {
                        Layout.alignment: Qt.AlignHCenter
                        text: qsTr("No local wallpapers found")
                        color: FlausenStyle.secondary
                        font: FlausenStyle.typeface(18)
                    }
                }
            }
        }
    }
}
