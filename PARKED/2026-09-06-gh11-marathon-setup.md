# Parked — 2026-09-06, GH-11 Act 1 marathon setup

Out-of-scope findings from setting up the GH-11 Act 1 marathon. None block the marathon.

1. **Run 12-15 evidence and code are on no branch of `origin`.** Issues #2, #8, #14 are closed as
   "fixed in the Run 12 batched re-embed" (MRR 0.978) and #11 cites Runs 12-15 on `sleuth-arm-vm`,
   but neither `origin/main` nor `origin/v0.5/embedding-eval-coderankembed-vs-gemini` carries that
   chunker code or `BENCHMARKS.md` beyond Run 10, and no local clone has it. Find and push that work
   or re-record the baseline; until then the 0.978 number is unreproducible.
2. **`GUIDING-PRINCIPLES.md` and `AGENTS.md` are PDDA-repo boilerplate** ("this repo is about
   PDDA", "keep this repo about PDDA"). p0 of the marathon fixes the Purpose + adds two principles;
   `AGENTS.md` still needs a rewrite for this repo.
3. **No `development` branch**, so `marathon-closeout.sh` (hard-locked to base `development`) cannot
   open the PR; the PR is opened by hand against `main`. Decide whether this repo adopts a
   `development` integration branch.
4. **`origin/v0.5/embedding-eval-coderankembed-vs-gemini` has no PR** and is 7 commits ahead of
   `main`. The marathon branch is stacked on it; its PR to `main` will carry those commits.
5. **`RELEASES.generated.md` / `.drift`** are emitted by `releases_app.py gen` into the repo root and
   are not gitignored; add them to `.gitignore` or commit them deliberately.
6. **`gh` fails inside the Claude Code sandbox** with `x509: OSStatus -26276` (TLS through the
   filtering proxy); works un-sandboxed. Not a repo issue.
7. **`.venv` is per-clone** — the marathon clone has its own venv with `sqlite-vec`, `tree-sitter`,
   `tree-sitter-language-pack`, `pytest`; the primary checkout's venv lacks them. `SOP.md` should list
   the full dependency set once `pyproject.toml` lands (p0).
8. **Phase 5 port item** (added to the canonical doc 2026-09-05): Ask-Self synthesis + citation +
   doc-history layer — no issue yet; file one when Act 2/3 planning starts.

## Post-marathon additions — 2026-09-06

9. **Reranker is unshippable as-is**: 50,004 ms p50 / 93,867 ms p95 per query on CPU, and it scored
   *below* dense-only on the labelled set. Needs the Phase 3 bake-off or a serving path, not a patch.
10. **The labelled set is saturated** (dense already R@3 = 1.000), so it cannot separate dense,
    hybrid and hybrid+rerank. Canonical Phase 2's 250-query benchmark is the unblock.
11. **Final implementation QA never completed** — the advisor hit its 300 s cap with no verdict.
    Load-bearing contracts were verified directly instead; a reviewer may want to redo that pass.
12. **The builder repeatedly creates nested duplicate trees** (`xyz/xyz/`, `tests/tests/`) via a bad
    recursive copy — happened in p2 and again in p3. Worth a harness-level guard if marathons
    continue in this repo.
13. **agy backend failed transiently mid-run** (`agy -p` exit 0, empty output), halting a phase
    before its gate. Recovered by re-firing.
14. **Full-corpus ingest is impractical on CPU**: ETA 206.5 min for 17,258 chunks, so p4 ran the
    339-file / 3,020-chunk subset. MPS was unavailable in the managed runtime.
