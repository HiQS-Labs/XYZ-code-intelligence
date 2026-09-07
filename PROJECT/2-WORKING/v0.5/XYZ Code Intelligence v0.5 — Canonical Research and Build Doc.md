---
title: XYZ Code Intelligence v0.5 — Canonical Research and Build Doc
status: active
created: 2026-08-28
updated: 2026-09-07
owner: Noel Saw
goal: Synthesize the Perplexity and Hyperagent v0.5 research into one canonical plan for building the XYZ code intelligence system and sunsetting Ask-Self.
effort: 4
complexity: 4
risk: 2
phases: 6
related:
  - "PROJECT/2-WORKING/v0.5/BGE Small vs Code-Capable Embeddings — Decision Report.md"
  - "PROJECT/2-WORKING/v0.5/Code Embedding Models — Full Evidence Table.md"
  - "PROJECT/2-WORKING/v0.5/NL-to-Code Retrieval Datasets — Full Evidence Table.md"
  - "PROJECT/2-WORKING/v0.5/Embedding Fine-Tuning Training Pipelines — Full Evidence Table.md"
  - "PROJECT/2-WORKING/v0.5/hyperagent-report.txt"
context_tags: [embeddings, retrieval, rag, ask-self-sunset, apple-silicon]
non_goals:
  - Cloud-hosted embedding APIs as the primary lane (local-first is the constraint)
  - Fine-tuning before the frozen benchmark exists
  - Rebuilding what Ask-Self already provides provider-agnostically (synthesis, citations, history, PR ingest, registry) — XYZ swaps its embed + KNN functions instead
---

# XYZ Code Intelligence v0.5 — Canonical Research and Build Doc

This document supersedes the five v0.5 research inputs (four Perplexity docs + the Hyperagent
report) as the single source of truth for what XYZ v0.5 builds. The research docs remain in this
folder as evidence appendices; per-claim citations live there.

## Status

| What was just completed | What's next |
|---|---|
| Act 1 delivered (Phases 0-1: `xyz` package, chunkers, store, hybrid retrieval, round-trip — PR #15). Phases 2-5 rescoped after a ponytail/debug-mantra audit (2026-09-07). | Phase 2: build the ~70-question **harder** frozen set, now including the PHP/WordPress repos. |

## Table of contents

- [Consensus verdict](#consensus-verdict)
- [Where the two research tracks diverge](#where-the-two-research-tracks-diverge)
- [Target architecture](#target-architecture)
- [Model shortlist and controls](#model-shortlist-and-controls)
- [Datasets](#datasets)
- [Fine-tuning pipeline (conditional)](#fine-tuning-pipeline-conditional)
- [What XYZ inherits from Ask-Self, and what it sunsets](#what-xyz-inherits-from-ask-self-and-what-it-sunsets)
- [Phase 0 — Decision lock and repo scaffolding](#phase-0--decision-lock-and-repo-scaffolding)
- [Phase 1 — Chunking + hybrid retrieval skeleton](#phase-1--chunking--hybrid-retrieval-skeleton)
- [Phase 2 — Frozen private benchmark](#phase-2--frozen-private-benchmark)
- [Phase 3 — Model bake-off](#phase-3--model-bake-off)
- [Phase 4 — Conditional fine-tuning — DEFERRED](#phase-4--conditional-fine-tuning--deferred)
- [Phase 5 — Ask-Self absorption](#phase-5--ask-self-absorption-was-sunset-and-migration)
- [Open questions and risks](#open-questions-and-risks)

## Consensus verdict

Both research tracks — Perplexity (4 docs) and Hyperagent (1 report) — independently reach the
same five conclusions:

1. **Do not fine-tune `BAAI/bge-small-en-v1.5` for code.** Its uncased 30,522-token
   `bert-base-uncased` tokenizer cannot faithfully encode identifiers (`getUserById`, `$wpdb`,
   `__init__`), and its 512-token window truncates real functions. Fine-tuning changes weights,
   not the tokenizer — the ceiling doesn't move. No credibly evaluated code fine-tune of it
   exists anywhere on Hugging Face (383 derivatives, 2 code-related, both fail the evidence bar).
   Hyperagent measured it at <20 MRR zero-shot on CodeSearchNet.
2. **Adopt a code-native embedding model as the dense lane** (shortlist below), benchmarked
   before any training.
3. **Hybrid retrieval is permanent, not a stopgap:** SQLite FTS5/BM25 lexical lane + dense lane,
   fused with Reciprocal Rank Fusion (k=60), then a local cross-encoder reranker over the top
   25–50 candidates (~40 ms/query end-to-end per Hyperagent). Exact-symbol lookup is lexical;
   hybrid+rerank is the safety net for cross-language and template queries.
4. **Benchmark before you train.** Public code benchmarks are leakage-saturated (CodeSearchNet
   contamination can inflate metrics up to 100%); most "fine-tuning needed" conclusions are
   benchmark artifacts. A frozen, hand-labeled private benchmark decides everything.
5. **HTML/templates/config/schemas are a genuine gap for every code model surveyed.** No public
   labeled HTML/template retrieval benchmark exists. Those file types get a dedicated BM25 lane,
   a custom eval slice, and `jinaai/jina-embeddings-v2-base-code` as the only dense model worth
   *testing* there (its HTML/CSS/Markdown coverage is a claim, not evidence).

## Where the two research tracks diverge

| Question | Perplexity | Hyperagent | Canonical resolution |
|---|---|---|---|
| Top dense-lane pick | NightOwl-CodeEmbedding-35M (same footprint as BGE-small) | CodeRankEmbed 137M ("Top Recommendation") | Benchmark both; CodeRankEmbed is the cross-source consensus, NightOwl-35M is the footprint-preserving challenger with single-author risk. The frozen benchmark decides. |
| Big-model option | Qwen3-Embedding-0.6B as licensable stand-in | jina-code-embeddings-1.5b (GGUF Q4) for complex RAG | Neither is v0.5 primary; 1.5B-class indexing throughput (~150 chunks/sec) is too slow for bulk indexing. Park for v0.6. |
| CoRNStack license | Unstated on the HF card | Apache 2.0 | Unverified — confirm before training on it (open question below). |
| Fine-tuned BGE-small in the bake-off | Excluded (wrong base, full stop) | Kept as a candidate to test whether LoRA overcomes its limits | Keep untuned BGE-small as a control only. Do not spend training budget proving what both docs already concluded. |

Benchmark slice counts differed slightly between sources; the merged canonical design in Phase 2
uses Hyperagent's 250-query/9-slice frame with Perplexity's metric set and decision rule.

## Target architecture

Query → embed (dense lane) + FTS5 match (lexical lane), in parallel, over AST/Tree-sitter
chunks → RRF fusion (k=60) → cross-encoder rerank of top 25–50
(`bge-reranker-large` or `jina-reranker-v2-base-multilingual`) → no-answer threshold τ on max
similarity → top-k context to the agent/synthesis layer.

- Chunking: AST/Tree-sitter function/class chunks for code; heading-level for Markdown;
  file-level for small config/templates/schemas. Chunking is held constant across all
  benchmark runs.
- Store: SQLite — `sqlite-vec` for vectors + FTS5 for lexical, one file, inheriting Ask-Self's
  proven store pattern (see inheritance section).
- Everything local on Apple Silicon (MPS/MLX); commercial-safe licenses only (Apache-2.0/MIT).

## Model shortlist and controls

Candidates (bake-off in Phase 3; exact figures per the evidence tables):

| Model | Params/dims/ctx | License | Key numbers | Role |
|---|---|---|---|---|
| `nomic-ai/CodeRankEmbed` | 137M / 768 / 8,192 | MIT | CSN MRR 77.9; CoIR 60.1; Py 78.4 / JS 71.4 / PHP 68.8; >1,200 chunks/sec on M-series | Consensus favorite; 8k window for cross-file queries. Mandatory query prefix "Represent this query for searching relevant code"; needs `trust_remote_code`. |
| `Shuu12121/NightOwl-CodeEmbedding-35M` | 34.1M / 384 / 1,024 | Apache-2.0 | MTEB(Code) 0.65555; CSN Py 0.893 / PHP 0.868 / JS 0.772 | Same-footprint BGE-small replacement; preferred fine-tuning base (ST-compatible); single-author risk; only 8% zero-shot. |
| `jinaai/jina-embeddings-v2-base-code` | 161M / 768 / 8,192 | Apache-2.0 | CoIR 58.4 (third-party); weakest on PHP 0.5701 | Templates/config lane test only — sole model declaring HTML/CSS/Markdown coverage. |
| `codesage/codesage-small-v2` | 130M / 1,024 / 2,048 | Apache-2.0 | NL2Code avg 64.41; PHP 60.20 | Optional 4th candidate; only compact model with published PHP + TS numbers. |

Controls (fixed): untuned BGE-small-en-v1.5, the current local Qwen embedding, FTS5/BM25
lexical-only, hybrid+RRF without rerank, hybrid+RRF+rerank.

Rejected with cause (full list in the evidence tables): jina-code-embeddings-0.5b and
SFR-Embedding-Code-400M_R (CC-BY-NC, non-commercial), BGE-code-v1 1.54B and nomic-embed-code 7B
(impractical locally), every BGE-small code fine-tune on HF (no credible eval), distillation
into BGE-small (keeps the broken tokenizer; weakest fallback), embeddinggemma-300m (non-OSI
license; kept only as a zero-shot reference point).

## Datasets

Training (only if Phase 4 triggers):
- **Own repo-mined triplets first** — docstring↔implementation, issue↔code-diff pairs; anchor =
  query/docstring/issue, positive = AST chunk, hard negative = BM25 false positive from the same
  repo. This is the highest-signal data and both sources rank it above all public sets.
- **The Vault (function level)** — 34.1M pairs, MIT, incl. 4.7M PHP: the PHP/scale workhorse.
- **CoRNStack** — ready-made hard-negative triplets (trained CodeRankEmbed); license unverified.
- **CommitPackFT** — the only realistic HTML/template + rich-PHP signal (php 24,791; html
  20,214 samples); requires reformatting commit subjects into queries.
- **CoSQA + StaQC** — shift query distribution from docstrings to real user phrasing.
- Rejected: raw CodeSearchNet (worst contamination), AdvTest/WebQueryTest/CoSQA+ (Python-only or
  toy-sized), SWE-bench Lite (memorized), The Stack raw (no labels — mining substrate only).

Evaluation:
- **The frozen private benchmark (Phase 2) is primary.** Public suites are secondary regression
  checks: CoIR subsets (`pip install coir-eval`, cosqa + codesearchnet) for speed, CORE-Bench for
  multi-positive PHP/TS qrels, CodeRAG-Bench's BEIR format for a local-repo conversion.
- Mandatory hygiene: dedup any public training data against eval corpora at function level
  before reporting a number.

## Fine-tuning pipeline (conditional)

Runs only if the Phase 3 decision rule fails. Stack (assembled — no ready-made
LoRA+hard-negatives+code recipe exists anywhere):

- Sentence Transformers end-to-end on `device="mps"`: `MultipleNegativesRankingLoss`
  (scale=20.0), `CachedMultipleNegativesRankingLoss` (GradCache) for large effective batches in
  unified memory, `BatchSamplers.NO_DUPLICATES`, `mine_hard_negatives()`,
  `InformationRetrievalEvaluator`.
- LoRA via the ST PEFT recipe: `LoraConfig(task_type=FEATURE_EXTRACTION, r=64, lora_alpha=128,
  lora_dropout=0.1)` — documented at 0.4705 vs 0.4728 NDCG@10 against full fine-tune, 9.44 MB
  adapter.
- FlagEmbedding borrowed for its data contract only: JSONL
  `{"query","pos","neg","pos_scores","neg_scores","prompt","type"}` and `hn_mine.py` parameters
  (`--range_for_sampling 2-200 --negative_number 15`). Not used as trainer (CUDA/DeepSpeed-shaped).
- MPS constraints: macOS 14+ for bf16, `PYTORCH_ENABLE_MPS_FALLBACK=1`, model must fit unified
  memory, fixed-shape batches + `torch_empty_cache_steps` against Metal graph-cache growth.
- Budget anchors (Hyperagent): bge-small-class full FT <2 GB / ~15 min; CodeRankEmbed LoRA
  (r=16 on q_proj, v_proj, out_proj) ~3.5 GB at batch 32. Neither Perplexity doc found any
  published Mac training time/cost figures — treat these as the only estimates we have.

## What XYZ inherits from Ask-Self, and what it sunsets

Ask-Self (the `Hypercart-Dev-Tools/ask-self` repo, v0.7.12) is the system XYZ replaces. Survey
of its architecture (2026-08-28):

**Inherit (proven, keep the pattern):**
- SQLite + `sqlite-vec` store with the `vec0` KNN `k = ?` form (their issue #23: parameterized
  `LIMIT ?` 500'd in production).
- Embedding cache keyed on `(sha256(content), model, dim, provider)` + drift detection that
  forces a rebuild on model/dim/provider change — this caught a real cross-provider cache
  poisoning bug (two "same" BGE-small providers agreeing only ~0.95 cosine).
- Ingest planner that dedupes against the existing DB before embedding (35.67s → 1.34s on
  unchanged re-ingest).
- Harness JSON include/exclude corpus policy — their hardest-won lesson: "bad include patterns
  hurt answer quality faster than prompt tuning fixes it."
- Chunk sizing discipline: their 1200-char/150-overlap targets existed to duck BGE-small's
  512-token window; XYZ re-derives sizes from the chosen model's real context (1,024–8,192).

**Sunset (do not port):**
- BGE-small and the Gemini-embedding default (768-d truncated) — replaced by the shortlist.
- Cloud synthesis dependency as default; XYZ is local-first.
- Priority-nudge + AST-boost shallow reranking — replaced by a real cross-encoder stage.
- The disabled Qwen provider paths, the `db_filename` vs `db_path` footgun, the globally
  exported `ASK_SELF_PATH` (made every repo query Ask-Self's own index), and copied-not-linked
  slash commands that go stale on upgrade.

> **Reconciliation with issue #11 (rewritten 2026-08-30; note added 2026-09-05).** The release
> issue supersedes this doc on posture: XYZ **absorbs** Ask-Self's Python pipeline (cache, drift
> detection, revision tracking, harness config) rather than rewriting it, and swaps only the
> embedding and ranking layers. Phase 0 steps 2-3 and all of Phase 1 are executed as **Act 1** of #11
> via [GH-11-ACT1-HYBRID-RETRIEVAL.md](GH-11-ACT1-HYBRID-RETRIEVAL.md). Phase 2's 250-query benchmark
> is deferred: the existing 30-query set is saturated (#11 caveat 2) and growing it is human
> labelling work. Phases 3-5 stand as written.

## Phase 0 — Decision lock and repo scaffolding

1. Ratify this doc as canonical; mark the five research inputs as evidence appendices.
2. Scaffold the XYZ package layout (ingest / index / retrieve / eval modules), pinning
   `sqlite-vec`, Sentence Transformers, Tree-sitter grammars for Python, JS/TS, PHP.
3. Record the licensing constraint (Apache-2.0/MIT models only) and local-first constraint as
   repo invariants.

**QA gate:** doc passes `utils/pdda/pdda.sh run`; skeleton imports cleanly; constraints written
into the repo's guiding docs.

## Phase 1 — Chunking + hybrid retrieval skeleton

1. AST/Tree-sitter chunkers for Python, JS/TS, PHP; heading-level Markdown; file-level
   config/templates/schemas.
2. SQLite store: `chunks` + FTS5 table + `sqlite-vec` `vec0` table; embed cache and drift
   detection per the Ask-Self inheritance list.
3. Retrieval path: parallel BM25 + dense → RRF(k=60) → cross-encoder rerank top 25–50 →
   no-answer threshold τ.
4. Wire any one shortlist model (CodeRankEmbed) end-to-end as the placeholder dense lane.

**QA gate:** ingest + query round-trip on one real repo; unchanged re-ingest is near-instant
(planner dedupe works); rerank stage measurably reorders RRF output; latency instrumented
(p50/p95).

## Phase 2 — Frozen private benchmark

> **Rescoped 2026-09-07** after the Act 1 measurement and a ponytail/debug-mantra audit
> (`PARKED/2026-09-07-phases-2-5-ponytail-audit.md`). The original 250-question, 9-slice spec
> assumed a corpus that did not exist and mis-diagnosed the problem as sample size.

**The problem is saturation, not volume.** On the 30-query set, dense retrieval returns the right
file in the top 3 for *every* query (R@3 = 1.000, MRR 0.9444). A ruler reading 100% cannot rank two
retrievers, and 220 more questions of the same difficulty produce a longer ruler that still reads
100%. Issue #8 already showed why most of these queries are easy: prefixing each chunk with its file
path moved MRR 0.80 → 0.98, because the answers are carried by filenames
(`"probe klaviyo api rate limits"` → `scripts/probe_klaviyo_rate_limits.py`). **Any question a
filename answers cannot separate two retrievers.**

So the target is **difficulty, not count**: roughly **60-80 questions selected to be hard**, frozen
before any model selection.

**Corpus (decided 2026-09-07: XYZ serves the PHP/WordPress repos too).** The four originally indexed
repos are Python/JS only — across all of them: 1 `.php` file, 0 `.blade.php`, 0 `.twig`, 0 `.tsx`.
PHP coverage therefore requires indexing the WordPress repos, which are real and git-backed:

| repo | .php | .js |
|---|---:|---:|
| `universal-child-theme-oct-2024` | 47 | 21 |
| `KISS-woo-order-monitoring-alerts` | 59 | 1 |
| `LTVera-Pandas` | — | 390 |
| `rebalanceOS` / `aegis-sleuth-slack-bot` / `XYZ-forge` | — | 459 |

**Blade and Twig are dropped as slices.** They are Laravel/Symfony conventions and appear **zero**
times in this stack; WordPress uses plain PHP templates. The template slice is retargeted to WP theme
templates and HTML, which do exist.

Slices, sized to the corpus (~70 questions):

| slice | n | why it is hard |
|---|---:|---|
| behaviour-described, not named | 15 | the query shares no token with the file or symbol name |
| cross-file / "how does X work" | 12 | the answer spans call sites, not one chunk |
| PHP (WordPress plugin + theme) | 12 | new corpus; hooks/filters indirection |
| Python | 10 | behaviour-led, not filename-led |
| JS | 8 | behaviour-led |
| WP templates + HTML | 6 | markup with logic embedded |
| test ↔ implementation linkage | 5 | asymmetric naming |
| no-answer negatives | 8 | must return nothing, not a plausible wrong chunk |

A separate ~15-question dev split tunes τ. The frozen set is never used for training or selection.

**Reuse, do not rebuild.** The query-file format (`.embed-tmp/eval/queries-*.json`) already works and
`xyz eval` already computes MRR@D / R@k / miss@D with chunk-id-preserving rankings. `xyz/eval/metrics.py`
is the **canonical** scorer; `.embed-tmp/eval/score_retrieval.py` and `ask_self_eval.py` should call it
rather than reimplement the metrics — three implementations exist today and that is two too many.

Metrics: file- and symbol-level Recall@5/@10, MRR@10, nDCG@10, no-answer precision, latency p50/p95.
Indexing throughput and index size are already emitted by `xyz ingest`; no new instrumentation.
Bootstrap confidence intervals; no winner declared inside overlapping CIs.

**Dropped:** end-to-end agent context success rate (top-5 chunks fed to a coding agent, downstream
pass rate). That is an agent-in-the-loop evaluation system — its own non-determinism, cost and
flakiness — built to referee a difference the direct metrics cannot yet measure. Revisit only if two
candidates tie on the harder set.

**QA gate:** every question hand-verified; **at least one arm scores below R@3 = 1.000** (proof the
set actually discriminates — a set that saturates again has failed its purpose); the PHP repos are
indexed and their gold paths resolve; the harness runs unattended and emits one scorecard.

## Phase 3 — Model bake-off

> **Rescoped 2026-09-07.** CodeRankEmbed already clears this phase's own decision rule by ~20 points
> (measured R@10 = 1.000, MRR = 0.9444 against a bar of 0.80 / 0.70). The bake-off's job is therefore
> **to try to break that result on a harder set**, not to survey the field.

1. Apple-Silicon smoke gate for any `trust_remote_code` model: one-batch encode and a save/reload
   round-trip. (The training-step check is dropped — nothing is trained unless Phase 4 re-opens.)
2. Run **CodeRankEmbed vs one challenger** on the Phase 2 frozen set using the existing N-arm scorer
   (`score_retrieval.py`, GH-6 — already supports per-arm `--model`/`--backend` and was verified
   against the Run 9 baseline). Pick the challenger for the weakness the harder set exposes — a
   code-aware reranker if reranking is the gap, a different base if PHP is.
3. **Decision rule (unchanged):** file-level Recall@10 ≥ 0.80 AND MRR@10 ≥ 0.70 on the Python, JS and
   PHP slices → adopt as-is, invest in chunking + reranking, **skip Phase 4**.

**Dropped:** the four-model matrix, the five controls, and the CoIR public-suite regression. This
doc's own evidence appendices record that public CSN/CoIR numbers are leakage-inflated upper bounds
and that *"the frozen benchmark is the only number that decides anything"* — so the CoIR arm decides
nothing by our own reasoning.

**QA gate:** scorecard published into this doc; winner declared only outside overlapping CIs;
decision + rationale recorded.

## Phase 4 — Conditional fine-tuning — DEFERRED

> **Deferred 2026-09-07 by Phase 3's own rule.** The rule says *"adopt as-is … skip Phase 4"* when
> R@10 ≥ 0.80 and MRR@10 ≥ 0.70. CodeRankEmbed measured **1.000** and **0.9444**. The rule has fired.

Stated honestly against itself: those numbers come from a saturated set and are an upper bound, so a
harder set could still drop the model below the bar. That is a reason to **defer**, not to build now
— nothing about LoRA gets cheaper by starting early, and the whole phase is wasted if the rule holds.

**Re-open condition (the only one):** the Phase 2 frozen set drops CodeRankEmbed below file-level
R@10 0.80 or MRR@10 0.70 on the Python, JS or PHP slices. If that happens, the original plan applies
— mine own-repo triplets, dedup against the benchmark repos at function level, LoRA on the winning
code-capable base (never BGE-small), re-run the frozen benchmark. Distillation stays a last-resort
footprint play.

**QA gate (if re-opened):** fine-tuned model beats its own base outside CIs; no benchmark query or
gold chunk appears in training data.

## Phase 5 — Ask-Self absorption (was: sunset and migration)

> **Inverted 2026-09-07** on the operator's recalibration (reuse/adapt over rebuild) and a full
> module inventory of `ask-self@origin/main` (`461574f`). The previous plan moved five subsystems
> *into* XYZ. That was backwards.

**Ask-Self already is the application.** It has the CLI (`ask_self_cli.py`, `bin/ask-self`), the HTTP
boundary (`rag_agent.py`), harness config, multi-repo registry, synthesis, citations, revision
history, PR ingestion, an architecture summariser, an eval harness, events and a dashboard — roughly
**7,700 lines that are already provider-agnostic**. Three inventory facts settle the direction:

1. **Synthesis is already pluggable.** `synthesize()` (`ask_self_query.py:1449`) dispatches on
   `settings["provider"]` to four sibling generators — Gemini (`:759`), Ollama (`:808`),
   OpenAI-compatible (`:859`), Cloudflare (`:918`). Gemini is the default, not privileged. There is
   nothing to port.
2. **Citations are pure post-processing** (`ask_self_query.py:1673-1685`) — built from retrieval hits,
   deduped, capped at 8, no model involved.
3. **`ask_self_eval.py` already takes a pluggable retriever** — `Retriever = Callable[[str], list[str]]`
   (`:166`), so XYZ can be scored by Ask-Self's existing harness by passing one function.

**What XYZ actually adds** — and all Act 1 was right to build: Tree-sitter chunking (Ask-Self's
`ask_self_helpers.py` chunkers are regex/line-based — no parse tree, no nested-symbol boundaries),
FTS5 + RRF + rerank retrieval, and local/offline embedding at $0 per query.

**So the swap surface is two functions, not five subsystems:**

1. **Ingest side** — `embed_one` / `embed_batch` (`ask_self_ingest.py:426`, `:502`) call XYZ's local
   embedder instead of the Gemini/Cloudflare HTTP path.
2. **Query side** — `knn_search` (`ask_self_query.py:1199`) calls XYZ's `Retriever` instead of
   pure vector KNN plus a 0.02 priority boost.

Everything else stays where it is and keeps working. Then:

3. Fix the corpus/classification config so Ask-Self's chunker dispatch defers to XYZ's chunkers; the
   engine-independent half of `ask_self_harness.json` (paths, corpus filters, classification rules)
   is reused as-is.
4. Point `/ask_self` and `/reingest` at the swapped path — the entry points do not change, only what
   they call.
5. Retire the duplicate scorers: `ask_self_eval.py` and `score_retrieval.py` call
   `xyz/eval/metrics.py` rather than reimplement it.

**Correction to issue #11 (verified 2026-09-07).** It states that `fetchMergedPRs` and
`buildArchitectureSummary` must be *"ported into Python before deletion"*. Both are wrong:
`fetch_merged_prs` already exists in Python (`ask_self_ingest.py:827-873`, consumed at `:1384` and
`:1495`, configured by `ask_self_harness.json:22-30`), and `buildArchitectureSummary` does not exist
in the repo at all — there is no Node ingest path, `ask_self_query.mjs` being query-only, while
`ask_self_architecture.py` (1,131 lines) already writes `ARCHITECTURE.md` with an `ast` symbol index
and a deterministic non-LLM fallback. **These stated blockers are already cleared.**

**QA gate:** every repo formerly served by Ask-Self answers its smoke queries through the swapped
path at equal-or-better Recall@10, scored by `ask_self_eval.py` against both the old and new
retriever; no second index, no second synthesis path, no second scorer introduced.

## Open questions and risks

- CoRNStack's license conflict (unstated on HF card vs Apache 2.0 in the Hyperagent report) —
  verify before it enters any training run.
- NightOwl models are single-author, low-download; only 8% zero-shot (in-domain trained on
  CoIR/MTEB-Code train splits) — treat headline numbers as upper bounds.
- Qwen3-Embedding-0.6B mined NightOwl's hard negatives — overlapping bias if both are compared.
- All CSN/CoIR public numbers are leakage-inflated upper bounds; the frozen benchmark is the
  only number that decides anything.
- TypeScript has no public qrel coverage (absent from CSN/The Vault/CoIR) — the private
  benchmark's JS/TS slice carries that weight alone.
- Whether repo-specific fine-tuning is needed at all is deliberately left open; both sources
  frame it as conditional, not planned.
