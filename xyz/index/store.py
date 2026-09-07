"""SQLite-backed chunk, lexical, vector, and embedding-cache store."""

from __future__ import annotations

import hashlib
import os
import sqlite3
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import sqlite_vec

from xyz.index.embed import Embedder
from xyz.ingest import Chunk, ChunkResult, chunk_file, chunk_repo, walk_repo


SCHEMA_VERSION = "1"


class StoreError(RuntimeError):
    """Base class for index-store failures."""


class IndexMismatch(StoreError):
    """The requested embedder does not match the index metadata."""


class EmptyCorpus(StoreError):
    """A traversal completed successfully but found no indexable files."""


class WalkIncomplete(StoreError):
    """A traversal could not prove a complete view of its requested scope."""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("repository walk incomplete: " + "; ".join(self.errors))


@dataclass(frozen=True)
class IngestReport:
    files_seen: int
    files_skipped: int
    files_reingested: int
    files_pruned: int
    chunks_written: int
    chunks_embedded: int
    cache_hits: int
    warnings: tuple[str, ...]
    seconds: float


@dataclass(frozen=True)
class StoreStats:
    chunks: int
    chunks_fts: int
    chunks_vec: int
    embed_cache: int
    files: int

    def __getitem__(self, key: str) -> int:
        return getattr(self, key)


def _normalise_prefixes(prefixes: Sequence[str] | None) -> tuple[str, ...] | None:
    if prefixes is None:
        return None
    result: set[str] = set()
    for prefix in prefixes:
        value = prefix.replace(os.sep, "/")
        if value.startswith("./"):
            value = value[2:]
        value = value.lstrip("/")
        if value and not value.endswith("/"):
            value += "/"
        result.add(value)
    return tuple(sorted(result))


def _in_scope(path: str, prefixes: tuple[str, ...] | None) -> bool:
    return prefixes is None or any(path.startswith(prefix) for prefix in prefixes)


class Store:
    """The sole writer for an XYZ index."""

    def __init__(self, connection: sqlite3.Connection, embedder: Embedder) -> None:
        self.connection = connection
        self.embedder = embedder

    @classmethod
    def open(cls, db_path: str | os.PathLike[str], embedder: Embedder) -> Store:
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        store = cls(connection, embedder)
        try:
            has_meta = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'meta'"
            ).fetchone()
            if has_meta:
                store.check_embedder(embedder)
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA journal_mode=WAL")
            connection.enable_load_extension(True)
            sqlite_vec.load(connection)
            connection.enable_load_extension(False)
            store._initialise_schema()
            store.check_embedder(embedder)
        except Exception:
            connection.close()
            raise
        return store

    def _initialise_schema(self) -> None:
        dim = int(self.embedder.dim)
        if dim <= 0:
            raise ValueError(f"embedder dim must be positive, got {dim}")
        with self.connection:
            self.connection.executescript(
                f"""
                CREATE TABLE IF NOT EXISTS meta(
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS files(
                    repo TEXT NOT NULL,
                    path TEXT NOT NULL,
                    file_sha TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    ingested_at TEXT NOT NULL,
                    PRIMARY KEY(repo, path)
                );
                CREATE TABLE IF NOT EXISTS chunks(
                    id INTEGER PRIMARY KEY,
                    repo TEXT NOT NULL,
                    path TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    qualified_name TEXT NOT NULL,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    content_sha TEXT NOT NULL,
                    text TEXT NOT NULL,
                    embedded_text TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS chunks_repo_path ON chunks(repo, path);
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    embedded_text,
                    qualified_name,
                    path,
                    content='chunks',
                    content_rowid='id'
                );
                CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
                    VALUES (new.id, new.embedded_text, new.qualified_name, new.path);
                END;
                CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
                    VALUES ('delete', old.id, old.embedded_text, old.qualified_name, old.path);
                END;
                CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
                    VALUES ('delete', old.id, old.embedded_text, old.qualified_name, old.path);
                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
                    VALUES (new.id, new.embedded_text, new.qualified_name, new.path);
                END;
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
                    embedding float[{dim}]
                );
                CREATE TABLE IF NOT EXISTS embed_cache(
                    content_sha TEXT NOT NULL,
                    model TEXT NOT NULL,
                    dim INTEGER NOT NULL,
                    provider TEXT NOT NULL,
                    vector BLOB NOT NULL,
                    PRIMARY KEY(content_sha, model, dim, provider)
                );
                """
            )
            current = dict(self.connection.execute("SELECT key, value FROM meta"))
            if not current:
                self.connection.executemany(
                    "INSERT INTO meta(key, value) VALUES (?, ?)",
                    (
                        ("model", self.embedder.model_id),
                        ("dim", str(dim)),
                        ("provider", self.embedder.provider),
                        ("schema_version", SCHEMA_VERSION),
                    ),
                )

    def check_embedder(self, embedder: Embedder) -> None:
        actual = dict(self.connection.execute("SELECT key, value FROM meta"))
        expected = {
            "model": str(embedder.model_id),
            "dim": str(embedder.dim),
            "provider": str(embedder.provider),
        }
        for field in ("model", "dim", "provider"):
            if actual.get(field) != expected[field]:
                raise IndexMismatch(
                    f"index {field} mismatch: stored={actual.get(field)!r}, requested={expected[field]!r}"
                )

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> Store:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def _snapshot_chunks(
        self,
        repo: str,
        root: Path,
        walked: Sequence[tuple[str, bytes]],
        chunker: Callable[..., ChunkResult],
        include_prefixes: Sequence[str] | None,
    ) -> tuple[dict[str, list[Chunk]], list[str]]:
        if chunker is chunk_repo:
            by_path: dict[str, list[Chunk]] = {}
            warnings: list[str] = []
            for path, source in walked:
                result = chunk_file(repo, path, source)
                by_path[path] = result.chunks
                warnings.extend(result.warnings)
            return by_path, warnings

        result = chunker(repo, root, include_prefixes=include_prefixes)
        walk_errors = [
            warning.removeprefix("walk error: ")
            for warning in result.warnings
            if warning.startswith("walk error: ")
        ]
        if walk_errors:
            raise WalkIncomplete(walk_errors)
        by_path = {path: [] for path, _source in walked}
        for chunk in result.chunks:
            by_path.setdefault(chunk.path, []).append(chunk)
        return by_path, list(result.warnings)

    def ingest(
        self,
        repo: str,
        root: str | os.PathLike[str],
        chunker: Callable[..., ChunkResult] = chunk_repo,
        include_prefixes: Sequence[str] | None = None,
        progress: Callable[[int, int, float], None] | None = None,
    ) -> IngestReport:
        started = time.monotonic()
        self.check_embedder(self.embedder)
        root_path = Path(root)
        errors: list[str] = []
        walked = list(walk_repo(root_path, include_prefixes=include_prefixes, errors=errors))
        if errors:
            raise WalkIncomplete(errors)
        if not walked:
            raise EmptyCorpus(f"repository walk found no indexable files under {root_path}")

        chunks_by_path, warnings = self._snapshot_chunks(
            repo, root_path, walked, chunker, include_prefixes
        )
        file_shas = {path: hashlib.sha256(source).hexdigest() for path, source in walked}
        existing = {
            path: file_sha
            for path, file_sha in self.connection.execute(
                "SELECT path, file_sha FROM files WHERE repo = ?", (repo,)
            )
        }
        candidate_chunks = sum(
            len(chunks_by_path.get(path, ()))
            for path, _source in walked
            if existing.get(path) != file_shas[path]
        )

        files_skipped = 0
        files_reingested = 0
        chunks_written = 0
        chunks_embedded = 0
        cache_hits = 0

        for path, _source in walked:
            if existing.get(path) == file_shas[path]:
                files_skipped += 1
                continue

            chunks = chunks_by_path.get(path, [])
            vectors: dict[str, bytes] = {}
            missing_by_sha: dict[str, Chunk] = {}
            for chunk in chunks:
                row = self.connection.execute(
                    """
                    SELECT vector FROM embed_cache
                    WHERE content_sha = ? AND model = ? AND dim = ? AND provider = ?
                    """,
                    (
                        chunk.content_sha,
                        self.embedder.model_id,
                        self.embedder.dim,
                        self.embedder.provider,
                    ),
                ).fetchone()
                if row is None:
                    missing_by_sha.setdefault(chunk.content_sha, chunk)
                else:
                    vectors[chunk.content_sha] = row[0]
                    cache_hits += 1

            missing = list(missing_by_sha.values())

            if missing:
                encoded = np.asarray(
                    self.embedder.encode_documents([chunk.embedded_text for chunk in missing]),
                    dtype=np.float32,
                )
                if encoded.shape != (len(missing), self.embedder.dim):
                    raise ValueError(
                        f"embedder returned shape {encoded.shape}; "
                        f"expected {(len(missing), self.embedder.dim)}"
                    )
                for chunk, vector in zip(missing, encoded, strict=True):
                    vectors[chunk.content_sha] = sqlite_vec.serialize_float32(vector.tolist())

            with self.connection:
                old_ids = [
                    row[0]
                    for row in self.connection.execute(
                        "SELECT id FROM chunks WHERE repo = ? AND path = ?", (repo, path)
                    )
                ]
                self.connection.executemany(
                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in old_ids)
                )
                self.connection.execute(
                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
                )
                for chunk in missing:
                    self.connection.execute(
                        """
                        INSERT OR IGNORE INTO embed_cache
                            (content_sha, model, dim, provider, vector)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            chunk.content_sha,
                            self.embedder.model_id,
                            self.embedder.dim,
                            self.embedder.provider,
                            vectors[chunk.content_sha],
                        ),
                    )
                for chunk in chunks:
                    cursor = self.connection.execute(
                        """
                        INSERT INTO chunks(
                            repo, path, kind, qualified_name, start_line, end_line,
                            content_sha, text, embedded_text
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            chunk.repo,
                            chunk.path,
                            chunk.kind,
                            chunk.qualified_name,
                            chunk.start_line,
                            chunk.end_line,
                            chunk.content_sha,
                            chunk.text,
                            chunk.embedded_text,
                        ),
                    )
                    self.connection.execute(
                        "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)",
                        (cursor.lastrowid, vectors[chunk.content_sha]),
                    )
                self.connection.execute(
                    """
                    INSERT INTO files(repo, path, file_sha, chunk_count, ingested_at)
                    VALUES (?, ?, ?, ?, datetime('now'))
                    ON CONFLICT(repo, path) DO UPDATE SET
                        file_sha=excluded.file_sha,
                        chunk_count=excluded.chunk_count,
                        ingested_at=excluded.ingested_at
                    """,
                    (repo, path, file_shas[path], len(chunks)),
                )
            files_reingested += 1
            chunks_written += len(chunks)
            chunks_embedded += len(missing)
            if progress is not None and missing:
                progress(chunks_embedded, candidate_chunks, time.monotonic() - started)

        walked_paths = set(file_shas)
        prefixes = _normalise_prefixes(include_prefixes)
        pruned = [
            path
            for path in existing
            if path not in walked_paths and _in_scope(path, prefixes)
        ]
        for path in pruned:
            with self.connection:
                ids = [
                    row[0]
                    for row in self.connection.execute(
                        "SELECT id FROM chunks WHERE repo = ? AND path = ?", (repo, path)
                    )
                ]
                self.connection.executemany(
                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in ids)
                )
                self.connection.execute(
                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
                )
                self.connection.execute(
                    "DELETE FROM files WHERE repo = ? AND path = ?", (repo, path)
                )

        return IngestReport(
            files_seen=len(walked),
            files_skipped=files_skipped,
            files_reingested=files_reingested,
            files_pruned=len(pruned),
            chunks_written=chunks_written,
            chunks_embedded=chunks_embedded,
            cache_hits=cache_hits,
            warnings=tuple(warnings),
            seconds=time.monotonic() - started,
        )

    def stats(self) -> StoreStats:
        def count(table: str) -> int:
            return int(self.connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0])

        return StoreStats(
            chunks=count("chunks"),
            chunks_fts=count("chunks_fts"),
            chunks_vec=count("chunks_vec"),
            embed_cache=count("embed_cache"),
            files=count("files"),
        )

    def fts_match(self, token: str, limit: int = 100) -> list[int]:
        return [
            int(row[0])
            for row in self.connection.execute(
                "SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?",
                (token, limit),
            )
        ]
