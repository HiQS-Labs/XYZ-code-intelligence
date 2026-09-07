**NO FIRSTHAND VERIFICATION CITED** — treat conclusions as conditional (codex's answer carries an unsupported [Pass]/verified/confirmed-style claim with no quoted span or file:line citation nearby, despite the consult PREAMBLE asking advisors to cite evidence.)

> **ATTESTATION**
> Model: gpt-5.6-terra
> Provider: openai
> Sandbox: read-only

Reading additional input from stdin...
OpenAI Codex v0.153.4
--------
workdir: /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-22132-rax9y1zy
model: gpt-5.6-terra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a07cd8-9499-7190-a355-15574df8bcdf
--------
user
You are an INDEPENDENT advisor in a one-shot cross-model consult. Another model is answering the SAME question separately and a coordinator will reconcile both answers, so give your own honest, specific read — do not hedge toward a consensus you cannot see. Read any repo files the question references (cite file:line). Respond with: (1) a short direct ANSWER; (2) graded FINDINGS — [Blocker]/[Should]/[Nit]/[Pass] — where applicable; (3) a one-line RECOMMENDATION. You are ADVISORY ONLY: output your analysis as text; do not rely on writing files (you are running in a throwaway copy).

=== CONSULT QUESTION ===
# Final QA — GH-11 Act 1 implementation (PR #15)

Budget note: you have ~15 minutes. **Produce a verdict even if you have not read everything.**
If you run short, stop exploring and write your findings — a partial graded answer is required;
silence is not. Put the verdict in your FIRST line.

## Scope — audit these files only
`xyz/index/store.py`, `xyz/retrieve/pipeline.py`, `xyz/retrieve/dense.py`, `xyz/retrieve/lexical.py`,
`xyz/retrieve/fuse.py`, `xyz/eval/metrics.py`, `xyz/ingest/walk.py`, and `tests/`.
Do NOT read PROJECT/**, relay-system/**, marathon-system/**, ROUTER.md, or the plan docs — the
contracts you need are stated below. Do not run the test suite; read the tests.

## The five contracts to verify (cite file:line for each)
1. **Single writer** — `xyz/index/store.py` is the only module that writes the `chunks`,
   `chunks_fts` or `chunks_vec` tables. No second index path.
2. **`k = ?` KNN** — dense search uses sqlite-vec's `k = ?` bound form, never a parameterised
   `LIMIT ?` (the latter 500'd in production upstream). Is it actually used at runtime, or only
   present in a string the test asserts on?
3. **Pruning safety** — an incomplete directory walk must raise `WalkIncomplete` **before any
   write or delete**, so a partial enumeration cannot prune live rows. Trace the actual order of
   operations in `Store.ingest`, not the docstring.
4. **τ is query-level** — the no-answer threshold is a decision about the whole result based on the
   top score, not a per-hit filter, and an empty candidate set is no-answer regardless of τ.
5. **Rerank tail + chunk ids** — fuse → truncate to depth → rerank the first min(depth,50) →
   append the untouched tail in RRF order; reranker scores are never compared against RRF scores;
   `(chunk_id, path)` pairs survive into `xyz/eval/metrics.py` so a same-path reorder is visible.

## The measured result to explain (this is the important question)
30-query set, depth 100, 3,020 chunks. dense MRR 0.9444 / R@1 0.9000 · hybrid 0.9222 / 0.8667 ·
hybrid+rerank 0.9016 / 0.8667. Rerank latency p50 50,004 ms on CPU. 30/30 top-10s reordered.

**Dense-only beat both hybrid arms.** Is that a BUG in this code — wrong score signs, a broken BM25
sanitiser, bad RRF, wrong rerank depth, reranker applied to the wrong text — or a genuine property
of a saturated 30-query set plus a general-domain reranker on code? Point at the specific code that
decides it. This is the finding I most need graded.

## Output format (keep it under 400 words)
Line 1: `VERDICT: PASS` or `VERDICT: CHANGES REQUESTED`.
Then graded bullets `[Blocker]`/`[Should]`/`[Nit]`/`[Pass]`, each with file:line.
End with: which items must be fixed BEFORE merging PR #15, versus filed as follow-ups.
Be blunt. Do not pad. Do not restate the contracts back to me.

codex
I’m applying the repo’s debugging discipline to trace the measured regression through the implementation and tests, within the requested audit scope.
exec
/bin/zsh -lc "sed -n '1,240p' /Users/noelsaw/.agents/skills/debug-mantra/SKILL.md && printf '\\n--- files ---\\n' && rg --files xyz/index/store.py xyz/retrieve xyz/eval xyz/ingest tests | sort" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-22132-rax9y1zy
 succeeded in 0ms:
---
name: debug-mantra
description: "Four-mantra debugging discipline — reproduce, trace the fail path, falsify the hypothesis, cross-reference every breadcrumb. Recite the mantra block verbatim at the start of any debugging session, then apply the four steps in order before proposing any fix. Trigger on /debug-mantra and proactively whenever debugging starts — user reports a bug, says something is broken/throwing/failing, asks to debug/diagnose/investigate an issue, pastes a stack trace or error log, or asks an attribution question ('where is this coming from?', 'what posts/triggers/generates this?', 'why is X appearing?') where the answer is an unknown source to find, not just a crash to fix. Also trigger on /debug-mantra plan, and proactively when writing or reviewing the acceptance criteria of a plan, capture doc, or marathon plan — apply the same four mantras through the pivots in 'When the target is a plan, not a bug'. Adapted from: https://github.com/thananon/9arm-skills"
---

# Debug Mantra

Four-step discipline for any debug session. Recite verbatim, then apply in order. When the target is a plan rather than a bug, the same four steps apply read through the pivots in [When the target is a plan, not a bug](#when-the-target-is-a-plan-not-a-bug).

## Recite this — verbatim, as the first thing in your first response

> **Mantra:**
> 1. **First is reproducibility.** Can the issue — or the artifact — be reproduced or observed reliably?
> 2. **Know the fail path.** Debugger first; then source trace + knob enumeration; then in-code instrumentation.
> 3. **Question your hypothesis.** What would disprove it?
> 4. **Every run is a breadcrumb.** Cross-reference all of them.

Then begin work.

---

## 1. Reproduce reliably

Establish ground truth before anything else — a runnable repro for a failure, a direct look at the real artifact for an attribution question.

**Reproduce = observe the primitive ground truth, not your impression of it.** For a crash that's a failing test; for an *attribution* question ("what posts this?", "where does X come from?") it's inspecting the actual artifact — the real message, record, or raw bytes — **before** theorising about its origin. A screenshot, a rendered view, or a remembered detail is an **observation to verify, not an axiom to build on**: name it as assumption-zero and check it first. The cheapest disproof is usually looking straight at the thing — one query against the real object beats a sweep of the code that *might* have produced it. Beware visual grouping and other rendering artifacts: what looks like "one consolidated thing" may be many separate ones (or vice versa) — confirm against the raw object before any hypothesis inherits the shape.

- **Reliable repro** → capture the exact steps, inputs, and environment as a runnable artifact: failing test, curl script, CLI invocation, replay harness.
- **Flaky repro** → the bug is not yet debuggable. Raise the rate first: loop the trigger, parallelise, add stress, narrow timing windows, inject sleeps. 50% flake is debuggable; 1% is not.
- **No repro at all** → stop. Say so explicitly. Ask the user for env access, captured artifacts (HAR, log dump, core), or permission to instrument. Do **not** proceed to hypothesise.

Target: a fast (1–5 s), deterministic pass/fail signal. Pin time, seed the RNG, freeze network, isolate filesystem.

## 2. Know the fail path

Once reproducible, find *where* the code breaks and *what stops it from breaking*. The differential narrows the search. Try in this order — escalate only when the prior tactic fails.

1. **Attach a debugger.** If the env supports it, attach and step to the failure site. One breakpoint beats ten logs. Do this **before** turning any knobs.
2. **Source trace + knob enumeration.** If no debugger (or it can't reach the bug), trace the code path end-to-end and list every knob that can influence the outcome:
   - config flags, env vars, feature toggles
   - branch conditions, input shape
   - timing, concurrency, build options
   Each knob is a candidate axis to flip in the differential. Flip one at a time.
3. **In-code instrumentation.** If outside knobs can't move the failure, go inside: `printf` / log statements at the suspected fail site, dump the relevant internal state. Tag every probe with a unique prefix (e.g. `[DBG-a4f2]`) so cleanup is a single grep. Let the trace show where reality diverges from your model.

## 3. Falsify the hypothesis

When a candidate root cause surfaces, scrutinise it **before** testing it.

- Does it actually explain the symptom end-to-end? Walk it through.
- What is the simplest **proof**? What is the cleanest **disproof**?
- Run the **disproof first**. If the hypothesis survives, it's real. If it dies, you saved yourself from chasing a phantom.
- Generate 3–5 ranked hypotheses, not one. Single-hypothesis thinking anchors on the first plausible idea.

## 4. Every run is a breadcrumb

Maintain a running **ledger** of every experiment in this session. Each entry: what changed, what happened, what it ruled in or out.

- When a new hypothesis surfaces, walk the ledger. Does it hold for **every** prior observation, not just the most recent?
- If any past run contradicts it, the hypothesis is wrong or incomplete — refine or discard.
- When in doubt, design the **single experiment** whose outcome makes it certain. Run that next, instead of churning on adjacent runs.
- Update the ledger after every run. It is your memory across the session.

---

## When the target is a plan, not a bug

Invoked as `/debug-mantra plan`, or proactively when writing or reviewing the acceptance criteria of a plan, capture doc, or marathon plan. The four mantras apply unchanged and the recital stands verbatim — "the issue — or the artifact" includes the plan's own evidence. Each step is read through its pivot:

| Step | Debug reading | Plan pivot |
|---|---|---|
| 1. Reproduce | Runnable repro of the failure. | **Measured ground truth at plan time.** Every count, `file:line`, and live-state claim in the plan is re-run now, not remembered — the "measured, not assumed" evidence table in [#419's "What is actually unenforced today" section](https://github.com/HiQS-Labs/XYZ-forge/issues/419) is the shape. A recalled repo state is hypothesis-zero. |
| 2. Fail path | Trace the code that breaks. | **Trace the real path the plan changes**, before proposing: walk it and enumerate every caller and surface it touches. A criterion about a path nobody traced is a guess wearing a checkbox. |
| 3. Falsify | Disprove the root-cause hypothesis. | **Falsify the acceptance criteria.** Each criterion must name how it fails — a criterion that cannot fail is decorative, and one an empty input satisfies passes vacuously. Specify the red control *and where its evidence will land* (`test/baselines/` negative-control pattern). Rank 3–5 alternatives for the load-bearing design choice and name the strongest counterargument ([#419](https://github.com/HiQS-Labs/XYZ-forge/issues/419)'s "Open question for the reviewers" block is the pattern). |
| 4. Breadcrumbs | Session experiment ledger. | **Recon ledger.** Record the greps, counts, and probes that grounded the plan, citable from the plan or its capture doc. Before finalizing, walk the ledger against what is already shipped — a plan resting on a stale claim (feature already exists, path already changed) inherits the stale claim. |

**The plan-only rule, and why pivot 3 is the strictest:** at plan time falsification is *specified*, not *performed* — strictly weaker evidence than a red control you have watched fire. That gap is why each criterion must name a destination for its red evidence: a planned red control that is not witnessed when implemented is a promise, not a control. Plan reviews have caught criteria "satisfiable by an empty pre-created file" and "satisfiable by a print statement while the defect persisted" — both passed review as written.

Scale rigor as ever: a one-line fix's plan needs a confirming observation, not the full table; a marathon or large-refactor plan needs every pivot. For large refactors this is the SOP "Arc planning" discipline applied debug-mantra-first.

## Operating rules

- Recite the mantra block **once** per debug session, in your first response. Do not re-recite mid-session.
- Recite **verbatim**. Never paraphrase or abridge the recital.
- If the user says "skip the mantra" → skip the recital but still apply the four steps silently.
- Apply the four steps **in order**:
  - Do not propose a fix before #1 is satisfied (reliable repro exists).
  - Do not start testing hypotheses before #2 has narrowed the fail path.
  - Do not commit to a hypothesis before #3 has tried to disprove it.
  - Do not declare a hypothesis correct until #4 confirms it against every prior breadcrumb.
- **Scale rigor to the bug.** The gate is on *evidence*, not ceremony: a trivially obvious defect — a typo, a stack trace pointing straight at the line — needs a confirming **observation**, not necessarily a runnable harness or a written ledger. The burden stays on a direct look, never on assumption.
- If you catch yourself proposing a fix without a reliable repro, stop and return to step 1.
- If you catch yourself building on an unverified observation ("it's obviously X", "that's clearly one Y") — especially one drawn from a screenshot, a rendered view, or memory — stop and inspect the raw artifact first. The impression is hypothesis-zero, not ground truth, and a single direct look at the real object usually settles it faster than any search of the code that might explain it.
- The mantra is a constraint **you** carry through the session — not advice to deliver back to the user.

--- files ---
tests/__init__.py
tests/fakes.py
tests/fixtures/mini-repo/Dockerfile
tests/fixtures/mini-repo/app/example.php
tests/fixtures/mini-repo/app/example.py
tests/fixtures/mini-repo/app/example.ts
tests/fixtures/mini-repo/broken.py
tests/fixtures/mini-repo/config.yml
tests/fixtures/mini-repo/docs/guide.md
tests/fixtures/mini-repo/node_modules/ignored.js
tests/test_chunkers.py
tests/test_cli.py
tests/test_metrics.py
tests/test_retrieve.py
tests/test_smoke.py
tests/test_store.py
xyz/eval/__init__.py
xyz/eval/metrics.py
xyz/index/store.py
xyz/ingest/__init__.py
xyz/ingest/chunk.py
xyz/ingest/walk.py
xyz/retrieve/__init__.py
xyz/retrieve/dense.py
xyz/retrieve/fuse.py
xyz/retrieve/latency.py
xyz/retrieve/lexical.py
xyz/retrieve/models.py
xyz/retrieve/pipeline.py
xyz/retrieve/rerank.py

codex
> **Mantra:**
> 1. **First is reproducibility.** Can the issue — or the artifact — be reproduced or observed reliably?
> 2. **Know the fail path.** Debugger first; then source trace + knob enumeration; then in-code instrumentation.
> 3. **Question your hypothesis.** What would disprove it?
> 4. **Every run is a breadcrumb.** Cross-reference all of them.


exec
/bin/zsh -lc 'nl -ba xyz/index/store.py && nl -ba xyz/retrieve/pipeline.py && nl -ba xyz/retrieve/dense.py && nl -ba xyz/retrieve/lexical.py && nl -ba xyz/retrieve/fuse.py && nl -ba xyz/eval/metrics.py && nl -ba xyz/ingest/walk.py' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-22132-rax9y1zy
 succeeded in 0ms:
     1	"""SQLite-backed chunk, lexical, vector, and embedding-cache store."""
     2	
     3	from __future__ import annotations
     4	
     5	import hashlib
     6	import os
     7	import sqlite3
     8	import time
     9	from collections.abc import Callable, Sequence
    10	from dataclasses import dataclass
    11	from pathlib import Path
    12	from typing import Any
    13	
    14	import numpy as np
    15	import sqlite_vec
    16	
    17	from xyz.index.embed import Embedder
    18	from xyz.ingest import Chunk, ChunkResult, chunk_file, chunk_repo, walk_repo
    19	
    20	
    21	SCHEMA_VERSION = "1"
    22	
    23	
    24	class StoreError(RuntimeError):
    25	    """Base class for index-store failures."""
    26	
    27	
    28	class IndexMismatch(StoreError):
    29	    """The requested embedder does not match the index metadata."""
    30	
    31	
    32	class EmptyCorpus(StoreError):
    33	    """A traversal completed successfully but found no indexable files."""
    34	
    35	
    36	class WalkIncomplete(StoreError):
    37	    """A traversal could not prove a complete view of its requested scope."""
    38	
    39	    def __init__(self, errors: Sequence[str]) -> None:
    40	        self.errors = tuple(errors)
    41	        super().__init__("repository walk incomplete: " + "; ".join(self.errors))
    42	
    43	
    44	@dataclass(frozen=True)
    45	class IngestReport:
    46	    files_seen: int
    47	    files_skipped: int
    48	    files_reingested: int
    49	    files_pruned: int
    50	    chunks_written: int
    51	    chunks_embedded: int
    52	    cache_hits: int
    53	    warnings: tuple[str, ...]
    54	    seconds: float
    55	
    56	
    57	@dataclass(frozen=True)
    58	class StoreStats:
    59	    chunks: int
    60	    chunks_fts: int
    61	    chunks_vec: int
    62	    embed_cache: int
    63	    files: int
    64	
    65	    def __getitem__(self, key: str) -> int:
    66	        return getattr(self, key)
    67	
    68	
    69	def _normalise_prefixes(prefixes: Sequence[str] | None) -> tuple[str, ...] | None:
    70	    if prefixes is None:
    71	        return None
    72	    result: set[str] = set()
    73	    for prefix in prefixes:
    74	        value = prefix.replace(os.sep, "/")
    75	        if value.startswith("./"):
    76	            value = value[2:]
    77	        value = value.lstrip("/")
    78	        if value and not value.endswith("/"):
    79	            value += "/"
    80	        result.add(value)
    81	    return tuple(sorted(result))
    82	
    83	
    84	def _in_scope(path: str, prefixes: tuple[str, ...] | None) -> bool:
    85	    return prefixes is None or any(path.startswith(prefix) for prefix in prefixes)
    86	
    87	
    88	class Store:
    89	    """The sole writer for an XYZ index."""
    90	
    91	    def __init__(self, connection: sqlite3.Connection, embedder: Embedder) -> None:
    92	        self.connection = connection
    93	        self.embedder = embedder
    94	
    95	    @classmethod
    96	    def open(cls, db_path: str | os.PathLike[str], embedder: Embedder) -> Store:
    97	        path = Path(db_path)
    98	        path.parent.mkdir(parents=True, exist_ok=True)
    99	        connection = sqlite3.connect(path)
   100	        store = cls(connection, embedder)
   101	        try:
   102	            has_meta = connection.execute(
   103	                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'meta'"
   104	            ).fetchone()
   105	            if has_meta:
   106	                store.check_embedder(embedder)
   107	            connection.execute("PRAGMA foreign_keys=ON")
   108	            connection.execute("PRAGMA journal_mode=WAL")
   109	            connection.enable_load_extension(True)
   110	            sqlite_vec.load(connection)
   111	            connection.enable_load_extension(False)
   112	            store._initialise_schema()
   113	            store.check_embedder(embedder)
   114	        except Exception:
   115	            connection.close()
   116	            raise
   117	        return store
   118	
   119	    def _initialise_schema(self) -> None:
   120	        dim = int(self.embedder.dim)
   121	        if dim <= 0:
   122	            raise ValueError(f"embedder dim must be positive, got {dim}")
   123	        with self.connection:
   124	            self.connection.executescript(
   125	                f"""
   126	                CREATE TABLE IF NOT EXISTS meta(
   127	                    key TEXT PRIMARY KEY,
   128	                    value TEXT NOT NULL
   129	                );
   130	                CREATE TABLE IF NOT EXISTS files(
   131	                    repo TEXT NOT NULL,
   132	                    path TEXT NOT NULL,
   133	                    file_sha TEXT NOT NULL,
   134	                    chunk_count INTEGER NOT NULL,
   135	                    ingested_at TEXT NOT NULL,
   136	                    PRIMARY KEY(repo, path)
   137	                );
   138	                CREATE TABLE IF NOT EXISTS chunks(
   139	                    id INTEGER PRIMARY KEY,
   140	                    repo TEXT NOT NULL,
   141	                    path TEXT NOT NULL,
   142	                    kind TEXT NOT NULL,
   143	                    qualified_name TEXT NOT NULL,
   144	                    start_line INTEGER NOT NULL,
   145	                    end_line INTEGER NOT NULL,
   146	                    content_sha TEXT NOT NULL,
   147	                    text TEXT NOT NULL,
   148	                    embedded_text TEXT NOT NULL
   149	                );
   150	                CREATE INDEX IF NOT EXISTS chunks_repo_path ON chunks(repo, path);
   151	                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
   152	                    embedded_text,
   153	                    qualified_name,
   154	                    path,
   155	                    content='chunks',
   156	                    content_rowid='id'
   157	                );
   158	                CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
   159	                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
   160	                    VALUES (new.id, new.embedded_text, new.qualified_name, new.path);
   161	                END;
   162	                CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
   163	                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
   164	                    VALUES ('delete', old.id, old.embedded_text, old.qualified_name, old.path);
   165	                END;
   166	                CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
   167	                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
   168	                    VALUES ('delete', old.id, old.embedded_text, old.qualified_name, old.path);
   169	                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
   170	                    VALUES (new.id, new.embedded_text, new.qualified_name, new.path);
   171	                END;
   172	                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
   173	                    embedding float[{dim}]
   174	                );
   175	                CREATE TABLE IF NOT EXISTS embed_cache(
   176	                    content_sha TEXT NOT NULL,
   177	                    model TEXT NOT NULL,
   178	                    dim INTEGER NOT NULL,
   179	                    provider TEXT NOT NULL,
   180	                    vector BLOB NOT NULL,
   181	                    PRIMARY KEY(content_sha, model, dim, provider)
   182	                );
   183	                """
   184	            )
   185	            current = dict(self.connection.execute("SELECT key, value FROM meta"))
   186	            if not current:
   187	                self.connection.executemany(
   188	                    "INSERT INTO meta(key, value) VALUES (?, ?)",
   189	                    (
   190	                        ("model", self.embedder.model_id),
   191	                        ("dim", str(dim)),
   192	                        ("provider", self.embedder.provider),
   193	                        ("schema_version", SCHEMA_VERSION),
   194	                    ),
   195	                )
   196	
   197	    def check_embedder(self, embedder: Embedder) -> None:
   198	        actual = dict(self.connection.execute("SELECT key, value FROM meta"))
   199	        expected = {
   200	            "model": str(embedder.model_id),
   201	            "dim": str(embedder.dim),
   202	            "provider": str(embedder.provider),
   203	        }
   204	        for field in ("model", "dim", "provider"):
   205	            if actual.get(field) != expected[field]:
   206	                raise IndexMismatch(
   207	                    f"index {field} mismatch: stored={actual.get(field)!r}, requested={expected[field]!r}"
   208	                )
   209	
   210	    def close(self) -> None:
   211	        self.connection.close()
   212	
   213	    def __enter__(self) -> Store:
   214	        return self
   215	
   216	    def __exit__(self, *_args: object) -> None:
   217	        self.close()
   218	
   219	    def _snapshot_chunks(
   220	        self,
   221	        repo: str,
   222	        root: Path,
   223	        walked: Sequence[tuple[str, bytes]],
   224	        chunker: Callable[..., ChunkResult],
   225	        include_prefixes: Sequence[str] | None,
   226	    ) -> tuple[dict[str, list[Chunk]], list[str]]:
   227	        if chunker is chunk_repo:
   228	            by_path: dict[str, list[Chunk]] = {}
   229	            warnings: list[str] = []
   230	            for path, source in walked:
   231	                result = chunk_file(repo, path, source)
   232	                by_path[path] = result.chunks
   233	                warnings.extend(result.warnings)
   234	            return by_path, warnings
   235	
   236	        result = chunker(repo, root, include_prefixes=include_prefixes)
   237	        walk_errors = [
   238	            warning.removeprefix("walk error: ")
   239	            for warning in result.warnings
   240	            if warning.startswith("walk error: ")
   241	        ]
   242	        if walk_errors:
   243	            raise WalkIncomplete(walk_errors)
   244	        by_path = {path: [] for path, _source in walked}
   245	        for chunk in result.chunks:
   246	            by_path.setdefault(chunk.path, []).append(chunk)
   247	        return by_path, list(result.warnings)
   248	
   249	    def ingest(
   250	        self,
   251	        repo: str,
   252	        root: str | os.PathLike[str],
   253	        chunker: Callable[..., ChunkResult] = chunk_repo,
   254	        include_prefixes: Sequence[str] | None = None,
   255	        progress: Callable[[int, int, float], None] | None = None,
   256	    ) -> IngestReport:
   257	        started = time.monotonic()
   258	        self.check_embedder(self.embedder)
   259	        root_path = Path(root)
   260	        errors: list[str] = []
   261	        walked = list(walk_repo(root_path, include_prefixes=include_prefixes, errors=errors))
   262	        if errors:
   263	            raise WalkIncomplete(errors)
   264	        if not walked:
   265	            raise EmptyCorpus(f"repository walk found no indexable files under {root_path}")
   266	
   267	        chunks_by_path, warnings = self._snapshot_chunks(
   268	            repo, root_path, walked, chunker, include_prefixes
   269	        )
   270	        file_shas = {path: hashlib.sha256(source).hexdigest() for path, source in walked}
   271	        existing = {
   272	            path: file_sha
   273	            for path, file_sha in self.connection.execute(
   274	                "SELECT path, file_sha FROM files WHERE repo = ?", (repo,)
   275	            )
   276	        }
   277	        candidate_chunks = sum(
   278	            len(chunks_by_path.get(path, ()))
   279	            for path, _source in walked
   280	            if existing.get(path) != file_shas[path]
   281	        )
   282	
   283	        files_skipped = 0
   284	        files_reingested = 0
   285	        chunks_written = 0
   286	        chunks_embedded = 0
   287	        cache_hits = 0
   288	
   289	        for path, _source in walked:
   290	            if existing.get(path) == file_shas[path]:
   291	                files_skipped += 1
   292	                continue
   293	
   294	            chunks = chunks_by_path.get(path, [])
   295	            vectors: dict[str, bytes] = {}
   296	            missing_by_sha: dict[str, Chunk] = {}
   297	            for chunk in chunks:
   298	                row = self.connection.execute(
   299	                    """
   300	                    SELECT vector FROM embed_cache
   301	                    WHERE content_sha = ? AND model = ? AND dim = ? AND provider = ?
   302	                    """,
   303	                    (
   304	                        chunk.content_sha,
   305	                        self.embedder.model_id,
   306	                        self.embedder.dim,
   307	                        self.embedder.provider,
   308	                    ),
   309	                ).fetchone()
   310	                if row is None:
   311	                    missing_by_sha.setdefault(chunk.content_sha, chunk)
   312	                else:
   313	                    vectors[chunk.content_sha] = row[0]
   314	                    cache_hits += 1
   315	
   316	            missing = list(missing_by_sha.values())
   317	
   318	            if missing:
   319	                encoded = np.asarray(
   320	                    self.embedder.encode_documents([chunk.embedded_text for chunk in missing]),
   321	                    dtype=np.float32,
   322	                )
   323	                if encoded.shape != (len(missing), self.embedder.dim):
   324	                    raise ValueError(
   325	                        f"embedder returned shape {encoded.shape}; "
   326	                        f"expected {(len(missing), self.embedder.dim)}"
   327	                    )
   328	                for chunk, vector in zip(missing, encoded, strict=True):
   329	                    vectors[chunk.content_sha] = sqlite_vec.serialize_float32(vector.tolist())
   330	
   331	            with self.connection:
   332	                old_ids = [
   333	                    row[0]
   334	                    for row in self.connection.execute(
   335	                        "SELECT id FROM chunks WHERE repo = ? AND path = ?", (repo, path)
   336	                    )
   337	                ]
   338	                self.connection.executemany(
   339	                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in old_ids)
   340	                )
   341	                self.connection.execute(
   342	                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
   343	                )
   344	                for chunk in missing:
   345	                    self.connection.execute(
   346	                        """
   347	                        INSERT OR IGNORE INTO embed_cache
   348	                            (content_sha, model, dim, provider, vector)
   349	                        VALUES (?, ?, ?, ?, ?)
   350	                        """,
   351	                        (
   352	                            chunk.content_sha,
   353	                            self.embedder.model_id,
   354	                            self.embedder.dim,
   355	                            self.embedder.provider,
   356	                            vectors[chunk.content_sha],
   357	                        ),
   358	                    )
   359	                for chunk in chunks:
   360	                    cursor = self.connection.execute(
   361	                        """
   362	                        INSERT INTO chunks(
   363	                            repo, path, kind, qualified_name, start_line, end_line,
   364	                            content_sha, text, embedded_text
   365	                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
   366	                        """,
   367	                        (
   368	                            chunk.repo,
   369	                            chunk.path,
   370	                            chunk.kind,
   371	                            chunk.qualified_name,
   372	                            chunk.start_line,
   373	                            chunk.end_line,
   374	                            chunk.content_sha,
   375	                            chunk.text,
   376	                            chunk.embedded_text,
   377	                        ),
   378	                    )
   379	                    self.connection.execute(
   380	                        "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)",
   381	                        (cursor.lastrowid, vectors[chunk.content_sha]),
   382	                    )
   383	                self.connection.execute(
   384	                    """
   385	                    INSERT INTO files(repo, path, file_sha, chunk_count, ingested_at)
   386	                    VALUES (?, ?, ?, ?, datetime('now'))
   387	                    ON CONFLICT(repo, path) DO UPDATE SET
   388	                        file_sha=excluded.file_sha,
   389	                        chunk_count=excluded.chunk_count,
   390	                        ingested_at=excluded.ingested_at
   391	                    """,
   392	                    (repo, path, file_shas[path], len(chunks)),
   393	                )
   394	            files_reingested += 1
   395	            chunks_written += len(chunks)
   396	            chunks_embedded += len(missing)
   397	            if progress is not None and missing:
   398	                progress(chunks_embedded, candidate_chunks, time.monotonic() - started)
   399	
   400	        walked_paths = set(file_shas)
   401	        prefixes = _normalise_prefixes(include_prefixes)
   402	        pruned = [
   403	            path
   404	            for path in existing
   405	            if path not in walked_paths and _in_scope(path, prefixes)
   406	        ]
   407	        for path in pruned:
   408	            with self.connection:
   409	                ids = [
   410	                    row[0]
   411	                    for row in self.connection.execute(
   412	                        "SELECT id FROM chunks WHERE repo = ? AND path = ?", (repo, path)
   413	                    )
   414	                ]
   415	                self.connection.executemany(
   416	                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in ids)
   417	                )
   418	                self.connection.execute(
   419	                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
   420	                )
   421	                self.connection.execute(
   422	                    "DELETE FROM files WHERE repo = ? AND path = ?", (repo, path)
   423	                )
   424	
   425	        return IngestReport(
   426	            files_seen=len(walked),
   427	            files_skipped=files_skipped,
   428	            files_reingested=files_reingested,
   429	            files_pruned=len(pruned),
   430	            chunks_written=chunks_written,
   431	            chunks_embedded=chunks_embedded,
   432	            cache_hits=cache_hits,
   433	            warnings=tuple(warnings),
   434	            seconds=time.monotonic() - started,
   435	        )
   436	
   437	    def stats(self) -> StoreStats:
   438	        def count(table: str) -> int:
   439	            return int(self.connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0])
   440	
   441	        return StoreStats(
   442	            chunks=count("chunks"),
   443	            chunks_fts=count("chunks_fts"),
   444	            chunks_vec=count("chunks_vec"),
   445	            embed_cache=count("embed_cache"),
   446	            files=count("files"),
   447	        )
   448	
   449	    def fts_match(self, token: str, limit: int = 100) -> list[int]:
   450	        return [
   451	            int(row[0])
   452	            for row in self.connection.execute(
   453	                "SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?",
   454	                (token, limit),
   455	            )
   456	        ]
     1	"""Instrumented dense, lexical, hybrid, and reranked retrieval pipeline."""
     2	
     3	from __future__ import annotations
     4	
     5	import time
     6	from collections.abc import Sequence
     7	
     8	from xyz.index.embed import Embedder
     9	from xyz.index.store import Store
    10	from xyz.retrieve.dense import dense_search
    11	from xyz.retrieve.fuse import rrf
    12	from xyz.retrieve.lexical import bm25_search
    13	from xyz.retrieve.models import Hit, SearchHit, SearchResult
    14	from xyz.retrieve.rerank import Reranker
    15	
    16	
    17	TIMING_STAGES = ("embed_query", "bm25", "dense", "fuse", "rerank", "total")
    18	MODES = frozenset({"auto", "dense", "bm25", "hybrid", "hybrid+rerank"})
    19	
    20	
    21	class Retriever:
    22	    def __init__(self, store: Store, embedder: Embedder, reranker: Reranker | None = None) -> None:
    23	        store.check_embedder(embedder)
    24	        self.store = store
    25	        self.embedder = embedder
    26	        self.reranker = reranker
    27	
    28	    @staticmethod
    29	    def _elapsed(started: float) -> float:
    30	        return max(0.0, (time.perf_counter() - started) * 1000.0)
    31	
    32	    def _chunk_rows(self, ids: Sequence[int]) -> dict[int, tuple[object, ...]]:
    33	        if not ids:
    34	            return {}
    35	        placeholders = ",".join("?" for _ in ids)
    36	        rows = self.store.connection.execute(
    37	            f"""
    38	            SELECT id, repo, path, kind, qualified_name, start_line, end_line, text, embedded_text
    39	            FROM chunks WHERE id IN ({placeholders})
    40	            """,
    41	            tuple(ids),
    42	        )
    43	        return {int(row[0]): tuple(row[1:]) for row in rows}
    44	
    45	    def search(
    46	        self,
    47	        query: str,
    48	        k: int = 10,
    49	        fetch_k: int = 50,
    50	        mode: str = "auto",
    51	        tau: float | None = None,
    52	    ) -> SearchResult:
    53	        if mode not in MODES:
    54	            raise ValueError(f"unknown retrieval mode: {mode!r}")
    55	        if k <= 0 or fetch_k <= 0:
    56	            raise ValueError("k and fetch_k must be positive")
    57	        resolved = ("hybrid+rerank" if self.reranker is not None else "hybrid") if mode == "auto" else mode
    58	        if resolved == "hybrid+rerank" and self.reranker is None:
    59	            raise ValueError("hybrid+rerank mode requires a reranker")
    60	
    61	        timings = {stage: 0.0 for stage in TIMING_STAGES}
    62	        total_started = time.perf_counter()
    63	        dense_hits: list[Hit] = []
    64	        lexical_hits: list[Hit] = []
    65	
    66	        if resolved in {"dense", "hybrid", "hybrid+rerank"}:
    67	            started = time.perf_counter()
    68	            query_vec = self.embedder.encode_query(query)
    69	            timings["embed_query"] = self._elapsed(started)
    70	            started = time.perf_counter()
    71	            dense_hits = dense_search(self.store, query_vec, fetch_k)
    72	            timings["dense"] = self._elapsed(started)
    73	        if resolved in {"bm25", "hybrid", "hybrid+rerank"}:
    74	            started = time.perf_counter()
    75	            lexical_hits = bm25_search(self.store, query, fetch_k)
    76	            timings["bm25"] = self._elapsed(started)
    77	
    78	        if resolved == "dense":
    79	            candidates = dense_hits[:fetch_k]
    80	        elif resolved == "bm25":
    81	            candidates = lexical_hits[:fetch_k]
    82	        else:
    83	            started = time.perf_counter()
    84	            candidates = rrf([dense_hits, lexical_hits])[:fetch_k]
    85	            timings["fuse"] = self._elapsed(started)
    86	
    87	        if resolved == "hybrid+rerank" and candidates:
    88	            rerank_count = min(len(candidates), 50)
    89	            head = candidates[:rerank_count]
    90	            rows = self._chunk_rows([hit.chunk_id for hit in head])
    91	            texts = [str(rows[hit.chunk_id][7]) for hit in head]
    92	            started = time.perf_counter()
    93	            scores = self.reranker.score(query, texts)  # type: ignore[union-attr]
    94	            timings["rerank"] = self._elapsed(started)
    95	            if len(scores) != len(head):
    96	                raise ValueError(f"reranker returned {len(scores)} scores for {len(head)} candidates")
    97	            rescored = [
    98	                Hit(hit.chunk_id, float(score), "rerank")
    99	                for hit, score in zip(head, scores, strict=True)
   100	            ]
   101	            candidates = sorted(rescored, key=lambda hit: (-hit.score, hit.chunk_id)) + candidates[rerank_count:]
   102	
   103	        rows = self._chunk_rows([hit.chunk_id for hit in candidates])
   104	        ranking = [(hit.chunk_id, str(rows[hit.chunk_id][1])) for hit in candidates]
   105	        top_score = candidates[0].score if candidates else None
   106	        no_answer = top_score is None or (tau is not None and top_score < tau)
   107	        materialised: list[SearchHit] = []
   108	        if not no_answer:
   109	            for hit in candidates[:k]:
   110	                repo, path, kind, name, start_line, end_line, text, embedded_text = rows[hit.chunk_id]
   111	                materialised.append(
   112	                    SearchHit(
   113	                        hit.chunk_id, str(repo), str(path), str(kind), str(name),
   114	                        int(start_line), int(end_line), str(text), str(embedded_text),
   115	                        hit.score, hit.stage,
   116	                    )
   117	                )
   118	        timings["total"] = self._elapsed(total_started)
   119	        return SearchResult(materialised, ranking, no_answer, timings, resolved)
     1	"""sqlite-vec nearest-neighbour retrieval."""
     2	
     3	from __future__ import annotations
     4	
     5	from collections.abc import Sequence
     6	
     7	import numpy as np
     8	import sqlite_vec
     9	
    10	from xyz.index.store import Store
    11	from xyz.retrieve.models import Hit
    12	
    13	
    14	KNN_SQL = """
    15	SELECT rowid, distance
    16	FROM chunks_vec
    17	WHERE embedding MATCH ? AND k = ?
    18	ORDER BY distance ASC
    19	"""
    20	
    21	
    22	def dense_search(store: Store, query_vec: Sequence[float] | np.ndarray, k: int) -> list[Hit]:
    23	    """Return the nearest vectors with negated distances as scores."""
    24	
    25	    if k <= 0:
    26	        return []
    27	    vector = np.asarray(query_vec, dtype=np.float32)
    28	    if vector.shape != (store.embedder.dim,):
    29	        raise ValueError(
    30	            f"query vector has shape {vector.shape}; expected {(store.embedder.dim,)}"
    31	        )
    32	    encoded = sqlite_vec.serialize_float32(vector.tolist())
    33	    rows = store.connection.execute(KNN_SQL, (encoded, k))
    34	    return [Hit(int(chunk_id), -float(distance), "dense") for chunk_id, distance in rows]
     1	"""FTS5/BM25 retrieval with safe query construction."""
     2	
     3	from __future__ import annotations
     4	
     5	import re
     6	
     7	from xyz.index.store import Store
     8	from xyz.retrieve.models import Hit
     9	
    10	
    11	_TOKEN = re.compile(r"[^\W_]+(?:_[^\W_]+)*", re.UNICODE)
    12	_STOPWORDS = frozenset(
    13	    {
    14	        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    15	        "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "with",
    16	    }
    17	)
    18	
    19	
    20	def sanitise_fts_query(query: str) -> str | None:
    21	    """Turn user text into an operator-free OR query, or ``None`` if empty."""
    22	
    23	    tokens: list[str] = []
    24	    seen: set[str] = set()
    25	    for match in _TOKEN.finditer(query):
    26	        token = match.group(0)
    27	        folded = token.casefold()
    28	        if folded in _STOPWORDS or folded in seen:
    29	            continue
    30	        seen.add(folded)
    31	        tokens.append(token.replace('"', '""'))
    32	    if not tokens:
    33	        return None
    34	    return " OR ".join(f'"{token}"' for token in tokens)
    35	
    36	
    37	def bm25_search(store: Store, query: str, k: int) -> list[Hit]:
    38	    """Return the best lexical matches with negated FTS5 BM25 scores."""
    39	
    40	    if k <= 0:
    41	        return []
    42	    safe_query = sanitise_fts_query(query)
    43	    if safe_query is None:
    44	        return []
    45	    rows = store.connection.execute(
    46	        """
    47	        SELECT rowid, bm25(chunks_fts) AS distance
    48	        FROM chunks_fts
    49	        WHERE chunks_fts MATCH ?
    50	        ORDER BY distance ASC, rowid ASC
    51	        LIMIT ?
    52	        """,
    53	        (safe_query, k),
    54	    )
    55	    return [Hit(int(chunk_id), -float(distance), "bm25") for chunk_id, distance in rows]
     1	"""Deterministic reciprocal-rank fusion."""
     2	
     3	from __future__ import annotations
     4	
     5	from collections.abc import Sequence
     6	
     7	from xyz.retrieve.models import Hit
     8	
     9	
    10	def rrf(rankings: Sequence[Sequence[Hit]], k: int = 60) -> list[Hit]:
    11	    """Fuse rankings using one-based ranks and deterministic chunk-id ties."""
    12	
    13	    if k < 0:
    14	        raise ValueError("RRF k must be non-negative")
    15	    scores: dict[int, float] = {}
    16	    for ranking in rankings:
    17	        seen: set[int] = set()
    18	        for rank, hit in enumerate(ranking, start=1):
    19	            if hit.chunk_id in seen:
    20	                continue
    21	            seen.add(hit.chunk_id)
    22	            scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (k + rank)
    23	    hits = [Hit(chunk_id, score, "rrf") for chunk_id, score in scores.items()]
    24	    return sorted(hits, key=lambda hit: (-hit.score, hit.chunk_id))
     1	"""Depth-bounded retrieval metrics with chunk identity preserved."""
     2	
     3	from __future__ import annotations
     4	
     5	import json
     6	from dataclasses import dataclass
     7	from pathlib import Path
     8	from typing import Any, Mapping, Sequence
     9	
    10	Ranking = Sequence[tuple[int, str]]
    11	
    12	
    13	@dataclass(frozen=True)
    14	class Report:
    15	    """Serializable MRR/recall report for one retrieval mode."""
    16	
    17	    mrr: float
    18	    recalls: Mapping[int, float]
    19	    never_found: int
    20	    depth: int
    21	    per_query: Sequence[Mapping[str, Any]]
    22	
    23	    def to_dict(self) -> dict[str, Any]:
    24	        return {
    25	            "mrr": self.mrr,
    26	            "recall@1": self.recalls[1],
    27	            "recall@3": self.recalls[3],
    28	            "recall@5": self.recalls[5],
    29	            "recall@10": self.recalls[10],
    30	            "never_found": self.never_found,
    31	            "depth": self.depth,
    32	            "per_query": list(self.per_query),
    33	        }
    34	
    35	    def write_json(self, path: str | Path) -> None:
    36	        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
    37	
    38	
    39	def score(
    40	    rankings: Mapping[str, Ranking],
    41	    queries: Sequence[Mapping[str, Any]],
    42	    depth: int,
    43	) -> Report:
    44	    """Score ordered chunk rankings against path-level relevance at ``depth``."""
    45	    if not queries:
    46	        raise ValueError("query list is empty")
    47	    if depth <= 0:
    48	        raise ValueError("depth must be positive")
    49	
    50	    ranks: list[int | None] = []
    51	    rows: list[dict[str, Any]] = []
    52	    for query in queries:
    53	        text = str(query["q"])
    54	        relevant = [str(path) for path in query["relevant"]]
    55	        ordered = list(rankings.get(text, ()))[:depth]
    56	        relevant_set = set(relevant)
    57	        rank = next(
    58	            (
    59	                position
    60	                for position, (_chunk_id, path) in enumerate(ordered, start=1)
    61	                if path in relevant_set
    62	            ),
    63	            None,
    64	        )
    65	        ranks.append(rank)
    66	        rows.append(
    67	            {
    68	                "q": text,
    69	                "relevant": relevant,
    70	                "rank": rank,
    71	                "top_hit": ordered[0][1] if ordered else None,
    72	                "ranking": [
    73	                    {"chunk_id": int(chunk_id), "path": str(path)}
    74	                    for chunk_id, path in ordered
    75	                ],
    76	            }
    77	        )
    78	
    79	    count = len(ranks)
    80	    recalls = {
    81	        k: round(sum(rank is not None and rank <= k for rank in ranks) / count, 4)
    82	        for k in (1, 3, 5, 10)
    83	    }
    84	    return Report(
    85	        mrr=round(sum(1.0 / rank for rank in ranks if rank is not None) / count, 4),
    86	        recalls=recalls,
    87	        never_found=sum(rank is None for rank in ranks),
    88	        depth=depth,
    89	        per_query=rows,
    90	    )
     1	"""Deterministic, failure-aware repository traversal."""
     2	
     3	from __future__ import annotations
     4	
     5	import fnmatch
     6	import os
     7	from collections.abc import Iterator, Sequence, Set
     8	from pathlib import Path
     9	
    10	
    11	DEFAULT_INCLUDE = frozenset(
    12	    {
    13	        ".py",
    14	        ".js",
    15	        ".ts",
    16	        ".tsx",
    17	        ".jsx",
    18	        ".php",
    19	        ".md",
    20	        ".go",
    21	        ".rb",
    22	        ".sh",
    23	        ".yml",
    24	        ".yaml",
    25	        ".toml",
    26	        ".ini",
    27	        ".cfg",
    28	        ".json",
    29	        ".sql",
    30	        ".html",
    31	        ".twig",
    32	        "Dockerfile",
    33	        "docker-compose*.yml",
    34	        "Makefile",
    35	        "*.blade.php",
    36	        ".env.example",
    37	    }
    38	)
    39	
    40	DEFAULT_EXCLUDE = frozenset(
    41	    {
    42	        ".git",
    43	        ".venv",
    44	        "node_modules",
    45	        "__pycache__",
    46	        "dist",
    47	        "build",
    48	        "temp",
    49	        ".embed-tmp",
    50	        ".xyz",
    51	        ".relay-scratch",
    52	        "marathon-system",
    53	        "relay-system",
    54	    }
    55	)
    56	
    57	MAX_FILE_BYTES = 1024 * 1024
    58	BINARY_SNIFF_BYTES = 8192
    59	
    60	
    61	def _included(name: str, include: Set[str] | Sequence[str]) -> bool:
    62	    suffix = Path(name).suffix.lower()
    63	    for rule in include:
    64	        if rule.startswith(".") and "*" not in rule:
    65	            if rule == suffix or rule == name:
    66	                return True
    67	        elif fnmatch.fnmatchcase(name, rule):
    68	            return True
    69	    return False
    70	
    71	
    72	def _normalise_prefixes(prefixes: Sequence[str] | None) -> tuple[str, ...] | None:
    73	    if prefixes is None:
    74	        return None
    75	    normalised: list[str] = []
    76	    for prefix in prefixes:
    77	        value = prefix.replace(os.sep, "/")
    78	        if value.startswith("./"):
    79	            value = value[2:]
    80	        value = value.lstrip("/")
    81	        if value and not value.endswith("/"):
    82	            value += "/"
    83	        normalised.append(value)
    84	    return tuple(sorted(set(normalised)))
    85	
    86	
    87	def _directory_may_match(rel_dir: str, prefixes: tuple[str, ...] | None) -> bool:
    88	    if prefixes is None:
    89	        return True
    90	    directory = f"{rel_dir}/" if rel_dir else ""
    91	    return any(prefix.startswith(directory) or directory.startswith(prefix) for prefix in prefixes)
    92	
    93	
    94	def _file_matches(rel_path: str, prefixes: tuple[str, ...] | None) -> bool:
    95	    return prefixes is None or any(rel_path.startswith(prefix) for prefix in prefixes)
    96	
    97	
    98	def walk_repo(
    99	    root: str | os.PathLike[str],
   100	    include_ext: Set[str] | Sequence[str] = DEFAULT_INCLUDE,
   101	    exclude_dirs: Set[str] | Sequence[str] = DEFAULT_EXCLUDE,
   102	    include_prefixes: Sequence[str] | None = None,
   103	    *,
   104	    errors: list[str],
   105	) -> Iterator[tuple[str, bytes]]:
   106	    """Yield included ``(relative_path, content)`` pairs in sorted order.
   107	
   108	    Enumeration, stat, and read failures for relevant candidate paths are
   109	    recorded in ``errors``. Intentional filters are silent.
   110	    """
   111	
   112	    root_path = Path(root)
   113	    if not root_path.is_dir():
   114	        raise ValueError(f"repository root is not an existing directory: {root_path}")
   115	
   116	    excluded = set(exclude_dirs)
   117	    prefixes = _normalise_prefixes(include_prefixes)
   118	
   119	    def visit(directory: Path, rel_dir: str) -> Iterator[tuple[str, bytes]]:
   120	        try:
   121	            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
   122	        except OSError as exc:
   123	            label = rel_dir or "."
   124	            errors.append(f"{label}: {type(exc).__name__}: {exc}")
   125	            return
   126	
   127	        for entry in entries:
   128	            rel_path = f"{rel_dir}/{entry.name}" if rel_dir else entry.name
   129	            rel_path = rel_path.replace(os.sep, "/")
   130	            try:
   131	                is_dir = entry.is_dir(follow_symlinks=False)
   132	                is_file = entry.is_file(follow_symlinks=False)
   133	            except OSError as exc:
   134	                errors.append(f"{rel_path}: {type(exc).__name__}: {exc}")
   135	                continue
   136	
   137	            if is_dir:
   138	                if entry.name in excluded or not _directory_may_match(rel_path, prefixes):
   139	                    continue
   140	                yield from visit(Path(entry.path), rel_path)
   141	                continue
   142	
   143	            if not is_file or not _file_matches(rel_path, prefixes):
   144	                continue
   145	            if not _included(entry.name, include_ext):
   146	                continue
   147	
   148	            try:
   149	                if entry.stat(follow_symlinks=False).st_size > MAX_FILE_BYTES:
   150	                    continue
   151	                with open(entry.path, "rb") as handle:
   152	                    head = handle.read(BINARY_SNIFF_BYTES)
   153	                    if b"\0" in head:
   154	                        continue
   155	                    content = head + handle.read()
   156	            except OSError as exc:
   157	                errors.append(f"{rel_path}: {type(exc).__name__}: {exc}")
   158	                continue
   159	            yield rel_path, content
   160	
   161	    yield from visit(root_path, "")

exec
/bin/zsh -lc "nl -ba tests/test_retrieve.py && nl -ba tests/test_store.py && nl -ba tests/test_metrics.py && nl -ba tests/test_smoke.py && nl -ba tests/test_cli.py && nl -ba tests/fakes.py && rg -n \"chunks(_fts|_vec)?|KNN_SQL|k = \\?|LIMIT \\?|WalkIncomplete|tau|no_answer|rerank|ranking|chunk_id|rrf|bm25|dense\" tests xyz/index/store.py xyz/retrieve/pipeline.py xyz/retrieve/dense.py xyz/retrieve/lexical.py xyz/retrieve/fuse.py xyz/eval/metrics.py xyz/ingest/walk.py" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-22132-rax9y1zy
 succeeded in 0ms:
     1	"""Contract tests for hybrid retrieval and its score semantics."""
     2	
     3	from __future__ import annotations
     4	
     5	from pathlib import Path
     6	
     7	import pytest
     8	import sqlite_vec
     9	
    10	from tests.fakes import FakeEmbedder, FakeReranker
    11	from xyz.index.store import IndexMismatch, Store
    12	from xyz.retrieve.dense import KNN_SQL, dense_search
    13	from xyz.retrieve.fuse import rrf
    14	from xyz.retrieve.latency import LatencyLog
    15	from xyz.retrieve.lexical import bm25_search
    16	from xyz.retrieve.models import Hit
    17	from xyz.retrieve.pipeline import Retriever
    18	
    19	
    20	def _add_chunks(store: Store, count: int, *, same_path: bool = False) -> None:
    21	    vector = sqlite_vec.serialize_float32([1.0] + [0.0] * (store.embedder.dim - 1))
    22	    with store.connection:
    23	        for chunk_id in range(1, count + 1):
    24	            path = "same.py" if same_path else f"p{chunk_id}.py"
    25	            store.connection.execute(
    26	                """
    27	                INSERT INTO chunks(
    28	                    id, repo, path, kind, qualified_name, start_line, end_line,
    29	                    content_sha, text, embedded_text
    30	                ) VALUES (?, 'repo', ?, 'function', ?, 1, 1, ?, ?, ?)
    31	                """,
    32	                (chunk_id, path, f"f{chunk_id}", f"sha{chunk_id}", f"text {chunk_id}", f"embedded {chunk_id}"),
    33	            )
    34	            store.connection.execute(
    35	                "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)", (chunk_id, vector)
    36	            )
    37	
    38	
    39	def test_rrf_matches_hand_computed_overlap_and_tie_break() -> None:
    40	    left = [Hit(1, 9, "a"), Hit(2, 8, "a"), Hit(3, 7, "a")]
    41	    right = [Hit(3, 9, "b"), Hit(4, 8, "b"), Hit(5, 7, "b")]
    42	    fused = rrf([left, right], k=60)
    43	    assert [hit.chunk_id for hit in fused] == [3, 1, 2, 4, 5]
    44	    assert fused[0].score == pytest.approx(1 / 63 + 1 / 61)
    45	    assert fused[1].score == pytest.approx(1 / 61)
    46	    assert fused[2].score == pytest.approx(1 / 62)
    47	
    48	
    49	def test_knn_sql_uses_bound_k_and_dense_query_executes(tmp_path: Path) -> None:
    50	    assert " k = ?" in KNN_SQL
    51	    assert "LIMIT ?" not in KNN_SQL.upper()
    52	    embedder = FakeEmbedder()
    53	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
    54	        _add_chunks(store, 2)
    55	        assert len(dense_search(store, embedder.encode_query("needle"), 1)) == 1
    56	
    57	
    58	def test_bm25_sanitises_operators_empty_and_keeps_higher_better(tmp_path: Path) -> None:
    59	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
    60	        _add_chunks(store, 2)
    61	        with store.connection:
    62	            store.connection.execute(
    63	                "UPDATE chunks SET embedded_text = 'foo bar foo' WHERE id = 1"
    64	            )
    65	            store.connection.execute(
    66	                "UPDATE chunks SET embedded_text = 'foo' WHERE id = 2"
    67	            )
    68	        assert bm25_search(store, "foo-bar: baz*", 10)
    69	        assert bm25_search(store, "", 10) == []
    70	        assert bm25_search(store, "the and", 10) == []
    71	        hits = bm25_search(store, "foo bar", 10)
    72	        assert hits[0].chunk_id == 1
    73	        assert hits[0].score > hits[1].score
    74	
    75	
    76	def test_rerank_reorders_rrf_and_tau_is_query_level(
    77	    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    78	) -> None:
    79	    import xyz.retrieve.pipeline as pipeline
    80	
    81	    embedder = FakeEmbedder()
    82	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
    83	        _add_chunks(store, 3)
    84	        lane = [Hit(1, 3, "lane"), Hit(2, 2, "lane"), Hit(3, 1, "lane")]
    85	        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
    86	        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
    87	        reranker = FakeReranker({"embedded 1": 2.0, "embedded 2": 0.0, "embedded 3": 3.0})
    88	        retriever = Retriever(store, embedder, reranker)
    89	
    90	        assert retriever.search("q", mode="hybrid").ranking[0][0] == 1
    91	        reranked = retriever.search("q", k=3, mode="hybrid+rerank", tau=1.0)
    92	        assert [chunk_id for chunk_id, _path in reranked.ranking] == [3, 1, 2]
    93	        assert not reranked.no_answer
    94	        assert len(reranked.hits) == 3
    95	        assert reranked.hits[-1].score < 1.0
    96	
    97	        rejected = Retriever(
    98	            store, embedder, FakeReranker({"embedded 1": 0.2, "embedded 2": 0.1, "embedded 3": 0.0})
    99	        ).search("q", mode="hybrid+rerank", tau=0.5)
   100	        assert rejected.no_answer and rejected.hits == [] and rejected.ranking
   101	
   102	
   103	def test_candidate_depth_rerank_cap_and_same_path_identity(
   104	    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
   105	) -> None:
   106	    import xyz.retrieve.pipeline as pipeline
   107	
   108	    embedder = FakeEmbedder()
   109	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
   110	        _add_chunks(store, 120, same_path=True)
   111	        lane = [Hit(chunk_id, 121 - chunk_id, "lane") for chunk_id in range(1, 121)]
   112	        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
   113	        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
   114	        scores = {f"embedded {chunk_id}": float(51 - chunk_id) for chunk_id in range(1, 51)}
   115	        scores["embedded 1"], scores["embedded 2"] = scores["embedded 2"], scores["embedded 1"]
   116	        retriever = Retriever(store, embedder, FakeReranker(scores))
   117	        hybrid = retriever.search("q", fetch_k=100, mode="hybrid")
   118	        reranked = retriever.search("q", fetch_k=100, mode="hybrid+rerank")
   119	        assert len(reranked.ranking) == 100
   120	        assert reranked.ranking[74][0] == 75
   121	        assert 75 not in {chunk_id for chunk_id, _path in retriever.search(
   122	            "q", fetch_k=50, mode="hybrid+rerank"
   123	        ).ranking}
   124	        assert hybrid.ranking != reranked.ranking
   125	        assert [path for _chunk_id, path in hybrid.ranking] == [
   126	            path for _chunk_id, path in reranked.ranking
   127	        ]
   128	
   129	
   130	@pytest.mark.parametrize(
   131	    "kwargs",
   132	    ({"model_id": "other"}, {"dim": 9}, {"provider": "other"}),
   133	)
   134	def test_retriever_rejects_embedder_identity_mismatch(tmp_path: Path, kwargs: dict[str, object]) -> None:
   135	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
   136	        with pytest.raises(IndexMismatch):
   137	            Retriever(store, FakeEmbedder(**kwargs))
   138	
   139	
   140	def test_auto_modes_errors_timings_and_latency_summary(
   141	    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
   142	) -> None:
   143	    import xyz.retrieve.pipeline as pipeline
   144	
   145	    embedder = FakeEmbedder()
   146	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
   147	        _add_chunks(store, 1)
   148	        lane = [Hit(1, 1.0, "lane")]
   149	        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
   150	        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
   151	        plain = Retriever(store, embedder)
   152	        assert plain.search("q", mode="auto").mode == "hybrid"
   153	        with pytest.raises(ValueError, match="requires"):
   154	            plain.search("q", mode="hybrid+rerank")
   155	        assert not plain.search("q", mode="dense", tau=None).no_answer
   156	        assert plain.search("q", mode="bm25", tau=2.0).no_answer
   157	
   158	        reranked = Retriever(store, embedder, FakeReranker({"embedded 1": 1.0}))
   159	        log = LatencyLog()
   160	        for _ in range(3):
   161	            result = reranked.search("q", mode="auto")
   162	            assert result.mode == "hybrid+rerank"
   163	            assert set(result.timings) == {
   164	                "embed_query", "bm25", "dense", "fuse", "rerank", "total"
   165	            }
   166	            assert all(value >= 0 for value in result.timings.values())
   167	            log.add(result.timings)
   168	        summary = log.summary()
   169	        assert all(set(summary[stage]) == {"p50", "p95"} for stage in result.timings)
     1	"""Contract tests for the SQLite index writer and embedding adapter."""
     2	
     3	from __future__ import annotations
     4	
     5	import os
     6	import shutil
     7	from pathlib import Path
     8	
     9	import numpy as np
    10	import pytest
    11	
    12	from tests.fakes import FakeEmbedder
    13	from xyz.index.embed import QUERY_PREFIX, CodeRankEmbedder
    14	from xyz.index.store import EmptyCorpus, IndexMismatch, Store, WalkIncomplete
    15	
    16	
    17	FIXTURE = Path(__file__).parent / "fixtures" / "mini-repo"
    18	
    19	
    20	def _copy_fixture(tmp_path: Path) -> Path:
    21	    root = tmp_path / "mini-repo"
    22	    shutil.copytree(FIXTURE, root)
    23	    python = root / "app" / "example.py"
    24	    python.write_text(python.read_text(encoding="utf-8") + "\n# OLDTOKEN\n", encoding="utf-8")
    25	    guide = root / "docs" / "guide.md"
    26	    guide.write_text(guide.read_text(encoding="utf-8") + "\nDELETEONLYTOKEN\n", encoding="utf-8")
    27	    return root
    28	
    29	
    30	def test_first_ingest_indexes_fts_and_vectors(tmp_path: Path) -> None:
    31	    embedder = FakeEmbedder()
    32	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
    33	        report = store.ingest("mini", _copy_fixture(tmp_path))
    34	        stats = store.stats()
    35	        assert report.chunks_embedded == report.chunks_written > 0
    36	        assert stats.chunks == stats.chunks_fts == stats.chunks_vec
    37	        assert store.fts_match("OLDTOKEN")
    38	
    39	
    40	def test_second_ingest_is_a_true_file_sha_short_circuit(tmp_path: Path) -> None:
    41	    root = _copy_fixture(tmp_path)
    42	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
    43	        store.ingest("mini", root)
    44	        embedder = FakeEmbedder()
    45	        store.embedder = embedder
    46	        report = store.ingest("mini", root)
    47	        assert report.files_skipped == report.files_seen
    48	        assert report.files_reingested == 0
    49	        assert report.chunks_written == 0
    50	        assert embedder.call_count == 0
    51	        assert report.seconds < 1.0
    52	
    53	
    54	def test_changed_file_reuses_unchanged_chunk_vectors_and_refreshes_fts(tmp_path: Path) -> None:
    55	    root = _copy_fixture(tmp_path)
    56	    embedder = FakeEmbedder()
    57	    with Store.open(tmp_path / "index.sqlite", embedder) as store:
    58	        store.ingest("mini", root)
    59	        source = root / "app" / "example.py"
    60	        source.write_text(
    61	            source.read_text(encoding="utf-8").replace("OLDTOKEN", "NEWTOKEN"),
    62	            encoding="utf-8",
    63	        )
    64	        embedder.document_calls = embedder.documents_encoded = 0
    65	        report = store.ingest("mini", root)
    66	        assert report.files_reingested == 1
    67	        assert report.cache_hits > 0
    68	        assert embedder.document_calls == 1
    69	        assert embedder.documents_encoded == 1
    70	        assert store.fts_match("NEWTOKEN")
    71	        assert store.fts_match("OLDTOKEN") == []
    72	
    73	
    74	def test_deleted_file_is_pruned_from_all_indexes(tmp_path: Path) -> None:
    75	    root = _copy_fixture(tmp_path)
    76	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
    77	        store.ingest("mini", root)
    78	        before = store.stats()
    79	        (root / "docs" / "guide.md").unlink()
    80	        report = store.ingest("mini", root)
    81	        after = store.stats()
    82	        assert report.files_pruned == 1
    83	        assert after.files == before.files - 1
    84	        assert after.chunks == after.chunks_fts == after.chunks_vec
    85	        assert after.chunks < before.chunks
    86	        assert store.fts_match("DELETEONLYTOKEN") == []
    87	
    88	
    89	def test_prefix_scoped_ingest_does_not_prune_outside_scope(tmp_path: Path) -> None:
    90	    root = _copy_fixture(tmp_path)
    91	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
    92	        store.ingest("mini", root)
    93	        (root / "docs" / "guide.md").unlink()
    94	        report = store.ingest("mini", root, include_prefixes=("app",))
    95	        assert report.files_pruned == 0
    96	        assert store.fts_match("DELETEONLYTOKEN")
    97	
    98	
    99	def test_empty_corpus_does_not_write(tmp_path: Path) -> None:
   100	    root = tmp_path / "empty"
   101	    root.mkdir()
   102	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
   103	        with pytest.raises(EmptyCorpus):
   104	            store.ingest("mini", root)
   105	        assert store.stats().files == store.stats().chunks == 0
   106	
   107	
   108	def test_incomplete_walk_preserves_every_existing_index(
   109	    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
   110	) -> None:
   111	    root = _copy_fixture(tmp_path)
   112	    blocked = root / "docs"
   113	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
   114	        store.ingest("mini", root)
   115	        before = store.stats()
   116	        token_ids = store.fts_match("DELETEONLYTOKEN")
   117	        real_scandir = os.scandir
   118	
   119	        def guarded_scandir(path: str | os.PathLike[str]):
   120	            if Path(path) == blocked:
   121	                raise PermissionError("blocked for test")
   122	            return real_scandir(path)
   123	
   124	        monkeypatch.setattr(os, "scandir", guarded_scandir)
   125	        with pytest.raises(WalkIncomplete, match="docs"):
   126	            store.ingest("mini", root)
   127	        assert store.stats() == before
   128	        assert store.fts_match("DELETEONLYTOKEN") == token_ids
   129	
   130	
   131	@pytest.mark.parametrize(
   132	    ("changed", "value"),
   133	    (("model_id", "other"), ("dim", 12), ("provider", "other-provider")),
   134	)
   135	def test_open_rejects_each_embedder_identity_mismatch(
   136	    tmp_path: Path, changed: str, value: object
   137	) -> None:
   138	    path = tmp_path / "index.sqlite"
   139	    Store.open(path, FakeEmbedder()).close()
   140	    kwargs = {"model_id": "fake", "dim": 8, "provider": "fake"}
   141	    kwargs[changed] = value
   142	    with pytest.raises(IndexMismatch, match={"model_id": "model"}.get(changed, changed)):
   143	        Store.open(path, FakeEmbedder(**kwargs))
   144	
   145	
   146	def test_chunk_vector_matches_provider_keyed_cache(tmp_path: Path) -> None:
   147	    with Store.open(tmp_path / "index.sqlite", FakeEmbedder()) as store:
   148	        store.ingest("mini", _copy_fixture(tmp_path))
   149	        chunk_vector, cache_vector = store.connection.execute(
   150	            """
   151	            SELECT v.embedding, c.vector
   152	            FROM chunks AS ch
   153	            JOIN chunks_vec AS v ON v.rowid = ch.id
   154	            JOIN embed_cache AS c
   155	              ON c.content_sha = ch.content_sha
   156	             AND c.model = ? AND c.dim = ? AND c.provider = ?
   157	            LIMIT 1
   158	            """,
   159	            ("fake", 8, "fake"),
   160	        ).fetchone()
   161	        assert np.array_equal(
   162	            np.frombuffer(chunk_vector, dtype=np.float32),
   163	            np.frombuffer(cache_vector, dtype=np.float32),
   164	        )
   165	
   166	
   167	def test_coderank_embedder_sets_guard_and_prefixes_queries_only(
   168	    monkeypatch: pytest.MonkeyPatch,
   169	) -> None:
   170	    calls: list[list[str]] = []
   171	
   172	    class StubModel:
   173	        max_seq_length = 99
   174	
   175	        def encode(self, texts: list[str], **_kwargs: object) -> np.ndarray:
   176	            calls.append(texts)
   177	            vectors = np.zeros((len(texts), 768), dtype=np.float32)
   178	            vectors[:, 0] = 1.0
   179	            return vectors
   180	
   181	    model = StubModel()
   182	    monkeypatch.setenv("EMBED_MAX_THREADS", "1")
   183	    embedder = CodeRankEmbedder(model_factory=lambda *_args, **_kwargs: model, device="cpu")
   184	    embedder.encode_documents(["raw document"])
   185	    query = embedder.encode_query("sort a list")
   186	    assert model.max_seq_length == 2048
   187	    assert calls == [["raw document"], [QUERY_PREFIX + "sort a list"]]
   188	    assert query.shape == (768,)
   189	    assert np.linalg.norm(query) == pytest.approx(1.0)
     1	from __future__ import annotations
     2	
     3	import json
     4	
     5	import pytest
     6	
     7	from xyz.eval.metrics import score
     8	
     9	
    10	def test_score_three_queries() -> None:
    11	    queries = [
    12	        {"q": "one", "relevant": ["a.py"]},
    13	        {"q": "two", "relevant": ["b.py"]},
    14	        {"q": "miss", "relevant": ["z.py"]},
    15	    ]
    16	    report = score(
    17	        {
    18	            "one": [(1, "a.py"), (2, "x.py")],
    19	            "two": [(3, "x.py"), (4, "b.py")],
    20	            "miss": [(5, "x.py")],
    21	        },
    22	        queries,
    23	        10,
    24	    ).to_dict()
    25	    assert report["mrr"] == 0.5
    26	    assert report["recall@1"] == pytest.approx(1 / 3, abs=0.0001)
    27	    assert report["recall@3"] == pytest.approx(2 / 3, abs=0.0001)
    28	    assert report["never_found"] == 1
    29	
    30	
    31	def test_rank_eleven_flips_at_depth() -> None:
    32	    queries = [{"q": "q", "relevant": ["hit.py"]}]
    33	    ranking = [(i, f"p{i}.py") for i in range(1, 11)] + [(11, "hit.py")]
    34	    shallow = score({"q": ranking}, queries, 10)
    35	    deep = score({"q": ranking}, queries, 100)
    36	    assert shallow.mrr == 0 and shallow.never_found == 1
    37	    assert deep.mrr == pytest.approx(1 / 11, abs=0.0001) and deep.never_found == 0
    38	
    39	
    40	def test_same_path_chunk_ids_survive_json_round_trip(tmp_path) -> None:
    41	    report = score(
    42	        {"q": [(41, "same.py"), (42, "same.py")]},
    43	        [{"q": "q", "relevant": ["same.py"]}],
    44	        10,
    45	    )
    46	    path = tmp_path / "report.json"
    47	    report.write_json(path)
    48	    ranking = json.loads(path.read_text())["per_query"][0]["ranking"]
    49	    assert ranking == [
    50	        {"chunk_id": 41, "path": "same.py"},
    51	        {"chunk_id": 42, "path": "same.py"},
    52	    ]
     1	"""Smoke tests for the initial package scaffold."""
     2	
     3	import xyz
     4	from xyz.cli import main
     5	
     6	
     7	def test_version() -> None:
     8	    assert xyz.__version__ == "0.5.0.dev0"
     9	
    10	
    11	def test_cli_without_arguments(capsys: object) -> None:
    12	    assert main([]) == 0
    13	
    14	
    15	def test_cli_version(capsys: object) -> None:
    16	    assert main(["--version"]) == 0
    17	
    18	
    19	def test_cli_unknown_subcommand(capsys: object) -> None:
    20	    assert main(["bogus"]) == 2
     1	from __future__ import annotations
     2	
     3	import json
     4	from pathlib import Path
     5	
     6	import pytest
     7	
     8	from tests.fakes import FakeEmbedder, FakeReranker
     9	from xyz.cli import main
    10	
    11	
    12	@pytest.fixture
    13	def fake_models(monkeypatch: pytest.MonkeyPatch) -> None:
    14	    import xyz.cli as cli
    15	
    16	    monkeypatch.setattr(cli, "_make_embedder", FakeEmbedder)
    17	    monkeypatch.setattr(cli, "_make_reranker", lambda: FakeReranker(default=0.0))
    18	
    19	
    20	def _repo(tmp_path: Path) -> Path:
    21	    root = tmp_path / "repo"
    22	    root.mkdir()
    23	    (root / "alpha.py").write_text(
    24	        "def alpha():\n    return 'alpha'\n\n"
    25	        "def alpha_helper():\n    return 'helper'\n"
    26	    )
    27	    (root / "beta.py").write_text("def beta():\n    return 'beta'\n")
    28	    return root
    29	
    30	
    31	def test_ingest_query_eval_end_to_end_and_dedupe(
    32	    tmp_path: Path, fake_models: None, capsys: pytest.CaptureFixture[str]
    33	) -> None:
    34	    root = _repo(tmp_path)
    35	    db = tmp_path / "index.sqlite"
    36	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    37	    first = json.loads(capsys.readouterr().out)
    38	    assert first["ingest"]["chunks_embedded"] > 0
    39	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    40	    second = json.loads(capsys.readouterr().out)
    41	    assert second["ingest"]["chunks_embedded"] == 0
    42	
    43	    assert main(["query", "--db", str(db), "--mode", "dense", "alpha"]) == 0
    44	    assert "timings_ms" in capsys.readouterr().out
    45	
    46	    queries = tmp_path / "queries.json"
    47	    queries.write_text(json.dumps({"queries": [{"q": "alpha", "relevant": ["alpha.py"]}]}))
    48	    out = tmp_path / "eval.json"
    49	    assert main(
    50	        [
    51	            "eval", "--db", str(db), "--queries", str(queries),
    52	            "--modes", "dense,bm25,hybrid,hybrid+rerank",
    53	            "--depth", "100", "--out", str(out),
    54	        ]
    55	    ) == 0
    56	    payload = json.loads(out.read_text())
    57	    assert set(payload["reports"]) == {"dense", "bm25", "hybrid", "hybrid+rerank"}
    58	    assert payload["corpus"]["chunk_count"] > 0
    59	    assert "reorder_count" in payload
    60	
    61	
    62	def test_eval_counts_chunk_id_reorder(
    63	    tmp_path: Path, fake_models: None, monkeypatch: pytest.MonkeyPatch
    64	) -> None:
    65	    import xyz.retrieve.pipeline as pipeline
    66	    from xyz.retrieve.models import Hit
    67	
    68	    root = _repo(tmp_path)
    69	    db = tmp_path / "index.sqlite"
    70	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    71	    # Chunk ids 1 and 2 are distinct functions from the same alpha.py path.
    72	    monkeypatch.setattr(
    73	        pipeline,
    74	        "dense_search",
    75	        lambda *_args: [Hit(1, 2.0, "dense"), Hit(2, 1.0, "dense")],
    76	    )
    77	    monkeypatch.setattr(
    78	        pipeline,
    79	        "bm25_search",
    80	        lambda *_args: [Hit(1, 2.0, "bm25"), Hit(2, 1.0, "bm25")],
    81	    )
    82	    import xyz.cli as cli
    83	
    84	    class SwapReranker:
    85	        def score(self, query: str, texts: list[str]) -> list[float]:
    86	            del query
    87	            return [float(index) for index, _text in enumerate(texts)]
    88	
    89	    monkeypatch.setattr(cli, "_make_reranker", SwapReranker)
    90	    queries = tmp_path / "queries.json"
    91	    queries.write_text(json.dumps([{"q": "alpha", "relevant": ["alpha.py"]}]))
    92	    out = tmp_path / "eval.json"
    93	    assert main(
    94	        [
    95	            "eval", "--db", str(db), "--queries", str(queries),
    96	            "--modes", "hybrid,hybrid+rerank", "--out", str(out),
    97	        ]
    98	    ) == 0
    99	    assert json.loads(out.read_text())["reorder_count"] == 1
   100	
   101	
   102	@pytest.mark.parametrize("payload", ([], {"queries": []}))
   103	def test_empty_query_file_exits_two(
   104	    tmp_path: Path, fake_models: None, payload: object
   105	) -> None:
   106	    path = tmp_path / "queries.json"
   107	    path.write_text(json.dumps(payload))
   108	    assert main(
   109	        [
   110	            "eval", "--db", str(tmp_path / "x.sqlite"), "--queries", str(path),
   111	            "--out", str(tmp_path / "out.json"),
   112	        ]
   113	    ) == 2
   114	
   115	
   116	def test_missing_gold_path_exits_two(tmp_path: Path, fake_models: None) -> None:
   117	    root = _repo(tmp_path)
   118	    db = tmp_path / "index.sqlite"
   119	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
   120	    queries = tmp_path / "queries.json"
   121	    queries.write_text(json.dumps([{"q": "missing", "relevant": ["absent.py"]}]))
   122	    assert main(
   123	        [
   124	            "eval", "--db", str(db), "--queries", str(queries),
   125	            "--out", str(tmp_path / "out.json"),
   126	        ]
   127	    ) == 2
   128	
   129	
   130	def test_bogus_ingest_path_exits_two(tmp_path: Path, fake_models: None) -> None:
   131	    assert main(
   132	        [
   133	            "ingest", "--db", str(tmp_path / "x.sqlite"), "--repo", "fixture",
   134	            str(tmp_path / "missing"),
   135	        ]
   136	    ) == 2
     1	"""Deterministic test doubles shared by index and retrieval tests."""
     2	
     3	from __future__ import annotations
     4	
     5	import hashlib
     6	from collections.abc import Sequence
     7	
     8	import numpy as np
     9	
    10	
    11	class FakeEmbedder:
    12	    provider = "fake"
    13	
    14	    def __init__(self, model_id: str = "fake", dim: int = 8, provider: str = "fake") -> None:
    15	        self.model_id = model_id
    16	        self.dim = dim
    17	        self.provider = provider
    18	        self.document_calls = 0
    19	        self.query_calls = 0
    20	        self.documents_encoded = 0
    21	
    22	    @property
    23	    def call_count(self) -> int:
    24	        return self.document_calls + self.query_calls
    25	
    26	    def _vector(self, text: str) -> np.ndarray:
    27	        values: list[float] = []
    28	        counter = 0
    29	        while len(values) < self.dim:
    30	            digest = hashlib.sha256(f"{counter}:{text}".encode()).digest()
    31	            values.extend((byte - 127.5) / 127.5 for byte in digest)
    32	            counter += 1
    33	        vector = np.asarray(values[: self.dim], dtype=np.float32)
    34	        return vector / np.linalg.norm(vector)
    35	
    36	    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
    37	        self.document_calls += 1
    38	        self.documents_encoded += len(texts)
    39	        return np.stack([self._vector(text) for text in texts]).astype(np.float32)
    40	
    41	    def encode_query(self, text: str) -> np.ndarray:
    42	        self.query_calls += 1
    43	        return self._vector(text)
    44	
    45	
    46	class FakeReranker:
    47	    """Return deterministic scores keyed by exact chunk text."""
    48	
    49	    def __init__(self, scores: dict[str, float] | None = None, default: float = 0.0) -> None:
    50	        self.scores = scores or {}
    51	        self.default = default
    52	
    53	    def score(self, query: str, texts: Sequence[str]) -> list[float]:
    54	        del query
    55	        return [float(self.scores.get(text, self.default)) for text in texts]
tests/test_retrieve.py:12:from xyz.retrieve.dense import KNN_SQL, dense_search
tests/test_retrieve.py:13:from xyz.retrieve.fuse import rrf
tests/test_retrieve.py:15:from xyz.retrieve.lexical import bm25_search
tests/test_retrieve.py:20:def _add_chunks(store: Store, count: int, *, same_path: bool = False) -> None:
tests/test_retrieve.py:23:        for chunk_id in range(1, count + 1):
tests/test_retrieve.py:24:            path = "same.py" if same_path else f"p{chunk_id}.py"
tests/test_retrieve.py:27:                INSERT INTO chunks(
tests/test_retrieve.py:32:                (chunk_id, path, f"f{chunk_id}", f"sha{chunk_id}", f"text {chunk_id}", f"embedded {chunk_id}"),
tests/test_retrieve.py:35:                "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)", (chunk_id, vector)
tests/test_retrieve.py:39:def test_rrf_matches_hand_computed_overlap_and_tie_break() -> None:
tests/test_retrieve.py:42:    fused = rrf([left, right], k=60)
tests/test_retrieve.py:43:    assert [hit.chunk_id for hit in fused] == [3, 1, 2, 4, 5]
tests/test_retrieve.py:49:def test_knn_sql_uses_bound_k_and_dense_query_executes(tmp_path: Path) -> None:
tests/test_retrieve.py:50:    assert " k = ?" in KNN_SQL
tests/test_retrieve.py:51:    assert "LIMIT ?" not in KNN_SQL.upper()
tests/test_retrieve.py:54:        _add_chunks(store, 2)
tests/test_retrieve.py:55:        assert len(dense_search(store, embedder.encode_query("needle"), 1)) == 1
tests/test_retrieve.py:58:def test_bm25_sanitises_operators_empty_and_keeps_higher_better(tmp_path: Path) -> None:
tests/test_retrieve.py:60:        _add_chunks(store, 2)
tests/test_retrieve.py:63:                "UPDATE chunks SET embedded_text = 'foo bar foo' WHERE id = 1"
tests/test_retrieve.py:66:                "UPDATE chunks SET embedded_text = 'foo' WHERE id = 2"
tests/test_retrieve.py:68:        assert bm25_search(store, "foo-bar: baz*", 10)
tests/test_retrieve.py:69:        assert bm25_search(store, "", 10) == []
tests/test_retrieve.py:70:        assert bm25_search(store, "the and", 10) == []
tests/test_retrieve.py:71:        hits = bm25_search(store, "foo bar", 10)
tests/test_retrieve.py:72:        assert hits[0].chunk_id == 1
tests/test_retrieve.py:76:def test_rerank_reorders_rrf_and_tau_is_query_level(
tests/test_retrieve.py:83:        _add_chunks(store, 3)
tests/test_retrieve.py:85:        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
tests/test_retrieve.py:86:        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
tests/test_retrieve.py:87:        reranker = FakeReranker({"embedded 1": 2.0, "embedded 2": 0.0, "embedded 3": 3.0})
tests/test_retrieve.py:88:        retriever = Retriever(store, embedder, reranker)
tests/test_retrieve.py:90:        assert retriever.search("q", mode="hybrid").ranking[0][0] == 1
tests/test_retrieve.py:91:        reranked = retriever.search("q", k=3, mode="hybrid+rerank", tau=1.0)
tests/test_retrieve.py:92:        assert [chunk_id for chunk_id, _path in reranked.ranking] == [3, 1, 2]
tests/test_retrieve.py:93:        assert not reranked.no_answer
tests/test_retrieve.py:94:        assert len(reranked.hits) == 3
tests/test_retrieve.py:95:        assert reranked.hits[-1].score < 1.0
tests/test_retrieve.py:99:        ).search("q", mode="hybrid+rerank", tau=0.5)
tests/test_retrieve.py:100:        assert rejected.no_answer and rejected.hits == [] and rejected.ranking
tests/test_retrieve.py:103:def test_candidate_depth_rerank_cap_and_same_path_identity(
tests/test_retrieve.py:110:        _add_chunks(store, 120, same_path=True)
tests/test_retrieve.py:111:        lane = [Hit(chunk_id, 121 - chunk_id, "lane") for chunk_id in range(1, 121)]
tests/test_retrieve.py:112:        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
tests/test_retrieve.py:113:        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
tests/test_retrieve.py:114:        scores = {f"embedded {chunk_id}": float(51 - chunk_id) for chunk_id in range(1, 51)}
tests/test_retrieve.py:118:        reranked = retriever.search("q", fetch_k=100, mode="hybrid+rerank")
tests/test_retrieve.py:119:        assert len(reranked.ranking) == 100
tests/test_retrieve.py:120:        assert reranked.ranking[74][0] == 75
tests/test_retrieve.py:121:        assert 75 not in {chunk_id for chunk_id, _path in retriever.search(
tests/test_retrieve.py:122:            "q", fetch_k=50, mode="hybrid+rerank"
tests/test_retrieve.py:123:        ).ranking}
tests/test_retrieve.py:124:        assert hybrid.ranking != reranked.ranking
tests/test_retrieve.py:125:        assert [path for _chunk_id, path in hybrid.ranking] == [
tests/test_retrieve.py:126:            path for _chunk_id, path in reranked.ranking
tests/test_retrieve.py:147:        _add_chunks(store, 1)
tests/test_retrieve.py:149:        monkeypatch.setattr(pipeline, "dense_search", lambda *_args: lane)
tests/test_retrieve.py:150:        monkeypatch.setattr(pipeline, "bm25_search", lambda *_args: lane)
tests/test_retrieve.py:154:            plain.search("q", mode="hybrid+rerank")
tests/test_retrieve.py:155:        assert not plain.search("q", mode="dense", tau=None).no_answer
tests/test_retrieve.py:156:        assert plain.search("q", mode="bm25", tau=2.0).no_answer
tests/test_retrieve.py:158:        reranked = Retriever(store, embedder, FakeReranker({"embedded 1": 1.0}))
tests/test_retrieve.py:161:            result = reranked.search("q", mode="auto")
tests/test_retrieve.py:162:            assert result.mode == "hybrid+rerank"
tests/test_retrieve.py:164:                "embed_query", "bm25", "dense", "fuse", "rerank", "total"
xyz/retrieve/pipeline.py:1:"""Instrumented dense, lexical, hybrid, and reranked retrieval pipeline."""
xyz/retrieve/pipeline.py:10:from xyz.retrieve.dense import dense_search
xyz/retrieve/pipeline.py:11:from xyz.retrieve.fuse import rrf
xyz/retrieve/pipeline.py:12:from xyz.retrieve.lexical import bm25_search
xyz/retrieve/pipeline.py:14:from xyz.retrieve.rerank import Reranker
xyz/retrieve/pipeline.py:17:TIMING_STAGES = ("embed_query", "bm25", "dense", "fuse", "rerank", "total")
xyz/retrieve/pipeline.py:18:MODES = frozenset({"auto", "dense", "bm25", "hybrid", "hybrid+rerank"})
xyz/retrieve/pipeline.py:22:    def __init__(self, store: Store, embedder: Embedder, reranker: Reranker | None = None) -> None:
xyz/retrieve/pipeline.py:26:        self.reranker = reranker
xyz/retrieve/pipeline.py:39:            FROM chunks WHERE id IN ({placeholders})
xyz/retrieve/pipeline.py:51:        tau: float | None = None,
xyz/retrieve/pipeline.py:57:        resolved = ("hybrid+rerank" if self.reranker is not None else "hybrid") if mode == "auto" else mode
xyz/retrieve/pipeline.py:58:        if resolved == "hybrid+rerank" and self.reranker is None:
xyz/retrieve/pipeline.py:59:            raise ValueError("hybrid+rerank mode requires a reranker")
xyz/retrieve/pipeline.py:63:        dense_hits: list[Hit] = []
xyz/retrieve/pipeline.py:66:        if resolved in {"dense", "hybrid", "hybrid+rerank"}:
xyz/retrieve/pipeline.py:71:            dense_hits = dense_search(self.store, query_vec, fetch_k)
xyz/retrieve/pipeline.py:72:            timings["dense"] = self._elapsed(started)
xyz/retrieve/pipeline.py:73:        if resolved in {"bm25", "hybrid", "hybrid+rerank"}:
xyz/retrieve/pipeline.py:75:            lexical_hits = bm25_search(self.store, query, fetch_k)
xyz/retrieve/pipeline.py:76:            timings["bm25"] = self._elapsed(started)
xyz/retrieve/pipeline.py:78:        if resolved == "dense":
xyz/retrieve/pipeline.py:79:            candidates = dense_hits[:fetch_k]
xyz/retrieve/pipeline.py:80:        elif resolved == "bm25":
xyz/retrieve/pipeline.py:84:            candidates = rrf([dense_hits, lexical_hits])[:fetch_k]
xyz/retrieve/pipeline.py:87:        if resolved == "hybrid+rerank" and candidates:
xyz/retrieve/pipeline.py:88:            rerank_count = min(len(candidates), 50)
xyz/retrieve/pipeline.py:89:            head = candidates[:rerank_count]
xyz/retrieve/pipeline.py:90:            rows = self._chunk_rows([hit.chunk_id for hit in head])
xyz/retrieve/pipeline.py:91:            texts = [str(rows[hit.chunk_id][7]) for hit in head]
xyz/retrieve/pipeline.py:93:            scores = self.reranker.score(query, texts)  # type: ignore[union-attr]
xyz/retrieve/pipeline.py:94:            timings["rerank"] = self._elapsed(started)
xyz/retrieve/pipeline.py:96:                raise ValueError(f"reranker returned {len(scores)} scores for {len(head)} candidates")
xyz/retrieve/pipeline.py:98:                Hit(hit.chunk_id, float(score), "rerank")
xyz/retrieve/pipeline.py:101:            candidates = sorted(rescored, key=lambda hit: (-hit.score, hit.chunk_id)) + candidates[rerank_count:]
xyz/retrieve/pipeline.py:103:        rows = self._chunk_rows([hit.chunk_id for hit in candidates])
xyz/retrieve/pipeline.py:104:        ranking = [(hit.chunk_id, str(rows[hit.chunk_id][1])) for hit in candidates]
xyz/retrieve/pipeline.py:106:        no_answer = top_score is None or (tau is not None and top_score < tau)
xyz/retrieve/pipeline.py:108:        if not no_answer:
xyz/retrieve/pipeline.py:110:                repo, path, kind, name, start_line, end_line, text, embedded_text = rows[hit.chunk_id]
xyz/retrieve/pipeline.py:113:                        hit.chunk_id, str(repo), str(path), str(kind), str(name),
xyz/retrieve/pipeline.py:119:        return SearchResult(materialised, ranking, no_answer, timings, resolved)
xyz/index/store.py:36:class WalkIncomplete(StoreError):
xyz/index/store.py:50:    chunks_written: int
xyz/index/store.py:51:    chunks_embedded: int
xyz/index/store.py:59:    chunks: int
xyz/index/store.py:60:    chunks_fts: int
xyz/index/store.py:61:    chunks_vec: int
xyz/index/store.py:138:                CREATE TABLE IF NOT EXISTS chunks(
xyz/index/store.py:150:                CREATE INDEX IF NOT EXISTS chunks_repo_path ON chunks(repo, path);
xyz/index/store.py:151:                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
xyz/index/store.py:155:                    content='chunks',
xyz/index/store.py:158:                CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
xyz/index/store.py:159:                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
xyz/index/store.py:162:                CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
xyz/index/store.py:163:                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
xyz/index/store.py:166:                CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
xyz/index/store.py:167:                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
xyz/index/store.py:169:                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
xyz/index/store.py:172:                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
xyz/index/store.py:219:    def _snapshot_chunks(
xyz/index/store.py:232:                by_path[path] = result.chunks
xyz/index/store.py:243:            raise WalkIncomplete(walk_errors)
xyz/index/store.py:245:        for chunk in result.chunks:
xyz/index/store.py:263:            raise WalkIncomplete(errors)
xyz/index/store.py:267:        chunks_by_path, warnings = self._snapshot_chunks(
xyz/index/store.py:277:        candidate_chunks = sum(
xyz/index/store.py:278:            len(chunks_by_path.get(path, ()))
xyz/index/store.py:285:        chunks_written = 0
xyz/index/store.py:286:        chunks_embedded = 0
xyz/index/store.py:294:            chunks = chunks_by_path.get(path, [])
xyz/index/store.py:297:            for chunk in chunks:
xyz/index/store.py:335:                        "SELECT id FROM chunks WHERE repo = ? AND path = ?", (repo, path)
xyz/index/store.py:339:                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in old_ids)
xyz/index/store.py:342:                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
xyz/index/store.py:359:                for chunk in chunks:
xyz/index/store.py:362:                        INSERT INTO chunks(
xyz/index/store.py:380:                        "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)",
xyz/index/store.py:392:                    (repo, path, file_shas[path], len(chunks)),
xyz/index/store.py:395:            chunks_written += len(chunks)
xyz/index/store.py:396:            chunks_embedded += len(missing)
xyz/index/store.py:398:                progress(chunks_embedded, candidate_chunks, time.monotonic() - started)
xyz/index/store.py:412:                        "SELECT id FROM chunks WHERE repo = ? AND path = ?", (repo, path)
xyz/index/store.py:416:                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in ids)
xyz/index/store.py:419:                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
xyz/index/store.py:430:            chunks_written=chunks_written,
xyz/index/store.py:431:            chunks_embedded=chunks_embedded,
xyz/index/store.py:442:            chunks=count("chunks"),
xyz/index/store.py:443:            chunks_fts=count("chunks_fts"),
xyz/index/store.py:444:            chunks_vec=count("chunks_vec"),
xyz/index/store.py:453:                "SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?",
xyz/retrieve/fuse.py:10:def rrf(rankings: Sequence[Sequence[Hit]], k: int = 60) -> list[Hit]:
xyz/retrieve/fuse.py:11:    """Fuse rankings using one-based ranks and deterministic chunk-id ties."""
xyz/retrieve/fuse.py:16:    for ranking in rankings:
xyz/retrieve/fuse.py:18:        for rank, hit in enumerate(ranking, start=1):
xyz/retrieve/fuse.py:19:            if hit.chunk_id in seen:
xyz/retrieve/fuse.py:21:            seen.add(hit.chunk_id)
xyz/retrieve/fuse.py:22:            scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (k + rank)
xyz/retrieve/fuse.py:23:    hits = [Hit(chunk_id, score, "rrf") for chunk_id, score in scores.items()]
xyz/retrieve/fuse.py:24:    return sorted(hits, key=lambda hit: (-hit.score, hit.chunk_id))
xyz/retrieve/dense.py:14:KNN_SQL = """
xyz/retrieve/dense.py:16:FROM chunks_vec
xyz/retrieve/dense.py:17:WHERE embedding MATCH ? AND k = ?
xyz/retrieve/dense.py:22:def dense_search(store: Store, query_vec: Sequence[float] | np.ndarray, k: int) -> list[Hit]:
xyz/retrieve/dense.py:33:    rows = store.connection.execute(KNN_SQL, (encoded, k))
xyz/retrieve/dense.py:34:    return [Hit(int(chunk_id), -float(distance), "dense") for chunk_id, distance in rows]
tests/test_cli.py:17:    monkeypatch.setattr(cli, "_make_reranker", lambda: FakeReranker(default=0.0))
tests/test_cli.py:38:    assert first["ingest"]["chunks_embedded"] > 0
tests/test_cli.py:41:    assert second["ingest"]["chunks_embedded"] == 0
tests/test_cli.py:43:    assert main(["query", "--db", str(db), "--mode", "dense", "alpha"]) == 0
tests/test_cli.py:52:            "--modes", "dense,bm25,hybrid,hybrid+rerank",
tests/test_cli.py:57:    assert set(payload["reports"]) == {"dense", "bm25", "hybrid", "hybrid+rerank"}
tests/test_cli.py:62:def test_eval_counts_chunk_id_reorder(
tests/test_cli.py:74:        "dense_search",
tests/test_cli.py:75:        lambda *_args: [Hit(1, 2.0, "dense"), Hit(2, 1.0, "dense")],
tests/test_cli.py:79:        "bm25_search",
tests/test_cli.py:80:        lambda *_args: [Hit(1, 2.0, "bm25"), Hit(2, 1.0, "bm25")],
tests/test_cli.py:89:    monkeypatch.setattr(cli, "_make_reranker", SwapReranker)
tests/test_cli.py:96:            "--modes", "hybrid,hybrid+rerank", "--out", str(out),
tests/test_metrics.py:33:    ranking = [(i, f"p{i}.py") for i in range(1, 11)] + [(11, "hit.py")]
tests/test_metrics.py:34:    shallow = score({"q": ranking}, queries, 10)
tests/test_metrics.py:35:    deep = score({"q": ranking}, queries, 100)
tests/test_metrics.py:40:def test_same_path_chunk_ids_survive_json_round_trip(tmp_path) -> None:
tests/test_metrics.py:48:    ranking = json.loads(path.read_text())["per_query"][0]["ranking"]
tests/test_metrics.py:49:    assert ranking == [
tests/test_metrics.py:50:        {"chunk_id": 41, "path": "same.py"},
tests/test_metrics.py:51:        {"chunk_id": 42, "path": "same.py"},
xyz/eval/metrics.py:40:    rankings: Mapping[str, Ranking],
xyz/eval/metrics.py:44:    """Score ordered chunk rankings against path-level relevance at ``depth``."""
xyz/eval/metrics.py:55:        ordered = list(rankings.get(text, ()))[:depth]
xyz/eval/metrics.py:60:                for position, (_chunk_id, path) in enumerate(ordered, start=1)
xyz/eval/metrics.py:72:                "ranking": [
xyz/eval/metrics.py:73:                    {"chunk_id": int(chunk_id), "path": str(path)}
xyz/eval/metrics.py:74:                    for chunk_id, path in ordered
tests/test_chunkers.py:56:def test_python_chunks_and_lines() -> None:
tests/test_chunkers.py:59:    by_name = {chunk.qualified_name: chunk for chunk in result.chunks}
tests/test_chunkers.py:71:def test_typescript_and_php_chunks() -> None:
tests/test_chunkers.py:75:    assert {chunk.qualified_name for chunk in ts.chunks} == {"greet", "Greeter", "Greeter.greet"}
tests/test_chunkers.py:76:    assert {chunk.qualified_name for chunk in php.chunks} == {"app/example.php", "Greeter", "Greeter.greet"}
tests/test_chunkers.py:77:    ts_method = next(chunk for chunk in ts.chunks if chunk.qualified_name == "Greeter.greet")
tests/test_chunkers.py:78:    php_method = next(chunk for chunk in php.chunks if chunk.qualified_name == "Greeter.greet")
tests/test_chunkers.py:83:def test_markdown_sections_and_file_chunks() -> None:
tests/test_chunkers.py:85:    assert [chunk.qualified_name for chunk in markdown.chunks] == [
tests/test_chunkers.py:91:    assert [(chunk.start_line, chunk.end_line) for chunk in markdown.chunks] == [
tests/test_chunkers.py:100:    assert len(yaml.chunks) == len(docker.chunks) == 1
tests/test_chunkers.py:101:    assert yaml.chunks[0].kind == docker.chunks[0].kind == "file"
tests/test_chunkers.py:106:    assert result.chunks
tests/test_chunkers.py:107:    for chunk in result.chunks:
tests/test_chunkers.py:114:    single = chunk_file("mini", "long.txt", (root / "long.txt").read_bytes()).chunks
tests/test_chunkers.py:115:    markdown = chunk_file("mini", "docs/long.md", (root / "docs" / "long.md").read_bytes()).chunks
tests/test_chunkers.py:129:    assert len(result.chunks) == 1
tests/test_chunkers.py:130:    assert result.chunks[0].kind == "file"
tests/test_chunkers.py:131:    assert result.chunks[0].qualified_name == "broken.py"
tests/test_store.py:14:from xyz.index.store import EmptyCorpus, IndexMismatch, Store, WalkIncomplete
tests/test_store.py:35:        assert report.chunks_embedded == report.chunks_written > 0
tests/test_store.py:36:        assert stats.chunks == stats.chunks_fts == stats.chunks_vec
tests/test_store.py:49:        assert report.chunks_written == 0
tests/test_store.py:84:        assert after.chunks == after.chunks_fts == after.chunks_vec
tests/test_store.py:85:        assert after.chunks < before.chunks
tests/test_store.py:105:        assert store.stats().files == store.stats().chunks == 0
tests/test_store.py:125:        with pytest.raises(WalkIncomplete, match="docs"):
tests/test_store.py:152:            FROM chunks AS ch
tests/test_store.py:153:            JOIN chunks_vec AS v ON v.rowid = ch.id
xyz/retrieve/lexical.py:37:def bm25_search(store: Store, query: str, k: int) -> list[Hit]:
xyz/retrieve/lexical.py:47:        SELECT rowid, bm25(chunks_fts) AS distance
xyz/retrieve/lexical.py:48:        FROM chunks_fts
xyz/retrieve/lexical.py:49:        WHERE chunks_fts MATCH ?
xyz/retrieve/lexical.py:51:        LIMIT ?
xyz/retrieve/lexical.py:55:    return [Hit(int(chunk_id), -float(distance), "bm25") for chunk_id, distance in rows]

exec
/bin/zsh -lc "nl -ba tests/test_cli.py | sed -n '1,130p'; nl -ba tests/fakes.py; nl -ba tests/test_chunkers.py; rg -n --glob '*.py' \"\\b(?:INSERT|UPDATE|DELETE|REPLACE)\\b.*\\bchunks(?:_fts|_vec)?\\b|\\bchunks(?:_fts|_vec)?\\b.*\\b(?:INSERT|UPDATE|DELETE|REPLACE)\\b\" . --glob '"'!PROJECT/**'"' --glob '"'!relay-system/**'"' --glob '"'!marathon-system/**'"'" in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-22132-rax9y1zy
 succeeded in 0ms:
     1	from __future__ import annotations
     2	
     3	import json
     4	from pathlib import Path
     5	
     6	import pytest
     7	
     8	from tests.fakes import FakeEmbedder, FakeReranker
     9	from xyz.cli import main
    10	
    11	
    12	@pytest.fixture
    13	def fake_models(monkeypatch: pytest.MonkeyPatch) -> None:
    14	    import xyz.cli as cli
    15	
    16	    monkeypatch.setattr(cli, "_make_embedder", FakeEmbedder)
    17	    monkeypatch.setattr(cli, "_make_reranker", lambda: FakeReranker(default=0.0))
    18	
    19	
    20	def _repo(tmp_path: Path) -> Path:
    21	    root = tmp_path / "repo"
    22	    root.mkdir()
    23	    (root / "alpha.py").write_text(
    24	        "def alpha():\n    return 'alpha'\n\n"
    25	        "def alpha_helper():\n    return 'helper'\n"
    26	    )
    27	    (root / "beta.py").write_text("def beta():\n    return 'beta'\n")
    28	    return root
    29	
    30	
    31	def test_ingest_query_eval_end_to_end_and_dedupe(
    32	    tmp_path: Path, fake_models: None, capsys: pytest.CaptureFixture[str]
    33	) -> None:
    34	    root = _repo(tmp_path)
    35	    db = tmp_path / "index.sqlite"
    36	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    37	    first = json.loads(capsys.readouterr().out)
    38	    assert first["ingest"]["chunks_embedded"] > 0
    39	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    40	    second = json.loads(capsys.readouterr().out)
    41	    assert second["ingest"]["chunks_embedded"] == 0
    42	
    43	    assert main(["query", "--db", str(db), "--mode", "dense", "alpha"]) == 0
    44	    assert "timings_ms" in capsys.readouterr().out
    45	
    46	    queries = tmp_path / "queries.json"
    47	    queries.write_text(json.dumps({"queries": [{"q": "alpha", "relevant": ["alpha.py"]}]}))
    48	    out = tmp_path / "eval.json"
    49	    assert main(
    50	        [
    51	            "eval", "--db", str(db), "--queries", str(queries),
    52	            "--modes", "dense,bm25,hybrid,hybrid+rerank",
    53	            "--depth", "100", "--out", str(out),
    54	        ]
    55	    ) == 0
    56	    payload = json.loads(out.read_text())
    57	    assert set(payload["reports"]) == {"dense", "bm25", "hybrid", "hybrid+rerank"}
    58	    assert payload["corpus"]["chunk_count"] > 0
    59	    assert "reorder_count" in payload
    60	
    61	
    62	def test_eval_counts_chunk_id_reorder(
    63	    tmp_path: Path, fake_models: None, monkeypatch: pytest.MonkeyPatch
    64	) -> None:
    65	    import xyz.retrieve.pipeline as pipeline
    66	    from xyz.retrieve.models import Hit
    67	
    68	    root = _repo(tmp_path)
    69	    db = tmp_path / "index.sqlite"
    70	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
    71	    # Chunk ids 1 and 2 are distinct functions from the same alpha.py path.
    72	    monkeypatch.setattr(
    73	        pipeline,
    74	        "dense_search",
    75	        lambda *_args: [Hit(1, 2.0, "dense"), Hit(2, 1.0, "dense")],
    76	    )
    77	    monkeypatch.setattr(
    78	        pipeline,
    79	        "bm25_search",
    80	        lambda *_args: [Hit(1, 2.0, "bm25"), Hit(2, 1.0, "bm25")],
    81	    )
    82	    import xyz.cli as cli
    83	
    84	    class SwapReranker:
    85	        def score(self, query: str, texts: list[str]) -> list[float]:
    86	            del query
    87	            return [float(index) for index, _text in enumerate(texts)]
    88	
    89	    monkeypatch.setattr(cli, "_make_reranker", SwapReranker)
    90	    queries = tmp_path / "queries.json"
    91	    queries.write_text(json.dumps([{"q": "alpha", "relevant": ["alpha.py"]}]))
    92	    out = tmp_path / "eval.json"
    93	    assert main(
    94	        [
    95	            "eval", "--db", str(db), "--queries", str(queries),
    96	            "--modes", "hybrid,hybrid+rerank", "--out", str(out),
    97	        ]
    98	    ) == 0
    99	    assert json.loads(out.read_text())["reorder_count"] == 1
   100	
   101	
   102	@pytest.mark.parametrize("payload", ([], {"queries": []}))
   103	def test_empty_query_file_exits_two(
   104	    tmp_path: Path, fake_models: None, payload: object
   105	) -> None:
   106	    path = tmp_path / "queries.json"
   107	    path.write_text(json.dumps(payload))
   108	    assert main(
   109	        [
   110	            "eval", "--db", str(tmp_path / "x.sqlite"), "--queries", str(path),
   111	            "--out", str(tmp_path / "out.json"),
   112	        ]
   113	    ) == 2
   114	
   115	
   116	def test_missing_gold_path_exits_two(tmp_path: Path, fake_models: None) -> None:
   117	    root = _repo(tmp_path)
   118	    db = tmp_path / "index.sqlite"
   119	    assert main(["ingest", "--db", str(db), "--repo", "fixture", str(root)]) == 0
   120	    queries = tmp_path / "queries.json"
   121	    queries.write_text(json.dumps([{"q": "missing", "relevant": ["absent.py"]}]))
   122	    assert main(
   123	        [
   124	            "eval", "--db", str(db), "--queries", str(queries),
   125	            "--out", str(tmp_path / "out.json"),
   126	        ]
   127	    ) == 2
   128	
   129	
   130	def test_bogus_ingest_path_exits_two(tmp_path: Path, fake_models: None) -> None:
     1	"""Deterministic test doubles shared by index and retrieval tests."""
     2	
     3	from __future__ import annotations
     4	
     5	import hashlib
     6	from collections.abc import Sequence
     7	
     8	import numpy as np
     9	
    10	
    11	class FakeEmbedder:
    12	    provider = "fake"
    13	
    14	    def __init__(self, model_id: str = "fake", dim: int = 8, provider: str = "fake") -> None:
    15	        self.model_id = model_id
    16	        self.dim = dim
    17	        self.provider = provider
    18	        self.document_calls = 0
    19	        self.query_calls = 0
    20	        self.documents_encoded = 0
    21	
    22	    @property
    23	    def call_count(self) -> int:
    24	        return self.document_calls + self.query_calls
    25	
    26	    def _vector(self, text: str) -> np.ndarray:
    27	        values: list[float] = []
    28	        counter = 0
    29	        while len(values) < self.dim:
    30	            digest = hashlib.sha256(f"{counter}:{text}".encode()).digest()
    31	            values.extend((byte - 127.5) / 127.5 for byte in digest)
    32	            counter += 1
    33	        vector = np.asarray(values[: self.dim], dtype=np.float32)
    34	        return vector / np.linalg.norm(vector)
    35	
    36	    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
    37	        self.document_calls += 1
    38	        self.documents_encoded += len(texts)
    39	        return np.stack([self._vector(text) for text in texts]).astype(np.float32)
    40	
    41	    def encode_query(self, text: str) -> np.ndarray:
    42	        self.query_calls += 1
    43	        return self._vector(text)
    44	
    45	
    46	class FakeReranker:
    47	    """Return deterministic scores keyed by exact chunk text."""
    48	
    49	    def __init__(self, scores: dict[str, float] | None = None, default: float = 0.0) -> None:
    50	        self.scores = scores or {}
    51	        self.default = default
    52	
    53	    def score(self, query: str, texts: Sequence[str]) -> list[float]:
    54	        del query
    55	        return [float(self.scores.get(text, self.default)) for text in texts]
     1	"""Contract tests for repository walking and source chunking."""
     2	
     3	from __future__ import annotations
     4	
     5	import os
     6	import shutil
     7	from pathlib import Path
     8	
     9	import pytest
    10	
    11	from xyz.ingest import chunk_file, chunk_repo, walk_repo
    12	
    13	
    14	FIXTURE = Path(__file__).parent / "fixtures" / "mini-repo"
    15	
    16	
    17	def _copy_fixture(tmp_path: Path) -> Path:
    18	    root = tmp_path / "mini-repo"
    19	    shutil.copytree(FIXTURE, root)
    20	    (root / "binary.py").write_bytes(b"print('before nul')\0ignored")
    21	    (root / "long.txt").write_text("x" * 6001, encoding="utf-8")
    22	    (root / "docs" / "long.md").write_text("# Long\n\n" + "word " * 1400, encoding="utf-8")
    23	    return root
    24	
    25	
    26	def test_walk_filters_and_is_deterministic(tmp_path: Path) -> None:
    27	    root = _copy_fixture(tmp_path)
    28	    first_errors: list[str] = []
    29	    second_errors: list[str] = []
    30	    first = list(walk_repo(root, errors=first_errors))
    31	    second = list(walk_repo(root, errors=second_errors))
    32	
    33	    assert first == second
    34	    assert first_errors == second_errors == []
    35	    paths = [path for path, _ in first]
    36	    assert paths == sorted(paths)
    37	    assert "config.yml" in paths
    38	    assert "Dockerfile" in paths
    39	    assert "binary.py" not in paths
    40	    assert "node_modules/ignored.js" not in paths
    41	
    42	
    43	def test_include_prefixes_keep_root_relative_paths(tmp_path: Path) -> None:
    44	    root = _copy_fixture(tmp_path)
    45	    errors: list[str] = []
    46	    paths = [path for path, _ in walk_repo(root, include_prefixes=("app/",), errors=errors)]
    47	    assert paths == ["app/example.php", "app/example.py", "app/example.ts"]
    48	    assert errors == []
    49	
    50	
    51	def test_missing_root_raises(tmp_path: Path) -> None:
    52	    with pytest.raises(ValueError):
    53	        list(walk_repo(tmp_path / "missing", errors=[]))
    54	
    55	
    56	def test_python_chunks_and_lines() -> None:
    57	    path = FIXTURE / "app" / "example.py"
    58	    result = chunk_file("mini", "app/example.py", path.read_bytes())
    59	    by_name = {chunk.qualified_name: chunk for chunk in result.chunks}
    60	
    61	    assert set(by_name) == {"app/example.py", "alpha", "beta", "Worker", "Worker.run", "Worker.stop"}
    62	    assert by_name["alpha"].kind == "function"
    63	    assert (by_name["alpha"].start_line, by_name["alpha"].end_line) == (6, 7)
    64	    assert (by_name["Worker.run"].start_line, by_name["Worker.run"].end_line) == (17, 18)
    65	    assert by_name["app/example.py"].kind == "module"
    66	    assert by_name["app/example.py"].start_line == 1
    67	    assert by_name["app/example.py"].end_line == 3
    68	    assert result.warnings == []
    69	
    70	
    71	def test_typescript_and_php_chunks() -> None:
    72	    ts = chunk_file("mini", "app/example.ts", (FIXTURE / "app" / "example.ts").read_bytes())
    73	    php = chunk_file("mini", "app/example.php", (FIXTURE / "app" / "example.php").read_bytes())
    74	
    75	    assert {chunk.qualified_name for chunk in ts.chunks} == {"greet", "Greeter", "Greeter.greet"}
    76	    assert {chunk.qualified_name for chunk in php.chunks} == {"app/example.php", "Greeter", "Greeter.greet"}
    77	    ts_method = next(chunk for chunk in ts.chunks if chunk.qualified_name == "Greeter.greet")
    78	    php_method = next(chunk for chunk in php.chunks if chunk.qualified_name == "Greeter.greet")
    79	    assert (ts_method.start_line, ts_method.end_line) == (6, 8)
    80	    assert (php_method.start_line, php_method.end_line) == (4, 6)
    81	
    82	
    83	def test_markdown_sections_and_file_chunks() -> None:
    84	    markdown = chunk_file("mini", "docs/guide.md", (FIXTURE / "docs" / "guide.md").read_bytes())
    85	    assert [chunk.qualified_name for chunk in markdown.chunks] == [
    86	        "docs/guide.md",
    87	        "Guide",
    88	        "Guide > Install",
    89	        "Guide > Install > Options",
    90	    ]
    91	    assert [(chunk.start_line, chunk.end_line) for chunk in markdown.chunks] == [
    92	        (1, 1),
    93	        (3, 5),
    94	        (7, 9),
    95	        (11, 13),
    96	    ]
    97	
    98	    yaml = chunk_file("mini", "config.yml", (FIXTURE / "config.yml").read_bytes())
    99	    docker = chunk_file("mini", "Dockerfile", (FIXTURE / "Dockerfile").read_bytes())
   100	    assert len(yaml.chunks) == len(docker.chunks) == 1
   101	    assert yaml.chunks[0].kind == docker.chunks[0].kind == "file"
   102	
   103	
   104	def test_all_embedded_text_is_path_prefixed_and_hashed(tmp_path: Path) -> None:
   105	    result = chunk_repo("mini", _copy_fixture(tmp_path))
   106	    assert result.chunks
   107	    for chunk in result.chunks:
   108	        assert chunk.embedded_text.startswith(chunk.path + "\n\n")
   109	        assert len(chunk.content_sha) == 64
   110	
   111	
   112	def test_oversize_single_line_and_markdown_split(tmp_path: Path) -> None:
   113	    root = _copy_fixture(tmp_path)
   114	    single = chunk_file("mini", "long.txt", (root / "long.txt").read_bytes()).chunks
   115	    markdown = chunk_file("mini", "docs/long.md", (root / "docs" / "long.md").read_bytes()).chunks
   116	
   117	    assert len(single) >= 2
   118	    assert [chunk.qualified_name for chunk in single][:2] == ["long.txt", "long.txt#2"]
   119	    assert len(single[0].text) == 6000
   120	    assert single[0].text[-150:] == single[1].text[:150]
   121	    assert len(markdown) >= 2
   122	    assert [chunk.qualified_name for chunk in markdown][:2] == ["Long", "Long#2"]
   123	    assert all(len(chunk.text) <= 6000 for chunk in single + markdown)
   124	    assert all(chunk.start_line <= chunk.end_line for chunk in single + markdown)
   125	
   126	
   127	def test_broken_parse_falls_back_with_warning() -> None:
   128	    result = chunk_file("mini", "broken.py", (FIXTURE / "broken.py").read_bytes())
   129	    assert len(result.chunks) == 1
   130	    assert result.chunks[0].kind == "file"
   131	    assert result.chunks[0].qualified_name == "broken.py"
   132	    assert len(result.warnings) == 1
   133	    assert "broken.py" in result.warnings[0]
   134	
   135	
   136	def test_scandir_error_is_recorded_after_other_yields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
   137	    root = tmp_path / "repo"
   138	    root.mkdir()
   139	    (root / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
   140	    blocked = root / "blocked"
   141	    blocked.mkdir()
   142	    (blocked / "hidden.py").write_text("VALUE = 2\n", encoding="utf-8")
   143	    (root / "node_modules").mkdir()
   144	    (root / "node_modules" / "ignored.py").write_text("VALUE = 3\n", encoding="utf-8")
   145	    (root / "binary.py").write_bytes(b"ok\0binary")
   146	
   147	    real_scandir = os.scandir
   148	
   149	    def guarded_scandir(path: str | os.PathLike[str]):
   150	        if Path(path) == blocked:
   151	            raise PermissionError("blocked for test")
   152	        return real_scandir(path)
   153	
   154	    monkeypatch.setattr(os, "scandir", guarded_scandir)
   155	    errors: list[str] = []
   156	    iterator = walk_repo(root, errors=errors)
   157	    assert next(iterator)[0] == "a.py"
   158	    assert list(iterator) == []
   159	    assert len(errors) == 1
   160	    assert "blocked" in errors[0]
   161	
   162	
   163	def test_chunk_repo_is_deterministic(tmp_path: Path) -> None:
   164	    root = _copy_fixture(tmp_path)
   165	    assert chunk_repo("mini", root) == chunk_repo("mini", root)
./tests/test_retrieve.py:27:                INSERT INTO chunks(
./tests/test_retrieve.py:35:                "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)", (chunk_id, vector)
./tests/test_retrieve.py:63:                "UPDATE chunks SET embedded_text = 'foo bar foo' WHERE id = 1"
./tests/test_retrieve.py:66:                "UPDATE chunks SET embedded_text = 'foo' WHERE id = 2"
./xyz/index/store.py:158:                CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
./xyz/index/store.py:159:                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:162:                CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
./xyz/index/store.py:163:                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:166:                CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
./xyz/index/store.py:167:                    INSERT INTO chunks_fts(chunks_fts, rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:169:                    INSERT INTO chunks_fts(rowid, embedded_text, qualified_name, path)
./xyz/index/store.py:339:                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in old_ids)
./xyz/index/store.py:342:                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)
./xyz/index/store.py:362:                        INSERT INTO chunks(
./xyz/index/store.py:380:                        "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)",
./xyz/index/store.py:416:                    "DELETE FROM chunks_vec WHERE rowid = ?", ((chunk_id,) for chunk_id in ids)
./xyz/index/store.py:419:                    "DELETE FROM chunks WHERE repo = ? AND path = ?", (repo, path)

codex
The runtime path is wired, not merely asserted: `dense_search()` executes the bound KNN SQL, and the pipeline calls that function. I’m doing one final cross-check of the changed scoped files and their contract tests before issuing the advisory verdict.
exec
/bin/zsh -lc 'git diff --check; git diff -- xyz/index/store.py xyz/retrieve/pipeline.py xyz/retrieve/dense.py xyz/retrieve/lexical.py xyz/retrieve/fuse.py xyz/eval/metrics.py xyz/ingest/walk.py tests; git status --short' in /private/var/folders/69/3l_82qtj7fzglnt_jjg07jh40000gn/T/consult-wt-22132-rax9y1zy
 succeeded in 11365ms:
2026-09-07 10:10:25.290 xcodebuild[99039:32611437]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-07 10:10:25.855 xcodebuild[99039:32611150] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yWsT3TIq' (errno=Operation not permitted)
2026-09-07 10:10:26.806 xcodebuild[5765:32622549]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-07 10:10:27.286 xcodebuild[5765:32622314] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-iyMm6h8b' (errno=Operation not permitted)
2026-09-07 10:10:29.255 xcodebuild[12236:32634494]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-07 10:10:29.631 xcodebuild[12236:32634286] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-XydffGrf' (errno=Operation not permitted)
2026-09-07 10:10:30.468 xcodebuild[15808:32640994]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-07 10:10:30.775 xcodebuild[15808:32640758] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-6S530FuW' (errno=Operation not permitted)
2026-09-07 10:10:32.659 xcodebuild[22443:32653490]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-07 10:10:33.034 xcodebuild[22443:32653092] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sJqHNHlk' (errno=Operation not permitted)
2026-09-07 10:10:33.861 xcodebuild[26172:32660603]  DVTFilePathFSEvents: Failed to start fs event stream.
2026-09-07 10:10:34.205 xcodebuild[26172:32660284] [MT] DVTDeveloperPaths: Failed to get length of DARWIN_USER_CACHE_DIR from confstr(3), error = Error Domain=NSPOSIXErrorDomain Code=5 "Input/output error". Using NSCachesDirectory instead.
?? relay-system/2026-09-06/gh11-act1-final-qa-182025/
?? relay-system/2026-09-07/gh11-act1-qa-round2-100922/

codex
VERDICT: PASS

- [Pass] Production index mutation is centralized in `Store`: schema/FTS triggers and chunk/vector inserts/deletes are in `xyz/index/store.py:151-174,331-392,407-423`. The only other writes found are test fixture setup, not an alternate index path (`tests/test_retrieve.py:20-36`).

- [Pass] The safe sqlite-vec form is executed at runtime: `KNN_SQL` uses `k = ?` (`xyz/retrieve/dense.py:14-19`) and `dense_search()` executes it with `(encoded, k)` (`xyz/retrieve/dense.py:32-34`). The test also performs a real query, not just a string assertion (`tests/test_retrieve.py:49-55`).

- [Pass] Incomplete walks abort before mutations: the walk is fully materialized and checked at `xyz/index/store.py:261-264`; snapshot walk errors also raise at `xyz/index/store.py:236-243`; first chunk deletion/write is only later at `xyz/index/store.py:331-392`. Preservation is covered by `tests/test_store.py:108-128`.

- [Pass] Thresholding is whole-query: candidates are retained as a ranking, then `no_answer` is based solely on its top score or emptiness (`xyz/retrieve/pipeline.py:103-109`).

- [Pass] Reranking exactly replaces the first 50 scores and appends the untouched RRF tail (`xyz/retrieve/pipeline.py:84-101`). It does not compare score domains. Chunk IDs remain in rankings and serialized metrics (`xyz/retrieve/pipeline.py:103-105`; `xyz/eval/metrics.py:71-75`).

- [Pass] Dense winning is not evidence of a sign, BM25, RRF, depth, or text-selection bug. Dense/BM25 correctly negate lower-is-better distances (`xyz/retrieve/dense.py:34`, `xyz/retrieve/lexical.py:55`); hybrid uses rank-only RRF (`xyz/retrieve/pipeline.py:84`, `xyz/retrieve/fuse.py:16-24`); rerank wholly reorders its 50-item head from model scores (`xyz/retrieve/pipeline.py:87-101`). On 30 already-saturated queries, lexical rank fusion and a general reranker over code can genuinely degrade MRR.

- [Nit] A 50-second CPU p50 makes `auto` rerank operationally unsuitable when a reranker is configured (`xyz/retrieve/pipeline.py:57`). This is performance/model-selection follow-up, not a correctness blocker.

Before merge: nothing. Follow-up: benchmark a code-aware reranker and reconsider `auto` rerank policy.
tokens used
53,365
VERDICT: PASS

- [Pass] Production index mutation is centralized in `Store`: schema/FTS triggers and chunk/vector inserts/deletes are in `xyz/index/store.py:151-174,331-392,407-423`. The only other writes found are test fixture setup, not an alternate index path (`tests/test_retrieve.py:20-36`).

- [Pass] The safe sqlite-vec form is executed at runtime: `KNN_SQL` uses `k = ?` (`xyz/retrieve/dense.py:14-19`) and `dense_search()` executes it with `(encoded, k)` (`xyz/retrieve/dense.py:32-34`). The test also performs a real query, not just a string assertion (`tests/test_retrieve.py:49-55`).

- [Pass] Incomplete walks abort before mutations: the walk is fully materialized and checked at `xyz/index/store.py:261-264`; snapshot walk errors also raise at `xyz/index/store.py:236-243`; first chunk deletion/write is only later at `xyz/index/store.py:331-392`. Preservation is covered by `tests/test_store.py:108-128`.

- [Pass] Thresholding is whole-query: candidates are retained as a ranking, then `no_answer` is based solely on its top score or emptiness (`xyz/retrieve/pipeline.py:103-109`).

- [Pass] Reranking exactly replaces the first 50 scores and appends the untouched RRF tail (`xyz/retrieve/pipeline.py:84-101`). It does not compare score domains. Chunk IDs remain in rankings and serialized metrics (`xyz/retrieve/pipeline.py:103-105`; `xyz/eval/metrics.py:71-75`).

- [Pass] Dense winning is not evidence of a sign, BM25, RRF, depth, or text-selection bug. Dense/BM25 correctly negate lower-is-better distances (`xyz/retrieve/dense.py:34`, `xyz/retrieve/lexical.py:55`); hybrid uses rank-only RRF (`xyz/retrieve/pipeline.py:84`, `xyz/retrieve/fuse.py:16-24`); rerank wholly reorders its 50-item head from model scores (`xyz/retrieve/pipeline.py:87-101`). On 30 already-saturated queries, lexical rank fusion and a general reranker over code can genuinely degrade MRR.

- [Nit] A 50-second CPU p50 makes `auto` rerank operationally unsuitable when a reranker is configured (`xyz/retrieve/pipeline.py:57`). This is performance/model-selection follow-up, not a correctness blocker.

Before merge: nothing. Follow-up: benchmark a code-aware reranker and reconsider `auto` rerank policy.
