"""Contract tests for hybrid retrieval and its score semantics."""

from __future__ import annotations

from pathlib import Path

import pytest
import sqlite_vec

from tests.fakes import FakeEmbedder, FakeReranker
from xyz.index.store import IndexMismatch, Store
from xyz.retrieve.dense import KNN_SQL, dense_search
from xyz.retrieve.fuse import rrf
from xyz.retrieve.latency import LatencyLog
from xyz.retrieve.lexical import bm25_search
from xyz.retrieve.models import Hit
from xyz.retrieve.pipeline import Retriever


def _add_chunks(store: Store, count: int, *, same_path: bool = False) -> None:
    vector = sqlite_vec.serialize_float32([1.0] + [0.0] * (store.embedder.dim - 1))
    with store.connection:
        for chunk_id in range(1, count + 1):
            path = "same.py" if same_path else f"p{chunk_id}.py"
            store.connection.execute(
                """
                INSERT INTO chunks(
                    id, repo, path, kind, qualified_name, start_line, end_line,
                    content_sha, text, embedded_text
                ) VALUES (?, 'repo', ?, 'function', ?, 1, 1, ?, ?, ?)
                """,
                (chunk_id, path, f"f{chunk_id}", f"sha{chunk_id}", f"text {chunk_id}", f"embedded {chunk_id}"),
            )
            store.connection.execute(
                "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)", (chunk_id, vector)
            )


def test_rrf_matches_hand_computed_overlap_and_tie_break() -> None:
    left = [Hit(1, 9, "a"), Hit(2, 8, "a"), Hit(3, 7, "a")]
    right = [Hit(3, 9, "b"), Hit(4, 8, "b"), Hit(5, 7, "b")]
    fused = rrf([left, right], k=60)
    assert [hit.chunk_id for hit in fused] == [3, 1, 2, 4, 5]
    assert fused[0].score == pytest.approx(1 / 63 + 1 / 61)
    assert fused[1].score == pytest.approx(1 / 61)
    assert fused[2].score == pytest.approx(1 / 62)


def test_knn_sql_uses_bound_k_and_dense_query_executes(tmp_path: Path) -> None:
    assert " k = ?" in KNN_SQL
    assert "LIMIT ?" not in KNN_SQL.upper()
    embedder = FakeEmbedder()
    with Store.open(tmp_path / "index.sqlite", embedder) as store:
        _add_chunks(store, 2)
        assert len(dense_search(store, embedder.encode_query("needle"), 1)) == 1


def test_bm25_sanitises_operators_empty_and_keeps_higher_better(tmp_path: Path) -> None:
    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
        _add_chunks(store, 2)
        with store.connection:
            store.connection.execute(
                "UPDATE chunks SET embedded_text = 'foo bar foo' WHERE id = 1"
            )
            store.connection.execute(
                "UPDATE chunks SET embedded_text = 'foo' WHERE id = 2"
            )
        assert bm25_search(store, "foo-bar: baz*", 10)
        assert bm25_search(store, "", 10) == []
        assert bm25_search(store, "the and", 10) == []
        hits = bm25_search(store, "foo bar", 10)
        assert hits[0].chunk_id == 1
        assert hits[0].score > hits[1].score


def test_rerank_reorders_rrf_and_tau_is_query_level(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import xyz.retrieve.pipeline as pipeline

    embedder = FakeEmbedder()
    with Store.open(tmp_path / "index.sqlite", embedder) as store:
        _add_chunks(store, 3)
        lane = [Hit(1, 3, "lane"), Hit(2, 2, "lane"), Hit(3, 1, "lane")]
        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
        reranker = FakeReranker({"embedded 1": 2.0, "embedded 2": 0.0, "embedded 3": 3.0})
        retriever = Retriever(store, embedder, reranker)

        assert retriever.search("q", mode="hybrid").ranking[0][0] == 1
        reranked = retriever.search("q", k=3, mode="hybrid+rerank", tau=1.0)
        assert [chunk_id for chunk_id, _path in reranked.ranking] == [3, 1, 2]
        assert not reranked.no_answer
        assert len(reranked.hits) == 3
        assert reranked.hits[-1].score < 1.0

        rejected = Retriever(
            store, embedder, FakeReranker({"embedded 1": 0.2, "embedded 2": 0.1, "embedded 3": 0.0})
        ).search("q", mode="hybrid+rerank", tau=0.5)
        assert rejected.no_answer and rejected.hits == [] and rejected.ranking


def test_candidate_depth_rerank_cap_and_same_path_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import xyz.retrieve.pipeline as pipeline

    embedder = FakeEmbedder()
    with Store.open(tmp_path / "index.sqlite", embedder) as store:
        _add_chunks(store, 120, same_path=True)
        lane = [Hit(chunk_id, 121 - chunk_id, "lane") for chunk_id in range(1, 121)]
        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
        scores = {f"embedded {chunk_id}": float(51 - chunk_id) for chunk_id in range(1, 51)}
        scores["embedded 1"], scores["embedded 2"] = scores["embedded 2"], scores["embedded 1"]
        retriever = Retriever(store, embedder, FakeReranker(scores))
        hybrid = retriever.search("q", fetch_k=100, mode="hybrid")
        reranked = retriever.search("q", fetch_k=100, mode="hybrid+rerank")
        assert len(reranked.ranking) == 100
        assert reranked.ranking[74][0] == 75
        assert 75 not in {chunk_id for chunk_id, _path in retriever.search(
            "q", fetch_k=50, mode="hybrid+rerank"
        ).ranking}
        assert hybrid.ranking != reranked.ranking
        assert [path for _chunk_id, path in hybrid.ranking] == [
            path for _chunk_id, path in reranked.ranking
        ]


@pytest.mark.parametrize(
    "kwargs",
    ({"model_id": "other"}, {"dim": 9}, {"provider": "other"}),
)
def test_retriever_rejects_embedder_identity_mismatch(tmp_path: Path, kwargs: dict[str, object]) -> None:
    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
        with pytest.raises(IndexMismatch):
            Retriever(store, FakeEmbedder(**kwargs))


def test_auto_modes_errors_timings_and_latency_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import xyz.retrieve.pipeline as pipeline

    embedder = FakeEmbedder()
    with Store.open(tmp_path / "index.sqlite", embedder) as store:
        _add_chunks(store, 1)
        lane = [Hit(1, 1.0, "lane")]
        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
        plain = Retriever(store, embedder)
        assert plain.search("q", mode="auto").mode == "hybrid"
        with pytest.raises(ValueError, match="requires"):
            plain.search("q", mode="hybrid+rerank")
        assert not plain.search("q", mode="dense", tau=None).no_answer
        assert plain.search("q", mode="bm25", tau=2.0).no_answer

        reranked = Retriever(store, embedder, FakeReranker({"embedded 1": 1.0}))
        log = LatencyLog()
        for _ in range(3):
            result = reranked.search("q", mode="auto")
            assert result.mode == "hybrid+rerank"
            assert set(result.timings) == {
                "embed_query", "bm25", "dense", "fuse", "rerank", "total"
            }
            assert all(value >= 0 for value in result.timings.values())
            log.add(result.timings)
        summary = log.summary()
        assert all(set(summary[stage]) == {"p50", "p95"} for stage in result.timings)
