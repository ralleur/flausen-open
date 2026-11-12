import QtQuick
import Quickshell
import Quickshell.Io
import "ui"
ShellRoot {
    settings.watchFiles: false
    TaskManager { id: manager }
    IpcHandler {
        target: "taskmanager"
        function open(): void { manager.visible = true; manager.minimized = false; manager.raiseWindow(); }
    }
}
