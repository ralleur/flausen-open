#!/usr/bin/env python3
"""Exercise rollback on real temporary metadata and non-owned bookmark edits."""
import base64
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location("installer", Path(__file__).resolve().parents[1] / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallerTest(unittest.TestCase):
    def test_metadata_rollback_preserves_external_edits(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            journal = root / "journal"
            journal.mkdir()
            for name, existed, edited in [("created", False, False), ("existing", True, False), ("edited", True, True)]:
                folder = root / name
                folder.mkdir()
                path = folder / ".directory"
                before = b"[Desktop Entry]\nComment=Original\nIcon=folder-blue\n"
                path.write_bytes(b"[Desktop Entry]\nIcon=folder-yellow\n")
                info = folder.stat()
                (journal / (name+".json")).write_text(json.dumps({"path": str(path), "identity": f"{info.st_dev}:{info.st_ino}",
                    "existedBefore": existed, "before": base64.b64encode(before).decode(), "mode": 0o640,
                    "lastDigest": installer.digest(path)}))
                if edited:
                    path.write_text("Changed by user")
            self.assertEqual(installer.restore_folder_colors(journal), (2, 1))
            self.assertFalse((root / "created/.directory").exists())
            self.assertEqual((root / "existing/.directory").read_bytes(), before)
            self.assertEqual((root / "existing/.directory").stat().st_mode & 0o777, 0o640)
            self.assertEqual((root / "edited/.directory").read_text(), "Changed by user")

    def test_bookmarks_keep_unrelated_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            old_data = installer.DATA
            installer.DATA = Path(temp)
            try:
                folder = Path(subprocess.check_output(["xdg-user-dir", "PICTURES"], text=True).strip())
                path = installer.DATA / "user-places.xbel"
                path.write_text(f'''<xbel xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"><bookmark href="{folder.as_uri()}"><title>Keep title</title><info><metadata><bookmark:icon name="old-picture"/><ID>keep-id</ID></metadata></info></bookmark></xbel>''')
                records = installer.places_icons()
                self.assertEqual(len(records), 1)
                path.write_text(path.read_text().replace("Keep title", "User renamed"))
                installer.places_icons(records, restoring=True)
                tree = ET.parse(path)
                self.assertEqual(tree.find(".//title").text, "User renamed")
                self.assertEqual(tree.find(".//ID").text, "keep-id")
                self.assertEqual(tree.find(".//{http://www.freedesktop.org/standards/desktop-bookmarks}icon").get("name"), "old-picture")
            finally:
                installer.DATA = old_data


if __name__ == "__main__":
    unittest.main()
