pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io

Singleton {
    id: root
    property var tokens: ({})
    property string mode: "dark"
    property var iconPaths: ({})
    function icon(name: string): string {
        return iconPaths[name] || (Quickshell.hasThemeIcon(name) ? Quickshell.iconPath(name) : "");
    }
    readonly property var colors: tokens.modes ? tokens.modes[mode] : ({
            background: "#11161D",
            text: "#F2F1EF",
            surface: "#191E24",
            muted: "#AFB4BC",
            stroke: "#363D46",
            focus: "#73AEF4",
            elevated: "#252B33"
        })
    readonly property var geo: tokens.geometry || ({
            edge: 10,
            gap: 18,
            top: 32,
            dock: 52,
            widget: 248,
            cardRadius: 18,
            widgetBreakpoint: 1500,
            compactBreakpoint: 1100,
            widgetMinHeight: 650
        })
    readonly property var type: tokens.typography || ({
            ui: "Inter",
            mono: "monospace",
            body: 12,
            small: 11,
            clock: 54
        })
    readonly property var brand: tokens.brand || ({
            blue: "#2563C9",
            red: "#DF493F",
            amber: "#E4AD22",
            green: "#3F7D44"
        })
    readonly property string base: Quickshell.env("RALLEUR_ROOT") || Quickshell.shellDir
    readonly property string state: Quickshell.env("RALLEUR_STATE") || "/tmp/ralleur-preview"
    function toggle(): void {
        Quickshell.execDetached([base + "/bin/ralleur", "theme", mode === "dark" ? "light" : "dark"]);
    }
    FileView {
        path: root.base + "/design/tokens.json"
        onLoaded: root.tokens = JSON.parse(text())
    }
    FileView {
        path: root.state + "/icons.json"
        onLoaded: root.iconPaths = JSON.parse(text())
    }
    FileView {
        path: root.state + "/theme.json"
        watchChanges: true
        onFileChanged: reload()
        onLoaded: root.mode = JSON.parse(text()).mode
    }
}
