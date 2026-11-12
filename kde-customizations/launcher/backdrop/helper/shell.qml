import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
ShellRoot {
    id: root
    property var shownScreens: ({})
    // Dolphin and launcher clients keep a persistent socket: disconnect/crash releases their surface.
    property var contexts: ({})
    readonly property bool contextActive: Object.keys(contexts).length > 0
    function updateContext(owner, update): void {
        const next = Object.assign({}, contexts);
        if (update && update.shown === true) next[owner] = update.cutouts || [];
        else delete next[owner];
        contexts = next;
    }
    function cutouts(): var {
        let result = [];
        for (const owner of Object.keys(contexts)) result = result.concat(contexts[owner]);
        return result;
    }
    function syncBlur(): void {
        if (!blurSettings.running) {
            blurSettings.command = [Quickshell.env("HOME") + "/.local/libexec/ralleur/blur-settings",
                                    contextActive ? "on" : "off", "dolphin-context-backdrop"];
            blurSettings.running = true;
        }
    }
    onContextActiveChanged: syncBlur()
    Component.onCompleted: syncBlur()
    Process {
        id: blurSettings
        onExited: {
            if (command[1] !== (root.contextActive ? "on" : "off")) root.syncBlur();
        }
    }
    settings.watchFiles: false
    IpcHandler {
        target: "backdrop"
        function set(screenName: string, shown: bool): void {
            const next = Object.assign({}, root.shownScreens);
            next[screenName] = shown;
            root.shownScreens = next;
        }
        function inspect(): string { return JSON.stringify(root.shownScreens); }
        function inspectContexts(): string { return JSON.stringify(root.contexts); }
    }
    SocketServer {
        active: true
        path: Quickshell.env("XDG_RUNTIME_DIR") + "/ralleur-start-backdrop.sock"
        handler: Socket {
            id: client
            property string contextOwner: ""
            onConnectionStateChanged: {
                if (!connected && contextOwner) root.updateContext(contextOwner, null);
            }
            Component.onDestruction: { if (contextOwner) root.updateContext(contextOwner, null); }
            parser: SplitParser {
                onRead: message => {
                    try {
                        const update = JSON.parse(message);
                        if (typeof update.owner === "string" && (update.owner.startsWith("dolphin:") || update.owner.startsWith("launcher:"))) {
                            if (client.contextOwner && client.contextOwner !== update.owner)
                                root.updateContext(client.contextOwner, null);
                            client.contextOwner = update.owner;
                            root.updateContext(update.owner, update);
                            return;
                        }
                        const next = Object.assign({}, root.shownScreens);
                        next[update.screen] = update.shown === true;
                        root.shownScreens = next;
                    } catch (error) { console.warn("Invalid backdrop request:", error); }
                }
            }
        }
    }
    Variants {
        model: Quickshell.screens
        PanelWindow {
            id: surface
            required property var modelData
            screen: modelData
            readonly property var cutouts: root.cutouts()
            visible: root.shownScreens[modelData.name] === true || root.contextActive
            anchors { top: true; bottom: true; left: true; right: true }
            exclusionMode: ExclusionMode.Ignore
            WlrLayershell.layer: WlrLayer.Top
            WlrLayershell.namespace: "ralleur-start-backdrop"
            WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
            mask: Region {}
            color: "#02000000"
            surfaceFormat.opaque: false
            Variants {
                id: holes
                model: surface.cutouts
                Region {
                    required property var modelData
                    x: modelData.x - surface.screen.x
                    y: modelData.y - surface.screen.y
                    width: modelData.width
                    height: modelData.height
                    radius: 14
                    intersection: Intersection.Subtract
                }
            }
            BackgroundEffect.blurRegion: Region {
                item: surface.contentItem
                regions: holes.instances
            }
        }
    }
}
