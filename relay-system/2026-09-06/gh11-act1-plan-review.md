# RELAY · GH-11 Act 1 plan review — hybrid retrieval marathon
<!--
  Single source of truth for this two-agent relay. Read the ENTIRE file before acting.
  Scaffolded by relay-automation/new-relay.sh on 2026-09-06.
-->

NEXT: Reviewer
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
- Artifact under review: **`PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`** (the plan) plus
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

<!-- ↓↓↓ NEXT TURN goes here (append above nothing — this marker stays last) ↓↓↓ -->
