import gettext
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from language import language, preferences
from qml_messages import convert
from catalog import standalone, build


class LocalizationTests(unittest.TestCase):
    def test_kde_precedence_and_fallbacks(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder)/'plasma-localerc'
            config.write_text('[Translations]\nLANGUAGE=de_DE:en_US\n[Formats]\nLANG=en_US.UTF-8\n')
            self.assertEqual(language(config, {'LC_ALL':'en_US.UTF-8'}), 'de')
            self.assertEqual(preferences(config, {})[1], 'en_US.UTF-8')
            for preference, expected in [('en_GB:de','en'), ('fr_FR:de_AT','de'), ('C:de','en'), ('de-CH','de')]:
                config.write_text('[Translations]\nLANGUAGE='+preference+'\n')
                self.assertEqual(language(config, {}), expected)
            config.unlink()
            self.assertEqual(language(config, {'LC_MESSAGES':'de_DE.UTF-8'}), 'de')

    def test_migration_preserves_protocol_and_is_idempotent(self):
        text = '''// text: "Netzwerk"
Item {
 text: "Netzwerk"
 command: "Settings"
 action: "Paste"
 xdg: ["Network", "Settings"]
 icon: "close"
 property bool active: state === "Ready"
 property string existing: qsTr("Sprache")
 property string translated: qsTranslate("Flausen", "Network settings")
}
'''
        migrated = convert(text)
        self.assertIn('text: qsTranslate("Flausen", "Network")', migrated)
        self.assertIn('command: "Settings"', migrated)
        self.assertIn('action: "Paste"', migrated)
        self.assertIn('xdg: ["Network", "Settings"]', migrated)
        self.assertIn('state === "Ready"', migrated)
        self.assertIn('qsTr("Language")', migrated)
        self.assertEqual(convert(migrated), migrated)

    def test_catalog_placeholders_match_and_native_catalog_loads(self):
        messages = json.loads((HERE/'messages-de.json').read_text())
        for source, translated in messages.items():
            self.assertEqual(sorted(re.findall(r'%\d+|\{\w+\}', source)), sorted(re.findall(r'%\d+|\{\w+\}', translated)), source)
        qm, mo = standalone()
        self.assertTrue(qm)
        import io
        native = gettext.GNUTranslations(io.BytesIO(mo))
        self.assertEqual(native.gettext('Quick preview is unavailable for this file type.'), 'Für diesen Dateityp ist keine Schnellvorschau verfügbar.')

    def test_live_qml_switch_roundtrip(self):
        # Real Caelestia QTranslator + engine retranslation + regional calendar rules.
        qm, _ = standalone()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'plasma-localerc').write_text('[Translations]\nLANGUAGE=en_US\n')
            (root/'translations').mkdir()
            (root/'translations/caelestia_de.qm').write_bytes(qm)
            (root/'SystemLanguage.qml').write_bytes((HERE/'SystemLanguage.qml').read_bytes())
            (root/'ContextMenuStore.qml').write_bytes((HERE.parent/'desktop-context-menu/services/ContextMenuStore.qml').read_bytes())
            (root/'qmldir').write_text('singleton SystemLanguage 1.0 SystemLanguage.qml\nsingleton ContextMenuStore 1.0 ContextMenuStore.qml\n')
            (root/'shell.qml').write_text('''import QtQuick
import Quickshell
import Quickshell.Io
import Caelestia
import "." as Local
ShellRoot {
    id: root
    property string sample: qsTranslate("Flausen", "Network settings")
    property bool menuLoaded: Local.ContextMenuStore.loaded
    property int phase: 0
    Process { id: writer }
    function writeSettings(contents: string): void {
        writer.command = ["python3", "-c", "from pathlib import Path; import sys; Path(sys.argv[1]).write_text(sys.argv[2])", Quickshell.env("XDG_CONFIG_HOME") + "/plasma-localerc", contents];
        writer.running = true;
    }
    Binding { target: Translations; property: "extraSearchPaths"; value: [Qt.resolvedUrl("translations")] }
    Binding { target: Translations; property: "language"; value: Local.SystemLanguage.language }
    Timer {
        interval: 250; repeat: true; running: true
        onTriggered: {
            if (root.phase === 0) {
                Local.ContextMenuStore.entries = [{id:"system_settings", label:"Old", type:"default"}, {id:"custom", label:"My label", type:"custom"}];
                root.writeSettings("[Translations]\\nLANGUAGE=de_DE:en\\n[Formats]\\nLANG=en_US.UTF-8\\n");
            } else if (root.phase === 1) {
                if (root.sample !== "Netzwerkeinstellungen" || Local.SystemLanguage.locale.firstDayOfWeek !== 0) throw new Error("German UI / US formats failed: " + root.sample);
                if (Local.ContextMenuStore.entries[0].label !== "Einstellungen" || Local.ContextMenuStore.entries[1].label !== "My label") throw new Error("Cached menu German/custom labels failed: " + JSON.stringify(Local.ContextMenuStore.entries));
                if (Local.ContextMenuStore.defaultEntries()[0].action !== "Paste") throw new Error("Translated action identifier");
                root.writeSettings("[Translations]\\nLANGUAGE=en_US\\n[Formats]\\nLANG=de_DE.UTF-8\\n");
            } else if (root.phase === 2) {
                if (root.sample !== "Network settings" || Local.SystemLanguage.locale.firstDayOfWeek !== 1) throw new Error("English UI / German formats failed: " + root.sample);
                if (Local.ContextMenuStore.entries[0].label !== "Settings") throw new Error("Cached menu English label failed");
                root.writeSettings("[Translations]\\nLANGUAGE=de_DE\\n");
            } else {
                if (root.sample !== "Netzwerkeinstellungen") throw new Error("Return to German failed");
                console.log("ROUNDTRIP_OK"); Qt.quit();
            }
            root.phase++;
        }
    }
}
''')
            (root/'translations/caelestia_de.qm').write_bytes(build(root, {}))
            env = dict(os.environ, QT_QPA_PLATFORM='offscreen', XDG_CONFIG_HOME=str(root))
            try:
                result = subprocess.run(['quickshell', '-p', str(root)], env=env, capture_output=True, text=True, timeout=4)
            except subprocess.TimeoutExpired as exc:
                self.fail(str(exc.stdout) + str(exc.stderr))
            self.assertIn('ROUNDTRIP_OK', result.stdout+result.stderr, result.stdout+result.stderr)

if __name__ == '__main__': unittest.main()
