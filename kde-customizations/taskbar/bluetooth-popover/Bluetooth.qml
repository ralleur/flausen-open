pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls as QQC
import QtQuick.Layouts
import Quickshell
import Quickshell.Bluetooth
import Caelestia.Config
import qs.components
import qs.components.controls
import qs.services
import qs.utils

ColumnLayout {
    id: root
    required property PopoutState popouts
    property real scaleOffset: 1.0
    property real fontScale: 1.0
    property bool _isSidebarOpen: false
    readonly property real bodyPointSize: MenuStyle.bodyPointSize(root.fontScale)
    readonly property real titlePointSize: root.bodyPointSize * 1.68
    readonly property real contentInset: 7 * root.scaleOffset
    readonly property color accent: MenuStyle.accent
    readonly property color muted: MenuStyle.muted
    readonly property color rule: MenuStyle.rule
    readonly property var adapter: Bluetooth.defaultAdapter
    readonly property var devices: [...Bluetooth.devices.values].sort((a, b) => (b.connected - a.connected) || (b.paired - a.paired) || a.name.localeCompare(b.name))
    readonly property int connectedCount: root.devices.filter(device => device.connected).length

    width: 420 * scaleOffset
    implicitWidth: width
    spacing: 10 * scaleOffset

    RowLayout {
        Layout.fillWidth: true
        Layout.topMargin: 3 * root.scaleOffset
        Layout.leftMargin: 12 * root.scaleOffset
        Layout.rightMargin: root.contentInset
        MenuText {
            Layout.fillWidth: true
            text: qsTr("Bluetooth")
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
                onClicked: root.popouts.detachRequested("bluetooth")
                Accessible.name: qsTr("Bluetooth settings")
                Accessible.role: Accessible.Button
            }
            HoverHandler { id: settingsHover }
            QQC.ToolTip.visible: settingsHover.hovered
            QQC.ToolTip.delay: 600
            QQC.ToolTip.text: qsTr("Bluetooth settings")
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
                        text: root.adapter?.enabled ? "bluetooth" : "bluetooth_disabled"
                        color: Colours.light ? "#164994" : "#dce9ff"
                        fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.scaleOffset * 1.25
                    }
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 3 * root.scaleOffset
                    MenuText {
                        Layout.fillWidth: true
                        text: qsTr("Bluetooth")
                        font.weight: 600
                        font.pointSize: root.bodyPointSize
                    }
                    MenuText {
                        Layout.fillWidth: true
                        text: !root.adapter ? qsTr("No adapter found") : !root.adapter.enabled ? qsTr("Off") : root.adapter.discovering ? qsTr("Searching for devices …") : root.connectedCount === 1 ? qsTr("1 device connected") : root.connectedCount > 1 ? qsTr("%1 devices connected").arg(root.connectedCount) : qsTr("Ready to connect")
                        color: root.muted
                        elide: Text.ElideRight
                        font.pointSize: root.bodyPointSize * 0.79
                    }
                }
                QQC.Switch {
                    id: powerSwitch
                    checked: root.adapter?.enabled ?? false
                    enabled: !!root.adapter
                    padding: 0
                    implicitWidth: 46 * root.scaleOffset
                    implicitHeight: 38 * root.scaleOffset
                    indicator: Rectangle {
                        width: powerSwitch.implicitWidth
                        height: 26 * root.scaleOffset
                        y: (powerSwitch.height - height) / 2
                        radius: height / 2
                        color: powerSwitch.checked ? root.accent : Qt.alpha(Colours.palette.m3onSurface, 0.22)
                        PrimaryControlFill {} // Capture primary material
                        opacity: powerSwitch.enabled ? 1 : 0.5
                        Rectangle {
                            y: 3 * root.scaleOffset
                            x: powerSwitch.checked ? parent.width - width - y : y
                            width: parent.height - 2 * y
                            height: width
                            radius: height / 2
                            color: "white"
                            Behavior on x { Anim {} }
                        }
                    }
                    onToggled: {
                        const adapter = Bluetooth.defaultAdapter;
                        if (adapter) adapter.enabled = checked;
                    }
                    Accessible.name: qsTr("Bluetooth")
                }
            }
        ]
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.leftMargin: 12 * root.scaleOffset
        Layout.rightMargin: root.contentInset
        Layout.topMargin: 3 * root.scaleOffset
        MenuText {
            Layout.fillWidth: true
            text: qsTr("Devices")
            color: root.muted
            font.weight: 500
            font.pointSize: root.bodyPointSize * 0.94
        }
        MenuText {
            text: root.devices.length
            color: root.muted
            font.pointSize: root.bodyPointSize * 0.94
        }
    }
    GroupCard {
        content: [
            Repeater {
                model: ScriptModel { values: root.devices.slice(0, 5) }
                StyledRect {
                    id: device
                    required property BluetoothDevice modelData
                    required property int index
                    readonly property bool loading: modelData.state === BluetoothDeviceState.Connecting || modelData.state === BluetoothDeviceState.Disconnecting
                    Layout.fillWidth: true
                    implicitHeight: Math.max(55 * root.scaleOffset, deviceContents.implicitHeight + 16 * root.scaleOffset)
                    radius: 13 * root.scaleOffset
                    color: modelData.connected ? Qt.alpha(root.accent, 0.08) : "transparent"
                    Rectangle {
                        visible: device.index > 0
                        anchors.top: parent.top
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.leftMargin: 68 * root.scaleOffset
                        anchors.rightMargin: 16 * root.scaleOffset
                        height: 1
                        color: root.rule
                    }
                    StateLayer {
                        disabled: device.loading
                        onClicked: device.modelData.connected = !device.modelData.connected
                        Accessible.name: device.modelData.name + ": " + (device.modelData.connected ? qsTr("Disconnect") : qsTr("Connect"))
                        Accessible.role: Accessible.Button
                    }
                    RowLayout {
                        id: deviceContents
                        anchors.fill: parent
                        anchors.leftMargin: 16 * root.scaleOffset
                        anchors.rightMargin: 8 * root.scaleOffset
                        spacing: 16 * root.scaleOffset
                        Item {
                            Layout.preferredWidth: 36 * root.scaleOffset
                            Layout.preferredHeight: 30 * root.scaleOffset
                            MaterialIcon {
                                anchors.centerIn: parent
                                text: Icons.getBluetoothIcon(device.modelData.icon)
                                color: device.modelData.connected ? root.accent : Colours.palette.m3onSurface
                                fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.scaleOffset * 1.35
                            }
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 3 * root.scaleOffset
                            MenuText {
                                Layout.fillWidth: true
                                text: device.modelData.name
                                font.weight: device.modelData.connected ? 500 : 400
                                font.pointSize: root.bodyPointSize
                                elide: Text.ElideRight
                            }
                            MenuText {
                                Layout.fillWidth: true
                                text: device.modelData.state === BluetoothDeviceState.Connecting ? qsTr("Connecting …") : device.modelData.state === BluetoothDeviceState.Disconnecting ? qsTr("Disconnecting …") : device.modelData.connected ? qsTr("Connected") : device.modelData.paired || device.modelData.bonded ? qsTr("Paired") : qsTr("Not connected")
                                color: root.muted
                                font.pointSize: root.bodyPointSize * 0.79
                                elide: Text.ElideRight
                            }
                        }
                        RowLayout {
                            visible: device.modelData.state === BluetoothDeviceState.Connected
                            Layout.preferredWidth: 51 * root.scaleOffset
                            spacing: 3 * root.scaleOffset
                            MaterialIcon {
                                text: device.modelData.batteryAvailable ? Icons.getBatteryIcon(device.modelData.battery) : "battery_alert"
                                color: device.modelData.batteryAvailable && device.modelData.battery < 0.2 ? Colours.palette.m3error : root.muted
                                fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.scaleOffset * 0.9
                            }
                            MenuText {
                                visible: device.modelData.batteryAvailable
                                text: qsTr("%1%").arg(Math.round(device.modelData.battery * 100))
                                color: device.modelData.battery < 0.2 ? Colours.palette.m3error : root.muted
                                font.pointSize: root.bodyPointSize * 0.79
                            }
                        }
                        Item {
                            Layout.preferredWidth: 20 * root.scaleOffset
                            Layout.preferredHeight: width
                            CircularIndicator { anchors.fill: parent; running: device.loading }
                            MaterialIcon {
                                anchors.centerIn: parent
                                visible: !device.loading
                                text: device.modelData.connected ? "check" : "chevron_right"
                                color: device.modelData.connected ? root.accent : root.muted
                                fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.scaleOffset
                            }
                        }
                        Item {
                            Layout.preferredWidth: 36 * root.scaleOffset
                            Layout.preferredHeight: width
                            StyledRect {
                                anchors.fill: parent
                                radius: height / 2
                                color: "transparent"
                                visible: device.modelData.bonded
                                enabled: !device.loading
                                opacity: enabled ? 1 : 0.38
                                MaterialIcon {
                                    anchors.centerIn: parent
                                    text: "delete"
                                    color: root.muted
                                    fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.scaleOffset
                                }
                                StateLayer {
                                    onClicked: device.modelData.forget()
                                    Accessible.name: qsTr("Remove %1").arg(device.modelData.name)
                                    Accessible.role: Accessible.Button
                                }
                                HoverHandler { id: forgetHover }
                                QQC.ToolTip.visible: forgetHover.hovered
                                QQC.ToolTip.delay: 600
                                QQC.ToolTip.text: qsTr("Remove device")
                            }
                        }
                    }
                    HoverHandler { id: deviceHover }
                    QQC.ToolTip.visible: deviceHover.hovered && !forgetHover.hovered
                    QQC.ToolTip.delay: 800
                    QQC.ToolTip.text: device.modelData.name + " · " + (device.modelData.connected ? qsTr("Disconnect") : qsTr("Connect"))
                }
            },
            MenuText {
                visible: root.devices.length === 0
                Layout.fillWidth: true
                Layout.margins: 18 * root.scaleOffset
                text: !root.adapter ? qsTr("No Bluetooth adapter found") : !root.adapter.enabled ? qsTr("Bluetooth is off") : root.adapter.discovering ? qsTr("Searching for devices …") : qsTr("No devices found")
                wrapMode: Text.Wrap
                color: root.muted
                font.pointSize: root.bodyPointSize
            }
        ]
    }

    StyledRect {
        Layout.fillWidth: true
        Layout.leftMargin: root.contentInset
        Layout.rightMargin: root.contentInset
        implicitHeight: Math.max(38 * root.scaleOffset, scanContents.implicitHeight + 10 * root.scaleOffset)
        radius: 14 * root.scaleOffset
        color: MenuStyle.cardFill
        border.width: 1
        border.color: root.rule
        enabled: root.adapter?.enabled ?? false
        opacity: enabled ? 1 : 0.45
        RowLayout {
            id: scanContents
            anchors.centerIn: parent
            spacing: 12 * root.scaleOffset
            MaterialIcon {
                text: root.adapter?.discovering ? "stop" : "refresh"
                color: root.muted
                fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.scaleOffset * 1.1
            }
            MenuText {
                text: root.adapter?.discovering ? qsTr("Stop searching") : qsTr("Search for devices")
                font.pointSize: root.bodyPointSize * 0.94
            }
        }
        StateLayer {
            disabled: !parent.enabled
            onClicked: {
                const adapter = Bluetooth.defaultAdapter;
                if (adapter) adapter.discovering = !adapter.discovering;
            }
            Accessible.name: root.adapter?.discovering ? qsTr("Stop Bluetooth discovery") : qsTr("Search for Bluetooth devices")
            Accessible.role: Accessible.Button
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
}
