"""Check catalogue errors using isolated trees, without any desktop access."""

import contextlib
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
CLI = runpy.run_path(str(ROOT / "bin/flausen"))


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "installation").mkdir()
        source = self.root / "kde-customizations/example"
        source.mkdir(parents=True)
        (source / "README.md").write_text("# Example\n", encoding="utf-8")
        self.component = {
            "id": "example", "name": "Example", "layer": "shell",
            "source": "kde-customizations/example",
            "documentation": "kde-customizations/example/README.md",
        }

    def write_catalogue(self, components=None, version=1):
        data = {"schema_version": version, "components": components or [self.component]}
        (self.root / CLI["CATALOGUE"]).write_text(json.dumps(data), encoding="utf-8")

    def test_real_repository(self):
        self.assertTrue(CLI["load_components"](ROOT))

    def test_new_desktop_component_requires_registration(self):
        self.write_catalogue()
        (self.root / "kde-customizations/new").mkdir()
        with self.assertRaisesRegex(ValueError, "Nicht registrierte.*new"):
            CLI["load_components"](self.root)

    def test_duplicate_ids_and_sources_are_rejected(self):
        for duplicate in (dict(self.component), dict(self.component, id="another")):
            with self.subTest(duplicate=duplicate):
                self.write_catalogue([self.component, duplicate])
                with self.assertRaisesRegex(ValueError, "Doppelte"):
                    CLI["load_components"](self.root)

    def test_missing_source_and_documentation_are_rejected(self):
        for field in ("source", "documentation"):
            with self.subTest(field=field):
                self.write_catalogue([dict(self.component, **{field: "missing"})])
                with self.assertRaisesRegex(ValueError, "fehlt"):
                    CLI["load_components"](self.root)

    def test_external_paths_are_rejected(self):
        for path in ("../outside", str(self.root)):
            with self.subTest(path=path):
                self.write_catalogue([dict(self.component, source=path)])
                with self.assertRaisesRegex(ValueError, "relativ"):
                    CLI["load_components"](self.root)

    def test_symlink_cannot_escape_repository(self):
        (self.root / "external").symlink_to(self.root.parent, target_is_directory=True)
        self.write_catalogue([dict(self.component, source="external")])
        with self.assertRaisesRegex(ValueError, "verlässt"):
            CLI["load_components"](self.root)

    def test_invalid_schema_or_layer_is_rejected(self):
        self.write_catalogue(version=2)
        with self.assertRaisesRegex(ValueError, "schema_version"):
            CLI["load_components"](self.root)
        self.write_catalogue([dict(self.component, layer="unknown")])
        with self.assertRaisesRegex(ValueError, "Unbekannter Bereich"):
            CLI["load_components"](self.root)

    def test_cli_filter_is_machine_readable(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(CLI["main"](["components", "--layer", "wm", "--json"]), 0)
        components = json.loads(output.getvalue())
        self.assertTrue(components)
        self.assertTrue(all(component["layer"] == "wm" for component in components))


if __name__ == "__main__":
    unittest.main()
