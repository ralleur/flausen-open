import QtQuick
import QtQuick.Layouts
import qs.components
import qs.modules.nexus.flausen
StyledText {
    property bool first
    Layout.fillWidth: true
    Layout.topMargin: first ? 0 : 16
    Layout.bottomMargin: 6
    color: FlausenStyle.text
    font: FlausenStyle.typeface(17)
    elide: Text.ElideRight
}
