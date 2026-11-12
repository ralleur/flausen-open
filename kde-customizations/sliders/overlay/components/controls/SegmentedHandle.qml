import QtQuick
Item {
    required property var control
    readonly property bool vertical: control.orientation === Qt.Vertical
    implicitWidth: vertical ? 28 : 10
    implicitHeight: vertical ? 10 : 28
    x: control.leftPadding + (vertical ? (control.availableWidth - width) / 2 : control.visualPosition * (control.availableWidth - width))
    y: control.topPadding + (vertical ? control.visualPosition * (control.availableHeight - height) : (control.availableHeight - height) / 2)
}
