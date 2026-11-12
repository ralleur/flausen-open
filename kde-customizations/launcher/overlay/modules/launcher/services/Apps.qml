pragma Singleton

import QtQuick
import QtCore
import Quickshell
import Caelestia
import Caelestia.Models
import Caelestia.Config
import qs.services
import qs.utils

Searcher {
    id: root

    property alias alphaApps: appDb.alphaApps

    Settings {
        id: recentSettings
        category: "RalleurStartMenu"
        property string recentAppIdsJson: "[]"
    }
    readonly property var recentAppIds: {
        try {
            const ids = JSON.parse(recentSettings.recentAppIdsJson);
            return Array.isArray(ids) ? ids.filter(id => typeof id === "string") : [];
        } catch (error) { return []; }
    }
    readonly property var recentApps: {
        const available = root.allApps();
        return recentAppIds.map(id => available.find(app => app.id === id)).filter(app => app);
    }
    property var knownWindowAddresses: []
    property bool windowsInitialized: false

    function rememberRecent(entry: var): void {
        if (!entry || !entry.id || root.recentAppIds[0] === entry.id)
            return;
        recentSettings.recentAppIdsJson = JSON.stringify([entry.id, ...root.recentAppIds.filter(id => id !== entry.id)].slice(0, 48));
    }
    function entryForWindow(window: var): var {
        const appClass = window?.class ?? "";
        if (!appClass) return null;
        const normalise = value => String(value || "").toLowerCase().replace(/\.desktop$/, "");
        const match = DesktopEntries.heuristicLookup(appClass);
        const all = root.allApps();
        const id = normalise(match?.id ?? appClass);
        return all.find(app => normalise(app.id) === id)
            ?? all.find(app => normalise(app.startupClass) === normalise(appClass)) ?? null;
    }
    function rememberActiveWindow(): void {
        root.rememberRecent(root.entryForWindow(Kwin.activeWindow));
    }
    function trackWindows(): void {
        const windows = Kwin.windowList;
        const initial = !root.windowsInitialized;
        if (root.windowsInitialized) {
            for (const window of windows) {
                if (!root.knownWindowAddresses.includes(window.address))
                    root.rememberRecent(root.entryForWindow(window));
            }
        }
        root.knownWindowAddresses = windows.map(window => window.address);
        root.windowsInitialized = true;
        if (initial) root.rememberActiveWindow();
    }
    Component.onCompleted: Qt.callLater(root.trackWindows)
    Connections {
        target: Kwin
        function onActiveWindowChanged(): void { root.rememberActiveWindow(); }
        function onWindowListChanged(): void { root.trackWindows(); }
    }
    Connections {
        target: appDb
        function onAppsChanged(): void { if (root.recentAppIds.length === 0) root.rememberActiveWindow(); }
    }

    function launch(entry: DesktopEntry): void {
        root.rememberRecent(entry);
        appDb.incrementFrequency(entry.id);
        Launch.launchEntry(entry);
    }

    /// Every visible desktop entry in AppDb order (favourites, then frequency, then name).
    function allApps(): list<var> {
        const res = [];
        const apps = list;
        for (let i = 0; i < apps.length; i++) {
            if (apps[i]?.entry)
                res.push(apps[i].entry);
        }
        return res;
    }

    function search(search: string): list<var> {
        const prefix = GlobalConfig.launcher.specialPrefix;

        if (search.startsWith(`${prefix}i `)) {
            keys = ["id", "name"];
            weights = [0.9, 0.1];
        } else if (search.startsWith(`${prefix}c `)) {
            keys = ["categories", "name"];
            weights = [0.9, 0.1];
        } else if (search.startsWith(`${prefix}d `)) {
            keys = ["comment", "name"];
            weights = [0.9, 0.1];
        } else if (search.startsWith(`${prefix}e `)) {
            keys = ["execString", "name"];
            weights = [0.9, 0.1];
        } else if (search.startsWith(`${prefix}w `)) {
            keys = ["startupClass", "name"];
            weights = [0.9, 0.1];
        } else if (search.startsWith(`${prefix}g `)) {
            keys = ["genericName", "name"];
            weights = [0.9, 0.1];
        } else if (search.startsWith(`${prefix}k `)) {
            keys = ["keywords", "name"];
            weights = [0.9, 0.1];
        } else {
            keys = ["name"];
            weights = [1];

            if (!search.startsWith(`${prefix}t `))
                return query(search).map(e => e.entry);
        }

        const results = query(search.slice(prefix.length + 2)).map(e => e.entry);
        if (search.startsWith(`${prefix}t `))
            return results.filter(a => a.runInTerminal);
        return results;
    }

    function selector(item: var): string {
        return keys.map(k => item[k]).join(" ");
    }

    list: appDb.apps.filter(a => a && !Strings.testRegexList(GlobalConfig.launcher.hiddenApps, a.id))
    useFuzzy: GlobalConfig.launcher.useFuzzy.apps

    AppDb {
        id: appDb

        path: `${Paths.state}/apps.sqlite`
        favouriteApps: GlobalConfig.launcher.favouriteApps
        entries: DesktopEntries.applications.values
    }
}
