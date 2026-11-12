import "../effects"
import QtQuick
import QtQuick.Templates
import Caelestia.Config
import qs.components
import qs.services
import qs.utils

Slider {
    id: root

    required property string icon
    property color fillColor: Colours.palette.m3primary
    property real oldValue
    property bool initialized

    orientation: Qt.Vertical

    implicitWidth: 34
    implicitHeight: 200
    background: SegmentedTrack {
        control: root
        fillColor: root.fillColor
        emptyColor: Colours.light ? "#c2c5c9" : "#575b60"
        outlineColor: Colours.light ? "#333b45" : "#e2e5e8"
    }
    handle: SegmentedHandle { control: root }
}
