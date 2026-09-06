"""Deterministic, failure-aware repository traversal."""

from __future__ import annotations

import fnmatch
import os
from collections.abc import Iterator, Sequence, Set
from pathlib import Path


DEFAULT_INCLUDE = frozenset(
    {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".php",
        ".md",
        ".go",
        ".rb",
        ".sh",
        ".yml",
        ".yaml",
        ".toml",
        ".ini",
        ".cfg",
        ".json",
        ".sql",
        ".html",
        ".twig",
        "Dockerfile",
        "docker-compose*.yml",
        "Makefile",
        "*.blade.php",
        ".env.example",
    }
)

DEFAULT_EXCLUDE = frozenset(
    {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
        "temp",
        ".embed-tmp",
        ".xyz",
        ".relay-scratch",
        "marathon-system",
        "relay-system",
    }
)

MAX_FILE_BYTES = 1024 * 1024
BINARY_SNIFF_BYTES = 8192


def _included(name: str, include: Set[str] | Sequence[str]) -> bool:
    suffix = Path(name).suffix.lower()
    for rule in include:
        if rule.startswith(".") and "*" not in rule:
            if rule == suffix or rule == name:
                return True
        elif fnmatch.fnmatchcase(name, rule):
            return True
    return False


def _normalise_prefixes(prefixes: Sequence[str] | None) -> tuple[str, ...] | None:
    if prefixes is None:
        return None
    normalised: list[str] = []
    for prefix in prefixes:
        value = prefix.replace(os.sep, "/")
        if value.startswith("./"):
            value = value[2:]
        value = value.lstrip("/")
        if value and not value.endswith("/"):
            value += "/"
        normalised.append(value)
    return tuple(sorted(set(normalised)))


def _directory_may_match(rel_dir: str, prefixes: tuple[str, ...] | None) -> bool:
    if prefixes is None:
        return True
    directory = f"{rel_dir}/" if rel_dir else ""
    return any(prefix.startswith(directory) or directory.startswith(prefix) for prefix in prefixes)


def _file_matches(rel_path: str, prefixes: tuple[str, ...] | None) -> bool:
    return prefixes is None or any(rel_path.startswith(prefix) for prefix in prefixes)


def walk_repo(
    root: str | os.PathLike[str],
    include_ext: Set[str] | Sequence[str] = DEFAULT_INCLUDE,
    exclude_dirs: Set[str] | Sequence[str] = DEFAULT_EXCLUDE,
    include_prefixes: Sequence[str] | None = None,
    *,
    errors: list[str],
) -> Iterator[tuple[str, bytes]]:
    """Yield included ``(relative_path, content)`` pairs in sorted order.

    Enumeration, stat, and read failures for relevant candidate paths are
    recorded in ``errors``. Intentional filters are silent.
    """

    root_path = Path(root)
    if not root_path.is_dir():
        raise ValueError(f"repository root is not an existing directory: {root_path}")

    excluded = set(exclude_dirs)
    prefixes = _normalise_prefixes(include_prefixes)

    def visit(directory: Path, rel_dir: str) -> Iterator[tuple[str, bytes]]:
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError as exc:
            label = rel_dir or "."
            errors.append(f"{label}: {type(exc).__name__}: {exc}")
            return

        for entry in entries:
            rel_path = f"{rel_dir}/{entry.name}" if rel_dir else entry.name
            rel_path = rel_path.replace(os.sep, "/")
            try:
                is_dir = entry.is_dir(follow_symlinks=False)
                is_file = entry.is_file(follow_symlinks=False)
            except OSError as exc:
                errors.append(f"{rel_path}: {type(exc).__name__}: {exc}")
                continue

            if is_dir:
                if entry.name in excluded or not _directory_may_match(rel_path, prefixes):
                    continue
                yield from visit(Path(entry.path), rel_path)
                continue

            if not is_file or not _file_matches(rel_path, prefixes):
                continue
            if not _included(entry.name, include_ext):
                continue

            try:
                if entry.stat(follow_symlinks=False).st_size > MAX_FILE_BYTES:
                    continue
                with open(entry.path, "rb") as handle:
                    head = handle.read(BINARY_SNIFF_BYTES)
                    if b"\0" in head:
                        continue
                    content = head + handle.read()
            except OSError as exc:
                errors.append(f"{rel_path}: {type(exc).__name__}: {exc}")
                continue
            yield rel_path, content

    yield from visit(root_path, "")
