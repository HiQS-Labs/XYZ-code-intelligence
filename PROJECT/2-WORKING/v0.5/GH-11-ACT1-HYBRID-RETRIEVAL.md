---
gh_issue: 11
source: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11
title: GH-11 Act 1 — XYZ hybrid retrieval library (canonical doc Phase 0 + Phase 1)
status: active
created: 2026-09-05
updated: 2026-09-05
owner: Noel Saw
goal: Ship the importable XYZ retrieval library — Tree-sitter chunking, SQLite chunks + FTS5 + sqlite-vec store with a provider-keyed embed cache and drift guard, and a BM25 + dense → RRF → cross-encoder rerank query path — verified by an ingest/query round-trip on one real repo, so Acts 2-5 of the v0.5 release are unblocked.
doc_type: feedback
effort: 4
complexity: 4
risk: 2
phases: 5
related:
  - "PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md"
  - "PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md"
  - "PROJECT/2-WORKING/v0.5/GH-6-LOCAL-ONLY-SCORER.md"
context_tags: [retrieval, hybrid-search, fts5, sqlite-vec, rrf, rerank, tree-sitter, chunking, marathon]
non_goals:
  - Absorbing Ask-Self's ingest/synthesis/history code (Act 2-3 of #11) — only the embed-cache semantics are ported here
  - Any Slack, HTTP or MCP surface (Acts 3-4 of #11)
  - The 250-query frozen benchmark (canonical doc Phase 2) — the 30-query LTVera-Pandas set is the gate for this act
  - Model bake-off, fine-tuning, ONNX/int8 serving (Phases 3-4, GH-5) — CodeRankEmbed via sentence-transformers is the placeholder dense lane
  - Ask-Self sunset (Phase 5)
---

# GH-11 Act 1 — XYZ hybrid retrieval library

Capture of **Act 1** of [issue #11](https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11)
("Build the XYZ retrieval library — the keystone, start here"). In the
[canonical build doc](<XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md>) this is
**Phase 0 steps 2-3 plus all of Phase 1**. Executed as one five-phase marathon
(`GH-11-marathon/MARATHON.yaml`), builder Codex, reviewer agy.

## Status

| What was just completed | What's next |
|---|---|
| Plan, phase briefs, marathon file and preflight contract authored; clone + venv provisioned (2026-09-05). | Codex plan review, then fire `marathon.sh` on the five phases in order. |

## Observed problem

- The XYZ hybrid retrieval library does not exist. The repo has a throwaway embedder
  (`.embed-tmp/scripts/embed_repos.py`) that writes `chunks.jsonl` + `embeddings.npy` sidecars, a
  brute-force query script (`.embed-tmp/scripts/query_repos.py`), and a scorer
  (`.embed-tmp/eval/score_retrieval.py`) — no package, no SQLite store, no BM25 lane, no fusion,
  no reranker. Issue #11 names this as the blocker for every downstream act.
- Canonical doc Phase 0 is only partly done: the doc is ratified (step 1) but there is no package
  scaffold (step 2) and the licensing / local-first constraints are not in `GUIDING-PRINCIPLES.md`
  (step 3). `GUIDING-PRINCIPLES.md` and `AGENTS.md` are still the PDDA-repo boilerplate.
- Evidence gap: issues #2, #8, #14 are closed as "fixed in the Run 12 batched re-embed" (MRR 0.978)
  but that code and `BENCHMARKS.md` Runs 11-15 are on **no branch of `origin`** and no clone on this
  machine. The branch this work is based on (`origin/v0.5/embedding-eval-coderankembed-vs-gemini`,
  `3301124`) carries Runs 1-10 (baseline Run 9: MRR 0.801 / R@1 0.700). The chunker changes those
  issues describe (path-prefix per #8, wider include list per #2) are therefore re-implemented in p1.

## Recon (base `3301124`, 2026-09-05)

- Existing writer for chunks: `.embed-tmp/scripts/embed_repos.py` — `INCLUDE_EXT`, `walk_repo`,
  per-repo re-exec, `max_seq_length=2048`, batch 16, `EMBED_PROFILE` telemetry. Keep it untouched;
  the library supersedes it, and it stays as the benchmark-history tool until Phase 3.
- Existing metric definitions: `.embed-tmp/eval/score_retrieval.py` — `rank_of_first_relevant`,
  MRR with misses as 0, recall@{1,3,5,10}, `never_found`; hit = retrieved chunk `path` in
  `relevant`. p4 reuses these definitions verbatim so numbers are comparable with Run 9.
- Labelled set: `.embed-tmp/eval/queries-LTVera-Pandas.json` — 30 queries, file-path gold labels,
  saturated at R@3+ after the path-prefix fix (issue #11 caveat 2). Deltas under 0.05 are noise
  (GH-5 doc).
- Runtime facts that shape the briefs (FINDINGS-0.5.md, SOP.md): query prefix
  `"Represent this query for searching relevant code: "` on queries only; `trust_remote_code=True`;
  MPS and CPU vectors identical; model load ≈ 11.6 s so one long-lived model per process; MPS
  allocations are invisible to RSS, `max_seq_length` is the real memory guard; sentence-transformers'
  `backend="onnx"` is broken for this model — do not use it.
- Ask-Self inheritance actually needed here (issue #11 carve-out 1): cache keyed by
  `(content_sha, model, dim, provider)` and a provider/dim mismatch guard. Reference:
  `ask_self_cache.py` and `detect_provider_mismatch` in the sibling `ask-self` checkout — port the
  semantics, not the file. Also inherit the `vec0` `k = ?` KNN form (Ask-Self issue #23: parameterised
  `LIMIT ?` 500'd in production).
- Untraced: Sleuth's Node `src/rag/` and Ask-Self's ingest planner — out of scope for Act 1.

## Acceptance — deviations from the issue

The issue's Act 1 checklist, with what this doc owns:

- XYZ hybrid retrieval library exists as an importable Python package with a clean API (in-process
  within Python) — **kept**, p0-p3.
- Hybrid retrieval beats vector-only on the labelled set — **[changed]** to: hybrid+rerank MRR and
  R@1 on the 30-query set are ≥ dense-only minus the 0.05 noise floor, and the reranker measurably
  reorders RRF output — reason: the issue itself records the 30-query set as saturated, so "beats"
  cannot be resolved on it; growing the set is human labelling work (canonical Phase 2), not a
  builder task.
- Use the `vec0` `k = ?` KNN form, not parameterised `LIMIT ?` — **kept**, p3, with a test that
  asserts the query text.
- Measure batch indexing RSS on ARM — **[dropped]** — reason: no ARM box is in scope for this
  marathon; the p4 run records RSS on the build machine instead and leaves the ARM row for Act 5.

Canonical doc Phase 1 QA gate, adopted verbatim as this act's gate: ingest + query round-trip on
one real repo; unchanged re-ingest is near-instant (planner dedupe works); rerank stage measurably
reorders RRF output; latency instrumented (p50/p95).

## Plan — five marathon phases, strictly sequential

| Phase | Scope | Artifacts | Gate |
|---|---|---|---|
| `gh11-p0-scaffold` | Phase 0 close-out: constraints into `GUIDING-PRINCIPLES.md`, `pyproject.toml`, `xyz/` package skeleton, `tests/`, extend `validate.sh` | `GUIDING-PRINCIPLES.md`, `pyproject.toml`, `xyz/`, `tests/`, `validate.sh` | `bash validate.sh`: package imports, pytest green, PDDA checks green |
| `gh11-p1-chunkers` | Tree-sitter chunkers (Python, JS/TS, PHP), heading-level Markdown, file-level config/templates; path-prefixed embedded text (#8); widened include list (#2) | `xyz/ingest/`, `tests/` | pytest on a fixture tree: function-aligned chunks with `qualified_name`/`start_line`/`end_line`, YAML/Dockerfile chunked, every chunk's `embedded_text` starts with its path |
| `gh11-p2-store` | SQLite store: `chunks` + FTS5 + `vec0`; embed cache keyed `(content_sha, model, dim, provider)`; file-level drift/planner so unchanged re-ingest embeds nothing; provider/dim mismatch refuses | `xyz/index/`, `tests/` | pytest with a fake embedder: second ingest calls the embedder 0 times; mismatch raises; FTS5 and vec0 row counts equal `chunks` |
| `gh11-p3-retrieve` | Query path: BM25 (FTS5) ∥ dense (`vec0`, `k = ?`) → RRF(k=60) → cross-encoder rerank top 25-50 → optional no-answer τ; per-stage latency + p50/p95 helper | `xyz/retrieve/`, `tests/` | pytest with fake embedder + fake reranker: a doc ranked low by both lanes but high by the reranker ends at rank 1; RRF matches the hand-computed value; `k = ?` present in the KNN SQL; τ suppresses below-threshold |
| `gh11-p4-roundtrip` | `xyz` CLI (`ingest`, `query`, `eval`); real round-trip on the sibling LTVera-Pandas checkout with CodeRankEmbed; dense vs hybrid vs hybrid+rerank scored with Run-9 metric definitions; record results | `xyz/cli.py`, `xyz/eval/`, `FINDINGS-0.5.md`, this doc | the four Phase 1 QA-gate bullets above, evidenced in FINDINGS-0.5.md with numbers |

Existing subsystem extended: the `.embed-tmp` embedder + scorer become the **reference** the new
`xyz/` package must reproduce (same chunk fields, same metrics); nothing is duplicated in `.embed-tmp`.
Canonical writer for the index is `xyz/index/store.py` — one SQLite file per index, one writer.

## Dependencies, risks, rollback

- Depends on: the venv at `.venv/` (sentence-transformers, torch, sqlite-vec, tree-sitter,
  tree-sitter-language-pack, pytest) and the HF cache holding `nomic-ai/CodeRankEmbed` and
  `cross-encoder/ms-marco-MiniLM-L-6-v2` (Apache-2.0). Builder turns run with `HF_HUB_OFFLINE=1`; no
  network is assumed inside a turn.
- Risk — p4 embedding time: ~5,100+ chunks at ~0.3 s/chunk on MPS ≈ 25-30 min; the turn timeout is
  set to 7200 s. Fallback recorded in the brief: ingest the `scripts/`, `app/`, `alembic/` subtrees
  only (every gold label lives there) and say so in the results.
- Risk — reranker choice is a placeholder: `cross-encoder/ms-marco-MiniLM-L-6-v2` is general-domain.
  It is configurable; the bake-off (Phase 3) picks the real one. The p3 gate tests behaviour with a
  fake reranker so the placeholder cannot make the gate flaky.
- Reversibility: **Easy** — all new files under `xyz/`, `tests/`, `pyproject.toml`, `validate.sh`;
  one small edit to `GUIDING-PRINCIPLES.md`; nothing in `.embed-tmp` changes. Revert = drop the branch.

## Rating (RELEASES ledger, 2026-09-05)

`rated 85/60/50/30` — pri 85: issue #11 names this act as the keystone every other act is blocked
on, and the user ordered it first. sev 60: not a defect; the consequence is blocked work across the
whole v0.5 release, not data loss. appeal 50: neutral, no user preference given. effort 30: five
phases, new package, one 30-minute real-corpus run — a multi-day build, not a quick win. Recurrence:
n/a (feature). No operator override.

## Swarm Preflight Contract

```json
{
  "target": { "repo": ".", "ref": "marathon/gh11-act1-hybrid-retrieval-2026-09-05" },
  "gate": "bash validate.sh",
  "fix_probes": [
    { "type": "path_absent", "path": "pyproject.toml" },
    { "type": "path_absent", "path": "xyz/" },
    { "type": "path_absent", "path": "tests/" },
    { "type": "path_absent", "path": "xyz/retrieve/pipeline.py" }
  ],
  "artifacts": [
    "GUIDING-PRINCIPLES.md",
    "pyproject.toml",
    "validate.sh",
    "xyz/",
    "tests/",
    "PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md",
    "PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md"
  ],
  "artifacts_new": [
    "pyproject.toml",
    "xyz/",
    "tests/"
  ],
  "remediation": {
    "source": "self#phases",
    "criteria": "Phases gh11-p0-scaffold through gh11-p4-roundtrip of this doc, each gated by bash validate.sh"
  },
  "lanes": {
    "agy_safe": [],
    "orchestrator_only": [".tick/", "marathon-system/", "relay-system/"]
  }
}
```

## Run log

- 2026-09-05 — clone `XYZ-code-intelligence-gh11-act1`, branch
  `marathon/gh11-act1-hybrid-retrieval-2026-09-05` off `origin/v0.5/embedding-eval-coderankembed-vs-gemini`
  (`3301124`, stacked: no PR exists for that branch yet). Venv provisioned, reranker pre-cached.
