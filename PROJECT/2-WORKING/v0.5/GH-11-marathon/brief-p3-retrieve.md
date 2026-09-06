---
title: GH-11 marathon brief — gh11-p3-retrieve
status: active
created: 2026-09-05
updated: 2026-09-06
owner: Noel Saw
goal: Phase brief consumed by marathon-drive.sh for phase gh11-p3-retrieve; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
roadmap_exempt: true
---

# Phase brief — gh11-p3-retrieve: BM25 ∥ dense → RRF → cross-encoder rerank → τ, instrumented

## Status

| What was just completed | What's next |
|---|---|
| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p3-retrieve` after `gh11-p2-store`; outcome recorded in the capture doc. |

Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
Canonical doc → "Phase 1", step 3: *parallel BM25 + dense → RRF(k=60) → cross-encoder rerank top
25-50 → no-answer threshold τ*.
Environment contract: see `brief-p0-scaffold.md` (`XYZ_PY`, `XYZ_SCRATCH`, offline env, no installs).

## Context you must read before coding

- `xyz/index/store.py` from p2 — query through the `Store`; do not open the SQLite file elsewhere.
- **`vec0` KNN must use the `k = ?` bound form** (`WHERE embedding MATCH ? AND k = ?`), never a
  parameterised `LIMIT ?` — Ask-Self issue #23: `LIMIT ?` was rejected at prepare time on stricter
  sqlite-vec builds and 500'd in production. This is a tested requirement.
- FTS5 ranking: the built-in `bm25()` function (lower = better) via `ORDER BY bm25(chunks_fts)`.
  Sanitise the query for FTS5 syntax (quote tokens; strip operators) so a query containing `-` or
  `:` cannot raise; an all-stopword/empty sanitised query returns no BM25 hits, not an error.
- Reranker default: `cross-encoder/ms-marco-MiniLM-L-6-v2` (Apache-2.0, in the HF cache, loaded via
  `sentence_transformers.CrossEncoder`). It is a placeholder — keep it injectable.

## Task

Implement `xyz/retrieve/`:

1. `xyz/retrieve/lexical.py` — `bm25_search(store, query, k) -> list[Hit]` (`Hit`: `chunk_id,
   score, stage`), with the FTS5 sanitiser and its unit tests.
2. `xyz/retrieve/dense.py` — `dense_search(store, query_vec, k) -> list[Hit]` using `vec0` with
   `k = ?`; `score` = the vec0 distance negated (document this); expose the SQL string as a module
   constant `KNN_SQL` so the test can assert on it.
3. `xyz/retrieve/fuse.py` — `rrf(rankings: list[list[Hit]], k=60) -> list[Hit]`:
   `score = Σ 1 / (k + rank_i)`; deterministic tie-break by `chunk_id`.
4. `xyz/retrieve/rerank.py` — a `Reranker` protocol (`score(query, texts) -> list[float]`),
   `CrossEncoderReranker`, and `FakeReranker` in `tests/fakes.py` (scores from a dict, default 0).
5. `xyz/retrieve/pipeline.py` — `Retriever(store, embedder, reranker=None)`:
   - the constructor calls `store.check_embedder(embedder)` → `IndexMismatch` on a wrong embedder
     (query-time guard; tested for model, dim, provider);
   - `search(query, k=10, fetch_k=50, mode="auto", tau=None) -> SearchResult` with
     `mode ∈ auto | dense | bm25 | hybrid | hybrid+rerank`; `auto` resolves to `hybrid+rerank` when a
     reranker is present else `hybrid`; an explicit `hybrid` never reranks; `hybrid+rerank` without
     a reranker raises `ValueError`;
   - dense and BM25 each fetch `fetch_k`; RRF fuses; in `hybrid+rerank` the reranker rescores the
     fused top `min(fetch_k, 50)` and reorders by its score; the top `k` are returned with chunk
     rows, and `SearchResult.ranking` carries the **full ordered candidate list of chunk ids** (up to
     `fetch_k`) so callers can compute ranks beyond `k`;
   - `tau` semantics per mode: compared against the top reranker score in `hybrid+rerank`, the top
     RRF score in `hybrid`, the top lane score in `dense` / `bm25`; below it → `no_answer=True`,
     `hits=[]`, `ranking` still populated. An empty candidate set is `no_answer=True` regardless of τ;
   - `SearchResult.timings` = per-stage milliseconds (`embed_query, bm25, dense, fuse, rerank,
     total`; stages not run report 0.0).
   - `xyz/retrieve/latency.py` — `LatencyLog` collecting `timings` and reporting p50 / p95 per stage.
6. Tests in `tests/test_retrieve.py` on a store built with `FakeEmbedder` from the p1 fixture:
   - `rrf` reproduces a hand-computed fusion for two 3-item lists with one overlap;
   - a chunk ranked last by both lanes but scored highest by `FakeReranker` ends at rank 1 in
     `hybrid+rerank` and **not** in `hybrid` (the "rerank measurably reorders RRF output" gate in
     miniature);
   - `KNN_SQL` contains the literal ` k = ?` and does not contain `LIMIT ?`;
   - `"foo-bar: baz*"` and `""` do not raise in `bm25_search`;
   - `tau` above every score → `no_answer=True`, empty hits, non-empty `ranking`; `tau=None` never
     does; `mode="hybrid+rerank"` with no reranker raises; `mode="auto"` picks per the rule;
   - `Retriever(store, FakeEmbedder(model_id="other"))` raises `IndexMismatch` (and likewise for
     `dim`, `provider`);
   - every `timings` key present and ≥ 0; `LatencyLog` p50/p95 over ≥ 3 searches.

## Non-goals

No CLI, no real-corpus run, no reranker bake-off. Read-only helpers in `xyz/index/` only if
genuinely needed (say so in the relay).

## Definition of done

- `bash validate.sh` green; every test above present and passing.
- One real smoke, out of pytest, offline env: `CrossEncoderReranker().score("sort a list",
  ["def sort_list(lst): return sorted(lst)", "SELECT 1"])` → two floats, the code snippet higher;
  quote them.
- Red control: swap `k = ?` for `LIMIT ?` in `dense.py`, confirm the `KNN_SQL` test fails, restore.
