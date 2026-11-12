pragma ComponentBehavior: Bound

import QtQuick
import Quickshell.Io
import Caelestia.Config
import qs.services

Bar {
    id: root

    dockOnly: true
    height: thickness
    readonly property real zoomExtent: (Visibilities.docks.get(root.screen.name)?.zoomActive ?? false) ? Math.ceil(thickness * SplitBarSettings.dockMagnificationAmount) : 0
    readonly property real footprintWidth: Math.min(width, middleZoneSize + (Visibilities.docks.get(root.screen.name)?.zoomSpread ?? 0) * 2)

    // Read-only diagnostics for the installed geometry and native popout routing.
    IpcHandler {
        target: "ralleurTaskbar-" + root.screen.name
        function inspect(): string {
            const top = root.parent.bar;
            const loader = top.children.find(child => child.item !== undefined);
            const content = loader?.item;
            const popout = root.popouts.parent;
            return JSON.stringify({
                screen: root.screen.name,
                glass: {type: "localNativeBackdrop", opacity: MenuStyle.taskbarSurface.a, additionalLocalPasses: 8},
                top: { position: top.position, scale: top.barScale, height: top.height, contentHeight: top.contentWidth,
                    left: content?.leftEntries, middle: content?.middleEntries, right: content?.rightEntries },
                dock: { visible: root.visible, scale: root.rawScale, x: (root.width - root.footprintWidth) / 2,
                    y: root.y, width: root.footprintWidth, height: root.height,
                    left: root.leftEntries, middle: root.middleEntries, right: root.rightEntries,
                    sections: Visibilities.docks.get(root.screen.name)?.inspectSections() },
                pointer: {x: root.parent.mouseX, y: root.parent.mouseY,
                    inDock: root.parent.inBottomDock(root.parent.mouseX, root.parent.mouseY)},
                fullscreen: root.fullscreen,
                popout: { name: root.popouts.currentName, open: root.popouts.hasCurrent,
                    position: popout.popoutPosition, x: popout.x, y: popout.y,
                    width: popout.width, height: popout.height,
                    parentY: popout.parent.topMargin }
            });
        }
    }

}
