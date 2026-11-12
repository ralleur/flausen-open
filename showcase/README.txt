flausen. / Phase one showcase
Your computer. Your playground.

READY TO SHARE
- flausen-showcase-1080p.mp4: 93.4 seconds, 1920 x 1080, H.264, 30 fps.
  Silent, with English captions baked into the video.
- flausen-showcase-en.srt: English sidecar captions.
- flausen-phase-one-overview.pdf: nine-page feature overview and complete index.
- exports/: nine overview pages and nine focused 1080p image cards.
- features.json: editable English feature copy, relationships, source paths and limits.
- demo-script.txt: timed narrative and capture notes.

PRESENTATION
All compositions use the existing 10-colour-current wallpaper selected by the user.
The video alternates large UI details with actual desktop interactions. The cards
were visually reviewed at 960 x 540 to represent playback in a smaller window.
The complete 4K desktop appears only for orientation and window-layout context.

CAPTURE NOTES
Files, Kate, settings, tiling and fullscreen routing were recorded on the real
running desktop. Fullscreen routing is demonstrated with a local media clip,
not gameplay or a game-performance test. The four-workspace pool remains fixed.
Recent documents, the screenshot gallery and clipboard contents are staged examples.
The initial Hermes chat was captured without issuing a paid model request.
The model-selection and VRAM views were captured without saving a new model profile.
The user's original workspace, wallpaper and notification setting were restored.

STATUS
This is a customization showcase of a current development build based on CachyOS,
KDE Plasma/KWin and Caelestia. It does not announce an ISO, installer or release.
The built login greeter is not shown as an installed login screen.
Update status is informational; responsible applications perform installations.
The current Hermes warning and experimental labels remain part of its native UI.

SOURCES
source/capture.py: isolated native Start menu, Hermes and popover captures.
source/capture_tools.py: native capture/gallery and clipboard with staged content.
source/capture_desktop.py: real desktop workflow capture with temporary windows.
source/build_assets.py: PDF generation and page PNG exports (ReportLab + Poppler).
source/build_video.py: focused image cards, editing and video/subtitle generation.
source/workflow-markers.json: measured timestamps for the real workflow.
source/background.png: the exact existing wallpaper used for the compositions.

REBUILD
Run from the repository root. Native captures require the installed flausen desktop.
Python dependencies: Pillow, ReportLab. Tools: ffmpeg, ffprobe, pdftoppm.
The desktop capture also uses the existing KWin and EIS test helpers in this repo.

python showcase/source/capture.py
python showcase/source/capture_tools.py
python showcase/source/capture_desktop.py

The desktop recorder writes its initial material to .cache/showcase-video/.
Review that local recording before export. The approved workflow in this kit starts
4.4 seconds into that take and lasts 40.4 seconds; its clean input is named
showcase/desktop-workflow.mp4. Do not package unreviewed raw desktop recordings.
The clean input and measured markers can be reused without recording again.

python showcase/source/build_assets.py
python showcase/source/build_video.py

The PDF is generated at output/pdf/flausen-phase-one-overview.pdf.
Bundled Python can be used when system ReportLab is unavailable.

ENGLISH DESKTOP
kde-customizations/localization/install.py applies the English presentation strings
and user-session language, preserving keyboard layout, timezone and data paths.
Run this after an older customization installer if it reintroduces German labels:

python kde-customizations/localization/install.py
systemctl --user restart caelestia-shell.service

Existing applications reload their language at next start. A full sign-out/sign-in
completes the session-language transition. No reboot or logout was triggered.
Language backups: ~/.local/state/flausen/language-backups/.
Use install.py --restore BACKUP to restore unchanged installed language files.
The native Files plugin has separate verified backups under
~/.local/state/flausen/language-native-backups/.
