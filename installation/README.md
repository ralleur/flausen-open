# Installation

Start with **[the manual setup guide](MANUAL.md)**. The preview dated
4 November 2026 includes a pinned Caelestia-KDE base, verifiable source assembly,
and steps for building, activation and recovery while the flausen installer is
being developed.

`prepare-shell.py` only prepares a new source directory. It does not install
anything. `shell-lock.json` references existing component sources;
`shell-integration.patch` holds the remaining integration changes. Do not apply
the historical individual patches on top of the assembled preview.

[`components.json`](components.json) is the central catalogue of active desktop
components and branding. It points to their existing sources and documentation.

```sh
./bin/flausen components
./bin/flausen check
```

Installation currently uses the tools documented by each component. Build
requirements, backups, root access and rollback differ between them. The catalogue
is not an installation order, and there is no common flausen installer for a clean
system yet.

Shared installation logic belongs here. A common installer needs pinned external
sources, verified dependencies, a complete preview, clear file ownership, backups
and a tested recovery path. It can reuse component installers once those contracts
are compatible. The catalogue tools do not change the running KDE session.

See the [development workflow](../docs/development.md) and
[distribution roadmap](../docs/structure.md#towards-an-installable-distribution).
