"""The path-only screen: reject benchmark questions their filename already answers.

Phase 2 exists because the 30-query set is saturated — dense retrieval puts the gold file in the
top 3 for every query. The measured cause is filename leakage: prefixing each chunk with its path
moved MRR 0.80 -> 0.98 (issue #8), because queries like "probe klaviyo api rate limits" are answered
outright by `scripts/probe_klaviyo_rate_limits.py`. A question a filename answers cannot separate
two retrievers, so it is worthless in a set whose only job is to separate two retrievers.

This module is the deterministic filter that keeps such questions out. It retrieves over **paths
alone** — no file contents at all — and rejects a candidate when a gold path lands in the top
`threshold` (default 3, per MEASUREMENTS/BASELINE.md).

Two lanes run, and a question is rejected if **either** fires:

- ``lexical`` — BM25 over tokenised paths. Catches the obvious leak, where query and filename share
  words.
- ``dense``   — the same embedding model the real pipeline uses, over the path strings. Catches the
  leak that lexical misses, where the query is a synonym rather than a repeat ("throttle checker"
  for `probe_klaviyo_rate_limits.py`).

Screening on one lane only would pass questions that leak through the other, and it is the *dense*
leak that issue #8 actually measured. Running both is what makes "zero name-carried questions" a
property of the set rather than a hope about it.
"""

from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np


DEFAULT_THRESHOLD = 3
LANES = ("lexical", "dense")

# Split a path into searchable words: separators, camelCase, and digit/letter runs.
# "app/api/getUserById.php" -> app api get user by id php
_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_SEPARATORS = re.compile(r"[^0-9A-Za-z]+")
_WORD = re.compile(r"[0-9A-Za-z]+")


class QueryEmbedder(Protocol):
    """The slice of ``xyz.index.embed.Embedder`` this screen needs."""

    def encode_documents(self, texts: Sequence[str]) -> np.ndarray: ...

    def encode_query(self, text: str) -> np.ndarray: ...


def tokenise_path(path: str) -> str:
    """Return a path as space-separated searchable words.

    Separators (``/ _ - .``) split, and so does camelCase, because a WordPress or JS corpus carries
    most of its meaning in identifiers like ``getUserById`` that a separator-only tokeniser leaves
    welded shut. Leaving them welded would understate leakage and pass questions that should fail.
    """

    words: list[str] = []
    for piece in _SEPARATORS.split(path):
        if not piece:
            continue
        for part in _CAMEL.split(piece):
            words.extend(match.group(0).casefold() for match in _WORD.finditer(part))
    return " ".join(words)


@dataclass(frozen=True)
class LaneResult:
    """Where a lane ranked the best gold path, and what it put above it."""

    lane: str
    best_rank: int | None  # 1-based; None when no gold path was retrieved at all
    best_path: str | None
    top: tuple[str, ...]

    @property
    def leaked(self) -> bool:
        return self.best_rank is not None


@dataclass(frozen=True)
class ScreenResult:
    """One candidate question's verdict."""

    query: str
    relevant: tuple[str, ...]
    threshold: int
    lanes: dict[str, LaneResult] = field(default_factory=dict)

    @property
    def rejected_by(self) -> tuple[str, ...]:
        return tuple(
            name
            for name, lane in self.lanes.items()
            if lane.best_rank is not None and lane.best_rank <= self.threshold
        )

    @property
    def passed(self) -> bool:
        return not self.rejected_by

    def as_dict(self) -> dict:
        return {
            "q": self.query,
            "relevant": list(self.relevant),
            "verdict": "pass" if self.passed else "reject",
            "rejected_by": list(self.rejected_by),
            "threshold": self.threshold,
            "lanes": {
                name: {
                    "best_rank": lane.best_rank,
                    "best_path": lane.best_path,
                    "top": list(lane.top),
                }
                for name, lane in self.lanes.items()
            },
        }


class PathScreen:
    """A path-only retrieval baseline over a fixed set of paths.

    Build it once for a corpus, then screen as many candidate questions as you like — the dense lane
    embeds every path on construction, which is the expensive part, and screening is then a matrix
    multiply per question.
    """

    def __init__(
        self,
        paths: Iterable[str],
        *,
        embedder: QueryEmbedder | None = None,
        threshold: int = DEFAULT_THRESHOLD,
    ) -> None:
        if threshold < 1:
            raise ValueError(f"threshold must be >= 1, got {threshold}")
        self.paths = tuple(dict.fromkeys(paths))  # de-duplicate, keep order for stable ties
        if not self.paths:
            raise ValueError("path screen needs at least one path")
        self.threshold = threshold
        self.embedder = embedder
        self._fts = self._build_fts(self.paths)
        self._vectors = (
            embedder.encode_documents([tokenise_path(p) for p in self.paths])
            if embedder is not None
            else None
        )

    @staticmethod
    def _build_fts(paths: Sequence[str]) -> sqlite3.Connection:
        connection = sqlite3.connect(":memory:")
        connection.execute("CREATE VIRTUAL TABLE paths USING fts5(words)")
        connection.executemany(
            "INSERT INTO paths(rowid, words) VALUES (?, ?)",
            [(index, tokenise_path(path)) for index, path in enumerate(paths)],
        )
        return connection

    def _lexical(self, query: str, depth: int) -> list[str]:
        from xyz.retrieve.lexical import sanitise_fts_query

        safe = sanitise_fts_query(query)
        if safe is None:
            return []
        rows = self._fts.execute(
            """
            SELECT rowid FROM paths WHERE paths MATCH ?
            ORDER BY bm25(paths) ASC, rowid ASC LIMIT ?
            """,
            (safe, depth),
        )
        return [self.paths[int(row[0])] for row in rows]

    def _dense(self, query: str, depth: int) -> list[str]:
        if self._vectors is None or self.embedder is None:
            return []
        # Vectors are L2-normalised by the embedder, so a dot product is cosine similarity.
        scores = self._vectors @ self.embedder.encode_query(query)
        order = np.argsort(-scores, kind="stable")[:depth]
        return [self.paths[int(index)] for index in order]

    def screen(self, query: str, relevant: Sequence[str], *, depth: int = 10) -> ScreenResult:
        """Rank paths for one candidate question and report where its gold paths landed.

        ``depth`` only controls how much context the result carries for a human reading it; the
        verdict depends solely on ``threshold``.
        """

        gold = set(relevant)
        depth = max(depth, self.threshold)
        lanes: dict[str, LaneResult] = {}
        for name, ranked in (("lexical", self._lexical(query, depth)), ("dense", self._dense(query, depth))):
            hit = next(((i + 1, p) for i, p in enumerate(ranked) if p in gold), None)
            lanes[name] = LaneResult(
                lane=name,
                best_rank=hit[0] if hit else None,
                best_path=hit[1] if hit else None,
                top=tuple(ranked[: self.threshold]),
            )
        return ScreenResult(
            query=query, relevant=tuple(relevant), threshold=self.threshold, lanes=lanes
        )

    def screen_all(self, questions: Sequence[dict], *, depth: int = 10) -> list[ScreenResult]:
        """Screen a list of ``{"q": ..., "relevant": [...]}`` entries.

        Entries with no ``relevant`` paths are no-answer questions: there is no gold file for a path
        to give away, so the screen does not apply and they are skipped rather than passed.
        """

        results = []
        for question in questions:
            relevant = question.get("relevant") or []
            if not relevant:
                continue
            results.append(self.screen(question["q"], relevant, depth=depth))
        return results


def paths_from_db(db_path: str, *, repo: str | None = None) -> list[str]:
    """Read the distinct chunk paths out of an existing index."""

    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        if repo:
            rows = connection.execute(
                "SELECT DISTINCT path FROM chunks WHERE repo = ? ORDER BY path", (repo,)
            )
        else:
            rows = connection.execute("SELECT DISTINCT path FROM chunks ORDER BY path")
        return [str(row[0]) for row in rows]
    finally:
        connection.close()


def paths_from_git(repo_root: str) -> list[str]:
    """Read a repository's tracked paths without indexing it.

    The screen only ever looks at paths, so it does not need an index — and during labelling you
    iterate on questions, not on the corpus. Reading straight from git makes screening a candidate
    cost seconds instead of an ingest.

    The path set is git's, not the indexer's, so it is a superset: it includes files the include
    list would skip (images, lockfiles). For screening that is the safe direction — a larger
    candidate pool can only push a gold path *down* the ranking, so this never invents a rejection
    that the indexed corpus would not also produce.
    """

    import subprocess

    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in completed.stdout.splitlines() if line]
