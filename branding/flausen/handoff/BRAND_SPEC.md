# flausen. – Brand Specification v1.0

## 1. Kernidentität

- Display-Name: **flausen.** — immer kleingeschrieben und mit einem gelben Punkt als Satzzeichen im Logo.
- Product descriptor: **Gaming OS** (in Lauftext gelegentlich „flausen OS“, aber kein angehängtes „OS“ im Hauptlogo).
- Technischer Identifier: `flausen-os`, z. B. Repo / App-ID / Image-Name soweit kompatibel.
- Parent branding: „by ralleur“ – zurückhaltend im About-Screen, Installer und Credits, nicht als dauerhafter Topbar-Text.
- Claim: **Your computer. Your playground.** Er ist optional und darf in kleinen Flächen komplett entfallen.
- Tonalität: zugänglich, souverän, eigenwillig, ruhig; nie aufdringlich, infantil oder voller Linux-Jargon.

## 2. Logo – unverhandelbare Form

Das ausgewählte ursprüngliche Konzept ist **ein dreifarbiger Punkt-Dreiklang über der kleingeschriebenen Wortmarke `flausen.`**:

1. Ein größerer warmer gelber Kreis links (`#F2B84B`).
2. Ein kleinerer Korall-Kreis in der Mitte (`#EB6B61`).
3. Ein kleinerer hellblauer Kreis rechts (`#649DEB`).
4. Die Wortmarke in **Inter Display Medium**, ohne zusätzlichen Schatten, Gradienten, Umriss oder Zierelemente.
5. Das **Schlusszeichen ist ein gelber Punkt**, kein normales typografisches Zeichen in Textfarbe.

Die drei Kreise sollen als ein eigenständiges, wiedererkennbares OS-Symbol funktionieren. Die **gestapelte Version** ist Standard. Die horizontale Version ist eine Platzvariante, nicht die neue Standardmarke. Kleine Systemflächen dürfen nur das Symbol zeigen.

**Assets:** `assets/logos/` (inkl. separater, fontabhängiger editierbarer Quellversion). Die Produktions-SVGs enthalten Glyph-Pfade und keine verlinkten Fonts. Positionen/Farben der Kreise nicht neu erfinden. Ursprung: im Chat abgestimmtes erstes `flausen.`-Konzept.

## 3. Palette

| Token | Hex | Rolle |
|---|---|---|
| Charcoal | `#17191D` | dunkler Basishintergrund |
| Off-white | `#F5F4F0` | Text auf dunkel / heller Basishintergrund |
| Muted slate | `#AAAEB7` | sekundäre Schrift dunkel |
| Warm yellow | `#F2B84B` | erster Kreis, Schlusspunkt, kleine Akzente |
| Coral | `#EB6B61` | zweiter Kreis, ergänzende Akzente |
| Sky blue | `#649DEB` | dritter Kreis, ergänzende Akzente |
| Dark surface | `#24272D` | Widgets / Karten auf dunkel |
| Dark border | `#33363E` | feine Trenner, keine harten Outlines |
| Light surface | `#FFFFFF` | Widgets / Karten auf hell |
| Light border | `#D9DBDF` | dezente helle Trenner |

Dark Mode ist die Hero-Präsentation; **Light Mode muss gleichwertig gestaltet sein**. Kontrast und Fokuszustände funktional verifizieren. Farben nie als alleinige Informationsquelle verwenden.

## 4. Typografie / Geometrie

- Logo: Inter Display Medium, als Pfadlogo geliefert.
- UI: Inter (sofern vorhanden) + generischer System-Sans-Fallback. Keine Fonts im Paket.
- Stil: große einfache Wortmarke, minimalistische Flächen, ruhige Typografie, kleine funktionale Farbtupfer.
- Fenster / Widgets: sanfte Rundungen; keine übertriebenen Glow-, Bokeh-, Neon- oder Gamer-RGB-Effekte.
- Minimalgrößen: Icon auf 24 px validieren; Logo mit Schrift nicht auf unleserliche Größen verkleinern.

## 5. Platzierung / UX

| Oberfläche | Geplante Verwendung |
|---|---|
| Boot / Plymouth | Symbol -> Wortmarke, ggf. dezente kurze Punktanimation, auf dunklem/hellem Grund |
| Login / SDDM bzw. gewählter Display Manager | `flausen.` + cleane Login-Oberfläche im selben Light/Dark-System |
| Shell / Launcher | kleine dreifarbige Marke in Menü/Launcher, kein permanentes Branding an jeder Ecke |
| About/System Settings | Name, Version, Build-Info, „by ralleur“, Open-Source-Infos |
| Installer / USB | flausen.-Branding ohne Terminal/Linux-Jargon in Nutzertexten |
| Updates / Fehlermeldungen | klare nutzerorientierte Sprache und einheitliche UI-Tokens |
| Fullscreen Gaming | brandbezogene Shell-Overlays verschwinden; keine störenden Animationen |
| Hintergrundbilder | Desktop-Mocks als Kompositionsreferenz, aber Logo nicht als gigantisches Wallpaper-Wasserzeichen |

### Boot-Animation (Konzept, nicht geliefert als Code)

Die Kreise dürfen nacheinander in ihre Position gleiten und sich dort setzen; danach tritt die Wortmarke ruhig hervor. Gesamtdauer kurz, ohne blockierende Animation. `prefers-reduced-motion` bzw. System-Accessibility berücksichtigen. Wenn Plymouth technisch eingeschränkt ist: die statischen SVG/PNG-Assets nutzen, nicht Animation vortäuschen.

## 6. Verbotene Abweichungen

- Nicht „Flausen“, „FLAUSEN“, „Flausen Linux“ oder „Flausen Gaming Edition“ als Hauptlogo.
- Nicht das parent brand `ralleur` komplett ablösen oder dessen Logo verändern.
- Keine generischen Gaming-Maskottchen, Controller-Icons, Sterne, Planeten oder weiteren Illustrationen ans Logo hängen.
- Das markante **gelbe Schlusszeichen** nicht entfernen.
- Keine unautorisierte Änderung der produktiven ralleur-Website oder anderer Projekte.
