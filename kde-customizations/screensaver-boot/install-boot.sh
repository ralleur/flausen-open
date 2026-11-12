#!/bin/bash
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Run with pkexec or sudo.' >&2; exit 1; }
base=$(cd -- "$(dirname -- "$0")" && pwd)
backup=/var/lib/ralleur-boot-backup
[[ ! -e /usr/share/plymouth/themes/ralleur ]] || { echo 'Theme already exists; refusing to overwrite.' >&2; exit 1; }
[[ ! -e "$backup" ]] || { echo 'Backup already exists; refusing to overwrite.' >&2; exit 1; }
install -d -m 700 "$backup"
cp -a /etc/plymouth/plymouthd.conf "$backup/plymouthd.conf"
cp -a /boot/initramfs-*.img "$backup/"
systemd-analyze > "$backup/boot-before.txt"
rollback() {
    echo 'Build failed: restoring original theme and initramfs.' >&2
    cp -a "$backup/plymouthd.conf" /etc/plymouth/plymouthd.conf
    cp -a "$backup"/initramfs-*.img /boot/
    rm -rf /usr/share/plymouth/themes/ralleur
}
trap rollback ERR
install -d -m 755 /usr/share/plymouth/themes/ralleur
install -m 644 "$base"/plymouth/* /usr/share/plymouth/themes/ralleur/
plymouth-set-default-theme ralleur
mkinitcpio -P
# Verify that the selected animation and the existing unlock integration are included.
for img in /boot/initramfs-*.img; do
    listing=$(lsinitcpio "$img")
    [[ $listing == *usr/share/plymouth/themes/ralleur/ralleur.script* ]]
    [[ $listing == *systemd-ask-password-plymouth* ]]
    [[ $listing == *systemd-cryptsetup* ]]
done
trap - ERR
printf 'SUCCESS: ralleur theme installed; initramfs verified. Backup: %s\n' "$backup"
