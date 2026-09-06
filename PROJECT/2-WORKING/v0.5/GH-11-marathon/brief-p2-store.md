---
title: GH-11 marathon brief — gh11-p2-store
status: active
created: 2026-09-05
updated: 2026-09-06
owner: Noel Saw
goal: Phase brief consumed by marathon-drive.sh for phase gh11-p2-store; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
roadmap_exempt: true
---

# Phase brief — gh11-p2-store: SQLite store (chunks + FTS5 + vec0), provider-keyed embed cache, drift guard

## Status

| What was just completed | What's next |
|---|---|
| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p2-store` after `gh11-p1-chunkers`; outcome recorded in the capture doc. |

Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
Canonical doc → "Phase 1", step 2 and step 4 (CodeRankEmbed as the placeholder dense lane).
Environment contract: see `brief-p0-scaffold.md` (`XYZ_PY`, `XYZ_SCRATCH`, offline env, no installs).

## Context you must read before coding

- `SOP.md` → CodeRankEmbed: query prefix `"Represent this query for searching relevant code: "`
  on **queries only**, documents raw; `trust_remote_code=True`; `TOKENIZERS_PARALLELISM=false`;
  batch 16. `FINDINGS-0.5.md` (~174-179): **`max_seq_length = 2048` is the real memory guard** and
  must be set explicitly on the loaded model (the old script never set it — this is a tested
  requirement here). Model load ≈ 11.6 s → load once per process.
- Issue #11 carve-out 1 (Ask-Self inheritance): the embed cache is keyed by
  `(content_sha, model, dim, provider)` and an index refuses to be opened, extended **or queried**
  by a different `(model, dim, provider)` — that guard caught real cross-provider cache poisoning.
  Port the semantics; do not copy Ask-Self files. This file-sha planner + cache is the **only**
  planner in XYZ; Act 2 reconciles Ask-Self's planner onto it, not beside it.
- `sqlite-vec` and FTS5 are verified present in `XYZ_PY` by `validate.sh`'s env preflight.

## Task

Implement `xyz/index/`:

1. `xyz/index/embed.py` — an `Embedder` protocol (`model_id`, `dim`, `provider`,
   `encode_documents(texts) -> np.ndarray[float32]`, `encode_query(text) -> np.ndarray`) and
   `CodeRankEmbedder` (`provider="sentence-transformers"`, `dim=768`, L2-normalised output, device
   auto: MPS if available else CPU; `EMBED_BATCH_SIZE` / `EMBED_MAX_THREADS` env like the old
   script). Constructor accepts an injectable `model_factory` so a test can pass a stub and assert:
   `max_seq_length` was set to **2048**, `encode_query` prepends the exact prefix, and
   `encode_documents` does **not**. `tests/fakes.py` provides `FakeEmbedder(model_id="fake",
   dim=8, provider="fake")` (deterministic hash-based unit vectors, counts calls) used by every
   store/retrieve test.
2. `xyz/index/store.py` — `Store`, the **only writer** of an index:
   - tables: `meta(key, value)` holding `model`, `dim`, `provider`, `schema_version`;
     `files(repo, path, file_sha, chunk_count, ingested_at, PRIMARY KEY(repo, path))`;
     `chunks(id INTEGER PRIMARY KEY, repo, path, kind, qualified_name, start_line, end_line,
     content_sha, text, embedded_text)`; `chunks_fts` = FTS5 **external-content** table over
     `chunks(embedded_text, qualified_name, path)` kept in sync by insert/delete/update triggers;
     `chunks_vec` = `vec0(embedding float[<dim>])` with rowid = `chunks.id`;
     `embed_cache(content_sha, model, dim, provider, vector BLOB, PRIMARY KEY(content_sha, model,
     dim, provider))`.
   - `Store.open(db_path, embedder)`: creates the schema on first use and writes `meta`; on an
     existing DB raises `IndexMismatch` naming the differing field if **any** of `model`, `dim`,
     `provider` differ. `Store.check_embedder(embedder)` exposes the same check for readers (p3).
   - `Store.ingest(repo, root, chunker=chunk_repo, include_prefixes=None) -> IngestReport`, the
     planner: walk (via p1, honouring `include_prefixes`); a walk that yields **zero files raises**
     `EmptyCorpus` before any write. For each file compute `file_sha`; same sha in `files` → skip;
     else delete that file's chunks (FTS/vec rows via triggers/explicit delete) and insert the new
     ones. Embed only chunks whose `content_sha` is absent from `embed_cache` for this
     `(model, dim, provider)`; cache every new vector. **Pruning is scoped:** files in `files` for
     this `repo` that are absent from the walk are pruned only when they fall under the walked scope
     (all of the repo when `include_prefixes` is None, else only under those prefixes).
     `IngestReport` carries `files_seen, files_skipped, files_reingested, files_pruned,
     chunks_written, chunks_embedded, cache_hits, warnings, seconds`.
   - `Store.stats()` → row counts of `chunks`, `chunks_fts` (via `SELECT count(*) FROM chunks_fts`),
     `chunks_vec`, `embed_cache`, `files`; `Store.fts_match(token, limit)` → chunk ids whose FTS row
     matches (used by tests to prove the inverted index, not just the row count, is current).
   - One transaction per file; WAL journal mode; `PRAGMA foreign_keys=ON`.
3. Tests in `tests/test_store.py` with `FakeEmbedder` on the p1 fixture copied to a tmp dir:
   - first ingest: `chunks_embedded == chunks_written > 0`; `chunks`, `chunks_fts`, `chunks_vec`
     counts equal; `fts_match` finds a token that exists only in one fixture file;
   - **second ingest, unchanged tree: `files_skipped == files_seen`, `files_reingested == 0`,
     `chunks_written == 0`, embedder call count 0, < 1 s** (all five asserted separately — the
     red control below depends on it);
   - edit one file to add a unique token: only that file is re-ingested (`files_reingested == 1`),
     its unchanged chunks are cache hits, `fts_match(new_token)` finds it and `fts_match(old_token)`
     no longer does;
   - delete one file: its chunks vanish from all three tables and `fts_match` of its unique token is
     empty; with `include_prefixes` naming a different directory, that deleted file is **not** pruned;
   - an empty directory raises `EmptyCorpus` and writes nothing;
   - `IndexMismatch` is raised separately for a differing `model_id`, a differing `dim`, and a
     differing `provider` (three tests);
   - a chunk's vector read back from `chunks_vec` equals its cached vector;
   - `CodeRankEmbedder` with the stub factory: `max_seq_length == 2048`, query prefix present on
     queries only.

## Non-goals

No query path (p3), no CLI (p4). No real model in pytest.

## Definition of done

- `bash validate.sh` green; every test above present and passing.
- One real smoke, out of pytest and under the offline env: `CodeRankEmbedder().encode_query("sort a
  list")` → shape `(768,)`, norm ≈ 1.0, and `model.max_seq_length == 2048` — quote all three.
- Red controls (show once each in the relay, then restore): (a) remove the `files` sha
  short-circuit → the `files_skipped == files_seen` / `files_reingested == 0` assertions fail even
  though the cache still keeps embedder calls at 0; (b) drop the FTS insert trigger → the
  `fts_match(new_token)` test fails while the count test may still pass.
