"""Value objects shared by retrieval lanes and the query pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Hit:
    """A scored chunk reference; scores are always higher-is-better."""

    chunk_id: int
    score: float
    stage: str


@dataclass(frozen=True)
class SearchHit:
    """A materialised chunk row returned to a caller."""

    chunk_id: int
    repo: str
    path: str
    kind: str
    qualified_name: str
    start_line: int
    end_line: int
    text: str
    embedded_text: str
    score: float
    stage: str


@dataclass(frozen=True)
class SearchResult:
    """The answer set plus the complete candidate ordering and instrumentation."""

    hits: list[SearchHit]
    ranking: list[tuple[int, str]]
    no_answer: bool
    timings: dict[str, float]
    mode: str
