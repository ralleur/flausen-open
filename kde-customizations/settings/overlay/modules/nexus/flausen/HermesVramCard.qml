pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls as C
import QtQuick.Layouts
import Quickshell
import Quickshell.Io

C.Pane {
    id: root
    required property string selectedModel
    property var snapshot: null
    property bool preview: true
    property int contextTokens: 65536
    onContextTokensChanged:contextSelect.currentIndex=Math.max(0,(local?.contexts ?? []).findIndex(item=>item.tokens===contextTokens))
    property string error: ""
    property bool received: false
    readonly property var adapters: snapshot?.gpus ?? []
    readonly property var gpu: adapters[gpuSelect.currentIndex] ?? adapters[0] ?? null
    readonly property var local: snapshot?.locals?.[selectedModel] ?? null
    property string previewModelName: ""
    onLocalChanged: {
        const name=local?.name ?? "";
        if(name!==previewModelName) {previewModelName=name;contextTokens=local?.contextTokens ?? 65536;}
    }
    readonly property var context: local?.contexts[contextSelect.currentIndex] ?? null
    readonly property bool canPreview: local !== null && context?.bytes !== null && context?.bytes !== undefined && (local.kind !== "qwen" || gpu?.id?.startsWith("GPU-"))
    readonly property bool showingPreview: preview && canPreview
    readonly property real capacity: gpu?.total ?? 0
    readonly property real modelBytes: showingPreview ? (context.modelBytes ?? local.modelBytes) : 0
    readonly property real contextBytes: showingPreview ? context.bytes : 0
    readonly property real runtimeBytes: showingPreview ? (context.runtimeBytes ?? 0) : 0
    // Loaded allocations cannot reliably be separated from desktop use per GPU.
    // Omit the measured total in that scenario to avoid counting models twice.
    readonly property bool includeCurrent: !showingPreview || snapshot?.loadedVram === 0
    readonly property real occupiedBytes: includeCurrent ? (gpu?.used ?? 0) : 0
    readonly property real requestedBytes: modelBytes+contextBytes+runtimeBytes+occupiedBytes
    readonly property real remaining: Math.max(0,capacity-requestedBytes)
    function gib(bytes): string {return (bytes/1073741824).toLocaleString(Qt.locale(),"f",2)+" GiB";}
    function share(bytes): string {return capacity>0 ? (100*bytes/capacity).toLocaleString(Qt.locale(),"f",1)+" %" : "–";}
    function refresh(): void {if(!reader.running) {received=false;reader.running=true;}}
    Component.onCompleted: refresh()
    padding:18
    background:Rectangle {radius:14;color:FlausenStyle.card;border.width:1;border.color:FlausenStyle.line}
    property Process reader: Process {
        command:["/usr/bin/python3",Quickshell.env("HOME")+"/.local/share/flausen-settings/hermes_settings.py"]
        stdinEnabled:true
        onStarted:write(JSON.stringify({action:"resources"})+"\n")
        stdout:SplitParser {onRead:line=>{
            try {
                const data=JSON.parse(line);
                root.received=true;
                if(data.ok) {root.snapshot=data;root.error="";}
                else root.error=qsTranslate("Flausen", "Could not read VRAM data.");
            } catch(e) {root.error=qsTranslate("Flausen", "Could not read VRAM data.");}
        }}
        onExited:if(!root.received)root.error=qsTranslate("Flausen", "VRAM data is currently unavailable.")
    }
    property KcmSkin gpuSkin: KcmSkin {targetItem:gpuSelect}
    property KcmSkin contextSkin: KcmSkin {targetItem:contextSelect}
    property Timer polling: Timer {interval:10000;running:root.visible;repeat:true;onTriggered:root.refresh()}
    contentItem:ColumnLayout {
        spacing:14
        RowLayout {
            Layout.fillWidth:true
            Text {text:root.showingPreview ? qsTranslate("Flausen", "GPU memory · Preview") : qsTranslate("Flausen", "GPU memory");color:FlausenStyle.text;font:FlausenStyle.typeface(17);Layout.fillWidth:true}
            Text {text:root.capacity>0 ? root.gib(root.capacity)+" · 100 %" : qsTranslate("Flausen", "Unavailable");color:FlausenStyle.secondary;font:FlausenStyle.typeface(12)}
        }
        Text {visible:root.adapters.length<=1;text:root.gpu?.name ?? (root.snapshot ? qsTranslate("Flausen", "No supported GPU with dedicated VRAM detected.") : qsTranslate("Flausen", "Detecting GPU …"));font:FlausenStyle.typeface(13);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
        C.ComboBox {id:gpuSelect;visible:root.adapters.length>1;model:root.adapters;textRole:"name";Layout.fillWidth:true;Accessible.name:qsTranslate("Flausen", "Graphics card for VRAM display")}
        Rectangle {
            id:track
            visible:root.capacity>0
            Layout.fillWidth:true;implicitHeight:24
            radius:6;color:FlausenStyle.line
            Accessible.role:Accessible.ProgressBar
            Accessible.name:qsTranslate("Flausen", "GPU memory. ")+(root.showingPreview ? qsTranslate("Flausen", "GPU preview. ") : qsTranslate("Flausen", "Current usage. "))+qsTranslate("Flausen", "Model ")+root.gib(root.modelBytes)+qsTranslate("Flausen", ", context ")+root.gib(root.contextBytes)+qsTranslate("Flausen", ", runtime and reserve ")+root.gib(root.runtimeBytes)+", other usage "+root.gib(root.occupiedBytes)+", remaining "+root.gib(root.remaining)
            Item {
                anchors.fill:parent;anchors.margins:3;clip:true
                Rectangle {id:weights;width:parent.width*Math.min(1,root.modelBytes/Math.max(1,root.capacity));height:parent.height;color:FlausenStyle.modelBlue}
                Rectangle {id:cache;x:weights.width;width:parent.width*Math.min(Math.max(0,1-root.modelBytes/Math.max(1,root.capacity)),root.contextBytes/Math.max(1,root.capacity));height:parent.height;color:FlausenStyle.contextYellow}
                Rectangle {id:buffers;x:cache.x+cache.width;width:parent.width*Math.min(Math.max(0,1-(root.modelBytes+root.contextBytes)/Math.max(1,root.capacity)),root.runtimeBytes/Math.max(1,root.capacity));height:parent.height;color:FlausenStyle.secondary}
                Rectangle {x:buffers.x+buffers.width;width:parent.width*Math.min(Math.max(0,1-(root.modelBytes+root.contextBytes+root.runtimeBytes)/Math.max(1,root.capacity)),root.occupiedBytes/Math.max(1,root.capacity));height:parent.height;color:FlausenStyle.secondary;opacity:0.5}
            }
        }
        Flow {
            Layout.fillWidth:true
            spacing:18
            Repeater {
                model:(root.showingPreview ? [{label:qsTranslate("Flausen", "Model (approx.)"),bytes:root.modelBytes,color:FlausenStyle.modelBlue},{label:qsTranslate("Flausen", "Context (approx.)"),bytes:root.contextBytes,color:FlausenStyle.contextYellow}].concat(root.runtimeBytes>0 ? [{label:qsTranslate("Flausen", "Runtime & reserve"),bytes:root.runtimeBytes,color:FlausenStyle.secondary}] : []) : []).concat(root.includeCurrent ? [{label:qsTranslate("Flausen", "Currently used"),bytes:root.occupiedBytes,color:FlausenStyle.secondary}] : [])
                Row {
                    required property var modelData
                    spacing:7
                    Rectangle {width:9;height:9;radius:3;color:parent.modelData.color;anchors.verticalCenter:parent.verticalCenter}
                    Text {text:parent.modelData.label+" · "+root.gib(parent.modelData.bytes);font:FlausenStyle.typeface(12);color:FlausenStyle.text}
                }
            }
        }
        Text {
            text:root.showingPreview ? (root.requestedBytes>root.capacity ? qsTranslate("Flausen", "Capacity exceeded: ")+root.gib(root.requestedBytes-root.capacity)+qsTranslate("Flausen", " short in this estimate.") : root.gib(root.remaining)+" remaining in this estimate"+(root.includeCurrent ? qsTranslate("Flausen", " for games and other GPU tasks.") : qsTranslate("Flausen", " before desktop, games and other GPU tasks."))) : root.gib(root.remaining)+" currently available for games and other GPU tasks."
            visible:root.capacity>0
            font:FlausenStyle.typeface(14);color:FlausenStyle.text;Layout.fillWidth:true;wrapMode:Text.WordWrap
        }
        Text {
            text:(root.selectedModel==="deepseek-flash" || root.selectedModel==="chatgpt") ? qsTranslate("Flausen", "The selected cloud model uses no local VRAM for its model or context.") : root.selectedModel==="qwen3.8:27b-hermes" ? qsTranslate("Flausen", "Qwen uses GPU memory and RAM. The preview accounts for the GPU portion of the configured profile; the remaining model layers use RAM.") : root.local?.cpuOnly ? qsTranslate("Flausen", "LFM3 is configured for the CPU: model and context use RAM instead of VRAM.") : qsTranslate("Flausen", "Total usage is measured. Model and context portions can only be estimated in the preview.")
            font:FlausenStyle.typeface(12);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap
        }
        Rectangle {Layout.fillWidth:true;implicitHeight:1;color:FlausenStyle.line}
        FlausenSwitch {text:qsTranslate("Flausen", "GPU preview")+(root.local ? " · "+root.local.label : "");checked:root.showingPreview;enabled:root.canPreview && root.capacity>0;Layout.fillWidth:true;leftPadding:0;rightPadding:0;implicitHeight:36;onToggled:root.preview=checked}
        RowLayout {
            visible:root.showingPreview
            Layout.fillWidth:true
            Text {text:qsTranslate("Flausen", "Context budget");font:FlausenStyle.typeface(13);color:FlausenStyle.text;Layout.fillWidth:true}
            C.ComboBox {
                id:contextSelect
                model:root.local?.contexts ?? []
                textRole:"tokens"
                displayText:Number(model[currentIndex]?.tokens ?? 0).toLocaleString(Qt.locale(),"f",0)+qsTranslate("Flausen", " tokens")
                Layout.preferredWidth:180
                Accessible.name:qsTranslate("Flausen", "Context size for GPU preview")
                onModelChanged:currentIndex=Math.max(0,model.findIndex(item=>item.tokens===root.contextTokens))
                onActivated:root.contextTokens=model[currentIndex].tokens
            }
        }
        Text {
            text:root.showingPreview ? (root.local.kind==="qwen" ? qsTranslate("Flausen", "Estimate for ")+root.local.gpuLayers+qsTranslate("Flausen", " GPU layers including context, runtime buffers and reserve. Remaining space is estimated. The preview does not change settings.") : qsTranslate("Flausen", "Full GPU estimate: model size from the file, context as a conservative FP16 budget. Additional runtime buffers are required. The preview does not change settings."))+(root.includeCurrent ? "" : qsTranslate("Flausen", " Currently measured usage: ")+root.gib(root.gpu?.used ?? 0)+"; it may already include models and is not added again here.") : (root.selectedModel==="deepseek-flash" || root.selectedModel==="chatgpt") ? qsTranslate("Flausen", "No local GPU preview is needed for the cloud model.") : root.local?.kind==="qwen" && !root.canPreview ? qsTranslate("Flausen", "Select the NVIDIA graphics card configured for Qwen.") : qsTranslate("Flausen", "The preview estimates VRAM requirements for the selected local model at different context sizes.")
            font:FlausenStyle.typeface(12);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap
        }
        Text {visible:root.error.length>0;text:root.error;color:FlausenStyle.secondary;font:FlausenStyle.typeface(12);Layout.fillWidth:true;wrapMode:Text.WordWrap}
    }
}
