#!/usr/bin/env python3
"""Move the live traffic card from the dashboard to the network popover."""
from datetime import datetime, timezone
from pathlib import Path
import difflib
import shutil

SOURCE = Path(__file__).resolve().parent
SHELL = Path.home() / '.config/quickshell/caelestia'


def install():
    name = 'modules/dashboard/Performance.qml'
    dashboard = (SHELL / name).read_text()
    start = dashboard.find('                WrappedLoader {\n                    id: networkCard\n')
    if start >= 0:
        end = dashboard.index('                WrappedLoader {\n                    id: memoryCard', start)
        dashboard = dashboard[:start] + dashboard[end:]
        dashboard = dashboard.replace(' || networkCard.active', '')
    elif 'id: networkCard' in dashboard:
        raise SystemExit('Unerwarteter Aufbau der Dashboard-Netzwerkkarte')
    # The empty-state calculation must follow the cards still displayed here.
    dashboard = dashboard.replace(' && !Config.dashboard.performance.showNetwork', '')
    files = {name: dashboard, 'modules/bar/popouts/Network.qml': (SOURCE / 'Network.qml').read_text()}
    changed = {name: text for name, text in files.items() if (SHELL / name).read_text() != text}
    if not changed:
        print('Live-Netzwerkkarte ist bereits verschoben.')
        return
    backup = Path.home() / '.local/state/ralleur-taskbar-backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-network-traffic')
    patch = []
    for name, text in changed.items():
        target = SHELL / name
        saved = backup / name
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
        patch.extend(difflib.unified_diff(target.read_text().splitlines(True), text.splitlines(True), fromfile=name, tofile=name))
    for name, text in changed.items():
        (SHELL / name).write_text(text)
    (SOURCE.parent / 'network-traffic.patch').write_text(''.join(patch))
    (SOURCE.parent / 'evidence/network-traffic-backup.txt').write_text(str(backup) + '\n')
    print(backup)


if __name__ == '__main__':
    install()
