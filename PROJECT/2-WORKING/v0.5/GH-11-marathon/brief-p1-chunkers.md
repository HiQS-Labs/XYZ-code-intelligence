---
title: GH-11 marathon brief — gh11-p1-chunkers
status: active
created: 2026-09-05
updated: 2026-09-06
owner: Noel Saw
goal: Phase brief consumed by marathon-drive.sh for phase gh11-p1-chunkers; the plan of record is GH-11-ACT1-HYBRID-RETRIEVAL.md.
roadmap_exempt: true
---

# Phase brief — gh11-p1-chunkers: AST / Markdown / file-level chunkers with path-prefixed text

## Status

| What was just completed | What's next |
|---|---|
| Brief revised after Codex plan review round 1 (2026-09-06). | Executed by `marathon.sh` as phase `gh11-p1-chunkers` after `gh11-p0-scaffold`; outcome recorded in the capture doc. |

Execution surface of record: `PROJECT/2-WORKING/v0.5/GH-11-ACT1-HYBRID-RETRIEVAL.md`
(issue: https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/11, Act 1).
Canonical doc → "Phase 1 — Chunking + hybrid retrieval skeleton", step 1.
Environment contract: see `brief-p0-scaffold.md` (`XYZ_PY`, `XYZ_SCRATCH`, offline env, no installs).

## Context you must read before coding

- `.embed-tmp/scripts/embed_repos.py` — the current (throwaway) chunker. What it actually has:
  `INCLUDE_EXT`, `iter_files(...)` (line ~106), and per-chunk records carrying **`path`,
  `start_line`, `end_line`, `text`**, to which `id` and `repo` are added (lines ~136-140, ~160-161).
  It has **no** `qualified_name`, `kind`, `content_sha` or `embedded_text` — those are **new** fields
  this phase introduces. The new chunker must still emit `path`, `start_line`, `end_line`, `text`
  so the existing scorer can read an exported `chunks.jsonl`.
- Issue #8 (closed): leading each chunk's embedded text with the file's relative path was the
  largest quality jump in the project (MRR 0.80 → 0.98). Issue #2 (closed): YAML and Dockerfiles
  were skipped, a silent infra blind spot. Both are re-implemented here because that code is not on
  this branch.
- `PROJECT/2-WORKING/v0.5/FINDINGS-0.5.md` (lines ~174-179): the model's real memory guard is
  `max_seq_length = 2048` tokens; the 6,000-character split below is a **character heuristic**
  chosen to sit under that window with headroom, not a tokenizer bound. The p2 embedder enforces the
  token cap; this phase only bounds characters.

## Task

Implement `xyz/ingest/`:

1. `xyz/ingest/walk.py` — `walk_repo(root, include_ext=DEFAULT_INCLUDE, exclude_dirs=DEFAULT_EXCLUDE,
   include_prefixes=None)` yielding `(rel_path, bytes)` in sorted order. `include_prefixes` (a
   tuple of repo-relative directory prefixes, e.g. `("scripts/", "app/")`) restricts the walk **while
   keeping paths relative to `root`** — this is the p4 subset fallback; it must not change any
   `rel_path`. `DEFAULT_INCLUDE` = the current `INCLUDE_EXT` list **plus** `.yml .yaml .toml .ini
   .cfg .json .sql .html .twig` and the filenames `Dockerfile`, `docker-compose*.yml`, `Makefile`,
   `*.blade.php`, `.env.example`. `DEFAULT_EXCLUDE` = `.git .venv node_modules __pycache__ dist build
   temp .embed-tmp .xyz .relay-scratch marathon-system relay-system`. Skip files > 1 MiB and binary
   files (NUL byte in the first 8 KiB). `root` must be an existing directory → else `ValueError`.
   **Traversal errors are not exclusions:** an `OSError` from directory enumeration or from reading
   a candidate file is appended to `errors` (a caller-supplied `list[str]`, required argument) with
   the path, and the walk continues; skips by extension, size, binary sniff, `exclude_dirs` or
   `include_prefixes` are intentional and are **not** recorded there. Callers that mutate an index
   (p2 `Store.ingest`) must treat a non-empty `errors` as an incomplete walk and refuse to prune.
2. `xyz/ingest/chunk.py` — a `Chunk` dataclass: `repo, path, kind, qualified_name, start_line,
   end_line, text, embedded_text, content_sha` (`content_sha` = sha256 of `embedded_text`), and
   `ChunkResult(chunks: list[Chunk], warnings: list[str])`. `embedded_text` **always begins with the
   relative path on its own line**, then a blank line, then `text` (#8).
   `chunk_file(repo, rel_path, source: bytes) -> ChunkResult` dispatches on extension:
   - **Python, JS, TS/TSX/JSX, PHP** → Tree-sitter via `tree_sitter_language_pack.get_parser(lang)`.
     One chunk per top-level function / class / method (methods become their own chunks with
     `qualified_name = "Class.method"`); the file's remaining top-level statements (imports, module
     docstring, constants) form one `kind="module"` chunk whose `start_line`/`end_line` are the first
     and last line of that residual text and whose `text` joins the pieces with a `# …` gap marker.
   - **Markdown** → one chunk per heading section (level ≤ 3); preamble before the first heading is
     its own chunk; `qualified_name` = heading path joined with ` > `.
   - **everything else** → file-level chunks, `kind="file"`, `qualified_name = rel_path`.
   - **Hard bound, every kind:** any chunk whose `text` exceeds **6,000 characters** is split — at
     the nearest blank line before the limit if one exists in the last 1,500 characters, otherwise
     **hard-cut at 6,000** — into parts ≤ 6,000 chars with ~150-char overlap, each keeping the
     `qualified_name` with a `#2`, `#3` suffix and correct `start_line`/`end_line`. A single-line
     6,001-char file must still yield ≥ 2 chunks (this is a test).
   - A parse failure never aborts ingest: fall back to the file-level chunker and append a warning.
3. `xyz/ingest/__init__.py` exports `walk_repo`, `chunk_file`, and
   `chunk_repo(repo, root, **walk_kwargs) -> ChunkResult` (all chunks + all warnings; p2's
   `Store.ingest` reports the warnings). The p2 `IngestReport` is the one channel for warnings.
4. Tests in `tests/test_chunkers.py` on a **fixture tree `tests/fixtures/mini-repo/`** that you
   create: a Python file with module docstring, two functions and a class with two methods; a TS
   file with an exported function and a class; a PHP file with a class; a Markdown file with three
   headings; `config.yml`; `Dockerfile`; a binary blob; `node_modules/ignored.js`; a generated
   single-line 6,001-char `.txt`; a generated Markdown section > 6,000 chars; a deliberately broken
   Python file. Assert: chunk counts and `qualified_name`s per file; `start_line`/`end_line` match
   the source; every `embedded_text` starts with `path + "\n\n"`; YAML and Dockerfile produce chunks
   (#2); binary and `node_modules` produce none; both oversize cases split with suffixes and ≤ 6,000
   chars each; the broken file yields a file-level chunk plus one warning; `include_prefixes`
   restricts the walk without altering `rel_path`; a missing root raises; output is deterministic
   (two runs equal); with `os.scandir` monkeypatched to raise `PermissionError` for one subdirectory
   **after** at least one file was yielded, the walk still yields the other files and `errors` has
   exactly one entry naming that subdirectory, while an excluded dir or a binary skip adds nothing
   to `errors`.

## Non-goals

No embedding, no SQLite, no CLI. Do not modify `.embed-tmp/`.

## Definition of done

- `bash validate.sh` green; every assertion above present in `tests/test_chunkers.py`.
- Red control (show once in the relay, then restore): remove the path-prefix line from
  `embedded_text` → the prefix test fails; remove the hard-cut branch → the single-line 6,001-char
  test fails.
