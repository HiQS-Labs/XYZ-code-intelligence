# Agy prompt — LTVera-Pandas with Gemini Embeddings + cost telemetry

> **STATUS: superseded — this run has since been executed directly.** Results,
> costs and the head-to-head against CodeRankEmbed are in `BENCHMARKS.md` (Run 6).
> Kept for reuse on the other three repos. Two corrections learned from the real run:
> `gemini-embedding-2` **does not support `task_type`** (it takes in-prompt task
> prefixes instead), so the `task_type` instruction below applies only to
> `gemini-embedding-001`; and `embed_content` returns **no usage metadata**, so
> tokens must be counted via the separate `countTokens` endpoint, per chunk —
> counting a list does not equal the sum of its per-item counts.

Paste the block below to Agy. It is written to be self-contained.

---

## Task

Embed the **LTVera-Pandas** repo with **Google Gemini embeddings** and produce sidecar
files plus full **cost telemetry in USD**. This is a head-to-head against a local
CodeRankEmbed run we have already completed, so **the chunking must match exactly** or
the comparison is meaningless.

Repo to embed: `/Users/noelsaw/Documents/GitHub Repos/LTVera-Pandas`

### 1. Credentials — GCloud Secrets Manager

Authenticate using the **LTVera-Pandas billing account**, with the credential pulled
from **GCloud Secret Manager** — do not hardcode a key, do not read one from a shell
profile, and do not write the secret value into any output file, log, or commit.

- Discover the correct secret rather than guessing: `gcloud secrets list --project <project>`.
- Confirm which GCP project is attached to the LTVera-Pandas billing account before
  spending anything: `gcloud billing projects list --billing-account <account-id>`.
- Fetch at run time, e.g.
  `gcloud secrets versions access latest --secret=<name> --project=<project>`.
- If more than one candidate secret or project exists, **stop and ask** — do not guess
  which billing account gets charged.
- Echo which project/secret name (not value) you used into the run log for auditability.

### 2. Chunking — must be byte-identical to the existing run

Do **not** write your own chunker. Import and reuse the functions from
`/Users/noelsaw/Documents/GitHub Repos/XYZ-code-intelligence/.embed-tmp/scripts/embed_repos.py`:

- `iter_files(root)` — file selection (`INCLUDE_EXT`, `EXCLUDE_DIR_PARTS`, 400 KB cap)
- `chunk_file(path, root)` — 60-line windows, 15-line overlap, min 20 chars body

Expected result, which you should assert before spending any money:
**819 files → 5,147 chunks.** If your count differs, stop and report — something has
drifted and the comparison is invalid.

### 3. Embedding

- Use the current recommended Gemini embedding model (likely `gemini-embedding-001`) —
  **confirm the current model name and status in the live docs first**; do not assume.
- Set `task_type` correctly. This is the Gemini analogue of CodeRankEmbed's query prefix
  and it materially changes retrieval quality:
  - stored chunks → `RETRIEVAL_DOCUMENT`
  - test queries → `RETRIEVAL_QUERY`
- Record the `output_dimensionality` you use. Gemini defaults higher than CodeRankEmbed's
  768; note that dimensions differ between the two indexes, so compare *ranking quality*,
  never raw cosine values across models.
- Gemini's embedding input limit is ~2,048 tokens per chunk, which happens to match the
  `max_seq_length=2048` cap the local run used — so truncation behaviour is comparable.
  Log how many chunks get truncated.
- Batch requests, and implement retry with exponential backoff on 429/5xx. Log any
  request that is retried or dropped; **never silently skip a chunk.**

### 4. Output

Write to `/Users/noelsaw/Documents/GitHub Repos/XYZ-code-intelligence/temp/LTVera-Pandas-gemini/`
(the `temp/` directory is gitignored — keep it that way; do not commit embeddings):

- `chunks.jsonl` — same schema as the local run: `{id, repo, path, start_line, end_line, text}`
- `embeddings.npy` — float32, row order matching `chunks.jsonl`
- `costs.csv` — per batch: `batch,chunks,input_tokens,usd_cost,cumulative_usd,latency_s,retries`
- `cost_summary.json` — see below
- `run.log`

### 5. Cost telemetry (this is a first-class deliverable, not an afterthought)

`cost_summary.json` must contain:

- `model`, `output_dimensionality`, `task_type`
- `gcp_project`, `billing_account_id`, `secret_name` (name only, never the value)
- `total_chunks`, `total_input_tokens`, `chunks_truncated`
- `unit_price_usd_per_1m_input_tokens` — **look this up from Google's live pricing page
  and record `price_source_url` and the date you read it.** Do not hardcode a
  remembered figure; embedding prices change and a stale number makes the whole
  telemetry exercise worthless.
- `total_cost_usd` — computed, showing the arithmetic in the log
- `cost_per_1k_chunks_usd` — normalised so it can be compared against other repos
- `projected_cost_all_four_repos_usd` — extrapolate using 16,433 total chunks across
  `aegis-sleuth-slack-bot` (3,226), `XYZ-forge` (3,949), `rebalanceOS` (4,111),
  `LTVera-Pandas` (5,147)
- `wall_time_s`, `api_calls`, `retries`

Prefer **billed token counts reported by the API** over your own estimate. If the
embedding response does not return usage metadata, count via the official token-counting
endpoint and clearly label the figure as estimated in the summary.

### 6. Test queries

Run these three (the same ones used for LTVera-Pandas locally) with
`task_type=RETRIEVAL_QUERY`, print top-3 hits with score, path, line range and a snippet,
and save to `query_results_gemini.json`:

1. `alembic database migration script`
2. `docker compose service configuration`
3. `pipeline that processes a pandas dataframe`

### 7. Report back

- The cost summary numbers above, with the pricing source you used.
- Wall time and API call count vs. the local baseline below.
- Your read on whether the top-3 hits look semantically relevant or off-base, per query.
- Anything that would make the comparison unfair (truncation counts, dropped chunks,
  model version surprises).

### Local baseline for comparison (already measured, Apple M4 Pro, 24 GB)

CodeRankEmbed `nomic-ai/CodeRankEmbed`, 768-dim, `max_seq_length=2048`, batch 16, MPS backend.
Local inference has **no API cost** — the comparison is dollars-and-latency vs. retrieval
quality.

| | CodeRankEmbed (local, MPS) |
|---|---|
| **LTVera-Pandas — 5,147 chunks** | **1,529.9 s (25.5 min) — 0.297 s/chunk** |
| aegis-sleuth-slack-bot (3,226 chunks) | 1,054.5 s (17.6 min) — 0.327 s/chunk |
| Peak RSS / avg host CPU (LTVera run) | 814 MB / 15 % |
| API cost | **$0.00** (local inference) |

So the bar for LTVera-Pandas is **25.5 minutes and zero dollars**. Report Gemini's
wall time and cost against that, and be explicit about whether any speed advantage
is worth the spend given the retrieval quality you observe.

Full details and the failure history are in
`/Users/noelsaw/Documents/GitHub Repos/XYZ-code-intelligence/.embed-tmp/BENCHMARKS.md`.
