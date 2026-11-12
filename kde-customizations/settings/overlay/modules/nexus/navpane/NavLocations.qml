pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import qs.components
import qs.modules.nexus
import "../flausen"
ScrollView {
    id: root
    required property NexusState nState
    property bool expanded: false
    // Stable indices preserve existing IPC callers and the original detail pages.
    readonly property var primary: [
        {idx:17, label:qsTranslate("Flausen", "General"), icon:"settings", group:0},
        {idx:0, label:qsTranslate("Flausen", "Appearance"), icon:"palette", group:0},
        {idx:2, label:qsTranslate("Flausen", "Desktop & Dock"), icon:"desktop_windows", group:0},
        {idx:22, label:"Hermes", icon:"auto_awesome", group:0},
        {idx:6, label:qsTranslate("Flausen", "Notifications"), icon:"notifications", group:0},
        {idx:3, label:qsTranslate("Flausen", "Network"), icon:"wifi", group:1},
        {idx:4, label:"Bluetooth", icon:"bluetooth", group:1},
        {idx:18, label:qsTranslate("Flausen", "Display"), icon:"monitor", group:1},
        {idx:5, label:qsTranslate("Flausen", "Sound"), icon:"volume_up", group:1},
        {idx:19, label:qsTranslate("Flausen", "Keyboard & mouse"), icon:"mouse", group:1},
        {idx:20, label:qsTranslate("Flausen", "Privacy & security"), icon:"shield", group:2},
        {idx:21, label:qsTranslate("Flausen", "System"), icon:"deployed_code", group:2}
    ]
    readonly property var more: [1,7,8,9,10,11,12,13,14,15,16].map(idx => ({idx:idx, label:PageRegistry.pages[idx].label, icon:PageRegistry.pages[idx].icon, group:3}))
    clip: true
    contentWidth: availableWidth
    ColumnLayout {
        width: root.availableWidth
        spacing: 3
        Repeater {
            model: root.primary
            delegate: NavItem {}
        }
        ToolButton {
            Layout.fillWidth: true
            Layout.topMargin: 12
            text: root.expanded ? qsTranslate("Flausen", "Fewer options") : qsTranslate("Flausen", "More settings")
            font.family: FlausenStyle.family
            palette.buttonText: FlausenStyle.secondary
            onClicked: root.expanded = !root.expanded
        }
        Repeater { model: root.expanded ? root.more : []; delegate: NavItem {} }
    }
    component NavItem: Item {
        id: row
        required property var modelData
        required property int index
        readonly property bool selected: root.nState.currentPageIdx === modelData.idx
        readonly property bool separator: index > 0 && modelData.group !== (root.primary[index - 1]?.group ?? modelData.group)
        Layout.fillWidth: true
        implicitHeight: 44 + (separator ? 23 : 0)
        Rectangle { visible: row.separator; height: 1; width: parent.width - 32; x: 16; y: 10; color: FlausenStyle.line }
        Button {
            id: button
            y: row.separator ? 23 : 0
            height: 44
            leftPadding: 12
            rightPadding: 12
            topPadding: 0
            bottomPadding: 0
            width: parent.width
            Accessible.name: row.modelData.label + (row.modelData.idx===22 ? " · Experimental" : "")
            onClicked: root.nState.goToSubPage(row.modelData.idx, -1)
            background: Rectangle { radius: 11; color: row.selected ? FlausenStyle.selected : button.hovered || button.visualFocus ? Qt.alpha(FlausenStyle.text, 0.06) : "transparent"; border.width: button.visualFocus ? 2 : 0; border.color: FlausenStyle.accent }
            contentItem: RowLayout {
                spacing: 12
                SettingsIcon { name: row.modelData.icon; fieldSize: 32; glyphPixels: 32; Layout.alignment: Qt.AlignVCenter; Layout.preferredWidth: 32; Layout.preferredHeight: 32 }
                Text { text: row.modelData.label; color: FlausenStyle.text; font {family: FlausenStyle.family; pixelSize: FlausenStyle.fontScale * 14} Layout.fillWidth: true; elide: Text.ElideRight }
                ExperimentalTag {visible:row.modelData.idx===22;compact:true;Layout.alignment:Qt.AlignVCenter}
            }
        }
    }
}
