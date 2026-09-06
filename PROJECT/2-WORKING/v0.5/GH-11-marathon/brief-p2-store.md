---
title: GH-11 marathon brief — gh11-p2-store
status: active
created: 2026-09-05
updated: 2026-09-05
owner: Noel Saw
goal: Phase brief consumed by marathon-drive.sh for phase gh11-p2-store; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
roadmap_exempt: true
---

# Phase brief — gh11-p2-store: SQLite store (chunks + FTS5 + vec0), provider-keyed embed cache, drift guard

## Status

| What was just completed | What's next |
|---|---|
| Brief authored (2026-09-05). | Executed by `marathon.sh` as phase `gh11-p2-store` after `gh11-p1-chunkers`; outcome recorded in the capture doc. |

Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
Canonical doc → "Phase 1", step 2 and step 4 (CodeRankEmbed as the placeholder dense lane).

## Context you must read before coding

- `SOP.md` → CodeRankEmbed: query prefix `"Represent this query for searching relevant code: "`
  on **queries only**, documents raw; `trust_remote_code=True`; `max_seq_length = 2048`; batch 16;
  `TOKENIZERS_PARALLELISM=false`. Model load ≈ 11.6 s → load once per process.
- Issue #11 carve-out 1 (Ask-Self inheritance): the embed cache is keyed by
  `(content_sha, model, dim, provider)` and an index refuses to be queried or extended by a
  different `(model, dim, provider)` — that guard caught real cross-provider cache poisoning. Port the
  semantics; do not copy Ask-Self files.
- `sqlite-vec` is installed (`import sqlite_vec; sqlite_vec.load(conn)` after
  `conn.enable_load_extension(True)`); FTS5 is compiled in. Verified on this venv.

## Task

Implement `xyz/index/`:

1. `xyz/index/embed.py` — an `Embedder` protocol (`model_id`, `dim`, `provider`,
   `encode_documents(texts) -> np.ndarray[float32]`, `encode_query(text) -> np.ndarray`) and
   `CodeRankEmbedder` implementing it with sentence-transformers (`provider="sentence-transformers"`,
   `dim=768`, L2-normalised output, device auto: MPS if available else CPU, batch size and thread cap
   configurable via `EMBED_BATCH_SIZE` / `EMBED_MAX_THREADS` like the existing script). Also a
   `FakeEmbedder` in `tests/` (deterministic hash-based vectors) so every store test runs in
   milliseconds without a model.
2. `xyz/index/store.py` — `Store(db_path)` owning one SQLite file, the **only writer** of the index:
   - tables: `meta(key, value)` holding `model`, `dim`, `provider`, `schema_version`;
     `files(repo, path, file_sha, chunk_count, ingested_at, PRIMARY KEY(repo, path))`;
     `chunks(id INTEGER PRIMARY KEY, repo, path, kind, qualified_name, start_line, end_line,
     content_sha, text, embedded_text)`; `chunks_fts` = FTS5 **external-content** table over
     `chunks(embedded_text, qualified_name, path)` kept in sync by triggers;
     `chunks_vec` = `vec0(embedding float[<dim>])` with rowid = `chunks.id`;
     `embed_cache(content_sha, model, dim, provider, vector BLOB, PRIMARY KEY(content_sha, model,
     dim, provider))`.
   - `Store.open(db_path, embedder)`: creates the schema on first use and writes `meta`; on an
     existing DB it **raises `IndexMismatch`** if `(model, dim, provider)` differ from `meta`.
   - `Store.ingest(repo, root, chunker=chunk_repo) -> IngestReport`: the planner. For each walked
     file compute `file_sha`; if `files` has the same sha, skip it entirely; otherwise delete that
     file's old chunks (cascading FTS/vec rows) and insert the new ones. Embed only chunks whose
     `content_sha` is **not** in `embed_cache` for this `(model, dim, provider)`; cache every new
     vector. Files present in `files` but absent from the walk are pruned. `IngestReport` carries
     `files_seen, files_skipped, files_reingested, chunks_written, chunks_embedded, cache_hits,
     seconds`.
   - `Store.stats()` → row counts of `chunks`, `chunks_fts`, `chunks_vec`, `embed_cache`, `files`.
   - Single transaction per file; WAL journal mode; `PRAGMA foreign_keys=ON`.
3. Tests in `tests/test_store.py` with `FakeEmbedder` on the p1 fixture tree (copied to a tmp dir):
   - first ingest: `chunks_embedded == chunks_written > 0`, and `chunks`, `chunks_fts`,
     `chunks_vec` counts are equal;
   - **second ingest, unchanged tree: the embedder is called 0 times, `files_skipped == files_seen`,
     `chunks_written == 0`, and it completes in < 1 s**;
   - touch one file: only that file is re-ingested; chunks whose `content_sha` is unchanged are
     cache hits (embedder not called for them);
   - delete one file: its chunks are pruned from all three tables;
   - opening the DB with a `FakeEmbedder(model_id="other")` raises `IndexMismatch`;
   - a chunk's vector read back from `chunks_vec` equals the cached vector.

## Non-goals

No query path (p3), no CLI (p4). No real model in tests.

## Definition of done

- `bash validate.sh` green; every test above present and passing.
- One deliberate smoke with the real model: `CodeRankEmbedder().encode_query("sort a list")` has
  shape `(768,)` and norm ≈ 1.0 — run it once, quote the numbers in the relay, but keep it **out of
  the pytest suite** (it costs 12 s and needs the model).
- Red control: the "0 embedder calls on unchanged re-ingest" test must fail if the `files` sha
  short-circuit is removed — show once in the relay.
