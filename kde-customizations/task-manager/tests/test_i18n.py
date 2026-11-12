import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n import Language


class LanguageTest(unittest.TestCase):
    def test_kde_language_precedes_environment_and_changes_live(self):
        with tempfile.TemporaryDirectory() as folder:
            config=Path(folder)/'plasma-localerc'
            config.write_text('[Translations]\nLANGUAGE=en_US\n')
            language=Language(config,{'LANGUAGE':'de_DE','LANG':'de_DE.UTF-8'})
            self.assertEqual(language.translate('Performance'),'Performance')
            config.write_text('[Translations]\nLANGUAGE=de_DE:en_US\n')
            language.refresh()
            self.assertEqual(language.translate('Performance'),'Leistung')
            self.assertEqual(language.translate('Core {number}',number=2),'Kern 2')

    def test_environment_and_unsupported_language_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            missing=Path(folder)/'missing'
            self.assertEqual(Language(missing,{'LC_MESSAGES':'de_DE.UTF-8'}).language,'de')
            self.assertEqual(Language(missing,{'LANG':'fr_FR.UTF-8'}).language,'en')
            self.assertEqual(Language(missing,{'LANG':'C.UTF-8'}).language,'en')

    def test_all_literal_ui_messages_have_a_german_catalog_entry(self):
        root=Path(__file__).resolve().parents[1]
        catalog=json.loads((root/'locales/de.json').read_text())
        source=(root/'ui/TaskManager.qml').read_text()
        messages=re.findall(r'win\.tr\([\'"]([^\'"\n]+)[\'"]\)',source)
        self.assertGreater(len(messages),60)
        self.assertEqual(sorted(set(messages)-catalog.keys()),[])
