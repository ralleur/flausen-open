import QtQuick

QtObject {
    property bool footerAction: false
    property string text: ""
    property string icon
    property string trailingIcon
    property string activeIcon: icon
    property string activeText: text
    property bool visible: true
    property var value

    property string shortcutName
    property string shortcutText
    signal editShortcut(var target)

    signal clicked
}
