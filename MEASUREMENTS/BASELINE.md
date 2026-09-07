# BASELINE — current default settings

Every knob XYZ runs on, its value, and **why that value**. Read the rules in `README.md` before
changing anything: a baseline row moves only when a run in `runs/` justifies it.

Last changed: **2026-09-07** (initial capture from the Act 1 delivery, PR #15 / `fa1812d`).

Legend for **Source**:
**default** = a recognised convention or the library default, adopted rather than invented ·
**measured** = set by a run in this folder · **constraint** = forced by hardware, licence or a
guiding principle · **judgment** = chosen by a person; the weakest kind, and each one is a candidate
for replacement by a default or a measurement.

## Embedding

| knob | value | source | why |
|---|---|---|---|
| model | `nomic-ai/CodeRankEmbed` | measured | Cross-source consensus pick; measured MRR@100 0.9444 / R@1 0.9000 (run `2026-09-06-act1-roundtrip`). MIT. |
| dims | 768 | constraint | Fixed by the model. |
| `max_seq_length` | 2048 | measured | The model's real window and the **actual** memory guard — the original OOM was sequence-length skew, not an unbounded process (FINDINGS-0.5.md; issue #14 removed the inert RSS watchdog). |
| query prefix | `Represent this query for searching relevant code: ` | constraint | Required by the model card; queries only, never documents. |
| batch size | 16 | default | `EMBED_BATCH_SIZE`; carried from the original embedder, never contested by a measurement. |
| device | MPS if available, else CPU | constraint | Vectors are identical either way (cosine 1.000000, max abs diff 7.2e-06). MPS was unavailable in the managed runtime for the Act 1 run. |
| normalisation | L2, at encode time | constraint | `vec0` ranks by L2 distance; unit vectors make it equivalent to cosine. |

## Chunking

| knob | value | source | why |
|---|---|---|---|
| code chunker | Tree-sitter, function/class level | constraint | Guiding principle: XYZ's genuine improvement over Ask-Self's regex/line chunkers. Languages: Python, JS, TS, TSX, PHP. |
| Markdown | heading sections, level ≤ 3 | judgment | **Candidate for review** — never measured against level ≤ 2 or ≤ 4. |
| everything else | file-level, split at 6,000 chars | judgment | 6,000 chars is a *character heuristic* chosen to sit under the 2,048-token window with headroom — **not** a tokenizer bound. Candidate for measurement. |
| overlap on split | ~150 chars | judgment | Carried from the original embedder. Never measured. |
| **path prefix** | **on** — every chunk's embedded text begins with its relative path | measured | The single largest quality change in the project: MRR 0.80 → 0.98 (issue #8). Do not turn this off without a run. |
| include list | code + YAML/TOML/JSON/SQL/HTML/Dockerfile/Makefile/templates | measured | Widened after issue #2 found YAML and Dockerfiles were silently invisible. |

## Retrieval

| knob | value | source | why |
|---|---|---|---|
| default mode | `auto` → `hybrid+rerank` when a reranker is present, else `hybrid` | judgment | **Contradicted by measurement** — dense-only currently scores highest and rerank costs 50 s/query. See Open questions. |
| RRF `k` | 60 | default | The value from the original RRF paper and the canonical doc; not tuned here. |
| `fetch_k` (candidates per lane) | 50 | default | Library default in `pipeline.py`; the Act 1 eval ran at depth 100 explicitly. |
| rerank depth | first `min(depth, 50)`, tail appended in RRF order | judgment | Canonical doc says "top 25–50"; 50 is the upper end. Untuned. |
| KNN form | `vec0 … WHERE embedding MATCH ? AND k = ?` | constraint | A parameterised `LIMIT ?` is rejected on stricter sqlite-vec builds and 500'd in production upstream (Ask-Self issue #23). |
| lexical | SQLite FTS5, `score = -bm25()` | constraint | All lanes normalised higher-is-better. |
| no-answer τ | unset (`None`) | judgment | Never tuned — that is what the Phase 2 dev split is for. |
| reranker | `mixedbread-ai/mxbai-rerank-xsmall-v1` | measured | **Replaced** `cross-encoder/ms-marco-MiniLM-L-6-v2`, which loads without error on torch 2.14 / transformers 5.16 and returns `[nan, nan]`. Apache-2.0, ~70 MB. Fallback `BAAI/bge-reranker-base` (MIT), also verified. |

## Evaluation

| knob | value | source | why |
|---|---|---|---|
| canonical scorer | `xyz/eval/metrics.py` | judgment | Chosen over two older implementations because it is the only depth-parameterised, chunk-id-preserving one. The others should call it, not reimplement. |
| depth `D` | 100 | judgment | The pipeline ranks `fetch_k` candidates, unlike the old whole-corpus scorer, so depth must be explicit for numbers to compare. |
| metrics | MRR@D, R@{1,3,5,10}, miss@D | default | Standard IR set; matches the pre-existing scorer so history stays comparable. |
| relevance | a hit is a retrieved chunk whose `path` is in the query's `relevant` list | default | Inherited from `score_retrieval.py`; file-level judgement. |
| noise floor | 0.05 | measured | At n=30, one query moves R@1 by 0.033; deltas below ~0.05 are unresolvable (GH-5). **This floor is a function of n and must be recomputed when the set grows.** |

## Frozen benchmark

| knob | value | source | why |
|---|---|---|---|
| size | **50** | default | The TREC per-track convention for a test collection. Chosen over the previous plan's 250 (unexecutable against this corpus) and over an agent's invented "60-80" — guiding principle #3, *deterministic where judgment isn't needed*, says take the field default rather than a made-up number. Principle #7 adds: labelling is expensive and irreversible, so start at the smallest defensible size and grow only on evidence. **Both consult advisors independently confirmed 50 and named the same convention.** |
| primary stratification | query **type**, not language | default | Both advisors, independently and emphatically. Language balance does nothing about the measured failure mode (filename leakage); question difficulty does. |
| slice allocation | 24 behaviour-described · 14 cross-file/architecture · 4 test↔implementation · 8 no-answer | default | Codex's allocation, adopted whole rather than blended — it is internally consistent and pairs with the path-only screen below. |
| **name-carried questions in the frozen set** | **zero**, enforced by a path-only screen | default | The decisive rule. Every answerable candidate is rejected if a **path-only retrieval baseline puts the gold file in its top 3**. This is a deterministic filter, not a human judgement about whether a question "looks easy" — principle #3. It is what makes re-saturation structurally hard rather than merely hoped against. |
| language secondary quota | Python 16 · JS+TS 12 · PHP 9 · HTML/WP-template 5 (= 42 answerable) | default | Recorded and checked, but subordinate to type. TS folded into JS (16 files repo-wide). Blade/Twig absent — zero in the corpus. |
| regression set | the existing 30-query set, kept separate | judgment | Tie-break: agy wanted 10 name-carried "sanity checks" *inside* the 50; Codex wanted zero. Resolved by keeping the old saturated set as a **separate smoke/regression set** — its saturation is exactly what makes it a fine "did we break the easy path" check, and it costs none of the frozen budget. |
| dev split | 20 — 10 answerable + 10 no-answer | default | Codex's, over agy's 15: tuning a *no-answer* threshold needs no-answer examples, so a balanced 10/10 is the right shape. Must be disjoint from the frozen set **and from its gold files**, or threshold tuning leaks selection information into the only decision set. |
| growth rule | +25 hard questions when **every compared arm scores answerable R@3 = 1.000** on the frozen 50 | default | Codex's, over agy's two-threshold version: it is a single unambiguous condition and a direct test of the actual failure mode. agy's alternative (top-two MRR gap < noise floor while both > 0.85) is recorded as a secondary signal, not a trigger. |

## Open questions this baseline is honest about

1. **The default mode contradicts the measurement.** `auto` prefers `hybrid+rerank`, which scored
   *lowest* (0.9016 vs dense 0.9444) and costs 50 s/query on CPU. It stays the default only because
   the current 30-query set is saturated and cannot referee it. **The Phase 2 set decides this row.**
2. **Six knobs are `judgment`** — Markdown heading depth, the 6,000-char split, the 150-char overlap,
   rerank depth, depth `D`, and the canonical-scorer choice. None has ever been measured. They are
   listed so they can be attacked deliberately rather than inherited silently.
3. **The 0.05 noise floor is tied to n=30** and will be wrong the moment the set changes size.
