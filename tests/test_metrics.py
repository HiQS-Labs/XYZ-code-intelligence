from __future__ import annotations

import json

import pytest

from xyz.eval.metrics import score


def test_score_three_queries() -> None:
    queries = [
        {"q": "one", "relevant": ["a.py"]},
        {"q": "two", "relevant": ["b.py"]},
        {"q": "miss", "relevant": ["z.py"]},
    ]
    report = score(
        {
            "one": [(1, "a.py"), (2, "x.py")],
            "two": [(3, "x.py"), (4, "b.py")],
            "miss": [(5, "x.py")],
        },
        queries,
        10,
    ).to_dict()
    assert report["mrr"] == 0.5
    assert report["recall@1"] == pytest.approx(1 / 3, abs=0.0001)
    assert report["recall@3"] == pytest.approx(2 / 3, abs=0.0001)
    assert report["never_found"] == 1


def test_rank_eleven_flips_at_depth() -> None:
    queries = [{"q": "q", "relevant": ["hit.py"]}]
    ranking = [(i, f"p{i}.py") for i in range(1, 11)] + [(11, "hit.py")]
    shallow = score({"q": ranking}, queries, 10)
    deep = score({"q": ranking}, queries, 100)
    assert shallow.mrr == 0 and shallow.never_found == 1
    assert deep.mrr == pytest.approx(1 / 11, abs=0.0001) and deep.never_found == 0


def test_same_path_chunk_ids_survive_json_round_trip(tmp_path) -> None:
    report = score(
        {"q": [(41, "same.py"), (42, "same.py")]},
        [{"q": "q", "relevant": ["same.py"]}],
        10,
    )
    path = tmp_path / "report.json"
    report.write_json(path)
    ranking = json.loads(path.read_text())["per_query"][0]["ranking"]
    assert ranking == [
        {"chunk_id": 41, "path": "same.py"},
        {"chunk_id": 42, "path": "same.py"},
    ]
