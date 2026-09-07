---
title: GH-11 marathon brief — gh11-p0-scaffold
status: active
created: 2026-09-05
updated: 2026-09-06
owner: Noel Saw
goal: Phase brief consumed by marathon-drive.sh for phase gh11-p0-scaffold; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
roadmap_exempt: true
---

# Phase brief — gh11-p0-scaffold: Phase 0 close-out (constraints, pyproject, `xyz/` skeleton, gate)

## Status

| What was just completed | What's next |
|---|---|
| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p0-scaffold`; outcome recorded in the capture doc. |

Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
Canonical doc: `PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md`
→ "Phase 0 — Decision lock and repo scaffolding", steps 2-3.

## Environment contract (read first — applies to every phase)

`validate.sh` defines it; the operator exports the values when launching the marathon:

| Variable | Meaning | Default |
|---|---|---|
| `XYZ_PY` | interpreter carrying the pinned deps (`sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`, `tree-sitter`, `tree-sitter-language-pack`, `pytest`, `psutil`) | `<repo>/.venv/bin/python` |
| `XYZ_SCRATCH` | where generated evidence goes (index DBs, eval JSON, logs); swept by the harness, never committed | `<repo>/.relay-scratch` |
| `XYZ_EVAL_REPO` | the corpus for the p4 round-trip (an absolute path to a LTVera-Pandas checkout) | unset — p4 fails fast if unset |
| `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `TOKENIZERS_PARALLELISM=false` | no network inside a turn; both models are already in the HF cache | exported by `validate.sh`; **export them yourself before any ad-hoc smoke** |

Rules: run Python only as `"$XYZ_PY"`; **no `pip install`**, no editable install (it writes
`*.egg-info/` into the tree, an off-lane write) — the package is imported from the tree via
`PYTHONPATH=<repo>` which `validate.sh` sets and `pyproject.toml` mirrors for pytest; write scratch
only under `$XYZ_SCRATCH`.

Readiness is **proven before the marathon fires**, not assumed: the operator runs `prelaunch.sh`
with the same `XYZ_PY`, which really imports every dependency, instantiates the Python / JS / TS /
TSX / PHP parsers, and loads **both models offline with their real classes** (encode + predict),
then writes `<venv>/xyz-prelaunch.json`. `validate.sh`'s `env preflight` requires that marker (for
this exact interpreter) and re-does the cheap parts (real imports, parser creation, FTS5/vec0). If
the marker is missing or names another interpreter, the gate fails with the command to run — do not
work around it. Before starting, run `bash validate.sh` once: `env preflight` must pass; the later
sections are expected to fail until this phase is done.

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
2. **`pyproject.toml`** at the repo root: name `xyz-code-intelligence`, version `0.5.0.dev0`,
   `requires-python = ">=3.11"`, dependencies pinned to the versions `"$XYZ_PY" -m pip list` shows
   for `sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`, `tree-sitter`,
   `tree-sitter-language-pack`; optional group `dev = ["pytest", "psutil"]`; console script
   `xyz = "xyz.cli:main"` (declared for a future install — not installed in this marathon);
   setuptools backend with `[tool.setuptools.packages.find] include = ["xyz*"]`;
   `[tool.pytest.ini_options] pythonpath = ["."]` and `testpaths = ["tests"]`.
3. **`xyz/` package skeleton** (canonical Phase 0 step 2), modules only — docstrings and
   `__version__`, no logic:
   - `xyz/__init__.py` (`__version__ = "0.5.0.dev0"` — `validate.sh` asserts this exact string)
   - `xyz/__main__.py` → `raise SystemExit(main())` from `xyz.cli`
   - `xyz/ingest/__init__.py`, `xyz/index/__init__.py`, `xyz/retrieve/__init__.py`,
     `xyz/eval/__init__.py`
   - `xyz/cli.py`: `main(argv: list[str] | None = None) -> int` (argparse). `--version` prints the
     version and returns 0; no arguments prints the subcommand list (`ingest`, `query`, `eval`, all
     "not implemented until gh11-p4") and returns 0; an unknown subcommand returns 2.
4. **`tests/`**: `tests/__init__.py`; `tests/test_smoke.py` asserting `xyz.__version__ ==
   "0.5.0.dev0"`, `main([])` returns 0, `main(["--version"])` returns 0, `main(["bogus"])` returns 2.
5. **`validate.sh`** already asserts everything above (package presence, exact version,
   `python -m xyz --version`, pytest). Do not edit it in this phase unless a check is wrong — if so,
   say exactly what and why in the relay.

## Non-goals

No chunking, embedding, SQL or retrieval code. No changes to `.embed-tmp/`. No `AGENTS.md`
rewrite (parked). No `CHANGELOG.md` entry — the orchestrator writes it at PR time.

## Definition of done

- `bash validate.sh` exits 0 end to end.
- `GUIDING-PRINCIPLES.md` contains both new principles and a repo-accurate Purpose; the eight
  original principles are unchanged; `./utils/pdda/pdda.sh governance` reports no new error.
- Red control (do it, quote the output in the relay, then restore): change `__version__` to
  `"0.0.0"` → `validate.sh` must fail at "import smoke (exact version)"; delete
  `xyz/__main__.py` → it must fail at "package presence".
