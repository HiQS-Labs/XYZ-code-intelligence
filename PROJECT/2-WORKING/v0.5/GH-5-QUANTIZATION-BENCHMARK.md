---
gh_issue: 5
source: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/5
title: GH-5 — int8 Quantization Benchmark on GCP Intel (Sapphire Rapids)
status: active
created: 2026-08-28
updated: 2026-08-28
owner: Noel Saw
goal: Determine whether int8 quantization (ONNX Runtime / OpenVINO) reduces CodeRankEmbed query-encode latency enough to justify deployment complexity, measured on Intel hardware with AMX, without regressing retrieval quality.
doc_type: feedback
effort: 3
complexity: 3
risk: 3
phases: 5
related:
  - "PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md"
  - "PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md"
context_tags: [embeddings, quantization, openvino, onnx, gcp, intel, benchmarking, cost-control]
non_goals:
  - Output-vector quantization (int8/binary embeddings) — the index is ~48 MB total, so there is no storage problem to solve
  - Unsloth / bitsandbytes 4-bit — targets decoder-only LLMs on CUDA; not applicable to a BERT-style encoder on CPU
  - Choosing between CodeRankEmbed and Gemini — settled separately in FINDINGS-0.5.md (near-parity; decide on cost/ops)
  - Running any benchmark on the Vultr `sleuth-development` box — unsuitable and unsafe (see Phase 0)
---

# GH-5 — int8 Quantization Benchmark on GCP Intel (Sapphire Rapids)

Tracking issue: [#5](https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/5).
Baseline measurements and the failure history this builds on are in
[FINDINGS-0.5.md](FINDINGS-0.5.md).

## Status

| What was just completed | What's next |
|---|---|
| Plan authored; Vultr box ruled out on specs; GCP `c3-standard-4` selected (2026-08-28). | Phase 1: provision the VM with all teardown safeguards armed and verify CPU flags. |

## Table of contents

- [Phase 0 — Hardware decision (complete)](#phase-0--hardware-decision-complete)
- [Phase 1 — Provision with teardown safeguards](#phase-1--provision-with-teardown-safeguards)
- [Phase 2 — Environment parity](#phase-2--environment-parity)
- [Phase 3 — Latency benchmark (all arms, no re-indexing)](#phase-3--latency-benchmark-all-arms-no-re-indexing)
- [Phase 4 — Quality validation (surviving arms only)](#phase-4--quality-validation-surviving-arms-only)
- [Teardown safeguards](#teardown-safeguards)
- [Baseline reference numbers](#baseline-reference-numbers)

---

## Phase 0 — Hardware decision (complete)

**This is a discovery phase; its findings are written back here per the PDDA memory-injection
contract.**

### Finding: the Vultr `sleuth-development` box cannot be used

Probed read-only. Three independent blockers:

| | |
|---|---|
| CPU | Intel Broadwell, **1 vCPU** |
| Instruction set | **AVX2 only — no AVX-512, no VNNI, no AMX** |
| RAM | **954 MB total, 411 MB available** |
| Swap | **none** |
| Co-resident services | `sleuth-app.service` (live dev app), GitHub Actions runner, node |

1. **Insufficient memory, dangerously so.** Model weights alone are 522 MB and measured peak
   RSS while *querying* is 579 MB, against 411 MB available with zero swap. Indexing peaks at
   ~2,475 MB. The OOM killer would fire and the likely victims are the live dev app and the CI
   runner. **Do not benchmark on this box.**
2. **The OpenVINO upside does not exist there.** The int8 speedup depends on AVX-512 VNNI
   (Cascade Lake+) or AMX (Sapphire Rapids+). Broadwell has neither, so results would understate
   modern Intel and mislead the decision.
3. **1 vCPU** vs the 4-thread baseline — not comparable without re-baselining.

### Decision: GCP `c3-standard-4`

4 vCPU / 16 GB, **guaranteed Intel Sapphire Rapids**, so both AMX and AVX-512 VNNI are present
and no `--min-cpu-platform` pin is needed (C3 dictates the CPU; the flag is rejected on families
that already do).

Rejected alternatives: `n2` (Cascade/Ice Lake — VNNI but no AMX, and needs a platform pin);
`n2d`/`c2d`/`c3d` (AMD EPYC — note Zen 4 *does* have AVX-512 VNNI, but OpenVINO's kernels are
Intel-tuned and AMX is Intel-only); `e2` (CPU platform not pinnable, benchmarks meaningless);
`n1` (Haswell/Broadwell/Skylake — no VNNI).

**Image: Debian 12, not Ubuntu 24.04.** Debian 12 ships Python 3.11, matching the local baseline
venv (3.11.15). Ubuntu 24.04 ships 3.12, which would introduce an interpreter confound into the
Phase 4 quality comparison for no benefit.

**Estimated cost: ~$1.28 all-in** for a 6-hour window (VM ~$0.20/hr, 50 GB balanced PD, external
IP). Expected actual runtime is ~1.5–3 hours. **On-demand, not Spot** — preemption mid-run would
leave a partially built index that scores silently worse, which is a correctness risk, not just
lost time.

**QA gate (met):** hardware selected with an explicit instruction-set requirement, the rejected
options recorded with reasons, and the unsafe option documented so nobody retries it.

---

## Phase 1 — Provision with teardown safeguards

Provision the VM with **every safeguard armed before any work starts**. See
[Teardown safeguards](#teardown-safeguards) for the full defence-in-depth list and rationale.

1. Create the instance with a GCP-enforced maximum lifetime.
2. Immediately verify the CPU actually has the instructions the whole experiment depends on:

   ```bash
   lscpu | grep -oE 'avx512[a-z_]*|vnni|amx[a-z_]*' | sort -u
   ```

   Expect `amx_bf16`, `amx_int8`, `amx_tile`, `avx512_vnni`.

3. Confirm the independent watchdog timer is running (`systemctl list-timers`).

**QA gate:** `amx_int8` **and** `avx512_vnni` both present; `--max-run-duration` confirmed on the
instance; watchdog timer listed. **If `amx_int8` is absent, stop and destroy the VM** — the run
would not be representative and must not be reported as an Intel result.

---

## Phase 2 — Environment parity

Install a venv matching the local baseline as closely as possible, plus the export backends.

- Python 3.11 (Debian 12 default), `torch`, `sentence-transformers`, `psutil`
- `sentence-transformers[onnx]` and `sentence-transformers[openvino]`

Export and quantization run through Hugging Face `optimum` under the hood —
`optimum[onnxruntime]` and `optimum-intel[openvino]` + `nncf`. Either use the export helpers
directly or load via `SentenceTransformer(..., backend="onnx"|"openvino")`. **`nomic-bert` ships
custom modeling code (`trust_remote_code=True`), so the exporter may need explicit Optimum CLI
flags** — this is the most likely place the export fails.

Record exact versions of `torch`, `sentence-transformers`, `onnxruntime`, `openvino`, `optimum`
and `nncf` into the results manifest. Version drift against the local baseline is a legitimate
confound and must be visible in the write-up rather than discovered later.

### Thread pinning — mandatory for a fair comparison

The fp32 baseline was measured at **4 threads** (`torch.set_num_threads(4)`, `OMP_NUM_THREADS=4`).
The other backends **do not** inherit that and default to all detected cores:

| backend | pin |
|---|---|
| PyTorch | `torch.set_num_threads(4)` |
| ONNX Runtime | `SessionOptions.intra_op_num_threads = 4` |
| OpenVINO | `INFERENCE_NUM_THREADS = 4` in core properties |

Left unpinned, an int8 arm silently using more threads than the baseline would report a speedup
that is partly just extra parallelism — a fabricated result, and one that would look plausible.
**Log the effective thread count per arm** so the pin is evidenced, not assumed.

**QA gate:** fp32 PyTorch CPU smoke test reproduces the documented sanity check — `encode([query,
code])` returns shape `(2, 768)` and cosine ≈ 0.771 for the SOP's sample pair; **and** every arm's
recorded thread count is 4. If the smoke test does not reproduce, the environment differs
materially and later numbers are not comparable.

---

## Phase 3 — Latency benchmark (all arms, no re-indexing)

**Key efficiency: latency does not require a re-index.** Encoding a query is independent of what
is stored in the index, so all arms can be timed against the existing fp32 sidecars.

> **Quality numbers from this phase are invalid and must not be recorded.** A quantized query
> vector compared against an fp32 document index measures nothing — the spaces differ. Only
> latency is meaningful here.

Arms:

| arm | export function |
|---|---|
| `baseline` | PyTorch fp32 CPU (no export) |
| `onnx-fp32` | `export_optimized_onnx_model` — isolates graph optimisation from quantization |
| `onnx-int8` | `export_dynamic_quantized_onnx_model` — no calibration data needed |
| `openvino-int8` | `export_static_quantized_openvino_model` — **static**, needs calibration data (see below) |

**Calibration data must match the inference distribution.** The thing being optimised is *query*
encoding: short strings of roughly 10–30 tokens carrying the
`"Represent this query for searching relevant code: "` prefix. Code chunks in `chunks.jsonl` are
hundreds of tokens with a different token distribution, so calibrating on chunks alone would tune
activation scale factors for the wrong workload and understate what int8 can do at query time.
Calibrate on **prefixed queries, or a balanced mix of queries and chunks** — and record which was
used, since it materially affects the result.

Per arm record: export wall time, model load time, query-encode mean / p50 / p95 over ≥50 queries
after warmup, and peak RSS.

**A failed arm must not abort the run.** Log the failure, continue to the next arm. ONNX export of
a `trust_remote_code` model (nomic-bert ships custom modeling code) is the single most likely
failure point in this plan — custom ops are exactly what breaks ONNX export. A partial result set
is still useful.

**QA gate:** ≥2 arms produce latency numbers (baseline plus at least one export), results written
to disk, and the **>2× speedup gate** evaluated. If no arm beats baseline by >2×, **stop here** —
end-to-end query time is already ~45 ms and interactive, so marginal gains do not justify the
added deployment complexity. Record the negative result; it is a valid outcome.

---

## Phase 4 — Quality validation (surviving arms only)

Only for arms that cleared the Phase 3 gate.

1. **Re-embed a repo with that arm's exact model.** Mandatory — this is the step that makes the
   quality comparison meaningful, and skipping it produces plausible-looking garbage.
2. Score against `.embed-tmp/eval/queries-LTVera-Pandas.json`.
3. Compare against the fp32 baseline.

> **Blocker CLEARED** ([GH-6](GH-6-LOCAL-ONLY-SCORER.md), issue
> [#6](https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/6)). The scorer previously called
> Gemini unconditionally and would have `KeyError`d on the VM *after* the expensive re-index. It
> now takes N labelled arms with Gemini opt-in and a lazy import, so a local-only run needs no key
> and not even the package. The Run 9 baseline was reproduced exactly after the change.

Invocation for a quantized arm — note `--model`/`--backend` are per-arm, so each arm encodes
queries with **its own** model:

```bash
python .embed-tmp/eval/score_retrieval.py \
    --queries .embed-tmp/eval/queries-LTVera-Pandas.json \
    --arm  "fp32=temp/LTVera-Pandas" \
    --arm  "onnx-int8=temp/LTVera-Pandas-onnx-int8" \
    --model   "onnx-int8=<exported model dir>" \
    --backend "onnx-int8=onnx" \
    --threads 4 \
    --out temp/eval_quant.json
```

`--threads 4` keeps the scorer's own query encoding on the same 4-thread footing as the
[thread-pinning requirement](#thread-pinning--mandatory-for-a-fair-comparison) above.

**Corpus choice.** The labelled query set targets `LTVera-Pandas` (5,147 chunks). Either re-index
that repo, or build a matching labelled set for the smaller `aegis-sleuth-slack-bot` (3,226
chunks) first. Do **not** score LTVera queries against an AEGIS index.

**The fp32 baseline index does not need rebuilding** — MPS and CPU were verified to produce
identical vectors (cosine 1.000000, max abs diff 7.2e-06), so the existing sidecars are a valid
baseline arm.

**QA gate:** MRR and R@1/3/5/10 recorded for each surviving arm against the baseline. Accept an
arm only if the latency win holds **and** quality regression is within noise. At n=30 a single
query moves R@1 by 0.033, so treat any delta under ~0.05 as unresolvable — in either direction.
Findings written back into this doc and into [FINDINGS-0.5.md](FINDINGS-0.5.md).

---

## Teardown safeguards

The failure mode here is not expense — it is a forgotten VM billing for weeks. **Six independent
layers**, each of which alone is sufficient:

1. **GCP-enforced maximum lifetime.** At creation:
   `--max-run-duration=4h --instance-termination-action=DELETE`. Enforced by GCP, independent of
   anything running on the box. Verify the flags are accepted by the installed `gcloud` version;
   if not, fall back to layer 2 plus a calendar reminder and note the gap.
2. **Independent watchdog timer**, armed at boot and independent of the benchmark script:
   `sudo systemd-run --on-active=4h shutdown -h now`. Survives the script crashing outright.
3. **Normal completion path.** The runner script ends with `shutdown -h now`.
4. **Error path.** A shell `trap` on `EXIT`/`ERR` shuts down even on an unhandled failure, so a
   crash at step 2 of 40 does not leave the box idling.
   **The trap must upload logs and partial results BEFORE calling `shutdown`.** A bare
   `trap 'shutdown -h now' ERR EXIT` combined with `--instance-termination-action=DELETE`
   destroys the tracebacks, arm logs and partial results that explain *why* it failed — leaving a
   deleted VM and no diagnosis. The crash path is precisely when those logs matter most. Correct
   shape:

   ```bash
   cleanup() { upload_results || true; shutdown -h now; }
   trap cleanup EXIT ERR
   ```

   `|| true` so a failed upload still shuts the box down — the cost guarantee must not depend on
   the upload succeeding.
5. **Results shipped off-box before shutdown.** Upload to GCS (or `scp`) *before* any teardown,
   so self-deletion can never destroy the findings. **Ordering matters: upload, verify, then
   shut down.** This applies to the success path *and* the error path in layer 4.
6. **Manual verification.** After the expected window, confirm nothing survives:
   `gcloud compute instances list --filter="name~benchmark"`. Plus a project **budget alert** as
   the backstop that catches every case the above miss.

**Interaction to respect:** layers 1 and 3–4 can race. If the script finishes at 3h58m while the
max-run-duration fires at 4h00m, the upload may be cut off. Keep `--max-run-duration` comfortably
above the expected runtime (4h against an expected 1.5–3h), and treat layer 1 as a backstop rather
than the normal exit path.

---

## Baseline reference numbers

Measured locally (Apple M4 Pro, 24 GB) — full detail in `.embed-tmp/BENCHMARKS.md`.

| | value |
|---|---|
| Query encode (CPU, 4 threads) | **44.0 ms** mean, p50 41.6, p95 53.8 |
| Vector search (brute force) | 1.5 ms mean |
| End-to-end per query | **45.4 ms** |
| Peak RSS while querying | **579 MB** |
| Model | 136.7M params, fp32, **522 MB** |
| Index size | 2.9 MB per 1,000 chunks (~48 MB for all four repos) |
| Retrieval baseline | **MRR 0.801, R@1 0.700, R@3 0.867, R@5 0.933, R@10 0.933** |

Model config for every arm: `max_seq_length=2048`, 768 dims. The sequence cap is **mandatory** —
uncapped, one long chunk inflates a batch to ~51 GB of attention and the process is OOM-killed
regardless of backend.
