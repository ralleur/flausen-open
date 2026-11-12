import QtQuick
import Quickshell
import Quickshell.Io
import Caelestia.Config
import qs.services
import qs.modules.drawers
import qs.modules.areapicker
import qs.modules.lock
import qs.modules
import qs.ralleur

ShellRoot {
    id: root
    settings.watchFiles: false
    Binding {
        target: ShellState
        property: "shellRoot"
        value: root
    }
    GSFLoader {}
    ServiceLoader {}
    Backend {
        id: backendSource
    }
    Drawers {}
    AreaPicker {}
    Lock {
        id: lock
    }
    Shortcuts {}
    BatteryMonitor {}
    IdleMonitors {
        lock: lock
    }
    Variants {
        model: Quickshell.screens
        Screen {
            backend: backendSource
        }
    }
    IpcHandler {
        target: "ralleur"
        function reload(): void {
            Quickshell.reload(true);
        }
        function widgets(): void {
            const screen = ShellState.forActive()?.modelData ?? Quickshell.screens[0];
            ShellUi.toggle(screen.width, screen.height);
        }
        function theme(): void {
            Theme.toggle();
        }
        function launcher(): void {
            const s = ShellState.forActive();
            if (s)
                s.launcher = !s.launcher;
        }
        function settings(): void {
            backendSource.drawer(Quickshell.screens[0], "settings");
        }
        function session(): void {
            const s = ShellState.forActive();
            if (s)
                s.session = !s.session;
        }
        function workspace(id: int): void {
            backendSource.workspace(id);
        }
        function focusApp(role: string): void {
            const app = AppCatalog.apps.find(a => a.id === role);
            if (app)
                backendSource.launch(app);
        }
        function status(): string {
            const screen = ShellState.forActive()?.modelData ?? Quickshell.screens[0];
            return JSON.stringify({
                theme: Theme.mode,
                workspace: backendSource.activeWorkspace,
                title: backendSource.activeTitle,
                player: backendSource.player?.identity ?? null,
                playing: backendSource.player?.isPlaying ?? false,
                cpu: Metrics.cpu,
                memory: Metrics.memory,
                disk: Metrics.disk,
                widgets: ShellUi.isWide(screen.width, screen.height) ? ShellUi.widgets : ShellUi.sidebar,
                fullscreen: Quickshell.screens.map(s => ({
                            screen: s.name,
                            active: backendSource.fullscreen(s)
                        }))
            });
        }
    }
}
