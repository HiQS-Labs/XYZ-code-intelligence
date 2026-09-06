---
title: GH-11 marathon brief — gh11-p4-roundtrip
status: active
created: 2026-09-05
updated: 2026-09-05
owner: Noel Saw
goal: Phase brief consumed by marathon-drive.sh for phase gh11-p4-roundtrip; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
roadmap_exempt: true
---

# Phase brief — gh11-p4-roundtrip: `xyz` CLI + real ingest/query round-trip on LTVera-Pandas, scored

## Status

| What was just completed | What's next |
|---|---|
| Brief authored (2026-09-05). | Executed by `marathon.sh` as phase `gh11-p4-roundtrip` after `gh11-p3-retrieve`; results land in FINDINGS-0.5.md and the capture doc. |

Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
Canonical doc → "Phase 1" **QA gate**: *ingest + query round-trip on one real repo; unchanged
re-ingest is near-instant (planner dedupe works); rerank stage measurably reorders RRF output;
latency instrumented (p50/p95).*

## Context you must read before coding

- `.embed-tmp/eval/score_retrieval.py` — the metric definitions to reproduce **exactly**:
  a hit is a retrieved chunk whose `path` is in the query's `relevant` list; MRR = mean of
  1/rank-of-first-hit with misses contributing 0; recall@k for k ∈ {1, 3, 5, 10}; `never_found`;
  `per_query` detail. Same definitions ⇒ comparable with BENCHMARKS.md Run 9 (MRR 0.801 / R@1 0.700,
  dense-only, old chunker).
- `.embed-tmp/eval/queries-LTVera-Pandas.json` — the 30 labelled queries. The set is **saturated**
  (issue #11 caveat 2) and deltas under 0.05 are noise (GH-5 doc) — report, don't over-claim.
- The corpus is the sibling checkout `../LTVera-Pandas` relative to this repo root; read its path
  from `XYZ_EVAL_REPO` (default `../LTVera-Pandas`). Expect ~5,100+ chunks; embedding on MPS is
  ≈ 0.3 s/chunk ⇒ **25-30 minutes**. Budget for it: start the ingest early in the turn, log
  progress with `python -u`. **Fallback** if the full corpus will not fit the turn: ingest only the
  `scripts/`, `app/` and `alembic/` subtrees (every gold label lives there) and state that in the
  results — it is an honest, smaller round-trip, not a failure.
- Put the index at `temp/xyz-eval/LTVera-Pandas.sqlite` (`temp/` is gitignored). Never commit it.

## Task

1. `xyz/eval/metrics.py` — `score(results: dict[query -> list[path]], queries) -> Report` with the
   definitions above, plus a JSON writer matching `score_retrieval.py`'s output shape
   (`mrr, recall@1/3/5/10, never_found, per_query`). Unit-test it against a tiny hand-built case
   and against a copy of one Run-9 `per_query` row if you can reconstruct it; otherwise the
   hand-built case is sufficient.
2. `xyz/cli.py` subcommands (argparse; `main(argv)` returns an int):
   - `xyz ingest --db DB --repo NAME PATH` → `Store.ingest`, prints the `IngestReport` and
     `Store.stats()`;
   - `xyz query --db DB [--mode dense|bm25|hybrid|hybrid+rerank] [--k N] [--tau T] "text"` →
     prints rank, path, qualified_name, lines, score and the per-stage timings;
   - `xyz eval --db DB --queries FILE --modes dense,bm25,hybrid,hybrid+rerank --out JSON` → runs
     every mode over the query file, writes one report per mode plus a `latency` block (p50/p95
     per stage per mode), and prints a comparison table.
   CLI tests in `tests/test_cli.py` with the fake embedder/reranker on the fixture tree
   (ingest → query → eval end to end, plus `ingest` twice shows `chunks_embedded == 0` the second
   time).
3. **The real round-trip** (this is the gate; do it in this order and keep the numbers):
   1. `time .venv/bin/python -u -m xyz ingest --db temp/xyz-eval/LTVera-Pandas.sqlite --repo LTVera-Pandas "$XYZ_EVAL_REPO"`
      — record wall time, `chunks_written`, `chunks_embedded`, peak RSS (`/usr/bin/time -l`).
   2. Run the same ingest again — record wall time and `chunks_embedded` (**must be 0** and the
      run must take seconds, not minutes).
   3. `xyz eval` over the 30 queries for all four modes; record MRR / R@1 / R@3 / R@5 / R@10 /
      never_found per mode and p50/p95 latency per stage.
   4. Reorder evidence: for the 30 queries, count how many have a different top-10 ordering between
      `hybrid` and `hybrid+rerank` (the CLI can print this from the two per_query lists).
4. **Record the results** — append a dated **"Run: XYZ hybrid retrieval round-trip (GH-11 Act 1)"**
   section to `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md` with the table from step 3 and the four
   Phase 1 QA-gate bullets each marked met / not met with the number that shows it; and update the
   `## Status` table and `## Run log` of `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`.
   Do not renumber or edit earlier runs; do not touch `.embed-tmp/BENCHMARKS.md`.

## Non-goals

No Slack/HTTP/MCP surface. No reranker or embedding-model comparison beyond the four modes above.
No changes to `.embed-tmp/`. No committing of `temp/`.

## Definition of done

- `bash validate.sh` green (unit tests with fakes only — the real run is **not** in pytest).
- All four Phase 1 QA-gate bullets evidenced with numbers in FINDINGS-0.5.md:
  round-trip done; second ingest `chunks_embedded == 0` and < 30 s; reorder count ≥ 1 query;
  p50/p95 recorded per stage.
- Acceptance from the capture doc: `hybrid+rerank` MRR and R@1 ≥ `dense` MRR and R@1 − 0.05 on the
  30-query set. If it is lower than that, the phase is **not** approved — report the numbers and
  the most likely cause (reranker choice, BM25 sanitiser, fusion depth) in the relay; do not tune
  against the labelled set to make it pass.
- Red control: run `xyz eval` with an empty `queries` list and confirm it exits non-zero with a
  clear message (an empty benchmark must not report a perfect score).
