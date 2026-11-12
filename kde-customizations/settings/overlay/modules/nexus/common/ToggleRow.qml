pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import qs.components
import qs.components.controls
import qs.modules.nexus.flausen
FlausenSwitch {
    id: root
    property string subtext
    property var reset
    property alias first: bg.first
    property alias last: bg.last
    readonly property alias bg: bg
    Layout.fillWidth: true
    horizontalPadding: 16
    verticalPadding: 14
    rightPadding: resetBtn.visible ? resetBtn.width + 54 : 16
    implicitHeight: Math.max(58, column.implicitHeight + verticalPadding * 2)
    background: ConnectedRect {
        id: bg
        border.color: root.visualFocus ? FlausenStyle.accent : FlausenStyle.line
    }
    contentItem: Column {
        id: column
        spacing: root.subtext ? 4 : 0
        Text { width: Math.max(0, parent.width - 60); text: root.text; font: FlausenStyle.typeface(14); color: FlausenStyle.text; elide: Text.ElideRight }
        Text { width: Math.max(0, parent.width - 60); visible: text.length > 0; text: root.subtext; font: FlausenStyle.typeface(12); color: FlausenStyle.secondary; wrapMode: Text.WordWrap }
    }
    SettingResetButton {
        id: resetBtn
        anchors.right: parent.right
        anchors.rightMargin: 12
        anchors.verticalCenter: parent.verticalCenter
        options: root.reset
    }
}
