/* KWin 6: route fullscreen windows among existing desktops; never create one. */
"use strict";
const spaces = [];

function exists(desktop) {
    return workspace.desktops.some(d => d.id === desktop.id);
}

function belongs(window, desktop) {
    return window.desktops.some(d => d.id === desktop.id);
}

function descendant(window, parent) {
    let current = window.transientFor;
    const seen = [];
    while (current && seen.indexOf(current) < 0) {
        if (current === parent) return true;
        seen.push(current);
        current = current.transientFor;
    }
    return false;
}

function fullscreenOwner(desktop, window) {
    return workspace.windowList().find(w => w !== window && w.fullScreen &&
        w.normalWindow && !w.transientFor && belongs(w, desktop));
}

function routeNewWindow(window) {
    if (window.specialWindow || window.desktopWindow || window.dock || window.onAllDesktops)
        return;
    const available = window.desktops.filter(desktop => {
        const owner = fullscreenOwner(desktop, window);
        return !owner || descendant(window, owner);
    });
    if (available.length === window.desktops.length) return;
    if (available.length) {
        window.desktops = available;
        return;
    }

    const source = window.desktops.find(d => d.id === workspace.currentDesktop.id) ||
        window.desktops[0];
    const space = spaces.find(s => s.window === fullscreenOwner(source, window));
    const desktops = workspace.desktops;
    const index = desktops.findIndex(d => d.id === source.id);
    const previousDesktops = desktops.slice(0, index).reverse()
        .concat(desktops.slice(index + 1).reverse());
    const preferred = space && exists(space.origin) ? [space.origin] : [];
    const target = preferred.concat(previousDesktops).find(d => !fullscreenOwner(d, window));
    if (target) window.desktops = [target];
}

function destination(window) {
    const desktops = workspace.desktops;
    const start = desktops.findIndex(d => d.id === workspace.currentDesktop.id);
    if (desktops.length < 2 || start < 0) return null;
    const others = workspace.windowList().filter(w => w !== window &&
        !descendant(w, window) && !w.desktopWindow && !w.dock && !w.onAllDesktops);
    // Search to the right, wrapping once; the current desktop is not a target.
    let fallback = null;
    for (let offset = 1; offset < desktops.length; ++offset) {
        const target = desktops[(start + offset) % desktops.length];
        if (fullscreenOwner(target, window)) continue;
        if (!others.some(w => belongs(w, target))) return target;
        if (!fallback) fallback = target;
    }
    return fallback;
}

function enter(window) {
    if (!window.fullScreen || !window.normalWindow || window.transientFor ||
            spaces.some(s => s.window === window)) return;
    const desktop = destination(window);
    if (!desktop) return;
    const previous = window.desktops.slice();
    const origin = previous.find(d => d.id === workspace.currentDesktop.id) ||
        previous[0] || workspace.currentDesktop;
    const follow = workspace.activeWindow === window;
    const space = {window: window, desktop: desktop, origin: origin,
        previous: previous, dialogs: [], manuallyMoved: false};
    spaces.push(space);
    window.desktops = [desktop];
    workspace.windowList().forEach(w => moveDialog(w, space));
    if (follow) workspace.currentDesktop = desktop;
}

function moveDialog(window, space) {
    if (!descendant(window, space.window) ||
            space.dialogs.some(d => d.window === window)) return;
    space.dialogs.push({window: window, previous: window.desktops.slice()});
    window.desktops = [space.desktop];
}

function leave(window, closed) {
    const index = spaces.findIndex(s => s.window === window);
    if (index < 0) return;
    const space = spaces[index];
    spaces.splice(index, 1);
    const target = space.previous.filter(exists);
    if (!target.length && space.previous.length && exists(space.origin)) target.push(space.origin);
    const follow = !space.manuallyMoved && workspace.currentDesktop.id === space.desktop.id &&
        (workspace.activeWindow === window || (closed && !workspace.activeWindow));
    if (!closed && !space.manuallyMoved && belongs(window, space.desktop)) window.desktops = target;
    space.dialogs.forEach(d => {
        if (belongs(d.window, space.desktop)) {
            const previous = d.previous.filter(exists);
            d.window.desktops = previous.length || !d.previous.length ? previous : target;
        }
    });
    if (follow && exists(space.origin)) workspace.currentDesktop = space.origin;
}

function watch(window) {
    window.fullScreenChanged.connect(() => {
        if (window.fullScreen) enter(window);
        else leave(window, false);
    });
    window.desktopsChanged.connect(() => {
        const space = spaces.find(s => s.window === window);
        if (space && (window.desktops.length !== 1 || !belongs(window, space.desktop)))
            space.manuallyMoved = true;
    });
    window.transientChanged.connect(() => spaces.forEach(s => moveDialog(window, s)));
    spaces.forEach(s => moveDialog(window, s));
}

workspace.windowAdded.connect(window => {
    watch(window);
    routeNewWindow(window);
    enter(window);
});
workspace.windowRemoved.connect(window => {
    spaces.forEach(s => { s.dialogs = s.dialogs.filter(d => d.window !== window); });
    leave(window, true);
});
// Existing fullscreen windows reserve their current desktop when the script is reloaded.
workspace.windowList().forEach(watch);
