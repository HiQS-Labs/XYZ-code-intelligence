#!/usr/bin/env bash
# prelaunch.sh — OPERATOR readiness control, run once before firing the GH-11 marathon (and again
# after any venv/cache change). Unlike validate.sh (the per-phase gate), this actually LOADS both
# models offline with their real classes and instantiates every Tree-sitter parser the chunker
# needs, using the exact interpreter builder turns will use. It writes a marker next to that
# interpreter (`<venv>/xyz-prelaunch.json`) which validate.sh requires — so a builder turn cannot
# start on a tree whose readiness was never proven. Evidence is printed and copied to $XYZ_SCRATCH.
#
# Usage: XYZ_PY=/path/to/.venv/bin/python bash prelaunch.sh
# Exit: 0 ready · 1 not ready (message names the first failing component).
set -euo pipefail
cd "$(dirname "$0")"
REPO="$PWD"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
export XYZ_PY="${XYZ_PY:-$REPO/.venv/bin/python}"
export XYZ_SCRATCH="${XYZ_SCRATCH:-$REPO/.relay-scratch}"
[[ -x "$XYZ_PY" ]] || { echo "prelaunch: XYZ_PY not executable: $XYZ_PY" >&2; exit 1; }
mkdir -p "$XYZ_SCRATCH"
MARKER="$(cd "$(dirname "$XYZ_PY")/.." && pwd)/xyz-prelaunch.json"

# INVALIDATE FIRST (GH-11 plan review r3): a readiness attempt must never be able to fall back on a
# previous success. The marker is removed before anything is tested and only re-published — atomically,
# via a temp file + os.replace — when every check passes. So a failed or interrupted run leaves NO
# marker, and validate.sh fails until a real success re-publishes one.
rm -f "$MARKER"

"$XYZ_PY" - "$MARKER" "$XYZ_SCRATCH/prelaunch.json" <<'PY'
import hashlib, importlib, json, os, pathlib, sys, time
marker, evidence = sys.argv[1], sys.argv[2]
RERANKER = os.environ.get("XYZ_RERANKER", "mixedbread-ai/mxbai-rerank-xsmall-v1")

def env_fingerprint():
    """What this readiness run actually validated. validate.sh compares it to the live env, so a
    changed reranker or model cache invalidates readiness instead of silently reusing it."""
    return {
        "reranker": RERANKER,
        "HF_HOME": os.environ.get("HF_HOME", ""),
        "HF_HUB_CACHE": os.environ.get("HF_HUB_CACHE", ""),
        "TRANSFORMERS_CACHE": os.environ.get("TRANSFORMERS_CACHE", ""),
        "hf_hub_dir": str(pathlib.Path(os.environ.get("HF_HOME", pathlib.Path.home() / ".cache/huggingface")) / "hub"),
    }

report = {"xyz_py": sys.executable, "python": sys.version.split()[0], "checks": {},
          "env": env_fingerprint(), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
def fail(msg):
    report["ok"] = False; report["error"] = msg
    pathlib.Path(evidence).write_text(json.dumps(report, indent=2))
    sys.exit(f"prelaunch: NOT READY — {msg}")

# 1. Real imports (not find_spec) of every runtime dependency.
for m in ("numpy", "sqlite_vec", "tree_sitter", "tree_sitter_language_pack", "sentence_transformers", "torch", "einops", "pytest", "psutil"):
    try:
        mod = importlib.import_module(m); report["checks"][m] = getattr(mod, "__version__", "ok")
    except Exception as e:
        fail(f"import {m} failed: {e!r}")

# 2. FTS5 + sqlite-vec usable.
import sqlite3, sqlite_vec
c = sqlite3.connect(":memory:"); c.enable_load_extension(True); sqlite_vec.load(c)
if c.execute("select sqlite_compileoption_used('ENABLE_FTS5')").fetchone()[0] != 1: fail("FTS5 not compiled in")
c.execute("create virtual table t using vec0(e float[4])"); c.execute("insert into t(rowid,e) values (1, ?)", (sqlite_vec.serialize_float32([1,0,0,0]),))
if c.execute("select rowid from t where e match ? and k = ?", (sqlite_vec.serialize_float32([1,0,0,0]), 1)).fetchone()[0] != 1: fail("vec0 k = ? query failed")
report["checks"]["sqlite_vec_version"] = c.execute("select vec_version()").fetchone()[0]

# 3. Tree-sitter parsers the chunker needs. tree_sitter_language_pack DOWNLOADS grammars on first
#    use (cache: ~/Library/Caches/tree-sitter-language-pack), so an offline builder turn fails
#    unless they are already cached. Assert they are cached BEFORE parsing, or the check is
#    vacuous on a machine that happens to have network.
from tree_sitter_language_pack import get_parser
try:
    from tree_sitter_language_pack import downloaded_languages
    cached = set(downloaded_languages())
    missing = [l for l in ("python", "javascript", "typescript", "tsx", "php") if l not in cached]
    if missing:
        fail(f"tree-sitter grammars not cached (offline turns cannot fetch them): {missing} — "
             f"run once WITH network: {sys.executable} -c \"from tree_sitter_language_pack import download; download(['python','javascript','typescript','tsx','php'])\"")
    report["checks"]["grammars_cached"] = sorted(l for l in cached if l in {"python","javascript","typescript","tsx","php"})
except ImportError:
    report["checks"]["grammars_cached"] = "downloaded_languages() unavailable — parse smoke only"
for lang, src in (("python", b"def f():\n  return 1\n"), ("javascript", b"function f(){return 1}\n"),
                  ("typescript", b"export function f(): number { return 1 }\n"), ("tsx", b"const A = () => <div/>;\n"),
                  ("php", b"<?php class A { function f() { return 1; } }\n")):
    try:
        tree = get_parser(lang).parse(src)
        if tree.root_node.has_error and lang != "tsx": fail(f"grammar {lang}: parse error on smoke snippet")
        report["checks"][f"grammar_{lang}"] = "ok"
    except Exception as e:
        fail(f"grammar {lang} unavailable: {e!r}")

# 4. Both models load OFFLINE with their real classes and produce output.
from sentence_transformers import SentenceTransformer, CrossEncoder
try:
    t0 = time.time(); m = SentenceTransformer("nomic-ai/CodeRankEmbed", trust_remote_code=True, device="cpu")
    m.max_seq_length = 2048
    v = m.encode(["Represent this query for searching relevant code: sort a list", "def sort_list(lst):\n    return sorted(lst)"])
    if tuple(v.shape) != (2, 768): fail(f"CodeRankEmbed output shape {v.shape} != (2, 768)")
    report["checks"]["CodeRankEmbed"] = {"shape": list(v.shape), "load_s": round(time.time() - t0, 1), "max_seq_length": m.max_seq_length}
except Exception as e:
    fail(f"CodeRankEmbed offline load failed (incomplete cache?): {e!r}")
try:
    t0 = time.time(); ce = CrossEncoder(RERANKER, device="cpu", trust_remote_code=True)
    s = [float(x) for x in ce.predict([("sort a list in python", "def sort_list(lst):\n    return sorted(lst)"),
                                       ("sort a list in python", "SELECT 1 FROM dual")])]
    # A finite-AND-ordered assertion is the point: cross-encoder/ms-marco-MiniLM-L-6-v2 loads
    # "successfully" on transformers 5.16.1 and returns [nan, nan] (old-format BERT checkpoint).
    # A shape-only check passes that; this does not.
    if len(s) != 2: fail(f"{RERANKER}: expected 2 scores, got {len(s)}")
    if not all(v == v and abs(v) != float("inf") for v in s): fail(f"{RERANKER}: non-finite scores {s} — model unusable on this stack")
    if not s[0] > s[1]: fail(f"{RERANKER}: does not rank the code snippet above unrelated SQL {s} — model unusable")
    report["checks"]["reranker"] = {"model": RERANKER, "scores": s, "load_s": round(time.time() - t0, 1)}
except SystemExit:
    raise
except Exception as e:
    fail(f"reranker {RERANKER} offline load failed (incomplete cache?): {e!r}")

report["ok"] = True
pathlib.Path(evidence).write_text(json.dumps(report, indent=2))
# Atomic publish: write beside the marker, then rename. A crash mid-write cannot leave a partial
# marker that validate.sh would accept.
tmp = pathlib.Path(marker + f".tmp.{os.getpid()}")
tmp.write_text(json.dumps(report, indent=2))
os.replace(tmp, marker)
print(json.dumps(report, indent=2))
print(f"prelaunch: READY — marker written to {marker}")
PY
