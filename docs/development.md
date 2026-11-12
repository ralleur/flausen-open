# Development

Read [AGENTS.md](../AGENTS.md), [the repository map](structure.md) and the affected
component's README first. For menu work, also read
[MENU_DESIGN.md](../kde-customizations/MENU_DESIGN.md).

## Shared entry point

From the project root, with Python 3.11 or later and no extra Python packages:

```sh
./bin/flausen components
./bin/flausen components --layer wm
./bin/flausen check
python3 -m unittest discover -s tests -v
```

`components` lists source paths and documentation. `check` validates the catalogue
format, unique IDs and sources, existing paths and registration of every direct
desktop component. Both commands only read repository files and work outside the
project root. They do not run installers or inspect the live session.

## Changing a component

1. Edit its existing source. Reuse shared tokens and UI elements.
2. Run the build and relevant tests from its README. Tests that access the live
   session or change the system belong on a suitable test machine; CI does not
   run them indiscriminately.
3. Use the component installer with its backups. `--dry-run` and `--restore`
   options are not yet standardized.
4. Check the actual session. For visual changes, compare reference and
   implementation at the same outer width.
5. Update documentation and useful evidence. Distinguish rendered checks,
   automated tests and live results.

Register new direct desktop components in `installation/components.json`.
Their READMEs should cover purpose, external requirements, build, installation,
validation and recovery. Exports, private data and local backup pointers are not
source payloads.

CI checks the catalogue, repository tools and pinned shell source assembly.
Native Qt/KWin builds, installers and visual acceptance still need the respective
component checks. A green structure check does not certify the desktop.

## Maintaining the manual preview

`installation/prepare-shell.py` assembles the pinned KDE shell from upstream Git
objects, referenced component files and the remaining integration patch. CI also
builds this source directory. Neither operation changes installation directories
or running sessions.

After reviewing a shell change, update the canonical component sources first.
A maintainer can explicitly capture the remaining integration differences from a
reviewed **source directory**:

```sh
python3 installation/capture-shell.py \
  --upstream /path/to/clean/caelestia-kde-checkout \
  --shell "$HOME/.config/quickshell/caelestia" \
  --output .cache/review-shell-update \
  --snapshot YYYY-MM-DD-manual-preview
```

The capture command only reads its allowed source file types, excluding personal
JSON configuration and binaries. It finds identical or closely matching existing
component files and records references instead of a second source copy. Review
both the heuristic mapping and **every** captured change for content, provenance
and private data before accepting it. Capture does not automatically approve the
running machine as a product source. New files should normally live in the
responsible existing component.

After review, copy `shell-lock.json` and `shell-integration.patch` together from
the new directory to `installation/`. Assemble them with `prepare-shell.py` in
another new directory and compare the result with the reviewed source state.
For an upstream version change, reconcile the base, build and manual guide first.
Do not update hashes merely to suppress an error.

The preview has source assembly checks, repository tests and local builds.
Installation on a second clean system, upgrades and complete recovery still need
their own validation.
