"""Exercise detection and the reboot sequence without touching firmware."""
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('windows_boot', Path(__file__).resolve().parents[1] / 'overlay/modules/launcher/windows-boot.py')
boot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boot)
GUID = '31eb1720-87e0-4d02-ba4d-90329951feda'
FIRMWARE = f'Boot0000* Windows Boot Manager\tHD(1,GPT,{GUID},0x800,0x32000)/\\EFI\\Microsoft\\Boot\\bootmgfw.efi'
DEVICES = [dict(partuuid=GUID, fstype='vfat', pkname='nvme0n1'), dict(fstype='ntfs', pkname='nvme0n1')]


class WindowsBootTest(unittest.TestCase):
    def test_detects_windows(self):
        self.assertEqual(boot.find_windows(FIRMWARE, DEVICES), '0000')

    def test_hides_without_windows_or_on_stale_firmware(self):
        for firmware, devices in [('', DEVICES), (FIRMWARE, []), (FIRMWARE, DEVICES[:1]),
                                  (FIRMWARE.replace('bootmgfw.efi', 'other.efi'), DEVICES),
                                  (FIRMWARE.replace('0000*', '0000 '), DEVICES),
                                  (FIRMWARE, [DEVICES[0], dict(fstype='ntfs', pkname='sda')])]:
            with self.subTest(firmware=firmware, devices=devices):
                self.assertIsNone(boot.find_windows(firmware, devices))

    def test_sets_only_next_boot_before_reboot(self):
        with patch.object(boot, 'run') as run:
            boot.reboot_windows('0000', FIRMWARE)
            self.assertEqual([c.args[0] for c in run.call_args_list], [
                ['/usr/bin/efibootmgr', '--bootnext', '0000'], ['/usr/bin/systemctl', 'reboot']])

    def test_does_not_reboot_when_setting_bootnext_fails(self):
        with patch.object(boot, 'run', side_effect=subprocess.CalledProcessError(1, 'efibootmgr')) as run:
            with self.assertRaises(subprocess.CalledProcessError):
                boot.reboot_windows('0000', FIRMWARE)
            self.assertEqual(run.call_count, 1)

    def test_failed_reboot_restores_previous_bootnext(self):
        for firmware, expected in [(FIRMWARE, ['--delete-bootnext']),
                                   ('BootNext: 0002\n' + FIRMWARE, ['--bootnext', '0002'])]:
            with patch.object(boot, 'run', side_effect=['', subprocess.CalledProcessError(1, 'systemctl'), '']) as run:
                with self.assertRaises(subprocess.CalledProcessError):
                    boot.reboot_windows('0000', firmware)
                self.assertEqual(run.call_args.args[0], ['/usr/bin/efibootmgr'] + expected)


if __name__ == '__main__':
    unittest.main()
