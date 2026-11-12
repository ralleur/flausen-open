pragma Singleton

import QtQuick
import Quickshell
import Quickshell.Io
import Caelestia.Config
import qs.services

Singleton {
    id: root

    property var apps: []
    readonly property bool split: apps.length >= 2
    property int users: 0
    property bool retryReady: true

    // Use the same assignment as the desktop spectrum, including solo orange.
    function colorForApp(name: string): color {
        const app = apps.find(app => app.name === name);
        return app ? (split ? app.color : "#E56D2F") : Colours.palette.m3onSurfaceVariant;
    }

    IpcHandler {
        target: "ralleurAppVisualiser"
        function inspect(): string {
            return JSON.stringify({split: root.split, users: root.users,
                apps: root.apps.map(app => ({name: app.name, color: app.color, peak: Math.max(0, ...app.values)}))});
        }
    }

    Process {
        id: reader
        command: ["python3", decodeURIComponent(Qt.resolvedUrl("../scripts/app-visualiser.py").toString().replace("file://", ""))]
        running: root.users > 0 && root.retryReady
        stdout: SplitParser {
            onRead: line => {
                try {
                    const frame = JSON.parse(line);
                    root.apps = frame.apps ?? [];
                } catch (error) {
                    root.apps = [];
                }
            }
        }
        onExited: {
            root.apps = [];
            if (root.users > 0) {
                root.retryReady = false;
                restart.start();
            }
        }
    }
    Timer {
        id: restart
        interval: 3000
        onTriggered: root.retryReady = true
    }
}
