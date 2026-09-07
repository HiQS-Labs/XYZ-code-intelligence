# MEASUREMENTS

The running record of **what XYZ is configured to do** and **what it measured**. One folder, two
kinds of file:

| file | what it is | who writes it |
|---|---|---|
| `BASELINE.md` | the current default settings — every knob, its value, and *why that value* | a human or agent, deliberately, when a default changes |
| `runs/YYYY-MM-DD-<slug>.md` | one measurement run: settings used, numbers produced, what changed | appended per run, **never edited afterwards** |

## Why this exists separately from FINDINGS-0.5.md

`PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md` is a *narrative* findings log for the v0.5 evaluation — it
argues and concludes. This folder is the *ledger*: settings and numbers, no argument. A run file
answers "what was the config and what did it score", so a later comparison is apples-to-apples
without re-reading prose.

Guiding principle #4 (*one canonical place per fact*): a knob's current value lives in `BASELINE.md`
and nowhere else. A run file records the value it *used*, which is history and may differ from the
current baseline — that is the point.

## Rules

1. **A run file is immutable once written.** Wrong numbers get a new run file with a correction note,
   never an edit. (Principle 8: a finding that was reported is not a finding that was seen — silently
   editing a number destroys the trail.)
2. **Every run states its full settings**, copied from `BASELINE.md` at run time plus any overrides.
   A run that cannot say what it ran is not evidence.
3. **Changing a baseline requires a run that justifies it.** Link the run from the `BASELINE.md` row.
   No knob changes on taste alone.
4. **Numbers only, in this folder.** Interpretation belongs in the project doc or CHANGELOG.
5. **State the caveat that would overturn the number.** A measurement on a saturated set is an upper
   bound and must say so in the run file, not just in someone's memory.

## Naming

`runs/2026-09-06-act1-roundtrip.md` — date first so the folder sorts chronologically, then a short
slug naming the thing measured.
