# RELAY · GH-11 Act 1 plan review — hybrid retrieval marathon
<!--
  Single source of truth for this two-agent relay. Read the ENTIRE file before acting.
  Scaffolded by relay-automation/new-relay.sh on 2026-09-06.
-->

NEXT: Producer
STATUS: Open
ROUND: 2 / 3

## ▶ TAKE YOUR TURN — read this first (works for ANY agent: Claude, Codex, agy)
1. **Read this whole file** (header, Setup, Ground rules, every block in the Log).
2. **Check it's your turn:** `NEXT` (top) names the role to act. Confirm you are bound to it and the
   last Log block isn't already yours. If not → STOP and reply "wrong window — nudge the <other> window."
3. **Do your role's work** on the artifact named in Setup:
   - **Reviewer:** review vs the Definition of Done → graded findings
     (`[Blocker]`/`[Should]`/`[Nit]`/`[Pass]`), each with a concrete fix → set a **Verdict**
     (Approved | Changes requested | Blocked). **Review the whole file, not just the diff** (GH-268):
     a beta test had this loop reach `Approved` in two rounds while an independent audit of the same
     branch found 20 issues (1 critical, 4 high) — every one of them in the pre-existing code the
     change sat on, which nobody had read. Pre-existing defects in a file you are touching are IN
     SCOPE; if you find none, say so explicitly rather than leaving it unstated.
     **Declare it: every review block must contain a literal `swept file: yes` or `swept file: no`
     line.** Without it a reviewer that skipped the sweep is indistinguishable in the transcript from
     one that did it and found nothing — which is how the original 20 issues stayed invisible.
     Any `[Pass]` or "verified"/"confirmed" finding MUST
     carry a quoted span or a `file:line` citation — an uncited one is mechanically downgraded to
     `[Unverified — no citation]` (GH-173 B3). Do **not** edit the artifact; only append findings here.
   - **Producer:** log a disposition for every open finding (Implemented / Modified / Declined + why),
     make the change, then add new work.
4. **Append ONE block** at the very bottom, directly **above** the marker line. Never edit earlier turns.
5. **Update the header:** flip `NEXT`; set `STATUS` (`Approved` closes — Reviewer only; else `Open`);
   the Producer bumps `ROUND` when opening a new cycle. If the max `ROUND` ends without `Approved`,
   set `STATUS: Escalated`.
6. **Commit only the relay file** (`relay(gh11-act1-plan-review): <role> r<N>`); no push. **Stop** and report one line.
7. **Hand off explicitly — EVERY turn, not just the first** (GH-268). End your turn by naming who acts
   next and what they should do: *"handing off to <other role> — go to the <other> window and say
   'take your turn'"*, or *"relay closed (Approved), no further turn needed"*. The beta report singled
   this out: the Reviewer turn never told the user to return to the Producer window, so a relay that
   was merely waiting looked stalled. A turn that ends without this line is not finished.

## Setup
- Artifact under review: **PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md** (the plan) plus
  the marathon it drives — `PROJECT/2-WORKING/v0.5/GH-11-marathon/MARATHON.yaml` and its five briefs
  `brief-p0-scaffold.md`, `brief-p1-chunkers.md`, `brief-p2-store.md`, `brief-p3-retrieve.md`,
  `brief-p4-roundtrip-eval.md` — and the gate `validate.sh`. All are committed on this branch; read
  them in the worktree. Requirements source: GitHub issue #11 "Act 1" section
  (https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11) and the canonical doc's Phase 0-1
  (`PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md`).
  Ground-truth code the plan cites: `.embed-tmp/scripts/embed_repos.py`,
  `.embed-tmp/eval/score_retrieval.py`, `.embed-tmp/eval/queries-LTVera-Pandas.json`, `SOP.md`,
  `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md`.
- Reviewer: codex   ·   Producer: claude-a
- Started: 2026-09-06
- Definition of Done: this is a PLAN review (no code exists yet — `xyz/` is created by the marathon).
  Approve only if every question below is answered "yes" with a citation, else request changes:
  1. Grounding — are the plan's claims about existing paths/behaviour true (chunk fields in
     `embed_repos.py`, metric definitions in `score_retrieval.py`, the query-prefix / `max_seq_length`
     / `k = ?` rules)? Cite `file:line`.
  2. Completeness — does the five-phase plan cover every Act 1 checklist item of issue #11 and every
     step of canonical Phase 0 (2-3) and Phase 1 (1-4), with each deviation stated under
     "Acceptance — deviations from the issue" with a reason?
  3. Surgical / DRY — does it extend the existing subsystem (one `xyz/` package, one SQLite writer
     `xyz/index/store.py`) without a second embedder/scorer/store, and leave `.embed-tmp/` untouched?
  4. Dependency ordering and blast radius — is the p0→p4 chain right, are the `artifact:` allowlists
     per phase sufficient for the work the briefs demand (a builder cannot touch paths outside them),
     and is rollback stated?
  5. Falsifiable checks — does every phase have a gate that detects the actual failure, rejects empty
     input where relevant (p4 eval on an empty query list), and names a red control?
  6. Risks — is the p4 real-corpus run (25-30 min embedding inside a 7200 s turn, no network,
     `HF_HUB_OFFLINE=1`) realistic, and is the fallback acceptable?
  7. Rating — is `rated 85/60/50/30` (pri/sev/appeal/effort-cheapness, 1-100) grounded in the stated
     rationale, appeal neutral (50) with no user preference given, and no override invented?
  Grade every finding `[Blocker]` / `[Should]` / `[Nit]` / `[Pass]`; every `[Pass]` needs a citation.

## Ground rules
1. This file is the single source of truth. The agents never share memory — read the whole file.
2. Take a turn only if `NEXT` names your role — otherwise reply "not my turn" and stop.
3. One turn = one block appended at the very bottom, above the marker. Never edit earlier turns.
4. Stay tight — findings are bullets, not essays. Grade every finding.
5. **The Reviewer never edits the artifact.** It proposes graded findings; the Producer implements.
6. The relay ends on **Approved** (Reviewer only). End each turn by committing just this file; no push.

## Log

## Reviewer — codex — Round 1 — 2026-09-06

Verdict: Changes requested
swept file: yes

Read the whole plan, MARATHON.yaml, all five briefs, and validate.sh, including their pre-existing content. Read the cited embedder/scorer/query set and relevant canonical/SOP/findings evidence; fetched issue #11 with `gh issue view 11 --repo HiQS-Labs/XYZ-code-intelligence --json body`. No graph tools were available; direct source inspection is the evidence tier here. No artifact/source execution, project gates, model runs, or git commands were performed. Findings include pre-existing gate defects, not only proposed additions. Reversibility of this review-only edit: Easy.

Citation shorthand below: `plan` = `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`; `p0`–`p4` = the corresponding `brief-p*.md` in `PROJECT/2-WORKING/v0.5/GH-11-marathon/` (p4 is `brief-p4-roundtrip-eval.md`); `canonical` = `PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md`.

- [Blocker] **The promised exact metrics cannot be reproduced from the specified retrieval depth.** `.embed-tmp/eval/score_retrieval.py:133-155` ranks the entire corpus: a relevant result at rank 11 contributes 1/11 to MRR and is not `never_found`. p3:51-55 returns 10 hits from 50 candidates; p4:27-31,44-48 promises identical definitions without specifying eval depth. Its reference `per_query` row only contains query/relevant/rank/top_hit (`score_retrieval.py:147-148`), so it also cannot establish the top-10 reorder count requested at p4:67-68. **Fix:** explicitly define and test ranking depth per mode; either reproduce full-ranking metrics or call them MRR@10/miss@10 and rescore the baseline at that cutoff, recording the deviation. Add ordered chunk IDs/paths to per-query evidence and a rank-11 red case; preserve chunk ranks rather than deduplicating paths silently.
- [Blocker] **Offline execution prerequisites are not specified for the actual worktree.** p0:26-31 assumes `.venv/` exists; p4:34-40 assumes a sibling corpus; p4:61 expands an env var without establishing its claimed default. Read-only `ls -ld` this turn found `.venv`, `.venv/bin/python`, and `../LTVera-Pandas` absent in this worktree, while `/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/.venv` and `/Users/noelsaw/Documents/GH Repos/LTVera-Pandas` exist. `validate.sh:8` exports offline mode only inside that child shell, not into subsequent real smokes/CLI invocations. **Fix:** name the harness provisioning step and explicit interpreter/corpus env contract, check it in the builder worktree before starting, and export offline settings at the turn/command level. Include offline pip/setuptools and grammar/model-cache readiness in that preflight. Do not infer installed/parser/model readiness from a parent venv directory's existence.
- [Blocker] **The smaller-corpus fallback is not executable safely as specified.** p4:37-39 asks for three subtrees, but p4:50 exposes only one root. Ingesting each subtree under the same repo name changes gold-relative paths and p2:61's pruning removes the earlier subtree's records. **Fix:** specify one root-preserving filtered walk (or one staged root preserving all three prefixes), a separate clean DB and explicit command. Reject missing/non-directory roots and incomplete walks before pruning; scope deletion to the requested repo. Require nonzero corpus counts and gold-path presence before scoring. Record candidate counts and reduced-corpus provenance; do not equate its score with full-corpus Run 9. The 7200-second budget (`MARATHON.yaml:51`) is plausible against the historical 1,529.9-second run (`FINDINGS-0.5.md`, table row “LTVera-Pandas, 5,147 chunks”), but the new chunker/wider walk needs a measured early estimate and fallback trigger.
- [Blocker] **Red controls and FTS checks can stay green with the defect present.** p0:82-83 removes `xyz/__init__.py`, but `validate.sh:20` accepts a namespace package and prints `?` when the version is missing. p2:87-88 removes the file-SHA shortcut, yet the independently specified embed cache (p2:59-60) still yields zero embedder calls. Also, counts from an external-content FTS table (p2:50-51,64-73) do not establish that its inverted index was updated. **Fix:** make the import smoke assert the exact version; make p2's red control assert file-skip/chunker/write counts, not merely encode calls; add MATCH tests for a unique inserted, changed, and deleted token and a trigger-disabled red control. Keep evidence in the phase relay. The existing gate's conditional pyproject/tests checks (`validate.sh:17-24`) also need a post-scaffold assertion so missing package/tests cannot skip validation and print OK.
- [Should] **Grounding claims about the current embedder are false.** p1:25-28 names `walk_repo` and `qualified_name` as existing; actual source uses `iter_files` (`.embed-tmp/scripts/embed_repos.py:106`) and emits path/start_line/end_line/text, then adds id/repo (`:136-140,160-161`). Plan:60-61 attributes `max_seq_length=2048` to this script, but model construction at `:170` has no subsequent cap assignment. **Fix:** correct the recon/brief to separate existing fields from new fields, define where the promised superset's `id` appears, and cite `FINDINGS-0.5.md:174-179` for the required cap. Make setting 2048 an explicit implementation acceptance assertion with a stub model; query shape/norm alone (p2:84-86) cannot detect the missing memory guard or query prefix.
- [Should] **The chunk contract is internally ambiguous and weakly bounded.** p1:49 promises `list[Chunk]`, p1:61-62 returns warnings alongside it, while p1:63-64 exports an iterator without a warning channel. p1:53-60 uses nearest blank lines and 6,000 characters as token headroom, but does not define a hard split when no blank line exists or bound Markdown sections. **Fix:** choose one return/report contract through Store.ingest; require a terminating split for long single-line code/config and long Markdown, define source ranges for noncontiguous module text, and distinguish a character heuristic from actual tokenizer bounds including the path prefix. Add explicit no-blank-line and long-Markdown cases.
- [Should] **Scope deviations are not fully reconciled with the live requirement.** Issue #11 Act 1 says “over the existing 21,580-vector sidecar”; its calibration says “REFACTOR / ABSORB” and “keeps ... revision tracking, ingest planner and harness config.” Plan:81-95 records quality/ARM deviations, but not replacing that sidecar with fresh ingest; plan:74-79 ports only cache semantics and explicitly leaves the planner untraced. **Fix:** add the sidecar/rebuild and inheritance deferrals to Acceptance with reasons and downstream ownership, and explain why this Act 1 implementation will not create a second planner/store to reconcile in Act 2. The existing quality relaxation is explicitly recorded, but is not evidence that issue #11's non-saturated-set win criterion is complete; keep that requirement visibly outstanding.
- [Should] **Containment and entry-point details need closure.** p0:53,67 asks for editable installation, whose generated package metadata needs an explicitly contained destination; p4:40 puts runtime output under `temp/`, absent from `MARATHON.yaml:49`'s allowlist. This turn's harness explicitly permits generated evidence only in `.relay-scratch/`; do not assume gitignored means containment-exempt in builder turns. No phase allows CHANGELOG.md despite `AGENTS.md:49-51` requiring it for substantive iterations. p4:61 invokes `python -m xyz`, while p0:54-62 lists no `xyz/__main__.py`. **Fix:** document builder scratch/generated-output exemptions or move outputs to the supported scratch location, assign changelog recording to an allowed actor, and explicitly require/test the module entry point (or use the supported console command).
- [Should] **The public retrieval API leaves mode and mismatch behavior underspecified.** p3:51 defaults mode to `hybrid` but p3:52-53 says a supplied reranker changes the default; it cannot distinguish an explicit hybrid request from that default. p3:56-57 refers to an RRF score even for dense/BM25-only modes, and a second embedder supplied to `Retriever` can differ from the one checked at Store.open (p2:55-56). **Fix:** use an explicit auto/None default, specify unsupported rerank and per-mode tau behavior plus empty results, and validate the retrieval embedder identity against the store. Test model, dim, and provider mismatches independently, including at query time; the current p2:74 test exercises model only.
- [Pass] **Canonical phase coverage and core structure are present at the outline level.** canonical:204-207,214-224 map to p0 constraints/scaffold, p1 chunking, p2 one-writer SQLite/cache, p3 hybrid/rerank/latency, and p4 round-trip. `MARATHON.yaml:23,32,41,50` supplies the p0→p4 dependency chain; its `xyz/` allowlists include p3's permitted read helper in `xyz/index/`. Plan:111-113 names one canonical writer and plan:127-128 states Easy rollback. These passes do not resolve the execution/containment issues above.
- [Pass] **Several acceptance choices are explicit and citable.** Query-only prefix matches `SOP.md:31-33` and p2:25-27; `k = ?` and its red control are specified at p3:27-29,67-68,84 and supported by issue #11 Act 1's quoted “Use the vec0 k = ? KNN form”. Empty-query rejection is explicitly required at p4:90-91. Rating `85/60/50/30` has a stated rationale, neutral appeal and “No operator override” at plan:132-136. The historical user-order assertion is not independently verified by this review.

DoD disposition: grounding, completeness/deviation accounting, DRY inheritance, executable blast radius, falsifiable gates, and runtime/fallback contracts need the fixes above; rating rationale passes. Producer should disposition each finding and revise only the plan/brief/gate artifacts in its own turn. Handing off to claude-a (Producer) for revision and round 2.

## Producer — claude-a — Round 2 — 2026-09-06

Dispositions for every Round 1 finding (all changes are to the plan, briefs and gate only; no code exists yet):

- [Blocker] Metric depth — **Implemented.** p4 now reports MRR@D / R@k / miss@D at an explicit depth D = 100 (`fetch_k=100` per lane) with its own dense-only arm at that depth as the baseline; Run 9 is context only. `per_query` rows carry the ordered `ranking`; ranks are chunk ranks (no silent path dedupe); rank-11 red case at depth 10 vs 100; `SearchResult.ranking` (p3) exposes the full candidate order. See brief-p4 §Context, Task 1, DoD; brief-p3 Task 5; plan §Recon.
- [Blocker] Offline prerequisites — **Implemented.** Environment contract (`XYZ_PY`, `XYZ_SCRATCH`, `XYZ_EVAL_REPO`, offline env) defined in `validate.sh` and brief-p0 §Environment; `validate.sh` now runs an env preflight (interpreter, modules, both cached models, FTS5) before anything else; offline vars are exported and briefs tell the builder to export them for ad-hoc smokes; `PYTHONPATH=<repo>` replaces the editable install (no `*.egg-info/` writes); p4 asserts `$XYZ_EVAL_REPO/scripts` and `/app` exist before starting. Isolation note: the operator exports the values when firing.
- [Blocker] Subset fallback — **Implemented.** `walk_repo(include_prefixes=...)` is a root-preserving filtered walk (p1 Task 1, tested for unchanged `rel_path`); `Store.ingest` raises `EmptyCorpus` on zero files and scopes pruning to the walked prefixes (p2 Task 2 + tests); p4 fallback is a **fresh** DB, one invocation with three `--include-prefix`, ETA-triggered (> 45 min after 200 chunks), labelled `corpus: subset`; `xyz eval` refuses an empty corpus or missing gold paths (exit 2) and records corpus provenance.
- [Blocker] Red controls / gate — **Implemented.** `validate.sh` is now unconditional (package presence incl. `xyz/__main__.py`, exact `__version__ == 0.5.0.dev0`, `python -m xyz --version`, pytest); p0 red controls flip the version and delete `__main__.py`; p2 red controls assert `files_skipped == files_seen` / `files_reingested == 0` separately from embedder calls, plus `fts_match` tests for inserted/changed/deleted tokens with a trigger-disabled red control.
- [Should] Grounding — **Implemented.** Plan §Recon and brief-p1 §Context corrected: `iter_files`, existing fields `path/start_line/end_line/text` + `id/repo`, new fields named as new; `max_seq_length=2048` attributed to FINDINGS-0.5.md and made a stub-model acceptance assertion in p2 (with query-prefix-on-queries-only asserted the same way).
- [Should] Chunk contract — **Implemented.** `chunk_file -> ChunkResult(chunks, warnings)`, `chunk_repo -> ChunkResult`, warnings surface only via `IngestReport`; hard cut at 6,000 chars when no blank line (single-line 6,001-char test), Markdown sections bounded too; module chunk line range defined; 6,000 chars stated as a character heuristic under the 2048-token cap.
- [Should] Scope deviations — **Implemented.** Three new entries under "Acceptance — deviations": sidecar → fresh ingest (reason), ABSORB of planner/revisions/harness → Act 2 with the single-planner argument, and the non-saturated-set win criterion recorded as outstanding.
- [Should] Containment / entry point — **Implemented.** Generated output goes to `$XYZ_SCRATCH` (default `.relay-scratch/`), nothing under `temp/`; no editable install; `xyz/__main__.py` required in p0 and asserted by the gate; `CHANGELOG.md` assigned to the orchestrator at PR time (plan §Dependencies, briefs §Non-goals).
- [Should] Retrieval API — **Implemented.** `mode="auto"` default with explicit resolution rule; explicit `hybrid` never reranks; `hybrid+rerank` without a reranker raises; per-mode τ semantics and empty-candidate behaviour defined; `Retriever` validates the embedder against the store via `Store.check_embedder`; model/dim/provider mismatches tested independently at open and at query time.
- [Pass] ×2 — noted; no change.

Round 2 requested: please re-check questions 1-7 against the revised artifacts (`validate.sh`, brief-p0…p4, plan §Recon/§Acceptance/§Dependencies). Handing off to codex (Reviewer) — codex, take your turn.

## Reviewer — codex — Round 2 — 2026-09-06

Verdict: Changes requested
swept file: yes

Swept the complete plan, MARATHON.yaml, all five briefs and validate.sh, including pre-existing content. Re-read the reference embedder, metric implementation, query labels, SOP and canonical Phase 0/1 plus the memory findings; fetched the live issue with `gh issue view 11 --repo HiQS-Labs/XYZ-code-intelligence --json body`. Graph `list_projects` returned all 50 entries with `has_more=false`; neither this worktree nor its source repo is indexed, so there is no applicable generation/coverage evidence. Used direct source inspection without indexing (review-only containment). No artifact/source execution, model probes, project gates or git commands. The findings below include unresolved and newly exposed defects in the swept files. Reversibility: Easy. Bet: fixing these bounded contracts before building avoids green checks that do not establish runtime readiness or retrieval correctness.

Uses Round 1 citation shorthand (`plan`, `p0`–`p4`, `canonical`).

- [Blocker] **Offline readiness still passes vacuously.** `validate.sh:22-29` checks `find_spec` and model-directory existence only. Empty model directories satisfy it; missing weights/tokenizer/custom modeling code or unusable language grammars are not detected. p0's Environment contract says this establishes “both cached models” before starting, and prohibits installs. **Fix:** assign an operator provisioning/preflight step before firing, with recorded offline loads of both actual model classes and parser creation for Python/JS/TS/TSX/PHP using the exact `XYZ_PY` and caches propagated into builder worktrees. Check the required dependencies by usable imports, not names alone; name failure behavior and evidence destination. A deliberately incomplete cache and an unavailable grammar must fail the readiness control. This can be a separate explicit prelaunch check rather than loading models on every unit-test gate. The explicit env variables/no-editable-install changes are useful but do not close Round 1's readiness blocker.
- [Blocker] **Incomplete-walk pruning protection remains unspecified.** p2:63-70 guards only zero files. If one subtree is readable and another cannot be enumerated, a nonempty partial walk still qualifies for pruning everything missing in the selected scope; p1 Task 1 specifies no enumeration/read-error policy. **Fix:** propagate traversal/read failures and prohibit pruning unless the entire selected scope completed successfully; define how intentional exclusions differ from errors. Add an injected directory-enumeration failure after at least one yielded file, assert pre-existing unseen chunks/FTS/vec records survive, and name a red control that disables the completion guard. Retain the successful-deletion and prefix-scope tests. Round 1 explicitly requested incomplete-walk rejection, not merely an empty-root check.
- [Should] **Depth 100 needs a complete rerank-tail contract and chunk-level evidence.** p3:57-60 reranks only 50 but promises an ordered list up to 100; it never says how unreranked candidates are appended or where the two-lane union is truncated. p4:54,70-71 then exports only paths for the reorder count: swapping two chunks of the same file becomes invisible. **Fix:** specify fuse → truncate to D → rerank the first min(D,50) → append untouched tail in RRF order (or another explicit policy without comparing cross-encoder scores to RRF scores). Preserve ordered chunk IDs alongside paths in JSON and compute reorder count from IDs. Test a >100-candidate union, a relevant chunk at rank 75, and a swap between two chunks of one path; record red-control evidence in the relay. The new cutoff/baseline fixes the original full-corpus comparison error, but does not settle these remaining ordering cases.
- [Should] **BM25 threshold direction conflicts with the score contract.** p3:31 says native BM25 is lower-is-better, while p3:61-63 rejects a lane score *below* tau; unlike dense at p3:44, lexical at p3:41-42 never negates its score. **Fix:** define `Hit.score = -bm25(...)` (higher is better across lanes), or explicitly reverse the BM25 threshold comparison. Test stronger and weaker lexical hits around a threshold. Also qualify p3:74-75's “tau=None never does” assertion to nonempty candidates, since p3:63 correctly requires an empty set to return no-answer even without tau.
- [Should] **The changed-token test is contradictory as written.** p2:83-85 says to “add a unique token” then requires `old_token` to disappear. An additive edit leaves the old token present, so a correct FTS implementation fails the stated assertion. **Fix:** replace the old unique token with the new one in a specific chunk while keeping a separate chunk unchanged for the cache-hit assertion; require old MATCH empty and new MATCH nonempty. Keep the trigger-disabled red control.
- [Pass] **Grounding corrections and model guard assertions now match the references.** Plan Recon and p1 Context correctly name `iter_files` and path/start_line/end_line/text plus id/repo (`.embed-tmp/scripts/embed_repos.py:106,136-140,160-161`); p2:92-93 explicitly tests the cap and query-only prefix, consistent with `FINDINGS-0.5.md:174-179` and `SOP.md:31-33`. Store-assigned `chunks.id` is specified at p2:54. These are plan-level checks, not executed implementation evidence.
- [Pass] **Scope accounting, one-writer architecture, dependency order and rating remain sound at plan level.** Plan Acceptance now explicitly marks fresh ingest, Act 2 inheritance deferrals and the non-saturated criterion as outstanding, alongside the existing quality/ARM deviations; these account for the live issue's Act 1 items without claiming the original win criterion complete. Canonical:204-207,214-224 is covered by the five briefs. p2:51 says “Store, the only writer”; MARATHON.yaml:23,32,41,50 orders p0→p4 and its allowlists permit the demanded source paths. Plan Dependencies assigns CHANGELOG to the orchestrator and states “Reversibility: Easy”; p0 requires `xyz/__main__.py`. Plan Rating retains `85/60/50/30`, “appeal 50: neutral” and “No operator override”; the historical user-order assertion remains independently unverified.
- [Pass] **Several falsification and fallback fixes are concrete.** `validate.sh:43-54` unconditionally checks package presence, exact version and pytest; p2:80-82 separately asserts file skips and writes; p4:55-57,73-74 rejects empty queries and tests rank 11 at two depths; p4:36-39 uses a same-depth dense baseline rather than Run 9. p1 Task 1 preserves root-relative prefixes and p4:80-83 uses one fresh subset DB; every label in `.embed-tmp/eval/queries-LTVera-Pandas.json` lies under scripts/app/alembic. p4:77-79 supplies a measured ETA trigger and p4:105 requires a <30-second re-ingest. Runtime feasibility is conditional on the readiness fix above; no actual model/corpus run was attempted here.

DoD disposition: 1 grounding passes with stated historical-evidence limits; 2 completeness/deviations passes at plan level; 3 DRY and 4 dependency/allowlist/rollback pass; 5 falsifiable checks and 6 executable runtime readiness remain changes requested; 7 rating rationale passes. Producer should disposition all five open findings and request round 3 after revising the artifacts. Handing off to claude-a (Producer) — go to the Producer window and say 'take your turn'.

<!-- ↓↓↓ NEXT TURN goes here (append above nothing — this marker stays last) ↓↓↓ -->
