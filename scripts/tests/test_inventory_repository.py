from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from inventory_repository import InventoryError, build_inventory, inspect_path  # noqa: E402


class InventoryRepositoryTests(unittest.TestCase):
    def test_inventory_is_sorted_classified_and_excludes_guide(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = Path(temporary_directory)
            guide = repo / "docs" / "codebase-guide"
            guide.mkdir(parents=True)
            (repo / "app.py").write_text("print('hello')\n", encoding="utf-8")
            (repo / "package-lock.json").write_text("{}\n", encoding="utf-8")
            vendor = repo / "vendor"
            vendor.mkdir()
            (vendor / "library.js").write_text("export {};\n", encoding="utf-8")
            cache = repo / "__pycache__"
            cache.mkdir()
            (cache / "app.pyc").write_bytes(b"cache")
            (guide / "README.md").write_text("generated guide\n", encoding="utf-8")

            inventory = build_inventory(repo, guide)

            paths = [entry.path for entry in inventory.files]
            self.assertEqual(paths, sorted(paths))
            self.assertEqual(
                paths, ["app.py", "package-lock.json", "vendor/library.js"]
            )
            hints = {entry.path: entry.classification_hint for entry in inventory.files}
            self.assertEqual(hints["app.py"], "first-party-candidate")
            self.assertEqual(hints["package-lock.json"], "dependency-metadata")
            self.assertEqual(hints["vendor/library.js"], "vendored")

    def test_inventory_enforces_file_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = Path(temporary_directory)
            guide = repo / "docs" / "codebase-guide"
            guide.mkdir(parents=True)
            (repo / "one.txt").write_text("one\n", encoding="utf-8")
            (repo / "two.txt").write_text("two\n", encoding="utf-8")

            with self.assertRaisesRegex(InventoryError, "max-files limit of 1"):
                build_inventory(repo, guide, max_files=1)

    def test_inventory_records_symlink_without_following_target(self) -> None:
        with (
            tempfile.TemporaryDirectory() as temporary_directory,
            tempfile.TemporaryDirectory() as target_directory,
        ):
            repo = Path(temporary_directory)
            guide = repo / "docs" / "codebase-guide"
            guide.mkdir(parents=True)
            target = Path(target_directory) / "target"
            target.write_text("outside\n", encoding="utf-8")
            link = repo / "outside-link"
            try:
                link.symlink_to(target)
                inventory = build_inventory(repo, guide)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")

            entry = next(
                item for item in inventory.files if item.path == "outside-link"
            )
            self.assertTrue(entry.is_symlink)
            self.assertEqual(entry.path_kind, "symlink")
            self.assertIsNone(entry.binary_hint)

    def test_inventory_records_symlinked_directory_without_traversing_it(self) -> None:
        with (
            tempfile.TemporaryDirectory() as temporary_directory,
            tempfile.TemporaryDirectory() as target_directory,
        ):
            repo = Path(temporary_directory)
            guide = repo / "docs" / "codebase-guide"
            guide.mkdir(parents=True)
            target = Path(target_directory) / "external-project"
            target.mkdir()
            (target / "external.py").write_text("outside = True\n", encoding="utf-8")
            link = repo / "linked-project"
            try:
                link.symlink_to(target, target_is_directory=True)
                inventory = build_inventory(repo, guide)
            except OSError as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")

            self.assertEqual(
                [entry.path for entry in inventory.files], ["linked-project"]
            )
            self.assertEqual(inventory.files[0].path_kind, "symlink")

    def test_inspection_supports_repository_link_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory) / "linked-project"
            directory.mkdir()

            entry = inspect_path("linked-project", directory, "tracked")

            self.assertEqual(entry.path_kind, "directory")
            self.assertEqual(entry.classification_hint, "repository-link")
            self.assertIsNone(entry.inspection_error)


if __name__ == "__main__":
    unittest.main()
