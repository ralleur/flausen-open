pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls as QQC
import QtQuick.Layouts
import Quickshell
import Caelestia.Components
import Caelestia.Services
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services
import qs.utils
import qs.modules.nexus

ColumnLayout {
    id: root
    required property PopoutState popouts
    property string view: "wireless"
    property var passwordNetwork: null
    property bool showPasswordDialog: false
    property bool _isSidebarOpen: false
    property real scaleOffset: 1.0
    property real fontScale: 1.0
    property bool vpnExpanded: false
    property bool detailsExpanded: false
    property bool wifiPending: false
    property string wifiError: ""
    readonly property real bodyPointSize: MenuStyle.bodyPointSize(root.fontScale)
    readonly property real titlePointSize: root.bodyPointSize * 1.68
    readonly property real contentInset: 7 * root.scaleOffset
    readonly property color accent: MenuStyle.accent
    readonly property color muted: MenuStyle.muted
    readonly property color rule: MenuStyle.rule
    readonly property var sortedNetworks: [...Nmcli.networks].sort((a, b) => a.active !== b.active ? b.active - a.active : b.strength - a.strength)
    readonly property var deviceDetails: root.view === "wireless" ? Nmcli.wirelessDeviceDetails : Nmcli.ethernetDeviceDetails
    readonly property var detailRows: {
        const d = root.deviceDetails;
        if (!d) return [];
        return [
            {label: qsTr("IP address"), value: d.ipAddress || ""},
            {label: qsTr("Subnet mask"), value: d.subnet || ""},
            {label: qsTr("Gateway"), value: d.gateway || ""},
            {label: qsTr("DNS"), value: Array.isArray(d.dns) ? d.dns.join(", ") : ""},
            {label: qsTr("MAC address"), value: d.macAddress || ""}
        ].filter(row => row.value);
    }

    width: 420 * scaleOffset
    implicitWidth: width
    spacing: 10 * scaleOffset

    function openSettings(): void {
        root.popouts.hasCurrent = false;
        WindowFactory.create(null, {initialPageIdx: Math.max(0, PageRegistry.indexForKey("network"))});
    }
    function connectNetwork(network): void {
        if (network.active) {
            Nmcli.disconnectFromNetwork();
            return;
        }
        NetworkConnection.handleConnect(network, null, ap => {
            const snapshot = {ssid: ap.ssid, bssid: ap.bssid || "", isSecure: ap.isSecure ?? true, strength: ap.strength ?? 0};
            NetworkConnection.passwordNetwork = snapshot;
            root.passwordNetwork = snapshot;
            root.showPasswordDialog = true;
            root.popouts.currentName = "wirelesspassword";
        });
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.topMargin: 3 * root.scaleOffset
        Layout.leftMargin: 12 * root.scaleOffset
        Layout.rightMargin: root.contentInset
        MenuText {
            Layout.fillWidth: true
            text: qsTr("Network")
                    wrapMode: Text.WordWrap
            font.weight: 600
            font.pointSize: root.titlePointSize
        }
        StyledRect {
            Layout.alignment: Qt.AlignTop
            implicitWidth: 38 * root.scaleOffset
            implicitHeight: implicitWidth
            radius: height / 2
            color: "transparent"
            MaterialIcon {
                anchors.centerIn: parent
                text: "settings"
                color: root.muted
                fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.fontScale * 1.2
            }
            StateLayer {
                onClicked: root.openSettings()
                Accessible.name: qsTr("Network settings")
                Accessible.role: Accessible.Button
            }
            HoverHandler { id: settingsHover }
            QQC.ToolTip.visible: settingsHover.hovered
            QQC.ToolTip.delay: 600
            QQC.ToolTip.text: qsTr("Network settings")
        }
    }

    GroupCard {
        content: [
            RowLayout {
                Layout.fillWidth: true
                Layout.leftMargin: 16 * root.scaleOffset
                Layout.rightMargin: 16 * root.scaleOffset
                Layout.topMargin: 10 * root.scaleOffset
                Layout.bottomMargin: 10 * root.scaleOffset
                spacing: 14 * root.scaleOffset
                StyledRect {
                    implicitWidth: 38 * root.scaleOffset
                    implicitHeight: implicitWidth
                    radius: 12 * root.scaleOffset
                    color: Qt.alpha(root.accent, Colours.light ? 0.2 : 0.25)
                    MaterialIcon {
                        anchors.centerIn: parent
                        text: root.view === "ethernet" ? "lan" : Nmcli.wifiEnabled ? "wifi" : "wifi_off"
                        color: Colours.light ? "#164994" : "#dce9ff"
                        fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.scaleOffset * 1.25
                    }
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 3 * root.scaleOffset
                    MenuText {
                        text: root.view === "wireless" ? "Wi-Fi" : qsTr("Ethernet")
                        font.weight: 600
                        font.pointSize: root.bodyPointSize
                    }
                    MenuText {
                        Layout.fillWidth: true
                        text: root.view === "ethernet" ? (Nmcli.activeEthernet?.iface || qsTr("Not connected")) : root.wifiPending ? qsTr("Switching …") : !Nmcli.wifiEnabled ? qsTr("Wi-Fi is off") : Nmcli.connectingSsid ? qsTr("Connecting to %1 …").arg(Nmcli.connectingSsid) : Nmcli.active?.ssid || qsTr("Not connected")
                        color: root.muted
                        elide: Text.ElideRight
                        font.pointSize: root.bodyPointSize * 0.79
                    }
                }
                QQC.Switch {
                    id: wifiSwitch
                    visible: root.view === "wireless"
                    checked: Nmcli.wifiEnabled
                    enabled: !root.wifiPending
                    padding: 0
                    implicitWidth: 46 * root.scaleOffset
                    implicitHeight: 38 * root.scaleOffset
                    indicator: Rectangle {
                        width: wifiSwitch.implicitWidth
                        height: 26 * root.scaleOffset
                        y: (wifiSwitch.height - height) / 2
                        radius: height / 2
                        color: wifiSwitch.checked ? root.accent : Qt.alpha(Colours.palette.m3onSurface, 0.22)
                        PrimaryControlFill {} // Capture primary material
                        opacity: wifiSwitch.enabled ? 1 : 0.5
                        Rectangle {
                            y: 3 * root.scaleOffset
                            x: wifiSwitch.checked ? parent.width - width - y : y
                            width: parent.height - 2 * y
                            height: width
                            radius: height / 2
                            color: "white"
                            Behavior on x { Anim {} }
                        }
                    }
                    onToggled: {
                        root.wifiPending = true;
                        root.wifiError = "";
                        Nmcli.enableWifi(checked, result => {
                            root.wifiPending = false;
                            if (result && result.success === false) root.wifiError = result.error || qsTr("Could not toggle Wi-Fi");
                        });
                    }
                    Accessible.name: qsTr("Wi-Fi")
                }
            }
        ]
    }
    MenuText {
        visible: !!root.wifiError
        Layout.fillWidth: true
        text: root.wifiError
        color: Colours.palette.m3error
        wrapMode: Text.Wrap
        font.pointSize: root.bodyPointSize * 0.79
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.leftMargin: 12 * root.scaleOffset
        Layout.rightMargin: root.contentInset
        Layout.topMargin: 3 * root.scaleOffset
        MenuText {
            Layout.fillWidth: true
            text: root.view === "wireless" ? qsTr("Available networks") : qsTr("Available devices")
            color: root.muted
            font.weight: 500
            font.pointSize: root.bodyPointSize * 0.94
        }
        MenuText {
            text: root.view === "wireless" ? (Nmcli.wifiEnabled ? Nmcli.networks.length : 0) : Nmcli.ethernetDevices.length
            color: root.muted
            font.pointSize: root.bodyPointSize * 0.94
        }
    }
    GroupCard {
        content: [
            Repeater {
                model: ScriptModel { values: root.view === "wireless" ? (Nmcli.wifiEnabled ? root.sortedNetworks.slice(0, 8) : []) : [...Nmcli.ethernetDevices].sort((a,b) => b.connected - a.connected).slice(0,8) }
                NetworkRow {
                    required property var modelData
                    required property int index
                    label: root.view === "wireless" ? modelData.ssid : modelData.iface || qsTr("Unknown")
                    symbol: root.view === "wireless" ? (modelData.strength >= 60 ? "wifi" : modelData.strength >= 30 ? "wifi_2_bar" : "wifi_1_bar") : "cable"
                    selected: root.view === "wireless" ? modelData.active : modelData.connected
                    secure: root.view === "wireless" && (modelData.isSecure ?? false)
                    loading: root.view === "wireless" && Nmcli.connectingSsid === modelData.ssid
                    divider: index > 0
                    onClicked: {
                        if (root.view === "wireless") root.connectNetwork(modelData);
                        else if (modelData.connected && modelData.connection) Nmcli.disconnectEthernet(modelData.connection, () => {});
                        else Nmcli.connectEthernet(modelData.connection || "", modelData.iface || "", () => {});
                    }
                }
            },
            MenuText {
                visible: root.view === "wireless" ? !Nmcli.wifiEnabled || !Nmcli.networks.length : !Nmcli.ethernetDevices.length
                Layout.fillWidth: true
                Layout.margins: 18 * root.scaleOffset
                text: root.view === "ethernet" ? qsTr("No Ethernet devices found") : !Nmcli.wifiEnabled ? qsTr("Turn on Wi-Fi to find networks") : Nmcli.scanning ? qsTr("Searching for networks …") : qsTr("No networks found")
                color: root.muted
                wrapMode: Text.Wrap
                font.pointSize: root.bodyPointSize
            }
        ]
    }

    StyledRect {
        visible: root.view === "wireless"
        Layout.fillWidth: true
        Layout.leftMargin: root.contentInset
        Layout.rightMargin: root.contentInset
        implicitHeight: Math.max(38 * root.scaleOffset, scanContent.implicitHeight + 10 * root.scaleOffset)
        radius: 14 * root.scaleOffset
        color: MenuStyle.cardFill
        border.width: 1
        border.color: root.rule
        enabled: Nmcli.wifiEnabled && !Nmcli.scanning
        opacity: Nmcli.wifiEnabled ? 1 : 0.45
        RowLayout {
            id: scanContent
            anchors.centerIn: parent
            spacing: 12 * root.scaleOffset
            MaterialIcon {
                text: "refresh"
                color: root.muted
                fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.scaleOffset * 1.1
            }
            MenuText {
                text: Nmcli.scanning ? qsTr("Searching …") : qsTr("Scan again")
                font.pointSize: root.bodyPointSize
            }
        }
        StateLayer {
            disabled: !parent.enabled
            onClicked: Nmcli.rescanWifi()
            Accessible.name: qsTr("Scan again")
            Accessible.role: Accessible.Button
        }
    }

    Rectangle {
        Layout.fillWidth: true
        Layout.leftMargin: root.contentInset
        Layout.rightMargin: root.contentInset
        Layout.topMargin: 2 * root.scaleOffset
        implicitHeight: 1
        color: root.rule
    }
    GroupCard {
        content: [
            NetworkRow {
                label: "VPN"
                subtitle: Nmcli.activeVpn?.name || qsTr("Manage connections")
                symbol: "shield"
                expanded: root.vpnExpanded
                expandable: true
                onClicked: root.vpnExpanded = !root.vpnExpanded
            },
            Repeater {
                model: root.vpnExpanded ? Nmcli.vpnConnections : []
                NetworkRow {
                    required property var modelData
                    label: modelData.name
                    subtitle: qsTranslate("Flausen", modelData.detail || "")
                    symbol: "vpn_key"
                    divider: true
                    selected: modelData.connected
                    loading: Nmcli.vpnPendingConnection === modelData.name
                    onClicked: {
                        if (modelData.connected) Nmcli.disconnectVpn(modelData.connectionId || modelData.name, () => {});
                        else Nmcli.connectVpn(modelData.connectionId || modelData.name, () => {});
                    }
                }
            },
            MenuText {
                visible: root.vpnExpanded && Nmcli.vpnConnections.length === 0
                Layout.fillWidth: true
                Layout.margins: 16 * root.scaleOffset
                text: qsTr("No VPN profiles available")
                color: root.muted
                font.pointSize: root.bodyPointSize * 0.79
            }
        ]
    }
    GroupCard {
        visible: root.detailRows.length > 0
        content: [
            NetworkRow {
                label: qsTr("Connection details")
                symbol: "info"
                expandable: true
                expanded: root.detailsExpanded
                onClicked: root.detailsExpanded = !root.detailsExpanded
            },
            Repeater {
                model: root.detailsExpanded ? root.detailRows : []
                RowLayout {
                    required property var modelData
                    Layout.fillWidth: true
                    Layout.leftMargin: 16 * root.scaleOffset
                    Layout.rightMargin: 16 * root.scaleOffset
                    Layout.bottomMargin: 10 * root.scaleOffset
                    MenuText {
                        text: modelData.label
                        font.pointSize: root.bodyPointSize * 0.79
                    }
                    MenuText {
                        Layout.fillWidth: true
                        text: modelData.value
                        color: root.muted
                        horizontalAlignment: Text.AlignRight
                        elide: Text.ElideRight
                        font.pointSize: root.bodyPointSize * 0.79
                    }
                }
            }
        ]
    }

    // Share the dashboard's live sampler and history, including its totals.
    ServiceRef { service: NetworkUsage }

    GroupCard {
        content: [
            ColumnLayout {
                Layout.fillWidth: true
                Layout.margins: 16 * root.scaleOffset
                spacing: 5 * root.scaleOffset

                RowLayout {
                    spacing: 10 * root.scaleOffset
                    MaterialIcon {
                        text: "swap_vert"
                        color: root.accent
                        fontStyle.pointSize: 18 * root.scaleOffset
                    }
                    MenuText {
                        text: qsTr("Traffic")
                        font.pointSize: root.bodyPointSize
                        font.weight: 600
                    }
                }

                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 52 * root.scaleOffset
                    Layout.topMargin: 4 * root.scaleOffset
                    Layout.bottomMargin: 5 * root.scaleOffset
                    SparklineItem {
                        id: trafficGraph
                        property real targetMax: Math.max(NetworkUsage.downloadBuffer.maximum, NetworkUsage.uploadBuffer.maximum, 1024)
                        property real smoothMax: targetMax
                        anchors.fill: parent
                        line1: NetworkUsage.uploadBuffer
                        line1Color: Colours.palette.m3secondary
                        line1FillAlpha: 0.15
                        line2: NetworkUsage.downloadBuffer
                        line2Color: Colours.palette.m3tertiary
                        line2FillAlpha: 0.2
                        maxValue: smoothMax
                        historyLength: NetworkUsage.historyLength
                        Connections {
                            target: NetworkUsage.downloadBuffer
                            function onValuesChanged(): void { trafficSlide.restart(); }
                        }
                        NumberAnimation {
                            id: trafficSlide
                            target: trafficGraph
                            property: "slideProgress"
                            from: 0
                            to: 1
                            easing.type: Easing.Linear
                            duration: GlobalConfig.dashboard.resourceUpdateInterval
                        }
                        Behavior on smoothMax { Anim {} }
                    }
                    MenuText {
                        anchors.centerIn: parent
                        visible: NetworkUsage.downloadBuffer.count < 2
                        text: qsTr("Collecting data …")
                        font.pointSize: root.bodyPointSize * 0.79
                        color: root.muted
                    }
                }

                TrafficRow {
                    symbol: "download"
                    label: qsTr("Download")
                    value: Units.formatBytes(NetworkUsage.downloadSpeed ?? 0, true)
                    valueColor: Colours.palette.m3tertiary
                }
                TrafficRow {
                    symbol: "upload"
                    label: qsTr("Upload")
                    value: Units.formatBytes(NetworkUsage.uploadSpeed ?? 0, true)
                    valueColor: Colours.palette.m3secondary
                }
                TrafficRow {
                    symbol: "history"
                    label: qsTr("Total")
                    value: `↓${Units.formatBytes(NetworkUsage.downloadTotal ?? 0)} ↑${Units.formatBytes(NetworkUsage.uploadTotal ?? 0)}`
                }
            }
        ]
    }

    component TrafficRow: RowLayout {
        required property string symbol
        required property string label
        required property string value
        property color valueColor: root.muted
        Layout.fillWidth: true
        spacing: 10 * root.scaleOffset
        MaterialIcon {
            text: parent.symbol
            color: parent.valueColor
            fontStyle.pointSize: 14 * root.scaleOffset
        }
        MenuText {
            text: parent.label
            color: root.muted
            font.pointSize: root.bodyPointSize
        }
        MenuText {
            Layout.fillWidth: true
            text: parent.value
            color: parent.valueColor
            horizontalAlignment: Text.AlignRight
            font.pointSize: root.bodyPointSize
        }
    }

    component GroupCard: StyledRect {
        property alias content: rows.data
        Layout.fillWidth: true
        Layout.leftMargin: root.contentInset
        Layout.rightMargin: root.contentInset
        implicitHeight: rows.implicitHeight + 4 * root.scaleOffset
        radius: 14 * root.scaleOffset
        color: MenuStyle.cardFill
        border.width: 1
        border.color: root.rule
        ColumnLayout {
            id: rows
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.topMargin: 2 * root.scaleOffset
            spacing: 0
        }
    }
    component NetworkRow: StyledRect {
        id: row
        required property string label
        required property string symbol
        property string subtitle: ""
        property bool selected: false
        property bool secure: false
        property bool loading: false
        property bool divider: false
        property bool expandable: false
        property bool expanded: false
        signal clicked
        Layout.fillWidth: true
        implicitHeight: Math.max((subtitle ? 55 : 44) * root.scaleOffset, rowContent.implicitHeight + 16 * root.scaleOffset)
        radius: 13 * root.scaleOffset
        color: row.selected ? Qt.alpha(root.accent, 0.08) : "transparent"
        Rectangle {
            visible: row.divider
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 68 * root.scaleOffset
            anchors.rightMargin: 16 * root.scaleOffset
            height: 1
            color: root.rule
        }
        RowLayout {
            id: rowContent
            anchors.fill: parent
            anchors.leftMargin: 16 * root.scaleOffset
            anchors.rightMargin: 16 * root.scaleOffset
            spacing: 16 * root.scaleOffset
            Item {
                Layout.preferredWidth: 36 * root.scaleOffset
                Layout.preferredHeight: 30 * root.scaleOffset
                MaterialIcon {
                    anchors.centerIn: parent
                    text: row.symbol
                    color: row.selected ? root.accent : Colours.palette.m3onSurface
                    fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.scaleOffset * 1.35
                }
            }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 3 * root.scaleOffset
                MenuText {
                    Layout.fillWidth: true
                    text: row.label
                    elide: Text.ElideRight
                    font.weight: row.selected || row.expandable ? 500 : 400
                    font.pointSize: root.bodyPointSize
                }
                MenuText {
                    visible: !!row.subtitle
                    Layout.fillWidth: true
                    text: row.subtitle
                    color: root.muted
                    elide: Text.ElideRight
                    font.pointSize: root.bodyPointSize * 0.79
                }
            }
            MaterialIcon {
                visible: row.secure
                text: "lock"
                color: root.muted
                fontStyle.pointSize: Tokens.font.icon.small.pointSize * root.fontScale
            }
            Item {
                Layout.preferredWidth: 20 * root.scaleOffset
                Layout.preferredHeight: width
                CircularIndicator { anchors.fill: parent; running: row.loading }
                MaterialIcon {
                    anchors.centerIn: parent
                    visible: !row.loading
                    text: row.expandable ? "expand_more" : row.selected ? "check" : "chevron_right"
                    rotation: row.expandable && row.expanded ? 180 : 0
                    color: row.selected ? root.accent : root.muted
                    fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.fontScale
                    Behavior on rotation { Anim {} }
                }
            }
        }
        StateLayer {
            disabled: row.loading
            onClicked: row.clicked()
            Accessible.name: row.label + (row.selected ? ", " + qsTr("Connected") : "")
            Accessible.role: Accessible.Button
        }
        HoverHandler { id: rowHover }
        QQC.ToolTip.visible: rowHover.hovered
        QQC.ToolTip.delay: 800
        QQC.ToolTip.text: row.label + (row.selected && !row.expandable ? " · " + qsTr("Disconnect") : "")
    }
    Connections {
        target: Nmcli
        function onActiveChanged(): void {
            if (root.showPasswordDialog && root.passwordNetwork && Nmcli.active?.ssid === root.passwordNetwork.ssid) {
                root.showPasswordDialog = false;
                root.passwordNetwork = null;
            }
        }
    }
    Connections {
        target: root.popouts
        function onCurrentNameChanged(): void {
            if (root.popouts.currentName !== "wirelesspassword" && root.showPasswordDialog) {
                root.showPasswordDialog = false;
                root.passwordNetwork = null;
            }
        }
    }
}
