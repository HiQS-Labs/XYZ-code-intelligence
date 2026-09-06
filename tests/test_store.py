"""Contract tests for the SQLite index writer and embedding adapter."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import numpy as np
import pytest

from tests.fakes import FakeEmbedder
from xyz.index.embed import QUERY_PREFIX, CodeRankEmbedder
from xyz.index.store import EmptyCorpus, IndexMismatch, Store, WalkIncomplete


FIXTURE = Path(__file__).parent / "fixtures" / "mini-repo"


def _copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "mini-repo"
    shutil.copytree(FIXTURE, root)
    python = root / "app" / "example.py"
    python.write_text(python.read_text(encoding="utf-8") + "\n# OLDTOKEN\n", encoding="utf-8")
    guide = root / "docs" / "guide.md"
    guide.write_text(guide.read_text(encoding="utf-8") + "\nDELETEONLYTOKEN\n", encoding="utf-8")
    return root


def test_first_ingest_indexes_fts_and_vectors(tmp_path: Path) -> None:
    embedder = FakeEmbedder()
    with Store.open(tmp_path / "index.sqlite", embedder) as store:
        report = store.ingest("mini", _copy_fixture(tmp_path))
        stats = store.stats()
        assert report.chunks_embedded == report.chunks_written > 0
        assert stats.chunks == stats.chunks_fts == stats.chunks_vec
        assert store.fts_match("OLDTOKEN")


def test_second_ingest_is_a_true_file_sha_short_circuit(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
        store.ingest("mini", root)
        embedder = FakeEmbedder()
        store.embedder = embedder
        report = store.ingest("mini", root)
        assert report.files_skipped == report.files_seen
        assert report.files_reingested == 0
        assert report.chunks_written == 0
        assert embedder.call_count == 0
        assert report.seconds < 1.0


def test_changed_file_reuses_unchanged_chunk_vectors_and_refreshes_fts(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    embedder = FakeEmbedder()
    with Store.open(tmp_path / "index.sqlite", embedder) as store:
        store.ingest("mini", root)
        source = root / "app" / "example.py"
        source.write_text(
            source.read_text(encoding="utf-8").replace("OLDTOKEN", "NEWTOKEN"),
            encoding="utf-8",
        )
        embedder.document_calls = embedder.documents_encoded = 0
        report = store.ingest("mini", root)
        assert report.files_reingested == 1
        assert report.cache_hits > 0
        assert embedder.document_calls == 1
        assert embedder.documents_encoded == 1
        assert store.fts_match("NEWTOKEN")
        assert store.fts_match("OLDTOKEN") == []


def test_deleted_file_is_pruned_from_all_indexes(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
        store.ingest("mini", root)
        before = store.stats()
        (root / "docs" / "guide.md").unlink()
        report = store.ingest("mini", root)
        after = store.stats()
        assert report.files_pruned == 1
        assert after.files == before.files - 1
        assert after.chunks == after.chunks_fts == after.chunks_vec
        assert after.chunks < before.chunks
        assert store.fts_match("DELETEONLYTOKEN") == []


def test_prefix_scoped_ingest_does_not_prune_outside_scope(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
        store.ingest("mini", root)
        (root / "docs" / "guide.md").unlink()
        report = store.ingest("mini", root, include_prefixes=("app",))
        assert report.files_pruned == 0
        assert store.fts_match("DELETEONLYTOKEN")


def test_empty_corpus_does_not_write(tmp_path: Path) -> None:
    root = tmp_path / "empty"
    root.mkdir()
    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
        with pytest.raises(EmptyCorpus):
            store.ingest("mini", root)
        assert store.stats().files == store.stats().chunks == 0


def test_incomplete_walk_preserves_every_existing_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _copy_fixture(tmp_path)
    blocked = root / "docs"
    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
        store.ingest("mini", root)
        before = store.stats()
        token_ids = store.fts_match("DELETEONLYTOKEN")
        real_scandir = os.scandir

        def guarded_scandir(path: str | os.PathLike[str]):
            if Path(path) == blocked:
                raise PermissionError("blocked for test")
            return real_scandir(path)

        monkeypatch.setattr(os, "scandir", guarded_scandir)
        with pytest.raises(WalkIncomplete, match="docs"):
            store.ingest("mini", root)
        assert store.stats() == before
        assert store.fts_match("DELETEONLYTOKEN") == token_ids


@pytest.mark.parametrize(
    ("changed", "value"),
    (("model_id", "other"), ("dim", 12), ("provider", "other-provider")),
)
def test_open_rejects_each_embedder_identity_mismatch(
    tmp_path: Path, changed: str, value: object
) -> None:
    path = tmp_path / "index.sqlite"
    Store.open(path, FakeEmbedder()).close()
    kwargs = {"model_id": "fake", "dim": 8, "provider": "fake"}
    kwargs[changed] = value
    with pytest.raises(IndexMismatch, match={"model_id": "model"}.get(changed, changed)):
        Store.open(path, FakeEmbedder(**kwargs))


def test_chunk_vector_matches_provider_keyed_cache(tmp_path: Path) -> None:
    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
        store.ingest("mini", _copy_fixture(tmp_path))
        chunk_vector, cache_vector = store.connection.execute(
            """
            SELECT v.embedding, c.vector
            FROM chunks AS ch
            JOIN chunks_vec AS v ON v.rowid = ch.id
            JOIN embed_cache AS c
              ON c.content_sha = ch.content_sha
             AND c.model = ? AND c.dim = ? AND c.provider = ?
            LIMIT 1
            """,
            ("fake", 8, "fake"),
        ).fetchone()
        assert np.array_equal(
            np.frombuffer(chunk_vector, dtype=np.float32),
            np.frombuffer(cache_vector, dtype=np.float32),
        )


def test_coderank_embedder_sets_guard_and_prefixes_queries_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    class StubModel:
        max_seq_length = 99

        def encode(self, texts: list[str], **_kwargs: object) -> np.ndarray:
            calls.append(texts)
            vectors = np.zeros((len(texts), 768), dtype=np.float32)
            vectors[:, 0] = 1.0
            return vectors

    model = StubModel()
    monkeypatch.setenv("EMBED_MAX_THREADS", "1")
    embedder = CodeRankEmbedder(model_factory=lambda *_args, **_kwargs: model, device="cpu")
    embedder.encode_documents(["raw document"])
    query = embedder.encode_query("sort a list")
    assert model.max_seq_length == 2048
    assert calls == [["raw document"], [QUERY_PREFIX + "sort a list"]]
    assert query.shape == (768,)
    assert np.linalg.norm(query) == pytest.approx(1.0)
