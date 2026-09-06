"""Repository walking and source chunking."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from xyz.ingest.chunk import Chunk, ChunkResult, chunk_file
from xyz.ingest.walk import DEFAULT_EXCLUDE, DEFAULT_INCLUDE, walk_repo


def chunk_repo(
    repo: str,
    root: str | os.PathLike[str],
    **walk_kwargs: Any,
) -> ChunkResult:
    """Walk and chunk a repository, accumulating parse and traversal warnings."""

    errors = walk_kwargs.pop("errors", None)
    if errors is None:
        errors = []
    chunks: list[Chunk] = []
    warnings: list[str] = []
    for rel_path, source in walk_repo(Path(root), errors=errors, **walk_kwargs):
        result = chunk_file(repo, rel_path, source)
        chunks.extend(result.chunks)
        warnings.extend(result.warnings)
    warnings.extend(f"walk error: {error}" for error in errors)
    return ChunkResult(chunks, warnings)


__all__ = [
    "Chunk",
    "ChunkResult",
    "DEFAULT_EXCLUDE",
    "DEFAULT_INCLUDE",
    "chunk_file",
    "chunk_repo",
    "walk_repo",
]
