pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls as QQC
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Caelestia.Config
import qs.components
import qs.services
import qs.modules.nexus.common
import "../flausen"
PageBase {
    id: root
    title: qsTranslate("Flausen", "Appearance")
    readonly property var accents: [
        {name:"blue", label:qsTranslate("Flausen", "Blue"), color:"#347fff"}, {name:"coral", label:qsTranslate("Flausen", "Coral"), color:"#f16f5c"},
        {name:"amber", label:qsTranslate("Flausen", "Gold"), color:"#efb34f"}, {name:"green", label:qsTranslate("Flausen", "Green"), color:"#53c67b"},
        {name:"violet", label:qsTranslate("Flausen", "Violet"), color:"#a464ec"}, {name:"graphite", label:qsTranslate("Flausen", "Graphite"), color:"#81868d"}
    ]
    property string themeError: ""
    function changeTheme(name: string, mode: string, automatic: bool): void {
        if (themeChange.running) return;
        themeError = "";
        GlobalConfig.services.autoSchemeEnabled = false;
        themeChange.automatic = automatic;
        themeChange.command = ["caelestia", "scheme", "set", "--notify", "-n", name, "-f", "default", "-m", mode, "--no-smart"];
        themeChange.running = true;
    }
    function applyAccent(name: string): void {
        changeTheme("flausen-" + name, Colours.light ? "light" : "dark", GlobalConfig.services.autoSchemeEnabled);
    }
    function applyMode(mode: string): void {
        changeTheme(Colours.scheme.startsWith("flausen-") ? Colours.scheme : "flausen-blue", mode === "auto" ? (Colours.light ? "light" : "dark") : mode, mode === "auto");
    }
    readonly property Process themeProcess: Process {
        id: themeChange
        property bool automatic
        onExited: code => {
            if (code === 0) {
                GlobalConfig.services.autoSchemeEnabled = automatic;
                if (automatic) AutoScheme.apply(true);
            } else root.themeError = qsTranslate("Flausen", "Could not apply the color scheme. Please try again.");
        }
    }
    ColumnLayout {
        anchors { left: parent.left; right: parent.right; top: parent.top }
        spacing: 14
        Text { text: qsTranslate("Flausen", "Make this space your own."); color: FlausenStyle.secondary; font {family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 15} Layout.topMargin: -8 }
        Text { text: qsTranslate("Flausen", "Color mode"); color: FlausenStyle.text; font {family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 17} Layout.topMargin: 8 }
        RowLayout {
            Layout.fillWidth: true
            spacing: 18
            ThemePreview { enabled: !themeChange.running; label: qsTranslate("Flausen", "Light"); selected: !GlobalConfig.services.autoSchemeEnabled && Colours.light; onClicked: root.applyMode("light") }
            ThemePreview { enabled: !themeChange.running; label: qsTranslate("Flausen", "Dark"); dark: true; selected: !GlobalConfig.services.autoSchemeEnabled && !Colours.light; onClicked: root.applyMode("dark") }
            ThemePreview { enabled: !themeChange.running; label: qsTranslate("Flausen", "Automatic"); automatic: true; selected: GlobalConfig.services.autoSchemeEnabled; onClicked: root.applyMode("auto") }
        }
        QQC.Label {
            visible: root.themeError !== ""
            text: root.themeError
            color: FlausenStyle.secondary
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        QQC.Label {
            visible: GlobalConfig.services.autoSchemeEnabled
            text: GlobalConfig.services.autoSchemeMode === "solar" ? qsTranslate("Flausen", "Switches at sunrise and sunset. Set times under Schedule & colors.") : qsTranslate("Flausen", "Light from ") + GlobalConfig.services.autoSchemeLightTime + " · Dark from " + GlobalConfig.services.autoSchemeDarkTime
            color: FlausenStyle.secondary
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        Text { text: qsTranslate("Flausen", "Wallpaper"); color: FlausenStyle.text; font {family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 17} Layout.topMargin: 5 }
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 82
            radius: 14; color: "transparent"; border {width: 1; color: FlausenStyle.line}
            RowLayout {
                anchors {fill: parent; margins: 10}
                spacing: 16
                Image { source: "file://" + Wallpapers.thumbFor(Wallpapers.actualCurrent || Wallpapers.fallback); fillMode: Image.PreserveAspectCrop; asynchronous: true; Layout.preferredWidth: 150; Layout.fillHeight: true; clip: true }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text { text: (Wallpapers.actualCurrent || Wallpapers.fallback).split("/").pop().replace(/\.[^.]+$/, ""); color: FlausenStyle.text; font {family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 15} elide: Text.ElideMiddle; Layout.fillWidth: true }
                    Text { text: qsTranslate("Flausen", "Your current wallpaper"); color: FlausenStyle.secondary; font {family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 12} }
                }
                FlausenButton { text: qsTranslate("Flausen", "Change …"); onClicked: root.nState.openSubPage(1) }
            }
        }
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: settings.implicitHeight + 12
            radius: 14; color: "transparent"; border {width: 1; color: FlausenStyle.line}
            ColumnLayout {
                id: settings
                anchors {left: parent.left; right: parent.right; top: parent.top; margins: 6}
                spacing: 0
                RowLayout {
                    Layout.fillWidth: true; Layout.margins: 12
                    Text { text: qsTranslate("Flausen", "Accent color"); color: FlausenStyle.text; font {family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 15} Layout.fillWidth: true }
                    Repeater {
                        model: root.accents
                        QQC.Button {
                            id: swatch
                            required property var modelData
                            text: modelData.label
                            contentItem: Item {}
                            readonly property bool chosen: Colours.scheme === "flausen-" + modelData.name
                            implicitWidth: 32; implicitHeight: 32
                            enabled: !themeChange.running
                            Accessible.name: modelData.label
                            Accessible.checkable: true
                            Accessible.checked: chosen
                            QQC.ToolTip.visible: hovered
                            QQC.ToolTip.text: modelData.label
                            onClicked: root.applyAccent(modelData.name)
                            background: Rectangle {
                                color: "transparent"; radius: 16; border { width: swatch.chosen || swatch.visualFocus ? 2 : 0; color: FlausenStyle.accent }
                                Rectangle {anchors.centerIn: parent; width: 23; height: 23; radius: 12; color: swatch.modelData.color}
                            }
                        }
                    }
                }
                Rectangle { Layout.fillWidth: true; Layout.leftMargin: 14; Layout.rightMargin: 14; implicitHeight: 1; color: FlausenStyle.line }
                FlausenSwitch {
                    Layout.fillWidth: true
                    text: qsTranslate("Flausen", "Transparency")
                    checked: GlobalConfig.appearance.transparency.enabled
                    onToggled: GlobalConfig.appearance.transparency.enabled = checked
                    palette.windowText: FlausenStyle.text
                    palette.highlight: FlausenStyle.accent
                    font {family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 15}
                    leftPadding: 16; rightPadding: 16; topPadding: 14; bottomPadding: 14
                }
                Rectangle { Layout.fillWidth: true; Layout.leftMargin: 14; Layout.rightMargin: 14; implicitHeight: 1; color: FlausenStyle.line }
                FlausenSwitch {
                    Layout.fillWidth: true
                    text: qsTranslate("Flausen", "Reduce motion")
                    checked: !GlobalConfig.appearance.anim.enabled
                    onToggled: GlobalConfig.appearance.anim.enabled = !checked
                    palette.windowText: FlausenStyle.text
                    palette.highlight: FlausenStyle.accent
                    font {family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 15}
                    leftPadding: 16; rightPadding: 16; topPadding: 14; bottomPadding: 14
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true; implicitHeight: 58; radius: 14; color: "transparent"; border {width:1; color:FlausenStyle.line}
            RowLayout {
                anchors {fill: parent; margins: 16}
                Text { text: qsTranslate("Flausen", "Text size"); color: FlausenStyle.text; font {family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 15} Layout.preferredWidth: 130 }
                FlausenSlider {
                    id: sizeSlider
                    objectName: "flausenTextScale"
                    Layout.fillWidth: true; from: 0.8; to: 1.4; stepSize: 0.05; value: GlobalConfig.appearance.font.scale; onMoved: GlobalConfig.appearance.font.scale = value; Accessible.name: qsTranslate("Flausen", "Desktop text size"); palette.highlight: FlausenStyle.accent }
                Text { text: Math.round(GlobalConfig.appearance.font.scale * 100) + " %"; color: FlausenStyle.secondary; font {family:FlausenStyle.family; pixelSize:FlausenStyle.fontScale * 13} Layout.preferredWidth: 48 }
            }
        }
        Flow {
            Layout.fillWidth: true
            spacing: 8
            FlausenButton { text: qsTranslate("Flausen", "Schedule & colors"); onClicked: root.nState.openSubPage(10) }
            FlausenButton { text: qsTranslate("Flausen", "Effects & fonts"); onClicked: root.nState.openSubPage(8) }
            FlausenButton { text: qsTranslate("Flausen", "Slideshow & collections"); onClicked: root.nState.openSubPage(6) }
        }
    }
}
