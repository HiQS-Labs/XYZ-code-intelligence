#!/usr/bin/env bash
# validate.sh — the repo's pre-advance gate (marathon-drive runs `bash validate.sh` before a phase
# is approved). Deterministic only: PDDA hygiene checks, then the Python package's import smoke and
# test suite once they exist. Extend it as phases land; never weaken a check to make a phase pass.
set -euo pipefail
cd "$(dirname "$0")"

export HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
PY=".venv/bin/python"

echo "== PDDA deterministic checks (PDDA_MODE=full so errors block; the repo's .pdda-mode stays observe)"
export PDDA_MODE=full
for check in frontmatter status-table roadmap roadmap-coverage hardcoded-paths; do
  ./utils/pdda/pdda.sh "$check"
done

if [[ -f pyproject.toml ]]; then
  [[ -x "$PY" ]] || { echo "validate: $PY missing — create the venv per SOP.md" >&2; exit 1; }
  echo "== import smoke"
  "$PY" -c "import xyz; print('xyz', getattr(xyz, '__version__', '?'))"
  if [[ -d tests ]]; then
    echo "== pytest"
    "$PY" -m pytest -q tests
  fi
fi

echo "validate: OK"
