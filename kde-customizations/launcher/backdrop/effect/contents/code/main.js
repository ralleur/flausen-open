// SPDX-License-Identifier: GPL-2.0-or-later
"use strict";
let helperPid = 0;
function loadConfig() {
    helperPid = Number(effect.readConfig("HelperPid", 0));
}
effect.configChanged.connect(loadConfig);
loadConfig();
function isBackdrop(window) {
    return helperPid > 0 && window.pid === helperPid && String(window.windowClass).indexOf("quickshell") !== -1;
}
effects.windowAdded.connect(function (window) {
    if (!isBackdrop(window)) return;
    effect.grab(window, Effect.WindowAddedGrabRole, true);
    animate({window: window, duration: 240, type: Effect.Opacity,
        from: 0.0, to: 1.0, curve: QEasingCurve.OutCubic});
});
effects.windowClosed.connect(function (window) {
    if (!isBackdrop(window)) return;
    effect.grab(window, Effect.WindowClosedGrabRole, true);
    animate({window: window, duration: 240, type: Effect.Opacity,
        to: 0.0, curve: QEasingCurve.InOutCubic});
});
