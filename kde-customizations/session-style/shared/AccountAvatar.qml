// SPDX-License-Identifier: MIT
import QtQuick
import org.kde.plasma.workspace.dbus as DBus

QtObject {
    id: root
    property string userName: ""
    property string accountPath: ""
    property int requestId: 0
    readonly property string iconFile: account.properties.IconFile || ""
    readonly property string source: iconFile.startsWith("/")
        ? "file://" + iconFile.split("/").map(encodeURIComponent).join("/") : ""

    // AccountsService is also used by the OS user settings. Home-directory
    // .face files alone do not reflect the configured system profile picture.
    property DBus.Properties account: DBus.Properties {
        busType: DBus.BusType.System
        service: "org.freedesktop.Accounts"
        path: root.accountPath
        iface: "org.freedesktop.Accounts.User"
    }

    function resolveAccount() {
        const request = ++requestId;
        accountPath = "";
        if (!userName) return;
        DBus.SystemBus.asyncCall({
            service: "org.freedesktop.Accounts",
            path: "/org/freedesktop/Accounts",
            iface: "org.freedesktop.Accounts",
            member: "FindUserByName",
            arguments: [userName],
        }, reply => {
            if (request === requestId) accountPath = String(reply.value);
        }, error => {
            // Keep the native model's avatar/icon when no account is available.
        });
    }

    onUserNameChanged: resolveAccount()
    Component.onCompleted: resolveAccount()
}
