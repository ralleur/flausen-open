// SPDX-License-Identifier: MIT
import QtQuick
import Quickshell
import org.kde.plasma.workspace.dbus as DBus
QtObject {
    id: root
    readonly property string userName: Quickshell.env("USER") || ""
    readonly property string displayName: account.properties.RealName || userName
    readonly property string iconFile: account.properties.IconFile || ""
    readonly property url source: iconFile.startsWith("/")
        ? "file://" + iconFile.split("/").map(encodeURIComponent).join("/") + "?revision=" + revision : ""
    property string accountPath: ""
    property int revision: 0
    property bool busy: false
    property string error: ""
    property DBus.Properties account: DBus.Properties {
        busType: DBus.BusType.System
        service: "org.freedesktop.Accounts"
        path: root.accountPath
        iface: "org.freedesktop.Accounts.User"
        onPropertiesChanged: root.revision++
    }
    function setPicture(selectedUrl: url): void {
        const uri = selectedUrl.toString();
        if (busy || !accountPath || !uri.startsWith("file:///")) return;
        error = "";
        busy = true;
        DBus.SystemBus.asyncCall({
            service: "org.freedesktop.Accounts", path: accountPath,
            iface: "org.freedesktop.Accounts.User", member: "SetIconFile",
            arguments: [decodeURIComponent(uri.slice(7))]
        }, reply => {
            root.busy = false;
            root.revision++;
            account.updateAll();
        }, failure => {
            root.busy = false;
            root.error = qsTranslate("Flausen", "Could not change the profile picture. ") + (failure.message || qsTranslate("Flausen", "Please try again."));
        });
    }
    Component.onCompleted: {
        DBus.SystemBus.asyncCall({
            service: "org.freedesktop.Accounts", path: "/org/freedesktop/Accounts",
            iface: "org.freedesktop.Accounts", member: "FindUserByName",
            arguments: [userName]
        }, reply => { root.accountPath = String(reply.value); }, failure => {});
    }
}
