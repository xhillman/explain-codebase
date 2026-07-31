from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from check_guide import AuditLimits, audit_guide  # noqa: E402


class GuideFixture:
    def __init__(self, root: Path) -> None:
        self.repo = root
        self.guide = root / "docs" / "codebase-guide"

    def create(self) -> None:
        (self.guide / "reference").mkdir(parents=True)
        (self.guide / "modules").mkdir()
        (self.repo / "app.py").write_text(
            "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
            encoding="utf-8",
        )
        (self.repo / "README.md").write_text("# Example project\n", encoding="utf-8")
        (self.guide / "README.md").write_text(
            "# Example guide\n\n[Coverage](reference/coverage.md)\n",
            encoding="utf-8",
        )
        (self.guide / "PROGRESS.md").write_text(
            "# Progress\n\nOverall status: complete\n",
            encoding="utf-8",
        )
        (self.guide / "modules" / "app.md").write_text(
            "# Application\n\n`app.py:L1-L2` defines the greeting. "
            "`README.md:L1` names the project.\n",
            encoding="utf-8",
        )
        self.write_coverage(include_readme=True, complete=True)
        (self.guide / "reference" / "symbol-index.md").write_text(
            """# Symbol Index

## Symbols

| Symbol | Kind | Defined at | Owned by | Called or consumed by | Detailed explanation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `greet` | function | `app.py:L1-L2` | application | callers | [Open](../modules/app.md) | verified |
""",
            encoding="utf-8",
        )

    def write_coverage(self, include_readme: bool, complete: bool) -> None:
        documentation_state = "verified" if complete else "drafted"
        decision = "complete" if complete else "incomplete"
        rows = [
            f"| `app.py` | First-party | inspected | {documentation_state} | 1 | 1 | [Guide](../modules/app.md) | None |"
        ]
        if include_readme:
            rows.append(
                f"| `README.md` | First-party | inspected | {documentation_state} | 0 | 0 | [Guide](../modules/app.md) | None |"
            )
        content = """# Coverage Ledger

## File inventory

| Path | Classification | Inspection | Documentation | Symbols discovered | Symbols documented | Guide link | Notes |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
"""
        content += "\n".join(rows)
        content += f"\n\n## Completion decision\n\n**Decision:** {decision}\n"
        (self.guide / "reference" / "coverage.md").write_text(content, encoding="utf-8")


class CheckGuideTests(unittest.TestCase):
    def audit(self, fixture: GuideFixture, allow_incomplete: bool = False):
        return audit_guide(
            fixture.repo,
            fixture.guide,
            AuditLimits(),
            allow_incomplete=allow_incomplete,
        )

    def test_complete_guide_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = GuideFixture(Path(temporary_directory))
            fixture.create()

            result = self.audit(fixture)

            self.assertEqual(result.error_count, 0, result.issues)
            self.assertEqual(result.repository_files, 2)
            self.assertEqual(result.ledger_files, 2)
            self.assertEqual(result.indexed_symbols, 1)

    def test_detects_placeholder_broken_link_and_bad_source_range(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = GuideFixture(Path(temporary_directory))
            fixture.create()
            (fixture.guide / "README.md").write_text(
                "# Guide\n\n{{UNFINISHED}}\n[Missing](missing.md)\n`app.py:L1-L99`\n",
                encoding="utf-8",
            )

            result = self.audit(fixture)
            codes = {issue.code for issue in result.issues}

            self.assertIn("placeholder", codes)
            self.assertIn("broken-link", codes)
            self.assertIn("source-line-range", codes)

    def test_detects_file_missing_from_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = GuideFixture(Path(temporary_directory))
            fixture.create()
            fixture.write_coverage(include_readme=False, complete=True)

            result = self.audit(fixture)

            self.assertIn(
                "coverage-missing-file", {issue.code for issue in result.issues}
            )

    def test_detects_missing_main_symbol_table(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = GuideFixture(Path(temporary_directory))
            fixture.create()
            (fixture.guide / "reference" / "symbol-index.md").write_text(
                "# Symbol Index\n", encoding="utf-8"
            )

            result = self.audit(fixture)

            self.assertIn("symbol-table", {issue.code for issue in result.issues})

    def test_requires_summary_reason_and_symbol_detail_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = GuideFixture(Path(temporary_directory))
            fixture.create()
            coverage_path = fixture.guide / "reference" / "coverage.md"
            coverage = coverage_path.read_text(encoding="utf-8").replace(
                "| `README.md` | First-party | inspected | verified | 0 | 0 | [Guide](../modules/app.md) | None |",
                "| `README.md` | Generated | inspected | summary-only | 0 | 0 | [Guide](../modules/app.md) | None |",
            )
            coverage_path.write_text(coverage, encoding="utf-8")
            symbol_path = fixture.guide / "reference" / "symbol-index.md"
            symbols = symbol_path.read_text(encoding="utf-8").replace(
                "[Open](../modules/app.md)", "None"
            )
            symbol_path.write_text(symbols, encoding="utf-8")

            result = self.audit(fixture)
            codes = {issue.code for issue in result.issues}

            self.assertIn("coverage-summary-reason", codes)
            self.assertIn("symbol-detail-link", codes)

    def test_direct_audit_rejects_external_guide_boundary(self) -> None:
        with (
            tempfile.TemporaryDirectory() as repository_directory,
            tempfile.TemporaryDirectory() as guide_directory,
        ):
            result = audit_guide(
                Path(repository_directory),
                Path(guide_directory),
                AuditLimits(),
            )

            self.assertEqual(result.error_count, 1)
            self.assertEqual(result.issues[0].code, "audit-boundary")

    def test_allow_incomplete_downgrades_draft_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = GuideFixture(Path(temporary_directory))
            fixture.create()
            fixture.write_coverage(include_readme=True, complete=False)

            strict_result = self.audit(fixture)
            draft_result = self.audit(fixture, allow_incomplete=True)

            self.assertGreater(strict_result.error_count, 0)
            self.assertEqual(draft_result.error_count, 0, draft_result.issues)
            self.assertGreater(draft_result.warning_count, 0)


if __name__ == "__main__":
    unittest.main()
