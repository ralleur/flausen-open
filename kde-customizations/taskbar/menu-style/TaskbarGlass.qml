pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import Quickshell.Wayland

// Persistent local blur surfaces. Animate regions, never native buffer sizes.
Scope {
    id: root
    required property var screen
    required property rect geometry
    required property bool active
    property rect reserveGeometry: geometry
    property bool prewarm: false
    property bool suspended: false
    property bool centered: false
    property bool bottomAnchored: false
    property real cornerRadius: 28
    property rect cutout: Qt.rect(0, 0, 0, 0)
    property size minimumSize: Qt.size(64, 64)
    property Region customShape: null
    property bool ready: false
    property bool initialized: false
    property int capacityWidth: minimumSize.width
    property int capacityHeight: minimumSize.height
    property int extentWidth: 16
    property int extentHeight: 16
    readonly property bool showing: active && !suspended
    readonly property int activePassCount: root.showing ? passes.instances.length : 0
    readonly property int pooledPassCount: passes.instances.length
    readonly property int mappedPassCount: passes.instances.filter(pass => pass.visible).length
    readonly property int windowX: Math.max(0, Math.min(screen.width - capacityWidth,
        Math.round(centered ? geometry.x + geometry.width / 2 - capacityWidth / 2 : geometry.x)))
    readonly property int windowY: Math.max(0, Math.min(screen.height - capacityHeight,
        Math.round(bottomAnchored ? geometry.y + geometry.height - capacityHeight : geometry.y)))
    readonly property int regionX: Math.round(geometry.x - windowX)
    readonly property int regionY: Math.round(geometry.y - windowY)

    readonly property int extentX: Math.max(0, Math.min(capacityWidth - extentWidth,
        centered ? Math.floor((capacityWidth - extentWidth) / 2) : regionX))
    readonly property int extentY: Math.max(0, Math.min(capacityHeight - extentHeight,
        bottomAnchored ? regionY + Math.round(geometry.height) - extentHeight : regionY))

    function prepare(resetExtent: bool): void {
        if (!ready || (!active && !prewarm) || !screen || screen.width <= 0 || screen.height <= 0 || !reserveGeometry || !minimumSize) return;
        // Bucket growth only when content/settings exceed the warmed capacity.
        const w = Math.ceil(Math.max(minimumSize.width, reserveGeometry.width, geometry.width) / 64) * 64;
        const h = Math.ceil(Math.max(minimumSize.height, reserveGeometry.height, geometry.height) / 64) * 64;
        capacityWidth = Math.min(screen.width, Math.max(capacityWidth, w));
        capacityHeight = Math.min(screen.height, Math.max(capacityHeight, h));
        // Keep KWin's texture extent stable while the visible rounded region grows.
        // Small 16-pixel buckets leave room for subpixel animation overshoot.
        const ew = Math.ceil(Math.max(1, geometry.width, reserveGeometry.width) / 16) * 16;
        const eh = Math.ceil(Math.max(1, geometry.height, reserveGeometry.height) / 16) * 16;
        extentWidth = Math.min(capacityWidth, (resetExtent ? ew : Math.max(extentWidth, ew)));
        extentHeight = Math.min(capacityHeight, (resetExtent ? eh : Math.max(extentHeight, eh)));
        initialized = true;
    }
    onActiveChanged: prepare(active)
    onGeometryChanged: if (active && (geometry.width > extentWidth || geometry.height > extentHeight)) prepare(false)
    onPrewarmChanged: prepare(false)
    onReserveGeometryChanged: prepare(false)
    onMinimumSizeChanged: prepare(false)
    onScreenChanged: prepare(true)
    Component.onCompleted: { ready = true; prepare(true); }
    Connections {
        target: root.screen
        function onGeometryChanged(): void { root.prepare(true); }
    }

    // Shared QRegion avoids building the same rounded shape eight times.
    property Region blurShape: Region {
        // An offscreen sentinel prevents an empty region from meaning "whole window".
        Region { x: -10; y: -10; width: 1; height: 1 }
        // Two single-pixel edge anchors stabilize KWin's blur texture extent.
        // They carry no tint; the actual rounded visible region remains below.
        Region {
            x: root.extentX; y: root.extentY
            width: root.showing ? 1 : 0; height: root.showing ? 1 : 0
            intersection: Intersection.Combine
        }
        Region {
            x: root.extentX + root.extentWidth - 1
            y: root.extentY + root.extentHeight - 1
            width: root.showing ? 1 : 0; height: root.showing ? 1 : 0
            intersection: Intersection.Combine
        }
        Region {
            x: root.regionX; y: root.regionY
            width: root.showing ? Math.round(root.geometry.width) : 0
            height: root.showing ? Math.round(root.geometry.height) : 0
            radius: root.cornerRadius
            intersection: Intersection.Combine
        }
        Region {
            x: root.regionX + root.cutout.x; y: root.regionY + root.cutout.y
            width: root.cutout.width; height: root.cutout.height
            radius: Math.min(width, height) / 2
            intersection: Intersection.Subtract
        }
    }
    Variants {
        id: passes
        model: root.initialized ? [0, 1, 2, 3, 4, 5, 6, 7] : []
        PanelWindow {
            required property var modelData
            screen: root.screen
            visible: true
            anchors { top: true; left: true }
            margins { top: root.windowY; left: root.windowX }
            implicitWidth: root.capacityWidth
            implicitHeight: root.capacityHeight
            exclusionMode: ExclusionMode.Ignore
            // Keep native surfaces alive below applications while inactive. Hiding
            // them would tear down Qt/Wayland resources and reintroduce the hitch.
            WlrLayershell.layer: root.showing ? WlrLayer.Top : WlrLayer.Bottom
            WlrLayershell.namespace: "ralleur-taskbar-glass"
            WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
            mask: Region {}
            color: "transparent"
            surfaceFormat.opaque: false
            // A minimal paint node keeps transparent Wayland surfaces in KWin's
            // blur stack without repainting a full translucent card each frame.
            Rectangle {
                x: root.extentX; y: root.extentY
                width: 1; height: 1
                color: "#01000000"
                visible: root.showing
            }
            BackgroundEffect.blurRegion: root.customShape ?? root.blurShape
        }
    }
}
