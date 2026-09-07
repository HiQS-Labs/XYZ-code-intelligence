"""Deterministic reciprocal-rank fusion."""

from __future__ import annotations

from collections.abc import Sequence

from xyz.retrieve.models import Hit


def rrf(rankings: Sequence[Sequence[Hit]], k: int = 60) -> list[Hit]:
    """Fuse rankings using one-based ranks and deterministic chunk-id ties."""

    if k < 0:
        raise ValueError("RRF k must be non-negative")
    scores: dict[int, float] = {}
    for ranking in rankings:
        seen: set[int] = set()
        for rank, hit in enumerate(ranking, start=1):
            if hit.chunk_id in seen:
                continue
            seen.add(hit.chunk_id)
            scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (k + rank)
    hits = [Hit(chunk_id, score, "rrf") for chunk_id, score in scores.items()]
    return sorted(hits, key=lambda hit: (-hit.score, hit.chunk_id))
