"""Deterministic test doubles shared by index and retrieval tests."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence

import numpy as np


class FakeEmbedder:
    provider = "fake"

    def __init__(self, model_id: str = "fake", dim: int = 8, provider: str = "fake") -> None:
        self.model_id = model_id
        self.dim = dim
        self.provider = provider
        self.document_calls = 0
        self.query_calls = 0
        self.documents_encoded = 0

    @property
    def call_count(self) -> int:
        return self.document_calls + self.query_calls

    def _vector(self, text: str) -> np.ndarray:
        values: list[float] = []
        counter = 0
        while len(values) < self.dim:
            digest = hashlib.sha256(f"{counter}:{text}".encode()).digest()
            values.extend((byte - 127.5) / 127.5 for byte in digest)
            counter += 1
        vector = np.asarray(values[: self.dim], dtype=np.float32)
        return vector / np.linalg.norm(vector)

    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
        self.document_calls += 1
        self.documents_encoded += len(texts)
        return np.stack([self._vector(text) for text in texts]).astype(np.float32)

    def encode_query(self, text: str) -> np.ndarray:
        self.query_calls += 1
        return self._vector(text)


class FakeReranker:
    """Return deterministic scores keyed by exact chunk text."""

    def __init__(self, scores: dict[str, float] | None = None, default: float = 0.0) -> None:
        self.scores = scores or {}
        self.default = default

    def score(self, query: str, texts: Sequence[str]) -> list[float]:
        del query
        return [float(self.scores.get(text, self.default)) for text in texts]
