---
title: BGE Small vs Code-Capable Embeddings — Decision Report
status: reference
created: 2026-08-28
updated: 2026-08-28
owner: Noel Saw
goal: Evidence appendix (Perplexity) for the v0.5 canonical research and build doc.
roadmap_exempt: true
---

## Status

| What was just completed | What's next |
|---|---|
| Frozen as an evidence appendix to the v0.5 canonical research and build doc (2026-08-28). | None — reference doc; execution lives in the canonical doc. |

# BGE Small vs. Code-Capable Embeddings for Private-Repo Code RAG on Apple Silicon

**Prepared:** 2026-08-28 · **Audience:** Noel Saw (Neochrome) · **Goal:** decide whether to fine-tune `BAAI/bge-small-en-v1.5` locally for semantic retrieval over private repos (Python, JS/TS, PHP, HTML/templates, Markdown/tests/config/routes/API schemas), or adopt a better starting point.

All factual claims are cited to a primary source fetched during this research session (Hugging Face model/dataset cards, GitHub repos, papers, or official docs). Full per-row evidence lives in three companion files: `research_models.md`, `research_datasets.md`, `research_training.md`.

---

## 1. Bottom line up front

1. **Do not fine-tune `bge-small-en-v1.5` for code.** There is no credibly evaluated code-search fine-tune of it anywhere on Hugging Face, and BGE Small is structurally wrong for code: a 33.4M-param English-text BERT with a 512-token window and an **uncased, non-code `bert-base-uncased` tokenizer** (30,522 tokens) that cannot faithfully encode identifiers like `getUserById`, `$wpdb`, or `__init__` ([BGE-small card](https://huggingface.co/BAAI/bge-small-en-v1.5), [config.json](https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/config.json)).
2. **A same-footprint, code-native replacement exists:** [`Shuu12121/NightOwl-CodeEmbedding-35M`](https://huggingface.co/Shuu12121/NightOwl-CodeEmbedding-35M) — 34.1M params, 384 dims, ~130 MiB FP32, 1,024-token context, a custom 50,368-token code BPE, 15 mined hard negatives per anchor, Apache-2.0, with a full MTEB(Code) sweep and per-language CodeSearchNet numbers (Python 0.893, PHP 0.868, JS 0.772).
3. **Benchmark before you train.** Your control group already includes BM25 and hybrid+rerank. Add NightOwl-35M and CodeRankEmbed to that group. Most "fine-tuning needed" conclusions in this space are artifacts of benchmark leakage ([Allamanis 2019](https://arxiv.org/abs/1812.06469), [Hernández López 2024](https://arxiv.org/abs/2401.07930)) — establish your real baseline first.
4. **HTML/templates/config/schemas are a genuine gap** for every code embedding model surveyed. Plan a separate lexical (BM25) lane for those file types, and add [`jinaai/jina-embeddings-v2-base-code`](https://huggingface.co/jinaai/jina-embeddings-v2-base-code) as the best dense model to *test* for them (it is the only one whose declared language list includes HTML/CSS/Markdown/Shell/Dockerfile) — but note this is a coverage claim, not evidence that Blade/Twig/Jinja/server-rendered template retrieval actually works; validate it on your own template slice before relying on it.
5. **Recommendation: (e) skip BGE Small**, adopt a code-capable model as the dense lane, and only then fine-tune on your own repo-derived pairs — on top of the code-capable base, not BGE Small — using Sentence Transformers `MultipleNegativesRankingLoss` + `mine_hard_negatives()` + `InformationRetrievalEvaluator` on an Apple Silicon MPS device.

---

## 2. The central question — do usable BGE-small code checkpoints exist?

**No.** A query of the Hugging Face model index for every checkpoint declaring `base_model:finetune:BAAI/bge-small-en-v1.5` returns **383 models, of which exactly two are code-related, and both fail the evidence bar** ([HF models API, filtered](https://huggingface.co/api/models?filter=base_model:finetune:BAAI/bge-small-en-v1.5&limit=1000)):

| Candidate | Why it fails |
|---|---|
| [Matthieufromparis/bge-small-code-search-v1](https://huggingface.co/Matthieufromparis/bge-small-code-search-v1) | Trained on only 6,000 CodeSearchNet-Python pairs; reports NDCG@10 0.9761→0.9849 on 500 self-built held-out pairs. A 0.976 base score is implausibly high for real code search — a saturated, single-language, self-run eval, not a benchmark. |
| [ArnavKewalram/bge-small-code-v1](https://huggingface.co/ArnavKewalram/bge-small-code-v1) | **No license declared.** Card describes an "Unnamed Dataset" of 200k triples and an `InformationRetrievalEvaluator` on a `cornstack_eval` split, but **publishes no evaluation numbers**. Excluded per your rules. |

**BAAI never shipped a small BGE code model.** `BAAI/bge-code-v1` is a 1.54B-param `Qwen2Model` (Qwen2.5-Coder class), not a BGE-small derivative ([config.json](https://huggingface.co/BAAI/bge-code-v1/resolve/main/config.json)). The only BGE-derived code fine-tune reporting a recognized benchmark is [jamie8johnson/bge-large-v1.5-code-search](https://huggingface.co/jamie8johnson/bge-large-v1.5-code-search) (LoRA, Apache-2.0) at CoIR 57.5 vs 55.7 base — but single-author, self-run evals, no paper, and it is BGE-large, not small.

**Why fine-tuning cannot rescue BGE-small for code:** the uncased 30,522-token `bert-base-uncased` vocabulary is the binding constraint — fine-tuning changes weights, not the tokenizer's inability to preserve case-sensitive symbols and identifiers ([BGE-small card](https://huggingface.co/BAAI/bge-small-en-v1.5)). The 512-token window also truncates most real files and templates.

---

## 3. Shortlist — candidates to benchmark against your control group

Your fixed control group: (1) untuned `BAAI/bge-small-en-v1.5`, (2) your current local Qwen embedding model, (3) SQLite FTS5/BM25, (4) hybrid lexical+dense via reciprocal-rank fusion, (5) a reranker over top 25–100. Add these five candidates (≤5 per your spec):

| # | Model | Link | Base / arch | Params | Emb. dim | Max seq len | Languages (data/eval) | Training data / provenance | Objective | Hard neg? | Eval benchmark & results | License | Last update | Mac / Apple Silicon | Suitability (a exact-symbol / b NL→code / c "how does it work?" / d cross-file/cross-lang) | Risks & limits | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | **NightOwl-CodeEmbedding-35M** | [card](https://huggingface.co/Shuu12121/NightOwl-CodeEmbedding-35M) | ModernBERT, 10 layers, hidden 384, custom 50,368 code BPE | 34.1M | 384 | 1,024 | Python, JS, PHP, Go, Java, Ruby, C, C++, Rust, + unseen langs in CodeEditSearch | Docstring↔code + mined hard negatives; Stack-derived; explicit decontamination vs CSN test | InfoNCE / in-batch + mined | **Yes, 15/anchor** | MTEB(Code,v1) macro 0.656; CSN 0.862 (Py 0.893, PHP 0.868, JS 0.772); SO-QA 0.811 | Apache-2.0 | 2026-08-01 | **Best-in-class for local**: card targets CPU/edge; FP32 130 MiB; ST-loadable. No MLX/ONNX statement | a: mod-good (code BPE) / b: strong for size / c: mod (1024 cap) / d: mod (CodeEditSearch 0.680, 13 langs) | Trained on CoIR/MTEB-Code training splits → only 8% zero-shot (card admits in-domain). JS weakest CSN lang. No HTML/template. Single author, low downloads | **High** |
| S2 | **nomic-ai/CodeRankEmbed** | [card](https://huggingface.co/nomic-ai/CodeRankEmbed) | NomicBert bi-encoder, init from snowflake-arctic-embed-m-long | 136.7M | 768 | 8,192 | Python, JS, PHP, Go, Java, Ruby (+ CSN 6 langs) | CoRNStack: 21M (text,code) pairs from deduped Stack v2, consistency-filtered, curriculum hard negatives | InfoNCE contrastive | **Yes (curriculum)** | CSN MRR 77.9; CoIR NDCG@10 60.1; SWE-Bench-Lite localization | MIT | 2025-06-24 | Good: ST (`trust_remote_code`), community ONNX/int8 ports (~547 MB fp32). 8k ctx is the differentiator | a: mod / b: strong / c: **good** (8k spans whole files) / d: good | Training code unreleased; CoRNStack is CSN-adjacent (Stack v2 docstrings) → CSN scores optimistic. 6 langs, **no HTML/template**. Needs `trust_remote_code` | **High** |
| S3 | **codesage/codesage-small-v2** | [card](https://huggingface.co/codesage/codesage-small-v2) | CodeSage encoder, 6 layers, StarCoder tokenizer | 130M | 1,024 (+ MRL) | 2,048 (config) | Python, JS, TS, PHP, Go, Java, Ruby, C, C++ | The Stack → The Stack V2 with consistency filtering | Contrastive (NL2Code + code-code) | n.a. | NL2Code avg 0.644; **per-language: PHP 0.602, JS 0.658, Python 0.688, + TS** | Apache-2.0 | 2024-12-28 | Good: ST-loadable (`trust_remote_code`), MRL truncation. No MLX/ONNX | a: mod (StarCoder tokenizer code-aware) / b: good / c: mod / d: mod (2048) | Card omits max-len & license detail; Stack v2 provenance = public-repo overlap; 9 langs, no HTML/template; low download volume | **High** |
| S4 | **jina-embeddings-v2-base-code** | [card](https://huggingface.co/jinaai/jina-embeddings-v2-base-code) | JinaBERT (BERT + symmetric bidirectional ALiBi) | 161M | 768 | 8,192 (trained 512, ALiBi extrapolates) | **HTML, CSS, Markdown, Shell, Dockerfile, SQL, PHP, TS, JS, Python, Go, Java, C, C++, +** | 150M-pair corpus (publicly unitemized); JinaBERT backbone | Contrastive (code↔text) | n.a. | No eval on its own card; third-party CoIR 58.4, CSN avg 0.648 (PHP 0.570, JS 0.630) | Apache-2.0 | 2025-01-06 | Good: ST (`trust_remote_code`), Transformers.js 8-bit, GGUF; 8k ctx | a: mod / b: moderate (mid-pack) / c: mod / d: **good** — only model covering HTML/templates | **No eval on its card**; weakest CSN-PHP/JS among specialists; older generation; training set unitemized | **Medium-high** |
| S5 | **Qwen3-Embedding-0.6B** (Apache-2.0 stand-in for non-commercial jina-code-0.5b) | [card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) | Qwen3ForCausalLM from Qwen3-0.6B-Base, 28 layers, instruction-aware, MRL | 596M | up to 1,024 (32–1024 selectable) | 32,768 | Multilingual; used as the hard-neg miner by NightOwl | n.a. on card (discloses no training data/objective) | Instruction-tuned contrastive | n.a. | Third-party MTEB-Code 74.69% (vs 78.72% for jina-code-0.5b); MTEB retrieval 64.64 | Apache-2.0 | 2026-04-20 | **Strong**: mature MLX ecosystem (`mlx-community/Qwen3-Embedding-0.6B-4bit` 13k+ downloads); ~1.19 GB bf16 | a: mod / b: good (below specialists) / c: good / d: **strong** (32k ctx, MRL) | Card discloses no training data/objective; no code benchmark of its own; used by NightOwl as miner (overlapping bias); larger vectors/latency | **High** availability, **medium** code-specific quality |

> **Qwen note:** if your "current local Qwen embedding model" is already `Qwen3-Embedding-0.6B`, treat S5 as the existing control (do not double-count it) and substitute `Shuu12121/NightOwl-CodeEmbedding` (150.8M, macro 0.709, Apache-2.0) as the fifth new candidate.
>
> **License note:** the best sub-1B code retriever measured anywhere in the survey is [`jinaai/jina-code-embeddings-0.5b`](https://huggingface.co/jinaai/jina-code-embeddings-0.5b) (MTEB-Code 78.72%, CoIR 73.94, 32k ctx, official [MLX port](https://huggingface.co/jinaai/jina-code-embeddings-0.5b-mlx) with Metal acceleration) — but it is **CC-BY-NC-4.0 (non-commercial)**, which disqualifies it for commercial private-repo use. Qwen3-Embedding-0.6B is the closest licensable substitute and is also a useful stand-in for your "current local Qwen embedding model" control.

### Why these five

- **S1 NightOwl-35M** is the direct drop-in replacement for BGE-small at the same footprint, with real code-retrieval evidence and an honestly self-disclosed 8% zero-shot fraction — the strongest signal of credible evaluation in the entire set.
- **S2 CodeRankEmbed** adds an 8,192-token window, which is the key differentiator for "how does this work?" and cross-file queries that every 512/1,024-token model truncates.
- **S3 CodeSage-small-v2** is the only compact model publishing per-language NL2Code numbers that include PHP and TypeScript.
- **S4 jina-v2-base-code** is the only model covering HTML/templates/config/schemas — the explicit gap in your corpus.
- **S5 Qwen3-0.6B** is your Apache-2.0 licensable sub-1B option with a mature MLX/Apple-Silicon story, and stands in for your existing Qwen control.

---

## 4. Datasets — what to fine-tune and evaluate on

### Training data (ranked)

| Dataset | Link | Source / build | Languages | Example types | Size | License | Leakage risk | Role |
|---|---|---|---|---|---|---|---|---|
| **The Vault (function)** | [card](https://huggingface.co/datasets/Fsoft-AIC/the-vault-function) | Extracted from The Stack, deduplicated before splitting; 11 docstring styles | Python, Java, JS, PHP, C, C#, C++, Go, Ruby, Rust (no TS/HTML) | code↔docstring | 34.1M pairs (PHP 4.7M, JS 1.68M, Py 7.8M) | MIT | High (Stack-derived; overlaps CSN/public GitHub) | Best scale + permissive license + PHP |
| **CoRNStack** | [card](https://huggingface.co/datasets/nomic-ai/cornstack-python-v1), [ICLR 2025](https://openreview.net/forum?id=iyJOUELYir) | Deduped Stack v2; dual-consistency filtering; curriculum hard negatives | Python (this shard; "multiple langs" overall) | `<query, positive, negatives>` triplets | 21M (est.) | n.a. on card | High (Stack v2) | Ready-made hard negatives — the highest-quality training pipeline found |
| **SWELocMulti / SweRank+** | [paper](https://web3.arxiv.org/pdf/2512.20482) | GitHub PRs linked to issues, ≥40% target-lang, consistency-filtered; InfoNCE training | JS, Java, TS, Ruby, Rust, Go, **PHP (16,608 instances)**, C, C++, Python (no HTML) | issue↔modified function | 155,663 (4,060 repos) | n.a. | Medium (repo-level train/eval overlap not stated) | Only issue→code training signal incl. PHP — matches real bug-report searches |
| **CodeXGLUE Code-to-Text** | [card](https://huggingface.co/datasets/google/code_x_glue_ct_code_to_text) | CodeSearchNet filtered (parseable, doc 3–256 tokens, English) | Go, Java, JS, PHP, Python, Ruby (no TS/HTML) | code↔docstring | 1.0M (PHP 241k train) | C-UDA | High (direct CSN derivative) | Standard warm-start |
| **CommitPackFT** | [card](https://huggingface.co/datasets/bigcode/commitpackft) | NL-instruction(commit subject)↔code-edit pairs from permissive GitHub | 277 langs incl. **php (24,791), html (20,214), html+erb (10,910), html+django, html+php, TS, JS, Python** | instruction↔code edit | 702,062 (1.58 GB) | per-sample permissive | High (public GitHub) | **Only realistic HTML/template + rich PHP signal** — reformat commit subjects into queries |

Supplement query realism with [CoSQA](https://github.com/Jun-jie-Huang/CoCLR) (19,604 human-labeled Python query↔code, CUDA license) and [StaQC](https://github.com/LittleYUYU/StackOverflow-Question-Code-Dataset) (147,546 real SO question↔Python-code, CC BY 4.0) to shift from docstring-style to real user phrasing.

### Evaluation benchmarks (ranked)

| Benchmark | Link | What it gives | qrels? | Metrics | Languages | Caveat |
|---|---|---|---|---|---|---|
| **CoIR** | [paper](https://arxiv.org/html/2407.02883v3), [repo](https://github.com/CoIR-team/coir), [leaderboard](https://archersama.github.io/coir/) | 10 code datasets, 2M+ docs, BEIR/MTEB schema | Yes (e.g. [cosqa qrels](https://huggingface.co/datasets/CoIR-Retrieval/cosqa)) | nDCG@10 | 14 langs incl. Python, JS, PHP, **HTML (CodeFeedback-ST)**; no TS | Most subsets = 1 relevant doc/query; CSN-contaminated → use as fast regression only |
| **CORE-Bench** (2026) | [paper](https://arxiv.org/html/2606.11864v1) | 180K+ queries, 823k/52k/106k qrels across 3 levels; multi-positive (10–41 rel/query); L3 = broader-context retrieval (docs/tests/config/call sites) | Yes (most explicit of any resource) | per-level, per-language | 11 langs incl. PHP, TS, JS, Python (no HTML) | L1 embeds CSN/CoSQA; L2/L3 use widely-memorized SWE-bench repos → still upper-bound |
| **CodeRAG-Bench** | [repo](https://github.com/code-rag-bench/code-rag-bench) | BEIR-format `corpus.jsonl`/`queries.jsonl`/`qrel/test.tsv` + execution-based end-to-end | Yes | NDCG/MRR/Recall/Precision @1–1000 | retrieval pool incl. Python, JS, TS, PHP, HTML | No license; unmaintained since Nov 2024; Java/Pyserini needed only for BM25 |

Add [Loc-Bench_V1](https://huggingface.co/datasets/czlll/Loc-Bench_V1/blob/main/README.md) (560 issue→function tests) and [CoREB](https://arxiv.org/html/2605.04615v2) (counterfactually rewritten, contamination-resistant) for leakage-resistant sanity checks.

### Hard constraints

- **HTML/templates: no labeled retrieval benchmark exists in anything fetched.** Only CoIR's CodeFeedback-ST language list includes HTML with qrels. If HTML/template retrieval matters, you must build your own eval set — raw material: [CommitPack html splits](https://huggingface.co/datasets/bigcode/commitpack), [The Stack `html`](https://huggingface.co/datasets/bigcode/the-stack), [code-rag-bench/github-repos](https://huggingface.co/datasets/code-rag-bench/github-repos).
- **PHP:** training data is plentiful (The Vault, CommitPack, CodeXGLUE CSN, SWELocMulti); PHP *evaluation* with qrels exists essentially only in CORE-Bench L2/L3 and SWE-Bench-Multilingual localization.
- **TypeScript:** absent from CodeSearchNet, The Vault, CoIR; available via The Stack, CommitPack, CommitChronicle, CORE-Bench, SWELocMulti.
- **Leakage is systemic:** CodeSearchNet is simultaneously the training corpus and the substrate for AdvTest, WebQueryTest, CoSQA+, CoIR CSN/CSN-CCR, and CORE-Bench L1. Dedup your training data against eval corpora at function level before trusting any headline number ([Allamanis 2019](https://arxiv.org/abs/1812.06469): up to 100% metric inflation; [Hernández López 2024](https://arxiv.org/abs/2401.07930): inter-dataset CSN leakage).

---

## 5. Training pipelines

| Stack / repo | Link | Framework | MNRL/InfoNCE? | Hard-neg mining? | Retrieval eval? | Reproducibility | Mac/Apple Silicon | License | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| **Sentence Transformers** (trainer + losses + miner + evaluator) | [repo](https://github.com/UKPLab/sentence-transformers), [losses](https://sbert.net/docs/package_reference/sentence_transformer/losses.html), [miner](https://sbert.net/docs/package_reference/util/hard_negatives.html), [eval](https://sbert.net/docs/package_reference/sentence_transformer/evaluation.html), [model](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html) | ST + PyTorch 2.2+ + HF datasets | **Yes** — MNRL = "InfoNCE / SimCSE / in-batch negatives" with `hardness_mode` | **Yes** — `mine_hard_negatives()` (range, margins, CrossEncoder rescoring, triplet/n-tuple output) | **Yes** — `InformationRetrievalEvaluator`: MRR, Recall@k, NDCG, MAP@k, precision@k; `NanoBEIREvaluator` | Yes — runnable end-to-end; local CSV/JSON or HF datasets | **`device="mps"`** supported | Apache-2.0 | **High** — only stack with all four pieces in one framework |
| ST PEFT/LoRA on encoder | [example](https://sbert.net/examples/sentence_transformer/training/peft/README.html) | ST + PEFT | Yes (MNRL) | No | Partly (NanoBEIR NDCG@10: PEFT 0.4705 vs full 0.4728) | Medium — runnable `add_adapter`/`load_adapter`; script filename not on page; no hard-neg mining in recipe | fp32 recommended; adapter = 9.44 MB = 2.14% of base | Apache-2.0 | High that encoder-LoRA works in ST; **low** that a code-retrieval LoRA recipe exists |
| FlagEmbedding (BAAI) | [repo](https://github.com/FlagOpen/FlagEmbedding), [embedder README](https://github.com/FlagOpen/FlagEmbedding/tree/master/examples/finetune/embedder) | FlagEmbedding + PyTorch + DeepSpeed + optional faiss | Loss names not stated on pages; kd `kl_div`/`m3_kd_loss` documented | **Yes** — `hn_mine.py` (`--range_for_sampling 2-200 --negative_number 15`); JSONL `{query,pos,neg,pos_scores,neg_scores,prompt,type}` | Yes (partial) — ndcg@10, recall@100 default; no MRR/MAP | Yes — `FlagEmbedding.finetune.embedder.encoder_only.base` trainer | n.a. (no macOS docs; CUDA/DeepSpeed-shaped) | MIT | Medium — use for the hard-neg mining + data contract even if you train with ST |
| CoIR | [repo](https://github.com/CoIR-team/coir) | BEIR/MTEB-based eval | No (eval only) | No | Yes — 10 code datasets, BEIR schema | Eval-only but runnable | n.a. (no GPU notes; `.to(device)`) | Apache-2.0 | High for eval scope |
| CodeRAG-Bench | [repo](https://github.com/code-rag-bench/code-rag-bench) | Pyserini (BM25) + ST (dense) | No (retrieval+gen eval) | No | **Yes** — NDCG/MRR/Recall/Precision @1–1000; BEIR format | Yes for retrieval eval | n.a. (needs OpenJDK 11 + Maven for BM25) | n.a. (null) | High for eval, medium overall |

**Key pipeline finding:** Sentence Transformers is the only stack where `MultipleNegativesRankingLoss` (explicitly the InfoNCE loss), `mine_hard_negatives()`, `InformationRetrievalEvaluator` (MRR/Recall@k/NDCG/MAP), and `device="mps"` are all documented together. Use `CachedMultipleNegativesRankingLoss` (GradCache) with a small `mini_batch_size` to get large effective batches within unified memory on the Mac. **Honest gap:** the one concrete LoRA-on-an-encoder example is on GooAQ (QA), not code, and has no hard-negative mining — so a code-retrieval LoRA recipe must be assembled, not downloaded.

### Apple Silicon practicality

- MPS training is supported but beta: macOS 12.3+, `PYTORCH_ENABLE_MPS_FALLBACK=1` for unsupported ops, model must fit unified memory (no CPU offload via `device_map="auto"`), `bf16` needs macOS 14+, and the per-shape Metal graph cache can exhaust memory with padded/variable-length batches — mitigate with `torch_empty_cache_steps` and fixed-shape batching ([Transformers Apple Silicon guide](https://huggingface.co/docs/transformers/en/perf_train_special), [PyTorch MPS notes](https://docs.pytorch.org/docs/stable/notes/mps.html), [Apple Metal PyTorch](https://developer.apple.com/metal/pytorch/)).
- For inference, [`taylorai/mlx_embedding_models`](https://github.com/taylorai/mlx_embedding_models) runs `bge-small` and other embeddings on the Apple Silicon GPU (MIT) — **inference only, no training**.

---

## 6. Experiment plan

### 6.1 Frozen benchmark of 150–300 real developer questions

Build a private, repo-grounded benchmark from your own repositories (not public corpora — this is the only way to escape the systemic CSN/Stack leakage documented above). Target ~250 questions stratified across the slices below. For each question, hand-label the gold file(s) and, where applicable, the gold symbol(s)/function(s). Include a held-out "no answer in corpus" slice (~10–15%) to measure false-positive behavior.

**Benchmark hygiene:** the 250-question set is a *frozen test set* — it is never used for training, model selection, or threshold tuning. Carve a separate small dev split (~30 questions) for calibrating the no-answer confidence threshold, and report no-answer precision on the frozen test set using a threshold chosen only on dev.

### 6.2 Evaluation slices

| Slice | Target n | Example query shape | Notes |
|---|---|---|---|
| Python | 35 | "where do we parse the webhook payload?" | Dense models should shine here |
| JavaScript/TypeScript | 30 | "which hook manages form state" | TS is a known gap area |
| PHP | 30 | "which endpoint serves the order export" | PHP has training data but thin eval |
| HTML/templates | 20 | "which partial renders the product card" | **Expect this to be the weakest dense lane** — pair with BM25 |
| Cross-language | 25 | "which PHP endpoint provides the data used by this JS component" | Tests cross-file/cross-lang — depends on chunking + graph more than the base model |
| Exact identifiers | 20 | "`getUserById`", "`$wpdb`", "`OrderExporter::run`" | BM25 should win; dense models with uncased tokenizers (BGE-small) lose |
| Architecture | 20 | "how does auth middleware chain together" | Needs whole-file / multi-file context → favors 8k-context models (CodeRankEmbed, jina) |
| Test/code linkage | 20 | "which test covers the refund path" | Tests ↔ implementation retrieval |
| No answer in corpus | 25 | questions with no gold file | Measures precision / refusal behavior |

### 6.3 Metrics

| Metric | What it captures | Why |
|---|---|---|
| File-level Recall@5, Recall@10 | Did the right file surface in top-k? | Primary developer-facing metric |
| Symbol-level Recall@5, Recall@10 | Did the right function/class surface? | Finer-grained; dense models often find the file but miss the symbol |
| MRR@10 | First-relevant ranking quality | Standard IR metric, comparable to CoIR |
| nDCG@10 | Graded ranking quality | Robust to multi-relevant questions |
| No-answer precision | Fraction of "no answer" cases correctly returned empty / low-confidence | Critical for agent trust |
| Latency (p50/p95) | End-to-end retrieval time per query | Apple Silicon budget constraint |
| Index size | Disk/memory footprint of the vector index | 384-d vs 768/1024-d tradeoff |
| End-to-end agent-context success rate | Did the retrieved context let an LLM answer the developer question correctly? | The metric that actually matters for code RAG |

### 6.4 Protocol

0. **Apple Silicon smoke-test gate (required before any candidate is benchmarked):** run a one-batch encode and one training step on MPS for every model that requires `trust_remote_code` (CodeRankEmbed, CodeSage, jina, Qwen3). Some custom modeling code uses ops that MPS does not support; confirm `PYTORCH_ENABLE_MPS_FALLBACK=1` is set and that a train+save+reload round-trip succeeds before committing a candidate. This gate also applies to any fine-tuning of CodeRankEmbed — its training code is unreleased, so only fine-tune it after a smoke test confirms training/save/load works end-to-end.
1. **Chunking:** fixed strategy across all models — function/class-level chunks for code, heading-level for Markdown, file-level for small config/templates. Hold chunking constant so differences isolate the embedding model.
2. **Embed all candidates on the same MPS device:** S1–S5 above, plus the control group (untuned BGE-small, your current Qwen, BM25, hybrid RRF, reranker over top-100).
3. **Run all slices, compute all metrics.** Report per-slice, not just aggregate — aggregate CSN/CoIR numbers are unreliable upper bounds.
4. **Leakage hygiene:** dedup any public training data you use against your eval repos at function level before fine-tuning ([Allamanis 2019](https://arxiv.org/abs/1812.06469), [Hernández López 2024](https://arxiv.org/abs/2401.07930)).
5. **Statistical sanity:** with n≈250, use bootstrap confidence intervals; don't declare a winner inside overlapping CIs.

---

## 7. Recommendation

### Against your five options (a–e)

| Option | Verdict | Rationale |
|---|---|---|
| **(a) use an existing checkpoint as-is** | **Adopt for non-BGE checkpoints** | No usable BGE-small code checkpoint exists, but NightOwl-35M / CodeRankEmbed are credible as-is. Benchmark them first — you may not need to fine-tune at all. |
| **(b) fine-tune BGE Small from a public code dataset** | **Reject** | BGE-small's uncased 30,522-token vocab and 512-token window are the binding constraint; public datasets (CSN/The Vault) are leakage-saturated. Starting base is wrong. |
| **(c) fine-tune BGE Small using your own repo-derived pairs** | **Reject as framed; adapt** | Own-repo pairs are the right *data* (escape leakage, match your symbol/casing distribution), but fine-tuning *on BGE-small* leaves the tokenizer/512 ceiling. Fine-tune on top of a code-capable base instead. |
| **(d) use a larger public model as a teacher, distill into BGE Small** | **Reject** | Distillation (FlagEmbedding `m3_kd_loss`) is feasible, but the student is still BGE-small with its tokenizer/512 limit — the ceiling doesn't move, and you've added a non-commercial-licensed teacher risk. |
| **(e) skip BGE Small, adopt a more code-capable embedding model** | **Choose this** | Evidence-based: code-native tokenizers, published per-language retrieval scores, hard-negative training, and 8k+ context are all available at the same or modestly larger footprint. |

### Concrete plan

1. **Benchmark phase (no training):** run the control group + S1 (NightOwl-35M) + S2 (CodeRankEmbed) + S4 (jina-v2-base-code) on your frozen 250-question benchmark. Use [CoIR](https://github.com/CoIR-team/coir) subsets as a fast regression harness and [CodeRAG-Bench](https://github.com/code-rag-bench/code-rag-bench) for the BEIR-format local eval.
2. **If a code-capable base beats BGE-small + your Qwen control on NL→code slices** (likely): adopt it as the dense lane. For HTML/templates/config/schemas, keep a separate BM25 lane or use jina-v2-base-code (the only model covering those file types).
3. **Fine-tune only if the gap to your requirements is real** — and fine-tune *on top of the winning code base*, preferring **NightOwl-35M** (or its 150.8M sibling) as the ST-compatible encoder to fine-tune, since CodeRankEmbed's training code is unreleased. Use your own repo-derived (query, code) pairs with Sentence Transformers `MultipleNegativesRankingLoss` + `mine_hard_negatives()` + `InformationRetrievalEvaluator` on MPS, gated by the smoke test above. Supplement PHP with The Vault + CommitPackFT; supplement HTML/templates with CommitPackFT reformatted into query↔edit pairs.
4. **Keep BM25 + hybrid RRF + reranker in the stack regardless** — exact-symbol lookup is a lexical problem that dense models (especially uncased ones) do not solve, and hybrid+rerank is your safety net for cross-language and template queries.

### Decision rule for fine-tuning vs. as-is

- If NightOwl-35M or CodeRankEmbed already hits **file-level Recall@10 ≥ 0.80** and **MRR@10 ≥ 0.70** on your Python/JS/PHP slices → **(a) use as-is**, spend effort on chunking + reranking instead.
- If it trails meaningfully on PHP or cross-language slices → **(c-adapted) fine-tune on your own repo-derived pairs on top of the code-capable base.**
- Only if footprint is the absolute binding constraint and no code-capable model fits → fall back to **(d)** distillation, accepting the BGE-small tokenizer ceiling — but this is the weakest option and the evidence does not force you there.
