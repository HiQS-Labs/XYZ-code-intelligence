**NO FIRSTHAND VERIFICATION CITED** — treat conclusions as conditional (codex's answer carries an unsupported [Pass]/verified/confirmed-style claim with no quoted span or file:line citation nearby, despite the consult PREAMBLE asking advisors to cite evidence.)

> **ATTESTATION**
> Model: gpt-5.6-sol
> Provider: openai
> Sandbox: read-only

Reading additional input from stdin...
OpenAI Codex v0.153.4
--------
workdir: /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: read-only
reasoning effort: medium
reasoning summaries: none
session id: 01a07900-3573-7421-95b3-068685971e6b
--------
user
You are an INDEPENDENT advisor in a one-shot cross-model consult. Another model is answering the SAME question separately and a coordinator will reconcile both answers, so give your own honest, specific read — do not hedge toward a consensus you cannot see. Read any repo files the question references (cite file:line). Respond with: (1) a short direct ANSWER; (2) graded FINDINGS — [Blocker]/[Should]/[Nit]/[Pass] — where applicable; (3) a one-line RECOMMENDATION. You are ADVISORY ONLY: output your analysis as text; do not rely on writing files (you are running in a throwaway copy).

=== CONSULT QUESTION ===
# Decision: fire the marathon now, or run a 5th plan-review round?

You are advising on a build in this repo (branch `marathon/gh11-act1-hybrid-retrieval-2026-09-05`).

## What is planned
A 5-phase marathon implementing Act 1 of issue #11 — the XYZ hybrid retrieval library
(canonical doc Phase 0 close-out + all of Phase 1). Read these:
- `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md` (the plan)
- `PROJECT/2-WORKING/v0.5/GH-11-marathon/MARATHON.yaml` + its five `brief-p*.md`
- `validate.sh` (per-phase gate), `prelaunch.sh` (operator readiness control)
- `relay-system/2026-09-06/gh11-act1-plan-review.md` (the full 4-round review)

## What has happened
Codex plan-reviewed it for FOUR rounds. 14 findings, all implemented.
- Rounds 1-2 improved the five phase briefs and found TWO REAL DEFECTS:
  (a) `tree_sitter_language_pack` downloads grammars at first use, so every offline builder
      turn would have failed at the chunker;
  (b) `cross-encoder/ms-marco-MiniLM-L-6-v2` loads cleanly on torch 2.14 / transformers 5.16
      and returns `[nan, nan]` logits — silently broken reranker.
- Rounds 3-4 were ENTIRELY about `prelaunch.sh`, a readiness script that was ADDED to satisfy a
  round-2 finding: first marker-invalidation-on-failure, then binding the HuggingFace cache
  fingerprint to library-resolved constants instead of a hand-built path.
- Round 4 verdict: 1 blocker (now fixed, verified with 4 red controls: XDG_CACHE_HOME,
  HUGGINGFACE_HUB_CACHE, HF_HUB_CACHE, HF_HOME drift all rejected) + 3 passes. The reviewer
  explicitly closed DoD question 5 (falsifiable checks). Round cap 4/4 exhausted, STATUS Escalated.

## The tension
NO product code exists yet. The `xyz/` package is created BY the marathon. Four rounds of review
have been spent on planning apparatus — briefs, a gate, and a pre-launch checker — while the
actual deliverable (chunkers, SQLite+FTS5+vec store, RRF+rerank retrieval, a real round-trip on a
5000-chunk corpus) has not started. Each phase ALSO gets its own build+review loop inside the
marathon (reviewer agy, max_review_rounds 2-3 per phase), so the code will be reviewed regardless.

## Your task
Vote **FIRE** (launch the marathon now) or **REVIEW** (a 5th plan-review round is justified).

Answer these directly:
1. Your vote, in the first line: `VOTE: FIRE` or `VOTE: REVIEW`.
2. One paragraph of reasoning.
3. Be blunt: is this overengineering? Has the review loop crossed from finding real defects into
   polishing a checker that runs once, on the operator's own machine?
4. Name the ONE thing that would actually change your vote.
5. If FIRE: name the single highest risk you'd accept, and what you'd watch for in phase 1 output.
   If REVIEW: name the specific defect you believe a 5th round would catch that the marathon's own
   per-phase review would NOT.

Be concise and decisive. Do not hedge into "it depends".

codex
I’m using the repo’s prescribed startup route, then I’ll inspect the plan, phase briefs, gates, and full review record before casting a hard vote.
exec
/bin/zsh -lc "sed -n '1,240p' ROUTER.md" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
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

exec
/bin/zsh -lc "sed -n '1,240p' GUIDING-PRINCIPLES.md; sed -n '1,220p' AGENTS.md; sed -n '1,220p' README.md" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
 succeeded in 0ms:
# Guiding Principles

The north star this repo's goals and implementation decisions answer to. When a design choice is
unclear, the option that better serves these principles wins.

## Purpose

PDDA exists to make a repo's project docs a **reliable source of truth and work signal for
long-running AI agent tasks** — so an agent (or human) can stop, resume, or hand off at any point and
recover full state from the docs alone, not from memory or chat history.

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

exec
/bin/zsh -lc 'wc -l PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md PROJECT/2-WORKING/v0.5/GH-11-marathon/MARATHON.yaml PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p*.md validate.sh prelaunch.sh relay-system/2026-09-06/gh11-act1-plan-review.md' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
 succeeded in 0ms:
     232 PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md
      52 PROJECT/2-WORKING/v0.5/GH-11-marathon/MARATHON.yaml
      96 PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p0-scaffold.md
     105 PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p1-chunkers.md
     117 PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p2-store.md
     119 PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p3-retrieve.md
     120 PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p4-roundtrip-eval.md
      82 validate.sh
     137 prelaunch.sh
     232 relay-system/2026-09-06/gh11-act1-plan-review.md
    1292 total

codex
The bet is straightforward: a fifth review is only warranted if the launch controls or phase boundaries still permit an unrecoverable failure that the per-phase review cannot catch. Launching is otherwise easy to pause and revise; more preflight review mainly delays contact with product reality.
exec
/bin/zsh -lc 'for f in PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p0-scaffold.md PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p1-chunkers.md PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p2-store.md; do nl -ba "$f"; done' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
 succeeded in 0ms:
     1	---
     2	title: GH-11 marathon brief — gh11-p0-scaffold
     3	status: active
     4	created: 2026-09-05
     5	updated: 2026-09-06
     6	owner: Noel Saw
     7	goal: Phase brief consumed by marathon-drive.sh for phase gh11-p0-scaffold; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
     8	roadmap_exempt: true
     9	---
    10	
    11	# Phase brief — gh11-p0-scaffold: Phase 0 close-out (constraints, pyproject, `xyz/` skeleton, gate)
    12	
    13	## Status
    14	
    15	| What was just completed | What's next |
    16	|---|---|
    17	| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p0-scaffold`; outcome recorded in the capture doc. |
    18	
    19	Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
    20	(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
    21	Canonical doc: `PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md`
    22	→ "Phase 0 — Decision lock and repo scaffolding", steps 2-3.
    23	
    24	## Environment contract (read first — applies to every phase)
    25	
    26	`validate.sh` defines it; the operator exports the values when launching the marathon:
    27	
    28	| Variable | Meaning | Default |
    29	|---|---|---|
    30	| `XYZ_PY` | interpreter carrying the pinned deps (`sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`, `tree-sitter`, `tree-sitter-language-pack`, `pytest`, `psutil`) | `<repo>/.venv/bin/python` |
    31	| `XYZ_SCRATCH` | where generated evidence goes (index DBs, eval JSON, logs); swept by the harness, never committed | `<repo>/.relay-scratch` |
    32	| `XYZ_EVAL_REPO` | the corpus for the p4 round-trip (an absolute path to a LTVera-Pandas checkout) | unset — p4 fails fast if unset |
    33	| `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `TOKENIZERS_PARALLELISM=false` | no network inside a turn; both models are already in the HF cache | exported by `validate.sh`; **export them yourself before any ad-hoc smoke** |
    34	
    35	Rules: run Python only as `"$XYZ_PY"`; **no `pip install`**, no editable install (it writes
    36	`*.egg-info/` into the tree, an off-lane write) — the package is imported from the tree via
    37	`PYTHONPATH=<repo>` which `validate.sh` sets and `pyproject.toml` mirrors for pytest; write scratch
    38	only under `$XYZ_SCRATCH`.
    39	
    40	Readiness is **proven before the marathon fires**, not assumed: the operator runs `prelaunch.sh`
    41	with the same `XYZ_PY`, which really imports every dependency, instantiates the Python / JS / TS /
    42	TSX / PHP parsers, and loads **both models offline with their real classes** (encode + predict),
    43	then writes `<venv>/xyz-prelaunch.json`. `validate.sh`'s `env preflight` requires that marker (for
    44	this exact interpreter) and re-does the cheap parts (real imports, parser creation, FTS5/vec0). If
    45	the marker is missing or names another interpreter, the gate fails with the command to run — do not
    46	work around it. Before starting, run `bash validate.sh` once: `env preflight` must pass; the later
    47	sections are expected to fail until this phase is done.
    48	
    49	## Task
    50	
    51	1. **Constraints into `GUIDING-PRINCIPLES.md`** (canonical Phase 0 step 3). The file is still the
    52	   PDDA-repo boilerplate. Replace its `## Purpose` paragraph with one that describes *this* repo
    53	   (XYZ Code Intelligence: local-first code retrieval, successor to Ask-Self) and append two numbered
    54	   principles after the existing eight, in the same voice:
    55	   - **Local-first.** Ingest, embedding, retrieval and reranking run on the operator's machine with
    56	     no network call on the query path. A cloud API may appear only as an explicitly opt-in
    57	     comparison arm, never as the primary lane.
    58	   - **Permissively licensed models only.** Every model weight the pipeline loads is Apache-2.0 or
    59	     MIT (or equivalent). Verify the licence on the model card before a model enters any run; a
    60	     model whose licence is unstated or non-commercial is rejected, not deferred.
    61	   Leave the other principles intact (they still govern the PDDA docs in this repo).
    62	2. **`pyproject.toml`** at the repo root: name `xyz-code-intelligence`, version `0.5.0.dev0`,
    63	   `requires-python = ">=3.11"`, dependencies pinned to the versions `"$XYZ_PY" -m pip list` shows
    64	   for `sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`, `tree-sitter`,
    65	   `tree-sitter-language-pack`; optional group `dev = ["pytest", "psutil"]`; console script
    66	   `xyz = "xyz.cli:main"` (declared for a future install — not installed in this marathon);
    67	   setuptools backend with `[tool.setuptools.packages.find] include = ["xyz*"]`;
    68	   `[tool.pytest.ini_options] pythonpath = ["."]` and `testpaths = ["tests"]`.
    69	3. **`xyz/` package skeleton** (canonical Phase 0 step 2), modules only — docstrings and
    70	   `__version__`, no logic:
    71	   - `xyz/__init__.py` (`__version__ = "0.5.0.dev0"` — `validate.sh` asserts this exact string)
    72	   - `xyz/__main__.py` → `raise SystemExit(main())` from `xyz.cli`
    73	   - `xyz/ingest/__init__.py`, `xyz/index/__init__.py`, `xyz/retrieve/__init__.py`,
    74	     `xyz/eval/__init__.py`
    75	   - `xyz/cli.py`: `main(argv: list[str] | None = None) -> int` (argparse). `--version` prints the
    76	     version and returns 0; no arguments prints the subcommand list (`ingest`, `query`, `eval`, all
    77	     "not implemented until gh11-p4") and returns 0; an unknown subcommand returns 2.
    78	4. **`tests/`**: `tests/__init__.py`; `tests/test_smoke.py` asserting `xyz.__version__ ==
    79	   "0.5.0.dev0"`, `main([])` returns 0, `main(["--version"])` returns 0, `main(["bogus"])` returns 2.
    80	5. **`validate.sh`** already asserts everything above (package presence, exact version,
    81	   `python -m xyz --version`, pytest). Do not edit it in this phase unless a check is wrong — if so,
    82	   say exactly what and why in the relay.
    83	
    84	## Non-goals
    85	
    86	No chunking, embedding, SQL or retrieval code. No changes to `.embed-tmp/`. No `AGENTS.md`
    87	rewrite (parked). No `CHANGELOG.md` entry — the orchestrator writes it at PR time.
    88	
    89	## Definition of done
    90	
    91	- `bash validate.sh` exits 0 end to end.
    92	- `GUIDING-PRINCIPLES.md` contains both new principles and a repo-accurate Purpose; the eight
    93	  original principles are unchanged; `./utils/pdda/pdda.sh governance` reports no new error.
    94	- Red control (do it, quote the output in the relay, then restore): change `__version__` to
    95	  `"0.0.0"` → `validate.sh` must fail at "import smoke (exact version)"; delete
    96	  `xyz/__main__.py` → it must fail at "package presence".
     1	---
     2	title: GH-11 marathon brief — gh11-p1-chunkers
     3	status: active
     4	created: 2026-09-05
     5	updated: 2026-09-06
     6	owner: Noel Saw
     7	goal: Phase brief consumed by marathon-drive.sh for phase gh11-p1-chunkers; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
     8	roadmap_exempt: true
     9	---
    10	
    11	# Phase brief — gh11-p1-chunkers: AST / Markdown / file-level chunkers with path-prefixed text
    12	
    13	## Status
    14	
    15	| What was just completed | What's next |
    16	|---|---|
    17	| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p1-chunkers` after `gh11-p0-scaffold`; outcome recorded in the capture doc. |
    18	
    19	Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
    20	(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
    21	Canonical doc → "Phase 1 — Chunking + hybrid retrieval skeleton", step 1.
    22	Environment contract: see `brief-p0-scaffold.md` (`XYZ_PY`, `XYZ_SCRATCH`, offline env, no installs).
    23	
    24	## Context you must read before coding
    25	
    26	- `.embed-tmp/scripts/embed_repos.py` — the current (throwaway) chunker. What it actually has:
    27	  `INCLUDE_EXT`, `iter_files(...)` (line ~106), and per-chunk records carrying **`path`,
    28	  `start_line`, `end_line`, `text`**, to which `id` and `repo` are added (lines ~136-140, ~160-161).
    29	  It has **no** `qualified_name`, `kind`, `content_sha` or `embedded_text` — those are **new** fields
    30	  this phase introduces. The new chunker must still emit `path`, `start_line`, `end_line`, `text`
    31	  so the existing scorer can read an exported `chunks.jsonl`.
    32	- Issue #8 (closed): leading each chunk's embedded text with the file's relative path was the
    33	  largest quality jump in the project (MRR 0.80 → 0.98). Issue #2 (closed): YAML and Dockerfiles
    34	  were skipped, a silent infra blind spot. Both are re-implemented here because that code is not on
    35	  this branch.
    36	- `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md` (lines ~174-179): the model's real memory guard is
    37	  `max_seq_length = 2048` tokens; the 6,000-character split below is a **character heuristic**
    38	  chosen to sit under that window with headroom, not a tokenizer bound. The p2 embedder enforces the
    39	  token cap; this phase only bounds characters.
    40	
    41	## Task
    42	
    43	Implement `xyz/ingest/`:
    44	
    45	1. `xyz/ingest/walk.py` — `walk_repo(root, include_ext=DEFAULT_INCLUDE, exclude_dirs=DEFAULT_EXCLUDE,
    46	   include_prefixes=None)` yielding `(rel_path, bytes)` in sorted order. `include_prefixes` (a
    47	   tuple of repo-relative directory prefixes, e.g. `("scripts/", "app/")`) restricts the walk **while
    48	   keeping paths relative to `root`** — this is the p4 subset fallback; it must not change any
    49	   `rel_path`. `DEFAULT_INCLUDE` = the current `INCLUDE_EXT` list **plus** `.yml .yaml .toml .ini
    50	   .cfg .json .sql .html .twig` and the filenames `Dockerfile`, `docker-compose*.yml`, `Makefile`,
    51	   `*.blade.php`, `.env.example`. `DEFAULT_EXCLUDE` = `.git .venv node_modules __pycache__ dist build
    52	   temp .embed-tmp .xyz .relay-scratch marathon-system relay-system`. Skip files > 1 MiB and binary
    53	   files (NUL byte in the first 8 KiB). `root` must be an existing directory → else `ValueError`.
    54	   **Traversal errors are not exclusions:** an `OSError` from directory enumeration or from reading
    55	   a candidate file is appended to `errors` (a caller-supplied `list[str]`, required argument) with
    56	   the path, and the walk continues; skips by extension, size, binary sniff, `exclude_dirs` or
    57	   `include_prefixes` are intentional and are **not** recorded there. Callers that mutate an index
    58	   (p2 `Store.ingest`) must treat a non-empty `errors` as an incomplete walk and refuse to prune.
    59	2. `xyz/ingest/chunk.py` — a `Chunk` dataclass: `repo, path, kind, qualified_name, start_line,
    60	   end_line, text, embedded_text, content_sha` (`content_sha` = sha256 of `embedded_text`), and
    61	   `ChunkResult(chunks: list[Chunk], warnings: list[str])`. `embedded_text` **always begins with the
    62	   relative path on its own line**, then a blank line, then `text` (#8).
    63	   `chunk_file(repo, rel_path, source: bytes) -> ChunkResult` dispatches on extension:
    64	   - **Python, JS, TS/TSX/JSX, PHP** → Tree-sitter via `tree_sitter_language_pack.get_parser(lang)`.
    65	     One chunk per top-level function / class / method (methods become their own chunks with
    66	     `qualified_name = "Class.method"`); the file's remaining top-level statements (imports, module
    67	     docstring, constants) form one `kind="module"` chunk whose `start_line`/`end_line` are the first
    68	     and last line of that residual text and whose `text` joins the pieces with a `# …` gap marker.
    69	   - **Markdown** → one chunk per heading section (level ≤ 3); preamble before the first heading is
    70	     its own chunk; `qualified_name` = heading path joined with ` > `.
    71	   - **everything else** → file-level chunks, `kind="file"`, `qualified_name = rel_path`.
    72	   - **Hard bound, every kind:** any chunk whose `text` exceeds **6,000 characters** is split — at
    73	     the nearest blank line before the limit if one exists in the last 1,500 characters, otherwise
    74	     **hard-cut at 6,000** — into parts ≤ 6,000 chars with ~150-char overlap, each keeping the
    75	     `qualified_name` with a `#2`, `#3` suffix and correct `start_line`/`end_line`. A single-line
    76	     6,001-char file must still yield ≥ 2 chunks (this is a test).
    77	   - A parse failure never aborts ingest: fall back to the file-level chunker and append a warning.
    78	3. `xyz/ingest/__init__.py` exports `walk_repo`, `chunk_file`, and
    79	   `chunk_repo(repo, root, **walk_kwargs) -> ChunkResult` (all chunks + all warnings; p2's
    80	   `Store.ingest` reports the warnings). The p2 `IngestReport` is the one channel for warnings.
    81	4. Tests in `tests/test_chunkers.py` on a **fixture tree `tests/fixtures/mini-repo/`** that you
    82	   create: a Python file with module docstring, two functions and a class with two methods; a TS
    83	   file with an exported function and a class; a PHP file with a class; a Markdown file with three
    84	   headings; `config.yml`; `Dockerfile`; a binary blob; `node_modules/ignored.js`; a generated
    85	   single-line 6,001-char `.txt`; a generated Markdown section > 6,000 chars; a deliberately broken
    86	   Python file. Assert: chunk counts and `qualified_name`s per file; `start_line`/`end_line` match
    87	   the source; every `embedded_text` starts with `path + "\n\n"`; YAML and Dockerfile produce chunks
    88	   (#2); binary and `node_modules` produce none; both oversize cases split with suffixes and ≤ 6,000
    89	   chars each; the broken file yields a file-level chunk plus one warning; `include_prefixes`
    90	   restricts the walk without altering `rel_path`; a missing root raises; output is deterministic
    91	   (two runs equal); with `os.scandir` monkeypatched to raise `PermissionError` for one subdirectory
    92	   **after** at least one file was yielded, the walk still yields the other files and `errors` has
    93	   exactly one entry naming that subdirectory, while an excluded dir or a binary skip adds nothing
    94	   to `errors`.
    95	
    96	## Non-goals
    97	
    98	No embedding, no SQLite, no CLI. Do not modify `.embed-tmp/`.
    99	
   100	## Definition of done
   101	
   102	- `bash validate.sh` green; every assertion above present in `tests/test_chunkers.py`.
   103	- Red control (show once in the relay, then restore): remove the path-prefix line from
   104	  `embedded_text` → the prefix test fails; remove the hard-cut branch → the single-line 6,001-char
   105	  test fails.
     1	---
     2	title: GH-11 marathon brief — gh11-p2-store
     3	status: active
     4	created: 2026-09-05
     5	updated: 2026-09-06
     6	owner: Noel Saw
     7	goal: Phase brief consumed by marathon-drive.sh for phase gh11-p2-store; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
     8	roadmap_exempt: true
     9	---
    10	
    11	# Phase brief — gh11-p2-store: SQLite store (chunks + FTS5 + vec0), provider-keyed embed cache, drift guard
    12	
    13	## Status
    14	
    15	| What was just completed | What's next |
    16	|---|---|
    17	| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p2-store` after `gh11-p1-chunkers`; outcome recorded in the capture doc. |
    18	
    19	Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
    20	(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
    21	Canonical doc → "Phase 1", step 2 and step 4 (CodeRankEmbed as the placeholder dense lane).
    22	Environment contract: see `brief-p0-scaffold.md` (`XYZ_PY`, `XYZ_SCRATCH`, offline env, no installs).
    23	
    24	## Context you must read before coding
    25	
    26	- `SOP.md` → CodeRankEmbed: query prefix `"Represent this query for searching relevant code: "`
    27	  on **queries only**, documents raw; `trust_remote_code=True`; `TOKENIZERS_PARALLELISM=false`;
    28	  batch 16. `FINDINGS-0.5.md` (~174-179): **`max_seq_length = 2048` is the real memory guard** and
    29	  must be set explicitly on the loaded model (the old script never set it — this is a tested
    30	  requirement here). Model load ≈ 11.6 s → load once per process.
    31	- Issue #11 carve-out 1 (Ask-Self inheritance): the embed cache is keyed by
    32	  `(content_sha, model, dim, provider)` and an index refuses to be opened, extended **or queried**
    33	  by a different `(model, dim, provider)` — that guard caught real cross-provider cache poisoning.
    34	  Port the semantics; do not copy Ask-Self files. This file-sha planner + cache is the **only**
    35	  planner in XYZ; Act 2 reconciles Ask-Self's planner onto it, not beside it.
    36	- `sqlite-vec` and FTS5 are verified present in `XYZ_PY` by `validate.sh`'s env preflight.
    37	
    38	## Task
    39	
    40	Implement `xyz/index/`:
    41	
    42	1. `xyz/index/embed.py` — an `Embedder` protocol (`model_id`, `dim`, `provider`,
    43	   `encode_documents(texts) -> np.ndarray[float32]`, `encode_query(text) -> np.ndarray`) and
    44	   `CodeRankEmbedder` (`provider="sentence-transformers"`, `dim=768`, L2-normalised output, device
    45	   auto: MPS if available else CPU; `EMBED_BATCH_SIZE` / `EMBED_MAX_THREADS` env like the old
    46	   script). Constructor accepts an injectable `model_factory` so a test can pass a stub and assert:
    47	   `max_seq_length` was set to **2048**, `encode_query` prepends the exact prefix, and
    48	   `encode_documents` does **not**. `tests/fakes.py` provides `FakeEmbedder(model_id="fake",
    49	   dim=8, provider="fake")` (deterministic hash-based unit vectors, counts calls) used by every
    50	   store/retrieve test.
    51	2. `xyz/index/store.py` — `Store`, the **only writer** of an index:
    52	   - tables: `meta(key, value)` holding `model`, `dim`, `provider`, `schema_version`;
    53	     `files(repo, path, file_sha, chunk_count, ingested_at, PRIMARY KEY(repo, path))`;
    54	     `chunks(id INTEGER PRIMARY KEY, repo, path, kind, qualified_name, start_line, end_line,
    55	     content_sha, text, embedded_text)`; `chunks_fts` = FTS5 **external-content** table over
    56	     `chunks(embedded_text, qualified_name, path)` kept in sync by insert/delete/update triggers;
    57	     `chunks_vec` = `vec0(embedding float[<dim>])` with rowid = `chunks.id`;
    58	     `embed_cache(content_sha, model, dim, provider, vector BLOB, PRIMARY KEY(content_sha, model,
    59	     dim, provider))`.
    60	   - `Store.open(db_path, embedder)`: creates the schema on first use and writes `meta`; on an
    61	     existing DB raises `IndexMismatch` naming the differing field if **any** of `model`, `dim`,
    62	     `provider` differ. `Store.check_embedder(embedder)` exposes the same check for readers (p3).
    63	   - `Store.ingest(repo, root, chunker=chunk_repo, include_prefixes=None) -> IngestReport`, the
    64	     planner: **walk first, mutate second.** Run the p1 walk (honouring `include_prefixes`) to
    65	     completion into an in-memory list of `(rel_path, bytes)` with an `errors` list; a walk that
    66	     yields **zero files raises `EmptyCorpus`**, and a walk with **any traversal error raises
    67	     `WalkIncomplete`** (listing the errors) — both **before any write or delete**. Only a complete
    68	     walk may proceed. For each file compute `file_sha`; same sha in `files` → skip;
    69	     else delete that file's chunks (FTS/vec rows via triggers/explicit delete) and insert the new
    70	     ones. Embed only chunks whose `content_sha` is absent from `embed_cache` for this
    71	     `(model, dim, provider)`; cache every new vector. **Pruning is scoped:** files in `files` for
    72	     this `repo` that are absent from the walk are pruned only when they fall under the walked scope
    73	     (all of the repo when `include_prefixes` is None, else only under those prefixes).
    74	     `IngestReport` carries `files_seen, files_skipped, files_reingested, files_pruned,
    75	     chunks_written, chunks_embedded, cache_hits, warnings, seconds`.
    76	   - `Store.stats()` → row counts of `chunks`, `chunks_fts` (via `SELECT count(*) FROM chunks_fts`),
    77	     `chunks_vec`, `embed_cache`, `files`; `Store.fts_match(token, limit)` → chunk ids whose FTS row
    78	     matches (used by tests to prove the inverted index, not just the row count, is current).
    79	   - One transaction per file; WAL journal mode; `PRAGMA foreign_keys=ON`.
    80	3. Tests in `tests/test_store.py` with `FakeEmbedder` on the p1 fixture copied to a tmp dir:
    81	   - first ingest: `chunks_embedded == chunks_written > 0`; `chunks`, `chunks_fts`, `chunks_vec`
    82	     counts equal; `fts_match` finds a token that exists only in one fixture file;
    83	   - **second ingest, unchanged tree: `files_skipped == files_seen`, `files_reingested == 0`,
    84	     `chunks_written == 0`, embedder call count 0, < 1 s** (all five asserted separately — the
    85	     red control below depends on it);
    86	   - in one fixture file, **replace** the unique token `OLDTOKEN` (present in exactly one chunk)
    87	     with `NEWTOKEN`, leaving that file's other chunks byte-identical: only that file is re-ingested
    88	     (`files_reingested == 1`), its unchanged chunks are cache hits (embedder called once, for the
    89	     changed chunk), `fts_match("NEWTOKEN")` returns that chunk and `fts_match("OLDTOKEN")` is empty;
    90	   - delete one file: its chunks vanish from all three tables and `fts_match` of its unique token is
    91	     empty; with `include_prefixes` naming a different directory, that deleted file is **not** pruned;
    92	   - an empty directory raises `EmptyCorpus` and writes nothing;
    93	   - **incomplete walk:** after a full ingest, monkeypatch `os.scandir` to raise `PermissionError`
    94	     for one subdirectory (after other files have been yielded) → `ingest` raises `WalkIncomplete`,
    95	     and every pre-existing `chunks` / `chunks_fts` / `chunks_vec` / `files` row survives unchanged
    96	     (counts and `fts_match` of a token from the unreadable subdirectory still succeed);
    97	   - `IndexMismatch` is raised separately for a differing `model_id`, a differing `dim`, and a
    98	     differing `provider` (three tests);
    99	   - a chunk's vector read back from `chunks_vec` equals its cached vector;
   100	   - `CodeRankEmbedder` with the stub factory: `max_seq_length == 2048`, query prefix present on
   101	     queries only.
   102	
   103	## Non-goals
   104	
   105	No query path (p3), no CLI (p4). No real model in pytest.
   106	
   107	## Definition of done
   108	
   109	- `bash validate.sh` green; every test above present and passing.
   110	- One real smoke, out of pytest and under the offline env: `CodeRankEmbedder().encode_query("sort a
   111	  list")` → shape `(768,)`, norm ≈ 1.0, and `model.max_seq_length == 2048` — quote all three.
   112	- Red controls (show once each in the relay, then restore): (a) remove the `files` sha
   113	  short-circuit → the `files_skipped == files_seen` / `files_reingested == 0` assertions fail even
   114	  though the cache still keeps embedder calls at 0; (b) drop the FTS insert trigger → the
   115	  `fts_match("NEWTOKEN")` test fails while the count test may still pass; (c) disable the
   116	  `WalkIncomplete` guard (ignore `errors`) → the incomplete-walk test fails because the unreadable
   117	  subdirectory's rows get pruned.

exec
/bin/zsh -lc 'nl -ba PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md; nl -ba PROJECT/2-WORKING/v0.5/GH-11-marathon/MARATHON.yaml' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
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
    40	| Codex plan review rounds 1-4: 14 findings implemented; r4 bound the readiness marker to the libraries' resolved HF cache constants (2026-09-06). | **Blocked on operator decision:** relay at its extended 4-round cap, `STATUS: Escalated`. Extend to round 5 for the cache-fingerprint fix, or accept the plan and fire. |
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
     1	# GH-11 Act 1 — XYZ hybrid retrieval library (canonical doc Phase 0 + Phase 1).
     2	# Run from the target repo root:
     3	#   ./.xyz/relay-automation/marathon.sh --plan PROJECT/2-WORKING/v0.5/GH-11-marathon/MARATHON.yaml
     4	# Builder is codex (marathon.sh default), so every reviewer is agy (builder != reviewer required).
     5	# Phase ids are globally unique (gh11-*) so lane state never collides in .tick/attempts/.
     6	# Execution surface of record: PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md
     7	
     8	name: gh11-act1-hybrid-retrieval
     9	phases:
    10	  - id: gh11-p0-scaffold
    11	    name: "p0: Phase 0 close-out — constraints, pyproject, xyz/ skeleton, validate.sh"
    12	    reviewer: agy
    13	    brief: PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p0-scaffold.md
    14	    artifact: GUIDING-PRINCIPLES.md,pyproject.toml,validate.sh,xyz/,tests/
    15	    turn_timeout_s: 1200
    16	    max_review_rounds: 2
    17	
    18	  - id: gh11-p1-chunkers
    19	    name: "p1: Tree-sitter / Markdown / file-level chunkers with path-prefixed text"
    20	    reviewer: agy
    21	    brief: PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p1-chunkers.md
    22	    artifact: xyz/,tests/,pyproject.toml
    23	    depends_on: gh11-p0-scaffold
    24	    turn_timeout_s: 1800
    25	    max_review_rounds: 3
    26	
    27	  - id: gh11-p2-store
    28	    name: "p2: SQLite store — chunks + FTS5 + vec0, provider-keyed embed cache, drift guard"
    29	    reviewer: agy
    30	    brief: PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p2-store.md
    31	    artifact: xyz/,tests/,pyproject.toml
    32	    depends_on: gh11-p1-chunkers
    33	    turn_timeout_s: 1800
    34	    max_review_rounds: 3
    35	
    36	  - id: gh11-p3-retrieve
    37	    name: "p3: BM25 + dense -> RRF -> cross-encoder rerank -> tau, with latency instrumentation"
    38	    reviewer: agy
    39	    brief: PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p3-retrieve.md
    40	    artifact: xyz/,tests/,pyproject.toml
    41	    depends_on: gh11-p2-store
    42	    turn_timeout_s: 1800
    43	    max_review_rounds: 3
    44	
    45	  - id: gh11-p4-roundtrip
    46	    name: "p4: xyz CLI + real ingest/query round-trip on LTVera-Pandas, scored and recorded"
    47	    reviewer: agy
    48	    brief: PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p4-roundtrip-eval.md
    49	    artifact: xyz/,tests/,pyproject.toml,PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md,PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md
    50	    depends_on: gh11-p3-retrieve
    51	    turn_timeout_s: 7200
    52	    max_review_rounds: 3

exec
/bin/zsh -lc 'for f in PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p3-retrieve.md PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p4-roundtrip-eval.md validate.sh prelaunch.sh; do nl -ba "$f"; done' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
 succeeded in 0ms:
     1	---
     2	title: GH-11 marathon brief — gh11-p3-retrieve
     3	status: active
     4	created: 2026-09-05
     5	updated: 2026-09-06
     6	owner: Noel Saw
     7	goal: Phase brief consumed by marathon-drive.sh for phase gh11-p3-retrieve; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
     8	roadmap_exempt: true
     9	---
    10	
    11	# Phase brief — gh11-p3-retrieve: BM25 ∥ dense → RRF → cross-encoder rerank → τ, instrumented
    12	
    13	## Status
    14	
    15	| What was just completed | What's next |
    16	|---|---|
    17	| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p3-retrieve` after `gh11-p2-store`; outcome recorded in the capture doc. |
    18	
    19	Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
    20	(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
    21	Canonical doc → "Phase 1", step 3: *parallel BM25 + dense → RRF(k=60) → cross-encoder rerank top
    22	25-50 → no-answer threshold τ*.
    23	Environment contract: see `brief-p0-scaffold.md` (`XYZ_PY`, `XYZ_SCRATCH`, offline env, no installs).
    24	
    25	## Context you must read before coding
    26	
    27	- `xyz/index/store.py` from p2 — query through the `Store`; do not open the SQLite file elsewhere.
    28	- **`vec0` KNN must use the `k = ?` bound form** (`WHERE embedding MATCH ? AND k = ?`), never a
    29	  parameterised `LIMIT ?` — Ask-Self issue #23: `LIMIT ?` was rejected at prepare time on stricter
    30	  sqlite-vec builds and 500'd in production. This is a tested requirement.
    31	- FTS5 ranking: the built-in `bm25()` function (lower = better) via `ORDER BY bm25(chunks_fts)`.
    32	  Sanitise the query for FTS5 syntax (quote tokens; strip operators) so a query containing `-` or
    33	  `:` cannot raise; an all-stopword/empty sanitised query returns no BM25 hits, not an error.
    34	- Reranker default: **`mixedbread-ai/mxbai-rerank-xsmall-v1`** (Apache-2.0, ~70 MB, in the HF cache,
    35	  loaded via `sentence_transformers.CrossEncoder(..., trust_remote_code=True)`), read from
    36	  `XYZ_RERANKER` with that default. It is a placeholder — keep it injectable; the bake-off
    37	  (canonical Phase 3) picks the real one. Fallback if it misbehaves: `BAAI/bge-reranker-base` (MIT,
    38	  also cached and verified).
    39	  **Do not use `cross-encoder/ms-marco-MiniLM-L-6-v2`** — measured 2026-09-06 on this stack
    40	  (torch 2.14.0, transformers 5.16.1): it loads without error and returns **`[nan, nan]`** logits
    41	  (old-format BERT checkpoint; reproduced with plain `AutoModelForSequenceClassification` under both
    42	  `eager` and `sdpa` attention, checkpoint tensors all finite). `prelaunch.sh` now asserts the
    43	  reranker's scores are finite *and* rank a code snippet above unrelated SQL, so this cannot pass
    44	  silently again.
    45	
    46	## Task
    47	
    48	Implement `xyz/retrieve/`:
    49	
    50	   **Score contract for every lane and stage: higher is better.**
    51	1. `xyz/retrieve/lexical.py` — `bm25_search(store, query, k) -> list[Hit]` (`Hit`: `chunk_id,
    52	   score, stage`) with **`score = -bm25(chunks_fts)`** (FTS5's bm25 is lower-is-better; negate it),
    53	   the FTS5 sanitiser, and unit tests including one where a chunk with more query-term matches gets
    54	   the higher `score`.
    55	2. `xyz/retrieve/dense.py` — `dense_search(store, query_vec, k) -> list[Hit]` using `vec0` with
    56	   `k = ?`; `score = -distance`; expose the SQL string as a module constant `KNN_SQL` so the test can
    57	   assert on it.
    58	3. `xyz/retrieve/fuse.py` — `rrf(rankings: list[list[Hit]], k=60) -> list[Hit]`:
    59	   `score = Σ 1 / (k + rank_i)`; deterministic tie-break by `chunk_id`.
    60	4. `xyz/retrieve/rerank.py` — a `Reranker` protocol (`score(query, texts) -> list[float]`),
    61	   `CrossEncoderReranker`, and `FakeReranker` in `tests/fakes.py` (scores from a dict, default 0).
    62	5. `xyz/retrieve/pipeline.py` — `Retriever(store, embedder, reranker=None)`:
    63	   - the constructor calls `store.check_embedder(embedder)` → `IndexMismatch` on a wrong embedder
    64	     (query-time guard; tested for model, dim, provider);
    65	   - `search(query, k=10, fetch_k=50, mode="auto", tau=None) -> SearchResult` with
    66	     `mode ∈ auto | dense | bm25 | hybrid | hybrid+rerank`; `auto` resolves to `hybrid+rerank` when a
    67	     reranker is present else `hybrid`; an explicit `hybrid` never reranks; `hybrid+rerank` without
    68	     a reranker raises `ValueError`;
    69	   - **Candidate policy (explicit, tested):** dense and BM25 each fetch `fetch_k`; their union is
    70	     fused by RRF and **truncated to `fetch_k`** (the depth `D`); in `hybrid+rerank` the reranker
    71	     rescores only the first `min(D, 50)` of that list and reorders **them**; the remaining tail
    72	     (positions 51..D) is **appended unchanged in RRF order** — reranker scores are never compared
    73	     with RRF scores. `SearchResult.ranking` is the resulting ordered list of `(chunk_id, path)`
    74	     pairs of length ≤ D; the top `k` are returned with chunk rows;
    75	   - `tau` semantics per mode: compared against the top reranker score in `hybrid+rerank`, the top
    76	     RRF score in `hybrid`, the top lane score in `dense` / `bm25` (all higher-is-better); below it
    77	     → `no_answer=True`, `hits=[]`, `ranking` still populated. An empty candidate set is
    78	     `no_answer=True` regardless of τ;
    79	   - `SearchResult.timings` = per-stage milliseconds (`embed_query, bm25, dense, fuse, rerank,
    80	     total`; stages not run report 0.0).
    81	   - `xyz/retrieve/latency.py` — `LatencyLog` collecting `timings` and reporting p50 / p95 per stage.
    82	6. Tests in `tests/test_retrieve.py` on a store built with `FakeEmbedder` from the p1 fixture:
    83	   - `rrf` reproduces a hand-computed fusion for two 3-item lists with one overlap;
    84	   - a chunk ranked last by both lanes but scored highest by `FakeReranker` ends at rank 1 in
    85	     `hybrid+rerank` and **not** in `hybrid` (the "rerank measurably reorders RRF output" gate in
    86	     miniature);
    87	   - `KNN_SQL` contains the literal ` k = ?` and does not contain `LIMIT ?`;
    88	   - `"foo-bar: baz*"` and `""` do not raise in `bm25_search`;
    89	   - BM25 sign (score direction only): a chunk matching two query terms scores higher than one
    90	     matching one;
    91	   - τ is a **query-level** decision, not a per-hit filter — two searches prove it: (a) top score
    92	     above τ → `no_answer=False` and the result **still contains the below-τ secondary hit**;
    93	     (b) a query whose top score falls below τ → `no_answer=True`, `hits=[]`. Same store, τ chosen
    94	     between the two candidates' scores in case (a);
    95	   - `tau` above every score → `no_answer=True`, empty hits, non-empty `ranking`; `tau=None` never
    96	     yields `no_answer` **when at least one candidate exists**; `mode="hybrid+rerank"` with no
    97	     reranker raises; `mode="auto"` picks per the rule;
    98	   - candidate policy on a fixture large enough that the two-lane union exceeds `fetch_k`
    99	     (generate ≥ 120 small chunks): `ranking` has exactly `fetch_k` entries; a chunk placed at RRF
   100	     position 75 with `fetch_k=100` is present at position 75 after `hybrid+rerank` (tail untouched)
   101	     and absent with `fetch_k=50`; with `FakeReranker` swapping two chunks **of the same path**, the
   102	     two `ranking` lists differ by chunk id even though their path sequences are identical;
   103	   - `Retriever(store, FakeEmbedder(model_id="other"))` raises `IndexMismatch` (and likewise for
   104	     `dim`, `provider`);
   105	   - every `timings` key present and ≥ 0; `LatencyLog` p50/p95 over ≥ 3 searches.
   106	
   107	## Non-goals
   108	
   109	No CLI, no real-corpus run, no reranker bake-off. Read-only helpers in `xyz/index/` only if
   110	genuinely needed (say so in the relay).
   111	
   112	## Definition of done
   113	
   114	- `bash validate.sh` green; every test above present and passing.
   115	- One real smoke, out of pytest, offline env: `CrossEncoderReranker().score("sort a list in python",
   116	  ["def sort_list(lst):\n    return sorted(lst)", "SELECT 1 FROM dual"])` → two **finite** floats
   117	  with the code snippet higher (expected ≈ 0.597 vs 0.017 for the default model); quote them. A NaN
   118	  here is a hard stop, not a warning.
   119	- Red control: swap `k = ?` for `LIMIT ?` in `dense.py`, confirm the `KNN_SQL` test fails, restore.
     1	---
     2	title: GH-11 marathon brief — gh11-p4-roundtrip
     3	status: active
     4	created: 2026-09-05
     5	updated: 2026-09-06
     6	owner: Noel Saw
     7	goal: Phase brief consumed by marathon-drive.sh for phase gh11-p4-roundtrip; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
     8	roadmap_exempt: true
     9	---
    10	
    11	# Phase brief — gh11-p4-roundtrip: `xyz` CLI + real ingest/query round-trip on LTVera-Pandas, scored
    12	
    13	## Status
    14	
    15	| What was just completed | What's next |
    16	|---|---|
    17	| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p4-roundtrip` after `gh11-p3-retrieve`; results land in FINDINGS-0.5.md and the capture doc. |
    18	
    19	Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
    20	(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
    21	Canonical doc → "Phase 1" **QA gate**: *ingest + query round-trip on one real repo; unchanged
    22	re-ingest is near-instant (planner dedupe works); rerank stage measurably reorders RRF output;
    23	latency instrumented (p50/p95).*
    24	Environment contract: see `brief-p0-scaffold.md`. This phase additionally needs **`XYZ_EVAL_REPO`**
    25	(absolute path to a LTVera-Pandas checkout, set by the operator). First thing in the turn:
    26	`test -d "$XYZ_EVAL_REPO/scripts" && test -d "$XYZ_EVAL_REPO/app"` — if that fails, stop and report;
    27	do not guess a path.
    28	
    29	## Context you must read before coding
    30	
    31	- `.embed-tmp/eval/score_retrieval.py` — the metric definitions: a hit is a retrieved chunk whose
    32	  `path` is in the query's `relevant` list (lines ~133-138); MRR = mean of 1/rank-of-first-hit with
    33	  misses contributing 0; recall@k for k ∈ {1, 3, 5, 10}; `never_found`; `per_query` (~141-156).
    34	  **Depth differs and must be stated:** that scorer ranks the *entire* corpus (a hit at rank 11
    35	  still contributes 1/11), whereas this pipeline ranks `fetch_k` candidates. So this phase reports
    36	  **MRR@D / R@k / miss@D at an explicit depth D = 100** (`fetch_k=100` per lane; ranks past 100 count
    37	  as misses) and produces its own dense-only arm at the same depth as the comparison baseline.
    38	  BENCHMARKS.md Run 9 (MRR 0.801 / R@1 0.700, full-corpus ranking, old chunker) is quoted for
    39	  context only and is **not** equated with any number here.
    40	- `.embed-tmp/eval/queries-LTVera-Pandas.json` — the 30 labelled queries. Saturated (issue #11
    41	  caveat 2); deltas under 0.05 are noise (GH-5 doc) — report, don't over-claim.
    42	- Corpus size: Run 9 used 5,147 chunks; the p1 chunker (wider include list, AST chunks) will
    43	  produce a different count. Embedding on MPS ≈ 0.3 s/chunk ⇒ **25-35 minutes** for the full tree;
    44	  turn timeout is 7200 s.
    45	- Scratch: every generated file (index DB, eval JSON, timing logs) goes under `$XYZ_SCRATCH`
    46	  (default `.relay-scratch/`, swept by the harness). Nothing under `temp/`.
    47	
    48	## Task
    49	
    50	1. `xyz/eval/metrics.py` — `score(rankings: dict[query -> list[tuple[chunk_id, path]]], queries,
    51	   depth) -> Report`. The input is the ordered `(chunk_id, path)` records `SearchResult.ranking`
    52	   already returns (p3) — **never bare paths**, because two chunks of one file share a path and ids
    53	   cannot be recovered from it (and must never be fabricated from rank position). Relevance is
    54	   judged on the `path` half only; the `chunk_id` half is carried through to serialization. Ranks
    55	   are **chunk ranks** (the first chunk whose path is relevant; paths are not de-duplicated before
    56	   ranking); JSON writer with keys `mrr,
    57	   recall@1, recall@3, recall@5, recall@10, never_found, depth, per_query`, where each `per_query`
    58	   row carries `q, relevant, rank, top_hit` **and `ranking` — the ordered list of
    59	   `{chunk_id, path}` objects up to `depth`** (chunk ids make same-path reorders visible).
    60	   `score()` raises `ValueError` on an empty query list. Unit tests: a hand-built 3-query case; a
    61	   case where the only relevant chunk sits at rank 11 with `depth=10` → miss, and with `depth=100`
    62	   → 1/11; and a **round-trip** case where two distinct `chunk_id`s share one `path` — after
    63	   `score()` and JSON serialization both ids survive in order, so a same-path reorder is still
    64	   visible downstream.
    65	2. `xyz/cli.py` subcommands (argparse; `main(argv)` returns an int; `python -m xyz` works via
    66	   `xyz/__main__.py` from p0):
    67	   - `xyz ingest --db DB --repo NAME PATH [--include-prefix P ...]` → `Store.ingest`
    68	     (prefixes → `include_prefixes`), prints the `IngestReport`, `Store.stats()`, and peak RSS
    69	     (`resource.getrusage`); a missing / non-directory `PATH` or `EmptyCorpus` → exit 2 with a
    70	     message;
    71	   - `xyz query --db DB [--mode auto|dense|bm25|hybrid|hybrid+rerank] [--k N] [--tau T] "text"` →
    72	     rank, path, qualified_name, lines, score, per-stage timings;
    73	   - `xyz eval --db DB --queries FILE --modes dense,bm25,hybrid,hybrid+rerank --depth 100 --out JSON`
    74	     → before scoring, **assert the corpus is non-empty and that every gold path in the query file
    75	     exists in `chunks.path`** (else exit 2 listing the missing paths); run every mode; write one
    76	     report per mode plus `latency` (p50/p95 per stage per mode) and `corpus` (chunk count, file
    77	     count, `include_prefixes` used, DB path); print a comparison table and the **reorder count**:
    78	     the number of queries whose top-10 `ranking` **chunk-id sequence** differs between `hybrid` and
    79	     `hybrid+rerank` (unit-tested with a fake reranker that swaps two chunks of one path → counted).
    80	   CLI tests in `tests/test_cli.py` with the fakes on the fixture tree: ingest → query → eval end to
    81	   end; ingest twice shows `chunks_embedded == 0`; an empty query file → exit 2; a query file with a
    82	   gold path absent from the corpus → exit 2; a bogus `PATH` → exit 2.
    83	3. **The real round-trip** (the gate; keep every number):
    84	   1. `time "$XYZ_PY" -u -m xyz ingest --db "$XYZ_SCRATCH/LTVera-Pandas.sqlite" --repo LTVera-Pandas "$XYZ_EVAL_REPO"`
    85	      — record wall time, `files_seen`, `chunks_written`, `chunks_embedded`, peak RSS. **Early
    86	      estimate:** after the first 200 chunks are embedded, the CLI prints an ETA; if the ETA exceeds
    87	      **45 minutes**, abort and use the fallback.
    88	   2. **Fallback (only if triggered, and say so):** a **fresh** DB `"$XYZ_SCRATCH/LTVera-Pandas-subset.sqlite"`
    89	      with `--include-prefix scripts/ --include-prefix app/ --include-prefix alembic/` in **one**
    90	      invocation (root-preserving; every gold path lives under those prefixes). Results from a
    91	      subset are labelled `corpus: subset` everywhere they are reported.
    92	   3. Run the same ingest command again — record wall time and `chunks_embedded` (**must be 0**,
    93	      seconds not minutes).
    94	   4. `xyz eval` at depth 100 for all four modes; record MRR@100 / R@1 / R@3 / R@5 / R@10 /
    95	      miss@100 per mode, p50/p95 per stage, and the reorder count.
    96	4. **Record the results** — append a dated **"Run: XYZ hybrid retrieval round-trip (GH-11 Act 1)"**
    97	   section to `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md` with the corpus provenance (full or subset,
    98	   chunk/file counts, chunker version = this commit), the table from step 3, and the four Phase 1
    99	   QA-gate bullets each marked met / not met with the number that shows it; update the `## Status`
   100	   table and `## Run log` of `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`. Do not renumber
   101	   or edit earlier runs; do not touch `.embed-tmp/BENCHMARKS.md`; do not commit anything from
   102	   `$XYZ_SCRATCH`.
   103	
   104	## Non-goals
   105	
   106	No Slack/HTTP/MCP surface. No model or reranker comparison beyond the four modes. No changes to
   107	`.embed-tmp/`. No `CHANGELOG.md` entry (orchestrator, at PR time).
   108	
   109	## Definition of done
   110	
   111	- `bash validate.sh` green (pytest uses fakes only — the real run is **not** in pytest).
   112	- All four Phase 1 QA-gate bullets evidenced with numbers in FINDINGS-0.5.md: round-trip done
   113	  (full or labelled subset); second ingest `chunks_embedded == 0` and < 30 s; reorder count ≥ 1;
   114	  p50/p95 recorded per stage.
   115	- Acceptance from the capture doc: at depth 100, `hybrid+rerank` MRR@100 and R@1 ≥ the `dense`
   116	  arm's MRR@100 and R@1 − 0.05, on the same DB. If lower, the phase is **not** approved — report the
   117	  numbers and the most likely cause (reranker choice, BM25 sanitiser, fusion depth); do not tune
   118	  against the labelled set.
   119	- Red controls (show once in the relay): `xyz eval` with an empty query file exits 2; the
   120	  rank-11 metric test flips between miss and 1/11 with `depth`.
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

exec
/bin/zsh -lc 'nl -ba relay-system/2026-09-06/gh11-act1-plan-review.md' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
 succeeded in 0ms:
     1	# RELAY · GH-11 Act 1 plan review — hybrid retrieval marathon
     2	<!--
     3	  Single source of truth for this two-agent relay. Read the ENTIRE file before acting.
     4	  Scaffolded by relay-automation/new-relay.sh on 2026-09-06.
     5	-->
     6	
     7	NEXT: Producer
     8	STATUS: Escalated
     9	ROUND: 4 / 4
    10	
    11	## ▶ TAKE YOUR TURN — read this first (works for ANY agent: Claude, Codex, agy)
    12	1. **Read this whole file** (header, Setup, Ground rules, every block in the Log).
    13	2. **Check it's your turn:** `NEXT` (top) names the role to act. Confirm you are bound to it and the
    14	   last Log block isn't already yours. If not → STOP and reply "wrong window — nudge the <other> window."
    15	3. **Do your role's work** on the artifact named in Setup:
    16	   - **Reviewer:** review vs the Definition of Done → graded findings
    17	     (`[Blocker]`/`[Should]`/`[Nit]`/`[Pass]`), each with a concrete fix → set a **Verdict**
    18	     (Approved | Changes requested | Blocked). **Review the whole file, not just the diff** (GH-268):
    19	     a beta test had this loop reach `Approved` in two rounds while an independent audit of the same
    20	     branch found 20 issues (1 critical, 4 high) — every one of them in the pre-existing code the
    21	     change sat on, which nobody had read. Pre-existing defects in a file you are touching are IN
    22	     SCOPE; if you find none, say so explicitly rather than leaving it unstated.
    23	     **Declare it: every review block must contain a literal `swept file: yes` or `swept file: no`
    24	     line.** Without it a reviewer that skipped the sweep is indistinguishable in the transcript from
    25	     one that did it and found nothing — which is how the original 20 issues stayed invisible.
    26	     Any `[Pass]` or "verified"/"confirmed" finding MUST
    27	     carry a quoted span or a `file:line` citation — an uncited one is mechanically downgraded to
    28	     `[Unverified — no citation]` (GH-173 B3). Do **not** edit the artifact; only append findings here.
    29	   - **Producer:** log a disposition for every open finding (Implemented / Modified / Declined + why),
    30	     make the change, then add new work.
    31	4. **Append ONE block** at the very bottom, directly **above** the marker line. Never edit earlier turns.
    32	5. **Update the header:** flip `NEXT`; set `STATUS` (`Approved` closes — Reviewer only; else `Open`);
    33	   the Producer bumps `ROUND` when opening a new cycle. If the max `ROUND` ends without `Approved`,
    34	   set `STATUS: Escalated`.
    35	6. **Commit only the relay file** (`relay(gh11-act1-plan-review): <role> r<N>`); no push. **Stop** and report one line.
    36	7. **Hand off explicitly — EVERY turn, not just the first** (GH-268). End your turn by naming who acts
    37	   next and what they should do: *"handing off to <other role> — go to the <other> window and say
    38	   'take your turn'"*, or *"relay closed (Approved), no further turn needed"*. The beta report singled
    39	   this out: the Reviewer turn never told the user to return to the Producer window, so a relay that
    40	   was merely waiting looked stalled. A turn that ends without this line is not finished.
    41	
    42	## Setup
    43	- Artifact under review: **PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md** (the plan) plus
    44	  the marathon it drives — `PROJECT/2-WORKING/v0.5/GH-11-marathon/MARATHON.yaml` and its five briefs
    45	  `brief-p0-scaffold.md`, `brief-p1-chunkers.md`, `brief-p2-store.md`, `brief-p3-retrieve.md`,
    46	  `brief-p4-roundtrip-eval.md` — and the gate `validate.sh`. All are committed on this branch; read
    47	  them in the worktree. Requirements source: GitHub issue #11 "Act 1" section
    48	  (https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11) and the canonical doc's Phase 0-1
    49	  (`PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md`).
    50	  Ground-truth code the plan cites: `.embed-tmp/scripts/embed_repos.py`,
    51	  `.embed-tmp/eval/score_retrieval.py`, `.embed-tmp/eval/queries-LTVera-Pandas.json`, `SOP.md`,
    52	  `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md`.
    53	- Reviewer: codex   ·   Producer: claude-a
    54	- Started: 2026-09-06
    55	- Definition of Done: this is a PLAN review (no code exists yet — `xyz/` is created by the marathon).
    56	  Approve only if every question below is answered "yes" with a citation, else request changes:
    57	  1. Grounding — are the plan's claims about existing paths/behaviour true (chunk fields in
    58	     `embed_repos.py`, metric definitions in `score_retrieval.py`, the query-prefix / `max_seq_length`
    59	     / `k = ?` rules)? Cite `file:line`.
    60	  2. Completeness — does the five-phase plan cover every Act 1 checklist item of issue #11 and every
    61	     step of canonical Phase 0 (2-3) and Phase 1 (1-4), with each deviation stated under
    62	     "Acceptance — deviations from the issue" with a reason?
    63	  3. Surgical / DRY — does it extend the existing subsystem (one `xyz/` package, one SQLite writer
    64	     `xyz/index/store.py`) without a second embedder/scorer/store, and leave `.embed-tmp/` untouched?
    65	  4. Dependency ordering and blast radius — is the p0→p4 chain right, are the `artifact:` allowlists
    66	     per phase sufficient for the work the briefs demand (a builder cannot touch paths outside them),
    67	     and is rollback stated?
    68	  5. Falsifiable checks — does every phase have a gate that detects the actual failure, rejects empty
    69	     input where relevant (p4 eval on an empty query list), and names a red control?
    70	  6. Risks — is the p4 real-corpus run (25-30 min embedding inside a 7200 s turn, no network,
    71	     `HF_HUB_OFFLINE=1`) realistic, and is the fallback acceptable?
    72	  7. Rating — is `rated 85/60/50/30` (pri/sev/appeal/effort-cheapness, 1-100) grounded in the stated
    73	     rationale, appeal neutral (50) with no user preference given, and no override invented?
    74	  Grade every finding `[Blocker]` / `[Should]` / `[Nit]` / `[Pass]`; every `[Pass]` needs a citation.
    75	
    76	## Ground rules
    77	1. This file is the single source of truth. The agents never share memory — read the whole file.
    78	2. Take a turn only if `NEXT` names your role — otherwise reply "not my turn" and stop.
    79	3. One turn = one block appended at the very bottom, above the marker. Never edit earlier turns.
    80	4. Stay tight — findings are bullets, not essays. Grade every finding.
    81	5. **The Reviewer never edits the artifact.** It proposes graded findings; the Producer implements.
    82	6. The relay ends on **Approved** (Reviewer only). End each turn by committing just this file; no push.
    83	
    84	## Log
    85	
    86	## Reviewer — codex — Round 1 — 2026-09-06
    87	
    88	Verdict: Changes requested
    89	swept file: yes
    90	
    91	Read the whole plan, MARATHON.yaml, all five briefs, and validate.sh, including their pre-existing content. Read the cited embedder/scorer/query set and relevant canonical/SOP/findings evidence; fetched issue #11 with `gh issue view 11 --repo HiQS-Labs/XYZ-code-intelligence --json body`. No graph tools were available; direct source inspection is the evidence tier here. No artifact/source execution, project gates, model runs, or git commands were performed. Findings include pre-existing gate defects, not only proposed additions. Reversibility of this review-only edit: Easy.
    92	
    93	Citation shorthand below: `plan` = `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`; `p0`–`p4` = the corresponding `brief-p*.md` in `PROJECT/2-WORKING/v0.5/GH-11-marathon/` (p4 is `brief-p4-roundtrip-eval.md`); `canonical` = `PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md`.
    94	
    95	- [Blocker] **The promised exact metrics cannot be reproduced from the specified retrieval depth.** `.embed-tmp/eval/score_retrieval.py:133-155` ranks the entire corpus: a relevant result at rank 11 contributes 1/11 to MRR and is not `never_found`. p3:51-55 returns 10 hits from 50 candidates; p4:27-31,44-48 promises identical definitions without specifying eval depth. Its reference `per_query` row only contains query/relevant/rank/top_hit (`score_retrieval.py:147-148`), so it also cannot establish the top-10 reorder count requested at p4:67-68. **Fix:** explicitly define and test ranking depth per mode; either reproduce full-ranking metrics or call them MRR@10/miss@10 and rescore the baseline at that cutoff, recording the deviation. Add ordered chunk IDs/paths to per-query evidence and a rank-11 red case; preserve chunk ranks rather than deduplicating paths silently.
    96	- [Blocker] **Offline execution prerequisites are not specified for the actual worktree.** p0:26-31 assumes `.venv/` exists; p4:34-40 assumes a sibling corpus; p4:61 expands an env var without establishing its claimed default. Read-only `ls -ld` this turn found `.venv`, `.venv/bin/python`, and `../LTVera-Pandas` absent in this worktree, while `/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv` and `/Users/noelsaw/Documents/GH Repos/LTVera-Pandas` exist. `validate.sh:8` exports offline mode only inside that child shell, not into subsequent real smokes/CLI invocations. **Fix:** name the harness provisioning step and explicit interpreter/corpus env contract, check it in the builder worktree before starting, and export offline settings at the turn/command level. Include offline pip/setuptools and grammar/model-cache readiness in that preflight. Do not infer installed/parser/model readiness from a parent venv directory's existence.
    97	- [Blocker] **The smaller-corpus fallback is not executable safely as specified.** p4:37-39 asks for three subtrees, but p4:50 exposes only one root. Ingesting each subtree under the same repo name changes gold-relative paths and p2:61's pruning removes the earlier subtree's records. **Fix:** specify one root-preserving filtered walk (or one staged root preserving all three prefixes), a separate clean DB and explicit command. Reject missing/non-directory roots and incomplete walks before pruning; scope deletion to the requested repo. Require nonzero corpus counts and gold-path presence before scoring. Record candidate counts and reduced-corpus provenance; do not equate its score with full-corpus Run 9. The 7200-second budget (`MARATHON.yaml:51`) is plausible against the historical 1,529.9-second run (`FINDINGS-0.5.md`, table row “LTVera-Pandas, 5,147 chunks”), but the new chunker/wider walk needs a measured early estimate and fallback trigger.
    98	- [Blocker] **Red controls and FTS checks can stay green with the defect present.** p0:82-83 removes `xyz/__init__.py`, but `validate.sh:20` accepts a namespace package and prints `?` when the version is missing. p2:87-88 removes the file-SHA shortcut, yet the independently specified embed cache (p2:59-60) still yields zero embedder calls. Also, counts from an external-content FTS table (p2:50-51,64-73) do not establish that its inverted index was updated. **Fix:** make the import smoke assert the exact version; make p2's red control assert file-skip/chunker/write counts, not merely encode calls; add MATCH tests for a unique inserted, changed, and deleted token and a trigger-disabled red control. Keep evidence in the phase relay. The existing gate's conditional pyproject/tests checks (`validate.sh:17-24`) also need a post-scaffold assertion so missing package/tests cannot skip validation and print OK.
    99	- [Should] **Grounding claims about the current embedder are false.** p1:25-28 names `walk_repo` and `qualified_name` as existing; actual source uses `iter_files` (`.embed-tmp/scripts/embed_repos.py:106`) and emits path/start_line/end_line/text, then adds id/repo (`:136-140,160-161`). Plan:60-61 attributes `max_seq_length=2048` to this script, but model construction at `:170` has no subsequent cap assignment. **Fix:** correct the recon/brief to separate existing fields from new fields, define where the promised superset's `id` appears, and cite `FINDINGS-0.5.md:174-179` for the required cap. Make setting 2048 an explicit implementation acceptance assertion with a stub model; query shape/norm alone (p2:84-86) cannot detect the missing memory guard or query prefix.
   100	- [Should] **The chunk contract is internally ambiguous and weakly bounded.** p1:49 promises `list[Chunk]`, p1:61-62 returns warnings alongside it, while p1:63-64 exports an iterator without a warning channel. p1:53-60 uses nearest blank lines and 6,000 characters as token headroom, but does not define a hard split when no blank line exists or bound Markdown sections. **Fix:** choose one return/report contract through Store.ingest; require a terminating split for long single-line code/config and long Markdown, define source ranges for noncontiguous module text, and distinguish a character heuristic from actual tokenizer bounds including the path prefix. Add explicit no-blank-line and long-Markdown cases.
   101	- [Should] **Scope deviations are not fully reconciled with the live requirement.** Issue #11 Act 1 says “over the existing 21,580-vector sidecar”; its calibration says “REFACTOR / ABSORB” and “keeps ... revision tracking, ingest planner and harness config.” Plan:81-95 records quality/ARM deviations, but not replacing that sidecar with fresh ingest; plan:74-79 ports only cache semantics and explicitly leaves the planner untraced. **Fix:** add the sidecar/rebuild and inheritance deferrals to Acceptance with reasons and downstream ownership, and explain why this Act 1 implementation will not create a second planner/store to reconcile in Act 2. The existing quality relaxation is explicitly recorded, but is not evidence that issue #11's non-saturated-set win criterion is complete; keep that requirement visibly outstanding.
   102	- [Should] **Containment and entry-point details need closure.** p0:53,67 asks for editable installation, whose generated package metadata needs an explicitly contained destination; p4:40 puts runtime output under `temp/`, absent from `MARATHON.yaml:49`'s allowlist. This turn's harness explicitly permits generated evidence only in `.relay-scratch/`; do not assume gitignored means containment-exempt in builder turns. No phase allows CHANGELOG.md despite `AGENTS.md:49-51` requiring it for substantive iterations. p4:61 invokes `python -m xyz`, while p0:54-62 lists no `xyz/__main__.py`. **Fix:** document builder scratch/generated-output exemptions or move outputs to the supported scratch location, assign changelog recording to an allowed actor, and explicitly require/test the module entry point (or use the supported console command).
   103	- [Should] **The public retrieval API leaves mode and mismatch behavior underspecified.** p3:51 defaults mode to `hybrid` but p3:52-53 says a supplied reranker changes the default; it cannot distinguish an explicit hybrid request from that default. p3:56-57 refers to an RRF score even for dense/BM25-only modes, and a second embedder supplied to `Retriever` can differ from the one checked at Store.open (p2:55-56). **Fix:** use an explicit auto/None default, specify unsupported rerank and per-mode tau behavior plus empty results, and validate the retrieval embedder identity against the store. Test model, dim, and provider mismatches independently, including at query time; the current p2:74 test exercises model only.
   104	- [Pass] **Canonical phase coverage and core structure are present at the outline level.** canonical:204-207,214-224 map to p0 constraints/scaffold, p1 chunking, p2 one-writer SQLite/cache, p3 hybrid/rerank/latency, and p4 round-trip. `MARATHON.yaml:23,32,41,50` supplies the p0→p4 dependency chain; its `xyz/` allowlists include p3's permitted read helper in `xyz/index/`. Plan:111-113 names one canonical writer and plan:127-128 states Easy rollback. These passes do not resolve the execution/containment issues above.
   105	- [Pass] **Several acceptance choices are explicit and citable.** Query-only prefix matches `SOP.md:31-33` and p2:25-27; `k = ?` and its red control are specified at p3:27-29,67-68,84 and supported by issue #11 Act 1's quoted “Use the vec0 k = ? KNN form”. Empty-query rejection is explicitly required at p4:90-91. Rating `85/60/50/30` has a stated rationale, neutral appeal and “No operator override” at plan:132-136. The historical user-order assertion is not independently verified by this review.
   106	
   107	DoD disposition: grounding, completeness/deviation accounting, DRY inheritance, executable blast radius, falsifiable gates, and runtime/fallback contracts need the fixes above; rating rationale passes. Producer should disposition each finding and revise only the plan/brief/gate artifacts in its own turn. Handing off to claude-a (Producer) for revision and round 2.
   108	
   109	## Producer — claude-a — Round 2 — 2026-09-06
   110	
   111	Dispositions for every Round 1 finding (all changes are to the plan, briefs and gate only; no code exists yet):
   112	
   113	- [Blocker] Metric depth — **Implemented.** p4 now reports MRR@D / R@k / miss@D at an explicit depth D = 100 (`fetch_k=100` per lane) with its own dense-only arm at that depth as the baseline; Run 9 is context only. `per_query` rows carry the ordered `ranking`; ranks are chunk ranks (no silent path dedupe); rank-11 red case at depth 10 vs 100; `SearchResult.ranking` (p3) exposes the full candidate order. See brief-p4 §Context, Task 1, DoD; brief-p3 Task 5; plan §Recon.
   114	- [Blocker] Offline prerequisites — **Implemented.** Environment contract (`XYZ_PY`, `XYZ_SCRATCH`, `XYZ_EVAL_REPO`, offline env) defined in `validate.sh` and brief-p0 §Environment; `validate.sh` now runs an env preflight (interpreter, modules, both cached models, FTS5) before anything else; offline vars are exported and briefs tell the builder to export them for ad-hoc smokes; `PYTHONPATH=<repo>` replaces the editable install (no `*.egg-info/` writes); p4 asserts `$XYZ_EVAL_REPO/scripts` and `/app` exist before starting. Isolation note: the operator exports the values when firing.
   115	- [Blocker] Subset fallback — **Implemented.** `walk_repo(include_prefixes=...)` is a root-preserving filtered walk (p1 Task 1, tested for unchanged `rel_path`); `Store.ingest` raises `EmptyCorpus` on zero files and scopes pruning to the walked prefixes (p2 Task 2 + tests); p4 fallback is a **fresh** DB, one invocation with three `--include-prefix`, ETA-triggered (> 45 min after 200 chunks), labelled `corpus: subset`; `xyz eval` refuses an empty corpus or missing gold paths (exit 2) and records corpus provenance.
   116	- [Blocker] Red controls / gate — **Implemented.** `validate.sh` is now unconditional (package presence incl. `xyz/__main__.py`, exact `__version__ == 0.5.0.dev0`, `python -m xyz --version`, pytest); p0 red controls flip the version and delete `__main__.py`; p2 red controls assert `files_skipped == files_seen` / `files_reingested == 0` separately from embedder calls, plus `fts_match` tests for inserted/changed/deleted tokens with a trigger-disabled red control.
   117	- [Should] Grounding — **Implemented.** Plan §Recon and brief-p1 §Context corrected: `iter_files`, existing fields `path/start_line/end_line/text` + `id/repo`, new fields named as new; `max_seq_length=2048` attributed to FINDINGS-0.5.md and made a stub-model acceptance assertion in p2 (with query-prefix-on-queries-only asserted the same way).
   118	- [Should] Chunk contract — **Implemented.** `chunk_file -> ChunkResult(chunks, warnings)`, `chunk_repo -> ChunkResult`, warnings surface only via `IngestReport`; hard cut at 6,000 chars when no blank line (single-line 6,001-char test), Markdown sections bounded too; module chunk line range defined; 6,000 chars stated as a character heuristic under the 2048-token cap.
   119	- [Should] Scope deviations — **Implemented.** Three new entries under "Acceptance — deviations": sidecar → fresh ingest (reason), ABSORB of planner/revisions/harness → Act 2 with the single-planner argument, and the non-saturated-set win criterion recorded as outstanding.
   120	- [Should] Containment / entry point — **Implemented.** Generated output goes to `$XYZ_SCRATCH` (default `.relay-scratch/`), nothing under `temp/`; no editable install; `xyz/__main__.py` required in p0 and asserted by the gate; `CHANGELOG.md` assigned to the orchestrator at PR time (plan §Dependencies, briefs §Non-goals).
   121	- [Should] Retrieval API — **Implemented.** `mode="auto"` default with explicit resolution rule; explicit `hybrid` never reranks; `hybrid+rerank` without a reranker raises; per-mode τ semantics and empty-candidate behaviour defined; `Retriever` validates the embedder against the store via `Store.check_embedder`; model/dim/provider mismatches tested independently at open and at query time.
   122	- [Pass] ×2 — noted; no change.
   123	
   124	Round 2 requested: please re-check questions 1-7 against the revised artifacts (`validate.sh`, brief-p0…p4, plan §Recon/§Acceptance/§Dependencies). Handing off to codex (Reviewer) — codex, take your turn.
   125	
   126	## Reviewer — codex — Round 2 — 2026-09-06
   127	
   128	Verdict: Changes requested
   129	swept file: yes
   130	
   131	Swept the complete plan, MARATHON.yaml, all five briefs and validate.sh, including pre-existing content. Re-read the reference embedder, metric implementation, query labels, SOP and canonical Phase 0/1 plus the memory findings; fetched the live issue with `gh issue view 11 --repo HiQS-Labs/XYZ-code-intelligence --json body`. Graph `list_projects` returned all 50 entries with `has_more=false`; neither this worktree nor its source repo is indexed, so there is no applicable generation/coverage evidence. Used direct source inspection without indexing (review-only containment). No artifact/source execution, model probes, project gates or git commands. The findings below include unresolved and newly exposed defects in the swept files. Reversibility: Easy. Bet: fixing these bounded contracts before building avoids green checks that do not establish runtime readiness or retrieval correctness.
   132	
   133	Uses Round 1 citation shorthand (`plan`, `p0`–`p4`, `canonical`).
   134	
   135	- [Blocker] **Offline readiness still passes vacuously.** `validate.sh:22-29` checks `find_spec` and model-directory existence only. Empty model directories satisfy it; missing weights/tokenizer/custom modeling code or unusable language grammars are not detected. p0's Environment contract says this establishes “both cached models” before starting, and prohibits installs. **Fix:** assign an operator provisioning/preflight step before firing, with recorded offline loads of both actual model classes and parser creation for Python/JS/TS/TSX/PHP using the exact `XYZ_PY` and caches propagated into builder worktrees. Check the required dependencies by usable imports, not names alone; name failure behavior and evidence destination. A deliberately incomplete cache and an unavailable grammar must fail the readiness control. This can be a separate explicit prelaunch check rather than loading models on every unit-test gate. The explicit env variables/no-editable-install changes are useful but do not close Round 1's readiness blocker.
   136	- [Blocker] **Incomplete-walk pruning protection remains unspecified.** p2:63-70 guards only zero files. If one subtree is readable and another cannot be enumerated, a nonempty partial walk still qualifies for pruning everything missing in the selected scope; p1 Task 1 specifies no enumeration/read-error policy. **Fix:** propagate traversal/read failures and prohibit pruning unless the entire selected scope completed successfully; define how intentional exclusions differ from errors. Add an injected directory-enumeration failure after at least one yielded file, assert pre-existing unseen chunks/FTS/vec records survive, and name a red control that disables the completion guard. Retain the successful-deletion and prefix-scope tests. Round 1 explicitly requested incomplete-walk rejection, not merely an empty-root check.
   137	- [Should] **Depth 100 needs a complete rerank-tail contract and chunk-level evidence.** p3:57-60 reranks only 50 but promises an ordered list up to 100; it never says how unreranked candidates are appended or where the two-lane union is truncated. p4:54,70-71 then exports only paths for the reorder count: swapping two chunks of the same file becomes invisible. **Fix:** specify fuse → truncate to D → rerank the first min(D,50) → append untouched tail in RRF order (or another explicit policy without comparing cross-encoder scores to RRF scores). Preserve ordered chunk IDs alongside paths in JSON and compute reorder count from IDs. Test a >100-candidate union, a relevant chunk at rank 75, and a swap between two chunks of one path; record red-control evidence in the relay. The new cutoff/baseline fixes the original full-corpus comparison error, but does not settle these remaining ordering cases.
   138	- [Should] **BM25 threshold direction conflicts with the score contract.** p3:31 says native BM25 is lower-is-better, while p3:61-63 rejects a lane score *below* tau; unlike dense at p3:44, lexical at p3:41-42 never negates its score. **Fix:** define `Hit.score = -bm25(...)` (higher is better across lanes), or explicitly reverse the BM25 threshold comparison. Test stronger and weaker lexical hits around a threshold. Also qualify p3:74-75's “tau=None never does” assertion to nonempty candidates, since p3:63 correctly requires an empty set to return no-answer even without tau.
   139	- [Should] **The changed-token test is contradictory as written.** p2:83-85 says to “add a unique token” then requires `old_token` to disappear. An additive edit leaves the old token present, so a correct FTS implementation fails the stated assertion. **Fix:** replace the old unique token with the new one in a specific chunk while keeping a separate chunk unchanged for the cache-hit assertion; require old MATCH empty and new MATCH nonempty. Keep the trigger-disabled red control.
   140	- [Pass] **Grounding corrections and model guard assertions now match the references.** Plan Recon and p1 Context correctly name `iter_files` and path/start_line/end_line/text plus id/repo (`.embed-tmp/scripts/embed_repos.py:106,136-140,160-161`); p2:92-93 explicitly tests the cap and query-only prefix, consistent with `FINDINGS-0.5.md:174-179` and `SOP.md:31-33`. Store-assigned `chunks.id` is specified at p2:54. These are plan-level checks, not executed implementation evidence.
   141	- [Pass] **Scope accounting, one-writer architecture, dependency order and rating remain sound at plan level.** Plan Acceptance now explicitly marks fresh ingest, Act 2 inheritance deferrals and the non-saturated criterion as outstanding, alongside the existing quality/ARM deviations; these account for the live issue's Act 1 items without claiming the original win criterion complete. Canonical:204-207,214-224 is covered by the five briefs. p2:51 says “Store, the only writer”; MARATHON.yaml:23,32,41,50 orders p0→p4 and its allowlists permit the demanded source paths. Plan Dependencies assigns CHANGELOG to the orchestrator and states “Reversibility: Easy”; p0 requires `xyz/__main__.py`. Plan Rating retains `85/60/50/30`, “appeal 50: neutral” and “No operator override”; the historical user-order assertion remains independently unverified.
   142	- [Pass] **Several falsification and fallback fixes are concrete.** `validate.sh:43-54` unconditionally checks package presence, exact version and pytest; p2:80-82 separately asserts file skips and writes; p4:55-57,73-74 rejects empty queries and tests rank 11 at two depths; p4:36-39 uses a same-depth dense baseline rather than Run 9. p1 Task 1 preserves root-relative prefixes and p4:80-83 uses one fresh subset DB; every label in `.embed-tmp/eval/queries-LTVera-Pandas.json` lies under scripts/app/alembic. p4:77-79 supplies a measured ETA trigger and p4:105 requires a <30-second re-ingest. Runtime feasibility is conditional on the readiness fix above; no actual model/corpus run was attempted here.
   143	
   144	DoD disposition: 1 grounding passes with stated historical-evidence limits; 2 completeness/deviations passes at plan level; 3 DRY and 4 dependency/allowlist/rollback pass; 5 falsifiable checks and 6 executable runtime readiness remain changes requested; 7 rating rationale passes. Producer should disposition all five open findings and request round 3 after revising the artifacts. Handing off to claude-a (Producer) — go to the Producer window and say 'take your turn'.
   145	
   146	## Producer — claude-a — Round 3 — 2026-09-06
   147	
   148	Dispositions for all five open Round 2 findings. Two of them found real defects when I implemented the control — details below.
   149	
   150	- [Blocker] Vacuous offline readiness — **Implemented, and it immediately caught two real defects.** Added `prelaunch.sh`: an operator-run readiness control that really imports every dependency, instantiates the Python/JS/TS/TSX/PHP parsers **and asserts the grammars are already cached** (`downloaded_languages()`), and loads **both models offline with their real classes**, then writes `<venv>/xyz-prelaunch.json`. `validate.sh:20-36` now requires that marker for the same interpreter and repeats the cheap parts as real imports + parser creation (no more `find_spec`/directory-existence). Defects it found before any builder turn:
   151	  1. `tree_sitter_language_pack` **downloads grammars at first use** (cache `~/Library/Caches/tree-sitter-language-pack`) — every builder turn would have failed offline. Grammars are now pre-cached and the check asserts it; red control: `HF_HOME=<empty>` → NOT READY.
   152	  2. `cross-encoder/ms-marco-MiniLM-L-6-v2` loads without error on this stack (torch 2.14.0, transformers 5.16.1) and returns **`[nan, nan]`** — reproduced with plain `AutoModelForSequenceClassification` under both `eager` and `sdpa`, checkpoint tensors all finite; it is an old-format BERT checkpoint. A shape-only assertion passed it, exactly as you predicted. Default reranker changed to **`mixedbread-ai/mxbai-rerank-xsmall-v1`** (Apache-2.0, ~70 MB; verified 0.5973 vs 0.0174 on the code-vs-SQL pair), fallback `BAAI/bge-reranker-base` (MIT, verified 0.9155 vs 0.0614), both overridable via `XYZ_RERANKER`. `prelaunch.sh` now asserts scores are **finite and correctly ordered**; red control: `XYZ_RERANKER=cross-encoder/ms-marco-MiniLM-L-6-v2 bash prelaunch.sh` → `NOT READY - non-finite scores [nan, nan]`. Evidence goes to `$XYZ_SCRATCH/prelaunch.json`.
   153	- [Blocker] Incomplete-walk pruning — **Implemented.** p1 `walk_repo` takes a required `errors: list[str]`; `OSError` from enumeration or read is appended and the walk continues, while extension/size/binary/`exclude_dirs`/`include_prefixes` skips are **not** recorded (intentional exclusions are distinguished from errors). p2 `Store.ingest` now walks to completion **before any write or delete** and raises `EmptyCorpus` (zero files) or `WalkIncomplete` (any error) up front. Tests added: `os.scandir` monkeypatched to raise `PermissionError` for one subdirectory after files were yielded → p1 keeps yielding and records exactly one error while excluded/binary skips record none; p2 raises `WalkIncomplete` and every pre-existing chunks/FTS/vec/files row survives (verified by counts and `fts_match` of a token from the unreadable subtree). Red control (c): ignore `errors` → the surviving-rows test fails.
   154	- [Should] Rerank tail / chunk-level evidence — **Implemented.** p3 now fixes the policy: fuse → truncate to D (`fetch_k`) → rerank the first `min(D, 50)` → **append the untouched tail in RRF order**; reranker scores are never compared against RRF scores. `SearchResult.ranking` is an ordered list of `(chunk_id, path)` of length ≤ D. p4 `per_query.ranking` stores `{chunk_id, path}` objects and the reorder count compares **chunk-id sequences**. Tests: a ≥120-chunk fixture so the union exceeds `fetch_k`; a chunk at RRF position 75 stays at 75 with `fetch_k=100` and is absent with `fetch_k=50`; a fake reranker swapping two chunks **of the same path** makes the two rankings differ by id while path sequences are identical (and is counted as a reorder).
   155	- [Should] BM25 threshold direction — **Implemented.** Score contract is now stated once for every lane and stage: **higher is better**, with `bm25_search` returning `score = -bm25(chunks_fts)` alongside dense's `-distance`. Tests: a chunk matching two query terms scores above one matching one, and a tau between them keeps the stronger and rejects the weaker in `mode="bm25"`. The tau assertion is qualified as you asked: `tau=None` never yields no-answer **when at least one candidate exists**, while an empty candidate set is no-answer regardless of tau.
   156	- [Should] Contradictory changed-token test — **Implemented.** The edit is now a **replacement** (`OLDTOKEN` → `NEWTOKEN` in exactly one chunk, that file's other chunks byte-identical), so `fts_match("NEWTOKEN")` non-empty and `fts_match("OLDTOKEN")` empty are both correct, and the untouched chunks still prove the cache-hit path. Trigger-disabled red control retained.
   157	- [Pass] x3 — noted; no change.
   158	
   159	Round 3 requested: re-check questions 5 (falsifiable checks) and 6 (executable runtime readiness), which you left open, against `prelaunch.sh`, `validate.sh:18-36`, brief-p1 Task 1 + tests, brief-p2 Task 2 + tests, brief-p3 Task 1/5 + tests, brief-p4 Task 1/2. Handing off to codex (Reviewer) - codex, take your turn.
   160	
   161	## Reviewer — codex — Round 3 — 2026-09-06
   162	
   163	Verdict: Changes requested
   164	swept file: yes
   165	
   166	Swept the whole plan, MARATHON.yaml, all five briefs, validate.sh and the newly added prelaunch.sh, including pre-existing content. Read reference embedder/scorer/query labels, SOP, canonical Phase 0/1 and relevant FINDINGS evidence. No graph tools were exposed this turn; direct source inspection is the evidence, with no applicable graph generation or coverage claim. Live issue refresh failed through both gh (api.github.com connection error) and web (cache miss); issue completeness therefore relies on the prior relay's quoted issue evidence and the local canonical reconciliation, not a fresh live verification. No artifact/source execution, model probes, gates or git commands were performed. Producer-reported model runs remain attributed evidence, not runs reproduced by this reviewer. Reversibility: Easy. Bet: closing the remaining readiness and API contradictions before building prevents false readiness and incompatible implementations. Uses the earlier plan/p0–p4/canonical citation shorthand.
   167	
   168	- [Blocker] **A failed readiness run leaves a usable old success marker, and changed model/cache settings are not checked.** `prelaunch.sh:25-28` writes failure only to the evidence file; the marker is written only on success at `:97-99` and is never invalidated before a retry. `validate.sh:26-28` accepts any old `ok=true` marker naming the same interpreter. Thus a successful default run followed by the producer's failing `XYZ_RERANKER=cross-encoder/ms-marco-MiniLM-L-6-v2` control leaves the readiness check accepting the old success, even if that failing model remains selected; changing `HF_HOME` similarly escapes validation. **Fix:** invalidate the marker before starting any readiness attempt (including early failures), publish success atomically, record and compare the selected reranker and effective cache configuration in validation, and require re-prelaunch after environment changes. Add a success → failed retry → readiness rejection control and a changed-reranker/cache-without-rerun rejection control; put their evidence under `.relay-scratch/`. The actual offline loads and finite reranker assertions are valuable, but the marker consumer must enforce what was tested.
   169	- [Should] **The BM25 threshold test still contradicts the public threshold contract.** p3:75-78 defines a query-level decision using the top score: either all returned hits survive or the result becomes no-answer. p3:89-90 instead says a threshold between two candidate scores “keeps the stronger hit and rejects the weaker one”, implying per-hit filtering in the same result. **Fix:** preserve the specified query-level rule and make this two searches with controlled candidate sets/top scores on opposite sides of tau, explicitly asserting that a below-tau secondary hit remains when the top hit passes; or deliberately change the API to per-hit filtering and reconcile every mode. Keep the score-negation test separately.
   170	- [Should] **The scorer input cannot supply its required chunk-id output.** p4:50-51 still defines `score(rankings: dict[query -> list[chunk_path_in_rank_order]], queries, depth)`, but p4:54-55 requires its JSON rows to preserve `{chunk_id, path}` and p4:72-73 counts reorders by actual chunk IDs. Paths cannot recover IDs when two chunks share a path. **Fix:** accept ordered `(chunk_id, path)` records throughout the scorer (matching p3:73-74), use only their paths for relevance checks, and preserve IDs in serialization; add a scorer/JSON round-trip assertion for two distinct IDs with one path. Do not fabricate IDs from rank positions.
   171	- [Nit] **Current-state pointers lag two review rounds.** Plan:40 still says round 1 implemented / round 2 next, and plan:213-216 ends at round 2 requested. **Fix:** update the producer-owned status/run log to the round 3 outcome and remaining readiness work before launch.
   172	- [Pass] **Incomplete-walk protection and the changed-token test are now explicit.** p1:54-58 distinguishes errors from exclusions; p2:64-68 requires completing the walk and rejecting errors before any mutation. p2:93-96 and :115-117 specify surviving-row/MATCH evidence and the disabled-guard red control. p2:86-89 replaces OLDTOKEN with NEWTOKEN while retaining unchanged chunks for cache hits. These close the corresponding Round 2 findings at plan level.
   173	- [Pass] **Rerank tail and lane score direction are defined.** p3:69-74 now specifies fuse → truncate to D → rerank first min(D,50) → append unchanged tail, and p3:94-98 tests a large union, rank 75 and same-path/different-ID reordering. p3:50-56 normalizes both lane scores to higher-is-better. The remaining threshold-test and scorer-input contradictions are separately graded above.
   174	- [Pass] **Grounding, architecture, phase ordering and rating retain citable support.** Plan:60-70 agrees with `.embed-tmp/scripts/embed_repos.py:106,136-140,160-170` and `.embed-tmp/eval/score_retrieval.py:133-156`; p2:100-101 requires the sequence cap and query prefix from `FINDINGS-0.5.md:174-179` and `SOP.md:31-33`. Canonical:204-207,214-224 maps to p0–p4; plan:90-112 explicitly accounts for scope deviations without claiming the non-saturated win criterion complete. p2:51 names one writer; MARATHON.yaml's `depends_on` chain and `artifact` entries support the briefs; plan:150-161 assigns changelog ownership and Easy rollback. Plan:165-169 grounds 85/60/50/30, neutral appeal and no override. The historical user-order claim remains independently unverified.
   175	- [Pass] **Runtime budget/fallback and nonempty checks remain concrete, conditional on readiness.** `FINDINGS-0.5.md:58` records 1,529.9 seconds for 5,147 chunks; MARATHON.yaml's p4 timeout is 7200 seconds. p4:78-85 requires a measured 200-chunk ETA and a fresh root-preserving subset DB, with subset provenance; all gold paths in `.embed-tmp/eval/queries-LTVera-Pandas.json` use scripts/app/alembic. p4:56-58,68-76,105-114 specifies empty-query/missing-gold rejection, cutoff metrics, measured real-run evidence and red controls. `prelaunch.sh:73-95` now actually loads both model classes and rejects non-finite/misordered reranker scores; this is source evidence of the control, not independent proof of the claimed model outputs.
   176	
   177	DoD disposition: 1 grounding passes within the stated evidence limits; 2 local completeness/deviation accounting retains prior support but the live issue was unavailable; 3 DRY, 4 dependency/allowlist/rollback and 7 rating pass at plan level. 5 consistent falsifiable checks and 6 enforced runtime readiness remain changes requested. This sweep includes newly introduced readiness defects and remaining pre-existing API contradictions. Round 3 / 3 is exhausted, so STATUS is Escalated, not Approved. Handing off to claude-a (Producer) — go to the Producer window and say 'take your turn' to resolve the findings and arrange the next review decision; do not launch on this verdict.
   178	
   179	## Producer — claude-a — Round 3 dispositions — 2026-09-06
   180	
   181	All four Round 3 findings implemented. Recording them here for the record; the relay is at its 3/3 cap and STATUS stays Escalated — the marathon was NOT launched, and whether to reopen for a round 4 is the operator's call, not mine.
   182	
   183	- [Blocker] Stale success marker / unvalidated config — **Implemented.** You were right that my own red-control run demonstrated the hole. `prelaunch.sh:24-30` now **deletes the marker before any check runs**, so a failed or interrupted attempt leaves none; success is published **atomically** (`tmp + os.replace`, :112-116) so a crash mid-write cannot leave a partial marker. The marker now records an `env` fingerprint (selected reranker, `HF_HOME`, `HF_HUB_CACHE`, `TRANSFORMERS_CACHE`, resolved hub dir) and `validate.sh:27-42` compares it against the live environment, failing with the exact drift and the re-run command. Three controls run, evidence in `.relay-scratch/prelaunch.json`:
   184	  1. success → failing `XYZ_RERANKER` retry → `marker present = no`, and validate fails `readiness marker missing`;
   185	  2. `XYZ_RERANKER=BAAI/bge-reranker-base` without re-prelaunch → `environment changed since prelaunch (validated, now): {"reranker": ["mixedbread-ai/mxbai-rerank-xsmall-v1", "BAAI/bge-reranker-base"]}`;
   186	  3. `HF_HOME=$TMPDIR/other-hf` → rejected on `HF_HOME` and `hf_hub_dir`.
   187	- [Should] τ contract vs test — **Implemented**, keeping the query-level rule as specified rather than changing the API. brief-p3 now separates the two concerns: a score-direction test (two-term match scores above one-term), and **two searches** for τ — (a) top score above τ → `no_answer=False` and the result **still contains the below-τ secondary hit** (explicitly asserted), (b) top score below τ → `no_answer=True`, `hits=[]`.
   188	- [Should] Scorer input cannot supply chunk ids — **Implemented.** `score()` now takes `dict[query -> list[tuple[chunk_id, path]]]`, matching what `SearchResult.ranking` already returns; relevance is judged on the `path` half only, ids are carried through serialization, and ids must never be fabricated from rank position. Added a round-trip test: two distinct `chunk_id`s sharing one `path` survive `score()` + JSON in order, so a same-path reorder stays visible.
   189	- [Nit] Stale status pointers — **Implemented.** The plan's `## Status` row and `## Run log` now carry all three rounds, the two defects the readiness control found, and the escalation state.
   190	
   191	Relay closed at the cap: **Escalated**, not Approved. Next action is the operator's — reopen for one more review round against these fixes, or accept the plan explicitly. No launch on this verdict.
   192	
   193	## Operator — round cap extended — 2026-09-06
   194	
   195	The 3-round cap was exhausted at `STATUS: Escalated` and implementation stopped; the marathon was **not** fired. The operator (Noel Saw) was asked and chose **one more review round** over accepting the plan as-is or stopping. Cap raised to 4 and STATUS reopened to `Open` on that explicit authority — recorded here rather than done silently, since the cap is a governance boundary. `XYZ_EVAL_REPO` is confirmed as `/Users/noelsaw/Documents/GH Repos/LTVera-Pandas` (full tree first, subset fallback per brief-p4).
   196	
   197	Reviewer: this round covers **only** the Round 3 fixes recorded in the Producer block above — DoD questions 5 (falsifiable checks) and 6 (runtime readiness). Approve if they close, else name what remains.
   198	
   199	## Reviewer — codex — Round 4 — 2026-09-06
   200	
   201	Verdict: Changes requested
   202	swept file: yes
   203	
   204	Swept the complete plan, MARATHON.yaml, all five briefs, `validate.sh`, and `prelaunch.sh`, including their pre-existing content, while limiting the decision to the operator-authorized DoD questions 5 and 6. Read the retained `.relay-scratch/prelaunch.json` and the installed libraries' cache-resolution source. No artifact/source execution, model probes, project gates, or git commands were performed. No graph tools were exposed; direct source inspection is the evidence tier. Reversibility: Easy. Bet: bind readiness to the cache the libraries actually resolve, or an offline builder can inherit a false-success marker after cache environment drift.
   205	
   206	- [Blocker] **The readiness marker still does not bind the effective Hugging Face cache for two supported environment paths.** `prelaunch.sh:35-40` and `validate.sh:31-39` record/compare raw `HF_HOME`, `HF_HUB_CACHE`, and `TRANSFORMERS_CACHE`, but reconstruct `hf_hub_dir` from `HF_HOME` alone. The installed `huggingface_hub/constants.py:158-179` resolves its default through `XDG_CACHE_HOME` and allows legacy `HUGGINGFACE_HUB_CACHE` to feed `HF_HUB_CACHE`; `transformers/utils/hub.py:408` then uses that resolved constant. Neither omitted variable changes the current fingerprint, so changing either after a successful prelaunch can make validation accept a marker for a different or empty cache; cheap imports/parser checks do not load the models (`validate.sh:43-51`). **Fix:** in both scripts fingerprint the library-resolved cache constants (at minimum `huggingface_hub.constants.HF_HOME` and `HF_HUB_CACHE`, plus the effective Transformers module/cache directory used here) rather than hand-reconstructing them, and add `XDG_CACHE_HOME=<empty>` and `HUGGINGFACE_HUB_CACHE=<empty>` success→drift controls proving `validate.sh` rejects until prelaunch is rerun. Preserve the marker-first invalidation and atomic publication at `prelaunch.sh:21-25,116-122`.
   207	- [Pass] **The τ test now matches the query-level API contract.** p3:75-78 defines the top-score decision and preserved ranking; p3:89-97 separates BM25 score direction from two τ searches, explicitly retaining the below-τ secondary hit when the top hit passes and returning empty hits when the top fails.
   208	- [Pass] **Chunk IDs now survive the scoring boundary and make same-path reorders falsifiable.** p4:50-64 accepts ordered `(chunk_id, path)` records, judges relevance by path, serializes both fields, and requires a same-path/two-ID round-trip; p4:73-82 computes and tests reorder count from chunk-ID sequences and rejects empty query input.
   209	- [Pass] **The remaining phase red controls and runtime fallback stay concrete at plan level.** p0:89-96, p1:100-105, p2:107-117, p3:112-119, and p4:109-120 each name a failure-sensitive check/red control. p4:83-95 gives the measured-ETA trigger, fresh root-preserving subset DB, unchanged re-ingest, depth-100 evaluation, and recorded metrics; `MARATHON.yaml:45-52` retains the 7200-second p4 budget. `.relay-scratch/prelaunch.json:27-52` records successful offline model shapes/scores for the pinned interpreter, but that success does not close the cache-drift escape above.
   210	
   211	DoD disposition for this authorized round: question 5 now passes; question 6 remains open because readiness can still false-pass after effective cache drift. Round 4 / 4 is exhausted, so STATUS is Escalated, not Approved. Handing off to claude-a (Producer) — go to the Producer window and say 'take your turn' to disposition the remaining readiness blocker and return the escalation to the operator; do not launch on this verdict.
   212	
   213	## Producer — claude-a — Round 4 dispositions — 2026-09-06
   214	
   215	The single Round 4 blocker is implemented. Returning the escalation to the operator as instructed; the marathon remains unfired.
   216	
   217	- [Blocker] Cache fingerprint not bound to the libraries' resolved constants — **Implemented, finding confirmed.** Both scripts now read the cache paths from `huggingface_hub.constants` (`HF_HOME`, `HF_HUB_CACHE`, `HF_ASSETS_CACHE`) and `transformers.utils.hub` (`TRANSFORMERS_CACHE`, `HF_MODULES_CACHE`) instead of rebuilding a path from `HF_HOME` — one shared shape, `prelaunch.sh:32-53` writing it and `validate.sh:27-48` comparing it. Your two named escapes are now caught, along with two more:
   218	
   219	  | control | result |
   220	  |---|---|
   221	  | `XDG_CACHE_HOME=$TMPDIR/xdg` | rejected — all five paths drift |
   222	  | `HUGGINGFACE_HUB_CACHE=$TMPDIR/legacy-hub` | rejected — `hf_hub_cache` drift (legacy var honoured) |
   223	  | `HF_HUB_CACHE=$TMPDIR/newhub` | rejected — `hf_hub_cache` drift |
   224	  | `HF_HOME=$TMPDIR/hfhome` | rejected — all five paths drift |
   225	  | unchanged env | passes: `env ok: 3.11.15 prelaunch 2026-09-06T22:57:26Z sqlite-vec v0.1.9` |
   226	
   227	  Marker-first invalidation and atomic publication are preserved. Recorded fingerprint on this machine: `hf_home=/Users/noelsaw/.cache/huggingface`, `hf_hub_cache=.../hub`, `hf_assets_cache=.../assets`, `transformers_cache=hf_modules_cache=.../modules`.
   228	- [Pass] x3 — noted. Question 5 is closed per your disposition.
   229	
   230	**Round 4 / 4 exhausted; STATUS stays Escalated and nothing was launched.** The operator already extended the cap once (3 → 4) and asked to be brought the specifics rather than have it extended again, so the next move is theirs: extend to a round 5 covering only this cache-fingerprint fix, or accept and launch. Not launching on this verdict.
   231	
   232	<!-- ↓↓↓ NEXT TURN goes here (append above nothing — this marker stays last) ↓↓↓ -->

exec
/bin/zsh -lc 'nl -ba PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p2-store.md' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
 succeeded in 0ms:
     1	---
     2	title: GH-11 marathon brief — gh11-p2-store
     3	status: active
     4	created: 2026-09-05
     5	updated: 2026-09-06
     6	owner: Noel Saw
     7	goal: Phase brief consumed by marathon-drive.sh for phase gh11-p2-store; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
     8	roadmap_exempt: true
     9	---
    10	
    11	# Phase brief — gh11-p2-store: SQLite store (chunks + FTS5 + vec0), provider-keyed embed cache, drift guard
    12	
    13	## Status
    14	
    15	| What was just completed | What's next |
    16	|---|---|
    17	| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p2-store` after `gh11-p1-chunkers`; outcome recorded in the capture doc. |
    18	
    19	Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
    20	(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
    21	Canonical doc → "Phase 1", step 2 and step 4 (CodeRankEmbed as the placeholder dense lane).
    22	Environment contract: see `brief-p0-scaffold.md` (`XYZ_PY`, `XYZ_SCRATCH`, offline env, no installs).
    23	
    24	## Context you must read before coding
    25	
    26	- `SOP.md` → CodeRankEmbed: query prefix `"Represent this query for searching relevant code: "`
    27	  on **queries only**, documents raw; `trust_remote_code=True`; `TOKENIZERS_PARALLELISM=false`;
    28	  batch 16. `FINDINGS-0.5.md` (~174-179): **`max_seq_length = 2048` is the real memory guard** and
    29	  must be set explicitly on the loaded model (the old script never set it — this is a tested
    30	  requirement here). Model load ≈ 11.6 s → load once per process.
    31	- Issue #11 carve-out 1 (Ask-Self inheritance): the embed cache is keyed by
    32	  `(content_sha, model, dim, provider)` and an index refuses to be opened, extended **or queried**
    33	  by a different `(model, dim, provider)` — that guard caught real cross-provider cache poisoning.
    34	  Port the semantics; do not copy Ask-Self files. This file-sha planner + cache is the **only**
    35	  planner in XYZ; Act 2 reconciles Ask-Self's planner onto it, not beside it.
    36	- `sqlite-vec` and FTS5 are verified present in `XYZ_PY` by `validate.sh`'s env preflight.
    37	
    38	## Task
    39	
    40	Implement `xyz/index/`:
    41	
    42	1. `xyz/index/embed.py` — an `Embedder` protocol (`model_id`, `dim`, `provider`,
    43	   `encode_documents(texts) -> np.ndarray[float32]`, `encode_query(text) -> np.ndarray`) and
    44	   `CodeRankEmbedder` (`provider="sentence-transformers"`, `dim=768`, L2-normalised output, device
    45	   auto: MPS if available else CPU; `EMBED_BATCH_SIZE` / `EMBED_MAX_THREADS` env like the old
    46	   script). Constructor accepts an injectable `model_factory` so a test can pass a stub and assert:
    47	   `max_seq_length` was set to **2048**, `encode_query` prepends the exact prefix, and
    48	   `encode_documents` does **not**. `tests/fakes.py` provides `FakeEmbedder(model_id="fake",
    49	   dim=8, provider="fake")` (deterministic hash-based unit vectors, counts calls) used by every
    50	   store/retrieve test.
    51	2. `xyz/index/store.py` — `Store`, the **only writer** of an index:
    52	   - tables: `meta(key, value)` holding `model`, `dim`, `provider`, `schema_version`;
    53	     `files(repo, path, file_sha, chunk_count, ingested_at, PRIMARY KEY(repo, path))`;
    54	     `chunks(id INTEGER PRIMARY KEY, repo, path, kind, qualified_name, start_line, end_line,
    55	     content_sha, text, embedded_text)`; `chunks_fts` = FTS5 **external-content** table over
    56	     `chunks(embedded_text, qualified_name, path)` kept in sync by insert/delete/update triggers;
    57	     `chunks_vec` = `vec0(embedding float[<dim>])` with rowid = `chunks.id`;
    58	     `embed_cache(content_sha, model, dim, provider, vector BLOB, PRIMARY KEY(content_sha, model,
    59	     dim, provider))`.
    60	   - `Store.open(db_path, embedder)`: creates the schema on first use and writes `meta`; on an
    61	     existing DB raises `IndexMismatch` naming the differing field if **any** of `model`, `dim`,
    62	     `provider` differ. `Store.check_embedder(embedder)` exposes the same check for readers (p3).
    63	   - `Store.ingest(repo, root, chunker=chunk_repo, include_prefixes=None) -> IngestReport`, the
    64	     planner: **walk first, mutate second.** Run the p1 walk (honouring `include_prefixes`) to
    65	     completion into an in-memory list of `(rel_path, bytes)` with an `errors` list; a walk that
    66	     yields **zero files raises `EmptyCorpus`**, and a walk with **any traversal error raises
    67	     `WalkIncomplete`** (listing the errors) — both **before any write or delete**. Only a complete
    68	     walk may proceed. For each file compute `file_sha`; same sha in `files` → skip;
    69	     else delete that file's chunks (FTS/vec rows via triggers/explicit delete) and insert the new
    70	     ones. Embed only chunks whose `content_sha` is absent from `embed_cache` for this
    71	     `(model, dim, provider)`; cache every new vector. **Pruning is scoped:** files in `files` for
    72	     this `repo` that are absent from the walk are pruned only when they fall under the walked scope
    73	     (all of the repo when `include_prefixes` is None, else only under those prefixes).
    74	     `IngestReport` carries `files_seen, files_skipped, files_reingested, files_pruned,
    75	     chunks_written, chunks_embedded, cache_hits, warnings, seconds`.
    76	   - `Store.stats()` → row counts of `chunks`, `chunks_fts` (via `SELECT count(*) FROM chunks_fts`),
    77	     `chunks_vec`, `embed_cache`, `files`; `Store.fts_match(token, limit)` → chunk ids whose FTS row
    78	     matches (used by tests to prove the inverted index, not just the row count, is current).
    79	   - One transaction per file; WAL journal mode; `PRAGMA foreign_keys=ON`.
    80	3. Tests in `tests/test_store.py` with `FakeEmbedder` on the p1 fixture copied to a tmp dir:
    81	   - first ingest: `chunks_embedded == chunks_written > 0`; `chunks`, `chunks_fts`, `chunks_vec`
    82	     counts equal; `fts_match` finds a token that exists only in one fixture file;
    83	   - **second ingest, unchanged tree: `files_skipped == files_seen`, `files_reingested == 0`,
    84	     `chunks_written == 0`, embedder call count 0, < 1 s** (all five asserted separately — the
    85	     red control below depends on it);
    86	   - in one fixture file, **replace** the unique token `OLDTOKEN` (present in exactly one chunk)
    87	     with `NEWTOKEN`, leaving that file's other chunks byte-identical: only that file is re-ingested
    88	     (`files_reingested == 1`), its unchanged chunks are cache hits (embedder called once, for the
    89	     changed chunk), `fts_match("NEWTOKEN")` returns that chunk and `fts_match("OLDTOKEN")` is empty;
    90	   - delete one file: its chunks vanish from all three tables and `fts_match` of its unique token is
    91	     empty; with `include_prefixes` naming a different directory, that deleted file is **not** pruned;
    92	   - an empty directory raises `EmptyCorpus` and writes nothing;
    93	   - **incomplete walk:** after a full ingest, monkeypatch `os.scandir` to raise `PermissionError`
    94	     for one subdirectory (after other files have been yielded) → `ingest` raises `WalkIncomplete`,
    95	     and every pre-existing `chunks` / `chunks_fts` / `chunks_vec` / `files` row survives unchanged
    96	     (counts and `fts_match` of a token from the unreadable subdirectory still succeed);
    97	   - `IndexMismatch` is raised separately for a differing `model_id`, a differing `dim`, and a
    98	     differing `provider` (three tests);
    99	   - a chunk's vector read back from `chunks_vec` equals its cached vector;
   100	   - `CodeRankEmbedder` with the stub factory: `max_seq_length == 2048`, query prefix present on
   101	     queries only.
   102	
   103	## Non-goals
   104	
   105	No query path (p3), no CLI (p4). No real model in pytest.
   106	
   107	## Definition of done
   108	
   109	- `bash validate.sh` green; every test above present and passing.
   110	- One real smoke, out of pytest and under the offline env: `CodeRankEmbedder().encode_query("sort a
   111	  list")` → shape `(768,)`, norm ≈ 1.0, and `model.max_seq_length == 2048` — quote all three.
   112	- Red controls (show once each in the relay, then restore): (a) remove the `files` sha
   113	  short-circuit → the `files_skipped == files_seen` / `files_reingested == 0` assertions fail even
   114	  though the cache still keeps embedder calls at 0; (b) drop the FTS insert trigger → the
   115	  `fts_match("NEWTOKEN")` test fails while the count test may still pass; (c) disable the
   116	  `WalkIncomplete` guard (ignore `errors`) → the incomplete-walk test fails because the unreadable
   117	  subdirectory's rows get pruned.

exec
/bin/zsh -lc 'nl -ba PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p3-retrieve.md; nl -ba PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p4-roundtrip-eval.md' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
 succeeded in 0ms:
     1	---
     2	title: GH-11 marathon brief — gh11-p3-retrieve
     3	status: active
     4	created: 2026-09-05
     5	updated: 2026-09-06
     6	owner: Noel Saw
     7	goal: Phase brief consumed by marathon-drive.sh for phase gh11-p3-retrieve; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
     8	roadmap_exempt: true
     9	---
    10	
    11	# Phase brief — gh11-p3-retrieve: BM25 ∥ dense → RRF → cross-encoder rerank → τ, instrumented
    12	
    13	## Status
    14	
    15	| What was just completed | What's next |
    16	|---|---|
    17	| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p3-retrieve` after `gh11-p2-store`; outcome recorded in the capture doc. |
    18	
    19	Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
    20	(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
    21	Canonical doc → "Phase 1", step 3: *parallel BM25 + dense → RRF(k=60) → cross-encoder rerank top
    22	25-50 → no-answer threshold τ*.
    23	Environment contract: see `brief-p0-scaffold.md` (`XYZ_PY`, `XYZ_SCRATCH`, offline env, no installs).
    24	
    25	## Context you must read before coding
    26	
    27	- `xyz/index/store.py` from p2 — query through the `Store`; do not open the SQLite file elsewhere.
    28	- **`vec0` KNN must use the `k = ?` bound form** (`WHERE embedding MATCH ? AND k = ?`), never a
    29	  parameterised `LIMIT ?` — Ask-Self issue #23: `LIMIT ?` was rejected at prepare time on stricter
    30	  sqlite-vec builds and 500'd in production. This is a tested requirement.
    31	- FTS5 ranking: the built-in `bm25()` function (lower = better) via `ORDER BY bm25(chunks_fts)`.
    32	  Sanitise the query for FTS5 syntax (quote tokens; strip operators) so a query containing `-` or
    33	  `:` cannot raise; an all-stopword/empty sanitised query returns no BM25 hits, not an error.
    34	- Reranker default: **`mixedbread-ai/mxbai-rerank-xsmall-v1`** (Apache-2.0, ~70 MB, in the HF cache,
    35	  loaded via `sentence_transformers.CrossEncoder(..., trust_remote_code=True)`), read from
    36	  `XYZ_RERANKER` with that default. It is a placeholder — keep it injectable; the bake-off
    37	  (canonical Phase 3) picks the real one. Fallback if it misbehaves: `BAAI/bge-reranker-base` (MIT,
    38	  also cached and verified).
    39	  **Do not use `cross-encoder/ms-marco-MiniLM-L-6-v2`** — measured 2026-09-06 on this stack
    40	  (torch 2.14.0, transformers 5.16.1): it loads without error and returns **`[nan, nan]`** logits
    41	  (old-format BERT checkpoint; reproduced with plain `AutoModelForSequenceClassification` under both
    42	  `eager` and `sdpa` attention, checkpoint tensors all finite). `prelaunch.sh` now asserts the
    43	  reranker's scores are finite *and* rank a code snippet above unrelated SQL, so this cannot pass
    44	  silently again.
    45	
    46	## Task
    47	
    48	Implement `xyz/retrieve/`:
    49	
    50	   **Score contract for every lane and stage: higher is better.**
    51	1. `xyz/retrieve/lexical.py` — `bm25_search(store, query, k) -> list[Hit]` (`Hit`: `chunk_id,
    52	   score, stage`) with **`score = -bm25(chunks_fts)`** (FTS5's bm25 is lower-is-better; negate it),
    53	   the FTS5 sanitiser, and unit tests including one where a chunk with more query-term matches gets
    54	   the higher `score`.
    55	2. `xyz/retrieve/dense.py` — `dense_search(store, query_vec, k) -> list[Hit]` using `vec0` with
    56	   `k = ?`; `score = -distance`; expose the SQL string as a module constant `KNN_SQL` so the test can
    57	   assert on it.
    58	3. `xyz/retrieve/fuse.py` — `rrf(rankings: list[list[Hit]], k=60) -> list[Hit]`:
    59	   `score = Σ 1 / (k + rank_i)`; deterministic tie-break by `chunk_id`.
    60	4. `xyz/retrieve/rerank.py` — a `Reranker` protocol (`score(query, texts) -> list[float]`),
    61	   `CrossEncoderReranker`, and `FakeReranker` in `tests/fakes.py` (scores from a dict, default 0).
    62	5. `xyz/retrieve/pipeline.py` — `Retriever(store, embedder, reranker=None)`:
    63	   - the constructor calls `store.check_embedder(embedder)` → `IndexMismatch` on a wrong embedder
    64	     (query-time guard; tested for model, dim, provider);
    65	   - `search(query, k=10, fetch_k=50, mode="auto", tau=None) -> SearchResult` with
    66	     `mode ∈ auto | dense | bm25 | hybrid | hybrid+rerank`; `auto` resolves to `hybrid+rerank` when a
    67	     reranker is present else `hybrid`; an explicit `hybrid` never reranks; `hybrid+rerank` without
    68	     a reranker raises `ValueError`;
    69	   - **Candidate policy (explicit, tested):** dense and BM25 each fetch `fetch_k`; their union is
    70	     fused by RRF and **truncated to `fetch_k`** (the depth `D`); in `hybrid+rerank` the reranker
    71	     rescores only the first `min(D, 50)` of that list and reorders **them**; the remaining tail
    72	     (positions 51..D) is **appended unchanged in RRF order** — reranker scores are never compared
    73	     with RRF scores. `SearchResult.ranking` is the resulting ordered list of `(chunk_id, path)`
    74	     pairs of length ≤ D; the top `k` are returned with chunk rows;
    75	   - `tau` semantics per mode: compared against the top reranker score in `hybrid+rerank`, the top
    76	     RRF score in `hybrid`, the top lane score in `dense` / `bm25` (all higher-is-better); below it
    77	     → `no_answer=True`, `hits=[]`, `ranking` still populated. An empty candidate set is
    78	     `no_answer=True` regardless of τ;
    79	   - `SearchResult.timings` = per-stage milliseconds (`embed_query, bm25, dense, fuse, rerank,
    80	     total`; stages not run report 0.0).
    81	   - `xyz/retrieve/latency.py` — `LatencyLog` collecting `timings` and reporting p50 / p95 per stage.
    82	6. Tests in `tests/test_retrieve.py` on a store built with `FakeEmbedder` from the p1 fixture:
    83	   - `rrf` reproduces a hand-computed fusion for two 3-item lists with one overlap;
    84	   - a chunk ranked last by both lanes but scored highest by `FakeReranker` ends at rank 1 in
    85	     `hybrid+rerank` and **not** in `hybrid` (the "rerank measurably reorders RRF output" gate in
    86	     miniature);
    87	   - `KNN_SQL` contains the literal ` k = ?` and does not contain `LIMIT ?`;
    88	   - `"foo-bar: baz*"` and `""` do not raise in `bm25_search`;
    89	   - BM25 sign (score direction only): a chunk matching two query terms scores higher than one
    90	     matching one;
    91	   - τ is a **query-level** decision, not a per-hit filter — two searches prove it: (a) top score
    92	     above τ → `no_answer=False` and the result **still contains the below-τ secondary hit**;
    93	     (b) a query whose top score falls below τ → `no_answer=True`, `hits=[]`. Same store, τ chosen
    94	     between the two candidates' scores in case (a);
    95	   - `tau` above every score → `no_answer=True`, empty hits, non-empty `ranking`; `tau=None` never
    96	     yields `no_answer` **when at least one candidate exists**; `mode="hybrid+rerank"` with no
    97	     reranker raises; `mode="auto"` picks per the rule;
    98	   - candidate policy on a fixture large enough that the two-lane union exceeds `fetch_k`
    99	     (generate ≥ 120 small chunks): `ranking` has exactly `fetch_k` entries; a chunk placed at RRF
   100	     position 75 with `fetch_k=100` is present at position 75 after `hybrid+rerank` (tail untouched)
   101	     and absent with `fetch_k=50`; with `FakeReranker` swapping two chunks **of the same path**, the
   102	     two `ranking` lists differ by chunk id even though their path sequences are identical;
   103	   - `Retriever(store, FakeEmbedder(model_id="other"))` raises `IndexMismatch` (and likewise for
   104	     `dim`, `provider`);
   105	   - every `timings` key present and ≥ 0; `LatencyLog` p50/p95 over ≥ 3 searches.
   106	
   107	## Non-goals
   108	
   109	No CLI, no real-corpus run, no reranker bake-off. Read-only helpers in `xyz/index/` only if
   110	genuinely needed (say so in the relay).
   111	
   112	## Definition of done
   113	
   114	- `bash validate.sh` green; every test above present and passing.
   115	- One real smoke, out of pytest, offline env: `CrossEncoderReranker().score("sort a list in python",
   116	  ["def sort_list(lst):\n    return sorted(lst)", "SELECT 1 FROM dual"])` → two **finite** floats
   117	  with the code snippet higher (expected ≈ 0.597 vs 0.017 for the default model); quote them. A NaN
   118	  here is a hard stop, not a warning.
   119	- Red control: swap `k = ?` for `LIMIT ?` in `dense.py`, confirm the `KNN_SQL` test fails, restore.
     1	---
     2	title: GH-11 marathon brief — gh11-p4-roundtrip
     3	status: active
     4	created: 2026-09-05
     5	updated: 2026-09-06
     6	owner: Noel Saw
     7	goal: Phase brief consumed by marathon-drive.sh for phase gh11-p4-roundtrip; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
     8	roadmap_exempt: true
     9	---
    10	
    11	# Phase brief — gh11-p4-roundtrip: `xyz` CLI + real ingest/query round-trip on LTVera-Pandas, scored
    12	
    13	## Status
    14	
    15	| What was just completed | What's next |
    16	|---|---|
    17	| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p4-roundtrip` after `gh11-p3-retrieve`; results land in FINDINGS-0.5.md and the capture doc. |
    18	
    19	Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
    20	(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
    21	Canonical doc → "Phase 1" **QA gate**: *ingest + query round-trip on one real repo; unchanged
    22	re-ingest is near-instant (planner dedupe works); rerank stage measurably reorders RRF output;
    23	latency instrumented (p50/p95).*
    24	Environment contract: see `brief-p0-scaffold.md`. This phase additionally needs **`XYZ_EVAL_REPO`**
    25	(absolute path to a LTVera-Pandas checkout, set by the operator). First thing in the turn:
    26	`test -d "$XYZ_EVAL_REPO/scripts" && test -d "$XYZ_EVAL_REPO/app"` — if that fails, stop and report;
    27	do not guess a path.
    28	
    29	## Context you must read before coding
    30	
    31	- `.embed-tmp/eval/score_retrieval.py` — the metric definitions: a hit is a retrieved chunk whose
    32	  `path` is in the query's `relevant` list (lines ~133-138); MRR = mean of 1/rank-of-first-hit with
    33	  misses contributing 0; recall@k for k ∈ {1, 3, 5, 10}; `never_found`; `per_query` (~141-156).
    34	  **Depth differs and must be stated:** that scorer ranks the *entire* corpus (a hit at rank 11
    35	  still contributes 1/11), whereas this pipeline ranks `fetch_k` candidates. So this phase reports
    36	  **MRR@D / R@k / miss@D at an explicit depth D = 100** (`fetch_k=100` per lane; ranks past 100 count
    37	  as misses) and produces its own dense-only arm at the same depth as the comparison baseline.
    38	  BENCHMARKS.md Run 9 (MRR 0.801 / R@1 0.700, full-corpus ranking, old chunker) is quoted for
    39	  context only and is **not** equated with any number here.
    40	- `.embed-tmp/eval/queries-LTVera-Pandas.json` — the 30 labelled queries. Saturated (issue #11
    41	  caveat 2); deltas under 0.05 are noise (GH-5 doc) — report, don't over-claim.
    42	- Corpus size: Run 9 used 5,147 chunks; the p1 chunker (wider include list, AST chunks) will
    43	  produce a different count. Embedding on MPS ≈ 0.3 s/chunk ⇒ **25-35 minutes** for the full tree;
    44	  turn timeout is 7200 s.
    45	- Scratch: every generated file (index DB, eval JSON, timing logs) goes under `$XYZ_SCRATCH`
    46	  (default `.relay-scratch/`, swept by the harness). Nothing under `temp/`.
    47	
    48	## Task
    49	
    50	1. `xyz/eval/metrics.py` — `score(rankings: dict[query -> list[tuple[chunk_id, path]]], queries,
    51	   depth) -> Report`. The input is the ordered `(chunk_id, path)` records `SearchResult.ranking`
    52	   already returns (p3) — **never bare paths**, because two chunks of one file share a path and ids
    53	   cannot be recovered from it (and must never be fabricated from rank position). Relevance is
    54	   judged on the `path` half only; the `chunk_id` half is carried through to serialization. Ranks
    55	   are **chunk ranks** (the first chunk whose path is relevant; paths are not de-duplicated before
    56	   ranking); JSON writer with keys `mrr,
    57	   recall@1, recall@3, recall@5, recall@10, never_found, depth, per_query`, where each `per_query`
    58	   row carries `q, relevant, rank, top_hit` **and `ranking` — the ordered list of
    59	   `{chunk_id, path}` objects up to `depth`** (chunk ids make same-path reorders visible).
    60	   `score()` raises `ValueError` on an empty query list. Unit tests: a hand-built 3-query case; a
    61	   case where the only relevant chunk sits at rank 11 with `depth=10` → miss, and with `depth=100`
    62	   → 1/11; and a **round-trip** case where two distinct `chunk_id`s share one `path` — after
    63	   `score()` and JSON serialization both ids survive in order, so a same-path reorder is still
    64	   visible downstream.
    65	2. `xyz/cli.py` subcommands (argparse; `main(argv)` returns an int; `python -m xyz` works via
    66	   `xyz/__main__.py` from p0):
    67	   - `xyz ingest --db DB --repo NAME PATH [--include-prefix P ...]` → `Store.ingest`
    68	     (prefixes → `include_prefixes`), prints the `IngestReport`, `Store.stats()`, and peak RSS
    69	     (`resource.getrusage`); a missing / non-directory `PATH` or `EmptyCorpus` → exit 2 with a
    70	     message;
    71	   - `xyz query --db DB [--mode auto|dense|bm25|hybrid|hybrid+rerank] [--k N] [--tau T] "text"` →
    72	     rank, path, qualified_name, lines, score, per-stage timings;
    73	   - `xyz eval --db DB --queries FILE --modes dense,bm25,hybrid,hybrid+rerank --depth 100 --out JSON`
    74	     → before scoring, **assert the corpus is non-empty and that every gold path in the query file
    75	     exists in `chunks.path`** (else exit 2 listing the missing paths); run every mode; write one
    76	     report per mode plus `latency` (p50/p95 per stage per mode) and `corpus` (chunk count, file
    77	     count, `include_prefixes` used, DB path); print a comparison table and the **reorder count**:
    78	     the number of queries whose top-10 `ranking` **chunk-id sequence** differs between `hybrid` and
    79	     `hybrid+rerank` (unit-tested with a fake reranker that swaps two chunks of one path → counted).
    80	   CLI tests in `tests/test_cli.py` with the fakes on the fixture tree: ingest → query → eval end to
    81	   end; ingest twice shows `chunks_embedded == 0`; an empty query file → exit 2; a query file with a
    82	   gold path absent from the corpus → exit 2; a bogus `PATH` → exit 2.
    83	3. **The real round-trip** (the gate; keep every number):
    84	   1. `time "$XYZ_PY" -u -m xyz ingest --db "$XYZ_SCRATCH/LTVera-Pandas.sqlite" --repo LTVera-Pandas "$XYZ_EVAL_REPO"`
    85	      — record wall time, `files_seen`, `chunks_written`, `chunks_embedded`, peak RSS. **Early
    86	      estimate:** after the first 200 chunks are embedded, the CLI prints an ETA; if the ETA exceeds
    87	      **45 minutes**, abort and use the fallback.
    88	   2. **Fallback (only if triggered, and say so):** a **fresh** DB `"$XYZ_SCRATCH/LTVera-Pandas-subset.sqlite"`
    89	      with `--include-prefix scripts/ --include-prefix app/ --include-prefix alembic/` in **one**
    90	      invocation (root-preserving; every gold path lives under those prefixes). Results from a
    91	      subset are labelled `corpus: subset` everywhere they are reported.
    92	   3. Run the same ingest command again — record wall time and `chunks_embedded` (**must be 0**,
    93	      seconds not minutes).
    94	   4. `xyz eval` at depth 100 for all four modes; record MRR@100 / R@1 / R@3 / R@5 / R@10 /
    95	      miss@100 per mode, p50/p95 per stage, and the reorder count.
    96	4. **Record the results** — append a dated **"Run: XYZ hybrid retrieval round-trip (GH-11 Act 1)"**
    97	   section to `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md` with the corpus provenance (full or subset,
    98	   chunk/file counts, chunker version = this commit), the table from step 3, and the four Phase 1
    99	   QA-gate bullets each marked met / not met with the number that shows it; update the `## Status`
   100	   table and `## Run log` of `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`. Do not renumber
   101	   or edit earlier runs; do not touch `.embed-tmp/BENCHMARKS.md`; do not commit anything from
   102	   `$XYZ_SCRATCH`.
   103	
   104	## Non-goals
   105	
   106	No Slack/HTTP/MCP surface. No model or reranker comparison beyond the four modes. No changes to
   107	`.embed-tmp/`. No `CHANGELOG.md` entry (orchestrator, at PR time).
   108	
   109	## Definition of done
   110	
   111	- `bash validate.sh` green (pytest uses fakes only — the real run is **not** in pytest).
   112	- All four Phase 1 QA-gate bullets evidenced with numbers in FINDINGS-0.5.md: round-trip done
   113	  (full or labelled subset); second ingest `chunks_embedded == 0` and < 30 s; reorder count ≥ 1;
   114	  p50/p95 recorded per stage.
   115	- Acceptance from the capture doc: at depth 100, `hybrid+rerank` MRR@100 and R@1 ≥ the `dense`
   116	  arm's MRR@100 and R@1 − 0.05, on the same DB. If lower, the phase is **not** approved — report the
   117	  numbers and the most likely cause (reranker choice, BM25 sanitiser, fusion depth); do not tune
   118	  against the labelled set.
   119	- Red controls (show once in the relay): `xyz eval` with an empty query file exits 2; the
   120	  rank-11 metric test flips between miss and 1/11 with `depth`.

exec
/bin/zsh -lc 'nl -ba PROJECT/2-WORKING/v0.5/GH-11-marathon/MARATHON.yaml; nl -ba PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p0-scaffold.md; nl -ba PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p1-chunkers.md' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
 succeeded in 0ms:
     1	# GH-11 Act 1 — XYZ hybrid retrieval library (canonical doc Phase 0 + Phase 1).
     2	# Run from the target repo root:
     3	#   ./.xyz/relay-automation/marathon.sh --plan PROJECT/2-WORKING/v0.5/GH-11-marathon/MARATHON.yaml
     4	# Builder is codex (marathon.sh default), so every reviewer is agy (builder != reviewer required).
     5	# Phase ids are globally unique (gh11-*) so lane state never collides in .tick/attempts/.
     6	# Execution surface of record: PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md
     7	
     8	name: gh11-act1-hybrid-retrieval
     9	phases:
    10	  - id: gh11-p0-scaffold
    11	    name: "p0: Phase 0 close-out — constraints, pyproject, xyz/ skeleton, validate.sh"
    12	    reviewer: agy
    13	    brief: PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p0-scaffold.md
    14	    artifact: GUIDING-PRINCIPLES.md,pyproject.toml,validate.sh,xyz/,tests/
    15	    turn_timeout_s: 1200
    16	    max_review_rounds: 2
    17	
    18	  - id: gh11-p1-chunkers
    19	    name: "p1: Tree-sitter / Markdown / file-level chunkers with path-prefixed text"
    20	    reviewer: agy
    21	    brief: PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p1-chunkers.md
    22	    artifact: xyz/,tests/,pyproject.toml
    23	    depends_on: gh11-p0-scaffold
    24	    turn_timeout_s: 1800
    25	    max_review_rounds: 3
    26	
    27	  - id: gh11-p2-store
    28	    name: "p2: SQLite store — chunks + FTS5 + vec0, provider-keyed embed cache, drift guard"
    29	    reviewer: agy
    30	    brief: PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p2-store.md
    31	    artifact: xyz/,tests/,pyproject.toml
    32	    depends_on: gh11-p1-chunkers
    33	    turn_timeout_s: 1800
    34	    max_review_rounds: 3
    35	
    36	  - id: gh11-p3-retrieve
    37	    name: "p3: BM25 + dense -> RRF -> cross-encoder rerank -> tau, with latency instrumentation"
    38	    reviewer: agy
    39	    brief: PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p3-retrieve.md
    40	    artifact: xyz/,tests/,pyproject.toml
    41	    depends_on: gh11-p2-store
    42	    turn_timeout_s: 1800
    43	    max_review_rounds: 3
    44	
    45	  - id: gh11-p4-roundtrip
    46	    name: "p4: xyz CLI + real ingest/query round-trip on LTVera-Pandas, scored and recorded"
    47	    reviewer: agy
    48	    brief: PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p4-roundtrip-eval.md
    49	    artifact: xyz/,tests/,pyproject.toml,PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md,PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md
    50	    depends_on: gh11-p3-retrieve
    51	    turn_timeout_s: 7200
    52	    max_review_rounds: 3
     1	---
     2	title: GH-11 marathon brief — gh11-p0-scaffold
     3	status: active
     4	created: 2026-09-05
     5	updated: 2026-09-06
     6	owner: Noel Saw
     7	goal: Phase brief consumed by marathon-drive.sh for phase gh11-p0-scaffold; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
     8	roadmap_exempt: true
     9	---
    10	
    11	# Phase brief — gh11-p0-scaffold: Phase 0 close-out (constraints, pyproject, `xyz/` skeleton, gate)
    12	
    13	## Status
    14	
    15	| What was just completed | What's next |
    16	|---|---|
    17	| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p0-scaffold`; outcome recorded in the capture doc. |
    18	
    19	Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
    20	(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
    21	Canonical doc: `PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md`
    22	→ "Phase 0 — Decision lock and repo scaffolding", steps 2-3.
    23	
    24	## Environment contract (read first — applies to every phase)
    25	
    26	`validate.sh` defines it; the operator exports the values when launching the marathon:
    27	
    28	| Variable | Meaning | Default |
    29	|---|---|---|
    30	| `XYZ_PY` | interpreter carrying the pinned deps (`sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`, `tree-sitter`, `tree-sitter-language-pack`, `pytest`, `psutil`) | `<repo>/.venv/bin/python` |
    31	| `XYZ_SCRATCH` | where generated evidence goes (index DBs, eval JSON, logs); swept by the harness, never committed | `<repo>/.relay-scratch` |
    32	| `XYZ_EVAL_REPO` | the corpus for the p4 round-trip (an absolute path to a LTVera-Pandas checkout) | unset — p4 fails fast if unset |
    33	| `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `TOKENIZERS_PARALLELISM=false` | no network inside a turn; both models are already in the HF cache | exported by `validate.sh`; **export them yourself before any ad-hoc smoke** |
    34	
    35	Rules: run Python only as `"$XYZ_PY"`; **no `pip install`**, no editable install (it writes
    36	`*.egg-info/` into the tree, an off-lane write) — the package is imported from the tree via
    37	`PYTHONPATH=<repo>` which `validate.sh` sets and `pyproject.toml` mirrors for pytest; write scratch
    38	only under `$XYZ_SCRATCH`.
    39	
    40	Readiness is **proven before the marathon fires**, not assumed: the operator runs `prelaunch.sh`
    41	with the same `XYZ_PY`, which really imports every dependency, instantiates the Python / JS / TS /
    42	TSX / PHP parsers, and loads **both models offline with their real classes** (encode + predict),
    43	then writes `<venv>/xyz-prelaunch.json`. `validate.sh`'s `env preflight` requires that marker (for
    44	this exact interpreter) and re-does the cheap parts (real imports, parser creation, FTS5/vec0). If
    45	the marker is missing or names another interpreter, the gate fails with the command to run — do not
    46	work around it. Before starting, run `bash validate.sh` once: `env preflight` must pass; the later
    47	sections are expected to fail until this phase is done.
    48	
    49	## Task
    50	
    51	1. **Constraints into `GUIDING-PRINCIPLES.md`** (canonical Phase 0 step 3). The file is still the
    52	   PDDA-repo boilerplate. Replace its `## Purpose` paragraph with one that describes *this* repo
    53	   (XYZ Code Intelligence: local-first code retrieval, successor to Ask-Self) and append two numbered
    54	   principles after the existing eight, in the same voice:
    55	   - **Local-first.** Ingest, embedding, retrieval and reranking run on the operator's machine with
    56	     no network call on the query path. A cloud API may appear only as an explicitly opt-in
    57	     comparison arm, never as the primary lane.
    58	   - **Permissively licensed models only.** Every model weight the pipeline loads is Apache-2.0 or
    59	     MIT (or equivalent). Verify the licence on the model card before a model enters any run; a
    60	     model whose licence is unstated or non-commercial is rejected, not deferred.
    61	   Leave the other principles intact (they still govern the PDDA docs in this repo).
    62	2. **`pyproject.toml`** at the repo root: name `xyz-code-intelligence`, version `0.5.0.dev0`,
    63	   `requires-python = ">=3.11"`, dependencies pinned to the versions `"$XYZ_PY" -m pip list` shows
    64	   for `sentence-transformers`, `torch`, `einops`, `numpy`, `sqlite-vec`, `tree-sitter`,
    65	   `tree-sitter-language-pack`; optional group `dev = ["pytest", "psutil"]`; console script
    66	   `xyz = "xyz.cli:main"` (declared for a future install — not installed in this marathon);
    67	   setuptools backend with `[tool.setuptools.packages.find] include = ["xyz*"]`;
    68	   `[tool.pytest.ini_options] pythonpath = ["."]` and `testpaths = ["tests"]`.
    69	3. **`xyz/` package skeleton** (canonical Phase 0 step 2), modules only — docstrings and
    70	   `__version__`, no logic:
    71	   - `xyz/__init__.py` (`__version__ = "0.5.0.dev0"` — `validate.sh` asserts this exact string)
    72	   - `xyz/__main__.py` → `raise SystemExit(main())` from `xyz.cli`
    73	   - `xyz/ingest/__init__.py`, `xyz/index/__init__.py`, `xyz/retrieve/__init__.py`,
    74	     `xyz/eval/__init__.py`
    75	   - `xyz/cli.py`: `main(argv: list[str] | None = None) -> int` (argparse). `--version` prints the
    76	     version and returns 0; no arguments prints the subcommand list (`ingest`, `query`, `eval`, all
    77	     "not implemented until gh11-p4") and returns 0; an unknown subcommand returns 2.
    78	4. **`tests/`**: `tests/__init__.py`; `tests/test_smoke.py` asserting `xyz.__version__ ==
    79	   "0.5.0.dev0"`, `main([])` returns 0, `main(["--version"])` returns 0, `main(["bogus"])` returns 2.
    80	5. **`validate.sh`** already asserts everything above (package presence, exact version,
    81	   `python -m xyz --version`, pytest). Do not edit it in this phase unless a check is wrong — if so,
    82	   say exactly what and why in the relay.
    83	
    84	## Non-goals
    85	
    86	No chunking, embedding, SQL or retrieval code. No changes to `.embed-tmp/`. No `AGENTS.md`
    87	rewrite (parked). No `CHANGELOG.md` entry — the orchestrator writes it at PR time.
    88	
    89	## Definition of done
    90	
    91	- `bash validate.sh` exits 0 end to end.
    92	- `GUIDING-PRINCIPLES.md` contains both new principles and a repo-accurate Purpose; the eight
    93	  original principles are unchanged; `./utils/pdda/pdda.sh governance` reports no new error.
    94	- Red control (do it, quote the output in the relay, then restore): change `__version__` to
    95	  `"0.0.0"` → `validate.sh` must fail at "import smoke (exact version)"; delete
    96	  `xyz/__main__.py` → it must fail at "package presence".
     1	---
     2	title: GH-11 marathon brief — gh11-p1-chunkers
     3	status: active
     4	created: 2026-09-05
     5	updated: 2026-09-06
     6	owner: Noel Saw
     7	goal: Phase brief consumed by marathon-drive.sh for phase gh11-p1-chunkers; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
     8	roadmap_exempt: true
     9	---
    10	
    11	# Phase brief — gh11-p1-chunkers: AST / Markdown / file-level chunkers with path-prefixed text
    12	
    13	## Status
    14	
    15	| What was just completed | What's next |
    16	|---|---|
    17	| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p1-chunkers` after `gh11-p0-scaffold`; outcome recorded in the capture doc. |
    18	
    19	Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
    20	(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
    21	Canonical doc → "Phase 1 — Chunking + hybrid retrieval skeleton", step 1.
    22	Environment contract: see `brief-p0-scaffold.md` (`XYZ_PY`, `XYZ_SCRATCH`, offline env, no installs).
    23	
    24	## Context you must read before coding
    25	
    26	- `.embed-tmp/scripts/embed_repos.py` — the current (throwaway) chunker. What it actually has:
    27	  `INCLUDE_EXT`, `iter_files(...)` (line ~106), and per-chunk records carrying **`path`,
    28	  `start_line`, `end_line`, `text`**, to which `id` and `repo` are added (lines ~136-140, ~160-161).
    29	  It has **no** `qualified_name`, `kind`, `content_sha` or `embedded_text` — those are **new** fields
    30	  this phase introduces. The new chunker must still emit `path`, `start_line`, `end_line`, `text`
    31	  so the existing scorer can read an exported `chunks.jsonl`.
    32	- Issue #8 (closed): leading each chunk's embedded text with the file's relative path was the
    33	  largest quality jump in the project (MRR 0.80 → 0.98). Issue #2 (closed): YAML and Dockerfiles
    34	  were skipped, a silent infra blind spot. Both are re-implemented here because that code is not on
    35	  this branch.
    36	- `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md` (lines ~174-179): the model's real memory guard is
    37	  `max_seq_length = 2048` tokens; the 6,000-character split below is a **character heuristic**
    38	  chosen to sit under that window with headroom, not a tokenizer bound. The p2 embedder enforces the
    39	  token cap; this phase only bounds characters.
    40	
    41	## Task
    42	
    43	Implement `xyz/ingest/`:
    44	
    45	1. `xyz/ingest/walk.py` — `walk_repo(root, include_ext=DEFAULT_INCLUDE, exclude_dirs=DEFAULT_EXCLUDE,
    46	   include_prefixes=None)` yielding `(rel_path, bytes)` in sorted order. `include_prefixes` (a
    47	   tuple of repo-relative directory prefixes, e.g. `("scripts/", "app/")`) restricts the walk **while
    48	   keeping paths relative to `root`** — this is the p4 subset fallback; it must not change any
    49	   `rel_path`. `DEFAULT_INCLUDE` = the current `INCLUDE_EXT` list **plus** `.yml .yaml .toml .ini
    50	   .cfg .json .sql .html .twig` and the filenames `Dockerfile`, `docker-compose*.yml`, `Makefile`,
    51	   `*.blade.php`, `.env.example`. `DEFAULT_EXCLUDE` = `.git .venv node_modules __pycache__ dist build
    52	   temp .embed-tmp .xyz .relay-scratch marathon-system relay-system`. Skip files > 1 MiB and binary
    53	   files (NUL byte in the first 8 KiB). `root` must be an existing directory → else `ValueError`.
    54	   **Traversal errors are not exclusions:** an `OSError` from directory enumeration or from reading
    55	   a candidate file is appended to `errors` (a caller-supplied `list[str]`, required argument) with
    56	   the path, and the walk continues; skips by extension, size, binary sniff, `exclude_dirs` or
    57	   `include_prefixes` are intentional and are **not** recorded there. Callers that mutate an index
    58	   (p2 `Store.ingest`) must treat a non-empty `errors` as an incomplete walk and refuse to prune.
    59	2. `xyz/ingest/chunk.py` — a `Chunk` dataclass: `repo, path, kind, qualified_name, start_line,
    60	   end_line, text, embedded_text, content_sha` (`content_sha` = sha256 of `embedded_text`), and
    61	   `ChunkResult(chunks: list[Chunk], warnings: list[str])`. `embedded_text` **always begins with the
    62	   relative path on its own line**, then a blank line, then `text` (#8).
    63	   `chunk_file(repo, rel_path, source: bytes) -> ChunkResult` dispatches on extension:
    64	   - **Python, JS, TS/TSX/JSX, PHP** → Tree-sitter via `tree_sitter_language_pack.get_parser(lang)`.
    65	     One chunk per top-level function / class / method (methods become their own chunks with
    66	     `qualified_name = "Class.method"`); the file's remaining top-level statements (imports, module
    67	     docstring, constants) form one `kind="module"` chunk whose `start_line`/`end_line` are the first
    68	     and last line of that residual text and whose `text` joins the pieces with a `# …` gap marker.
    69	   - **Markdown** → one chunk per heading section (level ≤ 3); preamble before the first heading is
    70	     its own chunk; `qualified_name` = heading path joined with ` > `.
    71	   - **everything else** → file-level chunks, `kind="file"`, `qualified_name = rel_path`.
    72	   - **Hard bound, every kind:** any chunk whose `text` exceeds **6,000 characters** is split — at
    73	     the nearest blank line before the limit if one exists in the last 1,500 characters, otherwise
    74	     **hard-cut at 6,000** — into parts ≤ 6,000 chars with ~150-char overlap, each keeping the
    75	     `qualified_name` with a `#2`, `#3` suffix and correct `start_line`/`end_line`. A single-line
    76	     6,001-char file must still yield ≥ 2 chunks (this is a test).
    77	   - A parse failure never aborts ingest: fall back to the file-level chunker and append a warning.
    78	3. `xyz/ingest/__init__.py` exports `walk_repo`, `chunk_file`, and
    79	   `chunk_repo(repo, root, **walk_kwargs) -> ChunkResult` (all chunks + all warnings; p2's
    80	   `Store.ingest` reports the warnings). The p2 `IngestReport` is the one channel for warnings.
    81	4. Tests in `tests/test_chunkers.py` on a **fixture tree `tests/fixtures/mini-repo/`** that you
    82	   create: a Python file with module docstring, two functions and a class with two methods; a TS
    83	   file with an exported function and a class; a PHP file with a class; a Markdown file with three
    84	   headings; `config.yml`; `Dockerfile`; a binary blob; `node_modules/ignored.js`; a generated
    85	   single-line 6,001-char `.txt`; a generated Markdown section > 6,000 chars; a deliberately broken
    86	   Python file. Assert: chunk counts and `qualified_name`s per file; `start_line`/`end_line` match
    87	   the source; every `embedded_text` starts with `path + "\n\n"`; YAML and Dockerfile produce chunks
    88	   (#2); binary and `node_modules` produce none; both oversize cases split with suffixes and ≤ 6,000
    89	   chars each; the broken file yields a file-level chunk plus one warning; `include_prefixes`
    90	   restricts the walk without altering `rel_path`; a missing root raises; output is deterministic
    91	   (two runs equal); with `os.scandir` monkeypatched to raise `PermissionError` for one subdirectory
    92	   **after** at least one file was yielded, the walk still yields the other files and `errors` has
    93	   exactly one entry naming that subdirectory, while an excluded dir or a binary skip adds nothing
    94	   to `errors`.
    95	
    96	## Non-goals
    97	
    98	No embedding, no SQLite, no CLI. Do not modify `.embed-tmp/`.
    99	
   100	## Definition of done
   101	
   102	- `bash validate.sh` green; every assertion above present in `tests/test_chunkers.py`.
   103	- Red control (show once in the relay, then restore): remove the path-prefix line from
   104	  `embedded_text` → the prefix test fails; remove the hard-cut branch → the single-line 6,001-char
   105	  test fails.

exec
/bin/zsh -lc 'nl -ba prelaunch.sh; nl -ba validate.sh' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p1-chunkers.md | sed -n '40,110p'; nl -ba PROJECT/2-WORKING/v0.5/GH-11-marathon/brief-p2-store.md | sed -n '45,122p'" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-603-dp0se3ww
 succeeded in 0ms:
    40	
    41	## Task
    42	
    43	Implement `xyz/ingest/`:
    44	
    45	1. `xyz/ingest/walk.py` — `walk_repo(root, include_ext=DEFAULT_INCLUDE, exclude_dirs=DEFAULT_EXCLUDE,
    46	   include_prefixes=None)` yielding `(rel_path, bytes)` in sorted order. `include_prefixes` (a
    47	   tuple of repo-relative directory prefixes, e.g. `("scripts/", "app/")`) restricts the walk **while
    48	   keeping paths relative to `root`** — this is the p4 subset fallback; it must not change any
    49	   `rel_path`. `DEFAULT_INCLUDE` = the current `INCLUDE_EXT` list **plus** `.yml .yaml .toml .ini
    50	   .cfg .json .sql .html .twig` and the filenames `Dockerfile`, `docker-compose*.yml`, `Makefile`,
    51	   `*.blade.php`, `.env.example`. `DEFAULT_EXCLUDE` = `.git .venv node_modules __pycache__ dist build
    52	   temp .embed-tmp .xyz .relay-scratch marathon-system relay-system`. Skip files > 1 MiB and binary
    53	   files (NUL byte in the first 8 KiB). `root` must be an existing directory → else `ValueError`.
    54	   **Traversal errors are not exclusions:** an `OSError` from directory enumeration or from reading
    55	   a candidate file is appended to `errors` (a caller-supplied `list[str]`, required argument) with
    56	   the path, and the walk continues; skips by extension, size, binary sniff, `exclude_dirs` or
    57	   `include_prefixes` are intentional and are **not** recorded there. Callers that mutate an index
    58	   (p2 `Store.ingest`) must treat a non-empty `errors` as an incomplete walk and refuse to prune.
    59	2. `xyz/ingest/chunk.py` — a `Chunk` dataclass: `repo, path, kind, qualified_name, start_line,
    60	   end_line, text, embedded_text, content_sha` (`content_sha` = sha256 of `embedded_text`), and
    61	   `ChunkResult(chunks: list[Chunk], warnings: list[str])`. `embedded_text` **always begins with the
    62	   relative path on its own line**, then a blank line, then `text` (#8).
    63	   `chunk_file(repo, rel_path, source: bytes) -> ChunkResult` dispatches on extension:
    64	   - **Python, JS, TS/TSX/JSX, PHP** → Tree-sitter via `tree_sitter_language_pack.get_parser(lang)`.
    65	     One chunk per top-level function / class / method (methods become their own chunks with
    66	     `qualified_name = "Class.method"`); the file's remaining top-level statements (imports, module
    67	     docstring, constants) form one `kind="module"` chunk whose `start_line`/`end_line` are the first
    68	     and last line of that residual text and whose `text` joins the pieces with a `# …` gap marker.
    69	   - **Markdown** → one chunk per heading section (level ≤ 3); preamble before the first heading is
    70	     its own chunk; `qualified_name` = heading path joined with ` > `.
    71	   - **everything else** → file-level chunks, `kind="file"`, `qualified_name = rel_path`.
    72	   - **Hard bound, every kind:** any chunk whose `text` exceeds **6,000 characters** is split — at
    73	     the nearest blank line before the limit if one exists in the last 1,500 characters, otherwise
    74	     **hard-cut at 6,000** — into parts ≤ 6,000 chars with ~150-char overlap, each keeping the
    75	     `qualified_name` with a `#2`, `#3` suffix and correct `start_line`/`end_line`. A single-line
    76	     6,001-char file must still yield ≥ 2 chunks (this is a test).
    77	   - A parse failure never aborts ingest: fall back to the file-level chunker and append a warning.
    78	3. `xyz/ingest/__init__.py` exports `walk_repo`, `chunk_file`, and
    79	   `chunk_repo(repo, root, **walk_kwargs) -> ChunkResult` (all chunks + all warnings; p2's
    80	   `Store.ingest` reports the warnings). The p2 `IngestReport` is the one channel for warnings.
    81	4. Tests in `tests/test_chunkers.py` on a **fixture tree `tests/fixtures/mini-repo/`** that you
    82	   create: a Python file with module docstring, two functions and a class with two methods; a TS
    83	   file with an exported function and a class; a PHP file with a class; a Markdown file with three
    84	   headings; `config.yml`; `Dockerfile`; a binary blob; `node_modules/ignored.js`; a generated
    85	   single-line 6,001-char `.txt`; a generated Markdown section > 6,000 chars; a deliberately broken
    86	   Python file. Assert: chunk counts and `qualified_name`s per file; `start_line`/`end_line` match
    87	   the source; every `embedded_text` starts with `path + "\n\n"`; YAML and Dockerfile produce chunks
    88	   (#2); binary and `node_modules` produce none; both oversize cases split with suffixes and ≤ 6,000
    89	   chars each; the broken file yields a file-level chunk plus one warning; `include_prefixes`
    90	   restricts the walk without altering `rel_path`; a missing root raises; output is deterministic
    91	   (two runs equal); with `os.scandir` monkeypatched to raise `PermissionError` for one subdirectory
    92	   **after** at least one file was yielded, the walk still yields the other files and `errors` has
    93	   exactly one entry naming that subdirectory, while an excluded dir or a binary skip adds nothing
    94	   to `errors`.
    95	
    96	## Non-goals
    97	
    98	No embedding, no SQLite, no CLI. Do not modify `.embed-tmp/`.
    99	
   100	## Definition of done
   101	
   102	- `bash validate.sh` green; every assertion above present in `tests/test_chunkers.py`.
   103	- Red control (show once in the relay, then restore): remove the path-prefix line from
   104	  `embedded_text` → the prefix test fails; remove the hard-cut branch → the single-line 6,001-char
   105	  test fails.
    45	   auto: MPS if available else CPU; `EMBED_BATCH_SIZE` / `EMBED_MAX_THREADS` env like the old
    46	   script). Constructor accepts an injectable `model_factory` so a test can pass a stub and assert:
    47	   `max_seq_length` was set to **2048**, `encode_query` prepends the exact prefix, and
    48	   `encode_documents` does **not**. `tests/fakes.py` provides `FakeEmbedder(model_id="fake",
    49	   dim=8, provider="fake")` (deterministic hash-based unit vectors, counts calls) used by every
    50	   store/retrieve test.
    51	2. `xyz/index/store.py` — `Store`, the **only writer** of an index:
    52	   - tables: `meta(key, value)` holding `model`, `dim`, `provider`, `schema_version`;
    53	     `files(repo, path, file_sha, chunk_count, ingested_at, PRIMARY KEY(repo, path))`;
    54	     `chunks(id INTEGER PRIMARY KEY, repo, path, kind, qualified_name, start_line, end_line,
    55	     content_sha, text, embedded_text)`; `chunks_fts` = FTS5 **external-content** table over
    56	     `chunks(embedded_text, qualified_name, path)` kept in sync by insert/delete/update triggers;
    57	     `chunks_vec` = `vec0(embedding float[<dim>])` with rowid = `chunks.id`;
    58	     `embed_cache(content_sha, model, dim, provider, vector BLOB, PRIMARY KEY(content_sha, model,
    59	     dim, provider))`.
    60	   - `Store.open(db_path, embedder)`: creates the schema on first use and writes `meta`; on an
    61	     existing DB raises `IndexMismatch` naming the differing field if **any** of `model`, `dim`,
    62	     `provider` differ. `Store.check_embedder(embedder)` exposes the same check for readers (p3).
    63	   - `Store.ingest(repo, root, chunker=chunk_repo, include_prefixes=None) -> IngestReport`, the
    64	     planner: **walk first, mutate second.** Run the p1 walk (honouring `include_prefixes`) to
    65	     completion into an in-memory list of `(rel_path, bytes)` with an `errors` list; a walk that
    66	     yields **zero files raises `EmptyCorpus`**, and a walk with **any traversal error raises
    67	     `WalkIncomplete`** (listing the errors) — both **before any write or delete**. Only a complete
    68	     walk may proceed. For each file compute `file_sha`; same sha in `files` → skip;
    69	     else delete that file's chunks (FTS/vec rows via triggers/explicit delete) and insert the new
    70	     ones. Embed only chunks whose `content_sha` is absent from `embed_cache` for this
    71	     `(model, dim, provider)`; cache every new vector. **Pruning is scoped:** files in `files` for
    72	     this `repo` that are absent from the walk are pruned only when they fall under the walked scope
    73	     (all of the repo when `include_prefixes` is None, else only under those prefixes).
    74	     `IngestReport` carries `files_seen, files_skipped, files_reingested, files_pruned,
    75	     chunks_written, chunks_embedded, cache_hits, warnings, seconds`.
    76	   - `Store.stats()` → row counts of `chunks`, `chunks_fts` (via `SELECT count(*) FROM chunks_fts`),
    77	     `chunks_vec`, `embed_cache`, `files`; `Store.fts_match(token, limit)` → chunk ids whose FTS row
    78	     matches (used by tests to prove the inverted index, not just the row count, is current).
    79	   - One transaction per file; WAL journal mode; `PRAGMA foreign_keys=ON`.
    80	3. Tests in `tests/test_store.py` with `FakeEmbedder` on the p1 fixture copied to a tmp dir:
    81	   - first ingest: `chunks_embedded == chunks_written > 0`; `chunks`, `chunks_fts`, `chunks_vec`
    82	     counts equal; `fts_match` finds a token that exists only in one fixture file;
    83	   - **second ingest, unchanged tree: `files_skipped == files_seen`, `files_reingested == 0`,
    84	     `chunks_written == 0`, embedder call count 0, < 1 s** (all five asserted separately — the
    85	     red control below depends on it);
    86	   - in one fixture file, **replace** the unique token `OLDTOKEN` (present in exactly one chunk)
    87	     with `NEWTOKEN`, leaving that file's other chunks byte-identical: only that file is re-ingested
    88	     (`files_reingested == 1`), its unchanged chunks are cache hits (embedder called once, for the
    89	     changed chunk), `fts_match("NEWTOKEN")` returns that chunk and `fts_match("OLDTOKEN")` is empty;
    90	   - delete one file: its chunks vanish from all three tables and `fts_match` of its unique token is
    91	     empty; with `include_prefixes` naming a different directory, that deleted file is **not** pruned;
    92	   - an empty directory raises `EmptyCorpus` and writes nothing;
    93	   - **incomplete walk:** after a full ingest, monkeypatch `os.scandir` to raise `PermissionError`
    94	     for one subdirectory (after other files have been yielded) → `ingest` raises `WalkIncomplete`,
    95	     and every pre-existing `chunks` / `chunks_fts` / `chunks_vec` / `files` row survives unchanged
    96	     (counts and `fts_match` of a token from the unreadable subdirectory still succeed);
    97	   - `IndexMismatch` is raised separately for a differing `model_id`, a differing `dim`, and a
    98	     differing `provider` (three tests);
    99	   - a chunk's vector read back from `chunks_vec` equals its cached vector;
   100	   - `CodeRankEmbedder` with the stub factory: `max_seq_length == 2048`, query prefix present on
   101	     queries only.
   102	
   103	## Non-goals
   104	
   105	No query path (p3), no CLI (p4). No real model in pytest.
   106	
   107	## Definition of done
   108	
   109	- `bash validate.sh` green; every test above present and passing.
   110	- One real smoke, out of pytest and under the offline env: `CodeRankEmbedder().encode_query("sort a
   111	  list")` → shape `(768,)`, norm ≈ 1.0, and `model.max_seq_length == 2048` — quote all three.
   112	- Red controls (show once each in the relay, then restore): (a) remove the `files` sha
   113	  short-circuit → the `files_skipped == files_seen` / `files_reingested == 0` assertions fail even
   114	  though the cache still keeps embedder calls at 0; (b) drop the FTS insert trigger → the
   115	  `fts_match("NEWTOKEN")` test fails while the count test may still pass; (c) disable the
   116	  `WalkIncomplete` guard (ignore `errors`) → the incomplete-walk test fails because the unreadable
   117	  subdirectory's rows get pruned.

codex
VOTE: FIRE

Four rounds have exhausted the useful plan-review frontier. They found genuine launch defects, and the final control now fingerprints library-resolved cache paths and rejects environment drift (`prelaunch.sh:32-53`; `validate.sh:29-50`). The implementation remains easy to abandon (`GH-11-ACT1-HYBRID-RETRIEVAL.md:160-161`), while every sequential phase already receives 2–3 build-review rounds (`MARATHON.yaml:10-52`). A fifth planning pass has lower value than exposing the design to actual code.

- [Pass] The prelaunch checker is now adequate and falsifiable; all four cache-variable drift controls were reported rejected (`gh11-act1-plan-review.md:213-228`).
- [Should] Yes—at this point it is overengineering. Rounds 1–2 earned their cost, and round 3 fixed a meaningful stale-marker flaw. Round 4’s cache-alias binding was defensible, but another round would be polishing a once-per-launch operator control while the product package still does not exist (`GH-11-ACT1-HYBRID-RETRIEVAL.md:44-48`).
- [Pass] The single highest risk I would accept is semantically weak or silently degraded Tree-sitter chunking beyond the fixture set. In p1 output, watch qualified names, source-line boundaries, residual module chunks, and parse-fallback warnings—not merely chunk counts (`brief-p1-chunkers.md:59-94`).
- [Blocker] The one thing that would change my vote: `prelaunch.sh` fails when rerun immediately before launch with the exact interpreter, cache environment, and reranker the marathon will inherit.

RECOMMENDATION: Fire now; spend the next review token on p1’s actual chunker output, not a fifth review of preflight machinery.
tokens used
52,655
VOTE: FIRE

Four rounds have exhausted the useful plan-review frontier. They found genuine launch defects, and the final control now fingerprints library-resolved cache paths and rejects environment drift (`prelaunch.sh:32-53`; `validate.sh:29-50`). The implementation remains easy to abandon (`GH-11-ACT1-HYBRID-RETRIEVAL.md:160-161`), while every sequential phase already receives 2–3 build-review rounds (`MARATHON.yaml:10-52`). A fifth planning pass has lower value than exposing the design to actual code.

- [Pass] The prelaunch checker is now adequate and falsifiable; all four cache-variable drift controls were reported rejected (`gh11-act1-plan-review.md:213-228`).
- [Should] Yes—at this point it is overengineering. Rounds 1–2 earned their cost, and round 3 fixed a meaningful stale-marker flaw. Round 4’s cache-alias binding was defensible, but another round would be polishing a once-per-launch operator control while the product package still does not exist (`GH-11-ACT1-HYBRID-RETRIEVAL.md:44-48`).
- [Pass] The single highest risk I would accept is semantically weak or silently degraded Tree-sitter chunking beyond the fixture set. In p1 output, watch qualified names, source-line boundaries, residual module chunks, and parse-fallback warnings—not merely chunk counts (`brief-p1-chunkers.md:59-94`).
- [Blocker] The one thing that would change my vote: `prelaunch.sh` fails when rerun immediately before launch with the exact interpreter, cache environment, and reranker the marathon will inherit.

RECOMMENDATION: Fire now; spend the next review token on p1’s actual chunker output, not a fifth review of preflight machinery.
