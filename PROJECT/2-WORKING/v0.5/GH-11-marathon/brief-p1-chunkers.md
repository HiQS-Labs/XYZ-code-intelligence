---
title: GH-11 marathon brief — gh11-p1-chunkers
status: active
created: 2026-09-05
updated: 2026-09-05
owner: Noel Saw
goal: Phase brief consumed by marathon-drive.sh for phase gh11-p1-chunkers; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
roadmap_exempt: true
---

# Phase brief — gh11-p1-chunkers: AST / Markdown / file-level chunkers with path-prefixed text

## Status

| What was just completed | What's next |
|---|---|
| Brief authored (2026-09-05). | Executed by `marathon.sh` as phase `gh11-p1-chunkers` after `gh11-p0-scaffold`; outcome recorded in the capture doc. |

Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
Canonical doc → "Phase 1 — Chunking + hybrid retrieval skeleton", step 1.

## Context you must read before coding

- `.embed-tmp/scripts/embed_repos.py` — the current (throwaway) chunker: `INCLUDE_EXT`, `walk_repo`,
  the chunk record fields written to `chunks.jsonl` (`repo`, `path`, `qualified_name`,
  `start_line`, `end_line`, `text`, …). The new chunker must emit a **superset** of those fields so
  the existing scorer still works on its output.
- Issue #8 (closed): leading each chunk's embedded text with the file's relative path was the
  largest quality jump in the project (MRR 0.80 → 0.98). Issue #2 (closed): YAML and Dockerfiles
  were skipped, a silent infra blind spot. Both are re-implemented here because that code is not on
  this branch.
- `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md` — chunk sizing is derived from the model's real window
  (`max_seq_length=2048` tokens for CodeRankEmbed), not from BGE-small's 512.

## Task

Implement `xyz/ingest/`:

1. `xyz/ingest/walk.py` — `walk_repo(root, include_ext=DEFAULT_INCLUDE, exclude_dirs=DEFAULT_EXCLUDE)`
   yielding `(rel_path, bytes)`. `DEFAULT_INCLUDE` = the current `embed_repos.py` list **plus**
   `.yml .yaml .toml .ini .cfg .json .env.example .sql .html .blade.php .twig` and filenames
   `Dockerfile`, `docker-compose*.yml`, `Makefile`. `DEFAULT_EXCLUDE` = `.git .venv node_modules
   __pycache__ dist build temp .embed-tmp .xyz marathon-system relay-system`. Skip files > 1 MiB and
   binary files (NUL byte in the first 8 KiB).
2. `xyz/ingest/chunk.py` — a `Chunk` dataclass: `repo, path, kind, qualified_name, start_line,
   end_line, text, embedded_text, content_sha` (`content_sha` = sha256 of `embedded_text`).
   `embedded_text` **always begins with the relative path on its own line** followed by a blank line
   then `text` (#8). `chunk_file(repo, rel_path, source) -> list[Chunk]` dispatching on extension:
   - **Python, JS, TS/TSX/JSX, PHP** → Tree-sitter via `tree_sitter_language_pack.get_parser(lang)`.
     One chunk per top-level function / class / method (nested methods become their own chunks with
     `qualified_name = "Class.method"`); the file's remaining top-level statements (imports, module
     docstring, constants) become one `kind="module"` chunk. A chunk longer than **6,000 characters**
     (≈ the 2,048-token window with headroom) is split at the nearest blank line, each part keeping
     the same `qualified_name` with a `#2`, `#3` suffix.
   - **Markdown** → one chunk per heading section (heading level ≤ 3); preamble before the first
     heading is its own chunk; `qualified_name` = the heading path joined with ` > `.
   - **everything else** (YAML, TOML, JSON, Dockerfile, SQL, HTML/Blade/Twig, shell, Go, Ruby, …)
     → file-level chunks: whole file if ≤ 6,000 chars, else split at blank lines into ≤ 6,000-char
     windows with ~150-char overlap; `kind="file"`, `qualified_name = rel_path`.
   - A parse failure never aborts ingest: fall back to the file-level chunker and record the
     fallback in a `warnings` list returned alongside.
3. `xyz/ingest/__init__.py` exports `walk_repo`, `chunk_file`, `chunk_repo(repo, root) ->
   Iterator[Chunk]` and the constants.
4. Tests in `tests/test_chunkers.py` using a **fixture tree under `tests/fixtures/mini-repo/`**
   that you create: one Python file with a module docstring, two functions and a class with two
   methods; one TS file with an exported function and a class; one PHP file with a class; one
   Markdown file with three headings; one `config.yml`; one `Dockerfile`; one binary blob; one
   `node_modules/ignored.js`. Assert: chunk counts and `qualified_name`s per file; `start_line` /
   `end_line` match the source; every `embedded_text` starts with the chunk's `path`; the YAML and
   Dockerfile produce chunks (#2); the binary and `node_modules` file produce none; a > 6,000-char
   generated function splits into suffixed parts; a deliberately broken Python file falls back to a
   file-level chunk with a warning.

## Non-goals

No embedding, no SQLite, no CLI. Do not modify `.embed-tmp/scripts/embed_repos.py`.

## Definition of done

- `bash validate.sh` green; `tests/test_chunkers.py` passes with every assertion above present.
- Running `chunk_repo` over `tests/fixtures/mini-repo` is deterministic (same output twice).
- Red control: the test that asserts the path prefix must fail if the prefix line is removed —
  show this once in the relay (flip, run, restore).
