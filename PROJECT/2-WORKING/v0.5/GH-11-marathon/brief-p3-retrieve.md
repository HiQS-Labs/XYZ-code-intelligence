---
title: GH-11 marathon brief — gh11-p3-retrieve
status: active
created: 2026-09-05
updated: 2026-09-05
owner: Noel Saw
goal: Phase brief consumed by marathon-drive.sh for phase gh11-p3-retrieve; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
roadmap_exempt: true
---

# Phase brief — gh11-p3-retrieve: BM25 ∥ dense → RRF → cross-encoder rerank → τ, instrumented

## Status

| What was just completed | What's next |
|---|---|
| Brief authored (2026-09-05). | Executed by `marathon.sh` as phase `gh11-p3-retrieve` after `gh11-p2-store`; outcome recorded in the capture doc. |

Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
Canonical doc → "Phase 1", step 3: *parallel BM25 + dense → RRF(k=60) → cross-encoder rerank top
25-50 → no-answer threshold τ*.

## Context you must read before coding

- `xyz/index/store.py` from p2 — query through the `Store`; do not open the SQLite file elsewhere.
- **`vec0` KNN must use the `k = ?` bound form** (`WHERE embedding MATCH ? AND k = ?`), never a
  parameterised `LIMIT ?` — Ask-Self issue #23: `LIMIT ?` was rejected at prepare time on stricter
  sqlite-vec builds and 500'd in production. This is a tested requirement.
- FTS5 ranking: use the built-in `bm25()` function (lower = better) via `ORDER BY bm25(chunks_fts)`.
  Sanitise the query for FTS5 syntax (quote tokens; strip operators) so a query containing `-` or
  `:` cannot raise.
- Reranker default: `cross-encoder/ms-marco-MiniLM-L-6-v2` (Apache-2.0, already in the HF cache,
  loaded via `sentence_transformers.CrossEncoder`). It is a placeholder — keep it injectable.

## Task

Implement `xyz/retrieve/`:

1. `xyz/retrieve/lexical.py` — `bm25_search(store, query, k) -> list[Hit]` (`Hit`: `chunk_id,
   score, stage`), with the FTS5 sanitiser and its unit test.
2. `xyz/retrieve/dense.py` — `dense_search(store, query_vec, k) -> list[Hit]` using `vec0` with
   `k = ?`; returns cosine-style similarity (`1 - distance` for L2 on unit vectors, or the vec0
   distance negated — document which).
3. `xyz/retrieve/fuse.py` — `rrf(rankings: list[list[Hit]], k=60) -> list[Hit]`:
   `score = Σ 1 / (k + rank_i)` over the lists a chunk appears in; deterministic tie-break by
   `chunk_id`.
4. `xyz/retrieve/rerank.py` — a `Reranker` protocol (`score(query, texts) -> list[float]`), a
   `CrossEncoderReranker` and a `FakeReranker` (lives in `tests/`) that scores from a dict.
5. `xyz/retrieve/pipeline.py` — `Retriever(store, embedder, reranker=None)` with
   `search(query, k=10, fetch_k=50, mode="hybrid", tau=None) -> SearchResult`:
   - `mode` ∈ `dense | bm25 | hybrid | hybrid+rerank` (`hybrid+rerank` is the default when a
     reranker is present);
   - dense and BM25 each fetch `fetch_k`; RRF fuses; the reranker rescores the fused top
     `min(fetch_k, 50)` and reorders by its score; the top `k` are returned with their chunk rows;
   - `tau`: when set and the top reranker score (or, without a reranker, the top RRF score) is
     below it, `SearchResult.no_answer = True` and `hits = []`;
   - `SearchResult.timings` = per-stage milliseconds (`embed_query, bm25, dense, fuse, rerank,
     total`).
   - `xyz/retrieve/latency.py` — `LatencyLog` collecting `SearchResult.timings` and reporting
     p50 / p95 per stage.
6. Tests in `tests/test_retrieve.py` on a store built with `FakeEmbedder` from the p1 fixture:
   - `rrf` reproduces a hand-computed fusion for two 3-item lists with one overlap;
   - a chunk ranked last by both lanes but scored highest by `FakeReranker` ends at rank 1 in
     `hybrid+rerank` and **not** in `hybrid` — this is the "rerank measurably reorders RRF output"
     gate in miniature;
   - the dense SQL contains the literal ` k = ?` and no `LIMIT ?` (assert on the SQL string the
     module builds);
   - a query string `"foo-bar: baz*"` does not raise in `bm25_search`;
   - `tau` above every score yields `no_answer=True` with empty hits; `tau=None` never does;
   - every `timings` key is present and non-negative; `LatencyLog` p50/p95 are computed over ≥ 3
     searches.

## Non-goals

No CLI, no real-corpus run, no reranker bake-off. No changes to `xyz/index/` beyond adding a
read-only helper if you genuinely need one (say so in the relay).

## Definition of done

- `bash validate.sh` green; every test above present and passing.
- One real smoke (out of pytest): `CrossEncoderReranker().score("sort a list", ["def sort(...)",
  "SELECT 1"])` returns two floats with the code snippet scoring higher — quote them in the relay.
- Red control: swap `k = ?` for `LIMIT ?` in `dense.py`, confirm the SQL-string test fails, restore.
