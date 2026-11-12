# System definition

This area is reserved for a shared flausen target-system definition: package sets,
service activation, hardware profiles and boot integration. There is no installable
system definition here yet. A proper installable spin is a longer-term goal.

The active desktop is KDE Plasma/KWin with Caelestia, developed on CachyOS.
Existing KWin and session extensions stay in `kde-customizations/`; their
component-specific services are not copied here. Individual requirements are
currently documented in component READMEs.

Future shared definitions should be read by both installation and packaging.
Include package names and services only after checking them on a clean target
system. Keep hardware-specific options separate from the common desktop.
Distribution and hardware support require actual installation and runtime testing.
