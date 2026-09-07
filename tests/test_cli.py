from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.fakes import FakeEmbedder, FakeReranker
from xyz.cli import main


@pytest.fixture
def fake_models(monkeypatch: pytest.MonkeyPatch) -> None:
    import xyz.cli as cli

    monkeypatch.setattr(cli, "_make_embedder", FakeEmbedder)
    monkeypatch.setattr(cli, "_make_reranker", lambda: FakeReranker(default=0.0))


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "alpha.py").write_text(
        "def alpha():\n    return 'alpha'\n\n"
        "def alpha_helper():\n    return 'helper'\n"
    )
    (root / "beta.py").write_text("def beta():\n    return 'beta'\n")
    return root


def test_ingest_query_eval_end_to_end_and_dedupe(
    tmp_path: Path, fake_models: None, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path)
    db = tmp_path / "index.sqlite"
    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    first = json.loads(capsys.readouterr().out)
    assert first["ingest"]["chunks_embedded"] > 0
    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    second = json.loads(capsys.readouterr().out)
    assert second["ingest"]["chunks_embedded"] == 0

    assert main(["query", "--db", str(db), "--mode", "dense", "alpha"]) == 0
    assert "timings_ms" in capsys.readouterr().out

    queries = tmp_path / "queries.json"
    queries.write_text(json.dumps({"queries": [{"q": "alpha", "relevant": ["alpha.py"]}]}))
    out = tmp_path / "eval.json"
    assert main(
        [
            "eval", "--db", str(db), "--queries", str(queries),
            "--modes", "dense,bm25,hybrid,hybrid+rerank",
            "--depth", "100", "--out", str(out),
        ]
    ) == 0
    payload = json.loads(out.read_text())
    assert set(payload["reports"]) == {"dense", "bm25", "hybrid", "hybrid+rerank"}
    assert payload["corpus"]["chunk_count"] > 0
    assert "reorder_count" in payload


def test_eval_counts_chunk_id_reorder(
    tmp_path: Path, fake_models: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    import xyz.retrieve.pipeline as pipeline
    from xyz.retrieve.models import Hit

    root = _repo(tmp_path)
    db = tmp_path / "index.sqlite"
    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    # Chunk ids 1 and 2 are distinct functions from the same alpha.py path.
    monkeypatch.setattr(
        pipeline,
        "dense_search",
        lambda *_args: [Hit(1, 2.0, "dense"), Hit(2, 1.0, "dense")],
    )
    monkeypatch.setattr(
        pipeline,
        "bm25_search",
        lambda *_args: [Hit(1, 2.0, "bm25"), Hit(2, 1.0, "bm25")],
    )
    import xyz.cli as cli

    class SwapReranker:
        def score(self, query: str, texts: list[str]) -> list[float]:
            del query
            return [float(index) for index, _text in enumerate(texts)]

    monkeypatch.setattr(cli, "_make_reranker", SwapReranker)
    queries = tmp_path / "queries.json"
    queries.write_text(json.dumps([{"q": "alpha", "relevant": ["alpha.py"]}]))
    out = tmp_path / "eval.json"
    assert main(
        [
            "eval", "--db", str(db), "--queries", str(queries),
            "--modes", "hybrid,hybrid+rerank", "--out", str(out),
        ]
    ) == 0
    assert json.loads(out.read_text())["reorder_count"] == 1


@pytest.mark.parametrize("payload", ([], {"queries": []}))
def test_empty_query_file_exits_two(
    tmp_path: Path, fake_models: None, payload: object
) -> None:
    path = tmp_path / "queries.json"
    path.write_text(json.dumps(payload))
    assert main(
        [
            "eval", "--db", str(tmp_path / "x.sqlite"), "--queries", str(path),
            "--out", str(tmp_path / "out.json"),
        ]
    ) == 2


def test_missing_gold_path_exits_two(tmp_path: Path, fake_models: None) -> None:
    root = _repo(tmp_path)
    db = tmp_path / "index.sqlite"
    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    queries = tmp_path / "queries.json"
    queries.write_text(json.dumps([{"q": "missing", "relevant": ["absent.py"]}]))
    assert main(
        [
            "eval", "--db", str(db), "--queries", str(queries),
            "--out", str(tmp_path / "out.json"),
        ]
    ) == 2


def test_bogus_ingest_path_exits_two(tmp_path: Path, fake_models: None) -> None:
    assert main(
        [
            "ingest", "--db", str(tmp_path / "x.sqlite"), "--repo", "fixture",
            str(tmp_path / "missing"),
        ]
    ) == 2
