pragma Singleton
pragma ComponentBehavior: Bound
import QtQuick
import QtCore
import Quickshell
import Quickshell.Io
import Caelestia
import qs.services

Singleton {
    id: root
    property var status: ({})
    property string error: ""
    property double lastCheck: 0
    property bool online: true
    readonly property bool checking: probe.running && online
    readonly property var sources: [
        {key: "steam", name: "Steam", hint: qsTranslate("Flausen", "Client updates and beta channel in Steam → Settings → Interface"), desktop: "steam", url: "steam://open/settings"},
        {key: "steamGames", name: qsTranslate("Flausen", "Steam · Games"), hint: qsTranslate("Flausen", "Downloads, schedule and limits; per game: Properties → Updates"), desktop: "steam", url: "steam://open/downloads"},
        {key: "battlenet", name: "Battle.net", hint: qsTranslate("Flausen", "Client updates are managed by Battle.net. Open Settings in the launcher."), desktop: "lab-battlenet"},
        {key: "battlenetGames", name: qsTranslate("Flausen", "Battle.net · Games"), hint: qsTranslate("Flausen", "In the launcher: Settings → Downloads → Automatic updates"), desktop: "lab-battlenet"},
        {key: "wowup", name: "WowUp", hint: qsTranslate("Flausen", "App updates and addons: Options → WoW clients; configure individual addons separately"), desktop: "lab-wowup"},
        {key: "artcraft", name: "ArtCraft · Suite", hint: qsTranslate("Flausen", "Configure suite updates, check interval and automatic updates in the ArtCraft Launcher"), desktop: "ai.storyteller.artcraft-launcher"}
    ]
    readonly property int pendingCount: sources.reduce((sum, source) => sum + (enabled(source.key) ? (status[source.key]?.pending?.length ?? 0) + (status[source.key]?.addonPending ?? 0) : 0), 0)
    readonly property bool hasErrors: sources.some(source => enabled(source.key) && !!status[source.key]?.error)
    readonly property string overview: checking ? qsTranslate("Flausen", "Checking online …") : pendingCount > 0 ? pendingCount + qsTranslate("Flausen", " updates available") : hasErrors ? qsTranslate("Flausen", "Some sources are unavailable") : qsTranslate("Flausen", "No known app updates")
    Settings {
        id: prefs
        category: "RalleurUpdateHub"
        property string hiddenSources: "[]"
    }
    function enabled(key: string): bool {
        try { return !JSON.parse(prefs.hiddenSources).includes(key); } catch (e) { return true; }
    }
    function setEnabled(key: string, value: bool): void {
        let hidden;
        try { hidden = JSON.parse(prefs.hiddenSources); } catch (e) { hidden = []; }
        hidden = hidden.filter(k => k !== key);
        if (!value) hidden.push(key);
        prefs.hiddenSources = JSON.stringify(hidden);
        prefs.setValue("hiddenSources", prefs.hiddenSources);
        prefs.sync();
    }
    function stamp(seconds: double): string {
        return seconds > 0 ? new Date(seconds * 1000).toLocaleString(SystemLanguage.timeLocale, SystemLanguage.timeLocale.dateTimeFormat(Locale.ShortFormat)) : qsTranslate("Flausen", "never");
    }
    function itemState(item: var): string {
        if (item.downloading) {
            const percent = item.bytesTotal > 0 ? Math.min(100, Math.floor(item.bytesDownloaded * 100 / item.bytesTotal)) + " %" : "";
            return qsTranslate("Flausen", "Downloading %1").arg(percent);
        }
        if (item.state === "update") return qsTranslate("Flausen", "Update available");
        if (item.state === "current") return qsTranslate("Flausen", "Up to date");
        if (item.state === "ahead") return qsTranslate("Flausen", "Newer than the published release");
        if (item.state === "local") return qsTranslate("Flausen", "No update queued");
        return qsTranslate("Flausen", "Version comparison unavailable");
    }
    function statusIcon(key: string): string {
        const value = status[key];
        if (root.checking) return "sync";
        if ((value?.pending?.length ?? 0) + (value?.addonPending ?? 0) > 0 || value?.downloading > 0) return "arrow_upward";
        if (root.error || !value || value.error || value.stale || !value.items?.length || value.items.some(item => item.state === "unknown")) return "question_mark";
        if (key === "wowup" && (!value.addonCheckedAt || Date.now() / 1000 - value.addonCheckedAt > 86400)) return "question_mark";
        return "check";
    }
    function summary(key: string): string {
        const value = status[key];
        if (!value) return qsTranslate("Flausen", "Not checked yet");
        if (value.error && !value.items?.length) return qsTranslate("Flausen", "Check failed · ") + qsTranslate("Flausen", value.error);
        if (value.installed === 0) return key === "steamGames" ? qsTranslate("Flausen", "No Steam games installed") : qsTranslate("Flausen", "Not installed");
        let label;
        const pending = value.pending?.length ?? 0;
        if (key === "steamGames") {
            label = value.downloading > 0 ? value.downloading + qsTranslate("Flausen", " active downloads") : pending > 0 ? pending + qsTranslate("Flausen", " updates queued") : value.installed + qsTranslate("Flausen", " titles · No updates queued");
        } else if (pending > 0) label = pending + qsTranslate("Flausen", " updates available");
        else if (value.items.some(item => item.state === "unknown")) label = qsTranslate("Flausen", "Some versions are unknown");
        else if (value.items.some(item => item.state === "ahead")) label = qsTranslate("Flausen", "Installed version newer than release");
        else label = value.items.length === 1 ? (key === "steam" ? "Build " : "Version ") + value.items[0].installedVersion + qsTranslate("Flausen", " · Up to date") : value.items.length + (key === "battlenetGames" ? qsTranslate("Flausen", " games up to date") : qsTranslate("Flausen", " apps up to date"));
        if (key === "wowup") label += " · " + value.addons.length + " addons, " + value.addonPending + qsTranslate("Flausen", " known updates");
        if (value.stale) label = (value.error ? qsTranslate("Flausen", "Offline · Last known status: ") : qsTranslate("Flausen", "Outdated check: ")) + label;
        return label;
    }
    function details(key: string): string {
        const value = status[key];
        if (!value) return qsTranslate("Flausen", "The first check runs when the shell starts.");
        const lines = (value.items ?? []).map(item => {
            let line = item.name + ": " + (item.installedVersion || "unknown");
            if (item.latestVersion && item.latestVersion !== item.installedVersion) line += " → " + item.latestVersion;
            line += " · " + root.itemState(item);
            if (item.policy) line += " · " + qsTranslate("Flausen", item.policy);
            if (item.detail) line += "\n" + qsTranslate("Flausen", item.detail);
            return line;
        });
        if (value.evidence) lines.push(qsTranslate("Flausen", value.evidence) + qsTranslate("Flausen", " · Checked ") + root.stamp(value.checkedAt));
        if (value.error) lines.push(qsTranslate("Flausen", "Online check failed: ") + qsTranslate("Flausen", value.error));
        if (key === "wowup" && value.addons) {
            lines.push(qsTranslate("Flausen", "Addon data from WowUp dated ") + root.stamp(value.addonCheckedAt) + ": " + value.addonPending + qsTranslate("Flausen", " known updates · ") + value.addonAutoUpdate + qsTranslate("Flausen", " with automatic updates"));
            value.addons.filter(item => item.state === "update").slice(0, 8).forEach(item => lines.push(item.name + ": " + item.installedVersion + " → " + item.latestVersion));
        }
        if (key === "artcraft" && value.feedTimestamp) lines.push(qsTranslate("Flausen", "ArtCraft feed dated ") + new Date(value.feedTimestamp).toLocaleString(SystemLanguage.timeLocale, SystemLanguage.timeLocale.dateTimeFormat(Locale.ShortFormat)));
        if (key === "artcraft" && value.autoUpdate !== undefined) lines.push(qsTranslate("Flausen", "Automatic suite updates: ") + (value.autoUpdate === null ? "unknown" : value.autoUpdate ? "on" : "off"));
        return lines.join("\n");
    }
    function compact(key: string): string {
        const value = status[key];
        let text = root.summary(key);
        if (value?.items?.length > 1 && key !== "steamGames") text += "\n" + value.items.map(item => item.name.replace("World of Warcraft · ", "WoW ") + " " + item.installedVersion + (item.state === "update" ? " → " + item.latestVersion : "")).join(" · ");
        if (value?.checkedAt) text += "\n" + (key === "steamGames" ? qsTranslate("Flausen", "Read locally ") : qsTranslate("Flausen", "Checked online ")) + root.stamp(value.checkedAt);
        if (key === "wowup" && value?.addonCheckedAt) text += qsTranslate("Flausen", "\nAddon status ") + root.stamp(value.addonCheckedAt);
        return text;
    }
    function open(source: var): void {
        if (source.url) Qt.openUrlExternally(source.url);
        else Launch.exec(["gtk-launch", source.desktop]);
    }
    function refresh(checkOnline) {
        if (probe.running) return;
        root.online = checkOnline !== false;
        probe.running = true;
    }
    Process {
        id: probe
        command: ["python3", Qt.resolvedUrl("update-hub-probe.py").toString().replace("file://", ""), ...(root.online ? [] : ["--local"])]
        stdout: StdioCollector {
            onStreamFinished: {
                try { root.status = JSON.parse(text); root.error = ""; root.lastCheck = Date.now(); }
                catch (e) { root.error = qsTranslate("Flausen", "Could not read the update check"); }
            }
        }
        onExited: code => { if (code !== 0) root.error = qsTranslate("Flausen", "Update check failed (") + code + ")"; }
    }
    IpcHandler {
        target: "updateHub"
        function inspect(): string {
            return JSON.stringify({status: root.status, error: root.error, checking: root.checking, lastCheck: root.lastCheck, enabled: root.sources.filter(s => root.enabled(s.key)).map(s => s.key)});
        }
    }
    Timer { interval: 20000; repeat: true; running: true; onTriggered: root.refresh(false) }
    Timer { interval: 1800000; repeat: true; running: true; triggeredOnStart: true; onTriggered: root.refresh() }
}
