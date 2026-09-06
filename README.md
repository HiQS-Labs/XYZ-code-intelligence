# XYZ Code Intelligence

A local-first code retrieval system for answering natural-language questions about codebases — the planned successor to [Ask-Self](https://github.com/Hypercart-Dev-Tools/ask-self).

XYZ indexes source code from one or more repos and retrieves the most relevant functions/classes for a query using a hybrid of dense embeddings and lexical (BM25) search, fused and reranked, running entirely on-device (Apple Silicon) rather than through cloud APIs. It also carries a documentation-governance layer (PDDA) that keeps the project's own planning docs consistent, and a vendored multi-agent coordination harness (`.xyz/`) used to drive AI-agent workflows in this repo.

**Status:** early-stage / spike. The full retrieval pipeline described below is not yet built — see [Status](#status).

## Architecture (planned)

Per the canonical build doc (`PROJECT/2-WORKING/v0.5/`):

1. **Chunking** — AST/Tree-sitter based, at the function/class level.
2. **Dense lane** — code-native embedding model, candidate `nomic-ai/CodeRankEmbed` (768-dim, via `sentence-transformers`).
3. **Lexical lane** — SQLite FTS5 / BM25.
4. **Fusion** — Reciprocal Rank Fusion across both lanes.
5. **Reranking** — cross-encoder rerank of fused candidates.

Build plan is 6 phases: decision lock → chunking/retrieval skeleton → frozen benchmark → model bake-off → conditional fine-tuning → Ask-Self sunset/migration. Full detail and evidence (embedding model comparisons, fine-tuning datasets, the original Hyperagent research report) live in `PROJECT/2-WORKING/v0.5/`.

## Status

| Completed | Next |
|---|---|
| CodeRankEmbed installed and validated; v0.5 canonical research/build doc synthesized from prior research | Phase 1: chunking + hybrid retrieval skeleton |

See `ROADMAP.md` for the live ledger and `CHANGELOG.md` for dated iteration history.

## What's in this repo today

- `PROJECT/2-WORKING/v0.5/` — the canonical build doc plus research evidence appendices (embedding model decision report, fine-tuning pipeline evidence, NL-to-code dataset survey, raw Hyperagent report).
- `.embed-tmp/scripts/embed_repos.py`, `query_repos.py` — working proof-of-concept embedding pipeline: batch-embeds a repo with CodeRankEmbed, with CPU/memory throttling, per-repo process isolation, and profiling. Sidecar embeddings already generated for several external repos under `.embed-tmp/<repo>/`.
- `utils/pdda/` + `PROJECT/PDDA.md` — the doc-governance automation (frontmatter checks, roadmap coverage, changelog hygiene) this repo runs on itself.
- `.xyz/` — vendored multi-agent coordination harness (`tick` CLI, relay/marathon tooling) used to run AI-agent workflows here; not part of the XYZ Code Intelligence product itself.
- Root governance docs: `ROUTER.md` (start here each session), `AGENTS.md`, `GUIDING-PRINCIPLES.md`, `SOP.md`, `CHANGELOG.md`, `ROADMAP.md`, `RELEASES.md`.

## Setup

No packaged project yet (no `package.json`/`pyproject.toml`) — this is scripts run inside a local venv.

```bash
uv venv .venv --python 3.11
uv pip install --python .venv sentence-transformers einops torch psutil
```

Model weights (`nomic-ai/CodeRankEmbed`) download on first use into the default HuggingFace cache. Full usage notes, throttling env vars, and memory-safety details are in `SOP.md`.

## Usage

Encode a query/code pair:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("nomic-ai/CodeRankEmbed", trust_remote_code=True)
query = "Represent this query for searching relevant code: sort a list in python"
code = "def sort_list(lst):\n    return sorted(lst)"
embeddings = model.encode([query, code])  # shape: (2, 768)
```

Batch-embed a repo:

```bash
.venv/bin/python -u .embed-tmp/scripts/embed_repos.py --repo <name> <path>
```

See `SOP.md` for throttling (`EMBED_MAX_THREADS`, `EMBED_BATCH_SIZE`, `EMBED_MAX_MEM_MB`) and profiling (`EMBED_PROFILE=1`) options.

## Where to start

Read `ROUTER.md` first — it defines the session startup sequence and points to the current canonical doc and PDDA state.
