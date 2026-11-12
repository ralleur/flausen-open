pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "generated/Brand.js" as Brand

ApplicationWindow {
    id: root
    visible: true
    width: 540; height: 590
    minimumWidth: 360; minimumHeight: 480
    title: qsTranslate("Flausen", "About %1").arg(Brand.tokens.brand.name)
    SystemPalette { id: systemPalette }
    readonly property bool dark: Qt.application.arguments.indexOf("--light") < 0 && (Qt.application.arguments.indexOf("--dark") >= 0 || systemPalette.window.hslLightness < 0.5)
    readonly property var theme: dark ? Brand.tokens.color.dark : Brand.tokens.color.light
    color: theme.background
    palette.windowText: theme.text
    palette.buttonText: theme.primaryButtonText
    palette.button: theme.primaryButtonBackground
    palette.highlight: theme.focus
    font.family: "Inter"
    component BrandButton: Button {
        id: control
        padding: 11
        contentItem: Text {
            text: control.text
            font: control.font
            color: root.theme.primaryButtonText
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
        background: Rectangle {
            color: root.theme.primaryButtonBackground
            opacity: control.down ? 0.75 : control.hovered ? 0.9 : 1
            radius: Brand.tokens.shape.smallRadius
            border.width: control.visualFocus ? 2 : 0
            border.color: root.theme.focus
        }
    }
    ScrollView {
        anchors.fill: parent
        anchors.margins: 28
        contentWidth: availableWidth
        ColumnLayout {
            width: parent.width
            spacing: 20
            Image {
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 260; Layout.preferredHeight: 155
                source: "handoff/assets/logos/flausen-lockup-on-" + (root.dark ? "dark" : "light") + ".svg"
                fillMode: Image.PreserveAspectFit
                sourceSize.width: 520
                Accessible.name: Brand.tokens.brand.name
            }
            Label { text: qsTranslate("Flausen", "Everyday OS · by %1").arg(Brand.tokens.brand.parent); color: root.theme.text; Layout.alignment: Qt.AlignHCenter }
            Label { text: Brand.tokens.brand.tagline; color: root.theme.textMuted; Layout.alignment: Qt.AlignHCenter }
            Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: root.theme.border }
            Label { text: qsTranslate("Flausen", "Development build · flausen-os"); color: root.theme.text; font.bold: true }
            Label {
                Layout.fillWidth: true; wrapMode: Text.Wrap
                text: qsTranslate("Flausen", "This installation is built on CachyOS/Arch, KDE Plasma and Caelestia. Each project retains its name and license.")
                color: root.theme.text
            }
            Label {
                Layout.fillWidth: true; wrapMode: Text.Wrap
                text: qsTranslate("Flausen", "Interface: Qt Quick · %1").arg(Qt.platform.os)
                color: root.theme.textMuted
            }
            Label {
                Layout.fillWidth: true; wrapMode: Text.Wrap
                text: qsTranslate("Flausen", "Brand assets: Inter Display, SIL Open Font License 1.1. See the project for further attribution and release notes.")
                color: root.theme.textMuted
            }
            RowLayout {
                BrandButton { text: qsTranslate("Flausen", "System details"); onClicked: Qt.openUrlExternally("file:///etc/os-release") }
                BrandButton { text: qsTranslate("Flausen", "Credits"); onClicked: Qt.openUrlExternally(Qt.resolvedUrl("handoff/ATTRIBUTION_AND_RELEASE.md")) }
                Item { Layout.fillWidth: true }
                BrandButton { text: qsTranslate("Flausen", "Close"); onClicked: root.close() }
            }
        }
    }
    Shortcut { sequence: "Escape"; onActivated: root.close() }
}
