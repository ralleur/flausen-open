#!/usr/bin/env python3
"""Keep the wallpaper below Krohnkite's keep-below tiled windows."""
import datetime
from pathlib import Path
import shutil


def main():
    target = (Path.home() / '.config/quickshell/caelestia/modules/background/Background.qml')
    text = target.read_text()
    old = 'WlrLayershell.layer: WlrLayer.Bottom'
    new = 'WlrLayershell.layer: WlrLayer.Background'
    if new in text and old not in text:
        print('Desktop already uses the background layer.')
        return
    if text.count(old) != 1:
        raise SystemExit('Desktop layer declaration changed; review before applying.')
    backup = (Path.home() / '.local/state/ralleur-tiling' /
              ('before-desktop-layer-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')))
    backup.mkdir(parents=True)
    shutil.copy2(target, backup / 'Background.qml')
    target.write_text(text.replace(old, new))
    print('Desktop layer corrected; backup: ' + str(backup))


if __name__ == '__main__':
    main()
