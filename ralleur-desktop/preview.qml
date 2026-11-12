import QtQuick
import Quickshell
import Quickshell.Io
import "qml"

ShellRoot {
    PreviewBackend {
        id: backend
    }
    FloatingWindow {
        id: window
        title: "Ralleur · Komponenten-Vorschau"
        implicitWidth: Number(Quickshell.env("RALLEUR_WIDTH")) || 1586
        implicitHeight: Number(Quickshell.env("RALLEUR_HEIGHT")) || 992
        color: Theme.colors.background
        Desktop {
            id: desktop
            anchors.fill: parent
            backend: backend
            shellScreen: window.screen
        }
        IpcHandler {
            target: "preview"
            function capture(path: string): void {
                desktop.grabToImage(result => result.saveToFile(path));
            }
            function widgets(): void {
                ShellUi.toggle(window.width, window.height);
            }
            function resize(width: int, height: int): void {
                window.width = width;
                window.height = height;
            }
        }
    }
}
