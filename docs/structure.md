# Repository structure

flausen is developed as a connected desktop in this repository. Its active base
is KDE Plasma/KWin with Caelestia. The machine is a deployment target; source code,
specifications and traceable changes belong in the repository.

The separation of responsibilities takes inspiration from
[Ryoku's repository structure](https://github.com/Ryoku-dev/ryoku/blob/main/docs/structure.md),
adapted to this KDE desktop and its current stage of development. Ryoku's
compositors, distribution ports and release infrastructure are not prerequisites.

## Areas

| Path | Responsibility | Current state |
| --- | --- | --- |
| `kde-customizations/` | Active desktop: shell, apps, KWin, session and themes | Existing components with their own builds, installers and checks |
| `branding/flausen/` | Identity, tokens, assets and generators | Shared source for branded surfaces |
| `installation/` | Component catalogue and installation documentation | Manual preview with a pinned shell base; installation remains component-specific |
| `system/` | Shared system definition, future package sets and services | Scope documented; no complete system definition yet |
| `release/` | Packaging and distribution | Requirements documented; no package repository or ISO build yet |
| `bin/` | Shared repository tools | `flausen` lists and checks the component catalogue |
| `tests/` | Cross-component checks | Repository tool tests; desktop tests stay with their components |
| `.github/workflows/` | Automated checks | Structure, repository tools and pinned shell source assembly |
| `docs/` | Architecture and shared development workflow | This map and `development.md` |
| `website/` | Independent product website | Local development and its own build |
| `showcase/` | Selected presentations and recordings | Outside the installation payload |
| `ralleur-desktop/` | Earlier separate Hyprland prototype | Inactive for current KDE development |
| `ralleur-caelestia-codex-handoff/` | Historical handoff and reference mockups | Reference material |
| `.cache/`, `dist/`, `output/` | Local builds, archives and exports | Not authoritative sources |

## Desktop and shared design

The [component catalogue](../installation/components.json) assigns each direct
component under `kde-customizations/` to `shell`, `apps`, `wm`, `session` or
`appearance`. `branding` covers the shared identity. This records existing code;
it does not claim independent packages or a verified installation order.

Keep existing source paths: installers, patches, recovery and evidence refer to
them. Do not create a parallel source copy in a new product directory. Any future
move must update those references and their recovery paths together.

Maintain shared UI sources once:
[MenuStyle and MenuText](../kde-customizations/taskbar/menu-style/README.md) define
typography and material. The [menu rules](../kde-customizations/MENU_DESIGN.md) and
[brand guidelines](../branding/flausen/README.md) apply across components.

## From source to desktop

Repository source → component build and tests → installation with backups → live
validation. Do not silently promote the contents of `~/.config` into a new product
source. User settings, backups and credentials belong outside the repository.

## Towards an installable distribution

1. Build the desktop from a fresh checkout on a test system. Record each
   component's external sources, versions and dependencies; replace reliance on
   local caches with reproducible builds.
2. Give the different installers a common contract: a preview without writes,
   clear file ownership, backups, protection of user settings and a tested recovery
   path. Only then provide a common installation command.
3. Record shared package and service definitions under `system/` and check them
   on a clean system.
4. Build packages under `release/`, test upgrades and recovery, verify provenance,
   licenses and artifacts. Update channels and eventually an ISO installer can
   build on that foundation.

The structure check covers registered source paths in step 1. It does not validate
a complete installation on a new machine.
