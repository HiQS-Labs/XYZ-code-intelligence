"""sqlite-vec nearest-neighbour retrieval."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import sqlite_vec

from xyz.index.store import Store
from xyz.retrieve.models import Hit


KNN_SQL = """
SELECT rowid, distance
FROM chunks_vec
WHERE embedding MATCH ? AND k = ?
ORDER BY distance ASC
"""


def dense_search(store: Store, query_vec: Sequence[float] | np.ndarray, k: int) -> list[Hit]:
    """Return the nearest vectors with negated distances as scores."""

    if k <= 0:
        return []
    vector = np.asarray(query_vec, dtype=np.float32)
    if vector.shape != (store.embedder.dim,):
        raise ValueError(
            f"query vector has shape {vector.shape}; expected {(store.embedder.dim,)}"
        )
    encoded = sqlite_vec.serialize_float32(vector.tolist())
    rows = store.connection.execute(KNN_SQL, (encoded, k))
    return [Hit(int(chunk_id), -float(distance), "dense") for chunk_id, distance in rows]
