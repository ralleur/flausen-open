# Idle-Logo im Session-Menü

`ralleur-idle.gif`: 320 × 320 Pixel, 80 Frames, 20 fps, vier Sekunden,
unendliche Schleife, transparenter Hintergrund, originale acht Markenfarben.
Leichtes Schweben (1,1 Logo-Einheiten) und Wippen (unter einem Grad).
Die Bewegung und ihre Geschwindigkeit schließen am Schleifenübergang an.
Die Logo-Geometrie stammt aus `ralleur-screensaver-main/Sources/Logo.swift`.

Erzeugung: `python render-idle.py` (Pillow).

Installiert unter `~/.config/quickshell/caelestia/assets/ralleur-idle.gif`.
Das angepasste `modules/session/Content.qml` verwendet eine einzige
`AnimatedImage` ohne Einfärbung/Shader und spielt sie nur im geöffneten
Session-Menü. GIF-Frame-Caching ist deaktiviert. Die Session-Aktionen bleiben
unverändert. `Content.qml` hier ist der installierte Stand.

Rückbau: `backup/Content.qml` nach
`~/.config/quickshell/caelestia/modules/session/Content.qml` kopieren.
Das bisherige Dino-GIF bleibt als Originaldatei erhalten.
