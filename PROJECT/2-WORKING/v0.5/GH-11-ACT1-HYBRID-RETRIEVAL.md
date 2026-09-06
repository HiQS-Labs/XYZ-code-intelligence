---
gh_issue: 11
source: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11
title: GH-11 Act 1 — XYZ hybrid retrieval library (canonical doc Phase 0 + Phase 1)
status: active
created: 2026-09-05
updated: 2026-09-06
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
| Plan review closed after 4 rounds / 14 findings; cross-model consult voted FIRE unanimously (both advisors called rounds 3-4 overengineering); prelaunch re-verified with the launch env (2026-09-06). | Marathon firing: p0 scaffold -> p1 chunkers -> p2 store -> p3 retrieval -> p4 real round-trip on LTVera-Pandas. |

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

- Existing writer for chunks: `.embed-tmp/scripts/embed_repos.py` — `INCLUDE_EXT`, `iter_files`
  (~line 106), per-chunk records with `path`, `start_line`, `end_line`, `text` plus `id`/`repo`
  (~136-140, ~160-161), per-repo re-exec, batch 16, `EMBED_PROFILE` telemetry. It does **not** set
  `max_seq_length`; the 2048 cap is a FINDINGS-0.5.md requirement (~174-179) that the new embedder
  must set and test. `qualified_name`, `kind`, `content_sha`, `embedded_text` are new fields. Keep
  the script untouched; the library supersedes it, and it stays as the benchmark-history tool.
- Existing metric definitions: `.embed-tmp/eval/score_retrieval.py` — `rank_of_first_relevant`
  (~133-138), MRR with misses as 0, recall@{1,3,5,10}, `never_found`, `per_query` (~141-156); hit =
  retrieved chunk `path` in `relevant`. It ranks the **whole corpus**; the hybrid pipeline ranks
  `fetch_k` candidates, so p4 reports the same metrics **at an explicit depth D = 100** with its own
  dense-only arm at that depth as the baseline. Run 9 is context, not a comparable number.
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
- "…over the existing 21,580-vector sidecar" — **[changed]** to a fresh ingest of one repo — reason:
  the sidecars are gitignored and not on this branch, and the p1 chunker (path prefix, wider walk)
  changes every chunk, so old vectors would be invalid anyway (FINDINGS-0.5.md: index and query
  model/chunks must match).
- REFACTOR / ABSORB of Ask-Self's revision tracking, ingest planner and harness config
  (issue #11 calibration) — **[dropped]** here, owned by Act 2 — reason: Act 1 needs only the
  cache-key + mismatch semantics (carve-out 1) to be correct; the XYZ file-sha planner in
  `xyz/index/store.py` is the single planner Act 2 reconciles Ask-Self's onto (no second
  planner/store is created here, so nothing is duplicated to remove later).
- "beats vector-only on a **non-saturated** query set" (exit criterion) — **[changed]**, remains
  **outstanding** after this act — reason: growing the set is canonical Phase 2 human labelling; this
  act's gate is the noise-floor comparison above and does not claim to close that criterion.

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

- Environment contract (defined in `validate.sh`, values exported by the operator when firing):
  `XYZ_PY` (interpreter with the pinned deps; default `<repo>/.venv/bin/python`), `XYZ_SCRATCH`
  (generated evidence; default `<repo>/.relay-scratch`, the harness's swept scratch dir — nothing
  goes under `temp/`), `XYZ_EVAL_REPO` (absolute path to the LTVera-Pandas checkout; p4 fails fast if
  unset), `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`. Readiness is a two-step control:
  **`prelaunch.sh`** (operator, before firing) really imports every dependency, instantiates the five
  Tree-sitter parsers and loads both models offline with their real classes (encode + predict) using
  the exact `XYZ_PY`, then writes `<venv>/xyz-prelaunch.json`; **`validate.sh`** (every phase)
  requires that marker for the same interpreter and repeats the cheap checks (real imports, parser
  creation, FTS5/vec0). Red controls for the operator step: run `prelaunch.sh` with `HF_HOME` pointed
  at an empty directory → NOT READY on CodeRankEmbed; with a bogus `XYZ_PY` → not executable. No `pip install` and no editable install inside a turn (the latter
  writes `*.egg-info/` into the tree); `PYTHONPATH=<repo>` makes `xyz` importable.
- Risk — p4 embedding time: ~5,100+ chunks at ~0.3 s/chunk on MPS ≈ 25-35 min; the turn timeout is
  7200 s. The CLI prints an ETA after 200 chunks; > 45 min triggers the fallback: a **fresh** DB
  ingested in one root-preserving invocation restricted to `scripts/`, `app/`, `alembic/` (every gold
  label lives there), labelled `corpus: subset` wherever reported.
- Containment: `CHANGELOG.md` is not on any phase allowlist by design — the orchestrator writes the
  end-of-iteration entry when opening the PR (AGENTS.md §7).
- Risk — reranker choice is a placeholder: `mixedbread-ai/mxbai-rerank-xsmall-v1` (Apache-2.0,
  ~70 MB) is general-domain and configurable via `XYZ_RERANKER`; the bake-off (Phase 3) picks the
  real one, and the p3 gate tests behaviour with a fake reranker so the placeholder cannot make the
  gate flaky. **Changed 2026-09-06:** the original choice `cross-encoder/ms-marco-MiniLM-L-6-v2`
  loads cleanly on this stack (torch 2.14.0 / transformers 5.16.1) but returns `[nan, nan]` — an
  old-format BERT checkpoint, reproduced with plain `AutoModelForSequenceClassification` under both
  `eager` and `sdpa`. Found by `prelaunch.sh` before the marathon fired; `prelaunch.sh` now asserts
  finite *and* correctly-ordered scores. Fallback: `BAAI/bge-reranker-base` (MIT, also verified).
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
- 2026-09-06 — preflight ready (exit 0), `marathon.sh --dry-run` OK (5 phases in order). Codex plan
  review (`relay-system/2026-09-06/gh11-act1-plan-review.md`), three rounds, 13 findings, all
  implemented:
  - **r1** — metric depth, environment contract, subset fallback, red controls, grounding, chunk
    contract, deviation accounting, containment, API defaults.
  - **r2** — vacuous readiness check, incomplete-walk pruning, rerank-tail policy + chunk-id
    evidence, BM25 score direction, contradictory changed-token test. Implementing the readiness
    control (`prelaunch.sh`) **found two real defects before any builder turn**: (1)
    `tree_sitter_language_pack` downloads grammars at first use, so every offline turn would have
    failed at the chunker — now pre-cached and asserted; (2) `cross-encoder/ms-marco-MiniLM-L-6-v2`
    loads cleanly on torch 2.14.0 / transformers 5.16.1 and returns `[nan, nan]` — default reranker
    changed to `mixedbread-ai/mxbai-rerank-xsmall-v1`.
  - **r3** — readiness marker not invalidated on failure and not bound to the validated reranker /
    cache (my own red-control run had left a stale success marker); τ specified as a query-level
    decision, not a per-hit filter; scorer input takes `(chunk_id, path)` records so same-path
    reorders survive. All fixed; `prelaunch.sh` now deletes the marker before testing and publishes
    it atomically, and `validate.sh` rejects it when `XYZ_RERANKER` or the HF cache differs.
  - **Round cap 3/3 exhausted → `STATUS: Escalated`.** Implementation is stopped pending an operator
    decision: extend the cap for a round-4 re-review of the r3 fixes, or accept the plan explicitly.
    The marathon was **not** fired.
