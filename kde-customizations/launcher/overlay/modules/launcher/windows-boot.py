#!/usr/bin/env python3
"""Detect a local Windows UEFI target and request a one-shot reboot into it."""
import argparse
import json
import os
import re
import subprocess
import sys


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=15).stdout


def find_windows(firmware, devices):
    """Reject generic NTFS disks and stale entries for absent EFI partitions."""
    for line in firmware.splitlines():
        match = re.match(r'Boot([0-9A-Fa-f]{4})\*\s+.*?HD\(\d+,GPT,([0-9A-Fa-f-]{36}),', line)
        if not match or not re.search(r'\\EFI\\Microsoft\\Boot\\bootmgfw\.efi', line, re.I):
            continue
        esp = next((d for d in devices if (d.get('partuuid') or '').lower() == match[2].lower()
                    and d.get('fstype') == 'vfat'), None)
        if esp and esp.get('pkname') and any(d.get('pkname') == esp['pkname']
                                                and d.get('fstype') in ('ntfs', 'BitLocker') for d in devices):
            return match[1].upper()
    return None


def detect():
    firmware = run(['/usr/bin/efibootmgr', '-v'])
    devices = json.loads(run(['/usr/bin/lsblk', '--json', '--list', '--output', 'PATH,FSTYPE,PARTUUID,PKNAME']))['blockdevices']
    return find_windows(firmware, devices), firmware


def reboot_windows(entry, firmware):
    previous = re.search(r'^BootNext: ([0-9A-Fa-f]{4})$', firmware, re.M)
    run(['/usr/bin/efibootmgr', '--bootnext', entry])
    try:
        run(['/usr/bin/systemctl', 'reboot'])
    except (OSError, subprocess.SubprocessError):
        # A blocked reboot must not silently redirect a later normal restart.
        run(['/usr/bin/efibootmgr', '--bootnext', previous[1]] if previous else
            ['/usr/bin/efibootmgr', '--delete-bootnext'])
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reboot', action='store_true')
    args = parser.parse_args()
    try:
        entry, firmware = detect()
        if not args.reboot:
            print(json.dumps({'available': entry is not None}))
            return 0
        if os.geteuid() != 0:
            raise RuntimeError('Die Windows-Neustartaktion benötigt die Systemfreigabe.')
        if entry is None:
            raise RuntimeError('Kein lokaler Windows-Bootmanager mit Windows-Partition gefunden.')
        reboot_windows(entry, firmware)
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        if not args.reboot:
            print(json.dumps({'available': False}))
        else:
            print(f'Windows-Neustart fehlgeschlagen: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
