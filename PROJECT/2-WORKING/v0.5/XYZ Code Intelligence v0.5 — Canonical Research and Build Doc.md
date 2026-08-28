---
title: XYZ Code Intelligence v0.5 — Canonical Research and Build Doc
status: active
created: 2026-08-28
updated: 2026-08-28
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
  - Porting Ask-Self's synthesis/answer layer unchanged
---

# XYZ Code Intelligence v0.5 — Canonical Research and Build Doc

This document supersedes the five v0.5 research inputs (four Perplexity docs + the Hyperagent
report) as the single source of truth for what XYZ v0.5 builds. The research docs remain in this
folder as evidence appendices; per-claim citations live there.

## Status

| What was just completed | What's next |
|---|---|
| Synthesized Perplexity + Hyperagent research into this canonical doc (2026-08-28). | Phase 1: stand up AST/Tree-sitter chunking + hybrid retrieval skeleton. |

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
- [Phase 4 — Conditional fine-tuning](#phase-4--conditional-fine-tuning)
- [Phase 5 — Ask-Self sunset and migration](#phase-5--ask-self-sunset-and-migration)
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

250 hand-annotated real developer questions from own private repos, gold-labeled at file and
symbol level, frozen before any model selection. Slices: exact symbol lookup 30, Python 30,
JS/TS 30, PHP 30, HTML/Blade/Twig templates 25, cross-language PHP↔JS/TS bridging 30,
architecture/"how does X work" 30, test↔implementation linkage 25, no-answer negatives 20.
Separate ~30-question dev split tunes the no-answer threshold τ; the frozen set is never used
for training or selection.

Metrics: file-level and symbol-level Recall@5/@10, MRR@10, nDCG@10, no-answer precision,
latency p50/p95, indexing throughput (chunks/sec), index size on disk, and end-to-end agent
context success rate (top-5 chunks fed to a coding agent, downstream pass rate). Bootstrap
confidence intervals; no winner declared inside overlapping CIs.

**QA gate:** all 250 queries have hand-verified gold labels; slice counts match; benchmark
harness runs the full matrix unattended and emits one scorecard.

## Phase 3 — Model bake-off

1. Apple Silicon smoke-test gate first for every `trust_remote_code` model: one-batch encode,
   one training step, save/reload round-trip on MPS.
2. Run candidates (CodeRankEmbed, NightOwl-35M, jina-v2-base-code on the template slice,
   optionally CodeSage-small-v2) against the five controls on the frozen benchmark; CoIR subset
   as public regression.
3. **Decision rule:** if a candidate hits file-level Recall@10 ≥ 0.80 AND MRR@10 ≥ 0.70 on the
   Python, JS/TS, and PHP slices → adopt as-is and invest in chunking + reranking; skip Phase 4.
   If it trails on PHP or cross-language slices → proceed to Phase 4 on the code-capable base
   (never on BGE-small).

**QA gate:** scorecard published into this doc (memory-injection rule); winner declared only
outside overlapping CIs; decision + rationale recorded.

## Phase 4 — Conditional fine-tuning

Only if the Phase 3 rule fails. Mine own-repo triplets, supplement per the datasets section,
dedup against the benchmark repos at function level, train LoRA on the winning base with the
pipeline above, re-run the frozen benchmark. Distillation into a smaller student is the
last-resort footprint play only.

**QA gate:** fine-tuned model beats its own base on the frozen benchmark outside CIs; no
benchmark query (or its gold chunk) appears in training data.

## Phase 5 — Ask-Self sunset and migration

1. Port the surviving Ask-Self harness configs to XYZ format for the repos that use them.
2. Replace the `/ask_self` and `/reingest` skill entry points with XYZ equivalents.
3. Archive the Ask-Self repo: README banner pointing here, final tag, stop indexing.
4. Delete stale global state (`ASK_SELF_PATH` export, copied slash commands).

**QA gate:** every repo formerly served by Ask-Self answers its smoke queries through XYZ at
equal-or-better Recall@10; Ask-Self archived with pointer.

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
