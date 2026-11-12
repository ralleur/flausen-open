// Resize intent comes from KWin, never from asynchronous client buffer commits.
function ralleurResizeStart(controller, ctx, window) {
    if (!CONFIG.adjustLayout || !window.isTiled) return;
    controller.engine.ralleurResizingWindow = window;
    window.ralleurResizePending = true;
}

function ralleurResizeStep(controller, ctx, window, geometry) {
    if (!window.ralleurResizePending || !CONFIG.adjustLayoutLive) return;
    controller.engine.adjustLayout(window, toRect(geometry));
    controller.engine.arrange(ctx, "onWindowResize", "ralleurResizeStep");
}

function ralleurResizeOver(controller, ctx, window) {
    if (!window.ralleurResizePending) return false;
    // moveResizedChanged fires before KWin restores geometry on Escape. Read
    // the final requested geometry on the next event-loop turn, not the buffer.
    ctx.setTimeout(() => {
        if (!window.ralleurResizePending) return;
        if (window.isAlive() && !window.window.window.resize) {
            const geometry = RALLEUR_INPUT.requestedGeometry(window.window.window);
            if (window.isTiled && geometry.width > 0 && geometry.height > 0)
                controller.engine.adjustLayout(window, toRect(geometry));
            window.ralleurResizePending = false;
            if (controller.engine.ralleurResizingWindow === window)
                controller.engine.ralleurResizingWindow = null;
            controller.engine.arrange(ctx, "onWindowResizeOver", "ralleurResizeOver");
        } else if (!window.isAlive()) {
            window.ralleurResizePending = false;
            if (controller.engine.ralleurResizingWindow === window)
                controller.engine.ralleurResizingWindow = null;
        }
    }, 0);
    return true;
}

function ralleurResizeOwnsSurface(engine, window) {
    const active = engine.ralleurResizingWindow;
    return active && active.isAlive() && active.ralleurResizePending
        && active.surface.id === window.surface.id;
}
