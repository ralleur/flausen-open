"""Version-checked resize patch; usable for initial installs and staged upgrades."""
from pathlib import Path


def patched_resize(text):
    if '// RALLEUR RESIZE BEGIN' in text:
        return text
    replacements = {
        'this.control.onWindowResizeStart(window);':
            'this.control.onWindowResizeStart(window, this);',
        '    onWindowResizeStart(window) {\n    }':
            '    onWindowResizeStart(window, ctx) {\n        if (RALLEUR_INPUT) ralleurResizeStart(this, ctx, window);\n    }',
        '            if (client.resize)\n                return;':
            '''            if (client.resize) {
                if (RALLEUR_INPUT) ralleurResizeStep(this.control, this, window, geometry);
                return;
            }''',
        '    onWindowResize(ctx, window, reason) {':
            '''    onWindowResize(ctx, window, reason) {
        if (window.ralleurResizePending) return;''',
        '    onWindowResizeOver(ctx, window, reason) {':
            '''    onWindowResizeOver(ctx, window, reason) {
        if (RALLEUR_INPUT && ralleurResizeOver(this, ctx, window)) return;''',
        '    adjustLayout(basis) {\n        let delta = basis.geometryDelta;':
            '''    adjustLayout(basis, requestedGeometry) {
        let delta = requestedGeometry ? RectDelta.fromRects(basis.geometry, requestedGeometry) : basis.geometryDelta;''',
        '    enforceSize(ctx, window) {':
            '''    enforceSize(ctx, window) {
        if (ralleurResizeOwnsSurface(this, window)) return;''',
        '                if (window.isAlive() &&\n                    !window.isRelocationPending &&':
            '''                if (window.isAlive() &&
                    !ralleurResizeOwnsSurface(this, window) &&
                    !window.isRelocationPending &&''',
    }
    for old, new in replacements.items():
        if text.count(old) != 1:
            raise RuntimeError('Krohnkite resize hook changed: ' + old)
        text = text.replace(old, new)
    return text + '\n// RALLEUR RESIZE BEGIN\n' + Path(__file__).with_name('resize.js').read_text()
