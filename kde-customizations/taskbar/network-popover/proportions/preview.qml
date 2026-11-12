import QtQuick
import QtQuick.Window
import Quickshell
import Caelestia.Config
import qs.modules.bar.popouts as Popouts
import qs.services

ShellRoot {
    id: harness
    readonly property string mode: Quickshell.env("NETWORK_PREVIEW_KIND") || "network"
    readonly property string output: Quickshell.env("NETWORK_PREVIEW_OUTPUT") || "/tmp/network-render.png"
    Window {
        id: window
        visible: true
        width: harness.mode === "clock" ? 610 : 520
        height: surface.height
        color: "#17191d"
        Popouts.PopoutState { id: previewPopoutState; currentName: harness.mode; hasCurrent: true }
        Rectangle {
            id: surface
            width: window.width
            height: Math.ceil(loader.implicitHeight + 38)
            radius: 28
            color: MenuStyle.taskbarSurface
            border.width: 1
            border.color: MenuStyle.border
            Loader {
                id: loader
                x: (surface.width-width)/2; y: 19
                width: harness.mode === "clock" ? 571.55 : 483
                sourceComponent: harness.mode === "audio" ? audio : harness.mode === "battery" ? battery : harness.mode === "clock" ? calendar : harness.mode === "updates" ? updates : harness.mode === "bluetooth" ? bluetooth : harness.mode === "wirelesspassword" ? password : network
            }
            Component {
                id: network
                Popouts.Network {
                    popouts: previewPopoutState
                    view: harness.mode === "ethernet" ? "ethernet" : "wireless"
                    scaleOffset: 1.15
                    fontScale: 1.15
                    vpnExpanded: Quickshell.env("NETWORK_PREVIEW_EXPANDED") === "1"
                    detailsExpanded: vpnExpanded
                }
            }
            Component {
                id: audio
                Popouts.Audio {
                    popouts: previewPopoutState; scaleOffset:1.15; fontScale: 1.15
                    Component.onCompleted: if (Quickshell.env("NETWORK_PREVIEW_EXPANDED")==="1") {
                        _outputsOpen=true;
                        Qt.callLater(()=>{for(const child of children) if(child.expanded!==undefined) child.expanded=true;});
                    }
                }
            }
            Component {
                id: battery
                Popouts.Battery { popouts: previewPopoutState; scaleOffset:1.15; fontScale: 1.15 }
            }
            Component {
                id: calendar
                Popouts.CalendarPopout { color:"transparent"; popouts: previewPopoutState; scaleOffset:1.15; fontScale: 1.15 }
            }
            Component {
                id: updates
                Popouts.Updates {
                    popouts: previewPopoutState
                    scaleOffset: 1.15
                    fontScale: 1.15
                }
            }
            Component {
                id: bluetooth
                Popouts.Bluetooth {
                    popouts: previewPopoutState
                    scaleOffset: 1.15
                    fontScale: 1.15
                }
            }
            Component {
                id: password
                Popouts.WirelessPassword {
                    popouts: previewPopoutState
                    network: ({ssid:"Netzwerk-Vorschau mit längerem Namen", isSecure:true, strength:80})
                    scaleOffset: 1.15
                    fontScale: 1.15
                }
            }
        }
        Timer {
            interval: 2000; running: true
            onTriggered: { console.log("PREVIEW_GRAB_START",surface.width,surface.height,window.visible); surface.grabToImage(result => {
                const saved = result.saveToFile(harness.output);
                console.log("NETWORK_PREVIEW", JSON.stringify({saved:saved,mode:harness.mode,width:surface.width,height:surface.height,bodyPointSize:loader.item?.bodyPointSize,scale:loader.item?.scaleOffset,fontScale:loader.item?.fontScale,fontFamily:MenuStyle.fontFamily,layout:loader.item?.children.map(child=>({type:String(child).split("(")[0].replace(/_QMLTYPE_\d+/,""),x:child.x,y:child.y,width:child.width,height:child.height}))}));
                Qt.quit();
            }); }
        }
        Timer { interval: 12000; running:true; onTriggered: Qt.quit() }
    }
}
