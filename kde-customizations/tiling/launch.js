// One request consumes exactly one future main window; existing windows are untouched.
var RALLEUR_LAUNCHES = [];
function ralleurLaunchKey(value) {
    return String(value || "").toLowerCase().replace(/\.desktop$/, "");
}
function ralleurArmLaunch(payload) {
    const now = Date.now();
    RALLEUR_LAUNCHES = RALLEUR_LAUNCHES.filter(item => item.expires > now);
    RALLEUR_LAUNCHES.push({keys: JSON.parse(payload).map(ralleurLaunchKey), expires: now + 15000});
    RALLEUR_LAUNCHES = RALLEUR_LAUNCHES.slice(-16);
}
function ralleurApplyLaunch(controller, ctx, window) {
    const now = Date.now();
    RALLEUR_LAUNCHES = RALLEUR_LAUNCHES.filter(item => item.expires > now);
    const client = window.window.window;
    if (window.shouldIgnore || window.window.shouldFloat || client.dialog || client.splash
        || client.transient || client.specialWindow || client.fullScreen) return;
    const keys = [client.desktopFileName, client.resourceClass, client.resourceName].map(ralleurLaunchKey);
    const index = RALLEUR_LAUNCHES.findIndex(item => item.keys.some(key => keys.includes(key)));
    if (index < 0) return;
    RALLEUR_LAUNCHES.splice(index, 1);
    const layout = controller.engine.layouts.getCurrentLayout(window.surface);
    const tiles = controller.engine.windows.getVisibleTiles(window.surface).filter(w => w !== window);
    if (layout.capacity != null && tiles.length >= layout.capacity) return;
    window.ralleurFloatGeometry = window.actualGeometry.clone();
    client.tile = null;
    window.state = WindowState.Tiled;
}
