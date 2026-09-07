Reading additional input from stdin...
OpenAI Codex v0.153.4
--------
workdir: /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: read-only
reasoning effort: medium
reasoning summaries: none
session id: 01a07973-c8a4-7870-b438-8b1ca4bb3577
--------
user
You are an INDEPENDENT advisor in a one-shot cross-model consult. Another model is answering the SAME question separately and a coordinator will reconcile both answers, so give your own honest, specific read — do not hedge toward a consensus you cannot see. Read any repo files the question references (cite file:line). Respond with: (1) a short direct ANSWER; (2) graded FINDINGS — [Blocker]/[Should]/[Nit]/[Pass] — where applicable; (3) a one-line RECOMMENDATION. You are ADVISORY ONLY: output your analysis as text; do not rely on writing files (you are running in a throwaway copy).

=== CONSULT QUESTION ===
# Final QA — GH-11 Act 1 implementation (marathon complete, all 5 phases Approved)

Review the IMPLEMENTATION on this branch against its plan. This is the last gate before a PR.

## Read
- `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md` — the plan, acceptance and deviations
- `xyz/` — the delivered package (ingest, index, retrieve, eval, cli)
- `tests/` — 45 tests
- `validate.sh` / `prelaunch.sh` — the gate and readiness control
- `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md` → section "Run: XYZ hybrid retrieval round-trip (GH-11 Act 1)"

## Measured result to scrutinise
Depth-100, 30-query saturated LTVera-Pandas subset (339 files / 3,020 chunks):

| mode | MRR@100 | R@1 | miss |
|---|---|---|---|
| dense | 0.9444 | 0.9000 | 0 |
| BM25 | 0.8583 | 0.7667 | 0 |
| hybrid | 0.9222 | 0.8667 | 0 |
| hybrid+rerank | 0.9016 | 0.8667 | 0 |

Rerank latency: p50 50,003 ms / p95 93,867 ms on CPU. Reranker reordered 30/30 top-10s.

## Answer these, concisely
1. Is each Act 1 acceptance item actually satisfied by the code (not just claimed)? Cite file:line.
2. Did a duplicate subsystem, second writer, or parallel index path slip in? `xyz/index/store.py`
   is supposed to be the single writer. Two phases accidentally created nested `xyz/xyz/` copies
   which have now been deleted — confirm nothing references them and no logic was lost.
3. Do the tests substantiate the claims, or are any vacuous? Specifically check the `k = ?` SQL
   assertion, the incomplete-walk/WalkIncomplete guard, the FTS trigger evidence, the tau
   query-level contract, and the chunk-id-preserving reorder count.
4. **The headline concern:** dense-only beats hybrid and hybrid+rerank on this benchmark, and the
   reranker costs 50 s/query on CPU. Is that a defect in the implementation (bad fusion, bad BM25
   sanitiser, wrong rerank depth, wrong score signs) or a genuine property of a saturated 30-query
   set plus a general-domain reranker? Point at the code that decides it.
5. Anything that must be fixed BEFORE this becomes a PR, versus filed as follow-up.

Grade findings [Blocker]/[Should]/[Nit]/[Pass]. Be blunt. Do not pad.

codex
I’ll audit this as a verification pass against the stated acceptance criteria and runnable evidence. I’m first following the repository’s mandated startup sequence, then I’ll trace each requested contract to exact code and tests.
codex
I’m also applying the repository’s codebase-memory workflow so structural claims—especially the single-writer and no-parallel-path checks—are grounded in indexed relationships plus source verification.
exec
/bin/zsh -lc "sed -n '1,240p' ROUTER.md && sed -n '1,260p' /Users/noelsaw/.codex/skills/codebase-memory/SKILL.md" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 0ms:
# ROUTER.md

This file is the first entry point for an AI agent working in this repo: it tells you what to read, what to run, and which files are canonical.

## Role split

- `ROUTER.md` = startup order and canonical entry points
- `GUIDING-PRINCIPLES.md` = the north star; what the repo's goals and design tradeoffs answer to
- `AGENTS.md` = behavioral rules, decision quality, reversibility, blast radius, proof
- `README.md` = human-facing repo/product overview
- `ROADMAP.md` = pointer ledger for this repo's own maintenance work
- `CHANGELOG.md` = the end-of-iteration running log (first-class PDDA artifact; governed by `PROJECT/PDDA.md`)
- `RELEASES.md` = forward-looking release-planning ledger (first-class PDDA artifact; governed by `PROJECT/PDDA.md`)
- `PROJECT/PDDA.md` = the canonical PDDA contract and automation rules
- `utils/pdda/PDDA-INSTALL.md` = the extraction/install manifest PDDA was installed from
- `utils/pdda/pdda.sh` = the unified runnable surface (dispatcher + every deterministic check + `run`)
- `utils/pdda/pdda-doc-ready.sh` = the opt-in LLM readiness review; `utils/pdda/pdda-lib.sh` = shared helpers

## Startup sequence

1. Read `ROUTER.md` to understand the repo's operating order and canonical files. -> expect one clear next file, not a repo-wide scavenger hunt.
2. Read `GUIDING-PRINCIPLES.md` for the repo's north star. -> expect the goals and tradeoff lens that every design choice answers to.
3. Read `AGENTS.md` before making recommendations or edits. -> expect explicit assumptions, a reversibility read on consequential changes, and verified claims only.
4. Read `README.md` for the repo's purpose and baseline usage. -> expect a short explanation of what is canonical here.
5. If the task is about the PDDA contract or enforcement model, read `PROJECT/PDDA.md`. -> expect the source of truth for lifecycle, roadmap, changelog, and enforcement rules.
6. Read `ROADMAP.md` only for repo-local maintenance state. -> expect a pointer ledger, not a copied plan body from another repo.
7. Before reporting success on repo changes, run `utils/pdda/pdda.sh run` or the relevant single check (`utils/pdda/pdda.sh <check>`). -> expect deterministic findings first, then any LLM review.
8. If you are exploring an unknown system, proposing a new spike, or are blocked, search `PROJECT/3-COMPLETED/` and `CHANGELOG.md` for past context first. -> expect to recover memory of past struggles, gotchas, or decisions.

## Canonical rules

- Do not put phase checklists, build steps, or deep execution notes in `ROADMAP.md`.
- Do not edit `utils/pdda/**` in this repo. PDDA's runtime is installed here, not authored here; a local edit is overwritten the next time the runtime is synced from the canonical PDDA repo. Fix it upstream instead.
- `PROJECT/PDDA-ACTIVITY.jsonl` is runtime output, not source. It starts fresh in this repo and is gitignored.
- Every active doc in `PROJECT/2-WORKING/` must be reflected by a pointer in `ROADMAP.md` — a one-line ledger entry that links it. A working doc that should not appear opts out with `roadmap_exempt: true` in its frontmatter. Enforced by `utils/pdda/pdda.sh roadmap-coverage`; governance lives in `PROJECT/PDDA.md` -> "ROADMAP.md contract".
- Every captured GitHub issue doc in `PROJECT/1-INBOX/GH-*.md` must also be parked in `ROADMAP.md` as a one-line queue entry immediately at intake, then promoted or removed later. Enforced by `utils/pdda/pdda.sh roadmap-coverage`; governance lives in `PROJECT/PDDA.md` -> "GitHub issue intake" + "ROADMAP.md contract".
- The long-term canonical deterministic surface is `utils/pdda/pdda.sh`; do not add wrapper commands unless a real external integration forces them.
- Do not override deterministic PDDA findings with prose.
- Do not report a win you did not verify with the relevant script or test.
- Update `CHANGELOG.md` at the end of each iteration; its governance lives in `PROJECT/PDDA.md` — do not re-specify CHANGELOG rules in `AGENTS.md` or elsewhere.

## Command rails

For baseline verification and document hygiene:

```bash
utils/pdda/pdda.sh run
```

For targeted PDDA debugging, run a single check by name:

```bash
utils/pdda/pdda.sh frontmatter
utils/pdda/pdda.sh status-table
utils/pdda/pdda.sh hardcoded-paths
utils/pdda/pdda.sh roadmap
utils/pdda/pdda.sh roadmap-coverage
utils/pdda/pdda.sh changelog
utils/pdda/pdda.sh stale
utils/pdda/pdda.sh quad-concepts    # opt-in: a "## Quad Concepts" section of 1-4 bullets (lever: .pdda-quad / PDDA_QUAD)
utils/pdda/pdda.sh glance           # read-only roll-up: title + Quad Concepts for each PROJECT/2-WORKING doc
utils/pdda/pdda.sh issue-doc-sync   # flag GH-*.md docs drifted from their GitHub issue state (warn-only; gh-degrades to cache)
utils/pdda/pdda.sh releases    # validate RELEASES.md, the release-planning ledger (warn-only nudge)
utils/pdda/pdda.sh releases-current  # read-only roll-up: RELEASES.md entries whose Status isn't "Shipped"
utils/pdda/pdda.sh governance  # governance-doc cross-reference + doc/code drift (this file, AGENTS.md, CLAUDE.md, ...)
utils/pdda/pdda.sh gh-refresh  # refresh the cached GitHub issue-state file issue-doc-sync reads offline (needs gh)
utils/pdda/pdda.sh doc-ready   # LLM readiness review — set PDDA_LLM_BIN (codex/claude/agy) for recommendations, else it self-skips
utils/pdda/pdda.sh catchup     # LLM repo triage and ROUTER.md recommendations — opt-in like doc-ready
utils/pdda/pdda.sh help        # list every command
```

## Routing hints

- If the task is about document quality, active-doc lifecycle, roadmap sprawl, or automation policy, start in `PROJECT/PDDA.md`.
- If the task is about repo-local maintenance state, start in `ROADMAP.md`.
- If the task is about the changelog, provenance, or end-of-iteration logging, the governance is in `PROJECT/PDDA.md` (the "CHANGELOG.md — end-of-iteration record" contract).
- To re-run this startup sequence mid-session (task switch, resume, post-compact, context drift), invoke the `/pdda` skill (`.claude/skills/pdda/SKILL.md`) instead of re-reading by hand.

<!-- Written by PDDA's installer from the target-router template in the canonical PDDA repo. This is a
     scaffold: your repo owns it now, and the installer will not overwrite it again without --force.
     Sections that only apply to the canonical repo (distributing the runtime, the install and sync
     command rails) are deliberately absent — the scripts they name are not installed here. -->
---
name: codebase-memory
description: "Use the codebase knowledge graph for structural code queries. Triggers on: explore the codebase, understand the architecture, what functions exist, show me the structure, who calls this function, what does X call, trace the call chain, find callers of, show dependencies, impact analysis, dead code, unused functions, high fan-out, refactor candidates, code quality audit, graph query syntax, Cypher query examples, edge types, how to use search_graph."
---

# Codebase Memory — Knowledge Graph Tools

Graph tools return precise structural results in ~500 tokens vs ~80K for grep.

## Quick Decision Matrix

| Question | Tool call |
|----------|----------|
| Who calls X? | `trace_path(direction="inbound")` |
| What does X call? | `trace_path(direction="outbound")` |
| Full call context | `trace_path(direction="both")` |
| Find by name pattern | `search_graph(name_pattern="...")` |
| Dead code | `search_graph(max_degree=0, exclude_entry_points=true)` |
| Cross-service edges | `query_graph` with Cypher |
| Impact of local changes | `detect_changes()` |
| Risk-classified trace | `trace_path(risk_labels=true)` |
| Text search | `search_code` or Grep |

## Exploration Workflow
1. `list_projects` — check if project is indexed
2. `get_graph_schema` — understand node/edge types
3. `search_graph(label="Function", name_pattern=".*Pattern.*")` — find code
4. `get_code_snippet(qualified_name="project.path.FuncName")` — read source

## Tracing Workflow
1. `search_graph(name_pattern=".*FuncName.*")` — discover exact name
2. `trace_path(function_name="FuncName", direction="both", depth=3)` — trace
3. `detect_changes()` — map git diff to affected symbols

## Evidence Tiers
- **Scout (Tier 1):** fast positive lookup with few graph calls and targeted source checks. Treat results as provisional; never make absence, exhaustive, dead-code, or complete-impact claims.
- **Verify (Tier 2, default):** task-directed searches, relevant trace directions, exact snippets for material claims, and all relevant result pages.
- **Auditor (Tier 3):** bounded-scope full verification with a current graph generation, complete relevant pagination, both call directions and broader relationships when material, plus explicit unresolved limitations.
- **Every tier:** after candidate paths are known, call `check_index_coverage` once with every evidence path. For negative or exhaustive claims also include the relevant scopes. A clean result means no recorded gap, not proof of completeness. For partial, skipped, excluded, stale, pending, or unknown coverage, read/grep the reported ranges or scope before relying on the graph.

## Sessions and Subagents
- At session start or after compaction, call `list_projects`/`index_status` before structural exploration, then choose Scout, Verify, or Auditor for the task.
- Before delegating, query the graph and coverage in the parent. Pass the tier, exact project, generation/freshness, bounded scope, queries and pagination state, qualified symbols, paths, call-chain findings, coverage ranges/reasons, source fallback already performed, and unresolved questions to the child.
- Runtimes such as Hermes isolate child context: put those graph findings in the `context` argument to `delegate_task`; do not assume the child inherits MCP access or the parent's conversation.
- A child without MCP tools must not call or claim MCP access. It should work from the supplied evidence and use read/grep on exact source, especially every reported missed-coverage range.

## Quality Analysis
- Dead code: `search_graph(max_degree=0, exclude_entry_points=true)`
- High fan-out: `search_graph(min_degree=10, relationship="CALLS", direction="outbound")`
- High fan-in: `search_graph(min_degree=10, relationship="CALLS", direction="inbound")`

## 15 MCP Tools
`index_repository`, `index_status`, `list_projects`, `delete_project`,
`search_graph`, `search_code`, `trace_path`, `detect_changes`,
`query_graph`, `get_graph_schema`, `get_code_snippet`, `get_architecture`,
`check_index_coverage`, `manage_adr`, `ingest_traces`

## Edge Types
CALLS, HTTP_CALLS, ASYNC_CALLS, DATA_FLOWS, IMPORTS, DEFINES, DEFINES_METHOD,
HANDLES, IMPLEMENTS, OVERRIDE, USAGE, CALL_REFERENCE, CONFIGURES, FILE_CHANGES_WITH,
SIMILAR_TO, SEMANTICALLY_RELATED, CONTAINS_FILE, CONTAINS_FOLDER,
CONTAINS_PACKAGE

## Cypher Examples (for query_graph)
```
MATCH (a)-[r:HTTP_CALLS]->(b) RETURN a.name, b.name, r.url_path, r.confidence LIMIT 20
MATCH (f:Function) WHERE f.name =~ '.*Handler.*' RETURN f.name, f.file_path
MATCH (a)-[r:CALLS]->(b) WHERE a.name = 'main' RETURN b.name
```

## Gotchas
1. `search_graph(relationship="HTTP_CALLS")` filters nodes by degree — use `query_graph` with Cypher to see actual edges.
2. `query_graph` has a 100k row ceiling — add a Cypher `LIMIT` for broad queries or use `search_graph` pagination.
3. `trace_path` needs exact names — use `search_graph(name_pattern=...)` first.
4. `direction="outbound"` misses cross-service callers — use `direction="both"`.
5. `search_graph` results default to 50 per page — check `has_more` and use `offset`.

exec
/bin/zsh -lc "sed -n '1,260p' GUIDING-PRINCIPLES.md && sed -n '1,300p' AGENTS.md && sed -n '1,260p' README.md" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 0ms:
# Guiding Principles

The north star this repo's goals and implementation decisions answer to. When a design choice is
unclear, the option that better serves these principles wins.

## Purpose

XYZ Code Intelligence is a **local-first code retrieval system** for answering natural-language
questions about codebases. It is the planned successor to Ask-Self, combining dense and lexical
retrieval with reranking on the operator's machine while keeping the repository's work state
reliable for long-running human and AI-agent collaboration.

## Principles

1. **Docs are the runtime state, not a record of it.** The current `PROJECT/**` docs *are* the
   project's state. If reality and the docs disagree, that is the bug to fix.
2. **Resumable by a cold agent.** Every active doc must let an agent with zero prior context answer
   "what was just done, what's next" in seconds — that's why the status header is a contract.
3. **Deterministic where judgment isn't needed.** Scripts enforce the mechanical rules; the LLM
   reviewer only handles what regex can't. Never make an agent re-decide settled hygiene.
4. **One canonical place per fact.** `ROADMAP.md` points, project docs hold detail, `CHANGELOG.md`
   logs outcomes. No fact lives in two places where they can drift.
5. **A clear signal of what is live.** `PROJECT/2-WORKING` holds only truly active work, so "what
   should an agent pick up" is never ambiguous.
6. **Low-friction and portable.** The contract must be cheap to adopt (a one-command install) and
   cheap to obey, or agents will route around it.
7. **Default to the reversible action; require evidence for the expensive one.** When an item is
   stale, orphaned, or its dependency has left the repo, *close / park / archive is the default* —
   those are cheap and undoable. Keeping it open is what costs: it buys recurring triage attention on
   every future pass. So the burden of proof sits on **keeping**, not on closing. State a default and
   the one fact that would overturn it, rather than presenting symmetric options — "close as obsolete,
   or re-scope?" is how an item sits untouched for nine days.
8. **A finding that was reported is not a finding that was seen.** Detection is only half a check.
   If a run's closing line contradicts its own output, the signal is lost no matter how correct the
   detector was — so summary lines must reflect what was actually found. Corollary of #3: being
   deterministic about *detecting* is wasted if the *reporting* rounds it off.
9. **Local-first.** Ingest, embedding, retrieval, and reranking run on the operator's machine with
   no network call on the query path. A cloud API may appear only as an explicitly opt-in comparison
   arm, never as the primary lane.
10. **Permissively licensed models only.** Every model weight the pipeline loads is Apache-2.0 or
    MIT (or equivalent). Verify the licence on the model card before a model enters any run; a model
    whose licence is unstated or non-commercial is rejected, not deferred.

## How to apply

When adding a feature or making a tradeoff, ask: *does this make project state more resumable,
less ambiguous, and harder to drift for a long-running agent?* If not, reconsider.

When triaging existing work, ask: *what is the reversible move here, and what single fact would
argue against it?* Then say that, rather than listing options.
# AGENTS.md

**On your first action in this repo, follow the startup sequence in `ROUTER.md` before recommending or editing anything.** It names the canonical files and the order to read them. Re-run it (or `/pdda`) when you switch tasks, resume a long session, or feel context has drifted.

See `GUIDING-PRINCIPLES.md` for the repo's north star — the goals and tradeoff lens these rules serve.

## Operating principles

These apply to every response, plan, and change in this repo.

### 1. Lead with the call

The first sentence says what changed or what the verdict is. Supporting detail comes after.

### 2. State the bet before acting

Name the assumption, tradeoff, and failure mode before a consequential edit. If the claim cannot be wrong, it is probably too vague.

### 3. Use one reversibility scale

Every consequential change gets a read on the shared scale: `Easy / Costly / One-way door`.

### 4. Verify instead of implying

Do not report a win you did not verify. In this repo, `utils/pdda/pdda.sh run` is the main rail unless a narrower single check (`utils/pdda/pdda.sh <check>`) is more appropriate.

### 5. Keep the installer surface in lockstep

If a PDDA script is added, removed, or behaviorally changed, update the matching contract docs in the same change:

- `PROJECT/PDDA.md`
- `utils/pdda/PDDA-INSTALL.md`
- any repo-facing startup docs that describe the shipped surface

### 6. Keep this repo about PDDA

This is the standalone PDDA source-of-truth repo. Favor changes to the document contract, install manifest, and shipped shell checks. Do not pull in unrelated runtime or product docs from other repos.

### 7. Record substantive iterations

Update `CHANGELOG.md` at the end of a substantive iteration. `PROJECT/PDDA.md` owns the contract for what belongs there.

## Working in this repository

- The canonical PDDA contract lives in `PROJECT/PDDA.md`.
- The runnable install surface lives in `utils/pdda/pdda.sh` (checks + runner), `utils/pdda/pdda-doc-ready.sh` (LLM layer), and `utils/pdda/pdda-lib.sh` (shared helpers).
- The extraction contract lives in `utils/pdda/PDDA-INSTALL.md`.
- `ROADMAP.md` is this repo's pointer ledger, not a second plan body.
- `PROJECT/PDDA-ACTIVITY.jsonl` is runtime output, not install history to copy into target repos.
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

mcp: codebase-memory-mcp/list_projects started
mcp: codebase-memory-mcp/list_projects (completed)
mcp: codebase-memory-mcp/index_repository started
mcp: codebase-memory-mcp/index_repository (completed)
exec
/bin/zsh -lc "git status --short && rg --files xyz tests | sort && rg -n '"'^#{1,4} |Acceptance|Deviation|Run: XYZ hybrid retrieval round-trip'"' PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 3286ms:
2026-09-06 18:21:07.866 xcodebuild[40288:487467342]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:21:08.300 xcodebuild[40288:487467303] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-cn8ThZZA' (errno=Operation not permitted)
2026-09-06 18:21:09.058 xcodebuild[41744:487469434]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:21:09.248 xcodebuild[41744:487469341] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
?? relay-system/2026-09-06/gh11-act1-final-qa-182025/
tests/__init__.py
tests/fakes.py
tests/fixtures/mini-repo/Dockerfile
tests/fixtures/mini-repo/app/example.php
tests/fixtures/mini-repo/app/example.py
tests/fixtures/mini-repo/app/example.ts
tests/fixtures/mini-repo/broken.py
tests/fixtures/mini-repo/config.yml
tests/fixtures/mini-repo/docs/guide.md
tests/fixtures/mini-repo/node_modules/ignored.js
tests/test_chunkers.py
tests/test_cli.py
tests/test_metrics.py
tests/test_retrieve.py
tests/test_smoke.py
tests/test_store.py
xyz/__init__.py
xyz/__main__.py
xyz/cli.py
xyz/eval/__init__.py
xyz/eval/metrics.py
xyz/index/__init__.py
xyz/index/embed.py
xyz/index/store.py
xyz/ingest/__init__.py
xyz/ingest/chunk.py
xyz/ingest/walk.py
xyz/retrieve/__init__.py
xyz/retrieve/dense.py
xyz/retrieve/fuse.py
xyz/retrieve/latency.py
xyz/retrieve/lexical.py
xyz/retrieve/models.py
xyz/retrieve/pipeline.py
xyz/retrieve/rerank.py
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:28:# GH-11 Act 1 — XYZ hybrid retrieval library
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:36:## Status
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:42:## Observed problem
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:58:## Recon (base `3301124`, 2026-09-05)
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:86:## Acceptance — deviations from the issue
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:118:## Plan — five marathon phases, strictly sequential
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:132:## Dependencies, risks, rollback
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:163:## Rating (RELEASES ledger, 2026-09-05)
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:171:## Swarm Preflight Contract
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:208:## Run log
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:20:# FINDINGS-0.5.md
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:41:## Status
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:49:## 1. Corpus
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:72:## 2. Test query results (per repo, top-3)
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:77:### rebalanceOS
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:85:### LTVera-Pandas
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:93:### aegis-sleuth-slack-bot
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:101:### XYZ-forge
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:115:## 3. Finding: file paths are not embedded, so name-carried meaning is lost
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:141:## 4. Finding: the chunker cannot see YAML or Dockerfiles
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:158:## 5. Finding: the original failure diagnosis was wrong
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:183:## 6. CodeRankEmbed vs Gemini — measured, and it is a tie
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:205:### Cost and speed
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:216:### Recommendation
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:225:## 7. Querying is cheap — the expensive part is a one-off
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:247:## 8. Open items
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:264:## Run: XYZ hybrid retrieval round-trip (GH-11 Act 1) — 2026-09-06
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:271:### Corpus and ingest provenance
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:287:### Retrieval quality at depth 100
PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md:301:### Latency (milliseconds, p50 / p95)

exec
/bin/zsh -lc "nl -ba PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md | sed -n '1,360p'
nl -ba PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md | sed -n '250,350p'" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 0ms:
     1	---
     2	gh_issue: 11
     3	source: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11
     4	title: GH-11 Act 1 — XYZ hybrid retrieval library (canonical doc Phase 0 + Phase 1)
     5	status: active
     6	created: 2026-09-05
     7	updated: 2026-09-06
     8	owner: Noel Saw
     9	goal: Ship the importable XYZ retrieval library — Tree-sitter chunking, SQLite chunks + FTS5 + sqlite-vec store with a provider-keyed embed cache and drift guard, and a BM25 + dense → RRF → cross-encoder rerank query path — verified by an ingest/query round-trip on one real repo, so Acts 2-5 of the v0.5 release are unblocked.
    10	doc_type: feedback
    11	effort: 4
    12	complexity: 4
    13	risk: 2
    14	phases: 5
    15	related:
    16	  - "PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md"
    17	  - "PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md"
    18	  - "PROJECT/2-WORKING/v0.5/GH-6-LOCAL-ONLY-SCORER.md"
    19	context_tags: [retrieval, hybrid-search, fts5, sqlite-vec, rrf, rerank, tree-sitter, chunking, marathon]
    20	non_goals:
    21	  - Absorbing Ask-Self's ingest/synthesis/history code (Act 2-3 of #11) — only the embed-cache semantics are ported here
    22	  - Any Slack, HTTP or MCP surface (Acts 3-4 of #11)
    23	  - The 250-query frozen benchmark (canonical doc Phase 2) — the 30-query LTVera-Pandas set is the gate for this act
    24	  - Model bake-off, fine-tuning, ONNX/int8 serving (Phases 3-4, GH-5) — CodeRankEmbed via sentence-transformers is the placeholder dense lane
    25	  - Ask-Self sunset (Phase 5)
    26	---
    27	
    28	# GH-11 Act 1 — XYZ hybrid retrieval library
    29	
    30	Capture of **Act 1** of [issue #11](https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11)
    31	("Build the XYZ retrieval library — the keystone, start here"). In the
    32	[canonical build doc](<XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md>) this is
    33	**Phase 0 steps 2-3 plus all of Phase 1**. Executed as one five-phase marathon
    34	(`GH-11-marathon/MARATHON.yaml`), builder Codex, reviewer agy.
    35	
    36	## Status
    37	
    38	| What was just completed | What's next |
    39	|---|---|
    40	| Built p4 CLI/evaluator and completed the real labelled-subset round-trip: 3,020 chunks, second ingest 8.62 s with zero embeddings, four modes scored, 30/30 reranked (2026-09-06). | agy reviews p4 implementation and recorded evidence; if approved, Act 1 is ready for orchestrator close-out. |
    41	
    42	## Observed problem
    43	
    44	- The XYZ hybrid retrieval library does not exist. The repo has a throwaway embedder
    45	  (`.embed-tmp/scripts/embed_repos.py`) that writes `chunks.jsonl` + `embeddings.npy` sidecars, a
    46	  brute-force query script (`.embed-tmp/scripts/query_repos.py`), and a scorer
    47	  (`.embed-tmp/eval/score_retrieval.py`) — no package, no SQLite store, no BM25 lane, no fusion,
    48	  no reranker. Issue #11 names this as the blocker for every downstream act.
    49	- Canonical doc Phase 0 is only partly done: the doc is ratified (step 1) but there is no package
    50	  scaffold (step 2) and the licensing / local-first constraints are not in `GUIDING-PRINCIPLES.md`
    51	  (step 3). `GUIDING-PRINCIPLES.md` and `AGENTS.md` are still the PDDA-repo boilerplate.
    52	- Evidence gap: issues #2, #8, #14 are closed as "fixed in the Run 12 batched re-embed" (MRR 0.978)
    53	  but that code and `BENCHMARKS.md` Runs 11-15 are on **no branch of `origin`** and no clone on this
    54	  machine. The branch this work is based on (`origin/v0.5/embedding-eval-coderankembed-vs-gemini`,
    55	  `3301124`) carries Runs 1-10 (baseline Run 9: MRR 0.801 / R@1 0.700). The chunker changes those
    56	  issues describe (path-prefix per #8, wider include list per #2) are therefore re-implemented in p1.
    57	
    58	## Recon (base `3301124`, 2026-09-05)
    59	
    60	- Existing writer for chunks: `.embed-tmp/scripts/embed_repos.py` — `INCLUDE_EXT`, `iter_files`
    61	  (~line 106), per-chunk records with `path`, `start_line`, `end_line`, `text` plus `id`/`repo`
    62	  (~136-140, ~160-161), per-repo re-exec, batch 16, `EMBED_PROFILE` telemetry. It does **not** set
    63	  `max_seq_length`; the 2048 cap is a FINDINGS-0.5.md requirement (~174-179) that the new embedder
    64	  must set and test. `qualified_name`, `kind`, `content_sha`, `embedded_text` are new fields. Keep
    65	  the script untouched; the library supersedes it, and it stays as the benchmark-history tool.
    66	- Existing metric definitions: `.embed-tmp/eval/score_retrieval.py` — `rank_of_first_relevant`
    67	  (~133-138), MRR with misses as 0, recall@{1,3,5,10}, `never_found`, `per_query` (~141-156); hit =
    68	  retrieved chunk `path` in `relevant`. It ranks the **whole corpus**; the hybrid pipeline ranks
    69	  `fetch_k` candidates, so p4 reports the same metrics **at an explicit depth D = 100** with its own
    70	  dense-only arm at that depth as the baseline. Run 9 is context, not a comparable number.
    71	- Labelled set: `.embed-tmp/eval/queries-LTVera-Pandas.json` — 30 queries, file-path gold labels,
    72	  saturated at R@3+ after the path-prefix fix (issue #11 caveat 2). Deltas under 0.05 are noise
    73	  (GH-5 doc).
    74	- Runtime facts that shape the briefs (FINDINGS-0.5.md, SOP.md): query prefix
    75	  `"Represent this query for searching relevant code: "` on queries only; `trust_remote_code=True`;
    76	  MPS and CPU vectors identical; model load ≈ 11.6 s so one long-lived model per process; MPS
    77	  allocations are invisible to RSS, `max_seq_length` is the real memory guard; sentence-transformers'
    78	  `backend="onnx"` is broken for this model — do not use it.
    79	- Ask-Self inheritance actually needed here (issue #11 carve-out 1): cache keyed by
    80	  `(content_sha, model, dim, provider)` and a provider/dim mismatch guard. Reference:
    81	  `ask_self_cache.py` and `detect_provider_mismatch` in the sibling `ask-self` checkout — port the
    82	  semantics, not the file. Also inherit the `vec0` `k = ?` KNN form (Ask-Self issue #23: parameterised
    83	  `LIMIT ?` 500'd in production).
    84	- Untraced: Sleuth's Node `src/rag/` and Ask-Self's ingest planner — out of scope for Act 1.
    85	
    86	## Acceptance — deviations from the issue
    87	
    88	The issue's Act 1 checklist, with what this doc owns:
    89	
    90	- XYZ hybrid retrieval library exists as an importable Python package with a clean API (in-process
    91	  within Python) — **kept**, p0-p3.
    92	- Hybrid retrieval beats vector-only on the labelled set — **[changed]** to: hybrid+rerank MRR and
    93	  R@1 on the 30-query set are ≥ dense-only minus the 0.05 noise floor, and the reranker measurably
    94	  reorders RRF output — reason: the issue itself records the 30-query set as saturated, so "beats"
    95	  cannot be resolved on it; growing the set is human labelling work (canonical Phase 2), not a
    96	  builder task.
    97	- Use the `vec0` `k = ?` KNN form, not parameterised `LIMIT ?` — **kept**, p3, with a test that
    98	  asserts the query text.
    99	- Measure batch indexing RSS on ARM — **[dropped]** — reason: no ARM box is in scope for this
   100	  marathon; the p4 run records RSS on the build machine instead and leaves the ARM row for Act 5.
   101	- "…over the existing 21,580-vector sidecar" — **[changed]** to a fresh ingest of one repo — reason:
   102	  the sidecars are gitignored and not on this branch, and the p1 chunker (path prefix, wider walk)
   103	  changes every chunk, so old vectors would be invalid anyway (FINDINGS-0.5.md: index and query
   104	  model/chunks must match).
   105	- REFACTOR / ABSORB of Ask-Self's revision tracking, ingest planner and harness config
   106	  (issue #11 calibration) — **[dropped]** here, owned by Act 2 — reason: Act 1 needs only the
   107	  cache-key + mismatch semantics (carve-out 1) to be correct; the XYZ file-sha planner in
   108	  `xyz/index/store.py` is the single planner Act 2 reconciles Ask-Self's onto (no second
   109	  planner/store is created here, so nothing is duplicated to remove later).
   110	- "beats vector-only on a **non-saturated** query set" (exit criterion) — **[changed]**, remains
   111	  **outstanding** after this act — reason: growing the set is canonical Phase 2 human labelling; this
   112	  act's gate is the noise-floor comparison above and does not claim to close that criterion.
   113	
   114	Canonical doc Phase 1 QA gate, adopted verbatim as this act's gate: ingest + query round-trip on
   115	one real repo; unchanged re-ingest is near-instant (planner dedupe works); rerank stage measurably
   116	reorders RRF output; latency instrumented (p50/p95).
   117	
   118	## Plan — five marathon phases, strictly sequential
   119	
   120	| Phase | Scope | Artifacts | Gate |
   121	|---|---|---|---|
   122	| `gh11-p0-scaffold` | Phase 0 close-out: constraints into `GUIDING-PRINCIPLES.md`, `pyproject.toml`, `xyz/` package skeleton, `tests/`, extend `validate.sh` | `GUIDING-PRINCIPLES.md`, `pyproject.toml`, `xyz/`, `tests/`, `validate.sh` | `bash validate.sh`: package imports, pytest green, PDDA checks green |
   123	| `gh11-p1-chunkers` | Tree-sitter chunkers (Python, JS/TS, PHP), heading-level Markdown, file-level config/templates; path-prefixed embedded text (#8); widened include list (#2) | `xyz/ingest/`, `tests/` | pytest on a fixture tree: function-aligned chunks with `qualified_name`/`start_line`/`end_line`, YAML/Dockerfile chunked, every chunk's `embedded_text` starts with its path |
   124	| `gh11-p2-store` | SQLite store: `chunks` + FTS5 + `vec0`; embed cache keyed `(content_sha, model, dim, provider)`; file-level drift/planner so unchanged re-ingest embeds nothing; provider/dim mismatch refuses | `xyz/index/`, `tests/` | pytest with a fake embedder: second ingest calls the embedder 0 times; mismatch raises; FTS5 and vec0 row counts equal `chunks` |
   125	| `gh11-p3-retrieve` | Query path: BM25 (FTS5) ∥ dense (`vec0`, `k = ?`) → RRF(k=60) → cross-encoder rerank top 25-50 → optional no-answer τ; per-stage latency + p50/p95 helper | `xyz/retrieve/`, `tests/` | pytest with fake embedder + fake reranker: a doc ranked low by both lanes but high by the reranker ends at rank 1; RRF matches the hand-computed value; `k = ?` present in the KNN SQL; τ suppresses below-threshold |
   126	| `gh11-p4-roundtrip` | `xyz` CLI (`ingest`, `query`, `eval`); real round-trip on the sibling LTVera-Pandas checkout with CodeRankEmbed; dense vs hybrid vs hybrid+rerank scored with Run-9 metric definitions; record results | `xyz/cli.py`, `xyz/eval/`, `FINDINGS-0.5.md`, this doc | the four Phase 1 QA-gate bullets above, evidenced in FINDINGS-0.5.md with numbers |
   127	
   128	Existing subsystem extended: the `.embed-tmp` embedder + scorer become the **reference** the new
   129	`xyz/` package must reproduce (same chunk fields, same metrics); nothing is duplicated in `.embed-tmp`.
   130	Canonical writer for the index is `xyz/index/store.py` — one SQLite file per index, one writer.
   131	
   132	## Dependencies, risks, rollback
   133	
   134	- Environment contract (defined in `validate.sh`, values exported by the operator when firing):
   135	  `XYZ_PY` (interpreter with the pinned deps; default `<repo>/.venv/bin/python`), `XYZ_SCRATCH`
   136	  (generated evidence; default `<repo>/.relay-scratch`, the harness's swept scratch dir — nothing
   137	  goes under `temp/`), `XYZ_EVAL_REPO` (absolute path to the LTVera-Pandas checkout; p4 fails fast if
   138	  unset), `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1`. Readiness is a two-step control:
   139	  **`prelaunch.sh`** (operator, before firing) really imports every dependency, instantiates the five
   140	  Tree-sitter parsers and loads both models offline with their real classes (encode + predict) using
   141	  the exact `XYZ_PY`, then writes `<venv>/xyz-prelaunch.json`; **`validate.sh`** (every phase)
   142	  requires that marker for the same interpreter and repeats the cheap checks (real imports, parser
   143	  creation, FTS5/vec0). Red controls for the operator step: run `prelaunch.sh` with `HF_HOME` pointed
   144	  at an empty directory → NOT READY on CodeRankEmbed; with a bogus `XYZ_PY` → not executable. No `pip install` and no editable install inside a turn (the latter
   145	  writes `*.egg-info/` into the tree); `PYTHONPATH=<repo>` makes `xyz` importable.
   146	- Risk — p4 embedding time: ~5,100+ chunks at ~0.3 s/chunk on MPS ≈ 25-35 min; the turn timeout is
   147	  7200 s. The CLI prints an ETA after 200 chunks; > 45 min triggers the fallback: a **fresh** DB
   148	  ingested in one root-preserving invocation restricted to `scripts/`, `app/`, `alembic/` (every gold
   149	  label lives there), labelled `corpus: subset` wherever reported.
   150	- Containment: `CHANGELOG.md` is not on any phase allowlist by design — the orchestrator writes the
   151	  end-of-iteration entry when opening the PR (AGENTS.md §7).
   152	- Risk — reranker choice is a placeholder: `mixedbread-ai/mxbai-rerank-xsmall-v1` (Apache-2.0,
   153	  ~70 MB) is general-domain and configurable via `XYZ_RERANKER`; the bake-off (Phase 3) picks the
   154	  real one, and the p3 gate tests behaviour with a fake reranker so the placeholder cannot make the
   155	  gate flaky. **Changed 2026-09-06:** the original choice `cross-encoder/ms-marco-MiniLM-L-6-v2`
   156	  loads cleanly on this stack (torch 2.14.0 / transformers 5.16.1) but returns `[nan, nan]` — an
   157	  old-format BERT checkpoint, reproduced with plain `AutoModelForSequenceClassification` under both
   158	  `eager` and `sdpa`. Found by `prelaunch.sh` before the marathon fired; `prelaunch.sh` now asserts
   159	  finite *and* correctly-ordered scores. Fallback: `BAAI/bge-reranker-base` (MIT, also verified).
   160	- Reversibility: **Easy** — all new files under `xyz/`, `tests/`, `pyproject.toml`, `validate.sh`;
   161	  one small edit to `GUIDING-PRINCIPLES.md`; nothing in `.embed-tmp` changes. Revert = drop the branch.
   162	
   163	## Rating (RELEASES ledger, 2026-09-05)
   164	
   165	`rated 85/60/50/30` — pri 85: issue #11 names this act as the keystone every other act is blocked
   166	on, and the user ordered it first. sev 60: not a defect; the consequence is blocked work across the
   167	whole v0.5 release, not data loss. appeal 50: neutral, no user preference given. effort 30: five
   168	phases, new package, one 30-minute real-corpus run — a multi-day build, not a quick win. Recurrence:
   169	n/a (feature). No operator override.
   170	
   171	## Swarm Preflight Contract
   172	
   173	```json
   174	{
   175	  "target": { "repo": ".", "ref": "marathon/gh11-act1-hybrid-retrieval-2026-09-05" },
   176	  "gate": "bash validate.sh",
   177	  "fix_probes": [
   178	    { "type": "path_absent", "path": "pyproject.toml" },
   179	    { "type": "path_absent", "path": "xyz/" },
   180	    { "type": "path_absent", "path": "tests/" },
   181	    { "type": "path_absent", "path": "xyz/retrieve/pipeline.py" }
   182	  ],
   183	  "artifacts": [
   184	    "GUIDING-PRINCIPLES.md",
   185	    "pyproject.toml",
   186	    "validate.sh",
   187	    "xyz/",
   188	    "tests/",
   189	    "PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md",
   190	    "PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md"
   191	  ],
   192	  "artifacts_new": [
   193	    "pyproject.toml",
   194	    "xyz/",
   195	    "tests/"
   196	  ],
   197	  "remediation": {
   198	    "source": "self#phases",
   199	    "criteria": "Phases gh11-p0-scaffold through gh11-p4-roundtrip of this doc, each gated by bash validate.sh"
   200	  },
   201	  "lanes": {
   202	    "agy_safe": [],
   203	    "orchestrator_only": [".tick/", "marathon-system/", "relay-system/"]
   204	  }
   205	}
   206	```
   207	
   208	## Run log
   209	
   210	- 2026-09-05 — clone `XYZ-code-intelligence-gh11-act1`, branch
   211	  `marathon/gh11-act1-hybrid-retrieval-2026-09-05` off `origin/v0.5/embedding-eval-coderankembed-vs-gemini`
   212	  (`3301124`, stacked: no PR exists for that branch yet). Venv provisioned, reranker pre-cached.
   213	- 2026-09-06 — preflight ready (exit 0), `marathon.sh --dry-run` OK (5 phases in order). Codex plan
   214	  review (`relay-system/2026-09-06/gh11-act1-plan-review.md`), three rounds, 13 findings, all
   215	  implemented:
   216	  - **r1** — metric depth, environment contract, subset fallback, red controls, grounding, chunk
   217	    contract, deviation accounting, containment, API defaults.
   218	  - **r2** — vacuous readiness check, incomplete-walk pruning, rerank-tail policy + chunk-id
   219	    evidence, BM25 score direction, contradictory changed-token test. Implementing the readiness
   220	    control (`prelaunch.sh`) **found two real defects before any builder turn**: (1)
   221	    `tree_sitter_language_pack` downloads grammars at first use, so every offline turn would have
   222	    failed at the chunker — now pre-cached and asserted; (2) `cross-encoder/ms-marco-MiniLM-L-6-v2`
   223	    loads cleanly on torch 2.14.0 / transformers 5.16.1 and returns `[nan, nan]` — default reranker
   224	    changed to `mixedbread-ai/mxbai-rerank-xsmall-v1`.
   225	  - **r3** — readiness marker not invalidated on failure and not bound to the validated reranker /
   226	    cache (my own red-control run had left a stale success marker); τ specified as a query-level
   227	    decision, not a per-hit filter; scorer input takes `(chunk_id, path)` records so same-path
   228	    reorders survive. All fixed; `prelaunch.sh` now deletes the marker before testing and publishes
   229	    it atomically, and `validate.sh` rejects it when `XYZ_RERANKER` or the HF cache differs.
   230	  - **Round cap 3/3 exhausted → `STATUS: Escalated`.** Implementation is stopped pending an operator
   231	    decision: extend the cap for a round-4 re-review of the r3 fixes, or accept the plan explicitly.
   232	    The marathon was **not** fired.
   233	- 2026-09-06 — p4 round-trip built and measured. The full corpus was projected at 17,258 chunks;
   234	  its real CPU run triggered the documented fallback at 204 chunks with a 206.5-minute ETA. The
   235	  fresh root-preserving `scripts/` + `app/` + `alembic/` subset indexed 339 files / 3,020 chunks in
   236	  1,664.72 s wall at 9,852.62 MB peak RSS. Identical re-ingest took 8.62 s and embedded zero chunks.
   237	  Depth-100 results: dense MRR/R@1 0.9444/0.9000; BM25 0.8583/0.7667; hybrid 0.9222/0.8667;
   238	  hybrid+rerank 0.9016/0.8667, with zero misses in every arm and 30/30 top-10 chunk-id sequences
   239	  reordered. The reranked arm remains within the 0.05 acceptance tolerance of dense on both load-
   240	  bearing metrics. Full per-stage p50/p95 and QA-gate evidence are recorded in FINDINGS-0.5.md.
   250	  needs re-index + re-score.
   251	- **Widen `INCLUDE_EXT`** to cover YAML and extensionless files (issue #2) — requires
   252	  re-embedding, since the corpus changes.
   253	- **int8 quantization experiment** (issue #5) — for query latency on Intel, not memory.
   254	  Note Unsloth is the wrong tool (decoder-only LLMs, CUDA); the path is
   255	  `export_dynamic_quantized_onnx_model` / `export_static_quantized_openvino_model`.
   256	- **Verify on real Intel hardware** — everything in issue #4 is extrapolated from an M4 Pro.
   257	- **Grow the labelled set beyond 30 queries / one repo** if a small real quality difference
   258	  ever needs resolving.
   259	- `query_repos.py` still derives `OUT_ROOT` from its own location and cannot see the
   260	  sidecars now that they live in `temp/`; it needs the same override the embedding runs use.
   261	
   262	---
   263	
   264	## Run: XYZ hybrid retrieval round-trip (GH-11 Act 1) — 2026-09-06
   265	
   266	This run used the new `xyz` SQLite/FTS5/sqlite-vec pipeline and the existing 30-query labelled
   267	LTVera-Pandas set. Metrics are depth-bounded: **MRR@100 / R@k / miss@100**, with chunk ranks and
   268	no path de-duplication. Run 9's MRR 0.801 / R@1 0.700 ranked the full corpus with the old chunker
   269	and is context only, not a directly comparable baseline.
   270	
   271	### Corpus and ingest provenance
   272	
   273	- **corpus: subset** — one root-preserving invocation with `scripts/`, `app/`, and `alembic/`;
   274	  every gold path was verified present in `chunks.path` before scoring.
   275	- **339 files / 3,020 chunks**; chunker version = **this commit** (including byte-offset-derived
   276	  source lines, avoiding corrupt native Tree-sitter point metadata observed during the full run).
   277	- Full-corpus attempt: 1,793 files / 17,258 chunks projected by the fake-model dry run. The real
   278	  CPU ingest was aborted at 204 chunks when the required early estimate reported **206.5 min**,
   279	  above the 45-minute fallback threshold.
   280	- First subset ingest: **1,664.72 s wall** (27m 44.72s); `files_seen=339`,
   281	  `chunks_written=3,020`, `chunks_embedded=3,020`; peak RSS **9,852.62 MB**.
   282	- Identical second ingest: **8.62 s wall**; `files_skipped=339`, `chunks_written=0`,
   283	  `chunks_embedded=0`.
   284	- Local-only execution: cached CodeRankEmbed and `mixedbread-ai/mxbai-rerank-xsmall-v1`, CPU.
   285	  MPS could not be used in the managed runtime, so `XYZ_DEVICE=cpu` was pinned explicitly.
   286	
   287	### Retrieval quality at depth 100
   288	
   289	| mode | MRR@100 | R@1 | R@3 | R@5 | R@10 | miss@100 |
   290	|---|---:|---:|---:|---:|---:|---:|
   291	| dense | **0.9444** | **0.9000** | **1.0000** | **1.0000** | **1.0000** | 0 |
   292	| BM25 | 0.8583 | 0.7667 | 0.9333 | 0.9667 | 0.9667 | 0 |
   293	| hybrid | 0.9222 | 0.8667 | 0.9667 | 0.9667 | **1.0000** | 0 |
   294	| hybrid+rerank | 0.9016 | 0.8667 | 0.9667 | 0.9667 | 0.9667 | 0 |
   295	
   296	The reranked arm passes the Act 1 noise-floor criterion: its MRR is 0.0428 below dense and its
   297	R@1 is 0.0333 below dense, both within 0.05. This saturated 30-query set does **not** establish
   298	that reranking improves relevance: it reordered all 30 top-10 chunk-id sequences but scored below
   299	dense and hybrid. The CPU reranker cost is also material and belongs in later serving work.
   300	
   301	### Latency (milliseconds, p50 / p95)
   302	
   303	| mode | embed query | BM25 | dense | fuse | rerank | total |
   304	|---|---:|---:|---:|---:|---:|---:|
   305	| dense | 81.28 / 119.48 | 0 / 0 | 3.12 / 4.65 | 0 / 0 | 0 / 0 | 86.42 / 125.35 |
   306	| BM25 | 0 / 0 | 0.85 / 2.03 | 0 / 0 | 0 / 0 | 0 / 0 | 1.34 / 2.68 |
   307	| hybrid | 73.68 / 91.92 | 0.73 / 1.89 | 3.10 / 3.82 | 0.12 / 0.16 | 0 / 0 | 78.70 / 96.23 |
   308	| hybrid+rerank | 142.91 / 313.98 | 1.27 / 3.33 | 3.93 / 6.40 | 0.13 / 0.32 | 50,003.77 / 93,867.16 | 50,175.41 / 94,262.74 |
   309	
   310	Four Phase 1 QA-gate bullets:
   311	
   312	- **MET — real ingest + query round-trip:** labelled subset indexed 339 files / 3,020 chunks and
   313	  all four modes scored 30 queries at depth 100 with zero misses.
   314	- **MET — unchanged re-ingest near-instant:** 8.62 s, `chunks_embedded=0` (<30 s).
   315	- **MET — reranker measurably reorders RRF:** **30/30** queries had a different top-10 chunk-id
   316	  sequence under `hybrid+rerank` than under `hybrid`.
   317	- **MET — latency instrumented:** p50/p95 recorded above for every stage in every mode.

mcp: codebase-memory-mcp/index_status started
mcp: codebase-memory-mcp/index_status (completed)
mcp: codebase-memory-mcp/search_graph started
mcp: codebase-memory-mcp/search_graph (completed)
mcp: codebase-memory-mcp/search_graph started
mcp: codebase-memory-mcp/search_graph (completed)
mcp: codebase-memory-mcp/search_graph started
mcp: codebase-memory-mcp/search_graph (completed)
mcp: codebase-memory-mcp/search_graph started
mcp: codebase-memory-mcp/search_graph (completed)
mcp: codebase-memory-mcp/trace_path started
mcp: codebase-memory-mcp/trace_path (failed)
MCP tool call requires approval, but approval policy is never
mcp: codebase-memory-mcp/trace_path started
mcp: codebase-memory-mcp/trace_path (failed)
MCP tool call requires approval, but approval policy is never
mcp: codebase-memory-mcp/trace_path started
mcp: codebase-memory-mcp/trace_path (failed)
MCP tool call requires approval, but approval policy is never
mcp: codebase-memory-mcp/trace_path started
mcp: codebase-memory-mcp/trace_path (failed)
MCP tool call requires approval, but approval policy is never
exec
/bin/zsh -lc 'for f in xyz/index/store.py xyz/index/embed.py xyz/ingest/walk.py xyz/ingest/chunk.py xyz/retrieve/dense.py xyz/retrieve/lexical.py xyz/retrieve/fuse.py xyz/retrieve/pipeline.py xyz/retrieve/rerank.py xyz/retrieve/latency.py xyz/retrieve/models.py xyz/eval/metrics.py xyz/cli.py xyz/__init__.py xyz/__main__.py; do echo "FILE $f"; nl -ba "$f"; done' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 7484ms:
FILE xyz/index/store.py
     1	"""SQLite-backed chunk, lexical, vector, and embedding-cache store."""
     2	
     3	from __future__ import annotations
     4	
     5	import hashlib
     6	import os
     7	import sqlite3
     8	import time
     9	from collections.abc import Callable, Sequence
    10	from dataclasses import dataclass
    11	from pathlib import Path
    12	from typing import Any
    13	
    14	import numpy as np
    15	import sqlite_vec
    16	
    17	from xyz.index.embed import Embedder
    18	from xyz.ingest import Chunk, ChunkResult, chunk_file, chunk_repo, walk_repo
    19	
    20	
    21	SCHEMA_VERSION = "1"
    22	
    23	
    24	class StoreError(RuntimeError):
    25	    """Base class for index-store failures."""
    26	
    27	
    28	class IndexMismatch(StoreError):
    29	    """The requested embedder does not match the index metadata."""
    30	
    31	
    32	class EmptyCorpus(StoreError):
    33	    """A traversal completed successfully but found no indexable files."""
    34	
    35	
    36	class WalkIncomplete(StoreError):
    37	    """A traversal could not prove a complete view of its requested scope."""
    38	
    39	    def __init__(self, errors: Sequence[str]) -> None:
    40	        self.errors = tuple(errors)
    41	        super().__init__("repository walk incomplete: " + "; ".join(self.errors))
    42	
    43	
    44	@dataclass(frozen=True)
    45	class IngestReport:
    46	    files_seen: int
    47	    files_skipped: int
    48	    files_reingested: int
    49	    files_pruned: int
    50	    chunks_written: int
    51	    chunks_embedded: int
    52	    cache_hits: int
    53	    warnings: tuple[str, ...]
    54	    seconds: float
    55	
    56	
    57	@dataclass(frozen=True)
    58	class StoreStats:
    59	    chunks: int
    60	    chunks_fts: int
    61	    chunks_vec: int
    62	    embed_cache: int
    63	    files: int
    64	
    65	    def __getitem__(self, key: str) -> int:
    66	        return getattr(self, key)
    67	
    68	
    69	def _normalise_prefixes(prefixes: Sequence[str] | None) -> tuple[str, ...] | None:
    70	    if prefixes is None:
    71	        return None
    72	    result: set[str] = set()
    73	    for prefix in prefixes:
    74	        value = prefix.replace(os.sep, "/")
    75	        if value.startswith("./"):
    76	            value = value[2:]
    77	        value = value.lstrip("/")
    78	        if value and not value.endswith("/"):
    79	            value += "/"
    80	        result.add(value)
    81	    return tuple(sorted(result))
    82	
    83	
    84	def _in_scope(path: str, prefixes: tuple[str, ...] | None) -> bool:
    85	    return prefixes is None or any(path.startswith(prefix) for prefix in prefixes)
    86	
    87	
    88	class Store:
    89	    """The sole writer for an XYZ index."""
    90	
    91	    def __init__(self, connection: sqlite3.Connection, embedder: Embedder) -> None:
    92	        self.connection = connection
    93	        self.embedder = embedder
    94	
    95	    @classmethod
    96	    def open(cls, db_path: str | os.PathLike[str], embedder: Embedder) -> Store:
    97	        path = Path(db_path)
    98	        path.parent.mkdir(parents=True, exist_ok=True)
    99	        connection = sqlite3.connect(path)
   100	        store = cls(connection, embedder)
   101	        try:
   102	            has_meta = connection.execute(
   103	                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'meta'"
   104	            ).fetchone()
   105	            if has_meta:
   106	                store.check_embedder(embedder)
   107	            connection.execute("PRAGMA foreign_keys=ON")
   108	            connection.execute("PRAGMA journal_mode=WAL")
   109	            connection.enable_load_extension(True)
   110	            sqlite_vec.load(connection)
   111	            connection.enable_load_extension(False)
   112	            store._initialise_schema()
   113	            store.check_embedder(embedder)
   114	        except Exception:
   115	            connection.close()
   116	            raise
   117	        return store
   118	
   119	    def _initialise_schema(self) -> None:
   120	        dim = int(self.embedder.dim)
   121	        if dim <= 0:
   122	            raise ValueError(f"embedder dim must be positive, got {dim}")
   123	        with self.connection:
   124	            self.connection.executescript(
   125	                f"""
   126	                CREATE TABLE IF NOT EXISTS meta(
   127	                    key TEXT PRIMARY KEY,
   128	                    value TEXT NOT NULL
   129	                );
   130	                CREATE TABLE IF NOT EXISTS files(
   131	                    repo TEXT NOT NULL,
   132	                    path TEXT NOT NULL,
   133	                    file_sha TEXT NOT NULL,
   134	                    chunk_count INTEGER NOT NULL,
   135	                    ingested_at TEXT NOT NULL,
   136	                    PRIMARY KEY(repo, path)
   137	                );
   138	                CREATE TABLE IF NOT EXISTS chunks(
   139	                    id INTEGER PRIMARY KEY,
   140	                    repo TEXT NOT NULL,
   141	                    path TEXT NOT NULL,
   142	                    kind TEXT NOT NULL,
   143	                    qualified_name TEXT NOT NULL,
   144	                    start_line INTEGER NOT NULL,
   145	                    end_line INTEGER NOT NULL,
   146	                    content_sha TEXT NOT NULL,
   147	                    text TEXT NOT NULL,
   148	                    embedded_text TEXT NOT NULL
   149	                );
   150	                CREATE INDEX IF NOT EXISTS chunks_repo_path ON chunks(repo, path);
   151	                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
   152	                    embedded_text,
   153	                    qualified_name,
   154	                    path,
   155	                    content='chunks',
   156	                    content_rowid='id'
   157	                );
   158	                CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
   159	                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
   160	                    VALUES (new.id, new.embedded_text, new.qualified_name, new.path);
   161	                END;
   162	                CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
   163	                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
   164	                    VALUES ('delete', old.id, old.embedded_text, old.qualified_name, old.path);
   165	                END;
   166	                CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
   167	                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
   168	                    VALUES ('delete', old.id, old.embedded_text, old.qualified_name, old.path);
   169	                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
   170	                    VALUES (new.id, new.embedded_text, new.qualified_name, new.path);
   171	                END;
   172	                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
   173	                    embedding float[{dim}]
   174	                );
   175	                CREATE TABLE IF NOT EXISTS embed_cache(
   176	                    content_sha TEXT NOT NULL,
   177	                    model TEXT NOT NULL,
   178	                    dim INTEGER NOT NULL,
   179	                    provider TEXT NOT NULL,
   180	                    vector BLOB NOT NULL,
   181	                    PRIMARY KEY(content_sha, model, dim, provider)
   182	                );
   183	                """
   184	            )
   185	            current = dict(self.connection.execute("SELECT key, value FROM meta"))
   186	            if not current:
   187	                self.connection.executemany(
   188	                    "INSERT INTO meta(key, value) VALUES (?, ?)",
   189	                    (
   190	                        ("model", self.embedder.model_id),
   191	                        ("dim", str(dim)),
   192	                        ("provider", self.embedder.provider),
   193	                        ("schema_version", SCHEMA_VERSION),
   194	                    ),
   195	                )
   196	
   197	    def check_embedder(self, embedder: Embedder) -> None:
   198	        actual = dict(self.connection.execute("SELECT key, value FROM meta"))
   199	        expected = {
   200	            "model": str(embedder.model_id),
   201	            "dim": str(embedder.dim),
   202	            "provider": str(embedder.provider),
   203	        }
   204	        for field in ("model", "dim", "provider"):
   205	            if actual.get(field) != expected[field]:
   206	                raise IndexMismatch(
   207	                    f"index {field} mismatch: stored={actual.get(field)!r}, requested={expected[field]!r}"
   208	                )
   209	
   210	    def close(self) -> None:
   211	        self.connection.close()
   212	
   213	    def __enter__(self) -> Store:
   214	        return self
   215	
   216	    def __exit__(self, *_args: object) -> None:
   217	        self.close()
   218	
   219	    def _snapshot_chunks(
   220	        self,
   221	        repo: str,
   222	        root: Path,
   223	        walked: Sequence[tuple[str, bytes]],
   224	        chunker: Callable[..., ChunkResult],
   225	        include_prefixes: Sequence[str] | None,
   226	    ) -> tuple[dict[str, list[Chunk]], list[str]]:
   227	        if chunker is chunk_repo:
   228	            by_path: dict[str, list[Chunk]] = {}
   229	            warnings: list[str] = []
   230	            for path, source in walked:
   231	                result = chunk_file(repo, path, source)
   232	                by_path[path] = result.chunks
   233	                warnings.extend(result.warnings)
   234	            return by_path, warnings
   235	
   236	        result = chunker(repo, root, include_prefixes=include_prefixes)
   237	        walk_errors = [
   238	            warning.removeprefix("walk error: ")
   239	            for warning in result.warnings
   240	            if warning.startswith("walk error: ")
   241	        ]
   242	        if walk_errors:
   243	            raise WalkIncomplete(walk_errors)
   244	        by_path = {path: [] for path, _source in walked}
   245	        for chunk in result.chunks:
   246	            by_path.setdefault(chunk.path, []).append(chunk)
   247	        return by_path, list(result.warnings)
   248	
   249	    def ingest(
   250	        self,
   251	        repo: str,
   252	        root: str | os.PathLike[str],
   253	        chunker: Callable[..., ChunkResult] = chunk_repo,
   254	        include_prefixes: Sequence[str] | None = None,
   255	        progress: Callable[[int, int, float], None] | None = None,
   256	    ) -> IngestReport:
   257	        started = time.monotonic()
   258	        self.check_embedder(self.embedder)
   259	        root_path = Path(root)
   260	        errors: list[str] = []
   261	        walked = list(walk_repo(root_path, include_prefixes=include_prefixes, errors=errors))
   262	        if errors:
   263	            raise WalkIncomplete(errors)
   264	        if not walked:
   265	            raise EmptyCorpus(f"repository walk found no indexable files under {root_path}")
   266	
   267	        chunks_by_path, warnings = self._snapshot_chunks(
   268	            repo, root_path, walked, chunker, include_prefixes
   269	        )
   270	        file_shas = {path: hashlib.sha256(source).hexdigest() for path, source in walked}
   271	        existing = {
   272	            path: file_sha
   273	            for path, file_sha in self.connection.execute(
   274	                "SELECT path, file_sha FROM files WHERE repo = ?", (repo,)
   275	            )
   276	        }
   277	        candidate_chunks = sum(
   278	            len(chunks_by_path.get(path, ()))
   279	            for path, _source in walked
   280	            if existing.get(path) != file_shas[path]
   281	        )
   282	
   283	        files_skipped = 0
   284	        files_reingested = 0
   285	        chunks_written = 0
   286	        chunks_embedded = 0
   287	        cache_hits = 0
   288	
   289	        for path, _source in walked:
   290	            if existing.get(path) == file_shas[path]:
   291	                files_skipped += 1
   292	                continue
   293	
   294	            chunks = chunks_by_path.get(path, [])
   295	            vectors: dict[str, bytes] = {}
   296	            missing_by_sha: dict[str, Chunk] = {}
   297	            for chunk in chunks:
   298	                row = self.connection.execute(
   299	                    """
   300	                    SELECT vector FROM embed_cache
   301	                    WHERE content_sha = ? AND model = ? AND dim = ? AND provider = ?
   302	                    """,
   303	                    (
   304	                        chunk.content_sha,
   305	                        self.embedder.model_id,
   306	                        self.embedder.dim,
   307	                        self.embedder.provider,
   308	                    ),
   309	                ).fetchone()
   310	                if row is None:
   311	                    missing_by_sha.setdefault(chunk.content_sha, chunk)
   312	                else:
   313	                    vectors[chunk.content_sha] = row[0]
   314	                    cache_hits += 1
   315	
   316	            missing = list(missing_by_sha.values())
   317	
   318	            if missing:
   319	                encoded = np.asarray(
   320	                    self.embedder.encode_documents([chunk.embedded_text for chunk in missing]),
   321	                    dtype=np.float32,
   322	                )
   323	                if encoded.shape != (len(missing), self.embedder.dim):
   324	                    raise ValueError(
   325	                        f"embedder returned shape {encoded.shape}; "
   326	                        f"expected {(len(missing), self.embedder.dim)}"
   327	                    )
   328	                for chunk, vector in zip(missing, encoded, strict=True):
   329	                    vectors[chunk.content_sha] = sqlite_vec.serialize_float32(vector.tolist())
   330	
   331	            with self.connection:
   332	                old_ids = [
   333	                    row[0]
   334	                    for row in self.connection.execute(
   335	                        "SELECT id FROM chunks WHERE repo = ? AND path = ?", (repo, path)
   336	                    )
   337	                ]
   338	                self.connection.executemany(
   339	                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in old_ids)
   340	                )
   341	                self.connection.execute(
   342	                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
   343	                )
   344	                for chunk in missing:
   345	                    self.connection.execute(
   346	                        """
   347	                        INSERT OR IGNORE INTO embed_cache
   348	                            (content_sha, model, dim, provider, vector)
   349	                        VALUES (?, ?, ?, ?, ?)
   350	                        """,
   351	                        (
   352	                            chunk.content_sha,
   353	                            self.embedder.model_id,
   354	                            self.embedder.dim,
   355	                            self.embedder.provider,
   356	                            vectors[chunk.content_sha],
   357	                        ),
   358	                    )
   359	                for chunk in chunks:
   360	                    cursor = self.connection.execute(
   361	                        """
   362	                        INSERT INTO chunks(
   363	                            repo, path, kind, qualified_name, start_line, end_line,
   364	                            content_sha, text, embedded_text
   365	                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
   366	                        """,
   367	                        (
   368	                            chunk.repo,
   369	                            chunk.path,
   370	                            chunk.kind,
   371	                            chunk.qualified_name,
   372	                            chunk.start_line,
   373	                            chunk.end_line,
   374	                            chunk.content_sha,
   375	                            chunk.text,
   376	                            chunk.embedded_text,
   377	                        ),
   378	                    )
   379	                    self.connection.execute(
   380	                        "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)",
   381	                        (cursor.lastrowid, vectors[chunk.content_sha]),
   382	                    )
   383	                self.connection.execute(
   384	                    """
   385	                    INSERT INTO files(repo, path, file_sha, chunk_count, ingested_at)
   386	                    VALUES (?, ?, ?, ?, datetime('now'))
   387	                    ON CONFLICT(repo, path) DO UPDATE SET
   388	                        file_sha=excluded.file_sha,
   389	                        chunk_count=excluded.chunk_count,
   390	                        ingested_at=excluded.ingested_at
   391	                    """,
   392	                    (repo, path, file_shas[path], len(chunks)),
   393	                )
   394	            files_reingested += 1
   395	            chunks_written += len(chunks)
   396	            chunks_embedded += len(missing)
   397	            if progress is not None and missing:
   398	                progress(chunks_embedded, candidate_chunks, time.monotonic() - started)
   399	
   400	        walked_paths = set(file_shas)
   401	        prefixes = _normalise_prefixes(include_prefixes)
   402	        pruned = [
   403	            path
   404	            for path in existing
   405	            if path not in walked_paths and _in_scope(path, prefixes)
   406	        ]
   407	        for path in pruned:
   408	            with self.connection:
   409	                ids = [
   410	                    row[0]
   411	                    for row in self.connection.execute(
   412	                        "SELECT id FROM chunks WHERE repo = ? AND path = ?", (repo, path)
   413	                    )
   414	                ]
   415	                self.connection.executemany(
   416	                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in ids)
   417	                )
   418	                self.connection.execute(
   419	                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
   420	                )
   421	                self.connection.execute(
   422	                    "DELETE FROM files WHERE repo = ? AND path = ?", (repo, path)
   423	                )
   424	
   425	        return IngestReport(
   426	            files_seen=len(walked),
   427	            files_skipped=files_skipped,
   428	            files_reingested=files_reingested,
   429	            files_pruned=len(pruned),
   430	            chunks_written=chunks_written,
   431	            chunks_embedded=chunks_embedded,
   432	            cache_hits=cache_hits,
   433	            warnings=tuple(warnings),
   434	            seconds=time.monotonic() - started,
   435	        )
   436	
   437	    def stats(self) -> StoreStats:
   438	        def count(table: str) -> int:
   439	            return int(self.connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0])
   440	
   441	        return StoreStats(
   442	            chunks=count("chunks"),
   443	            chunks_fts=count("chunks_fts"),
   444	            chunks_vec=count("chunks_vec"),
   445	            embed_cache=count("embed_cache"),
   446	            files=count("files"),
   447	        )
   448	
   449	    def fts_match(self, token: str, limit: int = 100) -> list[int]:
   450	        return [
   451	            int(row[0])
   452	            for row in self.connection.execute(
   453	                "SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?",
   454	                (token, limit),
   455	            )
   456	        ]
FILE xyz/index/embed.py
     1	"""Embedding contracts and the local CodeRankEmbed provider."""
     2	
     3	from __future__ import annotations
     4	
     5	import os
     6	from collections.abc import Callable, Sequence
     7	from typing import Any, Protocol
     8	
     9	import numpy as np
    10	
    11	
    12	QUERY_PREFIX = "Represent this query for searching relevant code: "
    13	DEFAULT_MODEL_ID = "nomic-ai/CodeRankEmbed"
    14	DEFAULT_DIM = 768
    15	MAX_SEQ_LENGTH = 2048
    16	
    17	
    18	class Embedder(Protocol):
    19	    """Minimal embedding interface shared by indexing and retrieval."""
    20	
    21	    model_id: str
    22	    dim: int
    23	    provider: str
    24	
    25	    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
    26	        """Return one float32 unit vector per document."""
    27	
    28	    def encode_query(self, text: str) -> np.ndarray:
    29	        """Return one float32 unit vector for a natural-language query."""
    30	
    31	
    32	def _positive_env_int(name: str, default: int) -> int:
    33	    raw = os.environ.get(name)
    34	    if raw is None:
    35	        return default
    36	    try:
    37	        value = int(raw)
    38	    except ValueError as exc:
    39	        raise ValueError(f"{name} must be a positive integer, got {raw!r}") from exc
    40	    if value <= 0:
    41	        raise ValueError(f"{name} must be a positive integer, got {raw!r}")
    42	    return value
    43	
    44	
    45	def _unit_float32(vectors: Any, *, rows: int, dim: int) -> np.ndarray:
    46	    array = np.asarray(vectors, dtype=np.float32)
    47	    if rows == 1 and array.shape == (dim,):
    48	        array = array.reshape(1, dim)
    49	    if array.shape != (rows, dim):
    50	        raise ValueError(f"embedder returned shape {array.shape}; expected {(rows, dim)}")
    51	    norms = np.linalg.norm(array, axis=1, keepdims=True)
    52	    if np.any(norms == 0):
    53	        raise ValueError("embedder returned a zero-length vector")
    54	    return np.asarray(array / norms, dtype=np.float32)
    55	
    56	
    57	class CodeRankEmbedder:
    58	    """On-device CodeRankEmbed adapter with the repository memory guards."""
    59	
    60	    provider = "sentence-transformers"
    61	    dim = DEFAULT_DIM
    62	
    63	    def __init__(
    64	        self,
    65	        model_id: str = DEFAULT_MODEL_ID,
    66	        *,
    67	        model_factory: Callable[..., Any] | None = None,
    68	        device: str | None = None,
    69	    ) -> None:
    70	        os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    71	        self.model_id = model_id
    72	        self.batch_size = _positive_env_int("EMBED_BATCH_SIZE", 16)
    73	        max_threads = _positive_env_int("EMBED_MAX_THREADS", max(1, os.cpu_count() or 1))
    74	
    75	        import torch
    76	
    77	        torch.set_num_threads(max_threads)
    78	        if device is None:
    79	            device = "mps" if torch.backends.mps.is_available() else "cpu"
    80	        if model_factory is None:
    81	            from sentence_transformers import SentenceTransformer
    82	
    83	            model_factory = SentenceTransformer
    84	        self.model = model_factory(model_id, trust_remote_code=True, device=device)
    85	        self.model.max_seq_length = MAX_SEQ_LENGTH
    86	
    87	    def _encode(self, texts: Sequence[str]) -> np.ndarray:
    88	        materialised = list(texts)
    89	        if not materialised:
    90	            return np.empty((0, self.dim), dtype=np.float32)
    91	        encoded = self.model.encode(
    92	            materialised,
    93	            batch_size=self.batch_size,
    94	            normalize_embeddings=True,
    95	            convert_to_numpy=True,
    96	            show_progress_bar=False,
    97	        )
    98	        return _unit_float32(encoded, rows=len(materialised), dim=self.dim)
    99	
   100	    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
   101	        return self._encode(texts)
   102	
   103	    def encode_query(self, text: str) -> np.ndarray:
   104	        return self._encode([QUERY_PREFIX + text])[0]
FILE xyz/ingest/walk.py
     1	"""Deterministic, failure-aware repository traversal."""
     2	
     3	from __future__ import annotations
     4	
     5	import fnmatch
     6	import os
     7	from collections.abc import Iterator, Sequence, Set
     8	from pathlib import Path
     9	
    10	
    11	DEFAULT_INCLUDE = frozenset(
    12	    {
    13	        ".py",
    14	        ".js",
    15	        ".ts",
    16	        ".tsx",
    17	        ".jsx",
    18	        ".php",
    19	        ".md",
    20	        ".go",
    21	        ".rb",
    22	        ".sh",
    23	        ".yml",
    24	        ".yaml",
    25	        ".toml",
    26	        ".ini",
    27	        ".cfg",
    28	        ".json",
    29	        ".sql",
    30	        ".html",
    31	        ".twig",
    32	        "Dockerfile",
    33	        "docker-compose*.yml",
    34	        "Makefile",
    35	        "*.blade.php",
    36	        ".env.example",
    37	    }
    38	)
    39	
    40	DEFAULT_EXCLUDE = frozenset(
    41	    {
    42	        ".git",
    43	        ".venv",
    44	        "node_modules",
    45	        "__pycache__",
    46	        "dist",
    47	        "build",
    48	        "temp",
    49	        ".embed-tmp",
    50	        ".xyz",
    51	        ".relay-scratch",
    52	        "marathon-system",
    53	        "relay-system",
    54	    }
    55	)
    56	
    57	MAX_FILE_BYTES = 1024 * 1024
    58	BINARY_SNIFF_BYTES = 8192
    59	
    60	
    61	def _included(name: str, include: Set[str] | Sequence[str]) -> bool:
    62	    suffix = Path(name).suffix.lower()
    63	    for rule in include:
    64	        if rule.startswith(".") and "*" not in rule:
    65	            if rule == suffix or rule == name:
    66	                return True
    67	        elif fnmatch.fnmatchcase(name, rule):
    68	            return True
    69	    return False
    70	
    71	
    72	def _normalise_prefixes(prefixes: Sequence[str] | None) -> tuple[str, ...] | None:
    73	    if prefixes is None:
    74	        return None
    75	    normalised: list[str] = []
    76	    for prefix in prefixes:
    77	        value = prefix.replace(os.sep, "/")
    78	        if value.startswith("./"):
    79	            value = value[2:]
    80	        value = value.lstrip("/")
    81	        if value and not value.endswith("/"):
    82	            value += "/"
    83	        normalised.append(value)
    84	    return tuple(sorted(set(normalised)))
    85	
    86	
    87	def _directory_may_match(rel_dir: str, prefixes: tuple[str, ...] | None) -> bool:
    88	    if prefixes is None:
    89	        return True
    90	    directory = f"{rel_dir}/" if rel_dir else ""
    91	    return any(prefix.startswith(directory) or directory.startswith(prefix) for prefix in prefixes)
    92	
    93	
    94	def _file_matches(rel_path: str, prefixes: tuple[str, ...] | None) -> bool:
    95	    return prefixes is None or any(rel_path.startswith(prefix) for prefix in prefixes)
    96	
    97	
    98	def walk_repo(
    99	    root: str | os.PathLike[str],
   100	    include_ext: Set[str] | Sequence[str] = DEFAULT_INCLUDE,
   101	    exclude_dirs: Set[str] | Sequence[str] = DEFAULT_EXCLUDE,
   102	    include_prefixes: Sequence[str] | None = None,
   103	    *,
   104	    errors: list[str],
   105	) -> Iterator[tuple[str, bytes]]:
   106	    """Yield included ``(relative_path, content)`` pairs in sorted order.
   107	
   108	    Enumeration, stat, and read failures for relevant candidate paths are
   109	    recorded in ``errors``. Intentional filters are silent.
   110	    """
   111	
   112	    root_path = Path(root)
   113	    if not root_path.is_dir():
   114	        raise ValueError(f"repository root is not an existing directory: {root_path}")
   115	
   116	    excluded = set(exclude_dirs)
   117	    prefixes = _normalise_prefixes(include_prefixes)
   118	
   119	    def visit(directory: Path, rel_dir: str) -> Iterator[tuple[str, bytes]]:
   120	        try:
   121	            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
   122	        except OSError as exc:
   123	            label = rel_dir or "."
   124	            errors.append(f"{label}: {type(exc).__name__}: {exc}")
   125	            return
   126	
   127	        for entry in entries:
   128	            rel_path = f"{rel_dir}/{entry.name}" if rel_dir else entry.name
   129	            rel_path = rel_path.replace(os.sep, "/")
   130	            try:
   131	                is_dir = entry.is_dir(follow_symlinks=False)
   132	                is_file = entry.is_file(follow_symlinks=False)
   133	            except OSError as exc:
   134	                errors.append(f"{rel_path}: {type(exc).__name__}: {exc}")
   135	                continue
   136	
   137	            if is_dir:
   138	                if entry.name in excluded or not _directory_may_match(rel_path, prefixes):
   139	                    continue
   140	                yield from visit(Path(entry.path), rel_path)
   141	                continue
   142	
   143	            if not is_file or not _file_matches(rel_path, prefixes):
   144	                continue
   145	            if not _included(entry.name, include_ext):
   146	                continue
   147	
   148	            try:
   149	                if entry.stat(follow_symlinks=False).st_size > MAX_FILE_BYTES:
   150	                    continue
   151	                with open(entry.path, "rb") as handle:
   152	                    head = handle.read(BINARY_SNIFF_BYTES)
   153	                    if b"\0" in head:
   154	                        continue
   155	                    content = head + handle.read()
   156	            except OSError as exc:
   157	                errors.append(f"{rel_path}: {type(exc).__name__}: {exc}")
   158	                continue
   159	            yield rel_path, content
   160	
   161	    yield from visit(root_path, "")
FILE xyz/ingest/chunk.py
     1	"""Language-aware source chunking with deterministic hard bounds."""
     2	
     3	from __future__ import annotations
     4	
     5	import hashlib
     6	import re
     7	from dataclasses import dataclass
     8	from pathlib import PurePosixPath
     9	
    10	from tree_sitter import Node
    11	from tree_sitter_language_pack import get_parser
    12	
    13	
    14	MAX_CHARS = 6000
    15	SPLIT_SEARCH_CHARS = 1500
    16	SPLIT_OVERLAP_CHARS = 150
    17	
    18	
    19	@dataclass(frozen=True)
    20	class Chunk:
    21	    repo: str
    22	    path: str
    23	    kind: str
    24	    qualified_name: str
    25	    start_line: int
    26	    end_line: int
    27	    text: str
    28	    embedded_text: str
    29	    content_sha: str
    30	
    31	
    32	@dataclass(frozen=True)
    33	class ChunkResult:
    34	    chunks: list[Chunk]
    35	    warnings: list[str]
    36	
    37	
    38	@dataclass(frozen=True)
    39	class _Draft:
    40	    kind: str
    41	    qualified_name: str
    42	    text: str
    43	    line_map: tuple[int, ...]
    44	
    45	
    46	_LANGUAGES = {
    47	    ".py": "python",
    48	    ".js": "javascript",
    49	    ".jsx": "javascript",
    50	    ".ts": "typescript",
    51	    ".tsx": "tsx",
    52	    ".php": "php",
    53	}
    54	
    55	_TOP_LEVEL_TYPES = {
    56	    "python": {"function_definition": "function", "class_definition": "class"},
    57	    "javascript": {"function_declaration": "function", "class_declaration": "class"},
    58	    "typescript": {"function_declaration": "function", "class_declaration": "class"},
    59	    "tsx": {"function_declaration": "function", "class_declaration": "class"},
    60	    "php": {"function_definition": "function", "class_declaration": "class"},
    61	}
    62	
    63	
    64	def _line_map(text: str, start_line: int) -> tuple[int, ...]:
    65	    line = start_line
    66	    result: list[int] = []
    67	    for char in text:
    68	        result.append(line)
    69	        if char == "\n":
    70	            line += 1
    71	    return tuple(result)
    72	
    73	
    74	def _line_at(source: bytes, byte_offset: int) -> int:
    75	    """Return a one-based line without trusting parser point metadata."""
    76	    return source[:byte_offset].count(b"\n") + 1
    77	
    78	
    79	def _draft(kind: str, qualified_name: str, text: str, start_line: int) -> _Draft:
    80	    return _Draft(kind, qualified_name, text, _line_map(text, start_line))
    81	
    82	
    83	def _trim(text: str, line_map: tuple[int, ...]) -> tuple[str, tuple[int, ...]]:
    84	    left = len(text) - len(text.lstrip())
    85	    right = len(text.rstrip())
    86	    return text[left:right], line_map[left:right]
    87	
    88	
    89	def _node_name(node: Node) -> str | None:
    90	    name = node.child_by_field_name("name")
    91	    if name is None:
    92	        return None
    93	    return name.text.decode("utf-8", errors="replace")
    94	
    95	
    96	def _unwrap_definition(node: Node, language: str) -> Node | None:
    97	    wanted = _TOP_LEVEL_TYPES[language]
    98	    if node.type in wanted:
    99	        return node
   100	    if node.type in {"decorated_definition", "export_statement"}:
   101	        return next((child for child in node.named_children if child.type in wanted), None)
   102	    return None
   103	
   104	
   105	def _method_nodes(class_node: Node, language: str) -> list[Node]:
   106	    if language == "python":
   107	        body = class_node.child_by_field_name("body")
   108	        method_type = "function_definition"
   109	        wrappers = {"decorated_definition"}
   110	    elif language == "php":
   111	        body = class_node.child_by_field_name("body")
   112	        if body is None:
   113	            body = next((child for child in class_node.named_children if child.type == "declaration_list"), None)
   114	        method_type = "method_declaration"
   115	        wrappers = set()
   116	    else:
   117	        body = class_node.child_by_field_name("body")
   118	        method_type = "method_definition"
   119	        wrappers = set()
   120	    if body is None:
   121	        return []
   122	
   123	    methods: list[Node] = []
   124	    for child in body.named_children:
   125	        if child.type == method_type:
   126	            methods.append(child)
   127	        elif child.type in wrappers:
   128	            wrapped = next((item for item in child.named_children if item.type == method_type), None)
   129	            if wrapped is not None:
   130	                methods.append(child)
   131	    return methods
   132	
   133	
   134	def _ast_drafts(rel_path: str, source: bytes, language: str) -> list[_Draft]:
   135	    tree = get_parser(language).parse(source)
   136	    if tree.root_node.has_error:
   137	        raise ValueError("syntax tree contains parse errors")
   138	
   139	    drafts: list[_Draft] = []
   140	    occupied: list[tuple[int, int]] = []
   141	    for outer in tree.root_node.named_children:
   142	        definition = _unwrap_definition(outer, language)
   143	        if definition is None:
   144	            continue
   145	        name = _node_name(definition)
   146	        if not name:
   147	            continue
   148	        kind = _TOP_LEVEL_TYPES[language][definition.type]
   149	        text = source[outer.start_byte : outer.end_byte].decode("utf-8", errors="replace")
   150	        drafts.append(_draft(kind, name, text, _line_at(source, outer.start_byte)))
   151	        occupied.append((outer.start_byte, outer.end_byte))
   152	
   153	        if kind == "class":
   154	            for method in _method_nodes(definition, language):
   155	                method_definition = method
   156	                if method.type == "decorated_definition":
   157	                    method_definition = next(
   158	                        child for child in method.named_children if child.type == "function_definition"
   159	                    )
   160	                method_name = _node_name(method_definition)
   161	                if method_name:
   162	                    method_text = source[method.start_byte : method.end_byte].decode(
   163	                        "utf-8", errors="replace"
   164	                    )
   165	                    drafts.append(
   166	                        _draft(
   167	                            "method",
   168	                            f"{name}.{method_name}",
   169	                            method_text,
   170	                            _line_at(source, method.start_byte),
   171	                        )
   172	                    )
   173	
   174	    residual_parts: list[tuple[str, tuple[int, ...]]] = []
   175	    cursor = 0
   176	    for start, end in sorted(occupied):
   177	        if start > cursor:
   178	            raw = source[cursor:start].decode("utf-8", errors="replace")
   179	            mapped = _line_map(raw, _line_at(source, cursor))
   180	            part = _trim(raw, mapped)
   181	            if part[0]:
   182	                residual_parts.append(part)
   183	        cursor = max(cursor, end)
   184	    if cursor < len(source):
   185	        raw = source[cursor:].decode("utf-8", errors="replace")
   186	        mapped = _line_map(raw, _line_at(source, cursor))
   187	        part = _trim(raw, mapped)
   188	        if part[0]:
   189	            residual_parts.append(part)
   190	
   191	    if residual_parts:
   192	        text_bits: list[str] = []
   193	        map_bits: list[int] = []
   194	        for index, (text, mapped) in enumerate(residual_parts):
   195	            if index:
   196	                marker_line = map_bits[-1] if map_bits else mapped[0]
   197	                marker = "\n# …\n"
   198	                text_bits.append(marker)
   199	                map_bits.extend([marker_line] * len(marker))
   200	            text_bits.append(text)
   201	            map_bits.extend(mapped)
   202	        drafts.append(_Draft("module", rel_path, "".join(text_bits), tuple(map_bits)))
   203	
   204	    drafts.sort(key=lambda item: (item.line_map[0], {"module": 0, "class": 1, "function": 1, "method": 2}.get(item.kind, 3), item.qualified_name))
   205	    return drafts
   206	
   207	
   208	_HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$")
   209	
   210	
   211	def _markdown_drafts(rel_path: str, text: str) -> list[_Draft]:
   212	    lines = text.splitlines(keepends=True)
   213	    headings: list[tuple[int, int, str]] = []
   214	    for index, line in enumerate(lines):
   215	        match = _HEADING.match(line.rstrip("\r\n"))
   216	        if match:
   217	            headings.append((index, len(match.group(1)), match.group(2).strip()))
   218	
   219	    boundaries = [item[0] for item in headings]
   220	    drafts: list[_Draft] = []
   221	    if not headings:
   222	        body = text.rstrip()
   223	        return [_draft("file", rel_path, body, 1)] if body else []
   224	
   225	    first_heading = headings[0][0]
   226	    if first_heading:
   227	        preamble = "".join(lines[:first_heading]).rstrip()
   228	        if preamble:
   229	            drafts.append(_draft("preamble", rel_path, preamble, 1))
   230	
   231	    path: list[str] = []
   232	    for position, (start, level, title) in enumerate(headings):
   233	        path = path[: level - 1]
   234	        path.append(title)
   235	        end = boundaries[position + 1] if position + 1 < len(boundaries) else len(lines)
   236	        body = "".join(lines[start:end]).rstrip()
   237	        if body:
   238	            drafts.append(_draft("section", " > ".join(path), body, start + 1))
   239	    return drafts
   240	
   241	
   242	def _file_drafts(rel_path: str, text: str) -> list[_Draft]:
   243	    body = text.rstrip()
   244	    return [_draft("file", rel_path, body, 1)] if body else []
   245	
   246	
   247	def _split_draft(draft: _Draft) -> list[_Draft]:
   248	    if len(draft.text) <= MAX_CHARS:
   249	        return [draft]
   250	
   251	    result: list[_Draft] = []
   252	    start = 0
   253	    part_number = 1
   254	    while len(draft.text) - start > MAX_CHARS:
   255	        limit = start + MAX_CHARS
   256	        blank = draft.text.rfind("\n\n", limit - SPLIT_SEARCH_CHARS, limit)
   257	        cut = blank + 2 if blank >= start else limit
   258	        name = draft.qualified_name if part_number == 1 else f"{draft.qualified_name}#{part_number}"
   259	        result.append(_Draft(draft.kind, name, draft.text[start:cut], draft.line_map[start:cut]))
   260	        next_start = max(cut - SPLIT_OVERLAP_CHARS, start + 1)
   261	        start = next_start
   262	        part_number += 1
   263	    name = draft.qualified_name if part_number == 1 else f"{draft.qualified_name}#{part_number}"
   264	    result.append(_Draft(draft.kind, name, draft.text[start:], draft.line_map[start:]))
   265	    return result
   266	
   267	
   268	def _materialise(repo: str, rel_path: str, draft: _Draft) -> Chunk:
   269	    embedded_text = f"{rel_path}\n\n{draft.text}"
   270	    non_newline = [line for char, line in zip(draft.text, draft.line_map) if char not in "\r\n"]
   271	    start_line = non_newline[0] if non_newline else draft.line_map[0]
   272	    end_line = non_newline[-1] if non_newline else draft.line_map[-1]
   273	    return Chunk(
   274	        repo=repo,
   275	        path=rel_path,
   276	        kind=draft.kind,
   277	        qualified_name=draft.qualified_name,
   278	        start_line=start_line,
   279	        end_line=end_line,
   280	        text=draft.text,
   281	        embedded_text=embedded_text,
   282	        content_sha=hashlib.sha256(embedded_text.encode("utf-8")).hexdigest(),
   283	    )
   284	
   285	
   286	def chunk_file(repo: str, rel_path: str, source: bytes) -> ChunkResult:
   287	    """Chunk one source file, falling back to file chunks after parse errors."""
   288	
   289	    rel_path = rel_path.replace("\\", "/")
   290	    suffix = PurePosixPath(rel_path).suffix.lower()
   291	    text = source.decode("utf-8", errors="replace")
   292	    warnings: list[str] = []
   293	
   294	    if suffix in _LANGUAGES:
   295	        try:
   296	            drafts = _ast_drafts(rel_path, source, _LANGUAGES[suffix])
   297	        except Exception as exc:
   298	            warnings.append(f"{rel_path}: parse failed; used file chunker ({type(exc).__name__}: {exc})")
   299	            drafts = _file_drafts(rel_path, text)
   300	    elif suffix in {".md", ".markdown"}:
   301	        drafts = _markdown_drafts(rel_path, text)
   302	    else:
   303	        drafts = _file_drafts(rel_path, text)
   304	
   305	    chunks = [
   306	        _materialise(repo, rel_path, part)
   307	        for draft in drafts
   308	        for part in _split_draft(draft)
   309	        if part.text
   310	    ]
   311	    return ChunkResult(chunks, warnings)
FILE xyz/retrieve/dense.py
     1	"""sqlite-vec nearest-neighbour retrieval."""
     2	
     3	from __future__ import annotations
     4	
     5	from collections.abc import Sequence
     6	
     7	import numpy as np
     8	import sqlite_vec
     9	
    10	from xyz.index.store import Store
    11	from xyz.retrieve.models import Hit
    12	
    13	
    14	KNN_SQL = """
    15	SELECT rowid, distance
    16	FROM chunks_vec
    17	WHERE embedding MATCH ? AND k = ?
    18	ORDER BY distance ASC
    19	"""
    20	
    21	
    22	def dense_search(store: Store, query_vec: Sequence[float] | np.ndarray, k: int) -> list[Hit]:
    23	    """Return the nearest vectors with negated distances as scores."""
    24	
    25	    if k <= 0:
    26	        return []
    27	    vector = np.asarray(query_vec, dtype=np.float32)
    28	    if vector.shape != (store.embedder.dim,):
    29	        raise ValueError(
    30	            f"query vector has shape {vector.shape}; expected {(store.embedder.dim,)}"
    31	        )
    32	    encoded = sqlite_vec.serialize_float32(vector.tolist())
    33	    rows = store.connection.execute(KNN_SQL, (encoded, k))
    34	    return [Hit(int(chunk_id), -float(distance), "dense") for chunk_id, distance in rows]
FILE xyz/retrieve/lexical.py
     1	"""FTS5/BM25 retrieval with safe query construction."""
     2	
     3	from __future__ import annotations
     4	
     5	import re
     6	
     7	from xyz.index.store import Store
     8	from xyz.retrieve.models import Hit
     9	
    10	
    11	_TOKEN = re.compile(r"[^\W_]+(?:_[^\W_]+)*", re.UNICODE)
    12	_STOPWORDS = frozenset(
    13	    {
    14	        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    15	        "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "with",
    16	    }
    17	)
    18	
    19	
    20	def sanitise_fts_query(query: str) -> str | None:
    21	    """Turn user text into an operator-free OR query, or ``None`` if empty."""
    22	
    23	    tokens: list[str] = []
    24	    seen: set[str] = set()
    25	    for match in _TOKEN.finditer(query):
    26	        token = match.group(0)
    27	        folded = token.casefold()
    28	        if folded in _STOPWORDS or folded in seen:
    29	            continue
    30	        seen.add(folded)
    31	        tokens.append(token.replace('"', '""'))
    32	    if not tokens:
    33	        return None
    34	    return " OR ".join(f'"{token}"' for token in tokens)
    35	
    36	
    37	def bm25_search(store: Store, query: str, k: int) -> list[Hit]:
    38	    """Return the best lexical matches with negated FTS5 BM25 scores."""
    39	
    40	    if k <= 0:
    41	        return []
    42	    safe_query = sanitise_fts_query(query)
    43	    if safe_query is None:
    44	        return []
    45	    rows = store.connection.execute(
    46	        """
    47	        SELECT rowid, bm25(chunks_fts) AS distance
    48	        FROM chunks_fts
    49	        WHERE chunks_fts MATCH ?
    50	        ORDER BY distance ASC, rowid ASC
    51	        LIMIT ?
    52	        """,
    53	        (safe_query, k),
    54	    )
    55	    return [Hit(int(chunk_id), -float(distance), "bm25") for chunk_id, distance in rows]
FILE xyz/retrieve/fuse.py
     1	"""Deterministic reciprocal-rank fusion."""
     2	
     3	from __future__ import annotations
     4	
     5	from collections.abc import Sequence
     6	
     7	from xyz.retrieve.models import Hit
     8	
     9	
    10	def rrf(rankings: Sequence[Sequence[Hit]], k: int = 60) -> list[Hit]:
    11	    """Fuse rankings using one-based ranks and deterministic chunk-id ties."""
    12	
    13	    if k < 0:
    14	        raise ValueError("RRF k must be non-negative")
    15	    scores: dict[int, float] = {}
    16	    for ranking in rankings:
    17	        seen: set[int] = set()
    18	        for rank, hit in enumerate(ranking, start=1):
    19	            if hit.chunk_id in seen:
    20	                continue
    21	            seen.add(hit.chunk_id)
    22	            scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (k + rank)
    23	    hits = [Hit(chunk_id, score, "rrf") for chunk_id, score in scores.items()]
    24	    return sorted(hits, key=lambda hit: (-hit.score, hit.chunk_id))
FILE xyz/retrieve/pipeline.py
     1	"""Instrumented dense, lexical, hybrid, and reranked retrieval pipeline."""
     2	
     3	from __future__ import annotations
     4	
     5	import time
     6	from collections.abc import Sequence
     7	
     8	from xyz.index.embed import Embedder
     9	from xyz.index.store import Store
    10	from xyz.retrieve.dense import dense_search
    11	from xyz.retrieve.fuse import rrf
    12	from xyz.retrieve.lexical import bm25_search
    13	from xyz.retrieve.models import Hit, SearchHit, SearchResult
    14	from xyz.retrieve.rerank import Reranker
    15	
    16	
    17	TIMING_STAGES = ("embed_query", "bm25", "dense", "fuse", "rerank", "total")
    18	MODES = frozenset({"auto", "dense", "bm25", "hybrid", "hybrid+rerank"})
    19	
    20	
    21	class Retriever:
    22	    def __init__(self, store: Store, embedder: Embedder, reranker: Reranker | None = None) -> None:
    23	        store.check_embedder(embedder)
    24	        self.store = store
    25	        self.embedder = embedder
    26	        self.reranker = reranker
    27	
    28	    @staticmethod
    29	    def _elapsed(started: float) -> float:
    30	        return max(0.0, (time.perf_counter() - started) * 1000.0)
    31	
    32	    def _chunk_rows(self, ids: Sequence[int]) -> dict[int, tuple[object, ...]]:
    33	        if not ids:
    34	            return {}
    35	        placeholders = ",".join("?" for _ in ids)
    36	        rows = self.store.connection.execute(
    37	            f"""
    38	            SELECT id, repo, path, kind, qualified_name, start_line, end_line, text, embedded_text
    39	            FROM chunks WHERE id IN ({placeholders})
    40	            """,
    41	            tuple(ids),
    42	        )
    43	        return {int(row[0]): tuple(row[1:]) for row in rows}
    44	
    45	    def search(
    46	        self,
    47	        query: str,
    48	        k: int = 10,
    49	        fetch_k: int = 50,
    50	        mode: str = "auto",
    51	        tau: float | None = None,
    52	    ) -> SearchResult:
    53	        if mode not in MODES:
    54	            raise ValueError(f"unknown retrieval mode: {mode!r}")
    55	        if k <= 0 or fetch_k <= 0:
    56	            raise ValueError("k and fetch_k must be positive")
    57	        resolved = ("hybrid+rerank" if self.reranker is not None else "hybrid") if mode == "auto" else mode
    58	        if resolved == "hybrid+rerank" and self.reranker is None:
    59	            raise ValueError("hybrid+rerank mode requires a reranker")
    60	
    61	        timings = {stage: 0.0 for stage in TIMING_STAGES}
    62	        total_started = time.perf_counter()
    63	        dense_hits: list[Hit] = []
    64	        lexical_hits: list[Hit] = []
    65	
    66	        if resolved in {"dense", "hybrid", "hybrid+rerank"}:
    67	            started = time.perf_counter()
    68	            query_vec = self.embedder.encode_query(query)
    69	            timings["embed_query"] = self._elapsed(started)
    70	            started = time.perf_counter()
    71	            dense_hits = dense_search(self.store, query_vec, fetch_k)
    72	            timings["dense"] = self._elapsed(started)
    73	        if resolved in {"bm25", "hybrid", "hybrid+rerank"}:
    74	            started = time.perf_counter()
    75	            lexical_hits = bm25_search(self.store, query, fetch_k)
    76	            timings["bm25"] = self._elapsed(started)
    77	
    78	        if resolved == "dense":
    79	            candidates = dense_hits[:fetch_k]
    80	        elif resolved == "bm25":
    81	            candidates = lexical_hits[:fetch_k]
    82	        else:
    83	            started = time.perf_counter()
    84	            candidates = rrf([dense_hits, lexical_hits])[:fetch_k]
    85	            timings["fuse"] = self._elapsed(started)
    86	
    87	        if resolved == "hybrid+rerank" and candidates:
    88	            rerank_count = min(len(candidates), 50)
    89	            head = candidates[:rerank_count]
    90	            rows = self._chunk_rows([hit.chunk_id for hit in head])
    91	            texts = [str(rows[hit.chunk_id][7]) for hit in head]
    92	            started = time.perf_counter()
    93	            scores = self.reranker.score(query, texts)  # type: ignore[union-attr]
    94	            timings["rerank"] = self._elapsed(started)
    95	            if len(scores) != len(head):
    96	                raise ValueError(f"reranker returned {len(scores)} scores for {len(head)} candidates")
    97	            rescored = [
    98	                Hit(hit.chunk_id, float(score), "rerank")
    99	                for hit, score in zip(head, scores, strict=True)
   100	            ]
   101	            candidates = sorted(rescored, key=lambda hit: (-hit.score, hit.chunk_id)) + candidates[rerank_count:]
   102	
   103	        rows = self._chunk_rows([hit.chunk_id for hit in candidates])
   104	        ranking = [(hit.chunk_id, str(rows[hit.chunk_id][1])) for hit in candidates]
   105	        top_score = candidates[0].score if candidates else None
   106	        no_answer = top_score is None or (tau is not None and top_score < tau)
   107	        materialised: list[SearchHit] = []
   108	        if not no_answer:
   109	            for hit in candidates[:k]:
   110	                repo, path, kind, name, start_line, end_line, text, embedded_text = rows[hit.chunk_id]
   111	                materialised.append(
   112	                    SearchHit(
   113	                        hit.chunk_id, str(repo), str(path), str(kind), str(name),
   114	                        int(start_line), int(end_line), str(text), str(embedded_text),
   115	                        hit.score, hit.stage,
   116	                    )
   117	                )
   118	        timings["total"] = self._elapsed(total_started)
   119	        return SearchResult(materialised, ranking, no_answer, timings, resolved)
FILE xyz/retrieve/rerank.py
     1	"""Injectable local cross-encoder reranking."""
     2	
     3	from __future__ import annotations
     4	
     5	import math
     6	import os
     7	from collections.abc import Callable, Sequence
     8	from typing import Any, Protocol
     9	
    10	
    11	DEFAULT_RERANKER = "mixedbread-ai/mxbai-rerank-xsmall-v1"
    12	
    13	
    14	class Reranker(Protocol):
    15	    def score(self, query: str, texts: Sequence[str]) -> list[float]:
    16	        """Return one higher-is-better score for each text."""
    17	
    18	
    19	class CrossEncoderReranker:
    20	    """Sentence Transformers CrossEncoder adapter, kept injectable for bake-offs."""
    21	
    22	    def __init__(
    23	        self,
    24	        model_id: str | None = None,
    25	        *,
    26	        model_factory: Callable[..., Any] | None = None,
    27	        device: str | None = None,
    28	    ) -> None:
    29	        self.model_id = model_id or os.environ.get("XYZ_RERANKER", DEFAULT_RERANKER)
    30	        if model_factory is None:
    31	            from sentence_transformers import CrossEncoder
    32	
    33	            model_factory = CrossEncoder
    34	        kwargs: dict[str, object] = {"trust_remote_code": True}
    35	        if device is not None:
    36	            kwargs["device"] = device
    37	        self.model = model_factory(self.model_id, **kwargs)
    38	
    39	    def score(self, query: str, texts: Sequence[str]) -> list[float]:
    40	        materialised = list(texts)
    41	        if not materialised:
    42	            return []
    43	        raw = self.model.predict([(query, text) for text in materialised])
    44	        if hasattr(raw, "tolist"):
    45	            raw = raw.tolist()
    46	        scores = [float(value) for value in raw]
    47	        if len(scores) != len(materialised):
    48	            raise ValueError(
    49	                f"reranker returned {len(scores)} scores for {len(materialised)} texts"
    50	            )
    51	        if not all(math.isfinite(value) for value in scores):
    52	            raise ValueError("reranker returned a non-finite score")
    53	        return scores
FILE xyz/retrieve/latency.py
     1	"""In-memory retrieval latency aggregation."""
     2	
     3	from __future__ import annotations
     4	
     5	from collections.abc import Iterable, Mapping
     6	
     7	
     8	def _percentile(values: list[float], percentile: float) -> float:
     9	    if not values:
    10	        return 0.0
    11	    ordered = sorted(values)
    12	    position = (len(ordered) - 1) * percentile
    13	    lower = int(position)
    14	    upper = min(lower + 1, len(ordered) - 1)
    15	    fraction = position - lower
    16	    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction
    17	
    18	
    19	class LatencyLog:
    20	    """Collect timing dictionaries and report p50/p95 milliseconds per stage."""
    21	
    22	    def __init__(self, timings: Iterable[Mapping[str, float]] = ()) -> None:
    23	        self.timings: list[dict[str, float]] = []
    24	        for sample in timings:
    25	            self.add(sample)
    26	
    27	    def add(self, timings: Mapping[str, float]) -> None:
    28	        self.timings.append({key: float(value) for key, value in timings.items()})
    29	
    30	    append = add
    31	
    32	    def summary(self) -> dict[str, dict[str, float]]:
    33	        stages = sorted({stage for sample in self.timings for stage in sample})
    34	        return {
    35	            stage: {
    36	                "p50": _percentile([sample.get(stage, 0.0) for sample in self.timings], 0.50),
    37	                "p95": _percentile([sample.get(stage, 0.0) for sample in self.timings], 0.95),
    38	            }
    39	            for stage in stages
    40	        }
    41	
    42	    report = summary
FILE xyz/retrieve/models.py
     1	"""Value objects shared by retrieval lanes and the query pipeline."""
     2	
     3	from __future__ import annotations
     4	
     5	from dataclasses import dataclass
     6	
     7	
     8	@dataclass(frozen=True)
     9	class Hit:
    10	    """A scored chunk reference; scores are always higher-is-better."""
    11	
    12	    chunk_id: int
    13	    score: float
    14	    stage: str
    15	
    16	
    17	@dataclass(frozen=True)
    18	class SearchHit:
    19	    """A materialised chunk row returned to a caller."""
    20	
    21	    chunk_id: int
    22	    repo: str
    23	    path: str
    24	    kind: str
    25	    qualified_name: str
    26	    start_line: int
    27	    end_line: int
    28	    text: str
    29	    embedded_text: str
    30	    score: float
    31	    stage: str
    32	
    33	
    34	@dataclass(frozen=True)
    35	class SearchResult:
    36	    """The answer set plus the complete candidate ordering and instrumentation."""
    37	
    38	    hits: list[SearchHit]
    39	    ranking: list[tuple[int, str]]
    40	    no_answer: bool
    41	    timings: dict[str, float]
    42	    mode: str
FILE xyz/eval/metrics.py
     1	"""Depth-bounded retrieval metrics with chunk identity preserved."""
     2	
     3	from __future__ import annotations
     4	
     5	import json
     6	from dataclasses import dataclass
     7	from pathlib import Path
     8	from typing import Any, Mapping, Sequence
     9	
    10	Ranking = Sequence[tuple[int, str]]
    11	
    12	
    13	@dataclass(frozen=True)
    14	class Report:
    15	    """Serializable MRR/recall report for one retrieval mode."""
    16	
    17	    mrr: float
    18	    recalls: Mapping[int, float]
    19	    never_found: int
    20	    depth: int
    21	    per_query: Sequence[Mapping[str, Any]]
    22	
    23	    def to_dict(self) -> dict[str, Any]:
    24	        return {
    25	            "mrr": self.mrr,
    26	            "recall@1": self.recalls[1],
    27	            "recall@3": self.recalls[3],
    28	            "recall@5": self.recalls[5],
    29	            "recall@10": self.recalls[10],
    30	            "never_found": self.never_found,
    31	            "depth": self.depth,
    32	            "per_query": list(self.per_query),
    33	        }
    34	
    35	    def write_json(self, path: str | Path) -> None:
    36	        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
    37	
    38	
    39	def score(
    40	    rankings: Mapping[str, Ranking],
    41	    queries: Sequence[Mapping[str, Any]],
    42	    depth: int,
    43	) -> Report:
    44	    """Score ordered chunk rankings against path-level relevance at ``depth``."""
    45	    if not queries:
    46	        raise ValueError("query list is empty")
    47	    if depth <= 0:
    48	        raise ValueError("depth must be positive")
    49	
    50	    ranks: list[int | None] = []
    51	    rows: list[dict[str, Any]] = []
    52	    for query in queries:
    53	        text = str(query["q"])
    54	        relevant = [str(path) for path in query["relevant"]]
    55	        ordered = list(rankings.get(text, ()))[:depth]
    56	        relevant_set = set(relevant)
    57	        rank = next(
    58	            (
    59	                position
    60	                for position, (_chunk_id, path) in enumerate(ordered, start=1)
    61	                if path in relevant_set
    62	            ),
    63	            None,
    64	        )
    65	        ranks.append(rank)
    66	        rows.append(
    67	            {
    68	                "q": text,
    69	                "relevant": relevant,
    70	                "rank": rank,
    71	                "top_hit": ordered[0][1] if ordered else None,
    72	                "ranking": [
    73	                    {"chunk_id": int(chunk_id), "path": str(path)}
    74	                    for chunk_id, path in ordered
    75	                ],
    76	            }
    77	        )
    78	
    79	    count = len(ranks)
    80	    recalls = {
    81	        k: round(sum(rank is not None and rank <= k for rank in ranks) / count, 4)
    82	        for k in (1, 3, 5, 10)
    83	    }
    84	    return Report(
    85	        mrr=round(sum(1.0 / rank for rank in ranks if rank is not None) / count, 4),
    86	        recalls=recalls,
    87	        never_found=sum(rank is None for rank in ranks),
    88	        depth=depth,
    89	        per_query=rows,
    90	    )
FILE xyz/cli.py
     1	"""Command-line entry point for XYZ Code Intelligence."""
     2	
     3	from __future__ import annotations
     4	
     5	import argparse
     6	import json
     7	import os
     8	import resource
     9	import sys
    10	from dataclasses import asdict
    11	from pathlib import Path
    12	from typing import Any, Sequence
    13	
    14	from xyz import __version__
    15	from xyz.eval.metrics import score
    16	from xyz.index import CodeRankEmbedder, EmptyCorpus, Store
    17	from xyz.retrieve import Retriever
    18	from xyz.retrieve.latency import LatencyLog
    19	from xyz.retrieve.pipeline import MODES
    20	from xyz.retrieve.rerank import CrossEncoderReranker
    21	
    22	
    23	def _make_embedder() -> CodeRankEmbedder:
    24	    return CodeRankEmbedder(device=os.environ.get("XYZ_DEVICE"))
    25	
    26	
    27	def _make_reranker() -> CrossEncoderReranker:
    28	    return CrossEncoderReranker(device=os.environ.get("XYZ_DEVICE"))
    29	
    30	
    31	def _parser() -> argparse.ArgumentParser:
    32	    parser = argparse.ArgumentParser(prog="xyz")
    33	    parser.add_argument("--version", action="version", version=__version__)
    34	    subparsers = parser.add_subparsers(dest="command", metavar="{ingest,query,eval}")
    35	
    36	    ingest = subparsers.add_parser("ingest", help="ingest a repository")
    37	    ingest.add_argument("--db", required=True)
    38	    ingest.add_argument("--repo", required=True)
    39	    ingest.add_argument("--include-prefix", action="append", default=None)
    40	    ingest.add_argument("path")
    41	
    42	    query = subparsers.add_parser("query", help="query an index")
    43	    query.add_argument("--db", required=True)
    44	    query.add_argument("--mode", choices=sorted(MODES), default="auto")
    45	    query.add_argument("--k", type=int, default=10)
    46	    query.add_argument("--tau", type=float)
    47	    query.add_argument("text")
    48	
    49	    evaluate = subparsers.add_parser("eval", help="score retrieval modes")
    50	    evaluate.add_argument("--db", required=True)
    51	    evaluate.add_argument("--queries", required=True)
    52	    evaluate.add_argument(
    53	        "--modes",
    54	        default="dense,bm25,hybrid,hybrid+rerank",
    55	        help="comma-separated retrieval modes",
    56	    )
    57	    evaluate.add_argument("--depth", type=int, default=100)
    58	    evaluate.add_argument("--out", required=True)
    59	    return parser
    60	
    61	
    62	def _error(message: str) -> int:
    63	    print(f"xyz: error: {message}", file=sys.stderr)
    64	    return 2
    65	
    66	
    67	def _peak_rss_mb() -> float:
    68	    rss = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    69	    if sys.platform == "darwin":
    70	        return rss / (1024 * 1024)
    71	    return rss / 1024
    72	
    73	
    74	def _record_ingest_metadata(store: Store, repo: str, prefixes: Sequence[str] | None) -> None:
    75	    with store.connection:
    76	        store.connection.execute(
    77	            "INSERT OR REPLACE INTO meta(key, value) VALUES ('ingest.repo', ?)", (repo,)
    78	        )
    79	        store.connection.execute(
    80	            "INSERT OR REPLACE INTO meta(key, value) VALUES ('ingest.include_prefixes', ?)",
    81	            (json.dumps(list(prefixes or [])),),
    82	        )
    83	
    84	
    85	def _ingest(args: argparse.Namespace) -> int:
    86	    root = Path(args.path)
    87	    if not root.is_dir():
    88	        return _error(f"repository path is not a directory: {root}")
    89	
    90	    eta_printed = False
    91	
    92	    def progress(done: int, total: int, elapsed: float) -> None:
    93	        nonlocal eta_printed
    94	        if not eta_printed and done >= 200:
    95	            remaining = max(0.0, elapsed / done * max(0, total - done))
    96	            print(f"progress: {done}/{total} chunks embedded; ETA {remaining / 60:.1f} minutes")
    97	            eta_printed = True
    98	
    99	    try:
   100	        with Store.open(args.db, _make_embedder()) as store:
   101	            report = store.ingest(
   102	                args.repo,
   103	                root,
   104	                include_prefixes=args.include_prefix,
   105	                progress=progress,
   106	            )
   107	            _record_ingest_metadata(store, args.repo, args.include_prefix)
   108	            stats = store.stats()
   109	    except EmptyCorpus as exc:
   110	        return _error(str(exc))
   111	
   112	    print(
   113	        json.dumps(
   114	            {
   115	                "ingest": asdict(report),
   116	                "stats": asdict(stats),
   117	                "peak_rss_mb": round(_peak_rss_mb(), 2),
   118	            }
   119	        )
   120	    )
   121	    return 0
   122	
   123	
   124	def _query(args: argparse.Namespace) -> int:
   125	    if args.k <= 0:
   126	        return _error("k must be positive")
   127	    embedder = _make_embedder()
   128	    reranker = _make_reranker() if args.mode in {"auto", "hybrid+rerank"} else None
   129	    with Store.open(args.db, embedder) as store:
   130	        result = Retriever(store, embedder, reranker).search(
   131	            args.text, k=args.k, fetch_k=max(100, args.k), mode=args.mode, tau=args.tau
   132	        )
   133	    if result.no_answer:
   134	        print("no answer")
   135	    else:
   136	        print("rank\tpath\tqualified_name\tlines\tscore")
   137	        for rank, hit in enumerate(result.hits, start=1):
   138	            print(
   139	                f"{rank}\t{hit.path}\t{hit.qualified_name}\t"
   140	                f"{hit.start_line}-{hit.end_line}\t{hit.score:.6f}"
   141	            )
   142	    print("timings_ms " + json.dumps(result.timings, sort_keys=True))
   143	    return 0
   144	
   145	
   146	def _load_queries(path: str) -> list[dict[str, Any]]:
   147	    payload = json.loads(Path(path).read_text(encoding="utf-8"))
   148	    rows = payload.get("queries", []) if isinstance(payload, dict) else payload
   149	    if not isinstance(rows, list):
   150	        raise ValueError("query file must contain a list or a top-level 'queries' list")
   151	    return rows
   152	
   153	
   154	def _stored_prefixes(store: Store) -> list[str]:
   155	    row = store.connection.execute(
   156	        "SELECT value FROM meta WHERE key = 'ingest.include_prefixes'"
   157	    ).fetchone()
   158	    return list(json.loads(row[0])) if row else []
   159	
   160	
   161	def _eval(args: argparse.Namespace) -> int:
   162	    if args.depth <= 0:
   163	        return _error("depth must be positive")
   164	    try:
   165	        queries = _load_queries(args.queries)
   166	    except (OSError, ValueError, json.JSONDecodeError) as exc:
   167	        return _error(f"cannot read query file: {exc}")
   168	    if not queries:
   169	        return _error("query list is empty")
   170	
   171	    modes = [mode.strip() for mode in args.modes.split(",") if mode.strip()]
   172	    invalid = [mode for mode in modes if mode not in MODES or mode == "auto"]
   173	    if not modes or invalid:
   174	        return _error(f"invalid eval modes: {', '.join(invalid) or '(none)'}")
   175	
   176	    embedder = _make_embedder()
   177	    needs_reranker = "hybrid+rerank" in modes
   178	    with Store.open(args.db, embedder) as store:
   179	        stats = store.stats()
   180	        if stats.chunks == 0:
   181	            return _error("cannot evaluate an empty corpus")
   182	        corpus_paths = {
   183	            row[0] for row in store.connection.execute("SELECT DISTINCT path FROM chunks")
   184	        }
   185	        gold_paths = {str(path) for query in queries for path in query.get("relevant", [])}
   186	        missing = sorted(gold_paths - corpus_paths)
   187	        if missing:
   188	            return _error("gold paths missing from corpus: " + ", ".join(missing))
   189	
   190	        retriever = Retriever(store, embedder, _make_reranker() if needs_reranker else None)
   191	        reports: dict[str, dict[str, Any]] = {}
   192	        latency: dict[str, dict[str, dict[str, float]]] = {}
   193	        raw_rankings: dict[str, dict[str, list[tuple[int, str]]]] = {}
   194	        for mode in modes:
   195	            mode_rankings: dict[str, list[tuple[int, str]]] = {}
   196	            timing_log = LatencyLog()
   197	            for query in queries:
   198	                text = str(query["q"])
   199	                result = retriever.search(
   200	                    text, k=min(10, args.depth), fetch_k=args.depth, mode=mode
   201	                )
   202	                mode_rankings[text] = result.ranking
   203	                timing_log.add(result.timings)
   204	            raw_rankings[mode] = mode_rankings
   205	            reports[mode] = score(mode_rankings, queries, args.depth).to_dict()
   206	            latency[mode] = timing_log.summary()
   207	
   208	        reorder_count = 0
   209	        if "hybrid" in raw_rankings and "hybrid+rerank" in raw_rankings:
   210	            for query in queries:
   211	                text = str(query["q"])
   212	                before = [chunk_id for chunk_id, _path in raw_rankings["hybrid"][text][:10]]
   213	                after = [
   214	                    chunk_id
   215	                    for chunk_id, _path in raw_rankings["hybrid+rerank"][text][:10]
   216	                ]
   217	                reorder_count += before != after
   218	
   219	        payload = {
   220	            "reports": reports,
   221	            "latency": latency,
   222	            "corpus": {
   223	                "chunk_count": stats.chunks,
   224	                "file_count": stats.files,
   225	                "include_prefixes": _stored_prefixes(store),
   226	                "db": str(Path(args.db).resolve()),
   227	            },
   228	            "reorder_count": reorder_count,
   229	        }
   230	
   231	    out = Path(args.out)
   232	    out.parent.mkdir(parents=True, exist_ok=True)
   233	    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
   234	    print("mode\tMRR@D\tR@1\tR@3\tR@5\tR@10\tmiss@D")
   235	    for mode in modes:
   236	        report = reports[mode]
   237	        print(
   238	            f"{mode}\t{report['mrr']:.4f}\t{report['recall@1']:.4f}\t"
   239	            f"{report['recall@3']:.4f}\t{report['recall@5']:.4f}\t"
   240	            f"{report['recall@10']:.4f}\t{report['never_found']}"
   241	        )
   242	    print(f"depth={args.depth}; reorder_count={reorder_count}")
   243	    return 0
   244	
   245	
   246	def main(argv: list[str] | None = None) -> int:
   247	    """Parse the command line and return a process exit status."""
   248	    parser = _parser()
   249	    try:
   250	        args = parser.parse_args(argv)
   251	    except SystemExit as exc:
   252	        return int(exc.code)
   253	    if args.command is None:
   254	        parser.print_help()
   255	        return 0
   256	    try:
   257	        return {"ingest": _ingest, "query": _query, "eval": _eval}[args.command](args)
   258	    except (OSError, ValueError) as exc:
   259	        return _error(str(exc))
FILE xyz/__init__.py
     1	"""XYZ Code Intelligence package."""
     2	
     3	__version__ = "0.5.0.dev0"
FILE xyz/__main__.py
     1	"""Run the XYZ Code Intelligence command-line interface."""
     2	
     3	from xyz.cli import main
     4	
     5	
     6	if __name__ == "__main__":
     7	    raise SystemExit(main())

exec
/bin/zsh -lc "nl -ba xyz/index/store.py | sed -n '430,480p'
nl -ba xyz/index/embed.py
nl -ba xyz/ingest/walk.py
nl -ba xyz/ingest/chunk.py | sed -n '1,420p'
nl -ba xyz/retrieve/dense.py
nl -ba xyz/retrieve/lexical.py
nl -ba xyz/retrieve/fuse.py
nl -ba xyz/retrieve/pipeline.py" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 0ms:
   430	            chunks_written=chunks_written,
   431	            chunks_embedded=chunks_embedded,
   432	            cache_hits=cache_hits,
   433	            warnings=tuple(warnings),
   434	            seconds=time.monotonic() - started,
   435	        )
   436	
   437	    def stats(self) -> StoreStats:
   438	        def count(table: str) -> int:
   439	            return int(self.connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0])
   440	
   441	        return StoreStats(
   442	            chunks=count("chunks"),
   443	            chunks_fts=count("chunks_fts"),
   444	            chunks_vec=count("chunks_vec"),
   445	            embed_cache=count("embed_cache"),
   446	            files=count("files"),
   447	        )
   448	
   449	    def fts_match(self, token: str, limit: int = 100) -> list[int]:
   450	        return [
   451	            int(row[0])
   452	            for row in self.connection.execute(
   453	                "SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?",
   454	                (token, limit),
   455	            )
   456	        ]
     1	"""Embedding contracts and the local CodeRankEmbed provider."""
     2	
     3	from __future__ import annotations
     4	
     5	import os
     6	from collections.abc import Callable, Sequence
     7	from typing import Any, Protocol
     8	
     9	import numpy as np
    10	
    11	
    12	QUERY_PREFIX = "Represent this query for searching relevant code: "
    13	DEFAULT_MODEL_ID = "nomic-ai/CodeRankEmbed"
    14	DEFAULT_DIM = 768
    15	MAX_SEQ_LENGTH = 2048
    16	
    17	
    18	class Embedder(Protocol):
    19	    """Minimal embedding interface shared by indexing and retrieval."""
    20	
    21	    model_id: str
    22	    dim: int
    23	    provider: str
    24	
    25	    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
    26	        """Return one float32 unit vector per document."""
    27	
    28	    def encode_query(self, text: str) -> np.ndarray:
    29	        """Return one float32 unit vector for a natural-language query."""
    30	
    31	
    32	def _positive_env_int(name: str, default: int) -> int:
    33	    raw = os.environ.get(name)
    34	    if raw is None:
    35	        return default
    36	    try:
    37	        value = int(raw)
    38	    except ValueError as exc:
    39	        raise ValueError(f"{name} must be a positive integer, got {raw!r}") from exc
    40	    if value <= 0:
    41	        raise ValueError(f"{name} must be a positive integer, got {raw!r}")
    42	    return value
    43	
    44	
    45	def _unit_float32(vectors: Any, *, rows: int, dim: int) -> np.ndarray:
    46	    array = np.asarray(vectors, dtype=np.float32)
    47	    if rows == 1 and array.shape == (dim,):
    48	        array = array.reshape(1, dim)
    49	    if array.shape != (rows, dim):
    50	        raise ValueError(f"embedder returned shape {array.shape}; expected {(rows, dim)}")
    51	    norms = np.linalg.norm(array, axis=1, keepdims=True)
    52	    if np.any(norms == 0):
    53	        raise ValueError("embedder returned a zero-length vector")
    54	    return np.asarray(array / norms, dtype=np.float32)
    55	
    56	
    57	class CodeRankEmbedder:
    58	    """On-device CodeRankEmbed adapter with the repository memory guards."""
    59	
    60	    provider = "sentence-transformers"
    61	    dim = DEFAULT_DIM
    62	
    63	    def __init__(
    64	        self,
    65	        model_id: str = DEFAULT_MODEL_ID,
    66	        *,
    67	        model_factory: Callable[..., Any] | None = None,
    68	        device: str | None = None,
    69	    ) -> None:
    70	        os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    71	        self.model_id = model_id
    72	        self.batch_size = _positive_env_int("EMBED_BATCH_SIZE", 16)
    73	        max_threads = _positive_env_int("EMBED_MAX_THREADS", max(1, os.cpu_count() or 1))
    74	
    75	        import torch
    76	
    77	        torch.set_num_threads(max_threads)
    78	        if device is None:
    79	            device = "mps" if torch.backends.mps.is_available() else "cpu"
    80	        if model_factory is None:
    81	            from sentence_transformers import SentenceTransformer
    82	
    83	            model_factory = SentenceTransformer
    84	        self.model = model_factory(model_id, trust_remote_code=True, device=device)
    85	        self.model.max_seq_length = MAX_SEQ_LENGTH
    86	
    87	    def _encode(self, texts: Sequence[str]) -> np.ndarray:
    88	        materialised = list(texts)
    89	        if not materialised:
    90	            return np.empty((0, self.dim), dtype=np.float32)
    91	        encoded = self.model.encode(
    92	            materialised,
    93	            batch_size=self.batch_size,
    94	            normalize_embeddings=True,
    95	            convert_to_numpy=True,
    96	            show_progress_bar=False,
    97	        )
    98	        return _unit_float32(encoded, rows=len(materialised), dim=self.dim)
    99	
   100	    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
   101	        return self._encode(texts)
   102	
   103	    def encode_query(self, text: str) -> np.ndarray:
   104	        return self._encode([QUERY_PREFIX + text])[0]
     1	"""Deterministic, failure-aware repository traversal."""
     2	
     3	from __future__ import annotations
     4	
     5	import fnmatch
     6	import os
     7	from collections.abc import Iterator, Sequence, Set
     8	from pathlib import Path
     9	
    10	
    11	DEFAULT_INCLUDE = frozenset(
    12	    {
    13	        ".py",
    14	        ".js",
    15	        ".ts",
    16	        ".tsx",
    17	        ".jsx",
    18	        ".php",
    19	        ".md",
    20	        ".go",
    21	        ".rb",
    22	        ".sh",
    23	        ".yml",
    24	        ".yaml",
    25	        ".toml",
    26	        ".ini",
    27	        ".cfg",
    28	        ".json",
    29	        ".sql",
    30	        ".html",
    31	        ".twig",
    32	        "Dockerfile",
    33	        "docker-compose*.yml",
    34	        "Makefile",
    35	        "*.blade.php",
    36	        ".env.example",
    37	    }
    38	)
    39	
    40	DEFAULT_EXCLUDE = frozenset(
    41	    {
    42	        ".git",
    43	        ".venv",
    44	        "node_modules",
    45	        "__pycache__",
    46	        "dist",
    47	        "build",
    48	        "temp",
    49	        ".embed-tmp",
    50	        ".xyz",
    51	        ".relay-scratch",
    52	        "marathon-system",
    53	        "relay-system",
    54	    }
    55	)
    56	
    57	MAX_FILE_BYTES = 1024 * 1024
    58	BINARY_SNIFF_BYTES = 8192
    59	
    60	
    61	def _included(name: str, include: Set[str] | Sequence[str]) -> bool:
    62	    suffix = Path(name).suffix.lower()
    63	    for rule in include:
    64	        if rule.startswith(".") and "*" not in rule:
    65	            if rule == suffix or rule == name:
    66	                return True
    67	        elif fnmatch.fnmatchcase(name, rule):
    68	            return True
    69	    return False
    70	
    71	
    72	def _normalise_prefixes(prefixes: Sequence[str] | None) -> tuple[str, ...] | None:
    73	    if prefixes is None:
    74	        return None
    75	    normalised: list[str] = []
    76	    for prefix in prefixes:
    77	        value = prefix.replace(os.sep, "/")
    78	        if value.startswith("./"):
    79	            value = value[2:]
    80	        value = value.lstrip("/")
    81	        if value and not value.endswith("/"):
    82	            value += "/"
    83	        normalised.append(value)
    84	    return tuple(sorted(set(normalised)))
    85	
    86	
    87	def _directory_may_match(rel_dir: str, prefixes: tuple[str, ...] | None) -> bool:
    88	    if prefixes is None:
    89	        return True
    90	    directory = f"{rel_dir}/" if rel_dir else ""
    91	    return any(prefix.startswith(directory) or directory.startswith(prefix) for prefix in prefixes)
    92	
    93	
    94	def _file_matches(rel_path: str, prefixes: tuple[str, ...] | None) -> bool:
    95	    return prefixes is None or any(rel_path.startswith(prefix) for prefix in prefixes)
    96	
    97	
    98	def walk_repo(
    99	    root: str | os.PathLike[str],
   100	    include_ext: Set[str] | Sequence[str] = DEFAULT_INCLUDE,
   101	    exclude_dirs: Set[str] | Sequence[str] = DEFAULT_EXCLUDE,
   102	    include_prefixes: Sequence[str] | None = None,
   103	    *,
   104	    errors: list[str],
   105	) -> Iterator[tuple[str, bytes]]:
   106	    """Yield included ``(relative_path, content)`` pairs in sorted order.
   107	
   108	    Enumeration, stat, and read failures for relevant candidate paths are
   109	    recorded in ``errors``. Intentional filters are silent.
   110	    """
   111	
   112	    root_path = Path(root)
   113	    if not root_path.is_dir():
   114	        raise ValueError(f"repository root is not an existing directory: {root_path}")
   115	
   116	    excluded = set(exclude_dirs)
   117	    prefixes = _normalise_prefixes(include_prefixes)
   118	
   119	    def visit(directory: Path, rel_dir: str) -> Iterator[tuple[str, bytes]]:
   120	        try:
   121	            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
   122	        except OSError as exc:
   123	            label = rel_dir or "."
   124	            errors.append(f"{label}: {type(exc).__name__}: {exc}")
   125	            return
   126	
   127	        for entry in entries:
   128	            rel_path = f"{rel_dir}/{entry.name}" if rel_dir else entry.name
   129	            rel_path = rel_path.replace(os.sep, "/")
   130	            try:
   131	                is_dir = entry.is_dir(follow_symlinks=False)
   132	                is_file = entry.is_file(follow_symlinks=False)
   133	            except OSError as exc:
   134	                errors.append(f"{rel_path}: {type(exc).__name__}: {exc}")
   135	                continue
   136	
   137	            if is_dir:
   138	                if entry.name in excluded or not _directory_may_match(rel_path, prefixes):
   139	                    continue
   140	                yield from visit(Path(entry.path), rel_path)
   141	                continue
   142	
   143	            if not is_file or not _file_matches(rel_path, prefixes):
   144	                continue
   145	            if not _included(entry.name, include_ext):
   146	                continue
   147	
   148	            try:
   149	                if entry.stat(follow_symlinks=False).st_size > MAX_FILE_BYTES:
   150	                    continue
   151	                with open(entry.path, "rb") as handle:
   152	                    head = handle.read(BINARY_SNIFF_BYTES)
   153	                    if b"\0" in head:
   154	                        continue
   155	                    content = head + handle.read()
   156	            except OSError as exc:
   157	                errors.append(f"{rel_path}: {type(exc).__name__}: {exc}")
   158	                continue
   159	            yield rel_path, content
   160	
   161	    yield from visit(root_path, "")
     1	"""Language-aware source chunking with deterministic hard bounds."""
     2	
     3	from __future__ import annotations
     4	
     5	import hashlib
     6	import re
     7	from dataclasses import dataclass
     8	from pathlib import PurePosixPath
     9	
    10	from tree_sitter import Node
    11	from tree_sitter_language_pack import get_parser
    12	
    13	
    14	MAX_CHARS = 6000
    15	SPLIT_SEARCH_CHARS = 1500
    16	SPLIT_OVERLAP_CHARS = 150
    17	
    18	
    19	@dataclass(frozen=True)
    20	class Chunk:
    21	    repo: str
    22	    path: str
    23	    kind: str
    24	    qualified_name: str
    25	    start_line: int
    26	    end_line: int
    27	    text: str
    28	    embedded_text: str
    29	    content_sha: str
    30	
    31	
    32	@dataclass(frozen=True)
    33	class ChunkResult:
    34	    chunks: list[Chunk]
    35	    warnings: list[str]
    36	
    37	
    38	@dataclass(frozen=True)
    39	class _Draft:
    40	    kind: str
    41	    qualified_name: str
    42	    text: str
    43	    line_map: tuple[int, ...]
    44	
    45	
    46	_LANGUAGES = {
    47	    ".py": "python",
    48	    ".js": "javascript",
    49	    ".jsx": "javascript",
    50	    ".ts": "typescript",
    51	    ".tsx": "tsx",
    52	    ".php": "php",
    53	}
    54	
    55	_TOP_LEVEL_TYPES = {
    56	    "python": {"function_definition": "function", "class_definition": "class"},
    57	    "javascript": {"function_declaration": "function", "class_declaration": "class"},
    58	    "typescript": {"function_declaration": "function", "class_declaration": "class"},
    59	    "tsx": {"function_declaration": "function", "class_declaration": "class"},
    60	    "php": {"function_definition": "function", "class_declaration": "class"},
    61	}
    62	
    63	
    64	def _line_map(text: str, start_line: int) -> tuple[int, ...]:
    65	    line = start_line
    66	    result: list[int] = []
    67	    for char in text:
    68	        result.append(line)
    69	        if char == "\n":
    70	            line += 1
    71	    return tuple(result)
    72	
    73	
    74	def _line_at(source: bytes, byte_offset: int) -> int:
    75	    """Return a one-based line without trusting parser point metadata."""
    76	    return source[:byte_offset].count(b"\n") + 1
    77	
    78	
    79	def _draft(kind: str, qualified_name: str, text: str, start_line: int) -> _Draft:
    80	    return _Draft(kind, qualified_name, text, _line_map(text, start_line))
    81	
    82	
    83	def _trim(text: str, line_map: tuple[int, ...]) -> tuple[str, tuple[int, ...]]:
    84	    left = len(text) - len(text.lstrip())
    85	    right = len(text.rstrip())
    86	    return text[left:right], line_map[left:right]
    87	
    88	
    89	def _node_name(node: Node) -> str | None:
    90	    name = node.child_by_field_name("name")
    91	    if name is None:
    92	        return None
    93	    return name.text.decode("utf-8", errors="replace")
    94	
    95	
    96	def _unwrap_definition(node: Node, language: str) -> Node | None:
    97	    wanted = _TOP_LEVEL_TYPES[language]
    98	    if node.type in wanted:
    99	        return node
   100	    if node.type in {"decorated_definition", "export_statement"}:
   101	        return next((child for child in node.named_children if child.type in wanted), None)
   102	    return None
   103	
   104	
   105	def _method_nodes(class_node: Node, language: str) -> list[Node]:
   106	    if language == "python":
   107	        body = class_node.child_by_field_name("body")
   108	        method_type = "function_definition"
   109	        wrappers = {"decorated_definition"}
   110	    elif language == "php":
   111	        body = class_node.child_by_field_name("body")
   112	        if body is None:
   113	            body = next((child for child in class_node.named_children if child.type == "declaration_list"), None)
   114	        method_type = "method_declaration"
   115	        wrappers = set()
   116	    else:
   117	        body = class_node.child_by_field_name("body")
   118	        method_type = "method_definition"
   119	        wrappers = set()
   120	    if body is None:
   121	        return []
   122	
   123	    methods: list[Node] = []
   124	    for child in body.named_children:
   125	        if child.type == method_type:
   126	            methods.append(child)
   127	        elif child.type in wrappers:
   128	            wrapped = next((item for item in child.named_children if item.type == method_type), None)
   129	            if wrapped is not None:
   130	                methods.append(child)
   131	    return methods
   132	
   133	
   134	def _ast_drafts(rel_path: str, source: bytes, language: str) -> list[_Draft]:
   135	    tree = get_parser(language).parse(source)
   136	    if tree.root_node.has_error:
   137	        raise ValueError("syntax tree contains parse errors")
   138	
   139	    drafts: list[_Draft] = []
   140	    occupied: list[tuple[int, int]] = []
   141	    for outer in tree.root_node.named_children:
   142	        definition = _unwrap_definition(outer, language)
   143	        if definition is None:
   144	            continue
   145	        name = _node_name(definition)
   146	        if not name:
   147	            continue
   148	        kind = _TOP_LEVEL_TYPES[language][definition.type]
   149	        text = source[outer.start_byte : outer.end_byte].decode("utf-8", errors="replace")
   150	        drafts.append(_draft(kind, name, text, _line_at(source, outer.start_byte)))
   151	        occupied.append((outer.start_byte, outer.end_byte))
   152	
   153	        if kind == "class":
   154	            for method in _method_nodes(definition, language):
   155	                method_definition = method
   156	                if method.type == "decorated_definition":
   157	                    method_definition = next(
   158	                        child for child in method.named_children if child.type == "function_definition"
   159	                    )
   160	                method_name = _node_name(method_definition)
   161	                if method_name:
   162	                    method_text = source[method.start_byte : method.end_byte].decode(
   163	                        "utf-8", errors="replace"
   164	                    )
   165	                    drafts.append(
   166	                        _draft(
   167	                            "method",
   168	                            f"{name}.{method_name}",
   169	                            method_text,
   170	                            _line_at(source, method.start_byte),
   171	                        )
   172	                    )
   173	
   174	    residual_parts: list[tuple[str, tuple[int, ...]]] = []
   175	    cursor = 0
   176	    for start, end in sorted(occupied):
   177	        if start > cursor:
   178	            raw = source[cursor:start].decode("utf-8", errors="replace")
   179	            mapped = _line_map(raw, _line_at(source, cursor))
   180	            part = _trim(raw, mapped)
   181	            if part[0]:
   182	                residual_parts.append(part)
   183	        cursor = max(cursor, end)
   184	    if cursor < len(source):
   185	        raw = source[cursor:].decode("utf-8", errors="replace")
   186	        mapped = _line_map(raw, _line_at(source, cursor))
   187	        part = _trim(raw, mapped)
   188	        if part[0]:
   189	            residual_parts.append(part)
   190	
   191	    if residual_parts:
   192	        text_bits: list[str] = []
   193	        map_bits: list[int] = []
   194	        for index, (text, mapped) in enumerate(residual_parts):
   195	            if index:
   196	                marker_line = map_bits[-1] if map_bits else mapped[0]
   197	                marker = "\n# …\n"
   198	                text_bits.append(marker)
   199	                map_bits.extend([marker_line] * len(marker))
   200	            text_bits.append(text)
   201	            map_bits.extend(mapped)
   202	        drafts.append(_Draft("module", rel_path, "".join(text_bits), tuple(map_bits)))
   203	
   204	    drafts.sort(key=lambda item: (item.line_map[0], {"module": 0, "class": 1, "function": 1, "method": 2}.get(item.kind, 3), item.qualified_name))
   205	    return drafts
   206	
   207	
   208	_HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$")
   209	
   210	
   211	def _markdown_drafts(rel_path: str, text: str) -> list[_Draft]:
   212	    lines = text.splitlines(keepends=True)
   213	    headings: list[tuple[int, int, str]] = []
   214	    for index, line in enumerate(lines):
   215	        match = _HEADING.match(line.rstrip("\r\n"))
   216	        if match:
   217	            headings.append((index, len(match.group(1)), match.group(2).strip()))
   218	
   219	    boundaries = [item[0] for item in headings]
   220	    drafts: list[_Draft] = []
   221	    if not headings:
   222	        body = text.rstrip()
   223	        return [_draft("file", rel_path, body, 1)] if body else []
   224	
   225	    first_heading = headings[0][0]
   226	    if first_heading:
   227	        preamble = "".join(lines[:first_heading]).rstrip()
   228	        if preamble:
   229	            drafts.append(_draft("preamble", rel_path, preamble, 1))
   230	
   231	    path: list[str] = []
   232	    for position, (start, level, title) in enumerate(headings):
   233	        path = path[: level - 1]
   234	        path.append(title)
   235	        end = boundaries[position + 1] if position + 1 < len(boundaries) else len(lines)
   236	        body = "".join(lines[start:end]).rstrip()
   237	        if body:
   238	            drafts.append(_draft("section", " > ".join(path), body, start + 1))
   239	    return drafts
   240	
   241	
   242	def _file_drafts(rel_path: str, text: str) -> list[_Draft]:
   243	    body = text.rstrip()
   244	    return [_draft("file", rel_path, body, 1)] if body else []
   245	
   246	
   247	def _split_draft(draft: _Draft) -> list[_Draft]:
   248	    if len(draft.text) <= MAX_CHARS:
   249	        return [draft]
   250	
   251	    result: list[_Draft] = []
   252	    start = 0
   253	    part_number = 1
   254	    while len(draft.text) - start > MAX_CHARS:
   255	        limit = start + MAX_CHARS
   256	        blank = draft.text.rfind("\n\n", limit - SPLIT_SEARCH_CHARS, limit)
   257	        cut = blank + 2 if blank >= start else limit
   258	        name = draft.qualified_name if part_number == 1 else f"{draft.qualified_name}#{part_number}"
   259	        result.append(_Draft(draft.kind, name, draft.text[start:cut], draft.line_map[start:cut]))
   260	        next_start = max(cut - SPLIT_OVERLAP_CHARS, start + 1)
   261	        start = next_start
   262	        part_number += 1
   263	    name = draft.qualified_name if part_number == 1 else f"{draft.qualified_name}#{part_number}"
   264	    result.append(_Draft(draft.kind, name, draft.text[start:], draft.line_map[start:]))
   265	    return result
   266	
   267	
   268	def _materialise(repo: str, rel_path: str, draft: _Draft) -> Chunk:
   269	    embedded_text = f"{rel_path}\n\n{draft.text}"
   270	    non_newline = [line for char, line in zip(draft.text, draft.line_map) if char not in "\r\n"]
   271	    start_line = non_newline[0] if non_newline else draft.line_map[0]
   272	    end_line = non_newline[-1] if non_newline else draft.line_map[-1]
   273	    return Chunk(
   274	        repo=repo,
   275	        path=rel_path,
   276	        kind=draft.kind,
   277	        qualified_name=draft.qualified_name,
   278	        start_line=start_line,
   279	        end_line=end_line,
   280	        text=draft.text,
   281	        embedded_text=embedded_text,
   282	        content_sha=hashlib.sha256(embedded_text.encode("utf-8")).hexdigest(),
   283	    )
   284	
   285	
   286	def chunk_file(repo: str, rel_path: str, source: bytes) -> ChunkResult:
   287	    """Chunk one source file, falling back to file chunks after parse errors."""
   288	
   289	    rel_path = rel_path.replace("\\", "/")
   290	    suffix = PurePosixPath(rel_path).suffix.lower()
   291	    text = source.decode("utf-8", errors="replace")
   292	    warnings: list[str] = []
   293	
   294	    if suffix in _LANGUAGES:
   295	        try:
   296	            drafts = _ast_drafts(rel_path, source, _LANGUAGES[suffix])
   297	        except Exception as exc:
   298	            warnings.append(f"{rel_path}: parse failed; used file chunker ({type(exc).__name__}: {exc})")
   299	            drafts = _file_drafts(rel_path, text)
   300	    elif suffix in {".md", ".markdown"}:
   301	        drafts = _markdown_drafts(rel_path, text)
   302	    else:
   303	        drafts = _file_drafts(rel_path, text)
   304	
   305	    chunks = [
   306	        _materialise(repo, rel_path, part)
   307	        for draft in drafts
   308	        for part in _split_draft(draft)
   309	        if part.text
   310	    ]
   311	    return ChunkResult(chunks, warnings)
     1	"""sqlite-vec nearest-neighbour retrieval."""
     2	
     3	from __future__ import annotations
     4	
     5	from collections.abc import Sequence
     6	
     7	import numpy as np
     8	import sqlite_vec
     9	
    10	from xyz.index.store import Store
    11	from xyz.retrieve.models import Hit
    12	
    13	
    14	KNN_SQL = """
    15	SELECT rowid, distance
    16	FROM chunks_vec
    17	WHERE embedding MATCH ? AND k = ?
    18	ORDER BY distance ASC
    19	"""
    20	
    21	
    22	def dense_search(store: Store, query_vec: Sequence[float] | np.ndarray, k: int) -> list[Hit]:
    23	    """Return the nearest vectors with negated distances as scores."""
    24	
    25	    if k <= 0:
    26	        return []
    27	    vector = np.asarray(query_vec, dtype=np.float32)
    28	    if vector.shape != (store.embedder.dim,):
    29	        raise ValueError(
    30	            f"query vector has shape {vector.shape}; expected {(store.embedder.dim,)}"
    31	        )
    32	    encoded = sqlite_vec.serialize_float32(vector.tolist())
    33	    rows = store.connection.execute(KNN_SQL, (encoded, k))
    34	    return [Hit(int(chunk_id), -float(distance), "dense") for chunk_id, distance in rows]
     1	"""FTS5/BM25 retrieval with safe query construction."""
     2	
     3	from __future__ import annotations
     4	
     5	import re
     6	
     7	from xyz.index.store import Store
     8	from xyz.retrieve.models import Hit
     9	
    10	
    11	_TOKEN = re.compile(r"[^\W_]+(?:_[^\W_]+)*", re.UNICODE)
    12	_STOPWORDS = frozenset(
    13	    {
    14	        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    15	        "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "with",
    16	    }
    17	)
    18	
    19	
    20	def sanitise_fts_query(query: str) -> str | None:
    21	    """Turn user text into an operator-free OR query, or ``None`` if empty."""
    22	
    23	    tokens: list[str] = []
    24	    seen: set[str] = set()
    25	    for match in _TOKEN.finditer(query):
    26	        token = match.group(0)
    27	        folded = token.casefold()
    28	        if folded in _STOPWORDS or folded in seen:
    29	            continue
    30	        seen.add(folded)
    31	        tokens.append(token.replace('"', '""'))
    32	    if not tokens:
    33	        return None
    34	    return " OR ".join(f'"{token}"' for token in tokens)
    35	
    36	
    37	def bm25_search(store: Store, query: str, k: int) -> list[Hit]:
    38	    """Return the best lexical matches with negated FTS5 BM25 scores."""
    39	
    40	    if k <= 0:
    41	        return []
    42	    safe_query = sanitise_fts_query(query)
    43	    if safe_query is None:
    44	        return []
    45	    rows = store.connection.execute(
    46	        """
    47	        SELECT rowid, bm25(chunks_fts) AS distance
    48	        FROM chunks_fts
    49	        WHERE chunks_fts MATCH ?
    50	        ORDER BY distance ASC, rowid ASC
    51	        LIMIT ?
    52	        """,
    53	        (safe_query, k),
    54	    )
    55	    return [Hit(int(chunk_id), -float(distance), "bm25") for chunk_id, distance in rows]
     1	"""Deterministic reciprocal-rank fusion."""
     2	
     3	from __future__ import annotations
     4	
     5	from collections.abc import Sequence
     6	
     7	from xyz.retrieve.models import Hit
     8	
     9	
    10	def rrf(rankings: Sequence[Sequence[Hit]], k: int = 60) -> list[Hit]:
    11	    """Fuse rankings using one-based ranks and deterministic chunk-id ties."""
    12	
    13	    if k < 0:
    14	        raise ValueError("RRF k must be non-negative")
    15	    scores: dict[int, float] = {}
    16	    for ranking in rankings:
    17	        seen: set[int] = set()
    18	        for rank, hit in enumerate(ranking, start=1):
    19	            if hit.chunk_id in seen:
    20	                continue
    21	            seen.add(hit.chunk_id)
    22	            scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (k + rank)
    23	    hits = [Hit(chunk_id, score, "rrf") for chunk_id, score in scores.items()]
    24	    return sorted(hits, key=lambda hit: (-hit.score, hit.chunk_id))
     1	"""Instrumented dense, lexical, hybrid, and reranked retrieval pipeline."""
     2	
     3	from __future__ import annotations
     4	
     5	import time
     6	from collections.abc import Sequence
     7	
     8	from xyz.index.embed import Embedder
     9	from xyz.index.store import Store
    10	from xyz.retrieve.dense import dense_search
    11	from xyz.retrieve.fuse import rrf
    12	from xyz.retrieve.lexical import bm25_search
    13	from xyz.retrieve.models import Hit, SearchHit, SearchResult
    14	from xyz.retrieve.rerank import Reranker
    15	
    16	
    17	TIMING_STAGES = ("embed_query", "bm25", "dense", "fuse", "rerank", "total")
    18	MODES = frozenset({"auto", "dense", "bm25", "hybrid", "hybrid+rerank"})
    19	
    20	
    21	class Retriever:
    22	    def __init__(self, store: Store, embedder: Embedder, reranker: Reranker | None = None) -> None:
    23	        store.check_embedder(embedder)
    24	        self.store = store
    25	        self.embedder = embedder
    26	        self.reranker = reranker
    27	
    28	    @staticmethod
    29	    def _elapsed(started: float) -> float:
    30	        return max(0.0, (time.perf_counter() - started) * 1000.0)
    31	
    32	    def _chunk_rows(self, ids: Sequence[int]) -> dict[int, tuple[object, ...]]:
    33	        if not ids:
    34	            return {}
    35	        placeholders = ",".join("?" for _ in ids)
    36	        rows = self.store.connection.execute(
    37	            f"""
    38	            SELECT id, repo, path, kind, qualified_name, start_line, end_line, text, embedded_text
    39	            FROM chunks WHERE id IN ({placeholders})
    40	            """,
    41	            tuple(ids),
    42	        )
    43	        return {int(row[0]): tuple(row[1:]) for row in rows}
    44	
    45	    def search(
    46	        self,
    47	        query: str,
    48	        k: int = 10,
    49	        fetch_k: int = 50,
    50	        mode: str = "auto",
    51	        tau: float | None = None,
    52	    ) -> SearchResult:
    53	        if mode not in MODES:
    54	            raise ValueError(f"unknown retrieval mode: {mode!r}")
    55	        if k <= 0 or fetch_k <= 0:
    56	            raise ValueError("k and fetch_k must be positive")
    57	        resolved = ("hybrid+rerank" if self.reranker is not None else "hybrid") if mode == "auto" else mode
    58	        if resolved == "hybrid+rerank" and self.reranker is None:
    59	            raise ValueError("hybrid+rerank mode requires a reranker")
    60	
    61	        timings = {stage: 0.0 for stage in TIMING_STAGES}
    62	        total_started = time.perf_counter()
    63	        dense_hits: list[Hit] = []
    64	        lexical_hits: list[Hit] = []
    65	
    66	        if resolved in {"dense", "hybrid", "hybrid+rerank"}:
    67	            started = time.perf_counter()
    68	            query_vec = self.embedder.encode_query(query)
    69	            timings["embed_query"] = self._elapsed(started)
    70	            started = time.perf_counter()
    71	            dense_hits = dense_search(self.store, query_vec, fetch_k)
    72	            timings["dense"] = self._elapsed(started)
    73	        if resolved in {"bm25", "hybrid", "hybrid+rerank"}:
    74	            started = time.perf_counter()
    75	            lexical_hits = bm25_search(self.store, query, fetch_k)
    76	            timings["bm25"] = self._elapsed(started)
    77	
    78	        if resolved == "dense":
    79	            candidates = dense_hits[:fetch_k]
    80	        elif resolved == "bm25":
    81	            candidates = lexical_hits[:fetch_k]
    82	        else:
    83	            started = time.perf_counter()
    84	            candidates = rrf([dense_hits, lexical_hits])[:fetch_k]
    85	            timings["fuse"] = self._elapsed(started)
    86	
    87	        if resolved == "hybrid+rerank" and candidates:
    88	            rerank_count = min(len(candidates), 50)
    89	            head = candidates[:rerank_count]
    90	            rows = self._chunk_rows([hit.chunk_id for hit in head])
    91	            texts = [str(rows[hit.chunk_id][7]) for hit in head]
    92	            started = time.perf_counter()
    93	            scores = self.reranker.score(query, texts)  # type: ignore[union-attr]
    94	            timings["rerank"] = self._elapsed(started)
    95	            if len(scores) != len(head):
    96	                raise ValueError(f"reranker returned {len(scores)} scores for {len(head)} candidates")
    97	            rescored = [
    98	                Hit(hit.chunk_id, float(score), "rerank")
    99	                for hit, score in zip(head, scores, strict=True)
   100	            ]
   101	            candidates = sorted(rescored, key=lambda hit: (-hit.score, hit.chunk_id)) + candidates[rerank_count:]
   102	
   103	        rows = self._chunk_rows([hit.chunk_id for hit in candidates])
   104	        ranking = [(hit.chunk_id, str(rows[hit.chunk_id][1])) for hit in candidates]
   105	        top_score = candidates[0].score if candidates else None
   106	        no_answer = top_score is None or (tau is not None and top_score < tau)
   107	        materialised: list[SearchHit] = []
   108	        if not no_answer:
   109	            for hit in candidates[:k]:
   110	                repo, path, kind, name, start_line, end_line, text, embedded_text = rows[hit.chunk_id]
   111	                materialised.append(
   112	                    SearchHit(
   113	                        hit.chunk_id, str(repo), str(path), str(kind), str(name),
   114	                        int(start_line), int(end_line), str(text), str(embedded_text),
   115	                        hit.score, hit.stage,
   116	                    )
   117	                )
   118	        timings["total"] = self._elapsed(total_started)
   119	        return SearchResult(materialised, ranking, no_answer, timings, resolved)

exec
/bin/zsh -lc 'for f in tests/test_chunkers.py tests/test_store.py tests/test_retrieve.py tests/test_metrics.py tests/test_cli.py tests/test_smoke.py tests/fakes.py; do echo "FILE $f"; nl -ba "$f"; done' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 0ms:
FILE tests/test_chunkers.py
     1	"""Contract tests for repository walking and source chunking."""
     2	
     3	from __future__ import annotations
     4	
     5	import os
     6	import shutil
     7	from pathlib import Path
     8	
     9	import pytest
    10	
    11	from xyz.ingest import chunk_file, chunk_repo, walk_repo
    12	
    13	
    14	FIXTURE = Path(__file__).parent / "fixtures" / "mini-repo"
    15	
    16	
    17	def _copy_fixture(tmp_path: Path) -> Path:
    18	    root = tmp_path / "mini-repo"
    19	    shutil.copytree(FIXTURE, root)
    20	    (root / "binary.py").write_bytes(b"print('before nul')\0ignored")
    21	    (root / "long.txt").write_text("x" * 6001, encoding="utf-8")
    22	    (root / "docs" / "long.md").write_text("# Long\n\n" + "word " * 1400, encoding="utf-8")
    23	    return root
    24	
    25	
    26	def test_walk_filters_and_is_deterministic(tmp_path: Path) -> None:
    27	    root = _copy_fixture(tmp_path)
    28	    first_errors: list[str] = []
    29	    second_errors: list[str] = []
    30	    first = list(walk_repo(root, errors=first_errors))
    31	    second = list(walk_repo(root, errors=second_errors))
    32	
    33	    assert first == second
    34	    assert first_errors == second_errors == []
    35	    paths = [path for path, _ in first]
    36	    assert paths == sorted(paths)
    37	    assert "config.yml" in paths
    38	    assert "Dockerfile" in paths
    39	    assert "binary.py" not in paths
    40	    assert "node_modules/ignored.js" not in paths
    41	
    42	
    43	def test_include_prefixes_keep_root_relative_paths(tmp_path: Path) -> None:
    44	    root = _copy_fixture(tmp_path)
    45	    errors: list[str] = []
    46	    paths = [path for path, _ in walk_repo(root, include_prefixes=("app/",), errors=errors)]
    47	    assert paths == ["app/example.php", "app/example.py", "app/example.ts"]
    48	    assert errors == []
    49	
    50	
    51	def test_missing_root_raises(tmp_path: Path) -> None:
    52	    with pytest.raises(ValueError):
    53	        list(walk_repo(tmp_path / "missing", errors=[]))
    54	
    55	
    56	def test_python_chunks_and_lines() -> None:
    57	    path = FIXTURE / "app" / "example.py"
    58	    result = chunk_file("mini", "app/example.py", path.read_bytes())
    59	    by_name = {chunk.qualified_name: chunk for chunk in result.chunks}
    60	
    61	    assert set(by_name) == {"app/example.py", "alpha", "beta", "Worker", "Worker.run", "Worker.stop"}
    62	    assert by_name["alpha"].kind == "function"
    63	    assert (by_name["alpha"].start_line, by_name["alpha"].end_line) == (6, 7)
    64	    assert (by_name["Worker.run"].start_line, by_name["Worker.run"].end_line) == (17, 18)
    65	    assert by_name["app/example.py"].kind == "module"
    66	    assert by_name["app/example.py"].start_line == 1
    67	    assert by_name["app/example.py"].end_line == 3
    68	    assert result.warnings == []
    69	
    70	
    71	def test_typescript_and_php_chunks() -> None:
    72	    ts = chunk_file("mini", "app/example.ts", (FIXTURE / "app" / "example.ts").read_bytes())
    73	    php = chunk_file("mini", "app/example.php", (FIXTURE / "app" / "example.php").read_bytes())
    74	
    75	    assert {chunk.qualified_name for chunk in ts.chunks} == {"greet", "Greeter", "Greeter.greet"}
    76	    assert {chunk.qualified_name for chunk in php.chunks} == {"app/example.php", "Greeter", "Greeter.greet"}
    77	    ts_method = next(chunk for chunk in ts.chunks if chunk.qualified_name == "Greeter.greet")
    78	    php_method = next(chunk for chunk in php.chunks if chunk.qualified_name == "Greeter.greet")
    79	    assert (ts_method.start_line, ts_method.end_line) == (6, 8)
    80	    assert (php_method.start_line, php_method.end_line) == (4, 6)
    81	
    82	
    83	def test_markdown_sections_and_file_chunks() -> None:
    84	    markdown = chunk_file("mini", "docs/guide.md", (FIXTURE / "docs" / "guide.md").read_bytes())
    85	    assert [chunk.qualified_name for chunk in markdown.chunks] == [
    86	        "docs/guide.md",
    87	        "Guide",
    88	        "Guide > Install",
    89	        "Guide > Install > Options",
    90	    ]
    91	    assert [(chunk.start_line, chunk.end_line) for chunk in markdown.chunks] == [
    92	        (1, 1),
    93	        (3, 5),
    94	        (7, 9),
    95	        (11, 13),
    96	    ]
    97	
    98	    yaml = chunk_file("mini", "config.yml", (FIXTURE / "config.yml").read_bytes())
    99	    docker = chunk_file("mini", "Dockerfile", (FIXTURE / "Dockerfile").read_bytes())
   100	    assert len(yaml.chunks) == len(docker.chunks) == 1
   101	    assert yaml.chunks[0].kind == docker.chunks[0].kind == "file"
   102	
   103	
   104	def test_all_embedded_text_is_path_prefixed_and_hashed(tmp_path: Path) -> None:
   105	    result = chunk_repo("mini", _copy_fixture(tmp_path))
   106	    assert result.chunks
   107	    for chunk in result.chunks:
   108	        assert chunk.embedded_text.startswith(chunk.path + "\n\n")
   109	        assert len(chunk.content_sha) == 64
   110	
   111	
   112	def test_oversize_single_line_and_markdown_split(tmp_path: Path) -> None:
   113	    root = _copy_fixture(tmp_path)
   114	    single = chunk_file("mini", "long.txt", (root / "long.txt").read_bytes()).chunks
   115	    markdown = chunk_file("mini", "docs/long.md", (root / "docs" / "long.md").read_bytes()).chunks
   116	
   117	    assert len(single) >= 2
   118	    assert [chunk.qualified_name for chunk in single][:2] == ["long.txt", "long.txt#2"]
   119	    assert len(single[0].text) == 6000
   120	    assert single[0].text[-150:] == single[1].text[:150]
   121	    assert len(markdown) >= 2
   122	    assert [chunk.qualified_name for chunk in markdown][:2] == ["Long", "Long#2"]
   123	    assert all(len(chunk.text) <= 6000 for chunk in single + markdown)
   124	    assert all(chunk.start_line <= chunk.end_line for chunk in single + markdown)
   125	
   126	
   127	def test_broken_parse_falls_back_with_warning() -> None:
   128	    result = chunk_file("mini", "broken.py", (FIXTURE / "broken.py").read_bytes())
   129	    assert len(result.chunks) == 1
   130	    assert result.chunks[0].kind == "file"
   131	    assert result.chunks[0].qualified_name == "broken.py"
   132	    assert len(result.warnings) == 1
   133	    assert "broken.py" in result.warnings[0]
   134	
   135	
   136	def test_scandir_error_is_recorded_after_other_yields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
   137	    root = tmp_path / "repo"
   138	    root.mkdir()
   139	    (root / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
   140	    blocked = root / "blocked"
   141	    blocked.mkdir()
   142	    (blocked / "hidden.py").write_text("VALUE = 2\n", encoding="utf-8")
   143	    (root / "node_modules").mkdir()
   144	    (root / "node_modules" / "ignored.py").write_text("VALUE = 3\n", encoding="utf-8")
   145	    (root / "binary.py").write_bytes(b"ok\0binary")
   146	
   147	    real_scandir = os.scandir
   148	
   149	    def guarded_scandir(path: str | os.PathLike[str]):
   150	        if Path(path) == blocked:
   151	            raise PermissionError("blocked for test")
   152	        return real_scandir(path)
   153	
   154	    monkeypatch.setattr(os, "scandir", guarded_scandir)
   155	    errors: list[str] = []
   156	    iterator = walk_repo(root, errors=errors)
   157	    assert next(iterator)[0] == "a.py"
   158	    assert list(iterator) == []
   159	    assert len(errors) == 1
   160	    assert "blocked" in errors[0]
   161	
   162	
   163	def test_chunk_repo_is_deterministic(tmp_path: Path) -> None:
   164	    root = _copy_fixture(tmp_path)
   165	    assert chunk_repo("mini", root) == chunk_repo("mini", root)
FILE tests/test_store.py
     1	"""Contract tests for the SQLite index writer and embedding adapter."""
     2	
     3	from __future__ import annotations
     4	
     5	import os
     6	import shutil
     7	from pathlib import Path
     8	
     9	import numpy as np
    10	import pytest
    11	
    12	from tests.fakes import FakeEmbedder
    13	from xyz.index.embed import QUERY_PREFIX, CodeRankEmbedder
    14	from xyz.index.store import EmptyCorpus, IndexMismatch, Store, WalkIncomplete
    15	
    16	
    17	FIXTURE = Path(__file__).parent / "fixtures" / "mini-repo"
    18	
    19	
    20	def _copy_fixture(tmp_path: Path) -> Path:
    21	    root = tmp_path / "mini-repo"
    22	    shutil.copytree(FIXTURE, root)
    23	    python = root / "app" / "example.py"
    24	    python.write_text(python.read_text(encoding="utf-8") + "\n# OLDTOKEN\n", encoding="utf-8")
    25	    guide = root / "docs" / "guide.md"
    26	    guide.write_text(guide.read_text(encoding="utf-8") + "\nDELETEONLYTOKEN\n", encoding="utf-8")
    27	    return root
    28	
    29	
    30	def test_first_ingest_indexes_fts_and_vectors(tmp_path: Path) -> None:
    31	    embedder = FakeEmbedder()
    32	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
    33	        report = store.ingest("mini", _copy_fixture(tmp_path))
    34	        stats = store.stats()
    35	        assert report.chunks_embedded == report.chunks_written > 0
    36	        assert stats.chunks == stats.chunks_fts == stats.chunks_vec
    37	        assert store.fts_match("OLDTOKEN")
    38	
    39	
    40	def test_second_ingest_is_a_true_file_sha_short_circuit(tmp_path: Path) -> None:
    41	    root = _copy_fixture(tmp_path)
    42	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
    43	        store.ingest("mini", root)
    44	        embedder = FakeEmbedder()
    45	        store.embedder = embedder
    46	        report = store.ingest("mini", root)
    47	        assert report.files_skipped == report.files_seen
    48	        assert report.files_reingested == 0
    49	        assert report.chunks_written == 0
    50	        assert embedder.call_count == 0
    51	        assert report.seconds < 1.0
    52	
    53	
    54	def test_changed_file_reuses_unchanged_chunk_vectors_and_refreshes_fts(tmp_path: Path) -> None:
    55	    root = _copy_fixture(tmp_path)
    56	    embedder = FakeEmbedder()
    57	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
    58	        store.ingest("mini", root)
    59	        source = root / "app" / "example.py"
    60	        source.write_text(
    61	            source.read_text(encoding="utf-8").replace("OLDTOKEN", "NEWTOKEN"),
    62	            encoding="utf-8",
    63	        )
    64	        embedder.document_calls = embedder.documents_encoded = 0
    65	        report = store.ingest("mini", root)
    66	        assert report.files_reingested == 1
    67	        assert report.cache_hits > 0
    68	        assert embedder.document_calls == 1
    69	        assert embedder.documents_encoded == 1
    70	        assert store.fts_match("NEWTOKEN")
    71	        assert store.fts_match("OLDTOKEN") == []
    72	
    73	
    74	def test_deleted_file_is_pruned_from_all_indexes(tmp_path: Path) -> None:
    75	    root = _copy_fixture(tmp_path)
    76	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
    77	        store.ingest("mini", root)
    78	        before = store.stats()
    79	        (root / "docs" / "guide.md").unlink()
    80	        report = store.ingest("mini", root)
    81	        after = store.stats()
    82	        assert report.files_pruned == 1
    83	        assert after.files == before.files - 1
    84	        assert after.chunks == after.chunks_fts == after.chunks_vec
    85	        assert after.chunks < before.chunks
    86	        assert store.fts_match("DELETEONLYTOKEN") == []
    87	
    88	
    89	def test_prefix_scoped_ingest_does_not_prune_outside_scope(tmp_path: Path) -> None:
    90	    root = _copy_fixture(tmp_path)
    91	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
    92	        store.ingest("mini", root)
    93	        (root / "docs" / "guide.md").unlink()
    94	        report = store.ingest("mini", root, include_prefixes=("app",))
    95	        assert report.files_pruned == 0
    96	        assert store.fts_match("DELETEONLYTOKEN")
    97	
    98	
    99	def test_empty_corpus_does_not_write(tmp_path: Path) -> None:
   100	    root = tmp_path / "empty"
   101	    root.mkdir()
   102	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
   103	        with pytest.raises(EmptyCorpus):
   104	            store.ingest("mini", root)
   105	        assert store.stats().files == store.stats().chunks == 0
   106	
   107	
   108	def test_incomplete_walk_preserves_every_existing_index(
   109	    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
   110	) -> None:
   111	    root = _copy_fixture(tmp_path)
   112	    blocked = root / "docs"
   113	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
   114	        store.ingest("mini", root)
   115	        before = store.stats()
   116	        token_ids = store.fts_match("DELETEONLYTOKEN")
   117	        real_scandir = os.scandir
   118	
   119	        def guarded_scandir(path: str | os.PathLike[str]):
   120	            if Path(path) == blocked:
   121	                raise PermissionError("blocked for test")
   122	            return real_scandir(path)
   123	
   124	        monkeypatch.setattr(os, "scandir", guarded_scandir)
   125	        with pytest.raises(WalkIncomplete, match="docs"):
   126	            store.ingest("mini", root)
   127	        assert store.stats() == before
   128	        assert store.fts_match("DELETEONLYTOKEN") == token_ids
   129	
   130	
   131	@pytest.mark.parametrize(
   132	    ("changed", "value"),
   133	    (("model_id", "other"), ("dim", 12), ("provider", "other-provider")),
   134	)
   135	def test_open_rejects_each_embedder_identity_mismatch(
   136	    tmp_path: Path, changed: str, value: object
   137	) -> None:
   138	    path = tmp_path / "index.sqlite"
   139	    Store.open(path, FakeEmbedder()).close()
   140	    kwargs = {"model_id": "fake", "dim": 8, "provider": "fake"}
   141	    kwargs[changed] = value
   142	    with pytest.raises(IndexMismatch, match={"model_id": "model"}.get(changed, changed)):
   143	        Store.open(path, FakeEmbedder(**kwargs))
   144	
   145	
   146	def test_chunk_vector_matches_provider_keyed_cache(tmp_path: Path) -> None:
   147	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
   148	        store.ingest("mini", _copy_fixture(tmp_path))
   149	        chunk_vector, cache_vector = store.connection.execute(
   150	            """
   151	            SELECT v.embedding, c.vector
   152	            FROM chunks AS ch
   153	            JOIN chunks_vec AS v ON v.rowid = ch.id
   154	            JOIN embed_cache AS c
   155	              ON c.content_sha = ch.content_sha
   156	             AND c.model = ? AND c.dim = ? AND c.provider = ?
   157	            LIMIT 1
   158	            """,
   159	            ("fake", 8, "fake"),
   160	        ).fetchone()
   161	        assert np.array_equal(
   162	            np.frombuffer(chunk_vector, dtype=np.float32),
   163	            np.frombuffer(cache_vector, dtype=np.float32),
   164	        )
   165	
   166	
   167	def test_coderank_embedder_sets_guard_and_prefixes_queries_only(
   168	    monkeypatch: pytest.MonkeyPatch,
   169	) -> None:
   170	    calls: list[list[str]] = []
   171	
   172	    class StubModel:
   173	        max_seq_length = 99
   174	
   175	        def encode(self, texts: list[str], **_kwargs: object) -> np.ndarray:
   176	            calls.append(texts)
   177	            vectors = np.zeros((len(texts), 768), dtype=np.float32)
   178	            vectors[:, 0] = 1.0
   179	            return vectors
   180	
   181	    model = StubModel()
   182	    monkeypatch.setenv("EMBED_MAX_THREADS", "1")
   183	    embedder = CodeRankEmbedder(model_factory=lambda *_args, **_kwargs: model, device="cpu")
   184	    embedder.encode_documents(["raw document"])
   185	    query = embedder.encode_query("sort a list")
   186	    assert model.max_seq_length == 2048
   187	    assert calls == [["raw document"], [QUERY_PREFIX + "sort a list"]]
   188	    assert query.shape == (768,)
   189	    assert np.linalg.norm(query) == pytest.approx(1.0)
FILE tests/test_retrieve.py
     1	"""Contract tests for hybrid retrieval and its score semantics."""
     2	
     3	from __future__ import annotations
     4	
     5	from pathlib import Path
     6	
     7	import pytest
     8	import sqlite_vec
     9	
    10	from tests.fakes import FakeEmbedder, FakeReranker
    11	from xyz.index.store import IndexMismatch, Store
    12	from xyz.retrieve.dense import KNN_SQL, dense_search
    13	from xyz.retrieve.fuse import rrf
    14	from xyz.retrieve.latency import LatencyLog
    15	from xyz.retrieve.lexical import bm25_search
    16	from xyz.retrieve.models import Hit
    17	from xyz.retrieve.pipeline import Retriever
    18	
    19	
    20	def _add_chunks(store: Store, count: int, *, same_path: bool = False) -> None:
    21	    vector = sqlite_vec.serialize_float32([1.0] + [0.0] * (store.embedder.dim - 1))
    22	    with store.connection:
    23	        for chunk_id in range(1, count + 1):
    24	            path = "same.py" if same_path else f"p{chunk_id}.py"
    25	            store.connection.execute(
    26	                """
    27	                INSERT INTO chunks(
    28	                    id, repo, path, kind, qualified_name, start_line, end_line,
    29	                    content_sha, text, embedded_text
    30	                ) VALUES (?, 'repo', ?, 'function', ?, 1, 1, ?, ?, ?)
    31	                """,
    32	                (chunk_id, path, f"f{chunk_id}", f"sha{chunk_id}", f"text {chunk_id}", f"embedded {chunk_id}"),
    33	            )
    34	            store.connection.execute(
    35	                "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)", (chunk_id, vector)
    36	            )
    37	
    38	
    39	def test_rrf_matches_hand_computed_overlap_and_tie_break() -> None:
    40	    left = [Hit(1, 9, "a"), Hit(2, 8, "a"), Hit(3, 7, "a")]
    41	    right = [Hit(3, 9, "b"), Hit(4, 8, "b"), Hit(5, 7, "b")]
    42	    fused = rrf([left, right], k=60)
    43	    assert [hit.chunk_id for hit in fused] == [3, 1, 2, 4, 5]
    44	    assert fused[0].score == pytest.approx(1 / 63 + 1 / 61)
    45	    assert fused[1].score == pytest.approx(1 / 61)
    46	    assert fused[2].score == pytest.approx(1 / 62)
    47	
    48	
    49	def test_knn_sql_uses_bound_k_and_dense_query_executes(tmp_path: Path) -> None:
    50	    assert " k = ?" in KNN_SQL
    51	    assert "LIMIT ?" not in KNN_SQL.upper()
    52	    embedder = FakeEmbedder()
    53	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
    54	        _add_chunks(store, 2)
    55	        assert len(dense_search(store, embedder.encode_query("needle"), 1)) == 1
    56	
    57	
    58	def test_bm25_sanitises_operators_empty_and_keeps_higher_better(tmp_path: Path) -> None:
    59	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
    60	        _add_chunks(store, 2)
    61	        with store.connection:
    62	            store.connection.execute(
    63	                "UPDATE chunks SET embedded_text = 'foo bar foo' WHERE id = 1"
    64	            )
    65	            store.connection.execute(
    66	                "UPDATE chunks SET embedded_text = 'foo' WHERE id = 2"
    67	            )
    68	        assert bm25_search(store, "foo-bar: baz*", 10)
    69	        assert bm25_search(store, "", 10) == []
    70	        assert bm25_search(store, "the and", 10) == []
    71	        hits = bm25_search(store, "foo bar", 10)
    72	        assert hits[0].chunk_id == 1
    73	        assert hits[0].score > hits[1].score
    74	
    75	
    76	def test_rerank_reorders_rrf_and_tau_is_query_level(
    77	    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    78	) -> None:
    79	    import xyz.retrieve.pipeline as pipeline
    80	
    81	    embedder = FakeEmbedder()
    82	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
    83	        _add_chunks(store, 3)
    84	        lane = [Hit(1, 3, "lane"), Hit(2, 2, "lane"), Hit(3, 1, "lane")]
    85	        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
    86	        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
    87	        reranker = FakeReranker({"embedded 1": 2.0, "embedded 2": 0.0, "embedded 3": 3.0})
    88	        retriever = Retriever(store, embedder, reranker)
    89	
    90	        assert retriever.search("q", mode="hybrid").ranking[0][0] == 1
    91	        reranked = retriever.search("q", k=3, mode="hybrid+rerank", tau=1.0)
    92	        assert [chunk_id for chunk_id, _path in reranked.ranking] == [3, 1, 2]
    93	        assert not reranked.no_answer
    94	        assert len(reranked.hits) == 3
    95	        assert reranked.hits[-1].score < 1.0
    96	
    97	        rejected = Retriever(
    98	            store, embedder, FakeReranker({"embedded 1": 0.2, "embedded 2": 0.1, "embedded 3": 0.0})
    99	        ).search("q", mode="hybrid+rerank", tau=0.5)
   100	        assert rejected.no_answer and rejected.hits == [] and rejected.ranking
   101	
   102	
   103	def test_candidate_depth_rerank_cap_and_same_path_identity(
   104	    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
   105	) -> None:
   106	    import xyz.retrieve.pipeline as pipeline
   107	
   108	    embedder = FakeEmbedder()
   109	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
   110	        _add_chunks(store, 120, same_path=True)
   111	        lane = [Hit(chunk_id, 121 - chunk_id, "lane") for chunk_id in range(1, 121)]
   112	        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
   113	        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
   114	        scores = {f"embedded {chunk_id}": float(51 - chunk_id) for chunk_id in range(1, 51)}
   115	        scores["embedded 1"], scores["embedded 2"] = scores["embedded 2"], scores["embedded 1"]
   116	        retriever = Retriever(store, embedder, FakeReranker(scores))
   117	        hybrid = retriever.search("q", fetch_k=100, mode="hybrid")
   118	        reranked = retriever.search("q", fetch_k=100, mode="hybrid+rerank")
   119	        assert len(reranked.ranking) == 100
   120	        assert reranked.ranking[74][0] == 75
   121	        assert 75 not in {chunk_id for chunk_id, _path in retriever.search(
   122	            "q", fetch_k=50, mode="hybrid+rerank"
   123	        ).ranking}
   124	        assert hybrid.ranking != reranked.ranking
   125	        assert [path for _chunk_id, path in hybrid.ranking] == [
   126	            path for _chunk_id, path in reranked.ranking
   127	        ]
   128	
   129	
   130	@pytest.mark.parametrize(
   131	    "kwargs",
   132	    ({"model_id": "other"}, {"dim": 9}, {"provider": "other"}),
   133	)
   134	def test_retriever_rejects_embedder_identity_mismatch(tmp_path: Path, kwargs: dict[str, object]) -> None:
   135	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
   136	        with pytest.raises(IndexMismatch):
   137	            Retriever(store, FakeEmbedder(**kwargs))
   138	
   139	
   140	def test_auto_modes_errors_timings_and_latency_summary(
   141	    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
   142	) -> None:
   143	    import xyz.retrieve.pipeline as pipeline
   144	
   145	    embedder = FakeEmbedder()
   146	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
   147	        _add_chunks(store, 1)
   148	        lane = [Hit(1, 1.0, "lane")]
   149	        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
   150	        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
   151	        plain = Retriever(store, embedder)
   152	        assert plain.search("q", mode="auto").mode == "hybrid"
   153	        with pytest.raises(ValueError, match="requires"):
   154	            plain.search("q", mode="hybrid+rerank")
   155	        assert not plain.search("q", mode="dense", tau=None).no_answer
   156	        assert plain.search("q", mode="bm25", tau=2.0).no_answer
   157	
   158	        reranked = Retriever(store, embedder, FakeReranker({"embedded 1": 1.0}))
   159	        log = LatencyLog()
   160	        for _ in range(3):
   161	            result = reranked.search("q", mode="auto")
   162	            assert result.mode == "hybrid+rerank"
   163	            assert set(result.timings) == {
   164	                "embed_query", "bm25", "dense", "fuse", "rerank", "total"
   165	            }
   166	            assert all(value >= 0 for value in result.timings.values())
   167	            log.add(result.timings)
   168	        summary = log.summary()
   169	        assert all(set(summary[stage]) == {"p50", "p95"} for stage in result.timings)
FILE tests/test_metrics.py
     1	from __future__ import annotations
     2	
     3	import json
     4	
     5	import pytest
     6	
     7	from xyz.eval.metrics import score
     8	
     9	
    10	def test_score_three_queries() -> None:
    11	    queries = [
    12	        {"q": "one", "relevant": ["a.py"]},
    13	        {"q": "two", "relevant": ["b.py"]},
    14	        {"q": "miss", "relevant": ["z.py"]},
    15	    ]
    16	    report = score(
    17	        {
    18	            "one": [(1, "a.py"), (2, "x.py")],
    19	            "two": [(3, "x.py"), (4, "b.py")],
    20	            "miss": [(5, "x.py")],
    21	        },
    22	        queries,
    23	        10,
    24	    ).to_dict()
    25	    assert report["mrr"] == 0.5
    26	    assert report["recall@1"] == pytest.approx(1 / 3, abs=0.0001)
    27	    assert report["recall@3"] == pytest.approx(2 / 3, abs=0.0001)
    28	    assert report["never_found"] == 1
    29	
    30	
    31	def test_rank_eleven_flips_at_depth() -> None:
    32	    queries = [{"q": "q", "relevant": ["hit.py"]}]
    33	    ranking = [(i, f"p{i}.py") for i in range(1, 11)] + [(11, "hit.py")]
    34	    shallow = score({"q": ranking}, queries, 10)
    35	    deep = score({"q": ranking}, queries, 100)
    36	    assert shallow.mrr == 0 and shallow.never_found == 1
    37	    assert deep.mrr == pytest.approx(1 / 11, abs=0.0001) and deep.never_found == 0
    38	
    39	
    40	def test_same_path_chunk_ids_survive_json_round_trip(tmp_path) -> None:
    41	    report = score(
    42	        {"q": [(41, "same.py"), (42, "same.py")]},
    43	        [{"q": "q", "relevant": ["same.py"]}],
    44	        10,
    45	    )
    46	    path = tmp_path / "report.json"
    47	    report.write_json(path)
    48	    ranking = json.loads(path.read_text())["per_query"][0]["ranking"]
    49	    assert ranking == [
    50	        {"chunk_id": 41, "path": "same.py"},
    51	        {"chunk_id": 42, "path": "same.py"},
    52	    ]
FILE tests/test_cli.py
     1	from __future__ import annotations
     2	
     3	import json
     4	from pathlib import Path
     5	
     6	import pytest
     7	
     8	from tests.fakes import FakeEmbedder, FakeReranker
     9	from xyz.cli import main
    10	
    11	
    12	@pytest.fixture
    13	def fake_models(monkeypatch: pytest.MonkeyPatch) -> None:
    14	    import xyz.cli as cli
    15	
    16	    monkeypatch.setattr(cli, "_make_embedder", FakeEmbedder)
    17	    monkeypatch.setattr(cli, "_make_reranker", lambda: FakeReranker(default=0.0))
    18	
    19	
    20	def _repo(tmp_path: Path) -> Path:
    21	    root = tmp_path / "repo"
    22	    root.mkdir()
    23	    (root / "alpha.py").write_text(
    24	        "def alpha():\n    return 'alpha'\n\n"
    25	        "def alpha_helper():\n    return 'helper'\n"
    26	    )
    27	    (root / "beta.py").write_text("def beta():\n    return 'beta'\n")
    28	    return root
    29	
    30	
    31	def test_ingest_query_eval_end_to_end_and_dedupe(
    32	    tmp_path: Path, fake_models: None, capsys: pytest.CaptureFixture[str]
    33	) -> None:
    34	    root = _repo(tmp_path)
    35	    db = tmp_path / "index.sqlite"
    36	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    37	    first = json.loads(capsys.readouterr().out)
    38	    assert first["ingest"]["chunks_embedded"] > 0
    39	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    40	    second = json.loads(capsys.readouterr().out)
    41	    assert second["ingest"]["chunks_embedded"] == 0
    42	
    43	    assert main(["query", "--db", str(db), "--mode", "dense", "alpha"]) == 0
    44	    assert "timings_ms" in capsys.readouterr().out
    45	
    46	    queries = tmp_path / "queries.json"
    47	    queries.write_text(json.dumps({"queries": [{"q": "alpha", "relevant": ["alpha.py"]}]}))
    48	    out = tmp_path / "eval.json"
    49	    assert main(
    50	        [
    51	            "eval", "--db", str(db), "--queries", str(queries),
    52	            "--modes", "dense,bm25,hybrid,hybrid+rerank",
    53	            "--depth", "100", "--out", str(out),
    54	        ]
    55	    ) == 0
    56	    payload = json.loads(out.read_text())
    57	    assert set(payload["reports"]) == {"dense", "bm25", "hybrid", "hybrid+rerank"}
    58	    assert payload["corpus"]["chunk_count"] > 0
    59	    assert "reorder_count" in payload
    60	
    61	
    62	def test_eval_counts_chunk_id_reorder(
    63	    tmp_path: Path, fake_models: None, monkeypatch: pytest.MonkeyPatch
    64	) -> None:
    65	    import xyz.retrieve.pipeline as pipeline
    66	    from xyz.retrieve.models import Hit
    67	
    68	    root = _repo(tmp_path)
    69	    db = tmp_path / "index.sqlite"
    70	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    71	    # Chunk ids 1 and 2 are distinct functions from the same alpha.py path.
    72	    monkeypatch.setattr(
    73	        pipeline,
    74	        "dense_search",
    75	        lambda *_args: [Hit(1, 2.0, "dense"), Hit(2, 1.0, "dense")],
    76	    )
    77	    monkeypatch.setattr(
    78	        pipeline,
    79	        "bm25_search",
    80	        lambda *_args: [Hit(1, 2.0, "bm25"), Hit(2, 1.0, "bm25")],
    81	    )
    82	    import xyz.cli as cli
    83	
    84	    class SwapReranker:
    85	        def score(self, query: str, texts: list[str]) -> list[float]:
    86	            del query
    87	            return [float(index) for index, _text in enumerate(texts)]
    88	
    89	    monkeypatch.setattr(cli, "_make_reranker", SwapReranker)
    90	    queries = tmp_path / "queries.json"
    91	    queries.write_text(json.dumps([{"q": "alpha", "relevant": ["alpha.py"]}]))
    92	    out = tmp_path / "eval.json"
    93	    assert main(
    94	        [
    95	            "eval", "--db", str(db), "--queries", str(queries),
    96	            "--modes", "hybrid,hybrid+rerank", "--out", str(out),
    97	        ]
    98	    ) == 0
    99	    assert json.loads(out.read_text())["reorder_count"] == 1
   100	
   101	
   102	@pytest.mark.parametrize("payload", ([], {"queries": []}))
   103	def test_empty_query_file_exits_two(
   104	    tmp_path: Path, fake_models: None, payload: object
   105	) -> None:
   106	    path = tmp_path / "queries.json"
   107	    path.write_text(json.dumps(payload))
   108	    assert main(
   109	        [
   110	            "eval", "--db", str(tmp_path / "x.sqlite"), "--queries", str(path),
   111	            "--out", str(tmp_path / "out.json"),
   112	        ]
   113	    ) == 2
   114	
   115	
   116	def test_missing_gold_path_exits_two(tmp_path: Path, fake_models: None) -> None:
   117	    root = _repo(tmp_path)
   118	    db = tmp_path / "index.sqlite"
   119	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
   120	    queries = tmp_path / "queries.json"
   121	    queries.write_text(json.dumps([{"q": "missing", "relevant": ["absent.py"]}]))
   122	    assert main(
   123	        [
   124	            "eval", "--db", str(db), "--queries", str(queries),
   125	            "--out", str(tmp_path / "out.json"),
   126	        ]
   127	    ) == 2
   128	
   129	
   130	def test_bogus_ingest_path_exits_two(tmp_path: Path, fake_models: None) -> None:
   131	    assert main(
   132	        [
   133	            "ingest", "--db", str(tmp_path / "x.sqlite"), "--repo", "fixture",
   134	            str(tmp_path / "missing"),
   135	        ]
   136	    ) == 2
FILE tests/test_smoke.py
     1	"""Smoke tests for the initial package scaffold."""
     2	
     3	import xyz
     4	from xyz.cli import main
     5	
     6	
     7	def test_version() -> None:
     8	    assert xyz.__version__ == "0.5.0.dev0"
     9	
    10	
    11	def test_cli_without_arguments(capsys: object) -> None:
    12	    assert main([]) == 0
    13	
    14	
    15	def test_cli_version(capsys: object) -> None:
    16	    assert main(["--version"]) == 0
    17	
    18	
    19	def test_cli_unknown_subcommand(capsys: object) -> None:
    20	    assert main(["bogus"]) == 2
FILE tests/fakes.py
     1	"""Deterministic test doubles shared by index and retrieval tests."""
     2	
     3	from __future__ import annotations
     4	
     5	import hashlib
     6	from collections.abc import Sequence
     7	
     8	import numpy as np
     9	
    10	
    11	class FakeEmbedder:
    12	    provider = "fake"
    13	
    14	    def __init__(self, model_id: str = "fake", dim: int = 8, provider: str = "fake") -> None:
    15	        self.model_id = model_id
    16	        self.dim = dim
    17	        self.provider = provider
    18	        self.document_calls = 0
    19	        self.query_calls = 0
    20	        self.documents_encoded = 0
    21	
    22	    @property
    23	    def call_count(self) -> int:
    24	        return self.document_calls + self.query_calls
    25	
    26	    def _vector(self, text: str) -> np.ndarray:
    27	        values: list[float] = []
    28	        counter = 0
    29	        while len(values) < self.dim:
    30	            digest = hashlib.sha256(f"{counter}:{text}".encode()).digest()
    31	            values.extend((byte - 127.5) / 127.5 for byte in digest)
    32	            counter += 1
    33	        vector = np.asarray(values[: self.dim], dtype=np.float32)
    34	        return vector / np.linalg.norm(vector)
    35	
    36	    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
    37	        self.document_calls += 1
    38	        self.documents_encoded += len(texts)
    39	        return np.stack([self._vector(text) for text in texts]).astype(np.float32)
    40	
    41	    def encode_query(self, text: str) -> np.ndarray:
    42	        self.query_calls += 1
    43	        return self._vector(text)
    44	
    45	
    46	class FakeReranker:
    47	    """Return deterministic scores keyed by exact chunk text."""
    48	
    49	    def __init__(self, scores: dict[str, float] | None = None, default: float = 0.0) -> None:
    50	        self.scores = scores or {}
    51	        self.default = default
    52	
    53	    def score(self, query: str, texts: Sequence[str]) -> list[float]:
    54	        del query
    55	        return [float(self.scores.get(text, self.default)) for text in texts]

exec
/bin/zsh -lc 'for f in pyproject.toml xyz/index/__init__.py xyz/ingest/__init__.py xyz/retrieve/__init__.py xyz/eval/__init__.py validate.sh prelaunch.sh; do echo "FILE $f"; nl -ba "$f"; done
rg -n --hidden --glob '"'"'!relay-system/**'"' --glob '"'!marathon-system/**'"' --glob '"'!.git/**'"' 'xyz/xyz|xyz\\.xyz|from xyz\\.xyz|import xyz\\.xyz' . || true
find xyz -type d -print | sort
rg -n --glob 'xyz/**' --glob '"'!xyz/index/store.py'"' '(INSERT|UPDATE|DELETE|CREATE (TABLE|VIRTUAL TABLE|TRIGGER)|executescript|connection\\.execute|\\.write_text|sqlite3\\.connect)'" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 0ms:
FILE pyproject.toml
     1	[build-system]
     2	requires = ["setuptools"]
     3	build-backend = "setuptools.build_meta"
     4	
     5	[project]
     6	name = "xyz-code-intelligence"
     7	version = "0.5.0.dev0"
     8	requires-python = ">=3.11"
     9	dependencies = [
    10	    "sentence-transformers==6.0.1",
    11	    "torch==2.14.0",
    12	    "einops==0.8.2",
    13	    "numpy==2.4.6",
    14	    "sqlite-vec==0.1.9",
    15	    "tree-sitter==0.26.0",
    16	    "tree-sitter-language-pack==1.16.1",
    17	]
    18	
    19	[project.optional-dependencies]
    20	dev = ["pytest", "psutil"]
    21	
    22	[project.scripts]
    23	xyz = "xyz.cli:main"
    24	
    25	[tool.setuptools.packages.find]
    26	include = ["xyz*"]
    27	
    28	[tool.pytest.ini_options]
    29	pythonpath = ["."]
    30	testpaths = ["tests"]
FILE xyz/index/__init__.py
     1	"""Code index package."""
     2	
     3	from xyz.index.embed import CodeRankEmbedder, Embedder
     4	from xyz.index.store import (
     5	    EmptyCorpus,
     6	    IndexMismatch,
     7	    IngestReport,
     8	    Store,
     9	    StoreStats,
    10	    WalkIncomplete,
    11	)
    12	
    13	__all__ = [
    14	    "CodeRankEmbedder",
    15	    "Embedder",
    16	    "EmptyCorpus",
    17	    "IndexMismatch",
    18	    "IngestReport",
    19	    "Store",
    20	    "StoreStats",
    21	    "WalkIncomplete",
    22	]
FILE xyz/ingest/__init__.py
     1	"""Repository walking and source chunking."""
     2	
     3	from __future__ import annotations
     4	
     5	import os
     6	from pathlib import Path
     7	from typing import Any
     8	
     9	from xyz.ingest.chunk import Chunk, ChunkResult, chunk_file
    10	from xyz.ingest.walk import DEFAULT_EXCLUDE, DEFAULT_INCLUDE, walk_repo
    11	
    12	
    13	def chunk_repo(
    14	    repo: str,
    15	    root: str | os.PathLike[str],
    16	    **walk_kwargs: Any,
    17	) -> ChunkResult:
    18	    """Walk and chunk a repository, accumulating parse and traversal warnings."""
    19	
    20	    errors = walk_kwargs.pop("errors", None)
    21	    if errors is None:
    22	        errors = []
    23	    chunks: list[Chunk] = []
    24	    warnings: list[str] = []
    25	    for rel_path, source in walk_repo(Path(root), errors=errors, **walk_kwargs):
    26	        result = chunk_file(repo, rel_path, source)
    27	        chunks.extend(result.chunks)
    28	        warnings.extend(result.warnings)
    29	    warnings.extend(f"walk error: {error}" for error in errors)
    30	    return ChunkResult(chunks, warnings)
    31	
    32	
    33	__all__ = [
    34	    "Chunk",
    35	    "ChunkResult",
    36	    "DEFAULT_EXCLUDE",
    37	    "DEFAULT_INCLUDE",
    38	    "chunk_file",
    39	    "chunk_repo",
    40	    "walk_repo",
    41	]
FILE xyz/retrieve/__init__.py
     1	"""Code retrieval package."""
     2	
     3	from xyz.retrieve.models import Hit, SearchHit, SearchResult
     4	from xyz.retrieve.pipeline import Retriever
     5	
     6	__all__ = ["Hit", "Retriever", "SearchHit", "SearchResult"]
FILE xyz/eval/__init__.py
     1	"""Evaluation metrics for XYZ retrieval runs."""
     2	
     3	from xyz.eval.metrics import Report, score
     4	
     5	__all__ = ["Report", "score"]
FILE validate.sh
     1	#!/usr/bin/env bash
     2	# validate.sh — the repo's pre-advance gate (marathon-drive runs `bash validate.sh` before a phase
     3	# is approved). Deterministic only: environment preflight, PDDA hygiene checks (blocking), the
     4	# package's import smoke with an exact version assertion, and the test suite. It is unconditional:
     5	# a clone without pyproject.toml / xyz/ / tests/ FAILS here — phase gh11-p0-scaffold's job is to
     6	# make it green. Extend it as phases land; never weaken a check to make a phase pass.
     7	set -euo pipefail
     8	cd "$(dirname "$0")"
     9	REPO="$PWD"
    10	
    11	# ── Environment contract (set by the operator when launching a marathon; defaults are repo-relative)
    12	export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
    13	export XYZ_PY="${XYZ_PY:-$REPO/.venv/bin/python}"          # interpreter with the pinned deps
    14	export XYZ_SCRATCH="${XYZ_SCRATCH:-$REPO/.relay-scratch}"  # generated evidence (index DBs, eval JSON)
    15	export PYTHONPATH="$REPO${PYTHONPATH:+:$PYTHONPATH}"       # import xyz from the tree; no editable install
    16	EXPECTED_VERSION="0.5.0.dev0"
    17	
    18	echo "== env preflight"
    19	[[ -x "$XYZ_PY" ]] || { echo "validate: XYZ_PY not executable: $XYZ_PY — create the venv per SOP.md or export XYZ_PY" >&2; exit 1; }
    20	# Readiness is proven by prelaunch.sh (operator-run: real offline model loads + parser creation with
    21	# this exact interpreter). Its marker must exist next to the venv and name this interpreter.
    22	MARKER="$(cd "$(dirname "$XYZ_PY")/.." && pwd)/xyz-prelaunch.json"
    23	[[ -f "$MARKER" ]] || { echo "validate: readiness marker missing: $MARKER — run: XYZ_PY=$XYZ_PY bash prelaunch.sh" >&2; exit 1; }
    24	"$XYZ_PY" - "$MARKER" <<'PY'
    25	import importlib, json, os, pathlib, sys
    26	m = json.load(open(sys.argv[1]))
    27	if not m.get("ok"): sys.exit("validate: prelaunch marker records NOT READY — re-run prelaunch.sh")
    28	if m.get("xyz_py") != sys.executable: sys.exit(f"validate: prelaunch marker is for {m.get('xyz_py')}, not {sys.executable}")
    29	# The marker must have validated THIS configuration: the same reranker and the same model cache.
    30	# Cache paths come from the LIBRARIES' resolved constants (huggingface_hub resolves through
    31	# XDG_CACHE_HOME and honours the legacy HUGGINGFACE_HUB_CACHE), never rebuilt from HF_HOME — a
    32	# hand-built path misses both and lets a stale marker vouch for a cache that was never tested.
    33	import huggingface_hub.constants as hc
    34	live = {
    35	    "reranker": os.environ.get("XYZ_RERANKER", "mixedbread-ai/mxbai-rerank-xsmall-v1"),
    36	    "hf_home": str(getattr(hc, "HF_HOME", "")),
    37	    "hf_hub_cache": str(getattr(hc, "HF_HUB_CACHE", "")),
    38	    "hf_assets_cache": str(getattr(hc, "HF_ASSETS_CACHE", "")),
    39	}
    40	try:
    41	    import transformers.utils.hub as th
    42	    live["transformers_cache"] = str(getattr(th, "TRANSFORMERS_CACHE", getattr(th, "HF_MODULES_CACHE", "")))
    43	    live["hf_modules_cache"] = str(getattr(th, "HF_MODULES_CACHE", ""))
    44	except Exception:
    45	    live["transformers_cache"] = live["hf_modules_cache"] = "<unresolved>"
    46	was = m.get("env") or {}
    47	drift = {k: (was.get(k), v) for k, v in live.items() if was.get(k) != v}
    48	if drift:
    49	    sys.exit("validate: environment changed since prelaunch (validated, now): "
    50	             + json.dumps(drift) + " — re-run: XYZ_PY=%s bash prelaunch.sh" % sys.executable)
    51	for mod in ("numpy", "sqlite_vec", "tree_sitter_language_pack", "sentence_transformers", "pytest"):
    52	    importlib.import_module(mod)  # real import, not find_spec
    53	from tree_sitter_language_pack import get_parser
    54	for lang in ("python", "javascript", "typescript", "tsx", "php"):
    55	    get_parser(lang)
    56	import sqlite3, sqlite_vec
    57	c = sqlite3.connect(":memory:"); c.enable_load_extension(True); sqlite_vec.load(c)
    58	assert c.execute("select sqlite_compileoption_used('ENABLE_FTS5')").fetchone()[0] == 1, "FTS5 missing"
    59	print("env ok:", sys.version.split()[0], "prelaunch", m["at"], "sqlite-vec", c.execute("select vec_version()").fetchone()[0])
    60	PY
    61	mkdir -p "$XYZ_SCRATCH"
    62	
    63	echo "== PDDA deterministic checks (PDDA_MODE=full so errors block; the repo's .pdda-mode stays observe)"
    64	export PDDA_MODE=full
    65	for check in frontmatter status-table roadmap roadmap-coverage hardcoded-paths; do
    66	  ./utils/pdda/pdda.sh "$check"
    67	done
    68	
    69	echo "== package presence (unconditional after gh11-p0-scaffold)"
    70	for p in pyproject.toml xyz/__init__.py xyz/__main__.py tests; do
    71	  [[ -e "$p" ]] || { echo "validate: required path missing: $p" >&2; exit 1; }
    72	done
    73	
    74	echo "== import smoke (exact version)"
    75	got="$("$XYZ_PY" -c 'import xyz; print(xyz.__version__)')"
    76	[[ "$got" == "$EXPECTED_VERSION" ]] || { echo "validate: xyz.__version__ = '$got', expected '$EXPECTED_VERSION'" >&2; exit 1; }
    77	"$XYZ_PY" -m xyz --version >/dev/null
    78	
    79	echo "== pytest"
    80	"$XYZ_PY" -m pytest -q tests
    81	
    82	echo "validate: OK"
FILE prelaunch.sh
     1	#!/usr/bin/env bash
     2	# prelaunch.sh — OPERATOR readiness control, run once before firing the GH-11 marathon (and again
     3	# after any venv/cache change). Unlike validate.sh (the per-phase gate), this actually LOADS both
     4	# models offline with their real classes and instantiates every Tree-sitter parser the chunker
     5	# needs, using the exact interpreter builder turns will use. It writes a marker next to that
     6	# interpreter (`<venv>/xyz-prelaunch.json`) which validate.sh requires — so a builder turn cannot
     7	# start on a tree whose readiness was never proven. Evidence is printed and copied to $XYZ_SCRATCH.
     8	#
     9	# Usage: XYZ_PY=/path/to/.venv/bin/python bash prelaunch.sh
    10	# Exit: 0 ready · 1 not ready (message names the first failing component).
    11	set -euo pipefail
    12	cd "$(dirname "$0")"
    13	REPO="$PWD"
    14	export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONUNBUFFERED=1
    15	export XYZ_PY="${XYZ_PY:-$REPO/.venv/bin/python}"
    16	export XYZ_SCRATCH="${XYZ_SCRATCH:-$REPO/.relay-scratch}"
    17	[[ -x "$XYZ_PY" ]] || { echo "prelaunch: XYZ_PY not executable: $XYZ_PY" >&2; exit 1; }
    18	mkdir -p "$XYZ_SCRATCH"
    19	MARKER="$(cd "$(dirname "$XYZ_PY")/.." && pwd)/xyz-prelaunch.json"
    20	
    21	# INVALIDATE FIRST (GH-11 plan review r3): a readiness attempt must never be able to fall back on a
    22	# previous success. The marker is removed before anything is tested and only re-published — atomically,
    23	# via a temp file + os.replace — when every check passes. So a failed or interrupted run leaves NO
    24	# marker, and validate.sh fails until a real success re-publishes one.
    25	rm -f "$MARKER"
    26	
    27	"$XYZ_PY" - "$MARKER" "$XYZ_SCRATCH/prelaunch.json" <<'PY'
    28	import hashlib, importlib, json, os, pathlib, sys, time
    29	marker, evidence = sys.argv[1], sys.argv[2]
    30	RERANKER = os.environ.get("XYZ_RERANKER", "mixedbread-ai/mxbai-rerank-xsmall-v1")
    31	
    32	def env_fingerprint():
    33	    """What this readiness run actually validated. validate.sh compares it to the live env, so a
    34	    changed reranker or model cache invalidates readiness instead of silently reusing it.
    35	
    36	    The cache paths are read from the LIBRARIES' OWN resolved constants, not reconstructed from
    37	    HF_HOME. huggingface_hub resolves its default through XDG_CACHE_HOME and accepts the legacy
    38	    HUGGINGFACE_HUB_CACHE, so a hand-built path misses both and would let readiness survive a real
    39	    cache change (GH-11 plan review r4). Same function is used by validate.sh — one definition."""
    40	    import huggingface_hub.constants as hc
    41	    fp = {
    42	        "reranker": RERANKER,
    43	        "hf_home": str(getattr(hc, "HF_HOME", "")),
    44	        "hf_hub_cache": str(getattr(hc, "HF_HUB_CACHE", "")),
    45	        "hf_assets_cache": str(getattr(hc, "HF_ASSETS_CACHE", "")),
    46	    }
    47	    try:
    48	        import transformers.utils.hub as th
    49	        fp["transformers_cache"] = str(getattr(th, "TRANSFORMERS_CACHE", getattr(th, "HF_MODULES_CACHE", "")))
    50	        fp["hf_modules_cache"] = str(getattr(th, "HF_MODULES_CACHE", ""))
    51	    except Exception:
    52	        fp["transformers_cache"] = fp["hf_modules_cache"] = "<unresolved>"
    53	    return fp
    54	
    55	report = {"xyz_py": sys.executable, "python": sys.version.split()[0], "checks": {},
    56	          "env": env_fingerprint(), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    57	def fail(msg):
    58	    report["ok"] = False; report["error"] = msg
    59	    pathlib.Path(evidence).write_text(json.dumps(report, indent=2))
    60	    sys.exit(f"prelaunch: NOT READY — {msg}")
    61	
    62	# 1. Real imports (not find_spec) of every runtime dependency.
    63	for m in ("numpy", "sqlite_vec", "tree_sitter", "tree_sitter_language_pack", "sentence_transformers", "torch", "einops", "pytest", "psutil"):
    64	    try:
    65	        mod = importlib.import_module(m); report["checks"][m] = getattr(mod, "__version__", "ok")
    66	    except Exception as e:
    67	        fail(f"import {m} failed: {e!r}")
    68	
    69	# 2. FTS5 + sqlite-vec usable.
    70	import sqlite3, sqlite_vec
    71	c = sqlite3.connect(":memory:"); c.enable_load_extension(True); sqlite_vec.load(c)
    72	if c.execute("select sqlite_compileoption_used('ENABLE_FTS5')").fetchone()[0] != 1: fail("FTS5 not compiled in")
    73	c.execute("create virtual table t using vec0(e float[4])"); c.execute("insert into t(rowid,e) values (1, ?)", (sqlite_vec.serialize_float32([1,0,0,0]),))
    74	if c.execute("select rowid from t where e match ? and k = ?", (sqlite_vec.serialize_float32([1,0,0,0]), 1)).fetchone()[0] != 1: fail("vec0 k = ? query failed")
    75	report["checks"]["sqlite_vec_version"] = c.execute("select vec_version()").fetchone()[0]
    76	
    77	# 3. Tree-sitter parsers the chunker needs. tree_sitter_language_pack DOWNLOADS grammars on first
    78	#    use (cache: ~/Library/Caches/tree-sitter-language-pack), so an offline builder turn fails
    79	#    unless they are already cached. Assert they are cached BEFORE parsing, or the check is
    80	#    vacuous on a machine that happens to have network.
    81	from tree_sitter_language_pack import get_parser
    82	try:
    83	    from tree_sitter_language_pack import downloaded_languages
    84	    cached = set(downloaded_languages())
    85	    missing = [l for l in ("python", "javascript", "typescript", "tsx", "php") if l not in cached]
    86	    if missing:
    87	        fail(f"tree-sitter grammars not cached (offline turns cannot fetch them): {missing} — "
    88	             f"run once WITH network: {sys.executable} -c \"from tree_sitter_language_pack import download; download(['python','javascript','typescript','tsx','php'])\"")
    89	    report["checks"]["grammars_cached"] = sorted(l for l in cached if l in {"python","javascript","typescript","tsx","php"})
    90	except ImportError:
    91	    report["checks"]["grammars_cached"] = "downloaded_languages() unavailable — parse smoke only"
    92	for lang, src in (("python", b"def f():\n  return 1\n"), ("javascript", b"function f(){return 1}\n"),
    93	                  ("typescript", b"export function f(): number { return 1 }\n"), ("tsx", b"const A = () => <div/>;\n"),
    94	                  ("php", b"<?php class A { function f() { return 1; } }\n")):
    95	    try:
    96	        tree = get_parser(lang).parse(src)
    97	        if tree.root_node.has_error and lang != "tsx": fail(f"grammar {lang}: parse error on smoke snippet")
    98	        report["checks"][f"grammar_{lang}"] = "ok"
    99	    except Exception as e:
   100	        fail(f"grammar {lang} unavailable: {e!r}")
   101	
   102	# 4. Both models load OFFLINE with their real classes and produce output.
   103	from sentence_transformers import SentenceTransformer, CrossEncoder
   104	try:
   105	    t0 = time.time(); m = SentenceTransformer("nomic-ai/CodeRankEmbed", trust_remote_code=True, device="cpu")
   106	    m.max_seq_length = 2048
   107	    v = m.encode(["Represent this query for searching relevant code: sort a list", "def sort_list(lst):\n    return sorted(lst)"])
   108	    if tuple(v.shape) != (2, 768): fail(f"CodeRankEmbed output shape {v.shape} != (2, 768)")
   109	    report["checks"]["CodeRankEmbed"] = {"shape": list(v.shape), "load_s": round(time.time() - t0, 1), "max_seq_length": m.max_seq_length}
   110	except Exception as e:
   111	    fail(f"CodeRankEmbed offline load failed (incomplete cache?): {e!r}")
   112	try:
   113	    t0 = time.time(); ce = CrossEncoder(RERANKER, device="cpu", trust_remote_code=True)
   114	    s = [float(x) for x in ce.predict([("sort a list in python", "def sort_list(lst):\n    return sorted(lst)"),
   115	                                       ("sort a list in python", "SELECT 1 FROM dual")])]
   116	    # A finite-AND-ordered assertion is the point: cross-encoder/ms-marco-MiniLM-L-6-v2 loads
   117	    # "successfully" on transformers 5.16.1 and returns [nan, nan] (old-format BERT checkpoint).
   118	    # A shape-only check passes that; this does not.
   119	    if len(s) != 2: fail(f"{RERANKER}: expected 2 scores, got {len(s)}")
   120	    if not all(v == v and abs(v) != float("inf") for v in s): fail(f"{RERANKER}: non-finite scores {s} — model unusable on this stack")
   121	    if not s[0] > s[1]: fail(f"{RERANKER}: does not rank the code snippet above unrelated SQL {s} — model unusable")
   122	    report["checks"]["reranker"] = {"model": RERANKER, "scores": s, "load_s": round(time.time() - t0, 1)}
   123	except SystemExit:
   124	    raise
   125	except Exception as e:
   126	    fail(f"reranker {RERANKER} offline load failed (incomplete cache?): {e!r}")
   127	
   128	report["ok"] = True
   129	pathlib.Path(evidence).write_text(json.dumps(report, indent=2))
   130	# Atomic publish: write beside the marker, then rename. A crash mid-write cannot leave a partial
   131	# marker that validate.sh would accept.
   132	tmp = pathlib.Path(marker + f".tmp.{os.getpid()}")
   133	tmp.write_text(json.dumps(report, indent=2))
   134	os.replace(tmp, marker)
   135	print(json.dumps(report, indent=2))
   136	print(f"prelaunch: READY — marker written to {marker}")
   137	PY
xyz
xyz/eval
xyz/index
xyz/ingest
xyz/retrieve
xyz/retrieve/lexical.py:45:    rows = store.connection.execute(
xyz/retrieve/pipeline.py:36:        rows = self.store.connection.execute(
xyz/retrieve/dense.py:33:    rows = store.connection.execute(KNN_SQL, (encoded, k))
xyz/eval/metrics.py:36:        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
xyz/cli.py:76:        store.connection.execute(
xyz/cli.py:77:            "INSERT OR REPLACE INTO meta(key, value) VALUES ('ingest.repo', ?)", (repo,)
xyz/cli.py:79:        store.connection.execute(
xyz/cli.py:80:            "INSERT OR REPLACE INTO meta(key, value) VALUES ('ingest.include_prefixes', ?)",
xyz/cli.py:155:    row = store.connection.execute(
xyz/cli.py:183:            row[0] for row in store.connection.execute("SELECT DISTINCT path FROM chunks")
xyz/cli.py:233:    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

exec
/bin/zsh -lc "git log --oneline --decorate -20
git log --all --name-status --pretty='format:COMMIT %H %s' -- 'xyz/xyz/**' | sed -n '1,260p'
git diff --stat 3301124..HEAD
git diff --name-status 3301124..HEAD | sed -n '1,260p'" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 17809ms:
2026-09-06 18:22:28.190 xcodebuild[93520:487585905]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:22:28.514 xcodebuild[93520:487585752] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BpkmXUlj' (errno=Operation not permitted)
2026-09-06 18:22:29.325 xcodebuild[94345:487588821]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:22:29.611 xcodebuild[94345:487588756] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
f0554ea (HEAD, marathon/gh11-act1-hybrid-retrieval-2026-09-05) GH-11 Act 1: remove duplicate nested trees reintroduced by p3; gitignore build junk
e9ed6e6 marathon: phase gh11-p4-roundtrip transcript saved (MARATHON-GH11-P4-ROUNDTRIP-TURN)
695e7e1 relay(MARATHON-GH11-P4-ROUNDTRIP-TURN): agy turn (agy headless; no push)
f4f1ccb relay(MARATHON-GH11-P4-ROUNDTRIP-TURN): codex turn (codex headless; no push)
073e55f marathon: render phase gh11-p4-roundtrip relay (MARATHON-GH11-P4-ROUNDTRIP-TURN)
857b1e4 marathon: phase gh11-p3-retrieve transcript saved (MARATHON-GH11-P3-RETRIEVE-TURN)
920f1f5 relay(MARATHON-GH11-P3-RETRIEVE-TURN): agy turn (agy headless; no push)
49395a8 relay(MARATHON-GH11-P3-RETRIEVE-TURN): codex turn (codex headless; no push)
52e7dd3 marathon: render phase gh11-p3-retrieve relay (MARATHON-GH11-P3-RETRIEVE-TURN)
0f748ae marathon: phase gh11-p2-store transcript saved (MARATHON-GH11-P2-STORE-TURN)
72142fd relay(MARATHON-GH11-P2-STORE-TURN): agy turn (agy headless; no push)
534fc54 relay(MARATHON-GH11-P2-STORE-TURN): codex turn (codex headless; no push)
7d52f3c marathon: render phase gh11-p2-store relay (MARATHON-GH11-P2-STORE-TURN)
13644e5 marathon: phase gh11-p1-chunkers transcript saved (MARATHON-GH11-P1-CHUNKERS-TURN)
b6a164d marathon: phase gh11-p0-scaffold transcript saved (MARATHON-GH11-P0-SCAFFOLD-TURN)
ae651da GH-11 p2: remove duplicate xyz/xyz and tests/tests per agy review; re-fire
83fa433 marathon: phase gh11-p2-store transcript saved (MARATHON-GH11-P2-STORE-TURN)
e32c439 marathon: phase gh11-p2-store escalation (relay-failed-before-gate)
c0feb22 relay(MARATHON-GH11-P2-STORE-TURN): agy turn (agy headless; no push)
3d11c3f relay(MARATHON-GH11-P2-STORE-TURN): codex turn (codex headless; no push)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fAyfVq0m' (errno=Operation not permitted)
2026-09-06 18:22:31.780 xcodebuild[95850:487594505]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:22:32.210 xcodebuild[95850:487594348] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-16cCDp7B' (errno=Operation not permitted)
2026-09-06 18:22:33.165 xcodebuild[96870:487598411]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:22:33.842 xcodebuild[96870:487598308] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
COMMIT f0554ea8a883a67bf7acac25cb61ffda74e3cbd0 GH-11 Act 1: remove duplicate nested trees reintroduced by p3; gitignore build junk
D	xyz/xyz/__init__.py
D	xyz/xyz/__main__.py
D	xyz/xyz/cli.py
D	xyz/xyz/eval/__init__.py
D	xyz/xyz/index/__init__.py
D	xyz/xyz/index/embed.py
D	xyz/xyz/index/store.py
D	xyz/xyz/ingest/__init__.py
D	xyz/xyz/ingest/chunk.py
D	xyz/xyz/ingest/walk.py
D	xyz/xyz/retrieve/__init__.py
D	xyz/xyz/retrieve/dense.py
D	xyz/xyz/retrieve/fuse.py
D	xyz/xyz/retrieve/latency.py
D	xyz/xyz/retrieve/lexical.py
D	xyz/xyz/retrieve/models.py
D	xyz/xyz/retrieve/pipeline.py
D	xyz/xyz/retrieve/rerank.py
D	xyz/xyz/xyz/__init__.py
D	xyz/xyz/xyz/__main__.py
D	xyz/xyz/xyz/cli.py
D	xyz/xyz/xyz/eval/__init__.py
D	xyz/xyz/xyz/index/__init__.py
D	xyz/xyz/xyz/index/embed.py
D	xyz/xyz/xyz/index/store.py
D	xyz/xyz/xyz/ingest/__init__.py
D	xyz/xyz/xyz/ingest/chunk.py
D	xyz/xyz/xyz/ingest/walk.py
D	xyz/xyz/xyz/retrieve/__init__.py

COMMIT e9ed6e66c212dbe867d10275cf72c06c711e44e6 marathon: phase gh11-p4-roundtrip transcript saved (MARATHON-GH11-P4-ROUNDTRIP-TURN)
M	xyz/xyz/retrieve/__init__.py
A	xyz/xyz/retrieve/dense.py
A	xyz/xyz/retrieve/fuse.py
A	xyz/xyz/retrieve/latency.py
A	xyz/xyz/retrieve/lexical.py
A	xyz/xyz/retrieve/models.py
A	xyz/xyz/retrieve/pipeline.py
A	xyz/xyz/retrieve/rerank.py
A	xyz/xyz/xyz/__init__.py
A	xyz/xyz/xyz/__main__.py
A	xyz/xyz/xyz/cli.py
A	xyz/xyz/xyz/eval/__init__.py
A	xyz/xyz/xyz/index/__init__.py
A	xyz/xyz/xyz/index/embed.py
A	xyz/xyz/xyz/index/store.py
A	xyz/xyz/xyz/ingest/__init__.py
A	xyz/xyz/xyz/ingest/chunk.py
A	xyz/xyz/xyz/ingest/walk.py
A	xyz/xyz/xyz/retrieve/__init__.py

COMMIT 857b1e40b3f6b223a4230b28e42142eb9efcb866 marathon: phase gh11-p3-retrieve transcript saved (MARATHON-GH11-P3-RETRIEVE-TURN)
A	xyz/xyz/__init__.py
A	xyz/xyz/__main__.py
A	xyz/xyz/cli.py
A	xyz/xyz/eval/__init__.py
A	xyz/xyz/index/__init__.py
A	xyz/xyz/index/embed.py
A	xyz/xyz/index/store.py
A	xyz/xyz/ingest/__init__.py
A	xyz/xyz/ingest/chunk.py
A	xyz/xyz/ingest/walk.py
A	xyz/xyz/retrieve/__init__.py

COMMIT ae651da30b5daffd970883cb61e5659d0f18a42e GH-11 p2: remove duplicate xyz/xyz and tests/tests per agy review; re-fire
D	xyz/xyz/__init__.py
D	xyz/xyz/__main__.py
D	xyz/xyz/cli.py
D	xyz/xyz/eval/__init__.py
D	xyz/xyz/index/__init__.py
D	xyz/xyz/ingest/__init__.py
D	xyz/xyz/ingest/chunk.py
D	xyz/xyz/ingest/walk.py
D	xyz/xyz/retrieve/__init__.py
D	xyz/xyz/xyz/__init__.py
D	xyz/xyz/xyz/__main__.py
D	xyz/xyz/xyz/cli.py
D	xyz/xyz/xyz/eval/__init__.py
D	xyz/xyz/xyz/index/__init__.py
D	xyz/xyz/xyz/ingest/__init__.py
D	xyz/xyz/xyz/retrieve/__init__.py

COMMIT e32c439875f692daa410a61d508e29adc51faae0 marathon: phase gh11-p2-store escalation (relay-failed-before-gate)
M	xyz/xyz/ingest/__init__.py
A	xyz/xyz/ingest/chunk.py
A	xyz/xyz/ingest/walk.py
A	xyz/xyz/xyz/__init__.py
A	xyz/xyz/xyz/__main__.py
A	xyz/xyz/xyz/cli.py
A	xyz/xyz/xyz/eval/__init__.py
A	xyz/xyz/xyz/index/__init__.py
A	xyz/xyz/xyz/ingest/__init__.py
A	xyz/xyz/xyz/retrieve/__init__.py

COMMIT 4a5b9f764e51805482c30728e436ffcad7e6f562 marathon: phase gh11-p1-chunkers transcript saved (MARATHON-GH11-P1-CHUNKERS-TURN)
A	xyz/xyz/__init__.py
A	xyz/xyz/__main__.py
A	xyz/xyz/cli.py
A	xyz/xyz/eval/__init__.py
A	xyz/xyz/index/__init__.py
A	xyz/xyz/ingest/__init__.py
A	xyz/xyz/retrieve/__init__.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-si7kVNbN' (errno=Operation not permitted)
2026-09-06 18:22:36.533 xcodebuild[160:487607323]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:22:37.052 xcodebuild[160:487607198] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-a1fJhycC' (errno=Operation not permitted)
2026-09-06 18:22:38.229 xcodebuild[1887:487611709]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:22:38.999 xcodebuild[1887:487611487] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
 .DS_Store                                          |  Bin 6148 -> 0 bytes
 .gitignore                                         |    8 +-
 GUIDING-PRINCIPLES.md                              |   13 +-
 PROJECT/.DS_Store                                  |  Bin 6148 -> 0 bytes
 PROJECT/1-INBOX/.DS_Store                          |  Bin 6148 -> 0 bytes
 PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md             |   61 +-
 .../2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md  |  240 ++
 .../2-WORKING/v0.5/GH-11-marathon/MARATHON.yaml    |   52 +
 .../v0.5/GH-11-marathon/brief-p0-scaffold.md       |   96 +
 .../v0.5/GH-11-marathon/brief-p1-chunkers.md       |  105 +
 .../v0.5/GH-11-marathon/brief-p2-store.md          |  117 +
 .../v0.5/GH-11-marathon/brief-p3-retrieve.md       |  119 +
 .../v0.5/GH-11-marathon/brief-p4-roundtrip-eval.md |  120 +
 ...42\200\224 Canonical Research and Build Doc.md" |   20 +-
 README.md                                          |   71 +
 ROADMAP.md                                         |    5 +-
 .../RELAY.md                                       |  199 ++
 .../RELAY.md                                       |  198 ++
 .../ESCALATION.md                                  |    8 +
 .../RELAY.md                                       |  217 ++
 .../RELAY.md                                       |  204 ++
 .../RELAY.md                                       |  213 ++
 prelaunch.sh                                       |  137 +
 pyproject.toml                                     |   30 +
 relay-system/2026-09-06/gh11-act1-plan-review.md   |  248 ++
 .../gh11-fire-or-review.PROMPT.txt                 |   47 +
 .../gh11-fire-or-review.agy.PROVENANCE.txt         |    3 +
 .../gh11-fire-or-review.agy.md                     |   12 +
 .../gh11-fire-or-review.codex.NO-CITATION.txt      |    1 +
 .../gh11-fire-or-review.codex.PROVENANCE.txt       |   15 +
 .../gh11-fire-or-review.codex.md                   | 2661 ++++++++++++++++++++
 .../2026-09-06/marathon-gh11-p0-scaffold-232225.md |  199 ++
 .../2026-09-06/marathon-gh11-p0-scaffold-234518.md |  199 ++
 .../2026-09-06/marathon-gh11-p1-chunkers-233238.md |  198 ++
 .../2026-09-06/marathon-gh11-p1-chunkers-234530.md |  198 ++
 .../2026-09-06/marathon-gh11-p2-store-234310.md    |  203 ++
 .../2026-09-06/marathon-gh11-p2-store-235256.md    |  217 ++
 .../2026-09-07/marathon-gh11-p3-retrieve-000156.md |  204 ++
 .../marathon-gh11-p4-roundtrip-011836.md           |  213 ++
 .../gh-11-act1-hybrid-retrieval/freshness.json     |   37 +
 .../gh-11-act1-hybrid-retrieval/lane-plan.json     |   29 +
 .../marathon-invocation.txt                        |    7 +
 .../gh-11-act1-hybrid-retrieval/packet.md          |   47 +
 .../gh-11-act1-hybrid-retrieval/readiness.json     |   33 +
 .../gh-11-act1-hybrid-retrieval/run-candidate.json |  170 ++
 .../2026-09-06/marathon-MARATHON_-164508-84084.log |  244 ++
 releases.db                                        |  Bin 192512 -> 192512 bytes
 releases.sql                                       |   13 +-
 tests/__init__.py                                  |    1 +
 tests/fakes.py                                     |   55 +
 tests/fixtures/mini-repo/Dockerfile                |    2 +
 tests/fixtures/mini-repo/app/example.php           |    7 +
 tests/fixtures/mini-repo/app/example.py            |   21 +
 tests/fixtures/mini-repo/app/example.ts            |    9 +
 tests/fixtures/mini-repo/broken.py                 |    2 +
 tests/fixtures/mini-repo/config.yml                |    2 +
 tests/fixtures/mini-repo/docs/guide.md             |   13 +
 tests/fixtures/mini-repo/node_modules/ignored.js   |    3 +
 tests/test_chunkers.py                             |  165 ++
 tests/test_cli.py                                  |  136 +
 tests/test_metrics.py                              |   52 +
 tests/test_retrieve.py                             |  169 ++
 tests/test_smoke.py                                |   20 +
 tests/test_store.py                                |  189 ++
 validate.sh                                        |   82 +
 xyz/__init__.py                                    |    3 +
 xyz/__main__.py                                    |    7 +
 xyz/cli.py                                         |  259 ++
 xyz/eval/__init__.py                               |    5 +
 xyz/eval/metrics.py                                |   90 +
 xyz/index/__init__.py                              |   22 +
 xyz/index/embed.py                                 |  104 +
 xyz/index/store.py                                 |  456 ++++
 xyz/ingest/__init__.py                             |   41 +
 xyz/ingest/chunk.py                                |  311 +++
 xyz/ingest/walk.py                                 |  161 ++
 xyz/retrieve/__init__.py                           |    6 +
 xyz/retrieve/dense.py                              |   34 +
 xyz/retrieve/fuse.py                               |   24 +
 xyz/retrieve/latency.py                            |   42 +
 xyz/retrieve/lexical.py                            |   55 +
 xyz/retrieve/models.py                             |   42 +
 xyz/retrieve/pipeline.py                           |  119 +
 xyz/retrieve/rerank.py                             |   53 +
 84 files changed, 10177 insertions(+), 16 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-EaWQI6gQ' (errno=Operation not permitted)
2026-09-06 18:22:41.525 xcodebuild[5098:487620867]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:22:41.985 xcodebuild[5098:487620708] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-eRQzGZ5M' (errno=Operation not permitted)
2026-09-06 18:22:42.929 xcodebuild[6614:487625704]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:22:43.391 xcodebuild[6614:487625616] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
D	.DS_Store
M	.gitignore
M	GUIDING-PRINCIPLES.md
D	PROJECT/.DS_Store
D	PROJECT/1-INBOX/.DS_Store
M	PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md
A	PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md
A	PROJECT/2-WORKING/v0.5/GH-11-marathon/MARATHON.yaml
A	PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p0-scaffold.md
A	PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p1-chunkers.md
A	PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p2-store.md
A	PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p3-retrieve.md
A	PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p4-roundtrip-eval.md
M	"PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 \342\200\224 Canonical Research and Build Doc.md"
A	README.md
M	ROADMAP.md
A	marathon-system/gh11-act1-hybrid-retrieval--gh11-p0-scaffold/RELAY.md
A	marathon-system/gh11-act1-hybrid-retrieval--gh11-p1-chunkers/RELAY.md
A	marathon-system/gh11-act1-hybrid-retrieval--gh11-p2-store/ESCALATION.md
A	marathon-system/gh11-act1-hybrid-retrieval--gh11-p2-store/RELAY.md
A	marathon-system/gh11-act1-hybrid-retrieval--gh11-p3-retrieve/RELAY.md
A	marathon-system/gh11-act1-hybrid-retrieval--gh11-p4-roundtrip/RELAY.md
A	prelaunch.sh
A	pyproject.toml
A	relay-system/2026-09-06/gh11-act1-plan-review.md
A	relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.PROMPT.txt
A	relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.agy.PROVENANCE.txt
A	relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.agy.md
A	relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.NO-CITATION.txt
A	relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.PROVENANCE.txt
A	relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md
A	relay-system/2026-09-06/marathon-gh11-p0-scaffold-232225.md
A	relay-system/2026-09-06/marathon-gh11-p0-scaffold-234518.md
A	relay-system/2026-09-06/marathon-gh11-p1-chunkers-233238.md
A	relay-system/2026-09-06/marathon-gh11-p1-chunkers-234530.md
A	relay-system/2026-09-06/marathon-gh11-p2-store-234310.md
A	relay-system/2026-09-06/marathon-gh11-p2-store-235256.md
A	relay-system/2026-09-07/marathon-gh11-p3-retrieve-000156.md
A	relay-system/2026-09-07/marathon-gh11-p4-roundtrip-011836.md
A	relay-system/preflight/2026-09-06/gh-11-act1-hybrid-retrieval/freshness.json
A	relay-system/preflight/2026-09-06/gh-11-act1-hybrid-retrieval/lane-plan.json
A	relay-system/preflight/2026-09-06/gh-11-act1-hybrid-retrieval/marathon-invocation.txt
A	relay-system/preflight/2026-09-06/gh-11-act1-hybrid-retrieval/packet.md
A	relay-system/preflight/2026-09-06/gh-11-act1-hybrid-retrieval/readiness.json
A	relay-system/preflight/2026-09-06/gh-11-act1-hybrid-retrieval/run-candidate.json
A	relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log
M	releases.db
M	releases.sql
A	tests/__init__.py
A	tests/fakes.py
A	tests/fixtures/mini-repo/Dockerfile
A	tests/fixtures/mini-repo/app/example.php
A	tests/fixtures/mini-repo/app/example.py
A	tests/fixtures/mini-repo/app/example.ts
A	tests/fixtures/mini-repo/broken.py
A	tests/fixtures/mini-repo/config.yml
A	tests/fixtures/mini-repo/docs/guide.md
A	tests/fixtures/mini-repo/node_modules/ignored.js
A	tests/test_chunkers.py
A	tests/test_cli.py
A	tests/test_metrics.py
A	tests/test_retrieve.py
A	tests/test_smoke.py
A	tests/test_store.py
A	validate.sh
A	xyz/__init__.py
A	xyz/__main__.py
A	xyz/cli.py
A	xyz/eval/__init__.py
A	xyz/eval/metrics.py
A	xyz/index/__init__.py
A	xyz/index/embed.py
A	xyz/index/store.py
A	xyz/ingest/__init__.py
A	xyz/ingest/chunk.py
A	xyz/ingest/walk.py
A	xyz/retrieve/__init__.py
A	xyz/retrieve/dense.py
A	xyz/retrieve/fuse.py
A	xyz/retrieve/latency.py
A	xyz/retrieve/lexical.py
A	xyz/retrieve/models.py
A	xyz/retrieve/pipeline.py
A	xyz/retrieve/rerank.py

exec
/bin/zsh -lc 'for p in $(git ls-tree -r --name-only e9ed6e6 xyz/xyz | sort); do rel=${p#xyz/xyz/}; if git cat-file -e e9ed6e6:xyz/$rel 2>/dev/null; then a=$(git rev-parse e9ed6e6:$p); b=$(git rev-parse e9ed6e6:xyz/$rel); if [ "$a" != "$b" ]; then echo "DIFF $p vs xyz/$rel"; fi; else echo "NO_ROOT $p -> xyz/$rel"; fi; done
for p in $(git ls-tree -r --name-only e9ed6e6 xyz/xyz/xyz | sort); do rel=${p#xyz/xyz/xyz/}; if git cat-file -e e9ed6e6:xyz/$rel 2>/dev/null; then a=$(git rev-parse e9ed6e6:$p); b=$(git rev-parse e9ed6e6:xyz/$rel); if [ "$a" != "$b" ]; then echo "DEEP_DIFF $p vs xyz/$rel"; fi; else echo "DEEP_NO_ROOT $p -> xyz/$rel"; fi; done' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
codex
The core retrieval math is now clear: score signs are normalized correctly, but fusion is equal-weight rank-only RRF, and the reranker replaces scores for the first 50 fused candidates. I’m checking the executable test/gate evidence and the deletion history now; one architectural exception has already surfaced—the CLI writes ingest metadata directly into SQLite outside `store.py`.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 exited 127 in 0ms:
zsh:1: no such file or directory: .venv/bin/python

exec
/bin/zsh -lc "python3 -c \"import importlib.util; print([(m, bool(importlib.util.find_spec(m))) for m in ['pytest','numpy','sqlite_vec','tree_sitter','tree_sitter_language_pack']])\"" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 0ms:
[('pytest', True), ('numpy', False), ('sqlite_vec', False), ('tree_sitter', False), ('tree_sitter_language_pack', False)]

exec
/bin/zsh -lc "rg -n '45 passed|validate: OK|pytest' marathon-system relay-system PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md | tail -120" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 0ms:
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:122:| `gh11-p0-scaffold` | Phase 0 close-out: constraints into `GUIDING-PRINCIPLES.md`, `pyproject.toml`, `xyz/` package skeleton, `tests/`, extend `validate.sh` | `GUIDING-PRINCIPLES.md`, `pyproject.toml`, `xyz/`, `tests/`, `validate.sh` | `bash validate.sh`: package imports, pytest green, PDDA checks green |
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:123:| `gh11-p1-chunkers` | Tree-sitter chunkers (Python, JS/TS, PHP), heading-level Markdown, file-level config/templates; path-prefixed embedded text (#8); widened include list (#2) | `xyz/ingest/`, `tests/` | pytest on a fixture tree: function-aligned chunks with `qualified_name`/`start_line`/`end_line`, YAML/Dockerfile chunked, every chunk's `embedded_text` starts with its path |
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:124:| `gh11-p2-store` | SQLite store: `chunks` + FTS5 + `vec0`; embed cache keyed `(content_sha, model, dim, provider)`; file-level drift/planner so unchanged re-ingest embeds nothing; provider/dim mismatch refuses | `xyz/index/`, `tests/` | pytest with a fake embedder: second ingest calls the embedder 0 times; mismatch raises; FTS5 and vec0 row counts equal `chunks` |
PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md:125:| `gh11-p3-retrieve` | Query path: BM25 (FTS5) ∥ dense (`vec0`, `k = ?`) → RRF(k=60) → cross-encoder rerank top 25-50 → optional no-answer τ; per-stage latency + p50/p95 helper | `xyz/retrieve/`, `tests/` | pytest with fake embedder + fake reranker: a doc ranked low by both lanes but high by the reranker ends at rank 1; RRF matches the hand-computed value; `k = ?` present in the KNN SQL; τ suppresses below-threshold |
marathon-system/gh11-act1-hybrid-retrieval--gh11-p2-store/RELAY.md:113:No query path (p3), no CLI (p4). No real model in pytest.
marathon-system/gh11-act1-hybrid-retrieval--gh11-p2-store/RELAY.md:118:- One real smoke, out of pytest and under the offline env: `CodeRankEmbedder().encode_query("sort a
marathon-system/gh11-act1-hybrid-retrieval--gh11-p3-retrieve/RELAY.md:123:- One real smoke, out of pytest, offline env: `CrossEncoderReranker().score("sort a list in python",
marathon-system/gh11-act1-hybrid-retrieval--gh11-p3-retrieve/RELAY.md:184:- Focused verification: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" "$XYZ_PY" -m pytest -q
marathon-system/gh11-act1-hybrid-retrieval--gh11-p3-retrieve/RELAY.md:200:- Passed 100% (9 tests) in pytest suite.
marathon-system/gh11-act1-hybrid-retrieval--gh11-p0-scaffold/RELAY.md:38:| `XYZ_PY` | interpreter carrying the pinned deps (`sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`, `tree-sitter`, `tree-sitter-language-pack`, `pytest`, `psutil`) | `<repo>/.venv/bin/python` |
marathon-system/gh11-act1-hybrid-retrieval--gh11-p0-scaffold/RELAY.md:45:`PYTHONPATH=<repo>` which `validate.sh` sets and `pyproject.toml` mirrors for pytest; write scratch
marathon-system/gh11-act1-hybrid-retrieval--gh11-p0-scaffold/RELAY.md:73:   `tree-sitter-language-pack`; optional group `dev = ["pytest", "psutil"]`; console script
marathon-system/gh11-act1-hybrid-retrieval--gh11-p0-scaffold/RELAY.md:76:   `[tool.pytest.ini_options] pythonpath = ["."]` and `testpaths = ["tests"]`.
marathon-system/gh11-act1-hybrid-retrieval--gh11-p0-scaffold/RELAY.md:89:   `python -m xyz --version`, pytest). Do not edit it in this phase unless a check is wrong — if so,
marathon-system/gh11-act1-hybrid-retrieval--gh11-p0-scaffold/RELAY.md:154:  package discovery, pytest configuration, and exact runtime dependency versions from the pinned
marathon-system/gh11-act1-hybrid-retrieval--gh11-p0-scaffold/RELAY.md:192:- `pyproject.toml` contains correct metadata, `requires-python`, exact pinned dependencies, pytest and setuptools config.
marathon-system/gh11-act1-hybrid-retrieval--gh11-p4-roundtrip/RELAY.md:119:- `bash validate.sh` green (pytest uses fakes only — the real run is **not** in pytest).
relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log:25:== pytest
relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log:28:validate: OK
relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log:56:== pytest
relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log:59:validate: OK
relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log:105:== pytest
relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log:108:validate: OK
relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log:164:== pytest
relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log:167:validate: OK
relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log:223:== pytest
relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log:227:validate: OK
marathon-system/gh11-act1-hybrid-retrieval--gh11-p1-chunkers/RELAY.md:176:- `python -m pytest -p no:cacheprovider tests/test_chunkers.py -q` → `11 passed in 0.07s`.
relay-system/2026-09-07/marathon-gh11-p3-retrieve-000156.md:123:- One real smoke, out of pytest, offline env: `CrossEncoderReranker().score("sort a list in python",
relay-system/2026-09-07/marathon-gh11-p3-retrieve-000156.md:184:- Focused verification: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" "$XYZ_PY" -m pytest -q
relay-system/2026-09-07/marathon-gh11-p3-retrieve-000156.md:200:- Passed 100% (9 tests) in pytest suite.
relay-system/2026-09-07/marathon-gh11-p4-roundtrip-011836.md:119:- `bash validate.sh` green (pytest uses fakes only — the real run is **not** in pytest).
relay-system/2026-09-06/marathon-gh11-p0-scaffold-234518.md:38:| `XYZ_PY` | interpreter carrying the pinned deps (`sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`, `tree-sitter`, `tree-sitter-language-pack`, `pytest`, `psutil`) | `<repo>/.venv/bin/python` |
relay-system/2026-09-06/marathon-gh11-p0-scaffold-234518.md:45:`PYTHONPATH=<repo>` which `validate.sh` sets and `pyproject.toml` mirrors for pytest; write scratch
relay-system/2026-09-06/marathon-gh11-p0-scaffold-234518.md:73:   `tree-sitter-language-pack`; optional group `dev = ["pytest", "psutil"]`; console script
relay-system/2026-09-06/marathon-gh11-p0-scaffold-234518.md:76:   `[tool.pytest.ini_options] pythonpath = ["."]` and `testpaths = ["tests"]`.
relay-system/2026-09-06/marathon-gh11-p0-scaffold-234518.md:89:   `python -m xyz --version`, pytest). Do not edit it in this phase unless a check is wrong — if so,
relay-system/2026-09-06/marathon-gh11-p0-scaffold-234518.md:154:  package discovery, pytest configuration, and exact runtime dependency versions from the pinned
relay-system/2026-09-06/marathon-gh11-p0-scaffold-234518.md:192:- `pyproject.toml` contains correct metadata, `requires-python`, exact pinned dependencies, pytest and setuptools config.
relay-system/2026-09-06/gh11-act1-plan-review.md:116:- [Blocker] Red controls / gate — **Implemented.** `validate.sh` is now unconditional (package presence incl. `xyz/__main__.py`, exact `__version__ == 0.5.0.dev0`, `python -m xyz --version`, pytest); p0 red controls flip the version and delete `__main__.py`; p2 red controls assert `files_skipped == files_seen` / `files_reingested == 0` separately from embedder calls, plus `fts_match` tests for inserted/changed/deleted tokens with a trigger-disabled red control.
relay-system/2026-09-06/gh11-act1-plan-review.md:142:- [Pass] **Several falsification and fallback fixes are concrete.** `validate.sh:43-54` unconditionally checks package presence, exact version and pytest; p2:80-82 separately asserts file skips and writes; p4:55-57,73-74 rejects empty queries and tests rank 11 at two depths; p4:36-39 uses a same-depth dense baseline rather than Run 9. p1 Task 1 preserves root-relative prefixes and p4:80-83 uses one fresh subset DB; every label in `.embed-tmp/eval/queries-LTVera-Pandas.json` lies under scripts/app/alembic. p4:77-79 supplies a measured ETA trigger and p4:105 requires a <30-second re-ingest. Runtime feasibility is conditional on the readiness fix above; no actual model/corpus run was attempted here.
relay-system/2026-09-06/marathon-gh11-p0-scaffold-232225.md:38:| `XYZ_PY` | interpreter carrying the pinned deps (`sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`, `tree-sitter`, `tree-sitter-language-pack`, `pytest`, `psutil`) | `<repo>/.venv/bin/python` |
relay-system/2026-09-06/marathon-gh11-p0-scaffold-232225.md:45:`PYTHONPATH=<repo>` which `validate.sh` sets and `pyproject.toml` mirrors for pytest; write scratch
relay-system/2026-09-06/marathon-gh11-p0-scaffold-232225.md:73:   `tree-sitter-language-pack`; optional group `dev = ["pytest", "psutil"]`; console script
relay-system/2026-09-06/marathon-gh11-p0-scaffold-232225.md:76:   `[tool.pytest.ini_options] pythonpath = ["."]` and `testpaths = ["tests"]`.
relay-system/2026-09-06/marathon-gh11-p0-scaffold-232225.md:89:   `python -m xyz --version`, pytest). Do not edit it in this phase unless a check is wrong — if so,
relay-system/2026-09-06/marathon-gh11-p0-scaffold-232225.md:154:  package discovery, pytest configuration, and exact runtime dependency versions from the pinned
relay-system/2026-09-06/marathon-gh11-p0-scaffold-232225.md:192:- `pyproject.toml` contains correct metadata, `requires-python`, exact pinned dependencies, pytest and setuptools config.
relay-system/2026-09-06/marathon-gh11-p1-chunkers-233238.md:176:- `python -m pytest -p no:cacheprovider tests/test_chunkers.py -q` → `11 passed in 0.07s`.
relay-system/2026-09-06/marathon-gh11-p1-chunkers-234530.md:176:- `python -m pytest -p no:cacheprovider tests/test_chunkers.py -q` → `11 passed in 0.07s`.
relay-system/2026-09-06/marathon-gh11-p2-store-235256.md:113:No query path (p3), no CLI (p4). No real model in pytest.
relay-system/2026-09-06/marathon-gh11-p2-store-235256.md:118:- One real smoke, out of pytest and under the offline env: `CodeRankEmbedder().encode_query("sort a
relay-system/2026-09-06/marathon-gh11-p2-store-234310.md:113:No query path (p3), no CLI (p4). No real model in pytest.
relay-system/2026-09-06/marathon-gh11-p2-store-234310.md:118:- One real smoke, out of pytest and under the offline env: `CodeRankEmbedder().encode_query("sort a
relay-system/2026-09-06/marathon-gh11-p2-store-234310.md:184:- Verification: `"$XYZ_PY" -m pytest -q tests/test_store.py` → `12 passed in 0.85s`.
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:376:    30	| `XYZ_PY` | interpreter carrying the pinned deps (`sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`, `tree-sitter`, `tree-sitter-language-pack`, `pytest`, `psutil`) | `<repo>/.venv/bin/python` |
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:383:    37	`PYTHONPATH=<repo>` which `validate.sh` sets and `pyproject.toml` mirrors for pytest; write scratch
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:411:    65	   `tree-sitter-language-pack`; optional group `dev = ["pytest", "psutil"]`; console script
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:414:    68	   `[tool.pytest.ini_options] pythonpath = ["."]` and `testpaths = ["tests"]`.
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:427:    81	   `python -m xyz --version`, pytest). Do not edit it in this phase unless a check is wrong — if so,
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:652:   105	No query path (p3), no CLI (p4). No real model in pytest.
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:657:   110	- One real smoke, out of pytest and under the offline env: `CodeRankEmbedder().encode_query("sort a
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:790:   122	| `gh11-p0-scaffold` | Phase 0 close-out: constraints into `GUIDING-PRINCIPLES.md`, `pyproject.toml`, `xyz/` package skeleton, `tests/`, extend `validate.sh` | `GUIDING-PRINCIPLES.md`, `pyproject.toml`, `xyz/`, `tests/`, `validate.sh` | `bash validate.sh`: package imports, pytest green, PDDA checks green |
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:791:   123	| `gh11-p1-chunkers` | Tree-sitter chunkers (Python, JS/TS, PHP), heading-level Markdown, file-level config/templates; path-prefixed embedded text (#8); widened include list (#2) | `xyz/ingest/`, `tests/` | pytest on a fixture tree: function-aligned chunks with `qualified_name`/`start_line`/`end_line`, YAML/Dockerfile chunked, every chunk's `embedded_text` starts with its path |
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:792:   124	| `gh11-p2-store` | SQLite store: `chunks` + FTS5 + `vec0`; embed cache keyed `(content_sha, model, dim, provider)`; file-level drift/planner so unchanged re-ingest embeds nothing; provider/dim mismatch refuses | `xyz/index/`, `tests/` | pytest with a fake embedder: second ingest calls the embedder 0 times; mismatch raises; FTS5 and vec0 row counts equal `chunks` |
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:793:   125	| `gh11-p3-retrieve` | Query path: BM25 (FTS5) ∥ dense (`vec0`, `k = ?`) → RRF(k=60) → cross-encoder rerank top 25-50 → optional no-answer τ; per-stage latency + p50/p95 helper | `xyz/retrieve/`, `tests/` | pytest with fake embedder + fake reranker: a doc ranked low by both lanes but high by the reranker ends at rank 1; RRF matches the hand-computed value; `k = ?` present in the KNN SQL; τ suppresses below-threshold |
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1071:   115	- One real smoke, out of pytest, offline env: `CrossEncoderReranker().score("sort a list in python",
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1186:   111	- `bash validate.sh` green (pytest uses fakes only — the real run is **not** in pytest).
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1246:    51	for mod in ("numpy", "sqlite_vec", "tree_sitter_language_pack", "sentence_transformers", "pytest"):
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1274:    79	echo "== pytest"
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1275:    80	"$XYZ_PY" -m pytest -q tests
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1277:    82	echo "validate: OK"
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1340:    63	for m in ("numpy", "sqlite_vec", "tree_sitter", "tree_sitter_language_pack", "sentence_transformers", "torch", "einops", "pytest", "psutil"):
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1534:   116	- [Blocker] Red controls / gate — **Implemented.** `validate.sh` is now unconditional (package presence incl. `xyz/__main__.py`, exact `__version__ == 0.5.0.dev0`, `python -m xyz --version`, pytest); p0 red controls flip the version and delete `__main__.py`; p2 red controls assert `files_skipped == files_seen` / `files_reingested == 0` separately from embedder calls, plus `fts_match` tests for inserted/changed/deleted tokens with a trigger-disabled red control.
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1560:   142	- [Pass] **Several falsification and fallback fixes are concrete.** `validate.sh:43-54` unconditionally checks package presence, exact version and pytest; p2:80-82 separately asserts file skips and writes; p4:55-57,73-74 rejects empty queries and tests rank 11 at two depths; p4:36-39 uses a same-depth dense baseline rather than Run 9. p1 Task 1 preserves root-relative prefixes and p4:80-83 uses one fresh subset DB; every label in `.embed-tmp/eval/queries-LTVera-Pandas.json` lies under scripts/app/alembic. p4:77-79 supplies a measured ETA trigger and p4:105 requires a <30-second re-ingest. Runtime feasibility is conditional on the readiness fix above; no actual model/corpus run was attempted here.
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1759:   105	No query path (p3), no CLI (p4). No real model in pytest.
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1764:   110	- One real smoke, out of pytest and under the offline env: `CodeRankEmbedder().encode_query("sort a
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:1890:   115	- One real smoke, out of pytest, offline env: `CrossEncoderReranker().score("sort a list in python",
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2005:   111	- `bash validate.sh` green (pytest uses fakes only — the real run is **not** in pytest).
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2100:    30	| `XYZ_PY` | interpreter carrying the pinned deps (`sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`, `tree-sitter`, `tree-sitter-language-pack`, `pytest`, `psutil`) | `<repo>/.venv/bin/python` |
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2107:    37	`PYTHONPATH=<repo>` which `validate.sh` sets and `pyproject.toml` mirrors for pytest; write scratch
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2135:    65	   `tree-sitter-language-pack`; optional group `dev = ["pytest", "psutil"]`; console script
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2138:    68	   `[tool.pytest.ini_options] pythonpath = ["."]` and `testpaths = ["tests"]`.
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2151:    81	   `python -m xyz --version`, pytest). Do not edit it in this phase unless a check is wrong — if so,
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2338:    63	for m in ("numpy", "sqlite_vec", "tree_sitter", "tree_sitter_language_pack", "sentence_transformers", "torch", "einops", "pytest", "psutil"):
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2463:    51	for mod in ("numpy", "sqlite_vec", "tree_sitter_language_pack", "sentence_transformers", "pytest"):
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2491:    79	echo "== pytest"
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2492:    80	"$XYZ_PY" -m pytest -q tests
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2494:    82	echo "validate: OK"
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2625:   105	No query path (p3), no CLI (p4). No real model in pytest.
relay-system/2026-09-06/gh11-fire-or-review-161410/gh11-fire-or-review.codex.md:2630:   110	- One real smoke, out of pytest and under the offline env: `CodeRankEmbedder().encode_query("sort a

exec
/bin/zsh -lc "nl -ba relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log | sed -n '205,235p'
nl -ba marathon-system/gh11-act1-hybrid-retrieval--gh11-p4-roundtrip/RELAY.md | sed -n '105,140p'
nl -ba .gitignore | tail -50" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 0ms:
   205	env ok: 3.11.15 prelaunch 2026-09-06T23:45:01Z sqlite-vec v0.1.9
   206	== PDDA deterministic checks (PDDA_MODE=full so errors block; the repo's .pdda-mode stays observe)
   207	SUMMARY [pdda-check-frontmatter] errors=0 warns=0 info=0
   208	SUMMARY [pdda-check-status-table] errors=0 warns=0 info=0
   209	SUMMARY [pdda-check-roadmap] errors=0 warns=0 info=0
   210	INFO [pdda-check-roadmap-coverage] PROJECT/2-WORKING/v0.5/BGE Small vs Code-Capable Embeddings — Decision Report.md:1 roadmap coverage check skipped because roadmap_exempt=true
   211	INFO [pdda-check-roadmap-coverage] PROJECT/2-WORKING/v0.5/Code Embedding Models — Full Evidence Table.md:1 roadmap coverage check skipped because roadmap_exempt=true
   212	INFO [pdda-check-roadmap-coverage] PROJECT/2-WORKING/v0.5/Embedding Fine-Tuning Training Pipelines — Full Evidence Table.md:1 roadmap coverage check skipped because roadmap_exempt=true
   213	INFO [pdda-check-roadmap-coverage] PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p0-scaffold.md:1 roadmap coverage check skipped because roadmap_exempt=true
   214	INFO [pdda-check-roadmap-coverage] PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p1-chunkers.md:1 roadmap coverage check skipped because roadmap_exempt=true
   215	INFO [pdda-check-roadmap-coverage] PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p2-store.md:1 roadmap coverage check skipped because roadmap_exempt=true
   216	INFO [pdda-check-roadmap-coverage] PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p3-retrieve.md:1 roadmap coverage check skipped because roadmap_exempt=true
   217	INFO [pdda-check-roadmap-coverage] PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p4-roundtrip-eval.md:1 roadmap coverage check skipped because roadmap_exempt=true
   218	INFO [pdda-check-roadmap-coverage] PROJECT/2-WORKING/v0.5/NL-to-Code Retrieval Datasets — Full Evidence Table.md:1 roadmap coverage check skipped because roadmap_exempt=true
   219	SUMMARY [pdda-check-roadmap-coverage] errors=0 warns=0 info=9
   220	SUMMARY [pdda-check-hardcoded-paths] errors=0 warns=0 info=0
   221	== package presence (unconditional after gh11-p0-scaffold)
   222	== import smoke (exact version)
   223	== pytest
   224	........................................................................ [ 66%]
   225	....................................                                     [100%]
   226	108 passed in 1.45s
   227	validate: OK
   228	marathon-drive: gate-guard: gate exit 0 after 12s — peak group RSS 386MB (tier full; caps: RSS 8192MB, wall 1800s, CPU 1200s)
   229	marathon-drive: transcript saved: /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/relay-system/2026-09-07/marathon-gh11-p4-roundtrip-011836.md
   230	marathon-drive: warn: host free swap is critically low (998MB < 1024MB)
   231	marathon-drive: memory-telemetry: phase gh11-p4-roundtrip-complete boundary — compressor=7236MB, swap_free=998MB
   232	marathon-drive: phase gh11-p4-roundtrip complete — STATUS: Approved, gate passed
   233	
   234	marathon-drive: end-of-run cost summary (tick analyze) —
   235	--- cost ---
   105	   section to `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md` with the corpus provenance (full or subset,
   106	   chunk/file counts, chunker version = this commit), the table from step 3, and the four Phase 1
   107	   QA-gate bullets each marked met / not met with the number that shows it; update the `## Status`
   108	   table and `## Run log` of `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`. Do not renumber
   109	   or edit earlier runs; do not touch `.embed-tmp/BENCHMARKS.md`; do not commit anything from
   110	   `$XYZ_SCRATCH`.
   111	
   112	## Non-goals
   113	
   114	No Slack/HTTP/MCP surface. No model or reranker comparison beyond the four modes. No changes to
   115	`.embed-tmp/`. No `CHANGELOG.md` entry (orchestrator, at PR time).
   116	
   117	## Definition of done
   118	
   119	- `bash validate.sh` green (pytest uses fakes only — the real run is **not** in pytest).
   120	- All four Phase 1 QA-gate bullets evidenced with numbers in FINDINGS-0.5.md: round-trip done
   121	  (full or labelled subset); second ingest `chunks_embedded == 0` and < 30 s; reorder count ≥ 1;
   122	  p50/p95 recorded per stage.
   123	- Acceptance from the capture doc: at depth 100, `hybrid+rerank` MRR@100 and R@1 ≥ the `dense`
   124	  arm's MRR@100 and R@1 − 0.05, on the same DB. If lower, the phase is **not** approved — report the
   125	  numbers and the most likely cause (reranker choice, BM25 sanitiser, fusion depth); do not tune
   126	  against the labelled set.
   127	- Red controls (show once in the relay): `xyz eval` with an empty query file exits 2; the
   128	  rank-11 metric test flips between miss and 1/11 with `depth`.
   129	
   130	
   131	---
   132	
   133	▶ TAKE YOUR TURN (codex — BUILDER role)
   134	
   135	You are the BUILDER for this phase. Read the phase brief above and implement it.
   136	1. Implement the brief by creating/editing the artifact file(s): xyz/,tests/,pyproject.toml,PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md,PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md
   137	2. Append a build block to this relay file: `### Round N · Builder · codex` summarizing what you did (files touched, key decisions).
   138	3. Use this exact tick binary (run it from any directory): /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.xyz/bin/tick
   139	   - /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.xyz/bin/tick claim MARATHON-GH11-P4-ROUNDTRIP-TURN --agent codex --paths "marathon-system/gh11-act1-hybrid-retrieval--gh11-p4-roundtrip/RELAY.md,xyz/,tests/,pyproject.toml,PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md,PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md"
   140	   - /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.xyz/bin/tick ping MARATHON-GH11-P4-ROUNDTRIP-TURN --agent codex
     1	*.pyc
     2	.DS_Store
     3	.pdda-gh-state.tsv
     4	.relay-scratch/
     5	.venv/
     6	.xyz/
     7	/.tick/
     8	/temp/
     9	PROJECT/PDDA-ACTIVITY.jsonl
    10	__pycache__/
    11	temp/

exec
/bin/zsh -lc "git show --stat --oneline f0554ea
git show --name-status --format='' f0554ea | sed -n '1,300p'
rg -n '"'^def test_|''^    def test_'"' tests --glob '*.py' | wc -l
rg -n '@pytest.mark.parametrize' tests --glob '*.py'" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 6389ms:
2026-09-06 18:23:51.007 xcodebuild[77425:487825425]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:23:51.306 xcodebuild[77425:487825286] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-oWDJYLEM' (errno=Operation not permitted)
2026-09-06 18:23:52.167 xcodebuild[78401:487828135]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:23:52.469 xcodebuild[78401:487828006] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
f0554ea GH-11 Act 1: remove duplicate nested trees reintroduced by p3; gitignore build junk
 .DS_Store                                          | Bin 6148 -> 0 bytes
 .gitignore                                         |   8 +-
 .relay-scratch/prelaunch.json                      |  54 ---
 PROJECT/.DS_Store                                  | Bin 6148 -> 0 bytes
 PROJECT/1-INBOX/.DS_Store                          | Bin 6148 -> 0 bytes
 .../2026-09-06/marathon-MARATHON_-164508-84084.log | 244 +++++++++++
 tests/tests/__init__.py                            |   1 -
 tests/tests/fakes.py                               |  55 ---
 tests/tests/fixtures/mini-repo/Dockerfile          |   2 -
 tests/tests/fixtures/mini-repo/app/example.php     |   7 -
 tests/tests/fixtures/mini-repo/app/example.py      |  21 -
 tests/tests/fixtures/mini-repo/app/example.ts      |   9 -
 tests/tests/fixtures/mini-repo/broken.py           |   2 -
 tests/tests/fixtures/mini-repo/config.yml          |   2 -
 tests/tests/fixtures/mini-repo/docs/guide.md       |  13 -
 .../fixtures/mini-repo/node_modules/ignored.js     |   3 -
 tests/tests/test_chunkers.py                       | 165 --------
 tests/tests/test_retrieve.py                       | 169 --------
 tests/tests/test_smoke.py                          |  20 -
 tests/tests/test_store.py                          | 189 ---------
 tests/tests/tests/__init__.py                      |   1 -
 tests/tests/tests/fakes.py                         |  43 --
 tests/tests/tests/fixtures/mini-repo/Dockerfile    |   2 -
 .../tests/tests/fixtures/mini-repo/app/example.php |   7 -
 .../tests/tests/fixtures/mini-repo/app/example.py  |  21 -
 .../tests/tests/fixtures/mini-repo/app/example.ts  |   9 -
 tests/tests/tests/fixtures/mini-repo/broken.py     |   2 -
 tests/tests/tests/fixtures/mini-repo/config.yml    |   2 -
 tests/tests/tests/fixtures/mini-repo/docs/guide.md |  13 -
 .../fixtures/mini-repo/node_modules/ignored.js     |   3 -
 tests/tests/tests/test_chunkers.py                 | 165 --------
 tests/tests/tests/test_smoke.py                    |  20 -
 tests/tests/tests/test_store.py                    | 189 ---------
 xyz/xyz/__init__.py                                |   3 -
 xyz/xyz/__main__.py                                |   7 -
 xyz/xyz/cli.py                                     |  33 --
 xyz/xyz/eval/__init__.py                           |   1 -
 xyz/xyz/index/__init__.py                          |  22 -
 xyz/xyz/index/embed.py                             | 104 -----
 xyz/xyz/index/store.py                             | 448 ---------------------
 xyz/xyz/ingest/__init__.py                         |  41 --
 xyz/xyz/ingest/chunk.py                            | 307 --------------
 xyz/xyz/ingest/walk.py                             | 161 --------
 xyz/xyz/retrieve/__init__.py                       |   6 -
 xyz/xyz/retrieve/dense.py                          |  34 --
 xyz/xyz/retrieve/fuse.py                           |  24 --
 xyz/xyz/retrieve/latency.py                        |  42 --
 xyz/xyz/retrieve/lexical.py                        |  55 ---
 xyz/xyz/retrieve/models.py                         |  42 --
 xyz/xyz/retrieve/pipeline.py                       | 119 ------
 xyz/xyz/retrieve/rerank.py                         |  53 ---
 xyz/xyz/xyz/__init__.py                            |   3 -
 xyz/xyz/xyz/__main__.py                            |   7 -
 xyz/xyz/xyz/cli.py                                 |  33 --
 xyz/xyz/xyz/eval/__init__.py                       |   1 -
 xyz/xyz/xyz/index/__init__.py                      |  22 -
 xyz/xyz/xyz/index/embed.py                         | 104 -----
 xyz/xyz/xyz/index/store.py                         | 448 ---------------------
 xyz/xyz/xyz/ingest/__init__.py                     |  41 --
 xyz/xyz/xyz/ingest/chunk.py                        | 307 --------------
 xyz/xyz/xyz/ingest/walk.py                         | 161 --------
 xyz/xyz/xyz/retrieve/__init__.py                   |   1 -
 62 files changed, 250 insertions(+), 3821 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-pmzO853M' (errno=Operation not permitted)
2026-09-06 18:23:54.375 xcodebuild[80157:487832275]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:23:54.630 xcodebuild[80157:487832192] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-u01QRlnk' (errno=Operation not permitted)
2026-09-06 18:23:55.491 xcodebuild[81268:487834461]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-06 18:23:55.729 xcodebuild[81268:487834395] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
D	.DS_Store
M	.gitignore
D	.relay-scratch/prelaunch.json
D	PROJECT/.DS_Store
D	PROJECT/1-INBOX/.DS_Store
A	relay-system/run-logs/2026-09-06/marathon-MARATHON_-164508-84084.log
D	tests/tests/__init__.py
D	tests/tests/fakes.py
D	tests/tests/fixtures/mini-repo/Dockerfile
D	tests/tests/fixtures/mini-repo/app/example.php
D	tests/tests/fixtures/mini-repo/app/example.py
D	tests/tests/fixtures/mini-repo/app/example.ts
D	tests/tests/fixtures/mini-repo/broken.py
D	tests/tests/fixtures/mini-repo/config.yml
D	tests/tests/fixtures/mini-repo/docs/guide.md
D	tests/tests/fixtures/mini-repo/node_modules/ignored.js
D	tests/tests/test_chunkers.py
D	tests/tests/test_retrieve.py
D	tests/tests/test_smoke.py
D	tests/tests/test_store.py
D	tests/tests/tests/__init__.py
D	tests/tests/tests/fakes.py
D	tests/tests/tests/fixtures/mini-repo/Dockerfile
D	tests/tests/tests/fixtures/mini-repo/app/example.php
D	tests/tests/tests/fixtures/mini-repo/app/example.py
D	tests/tests/tests/fixtures/mini-repo/app/example.ts
D	tests/tests/tests/fixtures/mini-repo/broken.py
D	tests/tests/tests/fixtures/mini-repo/config.yml
D	tests/tests/tests/fixtures/mini-repo/docs/guide.md
D	tests/tests/tests/fixtures/mini-repo/node_modules/ignored.js
D	tests/tests/tests/test_chunkers.py
D	tests/tests/tests/test_smoke.py
D	tests/tests/tests/test_store.py
D	xyz/xyz/__init__.py
D	xyz/xyz/__main__.py
D	xyz/xyz/cli.py
D	xyz/xyz/eval/__init__.py
D	xyz/xyz/index/__init__.py
D	xyz/xyz/index/embed.py
D	xyz/xyz/index/store.py
D	xyz/xyz/ingest/__init__.py
D	xyz/xyz/ingest/chunk.py
D	xyz/xyz/ingest/walk.py
D	xyz/xyz/retrieve/__init__.py
D	xyz/xyz/retrieve/dense.py
D	xyz/xyz/retrieve/fuse.py
D	xyz/xyz/retrieve/latency.py
D	xyz/xyz/retrieve/lexical.py
D	xyz/xyz/retrieve/models.py
D	xyz/xyz/retrieve/pipeline.py
D	xyz/xyz/retrieve/rerank.py
D	xyz/xyz/xyz/__init__.py
D	xyz/xyz/xyz/__main__.py
D	xyz/xyz/xyz/cli.py
D	xyz/xyz/xyz/eval/__init__.py
D	xyz/xyz/xyz/index/__init__.py
D	xyz/xyz/xyz/index/embed.py
D	xyz/xyz/xyz/index/store.py
D	xyz/xyz/xyz/ingest/__init__.py
D	xyz/xyz/xyz/ingest/chunk.py
D	xyz/xyz/xyz/ingest/walk.py
D	xyz/xyz/xyz/retrieve/__init__.py
      40
tests/test_retrieve.py:130:@pytest.mark.parametrize(
tests/test_cli.py:102:@pytest.mark.parametrize("payload", ([], {"queries": []}))
tests/test_store.py:131:@pytest.mark.parametrize(

exec
/bin/zsh -lc 'for p in $(git ls-tree -r --name-only e9ed6e6 tests/tests | sort); do rel=${p#tests/tests/}; if git cat-file -e e9ed6e6:tests/$rel 2>/dev/null; then a=$(git rev-parse e9ed6e6:$p); b=$(git rev-parse e9ed6e6:tests/$rel); if [ "$a" != "$b" ]; then echo "DIFF $p vs tests/$rel"; fi; else echo "NO_ROOT $p -> tests/$rel"; fi; done' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" '"'/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/bin/python' -m pytest --collect-only -q -p no:cacheprovider tests" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 exited 1 in 177ms:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/pytest/__main__.py", line 9, in <module>
    raise SystemExit(_console_main())
                     ^^^^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/_pytest/config/__init__.py", line 253, in _console_main
    code = _main(prog=_get_prog_name(sys.argv))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/_pytest/config/__init__.py", line 223, in _main
    config = _prepareconfig(new_args, plugins, prog=prog)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/_pytest/config/__init__.py", line 410, in _prepareconfig
    config: Config = pluginmanager.hook.pytest_cmdline_parse(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/_pytest/helpconfig.py", line 124, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/_pytest/config/__init__.py", line 1232, in pytest_cmdline_parse
    self.parse(args)
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/_pytest/config/__init__.py", line 1605, in parse
    self.hook.pytest_load_initial_conftests(
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/_pytest/warnings.py", line 129, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/pluggy/_callers.py", line 116, in _multicall
    next(function_gen)  # first yield
    ^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/_pytest/capture.py", line 170, in pytest_load_initial_conftests
    capman.start_global_capturing()
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/_pytest/capture.py", line 773, in start_global_capturing
    self._global_capturing = _get_multicapture(self._method)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/_pytest/capture.py", line 714, in _get_multicapture
    return MultiCapture(in_=FDCapture(0), out=FDCapture(1), err=FDCapture(2))
                                              ^^^^^^^^^^^^
  File "/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/lib/python3.11/site-packages/_pytest/capture.py", line 493, in __init__
    TemporaryFile(buffering=0),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/.local/share/uv/python/cpython-3.11.15-macos-aarch64-none/lib/python3.11/tempfile.py", line 628, in TemporaryFile
    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/.local/share/uv/python/cpython-3.11.15-macos-aarch64-none/lib/python3.11/tempfile.py", line 127, in _sanitize_params
    dir = gettempdir()
          ^^^^^^^^^^^^
  File "/Users/noelsaw/.local/share/uv/python/cpython-3.11.15-macos-aarch64-none/lib/python3.11/tempfile.py", line 316, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/Users/noelsaw/.local/share/uv/python/cpython-3.11.15-macos-aarch64-none/lib/python3.11/tempfile.py", line 309, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/noelsaw/.local/share/uv/python/cpython-3.11.15-macos-aarch64-none/lib/python3.11/tempfile.py", line 224, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq']

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" '"'/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv/bin/python' -m pytest --collect-only -q -s -p no:cacheprovider tests" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 240ms:
tests/test_chunkers.py::test_walk_filters_and_is_deterministic
tests/test_chunkers.py::test_include_prefixes_keep_root_relative_paths
tests/test_chunkers.py::test_missing_root_raises
tests/test_chunkers.py::test_python_chunks_and_lines
tests/test_chunkers.py::test_typescript_and_php_chunks
tests/test_chunkers.py::test_markdown_sections_and_file_chunks
tests/test_chunkers.py::test_all_embedded_text_is_path_prefixed_and_hashed
tests/test_chunkers.py::test_oversize_single_line_and_markdown_split
tests/test_chunkers.py::test_broken_parse_falls_back_with_warning
tests/test_chunkers.py::test_scandir_error_is_recorded_after_other_yields
tests/test_chunkers.py::test_chunk_repo_is_deterministic
tests/test_cli.py::test_ingest_query_eval_end_to_end_and_dedupe
tests/test_cli.py::test_eval_counts_chunk_id_reorder
tests/test_cli.py::test_empty_query_file_exits_two[payload0]
tests/test_cli.py::test_empty_query_file_exits_two[payload1]
tests/test_cli.py::test_missing_gold_path_exits_two
tests/test_cli.py::test_bogus_ingest_path_exits_two
tests/test_metrics.py::test_score_three_queries
tests/test_metrics.py::test_rank_eleven_flips_at_depth
tests/test_metrics.py::test_same_path_chunk_ids_survive_json_round_trip
tests/test_retrieve.py::test_rrf_matches_hand_computed_overlap_and_tie_break
tests/test_retrieve.py::test_knn_sql_uses_bound_k_and_dense_query_executes
tests/test_retrieve.py::test_bm25_sanitises_operators_empty_and_keeps_higher_better
tests/test_retrieve.py::test_rerank_reorders_rrf_and_tau_is_query_level
tests/test_retrieve.py::test_candidate_depth_rerank_cap_and_same_path_identity
tests/test_retrieve.py::test_retriever_rejects_embedder_identity_mismatch[kwargs0]
tests/test_retrieve.py::test_retriever_rejects_embedder_identity_mismatch[kwargs1]
tests/test_retrieve.py::test_retriever_rejects_embedder_identity_mismatch[kwargs2]
tests/test_retrieve.py::test_auto_modes_errors_timings_and_latency_summary
tests/test_smoke.py::test_version
tests/test_smoke.py::test_cli_without_arguments
tests/test_smoke.py::test_cli_version
tests/test_smoke.py::test_cli_unknown_subcommand
tests/test_store.py::test_first_ingest_indexes_fts_and_vectors
tests/test_store.py::test_second_ingest_is_a_true_file_sha_short_circuit
tests/test_store.py::test_changed_file_reuses_unchanged_chunk_vectors_and_refreshes_fts
tests/test_store.py::test_deleted_file_is_pruned_from_all_indexes
tests/test_store.py::test_prefix_scoped_ingest_does_not_prune_outside_scope
tests/test_store.py::test_empty_corpus_does_not_write
tests/test_store.py::test_incomplete_walk_preserves_every_existing_index
tests/test_store.py::test_open_rejects_each_embedder_identity_mismatch[model_id-other]
tests/test_store.py::test_open_rejects_each_embedder_identity_mismatch[dim-12]
tests/test_store.py::test_open_rejects_each_embedder_identity_mismatch[provider-other-provider]
tests/test_store.py::test_chunk_vector_matches_provider_keyed_cache
tests/test_store.py::test_coderank_embedder_sets_guard_and_prefixes_queries_only

45 tests collected in 0.17s

mcp: codebase-memory-mcp/check_index_coverage started
mcp: codebase-memory-mcp/check_index_coverage (completed)
mcp: codebase-memory-mcp/get_code_snippet started
mcp: codebase-memory-mcp/get_code_snippet (completed)
mcp: codebase-memory-mcp/get_code_snippet started
mcp: codebase-memory-mcp/get_code_snippet (completed)
mcp: codebase-memory-mcp/get_code_snippet started
mcp: codebase-memory-mcp/get_code_snippet (completed)
mcp: codebase-memory-mcp/get_code_snippet started
mcp: codebase-memory-mcp/get_code_snippet (completed)
exec
/bin/zsh -lc "rg -n --hidden --glob '"'!.git/**'"' --glob '"'!relay-system/**'"' --glob '"'!marathon-system/**'"' --glob '"'!PROJECT/**'"' '(sqlite3\\.connect|CREATE VIRTUAL TABLE.*chunks|INSERT INTO chunks|DELETE FROM chunks|INSERT OR REPLACE INTO meta)' .
rg -n --hidden --glob '"'!.git/**'"' --glob '"'!relay-system/**'"' --glob '"'!marathon-system/**'"' --glob '"'!PROJECT/**'"' '(from xyz|import xyz)' . | sed -n '1,260p'" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 0ms:
./validate.sh:57:c = sqlite3.connect(":memory:"); c.enable_load_extension(True); sqlite_vec.load(c)
./xyz/index/store.py:99:        connection = sqlite3.connect(path)
./xyz/index/store.py:151:                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
./xyz/index/store.py:159:                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:163:                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:167:                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:169:                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:172:                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
./xyz/index/store.py:339:                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in old_ids)
./xyz/index/store.py:342:                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
./xyz/index/store.py:362:                        INSERT INTO chunks(
./xyz/index/store.py:380:                        "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)",
./xyz/index/store.py:416:                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in ids)
./xyz/index/store.py:419:                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
./prelaunch.sh:71:c = sqlite3.connect(":memory:"); c.enable_load_extension(True); sqlite_vec.load(c)
./xyz/cli.py:77:            "INSERT OR REPLACE INTO meta(key, value) VALUES ('ingest.repo', ?)", (repo,)
./xyz/cli.py:80:            "INSERT OR REPLACE INTO meta(key, value) VALUES ('ingest.include_prefixes', ?)",
./tests/test_retrieve.py:27:                INSERT INTO chunks(
./tests/test_retrieve.py:35:                "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)", (chunk_id, vector)
./validate.sh:15:export PYTHONPATH="$REPO${PYTHONPATH:+:$PYTHONPATH}"       # import xyz from the tree; no editable install
./validate.sh:75:got="$("$XYZ_PY" -c 'import xyz; print(xyz.__version__)')"
./tests/test_retrieve.py:11:from xyz.index.store import IndexMismatch, Store
./tests/test_retrieve.py:12:from xyz.retrieve.dense import KNN_SQL, dense_search
./tests/test_retrieve.py:13:from xyz.retrieve.fuse import rrf
./tests/test_retrieve.py:14:from xyz.retrieve.latency import LatencyLog
./tests/test_retrieve.py:15:from xyz.retrieve.lexical import bm25_search
./tests/test_retrieve.py:16:from xyz.retrieve.models import Hit
./tests/test_retrieve.py:17:from xyz.retrieve.pipeline import Retriever
./tests/test_retrieve.py:79:    import xyz.retrieve.pipeline as pipeline
./tests/test_retrieve.py:106:    import xyz.retrieve.pipeline as pipeline
./tests/test_retrieve.py:143:    import xyz.retrieve.pipeline as pipeline
./tests/test_cli.py:9:from xyz.cli import main
./tests/test_cli.py:14:    import xyz.cli as cli
./tests/test_cli.py:65:    import xyz.retrieve.pipeline as pipeline
./tests/test_cli.py:66:    from xyz.retrieve.models import Hit
./tests/test_cli.py:82:    import xyz.cli as cli
./xyz/ingest/__init__.py:9:from xyz.ingest.chunk import Chunk, ChunkResult, chunk_file
./xyz/ingest/__init__.py:10:from xyz.ingest.walk import DEFAULT_EXCLUDE, DEFAULT_INCLUDE, walk_repo
./xyz/cli.py:14:from xyz import __version__
./xyz/cli.py:15:from xyz.eval.metrics import score
./xyz/cli.py:16:from xyz.index import CodeRankEmbedder, EmptyCorpus, Store
./xyz/cli.py:17:from xyz.retrieve import Retriever
./xyz/cli.py:18:from xyz.retrieve.latency import LatencyLog
./xyz/cli.py:19:from xyz.retrieve.pipeline import MODES
./xyz/cli.py:20:from xyz.retrieve.rerank import CrossEncoderReranker
./xyz/index/__init__.py:3:from xyz.index.embed import CodeRankEmbedder, Embedder
./xyz/index/__init__.py:4:from xyz.index.store import (
./xyz/index/store.py:17:from xyz.index.embed import Embedder
./xyz/index/store.py:18:from xyz.ingest import Chunk, ChunkResult, chunk_file, chunk_repo, walk_repo
./xyz/eval/__init__.py:3:from xyz.eval.metrics import Report, score
./xyz/retrieve/fuse.py:7:from xyz.retrieve.models import Hit
./tests/test_smoke.py:3:import xyz
./tests/test_smoke.py:4:from xyz.cli import main
./xyz/retrieve/lexical.py:7:from xyz.index.store import Store
./xyz/retrieve/lexical.py:8:from xyz.retrieve.models import Hit
./xyz/retrieve/dense.py:10:from xyz.index.store import Store
./xyz/retrieve/dense.py:11:from xyz.retrieve.models import Hit
./tests/test_store.py:13:from xyz.index.embed import QUERY_PREFIX, CodeRankEmbedder
./tests/test_store.py:14:from xyz.index.store import EmptyCorpus, IndexMismatch, Store, WalkIncomplete
./xyz/retrieve/pipeline.py:8:from xyz.index.embed import Embedder
./xyz/retrieve/pipeline.py:9:from xyz.index.store import Store
./xyz/retrieve/pipeline.py:10:from xyz.retrieve.dense import dense_search
./xyz/retrieve/pipeline.py:11:from xyz.retrieve.fuse import rrf
./xyz/retrieve/pipeline.py:12:from xyz.retrieve.lexical import bm25_search
./xyz/retrieve/pipeline.py:13:from xyz.retrieve.models import Hit, SearchHit, SearchResult
./xyz/retrieve/pipeline.py:14:from xyz.retrieve.rerank import Reranker
./tests/test_metrics.py:7:from xyz.eval.metrics import score
./xyz/retrieve/__init__.py:3:from xyz.retrieve.models import Hit, SearchHit, SearchResult
./xyz/retrieve/__init__.py:4:from xyz.retrieve.pipeline import Retriever
./xyz/__main__.py:3:from xyz.cli import main
./tests/test_chunkers.py:11:from xyz.ingest import chunk_file, chunk_repo, walk_repo

exec
/bin/zsh -lc "rg -n --hidden --no-ignore --glob '"'!.git/**'"' --glob '"'!relay-system/**'"' --glob '"'!marathon-system/**'"' --glob '"'!PROJECT/**'"' '(sqlite3\\.connect|CREATE VIRTUAL TABLE.*chunks|INSERT INTO chunks|DELETE FROM chunks|INSERT OR REPLACE INTO meta)' . | sed -n '1,260p'
rg -n --hidden --no-ignore --glob '"'!.git/**'"' --glob '"'!relay-system/**'"' --glob '"'!marathon-system/**'"' --glob '"'!PROJECT/**'"' 'xyz/xyz|xyz\\.xyz' . || true" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-3812-8u6bqxuq
 succeeded in 0ms:
./prelaunch.sh:71:c = sqlite3.connect(":memory:"); c.enable_load_extension(True); sqlite_vec.load(c)
./tests/test_retrieve.py:27:                INSERT INTO chunks(
./tests/test_retrieve.py:35:                "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)", (chunk_id, vector)
./validate.sh:57:c = sqlite3.connect(":memory:"); c.enable_load_extension(True); sqlite_vec.load(c)
./xyz/index/store.py:99:        connection = sqlite3.connect(path)
./xyz/index/store.py:151:                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
./xyz/index/store.py:159:                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:163:                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:167:                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:169:                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:172:                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
./xyz/index/store.py:339:                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in old_ids)
./xyz/index/store.py:342:                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
./xyz/index/store.py:362:                        INSERT INTO chunks(
./xyz/index/store.py:380:                        "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)",
./xyz/index/store.py:416:                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in ids)
./xyz/index/store.py:419:                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
./xyz/cli.py:77:            "INSERT OR REPLACE INTO meta(key, value) VALUES ('ingest.repo', ?)", (repo,)
./xyz/cli.py:80:            "INSERT OR REPLACE INTO meta(key, value) VALUES ('ingest.include_prefixes', ?)",


consult: advisor failed or exceeded the 300s cap
