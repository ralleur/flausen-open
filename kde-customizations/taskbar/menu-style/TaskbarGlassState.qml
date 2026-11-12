pragma Singleton
import QtQuick

// A single dropdown pool per screen survives short-lived popover/Menu objects.
QtObject {
    id: root
    property var dropdowns: ({})
    property int nextOwner: 0
    function acquire(): int { return ++nextOwner; }
    function request(screen: string, owner: int, geometry: rect, reserve: rect,
                     radius: real, bottomAnchored: bool, active: bool): void {
        if (!active) {
            release(screen, owner);
            return;
        }
        const next = Object.assign({}, dropdowns);
        next[screen] = { owner: owner, geometry: geometry, reserve: reserve,
            radius: radius, bottomAnchored: bottomAnchored };
        dropdowns = next;
    }
    function release(screen: string, owner: int): void {
        if (dropdowns[screen]?.owner !== owner) return;
        const next = Object.assign({}, dropdowns);
        delete next[screen];
        dropdowns = next;
    }
}
