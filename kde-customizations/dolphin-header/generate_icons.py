#!/usr/bin/env python3
"""Small original SVG folder overlay; all other icons come from KDE's theme."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "icons"
COLORS = {
    "folder": "#ff7058", "folder-open": "#ff7058", "inode-directory": "#ff7058",
    "folder-red": "#ff7058", "folder-download": "#ff7058", "folder-blue": "#5798ee",
    "folder-yellow": "#efb85b", "folder-green": "#65c88a",
    "folder-violet": "#a87be7", "folder-grey": "#9b9da1",
    "folder-cyan": "#65c8cc", "folder-orange": "#efa569",
    "folder-documents": "#5798ee", "folder-downloads": "#9b9da1",
    "folder-pictures": "#a87be7", "folder-music": "#65c88a",
    "folder-videos": "#5798ee", "folder-desktop": "#5798ee",
    "folder-templates": "#efb85b", "folder-public": "#9b9da1",
}
PLACES = {
    "downloads": ("#ff7058", '<path d="M12 3v12m-4-4 4 4 4-4M5 17v4h14v-4"/>'),
    "documents": ("#5798ee", '<path d="M14 3H6a2 2 0 0 0-2 2v15a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V9Z M14 3v6h6M8 13h8M8 17h6"/>'),
    "pictures": ("#a87be7", '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8" cy="9" r="1.5"/><path d="m4 18 5-5 4 4 3-3 4 4"/>'),
    "music": ("#65c88a", '<path d="M9 18V5l11-2v13M9 9l11-2"/><ellipse cx="6" cy="18" rx="3" ry="2.5"/><ellipse cx="17" cy="16" rx="3" ry="2.5"/>'),
    "videos": ("#5798ee", '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 9h4M3 15h4M17 9h4M17 15h4m-11-5 4 2-4 2Z"/>'),
}


def svg(color):
    paint = f'fill="{color}"' if color else 'class="ColorScheme-Accent" fill="currentColor"'
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- SPDX-License-Identifier: MIT; original Ralleur folder geometry -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
 <defs>
  <style id="current-color-scheme">.ColorScheme-Accent {{ color: #ff7058; }}</style>
  <linearGradient id="soft-light" x1="0" y1="0" x2="0" y2="1">
   <stop stop-color="#fff" stop-opacity=".22"/>
   <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
 </defs>
 <g {paint}>
  <path d="M4 15 Q4 9 10 9 H24 Q27 9 29 12 L32 15 H54 Q60 15 60 21 V49 Q60 55 54 55 H10 Q4 55 4 49Z"/>
  <path fill="#000" fill-opacity=".17" d="M4 15 Q4 9 10 9 H24 Q27 9 29 12 L32 15 H54 Q60 15 60 21 V49 Q60 55 54 55 H10 Q4 55 4 49Z"/>
  <rect x="4" y="19" width="56" height="38" rx="5"/>
 </g>
 <rect x="4" y="19" width="56" height="38" rx="5" fill="url(#soft-light)"/>
 <rect x="4.5" y="19.5" width="55" height="37" rx="4.5" fill="none" stroke="#fff" stroke-opacity=".13"/>
</svg>
'''


def generate():
    folder = ROOT / "scalable/places"
    folder.mkdir(parents=True, exist_ok=True)
    for name, color in COLORS.items():
        (folder / (name + ".svg")).write_text(svg(color))
    for name, (color, paths) in PLACES.items():
        (folder / ("ralleur-place-" + name + ".svg")).write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">\n'
            f'<g fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{paths}</g>\n</svg>\n')
    (ROOT / "index.theme").write_text('''[Icon Theme]
Name=Ralleur Rounded Folders
Comment=Rounded folder SVGs for Dolphin; other icons inherit the existing KDE theme
Inherits=@PARENT@,hicolor
FollowsColorScheme=true
Directories=scalable/places

[scalable/places]
Size=64
MinSize=16
MaxSize=512
Type=Scalable
Context=Places
''')


if __name__ == "__main__":
    generate()
