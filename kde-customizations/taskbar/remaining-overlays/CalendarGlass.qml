pragma ComponentBehavior: Bound
import QtQuick
import qs.components

// Compatibility for the calendar installer; all taskbar surfaces share one helper.
TaskbarGlass {
    required property Item target
    geometry: Qt.rect(target.x + target.parent.leftMargin,
        target.y + target.parent.topMargin, target.width, target.height)
}
