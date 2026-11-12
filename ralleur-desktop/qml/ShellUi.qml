pragma Singleton
import Quickshell

Singleton {
    property bool widgets: true
    property bool sidebar: false
    function isWide(width: int, height: int): bool {
        return width >= Theme.geo.widgetBreakpoint && height >= Theme.geo.widgetMinHeight;
    }
    function toggle(width: int, height: int): void {
        if (isWide(width, height))
            widgets = !widgets;
        else
            sidebar = !sidebar;
    }
}
