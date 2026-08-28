"""
Embed a set of external repos with CodeRankEmbed for retrieval evaluation.
Outputs (per repo) into .embed-tmp/<repo>/:
  - chunks.jsonl   one JSON object per chunk: {id, repo, path, start_line, end_line, text}
  - embeddings.npy float32 array, row order matches chunks.jsonl
All output stays under .embed-tmp/, which is gitignored.
"""
import functools
import gc
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

print = functools.partial(print, flush=True)  # unbuffered even when piped to a log file

# HF tokenizers spawns worker processes for parallel tokenization; in a tight
# per-batch loop these leak semaphores and add to RSS instead of being reused.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# --- rate limiting / throttling -------------------------------------------
# Local CPU inference has no external API to rate-limit, but left unbounded
# it pins all cores and starves the machine. Cap threads and pace batches so
# this can run alongside other work. Override via env vars if needed.
MAX_THREADS = int(os.environ.get("EMBED_MAX_THREADS", "4"))
BATCH_SLEEP_SECONDS = float(os.environ.get("EMBED_BATCH_SLEEP", "0.5"))
ENCODE_BATCH_SIZE = int(os.environ.get("EMBED_BATCH_SIZE", "16"))

# --- memory constraints -----------------------------------------------------
# Hard cap via RLIMIT_AS (best-effort — not fully enforced on macOS) plus a
# soft RSS watchdog checked every batch that backs off / aborts before the
# machine starts swapping.
MAX_MEM_MB = int(os.environ.get("EMBED_MAX_MEM_MB", "4096"))

os.environ.setdefault("OMP_NUM_THREADS", str(MAX_THREADS))
os.environ.setdefault("MKL_NUM_THREADS", str(MAX_THREADS))

try:
    resource.setrlimit(resource.RLIMIT_AS, (MAX_MEM_MB * 1024 * 1024, resource.RLIM_INFINITY))
except (ValueError, OSError) as e:
    print(f"[warn] could not set RLIMIT_AS hard cap ({e}); relying on RSS watchdog only")

import torch  # noqa: E402  (must set env vars before importing torch)

torch.set_num_threads(MAX_THREADS)

import numpy as np  # noqa: E402
import psutil  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

_PROC = psutil.Process(os.getpid())


def rss_mb() -> float:
    """Current (live) resident set size in MB.

    NOTE: resource.getrusage().ru_maxrss is a lifetime *high-water mark*, not
    a live reading — it never goes back down after gc, so it's useless as a
    watchdog signal (it trips once and stays tripped forever). psutil gives
    the actual current RSS.
    """
    return _PROC.memory_info().rss / (1024 * 1024)

REPOS = {
    "rebalanceOS": "/Users/noelsaw/Documents/GH Repos/rebalanceOS",
    "LTVera-Pandas": "/Users/noelsaw/Documents/GH Repos/LTVera-Pandas",
    "aegis-sleuth-slack-bot": "/Users/noelsaw/Documents/GH Repos/aegis-sleuth-slack-bot",
    "XYZ-forge": "/Users/noelsaw/Documents/GH Repos/XYZ-forge",
}

INCLUDE_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".php", ".md", ".go", ".rb", ".sh"}

EXCLUDE_DIR_PARTS = {
    "node_modules", ".git", "vendor", ".venv", "venv", ".claude", ".xyz", ".tick",
    ".web", "__pycache__", "dist", "build", "coverage", "logs", "temp", "PARKED",
    "relay-system", "marathon-system", "artifacts", "site-packages", ".next",
}

OUT_ROOT = Path(__file__).resolve().parent.parent  # .embed-tmp/
CHUNK_LINES = 60
CHUNK_OVERLAP = 15
MAX_FILE_BYTES = 400_000  # skip anything bigger (generated/data files)


def iter_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in INCLUDE_EXT:
            continue
        if any(part in EXCLUDE_DIR_PARTS for part in p.parts):
            continue
        try:
            if p.stat().st_size > MAX_FILE_BYTES or p.stat().st_size == 0:
                continue
        except OSError:
            continue
        yield p


def chunk_file(path: Path, root: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return
    lines = text.splitlines()
    if not lines:
        return
    step = CHUNK_LINES - CHUNK_OVERLAP
    rel = str(path.relative_to(root))
    for start in range(0, len(lines), step):
        end = min(start + CHUNK_LINES, len(lines))
        body = "\n".join(lines[start:end]).strip()
        if len(body) >= 20:
            yield {
                "path": rel,
                "start_line": start + 1,
                "end_line": end,
                "text": body,
            }
        if end == len(lines):
            break


def process_repo(repo_name: str, repo_path: str) -> None:
    """Embed one repo in this process. Called either directly (single-repo
    mode) or as a subprocess spawned by the dispatcher below."""
    root = Path(repo_path)
    if not root.exists():
        print(f"[skip] {repo_name}: {repo_path} not found")
        return

    out_dir = OUT_ROOT / repo_name
    out_dir.mkdir(parents=True, exist_ok=True)

    chunks = []
    for f in iter_files(root):
        for c in chunk_file(f, root):
            c["id"] = len(chunks)
            c["repo"] = repo_name
            chunks.append(c)

    if not chunks:
        print(f"[skip] {repo_name}: no chunks produced")
        return

    print(f"[{repo_name}] {len(chunks)} chunks from repo at {repo_path}")

    model = SentenceTransformer("nomic-ai/CodeRankEmbed", trust_remote_code=True)
    t0 = time.time()
    texts = [c["text"] for c in chunks]

    # Encode in throttled batches (own loop, not model.encode's internal
    # batching) so we can sleep between batches and keep CPU usage capped.
    batch_embeddings = []
    n_batches = (len(texts) + ENCODE_BATCH_SIZE - 1) // ENCODE_BATCH_SIZE
    over_cap_streak = 0
    for bi in range(n_batches):
        batch = texts[bi * ENCODE_BATCH_SIZE : (bi + 1) * ENCODE_BATCH_SIZE]
        emb = model.encode(batch, batch_size=ENCODE_BATCH_SIZE, convert_to_numpy=True)
        batch_embeddings.append(emb)
        if (bi + 1) % 10 == 0 or bi == n_batches - 1:
            print(f"[{repo_name}] batch {bi + 1}/{n_batches}  rss={rss_mb():.0f}MB")

        # RSS watchdog: back off, then abort rather than let the box swap.
        # A per-repo subprocess (see dispatch()) means this cap is measured
        # against one repo's own footprint, not a running total across repos.
        if rss_mb() > MAX_MEM_MB:
            gc.collect()
            if rss_mb() > MAX_MEM_MB:
                over_cap_streak += 1
                print(f"[warn] {repo_name}: rss {rss_mb():.0f}MB over cap {MAX_MEM_MB}MB "
                      f"after gc (streak {over_cap_streak})")
                time.sleep(BATCH_SLEEP_SECONDS * 4)
                if over_cap_streak >= 3:
                    print(f"[abort] {repo_name}: memory cap exceeded 3x in a row, stopping "
                          f"early at batch {bi + 1}/{n_batches}. Partial results saved.")
                    break
            else:
                over_cap_streak = 0
        else:
            over_cap_streak = 0

        if BATCH_SLEEP_SECONDS > 0 and bi != n_batches - 1:
            time.sleep(BATCH_SLEEP_SECONDS)

    embeddings = np.concatenate(batch_embeddings, axis=0)
    n_saved = embeddings.shape[0]
    chunks = chunks[:n_saved]
    print(f"[{repo_name}] encoded {n_saved}/{len(texts)} chunks in "
          f"{time.time() - t0:.1f}s -> shape {embeddings.shape}")

    np.save(out_dir / "embeddings.npy", embeddings.astype(np.float32))
    with open(out_dir / "chunks.jsonl", "w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(json.dumps(c) + "\n")

    print(f"[{repo_name}] saved sidecars -> {out_dir}")


def dispatch() -> int:
    """Run each repo as its own fresh subprocess.

    torch/transformers/tokenizers don't reliably hand memory back to the OS
    within one long-lived process (RSS climbed repo-over-repo even after
    del + gc.collect()). A subprocess per repo guarantees the OS reclaims
    everything on exit, so the memory cap applies per-repo, not cumulatively.
    """
    failures = []
    for repo_name, repo_path in REPOS.items():
        print(f"[dispatch] starting {repo_name} in a fresh subprocess")
        result = subprocess.run(
            [sys.executable, __file__, "--repo", repo_name, repo_path],
            env=os.environ.copy(),
        )
        if result.returncode != 0:
            failures.append(repo_name)
            print(f"[dispatch] {repo_name} exited with code {result.returncode}")
    print("DONE" if not failures else f"DONE with failures: {failures}")
    return 1 if failures else 0


def main() -> int:
    if len(sys.argv) >= 4 and sys.argv[1] == "--repo":
        process_repo(sys.argv[2], sys.argv[3])
        return 0
    return dispatch()


if __name__ == "__main__":
    sys.exit(main())
