---
gh_issue: 6
source: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/6
title: score_retrieval.py — add local-only multi-arm comparison mode (blocks GH-5)
status: active
created: 2026-08-28
updated: 2026-08-28
owner: Noel Saw
goal: Generalise the retrieval scorer from one-local-plus-Gemini to N labelled arms with Gemini opt-in, so quantization arms can be scored locally with no API key or network.
doc_type: bugfix
effort: 2
complexity: 2
risk: 2
phases: 1
related:
  - "PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md"
  - "PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md"
context_tags: [evaluation, retrieval, scoring, quantization, tooling]
---

# GH-6 — score_retrieval.py local-only comparison mode

Capture of [issue #6](https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/6). Blocks
Phase 4 of [GH-5](GH-5-QUANTIZATION-BENCHMARK.md).

## Status

| What was just completed | What's next |
|---|---|
| Implemented N-arm scoring with lazy Gemini import; all 6 acceptance criteria verified, baseline reproduced exactly (2026-08-28). | Review/commit, then use it for GH-5 Phase 4. |

## The ask

`.embed-tmp/eval/score_retrieval.py` cannot compare two **local** models. It hardcodes a Gemini
arm and calls the API unconditionally, so it is unusable for the quantization benchmark, where
every arm is local and the VM has no Gemini key.

- `score_retrieval.py:76` — `client = genai.Client(api_key=os.environ["GEMINI_KEY"])`, unconditional
- `score_retrieval.py:86` — arm list hardcoded to exactly one local + one Gemini arm
- CLI fixed at `<queries.json> <local_dir> <gemini_dir> <out.json>`

Without `GEMINI_KEY` it raises `KeyError` **before scoring anything** — after the expensive
re-index has already run. On a paid VM that wastes the whole re-index.

Found by agy in the GH-5 plan relay review (round 1, `[Should]`).

## Acceptance criteria

1. Scoring two local index directories succeeds with `GEMINI_KEY` unset **and** `google-genai` not
   installed — so `google.genai` must be imported lazily, only when a Gemini arm is requested.
2. Generalise to **N labelled arms** (`--arm "name=dir"`), with Gemini opt-in rather than required.
3. Keep the corpus-identity assertion across arms — mismatched `chunks.jsonl` must still fail
   loudly. This guard is why the existing numbers are trustworthy.
4. Preserve metrics and output shape: MRR, R@1/3/5/10, `never_found`, `per_query`.
5. Each local arm encodes queries with **its own** model; a quantized arm's index must never be
   queried with the fp32 baseline's vectors.
6. Regression check — re-running the CodeRankEmbed vs Gemini comparison must reproduce
   **MRR 0.801 / 0.782, R@1 0.700 / 0.667** (`.embed-tmp/BENCHMARKS.md`, Run 9). A drift there
   means the scoring maths changed.

Backwards compatibility with the 4-positional-arg form is explicitly **not** required; update the
single caller and the GH-5 plan instead.

## Outcome — implemented

`.embed-tmp/eval/score_retrieval.py` rewritten around N labelled arms:

```bash
# local-only — no network, no key, package not even required
python score_retrieval.py --queries .embed-tmp/eval/queries-LTVera-Pandas.json \
    --arm "fp32=temp/LTVera-Pandas" \
    --arm "onnx-int8=temp/LTVera-Pandas-onnx" \
    --model   "onnx-int8=temp/models/coderank-onnx-int8" \
    --backend "onnx-int8=onnx" \
    --out temp/eval_quant.json

# cross-model — Gemini now opt-in rather than mandatory
GEMINI_KEY=... python score_retrieval.py --queries ... \
    --arm "CodeRankEmbed (local)=temp/LTVera-Pandas" \
    --gemini-arm "gemini-embedding-001=temp/LTVera-Pandas-gemini" --out ...
```

`--model` and `--backend` are per-arm, so each arm encodes queries with **its own** model — the
requirement that makes a quantized comparison meaningful at all.

### Acceptance verification

| # | Criterion | Result |
|---|---|---|
| 1 | Local-only run with `GEMINI_KEY` unset **and** `google.genai` unimportable | **Pass** — verified with an import blocker on `sys.meta_path`; the module is only imported inside `encode_gemini()` |
| 2 | N labelled arms, Gemini opt-in | **Pass** — 1-arm and 2-arm runs both scored |
| 3 | Corpus-identity assertion retained | **Pass** — mismatched arms fail with a named-arm error, no scoring attempted |
| 4 | Metrics and output shape preserved | **Pass** — MRR, R@1/3/5/10, `never_found`, `per_query` all unchanged |
| 5 | Each local arm uses its own model | **Pass** — per-arm `--model` / `--backend` |
| 6 | Regression: reproduce Run 9 baseline | **Pass** — exactly: **MRR 0.801 / 0.782, R@1 0.700 / 0.667, R@3 0.867 / 0.933, R@5 & R@10 0.933 / 0.967** |

Two-identical-arms control: an arm and a byte-copy of it scored identically (0.801 across both),
confirming the multi-arm path introduces no per-arm drift.

### Error paths, all verified to fail loudly with actionable messages

mismatched corpora · `--gemini-arm` without a key · `--gemini-arm` without the package ·
`--model`/`--backend` naming an unknown arm · malformed `label=value` · missing index directory ·
missing `embeddings.npy`/`chunks.jsonl` · vector/chunk count mismatch · no arms supplied.

### Not done

The GH-5 plan's Phase 4 blocker note is updated to reference the new invocation, but **no
quantized arm has been scored yet** — that needs the exports from GH-5 Phase 3, which need the
GCP box.
