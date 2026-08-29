# CodeRankEmbed calibration benchmarks

Profiling runs used to size `EMBED_MAX_MEM_MB` / `EMBED_MAX_THREADS` / `EMBED_BATCH_SIZE`
before committing to the full multi-repo embedding run. See `SOP.md` for the knobs
themselves; this file is the run-by-run record, including failures.

## Machine

| | |
|---|---|
| Host | Apple M4 Pro, 12 cores |
| RAM | 24 GB unified |
| OS | macOS (Darwin 24.6.0) |
| Python | 3.11.15 (`.venv`, created with stdlib `venv` — `uv` is not installed here) |
| torch | 2.13.0 |
| sentence-transformers | 6.0.0 |
| MPS available | yes (`torch.backends.mps.is_available() → True`) |

Model smoke test (per `SOP.md`) passes: `encode([query, code])` → shape `(2, 768)`,
cosine similarity 0.771 between the sample query and its matching snippet.

## Calibration repo

`aegis-sleuth-slack-bot` → `/Users/noelsaw/Documents/GitHub Repos/AEGIS-Sleuth-Slackbot`
(remote `HiQS-Labs/AEGIS-Sleuth-Slackbot`), **536 files / 3,226 chunks** — the smallest
of the four target repos, so the fastest calibration turnaround.

Chunk counts for the other three, measured with the script's own
`iter_files` + `chunk_file`:

| Repo | Path (under `GitHub Repos/`) | Files | Chunks |
|---|---|---|---|
| `aegis-sleuth-slack-bot` | `AEGIS-Sleuth-Slackbot` | 536 | 3,226 |
| `XYZ-forge` | `XYZ-forge` | 958 | 3,949 |
| `rebalanceOS` | `rebalanceOS` | 719 | 4,111 |
| `LTVera-Pandas` | `LTVera-Pandas` | 819 | 5,147 |
| | | | **16,433 total** |

Each checkout was confirmed against the previous run's partial `chunks.jsonl` by
checking that every distinct file path recorded there still resolves:
AEGIS 17/17, rebalanceOS 7/7.

> **Path trap:** there are two similarly-named directories —
> `rebalanceOS` (the real checkout, `HiQS-Labs/rebalanceOS`, 27 MB) and
> `rebalance-OS` (an empty stub containing only `temp/`). The `REPOS` dict must
> point at `rebalanceOS`. Pointed at the stub, `process_repo` prints
> `[skip] no chunks produced` and the full run silently omits that repo.

---

## Run 1 — default device (MPS), batch 16 — FAILED

```bash
EMBED_MAX_MEM_MB=12288 EMBED_PROFILE=1 nice -n 10 \
  .venv/bin/python -u .embed-tmp/scripts/embed_repos.py \
  --repo aegis-sleuth-slack-bot "…/AEGIS-Sleuth-Slackbot"
```

| | |
|---|---|
| Device | `mps` (auto-selected) |
| `EMBED_MAX_MEM_MB` | 12288 |
| `EMBED_BATCH_SIZE` | 16 (default) |
| `EMBED_MAX_THREADS` | 4 (default) |
| Outcome | **failed, exit 1**, on the first batch |
| Chunks embedded | 0 of 3,226 |
| profile.csv | not written |

Chunking succeeded (3,226 chunks) and the model loaded; the run then died with a
Metal command-buffer OOM:

```
Error: command buffer exited with error status.
	Insufficient Memory (00000008:kIOGPUCommandBufferCallbackErrorOutOfMemory)
	<AGXG16XFamilyCommandBuffer: 0x16f728660> device = Apple M4 Pro
```

**Findings:**

1. `.embed-tmp/scripts/embed_repos.py:165` constructs
   `SentenceTransformer("nomic-ai/CodeRankEmbed", trust_remote_code=True)` with no
   `device` argument, so sentence-transformers auto-selects `mps` on Apple Silicon.
2. **None of the SOP's memory knobs constrain the Metal allocator.**
   `EMBED_MAX_MEM_MB` drives an RSS watchdog over *host* memory, and
   `EMBED_MAX_THREADS` / `torch.set_num_threads` cap *CPU* threads. The GPU path
   ignores all of them, so this failure is unrelated to the 4096 → 12288 change.
3. `RLIMIT_AS` cannot be set on this machine at all — the script logs
   `could not set RLIMIT_AS hard cap (current limit exceeds maximum limit)`, so
   that best-effort cap is a no-op here and the RSS watchdog is the only host-side
   guard.

This is a *different* failure mode from the earlier small-RAM machine, where the
RSS watchdog tripped and aborted after ~48–64 chunks. Here nothing was embedded at all.

---

## Run 2 — CPU pinned, batch 16, no sequence cap — FAILED

Same command, with the model constructor patched to `device="cpu"` via a scratchpad
wrapper (the committed script was left untouched).

| | |
|---|---|
| Device | `cpu` |
| `EMBED_MAX_MEM_MB` | 12288 |
| `EMBED_BATCH_SIZE` | 16 (default) |
| `max_seq_length` | 8192 (model default) |
| Outcome | **failed, exit 137 (SIGKILL)** — OS-killed |
| Chunks embedded | 0 of 3,226 (died before batch 10) |
| profile.csv | not written |

The log ends immediately after the model loads, with a leaked-semaphore warning at
shutdown — the signature of an abnormal kill, not a clean exit. Note the background
task runner reported "exit code 0"; the process's real status was 137.

## Root cause (applies to Runs 1 and 2 alike)

Measured token-length distribution over all 3,226 AEGIS chunks:

| | tokens |
|---|---|
| `model.max_seq_length` | **8192** |
| min | 28 |
| p50 | 808 |
| p90 | 1,133 |
| p99 | 1,844 |
| max | **8,540** |
| chunks > 2048 tokens | 21 |
| chunks > 8192 tokens | 1 (truncated) |

`model.encode()` pads every sequence in a batch to the longest member of that batch.
The distribution is heavily right-skewed, so a batch of 16 that happens to include the
8,540-token chunk is padded to 8,192 — and the attention scores alone are
`16 × 12 heads × 8192 × 8192 × 4 bytes ≈ 51 GB`. On 24 GB that is fatal regardless of
backend: Metal reports an allocator OOM (Run 1), the CPU path gets SIGKILLed by the
kernel (Run 2).

Two consequences for calibration:

1. **`EMBED_MAX_MEM_MB` cannot prevent this.** The RSS watchdog is sampled *between*
   batches ([embed_repos.py:182](.embed-tmp/scripts/embed_repos.py#L182)); a single
   oversized batch exhausts memory *within* one `encode()` call, so the process dies
   before the watchdog ever takes a reading. Raising the cap 4096 → 12288 changes
   nothing about this failure.
2. **The real lever is `max_seq_length`,** with `EMBED_BATCH_SIZE` secondary. Capping
   sequence length to 2048 covers p99 of the corpus and drops worst-case attention to
   `16 × 12 × 2048² × 4 ≈ 3.2 GB`; capping to 1024 covers p90 at ≈ 0.8 GB.

This also retro-explains the earlier small-RAM machine: the watchdog "tripping" after
~48–64 chunks (3–4 batches of 16) is exactly when the first long-chunk batch lands.
The original diagnosis — that 4096 MB was merely "too tight" — was incomplete.

---

## Run 3 — CPU, batch 16, `max_seq_length=2048` — PASSED

```bash
EMBED_DEVICE=cpu EMBED_MAX_SEQ=2048 EMBED_MAX_MEM_MB=12288 EMBED_PROFILE=1 nice -n 10 \
  .venv/bin/python -u <wrapper> aegis-sleuth-slack-bot "…/AEGIS-Sleuth-Slackbot"
```

| | |
|---|---|
| Device | `cpu` |
| `max_seq_length` | 2048 |
| `EMBED_BATCH_SIZE` / `EMBED_MAX_THREADS` | 16 / 4 |
| `EMBED_MAX_MEM_MB` | 12288 |
| Outcome | **passed, exit 0** — no watchdog warning, no early abort |
| Chunks embedded | **3,226 / 3,226** |
| Wall time | **2,108.6 s (35.1 min)** |
| Peak / avg RSS | **2,475 MB** / 2,179 MB |
| Peak / avg CPU | **275 %** / 243 % |
| Avg batch time | **9.93 s** (p50 8.64 s, max 23.67 s) |

Artifacts: `_bench/run3_cpu_seq2048_profile.csv`, `_bench/run3_cpu_seq2048.log`.

## Run 4 — MPS, batch 16, `max_seq_length=2048` — PASSED

Identical to Run 3 except `EMBED_DEVICE=mps`, so the backend is the only variable.

| | |
|---|---|
| Device | `mps` |
| `max_seq_length` | 2048 |
| Outcome | **passed, exit 0** |
| Chunks embedded | **3,226 / 3,226** |
| Wall time | **1,054.5 s (17.6 min)** |
| Peak / avg RSS | **659 MB** / 129 MB |
| Peak / avg CPU | **82 %** / 16 % |
| Avg batch time | **4.71 s** |

Artifacts: `_bench/run4_mps_seq2048_profile.csv`, `_bench/run4_mps_seq2048.log`,
`_bench/run4_mps_embeddings.npy`.

### Equivalence check

MPS output was validated against a CPU re-encode of 64 chunks sampled evenly across
the corpus, at the same sequence cap:

```
cosine CPU-vs-MPS: min=1.000000  mean=1.000000
max abs diff:      7.153e-06
```

The two backends produce the same vectors to fp32 rounding noise, so the MPS speedup
costs nothing in retrieval quality.

---

## Comparison and recommendation

| | CPU | MPS | |
|---|---|---|---|
| Wall time (3,226 chunks) | 2,108.6 s | **1,054.5 s** | **2.00× faster** |
| Per chunk | 0.654 s | **0.327 s** | |
| Avg batch time | 9.93 s | **4.71 s** | |
| Peak RSS | 2,475 MB | 659 MB | *not comparable — see below* |
| Avg host CPU | 243 % | **16 %** | leaves the machine usable |

Projected full 4-repo run (16,433 chunks, same settings):

| | estimate |
|---|---|
| CPU | ≈ 10,700 s — **~3 h 0 m** |
| MPS | ≈ 5,400 s — **~1 h 30 m** |

**Recommended: MPS, `max_seq_length=2048`, `EMBED_BATCH_SIZE=16`.** Half the wall
clock, identical vectors, and it leaves the CPU almost entirely free (16 % avg vs
243 %) — which serves the SOP's original "don't starve the machine" goal far better
than CPU throttling does.

### Caveats that matter more than the timings

1. **On MPS the RSS watchdog is blind.** Metal allocations live in the unified-memory
   GPU heap and never appear in process RSS — hence 659 MB peak on MPS vs 2,475 MB for
   the same work on CPU. `EMBED_MAX_MEM_MB` therefore constrains *nothing* on the MPS
   path, which is why Run 1 died with no watchdog warning at all. An MPS full run has
   no memory guard; safety comes entirely from the sequence cap.
2. **`EMBED_MAX_MEM_MB` was never the binding constraint.** Even the CPU run peaked at
   2,475 MB — comfortably inside the *original* 4096 MB. The 4096 → 12288 change was
   not what fixed anything; the sequence cap was.
3. **The cap truncates 21 chunks** (those over 2,048 tokens, 0.65 % of the corpus).
   Lowering to 1024 would truncate ~10 %. A non-truncating alternative is to sort
   chunks by token length before batching so long chunks batch together and padding
   waste collapses — but that changes the script's batching loop rather than a knob,
   and has not been benchmarked here.
4. `RLIMIT_AS` cannot be set on this machine at all, so that cap is a no-op regardless
   of backend.

---

## Run 5 — LTVera-Pandas, MPS, batch 16, `max_seq_length=2048` — PASSED

Second-repo confirmation that the recommended config generalises, on the *largest*
of the four repos rather than the smallest.

| | |
|---|---|
| Repo | `LTVera-Pandas` (819 files) |
| Device / seq cap | `mps` / 2048 |
| Outcome | **passed, exit 0** |
| Chunks embedded | **5,147 / 5,147** |
| Wall time | **1,529.9 s (25.5 min)** |
| Per chunk | **0.297 s** |
| Peak / avg RSS | **814 MB** / 125 MB |
| Peak / avg CPU | **73 %** / 15 % |
| Avg batch time | **4.25 s** (322 batches) |

Output integrity checks on `embeddings.npy`: shape `(5147, 768)` float32, row count
matches `chunks.jsonl`, no NaNs, no all-zero rows.

Per-chunk throughput is slightly *better* than the smaller AEGIS repo (0.297 s vs
0.327 s), so cost scales with chunk count rather than degrading on larger repos.

### Revised projection for the full 4-repo run (MPS)

Two repos are now measured rather than extrapolated: 8,373 chunks in 2,584.4 s.
Applying the blended 0.309 s/chunk to the remaining 8,060 chunks
(`XYZ-forge` 3,949 + `rebalanceOS` 4,111):

| | |
|---|---|
| Measured so far | 2,584 s (AEGIS + LTVera-Pandas) |
| Remaining estimate | ≈ 2,490 s |
| **Full 4-repo run** | **≈ 5,075 s — about 1 h 25 m** |

---

## Run 6 — LTVera-Pandas, Gemini `gemini-embedding-001` — PASSED

Same corpus as Run 5 (identical chunker, asserted 5,147 chunks before spending), so
this is a like-for-like comparison against local CodeRankEmbed.

| | |
|---|---|
| Model | `gemini-embedding-001`, 768 dims |
| task_type | `RETRIEVAL_DOCUMENT` (chunks) / `RETRIEVAL_QUERY` (queries) |
| Auth | Secret Manager `ltvera-gemini-api-key`, project `ltvera-gce-and-bigquery`, billing `01F8BE-516825-41AC0E` |
| Chunks | **5,147 / 5,147** |
| Embed wall time | **58.8 s** (52 API calls, batch 100) |
| Token-count wall time | 32.4 s (5,147 free `countTokens` calls, 16 workers) |
| Retries / dropped | **0 / 0** |
| Input tokens | 3,904,933 raw → **3,849,555 billed** (capped at the 2,048 limit) |
| Unit price | **$0.15 / 1M** (paid standard; batch tier $0.075/1M not used) |
| **Total cost** | **$0.5774** |
| Cost per 1k chunks | $0.1122 |
| Projected 4 repos (16,433 chunks) | **$1.84** |

Price read from <https://ai.google.dev/gemini-api/docs/pricing> on 2026-08-28 and
recorded in `cost_summary.json` with the source URL, rather than taken from memory.

### Measurement caveats

1. `embed_content` returns **no usage metadata** (`response.metadata is None`), so billed
   tokens cannot be read off the embedding response. They come from the separate
   `countTokens` endpoint, which is not billed as embedding input.
2. `count_tokens` over a **list does not equal the sum of per-item counts** (10 copies of a
   5-token string → 41, not 50). Tokens were therefore counted per chunk, not per batch;
   batch-level counting would have understated the bill.
3. **Over-limit inputs are silently truncated, not rejected.** An 8,101-token text embedded
   without error against a 2,048-token limit. Billed tokens are reported capped at the
   limit, with the raw sum kept for transparency.
4. **The two tokenizers disagree on the same text.** 72 chunks exceed Gemini's 2,048-token
   limit versus 21 under CodeRankEmbed's tokenizer — Gemini silently truncates ~3.5× more
   of the corpus at a nominally identical cap.

## Head-to-head: CodeRankEmbed (local) vs Gemini — LTVera-Pandas, 5,147 chunks

| | CodeRankEmbed (MPS) | Gemini `-001` |
|---|---|---|
| Wall time | 1,529.9 s (25.5 min) | **58.8 s** (91.2 s incl. token counting) |
| Speed | 0.297 s/chunk | **0.0114 s/chunk — ~26× faster** |
| Cost | **$0.00** | $0.5774 |
| Dims | 768 | 768 |
| Projected 4 repos | ~85 min, $0.00 | **~5 min, $1.84** |

### Retrieval quality (3 test queries, top-3)

Scores are **not comparable across models** — different embedding spaces. Judge ranking only.

**1. "alembic database migration script"**

| CodeRankEmbed | Gemini |
|---|---|
| `alembic/env.py:1-60` | `alembic/env.py:1-60` |
| `tests/test_migrations.py:1-60` | `REPO_MAP.md:91-150` |
| `tests/test_rls_isolation.py:46-105` | `REPO_MAP.md:136-195` |

Both nail the same #1. CodeRankEmbed's remaining hits are **real migration code**;
Gemini's are **documentation about** the repo. Edge: CodeRankEmbed.

**2. "docker compose service configuration" — INVALID TEST**

Neither result is meaningful. The repo has 5 `docker-compose*.yml` files and 4
`Dockerfile`s, but `INCLUDE_EXT` covers only `.py .js .ts .tsx .jsx .php .md .go .rb .sh`
— **zero `.yml`/`.yaml` chunks are in the index** (`Dockerfile` has no extension either).
Both models were forced to return second-best prose. This is a **chunker configuration
gap, not a model failure**, and the query cannot discriminate between models until
`INCLUDE_EXT` is widened.

**3. "pipeline that processes a pandas dataframe"**

| CodeRankEmbed | Gemini |
|---|---|
| `external/…/pull_to_bq.py:901-929` | `utils/wp-bq/PIPELINE.md:1-60` |
| `external/…/BUNDLE.md:181-199` | `app/ai/service.py:451-510` |
| `scripts/monitor_open_cdp_phase4.py:226-285` | `PROJECT/2-WORKING/WPDBTK-FULL-MIGRATION.md:1-60` |

CodeRankEmbed returns 2 code hits including an actual dataframe→BigQuery loader;
Gemini leads with a prose `PIPELINE.md` and a migration doc. Edge: CodeRankEmbed.

### Read

On this evidence **CodeRankEmbed retrieves code, Gemini retrieves prose about code** —
consistent with CodeRankEmbed being code-specialised and Gemini being general-purpose.
For a code-intelligence index that favours CodeRankEmbed, and it is free.

Gemini's advantage is throughput: ~26× faster, and the whole 4-repo corpus for under $2.

**This is weak evidence and should not settle the decision.** Only 2 of 3 queries were
valid, top-3 only, one repo, and no ground-truth relevance labels — the judgement above is
my read of the hits, not a measured score. A real verdict needs a labelled query set
(say 20–30 queries with known-correct targets) and recall@k. Worth doing before
committing to a model.

> **Superseded — see Run 9 below.** The labelled 30-query evaluation does **not** support
> the "CodeRankEmbed clearly wins on quality" read above. Measured, the two models are
> near-parity. The three-query impression was an artifact of a tiny sample.

---

## Run 9 — labelled retrieval evaluation (30 queries, ground truth)

Both indexes were built from a **byte-identical `chunks.jsonl`** (verified with `cmp`), so
row *i* is the same chunk in both and scores are directly comparable. 30 queries with
known-correct target files, each target verified to exist *and* to be present in the index
before scoring. Query set: `.embed-tmp/eval/queries-LTVera-Pandas.json`;
scorer: `.embed-tmp/eval/score_retrieval.py`; raw output: `temp/eval_LTVera-Pandas.json`.

| model | MRR | R@1 | R@3 | R@5 | R@10 | never found |
|---|---|---|---|---|---|---|
| CodeRankEmbed (local) | **0.801** | **0.700** | 0.867 | 0.933 | 0.933 | 0 |
| gemini-embedding-001 | 0.782 | 0.667 | **0.933** | **0.967** | **0.967** | 0 |

### What this actually says

**The two models are effectively tied.** CodeRankEmbed is marginally better at getting the
right file into the *top slot* (MRR 0.801 vs 0.782, R@1 0.700 vs 0.667); Gemini is better
at getting it into the *top few* (R@3 0.933 vs 0.867, R@5/R@10 0.967 vs 0.933). Neither
ever failed to find the target somewhere. On 30 queries these gaps are within noise —
a one-query swing moves R@1 by 0.033.

**This overturns the earlier three-query impression.** The idea that "CodeRankEmbed
retrieves code while Gemini retrieves prose" did not survive contact with ground truth.
It came from 2 usable queries and was a sampling artifact, which is exactly why it was
flagged as unreliable at the time.

### Each model has distinct failure modes

| query | local rank | gemini rank |
|---|---|---|
| benchmark campaign ranking performance | **106** | 11 |
| check whether next best product is populated | **16** | 1 |
| compute signals in bigquery | 5 | 2 |
| audit klaviyo oauth scopes | 1 | **5** |
| seed the calendar library with initial data | 4 | 2 |

CodeRankEmbed's two bad misses (ranks 106 and 16) are both queries whose target is
identified by a *domain abbreviation or product noun* ("campaign ranking", "next best
product") rather than by code structure. Gemini's worst case is milder. Neither pattern
is strong enough at n=30 to design around.

### Verdict on model choice

Since retrieval quality is a wash, **the decision should be made on cost, speed and
operational fit, not quality.** On those axes: CodeRankEmbed is free and self-hosted at
~85 min for the full corpus; Gemini is ~26× faster (~5 min) for ~$1.84 per full re-index
but adds an external dependency, an API key to manage, and per-run cost.

**Caveats that remain:** one repo, 30 queries, single ground-truth file per query, and the
labels are author-assigned from filename semantics rather than independently adjudicated.
This is enough to rule out "one model is clearly better", not enough to detect a small
true difference.

## Output location

Sidecars and benchmark artifacts now live in `temp/` at the repo root, which is
gitignored (`/temp/` in `.gitignore`). They were previously committed under
`.embed-tmp/<repo>/`; that history remains but the working copies are no longer tracked.

> `query_repos.py` derives `OUT_ROOT` from its own file location
> ([query_repos.py:11](.embed-tmp/scripts/query_repos.py#L11)), so it still looks in
> `.embed-tmp/` and will report `[skip] no sidecar found` for every repo until it is
> given the same `EMBED_OUT_ROOT` override used for the embedding runs. Not yet changed.

### Note on the committed script

Runs 3 and 4 used a scratchpad wrapper that patches only the model constructor to
inject `device=` and `max_seq_length`; `.embed-tmp/scripts/embed_repos.py` is
**unmodified**. To make these settings first-class, the script would need
`EMBED_DEVICE` / `EMBED_MAX_SEQ` env vars wired into the
`SentenceTransformer(...)` call at line 165 — not yet done, pending sign-off.
