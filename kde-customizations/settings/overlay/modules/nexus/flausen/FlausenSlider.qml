pragma ComponentBehavior: Bound
import QtQuick
import qs.components.controls
import QtQuick.Controls
import qs.services
Slider {
    id: root
    property int radius: 3
    signal interaction(v: real)
    signal released(v: real)
    implicitHeight: 28
    onMoved: interaction(value)
    onPressedChanged: if (!pressed) released(value)
    implicitWidth: 200
    background: SegmentedTrack {
        control: root
        fillColor: Colours.palette.m3primary
        emptyColor: FlausenStyle.light ? "#c2c5c9" : "#575b60"
        outlineColor: FlausenStyle.light ? "#333b45" : "#e2e5e8"
    }
    handle: SegmentedHandle { control: root }
}
