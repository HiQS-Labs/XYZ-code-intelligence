---
title: GH-11 marathon brief — gh11-p0-scaffold
status: active
created: 2026-09-05
updated: 2026-09-05
owner: Noel Saw
goal: Phase brief consumed by marathon-drive.sh for phase gh11-p0-scaffold; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
roadmap_exempt: true
---

# Phase brief — gh11-p0-scaffold: Phase 0 close-out (constraints, pyproject, `xyz/` skeleton, gate)

## Status

| What was just completed | What's next |
|---|---|
| Brief authored (2026-09-05). | Executed by `marathon.sh` as phase `gh11-p0-scaffold`; outcome recorded in the capture doc. |

Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
Canonical doc: `PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md`
→ "Phase 0 — Decision lock and repo scaffolding", steps 2-3.

## Environment (read first)

- Python venv already exists at `.venv/` (Python 3.11) with `sentence-transformers`, `torch`,
  `einops`, `numpy`, `sqlite-vec`, `tree-sitter`, `tree-sitter-language-pack`, `pytest`, `psutil`.
  Run everything as `.venv/bin/python ...`. **No network inside a turn** — do not `pip install`;
  if a dependency is missing, say so in the relay and stop.
- `HF_HUB_OFFLINE=1` is exported by `validate.sh`; the HF cache already holds
  `nomic-ai/CodeRankEmbed` and `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Gate: `bash validate.sh` (already present, thin). Extend it, never weaken it.

## Task

1. **Constraints into `GUIDING-PRINCIPLES.md`** (canonical Phase 0 step 3). The file is still the
   PDDA-repo boilerplate. Replace its `## Purpose` paragraph with one that describes *this* repo
   (XYZ Code Intelligence: local-first code retrieval, successor to Ask-Self) and append two numbered
   principles after the existing eight, in the same voice:
   - **Local-first.** Ingest, embedding, retrieval and reranking run on the operator's machine with
     no network call on the query path. A cloud API may appear only as an explicitly opt-in
     comparison arm, never as the primary lane.
   - **Permissively licensed models only.** Every model weight the pipeline loads is Apache-2.0 or
     MIT (or equivalent). Verify the licence on the model card before a model enters any run; a
     model whose licence is unstated or non-commercial is rejected, not deferred.
   Leave the other principles intact (they still govern the PDDA docs in this repo).
2. **`pyproject.toml`** at the repo root: project name `xyz-code-intelligence`, version `0.5.0.dev0`,
   `requires-python = ">=3.11"`, dependencies pinned to the *installed* versions (read them with
   `.venv/bin/python -m pip list`): `sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`,
   `tree-sitter`, `tree-sitter-language-pack`; optional group `dev = ["pytest", "psutil"]`; console
   script `xyz = "xyz.cli:main"`; setuptools build backend with `packages = ["xyz", ...]` found
   automatically (`[tool.setuptools.packages.find] include = ["xyz*"]`). Install it editable:
   `.venv/bin/python -m pip install -e . --no-deps --no-build-isolation` (works offline).
3. **`xyz/` package skeleton** (canonical Phase 0 step 2), modules only — no logic yet beyond
   docstrings and `__version__`:
   - `xyz/__init__.py` (`__version__ = "0.5.0.dev0"`)
   - `xyz/ingest/__init__.py` — chunking (p1)
   - `xyz/index/__init__.py` — SQLite store + embed cache (p2)
   - `xyz/retrieve/__init__.py` — BM25 + dense + RRF + rerank (p3)
   - `xyz/eval/__init__.py` — metrics (p4)
   - `xyz/cli.py` with a `main()` that prints the version and the subcommand list (`ingest`,
     `query`, `eval`) and exits 0; real subcommands land in p4.
4. **`tests/`**: `tests/__init__.py` empty; `tests/test_smoke.py` asserting `import xyz` and that
   `xyz.cli.main([])` returns 0 (make `main` accept an `argv` list for testability).
5. **Extend `validate.sh`**: it already runs the import smoke and pytest once `pyproject.toml`
   exists — confirm it goes green end to end after your changes. Add the editable-install line
   `"$PY" -m pip install -e . --no-deps --no-build-isolation -q` guarded by `[[ -f pyproject.toml ]]`
   so a fresh clone with the venv can self-heal the import.

## Non-goals

No chunking, embedding, SQL or retrieval code in this phase. No changes to `.embed-tmp/`.
Do not rewrite `AGENTS.md` (out of scope; parked).

## Definition of done

- `bash validate.sh` exits 0 and prints the `xyz` version from the import smoke.
- `.venv/bin/python -m pytest -q tests` → 1 passed.
- `GUIDING-PRINCIPLES.md` contains both new principles and a repo-accurate Purpose; the eight
  original principles are unchanged.
- `./utils/pdda/pdda.sh governance` reports no new error (warnings allowed).
- Red control: temporarily rename `xyz/__init__.py` and confirm `validate.sh` fails on the import
  smoke; restore it. Record that you did this in your relay block.
