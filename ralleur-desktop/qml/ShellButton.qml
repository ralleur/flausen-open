import QtQuick
import QtQuick.Controls
import Quickshell

Button {
    id: root
    property string iconName: ""
    property string hint: text
    property bool selected: false
    implicitWidth: Theme.geo.action ?? 36
    implicitHeight: Theme.geo.action ?? 36
    hoverEnabled: true
    focusPolicy: Qt.StrongFocus
    opacity: enabled ? 1 : 0.35
    Accessible.name: hint
    ToolTip.visible: hovered && hint.length > 0
    ToolTip.text: hint
    ToolTip.delay: 600
    background: Rectangle {
        radius: Theme.geo.buttonRadius ?? 11
        color: root.selected || root.hovered || root.down ? Qt.alpha(Theme.colors.text, Theme.tokens.effects?.hoverOpacity ?? 0.08) : "transparent"
        border.width: root.activeFocus ? (Theme.geo.focusWidth ?? 2) : 0
        border.color: Theme.colors.focus
    }
    contentItem: Item {
        Image {
            id: picture
            anchors.centerIn: parent
            width: Theme.type.icon ?? 23
            height: Theme.type.icon ?? 23
            source: root.iconName ? Theme.icon(root.iconName) : ""
            visible: source.toString().length > 0 && status !== Image.Error
            sourceSize: Qt.size(32, 32)
        }
        ShellText {
            anchors.centerIn: parent
            text: root.iconName ? "□" : root.text
            visible: !picture.visible
            font.pixelSize: Theme.type.buttonGlyph ?? 17
        }
    }
}
