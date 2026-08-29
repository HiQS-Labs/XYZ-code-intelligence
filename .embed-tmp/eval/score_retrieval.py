"""Score embedding models on a labelled retrieval set.

Both indexes must be built from the identical chunks.jsonl so row i refers to the
same chunk; that is asserted before scoring. Reports recall@k and MRR.

Usage:
  GEMINI_KEY=... python score_retrieval.py <queries.json> <local_dir> <gemini_dir> <out.json>
"""
import functools
import json
import os
import sys
from pathlib import Path

import numpy as np

print = functools.partial(print, flush=True)
KS = (1, 3, 5, 10)
QUERY_PREFIX = "Represent this query for searching relevant code: "


def load(d: Path):
    emb = np.load(d / "embeddings.npy").astype(np.float32)
    chunks = [json.loads(l) for l in open(d / "chunks.jsonl", encoding="utf-8")]
    return emb / np.linalg.norm(emb, axis=1, keepdims=True), chunks


def rank_of_first_relevant(sims, chunks, relevant):
    order = np.argsort(-sims)
    for rank, i in enumerate(order, start=1):
        if chunks[i]["path"] in relevant:
            return rank, i
    return None, None


def score(name, qvecs, norms, chunks, queries):
    ranks, rows = [], []
    for q, qv in zip(queries, qvecs):
        r, i = rank_of_first_relevant(norms @ qv, chunks, set(q["relevant"]))
        ranks.append(r)
        rows.append({"query": q["q"], "relevant": q["relevant"], "rank": r,
                     "top_hit": chunks[int(np.argmax(norms @ qv))]["path"]})
    n = len(ranks)
    out = {"model": name, "n_queries": n,
           "mrr": round(sum(1.0 / r for r in ranks if r) / n, 4)}
    for k in KS:
        out[f"recall@{k}"] = round(sum(1 for r in ranks if r and r <= k) / n, 4)
    out["never_found"] = sum(1 for r in ranks if r is None)
    out["per_query"] = rows
    return out


def main():
    qfile, local_dir, gem_dir, outfile = sys.argv[1:5]
    spec = json.load(open(qfile, encoding="utf-8"))
    queries = spec["queries"]

    ln, lc = load(Path(local_dir))
    gn, gc = load(Path(gem_dir))
    assert [c["path"] for c in lc] == [c["path"] for c in gc], \
        "indexes built from different corpora — scores would not be comparable"
    print(f"{len(queries)} queries, {len(lc)} chunks, corpora match")

    # --- local CodeRankEmbed (CPU: the GPU is busy with other runs) --------
    import torch
    torch.set_num_threads(4)
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer("nomic-ai/CodeRankEmbed", trust_remote_code=True, device="cpu")
    m.max_seq_length = 2048
    lq = m.encode([QUERY_PREFIX + q["q"] for q in queries], convert_to_numpy=True)
    lq = lq / np.linalg.norm(lq, axis=1, keepdims=True)

    # --- Gemini -----------------------------------------------------------
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_KEY"])
    r = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[q["q"] for q in queries],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY", output_dimensionality=768),
    )
    gq = np.asarray([e.values for e in r.embeddings], dtype=np.float32)
    gq = gq / np.linalg.norm(gq, axis=1, keepdims=True)

    results = [score("CodeRankEmbed (local)", lq, ln, lc, queries),
               score("gemini-embedding-001", gq, gn, gc, queries)]

    hdr = f"{'model':<24} {'MRR':>6} " + " ".join(f"{'R@'+str(k):>6}" for k in KS) + f" {'miss':>5}"
    print("\n" + hdr)
    print("-" * len(hdr))
    for s in results:
        print(f"{s['model']:<24} {s['mrr']:>6.3f} " +
              " ".join(f"{s['recall@' + str(k)]:>6.3f}" for k in KS) +
              f" {s['never_found']:>5}")

    print("\nPer-query rank of first relevant hit (lower is better, '-' = not in corpus order):")
    print(f"{'query':<52} {'local':>6} {'gemini':>7}")
    for a, b in zip(results[0]["per_query"], results[1]["per_query"]):
        print(f"{a['query'][:50]:<52} {str(a['rank'] or '-'):>6} {str(b['rank'] or '-'):>7}")

    json.dump({"queries_file": qfile, "results": results}, open(outfile, "w"), indent=2)
    print(f"\nSaved -> {outfile}")


if __name__ == "__main__":
    main()
