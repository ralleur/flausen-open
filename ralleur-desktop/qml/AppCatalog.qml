pragma Singleton
import Quickshell

Singleton {
    readonly property var apps: [
        {
            id: "browser",
            name: "Browser",
            icon: Quickshell.hasThemeIcon("firefox") ? "firefox" : "chromium",
            classes: ["firefox", "zen", "chromium"]
        },
        {
            id: "code",
            name: "Editor",
            icon: Quickshell.hasThemeIcon("visual-studio-code") ? "visual-studio-code" : "kate",
            classes: ["code", "codium", "kate"]
        },
        {
            id: "terminal",
            name: "Terminal",
            icon: "utilities-terminal",
            classes: ["kitty", "konsole", "foot"]
        },
        {
            id: "files",
            name: "Dateien",
            icon: "system-file-manager",
            classes: ["thunar", "dolphin", "nemo"]
        },
        {
            id: "music",
            name: "Musik",
            icon: "mpv",
            classes: ["spotify", "elisa", "rhythmbox", "mpv"]
        }
    ]
}
