"""Score embedding models on a labelled retrieval set.

Compares N labelled "arms", each an index directory (embeddings.npy + chunks.jsonl).
Every arm must be built from an identical chunks.jsonl so row i is the same chunk in
all of them; that is asserted before scoring. Reports MRR and recall@k.

Gemini is an OPT-IN arm, not a requirement: `google.genai` is imported lazily and only
when a --gemini-arm is requested, so local-only runs work on a machine with no API key
and without the package installed at all (GH-6).

Each local arm encodes the queries with ITS OWN model — a quantized arm's index must
never be queried with another arm's vectors, or the comparison is meaningless.

Examples:

  # local-only: fp32 baseline vs a quantized arm — no network, no key
  python score_retrieval.py --queries eval/queries-LTVera-Pandas.json \
      --arm  "fp32=temp/LTVera-Pandas" \
      --arm  "onnx-int8=temp/LTVera-Pandas-onnx" \
      --model   "onnx-int8=temp/models/coderank-onnx-int8" \
      --backend "onnx-int8=onnx" \
      --out temp/eval_quant.json

  # cross-model: local vs Gemini (needs GEMINI_KEY)
  GEMINI_KEY=... python score_retrieval.py --queries eval/queries-LTVera-Pandas.json \
      --arm "CodeRankEmbed (local)=temp/LTVera-Pandas" \
      --gemini-arm "gemini-embedding-001=temp/LTVera-Pandas-gemini" \
      --out temp/eval_LTVera-Pandas.json
"""
import argparse
import functools
import json
import os
import sys
from pathlib import Path

import numpy as np

print = functools.partial(print, flush=True)

KS = (1, 3, 5, 10)
QUERY_PREFIX = "Represent this query for searching relevant code: "
DEFAULT_MODEL = "nomic-ai/CodeRankEmbed"
DEFAULT_GEMINI_MODEL = "gemini-embedding-001"


def kv(pairs, what):
    """Parse repeatable `label=value` options into an ordered dict."""
    out = {}
    for raw in pairs or []:
        if "=" not in raw:
            sys.exit(f"score_retrieval: --{what} expects 'label=value', got {raw!r}")
        label, value = raw.split("=", 1)
        label, value = label.strip(), value.strip()
        if not label or not value:
            sys.exit(f"score_retrieval: --{what} has an empty label or value: {raw!r}")
        if label in out:
            sys.exit(f"score_retrieval: duplicate label {label!r} for --{what}")
        out[label] = value
    return out


def load_index(d: Path, label: str):
    if not d.is_dir():
        sys.exit(f"score_retrieval: arm {label!r}: no such directory {d}")
    for f in ("embeddings.npy", "chunks.jsonl"):
        if not (d / f).exists():
            sys.exit(f"score_retrieval: arm {label!r}: missing {f} in {d}")
    emb = np.load(d / "embeddings.npy").astype(np.float32)
    chunks = [json.loads(l) for l in open(d / "chunks.jsonl", encoding="utf-8")]
    if emb.shape[0] != len(chunks):
        sys.exit(f"score_retrieval: arm {label!r}: {emb.shape[0]} vectors vs "
                 f"{len(chunks)} chunks — index is inconsistent")
    return emb / np.linalg.norm(emb, axis=1, keepdims=True), chunks


def encode_local(queries, model_ref, backend, device, threads, max_seq, use_prefix):
    """Encode queries with a local sentence-transformers model."""
    import torch
    torch.set_num_threads(threads)
    from sentence_transformers import SentenceTransformer

    kwargs = {"trust_remote_code": True, "device": device}
    if backend and backend != "torch":
        # ONNX / OpenVINO runtimes default to ALL cores; the caller is responsible for
        # pinning them (see GH-5), but record what we asked for.
        kwargs["backend"] = backend
    model = SentenceTransformer(model_ref, **kwargs)
    model.max_seq_length = max_seq
    texts = [(QUERY_PREFIX if use_prefix else "") + q["q"] for q in queries]
    v = model.encode(texts, convert_to_numpy=True)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def encode_gemini(queries, model_ref, dims, vertex_project=None, vertex_location=None):
    """Encode queries with Gemini, via Vertex AI or the Developer API.

    Imported lazily — never touched unless a --gemini-arm was requested, so
    local-only runs need no key and no package.

    Vertex (--vertex-project) authenticates with ADC and bills through the
    project's Cloud Billing account, so its spend lands under any Cloud Billing
    budget. The Developer API key path bills through AI Studio's separate prepay
    pool instead, which a Cloud Billing budget does not cover.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        sys.exit("score_retrieval: a --gemini-arm was requested but google-genai is not "
                 "installed. Install it, or drop the --gemini-arm for a local-only run.")

    if vertex_project:
        client = genai.Client(vertexai=True, project=vertex_project,
                              location=vertex_location or "us-central1")
    else:
        key = os.environ.get("GEMINI_KEY")
        if not key:
            sys.exit("score_retrieval: a --gemini-arm was requested but GEMINI_KEY is unset. "
                     "Set it, pass --vertex-project to use Vertex AI with ADC instead, or "
                     "drop the --gemini-arm for a local-only run.")
        client = genai.Client(api_key=key)
    r = client.models.embed_content(
        model=model_ref,
        contents=[q["q"] for q in queries],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY",
                                        output_dimensionality=dims),
    )
    v = np.asarray([e.values for e in r.embeddings], dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def rank_of_first_relevant(sims, chunks, relevant):
    order = np.argsort(-sims)
    for rank, i in enumerate(order, start=1):
        if chunks[i]["path"] in relevant:
            return rank, i
    return None, None


def score(label, qvecs, norms, chunks, queries):
    ranks, rows = [], []
    for q, qv in zip(queries, qvecs):
        sims = norms @ qv
        r, _ = rank_of_first_relevant(sims, chunks, set(q["relevant"]))
        ranks.append(r)
        rows.append({"query": q["q"], "relevant": q["relevant"], "rank": r,
                     "top_hit": chunks[int(np.argmax(sims))]["path"]})
    n = len(ranks)
    out = {"model": label, "n_queries": n,
           "mrr": round(sum(1.0 / r for r in ranks if r) / n, 4)}
    for k in KS:
        out[f"recall@{k}"] = round(sum(1 for r in ranks if r and r <= k) / n, 4)
    out["never_found"] = sum(1 for r in ranks if r is None)
    out["per_query"] = rows
    return out


def parse_args(argv):
    p = argparse.ArgumentParser(
        description="Score N embedding arms on a labelled retrieval set.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--queries", required=True, help="labelled query set JSON")
    p.add_argument("--out", required=True, help="where to write results JSON")
    p.add_argument("--arm", action="append", metavar="LABEL=INDEX_DIR",
                   help="local arm; repeatable")
    p.add_argument("--model", action="append", metavar="LABEL=MODEL_REF",
                   help=f"model per local arm (default {DEFAULT_MODEL})")
    p.add_argument("--backend", action="append", metavar="LABEL=BACKEND",
                   help="torch|onnx|openvino per local arm (default torch)")
    p.add_argument("--gemini-arm", action="append", metavar="LABEL=INDEX_DIR",
                   help="Gemini arm; repeatable. Only these trigger any network call.")
    p.add_argument("--gemini-model", default=DEFAULT_GEMINI_MODEL)
    p.add_argument("--vertex-project", default=None,
                   help="use Vertex AI (ADC auth, bills via Cloud Billing) instead of an API key")
    p.add_argument("--vertex-location", default="us-central1")
    p.add_argument("--dims", type=int, default=768)
    p.add_argument("--device", default="cpu")
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--max-seq", type=int, default=2048)
    p.add_argument("--no-query-prefix", action="store_true",
                   help="omit the CodeRankEmbed query prefix on local arms")
    a = p.parse_args(argv)
    if not a.arm and not a.gemini_arm:
        p.error("at least one --arm or --gemini-arm is required")
    return a


def main(argv=None):
    a = parse_args(argv)
    spec = json.load(open(a.queries, encoding="utf-8"))
    queries = spec["queries"]

    local = kv(a.arm, "arm")
    gemini = kv(a.gemini_arm, "gemini-arm")
    models = kv(a.model, "model")
    backends = kv(a.backend, "backend")

    overlap = set(local) & set(gemini)
    if overlap:
        sys.exit(f"score_retrieval: label(s) used for both a local and a Gemini arm: "
                 f"{', '.join(sorted(overlap))}")
    for opt, given in (("model", models), ("backend", backends)):
        unknown = set(given) - set(local)
        if unknown:
            sys.exit(f"score_retrieval: --{opt} names unknown local arm(s): "
                     f"{', '.join(sorted(unknown))}")

    # --- load every index, assert one shared corpus -------------------------
    loaded, reference = {}, None
    for label, d in list(local.items()) + list(gemini.items()):
        norms, chunks = load_index(Path(d), label)
        paths = [c["path"] for c in chunks]
        if reference is None:
            reference = (label, paths)
        elif paths != reference[1]:
            sys.exit(f"score_retrieval: arm {label!r} was built from a different corpus "
                     f"than {reference[0]!r} — row i is not the same chunk in both, so the "
                     f"scores would not be comparable. Re-index one of them.")
        loaded[label] = (norms, chunks)
    n_chunks = len(reference[1])
    print(f"{len(queries)} queries, {n_chunks} chunks, {len(loaded)} arm(s), corpora match")

    # --- encode + score -----------------------------------------------------
    results = []
    for label, d in local.items():
        ref = models.get(label, DEFAULT_MODEL)
        backend = backends.get(label, "torch")
        print(f"[{label}] local · model={ref} backend={backend} "
              f"device={a.device} threads={a.threads}")
        qv = encode_local(queries, ref, backend, a.device, a.threads, a.max_seq,
                          not a.no_query_prefix)
        norms, chunks = loaded[label]
        results.append(score(label, qv, norms, chunks, queries))

    for label, d in gemini.items():
        route = (f"vertex project={a.vertex_project} location={a.vertex_location}"
                 if a.vertex_project else "developer-api (GEMINI_KEY)")
        print(f"[{label}] gemini · model={a.gemini_model} dims={a.dims} · {route}")
        qv = encode_gemini(queries, a.gemini_model, a.dims,
                           a.vertex_project, a.vertex_location)
        norms, chunks = loaded[label]
        results.append(score(label, qv, norms, chunks, queries))

    # --- report -------------------------------------------------------------
    width = max(len(r["model"]) for r in results) + 2
    hdr = (f"{'arm':<{width}} {'MRR':>6} "
           + " ".join(f"{'R@' + str(k):>6}" for k in KS) + f" {'miss':>5}")
    print("\n" + hdr)
    print("-" * len(hdr))
    for s in results:
        print(f"{s['model']:<{width}} {s['mrr']:>6.3f} "
              + " ".join(f"{s['recall@' + str(k)]:>6.3f}" for k in KS)
              + f" {s['never_found']:>5}")

    print("\nPer-query rank of first relevant hit (lower is better, '-' = never found):")
    labels = [r["model"] for r in results]
    print(f"{'query':<52} " + " ".join(f"{l[:11]:>12}" for l in labels))
    for i in range(len(queries)):
        cells = " ".join(f"{str(r['per_query'][i]['rank'] or '-'):>12}" for r in results)
        print(f"{results[0]['per_query'][i]['query'][:50]:<52} {cells}")

    json.dump({"queries_file": a.queries, "n_chunks": n_chunks, "results": results},
              open(a.out, "w"), indent=2)
    print(f"\nSaved -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
