# RELAY · GH-11 Act 1 plan review — hybrid retrieval marathon
<!--
  Single source of truth for this two-agent relay. Read the ENTIRE file before acting.
  Scaffolded by relay-automation/new-relay.sh on 2026-09-06.
-->

NEXT: Producer
STATUS: Open
ROUND: 1 / 3

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

<!-- ↓↓↓ NEXT TURN goes here (append above nothing — this marker stays last) ↓↓↓ -->
