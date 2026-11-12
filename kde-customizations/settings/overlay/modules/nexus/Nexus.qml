pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Effects
import Flausen.Settings
import QtQuick.Window
import QtQuick.Controls as QQC
import QtQuick.Layouts
import Caelestia.Config
import qs.components
import qs.services
import qs.modules.nexus
import "flausen"
Item {
    id: root
    property int initialPageIdx: 0
    property int initialSubPageIdx: -1
    readonly property NexusState nState: NexusState {
        id: state
        currentPageIdx: root.initialPageIdx
        Component.onCompleted: { if (root.initialSubPageIdx !== -1) openSubPage(root.initialSubPageIdx); }
        onClose: root.close()
    }
    property color blobColour: FlausenStyle.surface
    signal close
    signal minimizeRequested
    signal maximizeRequested
    signal moveRequested
    property bool windowMaximized: false
    readonly property real frameRadius: nState.isWindow && !windowMaximized ? 12 : 0
    SystemPalette { id: windowPalette }
    WindowFrame { id: nativeFrame; objectName: "settingsWindowFrame" }
    layer.enabled: nState.isWindow && !windowMaximized
    layer.effect: MultiEffect {
        maskEnabled: true
        maskSource: frameMask
        Rectangle {
            id: frameMask
            anchors.fill: parent
            radius: root.frameRadius
            color: "white"
            visible: false
            layer.enabled: true
        }
        maskThresholdMin: 0.5
        maskSpreadAtMin: 1
    }
    Binding {
        target: root.Window.window
        property: "flags"
        value: Qt.Window | Qt.FramelessWindowHint
        when: root.nState.isWindow && root.Window.window !== null
    }
    function requestClose(): void { nState.requestExit(); }
    implicitWidth: Math.min(1180, (nState.screen?.width ?? 1440) * 0.86)
    // Fit the Appearance overview, including its bottom actions, at the default size.
    implicitHeight: Math.min(900, (nState.screen?.height ?? 1000) * 0.90)
    Rectangle { anchors.fill: parent; color: GlobalConfig.appearance.transparency.enabled ? Qt.alpha(FlausenStyle.surface, 0.94) : FlausenStyle.surface }
    Rectangle { width: nav.width + 40; anchors.top: parent.top; anchors.bottom: parent.bottom; color: FlausenStyle.sidebar }
    Rectangle { x: nav.width + 40; width: 1; height: parent.height; color: FlausenStyle.line; opacity: 0.5 }
    NavPane {
        id: nav
        anchors { left: parent.left; top: parent.top; bottom: parent.bottom; margins: 20 }
        width: root.width < 850 ? 225 : 260
        nState: state
    }
    FlausenKcmPage {
        id: systemPage
        visible: nState.systemModule !== ""
        nState: state
        anchors {left:nav.right;right:parent.right;top:parent.top;bottom:parent.bottom;leftMargin:52;rightMargin:32;topMargin:58;bottomMargin:20}
    }
    Item {
        visible: nState.isWindow
        x: nav.width + 40
        width: parent.width - x
        height: 40
        z: 10
        MouseArea {
            anchors.fill: parent
            anchors.rightMargin: 111
            onPressed: root.moveRequested()
            onDoubleClicked: root.maximizeRequested()
        }
        Row {
            anchors.right: parent.right
            anchors.rightMargin: 5
            anchors.top: parent.top
            anchors.topMargin: 5
            spacing: 6
            WindowControl { controlAction: "minimize"; description: qsTranslate("Flausen", "Minimize"); onClicked: root.minimizeRequested() }
            WindowControl { controlAction: "maximize"; description: root.windowMaximized ? qsTranslate("Flausen", "Restore") : qsTranslate("Flausen", "Maximize"); onClicked: root.maximizeRequested() }
            WindowControl { controlAction: "close"; description: qsTranslate("Flausen", "Close"); onClicked: root.requestClose() }
        }
    }
    QQC.Dialog {
        id: leaveDialog
        parent: root
        anchors.centerIn: parent
        width: Math.min(540, parent.width-40)
        modal: true
        closePolicy: QQC.Popup.NoAutoClose
        padding: 24
        background: Rectangle {radius:18;color:FlausenStyle.card;border.width:1;border.color:FlausenStyle.line}
        contentItem: ColumnLayout {
            spacing:20
            Text {text:qsTranslate("Flausen", "Apply changes?");font:FlausenStyle.typeface(21);color:FlausenStyle.text;Layout.fillWidth:true;wrapMode:Text.WordWrap}
            Text {text:qsTranslate("Flausen", "This page has unsaved changes.");font:FlausenStyle.typeface(14);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
            RowLayout {
                Layout.fillWidth:true
                FlausenButton {text:qsTranslate("Flausen", "Keep editing");onClicked:{state.cancelPending();leaveDialog.close();}}
                Item {Layout.fillWidth:true}
                FlausenButton {text:qsTranslate("Flausen", "Discard");onClicked:{leaveDialog.close();systemPage.discardAndContinue();}}
                FlausenButton {text:qsTranslate("Flausen", "Apply");onClicked:{leaveDialog.close();systemPage.saveAndContinue();}}
            }
        }
    }
    Connections {target:state;function onConfirmLeave(){leaveDialog.open();}}
    Pages {
        visible: state.systemModule === ""
        anchors { left: nav.right; right: parent.right; top: parent.top; bottom: parent.bottom; leftMargin: 52; rightMargin: 32; topMargin: 58; bottomMargin: 20 }
        nState: state
    }
    Rectangle {
        anchors.fill: parent
        z: 30
        visible: nState.isWindow
        color: "transparent"
        radius: root.frameRadius
        border.width: 1
        border.color: Qt.alpha(windowPalette.mid, 90 / 255)
    }
    Shortcut { sequence: "Escape"; enabled: !leaveDialog.opened; onActivated: state.requestBack() }
}
