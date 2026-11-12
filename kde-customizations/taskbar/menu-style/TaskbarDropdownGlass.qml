pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import qs.services

Scope {
    id: root
    required property var screen
    required property rect geometry
    required property bool active
    property rect reserveGeometry: geometry
    property real cornerRadius: 14
    property bool bottomAnchored: false
    property int owner: 0
    property string registeredScreen: ""
    function publish(): void {
        if (!owner) return;
        const name = screen?.name ?? "";
        if (registeredScreen && registeredScreen !== name)
            TaskbarGlassState.release(registeredScreen, owner);
        registeredScreen = name;
        if (name) TaskbarGlassState.request(name, owner, geometry, reserveGeometry,
            cornerRadius, bottomAnchored, active);
    }
    onActiveChanged: publish()
    onGeometryChanged: Qt.callLater(root.publish)
    onReserveGeometryChanged: Qt.callLater(root.publish)
    onCornerRadiusChanged: publish()
    onBottomAnchoredChanged: publish()
    onScreenChanged: publish()
    Component.onCompleted: { owner = TaskbarGlassState.acquire(); publish(); }
    Component.onDestruction: if (registeredScreen) TaskbarGlassState.release(registeredScreen, owner)
}
