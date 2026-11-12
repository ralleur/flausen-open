# Contributing to flausen.

flausen brings together familiar Windows and macOS desktop ideas on CachyOS,
KDE/KWin and Caelestia. The aim is a consistent everyday desktop that also works
well for gaming, with visible controls that people can discover as they use it.
Some parts are still experimental; feedback from real setups is welcome.

Read [AGENTS.md](AGENTS.md) for the project's local design rules,
[the repository map](docs/structure.md) for responsibilities, and
[the development workflow](docs/development.md) for checks and installation.

Keep changes in the existing component. Reuse shared design and branding sources.
Register new desktop components in the central catalogue.

Check and preserve existing local work before making changes. Stage only files
within your task. Run the relevant component checks and inspect the actual desktop
for UI changes. A pull request should describe the resulting behavior, the change,
validation and its limits. Keep builds, private configuration and credentials out
of the repository.

For a bug report, include the flausen commit, distribution, Plasma/Qt versions,
the affected component and steps to reproduce. Redact personal data and secrets
from logs. Installation on a clean second machine is especially useful feedback;
a passing structure check alone does not validate a complete desktop deployment.
