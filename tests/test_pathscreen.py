"""Tests for the path-only screen.

The screen is the load-bearing rule of Phase 2 — if it under-rejects, name-carried questions enter
the frozen set and it saturates again, which is the exact failure the set exists to prevent. So the
tests here care most about the ways it could silently pass something it should reject.
"""

from __future__ import annotations

import json
import sqlite3

import numpy as np
import pytest

from xyz.eval.pathscreen import DEFAULT_THRESHOLD, PathScreen, paths_from_db, tokenise_path


CORPUS = [
    "scripts/probe_klaviyo_rate_limits.py",
    "scripts/migrate_secrets_local_to_gcp.py",
    "app/api/keycloak_admin.py",
    "app/models/order.py",
    "themes/child/inc/getUserById.php",
    "alembic/versions/0004_add_index.py",
]


class WordOverlapEmbedder:
    """A deterministic stand-in for CodeRankEmbed, with no model download.

    Encodes text as an L2-normalised bag of words over a fixed vocabulary, so the dense lane's
    ranking is exactly word overlap. That is enough to exercise the lane's plumbing — ordering,
    thresholding, normalisation — without pretending to reproduce a real model's semantics.
    """

    VOCAB = sorted(
        {word for path in CORPUS for word in tokenise_path(path).split()}
        | {"throttle", "checker", "cache", "invalidation", "unrelated", "quantum"}
    )

    def _encode(self, text: str) -> np.ndarray:
        vector = np.zeros(len(self.VOCAB), dtype=np.float32)
        for word in text.casefold().split():
            if word in self.VOCAB:
                vector[self.VOCAB.index(word)] += 1.0
        norm = float(np.linalg.norm(vector))
        return vector / norm if norm else vector

    def encode_documents(self, texts):
        return np.vstack([self._encode(text) for text in texts])

    def encode_query(self, text):
        return self._encode(text)


def test_tokenise_path_splits_separators_and_camel_case():
    assert tokenise_path("themes/child/inc/getUserById.php") == "themes child inc get user by id php"
    assert tokenise_path("scripts/probe_klaviyo_rate_limits.py") == (
        "scripts probe klaviyo rate limits py"
    )


def test_tokenise_path_splits_acronym_boundaries():
    # HTTPServer must not stay welded, or a query saying "http server" misses the leak.
    assert tokenise_path("lib/HTTPServer.php") == "lib http server php"


def test_lexical_lane_rejects_a_question_the_filename_answers():
    screen = PathScreen(CORPUS)
    result = screen.screen("probe klaviyo api rate limits", ["scripts/probe_klaviyo_rate_limits.py"])
    assert not result.passed
    assert "lexical" in result.rejected_by
    assert result.lanes["lexical"].best_rank == 1


def test_behaviour_described_question_passes_both_lanes():
    screen = PathScreen(CORPUS, embedder=WordOverlapEmbedder())
    result = screen.screen(
        "where do we decide a customer has churned", ["app/models/order.py"]
    )
    assert result.passed, result.as_dict()
    assert result.rejected_by == ()


def test_camel_case_leakage_is_caught_by_both_lanes():
    """What the camelCase tokeniser buys.

    'get user by id' shares no whole token with the raw string `getUserById.php`. Splitting the
    identifier makes the leak visible, and once visible *both* lanes see it — which is the point:
    without the split, both would miss it and the question would enter the frozen set.
    """
    screen = PathScreen(CORPUS, embedder=WordOverlapEmbedder())
    result = screen.screen("get user by id", ["themes/child/inc/getUserById.php"])
    assert result.rejected_by == ("lexical", "dense")
    assert result.lanes["lexical"].best_rank == 1


def test_dense_lane_rejects_alone_when_lexical_retrieves_nothing():
    """The reason two lanes exist rather than one.

    A question can be a synonym of its gold path rather than a repetition of it — "throttle checker"
    for `probe_klaviyo_rate_limits.py`. BM25 sees no shared word and returns nothing, so a
    lexical-only screen would pass the question. A model that considers the two similar still ranks
    the gold path first, and that leak is the one issue #8 actually measured.

    The stub below encodes exactly that situation; a bag-of-words embedder cannot express synonymy,
    so faking the similarity is the only honest way to test the lane in isolation.
    """

    gold = "scripts/probe_klaviyo_rate_limits.py"

    class SynonymEmbedder:
        """Puts `gold` nearest to any query, and is blind to everything else."""

        def encode_documents(self, texts):
            vectors = np.zeros((len(texts), 2), dtype=np.float32)
            for row, text in enumerate(texts):
                vectors[row] = [1.0, 0.0] if text == tokenise_path(gold) else [0.0, 1.0]
            return vectors

        def encode_query(self, text):
            return np.array([1.0, 0.0], dtype=np.float32)

    screen = PathScreen(CORPUS, embedder=SynonymEmbedder())
    result = screen.screen("throttle checker", [gold])

    assert result.lanes["lexical"].best_rank is None, "fixture must share no word with the path"
    assert result.rejected_by == ("dense",)
    assert result.lanes["dense"].best_rank == 1


def test_rank_outside_threshold_is_not_a_rejection():
    screen = PathScreen(CORPUS, threshold=1)
    loose = PathScreen(CORPUS, threshold=DEFAULT_THRESHOLD)
    query = "order index migration"
    strict_result = screen.screen(query, ["alembic/versions/0004_add_index.py"])
    loose_result = loose.screen(query, ["alembic/versions/0004_add_index.py"])
    rank = loose_result.lanes["lexical"].best_rank
    assert rank is not None and rank > 1, "fixture no longer exercises the threshold boundary"
    assert strict_result.passed
    assert not loose_result.passed


def test_no_lane_retrieval_leaves_best_rank_none():
    screen = PathScreen(CORPUS)
    result = screen.screen("quantum entanglement scheduler", ["app/models/order.py"])
    assert result.passed
    assert result.lanes["lexical"].best_rank is None
    assert not result.lanes["lexical"].leaked


def test_screen_all_skips_no_answer_questions():
    screen = PathScreen(CORPUS)
    results = screen.screen_all(
        [
            {"q": "probe klaviyo api rate limits", "relevant": ["scripts/probe_klaviyo_rate_limits.py"]},
            {"q": "how do we bill in yen", "relevant": []},
            {"q": "unanswerable by design"},
        ]
    )
    # A no-answer question has no gold file for a path to give away, so the screen does not apply.
    assert len(results) == 1


def test_lexical_only_screen_reports_an_empty_dense_lane():
    screen = PathScreen(CORPUS)  # no embedder
    result = screen.screen("probe klaviyo api rate limits", ["scripts/probe_klaviyo_rate_limits.py"])
    assert result.lanes["dense"].best_rank is None
    assert result.lanes["dense"].top == ()


def test_duplicate_paths_are_collapsed():
    screen = PathScreen(["a/b.py", "a/b.py", "c/d.py"])
    assert screen.paths == ("a/b.py", "c/d.py")


@pytest.mark.parametrize("bad", [0, -1])
def test_threshold_must_be_positive(bad):
    with pytest.raises(ValueError):
        PathScreen(CORPUS, threshold=bad)


def test_empty_corpus_is_rejected():
    with pytest.raises(ValueError):
        PathScreen([])


def test_paths_from_db_reads_distinct_paths_and_filters_by_repo(tmp_path):
    db = tmp_path / "index.db"
    connection = sqlite3.connect(db)
    connection.execute("CREATE TABLE chunks(id INTEGER PRIMARY KEY, repo TEXT, path TEXT)")
    connection.executemany(
        "INSERT INTO chunks(repo, path) VALUES (?, ?)",
        [("one", "a.py"), ("one", "a.py"), ("one", "b.py"), ("two", "c.php")],
    )
    connection.commit()
    connection.close()

    assert paths_from_db(str(db)) == ["a.py", "b.py", "c.php"]
    assert paths_from_db(str(db), repo="two") == ["c.php"]


def test_as_dict_round_trips_to_json():
    screen = PathScreen(CORPUS)
    payload = screen.screen("keycloak admin operations", ["app/api/keycloak_admin.py"]).as_dict()
    assert json.loads(json.dumps(payload))["verdict"] == "reject"
