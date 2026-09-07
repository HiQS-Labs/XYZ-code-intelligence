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

## Ephemeral GCP VMs for benchmarking

For short-lived compute — a benchmark, a one-off export, anything needing hardware we do
not own. Every identifier below is a placeholder; substitute real values at run time and
never commit them.

### 1. Scope — verify the hardware, never assume it

The instruction set is usually the whole reason for renting the machine, so check it
**before** trusting a single number:

```bash
lscpu | grep -oE 'avx512[a-z_0-9]*|vnni|amx[a-z_]*' | sort -u
```

- Pin the CPU generation by choosing a machine family that guarantees it. Families spanning
  several generations need an explicit minimum-CPU-platform flag; families that dictate the
  CPU reject that flag outright.
- Avoid families where the vendor may substitute silicon — the benchmark becomes
  unreproducible.
- **A box that looks adequate on paper often isn't.** Check RAM, swap, core count *and*
  flags. A host already running live services is disqualified regardless of specs: a
  benchmark that OOM-kills a production daemon is a far worse outcome than a slow benchmark.
- Match the OS image's Python minor version to the baseline you are comparing against, or
  you have added an interpreter confound for free.

### 2. Budget — a GCP budget is an alert, not a cap

**This is the single most misunderstood control.** A budget emails at its thresholds and
does nothing else; resources keep running and billing straight past it.

To make it a real cap:

1. Create a Pub/Sub topic and set the budget's notifications rule to publish to it.
2. Deploy a function subscribed to that topic which detaches billing from the project once
   actual spend reaches the budget.
3. Deploy it in dry-run first and confirm the logs before arming it.

Caveats worth stating plainly: billing data **lags**, so spend can overshoot before the
notification fires; detaching billing stops *everything* in the target project, so only ever
point it at a disposable one; and re-enabling requires manually re-linking a billing account.

### 3. Build — arm the teardown before starting work

Create the instance with a provider-enforced lifetime from the very first command, so a
forgotten VM cannot outlive it:

```bash
--max-run-duration=<N>h --instance-termination-action=DELETE
```

Set the cap comfortably above the expected runtime and treat it as a backstop, not the
normal exit path — if it fires mid-run it can cut off the results upload.

- **Use a dedicated, disposable project.** Deleting the project is an atomic teardown that
  destroys anything the other safeguards missed, and it makes cost attribution unambiguous.
- **Prefer on-demand over spot/preemptible for benchmarks.** Preemption mid-run leaves
  *partial* output — a half-built index scores silently worse — which is a correctness risk,
  not merely lost time. The saving is not worth an unreliable number.
- Layer independent teardowns: provider lifetime cap, an OS-level watchdog timer armed at
  boot, a normal shutdown at end of script, and an error-path trap. Each should be
  sufficient alone.
- **The error trap must upload results before shutting down.** A bare
  `trap 'shutdown -h now' ERR EXIT` combined with delete-on-termination destroys exactly the
  logs that explain the failure. Use `cleanup() { upload_results || true; shutdown -h now; }`
  — the `|| true` keeps the cost guarantee from depending on the upload succeeding.

### 4. Run — exfiltrate early and often

Copy results off **as each phase completes**, not once at the end. A run that dies at 90%
with everything still on the box yields nothing.

Capture provenance alongside the results, or the numbers cannot be audited later:
`lscpu`, a dependency freeze, every phase log, and the raw per-phase JSON — not just a
summary. A summary with no underlying data is unfalsifiable.

Design multi-arm runs so **a failing arm logs and continues** rather than aborting. Partial
results are useful; a run that dies on arm 2 of 4 is not.

### 5. Tear down — delete, do not stop

| state | ongoing cost |
|---|---|
| deleted | none |
| **stopped** | **boot disk keeps billing** — easily several dollars a month |
| custom image / snapshot retained | storage charges |
| unattached static IP | billed hourly even while unused |

"Shut down" and "delete" are not the same thing. Stopping a VM silently keeps billing its
disk, which on a small budget can quietly consume a meaningful fraction of it every month.

Verify explicitly afterwards — the instance list alone is not enough:

```bash
gcloud compute instances list --project=<PROJECT>
gcloud compute disks     list --project=<PROJECT>
gcloud compute images    list --project=<PROJECT> --no-standard-images
gcloud compute snapshots list --project=<PROJECT>
gcloud compute addresses list --project=<PROJECT>
```

All five should be empty. Record the actual runtime and cost in the benchmark write-up so
the next estimate is grounded in a measurement rather than a guess.

### 6. Credentials

Fetch secrets at run time from a secret manager; never bake them into images, startup
scripts, logs or the repo. Prefer workload identity / application-default credentials over
API keys where the service supports it — fewer artifacts to leak, and the spend then flows
through normal cloud billing where a budget can actually see it.
