# Marathon Phase gh11-p3-retrieve
STATUS: Open
NEXT: codex (Builder)

<!-- marathon-drive: task=MARATHON-GH11-P3-RETRIEVE-TURN builder=codex reviewer=agy round-cap=7 -->

## Phase Brief

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
- Reranker default: **`mixedbread-ai/mxbai-rerank-xsmall-v1`** (Apache-2.0, ~70 MB, in the HF cache,
  loaded via `sentence_transformers.CrossEncoder(..., trust_remote_code=True)`), read from
  `XYZ_RERANKER` with that default. It is a placeholder — keep it injectable; the bake-off
  (canonical Phase 3) picks the real one. Fallback if it misbehaves: `BAAI/bge-reranker-base` (MIT,
  also cached and verified).
  **Do not use `cross-encoder/ms-marco-MiniLM-L-6-v2`** — measured 2026-09-06 on this stack
  (torch 2.14.0, transformers 5.16.1): it loads without error and returns **`[nan, nan]`** logits
  (old-format BERT checkpoint; reproduced with plain `AutoModelForSequenceClassification` under both
  `eager` and `sdpa` attention, checkpoint tensors all finite). `prelaunch.sh` now asserts the
  reranker's scores are finite *and* rank a code snippet above unrelated SQL, so this cannot pass
  silently again.

## Task

Implement `xyz/retrieve/`:

   **Score contract for every lane and stage: higher is better.**
1. `xyz/retrieve/lexical.py` — `bm25_search(store, query, k) -> list[Hit]` (`Hit`: `chunk_id,
   score, stage`) with **`score = -bm25(chunks_fts)`** (FTS5's bm25 is lower-is-better; negate it),
   the FTS5 sanitiser, and unit tests including one where a chunk with more query-term matches gets
   the higher `score`.
2. `xyz/retrieve/dense.py` — `dense_search(store, query_vec, k) -> list[Hit]` using `vec0` with
   `k = ?`; `score = -distance`; expose the SQL string as a module constant `KNN_SQL` so the test can
   assert on it.
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
   - **Candidate policy (explicit, tested):** dense and BM25 each fetch `fetch_k`; their union is
     fused by RRF and **truncated to `fetch_k`** (the depth `D`); in `hybrid+rerank` the reranker
     rescores only the first `min(D, 50)` of that list and reorders **them**; the remaining tail
     (positions 51..D) is **appended unchanged in RRF order** — reranker scores are never compared
     with RRF scores. `SearchResult.ranking` is the resulting ordered list of `(chunk_id, path)`
     pairs of length ≤ D; the top `k` are returned with chunk rows;
   - `tau` semantics per mode: compared against the top reranker score in `hybrid+rerank`, the top
     RRF score in `hybrid`, the top lane score in `dense` / `bm25` (all higher-is-better); below it
     → `no_answer=True`, `hits=[]`, `ranking` still populated. An empty candidate set is
     `no_answer=True` regardless of τ;
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
   - BM25 sign (score direction only): a chunk matching two query terms scores higher than one
     matching one;
   - τ is a **query-level** decision, not a per-hit filter — two searches prove it: (a) top score
     above τ → `no_answer=False` and the result **still contains the below-τ secondary hit**;
     (b) a query whose top score falls below τ → `no_answer=True`, `hits=[]`. Same store, τ chosen
     between the two candidates' scores in case (a);
   - `tau` above every score → `no_answer=True`, empty hits, non-empty `ranking`; `tau=None` never
     yields `no_answer` **when at least one candidate exists**; `mode="hybrid+rerank"` with no
     reranker raises; `mode="auto"` picks per the rule;
   - candidate policy on a fixture large enough that the two-lane union exceeds `fetch_k`
     (generate ≥ 120 small chunks): `ranking` has exactly `fetch_k` entries; a chunk placed at RRF
     position 75 with `fetch_k=100` is present at position 75 after `hybrid+rerank` (tail untouched)
     and absent with `fetch_k=50`; with `FakeReranker` swapping two chunks **of the same path**, the
     two `ranking` lists differ by chunk id even though their path sequences are identical;
   - `Retriever(store, FakeEmbedder(model_id="other"))` raises `IndexMismatch` (and likewise for
     `dim`, `provider`);
   - every `timings` key present and ≥ 0; `LatencyLog` p50/p95 over ≥ 3 searches.

## Non-goals

No CLI, no real-corpus run, no reranker bake-off. Read-only helpers in `xyz/index/` only if
genuinely needed (say so in the relay).

## Definition of done

- `bash validate.sh` green; every test above present and passing.
- One real smoke, out of pytest, offline env: `CrossEncoderReranker().score("sort a list in python",
  ["def sort_list(lst):\n    return sorted(lst)", "SELECT 1 FROM dual"])` → two **finite** floats
  with the code snippet higher (expected ≈ 0.597 vs 0.017 for the default model); quote them. A NaN
  here is a hard stop, not a warning.
- Red control: swap `k = ?` for `LIMIT ?` in `dense.py`, confirm the `KNN_SQL` test fails, restore.


---

▶ TAKE YOUR TURN (codex — BUILDER role)

You are the BUILDER for this phase. Read the phase brief above and implement it.
1. Implement the brief by creating/editing the artifact file(s): xyz/,tests/,pyproject.toml
2. Append a build block to this relay file: `### Round N · Builder · codex` summarizing what you did (files touched, key decisions).
3. Use this exact tick binary (run it from any directory): /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.xyz/bin/tick
   - /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.xyz/bin/tick claim MARATHON-GH11-P3-RETRIEVE-TURN --agent codex --paths "marathon-system/gh11-act1-hybrid-retrieval--gh11-p3-retrieve/RELAY.md,xyz/,tests/,pyproject.toml"
   - /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.xyz/bin/tick ping MARATHON-GH11-P3-RETRIEVE-TURN --agent codex
   - /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.xyz/bin/tick release MARATHON-GH11-P3-RETRIEVE-TURN --agent codex --to agy
4. Edit ONLY these paths: marathon-system/gh11-act1-hybrid-retrieval--gh11-p3-retrieve/RELAY.md and xyz/,tests/,pyproject.toml. Do NOT run git. Do NOT touch any other file — the harness commits for you.
5. HAND OFF EXPLICITLY (GH-268): after releasing the token, end your turn by naming who acts next —
   "handing off to agy — agy, take your turn." A turn that ends without that line
   leaves a human guessing whether the relay is waiting on them or has stalled. Do this EVERY round,
   not just the first. ALSO, you MUST update the `NEXT:` line at the top of this file to exactly: `NEXT: agy (Reviewer)`

---

▶ TAKE YOUR TURN (agy — REVIEWER role)

You are the REVIEWER for this phase. Read the latest builder block above AND review the artifact file(s) on disk: xyz/,tests/,pyproject.toml. REVIEW THE WHOLE FILE, NOT JUST THE DIFF (GH-268): a beta test had this loop reach 'Approved' in two rounds while an independent audit of the same branch found 20 issues (1 critical, 4 high) — every one of them in the pre-existing code the change sat on, which nobody had read. Pre-existing defects in a file you are touching are IN SCOPE; say so explicitly if you find none. DECLARE IT: your review block MUST contain a literal 'swept file: yes' or 'swept file: no' line — without it a reviewer that skipped the sweep is indistinguishable in the transcript from one that did it and found nothing, which is exactly how those 20 issues stayed invisible.
1. Append a review block: `### Round N · Reviewer · agy` followed by your assessment.
2. If changes needed: add `**Verdict:** Changes requested`, update the `NEXT:` line to exactly `NEXT: codex (Builder)`, then: /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.xyz/bin/tick release MARATHON-GH11-P3-RETRIEVE-TURN --agent agy --to codex
3. If satisfied: add `**Verdict:** Approved`, set `STATUS: Approved`, then: /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.xyz/bin/tick done MARATHON-GH11-P3-RETRIEVE-TURN --agent agy
4. Use this exact tick binary (run it from any directory) for all token operations: /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.xyz/bin/tick
   Edit ONLY marathon-system/gh11-act1-hybrid-retrieval--gh11-p3-retrieve/RELAY.md (your review block + STATUS). Do NOT edit the artifact yourself — request changes instead. Do NOT run git.
4b. TO VERIFY A FINDING, WRITE PROBE FILES OUTSIDE THE REPO — under $TMPDIR, never inside the
   working tree. Creating even one scratch file in the repo is an off-lane write: containment
   reverts it and FAILS YOUR WHOLE TURN, discarding the review you just did (GH-441). Observed
   2026-08-08: a reviewer found a real latent crash, wrote two probe files in-tree to demonstrate
   it, and lost the turn for doing so — the finding survived only because RELAY.md happens to be
   on your allowlist. `cp` what you need to "$TMPDIR/probe.$$/" and work there instead. Verifying
   is wanted; verifying in-tree is what costs you the turn.
5. HAND OFF EXPLICITLY (GH-268): end your turn by naming who acts next — "handing off to codex —
   codex, take your turn" when requesting changes, or "relay closed, no further turn needed" when
   approving. The beta report singled this out: the Reviewer turn did not tell the user to go back to the
   Producer, so the relay looked stalled when it was simply waiting. Do this EVERY round.
