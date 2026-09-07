"""FTS5/BM25 retrieval with safe query construction."""

from __future__ import annotations

import re

from xyz.index.store import Store
from xyz.retrieve.models import Hit


_TOKEN = re.compile(r"[^\W_]+(?:_[^\W_]+)*", re.UNICODE)
_STOPWORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
        "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "with",
    }
)


def sanitise_fts_query(query: str) -> str | None:
    """Turn user text into an operator-free OR query, or ``None`` if empty."""

    tokens: list[str] = []
    seen: set[str] = set()
    for match in _TOKEN.finditer(query):
        token = match.group(0)
        folded = token.casefold()
        if folded in _STOPWORDS or folded in seen:
            continue
        seen.add(folded)
        tokens.append(token.replace('"', '""'))
    if not tokens:
        return None
    return " OR ".join(f'"{token}"' for token in tokens)


def bm25_search(store: Store, query: str, k: int) -> list[Hit]:
    """Return the best lexical matches with negated FTS5 BM25 scores."""

    if k <= 0:
        return []
    safe_query = sanitise_fts_query(query)
    if safe_query is None:
        return []
    rows = store.connection.execute(
        """
        SELECT rowid, bm25(chunks_fts) AS distance
        FROM chunks_fts
        WHERE chunks_fts MATCH ?
        ORDER BY distance ASC, rowid ASC
        LIMIT ?
        """,
        (safe_query, k),
    )
    return [Hit(int(chunk_id), -float(distance), "bm25") for chunk_id, distance in rows]
