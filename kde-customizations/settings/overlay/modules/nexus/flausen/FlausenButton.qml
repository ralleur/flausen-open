pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
Button {
    id: root
    horizontalPadding: 17; verticalPadding: 9
    font {family:FlausenStyle.family; pixelSize:FlausenStyle.fontScale * 13}
    background: Rectangle {
        implicitHeight: 34
        radius: height/2
        color: root.down ? FlausenStyle.selected : root.hovered ? Qt.alpha(FlausenStyle.text,0.07) : "transparent"
        border {width:root.visualFocus ? 2 : 1; color:root.visualFocus ? FlausenStyle.accent : FlausenStyle.line}
    }
    contentItem: Text {text:root.text; font:root.font; color:FlausenStyle.text; horizontalAlignment:Text.AlignHCenter; verticalAlignment:Text.AlignVCenter; elide:Text.ElideRight}
}
