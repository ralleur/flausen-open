# flausen. kinetic website

Local-only, standalone TypeScript/Vite site. The operating-system code and existing
production websites are unchanged. No remote fonts, runtime services or analytics.

From this repository, `./website/dev.sh` starts the local development server. On
this workstation it can use the available Codex Node/npm tools if npm is absent
from PATH. In a normal Node environment:

```sh
cd website
npm ci
npm run dev
```

Use a supported Node release compatible with [Vite](https://vite.dev/guide/)
(Node 22.12+ or newer supported LTS). Dependencies are pinned in `package-lock.json`;
versions were resolved from the official npm registry. Tested with Node 24.22.1.

```sh
npm run build       # regenerate HTML, type-check, produce dist/
npm test            # Chromium interaction and responsive checks
npm run preview     # serve the production build locally
node scripts/inspect.mjs # capture the visual review set while dev server runs
```

Tests start the local server if needed. They use system Chromium when present;
otherwise install Playwright Chromium with `npx playwright install chromium`.
`CHROMIUM_PATH` overrides the browser executable. The site needs no installation
on a hosting provider and this task does not deploy it.

## Source responsibilities

- `src/content.json`: authoritative supplied English copy; no release/download claims.
- `src/geometry.json`: editable supplied paths, with the orange attachment corrected.
- `src/scene-geometry.json`: original handoff pivot map, kept as authoring reference.
- `scripts/render.mjs`: desktop/phone composition and semantic HTML generation.
  `index.html` is generated and committed so content and links exist without JS.
- `src/tokens.css`, `src/style.css`: exact palette and responsive presentation.
- `public/brand/`: supplied compact symbols and an original outlined serif wordmark.
- `src/navigation.ts`: fragment navigation, single inline editorial sheet, focus and Escape.
- `src/motion.ts`: bounded damped springs; no framework rendering or idle animation.

The inline sheet uses normal document flow, not a modal, so focus is not trapped.
While reading, the small sculpture is inert visual context. Escape or the visible
back link restores the initiating object. Native fragments and all sections remain
usable without JavaScript. Mouse dragging starts after 6 CSS pixels; touch uses
taps and normal scrolling. Reduced motion disables all spring reactions.

See [VERIFICATION.md](VERIFICATION.md) for checks and remaining limits.
