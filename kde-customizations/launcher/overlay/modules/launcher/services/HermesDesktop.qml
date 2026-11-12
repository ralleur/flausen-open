pragma Singleton

import QtQuick
import Quickshell
import Quickshell.Io
import Caelestia.Config
import qs.services

QtObject {
    readonly property var ipc: IpcHandler {
        target: "ralleurHermesDesktop"
        function status(): string {
            return JSON.stringify({theme: Colours.light ? "light" : "dark",
                volume_percent: Math.round(Audio.volume * 100), muted: Audio.muted,
                audio_output: Audio.sink?.description ?? qsTranslate("Flausen", "Unavailable")});
        }
        function launch(app: string): string {
            const ids = {files: ["org.kde.dolphin"], settings: ["flausen-settings", "org.kde.systemsettings"], dateien: ["org.kde.dolphin"], einstellungen: ["systemsettings", "org.kde.systemsettings"],
                browser: ["chromium"], terminal: ["org.kde.konsole"], steam: ["steam"],
                battlenet: ["lab-battlenet"], discord: ["lab-discord"], wowup: ["lab-wowup"]};
            const candidates = ids[app];
            if (!candidates) return JSON.stringify({error: qsTranslate("Flausen", "Unknown app.")});
            const entry = candidates.map(id => DesktopEntries.byId(id)).find(app => app);
            if (!entry) return JSON.stringify({error: qsTranslate("Flausen", "The app is not installed.")});
            Apps.launch(entry);
            return JSON.stringify({launched: app});
        }
    }
}
