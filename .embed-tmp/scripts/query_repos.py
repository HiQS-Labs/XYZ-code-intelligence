"""
Run test queries against the embedding sidecars produced by embed_repos.py.
Prints top-k results per query. Read-only; does not write anything.
"""
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

OUT_ROOT = Path(__file__).resolve().parent.parent  # .embed-tmp/
QUERY_PREFIX = "Represent this query for searching relevant code: "
TOP_K = 3

QUERIES = {
    "rebalanceOS": [
        "PDDA lifecycle tracking roadmap items",
        "Gmail integration for reading and sending mail",
        "calendar scheduler that finds available time slots",
    ],
    "LTVera-Pandas": [
        "alembic database migration script",
        "docker compose service configuration",
        "pipeline that processes a pandas dataframe",
    ],
    "aegis-sleuth-slack-bot": [
        "slack event handler for incoming messages",
        "sentinel security monitoring check",
        "backup script for sleuth data",
    ],
    "XYZ-forge": [
        "harness registry of model configurations",
        "relay automation loop between two agents",
        "fuzzing test queue runner",
    ],
}


def load_repo(name):
    d = OUT_ROOT / name
    emb = np.load(d / "embeddings.npy")
    chunks = [json.loads(l) for l in open(d / "chunks.jsonl", encoding="utf-8")]
    norms = emb / np.linalg.norm(emb, axis=1, keepdims=True)
    return norms, chunks


def main():
    model = SentenceTransformer("nomic-ai/CodeRankEmbed", trust_remote_code=True)

    results = {}
    for repo, queries in QUERIES.items():
        d = OUT_ROOT / repo
        if not (d / "embeddings.npy").exists():
            print(f"[skip] {repo}: no sidecar found")
            continue
        norms, chunks = load_repo(repo)
        repo_results = []
        for q in queries:
            qvec = model.encode([QUERY_PREFIX + q], convert_to_numpy=True)[0]
            qvec = qvec / np.linalg.norm(qvec)
            sims = norms @ qvec
            top_idx = np.argsort(-sims)[:TOP_K]
            hits = [
                {
                    "score": float(sims[i]),
                    "path": chunks[i]["path"],
                    "lines": f"{chunks[i]['start_line']}-{chunks[i]['end_line']}",
                    "snippet": chunks[i]["text"][:200].replace("\n", " "),
                }
                for i in top_idx
            ]
            repo_results.append({"query": q, "hits": hits})
            print(f"\n=== [{repo}] {q} ===")
            for h in hits:
                print(f"  {h['score']:.3f}  {h['path']}:{h['lines']}")
                print(f"       {h['snippet']}")
        results[repo] = repo_results

    with open(OUT_ROOT / "query_results.json", "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    print("\nSaved -> query_results.json")


if __name__ == "__main__":
    main()
