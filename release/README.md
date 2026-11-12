# Releases and distribution

This area is reserved for flausen packaging. There is currently no complete
package build, signed package repository, update channel or ISO build. Archives
under `dist/` are local development artifacts.

A distributable release needs:

- Reproducible sources, including pinned external versions.
- Clear package boundaries and file ownership based on the
  [component catalogue](../installation/components.json).
- Traceable origins, licenses and credits for every included part.
- Verified installation, upgrades, preservation of user settings and recovery
  on a clean test system.
- Version and change information, checksums and verifiable artifacts.

Package recipes, build tools and release checks belong here once implemented.
The version of the earlier Hyprland prototype is not treated as the product
version of the active KDE desktop.

The current [manual preview](../installation/MANUAL.md) lets technically comfortable
CachyOS users try the setup while the installer is developed. Its source manifest
records an intermediate development state. It is not a packaged release or a
claim that installation on a clean machine has been validated.
