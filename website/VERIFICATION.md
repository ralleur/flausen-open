# Verification — 2 November 2026

## Passed

- `npm run build`: generated static HTML, TypeScript check, production Vite build.
- Production preview smoke check: HTTP 200, content navigation and Escape work,
  no failed assets or browser errors.
- `npm test`: all 10 Chromium tests passed. Coverage includes three destinations
  at 320×740, 390×844, 768×1024, 1366×768 and 1536×1024; keyboard activation,
  visible focus, focus restoration, Escape, direct fragments, browser Back,
  mouse dragging with click suppression, pointer cancellation, window blur,
  simulated document hiding/resume, settling to rest, reduced motion, touch taps,
  native touch scrolling, no-JavaScript content and failed wordmark loading.
- No page errors or console errors in the normal responsive/navigation checks.
- No horizontal overflow in the viewport matrix or enlarged-content check.
  Phone destination label targets exceed 44×44 CSS pixels.
- Visual review of generated screenshots at all five sizes, keyboard and reduced
  motion states, narrow editorial content, and 200% equivalent layout viewport
  (683×384 for a 1366×768 display). Enlarged paragraph/note text also checked.
- Supplied symbols inspected at 16/24px (blue-only), 32/64px (full color), and
  64px monochrome. Full-color mark is used above 48px; favicon is blue-only.
- Calculated WCAG text contrast: chalk/blue 5.15:1, graphite/orange 5.50:1,
  graphite/petrol 4.52:1, graphite/mist 15.13:1.
- Essential assets are local. SVG cutouts are transparent even-odd paths.
  No GitHub, download, release or other external action links were added.

## Visual corrections

The supplied static scene's orange suspension point lay outside its original
triangle. The upper edge now encloses the pivot. Phone geometry is recomposed
with connected wires, independent readable labels, and an uncropped brown
counterweight. Tablet labels are enlarged independently of the drawing. The
wordmark is original serif vector lettering inspired by the supplied study;
it is not an extracted image or a falsely identified typeface.

## Limits

Testing used local desktop Chromium, including emulated touch and reduced motion.
No physical phone, Safari/Firefox run, screen-reader audit or actual browser-menu
200% zoom was performed. Hidden-tab behavior was exercised through visibility
state/event simulation rather than an operating-system tab switch. These checks
verify the implemented behavior, not OS feature availability or compatibility.

Screenshots are reproducible with `node scripts/inspect.mjs` while the development
server is running. They are local artifacts under ignored `test-results/`.
