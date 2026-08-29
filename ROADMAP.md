<!-- PDDA ROADMAP CONTRACT — this file is a POINTER/LEDGER, not a plan body.
     Allowed: queued intake / projects in progress / completed / attempted / deferred + links to PROJECT/** docs.
     NOT allowed: phase checklists, build steps, deep execution notes — put those in the project doc.
     Carve-out: a SHORT exception note is OK only when omitting it would hide an operationally critical fact.
     Coverage rule: every PROJECT/2-WORKING doc must be reflected here by a pointer (or opt out with roadmap_exempt: true).
     Enforced by `pdda.sh roadmap` + `pdda.sh roadmap-coverage` (deterministic) + utils/pdda/pdda-doc-ready.sh ROADMAP rubric (LLM). -->

# Roadmap

> **Pointer/ledger only — not a plan body.** Execution detail (phase checklists, build steps, QA
> gates, deep notes) lives in the linked `PROJECT/**` docs; keep it there. See the contract banner above.

## Status

| What was just completed | What's next |
|---|---|
| Benchmarked CodeRankEmbed vs Gemini embeddings across 4 repos; near-parity on a 30-query labelled set (2026-08-28). | GH-5: int8 quantization benchmark on GCP Intel (Sapphire Rapids). |

## Ledger

### Queue / parked intake

- **GH-5 · int8 Quantization Benchmark on GCP Intel** — [PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md](<PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md>) — benchmark ONNX/OpenVINO int8 query-encode latency on Sapphire Rapids; rated 3/3/3/5

### In progress

- [XYZ Code Intelligence v0.5 — Canonical Research and Build Doc](<PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md>) — 6-phase plan to build XYZ and sunset Ask-Self; the five v0.5 research docs in the same folder are its roadmap-exempt evidence appendices.
- [FINDINGS-0.5 — Embedding Model Evaluation Findings Log](<PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md>) — running findings log for the v0.5 embedding evaluation; spans GH-2/3/4/5 rather than owning one issue.

### Completed

- No completed docs.

### Deferred

- No deferred docs.

---

*Add new work here only when a real `PROJECT/**` doc exists to own the execution detail.*
