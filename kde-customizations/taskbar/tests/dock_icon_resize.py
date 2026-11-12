#!/usr/bin/env python3
"""Exercise the real DockIcon in Quickshell without changing the desktop.

Requires the installed Caelestia icon normalizer. Checks
that resizing never reloads a ready texture, both normalized and fallback.
"""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

source = Path(__file__).resolve().parents[1] / 'icon-normalization/DockIcon.qml'
installed = Path.home() / '.config/quickshell/caelestia'
with tempfile.TemporaryDirectory(prefix='dock-icon-resize-') as directory:
    root = Path(directory)
    images = root / 'components/images'
    images.mkdir(parents=True)
    shutil.copy2(source, images / source.name)
    (root / 'scripts').symlink_to(installed / 'scripts', target_is_directory=True)
    (root / 'shell.qml').write_text('''
import QtQuick
import Quickshell
import qs.components.images

Scope {
    id: test
    property bool armed: false
    property int step: 0
    property int passes: 0
    property int waits: 0
    function fail(reason: string): void {
        console.error("FAIL: " + reason);
        Qt.exit(1);
    }
    DockIcon {
        id: icon
        implicitSize: 46
        originalSource: "image://icon/org.kde.dolphin"
        onStatusChanged: {
            if (test.armed && status !== Image.Ready)
                test.fail("ready texture reloaded during resize");
        }
    }
    Timer {
        interval: 16
        running: true
        repeat: true
        onTriggered: {
            if (!test.armed) {
                if (++test.waits > 600) test.fail("icon did not load");
                if (icon.status !== Image.Ready || (icon.normalize && !icon.normalizedSource.toString())) return;
                test.armed = true;
            }
            // Sweep the complete dock icon range in both directions repeatedly.
            icon.implicitSize = 10 + Math.abs((test.step * 7) % 160 - 80);
            const texture = icon.children[0];
            if (texture.sourceSize.width !== 512 || texture.sourceSize.height !== 512)
                test.fail("decode resolution changed");
            if (!texture.smooth || !texture.mipmap)
                test.fail("minification filtering disabled");
            if (Math.abs(texture.width - icon.width) > 0.001 || Math.abs(texture.height - icon.height) > 0.001)
                test.fail("display size differs from layout");
            if (++test.step < 240) return;
            test.armed = false;
            test.step = 0;
            test.waits = 0;
            if (++test.passes === 1) {
                icon.normalize = false;
                return;
            }
            console.log("PASS: 480 resize frames, normalized and fallback, no texture reloads");
            Qt.quit();
        }
    }
}
''')
    result = subprocess.run(['quickshell', '-p', str(root), '--no-color'],
                            capture_output=True, text=True, timeout=30,
                            env={**os.environ, 'QT_QPA_PLATFORM': 'offscreen'})
    output = result.stdout + result.stderr
    print(output)
    if result.returncode or 'PASS: 480 resize frames' not in output or 'FAIL:' in output:
        raise SystemExit(1)
