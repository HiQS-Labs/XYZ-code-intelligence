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
| GH-11 Act 1 delivered — `xyz` package, chunkers, store, hybrid retrieval and a real round-trip, all 5 marathon phases approved, QA passed (PR #15); canonical Phases 2-5 rescoped, and the benchmark's size and shape settled from defaults into `MEASUREMENTS/BASELINE.md` (PR #16, 2026-09-07). | Phase 2 (#17): the **frozen 50** plus a disjoint 20-question dev split, every answerable question screened so its filename does not give the answer away, now including the PHP/WordPress repos. Act 1 measured dense-only ahead of hybrid+rerank on a saturated set, so the new set must actually discriminate — at least one arm has to score below R@3 = 1.000. |

## Ledger

### Queue / parked intake

- **GH-5 · int8 Quantization Benchmark on GCP Intel** — [PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md](<PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md>) — benchmark ONNX/OpenVINO int8 query-encode latency on Sapphire Rapids; rated 3/3/3/5

### In progress

- **GH-11 · Act 1 — XYZ hybrid retrieval library** — [PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md](<PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md>) — canonical Phase 0 close-out + Phase 1, delivered via marathon; PR #15 open (not merged); rated 85/60/50/30
- [XYZ Code Intelligence v0.5 — Canonical Research and Build Doc](<PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md>) — 6-phase plan to build XYZ and absorb Ask-Self; Phases 0-1 delivered, Phases 2-5 rescoped 2026-09-07 (Phase 4 deferred, Phase 5 inverted to a two-function swap); the five v0.5 research docs in the same folder are its roadmap-exempt evidence appendices.
- **GH-6 · score_retrieval.py local-only comparison mode** — [PROJECT/2-WORKING/v0.5/GH-6-LOCAL-ONLY-SCORER.md](<PROJECT/2-WORKING/v0.5/GH-6-LOCAL-ONLY-SCORER.md>) — N-arm local scoring with Gemini opt-in; unblocks GH-5 Phase 4; implemented, baseline reproduced; rated 2/2/2/1
- [FINDINGS-0.5 — Embedding Model Evaluation Findings Log](<PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md>) — running findings log for the v0.5 embedding evaluation; spans GH-2/3/4/5 rather than owning one issue.

### Completed

- No completed docs.

### Deferred

- No deferred docs.

---

*Add new work here only when a real `PROJECT/**` doc exists to own the execution detail.*
