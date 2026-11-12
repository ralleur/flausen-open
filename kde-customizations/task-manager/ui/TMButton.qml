import QtQuick
import QtQuick.Controls
import qs.modules.nexus.flausen
Button {
    id: button
    property int textAlignment: Text.AlignHCenter
    property bool selected: false
    property bool danger: false
    implicitHeight: 38
    implicitWidth: Math.max(38, label.implicitWidth + 28)
    opacity: enabled ? 1 : .4
    hoverEnabled: true
    contentItem: TMText { id: label; text: button.text; size: 14; horizontalAlignment: button.textAlignment; verticalAlignment: Text.AlignVCenter; color: button.danger ? '#f47c69' : FlausenStyle.text }
    background: Rectangle {
        radius: 10
        color: button.selected ? FlausenStyle.selected : button.hovered || button.down ? Qt.alpha(FlausenStyle.secondary, .12) : 'transparent'
        border.width: button.selected || button.danger || button.visualFocus ? 1 : 0
        border.color: button.danger ? '#f47c69' : button.visualFocus ? FlausenStyle.accent : FlausenStyle.line
    }
}
