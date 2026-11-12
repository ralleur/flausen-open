pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io
import Caelestia

Singleton {
    id: root
    property string language: resolve("", "")
    property string formatLocale: Qt.locale().name
    property string timeFormatLocale: formatLocale
    property string numberFormatLocale: formatLocale
    readonly property var locale: Qt.locale(numberFormatLocale)
    readonly property var timeLocale: Qt.locale(timeFormatLocale)

    function resolve(preference: string, formats: string): string {
        const fallback = Quickshell.env("LANGUAGE") || Quickshell.env("LC_ALL") || Quickshell.env("LC_MESSAGES") || Quickshell.env("LANG") || "en";
        const supported = Translations.available.map(entry => entry.code);
        for (const candidate of (preference || formats || fallback).split(":")) {
            const code = candidate.split(".")[0].split("@")[0].replace(/-/g, "_");
            if (code === "C" || code === "POSIX") return "en";
            if (supported.includes(code)) return code;
            if (supported.includes(code.split("_")[0])) return code.split("_")[0];
        }
        return "en";
    }
    function load(contents: string): void {
        let section = "", preference = "", formats = "", time = "", numbers = "";
        for (const raw of contents.split("\n")) {
            const line = raw.trim();
            if (line.startsWith("[")) section = line;
            else if (section === "[Translations]" && line.startsWith("LANGUAGE=")) preference = line.slice(9).trim();
            else if (section === "[Formats]" && line.startsWith("LANG=")) formats = line.slice(5).trim();
            else if (section === "[Formats]" && line.startsWith("LC_TIME=")) time = line.slice(8).trim();
            else if (section === "[Formats]" && line.startsWith("LC_NUMERIC=")) numbers = line.slice(11).trim();
        }
        language = resolve(preference, formats);
        formatLocale = formats ? formats.split(".")[0] : Qt.locale().name;
        timeFormatLocale = time ? time.split(".")[0] : formatLocale;
        numberFormatLocale = numbers ? numbers.split(".")[0] : formatLocale;
    }
    IpcHandler {
        target: "localization"
        function inspect(): string {
            return JSON.stringify({system: root.language, requested: Translations.language, active: Translations.activeLanguage, formats: root.formatLocale});
        }
    }
    FileView {
        path: (Quickshell.env("XDG_CONFIG_HOME") || Quickshell.env("HOME") + "/.config") + "/plasma-localerc"
        watchChanges: true
        onFileChanged: reload()
        onLoaded: root.load(text())
        onLoadFailed: root.load("")
    }
}
