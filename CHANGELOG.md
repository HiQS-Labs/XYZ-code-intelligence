# CHANGELOG.md

Newest-first, dated end-of-iteration record. One entry per substantive iteration: what changed,
why, and the verification. See `PROJECT/PDDA.md` for the full contract.

## 2026-09-07 (evening)

### The path-only screen, and the red control that proves it works

Phase 2 (#17) is defined by one rule — zero name-carried questions, enforced by a path-only screen.
This makes the rule runnable, so screening is a command rather than a judgment call per question.

- Added `xyz screen` (`xyz/eval/pathscreen.py`). It retrieves over **paths alone**, no file
  contents, and rejects a candidate when a gold path lands in the top 3. Two lanes run and either
  firing is a rejection: BM25 over tokenised paths, and the real embedding model over path strings.
  Paths split on camelCase as well as separators, because a WordPress or JS corpus hides its meaning
  in identifiers like `getUserById` that a separator-only tokeniser leaves welded shut. Exits 1 on
  any rejection, so it can gate a build.
- **Red control: the screen rejects 30/30 of the known-saturated set**, and the dense lane caught 3
  that BM25 never retrieved at all — "timezone and time formatting helpers" for `app/timefmt.py` is
  the shape of it, where query and path share no token but mean the same thing. A lexical-only
  screen would have passed those three into the frozen set. Numbers, and the two caveats that would
  overturn them, in `MEASUREMENTS/runs/2026-09-07-pathscreen-redcontrol.md`.
- Added `--paths-from-git`, so a candidate can be screened without an index. During labelling you
  iterate on questions, not on the corpus; this turns a 10-minute ingest into seconds and makes the
  red control reproducible as a single command.
- **Indexed the first PHP/WordPress repo** — `universal-child-theme-oct-2024`, 143 files / 1,341
  chunks / 9m 48s on CPU, all 47 PHP files in. Two findings worth carrying into Phase 2: the
  "HTML/WP-template" language quota has to be read as **PHP** templates (the repo holds exactly one
  `.html` file, while `archive.php` and `header.php` are the templates), and peak RSS reached
  12.9 GB.
- **One PHP file fails Tree-sitter parsing** because `tree-sitter-php` 1.16.1 rejects
  `const NAMESPACE = ...`, which PHP 7 permits. Measured across both WordPress repos it is **1 of
  120 files** (0 of 73 in the second), so it is isolated and does not undercut the premise that
  Tree-sitter chunking is XYZ's genuine improvement over Ask-Self's regex chunkers. Taking the
  number mattered more than assuming it.

**Verification:** `validate: OK` — 65 tests (20 for the screen, including four that drive the CLI
after a missing import passed every unit test and still crashed the command).

## 2026-09-07 (latest)

### Post-merge consistency sweep: stale numbers, a dropped cleanup step, and the verified env

Housekeeping after PR #16 merged, plus one thing a two-agent recon of the pre-merge stash found.

- **Three live "what's next" statements still said `~70 questions`** — the canonical doc's status
  table, `ROADMAP.md`, and the Act 1 capture doc — while `MEASUREMENTS/BASELINE.md` had already
  settled the size at **50**. Anyone starting Phase 2 reads a status table, not a ledger, so the
  contradiction pointed the wrong way. All three now name the frozen 50, the 20-question dev split
  and the path-only screen, and link #17. Two older `250-query` references are kept but re-framed as
  history rather than plan, since the reasoning behind their supersession is worth preserving.
- **Phase 5 gained step 6: delete the known footguns in place.** `ASK_SELF_PATH`, the
  `db_filename`/`db_path` footgun, the disabled Qwen provider paths and the copied-not-linked slash
  commands were listed under **Sunset (do not port)** and were retired implicitly by the old step
  "archive the Ask-Self repo". The 2026-09-07 inversion to an absorption model dropped that archive
  step by design — Ask-Self stays and keeps running — which silently un-retired all four. "Do not
  port" retires nothing when there is no longer a port.
- **Added `requirements-verified.txt`** — the exact 49-package set, captured from the Act 1 clone's
  virtualenv just before that clone was deleted. `pyproject.toml` remains the install source and
  pins the 7 direct dependencies; this file records the transitive set as well, because the
  transitive versions were load-bearing at least once: transformers 5.16.1 with torch 2.14.0 loads
  `cross-encoder/ms-marco-MiniLM-L-6-v2` without error and returns `[nan, nan]`. It is a record to
  diff against, not a lockfile to install from.
- Closed #6 (local-only multi-arm scorer) — delivered as `xyz eval --modes`, not as the proposed
  patch to `score_retrieval.py`. Opened #17 (Phase 2). Retired the Act 1 clone and dropped the
  superseded stash; the recon confirmed no URL, numeric constraint, issue reference or decision
  rationale was lost with it.

**Verification:** `pdda governance / frontmatter / status-table / roadmap / roadmap-coverage /
hardcoded-paths / changelog` all `errors=0 warns=0` under `PDDA_MODE=full`.

## 2026-09-07 (later)

### MEASUREMENTS ledger, and the benchmark baseline settled from defaults

- Added `MEASUREMENTS/` — `BASELINE.md` (every tuning knob, its value, and *why that value*) and
  `runs/` (one immutable file per measurement run). Wired into `ROUTER.md` and `README.md`. The
  first run record backfills the Act 1 round-trip, including the caveat that its numbers are upper
  bounds on a saturated set. Each knob is tagged **default / measured / constraint / judgment**, and
  the six that are still `judgment` are listed openly so they can be attacked rather than inherited.
- **Replaced the invented "~70" benchmark size with 50** — the TREC per-track convention. Derived by
  the operator's ladder: field default first, then guiding principles #3 (*deterministic where
  judgment isn't needed*) and #7 (*labelling is expensive and irreversible, so start small and grow
  on evidence*), then a cross-model consult to break what remained. Both advisors independently
  confirmed 50 and named the same convention.
- Consult adjudications recorded with their reasoning: stratify by **query type, not language**
  (both advisors); **zero name-carried questions** enforced by a deterministic **path-only screen** —
  reject any candidate whose gold file a path-only baseline ranks in the top 3 (Codex over agy, whose
  10 "sanity check" questions are instead served by keeping the old saturated 30-query set as a
  separate regression set); **dev split 20** as 10 answerable + 10 no-answer, disjoint from the frozen
  set *and its gold files*; **growth rule** of +25 when every arm hits answerable R@3 = 1.000.

Verification: `bash validate.sh` -> `validate: OK`. Consult transcripts:
`relay-system/2026-09-07/benchmark-baseline-103905/`.

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
