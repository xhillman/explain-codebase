#!/usr/bin/env python3
"""Produce a bounded, deterministic inventory for a repository guide."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Iterable, Sequence


DEFAULT_MAX_FILES = 100_000
MAX_ALLOWED_FILES = 1_000_000
GIT_TIMEOUT_SECONDS = 30
BINARY_SAMPLE_BYTES = 8_192
GIT_READ_BYTES = 65_536
MAX_PATH_BYTES = 65_536

LOCKFILE_NAMES = {
    "bun.lock",
    "bun.lockb",
    "cargo.lock",
    "composer.lock",
    "gemfile.lock",
    "go.sum",
    "package-lock.json",
    "packages.lock.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",
    "yarn.lock",
}
VENDORED_PARTS = {"third_party", "third-party", "vendor", "vendored"}
BUILD_PARTS = {"build", "coverage", "dist", "out", "target"}
GENERATED_MARKERS = {"generated", "autogen", "auto-generated"}
FALLBACK_EXCLUDED_DIRECTORIES = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    "__pycache__",
    "node_modules",
}
FALLBACK_EXCLUDED_FILE_NAMES = {".DS_Store"}
FALLBACK_EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


class InventoryError(RuntimeError):
    """Report a repository boundary or inventory failure."""


@dataclass(frozen=True)
class InventoryEntry:
    path: str
    source: str
    path_kind: str
    size_bytes: int | None
    is_symlink: bool
    binary_hint: bool | None
    classification_hint: str
    inspection_error: str | None


@dataclass(frozen=True)
class InventoryResult:
    repository: str
    guide_directory: str
    discovery_method: str
    max_files: int
    files: tuple[InventoryEntry, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "repository": self.repository,
            "guide_directory": self.guide_directory,
            "discovery_method": self.discovery_method,
            "limits": {"max_files": self.max_files},
            "totals": {
                "files": len(self.files),
                "tracked": sum(entry.source == "tracked" for entry in self.files),
                "untracked": sum(entry.source == "untracked" for entry in self.files),
                "filesystem": sum(entry.source == "filesystem" for entry in self.files),
                "inspection_errors": sum(
                    entry.inspection_error is not None for entry in self.files
                ),
            },
            "classification_hints_are_authoritative": False,
            "files": [asdict(entry) for entry in self.files],
        }


def positive_file_limit(raw_value: str) -> int:
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("max-files must be an integer") from exc
    if not 1 <= value <= MAX_ALLOWED_FILES:
        raise argparse.ArgumentTypeError(
            f"max-files must be between 1 and {MAX_ALLOWED_FILES}"
        )
    return value


def resolve_boundaries(repo_value: str, guide_value: str) -> tuple[Path, Path]:
    repo = Path(repo_value).expanduser().resolve()
    if not repo.is_dir():
        raise InventoryError(f"repository is not a directory: {repo}")

    guide_candidate = Path(guide_value).expanduser()
    guide = (
        guide_candidate.resolve()
        if guide_candidate.is_absolute()
        else (repo / guide_candidate).resolve()
    )
    if guide == repo or not guide.is_relative_to(repo):
        raise InventoryError("guide directory must be a child of the repository")
    return repo, guide


def read_git_paths(
    stream: BinaryIO,
    process: subprocess.Popen[bytes],
    max_paths: int,
    paths: list[str],
    errors: list[InventoryError],
) -> None:
    buffer = bytearray()
    try:
        while chunk := stream.read(GIT_READ_BYTES):
            buffer.extend(chunk)
            while b"\0" in buffer:
                separator = buffer.index(0)
                raw_path = bytes(buffer[:separator])
                del buffer[: separator + 1]
                if len(raw_path) > MAX_PATH_BYTES:
                    raise InventoryError(
                        f"Git inventory path exceeds {MAX_PATH_BYTES} bytes"
                    )
                if raw_path:
                    paths.append(os.fsdecode(raw_path))
                if len(paths) > max_paths:
                    raise InventoryError(
                        f"Git inventory exceeds max-files limit of {max_paths}"
                    )
            if len(buffer) > MAX_PATH_BYTES:
                raise InventoryError(
                    f"Git inventory path exceeds {MAX_PATH_BYTES} bytes"
                )
        if buffer:
            raise InventoryError("Git inventory returned an unterminated path")
    except (InventoryError, OSError) as exc:
        inventory_error = (
            exc
            if isinstance(exc, InventoryError)
            else InventoryError(f"failed to read Git inventory: {exc}")
        )
        errors.append(inventory_error)
        try:
            process.kill()
        except OSError:
            pass


def run_git_paths(
    repo: Path, arguments: Sequence[str], max_paths: int
) -> tuple[str, ...] | None:
    command = ["git", "-C", str(repo), "ls-files", "-z", *arguments]
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return None

    if process.stdout is None:
        process.kill()
        process.wait()
        raise InventoryError("Git inventory did not provide a readable output stream")

    paths: list[str] = []
    errors: list[InventoryError] = []
    reader = threading.Thread(
        target=read_git_paths,
        args=(process.stdout, process, max_paths, paths, errors),
        daemon=True,
    )
    reader.start()
    try:
        return_code = process.wait(timeout=GIT_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        reader.join()
        process.stdout.close()
        return None

    reader.join(timeout=5)
    if reader.is_alive():
        process.stdout.close()
        reader.join(timeout=1)
        return None
    process.stdout.close()
    if errors:
        raise errors[0]
    if return_code != 0:
        return None
    return tuple(paths)


def git_discovery(repo: Path, max_files: int) -> dict[str, str] | None:
    tracked = run_git_paths(repo, ("--cached",), max_files)
    if tracked is None:
        return None
    remaining_files = max_files - len(tracked)
    untracked = run_git_paths(repo, ("--others", "--exclude-standard"), remaining_files)
    if tracked is None or untracked is None:
        return None

    discovered = {path: "tracked" for path in tracked}
    for path in untracked:
        discovered.setdefault(path, "untracked")
    return discovered


def filesystem_discovery(repo: Path, guide: Path, max_files: int) -> dict[str, str]:
    discovered: dict[str, str] = {}
    walk_errors: list[str] = []

    def record_error(error: OSError) -> None:
        walk_errors.append(str(error))

    for current_root, directories, files in os.walk(
        repo, topdown=True, followlinks=False, onerror=record_error
    ):
        current = Path(current_root)
        retained_directories: list[str] = []
        for directory in sorted(directories):
            absolute_directory = current / directory
            if absolute_directory.is_symlink():
                relative_path = absolute_directory.relative_to(repo).as_posix()
                discovered[relative_path] = "filesystem"
                if len(discovered) > max_files:
                    raise InventoryError(
                        f"filesystem inventory exceeds max-files limit of {max_files}"
                    )
                continue
            if directory in FALLBACK_EXCLUDED_DIRECTORIES:
                continue
            if absolute_directory.resolve().is_relative_to(guide):
                continue
            retained_directories.append(directory)
        directories[:] = retained_directories
        for filename in sorted(files):
            if filename in FALLBACK_EXCLUDED_FILE_NAMES:
                continue
            if Path(filename).suffix.lower() in FALLBACK_EXCLUDED_SUFFIXES:
                continue
            absolute_path = current / filename
            if absolute_path.resolve().is_relative_to(guide):
                continue
            relative_path = absolute_path.relative_to(repo).as_posix()
            discovered[relative_path] = "filesystem"
            if len(discovered) > max_files:
                raise InventoryError(
                    f"filesystem inventory exceeds max-files limit of {max_files}"
                )

    if walk_errors:
        details = "; ".join(walk_errors[:5])
        raise InventoryError(f"filesystem traversal failed: {details}")
    return discovered


def normalized_relative_path(repo: Path, raw_path: str) -> tuple[str, Path]:
    pure_path = PurePosixPath(raw_path)
    if pure_path.is_absolute() or ".." in pure_path.parts:
        raise InventoryError(
            f"unsafe repository path returned by discovery: {raw_path}"
        )
    absolute_path = repo / Path(*pure_path.parts)
    return pure_path.as_posix(), absolute_path


def classification_hint(relative_path: str) -> str:
    path = PurePosixPath(relative_path)
    lower_parts = {part.lower() for part in path.parts}
    lower_name = path.name.lower()
    if lower_name in LOCKFILE_NAMES or lower_name.endswith(".lock"):
        return "dependency-metadata"
    if lower_parts & VENDORED_PARTS:
        return "vendored"
    if lower_parts & BUILD_PARTS:
        return "build-output"
    if any(marker in lower_name for marker in GENERATED_MARKERS):
        return "generated"
    return "first-party-candidate"


def inspect_path(
    relative_path: str, absolute_path: Path, source: str
) -> InventoryEntry:
    try:
        stat_result = absolute_path.lstat()
        is_symlink = absolute_path.is_symlink()
        if is_symlink:
            return InventoryEntry(
                relative_path,
                source,
                "symlink",
                stat_result.st_size,
                True,
                None,
                classification_hint(relative_path),
                None,
            )
        if absolute_path.is_dir():
            return InventoryEntry(
                relative_path,
                source,
                "directory",
                stat_result.st_size,
                False,
                None,
                "repository-link",
                None,
            )
        with absolute_path.open("rb") as handle:
            sample = handle.read(BINARY_SAMPLE_BYTES)
        return InventoryEntry(
            relative_path,
            source,
            "file",
            stat_result.st_size,
            False,
            b"\0" in sample,
            classification_hint(relative_path),
            None,
        )
    except OSError as exc:
        return InventoryEntry(
            relative_path,
            source,
            "unknown",
            None,
            absolute_path.is_symlink(),
            None,
            classification_hint(relative_path),
            str(exc),
        )


def build_inventory(
    repo: Path, guide: Path, max_files: int = DEFAULT_MAX_FILES
) -> InventoryResult:
    repo = repo.resolve()
    guide = guide.resolve()
    if not repo.is_dir():
        raise InventoryError(f"repository is not a directory: {repo}")
    if guide == repo or not guide.is_relative_to(repo):
        raise InventoryError("guide directory must be a child of the repository")

    discovered = git_discovery(repo, max_files)
    discovery_method = "git"
    if discovered is None:
        discovered = filesystem_discovery(repo, guide, max_files)
        discovery_method = "filesystem"

    filtered: list[tuple[str, Path, str]] = []
    for raw_path, source in discovered.items():
        relative_path, absolute_path = normalized_relative_path(repo, raw_path)
        if absolute_path.is_relative_to(guide):
            continue
        filtered.append((relative_path, absolute_path, source))

    filtered.sort(key=lambda item: item[0])
    if len(filtered) > max_files:
        raise InventoryError(
            f"inventory contains {len(filtered)} files; max-files is {max_files}"
        )

    entries = tuple(
        inspect_path(relative_path, absolute_path, source)
        for relative_path, absolute_path, source in filtered
    )
    guide_relative = guide.relative_to(repo).as_posix()
    return InventoryResult(
        str(repo), guide_relative, discovery_method, max_files, entries
    )


def paths_output(entries: Iterable[InventoryEntry]) -> str:
    return "\n".join(entry.path for entry in entries)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a deterministic repository file inventory."
    )
    parser.add_argument(
        "--repo", default=".", help="Repository root. Default: current directory"
    )
    parser.add_argument(
        "--guide-dir",
        default="docs/codebase-guide",
        help="Guide output directory to exclude from inventory",
    )
    parser.add_argument(
        "--max-files", type=positive_file_limit, default=DEFAULT_MAX_FILES
    )
    parser.add_argument("--format", choices=("json", "paths"), default="json")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        repo, guide = resolve_boundaries(args.repo, args.guide_dir)
        inventory = build_inventory(repo, guide, args.max_files)
    except InventoryError as exc:
        print(f"inventory error: {exc}", file=sys.stderr)
        return 2

    if args.format == "paths":
        print(paths_output(inventory.files))
        return 0
    json.dump(inventory.to_dict(), sys.stdout, indent=2, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
