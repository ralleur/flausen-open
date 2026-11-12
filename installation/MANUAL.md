# Manual setup

**4 November 2026 · manual development preview**.
This guide is for people comfortable comparing KDE configuration, reading CMake
errors and recovering a session from a TTY. The flausen installer is still being
developed. The aim is an approachable everyday desktop; setting up this preview
still involves terminal commands.

## Requirements and scope

The reference is the running CachyOS development machine: Plasma/KWin **6.8.2**,
Dolphin **26.08.2**, Qt **6.12.0**, Quickshell **0.3.2**, KF6 **6.31.0** and
Darkly **0.5.42**, on Wayland. These are observed versions, not a tested minimum
version matrix. A complete clean installation on another machine has not yet
been validated. Use a separate test account or a recoverable system first.

You need:

- KDE Plasma 6 on Wayland with a working graphical session.
- Git, Python 3.11+, GNU `patch`, CMake, Ninja, a C/C++ compiler and `pkg-config`.
- The runtime and build dependencies of the pinned **Caelestia-KDE port** below,
  including its native QML modules.
- Qt6 Quick/QML/DBus/Widgets/Concurrent/Test, Multimedia/Pdf and LinguistTools
  for translations; KF6 KCMUtilsQuick, CoreAddons, I18n, WindowSystem, Config,
  KIOFileWidgets, XmlGui and IconThemes for the additional components.
- NetworkManager and PipeWire/WirePlumber for the corresponding controls;
  individual component READMEs list further tools.

Package names differ between distributions. This list names libraries; there is
no verified common flausen package list yet. Native shell and KWin extensions must
match your installed Qt/KF6/KWin ABI. Build them locally rather than copying `.so`
files from the development machine.

Source assembly covers the topbar/dock, start menu, popovers, settings QML,
desktop context menu and shared controls. The following steps cover native modules,
user configuration, services and standalone apps. Games, personal app shortcuts,
accounts and AI models are separate.

## 1. Get the repository and pinned base

The repository is private. Your GitHub account needs access and a registered SSH
key. You can alternatively use GitHub HTTPS with your own authentication.

```sh
git clone git@github.com:ralleur/flausen.git
cd flausen
export FLAUSEN_REPO="$PWD"
./bin/flausen check
python3 -m unittest discover -s tests -v
mkdir -p .cache/manual

git clone --recurse-submodules https://github.com/ladybug-me/caelestia-kde.git .cache/manual/caelestia-kde
git -C .cache/manual/caelestia-kde checkout --detach c0cfd04d5b9da3fbf7b5f47016822888468e9829
git -C .cache/manual/caelestia-kde submodule update --init --recursive
```

[`shell-lock.json`](shell-lock.json) records the base. The latest Caelestia `main`
is not automatically compatible, and the original Hyprland upstream is not a
substitute for the KDE port.

Set up **this Caelestia-KDE base first**. Read the README and scripts at the checked
out revision. Its setup entry point is:

```sh
cd "$FLAUSEN_REPO/.cache/manual/caelestia-kde"
bash scripts/setup.sh
cd "$FLAUSEN_REPO"
```

This is the **upstream installer**, with its own prompts, downloads, package
installation and KDE configuration changes. Follow its documentation for choices
and recovery. Calling the setup script directly avoids the `install.sh`
bootstrapper, which can update an existing checkout. Dependencies that upstream
itself downloads are not all reproducibly pinned by this procedure.

Log in again if necessary and check the base before applying flausen:

```sh
systemctl --user status caelestia-shell.service
journalctl --user -u caelestia-shell.service -b -n 60 --no-pager
```

This manual path expects `~/.config/quickshell/caelestia`,
`~/.config/caelestia/shell.json`, `~/.local/lib/qt6/qml` and `~/.local/bin`.
For a different packaged upstream layout, reconcile paths and the QML import
environment first.

## 2. Assemble the current shell sources

```sh
cd "$FLAUSEN_REPO"
python3 installation/prepare-shell.py \
  --upstream .cache/manual/caelestia-kde \
  --output .cache/manual/flausen-shell
```

The tool reads committed Git objects from the pinned base, references 225 existing
component files, applies the remaining integration patch and verifies hashes for
all 284 modified files. It writes only to a **new** output directory and refuses
an existing destination. Changed source hashes need to be reconciled in the
manifest first.

It excludes `shell.json`, Qt user settings, `context_menu.json`, chat histories,
tokens, updater metadata, local backups and compiled native modules. Icons and
base files installed by upstream remain in place when the prepared sources are
copied over them. Do **not** reapply the historical individual patches under
`kde-customizations/` on top of this assembled state.

## 3. Build native settings and the dock helper

The shell imports `Flausen.Settings`. Build it before the first start:

```sh
cmake -S kde-customizations/settings/native -B .cache/manual/settings \
  -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build .cache/manual/settings -j 4

c++ -std=c++17 -O2 -fPIC \
  kde-customizations/taskbar/icon-normalization/normalize.cpp \
  -o .cache/manual/normalize-dock-icon \
  $(pkg-config --cflags --libs Qt6Gui Qt6Core)
```

These copy commands are for an initial setup in a test account. Back up and compare
any existing files at the destinations before continuing.

```sh
mkdir -p "$HOME/.local/lib/qt6/qml/Flausen/Settings"
cp .cache/manual/settings/Flausen/Settings/{qmldir,flausensettings.qmltypes,libflausensettings.so,libflausensettingsplugin.so} \
  "$HOME/.local/lib/qt6/qml/Flausen/Settings/"
install -m755 .cache/manual/normalize-dock-icon .cache/manual/flausen-shell/scripts/normalize-dock-icon
```

The Caelestia start command must include `~/.local/lib/qt6/qml` in its QML import
path. Check `~/.local/bin/caelestia-autostart.sh`. The
[settings component](../kde-customizations/settings/README.md) describes the native
integration. Do not additionally run its historical full installer over this
shell assembly: that installer expects a different intermediate state.

## 4. Back up and activate the shell

Finish open file operations. Back up the base **before** copying the shell, and
keep the printed backup path for recovery:

```sh
export FLAUSEN_BACKUP="$HOME/.local/state/flausen/manual-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$FLAUSEN_BACKUP"
systemctl --user stop caelestia-shell.service
cp -a "$HOME/.config/quickshell/caelestia" "$FLAUSEN_BACKUP/shell"
cp -a "$HOME/.config/caelestia" "$FLAUSEN_BACKUP/config"
# Also back up ~/.config/Caelestia and any existing Flausen modules, if present.
printf '%s\n' "$FLAUSEN_BACKUP"
cp -a .cache/manual/flausen-shell/. "$HOME/.config/quickshell/caelestia/"
```

Edit your existing `~/.config/caelestia/shell.json`: **merge changes**, rather than
replacing it with somebody else's complete configuration. Set `bar.position` to
`"top"`, `bar.persistent` to `true`, `osd.enableMicrophone` to `true`, and
`general.language` to `"system"`. Check that `bar.entries` places the dock in
`"middle"`, the logo/workspaces on the left and status icons/clock on the right.
Preserve other upstream-generated keys. Pin your own applications.

Do not indiscriminately copy global KWin blur values from older work logs. Shared
material values live in `MenuStyle`; the current shell provides its geometry and
typography.

Install branding and the small settings launcher:

```sh
python3 branding/flausen/install.py
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/flausen-settings"
cp kde-customizations/settings/helpers/{hermes_settings.py,openai_auth.py} \
  "$HOME/.local/share/flausen-settings/"
cat > "$HOME/.local/bin/flausen-settings" <<'SH'
#!/bin/sh
exec /usr/bin/quickshell ipc -p "$HOME/.config/quickshell/caelestia" call nexus open
SH
chmod 755 "$HOME/.local/bin/flausen-settings"
```

Ensure `~/.local/bin` is in the session PATH. Open settings from the start menu or
by running `flausen-settings`.

```sh
python3 kde-customizations/localization/install.py
systemctl --user start caelestia-shell.service
journalctl --user -u caelestia-shell.service -b -n 80 --no-pager
```

Localization rebuilds the German catalogue with Qt Linguist tools and follows
the KDE system language. English remains the source language and fallback.
Missing `Flausen.Settings` or `Caelestia` imports indicate a build or import-path
problem; restarting the shell again will not fix those paths.

## 5. Files and additional components

The shell does not install the standalone extensions. Set up each component
separately and check its result. Component READMEs contain the detailed development
and recovery notes; some historical notes are still in German.

| Component | Setup / limits |
| --- | --- |
| Files / Dolphin | [Build and installer](../kde-customizations/dolphin-header/README.md#bauen-und-installieren); includes sources and tests |
| File dialogs / ZIP extraction | [Files integration](../kde-customizations/files/README.md), after the Dolphin plugin |
| Task Manager | `python3 kde-customizations/task-manager/install.py --dry-run`, then without `--dry-run`; reuses shared shell sources |
| Window controls / Darkly | [Versioned Darkly build](../kde-customizations/window-controls/README.md), followed by the [Qt dialog style](../kde-customizations/dialogs/README.md) |
| Optional tiling | [Krohnkite and native KWin helpers](../kde-customizations/tiling/README.md); build against your exact KWin version |
| Fullscreen workspace routing | [Fullscreen workspaces](../kde-customizations/fullscreen-desktops/README.md) |
| Start menu / Files background blur | [Launcher backdrop](../kde-customizations/launcher/README.md#wiederhergestellt-bildschirmfüllender-hintergrund-blur), with setup below |
| Wallpapers | [flausen wallpapers](../kde-customizations/wallpapers/flausen/README.md) and [picker](../kde-customizations/wallpapers/set-picker/README.md) |
| Lock screen / login | [Session style](../kde-customizations/session-style/README.md); optional and version-specific; change the login manager last |
| Other customizations | [Catalogue](components.json) and each component README; do not blindly run every installer |

Example Files build, from the repository root:

```sh
python3 kde-customizations/dolphin-header/generate_icons.py
cmake -S kde-customizations/dolphin-header -B .cache/manual/dolphin \
  -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build .cache/manual/dolphin -j 4
ctest --test-dir .cache/manual/dolphin --output-on-failure
python3 kde-customizations/dolphin-header/install.py --build .cache/manual/dolphin
```

Close existing Dolphin windows normally and reopen Files. Replace the historical
`/home/USER/ralleurOS` prefix in older component examples with `$FLAUSEN_REPO`.
Historical backup paths document the development machine; use the paths printed
by **your own** installer runs.

The shared fullscreen background blur also requires `backdrop/build-blur-settings.sh`,
the helper under `~/.config/quickshell/ralleur-start-backdrop/`, and its user service
and KWin effect from the launcher component. For an initial setup, after backing
up any existing files with those names:

```sh
bash kde-customizations/launcher/backdrop/build-blur-settings.sh
mkdir -p "$HOME/.config/quickshell/ralleur-start-backdrop" \
  "$HOME/.local/share/kwin/effects/ralleur-start-backdrop" \
  "$HOME/.config/systemd/user/caelestia-shell.service.d"
cp kde-customizations/launcher/backdrop/helper/* "$HOME/.config/quickshell/ralleur-start-backdrop/"
cp kde-customizations/launcher/backdrop/ralleur-start-backdrop.service "$HOME/.config/systemd/user/"
cp -a kde-customizations/launcher/backdrop/effect/. "$HOME/.local/share/kwin/effects/ralleur-start-backdrop/"
```

The existing `launcher-blur.conf` assumes upstream's password dialog under
`~/.config/quickshell/minimal-polkit`. If installed, back up its `blur-strength.py`,
replace it with the version from `launcher/backdrop/`, and copy the drop-in to
`~/.config/systemd/user/caelestia-shell.service.d/`. Without that password dialog,
create a drop-in containing only the service dependency instead:

```ini
[Unit]
Wants=ralleur-start-backdrop.service
After=ralleur-start-backdrop.service
```

Then run:

```sh
kwriteconfig6 --file kwinrc --group Plugins --key ralleur-start-backdropEnabled true
qdbus6 org.kde.KWin /KWin reconfigure
systemctl --user daemon-reload
systemctl --user restart caelestia-shell.service
systemctl --user status ralleur-start-backdrop.service
```

The shell already includes the current socket connection. Do not run old launcher
QML patches or `taskbar_glass.py` over it again. Without the helper service, the
fullscreen background blur is absent; assembling the menu does not install that
service. The full service chain still needs validation on a clean machine.

## 6. Optional Hermes and gaming setup

The Hermes UI is in the shell; install the agent separately. Read the
[Hermes notes](../kde-customizations/launcher/README.md#hermes-aus-der-suchleiste)
first. `hermes/install.sh` sets up the runtime and profile, and may obtain further
dependencies depending on the selected model. It pins the runtime commit.
Keep cloud credentials in your private profile, never in this repository.
Local models need separate downloads and suitable hardware; the
[Qwen profile](../kde-customizations/launcher/hermes/qwen38/README.md) is optional.
The desktop works without an AI account.

Install and configure Steam, Battle.net, WoW, Discord, Spotify and other apps from
the screenshots independently. The Windows reboot button appears only when a
compatible UEFI Windows installation is detected. flausen does not create a
dual-boot installation. Gaming helpers, WowUp automation and NVIDIA settings need
their respective launcher, application and hardware setup.

## Check your installation

After login, check the topbar and dock, maximized/fullscreen windows, app launch
and switching, start menu/search, settings, and audio/network/Bluetooth displays.
A visual check does not require changing connections or devices. Test Files with
a sample folder, quick preview and normal window closing. Test tiling and login
components after their individual setup.

The current tiling component uses **Super + Shift + left-button drag** to add a
window to tiling. **Super + left-button drag** moves it freely or takes it out of
tiling. **Super + right-button drag** resizes. Workspace scrolling is a separate
[Super + mouse wheel component](../kde-customizations/desktop-scroll/README.md).

```sh
systemctl --user is-active caelestia-shell.service
journalctl --user -u caelestia-shell.service -b -p warning --no-pager
```

Report problems with the flausen commit (`git rev-parse HEAD`), distribution,
Qt/Plasma versions, affected component and a redacted log. Do not attach tokens
or personal configuration to an issue.

## Updates and recovery

`git pull --ff-only` initially updates only the repository. Record your working
commit first. Assemble the new state in a **new** output directory, compare it
with installed files, and take another backup before copying changes. There is
currently no automatic merge of your own shell edits. Caelestia's updaters update
upstream and can overwrite flausen; do not use them as a flausen update mechanism.

For recovery, first undo additional components with **their own** manifests in
reverse order, including localization and branding. Remove the manually copied
settings launcher and native settings files if they were new to this installation;
if they replaced earlier files, restore your backups instead.

Restore the shell base using your own backup from step 4:

```sh
systemctl --user stop caelestia-shell.service
# Set FLAUSEN_BACKUP to your backup path if the variable is no longer set.
mv "$HOME/.config/quickshell/caelestia" "$FLAUSEN_BACKUP/shell-flausen"
cp -a "$FLAUSEN_BACKUP/shell" "$HOME/.config/quickshell/caelestia"
mv "$HOME/.config/caelestia" "$FLAUSEN_BACKUP/config-flausen"
cp -a "$FLAUSEN_BACKUP/config" "$HOME/.config/caelestia"
systemctl --user start caelestia-shell.service
```

Compare and restore a separately backed up `~/.config/Caelestia` as well.
Reconcile settings changed since your backup before replacing them. The moved
flausen directories remain available for comparison. If the graphical session
fails to start, use the same steps in a TTY as the affected user. To return from
Caelestia to Plasma completely, also follow the pinned upstream installer's
recovery procedure.

## What has been verified

The source snapshot comes from the running development session. Assembly is
performed in isolation from pinned upstream Git objects and checked against all
284 recorded modified source files. Structure checks and repository tests run in
addition. This does not replace a clean installation, hardware testing or
validation of optional services on a second machine.
