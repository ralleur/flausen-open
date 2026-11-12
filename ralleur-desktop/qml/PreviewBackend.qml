import QtQuick
import Quickshell
import Quickshell.Services.Mpris

QtObject {
    property var player: Mpris.players.values[0] ?? null
    property int activeWorkspace: 0
    property string activeTitle: "Vorschau · Shell mit Live-Daten"
    function workspace(id: int): void {
        console.log("Workspace requires Hyprland:", id);
    }
    function drawer(screen: var, name: string): void {
        console.log("Caelestia drawer requires runtime:", name);
    }
    function running(app: var): bool {
        return false;
    }
    function launch(app: var): void {
        Quickshell.execDetached([Theme.base + "/bin/ralleur", "app", app.id]);
    }
}
