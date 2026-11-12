pragma Singleton
import QtQuick
import Caelestia.Config
import qs.services

// Shared launcher/popover typography and material. Geometry belongs to each menu.
QtObject {
    readonly property font applicationFont: systemText.font
    readonly property string fontFamily: applicationFont.family
    readonly property real bodyPixels: 16
    readonly property real secondaryPixels: 13
    readonly property real captionPixels: 12
    readonly property real listPixels: 15
    readonly property color surface: Colours.light ? "#e6f4f5f7" : "#d911161d"
    readonly property color border: Colours.light ? "#70969ca5" : "#38ffffff"
    readonly property color ink: Colours.light ? "#20252d" : "#f3f4f6"
    readonly property color muted: Colours.light ? "#5b626d" : "#aeb6c2"
    readonly property color rule: Colours.light ? "#2420252d" : "#26ffffff"
    readonly property color cardFill: Colours.light ? "#0a000000" : "#09ffffff"
    readonly property color accent: "#287dff"
    // Native Dolphin context-menu values (dolphin-header/contextmenu.cpp).
    readonly property color contextSurface: Colours.light ? "#59f8f6f3" : "#401c2024"
    readonly property color contextBorder: Colours.light ? "#66ffffff" : "#38ffffff"
    readonly property color contextHover: Colours.light ? "#10000000" : "#18ffffff"
    readonly property int contextRadius: 14
    readonly property int contextPadding: 8
    readonly property int contextRowRadius: 9
    // Preserve the separate accessibility font scale; 1.15 is the menu baseline.
    function bodyPointSize(fontScale: real): real {
        return bodyPixels * 0.75 * fontScale / 1.15;
    }
    property Text systemText: Text { visible: false }
}
