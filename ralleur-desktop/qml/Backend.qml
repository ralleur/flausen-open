import QtQuick
import Quickshell
import qs.services
import qs.modules.nexus

QtObject {
    id: root
    property var player: Players.active
    property int activeWorkspace: Hypr.activeWsId
    property string activeTitle: Hypr.activeToplevel?.title || "Ralleur Desktop"
    property var windows: Hypr.toplevels.values
    function fullscreen(screen: var): bool {
        const mon = Hypr.monitorFor(screen);
        const special = mon?.lastIpcObject.specialWorkspace?.name;
        const ws = special ? Hypr.workspaces.values.find(w => w.name === special) : mon?.activeWorkspace;
        return ws?.toplevels.values.some(t => t.lastIpcObject.fullscreen > 1) ?? false;
    }
    function workspace(id: int): void {
        Hypr.focusWorkspace(String(id));
    }
    function drawer(screen: var, name: string): void {
        if (name === "settings") {
            WindowFactory.create();
            return;
        }
        const state = ShellState.forScreen(screen);
        if (state)
            state[name] = !state[name];
    }
    function matches(win: var, app: var): bool {
        return app.classes.some(c => (win.lastIpcObject.class || "").toLowerCase().includes(c));
    }
    function running(app: var): bool {
        return windows.some(w => matches(w, app));
    }
    function launch(app: var): void {
        if (app.id === "home") {
            Quickshell.execDetached([Theme.base + "/bin/ralleur", "app", "home"]);
            return;
        }
        const win = windows.find(w => matches(w, app));
        if (win)
            Hypr.dispatch(Hypr.usingLua ? `hl.dsp.focus({ window = "address:${win.lastIpcObject.address}" })` : `focuswindow address:${win.lastIpcObject.address}`);
        else
            Quickshell.execDetached([Theme.base + "/bin/ralleur", "app", app.id]);
    }
}
