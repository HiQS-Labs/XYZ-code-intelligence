# RELAY · GH-5 int8 quantization benchmark plan review
<!--
  Single source of truth for this two-agent relay. Read the ENTIRE file before acting.
  Scaffolded by relay-automation/new-relay.sh on 2026-08-28.
-->

NEXT: Producer
STATUS: Open
ROUND: 1 / 4

## ▶ TAKE YOUR TURN — read this first (works for ANY agent: Claude, Codex, agy)
1. **Read this whole file** (header, Setup, Ground rules, every block in the Log).
2. **Check it's your turn:** `NEXT` (top) names the role to act. Confirm you are bound to it and the
   last Log block isn't already yours. If not → STOP and reply "wrong window — nudge the <other> window."
3. **Do your role's work** on the artifact named in Setup:
   - **Reviewer:** review vs the Definition of Done → graded findings
     (`[Blocker]`/`[Should]`/`[Nit]`/`[Pass]`), each with a concrete fix → set a **Verdict**
     (Approved | Changes requested | Blocked). **Review the whole file, not just the diff** (GH-268):
     a beta test had this loop reach `Approved` in two rounds while an independent audit of the same
     branch found 20 issues (1 critical, 4 high) — every one of them in the pre-existing code the
     change sat on, which nobody had read. Pre-existing defects in a file you are touching are IN
     SCOPE; if you find none, say so explicitly rather than leaving it unstated.
     **Declare it: every review block must contain a literal `swept file: yes` or `swept file: no`
     line.** Without it a reviewer that skipped the sweep is indistinguishable in the transcript from
     one that did it and found nothing — which is how the original 20 issues stayed invisible.
     Any `[Pass]` or "verified"/"confirmed" finding MUST
     carry a quoted span or a `file:line` citation — an uncited one is mechanically downgraded to
     `[Unverified — no citation]` (GH-173 B3). Do **not** edit the artifact; only append findings here.
   - **Producer:** log a disposition for every open finding (Implemented / Modified / Declined + why),
     make the change, then add new work.
4. **Append ONE block** at the very bottom, directly **above** the marker line. Never edit earlier turns.
5. **Update the header:** flip `NEXT`; set `STATUS` (`Approved` closes — Reviewer only; else `Open`);
   the Producer bumps `ROUND` when opening a new cycle. If the max `ROUND` ends without `Approved`,
   set `STATUS: Escalated`.
6. **Commit only the relay file** (`relay(gh5-quantization-plan-review): <role> r<N>`); no push. **Stop** and report one line.
7. **Hand off explicitly — EVERY turn, not just the first** (GH-268). End your turn by naming who acts
   next and what they should do: *"handing off to <other role> — go to the <other> window and say
   'take your turn'"*, or *"relay closed (Approved), no further turn needed"*. The beta report singled
   this out: the Reviewer turn never told the user to return to the Producer window, so a relay that
   was merely waiting looked stalled. A turn that ends without this line is not finished.

## Setup
- Artifact under review: **.relay-artifacts/GH-5-QUANTIZATION-BENCHMARK.md** — the read-only path that
  `relay-drive.sh --artifact-file PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md` seeds into the isolated worktree (read it there; do NOT edit it).
- Reviewer: agy   ·   Producer: claude-a
- Started: 2026-08-28
- Definition of Done: Comprehensive, execution-ready GCP int8 quantization benchmarking and quality validation plan with CPU feature verification, 6-layer teardown safeguards, decoupled retrieval scoring, backend runtime thread pinning, and calibrated static quantization.

## Ground rules
1. This file is the single source of truth. The agents never share memory — read the whole file.
2. Take a turn only if `NEXT` names your role — otherwise reply "not my turn" and stop.
3. One turn = one block appended at the very bottom, above the marker. Never edit earlier turns.
4. Stay tight — findings are bullets, not essays. Grade every finding.
5. **The Reviewer never edits the artifact.** It proposes graded findings; the Producer implements.
6. The relay ends on **Approved** (Reviewer only). End each turn by committing just this file; no push.

## Log

### Reviewer · Round 1 · agy

swept file: yes

VERDICT: FAIL
Basis: The benchmark plan is structurally thorough and has exceptional teardown safeguards, but requires 4 targeted changes before VM execution: decoupling score_retrieval.py from the Gemini API, ensuring crash-path error traps exfiltrate logs before self-termination, pinning thread runtime configs for ONNX/OpenVINO to ensure 4-vCPU parity, and including query samples in OpenVINO static calibration.

#### Findings

- [Should] Decouple retrieval quality scoring script from Google Gemini API dependency
  - Citation: `PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md:179-180` ("Score with `.embed-tmp/eval/score_retrieval.py` against `.embed-tmp/eval/queries-LTVera-Pandas.json`.")
  - Problem: `.embed-tmp/eval/score_retrieval.py:7-8, 76-84` hardcodes an external call to `gemini-embedding-001` and requires `os.environ["GEMINI_KEY"]`. When scoring candidate quantized CodeRankEmbed models on the GCP VM (or offline) against the local fp32 baseline, `score_retrieval.py` will fail if `GEMINI_KEY` is missing or if two local index directories are passed without Gemini.
  - Concrete Fix: Update Phase 4 to specify a direct local-comparison mode (e.g. comparing the candidate quantized embedding directory directly against the baseline `.embed-tmp/LTVera-Pandas/` embeddings and queries) without requiring Gemini API calls or keys on the benchmark VM.

- [Should] Ensure Error Trap exfiltrates diagnostic logs to GCS/remote before triggering VM shutdown
  - Citation: `PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md:210-212` ("4. Error path. A shell `trap` on `EXIT`/`ERR` shuts down even on an unhandled failure, so a crash at step 2 of 40 does not leave the box idling.")
  - Problem: If an unhandled failure occurs early in execution and the shell trap immediately issues `shutdown -h now`, all error traces, traceback outputs, and `.relay-scratch/` logs on the instance will be lost when `--instance-termination-action=DELETE` destroys the VM.
  - Concrete Fix: Update Teardown Safeguard #4 and Phase 1 to explicitly require that the `trap ... ERR EXIT` handler runs the GCS/scp log-upload routine before calling `shutdown -h now`.

- [Should] Explicitly specify runtime thread pinning for ONNX Runtime and OpenVINO backends
  - Citation: `PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md:158-159` ("Per arm record: export wall time, model load time, query-encode mean / p50 / p95 over ≥50 queries after warmup, and peak RSS.")
  - Problem: While PyTorch CPU uses `torch.set_num_threads(4)` and `OMP_NUM_THREADS=4`, ONNX Runtime (`InferenceSession`) defaults to all detected threads unless `intra_op_num_threads=4` is configured in `SessionOptions`, and OpenVINO defaults to its internal thread pool unless `INFERENCE_NUM_THREADS=4` is set in core properties. Unpinned backends could use varying thread counts, invalidating fair CPU latency comparisons against the 4-thread baseline.
  - Concrete Fix: Add explicit runtime configuration instructions in Phase 2 / Phase 3 specifying `intra_op_num_threads=4` for ONNX Runtime and `INFERENCE_NUM_THREADS=4` for OpenVINO.

- [Should] Calibrate OpenVINO static quantization using query distributions rather than code chunks alone
  - Citation: `PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md:156` ("`openvino-int8` | `export_static_quantized_openvino_model` — static, needs calibration data; sample from an existing `chunks.jsonl`")
  - Problem: The primary objective is query-encode latency and quality (short prompt-prefixed strings, ~10–30 tokens). Code chunks in `chunks.jsonl` have very different sequence lengths (~60 lines, hundreds of tokens) and token distributions. Calibrating static quantization solely on code chunks risks calibrating activation scale factors suboptimal for query encoding.
  - Concrete Fix: In Phase 3, specify that calibration data for static quantization must sample representative search queries (with `"Represent this query for searching relevant code: "` prefix) or a balanced mix of queries and code chunks.

- [Nit] Clarify Optimum / Optimum-Intel library tooling for export functions
  - Citation: `PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md:128, 151-157` ("`sentence-transformers[onnx]` and `sentence-transformers[openvino]`")
  - Note: Clarify in Phase 2 that model export and quantization will leverage Hugging Face `optimum` (`optimum[onnxruntime]`, `optimum-intel[openvino]`, `nncf`) or `SentenceTransformer(..., backend="onnx"|"openvino")`, noting that custom `nomic-bert` modeling (`trust_remote_code=True`) may require Optimum CLI / exporter flags.

- [Pass] Verified hardware decision: GCP `c3-standard-4` matches Sapphire Rapids instruction set requirements
  - Citation: `PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md:78-80` ("4 vCPU / 16 GB, guaranteed Intel Sapphire Rapids, so both AMX and AVX-512 VNNI are present and no `--min-cpu-platform` pin is needed")
  - Verified: Provides AMX (`amx_int8`, `amx_tile`) and AVX-512 VNNI with 16 GB RAM, well above the 2.5 GB peak indexing RSS.

- [Pass] Verified multi-layered teardown defense-in-depth and race-condition buffer
  - Citation: `PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md:200-222` ("Six independent layers, each of which alone is sufficient... Keep `--max-run-duration` comfortably above the expected runtime (4h against an expected 1.5–3h)")
  - Verified: GCP max-run-duration (4h), systemd watchdog, normal exit, error trap, pre-shutdown upload, and budget alert provide robust cost protection.

- [Pass] Verified decoupled latency gating before expensive corpus re-indexing
  - Citation: `PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md:142-143, 167-169` ("Key efficiency: latency does not require a re-index... If no arm beats baseline by >2×, stop here")
  - Verified: Avoids unnecessary repo re-embedding if neither ONNX nor OpenVINO achieves the >2× speedup hurdle.

- [Pass] Verified mandatory sequence length cap to prevent quadratic attention OOM
  - Citation: `PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md:240-242` ("Model config for every arm: `max_seq_length=2048`, 768 dims. The sequence cap is mandatory — uncapped, one long chunk inflates a batch to ~51 GB of attention and the process is OOM-killed regardless of backend.")
  - Verified: Enforcing `max_seq_length=2048` is consistent across all baseline scripts and prevents OOM crashes.

handing off to Producer (claude-a) — go to the claude-a window and say 'take your turn'

<!-- ↓↓↓ NEXT TURN goes here (append above nothing — this marker stays last) ↓↓↓ -->

