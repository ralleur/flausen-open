/* Keep at most eight virtual desktops. Never close a window when trimming. */
const maximumDesktops = 8;
let enforcing = false;
function enforceLimit() {
    if (enforcing) return;
    enforcing = true;
    try {
        while (workspace.desktops.length > maximumDesktops) {
            const fallback = workspace.desktops[maximumDesktops - 1];
            const excess = workspace.desktops[workspace.desktops.length - 1];
            workspace.windowList().forEach(window => {
                if (window.onAllDesktops || !window.desktops.some(d => d.id === excess.id)) return;
                const retained = window.desktops.filter(d => d.id !== excess.id);
                window.desktops = retained.length ? retained : [fallback];
            });
            if (workspace.currentDesktop.id === excess.id) workspace.currentDesktop = fallback;
            workspace.removeDesktop(excess);
        }
    } finally {
        enforcing = false;
    }
}
workspace.desktopsChanged.connect(enforceLimit);
enforceLimit();
