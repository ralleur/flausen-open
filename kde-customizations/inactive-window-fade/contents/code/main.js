// SPDX-License-Identifier: GPL-2.0-or-later
"use strict";

// Keep KWin's rules (including opacity exceptions) authoritative. Temporarily
// compensate their instantaneous change with a compositor opacity animation.
const transitions = new Map();
function ease(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}
function factorAt(state, now) {
    const t = state.duration > 0 ? Math.min(1, Math.max(0, (now - state.started) / state.duration)) : 1;
    return state.from + (1 - state.from) * ease(t);
}
function clear(window) {
    const state = transitions.get(window);
    if (state) cancel(state.ids);
    transitions.delete(window);
}
function near(a, b) { return Math.abs(a - b) < 0.00001; }
function changed(window, oldOpacity, newOpacity) {
    const state = transitions.get(window);
    const now = Date.now();
    const previousFactor = state ? factorAt(state, now) : 1;
    clear(window);
    // Only the existing Caelestia focus rule, never hidden bridge windows,
    // popups, application fades, or explicit 100-percent exceptions.
    if (!(window.normalWindow || window.dialog) || window.deleted || window.minimized ||
        !((near(oldOpacity, 1) && near(newOpacity, 0.95)) ||
          (near(oldOpacity, 0.95) && near(newOpacity, 1)))) return;
    const systemDuration = animationTime(250);
    if (systemDuration <= 0) return;
    // The session uses very fast global animations. Keep this subtle fade
    // perceptible without changing the speed of any other desktop effect.
    const duration = Math.max(250, systemDuration);
    const from = oldOpacity * previousFactor / newOpacity;
    const ids = animate({window: window, duration: duration, type: Effect.Opacity,
        from: from, to: 1, curve: QEasingCurve.InOutCubic});
    transitions.set(window, {ids: ids, started: now, duration: duration, from: from});
    if (effect.readConfig("Debug", false))
        console.warn("flausen-focus-fade", window.caption, oldOpacity, newOpacity, from, duration);
}
function manage(window) {
    window.windowOpacityChanged.connect(changed);
}
effects.stackingOrder.forEach(manage);
effects.windowAdded.connect(manage);
effects.windowClosed.connect(clear);
