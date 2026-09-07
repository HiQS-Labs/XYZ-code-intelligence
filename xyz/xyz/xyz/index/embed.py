"""Embedding contracts and the local CodeRankEmbed provider."""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from typing import Any, Protocol

import numpy as np


QUERY_PREFIX = "Represent this query for searching relevant code: "
DEFAULT_MODEL_ID = "nomic-ai/CodeRankEmbed"
DEFAULT_DIM = 768
MAX_SEQ_LENGTH = 2048


class Embedder(Protocol):
    """Minimal embedding interface shared by indexing and retrieval."""

    model_id: str
    dim: int
    provider: str

    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
        """Return one float32 unit vector per document."""

    def encode_query(self, text: str) -> np.ndarray:
        """Return one float32 unit vector for a natural-language query."""


def _positive_env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive integer, got {raw!r}") from exc
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer, got {raw!r}")
    return value


def _unit_float32(vectors: Any, *, rows: int, dim: int) -> np.ndarray:
    array = np.asarray(vectors, dtype=np.float32)
    if rows == 1 and array.shape == (dim,):
        array = array.reshape(1, dim)
    if array.shape != (rows, dim):
        raise ValueError(f"embedder returned shape {array.shape}; expected {(rows, dim)}")
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("embedder returned a zero-length vector")
    return np.asarray(array / norms, dtype=np.float32)


class CodeRankEmbedder:
    """On-device CodeRankEmbed adapter with the repository memory guards."""

    provider = "sentence-transformers"
    dim = DEFAULT_DIM

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        *,
        model_factory: Callable[..., Any] | None = None,
        device: str | None = None,
    ) -> None:
        os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
        self.model_id = model_id
        self.batch_size = _positive_env_int("EMBED_BATCH_SIZE", 16)
        max_threads = _positive_env_int("EMBED_MAX_THREADS", max(1, os.cpu_count() or 1))

        import torch

        torch.set_num_threads(max_threads)
        if device is None:
            device = "mps" if torch.backends.mps.is_available() else "cpu"
        if model_factory is None:
            from sentence_transformers import SentenceTransformer

            model_factory = SentenceTransformer
        self.model = model_factory(model_id, trust_remote_code=True, device=device)
        self.model.max_seq_length = MAX_SEQ_LENGTH

    def _encode(self, texts: Sequence[str]) -> np.ndarray:
        materialised = list(texts)
        if not materialised:
            return np.empty((0, self.dim), dtype=np.float32)
        encoded = self.model.encode(
            materialised,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return _unit_float32(encoded, rows=len(materialised), dim=self.dim)

    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode(texts)

    def encode_query(self, text: str) -> np.ndarray:
        return self._encode([QUERY_PREFIX + text])[0]
