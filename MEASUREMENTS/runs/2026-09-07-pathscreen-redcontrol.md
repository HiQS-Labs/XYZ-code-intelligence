# Run — path-only screen red control, and WordPress repo 1 ingest

- **Date:** 2026-09-07
- **Commit:** `c37becf` on `feat/gh17-path-only-screen` (branched from `7d7ddd9`)
- **What was measured:** (1) whether the new path-only screen rejects a set already known to be
  name-carried; (2) the cost and shape of indexing the first PHP/WordPress repo
- **Status:** immutable — see `../README.md` rule 1

## Settings used

Baseline as of this run, with the overrides noted:

| knob | value | note |
|---|---|---|
| model | `nomic-ai/CodeRankEmbed`, 768d, `max_seq_length` 2048 | |
| device | **CPU** | override — `XYZ_DEVICE=cpu` pinned explicitly |
| chunking | Tree-sitter, path-prefixed, 6,000-char split | |
| screen threshold | 3 | `MEASUREMENTS/BASELINE.md`, frozen-benchmark section |
| screen lanes | `lexical` (BM25 over tokenised paths) + `dense` (CodeRankEmbed over path strings) | either firing is a rejection |
| path tokenisation | separators + camelCase + digit/letter boundaries | |
| environment | `requirements-verified.txt` exactly, drift 0 | rebuilt from the record; `validate: OK` |

## Part 1 — Red control: does the screen reject a known-bad set?

**The question.** Toy fixtures cannot show that a screen under-rejects on real text. The 30-query
LTVera-Pandas set is independently known to be name-carried — path-prefixing chunks moved MRR
0.80 → 0.98 on it (issue #8) and dense retrieval scores R@3 = 1.000 (run
`2026-09-06-act1-roundtrip`). If the screen is doing its job it must reject most of that set.

Paths were read from the repo's git index (**1,460 paths**), not from an xyz index — the screen only
ever looks at paths.

**Reproduce with one command:**

```bash
xyz screen --paths-from-git <LTVera-Pandas> \
           --queries .embed-tmp/eval/queries-LTVera-Pandas.json \
           --out redcontrol.json
```

The run was performed twice — once by an ad-hoc script, once through the shipped CLI — and the two
agree on **every verdict and every per-lane rank**. The path counts differed (1,462 vs 1,460)
because the ad-hoc script split `git ls-files` output on whitespace, which breaks the two paths
containing spaces. The CLI splits on lines and is the correct one; the figure above is the CLI's.
No verdict changed, because two extra malformed paths cannot outrank a gold file.

| | |
|---|---:|
| questions screened | 30 |
| **rejected** | **30 (100.0%)** |
| passed | 0 |

**Rejections by lane**

| caught by | n |
|---|---:|
| both lanes | 27 |
| **dense only** | **3** |
| lexical only | 0 |

**Where each lane ranked the gold path**

| best rank | dense | lexical |
|---|---:|---:|
| 1 | 28 | 25 |
| 2 | 2 | 2 |
| 7 | 0 | 1 |
| never retrieved | 0 | 2 |

### The three the dense lane caught alone

These are the case the two-lane design exists for — the query is a *synonym* of the path, not a
repetition of it, so BM25 sees no shared word:

| question | gold path | dense rank | lexical rank |
|---|---|---:|---:|
| "timezone and time formatting helpers" | `app/timefmt.py` | 1 | never retrieved |
| "application configuration and settings" | `app/config.py` | 1 | never retrieved |
| "alembic migration environment setup" | `alembic/env.py` | 1 | 7 |

`timefmt` and "time formatting" share no token. A lexical-only screen would have passed all three
into the frozen set, where they would have contributed nothing to separating two retrievers.

### What this decides

- **The screen works.** It rejects 100% of a set independently known to be saturated.
- **Both lanes stay.** The dense lane's 3 solo catches are 10% of the set, and they are exactly the
  failure mode issue #8 measured. Removing it would silently weaken the rule.
- **The old 30-query set is confirmed unusable as a discriminating benchmark** — not by argument
  this time, but by the same deterministic filter the new set must pass. It is retained only as the
  regression/smoke set, which is what `BASELINE.md` already says.

### The caveat that would overturn this

**Zero questions were rejected by the lexical lane alone**, so on this corpus dense is a strict
superset of lexical and the lexical lane changed no verdict. It is kept because it is nearly free,
needs no model, is deterministic, and has not been tested on a corpus where the dense model is
weak — not because this run proved it necessary. If a later run again shows zero lexical-only
catches, that is evidence for dropping it, and this row should be revisited rather than inherited.

A second caveat: 100% rejection is a *floor* on how well the screen works, not proof it is
calibrated. It shows the screen catches the obvious case. It does **not** show the screen avoids
rejecting genuinely hard questions — that error is invisible until real candidates are written, and
it will show up as an unexpectedly high rejection rate during Phase 2 labelling.

## Part 2 — WordPress repo 1 ingest

`universal-child-theme-oct-2024` at `f238c1d`, indexed whole (no `--include-prefix`).

| | |
|---|---:|
| wall | 587.87 s (9m 48s) |
| files indexed | 143 |
| chunks written | 1,341 |
| chunks embedded | 1,319 |
| cache hits | 0 (cold) |
| **peak RSS** | **12,897.14 MB** |

**Corpus composition (142 distinct paths):**

| ext | files |
|---|---:|
| php | 47 |
| md | 39 |
| js | 20 |
| py | 19 |
| json | 8 |
| yml | 7 |
| html | 1 |
| sh | 1 |

All 47 PHP files were indexed, matching the count the canonical doc assumed. 290 chunks are PHP.

### Findings

1. **The "HTML/WP-template" language quota needs rereading as PHP.** `BASELINE.md` allocates 5
   questions to HTML/WP-template. The repo contains exactly **one** `.html` file. WordPress
   templates here *are* PHP — `archive.php`, `header.php`, `footer.php`, `content-single.php`. The
   quota is satisfiable, but by PHP template files, not by HTML.
2. **One file failed Tree-sitter parsing, and the cause is a grammar limitation, not a bad file.**
   `inc/class-binoid-cart-rest.php` fell back to the file chunker. The single ERROR node is at
   line 18:

   ```php
   const NAMESPACE = 'binoid/v1';
   ```

   A class constant may be named with a reserved word from PHP 7 onward, but `tree-sitter-php`
   1.16.1 does not accept it. The file is valid PHP; the grammar is behind.

   **Measured blast radius: 1 of 120 PHP files across both WordPress repos** — 1/47 in
   `universal-child-theme-oct-2024`, **0/73** in `KISS-woo-order-monitoring-alerts`. So this is
   isolated, and the premise that Tree-sitter chunking is XYZ's real improvement over Ask-Self's
   regex chunkers survives for PHP. Had the rate been high it would have undercut that premise, so
   the number was worth taking rather than assuming.

   Consequence for Phase 2: that one file's chunks have no symbol boundaries, so a question
   targeting it is scored against a coarser unit than the rest of the corpus. Prefer a different
   gold file, or accept the coarser unit knowingly.
3. **Peak RSS 12.9 GB on CPU** for 1,341 chunks. Recorded, not diagnosed. The Act 1 run reached
   9.85 GB for 3,020 chunks, so this is not a simple function of corpus size and is worth watching
   before the second repo is added.
4. **27 of 142 files are agent/CI/docs material** (`.claude/`, `.claude-docs/`, `.github/`,
   `ask_self/`). Kept deliberately as realistic distractors — noise makes retrieval harder, which
   serves a set whose purpose is to discriminate. Reversible via `--include-prefix` if a later run
   shows it distorts results.

## What this run did NOT decide

- Whether the frozen 50 will discriminate between arms. That needs the questions to exist.
- Anything about retrieval quality on PHP. No PHP questions have been written or scored yet.
- Whether the second WordPress repo is needed. It holds 73 PHP files, not the 59 the canonical doc
  assumed; the decision was deferred until repo 1 is screened.
- The `auto` default mode. Still contradicted by the Act 1 measurement, still unresolved.
