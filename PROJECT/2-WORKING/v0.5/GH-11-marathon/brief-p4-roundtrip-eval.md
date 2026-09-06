---
title: GH-11 marathon brief — gh11-p4-roundtrip
status: active
created: 2026-09-05
updated: 2026-09-06
owner: Noel Saw
goal: Phase brief consumed by marathon-drive.sh for phase gh11-p4-roundtrip; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
roadmap_exempt: true
---

# Phase brief — gh11-p4-roundtrip: `xyz` CLI + real ingest/query round-trip on LTVera-Pandas, scored

## Status

| What was just completed | What's next |
|---|---|
| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p4-roundtrip` after `gh11-p3-retrieve`; results land in FINDINGS-0.5.md and the capture doc. |

Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
Canonical doc → "Phase 1" **QA gate**: *ingest + query round-trip on one real repo; unchanged
re-ingest is near-instant (planner dedupe works); rerank stage measurably reorders RRF output;
latency instrumented (p50/p95).*
Environment contract: see `brief-p0-scaffold.md`. This phase additionally needs **`XYZ_EVAL_REPO`**
(absolute path to a LTVera-Pandas checkout, set by the operator). First thing in the turn:
`test -d "$XYZ_EVAL_REPO/scripts" && test -d "$XYZ_EVAL_REPO/app"` — if that fails, stop and report;
do not guess a path.

## Context you must read before coding

- `.embed-tmp/eval/score_retrieval.py` — the metric definitions: a hit is a retrieved chunk whose
  `path` is in the query's `relevant` list (lines ~133-138); MRR = mean of 1/rank-of-first-hit with
  misses contributing 0; recall@k for k ∈ {1, 3, 5, 10}; `never_found`; `per_query` (~141-156).
  **Depth differs and must be stated:** that scorer ranks the *entire* corpus (a hit at rank 11
  still contributes 1/11), whereas this pipeline ranks `fetch_k` candidates. So this phase reports
  **MRR@D / R@k / miss@D at an explicit depth D = 100** (`fetch_k=100` per lane; ranks past 100 count
  as misses) and produces its own dense-only arm at the same depth as the comparison baseline.
  BENCHMARKS.md Run 9 (MRR 0.801 / R@1 0.700, full-corpus ranking, old chunker) is quoted for
  context only and is **not** equated with any number here.
- `.embed-tmp/eval/queries-LTVera-Pandas.json` — the 30 labelled queries. Saturated (issue #11
  caveat 2); deltas under 0.05 are noise (GH-5 doc) — report, don't over-claim.
- Corpus size: Run 9 used 5,147 chunks; the p1 chunker (wider include list, AST chunks) will
  produce a different count. Embedding on MPS ≈ 0.3 s/chunk ⇒ **25-35 minutes** for the full tree;
  turn timeout is 7200 s.
- Scratch: every generated file (index DB, eval JSON, timing logs) goes under `$XYZ_SCRATCH`
  (default `.relay-scratch/`, swept by the harness). Nothing under `temp/`.

## Task

1. `xyz/eval/metrics.py` — `score(rankings: dict[query -> list[chunk_path_in_rank_order]],
   queries, depth) -> Report` with the definitions above; ranks are **chunk ranks** (the first chunk
   whose path is relevant; paths are not de-duplicated before ranking); JSON writer with keys `mrr,
   recall@1, recall@3, recall@5, recall@10, never_found, depth, per_query`, where each `per_query`
   row carries `q, relevant, rank, top_hit` **and `ranking` (the ordered paths up to `depth`)**.
   `score()` raises `ValueError` on an empty query list. Unit tests: a hand-built 3-query case; a
   case where the only relevant chunk sits at rank 11 with `depth=10` → miss, and with `depth=100`
   → 1/11.
2. `xyz/cli.py` subcommands (argparse; `main(argv)` returns an int; `python -m xyz` works via
   `xyz/__main__.py` from p0):
   - `xyz ingest --db DB --repo NAME PATH [--include-prefix P ...]` → `Store.ingest`
     (prefixes → `include_prefixes`), prints the `IngestReport`, `Store.stats()`, and peak RSS
     (`resource.getrusage`); a missing / non-directory `PATH` or `EmptyCorpus` → exit 2 with a
     message;
   - `xyz query --db DB [--mode auto|dense|bm25|hybrid|hybrid+rerank] [--k N] [--tau T] "text"` →
     rank, path, qualified_name, lines, score, per-stage timings;
   - `xyz eval --db DB --queries FILE --modes dense,bm25,hybrid,hybrid+rerank --depth 100 --out JSON`
     → before scoring, **assert the corpus is non-empty and that every gold path in the query file
     exists in `chunks.path`** (else exit 2 listing the missing paths); run every mode; write one
     report per mode plus `latency` (p50/p95 per stage per mode) and `corpus` (chunk count, file
     count, `include_prefixes` used, DB path); print a comparison table and the **reorder count**:
     the number of queries whose top-10 `ranking` differs between `hybrid` and `hybrid+rerank`.
   CLI tests in `tests/test_cli.py` with the fakes on the fixture tree: ingest → query → eval end to
   end; ingest twice shows `chunks_embedded == 0`; an empty query file → exit 2; a query file with a
   gold path absent from the corpus → exit 2; a bogus `PATH` → exit 2.
3. **The real round-trip** (the gate; keep every number):
   1. `time "$XYZ_PY" -u -m xyz ingest --db "$XYZ_SCRATCH/LTVera-Pandas.sqlite" --repo LTVera-Pandas "$XYZ_EVAL_REPO"`
      — record wall time, `files_seen`, `chunks_written`, `chunks_embedded`, peak RSS. **Early
      estimate:** after the first 200 chunks are embedded, the CLI prints an ETA; if the ETA exceeds
      **45 minutes**, abort and use the fallback.
   2. **Fallback (only if triggered, and say so):** a **fresh** DB `"$XYZ_SCRATCH/LTVera-Pandas-subset.sqlite"`
      with `--include-prefix scripts/ --include-prefix app/ --include-prefix alembic/` in **one**
      invocation (root-preserving; every gold path lives under those prefixes). Results from a
      subset are labelled `corpus: subset` everywhere they are reported.
   3. Run the same ingest command again — record wall time and `chunks_embedded` (**must be 0**,
      seconds not minutes).
   4. `xyz eval` at depth 100 for all four modes; record MRR@100 / R@1 / R@3 / R@5 / R@10 /
      miss@100 per mode, p50/p95 per stage, and the reorder count.
4. **Record the results** — append a dated **"Run: XYZ hybrid retrieval round-trip (GH-11 Act 1)"**
   section to `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md` with the corpus provenance (full or subset,
   chunk/file counts, chunker version = this commit), the table from step 3, and the four Phase 1
   QA-gate bullets each marked met / not met with the number that shows it; update the `## Status`
   table and `## Run log` of `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`. Do not renumber
   or edit earlier runs; do not touch `.embed-tmp/BENCHMARKS.md`; do not commit anything from
   `$XYZ_SCRATCH`.

## Non-goals

No Slack/HTTP/MCP surface. No model or reranker comparison beyond the four modes. No changes to
`.embed-tmp/`. No `CHANGELOG.md` entry (orchestrator, at PR time).

## Definition of done

- `bash validate.sh` green (pytest uses fakes only — the real run is **not** in pytest).
- All four Phase 1 QA-gate bullets evidenced with numbers in FINDINGS-0.5.md: round-trip done
  (full or labelled subset); second ingest `chunks_embedded == 0` and < 30 s; reorder count ≥ 1;
  p50/p95 recorded per stage.
- Acceptance from the capture doc: at depth 100, `hybrid+rerank` MRR@100 and R@1 ≥ the `dense`
  arm's MRR@100 and R@1 − 0.05, on the same DB. If lower, the phase is **not** approved — report the
  numbers and the most likely cause (reranker choice, BM25 sanitiser, fusion depth); do not tune
  against the labelled set.
- Red controls (show once in the relay): `xyz eval` with an empty query file exits 2; the
  rank-11 metric test flips between miss and 1/11 with `depth`.
