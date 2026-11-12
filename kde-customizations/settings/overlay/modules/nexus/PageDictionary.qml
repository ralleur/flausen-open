pragma Singleton

import QtQuick
import qs.utils

QtObject {
    readonly property list<var> pages: [
        {
            label: qsTr("Appearance"),
            key: "appearance",
            icon: "palette",
            description: qsTr("Wallpapers, fonts, colors"),
            category: "personalization",
            settings: [
                { label: qsTranslate("Flausen", "Text size"), keywords: [qsTranslate("Flausen", "Font size"), qsTranslate("Flausen", "Scaling"), "Text"], subPageIdx: -1 },
                { label: qsTranslate("Flausen", "Transparency"), keywords: [qsTranslate("Flausen", "Glass"), qsTranslate("Flausen", "Transparent")], subPageIdx: -1 },
                { label: qsTranslate("Flausen", "Reduce motion"), keywords: [qsTranslate("Flausen", "Animations"), qsTranslate("Flausen", "Effects")], subPageIdx: -1 },
                { label: qsTranslate("Flausen", "Color mode"), keywords: [qsTranslate("Flausen", "Light"), qsTranslate("Flausen", "Dark"), qsTranslate("Flausen", "Automatic"), "Design"], subPageIdx: -1 },
                { label: qsTranslate("Flausen", "Accent color"), keywords: [qsTranslate("Flausen", "Blue"), qsTranslate("Flausen", "Coral"), qsTranslate("Flausen", "Gold"), qsTranslate("Flausen", "Green"), qsTranslate("Flausen", "Violet"), qsTranslate("Flausen", "Graphite")], subPageIdx: -1 },
                { label: qsTranslate("Flausen", "Schedule"), keywords: [qsTranslate("Flausen", "Sunrise"), qsTranslate("Flausen", "Sunset"), qsTranslate("Flausen", "Automatic")], subPageIdx: 10 },
                { label: qsTr("Theme & Effects"), pagePath: "wallandstyle/AppearancePage.qml", subPageIdx: 8 },
                { label: qsTr("Font"), keywords: ["font", "typeface", "family", "text"], pagePath: "wallandstyle/AppearancePage.qml", subPageIdx: 8 },
                { label: qsTr("Monospace font"), keywords: ["monospace", "font", "code", "terminal"], pagePath: "wallandstyle/AppearancePage.qml", subPageIdx: 8 },
                { label: qsTr("Font scale"), keywords: ["font", "scale", "size", "text"], pagePath: "wallandstyle/AppearancePage.qml", subPageIdx: 8 },
                { label: qsTr("Colors"), keywords: ["accent", "palette", "scheme", "theme", "color"], pagePath: "wallandstyle/ColourSelect.qml", subPageIdx: 3 },
                { label: qsTr("Advanced color settings"), keywords: ["advanced", "colors", "palette", "saturation", "contrast", "matugen"], pagePath: "wallandstyle/AdvancedColorsPage.qml", subPageIdx: 10 },
                { label: qsTr("Color intensity"), keywords: ["intensity", "chroma", "vibrant", "vibrancy"], pagePath: "wallandstyle/AdvancedColorsPage.qml", subPageIdx: 10 },
                { label: qsTr("Blur & Opacity"), pagePath: "wallandstyle/AppearancePage.qml", subPageIdx: 8 },
                { label: qsTr("Corner Radius"), keywords: ["rounding", "radius"], pagePath: "wallandstyle/AppearancePage.qml", subPageIdx: 8 },
                { label: qsTr("Wallpapers"), pagePath: "wallandstyle/WallpaperSelect.qml", subPageIdx: 1 },
                { label: qsTr("Wallhaven"), keywords: ["wallhaven", "download", "online", "search"], pagePath: "wallandstyle/WallhavenPage.qml", subPageIdx: 4 },
                { label: qsTr("Wallpaper settings"), keywords: ["filters", "thumbnails", "wallpaper"], pagePath: "wallandstyle/WallpaperSettingsPage.qml", subPageIdx: 5 },
                { label: qsTr("Slideshow & Order"), keywords: ["slideshow", "interval", "randomise", "shuffle", "order"], pagePath: "wallandstyle/SlideshowAndOrderPage.qml", subPageIdx: 6 },
                { label: qsTr("Video wallpapers"), keywords: ["video", "animated", "motion"], pagePath: "wallandstyle/VideoWallpapersPage.qml", subPageIdx: 7 },
                { label: qsTr("Lock Screen"), keywords: ["lock", "wallpaper sync", "screen lock"], pagePath: "wallandstyle/LockScreenPage.qml", subPageIdx: 9 },
                { label: qsTr("Fingerprint"), keywords: ["fingerprint", "unlock", "attempts", "tries", "howdy", "biometric"], pagePath: "wallandstyle/LockScreenPage.qml", subPageIdx: 9 },
                { label: qsTr("Bezel mode"), keywords: ["pitch black", "bezels", "black", "theme and effects"], pagePath: "wallandstyle/AppearancePage.qml", subPageIdx: 8 }
            ]
        },
        {
            label: qsTr("Desktop & Tiling"),
            key: "desktop",
            icon: "desktop_windows",
            description: qsTr("KDE Desktop, addons, right click menu"),
            category: "personalization",
            settings: [
                { label: qsTr("KDE Desktop Integration"), keywords: ["plasma", "icons", "desktop"] },
                { label: qsTr("Right Click Menu"), pagePath: "wallandstyle/ContextMenuPage.qml", subPageIdx: 2 },
                { label: qsTr("Desktop Addons"), pagePath: "wallandstyle/DesktopAddonsPage.qml", subPageIdx: 1 },
                { label: qsTr("Window Tiling"), pagePath: "desktop/KrohnkitePage.qml", keywords: ["krohnkite", "tiling", "layouts"], subPageIdx: 3 },
                { label: qsTr("Floating windows"), keywords: ["floating", "float", "krohnkite"], pagePath: "desktop/KrohnkitePage.qml", subPageIdx: 3 },
                { label: qsTr("Virtual Workspaces"), keywords: ["desktops", "virtual", "switcher"] }
            ]
        },
        {
            label: qsTr("Desktop & Dock"),
            key: "panels",
            icon: "dock_to_bottom",
            description: qsTr("Dashboard, taskbar, launcher, sidebar"),
            category: "personalization",
            settings: [
                { label: qsTr("Taskbar"), pagePath: "panels/TaskbarPanel.qml", keywords: ["per-monitor", "position", "screen"], subPageIdx: 2 },
                { label: qsTr("Dashboard"), pagePath: "panels/DashboardPanel.qml", subPageIdx: 1 },
                { label: qsTr("Launcher"), pagePath: "panels/LauncherPanel.qml", subPageIdx: 3 },
                { label: qsTr("App browser layout"), keywords: ["launcher", "layout", "simple", "compact", "categories", "favourites"], pagePath: "panels/LauncherPanel.qml", subPageIdx: 3 },
                { label: qsTr("Truncated app names"), keywords: ["launcher", "name", "truncated", "long", "tooltip", "shrink", "flip"], pagePath: "panels/LauncherPanel.qml", subPageIdx: 3 },
                { label: qsTr("Clipboard"), keywords: ["history", "copied", "paste", "maximum entries", "history size", "confirm clear"], pagePath: "panels/LauncherPanel.qml", subPageIdx: 3 },
                { label: qsTr("Sidebar"), pagePath: "panels/SidebarPanel.qml", subPageIdx: 4 },
                { label: qsTr("Quick Toggles Panel"), pagePath: "panels/UtilitiesPanel.qml", subPageIdx: 5 },
                { label: qsTr("Overview"), pagePath: "panels/OverviewPanel.qml", keywords: ["overview", "animations", "blur"], subPageIdx: 16 },
                { label: qsTr("Toggle & Rearrange"), keywords: ["widgets", "components", "reorder", "add"], pagePath: "panels/taskbar/BarComponents.qml", subPageIdx: 6 },
                { label: qsTr("Workspaces indicator"), keywords: ["workspaces", "indicators", "window icons"], pagePath: "panels/taskbar/BarWorkspaces.qml", subPageIdx: 7 },
                { label: qsTr("Unoccupied workspaces"), keywords: ["workspaces", "empty", "inactive", "hide"], pagePath: "panels/taskbar/BarWorkspaces.qml", subPageIdx: 7 },
                { label: qsTr("Greeter"), keywords: ["greeting", "popout"], pagePath: "panels/taskbar/BarGreeter.qml", subPageIdx: 8 },
                { label: qsTr("Greeter slideshow"), keywords: ["slideshow", "folders", "media", "greeting", "timing", "order"], pagePath: "panels/taskbar/BarGreeter.qml", subPageIdx: 8 },
                { label: qsTr("Tray"), keywords: ["system tray", "icons"], pagePath: "panels/taskbar/BarTray.qml", subPageIdx: 9 },
                { label: qsTr("Status icons"), keywords: ["indicators", "bar"], pagePath: "panels/taskbar/BarStatusIcons.qml", subPageIdx: 10 },
                { label: qsTr("Clock"), keywords: ["date", "time"], pagePath: "panels/taskbar/BarClock.qml", subPageIdx: 11 },
                { label: qsTr("Clock seconds"), keywords: ["clock", "time", "seconds", "show seconds"], pagePath: "panels/taskbar/BarClock.qml", subPageIdx: 11 },
                { label: qsTr("Dock"), keywords: ["dock", "pinned", "apps", "grouping", "ungroup", "combine"], pagePath: "panels/taskbar/BarDock.qml", subPageIdx: 12 },
                { label: qsTr("GitHub"), keywords: ["github", "contributions", "token"], pagePath: "panels/taskbar/BarGithub.qml", subPageIdx: 13 },
                { label: qsTr("Media"), keywords: ["media", "music", "player", "spotify", "youtube", "now playing", "volume", "visualiser"], pagePath: "panels/taskbar/BarMedia.qml", subPageIdx: 19 },
                { label: qsTr("Weather"), keywords: ["weather", "temperature", "units", "celsius", "fahrenheit", "city"], pagePath: "panels/taskbar/BarWeather.qml", subPageIdx: 20 },
                { label: qsTr("Performance"), keywords: ["performance", "cpu", "gpu", "ram", "memory", "storage", "network", "battery", "pills", "stats"], pagePath: "panels/taskbar/BarPerformance.qml", subPageIdx: 21 },
                { label: qsTr("Screen Capture"), keywords: ["screenshot", "recording", "region", "spectacle", "gif"], pagePath: "panels/taskbar/BarScreenCapture.qml", subPageIdx: 22 },
                { label: qsTr("Keep Awake"), keywords: ["idle", "inhibit", "sleep", "caffeine", "coffee"], pagePath: "panels/taskbar/BarKeepAwake.qml", subPageIdx: 23 },
                { label: qsTr("Per-element scaling offsets"), keywords: ["scale", "font scale", "preview"], pagePath: "panels/taskbar/BarPreviewScales.qml", subPageIdx: 14 },
                { label: qsTr("Elements & Modules"), keywords: ["workspaces", "tray", "clock", "modules"], pagePath: "panels/taskbar/TaskbarElements.qml", subPageIdx: 15 },
                { label: qsTr("Update indicator"), keywords: ["updates", "indicator"], pagePath: "panels/taskbar/BarUpdates.qml", subPageIdx: 17 },
                { label: qsTr("Topbar scale"), keywords: ["topbar", "scale", "size", qsTranslate("Flausen", "Scale"), qsTranslate("Flausen", "Size")], pagePath: "panels/TaskbarPanel.qml", subPageIdx: 2 },
                { label: qsTr("Dock scale"), keywords: ["dock", "scale", "size", qsTranslate("Flausen", "Scale"), qsTranslate("Flausen", "Size")], pagePath: "panels/TaskbarPanel.qml", subPageIdx: 2 },
                { label: qsTr("Preview scale"), keywords: ["preview", "thumbnails", "scale"], pagePath: "panels/TaskbarPanel.qml", subPageIdx: 2 },
                { label: qsTr("Performance"), keywords: ["performance widgets", "dashboard", "randomize shape colors", "cpu", "memory", "storage"], pagePath: "panels/DashboardPanel.qml", subPageIdx: 1 },
                { label: qsTr("Dashboard clock seconds"), keywords: ["clock", "seconds", "dashboard", "time"], pagePath: "panels/DashboardPanel.qml", subPageIdx: 1 },
                { label: qsTr("Fuzzy search"), keywords: ["launcher", "search", "fuzzy"], pagePath: "panels/LauncherPanel.qml", subPageIdx: 3 },
                { label: qsTr("Activation"), keywords: ["hot corner", "bottom left corner", "bottom right corner", "gestures", "overview"], pagePath: "panels/OverviewPanel.qml", subPageIdx: 16 },
                { label: qsTr("Window Switcher"), keywords: ["tab switcher", "alt+tab", "task switcher", "desktop", "preview", "filter", "windows"], pagePath: "panels/TabSwitcherPanel.qml", subPageIdx: 18 }
            ]
        },
        {
            label: qsTr("Network"),
            key: "network",
            icon: "wifi",
            description: qsTr("Wi-Fi and VPN connections"),
            category: "connectivity",
            settings: [
                { label: qsTr("Wi-Fi"), keywords: ["wireless", "internet", "connections"] },
                { label: qsTr("VPN"), keywords: ["vpn", "tunnel", "secure"] },
                { label: qsTr("IPv4"), keywords: ["ethernet", "ip address", "dhcp", "gateway"] },
                { label: qsTr("All networks"), keywords: ["list", "available", "scan"], pagePath: "network/AllNetworksPage.qml", subPageIdx: 5 },
                { label: qsTr("Saved networks"), keywords: ["remembered", "forget", "profiles"], pagePath: "network/SavedNetworksPage.qml", subPageIdx: 6 },
                { label: qsTr("Hotspot"), keywords: ["hotspot", "tethering", "access point", "share connection"], pagePath: "network/HotspotPage.qml", subPageIdx: 7 }
            ]
        },
        {
            label: qsTr("Connected devices"),
            key: "bluetooth",
            icon: "bluetooth",
            description: qsTr("Bluetooth, pairing, drivers"),
            category: "connectivity",
            settings: [
                { label: qsTr("Bluetooth"), keywords: ["wireless", "devices", "accessories"] },
                { label: qsTr("Discoverable"), keywords: ["discoverable", "visibility", "bluetooth"] },
                { label: qsTr("Pairable"), keywords: ["pairable", "bluetooth"] },
                { label: qsTr("Pairing"), pagePath: "bluetooth/BluetoothPairing.qml", subPageIdx: 2 }
            ]
        },
        {
            label: qsTr("Audio & Sound"),
            key: "audio",
            icon: "volume_up",
            description: qsTr("Output, input, app volume, sound effects"),
            category: "connectivity",
            settings: [
                { label: qsTr("Speakers & Output"), keywords: ["volume", "playback", "sink"] },
                { label: qsTr("Microphones"), keywords: ["input", "recording", "source"] },
                { label: qsTr("App Volumes"), pagePath: "audio/AppVolumes.qml", subPageIdx: 1 },
                { label: qsTr("Sound Effects"), pagePath: "audio/SoundEffectsPage.qml", subPageIdx: 2, keywords: ["sfx", "feedback", "camera", "screen lock"] },
                { label: qsTr("Muted Notification Apps"), pagePath: "audio/NotificationSilencingPage.qml", subPageIdx: 3, keywords: ["silence", "mute", "notification sound"] }
            ]
        },
        {
            label: qsTr("Notifications"),
            key: "notifications",
            icon: "notifications",
            description: qsTr("Alerts, toasts, and delivery behavior"),
            category: "controls",
            settings: [
                { label: qsTr("Notification behavior"), pagePath: "services/NotificationPreferencesPage.qml", subPageIdx: 1, keywords: ["fullscreen", "position", "timeout", "taskbar"] },
                { label: qsTr("Toasts"), pagePath: "services/ToastPreferencesPage.qml", subPageIdx: 2, keywords: ["popup", "banner", "sound", "volume"] },
                { label: qsTr("Toast events"), pagePath: "services/ToastEventsPage.qml", subPageIdx: 3, keywords: ["charging", "clipboard", "vpn", "keyboard", "audio"] }
            ]
        },
        {
            label: qsTr("Utilities"),
            key: "utilities",
            icon: "build",
            description: qsTr("Quick controls, game mode"),
            category: "controls",
            settings: [
                { label: qsTr("On-screen Sliders"), subPageIdx: 3, keywords: ["volume", "microphone", "brightness", "osd"] },
                { label: qsTr("Utilities Panel"), subPageIdx: 4, keywords: ["keep awake", "screenshot", "record"] },
                { label: qsTr("Quick Toggles"), subPageIdx: 5, keywords: ["toggles", "dashboard", "switches"] },
                { label: qsTr("Game Mode"), pagePath: "services/GameModePage.qml", subPageIdx: 1, keywords: ["hyprland overrides", "performance", "games"] },
                { label: qsTr("Auto-enable rules"), keywords: ["game mode", "rules", "target windows"], pagePath: "services/GameModeTargetsPage.qml", subPageIdx: 2 },
                { label: qsTr("Quick Share"), pagePath: "services/QuickSharePage.qml", subPageIdx: 6, keywords: ["bluetooth", "nearby", "file sharing", "send file", "receive file", "android"] }
            ]
        },
        {
            label: qsTr("Session"),
            key: "session",
            icon: "power_settings_new",
            description: qsTr("Shutdown, logout, and reboot menu"),
            category: "controls",
            settings: [
                { label: qsTr("Session Menu"), keywords: ["power", "shutdown", "logout", "reboot", "hibernate"] },
                { label: qsTr("Session Icons"), keywords: ["icon", "logout", "shutdown"] },
                { label: qsTr("Session Commands"), keywords: ["command", "logout", "shutdown"] }
            ]
        },
        {
            label: qsTr("Shortcuts"),
            key: "shortcuts",
            icon: "keyboard",
            description: qsTr("Keyboard shortcuts, custom keybinds"),
            category: "controls",
            settings: [
                { label: qsTr("System Shortcuts"), keywords: ["global", "keys", "hotkeys"] },
                { label: qsTr("App Shortcuts"), keywords: ["launch", "open", "binding"] },
                { label: qsTr("Custom Keybinds"), pagePath: "wallandstyle/AddShortcutDialog.qml", keywords: ["scripts", "commands", "actions"] }
            ]
        },
        {
            label: qsTr("Apps"),
            key: "apps",
            icon: "apps",
            description: qsTr("Default apps, file types, app details"),
            category: "shell",
            settings: [
                { label: qsTr("Default Apps"), keywords: ["browser", "email", "default"] },
                { label: qsTr("File Types"), keywords: ["associations", "extensions", "open with"] },
                { label: qsTr("All Apps"), keywords: ["installed", "list", "uninstall"], subPageIdx: 1 },
                { label: qsTr("Favorites & Hidden"), keywords: ["pinned", "dock", "launcher", "ignore"], subPageIdx: 1 },
            ]
        },
        {
            label: qsTr("Services"),
            key: "services",
            icon: "settings_suggest",
            description: qsTr("Background services, daemon control"),
            category: "shell",
            settings: [
                { label: qsTr("Background Services"), keywords: ["daemons", "systemd", "tuning"] },
                { label: qsTr("Visualiser Input"), keywords: ["visualiser", "microphone", "cava", "audio"] },
                { label: qsTr("Rich Presence"), keywords: ["discord", "steamgriddb", "activity"], pagePath: "services/ArpcPage.qml", subPageIdx: 1 }
            ]
        },
        {
            label: qsTr("Language & region"),
            key: "language",
            icon: "language",
            description: qsTr("Locale, timezone, formats"),
            category: "shell",
            settings: [
                { label: qsTr("Language"), keywords: ["locale", "translation", "ui"] },
                { label: qsTr("Time & Date"), keywords: ["clock", "timezone", "format"] },
                { label: qsTr("Weather Location"), keywords: ["city", "forecast", "units", "celsius", "fahrenheit"] }
            ]
        },
        {
            label: qsTranslate("Flausen", "Update hub"),
            key: "updates",
            icon: "update",
            description: qsTranslate("Flausen", "Caelestia, apps and games"),
            category: "system",
            settings: [
                { label: qsTranslate("Flausen", "Apps & games"), keywords: ["Steam", "Battle.net", "WowUp", "ArtCraft", "PhotoCraft", "LightCraft", "Updates", "Downloads", "automatisch"] },
                { label: qsTr("Firmware Updates"), keywords: ["bios", "fwupd", "hardware"] }
            ]
        },
        {
            label: qsTr("Plugins"),
            key: "plugins",
            icon: "extension",
            description: qsTr("Personalized desktop experience"),
            category: "system",
            settings: [
                { label: qsTr("Plugin system"), description: qsTr("Personalized desktop experience"), keywords: ["extensions", "addons", "plugins"] }
            ]
        },
        {
            label: qsTr("About System"),
            key: "about",
            icon: "info",
            description: qsTr("Specs, version, system information"),
            category: "system",
            settings: [
                { label: qsTr("Device Info"), keywords: ["hardware", "specs", "cpu", "ram"] },
                { label: qsTr("OS Version"), keywords: ["caelestia", "quickshell", "release"] },
                { label: qsTr("Uninstall Caelestia"), keywords: ["remove", "delete", "uninstall", "purge"] }
            ]
        },
        {
            label: qsTr("AI Assistant"),
            key: "ai",
            icon: "smart_toy",
            description: qsTr("Claude Code, accounts, providers"),
            category: "assistant",
            settings: [
                { label: qsTr("Claude Code"), keywords: ["claude", "cli", "subscription", "login"] },
                { label: qsTr("Let the CLI run its own tools"), keywords: ["claude", "permissions", "tools", "bypass", "dangerous"] },
                { label: qsTr("Accounts"), keywords: ["claude", "account", "login", "switch"] },
                { label: qsTr("Providers"), keywords: ["ollama", "openai", "chatgpt", "gemini", "openrouter", "api key"] }
            ]
        },
        {"label": qsTranslate("Flausen", "General"), "key": "general", "icon": "settings", "description": qsTranslate("Flausen", "Account, language, date, default apps, accessibility"), "category": "flausen", "settings": [{"label": "Account", "systemModule": "kcm_users", "systemTitle": qsTranslate("Flausen", "Account")}, {"label": qsTranslate("Flausen", "Language"), "systemModule": "kcm_regionandlang", "systemTitle": qsTranslate("Flausen", "Language")}, {"label": qsTranslate("Flausen", "Date"), "systemModule": "kcm_clock", "systemTitle": qsTranslate("Flausen", "Date")}, {"label": qsTranslate("Flausen", "Default apps"), "systemModule": "kcm_componentchooser", "systemTitle": qsTranslate("Flausen", "Default apps")}, {"label": "Accessibility", "systemModule": "kcm_access", "systemTitle": "Accessibility"}, {"label": qsTranslate("Flausen", "User account"), "systemModule": "kcm_users", "systemTitle": qsTranslate("Flausen", "User account"), "keywords": ["Account", "Profile picture", "Password"]}, {"label": qsTranslate("Flausen", "Language & region"), "systemModule": "kcm_regionandlang", "systemTitle": qsTranslate("Flausen", "Language & region"), "keywords": ["Language", "Formats"]}, {"label": qsTranslate("Flausen", "Date & time"), "systemModule": "kcm_clock", "systemTitle": qsTranslate("Flausen", "Date & time"), "keywords": ["Date", "Time", "Time zone"]}]},
        {"label": qsTranslate("Flausen", "Display"), "key": "display", "icon": "monitor", "description": qsTranslate("Flausen", "Resolution, scaling, night light, monitors"), "category": "flausen", "settings": [{"label": "Resolution", "systemModule": "kcm_kscreen", "systemTitle": "Resolution"}, {"label": qsTranslate("Flausen", "Scaling"), "systemModule": "kcm_kscreen", "systemTitle": qsTranslate("Flausen", "Scaling")}, {"label": qsTranslate("Flausen", "Night light"), "systemModule": "kcm_nightlight", "systemTitle": qsTranslate("Flausen", "Night light")}, {"label": "Monitors", "systemModule": "kcm_kscreen", "systemTitle": "Monitors"}, {"label": qsTranslate("Flausen", "Display configuration"), "systemModule": "kcm_kscreen", "systemTitle": qsTranslate("Flausen", "Display configuration"), "keywords": ["Resolution", "Scaling", "Monitors", "HDR"]}, {"label": qsTranslate("Flausen", "Power & sleep"), "systemModule": "kcm_powerdevilprofilesconfig", "systemTitle": qsTranslate("Flausen", "Power & sleep"), "keywords": ["Power", "Standby"]}]},
        {"label": qsTranslate("Flausen", "Keyboard & mouse"), "key": "input", "icon": "mouse", "description": qsTranslate("Flausen", "Input devices, touchpad, shortcuts"), "category": "flausen", "settings": [{"label": qsTranslate("Flausen", "Input devices")}, {"label": "Touchpad", "systemModule": "kcm_touchpad", "systemTitle": "Touchpad"}, {"label": qsTranslate("Flausen", "Keyboard shortcuts"), "systemModule": "kcm_keys", "systemTitle": qsTranslate("Flausen", "Keyboard shortcuts")}, {"label": "Keyboard", "systemModule": "kcm_keyboard", "systemTitle": "Keyboard", "keywords": ["Layout", "Num-Lock"]}, {"label": "Mouse", "systemModule": "kcm_mouse", "systemTitle": qsTranslate("Flausen", "Mouse"), "keywords": ["Speed", "Scrolling"]}, {"label": qsTranslate("Flausen", "System shortcuts"), "systemModule": "kcm_keys", "systemTitle": qsTranslate("Flausen", "System shortcuts"), "keywords": ["Keyboard shortcuts"]}]},
        {"label": qsTranslate("Flausen", "Privacy & security"), "key": "privacy", "icon": "shield", "description": qsTranslate("Flausen", "Lock screen, password, firewall"), "category": "flausen", "settings": [{"label": qsTranslate("Flausen", "Lock screen"), "systemModule": "kcm_screenlocker", "systemTitle": qsTranslate("Flausen", "Lock screen")}, {"label": "Password", "systemModule": "kcm_users", "systemTitle": "Password"}, {"label": "Firewall", "systemModule": "kcm_firewall", "systemTitle": "Firewall"}, {"label": qsTranslate("Flausen", "Screen locking"), "systemModule": "kcm_screenlocker", "systemTitle": qsTranslate("Flausen", "Screen locking"), "keywords": ["Lock screen", "Lock"]}, {"label": qsTranslate("Flausen", "Password & account"), "systemModule": "kcm_users", "systemTitle": qsTranslate("Flausen", "Password & account"), "keywords": ["Password"]}]},
        {"label": qsTranslate("Flausen", "System"), "key": "system", "icon": "deployed_code", "description": qsTranslate("Flausen", "Updates, hardware, power, startup, system information"), "category": "flausen", "settings": [{"label": "Updates", "targetPage": 13}, {"label": "Hardware", "systemModule": "kcm_about-distro", "systemTitle": "Hardware"}, {"label": qsTranslate("Flausen", "Power"), "systemModule": "kcm_powerdevilprofilesconfig", "systemTitle": qsTranslate("Flausen", "Power")}, {"label": qsTranslate("Flausen", "Startup"), "targetPage": 8}, {"label": qsTranslate("Flausen", "System information"), "systemModule": "kcm_about-distro", "systemTitle": qsTranslate("Flausen", "System information")}, {"label": qsTranslate("Flausen", "Power management"), "systemModule": "kcm_powerdevilprofilesconfig", "systemTitle": qsTranslate("Flausen", "Power management"), "keywords": ["Power", "Battery"]}]},
        {label:"Hermes",key:"hermes",icon:"auto_awesome",description:qsTranslate("Flausen", "Your assistant in the Start menu"),category:"assistant",settings:[{label:qsTranslate("Flausen", "Model & thinking mode"),keywords:["Hermes","DeepSeek","ChatGPT","OpenAI","Codex","Ollama","Qwen","llama.cpp","Local endpoint",qsTranslate("Flausen", "Network"),"Endpoint","lokal","Cloud","KI","Assistent"]},{label:qsTranslate("Flausen", "API key"),keywords:["Hermes","DeepSeek",qsTranslate("Flausen", "Access")]}]}
    ]

    // Sub page index of the first entry pointing at the given page, or -1 when
    // no entry does. Callers that jump to a sub page should look it up instead
    // of hardcoding the number: inserting a sub page anywhere in the registry
    // shifts every index after it, which silently repoints shortcuts.
    function subPageIdxFor(pagePath: string): int {
        for (let i = 0; i < pages.length; i++) {
            const settings = pages[i].settings || [];
            for (let j = 0; j < settings.length; j++) {
                if (settings[j].pagePath === pagePath)
                    return settings[j].subPageIdx;
            }
        }
        return -1;
    }
}
