#!/usr/bin/env bash
# validate.sh — the repo's pre-advance gate (marathon-drive runs `bash validate.sh` before a phase
# is approved). Deterministic only: environment preflight, PDDA hygiene checks (blocking), the
# package's import smoke with an exact version assertion, and the test suite. It is unconditional:
# a clone without pyproject.toml / xyz/ / tests/ FAILS here — phase gh11-p0-scaffold's job is to
# make it green. Extend it as phases land; never weaken a check to make a phase pass.
set -euo pipefail
cd "$(dirname "$0")"
REPO="$PWD"

# ── Environment contract (set by the operator when launching a marathon; defaults are repo-relative)
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
export XYZ_PY="${XYZ_PY:-$REPO/.venv/bin/python}"          # interpreter with the pinned deps
export XYZ_SCRATCH="${XYZ_SCRATCH:-$REPO/.relay-scratch}"  # generated evidence (index DBs, eval JSON)
export PYTHONPATH="$REPO${PYTHONPATH:+:$PYTHONPATH}"       # import xyz from the tree; no editable install
EXPECTED_VERSION="0.5.0.dev0"

echo "== env preflight"
[[ -x "$XYZ_PY" ]] || { echo "validate: XYZ_PY not executable: $XYZ_PY — create the venv per SOP.md or export XYZ_PY" >&2; exit 1; }
# Readiness is proven by prelaunch.sh (operator-run: real offline model loads + parser creation with
# this exact interpreter). Its marker must exist next to the venv and name this interpreter.
MARKER="$(cd "$(dirname "$XYZ_PY")/.." && pwd)/xyz-prelaunch.json"
[[ -f "$MARKER" ]] || { echo "validate: readiness marker missing: $MARKER — run: XYZ_PY=$XYZ_PY bash prelaunch.sh" >&2; exit 1; }
"$XYZ_PY" - "$MARKER" <<'PY'
import importlib, json, os, pathlib, sys
m = json.load(open(sys.argv[1]))
if not m.get("ok"): sys.exit("validate: prelaunch marker records NOT READY — re-run prelaunch.sh")
if m.get("xyz_py") != sys.executable: sys.exit(f"validate: prelaunch marker is for {m.get('xyz_py')}, not {sys.executable}")
# The marker must have validated THIS configuration: the same reranker and the same model cache.
# Otherwise a stale success would vouch for a model or cache that was never tested.
live = {
    "reranker": os.environ.get("XYZ_RERANKER", "mixedbread-ai/mxbai-rerank-xsmall-v1"),
    "HF_HOME": os.environ.get("HF_HOME", ""),
    "HF_HUB_CACHE": os.environ.get("HF_HUB_CACHE", ""),
    "TRANSFORMERS_CACHE": os.environ.get("TRANSFORMERS_CACHE", ""),
    "hf_hub_dir": str(pathlib.Path(os.environ.get("HF_HOME", pathlib.Path.home() / ".cache/huggingface")) / "hub"),
}
was = m.get("env") or {}
drift = {k: (was.get(k), v) for k, v in live.items() if was.get(k) != v}
if drift:
    sys.exit("validate: environment changed since prelaunch (validated, now): "
             + json.dumps(drift) + " — re-run: XYZ_PY=%s bash prelaunch.sh" % sys.executable)
for mod in ("numpy", "sqlite_vec", "tree_sitter_language_pack", "sentence_transformers", "pytest"):
    importlib.import_module(mod)  # real import, not find_spec
from tree_sitter_language_pack import get_parser
for lang in ("python", "javascript", "typescript", "tsx", "php"):
    get_parser(lang)
import sqlite3, sqlite_vec
c = sqlite3.connect(":memory:"); c.enable_load_extension(True); sqlite_vec.load(c)
assert c.execute("select sqlite_compileoption_used('ENABLE_FTS5')").fetchone()[0] == 1, "FTS5 missing"
print("env ok:", sys.version.split()[0], "prelaunch", m["at"], "sqlite-vec", c.execute("select vec_version()").fetchone()[0])
PY
mkdir -p "$XYZ_SCRATCH"

echo "== PDDA deterministic checks (PDDA_MODE=full so errors block; the repo's .pdda-mode stays observe)"
export PDDA_MODE=full
for check in frontmatter status-table roadmap roadmap-coverage hardcoded-paths; do
  ./utils/pdda/pdda.sh "$check"
done

echo "== package presence (unconditional after gh11-p0-scaffold)"
for p in pyproject.toml xyz/__init__.py xyz/__main__.py tests; do
  [[ -e "$p" ]] || { echo "validate: required path missing: $p" >&2; exit 1; }
done

echo "== import smoke (exact version)"
got="$("$XYZ_PY" -c 'import xyz; print(xyz.__version__)')"
[[ "$got" == "$EXPECTED_VERSION" ]] || { echo "validate: xyz.__version__ = '$got', expected '$EXPECTED_VERSION'" >&2; exit 1; }
"$XYZ_PY" -m xyz --version >/dev/null

echo "== pytest"
"$XYZ_PY" -m pytest -q tests

echo "validate: OK"
