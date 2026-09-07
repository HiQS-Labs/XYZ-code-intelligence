"""Instrumented dense, lexical, hybrid, and reranked retrieval pipeline."""

from __future__ import annotations

import time
from collections.abc import Sequence

from xyz.index.embed import Embedder
from xyz.index.store import Store
from xyz.retrieve.dense import dense_search
from xyz.retrieve.fuse import rrf
from xyz.retrieve.lexical import bm25_search
from xyz.retrieve.models import Hit, SearchHit, SearchResult
from xyz.retrieve.rerank import Reranker


TIMING_STAGES = ("embed_query", "bm25", "dense", "fuse", "rerank", "total")
MODES = frozenset({"auto", "dense", "bm25", "hybrid", "hybrid+rerank"})


class Retriever:
    def __init__(self, store: Store, embedder: Embedder, reranker: Reranker | None = None) -> None:
        store.check_embedder(embedder)
        self.store = store
        self.embedder = embedder
        self.reranker = reranker

    @staticmethod
    def _elapsed(started: float) -> float:
        return max(0.0, (time.perf_counter() - started) * 1000.0)

    def _chunk_rows(self, ids: Sequence[int]) -> dict[int, tuple[object, ...]]:
        if not ids:
            return {}
        placeholders = ",".join("?" for _ in ids)
        rows = self.store.connection.execute(
            f"""
            SELECT id, repo, path, kind, qualified_name, start_line, end_line, text, embedded_text
            FROM chunks WHERE id IN ({placeholders})
            """,
            tuple(ids),
        )
        return {int(row[0]): tuple(row[1:]) for row in rows}

    def search(
        self,
        query: str,
        k: int = 10,
        fetch_k: int = 50,
        mode: str = "auto",
        tau: float | None = None,
    ) -> SearchResult:
        if mode not in MODES:
            raise ValueError(f"unknown retrieval mode: {mode!r}")
        if k <= 0 or fetch_k <= 0:
            raise ValueError("k and fetch_k must be positive")
        resolved = ("hybrid+rerank" if self.reranker is not None else "hybrid") if mode == "auto" else mode
        if resolved == "hybrid+rerank" and self.reranker is None:
            raise ValueError("hybrid+rerank mode requires a reranker")

        timings = {stage: 0.0 for stage in TIMING_STAGES}
        total_started = time.perf_counter()
        dense_hits: list[Hit] = []
        lexical_hits: list[Hit] = []

        if resolved in {"dense", "hybrid", "hybrid+rerank"}:
            started = time.perf_counter()
            query_vec = self.embedder.encode_query(query)
            timings["embed_query"] = self._elapsed(started)
            started = time.perf_counter()
            dense_hits = dense_search(self.store, query_vec, fetch_k)
            timings["dense"] = self._elapsed(started)
        if resolved in {"bm25", "hybrid", "hybrid+rerank"}:
            started = time.perf_counter()
            lexical_hits = bm25_search(self.store, query, fetch_k)
            timings["bm25"] = self._elapsed(started)

        if resolved == "dense":
            candidates = dense_hits[:fetch_k]
        elif resolved == "bm25":
            candidates = lexical_hits[:fetch_k]
        else:
            started = time.perf_counter()
            candidates = rrf([dense_hits, lexical_hits])[:fetch_k]
            timings["fuse"] = self._elapsed(started)

        if resolved == "hybrid+rerank" and candidates:
            rerank_count = min(len(candidates), 50)
            head = candidates[:rerank_count]
            rows = self._chunk_rows([hit.chunk_id for hit in head])
            texts = [str(rows[hit.chunk_id][7]) for hit in head]
            started = time.perf_counter()
            scores = self.reranker.score(query, texts)  # type: ignore[union-attr]
            timings["rerank"] = self._elapsed(started)
            if len(scores) != len(head):
                raise ValueError(f"reranker returned {len(scores)} scores for {len(head)} candidates")
            rescored = [
                Hit(hit.chunk_id, float(score), "rerank")
                for hit, score in zip(head, scores, strict=True)
            ]
            candidates = sorted(rescored, key=lambda hit: (-hit.score, hit.chunk_id)) + candidates[rerank_count:]

        rows = self._chunk_rows([hit.chunk_id for hit in candidates])
        ranking = [(hit.chunk_id, str(rows[hit.chunk_id][1])) for hit in candidates]
        top_score = candidates[0].score if candidates else None
        no_answer = top_score is None or (tau is not None and top_score < tau)
        materialised: list[SearchHit] = []
        if not no_answer:
            for hit in candidates[:k]:
                repo, path, kind, name, start_line, end_line, text, embedded_text = rows[hit.chunk_id]
                materialised.append(
                    SearchHit(
                        hit.chunk_id, str(repo), str(path), str(kind), str(name),
                        int(start_line), int(end_line), str(text), str(embedded_text),
                        hit.score, hit.stage,
                    )
                )
        timings["total"] = self._elapsed(total_started)
        return SearchResult(materialised, ranking, no_answer, timings, resolved)
