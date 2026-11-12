#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import difflib
import shutil
import sys

SOURCE = Path(__file__).resolve().parent
SHELL = Path.home() / '.config/quickshell/caelestia'
BACKUP = Path.home() / '.local/state/ralleur-taskbar-backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-update-hub')


def install():
    if (SHELL / 'services/UpdateHub.qml').exists():
        if '--upgrade' not in sys.argv:
            raise SystemExit('Update-Hub bereits installiert. Für die neue Statusintegration --upgrade verwenden.')
        names = ['modules/bar/popouts/ClipWrapper.qml', 'modules/bar/popouts/Updates.qml', 'modules/bar/components/UpdateIndicator.qml', 'modules/nexus/pages/UpdatesPage.qml']
        files = {name: (SHELL / name).read_text() for name in names}
        files['services/UpdateHub.qml'] = (SOURCE / 'UpdateHub.qml').read_text()
        files['services/update-hub-probe.py'] = (SOURCE / 'probe.py').read_text()
        enrich_status(files)
        write_files(files)
        return
    files = {}
    path = 'modules/bar/popouts/Content.qml'
    text = (SHELL / path).read_text()
    text = text.replace('name: "updateIndicator"\n            sourceComponent:', 'name: "updateIndicator"\n            minScale: 1.15\n            sourceComponent:')
    files[path] = text
    path = 'modules/bar/popouts/Updates.qml'
    text = (SHELL / path).read_text()
    text = text.replace('300 * scaleOffset', '420 * scaleOffset')
    text = text.replace('return qsTr("System is up to date");', 'return "Caelestia ist aktuell";')
    text = text.replace('text: root.statusText', 'text: "Update-Hub\\n" + root.statusText')
    text = text.replace('qsTr("Last check: not yet")', '"Caelestia: noch nicht geprüft"').replace('qsTr("Last check %1 ago")', '"Caelestia: vor %1 geprüft"').replace('qsTr("Next check in %1")', '"Nächste Shell-Prüfung in %1"')
    text = text.replace('onClicked: UpdateChecker.checkUpdates()', 'onClicked: { UpdateChecker.checkUpdates(); UpdateHub.refresh(); }')
    text = text.replace('qsTr("Check for updates")', '"Update-Status aktualisieren"').replace('qsTr("Open Updates")', '"Update-Hub konfigurieren"')
    marker = '    Timer {\n        interval: 1000'
    panel = '''    StyledRect {
        Layout.fillWidth: true
        implicitHeight: sourceRows.implicitHeight + Tokens.padding.medium * 2 * root.scaleOffset
        radius: Tokens.rounding.medium * root.scaleOffset
        color: Colours.tPalette.m3surfaceContainer
        ColumnLayout {
            id: sourceRows
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: Tokens.padding.medium * root.scaleOffset
            spacing: Tokens.spacing.medium * root.scaleOffset
            Repeater {
                model: UpdateHub.sources
                delegate: ColumnLayout {
                    id: sourceRow
                    required property var modelData
                    visible: UpdateHub.enabled(modelData.key)
                    Layout.fillWidth: true
                    spacing: 2
                    StyledText {
                        Layout.fillWidth: true
                        text: sourceRow.modelData.name
                        font.pointSize: Tokens.font.body.medium.pointSize * root.fontScale
                        font.weight: 600
                    }
                    StyledText {
                        Layout.fillWidth: true
                        text: UpdateHub.checking ? "Wird geprüft …" : UpdateHub.summary(sourceRow.modelData.key)
                        font.pointSize: Tokens.font.body.medium.pointSize * root.fontScale
                        color: Colours.palette.m3onSurfaceVariant
                        wrapMode: Text.Wrap
                    }
                    TapHandler { onTapped: UpdateHub.open(sourceRow.modelData) }
                }
            }
            StyledText {
                Layout.fillWidth: true
                visible: !!UpdateHub.error
                text: UpdateHub.error
                wrapMode: Text.Wrap
                font.pointSize: Tokens.font.body.medium.pointSize * root.fontScale
                color: Colours.palette.m3error
            }
        }
    }

'''
    text = text.replace(marker, panel + marker)
    files[path] = text
    path = 'modules/nexus/pages/UpdatesPage.qml'
    text = (SHELL / path).read_text().replace('title: qsTr("Updates")', 'title: "Update-Hub"')
    marker = '        ConnectedRect {\n            visible: !root.branchDataLoading'
    panel = '''        SectionHeader { text: "Apps & Spiele" }
        StyledText {
            Layout.fillWidth: true
            text: "Quellen für die Übersicht wählen. Automatische Downloads, Zeitpläne und Spielregeln werden in der jeweiligen App eingestellt. Ausblenden im Hub stoppt keine Updates."
            wrapMode: Text.Wrap
            font: Tokens.font.body.medium
            color: Colours.palette.m3onSurfaceVariant
        }
        IconTextButton {
            text: UpdateHub.checking ? "Wird geprüft …" : "Update-Status aktualisieren"
            icon: "refresh"
            disabled: UpdateHub.checking
            type: TextButton.Tonal
            onClicked: { UpdateHub.refresh(); UpdateChecker.checkUpdates(); }
        }
        StyledText {
            Layout.fillWidth: true
            visible: !!UpdateHub.error
            text: UpdateHub.error
            wrapMode: Text.Wrap
            color: Colours.palette.m3error
        }
        Repeater {
            model: UpdateHub.sources
            delegate: ColumnLayout {
                id: provider
                required property var modelData
                Layout.fillWidth: true
                spacing: Tokens.spacing.extraSmall / 2
                ToggleRow {
                    first: true
                    text: provider.modelData.name + " im Hub anzeigen"
                    font: Tokens.font.body.medium
                    subtext: UpdateHub.summary(provider.modelData.key)
                    checked: UpdateHub.enabled(provider.modelData.key)
                    onToggled: UpdateHub.setEnabled(provider.modelData.key, checked)
                }
                StyledText {
                    Layout.fillWidth: true
                    Layout.margins: Tokens.padding.medium
                    text: provider.modelData.hint
                    wrapMode: Text.Wrap
                    font: Tokens.font.body.medium
                    color: Colours.palette.m3onSurfaceVariant
                }
                NavRow {
                    last: true
                    icon: "open_in_new"
                    label: provider.modelData.key === "steamGames" ? "Steam-Downloads öffnen" : provider.modelData.name + " öffnen & konfigurieren"
                    onClicked: UpdateHub.open(provider.modelData)
                }

            }
        }
        SectionHeader { text: "Caelestia · Desktop-Shell" }

'''
    assert marker in text
    text = text.replace(marker, panel + marker, 1)
    files[path] = text
    path = 'modules/bar/components/UpdateIndicator.qml'
    text = (SHELL / path).read_text().replace('UpdateChecker.hasUpdate', '(UpdateChecker.hasUpdate || UpdateHub.pendingCount > 0)').replace('UpdateChecker.checkingUpdates', '(UpdateChecker.checkingUpdates || UpdateHub.checking)').replace('UpdateChecker.checkUpdates();', 'UpdateChecker.checkUpdates(); UpdateHub.refresh();').replace('Caelestia updates', 'Update-Hub')
    files[path] = text
    path = 'modules/nexus/PageDictionary.qml'
    text = (SHELL / path).read_text()
    text = text.replace('label: qsTr("Updates"),\n            key: "updates",', 'label: "Update-Hub",\n            key: "updates",')
    text = text.replace('description: qsTr("System updates"),', 'description: "Caelestia, Apps und Spiele",')
    text = text.replace('{ label: qsTr("Software Updates"), keywords: ["upgrade", "packages", "pacman", "dnf", "apt"] },', '{ label: "Apps & Spiele", keywords: ["Steam", "Battle.net", "WowUp", "ArtCraft", "PhotoCraft", "LightCraft", "Updates", "Downloads", "automatisch"] },')
    files[path] = text
    files['services/UpdateHub.qml'] = (SOURCE / 'UpdateHub.qml').read_text()
    files['services/update-hub-probe.py'] = (SOURCE / 'probe.py').read_text()
    if (SHELL / 'services/UpdateHub.qml').exists():
        raise SystemExit('Update-Hub bereits installiert.')
    enrich_status(files)
    write_files(files)


def enrich_status(files):
    path = 'modules/bar/popouts/ClipWrapper.qml'
    text = files.get(path, (SHELL / path).read_text())
    text = text.replace('#dcf5f3f1', '#eff5f3f1').replace('#d41a1f26', '#ed1a1f26')
    text = text.replace('        radius: 24\n', '        radius: content.currentName === "updateIndicator" ? 28 : 24\n')
    text = text.replace('color: Colours.light ? "#e6f4f5f7" : "#d911161d"', 'color: content.currentName === "updateIndicator" ? (Colours.light ? "#eff5f3f1" : "#ed1a1f26") : (Colours.light ? "#e6f4f5f7" : "#d911161d")')
    text = text.replace('border.color: Colours.light ? "#70969ca5" : "#38ffffff"', 'border.color: content.currentName === "updateIndicator" ? (Colours.light ? "#b3ffffff" : "#4dffffff") : (Colours.light ? "#70969ca5" : "#38ffffff")')
    files[path] = text
    path = 'modules/bar/popouts/Updates.qml'
    files[path] = files[path].replace('text: UpdateHub.checking ? "Wird geprüft …" : UpdateHub.summary(sourceRow.modelData.key)', 'text: UpdateHub.compact(sourceRow.modelData.key)')
    files[path] = files[path].replace('text: "Update-Hub\\n" + root.statusText', 'text: "Update-Hub\\n" + UpdateHub.overview + "\\nCaelestia · " + root.statusText')
    files['modules/bar/popouts/Updates.qml'] = (SOURCE / 'Updates.qml').read_text()
    path = 'modules/nexus/pages/UpdatesPage.qml'
    files[path] = files[path].replace('text: provider.modelData.hint', 'text: UpdateHub.details(provider.modelData.key) + "\\n\\n" + provider.modelData.hint')
    path = 'modules/bar/components/UpdateIndicator.qml'
    files[path] = files[path].replace('root.hasUpdate ? "update" : "check_circle"', 'root.hasUpdate ? "update" : UpdateHub.hasErrors ? "error_outline" : "check_circle"')
    files[path] = files[path].replace('root.hasUpdate ? "update" : UpdateHub.hasErrors ? "error_outline" : "check_circle"', 'root.hasUpdate ? "arrow_upward" : UpdateHub.hasErrors ? "question_mark" : "check"')


def write_files(files):
    BACKUP.mkdir(parents=True)
    diff = []
    for name, value in files.items():
        target = SHELL / name
        original = target.read_text() if target.exists() else ''
        backup = BACKUP / name
        backup.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.copy2(target, backup)
        diff.extend(difflib.unified_diff(original.splitlines(True), value.splitlines(True), fromfile=name if original else '/dev/null', tofile=name))
        target.write_text(value)
    (SOURCE.parent / ('update-hub-status.patch' if '--upgrade' in sys.argv else 'update-hub.patch')).write_text(''.join(diff))
    (SOURCE.parent / 'evidence/update-hub-backup.txt').write_text(str(BACKUP) + '\n')
    print(BACKUP)


if __name__ == '__main__':
    install()
