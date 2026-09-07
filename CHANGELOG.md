# CHANGELOG.md

Newest-first, dated end-of-iteration record. One entry per substantive iteration: what changed,
why, and the verification. See `PROJECT/PDDA.md` for the full contract.

## 2026-09-07

### GH-11 Act 1 — the XYZ retrieval library exists

- Delivered canonical Phase 0 close-out + all of Phase 1 as a five-phase marathon (builder Codex,
  reviewer agy); every phase reached `STATUS: Approved`. New `xyz` package: Tree-sitter chunkers
  (Python, JS/TS/TSX, PHP) with path-prefixed chunk text and a widened walk, a SQLite store
  (`chunks` + FTS5 + `vec0`) with a provider-keyed embed cache and a `WalkIncomplete` guard that
  refuses to prune on a partial walk, a BM25 + dense -> RRF -> cross-encoder rerank query path using
  sqlite-vec's `k = ?` form, and an `xyz ingest|query|eval` CLI. 45 tests; `validate.sh` green.
- **Measured, and it cuts against the plan's premise:** at depth 100 on the 30-query labelled subset,
  dense-only scored MRR 0.9444 / R@1 0.9000, hybrid 0.9222, hybrid+rerank 0.9016 — the reranked arm
  is worst, and costs 50,004 ms p50 on CPU. It passed acceptance only because that was written as a
  noise-floor test. The set is saturated (dense R@3 = 1.000) and cannot separate the arms.
- Two defects were caught by the new `prelaunch.sh` readiness control *before* any builder turn ran:
  `tree_sitter_language_pack` downloads grammars at first use (every offline turn would have failed),
  and `cross-encoder/ms-marco-MiniLM-L-6-v2` returns `[nan, nan]` on torch 2.14 / transformers 5.16
  while loading without error. Default reranker changed to `mixedbread-ai/mxbai-rerank-xsmall-v1`.

Verification: `bash validate.sh` -> 45 passed, `validate: OK`; final Codex QA **VERDICT: PASS**
(6 pass, 1 nit, 0 blockers), which also adjudicated the dense win as a property of the saturated
benchmark rather than an implementation bug. PR #15.

### Canonical Phases 2-5 rescoped

- Operator recalibrated to reuse/adapt Ask-Self wherever possible. A `/ponytail` + `/debug-mantra`
  audit (`PARKED/2026-09-07-phases-2-5-ponytail-audit.md`, 8 findings) cut the remaining plan:
  Phase 2 from 250 questions to ~70 selected for **difficulty** (the problem was saturation, not
  sample size); Phase 3 from a four-model matrix to one challenger on the harder set; **Phase 4
  deferred** by Phase 3's own decision rule, which CodeRankEmbed already clears by ~20 points;
  Phase 5 **inverted** — Ask-Self stays the application and XYZ swaps two functions
  (`embed_one`/`embed_batch`, `knn_search`) rather than five subsystems being ported into XYZ.
- Corpus decision: XYZ serves the PHP/WordPress repos. The four originally indexed repos hold
  1 `.php` file between them while the old spec allocated 85 of 250 questions to PHP/Blade/Twig.
  Blade and Twig slices dropped outright — zero occurrences anywhere; WordPress uses plain PHP.
- Corrected two wrong premises in issue #11: `fetch_merged_prs` already exists in Python
  (`ask_self_ingest.py:827-873`) and `buildArchitectureSummary` does not exist at all. Both were
  listed there as blockers gating the Node deletion; both are already cleared.

Verification: `bash validate.sh` -> `validate: OK` (PDDA frontmatter, status-table, roadmap,
roadmap-coverage, hardcoded-paths all clean); module inventory read at `ask-self@origin/main`.

## 2026-08-28

### CodeRankEmbed installed

- Set up local `.venv/` (gitignored) with `sentence-transformers`, `torch`, `einops`; pulled
  `nomic-ai/CodeRankEmbed` into the HuggingFace cache. Usage documented in `SOP.md`.

Verification: loaded the model and encoded a query/code pair, got the expected 768-dim embeddings.

### v0.5 canonical research and build doc

- Synthesized the four Perplexity research docs and the Hyperagent report into
  `PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md`:
  consensus verdict (skip BGE-small, code-native dense lane + permanent BM25/RRF/rerank hybrid),
  reconciled divergences, model shortlist, datasets, conditional fine-tuning pipeline, a 6-phase
  build plan with QA gates, and the Ask-Self inherit/sunset split.
- Marked the five research inputs as roadmap-exempt reference appendices (frontmatter + status
  tables added); pointed the canonical doc from `ROADMAP.md`.

Verification: `./utils/pdda/pdda.sh run` — all checks passed.

### PDDA installed

- Installed the PDDA document-automation surface (`utils/pdda/pdda.sh` + helpers, `PROJECT/PDDA.md`)
  and the `PROJECT/**` lifecycle tree in `observe` mode.
- Next: replace this entry as real iterations land.

Verification: `./utils/pdda/pdda.sh run`
