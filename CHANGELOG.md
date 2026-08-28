# CHANGELOG.md

Newest-first, dated end-of-iteration record. One entry per substantive iteration: what changed,
why, and the verification. See `PROJECT/PDDA.md` for the full contract.

## 2026-08-28

### CodeRankEmbed installed

- Set up local `.venv/` (gitignored) with `sentence-transformers`, `torch`, `einops`; pulled
  `nomic-ai/CodeRankEmbed` into the HuggingFace cache. Usage documented in `SOP.md`.

Verification: loaded the model and encoded a query/code pair, got the expected 768-dim embeddings.

### v0.5 canonical research and build doc

- Synthesized the four Perplexity research docs and the Hyperagent report into
  `PROJECT/2-WORKING/v0.5/XYZ Code Intelligence v0.5 — Canonical Research and Build Doc.md`:
  consensus verdict (skip BGE-small, code-native dense lane + permanent BM25/RRF/rerank hybrid),
  reconciled divergences, model shortlist, datasets, conditional fine-tuning pipeline, a 6-phase
  build plan with QA gates, and the Ask-Self inherit/sunset split.
- Marked the five research inputs as roadmap-exempt reference appendices (frontmatter + status
  tables added); pointed the canonical doc from `ROADMAP.md`.

Verification: `./utils/pdda/pdda.sh run` — all checks passed.

### PDDA installed

- Installed the PDDA document-automation surface (`utils/pdda/pdda.sh` + helpers, `PROJECT/PDDA.md`)
  and the `PROJECT/**` lifecycle tree in `observe` mode.
- Next: replace this entry as real iterations land.

Verification: `./utils/pdda/pdda.sh run`
