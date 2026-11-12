// SPDX-License-Identifier: MIT
import QtQuick
import org.kde.kirigami as Kirigami
Rectangle {
    property bool dark: true
    property bool showLock: false
    property bool focused: parent.activeFocus
    implicitWidth: 48
    implicitHeight: 48
    radius: 24
    color: dark ? "#662b3035" : "#ddffffff"
    border.width: focused ? 2 : 1
    border.color: focused ? "#729bd4" : dark ? "#555b6168" : "#77ffffff"
    Kirigami.Icon {
        visible: parent.showLock
        source: "object-locked"
        width: 18; height: 18
        anchors { left: parent.left; leftMargin: 17; verticalCenter: parent.verticalCenter }
        color: parent.dark ? "#eeeeef" : "#242629"
    }
}

