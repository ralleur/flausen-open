pragma Singleton
import QtQuick
import Quickshell
import Caelestia.Config
import qs.services
Singleton {
    readonly property real fontScale: GlobalConfig.appearance.font.scale
    readonly property int motionDuration: GlobalConfig.appearance.anim.enabled ? 120 : 0
    readonly property bool light: Colours.light
    readonly property color text: light ? "#202123" : "#f3f4f5"
    readonly property color secondary: light ? "#73767c" : "#aeb3ba"
    readonly property color surface: light ? "#f7f6f5" : "#1b1e23"
    readonly property color sidebar: light ? "#eeedec" : "#16191e"
    readonly property color card: light ? "#faf9f8" : "#20242a"
    readonly property color line: light ? "#dcdcdc" : "#373c43"
    readonly property color modelBlue: light ? "#2862c4" : "#347fff"
    readonly property color contextYellow: light ? "#b88a3d" : "#efb34f"
    readonly property color selected: light ? "#dedfe2" : "#2c394a"
    readonly property color accent: Colours.scheme.startsWith("flausen-") ? Colours.palette.m3primary : "#347fff"
    function typeface(size: real): font { return Qt.font({family: family, pixelSize: fontScale * size}); }
    readonly property string family: "Inter"
}
