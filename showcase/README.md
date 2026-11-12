# flausen. in pictures

An everyday CachyOS desktop for work, creativity and play, built with KDE, KWin
and Caelestia. These screenshots were supplied from the development machine on
4 November 2026. They show real interfaces and personal configuration; the apps,
accounts, hardware and example data visible here are not bundled with the preview.

The original PNGs are stored once under [`screenshots/2026-11-04/`](screenshots/2026-11-04/)
and reused in the [project introduction](../README.md). Open an image to inspect
it at full resolution.

[Start menu and Files](#start-menu-and-files) · [Settings](#settings) ·
[Task Manager](#task-manager) · [Capture and clipboard](#capture-and-clipboard) ·
[Audio and media](#audio-and-media) · [Network and updates](#network-and-updates) ·
[Gaming integration](#gaming-integration)

## Start menu and Files

The start menu brings search, recent apps, recently opened files and session
controls together. The Windows reboot action is available on compatible UEFI
dual-boot setups. Files gives Dolphin an integrated header and a familiar Places
sidebar while retaining its native file-management functionality.

<p align="center">
  <img src="screenshots/2026-11-04/start-menu.png" width="600" alt="Start menu with search, recent apps and files, settings, Windows reboot and session controls">
</p>

![Files showing a Downloads folder through its smoky glass surface](screenshots/2026-11-04/files.png)

## Settings

Appearance controls and embedded KDE modules live in the same settings interface.
The display view shows the configuration available on this particular monitor;
hardware support and available controls depend on your system.

| Appearance | Display |
| --- | --- |
| ![Appearance settings with light, dark and automatic modes, wallpaper and accent choices](screenshots/2026-11-04/settings-appearance.png) | ![Display settings with resolution, scaling, refresh rate and HDR options](screenshots/2026-11-04/settings-display.png) |

<details>
<summary>Experimental Hermes settings</summary>

Cloud and local model choices are grouped separately. The GPU memory preview
estimates the configured local model's footprint on this machine; it is not a
general hardware requirement or a measurement of every model.

![Hermes model selection and estimated GPU memory budget](screenshots/2026-11-04/settings-hermes.png)

</details>

## Task Manager

Resource cards stay visible across the Processes, Performance, Startup and
Services views. The screenshots show the development machine's hardware and
runtime readings, rather than a performance benchmark.

### Processes

Grouped processes, resource usage and a process inspector in one view.

![Processes and resource overview](screenshots/2026-11-04/task-manager-processes.png)

### Performance

CPU core histories, memory, separate GPUs, disk and network activity.

![CPU, memory, GPU, disk and network histories](screenshots/2026-11-04/task-manager-performance.png)

### Startup and user services

Startup entries control what starts at sign-in. The Services view exposes user
services in the systemd session and their available controls.

| Startup | User services |
| --- | --- |
| ![Startup entries with enabled and disabled states](screenshots/2026-11-04/task-manager-startup.png) | ![User service statuses and start or stop controls](screenshots/2026-11-04/task-manager-services.png) |

## Capture and clipboard

Screen Capture groups screenshots, recording and recent captures with text
extraction and image search. Clipboard history includes copied text and images.

| Screen Capture | Clipboard |
| --- | --- |
| ![Screen Capture with recent capture thumbnails, OCR and image search](screenshots/2026-11-04/screen-capture.png) | ![Clipboard history with text and image entries](screenshots/2026-11-04/clipboard.png) |

## Audio and media

Separate applications have their own colors in the bottom-edge visualizer and
per-app volume controls. Output and microphone levels remain distinct, with media
source selection and playback controls in Now playing.

![App-colored visualizer along the dock and bottom edge](screenshots/2026-11-04/app-audio-visualizer.png)

| Audio controls | Now playing |
| --- | --- |
| ![Output and microphone levels, device selection and individual app volumes](screenshots/2026-11-04/audio-controls.png) | ![Media source, artwork, timeline and playback controls](screenshots/2026-11-04/now-playing.png) |

## Network and updates

The network popover combines Wi-Fi, VPN status and live traffic. The update hub
groups system, launcher, game and application update information; installation
still belongs to the respective package manager or application.

| Network | Updates |
| --- | --- |
| ![Wi-Fi network list, Tailscale VPN section and live traffic history](screenshots/2026-11-04/network.png) | ![System, game and app update groups](screenshots/2026-11-04/updates.png) |

## Gaming integration

Gaming is one part of the everyday desktop. This Battle.net context menu shows
the optional frame-generation launch setting for the configured NVIDIA setup.
It depends on the relevant driver, hardware and launcher integration.

<p align="center">
  <img src="screenshots/2026-11-04/battlenet-framegen.png" width="367" alt="Battle.net context menu with Framegen enabled above the app dock">
</p>

[Manual setup](../installation/MANUAL.md) · [Back to the project](../README.md)
