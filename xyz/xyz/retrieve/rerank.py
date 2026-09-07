"""Injectable local cross-encoder reranking."""

from __future__ import annotations

import math
import os
from collections.abc import Callable, Sequence
from typing import Any, Protocol


DEFAULT_RERANKER = "mixedbread-ai/mxbai-rerank-xsmall-v1"


class Reranker(Protocol):
    def score(self, query: str, texts: Sequence[str]) -> list[float]:
        """Return one higher-is-better score for each text."""


class CrossEncoderReranker:
    """Sentence Transformers CrossEncoder adapter, kept injectable for bake-offs."""

    def __init__(
        self,
        model_id: str | None = None,
        *,
        model_factory: Callable[..., Any] | None = None,
        device: str | None = None,
    ) -> None:
        self.model_id = model_id or os.environ.get("XYZ_RERANKER", DEFAULT_RERANKER)
        if model_factory is None:
            from sentence_transformers import CrossEncoder

            model_factory = CrossEncoder
        kwargs: dict[str, object] = {"trust_remote_code": True}
        if device is not None:
            kwargs["device"] = device
        self.model = model_factory(self.model_id, **kwargs)

    def score(self, query: str, texts: Sequence[str]) -> list[float]:
        materialised = list(texts)
        if not materialised:
            return []
        raw = self.model.predict([(query, text) for text in materialised])
        if hasattr(raw, "tolist"):
            raw = raw.tolist()
        scores = [float(value) for value in raw]
        if len(scores) != len(materialised):
            raise ValueError(
                f"reranker returned {len(scores)} scores for {len(materialised)} texts"
            )
        if not all(math.isfinite(value) for value in scores):
            raise ValueError("reranker returned a non-finite score")
        return scores
