"""Two functions the pipeline and the tests both use."""

from __future__ import annotations

from collections.abc import Iterable


def mean_score(values: Iterable[float]) -> float:
    """Arithmetic mean. Raises on an empty input rather than returning 0."""
    items = list(values)
    if not items:
        raise ValueError("mean_score needs at least one value")
    return round(sum(items) / len(items), 4)


def normalise(score: float, low: float = 0.0, high: float = 100.0) -> float:
    """Map a score to 0..1, clamping out-of-range values."""
    if high <= low:
        raise ValueError("high must be greater than low")
    return round(min(max((score - low) / (high - low), 0.0), 1.0), 4)
