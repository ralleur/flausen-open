#!/usr/bin/env python3
"""Render production QML with isolated visual fixtures; no NetworkManager or BlueZ access."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('--source-root', type=Path, help='Optional saved source tree for visual before/after checks')
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--kind', choices=['network', 'ethernet', 'wirelesspassword', 'bluetooth', 'updates', 'audio', 'battery', 'clock'], default='network')
parser.add_argument('--native', action='store_true', help='Render isolated fixtures in a native Wayland window, including GPU shaders')
parser.add_argument('--verify-audio', action='store_true', help='Exercise audio controls against isolated fixtures with QtTest')
parser.add_argument('--light', action='store_true')
parser.add_argument('--expanded', action='store_true')
parser.add_argument('--password-error', action='store_true')
parser.add_argument('--battery-state', choices=['battery','charging','low','none','degraded'], default='battery')
parser.add_argument('--audio-state', choices=['normal','muted','empty'], default='normal')
parser.add_argument('--bluetooth-state', choices=['normal','off','empty','missing','searching'], default='normal')
parser.add_argument('--font-scale', type=float, default=1.15)
args = parser.parse_args()
if args.verify_audio and (args.kind != 'audio' or args.audio_state != 'normal' or args.expanded):
    parser.error('--verify-audio requires --kind audio with the normal collapsed fixture')
args.out = args.out.resolve()
args.out.parent.mkdir(parents=True, exist_ok=True)
shell = Path.home() / '.config/quickshell/caelestia'
with tempfile.TemporaryDirectory(prefix='network-layout-') as temp:
    config = Path(temp)
    def write(name, text):
        path = config / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    def production(name):
        saved = args.source_root / name if args.source_root else None
        return (saved if saved and saved.exists() else shell / name).read_text()
    for name in ['MenuText', 'StyledText', 'StyledRect', 'MaterialIcon', 'StateLayer', 'CAnim', 'Anim', 'AnchorAnim', 'CalendarMonthSlide']:
        write('components/' + name + '.qml', production('components/' + name + '.qml'))
    for name in ['CircularIndicator', 'CircularProgress', 'TextButton', 'ButtonBase', 'IconButton', 'StyledSlider', 'SegmentedTrack', 'SegmentedHandle', 'CustomMouseArea']:
        write('components/controls/' + name + '.qml', production('components/controls/' + name + '.qml'))
    for name in ['Network', 'WirelessPassword', 'PopoutState', 'Bluetooth', 'Updates', 'Audio', 'Battery', 'CalendarPopout', 'MenuAudioSection', 'MenuAudioSlider', 'MenuAppStreamRow']:
        write('modules/bar/popouts/' + name + '.qml', production('modules/bar/popouts/' + name + '.qml'))
    # Layout previews do not start the native sampler's worker thread.
    network_path = config / 'modules/bar/popouts/Network.qml'
    network_path.write_text(network_path.read_text().replace('ServiceRef { service: NetworkUsage }', 'QtObject {}'))
    bluetooth_path = config / 'modules/bar/popouts/Bluetooth.qml'
    bluetooth_path.write_text(bluetooth_path.read_text().replace('import Quickshell.Bluetooth', 'import qs.preview'))
    for name in ['Audio','MenuAppStreamRow','Battery']:
        path=config/('modules/bar/popouts/'+name+'.qml')
        path.write_text(path.read_text().replace('import Quickshell.Services.Pipewire','import qs.preview').replace('import Quickshell.Services.UPower','import qs.preview'))
    audio_path=config/'modules/bar/popouts/Audio.qml'
    audio_path.write_text(audio_path.read_text().replace('?.id','?.nodeId').replace('modelData.id','modelData.nodeId'))
    write('components/effects/Colouriser.qml',production('components/effects/Colouriser.qml'))
    write('services/qmldir', 'module qs.services\nsingleton Colours 1.0 Colours.qml\nsingleton Nmcli 1.0 Nmcli.qml\nsingleton Visibilities 1.0 Visibilities.qml\n')
    write('services/Colours.qml', '''pragma Singleton
import QtQuick
import Quickshell
QtObject {
 property bool light: Quickshell.env("NETWORK_PREVIEW_LIGHT") === "1"
 property bool switchingTheme: true
 property QtObject palette: QtObject {
  property color m3onSurface: Colours.light ? "#202329" : "#f5f4f0"
  property color m3outline: Colours.light ? "#737780" : "#aaaeb7"
  property color m3onSurfaceVariant: m3outline
  property color m3surfaceContainer: Colours.light ? "#eeece9" : "#24272d"
  property color m3primary: "#287dff"
  property color m3onPrimary: "white"
  property color m3primaryContainer: "#233c60"
  property color m3onPrimaryContainer: "#dce9ff"
  property color m3surfaceContainerHigh: Colours.light ? "#e0e2e5" : "#333943"
  property color m3tertiary: Colours.light ? "#346485" : "#a3c4df"
  property color m3onError: Colours.light ? "white" : "#5f161c"
  property color m3secondary: m3primary
  property color m3onSecondary: "white"
  property color m3secondaryContainer: Colours.light ? "#dee2e8" : "#333943"
  property color m3onSecondaryContainer: m3onSurface
  property color m3error: Colours.light ? "#a52b32" : "#ffb4ab"
 }
 property QtObject tPalette: palette
 property color disabledContainer: Qt.alpha(palette.m3onSurface,0.1)
 property color disabledContent: Qt.alpha(palette.m3onSurface,0.38)
}''')
    write('services/Visibilities.qml', 'pragma Singleton\nimport QtQuick\nQtObject { function sidebarWidthFor(value) { return value; } }')
    write('services/Nmcli.qml', '''pragma Singleton
import QtQuick
QtObject {
 property bool wifiEnabled: true
 property bool scanning: false
 property string connectingSsid: ""
 property var pendingConnection: null
 property string vpnPendingConnection: ""
 property var active: ({ssid:"Heimnetz"})
 property var activeEthernet: ({iface:"enp5s0"})
 property var networks: [
  {ssid:"Heimnetz",active:true,strength:92,isSecure:true},
  {ssid:"Ein etwas längerer Netzwerkname",active:false,strength:75,isSecure:true},
  {ssid:"Gästenetz",active:false,strength:56,isSecure:true},
  {ssid:"Offenes WLAN",active:false,strength:35,isSecure:false}]
 property var ethernetDevices: [{iface:"enp5s0",connected:true,connection:"Ethernet"}]
 property var vpnConnections: [{name:"Tailscale",detail:"Verbunden",connected:true},{name:"Arbeitsnetz",detail:"Nicht verbunden",connected:false}]
 property var activeVpn: ({name:"Tailscale"})
 property var wirelessDeviceDetails: ({ipAddress:"192.0.2.10",subnet:"255.255.255.0",gateway:"192.0.2.1",dns:["192.0.2.1"],macAddress:"00:00:00:00:00:00"})
 property var ethernetDeviceDetails: wirelessDeviceDetails
 signal connectionSuccessful(string ssid)
 signal connectionFailed(string ssid)
 function enableWifi() {}
 function disconnectFromNetwork() {}
 function rescanWifi() {}
 function connectEthernet() {}
 function disconnectEthernet() {}
 function connectVpn() {}
 function disconnectVpn() {}
 function forgetNetwork() {}
}''')
    write('utils/qmldir', 'module qs.utils\nsingleton NetworkConnection 1.0 NetworkConnection.qml\n')
    write('utils/NetworkConnection.qml', '''pragma Singleton
import QtQuick
QtObject {
 property var passwordNetwork: ({ssid:"Ein etwas längerer Netzwerkname",isSecure:true,strength:80})
 function handleConnect() {}
 function connectWithPassword() {}
}''')
    write('modules/nexus/qmldir', 'module qs.modules.nexus\nsingleton WindowFactory 1.0 WindowFactory.qml\nsingleton PageRegistry 1.0 PageRegistry.qml\n')
    write('modules/nexus/WindowFactory.qml', 'pragma Singleton\nimport QtQuick\nQtObject { function create() {} }')
    write('modules/nexus/PageRegistry.qml', 'pragma Singleton\nimport QtQuick\nQtObject { function indexForKey(key) { return 0; } }')
    write('preview/qmldir', 'module qs.preview\nsingleton Bluetooth 1.0 Bluetooth.qml\nBluetoothDevice 1.0 BluetoothDevice.qml\nBluetoothDeviceState 1.0 BluetoothDeviceState.qml\n')
    write('preview/BluetoothDeviceState.qml', 'import QtQuick\nQtObject { enum State { Disconnected, Connected, Disconnecting, Connecting } }')
    write('preview/BluetoothDevice.qml', """import QtQuick
QtObject {
 property string name
 property string icon: "audio-headphones"
 property int state: BluetoothDeviceState.Disconnected
 property bool connected: state === BluetoothDeviceState.Connected
 property bool paired: true
 property bool bonded: true
 property bool batteryAvailable: false
 property real battery: 0
 function forget() {}
}""")
    write('preview/Bluetooth.qml', """pragma Singleton
import QtQuick
import Quickshell
QtObject {
 readonly property string fixtureState: Quickshell.env("BLUETOOTH_PREVIEW_STATE")
 property QtObject backendAdapter: QtObject {
  property bool enabled: Bluetooth.fixtureState !== "off"
  property bool discovering: Bluetooth.fixtureState === "searching"
 }
 property QtObject defaultAdapter: fixtureState === "missing" ? null : backendAdapter
 property list<BluetoothDevice> fixtureDevices: [
  BluetoothDevice { name:"Kopfhörer"; state:BluetoothDeviceState.Connected; batteryAvailable:true; battery:0.15 },
  BluetoothDevice { name:"Tastatur"; icon:"input-keyboard"; state:BluetoothDeviceState.Connected; batteryAvailable:true; battery:0.85 },
  BluetoothDevice { name:"Ein besonders langer Bluetooth-Gerätename"; icon:"input-mouse"; state:BluetoothDeviceState.Connecting },
  BluetoothDevice { name:"Lautsprecher"; icon:"audio-card"; paired:false; bonded:false }
 ]
 property var devices: ({values: ["off","empty","missing"].includes(fixtureState) ? [] : fixtureDevices})
}""")
    with (config / 'utils/qmldir').open('a') as file:
        file.write('singleton Icons 1.0 Icons.qml\n')
    icon_source = (shell / 'utils/Icons.qml').read_text()
    icon_functions = []
    for function_name in ['getBluetoothIcon', 'getBatteryIcon','getVolumeIcon','getMicVolumeIcon']:
        begin = icon_source.index('    function ' + function_name + '(')
        position = icon_source.index('{', begin) + 1
        depth = 1
        while depth:
            if icon_source[position] == '{': depth += 1
            elif icon_source[position] == '}': depth -= 1
            position += 1
        icon_functions.append(icon_source[begin:position])
    with (config/'utils/qmldir').open('a') as file:
        file.write('singleton Centering 1.0 Centering.qml\n')
    write('utils/Centering.qml',production('utils/Centering.qml'))
    write('utils/Icons.qml', 'pragma Singleton\nimport QtQuick\nQtObject {\n' + '\n'.join(icon_functions) + '\n}')
    with (config / 'services/qmldir').open('a') as file:
        file.write('singleton MenuStyle 1.0 MenuStyle.qml\nsingleton UpdateHub 1.0 UpdateHub.qml\nsingleton UpdateChecker 1.0 UpdateChecker.qml\nsingleton WinIcons 1.0 WinIcons.qml\n')
    write('services/MenuStyle.qml', production('services/MenuStyle.qml'))
    with (config/'services/qmldir').open('a') as file:
        file.write('singleton Time 1.0 Time.qml\n')
    write('services/Time.qml', 'pragma Singleton\nimport QtQuick\nQtObject { readonly property date date: new Date() }')
    write('services/UpdateChecker.qml', """pragma Singleton
import QtQuick
QtObject {
 property bool checkingUpdates: false
 property bool hasUpdate: true
 property double lastCheckMs: Date.now()
 property string currentVersion: "1.0"
 function checkUpdates() {}
}""")
    write('services/UpdateHub.qml', """pragma Singleton
import QtQuick
QtObject {
 property bool checking: false
 property bool hasErrors: false
 property int pendingCount: 0
 property var sources: [{key:"steam",name:"Steam"},{key:"steamGames",name:"Steam · Spiele"},{key:"battlenet",name:"Battle.net"},{key:"battlenetGames",name:"Battle.net · Spiele"},{key:"wowup",name:"WowUp"},{key:"artcraft",name:"ArtCraft Suite"}]
 property var status: ({steam:{checkedAt:Date.now()/1000},steamGames:{checkedAt:Date.now()/1000},battlenet:{checkedAt:Date.now()/1000},battlenetGames:{checkedAt:Date.now()/1000},wowup:{checkedAt:Date.now()/1000},artcraft:{checkedAt:Date.now()/1000}})
 function enabled(key) { return true; }
 function statusIcon(key) { return "check"; }
 function details(key) { return "Beispieldaten"; }
 function stamp(time) { return "gerade"; }
 function open(source) {}
 function refresh() {}
}""")
    import json
    icon_names = {}
    for app_id in ['steam','lab-wowup','lab-battlenet','ai.storyteller.artcraft-launcher']:
        for directory in [Path.home()/'.local/share/applications',Path.home()/'.local/share/flatpak/exports/share/applications',Path('/usr/share/applications')]:
            desktop = directory/(app_id+'.desktop')
            if desktop.exists():
                for line in desktop.read_text().splitlines():
                    if line.startswith('Icon='):
                        icon_names[app_id] = line[5:]; break
                break
    art_icon = Path.home()/'.local/share/flatpak/exports/share/icons/hicolor/256x256/apps/ai.storyteller.artcraft-launcher.png'
    if art_icon.exists(): icon_names['ai.storyteller.artcraft-launcher'] = str(art_icon)
    for app_id,icon_name in list(icon_names.items()):
        icon_file=Path.home()/'.local/share/icons/hicolor/256x256/apps'/(icon_name+'.png')
        if icon_file.exists(): icon_names[app_id]=str(icon_file)
    write('services/WinIcons.qml', 'pragma Singleton\nimport QtQuick\nimport Quickshell\nQtObject { property var iconNames: ' + json.dumps(icon_names) + '; function sourceFor(entry,appClass,icon,pid) { const name=entry?.icon || iconNames[icon] || icon; return name.startsWith("/") ? "file://"+name : Quickshell.iconPath(name,"application-x-executable"); } }')
    write('modules/bar/qmldir', 'module qs.modules.bar\nsingleton BarWidgets 1.0 BarWidgets.qml\n')
    write('modules/bar/BarWidgets.qml', 'pragma Singleton\nimport QtQuick\nQtObject { function setEnabled() {} }')
    with (config/'preview/qmldir').open('a') as file:
        file.write('PwNode 1.0 PwNode.qml\nsingleton UPower 1.0 UPower.qml\nsingleton PowerProfiles 1.0 PowerProfiles.qml\nPowerProfile 1.0 PowerProfile.qml\nPerformanceDegradationReason 1.0 PerformanceDegradationReason.qml\nUPowerDeviceState 1.0 UPowerDeviceState.qml\n')
    write('preview/PwNode.qml', """import QtQuick
QtObject {
 property int nodeId: 1
 property string description: "Lautsprecher"
 property string name: "speaker"
 property var properties: ({})
 property bool ready: true
 property QtObject audio: QtObject { property bool muted: false }
}""")
    write('preview/PowerProfile.qml','import QtQuick\nQtObject { enum Profile { PowerSaver, Balanced, Performance } }')
    write('preview/PerformanceDegradationReason.qml','import QtQuick\nQtObject { enum Reason { None, HighTemperature, LapDetected } }')
    write('preview/UPowerDeviceState.qml','import QtQuick\nQtObject { enum State { Unknown, Charging, Discharging, Empty, FullyCharged } }')
    write('preview/PowerProfiles.qml',"""pragma Singleton
import QtQuick
import Quickshell
QtObject {
 property int profile: PowerProfile.Balanced
 property int degradationReason: Quickshell.env("BATTERY_PREVIEW_STATE")==="degraded" ? PerformanceDegradationReason.HighTemperature : PerformanceDegradationReason.None
}""")
    write('preview/UPower.qml',"""pragma Singleton
import QtQuick
import Quickshell
QtObject {
 readonly property string fixture: Quickshell.env("BATTERY_PREVIEW_STATE")
 property bool onBattery: fixture !== "charging" && fixture !== "none"
 property QtObject displayDevice: QtObject {
  property bool isLaptopBattery: UPower.fixture !== "none"
  property real percentage: UPower.fixture === "low" ? 0.12 : 0.72
  property int state: UPower.onBattery ? UPowerDeviceState.Discharging : UPowerDeviceState.Charging
  property real timeToEmpty: 14400
  property real timeToFull: 2400
 }
}""")
    with (config/'services/qmldir').open('a') as file:
        file.write('singleton Units 1.0 Units.qml\nsingleton Audio 1.0 Audio.qml\nsingleton Players 1.0 Players.qml\nsingleton AppVisualiser 1.0 AppVisualiser.qml\n')
    write('services/Units.qml','pragma Singleton\nimport QtQuick\nQtObject { function formatDurationShort(seconds,fallback) { return seconds>0 ? \"4 h\" : fallback; } }')
    write('services/Players.qml','pragma Singleton\nimport QtQuick\nQtObject { property var active: null; property var list: [] }')
    write('services/AppVisualiser.qml','pragma Singleton\nimport QtQuick\nQtObject { function colorForApp(name) { return name === "Browser" ? "#ee9b53" : "#5b9cfa"; } }')
    write('services/Audio.qml',"""pragma Singleton
import QtQuick
import Quickshell
import qs.preview
QtObject {
 readonly property string fixture: Quickshell.env("AUDIO_PREVIEW_STATE")
 property PwNode outputDevice: PwNode { id:out; description:"Kopfhoerer mit laengerem Geraetenamen"; name:"headphones" }
 property PwNode otherDevice: PwNode { id:other; nodeId:2; description:"Monitor-Lautsprecher" }
 property PwNode inputDevice: PwNode { id:input; nodeId:3; description:"Mikrofon"; name:"mic" }
 property PwNode streamDevice: PwNode { id:app; nodeId:4; description:"Browser" }
 property var sinks: fixture === "empty" ? [] : [out,other]
 property var sources: fixture === "empty" ? [] : [input]
 property var sink: fixture === "empty" ? null : out
 property var source: fixture === "empty" ? null : input
 property var appStreams: fixture === "empty" ? [] : [app]
 property real volume: 0.64
 property real sourceVolume: 0.8
 property bool muted: fixture === "muted"
 property bool sourceMuted: false
 property QtObject cava: null
 signal streamsChanged()
 function getStreamName(node) { return node.description; }
 function getAppVolume(node) { return 0.55; }
 function getAppMuted(node) { return false; }
 function setAppVolume() {}
 function setAppMuted() {}
 function setAudioSink(node) { sink = node; }
 function setAudioSource(node) { source = node; }
 function setVolume(v) { volume = v; out.audio.muted = false; }
 function setSourceVolume(v) { sourceVolume = v; input.audio.muted = false; }
 function incrementVolume() {}
 function decrementVolume() {}
 function playEffectTick() {}
}""")
    with (config/'utils/qmldir').open('a') as file:
        file.write('singleton Units 1.0 Units.qml\n')
    write('utils/Units.qml','pragma Singleton\nimport QtQuick\nQtObject { function formatDurationShort(seconds,fallback) { return seconds>0 ? "4 h" : fallback; } }')
    # Use the production byte formatter for the traffic rows in both import scopes.
    write('services/Units.qml', production('services/Units.qml'))
    write('utils/Units.qml', production('services/Units.qml'))
    harness = Path(__file__).with_name('preview.qml').read_text()
    harness = harness.replace('interval: 2000;', 'interval: 500;').replace('fontScale: 1.15', 'fontScale: ' + str(args.font_scale))
    if args.source_root:
        harness = harness.replace('color: MenuStyle.surface', 'color: Colours.light ? \"#eff5f3f1\" : \"#ed1a1f26\"')
    if args.password_error:
        preparation = """        Timer {
            interval: 80; running: true
            onTriggered: {
                function prepare(item) {
                    if (item.objectName === "passwordContainer") item.passwordBuffer = "A".repeat(64);
                    if (item.hasError !== undefined) item.hasError = true;
                    for (const child of item.children ?? []) prepare(child);
                }
                prepare(loader.item);
            }
        }
"""
        harness = harness.replace('        Timer {\n            interval: 500;', preparation + '        Timer {\n            interval: 900;')
    if args.verify_audio:
        write('AudioControls.qml', (Path(__file__).resolve().parents[2]/'remaining-overlays/tests/AudioControls.qml').read_text())
        harness = harness.replace('interval: 500;', 'interval: 2200;')
        harness = harness.replace('        Timer {\n            interval: 2200;', '        AudioControls { audio: loader.item }\n        Timer {\n            interval: 2200;')
    write('shell.qml', harness)
    env = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software',
               QML2_IMPORT_PATH=str(Path.home()/'.local/lib/qt6/qml')+':'+str(config),
               NETWORK_PREVIEW_KIND=args.kind, NETWORK_PREVIEW_OUTPUT=str(args.out),
               NETWORK_PREVIEW_EXPANDED='1' if args.expanded else '0',
               NETWORK_PREVIEW_LIGHT='1' if args.light else '0',
               BLUETOOTH_PREVIEW_STATE=args.bluetooth_state,
               BATTERY_PREVIEW_STATE=args.battery_state,AUDIO_PREVIEW_STATE=args.audio_state,
               QS_DISABLE_CRASH_HANDLER='1', QS_NO_RELOAD_POPUP='1')
    if args.native:
        env['QT_QPA_PLATFORM']='wayland'
        env.pop('QT_QUICK_BACKEND',None)
    else:
        env.pop('WAYLAND_DISPLAY', None)
        env.pop('DISPLAY', None)
    try:
        process = subprocess.run(['quickshell', '-p', str(config)], env=env, capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired as error:
        output = (error.stdout or b'').decode() + (error.stderr or b'').decode()
        if args.out.exists() and '"saved":true' in output:
            print(output)
            print('Preview saved; native NetworkUsage shutdown timed out after rendering.')
            raise SystemExit(0)
        raise SystemExit(output)
    if not args.out.exists():
        raise SystemExit(process.stdout + process.stderr)
    if args.verify_audio and 'AUDIO_INTERACTIONS_PASS' not in process.stdout + process.stderr:
        raise SystemExit(process.stdout + process.stderr + '\nAudio interaction verification failed.')
    relevant = [line for line in (process.stdout + process.stderr).splitlines() if any(word in line for word in ['NETWORK_PREVIEW','AUDIO_INTERACTIONS_PASS','WARN','ERROR'])]
    print('\n'.join(relevant))
