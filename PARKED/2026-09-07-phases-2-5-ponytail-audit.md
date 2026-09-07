# Phases 2-5 — ponytail / debug-mantra audit, 2026-09-07

Lens: `/ponytail` (full) + `/debug-mantra`. Goal recalibrated by the operator to *reuse and adapt
Ask-Self / Ask-Code wherever possible* — with the follow-up clarification that **"rebuild clean" is
close enough to "reuse and adapt"**. So the test applied below is **least total work to ship**, not
"must port".

Ground truth this audit is built on (measured, PR #15, `FINDINGS-0.5.md`):

| mode | MRR@100 | R@1 | R@3 | R@10 |
|---|---:|---:|---:|---:|
| dense (CodeRankEmbed) | 0.9444 | 0.9000 | 1.0000 | 1.0000 |
| hybrid | 0.9222 | 0.8667 | 0.9667 | 1.0000 |
| hybrid+rerank | 0.9016 | 0.8667 | 0.9667 | 0.9667 |

Corpus: 339 files / 3,020 chunks, 30 labelled queries, saturated at R@3.

---

## Finding 1 — Phase 4 is already excluded by Phase 3's own decision rule

**Severity: high (deletes an entire phase).**

Phase 3's rule, verbatim: *"if a candidate hits file-level Recall@10 ≥ 0.80 AND MRR@10 ≥ 0.70 on the
Python, JS/TS, and PHP slices → adopt as-is and invest in chunking + reranking; **skip Phase 4**."*

CodeRankEmbed measured **R@10 = 1.000** and **MRR = 0.9444** — clearing both bars by ~20 and ~24
points. The rule fires "adopt as-is."

Phase 4 is LoRA fine-tuning, triplet mining, benchmark deduplication and optional distillation. Its
own preamble says *"Only if the Phase 3 rule fails."* It has not failed.

**Honest caveat, stated because it cuts against the finding:** the current set is saturated, so these
numbers are an upper bound and a harder set could drop the model below the bar. That is a reason to
**defer Phase 4 until the harder set exists**, not a reason to build it now. Nothing about fine-tuning
gets cheaper by starting early, and every hour spent there is unrecoverable if the rule holds.

**Action:** mark Phase 4 *deferred — decision rule already satisfied on available evidence; re-open
only if the Phase 2 replacement set drops CodeRankEmbed below R@10 0.80 / MRR 0.70.*

---

## Finding 2 — A third of Phase 2's benchmark targets languages the corpus does not contain

**Severity: high (the spec cannot be executed as written).**

Phase 2 specifies 250 questions in 9 slices, including **PHP 30**, **HTML/Blade/Twig 25**, and
**cross-language PHP↔JS/TS bridging 30** — **85 of 250 (34%)**.

File census across all four indexed repos (`find`, excluding `node_modules`/`.venv`/`.git`):

| repo | .py | .js | .ts | .tsx | .php | .blade.php | .twig | .html |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LTVera-Pandas | 660 | 390 | 0 | 0 | **1** | 0 | 0 | 220 |
| aegis-sleuth-slack-bot | 54 | 325 | 2 | 0 | **0** | 0 | 0 | 11 |
| rebalanceOS | 550 | 21 | 8 | 0 | **0** | 0 | 0 | 6 |
| XYZ-forge | 200 | 113 | 6 | 0 | **0** | 0 | 0 | 80 |
| **total** | 1,464 | 849 | 16 | **0** | **1** | **0** | **0** | 317 |

One PHP file. Zero Blade, zero Twig, zero TSX. You cannot hand-label 85 questions against content
that is not there. TS is also thin (16 files) against a 30-question slice.

This is **not** "the plan is wrong" — the operator demonstrably works in PHP/WordPress elsewhere
(mu-plugins, Woo plugins, child themes are all in the working directories). The plan and the corpus
simply disagree about which repos XYZ serves.

**Action — pick one, do not split the difference:**
- (a) Index the PHP/WordPress repos, and the PHP slices become real; or
- (b) Drop the PHP/Blade/Twig/cross-language slices and size the set to the corpus we have.

Until that is decided, Phase 2 cannot start on 34% of its scope.

---

## Finding 3 — Phase 2 needs *harder* questions, not 250 of them

**Severity: medium (8x scope reduction).**

Diagnosis first (debug-mantra: know the fail path). The failure is **not** "30 is too few for
statistical power." It is **saturation**: dense already returns the right file in the top 3 for
**every single query**. A ruler that reads 100% cannot show that one arm beats another, and adding
220 more questions of the same difficulty produces a longer ruler that still reads 100%.

What actually restores discriminating power is difficulty: questions whose answer is *not*
name-carried. The project already proved the mechanism — issue #8 showed that simply prefixing each
chunk with its file path moved MRR 0.80 → 0.98, because most of these queries are answerable from
filenames alone (`"probe klaviyo api rate limits"` → `scripts/probe_klaviyo_rate_limits.py`). Any
question a filename answers cannot separate two retrievers.

**Lazy version:** grow to ~60-80 questions **selected for difficulty** — behaviour-described-not-named,
cross-file, "how does X work", and no-answer negatives — on repos that exist. Reuse
`.embed-tmp/eval/queries-*.json` (the format already works) and `xyz eval` (already written, already
depth-parameterised, already computes MRR/R@k/miss). Freeze it before the next model comparison.

Skipped: the 250 target and the 9-slice matrix. Add when a real second corpus (PHP/WordPress) is
indexed and the slices correspond to something.

---

## Finding 4 — Phase 2's "end-to-end agent context success rate" is a second evaluation system

**Severity: medium (delete for now).**

Phase 2's metric list ends with *"end-to-end agent context success rate (top-5 chunks fed to a coding
agent, downstream pass rate)."* That means: wire a coding agent into the benchmark harness, define
task success, and run it per model per slice — an agent-in-the-loop evaluation with its own
non-determinism, cost and flakiness, built to referee a retrieval difference we cannot yet measure
with MRR.

Ponytail rung 1: does this machinery need to exist? Not yet. It is a *downstream* proxy for a metric
we already have a *direct* one for.

Also in the same list and worth trimming: bootstrap confidence intervals and nDCG@10 are fine to
keep (cheap, already-standard), but "index size on disk" and "indexing throughput" are already
emitted by `xyz ingest`'s report — no new instrumentation needed.

**Action:** drop the agent-in-the-loop metric from Phase 2. Revisit only if two candidate models tie
on the harder set and a tiebreak is genuinely needed.

---

## Finding 5 — Phase 3's bake-off re-confirms a bar already cleared

**Severity: medium (scope reduction, not deletion).**

Phase 3 as written: an Apple-Silicon smoke gate for every `trust_remote_code` model, then
CodeRankEmbed + NightOwl-35M + jina-v2-base-code + optionally CodeSage-small-v2, against five
controls, plus a CoIR public-suite regression.

The doc's own evidence appendices already record that the public CoIR/CSN numbers are
**leakage-inflated upper bounds** and that *"the frozen benchmark is the only number that decides
anything."* So the CoIR regression arm decides nothing by the plan's own reasoning.

`.embed-tmp/eval/score_retrieval.py` **already implements N-arm local comparison** with per-arm
`--model`/`--backend` (that was GH-6, already shipped and verified against the Run 9 baseline). The
bake-off does not need new machinery — it needs the harder query set from Finding 3 and one command.

**Lazy version:** when the harder set exists, run **CodeRankEmbed vs one challenger** on it with the
existing scorer. If CodeRankEmbed still clears R@10 0.80 / MRR 0.70, stop — the rule says adopt.
Skipped: the four-model matrix, the five controls, the CoIR arm, the MPS training-step smoke (nothing
is being trained unless Phase 4 re-opens).

---

## Finding 6 — Phase 5 is the one place the recalibration really bites

**Severity: high (largest work reduction available).**

Phase 5 currently reads: *"Port Ask-Self's synthesis + citation + doc-history layer into XYZ."* That
is five subsystems moving **into** XYZ — synthesis, citations, revision history, harness config,
entry points.

The recalibration inverts the direction, and the inversion is much lazier: **Ask-Self already is the
application.** It has the CLI, the harness config, the registry, synthesis, citations, history and
the slash-command entry points. What it has that is *worse* than XYZ is exactly one thing, and issue
#11 already pinned it: `knnSearch()` is *"pure vector KNN + a 0.02 priority boost — no FTS5, no
hybrid fusion, no rerank."*

So the smallest change that ships the whole capability is: **XYZ stays a retrieval library, and
Ask-Self's query path imports it** — replacing its embed+KNN internals while every other Ask-Self
subsystem stays where it is and keeps working. Nothing gets ported; one function gets swapped.

The measured result strengthens this, incidentally: dense-only currently wins, and dense-only is very
close to what Ask-Self already does. The honest near-term delta XYZ brings is *local + free + no
network*, not *better ranking* — the ranking win is unproven until the harder set exists.

**Inventory landed — the direction is confirmed, and more strongly than expected.** Read at
`origin/main` (`461574f`):

| Ask-Self module | lines | provider coupling |
|---|---:|---|
| `ask_self_query.py` | 1,879 | mixed — 4 embed + 4 synthesis providers, all behind dispatchers |
| `ask_self_ingest.py` | 2,291 | mixed — only `embed_one`/`embed_batch` (`:426`, `:502`) are provider-specific |
| `ask_self_revisions.py` | 685 | **agnostic** — full revision schema + CRUD |
| `ask_self_history.py` | 348 | **agnostic** — `history` / `prune-history` CLI |
| `ask_self_architecture.py` | 1,131 | mixed — has a deterministic non-LLM fallback (`:481`) |
| `ask_self_eval.py` | 322 | **agnostic** — recall@k, precision@k, MRR, nDCG@k |
| `ask_self_helpers.py` | 389 | **agnostic, pure** — the chunkers |
| `ask_self_cache.py` | 189 | **agnostic** — cache keyed `(content_sha, model, dim, provider)` |
| `ask_self_harness.py` | 927 | mostly agnostic; corpus/classification half is engine-independent |
| registry / events / dashboard / normalize / audit / cli / `rag_agent.py` / `bin/ask-self` | ~1,600 | **agnostic** |

Three facts decide it:

1. **Synthesis is already provider-pluggable.** `synthesize()` (`ask_self_query.py:1449`) dispatches
   on `settings["provider"]` to four sibling functions — Gemini (`:759`), Ollama (`:808`),
   OpenAI-compatible (`:859`), Cloudflare (`:918`). Gemini is the default but **not** structurally
   privileged. There is nothing to "port": swapping or adding a provider is one function plus one
   branch at `:1461`.
2. **Citations are pure post-processing** (`ask_self_query.py:1673-1685`) — built from retrieval hits,
   deduped, capped at 8, no LLM involvement at all. Nothing to port.
3. **`ask_self_eval.py` already accepts a pluggable retriever** — `Retriever = Callable[[str],
   list[str]]`, wired via `make_live_retriever` (`:166`). XYZ's retriever can be scored by Ask-Self's
   existing harness by passing one function.

**The swap surface is two functions**, not five subsystems: `embed_one`/`embed_batch` on the ingest
side and `knn_search` (`ask_self_query.py:1199`) on the query side. Everything else — CLI, HTTP
wrapper, registry, config, synthesis, citations, history, PR ingest, architecture, dashboard —
already works and is provider-agnostic.

**What XYZ genuinely adds** (i.e. what Act 1 was right to build): Tree-sitter chunking (Ask-Self's
`ask_self_helpers.py` chunkers are **regex/line-based**, no parse tree, no nested-symbol boundaries),
FTS5 + RRF + rerank retrieval, and local/offline embedding. Those are real upgrades, not duplication.

---

## Finding 7 — Two premises in issue #11 are factually wrong

**Severity: medium (removes stated blockers from Acts 2-3).**

Issue #11 states: *"What the Node side has that must be **ported into Python** before deletion:
**GitHub PR ingestion** (`fetchMergedPRs`) and `buildArchitectureSummary`. These are the only real
migration items — do not delete `src/rag/` until they land."*

Both claims fail on inspection of `origin/main`:

- **PR ingestion already exists in Python.** `fetch_merged_prs` at `ask_self_ingest.py:827-873` —
  paginated `GET /repos/{owner}/{repo}/pulls?state=closed`, filtered on `merged_at`, Bearer token;
  consumed by `build_pr_file_builds` (`:1384`) and `build_pr_rows` (`:1495`); configured by the
  `github` block in `ask_self_harness.json:22-30`. Nothing to port.
- **`buildArchitectureSummary` does not exist in this repo at all** — and neither does a Node ingest
  path; `ask_self_query.mjs` is query-only. Python's `ask_self_architecture.py` (1,131 lines) already
  writes `ARCHITECTURE.md` with an `ast` symbol index and a deterministic non-LLM narrative fallback.

**Action:** correct issue #11's Act 2 section. The stated pre-deletion blockers are already satisfied
or never existed, which removes work from the critical path rather than adding it.

---

## Finding 8 — There are now three retrieval scorers

**Severity: medium (self-inflicted, worth fixing before Act 2).**

1. `.embed-tmp/eval/score_retrieval.py` — N-arm local comparison (GH-6, verified against Run 9)
2. `xyz/eval/metrics.py` — built in Act 1 p4 (MRR@D, R@k, miss@D, chunk-id preserving)
3. `ask_self_eval.py:70-115` — recall@k, precision@k, MRR, nDCG@k, markdown report, baseline diff

Three implementations of the same metrics is exactly the duplication the plan set out to avoid. In
fairness the Act 1 one was written to a spec that predates this audit, and it is the only one that is
depth-parameterised and chunk-id-aware — so it is the reasonable survivor.

**Action:** pick `xyz/eval/metrics.py` as canonical, and have the other two call it rather than
reimplement. Do not write a fourth for Phase 2.

---

## What this collapses to

| phase | as planned | after audit |
|---|---|---|
| 2 | 250 questions, 9 slices, agent-in-the-loop metric | ~60-80 **harder** questions on repos that exist; existing scorer; decide the PHP corpus question first |
| 3 | 4 models × 5 controls + CoIR regression | 1 challenger vs CodeRankEmbed on the harder set, existing N-arm scorer |
| 4 | LoRA + triplet mining + distillation | **deferred** — Phase 3's own rule already says skip |
| 5 | port 5 subsystems into XYZ | swap **two functions** inside Ask-Self — `embed_one`/`embed_batch` and `knn_search`; ~7,700 lines of agnostic Ask-Self stay put |

**One decision is genuinely the operator's and blocks Phase 2:** does XYZ serve the PHP/WordPress
repos, or only the four Python/JS repos currently indexed? Everything in Finding 2 hangs on it.
