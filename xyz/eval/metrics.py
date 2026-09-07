"""Depth-bounded retrieval metrics with chunk identity preserved."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

Ranking = Sequence[tuple[int, str]]


@dataclass(frozen=True)
class Report:
    """Serializable MRR/recall report for one retrieval mode."""

    mrr: float
    recalls: Mapping[int, float]
    never_found: int
    depth: int
    per_query: Sequence[Mapping[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mrr": self.mrr,
            "recall@1": self.recalls[1],
            "recall@3": self.recalls[3],
            "recall@5": self.recalls[5],
            "recall@10": self.recalls[10],
            "never_found": self.never_found,
            "depth": self.depth,
            "per_query": list(self.per_query),
        }

    def write_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")


def score(
    rankings: Mapping[str, Ranking],
    queries: Sequence[Mapping[str, Any]],
    depth: int,
) -> Report:
    """Score ordered chunk rankings against path-level relevance at ``depth``."""
    if not queries:
        raise ValueError("query list is empty")
    if depth <= 0:
        raise ValueError("depth must be positive")

    ranks: list[int | None] = []
    rows: list[dict[str, Any]] = []
    for query in queries:
        text = str(query["q"])
        relevant = [str(path) for path in query["relevant"]]
        ordered = list(rankings.get(text, ()))[:depth]
        relevant_set = set(relevant)
        rank = next(
            (
                position
                for position, (_chunk_id, path) in enumerate(ordered, start=1)
                if path in relevant_set
            ),
            None,
        )
        ranks.append(rank)
        rows.append(
            {
                "q": text,
                "relevant": relevant,
                "rank": rank,
                "top_hit": ordered[0][1] if ordered else None,
                "ranking": [
                    {"chunk_id": int(chunk_id), "path": str(path)}
                    for chunk_id, path in ordered
                ],
            }
        )

    count = len(ranks)
    recalls = {
        k: round(sum(rank is not None and rank <= k for rank in ranks) / count, 4)
        for k in (1, 3, 5, 10)
    }
    return Report(
        mrr=round(sum(1.0 / rank for rank in ranks if rank is not None) / count, 4),
        recalls=recalls,
        never_found=sum(rank is None for rank in ranks),
        depth=depth,
        per_query=rows,
    )
