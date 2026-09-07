# Run — Act 1 hybrid retrieval round-trip

- **Date:** 2026-09-06
- **Commit:** `fa1812d` (PR #15, merged 2026-09-07)
- **What was measured:** the four retrieval modes of the new `xyz` package, end to end on a real corpus
- **Status:** immutable — see `../README.md` rule 1

## Settings used

Baseline as of this run, with the overrides noted:

| knob | value | note |
|---|---|---|
| model | `nomic-ai/CodeRankEmbed`, 768d, `max_seq_length` 2048 | |
| device | **CPU** | override — MPS unavailable in the managed runtime, `XYZ_DEVICE=cpu` pinned explicitly |
| reranker | `mixedbread-ai/mxbai-rerank-xsmall-v1` | |
| chunking | Tree-sitter, path-prefixed, 6,000-char split | |
| RRF `k` | 60 | |
| depth `D` | 100 | `fetch_k=100` per lane |
| τ | unset | |
| query set | `.embed-tmp/eval/queries-LTVera-Pandas.json`, 30 queries | |

## Corpus

**subset** — one root-preserving invocation restricted to `scripts/`, `app/`, `alembic/` of
LTVera-Pandas. Every gold path verified present in `chunks.path` before scoring.

- 339 files / **3,020 chunks**
- Full-corpus attempt aborted at 204 chunks: the required early ETA reported **206.5 min**, above the
  45-minute fallback threshold. Full corpus projected at 1,793 files / 17,258 chunks.

## Ingest

| | wall | files | chunks written | chunks embedded | peak RSS |
|---|---:|---:|---:|---:|---:|
| first | 1,664.72 s (27m 45s) | 339 seen | 3,020 | 3,020 | 9,852.62 MB |
| second, unchanged | **8.62 s** | 339 skipped | 0 | **0** | — |

## Retrieval quality — MRR@100 / R@k / miss@100

| mode | MRR@100 | R@1 | R@3 | R@5 | R@10 | miss@100 |
|---|---:|---:|---:|---:|---:|---:|
| **dense** | **0.9444** | **0.9000** | 1.0000 | 1.0000 | 1.0000 | 0 |
| BM25 | 0.8583 | 0.7667 | 0.9333 | 0.9667 | 0.9667 | 0 |
| hybrid | 0.9222 | 0.8667 | 0.9667 | 0.9667 | 1.0000 | 0 |
| hybrid+rerank | 0.9016 | 0.8667 | 0.9667 | 0.9667 | 0.9667 | 0 |

Reranker reordered **30/30** top-10 chunk-id sequences.

## Latency — ms, p50 / p95

| mode | embed query | BM25 | dense | fuse | rerank | total |
|---|---:|---:|---:|---:|---:|---:|
| dense | 81.28 / 119.48 | — | 3.12 / 4.65 | — | — | 86.42 / 125.35 |
| BM25 | — | 0.85 / 2.03 | — | — | — | 1.34 / 2.68 |
| hybrid | 73.68 / 91.92 | 0.73 / 1.89 | 3.10 / 3.82 | 0.12 / 0.16 | — | 78.70 / 96.23 |
| hybrid+rerank | 142.91 / 313.98 | 1.27 / 3.33 | 3.93 / 6.40 | 0.13 / 0.32 | **50,003.77 / 93,867.16** | 50,175.41 / 94,262.74 |

## The caveat that would overturn these numbers

**This set is saturated and these are upper bounds.** Dense scores R@3 = 1.000 — every query's gold
file is in the top 3 — so the set cannot rank the arms. The 0.0428 MRR gap between dense and
hybrid+rerank sits inside the 0.05 noise floor for n=30. **Nothing here establishes that any arm is
better than any other.** What it does establish is that all four run, end to end, on a real corpus.

Root cause of the saturation is known and measured: most queries are answerable from the filename
alone — prefixing chunks with their path moved MRR 0.80 → 0.98 (issue #8).

## What this run decided

- Reranker default changed to `mixedbread-ai/mxbai-rerank-xsmall-v1`: the previous choice,
  `cross-encoder/ms-marco-MiniLM-L-6-v2`, loads without error on torch 2.14 / transformers 5.16 and
  returns `[nan, nan]`. Reproduced with plain `AutoModelForSequenceClassification` under both `eager`
  and `sdpa`; checkpoint tensors all finite (old-format BERT checkpoint).
- Tree-sitter grammars must be pre-cached: `tree_sitter_language_pack` downloads them at first use,
  so offline runs fail without a warm cache.
- The frozen benchmark must be built for **difficulty**, not size — this run is the evidence for that.

## What this run did NOT decide

- Whether hybrid or reranking helps. Unresolvable on this set.
- Whether the `auto` default (which prefers `hybrid+rerank`) is right. It currently prefers the
  lowest-scoring, slowest arm.
- Anything about the PHP/WordPress corpus, which was not indexed for this run.

## Independent check

Final Codex QA (900 s cap): **VERDICT: PASS**, 6 pass / 1 nit / 0 blockers. It specifically
adjudicated the dense win as *not* an implementation bug — score signs, RRF and rerank
head-replacement all trace correct — but a property of the saturated set plus a general-domain
reranker over code.
