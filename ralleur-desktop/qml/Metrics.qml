pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io

Singleton {
    id: root
    property real cpu: -1
    property real memory: -1
    property real disk: -1
    property bool available: false
    Process {
        id: sampler
        running: true
        command: ["python3", Theme.base + "/bin/metrics.py"]
        stdout: SplitParser {
            onRead: line => {
                try {
                    const data = JSON.parse(line);
                    root.cpu = data.cpu ?? -1;
                    root.memory = data.memory ?? -1;
                    root.disk = data.disk ?? -1;
                    root.available = true;
                } catch (e) {
                    console.warn("Metrics:", e);
                }
            }
        }
        onExited: {
            root.available = false;
            retry.restart();
        }
    }
    Timer {
        id: retry
        interval: 10000
        onTriggered: sampler.running = true
    }
}
