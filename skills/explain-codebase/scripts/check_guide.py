#!/usr/bin/env python3
"""Audit a generated codebase guide against its repository inventory."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence
from urllib.parse import unquote

from inventory_repository import (
    DEFAULT_MAX_FILES,
    InventoryError,
    build_inventory,
    normalized_relative_path,
    positive_file_limit,
    resolve_boundaries,
)


DEFAULT_MAX_DOCS = 20_000
DEFAULT_MAX_DOC_BYTES = 5_000_000
DEFAULT_MAX_SOURCE_BYTES = 20_000_000
DEFAULT_MAX_ISSUES = 1_000
MAX_ALLOWED_DOCS = 100_000
MAX_ALLOWED_BYTES = 100_000_000
MAX_ALLOWED_ISSUES = 10_000

REQUIRED_DOCUMENTS = (
    "README.md",
    "PROGRESS.md",
    "reference/coverage.md",
    "reference/symbol-index.md",
)
CLASSIFICATIONS = {
    "First-party",
    "Generated",
    "Vendored",
    "Dependency metadata",
    "Build output",
}
INSPECTION_STATES = {"not-started", "inspected", "blocked"}
DOCUMENTATION_STATES = {"not-started", "drafted", "verified", "summary-only"}
SYMBOL_STATES = {"drafted", "verified"}

PLACEHOLDER_PATTERN = re.compile(r"\{\{[^{}\n]+\}\}")
UNFINISHED_PATTERN = re.compile(
    r"\b(?:TODO|TBD)\b|document later|similar functions work similarly",
    re.IGNORECASE,
)
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SOURCE_REFERENCE_PATTERN = re.compile(
    r"`(?P<path>[^`\n:]+):L(?P<start>[1-9][0-9]*)"
    r"(?:-L(?P<end>[1-9][0-9]*))?`"
)
SEPARATOR_CELL_PATTERN = re.compile(r"^:?-{3,}:?$")


@dataclass(frozen=True)
class AuditLimits:
    max_files: int = DEFAULT_MAX_FILES
    max_docs: int = DEFAULT_MAX_DOCS
    max_doc_bytes: int = DEFAULT_MAX_DOC_BYTES
    max_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES
    max_issues: int = DEFAULT_MAX_ISSUES


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    path: str
    line: int | None
    message: str


@dataclass(frozen=True)
class MarkdownDocument:
    path: Path
    relative_path: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class LedgerSummary:
    paths: frozenset[str]
    first_party_symbols: int


@dataclass(frozen=True)
class AuditResult:
    repository_files: int
    guide_documents: int
    ledger_files: int
    indexed_symbols: int
    issues: tuple[Issue, ...]
    issues_truncated: bool

    @property
    def error_count(self) -> int:
        return sum(issue.severity == "error" for issue in self.issues)

    @property
    def warning_count(self) -> int:
        return sum(issue.severity == "warning" for issue in self.issues)


class IssueCollector:
    def __init__(self, max_issues: int) -> None:
        self._max_issues = max_issues
        self._issues: list[Issue] = []
        self.truncated = False

    @property
    def issues(self) -> tuple[Issue, ...]:
        return tuple(self._issues)

    def add(
        self,
        severity: str,
        code: str,
        path: str,
        message: str,
        line: int | None = None,
    ) -> None:
        if len(self._issues) >= self._max_issues:
            self.truncated = True
            return
        self._issues.append(Issue(severity, code, path, line, message))


def bounded_integer(name: str, maximum: int):
    def parse(raw_value: str) -> int:
        try:
            value = int(raw_value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"{name} must be an integer") from exc
        if not 1 <= value <= maximum:
            raise argparse.ArgumentTypeError(f"{name} must be between 1 and {maximum}")
        return value

    return parse


def discover_markdown_paths(
    guide: Path, max_docs: int, collector: IssueCollector
) -> tuple[Path, ...]:
    discovered: list[Path] = []
    traversal_errors: list[str] = []

    def record_error(error: OSError) -> None:
        traversal_errors.append(str(error))

    for root, directories, files in os.walk(
        guide, topdown=True, followlinks=False, onerror=record_error
    ):
        directories[:] = sorted(directories)
        for filename in sorted(files):
            if not filename.lower().endswith(".md"):
                continue
            discovered.append(Path(root) / filename)
            if len(discovered) > max_docs:
                collector.add(
                    "error",
                    "guide-doc-limit",
                    guide.as_posix(),
                    f"guide exceeds max-docs limit of {max_docs}",
                )
                return tuple(discovered[:max_docs])

    for error in traversal_errors[:5]:
        collector.add("error", "guide-traversal", guide.as_posix(), error)
    return tuple(discovered)


def load_documents(
    guide: Path, limits: AuditLimits, collector: IssueCollector
) -> tuple[MarkdownDocument, ...]:
    if not guide.is_dir():
        collector.add(
            "error", "guide-missing", guide.as_posix(), "guide directory does not exist"
        )
        return ()

    documents: list[MarkdownDocument] = []
    for path in discover_markdown_paths(guide, limits.max_docs, collector):
        relative_path = path.relative_to(guide).as_posix()
        try:
            with path.open("rb") as handle:
                content = handle.read(limits.max_doc_bytes + 1)
            if len(content) > limits.max_doc_bytes:
                collector.add(
                    "error",
                    "guide-doc-size",
                    relative_path,
                    f"document exceeds byte limit of {limits.max_doc_bytes}",
                )
                continue
            text = content.decode("utf-8")
        except (OSError, UnicodeError) as exc:
            collector.add("error", "guide-doc-read", relative_path, str(exc))
            continue
        documents.append(
            MarkdownDocument(path, relative_path, tuple(text.splitlines()))
        )
    return tuple(documents)


def check_required_documents(guide: Path, collector: IssueCollector) -> None:
    for relative_path in REQUIRED_DOCUMENTS:
        if (guide / relative_path).is_file():
            continue
        collector.add(
            "error",
            "required-document",
            relative_path,
            "required guide document is missing",
        )


def check_unfinished_content(
    document: MarkdownDocument, collector: IssueCollector
) -> None:
    for line_number, line in enumerate(document.lines, start=1):
        for match in PLACEHOLDER_PATTERN.finditer(line):
            collector.add(
                "error",
                "placeholder",
                document.relative_path,
                f"unresolved placeholder: {match.group(0)}",
                line_number,
            )
        if UNFINISHED_PATTERN.search(line):
            collector.add(
                "error",
                "unfinished-marker",
                document.relative_path,
                "unfinished documentation marker remains",
                line_number,
            )


def parse_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    return target.split(maxsplit=1)[0]


def check_links(
    document: MarkdownDocument, repo: Path, collector: IssueCollector
) -> None:
    for line_number, line in enumerate(document.lines, start=1):
        for match in MARKDOWN_LINK_PATTERN.finditer(line):
            raw_target = parse_link_target(match.group(1))
            if not raw_target or raw_target.startswith(
                ("#", "http://", "https://", "mailto:", "data:")
            ):
                continue
            path_part = unquote(raw_target.split("#", 1)[0].split("?", 1)[0])
            if not path_part:
                continue
            resolved = (document.path.parent / path_part).resolve()
            if not resolved.is_relative_to(repo):
                collector.add(
                    "error",
                    "link-outside-repository",
                    document.relative_path,
                    f"link escapes repository: {raw_target}",
                    line_number,
                )
                continue
            if not resolved.exists():
                collector.add(
                    "error",
                    "broken-link",
                    document.relative_path,
                    f"link target does not exist: {raw_target}",
                    line_number,
                )


def source_line_count(
    source: Path,
    relative_path: str,
    limits: AuditLimits,
    collector: IssueCollector,
) -> int | None:
    try:
        with source.open("rb") as handle:
            content = handle.read(limits.max_source_bytes + 1)
        if len(content) > limits.max_source_bytes:
            collector.add(
                "error",
                "source-size-limit",
                relative_path,
                f"source exceeds validation limit of {limits.max_source_bytes} bytes",
            )
            return None
    except OSError as exc:
        collector.add("error", "source-read", relative_path, str(exc))
        return None
    if b"\0" in content:
        collector.add(
            "error",
            "source-binary",
            relative_path,
            "line reference points to a binary file",
        )
        return None
    if not content:
        return 0
    return content.count(b"\n") + (0 if content.endswith(b"\n") else 1)


def check_source_references(
    document: MarkdownDocument,
    repo: Path,
    guide: Path,
    limits: AuditLimits,
    collector: IssueCollector,
    line_counts: dict[Path, int | None],
) -> None:
    for guide_line, line in enumerate(document.lines, start=1):
        for match in SOURCE_REFERENCE_PATTERN.finditer(line):
            source_path = match.group("path").strip()
            source = (repo / source_path).resolve()
            if not source.is_relative_to(repo) or source.is_relative_to(guide):
                collector.add(
                    "error",
                    "invalid-source-reference",
                    document.relative_path,
                    f"source reference is outside source scope: {source_path}",
                    guide_line,
                )
                continue
            if not source.is_file():
                collector.add(
                    "error",
                    "missing-source-reference",
                    document.relative_path,
                    f"source file does not exist: {source_path}",
                    guide_line,
                )
                continue
            if source not in line_counts:
                line_counts[source] = source_line_count(
                    source, source_path, limits, collector
                )
            available_lines = line_counts[source]
            if available_lines is None:
                continue
            start = int(match.group("start"))
            end = int(match.group("end") or start)
            if start > end or end > available_lines:
                collector.add(
                    "error",
                    "source-line-range",
                    document.relative_path,
                    f"invalid range {source_path}:L{start}-L{end}; file has {available_lines} lines",
                    guide_line,
                )


def markdown_cells(line: str) -> tuple[str, ...]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return ()
    return tuple(cell.strip() for cell in stripped[1:-1].split("|"))


def is_separator_row(cells: tuple[str, ...]) -> bool:
    return bool(cells) and all(SEPARATOR_CELL_PATTERN.fullmatch(cell) for cell in cells)


def table_rows(
    lines: tuple[str, ...], heading: str
) -> tuple[tuple[int, tuple[str, ...]], ...]:
    start_index = next(
        (index for index, line in enumerate(lines) if line.strip() == heading), None
    )
    if start_index is None:
        return ()

    rows: list[tuple[int, tuple[str, ...]]] = []
    for index in range(start_index + 1, len(lines)):
        line = lines[index]
        if line.startswith("## "):
            break
        cells = markdown_cells(line)
        if not cells or is_separator_row(cells):
            continue
        rows.append((index + 1, cells))
    return tuple(rows)


def clean_code_cell(value: str) -> str:
    cleaned = value.strip()
    if len(cleaned) >= 2 and cleaned.startswith("`") and cleaned.endswith("`"):
        return cleaned[1:-1]
    return cleaned


def integer_cell(
    value: str,
    document: MarkdownDocument,
    line_number: int,
    name: str,
    collector: IssueCollector,
) -> int | None:
    try:
        parsed = int(value)
    except ValueError:
        collector.add(
            "error",
            "coverage-count",
            document.relative_path,
            f"{name} must be a non-negative integer",
            line_number,
        )
        return None
    if parsed < 0:
        collector.add(
            "error",
            "coverage-count",
            document.relative_path,
            f"{name} must be a non-negative integer",
            line_number,
        )
        return None
    return parsed


def validate_ledger_labels(
    relative_path: str,
    classification: str,
    inspection: str,
    documentation: str,
    document: MarkdownDocument,
    line_number: int,
    collector: IssueCollector,
) -> None:
    checks = (
        (classification, CLASSIFICATIONS, "coverage-classification", "classification"),
        (inspection, INSPECTION_STATES, "coverage-inspection", "inspection state"),
        (
            documentation,
            DOCUMENTATION_STATES,
            "coverage-documentation",
            "documentation state",
        ),
    )
    for value, allowed, code, label in checks:
        if value in allowed:
            continue
        collector.add(
            "error",
            code,
            document.relative_path,
            f"unknown {label} for {relative_path}: {value}",
            line_number,
        )


def validate_ledger_path(
    relative_path: str,
    document: MarkdownDocument,
    line_number: int,
    repo: Path,
    guide: Path,
    collector: IssueCollector,
) -> str:
    try:
        normalized_path, resolved = normalized_relative_path(repo, relative_path)
    except InventoryError:
        collector.add(
            "error",
            "coverage-path",
            document.relative_path,
            f"path is outside source scope: {relative_path}",
            line_number,
        )
        return relative_path
    if resolved.is_relative_to(guide):
        collector.add(
            "error",
            "coverage-path",
            document.relative_path,
            f"path is inside guide output: {relative_path}",
            line_number,
        )
    elif not resolved.exists():
        collector.add(
            "error",
            "coverage-path",
            document.relative_path,
            f"inventoried path does not exist: {relative_path}",
            line_number,
        )
    return normalized_path


def validate_ledger_counts(
    cells: tuple[str, ...],
    relative_path: str,
    document: MarkdownDocument,
    line_number: int,
    collector: IssueCollector,
) -> tuple[int, int]:
    discovered = integer_cell(
        cells[4], document, line_number, "symbols discovered", collector
    )
    documented = integer_cell(
        cells[5], document, line_number, "symbols documented", collector
    )
    if discovered is None or documented is None:
        return 0, 0
    if documented > discovered:
        collector.add(
            "error",
            "coverage-symbol-count",
            document.relative_path,
            f"documented symbols exceed discovered symbols for {relative_path}",
            line_number,
        )
    return discovered, documented


def validate_ledger_completion(
    relative_path: str,
    classification: str,
    inspection: str,
    documentation: str,
    discovered: int,
    documented: int,
    notes: str,
    document: MarkdownDocument,
    line_number: int,
    allow_incomplete: bool,
    collector: IssueCollector,
) -> None:
    severity = "warning" if allow_incomplete else "error"
    final_state = inspection == "inspected" and documentation in {
        "verified",
        "summary-only",
    }
    if not final_state:
        collector.add(
            severity,
            "coverage-incomplete",
            document.relative_path,
            f"coverage is incomplete for {relative_path}",
            line_number,
        )
    if classification == "First-party" and documentation == "summary-only":
        collector.add(
            "error",
            "coverage-summary-only",
            document.relative_path,
            f"first-party file cannot be summary-only: {relative_path}",
            line_number,
        )
    if classification != "First-party" and documentation == "verified":
        collector.add(
            "warning",
            "coverage-detail-level",
            document.relative_path,
            f"non-first-party file is marked verified instead of summary-only: {relative_path}",
            line_number,
        )
    if (
        classification != "First-party"
        and documentation == "summary-only"
        and notes.strip().lower() in {"", "none", "n/a"}
    ):
        collector.add(
            "error",
            "coverage-summary-reason",
            document.relative_path,
            f"summary-only file needs a specific reason: {relative_path}",
            line_number,
        )
    if classification == "First-party" and discovered != documented:
        collector.add(
            severity,
            "coverage-symbol-gap",
            document.relative_path,
            f"first-party symbol counts do not match for {relative_path}",
            line_number,
        )


def check_ledger_row(
    cells: tuple[str, ...],
    line_number: int,
    document: MarkdownDocument,
    repo: Path,
    guide: Path,
    allow_incomplete: bool,
    collector: IssueCollector,
) -> tuple[str, int] | None:
    if len(cells) != 8:
        collector.add(
            "error",
            "coverage-columns",
            document.relative_path,
            f"file inventory row has {len(cells)} columns; expected 8",
            line_number,
        )
        return None

    raw_path, classification, inspection, documentation = cells[:4]
    relative_path = clean_code_cell(raw_path)
    validate_ledger_labels(
        relative_path,
        classification,
        inspection,
        documentation,
        document,
        line_number,
        collector,
    )
    normalized_path = validate_ledger_path(
        relative_path, document, line_number, repo, guide, collector
    )
    discovered, documented = validate_ledger_counts(
        cells, relative_path, document, line_number, collector
    )
    if MARKDOWN_LINK_PATTERN.fullmatch(cells[6]) is None:
        collector.add(
            "error",
            "coverage-guide-link",
            document.relative_path,
            f"coverage row needs a guide link: {relative_path}",
            line_number,
        )
    validate_ledger_completion(
        relative_path,
        classification,
        inspection,
        documentation,
        discovered,
        documented,
        cells[7],
        document,
        line_number,
        allow_incomplete,
        collector,
    )

    first_party_discovered = discovered if classification == "First-party" else 0
    return normalized_path, first_party_discovered


def audit_coverage_ledger(
    document: MarkdownDocument,
    repo: Path,
    guide: Path,
    inventory_paths: frozenset[str],
    allow_incomplete: bool,
    collector: IssueCollector,
) -> LedgerSummary:
    rows = table_rows(document.lines, "## File inventory")
    if not rows:
        collector.add(
            "error",
            "coverage-table",
            document.relative_path,
            "file inventory table is missing or empty",
        )
        return LedgerSummary(frozenset(), 0)

    ledger_paths: set[str] = set()
    discovered_symbols = 0
    for line_number, cells in rows:
        if cells and cells[0] == "Path":
            continue
        checked = check_ledger_row(
            cells, line_number, document, repo, guide, allow_incomplete, collector
        )
        if checked is None:
            continue
        relative_path, discovered = checked
        if relative_path in ledger_paths:
            collector.add(
                "error",
                "coverage-duplicate",
                document.relative_path,
                f"duplicate file inventory row: {relative_path}",
                line_number,
            )
        ledger_paths.add(relative_path)
        discovered_symbols += discovered

    severity = "warning" if allow_incomplete else "error"
    for missing_path in sorted(inventory_paths - ledger_paths):
        collector.add(
            severity,
            "coverage-missing-file",
            document.relative_path,
            f"repository file is missing from ledger: {missing_path}",
        )
    for extra_path in sorted(ledger_paths - inventory_paths):
        collector.add(
            "error",
            "coverage-extra-file",
            document.relative_path,
            f"ledger path is absent from fresh inventory: {extra_path}",
        )

    decision_line = next(
        (line for line in document.lines if line.startswith("**Decision:**")), None
    )
    is_complete = bool(
        decision_line
        and re.match(r"^\*\*Decision:\*\*\s+complete\b", decision_line, re.IGNORECASE)
    )
    if not is_complete:
        collector.add(
            severity,
            "completion-decision",
            document.relative_path,
            "coverage decision is not complete",
        )
    return LedgerSummary(frozenset(ledger_paths), discovered_symbols)


def audit_symbol_index(
    document: MarkdownDocument,
    expected_symbols: int,
    allow_incomplete: bool,
    collector: IssueCollector,
) -> int:
    if "## Symbols" not in document.lines:
        collector.add(
            "error",
            "symbol-table",
            document.relative_path,
            "main symbol table is missing",
        )
        return 0
    rows = table_rows(document.lines, "## Symbols")
    symbol_rows = tuple(
        (line, cells) for line, cells in rows if cells and cells[0] != "Symbol"
    )
    seen: set[tuple[str, str]] = set()
    severity = "warning" if allow_incomplete else "error"

    for line_number, cells in symbol_rows:
        if len(cells) != 7:
            collector.add(
                "error",
                "symbol-columns",
                document.relative_path,
                f"symbol row has {len(cells)} columns; expected 7",
                line_number,
            )
            continue
        key = (clean_code_cell(cells[0]), clean_code_cell(cells[2]))
        if SOURCE_REFERENCE_PATTERN.search(cells[2]) is None:
            collector.add(
                "error",
                "symbol-source-reference",
                document.relative_path,
                f"symbol needs a source line reference: {key[0]}",
                line_number,
            )
        if MARKDOWN_LINK_PATTERN.fullmatch(cells[5]) is None:
            collector.add(
                "error",
                "symbol-detail-link",
                document.relative_path,
                f"symbol needs a detailed explanation link: {key[0]}",
                line_number,
            )
        if key in seen:
            collector.add(
                "error",
                "symbol-duplicate",
                document.relative_path,
                f"duplicate symbol entry: {key[0]} at {key[1]}",
                line_number,
            )
        seen.add(key)
        if cells[6] not in SYMBOL_STATES:
            collector.add(
                "error",
                "symbol-state",
                document.relative_path,
                f"unknown symbol state for {key[0]}: {cells[6]}",
                line_number,
            )
        elif cells[6] != "verified":
            collector.add(
                severity,
                "symbol-incomplete",
                document.relative_path,
                f"symbol is not verified: {key[0]}",
                line_number,
            )

    if len(symbol_rows) != expected_symbols:
        collector.add(
            severity,
            "symbol-count-mismatch",
            document.relative_path,
            f"index has {len(symbol_rows)} symbols; first-party ledger count is {expected_symbols}",
        )
    return len(symbol_rows)


def document_by_path(
    documents: tuple[MarkdownDocument, ...], relative_path: str
) -> MarkdownDocument | None:
    return next(
        (document for document in documents if document.relative_path == relative_path),
        None,
    )


def audit_guide(
    repo: Path,
    guide: Path,
    limits: AuditLimits,
    allow_incomplete: bool = False,
) -> AuditResult:
    repo = repo.resolve()
    guide = guide.resolve()
    collector = IssueCollector(limits.max_issues)
    if not repo.is_dir() or guide == repo or not guide.is_relative_to(repo):
        collector.add(
            "error",
            "audit-boundary",
            guide.as_posix(),
            "guide directory must be a child of an existing repository",
        )
        return AuditResult(0, 0, 0, 0, collector.issues, collector.truncated)
    check_required_documents(guide, collector)
    documents = load_documents(guide, limits, collector)
    line_counts: dict[Path, int | None] = {}

    for document in documents:
        check_unfinished_content(document, collector)
        check_links(document, repo, collector)
        check_source_references(document, repo, guide, limits, collector, line_counts)

    try:
        inventory = build_inventory(repo, guide, limits.max_files)
    except InventoryError as exc:
        collector.add("error", "repository-inventory", repo.as_posix(), str(exc))
        inventory_paths: frozenset[str] = frozenset()
    else:
        inventory_paths = frozenset(entry.path for entry in inventory.files)

    coverage_document = document_by_path(documents, "reference/coverage.md")
    ledger = LedgerSummary(frozenset(), 0)
    if coverage_document is not None:
        ledger = audit_coverage_ledger(
            coverage_document, repo, guide, inventory_paths, allow_incomplete, collector
        )

    symbol_document = document_by_path(documents, "reference/symbol-index.md")
    indexed_symbols = 0
    if symbol_document is not None:
        indexed_symbols = audit_symbol_index(
            symbol_document, ledger.first_party_symbols, allow_incomplete, collector
        )

    return AuditResult(
        len(inventory_paths),
        len(documents),
        len(ledger.paths),
        indexed_symbols,
        collector.issues,
        collector.truncated,
    )


def print_text_result(result: AuditResult) -> None:
    for issue in result.issues:
        location = issue.path if issue.line is None else f"{issue.path}:{issue.line}"
        print(f"{issue.severity.upper()} [{issue.code}] {location}: {issue.message}")
    if result.issues_truncated:
        print("ERROR [issue-limit] additional issues were suppressed")
    print(
        "Audit summary: "
        f"{result.error_count} errors, {result.warning_count} warnings, "
        f"{result.repository_files} repository files, "
        f"{result.ledger_files} ledger files, {result.indexed_symbols} indexed symbols"
    )


def print_json_result(result: AuditResult) -> None:
    payload = {
        "errors": result.error_count,
        "warnings": result.warning_count,
        "repository_files": result.repository_files,
        "guide_documents": result.guide_documents,
        "ledger_files": result.ledger_files,
        "indexed_symbols": result.indexed_symbols,
        "issues_truncated": result.issues_truncated,
        "issues": [asdict(issue) for issue in result.issues],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    print()


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit a generated codebase guide for deterministic coverage gaps."
    )
    parser.add_argument(
        "--repo", default=".", help="Repository root. Default: current directory"
    )
    parser.add_argument("--guide-dir", default="docs/codebase-guide")
    parser.add_argument(
        "--max-files", type=positive_file_limit, default=DEFAULT_MAX_FILES
    )
    parser.add_argument(
        "--max-docs",
        type=bounded_integer("max-docs", MAX_ALLOWED_DOCS),
        default=DEFAULT_MAX_DOCS,
    )
    parser.add_argument(
        "--max-doc-bytes",
        type=bounded_integer("max-doc-bytes", MAX_ALLOWED_BYTES),
        default=DEFAULT_MAX_DOC_BYTES,
    )
    parser.add_argument(
        "--max-source-bytes",
        type=bounded_integer("max-source-bytes", MAX_ALLOWED_BYTES),
        default=DEFAULT_MAX_SOURCE_BYTES,
    )
    parser.add_argument(
        "--max-issues",
        type=bounded_integer("max-issues", MAX_ALLOWED_ISSUES),
        default=DEFAULT_MAX_ISSUES,
    )
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Report draft coverage gaps as warnings",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        repo, guide = resolve_boundaries(args.repo, args.guide_dir)
    except InventoryError as exc:
        print(f"audit error: {exc}", file=sys.stderr)
        return 2

    limits = AuditLimits(
        args.max_files,
        args.max_docs,
        args.max_doc_bytes,
        args.max_source_bytes,
        args.max_issues,
    )
    result = audit_guide(repo, guide, limits, args.allow_incomplete)
    if args.format == "json":
        print_json_result(result)
    else:
        print_text_result(result)
    return 1 if result.error_count or result.issues_truncated else 0


if __name__ == "__main__":
    raise SystemExit(main())
