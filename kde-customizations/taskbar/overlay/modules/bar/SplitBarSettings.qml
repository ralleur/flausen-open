pragma Singleton

import QtQuick
import QtCore
import Caelestia.Config

Settings {
    id: root

    category: "RalleurTaskbar"
    readonly property int edgeGap: 12
    readonly property real minDockScale: 0.4
    readonly property real maxDockScale: 3.2
    property bool taskbarUnlocked: false
    function setTaskbarUnlocked(value: bool): void {
        taskbarUnlocked = value;
        setValue("taskbarUnlocked", value);
        sync();
    }
    property real dockScale: -1
    property bool dockMagnification: true
    property real dockMagnificationAmount: 0.55

    function setMagnification(enabled: bool): void {
        dockMagnification = enabled;
        setValue("dockMagnification", enabled);
        sync();
    }
    function setMagnificationAmount(value: real): void {
        if (!isFinite(value)) return;
        dockMagnificationAmount = Math.max(0.15, Math.min(0.9, value));
        setValue("dockMagnificationAmount", dockMagnificationAmount);
        sync();
    }
    // Only launchable desktop IDs are retained; windows and process IDs are not stored.
    property string recentDockApps: "[]"

    function recentApps(): var {
        try {
            const apps = JSON.parse(recentDockApps);
            return Array.isArray(apps) ? apps.filter(id => typeof id === "string").slice(0, 3) : [];
        } catch (error) {
            return [];
        }
    }

    function saveRecentApps(apps: var): void {
        const value = JSON.stringify(apps.slice(0, 3));
        if (value === recentDockApps)
            return;
        recentDockApps = value;
        setValue("recentDockApps", value);
        sync();
    }

    function setDockScale(value: real): void {
        if (!isFinite(value))
            return;
        dockScale = Math.max(minDockScale, Math.min(maxDockScale, value));
        setValue("dockScale", dockScale);
        sync();
    }

    Component.onCompleted: {
        // Copy the previous common scale once. Subsequent topbar edits are independent.
        if (!isFinite(dockScale) || dockScale < minDockScale || dockScale > maxDockScale)
            setDockScale(GlobalConfig.bar.scale);
    }
}
