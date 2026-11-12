pragma Singleton
import QtQuick
import Caelestia.Config
import qs.services

// Shared launcher/popover typography and material. Geometry belongs to each menu.
QtObject {
    id: root
    readonly property font applicationFont: systemText.font
    readonly property string fontFamily: applicationFont.family
    // Keep Caelestia's normal text tokens on the same system family as menus.
    // Setting StyledText alone misses callers assigning an entire token font
    // (e.g. Now Playing). Sizes, weights, mono and icon fonts stay independent.
    readonly property list<QtObject> systemFontBindings: [
        Binding { target: GlobalConfig.appearance.font.body; property: "family"; value: root.fontFamily },
        Binding { target: GlobalConfig.appearance.font.label; property: "family"; value: root.fontFamily },
        Binding { target: GlobalConfig.appearance.font.title; property: "family"; value: root.fontFamily },
        Binding { target: GlobalConfig.appearance.font.headline; property: "family"; value: root.fontFamily }
    ]
    readonly property real bodyPixels: 16
    readonly property real secondaryPixels: 13
    readonly property real captionPixels: 12
    readonly property real listPixels: 15
    readonly property color surface: Colours.light ? "#e6f4f5f7" : "#d911161d"
    // Approved smoke material, shared by bars, launcher and dashboard.
    readonly property color smokeSurface: Colours.light ? "#e6e9ecef" : "#b823292e"
    readonly property color taskbarSurface: smokeSurface
    readonly property color calendarSurface: taskbarSurface
    readonly property color border: Colours.light ? "#70969ca5" : "#38ffffff"
    readonly property color ink: Colours.light ? "#20252d" : "#f3f4f6"
    readonly property color muted: Colours.light ? "#5b626d" : "#aeb6c2"
    readonly property color rule: Colours.light ? "#2420252d" : "#26ffffff"
    readonly property color cardFill: Colours.light ? "#0a000000" : "#09ffffff"
    readonly property color accent: "#287dff"
    // Primary-action reference, first applied to Screen Capture. Keep the hue
    // stable; depth comes from a restrained vertical light falloff.
    readonly property color primaryTop: "#2588ff"
    readonly property color primaryBottom: "#0871ef"
    readonly property color primaryEdge: "#7db5ff"
    readonly property color primaryLight: "#38ffffff"
    // Solid blue fills only; muted selection tints and other accent hues survive.
    function isBlueControl(colour: color): bool {
        return colour.a > 0.85 && colour.b > colour.r * 1.25
            && colour.b > colour.g * 1.06 && colour.b - colour.r > 0.15;
    }
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
    // Preserve widget-specific size/weight while sharing the application family.
    function withSystemFamily(role: font): font {
        return Qt.font({ family: fontFamily, pixelSize: role.pixelSize,
            weight: role.weight, italic: role.italic,
            capitalization: role.capitalization, letterSpacing: role.letterSpacing });
    }
    property Text systemText: Text { visible: false }
}
