"""In-memory retrieval latency aggregation."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


class LatencyLog:
    """Collect timing dictionaries and report p50/p95 milliseconds per stage."""

    def __init__(self, timings: Iterable[Mapping[str, float]] = ()) -> None:
        self.timings: list[dict[str, float]] = []
        for sample in timings:
            self.add(sample)

    def add(self, timings: Mapping[str, float]) -> None:
        self.timings.append({key: float(value) for key, value in timings.items()})

    append = add

    def summary(self) -> dict[str, dict[str, float]]:
        stages = sorted({stage for sample in self.timings for stage in sample})
        return {
            stage: {
                "p50": _percentile([sample.get(stage, 0.0) for sample in self.timings], 0.50),
                "p95": _percentile([sample.get(stage, 0.0) for sample in self.timings], 0.95),
            }
            for stage in stages
        }

    report = summary
