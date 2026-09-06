# Marathon preflight packet — gh-11-act1-hybrid-retrieval

- Generated: 2026-09-06T18:10:36Z
- Mode: project-doc
- Sources: /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md 
- Target root: /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1 (marathon/gh11-act1-hybrid-retrieval-2026-09-05 @ eb4f3d061)
- Suggested branch: `marathon/gh-11-act1-hybrid-retrieval-2026-09-06` (branch_ready=false — not cut yet; ask the operator before proceeding, per GUIDING-PRINCIPLES.md §8)
- Verdict: ready
- Source issue state: OPEN.
- Gate: `bash validate.sh`

- Artifacts: GUIDING-PRINCIPLES.md,pyproject.toml,validate.sh,xyz/,tests/,PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md,PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md
- Suggested turn budget: `turn_timeout_s: 1800` in this phase's MARATHON.yaml entry (≈ 509 LOC across 7 artifact(s) — over the 900s default, so it needs headroom). marathon.sh reads that field and applies it to the phase; the value is a starting point, not a measurement.


This packet is the producer's output. The orchestrator launches the run; the planner does not
(GUIDING-PRINCIPLES.md §8).

## Acceptance criteria — the build is DONE when these hold
*Inlined verbatim from `/Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md` (0 checkbox(es) found across the WHOLE document — the doc has no `## Acceptance` section, so this list may include phase checklists). Continuation lines included; if a
criterion here reads as a fragment, that is the source text, not a truncation.*
*NOT verified, and NOT verifiable as things stand — issue #11 has no '## Acceptance' section — nothing to copy from. This list exists only in the capture doc; reading the issue will not confirm it, because the issue states no criteria. Establish the criteria on the issue before treating anything below as the definition of done.*
(no '- [ ]' checklist found in /Users/noelsaw/Documents/GH Repos/XYZ-code-intelligence-gh11-act1/PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md — add an Acceptance criteria list)

## Scope lock — builder, do exactly this and nothing else
- Edit ONLY: `GUIDING-PRINCIPLES.md,pyproject.toml,validate.sh,xyz/,tests/,PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md,PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md` (plus the relay file). Any other edit is reverted and FAILS the turn.
- Do NOT run the full gate (`bash validate.sh`) yourself — it can create files that trip containment and discard your turn. Verify with ONLY the specific test for the file(s) you changed; the harness runs the gate after your turn.
- Do NOT analyze the roadmap, file issues, or refactor adjacent code. Implement the acceptance criteria above — nothing more.

## Suggested marathon-drive.sh invocation

```bash
XYZ_HARNESS_CONTEXT=swarm XYZ_SESSION_ID=gh-11-act1-hybrid-retrieval RELAY_WORKTREE_ISOLATION=1 .xyz/relay-automation/marathon-drive.sh \
  --phase-brief <packet>/packet.md \
  --reviewer agy \
  --builder codex \
  --artifact GUIDING-PRINCIPLES.md,pyproject.toml,validate.sh,xyz/,tests/,PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md,PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md \
  --pre-advance-cmd 'bash validate.sh' \
  --require-clean
```

## Files in this packet
- `run-candidate.json` — normalized run candidate (provenance + contract + checks)
- `freshness.json` — branch state + fix-still-required probes
- `readiness.json` — remediation readiness verdict
- `lane-plan.json` — Codex / agy / orchestrator lane assignment
- `marathon-invocation.txt` — the invocation hint above
