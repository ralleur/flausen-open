pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Caelestia.Config
import qs.components
import qs.services
import qs.modules.launcher.services
import qs.modules.bar as Bar

Rectangle {
    id: root

    required property var visibilities
    property bool expanded: false
    property bool busy: false
    property bool ready: false
    property string modelLabel: qsTr("Preparing connection …")
    property bool cloudModel: false
    property bool stopping: false
    property var pendingApproval: null
    property bool approvalSent: false
    property string pendingPrompt: ""
    property string statusText: qsTr("Ready for your next idea")
    property int answerIndex: -1
    property real reveal: expanded ? 1 : 0
    readonly property color accent: Colours.palette.m3primary
    readonly property color foreground: Colours.palette.m3onSurface
    readonly property color muted: Colours.palette.m3onSurfaceVariant
    readonly property bool hasConversation: messages.count > 0
    signal back()

    x: 26 * (1 - reveal)
    y: 26 * (1 - reveal)
    width: parent.width - 52 * (1 - reveal)
    height: 56 + (parent.height - 56) * reveal
    radius: 17 + 7 * reveal
    color: "transparent"
    visible: reveal > 0
    clip: true
    z: 20
    focus: expanded

    // Shared smoke tint and rim; retain the chat geometry.
    Bar.GlassSurface {
        anchors.fill: parent
        radius: root.radius
        smoke: true
    }

    Behavior on reveal { NumberAnimation { duration: 360; easing.type: Easing.OutCubic } }
    onExpandedChanged: if (expanded) {
        if (!bridge.running) bridge.running = true;
        Qt.callLater(() => composer.forceActiveFocus());
    }
    Keys.onEscapePressed: root.back()
    Shortcut { sequence: "Ctrl+K"; enabled: root.expanded && root.visibilities.launcher; onActivated: composer.forceActiveFocus() }

    function append(role, text, toolId, detail, state) {
        messages.append({speaker: role, body: text || "", toolId: toolId || "", detail: detail || "", state: state || "", summary: ""});
        followTail();
    }
    function focusComposer() { Qt.callLater(() => composer.forceActiveFocus()); }
    function stop() {
        root.stopping = true;
        root.pendingApproval = null;
        root.statusText = qsTr("Cancelling …");
        if (!root.ready) {
            root.pendingPrompt = "";
            root.receive({event: "cancelled"});
        } else {
            bridge.write(JSON.stringify({action: "cancel"}) + "\n");
            stopDeadline.restart();
        }
    }
    function followTail() { if (followEnd.checked) Qt.callLater(() => transcript.positionViewAtEnd()); }
    function answer(text, replace) {
        if (root.answerIndex < 0) {
            append("assistant", "", "", "", "");
            root.answerIndex = messages.count - 1;
        }
        messages.setProperty(root.answerIndex, "body", replace ? text : messages.get(root.answerIndex).body + text);
        followTail();
    }
    function send(text) {
        const prompt = text.trim();
        if (!prompt || root.busy) return;
        if (prompt.length > 6000) { root.statusText = qsTr("Please enter no more than 6,000 characters."); return; }
        root.expanded = true;
        root.busy = true;
        root.stopping = false;
        root.answerIndex = -1;
        root.statusText = root.ready ? qsTr("Hermes is working …") : qsTr("Starting Hermes …");
        append("user", prompt);
        composer.text = "";
        followEnd.checked = true;
        if (root.ready) bridge.write(JSON.stringify({action: "prompt", text: prompt}) + "\n");
        else { root.pendingPrompt = prompt; bridge.running = true; }
    }
    function receive(event) {
        switch (event.event) {
        case "approval":
            root.pendingApproval = event;
            root.approvalSent = false;
            root.statusText = qsTr("Waiting for your approval");
            break;
        case "approval_resolved":
            if (root.pendingApproval?.id === event.id) root.pendingApproval = null;
            root.statusText = qsTr("Hermes is working …");
            break;
        case "ready":
            root.ready = true;
            root.modelLabel = event.model === "gpt-6.1-sol" ? "ChatGPT · GPT-6.1 Sol" : event.model === "local-endpoint" ? "Local endpoint" : event.model === "deepseek-flash" ? "DeepSeek Flash" : event.model === "qwen3.8:27b-hermes" ? "Qwen 3.8 · 27B" : event.model || qsTr("Local model");
            root.cloudModel = event.location === "cloud";
            if (root.pendingPrompt) {
                bridge.write(JSON.stringify({action: "prompt", text: root.pendingPrompt}) + "\n");
                root.pendingPrompt = "";
            }
            break;
        case "status": root.statusText = event.text; break;
        case "delta": answer(event.text, false); break;
        case "tool_start":
            root.answerIndex = -1;
            const labels = {system_status: "Read system status", desktop_status: "Check desktop", autostart_status: "Check startup apps", inspect_system: qsTranslate("Flausen", "Inspect system"), system_command: "Run system task", read_file: qsTranslate("Flausen", "Read configuration"), search_files: qsTranslate("Flausen", "Search files"), open_app: qsTranslate("Flausen", "Open app"), set_volume: qsTranslate("Flausen", "Change volume")};
            append("tool", labels[event.name] || event.name, event.id, JSON.stringify(event.arguments, null, 2), "running");
            root.statusText = labels[event.name] || qsTr("Running action …");
            break;
        case "tool_end":
            for (let i = 0; i < messages.count; ++i) {
                if (messages.get(i).toolId === event.id) {
                    let parsedResult = null;
                    try { parsedResult = JSON.parse(event.result); } catch (error) {}
                    const failed = !!parsedResult?.error || parsedResult?.success === false || parsedResult?.not_found === true || (parsedResult?.exit_code !== undefined && parsedResult.exit_code !== null && parsedResult.exit_code !== 0);
                    messages.setProperty(i, "state", failed ? "error" : "done");
                    messages.setProperty(i, "detail", messages.get(i).detail + "\n\n" + event.result);
                    try {
                        const result = JSON.parse(event.result);
                        let summary = "";
                        if (result.error) summary = String(result.error);
                        else if (failed && result.note) summary = String(result.note);
                        else if (result.ram_available_gib !== undefined)
                            summary = result.ram_available_gib + qsTranslate("Flausen", " GiB available · ") + result.ram_total_gib + qsTranslate("Flausen", " GiB total");
                        else if (result.volume_percent !== undefined)
                            summary = qsTr("Volume: ") + result.volume_percent + "% · " + (result.muted ? qsTr("Muted") : result.audio_output);
                        else if (result.launched) summary = qsTr("Opened: ") + result.launched;
                        else if (result.volume) summary = String(result.volume);
                        else if (result.desktop_entries) {
                            const entries = result.desktop_entries.map(e => e.name + " · " + e.status);
                            const units = result.enabled_user_units.map(e => e.name);
                            const scripts = result.session_scripts.map(e => e.name);
                            summary = qsTr("Apps at sign-in:\n") + (entries.join("\n") || qsTr("No entries"));
                            if (units.length) summary += qsTr("\n\nEnabled user services / timers:\n") + units.join("\n");
                            if (scripts.length) summary += qsTr("\n\nSession scripts:\n") + scripts.join("\n");
                            if (result.errors?.length) summary += "\n\n" + result.errors.join("\n");
                            summary += "\n\n" + result.note;
                        } else if (result.output || result.content) {
                            const output = String(result.output || result.content);
                            summary = output.slice(0, 1800) + (output.length > 1800 ? qsTr("\n… full output in details") : "");
                        } else if (Array.isArray(result.files)) summary = result.files.slice(0, 30).join("\n");
                        if (result.approved_by_user === true) summary = qsTr("Approved by you\n") + summary;
                        messages.setProperty(i, "summary", summary);
                    } catch (error) { /* The raw result remains available in the details. */ }
                    break;
                }
            }
            root.statusText = qsTr("Hermes is preparing the answer …");
            break;
        case "done":
            root.pendingApproval = null;
            stopDeadline.stop();
            root.stopping = false;
            answer(event.text, true);
            root.busy = false;
            root.statusText = root.cloudModel ? qsTr("Completed · DeepSeek Flash") : qsTr("Completed · locally on your computer");
            break;
        case "error":
            root.pendingApproval = null;
            stopDeadline.stop();
            root.stopping = false;
            append("error", event.text);
            root.busy = false;
            root.pendingPrompt = "";
            root.statusText = qsTr("Request failed · You can try again");
            break;
        case "cancelled":
            root.pendingApproval = null;
            root.stopping = false;
            stopDeadline.stop();
            append("notice", qsTr("Request cancelled. Actions already completed remain in effect."));
            for (let j = 0; j < messages.count; ++j)
                if (messages.get(j).state === "running") messages.setProperty(j, "state", "cancelled");
            root.busy = false;
            root.statusText = qsTr("Cancelled");
            break;
        case "reset": root.statusText = qsTr("Ready for your next idea"); break;
        }
    }

    Process {
        id: bridge
        command: [Quickshell.env("HOME") + "/.local/bin/ralleur-hermes"]
        stdinEnabled: true
        stdout: SplitParser {
            onRead: line => {
                try { root.receive(JSON.parse(line)); }
                catch (error) { console.warn("Hermes protocol:", String(error)); }
            }
        }
        stderr: SplitParser { onRead: line => console.debug("Hermes:", line) }
        onExited: (code, status) => {
            root.ready = false;
            if (root.stopping) root.receive({event: "cancelled"});
            else if (root.busy) root.receive({event: "error", text: qsTr("The connection to Hermes ended. Please try again.")});
        }
    }
    Timer { id: stopDeadline; interval: 6000; onTriggered: if (root.busy) bridge.signal(15) }
    Timer {
        interval: 12000
        running: root.busy && !root.ready
        onTriggered: {
            root.pendingPrompt = "";
            bridge.running = false;
            root.receive({event: "error", text: qsTr("Could not start Hermes. Please try again.")});
        }
    }
    ListModel { id: messages }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16
        opacity: Math.max(0, (root.reveal - 0.16) / 0.84)

        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Rectangle {
                width: 40; height: 40; radius: 13
                color: Qt.alpha(root.accent, 0.14)
                MaterialIcon { anchors.centerIn: parent; text: "auto_awesome"; color: root.accent }
            }
            ColumnLayout {
                spacing: 3
                RowLayout {
                    spacing:8
                    Text {text:"Hermes";color:root.foreground;font.pixelSize:19;font.weight:Font.DemiBold}
                    ExperimentalTag {}
                }
                Row {
                    spacing: 6
                    Rectangle { width: 6; height: 6; radius: 3; color: root.busy ? root.accent : "#73c9a1"; anchors.verticalCenter: parent.verticalCenter }
                    Text { text: root.modelLabel + (root.ready ? (root.cloudModel ? qsTr(" · Cloud") : root.modelLabel === "Local endpoint" ? qsTr(" · Network") : root.modelLabel === "Qwen 3.8 · 27B" ? qsTr(" · Local · GPU + RAM") : qsTr(" · Local · CPU")) : ""); color: root.muted; font.pixelSize: 11 }
                }
            }
            Item { Layout.fillWidth: true }
            Button {
                id: newChat
                enabled: !root.busy && root.hasConversation
                implicitWidth: 36; implicitHeight: 36
                ToolTip.visible: hovered; ToolTip.text: qsTr("New conversation")
                background: Rectangle { radius: 10; color: newChat.hovered ? Qt.alpha(root.accent, 0.12) : "transparent" }
                contentItem: MaterialIcon { text: "add_comment"; color: newChat.enabled ? root.muted : Qt.alpha(root.muted, 0.3); horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                onClicked: {
                    messages.clear(); root.answerIndex = -1;
                    if (root.ready) bridge.write(JSON.stringify({action: "reset"}) + "\n");
                    composer.forceActiveFocus();
                }
            }
            Button {
                id: backButton
                implicitWidth: 36; implicitHeight: 36
                ToolTip.visible: hovered; ToolTip.text: qsTr("Back to Start menu · Esc")
                background: Rectangle { radius: 10; color: backButton.hovered ? Qt.alpha(root.accent, 0.12) : "transparent" }
                contentItem: MaterialIcon { text: "close"; color: root.muted; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                onClicked: root.back()
            }
        }
        Rectangle { Layout.fillWidth: true; height: 1; color: Qt.alpha(root.foreground, 0.08) }
        AgentSafetyNotice {Layout.fillWidth:true}

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            ColumnLayout {
                anchors.centerIn: parent
                width: Math.min(420, parent.width - 24)
                visible: !root.hasConversation
                spacing: 14
                MaterialIcon { Layout.alignment: Qt.AlignHCenter; text: "auto_awesome"; color: root.accent }
                Text { Layout.fillWidth: true; text: qsTr("What would you like to do?"); color: root.foreground; font.pixelSize: 22; font.weight: Font.DemiBold; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap }
                Text { Layout.fillWidth: true; text: qsTr("Ask about your computer or describe what you need. Hermes shows its steps and results."); color: root.muted; font.pixelSize: 13; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap }
                Repeater {
                    model: [qsTr("How much memory is available?"), qsTr("What is my volume set to?"), qsTr("Open Files")]
                    Button {
                        id: suggestion
                        required property string modelData
                        Layout.fillWidth: true
                        implicitHeight: 42
                        background: Rectangle { radius: 12; color: Qt.alpha(root.accent, suggestion.hovered ? 0.13 : 0.055); border.width: 1; border.color: Qt.alpha(root.accent, 0.12) }
                        contentItem: Text { text: suggestion.modelData; color: root.foreground; font.pixelSize: 12; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        onClicked: root.send(modelData)
                    }
                }
            }
            ListView {
                id: transcript
                anchors.fill: parent
                clip: true
                spacing: 18
                model: messages
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ScrollBar {}
                onMovementStarted: followEnd.checked = false
                delegate: Item {
                    id: message
                    required property string speaker
                    required property string body
                    required property string toolId
                    required property string detail
                    required property string state
                    required property string summary
                    property bool detailsOpen: false
                    width: transcript.width
                    height: body ? bubble.height : 0
                    visible: !!body
                    Rectangle {
                        id: bubble
                        readonly property bool user: message.speaker === "user"
                        x: user ? message.width - width - 8 : 0
                        width: user ? Math.min(message.width * 0.88, bodyText.implicitWidth + 32) : message.width - 8
                        height: contents.implicitHeight + 28
                        radius: 16
                        color: user ? Qt.alpha(root.accent, 0.16) : message.speaker === "error" ? Qt.alpha(Colours.palette.m3error, 0.09) : message.speaker === "tool" ? Qt.alpha(root.foreground, 0.035) : "transparent"
                        border.width: message.speaker === "tool" || user ? 1 : 0
                        border.color: user ? Qt.alpha(root.accent, 0.16) : Qt.alpha(root.foreground, 0.07)
                        ColumnLayout {
                            id: contents
                            anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
                            anchors.margins: 14
                            spacing: 9
                            RowLayout {
                                Layout.fillWidth: true
                                visible: !bubble.user
                                spacing: 7
                                MaterialIcon {
                                    text: message.speaker === "tool" ? (message.state === "running" ? "pending" : message.state === "error" ? "error_outline" : message.state === "cancelled" ? "stop_circle" : "check_circle") : message.speaker === "error" ? "error_outline" : message.speaker === "notice" ? "info" : "auto_awesome"
                                    color: message.speaker === "error" || message.state === "error" ? Colours.palette.m3error : root.accent
                                }
                                Text {
                                    Layout.fillWidth: true
                                    text: message.speaker === "tool" ? message.body : message.speaker === "error" ? qsTr("Something went wrong") : message.speaker === "notice" ? qsTr("Notice") : "Hermes"
                                    color: root.muted
                                    font.pixelSize: 11; font.weight: Font.DemiBold
                                    wrapMode: Text.WordWrap
                                }
                                Button {
                                    id: detailsButton
                                    visible: message.speaker === "tool"
                                    implicitWidth: 28; implicitHeight: 24
                                    background: Item {}
                                    contentItem: MaterialIcon { text: message.detailsOpen ? "expand_less" : "expand_more"; color: root.muted }
                                    onClicked: message.detailsOpen = !message.detailsOpen
                                }
                            }
                            TextEdit {
                                id: bodyText
                                Layout.fillWidth: true
                                visible: message.speaker !== "tool" || message.detailsOpen
                                // Disable inline images and raw HTML; model text cannot fetch media.
                                text: message.speaker === "tool" ? message.detail : message.speaker === "assistant" ? message.body.replace(/</g, "&lt;").replace(/!\[/g, "[") : message.body
                                textFormat: message.speaker === "assistant" ? TextEdit.MarkdownText : TextEdit.PlainText
                                readOnly: true
                                selectByMouse: true
                                wrapMode: TextEdit.Wrap
                                color: message.speaker === "error" ? Colours.palette.m3error : root.foreground
                                selectionColor: Qt.alpha(root.accent, 0.4)
                                font.family: message.speaker === "tool" ? "monospace" : "Inter"
                                font.pixelSize: message.speaker === "tool" ? 11 : 14
                                Accessible.name: message.speaker === "user" ? qsTr("Your message") : qsTr("Response from Hermes")
                                onLinkActivated: link => { if (/^https?:\/\//.test(link)) Qt.openUrlExternally(link); }
                            }
                            Text {
                                Layout.fillWidth: true
                                visible: message.speaker === "tool" && !!message.summary
                                text: message.summary
                                color: root.foreground
                                font.pixelSize: 12
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }
            }
            Button {
                id: followEnd
                checkable: true; checked: true
                visible: !checked
                anchors.right: parent.right; anchors.bottom: parent.bottom; anchors.margins: 8
                implicitWidth: 38; implicitHeight: 38
                background: Rectangle { radius: 19; color: Colours.palette.m3surfaceContainerHigh; border.width: 1; border.color: Qt.alpha(root.accent, 0.3) }
                contentItem: MaterialIcon { text: "arrow_downward"; color: root.accent; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                onClicked: { checked = true; root.followTail(); }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: approvalContents.implicitHeight + 28
            visible: root.pendingApproval !== null
            radius: 14
            color: Qt.alpha(root.accent, 0.11)
            border.width: 1
            border.color: Qt.alpha(root.accent, 0.3)
            ColumnLayout {
                id: approvalContents
                anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
                anchors.margins: 14
                spacing: 9
                Text { text: qsTr("Run this proposal?"); color: root.foreground; font.pixelSize: 13; font.weight: Font.DemiBold }
                Text { Layout.fillWidth: true; text: root.pendingApproval?.reason ?? ""; color: root.muted; font.pixelSize: 12; wrapMode: Text.WordWrap }
                ScrollView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 64
                    TextArea {
                        text: root.pendingApproval?.command ?? ""
                        readOnly: true; selectByMouse: true
                        wrapMode: TextEdit.Wrap
                        color: root.foreground
                        font.family: "monospace"; font.pixelSize: 11
                        background: Rectangle { radius: 8; color: Qt.alpha(root.foreground, 0.04) }
                    }
                }
                RowLayout {
                    Layout.alignment: Qt.AlignRight
                    spacing: 8
                    Button {
                        id: denyButton
                        text: qsTr("Decline")
                        enabled: !root.approvalSent
                        implicitHeight: 34
                        background: Rectangle { radius: 9; color: Qt.alpha(root.foreground, denyButton.hovered ? 0.12 : 0.06) }
                        contentItem: Text { text: denyButton.text; color: root.foreground; font.pixelSize: 12; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        onClicked: {
                            root.approvalSent = true;
                            bridge.write(JSON.stringify({action: "approve", id: root.pendingApproval.id, allowed: false}) + "\n");
                        }
                    }
                    Button {
                        id: allowButton
                        text: qsTr("Run once")
                        enabled: !root.approvalSent
                        implicitHeight: 34
                        background: Rectangle { radius: 9; color: root.accent; opacity: allowButton.enabled ? 1 : 0.5 ; PrimaryControlFill {} }
                        contentItem: Text { text: allowButton.text; color: Colours.palette.m3onPrimary; font.pixelSize: 12; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        onClicked: {
                            root.approvalSent = true;
                            bridge.write(JSON.stringify({action: "approve", id: root.pendingApproval.id, allowed: true}) + "\n");
                        }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Row {
                spacing: 4
                visible: root.busy
                Repeater {
                    model: 3
                    Rectangle {
                        id: activityDot
                        required property int index
                        width: 5; height: 5; radius: 2.5; color: root.accent
                        SequentialAnimation on opacity {
                            running: root.busy && root.expanded && root.visibilities.launcher
                            loops: Animation.Infinite
                            PauseAnimation { duration: activityDot.index * 100 }
                            NumberAnimation { from: 0.3; to: 1; duration: 350 }
                            NumberAnimation { from: 1; to: 0.3; duration: 350 }
                            PauseAnimation { duration: (2 - activityDot.index) * 100 }
                        }
                    }
                }
            }
            Text { Layout.fillWidth: true; text: root.statusText; color: root.muted; font.pixelSize: 11; elide: Text.ElideRight }
            Button {
                id: stopButton
                visible: root.busy
                text: qsTr("Cancel")
                implicitHeight: 28
                background: Rectangle { radius: 8; color: stopButton.hovered ? Qt.alpha(Colours.palette.m3error, 0.16) : Qt.alpha(root.foreground, 0.05) }
                contentItem: Text { text: stopButton.text; color: root.foreground; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                onClicked: root.stop()
            }
        }
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: Math.max(58, Math.min(140, composer.contentHeight + 26))
            radius: 17
            color: Qt.alpha(root.foreground, Colours.light ? 0.045 : 0.055)
            border.width: 1
            border.color: composer.activeFocus ? Qt.alpha(root.accent, 0.65) : Qt.alpha(root.foreground, 0.12)
            Behavior on border.color { ColorAnimation { duration: 180 } }
            ScrollView {
                anchors.left: parent.left; anchors.right: sendButton.left
                anchors.top: parent.top; anchors.bottom: parent.bottom
                anchors.margins: 13
                TextArea {
                    id: composer
                    padding: 0
                    color: root.foreground
                    selectionColor: Qt.alpha(root.accent, 0.4)
                    placeholderText: root.busy ? qsTr("Hermes is working on your request …") : qsTr("Ask a follow-up or describe what you need next …")
                    placeholderTextColor: root.muted
                    readOnly: root.busy
                    wrapMode: TextEdit.Wrap
                    font.family: "Inter"; font.pixelSize: 13
                    background: Item {}
                    Accessible.name: qsTr("Message Hermes")
                    Keys.onReturnPressed: event => {
                        if (event.modifiers & Qt.ShiftModifier) event.accepted = false;
                        else { root.send(text); event.accepted = true; }
                    }
                    Keys.onEnterPressed: event => {
                        if (event.modifiers & Qt.ShiftModifier) event.accepted = false;
                        else { root.send(text); event.accepted = true; }
                    }
                    Keys.onEscapePressed: root.back()
                }
            }
            Button {
                id: sendButton
                anchors.right: parent.right; anchors.bottom: parent.bottom; anchors.margins: 10
                implicitWidth: 36; implicitHeight: 36
                enabled: !root.busy && composer.text.trim().length > 0
                ToolTip.visible: hovered; ToolTip.text: qsTr("Send · Enter")
                background: Rectangle { radius: 11; color: sendButton.enabled ? root.accent : Qt.alpha(root.foreground, 0.07); opacity: sendButton.hovered ? 0.85 : 1 ; PrimaryControlFill {} }
                contentItem: MaterialIcon { text: "arrow_upward"; color: sendButton.enabled ? Colours.palette.m3onPrimary : root.muted; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                onClicked: root.send(composer.text)
            }
        }
        Text { Layout.alignment: Qt.AlignHCenter; text: qsTr("Enter to send · Shift + Enter for a new line"); color: Qt.alpha(root.muted, 0.7); font.pixelSize: 10 }
    }
}
