#!/usr/bin/env bash
# Export CodeRankEmbed to ONNX (fp32, graph-optimised) — the GH-5 recommended
# serving config: 2.15x faster than PyTorch CPU at cosine 1.000000, i.e. the
# vectors are identical to the fp32 baseline, so quality is provably unchanged.
#
# The ~550MB artifact goes to temp/ (gitignored) — it is reproducible from this
# script in a few minutes and has no business in git history.
#
#   .embed-tmp/scripts/export_onnx.sh [OUT_DIR]
#
# Requires: .venv with optimum[onnxruntime]  (pip install "optimum[onnxruntime]" onnxruntime)
#
# NOTE ON PORTABILITY: this fp32 export is architecture-independent — ONNX Runtime
# runs it on x86_64 and arm64 alike. Only the *int8* path is x86-specific (its
# quantization config targets avx512_vnni), and int8 was rejected on quality
# anyway (R@1 0.700 -> 0.533). See .embed-tmp/BENCHMARKS.md Run 10.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="${1:-$REPO_ROOT/temp/models/coderankembed-onnx-fp32}"
MODEL="nomic-ai/CodeRankEmbed"

# ISOLATED VENV — this is not optional. `optimum-onnx` pins transformers<4.58
# while `sentence-transformers>=6` needs transformers>=5.0.0, so the exporter and
# the main .venv CANNOT share an environment. Installing the exporter into .venv
# silently downgrades transformers and breaks the embedding pipeline. Keep them
# apart; the exported artifact is version-independent once produced.
EXPORT_VENV="$REPO_ROOT/temp/.venv-onnx-export"

if [ ! -x "$EXPORT_VENV/bin/optimum-cli" ]; then
  echo "creating isolated export venv at $EXPORT_VENV"
  python3.11 -m venv "$EXPORT_VENV"
  "$EXPORT_VENV/bin/pip" install -q --upgrade pip
  # ORDER MATTERS. pip cannot resolve this set in one shot — it is deliberately
  # built up, then transformers is forced back DOWN last. Each step is load-bearing:
  #
  #   1. torch from its own index (CPU wheel ~200MB vs ~900MB with CUDA). Separate
  #      command: passing --index-url to a combined install restricts EVERY package
  #      to the pytorch server, where transformers does not exist.
  "$EXPORT_VENV/bin/pip" install -q torch --index-url https://download.pytorch.org/whl/cpu
  #   2. optimum + runtime.
  "$EXPORT_VENV/bin/pip" install -q "optimum[onnxruntime]" onnxruntime einops
  #   3. optimum>=2.3 — 2.1.x fails on this model.
  "$EXPORT_VENV/bin/pip" install -q "optimum>=2.3.0"
  #   4. sentence-transformers — REQUIRED. optimum's ST export path is the only one
  #      that handles nomic_bert; without it the export dies with "custom or
  #      unsupported architecture ... no custom_onnx_configs". Installing it drags
  #      transformers up to 5.x, which then breaks optimum's exporter
  #      (ImportError: get_parameter_dtype) — hence step 5.
  "$EXPORT_VENV/bin/pip" install -q sentence-transformers
  #   5. force transformers back to <4.58. pip warns about the conflict and installs
  #      anyway; this is the combination that actually works, and is what the GH-5
  #      benchmark host ran. Do not "fix" the warning.
  "$EXPORT_VENV/bin/pip" install -q "transformers==4.57.6"
fi

mkdir -p "$OUT_DIR"
echo "exporting $MODEL -> $OUT_DIR"

# --trust-remote-code is REQUIRED: nomic-bert ships custom modeling code.
# --task feature-extraction bakes pooling into the graph, so the exported model
# emits `sentence_embedding` directly (NOT `last_hidden_state`).
# --library sentence_transformers is REQUIRED: the plain transformers export path
# rejects nomic_bert as an unsupported architecture. The ST path handles it.
"$EXPORT_VENV/bin/optimum-cli" export onnx \
  --model "$MODEL" \
  --trust-remote-code \
  --library sentence_transformers \
  --task feature-extraction \
  "$OUT_DIR"

echo
echo "exported:"
ls -la "$OUT_DIR"
cat <<'USAGE'

Serving it — drive onnxruntime directly, NOT sentence-transformers:

    import onnxruntime as ort, numpy as np
    from transformers import AutoTokenizer

    so = ort.SessionOptions()
    so.intra_op_num_threads = 4       # pin explicitly; ORT defaults to ALL cores
    so.inter_op_num_threads = 1
    sess = ort.InferenceSession(f"{OUT_DIR}/model.onnx", sess_options=so,
                                providers=["CPUExecutionProvider"])
    tok = AutoTokenizer.from_pretrained(OUT_DIR)

    def embed(texts, is_query=False):
        if is_query:   # queries need the prefix; documents do not
            texts = ["Represent this query for searching relevant code: " + t for t in texts]
        e = tok(texts, return_tensors="np", truncation=True, max_length=2048, padding=True)
        v = sess.run(["sentence_embedding"],
                     {"input_ids": e["input_ids"].astype(np.int64),
                      "attention_mask": e["attention_mask"].astype(np.int64)})[0]
        return v / np.linalg.norm(v, axis=-1, keepdims=True)

Why not sentence-transformers: its backend="onnx" loader looks for a pre-exported
ONNX artifact in the HF repo, finds none, and falls through to nomic's custom
loader with a misleading "Model name not found". Even when pointed at a local
export it then fails at inference with KeyError: 'last_hidden_state', because this
graph emits `sentence_embedding`. Driving ORT directly avoids both and gives exact
thread control.

MEMORY WARNING: ONNX fp32 measured ~1844 MB peak RSS vs ~970 MB for PyTorch —
faster, but roughly 1.9x the memory. On a small server check RAM before adopting.
USAGE
