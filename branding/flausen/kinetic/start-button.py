#!/usr/bin/env python3
"""Install/restore only the kinetic start-button symbol via Caelestia's logo setting."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil

HOME = Path.home()
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', HOME / '.config')) / 'caelestia/shell.json'
STATE = Path(os.environ.get('XDG_STATE_HOME', HOME / '.local/state')) / 'flausen-os/kinetic-start-button'
ASSET = Path(os.environ.get('XDG_DATA_HOME', HOME / '.local/share')) / 'flausen-os/kinetic/flausen-start-orange.svg'
SOURCE = Path(__file__).with_name('flausen-start-orange.svg')
RECORD = STATE / 'current.json'

def save(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.kinetic-new')
    temp.write_text(text)
    temp.replace(path)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    if CONFIG.is_symlink():
        raise SystemExit('Refusing to replace a symlinked configuration.')
    config = json.loads(CONFIG.read_text())
    if args.restore:
        record = json.loads(RECORD.read_text())
        if config.get('general', {}).get('logo') != str(ASSET):
            raise SystemExit('Logo changed since installation; leaving it untouched.')
        if record['hadLogo']:
            config.setdefault('general', {})['logo'] = record['logoBefore']
        else:
            config.get('general', {}).pop('logo', None)
        save(CONFIG, json.dumps(config, ensure_ascii=False, indent=4) + '\n')
        if ASSET.is_file() and not ASSET.is_symlink() and ASSET.read_bytes() == SOURCE.read_bytes():
            ASSET.unlink()
        RECORD.unlink()
        print('Previous start-button logo restored.')
        return
    if RECORD.exists():
        if config.get('general', {}).get('logo') != str(ASSET) or not ASSET.exists() or ASSET.read_bytes() != SOURCE.read_bytes():
            raise SystemExit('Existing installation changed; leaving it untouched.')
        print('Kinetic start-button logo already installed.')
        return
    if ASSET.exists():
        raise SystemExit('Unmanaged destination asset exists; leaving it untouched.')
    backup = STATE / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True)
    shutil.copy2(CONFIG, backup / 'shell.json')
    record = {'hadLogo': 'logo' in config.get('general', {}), 'logoBefore': config.get('general', {}).get('logo'), 'backup': str(backup)}
    ASSET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, ASSET)
    save(RECORD, json.dumps(record, indent=2) + '\n')
    config.setdefault('general', {})['logo'] = str(ASSET)
    save(CONFIG, json.dumps(config, ensure_ascii=False, indent=4) + '\n')
    print(f'Kinetic start-button logo installed. Backup: {backup}')

if __name__ == '__main__':
    main()
