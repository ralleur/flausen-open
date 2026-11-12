pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls as C
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import qs.components
import qs.modules.nexus.common

PageBase {
    id: root
    title: "Hermes"
    headerActions: [ExperimentalTag {}]
    subtitle: qsTranslate("Flausen", "Your assistant. Right in the Start menu.")
    property var saved: null
    property string selectedModel: ""
    property bool thinking: true
    property string chatgptAuth: "api"
    property string openaiApiKey: ""
    property string deepseekApiKey: ""
    property string endpointUrl: ""
    property string endpointModel: ""
    property string endpointApiKey: ""
    property bool codexLoggedIn: false
    property string loginCode: ""
    property string loginUrl: ""
    property bool loginComplete: false
    property string message: ""
    property bool failed: false
    property bool loading: true
    property bool received: false
    property var request: ({action:"read"})
    readonly property bool dirty: saved !== null && ((selectedModel === "local-endpoint" && (endpointUrl !== (saved.endpointUrl ?? "") || endpointModel !== (saved.endpointModel ?? "") || endpointApiKey.length>0)) || selectedModel !== saved.model || thinking !== saved.thinking || deepseekApiKey.length>0 || openaiApiKey.length>0 || chatgptAuth !== (saved.chatgptAuth ?? "api"))
    function load(): void { start({action:"read"}); }
    function start(value): void {
        if (transport.running) return;
        request=value; received=false; loading=true; message=""; failed=false;
        transport.running=true;
    }
    Component.onCompleted: load()
    property Process transport: Process {
        command: ["/usr/bin/python3", Quickshell.env("HOME")+"/.local/share/flausen-settings/hermes_settings.py"]
        stdinEnabled: true
        onStarted: {write(JSON.stringify(root.request)+"\n");}
        stdout: SplitParser {
            onRead: line => {
                try {
                    const data=JSON.parse(line);
                    root.received=true;
                    if(!data.ok) {root.failed=true;root.message=data.error;return;}
                    root.saved=data;root.selectedModel=data.model;root.thinking=data.thinking;root.chatgptAuth=data.chatgptAuth ?? "api";root.codexLoggedIn=data.codexLoggedIn ?? false;root.openaiApiKey="";
                    root.deepseekApiKey="";root.endpointApiKey="";
                    root.endpointUrl=data.endpointUrl ?? "";root.endpointModel=data.endpointModel ?? "";
                    if(root.request.action==="save") root.message="Saved. Start a new conversation in Hermes to use these changes.";
                } catch(error) {root.failed=true;root.message="Could not read the response from Hermes.";}
            }
        }
        onExited: {
            root.loading=false;
            if(!root.received) {root.failed=true;root.message="Hermes is unavailable. Check that the integration is installed.";}
            root.request={action:"read"};
        }
    }
    ColumnLayout {
        id: body
        width: parent.width
        spacing: 16
        AgentSafetyNotice {Layout.fillWidth:true}
        Repeater {
            model:[
                {title:qsTranslate("Flausen", "Cloud models"),description:qsTranslate("Flausen", "Processed by the provider · Internet connection required"),models:[
                    {key:"deepseek-flash",title:"DeepSeek Flash",subtitle:"DeepSeek",icon:"cloud",description:qsTranslate("Flausen", "Requests and content read by Hermes are sent to DeepSeek.")},
                    {key:"chatgpt",title:"ChatGPT",subtitle:"OpenAI · GPT-6.1 Sol",icon:"cloud",description:qsTranslate("Flausen", "Use an API key or sign in with your Codex subscription.")}]},
                {title:qsTranslate("Flausen", "Local models"),description:qsTranslate("Flausen", "Processed on your computer or local network"),models:[
                    {key:"lfm3:1.7b-hermes",title:"LFM3",subtitle:"CPU · Ollama",icon:"computer",description:qsTranslate("Flausen", "Light on resources. Less reliable for demanding tasks.")},
                    {key:"qwen3.8:27b-hermes",title:"Qwen 3.8 · 27B",subtitle:"NVIDIA GPU + RAM",icon:"memory",description:qsTranslate("Flausen", "90,112-token context. Starts on demand and releases GPU memory after inactivity.")},
                    {key:"local-endpoint",title:"Local endpoint",subtitle:qsTranslate("Flausen", "Local network"),icon:"lan",description:qsTranslate("Flausen", "Connect a model server through an OpenAI-compatible interface.")}]}
            ]
            ColumnLayout {
                id:group
                objectName:index===0 ? "hermesCloudModels" : "hermesLocalModels"
                required property var modelData
                required property int index
                Layout.fillWidth:true
                Layout.topMargin:index>0 ? 12 : 0
                spacing:10
                Text {text:group.modelData.title;font:FlausenStyle.typeface(19);color:FlausenStyle.text;Layout.fillWidth:true}
                Text {text:group.modelData.description;font:FlausenStyle.typeface(12);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
                GridLayout {
                    Layout.fillWidth:true
                    columns:width>480 ? 2 : 1
                    columnSpacing:12;rowSpacing:12
                    Repeater {
                        model:group.modelData.models
                        C.Button {
                            id: option
                            required property var modelData
                            Layout.fillWidth:true
                            Layout.preferredWidth:1
                            implicitHeight:Math.max(170, optionContent.implicitHeight+36)
                            enabled:root.saved!==null && !root.loading
                            text:modelData.title
                            checkable:true
                            checked:root.selectedModel===modelData.key
                            Accessible.name:modelData.title+". "+modelData.subtitle
                            onClicked:root.selectedModel=modelData.key
                            padding:18
                            background:Rectangle {radius:14;color:option.checked ? FlausenStyle.selected : FlausenStyle.card;border.width:option.checked || option.visualFocus ? 2 : 1;border.color:option.checked || option.visualFocus ? FlausenStyle.accent : FlausenStyle.line}
                            contentItem:ColumnLayout {
                                id:optionContent
                                spacing:8
                                RowLayout {
                                    Layout.fillWidth:true
                                    MaterialIcon {text:option.modelData.icon;color:option.checked ? FlausenStyle.accent : FlausenStyle.secondary;Layout.preferredWidth:28}
                                    Text {text:option.modelData.title;font:FlausenStyle.typeface(17);color:FlausenStyle.text;Layout.fillWidth:true;wrapMode:Text.WordWrap}
                                    MaterialIcon {text:option.checked ? "radio_button_checked" : "radio_button_unchecked";color:option.checked ? FlausenStyle.accent : FlausenStyle.secondary;Layout.preferredWidth:24}
                                }
                                Text {text:option.modelData.subtitle;font:FlausenStyle.typeface(12);color:FlausenStyle.secondary}
                                Text {text:option.modelData.description;font:FlausenStyle.typeface(13);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
                            }
                        }
                    }
                }
                Item {
                    id:accessArea
                    objectName:group.index===0 ? "hermesCloudAccess" : ""
                    visible:group.index===0
                    Layout.fillWidth:true
                    // Cancel the layout's spacing while collapsed; reveal the gap with the panel.
                    Layout.topMargin:-group.spacing
                    clip:true
                    readonly property bool deepseekSelected:root.selectedModel==="deepseek-flash"
                    readonly property bool openaiSelected:root.selectedModel==="chatgpt"
                    readonly property real targetHeight:deepseekSelected ? (deepseekPanel.item?.implicitHeight ?? 0)+10 : openaiSelected ? (openaiPanel.item?.implicitHeight ?? 0)+10 : 0
                    implicitHeight:targetHeight
                    Behavior on implicitHeight {NumberAnimation {duration:FlausenStyle.motionDuration>0 ? 220 : 0;easing.type:Easing.InOutCubic}}
                    Loader {
                        id:deepseekPanel
                        active:group.index===0
                        sourceComponent:root.deepseekAccess
                        width:parent.width;y:10
                        opacity:accessArea.deepseekSelected ? 1 : 0
                        visible:opacity>0
                        enabled:accessArea.deepseekSelected && !root.loading
                        Behavior on opacity {NumberAnimation {duration:FlausenStyle.motionDuration>0 ? 140 : 0}}
                    }
                    Loader {
                        id:openaiPanel
                        active:group.index===0
                        sourceComponent:root.openaiAccess
                        width:parent.width;y:10
                        opacity:accessArea.openaiSelected ? 1 : 0
                        visible:opacity>0
                        enabled:accessArea.openaiSelected && !root.loading
                        Behavior on opacity {NumberAnimation {duration:FlausenStyle.motionDuration>0 ? 140 : 0}}
                    }
                }
            }
        }
        Loader {
            Layout.fillWidth:true
            active:root.selectedModel==="local-endpoint"
            visible:active
            sourceComponent:root.endpointAccess
        }
        HermesVramCard {Layout.fillWidth:true;selectedModel:root.selectedModel;visible:root.selectedModel!=="local-endpoint"}
        Rectangle {
            visible:root.selectedModel!=="local-endpoint"
            Layout.fillWidth:true;implicitHeight:thinkingBody.implicitHeight+16
            radius:14;color:FlausenStyle.card;border.width:1;border.color:FlausenStyle.line
            ColumnLayout {
                id:thinkingBody
                anchors {left:parent.left;right:parent.right;top:parent.top;topMargin:4;bottomMargin:12}
                spacing:0
                FlausenSwitch {text:qsTranslate("Flausen", "Thinking mode");checked:root.thinking;enabled:root.saved!==null && !root.loading && root.selectedModel!=="local-endpoint";Layout.fillWidth:true;onToggled:root.thinking=checked}
                Text {text:root.selectedModel==="local-endpoint" ? qsTranslate("Flausen", "Configure thinking mode on the model server.") : qsTranslate("Flausen", "More time to think through complex tasks. Responses may take longer.");Layout.fillWidth:true;Layout.leftMargin:16;Layout.rightMargin:16;wrapMode:Text.WordWrap;font:FlausenStyle.typeface(13);color:FlausenStyle.secondary}
            }
        }
        Text {text:qsTranslate("Flausen", "System actions");font:FlausenStyle.typeface(17);color:FlausenStyle.text;Layout.topMargin:8}
        Text {text:qsTranslate("Flausen", "Hermes can read system information, open apps and change the volume. Approve each proposed shell command in the chat.");font:FlausenStyle.typeface(14);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
        RowLayout {
            Layout.fillWidth:true;Layout.topMargin:8
            Text {text:root.loading ? qsTranslate("Flausen", "Loading …") : root.dirty ? qsTranslate("Flausen", "Unsaved changes") : qsTranslate("Flausen", "Changes take effect in a new conversation.");Layout.fillWidth:true;wrapMode:Text.WordWrap;font:FlausenStyle.typeface(12);color:FlausenStyle.secondary}
            FlausenButton {text:qsTranslate("Flausen", "Reset");enabled:!root.loading;onClicked:root.load()}
            FlausenButton {text:qsTranslate("Flausen", "Apply");enabled:root.dirty && !root.loading;onClicked:root.start({action:"save",revision:root.saved.revision,model:root.selectedModel,thinking:root.thinking,apiKey:root.deepseekApiKey,chatgptAuth:root.chatgptAuth,openaiApiKey:root.openaiApiKey,endpointUrl:root.endpointUrl,endpointModel:root.endpointModel,endpointApiKey:root.endpointApiKey})}
        }
        Text {visible:root.message.length>0;text:qsTranslate("Flausen", root.message);font:FlausenStyle.typeface(13);color:root.failed ? "#f08080" : FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
        Item {Layout.preferredHeight:8}
    }
    property Process loginProcess: Process {
        command:[Quickshell.env("HOME")+"/.local/share/ralleur-hermes/venv/bin/python",Quickshell.env("HOME")+"/.local/share/flausen-settings/openai_auth.py","login"]
        stdout:SplitParser {onRead:line=>{
            try {
                const data=JSON.parse(line);
                if(data.event==="device") {root.loginCode=data.code;root.loginUrl=data.url;Qt.openUrlExternally(data.url);}
                else if(data.event==="complete" && data.ok) {root.loginComplete=true;root.codexLoggedIn=true;root.loginCode="";root.message="Codex subscription connected. Apply your selection for a new conversation.";}
                else if(data.event==="error") {root.failed=true;root.message=data.error;}
            } catch(error) {root.failed=true;root.message="Could not read the sign-in response.";}
        }}
        onExited: {root.loginCode="";if(!root.loginComplete && !root.failed)root.message="Sign-in ended. You can try again.";}
    }
    property Component endpointAccess: Component {
        C.Pane {
            id:endpointPane
            objectName:"hermesEndpointPanel"
            enabled:!root.loading
            property KcmSkin accessSkin: KcmSkin {targetItem:endpointPane;moduleKey:"hermes-local-endpoint"}
            padding:18
            background:Rectangle {radius:14;color:FlausenStyle.card;border.width:1;border.color:FlausenStyle.line}
            contentItem:ColumnLayout {
                spacing:12
                Text {text:"Local endpoint";font:FlausenStyle.typeface(17);color:FlausenStyle.text;Layout.fillWidth:true}
                Text {text:qsTranslate("Flausen", "OpenAI-compatible base URL including the API path, usually /v1. The model runs on the specified server.");font:FlausenStyle.typeface(13);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
                C.Label {text:qsTranslate("Flausen", "Base URL")}
                C.TextField {Layout.fillWidth:true;text:root.endpointUrl;onTextEdited:root.endpointUrl=text;placeholderText:"http://192.168.1.20:1234/v1";Accessible.name:qsTranslate("Flausen", "Endpoint base URL");selectByMouse:true}
                C.Label {text:qsTranslate("Flausen", "Model ID")}
                C.TextField {Layout.fillWidth:true;text:root.endpointModel;onTextEdited:root.endpointModel=text;placeholderText:qsTranslate("Flausen", "Model ID reported by the server");Accessible.name:qsTranslate("Flausen", "Endpoint model ID");selectByMouse:true}
                C.Label {text:qsTranslate("Flausen", "API key (optional)")}
                C.TextField {Layout.fillWidth:true;text:root.endpointApiKey;onTextEdited:root.endpointApiKey=text;echoMode:TextInput.Password;placeholderText:root.saved?.endpointKeyConfigured ? qsTranslate("Flausen", "Key saved · leave blank to keep it") : qsTranslate("Flausen", "Only if the server requires a key");Accessible.name:qsTranslate("Flausen", "Endpoint API key");selectByMouse:true}
                Text {text:qsTranslate("Flausen", "The server must support Chat Completions and tool calls for Hermes. Configure thinking mode on the server. Changes take effect in a new conversation.");font:FlausenStyle.typeface(12);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
            }
        }
    }
    property Component deepseekAccess: Component {
        C.Pane {
            id:credentials
            property KcmSkin accessSkin: KcmSkin {targetItem:credentials;moduleKey:"hermes-deepseek"}
            padding:18
            background:Rectangle {radius:14;color:FlausenStyle.card;border.width:1;border.color:FlausenStyle.line}
            contentItem:ColumnLayout {
                spacing:12
                Text {text:qsTranslate("Flausen", "DeepSeek access");font:FlausenStyle.typeface(17);color:FlausenStyle.text;Layout.fillWidth:true}
                Text {text:root.saved?.keyConfigured ? qsTranslate("Flausen", "API key saved") : qsTranslate("Flausen", "No API key saved yet");font:FlausenStyle.typeface(14);color:FlausenStyle.text;Layout.fillWidth:true;wrapMode:Text.WordWrap}
                C.TextField {Layout.fillWidth:true;text:root.deepseekApiKey;onTextEdited:root.deepseekApiKey=text;echoMode:TextInput.Password;placeholderText:root.saved?.keyConfigured ? qsTranslate("Flausen", "Enter a new API key …") : qsTranslate("Flausen", "Enter an API key …");Accessible.name:qsTranslate("Flausen", "DeepSeek API key");selectByMouse:true}
                Text {text:qsTranslate("Flausen", "Leave blank to keep the existing key. It is stored only in your private Hermes profile.");font:FlausenStyle.typeface(12);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
            }
        }
    }
    property Component openaiAccess: Component {
        C.Pane {
            id:openaiPane
            property KcmSkin accessSkin: KcmSkin {targetItem:openaiPane;moduleKey:"hermes-openai"}
            padding:18
            background:Rectangle {radius:14;color:FlausenStyle.card;border.width:1;border.color:FlausenStyle.line}
            contentItem:ColumnLayout {
                spacing:12
                Text {text:qsTranslate("Flausen", "ChatGPT access");font:FlausenStyle.typeface(17);color:FlausenStyle.text;Layout.fillWidth:true}
                RowLayout {
                    Layout.fillWidth:true
                    C.RadioButton {implicitHeight:44;padding:10;text:qsTranslate("Flausen", "API key");checked:root.chatgptAuth==="api";onClicked:root.chatgptAuth="api"}
                    C.RadioButton {implicitHeight:44;padding:10;text:qsTranslate("Flausen", "Codex subscription");checked:root.chatgptAuth==="codex";onClicked:root.chatgptAuth="codex"}
                }
                ColumnLayout {
                    visible:root.chatgptAuth==="api";Layout.fillWidth:true;spacing:10
                    Text {text:qsTranslate("Flausen", "Billed to your OpenAI API account, separately from your Codex subscription.");font:FlausenStyle.typeface(13);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
                    Text {text:root.saved?.openaiKeyConfigured ? qsTranslate("Flausen", "OpenAI API key saved") : qsTranslate("Flausen", "No OpenAI API key saved yet");font:FlausenStyle.typeface(13);color:FlausenStyle.text;Layout.fillWidth:true;wrapMode:Text.WordWrap}
                    C.TextField {Layout.fillWidth:true;text:root.openaiApiKey;onTextEdited:root.openaiApiKey=text;echoMode:TextInput.Password;placeholderText:qsTranslate("Flausen", "Enter an OpenAI API key …");Accessible.name:qsTranslate("Flausen", "OpenAI API key");selectByMouse:true}
                    Text {text:qsTranslate("Flausen", "Leave blank to keep the existing key. It is stored only in your private Hermes profile.");font:FlausenStyle.typeface(12);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
                }
                ColumnLayout {
                    visible:root.chatgptAuth==="codex";Layout.fillWidth:true;spacing:10
                    Text {text:qsTranslate("Flausen", "Uses the Codex access and usage limits of your ChatGPT subscription. A suitable plan and model access are required.");font:FlausenStyle.typeface(13);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
                    Text {text:root.codexLoggedIn ? qsTranslate("Flausen", "Codex subscription connected to Hermes") : qsTranslate("Flausen", "Not connected to Hermes yet");font:FlausenStyle.typeface(13);color:FlausenStyle.text;Layout.fillWidth:true}
                    FlausenButton {text:root.loginProcess.running ? qsTranslate("Flausen", "Cancel sign-in") : root.codexLoggedIn ? qsTranslate("Flausen", "Sign in again") : qsTranslate("Flausen", "Sign in with a Codex subscription");onClicked:{if(root.loginProcess.running)root.loginProcess.running=false;else {root.loginComplete=false;root.failed=false;root.message="";root.loginCode="";root.loginProcess.running=true;}}}
                    Text {visible:root.loginCode.length>0;text:qsTranslate("Flausen", "Enter this code in the browser:");font:FlausenStyle.typeface(13);color:FlausenStyle.text;Layout.fillWidth:true;wrapMode:Text.WordWrap}
                    C.TextField {visible:root.loginCode.length>0;text:root.loginCode;readOnly:true;selectByMouse:true;Accessible.name:qsTranslate("Flausen", "Codex sign-in code");Layout.fillWidth:true}
                    FlausenButton {visible:root.loginCode.length>0;text:qsTranslate("Flausen", "Open sign-in page");onClicked:Qt.openUrlExternally(root.loginUrl)}
                    Text {text:qsTranslate("Flausen", "Hermes uses a separate sign-in. Your current Codex session stays active.");font:FlausenStyle.typeface(12);color:FlausenStyle.secondary;Layout.fillWidth:true;wrapMode:Text.WordWrap}
                }
            }
        }
    }

}
