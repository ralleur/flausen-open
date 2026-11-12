#!/usr/bin/env python3
"""Exercise installed Dock launch helpers in the actual QML JavaScript engine."""
from pathlib import Path
import os
import subprocess
import tempfile

source = (Path.home() / '.config/quickshell/caelestia/modules/bar/components/Dock.qml').read_text()

def method(name):
    start = source.index('    function ' + name + '(')
    end = source.index('\n    }', start) + len('\n    }')
    return source[start:end]

qml = '''import QtQuick
import Quickshell
ShellRoot {
    property var launchingApps: ({})
    readonly property int launchTimeoutMs: 15000
'''
qml += '\n'.join(method(n) for n in ('launchKey', 'markLaunching', 'clearFinishedLaunches'))
qml += '''
    function check(ok, message) {
        if (!ok) throw new Error(message);
    }
    Component.onCompleted: {
        try {
            const starter = { id: "flausen-spotify", entry: {id: "flausen-spotify"}, appClass: "flausen-spotify", toplevels: [] };
            const window = { id: "chrome-open.spotify.com__-Default#42", entry: starter.entry, appClass: "chrome-open.spotify.com__-Default", toplevels: [{}] };
            check(launchKey(starter) === launchKey(window), "identity across window class / ungrouped id");
            markLaunching(starter);
            check(launchingApps[launchKey(starter)] > 0, "start timestamp");
            launchingApps = {"flausen-spotify": 1000, discord: 2000};
            clearFinishedLaunches([window], 3000);
            check(!launchingApps["flausen-spotify"] && launchingApps.discord === 2000, "window clears only its launch");
            clearFinishedLaunches([], 16999);
            check(launchingApps.discord === 2000, "pending before deadline");
            clearFinishedLaunches([], 17000);
            check(Object.keys(launchingApps).length === 0, "failed launch expires at deadline");
            console.log("PASS: Dock launch identity, completion, independent apps and timeout");
        } catch (error) {
            console.error("FAIL: " + error);
        }

    }
}
'''
with tempfile.TemporaryDirectory(prefix='dock-launch-test-') as tmp:
    path = Path(tmp) / 'shell.qml'
    path.write_text(qml)
    process = subprocess.Popen(['quickshell', '-p', str(path), '--no-color'],
                               env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen'},
                               text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        output, _ = process.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        process.terminate()
        output, _ = process.communicate(timeout=5)
    print(output)
    assert 'PASS: Dock launch' in output and 'FAIL:' not in output
