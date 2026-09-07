---
title: FINDINGS-0.5 — Embedding Model Evaluation Findings Log
status: active
created: 2026-08-28
updated: 2026-09-06
owner: Noel Saw
goal: Running findings log for the v0.5 embedding-model evaluation — CodeRankEmbed across four repos, measured against Gemini embeddings on a labelled retrieval set.
effort: 3
complexity: 3
risk: 2
related:
  - "PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md"
  - "PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md"
context_tags: [embeddings, retrieval, benchmarking, coderankembed, gemini, evaluation]
non_goals:
  - Per-issue execution planning — that lives in the GH-numbered docs (e.g. GH-5)
  - Replacing the run-by-run record in .embed-tmp/BENCHMARKS.md
---

# FINDINGS-0.5.md

Running findings log for the v0.5 embedding-model evaluation.

Scope: `nomic-ai/CodeRankEmbed` run over four repos, compared against Google
`gemini-embedding-001`. Machine: Apple M4 Pro, 12 cores, 24 GB.

Supporting detail: `.embed-tmp/BENCHMARKS.md` (run-by-run record, including failures),
`.embed-tmp/eval/` (labelled query set + scorer). Sidecars and raw telemetry live in
`temp/` (gitignored).

> **Naming note.** This doc keeps its non-`GH-` name deliberately: it is a *findings log
> spanning* issues [#2](https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/2),
> [#3](https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/3),
> [#4](https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/4) and
> [#5](https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/5), not the execution doc for
> any single one. Per the PDDA issue-intake contract, `GH-<number>-*.md` names a doc that owns
> one issue's execution; renaming this to a single number would misrepresent its scope.
> Per-issue execution docs are named that way — see
> [GH-5-QUANTIZATION-BENCHMARK.md](GH-5-QUANTIZATION-BENCHMARK.md).

## Status

| What was just completed | What's next |
|---|---|
| Completed the GH-11 Act 1 hybrid retrieval round-trip on the labelled LTVera-Pandas subset: 3,020 chunks, four scored modes, dedupe and latency gates met (2026-09-06). | Review the Act 1 evidence, then continue the v0.5 plan with a larger non-saturated benchmark and serving/runtime work. |

---

## 1. Corpus

All four repos embedded with CodeRankEmbed at `max_seq_length=2048`, batch 16, MPS,
768 dims. Every sidecar verified: row count matches `chunks.jsonl`, float32, no NaNs,
no zero vectors.

| Repo | Chunks | Wall time | s/chunk |
|---|---|---|---|
| `aegis-sleuth-slack-bot` | 3,226 | 1,054.5 s (17.6 min) | 0.327 |
| `LTVera-Pandas` | 5,147 | 1,529.9 s (25.5 min) | 0.297 |
| `rebalanceOS` | 4,111 | 1,145.8 s (19.1 min) | 0.279 |
| `XYZ-forge` | 3,949 | 2,257.3 s (37.6 min) † | 0.572 † |
| **Total** | **16,433** | **~86 min** (clean estimate) | ~0.31 |

† **XYZ-forge's timing is contaminated and should not be quoted.** CPU-bound evaluation
work was run concurrently during its third quarter. Its profile shows quarters 1/2/4 at
5.5–6.6 s per batch and quarter 3 at 16.9 s with one 269 s batch. Corrected estimate is
~1,460 s (~24 min, ~0.37 s/chunk), consistent with the other three. The *embeddings* are
unaffected — only the timing measurement is. Not re-run, as the numbers are not
load-bearing for any decision.

---

## 2. Test query results (per repo, top-3)

Queries are the ones already defined in `query_repos.py`. Assessment is a human read of
whether hits are semantically on target.

### rebalanceOS

| Query | Top hit | Read |
|---|---|---|
| PDDA lifecycle tracking roadmap items | `PROJECT/PDDA.md:1036-1095` (0.482) | **On target.** All three hits are PDDA/roadmap docs. |
| Gmail integration for reading and sending mail | `GMAIL.md:1-60` (0.461) | **On target**, but all three hits are docs — the actual Gmail ingest code did not surface in top-3. |
| calendar scheduler that finds available time slots | `scripts/pulse_web.py:1486-1545` (0.377) | **Partial.** Retrieved calendar *rendering* and a calendar *collector*; nothing that finds free slots. The concept may not exist in the repo. |

### LTVera-Pandas

| Query | Top hit | Read |
|---|---|---|
| alembic database migration script | `alembic/env.py:1-60` (0.492) | **Bullseye.** Hits 2–3 are migration tests. |
| docker compose service configuration | `PROJECT/3-COMPLETED/FOUNDATION.md:91-150` (0.441) | **Invalid query** — see §4. No compose file is in the corpus. |
| pipeline that processes a pandas dataframe | `external/.../pull_to_bq.py:901-929` (0.413) | **On target.** An actual dataframe→BigQuery loader. |

### aegis-sleuth-slack-bot

| Query | Top hit | Read |
|---|---|---|
| slack event handler for incoming messages | `src/slack-app.js:1621-1680` (0.469) | **Bullseye.** The literal message-event handler. |
| sentinel security monitoring check | `docs/SSH.md:46-105` (0.308) | **Off-base**, and instructively so — see §3. |
| backup script for sleuth data | `backup-sleuth-data-fixed.sh:1-60` (0.671) | **Bullseye**, and the highest-confidence hit in the whole set. |

### XYZ-forge

| Query | Top hit | Read |
|---|---|---|
| harness registry of model configurations | `HARNESS-MODELS-REGISTRY.generated.md:1-60` (0.472) | **On target.** Registry doc, its design doc, and `harness_app.py`. |
| relay automation loop between two agents | `test/relay-turn-handoff.sh:46-74` (0.516) | **On target.** All three hits are relay machinery. |
| fuzzing test queue runner | `pop-and-run-agy.sh:1-29` (0.488) | **Partial.** Top hit is a queue runner but not fuzzing; hits 2–3 are genuinely fuzzing. The query conflates two concepts. |

**Overall: 8 of 12 clearly on target, 2 partial, 1 off-base, 1 invalid by construction.**
For unlabelled spot-checks that is a good result — but see §6 on why it should not be read
as a quality verdict.

---

## 3. Finding: file paths are not embedded, so name-carried meaning is lost

The sharpest result in the whole exercise. `SENTINEL.md` **is** in the
`aegis-sleuth-slack-bot` index, yet for the query "sentinel security monitoring check" it
ranks **2,891 of 3,226** (score 0.011). For the near-literal query "SENTINEL monitoring" it
ranks **3,117** with a *negative* score.

Cause: `SENTINEL.md` is a **generated activity-log table** — timestamps, document paths and
status codes — not prose about security monitoring. Its filename carries the meaning; its
content does not.

And the chunker embeds **only the chunk body**. `path` is stored as metadata but never
included in the embedded text
(`.embed-tmp/scripts/embed_repos.py`, `chunk_file` → `text`). So for any file whose name is
informative and whose content is tabular, generated, or boilerplate, the model has nothing
to match on.

**Suggested fix:** prepend the file path (and enclosing heading, where cheap) to each
chunk's embedded text. This is a small change with a plausibly large recall benefit, and it
would need a re-index plus a re-score against the labelled set to confirm it does not
regress anything else.

This is worth its own issue and experiment.

---

## 4. Finding: the chunker cannot see YAML or Dockerfiles

Filed as **issue #2**.

`INCLUDE_EXT` is `.py .js .ts .tsx .jsx .php .md .go .rb .sh` — no `.yml`/`.yaml`, and
`Dockerfile` has no extension to match. LTVera-Pandas contains 5 `docker-compose*.yml`
files and 4 `Dockerfile`s; the index contains **zero** YAML chunks.

Consequences:

1. The standing test query "docker compose service configuration" is **unanswerable** and
   cannot discriminate between models. It should be excluded from evaluation until fixed.
2. More seriously, infra-as-code and CI workflows are a **silent blind spot** in production
   retrieval — no error, just quietly worse answers.

---

## 5. Finding: the original failure diagnosis was wrong

The earlier stalled run was attributed to `EMBED_MAX_MEM_MB=4096` being "too tight". That
is **not** what was happening.

`encode()` pads every sequence in a batch to the longest member. Chunk token lengths are
heavily right-skewed (p50 808, max 8,540 in LTVera-Pandas), so one long chunk inflates its
whole batch to 8,192 tokens, and the attention tensor alone needs
`16 × 12 heads × 8192² × 4 B ≈ 51 GB`. On 24 GB that is fatal: Metal reports an allocator
OOM, the CPU path is SIGKILLed.

Two consequences:

- **`EMBED_MAX_MEM_MB` cannot prevent this.** The RSS watchdog samples *between* batches;
  the process dies *inside* a single `encode()` call. Raising 4096 → 12288 changed nothing.
- **Measured peak RSS was 2,475 MB** — comfortably inside the *original* 4096 ceiling. The
  cap was never the binding constraint. Capping `max_seq_length` to 2048 is what fixed it.

Also: `RLIMIT_AS` cannot be set on this machine at all, so that guard is a no-op regardless.
And on MPS the RSS watchdog is **structurally blind** — Metal allocations never enter
process RSS (659 MB reported for work that costs 2,475 MB on CPU), so `EMBED_MAX_MEM_MB`
constrains nothing on the GPU path. The sequence cap is the only real safety mechanism.

---

## 6. CodeRankEmbed vs Gemini — measured, and it is a tie

Filed as **issue #3**, with a correction comment.

Labelled evaluation: 30 queries with verified ground-truth targets, both indexes built from
a **byte-identical** `chunks.jsonl` (verified with `cmp`), every target confirmed present in
the index before scoring.

| model | MRR | R@1 | R@3 | R@5 | R@10 | never found |
|---|---|---|---|---|---|---|
| CodeRankEmbed (local) | **0.801** | **0.700** | 0.867 | 0.933 | 0.933 | 0 |
| `gemini-embedding-001` | 0.782 | 0.667 | **0.933** | **0.967** | **0.967** | 0 |

**The models are effectively tied.** CodeRankEmbed is marginally better at the top slot,
Gemini at the top few. Neither ever failed to find the target. At n=30 a single query moves
R@1 by 0.033, so both gaps are inside the noise floor.

**An earlier three-query impression — that CodeRankEmbed "retrieves code where Gemini
retrieves prose" — did not survive contact with ground truth.** It was a sampling artifact.
This is the main methodological lesson of the exercise: unlabelled spot-checks produced a
confident and wrong conclusion, and §2 above should be read with that in mind.

### Cost and speed

| | CodeRankEmbed (local, MPS) | Gemini |
|---|---|---|
| LTVera-Pandas, 5,147 chunks | 1,529.9 s | **58.8 s (~26× faster)** |
| Cost | **$0.00** | $0.5774 |
| All 4 repos (16,433 chunks) | ~86 min, **$0.00** | ~5 min, **$1.84** |

Billed 3,849,555 tokens at $0.15/1M (paid standard tier), read from Google's live pricing
page on 2026-08-28. Zero retries, zero dropped chunks.

### Recommendation

Since quality does not discriminate, **decide on cost and operational fit.** Lean local:
free, self-hosted, no API key to manage, and ~86 min is acceptable for a full re-index that
happens rarely. Gemini's 26× speed advantage matters only if frequent full re-indexing
becomes a requirement.

---

## 7. Querying is cheap — the expensive part is a one-off

Filed as **issue #4** (draft). Query-path measurements, which matter more than indexing
cost since querying is the repeated workload:

| | measured (CPU, 4 threads) |
|---|---|
| Query encode | **44.0 ms** (p50 41.6, p95 53.8) |
| Vector search (brute-force cosine) | **1.5 ms** (p50 0.23) |
| End-to-end per query | **45.4 ms** |
| Peak RSS while querying | **579 MB** |
| Index size | **2.9 MB per 1,000 chunks** — ~48 MB for all four repos |

- **A 16 GB box is ample**: model + all four indexes resident is ~630 MB, about 4% of RAM.
- **Search is not the bottleneck** — the model encode is, by ~30×. A vector database buys
  nothing at this scale; brute-force numpy is ~5 ms over the full 16k corpus.
- Model load is **11.6 s**, which argues for a long-lived service over per-query CLI runs.
- **Index and query model must match.** A CodeRankEmbed index cannot be queried with Gemini
  vectors; switching one side means re-indexing.

---

## 8. Open items

- **Embed the file path with each chunk** (§3) — likely the highest-value single change;
  needs re-index + re-score.
- **Widen `INCLUDE_EXT`** to cover YAML and extensionless files (issue #2) — requires
  re-embedding, since the corpus changes.
- **int8 quantization experiment** (issue #5) — for query latency on Intel, not memory.
  Note Unsloth is the wrong tool (decoder-only LLMs, CUDA); the path is
  `export_dynamic_quantized_onnx_model` / `export_static_quantized_openvino_model`.
- **Verify on real Intel hardware** — everything in issue #4 is extrapolated from an M4 Pro.
- **Grow the labelled set beyond 30 queries / one repo** if a small real quality difference
  ever needs resolving.
- `query_repos.py` still derives `OUT_ROOT` from its own location and cannot see the
  sidecars now that they live in `temp/`; it needs the same override the embedding runs use.

---

## Run: XYZ hybrid retrieval round-trip (GH-11 Act 1) — 2026-09-06

This run used the new `xyz` SQLite/FTS5/sqlite-vec pipeline and the existing 30-query labelled
LTVera-Pandas set. Metrics are depth-bounded: **MRR@100 / R@k / miss@100**, with chunk ranks and
no path de-duplication. Run 9's MRR 0.801 / R@1 0.700 ranked the full corpus with the old chunker
and is context only, not a directly comparable baseline.

### Corpus and ingest provenance

- **corpus: subset** — one root-preserving invocation with `scripts/`, `app/`, and `alembic/`;
  every gold path was verified present in `chunks.path` before scoring.
- **339 files / 3,020 chunks**; chunker version = **this commit** (including byte-offset-derived
  source lines, avoiding corrupt native Tree-sitter point metadata observed during the full run).
- Full-corpus attempt: 1,793 files / 17,258 chunks projected by the fake-model dry run. The real
  CPU ingest was aborted at 204 chunks when the required early estimate reported **206.5 min**,
  above the 45-minute fallback threshold.
- First subset ingest: **1,664.72 s wall** (27m 44.72s); `files_seen=339`,
  `chunks_written=3,020`, `chunks_embedded=3,020`; peak RSS **9,852.62 MB**.
- Identical second ingest: **8.62 s wall**; `files_skipped=339`, `chunks_written=0`,
  `chunks_embedded=0`.
- Local-only execution: cached CodeRankEmbed and `mixedbread-ai/mxbai-rerank-xsmall-v1`, CPU.
  MPS could not be used in the managed runtime, so `XYZ_DEVICE=cpu` was pinned explicitly.

### Retrieval quality at depth 100

| mode | MRR@100 | R@1 | R@3 | R@5 | R@10 | miss@100 |
|---|---:|---:|---:|---:|---:|---:|
| dense | **0.9444** | **0.9000** | **1.0000** | **1.0000** | **1.0000** | 0 |
| BM25 | 0.8583 | 0.7667 | 0.9333 | 0.9667 | 0.9667 | 0 |
| hybrid | 0.9222 | 0.8667 | 0.9667 | 0.9667 | **1.0000** | 0 |
| hybrid+rerank | 0.9016 | 0.8667 | 0.9667 | 0.9667 | 0.9667 | 0 |

The reranked arm passes the Act 1 noise-floor criterion: its MRR is 0.0428 below dense and its
R@1 is 0.0333 below dense, both within 0.05. This saturated 30-query set does **not** establish
that reranking improves relevance: it reordered all 30 top-10 chunk-id sequences but scored below
dense and hybrid. The CPU reranker cost is also material and belongs in later serving work.

### Latency (milliseconds, p50 / p95)

| mode | embed query | BM25 | dense | fuse | rerank | total |
|---|---:|---:|---:|---:|---:|---:|
| dense | 81.28 / 119.48 | 0 / 0 | 3.12 / 4.65 | 0 / 0 | 0 / 0 | 86.42 / 125.35 |
| BM25 | 0 / 0 | 0.85 / 2.03 | 0 / 0 | 0 / 0 | 0 / 0 | 1.34 / 2.68 |
| hybrid | 73.68 / 91.92 | 0.73 / 1.89 | 3.10 / 3.82 | 0.12 / 0.16 | 0 / 0 | 78.70 / 96.23 |
| hybrid+rerank | 142.91 / 313.98 | 1.27 / 3.33 | 3.93 / 6.40 | 0.13 / 0.32 | 50,003.77 / 93,867.16 | 50,175.41 / 94,262.74 |

Four Phase 1 QA-gate bullets:

- **MET — real ingest + query round-trip:** labelled subset indexed 339 files / 3,020 chunks and
  all four modes scored 30 queries at depth 100 with zero misses.
- **MET — unchanged re-ingest near-instant:** 8.62 s, `chunks_embedded=0` (<30 s).
- **MET — reranker measurably reorders RRF:** **30/30** queries had a different top-10 chunk-id
  sequence under `hybrid+rerank` than under `hybrid`.
- **MET — latency instrumented:** p50/p95 recorded above for every stage in every mode.
