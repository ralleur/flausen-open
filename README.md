<div align="center">

# flausen.

**Your computer. Your playground.**

An everyday OS for work, creativity and play.
A familiar desktop built on CachyOS, KDE Plasma, KWin and Caelestia.

[Manual setup](installation/MANUAL.md) · [Components](installation/README.md) · [Contributing](CONTRIBUTING.md)

</div>

## Source availability

This repository contains the public source snapshot. The desktop wallpaper sets,
brand artwork, screenshots and videos are omitted pending redistribution review.
Some desktop components and the website require those assets for their full appearance.
The source snapshot has no public ISO builds attached.

Original flausen. code is available under GPL-3.0-or-later unless a component
states a different license. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

## How it started

I started gaming on Windows in the late 90s and spent most of my IT career working
with it. Years ago, I moved my personal and professional work to macOS. Linux was
always somewhere in the background, but I never seriously considered it for my own
desktop. I have a broad IT background; I have never been a developer or worked
professionally with Linux.

Like many others, I noticed the excitement around Omarchy and gave it a try. It
showed me how quickly ideas could become real through agent-assisted customization.
But the desktop itself did not quite fit me: too many shortcuts to remember, and
not enough that felt self-explanatory. After some research, I landed on KDE and
Caelestia as a starting point.

The idea behind **flausen.** is to bring together the things I enjoy about Windows
and macOS, add a few things I have always wanted, and give them a consistent look.
A versatile everyday PC for getting work done, creating things, browsing,
listening to music and playing games. I try to keep the terminal out of
normal desktop tasks because, in my experience, it is often where people who are
new to Linux lose the confidence to keep exploring.

## A desktop that feels connected

Smoky glass runs through the shell, Dolphin, settings, context menus and dialogs.
Shared typography and controls give the different parts a common visual language.
The settings interface brings KDE modules and Caelestia controls together, so you
spend less time working out which settings application owns a particular option.

*Appearance controls and KDE display settings share the same settings window.*

Coming from macOS, I wanted a dock that behaved familiarly as well as looking the
part. I also missed Finder's layout and pressing **Space** to preview a file.
Files builds those ideas into Dolphin, with an integrated header, folder colors
and quick previews. An optional ZIP association makes a double-click extract an
archive through Ark without an extra dialog.

*Dolphin with a compact integrated header and a familiar Places sidebar.*

## Familiar ways to get things done

From Windows, I missed a proper Task Manager and a start menu that put recent apps,
documents, settings and power options in one place. Both are part of flausen.

*Recent apps and files, search, settings and power controls in one menu, with a
blurred backdrop that keeps attention on the task at hand.*

On a compatible UEFI dual-boot setup, the start menu can also reboot directly into
Windows. That is useful for an online game that still requires it, or a hardware
utility such as the one for configuring my SteelSeries mouse buttons. Linux stays
the default; Windows is there when I need it, without reaching for boot-menu keys.
flausen does not install Windows or set up dual boot for you.

### Task Manager

Processes, resource histories, startup entries and user services have their own
views. The hardware cards stay visible as you move between them.

### Windows when you want them

Windows float by default. You can bring them into a Hyprland-inspired tiling
workflow with **Super + Shift + left-button drag**, then move them back out when
you want. Fullscreen applications move to the next available workspace, and
**Super + mouse wheel** switches workspaces. These behaviors are provided by the
optional KWin components described in the setup guide.

### Everyday tools in the taskbar

Screenshot tools and clipboard history live in the taskbar. Recent captures,
recording, text extraction and image search are grouped in Screen Capture;
clipboard history keeps copied text and images within reach.

Network controls bring Wi-Fi, VPN status and live traffic into one popover.
There is also a custom lock screen and screensaver.

### Sound you can see

Caelestia's audio visualizer has been adapted to show separate applications in
different colors. The audio controls use those same application colors.

<details>
<summary>Audio controls and Now playing</summary>

*Output, input and individual app volumes sit alongside media playback controls.*

</details>

## Making gaming feel simpler

I would like launching a game to feel straightforward regardless of whether it
uses Proton, Wine or a native build. That is a direction for the project;
compatibility still depends on the game, its launcher and your system.

The current setup brings system, app and game update information into one hub,
including Steam, Battle.net and WoW addon status through WowUp. Update installation
and addon automation still depend on their respective tools and configuration.
The hub does not replace those tools or silently install everything for you.

There is also an optional NVIDIA frame-generation toggle in the Battle.net context
menu for the configured gaming integration. It applies the driver's setting when
launching through that integration. It is specific to the relevant hardware and
launcher setup; see the [taskbar component notes](kde-customizations/taskbar/README.md).

## An experimental assistant in the start menu

I have also been experimenting with [Hermes Agent](https://github.com/NousResearch/hermes-agent)
in the start menu, with local and cloud model selection, tool activity and usage
information. This is still experimental. You provide your own runtime, models and
credentials; using the rest of the desktop does not require an AI account.

<details>
<summary>Hermes model selection and GPU memory preview</summary>

*Local and cloud model selection, with an estimated GPU memory budget for the
configured local model. The estimate describes this machine and profile.*

</details>

## Try the current setup

Right now, flausen is my custom **CachyOS setup**. Turning it into a properly
installable spin is a longer-term goal. The current GitHub snapshot gives other
technically comfortable CachyOS users a manual path to try it while I work on the
installer.

The development machine runs **Plasma/KWin 6.8.2, Qt 6.12 and Quickshell 0.3.2 on
Wayland**. A complete installation on a second, clean machine has not yet been
validated. Other distributions are untested for flausen. There is no flausen ISO,
package repository or automatic flausen update channel yet.

This repository is currently **private**. Testers need an invitation and GitHub
access before they can clone it.

```sh
git clone git@github.com:ralleur/flausen.git
cd flausen
./bin/flausen check
```

**Continue with the [manual setup guide](installation/MANUAL.md).** It covers the
pinned Caelestia-KDE base, source preparation, native builds, backups, activation,
optional components and recovery. Everyday desktop use aims to keep the terminal
out of the way; setting up this early preview still involves terminal commands.

The screenshots show my development machine. Its games, commercial apps, accounts
and personal configuration are not bundled. Some features require the additional
components in the guide.

## Where things live

| Area | Start here |
| --- | --- |
| Current desktop | [Component catalogue](installation/components.json), [`kde-customizations/`](kde-customizations/) |
| Manual setup | [Guide](installation/MANUAL.md), [source manifest](installation/shell-lock.json) |
| Design | [Branding](branding/flausen/README.md), [shared menu rules](kde-customizations/MENU_DESIGN.md) |
| Development | [Repository structure](docs/structure.md), [development workflow](docs/development.md) |
| Future distribution | [System definition](system/README.md), [release status](release/README.md) |
| Website | [Local website](website/README.md) |

The active desktop uses KDE/KWin. `ralleur-desktop/` contains an earlier Hyprland
prototype. The separation of desktop sources, system definition, installation and
release work takes inspiration from [Ryoku](https://github.com/Ryoku-dev/ryoku).

## Credits and feedback

flausen builds on [Caelestia-KDE](https://github.com/ladybug-me/caelestia-kde),
Caelestia, KDE and other projects credited in [NOTICE.md](NOTICE.md). Their license
terms and the separate status of supplied branding and assets are documented there.

There are probably a hundred things that could be done differently, and some parts
are still rough. I am also fairly new to using Linux as my daily desktop. I would
love to hear what feels useful, what feels confusing, and what you would change.
If you have repository access, open an issue with your setup and what you found,
or read [Contributing](CONTRIBUTING.md) to get involved.
