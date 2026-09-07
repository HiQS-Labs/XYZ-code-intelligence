"""Command-line entry point for XYZ Code Intelligence."""

from __future__ import annotations

import argparse
import json
import os
import resource
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Sequence

from xyz import __version__
from xyz.eval.metrics import score
from xyz.eval.pathscreen import (
    DEFAULT_THRESHOLD,
    LANES,
    PathScreen,
    paths_from_db,
    paths_from_git,
)
from xyz.index import CodeRankEmbedder, EmptyCorpus, Store
from xyz.retrieve import Retriever
from xyz.retrieve.latency import LatencyLog
from xyz.retrieve.pipeline import MODES
from xyz.retrieve.rerank import CrossEncoderReranker


def _make_embedder() -> CodeRankEmbedder:
    return CodeRankEmbedder(device=os.environ.get("XYZ_DEVICE"))


def _make_reranker() -> CrossEncoderReranker:
    return CrossEncoderReranker(device=os.environ.get("XYZ_DEVICE"))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="xyz")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", metavar="{ingest,query,eval,screen}")

    ingest = subparsers.add_parser("ingest", help="ingest a repository")
    ingest.add_argument("--db", required=True)
    ingest.add_argument("--repo", required=True)
    ingest.add_argument("--include-prefix", action="append", default=None)
    ingest.add_argument("path")

    query = subparsers.add_parser("query", help="query an index")
    query.add_argument("--db", required=True)
    query.add_argument("--mode", choices=sorted(MODES), default="auto")
    query.add_argument("--k", type=int, default=10)
    query.add_argument("--tau", type=float)
    query.add_argument("text")

    evaluate = subparsers.add_parser("eval", help="score retrieval modes")
    evaluate.add_argument("--db", required=True)
    evaluate.add_argument("--queries", required=True)
    evaluate.add_argument(
        "--modes",
        default="dense,bm25,hybrid,hybrid+rerank",
        help="comma-separated retrieval modes",
    )
    evaluate.add_argument("--depth", type=int, default=100)
    evaluate.add_argument("--out", required=True)

    screen = subparsers.add_parser(
        "screen",
        help="reject benchmark questions their filename already answers",
        description=(
            "Rank paths ALONE — no file contents — for each candidate question, and reject any "
            "whose gold file lands in the top --threshold. Two lanes run (BM25 over tokenised "
            "paths, and the embedding model over path strings); either one firing is a rejection. "
            "Exits 1 if any question is rejected, so it can gate a build."
        ),
    )
    source = screen.add_mutually_exclusive_group(required=True)
    source.add_argument("--db", help="an index to read the corpus paths from")
    source.add_argument(
        "--paths-from-git",
        metavar="REPO_ROOT",
        help="read tracked paths straight from a git repo — no index needed, so a candidate can be "
        "screened in seconds while you are still writing it",
    )
    screen.add_argument("--queries", required=True, help="candidate questions, in queries-*.json form")
    screen.add_argument("--repo", help="restrict the path corpus to one repo in the index (--db only)")
    screen.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help=f"reject when a gold path ranks this high or better (default {DEFAULT_THRESHOLD})",
    )
    screen.add_argument(
        "--lexical-only",
        action="store_true",
        help="skip the dense lane; faster, but misses synonym leakage (see pathscreen docstring)",
    )
    screen.add_argument("--out", help="write the full per-question report here as JSON")
    return parser


def _error(message: str) -> int:
    print(f"xyz: error: {message}", file=sys.stderr)
    return 2


def _peak_rss_mb() -> float:
    rss = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if sys.platform == "darwin":
        return rss / (1024 * 1024)
    return rss / 1024


def _record_ingest_metadata(store: Store, repo: str, prefixes: Sequence[str] | None) -> None:
    with store.connection:
        store.connection.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES ('ingest.repo', ?)", (repo,)
        )
        store.connection.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES ('ingest.include_prefixes', ?)",
            (json.dumps(list(prefixes or [])),),
        )


def _ingest(args: argparse.Namespace) -> int:
    root = Path(args.path)
    if not root.is_dir():
        return _error(f"repository path is not a directory: {root}")

    eta_printed = False

    def progress(done: int, total: int, elapsed: float) -> None:
        nonlocal eta_printed
        if not eta_printed and done >= 200:
            remaining = max(0.0, elapsed / done * max(0, total - done))
            print(f"progress: {done}/{total} chunks embedded; ETA {remaining / 60:.1f} minutes")
            eta_printed = True

    try:
        with Store.open(args.db, _make_embedder()) as store:
            report = store.ingest(
                args.repo,
                root,
                include_prefixes=args.include_prefix,
                progress=progress,
            )
            _record_ingest_metadata(store, args.repo, args.include_prefix)
            stats = store.stats()
    except EmptyCorpus as exc:
        return _error(str(exc))

    print(
        json.dumps(
            {
                "ingest": asdict(report),
                "stats": asdict(stats),
                "peak_rss_mb": round(_peak_rss_mb(), 2),
            }
        )
    )
    return 0


def _query(args: argparse.Namespace) -> int:
    if args.k <= 0:
        return _error("k must be positive")
    embedder = _make_embedder()
    reranker = _make_reranker() if args.mode in {"auto", "hybrid+rerank"} else None
    with Store.open(args.db, embedder) as store:
        result = Retriever(store, embedder, reranker).search(
            args.text, k=args.k, fetch_k=max(100, args.k), mode=args.mode, tau=args.tau
        )
    if result.no_answer:
        print("no answer")
    else:
        print("rank\tpath\tqualified_name\tlines\tscore")
        for rank, hit in enumerate(result.hits, start=1):
            print(
                f"{rank}\t{hit.path}\t{hit.qualified_name}\t"
                f"{hit.start_line}-{hit.end_line}\t{hit.score:.6f}"
            )
    print("timings_ms " + json.dumps(result.timings, sort_keys=True))
    return 0


def _load_queries(path: str) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("queries", []) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("query file must contain a list or a top-level 'queries' list")
    return rows


def _stored_prefixes(store: Store) -> list[str]:
    row = store.connection.execute(
        "SELECT value FROM meta WHERE key = 'ingest.include_prefixes'"
    ).fetchone()
    return list(json.loads(row[0])) if row else []


def _eval(args: argparse.Namespace) -> int:
    if args.depth <= 0:
        return _error("depth must be positive")
    try:
        queries = _load_queries(args.queries)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _error(f"cannot read query file: {exc}")
    if not queries:
        return _error("query list is empty")

    modes = [mode.strip() for mode in args.modes.split(",") if mode.strip()]
    invalid = [mode for mode in modes if mode not in MODES or mode == "auto"]
    if not modes or invalid:
        return _error(f"invalid eval modes: {', '.join(invalid) or '(none)'}")

    embedder = _make_embedder()
    needs_reranker = "hybrid+rerank" in modes
    with Store.open(args.db, embedder) as store:
        stats = store.stats()
        if stats.chunks == 0:
            return _error("cannot evaluate an empty corpus")
        corpus_paths = {
            row[0] for row in store.connection.execute("SELECT DISTINCT path FROM chunks")
        }
        gold_paths = {str(path) for query in queries for path in query.get("relevant", [])}
        missing = sorted(gold_paths - corpus_paths)
        if missing:
            return _error("gold paths missing from corpus: " + ", ".join(missing))

        retriever = Retriever(store, embedder, _make_reranker() if needs_reranker else None)
        reports: dict[str, dict[str, Any]] = {}
        latency: dict[str, dict[str, dict[str, float]]] = {}
        raw_rankings: dict[str, dict[str, list[tuple[int, str]]]] = {}
        for mode in modes:
            mode_rankings: dict[str, list[tuple[int, str]]] = {}
            timing_log = LatencyLog()
            for query in queries:
                text = str(query["q"])
                result = retriever.search(
                    text, k=min(10, args.depth), fetch_k=args.depth, mode=mode
                )
                mode_rankings[text] = result.ranking
                timing_log.add(result.timings)
            raw_rankings[mode] = mode_rankings
            reports[mode] = score(mode_rankings, queries, args.depth).to_dict()
            latency[mode] = timing_log.summary()

        reorder_count = 0
        if "hybrid" in raw_rankings and "hybrid+rerank" in raw_rankings:
            for query in queries:
                text = str(query["q"])
                before = [chunk_id for chunk_id, _path in raw_rankings["hybrid"][text][:10]]
                after = [
                    chunk_id
                    for chunk_id, _path in raw_rankings["hybrid+rerank"][text][:10]
                ]
                reorder_count += before != after

        payload = {
            "reports": reports,
            "latency": latency,
            "corpus": {
                "chunk_count": stats.chunks,
                "file_count": stats.files,
                "include_prefixes": _stored_prefixes(store),
                "db": str(Path(args.db).resolve()),
            },
            "reorder_count": reorder_count,
        }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("mode\tMRR@D\tR@1\tR@3\tR@5\tR@10\tmiss@D")
    for mode in modes:
        report = reports[mode]
        print(
            f"{mode}\t{report['mrr']:.4f}\t{report['recall@1']:.4f}\t"
            f"{report['recall@3']:.4f}\t{report['recall@5']:.4f}\t"
            f"{report['recall@10']:.4f}\t{report['never_found']}"
        )
    print(f"depth={args.depth}; reorder_count={reorder_count}")
    return 0


def _screen(args: argparse.Namespace) -> int:
    queries = json.loads(Path(args.queries).read_text(encoding="utf-8"))["queries"]
    if args.paths_from_git:
        if args.repo:
            return _error("--repo filters an index; it does not apply to --paths-from-git")
        source = args.paths_from_git
        paths = paths_from_git(source)
    else:
        source = args.db
        paths = paths_from_db(args.db, repo=args.repo)
    if not paths:
        return _error(f"no paths in {source}" + (f" for repo {args.repo}" if args.repo else ""))

    embedder = None if args.lexical_only else _make_embedder()
    results = PathScreen(paths, embedder=embedder, threshold=args.threshold).screen_all(queries)

    answerable = len(results)
    skipped = len(queries) - answerable
    rejected = [result for result in results if not result.passed]

    for result in rejected:
        lanes = ", ".join(
            f"{name} rank {result.lanes[name].best_rank}" for name in result.rejected_by
        )
        print(f"REJECT  {result.query}\n        gold {result.lanes[result.rejected_by[0]].best_path} — {lanes}")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(
                {
                    "threshold": args.threshold,
                    "lanes": ["lexical"] if args.lexical_only else list(LANES),
                    "corpus": {"paths": len(paths), "source": str(Path(source).resolve())},
                    "counts": {
                        "screened": answerable,
                        "passed": answerable - len(rejected),
                        "rejected": len(rejected),
                        "skipped_no_answer": skipped,
                    },
                    "results": [result.as_dict() for result in results],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    print(
        f"screened {answerable} answerable ({skipped} no-answer skipped) against {len(paths)} paths; "
        f"passed {answerable - len(rejected)}, rejected {len(rejected)}"
    )
    return 1 if rejected else 0


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and return a process exit status."""
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        return {"ingest": _ingest, "query": _query, "eval": _eval, "screen": _screen}[
            args.command
        ](args)
    except (OSError, ValueError) as exc:
        return _error(str(exc))
