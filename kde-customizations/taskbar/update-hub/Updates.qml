pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Widgets
import Caelestia.Config
import qs.components
import qs.services
import qs.modules.bar
import qs.modules.nexus

ColumnLayout {
    id: root
    required property PopoutState popouts
    property real scaleOffset: 1.0
    property real fontScale: 1.0
    property bool _isSidebarOpen: false
    readonly property bool checking: UpdateHub.checking || UpdateChecker.checkingUpdates
    readonly property bool incomplete: UpdateHub.hasErrors || UpdateHub.sources.some(source => UpdateHub.enabled(source.key) && UpdateHub.statusIcon(source.key) === "question_mark") || root.shellIcon === "question_mark"
    readonly property int updateCount: UpdateHub.pendingCount + (UpdateChecker.hasUpdate ? 1 : 0)
    readonly property color accent: MenuStyle.accent
    readonly property color muted: MenuStyle.muted
    readonly property color rule: MenuStyle.rule
    readonly property string shellIcon: UpdateChecker.checkingUpdates ? "sync" : UpdateChecker.hasUpdate ? "arrow_upward" : UpdateChecker.lastCheckMs > 0 && UpdateChecker.currentVersion !== "unknown" ? "check" : "question_mark"
    // Proportions are measured against the reference at equal outer width.
    // App icons stay large while typography and row rhythm become quieter.
    readonly property real bodyPointSize: MenuStyle.bodyPointSize(root.fontScale)
    readonly property real titlePointSize: root.bodyPointSize * 1.68
    readonly property real contentInset: 7 * root.scaleOffset
    property double nowMs: Date.now()
    readonly property string checkedText: {
        const checks = UpdateHub.sources.filter(s => UpdateHub.enabled(s.key)).map(s => UpdateHub.status[s.key]?.checkedAt ?? 0);
        if (UpdateChecker.lastCheckMs > 0) checks.push(UpdateChecker.lastCheckMs / 1000);
        if (!checks.length || checks.some(time => time <= 0)) return qsTranslate("Flausen", "Not fully checked yet");
        const oldest = Math.min(...checks);
        const minutes = Math.floor((root.nowMs / 1000 - oldest) / 60);
        if (minutes < 1) return qsTranslate("Flausen", "Just checked");
        if (minutes < 60) return qsTranslate("Flausen", "Checked %1 min ago").arg(minutes);
        return qsTranslate("Flausen", "Checked %1").arg(UpdateHub.stamp(oldest));
    }

    width: 420 * scaleOffset
    implicitWidth: width
    spacing: 10 * scaleOffset

    function openSettings(): void {
        root.popouts.hasCurrent = false;
        WindowFactory.create(null, {initialPageIdx: Math.max(0, PageRegistry.indexForKey("updates"))});
    }
    function openSource(key: string): void {
        const source = UpdateHub.sources.find(s => s.key === key);
        if (source) UpdateHub.open(source);
    }

    RowLayout {
        // Reserve the previous heading block; new fonts must not pull cards upward.
        Layout.minimumHeight: 70 * root.fontScale / 1.15
        Layout.fillWidth: true
        Layout.topMargin: 3 * root.scaleOffset
        Layout.leftMargin: 12 * root.scaleOffset
        Layout.rightMargin: root.contentInset
        spacing: 6 * root.scaleOffset
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 4 * root.scaleOffset
            MenuText {
                Layout.fillWidth: true
                text: qsTranslate("Flausen", "Updates")
                font.weight: 600
                font.pointSize: root.titlePointSize
            }
            RowLayout {
                Layout.fillWidth: true
                spacing: 8 * root.scaleOffset
                Rectangle {
                    implicitWidth: 7 * root.scaleOffset
                    implicitHeight: implicitWidth
                    radius: height / 2
                    color: root.updateCount > 0 ? root.accent : root.muted
                }
                MenuText {
                    Layout.fillWidth: true
                    text: root.checking ? qsTranslate("Flausen", "Checking …") : root.updateCount === 1 ? qsTranslate("Flausen", "1 update available") : root.updateCount > 1 ? root.updateCount + qsTranslate("Flausen", " updates available") : root.incomplete ? qsTranslate("Flausen", "Check incomplete") : qsTranslate("Flausen", "All up to date")
                    color: root.muted
                    font.pointSize: root.bodyPointSize * 0.94
                }
            }
        }
        HeaderAction {
            icon: root.checking ? "sync" : "refresh"
            description: qsTranslate("Flausen", "Check for updates")
            enabled: !root.checking
            onClicked: { UpdateChecker.checkUpdates(); UpdateHub.refresh(); }
        }
        HeaderAction {
            icon: "settings"
            description: qsTranslate("Flausen", "Details & settings")
            onClicked: root.openSettings()
        }
    }

    SectionLabel { text: qsTranslate("Flausen", "System") }
    GroupCard {
        content: [
            StatusRow {
                label: "Caelestia"
                symbol: "desktop_windows"
                statusIcon: root.shellIcon
                detail: UpdateChecker.hasUpdate ? qsTranslate("Flausen", "Shell update available") : "Installed: " + UpdateChecker.currentVersion
                showUpdateLabel: true
                onClicked: root.openSettings()
            }
        ]
    }

    SectionLabel { text: qsTranslate("Flausen", "Games"); visible: steamCard.visible || battleCard.visible }
    GameCard {
        id: steamCard
        label: "Steam"
        desktop: "steam"
        provider: "steam"
        games: "steamGames"
    }
    GameCard {
        id: battleCard
        label: "Battle.net"
        desktop: "lab-battlenet"
        provider: "battlenet"
        games: "battlenetGames"
    }

    SectionLabel { text: "Apps"; visible: appsCard.visible }
    GroupCard {
        id: appsCard
        visible: UpdateHub.enabled("wowup") || UpdateHub.enabled("artcraft")
        content: [
            StatusRow {
                visible: UpdateHub.enabled("wowup")
                label: "WowUp"
                desktop: "lab-wowup"
                statusIcon: UpdateHub.statusIcon("wowup")
                detail: UpdateHub.details("wowup")
                onClicked: root.openSource("wowup")
            },
            Divider { visible: UpdateHub.enabled("wowup") && UpdateHub.enabled("artcraft") },
            StatusRow {
                visible: UpdateHub.enabled("artcraft")
                label: "ArtCraft Suite"
                desktop: "ai.storyteller.artcraft-launcher"
                statusIcon: UpdateHub.statusIcon("artcraft")
                detail: UpdateHub.details("artcraft")
                onClicked: root.openSource("artcraft")
            }
        ]
    }

    Rectangle {
        Layout.fillWidth: true
        Layout.leftMargin: root.contentInset
        Layout.rightMargin: root.contentInset
        Layout.topMargin: 5 * root.scaleOffset
        Layout.bottomMargin: 2 * root.scaleOffset
        implicitHeight: 1
        color: root.rule
    }
    RowLayout {
        Layout.fillWidth: true
        Layout.bottomMargin: 5 * root.scaleOffset
        Layout.leftMargin: root.contentInset
        Layout.rightMargin: root.contentInset
        spacing: 12 * root.scaleOffset
        MenuText {
            Layout.fillWidth: true
            text: root.checkedText
            color: root.muted
            font.pointSize: root.bodyPointSize * 0.84
            elide: Text.ElideRight
        }
        StyledRect {
            id: updateButton
            PrimaryControlFill {} // Capture primary material
            implicitWidth: buttonContents.implicitWidth + 24 * root.scaleOffset
            implicitHeight: 32 * root.scaleOffset
            radius: height / 2
            color: root.accent
            enabled: (root.updateCount > 0 || root.incomplete) && !root.checking
            opacity: enabled ? 1 : 0.4
            RowLayout {
                id: buttonContents
                anchors.centerIn: parent
                spacing: 7 * root.scaleOffset
                MaterialIcon {
                    text: root.updateCount > 0 ? "arrow_upward" : "check"
                    color: "white"
                    fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.fontScale * 0.9
                }
                MenuText {
                    text: root.updateCount > 0 ? qsTranslate("Flausen", "Open updates") : root.incomplete ? qsTranslate("Flausen", "Open details") : qsTranslate("Flausen", "All up to date")
                    color: "white"
                    font.weight: 600
                    font.pointSize: root.bodyPointSize * 0.94
                }
            }
            StateLayer {
                onClicked: root.openSettings()
                Accessible.name: qsTranslate("Flausen", "View available updates")
                Accessible.role: Accessible.Button
            }
        }
    }
    Timer { interval: 30000; running: true; repeat: true; onTriggered: root.nowMs = Date.now() }

    component SectionLabel: MenuText {
        Layout.minimumHeight: 24 * root.fontScale / 1.15
        verticalAlignment: Text.AlignVCenter
        Layout.leftMargin: 12 * root.scaleOffset
        Layout.topMargin: 3 * root.scaleOffset
        Layout.bottomMargin: -3 * root.scaleOffset
        color: root.muted
        font.weight: 500
        font.pointSize: root.bodyPointSize * 0.94
    }
    component GroupCard: StyledRect {
        property alias content: cardRows.data
        Layout.fillWidth: true
        Layout.leftMargin: root.contentInset
        Layout.rightMargin: root.contentInset
        implicitHeight: cardRows.implicitHeight + 4 * root.scaleOffset
        radius: 14 * root.scaleOffset
        color: MenuStyle.cardFill
        border.width: 1
        border.color: root.rule
        ColumnLayout {
            id: cardRows
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.topMargin: 2 * root.scaleOffset
            spacing: 0
        }
    }
    component Divider: Rectangle {
        property bool alignToIconEdge: false
        Layout.fillWidth: true
        Layout.leftMargin: (alignToIconEdge ? 53 : 67) * root.scaleOffset
        Layout.rightMargin: 15 * root.scaleOffset
        implicitHeight: 1
        color: root.rule
    }
    component GameCard: GroupCard {
        id: gameCard
        required property string label
        required property string desktop
        required property string provider
        required property string games
        visible: UpdateHub.enabled(provider) || UpdateHub.enabled(games)
        content: [
            StatusRow {
                visible: UpdateHub.enabled(gameCard.provider)
                label: gameCard.label
                desktop: gameCard.desktop
                subtitle: "Launcher"
                statusIcon: UpdateHub.statusIcon(gameCard.provider)
                detail: UpdateHub.details(gameCard.provider)
                onClicked: root.openSource(gameCard.provider)
            },
            Divider { alignToIconEdge: true; visible: UpdateHub.enabled(gameCard.provider) && UpdateHub.enabled(gameCard.games) },
            StatusRow {
                visible: UpdateHub.enabled(gameCard.games)
                label: qsTranslate("Flausen", "Games")
                symbol: "sports_esports"
                nested: true
                statusIcon: UpdateHub.statusIcon(gameCard.games)
                detail: UpdateHub.details(gameCard.games)
                onClicked: root.openSource(gameCard.games)
            }
        ]
    }
    component HeaderAction: StyledRect {
        id: action
        required property string icon
        required property string description
        signal clicked
        Layout.alignment: Qt.AlignTop
        implicitWidth: 38 * root.scaleOffset
        implicitHeight: 38 * root.scaleOffset
        radius: Tokens.rounding.full
        color: "transparent"
        MaterialIcon {
            anchors.centerIn: parent
            text: action.icon
            color: root.muted
            fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.fontScale * 1.2
        }
        StateLayer {
            onClicked: action.clicked()
            Accessible.name: action.description
            Accessible.role: Accessible.Button
        }
        HoverHandler { id: actionHover }
        ToolTip.visible: actionHover.hovered
        ToolTip.delay: 600
        ToolTip.text: action.description
    }
    component StatusRow: StyledRect {
        id: row
        required property string label
        required property string statusIcon
        property string subtitle
        property string desktop
        property string symbol
        property string detail
        property bool nested: false
        property bool showUpdateLabel: false
        signal clicked
        Layout.fillWidth: true
        implicitHeight: (row.showUpdateLabel ? 43 : row.subtitle ? 55 : row.nested ? 38 : 47) * root.scaleOffset
        radius: 13 * root.scaleOffset
        color: "transparent"
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: (row.nested ? 52 : 16) * root.scaleOffset
            anchors.rightMargin: 16 * root.scaleOffset
            spacing: 15 * root.scaleOffset
            Item {
                Layout.preferredWidth: (row.nested ? 26 : 37) * root.scaleOffset
                Layout.preferredHeight: 37 * root.scaleOffset
                IconImage {
                    anchors.centerIn: parent
                    implicitSize: 37 * root.scaleOffset
                    visible: !!row.desktop
                    source: row.desktop ? WinIcons.sourceFor(DesktopEntries.byId(row.desktop), "", row.desktop, 0) : ""
                }
                MaterialIcon {
                    anchors.centerIn: parent
                    visible: !!row.symbol
                    text: row.symbol
                    color: Colours.palette.m3onSurface
                    fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.fontScale * (row.nested ? 1.25 : 1.35)
                }
            }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2 * root.scaleOffset
                MenuText {
                    Layout.fillWidth: true
                    text: row.label
                    font.weight: row.nested ? 400 : 600
                    font.pointSize: root.bodyPointSize
                    elide: Text.ElideRight
                }
                MenuText {
                    visible: !!row.subtitle
                    text: row.subtitle
                    color: root.muted
                    font.pointSize: root.bodyPointSize * 0.79
                }
            }
            MaterialIcon {
                text: row.statusIcon
                fontStyle.pointSize: Tokens.font.icon.medium.pointSize * root.fontScale * 1.08
                color: row.statusIcon === "arrow_upward" ? root.accent : root.muted
            }
            MenuText {
                visible: row.showUpdateLabel && row.statusIcon === "arrow_upward"
                text: qsTranslate("Flausen", "Update available")
                color: root.accent
                font.pointSize: root.bodyPointSize * 0.9
            }
        }
        StateLayer {
            onClicked: row.clicked()
            Accessible.name: row.label + ": " + (row.statusIcon === "check" ? qsTranslate("Flausen", "Up to date") : row.statusIcon === "arrow_upward" ? qsTranslate("Flausen", "Update available") : row.statusIcon === "sync" ? qsTranslate("Flausen", "Checking") : qsTranslate("Flausen", "Status unknown"))
            Accessible.role: Accessible.Button
        }
        HoverHandler { id: rowHover }
        ToolTip.visible: rowHover.hovered && !!row.detail
        ToolTip.delay: 800
        ToolTip.text: row.detail
    }
}
