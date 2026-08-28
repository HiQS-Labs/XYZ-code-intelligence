# SOP.md

Standard operating procedures for tools and models used in this repo.

## CodeRankEmbed (code embedding model)

Local venv at `.venv/` (gitignored), model weights cached in the default
HuggingFace cache (`~/.cache/huggingface`).

### Setup (already done on this machine)

```bash
uv venv .venv --python 3.11
uv pip install --python .venv sentence-transformers einops torch
```

### Usage

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("nomic-ai/CodeRankEmbed", trust_remote_code=True)

query = "Represent this query for searching relevant code: sort a list in python"
code = "def sort_list(lst):\n    return sorted(lst)"

embeddings = model.encode([query, code])  # shape: (2, 768)
```

Notes:
- Queries **must** be prefixed with `"Represent this query for searching relevant code: "`.
  Code snippets are encoded raw, no prefix.
- `trust_remote_code=True` is required (model ships custom modeling code).
- Activate the venv first: `source .venv/bin/activate`, or invoke `.venv/bin/python` directly.

### Rate limiting / throttling (batch embedding jobs)

There's no external API here, so "rate limiting" means capping local CPU/thread
usage so a batch embedding run doesn't pin all cores and starve the machine.
`.embed-tmp/scripts/embed_repos.py` applies this by default:

- `EMBED_MAX_THREADS` (default `4`) — caps `torch`/OpenMP/MKL threads.
- `EMBED_BATCH_SIZE` (default `16`) — chunks per `model.encode()` call.
- `EMBED_BATCH_SLEEP` (default `0.5`s) — pause between batches to yield the CPU.

Override via env vars, e.g. `EMBED_MAX_THREADS=2 EMBED_BATCH_SLEEP=1 .venv/bin/python ...`.
Also launch with `nice -n 10` so it stays a background-priority process (best-effort —
sandboxed/restricted shells may reject the niceness change; the script still runs).

### Memory constraints

- `EMBED_MAX_MEM_MB` (default `4096`) — memory ceiling for the process.
  - Applied as a best-effort hard cap via `RLIMIT_AS` (not fully enforced on macOS).
  - Backed by a soft RSS watchdog checked every batch, using **live** RSS from
    `psutil.Process().memory_info().rss` — not `resource.getrusage().ru_maxrss`,
    which is a lifetime high-water mark that never drops and will falsely trip
    the watchdog on every run after the first big allocation. Over cap →
    `gc.collect()` → if still over, back off (4x batch sleep); 3 consecutive
    over-cap batches → abort that repo early and save whatever was embedded so
    far, rather than risk swapping the machine.
  - Requires `psutil` in `.venv` (`uv pip install --python .venv psutil`).
- **Per-repo process isolation**: torch/transformers/tokenizers don't reliably return
  memory to the OS within one long-lived process — RSS kept climbing repo-over-repo
  even after `del` + `gc.collect()` (4GB → 6GB → 8GB..., eventually killed with exit
  137). Fixed by having the script re-exec itself once per repo
  (`python embed_repos.py --repo <name> <path>`) so each repo gets a clean process
  and the OS fully reclaims memory on exit; the RSS cap then applies per-repo instead
  of accumulating across the whole run.
- `TOKENIZERS_PARALLELISM=false` is set to stop HF tokenizers from spawning worker
  processes that leak semaphores in a tight per-batch loop.
- Always launch with `python -u` (or `PYTHONUNBUFFERED=1`) when logging to a file —
  otherwise stdout is block-buffered and progress lines won't show up until exit.

### Profiling a single-repo run

`EMBED_PROFILE=1` (default on) records per-batch RSS + CPU% + batch latency to
`.embed-tmp/<repo>/profile.csv` (columns: `batch,elapsed_s,batch_s,chunks,rss_mb,cpu_pct`),
and prints a summary line (peak/avg RSS, peak/avg CPU%, avg batch time) once the
repo finishes. `cpu_pct` is CPU% since the last sample and can exceed 100 — e.g.
~400% means all 4 of `EMBED_MAX_THREADS` are fully pegged. Use this to size
`EMBED_MAX_MEM_MB` / `EMBED_MAX_THREADS` for a machine before running the full
multi-repo batch. Run one repo directly (bypassing the dispatcher) with:
```bash
.venv/bin/python -u .embed-tmp/scripts/embed_repos.py --repo <name> <path>
```
